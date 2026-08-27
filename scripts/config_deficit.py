# -*- coding: utf-8 -*-
"""
FASE 2 - Criterios del deficit habitacional del DANE (metodologia 2020).

Todo lo de este archivo es TRANSCRIPCION de dos fuentes oficiales, no
interpretacion propia:

  [NM] Nota metodologica "Deficit Habitacional CNPV 2018" (DANE, abril 2020),
       dane.gov.co/files/investigaciones/deficit-habitacional/
       deficit-hab-2020-nota-metodologica.pdf
  [FM] Formulario de la ECV 2024, capitulo B "Datos de la vivienda",
       dane.gov.co/files/operaciones/ECV/formulario-ECV-2024.pdf

TRAMPA IMPORTANTE, verificada: los nombres de variable de la ECV NO siguen el
orden del cuestionario. Contra lo que sugiere el nombre:

    P4005 = material predominante de las PAREDES exteriores  (10 categorias)
    P4015 = material predominante de los PISOS               ( 7 categorias)

Se confirma por el numero de categorias y por la distribucion real (ECV 2024):
P4005 tiene 10 valores y su codigo 1 (bloque/ladrillo/piedra/madera pulida)
concentra el 76% de los hogares; P4015 tiene 7 valores y sus codigos 4
(baldosa/vinilo/tableta) y 6 (cemento/gravilla) concentran 46% y 36%. Invertirlas
-que es el error natural al leer los nombres- da un deficit equivocado sin
lanzar ningun error.

ALCANCE: las 23 ciudades del observatorio son cabecera municipal (CLASE=1), asi
que aqui solo se codifican los criterios de CABECERA. Los de centros poblados y
rural disperso difieren (ver [NM]) y quedan fuera a proposito.
"""

# --- Codigos del formulario ECV, capitulo B [FM] --------------------------

# 2. Tipo de vivienda
TIPO_VIVIENDA = {
    1: "Casa",
    2: "Apartamento",
    3: "Cuarto(s)",
    4: "Vivienda tradicional indígena",
    5: "Otro (carpa, contenedor, vagón, embarcación, cueva, refugio natural, etc.)",
}
VAR_TIPO_VIVIENDA = "P1070"

# 3. Material predominante de las PAREDES exteriores  -> variable P4005
MATERIAL_PAREDES = {
    1: "Bloque, ladrillo, piedra, madera pulida",
    2: "Tapia pisada, adobe",
    3: "Bahareque revocado",
    4: "Bahareque sin revocar",
    5: "Madera burda, tabla, tablón",
    6: "Material prefabricado",
    7: "Guadua",
    8: "Caña, esterilla, otro vegetal",
    9: "Zinc, tela, lona, cartón, latas, desechos, plástico",
    10: "Sin paredes",
}
VAR_PAREDES = "P4005"

# 4. Material predominante de los PISOS  -> variable P4015
MATERIAL_PISOS = {
    1: "Alfombra o tapete de pared a pared",
    2: "Madera pulida y lacada, parqué",
    3: "Mármol",
    4: "Baldosa, vinilo, tableta, ladrillo, laminado",
    5: "Madera burda, tabla, tablón, otro vegetal",
    6: "Cemento, gravilla",
    7: "Tierra, arena o barro",
}
VAR_PISOS = "P4015"

# 6. Servicios publicos (1=Sí, 2=No)
VAR_ENERGIA = "P8520S1"
VAR_ACUEDUCTO = "P8520S5"
VAR_ALCANTARILLADO = "P8520S3"
VAR_BASURAS = "P8520S4"
VAR_ESTRATO = "P8520S1A1"          # estrato para tarifa de energia

VAR_HOGARES_EN_VIVIENDA = "CANT_HOGARES_VIVIENDA"
VAR_PERSONAS_HOGAR = "CANT_PERSONAS_HOGAR"   # modulo "Servicios del hogar"
VAR_CUARTOS_TOTAL = "P5000"                  # modulo "Servicios del hogar"
VAR_CUARTOS_DORMIR = "P5010"                 # modulo "Servicios del hogar"

# --- Criterios de deficit, CABECERA [NM] ----------------------------------

# Se excluyen del calculo completo los hogares en vivienda tradicional indigena:
# "del calculo de este deficit habitacional se excluyen a los hogares que habitan
# en viviendas etnicas o indigenas, pues estas viviendas tendran una metodologia
# aparte" [NM p.5]
TIPO_VIVIENDA_EXCLUIR = {4}

# DEFICIT CUANTITATIVO (estructural). Un hogar entra si cumple AL MENOS UNA:
#
#  a) Tipo de vivienda: "contenedor, carpa, embarcacion, vagon, cueva o refugio
#     natural [...] los tipos de vivienda que son aceptables son: las casas,
#     apartamentos y viviendas tipo cuarto" [NM p.5]
TIPO_VIVIENDA_DEFICIENTE = {5}
#
#  b) Material de paredes: "ademas de la madera burda, tabla o tablon, los otros
#     materiales de paredes que no se consideran inadecuados son: caña,
#     esterilla, otros vegetales, o materiales de desecho. Ademas, los hogares
#     que habitan en viviendas sin paredes se consideran en deficit
#     cuantitativo" [NM p.6]
#     (la frase del DANE dice "no se consideran inadecuados" por errata evidente;
#      el sentido y las tablas del boletin son que SI son inadecuados)
PAREDES_DEFICIENTE = {5, 8, 9, 10}
#
#  c) Cohabitacion: "se consideran en deficit habitacional por cohabitacion los
#     hogares [...] que habitan en una vivienda en la que hay tres o mas hogares.
#     En los casos en los que hay dos hogares en una misma vivienda, en las
#     cabeceras y en los centros poblados, se los considera en deficit cuando hay
#     mas de seis personas en total en la vivienda. En todos los casos se excluyen
#     los hogares principales y los hogares unipersonales" [NM p.7]
COHABITACION_HOGARES_MINIMO = 3
COHABITACION_DOS_HOGARES_PERSONAS = 6      # > 6 personas en la vivienda
#
#  d) Hacinamiento no mitigable: "se considera que un hogar se encuentra en
#     deficit cuando hay mas de cuatro personas por cuarto para dormir" [NM p.9].
#     Se calcula para cabeceras y centros poblados; excluye rural disperso.
HACINAMIENTO_NO_MITIGABLE = 4              # > 4 personas por cuarto para dormir

# DEFICIT CUALITATIVO (no estructural). EXCLUYENTE del cuantitativo: "un hogar
# que se encuentra en deficit cuantitativo no se contabiliza en deficit
# cualitativo" [NM p.9]. Entra si cumple AL MENOS UNA:
#
#  a) Hacinamiento mitigable: "hogares en los que hay mas de 2 y hasta 4 personas
#     por cuarto, en las cabeceras y centros poblados" [NM p.10]
HACINAMIENTO_MITIGABLE = (2, 4)            # > 2 y <= 4 personas por cuarto dormir
#
#  b) Material de pisos: "se consideran en deficit cualitativo los hogares que
#     habitan en viviendas en las que el material de los pisos es de tierra,
#     arena o barro" [NM p.10]
PISOS_DEFICIENTE = {7}
#
#  c) Lugar donde cocina: en cabeceras, "se cocinan los alimentos en un cuarto
#     usado tambien para dormir, en una sala-comedor sin lavaplatos, en un patio,
#     corredor, enramada, o al aire libre. Los hogares que responden que en ese
#     hogar no se cocinan alimentos no se consideran en deficit" [NM p.10]
#     -> variable y codigos PENDIENTES de confirmar en el modulo "Servicios del
#        hogar" contra el formulario; NO codificar a ojo.
#
#  d) Acueducto: "los hogares en cabeceras que habitan viviendas que no cuentan
#     con acueducto se consideran en deficit cualitativo" [NM p.10]
#     -> VAR_ACUEDUCTO == 2 (No)
#
#  e) Alcantarillado: en cabeceras, "hogares que no cuentan con servicio de
#     alcantarillado, o que, teniendo acceso a alcantarillado, el servicio del
#     sanitario con el que cuenta el hogar esta conectado a un pozo septico, no
#     tiene conexion, el sanitario es tipo letrina, tiene descarga directa a
#     fuentes de agua (bajamar), o si no tiene servicio de sanitario" [NM p.11]
#     -> VAR_ALCANTARILLADO == 2, O el tipo de sanitario en la lista anterior;
#        variable de sanitario PENDIENTE de confirmar.
#
#  f) Energia electrica: "cuando la vivienda en la que habitan no tiene conexion
#     a servicio de energia electrica" [NM p.11] -> VAR_ENERGIA == 2
#
#  g) Recoleccion de basuras: "hogares que no tienen acceso al servicio de
#     recoleccion de basuras" [NM p.11] -> VAR_BASURAS == 2

SI, NO = 1, 2

# Cifras oficiales del DANE contra las que hay que validar el calculo antes de
# publicar nada por ciudad (boletines tecnicos ECV):
VALIDACION_OFICIAL = {
    # Fuente: anexo oficial ECV 2024 del DANE, "Cuadro 10 - Hogares por deficit
    # habitacional segun tipo y componentes" (anex-ECV-2024.xlsx). Son las
    # cifras exactas, no las de prensa: circulan por ahi un 19,6% de cabeceras
    # y un 65,5% de rural que NO corresponden a este cuadro.
    2024: {
        "hogares_miles": 18324, "hogares_cabecera_miles": 14338,
        "total_nacional": 26.8436, "cuantitativo_nacional": 6.8158,
        "cualitativo_nacional": 20.0278,
        "total_cabecera": 17.2910, "cuantitativo_cabecera": 2.8041,
        "cualitativo_cabecera": 14.4869,
        "total_resto": 61.2035,
        # componentes en CABECERA, columna "jerarquizado" (que es la excluyente,
        # la que corresponde a este calculo)
        "cab_hacinamiento_mitigable": 8.0464, "cab_pisos": 0.6081,
        "cab_cocina": 2.3890, "cab_agua": 1.1967, "cab_alcantarillado": 5.4829,
        "cab_energia": 0.0855, "cab_basuras": 0.8780,
    },
}

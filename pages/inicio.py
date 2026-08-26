# -*- coding: utf-8 -*-
"""Vista Inicio: portada del observatorio.

Antes era solo la tabla de 23 ciudades. Ahora la tabla va precedida de lo que
alguien que llega por primera vez necesita para leerla bien: para que sirve el
observatorio, que variables cubre y - la parte que casi ningun tablero publica -
que cosas deliberadamente NO mide. Ese ultimo bloque no es relleno: es la misma
disciplina que sostiene todo el pipeline (el dato nunca se oculta, pero tampoco
se presenta como mas preciso de lo que es).

Todas las cifras de esta pagina se calculan en vivo desde la tabla maestra y los
CSV de control; ninguna esta escrita a mano, para que no se desfasen si el
pipeline se vuelve a correr.
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
import datos_observatorio as datos
import estilo

ANIO_REFERENCIA = "2025"

INDICADORES_CLAVE = [
    ("Tenencia: En arriendo o subarriendo", "% en arriendo"),
    ("Canon de arriendo mensual - mediana", "Canon mediano de arriendo (COP)"),
    ("Arriendo/ingreso del hogar (mediana)", "Arriendo / ingreso (mediana, %)"),
    ("Arrendatarios que destinan >30% del ingreso al arriendo", "Sobrecarga >30% (%)"),
    ("Tenencia: Propia, totalmente pagada", "Vivienda propia pagada (%)"),
    ("Hogares con hacinamiento (>3 personas/cuarto para dormir)", "Hacinamiento (%)"),
]

# Nombre legible y glosa de cada bloque del catalogo. El bloque
# `deficit_habitacional` no esta aqui a proposito: vive en "Lo que no mide".
BLOQUES = {
    "tenencia": ("Tenencia", "Cómo ocupa su vivienda el hogar: propia pagada o pagándose, arriendo, usufructo, posesión sin título."),
    "arriendo": ("Mercado de arriendo", "Canon efectivamente pagado por los hogares arrendatarios: mediana, promedio y cuartiles."),
    "esfuerzo_financiero": ("Esfuerzo financiero", "Qué proporción del ingreso se va en arriendo, y cuántos hogares superan los umbrales del 30 % y 50 %."),
    "vivienda_propia_credito": ("Vivienda propia y crédito", "Valor comercial estimado, cuota hipotecaria y arriendo imputado de quienes son propietarios."),
    "hacinamiento": ("Hacinamiento", "Personas por cuarto para dormir y hogares por encima del umbral crítico."),
    "servicios_publicos": ("Servicios públicos", "Hogares sin acueducto, alcantarillado, gas a red, energía o recolección de basuras."),
    "ingreso_pobreza": ("Ingreso y pobreza", "Ingreso del hogar y pobreza monetaria, separando propietarios de arrendatarios."),
}

NO_MIDE = [
    ("Déficit habitacional cuantitativo y cualitativo",
     "Requiere la Encuesta Nacional de Calidad de Vida (ECV), fuera del alcance de esta fase. "
     "No se estimó ni se aproximó: cualquier cifra de déficit atribuida a este observatorio sería incorrecta."),
    ("Estrato socioeconómico",
     "Misma razón: la GEIH no lo trae con la desagregación necesaria para estas 23 ciudades."),
    ("Ingreso, carga financiera y pobreza en 2026*",
     "El DANE no publica la medición de Pobreza Monetaria del año en curso, que requiere año calendario completo. "
     "Esos ND son estructurales, no un fallo del cálculo."),
    ("Municipios distintos a estas 23 ciudades",
     "El observatorio se limita a los dominios que la GEIH identifica por separado; el resto del país no es estimable con esta fuente."),
]

estilo.cabecera(
    antetitulo="DANE · GEIH y Pobreza Monetaria · 2023–2026*",
    titulo="Observatorio Nacional de Vivienda",
    bajada="23 ciudades capitales y áreas metropolitanas de Colombia",
)

tabla = datos.cargar_tabla_maestra()
control = datos.cargar_control_geografico()
auditoria = datos.cargar_auditoria()


def _es(n: int) -> str:
    """Separador de miles en español (punto)."""
    return f"{n:,}".replace(",", ".")


# --- Tesis y entradilla -----------------------------------------------------

izq, der = st.columns([5, 4], gap="large")

with izq:
    st.markdown(
        '<div class="obs-tesis">Cuánto pesa la vivienda en el bolsillo de los hogares '
        'colombianos —<em> con el margen de error a la vista.</em></div>',
        unsafe_allow_html=True,
    )

with der:
    st.markdown(
        '<div class="obs-entrada">Este observatorio reúne los indicadores de tenencia, '
        'arriendo, esfuerzo financiero, hacinamiento, servicios públicos e ingreso de las '
        '23 ciudades capitales y áreas metropolitanas del país, calculados directamente '
        'desde los microdatos de la Gran Encuesta Integrada de Hogares del DANE.</div>'
        '<div class="obs-entrada">Cada cifra se publica junto con su tamaño de muestra, su '
        'intervalo de confianza y las advertencias que le apliquen. El dato nunca se '
        'oculta ni se maquilla: si una estimación es frágil, lo dice.</div>',
        unsafe_allow_html=True,
    )

# --- Cifras de alcance (todas calculadas en vivo) ---------------------------

hogares = int(control["registros"].sum())
meses = control.groupby(["anio", "mes"]).ngroups
con_precision = int(tabla["error_estandar"].notna().sum())
rechazos = int((auditoria["resultado"] == "RECHAZADO").sum())
controles = len(auditoria)

estilo.seccion("El observatorio en cuatro cifras")
c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    estilo.cifra(str(len(datos.NOMBRES)), "ciudades capitales y áreas metropolitanas")
with c2:
    estilo.cifra(_es(hogares), f"hogares encuestados en {meses} meses")
with c3:
    estilo.cifra(_es(con_precision), "estimaciones con intervalo de confianza")
with c4:
    estilo.cifra(str(rechazos), f"rechazos en {controles} controles de auditoría")

# --- Qué mide ---------------------------------------------------------------

estilo.seccion("Qué mide")

catalogo = datos.indicadores_disponibles(tabla)
por_bloque: dict[str, list[str]] = {}
for bloque, nombre in catalogo:
    if "(control)" in nombre:      # fila de control de auditoría, no es un indicador publicado
        continue
    por_bloque.setdefault(bloque, []).append(nombre)

# Las columnas agrupan por tema, no por orden alfabetico: cada una responde una
# pregunta distinta sobre el mismo hogar.
COLUMNAS_BLOQUES = [
    ["tenencia", "vivienda_propia_credito"],            # cómo ocupa la vivienda
    ["arriendo", "esfuerzo_financiero", "ingreso_pobreza"],  # cuánto le cuesta
    ["hacinamiento", "servicios_publicos"],             # en qué condiciones
]

columnas = st.columns(3, gap="large")
for columna, claves in zip(columnas, COLUMNAS_BLOQUES):
    with columna:
        for clave in claves:
            titulo, glosa = BLOQUES[clave]
            cuantos = len(por_bloque.get(clave, []))
            st.markdown(
                f'<div class="obs-bloque-nombre">{titulo} '
                f'<span style="color:{estilo.TERRACOTA};font-weight:600">· {cuantos}</span></div>'
                f'<div class="obs-bloque-detalle">{glosa}</div>',
                unsafe_allow_html=True,
            )

total_indicadores = sum(len(v) for v in por_bloque.values())
st.caption(
    f"{total_indicadores} indicadores en {len(BLOQUES)} bloques, para cada ciudad y cada uno de "
    f"los años 2023, 2024, 2025 y 2026*. 2026* es enero–junio: el único periodo publicado por el "
    f"DANE al momento del cálculo."
)

# --- Lo que no mide (el bloque que da carácter a la portada) ----------------

estilo.seccion("Lo que no mide")

filas_dl = "".join(f"<dt>{t}</dt><dd>{d}</dd>" for t, d in NO_MIDE)
areas_metro = sum(1 for n in datos.NOMBRES if n.endswith("A.M."))
st.markdown(
    f"""
    <div class="obs-nomide">
      <h4>Los límites también son un resultado</h4>
      <div class="intro">Un observatorio que solo publica lo que le conviene no sirve para decidir.
      Estas son las preguntas que esta fuente <strong>no</strong> puede responder, y por qué:</div>
      <dl>{filas_dl}</dl>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    f"Además: {areas_metro} de las 23 unidades son áreas metropolitanas completas, no solo el "
    f"municipio núcleo — no son comparables directamente con cifras municipales de otra fuente. "
    f"El error estándar publicado es una cota inferior del real: los microdatos públicos de la "
    f"GEIH no incluyen las variables de diseño muestral."
)

# --- La tabla ---------------------------------------------------------------

estilo.seccion(f"Las 23 ciudades en {ANIO_REFERENCIA}")

filas = []
notas_vista: list[str] = []
for ciudad in datos.NOMBRES:
    fila = {"Ciudad": ciudad}
    for nombre_indicador, etiqueta in INDICADORES_CLAVE:
        ind = datos.indicador(tabla, ciudad, ANIO_REFERENCIA, nombre_indicador)
        fila[etiqueta] = ind["valor"] if ind and isinstance(ind["valor"], (int, float)) else None
        notas_vista += datos.notas(ciudad, ANIO_REFERENCIA, nombre_indicador)
    filas.append(fila)

resumen = pd.DataFrame(filas)

column_config = {
    "Ciudad": st.column_config.TextColumn(width="medium"),
    "Canon mediano de arriendo (COP)": st.column_config.NumberColumn(format="$ %d"),
}
for etiqueta in [
    "% en arriendo",
    "Arriendo / ingreso (mediana, %)",
    "Sobrecarga >30% (%)",
    "Vivienda propia pagada (%)",
    "Hacinamiento (%)",
]:
    column_config[etiqueta] = st.column_config.NumberColumn(format="%.1f%%")

st.dataframe(
    resumen,
    column_config=column_config,
    hide_index=True,
    use_container_width=True,
    height=(len(resumen) + 1) * 35 + 3,
)
st.caption(
    f"Año {ANIO_REFERENCIA}, el último completo. Clic en un encabezado para ordenar; "
    f"use la Ficha de ciudad para ver una sola ciudad en detalle, o el Comparador para "
    f"seguir la evolución de varias."
)

notas_unicas = list(dict.fromkeys(notas_vista))
if notas_unicas:
    with st.expander(f"Notas metodológicas de esta vista ({len(notas_unicas)})"):
        for n in notas_unicas:
            st.markdown(f"- {n}")

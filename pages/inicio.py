# -*- coding: utf-8 -*-
"""Vista Inicio: portada del observatorio.

Antes era solo la tabla de 23 ciudades. Ahora la tabla va precedida de lo que
alguien que llega por primera vez necesita para leerla bien: para que sirve el
observatorio, que variables cubre y que preguntas quedan fuera de su alcance.

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
# `deficit_habitacional` no esta aqui a proposito: vive en "Fuera de alcance".
BLOQUES = {
    "tenencia": ("Tenencia", "Cómo ocupa el hogar su vivienda: propia pagada o pagándose, arriendo, usufructo, posesión sin título."),
    "arriendo": ("Mercado de arriendo", "Canon efectivamente pagado por los hogares arrendatarios: mediana, promedio y cuartiles."),
    "esfuerzo_financiero": ("Esfuerzo financiero", "Proporción del ingreso destinada al arriendo y hogares que superan los umbrales del 30 % y el 50 %."),
    "vivienda_propia_credito": ("Vivienda propia y crédito", "Valor comercial estimado, cuota hipotecaria y arriendo imputado de los hogares propietarios."),
    "hacinamiento": ("Hacinamiento", "Personas por cuarto para dormir y hogares por encima del umbral crítico."),
    "servicios_publicos": ("Servicios públicos", "Hogares sin acueducto, alcantarillado, gas conectado a red, energía o recolección de basuras."),
    "ingreso_pobreza": ("Ingreso y pobreza", "Ingreso del hogar y pobreza monetaria, diferenciando propietarios de arrendatarios."),
}

# Las columnas agrupan por tema, no por orden alfabetico: cada una responde una
# pregunta distinta sobre el mismo hogar.
COLUMNAS_BLOQUES = [
    ["tenencia", "vivienda_propia_credito"],
    ["arriendo", "esfuerzo_financiero", "ingreso_pobreza"],
    ["hacinamiento", "servicios_publicos"],
]

FUERA_DE_ALCANCE = [
    ("Déficit habitacional cuantitativo y cualitativo",
     "Su cálculo requiere la Encuesta Nacional de Calidad de Vida, que no forma parte de esta fase. "
     "No se estimó ni se aproximó por otras vías."),
    ("Estrato socioeconómico",
     "La GEIH no incluye esta variable con la desagregación necesaria para las 23 ciudades."),
    ("Ingreso, carga financiera y pobreza en 2026*",
     "El DANE publica la medición de Pobreza Monetaria por año calendario completo, de modo que "
     "aún no existe la de 2026. Los ND de esas filas corresponden a esa ausencia de fuente."),
    ("Municipios distintos a estas 23 ciudades",
     "El observatorio se limita a los dominios que la GEIH identifica por separado. El resto del "
     "país no es estimable con esta fuente."),
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
        '<div class="obs-tesis obs-anim obs-anim-1">Qué pagan por vivienda los hogares de las '
        '23 ciudades principales de Colombia, <em>y con cuánta precisión lo sabemos.</em></div>',
        unsafe_allow_html=True,
    )

with der:
    st.markdown(
        '<div class="obs-anim obs-anim-2">'
        '<div class="obs-entrada">Este observatorio reúne indicadores de tenencia, arriendo, '
        'esfuerzo financiero, hacinamiento, servicios públicos e ingreso para las 23 ciudades '
        'capitales y áreas metropolitanas del país. Todos se calculan a partir de los microdatos '
        'de la Gran Encuesta Integrada de Hogares del DANE.</div>'
        '<div class="obs-entrada">Cada estimación se publica con su tamaño de muestra, su '
        'intervalo de confianza al 95 % y las advertencias metodológicas que le correspondan. '
        'Cuando una cifra tiene poca precisión estadística, la nota al pie de la vista lo señala '
        'en lugar de omitir el dato.</div>'
        "</div>",
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
    estilo.cifra(str(len(datos.NOMBRES)), "ciudades capitales y áreas metropolitanas", orden=3)
with c2:
    estilo.cifra(_es(hogares), f"hogares encuestados en {meses} meses", orden=4)
with c3:
    estilo.cifra(_es(con_precision), "estimaciones con intervalo de confianza", orden=5)
with c4:
    estilo.cifra(str(rechazos), f"rechazos en {controles} controles de auditoría", orden=6)

# --- Qué mide ---------------------------------------------------------------

estilo.seccion("Qué mide")

catalogo = datos.indicadores_disponibles(tabla)
por_bloque: dict[str, list[str]] = {}
for bloque, nombre in catalogo:
    if "(control)" in nombre:      # fila de control de auditoría, no es un indicador publicado
        continue
    por_bloque.setdefault(bloque, []).append(nombre)

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
    f"{total_indicadores} indicadores en {len(BLOQUES)} bloques, para cada ciudad y para cada uno "
    f"de los años 2023, 2024, 2025 y 2026*. El asterisco indica que 2026 cubre solo de enero a "
    f"junio, el último periodo publicado por el DANE al momento del cálculo."
)

# --- Fuera de alcance -------------------------------------------------------

estilo.seccion("Fuera de alcance")

filas_dl = "".join(f"<dt>{t}</dt><dd>{d}</dd>" for t, d in FUERA_DE_ALCANCE)
areas_metro = sum(1 for n in datos.NOMBRES if n.endswith("A.M."))
st.markdown(
    f"""
    <div class="obs-nomide">
      <h4>Lo que este observatorio no mide</h4>
      <div class="intro">Estas preguntas no se pueden responder con las fuentes utilizadas.
      Se listan de forma explícita para evitar que las cifras publicadas se usen para
      responderlas.</div>
      <dl>{filas_dl}</dl>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    f"Dos advertencias generales. {areas_metro} de las 23 unidades corresponden al área "
    f"metropolitana completa y no solo al municipio núcleo, por lo que no son comparables con "
    f"cifras municipales de otra fuente. El error estándar publicado es una cota inferior del "
    f"real, porque los microdatos públicos de la GEIH no incluyen las variables de diseño "
    f"muestral."
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
    f"Datos de {ANIO_REFERENCIA}, el último año completo disponible. Las columnas se ordenan "
    f"haciendo clic en el encabezado. La Ficha de ciudad muestra una sola ciudad en detalle y el "
    f"Comparador sigue la evolución de varias a la vez."
)

notas_unicas = list(dict.fromkeys(notas_vista))
if notas_unicas:
    with st.expander(f"Notas metodológicas de esta vista ({len(notas_unicas)})"):
        for n in notas_unicas:
            st.markdown(f"- {n}")

estilo.pie(estilo.FUENTES)

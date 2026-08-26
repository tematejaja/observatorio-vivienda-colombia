# -*- coding: utf-8 -*-
"""Vista Ficha de ciudad: las mismas 9 secciones del Ficha Markdown
(fichas_ciudades/ficha_*.md), mismo orden, scroll continuo. A diferencia del
Markdown, ningun valor lleva tachado/emoji inline (ADR-0005) - la
confiabilidad se resume en una sola nota al pie al final de la vista."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
import datos_observatorio as datos
import estilo
from config_ciudades import NOMBRE_A_CIUDAD

ANIOS = datos.ANIOS


def fmt(ind: dict | None, tipo: str = "num", decimales: int = 1) -> str:
    if ind is None or not isinstance(ind["valor"], (int, float)):
        return str(ind["valor"]) if ind is not None else "ND"
    v = ind["valor"]
    if tipo == "cop":
        return f"${v:,.0f}"
    if tipo == "pct":
        return f"{v:.{decimales}f}%"
    return f"{v:.{decimales}f}"


def fila_serie(tabla, ciudad, nombre_indicador, tipo="num", decimales=1):
    serie = datos.serie_ciudad(tabla, ciudad, nombre_indicador)
    return [fmt(serie[a], tipo, decimales) for a in ANIOS]


def tabla_series(tabla, ciudad, especificacion, notas_out):
    """especificacion: lista de (etiqueta_fila, nombre_indicador, tipo, decimales)."""
    filas = {}
    for etiqueta, nombre_indicador, tipo, decimales in especificacion:
        filas[etiqueta] = fila_serie(tabla, ciudad, nombre_indicador, tipo, decimales)
        for a in ANIOS:
            notas_out.extend(datos.notas(ciudad, a, nombre_indicador))
    return pd.DataFrame(filas, index=ANIOS).T


def posicion(rankings, ciudad, nombre_ranking, anio="2025"):
    r = datos.ranking(rankings, nombre_ranking, anio)
    fila = r[r["ciudad"] == ciudad]
    if fila.empty or str(fila.iloc[0]["posicion"]) == "ND":
        return None
    return int(fila.iloc[0]["posicion"])


estilo.cabecera(
    antetitulo="Perfil completo · 2023–2026*",
    titulo="Ficha de ciudad",
    bajada="Las nueve secciones del perfil de vivienda de una ciudad, con sus notas al pie.",
)

ciudad = st.selectbox("Ciudad", datos.NOMBRES)
info = NOMBRE_A_CIUDAD[ciudad]

tabla = datos.cargar_tabla_maestra()
rankings = datos.cargar_rankings()
ctrl = datos.cargar_control_geografico()
notas_vista: list[str] = []

ctrl_c = ctrl[ctrl["ciudad_nombre"] == ciudad]
n_total = int(ctrl_c["registros"].sum())
hogares_mes = ctrl_c[ctrl_c["anio"] == 2025]["suma_fex_c18"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Dominio GEIH (AREA)", info["area"])
c2.metric("Departamento", info["dpto_nombre"])
c3.metric("Periodo", "2023–2026*")
st.caption(
    f"Muestra: {n_total:,} hogares encuestados en 42 meses · "
    f"Hogares expandidos (promedio mensual 2025): {hogares_mes:,.0f}"
)
st.info(
    "2026\\* = enero–junio de 2026, único periodo publicado por el DANE. Toda variación de "
    "2026 en esta ficha usa comparación pareada contra los mismos meses de 2025, nunca contra "
    "el año completo.",
    icon=":material/info:",
)

# --- 1. Retrato rápido ---
st.header("1. Retrato rápido (2025)")
retrato = [
    ("Hogares en arriendo", "Tenencia: En arriendo o subarriendo", "pct", 1),
    ("Canon mediano de arriendo", "Canon de arriendo mensual - mediana", "cop", 0),
    ("Arriendo / ingreso del hogar", "Arriendo/ingreso del hogar (mediana)", "pct", 1),
    ("Arrendatarios con sobrecarga (>30 %)",
     "Arrendatarios que destinan >30% del ingreso al arriendo", "pct", 1),
    ("Vivienda propia totalmente pagada", "Tenencia: Propia, totalmente pagada", "pct", 1),
    ("Hogares con hacinamiento",
     "Hogares con hacinamiento (>3 personas/cuarto para dormir)", "pct", 2),
]
filas = []
for etiqueta, nombre_indicador, tipo, decimales in retrato:
    ind = datos.indicador(tabla, ciudad, "2025", nombre_indicador)
    filas.append({"Indicador": etiqueta, "Valor (2025)": fmt(ind, tipo, decimales)})
    notas_vista += datos.notas(ciudad, "2025", nombre_indicador)
st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)

st.markdown("**Posición nacional (entre 23 ciudades, 2025):**")
for etiqueta, nombre_ranking in [
    ("% en arriendo", datos.RANKINGS[0]),
    ("Canon de arriendo", datos.RANKINGS[1]),
    ("Sobrecarga >30 %", datos.RANKINGS[2]),
    ("Hacinamiento", datos.RANKINGS[4]),
]:
    pos = posicion(rankings, ciudad, nombre_ranking)
    if pos:
        st.markdown(f"- **{etiqueta}:** puesto {pos} de 23")

# --- 2. Tenencia ---
st.header("2. ¿Cómo viven los hogares? (tenencia)")
cats = [
    "Propia, totalmente pagada", "Propia, la estan pagando", "En arriendo o subarriendo",
    "En usufructo", "Posesion sin titulo", "Propiedad colectiva", "Otra",
]
etiquetas = [
    "Propia, totalmente pagada", "Propia, la están pagando", "En arriendo o subarriendo",
    "En usufructo", "Posesión sin título", "Propiedad colectiva", "Otra",
]
espec = [(et, f"Tenencia: {cat}", "pct", 2) for cat, et in zip(cats, etiquetas)]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_vista), use_container_width=True)

# --- 3. Mercado de arriendo ---
st.header("3. Mercado de arriendo")
espec = [
    (et, f"Canon de arriendo mensual - {est}", "cop", 0)
    for est, et in [("mediana", "Mediana"), ("promedio", "Promedio"),
                    ("P25", "Percentil 25"), ("P75", "Percentil 75")]
]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_vista), use_container_width=True)
st.caption(
    "Corresponde a P5140, el arriendo efectivamente pagado por hogares arrendatarios. No debe "
    "confundirse con el arriendo imputado (sección 5), que es una estimación del propio hogar "
    "y no un pago real."
)

# --- 4. Esfuerzo financiero ---
st.header("4. ¿Cuánto pesa el arriendo en el bolsillo?")
espec = [
    ("Arriendo / ingreso (mediana)", "Arriendo/ingreso del hogar (mediana)", "pct", 1),
    ("Sobrecarga: >30 % del ingreso",
     "Arrendatarios que destinan >30% del ingreso al arriendo", "pct", 1),
    ("Sobrecarga severa: >50 % del ingreso",
     "Arrendatarios que destinan >50% del ingreso al arriendo", "pct", 1),
]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_vista), use_container_width=True)
st.caption(
    "El umbral del 30 % es la convención internacional de sobrecarga por vivienda. 2026\\* "
    "aparece como ND porque el DANE no publica la medición de Pobreza Monetaria del año en "
    "curso, de la que proviene el ingreso del hogar."
)

st.subheader("Ingresos y pobreza según la tenencia")
espec = [
    ("Ingreso mediano — propietarios", "Ingreso mediano hogares propietarios", "cop", 0),
    ("Ingreso mediano — arrendatarios", "Ingreso mediano hogares arrendatarios", "cop", 0),
    ("Brecha propietarios vs arrendatarios",
     "Brecha de ingreso propietarios vs arrendatarios", "pct", 1),
    ("% arrendatarios en pobreza monetaria", "% arrendatarios en pobreza monetaria", "pct", 1),
    ("% propietarios en pobreza monetaria", "% propietarios en pobreza monetaria", "pct", 1),
    ("% de hogares pobres que viven en arriendo",
     "% hogares pobres que viven en arriendo", "pct", 1),
]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_vista), use_container_width=True)

# --- 5. Vivienda propia ---
st.header("5. Vivienda propia, crédito y arriendo imputado")
espec = [
    ("Valor comercial estimado (mediana)",
     "Valor estimado de venta de la vivienda - mediana", "cop", 0),
    ("Cuota hipotecaria mensual (mediana)", "Cuota hipotecaria mensual - mediana", "cop", 0),
    ("Arriendo imputado (mediana)", "Arriendo imputado (estimado) - mediana", "cop", 0),
]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_vista), use_container_width=True)
st.caption(
    "El arriendo imputado (P5130) es lo que un propietario estima que pagaría si arrendara su "
    "vivienda. Es una valoración hipotética, no un desembolso: no debe sumarse ni compararse "
    "directamente con el canon pagado de la sección 3."
)

# --- 6. Hacinamiento y servicios ---
st.header("6. Espacio habitacional y servicios públicos")
espec = [
    ("Personas por cuarto para dormir (promedio)",
     "Personas por cuarto para dormir - promedio", "num", 2),
    ("Hogares con hacinamiento (>3 pers./cuarto)",
     "Hogares con hacinamiento (>3 personas/cuarto para dormir)", "pct", 2),
    ("Hacinamiento crítico NBI (cuartos totales)",
     "Hogares con hacinamiento critico NBI (>3 personas/cuarto TOTAL)", "pct", 2),
]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_vista), use_container_width=True)

espec = [
    (et, f"Hogares {srv}", "pct", 2)
    for srv, et in [
        ("sin acueducto", "Sin acueducto"),
        ("sin alcantarillado", "Sin alcantarillado"),
        ("sin gas natural conectado a red", "Sin gas natural a red"),
        ("sin energia electrica", "Sin energía eléctrica"),
        ("sin recoleccion de basuras", "Sin recolección de basuras"),
    ]
]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_vista), use_container_width=True)

# --- 7. Déficit habitacional ---
st.header("7. Déficit habitacional — no disponible en esta fase")
espec_deficit = [
    "Deficit habitacional cuantitativo",
    "Deficit habitacional cualitativo",
    "Distribucion por estrato socioeconomico",
]
filas = []
for nombre_indicador in espec_deficit:
    ind = datos.indicador(tabla, ciudad, "2023", nombre_indicador)
    filas.append({"Indicador": nombre_indicador, "Estado": fmt(ind)})
st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
st.caption(
    "Estos indicadores requieren la Encuesta Nacional de Calidad de Vida (ECV), que no forma "
    "parte del alcance de esta fase. No fueron estimados ni aproximados: cualquier cifra de "
    "déficit habitacional atribuida a este observatorio sería incorrecta."
)

# --- Notas metodológicas (reemplaza las secciones 8-9 del Markdown, ADR-0005) ---
st.header("Notas metodológicas de esta ficha")
st.markdown(
    "1. **El margen de error real es mayor al reportado.** Los microdatos públicos de la GEIH "
    "no incluyen variables de diseño muestral (UPM/estrato); la varianza se estimó por "
    "bootstrap agrupando en `DIRECTORIO`, que captura solo parte del efecto de conglomeración. "
    "El error estándar publicado es una cota inferior.\n"
    "2. **El déficit habitacional no está calculado** (sección 7)."
)
notas_unicas = list(dict.fromkeys(notas_vista))
if notas_unicas:
    st.markdown(f"**{len(notas_unicas)} cifra(s) de esta ficha requieren cuidado adicional:**")
    for n in notas_unicas:
        st.markdown(f"- {n}")
else:
    st.markdown("Ninguna cifra de esta ficha quedó marcada con una advertencia adicional.")

st.caption(
    "Fuentes: DANE — GEIH 2023–2026 (catálogos ANDA 782, 819, 853, 900); Pobreza Monetaria y "
    "Desigualdad 2023–2025 (835, 874, 908); Proyecciones de población CNPV 2018."
)

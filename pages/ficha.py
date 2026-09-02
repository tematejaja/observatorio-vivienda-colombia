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
        return estilo.pesos(v)
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
    bajada="Tenencia, arriendo, esfuerzo financiero, hacinamiento y servicios de una ciudad, "
           "con sus notas metodológicas al pie.",
)

ciudad = st.selectbox("Ciudad", datos.NOMBRES)
info = NOMBRE_A_CIUDAD[ciudad]

tabla = datos.cargar_tabla_maestra()
rankings = datos.cargar_rankings()
ctrl = datos.cargar_control_geografico()
notas_vista: list[str] = []

ctrl_c = ctrl[ctrl["ciudad_nombre"] == ciudad]
n_total = int(ctrl_c["registros"].sum())
meses_ciudad = ctrl_c.groupby(["anio", "mes"]).ngroups
hogares_mes = ctrl_c[ctrl_c["anio"] == 2025]["suma_fex_c18"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Dominio GEIH (AREA)", info["area"])
c2.metric("Departamento", info["dpto_nombre"])
c3.metric("Periodo", "2023–2026*")
st.caption(
    f"Muestra: {estilo.numero(n_total)} hogares encuestados en {meses_ciudad} meses · "
    f"Hogares expandidos (promedio mensual 2025): {estilo.numero(hogares_mes)}"
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

# Variacion pareada Ene-Jun 2026 contra los MISMOS meses de 2025 (Principio V).
# Estaba en la ficha Markdown y faltaba aqui: es el punto donde es mas facil
# equivocarse al citar la cifra de 2026*.
temporal = datos.cargar_validacion_temporal()
fila_temp = temporal[
    (temporal["ciudad_nombre"] == ciudad)
    & (temporal["indicador"] == "Canon mediano de arriendo")
]
if not fila_temp.empty:
    r_t = fila_temp.iloc[0]
    homogenea = r_t["variacion_homogenea"]
    ingenua = r_t["variacion_ingenua"]
    sesgo = r_t["sesgo_estacional"]
    st.markdown(
        f"**Variación del canon mediano, 2025 a 2026\\*** (comparación pareada enero–junio): "
        f"**{homogenea:+.1f} %**"
    )
    # El caso que importa no es que las dos cifras difieran, sino que cambie la
    # LECTURA: si la comparacion ingenua es plana o de signo contrario, se avisa.
    if abs(sesgo) >= 1.0 and (abs(ingenua) < 1.0 or (ingenua * homogenea) < 0):
        lectura = (
            "sugeriría que el arriendo no subió"
            if abs(ingenua) < 1.0
            else "sugeriría un movimiento en sentido contrario"
        )
        st.warning(
            f"Comparar 2026\\* contra el año 2025 completo daría {ingenua:+.1f} %, lo que "
            f"{lectura}. Esa diferencia de {abs(sesgo):.1f} pp es efecto estacional y no un "
            f"cambio real de precios. Cite siempre la cifra pareada.",
            icon=":material/warning:",
        )
    else:
        st.caption(
            f"Comparar contra el año 2025 completo daría {ingenua:+.1f} %, un sesgo estacional "
            f"de {sesgo:+.1f} pp. Cite siempre la cifra pareada."
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
st.header("7. Déficit habitacional, materiales y estrato")
st.caption(
    "Fuente distinta al resto de la ficha: Encuesta Nacional de Calidad de Vida (ECV), no GEIH. "
    "Se aplica la metodología oficial de déficit habitacional del DANE (2020) con sus criterios "
    "de cabecera municipal. La réplica reproduce el dato publicado: en cabecera nacional 2024 da "
    "17,18 % contra 17,29 % oficial, y los siete componentes coinciden dentro de 0,07 puntos."
)
# El bloque de deficit no vuelca una nota por fila: por la muestra de la ECV
# tiene decenas de celdas en PRECAUCION o NO PUBLICAR, y enumerarlas una a una
# ahogaria el pie de la ficha. Se consolidan en una sola linea mas abajo
# (ADR-0005: una nota al pie por vista).
notas_deficit = []
espec = [
    ("Déficit habitacional total", "Deficit habitacional total", "pct", 2),
    ("— cuantitativo (estructural)", "Deficit habitacional cuantitativo", "pct", 2),
    ("— cualitativo (subsanable)", "Deficit habitacional cualitativo", "pct", 2),
]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_deficit), use_container_width=True)
st.caption(
    "Las dos categorías son excluyentes: un hogar en déficit cuantitativo no se cuenta además "
    "en cualitativo, así que total = cuantitativo + cualitativo."
)

espec = [
    ("Hacinamiento mitigable", "Componente: hacinamiento mitigable", "pct", 2),
    ("Lugar inadecuado para cocinar", "Componente: lugar inadecuado para cocinar", "pct", 2),
    ("Alcantarillado o sanitario inadecuado",
     "Componente: alcantarillado o sanitario inadecuado", "pct", 2),
    ("Sin acueducto", "Componente: sin acueducto", "pct", 2),
    ("Sin recolección de basuras", "Componente: sin recoleccion de basuras", "pct", 2),
    ("Paredes en material inadecuado", "Paredes en material inadecuado", "pct", 2),
    ("Pisos de tierra, arena o barro", "Pisos de tierra, arena o barro", "pct", 2),
]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_deficit), use_container_width=True)

espec = [
    ("Estrato 1 o 2", "Hogares en estrato 1 o 2", "pct", 2),
    ("Estrato 3", "Hogares en estrato 3", "pct", 2),
    ("Estrato 4, 5 o 6", "Hogares en estrato 4, 5 o 6", "pct", 2),
    ("Sin estrato o no informa", "Hogares sin estrato o no informa", "pct", 2),
]
st.dataframe(tabla_series(tabla, ciudad, espec, notas_deficit), use_container_width=True)

_bloque = tabla[(tabla["ciudad"] == ciudad)
                & (tabla["bloque_indicador"] == "deficit_habitacional")
                & (tabla["anio"] != "2026*")]
_no = int((_bloque["etiqueta_confiabilidad"] == "NO PUBLICAR").sum())
_pre = int((_bloque["etiqueta_confiabilidad"] == "PRECAUCION").sum())
if _no or _pre:
    notas_vista.append(
        f"Sección 7 (déficit, ECV): {_no} estimación(es) marcadas NO PUBLICAR y {_pre} en "
        f"PRECAUCIÓN, por el tamaño de la muestra que la ECV asigna a esta ciudad. Están "
        f"señaladas en las tablas de esa sección; no se enumeran aquí una por una."
    )
st.caption(
    "El estrato se publica agrupado porque con unos 700 hogares de muestra por ciudad los "
    "estratos 4, 5 y 6 por separado no alcanzan precisión utilizable. Es el estrato que el "
    "hogar reporta en su factura de energía. Con la muestra que la ECV asigna a cada ciudad, el "
    "déficit total, el cualitativo, el hacinamiento y el estrato 1 o 2 se estiman con precisión "
    "utilizable; el déficit cuantitativo y los componentes poco frecuentes quedan casi siempre "
    "marcados NO PUBLICAR, lo que no significa que valgan cero sino que la muestra no permite "
    "afirmarlos para una ciudad. 2026* aparece en ND: el DANE aún no publica la ECV 2026."
)

# --- Notas metodológicas (reemplaza las secciones 8-9 del Markdown, ADR-0005) ---
st.header("Notas metodológicas de esta ficha")
st.markdown(
    "1. **El margen de error de las cifras GEIH es mayor al reportado.** Los microdatos "
    "públicos de la GEIH no incluyen variables de diseño muestral (UPM/estrato); su varianza se "
    "estimó por bootstrap agrupando en `DIRECTORIO`, que captura solo parte del efecto de "
    "conglomeración, así que ese error estándar es una cota inferior. No aplica a la sección 7: "
    "la ECV sí publica sus variables de diseño, y allí la varianza se estima con el diseño real "
    "(estrato y UPM).\n"
    "2. **El déficit habitacional viene de otra encuesta** (sección 7): es ECV, no GEIH, y son "
    "años completos distintos a la serie GEIH. No mezcle ambas fuentes en una misma serie."
)
notas_unicas = list(dict.fromkeys(estilo.legible(n) for n in notas_vista))
if notas_unicas:
    st.markdown(
        f"**{len(notas_unicas)} advertencias aplican a las cifras de esta ficha:**"
    )
    for n in notas_unicas:
        st.markdown(f"- {n}")
else:
    st.markdown("Ninguna cifra de esta ficha quedó marcada con una advertencia adicional.")

estilo.pie(estilo.FUENTES)

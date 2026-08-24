# -*- coding: utf-8 -*-
"""Vista Inicio: tabla de 23 ciudades x indicadores clave (equivalente
interactivo de la hoja Resumen_Nacional del Excel). Sin titulares, sin mapa."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
import datos_observatorio as datos

ANIO_REFERENCIA = "2025"

INDICADORES_CLAVE = [
    ("Tenencia: En arriendo o subarriendo", "% en arriendo"),
    ("Canon de arriendo mensual - mediana", "Canon mediano de arriendo (COP)"),
    ("Arriendo/ingreso del hogar (mediana)", "Arriendo / ingreso (mediana, %)"),
    ("Arrendatarios que destinan >30% del ingreso al arriendo", "Sobrecarga >30% (%)"),
    ("Tenencia: Propia, totalmente pagada", "Vivienda propia pagada (%)"),
    ("Hogares con hacinamiento (>3 personas/cuarto para dormir)", "Hacinamiento (%)"),
]

st.title("Observatorio Nacional de Vivienda")
st.caption(
    "23 ciudades capitales y áreas metropolitanas de Colombia · GEIH y Pobreza Monetaria "
    "DANE, 2023–2026\\* · Fase 1 auditada, 0 rechazados."
)

tabla = datos.cargar_tabla_maestra()

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
st.caption(f"Indicadores del año {ANIO_REFERENCIA} (año completo más reciente). Clic en un encabezado para ordenar.")

notas_unicas = list(dict.fromkeys(notas_vista))
if notas_unicas:
    with st.expander(f"Notas metodológicas de esta vista ({len(notas_unicas)})"):
        for n in notas_unicas:
            st.markdown(f"- {n}")

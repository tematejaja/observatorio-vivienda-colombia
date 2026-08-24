# -*- coding: utf-8 -*-
"""Vista Metodología: resumen propio breve (no el .md completo, ver esta
misma decisión en la conversación de diseño) + descargas de los entregables
de la Fase 1."""
import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
OUT_DIR = BASE_DIR / "output"

st.title("Metodología")

st.markdown(
    """
Los indicadores de este observatorio se calculan a partir de microdatos públicos del DANE —
la Gran Encuesta Integrada de Hogares (GEIH) y la medición de Pobreza Monetaria y Desigualdad,
2023 a 2026\\* (2026 parcial: enero-junio) — para las 23 ciudades capitales y áreas
metropolitanas de Colombia. El cálculo (Fase 1) está completo y auditado: 465 controles
red-team aprobados, 0 rechazados.

**Etiqueta de confiabilidad.** Cada Indicador trae una de cuatro etiquetas, según su tamaño de
muestra (n) y coeficiente de variación (CV): **EXCELENTE**, **ACEPTABLE**, **PRECAUCIÓN** (CV
alto o n bajo — usar con cautela) y **NO PUBLICAR** (n < 30 o CV > 25 % — no debe citarse). El
valor nunca se oculta ni se reemplaza; la etiqueta solo indica cuánto cuidado requiere.

**Nota Metodológica.** Cualquier limitación adicional relevante para interpretar una cifra —
desvío frente a la proyección poblacional CNPV, un periodo parcial, que una ciudad sea un área
metropolitana completa, una exclusión de valores extremos — se muestra como texto explícito en
la vista correspondiente, nunca como un cambio silencioso al dato.

**Limitación general del error estándar.** Los microdatos públicos de la GEIH no incluyen
variables de diseño muestral (UPM/estrato); el error estándar se estimó por bootstrap agrupando
en `DIRECTORIO` (la vivienda), que captura solo parte del efecto de conglomeración — es una
cota inferior del error real.

**Déficit habitacional:** no calculado en esta fase (requiere la Encuesta Nacional de Calidad
de Vida, fuera de alcance de la Fase 1).
"""
)

st.subheader("Descargar los entregables")

archivos = [
    ("Tabla maestra (CSV)", OUT_DIR / "observatorio_vivienda_capitales_2023_2026.csv", "text/csv"),
    (
        "Libro Excel nacional (12 hojas)",
        OUT_DIR / "observatorio_vivienda_capitales_2023_2026.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
    (
        "Excel de auditoría red-team",
        OUT_DIR / "auditoria_estadistica_observatorio_nacional.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
    ("Metodología completa (Markdown)", OUT_DIR / "metodologia_observatorio_nacional.md", "text/markdown"),
]

for etiqueta, ruta, mime in archivos:
    if ruta.exists():
        st.download_button(
            etiqueta, data=ruta.read_bytes(), file_name=ruta.name, mime=mime,
            icon=":material/download:",
        )
    else:
        st.caption(f"{etiqueta}: archivo no encontrado ({ruta.name})")

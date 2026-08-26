# -*- coding: utf-8 -*-
"""Vista Metodología: resumen propio breve (no el .md completo, ver esta
misma decisión en la conversación de diseño) + descargas de los entregables
de la Fase 1."""
import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
import estilo

OUT_DIR = BASE_DIR / "output"

estilo.cabecera(
    antetitulo="Cómo se calculó",
    titulo="Metodología",
    bajada="Fuentes, umbrales de confiabilidad y los entregables completos para descargar.",
)

st.markdown(
    """
Los indicadores se calculan a partir de dos fuentes de microdatos públicos del DANE: la Gran
Encuesta Integrada de Hogares (GEIH) y la Medición de Pobreza Monetaria y Desigualdad. El periodo
cubierto va de 2023 a 2026\\*, donde el asterisco indica que 2026 comprende solo de enero a junio.
La cobertura geográfica son las 23 ciudades capitales y áreas metropolitanas del país. El cálculo
está completo y auditado, con 465 controles aprobados y ninguno rechazado.

**Etiqueta de confiabilidad.** Cada indicador trae una de cuatro etiquetas, asignadas según su
tamaño de muestra (n) y su coeficiente de variación (CV): **EXCELENTE**, **ACEPTABLE**,
**PRECAUCIÓN** (CV alto o n bajo) y **NO PUBLICAR** (n < 30 o CV > 25 %). La etiqueta indica el
grado de cuidado que exige la cifra al citarla. El valor se muestra en todos los casos.

**Notas metodológicas.** Las limitaciones que afectan la lectura de una cifra aparecen como texto
en la nota al pie de cada vista. Incluyen el desvío frente a la proyección poblacional CNPV, los
periodos parciales, las ciudades medidas como área metropolitana completa y la exclusión de
valores extremos.

**Error estándar.** Los microdatos públicos de la GEIH no incluyen las variables de diseño
muestral (UPM y estrato). La varianza se estimó por bootstrap agrupando en `DIRECTORIO`, que
captura solo parte del efecto de conglomeración. Por esa razón el error estándar reportado debe
leerse como una cota inferior del real.

**Déficit habitacional.** No se calcula en esta fase. Su estimación requiere la Encuesta Nacional
de Calidad de Vida, que está fuera del alcance del trabajo.
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

estilo.pie(estilo.FUENTES)

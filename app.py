# -*- coding: utf-8 -*-
"""Punto de entrada del Observatorio Nacional de Vivienda.

Ejecutar con: streamlit run app.py

Backend de solo lectura (ADR-0002): esta app nunca dispara el pipeline, solo
lee lo que `script_observatorio_nacional.py` ya dejo en `output/` y
`GEIH/procesado_nacional/` a traves de `scripts/datos_observatorio.py`.
"""
import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

st.set_page_config(
    page_title="Observatorio Nacional de Vivienda",
    page_icon=":material/house:",
    layout="wide",
)

paginas = [
    st.Page("pages/inicio.py", title="Inicio", icon=":material/home:", default=True),
    st.Page("pages/ficha.py", title="Ficha de ciudad", icon=":material/apartment:"),
    st.Page("pages/rankings.py", title="Rankings", icon=":material/leaderboard:"),
    st.Page("pages/comparador.py", title="Comparador", icon=":material/compare_arrows:"),
    st.Page("pages/metodologia.py", title="Metodología", icon=":material/menu_book:"),
]
pg = st.navigation(paginas)
pg.run()

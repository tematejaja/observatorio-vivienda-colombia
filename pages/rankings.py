# -*- coding: utf-8 -*-
"""Vista Rankings: uno de los 5 rankings de FR-011 a la vez (selector de
ranking + selector de año), barras horizontales con las 23 ciudades. Un solo
tono (comparación de magnitud de UN indicador = sequential, no categórico)."""
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
import datos_observatorio as datos
import estilo

COLOR_ACENTO = estilo.TERRACOTA

estilo.cabecera(
    antetitulo="Comparación nacional",
    titulo="Rankings",
    bajada="Las 23 ciudades ordenadas en uno de los cinco indicadores comparables, año por año.",
)

etiquetas_ranking = {r: r.split(". ", 1)[1] for r in datos.RANKINGS}
nombre_ranking = st.selectbox(
    "Ranking", datos.RANKINGS, format_func=lambda r: etiquetas_ranking[r]
)
anio = st.selectbox("Año", datos.ANIOS, index=len(datos.ANIOS) - 2)

rankings_df = datos.cargar_rankings()
tabla = datos.ranking(rankings_df, nombre_ranking, anio)
tabla_valida = tabla.dropna(subset=["valor"])

if tabla_valida.empty:
    st.warning(
        f"Este ranking no tiene datos para {anio}: depende de ingreso/pobreza, que el DANE no "
        "publica para el año en curso. Elija otro año.",
        icon=":material/info:",
    )
else:
    unidad = tabla_valida["unidad"].iloc[0]
    tabla_orden = tabla_valida.sort_values("valor", ascending=True)

    if unidad == "%":
        texto = tabla_orden["valor"].map(lambda v: f"{v:.1f}%")
    elif unidad.upper() == "COP":
        texto = tabla_orden["valor"].map(lambda v: f"${v:,.0f}")
    else:
        texto = tabla_orden["valor"].map(lambda v: f"{v:.1f} {unidad}")

    fig = go.Figure(
        go.Bar(
            x=tabla_orden["valor"],
            y=tabla_orden["ciudad"],
            orientation="h",
            marker_color=COLOR_ACENTO,
            text=texto,
            textposition="outside",
        )
    )
    fig.update_layout(
        height=650,
        margin=dict(l=10, r=40, t=10, b=10),
        xaxis_title=unidad,
        yaxis_title=None,
        transition={"duration": 300, "easing": "cubic-in-out"},
        uniformtext_minsize=10,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    notas_vista = []
    for _, fila in tabla_valida.iterrows():
        notas_vista += datos.notas_ranking(fila)
    notas_unicas = list(dict.fromkeys(notas_vista))
    if notas_unicas:
        with st.expander(f"Notas metodológicas de esta vista ({len(notas_unicas)})"):
            for n in notas_unicas:
                st.markdown(f"- {n}")

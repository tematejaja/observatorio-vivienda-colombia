# -*- coding: utf-8 -*-
"""Vista Comparador: 2 a 6 ciudades elegidas libremente + un indicador
elegido libremente, serie temporal 2023-2026* (una línea por ciudad). A
diferencia del Ranking, ni el conjunto de ciudades ni el de indicadores es
fijo (CONTEXT.md). Paleta categórica validada con dataviz/scripts/
validate_palette.js (CVD-safe en el pairlist adyacente para líneas)."""
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
import datos_observatorio as datos
import estilo

PALETA_CATEGORICA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]

estilo.cabecera(
    antetitulo="Serie 2023–2026*",
    titulo="Comparador",
    bajada="Elija entre dos y seis ciudades y siga la evolución de un mismo indicador.",
)

# Nombre legible de cada bloque: el selector mostraba la llave cruda del CSV
# ("esfuerzo_financiero", "vivienda_propia_credito"), que no es texto de cara al
# publico.
BLOQUES_LEGIBLES = {
    "tenencia": "Tenencia",
    "arriendo": "Mercado de arriendo",
    "esfuerzo_financiero": "Esfuerzo financiero",
    "vivienda_propia_credito": "Vivienda propia y crédito",
    "hacinamiento": "Hacinamiento",
    "servicios_publicos": "Servicios públicos",
    "ingreso_pobreza": "Ingreso y pobreza",
}

# Arranque util en vez del primero alfabetico (que era el percentil 25 del canon).
INDICADOR_INICIAL = ("arriendo", "Canon de arriendo mensual - mediana")

# Indicadores en pesos corrientes. El resto son porcentajes, salvo las dos
# series de personas por cuarto.
_EN_PESOS = ("Canon de arriendo mensual", "Ingreso mediano hogares",
             "Arriendo imputado", "Cuota hipotecaria", "Valor estimado de venta")


def unidad_eje(nombre: str) -> str:
    """Rotulo del eje Y. No basta con 'porcentaje': varios indicadores son
    porcentaje de un subconjunto (arrendatarios, propietarios) o del ingreso,
    no del total de hogares, y rotularlos igual induciria a leerlos mal."""
    if nombre.startswith(_EN_PESOS):
        return "Pesos corrientes"
    if nombre.startswith("Personas por cuarto"):
        return "Personas por cuarto"
    if nombre.startswith("Arriendo/ingreso"):
        return "Porcentaje del ingreso del hogar"
    if nombre.startswith("Brecha de ingreso"):
        return "Diferencia porcentual entre medianas"
    if nombre.startswith("Arrendatarios que destinan") or nombre.startswith("% arrendatarios"):
        return "Porcentaje de arrendatarios"
    if nombre.startswith("% propietarios"):
        return "Porcentaje de propietarios"
    return "Porcentaje de hogares"


def formato_eje(nombre: str) -> str:
    if nombre.startswith(_EN_PESOS):
        return "$,.0f"
    if nombre.startswith("Personas por cuarto"):
        return ".2f"
    return ".1f"

tabla = datos.cargar_tabla_maestra()
opciones = datos.indicadores_disponibles(tabla)
opciones.sort(key=lambda p: (BLOQUES_LEGIBLES.get(p[0], p[0]), p[1]))
etiquetas = {
    par: f"{BLOQUES_LEGIBLES.get(par[0], par[0])} · {estilo.legible(par[1])}"
    for par in opciones
}
indice_inicial = opciones.index(INDICADOR_INICIAL) if INDICADOR_INICIAL in opciones else 0

ciudades_sel = st.multiselect(
    "Ciudades (2 a 6)", datos.NOMBRES, max_selections=6,
    placeholder="Escriba o elija las ciudades",
)
indicador_sel = st.selectbox(
    "Indicador", opciones, index=indice_inicial, format_func=lambda par: etiquetas[par]
)

if len(ciudades_sel) < 2:
    st.info("Elija al menos 2 ciudades para comparar.", icon=":material/info:")
else:
    _, nombre_indicador = indicador_sel
    fig = go.Figure()
    notas_vista = []
    for i, ciudad in enumerate(ciudades_sel):
        serie = datos.serie_ciudad(tabla, ciudad, nombre_indicador)
        y = [
            serie[a]["valor"] if serie[a] and isinstance(serie[a]["valor"], (int, float)) else None
            for a in datos.ANIOS
        ]
        fig.add_trace(
            go.Scatter(
                x=datos.ANIOS,
                y=y,
                name=ciudad,
                mode="lines+markers",
                line=dict(width=2, color=PALETA_CATEGORICA[i % len(PALETA_CATEGORICA)]),
                marker=dict(size=8),
                connectgaps=False,
            )
        )
        for a in datos.ANIOS:
            notas_vista += datos.notas(ciudad, a, nombre_indicador)

    fig.update_yaxes(title_text=unidad_eje(nombre_indicador),
                     tickformat=formato_eje(nombre_indicador))
    fig.update_xaxes(title_text="Año")
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified",
        # separators: decimal, miles. Español usa coma decimal y punto de miles.
        separators=",.",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        transition={"duration": 300, "easing": "cubic-in-out"},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    notas_unicas = list(dict.fromkeys(estilo.legible(n) for n in notas_vista))
    if notas_unicas:
        with st.expander(f"Notas metodológicas de esta vista ({len(notas_unicas)})"):
            for n in notas_unicas:
                st.markdown(f"- {n}")

estilo.pie(estilo.FUENTES)

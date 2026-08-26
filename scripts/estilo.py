# -*- coding: utf-8 -*-
"""
Piezas de presentacion compartidas por las 5 vistas del observatorio.

La mayor parte del tema vive en `.streamlit/config.toml` (fuentes, escala
tipografica, colores, barra lateral) - eso es lo nativo y es donde se debe
tocar primero. Aqui viven solo las piezas que el tema nativo no puede dar:
la cabecera con antetitulo y la fila de cifras de alcance de la portada.

Regla que se mantiene del diseno original: nada de esto anima ni decora un
valor. Las advertencias siguen yendo en la nota al pie consolidada por vista
(ADR-0005), no incrustadas en la cifra.
"""
import streamlit as st

TERRACOTA = "#B5502F"
TERRACOTA_PROFUNDO = "#8A3A1F"
TINTA = "#1C1917"
PIEDRA = "#57534E"
HAIRLINE = "#E7E5E4"
CREMA = "#FBFAF9"

# `.streamlit/config.toml` declara las familias (Fraunces / IBM Plex Sans /
# IBM Plex Mono) y Streamlit las pone en su cadena CSS, pero en 1.55 no llego a
# inyectar el <link> de Google Fonts: verificado midiendo el ancho de un texto
# de prueba, las tres caian al fallback. Se cargan aqui con @import, que si
# funciona y ademas deja el archivo de tema como unica fuente de los NOMBRES.
# El @import tiene que ir primero: el navegador ignora los que van despues de
# cualquier otra regla.
_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

.obs-antetitulo {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {TERRACOTA};
    margin: 0 0 0.35rem 0;
}}
.obs-titulo {{
    font-family: "Fraunces", serif;
    font-size: 2.6rem;
    font-weight: 600;
    line-height: 1.1;
    color: {TINTA};
    margin: 0 0 0.4rem 0;
}}
.obs-bajada {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 1rem;
    color: {PIEDRA};
    margin: 0 0 0.9rem 0;
}}
.obs-regla {{
    border: 0;
    border-top: 2px solid {TINTA};
    margin: 0 0 1.6rem 0;
}}
.obs-tesis {{
    font-family: "Fraunces", serif;
    font-size: 2.05rem;
    font-weight: 400;
    line-height: 1.22;
    color: {TINTA};
    max-width: 26ch;
    margin: 0.6rem 0 1.1rem 0;
}}
.obs-tesis em {{
    font-style: italic;
    color: {TERRACOTA_PROFUNDO};
}}
.obs-entrada {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 1.05rem;
    line-height: 1.62;
    color: {TINTA};
    max-width: 68ch;
    margin: 0 0 0.4rem 0;
}}
.obs-cifra {{
    font-family: "Fraunces", serif;
    font-size: 2.3rem;
    font-weight: 600;
    line-height: 1;
    color: {TERRACOTA_PROFUNDO};
    font-variant-numeric: lining-nums tabular-nums;
}}
.obs-cifra-nota {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.85rem;
    line-height: 1.35;
    color: {PIEDRA};
    margin-top: 0.3rem;
}}
.obs-seccion {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {PIEDRA};
    border-top: 1px solid {HAIRLINE};
    padding-top: 0.75rem;
    margin: 2.2rem 0 0.2rem 0;
}}
.obs-bloque-nombre {{
    font-family: "IBM Plex Sans", sans-serif;
    font-weight: 600;
    font-size: 0.98rem;
    color: {TINTA};
}}
.obs-bloque-detalle {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.88rem;
    line-height: 1.5;
    color: {PIEDRA};
    margin: 0.1rem 0 0.9rem 0;
}}
.obs-nomide {{
    border-left: 3px solid {TERRACOTA};
    background: {CREMA};
    padding: 1.1rem 1.3rem 0.9rem 1.3rem;
    margin-top: 0.4rem;
}}
.obs-nomide h4 {{
    font-family: "Fraunces", serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: {TINTA};
    margin: 0 0 0.2rem 0;
}}
.obs-nomide .intro {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.95rem;
    color: {PIEDRA};
    margin: 0 0 0.9rem 0;
}}
.obs-nomide dl {{ margin: 0; }}
.obs-nomide dt {{
    font-family: "IBM Plex Sans", sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    color: {TINTA};
    margin-top: 0.75rem;
}}
.obs-nomide dd {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.9rem;
    line-height: 1.5;
    color: {PIEDRA};
    margin: 0.1rem 0 0 0;
}}
</style>
"""


def aplicar_estilo() -> None:
    """Inyecta el CSS de las piezas propias. Idempotente por sesion-pagina."""
    st.markdown(_CSS, unsafe_allow_html=True)


def cabecera(antetitulo: str, titulo: str, bajada: str = "") -> None:
    """Cabecera comun a las 5 vistas: antetitulo en versalitas terracota,
    titulo en Fraunces, bajada opcional y una regla gruesa que cierra el
    bloque. Reemplaza a `st.title` para que las vistas no se vean como cinco
    paginas sueltas."""
    aplicar_estilo()
    # Se usa <div> y no <p> a proposito: Streamlit estiliza
    # `[data-testid="stMarkdownContainer"] p`, que gana en especificidad a una
    # clase suelta y pisaba el font-size (la familia si pasaba, el tamano no).
    bloque = [
        f'<div class="obs-antetitulo">{antetitulo}</div>',
        f'<h1 class="obs-titulo">{titulo}</h1>',
    ]
    if bajada:
        bloque.append(f'<div class="obs-bajada">{bajada}</div>')
    bloque.append('<hr class="obs-regla">')
    st.markdown("".join(bloque), unsafe_allow_html=True)


def seccion(texto: str) -> None:
    """Encabezado de seccion: versalitas sobre una linea fina. Mas discreto
    que `st.header` - en una pagina densa de datos el encabezado no debe
    competir con las cifras."""
    st.markdown(f'<div class="obs-seccion">{texto}</div>', unsafe_allow_html=True)


def cifra(valor: str, nota: str) -> None:
    """Una cifra de alcance: numero grande en Fraunces + glosa corta. Sin
    caja ni borde a proposito - es tipografia, no una tarjeta de dashboard."""
    st.markdown(
        f'<div class="obs-cifra">{valor}</div>'
        f'<div class="obs-cifra-nota">{nota}</div>',
        unsafe_allow_html=True,
    )

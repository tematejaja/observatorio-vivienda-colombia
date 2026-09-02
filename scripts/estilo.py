# -*- coding: utf-8 -*-
"""
Piezas de presentacion compartidas por las 5 vistas del observatorio.

La mayor parte del tema vive en `.streamlit/config.toml` (fuentes, escala
tipografica, colores, barra lateral) - eso es lo nativo y es donde se debe
tocar primero. Aqui viven solo las piezas que el tema nativo no puede dar: la
cabecera, las cifras de portada, el ancho y el tamano de la barra lateral, el
pie de pagina y el sistema de movimiento.

Movimiento (lane "Linear": minimo y discreto):
  * Una sola secuencia de entrada, escalonada, de 620 ms en total.
  * Micro-interacciones de 160 ms en lo que se puede senalar o pulsar.
  * Solo se animan `opacity` y `transform` (nunca ancho/alto/posicion).
  * TODA la animacion vive dentro de `prefers-reduced-motion: no-preference`.
    El estado por defecto es el visible: si alguien pide menos movimiento, no
    hay animacion y no hay riesgo de que el contenido quede invisible.
  * En Streamlit el script se re-ejecuta con cada interaccion, asi que la
    secuencia de entrada se aplica solo donde no hay widgets que la disparen a
    cada rato (cabecera y portada), no en las vistas con selectores.

Regla que se mantiene del diseno original: nada de esto anima ni decora un
valor. Las advertencias siguen yendo en la nota al pie consolidada por vista
(ADR-0005), no incrustadas en la cifra.
"""
import re
from pathlib import Path

import streamlit as st

TERRACOTA = "#B5502F"
TERRACOTA_PROFUNDO = "#8A3A1F"
TINTA = "#1C1917"
PIEDRA = "#57534E"
HAIRLINE = "#E7E5E4"
CREMA = "#FBFAF9"

AUTOR = "Nicolás Álvarez Bernal"
AUTOR_ROL = "Economista"
AUTOR_CORREO = "nicolasalvarezbernal@gmail.com"

FUENTES = (
    "Fuentes: DANE. Gran Encuesta Integrada de Hogares 2023–2026 (catálogos ANDA 782, 819, 853 "
    "y 900); Medición de Pobreza Monetaria y Desigualdad 2023–2025 (835, 874 y 908); Encuesta "
    "Nacional de Calidad de Vida 2023–2025 (827, 861 y 905), de donde sale el déficit "
    "habitacional. Proyecciones de población CNPV 2018."
)

MARCA = Path(__file__).resolve().parent.parent / "assets" / "marca.svg"

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

:root {{
    --obs-micro: 160ms;
    --obs-ui: 240ms;
    --obs-entrada: 520ms;
    --obs-salida: cubic-bezier(0.16, 1, 0.3, 1);
}}

/* ---------- Barra lateral ---------- */
section[data-testid="stSidebar"] {{
    width: 336px !important;
    min-width: 336px !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {{
    font-size: 1.06rem;
    font-weight: 500;
    padding-top: 0.62rem;
    padding-bottom: 0.62rem;
    border-radius: 6px;
    transition: background-color var(--obs-micro) ease-out,
                transform var(--obs-micro) var(--obs-salida);
}}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {{
    background-color: #F1EBE8;
    transform: translateX(3px);
}}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span {{
    font-size: inherit;
}}
/* El testid es stSidebarLogo, no stLogo (verificado en el DOM). Streamlit deja
   la marca en 34px aun con size="large"; se sube para que tenga presencia. */
[data-testid="stSidebarLogo"] {{
    height: 2.7rem !important;
    width: auto !important;
    margin-bottom: 0.5rem;
    transition: transform var(--obs-ui) var(--obs-salida);
}}
[data-testid="stLogoLink"]:hover [data-testid="stSidebarLogo"] {{
    transform: scale(1.06) rotate(-1.5deg);
}}

/* ---------- Cabecera ---------- */
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
    transform-origin: left center;
}}

/* ---------- Portada ---------- */
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
    margin: 0 0 0.8rem 0;
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

/* ---------- Pie de pagina ---------- */
.obs-pie {{
    border-top: 1px solid {HAIRLINE};
    margin-top: 3rem;
    padding-top: 1.1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem 3rem;
    justify-content: space-between;
    align-items: flex-start;
}}
.obs-pie-nombre {{
    font-family: "Fraunces", serif;
    font-size: 1.12rem;
    font-weight: 600;
    color: {TINTA};
}}
.obs-pie-rol {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {TERRACOTA};
    margin: 0.12rem 0 0.4rem 0;
}}
.obs-pie a {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.88rem;
    color: {TERRACOTA_PROFUNDO};
    text-decoration: none;
    border-bottom: 1px solid {HAIRLINE};
    transition: border-color var(--obs-micro) ease-out;
}}
.obs-pie a:hover {{ border-color: {TERRACOTA}; }}
.obs-pie-fuente {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.82rem;
    line-height: 1.55;
    color: {PIEDRA};
    max-width: 52ch;
}}

/* ---------- Movimiento ----------
   Todo va dentro de no-preference: el estado por defecto ya es el visible. */
@media (prefers-reduced-motion: no-preference) {{
    @keyframes obs-surgir {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to   {{ opacity: 1; transform: none; }}
    }}
    @keyframes obs-aparecer {{
        from {{ opacity: 0; }}
        to   {{ opacity: 1; }}
    }}
    @keyframes obs-trazar {{
        from {{ transform: scaleX(0); }}
        to   {{ transform: scaleX(1); }}
    }}

    .obs-anim {{
        animation: obs-surgir var(--obs-entrada) var(--obs-salida) both;
    }}
    .obs-antetitulo {{ animation: obs-aparecer 380ms ease-out both; }}
    .obs-titulo     {{ animation: obs-surgir var(--obs-entrada) var(--obs-salida) 60ms both; }}
    .obs-bajada     {{ animation: obs-surgir var(--obs-entrada) var(--obs-salida) 120ms both; }}
    .obs-regla      {{ animation: obs-trazar 620ms var(--obs-salida) 180ms both; }}

    /* Escalonado de 70 ms: da orden de lectura sin que se sienta lento. */
    .obs-anim-1 {{ animation-delay: 240ms; }}
    .obs-anim-2 {{ animation-delay: 310ms; }}
    .obs-anim-3 {{ animation-delay: 380ms; }}
    .obs-anim-4 {{ animation-delay: 450ms; }}
    .obs-anim-5 {{ animation-delay: 520ms; }}
    .obs-anim-6 {{ animation-delay: 590ms; }}

    .obs-nomide {{
        transition: border-left-width var(--obs-ui) var(--obs-salida),
                    background-color var(--obs-ui) ease-out;
    }}
    .obs-nomide:hover {{
        border-left-width: 6px;
        background-color: #F8F3F0;
    }}
}}
</style>
"""


# Los CSV del pipeline guardan los nombres de indicador y las observaciones sin
# tildes (se escribieron asi para evitar problemas de codificacion en consola
# Windows). En pantalla eso se ve descuidado, asi que se restituyen aqui, en la
# capa de presentacion: los datos no se tocan. Solo palabras inequivocas - se
# excluyen a proposito las formas verbales homografas ("publica", "calcula",
# "ganan"), que en estos textos no llevan tilde.
_TILDES = {
    "Deficit": "Déficit", "Definicion": "Definición", "Distribucion": "Distribución",
    "Medicion": "Medición", "Posesion": "Posesión", "auditoria": "auditoría",
    "categorias": "categorías", "critico": "crítico", "electrica": "eléctrica",
    "energia": "energía", "estan": "están", "recoleccion": "recolección",
    "socioeconomico": "socioeconómico", "titulo": "título", "mas": "más",
}
_TILDES_RE = re.compile(r"\b(" + "|".join(map(re.escape, _TILDES)) + r")\b")


def legible(texto: str) -> str:
    """Restituye las tildes que los CSV del pipeline no traen. Se aplica solo
    al mostrar; nunca al comparar o filtrar (las llaves siguen siendo las del
    CSV)."""
    return _TILDES_RE.sub(lambda m: _TILDES[m.group(0)], texto)


def numero(n) -> str:
    """Entero con separador de miles en español (punto): 682.054."""
    return f"{n:,.0f}".replace(",", ".")


def pesos(n) -> str:
    """Importe en pesos con separador español: $600.000. El formato con coma
    de miles ($600,000) se lee como decimales en Colombia."""
    return f"${numero(n)}"


def aplicar_estilo() -> None:
    """Inyecta el CSS de las piezas propias. Idempotente por sesion-pagina."""
    st.markdown(_CSS, unsafe_allow_html=True)


def marca() -> None:
    """Pone la marca en la parte superior de la barra lateral. Es solo el
    simbolo, sin texto: un SVG servido como imagen no puede cargar Fraunces,
    y un logotipo con una tipografia de reemplazo distinta en cada equipo se
    ve peor que ninguno. El nombre completo ya lo lleva el titulo de cada
    pagina, en Fraunces de verdad."""
    if MARCA.exists():
        # Sin `link`: por defecto la marca lleva al inicio de la propia app, que
        # es lo que espera quien la pulsa. Apuntarla a la URL de produccion
        # sacaria al usuario de la copia local.
        st.logo(str(MARCA), size="large")


def cabecera(antetitulo: str, titulo: str, bajada: str = "") -> None:
    """Cabecera comun a las 5 vistas: antetitulo en versalitas terracota,
    titulo en Fraunces, bajada opcional y una regla que se traza de izquierda a
    derecha. Reemplaza a `st.title` para que las vistas no se vean como cinco
    paginas sueltas."""
    aplicar_estilo()
    marca()
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


def cifra(valor: str, nota: str, orden: int = 0) -> None:
    """Una cifra de alcance: numero grande en Fraunces + glosa corta. Sin caja
    ni borde a proposito - es tipografia, no una tarjeta de tablero. `orden`
    (1-6) escalona su entrada dentro de la fila."""
    clase = f"obs-anim obs-anim-{orden}" if orden else ""
    st.markdown(
        f'<div class="{clase}">'
        f'<div class="obs-cifra">{valor}</div>'
        f'<div class="obs-cifra-nota">{nota}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def pie(fuente: str = "") -> None:
    """Pie de pagina con la autoria. Va al final de cada vista."""
    izquierda = (
        f'<div>'
        f'<div class="obs-pie-nombre">{AUTOR}</div>'
        f'<div class="obs-pie-rol">{AUTOR_ROL}</div>'
        f'<a href="mailto:{AUTOR_CORREO}">{AUTOR_CORREO}</a>'
        f"</div>"
    )
    derecha = f'<div class="obs-pie-fuente">{fuente}</div>' if fuente else ""
    st.markdown(f'<div class="obs-pie">{izquierda}{derecha}</div>', unsafe_allow_html=True)

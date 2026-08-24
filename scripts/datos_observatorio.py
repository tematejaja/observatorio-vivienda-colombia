# -*- coding: utf-8 -*-
"""
Modulo compartido de acceso a datos del Observatorio Nacional de Vivienda.

Unico punto de lectura de `output/observatorio_vivienda_capitales_2023_2026.csv`
y de los CSV intermedios de `GEIH/procesado_nacional/` (ADR-0003). Lo usan dos
consumidores: `scripts/30_generar_fichas_ciudades.py` (offline, Ficha Markdown) y
la app de Streamlit en `pages/` (online). Ninguno de los dos debe leer esos
archivos por su cuenta.

Principios de diseno (ver docs/adr/0001 a 0005):
  * Sin base de datos, sin clase intermedia: pandas nativo (ADR-0001, ADR-0004).
  * Backend de solo lectura: este modulo nunca dispara el pipeline (ADR-0002).
  * `valor` se devuelve exactamente como viene del CSV (numerico o el string ND
    que traiga la fuente) - nunca se fabrica un None especial (ADR-0004).
  * Las advertencias metodologicas se devuelven como texto plano via `notas()`;
    quien llama decide como mostrarlas - inline, al pie, etc. (ADR-0003/0004).
"""
from pathlib import Path

import pandas as pd

from config_ciudades import NOMBRES  # noqa: F401  (reexportado para los consumidores)

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "output"
PROC = BASE_DIR / "GEIH" / "procesado_nacional"

CSV_MAESTRO = OUT_DIR / "observatorio_vivienda_capitales_2023_2026.csv"
CSV_RANKINGS = PROC / "rankings_nacionales.csv"
CSV_POBLACIONAL = PROC / "validacion_poblacion_cnpv.csv"
CSV_TEMPORAL = PROC / "validacion_temporal_nacional.csv"
CSV_CONTROL_GEOGRAFICO = BASE_DIR / "GEIH" / "control_geografico_23_ciudades.csv"
CSV_AUDITORIA = PROC / "auditoria_red_team_nacional.csv"

ANIOS = ["2023", "2024", "2025", "2026*"]

# Catalogo cerrado de los 5 rankings (FR-011), en el orden en que se calcularon.
RANKINGS = [
    "1. Inquilinato (% hogares en arriendo)",
    "2. Costo de arriendo (canon mediano)",
    "3. Estres habitacional (% arrendatarios con carga >30%)",
    "4. Desigualdad habitacional (brecha de ingreso propietarios vs arrendatarios)",
    "5. Hacinamiento (% hogares >3 personas/cuarto para dormir)",
]

# bloque_indicador que nunca tiene valor en esta fase (FR-013) - se excluye de
# los selectores interactivos (Comparador) en vez de dejarlo elegible-pero-vacio.
BLOQUE_SIN_DATOS_FASE1 = "deficit_habitacional"

# Puente entre el nombre_indicador del CSV maestro y el nombre mas corto que usa
# validacion_temporal_nacional.csv (los dos archivos nombran el mismo indicador
# distinto porque se generaron en pasos distintos del pipeline).
INDICADOR_A_NOMBRE_TEMPORAL = {
    "Tenencia: En arriendo o subarriendo": "% en arriendo",
    "Canon de arriendo mensual - mediana": "Canon mediano de arriendo",
    "Tenencia: Propia, totalmente pagada": "% propia totalmente pagada",
    "Hogares con hacinamiento (>3 personas/cuarto para dormir)": "% hacinamiento (>3 pers/cuarto dormir)",
}


# --------------------------------------------------------------------------
# Carga cacheada por mtime del archivo: si el pipeline regenera output/ o
# GEIH/procesado_nacional/ mientras la app sigue corriendo, la proxima lectura
# recoge el archivo nuevo sin reiniciar el proceso. Cache propia en vez de
# `st.cache_data`: este modulo lo importa tambien un script de linea de
# comandos sin runtime de Streamlit (ADR-0003), y `st.cache_data` emite
# advertencias de "no runtime found" fuera de `streamlit run`.
# --------------------------------------------------------------------------

_CACHE: dict = {}


def _leer(ruta: Path, **kwargs) -> pd.DataFrame:
    clave = (str(ruta), ruta.stat().st_mtime, tuple(sorted(kwargs.items())))
    if clave not in _CACHE:
        _CACHE[clave] = pd.read_csv(ruta, **kwargs)
    return _CACHE[clave]


def cargar_tabla_maestra() -> pd.DataFrame:
    """`output/observatorio_vivienda_capitales_2023_2026.csv`. Una fila por
    (ciudad, anio, nombre_indicador). Agrega `v`: `valor` convertido a numerico
    (NaN cuando `valor` no es numerico, sea cual sea el texto que traiga)."""
    t = _leer(CSV_MAESTRO, dtype=str).copy()
    t["v"] = pd.to_numeric(t["valor"], errors="coerce")
    t["n_muestral"] = pd.to_numeric(t["n_muestral"], errors="coerce")
    t["cv_pct"] = pd.to_numeric(t["cv_pct"], errors="coerce")
    return t


def cargar_rankings() -> pd.DataFrame:
    """`GEIH/procesado_nacional/rankings_nacionales.csv` - los 5 rankings de
    FR-011, 23 ciudades x 4 anios x 5 rankings."""
    return _leer(CSV_RANKINGS)


def cargar_validacion_poblacional() -> pd.DataFrame:
    """`GEIH/procesado_nacional/validacion_poblacion_cnpv.csv` - desvio de
    `FEX_C18` frente a la proyeccion CNPV 2018, por ciudad-anio. `anio` es
    entero plano (2023-2026), sin el asterisco de periodo parcial."""
    return _leer(CSV_POBLACIONAL)


def cargar_validacion_temporal() -> pd.DataFrame:
    """`GEIH/procesado_nacional/validacion_temporal_nacional.csv` - variacion
    pareada Ene-Jun 2026 vs Ene-Jun 2025 para los 4 indicadores cubiertos
    (ver `INDICADOR_A_NOMBRE_TEMPORAL`). Siempre 2026 vs 2025; no tiene columna
    `anio` porque no aplica a otros anios."""
    return _leer(CSV_TEMPORAL)


def cargar_control_geografico() -> pd.DataFrame:
    """`GEIH/control_geografico_23_ciudades.csv` - grano ciudad-anio-mes.
    `anio` es entero plano (2023-2026)."""
    return _leer(CSV_CONTROL_GEOGRAFICO)


def cargar_auditoria() -> pd.DataFrame:
    """`GEIH/procesado_nacional/auditoria_red_team_nacional.csv` - veredictos
    de las 4 pruebas red-team (465 aprobados / 25 advertencias / 0 rechazados)."""
    return _leer(CSV_AUDITORIA)


# --------------------------------------------------------------------------
# Consultas (sin cache propio - trabajan sobre DataFrames ya cargados y
# cacheados arriba, son baratas).
# --------------------------------------------------------------------------

def indicadores_disponibles(tabla: pd.DataFrame | None = None, incluir_deficit: bool = False):
    """Catalogo (bloque_indicador, nombre_indicador) presente en la tabla
    maestra, en el orden en que aparecen las columnas. Por defecto excluye
    `deficit_habitacional` (siempre ND en esta fase, FR-013) para no ofrecer
    en un selector interactivo indicadores que nunca tienen valor."""
    if tabla is None:
        tabla = cargar_tabla_maestra()
    pares = (
        tabla[["bloque_indicador", "nombre_indicador"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )
    if incluir_deficit:
        return list(pares)
    return [p for p in pares if p[0] != BLOQUE_SIN_DATOS_FASE1]


def _fila(tabla: pd.DataFrame, ciudad: str, anio: str, nombre_indicador: str):
    f = tabla[
        (tabla["ciudad"] == ciudad)
        & (tabla["anio"] == anio)
        & (tabla["nombre_indicador"] == nombre_indicador)
    ]
    return f.iloc[0] if len(f) else None


def indicador(tabla: pd.DataFrame, ciudad: str, anio: str, nombre_indicador: str) -> dict | None:
    """Un Indicador puntual: Ciudad x Periodo x nombre_indicador. `valor` es el
    float ya calculado, o el string ND exacto que trae el CSV (puede traer
    contexto propio, p. ej. "ND - pendiente Fase 2 (ECV)") - nunca se
    normaliza ni se reemplaza (ADR-0004). None si la combinacion no existe."""
    r = _fila(tabla, ciudad, anio, nombre_indicador)
    if r is None:
        return None
    valor = r["v"] if pd.notna(r["v"]) else r["valor"]
    return {
        "ciudad": ciudad,
        "anio": anio,
        "nombre_indicador": nombre_indicador,
        "valor": valor,
        "error_estandar": r["error_estandar"] if pd.notna(r["error_estandar"]) else None,
        "ic95_inf": r["ic95_inf"] if pd.notna(r["ic95_inf"]) else None,
        "ic95_sup": r["ic95_sup"] if pd.notna(r["ic95_sup"]) else None,
        "deff": r["deff"] if pd.notna(r["deff"]) else None,
        "n_muestral": int(r["n_muestral"]) if pd.notna(r["n_muestral"]) else None,
        "cv_pct": float(r["cv_pct"]) if pd.notna(r["cv_pct"]) else None,
        "etiqueta_confiabilidad": r["etiqueta_confiabilidad"],
        "fuente": r["fuente"],
    }


def serie_ciudad(tabla: pd.DataFrame, ciudad: str, nombre_indicador: str) -> dict:
    """El Indicador de una ciudad a lo largo de los 4 anios (`ANIOS`). Usado
    por la Ficha (las 9 secciones) y por el Comparador (una serie por ciudad
    elegida). Devuelve {anio: indicador() o None}."""
    return {a: indicador(tabla, ciudad, a, nombre_indicador) for a in ANIOS}


def ranking(rankings: pd.DataFrame, nombre_ranking: str, anio: str) -> pd.DataFrame:
    """Las 23 ciudades del ranking `nombre_ranking` (uno de `RANKINGS`) para
    `anio`, ordenadas por posicion. `valor` viene convertido a numerico (NaN
    en las filas ND - algunos rankings quedan ND por completo en 2026* porque
    dependen de ingreso/pobreza, que el DANE no publica para el ano en curso).
    A diferencia del Comparador, el conjunto de ciudades y el indicador no los
    elige quien consulta (ver CONTEXT.md)."""
    r = rankings[(rankings["ranking"] == nombre_ranking) & (rankings["anio"] == anio)].copy()
    r["posicion_num"] = pd.to_numeric(r["posicion"], errors="coerce")
    r["valor"] = pd.to_numeric(r["valor"], errors="coerce")
    return r.sort_values("posicion_num").drop(columns="posicion_num")


def _nota_confiabilidad(etiqueta, n, cv, contexto: str) -> list[str]:
    """Nota de confiabilidad n/CV a partir de una fila que ya trae
    etiqueta_confiabilidad/n_muestral/cv_pct - la usan tanto `notas()` (filas
    de la tabla maestra) como `notas_ranking()` (filas de un Ranking, que
    traen su propia etiqueta/n/CV en vez de la del indicador base)."""
    n = int(n) if pd.notna(n) else None
    cv = float(cv) if pd.notna(cv) else None
    detalle = f"n={n}" + (f", CV={cv:.1f}%" if cv is not None else "")
    if etiqueta == "NO PUBLICAR":
        return [f"{contexto}: NO PUBLICAR ({detalle}) — no debe citarse."]
    if etiqueta == "PRECAUCION":
        return [f"{contexto}: PRECAUCIÓN ({detalle}) — usar con cautela."]
    return []


def _nota_area_metropolitana(ciudad: str) -> list[str]:
    if ciudad.endswith("A.M."):
        return [
            f"{ciudad}: esta cifra corresponde al área metropolitana completa, no solo al "
            f"municipio núcleo — no comparable directamente con cifras municipales de otra fuente."
        ]
    return []


def notas_ranking(fila_ranking) -> list[str]:
    """Notas para una fila de `ranking()` (una ciudad dentro de un Ranking):
    confiabilidad propia de esa posición + área metropolitana. No pasa por la
    tabla maestra - un Ranking ya trae su propia n/CV/etiqueta (ver
    `rankings_nacionales.csv`)."""
    ciudad = fila_ranking["ciudad"]
    out = _nota_confiabilidad(
        fila_ranking["etiqueta_confiabilidad"],
        fila_ranking["n_muestral"],
        fila_ranking["cv_pct"],
        contexto=ciudad,
    )
    if fila_ranking["etiqueta_confiabilidad"] in ("NO PUBLICAR", "PRECAUCION"):
        obs = fila_ranking.get("observacion")
        if isinstance(obs, str) and obs.strip():
            out.append(f"{ciudad}: {obs.strip()}")
    out += _nota_area_metropolitana(ciudad)
    return out


def notas(ciudad: str, anio: str, nombre_indicador: str | None = None) -> list[str]:
    """Toda Nota Metodologica que aplica a este Indicador (o, si
    `nombre_indicador` es None, solo las de nivel ciudad-anio): confiabilidad
    n/CV, la razon detras de un ND, desvio poblacional CNPV, sesgo estacional
    2026*, area metropolitana completa, periodo parcial. Nunca oculta ni
    reemplaza el valor (ADR-0004) - solo lo acompana. Quien llama agrega/dedupe
    las de varias celdas para la nota al pie consolidada de una vista
    (ADR-0005)."""
    out: list[str] = []

    if nombre_indicador is not None:
        tabla = cargar_tabla_maestra()
        r = _fila(tabla, ciudad, anio, nombre_indicador)
        if r is not None:
            contexto = f"{nombre_indicador} ({anio})"
            et = r["etiqueta_confiabilidad"]
            out += _nota_confiabilidad(et, r["n_muestral"], r["cv_pct"], contexto)
            obs = r.get("observacion")
            # `observacion` tambien carga texto rutinario sin valor de
            # advertencia (exclusion de outliers, % de match de un merge,
            # notas definicionales) en filas EXCELENTE/ACEPTABLE - la ficha
            # Markdown nunca lo muestra. Solo se surface cuando de verdad
            # explica algo: por que esta fila esta senalada (NO PUBLICAR/
            # PRECAUCION) o por que no tiene valor (ND/NO_APLICA).
            if et in ("NO PUBLICAR", "PRECAUCION") and isinstance(obs, str) and obs.strip():
                out.append(f"{contexto}: {obs.strip()}")
            elif et in ("ND", "NO_APLICA") and isinstance(obs, str) and obs.strip():
                # Sin el prefijo de indicador/anio: el mismo motivo estructural
                # (p. ej. "el DANE no publica X para 2026") se repite identico
                # en varios indicadores - sin prefijo, el dedup de quien llama
                # lo colapsa en una sola linea en vez de una por indicador.
                out.append(obs.strip())

        # Sesgo estacional 2026* pareado - solo aplica al subconjunto de
        # indicadores cubiertos por validacion_temporal_nacional.csv.
        nombre_temporal = INDICADOR_A_NOMBRE_TEMPORAL.get(nombre_indicador)
        if anio == "2026*" and nombre_temporal is not None:
            temp = cargar_validacion_temporal()
            tt = temp[
                (temp["ciudad_nombre"] == ciudad) & (temp["indicador"] == nombre_temporal)
            ]
            if not tt.empty:
                fila_t = tt.iloc[0]
                hom, ing, sesgo = (
                    fila_t["variacion_homogenea"],
                    fila_t["variacion_ingenua"],
                    fila_t["sesgo_estacional"],
                )
                if abs(sesgo) >= 1.0 and (abs(ing) < 1.0 or (ing * hom) < 0):
                    out.append(
                        f"{nombre_indicador}: comparar 2026* contra el año 2025 completo daría "
                        f"{ing:+.1f}% en vez de la variación pareada ({hom:+.1f}%) — "
                        f"{abs(sesgo):.1f} pp de efecto estacional, no cambio real. "
                        f"Cite siempre la cifra pareada."
                    )

    # Desvio poblacional CNPV - a nivel ciudad-anio, independiente del indicador.
    anio_plano = int(str(anio).rstrip("*"))
    pob = cargar_validacion_poblacional()
    pv = pob[(pob["ciudad_nombre"] == ciudad) & (pob["anio"] == anio_plano)]
    if not pv.empty and pv.iloc[0]["estado_poblacional"] == "REVISAR":
        out.append(
            f"{ciudad} ({anio}): desvío poblacional fuera de tolerancia frente a la proyección "
            f"CNPV 2018 — es una divergencia de calibración de FEX_C18, no un error de "
            f"identificación geográfica; afecta los niveles absolutos de población expandida, "
            f"no los porcentajes ni las medianas."
        )

    # Area metropolitana completa - a nivel ciudad, constante.
    out += _nota_area_metropolitana(ciudad)

    # Periodo parcial 2026* - a nivel anio, constante.
    if anio == "2026*":
        out.append(
            "2026* = enero–junio, único periodo publicado por el DANE al momento del cálculo — "
            "toda variación frente a 2026* debe usar comparación pareada, nunca el año completo."
        )

    return out

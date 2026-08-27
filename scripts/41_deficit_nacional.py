# -*- coding: utf-8 -*-
"""
FASE 2 - Paso 1: deficit habitacional, validado contra el anexo oficial.

Antes de desagregar por ciudad hay que demostrar que la replica de la
metodologia DANE 2020 reproduce las cifras que el propio DANE publico. Si no
cuadra, el mapeo de variables tiene un error y desagregar solo lo propagaria a
23 ciudades.

Blanco de validacion: anexo oficial `anex-ECV-2024.xlsx`, "Cuadro 10 - Hogares
por deficit habitacional segun tipo y componentes". Se compara contra la columna
**jerarquizado** de cada componente, que es la excluyente (un hogar cuenta una
sola vez), igual que este calculo.

Ojo: circulan en prensa un 19,6% de cabeceras y un 65,5% de resto que NO
corresponden a ese cuadro. Las cifras del anexo son 17,29% y 61,20%.
"""
import io
import sys
import zipfile
from pathlib import Path

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from config_ciudades import stdout_utf8
import config_deficit as cfg

BASE_DIR = SCRIPTS_DIR.parent
ECV_DIR = BASE_DIR / "GEIH" / "ECV"

# Variables del modulo "Servicios del hogar", identificadas contra el formulario
# ECV 2024 (cap. C) y confirmadas por calibracion contra el anexo oficial.
VAR_SANITARIO = "P8526"     # preg. 8. Su codigo 1 da 49,2%, que cuadra con el
                            # 50,3% de "si tiene alcantarillado".
VAR_COCINA = "P764"         # preg. 30. {2,3,5} da 3,15% en cabecera frente al
                            # 3,11% publicado. P5041 NO es esta variable, pese a
                            # tener tambien 6 categorias.

# preg. 8: 1=inodoro a alcantarillado, 2=a pozo septico, 3=inodoro sin conexion,
#          4=letrina, 5=descarga directa (bajamar), 6=no tiene sanitario
SANITARIO_DEFICIENTE_CABECERA = {2, 3, 4, 5, 6}
# preg. 30: 2=cuarto usado tambien para dormir, 3=sala-comedor sin lavaplatos,
#           5=patio/corredor/enramada/aire libre.  6 = no cocinan -> NO es deficit
COCINA_DEFICIENTE_CABECERA = {2, 3, 5}


def _csv(nombre: str) -> pd.DataFrame:
    z = zipfile.ZipFile(ECV_DIR / nombre)
    archivo = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    df = pd.read_csv(io.BytesIO(z.read(archivo)), sep=None, engine="python",
                     dtype=str, encoding="latin-1")
    df.columns = [c.upper().strip() for c in df.columns]
    return df


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def construir(anio: int) -> pd.DataFrame:
    viv = _csv(f"ecv_{anio}_vivienda.zip")
    ser = _csv(f"ecv_{anio}_servicios.zip")

    # El capitulo de vivienda se diligencia solo para el hogar 01, asi que sus
    # caracteristicas son de la VIVIENDA y se replican a todos sus hogares.
    cols_viv = ["DIRECTORIO", "CLASE", cfg.VAR_TIPO_VIVIENDA, cfg.VAR_PAREDES,
                cfg.VAR_PISOS, cfg.VAR_ENERGIA, cfg.VAR_ACUEDUCTO,
                cfg.VAR_ALCANTARILLADO, cfg.VAR_BASURAS,
                cfg.VAR_HOGARES_EN_VIVIENDA, "P1_DEPARTAMENTO", "P1_MUNICIPIO"]
    cols_ser = ["DIRECTORIO", "SECUENCIA_P", "FEX_C", cfg.VAR_CUARTOS_DORMIR,
                cfg.VAR_PERSONAS_HOGAR, VAR_SANITARIO, VAR_COCINA]

    h = ser[cols_ser].merge(viv[cols_viv], on="DIRECTORIO", how="inner")
    for c in h.columns:
        if c != "DIRECTORIO":
            h[c] = num(h[c])

    h["_personas_vivienda"] = h.groupby("DIRECTORIO")[cfg.VAR_PERSONAS_HOGAR].transform("sum")
    h["_personas_cuarto"] = h[cfg.VAR_PERSONAS_HOGAR] / h[cfg.VAR_CUARTOS_DORMIR]
    return h


def calcular(h: pd.DataFrame) -> pd.DataFrame:
    d = h.copy()
    cab = d["CLASE"] == 1                     # 1 = cabecera municipal

    # Excluidos del calculo completo: vivienda tradicional indigena [NM p.5]
    d["_excluido"] = d[cfg.VAR_TIPO_VIVIENDA].isin(cfg.TIPO_VIVIENDA_EXCLUIR)

    # --- CUANTITATIVO -----------------------------------------------------
    c_tipo = d[cfg.VAR_TIPO_VIVIENDA].isin(cfg.TIPO_VIVIENDA_DEFICIENTE)
    c_pared = d[cfg.VAR_PAREDES].isin(cfg.PAREDES_DEFICIENTE)

    # Cohabitacion: 3+ hogares en la vivienda; o 2 hogares y >6 personas en la
    # vivienda. Se excluyen hogares principales y unipersonales [NM p.7].
    secundario = (d["SECUENCIA_P"] != 1) & (d[cfg.VAR_PERSONAS_HOGAR] > 1)
    c_cohab = secundario & (
        (d[cfg.VAR_HOGARES_EN_VIVIENDA] >= cfg.COHABITACION_HOGARES_MINIMO)
        | ((d[cfg.VAR_HOGARES_EN_VIVIENDA] == 2)
           & (d["_personas_vivienda"] > cfg.COHABITACION_DOS_HOGARES_PERSONAS))
    )
    c_hacin = d["_personas_cuarto"] > cfg.HACINAMIENTO_NO_MITIGABLE

    d["cuantitativo"] = (c_tipo | c_pared | c_cohab | c_hacin) & ~d["_excluido"]

    # --- CUALITATIVO (excluyente del cuantitativo) [NM p.9] ----------------
    bajo, alto = cfg.HACINAMIENTO_MITIGABLE
    componentes = {
        "q_hacin": (d["_personas_cuarto"] > bajo) & (d["_personas_cuarto"] <= alto),
        "q_piso": d[cfg.VAR_PISOS].isin(cfg.PISOS_DEFICIENTE),
        "q_cocina": cab & d[VAR_COCINA].isin(COCINA_DEFICIENTE_CABECERA),
        "q_agua": cab & (d[cfg.VAR_ACUEDUCTO] == cfg.NO),
        "q_alcan": cab & ((d[cfg.VAR_ALCANTARILLADO] == cfg.NO)
                          | d[VAR_SANITARIO].isin(SANITARIO_DEFICIENTE_CABECERA)),
        "q_energia": d[cfg.VAR_ENERGIA] == cfg.NO,
        "q_basura": d[cfg.VAR_BASURAS] == cfg.NO,
    }
    union = None
    for nombre, serie in componentes.items():
        union = serie if union is None else (union | serie)
        d[nombre] = serie & ~d["cuantitativo"] & ~d["_excluido"]

    d["cualitativo"] = union & ~d["cuantitativo"] & ~d["_excluido"]
    d["deficit"] = d["cuantitativo"] | d["cualitativo"]
    return d


def pct(d: pd.DataFrame, mascara, filtro=None) -> float:
    base = d if filtro is None else d[filtro]
    m = mascara if filtro is None else mascara[filtro]
    w = base["FEX_C"]
    valido = ~base["_excluido"]
    return 100 * (w[m & valido].sum() / w[valido].sum())


def main() -> None:
    stdout_utf8()
    print("FASE 2 · Paso 1 — déficit habitacional, validación contra el anexo oficial")
    print("=" * 78)

    for anio in (2023, 2024):
        d = calcular(construir(anio))
        cab = d["CLASE"] == 1
        o = cfg.VALIDACION_OFICIAL.get(anio, {})

        def linea(etiqueta, calc, clave, tol=0.5):
            of = o.get(clave)
            if of is None:
                print(f"  {etiqueta:<34}{calc:>9.2f}%{'—':>10}")
                return
            dif = calc - of
            marca = "OK" if abs(dif) <= tol else ("~" if abs(dif) <= 1.5 else "XX")
            print(f"  {etiqueta:<34}{calc:>9.2f}%{of:>8.2f}%{dif:>+8.2f}  {marca}")

        print("")
        print("-" * 78)
        print(f"{anio}   ({len(d):,} hogares · "
              f"{int(d['_excluido'].sum()):,} excluidos por vivienda indígena)")
        print(f"  {'indicador':<34}{'calculado':>10}{'DANE':>9}{'dif':>8}")

        linea("CABECERA · déficit total", pct(d, d["deficit"], cab), "total_cabecera")
        linea("CABECERA · cuantitativo", pct(d, d["cuantitativo"], cab), "cuantitativo_cabecera")
        linea("CABECERA · cualitativo", pct(d, d["cualitativo"], cab), "cualitativo_cabecera")
        print("  " + "-" * 58)
        for etiq, col, clave in [
            ("  comp. hacinamiento mitigable", "q_hacin", "cab_hacinamiento_mitigable"),
            ("  comp. material de pisos", "q_piso", "cab_pisos"),
            ("  comp. lugar donde cocina", "q_cocina", "cab_cocina"),
            ("  comp. agua para cocinar", "q_agua", "cab_agua"),
            ("  comp. alcantarillado", "q_alcan", "cab_alcantarillado"),
            ("  comp. energía eléctrica", "q_energia", "cab_energia"),
            ("  comp. recolección basuras", "q_basura", "cab_basuras"),
        ]:
            linea(etiq, pct(d, d[col], cab), clave, tol=0.3)
        print("  " + "-" * 58)
        linea("NACIONAL · déficit total", pct(d, d["deficit"]), "total_nacional")
        linea("NACIONAL · cuantitativo", pct(d, d["cuantitativo"]), "cuantitativo_nacional")
        linea("RESTO · déficit total", pct(d, d["deficit"], ~cab), "total_resto")

    print("")
    print("=" * 78)
    print("El bloque RESTO no se puede reproducir, y no se pretende: la ECV publica CLASE")
    print("con solo dos valores (1=cabecera, 2=resto), mientras que la metodología del")
    print("DANE aplica reglas distintas a centros poblados y a rural disperso (basuras")
    print("solo en centros poblados; hacinamiento no mitigable excluido en rural")
    print("disperso). Sin esa distinción el resto queda sobreestimado, y con él el total")
    print("nacional. No afecta al observatorio: las 23 ciudades son todas cabecera.")


if __name__ == "__main__":
    main()

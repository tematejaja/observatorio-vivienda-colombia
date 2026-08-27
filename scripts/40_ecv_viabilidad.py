# -*- coding: utf-8 -*-
"""
FASE 2 - Paso 0: estudio de viabilidad de la ECV para las 23 ciudades.

NO calcula deficit habitacional. Su unico proposito es responder, con datos y no
con supuestos, la pregunta que la Fase 1 dejo abierta (ver research.md, Decision
4): **la Encuesta Nacional de Calidad de Vida, cuyo diseno muestral esta pensado
para departamentos y 9 regiones, tiene muestra suficiente para estimar por
separado cada una de las 23 ciudades capitales?**

Lo que se sabe de la ficha metodologica oficial (DSO-ECV-FME-001 v12, feb-2025):
  * Muestra 2024: 77.400 hogares esperados en TODO el pais.
  * El error marginal se fija por departamento y area (2,5% cabecera en
    departamentos antiguos, 4,0% en los nuevos), NO por ciudad.
  * Las capitales estan en un "estrato de inclusion forzosa": cada capital SI
    entra en la muestra todos los anios. Por eso la pregunta no es si aparecen,
    sino con cuantos hogares.
  * A diferencia de la GEIH, la ECV SI publica variables de diseno muestral
    (ESTRATO2020, SEGMENTO), asi que aqui la varianza se puede estimar bien y no
    haria falta el bootstrap por DIRECTORIO de la Fase 1.

Salida: GEIH/procesado_nacional/ecv_viabilidad_23ciudades.csv y un resumen por
consola con el veredicto por ciudad-anio segun los umbrales del Principio VI.
"""
import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from config_ciudades import CIUDADES, stdout_utf8

BASE_DIR = SCRIPTS_DIR.parent
ECV_DIR = BASE_DIR / "GEIH" / "ECV"
SALIDA = BASE_DIR / "GEIH" / "procesado_nacional" / "ecv_viabilidad_23ciudades.csv"

# Modulo "Datos de la vivienda": es el que trae P1_DEPARTAMENTO / P1_MUNICIPIO,
# CLASE y FEX_C. file_id extraido de la pestana "Obtener Microdatos" de cada
# catalogo (mismo patron ya verificado para la GEIH).
ECV_VIVIENDA = {
    2023: ("https://microdatos.dane.gov.co/index.php/catalog/827/download/23439", "ecv_2023_vivienda.zip"),
    2024: ("https://microdatos.dane.gov.co/index.php/catalog/861/download/23948", "ecv_2024_vivienda.zip"),
    2025: ("https://microdatos.dane.gov.co/index.php/catalog/905/download/24628", "ecv_2025_vivienda.zip"),
}

# HIPOTESIS, no verdad asumida (Principio II): en DIVIPOLA la capital de cada
# departamento suele ser el municipio `DD001`. El script lo VERIFICA contra los
# codigos que realmente aparecen en los microdatos antes de usarlo.
CAPITALES_HIPOTESIS = {c["nombre"]: c["dpto_divipola"].zfill(2) + "001" for c in CIUDADES}

# Umbrales del Principio VI ya usados en la Fase 1.
N_MINIMO_PUBLICAR = 30
N_MINIMO_HOLGADO = 100


def descargar(anio: int) -> Path:
    url, nombre = ECV_VIVIENDA[anio]
    destino = ECV_DIR / nombre
    if destino.exists() and destino.stat().st_size > 0:
        print(f"  {anio}: ya descargado ({destino.stat().st_size:,} bytes)")
        return destino
    ECV_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  {anio}: descargando...", end=" ", flush=True)
    r = requests.get(url, timeout=180, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    destino.write_bytes(r.content)
    print(f"{len(r.content):,} bytes")
    return destino


def leer_vivienda(ruta_zip: Path) -> pd.DataFrame:
    """Lee el modulo de vivienda del ZIP. El DANE publica la ECV en DBF (y a
    veces CSV/SAV); se intenta en ese orden."""
    with zipfile.ZipFile(ruta_zip) as z:
        nombres = z.namelist()
        csvs = [n for n in nombres if n.lower().endswith(".csv")]
        dbfs = [n for n in nombres if n.lower().endswith(".dbf")]
        if csvs:
            with z.open(csvs[0]) as f:
                return pd.read_csv(io.BytesIO(f.read()), sep=None, engine="python",
                                   dtype=str, encoding="latin-1")
        if dbfs:
            from dbfread import DBF   # noqa: PLC0415
            destino = ruta_zip.parent / dbfs[0]
            if not destino.exists():
                z.extract(dbfs[0], ruta_zip.parent)
            return pd.DataFrame(iter(DBF(str(destino), encoding="latin-1", char_decode_errors="ignore")))
        raise RuntimeError(f"El ZIP no trae CSV ni DBF: {nombres[:8]}")


def main() -> None:
    stdout_utf8()
    print("FASE 2 · Paso 0 — viabilidad de la ECV para las 23 ciudades")
    print("=" * 74)

    filas = []
    for anio in sorted(ECV_VIVIENDA):
        try:
            ruta = descargar(anio)
            viv = leer_vivienda(ruta)
        except Exception as e:
            print(f"  {anio}: NO SE PUDO LEER ({type(e).__name__}: {e})")
            continue

        viv.columns = [c.upper().strip() for c in viv.columns]
        col_dpto = next((c for c in viv.columns if "DEPARTAMENTO" in c), None)
        col_mpio = next((c for c in viv.columns if "MUNICIPIO" in c), None)
        col_clase = "CLASE" if "CLASE" in viv.columns else None
        print(f"  {anio}: {len(viv):,} viviendas · columnas geográficas: "
              f"{col_dpto}, {col_mpio}, {col_clase}")
        if not (col_dpto and col_mpio):
            print(f"     -> sin identificador municipal; columnas: {list(viv.columns)[:14]}")
            continue

        # Codigo DIVIPOLA completo = departamento(2) + municipio(3)
        viv["_divipola"] = (viv[col_dpto].astype(str).str.strip().str.zfill(2)
                            + viv[col_mpio].astype(str).str.strip().str.zfill(3).str[-3:])

        presentes = set(viv["_divipola"].unique())
        for nombre, codigo in CAPITALES_HIPOTESIS.items():
            sub = viv[viv["_divipola"] == codigo]
            n = len(sub)
            n_cabecera = int((sub[col_clase].astype(str).str.strip() == "1").sum()) if col_clase and n else n
            filas.append({
                "anio": anio, "ciudad": nombre, "divipola_hipotesis": codigo,
                "codigo_existe_en_ecv": codigo in presentes,
                "n_viviendas": n, "n_viviendas_cabecera": n_cabecera,
                "veredicto": ("SIN_DATOS" if n == 0 else
                              "NO_PUBLICAR" if n_cabecera < N_MINIMO_PUBLICAR else
                              "PRECAUCION" if n_cabecera < N_MINIMO_HOLGADO else
                              "SUFICIENTE"),
            })

    if not filas:
        print("\nNo se obtuvo ninguna tabla legible. Nada que concluir.")
        return

    res = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(SALIDA, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 74)
    print("MUESTRA POR CIUDAD (viviendas en cabecera)")
    print("=" * 74)
    tabla = res.pivot_table(index="ciudad", columns="anio", values="n_viviendas_cabecera",
                            aggfunc="first").fillna(0).astype(int)
    tabla["mín"] = tabla.min(axis=1)
    print(tabla.sort_values("mín").to_string())

    print("\n" + "=" * 74)
    print("VEREDICTO")
    print("=" * 74)
    for anio, grupo in res.groupby("anio"):
        conteo = grupo["veredicto"].value_counts().to_dict()
        print(f"  {anio}: {conteo}")
    flojas = sorted(set(res[res["veredicto"].isin(["SIN_DATOS", "NO_PUBLICAR"])]["ciudad"]))
    if flojas:
        print(f"\n  Ciudades bajo el umbral de n={N_MINIMO_PUBLICAR} en algún año ({len(flojas)}):")
        for c in flojas:
            print(f"    - {c}")
    print(f"\n  -> {SALIDA}")


if __name__ == "__main__":
    main()

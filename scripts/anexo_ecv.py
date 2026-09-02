# -*- coding: utf-8 -*-
"""
Lector del anexo oficial de deficit habitacional de la ECV.

El DANE publica el deficit en un cuadro del anexo de cada anio
(`anex-ECV-<anio>.xlsx`). Ese cuadro es la unica fuente valida para validar
este proyecto: las cifras que circulan en prensa mezclan anios. El 19,6% que
suele citarse como "cabeceras" es el dato de 2023, no el de 2024 (17,29%).

El layout cambia entre anios -el numero de cuadro y el ancho de cada bloque de
columnas- asi que aqui NADA se fija por posicion: los bloques se localizan
leyendo los encabezados por nombre. Si el DANE reordena el cuadro, esto sigue
funcionando; si renombra un bloque, falla de forma visible en vez de devolver
un numero equivocado.
"""
from pathlib import Path

import pandas as pd

# Nombre del bloque en el encabezado -> clave interna
BLOQUES = {
    "Déficit cuantitativo": "cuantitativo",
    "Déficit cualitativo": "cualitativo",
    "Déficit habitacional": "total",
    "Hacinamiento mitigable jerarquizado": "hacinamiento_mitigable",
    "Material de pisos jerarquizado": "pisos",
    "Cocina jerarquizado": "cocina",
    "Agua para cocinar jerarquizado": "agua",
    "Alcantarillado jerarquizado": "alcantarillado",
    "Energía jerarquizado": "energia",
    "Recolección de basuras jerarquizado": "basuras",
}


def _hoja_deficit(x: pd.ExcelFile) -> str:
    """Encuentra el cuadro del deficit leyendo el indice del anexo."""
    idx = pd.read_excel(x, sheet_name=x.sheet_names[0], header=None, dtype=str).fillna("")
    for i in range(len(idx)):
        fila = " ".join(v for v in idx.iloc[i].tolist() if v and v != "nan")
        if "ficit habitacional" in fila and "Cuadro" in fila:
            return "Cuadro " + fila.split("Cuadro")[1].split()[0]
    raise RuntimeError("El anexo no trae un cuadro de déficit habitacional")


def leer(ruta: Path) -> pd.DataFrame:
    """Devuelve un DataFrame indexado por (departamento, area) con los % del anexo.

    `area` es 'Total', 'Cabecera' o 'Centros poblados y rural disperso'.
    """
    x = pd.ExcelFile(ruta)
    df = pd.read_excel(x, sheet_name=_hoja_deficit(x), header=None, dtype=str).fillna("")

    # Fila de nombres de bloque y fila de subencabezados (Total/L Inf./L Sup./CVE/%).
    fila_sub = next(i for i in range(len(df))
                    if (df.iloc[i] == "%").any() and (df.iloc[i] == "CVE").any())
    # Los nombres de bloque estan en las 1-2 filas de arriba.
    col_de = {}
    for arriba in (fila_sub - 1, fila_sub - 2):
        if arriba < 0:
            continue
        for j, v in enumerate(df.iloc[arriba]):
            nombre = str(v).strip()
            if nombre in BLOQUES and BLOQUES[nombre] not in col_de:
                # dentro del bloque, la columna "%" es la primera '%' a la derecha
                pct = next((k for k in range(j, min(j + 12, df.shape[1]))
                            if str(df.iloc[fila_sub, k]).strip() == "%"), None)
                if pct is not None:
                    col_de[BLOQUES[nombre]] = pct
    faltan = set(BLOQUES.values()) - set(col_de)
    if faltan:
        raise RuntimeError(f"No se localizaron los bloques {sorted(faltan)} en {ruta.name}")

    col_hogares = next(k for k in range(df.shape[1])
                       if str(df.iloc[fila_sub, k]).strip() == "Total")

    filas, dpto = [], None
    for i in range(fila_sub + 1, len(df)):
        etiqueta = str(df.iloc[i, 0]).strip()
        area = str(df.iloc[i, 1]).strip()
        if etiqueta:
            dpto = etiqueta
        if not dpto or not area:
            continue
        reg = {"departamento": dpto, "area": area,
               "hogares_miles": pd.to_numeric(df.iloc[i, col_hogares], errors="coerce")}
        for clave, col in col_de.items():
            reg[clave] = pd.to_numeric(df.iloc[i, col], errors="coerce")
        filas.append(reg)

    res = pd.DataFrame(filas).dropna(subset=["total"])
    return res.set_index(["departamento", "area"])

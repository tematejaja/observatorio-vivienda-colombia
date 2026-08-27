# -*- coding: utf-8 -*-
"""
FASE 2 - Composicion municipal de las 23 ciudades del observatorio.

La Fase 1 (GEIH) mide 7 de las 23 ciudades como area metropolitana completa,
porque ese es el dominio muestral `AREA` de la encuesta. La ECV, en cambio,
identifica municipios sueltos (`P1_DEPARTAMENTO` + `P1_MUNICIPIO`). Para que
"Medellin A.M." signifique lo mismo en las dos fases, aqui se declara que
municipios componen cada ciudad y la Fase 2 los suma.

FUENTE (textual, catalogo GEIH del DANE, microdatos.dane.gov.co/catalog/819):
  "...siete ciudades y areas metropolitanas definidas para la encuesta, asi:
   Medellin - Valle de Aburra, conformada por los municipios de Barbosa, Bello,
   Caldas, Copacabana, Envigado, Girardota, Itagui, La Estrella y Sabaneta;
   Cali - Yumbo; Barranquilla - Soledad; Bucaramanga - Floridablanca, Giron y
   Piedecuesta; Manizales - Villamaria; Pereira - Dosquebradas y La Virginia; y
   Cucuta - Villa del Rosario, Puerto Santander, Los Patios y El Zulia..."

Las ciudades se declaran por NOMBRE de municipio, no por codigo: los codigos
DIVIPOLA se resuelven contra el archivo oficial de proyecciones del DANE
(`GEIH/proyecciones_poblacion/PPED-AreaMun-2018-2042_VP.xlsx`, columnas MPIO y
DPMP) mediante `resolver_codigos()`. Asi ningun codigo queda escrito a mano y
un error de digitacion se vuelve imposible en vez de silencioso.

ADVERTENCIA que debe ir en la metodologia de la Fase 2: esta es la definicion
de area metropolitana **de la GEIH**, que no tiene por que coincidir con el area
metropolitana legalmente constituida de cada ciudad. Se usa esta y no la legal
justamente para preservar la comparabilidad con la Fase 1.
"""
import sys
import unicodedata
from pathlib import Path

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from config_ciudades import CIUDADES

BASE_DIR = SCRIPTS_DIR.parent
PROYECCIONES = BASE_DIR / "GEIH" / "proyecciones_poblacion" / "PPED-AreaMun-2018-2042_VP.xlsx"

# ciudad canonica -> municipios que la componen (nombres DIVIPOLA).
# Las 16 ciudades que no aparecen aqui son un solo municipio: el propio.
COMPOSICION_AM = {
    "Medellín A.M.": ["Medellín", "Barbosa", "Bello", "Caldas", "Copacabana",
                      "Envigado", "Girardota", "Itagüí", "La Estrella", "Sabaneta"],
    "Cali A.M.": ["Cali", "Yumbo"],
    "Barranquilla A.M.": ["Barranquilla", "Soledad"],
    "Bucaramanga A.M.": ["Bucaramanga", "Floridablanca", "Girón", "Piedecuesta"],
    "Manizales A.M.": ["Manizales", "Villamaría"],
    "Pereira A.M.": ["Pereira", "Dosquebradas", "La Virginia"],
    "Cúcuta A.M.": ["San José de Cúcuta", "Villa del Rosario", "Puerto Santander",
                    "Los Patios", "El Zulia"],
}

# Nombre del municipio nucleo cuando difiere del nombre canonico de la ciudad.
# El DANE usa el nombre largo en DIVIPOLA para tres capitales; sin esta tabla la
# resolucion falla (y falla ruidosamente, que es lo que se quiere). Es el mismo
# tipo de trampa que la Fase 1 ya encontro con Cali.
NUCLEO = {c["nombre"]: c["nombre"].replace(" A.M.", "") for c in CIUDADES}
NUCLEO["Bogotá D.C."] = "Bogotá, D.C."
NUCLEO["Cúcuta A.M."] = "San José de Cúcuta"
NUCLEO["Cartagena"] = "Cartagena de Indias"


def _norm(s: str) -> str:
    """Compara nombres de municipio sin tildes, mayusculas ni puntuacion: los
    archivos del DANE no son consistentes entre si (p. ej. 'Bogota, D.C.' vs
    'Bogota D.C.', y el caso ya conocido de Cali/'Santiago de Cali')."""
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return "".join(c for c in s if c.isalnum())


def catalogo_divipola() -> pd.DataFrame:
    """(mpio, nombre, dpto) de los ~1.100 municipios, desde el archivo oficial
    de proyecciones del DANE que ya usa la Fase 1."""
    x = pd.ExcelFile(PROYECCIONES)
    hoja = next(h for h in x.sheet_names if _norm(h).startswith("pobmunicipal"))
    df = pd.read_excel(x, sheet_name=hoja, header=7, dtype=str)
    df.columns = [str(c).strip().upper() for c in df.columns]
    col_mpio = next(c for c in df.columns if c.startswith("MPIO"))
    col_nom = next(c for c in df.columns if c.startswith("DPMP"))
    col_dpto = next(c for c in df.columns if c.startswith("DPNOM"))
    out = df[[col_mpio, col_nom, col_dpto]].dropna().drop_duplicates()
    out.columns = ["mpio", "nombre", "dpto"]
    out["mpio"] = out["mpio"].str.strip().str.zfill(5)
    out["_norm"] = out["nombre"].map(_norm)
    return out


def resolver_codigos() -> dict[str, list[str]]:
    """ciudad canonica -> lista de codigos DIVIPOLA de 5 digitos.

    Resuelve por nombre contra el catalogo oficial y RESTRINGE la busqueda al
    departamento de la ciudad, porque hay nombres repetidos entre departamentos
    (hay varios 'Barbosa', varios 'La Virginia'). Lanza excepcion si un
    municipio declarado no se puede resolver: mejor que fallar en silencio.
    """
    cat = catalogo_divipola()
    por_dpto = {c["nombre"]: c["dpto_divipola"].zfill(2) for c in CIUDADES}
    resultado: dict[str, list[str]] = {}
    for ciudad in [c["nombre"] for c in CIUDADES]:
        municipios = COMPOSICION_AM.get(ciudad, [NUCLEO[ciudad]])
        dd = por_dpto[ciudad]
        codigos = []
        for m in municipios:
            hit = cat[(cat["_norm"] == _norm(m)) & (cat["mpio"].str.startswith(dd))]
            if hit.empty:
                raise ValueError(
                    f"No se pudo resolver el municipio '{m}' de {ciudad} "
                    f"(departamento {dd}) en {PROYECCIONES.name}."
                )
            codigos.append(hit.iloc[0]["mpio"])
        resultado[ciudad] = codigos
    return resultado


if __name__ == "__main__":
    from config_ciudades import stdout_utf8
    stdout_utf8()
    cat = catalogo_divipola()
    print(f"Catálogo DIVIPOLA: {len(cat)} municipios\n")
    mapa = resolver_codigos()
    total = 0
    for ciudad, codigos in mapa.items():
        cuantos = len(codigos)
        total += cuantos
        marca = "  " if cuantos == 1 else "A.M."
        nombres = [cat[cat["mpio"] == c].iloc[0]["nombre"] for c in codigos]
        print(f"{marca} {ciudad:<20} {cuantos:>2} municipio(s): "
              f"{', '.join(f'{n} ({c})' for n, c in zip(nombres, codigos))}")
    print(f"\n{len(mapa)} ciudades · {total} municipios en total")

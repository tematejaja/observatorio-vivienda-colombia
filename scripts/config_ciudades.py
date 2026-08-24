# -*- coding: utf-8 -*-
"""
T003 / Fase Foundational: lista canonica de las 23 ciudades capitales y areas
metropolitanas del Observatorio Nacional de Vivienda.

ADVERTENCIA METODOLOGICA (Principio II de la constitucion del proyecto):
los codigos de dominio (`AREA`) de este modulo son una HIPOTESIS DE PARTIDA,
no una verdad asumida. Provienen del diccionario oficial DANE 2023 ya auditado
durante la fase piloto (ver GEIH/diccionario_armonizado.csv, fila AREA), pero:

  1. El diccionario 2023 NO garantiza que el mismo codigo siga vigente en
     2024/2025/2026 (el propio diccionario armonizado advierte que DANE no
     reescribe el texto descriptivo cada año).
  2. Solo `04_identificacion_ciudades.py` puede CONFIRMAR un codigo, cruzandolo
     empiricamente contra DPTO/CLASE en los microdatos reales de cada año.

Ninguna ciudad debe considerarse identificada hasta que ese script la marque
`VALIDO`. Las que no se puedan confirmar quedan `ND`, nunca forzadas.

Nota sobre `dpto_divipola`: el codigo de dominio GEIH coincide NUMERICAMENTE
con el codigo DIVIPOLA del departamento de cada capital, pero es
conceptualmente otra variable (dominio muestral, no division politica). Esa
coincidencia es justamente lo que permite el cruce de verificacion, y por eso
se declara explicitamente en vez de derivarse.

Nota sobre `dominio_pobreza`: la base de Pobreza Monetaria DANE NO usa `AREA`;
identifica la ciudad por un campo de TEXTO (`dominio`). Los valores aqui son
la hipotesis de nombre esperado; `04b_dominios_pobreza.py` los verifica contra
los valores reales presentes en cada archivo anual antes de usarlos.

Nota sobre San Andres: el diccionario GEIH tiene un 24o dominio (88 = San
Andres) que NO forma parte de las 23 ciudades capitales de este observatorio.
Se excluye deliberadamente; no es una omision.
"""
import sys


def stdout_utf8():
    """La consola de Windows usa cp1252 por defecto y revienta con UnicodeEncodeError
    al imprimir nombres con tilde (Bogota D.C., Medellin, Quibdo...). Se llama al
    inicio de cada script del pipeline nacional."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


# (nombre canonico, codigo AREA hipotesis, dpto DIVIPOLA esperado, nombre dpto,
#  dominio esperado en la base de Pobreza Monetaria)
CIUDADES = [
    {"nombre": "Bogotá D.C.",      "area": "11", "dpto_divipola": "11", "dpto_nombre": "Bogotá D.C.",         "dominio_pobreza": "BOGOTA"},
    {"nombre": "Medellín A.M.",    "area": "05", "dpto_divipola": "05", "dpto_nombre": "Antioquia",           "dominio_pobreza": "MEDELLIN"},
    {"nombre": "Cali A.M.",        "area": "76", "dpto_divipola": "76", "dpto_nombre": "Valle del Cauca",     "dominio_pobreza": "CALI"},
    {"nombre": "Barranquilla A.M.","area": "08", "dpto_divipola": "08", "dpto_nombre": "Atlántico",           "dominio_pobreza": "BARRANQUILLA"},
    {"nombre": "Bucaramanga A.M.", "area": "68", "dpto_divipola": "68", "dpto_nombre": "Santander",           "dominio_pobreza": "BUCARAMANGA"},
    {"nombre": "Manizales A.M.",   "area": "17", "dpto_divipola": "17", "dpto_nombre": "Caldas",              "dominio_pobreza": "MANIZALES"},
    {"nombre": "Pereira A.M.",     "area": "66", "dpto_divipola": "66", "dpto_nombre": "Risaralda",           "dominio_pobreza": "PEREIRA"},
    {"nombre": "Cúcuta A.M.",      "area": "54", "dpto_divipola": "54", "dpto_nombre": "Norte de Santander",  "dominio_pobreza": "CUCUTA"},
    {"nombre": "Ibagué",           "area": "73", "dpto_divipola": "73", "dpto_nombre": "Tolima",              "dominio_pobreza": "IBAGUE"},
    {"nombre": "Pasto",            "area": "52", "dpto_divipola": "52", "dpto_nombre": "Nariño",              "dominio_pobreza": "PASTO"},
    {"nombre": "Villavicencio",    "area": "50", "dpto_divipola": "50", "dpto_nombre": "Meta",                "dominio_pobreza": "VILLAVICENCIO"},
    {"nombre": "Montería",         "area": "23", "dpto_divipola": "23", "dpto_nombre": "Córdoba",             "dominio_pobreza": "MONTERIA"},
    {"nombre": "Cartagena",        "area": "13", "dpto_divipola": "13", "dpto_nombre": "Bolívar",             "dominio_pobreza": "CARTAGENA"},
    {"nombre": "Neiva",            "area": "41", "dpto_divipola": "41", "dpto_nombre": "Huila",               "dominio_pobreza": "NEIVA"},
    {"nombre": "Armenia",          "area": "63", "dpto_divipola": "63", "dpto_nombre": "Quindío",             "dominio_pobreza": "ARMENIA"},
    {"nombre": "Santa Marta",      "area": "47", "dpto_divipola": "47", "dpto_nombre": "Magdalena",           "dominio_pobreza": "SANTA MARTA"},
    {"nombre": "Sincelejo",        "area": "70", "dpto_divipola": "70", "dpto_nombre": "Sucre",               "dominio_pobreza": "SINCELEJO"},
    {"nombre": "Valledupar",       "area": "20", "dpto_divipola": "20", "dpto_nombre": "Cesar",               "dominio_pobreza": "VALLEDUPAR"},
    {"nombre": "Popayán",          "area": "19", "dpto_divipola": "19", "dpto_nombre": "Cauca",               "dominio_pobreza": "POPAYAN"},
    {"nombre": "Tunja",            "area": "15", "dpto_divipola": "15", "dpto_nombre": "Boyacá",              "dominio_pobreza": "TUNJA"},
    {"nombre": "Riohacha",         "area": "44", "dpto_divipola": "44", "dpto_nombre": "La Guajira",          "dominio_pobreza": "RIOHACHA"},
    {"nombre": "Florencia",        "area": "18", "dpto_divipola": "18", "dpto_nombre": "Caquetá",             "dominio_pobreza": "FLORENCIA"},
    {"nombre": "Quibdó",           "area": "27", "dpto_divipola": "27", "dpto_nombre": "Chocó",               "dominio_pobreza": "QUIBDO"},
]

# Dominio GEIH que existe en el diccionario pero NO pertenece a este observatorio.
DOMINIOS_FUERA_DE_ALCANCE = {"88": "San Andrés (no es una de las 23 capitales del observatorio)"}

AREA_A_NOMBRE = {c["area"]: c["nombre"] for c in CIUDADES}
NOMBRE_A_CIUDAD = {c["nombre"]: c for c in CIUDADES}
AREAS = [c["area"] for c in CIUDADES]
NOMBRES = [c["nombre"] for c in CIUDADES]

PERIODOS = ["2023", "2024", "2025", "2026"]
ANIO_PARCIAL = "2026"          # unico año con meses incompletos
ETIQUETA_PARCIAL = "2026*"     # rotulo obligatorio (Principio V)


def etiqueta_periodo(anio: str) -> str:
    """2026 SIEMPRE se rotula con asterisco; el resto va tal cual."""
    return ETIQUETA_PARCIAL if str(anio) == ANIO_PARCIAL else str(anio)


if __name__ == "__main__":
    stdout_utf8()
    assert len(CIUDADES) == 23, f"Se esperaban 23 ciudades, hay {len(CIUDADES)}"
    assert len(set(AREAS)) == 23, "Hay codigos AREA duplicados"
    assert "88" not in AREAS, "San Andres no debe estar en el alcance"
    print(f"{len(CIUDADES)} ciudades configuradas (codigos AREA como HIPOTESIS a verificar):")
    for c in CIUDADES:
        print(f"  AREA={c['area']}  {c['nombre']:<20} dpto={c['dpto_divipola']} ({c['dpto_nombre']})")
    print(f"\nExcluido deliberadamente: {DOMINIOS_FUERA_DE_ALCANCE}")

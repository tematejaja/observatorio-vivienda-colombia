# -*- coding: utf-8 -*-
"""
FASE 2 - Paso 2: deficit habitacional y entorno de la vivienda, por ciudad.

Solo tiene sentido correr esto DESPUES de que `41_deficit_nacional.py` demuestre
que los criterios reproducen las cifras del DANE en cabecera. Este script no
redefine ningun criterio: importa `calcular()` de ese modulo, de modo que hay una
sola definicion del deficit en todo el proyecto.

Que agrega respecto del paso 1:

  1. Desagrega a las 23 ciudades del observatorio. Las 7 areas metropolitanas se
     reconstruyen sumando municipios (config_areas_metropolitanas), igual que en
     la Fase 1, para que "Medellin A.M." signifique lo mismo en las dos fases.

  2. Estima la varianza con el DISENO MUESTRAL REAL. La ECV si publica sus
     variables de diseno en un modulo aparte (ESTRATO2020 = estrato, SEGMENTO =
     UPM), asi que aqui se usa linealizacion de Taylor para muestreo
     estratificado por conglomerados. Esto es estrictamente mejor que el
     bootstrap por DIRECTORIO de la Fase 1, que solo daba una cota inferior.

  3. Se valida contra el anexo oficial en el unico punto donde el DANE publica
     una cifra comparable a una ciudad: BOGOTA D.C. cabecera. Para las otras 22
     no existe cifra oficial de deficit por ciudad -esa es justamente la razon de
     ser de este observatorio-, asi que Bogota es el control.
"""
import importlib
import sys
from pathlib import Path

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from config_ciudades import stdout_utf8
from config_areas_metropolitanas import resolver_codigos
import config_deficit as cfg
import anexo_ecv

nac = importlib.import_module("41_deficit_nacional")

BASE_DIR = SCRIPTS_DIR.parent
ECV_DIR = BASE_DIR / "GEIH" / "ECV"
SALIDA = BASE_DIR / "GEIH" / "procesado_nacional" / "deficit_23ciudades.csv"

ANIOS = (2023, 2024, 2025)
COMPOSICION = resolver_codigos()

# Umbrales de confiabilidad, los mismos de la Fase 1.
CV_EXCELENTE, CV_ACEPTABLE, CV_PRECAUCION = 5.0, 15.0, 25.0
N_MINIMO = 30

ESTRATO_SIN = {0, 8, 9}          # 0=sin estrato, 8/9=no sabe/no informa


def etiquetar(n: int, cv) -> str:
    if n < N_MINIMO:
        return "NO PUBLICAR"
    if cv is None or pd.isna(cv):
        return "ND"
    if cv <= CV_EXCELENTE:
        return "EXCELENTE"
    if cv <= CV_ACEPTABLE:
        return "ACEPTABLE"
    if cv <= CV_PRECAUCION:
        return "PRECAUCION"
    return "NO PUBLICAR"


def construir(anio: int) -> pd.DataFrame:
    """Hogares con criterios de deficit YA aplicados + variables de diseno."""
    h = nac.calcular(nac.construir(anio))

    dis = nac._csv(f"ecv_{anio}_diseno.zip")
    dis = dis[["DIRECTORIO", "SECUENCIA_P", "MPIO", "SEGMENTO", "ESTRATO2020"]].copy()
    dis["SECUENCIA_P"] = pd.to_numeric(dis["SECUENCIA_P"], errors="coerce")
    # El modulo de diseno viene a nivel de PERSONA; se deja una fila por hogar.
    dis = dis.drop_duplicates(subset=["DIRECTORIO", "SECUENCIA_P"])

    n_antes = len(h)
    h = h.merge(dis, on=["DIRECTORIO", "SECUENCIA_P"], how="inner")
    if len(h) != n_antes:
        raise RuntimeError(f"{anio}: el cruce con diseno perdio "
                           f"{n_antes - len(h)} hogares de {n_antes}")

    # DIVIPOLA desde el modulo de vivienda, con control contra MPIO del diseno.
    h["_divipola"] = (h["P1_DEPARTAMENTO"].astype("Int64").astype(str).str.zfill(2)
                      + h["P1_MUNICIPIO"].astype("Int64").astype(str).str.zfill(3).str[-3:])
    discrepa = int((h["_divipola"] != h["MPIO"].astype(str).str.strip().str.zfill(5)).sum())
    if discrepa:
        raise RuntimeError(f"{anio}: {discrepa} hogares con municipio discrepante "
                           f"entre el modulo de vivienda y el de diseno")

    h["_estrato_num"] = h[cfg.VAR_ESTRATO]
    return h


def estimar(sub: pd.DataFrame, y: pd.Series):
    """Proporcion y error estandar bajo muestreo estratificado por conglomerados.

    Linealizacion de Taylor: z_i = w_i (y_i - p); se agrega z por UPM dentro de
    cada estrato y se suma la varianza entre UPM. Los estratos que quedan con una
    sola UPM en el dominio se colapsan en un pseudo-estrato, que es la practica
    estandar para que aporten varianza en vez de cero.
    """
    w = sub["FEX_C"]
    W = float(w.sum())
    if W <= 0 or len(sub) == 0:
        return None, None, None
    p = float((w * y).sum() / W)

    g = pd.DataFrame({"h": sub["ESTRATO2020"].astype(str),
                      "c": sub["SEGMENTO"].astype(str),
                      "z": w * (y.astype(float) - p)})
    g = g.groupby(["h", "c"], observed=True)["z"].sum().reset_index()
    upm_por_estrato = g.groupby("h")["c"].transform("size")
    g.loc[upm_por_estrato == 1, "h"] = "__colapsado__"

    var = 0.0
    for _, gh in g.groupby("h", observed=True):
        n = len(gh)
        if n < 2:
            continue
        var += n / (n - 1) * float(((gh["z"] - gh["z"].mean()) ** 2).sum())
    if var <= 0:
        return p, None, None
    se = (var ** 0.5) / W

    # Efecto de diseno: varianza del diseno real contra la de un muestreo
    # aleatorio simple con el n efectivo de Kish. Un deff de 3 significa que este
    # diseno por conglomerados equivale a una muestra aleatoria 3 veces menor.
    n_efectivo = W ** 2 / float((w ** 2).sum())
    var_mas = p * (1 - p) / n_efectivo
    deff = None if var_mas <= 0 else (se ** 2) / var_mas
    return p, se, deff


def indicadores(d: pd.DataFrame) -> dict:
    """Nombre del indicador -> serie booleana sobre los hogares del dominio."""
    ind = {
        "Deficit habitacional total": d["deficit"],
        "Deficit habitacional cuantitativo": d["cuantitativo"],
        "Deficit habitacional cualitativo": d["cualitativo"],
        "Componente: hacinamiento mitigable": d["q_hacin"],
        "Componente: alcantarillado o sanitario inadecuado": d["q_alcan"],
        "Componente: sin acueducto": d["q_agua"],
        "Componente: lugar inadecuado para cocinar": d["q_cocina"],
        "Componente: sin recoleccion de basuras": d["q_basura"],
        "Paredes en material inadecuado": d[cfg.VAR_PAREDES].isin(cfg.PAREDES_DEFICIENTE),
        "Pisos de tierra, arena o barro": d[cfg.VAR_PISOS].isin(cfg.PISOS_DEFICIENTE),
    }
    # El estrato se publica AGRUPADO, no de 1 a 6 por separado. No es por
    # comodidad: con ~700 hogares por ciudad, los estratos 4, 5 y 6 son eventos
    # tan poco frecuentes que su CV supera el 25% en casi todas las ciudades y
    # habria que marcarlos NO PUBLICAR. Agrupados, las cuatro categorias si se
    # estiman y ademas suman 100%.
    est = d["_estrato_num"]
    ind["Hogares en estrato 1 o 2"] = est.isin({1, 2})
    ind["Hogares en estrato 3"] = est == 3
    ind["Hogares en estrato 4, 5 o 6"] = est.isin({4, 5, 6})
    ind["Hogares sin estrato o no informa"] = est.isin(ESTRATO_SIN) | est.isna()
    return ind


def main() -> None:
    stdout_utf8()
    print("FASE 2 · Paso 2 — déficit habitacional por ciudad (ECV, cabecera)")
    print("=" * 78)

    filas, control = [], []
    for anio in ANIOS:
        d = construir(anio)
        # Universo: cabecera y no excluidos (vivienda tradicional indigena).
        d = d[(d["CLASE"] == 1) & (~d["_excluido"])]
        print(f"  {anio}: {len(d):,} hogares en cabecera con diseño muestral cruzado")

        for ciudad, codigos in COMPOSICION.items():
            sub = d[d["_divipola"].isin(codigos)]
            n = len(sub)
            for nombre, y in indicadores(sub).items():
                p, se, deff = ((None, None, None) if n == 0
                               else estimar(sub, y.astype(float)))
                if p is None:
                    filas.append({"ciudad": ciudad, "anio": anio, "indicador": nombre,
                                  "valor_pct": None, "error_estandar": None,
                                  "ic95_inf": None, "ic95_sup": None,
                                  "deff": None, "n_muestral": n, "cv_pct": None,
                                  "etiqueta_confiabilidad": "NO PUBLICAR",
                                  "nota": "sin muestra en la ciudad"})
                    continue
                pct = 100 * p
                se_pct = None if se is None else 100 * se
                cv = None if (se_pct is None or pct <= 0) else 100 * se_pct / pct

                if pct == 0:
                    # CERO MUESTRAL. Sin casos en la muestra el error estandar
                    # da cero y la cifra se veria como la mas solida de la
                    # tabla, cuando es lo contrario: significa "no aparecio en
                    # ~700 hogares", no "no existe en la ciudad". Se acota por
                    # la regla de tres (techo del IC95 ~ 3/n) sobre el n
                    # efectivo de Kish, y se marca para que nadie la lea como
                    # un cero verdadero.
                    w = sub["FEX_C"]
                    n_ef = float(w.sum()) ** 2 / float((w ** 2).sum())
                    techo = round(min(100.0, 100 * 3 / n_ef), 4)
                    filas.append({
                        "ciudad": ciudad, "anio": anio, "indicador": nombre,
                        "valor_pct": 0.0, "error_estandar": None,
                        "ic95_inf": 0.0, "ic95_sup": techo, "deff": None,
                        "n_muestral": n, "cv_pct": None,
                        "etiqueta_confiabilidad": "PRECAUCION",
                        "nota": f"sin casos en la muestra; el IC95 llega hasta {techo:.2f}%",
                    })
                    continue

                filas.append({
                    "ciudad": ciudad, "anio": anio, "indicador": nombre,
                    "valor_pct": round(pct, 4),
                    "error_estandar": None if se_pct is None else round(se_pct, 4),
                    "ic95_inf": None if se_pct is None else round(max(0.0, pct - 1.96 * se_pct), 4),
                    "ic95_sup": None if se_pct is None else round(min(100.0, pct + 1.96 * se_pct), 4),
                    "deff": None if deff is None else round(deff, 3),
                    "n_muestral": n,
                    "cv_pct": None if cv is None else round(cv, 2),
                    "etiqueta_confiabilidad": etiquetar(n, cv),
                    "nota": "",
                })

        # --- control contra el anexo oficial: Bogota D.C. cabecera ---
        of = anexo_ecv.leer(ECV_DIR / f"anex-ECV-{anio}.xlsx")
        b = of.loc[("Bogotá D.C.", "Cabecera")]
        sub = d[d["_divipola"].isin(COMPOSICION["Bogotá D.C."])]
        for clave, col in [("total", "deficit"), ("cuantitativo", "cuantitativo"),
                           ("cualitativo", "cualitativo")]:
            p, se, _ = estimar(sub, sub[col].astype(float))
            control.append({"anio": anio, "indicador": clave, "calculado": 100 * p,
                            "dane": float(b[clave]),
                            "ee": None if se is None else 100 * se})

    res = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(SALIDA, index=False, encoding="utf-8-sig")

    print("")
    print("=" * 78)
    print("CONTROL — Bogotá D.C. cabecera contra el anexo oficial del DANE")
    print("=" * 78)
    print(f"  {'año':<6}{'indicador':<16}{'calculado':>11}{'DANE':>9}{'dif':>8}")
    for c in control:
        dif = c["calculado"] - c["dane"]
        marca = "OK" if abs(dif) <= 0.5 else ("~" if abs(dif) <= 1.0 else "XX")
        print(f"  {c['anio']:<6}{c['indicador']:<16}{c['calculado']:>10.2f}%"
              f"{c['dane']:>8.2f}%{dif:>+8.2f}  {marca}")

    print("")
    print("=" * 78)
    print("DÉFICIT HABITACIONAL TOTAL POR CIUDAD (%)")
    print("=" * 78)
    t = res[res["indicador"] == "Deficit habitacional total"].pivot_table(
        index="ciudad", columns="anio", values="valor_pct")
    print(t.round(1).sort_values(ANIOS[-1]).to_string())

    print("")
    print("=" * 78)
    print("CONFIABILIDAD")
    print("=" * 78)
    print(res["etiqueta_confiabilidad"].value_counts().to_string())
    print(f"\n  n muestral por ciudad-año: mínimo {res['n_muestral'].min():,}, "
          f"mediana {int(res['n_muestral'].median()):,}")
    print(f"  -> {SALIDA}")


if __name__ == "__main__":
    main()

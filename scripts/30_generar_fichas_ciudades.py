# -*- coding: utf-8 -*-
"""
FASE 2 (parte narrativa) - Genera las 23 fichas individuales de ciudad en
Markdown, una por ciudad, en fichas_ciudades/.

POR QUE SE GENERAN POR SCRIPT Y NO A MANO (Principio VIII):
23 fichas escritas manualmente son 23 oportunidades de que una cifra se desvie
de la tabla auditada. Generarlas desde `output/observatorio_vivienda_capitales_
2023_2026.csv` garantiza que cada numero de cada ficha sea exactamente el que
paso el red team, y permite regenerarlas si la Fase 1 se recalcula.

REGLAS DE PUBLICACION APLICADAS EN CADA FICHA:
  * 2026 SIEMPRE rotulado "2026*" con nota de periodo parcial (Principio V).
  * Toda cifra con etiqueta NO PUBLICAR se muestra tachada y con advertencia
    explicita, nunca como si fuera un dato robusto (Principio VI).
  * Las cifras en PRECAUCION se marcan con simbolo de advertencia.
  * El deficit habitacional (seccion 7) viene de la ECV, no de la GEIH, y se
    rotula como tal para que nadie encadene las dos fuentes en una serie.
  * Las variaciones interanuales de 2026 usan SOLO la comparacion pareada
    homogenea Ene-Jun vs Ene-Jun (Principio V).
  * Cada ficha cierra con las limitaciones metodologicas que le aplican.

Salida: fichas_ciudades/ficha_<slug>.md  (23 archivos) + README.md indice
"""
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from config_ciudades import CIUDADES, stdout_utf8
import datos_observatorio as datos

BASE_DIR = SCRIPTS_DIR.parent
OUT_DIR = BASE_DIR / "fichas_ciudades"

ANIOS = datos.ANIOS
NO_PUBLICABLE = {"NO PUBLICAR"}
PRECAUCION = {"PRECAUCION"}


def slug(nombre: str) -> str:
    s = unicodedata.normalize("NFD", nombre)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return re.sub(r"_a_m$", "_am", s)


class Datos:
    """Formato Markdown (tachado/emojis) sobre el modulo compartido
    `datos_observatorio` (ADR-0003) - este script es UN consumidor de ese
    modulo, ya no el dueno de la lectura de los CSV."""

    def __init__(self):
        self.t = datos.cargar_tabla_maestra()
        self.rank = datos.cargar_rankings()
        self.pob = datos.cargar_validacion_poblacional()
        self.temp = datos.cargar_validacion_temporal()
        self.ctrl = datos.cargar_control_geografico()
        self.aud = datos.cargar_auditoria()

    def celda(self, ciudad, anio, indicador, fmt="num", decimales=1):
        """Devuelve el valor formateado, ya anotado segun su confiabilidad."""
        ind = datos.indicador(self.t, ciudad, anio, indicador)
        if ind is None or not isinstance(ind["valor"], (int, float)):
            return "ND"
        v = ind["valor"]
        et = str(ind["etiqueta_confiabilidad"])
        if fmt == "cop":
            txt = f"${v:,.0f}"
        elif fmt == "pct":
            txt = f"{v:.{decimales}f}%"
        else:
            txt = f"{v:.{decimales}f}"
        if et in NO_PUBLICABLE:
            return f"~~{txt}~~ 🔴"
        if et in PRECAUCION:
            return f"{txt} 🟡"
        return txt

    def serie(self, ciudad, indicador, fmt="num", decimales=1):
        return [self.celda(ciudad, a, indicador, fmt, decimales) for a in ANIOS]

    def posicion(self, ciudad, nombre_ranking, anio="2025"):
        r = datos.ranking(self.rank, nombre_ranking, anio)
        fila = r[r["ciudad"] == ciudad]
        if fila.empty:
            return None, None
        pos = fila.iloc[0]["posicion"]
        if str(pos) == "ND":
            return None, None
        return int(pos), fila.iloc[0]["valor"]


def tabla_md(encabezados, filas):
    out = ["| " + " | ".join(encabezados) + " |",
           "|" + "|".join(["---"] * len(encabezados)) + "|"]
    for f in filas:
        out.append("| " + " | ".join(str(x) for x in f) + " |")
    return "\n".join(out)


def generar_ficha(d: Datos, ciudad: dict) -> str:
    n = ciudad["nombre"]
    L = []

    # --- encabezado ---
    L.append(f"# Ficha de vivienda — {n}")
    L.append("")
    L.append(f"**Dominio GEIH (`AREA`):** {ciudad['area']} · "
             f"**Departamento:** {ciudad['dpto_nombre']} · "
             f"**Periodo:** 2023 – 2026\\*")
    L.append("")
    ctrl_c = d.ctrl[d.ctrl["ciudad_nombre"] == n]
    n_total = int(ctrl_c["registros"].sum())
    hogares_mes = ctrl_c[ctrl_c["anio"] == 2025]["suma_fex_c18"].mean()
    L.append(f"**Muestra:** {n_total:,} hogares encuestados en 42 meses · "
             f"**Hogares expandidos (promedio mensual 2025):** {hogares_mes:,.0f}")
    L.append("")
    L.append("> **2026\\*** = enero–junio de 2026, único periodo publicado por el DANE. "
             "Toda variación de 2026 en esta ficha usa comparación pareada contra los "
             "**mismos meses** de 2025, nunca contra el año completo.")
    L.append("")
    L.append("---")
    L.append("")

    # --- 1. retrato rapido ---
    L.append("## 1. Retrato rápido (2025)")
    L.append("")
    pares = [
        ("Hogares en arriendo", d.celda(n, "2025", "Tenencia: En arriendo o subarriendo", "pct")),
        ("Canon mediano de arriendo", d.celda(n, "2025", "Canon de arriendo mensual - mediana", "cop")),
        ("Arriendo / ingreso del hogar", d.celda(n, "2025", "Arriendo/ingreso del hogar (mediana)", "pct")),
        ("Arrendatarios con sobrecarga (>30 %)",
         d.celda(n, "2025", "Arrendatarios que destinan >30% del ingreso al arriendo", "pct")),
        ("Vivienda propia totalmente pagada",
         d.celda(n, "2025", "Tenencia: Propia, totalmente pagada", "pct")),
        ("Hogares con hacinamiento",
         d.celda(n, "2025", "Hogares con hacinamiento (>3 personas/cuarto para dormir)", "pct", 2)),
    ]
    L.append(tabla_md(["Indicador", "Valor"], pares))
    L.append("")

    # posiciones en rankings
    L.append("**Posición nacional (entre 23 ciudades, 2025):**")
    L.append("")
    for etiqueta, nombre_ranking in [("% en arriendo", datos.RANKINGS[0]),
                                     ("Canon de arriendo", datos.RANKINGS[1]),
                                     ("Sobrecarga >30 %", datos.RANKINGS[2]),
                                     ("Hacinamiento", datos.RANKINGS[4])]:
        pos, val = d.posicion(n, nombre_ranking)
        if pos:
            L.append(f"- **{etiqueta}:** puesto {pos} de 23")
    L.append("")
    L.append("---")
    L.append("")

    # --- 2. tenencia ---
    L.append("## 2. ¿Cómo viven los hogares? (tenencia)")
    L.append("")
    cats = ["Propia, totalmente pagada", "Propia, la estan pagando", "En arriendo o subarriendo",
            "En usufructo", "Posesion sin titulo", "Propiedad colectiva", "Otra"]
    etiquetas = ["Propia, totalmente pagada", "Propia, la están pagando", "En arriendo o subarriendo",
                 "En usufructo", "Posesión sin título", "Propiedad colectiva", "Otra"]
    filas = []
    for cat, et in zip(cats, etiquetas):
        filas.append([et] + d.serie(n, f"Tenencia: {cat}", "pct", 2))
    L.append(tabla_md(["Tenencia (%)"] + ANIOS, filas))
    L.append("")

    # --- 3. arriendo ---
    L.append("---")
    L.append("")
    L.append("## 3. Mercado de arriendo")
    L.append("")
    filas = []
    for est, et in [("mediana", "Mediana"), ("promedio", "Promedio"),
                    ("P25", "Percentil 25"), ("P75", "Percentil 75")]:
        filas.append([et] + d.serie(n, f"Canon de arriendo mensual - {est}", "cop"))
    L.append(tabla_md(["Canon mensual (COP)"] + ANIOS, filas))
    L.append("")
    L.append("*Corresponde a `P5140`, el arriendo **efectivamente pagado** por hogares "
             "arrendatarios. No debe confundirse con el arriendo imputado (sección 5), "
             "que es una estimación del propio hogar y no un pago real.*")
    L.append("")

    # variacion homogenea 2026
    tt = d.temp[(d.temp["ciudad_nombre"] == n) &
                (d.temp["indicador"] == "Canon mediano de arriendo")]
    if not tt.empty:
        r = tt.iloc[0]
        hom, ing, sesgo = r["variacion_homogenea"], r["variacion_ingenua"], r["sesgo_estacional"]
        L.append(f"**Variación 2025 → 2026\\* (comparación pareada enero–junio):** "
                 f"**{hom:+.1f}%**")
        L.append("")
        # El caso interesante no es que las dos cifras difieran, sino cuanto cambia la
        # LECTURA. Si la ingenua es plana o de signo contrario, decirlo explicitamente:
        # es justo el error que la comparacion pareada evita.
        if abs(sesgo) >= 1.0 and (abs(ing) < 1.0 or (ing * hom) < 0):
            lectura = ("sugeriría que el arriendo **no subió**" if abs(ing) < 1.0
                       else "sugeriría un movimiento en **sentido contrario**")
            L.append(f"> ⚠️ Comparar 2026\\* contra el año 2025 **completo** daría "
                     f"{ing:+.1f}%, lo que {lectura}. Esa diferencia de "
                     f"{abs(sesgo):.1f} pp es efecto estacional, no cambio real de precios. "
                     f"Cite siempre la cifra pareada.")
        else:
            L.append(f"> Comparar contra el año 2025 completo daría {ing:+.1f}%, un sesgo "
                     f"estacional de {sesgo:+.1f} pp. Cite siempre la cifra pareada.")
        L.append("")

    # --- 4. esfuerzo financiero ---
    L.append("---")
    L.append("")
    L.append("## 4. ¿Cuánto pesa el arriendo en el bolsillo?")
    L.append("")
    filas = [
        ["Arriendo / ingreso (mediana)"] + d.serie(n, "Arriendo/ingreso del hogar (mediana)", "pct"),
        ["Sobrecarga: >30 % del ingreso"] + d.serie(n, "Arrendatarios que destinan >30% del ingreso al arriendo", "pct"),
        ["Sobrecarga severa: >50 % del ingreso"] + d.serie(n, "Arrendatarios que destinan >50% del ingreso al arriendo", "pct"),
    ]
    L.append(tabla_md(["Esfuerzo financiero"] + ANIOS, filas))
    L.append("")
    L.append("*El umbral del 30 % es la convención internacional de sobrecarga por vivienda. "
             "2026\\* aparece como ND porque el DANE no publica la medición de Pobreza "
             "Monetaria del año en curso, de la que proviene el ingreso del hogar.*")
    L.append("")

    # ingresos y pobreza
    L.append("### Ingresos y pobreza según la tenencia")
    L.append("")
    filas = [
        ["Ingreso mediano — propietarios"] + d.serie(n, "Ingreso mediano hogares propietarios", "cop"),
        ["Ingreso mediano — arrendatarios"] + d.serie(n, "Ingreso mediano hogares arrendatarios", "cop"),
        ["Brecha propietarios vs arrendatarios"] + d.serie(n, "Brecha de ingreso propietarios vs arrendatarios", "pct"),
        ["% arrendatarios en pobreza monetaria"] + d.serie(n, "% arrendatarios en pobreza monetaria", "pct"),
        ["% propietarios en pobreza monetaria"] + d.serie(n, "% propietarios en pobreza monetaria", "pct"),
        ["% de hogares pobres que viven en arriendo"] + d.serie(n, "% hogares pobres que viven en arriendo", "pct"),
    ]
    L.append(tabla_md(["Ingreso y pobreza"] + ANIOS, filas))
    L.append("")

    # --- 5. vivienda propia ---
    L.append("---")
    L.append("")
    L.append("## 5. Vivienda propia, crédito y arriendo imputado")
    L.append("")
    filas = [
        ["Valor comercial estimado (mediana)"] + d.serie(n, "Valor estimado de venta de la vivienda - mediana", "cop"),
        ["Cuota hipotecaria mensual (mediana)"] + d.serie(n, "Cuota hipotecaria mensual - mediana", "cop"),
        ["Arriendo imputado (mediana)"] + d.serie(n, "Arriendo imputado (estimado) - mediana", "cop"),
    ]
    L.append(tabla_md(["Vivienda propia"] + ANIOS, filas))
    L.append("")
    L.append("*El **arriendo imputado** (`P5130`) es lo que un propietario estima que pagaría "
             "si arrendara su vivienda. Es una valoración hipotética, no un desembolso: no debe "
             "sumarse ni compararse directamente con el canon pagado de la sección 3.*")
    L.append("")

    # --- 6. hacinamiento y servicios ---
    L.append("---")
    L.append("")
    L.append("## 6. Espacio habitacional y servicios públicos")
    L.append("")
    filas = [
        ["Personas por cuarto para dormir (promedio)"] + d.serie(n, "Personas por cuarto para dormir - promedio", "num", 2),
        ["Hogares con hacinamiento (>3 pers./cuarto)"] + d.serie(n, "Hogares con hacinamiento (>3 personas/cuarto para dormir)", "pct", 2),
        ["Hacinamiento crítico NBI (cuartos totales)"] + d.serie(n, "Hogares con hacinamiento critico NBI (>3 personas/cuarto TOTAL)", "pct", 2),
    ]
    L.append(tabla_md(["Hacinamiento"] + ANIOS, filas))
    L.append("")
    filas = []
    for srv, et in [("sin acueducto", "Sin acueducto"), ("sin alcantarillado", "Sin alcantarillado"),
                    ("sin gas natural conectado a red", "Sin gas natural a red"),
                    ("sin energia electrica", "Sin energía eléctrica"),
                    ("sin recoleccion de basuras", "Sin recolección de basuras")]:
        filas.append([et] + d.serie(n, f"Hogares {srv}", "pct", 2))
    L.append(tabla_md(["Hogares sin el servicio (%)"] + ANIOS, filas))
    L.append("")

    # --- 7. deficit habitacional ---
    L.append("---")
    L.append("")
    L.append("## 7. Déficit habitacional, materiales y estrato")
    L.append("")
    L.append("Fuente distinta al resto de la ficha: **Encuesta Nacional de Calidad de Vida "
             "(ECV)**, no GEIH. Se aplica la metodología oficial de déficit habitacional del "
             "DANE (2020) con sus criterios de **cabecera municipal**. La réplica reproduce el "
             "dato publicado por el DANE: en cabecera nacional 2024 da 17,18 % contra 17,29 % "
             "oficial, y los siete componentes coinciden dentro de 0,07 puntos.")
    L.append("")
    filas = [
        ["Déficit habitacional total"] + d.serie(n, "Deficit habitacional total", "pct", 2),
        ["— cuantitativo (estructural)"] + d.serie(n, "Deficit habitacional cuantitativo", "pct", 2),
        ["— cualitativo (subsanable)"] + d.serie(n, "Deficit habitacional cualitativo", "pct", 2),
    ]
    L.append(tabla_md(["Hogares en déficit (%)"] + ANIOS, filas))
    L.append("")
    L.append("*Las dos categorías son **excluyentes**: un hogar en déficit cuantitativo no se "
             "cuenta además en cualitativo, así que total = cuantitativo + cualitativo.*")
    L.append("")
    filas = [
        ["Hacinamiento mitigable"] + d.serie(n, "Componente: hacinamiento mitigable", "pct", 2),
        ["Lugar inadecuado para cocinar"] + d.serie(n, "Componente: lugar inadecuado para cocinar", "pct", 2),
        ["Alcantarillado o sanitario inadecuado"] + d.serie(n, "Componente: alcantarillado o sanitario inadecuado", "pct", 2),
        ["Sin acueducto"] + d.serie(n, "Componente: sin acueducto", "pct", 2),
        ["Sin recolección de basuras"] + d.serie(n, "Componente: sin recoleccion de basuras", "pct", 2),
    ]
    L.append(tabla_md(["Componentes del déficit cualitativo (%)"] + ANIOS, filas))
    L.append("")
    filas = [
        ["Paredes en material inadecuado"] + d.serie(n, "Paredes en material inadecuado", "pct", 2),
        ["Pisos de tierra, arena o barro"] + d.serie(n, "Pisos de tierra, arena o barro", "pct", 2),
    ]
    L.append(tabla_md(["Materiales de la vivienda (%)"] + ANIOS, filas))
    L.append("")
    filas = [
        ["Estrato 1 o 2"] + d.serie(n, "Hogares en estrato 1 o 2", "pct", 2),
        ["Estrato 3"] + d.serie(n, "Hogares en estrato 3", "pct", 2),
        ["Estrato 4, 5 o 6"] + d.serie(n, "Hogares en estrato 4, 5 o 6", "pct", 2),
        ["Sin estrato o no informa"] + d.serie(n, "Hogares sin estrato o no informa", "pct", 2),
    ]
    L.append(tabla_md(["Estrato socioeconómico (% de hogares)"] + ANIOS, filas))
    L.append("")
    L.append("*El estrato se publica agrupado porque con unos 700 hogares de muestra por ciudad "
             "los estratos 4, 5 y 6 por separado no alcanzan precisión utilizable. El estrato es "
             "el que reporta el hogar en su factura de energía (`P8520S1A1`).*")
    L.append("")
    L.append("**Qué se puede leer por ciudad y qué no.** Con la muestra que la ECV asigna a cada "
             "ciudad, el déficit **total**, el **cualitativo**, el hacinamiento y el estrato 1 o 2 "
             "se estiman con precisión utilizable. El déficit **cuantitativo** y los componentes "
             "poco frecuentes (acueducto, basuras, materiales) quedan casi siempre marcados "
             "`NO PUBLICAR`: no es que valgan cero, es que la muestra no permite afirmarlos para "
             "una ciudad. A escala nacional sí se estiman bien.")
    L.append("")
    L.append("*`2026*` aparece en `ND` porque el DANE aún no publica la ECV 2026; no se "
             "extrapola.*")
    L.append("")

    # --- 8. calidad del dato ---
    L.append("---")
    L.append("")
    L.append("## 8. Calidad del dato para esta ciudad")
    L.append("")
    L.append(f"- **Validación geográfica:** {len(ctrl_c)} celdas ciudad-mes, "
             f"{int((ctrl_c['estado_geografico']=='VALIDO').sum())} en estado `VÁLIDO`. "
             f"Coincidencia con el departamento esperado: "
             f"{ctrl_c['pct_dpto_esperado'].astype(float).mean():.1f} %; "
             f"cabecera municipal (`CLASE=1`): {ctrl_c['pct_clase1'].astype(float).mean():.1f} %.")

    pv = d.pob[d.pob["ciudad_nombre"] == n]
    if not pv.empty:
        estados = pv["estado_poblacional"].value_counts().to_dict()
        detalle = ", ".join(f"{k}: {v}" for k, v in estados.items())
        L.append(f"- **Validación poblacional (CNPV 2018):** {detalle} (de 4 años). "
                 f"Desvío frente a la proyección oficial: "
                 f"{pd.to_numeric(pv['dif_pct_am'], errors='coerce').min():+.1f} % a "
                 f"{pd.to_numeric(pv['dif_pct_am'], errors='coerce').max():+.1f} %.")
        if (pv["estado_poblacional"] == "REVISAR").any():
            L.append("  - ⚠️ Esta ciudad presenta desvíos superiores al ±5 % en al menos un año. "
                     "El cruce geográfico dio 100 %, por lo que el desvío se atribuye a la "
                     "calibración de `FEX_C18` frente a la versión actualizada de las "
                     "proyecciones, no a un error de identificación. **Los porcentajes y "
                     "medianas de esta ficha no se ven afectados; la cautela aplica a los "
                     "niveles absolutos de población expandida.**")

    # Cifras no publicables. El bloque de deficit se cuenta aparte: por el tamano
    # de la muestra de la ECV tiene decenas de celdas marcadas, y enumerarlas
    # una a una aqui ahogaria las advertencias del resto de la ficha.
    de_ciudad = d.t[d.t["ciudad"] == n]
    es_deficit = de_ciudad["bloque_indicador"] == "deficit_habitacional"
    def_nopub = int((es_deficit & (de_ciudad["etiqueta_confiabilidad"] == "NO PUBLICAR")).sum())
    def_prec = int((es_deficit & (de_ciudad["etiqueta_confiabilidad"] == "PRECAUCION")).sum())
    if def_nopub or def_prec:
        L.append(f"- 📋 **Sección 7 (déficit, ECV):** {def_nopub} estimación(es) marcadas "
                 f"NO PUBLICAR y {def_prec} en PRECAUCIÓN, por el tamaño de la muestra que la "
                 f"ECV asigna a esta ciudad. Están señaladas en las tablas de esa sección; no "
                 f"se enumeran aquí una por una.")

    nopub = de_ciudad[~es_deficit & (de_ciudad["etiqueta_confiabilidad"] == "NO PUBLICAR")]
    if not nopub.empty:
        L.append(f"- 🔴 **{len(nopub)} estimación(es) marcadas NO PUBLICAR** "
                 f"(n < 30 o CV > 25 %). Aparecen ~~tachadas~~ en las tablas de arriba y "
                 f"**no deben citarse**:")
        for _, r in nopub.head(8).iterrows():
            L.append(f"  - {r['anio']} · {r['nombre_indicador']} "
                     f"(CV = {float(r['cv_pct']):.1f} %)" if pd.notna(r["cv_pct"]) and r["cv_pct"] != ""
                     else f"  - {r['anio']} · {r['nombre_indicador']}")
        if len(nopub) > 8:
            L.append(f"  - …y {len(nopub)-8} más (ver hoja `Precision_CV` del Excel).")
    else:
        L.append("- ✅ Ninguna estimación GEIH de esta ciudad quedó marcada como NO PUBLICAR.")

    prec = de_ciudad[~es_deficit & (de_ciudad["etiqueta_confiabilidad"] == "PRECAUCION")]
    if not prec.empty:
        L.append(f"- 🟡 {len(prec)} estimación(es) en **PRECAUCIÓN** (CV entre 15 % y 25 %, "
                 f"o n < 100): úselas con la advertencia correspondiente.")
    L.append("")

    # --- 9. limitaciones ---
    L.append("---")
    L.append("")
    L.append("## 9. Antes de citar estas cifras")
    L.append("")
    L.append("1. **El margen de error de las cifras GEIH es mayor al reportado.** Los "
             "microdatos públicos de la GEIH no incluyen variables de diseño muestral "
             "(UPM/estrato), así que su varianza se estimó por bootstrap agrupando en "
             "`DIRECTORIO` (la vivienda), que captura solo parte del efecto de "
             "conglomeración: ese error estándar es una **cota inferior**. No aplica a la "
             "sección 7: la ECV sí publica sus variables de diseño, y allí la varianza se "
             "estima con el diseño real (estrato y UPM).")
    L.append("2. **2026 es parcial** (enero–junio). Nunca compare esa cifra contra un año "
             "completo sin usar la comparación pareada que aparece en la sección 3.")
    L.append("3. **No hay datos de ingreso, carga financiera ni pobreza para 2026\\*** — el DANE "
             "no publica esa medición del año en curso. Los `ND` son estructurales, no un fallo "
             "del cálculo.")
    L.append("4. **El déficit habitacional viene de otra encuesta** (sección 7): es ECV, no "
             "GEIH, y son años completos distintos a la serie GEIH. No mezcle ambas fuentes "
             "en una misma serie.")
    if ciudad["nombre"].endswith("A.M."):
        L.append("5. **Esta ficha corresponde al área metropolitana completa**, no solo al "
                 "municipio núcleo. Compararla con cifras municipales de otra fuente sería "
                 "incorrecto.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("**Fuentes:** DANE — GEIH 2023–2026 (catálogos ANDA 782, 819, 853, 900); "
             "Pobreza Monetaria y Desigualdad 2023–2025 (835, 874, 908); Proyecciones de "
             "población CNPV 2018. Metodología completa: "
             "[`metodologia_observatorio_nacional.md`](../output/metodologia_observatorio_nacional.md). "
             "Auditoría: [`auditoria_estadistica_observatorio_nacional.xlsx`]"
             "(../output/auditoria_estadistica_observatorio_nacional.xlsx).")
    L.append("")
    L.append("*Ficha generada automáticamente desde la tabla maestra auditada "
             "(`scripts/30_generar_fichas_ciudades.py`). No editar a mano: regenerar.*")
    L.append("")
    return "\n".join(L)


def main():
    stdout_utf8()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = Datos()

    indice = ["# Fichas de vivienda por ciudad", "",
              "23 ciudades capitales y áreas metropolitanas de Colombia · 2023 – 2026\\*",
              "",
              "Generadas desde la tabla maestra auditada de la Fase 1 "
              "(465 controles aprobados, 0 rechazos).",
              "",
              "| # | Ciudad | `AREA` | Ficha | % arriendo 2025 | Canon mediano 2025 |",
              "|---|---|---|---|---|---|"]

    for i, ciudad in enumerate(CIUDADES, start=1):
        n = ciudad["nombre"]
        contenido = generar_ficha(d, ciudad)
        archivo = OUT_DIR / f"ficha_{slug(n)}.md"
        archivo.write_text(contenido, encoding="utf-8")
        arr = d.celda(n, "2025", "Tenencia: En arriendo o subarriendo", "pct")
        can = d.celda(n, "2025", "Canon de arriendo mensual - mediana", "cop")
        indice.append(f"| {i} | {n} | {ciudad['area']} | [`{archivo.name}`]({archivo.name}) "
                      f"| {arr} | {can} |")
        print(f"  {archivo.name:<34} {len(contenido):>6,} caracteres")

    indice += ["", "---", "",
               "**Advertencias comunes a todas las fichas:**", "",
               "- `2026*` es enero–junio; las variaciones usan comparación pareada.",
               "- El déficit habitacional (sección 7) proviene de la ECV, no de la GEIH; "
               "`2026*` queda en `ND` porque el DANE aún no la publica.",
               "- No hay ingreso ni pobreza para 2026 (el DANE no lo publica).",
               "- El error estándar reportado es una cota inferior del real.",
               "- Las cifras ~~tachadas~~ 🔴 no son publicables (n < 30 o CV > 25 %).",
               "", "Ver [`metodologia_observatorio_nacional.md`]"
               "(../output/metodologia_observatorio_nacional.md) para el detalle metodológico.",
               ""]
    (OUT_DIR / "README.md").write_text("\n".join(indice), encoding="utf-8")

    print(f"\n{len(CIUDADES)} fichas + índice -> {OUT_DIR}")


if __name__ == "__main__":
    main()

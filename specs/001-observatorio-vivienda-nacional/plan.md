# Implementation Plan: Motor Nacional del Observatorio de Vivienda — Fase 1 (23 Ciudades, GEIH + Pobreza)

**Branch**: `001-observatorio-vivienda-nacional` (sin git; identificador lógico de la feature) | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-observatorio-vivienda-nacional/spec.md`

## Summary

Generalizar el pipeline GEIH de vivienda ya construido, probado y auditado para una sola ciudad
(Ibagué, `AREA=73` hardcodeado) a las 23 ciudades capitales / áreas metropolitanas de Colombia,
para 2023-2026 parcial. El enfoque técnico es **parametrizar, no reescribir**: los mismos scripts
Python existentes pasan a iterar sobre una lista de 23 ciudades en vez de una constante, se añaden
4 módulos nuevos que no existían en el piloto (resolución/validación de dominio geográfico por
ciudad, obtención de proyecciones poblacionales CNPV, varianza por bootstrap de conglomerado, y
generalización del suite de auditoría), y se excluye explícitamente la ECV y los entregables
narrativos (fichas, videos) de esta fase.

## Technical Context

**Language/Version**: Python 3.11+ (entorno de desarrollo actual: 3.13.2)

**Primary Dependencies**: pandas, numpy, openpyxl, requests (ya en uso en el piloto); statsmodels
(solo en el suite de auditoría, para replicación independiente). No se requieren dependencias
nuevas: la obtención de proyecciones CNPV usa `requests` (ya presente) y el bootstrap de
conglomerado usa `numpy`/`pandas` (ya presentes).

**Storage**: sistema de archivos local únicamente (ZIP/CSV/XLSX/JSON). Sin base de datos.

**Testing**: sin framework formal (no pytest/unittest) — convención ya establecida e intencional
del proyecto: scripts de auditoría independientes (`scripts/aud_*.py`) que corren sobre datos
reales ya calculados y emiten veredictos pasa/no-pasa, en vez de tests contra mocks. Se mantiene
esta convención para las 23 ciudades (ver Constitution Check).

**Target Platform**: Windows 11 / PowerShell como shell principal para orquestar; el código
Python en sí es agnóstico de SO (ya usa `pathlib`), se mantiene así.

**Project Type**: pipeline de procesamiento por lotes (CLI), proyecto único — no hay
frontend/backend ni app móvil.

**Performance Goals**: sin SLA de servicio interactivo (es un batch job, no un servicio). Meta
operativa: una corrida completa del pipeline (23 ciudades × 4 años, incluyendo el bootstrap de
varianza) debe completarse en una sola sesión de trabajo local (horas, no días) sobre los ~2.5GB
de microdatos ya descargados.

**Constraints**: los microdatos públicos de GEIH no traen variables de diseño muestral
(UPM/segmento/estrato) — la varianza de "diseño complejo" solo puede aproximarse vía bootstrap
por conglomerado agrupado en `DIRECTORIO` (ver Principio VII de la constitución), nunca vía
linearización de Taylor real. El código nuevo debe reutilizar y extender los módulos compartidos
ya existentes (`scripts/io_geih.py`, `scripts/stats_ponderadas.py`) en vez de duplicarlos.

**Scale/Scope**: 23 ciudades × 4 años (2023, 2024, 2025, 2026 parcial Ene-Jun) × ~7 bloques de
indicadores (tenencia, arriendo, esfuerzo financiero, vivienda propia/crédito, hacinamiento,
servicios, ingreso/pobreza) × réplicas de bootstrap por indicador publicado. ~42 archivos GEIH
mensuales ya en disco (national scope) + 3 años de Pobreza Monetaria + 1 fuente nueva (CNPV,
agregada y pequeña, no microdatos).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principio / Sección de la constitución | Gate | Estado |
|---|------------------------------------------|------|--------|
| I | Rigor Metodológico Ante Todo | El plan no atajos la validación por velocidad (mantiene los 3 pasos de verificación geográfica, poblacional y de auditoría para las 23 ciudades) | PASS |
| II | Cero Alucinación de Datos | El plan resuelve los códigos de dominio geográfico empíricamente en tiempo de ejecución (User Story 1), no los fija como constantes de diseño; toda ciudad no verificable queda ND | PASS |
| III | Ponderación Estadística Obligatoria | El plan reutiliza `stats_ponderadas.py` sin alterar su uso de `FEX_C18`; ningún módulo nuevo calcula proporciones sin ponderar | PASS |
| IV | Precisión en Variables Monetarias de Vivienda | El plan reutiliza sin cambios la lógica de limpieza P5090/P5100/P5110/P5130/P5140 ya auditada, solo la generaliza por ciudad | PASS |
| V | Comparabilidad Temporal Honesta | El plan reutiliza y generaliza `aud_N_O_periodo_homogeneo.py` / `aud_N_tabla_homogenea_completa.py`, ya construidos para este propósito | PASS |
| VI | Umbral de Publicación por Confiabilidad | El plan reutiliza `clasificar_confiabilidad()` sin relajar sus umbrales para las ciudades nuevas | PASS |
| VII | Transparencia sobre Limitaciones del Diseño Muestral | El nuevo módulo de bootstrap (`stats_bootstrap.py`) debe documentar en su docstring, igual que `stats_ponderadas.py` ya lo hace, que es una aproximación conservadora y no Taylor linearization real | PASS (obligación de diseño, ver data-model.md) |
| VIII | Reproducibilidad y Reutilización de Código Auditado | Es la decisión estructural central de este plan: generalizar in-place, no crear una rama de código paralela | PASS |
| IX | Idioma de Trabajo: Español | Todo código, comentarios y documentos nuevos siguen en español, igual que el código existente | PASS |
| X | Fuentes Oficiales Exclusivas | El módulo nuevo de proyecciones poblacionales apunta exclusivamente a dane.gov.co (dominio oficial) | PASS |
| Alcance Fase 1/2 | ECV fuera de alcance | Ningún módulo de este plan descarga ni procesa ECV; el bloque de déficit habitacional se deja explícitamente "ND" | PASS |
| Loop Engineering | No generar narrativa antes de auditar | Esta feature no incluye entregables narrativos (fichas/videos) en absoluto — la restricción no aplica aquí, se aplicará en la especificación de la fase narrativa posterior | N/A (fuera del alcance de esta feature) |

**Resultado**: 11 PASS, 1 N/A, 0 FAIL. No se requiere la tabla de Complexity Tracking.

**Re-chequeo posterior al diseño de Fase 1** (tras `research.md`, `data-model.md`, `contracts/`,
`quickstart.md`): ningún artefacto de diseño introdujo una dependencia, atajo o excepción nueva
frente a la tabla anterior. El campo `deficit_habitacional_*` se modela explícitamente como
"ND" (Alcance Fase 1/2, PASS); el smoke test de `quickstart.md` para el bootstrap exige que el
nuevo error estándar no sea menor al método "sandwich" anterior, reforzando el Principio VII en
vez de debilitarlo. Se mantiene: 11 PASS, 1 N/A, 0 FAIL.

## Project Structure

### Documentation (this feature)

```text
specs/001-observatorio-vivienda-nacional/
├── plan.md              # Este archivo
├── research.md          # Fase 0
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/           # Fase 1 (esquema de los entregables, no una API)
│   └── entregables_schema.md
└── tasks.md             # Fase 2 (/speckit-tasks, aún no generado)
```

### Source Code (repository root)

Proyecto único (no hay opción frontend/backend/mobile). Estructura real ya existente, que este
plan extiende in-place — no se crea un árbol paralelo:

```text
observatorio de vivienda/
├── GEIH/                                  # datos (ya existente)
│   ├── {2023,2024,2025,2026}/*.zip        # microdatos GEIH nacionales (ya descargados)
│   ├── pobreza/{2023,2024,2025}/          # Pobreza Monetaria DANE (ya descargado)
│   ├── proyecciones_poblacion/            # [NUEVO] proyecciones CNPV 2018 (dane.gov.co)
│   ├── diccionarios/                      # diccionarios oficiales DANE (ya existente)
│   ├── diccionario_armonizado.csv         # [EXTENDER] ya documenta los 23 dominios (ver research.md)
│   ├── loop4_ibague_control.csv           # control geográfico del piloto (se mantiene, histórico)
│   ├── control_geografico_23_ciudades.csv # [NUEVO] equivalente generalizado a las 23 ciudades
│   └── procesado_nacional/                # [NUEVO] intermedios de las 23 ciudades (no pisa procesado/ del piloto)
├── scripts/
│   ├── config_ciudades.py                 # [NUEVO] lista canónica de 23 ciudades + código de dominio hipótesis
│   ├── 02b_descarga_proyecciones_poblacion.py  # [NUEVO] Loop 2 — fuente CNPV
│   ├── 04_identificacion_ciudades.py      # [NUEVO] generaliza 04_identificacion_ibague.py a 23 ciudades
│   ├── 06_validacion_poblacion_cnpv.py    # [NUEVO] Loop 2 — compara FEX_C18 vs. proyección DANE
│   ├── stats_bootstrap.py                 # [NUEVO] bootstrap por conglomerado DIRECTORIO + DEFF
│   ├── 05_limpieza.py                     # [MODIFICAR] parametrizar por ciudad (hoy hardcodea Ibagué)
│   ├── 07_indicadores_principales.py      # [MODIFICAR] parametrizar por ciudad
│   ├── 08_ingresos_pobreza.py             # [MODIFICAR] parametrizar por ciudad
│   ├── 11_validacion_temporal.py          # [MODIFICAR] parametrizar por ciudad
│   ├── 13_tabla_final.py                  # [MODIFICAR] consolidar 23 ciudades en vez de 1
│   ├── 14_generar_excel.py                # [MODIFICAR] generar el libro de 12 hojas nacional
│   ├── 15_rankings_nacionales.py          # [NUEVO] Loop 8 — rankings comparados entre las 23 ciudades
│   ├── aud_*.py (9 scripts existentes)    # [MODIFICAR] parametrizar por ciudad, sin cambiar su lógica de prueba
│   ├── 99_auditoria_matriz_final.py       # [MODIFICAR] consolidar veredictos de 23 ciudades
│   ├── 98_generar_excel_auditoria.py      # [MODIFICAR] libro de auditoría nacional
│   ├── io_geih.py                         # [REUTILIZAR sin cambios]
│   └── stats_ponderadas.py                # [REUTILIZAR sin cambios]
├── output/                                # [EXTENDER] agrega los 4 entregables nuevos junto a los del piloto
├── script_geih_ibague.py                  # orquestador del piloto (se conserva intacto, histórico)
├── script_auditoria_geih.py               # auditoría del piloto (se conserva intacto, histórico)
├── script_observatorio_nacional.py        # [NUEVO] orquestador de las 23 ciudades (mismo patrón que el piloto)
└── script_auditoria_nacional.py           # [NUEVO] auditoría de las 23 ciudades (mismo patrón que el piloto)
```

**Structure Decision**: extender la estructura real ya existente in-place (Principio VIII). No se
introduce un árbol de directorios paralelo para "nacional" — los scripts de etapa se parametrizan
por ciudad y los datos/salidas nacionales se distinguen de los del piloto por sufijo
(`_nacional`, `control_geografico_23_ciudades.csv`) para no sobrescribir ni perder los artefactos
ya auditados de Ibagué, que quedan como referencia histórica y como caso de prueba de regresión
(Ibagué debe seguir dando los mismos resultados dentro del cálculo de las 23 ciudades).

## Complexity Tracking

*No aplica — el Constitution Check no registró violaciones que requieran justificación.*

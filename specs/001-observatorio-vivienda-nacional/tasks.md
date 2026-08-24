---
description: "Task list for Motor Nacional del Observatorio de Vivienda — Fase 1 (23 Ciudades)"
---

# Tasks: Motor Nacional del Observatorio de Vivienda — Fase 1 (23 Ciudades, GEIH + Pobreza)

**Input**: Design documents from `/specs/001-observatorio-vivienda-nacional/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/entregables_schema.md, quickstart.md (todos ya generados)

**Tests**: no se generan tareas de test formal (pytest/mocks) — decisión intencional del proyecto
(ver plan.md → Technical Context → Testing). La "prueba" de cada historia de usuario son los
propios scripts de auditoría (`aud_*.py`, generalizados en la Fase 6) corriendo contra datos
reales del DANE, más los pasos de `quickstart.md`.

**Organization**: las tareas están agrupadas por historia de usuario (spec.md), en el mismo orden
de prioridad P1→P4, porque aquí las historias tienen una dependencia real y secuencial (no son
módulos independientes de un CRUD): sin ciudades validadas geográficamente no hay indicadores;
sin indicadores no hay varianza que estimar; sin varianza no hay nada que auditar.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede ejecutar en paralelo (archivos distintos, sin dependencia de tareas incompletas)
- **[Story]**: historia de usuario a la que pertenece (US1-US4)
- Cada tarea indica la ruta de archivo exacta (relativa a la raíz del proyecto)

## Path Conventions

Proyecto único (pipeline CLI en Python), no hay frontend/backend. Todas las rutas son relativas a
la raíz `observatorio de vivienda/`, siguiendo la estructura ya fijada en `plan.md`.

---

## Phase 1: Setup

**Purpose**: preparar la estructura de carpetas nueva que usarán las historias siguientes.

- [X] T001 [P] Crear las carpetas `GEIH/proyecciones_poblacion/` y `GEIH/procesado_nacional/` (vacías, con `.gitkeep` si aplica)
- [X] T002 [P] Confirmar en el entorno que `pandas`, `numpy`, `openpyxl`, `requests` y `statsmodels` ya están instalados (mismas versiones que usa `script_geih_ibague.py`); no se agrega pytest ni ningún framework de testing nuevo, por convención ya establecida del proyecto

**Checkpoint**: estructura de carpetas lista, sin tocar aún ningún script existente.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: crear el artefacto del que dependen las 4 historias de usuario.

**⚠️ CRITICAL**: ninguna historia de usuario puede empezar antes de que T003 exista.

- [X] T003 Crear `scripts/config_ciudades.py` con la lista canónica de las 23 ciudades capitales/áreas metropolitanas (nombre, código de dominio **hipótesis** según `research.md` — ej. `73=Ibagué`, `11=Bogotá D.C.`, `05=Medellín A.M.`, etc. — y departamento), dejando explícito en el módulo que estos códigos son un punto de partida a verificar empíricamente, no una verdad asumida (Principio II de la constitución)

**Checkpoint**: `config_ciudades.py` disponible — Fase 3 puede comenzar.

---

## Phase 3: User Story 1 - Identificación y validación geográfica de las 23 ciudades (Priority: P1) 🎯 MVP

**Goal**: cada una de las 23 ciudades queda con su código de dominio geográfico verificado
empíricamente por año, y su población expandida contrastada contra la proyección oficial DANE.

**Independent Test**: generar únicamente `GEIH/control_geografico_23_ciudades.csv` (sin haber
calculado todavía ningún indicador de vivienda) y verificar que las 23 ciudades queden
clasificadas como válidas, ND o con alerta — ver Paso 1 de `quickstart.md`.

### Implementation for User Story 1

- [X] T004 [US1] Generalizar la lógica de `scripts/04_identificacion_ibague.py` en un nuevo `scripts/04_identificacion_ciudades.py`: iterar sobre las 23 ciudades de `config_ciudades.py` (en vez del `AREA=73` hardcodeado), cruzar `AREA` vs `DPTO`/`CLASE` y unicidad de hogar por ciudad-mes-año, generar `GEIH/control_geografico_23_ciudades.csv` (mismas columnas que `GEIH/loop4_ibague_control.csv` + columna `ciudad_nombre`)
- [X] T005 [US1] En `scripts/04_identificacion_ciudades.py`, manejar el caso "ciudad sin dominio propio ese año en el diccionario oficial": marcar esa ciudad-año como `codigo_dominio_confirmado="ND"` en vez de fallar el script o inventar un código (Edge Case de `spec.md`)
- [X] T006 [P] [US1] Crear `scripts/02b_descarga_proyecciones_poblacion.py`: localizar en `dane.gov.co` (no `microdatos.dane.gov.co`) las proyecciones oficiales de población/hogares con base en el CNPV 2018, descargarlas a `GEIH/proyecciones_poblacion/`, y registrar la URL/fecha de descarga para trazabilidad (Principio X)
- [X] T007 [US1] Crear `scripts/06_validacion_poblacion_cnpv.py`: comparar la suma de `FEX_C18` por ciudad-año (salida de T004) contra la proyección de T006, clasificar `estado_poblacional` como `DENTRO_TOLERANCIA` / `REVISAR` / `ND` (tolerancia ±5%, o `ND` si la proyección no desagrega esa ciudad — Edge Case de `spec.md`)
- [X] T008 [US1] En `scripts/04_identificacion_ciudades.py`, generalizar la regla ya usada en el piloto de bloquear el avance de una ciudad-mes si la suma de `FEX_C18` antes y después de deduplicar hogares no coincide exactamente (Edge Case de `spec.md`)

**Checkpoint**: User Story 1 completa y verificable de forma independiente (Paso 1 de `quickstart.md`).

---

## Phase 4: User Story 2 - Indicadores núcleo de vivienda por ciudad y año (Priority: P2)

**Goal**: tenencia, arriendo, esfuerzo financiero, vivienda propia/crédito, hacinamiento,
servicios públicos e ingreso/pobreza calculados de forma ponderada para las 23 ciudades.

**Independent Test**: generar la tabla larga de indicadores para las 23 ciudades y verificar que
las 7 categorías de tenencia sumen 100% (±0.1pp) por ciudad-año — ver Paso 2 de `quickstart.md`.

### Implementation for User Story 2

- [X] T009 [US2] Generalizar `scripts/05_limpieza.py` para filtrar por las 23 ciudades confirmadas en `GEIH/control_geografico_23_ciudades.csv` (T004) en vez del `AREA=73` hardcodeado, preservando sin cambios las reglas de limpieza ya auditadas de P5090/P5100/P5110/P5130/P5140 (Principio IV)
- [X] T010 [US2] Generalizar `scripts/07_indicadores_principales.py` para calcular tenencia (7 categorías P5090), arriendo (mediana/media/P25/P75 ponderados vía `stats_ponderadas.py`), hacinamiento (`P6008/P5010`) y cobertura de servicios públicos, agrupando por `ciudad_nombre × anio`
- [X] T011 [P] [US2] Generalizar `scripts/08_ingresos_pobreza.py`: cruzar con la base de Pobreza Monetaria DANE por `directorio+secuencia_p` para las 23 ciudades, calcular esfuerzo financiero (ratio arriendo/ingreso, % sobrecarga >30%, % sobrecarga severa >50%, brecha de ingreso propietarios/arrendatarios) y pobreza monetaria por tenencia
- [X] T012 [US2] Generalizar `scripts/11_validacion_temporal.py` para aplicar, en las 23 ciudades, la comparación pareada 2026 parcial vs. mismo período 2025 (Principio V) — incluyendo la re-verificación del catálogo DANE vigente antes de fijar el corte de meses de 2026, por si ya hay más meses publicados que Ene-Jun (Edge Case de `spec.md`)
- [X] T013 [US2] Generalizar `scripts/13_tabla_final.py` para consolidar la tabla larga maestra de las 23 ciudades según el esquema de `contracts/entregables_schema.md`, incluyendo la columna `bloque_indicador="deficit_habitacional"` siempre con `valor="ND — pendiente Fase 2 (ECV)"` (FR-013) — depende de T010, T011, T012

**Checkpoint**: Historias 1 y 2 funcionan juntas de forma independiente (Paso 2 de
`quickstart.md`); ya es posible correr el caso de regresión de Ibagué sobre los indicadores núcleo.

---

## Phase 5: User Story 3 - Precisión estadística y varianza de diseño complejo (Priority: P3)

**Goal**: cada indicador incluye error estándar, IC95%, DEFF y una etiqueta de confiabilidad
consistente con el estándar DANE.

**Independent Test**: sobre un indicador ya calculado en la Historia 2, el bootstrap por
`DIRECTORIO` produce un SE, el DEFF resultante es ≥1, y la clasificación de confiabilidad sigue
los umbrales oficiales — ver Paso 3 de `quickstart.md`.

### Implementation for User Story 3

- [X] T014 [US3] Crear `scripts/stats_bootstrap.py`: remuestreo de `DIRECTORIO` con reemplazo dentro de cada celda ciudad-año, recálculo del indicador ponderado en cada réplica (200-500 réplicas), derivación de error estándar e IC95% desde la distribución empírica; documentar en el docstring del módulo, con el mismo estilo que `stats_ponderadas.py`, la limitación del Principio VII (`DIRECTORIO` ≈ vivienda, no el segmento/UPM real del diseño)
- [X] T015 [US3] En `scripts/stats_bootstrap.py`, implementar `DEFF = Var_bootstrap / Var_MAS_naive`, reutilizando la fórmula de varianza de muestreo aleatorio simple como referencia (depende de T014)
- [X] T016 [US3] Añadir el flag `--smoke-test` a `scripts/stats_bootstrap.py` (descrito en `quickstart.md`): verifica sobre un indicador conocido de Ibagué que el SE del bootstrap no sea menor al SE "sandwich" de `stats_ponderadas.weighted_se_mean_approx` — un SE menor sería señal de bug (depende de T014, T015)
- [X] T017 [US3] Integrar `scripts/stats_bootstrap.py` en `scripts/13_tabla_final.py` para anexar `error_estandar`, `ic95_inf`, `ic95_sup`, `deff`, `n_muestral` y `cv_pct` a cada fila de la tabla larga (depende de T013, T014, T015)
- [X] T018 [US3] Reutilizar `scripts/stats_ponderadas.clasificar_confiabilidad()` sin modificarlo para asignar `etiqueta_confiabilidad` (EXCELENTE/ACEPTABLE/PRECAUCION/NO_PUBLICAR) a cada fila, según los umbrales del Principio VI (depende de T017)

**Checkpoint**: Historias 1-3 funcionan juntas; Paso 3 de `quickstart.md` pasa.

---

## Phase 6: User Story 4 - Auditoría "red team" y entregables consolidados (Priority: P4)

**Goal**: la tabla nacional completa pasa las 4 pruebas adversariales antes de empaquetarse en
los entregables finales.

**Independent Test**: ejecutar la auditoría sobre la tabla ya consolidada y obtener un veredicto
explícito (`APROBADO`/`ADVERTENCIA`/`RECHAZADO`) por celda, sin intervención manual — ver Paso 4
de `quickstart.md`.

### Implementation for User Story 4

- [X] T019 [P] [US4] Generalizar los 9 scripts `scripts/aud_*.py` (ya auditados para Ibagué: `aud_L_panel_rotativo.py`, `aud_N_O_periodo_homogeneo.py`, `aud_N_tabla_homogenea_completa.py`, `aud_F_I_replicacion_independiente.py`, `aud_H_U_sensibilidad_outliers.py`, `aud_J_cv_dane_benchmark.py`, `aud_Z_consistencia_p5090_cruzada.py`) para iterar sobre las 23 ciudades, sin cambiar su lógica de prueba interna (depende de T017, T018)
- [X] T020 [US4] Generalizar `scripts/99_auditoria_matriz_final.py` para consolidar los veredictos de las 4 pruebas red-team (suma de tenencia, sensibilidad a outliers/winsorización P99, consistencia P5130/P5140, umbral de publicación n<30 o CV>25%) de las 23 ciudades (depende de T019)
- [X] T021 [P] [US4] Crear `scripts/15_rankings_nacionales.py`: generar las 5 tablas de ranking por año (inquilinato, costo de arriendo, estrés habitacional >30%, desigualdad de ingreso propietario/inquilino, hacinamiento), ordenando las 23 ciudades (FR-011) (depende de T018)
- [X] T022 [US4] Generalizar `scripts/14_generar_excel.py` para producir `output/observatorio_vivienda_capitales_2023_2026.xlsx` con las 12 hojas de `contracts/entregables_schema.md`, y `output/observatorio_vivienda_capitales_2023_2026.csv` (depende de T018, T021)
- [X] T023 [US4] Generalizar `scripts/98_generar_excel_auditoria.py` para producir `output/auditoria_estadistica_observatorio_nacional.xlsx` (depende de T020)
- [X] T024 [US4] Crear `script_observatorio_nacional.py` en la raíz (orquestador, mismo patrón de etapas y flag `--desde` que `script_geih_ibague.py`) y `script_auditoria_nacional.py` (mismo patrón que `script_auditoria_geih.py`) (depende de T022, T023)
- [X] T025 [US4] Implementar en `script_observatorio_nacional.py` el bloqueo de FR-014: no generar los entregables finales (T022) si `99_auditoria_matriz_final.py` (T020) reporta algún `RECHAZADO` — el pipeline se detiene y reporta, no continúa silenciosamente (depende de T024)
- [X] T026 [P] [US4] Redactar `metodologia_observatorio_nacional.md` (fórmulas KaTeX de cada indicador, justificación de `FEX_C18`, tratamiento del panel rotativo, limitación del bootstrap por `DIRECTORIO` citada explícitamente y no relegada a nota al pie, notas por ciudad cuando `estado_geografico` o `estado_poblacional` sea `ND`) (depende de T022)

**Checkpoint**: las 4 historias de usuario funcionan juntas — feature completa.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: validación final de extremo a extremo antes de considerar la feature terminada.

- [X] T027 [P] Ejecutar el caso de regresión obligatorio: Ibagué 2023-2026 debe reproducir, dentro del cálculo de las 23 ciudades, los mismos valores ya publicados en `output/geih_ibague_vivienda_2023_2026.csv` del piloto (ver `quickstart.md`)
- [X] T028 [P] Verificar la consistencia cruzada SC-007 sobre 2-3 celdas de muestra (p. ej. canon mediano de Bogotá 2025): mismo valor en `Resumen_Nacional`, en el CSV maestro y en `Precision_CV`
- [X] T029 Ejecutar `quickstart.md` de principio a fin (Pasos 1-5) como aceptación final de la feature, confirmando que `script_observatorio_nacional.py` produce los 4 entregables de `contracts/entregables_schema.md` sin intervención manual

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias — puede empezar de inmediato
- **Foundational (Phase 2)**: depende de Setup — bloquea las 4 historias de usuario (nadie puede filtrar por ciudad sin `config_ciudades.py`)
- **User Story 1 (Phase 3)**: depende de Foundational
- **User Story 2 (Phase 4)**: depende de User Story 1 (T004) — necesita saber qué registros pertenecen a qué ciudad antes de calcular cualquier indicador
- **User Story 3 (Phase 5)**: depende de User Story 2 (T013) — necesita indicadores ya calculados sobre los cuales estimar varianza
- **User Story 4 (Phase 6)**: depende de User Story 2 y 3 (T017, T018) — audita y empaqueta lo que ya existe
- **Polish (Phase 7)**: depende de que Phase 6 esté completa

A diferencia de una aplicación CRUD típica, estas 4 historias **no son independientes entre sí**
más allá de permitir una prueba de aceptación propia en cada checkpoint — hay una cadena de
dependencia real de datos (geografía → indicadores → precisión → auditoría) que sigue el mismo
orden que los Loops del prompt maestro original.

### Parallel Opportunities

- T001 y T002 (Setup) en paralelo
- T006 (proyecciones CNPV) puede avanzar en paralelo a T004-T005-T008 (identificación geográfica) dentro de la Historia 1, ya que son archivos y fuentes de datos independientes — solo T007 necesita ambos resultados
- T011 (ingresos/pobreza) puede avanzar en paralelo a T010 (indicadores principales) dentro de la Historia 2, ya que son scripts distintos que no se escriben entre sí — T013 espera a ambos
- T019 (generalizar los 9 `aud_*.py`) y T021 (rankings nacionales) pueden avanzar en paralelo dentro de la Historia 4
- T026 (redactar la metodología) puede avanzar en paralelo a T023-T025 una vez que T022 esté lista
- T027 y T028 (Polish) en paralelo

---

## Parallel Example: User Story 1

```bash
# T006 puede lanzarse en paralelo a T004 (archivos y fuentes distintas):
Task: "Crear scripts/02b_descarga_proyecciones_poblacion.py"
Task: "Generalizar scripts/04_identificacion_ciudades.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 solamente)

1. Completar Phase 1 (Setup) y Phase 2 (Foundational)
2. Completar Phase 3 (User Story 1)
3. **DETENERSE Y VALIDAR**: correr el Paso 1 de `quickstart.md` — confirmar que las 23 ciudades
   quedan clasificadas (válida/ND/alerta) antes de invertir en calcular un solo indicador
4. Solo entonces continuar a la Historia 2

### Entrega incremental

1. Setup + Foundational → base lista
2. Historia 1 → validar independientemente → checkpoint geográfico confiable
3. Historia 2 → validar independientemente (incluye regresión de Ibagué) → checkpoint de indicadores
4. Historia 3 → validar independientemente (smoke test de bootstrap) → checkpoint de precisión
5. Historia 4 → validar independientemente → entregables finales de la Fase 1 completos

No aplica una "estrategia de equipo en paralelo" por historia (a diferencia del template
genérico): dado que las historias dependen unas de otras en datos, el orden P1→P4 es también el
orden de ejecución real, no solo de prioridad.

---

## Notes

- `[P]` = archivos distintos sin dependencia directa entre sí
- `[Story]` mapea cada tarea a su historia de usuario para trazabilidad
- Ningún script existente auditado (`io_geih.py`, `stats_ponderadas.py`, la lógica de limpieza
  P5090/P5100/P5110/P5130/P5140) se reescribe — solo se generalizan los scripts de etapa que hoy
  asumen una sola ciudad
- Evitar: generar los entregables narrativos (fichas, rankings interpretativos, guiones de
  video) en esta feature — están fuera de alcance por diseño (ver `spec.md` → Assumptions)

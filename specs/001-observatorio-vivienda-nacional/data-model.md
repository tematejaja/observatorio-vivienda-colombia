# Data Model — Motor Nacional del Observatorio de Vivienda (Fase 1)

Extraído de la sección "Key Entities" de `spec.md`, con campos y reglas de validación concretas.
No son tablas de base de datos (el proyecto no usa una) sino la forma de los DataFrames/CSV
intermedios y de las filas de los entregables finales.

## Ciudad

Una de las 23 ciudades capitales / áreas metropolitanas en alcance.

| Campo | Tipo | Descripción | Regla de validación |
|---|---|---|---|
| `ciudad_nombre` | string | Nombre canónico (ej. "Ibagué", "Bogotá D.C.") | Debe pertenecer a la lista fija de 23 nombres de `spec.md` |
| `codigo_dominio_hipotesis` | string | Código AREA propuesto en `config_ciudades.py` (ver research.md) | Punto de partida, no verdad asumida |
| `codigo_dominio_confirmado` | string \| "ND" | Código AREA verificado empíricamente para un año dado | Solo se llena tras pasar el cruce contra DPTO/CLASE (ver Hogar) |
| `anio` | int (2023-2026) | Año al que aplica la confirmación | Cada ciudad tiene una fila de confirmación por año |
| `estado_geografico` | enum: `VALIDO` \| `ND` \| `ALERTA` | Resultado de la identificación (User Story 1) | `ALERTA` si hay duplicados de hogar o inconsistencia DPTO/CLASE |
| `estado_poblacional` | enum: `DENTRO_TOLERANCIA` \| `REVISAR` \| `ND` | Resultado de comparar `FEX_C18` sumado contra la proyección CNPV (User Story 1, FR-002) | `ND` si la proyección no desagrega esa ciudad |

**Relaciones**: una Ciudad tiene muchos Hogares (vía `codigo_dominio_confirmado` = `AREA` del
registro); una Ciudad tiene muchos Indicadores (uno por ciudad × año × métrica).

## Periodo

| Campo | Tipo | Descripción | Regla de validación |
|---|---|---|---|
| `anio` | int | 2023, 2024, 2025 o 2026 | — |
| `es_parcial` | bool | `true` únicamente para 2026 | Todo output que muestre 2026 debe rotularlo "2026*" cuando `es_parcial=true` |
| `meses_incluidos` | list[int] | Meses realmente publicados por el DANE para ese año | Para 2026, se revalida contra el catálogo DANE vigente en el momento de ejecución (no se asume fijo en Ene-Jun) |
| `mes_corte_comparacion` | int | Último mes común entre el año parcial y su año de comparación pareada | Usado por la comparabilidad temporal (Principio V); nunca se compara un período parcial contra un año completo sin este corte |

## Hogar

Registro de vivienda a nivel de microdato GEIH (una fila de `GEIH/*/​*.zip`, módulo "Datos del
hogar y la vivienda"), ya filtrado a las 23 ciudades.

| Campo | Tipo | Descripción | Regla de validación |
|---|---|---|---|
| `directorio`, `secuencia_p`, `hogar` | string | Componentes de la llave única | La combinación debe ser única dentro de cada ciudad-mes (FR generalizado de la regla ya usada en el piloto: suma de `FEX_C18` antes/después de deduplicar debe coincidir exactamente) |
| `area` | string | Código de dominio GEIH del registro | Debe coincidir con `codigo_dominio_confirmado` de alguna Ciudad para ese año, o el registro no entra al universo de las 23 ciudades |
| `dpto`, `clase` | string | Variables de verificación cruzada | Usadas para marcar `ALERTA` en Ciudad si no son consistentes con `area` |
| `p5090` | string (1-7) | Categoría de tenencia | Códigos fuera de 1-7 se descartan antes de cualquier cálculo |
| `p5100_num`, `p5110_num`, `p5130_num`, `p5140_num` | float \| NaN | Variables monetarias ya limpias | Cada una solo es válida para el subconjunto de `p5090` que le corresponde (ver Principio IV); 98/99 y outliers ya convertidos a NaN/flag |
| `fex_c18` | float | Factor de expansión | Nunca se omite en un cálculo poblacional (Principio III) |
| `pobre` | int (0/1) \| "ND" | Condición oficial de pobreza monetaria, tras el cruce con la base de Pobreza Monetaria DANE | "ND" si el hogar no tiene match en la base de pobreza de ese año |

**Relaciones**: un Hogar pertenece a exactamente una Ciudad-año (vía `area` confirmado); muchos
Hogares agregan a un Indicador.

## Indicador

Una métrica calculada y publicable para una Ciudad × Periodo × variable.

| Campo | Tipo | Descripción | Regla de validación |
|---|---|---|---|
| `ciudad_nombre`, `anio` | — | Llave de agregación | — |
| `nombre_indicador` | string | Ej. `pct_arriendo`, `canon_mediano`, `pct_sobrecarga_30` | Debe pertenecer al catálogo de indicadores de `spec.md` FR-003 a FR-008 |
| `valor` | float \| "ND" | Estimación puntual ponderada | "ND" si `n < 30` para ese corte (Principio VI), nunca un valor forzado |
| `error_estandar` | float \| null | SE vía bootstrap por conglomerado | Ver Indicador → Precisión más abajo |
| `ic95_inf`, `ic95_sup` | float \| null | Intervalo de confianza al 95% | Derivado de la distribución empírica de réplicas bootstrap, no de una fórmula analítica cerrada |
| `deff` | float \| null | `Var_bootstrap / Var_MAS_naive` | Se documenta junto con la nota de limitación (Principio VII) siempre que se muestre |
| `n_muestral` | int | Tamaño de muestra no ponderado del corte | — |
| `cv` | float \| null | Coeficiente de variación (%) | — |
| `etiqueta_confiabilidad` | enum: `EXCELENTE` \| `ACEPTABLE` \| `PRECAUCION` \| `NO_PUBLICAR` | Clasificación oficial DANE por n y CV | Debe coincidir exactamente con los umbrales del Principio VI; ver `stats_ponderadas.clasificar_confiabilidad` |
| `deficit_habitacional_*` | — | Placeholder para Fase 2 | Siempre `"ND — pendiente Fase 2 (ECV)"` en esta fase (FR-013); el campo existe en el esquema de salida pero nunca se calcula aquí |

**Relaciones**: un Indicador pertenece a una Ciudad y un Periodo; puede tener asociado un
Resultado de Auditoría.

## Resultado de Auditoría

Veredicto de una de las 4 pruebas adversariales (Loop 9 / FR-012) sobre una Ciudad-Periodo o
sobre un Indicador puntual.

| Campo | Tipo | Descripción | Regla de validación |
|---|---|---|---|
| `tipo_prueba` | enum: `SUMA_TENENCIA` \| `SENSIBILIDAD_OUTLIERS` \| `CONSISTENCIA_P5130_P5140` \| `UMBRAL_PUBLICACION` | Cuál de las 4 pruebas red-team | Coincide 1:1 con las pruebas ya implementadas en `scripts/aud_*.py` para el piloto |
| `ciudad_nombre`, `anio` | — | Alcance del veredicto | — |
| `resultado` | enum: `APROBADO` \| `ADVERTENCIA` \| `RECHAZADO` | Veredicto | Un `RECHAZADO` en cualquier ciudad-año bloquea la generación de los entregables finales (FR-014) hasta corregirse |
| `evidencia` | string / ruta a CSV | Detalle reproducible del hallazgo | Debe ser suficiente para que alguien reproduzca el veredicto sin releer el código |

**Relaciones**: un Resultado de Auditoría referencia una Ciudad-Periodo y, opcionalmente, un
Indicador específico.

## Notas de generalización (piloto → nacional)

- Todas las entidades de arriba ya existen implícitamente en el pipeline del piloto, pero con
  `ciudad_nombre` fijo a "Ibagué" en vez de ser una columna variable. La generalización consiste
  en convertir ese valor fijo en una dimensión real de los DataFrames (`groupby("ciudad_nombre")`
  en vez de asumir una sola ciudad), no en cambiar los nombres o tipos de campo.
- El campo `deficit_habitacional_*` se incluye desde ya en el esquema (aunque siempre "ND" en
  esta fase) para que la Fase 2 (ECV) solo tenga que llenar una columna ya prevista, en vez de
  romper el esquema del CSV/Excel ya publicado en Fase 1.

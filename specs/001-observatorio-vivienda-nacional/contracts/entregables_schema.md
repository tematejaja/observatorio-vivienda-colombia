# Contrato de Entregables — Motor Nacional del Observatorio de Vivienda (Fase 1)

Este proyecto no expone una API ni un servicio: su "contrato" es el esquema de los archivos que
produce, porque otros consumidores dependen de él sin ver el código — la fase narrativa
posterior (fichas, rankings, videos), la metodología, y cualquier persona que abra el Excel
directamente. Fijar este esquema ahora evita que Fase 2 tenga que adivinarlo.

## `observatorio_vivienda_capitales_2023_2026.csv` (tabla maestra, formato largo/tidy)

Una fila = una combinación (ciudad, año, indicador). Columnas:

| Columna | Tipo | Ejemplo | Notas |
|---|---|---|---|
| `ciudad` | string | `Ibagué` | Uno de los 23 nombres canónicos |
| `codigo_dominio` | string | `73` | O `ND` si no se pudo confirmar (ver data-model.md → Ciudad) |
| `anio` | string | `2026*` | El asterisco marca período parcial (Principio V) |
| `meses_incluidos` | string | `Ene-Jun` | Explícito, nunca implícito |
| `bloque_indicador` | string | `tenencia` \| `arriendo` \| `esfuerzo_financiero` \| `vivienda_propia_credito` \| `hacinamiento` \| `servicios_publicos` \| `ingreso_pobreza` \| `deficit_habitacional` | `deficit_habitacional` siempre en "ND" en esta fase |
| `nombre_indicador` | string | `canon_mediano_cop` | Catálogo cerrado, ver data-model.md → Indicador |
| `valor` | float \| `"ND"` | `850000` | Nunca un número inventado cuando debería ser ND |
| `error_estandar` | float \| vacío | `12500` | Vacío si `valor="ND"` |
| `ic95_inf`, `ic95_sup` | float \| vacío | | |
| `deff` | float \| vacío | `1.34` | |
| `n_muestral` | int | `412` | Tamaño de muestra no ponderado |
| `cv_pct` | float \| vacío | `4.8` | |
| `etiqueta_confiabilidad` | string | `ACEPTABLE` | Uno de los 4 valores del Principio VI |
| `fuente` | string | `GEIH 2026 catálogo ANDA 900` | Trazabilidad exigida por el Principio X |

## `observatorio_vivienda_capitales_2023_2026.xlsx` (12 hojas)

| Hoja | Contenido | Grano |
|---|---|---|
| `Resumen_Nacional` | Matriz de las 23 ciudades × indicadores clave + semáforo de precisión | 1 fila por ciudad, última fila = consolidado nacional |
| `Rankings_Comparados` | Las 5 tablas de ranking (FR-011) | 1 fila por ciudad × año × tipo de ranking |
| `Tenencia_23Ciudades` | Serie 2023-2026 de las 7 categorías de tenencia | 1 fila por ciudad × año |
| `Arriendos_23Ciudades` | Mediana/media/P25/P75 de arriendo | 1 fila por ciudad × año |
| `Carga_Financiera` | Distribución del ratio arriendo/ingreso, %>30%, %>50% | 1 fila por ciudad × año |
| `Ingresos_Brecha` | Ingreso mediano propietarios vs. arrendatarios | 1 fila por ciudad × año |
| `Deficit_Habitacional` | Placeholder Fase 2 | Todas las celdas de valor = `"ND — pendiente Fase 2 (ECV)"` |
| `Servicios_Publicos` | Cobertura de acueducto/alcantarillado/gas/energía/aseo | 1 fila por ciudad × año |
| `Muestra_y_FEX` | `n` y población expandida por ciudad y mes | 1 fila por ciudad × mes |
| `Precision_CV` | SE, IC95%, DEFF, CV, etiqueta por indicador | 1 fila por ciudad × año × indicador (espejo del CSV maestro) |
| `Diccionario_Fuentes` | Metadatos, variables DANE usadas, URLs de catálogo | 1 fila por variable/fuente |
| `Auditoria_10_10` | Veredictos de las 4 pruebas red-team | 1 fila por ciudad × año × tipo de prueba (espejo de Resultado de Auditoría en data-model.md) |

**Regla de consistencia (SC-007 de spec.md)**: el valor de un mismo `(ciudad, año, indicador)`
debe ser idéntico entre `Resumen_Nacional`, el CSV maestro y cualquier hoja específica que lo
repita — se generan todos a partir de la misma tabla larga en memoria, nunca recalculados por
separado.

## `metodologia_observatorio_nacional.md`

No tiene un esquema de columnas, pero sí una estructura de contenido obligatoria (contrato de
secciones, no de datos): fórmulas (KaTeX) de cada indicador, justificación de `FEX_C18`,
tratamiento del panel rotativo, limitación del bootstrap por `DIRECTORIO` (Principio VII) citada
explícitamente y no relegada a una nota al pie, y notas metodológicas por ciudad cuando aplique
(p. ej. una ciudad con `estado_geografico=ND` en algún año).

## `script_observatorio_nacional.py`

Contrato de ejecución (no de datos): debe aceptar un flag equivalente a `--desde` del orquestador
del piloto (`script_geih_ibague.py`) para retomar desde una etapa dada sin repetir la descarga, y
debe detenerse (no continuar silenciosamente) si una etapa termina en error, igual que ya hace el
orquestador piloto.

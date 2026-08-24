# Research — Motor Nacional del Observatorio de Vivienda (Fase 1)

No quedaron marcadores `NEEDS CLARIFICATION` en `spec.md` ni en el Technical Context de
`plan.md`: las decisiones de alcance y metodología ya se resolvieron antes de llegar a esta fase,
mediante una entrevista de diseño (`/grill-me`) cuyo resultado quedó registrado en
`.specify/memory/constitution.md`. Este documento consolida esas decisiones en el formato
Decision/Rationale/Alternatives, más una verificación puntual hecha directamente sobre los datos
ya existentes en el repositorio.

## Decisión 1 — Generalizar el pipeline existente en vez de reescribirlo

- **Decision**: parametrizar por ciudad los scripts ya construidos y auditados para Ibagué, en
  vez de crear un pipeline nuevo desde cero para las 23 ciudades.
- **Rationale**: los 42 archivos GEIH ya descargados son de alcance nacional (contienen las 23
  ciudades, no solo Ibagué); la lógica de limpieza e indicadores ya está auditada de punta a
  punta para una ciudad. Reescribir desperdiciaría esa validación y reintroduciría riesgo de
  error ya descartado.
- **Alternatives considered**: (a) reescritura completa siguiendo la numeración de loops del
  nuevo prompt maestro — descartada por costo/riesgo sin beneficio claro; (b) mantener dos
  pipelines paralelos (uno para Ibagué, otro nacional) — descartada porque duplica
  mantenimiento y contradice el Principio VIII de la constitución.

## Decisión 2 — Fuente de validación poblacional (Loop 2 / FR-002)

- **Decision**: usar las proyecciones oficiales de población y hogares del DANE con base en el
  CNPV 2018, obtenidas del portal principal `dane.gov.co` (no `microdatos.dane.gov.co`).
- **Rationale**: el prompt maestro original exige este oráculo externo con tolerancia ±5% pero no
  lo incluía en su propia lista de fuentes obligatorias — un vacío del plan, no una decisión ya
  tomada. Ir a buscar la fuente real (en vez de relajar el test o usar un sustituto informal)
  mantiene la validación externa independiente que le da defendibilidad al observatorio, con un
  costo de adquisición bajo (archivos agregados pequeños, no microdatos).
- **Alternatives considered**: (a) relajar el Loop 2 a una prueba de plausibilidad interna
  (consistencia mes a mes sin comparar contra censo) — descartada, pierde la validación externa;
  (b) usar cifras de "población total" de los boletines de mercado laboral GEIH como sustituto —
  descartada, es una fuente secundaria menos trazable que la proyección oficial directa.
- **Nota de ejecución**: la estructura exacta del archivo de proyecciones (formato, nivel de
  desagregación por municipio) todavía no se ha inspeccionado — es tarea de
  `02b_descarga_proyecciones_poblacion.py` (Fase de implementación), no de esta planeación.

## Decisión 3 — Método de varianza de diseño complejo (Loop 6 / FR-009, FR-010)

- **Decision**: bootstrap por conglomerado agrupado en `DIRECTORIO`, con DEFF calculado como
  `Var_bootstrap / Var_MAS_naive`, en vez de linearización de Taylor real.
- **Rationale**: los microdatos públicos de GEIH no incluyen UPM/segmento/estrato, por lo que
  Taylor linearization real es técnicamente inviable. El propio prompt maestro ofrece bootstrap
  por `DIRECTORIO` como alternativa explícita, y sí es viable porque esa variable existe en los
  microdatos públicos. Es estrictamente mejor que el error estándar aproximado tipo "sandwich"
  (sin ajuste por conglomerados) que ya usaba `stats_ponderadas.py` en el piloto.
- **Alternatives considered**: (a) mantener el método "sandwich" sin cambios — descartada, no
  cumple lo que pide el nuevo alcance ni mejora la subestimación de varianza ya documentada; (b)
  buscar acceso a las variables de diseño muestral restringidas del DANE — descartada para esta
  fase por requerir convenio institucional, sin garantía de acceso en un plazo razonable.
- **Limitación heredada, no resuelta por esta decisión**: `DIRECTORIO` identifica la vivienda, no
  el segmento/UPM real del diseño (~10 viviendas). El bootstrap por `DIRECTORIO` capta solo el
  conglomerado de hogares que comparten vivienda, no el conglomerado geográfico completo del
  diseño muestral — el CV real del DANE probablemente sea mayor al calculado aquí. Ver Principio
  VII de la constitución; el módulo `stats_bootstrap.py` debe documentar esto explícitamente.

## Decisión 4 — ECV diferida a Fase 2

- **Decision**: no descargar ni procesar la Encuesta de Calidad de Vida en esta fase; todo
  indicador de déficit habitacional cuantitativo/cualitativo y distribución por estrato queda
  "ND — pendiente Fase 2 (ECV)".
- **Rationale**: la ECV es una encuesta distinta (otro marco muestral, otra periodicidad, otro
  cuestionario) nunca antes tocada en este proyecto, y su tamaño de muestra anual podría no tener
  potencia estadística para las 23 ciudades individualmente (algunas capitales pequeñas caerían
  en n<30). Construir su sub-pipeline completo sin antes confirmar esa viabilidad arriesgaba
  trabajo desechable.
- **Alternatives considered**: (a) incluirla de una vez a plena escala asumiendo viabilidad —
  descartada, riesgo de trabajo desechable; (b) investigar primero su viabilidad y decidir
  después — descartada solo porque el usuario prefirió diferir directamente a una Fase 2
  explícita en vez de invertir tiempo en la investigación de viabilidad ahora.

## Decisión 5 — Secuencia de entregables (motor antes que narrativa)

- **Decision**: esta feature (001) entrega únicamente el motor de cálculo + auditoría (Excel,
  CSV, metodología, script). Las 23 fichas de ciudad, los rankings narrativos y los 10 guiones de
  video se especifican como una feature separada posterior, solo después de que el red team
  (Loop 9 / FR-012) apruebe la tabla nacional completa.
- **Rationale**: evita reescribir contenido narrativo si un hallazgo de auditoría obliga a
  corregir una cifra de última hora.
- **Alternatives considered**: (a) generar los 6 entregables en un solo paso — descartada, mismo
  riesgo de recorte descrito arriba; (b) priorizar aún más angosto (solo Excel+CSV+metodología en
  esta fase, script en otra) — descartada por el usuario, la separación motor/narrativa ya es
  suficiente granularidad.

## Verificación puntual — códigos de dominio geográfico de las 23 ciudades

El diccionario armonizado ya construido durante el piloto (`GEIH/diccionario_armonizado.csv`,
fila `AREA`) documenta, verificado contra el diccionario oficial DANE 2023, los 23 dominios
históricos de la GEIH — y un 24° dominio (`88 = San Andrés`) que **no** forma parte de la lista
de 23 ciudades de esta feature. Los 23 códigos listados en `spec.md`/la constitución coinciden
exactamente con los del diccionario armonizado:

`05 Medellín A.M., 08 Barranquilla A.M., 11 Bogotá, 13 Cartagena, 15 Tunja, 17 Manizales A.M.,
18 Florencia, 19 Popayán, 20 Valledupar, 23 Montería, 27 Quibdó, 41 Neiva, 44 Riohacha,
47 Santa Marta, 50 Villavicencio, 52 Pasto, 54 Cúcuta A.M., 63 Armenia, 66 Pereira A.M.,
68 Bucaramanga A.M., 70 Sincelejo, 73 Ibagué, 76 Cali A.M.`

Esto **no** exime de la validación empírica por año que exige FR-001 (el diccionario 2023 no
garantiza que el mismo código sea válido en 2024/2025/2026, y la nota del propio diccionario
armonizado advierte que el texto descriptivo de DANE no siempre se reescribe por año) — pero sí
significa que `config_ciudades.py` parte de una hipótesis ya verificada contra una fuente
primaria real, no de una suposición del prompt maestro. Ver `04_identificacion_ciudades.py` en
`plan.md`.

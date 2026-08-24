# Feature Specification: Motor Nacional del Observatorio de Vivienda — Fase 1 (23 Ciudades, GEIH + Pobreza)

**Feature Branch**: `001-observatorio-vivienda-nacional` (no hay rama git — este proyecto no usa control de versiones)

**Created**: 2026-08-22

**Status**: Draft

**Input**: User description: "Fase 1 del Observatorio de Vivienda de Ciudades Capitales de Colombia: generalizar el pipeline GEIH de vivienda ya construido, probado y auditado para Ibagué (una sola ciudad, AREA=73) a las 23 ciudades capitales / áreas metropolitanas de Colombia, para los períodos 2023, 2024, 2025 y 2026 parcial (Enero-Junio, según últimos meses publicados por el DANE). Incluye: identificación y validación geográfica de las 23 ciudades contra el diccionario oficial DANE de cada año; validación de población expandida contra proyecciones CNPV 2018; indicadores de tenencia, arriendo, esfuerzo financiero, vivienda propia y crédito, hacinamiento, servicios públicos e ingreso/pobreza por tenencia; varianza de diseño complejo vía bootstrap por conglomerado agrupado en DIRECTORIO con DEFF y clasificación de confiabilidad DANE; rankings nacionales comparados; y auditoría 'red team' generalizada. Explícitamente fuera de alcance: la Encuesta de Calidad de Vida (ECV) y todo indicador de déficit habitacional/estrato que dependa de ella (queda 'ND — pendiente Fase 2'), y las 23 fichas individuales de ciudad, guiones de video y rankings narrativos (fase posterior separada). Entregables: observatorio_vivienda_capitales_2023_2026.xlsx (12 hojas), .csv maestro en formato largo, metodologia_observatorio_nacional.md, y script_observatorio_nacional.py, reutilizando y generalizando el código ya auditado de la fase piloto de Ibagué en vez de reescribirlo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identificación y validación geográfica de las 23 ciudades (Priority: P1)

Como responsable del observatorio, quiero que cada una de las 23 ciudades capitales/áreas
metropolitanas tenga su código de dominio geográfico (AREA) verificado empíricamente contra el
diccionario oficial DANE de cada año — no asumido de memoria ni copiado de un prompt — para
poder confiar en que cualquier cifra posterior realmente corresponde a esa ciudad.

**Why this priority**: Es la base de todo lo demás — si el filtro geográfico de una ciudad está
mal, cada indicador calculado para esa ciudad es inválido sin importar cuán sofisticado sea el
cálculo posterior. La fase piloto (Ibagué) ya demostró que esta validación puede fallar de
formas no triviales.

**Independent Test**: Se puede probar generando únicamente la tabla de control geográfico (una
fila por ciudad y mes, con registros, hogares únicos, suma de FEX_C18, % de coincidencia contra
DPTO/CLASE, y validación contra la proyección poblacional DANE) — sin haber calculado todavía
ningún indicador de vivienda — y verificando que las 23 ciudades queden clasificadas como
válidas, ND, o con alerta.

**Acceptance Scenarios**:

1. **Given** los 42 archivos GEIH ya descargados y el diccionario oficial DANE de cada año,
   **When** se ejecuta la identificación geográfica para las 23 ciudades, **Then** cada
   ciudad-mes queda con su código de dominio confirmado (o marcada "ND" si no tiene dominio
   propio), con evidencia de cruce contra DPTO/CLASE y unicidad de hogar.
2. **Given** la suma ponderada (FEX_C18) de hogares expandidos de una ciudad, **When** se compara
   contra la proyección oficial de población/hogares del DANE (CNPV 2018) para esa ciudad y año,
   **Then** el sistema marca la ciudad como "dentro de tolerancia" (±5%) o "revisar filtro
   geográfico" si la diferencia excede el umbral.
3. **Given** una ciudad capital cuyo dominio GEIH no puede identificarse de forma inequívoca en
   el diccionario de un año dado, **When** se llega a esa etapa de la validación, **Then** esa
   ciudad-año se marca explícitamente "ND" en vez de forzarse con un código supuesto.

---

### User Story 2 - Indicadores núcleo de vivienda por ciudad y año (Priority: P2)

Como responsable del observatorio, quiero los indicadores de tenencia, arriendo, esfuerzo
financiero, vivienda propia/crédito, hacinamiento, servicios públicos e ingreso/pobreza
calculados de forma ponderada para cada una de las 23 ciudades y cada año (2023-2026 parcial),
para poder comparar el mercado de vivienda entre ciudades y en el tiempo.

**Why this priority**: Es el contenido analítico central del observatorio — sin esto no hay
producto, solo un andamiaje de validación. Depende de que la Historia 1 ya haya determinado qué
registros pertenecen a cada ciudad.

**Independent Test**: Se puede probar generando la tabla larga de indicadores para las 23
ciudades y verificando, por ejemplo, que las 7 categorías de tenencia sumen 100% (±0.1pp) por
ciudad-año, y que las medianas/percentiles de arriendo sean plausibles frente a los datos crudos
de esa ciudad.

**Acceptance Scenarios**:

1. **Given** los datos ya limpios de una ciudad y año, **When** se calcula la distribución de
   tenencia (P5090), **Then** las 7 categorías ponderadas suman 100% dentro de una tolerancia de
   ±0.1 puntos porcentuales.
2. **Given** los hogares en arriendo de una ciudad y año, **When** se calcula el canon mediano,
   promedio, P25 y P75, **Then** los resultados usan cuantiles ponderados y excluyen los códigos
   de no-respuesta (98/99) y valores fuera de rango.
3. **Given** el ingreso total del hogar y el arriendo pagado de un hogar arrendatario, **When**
   se calcula la razón arriendo/ingreso, **Then** el resultado se usa para clasificar sobrecarga
   financiera (>30%) y sobrecarga severa (>50%), y para la mediana ponderada de esa ciudad-año.
4. **Given** la base de Pobreza Monetaria DANE de un año, **When** se cruza con los hogares de
   vivienda vía directorio+secuencia_p, **Then** cada hogar de vivienda queda asociado (cuando
   exista match) a su condición oficial de pobreza, permitiendo calcular pobreza por tenencia.

---

### User Story 3 - Precisión estadística y varianza de diseño complejo (Priority: P3)

Como responsable del observatorio, quiero que cada indicador publicado incluya su error
estándar, intervalo de confianza, coeficiente de variación y una etiqueta de confiabilidad
calculados de forma consistente con el estándar del DANE, para poder distinguir qué cifras son
robustas y cuáles deben publicarse con advertencia o no publicarse.

**Why this priority**: Sin esto, el observatorio publicaría cifras sin indicar su margen de
error — inaceptable para un entregable defendible ante un estadístico o el propio DANE. Depende
de que ya existan los indicadores núcleo (Historia 2) sobre los cuales calcular la varianza.

**Independent Test**: Se puede probar tomando un indicador ya calculado en la Historia 2 (p. ej.
% de arriendo en una ciudad) y verificando que el bootstrap por conglomerado (agrupado en
DIRECTORIO) produce un error estándar, que el DEFF resultante es ≥1, y que la clasificación de
confiabilidad (n y CV) coincide con las reglas documentadas.

**Acceptance Scenarios**:

1. **Given** un indicador ponderado para una ciudad-año, **When** se remuestrean los DIRECTORIO
   con reemplazo y se recalcula el indicador en cada réplica, **Then** el error estándar y el
   intervalo de confianza al 95% se derivan de la distribución empírica de las réplicas.
2. **Given** el error estándar bootstrap y el error estándar teórico de muestreo aleatorio simple
   para el mismo indicador, **When** se calcula el DEFF, **Then** el resultado queda documentado
   junto a una nota explícita de que esta aproximación no sustituye la linearización de Taylor
   real (inviable sin variables de diseño muestral públicas).
3. **Given** el n muestral y el CV de un indicador, **When** se clasifica su confiabilidad,
   **Then** la etiqueta asignada (excelente/aceptable/precaución/no publicar) sigue exactamente
   los umbrales oficiales DANE.

---

### User Story 4 - Auditoría "red team" y entregables consolidados (Priority: P4)

Como responsable del observatorio, quiero que la tabla nacional completa pase un conjunto de
pruebas adversariales antes de empaquetarse en los entregables finales, para tener una garantía
explícita de que no se está publicando un error conocido.

**Why this priority**: Es el control de calidad final — depende de que ya existan los
indicadores (Historia 2) y su capa de precisión (Historia 3) para todas las ciudades, y es lo
que convierte los cálculos internos en un entregable publicable.

**Independent Test**: Se puede probar ejecutando el conjunto de pruebas de auditoría sobre la
tabla nacional ya consolidada y verificando que produce un veredicto explícito (aprobado / con
advertencia / no publicar) por cada celda, sin intervención manual.

**Acceptance Scenarios**:

1. **Given** la tabla nacional consolidada de las 23 ciudades, **When** se ejecuta la prueba de
   suma de tenencia, **Then** se reporta cualquier ciudad-año cuya suma se desvíe de 100% en más
   de ±0.1pp.
2. **Given** las variables monetarias de vivienda de las 23 ciudades, **When** se ejecuta la
   prueba de sensibilidad a outliers, **Then** se reporta el efecto de la winsorización al
   percentil 99 sobre las medianas/medias afectadas.
3. **Given** los valores de arriendo imputado y arriendo pagado ya calculados, **When** se
   ejecuta la prueba de consistencia, **Then** se confirma que ninguno se usó en el lugar del
   otro para ninguna ciudad.
4. **Given** el conjunto completo de indicadores con su n y CV, **When** se ejecuta la prueba de
   umbral de publicación, **Then** ninguna celda con n<30 o CV>25% aparece marcada como
   confiable en los entregables finales.
5. **Given** que las 4 pruebas anteriores pasan para las 23 ciudades, **When** se generan los
   entregables finales, **Then** se producen `observatorio_vivienda_capitales_2023_2026.xlsx`
   (12 hojas), `observatorio_vivienda_capitales_2023_2026.csv`, `metodologia_observatorio_nacional.md`
   y `script_observatorio_nacional.py`.

### Edge Cases

- ¿Qué pasa cuando una ciudad capital no tiene dominio geográfico propio en la GEIH de un año
  específico (queda agrupada en "resto urbano")? Esa ciudad-año se marca "ND", no se excluye
  silenciosamente ni se aproxima con otro dominio.
- ¿Qué pasa cuando el n muestral de un subgrupo (p. ej. solo arrendatarios) de una ciudad
  pequeña cae por debajo de 30 en un período específico? Ese indicador puntual se marca "no
  publicar", incluso si el resto de indicadores de esa misma ciudad sí son publicables.
- ¿Qué pasa si la fuente de proyecciones de población CNPV no tiene desagregación disponible
  para alguna de las 23 ciudades? Esa ciudad queda con la validación poblacional en "ND"
  documentado, sin bloquear el cálculo de sus demás indicadores.
- ¿Qué pasa si al verificar el catálogo DANE vigente aparecen más meses de 2026 publicados que
  los 6 asumidos (Ene-Jun)? Se actualiza el corte y la comparación pareada al nuevo rango real
  antes de calcular la comparabilidad temporal.
- ¿Qué pasa si una de las 23 ciudades resulta tener un hogar duplicado (misma llave
  directorio+secuencia_p+hogar) tras el filtro geográfico? La suma de FEX_C18 antes y después de
  deduplicar debe coincidir exactamente; cualquier diferencia bloquea el avance de esa
  ciudad-mes hasta resolverse.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE identificar, para cada una de las 23 ciudades capitales/áreas
  metropolitanas y cada año (2023-2026 parcial), el código de dominio geográfico correcto
  verificado empíricamente contra el diccionario oficial DANE de ese año.
- **FR-002**: El sistema DEBE validar la población expandida (suma de FEX_C18) de cada ciudad
  contra la proyección oficial de población/hogares del DANE (CNPV 2018), con tolerancia ±5%, y
  registrar el resultado de esa validación de forma trazable.
- **FR-003**: El sistema DEBE calcular, para cada ciudad y año, la distribución ponderada de
  tenencia de vivienda en sus 7 categorías oficiales, verificando que sumen 100% (±0.1pp).
- **FR-004**: El sistema DEBE calcular indicadores ponderados de mercado de arriendo (mediana,
  media, P25, P75) usando cuantiles ponderados, excluyendo códigos de no-respuesta y valores
  fuera de rango, y sin confundir arriendo pagado con arriendo imputado.
- **FR-005**: El sistema DEBE calcular el esfuerzo financiero de los hogares arrendatarios
  (razón arriendo/ingreso, % con sobrecarga >30%, % con sobrecarga severa >50%, brecha de
  ingreso propietarios vs. arrendatarios) para cada ciudad y año.
- **FR-006**: El sistema DEBE calcular indicadores de vivienda propia y crédito (valor comercial
  estimado, cuota hipotecaria, arriendo imputado) respetando el universo de aplicabilidad de
  cada variable según la categoría de tenencia.
- **FR-007**: El sistema DEBE calcular el hacinamiento (personas por cuarto para dormir) y la
  cobertura de servicios públicos por ciudad y año.
- **FR-008**: El sistema DEBE cruzar los hogares de vivienda con la base oficial de Pobreza
  Monetaria DANE para calcular pobreza monetaria por tenencia.
- **FR-009**: El sistema DEBE estimar error estándar e intervalo de confianza al 95% de cada
  indicador mediante bootstrap por conglomerado agrupado en el identificador de vivienda, y
  calcular el DEFF resultante frente a la varianza de muestreo aleatorio simple equivalente.
- **FR-010**: El sistema DEBE clasificar la confiabilidad de cada indicador (excelente/
  aceptable/precaución/no publicar) según los umbrales oficiales DANE de n muestral y
  coeficiente de variación, y DEBE evitar presentar como confiable cualquier indicador con n<30
  o CV>25%.
- **FR-011**: El sistema DEBE producir rankings nacionales comparados por año (inquilinato,
  costo de arriendo, estrés habitacional, desigualdad de ingreso propietario/inquilino,
  hacinamiento) ordenando las 23 ciudades.
- **FR-012**: El sistema DEBE ejecutar las 4 pruebas adversariales de auditoría (suma de
  tenencia, sensibilidad a outliers, consistencia arriendo pagado/imputado, umbral de
  publicación) sobre la tabla nacional completa antes de generar los entregables finales.
- **FR-013**: El sistema DEBE marcar explícitamente "ND — pendiente Fase 2 (ECV)" cualquier
  indicador de déficit habitacional cuantitativo/cualitativo o distribución por estrato, sin
  calcularlo ni aproximarlo en esta fase.
- **FR-014**: El sistema DEBE generar los 4 entregables de esta fase únicamente después de que
  la auditoría (FR-012) apruebe la tabla nacional completa.
- **FR-015**: El sistema DEBE reutilizar y generalizar (parametrizar por ciudad) la lógica de
  limpieza e indicadores ya auditada en la fase piloto de una sola ciudad, en vez de reescribirla
  desde cero.

### Key Entities

- **Ciudad**: una de las 23 ciudades capitales/áreas metropolitanas; atributos clave: nombre,
  código de dominio geográfico verificado por año, estado de validación poblacional (CNPV),
  estado general (ND/válida/con alerta).
- **Periodo**: año (2023/2024/2025/2026*) y, para el detalle mensual, mes; 2026 siempre rotulado
  como parcial.
- **Hogar**: unidad de observación de vivienda; atributos clave: llave única, categoría de
  tenencia, variables monetarias de vivienda, factor de expansión, condición de pobreza asociada.
- **Indicador**: una métrica calculada por ciudad-año; atributos clave: valor puntual, error
  estándar, intervalo de confianza, DEFF, n muestral, CV, etiqueta de confiabilidad.
- **Resultado de Auditoría**: veredicto de una prueba adversarial sobre una ciudad-año-indicador;
  atributos clave: tipo de prueba, resultado (aprobado/advertencia/rechazado), evidencia asociada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Las 23 ciudades quedan con su código de dominio geográfico verificado (o
  explícitamente marcadas "ND") para el 100% de los años 2023-2026 parcial.
- **SC-002**: El 100% de las ciudades-año con datos suficientes (n≥30) tiene su población
  expandida contrastada contra la proyección oficial DANE, con el resultado documentado y
  trazable a la fuente.
- **SC-003**: El 100% de las ciudades-año muestra una suma de tenencia de vivienda entre 99.9% y
  100.1%.
- **SC-004**: Cero indicadores en los entregables finales muestran una etiqueta de confiabilidad
  "alta" o "aceptable" cuando su n es menor a 30 o su CV es mayor a 25%.
- **SC-005**: El 100% de los indicadores de arriendo, esfuerzo financiero y crédito diferencian
  correctamente arriendo pagado de arriendo imputado, verificado por la prueba de consistencia
  de auditoría.
- **SC-006**: El pipeline completo (23 ciudades × 4 años) se ejecuta de principio a fin de forma
  reproducible a partir de un único script, sin intervención manual en los cálculos.
- **SC-007**: Los 4 entregables de esta fase quedan disponibles y consistentes entre sí (misma
  cifra reportada en el Excel, el CSV y la metodología para un mismo indicador ciudad-año).

## Assumptions

- Los 42 archivos GEIH mensuales (2023-2025 completos, 2026 Ene-Jun) y la base de Pobreza
  Monetaria 2023-2025 ya están descargados localmente y son de alcance nacional; no se requiere
  nueva descarga de GEIH en esta fase, salvo que al verificar el catálogo DANE aparezcan meses
  de 2026 más recientes que junio.
- La fuente de proyecciones de población/hogares (CNPV 2018) se obtiene del portal principal del
  DANE (distinto del portal de microdatos) y aún no está descargada; conseguirla forma parte del
  alcance de esta fase.
- La Encuesta de Calidad de Vida (ECV) está fuera de alcance de esta fase por decisión ya
  tomada; todo indicador que dependa de ella se marca "ND — pendiente Fase 2".
- La varianza de "diseño complejo" se aproxima mediante bootstrap por conglomerado, no mediante
  linearización de Taylor real, porque los microdatos públicos de la GEIH no incluyen variables
  de diseño muestral — limitación ya documentada en la constitución del proyecto.
- Las 23 fichas individuales de ciudad, los guiones de video y los rankings narrativos no forman
  parte de esta fase; se especificarán como una feature separada una vez que esta fase esté
  completa y auditada.
- El código de limpieza e indicadores ya construido y auditado para la fase piloto de una sola
  ciudad es reutilizable y generalizable a las 23 ciudades sin cambios de lógica, solo
  parametrización del filtro geográfico.

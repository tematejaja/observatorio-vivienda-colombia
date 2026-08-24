# Metodología — Observatorio de Vivienda de las Ciudades Capitales de Colombia
## Fase 1: GEIH + Pobreza Monetaria, 23 ciudades, 2023 – 2026*

**Fecha de elaboración:** 22 de agosto de 2026
**Cobertura temporal:** 2023, 2024, 2025 completos; 2026 parcial (enero–junio)
**Cobertura geográfica:** 23 ciudades capitales y áreas metropolitanas
**Fuentes:** exclusivamente DANE (microdatos.dane.gov.co y dane.gov.co)

> **Antes de citar cualquier cifra de este observatorio, lea la sección 8
> (Limitaciones declaradas).** Contiene tres restricciones que cambian cómo debe
> interpretarse el dato: la varianza de diseño complejo es una cota inferior, el
> déficit habitacional no está calculado en esta fase, y no existe medición de
> pobreza monetaria para 2026.

---

## 1. Alcance y qué NO incluye esta fase

Esta Fase 1 cubre únicamente los indicadores derivables de la **Gran Encuesta
Integrada de Hogares (GEIH)** y de la **base de Pobreza Monetaria y Desigualdad**
del DANE.

**Explícitamente fuera de alcance (no estimado, no aproximado, marcado `ND`):**

| Indicador | Estado | Razón |
|---|---|---|
| Déficit habitacional cuantitativo | `ND — pendiente Fase 2 (ECV)` | Requiere la Encuesta de Calidad de Vida |
| Déficit habitacional cualitativo | `ND — pendiente Fase 2 (ECV)` | Requiere la Encuesta de Calidad de Vida |
| Distribución por estrato socioeconómico | `ND — pendiente Fase 2 (ECV)` | Requiere la Encuesta de Calidad de Vida |
| Ingreso, carga financiera y pobreza 2026 | `ND` | El DANE no publica Pobreza Monetaria del año en curso |

Estas celdas existen en el esquema del CSV y del Excel, pero **nunca contienen un
número estimado**. No se extrapolaron desde años anteriores ni desde otras ciudades.

---

## 2. Universo de datos y volumen procesado

- **42 archivos mensuales** de GEIH (12 + 12 + 12 en 2023–2025; 6 en 2026).
- **682.054 registros de hogar** correspondientes a las 23 ciudades, extraídos del
  módulo *"Datos del hogar y la vivienda"*.
- **966 celdas ciudad-mes** (23 × 42), todas con dominio geográfico confirmado.
- **3 años** de la base de Pobreza Monetaria (2023, 2024, 2025).

---

## 3. Identificación geográfica de las 23 ciudades (Loop 2)

El dominio de ciudad de la GEIH está en la variable `AREA`. **Ningún código se
asumió**: cada uno se verificó empíricamente en los 42 archivos, comprobando en
cada ciudad-mes que:

1. el código exista realmente en ese archivo;
2. los hogares pertenezcan al departamento esperado (cruce `AREA` × `DPTO`);
3. correspondan a cabecera municipal (`CLASE = 1`);
4. la llave de hogar `DIRECTORIO + SECUENCIA_P + HOGAR` sea única;
5. la suma de `FEX_C18` **no cambie** al deduplicar hogares.

**Resultado: 966 de 966 celdas ciudad-mes en estado `VÁLIDO`**, sin duplicados y
con 100 % de coincidencia en los cruces de verificación. Ninguna ciudad quedó `ND`
por falta de dominio propio.

| Ciudad | AREA | Ciudad | AREA | Ciudad | AREA |
|---|---|---|---|---|---|
| Bogotá D.C. | 11 | Cartagena | 13 | Sincelejo | 70 |
| Medellín A.M. | 05 | Neiva | 41 | Valledupar | 20 |
| Cali A.M. | 76 | Armenia | 63 | Popayán | 19 |
| Barranquilla A.M. | 08 | Santa Marta | 47 | Tunja | 15 |
| Bucaramanga A.M. | 68 | Pasto | 52 | Riohacha | 44 |
| Manizales A.M. | 17 | Villavicencio | 50 | Florencia | 18 |
| Pereira A.M. | 66 | Montería | 23 | Quibdó | 27 |
| Cúcuta A.M. | 54 | Ibagué | 73 | | |

El dominio `88` (San Andrés) existe en la GEIH pero **no** forma parte de las 23
capitales de este observatorio; su exclusión es deliberada.

### 3.1 Composición de las áreas metropolitanas

Tomada de la **Ficha Metodológica GEIH V11 (DSO-GEIH-FME-001, 14/jun/2023)**:
Medellín incluye el Valle de Aburrá (Barbosa, Bello, Caldas, Copacabana, Envigado,
Girardota, Itagüí, La Estrella, Sabaneta); Cali incluye Yumbo; Barranquilla incluye
Soledad; Bucaramanga incluye Floridablanca, Girón y Piedecuesta; Manizales incluye
Villamaría; Pereira incluye Dosquebradas y La Virginia; Cúcuta incluye Villa del
Rosario, Puerto Santander, Los Patios y El Zulia.

Esta composición fue **validada empíricamente**: usando el dominio metropolitano
completo el desvío poblacional queda dentro de ±3,5 %, mientras que usando solo el
municipio núcleo el desvío sería de +60 % a +107 %. La coincidencia confirma que la
composición documentada es la correcta.

---

## 4. Validación poblacional contra el Censo (Loop 2, test de parada)

**Hallazgo previo, que cambió el diseño de esta validación:** el DANE **no publica
proyecciones de hogares desagregadas por municipio**; la serie municipal disponible
es de *población* por área. La validación se hace, por tanto, contra personas:

$$\text{Personas expandidas}_{c,t} = \frac{1}{M_t}\sum_{h \in c,t} FEX\_C18_h \times P6008_h$$

contrastadas contra la población proyectada en **cabecera municipal** del archivo
oficial `PPED-AreaMun-2018-2042_VP.xlsx` (proyecciones DANE con base en el CNPV
2018), con tolerancia de ±5 %.

**Resultado: 67 de 92 celdas ciudad-año dentro de tolerancia; 25 en `REVISAR`.**

Los 25 desvíos **no** indican un filtro geográfico erróneo — ese cruce dio 100 % en
las 966 celdas. El patrón es una **deriva creciente en el tiempo** (por ejemplo
Montería: −7,2 % en 2023 → −11,5 % en 2026), consistente con que los factores
`FEX_C18` de la GEIH fueron calibrados contra una versión anterior de las
proyecciones, mientras que el archivo usado aquí es la actualización post-pandemia
(publicada el 8 de agosto de 2025). Es una divergencia entre dos productos del DANE,
no un error de este pipeline, y se documenta en vez de ocultarse.

---

## 5. Limpieza de variables (Loop 3)

Se conservan sin cambios las reglas ya auditadas en la fase piloto:

| Variable | Concepto | Universo de aplicabilidad |
|---|---|---|
| `P5140` | Canon de arriendo **efectivamente pagado** | Solo `P5090 = 3` |
| `P5130` | Arriendo **imputado** (estimado por el hogar) | Solo `P5090 ≠ 3` |
| `P5110` | Valor comercial estimado de la vivienda | Solo `P5090 ∈ {1, 2}` |
| `P5100` | Cuota mensual de crédito hipotecario | Solo `P5090 = 2` |

- Los códigos **98** ("no sabe") y **99** ("no informa") se convierten a `NA`, nunca
  se tratan como valores monetarios. Confirmado contra la regla de validación oficial
  del diccionario DANE 2026.
- Fuera de su universo de aplicabilidad, un blanco es un **no-aplica estructural**,
  no un dato perdido.
- Los valores extremos se **marcan pero no se eliminan**, mediante un *fence* de
  Tukey (k = 3, "far outlier") sobre escala log₁₀.

**Diferencia deliberada frente al piloto:** los *fences* se calculan **por ciudad**,
no sobre el conjunto nacional. El nivel de precios entre Bogotá y Quibdó difiere en
casi un orden de magnitud; un umbral único marcaría como extremos valores normales en
la ciudad más cara y dejaría pasar errores de digitación en la más barata.

---

## 6. Ponderación y estimadores (Loop 5)

Todos los indicadores son **ponderados**; ninguna cifra se calcula como $n/n$ simple.

### 6.1 Peso de periodo — corrección crítica

Cada mes de la GEIH trae `FEX_C18` ya expandido a la población **total de ese mes**.
Sumarlo tal cual al agrupar 12 meses multiplicaría la población por 12. Por eso el
peso de periodo es:

$$w_h = \frac{FEX\_C18_h}{M_t}, \qquad M_t = \text{número de meses del periodo } t$$

En cambio, `fex_c` de la base de Pobreza Monetaria **ya viene anualizado por el DANE**
y **no** se vuelve a dividir. Confundir ambas convenciones es un error de un orden de
magnitud.

### 6.2 Estimadores

- **Proporción ponderada:** $\hat{p} = \dfrac{\sum_h w_h \cdot \mathbb{1}[y_h]}{\sum_h w_h} \times 100$
- **Media ponderada:** $\bar{y}_w = \dfrac{\sum_h w_h y_h}{\sum_h w_h}$
- **Cuantiles ponderados** por método del punto medio, que evita el sesgo en los
  extremos de la distribución.
- **Carga financiera:** $\text{Ratio}_h = \dfrac{P5140_h}{ingtotug_h} \times 100$,
  usando `ingtotug` (ingreso total de la unidad de gasto) y **no** `ingtotarr`, porque
  este último imputa un arriendo no monetario solo a propietarios y usufructuarios, lo
  que sesgaría al alza la comparación entre propietarios y arrendatarios.

### 6.3 Cruce con Pobreza Monetaria

El emparejamiento se hace por `directorio + secuencia_p + mes`. **Regla de calidad:**
si la tasa de coincidencia es inferior al 70 %, el indicador se marca `ND` en lugar de
publicarse con un sesgo de selección no caracterizado. En esta fase, **las 69 celdas
ciudad-año (23 × 3 años) superaron el umbral**.

---

## 7. Precisión estadística (Loop 6)

### 7.1 Método

Error estándar e intervalos de confianza al 95 % mediante **bootstrap por
conglomerado**, remuestreando con reemplazo los `DIRECTORIO` completos (300
réplicas, semilla fija 20260822 para reproducibilidad). Los IC se obtienen por
**percentiles empíricos** de las réplicas, no por aproximación normal.

$$DEFF = \frac{\widehat{Var}_{\text{bootstrap}}}{\widehat{Var}_{\text{MAS}}}, \qquad CV = \frac{SE}{\hat{\theta}} \times 100$$

### 7.2 Semáforo oficial DANE

| Etiqueta | Criterio |
|---|---|
| 🟢 EXCELENTE | CV ≤ 5 % y n ≥ 100 |
| 🟢 ACEPTABLE | 5 % < CV ≤ 15 % y n ≥ 100 |
| 🟡 PRECAUCIÓN | 15 % < CV ≤ 25 % o 30 ≤ n < 100 |
| 🔴 NO PUBLICAR | CV > 25 % o n < 30 |

**Resultado sobre 2.024 estimaciones:** 1.069 excelentes (52,8 %), 606 aceptables
(29,9 %), 142 en precaución (7,0 %) y 207 marcadas no publicar (10,2 %).
DEFF mediano = 1,172 (p90 = 1,771); CV mediano = 4,17 %.

Las estimaciones marcadas **NO PUBLICAR** son mayoritariamente eventos raros —por
ejemplo, el porcentaje de hogares sin energía eléctrica en Bogotá, donde la cobertura
es prácticamente universal y el CV se dispara— y **no reciben posición en los
rankings**.

---

## 8. Limitaciones declaradas

### 8.1 La varianza de diseño complejo es una cota inferior

Los microdatos **públicos** de la GEIH no incluyen las variables de diseño muestral
(UPM/segmento, estrato). Por lo tanto:

- **La linealización de Taylor es inviable** con estos datos y **no se implementó**.
  Ninguna cifra de este observatorio debe presentarse como si lo fuera.
- El único identificador de agrupamiento disponible es `DIRECTORIO`, que identifica la
  **vivienda**, no el segmento geográfico (~10 viviendas contiguas) del diseño real.
- En consecuencia, **el error estándar reportado es una cota inferior del error real**,
  y el CV verdadero del DANE es probablemente mayor. El semáforo debe leerse como una
  señal conservadora, no como una réplica de la precisión interna del DANE.

Evidencia de la magnitud del problema: en Ibagué 2025 hay 6.711 hogares en 6.691
conglomerados `DIRECTORIO` — casi un hogar por vivienda, por lo que el bootstrap
apenas puede capturar conglomeración. El DEFF resultante (1,18) es, casi con certeza,
menor que el real.

Aun así, es **estrictamente mejor** que ignorar la conglomeración: una verificación
automatizada comprueba que el error estándar del bootstrap nunca sea inferior al del
método sin conglomerados.

### 8.2 DEFF atípico en medianas con redondeo

25 estimaciones presentan DEFF > 10, concentradas en *"Arriendo imputado — mediana"*.
La causa está identificada: **heaping** (los hogares reportan cifras redondas como
400.000 o 500.000). La mediana ponderada salta discretamente entre esos valores y su
varianza bootstrap se infla frente al muestreo aleatorio simple. El CV de esas
estimaciones sigue siendo bajo (~6 %), por lo que la estimación puntual es válida: el
DEFF **no** debe interpretarse ahí como pérdida real de precisión.

### 8.3 Panel rotativo

La GEIH usa un esquema de panel rotativo que puede repetir hogares entre meses.
Verificado: **0 de 92 celdas ciudad-año superan el 5 %** de hogares repetidos, por lo
que agrupar los meses de un año no introduce correlación material por esta vía.

---

## 9. Comparabilidad temporal 2026 (Loop 7)

**2026 es un periodo parcial y se rotula siempre `2026*` (enero–junio).** El corte se
verificó contra el catálogo DANE vigente el 22 de agosto de 2026: solo hay seis meses
publicados.

Comparar 2026 parcial contra 2025 completo mezcla el cambio real con el componente
estacional. Por eso toda variación interanual se calcula de forma **pareada**,
restringiendo 2025 a los mismos meses de 2026.

**El sesgo es material y medible.** Para el canon mediano de arriendo, promediando las
23 ciudades:

| Comparación | Variación |
|---|---|
| Ingenua (2026 Ene–Jun vs 2025 completo) | **+10,26 %** ← no publicable |
| Homogénea (2026 Ene–Jun vs 2025 Ene–Jun) | **+12,47 %** ← válida |
| **Sesgo estacional** | **−2,21 pp** |

Usar la comparación ingenua subestimaría el encarecimiento del arriendo en más de dos
puntos porcentuales.

---

## 10. Auditoría adversarial (Loop 9)

Siete pruebas ejecutadas sobre la tabla nacional completa **antes** de generar los
entregables. Un solo `RECHAZADO` bloquea la publicación.

| Prueba | Resultado |
|---|---|
| Suma de tenencia = 100 % ± 0,1 pp | ✅ 92/92 aprobadas |
| Sensibilidad a outliers (winsorización P99) | ✅ 184/184 aprobadas |
| Consistencia `P5130` vs `P5140` | ✅ 27/27 aprobadas |
| Umbral de publicación (n < 30 o CV > 25 %) | ✅ 0 violaciones |
| Panel rotativo | ✅ 92/92 aprobadas |
| Consistencia `P5090` cruzada entre bases DANE | ✅ 69/69 aprobadas |
| DEFF atípico | ⚠️ 25 advertencias (explicadas en 8.2) |

**Veredicto: 465 aprobados, 25 advertencias, 0 rechazos.**

Sobre la prueba de consistencia `P5130`/`P5140`: en varias ciudades ambas medianas
coinciden en la misma cifra redonda. Esto **no** es confusión de variables — la
verificación estructural confirma que **cero** hogares arrendatarios tienen arriendo
imputado y **cero** no arrendatarios tienen arriendo pagado. Se distingue el caso
benigno (coincide la mediana por redondeo, difieren los promedios) del caso grave
(coincidirían mediana *y* promedio), que no ocurrió en ninguna ciudad.

---

## 11. Reproducibilidad

Todo el pipeline corre con un solo comando y sin intervención manual:

```bash
python script_observatorio_nacional.py
```

Los resultados son deterministas: el bootstrap usa semilla fija. La auditoría es una
etapa **bloqueante** previa a la generación de entregables.

**Control de regresión:** Ibagué, la ciudad del piloto ya auditado, se recalcula
dentro del pipeline de las 23 ciudades y debe reproducir exactamente sus resultados
previos. Verificado: 23.467 registros idénticos, 128 indicadores sin una sola
diferencia, y valores limpios y marcas de outlier idénticos en las cuatro variables
monetarias.

---

## 12. Notas por ciudad

- **Cali A.M.:** el archivo oficial de proyecciones lista el municipio 76001 como
  "Cali", no "Santiago de Cali". Resolverlo mal produce un desvío absurdo (+2.306 %);
  el pipeline incluye una salvaguarda que marca `ND` en vez de comparar parcialmente.
- **Montería, Valledupar, Sincelejo, Neiva, Quibdó:** son las ciudades con mayor
  deriva poblacional frente a las proyecciones actualizadas (ver sección 4). Sus
  indicadores de *estructura* (porcentajes, medianas) no se ven afectados; la cautela
  aplica a los *niveles* de población expandida.
- **Ciudades con área metropolitana:** los indicadores corresponden al dominio
  metropolitano completo, no al municipio núcleo. Compararlos con cifras municipales
  de otra fuente sería incorrecto.

---

## 13. Anexo — Fuentes oficiales

| Fuente | Catálogo | Cobertura |
|---|---|---|
| GEIH 2023 | ANDA 782 | 12 meses |
| GEIH 2024 | ANDA 819 | 12 meses |
| GEIH 2025 | ANDA 853 | 12 meses |
| GEIH 2026 | ANDA 900 | Enero–junio (verificado) |
| Pobreza Monetaria 2023 | ANDA 835 | Anual |
| Pobreza Monetaria 2024 | ANDA 874 | Anual |
| Pobreza Monetaria 2025 | ANDA 908 | Anual |
| Proyecciones de población | CNPV 2018 — `PPED-AreaMun-2018-2042_VP.xlsx` | 2018–2042 |
| Ficha Metodológica GEIH | DSO-GEIH-FME-001 V11 | 14/jun/2023 |

Todas descargadas de dominios oficiales del DANE (`microdatos.dane.gov.co` y
`www.dane.gov.co`). No se usó ninguna fuente secundaria.

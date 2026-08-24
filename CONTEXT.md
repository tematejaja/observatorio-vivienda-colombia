# Observatorio de Vivienda

Plataforma que expone los indicadores de vivienda de las 23 ciudades capitales de
Colombia — calculados por el pipeline auditado de la Fase 1 a partir de microdatos
DANE — a través de una interfaz interactiva construida en Streamlit.

## Language

**Ficha**:
El perfil de una ciudad: el conjunto curado de indicadores y narrativa que la describe
(tenencia, arriendo, esfuerzo financiero, hacinamiento, servicios, ingreso/pobreza),
independiente de cómo se presente.
_Avoid_: "reporte", "perfil de ciudad"

**Ficha Markdown**:
La renderización estática de una Ficha como archivo `.md` en `fichas_ciudades/`, con el
formato de publicación (tachado, emojis de confiabilidad) incrustado directamente en el
texto. Es un entregable de distribución offline — **no** es la fuente de datos del
backend; se genera a partir de él.
_Avoid_: "la ficha" a secas cuando el contexto es ambiguo entre el archivo y el concepto

**Indicador**:
Una estimación puntual de una métrica de vivienda para una Ciudad y un Periodo (p. ej.
"canon mediano de arriendo, Ibagué, 2025"). Vive como fila en la tabla maestra; el
backend lo consume como dato de pandas, sin envolverlo en una clase propia.
_Avoid_: "métrica", "dato" a secas

**Nota Metodológica**:
Una advertencia textual asociada a uno o más Indicadores, que señala una limitación o
cuidado necesario al interpretarlos — confiabilidad estadística baja, desvío frente a la
proyección poblacional CNPV, comparación de un periodo parcial, DEFF atípico, ciudad con
área metropolitana completa, etc. **No oculta ni reemplaza el valor del Indicador**: lo
acompaña. Reemplaza al gate binario de "publicable/disponible" — todo dato se muestra,
las Notas Metodológicas cargan la responsabilidad de advertir.
_Avoid_: "advertencia" a secas, "flag", "publicable" / "disponible" como categoría de dato

**Ranking**:
Una de las 5 tablas fijas del catálogo (FR-011) que ordena las 23 ciudades de mayor a
menor según un único Indicador, para un año dado: inquilinato, costo de arriendo, estrés
habitacional, desigualdad de ingreso propietario/inquilino, hacinamiento. Siempre las 23
ciudades — el conjunto no lo elige quien consulta, a diferencia del Comparador.
_Avoid_: "tabla de posiciones", "leaderboard"

**Comparador**:
Vista del frontend donde quien consulta elige libremente un subconjunto de ciudades y de
Indicadores para verlos lado a lado — a diferencia del Ranking, ni el conjunto de
ciudades ni el de indicadores es fijo.
_Avoid_: usar "Ranking" y "Comparador" como sinónimos

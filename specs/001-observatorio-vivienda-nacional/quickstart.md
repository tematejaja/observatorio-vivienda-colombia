# Quickstart — Validación de la Fase 1 (23 Ciudades)

Guía para comprobar que la feature funciona de punta a punta. No repite los esquemas
(ver [contracts/entregables_schema.md](./contracts/entregables_schema.md)) ni las entidades
(ver [data-model.md](./data-model.md)) — solo los pasos para ejecutar y verificar.

> Los nombres de script de este documento corresponden a la implementación real.
> Los scripts del piloto de Ibagué (`04_identificacion_ibague.py`, `05_limpieza.py`,
> `07_indicadores_principales.py`, …) se conservan **intactos**: sirven de referencia
> histórica y de base de comparación para el control de regresión.

## Prerrequisitos

- Python 3.11+ con `pandas`, `numpy`, `openpyxl`, `requests` (`statsmodels` no es
  necesario en el camino nacional).
- Los 42 archivos GEIH mensuales y `GEIH/pobreza/{2023,2024,2025}/` ya presentes en disco.
- Conexión a internet solo para la fuente nueva de proyecciones CNPV (~4 MB).

## Camino corto: todo de una vez

```bash
python script_observatorio_nacional.py
```

Ejecuta las 13 etapas en orden y **se detiene sin generar entregables** si la auditoría
red team reporta algún `RECHAZADO` (FR-014). Para retomar desde una etapa concreta:

```bash
python script_observatorio_nacional.py --desde 13
```

Para ver las etapas disponibles: `python script_observatorio_nacional.py --listar`

## Paso 1 — Validación geográfica y poblacional (User Story 1)

```bash
python scripts/04_identificacion_ciudades.py
```

**Esperado**: `GEIH/control_geografico_23_ciudades.csv` con 966 filas (23 ciudades × 42
meses). Ninguna ciudad debe faltar: las que no tuvieran dominio propio aparecerían
explícitamente con estado `ND`, no ausentes.
*Resultado obtenido: 966/966 en `VÁLIDO`.*

```bash
python scripts/02b_descarga_proyecciones_poblacion.py
python scripts/06_validacion_poblacion_cnpv.py
```

**Esperado**: cada ciudad-año clasificada `DENTRO_TOLERANCIA`, `REVISAR` o `ND` frente a
la proyección CNPV (±5 %).
*Resultado obtenido: 67 dentro de tolerancia, 25 en `REVISAR` por deriva de calibración
de `FEX_C18` (explicado en la metodología, sección 4).*

## Paso 2 — Indicadores núcleo (User Story 2)

```bash
python scripts/05_limpieza_nacional.py
python scripts/07_indicadores_nacional.py
python scripts/08_ingresos_pobreza_nacional.py
python scripts/11_validacion_temporal_nacional.py
python scripts/13_tabla_final_nacional.py
```

**Verificación mínima**: las 7 categorías de tenencia suman 100 % ± 0,1 pp en cada
ciudad-año. `07_indicadores_nacional.py` lo comprueba e imprime al final.
*Resultado obtenido: 92/92 celdas correctas.*

## Paso 3 — Precisión estadística (User Story 3)

```bash
python scripts/stats_bootstrap.py --smoke-test
```

**Esperado**: el SE del bootstrap por conglomerado **no** debe ser menor que el del método
"sandwich" del piloto — un SE menor indicaría un bug, porque ignorar la conglomeración no
puede producir más varianza que tenerla en cuenta.
*Resultado obtenido: 0,6626 vs 0,6449 pp → PASA; DEFF = 1,182.*

```bash
python scripts/17_precision_nacional.py
```

*Resultado obtenido: 2.024 estimaciones con SE, IC95 %, DEFF, CV y semáforo DANE (~3 min).*

## Paso 4 — Auditoría "red team" (User Story 4)

```bash
python script_auditoria_nacional.py
```

**Esperado**: cero `RECHAZADO`. Si aparece alguno, el pipeline no debe generar entregables
hasta corregirlo.
*Resultado obtenido: 465 aprobados, 25 advertencias (DEFF por heaping, explicado), 0 rechazos.*

## Paso 5 — Entregables

```bash
python scripts/15_rankings_nacionales.py
python scripts/22_generar_excel_nacional.py
```

**Esperado**: los 4 archivos de `contracts/entregables_schema.md` en `output/`, y la misma
cifra para un `(ciudad, año, indicador)` en `Resumen_Nacional`, el CSV maestro y
`Precision_CV` (SC-007).

## Controles finales

```bash
python scripts/27_regresion_y_consistencia.py
```

Corre juntos el **control de regresión de Ibagué** (debe reproducir exactamente los
resultados del piloto ya auditado) y la **verificación de consistencia SC-007**.
*Resultado obtenido: 23.467 registros idénticos, 162 indicadores sin diferencias,
15 celdas cruzadas consistentes → ambos controles pasan.*

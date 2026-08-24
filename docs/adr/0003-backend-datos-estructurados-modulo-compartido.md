---
status: accepted
---

# El backend expone datos estructurados; la Ficha Markdown deja de ser fuente de nadie

La app de Streamlit no reutiliza el Markdown ya renderizado de las Fichas
(`fichas_ciudades/ficha_*.md`) como fuente de datos — leer ese formato acoplaría la app
a un detalle de presentación (tachado, emojis) pensado para distribución offline, en vez
de al dato real. En su lugar, se extrae la lógica de acceso a datos ya escrita en la
clase `Datos` de `scripts/30_generar_fichas_ciudades.py` (lectura del CSV maestro,
rankings, validación poblacional, control geográfico, auditoría) a un módulo
compartido del que dependen **ambos** consumidores: el generador de Fichas Markdown
(offline) y el backend de Streamlit (online). El módulo expone `valor` y
`etiqueta_confiabilidad` como campos separados; cada consumidor decide cómo pintarlos.

## Considered Options

- **Parsear el Markdown ya renderizado** (extraer `~~...~~` y emojis con regex):
  descartada — frágil, y no permite usar los estilos nativos de Streamlit.
- **Duplicar la lógica de lectura** (un camino para las fichas, otro para la app):
  descartada — viola el principio ya establecido de reutilizar código auditado en vez
  de mantener dos copias que puedan divergir (ver Principio VIII de la constitución de
  la Fase 1).

## Consequences

- `scripts/30_generar_fichas_ciudades.py` deja su clase `Datos` propia y pasa a importar
  el módulo compartido.
- El módulo compartido se vuelve el único punto de acceso a
  `output/observatorio_vivienda_capitales_2023_2026.csv` y a los CSV intermedios de
  `GEIH/procesado_nacional/`. Un cambio futuro en el esquema (`contracts/entregables_schema.md`)
  se refleja una sola vez, no en dos lugares.

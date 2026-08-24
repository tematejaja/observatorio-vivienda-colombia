---
status: accepted
---

# Backend del observatorio: archivos planos, sin base de datos

El observatorio en Streamlit necesita servir el CSV maestro (4.232 filas, 877 KB), los
libros Excel nacional y de auditoría, y las 23 fichas Markdown ya generados por la Fase 1
del pipeline. Se decidió que el backend lea estos archivos planos directamente con
pandas, sin introducir SQLite ni DuckDB, porque el CSV maestro carga en 0,1s y ocupa
2,7 MB en RAM — muy por debajo del punto donde una base de datos aportaría algo que
pandas en memoria no dé ya, incluso considerando el crecimiento previsible (más meses de
2026, la Fase 2 con ECV, años futuros).

## Considered Options

- **SQLite** (stdlib, sin dependencia nueva): descartada por ahora — no hay necesidad
  real de consultas SQL ad-hoc ni de un dataset que exceda cómodamente la memoria.
- **DuckDB**: ni siquiera está instalado en el entorno; se descartó sin evaluarla más a
  fondo dado el tamaño real de los datos.

Si el dataset creciera a decenas de MB o se necesitaran filtros/joins dinámicos
complejos, esta decisión debería revisarse.

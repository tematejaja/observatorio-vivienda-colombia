# Observatorio Nacional de Vivienda

App en Streamlit que expone los indicadores de vivienda de las 23 ciudades capitales y áreas
metropolitanas de Colombia — calculados a partir de microdatos DANE (GEIH y Pobreza Monetaria y
Desigualdad, 2023–2026\*) por un pipeline auditado (465 controles red-team aprobados, 0
rechazados).

## Vistas

- **Inicio** — tabla de las 23 ciudades × indicadores clave.
- **Ficha de ciudad** — perfil completo de una ciudad (tenencia, arriendo, esfuerzo financiero,
  vivienda propia, hacinamiento, servicios, ingreso/pobreza).
- **Rankings** — las 23 ciudades ordenadas en 5 indicadores nacionales comparados.
- **Comparador** — 2 a 6 ciudades elegidas libremente, evolución 2023–2026\* de un indicador.
- **Metodología** — resumen del cálculo + descarga de los entregables (CSV maestro, Excel
  nacional, Excel de auditoría, metodología completa).

## Diseño

El diseño (glosario de dominio + decisiones de arquitectura) está documentado en
[`CONTEXT.md`](CONTEXT.md) y en [`docs/adr/`](docs/adr/) — son la fuente de verdad, no un resumen
aparte.

Este repositorio contiene solo el código y los datos ya agregados que la app necesita para
correr. Los microdatos crudos DANE y los intermedios a grano de hogar del pipeline completo no se
versionan aquí (ver `.gitignore`).

## Correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

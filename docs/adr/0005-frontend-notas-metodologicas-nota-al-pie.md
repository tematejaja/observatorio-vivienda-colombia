---
status: accepted
---

# Notas Metodológicas en el frontend: nota al pie por vista, sin marca inline en la celda

Las vistas interactivas de Streamlit (Ficha, Ranking, Comparador) no decoran el valor de un
Indicador con color, emoji o una columna de confiabilidad aparte — la cifra se muestra
exactamente como llega del CSV maestro (consistente con ADR-0004: el valor nunca se oculta, se
tacha ni se reemplaza). Toda Nota Metodológica que le aplique — confiabilidad n/CV, deriva
poblacional CNPV, periodo parcial, DEFF atípico, área metropolitana completa, etc. — se
consolida en una única nota al pie por vista completa, no una por cada tabla individual dentro
de ella, siguiendo el mismo patrón ya validado en la sección 8 ("Calidad del dato") de las
fichas Markdown.

## Considered Options

- **Marca inline (color/emoji) junto al valor**: descartada para la interfaz interactiva —
  es el recurso que usan las fichas Markdown estáticas para compensar la falta de
  interactividad, pero se decidió explícitamente en contra aquí.
- **Tooltip por valor** (`help=` de `st.metric`): descartada — no existe por celda en
  `st.dataframe`/tablas grandes, y deja la advertencia menos visible de un vistazo.
- **Columna "Confiabilidad" aparte en cada tabla**: descartada — duplica el ancho de cada
  tabla y se aleja del patrón visual ya usado en las fichas.
- **Nota al pie por tabla individual** (en vez de por vista completa): descartada — fragmenta
  la advertencia en vez de darle una sola lectura consolidada.

## Consequences

- El módulo compartido (`scripts/datos_observatorio.py`, ver ADR-0003) debe poder devolver,
  para el conjunto de Indicadores mostrados en una vista completa, la lista consolidada de
  Notas Metodológicas que les aplican — no solo consultarlas Indicador por Indicador.
- Si en el futuro se necesita destacar una cifra puntual dentro de una tabla larga sin obligar
  a leer toda la nota al pie, esta decisión debe revisarse.

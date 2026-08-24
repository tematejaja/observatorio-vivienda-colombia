---
status: accepted
---

# El backend trabaja directo sobre pandas; las advertencias van en Notas Metodológicas, no en un gate de "publicable"

El módulo compartido no envuelve los datos en una clase intermedia (dataclass/NamedTuple):
las funciones devuelven objetos nativos de pandas (Series, DataFrame, escalares),
consistente con el resto del pipeline — ningún script de la Fase 1 usa una clase de
datos propia para esto. Tampoco se introduce un campo booleano "publicable"/"disponible".

En vez de eso, cualquier limitación relevante para un Indicador — la etiqueta de
confiabilidad DANE (n/CV), un desvío frente a la proyección poblacional CNPV, un DEFF
atípico por heaping, que la ciudad sea un área metropolitana completa, que el periodo
sea parcial — se resuelve mediante un mecanismo único de **Notas Metodológicas**: una
función que, dado un Indicador, devuelve la lista de advertencias textuales que le
aplican. La interfaz decide cómo mostrarlas (marcador + texto al pie); el valor del dato
nunca se oculta, se tacha ni se reemplaza.

**Alcance interpretado:** el mecanismo cubre TODO tipo de advertencia metodológica, no
solo el criterio de confiabilidad n/CV. Es la lectura más consistente con lo ya
documentado en `metodologia_observatorio_nacional.md` (sección 8), donde ya conviven
varios tipos de limitación tratados como igual de importantes. Si la intención era más
acotada (solo el criterio DANE), este ADR debe revisarse.

## Considered Options

- **Clase intermedia con campo `es_publicable`** (propuesta inicial): descartada — el
  proyecto no ha usado clases de datos en ningún script hasta ahora, y un booleano único
  no tiene lugar para las demás advertencias ya documentadas (desvío poblacional, DEFF).
- **Repetir la lógica ad-hoc de `scripts/30_generar_fichas_ciudades.py`** (un chequeo de
  código distinto por cada tipo de advertencia, disperso en cada sección de la ficha):
  descartada — es exactamente el patrón que se quiere eliminar al centralizar en el
  módulo compartido (ver ADR-0003).

## Consequences

- `scripts/30_generar_fichas_ciudades.py` puede simplificarse: sus chequeos manuales de
  confiabilidad, deriva poblacional y DEFF se reemplazan por una sola llamada al
  mecanismo de Notas Metodológicas del módulo compartido.
- El valor de un Indicador (`valor`) sigue siendo exactamente lo que ya trae el CSV
  maestro (numérico o el string `"ND"`) — no se introduce un `None` especial. Las notas
  son información adicional, no una transformación del dato.

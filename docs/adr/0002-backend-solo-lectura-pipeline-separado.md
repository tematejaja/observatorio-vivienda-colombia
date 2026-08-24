---
status: accepted
---

# El backend es de solo lectura; el pipeline sigue siendo un proceso CLI separado

El backend del observatorio no dispara ni orquesta corridas de `script_observatorio_nacional.py`;
solo lee lo que ese pipeline ya dejó en `output/` y `GEIH/procesado_nacional/`. Se
rechazó explícitamente un botón de "recalcular" dentro de la app.

**Por qué:** el pipeline es largo (el bootstrap por sí solo toma ~200s, la corrida
completa varios minutos más), depende de red (descarga contra el DANE) y tiene un
**gate de auditoría bloqueante** (FR-014 — Fase 1 no genera entregables si el red team
reporta un `RECHAZADO`). Ese gate es justo lo que no se quiere arriesgar detrás de un
botón de una app web: si alguien lo dispara y la auditoría rechaza algo a mitad de
camino, la app quedaría sirviendo datos parciales a quien esté mirando en ese momento.
Mantener el recálculo como una acción deliberada por CLI separa limpiamente "producir el
dato" (batch, auditado, offline) de "mostrar el dato" (web, siempre disponible).

## Consequences

- El backend no necesita manejo de procesos en segundo plano, colas de trabajo, ni
  bloqueo de corridas concurrentes — la complejidad de orquestación queda fuera de su
  alcance.
- Streamlit no es un runtime pensado para jobs de varios minutos con reintentos de red;
  evitarlo aquí evita pelear contra esa limitación.
- Si en el futuro alguien sin acceso a terminal necesita disparar una recorrida, es una
  función **añadida** sobre este backend (p. ej. un proceso separado que la app solo
  consulta), no algo que deba rediseñarse desde cero.

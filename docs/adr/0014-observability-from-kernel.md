# ADR 0014 - Observabilidad minima desde el kernel

## Estado

Aceptado.

## Contexto

El kernel ya emite eventos y la capa de gobierno ya registra decisiones, approvals, bloqueos y doom loops. Antes de exponer estos datos por CLI o API, necesitamos una forma interna y estable de consultar que paso y cual es el estado operativo minimo del sistema.

## Decision

Agregar observabilidad minima dentro del kernel sin introducir persistencia durable todavia.

La implementacion inicial incluye:

- `AuditTrail` como read model sobre `EventStore`.
- `AuditSummary` para resumir eventos relevantes.
- `ResourceMonitor` para reportar salud y conteos operativos.
- `KernelResourceSnapshot` como contrato de estado operativo.

El audit trail permite listar:

- eventos por tarea,
- eventos por `trace_id`,
- decisiones de policy,
- approvals,
- bloqueos por kill switch, doom loop o transicion invalida.

El resource monitor reporta:

- salud del kernel,
- cantidad total de eventos,
- cantidad total de tareas,
- tareas por estado,
- approvals pendientes,
- estado del kill switch,
- ultimo evento observado.

## Consecuencias

- v0.4 podra exponer comandos CLI sobre datos reales del kernel.
- No hace falta persistencia JSONL/SQLite para tener introspeccion minima.
- El audit trail actual es reconstruible desde eventos en memoria.
- La persistencia durable del audit trail queda para v0.6.

## Reversibilidad

Media. Los read models pueden reemplazarse o persistirse luego, pero el principio de consultar observabilidad desde eventos del kernel queda aceptado.

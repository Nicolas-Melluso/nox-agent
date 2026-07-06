# ADR 0015 - CLI real y event log JSONL minimo

## Estado

Aceptado.

## Contexto

La v0.3 dejo un kernel gobernable, auditable y testeado, pero solo era comodo dentro del proceso de Python. Una CLI real necesita que las tareas y eventos sobrevivan entre invocaciones de `nox`.

Al mismo tiempo, la persistencia modular completa sigue perteneciendo a v0.6: stores formales, SQLite, migraciones, backup y adapters reemplazables.

## Decision

Agregar en v0.4 un `JsonlEventStore` minimo y append-only dentro del workspace:

```text
.nox/events.jsonl
```

El store implementa el mismo contrato de eventos que el kernel ya usa:

- `append`
- `list_for_task`
- `list_all`
- `last_event_id_for_task`

La CLI carga un kernel por comando usando ese event log, rehidrata controles operativos simples desde eventos y expone comandos reales:

- `nox status`
- `nox task create`
- `nox task list`
- `nox task show`
- `nox task transition`
- `nox logs list`
- `nox logs task`
- `nox policy check`
- `nox approvals list`
- `nox approvals approve`
- `nox approvals reject`
- `nox kill status`
- `nox kill on`
- `nox kill off`
- `nox cli`

`nox cli` mantiene un kernel vivo para pruebas interactivas y flujos de approvals, pero tambien escribe eventos en el mismo JSONL.

Nota v0.6: los comandos se nombran como `logs` y `cli` para reflejar mejor la experiencia de usuario. Los eventos siguen siendo el dato canonico interno.

## Consecuencias

- v0.4 ya es operable desde CLI.
- Las tareas sobreviven entre comandos.
- Policy decisions, approvals y kill switch pueden consultarse desde eventos.
- JSONL no reemplaza la persistencia modular de v0.6.
- SQLite, migraciones y stores mas ricos siguen fuera de alcance de v0.4.

## Reversibilidad

Alta. `JsonlEventStore` es un adapter del contrato `EventStore`. En v0.6 puede convivir con SQLite o ser reemplazado sin cambiar la logica del kernel.

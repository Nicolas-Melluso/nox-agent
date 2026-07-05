# ADR 0012 - Event sourcing inicial del kernel

## Estado

Aceptado.

## Contexto

El kernel debe ser auditable y reconstruible desde el primer proceso. El estado de una tarea no debe depender solo de campos mutables.

## Decision

Usar event sourcing como modelo inicial para tareas.

La primera implementacion incluye:

- `EventRecord`
- `TaskState`
- `InMemoryEventStore`
- `EventBus`
- `StateMachineKernel`
- `AgentKernel`

## Consecuencias

- Cada tarea nace mediante un evento `task_created`.
- Cada cambio de estado emite un evento.
- El estado actual se reconstruye por replay.
- Las transiciones invalidas emiten `state_transition_denied`.
- El storage persistente vendra despues como adapter del mismo contrato.

## Reversibilidad

Baja como principio del kernel. Los adapters de storage son reemplazables, pero el contrato de eventos es fundacional.

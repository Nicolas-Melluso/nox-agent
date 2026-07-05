# ADR 0013 - Gobierno inicial, approvals y kill switch

## Estado

Aceptado.

## Contexto

El kernel ya puede crear tareas, emitir eventos y reconstruir estado por replay. Antes de sumar herramientas, modelos o API local, el sistema necesita una primera capa ejecutable de gobierno: clasificar capacidades, pedir aprobacion humana, bloquear acciones sensibles y frenar loops repetitivos.

## Decision

Agregar un modulo `governance` separado del CLI y de futuros adaptadores HTTP.

La primera implementacion incluye:

- `Capability`: read, write, execute, network, delete, send y credentials.
- `RiskLevel`: low, medium, high y critical.
- `PermissionDecision`: allow, ask y deny.
- `DefaultPolicyEngine`.
- `InMemoryApprovalQueue`.
- `KillSwitch`.
- `DoomLoopGuard`.
- `GovernedActionResult`.

Politica por defecto:

- `read`: allow.
- `write`: ask.
- `execute`: ask.
- `network`: ask.
- `delete`: deny.
- `send`: ask.
- `credentials`: deny.

El `AgentKernel` expone `request_capability(...)` para evaluar una accion dentro de una tarea existente. Si la decision es `ask`, se crea un approval pendiente. Si el kill switch esta activo, se bloquea la tarea nueva o la accion gobernada. Si el `DoomLoopGuard` detecta repeticion de la misma accion/input, emite evento y mueve la tarea a `blocked`.

Eventos nuevos:

- `policy_decision_recorded`
- `approval_requested`
- `approval_resolved`
- `kill_switch_changed`
- `kill_switch_blocked`
- `doom_loop_detected`

## Consecuencias

- Las acciones sensibles ya no son una convencion documental: tienen comportamiento ejecutable.
- El sistema puede demostrar por tests que write pide aprobacion, delete se niega, kill switch bloquea y doom loop termina en bloqueo.
- La cola de approvals y el kill switch son en memoria por ahora.
- La ejecucion real de herramientas queda fuera de esta decision; sera responsabilidad del Tool Runtime.
- La persistencia durable del audit trail queda para un adapter posterior.

## Reversibilidad

Media. Los contratos pueden ampliarse, pero el principio de pasar capacidades por PolicyEngine, ApprovalQueue y KillSwitch antes de ejecutar side effects es fundacional.

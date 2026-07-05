# Arquitectura

La arquitectura del proyecto se basa en capas y contratos. Las superficies de usuario son adaptadores; el nucleo estable es el kernel gobernable.

## Capas iniciales

```text
Product Surfaces
  -> Governance Facade
    -> Agent Kernel
      -> State Machine
      -> Policy Engine
      -> Approval Queue
      -> Kill Switch
      -> DoomLoopGuard
      -> Event Bus
      -> Audit Trail
      -> Resource Monitor
      -> Model Router
      -> Tool Runtime
      -> Stores
```

## Regla de entrada

CLI, API, desktop, web o cualquier otra superficie no deben ejecutar logica core directamente.

Cada superficie traduce una intencion externa a un comando interno:

```text
HTTP request / CLI command / UI action
  -> Application command
  -> Governance
  -> Kernel
  -> Ports
  -> Adapters
```

## Regla de salida

El kernel no debe depender de FastAPI, Typer, SQLite, llama.cpp ni ningun backend concreto.

Los detalles concretos viven en adaptadores reemplazables.

## Gobierno inicial

Desde v0.3, las capacidades sensibles se piden al kernel mediante `request_capability(...)`. El kernel evalua la accion con `PolicyEngine`, registra la decision como evento, crea approvals si corresponde, respeta el kill switch y bloquea loops repetitivos antes de que exista un Tool Runtime real.

## Observabilidad inicial

Desde v0.3.1, el kernel expone `AuditTrail` y `ResourceMonitor` como read models en memoria. No reemplazan la persistencia futura; preparan la CLI/API para consultar eventos, decisiones, bloqueos, approvals pendientes y salud operativa sin saltar el kernel.

## CLI real

Desde v0.4, la CLI carga un `AgentKernel` por comando usando `.nox/events.jsonl` como event log minimo. Este JSONL es un adapter temprano de `EventStore`, no la persistencia definitiva. La regla sigue siendo la misma: Typer traduce comandos de usuario; el kernel decide, emite eventos y reconstruye estado.

## Fuente visual

El diagrama de referencia vive en:

```text
docs/local-agent-os-architecture.drawio
```

El plan maestro vive en:

```text
docs/local-agent-os-development-plan.md
```

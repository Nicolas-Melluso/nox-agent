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

## Fuente visual

El diagrama de referencia vive en:

```text
docs/local-agent-os-architecture.drawio
```

El plan maestro vive en:

```text
docs/local-agent-os-development-plan.md
```

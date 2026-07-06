# Arquitectura

Nox es un agente local modular. La arquitectura del proyecto se basa en capas y contratos. Las superficies de usuario son adaptadores; el nucleo estable es el kernel gobernable.

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

## Engine instalado e instancia de workspace

Nox se instala una vez como agente modular general a nivel usuario o sistema. Esa instalacion contiene el runtime, kernel, adapters, politicas, schemas y defaults.

Cada proyecto usa `.nox/` como instancia local del workspace. `.nox` guarda metadata, estado, eventos, evidencia y referencias al engine instalado; no copia ni reemplaza al agente general.

```text
Nox instalado
  -> runtime + kernel + adapters + politicas + schemas

Proyecto/.nox
  -> instancia del workspace
  -> system prompt, eventos, config local, evidencia y estado
  -> referencias al engine instalado
```

La instancia del workspace debe tener identidad propia:

```text
workspace_id -> identidad estable del proyecto
instance_id  -> identidad de esta carpeta .nox concreta
```

Estas identidades deben aparecer en logs, eventos, auditoria, backups, storage y observabilidad.

## Alineacion con stack agentico

El proyecto toma como referencia conceptual las capas comunes de una pila agéntica, pero las implementa con foco local, modular y gobernable:

| Capa | En Nox |
| --- | --- |
| Modelos | `ModelBackend`, `ModelRouter`, llama.cpp/OpenAI futuros. |
| Runtime de agente | Engine instalado, kernel, workspace `.nox`, storage y CLI/API. |
| Protocolos/interoperabilidad | API local, MCP/conectores futuros, contratos internos. |
| Orquestacion | `AgentKernel`, state machine, planner/router futuros. |
| Herramientas/enriquecimiento | Tool Runtime futuro, filesystem read-only, Evidence Ledger, RAG. |
| Aplicaciones/superficies | CLI, API, UI futura. |
| Observabilidad/gobernanza | Audit trail, logs, policy, approvals, kill switch, resource monitor, evals. |
 
La prioridad de diferenciacion de Nox no esta en reemplazar modelos base. Esta en gobierno, observabilidad, ejecucion local, modularidad, herramientas controladas y memoria/evidencia verificable.

## Gobierno inicial

Desde v0.3, las capacidades sensibles se piden al kernel mediante `request_capability(...)`. El kernel evalua la accion con `PolicyEngine`, registra la decision como evento, crea approvals si corresponde, respeta el kill switch y bloquea loops repetitivos antes de que exista un Tool Runtime real.

## Observabilidad inicial

Desde v0.3.1, el kernel expone `AuditTrail` y `ResourceMonitor` como read models en memoria. No reemplazan la persistencia futura; preparan la CLI/API para consultar eventos, decisiones, bloqueos, approvals pendientes y salud operativa sin saltar el kernel.

## CLI real

Desde v0.4, la CLI carga un `AgentKernel` por comando usando `.nox/events.jsonl` como event log minimo. Este JSONL es un adapter temprano de `EventStore`, no la persistencia definitiva. La regla sigue siendo la misma: Typer traduce comandos de usuario; el kernel decide, emite eventos y reconstruye estado.

## API local

Desde v0.5, FastAPI expone una superficie HTTP local sobre el mismo runtime que usa la CLI. La API no habla directo con storage ni policy: carga el workspace, obtiene un `AgentKernel`, llama contratos internos y devuelve respuestas HTTP.

## Persistencia modular

Desde v0.6, `nox_agent_os.storage` formaliza puertos para `EventStore`, `TaskStore`, `ConfigStore` y `EvidenceStore`.

Los adapters iniciales son:

- `InMemory` para tests y ejecucion efimera.
- `JSONL` para compatibilidad con `.nox/events.jsonl` y datos append-only.
- `SQLite` como primer backend local durable con migracion inicial.

La memoria semantica no vive aun en v0.6. `EvidenceStore` prepara provenance y evidencia para herramientas/RAG futuros, pero no decide que debe recordar el agente.

## Fuente visual

El diagrama de referencia vive en:

```text
docs/local-agent-os-architecture.drawio
```

El plan maestro vive en:

```text
docs/local-agent-os-development-plan.md
```

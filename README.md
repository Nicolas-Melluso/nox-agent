# Nox

Agente local modular para ejecutar tareas con memoria futura, herramientas, gobierno, seguridad, observabilidad y evaluacion.

Este proyecto no empieza como un chatbot. Empieza como un agente modular local: un kernel gobernable donde modelos, herramientas, persistencia, interfaces y politicas puedan reemplazarse sin reescribir el nucleo.

## Estado

Version actual de trabajo: `v0.7 - Model Router sin modelo real`.

Ya existe CLI instalable, scaffolding de workspace, identidad estable para `.nox`, kernel event-sourced, gobierno inicial, observabilidad minima, event log JSONL por workspace, API HTTP local, adapters de persistencia `InMemory`, `JSONL` y `SQLite`, y Model Router inicial con `MockBackend`. Todavia no hay Tool Runtime, modelo local real ni memoria semantica.

## Modelo de instalacion

Nox se instala como agente modular general a nivel usuario o sistema. Esa instalacion provee runtime, kernel, adapters, politicas, schemas y defaults.

Cada proyecto crea una instancia local en `.nox/`. Esa instancia no contiene todo el agente: guarda metadata, estado del workspace, eventos, referencias al engine instalado y, mas adelante, configuracion local de herramientas o conexiones habilitadas para ese workspace.

```text
Nox instalado
  -> engine general, adapters, politicas, schemas, defaults

Proyecto del usuario
  -> .nox/
     -> system.prompt.md
     -> identity.json
     -> model.config.json
     -> events.jsonl
     -> estado/config/evidencia del workspace
     -> referencias al engine instalado
```

La instancia `.nox` tiene identidad propia en `.nox/identity.json`. Registra `workspace_id` e `instance_id` para que logs, auditoria, observabilidad, backups y futuras memorias puedan correlacionar eventos sin depender solo del path local.

## Artefactos base

- Plan maestro: `docs/local-agent-os-development-plan.md`
- Diagrama: `docs/local-agent-os-architecture.drawio`
- Roadmap versionado: `docs/roadmap.md`
- Decisiones de arquitectura: `docs/adr/`
- Instalacion y distribucion: `docs/installation-and-distribution.md`
- Tests y evals: `docs/testing-and-evals.md`
- Backends de modelo: `docs/model-backends.md`
- Instalador Windows experimental: `docs/windows-installer.md`
- API local: `docs/api-local.md`

## Principios iniciales

- Python 3.14 como runtime objetivo.
- `uv` como manejador de Python, entorno y dependencias.
- FastAPI como adaptador HTTP, no como nucleo.
- Typer como adaptador CLI inicial, reemplazable por CLI/REPL propio.
- SQLite como primer backend de persistencia, detras de puertos.
- YAML para configuracion humana.
- JSON/JSONL para informacion del sistema, eventos, logs y evidencia.
- HITL por defecto para acciones sensibles, irreversibles, externas o ambiguas.
- `nox-agent-os` sera el paquete distribuible y `nox` el comando publico.
- `nox init` crea una instancia local minima en `.nox/system.prompt.md`.
- `.nox` no es el engine; es el estado y metadata del workspace.

## Fuente de verdad

Los ADRs en `docs/adr/` son la fuente canonica para decisiones aceptadas.
README, roadmap y stack resumen esas decisiones para orientar el trabajo.

## Comandos principales

```text
nox init
nox doctor
nox version
nox prompt
nox update
nox upgrade --check
nox status
nox audit status
nox audit level normal
nox audit off
nox model list
nox model set mock-balanced
nox model limit mock-balanced to 4096
nox model route "objetivo de prueba"
nox task create "objetivo"
nox task list
nox task show <task_id>
nox task transition <task_id> running --reason "start"
nox logs list
nox logs task <task_id>
nox policy check <task_id> write --target docs/example.md
nox approvals list
nox kill on --reason "freeze"
nox cli
nox api serve
nox storage info
nox storage backup
nox storage export-events --output events.json
```

`nox update` refresca la metadata del workspace `.nox`. `nox upgrade` queda reservado para actualizar el engine instalado; en v0.6 existe como comando seguro de diagnostico/check, pero la descarga e instalacion automatica desde GitHub queda para una fase posterior.

## Capacidades actuales del kernel

- Crear tareas con `trace_id` y eventos versionados.
- Reconstruir estado por replay.
- Rechazar transiciones invalidas.
- Evaluar capacidades con `PolicyEngine`.
- Crear y resolver approvals en memoria.
- Activar kill switch para tareas nuevas o acciones gobernadas.
- Detectar repeticion de accion/input con `DoomLoopGuard`.
- Consultar audit trail inicial desde eventos en memoria.
- Consultar snapshot operativo con `ResourceMonitor`.
- Persistir eventos del workspace en `.nox/events.jsonl`.
- Correlacionar eventos nuevos con `workspace_id` estable e `instance_id`.
- Configurar modelo default, limites de tokens y nivel de auditoria en `.nox/model.config.json`.
- Rutear prompts por `ModelRouter` usando `MockBackend`.
- Auditar seleccion e invocacion de modelo por niveles: `off`, `minimal`, `normal`, `debug` y `trace`.
- Usar puertos de storage para eventos, tareas, config y evidencia.
- Probar persistencia via adapters `InMemory`, `JSONL` y `SQLite`.
- Operar el kernel desde comandos CLI reales.
- Operar el kernel desde API HTTP local.

## Build experimental Windows

```powershell
.\scripts\build_nox_exe.ps1
.\scripts\build_nox_setup.ps1
```

El primer comando genera `dist\nox\nox.exe`.
El segundo intenta generar `dist\installer\NoxSetup.exe` si Inno Setup esta instalado.

## Regla central

Ninguna superficie de usuario debe hablar directo con modelos, herramientas, memoria o storage.
Todo entra por contratos internos gobernados por el kernel, politicas y observabilidad.

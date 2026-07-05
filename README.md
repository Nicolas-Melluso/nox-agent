# Local Agent OS

Plataforma local para ejecutar agentes con memoria, herramientas, gobierno, seguridad, observabilidad y evaluacion.

Este proyecto no empieza como un chatbot. Empieza como un sistema operativo agente local: un kernel gobernable donde modelos, herramientas, persistencia, interfaces y politicas puedan reemplazarse sin reescribir el nucleo.

## Estado

Version actual de trabajo: `v0.3 - Gobierno y Seguridad Inicial`.

Ya existe CLI instalable, scaffolding de workspace, kernel event-sourced y una primera capa ejecutable de gobierno en memoria. Todavia no hay Tool Runtime, modelo local, API HTTP ni persistencia durable conectada.

## Artefactos base

- Plan maestro: `docs/local-agent-os-development-plan.md`
- Diagrama: `docs/local-agent-os-architecture.drawio`
- Roadmap versionado: `docs/roadmap.md`
- Decisiones de arquitectura: `docs/adr/`
- Instalacion y distribucion: `docs/installation-and-distribution.md`
- Tests y evals: `docs/testing-and-evals.md`
- Backends de modelo: `docs/model-backends.md`
- Instalador Windows experimental: `docs/windows-installer.md`

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
- `nox init` crea un workspace local minimo en `.nox/system.prompt.md`.

## Fuente de verdad

Los ADRs en `docs/adr/` son la fuente canonica para decisiones aceptadas.
README, roadmap y stack resumen esas decisiones para orientar el trabajo.

## Comandos futuros esperados

```text
nox init
nox doctor
nox version
nox prompt
nox update
```

## Capacidades actuales del kernel

- Crear tareas con `trace_id` y eventos versionados.
- Reconstruir estado por replay.
- Rechazar transiciones invalidas.
- Evaluar capacidades con `PolicyEngine`.
- Crear y resolver approvals en memoria.
- Activar kill switch para tareas nuevas o acciones gobernadas.
- Detectar repeticion de accion/input con `DoomLoopGuard`.

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

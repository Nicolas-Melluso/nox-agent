# Roadmap

Este roadmap convierte la vision del plan maestro en versiones acumulativas. Cada version debe dejar una capacidad verificable antes de avanzar.

## v0.0 - Decisiones Base

- Elegir stack inicial: Python 3.14, uv, FastAPI, Typer y SQLite.
- Definir arquitectura modular por puertos y adaptadores.
- Definir convenciones de configuracion y datos: YAML, JSON y JSONL.
- Mover plan maestro y diagrama a `docs/`.
- Crear ADRs iniciales.
- Definir HITL como politica base.

## v0.0.1 - Saneamiento Documental

- Crear indice de ADRs y fijar proxima numeracion.
- Documentar instalacion y distribucion guiada estilo `uvx`.
- Documentar tests y evals por etapas.
- Formalizar `ModelBackend` y providers reemplazables.
- Definir fuente canonica por tipo de dato.
- Aclarar reglas HITL para verificaciones side-effect-free.
- Actualizar el backlog del plan maestro para evitar conflictos de ADRs.

## v0.1 - Proyecto Instalable Vacio

- Crear `pyproject.toml`, `.python-version` y lockfile.
- Crear estructura `src/`, `tests/`, `configs/`, `data/` y `evals/`.
- Crear comando base `nox`.
- Implementar `nox --help`.
- Implementar `nox init`.
- Implementar `nox doctor`.
- Implementar `nox version`.
- Implementar `nox update`.
- Crear workspace local minimo en `.nox/system.prompt.md`.
- Preparar instalacion futura via `uvx --from nox-agent-os nox init` o `uv tool install --editable .`.
- Agregar experimento para generar `nox.exe` y `NoxSetup.exe` en Windows.

## v0.2 - Kernel Minimo

- Crear `TaskContract`.
- Crear `EventContract`.
- Crear `StateMachineKernel`.
- Crear `EventBus`.
- Emitir `trace_id` desde la primera operacion.
- Crear stores iniciales en memoria y JSONL/SQLite.
- Crear y reconstruir tareas desde eventos.

## v0.3 - Gobierno y Seguridad Inicial

- Crear `PolicyEngine` minimo.
- Crear `ApprovalQueue`.
- Crear `KillSwitch`.
- Crear `TransitionGuards`.
- Crear `DoomLoopGuard` basico.
- Bloquear acciones sensibles por defecto.
- Registrar decisiones en audit trail.

## v0.4 - CLI Real

- Implementar comandos Typer iniciales.
- Enrutar cada comando por el kernel.
- Evitar logica de negocio dentro de la CLI.
- Exponer tareas, eventos, approvals, kill switch y verificaciones.

## v0.5 - API Local

- Agregar FastAPI como adaptador HTTP.
- Crear endpoints minimos para tareas, eventos y control.
- Mantener la logica core fuera de routers HTTP.

## v0.6 - Persistencia Modular

- Formalizar `EventStore`, `TaskStore`, `ConfigStore` y `EvidenceStore`.
- Implementar adaptadores `InMemory`, `JSONL` y `SQLite`.
- Agregar `schema_version`, migraciones iniciales y export/backup basico.

## v0.7 - Model Router Sin Modelo Real

- Crear `ModelBackend`.
- Crear `MockBackend`.
- Crear `ModelRegistry`.
- Crear `ReasoningProfile`.
- Crear `RoutingPolicy`.
- Registrar razon de seleccion, perfil y presupuesto.

## v0.8 - llama.cpp Backend

- Agregar `LlamaCppBackend`.
- Configurar endpoint local.
- Permitir cambiar backend por configuracion.
- Registrar errores y fallback.

## v0.9 - Evidence Ledger y Tools Read-Only

- Crear `EvidenceLedger`.
- Crear tool runtime minimo.
- Agregar filesystem read-only con provenance.
- Registrar archivos leidos como evidencia.
- Bloquear escritura, ejecucion y red por politica.

## v1.0 - Primera Version Funcional Local

- CLI usable.
- API local usable.
- Kernel event-sourced.
- Policy, HITL y KillSwitch activos.
- Modelo local via adaptador.
- Persistencia SQLite.
- Logs, traces y audit trail.
- Tests por etapas: none, smoke, unit, contract, safety, integration, eval, full.
- Instalacion guiada funcionando.

## v1.1+ - Evolucion

- RAG local.
- Memoria minima.
- Subagentes con contrato.
- UI de approvals.
- Workflows.
- Skills y plugins.
- Backend OpenAI/Codex opcional.
- Distribucion publica mas pulida.

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
- Crear store inicial en memoria.
- Crear y reconstruir tareas desde eventos.
- Dejar JSONL/SQLite para `v0.6 - Persistencia Modular`.

Estado actual:

- `TaskState` y `EventRecord` iniciales creados.
- `InMemoryEventStore`, `EventBus`, `StateMachineKernel` y `AgentKernel` iniciales creados.
- Replay de tarea y bloqueo de transicion invalida cubiertos por tests.
- JSONL/SQLite quedan explicitamente fuera de v0.2 y pasan a v0.6.

## v0.3 - Gobierno y Seguridad Inicial

- Crear `PolicyEngine` minimo.
- Crear `ApprovalQueue`.
- Crear `KillSwitch`.
- Crear `TransitionGuards`.
- Crear `DoomLoopGuard` basico.
- Bloquear acciones sensibles por defecto.
- Registrar decisiones en audit trail.

Estado actual:

- `DefaultPolicyEngine` inicial creado con decisiones `allow`, `ask` y `deny`.
- `InMemoryApprovalQueue` creada para approvals pendientes y resolucion humana.
- `KillSwitch` creado para bloquear nuevas tareas o acciones gobernadas.
- `DoomLoopGuard` basico creado para detectar accion/input repetidos.
- `AgentKernel.request_capability(...)` enruta capacidades por gobierno antes de cualquier side effect futuro.
- Decisiones de policy, approvals, kill switch y doom loop emiten eventos auditables.
- Tests `safety` iniciales cubren read allow, write ask, delete deny, kill switch y doom loop.
- Contratos ampliados de state machine creados: `AgentStatus`, `RunMode`, `RecoveryState` y `TerminationReason`.
- `TaskStatus` ampliado con estados de planificacion, approvals, tools, subagentes, recovery y timeout.
- `AuditTrail` inicial creado como read model sobre eventos en memoria.
- `ResourceMonitor` inicial creado para snapshot operativo del kernel.

Pendiente para fases posteriores:

- Persistir audit trail en JSONL/SQLite.
- Conectar estas decisiones a Tool Runtime real.
- Exponer approvals y kill switch desde CLI/API.
- Implementar comportamiento completo para todos los ejes de la state machine.

## v0.4 - CLI Real

- Implementar comandos Typer iniciales.
- Enrutar cada comando por el kernel.
- Evitar logica de negocio dentro de la CLI.
- Exponer tareas, eventos, approvals, kill switch y verificaciones.
- Agregar `JsonlEventStore` minimo en `.nox/events.jsonl` para que la CLI sea usable entre invocaciones.
- Agregar `nox cli` como sesion interactiva operativa con kernel vivo.

Estado actual:

- `JsonlEventStore` minimo creado como adapter de `EventStore`.
- `nox init` crea `.nox/events.jsonl`.
- `nox status` muestra snapshot operativo del kernel.
- `nox task create/list/show/transition` opera sobre eventos persistidos.
- `nox logs list/task` inspecciona el audit trail.
- `nox policy check` registra decisiones y approvals.
- `nox approvals list/approve/reject` rehidrata approvals pendientes desde eventos.
- `nox kill status/on/off` persiste estado del kill switch via eventos.
- `nox cli` permite operar tareas, policy, approvals, logs y kill switch en una sesion viva.
- Tests v0.4 cubren persistencia JSONL, comandos CLI y sesion interactiva basica.

Pendiente para fases posteriores:

- Persistencia modular formal con stores versionados en v0.6.
- CLI mas ergonomica para filtros, formatos JSON y workflows largos.
- Tool Runtime real para ejecutar acciones aprobadas.

## v0.5 - API Local

- Agregar FastAPI como adaptador HTTP.
- Crear endpoints minimos para tareas, eventos y control.
- Mantener la logica core fuera de routers HTTP.

Estado actual:

- `nox_agent_os.api.create_app(...)` creado como factory FastAPI.
- `nox api serve` creado para servir el workspace actual.
- API y CLI comparten `load_kernel_context(...)` y `.nox/events.jsonl`.
- Endpoints creados para health, status, tasks, events, policy, approvals y kill switch.
- Tests API cubren ciclo de tarea, eventos, approvals y kill switch.

Pendiente para fases posteriores:

- Autenticacion/local trust boundary.
- Streaming de eventos.
- Formatos de respuesta mas estables para SDK/UI.
- Persistencia modular formal en v0.6.

## v0.6 - Persistencia Modular

- Formalizar `EventStore`, `TaskStore`, `ConfigStore` y `EvidenceStore`.
- Implementar adaptadores `InMemory`, `JSONL` y `SQLite`.
- Agregar `schema_version`, migraciones iniciales y export/backup basico.
- Tomar `.nox/events.jsonl` de v0.4 como adapter inicial, no como persistencia final.

Estado actual:

- `nox_agent_os.storage` creado como capa de persistencia modular.
- Puertos `EventStore`, `TaskStore`, `ConfigStore` y `EvidenceStore` formalizados.
- Adapters `InMemory`, `JSONL` y `SQLite` implementados para eventos, tareas, config y evidencia.
- SQLite crea tablas de eventos, tareas, config, evidencia y `schema_migrations`.
- CLI agrega `nox storage info`, `nox storage backup` y `nox storage export-events`.
- CLI agrega `nox upgrade --check` como contrato inicial para actualizacion futura del engine instalado.
- Tests v0.6 cubren contratos de storage, migracion SQLite, backup/export y comandos CLI.

Pendiente para fases posteriores:

- Decidir si/como migrar workspaces de JSONL default a SQLite default.
- Agregar stores especificos de memoria cuando exista semantica de memoria.
- Conectar `EvidenceStore` con Tool Runtime y Evidence Ledger en v0.9.

## v0.6.1 - Identidad de Instancia

- Definir Nox publicamente como agente local modular.
- Crear `.nox/identity.json`.
- Generar `workspace_id` estable para el proyecto.
- Generar `instance_id` para la instancia `.nox` concreta.
- Registrar version de engine, executable path, fecha de creacion y ultima actualizacion.
- Hacer que `nox doctor` muestre `workspace_id` e `instance_id`.
- Hacer que eventos/logs futuros puedan incluir ambas identidades sin depender solo del path local.

Estado actual:

- `.nox/identity.json` se crea en `nox init` y se repara automaticamente si falta al cargar un workspace existente.
- `nox update` refresca version, engine y paths actuales sin cambiar `workspace_id` ni `instance_id`.
- `nox doctor`, `nox status`, `nox storage info`, `nox logs` y API local exponen identidad.
- Tareas nuevas usan `workspace_id` estable en vez del path del proyecto.
- Eventos nuevos pueden persistir `instance_id`; JSONL mantiene compatibilidad con eventos previos sin ese campo.
- SQLite sube storage schema a version 2 para agregar `instance_id` en eventos y tareas.

Pendiente para fases posteriores:

- Sincronizacion remota o multi-device de identidades.
- Politicas de rotacion/reemision de `instance_id`.
- Memoria semantica asociada a identidad.

## v0.7 - Model Router Sin Modelo Real

- Crear `ModelBackend`.
- Crear `MockBackend`.
- Crear `ModelRegistry`.
- Crear `ReasoningProfile`.
- Crear `RoutingPolicy`.
- Registrar razon de seleccion, perfil y presupuesto.

Estado actual:

- `nox_agent_os.modeling` creado como capa inicial de modelos.
- `ModelBackend`, `ModelRequest`, `ModelResponse`, `ModelRoute` y `ModelInvocationResult` creados.
- `MockBackend` implementado con modelos `mock-fast`, `mock-balanced` y `mock-deep`.
- `ModelRegistry`, `ReasoningProfile`, `RoutingPolicy` y `ModelRouter` implementados.
- `.nox/model.config.json` creado para modelo default, limites por modelo y nivel de auditoria.
- `nox model list`, `nox model set`, `nox model limit <modelo> to <tokens>` y `nox model route` implementados.
- `nox audit status`, `nox audit level` y `nox audit off` implementados.
- Eventos `model_route_selected` y `model_invocation_completed` agregados al audit trail cuando la auditoria no esta en `off`.
- Niveles de auditoria iniciales: `off`, `minimal`, `normal`, `debug` y `trace`.

Pendiente para fases posteriores:

- API HTTP especifica para modelos si la necesitamos como superficie estable.
- Streaming de respuestas.
- Costos reales, cuotas y credenciales.
- Modelos reales via `LlamaCppBackend` en v0.8.
- Integracion con Codex como subagente externo gobernado, no como backend plano de inferencia.

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
- `nox upgrade` descarga la ultima release desde GitHub, valida el artefacto y actualiza el engine instalado.

## v1.1+ - Evolucion

- RAG local.
- Memoria minima.
- Subagentes con contrato.
- UI de approvals.
- Workflows.
- Skills y plugins.
- Backend OpenAI/Codex opcional.
- Distribucion publica mas pulida.

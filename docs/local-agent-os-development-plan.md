# Local Agent OS - Guia maestra de desarrollo

Documento de trabajo para construir desde cero una plataforma de agente local, modular, gobernable y extensible.

Artefacto visual relacionado: `local-agent-os-architecture.drawio`.

## 1. Proposito

Construir una plataforma local de inteligencia artificial que funcione como un sistema operativo agente: no un chatbot aislado, sino un entorno donde agentes puedan nacer, operar, usar herramientas, recordar, ser auditados, pedir permisos, ser apagados con seguridad y evolucionar mediante evaluaciones.

El objetivo final es tener un agente local funcional con estas propiedades:

- Usa modelos locales reemplazables, inicialmente mediante `llama.cpp`.
- Puede cambiar de modelo y nivel de razonamiento en tiempo de ejecucion.
- Tiene un orquestador maestro que decide planes, herramientas, memoria y subagentes.
- Ejecuta acciones a traves de permisos, sandbox, logs y HITL por defecto.
- Tiene memoria de trabajo, episodica, semantica, procedural, reflexiva, biografica y reconstructiva.
- Usa RAG local con ingesta, limpieza, chunking, embeddings, indices, retrieval y trazabilidad.
- Incluye pensamiento critico artificial: detractor, premortem, incertidumbre, contradicciones, verificacion y postmortem.
- Puede exponerse como chat, CLI, desktop, web, mobile, IDE, browser extension, mensajeria, API o widgets.
- Puede crecer hacia workflow automation, agentes persistentes, marketplace de skills, EvalOps, admin y deployment.

Frase guia:

```text
No construimos un agente. Construimos una plataforma local donde agentes pueden operar con memoria, herramientas, gobierno, seguridad y evaluacion.
```

Diferenciacion a validar con cuidado:

- Privacidad local y control del usuario sobre datos, modelos y herramientas.
- Gobernabilidad demostrable, no solo declarada.
- Observabilidad desde el primer proceso, para poder explicar que paso, que se bloqueo y que se puede apagar.
- Memoria y RAG basados en evidencia, provenance, versionado, borrado y migraciones.
- Modelos y niveles de razonamiento reemplazables en tiempo de ejecucion.
- UX de confianza: el sistema debe mostrar riesgo, evidencia, permisos y razon de cada accion sensible.

Identidad refinada:

- Nox se define como agente local modular, no como sistema operativo literal.
- La metafora de kernel/OS se conserva solo como arquitectura interna.
- La instalacion general de Nox contiene engine, runtime, policies, adapters, schemas y defaults.
- Cada `.nox` es una instancia de workspace, no una copia del agente completo.
- Cada instancia `.nox` debe tener `workspace_id` e `instance_id` propios para logs, auditoria, observabilidad, backups y memoria futura.
- El roadmap debe seguir contemplando las capas de una pila agentica: modelos, runtime, protocolos, orquestacion, herramientas, superficies, observabilidad y gobernanza.

## 2. Principios no negociables

1. El modelo es reemplazable. El sistema no depende de un proveedor ni de una familia de modelos.
2. La inferencia se gobierna. El valor esta en el Model Router, Reasoning Controller y Policy Engine.
3. Todas las acciones pasan por politica, permisos, sandbox y observabilidad.
4. Autonomia por capacidad, supervision por consecuencia.
5. HITL por defecto para acciones irreversibles, externas o sensibles.
6. La memoria no es solo historial; es un subsistema con capas, consolidacion y olvido.
7. RAG no es tirar PDFs; requiere limpieza, chunking, embeddings, retrieval, reranking, citas y evaluacion.
8. Los subagentes son procesos con contrato, no entidades libres.
9. Las evaluaciones se escriben antes de confiar en el sistema.
10. El sistema debe ser interrumpible, auditable, reversible y desplegable.
11. Seguridad y observabilidad nacen con el kernel. Si no se puede monitorear desde el inicio, se pierde historia critica.
12. Gobernable significa verificable: debe haber eventos, trazas, replay, politicas y pruebas que demuestren control real.
13. Todo dato persistente importante debe tener versionado, provenance, politica de borrado, retencion y migracion.
14. Los niveles de razonamiento son configuracion ejecutable, no etiquetas descriptivas.

## 3. Arquitectura por capas

```text
Product Surface Layer
  -> Governance Layer
    -> Control Plane
    -> Policy & Security
    -> Master Orchestrator
      -> Self Model
      -> Cognitive Safety Layer
      -> Model Router + Reasoning Controller
      -> Agent Fleet Manager
      -> Workflow & Automation Engine
      -> Subagent Factory
      -> Context Engineering Layer
      -> Memory System
      -> Knowledge / RAG System
      -> Tool Runtime
        -> Integration Hub
        -> Skill & Plugin Supply Chain
    -> EvalOps Lab
    -> Observability
  -> Deployment & Admin
```

Regla de conexion clave:

```text
Ninguna superficie de usuario habla directo con herramientas, modelos o memoria.
Todo entra por Governance y se ejecuta a traves del Orquestador, Politicas y Tool Runtime.
```

## 4. Contratos base del sistema

Antes de implementar modulos grandes, definir estos contratos.

### 4.1 Task Contract

Cada tarea debe tener:

- `task_id`
- `user_goal`
- `workspace_id`
- `session_id`
- `risk_level`
- `allowed_capabilities`
- `required_human_approval`
- `budget`
- `deadline`
- `success_criteria`
- `current_state`

### 4.2 Model Invocation Contract

Cada llamada de modelo debe registrar:

- modelo elegido
- backend usado
- razon de seleccion
- nivel de razonamiento
- input normalizado
- contexto usado
- herramientas disponibles
- presupuesto de tokens/tiempo
- salida estructurada
- errores y fallback

### 4.3 Tool Call Contract

Toda herramienta debe declarar:

- nombre
- descripcion
- parametros
- permisos requeridos
- riesgo
- efectos secundarios
- sandbox requerido
- si requiere HITL
- inputs/outputs auditables

### 4.4 Memory Record Contract

Cada recuerdo debe tener:

- tipo: working, episodic, semantic, procedural, reflective, biographical, sensory
- fuente
- confianza
- fecha
- proyecto/sesion
- politica de retencion
- embeddings opcionales
- evidencia asociada
- version compactada

### 4.5 Eval Contract

Cada evaluacion debe definir:

- caso
- entrada
- resultado esperado
- criterios de aprobacion
- grader humano o automatico
- riesgo que cubre
- modulos involucrados
- regresion asociada

### 4.6 Event Contract

Cada evento del sistema debe ser inmutable y versionado:

- `event_id`
- `event_type`
- `schema_version`
- `trace_id`
- `task_id`
- `session_id`
- `workspace_id`
- `actor`
- `timestamp`
- `payload`
- `previous_event_id` opcional
- `source_module`
- `risk_level` opcional
- `decision_record_id` opcional

Este contrato permite replay, auditoria, reconstruccion de estado, debugging y apagado selectivo de capacidades.

### 4.7 Evidence Ledger Contract

El Evidence Ledger es el libro mayor de evidencia del sistema. No es memoria y no es RAG; es la base verificable que ambos pueden usar.

Sirve para registrar evidencia primaria antes de que el agente la interprete:

- documentos leidos
- fragmentos recuperados por RAG
- tool calls y resultados
- decisiones del router
- aprobaciones humanas
- outputs de subagentes
- errores, rechazos y postmortems

Cada entrada debe tener:

- `evidence_id`
- `source_type`: file, document, web, tool, user, model, memory, connector
- `source_uri`
- `source_hash`
- `created_at`
- `observed_by`
- `content_ref` o contenido normalizado
- `provenance`
- `confidence`
- `retention_policy`
- `delete_policy`
- `schema_version`
- `related_task_id`
- `related_memory_id` opcional
- `related_trace_id`

Regla importante:

```text
La memoria interpreta evidencia.
RAG recupera evidencia.
El Evidence Ledger conserva la trazabilidad de lo que realmente se observo.
```

### 4.8 Configuration and Environment Contract

Las decisiones tempranas de config/env vars que faltan definir antes de escribir demasiado codigo:

- formato de configuracion: `yaml`, `toml` o `json`
- precedencia: defaults -> archivo local -> env vars -> CLI flags -> policy runtime
- ubicacion de configs: global, workspace, proyecto, usuario
- perfiles: dev, test, local-cpu, local-gpu, workstation, air-gapped
- paths: data, logs, cache, models, workspaces, temp, backups
- endpoints de backends: `llama.cpp`, Ollama, vLLM, cloud opcional
- feature flags iniciales
- politicas por defecto: read, write, execute, network, delete, send, credentials
- variables secretas permitidas
- storage de secretos: env var, OS keychain, Vault futuro, archivo cifrado futuro
- telemetria: local-only por defecto
- retencion de logs, evidencia y memoria
- versionado de esquemas y migraciones
- estrategia de backup/restore
- limites de recursos: tokens, tiempo, RAM, CPU/GPU, concurrencia

### 4.9 Executable ReasoningProfile Contract

Un `ReasoningProfile` no debe ser una etiqueta como `deep` o `normal`. Debe ser una politica ejecutable:

- `profile_id`
- objetivo del perfil
- modelos permitidos
- backends permitidos
- presupuesto de tokens
- timeout
- cantidad maxima de tool calls
- herramientas permitidas
- verificaciones obligatorias
- si requiere detractor/premortem/evidence check
- si requiere HITL
- riesgo maximo permitido
- fallback si falla el modelo
- eval gates requeridos
- formato de salida esperado

Ejemplo conceptual:

```text
fast/direct:
  modelos: pequenos y rapidos
  herramientas: ninguna o read-only
  verificaciones: minimas
  riesgo permitido: bajo

deep/reviewed:
  modelos: razonador o modelo fuerte
  herramientas: read-only + RAG
  verificaciones: evidence check + contradiction check
  riesgo permitido: medio

multi-agent/verified:
  modelos: router dinamico
  herramientas: segun contrato
  verificaciones: detractor + second opinion + eval gate
  riesgo permitido: alto solo con HITL
```

### 4.10 State Machine Contract

La maquina de estados no debe ser una unica enum gigante. Debe ser un conjunto de ejes ortogonales que permiten reconstruir que ocurrio, por que ocurrio y que subsistema debe actuar.

Regla central:

```text
Ningun modulo escribe estado final directamente.
Todo cambio de estado pasa por State Machine Kernel, Transition Guards y Event Bus.
El estado actual siempre puede reconstruirse por replay de eventos.
```

Ejes iniciales:

```text
TaskStatus:
created, classified, planned, policy_review, waiting_approval,
queued, running, waiting_model, waiting_tool, waiting_subagent,
paused, completed, failed, blocked, cancelled, rejected,
timed_out, killed, recovering, replaying, rolled_back

AgentStatus:
spawning, active, idle, awaiting_user_input,
awaiting_confirmation, paused, finished, stopped,
error, rate_limited

RunMode:
plan, act, build, review, explore, research,
deep_planning, read_only, autonomous, incident_mode

PermissionDecision:
allow, ask, deny, approved_once, approved_session,
rejected, auto_reviewing, auto_approved, auto_denied

RecoveryState:
checkpointed, compacting, compacted, rewind_requested,
restore_files, restore_context, restore_all, replaying

TerminationReason:
completed, user_stop, max_steps, max_tokens, max_time,
policy_denied, tool_error, model_error, rate_limited,
kill_switch, shutdown_graceful, doom_loop_detected
```

Cada transicion debe registrar:

- `transition_id`
- eje afectado: task, agent, run_mode, permission, recovery, termination
- `from`
- `to`
- `reason`
- `guard_result`
- `actor`
- `trace_id`
- `task_id`
- `agent_id` opcional
- `evidence_id` opcional
- `timestamp`

Transition Guards obligatorios:

- No se puede pasar de `completed`, `cancelled`, `rejected` o `killed` a `running` sin crear una nueva tarea o una accion explicita de replay/recovery.
- `autonomous` no habilita por si mismo acciones destructivas, externas o irreversibles.
- `incident_mode` fuerza degradacion de capacidades: read-only, logging alto, red limitada y HITL mas estricto.
- `waiting_approval` solo puede avanzar con `approved_once`, `approved_session`, `auto_approved` o una politica explicita de bajo riesgo.
- `replaying` y `recovering` no pueden ejecutar herramientas con side effects.
- Toda transicion invalida emite `state_transition_denied`.

`doom_loop_detected` no es un error comun. Es una razon de terminacion o pausa que indica que el sistema esta repitiendo ciclos sin progreso verificable.

El `DoomLoopGuard` debe observar:

- misma herramienta con input normalizado igual o equivalente demasiadas veces
- misma falla repetida sin nueva evidencia
- mismo plan regenerado sin cambio material
- consumo de tokens/tiempo sin avance de `TaskStatus`
- subagentes devolviendo resultados redundantes
- intentos repetidos bloqueados por la misma politica

Acciones al detectar doom loop:

- emitir evento `doom_loop_detected`
- bloquear la tool call repetida o degradar el `RunMode`
- mover tarea a `blocked`, `paused` o `policy_review` segun riesgo
- crear entrada en Evidence Ledger con la trayectoria resumida
- pedir HITL si la tarea sigue siendo valiosa
- crear regression eval si el patron revela una falla sistemica

## 5. Roadmap de implementacion por fases

### Fase 0 - Fundacion documental y decisiones iniciales

Objetivo: transformar la vision en especificaciones versionables.

Componentes cubiertos:

- Local Agent OS
- arquitectura general
- proposito
- criterios de completitud
- decisiones de stack

Tareas:

- Crear `README.md` maestro del proyecto.
- Crear `docs/architecture.md` con capas y flujo.
- Crear `docs/glossary.md` con definiciones: agente, skill, memoria, RAG, HITL, sandbox, eval, subagente.
- Crear `docs/adr/` para Architecture Decision Records.
- Elegir stack inicial. Recomendacion inicial: core en Python, API en FastAPI, persistencia en SQLite/Postgres, modelo local via `llama.cpp` server detras de adaptador HTTP compatible.
- Definir que dependencias externas son runtime critico y cuales son reemplazables.
- Definir `docs/configuration.md` con formato de config, precedencia, perfiles, env vars, paths, secrets y limites.
- Definir `docs/schemas.md` con versionado inicial de eventos, tareas, evidencia, memoria y tool calls.
- Definir `docs/data-lifecycle.md` con retencion, borrado, export/import, backup/restore y migraciones.
- Crear ADRs tempranos para: persistencia, event sourcing, observabilidad local, secrets, sandbox inicial y Evidence Ledger.

Criterios de aceptacion:

- Existe una decision escrita para backend de inferencia inicial.
- Existe una decision escrita para persistencia.
- Existe una lista de modulos obligatorios y opcionales.
- El draw.io queda enlazado como mapa visual.
- Existe una decision escrita sobre config/env vars y precedencia.
- Existe una decision escrita sobre versionado, borrado, migraciones y provenance.

### Fase 1 - Kernel gobernable, estado, eventos y observabilidad minima

Objetivo: construir el nucleo minimo del sistema antes de sumar inteligencia, pero con seguridad y observabilidad desde el primer proceso.

Componentes cubiertos:

- Governance Layer
- Task Contract
- Event Contract
- State Machine Contract
- Event Bus
- Current State
- Transition Guards
- Sessions
- Workspaces
- Lifecycle
- Task Queue / Dispatch
- DoomLoopGuard
- Observability minima
- Policy minima
- EvalOps minimo

Tareas:

- Implementar `AgentKernel`.
- Implementar `StateMachineKernel` con ejes `TaskStatus`, `AgentStatus`, `RunMode`, `PermissionDecision`, `RecoveryState` y `TerminationReason`.
- Implementar `TaskState` como estado reconstruible por eventos, no como campo mutable aislado.
- Implementar `TransitionGuard` para rechazar transiciones invalidas y emitir `state_transition_denied`.
- Implementar `SessionStore`.
- Implementar `WorkspaceStore`.
- Implementar `EventBus` local.
- Implementar formato de evento versionado.
- Implementar `trace_id` desde el primer comando.
- Implementar logs estructurados minimos.
- Implementar audit trail minimo.
- Implementar decision records minimos para cambios de estado y politica.
- Implementar `PolicyEngine` minimo con acciones: read, write, execute, network, delete, send, credentials.
- Implementar `ApprovalQueue` minima en memoria.
- Implementar `KillSwitch` minimo para bloquear nuevas tareas y tool calls.
- Implementar `ResourceMonitor` inicial para procesos, tiempo, memoria y estado del kernel.
- Implementar `DoomLoopGuard` minimo con deteccion de herramienta/input repetidos, fallas repetidas y ausencia de progreso de estado.
- Implementar `TerminationReason` incluyendo `doom_loop_detected`, `kill_switch`, `shutdown_graceful`, `policy_denied`, `max_steps`, `max_tokens`, `max_time`, `tool_error`, `model_error` y `rate_limited`.
- Implementar estados iniciales completos definidos en `State Machine Contract`.
- Crear almacenamiento inicial en SQLite o archivos JSON versionados.
- Crear evals bloqueantes iniciales:
  - tarea persiste y se reconstruye tras reinicio
  - accion de escritura requiere aprobacion
  - evento tiene `trace_id` y `schema_version`
  - Kill Switch bloquea nueva ejecucion
  - replay reconstruye estado final
  - transicion invalida queda rechazada y auditada
  - doom loop repetible termina en `doom_loop_detected`

Criterios de aceptacion:

- Se puede crear una tarea.
- Se puede pausar, reanudar y cancelar.
- Cada cambio emite evento.
- Una transicion invalida no cambia estado y genera `state_transition_denied`.
- La tarea sobrevive reinicio del proceso.
- Se puede reconstruir una tarea por replay de eventos.
- Cada tarea tiene `trace_id`.
- Cada decision sensible queda en audit trail.
- Una accion peligrosa queda bloqueada o pendiente de aprobacion.
- El sistema puede mostrar procesos/tareas activas y detener nuevas acciones con Kill Switch.
- Un ciclo repetitivo sin progreso se pausa o bloquea con `doom_loop_detected`.
- Las evals minimas corren y bloquean avance si fallan.

### Fase 2 - Model Router e inferencia local

Objetivo: poder invocar modelos locales sin acoplar el sistema a un modelo concreto.

Componentes cubiertos:

- Model Router
- Reasoning Controller
- Model Registry
- llama.cpp
- vLLM futuro
- Ollama opcional
- Cloud Models opcionales
- Ejecutor propio futuro
- Fast / Direct
- Normal
- Deep Reasoning
- Multi-Agent Verified
- Maximum / Formal Eval
- Routing Policy

Tareas:

- Crear interfaz `ModelBackend`.
- Crear adaptador `LlamaCppBackend`.
- Crear `ModelRegistry` con capacidades: contexto, velocidad, coste, especialidad, tool-use, razonamiento, modalidad.
- Crear `ReasoningProfile` ejecutable: modelos permitidos, herramientas permitidas, verificaciones, timeout, presupuesto, riesgo permitido, fallback y eval gates.
- Crear `RoutingPolicy` basada en tarea, riesgo, costo, latencia y calidad esperada.
- Crear fallback: si un modelo falla, reintentar con otro backend o degradar razonamiento.

Criterios de aceptacion:

- El mismo prompt puede ejecutarse con distintos modelos.
- El orquestador puede pedir un nivel de razonamiento y recibir una estrategia concreta.
- El sistema registra por que eligio cada modelo.
- `llama.cpp` es reemplazable por otro backend sin tocar el orquestador.
- Cada perfil de razonamiento produce limites ejecutables y verificables.
- El router registra modelo, perfil, presupuesto, riesgo, fallback y razon de seleccion.

### Fase 3 - Superficie minima de producto

Objetivo: tener una forma simple de usar el sistema sin construir todavia toda la UI final.

Componentes cubiertos:

- Product Surface Layer
- Usuario / Objetivo
- Chat
- CLI
- API / SDK
- Embedded Widgets futuro
- Web, Desktop, Mobile, IDE, Browser Extension y Messaging Channels como objetivos posteriores

Tareas:

- Implementar CLI minima.
- Implementar API local minima.
- Implementar endpoint `POST /tasks`.
- Implementar endpoint `GET /tasks/{id}`.
- Implementar streaming de eventos basico.
- Definir contrato para futuras superficies: chat, desktop, web, mobile, IDE, browser extension y canales de mensajeria.

Criterios de aceptacion:

- Un usuario puede crear una tarea desde CLI.
- Un cliente puede crear una tarea por API.
- La respuesta muestra estado, modelo usado y eventos principales.
- Ninguna superficie puede saltar Governance, Policy Engine, trace_id o audit trail.

### Fase 4 - Gobierno, seguridad y control operativo

Objetivo: ampliar los limites ya nacidos en el kernel antes de dar herramientas peligrosas o acciones con efectos secundarios.

Componentes cubiertos:

- Control Plane
- Kill Switch
- Graceful Shutdown
- Feature Flags
- Resource Governor
- Incident Mode
- Rollback / Checkpoints
- Capability Gates
- Policy & Security
- Policy Engine
- Security Layer
- Human-in-the-Loop
- Sandbox
- Permissions / Capability Gates
- Prompt Injection Defense
- Secrets Policy
- Risk Classification
- Approval Queue

Tareas:

- Expandir `PolicyEngine` minimo creado en Fase 1.
- Implementar `FeatureFlagService`.
- Expandir `KillSwitch` global.
- Implementar `GracefulShutdown`: no acepta tareas nuevas, cancela tareas no criticas, persiste estado y cierra procesos.
- Implementar `RiskClassifier` para acciones: read, write, execute, external_send, delete, credential_use.
- Expandir `ApprovalQueue`.
- Implementar `CapabilityGate` por herramienta, usuario, workspace y modo.
- Implementar primer sandbox simple para herramientas locales.
- Implementar politica de secretos: nunca mostrar, persistir o enviar secretos sin permiso explicito.
- Implementar apagado selectivo por feature flag, herramienta, backend, workspace o perfil de razonamiento.
- Implementar modo contencion: read-only, sin memoria nueva, sin conectores externos y con logging ampliado.

Criterios de aceptacion:

- Una accion riesgosa queda en `waiting_approval`.
- Kill Switch bloquea nuevas ejecuciones.
- Incident Mode deja el sistema en modo solo lectura.
- Todas las decisiones de politica quedan auditadas.
- Se puede apagar una capacidad especifica sin apagar toda la plataforma.
- Se puede explicar que feature flag o policy bloqueo una accion.

### Fase 5 - Observabilidad y auditoria

Objetivo: ampliar la observabilidad minima del kernel hasta convertirla en trazabilidad operativa completa.

Componentes cubiertos:

- Observability
- Logs
- Traces
- Audit Trail
- Decision Records
- Metrics
- Cost / Usage Reporting
- Incident Reports / Postmortems
- Tool Call Audit

Tareas:

- Expandir logging estructurado.
- Expandir `TraceId` por tarea, subagente, modelo y herramienta.
- Registrar decisiones del router, policy engine, herramientas, HITL y memoria.
- Registrar costos estimados: tokens, tiempo, CPU/GPU, llamadas.
- Crear formato de postmortem para errores o incidentes.
- Implementar panel o comando de monitoreo de procesos/tareas activas.
- Implementar export de trazas para debug y auditoria.
- Implementar eventos de shutdown, feature flag change, approval decision y policy denial.

Criterios de aceptacion:

- Se puede reconstruir una tarea completa desde eventos.
- Cada tool call tiene input, output, permisos y side effects.
- Cada decision importante tiene reason record.
- Se puede monitorear el sistema desde el inicio hasta shutdown.
- Se puede detectar que componente esta activo, bloqueado, apagado o fallando.

### Fase 6 - Context Engineering

Objetivo: controlar que contexto entra al modelo y por que.

Componentes cubiertos:

- Context Engineering Layer
- Project Profiles
- Repo Maps
- Document Maps
- Compression / Compaction
- Event-driven Reminders
- Source Adapters
- Context Budgeter

Tareas:

- Crear `ProjectProfile`: reglas, estilo, objetivos, restricciones, paths importantes.
- Crear `RepoMap` para proyectos de codigo.
- Crear `DocumentMap` para documentos y colecciones.
- Crear `ContextBudgeter` para priorizar contexto segun ventana disponible.
- Crear compaction de conversaciones y tareas largas.
- Crear reminders basados en eventos: fechas, bloqueos, decisiones pendientes.
- Crear source adapters para filesystem, repos, docs y APIs.

Criterios de aceptacion:

- El sistema puede explicar por que incluyo o excluyo contexto.
- Una tarea larga puede compactarse sin perder decisiones clave.
- Un workspace tiene perfil persistente.

### Fase 7 - RAG y conocimiento local

Objetivo: dar conocimiento local confiable al agente.

Componentes cubiertos:

- Knowledge / RAG System
- Ingestion
- Cleaning
- Chunking
- Embeddings
- Vector / Hybrid Index
- Retriever
- Reranker
- Citations / Provenance
- Query Router / Retriever Router
- Graph RAG / Structured Retrieval
- Retrieval Test Harness
- Evidence Ledger
- Source Adapters read-only

Tareas:

- Implementar `EvidenceLedger` minimo antes de indexar conocimiento.
- Implementar source adapters read-only para filesystem, repositorios y documentos.
- Implementar pipeline de ingesta.
- Implementar cleaning por tipo de documento.
- Implementar chunking configurable.
- Implementar embeddings locales o reemplazables.
- Implementar indice vectorial inicial.
- Agregar busqueda hibrida cuando sea necesario.
- Implementar reranker opcional.
- Guardar citas, provenance, hash de fuente, version de chunk y relacion con Evidence Ledger.
- Implementar invalidacion/reindexado cuando cambia una fuente.
- Implementar borrado logico y fisico de evidencia indexada segun politica.
- Crear pruebas con preguntas esperadas y fuentes correctas.

Criterios de aceptacion:

- El agente recupera documentos relevantes con trazabilidad.
- Las respuestas muestran fuentes cuando usan conocimiento local.
- Hay evaluaciones de precision de recuperacion.
- Cada chunk indexado puede rastrearse a una fuente original.
- Se puede borrar o invalidar una fuente y actualizar el indice.
- RAG nunca se considera fuente primaria: referencia evidencia registrada.

### Fase 8 - Sistema de memoria

Objetivo: pasar de historial plano a memoria por capas.

Componentes cubiertos:

- Memory System
- Working Memory
- Episodic Memory
- Semantic Memory
- Procedural Memory
- Reflective Memory
- Continuity / Biography
- Sensory Context / Proprioception
- Forgetting / Compaction
- Reconstructive Recall
- Evidence Ledger

Tareas:

- Implementar working memory por tarea.
- Implementar episodic memory como eventos significativos.
- Implementar semantic memory como hechos estables.
- Implementar procedural memory como skills, rutinas y recetas.
- Implementar reflective memory: lecciones aprendidas, postmortems, preferencias.
- Implementar biografia del agente: continuidad, objetivos persistentes, historia de decisiones.
- Implementar sensory/proprioception context: estado del sistema, recursos, herramientas activas, entorno actual.
- Implementar olvido: expiracion, compactacion, degradacion de confianza, archivado.
- Implementar recall reconstructivo: reconstruir recuerdos a partir de evidencia, contexto y prioridad.
- Separar estrictamente memoria interpretada de evidencia primaria.
- Versionar recuerdos y permitir migraciones de schema.
- Implementar borrado/retencion por tipo de memoria y workspace.
- Registrar provenance de cada recuerdo: de que evidencia, decision o interaccion nacio.

Criterios de aceptacion:

- La memoria distingue tipos.
- El agente puede olvidar o compactar sin borrar evidencia critica.
- El recall muestra fuente, confianza e interpretacion.
- Un recuerdo puede ser reconstruido o descartado segun evidencia.
- Un recuerdo puede ser exportado, migrado, invalidado o borrado segun politica.

### Fase 9 - Tool Runtime e integraciones

Objetivo: permitir acciones reales de forma controlada.

Componentes cubiertos:

- Tool Runtime
- Skill Registry
- Filesystem
- Code Execution
- Web / Browser
- Computer / Browser Runtime
- Documents / Sheets / Media
- Tool Sandbox Boundary
- Integration Hub
- MCP
- APIs
- OAuth
- Credentials
- Channel Adapters
- App Connectors
- Connector Registry / Health

Tareas:

- Crear `ToolRegistry`.
- Crear contrato de herramienta.
- Implementar filesystem read-only primero.
- Implementar escritura bajo aprobacion.
- Implementar code execution en sandbox.
- Implementar web/browser como herramienta separada.
- Implementar computer/browser runtime como subsistema auditado.
- Implementar documentos y media como herramientas especializadas.
- Crear Integration Hub con MCP, APIs, OAuth, credenciales, channel adapters y app connectors.
- Monitorear salud de conectores.

Criterios de aceptacion:

- Ninguna herramienta se ejecuta sin permiso declarado.
- Todas las acciones quedan auditadas.
- El sistema puede desactivar una herramienta via feature flag.

### Fase 10 - Orquestador maestro y subagentes

Objetivo: convertir objetivos en planes, subtareas y ejecuciones coordinadas.

Componentes cubiertos:

- Master Orchestrator
- Self Model
- Capacities
- Limits
- Current State
- Known Risks
- Subagent Factory
- Subagent Contracts
- Role
- Budget
- Tool Limits
- Deadline
- Success Criteria
- Research Agent
- Code Agent
- Critic / Verifier Agent
- Domain Agent on Demand
- Termination Conditions / Handback Protocol
- Agent Fleet Manager
- Sessions
- Workspaces
- Fork / Resume / Share
- Lifecycle
- Budgets
- Concurrency
- Agent Health / Heartbeats
- Task Queue / Dispatch

Precondicion:

- Antes de habilitar subagentes complejos, deben existir policy minima, observabilidad, contratos de herramienta, Evidence Ledger y checks cognitivos simples para planes riesgosos.

Tareas:

- Implementar `MasterOrchestrator`.
- Implementar `SelfModel` con capacidades, limites, estado y riesgos.
- Implementar `Plan` con pasos y dependencias.
- Implementar `SubagentFactory`.
- Crear contratos de subagente.
- Implementar subagentes iniciales: research, code, critic/verifier, domain generic.
- Implementar condiciones de terminacion y handback.
- Implementar Agent Fleet Manager para sesiones, workspaces, lifecycle, budgets, concurrencia, health y dispatch.
- Implementar madurez de capacidades por subagente: experimental, guarded, trusted, autonomous.
- Implementar limites por subagente: herramientas, presupuesto, tiempo, memoria accesible y criterio de exito.

Criterios de aceptacion:

- El orquestador crea un plan simple.
- Puede crear un subagente con contrato.
- Puede cancelar subagentes.
- Puede sintetizar resultados parciales.
- Puede explicar estado, limites y riesgos actuales.
- Ningun subagente puede operar sin contrato, trace_id, presupuesto y limites.
- El orquestador puede apagar o degradar un subagente sin perder audit trail.

### Fase 11 - Capa de seguridad cognitiva

Objetivo: introducir pensamiento critico artificial antes de aumentar autonomia.

Componentes cubiertos:

- Cognitive Safety Layer
- Detractor Agent
- Premortem Agent
- Adversarial Self-Test
- Uncertainty Estimator
- Contradiction Detector
- Goal Drift Monitor
- Evidence Grounder
- Second Opinion Router
- Ethical / Harm Review
- Self-Consistency Checker
- Postmortem Learner
- Critical Thinking Protocol
- Metacognition Gates

Tareas:

- Implementar Detractor Agent para detectar fallas y supuestos debiles.
- Implementar Premortem Agent antes de acciones riesgosas.
- Implementar Adversarial Self-Test en sandbox.
- Implementar estimacion de incertidumbre y etiquetas: hecho, inferencia, supuesto, opinion, desconocido.
- Implementar detector de contradicciones con objetivo, memoria, politicas y evidencia.
- Implementar Goal Drift Monitor.
- Implementar Evidence Grounder.
- Implementar Second Opinion Router para riesgo alto.
- Implementar Ethical / Harm Review centrado en dano practico.
- Implementar Self-Consistency Checker.
- Implementar Postmortem Learner.
- Definir Metacognition Gates: cuando dudar, frenar, verificar o pedir HITL.

Criterios de aceptacion:

- Una propuesta riesgosa es criticada antes de ejecutarse.
- El agente distingue evidencia de suposicion.
- El sistema detecta desviacion de objetivo.
- Los errores generan postmortem y posibles evals nuevos.

### Fase 12 - Workflow y automatizacion

Objetivo: pasar de tareas manuales a procesos persistentes y recurrentes.

Componentes cubiertos:

- Workflow & Automation Engine
- Visual Flows
- Triggers
- Schedules
- Event Bus
- Recurring Jobs
- Structured Workflow Engine
- Flow Studio / Playground

Tareas:

- Crear workflow definition.
- Implementar triggers por evento.
- Implementar schedules.
- Implementar recurring jobs.
- Conectar workflows al Event Bus.
- Crear modo playground textual antes de UI visual.
- Diseñar Flow Studio futuro.

Criterios de aceptacion:

- Se puede definir un flujo recurrente.
- Un evento puede disparar una tarea.
- Una tarea programada respeta politicas, logs y HITL.

### Fase 13 - Skills, plugins y aprendizaje operativo

Objetivo: convertir capacidades en unidades instalables, auditables y reutilizables.

Componentes cubiertos:

- Skill & Plugin Supply Chain
- Marketplace
- Signatures
- Provenance
- Versioning
- Permissions
- Security Scanning
- Skill Learning / Consolidation

Tareas:

- Definir formato de skill.
- Definir manifest: nombre, version, permisos, herramientas, riesgos, tests.
- Implementar versioning.
- Implementar provenance.
- Implementar firmas opcionales.
- Implementar security scanning basico.
- Crear marketplace local.
- Implementar Skill Learning: una experiencia validada puede convertirse en skill candidata.

Criterios de aceptacion:

- Una skill puede instalarse, deshabilitarse y versionarse.
- Una skill declara permisos.
- Una skill riesgosa requiere aprobacion.
- Una skill generada por el agente queda como candidata, no activa automaticamente.

### Fase 14 - EvalOps Lab

Objetivo: construir confianza progresiva con pruebas repetibles.

Componentes cubiertos:

- EvalOps Lab
- Datasets
- Graders
- Gates
- Trajectories
- Regression Suites
- Leaderboards
- Behavioral / RAG / Security / Memory / Tool-use / Autonomy Evals

Tareas:

- Crear datasets de tareas esperadas.
- Crear graders simples.
- Crear gates que bloquean releases.
- Guardar trajectories completas.
- Crear regression suites.
- Crear leaderboard interno por modelo, router, skill y workflow.
- Crear evals de comportamiento, RAG, seguridad, memoria, tool-use y autonomia.

Criterios de aceptacion:

- Cada bug importante genera una regression.
- Cada fase critica tiene al menos una eval.
- Una version no pasa a release si rompe gates minimos.

### Fase 15 - Superficies de producto extendidas

Objetivo: convertir la plataforma en algo usable por distintos canales.

Componentes cubiertos:

- Chat
- CLI
- Desktop
- Web
- Mobile
- IDE
- Browser Extension
- Messaging Channels
- API / SDK
- Embedded Widgets

Tareas:

- Mantener CLI como superficie tecnica principal.
- Crear web UI para sesiones, tareas, logs y aprobaciones.
- Crear desktop launcher.
- Crear IDE extension si el foco codigo toma prioridad.
- Crear browser extension si el foco web/workflows toma prioridad.
- Crear channel adapters para mensajeria.
- Publicar API/SDK estable.

Criterios de aceptacion:

- Todas las superficies usan la misma API.
- Ninguna superficie saltea Governance.
- HITL tiene UX clara.

### Fase 16 - Deployment y administracion

Objetivo: instalar, operar y administrar la plataforma.

Componentes cubiertos:

- Deployment & Admin
- Installer
- Launcher
- Self-host
- Multi-user
- RBAC
- SSO
- Usage Reporting
- Air-gapped Mode
- Backup / Restore
- Admin Console
- Policy Management

Tareas:

- Crear installer local.
- Crear launcher.
- Crear modo self-host.
- Preparar multi-user.
- Implementar RBAC.
- Preparar SSO futuro.
- Implementar usage reporting.
- Diseñar modo air-gapped.
- Implementar backup/restore.
- Crear admin console.
- Crear policy management.

Criterios de aceptacion:

- La plataforma se instala de forma reproducible.
- Se puede exportar/importar configuracion y memoria.
- Se puede administrar politicas desde una consola.

### Fase 17 - Hardening y release funcional

Objetivo: llegar a una version funcional, segura y util.

Tareas:

- Ejecutar regression suite completa.
- Probar Kill Switch, Incident Mode y Graceful Shutdown.
- Probar permisos y HITL.
- Probar cambio de modelo en runtime.
- Probar memoria y olvido.
- Probar RAG con fuentes citadas.
- Probar subagentes y terminacion.
- Probar logs, traces y audit trail.
- Probar backup/restore.

Criterios de aceptacion:

- Un usuario puede instalar, iniciar, usar, pausar y apagar la plataforma.
- El sistema puede resolver tareas simples con modelo local.
- El sistema pide aprobacion para acciones sensibles.
- El sistema registra lo que hizo y por que.
- El sistema puede recuperar contexto local y citar fuentes.
- El sistema puede crear subagentes bajo contrato.
- El sistema puede fallar de forma contenida.

## 6. Camino evolutivo por entregables

No fijar todavia versiones ni MVP definitivos. El objetivo es avanzar por productos pequenos, verificables y acumulativos, sin perder componentes del diseno completo.

```text
Entregable A - Kernel gobernable
  TaskState event-sourced + EventBus + trace_id + logs + policy minima + evals iniciales

Entregable B - Inferencia reemplazable
  llama.cpp backend + Model Router + Model Registry + ReasoningProfile ejecutable

Entregable C - Superficie tecnica minima
  CLI/API pasando por Governance + estado visible + audit trail

Entregable D - Herramientas read-only y evidencia
  Tool Runtime minimo + filesystem/repo/doc source adapters + Evidence Ledger

Entregable E - RAG con provenance
  ingesta + cleaning + chunking + embeddings + retrieval + citas + borrado/invalidation

Entregable F - Memoria inicial verificable
  working/episodic/semantic minima + forgetting + recall con evidencia

Entregable G - Orquestador y critica simple
  Master Orchestrator + plan + evidence check + contradiction check + premortem

Entregable H - Subagentes controlados
  Subagent Factory + contratos + budgets + termination + critic/research agent

Entregable I - Producto operable
  Approval Queue UI + monitoreo + feature flags + graceful shutdown + backup/restore

Entregable J - Plataforma extensible
  workflows + skills/plugins + integration hub + deployment/admin
```

### 6.1 Como evolucionar sin perder nada

- Mantener una matriz de trazabilidad entre draw.io, documento, ADRs, issues, tests y modulos implementados.
- Cada entregable debe sumar una capacidad sin romper contratos anteriores.
- Cada contrato persistido debe tener `schema_version` y migracion.
- Cada capacidad nueva debe declarar madurez: experimental, guarded, trusted o autonomous.
- Cada capacidad debe tener feature flag y criterio de apagado.
- Cada accion relevante debe emitir evento y ser reconstruible por replay o audit trail.
- Cada dato persistente debe tener provenance, retencion, export/import y borrado definido.
- Cada bug importante debe transformarse en regression test o eval.
- Cada cambio de arquitectura debe quedar en ADR.
- Cada release interno debe correr una checklist: policy, observability, evals, migration, backup, rollback y docs.
- Ningun modulo se considera completo solo por existir: debe poder ser monitoreado, apagado y explicado.

## 7. Conexiones criticas entre modulos

- Product Surface solo habla con Governance.
- Governance decide si una tarea entra, se bloquea, se pausa o escala a HITL.
- Master Orchestrator nunca ejecuta herramientas directamente; usa Tool Runtime.
- Tool Runtime consulta Policy Engine antes de cada accion.
- Model Router consulta Model Registry y Reasoning Controller antes de invocar modelos.
- Reasoning Controller traduce perfiles de razonamiento en limites ejecutables.
- Context Engineering decide que contexto entra en cada llamada de modelo.
- Evidence Ledger registra evidencia primaria para RAG, memoria, tool calls y decisiones.
- Memory System almacena interpretaciones solo mediante contratos, provenance y politicas de retencion.
- RAG recupera evidencia registrada, no verdades absolutas.
- Cognitive Safety puede frenar, cuestionar o pedir segunda opinion.
- EvalOps define gates que bloquean releases o capacidades.
- Observability recibe eventos de todos los modulos.
- Control Plane puede apagar, pausar o degradar cualquier subsistema.

## 8. Primer backlog hiper especifico

1. Crear repo y estructura `docs/`, `src/`, `tests/`, `evals/`, `configs/`, `data/`.
2. Agregar `docs/architecture.md` basado en este documento.
3. Mantener `docs/adr/README.md` como indice canonico de decisiones.
4. Mantener `docs/adr/0012-event-sourcing.md` como decision de event sourcing inicial.
5. Mantener `docs/adr/0013-governance-initial-controls.md` como decision de gobierno inicial.
6. Mantener `docs/adr/0014-observability-from-kernel.md` como decision de observabilidad minima.
7. Mantener `docs/adr/0015-cli-and-jsonl-event-log.md` como decision de CLI real y JSONL minimo.
8. Mantener `docs/adr/0016-local-api-adapter.md` como decision de API local.
9. Mantener `docs/adr/0017-modular-persistence.md` como decision de persistencia modular inicial.
10. Agregar ADR futuro `0018-evidence-ledger.md`.
11. Agregar ADR futuro `0019-state-machine-kernel.md` si los ejes de estado requieren decision formal adicional.
12. Mantener `docs/model-backends.md` y `docs/adr/0009-model-backend-and-providers.md` como decision de modelos reemplazables.
13. Agregar `docs/configuration.md` con config/env vars, precedencia, perfiles, paths, secrets y limites.
14. Agregar `docs/testing-and-evals.md` con niveles `none`, `smoke`, `unit`, `contract`, `safety`, `integration`, `eval` y `full`.
15. Agregar `docs/schemas.md` con eventos, tareas, tool calls, evidencia, memoria, state machine y perfiles de razonamiento.
16. Agregar `docs/data-lifecycle.md` con versionado, borrado, migraciones, retencion, backup/restore y provenance.
17. Implementar `StateMachineKernel`.
18. Implementar `TaskState` event-sourced.
19. Implementar `TransitionGuard`.
20. Mantener `DoomLoopGuard` minimo.
21. Implementar `EventBus`.
22. Implementar `SessionStore`.
23. Implementar logs estructurados con `trace_id`.
24. Mantener audit trail minimo por eventos del kernel.
25. Mantener `PolicyEngine` minimo con read/write/execute/network/delete/send/credentials.
26. Mantener `ApprovalQueue` en memoria.
27. Mantener `KillSwitch`.
28. Mantener `ResourceMonitor` basico para procesos/tareas.
29. Crear eval: una tarea se reconstruye por replay tras reinicio.
30. Crear eval: una accion de escritura debe pedir aprobacion.
31. Crear eval: transicion invalida emite `state_transition_denied`.
32. Crear eval: doom loop repetible termina en `doom_loop_detected`.
33. Crear eval: Kill Switch bloquea nueva ejecucion.
34. Implementar `ModelBackend` interface.
35. Implementar `LlamaCppBackend`.
36. Implementar `ModelRegistry`.
37. Implementar `ReasoningProfile` ejecutable.
38. Implementar `RoutingPolicy` minima.
39. Crear eval: el router registra modelo, perfil, presupuesto, riesgo y razon de seleccion.
40. Implementar CLI de tareas pasando por Governance.
41. Mantener CLI real pasando por Governance y `.nox/events.jsonl`.
42. Mantener API local pasando por Governance y `.nox/events.jsonl`.
43. Implementar primer tool/source adapter: filesystem read-only con provenance.
44. Implementar `EvidenceLedger` minimo.

## 9. Riesgos principales

- Construir demasiada UI antes de tener kernel solido.
- Dar herramientas peligrosas antes de Policy Engine y audit trail.
- Confundir RAG con memoria.
- Confundir memoria con historial sin limpieza.
- Permitir subagentes sin contrato.
- No registrar decisiones internas.
- No escribir evals hasta despues de fallar.
- Acoplar el orquestador a un modelo concreto.
- Construir plugins sin supply chain ni permisos.
- Pensar autonomia como ausencia de supervision.
- Creer que el sistema es gobernable porque el documento lo dice, sin pruebas de bloqueo, replay y apagado selectivo.
- Persistir memoria, RAG o logs sin versionado, provenance, borrado ni migraciones.
- Tratar `ReasoningProfile` como etiquetas en vez de politicas ejecutables.
- Permitir evolucionar modulos sin matriz de trazabilidad, ADRs y regression tests.

## 10. Definicion de terminado para la primera version funcional

La primera version funcional existe cuando:

- Corre localmente.
- Usa al menos un modelo via `llama.cpp`.
- Permite cambiar modelo mediante registry/router.
- Recibe tareas desde CLI o API.
- Tiene Policy Engine, HITL y Kill Switch.
- Puede leer conocimiento local con RAG basico.
- Tiene memoria minima persistente.
- Usa al menos una herramienta bajo permisos.
- Crea al menos un subagente bajo contrato.
- Tiene logs, traces y audit trail.
- Tiene evals minimas de seguridad, RAG, memoria y tool-use.
- Puede apagarse gracefully.
- Puede reconstruir una tarea por replay de eventos.
- Puede mostrar provenance de evidencia usada por RAG o memoria.
- Puede borrar/invalidar evidencia o memoria segun politica.
- Puede desactivar una capacidad sin apagar toda la plataforma.
- Tiene migraciones de schema para datos persistentes.

## 11. Trazabilidad de componentes del drawio

Esta lista asegura que cada nodo del diagrama aparece contemplado en el plan.

- Product Surface Layer: Usuario / Objetivo, Chat, CLI, Desktop, Web, Mobile, IDE, Browser Extension, Messaging Channels, API / SDK, Embedded Widgets.
- Governance Layer: Control Plane, Policy & Security, Cognitive Core, EvalOps Lab, Observability, Deployment & Admin.
- Control Plane: Kill Switch, Graceful Shutdown, Feature Flags, Resource Governor, Resource Monitor, Incident Mode, Rollback / Checkpoints, Capability Gates, Selective Shutdown, State Machine Kernel, Transition Guards, Doom Loop Guard.
- Policy & Security: Policy Engine, Security Layer, Human-in-the-Loop, Sandbox, Permissions / Capability Gates, Prompt Injection Defense, Secrets Policy, Risk Classification, Approval Queue.
- Cognitive Core: Master Orchestrator, Self Model, Capacities, Limits, Current State, Known Risks, Configuration / Environment Contract.
- Model Layer: Model Router, Reasoning Controller, Model Registry, llama.cpp, vLLM futuro, Ollama opcional, Cloud Models opcionales, Ejecutor propio futuro, Fast / Direct, Normal, Deep Reasoning, Multi-Agent Verified, Maximum / Formal Eval, Routing Policy.
- Cognitive Safety Layer: Detractor Agent, Premortem Agent, Adversarial Self-Test, Uncertainty Estimator, Contradiction Detector, Goal Drift Monitor, Evidence Grounder, Second Opinion Router, Ethical / Harm Review, Self-Consistency Checker, Postmortem Learner, Critical Thinking Protocol, Metacognition Gates.
- Agent Fleet Manager: Sessions, Workspaces, Fork / Resume / Share, Lifecycle, Budgets, Concurrency, Agent Health / Heartbeats, Task Queue / Dispatch.
- Workflow & Automation Engine: Visual Flows, Triggers, Schedules, Event Bus, Recurring Jobs, Structured Workflow Engine, Flow Studio / Playground.
- Subagent Factory: Subagent Contracts, Role, Budget, Tool Limits, Deadline, Success Criteria, Research Agent, Code Agent, Critic / Verifier Agent, Domain Agent on Demand, Termination Conditions / Handback Protocol.
- Context Engineering Layer: Project Profiles, Repo Maps, Document Maps, Compression / Compaction, Event-driven Reminders, Source Adapters, Read-only Source Adapters, Context Budgeter.
- Memory System: Working Memory, Episodic Memory, Semantic Memory, Procedural Memory, Reflective Memory, Continuity / Biography, Sensory Context / Proprioception, Forgetting / Compaction, Reconstructive Recall, Memory Lifecycle.
- Knowledge / RAG System: Ingestion, Cleaning, Chunking, Embeddings, Vector / Hybrid Index, Retriever, Reranker, Citations / Provenance, Query Router / Retriever Router, Graph RAG / Structured Retrieval, Retrieval Test Harness.
- Tool Runtime: Skill Registry, Filesystem, Code Execution, Web / Browser, Computer / Browser Runtime, Documents / Sheets / Media, Tool Sandbox Boundary, Tool Call Audit.
- Integration Hub: MCP, APIs, OAuth, Credentials, Channel Adapters, App Connectors, Connector Registry / Health.
- Skill & Plugin Supply Chain: Marketplace, Signatures, Provenance, Versioning, Permissions, Security Scanning, Skill Learning / Consolidation.
- EvalOps Lab: Datasets, Graders, Gates, Trajectories, Regression Suites, Leaderboards, Behavioral / RAG / Security / Memory / Tool-use / Autonomy Evals.
- Observability: Logs, Traces, Audit Trail, Decision Records, Metrics, Cost / Usage Reporting, Incident Reports / Postmortems, Incident Reports / Postmortems / Doom Loop Alerts, Event Replay / State Reconstruction, Schema Versions / Migrations.
- Deployment & Admin: Installer, Launcher, Self-host, Multi-user, RBAC, SSO, Usage Reporting, Air-gapped Mode, Backup / Restore, Admin Console, Policy Management.

## 12. Fuentes y referencias

Esta seccion consolida fuentes usadas durante la conversacion y referencias utiles para validar decisiones futuras. Priorizar fuentes primarias, documentacion oficial, papers y repositorios mantenidos.

### 12.1 Historia de computacion e inteligencia artificial

- [Computer History Museum - Timeline](https://www.computerhistory.org/timeline/): hitos de computacion, ENIAC, ARPANET, UNIX, microprocesadores y sistemas historicos.
- [IBM - History of artificial intelligence](https://www.ibm.com/think/topics/history-of-artificial-intelligence): resumen historico de IA, Dartmouth, sistemas expertos, redes neuronales y deep learning.
- [Stanford HAI - AI Index Report](https://hai.stanford.edu/ai-index): reportes anuales sobre estado de IA, tendencias, benchmarks, inversiones, riesgos y adopcion.
- [Alan Turing - Computing Machinery and Intelligence](https://academic.oup.com/mind/article/LIX/236/433/986238): texto fundacional del test de Turing.
- [McCulloch & Pitts - A Logical Calculus of the Ideas Immanent in Nervous Activity](https://link.springer.com/article/10.1007/BF02478259): base historica de neuronas artificiales.

### 12.2 Papers fundacionales para modelos modernos, agentes y herramientas

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762): paper del Transformer.
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401): paper original de RAG.
- [WebGPT: Browser-assisted question-answering with human feedback](https://openai.com/index/webgpt/): modelo usando navegacion y fuentes web.
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629): patron razonar-actuar-observar.
- [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761): uso aprendido de herramientas por modelos.
- [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442): agentes con memoria, reflexion y planificacion.
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291): agente con skill library y aprendizaje continuo en Minecraft.
- [AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation](https://arxiv.org/abs/2308.08155): framework y patron multiagente conversacional.
- [Do As I Can, Not As I Say: Grounding Language in Robotic Affordances](https://arxiv.org/abs/2204.01691): SayCan, grounding de modelos de lenguaje en acciones posibles.
- [ACT-1: Transformer for Actions](https://www.adept.ai/blog/act-1): modelo orientado a usar interfaces digitales.

### 12.3 Modelos, agentes y herramientas modernas de OpenAI

- [Hello GPT-4o](https://openai.com/index/hello-gpt-4o/): modelo multimodal en tiempo real.
- [Introducing OpenAI o1-preview](https://openai.com/index/introducing-openai-o1-preview/): modelos orientados a razonamiento.
- [Introducing GPT-5](https://openai.com/index/introducing-gpt-5/): sistema con enrutamiento entre respuesta rapida y razonamiento profundo.
- [Introducing GPT-5.5](https://openai.com/index/introducing-gpt-5-5/): referencia de frontera para trabajo agente, codificacion y herramientas.
- [ChatGPT plugins](https://openai.com/index/chatgpt-plugins/): hito temprano de conexion entre LLMs y servicios externos.
- [Function calling and other API updates](https://openai.com/index/function-calling-and-other-api-updates/): funcion calling estructurado.
- [New tools for building agents](https://openai.com/index/new-tools-for-building-agents/): Responses API, herramientas y Agents SDK.
- [Introducing Operator](https://openai.com/index/introducing-operator/): agente con navegador para tareas web.
- [Introducing deep research](https://openai.com/index/introducing-deep-research/): investigacion multi-paso asistida por agente.
- [Introducing ChatGPT agent](https://openai.com/index/introducing-chatgpt-agent/): puente entre investigacion y accion.
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/): SDK de agentes, handoffs, tools, tracing y guardrails.
- [OpenAI Evals](https://github.com/openai/evals): referencia de evaluaciones automatizadas.

### 12.4 Otros laboratorios y modelos frontera

- [Google DeepMind - Gemini](https://deepmind.google/technologies/gemini/): familia Gemini y modelos multimodales.
- [Anthropic - Model Context Protocol](https://www.anthropic.com/news/model-context-protocol): anuncio original de MCP.
- [Model Context Protocol - Introduction](https://modelcontextprotocol.io/introduction): documentacion del protocolo.
- [Model Context Protocol - Specification](https://modelcontextprotocol.io/specification): especificacion para conectar aplicaciones IA con datos y herramientas.
- [Anthropic - Computer use](https://www.anthropic.com/news/3-5-models-and-computer-use): hito de uso de computadora por modelo.
- [Meta - Llama models](https://www.llama.com/): modelos Llama y ecosistema open-weight.
- [Google - Gemma](https://ai.google.dev/gemma): familia Gemma.
- [Mistral AI - Docs](https://docs.mistral.ai/): modelos y plataforma Mistral.
- [DeepSeek](https://www.deepseek.com/): modelos DeepSeek y referencias de razonamiento/codigo.

### 12.5 Inferencia local y backends de modelos

- [llama.cpp](https://github.com/ggml-org/llama.cpp): runtime local C/C++ y ecosistema GGUF.
- [llama.cpp server README](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md): servidor compatible con APIs de chat/completions.
- [GGUF format](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md): formato de modelos usado por llama.cpp.
- [Ollama](https://ollama.com/): gestor/runtime local para modelos.
- [Ollama API docs](https://github.com/ollama/ollama/blob/main/docs/api.md): API local de Ollama.
- [LM Studio](https://lmstudio.ai/): app local para ejecutar modelos.
- [LM Studio Docs](https://lmstudio.ai/docs): documentacion de servidor local y API.
- [vLLM](https://docs.vllm.ai/en/latest/): serving de alto rendimiento.
- [vLLM OpenAI-compatible server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html): servidor compatible con API estilo OpenAI.
- [Hugging Face Hub](https://huggingface.co/docs/hub/index): repositorio de modelos, datasets y Spaces.
- [Transformers](https://huggingface.co/docs/transformers/index): libreria de modelos.
- [Text Generation Inference](https://huggingface.co/docs/text-generation-inference/index): serving de modelos en produccion.

### 12.6 Orquestacion de agentes, workflows y frameworks

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview): agentes durables, estado, HITL y workflows.
- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents): agentes construidos sobre LangGraph.
- [LlamaIndex](https://developers.llamaindex.ai/python/framework/): RAG, agentes, query engines, retrievers y herramientas.
- [LlamaIndex agents](https://developers.llamaindex.ai/python/framework/understanding/agent/): conceptos de agentes.
- [Microsoft AutoGen](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html): multiagentes y conversaciones coordinadas.
- [Microsoft AutoGen termination](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html): condiciones de terminacion combinables, handoff, timeout, tokens, max messages y control externo.
- [CrewAI](https://docs.crewai.com/introduction): crews, flows, agentes y automatizacion.
- [Llama Stack](https://llama-stack.readthedocs.io/en/latest/): APIs para inference, agents, tools, safety, memory y evals.
- [OpenHands](https://docs.openhands.dev/): agente de software engineering, sandbox y runtime.
- [OpenHands AgentState legacy](https://raw.githubusercontent.com/OpenHands/OpenHands/main/openhands/core/schema/agent.py): referencia historica de estados de agente como loading, running, paused, finished, error y rate_limited.
- [SWE-agent](https://swe-agent.com/latest/): agentes para tareas de software engineering y trayectorias reproducibles.
- [Aider](https://aider.chat/docs/): pair programming con LLMs, repo map y flujos Git.
- [Aider chat modes](https://aider.chat/docs/usage/modes.html): modos code, ask, architect y help.
- [Cline](https://cline.bot/): agente de codigo en VS Code con HITL, MCP y checkpoints.
- [Cline Plan & Act](https://docs.cline.bot/core-workflows/plan-and-act): separacion de modo plan, modo act, deep planning y modelos distintos por modo.
- [Cline Checkpoints](https://docs.cline.bot/core-workflows/checkpoints): snapshots por tool use mediante shadow git y restores parciales.
- [Cline Subagents](https://docs.cline.bot/features/subagents): subagentes paralelos read-only con contexto y presupuesto propio.
- [OpenCode](https://opencode.ai/): agente de codigo open source en terminal/IDE.
- [OpenCode agents](https://opencode.ai/docs/agents): agentes Build, Plan, General, Explore, Scout y agentes ocultos de compaction/title/summary.
- [OpenCode permissions](https://opencode.ai/docs/permissions): decisiones allow, ask, deny y auto mode.
- [Claude Code permissions](https://code.claude.com/docs/en/permissions): modos default, acceptEdits, plan, auto, dontAsk y bypassPermissions; reglas allow/ask/deny.
- [Claude Code hooks](https://code.claude.com/docs/en/hooks): eventos de ciclo de vida, tool use, subagentes, tareas, compaction y session end.
- [Claude Code checkpointing](https://code.claude.com/docs/en/checkpointing): checkpoints por prompt, rewind y restore de codigo/conversacion.
- [Codex approvals and security](https://developers.openai.com/codex/agent-approvals-security): sandbox, approval policy, read-only/workspace-write y aprobaciones.
- [Codex hooks](https://developers.openai.com/codex/hooks): eventos PreToolUse, PermissionRequest, PostToolUse, PreCompact, SubagentStart y Stop.
- [Codex subagents](https://developers.openai.com/codex/subagents): subagentes con modelo, reasoning effort, sandbox y limites de concurrencia/profundidad.
- [Open Interpreter](https://docs.openinterpreter.com/getting-started/introduction): agentes que operan computadora/codigo local.
- [Browser Use](https://docs.browser-use.com/): automatizacion de navegador para agentes.

### 12.7 Plataformas open-source de producto, workflows y asistentes locales

- [Dify](https://docs.dify.ai/en/introduction): plataforma LLM app, workflows, agentes y knowledge bases.
- [Flowise](https://docs.flowiseai.com/): builder visual low-code para LLM apps.
- [Langflow](https://docs.langflow.org/): editor visual para flows, agentes y componentes.
- [AnythingLLM](https://docs.anythingllm.com/): asistente local/self-host con knowledge, agents y workspaces.
- [Khoj](https://docs.khoj.dev/): second brain local/self-host para documentos y notas.
- [Letta](https://docs.letta.com/): agentes memory-first, subagentes y memoria persistente.
- [Agent Zero](https://www.agent-zero.ai/): plataforma agente local con herramientas, docker y plugins.
- [AutoGPT Platform](https://docs.agpt.co/): agentes continuos, builder, marketplace y automatizaciones.

### 12.8 RAG, embeddings, busqueda vectorial y retrieval

- [FAISS](https://faiss.ai/): busqueda vectorial eficiente.
- [Qdrant](https://qdrant.tech/documentation/): vector database.
- [Chroma](https://docs.trychroma.com/): base vectorial local/flexible.
- [LanceDB](https://lancedb.github.io/lancedb/): vector database embebible.
- [Weaviate](https://weaviate.io/developers/weaviate): vector database y RAG.
- [Milvus](https://milvus.io/docs): vector database escalable.
- [Elasticsearch BM25](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-similarity.html): busqueda lexical/BM25 para retrieval hibrido.
- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/): GraphRAG y retrieval estructurado.
- [Ragas](https://docs.ragas.io/): evaluacion de RAG.
- [TruLens](https://www.trulens.org/): evaluacion y observabilidad de aplicaciones LLM/RAG.

### 12.9 Memoria, agentes persistentes y conocimiento personal

- [Letta memory concepts](https://docs.letta.com/concepts/memory): memoria persistente para agentes.
- [MemGPT paper](https://arxiv.org/abs/2310.08560): arquitectura inspirada en memoria virtual para LLMs.
- [Generative Agents](https://arxiv.org/abs/2304.03442): memoria, reflexion y planificacion en agentes simulados.
- [Khoj docs](https://docs.khoj.dev/): memoria/conocimiento personal sobre documentos y notas.
- [Obsidian](https://help.obsidian.md/Home): referencia de ecosistema de notas locales para posibles conectores.

### 12.10 Seguridad, politicas, sandbox, secretos y prompt injection

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/): riesgos de aplicaciones LLM.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework): marco de riesgo IA.
- [MITRE ATLAS](https://atlas.mitre.org/): amenazas y tacticas contra sistemas IA.
- [Open Policy Agent](https://www.openpolicyagent.org/docs/latest/): policy engine general.
- [OpenFeature](https://openfeature.dev/docs/reference/intro): estandar para feature flags.
- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs): gestion de secretos.
- [Docker security](https://docs.docker.com/engine/security/): aislamiento y seguridad de contenedores.
- [Firecracker](https://firecracker-microvm.github.io/): microVMs para aislamiento fuerte.
- [gVisor](https://gvisor.dev/docs/): sandboxing de contenedores.
- [Cloudflare - Prompt injection](https://developers.cloudflare.com/learning-paths/ai-security/concepts/prompt-injection/): introduccion practica a prompt injection.

### 12.11 Evaluaciones, observabilidad y trazabilidad

- [Inspect AI](https://inspect.aisi.org.uk/): framework de evaluaciones para modelos IA.
- [OpenAI Evals](https://github.com/openai/evals): evaluaciones programaticas.
- [DeepEval](https://docs.confident-ai.com/): evaluacion de aplicaciones LLM.
- [Ragas](https://docs.ragas.io/): evaluacion RAG.
- [LangSmith](https://docs.smith.langchain.com/): tracing, datasets y evaluacion para apps LLM.
- [OpenTelemetry](https://opentelemetry.io/docs/): trazas, metricas y logs.
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/): convenciones de observabilidad para sistemas GenAI.
- [CloudEvents](https://cloudevents.io/): formato estandar de eventos.
- [AsyncAPI](https://www.asyncapi.com/docs): documentacion de sistemas event-driven.
- [Martin Fowler - Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html): patron event sourcing.

### 12.12 APIs, integraciones, autenticacion y conectores

- [OAuth 2.0 RFC 6749](https://www.rfc-editor.org/rfc/rfc6749): autorizacion OAuth 2.0.
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html): especificacion para APIs HTTP.
- [JSON Schema](https://json-schema.org/): contratos de datos.
- [MCP specification](https://modelcontextprotocol.io/specification): protocolo para tools/contexto en agentes.
- [GitHub REST API](https://docs.github.com/en/rest): integracion con GitHub.
- [Google Drive API](https://developers.google.com/drive/api/guides/about-sdk): integracion con Drive.
- [Gmail API](https://developers.google.com/gmail/api/guides): integracion con Gmail.
- [Slack API](https://api.slack.com/): integracion con Slack.
- [Telegram Bot API](https://core.telegram.org/bots/api): integracion con Telegram.
- [Discord Developer Docs](https://discord.com/developers/docs/intro): integracion con Discord.

### 12.13 Producto, distribucion, administracion y operacion local

- [Electron](https://www.electronjs.org/docs/latest/): desktop apps.
- [Tauri](https://tauri.app/start/): desktop apps ligeras.
- [FastAPI](https://fastapi.tiangolo.com/): API backend Python.
- [Typer](https://typer.tiangolo.com/): CLI Python.
- [SQLite](https://www.sqlite.org/docs.html): persistencia local embebida.
- [PostgreSQL](https://www.postgresql.org/docs/): persistencia robusta multiusuario.
- [Alembic](https://alembic.sqlalchemy.org/en/latest/): migraciones de DB.
- [SQLAlchemy](https://docs.sqlalchemy.org/): ORM/persistencia Python.
- [Docker Compose](https://docs.docker.com/compose/): orquestacion local de servicios.
- [Kubernetes](https://kubernetes.io/docs/home/): despliegue escalable futuro.
- [Backstage](https://backstage.io/docs/): portal interno/developer platform como inspiracion para admin/plugin catalog.

### 12.14 Notas de uso de fuentes

- Para decisiones de implementacion, preferir documentacion oficial y repositorios sobre blogs secundarios.
- Para claims de modelos frontera, validar fecha y pagina oficial antes de fijar una decision.
- Para seguridad, convertir cada fuente en tests o gates: no basta con citar OWASP/NIST/MITRE.
- Para benchmarks, distinguir evaluaciones generales del modelo y evaluaciones propias del agente.
- Para dependencias externas, registrar version exacta, fecha de consulta y razon de adopcion en ADRs.

## 13. Nota final de direccion

El primer objetivo no es que el agente sea brillante. Es que sea gobernable.

Orden correcto:

```text
estado -> eventos -> modelo reemplazable -> politicas -> herramientas -> memoria -> RAG -> orquestacion -> subagentes -> seguridad cognitiva -> automatizacion -> producto
```

Cuando esta base exista, la inteligencia podra crecer sin romper el sistema.

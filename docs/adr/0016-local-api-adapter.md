# ADR 0016 - API local como adaptador HTTP

## Estado

Aceptado.

## Contexto

La CLI real ya opera el kernel usando `.nox/events.jsonl`. Para que futuras superficies de producto, scripts, UI o procesos externos puedan usar Nox sin acoplarse a Typer, necesitamos una API local.

Ya existia la decision temprana de usar FastAPI como adaptador HTTP inicial. Esta decision fija la implementacion concreta de v0.5.

## Decision

Crear `nox_agent_os.api` como adaptador HTTP local sobre el mismo runtime que usa la CLI.

La API se crea con:

```python
create_app(workspace_path=...)
```

El adaptador HTTP:

- carga el workspace con `load_kernel_context`,
- usa `.nox/events.jsonl` mediante `JsonlEventStore`,
- llama al `AgentKernel`,
- no contiene logica de negocio del kernel,
- no habla directo con storage, policy o state machine.

Endpoints iniciales:

- `GET /health`
- `GET /status`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/transitions`
- `GET /events`
- `GET /tasks/{task_id}/events`
- `POST /policy/check`
- `GET /approvals`
- `POST /approvals/{approval_id}/approve`
- `POST /approvals/{approval_id}/reject`
- `GET /kill`
- `POST /kill/on`
- `POST /kill/off`

Agregar comando:

```text
nox api serve --host 127.0.0.1 --port 8787
```

## Consecuencias

- Nox puede operar como servicio local.
- CLI y API comparten el mismo runtime y event log.
- FastAPI queda fuera del kernel.
- Futuros frontends pueden consumir HTTP sin saltar Governance.
- La persistencia robusta sigue quedando para v0.6.

## Reversibilidad

Alta. FastAPI es un adaptador reemplazable. Mientras conserve el contrato de entrada al kernel, otro framework HTTP podria sustituirlo sin cambiar la logica core.

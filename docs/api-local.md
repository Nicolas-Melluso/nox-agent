# API Local

La API local expone el kernel gobernable por HTTP. Es un adaptador, no el nucleo.

## Servir

```powershell
nox api serve --host 127.0.0.1 --port 8787
```

Por defecto usa el workspace actual y su event log:

```text
.nox/events.jsonl
```

## Endpoints iniciales

```text
GET  /health
GET  /status
POST /tasks
GET  /tasks
GET  /tasks/{task_id}
POST /tasks/{task_id}/transitions
GET  /events
GET  /tasks/{task_id}/events
POST /policy/check
GET  /approvals
POST /approvals/{approval_id}/approve
POST /approvals/{approval_id}/reject
GET  /kill
POST /kill/on
POST /kill/off
```

## Prueba rapida

```powershell
curl http://127.0.0.1:8787/health

curl -X POST http://127.0.0.1:8787/tasks `
  -H "Content-Type: application/json" `
  -d "{\"goal\":\"probar api local\"}"

curl http://127.0.0.1:8787/status
curl http://127.0.0.1:8787/events
```

## Regla

La API no ejecuta herramientas ni modelos. Solo expone capacidades ya existentes del kernel: tareas, eventos, policy, approvals, kill switch y status.

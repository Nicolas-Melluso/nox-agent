# Tests y Evals por Etapas

El sistema no debe ejecutar todo el ecosistema de tests cada vez que corre. Las verificaciones se agrupan por costo, riesgo y side effects.

## Modos de verificacion

| Modo | Objetivo | Costo | Side effects esperados | Default |
| --- | --- | --- | --- | --- |
| `none` | No correr verificaciones automaticas | ninguno | ninguno | si, para ejecucion normal |
| `smoke` | Confirmar arranque, config e imports basicos | bajo | ninguno | no |
| `unit` | Probar funciones y objetos aislados | bajo | ninguno | no |
| `contract` | Validar puertos/adaptadores y contratos internos | medio | ninguno o temporales controlados | no |
| `safety` | Verificar policy, HITL, kill switch y guards | medio | ninguno destructivo | no |
| `integration` | Probar SQLite/API/filesystem local | medio/alto | temporales controlados | no |
| `eval` | Medir comportamiento de modelo, RAG, memoria o agente | alto | puede usar modelo/red si esta habilitado | no |
| `full` | Ejecutar toda la suite aplicable | alto | segun configuracion | no |

## v0.1

```text
nox doctor
```

En v0.1, `nox doctor` cumple el rol de chequeo smoke intuitivo: valida instalacion, paquete importable, comando disponible y workspace `.nox`.

## v0.3

Los tests `safety` iniciales viven en `tests/test_governance_minimum.py`.

Cubren:

- read permitido por policy,
- write pendiente de approval,
- delete denegado por defecto,
- kill switch bloqueando tareas o acciones,
- doom loop repetible bloqueando una tarea,
- contratos ampliados de state machine,
- audit trail consultable por tarea, trace y tipo de evento,
- resource monitor con salud, conteos de tareas y approvals pendientes.

## v0.4

Los tests de CLI real viven en `tests/test_cli_v04.py` y `tests/test_jsonl_event_store.py`.

Cubren:

- persistencia de eventos en `JsonlEventStore`,
- creacion y replay de tareas entre comandos,
- `nox status`,
- policy check con approval rehidratable,
- kill switch persistente entre invocaciones,
- shell interactivo basico.

## v0.5

Los tests de API local viven en `tests/test_api_v05.py`.

Cubren:

- health y status,
- ciclo de tareas por HTTP,
- eventos por tarea,
- policy check con approval rehidratable,
- kill switch bloqueando nuevas tareas.

## Comandos futuros posibles

```text
nox check
nox check --level unit
nox check --level contract
nox check --level safety
nox check --level integration
nox eval run
```

No se implementa `nox verify smoke` porque no es una experiencia clara para el usuario inicial.

## Reglas HITL

Las verificaciones `none`, `smoke`, `unit`, `contract` y `safety` no requieren HITL si se ejecutan en modo read-only o con archivos temporales controlados.

`integration`, `eval` y `full` pueden requerir HITL si:

- escriben fuera de directorios temporales aprobados,
- usan red externa,
- usan credenciales,
- ejecutan modelos con costo,
- modifican datos persistentes reales,
- lanzan procesos externos no clasificados.

## Gates futuros

Los gates bloqueantes se activan por fase:

- v0.1: `smoke`
- v0.2: `smoke`, `unit`, `contract`
- v0.3: `safety`
- v0.5: `integration` inicial para API local sobre workspace temporal
- v0.6: `integration`
- v0.8: primeras evals de modelo
- v1.0: `full` para release interno

## Regla de crecimiento

Cada bug importante debe convertirse en test o eval solo si protege una conducta relevante. No se agregan suites por volumen; se agregan por riesgo cubierto.

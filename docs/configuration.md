# Configuracion y Datos

## Convenciones

- YAML para configuracion humana.
- JSON para informacion estructurada intercambiada por el sistema.
- JSONL para eventos, logs append-only, audit trail y evidencia.
- TOON puede usarse como representacion compacta para contexto de modelos, pero no como fuente canonica.

## Precedencia futura

```text
defaults
  -> config global
  -> config de workspace
  -> variables de entorno
  -> flags de CLI
  -> policy runtime
```

## Archivos esperados

```text
.nox/
  identity.json
  system.prompt.md
  events.jsonl
  backups/
```

`.nox` es la instancia del workspace. La instalacion general de Nox provee runtime, adapters, politicas, schemas y defaults; `.nox` conserva lo local al proyecto.

## Regla canonica

La configuracion humana puede vivir en YAML.

Los registros que deben auditarse, reproducirse o migrarse deben vivir como datos estructurados versionados.

## Fuente canonica por tipo de dato

| Tipo de dato | Formato inicial | Fuente canonica | Notas |
| --- | --- | --- | --- |
| Identidad de workspace | JSON | `.nox/identity.json` | Contiene `workspace_id`, `instance_id`, version y referencias al engine. |
| Workspace prompt | Markdown + frontmatter | `.nox/system.prompt.md` | Primer punto local creado por `nox init`. |
| Config humana futura | YAML | `.nox/config.yaml` futuro | Editable por usuario cuando exista configuracion expandida. |
| Defaults de producto | TOML/JSON futuro | paquete instalado | No se editan a mano. |
| Eventos | JSONL o SQLite adapter | `EventStore` | Append-only, con `schema_version`. |
| Tareas | JSONL o SQLite adapter | `TaskStore` | Snapshot/read model, no reemplaza eventos canonicos. |
| Config estructurada | JSONL o SQLite adapter | `ConfigStore` | Para datos de sistema, no necesariamente editable a mano. |
| Logs estructurados | JSONL | log local | Observabilidad, no estado canonico. |
| Audit trail | JSONL o SQLite adapter | `AuditStore` futuro | Debe poder correlacionarse con eventos. |
| Evidencia | SQLite o JSONL adapter | `EvidenceStore` | Con provenance, hash y retencion. |
| Snapshots de estado | SQLite adapter | `StateSnapshotStore` futuro | Optimizacion; el replay de eventos sigue siendo canonico. |
| Memoria | SQLite adapter futuro | `MemoryStore` | Siempre con evidencia asociada. |
| Contexto para modelos | TOON/JSON/texto | no canonico | Representacion transitoria. |

Todo dato persistente importante debe tener:

- `schema_version`
- provenance
- politica de retencion
- politica de borrado
- estrategia de migracion

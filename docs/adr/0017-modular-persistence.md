# ADR 0017 - Persistencia modular inicial

## Estado

Aceptado.

## Contexto

El kernel ya emite eventos y la CLI/API usan `.nox/events.jsonl` como event log minimo. Ese archivo hizo operable el sistema, pero no debe convertirse en una dependencia rigida del nucleo.

Antes de sumar modelos, herramientas, evidencia real, RAG o memoria, necesitamos puertos de persistencia reemplazables y versionados.

## Decision

Crear `nox_agent_os.storage` como capa de persistencia modular inicial.

Formalizar estos puertos:

- `EventStore`: eventos append-only del kernel y audit trail reconstruible.
- `TaskStore`: snapshots o vistas persistibles de tareas.
- `ConfigStore`: configuracion estructurada del sistema/workspace.
- `EvidenceStore`: evidencia con provenance para herramientas, RAG y memoria futuros.

Implementar adapters iniciales:

- `InMemory`: tests y ejecucion efimera.
- `JSONL`: compatibilidad con `.nox/events.jsonl` y registros append-only.
- `SQLite`: primer backend local durable, con migracion inicial.

Mantener JSONL como backend default de CLI/API por ahora para no romper workspaces existentes. SQLite queda disponible y testeado como adapter, no como default obligatorio.

## Alcance

v0.6 prepara persistencia. No implementa memoria semantica, RAG ni Tool Runtime.

`EvidenceStore` no decide que recordar. Solo define donde guardar evidencia/provenance cuando existan herramientas o memorias que la necesiten.

## Consecuencias

- El kernel puede seguir dependiendo de contratos, no de SQLite.
- JSONL puede convivir con SQLite o ser reemplazado mas adelante.
- Los tests contractuales pueden validar que varios adapters preserven el mismo comportamiento.
- Las futuras memorias pueden apoyarse en stores versionados sin acoplarse al formato fisico inicial.

## Reversibilidad

Alta para adapters concretos. Media para los puertos, porque `EventStore`, `TaskStore`, `ConfigStore` y `EvidenceStore` pasan a ser parte del vocabulario arquitectonico del proyecto.

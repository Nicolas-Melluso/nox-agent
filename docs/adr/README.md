# ADRs

Los ADRs son la fuente canonica para decisiones de arquitectura aceptadas.

README, roadmap, stack y plan maestro pueden resumir decisiones, pero no reemplazan a los ADRs.

## Indice

| ADR | Decision | Estado |
| --- | --- | --- |
| `0001` | Python 3.14 y uv como runtime base | Aceptado |
| `0002` | FastAPI como adaptador HTTP | Aceptado |
| `0003` | Arquitectura por puertos y adaptadores | Aceptado |
| `0004` | SQLite como primer storage adapter | Aceptado |
| `0005` | Convenciones YAML, JSON y JSONL | Aceptado |
| `0006` | Typer como adaptador CLI temporal | Aceptado |
| `0007` | Human-in-the-loop por defecto | Aceptado |
| `0008` | Instalacion y distribucion guiada original | Reemplazado por `0010` |
| `0009` | ModelBackend y providers reemplazables | Aceptado |
| `0010` | Nox como comando y workspace `.nox` | Aceptado |
| `0011` | Instalador Windows experimental `NoxSetup.exe` | Aceptado |
| `0012` | Event sourcing inicial del kernel | Aceptado |
| `0013` | Gobierno inicial, approvals y kill switch | Aceptado |
| `0014` | Observabilidad minima desde el kernel | Aceptado |
| `0015` | CLI real y event log JSONL minimo | Aceptado |
| `0016` | API local como adaptador HTTP | Aceptado |
| `0017` | Persistencia modular inicial | Aceptado |
| `0018` | Identidad de instancia de workspace | Aceptado |

## Proxima numeracion

El proximo ADR nuevo debe usar `0019`.

## Regla de numeracion

Los ADRs no se renombran una vez aceptados. Si una decision cambia, se crea un ADR nuevo que reemplaza o modifica la decision anterior.

## ADRs previstos

- `0019`: Evidence Ledger.
- `0020`: State Machine Kernel ampliado, si requiere decision formal adicional.
- `0021`: tests/evals por etapas, si requiere decision formal adicional.

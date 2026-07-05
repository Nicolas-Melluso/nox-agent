# Stack Inicial

## Runtime

- Lenguaje: Python.
- Version objetivo: Python 3.14.
- Manejador: uv.

## API

- FastAPI se usara como adaptador HTTP inicial.
- La logica del sistema no debe depender de FastAPI.
- Starlette, Litestar, Flask u otra superficie HTTP deben poder reemplazarlo.

## CLI

- Typer se usara como adaptador CLI inicial.
- Typer es una dependencia temporal, no una decision estructural.
- El proyecto puede evolucionar hacia CLI/REPL propio con menor dependencia externa.

## Persistencia

- SQLite sera el primer backend persistente.
- El codigo core hablara con puertos, no con SQLite directamente.
- Adaptadores esperados:
  - `InMemory`
  - `JSONL`
  - `SQLite`
  - `Postgres` futuro

## Modelos

- `llama.cpp` sera el primer backend local real.
- El kernel hablara con `ModelBackend`, no con `llama.cpp` directamente.
- El contrato conceptual vive en `docs/model-backends.md`.
- Backends futuros esperados:
  - `MockBackend`
  - `LlamaCppBackend`
  - `OpenAIBackend`
  - `CodexBackend`
  - `OllamaBackend`
  - `VllmBackend`

## Dependencias

El criterio es pocas dependencias, pero no cero dependencias.

Una dependencia es aceptable si:

- reduce riesgo operativo,
- acelera una superficie reemplazable,
- queda detras de un adaptador,
- no invade el kernel,
- puede retirarse con impacto acotado.

## Distribucion

- Paquete distribuible: `nox-agent-os`.
- Comando publico: `nox`.
- Paquete Python importable: `nox_agent_os`.
- La estrategia completa vive en `docs/installation-and-distribution.md`.

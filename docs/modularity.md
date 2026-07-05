# Modularidad

La plataforma debe poder reemplazar modulos sin reescribir el sistema.

## Regla central

El kernel depende de contratos internos. Los detalles concretos viven en adaptadores.

```text
Kernel -> Port -> Adapter
```

## Modulos reemplazables desde el inicio

- HTTP API
- CLI
- almacenamiento
- backend de modelo
- tool runtime
- sistema de configuracion
- mecanismo de approvals
- sistema de logs
- runners de tests/evals

## Forma esperada

```python
class EventStore:
    ...

class SQLiteEventStore(EventStore):
    ...

class JsonlEventStore(EventStore):
    ...

class InMemoryEventStore(EventStore):
    ...
```

## Prohibiciones iniciales

- No importar FastAPI dentro del kernel.
- No importar Typer dentro del kernel.
- No usar SQLite directamente fuera de su adapter.
- No llamar modelos directamente desde superficies de usuario.
- No ejecutar herramientas sin pasar por politica.

## Criterio de aceptacion

Un modulo es realmente modular si puede reemplazarse por otro adapter en tests sin cambiar logica core.

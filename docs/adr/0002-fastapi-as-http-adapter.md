# ADR 0002 - FastAPI como adaptador HTTP

## Estado

Aceptado.

## Contexto

La plataforma necesita una API local para que futuras superficies puedan crear tareas, consultar estado y observar eventos.

## Decision

Usar FastAPI como adaptador HTTP inicial.

FastAPI no forma parte del kernel. Solo traduce requests HTTP a comandos internos.

## Consecuencias

- Los routers HTTP no deben contener logica core.
- La API debe depender de servicios de aplicacion y contratos internos.
- Otra tecnologia HTTP debe poder reemplazar FastAPI en el futuro.

## Reversibilidad

Alta. Si la frontera interna esta bien disenada, se puede reemplazar FastAPI por Starlette, Litestar, Flask u otra superficie.

# ADR 0001 - Python 3.14 y uv como runtime base

## Estado

Aceptado.

## Contexto

El proyecto necesita un runtime local, multiplataforma y con buen ecosistema para agentes, RAG, APIs, procesos, persistencia y evaluaciones.

Tambien necesita una forma confiable de manejar versiones de Python, entornos y dependencias.

## Decision

Usar Python 3.14 como version objetivo y uv como manejador de Python, entorno y dependencias.

## Consecuencias

- El proyecto podra fijar version con `.python-version`.
- Las dependencias se declararan en `pyproject.toml`.
- El lockfile sera parte del flujo normal.
- El setup local debera poder guiarse con comandos uv.

## Reversibilidad

La decision es reversible si se mantiene el codigo compatible con Python estandar y no se acopla la logica core a uv.

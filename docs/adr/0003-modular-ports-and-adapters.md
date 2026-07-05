# ADR 0003 - Arquitectura por puertos y adaptadores

## Estado

Aceptado.

## Contexto

El proyecto debe permitir reemplazar modelos, almacenamiento, APIs, CLIs, herramientas y mecanismos de evaluacion sin reescribir el kernel.

## Decision

Usar una arquitectura por puertos y adaptadores.

El kernel declara lo que necesita mediante interfaces internas. Cada tecnologia concreta se implementa como adapter.

## Consecuencias

- El codigo core no debe depender de frameworks externos.
- Los tests pueden usar adapters en memoria.
- SQLite, FastAPI, Typer y llama.cpp son reemplazables.
- Cada modulo debe tener una frontera explicita.

## Reversibilidad

Baja como principio arquitectonico. Es una decision fundacional.

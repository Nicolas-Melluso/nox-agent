# ADR 0004 - SQLite como primer storage adapter

## Estado

Aceptado.

## Contexto

La plataforma necesita persistencia local simple, confiable y facil de distribuir.

## Decision

Usar SQLite como primer backend persistente, detras de puertos de almacenamiento.

## Consecuencias

- El sistema puede correr localmente sin servidor de base de datos.
- Python puede usar SQLite mediante `sqlite3`.
- El kernel no debe ejecutar SQL directamente.
- Los eventos y datos persistentes deben incluir `schema_version`.

## Reversibilidad

Alta si los puertos estan bien definidos. Postgres, JSONL u otros backends pueden implementarse como adapters.

# ADR 0005 - Convenciones YAML, JSON y JSONL

## Estado

Aceptado.

## Contexto

El proyecto necesita separar configuracion humana de datos auditables del sistema.

## Decision

Usar YAML para configuracion humana, JSON para datos estructurados y JSONL para eventos/logs append-only.

TOON puede evaluarse para serializar contexto hacia modelos, pero no sera fuente canonica de verdad.

## Consecuencias

- Los archivos de configuracion priorizan legibilidad humana.
- Eventos, evidencia y logs priorizan trazabilidad y parsing estable.
- Los formatos persistentes deben versionarse.

## Reversibilidad

Media. Cambiar formatos persistentes requiere migraciones. Cambiar formatos de configuracion es mas simple si existe un loader centralizado.

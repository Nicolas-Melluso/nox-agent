# ADR 0007 - Human-in-the-loop por defecto

## Estado

Aceptado.

## Contexto

El sistema ejecutara acciones con distintos niveles de riesgo. La autonomia debe crecer por capacidad demostrada, no por ausencia de supervision.

## Decision

Usar HITL por defecto para acciones sensibles, irreversibles, externas o ambiguas.

## Consecuencias

- Acciones de escritura, borrado, ejecucion, red, envio y credenciales requieren politica explicita.
- Si una accion no puede clasificarse con confianza, no se aprueba automaticamente.
- Las aprobaciones deben registrarse como eventos auditables.

## Reversibilidad

Baja como principio de seguridad. Las politicas pueden relajarse por capacidad y evidencia, pero el default debe seguir siendo conservador.

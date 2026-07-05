# Human In The Loop

HITL es una politica fundacional del sistema. No es una pantalla final ni una opcion cosmetica.

## Principio

Las acciones sensibles, irreversibles, externas o ambiguas requieren aprobacion humana antes de ejecutarse.

## Requieren HITL por defecto

- escribir archivos,
- borrar archivos,
- ejecutar comandos,
- usar red externa,
- enviar mensajes,
- usar credenciales,
- modificar configuracion persistente,
- cambiar politicas,
- habilitar capacidades nuevas,
- ejecutar acciones con impacto fuera del workspace.

## No requieren HITL por defecto

- leer configuracion local no sensible,
- listar tareas,
- ver eventos,
- correr verificaciones side-effect-free,
- usar backends mock,
- reconstruir estado por replay sin side effects.

## Verificaciones y HITL

Las verificaciones `smoke`, `unit`, `contract` y `safety` no requieren HITL si operan en modo read-only o usan archivos temporales controlados dentro del workspace.

Las verificaciones `integration`, `eval` y `full` requieren HITL cuando usan red externa, credenciales, modelos con costo, procesos externos no clasificados o datos persistentes reales.

El modo `none` no ejecuta verificaciones automaticas.

## Decisiones posibles

```text
allow
ask
deny
approved_once
approved_session
rejected
auto_reviewing
auto_approved
auto_denied
```

## Registro minimo

Cada decision HITL debe registrar:

- accion solicitada,
- actor,
- riesgo,
- razon,
- politica aplicada,
- aprobador humano si existe,
- duracion de la aprobacion,
- evento asociado,
- timestamp.

## Regla de seguridad

Si una accion no puede clasificarse con confianza, se trata como `ask` o `deny`, nunca como `allow`.

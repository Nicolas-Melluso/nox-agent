# Glosario

## Agente

Proceso gobernado que recibe una tarea, usa capacidades permitidas, emite eventos y finaliza bajo condiciones declaradas.

## Kernel

Nucleo del sistema. Coordina estado, politicas, eventos, permisos, herramientas, modelos y persistencia mediante contratos.

## Port

Interfaz estable que declara una capacidad requerida por el sistema.

## Adapter

Implementacion concreta de un port. Puede ser reemplazada sin cambiar el kernel.

## HITL

Human-in-the-loop. Punto donde una decision o accion requiere aprobacion humana antes de continuar.

## Policy Engine

Modulo que decide si una accion se permite, se deniega o requiere aprobacion.

## Evidence Ledger

Registro verificable de evidencia primaria observada por el sistema.

## Event Sourcing

Modelo donde el estado se reconstruye desde eventos inmutables en vez de depender solo de campos mutables.

## Reasoning Profile

Politica ejecutable que define modelos permitidos, presupuesto, herramientas, verificaciones, riesgo y fallback.

## Eval

Prueba orientada a comportamiento. Verifica que una capacidad responde de forma aceptable bajo criterios definidos.

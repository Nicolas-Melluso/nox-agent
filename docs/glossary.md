# Glosario

## Agente

Proceso gobernado que recibe una tarea, usa capacidades permitidas, emite eventos y finaliza bajo condiciones declaradas.

## Agente modular

Agente instalado como plataforma local reemplazable por modulos. En Nox, el agente modular general contiene runtime, kernel, adapters, politicas, schemas y defaults.

## Instancia de workspace

Carpeta `.nox` dentro de un proyecto. No es el agente completo; es la instancia local que conserva metadata, identidad, eventos, estado, config, evidencia y referencias al engine instalado.

## Workspace ID

Identidad estable de un workspace/proyecto Nox. Debe usarse para correlacionar logs, auditoria, almacenamiento y observabilidad aunque cambie el path local.

## Instance ID

Identidad de una instancia `.nox` concreta. Si `.nox` se borra y se inicializa otra vez, esta identidad puede cambiar aunque el proyecto sea el mismo.

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

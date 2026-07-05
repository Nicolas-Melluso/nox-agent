# Model Backends

El sistema no debe depender de un modelo ni de un proveedor concreto.

## Contrato conceptual

`ModelBackend` es el port que abstrae cualquier motor de inferencia.

Cada backend debe declarar:

- nombre,
- tipo de proveedor,
- modelos disponibles,
- capacidades,
- limites de contexto,
- soporte de herramientas,
- soporte de streaming,
- costo esperado,
- requisitos de red,
- requisitos de credenciales,
- politica HITL asociada,
- errores y fallback.

## Backends esperados

| Backend | Rol | Estado esperado |
| --- | --- | --- |
| `MockBackend` | pruebas, smoke, desarrollo sin modelo real | primero |
| `LlamaCppBackend` | inferencia local inicial | v0.8 |
| `OpenAIBackend` | API OpenAI opcional | futuro |
| `CodexBackend` | integracion futura con Codex como capacidad externa | futuro |
| `OllamaBackend` | backend local opcional | futuro |
| `VllmBackend` | backend local/servidor de alto rendimiento | futuro |

## Regla de gobierno

El Model Router selecciona backends mediante politica. Ninguna superficie de usuario invoca modelos directamente.

## OpenAI y Codex futuros

OpenAI/Codex deben tratarse como providers opcionales con reglas propias de:

- autenticacion,
- secretos,
- costos,
- uso de red,
- trazabilidad,
- HITL,
- limites por workspace,
- fallback local.

## Primera implementacion

Antes de `llama.cpp`, se implementara `MockBackend` para validar contratos, routing, logging, budgets y tests sin depender de inferencia real.

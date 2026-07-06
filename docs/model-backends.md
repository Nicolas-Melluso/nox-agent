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
| `MockBackend` | pruebas, smoke, desarrollo sin modelo real | implementado en v0.7 |
| `LlamaCppBackend` | inferencia local inicial | v0.8 |
| `OpenAIBackend` | API OpenAI opcional | futuro |
| `CodexAgentBackend` | integracion futura con Codex como agente/subagente externo | futuro |
| `OllamaBackend` | backend local opcional | futuro |
| `VllmBackend` | backend local/servidor de alto rendimiento | futuro |

## Regla de gobierno

El Model Router selecciona backends mediante politica. Ninguna superficie de usuario invoca modelos directamente.

## OpenAI y Codex futuros

OpenAI debe tratarse como provider opcional de inferencia directa.

Codex no debe tratarse como un `ModelBackend` plano por defecto, porque Codex es un agente con herramientas, sandbox, aprobaciones, MCP y ejecucion. La integracion futura debe modelarse como `CodexAgentBackend` o provider de subagente gobernado.

Caminos posibles:

- `codex exec --json` para una primera integracion automatizable.
- Codex SDK Python/TypeScript para control programatico mas flexible.
- `codex mcp-server` para exponer Codex como herramienta MCP dentro de otro orquestador.

OpenAI/Codex deben tener reglas propias de:

- autenticacion,
- secretos,
- costos,
- uso de red,
- trazabilidad,
- HITL,
- limites por workspace,
- fallback local.

## Primera implementacion

Antes de `llama.cpp`, v0.7 implementa `MockBackend` para validar contratos, routing, auditoria, budgets y tests sin depender de inferencia real.

Comandos iniciales:

```text
nox model list
nox model set <modelo>
nox model limit <modelo> to <tokens>
nox model route "prompt de prueba"
nox audit status
nox audit level <off|minimal|normal|debug|trace>
nox audit off
```

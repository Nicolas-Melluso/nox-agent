# ADR 0009 - ModelBackend y providers reemplazables

## Estado

Aceptado.

## Contexto

El sistema debe poder usar modelos locales y providers externos sin acoplar el orquestador a un backend concreto.

## Decision

Definir `ModelBackend` como port para inferencia.

Backends iniciales y futuros:

- `MockBackend`
- `LlamaCppBackend`
- `OpenAIBackend`
- `CodexBackend`
- `OllamaBackend`
- `VllmBackend`

## Consecuencias

- `llama.cpp` sera un adapter, no una dependencia estructural.
- `MockBackend` se implementara antes que un modelo real para habilitar tests y routing.
- Providers con red, costo o credenciales requeriran policy y HITL propios.
- El Model Router registrara backend, modelo, perfil, presupuesto, riesgo y razon de seleccion.

## Reversibilidad

Alta para providers concretos. Baja para el principio de usar un port estable de inferencia.

# ADR 0008 - Instalacion y distribucion guiada

## Estado

Reemplazado por ADR 0010.

Este ADR queda como registro historico de la decision anterior. La decision vigente vive en `docs/adr/0010-nox-command-and-workspace.md`.

## Contexto

La plataforma debe poder instalarse y crearse de forma guiada, con una experiencia parecida a `npm init` o `npx create-*`.

## Decision

Distribuir el proyecto como paquete Python `local-agent-os`, exponer el comando `local-agent` y soportar inicializacion futura con:

```text
uvx local-agent-os init
uv tool install local-agent-os
local-agent init
```

## Consecuencias

- El paquete importable sera `local_agent_os`.
- El comando publico sera `local-agent`.
- `pyproject.toml` debera declarar `project.scripts`.
- Capacidades opcionales se agruparan como extras: `api`, `llama`, `openai`, `dev` y `all`.
- El wizard de init debe crear configuracion y carpetas, no acoplarse al kernel.

## Reversibilidad

Media. Cambiar el nombre del paquete o comando despues de publicar afecta instalacion, docs y usuarios. Por eso se fija temprano.

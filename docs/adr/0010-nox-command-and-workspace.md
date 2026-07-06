# ADR 0010 - Nox como comando y workspace `.nox`

## Estado

Aceptado.

## Contexto

La plataforma se piensa como un agente general instalado una vez a nivel usuario o sistema, usable desde cualquier carpeta mediante un comando corto.

El workspace local no debe contener todo el sistema. Debe funcionar como una instancia de workspace: metadata minima, estado local y referencias para orientar al engine instalado.

Tambien existe una herramienta Python llamada `nox`, por lo que conviene evitar usar `nox` como nombre de paquete distribuible.

## Decision

Usar:

- Producto: Nox.
- Comando publico: `nox`.
- Paquete distribuible: `nox-agent-os`.
- Paquete Python importable: `nox_agent_os`.
- Workspace local: `.nox/`.
- Prompt local inicial: `.nox/system.prompt.md`.

`nox init` crea el workspace local minimo.

La instalacion general de Nox provee runtime, kernel, adapters, politicas, schemas y defaults. `.nox/` guarda solo lo propio del workspace: system prompt, eventos, estado, config local y referencias al engine instalado.

## Consecuencias

- El comando se siente como `git` o `npm`: disponible en cualquier carpeta tras instalarlo.
- El paquete evita colisionar con el paquete Python existente `nox`.
- El ejecutable `nox` puede colisionar con instalaciones previas de la herramienta Python Nox; esa colision debe resolverse explicitamente durante instalacion.
- `uv tool install --editable .` permite probar el comando desde el repo durante desarrollo.
- `nox doctor` se usa como chequeo inicial intuitivo en v0.1.
- `nox update` refresca la metadata de un workspace ya creado sin reinstalar el engine.
- `nox upgrade` queda reservado para actualizar el engine instalado. No debe confundirse con `nox update`.
- Los tests/evals dedicados quedan para fases posteriores.

## Reemplaza

Reemplaza la decision de distribucion original registrada en ADR 0008.

## Reversibilidad

Media. Cambiar el comando publico despues de usarlo en workspaces y documentacion afecta experiencia de usuario, instalacion y habitos.

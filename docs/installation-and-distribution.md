# Instalacion y Distribucion

La plataforma debe poder instalarse, inicializarse, diagnosticarse y actualizarse con comandos guiados.

El objetivo de producto es una experiencia parecida a `git`, `npm init` o `npx create-*`, usando el ecosistema Python y uv.

Nox se instala una vez a nivel usuario o sistema. Esa instalacion es el agente modular general: contiene runtime, kernel, adapters, politicas, schemas y defaults.

Cada workspace solo necesita una carpeta local `.nox` con el system prompt y metadata minima. Esa carpeta es una instancia del workspace, no una copia del agente completo.

La instancia `.nox` tiene identidad propia con `workspace_id` e `instance_id`, para que auditoria, observabilidad, backups y memoria futura puedan correlacionarse aunque cambien paths o versiones del engine.

## Nombres canonicos

| Concepto | Nombre |
| --- | --- |
| Producto | Nox |
| Paquete distribuible | `nox-agent-os` |
| Comando CLI | `nox` |
| Paquete Python importable | `nox_agent_os` |
| Workspace local | `.nox/` |
| Prompt del workspace | `.nox/system.prompt.md` |

## Modos de uso esperados

Ejecutar sin instalar permanentemente:

```powershell
uvx --from nox-agent-os nox init
```

Instalar como herramienta global/user-level:

```powershell
uv tool install nox-agent-os
nox init
```

Instalar desde el repo durante desarrollo:

```powershell
uv tool install --editable .
uv tool update-shell
nox doctor
```

Si ya existe otro ejecutable llamado `nox`, uv puede pedir reinstalar con `--force`. En ese caso hay que decidir explicitamente que comando debe ganar en el entorno del usuario.

Ejecutar desde el repo sin instalar:

```powershell
uv run nox init
uv run nox doctor
```

## Workspace minimo

`nox init` crea:

```text
.nox/
  identity.json
  system.prompt.md
  events.jsonl
```

El workspace no contiene el sistema completo. Solo declara como debe conectarse ese proyecto local con el engine instalado.

Con el tiempo, `.nox` puede guardar estado local, eventos, config del workspace, evidencia y referencias a capacidades disponibles en el engine instalado. La logica core sigue viviendo en la instalacion general de Nox.

El prompt del workspace guarda una referencia al engine instalado:

```yaml
engine:
  mode: installed
  package: "nox-agent-os"
  import_name: "nox_agent_os"
  version: "..."
  package_path: "..."
  executable_path: "..."
```

Si el engine cambia despues de haber creado un workspace, no hace falta desinstalar. Desde esa carpeta se corre:

```powershell
nox update
```

Eso refresca `.nox/system.prompt.md` y la metadata de engine en `.nox/identity.json`, preservando `workspace_id` e `instance_id`.

`nox update` no instala una version nueva de Nox. Solo actualiza metadata local del workspace.

Para actualizar el engine instalado se reserva:

```powershell
nox upgrade
```

En v0.6, `nox upgrade --check` muestra version, modo de engine, ejecutable activo y fuente esperada. La descarga e instalacion automatica desde GitHub queda pendiente para una fase posterior.

Comportamiento objetivo futuro:

```text
nox upgrade
  -> consulta la ultima release disponible en GitHub
  -> descarga NoxSetup.exe
  -> valida version/hash/firma cuando exista
  -> ejecuta el instalador
  -> deja el comando nox apuntando al engine actualizado
```

## Entry point

El comando CLI se publica mediante `pyproject.toml`:

```toml
[project.scripts]
nox = "nox_agent_os.cli.main:app"
```

## Extras opcionales

El nucleo debe mantenerse liviano. Capacidades adicionales entran como extras:

```text
nox-agent-os[api]
nox-agent-os[llama]
nox-agent-os[openai]
nox-agent-os[dev]
nox-agent-os[all]
```

## Regla de arquitectura

El instalador y el workspace local no deben contener logica core. El engine instalado provee runtime, politicas, adapters, schemas y defaults.

## Comandos v0.1

```text
nox --help
nox init
nox doctor
nox version
nox prompt
nox update
```

## Comandos futuros esperados

```text
nox run
nox check
nox api start
nox upgrade
```

## Instalador Windows experimental

El experimento de `NoxSetup.exe` vive en `docs/windows-installer.md`.

Comandos:

```powershell
.\scripts\build_nox_exe.ps1
.\scripts\build_nox_setup.ps1
```

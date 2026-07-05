# Instalador Windows Experimental

Este documento define el experimento para generar `nox.exe` y empaquetarlo como `NoxSetup.exe`.

## Objetivo

Probar de forma recurrente que Nox puede instalarse como una herramienta Windows normal:

```text
NoxSetup.exe
  -> el usuario elige path de instalacion
  -> se instala nox.exe y su engine
  -> se agrega nox al PATH de usuario
  -> el usuario puede correr nox desde cualquier carpeta
```

## Estado

Experimental.

No reemplaza todavia el flujo de desarrollo con uv:

```powershell
uv tool install --editable .
```

## Artefactos

| Artefacto | Ubicacion | Como se genera |
| --- | --- | --- |
| `nox.exe` | `dist/nox/nox.exe` | `scripts/build_nox_exe.ps1` |
| `NoxSetup.exe` | `dist/installer/NoxSetup.exe` | `scripts/build_nox_setup.ps1` |

## Build de nox.exe

```powershell
.\scripts\build_nox_exe.ps1
```

Si PowerShell bloquea scripts por politica local:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_nox_exe.ps1
```

Con limpieza previa:

```powershell
.\scripts\build_nox_exe.ps1 -Clean
```

Este paso usa PyInstaller y genera una distribucion `onedir`, no `onefile`.

Elegimos `onedir` porque representa mejor un engine instalado en un directorio estable. El workspace `.nox/system.prompt.md` puede guardar ese directorio como `engine.install_root_path`.

## Build de NoxSetup.exe

```powershell
.\scripts\build_nox_setup.ps1
```

Si PowerShell bloquea scripts por politica local:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_nox_setup.ps1
```

Con limpieza previa:

```powershell
.\scripts\build_nox_setup.ps1 -Clean
```

Este paso requiere Inno Setup. Si `ISCC.exe` no esta instalado, el script deja `nox.exe` listo y avisa que falta Inno Setup.

## Resultado esperado

Despues de instalar `NoxSetup.exe`, una terminal nueva deberia poder ejecutar:

```powershell
nox doctor
nox init
nox api serve --help
```

Cuando un workspace se inicializa, el prompt local debe incluir:

```yaml
engine:
  mode: 'frozen-exe'
  install_root_path: '...'
  executable_path: '...\nox.exe'
```

## Limitaciones conocidas

- El instalador todavia es experimental.
- El agregado al PATH se hace a nivel usuario y mueve el directorio de Nox al inicio
  para priorizar `NoxSetup.exe` frente a shims viejos de `uv tool`.
- No hay firma de codigo.
- No hay mecanismo de auto-update.
- No hay rollback avanzado mas alla del uninstall del instalador.
- No hay separacion final entre runtime, policies, schemas y adapters; por ahora viajan dentro del bundle.
- Cada vez que cambian dependencias runtime hay que reconstruir `NoxSetup.exe`.

## Criterio de exito del experimento

- `NoxSetup.exe` instala sin error.
- `nox.exe` queda disponible en una terminal nueva.
- `nox doctor` muestra el path de instalacion.
- `nox init` crea `.nox/system.prompt.md`.
- `nox update` refresca metadata del workspace.
- `nox api serve --help` funciona sin instalar dependencias externas.
- El binario empaquetado puede levantar `/health` desde la API local.

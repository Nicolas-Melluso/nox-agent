# ADR 0011 - Instalador Windows experimental `NoxSetup.exe`

## Estado

Aceptado.

## Contexto

Nox debe poder operar como una herramienta instalada a nivel usuario o sistema, similar a `git` o `npm`, sin exigir que el usuario conozca Python, uv o el layout interno del proyecto.

Durante desarrollo necesitamos poder generar instaladores de prueba de forma repetible para validar la operatividad real en Windows.

## Decision

Agregar un experimento de packaging Windows con dos pasos:

1. Generar `nox.exe` con PyInstaller.
2. Generar `NoxSetup.exe` con Inno Setup cuando `ISCC.exe` este disponible.

Los scripts viven en:

- `scripts/build_nox_exe.ps1`
- `scripts/build_nox_setup.ps1`
- `scripts/test_nox_distribution.ps1`

La configuracion de Inno Setup vive en:

- `packaging/windows/NoxSetup.iss`

## Consecuencias

- Podemos seguir desarrollando con uv y, cada tanto, construir un instalador Windows para probar UX real.
- El bundle usa modo `onedir` para preservar un directorio de instalacion estable.
- `.nox/system.prompt.md` puede registrar `engine.install_root_path` y `engine.executable_path`.
- El instalador debe incluir dependencias runtime necesarias para todas las capacidades publicas de `nox`.
- El build del ejecutable debe correr smoke tests contra el binario empaquetado, incluyendo `nox api serve --help` y una llamada real a `/health`.
- Inno Setup es una dependencia externa solo para construir el instalador, no para correr Nox.
- Todavia no hay firma de codigo, auto-update ni instalacion multiusuario robusta.

## Reversibilidad

Alta. El experimento no afecta el kernel ni el contrato del workspace. Si otra herramienta de instalacion conviene mas, puede reemplazar Inno Setup sin cambiar `nox init`.

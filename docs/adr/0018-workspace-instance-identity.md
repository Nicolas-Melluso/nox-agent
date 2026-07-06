# ADR 0018 - Identidad de Instancia de Workspace

## Estado

Aceptado.

## Contexto

Nox se instala como agente modular general, mientras que cada proyecto crea una instancia local en `.nox/`.

Antes de esta decision, los eventos creados desde CLI/API usaban el path del proyecto como `workspace_id`. Eso funciona para pruebas, pero es fragil para auditoria, backups, observabilidad, reinstalaciones, renombres de carpeta y futura memoria.

## Decision

Cada workspace Nox debe tener un archivo `.nox/identity.json` con:

- `workspace_id`: identidad estable del proyecto.
- `instance_id`: identidad de la instancia `.nox` concreta.
- `created_at` y `updated_at`.
- version de Nox usada para escribir la identidad.
- ultimo path conocido del workspace.
- referencia al engine instalado activo.

`nox init` crea la identidad. `nox update` refresca metadata de version, engine y paths sin cambiar `workspace_id` ni `instance_id`.

Los eventos nuevos deben poder registrar `instance_id` ademas de `workspace_id`. Las tareas nuevas usan el `workspace_id` estable en vez del path local.

## Consecuencias

- `.nox` pasa a ser una instancia identificable, no solo una carpeta de metadata.
- Logs, API, storage y auditoria pueden correlacionar actividad aunque cambie el path del proyecto.
- Los eventos JSONL previos siguen siendo legibles porque `instance_id` es opcional.
- SQLite sube su schema de storage a version 2 para agregar `instance_id` en eventos y tareas.
- La rotacion o regeneracion deliberada de `instance_id` queda para una fase posterior.

## No Objetivos

- No implementa sincronizacion remota de workspaces.
- No implementa memoria semantica.
- No define todavia politicas de duplicado, clonacion o migracion multi-device.

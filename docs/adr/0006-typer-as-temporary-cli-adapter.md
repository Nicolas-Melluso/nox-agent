# ADR 0006 - Typer como adaptador CLI temporal

## Estado

Aceptado.

## Contexto

La plataforma necesita una CLI usable desde el inicio, pero el objetivo a largo plazo puede incluir un REPL propio con menos dependencias.

## Decision

Usar Typer como adaptador CLI inicial.

Typer no forma parte del kernel y debe poder reemplazarse.

## Consecuencias

- Se obtiene una CLI rapida para v0.1-v0.4.
- La logica de comandos debe delegar en servicios internos.
- Un REPL propio puede reemplazar o complementar Typer mas adelante.

## Reversibilidad

Alta si la CLI no contiene logica core.

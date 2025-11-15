[private]
default:
    @just --list

set positional-arguments

fmt:
    uv run ruff check --select=I --fix
    uv run ruff format

ruff:
    uv run ruff check
    uv run ruff format --check

mypy:
    uv run mypy src

@run *args:
    uv run samarium $@

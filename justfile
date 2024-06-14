[private]
default:
    @just --list

set positional-arguments

fmt:
    poetry run ruff check --select=I --fix
    poetry run ruff format

ruff:
    poetry run ruff check
    poetry run ruff format --check

mypy:
    poetry run mypy samarium

@run *args:
    poetry run samarium $@

[private]
default:
    @just --list

set positional-arguments

fmt:
    poetry run ruff check --select=I --fix
    poetry run ruff format

mypy:
    poetry run mypy samarium

@run *args:
    poetry run samarium $@

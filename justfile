venv := "venv"

default:
    @just --list

[script]
venv force="false":
    if [ -d "{{venv}}" ] && [ "{{force}}" != "true" ]; then exit 0; fi
    uv venv --clear {{venv}}

install:
    uv tool install --editable .

install-dev: venv
    UV_PROJECT_ENVIRONMENT={{venv}} uv sync --extra dev

test: venv
    {{venv}}/bin/pytest

test-cov: venv
    {{venv}}/bin/pytest --cov=spek --cov-report=term-missing

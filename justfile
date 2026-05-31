default:
    @just --list

[script]
venv force="false":
    if [ -d ".venv" ] && [ "{{force}}" != "true" ]; then exit 0; fi
    uv venv --clear .venv

install:
    uv tool install --editable .

install-dev: venv
    UV_PROJECT_ENVIRONMENT=.venv uv sync --extra dev

sync:
    .venv/bin/kanon sync --pull

test: venv
    .venv/bin/pytest

test-cov: venv
    .venv/bin/pytest --cov=kanon --cov-report=term-missing

default:
    @just --list

install:
    uv pip install -e .

install-dev:
    uv pip install -e ".[dev]"

test:
    uv run pytest

test-cov:
    uv run pytest --cov=spek --cov-report=term-missing

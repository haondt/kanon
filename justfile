default:
    @just --list

install:
    uv pip install -e .

install-dev:
    uv pip install -e ".[dev]"

test:
    pytest

test-cov:
    pytest --cov=spek --cov-report=term-missing

# Python virtual environment

- Always use a virtual environment; never install packages into the system Python
- The venv is always at `./venv` relative to the project root unless otherwise stated in the STRUCTURE.md
- Run the application via `./venv/bin/python`
- Run tests via `./venv/bin/pytest` (or the relevant test runner under `./venv/bin/`)
- Never invoke `python`, `pip`, or test runners globally — always through `./venv/bin/`

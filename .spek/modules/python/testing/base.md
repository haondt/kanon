---
spek:
  description: "Test layout and assertion conventions"
---

# Python testing conventions

- Organize tests under `tests/`; mirror the source layout (`src/pkg/core/foo.py` → `tests/core/test_foo.py`)
- Test names describe the scenario: `test_load_missing_file_raises`, `test_returns_empty_list_when_no_input`
- Prefer real objects over mocks; only mock at external boundaries (filesystem, network, subprocesses)
- One logical assertion per test where practical; use a dedicated assertion library or built-in `assert` — do not mix styles
- Tests must be deterministic and order-independent

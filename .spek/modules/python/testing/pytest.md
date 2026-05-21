---
spek:
  description: "pytest-specific conventions"
---

# pytest conventions

- Use `pytest.raises` for exception assertions; never catch exceptions manually in tests
- Use fixtures for shared setup; prefer function-scoped fixtures unless shared state is intentional
- Parametrize with `@pytest.mark.parametrize` rather than loops inside a test body
- Do not use `unittest.TestCase`; write plain functions
- Run the full suite before committing: `pytest`
- Async tests: use `pytest-anyio` or `pytest-asyncio`; mark with `@pytest.mark.anyio` or `@pytest.mark.asyncio`

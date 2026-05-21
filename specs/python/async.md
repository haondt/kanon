---
spek:
  description: "Async/await and concurrency patterns"
---

# Python async conventions

- Use `async`/`await` throughout; do not mix sync and async in the same call chain
- Prefer `asyncio` as the event loop; avoid threads for I/O-bound work
- Use `asyncio.TaskGroup` (Python 3.11+) for concurrent tasks instead of `asyncio.gather` where error handling matters
- Do not call blocking I/O (file reads, `requests`, `time.sleep`) inside async functions — use async equivalents (`aiofiles`, `httpx`, `asyncio.sleep`)
- Annotate async functions with `async def` and return type; avoid `Coroutine[...]` in signatures — just annotate the return value
- Test async code with `pytest-anyio` or `pytest-asyncio`; mark async test functions appropriately

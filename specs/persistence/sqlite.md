---
spek:
  description: "SQLite conventions and WAL mode"
---

# SQLite

- Always enable WAL mode (`PRAGMA journal_mode=WAL`) for better concurrent read performance
- Always enable foreign key enforcement (`PRAGMA foreign_keys=ON`) — it is off by default

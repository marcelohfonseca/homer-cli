# Homer — AI Agent Instructions

## Project Overview

Homer is a personal productivity CLI for developers with native integrations for **Jira** and **Clockify**.

The project is written in Python and designed as a modular system where new integrations can be added without modifying existing functionality.

---

## Current State

The initial migration from PowerShell is **complete**. Homer is a fully functional Python application published on PyPI as `homer-cli`.

Current integrations:

- **Clockify** — timer start/stop, current timer, summary and detailed reports
- **Jira** — list issues, view, create, comment, mention

Future integrations may include Git, GitHub, and Microsoft Teams.

Repository structure:

```
src/homer/
    cli.py              # Root CLI app (registers clockify, ck, jira)
    config.py           # Settings from ~/.env via pydantic-settings
    exceptions.py       # Error types

    clockify/
        commands.py     # Typer CLI commands + Rich output
        service.py      # Business logic
        client.py       # httpx HTTP client
        models.py       # Pydantic models

    jira/
        commands.py
        service.py
        client.py
        models.py

tests/                  # pytest test suite
pyproject.toml          # PDM project config + commitizen
```

---

## Before Implementing

1. Inspect the existing project structure.
2. Understand the current architecture.
3. Identify affected files.
4. Explain the proposed approach.
5. Keep changes small, reviewable, and tested.

---

## Architecture Principles

Homer follows a **layered architecture** with clear separation of concerns:

### `commands.py`
- Typer CLI commands
- Argument parsing
- Rich output formatting
- User interaction (prompts, selectors)
- Must **not** contain business logic

### `service.py`
- Business rules and workflow orchestration
- Must **not** perform HTTP requests
- Must **not** print output
- Must be independently testable

### `client.py`
- HTTP communication via `httpx`
- Authentication, retries, pagination
- API-specific error handling
- Must **never** use `requests`

### `models.py`
- Pydantic models for API contracts and domain entities
- Use `extra="allow"` on models that receive external API responses

---

## Technology Stack

- Python 3.12+
- PDM (dependency and build manager)
- Typer (CLI framework)
- Rich (terminal output)
- httpx (HTTP client)
- pydantic-settings (configuration)
- pytest (tests)
- commitizen (versioning and changelog)

Use existing dependencies before introducing new ones.

---

## Configuration

Credentials are stored in `~/.env` and loaded via `pydantic-settings`. Never hardcode credentials. If required configuration is missing: fail fast with a clear error message.

---

## Code Style

- Type hints everywhere
- Google-style docstrings
- Small, focused functions
- Explicit over clever
- Composition over inheritance
- No global state
- No static utility classes

---

## Error Handling

- `client.py` raises API and communication exceptions
- `service.py` raises business exceptions
- `commands.py` converts exceptions into user-friendly Rich messages

---

## Testing

- Business logic must be testable without network access
- Mock all external API calls
- Keep tests deterministic
- Run with: `pdm run pytest tests/`

---

## Versioning

Uses `commitizen` with conventional commits:

```bash
pdm run cz bump --yes          # bump version + generate CHANGELOG
git tag -s "X.Y.Z" -m "..."   # sign the tag manually after bump
pdm build && git push origin develop --tags
```

---

## Non-Goals

Homer is not intended to:

- Become a generic automation framework
- Execute arbitrary scripts
- Expose low-level API wrappers as CLI commands

Only implement workflows that provide real developer productivity value.

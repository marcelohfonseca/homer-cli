# Homer AI Instructions

## Project Overview

Homer is a personal productivity CLI application for developers.

The purpose of Homer is to replace a collection of PowerShell automation
functions with a well-structured Python application.

Current integrations:

* Jira
* Clockify

Future integrations may include:

* Git
* GitHub
* Microsoft Teams

The application must be designed as a modular system where new integrations
can be added without modifying existing functionality.

The goal is to create a native Python application, not a direct translation of
PowerShell scripts.

---

## Current Project State

The project is currently in the initial migration phase.

Repository structure:

```txt
src/        Application source code
tests/      Automated tests
legacy/     Original PowerShell implementation
pyproject.toml  Project configuration
README.md   Project documentation
```

Before implementing new features:

1. Inspect the existing project structure.
2. Understand the current architecture.
3. Identify missing components.
4. Propose an implementation approach.
5. Avoid creating large amounts of code without understanding the required behaviour.

---

## Legacy PowerShell Implementation

The file:

```txt
legacy/legacy.psm1
```

contains the original PowerShell functions that are being migrated.

This file is the functional specification of Homer.

The legacy implementation defines:

* expected behaviours
* workflows
* integrations
* API interactions
* user-facing functionality

## Migration Rules

When migrating functionality:

* Treat `legacy/legacy.psm1` as the source of truth for behaviour.
* Never modify legacy files unless explicitly requested.
* Do not translate PowerShell code line by line.
* Do not preserve PowerShell naming conventions.
* Extract the intent and redesign the implementation using Python best practices.

For each migrated feature:

1. Understand the PowerShell function purpose.
2. Identify inputs and outputs.
3. Identify side effects.
4. Identify external dependencies.
5. Design Python components.
6. Implement tests.
7. Validate behaviour matches the original workflow.

---

## Migration Principles

The migration must prioritize:

* maintainability
* testability
* modularity
* readability
* Python best practices

Avoid:

* one Python file per PowerShell function
* classes created only to mirror functions
* preserving outdated naming
* unnecessary abstractions

Prefer:

* domain-oriented design
* reusable services
* clear responsibilities
* composition over inheritance

Example:

Avoid:

```txt
Clockify-Start
Clockify-Stop
Clockify-Status
```

Become:

```txt
clockify/
    client.py
    service.py
    commands.py
    models.py
```

---

## Implementation Strategy

Prefer vertical feature migration.

A complete feature should include:

1. CLI command
2. Business logic
3. External client integration
4. Data models
5. Automated tests

Avoid creating empty frameworks or abstractions without an immediate use case.

Keep every change small, reviewable and executable.

Before significant changes:

* Explain the proposed approach.
* Identify affected files.
* Describe architectural decisions.

---

## Technology Stack

Required technologies:

* Python 3.14+
* PDM
* Typer
* Rich
* httpx
* pydantic-settings
* pytest

Use existing technologies before introducing new dependencies.

---

## Dependencies

Before adding a dependency:

* Verify the functionality cannot be implemented using existing dependencies.
* Prefer mature and maintained libraries.
* Explain why the dependency is necessary.
* Avoid dependencies for small helper functions.

---

## Architecture

The project follows a modular integration architecture.

Expected structure:

```txt
src/homer/

    cli.py
    config.py
    exceptions.py

    jira/
        commands.py
        service.py
        client.py
        models.py

    clockify/
        commands.py
        service.py
        client.py
        models.py
```

---

## Component Responsibilities

## commands.py

Responsible for:

* Typer CLI commands
* argument parsing
* calling services
* formatting Rich output
* handling user interaction

Must not contain business rules.

---

## service.py

Responsible for:

* business rules
* workflow orchestration
* domain logic

Must:

* not perform HTTP requests
* not print output
* remain independently testable

---

## client.py

Responsible for:

* HTTP communication
* authentication
* retries
* pagination
* API-specific behaviour

Use:

```txt
httpx
```

Never use:

```txt
requests
```

---

## models.py

Responsible for:

* Pydantic models
* request/response contracts
* domain data structures

---

## Configuration

Never hardcode credentials.

Configuration must use:

```txt
pydantic-settings
```

Support environment variables.

---

## Initialization

After installation, users must execute:

```txt
homer init
```

before using other commands.

The init command must:

* create or update required environment variables
* store configuration in:

```txt
$HOME/.env
```

* work across operating systems
* preserve existing values whenever possible

---

## Missing Configuration

If required configuration is missing:

* fail fast
* raise a clear error
* explain exactly which configuration is missing

---

## Console Output

Use:

```txt
Rich
```

for all CLI output.

Rules:

* Services never print.
* Clients never print.
* Only CLI commands handle presentation.

---

## HTTP Guidelines

Use:

```txt
httpx
```

Design clients with future async compatibility in mind.

Handle:

* authentication
* retries
* pagination
* API errors

inside client implementations.

---

## Code Style

Follow these rules:

* type hints everywhere
* Google-style docstrings
* small functions
* explicit code
* composition over inheritance
* avoid global state
* avoid static utility classes

---

## Error Handling

Architecture layers:

Client:

* raises API and communication exceptions.

Service:

* raises business exceptions.

CLI:

* converts exceptions into user-friendly messages.

---

## Testing

Business logic must be testable without network access.

Rules:

* mock external APIs
* test services independently
* keep tests deterministic

---

## Naming Guidelines

Prefer domain names.

Examples:

Good:

```txt
JiraClient
JiraService
ClockifyClient
start_timer()
stop_timer()
```

Avoid:

```txt
StartClockifyTimerFunction
Clockify-Start
Invoke-JiraAction
```

Do not copy PowerShell naming conventions.

---

## Non Goals

Homer is not intended to:

* become a generic automation framework
* execute arbitrary scripts
* expose every legacy helper function as a CLI command
* preserve PowerShell architecture

Only migrate workflows that provide real developer productivity value.

---

## Final Goal

The final codebase should feel like it was originally designed in Python.

The migration is successful when:

* behaviour is preserved
* architecture is improved
* code is maintainable
* features are tested
* future integrations can be added safely

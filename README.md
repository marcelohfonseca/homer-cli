# Homer 🏠

Homer is a personal productivity CLI for developers — Jira and Clockify integrations from your terminal.

## Documentation

- **[INSTALL.md](INSTALL.md)** — Installation, credentials, and configuration
- **[USAGE.md](USAGE.md)** — Full feature guide and workflows
- **[CHEATSHEET.md](CHEATSHEET.md)** — Quick command reference
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Common issues and solutions

---

## Features

### ⏱️ Clockify Time Tracking
- Start/stop timers with description, project, and tags
- Interactive selectors for projects (from Clockify + Jira) and tags
- View the currently running timer with elapsed time
- Summary and detailed reports by date range, project, or tag

### 🎯 Jira Issue Management
- List your open issues
- View issue details (status, priority, assignee, description)
- Create issues with type, priority, and description
- Comment on issues and mention teammates

---

## Installation

```bash
pipx install homer-cli   # recommended
homer init               # interactive credential setup
```

See [INSTALL.md](INSTALL.md) for detailed instructions.

---

## Quick Start

```bash
homer init                                  # configure credentials

homer jira list                             # see your open issues
homer jira view NDI-123                     # view issue details

homer ck start "Fixing login bug"           # start a timer
homer ck start "Code review" -p "web-api"   # with project
homer ck start "Standup" -T                 # open tag selector
homer ck current                            # check elapsed time
homer ck stop                               # stop all timers

homer ck summary 2026-01-01 2026-01-31      # monthly report
```

---

## Commands Reference

> Both `homer clockify` and `homer ck` are equivalent.

### Global

| Command | Description |
|---|---|
| `homer init` | Interactive credential setup (saves to `~/.env`) |
| `homer --version` | Show installed version |
| `homer --help` | Show all available commands |

### Clockify — Timers

| Command | Description |
|---|---|
| `homer ck start DESCRIPTION` | Start a timer |
| `homer ck start DESCRIPTION -p PROJECT` | Start with project name or Jira key |
| `homer ck start DESCRIPTION -p ""` or `-s` | Start and open interactive project selector |
| `homer ck start DESCRIPTION -t "tag1,tag2"` | Start with tags |
| `homer ck start DESCRIPTION -t ""` or `-T` | Start and open interactive tag selector |
| `homer ck current` | Show currently running timer |
| `homer ck stop` | Stop all running timers |

**`start` options:**

| Option | Short | Description |
|---|---|---|
| `--project PROJECT` | `-p` | Project name or Jira key. Empty string or `-s` opens selector |
| `--tags TAGS` | `-t` | Comma-separated tags. Empty string or `-T` opens selector |
| `--select` | `-s` | Open interactive project selector |
| `--select-tags` | `-T` | Open interactive tag selector |

### Clockify — Reports

| Command | Description |
|---|---|
| `homer ck summary DATE_FROM DATE_TO` | Summary report grouped by project |
| `homer ck summary DATE_FROM DATE_TO -g DATE` | Group by date |
| `homer ck summary DATE_FROM DATE_TO -g TAG` | Group by tag |
| `homer ck summary DATE_FROM DATE_TO -p PROJECT` | Filter by project |
| `homer ck summary DATE_FROM DATE_TO -t TAG` | Filter by tag |
| `homer ck detailed DATE_FROM DATE_TO` | Detailed time entries |
| `homer ck detailed DATE_FROM DATE_TO -p PROJECT` | Detailed filtered by project |

Dates use `YYYY-MM-DD` format.

### Jira

| Command | Description |
|---|---|
| `homer jira list` | List your open issues |
| `homer jira view KEY` | View issue details |
| `homer jira create SUMMARY` | Create issue (default type: Story, project: from config) |
| `homer jira create SUMMARY -p KEY -t TYPE --priority P -d TEXT` | Create with all options |
| `homer jira comment KEY MESSAGE` | Add a comment |
| `homer jira mention KEY USERNAME MESSAGE` | Mention a user in a comment |

**`create` options:**

| Option | Short | Default |
|---|---|---|
| `--project KEY` | `-p` | `DEFAULT_PROJECT` from config |
| `--type TYPE` | `-t` | `Story` |
| `--priority LEVEL` | | `Medium` |
| `--description TEXT` | `-d` | _(none)_ |

---

## Configuration

Homer reads credentials from `~/.env`:

```env
JIRA_BASE_URL=https://company.atlassian.net
JIRA_USER=you@company.com
JIRA_API_TOKEN=your_token

CLOCKIFY_API_KEY=your_api_key
CLOCKIFY_WORKSPACE=workspace_id
CLOCKIFY_USER=alphanumeric_user_id
```

> ⚠️ `CLOCKIFY_USER` must be the alphanumeric ID (e.g. `646b733087e7196c5c918748`), **not** your email.  
> Get it with: `curl -H "X-Api-Key: YOUR_KEY" https://api.clockify.me/api/v1/user | grep '"id"'`

Run `homer init` to set or update credentials interactively.

---

## Project Structure

```
src/homer/
├── cli.py            # Root CLI (registers clockify, ck, jira)
├── config.py         # Settings from ~/.env
├── exceptions.py     # Error types
├── clockify/
│   ├── client.py     # HTTP client (httpx)
│   ├── service.py    # Business logic
│   ├── commands.py   # CLI commands (Typer + Rich)
│   └── models.py     # Pydantic models
└── jira/
    ├── client.py
    ├── service.py
    ├── commands.py
    └── models.py
tests/                # pytest test suite
```

---

## Development

```bash
git clone https://github.com/marcelohfonseca/homer-cli.git
cd homer && pdm install

pdm run pytest tests/          # run tests
pdm run ruff check src/        # lint
pdm run mypy src/               # type check
pdm run homer --help            # run from source
```

---

## License

MIT — see LICENSE file.

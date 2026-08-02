# Usage Guide

## Table of Contents

- [Clockify Timers](#clockify-timers)
- [Clockify Reports](#clockify-reports)
- [Jira Issues](#jira-issues)
- [Typical Workflows](#typical-workflows)

> Both `homer clockify` and `homer ck` work — `ck` is the short alias.

---

## Clockify Timers

### Start a timer

```bash
homer ck start "Fixing login bug"
```

With a project:
```bash
homer ck start "Code review" -p "web-api"
homer ck start "Code review" -p "NDI-12345"   # bare Jira key → fetches summary → creates [NDI-12345] Summary
```

With tags:
```bash
homer ck start "Standup" -t "meetings"
homer ck start "Feature work" -t "backend,feature"
```

### Interactive project selector

Opens a numbered list combining Clockify projects and your open Jira issues:

```bash
homer ck start "Task" -p ""    # -p with empty string
homer ck start "Task" -s       # --select flag
```

Pick by number, type a free-form name, or press Enter to skip.

### Interactive tag selector

Opens a numbered list of existing Clockify tags. Supports comma-separated multi-selection:

```bash
homer ck start "Task" -t ""    # -t with empty string
homer ck start "Task" -T       # --select-tags flag
```

Pick multiple tags: `1,3` — or type a new tag name.

### Combine selectors

```bash
homer ck start "Task" -p "" -T     # open both selectors
homer ck start "Task" -s -T        # flags form
```

### Check current timer

```bash
homer ck current
```

Shows description, elapsed time, project, and tags.

### Stop timers

```bash
homer ck stop
```

Stops all running timers and shows the final duration.

---

## Clockify Reports

Dates use `YYYY-MM-DD` format.

### Summary report

```bash
homer ck summary 2026-01-01 2026-01-31
```

Groups by project by default. Change grouping:

```bash
homer ck summary 2026-01-01 2026-01-31 -g DATE     # by date
homer ck summary 2026-01-01 2026-01-31 -g TAG      # by tag
homer ck summary 2026-01-01 2026-01-31 -g PROJECT  # by project (default)
```

Filter by project or tag:

```bash
homer ck summary 2026-01-01 2026-01-31 -p "web-api"
homer ck summary 2026-01-01 2026-01-31 -t "feature"
homer ck summary 2026-01-01 2026-01-31 -p "web-api" -t "feature"
```

### Detailed report

```bash
homer ck detailed 2026-01-01 2026-01-31
homer ck detailed 2026-01-01 2026-01-31 -p "web-api"
```

Shows every time entry with date, description, project, start/end, and duration.

---

## Jira Issues

### List your open issues

```bash
homer jira list
```

Shows all issues assigned to you that are not Done.

### View issue details

```bash
homer jira view NDI-123
```

Shows key, summary, status, priority, assignee, and description.

### Create an issue

Minimal:
```bash
homer jira create "Fix login bug"
```

With options:
```bash
homer jira create "Implement 2FA" \
  --project NDI \
  --type Story \
  --priority High \
  --description "Add TOTP-based two-factor authentication."
```

| Option | Short | Default |
|---|---|---|
| `--project` | `-p` | `DEFAULT_PROJECT` from `~/.env` |
| `--type` | `-t` | `Story` |
| `--priority` | | `Medium` |
| `--description` | `-d` | _(none)_ |

### Comment on an issue

```bash
homer jira comment NDI-123 "Ready for QA review"
```

### Mention a teammate

```bash
homer jira mention NDI-123 "alice" "Can you review this?"
```

Homer finds the user by name/email and adds a proper Jira mention.

---

## Typical Workflows

### Track time on a Jira issue

```bash
homer jira list                                   # see what's assigned
homer jira view NDI-456                           # read the issue

homer ck start "NDI-456 · Implementing feature" -p "" -T
# → opens project selector (pick or create) and tag selector

# ... work ...

homer ck current                                  # check elapsed time
homer ck stop                                     # done

homer jira comment NDI-456 "Implementation complete, ready for review"
homer jira mention NDI-456 "alice" "Please review when you can"
```

### Daily routine

```bash
# Morning: check workload
homer jira list

# Start work
homer ck start "Working on NDI-789" -p "NDI-789" -t "feature"

# Break: switch tasks
homer ck stop
homer ck start "Team standup" -t "meetings"
homer ck stop

# Resume
homer ck start "Working on NDI-789" -p "NDI-789" -t "feature"
homer ck stop

# End of day: summary
homer ck summary 2026-08-02 2026-08-02
```

### Weekly report

```bash
homer ck summary 2026-07-28 2026-08-01
homer ck detailed 2026-07-28 2026-08-01
```

### Create issue and track immediately

```bash
homer jira create "Critical bug: users can't log in" --type Bug --priority Highest
# returns NDI-999

homer ck start "Debugging NDI-999" -p "NDI-999"
# service fetches Jira summary → creates project "[NDI-999] Critical bug: users can't log in"

homer ck stop
homer jira comment NDI-999 "Root cause identified — LDAP timeout in auth middleware. Fix deployed."
```

---

## Shell Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias hstart='homer ck start'
alias hstop='homer ck stop'
alias hnow='homer ck current'
alias hjira='homer jira list'
```

Reload: `source ~/.bashrc`


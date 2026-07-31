# Homer Cheatsheet

Quick reference for Homer commands.

## Setup

```bash
# Install
pdm install
# or: pip install -e .

# Configure
homer init

# Verify
homer --help
```

## Clockify Timers

```bash
# Start timer
homer clockify start "Task description"
homer clockify start "Task" --project "project-name" --tags "tag1,tag2"

# Check current
homer clockify current

# Stop timer
homer clockify stop
```

## Clockify Reports

```bash
# Summary (by project)
homer clockify summary 2024-01-01 2024-01-31

# By date
homer clockify summary 2024-01-01 2024-01-31 --group-by DATE

# By project filter
homer clockify summary 2024-01-01 2024-01-31 --project "web-api"

# Detailed entries
homer clockify detailed 2024-01-01 2024-01-31
```

## Jira Issues

```bash
# List your issues
homer jira list

# View issue
homer jira view NDI-123

# Create issue
homer jira create "Issue title"
homer jira create "Title" --type Story --priority High --description "Details"

# Comment on issue
homer jira comment NDI-123 "Comment text"

# Mention user
homer jira mention NDI-123 "username" "Message text"
```

## Configuration

```bash
# Initialize/update
homer init

# View config
cat ~/.env

# Edit config
nano ~/.env
```

## Tips

- **Dates:** Always use `YYYY-MM-DD` format
- **Projects:** Use exact project names (case-sensitive)
- **Tags:** Must exist in Clockify (auto-create enabled)
- **Jira users:** First match wins in searches
- **Report groups:** DATE, PROJECT, TAG

## Troubleshooting

```bash
# Test Clockify
homer clockify current

# Test Jira
homer jira list

# Check install
homer --help
homer clockify --help
homer jira --help
```

**Full documentation:** See README.md and other docs.

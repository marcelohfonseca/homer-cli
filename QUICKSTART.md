# Quick Start Guide

Get started with Homer in 5 minutes.

## 1. Installation (2 minutes)

```bash
# Recommended: pipx (isolated, globally available)
pipx install homer-cli

# Alternative: pip
pip install homer-cli

# Verify
homer --version
```

## 2. Configuration (2 minutes)

```bash
homer init
```

When prompted, provide:
- Jira base URL (e.g., `https://company.atlassian.net`)
- Jira email and API token
- Clockify API key, workspace ID, user ID

All values are saved to `~/.env`.

## 3. First Commands (1 minute)

### Check your Jira issues:
```bash
homer jira list
```

### Start timing your work:
```bash
homer clockify start "Working on feature X"
```

### See what you're working on:
```bash
homer clockify current
```

### Stop the timer:
```bash
homer clockify stop
```

Done! You're ready to use Homer.

---

## Common Commands

### Time Tracking

**Start a timer:**
```bash
homer clockify start "Task description"
homer clockify start "Code review" --project "web-api" --tags "review"
```

**Check current timer:**
```bash
homer clockify current
```

**Stop timer:**
```bash
homer clockify stop
```

**View time report:**
```bash
homer clockify summary 2024-01-01 2024-01-31
homer clockify detailed 2024-01-01 2024-01-31 --project "web-api"
```

### Issue Management

**List your issues:**
```bash
homer jira list
```

**View issue:**
```bash
homer jira view NDI-123
```

**Create issue:**
```bash
homer jira create "Fix login bug"
homer jira create "New feature" --type Story --priority High
```

**Add comment:**
```bash
homer jira comment NDI-123 "This is ready"
```

**Mention someone:**
```bash
homer jira mention NDI-123 "alice" "Please review"
```

---

## Need Help?

```bash
# See all commands
homer --help

# Get help for a specific command
homer clockify --help
homer jira --help

# Detailed help for any command
homer clockify start --help
homer jira create --help

# Update configuration
homer init
```

## Next Steps

1. Read the full [README.md](../README.md) for detailed documentation
2. Check [INSTALL.md](INSTALL.md) for troubleshooting
3. Explore commands with `--help` flags
4. Set up shell aliases (see INSTALL.md)

---

**Now go be productive! ⚡**

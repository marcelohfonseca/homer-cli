# Installation Guide

This guide walks you through installing Homer on your machine.

## Prerequisites

- **Python 3.12 or higher**
- **Jira account** with API token access
- **Clockify account** with API key access

---

## Installation Methods

Homer is distributed as a Python package (`homer-cli`) and can be installed in three ways:

### ✅ Method 1: pipx (Recommended)

[pipx](https://pipx.pypa.io) installs Homer in an isolated environment and makes the `homer` command globally available — no virtual environment to activate.

```bash
# Install pipx if you don't have it
pip install pipx
pipx ensurepath

# Install Homer
pipx install homer-cli
```

**Upgrade later:**
```bash
pipx upgrade homer-cli
```

**Uninstall:**
```bash
pipx uninstall homer-cli
```

### Method 2: pip (global or venv)

**Into a virtual environment (recommended for pip users):**
```bash
python3 -m venv ~/.venvs/homer
source ~/.venvs/homer/bin/activate   # Windows: .venvs\homer\Scripts\activate
pip install homer-cli
```

**Into the user site (no venv):**
```bash
pip install --user homer-cli
```

> After `--user` install, make sure `~/.local/bin` is on your `PATH`.

### Method 3: From source (for contributors / development)

```bash
git clone https://github.com/marcelohfonseca/homer-cli.git
cd homer
pdm install            # installs all deps + project in editable mode
pdm run homer --help   # run inside the project venv
```

---

## Verify Installation

After any install method:

```bash
homer --version
homer --help
```

Expected output:
```
homer 0.1.0
```

---

## Configuration

### Step 1: Gather Your Credentials

#### Jira

1. Log in to your Jira instance
2. Go to **Account Settings → Security → API tokens**
3. Click **Create API token**, name it "Homer", copy the token
4. Note your login email and base URL (e.g., `https://company.atlassian.net`)

Links:
- Atlassian Cloud tokens: https://id.atlassian.com/manage-profile/security/api-tokens

#### Clockify

1. Log in at https://app.clockify.me
2. **API Key:** Settings → Advanced → API key
3. **Workspace ID:** Settings → Workspaces → click the workspace → copy from the URL
4. **User ID:** Settings → Profile → copy User ID

### Step 2: Initialize Homer

Run the interactive setup:

```bash
homer init
```

You'll be prompted for each credential. Values are saved to `~/.env` and preserved on subsequent runs — press Enter to keep an existing value.

Example session:
```
╭──────────────────────────────╮
│  Homer — Initial Setup       │
│  ~/.env                      │
╰──────────────────────────────╯
Press Enter to keep an existing value.

Jira base URL (e.g. https://company.atlassian.net): https://company.atlassian.net
Jira user email: john@company.com
Jira API token: ••••••••••••••••••••
Clockify API key: ••••••••••••••••••••
Clockify workspace ID: 123abc456def
Clockify user ID: 789ghi012jkl

✓ Configuration saved to ~/.env
```

### Step 3: Verify Configuration

```bash
homer jira list       # verifies Jira connection
homer clockify current  # verifies Clockify connection
```

---

## Post-Installation

### Update Configuration

```bash
homer init            # interactive — press Enter to keep existing values
# or edit directly:
nano ~/.env
```

### Shell Aliases (Optional)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias hstart='homer clockify start'
alias hstop='homer clockify stop'
alias hcur='homer clockify current'
alias hjira='homer jira list'
```

Reload: `source ~/.bashrc`

---

## Troubleshooting

### "command not found: homer"

- **pipx users:** run `pipx ensurepath` and reload your shell
- **pip users:** activate your virtualenv (`source ~/.venvs/homer/bin/activate`)
- **pip --user users:** ensure `~/.local/bin` is in `$PATH`

### "Python 3.12+ required"

```bash
python3 --version
```

Install 3.12+ if needed:
- macOS: `brew install python@3.12`
- Ubuntu: `sudo apt-get install python3.12`
- Windows/all: https://www.python.org/downloads/

### "Configuration missing: JIRA_BASE_URL"

```bash
homer init    # re-run and fill in all fields
```

### "401 Unauthorized" from Jira

1. Regenerate token at https://id.atlassian.com/manage-profile/security/api-tokens
2. Run `homer init` to update it

### "401 Unauthorized" from Clockify

1. Regenerate API key at https://app.clockify.me/settings/user (Advanced → API)
2. Run `homer init` to update it

---

## Next Steps

- [QUICKSTART.md](QUICKSTART.md) — 5-minute workflow guide
- [USAGE.md](USAGE.md) — Comprehensive feature guide
- [EXAMPLES.md](EXAMPLES.md) — Real-world recipes
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — More problem-solving

---

**Happy productivity! 🚀**


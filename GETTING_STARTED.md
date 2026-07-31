# First Time Setup Guide

Complete step-by-step guide for first-time Homer users.

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] **Python 3.13+** installed
- [ ] **Jira account** access
- [ ] **Clockify account** access
- [ ] A terminal/command line ready

### Check Python Version

```bash
python --version
# Should show: Python 3.13.0 or higher
```

If you don't have Python 3.13+, install it from https://www.python.org/downloads/

---

## Step 1: Get Your Credentials

### Jira Credentials

1. **Get your Jira Base URL:**
   - Open your Jira instance (e.g., https://company.atlassian.net)
   - Look at the URL in your browser
   - This is your **Jira Base URL**
   - Example: `https://company.atlassian.net`

2. **Get your email:**
   - This is the email you use to log into Jira
   - Example: `john.doe@company.com`

3. **Generate an API Token:**
   - Go to: https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API Token"
   - Name it "Homer"
   - Copy the token (save it somewhere safe)

### Clockify Credentials

1. **Get your API Key:**
   - Go to: https://app.clockify.me/settings/user
   - Scroll down to "API Key" section
   - Copy your API key (save it somewhere safe)

2. **Get your Workspace ID:**
   - Go to: https://app.clockify.me/settings/workspaces
   - Copy your workspace ID (usually shows in the URL or list)

3. **Get your User ID:**
   - Go to: https://app.clockify.me/settings/user
   - Look for "User ID" section
   - Copy it (save it somewhere safe)

---

## Step 2: Install Homer

### Option A: pipx (Recommended)

[pipx](https://pipx.pypa.io) installs Homer in an isolated environment and exposes `homer` globally — no virtualenv to manage.

```bash
# Install pipx (if you don't have it)
pip install pipx
pipx ensurepath

# Install Homer
pipx install homer-cli

# Verify
homer --version
```

### Option B: pip into a virtual environment

```bash
# Create a dedicated virtual environment
python3 -m venv ~/.venvs/homer

# Activate it
source ~/.venvs/homer/bin/activate  # Linux/Mac
# or:
~\.venvs\homer\Scripts\activate     # Windows

# Install Homer
pip install homer-cli

# Verify
homer --version
```

> With this method you need to activate the virtualenv each time, or add `~/.venvs/homer/bin` to your `PATH`.

### Option C: From source (contributors)

```bash
git clone https://github.com/marcelohfonseca/homer-cli.git
cd homer
pdm install
pdm run homer --version
```

---

## Step 3: Configure Homer

### Run Initialization

```bash
homer init
```

You'll see prompts like this:

```
Jira Base URL (e.g., https://company.atlassian.net): 
```

**For each prompt, enter the credentials you gathered in Step 1:**

1. **Jira Base URL** → Enter your full Jira URL (from Step 1)
   ```
   Example: https://company.atlassian.net
   ```

2. **Jira Email** → Enter your Jira login email
   ```
   Example: john.doe@company.com
   ```

3. **Jira API Token** → Paste the token you generated
   ```
   Example: aBcDeFgHiJkLmNoP1234567
   ```

4. **Clockify API Key** → Paste your Clockify API key
   ```
   Example: 1a2b3c4d5e6f7g8h9i0j1k2l
   ```

5. **Clockify Workspace ID** → Enter your workspace ID
   ```
   Example: 61f5a6c8d1e2f3g4h5i6j7k
   ```

6. **Clockify User ID** → Enter your user ID
   ```
   Example: 61a2b3c4d5e6f7g8h9i0j1k
   ```

When complete, you'll see:
```
✓ Configuration saved to ~/.env
```

---

## Step 4: Verify Everything Works

### Test Clockify

```bash
homer clockify current
```

You should see either:
- No timer running
- Or details of your current timer

### Test Jira

```bash
homer jira list
```

You should see a list of your open Jira issues.

If both commands work, **you're all set!** 🎉

---

## Step 5: Quick Test

### Create Your First Timer

```bash
homer clockify start "Testing Homer"
```

### Check It's Running

```bash
homer clockify current
```

You should see the timer counting up.

### Stop It

```bash
homer clockify stop
```

### Verify in Clockify

- Go to https://app.clockify.me
- Check your time entries
- You should see "Testing Homer" entry

---

## Setup Aliases (Optional)

To make commands easier, add these to your shell profile:

### For Bash (~/.bashrc or ~/.bash_profile)

```bash
alias ht='homer clockify'
alias hj='homer jira'
alias hc='homer clockify current'
alias hs='homer clockify stop'
```

Then reload:
```bash
source ~/.bashrc
```

Now you can use:
```bash
ht start "My task"  # Instead of: homer clockify start "My task"
hc                   # Instead of: homer clockify current
```

### For Zsh (~/.zshrc)

Same as Bash, add to ~/.zshrc and reload:
```bash
source ~/.zshrc
```

### For PowerShell ($PROFILE)

```powershell
Set-Alias -Name ht -Value homer
Set-Alias -Name hc -Value {homer clockify current}
Set-Alias -Name hs -Value {homer clockify stop}
```

---

## Troubleshooting Setup

### "Configuration missing" Error

**Problem:** `ConfigurationError: Missing required configuration: JIRA_BASE_URL`

**Solution:** Run initialization again:
```bash
homer init
```

Make sure to fill in ALL fields (don't skip any).

### "401 Unauthorized" Error

**Problem:** Can't authenticate with Jira or Clockify

**Jira fix:**
1. Verify email is correct: `cat ~/.env | grep JIRA`
2. Generate new API token: https://id.atlassian.com/manage-profile/security/api-tokens
3. Re-run: `homer init`

**Clockify fix:**
1. Verify API key: https://app.clockify.me/settings/user
2. Generate new key if needed
3. Re-run: `homer init`

### "Command not found" Error

**If using PDM:**
```bash
pdm run homer --help  # Always use pdm run
```

**If using pip:**
1. Activate virtualenv: `source venv/bin/activate`
2. Then run: `homer --help`

### "Module not found" Error

**PDM users:** Skip this, use `pdm run`

**Pip users:**
```bash
# Make sure you installed in editable mode
pip install -e .

# And virtualenv is activated
source venv/bin/activate
```

---

## Next Steps

Once setup is complete:

1. **Read Quick Start:** [QUICKSTART.md](QUICKSTART.md) - 5-minute workflow guide
2. **Explore Examples:** [EXAMPLES.md](EXAMPLES.md) - Real-world scenarios
3. **Learn Advanced:** [USAGE.md](USAGE.md) - Comprehensive feature guide
4. **Get Help:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

---

## Common Workflows

### Track Time on Task

```bash
# Start
homer clockify start "Implementing login feature" --project "web-api" --tags "feature"

# ... do work ...

# Check time
homer clockify current

# Stop
homer clockify stop
```

### Update Jira Issue

```bash
# View issue
homer jira view NDI-123

# Add comment
homer jira comment NDI-123 "Implementation complete, ready for review"

# Mention reviewer
homer jira mention NDI-123 "alice" "Please review when you have time"
```

### Weekly Report

```bash
# Monday start date
START=$(date -d "monday this week" +%Y-%m-%d)

# Friday end date
END=$(date -d "today" +%Y-%m-%d)

# Show summary
homer clockify summary $START $END
```

---

## Getting Help

If you get stuck:

1. **Check the error message** - It usually tells you what's wrong
2. **Verify credentials** - `cat ~/.env`
3. **Re-run init** - `homer init`
4. **Read documentation:**
   - [README.md](README.md) - Overview
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
   - [EXAMPLES.md](EXAMPLES.md) - Real scenarios
5. **Check Homer help** - `homer --help`

---

**You're ready to use Homer! Start with the [QUICKSTART.md](QUICKSTART.md) guide.**


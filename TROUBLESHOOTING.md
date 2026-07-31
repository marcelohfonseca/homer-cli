# Troubleshooting Guide

Common issues and solutions.

## Installation Issues

### Command Not Found

**Problem:** After installation, `homer` command doesn't work.

**Solutions:**

1. **pipx users:** run `pipx ensurepath` and reload your shell:
   ```bash
   pipx ensurepath
   source ~/.bashrc   # or: source ~/.zshrc
   homer --help
   ```

2. **pip + venv users:** activate the virtualenv:
   ```bash
   source ~/.venvs/homer/bin/activate
   homer --help
   ```

3. **pip --user users:** ensure `~/.local/bin` is on your PATH:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   homer --help
   ```

4. **Reinstall if needed:**
   ```bash
   pipx install homer-cli          # pipx
   pip install homer-cli           # pip
   # from source:
   pdm install && pdm run homer --help
   ```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'homer'`

**Solutions:**

```bash
# pipx reinstall
pipx install homer-cli --force

# pip: make sure the venv is activated
source ~/.venvs/homer/bin/activate
pip install homer-cli

# from source (development)
cd /path/to/homer && pdm install
```

### Permission Denied on ~/.env

**Problem:** `PermissionError: [Errno 13] Permission denied: '/home/user/.env'`

**Solution:**

```bash
# Fix file permissions
chmod 600 ~/.env

# Or reset it
rm ~/.env
homer init
```

---

## Configuration Issues

### Missing Configuration Error

**Problem:** `ConfigurationError: Missing required configuration: CLOCKIFY_API_KEY`

**Solution:**

1. **Run init again:**
   ```bash
   homer init
   ```
   Re-enter all credentials.

2. **Manually verify ~/.env:**
   ```bash
   cat ~/.env
   ```
   Make sure all required keys are present:
   - `CLOCKIFY_API_KEY`
   - `JIRA_BASE_URL`
   - `JIRA_EMAIL`
   - `JIRA_API_TOKEN`
   - `DEFAULT_PROJECT`
   - `DEFAULT_WORKSPACE` (optional)

3. **Fix manually if needed:**
   ```bash
   # Edit the file
   nano ~/.env
   
   # Add missing lines, for example:
   # CLOCKIFY_API_KEY=xxxxxxx
   # JIRA_BASE_URL=https://jira.company.com
   ```

### Wrong Credentials

**Problem:** `401 Unauthorized` or `403 Forbidden` errors

**Solutions:**

1. **For Clockify:**
   ```bash
   # Get API key from: https://clockify.me/app/settings/developer
   # Regenerate if forgotten
   
   # Update and test
   homer init
   homer clockify current  # Should work
   ```

2. **For Jira:**
   ```bash
   # Verify email and token
   # Email should match your Jira account
   # Token from: https://id.atlassian.com/manage-profile/security/api-tokens
   
   # Update and test
   homer init
   homer jira list  # Should work
   ```

3. **Check base URL format:**
   ```bash
   # Should be like: https://company.atlassian.net
   # NOT: https://company.atlassian.net/ (no trailing slash)
   # NOT: company.atlassian.net (no https://)
   
   nano ~/.env  # Fix if needed
   ```

---

## Clockify Issues

### Timer Won't Start

**Problem:** `ClockifyError: Could not start timer`

**Solutions:**

1. **Check if timer is already running:**
   ```bash
   homer clockify current
   ```
   If yes, stop it first:
   ```bash
   homer clockify stop
   ```

2. **Verify API key is valid:**
   ```bash
   homer init  # Re-enter credentials
   ```

3. **Check workspace:**
   ```bash
   # If workspace is set but wrong, reset it
   nano ~/.env
   # Delete the DEFAULT_WORKSPACE line or set to empty
   
   homer clockify current
   ```

### "Project Not Found" Error

**Problem:** `ClockifyError: Project 'my-project' not found`

**Solution:**

1. **List available projects:**
   ```bash
   homer clockify --help
   # See the --project option for available projects
   ```

2. **Create the project if needed:**
   - Go to Clockify: https://clockify.me
   - Create the project
   - Then use it:
   ```bash
   homer clockify start "Task" --project "my-project"
   ```

3. **Use exact project name:**
   ```bash
   # Project names are case-sensitive and must match exactly
   # If created as "Web-API", use "Web-API", not "web-api"
   ```

### "Tag Not Found" Error

**Problem:** `ClockifyError: Tag 'backend' not found`

**Solutions:**

1. **Create the tag first:**
   - In Clockify: https://clockify.me/app/settings/tags
   - Create the tag manually
   - Then use it

2. **Or, just use the tag with --create flag** (if available):
   ```bash
   homer clockify start "Task" --tags "backend" --create-tags
   ```

3. **Use exact tag name:**
   ```bash
   # Tags are case-sensitive
   # If tag is "Backend", use "Backend" not "backend"
   ```

### Reports Show No Data

**Problem:** `homer clockify summary` returns empty results

**Solutions:**

1. **Check date range:**
   ```bash
   # Dates should be YYYY-MM-DD
   # Example: 2024-01-15 to 2024-01-31
   
   homer clockify summary 2024-01-15 2024-01-31
   ```

2. **Verify you have entries in date range:**
   - Go to Clockify: https://clockify.me/time-entries
   - Check if there are entries in that date range

3. **Check timezone:**
   - Clockify stores times in UTC
   - If you're in a different timezone, entries might appear on different dates
   - Adjust date range if needed

4. **Verify project/tag filter:**
   ```bash
   # If using filters, they must match exactly
   homer clockify summary 2024-01-01 2024-01-31 --project "web-api"
   
   # Project must exist with exact name
   ```

---

## Jira Issues

### "Connection Refused"

**Problem:** `ConnectionError: Cannot connect to Jira at https://company.atlassian.net`

**Solutions:**

1. **Check Jira URL:**
   ```bash
   nano ~/.env
   # Verify JIRA_BASE_URL is correct and accessible
   ```

2. **Test connectivity:**
   ```bash
   # Try to access from browser
   https://your-jira-url.atlassian.net
   
   # Or test from terminal
   curl -I https://your-jira-url.atlassian.net
   ```

3. **Check firewall/VPN:**
   - Some Jira instances are behind corporate firewalls
   - Make sure you have network access
   - Connect to VPN if required

### "Invalid JQL"

**Problem:** `JiraError: Invalid JQL query`

**Solutions:**

1. **This is usually fixed in code**, but if you're using custom queries:
   ```bash
   # JQL must be valid Jira Query Language
   # Check syntax at: https://www.atlassian.com/software/jira/guides/expand-jira/jql
   ```

2. **Common issues:**
   ```bash
   # Wrong: "project = NDI"
   # Right: "project = 'NDI'"
   
   # Wrong: "assignee = me"
   # Right: "assignee = currentUser()"
   ```

### "User Not Found"

**Problem:** When using `homer jira mention`, user not found

**Solutions:**

1. **Check username/email:**
   ```bash
   homer jira mention NDI-123 "john.doe" "Please review"
   # Make sure "john.doe" exists in your Jira instance
   ```

2. **Use exact search:**
   - Jira searches by display name or email
   - If user's display name is "John Doe", try that
   - Or use email: "john.doe@company.com"

3. **Verify user is in your project:**
   - User must be a member of the project
   - Otherwise they can't be assigned or mentioned

### Can't Create Issue

**Problem:** `JiraError: Could not create issue`

**Solutions:**

1. **Check issue type:**
   ```bash
   # Issue type must exist in your project
   # Common types: Story, Bug, Task, Epic
   
   homer jira create "Title" --type "Story"  # Try this
   ```

2. **Check project:**
   ```bash
   # DEFAULT_PROJECT in ~/.env must exist and you must have create permission
   
   nano ~/.env
   # Make sure DEFAULT_PROJECT is set correctly
   ```

3. **Check permissions:**
   - Go to Jira: Projects → Your Project → Project Settings
   - Verify you have "Create Issue" permission
   - If not, contact your Jira admin

### "Invalid Credentials"

**Problem:** `401 Unauthorized` for Jira

**Solutions:**

1. **Verify email and token:**
   ```bash
   # Email: your Jira login email
   # Token: from https://id.atlassian.com/manage-profile/security/api-tokens
   # Make sure token hasn't expired
   ```

2. **Generate new token if needed:**
   - Go to: https://id.atlassian.com/manage-profile/security/api-tokens
   - Delete old token
   - Create new token
   - Update Homer: `homer init`

3. **Check base URL:**
   ```bash
   # Should be your Jira subdomain
   # Examples:
   # - https://company.atlassian.net
   # - https://jira.company.com
   # NOT: https://company.atlassian.net/jira
   ```

---

## Network/Connectivity

### Timeout Errors

**Problem:** `TimeoutError` or `Request timed out`

**Solutions:**

1. **Check internet connection:**
   ```bash
   # Test connectivity
   ping google.com
   curl https://api.clockify.me
   ```

2. **Retry the command:**
   ```bash
   # Sometimes APIs are slow
   homer clockify current  # Try again
   ```

3. **Check for service status:**
   - Clockify: https://status.clockify.me/
   - Jira: Your instance status page
   - Might be under maintenance

### SSL Certificate Error

**Problem:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solutions:**

1. **Update certificates** (most common fix):
   ```bash
   # On Mac with Python from python.org
   /Applications/Python\ 3.x/Install\ Certificates.command
   ```

2. **For corporate proxy:**
   ```bash
   # If behind corporate proxy with SSL inspection
   # Try using environment variable
   export REQUESTS_CA_BUNDLE=/path/to/corporate/ca.crt
   homer clockify current
   ```

3. **Last resort** (not recommended):
   ```bash
   # Only if you know what you're doing
   export PYTHONHTTPSVERIFY=0
   homer clockify current
   ```

---

## Debugging

### Enable Verbose Output

**Problem:** Command fails but error message is unclear

**Solution:**

1. **Check the error message carefully:**
   ```bash
   homer clockify current 2>&1 | head -20
   ```

2. **Check ~/.env for issues:**
   ```bash
   # Make sure no extra whitespace
   cat ~/.env | od -c  # Shows all characters including whitespace
   ```

3. **Re-run initialization:**
   ```bash
   homer init  # Re-enter everything
   ```

### Test Each Service Separately

**Clockify test:**
```bash
homer clockify current
# If this works, Clockify is OK
```

**Jira test:**
```bash
homer jira list
# If this works, Jira is OK
```

### Check Installation

**Verify Homer is properly installed:**
```bash
# Show where Homer is installed
which homer
homer --version

# Show installed commands
homer --help

# List all available Clockify commands
homer clockify --help

# List all available Jira commands
homer jira --help
```

---

## Getting Help

If you're still stuck:

1. **Check documentation:**
   - [README.md](README.md) - Overview
   - [INSTALL.md](INSTALL.md) - Installation details
   - [USAGE.md](USAGE.md) - Feature guide
   - [EXAMPLES.md](EXAMPLES.md) - Practical examples

2. **Verify credentials:**
   ```bash
   nano ~/.env
   ```

3. **Reinstall as last resort:**
   ```bash
   # pipx
   pipx install homer-cli --force

   # pip
   pip install --upgrade homer-cli
   ```

4. **Report issue:**
   - Include error message
   - Include output of `homer --help`
   - Include output of configuration test (without showing credentials)
   - Include Python version: `python --version`

# Troubleshooting

## Installation

### `homer: command not found`

- **pipx:** `pipx ensurepath` then reload shell (`source ~/.bashrc`)
- **pip + venv:** activate the virtualenv (`source ~/.venvs/homer/bin/activate`)
- **pip --user:** ensure `~/.local/bin` is in `$PATH`

### Python version error

```bash
python3 --version   # must be 3.12+
```

Install 3.12+: [python.org/downloads](https://www.python.org/downloads/), `brew install python@3.12`, or `sudo apt install python3.12`.

---

## Configuration

### `ConfigurationError: Missing required configuration`

```bash
homer init   # re-run and fill all fields
cat ~/.env   # verify all keys are present
```

Required keys: `JIRA_BASE_URL`, `JIRA_USER`, `JIRA_API_TOKEN`, `CLOCKIFY_API_KEY`, `CLOCKIFY_WORKSPACE`, `CLOCKIFY_USER`.

### `CLOCKIFY_USER` must be alphanumeric ID, not email

```bash
curl -H "X-Api-Key: YOUR_API_KEY" https://api.clockify.me/api/v1/user \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])"
```

Copy the result into `~/.env` as `CLOCKIFY_USER=...`.

---

## Clockify

### `401 Unauthorized`

Regenerate your API key at [app.clockify.me/user/settings](https://app.clockify.me/user/settings) and run `homer init`.

### `403 Forbidden` when creating a project

Homer now uses `isPublic: true` which works on all plans. If you still see 403, check that your workspace ID in `~/.env` is correct.

### Summary report shows all zeros

- Verify the date range contains entries: check [app.clockify.me/time-entries](https://app.clockify.me/time-entries)
- Dates must be `YYYY-MM-DD`
- If filtering by project/tag, the name must match exactly

### Timer won't stop

```bash
homer ck current   # verify a timer is running
homer ck stop      # stop it
```

---

## Jira

### `401 Unauthorized`

- Verify email matches your Atlassian account
- Regenerate token at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
- Run `homer init`

### `JIRA_BASE_URL` format

Must be `https://company.atlassian.net` — no trailing slash, include `https://`.

### User not found when using `mention`

Use first name, last name, or email substring. The first matching user is selected.

### Can't create issue

- Verify `DEFAULT_PROJECT` in `~/.env` exists in Jira
- Check you have "Create Issue" permission in the project

---

## General Debugging

```bash
homer ck current       # test Clockify connection
homer jira list        # test Jira connection
homer --help           # verify CLI is working
cat ~/.env             # check configuration
homer init             # reset credentials interactively
```

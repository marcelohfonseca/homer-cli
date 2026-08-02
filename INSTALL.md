# Installation & Configuration

## Requirements

- Python 3.12+
- Jira account with API token
- Clockify account with API key

---

## Install

### pipx (Recommended)

[pipx](https://pipx.pypa.io) installs Homer in an isolated environment and makes `homer` globally available.

```bash
pip install pipx && pipx ensurepath
pipx install homer-cli
```

**Upgrade:** `pipx upgrade homer-cli`  
**Uninstall:** `pipx uninstall homer-cli`

### pip

```bash
python3 -m venv ~/.venvs/homer
source ~/.venvs/homer/bin/activate   # Windows: .venvs\homer\Scripts\activate
pip install homer-cli
```

### From source (development)

```bash
git clone https://github.com/marcelohfonseca/homer-cli.git
cd homer && pdm install
pdm run homer --help
```

---

## Verify

```bash
homer --version
homer --help
```

---

## Gather Credentials

### Jira

| What | Where |
|---|---|
| **Base URL** | Your Jira instance URL, e.g. `https://company.atlassian.net` |
| **Email** | Your Jira login email |
| **API Token** | [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) → Create API token |

### Clockify

| What | Where |
|---|---|
| **API Key** | [app.clockify.me/user/settings](https://app.clockify.me/user/settings) → Advanced → API key |
| **Workspace ID** | [app.clockify.me/workspaces](https://app.clockify.me/workspaces) → Settings → copy ID from URL |
| **User ID** | Alphanumeric ID — **not your email**. Run: `curl -H "X-Api-Key: YOUR_KEY" https://api.clockify.me/api/v1/user \| python3 -c "import sys,json; print(json.load(sys.stdin)['id'])"` |

---

## Configure

```bash
homer init
```

The wizard prompts for each credential and saves them to `~/.env`. Press Enter to keep an existing value.

To edit manually:

```bash
nano ~/.env
```

Expected `~/.env` structure:

```env
JIRA_BASE_URL=https://company.atlassian.net
JIRA_USER=you@company.com
JIRA_API_TOKEN=your_token

CLOCKIFY_API_KEY=your_api_key
CLOCKIFY_WORKSPACE=workspace_id
CLOCKIFY_USER=646b733087e7196c5c918748
```

---

## Verify Configuration

```bash
homer jira list        # confirms Jira connection
homer ck current       # confirms Clockify connection
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

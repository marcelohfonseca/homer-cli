## 0.1.10 (2026-08-02)

### Fix

- create project with isPublic=true; resolve bare Jira key before creating

## 0.1.9 (2026-08-02)

### Fix

- summary report now reads groupOne/totals from real API response

## 0.1.8 (2026-08-02)

### Fix

- accept null tagIds from Clockify API stop response

## 0.1.7 (2026-08-02)

### Feat

- rich panel output redesign for jira and clockify commands
- interactive project selector + fix create_project error message
- add ASCII art banner to homer and homer init
- package Homer as installable Python distribution (homer-cli)

### Fix

- stop timer ValidationError on PT32S duration string
- ck start behavior + report models aligned to real API response
- jira project selection + graceful 403 on project creation
- clockify current endpoint + jira portuguese status/priority colors
- correct three broken API integrations
- pre-release review corrections
- lower requires-python to >=3.12, bump to 0.1.1
- replace ASCII art with clean block-style banner in yellow

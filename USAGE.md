# Usage Guide

Comprehensive guide for using Homer's features.

## Table of Contents

- [Clockify Timer](#clockify-timer)
- [Clockify Reports](#clockify-reports)
- [Jira Issues](#jira-issues)
- [Advanced Tips](#advanced-tips)

---

## Clockify Timer

### Starting a Timer

Basic usage - just a description:
```bash
homer clockify start "Implementing user authentication"
```

With project and tags:
```bash
homer clockify start "Code review" \
  --project "web-api" \
  --tags "review,urgent"
```

With multiple tags:
```bash
homer clockify start "Backend work" \
  --project "mobile-app" \
  --tags "api,backend,production"
```

The timer starts immediately. If the project or tags don't exist, Homer creates them automatically.

### Checking Current Timer

See what you're currently working on:
```bash
homer clockify current
```

Output shows:
- Timer status (Active)
- Description
- Elapsed time
- Project and tags (if set)

If no timer is running, you'll see:
```
ℹ No timer running
```

### Stopping Timers

Stop all running timers:
```bash
homer clockify stop
```

Output shows:
- What stopped
- Total time worked
- Project and tags

You can stop multiple timers at once:
```bash
# Stops all running timers
homer clockify stop
```

### Best Practices

**Clear descriptions:**
```bash
# Good
homer clockify start "Fixing bug #NDI-123: User login timeout"

# Less helpful
homer clockify start "Work"
```

**Use consistent projects:**
```bash
# Same project name every time
homer clockify start "Task 1" --project "web-api"
homer clockify start "Task 2" --project "web-api"
# Later reports group by project automatically
```

**Tag by context:**
```bash
# Tag by type of work
homer clockify start "Debugging" --tags "debugging"

# Tag by area
homer clockify start "API work" --tags "backend"

# Tag by urgency
homer clockify start "Critical bug" --tags "urgent,production"

# Multiple tags
homer clockify start "Fix prod bug" --tags "production,urgent,debugging"
```

---

## Clockify Reports

### Summary Reports

View a high-level breakdown by project/date/tag:

Basic - grouped by project (default):
```bash
homer clockify summary 2024-01-01 2024-01-31
```

Grouped by date:
```bash
homer clockify summary 2024-01-01 2024-01-31 --group-by DATE
```

Grouped by tag:
```bash
homer clockify summary 2024-01-01 2024-01-31 --group-by TAG
```

Multiple groupings (note: currently supports one primary grouping):
```bash
# Group by multiple dimensions
homer clockify summary 2024-01-01 2024-01-31 --group-by "DATE,PROJECT"
```

### Filtering Reports

Filter by project:
```bash
homer clockify summary 2024-01-01 2024-01-31 --project "web-api"
```

Filter by tag:
```bash
homer clockify summary 2024-01-01 2024-01-31 --tags "production"
```

Both project and tag:
```bash
homer clockify summary 2024-01-01 2024-01-31 \
  --project "web-api" \
  --tags "urgent"
```

### Detailed Reports

See every time entry:
```bash
homer clockify detailed 2024-01-01 2024-01-31
```

Output includes:
- Date
- Description
- Duration
- Start/end times
- Project

With filters:
```bash
homer clockify detailed 2024-01-01 2024-01-31 --project "mobile-app"
```

### Reading the Output

**Summary Report:**
```
Summary Report 2024-01-01 to 2024-01-31
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┓
┃ Name        ┃ Duration┃ Billable ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│ 2024-01-01  │ 8:15:00 │ 8:15:00  │
│ 2024-01-02  │ 7:45:00 │ 7:45:00  │
└─────────────┴─────────┴──────────┘

Total: 16:00:00 Billable: 16:00:00
```

**Detailed Report:**
```
Detailed Report 2024-01-01 to 2024-01-31
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━┓
┃ Date     ┃ Desc   ┃ Project┃ Dur.. ┃Start ┃End   ┃
├──────────┼────────┼────────┼───────┼──────┼──────┤
│ 2024-01-01│Debugging│web-api │01:30:00│09:00│10:30│
│ 2024-01-01│Feature X│web-api │04:00:00│14:00│18:00│
└──────────┴────────┴────────┴───────┴──────┴──────┘

Total Duration: 5:30:00
```

### Report Tips

**Weekly reports:**
```bash
# Monday to Friday of this week
homer clockify summary 2024-01-29 2024-02-02
```

**Monthly reports:**
```bash
# Entire January
homer clockify summary 2024-01-01 2024-01-31
```

**Find time by project:**
```bash
# How much time on web-api?
homer clockify summary 2024-01-01 2024-01-31 --project "web-api"
```

**Billable vs non-billable:**
The report shows both. Use tags to mark billable work.

---

## Jira Issues

### Listing Issues

See all your open issues (assigned to you, not Done):
```bash
homer jira list
```

Output:
```
Your Open Issues
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ Key     ┃ Summary ┃ Status ┃ Pri... ┃ Assig..┃
├─────────┼─────────┼────────┼────────┼────────┤
│ NDI-123 │ Fix...  │ Open   │ High   │ You    │
│ NDI-456 │ Feature │ In Pro │Medium  │ Alice  │
└─────────┴─────────┴────────┴────────┴────────┘

Total: 5 open issues
```

### Viewing Issues

Get full details of an issue:
```bash
homer jira view NDI-123
```

Output:
```
NDI-123 Fix login bug
────────────────────────────────────────────

Status:     In Progress
Priority:   High
Assignee:   John Doe
Project:    NDI

Description:
Users cannot log in with LDAP credentials.
Getting "Invalid token" error.
Stack trace shows issue in auth middleware.
```

### Creating Issues

Simple - just a summary:
```bash
homer jira create "Fix login bug"
```

With type and priority:
```bash
homer jira create "Implement password reset" \
  --type Story \
  --priority Medium
```

Full options:
```bash
homer jira create "Production bug: User data corruption" \
  --project NDI \
  --type Bug \
  --priority Highest \
  --description "Users reporting missing data in their profiles.
                 Looks like a database migration issue.
                 Started after 2024-01-30 deployment."
```

Output when created:
```
✓ Issue created: NDI-789
  Implement password reset
```

### Adding Comments

Simple comment:
```bash
homer jira comment NDI-123 "This is ready for QA"
```

Multi-line comment:
```bash
homer jira comment NDI-123 "Done with implementation.
  - All tests passing
  - Code reviewed
  - Ready for QA"
```

### Mentioning Users

Mention someone in a comment:
```bash
homer jira mention NDI-123 "alice" "Can you review this?"
```

Homer automatically finds the user and adds the mention.

Multiple mentions in one message:
```bash
# Mention first user, then another in the comment text
homer jira mention NDI-123 "alice" "alice please review, then QA"
```

### Workflow Example

**Typical issue lifecycle:**

1. Create issue:
```bash
homer jira create "Implement 2FA"
# Returns: NDI-999
```

2. View the issue:
```bash
homer jira view NDI-999
```

3. Start working (use Clockify):
```bash
homer clockify start "Implementing 2FA" --project "web-api" --tags "feature"
```

4. Add progress comments:
```bash
homer jira comment NDI-999 "Backend authentication complete, moving to frontend"
```

5. When done:
```bash
homer clockify stop
homer jira comment NDI-999 "Ready for code review"
homer jira mention NDI-999 "bob" "Please review implementation"
```

---

## Advanced Tips

### Shell Aliases

Add to your shell config (`~/.bashrc`, `~/.zshrc`, or `~/.fish/config.fish`):

```bash
# Clockify shortcuts
alias hstart='homer clockify start'
alias hstop='homer clockify stop'
alias hnow='homer clockify current'
alias hreport='homer clockify summary'

# Jira shortcuts
alias hjira='homer jira list'
alias hjview='homer jira view'
alias hjcreate='homer jira create'
alias hjcomment='homer jira comment'
alias hjmention='homer jira mention'
```

Then use:
```bash
hstart "Task description"
hnow
hstop
hjira
hjview NDI-123
```

### Scripting

Use Homer in shell scripts:

```bash
#!/bin/bash

# Start timer
ISSUE="NDI-$(date +%d)"
DESCRIPTION="Daily task $ISSUE"

homer clockify start "$DESCRIPTION" --project "daily-work"

# Do work...
sleep 3600  # Simulate 1 hour of work

# Stop and report
homer clockify stop

# Create summary
echo "Work summary for $(date +%Y-%m-%d)"
homer jira view "$ISSUE"
```

### Integration with Git Commits

Start timer before committing, stop after:

```bash
#!/bin/bash

BRANCH=$(git rev-parse --abbrev-ref HEAD)
ISSUE=$(echo $BRANCH | grep -oE '[A-Z]+-[0-9]+')

if [ ! -z "$ISSUE" ]; then
  homer clockify start "Working on $ISSUE" --tags "dev"
  # ... make commits ...
  homer clockify stop
fi
```

### Combining Multiple Operations

Complex workflow in one command:

```bash
# Create issue, then immediately comment
ISSUE=$(homer jira create "Bug report" --priority High | grep -oE '[A-Z]+-[0-9]+')
homer jira comment "$ISSUE" "Auto-created bug report"
```

### Getting Data for External Tools

Export time data:
```bash
# Get summary as structured text
homer clockify summary 2024-01-01 2024-01-31 > weekly_report.txt

# Get detailed data
homer clockify detailed 2024-01-01 2024-01-31 > timesheet.txt
```

### Check Multiple Issues

Loop through issues:

```bash
for issue in NDI-123 NDI-456 NDI-789; do
  echo "=== $issue ==="
  homer jira view $issue
done
```

---

## Troubleshooting Usage

### "No timer running" when I started one

The timer may have auto-stopped or there was an error. Check:
```bash
homer clockify current   # Verify if running
homer jira list          # Verify connection works
```

### "Issue not found" error

Verify the issue key:
```bash
homer jira list  # See all your issues
```

Issue key format is `PROJECT-NUMBER` (e.g., `NDI-123`, not just `123`).

### Dates in wrong format

Always use `YYYY-MM-DD` format for dates:

```bash
# Correct
homer clockify summary 2024-01-15 2024-01-31

# Incorrect (will fail)
homer clockify summary 01/15/2024 01/31/2024
```

### User not found when mentioning

Make sure to use first name or email substring:
```bash
# These might work
homer jira mention NDI-123 "alice" "..."
homer jira mention NDI-123 "alice@company" "..."

# This might not
homer jira mention NDI-123 "a" "..."  # Too ambiguous
```

---

## Getting Help

```bash
# See all commands
homer --help

# Help for Clockify commands
homer clockify --help

# Help for specific command
homer clockify start --help
homer jira create --help

# Update configuration if credentials change
homer init

# Check if you're properly configured
homer clockify current
homer jira list
```

---

**Happy productivity! 🚀**

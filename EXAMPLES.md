# Examples & Recipes

Real-world scenarios and Homer recipes for common workflows.

## Time Tracking Workflows

### Daily Time Tracking

**Morning:**
```bash
# Check your workload
homer jira list

# Review yesterday's hours
homer clockify summary $(date -d yesterday +%Y-%m-%d) $(date -d yesterday +%Y-%m-%d)
```

**Throughout the day:**
```bash
# Start working on an issue
homer clockify start "Implementing feature X" --project "web-api" --tags "feature"

# Later, check time spent
homer clockify current

# Switch tasks
homer clockify stop
homer clockify start "Code review for NDI-123" --tags "review"

# Check another issue while working
homer jira view NDI-456
```

**End of day:**
```bash
# Stop all timers
homer clockify stop

# Log what you worked on
homer jira comment NDI-123 "Ready for QA review"
homer jira comment NDI-456 "In progress - will finish tomorrow"
```

### Weekly Reporting

**Monday morning - see what's assigned:**
```bash
homer jira list
```

**Friday - generate weekly report:**
```bash
# This week's hours by project
MONDAY=$(date -d "monday this week" +%Y-%m-%d)
FRIDAY=$(date -d "friday this week" +%Y-%m-%d)
homer clockify summary $MONDAY $FRIDAY
```

**Or with specific project:**
```bash
homer clockify summary $MONDAY $FRIDAY --project "web-api"
```

### Project Time Breakdown

**How much time on each project this month?**
```bash
MONTH_START=$(date +%Y-%m-01)
MONTH_END=$(date +%Y-%m-31)

# Summary by project
homer clockify summary $MONTH_START $MONTH_END --group-by PROJECT

# Detailed times
homer clockify detailed $MONTH_START $MONTH_END
```

**How much time on specific project?**
```bash
homer clockify summary 2024-01-01 2024-01-31 --project "mobile-app"
```

---

## Issue Management Workflows

### Create and Track a Feature

**1. Create the issue:**
```bash
homer jira create "Implement user authentication" \
  --type Story \
  --priority High \
  --description "Add JWT-based auth to the API
  
Requirements:
- Support email/password login
- Generate JWT tokens
- Add refresh token flow
- Write tests for auth middleware"
```

Assume it creates `NDI-789`.

**2. Start working:**
```bash
homer clockify start "Implementing JWT auth" \
  --project "web-api" \
  --tags "authentication,backend"
```

**3. Make progress and comment:**
```bash
# After finishing the first part
homer clockify stop

# Update the issue
homer jira comment NDI-789 "Authentication routes complete.
Next: Add token refresh flow and tests."

# Continue working on next part
homer clockify start "JWT refresh token implementation" \
  --project "web-api" \
  --tags "authentication,backend"
```

**4. Request review:**
```bash
homer clockify stop

homer jira comment NDI-789 "Implementation complete.
Ready for code review."

# Mention a teammate
homer jira mention NDI-789 "alice" "Ready for review when you have time"
```

### Triage Bugs

**1. Find urgent bugs:**
```bash
homer jira list
```

**2. Review each one:**
```bash
homer jira view NDI-100
homer jira view NDI-101
homer jira view NDI-102
```

**3. Work on critical issues first:**
```bash
# Start with highest priority
homer clockify start "Debugging: Users can't log in" \
  --project "web-api" \
  --tags "bug,production,urgent"

# ... debug and fix ...

homer clockify stop

# Document the fix
homer jira comment NDI-100 "Found the issue in auth middleware.
Fixed in commit abc1234.
Ready for testing."
```

---

## Mention Workflows

### Code Review Request

**You're done with code, want review:**
```bash
homer jira mention NDI-456 "bob" "Implementation done, ready for code review"
```

**Multiple people (mention first, then text mentions others):**
```bash
homer jira mention NDI-456 "bob" "Code ready for review.
Also cc: alice for frontend part"
```

### Stakeholder Updates

**Inform QA about completion:**
```bash
homer jira mention NDI-789 "qa_team" "Feature implemented and tested. Ready for QA."
```

**Ask for approval:**
```bash
homer jira mention NDI-999 "product_owner" "Ready to deploy to production. Need approval?"
```

---

## Advanced Scenarios

### Tracking Interruptions

**Start your main task:**
```bash
homer clockify start "Implementing payment system" \
  --project "web-api" \
  --tags "payment"
```

**Interrupted by urgent issue:**
```bash
homer clockify stop

homer clockify start "Urgent: Fix prod data corruption bug" \
  --project "web-api" \
  --tags "bug,production,urgent"

# ... fix the issue ...

homer clockify stop

# Then resume original work
homer clockify start "Implementing payment system" \
  --project "web-api" \
  --tags "payment"
```

**Later, see the interrupt:**
```bash
homer clockify detailed 2024-01-31 2024-01-31
# Shows both tasks clearly separated
```

### Time by Issue Type

**Create issues with consistent tags:**
```bash
# Features
homer jira create "New endpoint" --type Story --tags "feature"

# Bugs
homer jira create "Login fails" --type Bug --tags "bug"

# Improvements
homer jira create "Optimize DB queries" --type Task --tags "improvement"
```

**Track time by type:**
```bash
# Time on features
homer clockify summary 2024-01-01 2024-01-31 --tags "feature"

# Time on bugs
homer clockify summary 2024-01-01 2024-01-31 --tags "bug"
```

### Context-Based Tagging

**Tag by context:**
```bash
# Urgent production issues
homer clockify start "Fix: Session timeout error" \
  --tags "production,urgent,debugging"

# Feature development
homer clockify start "Add user profiles" \
  --tags "feature,development,ui"

# Code review/QA
homer clockify start "Review PR for NDI-456" \
  --tags "review"

# Meetings/Admin
homer clockify start "Team meeting" \
  --tags "meeting,admin"
```

**Get time by context:**
```bash
# Total time on production issues
homer clockify summary 2024-01-01 2024-01-31 --tags "production"

# Development time
homer clockify summary 2024-01-01 2024-01-31 --tags "development"

# Review/QA time
homer clockify summary 2024-01-01 2024-01-31 --tags "review"
```

### Multi-Day Features

**Day 1 - Start feature:**
```bash
homer jira create "Build real-time notifications" \
  --type Story \
  --priority High
# Creates NDI-888

homer clockify start "Setting up WebSocket infrastructure" \
  --project "mobile-app" \
  --tags "realtime"
homer clockify stop

homer jira comment NDI-888 "Day 1: WebSocket setup complete"
```

**Day 2 - Continue:**
```bash
homer clockify start "Implementing notification handlers" \
  --project "mobile-app" \
  --tags "realtime"
homer clockify stop

homer jira comment NDI-888 "Day 2: Notification handlers implemented"
```

**Day 3 - Finish and review:**
```bash
homer clockify start "Testing and bug fixes" \
  --project "mobile-app" \
  --tags "realtime,testing"
homer clockify stop

homer jira comment NDI-888 "Complete. Tests passing. Ready for review."
homer jira mention NDI-888 "alice" "Real-time notifications ready for review"
```

**See total time spent:**
```bash
homer clockify detailed 2024-01-29 2024-01-31 --project "mobile-app"
# Shows all three days of work
```

---

## Reporting & Analysis

### Weekly Status Report

```bash
#!/bin/bash

WEEK_START=$(date -d "monday this week" +%Y-%m-%d)
WEEK_END=$(date -d "today" +%Y-%m-%d)

echo "=== Weekly Status Report ==="
echo "Period: $WEEK_START to $WEEK_END"
echo ""

echo "=== Time Breakdown by Project ==="
homer clockify summary $WEEK_START $WEEK_END

echo ""
echo "=== Completed Issues ==="
homer jira list

echo ""
echo "=== Detailed Time Log ==="
homer clockify detailed $WEEK_START $WEEK_END
```

Run it:
```bash
chmod +x weekly_report.sh
./weekly_report.sh > report.txt
```

### Time vs Issues Correlation

**See what you spent time on vs what you completed:**

```bash
echo "=== Issues Worked This Week ==="
homer jira list

echo ""
echo "=== Time Spent This Week ==="
WEEK_START=$(date -d "monday this week" +%Y-%m-%d)
WEEK_END=$(date -d "friday this week" +%Y-%m-%d)
homer clockify detailed $WEEK_START $WEEK_END
```

This shows both what you worked on (Jira) and how much time you spent (Clockify).

---

## Shell Script Integration

### Auto-Start Timer for Issue

```bash
#!/bin/bash
# Start timer for an issue

ISSUE=$1
if [ -z "$ISSUE" ]; then
  echo "Usage: start_work NDI-123"
  exit 1
fi

# Get issue details
DETAILS=$(homer jira view $ISSUE 2>&1)
SUMMARY=$(echo "$DETAILS" | grep -oE "^[A-Z0-9]+-[0-9]+ .*" | sed "s/^[A-Z0-9+-]* //")

# Start timer
homer clockify start "Working on $ISSUE: $SUMMARY" \
  --project "web-api" \
  --tags "development"

echo "✓ Timer started for $ISSUE"
echo "  $SUMMARY"
```

Usage:
```bash
chmod +x start_work.sh
./start_work.sh NDI-123
```

### Batch Comment Multiple Issues

```bash
#!/bin/bash
# Add same comment to multiple issues

MESSAGE=$1
shift
ISSUES=$@

if [ -z "$MESSAGE" ]; then
  echo "Usage: comment_all 'Message' ISSUE1 ISSUE2 ..."
  exit 1
fi

for issue in $ISSUES; do
  homer jira comment $issue "$MESSAGE"
  echo "✓ Commented on $issue"
done
```

Usage:
```bash
chmod +x comment_all.sh
./comment_all.sh "Ready for deployment" NDI-100 NDI-101 NDI-102
```

---

## Tips & Tricks

### Use Meaningful Descriptions

**Good:**
```bash
homer clockify start "NDI-123: Fixing user authentication timeout in LDAP"
```

**Less useful:**
```bash
homer clockify start "Work"
```

### Consistent Project Names

Use the same project name every time:
```bash
# Always "web-api", not "web-API" or "web api"
homer clockify start "Task 1" --project "web-api"
homer clockify start "Task 2" --project "web-api"

# Later reports group them together automatically
```

### Tag Strategically

```bash
# By area
--tags "backend,database"

# By urgency
--tags "urgent,production"

# By type
--tags "feature,testing"

# By client/project
--tags "client-a,mobile"

# All together
--tags "client-a,mobile,backend,urgent"
```

### Review Before Reporting

```bash
# Always verify your entries first
homer clockify detailed 2024-01-01 2024-01-31

# Check for issues
# - Gaps in coverage (missing entries)
# - Incorrect projects
# - Inconsistent tags

# Spot any issues and manually adjust if needed
```

---

**More examples? Check the main [README.md](README.md) and [USAGE.md](USAGE.md) documents!**

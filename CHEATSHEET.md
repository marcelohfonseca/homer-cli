# Homer Cheatsheet

> `homer ck` and `homer clockify` are equivalent.

## Setup

```bash
pipx install homer-cli
homer init              # configure credentials (~/.env)
homer --version
```

## Clockify — Timers

```bash
homer ck start "Description"                    # start timer
homer ck start "Description" -p "project"       # with project name or Jira key
homer ck start "Description" -p ""              # open project selector
homer ck start "Description" -P                 # same as -p ""
homer ck start "Description" -t "tag1,tag2"     # with tags
homer ck start "Description" -t ""              # open tag selector
homer ck start "Description" -T                 # same as -t ""
homer ck start "Description" -p "" -T           # both selectors

homer ck current                                # show running timer
homer ck stop                                   # stop all timers
```

## Clockify — Reports

```bash
homer ck summary                                # current week (Mon → today/Sun)
homer ck summary  2026-01-01 2026-01-31         # summary by project
homer ck summary  2026-01-01 2026-01-31 -g DATE # group by date
homer ck summary  2026-01-01 2026-01-31 -g TAG  # group by tag
homer ck summary  2026-01-01 2026-01-31 -p NAME # filter by project
homer ck summary  2026-01-01 2026-01-31 -t NAME # filter by tag

homer ck detailed 2026-01-01 2026-01-31         # detailed entries
homer ck detailed 2026-01-01 2026-01-31 -p NAME # filter by project
```

## Jira

```bash
homer jira list                                       # open issues assigned to you
homer jira view NDI-123                               # issue details

homer jira create "Summary"                           # create issue (defaults)
homer jira create "Summary" -p NDI -t Bug --priority High -d "Details"

homer jira comment NDI-123 "Message"                  # add comment
homer jira mention NDI-123 "username" "Message"       # mention user in comment
```

## Configuration

```bash
homer init          # interactive update (preserves existing values)
cat ~/.env          # view current config
nano ~/.env         # edit manually
```

## Tips

- Dates: always `YYYY-MM-DD`
- `-p "NDI-12345"` fetches Jira summary and creates `[NDI-12345] Summary` as a Clockify project
- `-p ""` or `-P` opens selector (Clockify projects + open Jira issues)
- `-t ""` or `-T` opens tag selector (Clockify tags)
- Tag selector: pick multiple with `1,3,5` or type free-form names
- After any selector, a review panel lets you reopen either selector before starting (`p`/`t`/Enter/`q`)
- `homer ck summary` with no args reports the current week (Monday → today, or Sunday if today is Sat/Sun)

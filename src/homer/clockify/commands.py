"""Clockify CLI commands."""

from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from homer.config import get_settings
from homer.clockify.service import ClockifyService
from homer.exceptions import ClockifyError, ConfigurationError

if TYPE_CHECKING:
    pass

app = typer.Typer(
    name="clockify",
    help="Clockify time tracking integration.",
    no_args_is_help=True,
)
console = Console()


def _get_service() -> ClockifyService:
    """Get a configured ClockifyService.

    Returns:
        Initialized service ready to use.

    Raises:
        typer.Exit: With error message if configuration is missing.
    """
    try:
        settings = get_settings()
    except ConfigurationError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)

    return ClockifyService.from_settings(settings)


def _format_duration(seconds: int) -> str:
    """Format a duration in seconds as HH:MM:SS.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted duration string.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:02d}"


def _validate_date(date_str: str) -> str:
    """Validate and normalize a date string to YYYY-MM-DD format.

    Args:
        date_str: Date string to validate.

    Returns:
        Validated date in YYYY-MM-DD format.

    Raises:
        ValueError: If date format is invalid.
    """
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date: {date_str}. {e}")
    return date_str


def _prompt_project(service: ClockifyService) -> str | None:
    """Interactively prompt the user to select or type a project name.

    Displays a numbered list combining existing Clockify projects and open
    Jira issues. The user may enter a number to select from the list, type
    any free-form text to use as a new project name, or leave blank to skip.

    Args:
        service: Initialized ClockifyService used to fetch projects.

    Returns:
        The chosen project name string, or None if the user skips.
    """
    choices: list[tuple[str, str]] = []  # (label_for_display, value_to_use)

    # --- Clockify projects ---
    try:
        project_names = service.list_projects()
        for name in project_names:
            choices.append((name, name))
    except ClockifyError:
        pass  # non-fatal — just skip the project list

    # --- Open Jira issues ---
    try:
        from homer.jira.service import JiraService
        settings = get_settings()
        jira_service = JiraService.from_settings(settings)
        issues = jira_service.list_my_issues()
        for issue in issues:
            label = f"{issue.key} · {issue.summary}"
            choices.append((label, label))
    except Exception:
        pass  # Jira not configured or unavailable — non-fatal

    if not choices:
        value = typer.prompt(
            "Project name (blank to skip)",
            default="",
            show_default=False,
        ).strip()
        return value or None

    # Build display
    console.print()
    col_width = max(len(label) for label, _ in choices) + 2

    # Separate Clockify projects from Jira issues
    clockify_count = sum(1 for label, _ in choices if " · " not in label)

    console.print("  [bold]Select a project[/bold] [dim](number, or type a new name, or Enter to skip)[/dim]")
    console.print()

    if clockify_count:
        console.print("  [dim]Clockify projects[/dim]")
        for i, (label, _) in enumerate(choices[:clockify_count], start=1):
            console.print(f"  [cyan]{i:>2}[/cyan]  {label}")

    jira_choices = choices[clockify_count:]
    if jira_choices:
        console.print()
        console.print("  [dim]Open Jira issues[/dim]")
        for i, (label, _) in enumerate(jira_choices, start=clockify_count + 1):
            console.print(f"  [cyan]{i:>2}[/cyan]  {label}")

    console.print()
    raw = typer.prompt("> ", default="", show_default=False, prompt_suffix="").strip()

    if not raw:
        return None

    # Numeric selection
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(choices):
            return choices[idx][1]
        console.print(f"[yellow]⚠[/yellow]  Invalid selection '{raw}', using as project name.")

    return raw


@app.command()
def start(
    description: str = typer.Argument(
        help="Timer description"
    ),
    project: str | None = typer.Option(
        None, "--project", "-p", help="Project name (omit to select interactively)"
    ),
    tags: str | None = typer.Option(
        None, "--tags", "-t", help="Comma-separated list of tags"
    ),
) -> None:
    """Start a new timer.

    When --project is omitted, an interactive selector shows your existing
    Clockify projects and open Jira issues to choose from.

    Examples:
        homer clockify start "Fixing login bug"
        homer clockify start "Code review" --project "web-api" --tags "review,urgent"
    """
    try:
        service = _get_service()

        # If no project supplied, offer interactive selection
        resolved_project = project
        if resolved_project is None:
            resolved_project = _prompt_project(service)

        # Parse tags from comma-separated string
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else None

        entry = service.start_timer(
            description=description,
            project_name=resolved_project,
            tag_names=tag_list,
        )

        console.print("[green]▶[/green] Timer started")
        console.print(f"[cyan]ID[/cyan]          {entry.id}")
        console.print(f"[cyan]Description[/cyan]  {entry.description}")
        if entry.projectId:
            console.print(f"[cyan]Project[/cyan]      {entry.projectId}")
        if entry.tagIds:
            console.print(f"[cyan]Tags[/cyan]         {', '.join(entry.tagIds)}")

    except ClockifyError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


@app.command()
def current() -> None:
    """Show the currently running timer."""
    try:
        service = _get_service()
        entry = service.get_current_timer()

        if not entry:
            console.print("[yellow]ℹ[/yellow] No timer running")
            return

        # Compute elapsed time
        if isinstance(entry.timeInterval.start, str):
            start_dt = datetime.fromisoformat(entry.timeInterval.start.replace("Z", "+00:00"))
        else:
            start_dt = entry.timeInterval.start
        elapsed = datetime.now(start_dt.tzinfo) - start_dt
        elapsed_sec = int(elapsed.total_seconds())

        desc = entry.description or "(no description)"
        console.print(f"[green]🚀[/green] Active: [bold]{desc}[/bold] [[bold]{_format_duration(elapsed_sec)}[/bold]]")

    except ClockifyError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


@app.command()
def stop() -> None:
    """Stop all running timers."""
    try:
        service = _get_service()
        stopped = service.stop_all_timers()

        if not stopped:
            console.print("[yellow]ℹ[/yellow] No timers running")
            return

        for entry in stopped:
            # Compute elapsed time
            if isinstance(entry.timeInterval.start, str):
                start_dt = datetime.fromisoformat(entry.timeInterval.start.replace("Z", "+00:00"))
            else:
                start_dt = entry.timeInterval.start

            if isinstance(entry.timeInterval.end, str):
                end_dt = datetime.fromisoformat(entry.timeInterval.end.replace("Z", "+00:00"))
            else:
                end_dt = entry.timeInterval.end

            elapsed = end_dt - start_dt
            elapsed_sec = int(elapsed.total_seconds())

            desc = entry.description or "(no description)"
            console.print(
                f"[red]⏹[/red] Stopped: [bold]{desc}[/bold] [[bold]{_format_duration(elapsed_sec)}[/bold]]"
            )

    except ClockifyError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


@app.command()
def summary(
    date_from: str = typer.Argument(
        help="Start date (YYYY-MM-DD)"
    ),
    date_to: str = typer.Argument(
        help="End date (YYYY-MM-DD)"
    ),
    project: str | None = typer.Option(
        None, "--project", "-p", help="Filter by project name"
    ),
    tags: str | None = typer.Option(
        None, "--tags", "-t", help="Filter by tag name"
    ),
    group_by: str | None = typer.Option(
        "PROJECT", "--group-by", "-g",
        help="Group by: PROJECT, DATE, TAG, or combinations"
    ),
) -> None:
    """Fetch a summary report for a date range.

    Examples:
        homer clockify summary 2024-01-01 2024-01-31
        homer clockify summary 2024-01-01 2024-01-31 --project "web-api"
        homer clockify summary 2024-01-01 2024-01-31 --group-by DATE
    """
    try:
        # Validate dates
        date_from = _validate_date(date_from)
        date_to = _validate_date(date_to)

        service = _get_service()

        # Parse group_by
        group_by_list = [g.strip() for g in group_by.split(",")] if group_by else None

        report = service.summary_report(
            date_from=date_from,
            date_to=date_to,
            project_name=project,
            tag_name=tags,
            group_by=group_by_list,
        )

        # Display summary
        if not report.groupEntries:
            console.print("[yellow]ℹ[/yellow] No time entries found for the specified period.")
            return

        # Create table
        table = Table(title=f"Summary Report {date_from} to {date_to}")
        table.add_column("Name", style="cyan")
        table.add_column("Duration", style="green", justify="right")
        table.add_column("Billable", style="blue", justify="right")

        def add_group_entry(entry, indent_level: int = 0) -> None:
            prefix = "  " * indent_level
            name = f"{prefix}{entry.name}" if indent_level > 0 else entry.name

            # Sum duration and billable from nested entries
            duration = entry.duration if entry.duration else 0
            billable = entry.billableDuration if entry.billableDuration else 0

            duration_str = _format_duration(duration // 1000)  # Clockify returns milliseconds
            billable_str = _format_duration(billable // 1000)

            table.add_row(name, duration_str, billable_str)

            # Add nested entries recursively
            if entry.children:
                for child in entry.children:
                    add_group_entry(child, indent_level + 1)

        for entry in report.groupEntries:
            add_group_entry(entry)

        console.print(table)
        total_duration = sum(e.duration or 0 for e in report.groupEntries) // 1000
        total_billable = sum(e.billableDuration or 0 for e in report.groupEntries) // 1000
        console.print(
            f"\n[bold]Total:[/bold] {_format_duration(total_duration)} "
            f"[bold]Billable:[/bold] {_format_duration(total_billable)}"
        )

    except ValueError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)
    except ClockifyError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


@app.command()
def detailed(
    date_from: str = typer.Argument(
        help="Start date (YYYY-MM-DD)"
    ),
    date_to: str = typer.Argument(
        help="End date (YYYY-MM-DD)"
    ),
    project: str | None = typer.Option(
        None, "--project", "-p", help="Filter by project name"
    ),
    tags: str | None = typer.Option(
        None, "--tags", "-t", help="Filter by tag name"
    ),
) -> None:
    """Fetch a detailed report for a date range.

    Examples:
        homer clockify detailed 2024-01-01 2024-01-31
        homer clockify detailed 2024-01-01 2024-01-31 --project "web-api"
    """
    try:
        # Validate dates
        date_from = _validate_date(date_from)
        date_to = _validate_date(date_to)

        service = _get_service()

        report = service.detailed_report(
            date_from=date_from,
            date_to=date_to,
            project_name=project,
            tag_name=tags,
        )

        # Display detailed entries
        if not report.totals or not report.totals.timeentries:
            console.print("[yellow]ℹ[/yellow] No time entries found for the specified period.")
            return

        # Create table
        table = Table(title=f"Detailed Report {date_from} to {date_to}")
        table.add_column("Date", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Project", style="blue")
        table.add_column("Duration", style="green", justify="right")
        table.add_column("Start", style="yellow")
        table.add_column("End", style="yellow")

        total_duration = 0

        for entry in report.totals.timeentries:
            entry_date = entry.timeInterval.start.split("T")[0] if "T" in entry.timeInterval.start else entry.timeInterval.start
            desc = entry.description or "(no description)"

            # Parse start/end times
            start_time = entry.timeInterval.start.split("T")[1][:5] if "T" in entry.timeInterval.start else ""
            end_time = entry.timeInterval.end.split("T")[1][:5] if "T" in entry.timeInterval.end else ""

            duration = entry.duration if entry.duration else 0
            total_duration += duration
            duration_str = _format_duration(duration // 1000)

            table.add_row(
                entry_date,
                desc[:40],  # Truncate long descriptions
                entry.projectId or "-",
                duration_str,
                start_time,
                end_time,
            )

        console.print(table)
        console.print(f"\n[bold]Total Duration:[/bold] {_format_duration(total_duration // 1000)}")

    except ValueError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)
    except ClockifyError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)

"""Jira CLI commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table, box
from rich.text import Text

from homer.config import get_settings
from homer.jira.service import JiraService
from homer.exceptions import ConfigurationError, JiraError

if TYPE_CHECKING:
    pass

app = typer.Typer(
    name="jira",
    help="Jira issue tracking integration.",
    no_args_is_help=True,
)
console = Console()

# Priority → colour mapping
_PRIORITY_STYLE: dict[str, str] = {
    "Highest": "bold red",
    "High": "red",
    "Medium": "yellow",
    "Low": "cyan",
    "Lowest": "dim cyan",
}

# Status → colour mapping
_STATUS_STYLE: dict[str, str] = {
    "To Do": "dim",
    "In Progress": "bold yellow",
    "In Review": "bold cyan",
    "Done": "green",
    "Blocked": "bold red",
}


def _priority(value: str) -> Text:
    style = _PRIORITY_STYLE.get(value, "white")
    return Text(value, style=style)


def _status(value: str) -> Text:
    style = _STATUS_STYLE.get(value, "white")
    return Text(value, style=style)


def _kv_table(*rows: tuple[str, str]) -> Table:
    t = Table.grid(padding=(0, 2))
    t.add_column(style="dim", min_width=11)
    t.add_column()
    for key, value in rows:
        t.add_row(key, value)
    return t


def _get_service() -> JiraService:
    """Get a configured JiraService."""
    try:
        settings = get_settings()
    except ConfigurationError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)
    return JiraService.from_settings(settings)


@app.command()
def list() -> None:
    """List issues assigned to you (not Done).

    Examples:
        homer jira list
    """
    try:
        service = _get_service()
        issues = service.list_my_issues()

        if not issues:
            console.print("[yellow]ℹ[/yellow]  No open issues assigned to you")
            return

        table = Table(
            title=f"[bold]Your Open Issues[/bold]  [dim]({len(issues)} total)[/dim]",
            box=box.ROUNDED,
            border_style="dim",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Key", style="cyan bold", min_width=10)
        table.add_column("Summary", style="white", min_width=30)
        table.add_column("Status", min_width=12)
        table.add_column("Priority", min_width=8)

        for issue in issues:
            table.add_row(
                issue.key,
                issue.summary[:55],
                _status(issue.status),
                _priority(issue.priority),
            )

        console.print()
        console.print(table)
        console.print()

    except JiraError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


@app.command()
def view(key: str = typer.Argument(help="Issue key (e.g., NDI-123)")) -> None:
    """Display details of an issue.

    Examples:
        homer jira view NDI-123
    """
    try:
        service = _get_service()
        issue = service.view_issue(key)

        # Header line: KEY · Summary
        header = Text()
        header.append(f"{issue.key}", style="bold cyan")
        header.append("  ")
        header.append(issue.summary, style="bold white")

        kv_rows: list[tuple[str, str]] = [
            ("Status",   f"[{_STATUS_STYLE.get(issue.status, 'white')}]{issue.status}[/]"),
            ("Priority", f"[{_PRIORITY_STYLE.get(issue.priority, 'white')}]{issue.priority}[/]"),
            ("Project",  issue.project_key),
        ]
        if issue.assignee:
            kv_rows.append(("Assignee", issue.assignee.displayName))

        content = Table.grid(padding=(0, 0))
        content.add_row(header)
        content.add_row("")
        content.add_row(_kv_table(*kv_rows))

        if issue.description:
            content.add_row("")
            content.add_row(Text("Description", style="dim"))
            content.add_row(Text(issue.description[:500], style="white"))

        console.print()
        console.print(
            Panel(
                content,
                border_style="cyan",
                expand=False,
                padding=(1, 2),
            )
        )
        console.print()

    except JiraError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


@app.command()
def create(
    summary: str = typer.Argument(help="Issue summary"),
    project: str | None = typer.Option("NDI", "--project", "-p", help="Project key"),
    issue_type: str | None = typer.Option("Story", "--type", "-t", help="Issue type (Story, Bug, Task, …)"),
    description: str | None = typer.Option(None, "--description", "-d", help="Issue description"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="Assignee account ID"),
    priority: str | None = typer.Option(None, "--priority", help="Priority (Highest, High, Medium, Low, Lowest)"),
) -> None:
    """Create a new issue.

    Examples:
        homer jira create "Fix login bug"
        homer jira create "Update docs" --type Task --priority High
    """
    try:
        service = _get_service()
        issue = service.create_issue(
            summary=summary,
            project=project or "NDI",
            issue_type=issue_type or "Story",
            description=description,
            assignee=assignee,
            priority=priority,
        )

        rows: list[tuple[str, str]] = [
            ("Key",     f"[bold cyan]{issue.key}[/bold cyan]"),
            ("Type",    issue_type or "Story"),
            ("Project", project or "NDI"),
        ]
        if priority:
            rows.append(("Priority", f"[{_PRIORITY_STYLE.get(priority, 'white')}]{priority}[/]"))

        content = Table.grid(padding=(0, 0))
        content.add_row(Text(issue.summary, style="bold white"))
        content.add_row("")
        content.add_row(_kv_table(*rows))

        console.print(
            Panel(
                content,
                title="[bold green]✓  Issue Created[/bold green]",
                border_style="green",
                expand=False,
                padding=(1, 2),
            )
        )

    except JiraError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


@app.command()
def comment(
    issue_key: str = typer.Argument(help="Issue key (e.g., NDI-123)"),
    message: str = typer.Argument(help="Comment text"),
) -> None:
    """Add a comment to an issue.

    Examples:
        homer jira comment NDI-123 "This is done"
    """
    try:
        service = _get_service()
        result = service.comment_issue(issue_key, message)

        content = _kv_table(
            ("Issue",  f"[bold cyan]{issue_key}[/bold cyan]"),
            ("Author", result.author.displayName),
            ("",       f"[dim]{message}[/dim]"),
        )

        console.print(
            Panel(
                content,
                title="[bold green]✓  Comment Added[/bold green]",
                border_style="green",
                expand=False,
                padding=(1, 2),
            )
        )

    except JiraError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


@app.command()
def mention(
    issue_key: str = typer.Argument(help="Issue key (e.g., NDI-123)"),
    username: str = typer.Argument(help="Username to mention"),
    message: str = typer.Argument(help="Comment text"),
) -> None:
    """Mention a user in a comment on an issue.

    Examples:
        homer jira mention NDI-123 "John" "Can you review this?"
    """
    try:
        service = _get_service()
        result = service.mention_user(issue_key, username, message)

        content = _kv_table(
            ("Issue",     f"[bold cyan]{issue_key}[/bold cyan]"),
            ("Mentioned", f"[cyan]@{username}[/cyan]"),
            ("Author",    result.author.displayName),
            ("",          f"[dim]{message}[/dim]"),
        )

        console.print(
            Panel(
                content,
                title="[bold green]✓  Mention Sent[/bold green]",
                border_style="green",
                expand=False,
                padding=(1, 2),
            )
        )

    except JiraError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


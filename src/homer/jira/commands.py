"""Jira CLI commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.table import Table

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


def _get_service() -> JiraService:
    """Get a configured JiraService.

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
            console.print("[yellow]ℹ[/yellow] No open issues assigned to you")
            return

        # Create table
        table = Table(title="Your Open Issues")
        table.add_column("Key", style="cyan")
        table.add_column("Summary", style="white")
        table.add_column("Status", style="blue")
        table.add_column("Priority", style="yellow")
        table.add_column("Assignee", style="green")

        for issue in issues:
            assignee_name = issue.assignee.displayName if issue.assignee else "-"
            table.add_row(
                issue.key,
                issue.summary[:50],  # Truncate long summaries
                issue.status,
                issue.priority,
                assignee_name,
            )

        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(issues)} open issues")

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

        console.print(f"\n[bold cyan]{issue.key}[/bold cyan] {issue.summary}")
        console.print("[dim]" + "─" * 80 + "[/dim]")

        # Display fields
        console.print(f"\n[bold]Status:[/bold] {issue.status}")
        console.print(f"[bold]Priority:[/bold] {issue.priority}")

        if issue.assignee:
            console.print(f"[bold]Assignee:[/bold] {issue.assignee.displayName}")

        console.print(f"[bold]Project:[/bold] {issue.project_key}")

        if issue.description:
            console.print(f"\n[bold]Description:[/bold]")
            console.print(issue.description)

    except JiraError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)


@app.command()
def create(
    summary: str = typer.Argument(help="Issue summary"),
    project: str | None = typer.Option(
        "NDI", "--project", "-p", help="Project key"
    ),
    issue_type: str | None = typer.Option(
        "Story", "--type", "-t", help="Issue type (Story, Bug, Task, etc.)"
    ),
    description: str | None = typer.Option(
        None, "--description", "-d", help="Issue description"
    ),
    assignee: str | None = typer.Option(
        None, "--assignee", "-a", help="Assignee account ID (or will default to you)"
    ),
    priority: str | None = typer.Option(
        None, "--priority", help="Priority (Highest, High, Medium, Low, Lowest)"
    ),
) -> None:
    """Create a new issue.

    Examples:
        homer jira create "Fix login bug"
        homer jira create "Update docs" --type Task --priority High
        homer jira create "Write tests" --project WEB --description "Add tests for API"
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

        console.print(f"[green]✓[/green] Issue created: [bold cyan]{issue.key}[/bold cyan]")
        console.print(f"[dim]{issue.summary}[/dim]")

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
        homer jira comment WEB-45 "Ready for QA"
    """
    try:
        service = _get_service()
        result = service.comment_issue(issue_key, message)

        console.print(f"[green]✓[/green] Comment added to [bold cyan]{issue_key}[/bold cyan]")
        console.print(f"[dim]{result.author.displayName}: {message}[/dim]")

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
        homer jira mention WEB-45 "alice" "Please approve"
    """
    try:
        service = _get_service()
        result = service.mention_user(issue_key, username, message)

        console.print(f"[green]✓[/green] Comment added to [bold cyan]{issue_key}[/bold cyan]")
        console.print(f"[dim]{result.author.displayName}: {message}[/dim]")

    except JiraError as exc:
        console.print(f"[red]✗[/red] {exc}", highlight=False)
        raise typer.Exit(code=1)

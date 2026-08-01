"""Homer CLI entry point.

Defines the root Typer application and top-level commands.
Integration-specific commands (jira, clockify) are registered as
sub-applications in their own ``commands.py`` modules.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from homer import __version__

_ASCII_ART = """
██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗ 
██║  ██║██╔═══██╗████╗ ████║██╔════╝██╔══██╗
███████║██║   ██║██╔████╔██║█████╗  ██████╔╝
██╔══██║██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗
██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║
╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝
"""

app = typer.Typer(
    name="homer",
    help="Homer — personal productivity CLI for developers.",
    no_args_is_help=False,
)
console = Console()

# Register sub-apps
from homer.clockify.commands import app as clockify_app
from homer.jira.commands import app as jira_app

app.add_typer(clockify_app, name="clockify")
app.add_typer(clockify_app, name="ck", hidden=False)
app.add_typer(jira_app, name="jira")


def _print_banner() -> None:
    """Print the Homer ASCII art banner."""
    art = Text(_ASCII_ART, style="bold yellow", no_wrap=True)
    console.print(art)
    console.print(
        f"  [dim]v{__version__} — personal productivity CLI for developers[/dim]\n"
    )


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"homer [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def _callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Homer — personal productivity CLI for developers."""
    if ctx.invoked_subcommand is None:
        _print_banner()
        console.print(ctx.get_help())

# Fields required by Settings, in the order they are prompted during init.
# Each entry is (env_key, human_label, is_secret).
_REQUIRED_FIELDS: list[tuple[str, str, bool]] = [
    ("JIRA_BASE_URL", "Jira base URL (e.g. https://company.atlassian.net)", False),
    ("JIRA_USER", "Jira user email", False),
    ("JIRA_API_TOKEN", "Jira API token", True),
    ("CLOCKIFY_API_KEY", "Clockify API key", True),
    ("CLOCKIFY_WORKSPACE", "Clockify workspace ID", False),
    ("CLOCKIFY_USER", "Clockify user ID", False),
]


def _get_env_path() -> Path:
    """Return the path to the user-level .env file."""
    return Path.home() / ".env"


def _load_env_file(path: Path) -> dict[str, str]:
    """Parse a .env file into a key/value dict.

    Args:
        path: Path to the .env file.

    Returns:
        Mapping of variable names to values. Empty if the file does not exist.
    """
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            key, _, value = stripped.partition("=")
            result[key.strip()] = value.strip()
    return result


def _write_env_file(path: Path, values: dict[str, str]) -> None:
    """Write key/value pairs to a .env file.

    Creates parent directories if they do not exist.
    Overwrites the file completely with the provided values.

    Args:
        path: Destination file path.
        values: Key/value pairs to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}={value}" for key, value in values.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@app.command()
def init() -> None:
    """Configure Homer credentials and settings.

    Creates or updates $HOME/.env with the API credentials required by
    Homer. Existing values are preserved when the prompt is left empty.
    Run this command again at any time to update individual settings.
    """
    env_path = _get_env_path()
    existing = _load_env_file(env_path)

    _print_banner()
    console.print(
        Panel(
            "Initial Setup",
            subtitle=f"[dim]{env_path}[/dim]",
            expand=False,
        )
    )
    console.print("Press [bold]Enter[/bold] to keep an existing value.\n")

    updated: dict[str, str] = dict(existing)

    for key, label, secret in _REQUIRED_FIELDS:
        current = existing.get(key, "")

        if current:
            suffix = " [[***] Enter to keep]" if secret else f" [[{current}] Enter to keep]"
            prompt_text = f"{label}{suffix}"
        else:
            prompt_text = label

        value: str = typer.prompt(
            prompt_text,
            default="",
            show_default=False,
            hide_input=secret,
        )

        if value:
            updated[key] = value
        elif not current:
            console.print(f"\n[red]✗[/red] [bold]{key}[/bold] is required.")
            raise typer.Exit(code=1)
        # else: value is empty but current exists — keep existing (already in updated)

    _write_env_file(env_path, updated)
    console.print(f"\n[green]✓[/green] Configuration saved to [bold]{env_path}[/bold]")

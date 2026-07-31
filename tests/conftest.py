"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from homer.cli import app


@pytest.fixture()
def runner() -> CliRunner:
    """Typer CLI test runner."""
    return CliRunner()


@pytest.fixture()
def tmp_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated .env file in a temp directory.

    Monkeypatches ``homer.cli._get_env_path`` so the init command reads
    from and writes to this path instead of the real ``~/.env``.
    """
    env_file = tmp_path / ".env"
    monkeypatch.setattr("homer.cli._get_env_path", lambda: env_file)
    return env_file

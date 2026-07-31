"""Tests for the homer CLI — init command and application entry point."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from homer.cli import _load_env_file, _write_env_file, app

# Stdin inputs for the six prompts, in order:
# JIRA_BASE_URL, JIRA_USER, JIRA_API_TOKEN, CLOCKIFY_API_KEY,
# CLOCKIFY_WORKSPACE, CLOCKIFY_USER
_FULL_INPUT = (
    "https://test.atlassian.net\n"
    "user@test.com\n"
    "jira-token\n"
    "clockify-key\n"
    "ws-abc123\n"
    "usr-xyz789\n"
)


class TestLoadEnvFile:
    """_load_env_file parses .env content correctly."""

    def test_returns_empty_dict_for_missing_file(self, tmp_path: Path) -> None:
        assert _load_env_file(tmp_path / "nonexistent.env") == {}

    def test_parses_key_value_pairs(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("FOO=bar\nBAZ=qux\n", encoding="utf-8")

        result = _load_env_file(env_file)

        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_ignores_blank_lines_and_comments(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "# comment\n\nFOO=bar\n  \nBAZ=qux\n", encoding="utf-8"
        )

        result = _load_env_file(env_file)

        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_value_may_contain_equals_sign(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("TOKEN=abc=def=ghi\n", encoding="utf-8")

        result = _load_env_file(env_file)

        assert result["TOKEN"] == "abc=def=ghi"


class TestWriteEnvFile:
    """_write_env_file persists key/value pairs to disk."""

    def test_writes_all_pairs(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        _write_env_file(env_file, {"FOO": "bar", "BAZ": "qux"})

        content = env_file.read_text(encoding="utf-8")
        assert "FOO=bar" in content
        assert "BAZ=qux" in content

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        env_file = tmp_path / "nested" / "dir" / ".env"
        _write_env_file(env_file, {"KEY": "value"})

        assert env_file.exists()

    def test_file_ends_with_newline(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        _write_env_file(env_file, {"KEY": "value"})

        assert env_file.read_text(encoding="utf-8").endswith("\n")


class TestInitCommand:
    """homer init creates and updates the .env file."""

    def test_creates_env_file_with_all_values(
        self, runner: CliRunner, tmp_env_file: Path
    ) -> None:
        result = runner.invoke(app, ["init"], input=_FULL_INPUT)

        assert result.exit_code == 0
        env = _load_env_file(tmp_env_file)
        assert env["JIRA_BASE_URL"] == "https://test.atlassian.net"
        assert env["JIRA_USER"] == "user@test.com"
        assert env["JIRA_API_TOKEN"] == "jira-token"
        assert env["CLOCKIFY_API_KEY"] == "clockify-key"
        assert env["CLOCKIFY_WORKSPACE"] == "ws-abc123"
        assert env["CLOCKIFY_USER"] == "usr-xyz789"

    def test_preserves_existing_values_when_input_is_empty(
        self, runner: CliRunner, tmp_env_file: Path
    ) -> None:
        # Pre-populate some values
        tmp_env_file.write_text(
            "JIRA_BASE_URL=https://existing.atlassian.net\n"
            "JIRA_USER=existing@test.com\n",
            encoding="utf-8",
        )

        # Press Enter for JIRA_BASE_URL and JIRA_USER (keep existing),
        # provide new values for the rest.
        result = runner.invoke(
            app,
            ["init"],
            input="\n\njira-token\nclocky-key\nws-abc123\nusr-xyz789\n",
        )

        assert result.exit_code == 0
        env = _load_env_file(tmp_env_file)
        assert env["JIRA_BASE_URL"] == "https://existing.atlassian.net"
        assert env["JIRA_USER"] == "existing@test.com"
        assert env["JIRA_API_TOKEN"] == "jira-token"

    def test_overwrites_existing_value_when_new_value_provided(
        self, runner: CliRunner, tmp_env_file: Path
    ) -> None:
        tmp_env_file.write_text(
            "JIRA_BASE_URL=https://old.atlassian.net\n", encoding="utf-8"
        )

        result = runner.invoke(app, ["init"], input=_FULL_INPUT)

        assert result.exit_code == 0
        env = _load_env_file(tmp_env_file)
        assert env["JIRA_BASE_URL"] == "https://test.atlassian.net"

    def test_exits_with_error_when_required_field_left_empty(
        self, runner: CliRunner, tmp_env_file: Path
    ) -> None:
        # All fields empty → should fail on the first required prompt
        result = runner.invoke(
            app,
            ["init"],
            input="\n\n\n\n\n\n",
        )

        assert result.exit_code == 1

    def test_env_file_not_created_on_failure(
        self, runner: CliRunner, tmp_env_file: Path
    ) -> None:
        # No pre-existing file, all inputs empty → failure before write
        runner.invoke(app, ["init"], input="\n\n\n\n\n\n")

        assert not tmp_env_file.exists()

    def test_preserves_unrelated_env_vars(
        self, runner: CliRunner, tmp_env_file: Path
    ) -> None:
        tmp_env_file.write_text(
            "SOME_OTHER_VAR=keep-me\n", encoding="utf-8"
        )

        result = runner.invoke(app, ["init"], input=_FULL_INPUT)

        assert result.exit_code == 0
        env = _load_env_file(tmp_env_file)
        assert env["SOME_OTHER_VAR"] == "keep-me"

    def test_success_output_mentions_env_path(
        self, runner: CliRunner, tmp_env_file: Path
    ) -> None:
        result = runner.invoke(app, ["init"], input=_FULL_INPUT)

        assert result.exit_code == 0
        assert str(tmp_env_file) in result.output

    def test_can_run_twice_idempotently(
        self, runner: CliRunner, tmp_env_file: Path
    ) -> None:
        runner.invoke(app, ["init"], input=_FULL_INPUT)
        result = runner.invoke(app, ["init"], input=_FULL_INPUT)

        assert result.exit_code == 0
        env = _load_env_file(tmp_env_file)
        assert env["JIRA_BASE_URL"] == "https://test.atlassian.net"


class TestAppEntryPoint:
    """The homer app itself is correctly configured."""

    def test_help_exits_cleanly(self, runner: CliRunner) -> None:
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "homer" in result.output.lower()

    def test_init_subcommand_appears_in_help(self, runner: CliRunner) -> None:
        result = runner.invoke(app, ["--help"])

        assert "init" in result.output

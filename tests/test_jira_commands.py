"""Integration tests for Jira CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from homer.jira.commands import app
from homer.jira.models import Issue, User, Comment


@pytest.fixture()
def runner() -> CliRunner:
    """CLI test runner."""
    return CliRunner()


class TestListCommand:
    """homer jira list command."""

    def test_displays_open_issues(self, runner: CliRunner) -> None:
        mock_issue = Issue(
            key="NDI-123",
            id="id-123",
            fields={
                "summary": "Fix login bug",
                "status": {"name": "Open"},
                "priority": {"name": "High"},
                "assignee": {
                    "accountId": "user-1",
                    "displayName": "John Doe",
                    "emailAddress": "john@example.com",
                    "active": True,
                },
            },
        )

        with patch("homer.jira.commands.get_settings"):
            with patch(
                "homer.jira.commands.JiraService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.list_my_issues.return_value = [mock_issue]
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "NDI-123" in result.output
        assert "Fix login bug" in result.output

    def test_shows_message_when_no_issues(self, runner: CliRunner) -> None:
        with patch("homer.jira.commands.get_settings"):
            with patch(
                "homer.jira.commands.JiraService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.list_my_issues.return_value = []
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No open issues" in result.output


class TestViewCommand:
    """homer jira view command."""

    def test_displays_issue_details(self, runner: CliRunner) -> None:
        mock_issue = Issue(
            key="NDI-123",
            id="id-123",
            fields={
                "summary": "Fix login bug",
                "description": "Users can't log in with LDAP",
                "status": {"name": "In Progress"},
                "priority": {"name": "High"},
                "assignee": {
                    "accountId": "user-1",
                    "displayName": "John Doe",
                    "emailAddress": "john@example.com",
                    "active": True,
                },
                "project": {"key": "NDI"},
            },
        )

        with patch("homer.jira.commands.get_settings"):
            with patch(
                "homer.jira.commands.JiraService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.view_issue.return_value = mock_issue
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["view", "NDI-123"])

        assert result.exit_code == 0
        assert "NDI-123" in result.output
        assert "Fix login bug" in result.output
        assert "In Progress" in result.output
        assert "High" in result.output


class TestCreateCommand:
    """homer jira create command."""

    def test_creates_issue_with_summary_only(self, runner: CliRunner) -> None:
        mock_issue = Issue(
            key="NDI-456",
            id="id-456",
            fields={"summary": "New feature"},
        )

        with patch("homer.jira.commands.get_settings"):
            with patch(
                "homer.jira.commands.JiraService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.create_issue.return_value = mock_issue
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["create", "New feature"])

        assert result.exit_code == 0
        assert "NDI-456" in result.output
        assert "Issue Created" in result.output

    def test_creates_issue_with_options(self, runner: CliRunner) -> None:
        mock_issue = Issue(
            key="NDI-789",
            id="id-789",
            fields={"summary": "Fix bug"},
        )

        with patch("homer.jira.commands.get_settings"):
            with patch(
                "homer.jira.commands.JiraService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.create_issue.return_value = mock_issue
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app,
                    [
                        "create",
                        "Fix bug",
                        "--project", "WEB",
                        "--type", "Bug",
                        "--priority", "High",
                    ],
                )

        assert result.exit_code == 0
        call_args = mock_service.create_issue.call_args
        assert call_args.kwargs["project"] == "WEB"
        assert call_args.kwargs["issue_type"] == "Bug"
        assert call_args.kwargs["priority"] == "High"


class TestCommentCommand:
    """homer jira comment command."""

    def test_adds_comment_to_issue(self, runner: CliRunner) -> None:
        mock_comment = Comment(
            id="comment-123",
            author=User(
                accountId="user-1",
                displayName="John",
                emailAddress="john@example.com",
            ),
            body="This is done",
            created="2026-07-31T08:00:00Z",
            updated="2026-07-31T08:00:00Z",
        )

        with patch("homer.jira.commands.get_settings"):
            with patch(
                "homer.jira.commands.JiraService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.comment_issue.return_value = mock_comment
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app,
                    ["comment", "NDI-123", "This is done"],
                )

        assert result.exit_code == 0
        assert "Comment Added" in result.output
        assert "NDI-123" in result.output


class TestMentionCommand:
    """homer jira mention command."""

    def test_mentions_user_in_comment(self, runner: CliRunner) -> None:
        mock_comment = Comment(
            id="comment-456",
            author=User(
                accountId="user-1",
                displayName="John",
                emailAddress="john@example.com",
            ),
            body="[~user-id] Can you review?",
            created="2026-07-31T08:00:00Z",
            updated="2026-07-31T08:00:00Z",
        )

        with patch("homer.jira.commands.get_settings"):
            with patch(
                "homer.jira.commands.JiraService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.mention_user.return_value = mock_comment
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app,
                    ["mention", "NDI-123", "john", "Can you review?"],
                )

        assert result.exit_code == 0
        assert "Mention Sent" in result.output

"""Tests for Jira service (business logic)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from homer.jira.client import JiraClient
from homer.jira.service import JiraService
from homer.jira.models import Issue, User, Comment
from homer.config import Settings
from homer.exceptions import JiraError


@pytest.fixture()
def mock_client() -> MagicMock:
    """Mock JiraClient."""
    return MagicMock(spec=JiraClient)


@pytest.fixture()
def service(mock_client: MagicMock) -> JiraService:
    """Service with mocked client."""
    return JiraService(mock_client)


@pytest.fixture()
def settings() -> Settings:
    """Test settings."""
    return Settings(
        jira_base_url="https://test.atlassian.net",
        jira_user="test@example.com",
        jira_api_token="test-token",
        clockify_api_key="test-key",
        clockify_workspace="ws-abc",
        clockify_user="usr-xyz",
        _env_file=None,
    )


class TestFromSettings:
    """Service factory from settings."""

    def test_creates_service_from_settings(self, settings: Settings) -> None:
        with patch.object(JiraClient, "__init__", return_value=None):
            service = JiraService.from_settings(settings)

        assert isinstance(service, JiraService)
        assert service.client is not None


class TestListMyIssues:
    """Service lists issues assigned to current user."""

    def test_returns_open_issues(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        issue1 = Issue(
            key="NDI-1",
            id="id-1",
            fields={"summary": "Issue 1"},
        )
        issue2 = Issue(
            key="NDI-2",
            id="id-2",
            fields={"summary": "Issue 2"},
        )

        mock_client.search.return_value = MagicMock(issues=[issue1, issue2])

        result = service.list_my_issues()

        assert len(result) == 2
        assert result[0].key == "NDI-1"

    def test_uses_correct_jql(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        mock_client.search.return_value = MagicMock(issues=[])

        service.list_my_issues()

        # Verify the JQL query
        call_args = mock_client.search.call_args
        jql = call_args[0][0]
        assert "currentUser()" in jql
        assert "Done" in jql


class TestViewIssue:
    """Service fetches a single issue."""

    def test_returns_issue_details(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        issue = Issue(
            key="NDI-123",
            id="id-123",
            fields={"summary": "Test", "status": {"name": "Open"}},
        )
        mock_client.get_issue.return_value = issue

        result = service.view_issue("NDI-123")

        assert result.key == "NDI-123"
        mock_client.get_issue.assert_called_once_with("NDI-123")

    def test_propagates_errors(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        mock_client.get_issue.side_effect = JiraError("Not found")

        with pytest.raises(JiraError):
            service.view_issue("INVALID-999")


class TestCreateIssue:
    """Service creates a new issue."""

    def test_creates_with_defaults(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        current_user = User(
            accountId="user-123",
            emailAddress="test@example.com",
            displayName="Test User",
        )
        mock_client.get_current_user.return_value = current_user

        issue = Issue(
            key="NDI-789",
            id="id-789",
            fields={"summary": "New issue"},
        )
        mock_client.create_issue.return_value = issue

        result = service.create_issue("New issue")

        assert result.key == "NDI-789"
        # Verify defaults were used
        call_args = mock_client.create_issue.call_args
        assert call_args[1]["project"] == "NDI"
        assert call_args[1]["issuetype"] == "Story"

    def test_uses_provided_assignee(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        issue = Issue(
            key="NDI-789",
            id="id-789",
            fields={"summary": "New issue"},
        )
        mock_client.create_issue.return_value = issue

        service.create_issue("New issue", assignee="specific-user-id")

        # Verify assignee was passed
        call_args = mock_client.create_issue.call_args
        assert call_args[1]["assignee"] == "specific-user-id"
        # Should NOT have called get_current_user
        mock_client.get_current_user.assert_not_called()

    def test_defaults_to_current_user_when_no_assignee(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        current_user = User(
            accountId="current-user-id",
            emailAddress="current@example.com",
            displayName="Current",
        )
        mock_client.get_current_user.return_value = current_user

        issue = Issue(
            key="NDI-789",
            id="id-789",
            fields={"summary": "New issue"},
        )
        mock_client.create_issue.return_value = issue

        service.create_issue("New issue")

        # Verify current user was used as assignee
        call_args = mock_client.create_issue.call_args
        assert call_args[1]["assignee"] == "current-user-id"


class TestCommentIssue:
    """Service adds a comment to an issue."""

    def test_adds_comment(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        comment = Comment(
            id="comment-123",
            author=User(
                accountId="user-1",
                displayName="John",
                emailAddress="john@example.com",
            ),
            body="Test message",
            created="2026-07-31T08:00:00Z",
            updated="2026-07-31T08:00:00Z",
        )
        mock_client.add_comment.return_value = comment

        result = service.comment_issue("NDI-123", "Test message")

        assert result.body == "Test message"
        mock_client.add_comment.assert_called_once_with("NDI-123", "Test message")


class TestMentionUser:
    """Service mentions a user in a comment."""

    def test_finds_user_and_mentions(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        user = User(
            accountId="john-id",
            displayName="John Doe",
            emailAddress="john@example.com",
        )
        mock_client.search_users.return_value = [user]

        comment = Comment(
            id="comment-456",
            author=user,
            body="[~john-id] Can you review?",
            created="2026-07-31T08:00:00Z",
            updated="2026-07-31T08:00:00Z",
        )
        mock_client.add_comment.return_value = comment

        result = service.mention_user("NDI-123", "john", "Can you review?")

        assert "[~john-id]" in result.body

    def test_raises_error_when_user_not_found(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        mock_client.search_users.return_value = []

        with pytest.raises(JiraError, match="not found"):
            service.mention_user("NDI-123", "nonexistent", "Hello")

    def test_takes_first_user_match(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        user1 = User(
            accountId="user-1",
            displayName="John A",
            emailAddress="johna@example.com",
        )
        user2 = User(
            accountId="user-2",
            displayName="John B",
            emailAddress="johnb@example.com",
        )
        mock_client.search_users.return_value = [user1, user2]

        comment = Comment(
            id="comment-789",
            author=user1,
            body="[~user-1] Test",
            created="2026-07-31T08:00:00Z",
            updated="2026-07-31T08:00:00Z",
        )
        mock_client.add_comment.return_value = comment

        service.mention_user("NDI-123", "john", "Test")

        # Verify first user was used
        call_args = mock_client.add_comment.call_args
        message = call_args[0][1]
        assert "[~user-1]" in message


class TestGetCurrentUser:
    """Service fetches and caches current user."""

    def test_returns_current_user(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        user = User(
            accountId="user-123",
            displayName="Current",
            emailAddress="current@example.com",
        )
        mock_client.get_current_user.return_value = user

        result = service.get_current_user()

        assert result.accountId == "user-123"

    def test_caches_current_user(
        self, service: JiraService, mock_client: MagicMock
    ) -> None:
        user = User(
            accountId="user-123",
            displayName="Current",
            emailAddress="current@example.com",
        )
        mock_client.get_current_user.return_value = user

        # Call twice
        service.get_current_user()
        service.get_current_user()

        # Should only call client once (cached)
        mock_client.get_current_user.assert_called_once()

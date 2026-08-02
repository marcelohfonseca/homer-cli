"""Tests for Jira client (with mocked httpx)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from homer.jira.client import JiraClient
from homer.jira.models import Issue, User, Comment, SearchResult
from homer.config import Settings
from homer.exceptions import JiraError


@pytest.fixture()
def settings() -> Settings:
    """Test settings with dummy credentials."""
    return Settings(
        jira_base_url="https://test.atlassian.net",
        jira_user="test@example.com",
        jira_api_token="test-token",
        clockify_api_key="test-key-123",
        clockify_workspace="ws-abc",
        clockify_user="usr-xyz",
        _env_file=None,
    )


@pytest.fixture()
def client(settings: Settings) -> JiraClient:
    """Test client."""
    return JiraClient(settings)


class TestSearch:
    """Client searches issues by JQL."""

    def test_returns_search_results(self, client: JiraClient) -> None:
        mock_response = {
            "issues": [
                {
                    "key": "NDI-1",
                    "id": "id-1",
                    "fields": {"summary": "Issue 1"},
                }
            ],
            "isLast": True,
        }

        with patch("httpx.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            result = client.search("assignee = currentUser()")

        assert len(result.issues) == 1
        assert result.issues[0].key == "NDI-1"

    def test_raises_jira_error_on_http_failure(self, client: JiraClient) -> None:
        with patch("httpx.post") as mock_post:
            mock_post.side_effect = httpx.HTTPError("Connection failed")

            with pytest.raises(JiraError, match="Failed to search issues"):
                client.search("assignee = currentUser()")


class TestGetIssue:
    """Client fetches a single issue."""

    def test_returns_issue(self, client: JiraClient) -> None:
        mock_response = {
            "key": "NDI-123",
            "id": "id-123",
            "fields": {"summary": "Test issue", "status": {"name": "Open"}},
        }

        with patch("httpx.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()

            result = client.get_issue("NDI-123")

        assert result.key == "NDI-123"
        assert result.summary == "Test issue"

    def test_raises_jira_error_on_not_found(self, client: JiraClient) -> None:
        with patch("httpx.get") as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "Not Found",
                request=MagicMock(),
                response=MagicMock(status_code=404),
            )

            with pytest.raises(JiraError):
                client.get_issue("INVALID-999")


class TestCreateIssue:
    """Client creates a new issue."""

    def test_creates_and_fetches_issue(self, client: JiraClient) -> None:
        create_response = {"key": "NDI-456", "id": "id-456"}
        get_response = {
            "key": "NDI-456",
            "id": "id-456",
            "fields": {"summary": "New issue"},
        }

        with patch("httpx.post") as mock_post:
            with patch.object(client, "get_issue") as mock_get_issue:
                mock_post.return_value.json.return_value = create_response
                mock_post.return_value.raise_for_status = MagicMock()
                mock_get_issue.return_value = Issue(**get_response)

                result = client.create_issue(
                    "New issue",
                    "NDI",
                    "Story",
                )

        assert result.key == "NDI-456"

    def test_passes_optional_fields(self, client: JiraClient) -> None:
        create_response = {"key": "NDI-789", "id": "id-789"}

        with patch("httpx.post") as mock_post:
            with patch.object(client, "get_issue") as mock_get_issue:
                mock_post.return_value.json.return_value = create_response
                mock_post.return_value.raise_for_status = MagicMock()
                mock_get_issue.return_value = MagicMock()

                client.create_issue(
                    "Test",
                    "NDI",
                    "Bug",
                    description="Desc",
                    assignee="user-1",
                    priority="High",
                )

                # Verify the request body
                call_args = mock_post.call_args
                body = call_args[1]["json"]
                assert body["fields"]["description"] == "Desc"
                assert body["fields"]["assignee"]["accountId"] == "user-1"
                assert body["fields"]["priority"]["name"] == "High"


class TestAddComment:
    """Client adds a comment to an issue."""

    def test_adds_comment(self, client: JiraClient) -> None:
        mock_response = {
            "id": "comment-123",
            "author": {
                "accountId": "user-1",
                "displayName": "John",
                "emailAddress": "john@example.com",
                "active": True,
            },
            "body": "Test comment",
            "created": "2026-07-31T08:00:00Z",
            "updated": "2026-07-31T08:00:00Z",
        }

        with patch("httpx.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            result = client.add_comment("NDI-123", "Test comment")

        assert result.id == "comment-123"
        assert result.body == "Test comment"


class TestSearchUsers:
    """Client searches for users."""

    def test_returns_list_of_users(self, client: JiraClient) -> None:
        mock_response = [
            {
                "accountId": "user-1",
                "emailAddress": "john@example.com",
                "displayName": "John Doe",
                "active": True,
            }
        ]

        with patch("httpx.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()

            result = client.search_users("john")

        assert len(result) == 1
        assert result[0].displayName == "John Doe"

    def test_returns_empty_when_no_users_found(self, client: JiraClient) -> None:
        with patch("httpx.get") as mock_get:
            mock_get.return_value.json.return_value = []
            mock_get.return_value.raise_for_status = MagicMock()

            result = client.search_users("nonexistent")

        assert result == []


class TestGetCurrentUser:
    """Client fetches the authenticated user."""

    def test_returns_current_user(self, client: JiraClient) -> None:
        mock_response = {
            "accountId": "user-123",
            "emailAddress": "current@example.com",
            "displayName": "Current User",
            "active": True,
        }

        with patch("httpx.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()

            result = client.get_current_user()

        assert result.accountId == "user-123"
        assert result.displayName == "Current User"

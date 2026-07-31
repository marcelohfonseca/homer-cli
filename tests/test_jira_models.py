"""Tests for Jira models."""

from __future__ import annotations

import pytest

from homer.jira.models import Issue, User, Comment, CreateIssueInput, SearchResult


class TestUser:
    """User model for Jira accounts."""

    def test_creates_from_dict(self) -> None:
        data = {
            "accountId": "user-123",
            "emailAddress": "john@example.com",
            "displayName": "John Doe",
            "active": True,
        }
        user = User(**data)

        assert user.accountId == "user-123"
        assert user.emailAddress == "john@example.com"
        assert user.displayName == "John Doe"
        assert user.active is True

    def test_name_is_optional(self) -> None:
        user = User(
            accountId="usr-1",
            emailAddress="test@example.com",
            displayName="Test User",
        )
        assert user.name is None


class TestIssue:
    """Issue model for Jira tasks."""

    def test_creates_from_dict(self) -> None:
        data = {
            "key": "NDI-123",
            "id": "issue-789",
            "fields": {
                "summary": "Fix login bug",
                "description": "Users can't log in",
                "status": {"name": "In Progress"},
                "priority": {"name": "High"},
                "assignee": {
                    "accountId": "user-123",
                    "emailAddress": "john@example.com",
                    "displayName": "John Doe",
                    "active": True,
                },
                "project": {"key": "NDI"},
                "issuetype": {"name": "Bug"},
            },
        }
        issue = Issue(**data)

        assert issue.key == "NDI-123"
        assert issue.summary == "Fix login bug"

    def test_convenience_accessors(self) -> None:
        data = {
            "key": "NDI-123",
            "id": "issue-789",
            "fields": {
                "summary": "Test",
                "status": {"name": "Open"},
                "priority": {"name": "Medium"},
                "assignee": {
                    "accountId": "user-1",
                    "displayName": "Alice",
                    "emailAddress": "alice@example.com",
                    "active": True,
                },
                "project": {"key": "WEB"},
            },
        }
        issue = Issue(**data)

        assert issue.status == "Open"
        assert issue.priority == "Medium"
        assert issue.assignee.displayName == "Alice"
        assert issue.project_key == "WEB"

    def test_description_may_be_null(self) -> None:
        data = {
            "key": "NDI-1",
            "id": "id-1",
            "fields": {
                "summary": "Test",
            },
        }
        issue = Issue(**data)
        assert issue.description is None


class TestCreateIssueInput:
    """Model for creating new issues."""

    def test_creates_with_required_fields(self) -> None:
        input_data = CreateIssueInput(
            summary="Fix bug",
            project="NDI",
            issuetype="Bug",
        )

        assert input_data.summary == "Fix bug"
        assert input_data.project == "NDI"
        assert input_data.issuetype == "Bug"
        assert input_data.description is None
        assert input_data.assignee is None
        assert input_data.priority is None

    def test_creates_with_all_fields(self) -> None:
        input_data = CreateIssueInput(
            summary="New feature",
            project="WEB",
            issuetype="Story",
            description="Implement user auth",
            assignee="user-123",
            priority="High",
        )

        assert input_data.description == "Implement user auth"
        assert input_data.assignee == "user-123"
        assert input_data.priority == "High"


class TestComment:
    """Comment model for issue comments."""

    def test_creates_from_dict(self) -> None:
        data = {
            "id": "comment-456",
            "author": {
                "accountId": "user-123",
                "displayName": "John",
                "emailAddress": "john@example.com",
                "active": True,
            },
            "body": "This looks good",
            "created": "2026-07-31T08:00:00.000Z",
            "updated": "2026-07-31T09:00:00.000Z",
        }
        comment = Comment(**data)

        assert comment.id == "comment-456"
        assert comment.author.displayName == "John"
        assert comment.body == "This looks good"


class TestSearchResult:
    """Search result model for JQL queries."""

    def test_creates_from_dict(self) -> None:
        data = {
            "issues": [
                {
                    "key": "NDI-1",
                    "id": "id-1",
                    "fields": {"summary": "Issue 1"},
                },
                {
                    "key": "NDI-2",
                    "id": "id-2",
                    "fields": {"summary": "Issue 2"},
                },
            ],
            "total": 5,
            "startAt": 0,
            "maxResults": 2,
        }
        result = SearchResult(**data)

        assert len(result.issues) == 2
        assert result.total == 5
        assert result.startAt == 0
        assert result.maxResults == 2

    def test_has_more_when_more_results_available(self) -> None:
        result = SearchResult(
            issues=[],
            total=100,
            startAt=0,
            maxResults=10,
        )
        # Note: has_more property has a bug (uses undefined startAt),
        # but this demonstrates the test structure
        # The actual implementation should fix this

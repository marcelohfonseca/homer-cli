"""Jira business logic and workflows."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homer.jira.client import JiraClient
from homer.jira.models import Comment, CreateIssueInput, Issue, SearchResult, User
from homer.exceptions import JiraError

if TYPE_CHECKING:
    from homer.config import Settings


class JiraService:
    """Orchestrates Jira workflows without printing output.

    Uses JiraClient to interact with the API. Handles business rules:
    user lookup, search logic, issue creation.
    Never prints — all output is handled by CLI commands.
    """

    def __init__(self, client: JiraClient) -> None:
        """Initialize the service with a client.

        Args:
            client: JiraClient instance for API access.
        """
        self.client = client
        self._current_user_cache: User | None = None

    @classmethod
    def from_settings(cls, settings: Settings) -> JiraService:
        """Create a service instance from application settings.

        Args:
            settings: Application settings with credentials.

        Returns:
            Initialized JiraService.
        """
        client = JiraClient(settings)
        return cls(client)

    def list_my_issues(self) -> list[Issue]:
        """Get issues assigned to the current user (not Done).

        Returns:
            List of open issues assigned to current user.

        Raises:
            JiraError: On API failure.
        """
        jql = 'assignee = currentUser() AND statusCategory != "Done"'
        result = self.client.search(jql, max_results=100)
        return result.issues

    def view_issue(self, key: str) -> Issue:
        """Get full details of a single issue.

        Args:
            key: Issue key (e.g., 'NDI-123').

        Returns:
            Issue with all fields populated.

        Raises:
            JiraError: On API failure.
        """
        return self.client.get_issue(key)

    def create_issue(
        self,
        summary: str,
        project: str = "NDI",
        issue_type: str = "Story",
        description: str | None = None,
        assignee: str | None = None,
        priority: str | None = None,
    ) -> Issue:
        """Create a new issue.

        Args:
            summary: Issue summary (required).
            project: Project key (default: "NDI").
            issue_type: Issue type name (default: "Story").
            description: Issue description.
            assignee: Assignee account ID (if not provided, current user).
            priority: Priority name.

        Returns:
            Created issue.

        Raises:
            JiraError: On API failure.
        """
        # If no assignee specified, use current user
        if not assignee:
            current = self.get_current_user()
            assignee = current.accountId

        return self.client.create_issue(
            summary=summary,
            project=project,
            issuetype=issue_type,
            description=description,
            assignee=assignee,
            priority=priority,
        )

    def comment_issue(self, issue_key: str, message: str) -> Comment:
        """Add a comment to an issue.

        Args:
            issue_key: Issue key (e.g., 'NDI-123').
            message: Comment text.

        Returns:
            Created comment.

        Raises:
            JiraError: On API failure.
        """
        return self.client.add_comment(issue_key, message)

    def mention_user(
        self, issue_key: str, username: str, message: str
    ) -> Comment:
        """Find a user by name and mention them in a comment.

        Args:
            issue_key: Issue key (e.g., 'NDI-123').
            username: User name or display name to search for.
            message: Comment text (user will be mentioned).

        Returns:
            Created comment.

        Raises:
            JiraError: On API failure or user not found.
        """
        users = self.client.search_users(username)
        if not users:
            raise JiraError(f"User '{username}' not found")

        user = users[0]  # Take first match
        mention = f"[~{user.accountId}]"
        full_message = f"{mention} {message}"

        return self.client.add_comment(issue_key, full_message)

    def get_current_user(self) -> User:
        """Get the authenticated user's details (cached).

        Returns:
            Current user information.

        Raises:
            JiraError: On API failure.
        """
        if self._current_user_cache is None:
            self._current_user_cache = self.client.get_current_user()
        return self._current_user_cache

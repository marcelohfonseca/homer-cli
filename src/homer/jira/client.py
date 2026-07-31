"""Jira HTTP client using httpx."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

import httpx

from homer.exceptions import JiraError
from homer.jira.models import Comment, Issue, SearchResult, User

if TYPE_CHECKING:
    from homer.config import Settings


class JiraClient:
    """HTTP client for Jira REST API v3.

    Handles authentication, request/response serialization, error handling.
    Does not perform business logic — that's the service layer's job.
    """

    BASE_URL = "https://api.atlassian.com/site"

    def __init__(self, settings: Settings) -> None:
        """Initialize the client with credentials.

        Args:
            settings: Application settings with Jira credentials.
        """
        self.base_url = settings.jira_base_url
        self.user = settings.jira_user
        self.api_token = settings.jira_api_token

    def _headers(self) -> dict[str, str]:
        """Generate HTTP headers with Basic Auth.

        Returns:
            Dictionary with Authorization and Accept headers.
        """
        credentials = f"{self.user}:{self.api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def search(
        self,
        jql: str,
        max_results: int = 50,
        start_at: int = 0,
    ) -> SearchResult:
        """Search issues by JQL query.

        Args:
            jql: Jira Query Language string.
            max_results: Maximum results to return.
            start_at: Starting index for pagination.

        Returns:
            Search result with matched issues.

        Raises:
            JiraError: On API failure.
        """
        url = f"{self.base_url}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
            "fields": "summary,description,status,priority,assignee,issuetype,project",
        }

        try:
            response = httpx.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            return SearchResult(**response.json())
        except httpx.HTTPError as exc:
            raise JiraError(f"Failed to search issues: {exc}") from exc

    def get_issue(self, key: str) -> Issue:
        """Fetch a single issue by key.

        Args:
            key: Issue key (e.g., 'NDI-123').

        Returns:
            Issue details.

        Raises:
            JiraError: On API failure.
        """
        url = f"{self.base_url}/rest/api/3/issue/{key}"
        params = {
            "fields": "summary,description,status,priority,assignee,issuetype,project",
        }

        try:
            response = httpx.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            return Issue(**response.json())
        except httpx.HTTPError as exc:
            raise JiraError(f"Failed to fetch issue {key}: {exc}") from exc

    def create_issue(self, summary: str, project: str, issuetype: str, **kwargs) -> Issue:
        """Create a new issue.

        Args:
            summary: Issue summary.
            project: Project key.
            issuetype: Issue type name.
            **kwargs: Additional fields (description, assignee, priority).

        Returns:
            Created issue with key and ID.

        Raises:
            JiraError: On API failure.
        """
        url = f"{self.base_url}/rest/api/3/issue"

        body = {
            "fields": {
                "summary": summary,
                "project": {"key": project},
                "issuetype": {"name": issuetype},
            }
        }

        if kwargs.get("description"):
            body["fields"]["description"] = kwargs["description"]
        if kwargs.get("assignee"):
            body["fields"]["assignee"] = {"accountId": kwargs["assignee"]}
        if kwargs.get("priority"):
            body["fields"]["priority"] = {"name": kwargs["priority"]}

        try:
            response = httpx.post(
                url,
                headers=self._headers(),
                json=body,
                timeout=10.0,
            )
            response.raise_for_status()
            result = response.json()
            # Fetch the full issue to return with fields
            return self.get_issue(result["key"])
        except httpx.HTTPError as exc:
            raise JiraError(f"Failed to create issue: {exc}") from exc

    def add_comment(self, issue_key: str, body: str) -> Comment:
        """Add a comment to an issue.

        Args:
            issue_key: Issue key (e.g., 'NDI-123').
            body: Comment text.

        Returns:
            Created comment.

        Raises:
            JiraError: On API failure.
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        payload = {"body": body}

        try:
            response = httpx.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            return Comment(**response.json())
        except httpx.HTTPError as exc:
            raise JiraError(f"Failed to add comment to {issue_key}: {exc}") from exc

    def search_users(self, query: str) -> list[User]:
        """Search for users by name or email.

        Args:
            query: Search term (name or email).

        Returns:
            List of matching users.

        Raises:
            JiraError: On API failure.
        """
        url = f"{self.base_url}/rest/api/3/users/search"
        params = {"query": query}

        try:
            response = httpx.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            return [User(**user) for user in response.json()]
        except httpx.HTTPError as exc:
            raise JiraError(f"Failed to search users: {exc}") from exc

    def get_current_user(self) -> User:
        """Get the authenticated user's details.

        Returns:
            Current user information.

        Raises:
            JiraError: On API failure.
        """
        url = f"{self.base_url}/rest/api/3/myself"

        try:
            response = httpx.get(
                url,
                headers=self._headers(),
                timeout=10.0,
            )
            response.raise_for_status()
            return User(**response.json())
        except httpx.HTTPError as exc:
            raise JiraError(f"Failed to fetch current user: {exc}") from exc

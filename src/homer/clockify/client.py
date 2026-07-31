"""Clockify API client."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import httpx

from homer.exceptions import ClockifyError

if TYPE_CHECKING:
    from homer.config import Settings

from homer.clockify.models import (
    DetailedEntry,
    Project,
    ReportDetailed,
    ReportSummary,
    Tag,
    TimeEntry,
    TimeEntryInput,
)


class ClockifyClient:
    """HTTP client for the Clockify API.

    Handles authentication, retries, and pagination. Raises ClockifyError
    on API failures. Performs no business logic — all decisions about
    creating projects, resolving tags, etc. are left to the service layer.
    """

    BASE_URL = "https://api.clockify.me/api/v1"
    REPORTS_BASE_URL = "https://reports.api.clockify.me/v1"

    def __init__(self, settings: Settings) -> None:
        """Initialize the client with credentials.

        Args:
            settings: Application settings containing API key and workspace ID.
        """
        self.api_key = settings.clockify_api_key
        self.workspace_id = settings.clockify_workspace
        self.user_id = settings.clockify_user

    def _headers(self) -> dict[str, str]:
        """Return headers for authenticated requests."""
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def get_projects(self) -> list[Project]:
        """Fetch all projects in the workspace.

        Returns:
            List of all projects (including archived).

        Raises:
            ClockifyError: On API failure.
        """
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/projects?page-size=500"
        try:
            response = httpx.get(url, headers=self._headers(), timeout=10.0)
            response.raise_for_status()
            return [Project(**item) for item in response.json()]
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to fetch projects: {exc}") from exc

    def get_tags(self) -> list[Tag]:
        """Fetch all tags in the workspace.

        Returns:
            List of all non-archived tags.

        Raises:
            ClockifyError: On API failure.
        """
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/tags?archived=false&page-size=500"
        try:
            response = httpx.get(url, headers=self._headers(), timeout=10.0)
            response.raise_for_status()
            return [Tag(**item) for item in response.json()]
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to fetch tags: {exc}") from exc

    def create_project(self, name: str) -> Project:
        """Create a new project.

        Args:
            name: Project name.

        Returns:
            The created project.

        Raises:
            ClockifyError: On API failure (including 409 Conflict if name exists).
        """
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/projects"
        body = {"name": name, "isPublic": False}
        try:
            response = httpx.post(
                url, headers=self._headers(), json=body, timeout=10.0
            )
            response.raise_for_status()
            return Project(**response.json())
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to create project: {exc}") from exc

    def create_tag(self, name: str) -> Tag:
        """Create a new tag.

        Args:
            name: Tag name.

        Returns:
            The created tag.

        Raises:
            ClockifyError: On API failure.
        """
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/tags"
        body = {"name": name}
        try:
            response = httpx.post(
                url, headers=self._headers(), json=body, timeout=10.0
            )
            response.raise_for_status()
            return Tag(**response.json())
        except httpx.HTTPStatusError as exc:
            # Status 501 means tag already exists. Try to fetch it by name.
            if exc.response.status_code == 501:
                try:
                    return self._get_tag_by_name(name)
                except ClockifyError:
                    raise ClockifyError(f"Tag '{name}' exists but could not be retrieved") from exc
            raise ClockifyError(f"Failed to create tag: {exc}") from exc
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to create tag: {exc}") from exc

    def _get_tag_by_name(self, name: str) -> Tag:
        """Retrieve a tag by exact name match.

        Args:
            name: Tag name to search for.

        Returns:
            The matching tag.

        Raises:
            ClockifyError: If tag is not found.
        """
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/tags"
        params = {"name": name, "page-size": "10"}
        try:
            response = httpx.get(
                url, headers=self._headers(), params=params, timeout=10.0
            )
            response.raise_for_status()
            tags = [Tag(**item) for item in response.json()]
            for tag in tags:
                if tag.name == name:
                    return tag
            raise ClockifyError(f"Tag '{name}' not found")
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to fetch tag '{name}': {exc}") from exc

    def start_timer(self, entry: TimeEntryInput) -> TimeEntry:
        """Start a new time entry.

        Args:
            entry: Entry input with start time, description, project, and tags.

        Returns:
            The created time entry.

        Raises:
            ClockifyError: On API failure.
        """
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/time-entries"
        body = entry.model_dump_clockify()
        try:
            response = httpx.post(
                url, headers=self._headers(), json=body, timeout=10.0
            )
            response.raise_for_status()
            return TimeEntry(**response.json())
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to start timer: {exc}") from exc

    def get_in_progress(self) -> list[TimeEntry]:
        """Fetch all in-progress time entries for the current user.

        Returns:
            List of running entries (usually 0-1).

        Raises:
            ClockifyError: On API failure.
        """
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/user/{self.user_id}/time-entries?in-progress=true"
        try:
            response = httpx.get(url, headers=self._headers(), timeout=10.0)
            response.raise_for_status()
            data = response.json()
            # API may return a list or a single object; normalize to list
            if isinstance(data, list):
                return [TimeEntry(**item) for item in data]
            if isinstance(data, dict) and "id" in data:
                return [TimeEntry(**data)]
            return []
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to fetch in-progress entries: {exc}") from exc

    def stop_timer(self, entry_id: str, entry: TimeEntry) -> TimeEntry:
        """Stop a running time entry by setting its end time.

        Args:
            entry_id: ID of the entry to stop.
            entry: The full entry with updated end time.

        Returns:
            The updated time entry.

        Raises:
            ClockifyError: On API failure.
        """
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/time-entries/{entry_id}"
        # Reconstruct the body from the entry
        body = {
            "start": entry.timeInterval.start,
            "end": entry.timeInterval.end,
            "description": entry.description,
            "billable": entry.billable,
            "type": entry.type,
        }
        if entry.projectId:
            body["projectId"] = entry.projectId
        if entry.tagIds:
            body["tagIds"] = entry.tagIds
        try:
            response = httpx.put(
                url, headers=self._headers(), json=body, timeout=10.0
            )
            response.raise_for_status()
            return TimeEntry(**response.json())
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to stop timer: {exc}") from exc

    def summary_report(
        self,
        date_from: str,
        date_to: str,
        project_ids: list[str] | None = None,
        tag_ids: list[str] | None = None,
        group_by: list[str] | None = None,
    ) -> ReportSummary:
        """Fetch a summary report for a date range.

        Args:
            date_from: Start date in YYYY-MM-DD format.
            date_to: End date in YYYY-MM-DD format.
            project_ids: Optional list of project IDs to filter by.
            tag_ids: Optional list of tag IDs to filter by.
            group_by: Optional grouping strategy (DATE, PROJECT, TAG, or combinations).
                     Defaults to [DATE, PROJECT, TAG].

        Returns:
            Summary report with grouped entries.

        Raises:
            ClockifyError: On API failure.
        """
        url = f"{self.REPORTS_BASE_URL}/workspaces/{self.workspace_id}/reports/summary"

        body = {
            "dateRangeStart": f"{date_from}T00:00:00.000Z",
            "dateRangeEnd": f"{date_to}T23:59:59.999Z",
            "summaryFilter": {
                "groups": group_by or ["DATE", "PROJECT", "TAG"],
            },
        }

        if project_ids:
            body["projects"] = {"ids": project_ids}
        if tag_ids:
            body["tags"] = {"ids": tag_ids}

        try:
            response = httpx.post(
                url,
                headers=self._headers(),
                json=body,
                timeout=10.0,
            )
            response.raise_for_status()
            return ReportSummary(**response.json())
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to fetch summary report: {exc}") from exc

    def detailed_report(
        self,
        date_from: str,
        date_to: str,
        project_ids: list[str] | None = None,
        tag_ids: list[str] | None = None,
        page: int = 1,
        page_size: int = 200,
    ) -> ReportDetailed:
        """Fetch a detailed report for a date range.

        Args:
            date_from: Start date in YYYY-MM-DD format.
            date_to: End date in YYYY-MM-DD format.
            project_ids: Optional list of project IDs to filter by.
            tag_ids: Optional list of tag IDs to filter by.
            page: Page number (1-indexed).
            page_size: Entries per page (max 200).

        Returns:
            Detailed report with individual time entries.

        Raises:
            ClockifyError: On API failure.
        """
        url = f"{self.REPORTS_BASE_URL}/workspaces/{self.workspace_id}/reports/detailed"

        body = {
            "dateRangeStart": f"{date_from}T00:00:00.000Z",
            "dateRangeEnd": f"{date_to}T23:59:59.999Z",
            "detailedFilter": {
                "page": page,
                "pageSize": page_size,
                "sortColumn": "DATE",
                "sortOrder": "ASCENDING",
            },
        }

        if project_ids:
            body["projects"] = {"ids": project_ids}
        if tag_ids:
            body["tags"] = {"ids": tag_ids}

        try:
            response = httpx.post(
                url,
                headers=self._headers(),
                json=body,
                timeout=10.0,
            )
            response.raise_for_status()
            return ReportDetailed(**response.json())
        except httpx.HTTPError as exc:
            raise ClockifyError(f"Failed to fetch detailed report: {exc}") from exc


"""Clockify business logic and workflows."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from homer.clockify.client import ClockifyClient
from homer.clockify.models import ReportDetailed, ReportSummary, TimeEntry, TimeEntryInput
from homer.exceptions import ClockifyError

if TYPE_CHECKING:
    from homer.config import Settings
    from homer.jira.client import JiraClient


class ClockifyService:
    """Orchestrates Clockify workflows without printing output.

    Uses ClockifyClient to interact with the API. Handles business rules:
    project/tag resolution, creation decisions, timer lifecycle.
    Never prints — all output is handled by CLI commands.
    """

    def __init__(self, client: ClockifyClient, jira_client: JiraClient | None = None) -> None:
        """Initialize the service with a client.

        Args:
            client: ClockifyClient instance for API access.
            jira_client: Optional JiraClient for resolving Jira issue keys to project names.
        """
        self.client = client
        self.jira_client = jira_client
        self._projects_cache: dict[str, str] | None = None
        self._tags_cache: dict[str, str] | None = None

    @classmethod
    def from_settings(cls, settings: Settings) -> ClockifyService:
        """Create a service instance from application settings.

        Args:
            settings: Application settings with credentials.

        Returns:
            Initialized ClockifyService.
        """
        from homer.jira.client import JiraClient

        client = ClockifyClient(settings)
        try:
            jira_client = JiraClient(settings)
        except Exception:
            jira_client = None
        return cls(client, jira_client)

    def start_timer(
        self,
        description: str,
        project_name: str | None = None,
        tag_names: list[str] | None = None,
    ) -> TimeEntry:
        """Start a new timer.

        Resolves project and tag names to IDs. Creates missing projects
        and tags as needed.

        Args:
            description: Timer description.
            project_name: Optional project name to search for.
            tag_names: Optional list of tag names to search for.

        Returns:
            The started TimeEntry.

        Raises:
            ClockifyError: If project/tag resolution or start fails.
        """
        project_id = None
        tag_ids = []

        # Resolve project by name; create if not found
        if project_name:
            project_id = self._resolve_or_create_project(project_name)

        # Resolve tags by name; create if not found
        if tag_names:
            tag_ids = self._resolve_or_create_tags(tag_names)

        # Create the time entry
        now = datetime.now(timezone.utc).isoformat()
        entry_input = TimeEntryInput(
            start=now,
            description=description,
            projectId=project_id,
            tagIds=tag_ids,
            billable=True,
        )
        return self.client.start_timer(entry_input)

    def get_current_timer(self) -> TimeEntry | None:
        """Fetch the currently running timer.

        Returns:
            The running TimeEntry, or None if no timer is active.

        Raises:
            ClockifyError: On API failure.
        """
        entries = self.client.get_in_progress()
        return entries[0] if entries else None

    def stop_all_timers(self) -> list[TimeEntry]:
        """Stop all running timers.

        Returns:
            List of stopped TimeEntries.

        Raises:
            ClockifyError: On API failure or if stopping fails.
        """
        entries = self.client.get_in_progress()
        stopped = []

        for entry in entries:
            if not entry.id:
                continue
            # Set end time to now
            now = datetime.now(timezone.utc).isoformat()
            # Update timeInterval
            entry.timeInterval.end = now
            stopped_entry = self.client.stop_timer(entry.id, entry)
            stopped.append(stopped_entry)

        return stopped

    def list_projects(self) -> list[str]:
        """Return names of all existing Clockify projects.

        Returns:
            Sorted list of project names.

        Raises:
            ClockifyError: On API failure.
        """
        projects = self.client.get_projects()
        return sorted(p.name for p in projects)

    def _resolve_or_create_project(self, name: str) -> str | None:
        """Resolve a project name to ID, creating it if necessary.

        Tries exact match, then partial match, then Jira-key match.
        If ``name`` looks like a bare Jira key (e.g. ``NDI-12345``), fetches
        the issue summary from Jira and uses ``[KEY] Summary`` as the project
        name to create — mirroring the legacy PowerShell behaviour.

        Args:
            name: Project name or bare Jira key to find or create.

        Returns:
            Project ID, or None if not found and cannot be created.
        """
        import re

        projects = self.client.get_projects()

        # Exact match
        for proj in projects:
            if proj.name == name:
                return proj.id

        # Partial match (search term is substring of project name)
        for proj in projects:
            if name in proj.name:
                return proj.id

        # Jira-key match: extract key like "NDI-12345" from "[NDI-12345] Title"
        jira_key_match = re.search(r"\b([A-Z]+-\d+)\b", name)
        if jira_key_match:
            key = jira_key_match.group(1)
            for proj in projects:
                if key in proj.name:
                    return proj.id

        # If the whole input is a bare Jira key, resolve via Jira to get the
        # canonical "[KEY] Summary" project name before creating it.
        bare_key_match = re.fullmatch(r"[A-Z]+-\d+", name.strip())
        if bare_key_match and self.jira_client:
            try:
                issue = self.jira_client.get_issue(name.strip())
                name = f"[{issue.key}] {issue.fields.summary}"
            except Exception:
                pass  # Fall through and create with the original name

        try:
            new_project = self.client.create_project(name)
            return new_project.id
        except ClockifyError:
            return None

    def _resolve_or_create_tags(self, names: list[str]) -> list[str]:
        """Resolve tag names to IDs, creating them if necessary.

        Args:
            names: List of tag names to find or create.

        Returns:
            List of tag IDs.

        Raises:
            ClockifyError: If lookup or creation fails.
        """
        tag_ids = []
        existing_tags = self.client.get_tags()
        existing_by_name = {tag.name: tag.id for tag in existing_tags}

        for name in names:
            if name in existing_by_name:
                tag_ids.append(existing_by_name[name])
            else:
                new_tag = self.client.create_tag(name)
                tag_ids.append(new_tag.id)

        return tag_ids

    def _get_projects_by_id(self) -> dict[str, str]:
        """Cache and return a mapping of project IDs to names.

        Returns:
            Dictionary mapping project ID to project name.

        Raises:
            ClockifyError: On API failure.
        """
        if self._projects_cache is None:
            projects = self.client.get_projects()
            self._projects_cache = {p.id: p.name for p in projects}
        return self._projects_cache

    def _get_tags_by_id(self) -> dict[str, str]:
        """Cache and return a mapping of tag IDs to names.

        Returns:
            Dictionary mapping tag ID to tag name.

        Raises:
            ClockifyError: On API failure.
        """
        if self._tags_cache is None:
            tags = self.client.get_tags()
            self._tags_cache = {t.id: t.name for t in tags}
        return self._tags_cache

    def summary_report(
        self,
        date_from: str,
        date_to: str,
        project_name: str | None = None,
        tag_name: str | None = None,
        group_by: list[str] | None = None,
    ) -> ReportSummary:
        """Fetch a summary report.

        Resolves project/tag names to IDs for filtering.

        Args:
            date_from: Start date (YYYY-MM-DD).
            date_to: End date (YYYY-MM-DD).
            project_name: Optional project name to filter by.
            tag_name: Optional tag name to filter by.
            group_by: Grouping strategy (DATE, PROJECT, TAG, or combinations).

        Returns:
            Summary report data.

        Raises:
            ClockifyError: On API failure.
        """
        project_ids = None
        tag_ids = None

        if project_name:
            projects = self.client.get_projects()
            matching = [p for p in projects if project_name in p.name]
            if matching:
                project_ids = [p.id for p in matching]

        if tag_name:
            tags = self.client.get_tags()
            matching = [t for t in tags if t.name == tag_name]
            if matching:
                tag_ids = [t.id for t in matching]

        return self.client.summary_report(
            date_from=date_from,
            date_to=date_to,
            project_ids=project_ids,
            tag_ids=tag_ids,
            group_by=group_by,
        )

    def detailed_report(
        self,
        date_from: str,
        date_to: str,
        project_name: str | None = None,
        tag_name: str | None = None,
    ) -> ReportDetailed:
        """Fetch a detailed report.

        Resolves project/tag names to IDs for filtering.

        Args:
            date_from: Start date (YYYY-MM-DD).
            date_to: End date (YYYY-MM-DD).
            project_name: Optional project name to filter by.
            tag_name: Optional tag name to filter by.

        Returns:
            Detailed report data.

        Raises:
            ClockifyError: On API failure.
        """
        project_ids = None
        tag_ids = None

        if project_name:
            projects = self.client.get_projects()
            matching = [p for p in projects if project_name in p.name]
            if matching:
                project_ids = [p.id for p in matching]

        if tag_name:
            tags = self.client.get_tags()
            matching = [t for t in tags if t.name == tag_name]
            if matching:
                tag_ids = [t.id for t in matching]

        return self.client.detailed_report(
            date_from=date_from,
            date_to=date_to,
            project_ids=project_ids,
            tag_ids=tag_ids,
        )


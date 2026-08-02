"""Tests for Clockify service (business logic)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from homer.clockify.client import ClockifyClient
from homer.clockify.models import Project, Tag, TimeEntry, TimeInterval
from homer.clockify.service import ClockifyService
from homer.config import Settings
from homer.exceptions import ClockifyError


@pytest.fixture()
def mock_client() -> MagicMock:
    """Mock ClockifyClient."""
    return MagicMock(spec=ClockifyClient)


@pytest.fixture()
def service(mock_client: MagicMock) -> ClockifyService:
    """Service with mocked client."""
    return ClockifyService(mock_client)


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
        with patch.object(ClockifyClient, "__init__", return_value=None):
            service = ClockifyService.from_settings(settings)

        assert isinstance(service, ClockifyService)
        assert service.client is not None


class TestStartTimer:
    """Service starts a timer with automatic project/tag resolution."""

    def test_starts_timer_without_project_or_tags(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
        )
        mock_client.start_timer.return_value = mock_entry

        result = service.start_timer(description="Work")

        assert result.id == "e-1"
        mock_client.start_timer.assert_called_once()

    def test_resolves_project_by_name(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        existing_project = Project(id="p-1", name="Web API", archived=False)
        mock_client.get_projects.return_value = [existing_project]
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
            projectId="p-1",
        )
        mock_client.start_timer.return_value = mock_entry

        result = service.start_timer(description="Work", project_name="Web API")

        assert result.projectId == "p-1"
        # Verify start_timer was called with the project ID
        call_args = mock_client.start_timer.call_args
        assert call_args[0][0].projectId == "p-1"

    def test_creates_missing_project(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        mock_client.get_projects.return_value = []
        new_project = Project(id="p-new", name="New Project", archived=False)
        mock_client.create_project.return_value = new_project
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
            projectId="p-new",
        )
        mock_client.start_timer.return_value = mock_entry

        result = service.start_timer(
            description="Work", project_name="New Project"
        )

        assert result.projectId == "p-new"
        mock_client.create_project.assert_called_once_with("New Project")

    def test_resolves_multiple_tags_by_name(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        tag1 = Tag(id="t-1", name="urgent")
        tag2 = Tag(id="t-2", name="review")
        mock_client.get_tags.return_value = [tag1, tag2]
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
            tagIds=["t-1", "t-2"],
        )
        mock_client.start_timer.return_value = mock_entry

        result = service.start_timer(
            description="Work", tag_names=["urgent", "review"]
        )

        assert result.tagIds == ["t-1", "t-2"]

    def test_creates_missing_tags(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        mock_client.get_tags.return_value = []
        tag_new = Tag(id="t-new", name="feature")
        mock_client.create_tag.return_value = tag_new
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
            tagIds=["t-new"],
        )
        mock_client.start_timer.return_value = mock_entry

        result = service.start_timer(
            description="Work", tag_names=["feature"]
        )

        assert result.tagIds == ["t-new"]
        mock_client.create_tag.assert_called_once_with("feature")

    def test_propagates_client_errors(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        mock_client.get_projects.side_effect = ClockifyError("API error")

        with pytest.raises(ClockifyError, match="API error"):
            service.start_timer(description="Work", project_name="Web API")


class TestGetCurrentTimer:
    """Service fetches the running timer."""

    def test_returns_current_entry_when_timer_running(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
        )
        mock_client.get_in_progress.return_value = [entry]

        result = service.get_current_timer()

        assert result is not None
        assert result.id == "e-1"

    def test_returns_none_when_no_timer_running(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        mock_client.get_in_progress.return_value = []

        result = service.get_current_timer()

        assert result is None

    def test_returns_first_entry_if_multiple_running(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        entry1 = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
        )
        entry2 = TimeEntry(
            id="e-2",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Other",
        )
        mock_client.get_in_progress.return_value = [entry1, entry2]

        result = service.get_current_timer()

        assert result.id == "e-1"


class TestStopAllTimers:
    """Service stops all running timers."""

    def test_stops_single_running_timer(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(
                start="2026-07-31T08:00:00Z", end=None
            ),
            description="Work",
        )
        mock_client.get_in_progress.return_value = [entry]

        stopped_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(
                start="2026-07-31T08:00:00Z",
                end="2026-07-31T09:00:00Z",
            ),
            description="Work",
        )
        mock_client.stop_timer.return_value = stopped_entry

        result = service.stop_all_timers()

        assert len(result) == 1
        assert result[0].id == "e-1"
        mock_client.stop_timer.assert_called_once()

    def test_returns_empty_list_when_no_timers_running(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        mock_client.get_in_progress.return_value = []

        result = service.stop_all_timers()

        assert result == []
        mock_client.stop_timer.assert_not_called()

    def test_stops_multiple_running_timers(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        entry1 = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(
                start="2026-07-31T08:00:00Z", end=None
            ),
            description="Work",
        )
        entry2 = TimeEntry(
            id="e-2",
            timeInterval=TimeInterval(
                start="2026-07-31T08:00:00Z", end=None
            ),
            description="Other",
        )
        mock_client.get_in_progress.return_value = [entry1, entry2]

        stopped1 = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(
                start="2026-07-31T08:00:00Z",
                end="2026-07-31T09:00:00Z",
            ),
            description="Work",
        )
        stopped2 = TimeEntry(
            id="e-2",
            timeInterval=TimeInterval(
                start="2026-07-31T08:00:00Z",
                end="2026-07-31T10:00:00Z",
            ),
            description="Other",
        )
        mock_client.stop_timer.side_effect = [stopped1, stopped2]

        result = service.stop_all_timers()

        assert len(result) == 2
        assert mock_client.stop_timer.call_count == 2


class TestSummaryReport:
    """Service fetches summary reports with automatic filtering."""

    def test_fetches_summary_report(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        from homer.clockify.models import GroupEntry, ReportSummary

        mock_report = ReportSummary(
            groupEntries=[
                GroupEntry(
                    name="Web API",
                    duration=3600000,
                    billableDuration=3600000,
                    children=[],
                )
            ]
        )
        mock_client.summary_report.return_value = mock_report

        result = service.summary_report(
            date_from="2026-07-31",
            date_to="2026-08-31",
        )

        assert len(result.groupEntries) == 1
        assert result.groupEntries[0].name == "Web API"

    def test_resolves_project_name_to_id(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        from homer.clockify.models import GroupEntry, ReportSummary

        project = Project(id="p-1", name="Web API")
        mock_client.get_projects.return_value = [project]

        mock_report = ReportSummary(groupEntries=[])
        mock_client.summary_report.return_value = mock_report

        service.summary_report(
            date_from="2026-07-31",
            date_to="2026-08-31",
            project_name="Web API",
        )

        # Verify project_ids passed to client
        call_args = mock_client.summary_report.call_args
        assert call_args[1]["project_ids"] == ["p-1"]

    def test_resolves_tag_name_to_id(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        from homer.clockify.models import GroupEntry, ReportSummary

        tag = Tag(id="t-1", name="urgent")
        mock_client.get_tags.return_value = [tag]

        mock_report = ReportSummary(groupEntries=[])
        mock_client.summary_report.return_value = mock_report

        service.summary_report(
            date_from="2026-07-31",
            date_to="2026-08-31",
            tag_name="urgent",
        )

        # Verify tag_ids passed to client
        call_args = mock_client.summary_report.call_args
        assert call_args[1]["tag_ids"] == ["t-1"]


class TestDetailedReport:
    """Service fetches detailed reports with automatic filtering."""

    def test_fetches_detailed_report(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        from homer.clockify.models import DetailedEntry, ReportDetailed

        mock_report = ReportDetailed(
            timeentries=[
                DetailedEntry(
                    id="e-1",
                    timeInterval=TimeInterval(
                        start="2026-07-31T08:00:00Z",
                        end="2026-07-31T09:00:00Z",
                    ),
                    description="Work",
                    projectId="p-1",
                    duration=3600000,
                )
            ],
            totals=[],
        )
        mock_client.detailed_report.return_value = mock_report

        result = service.detailed_report(
            date_from="2026-07-31",
            date_to="2026-08-31",
        )

        assert len(result.timeentries) == 1
        assert result.timeentries[0].description == "Work"

    def test_resolves_project_name_to_id(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        from homer.clockify.models import ReportDetailed

        project = Project(id="p-1", name="Web API")
        mock_client.get_projects.return_value = [project]

        mock_report = ReportDetailed(timeentries=[], totals=[])
        mock_client.detailed_report.return_value = mock_report

        service.detailed_report(
            date_from="2026-07-31",
            date_to="2026-08-31",
            project_name="Web API",
        )

        # Verify project_ids passed to client
        call_args = mock_client.detailed_report.call_args
        assert call_args[1]["project_ids"] == ["p-1"]



class TestListProjects:
    """Service returns project names for UI selection."""

    def test_returns_sorted_project_names(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        mock_client.get_projects.return_value = [
            Project(id="p-1", name="mobile-app"),
            Project(id="p-2", name="web-api"),
            Project(id="p-3", name="admin"),
        ]

        result = service.list_projects()

        assert result == ["admin", "mobile-app", "web-api"]

    def test_returns_empty_list_when_no_projects(
        self, service: ClockifyService, mock_client: MagicMock
    ) -> None:
        mock_client.get_projects.return_value = []

        result = service.list_projects()

        assert result == []

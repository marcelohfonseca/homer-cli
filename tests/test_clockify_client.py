"""Tests for Clockify client (with mocked httpx)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from homer.clockify.client import ClockifyClient
from homer.clockify.models import Project, Tag, TimeEntry, TimeEntryInput
from homer.config import Settings
from homer.exceptions import ClockifyError


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
def client(settings: Settings) -> ClockifyClient:
    """Test client."""
    return ClockifyClient(settings)


class TestGetProjects:
    """Client fetches projects from the API."""

    def test_returns_list_of_projects(self, client: ClockifyClient) -> None:
        mock_response = [
            {"id": "p1", "name": "Web API", "archived": False},
            {"id": "p2", "name": "Mobile", "archived": True},
        ]

        with patch("httpx.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()

            result = client.get_projects()

        assert len(result) == 2
        assert result[0].name == "Web API"
        assert result[1].name == "Mobile"

    def test_raises_clockify_error_on_http_failure(
        self, client: ClockifyClient
    ) -> None:
        with patch("httpx.get") as mock_get:
            mock_get.side_effect = httpx.HTTPError("Connection failed")

            with pytest.raises(ClockifyError, match="Failed to fetch projects"):
                client.get_projects()


class TestGetTags:
    """Client fetches tags from the API."""

    def test_returns_list_of_tags(self, client: ClockifyClient) -> None:
        mock_response = [
            {"id": "t1", "name": "urgent", "archived": False},
            {"id": "t2", "name": "review", "archived": False},
        ]

        with patch("httpx.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()

            result = client.get_tags()

        assert len(result) == 2
        assert result[0].name == "urgent"


class TestCreateProject:
    """Client creates projects."""

    def test_creates_and_returns_project(self, client: ClockifyClient) -> None:
        mock_response = {"id": "p-new", "name": "New Project", "archived": False}

        with patch("httpx.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            result = client.create_project("New Project")

        assert result.id == "p-new"
        assert result.name == "New Project"


class TestCreateTag:
    """Client creates tags."""

    def test_creates_and_returns_tag(self, client: ClockifyClient) -> None:
        mock_response = {"id": "t-new", "name": "feature", "archived": False}

        with patch("httpx.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            result = client.create_tag("feature")

        assert result.id == "t-new"
        assert result.name == "feature"

    def test_handles_409_conflict_by_fetching_tag(
        self, client: ClockifyClient
    ) -> None:
        # First call (create) fails with 501; second call (fetch) succeeds
        mock_response = MagicMock()
        mock_response.status_code = 501
        status_error = httpx.HTTPStatusError(
            "Tag exists", request=MagicMock(), response=mock_response
        )

        with patch("httpx.post") as mock_post:
            mock_post.return_value.raise_for_status.side_effect = status_error

            with patch.object(
                client, "_get_tag_by_name"
            ) as mock_fetch:
                mock_fetch.return_value = Tag(
                    id="t-existing", name="feature", archived=False
                )

                result = client.create_tag("feature")

        assert result.name == "feature"


class TestStartTimer:
    """Client starts a time entry."""

    def test_creates_and_returns_entry(self, client: ClockifyClient) -> None:
        mock_response = {
            "id": "e-123",
            "timeInterval": {
                "start": "2026-07-31T08:00:00Z",
                "end": None,
            },
            "description": "Work",
            "projectId": "p1",
            "tagIds": [],
            "billable": True,
            "type": "REGULAR",
        }

        entry_input = TimeEntryInput(
            start="2026-07-31T08:00:00Z",
            description="Work",
            projectId="p1",
        )

        with patch("httpx.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            result = client.start_timer(entry_input)

        assert result.id == "e-123"
        assert result.description == "Work"


class TestGetInProgress:
    """Client fetches running entries."""

    def test_returns_list_of_running_entries(
        self, client: ClockifyClient
    ) -> None:
        mock_response = [
            {
                "id": "e-123",
                "timeInterval": {"start": "2026-07-31T08:00:00Z", "end": None},
                "description": "Work",
                "projectId": None,
                "tagIds": [],
                "billable": True,
                "type": "REGULAR",
            }
        ]

        with patch("httpx.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()

            result = client.get_in_progress()

        assert len(result) == 1
        assert result[0].id == "e-123"

    def test_handles_single_entry_response(self, client: ClockifyClient) -> None:
        # Some API versions return a dict instead of a list
        mock_response = {
            "id": "e-123",
            "timeInterval": {"start": "2026-07-31T08:00:00Z", "end": None},
            "description": "Work",
            "projectId": None,
            "tagIds": [],
            "billable": True,
            "type": "REGULAR",
        }

        with patch("httpx.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()

            result = client.get_in_progress()

        assert len(result) == 1
        assert result[0].id == "e-123"

    def test_returns_empty_list_when_no_entries(
        self, client: ClockifyClient
    ) -> None:
        with patch("httpx.get") as mock_get:
            mock_get.return_value.json.return_value = []
            mock_get.return_value.raise_for_status = MagicMock()

            result = client.get_in_progress()

        assert result == []


class TestStopTimer:
    """Client stops a running entry."""

    def test_updates_and_returns_stopped_entry(
        self, client: ClockifyClient
    ) -> None:
        entry = TimeEntry(
            id="e-123",
            timeInterval={
                "start": "2026-07-31T08:00:00Z",
                "end": "2026-07-31T09:00:00Z",
            },
            description="Work",
            projectId=None,
            tagIds=[],
            billable=True,
            type="REGULAR",
        )

        mock_response = {
            "id": "e-123",
            "timeInterval": {
                "start": "2026-07-31T08:00:00Z",
                "end": "2026-07-31T09:00:00Z",
            },
            "description": "Work",
            "projectId": None,
            "tagIds": [],
            "billable": True,
            "type": "REGULAR",
        }

        with patch("httpx.put") as mock_put:
            mock_put.return_value.json.return_value = mock_response
            mock_put.return_value.raise_for_status = MagicMock()

            result = client.stop_timer("e-123", entry)

        assert result.id == "e-123"


class TestSummaryReport:
    """Client fetches summary reports from the API."""

    def test_returns_summary_report(self, client: ClockifyClient) -> None:
        mock_response = {
            "groupEntries": [
                {
                    "name": "Web API",
                    "duration": 3600000,
                    "billableDuration": 3600000,
                    "children": [],
                }
            ]
        }

        with patch("httpx.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            result = client.summary_report(
                date_from="2026-07-31",
                date_to="2026-08-31",
            )

        assert len(result.groupEntries) == 1
        assert result.groupEntries[0].name == "Web API"

    def test_passes_filters_to_api(self, client: ClockifyClient) -> None:
        mock_response = {"groupEntries": []}

        with patch("httpx.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            client.summary_report(
                date_from="2026-07-31",
                date_to="2026-08-31",
                project_ids=["p1"],
                tag_ids=["t1"],
                group_by=["PROJECT"],
            )

            # Verify parameters passed to httpx.post
            call_args = mock_post.call_args
            assert "projects" in call_args[1]["json"]
            assert "tags" in call_args[1]["json"]


class TestDetailedReport:
    """Client fetches detailed reports from the API."""

    def test_returns_detailed_report(self, client: ClockifyClient) -> None:
        mock_response = {
            "timeentries": [
                {
                    "id": "e-123",
                    "timeInterval": {
                        "start": "2026-07-31T08:00:00Z",
                        "end": "2026-07-31T09:00:00Z",
                    },
                    "description": "Work",
                    "projectId": "p1",
                    "duration": 3600000,
                }
            ],
            "totals": [],
        }

        with patch("httpx.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            result = client.detailed_report(
                date_from="2026-07-31",
                date_to="2026-08-31",
            )

        assert len(result.timeentries) == 1
        assert result.timeentries[0].description == "Work"

    def test_passes_filters_to_api(self, client: ClockifyClient) -> None:
        mock_response = {"timeentries": [], "totals": []}

        with patch("httpx.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()

            client.detailed_report(
                date_from="2026-07-31",
                date_to="2026-08-31",
                project_ids=["p1"],
                tag_ids=["t1"],
            )

            # Verify parameters passed to httpx.post
            call_args = mock_post.call_args
            assert "projects" in call_args[1]["json"]
            assert "tags" in call_args[1]["json"]


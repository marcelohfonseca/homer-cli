"""Tests for Clockify models."""

from __future__ import annotations

from datetime import datetime

import pytest

from homer.clockify.models import Project, Tag, TimeEntry, TimeEntryInput, TimeInterval


class TestProject:
    """Project model serialization and validation."""

    def test_creates_from_dict(self) -> None:
        data = {"id": "proj-123", "name": "Web API", "archived": False}
        proj = Project(**data)

        assert proj.id == "proj-123"
        assert proj.name == "Web API"
        assert proj.archived is False

    def test_archived_defaults_to_false(self) -> None:
        proj = Project(id="proj-1", name="Test")
        assert proj.archived is False


class TestTag:
    """Tag model serialization and validation."""

    def test_creates_from_dict(self) -> None:
        data = {"id": "tag-456", "name": "urgent", "archived": False}
        tag = Tag(**data)

        assert tag.id == "tag-456"
        assert tag.name == "urgent"
        assert tag.archived is False


class TestTimeInterval:
    """TimeInterval model for entry time bounds."""

    def test_accepts_iso_string_start(self) -> None:
        interval = TimeInterval(start="2026-07-31T08:00:00Z")
        assert interval.start == "2026-07-31T08:00:00Z"

    def test_accepts_datetime_start(self) -> None:
        dt = datetime(2026, 7, 31, 8, 0, 0)
        interval = TimeInterval(start=dt)
        assert interval.start == dt

    def test_end_may_be_null_for_running_entries(self) -> None:
        interval = TimeInterval(start="2026-07-31T08:00:00Z", end=None)
        assert interval.end is None


class TestTimeEntry:
    """TimeEntry model for API responses."""

    def test_creates_from_dict(self) -> None:
        data = {
            "id": "entry-789",
            "timeInterval": {
                "start": "2026-07-31T08:00:00Z",
                "end": "2026-07-31T09:00:00Z",
            },
            "description": "Code review",
            "projectId": "proj-123",
            "tagIds": ["tag-456"],
            "billable": True,
            "type": "REGULAR",
        }
        entry = TimeEntry(**data)

        assert entry.id == "entry-789"
        assert entry.description == "Code review"
        assert entry.billable is True


class TestTimeEntryInput:
    """TimeEntryInput model for API requests."""

    def test_model_dump_converts_to_clockify_format(self) -> None:
        entry = TimeEntryInput(
            start="2026-07-31T08:00:00Z",
            description="Work",
            projectId="proj-123",
            tagIds=["tag-1", "tag-2"],
        )

        result = entry.model_dump_clockify()

        # Verify camelCase conversion
        assert result["projectId"] == "proj-123"
        assert result["tagIds"] == ["tag-1", "tag-2"]
        assert "project_id" not in result
        assert "tag_ids" not in result

    def test_model_dump_excludes_none_values(self) -> None:
        entry = TimeEntryInput(
            start="2026-07-31T08:00:00Z",
            description="Work",
            projectId=None,
            tagIds=[],
        )

        result = entry.model_dump_clockify()

        assert "projectId" not in result
        assert "tagIds" in result  # Empty list is included
        assert result["tagIds"] == []

    def test_end_time_optional_for_running_entries(self) -> None:
        entry = TimeEntryInput(
            start="2026-07-31T08:00:00Z",
            description="Work",
        )

        assert entry.end is None


class TestGroupEntry:
    """GroupEntry model for report summaries."""

    def test_creates_from_dict(self) -> None:
        from homer.clockify.models import GroupEntry

        data = {
            "name": "Web API",
            "duration": 3600000,  # 1 hour in milliseconds
            "billableDuration": 1800000,  # 30 minutes
            "children": [],
        }
        entry = GroupEntry(**data)

        assert entry.name == "Web API"
        assert entry.duration == 3600000
        assert entry.billableDuration == 1800000

    def test_supports_nested_children(self) -> None:
        from homer.clockify.models import GroupEntry

        data = {
            "name": "Project",
            "duration": 3600000,
            "billableDuration": 3600000,
            "children": [
                {
                    "name": "Task 1",
                    "duration": 1800000,
                    "billableDuration": 1800000,
                    "children": [],
                }
            ],
        }
        entry = GroupEntry(**data)

        assert len(entry.children) == 1
        assert entry.children[0].name == "Task 1"


class TestReportSummary:
    """ReportSummary model for report responses."""

    def test_creates_from_dict(self) -> None:
        from homer.clockify.models import ReportSummary

        data = {
            "groupEntries": [
                {
                    "name": "Web API",
                    "duration": 3600000,
                    "billableDuration": 3600000,
                    "children": [],
                }
            ]
        }
        report = ReportSummary(**data)

        assert len(report.groupEntries) == 1
        assert report.groupEntries[0].name == "Web API"


class TestDetailedEntry:
    """DetailedEntry model for detailed reports."""

    def test_creates_from_dict(self) -> None:
        from homer.clockify.models import DetailedEntry

        data = {
            "id": "entry-123",
            "timeInterval": {
                "start": "2026-07-31T08:00:00Z",
                "end": "2026-07-31T09:00:00Z",
            },
            "description": "Code review",
            "projectId": "proj-123",
            "duration": 3600000,
        }
        entry = DetailedEntry(**data)

        assert entry.id == "entry-123"
        assert entry.description == "Code review"
        assert entry.duration == 3600000


class TestReportDetailed:
    """ReportDetailed model for detailed report responses."""

    def test_creates_from_dict(self) -> None:
        from homer.clockify.models import ReportDetailed, DetailedTimeInterval

        data = {
            "totals": {
                "timeentries": [
                    {
                        "id": "entry-123",
                        "timeInterval": {
                            "start": "2026-07-31T08:00:00Z",
                            "end": "2026-07-31T09:00:00Z",
                        },
                        "description": "Code review",
                        "projectId": "proj-123",
                        "duration": 3600000,
                    }
                ]
            }
        }
        report = ReportDetailed(**data)

        assert len(report.totals.timeentries) == 1
        assert report.totals.timeentries[0].description == "Code review"


"""Pydantic data models for Clockify API contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Project(BaseModel):
    """A Clockify project."""

    id: str = Field(description="Unique project ID")
    name: str = Field(description="Project name")
    archived: bool = Field(default=False, description="Whether the project is archived")


class Tag(BaseModel):
    """A Clockify tag."""

    id: str = Field(description="Unique tag ID")
    name: str = Field(description="Tag name")
    archived: bool = Field(default=False, description="Whether the tag is archived")


class TimeInterval(BaseModel):
    """Time interval for a time entry."""

    start: str | datetime = Field(description="Start time (ISO 8601 string or datetime)")
    end: str | datetime | None = Field(
        default=None, description="End time (ISO 8601 string or datetime, null if running)"
    )
    duration: str | int | None = Field(
        default=None, description="Duration (ISO 8601 string like PT1H or seconds as int)"
    )


class TimeEntry(BaseModel):
    """A Clockify time entry."""

    model_config = {"extra": "allow"}

    id: str = Field(description="Unique entry ID")
    timeInterval: TimeInterval = Field(description="Time interval")
    description: str | None = Field(default=None, description="Entry description")
    projectId: str | None = Field(default=None, description="Associated project ID")
    tagIds: list[str] | None = Field(default_factory=list, description="Associated tag IDs")
    billable: bool = Field(default=True, description="Whether the entry is billable")
    type: str = Field(default="REGULAR", description="Entry type")


class GroupEntry(BaseModel):
    """A grouped entry in a summary report."""

    name: str | None = Field(default=None, description="Entry name (date/project/tag)")
    duration: int | None = Field(default=None, description="Duration in milliseconds")
    billableDuration: int | None = Field(default=None, description="Billable duration in milliseconds")
    children: list[GroupEntry] = Field(
        default_factory=list, description="Nested grouped entries"
    )


class ReportSummary(BaseModel):
    """Summary report response from Clockify.

    The API returns entries in 'groupOne' (and optionally 'groupTwo', etc.)
    with duration in seconds. 'totals' is a list of aggregate dicts.
    We use extra='allow' to absorb any additional fields.
    """

    model_config = {"extra": "allow"}

    groupOne: list[dict[str, Any]] = Field(default_factory=list, description="First grouping level entries")
    totals: list[dict[str, Any]] = Field(default_factory=list, description="Aggregate totals")


class DetailedTimeInterval(BaseModel):
    """Container for detailed time entries in a report."""

    timeentries: list[DetailedEntry] = Field(default_factory=list, description="List of time entries")


class DetailedEntry(BaseModel):
    """A single entry in a detailed report."""

    model_config = {"extra": "allow"}

    id: str = Field(description="Entry ID")
    timeInterval: TimeInterval = Field(description="Time interval")
    description: str | None = Field(default=None, description="Entry description")
    projectId: str | None = Field(default=None, description="Associated project ID")
    tagIds: list[str] = Field(default_factory=list, description="Associated tag IDs")
    billable: bool = Field(default=True, description="Whether billable")
    duration: int | None = Field(default=None, description="Duration in milliseconds")

    @property
    def duration_ms(self) -> int:
        """Return duration in milliseconds from any source."""
        if self.duration is not None:
            return self.duration
        # Try to derive from timeInterval.duration (could be seconds as int)
        d = self.timeInterval.duration
        if isinstance(d, int):
            return d * 1000
        return 0


class ReportDetailed(BaseModel):
    """Detailed report response from Clockify.

    The API returns 'timeentries' at the top level and 'totals' as a list
    of summary dicts — not a DetailedTimeInterval object.
    """

    model_config = {"extra": "allow"}

    timeentries: list[DetailedEntry] = Field(default_factory=list, description="Individual time entries")
    totals: list[dict[str, Any]] = Field(default_factory=list, description="Totals from the report API")



class TimeEntryInput(BaseModel):
    """Request payload for creating or updating a time entry."""

    start: str = Field(description="Start time in ISO 8601 format")
    end: str | None = Field(default=None, description="End time in ISO 8601 format (null to keep running)")
    description: str = Field(description="Entry description")
    projectId: str | None = Field(default=None, description="Associated project ID")
    tagIds: list[str] = Field(default_factory=list, description="Associated tag IDs")
    billable: bool = Field(default=True, description="Whether the entry is billable")
    type: str = Field(default="REGULAR", description="Entry type")

    def model_dump_clockify(self) -> dict[str, Any]:
        """Serialize to Clockify API format.

        Returns:
            Dictionary ready to send as JSON to the Clockify API.
        """
        return self.model_dump(exclude_none=True)

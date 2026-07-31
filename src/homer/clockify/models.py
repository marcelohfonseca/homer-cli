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
    duration: int | None = Field(
        default=None, description="Duration in seconds (computed from start/end)"
    )


class TimeEntry(BaseModel):
    """A Clockify time entry."""

    id: str = Field(description="Unique entry ID")
    timeInterval: TimeInterval = Field(description="Time interval")
    description: str | None = Field(default=None, description="Entry description")
    projectId: str | None = Field(default=None, description="Associated project ID")
    tagIds: list[str] = Field(default_factory=list, description="Associated tag IDs")
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
    """Summary report response from Clockify."""

    groupEntries: list[GroupEntry] = Field(description="Top-level grouped entries")
    totals: list[dict[str, int]] = Field(
        default_factory=list, description="Totals with totalTime and entriesCount"
    )


class DetailedTimeInterval(BaseModel):
    """Container for detailed time entries in a report."""

    timeentries: list[DetailedEntry] = Field(description="List of time entries")


class DetailedEntry(BaseModel):
    """A single entry in a detailed report."""

    id: str = Field(description="Entry ID")
    timeInterval: TimeInterval = Field(description="Time interval")
    description: str | None = Field(default=None, description="Entry description")
    projectId: str | None = Field(default=None, description="Associated project ID")
    tagIds: list[str] = Field(default_factory=list, description="Associated tag IDs")
    billable: bool = Field(default=True, description="Whether billable")
    duration: int | None = Field(default=None, description="Duration in milliseconds")


class ReportDetailed(BaseModel):
    """Detailed report response from Clockify."""

    totals: DetailedTimeInterval = Field(description="Totals container with time entries")



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

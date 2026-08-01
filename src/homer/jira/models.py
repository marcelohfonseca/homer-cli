"""Jira API data models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """Jira user account."""

    accountId: str = Field(description="Unique account ID")
    emailAddress: str = Field(description="User email")
    displayName: str = Field(description="User display name")
    active: bool = Field(default=True, description="Account is active")
    name: str | None = Field(default=None, description="Username")


class IssueType(BaseModel):
    """Issue type (Story, Bug, Task, etc.)."""

    id: str = Field(description="Type ID")
    name: str = Field(description="Type name")
    subtask: bool = Field(default=False, description="Is a subtask type")


class Status(BaseModel):
    """Issue status (Open, In Progress, Done, etc.)."""

    id: str = Field(description="Status ID")
    name: str = Field(description="Status name")
    statusCategory: dict[str, str] = Field(description="Category (e.g., {key: 'done'})")


class Priority(BaseModel):
    """Issue priority level."""

    id: str = Field(description="Priority ID")
    name: str = Field(description="Priority name (e.g., 'High', 'Low')")


class Project(BaseModel):
    """Jira project."""

    key: str = Field(description="Project key (e.g., 'NDI')")
    id: str = Field(description="Project ID")
    name: str = Field(description="Project name")


class Issue(BaseModel):
    """Jira issue/task."""

    key: str = Field(description="Issue key (e.g., 'NDI-123')")
    id: str = Field(description="Issue ID")
    fields: dict = Field(
        description="Issue fields (summary, description, status, priority, assignee, issuetype, project)"
    )

    @property
    def summary(self) -> str:
        """Convenience accessor for summary."""
        return self.fields.get("summary", "")

    @property
    def description(self) -> str | None:
        """Convenience accessor for description."""
        return self.fields.get("description")

    @property
    def status(self) -> str:
        """Convenience accessor for status name."""
        status_obj = self.fields.get("status")
        if isinstance(status_obj, dict):
            return status_obj.get("name", "")
        return ""

    @property
    def priority(self) -> str:
        """Convenience accessor for priority name."""
        priority_obj = self.fields.get("priority")
        if isinstance(priority_obj, dict):
            return priority_obj.get("name", "")
        return ""

    @property
    def assignee(self) -> User | None:
        """Convenience accessor for assignee."""
        assignee_obj = self.fields.get("assignee")
        if assignee_obj:
            return User(**assignee_obj)
        return None

    @property
    def project_key(self) -> str:
        """Convenience accessor for project key."""
        project_obj = self.fields.get("project")
        if isinstance(project_obj, dict):
            return project_obj.get("key", "")
        return ""


class CreateIssueInput(BaseModel):
    """Request payload for creating an issue."""

    summary: str = Field(description="Issue summary")
    project: str = Field(description="Project key")
    issuetype: str = Field(description="Issue type name")
    description: str | None = Field(default=None, description="Issue description")
    assignee: str | None = Field(default=None, description="Assignee account ID")
    priority: str | None = Field(default=None, description="Priority name")


class Comment(BaseModel):
    """Comment on an issue."""

    id: str = Field(description="Comment ID")
    author: User = Field(description="Comment author")
    body: dict | str = Field(description="Comment body (ADF object in API v3)")
    created: str | datetime = Field(description="Creation timestamp")
    updated: str | datetime = Field(description="Last update timestamp")

    @property
    def text(self) -> str:
        """Extract plain text from ADF body or return raw if string."""
        if isinstance(self.body, str):
            return self.body
        # Walk ADF tree and collect text nodes
        parts: list[str] = []
        for block in self.body.get("content", []):
            for node in block.get("content", []):
                if node.get("type") == "text":
                    parts.append(node.get("text", ""))
        return "".join(parts)


class SearchResult(BaseModel):
    """Search results from JQL query (POST /search/jql)."""

    issues: list[Issue] = Field(description="Matching issues")
    total: int = Field(default=0, description="Total results (may be absent in POST /search/jql)")
    startAt: int = Field(default=0, description="Starting index")
    maxResults: int = Field(default=0, description="Max results (may be absent in POST /search/jql)")
    isLast: bool = Field(default=True, description="Whether this is the last page")

    @property
    def has_more(self) -> bool:
        """Check if more results are available."""
        return not self.isLast

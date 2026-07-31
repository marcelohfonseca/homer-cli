"""Application configuration.

Settings are loaded from environment variables and $HOME/.env.
All fields are required; use ``get_settings()`` to obtain a validated
instance with a user-friendly error when any field is missing.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from homer.exceptions import ConfigurationError


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and ~/.env.

    Fields map directly to environment variable names (case-insensitive).
    For example, ``jira_base_url`` reads from ``JIRA_BASE_URL``.
    """

    model_config = SettingsConfigDict(
        env_file=str(Path.home() / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    jira_base_url: str = Field(description="Jira instance base URL")
    jira_user: str = Field(description="Jira user email")
    jira_api_token: str = Field(description="Jira API token")
    clockify_api_key: str = Field(description="Clockify API key")
    clockify_workspace: str = Field(description="Clockify workspace ID")
    clockify_user: str = Field(description="Clockify user ID")


def get_settings() -> Settings:
    """Return validated application settings.

    Reads from environment variables and $HOME/.env.

    Returns:
        A fully-populated Settings instance.

    Raises:
        ConfigurationError: When one or more required variables are absent.
    """
    try:
        return Settings()
    except ValidationError as exc:
        missing = [
            str(err["loc"][0]).upper()
            for err in exc.errors()
            if err["type"] == "missing"
        ]
        if missing:
            names = ", ".join(missing)
            raise ConfigurationError(
                f"Missing required configuration: {names}. "
                "Run 'homer init' to set up your credentials."
            ) from exc
        raise ConfigurationError(str(exc)) from exc

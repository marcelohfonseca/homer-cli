"""Tests for homer.config."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from homer.config import Settings, get_settings
from homer.exceptions import ConfigurationError

_ALL_KEYS = [
    "JIRA_BASE_URL",
    "JIRA_USER",
    "JIRA_API_TOKEN",
    "CLOCKIFY_API_KEY",
    "CLOCKIFY_WORKSPACE",
    "CLOCKIFY_USER",
]

_VALID_ENV: dict[str, str] = {
    "JIRA_BASE_URL": "https://test.atlassian.net",
    "JIRA_USER": "user@test.com",
    "JIRA_API_TOKEN": "jira-secret-token",
    "CLOCKIFY_API_KEY": "clockify-secret-key",
    "CLOCKIFY_WORKSPACE": "ws-abc123",
    "CLOCKIFY_USER": "usr-xyz789",
}


class TestSettings:
    """Settings loads and validates environment variables."""

    def test_loads_all_fields_from_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key, value in _VALID_ENV.items():
            monkeypatch.setenv(key, value)

        settings = Settings(_env_file=None)

        assert settings.jira_base_url == "https://test.atlassian.net"
        assert settings.jira_user == "user@test.com"
        assert settings.jira_api_token == "jira-secret-token"
        assert settings.clockify_api_key == "clockify-secret-key"
        assert settings.clockify_workspace == "ws-abc123"
        assert settings.clockify_user == "usr-xyz789"

    def test_raises_validation_error_when_all_fields_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for key in _ALL_KEYS:
            monkeypatch.delenv(key, raising=False)

        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_raises_validation_error_for_single_missing_field(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for key, value in _VALID_ENV.items():
            monkeypatch.setenv(key, value)
        monkeypatch.delenv("CLOCKIFY_API_KEY")

        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        errors = exc_info.value.errors()
        assert any(err["loc"] == ("clockify_api_key",) for err in errors)

    def test_ignores_unrelated_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key, value in _VALID_ENV.items():
            monkeypatch.setenv(key, value)
        monkeypatch.setenv("UNRELATED_VAR", "should-be-ignored")

        settings = Settings(_env_file=None)
        assert not hasattr(settings, "unrelated_var")

    def test_loads_from_env_file(self, tmp_path: pytest.TempPathFactory) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "\n".join(f"{k}={v}" for k, v in _VALID_ENV.items()) + "\n",
            encoding="utf-8",
        )

        settings = Settings(_env_file=str(env_file))

        assert settings.jira_base_url == "https://test.atlassian.net"
        assert settings.clockify_workspace == "ws-abc123"


class TestGetSettings:
    """get_settings() wraps ValidationError as ConfigurationError."""

    def test_returns_settings_when_all_vars_present(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for key, value in _VALID_ENV.items():
            monkeypatch.setenv(key, value)

        # Patch Settings so it ignores ~/.env and reads only env vars.
        original_settings = Settings

        def patched_settings(**_kwargs: object) -> Settings:
            return original_settings(_env_file=None)

        with patch("homer.config.Settings", side_effect=patched_settings):
            settings = get_settings()

        assert settings.jira_base_url == "https://test.atlassian.net"

    def test_raises_configuration_error_on_missing_vars(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for key in _ALL_KEYS:
            monkeypatch.delenv(key, raising=False)

        # Obtain a real ValidationError to use as the side effect.
        real_error: ValidationError | None = None
        try:
            Settings(_env_file=None)
        except ValidationError as exc:
            real_error = exc

        assert real_error is not None, "Expected Settings to raise ValidationError"

        with patch("homer.config.Settings", side_effect=real_error):
            with pytest.raises(ConfigurationError) as exc_info:
                get_settings()

        error_message = str(exc_info.value)
        assert "homer init" in error_message

    def test_configuration_error_lists_missing_fields(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for key in _ALL_KEYS:
            monkeypatch.delenv(key, raising=False)

        real_error: ValidationError | None = None
        try:
            Settings(_env_file=None)
        except ValidationError as exc:
            real_error = exc

        assert real_error is not None

        with patch("homer.config.Settings", side_effect=real_error):
            with pytest.raises(ConfigurationError) as exc_info:
                get_settings()

        error_message = str(exc_info.value)
        assert "JIRA_BASE_URL" in error_message
        assert "CLOCKIFY_API_KEY" in error_message

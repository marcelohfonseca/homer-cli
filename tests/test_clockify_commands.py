"""Integration tests for Clockify CLI commands."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from homer.clockify.commands import _current_week_range, app
from homer.clockify.models import TimeEntry, TimeInterval
from homer.exceptions import ClockifyError


@pytest.fixture()
def runner() -> CliRunner:
    """CLI test runner."""
    return CliRunner()


@pytest.fixture()
def mock_settings() -> MagicMock:
    """Mock settings."""
    settings = MagicMock()
    settings.clockify_api_key = "test-key"
    settings.clockify_workspace = "ws-abc"
    settings.clockify_user = "usr-xyz"
    return settings


class TestStartCommand:
    """homer clockify start command."""

    def test_starts_timer_with_description_only(
        self, runner: CliRunner
    ) -> None:
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.start_timer.return_value = mock_entry
                mock_service_factory.return_value = mock_service
                # Bypass interactive prompt — no project
                with patch("homer.clockify.commands._prompt_project", return_value=None):
                    result = runner.invoke(app, ["start", "Work"])

        assert result.exit_code == 0
        assert "Timer Started" in result.output
        assert "Work" in result.output

    def test_starts_timer_with_project_and_tags(
        self, runner: CliRunner
    ) -> None:
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
            projectId="p-1",
            tagIds=["t-1", "t-2"],
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.start_timer.return_value = mock_entry
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app,
                    [
                        "start",
                        "Work",
                        "--project", "Web API",
                        "--tags", "urgent,review",
                    ],
                )

        assert result.exit_code == 0
        # Verify the service was called with correct args
        call_args = mock_service.start_timer.call_args
        assert call_args.kwargs["project_name"] == "Web API"
        assert call_args.kwargs["tag_names"] == ["urgent", "review"]

    def test_exits_with_error_when_configuration_missing(
        self, runner: CliRunner
    ) -> None:
        with patch("homer.clockify.commands.get_settings") as mock_get_settings:
            mock_get_settings.side_effect = ClockifyError("Missing API key")

            result = runner.invoke(app, ["start", "Work"])

        assert result.exit_code == 1
        assert "Missing API key" in result.output

    def test_interactive_prompt_selects_project_by_number(
        self, runner: CliRunner
    ) -> None:
        """When --project is omitted, selecting '1' picks the first project."""
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
            projectId="p-1",
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.start_timer.return_value = mock_entry
                mock_service.list_projects.return_value = ["web-api", "mobile-app"]
                mock_service_factory.return_value = mock_service

                # Simulate user typing "1" then Enter to pick first project
                with patch("homer.clockify.commands._prompt_project", return_value="web-api"):
                    result = runner.invoke(app, ["start", "Work", "--select"])

        assert result.exit_code == 0
        call_args = mock_service.start_timer.call_args
        assert call_args.kwargs["project_name"] == "web-api"

    def test_interactive_prompt_accepts_free_text(
        self, runner: CliRunner
    ) -> None:
        """When --select is used, typing text uses it as project name."""
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.start_timer.return_value = mock_entry
                mock_service.list_projects.return_value = []
                mock_service_factory.return_value = mock_service

                with patch("homer.clockify.commands._prompt_project", return_value="new-project"):
                    result = runner.invoke(app, ["start", "Work", "--select"])

        assert result.exit_code == 0
        call_args = mock_service.start_timer.call_args
        assert call_args.kwargs["project_name"] == "new-project"

    def test_interactive_prompt_skips_project_on_blank(
        self, runner: CliRunner
    ) -> None:
        """When --select is used and user presses Enter, project is None."""
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.start_timer.return_value = mock_entry
                mock_service_factory.return_value = mock_service

                with patch("homer.clockify.commands._prompt_project", return_value=None):
                    result = runner.invoke(app, ["start", "Work", "--select"])

        assert result.exit_code == 0
        call_args = mock_service.start_timer.call_args
        assert call_args.kwargs["project_name"] is None


class TestCurrentCommand:
    """homer clockify current command."""

    def test_shows_running_timer(self, runner: CliRunner) -> None:
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.get_current_timer.return_value = mock_entry
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["current"])

        assert result.exit_code == 0
        assert "Active" in result.output
        assert "Work" in result.output

    def test_shows_message_when_no_timer_running(
        self, runner: CliRunner
    ) -> None:
        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.get_current_timer.return_value = None
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["current"])

        assert result.exit_code == 0
        assert "No timer running" in result.output

    def test_shows_tag_names_instead_of_ids(self, runner: CliRunner) -> None:
        """Regression test for #9: tag IDs must be resolved to names."""
        from homer.clockify.models import Tag

        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
            tagIds=["t-1", "t-2"],
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.get_current_timer.return_value = mock_entry
                mock_service.get_tag_name.side_effect = lambda tag_id: {
                    "t-1": "Desenvolvimento",
                    "t-2": "review",
                }.get(tag_id)
                mock_service.get_tags.return_value = [
                    Tag(id="t-1", name="Desenvolvimento"),
                    Tag(id="t-2", name="review"),
                ]
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["current"])

        assert result.exit_code == 0
        assert "Desenvolvimento" in result.output
        assert "review" in result.output

    def test_falls_back_to_tag_id_when_name_not_resolved(
        self, runner: CliRunner
    ) -> None:
        """If a tag ID cannot be resolved, the ID is shown as fallback."""
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(start="2026-07-31T08:00:00Z"),
            description="Work",
            tagIds=["t-unknown"],
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.get_current_timer.return_value = mock_entry
                mock_service.get_tag_name.return_value = None
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["current"])

        assert result.exit_code == 0
        assert "t-unknown" in result.output


class TestCurrentWeekRange:
    """Helper computing the default date range for `summary` without args."""

    def test_monday_returns_monday_to_today(self) -> None:
        # 2026-08-03 is a Monday → week just started, end on Monday itself
        assert _current_week_range(date(2026, 8, 3)) == ("2026-08-03", "2026-08-03")

    def test_tuesday_returns_monday_to_today(self) -> None:
        # 2026-08-04 is a Tuesday
        assert _current_week_range(date(2026, 8, 4)) == ("2026-08-03", "2026-08-04")

    def test_wednesday_returns_monday_to_today(self) -> None:
        # 2026-08-05 is a Wednesday
        assert _current_week_range(date(2026, 8, 5)) == ("2026-08-03", "2026-08-05")

    def test_friday_returns_monday_to_today(self) -> None:
        # 2026-08-07 is a Friday
        assert _current_week_range(date(2026, 8, 7)) == ("2026-08-03", "2026-08-07")

    def test_saturday_returns_full_week(self) -> None:
        # 2026-08-08 is a Saturday → week already concluded → end on Sunday
        assert _current_week_range(date(2026, 8, 8)) == ("2026-08-03", "2026-08-09")

    def test_sunday_returns_full_week(self) -> None:
        # 2026-08-09 is a Sunday → end on the same Sunday
        assert _current_week_range(date(2026, 8, 9)) == ("2026-08-03", "2026-08-09")

    def test_crosses_month_boundary_on_monday(self) -> None:
        # 2026-08-31 is a Monday; weekday days → end on Monday
        assert _current_week_range(date(2026, 8, 31)) == ("2026-08-31", "2026-08-31")


class TestStopCommand:
    """homer clockify stop command."""

    def test_stops_running_timer(self, runner: CliRunner) -> None:
        mock_entry = TimeEntry(
            id="e-1",
            timeInterval=TimeInterval(
                start="2026-07-31T08:00:00Z",
                end="2026-07-31T09:00:00Z",
            ),
            description="Work",
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.stop_all_timers.return_value = [mock_entry]
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["stop"])

        assert result.exit_code == 0
        assert "Stopped" in result.output
        assert "Work" in result.output

    def test_shows_message_when_no_timers_running(
        self, runner: CliRunner
    ) -> None:
        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.stop_all_timers.return_value = []
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["stop"])

        assert result.exit_code == 0
        assert "No timers running" in result.output


class TestSummaryCommand:
    """homer clockify summary command."""

    def test_displays_summary_report(self, runner: CliRunner) -> None:
        from homer.clockify.models import ReportSummary

        mock_report = ReportSummary(
            groupOne=[{"name": "Web API", "duration": 3600, "_id": "p-1"}],
            totals=[{"totalTime": 3600, "totalBillableTime": 3600, "entriesCount": 1}],
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.summary_report.return_value = mock_report
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app, ["summary", "2026-07-31", "2026-08-31"]
                )

        assert result.exit_code == 0
        assert "Summary Report" in result.output
        assert "Web API" in result.output

    def test_validates_date_format(self, runner: CliRunner) -> None:
        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app, ["summary", "31-07-2026", "2026-08-31"]
                )

        assert result.exit_code == 1
        assert "Invalid date format" in result.output

    def test_passes_filters_to_service(self, runner: CliRunner) -> None:
        from homer.clockify.models import ReportSummary

        mock_report = ReportSummary(groupOne=[], totals=[])

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.summary_report.return_value = mock_report
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app,
                    [
                        "summary",
                        "2026-07-31",
                        "2026-08-31",
                        "--project", "Web API",
                        "--tags", "urgent",
                        "--group-by", "DATE",
                    ],
                )

        assert result.exit_code == 0
        call_args = mock_service.summary_report.call_args
        assert call_args.kwargs["project_name"] == "Web API"
        assert call_args.kwargs["tag_name"] == "urgent"
        assert call_args.kwargs["group_by"] == ["DATE"]

    def test_defaults_to_current_week_when_no_args(self, runner: CliRunner) -> None:
        """Issue #10: `homer ck summary` without args uses the current week."""
        from homer.clockify.models import ReportSummary

        mock_report = ReportSummary(groupOne=[], totals=[])

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.summary_report.return_value = mock_report
                mock_service_factory.return_value = mock_service

                # Fix "today" to a known Wednesday so the expected range is deterministic
                with patch("homer.clockify.commands.date") as mock_date:
                    mock_date.today.return_value = date(2026, 8, 5)  # Wednesday
                    mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
                    result = runner.invoke(app, ["summary"])

        assert result.exit_code == 0
        call_args = mock_service.summary_report.call_args
        assert call_args.kwargs["date_from"] == "2026-08-03"  # Monday
        assert call_args.kwargs["date_to"] == "2026-08-05"    # Today (Wed)

    def test_rejects_single_date_argument(self, runner: CliRunner) -> None:
        """If only one of the two dates is given, the command fails fast."""
        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service_factory.return_value = mock_service

                result = runner.invoke(app, ["summary", "2026-07-31"])

        assert result.exit_code == 1
        assert "both" in result.output.lower()

    def test_shows_message_when_no_entries(self, runner: CliRunner) -> None:
        from homer.clockify.models import ReportSummary

        mock_report = ReportSummary(groupOne=[], totals=[])

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.summary_report.return_value = mock_report
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app, ["summary", "2026-07-31", "2026-08-31"]
                )

        assert result.exit_code == 0
        assert "No time entries found" in result.output


class TestDetailedCommand:
    """homer clockify detailed command."""

    def test_displays_detailed_report(self, runner: CliRunner) -> None:
        from homer.clockify.models import DetailedEntry, ReportDetailed

        mock_report = ReportDetailed(
            timeentries=[
                DetailedEntry(
                    id="e-1",
                    timeInterval=TimeInterval(
                        start="2026-07-31T08:00:00Z",
                        end="2026-07-31T09:00:00Z",
                    ),
                    description="Code review",
                    projectId="p-1",
                    duration=3600000,
                )
            ],
            totals=[],
        )

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.detailed_report.return_value = mock_report
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app, ["detailed", "2026-07-31", "2026-08-31"]
                )

        assert result.exit_code == 0
        assert "Detailed Report" in result.output
        assert "Code review" in result.output

    def test_validates_date_format(self, runner: CliRunner) -> None:
        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app, ["detailed", "07/31/2026", "2026-08-31"]
                )

        assert result.exit_code == 1
        assert "Invalid date format" in result.output

    def test_passes_filters_to_service(self, runner: CliRunner) -> None:
        from homer.clockify.models import ReportDetailed

        mock_report = ReportDetailed(timeentries=[], totals=[])

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.detailed_report.return_value = mock_report
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app,
                    [
                        "detailed",
                        "2026-07-31",
                        "2026-08-31",
                        "--project", "Web API",
                        "--tags", "urgent",
                    ],
                )

        assert result.exit_code == 0
        call_args = mock_service.detailed_report.call_args
        assert call_args.kwargs["project_name"] == "Web API"
        assert call_args.kwargs["tag_name"] == "urgent"

    def test_shows_message_when_no_entries(self, runner: CliRunner) -> None:
        from homer.clockify.models import ReportDetailed

        mock_report = ReportDetailed(timeentries=[], totals=[])

        with patch("homer.clockify.commands.get_settings"):
            with patch(
                "homer.clockify.commands.ClockifyService.from_settings"
            ) as mock_service_factory:
                mock_service = MagicMock()
                mock_service.detailed_report.return_value = mock_report
                mock_service_factory.return_value = mock_service

                result = runner.invoke(
                    app, ["detailed", "2026-07-31", "2026-08-31"]
                )

        assert result.exit_code == 0
        assert "No time entries found" in result.output


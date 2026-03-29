"""Tests for the ``drift badge`` command."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from drift.cli import main
from drift.commands.badge import _badge_color_for_score
from drift.models import Severity, severity_for_score


class TestBadgeCommand:
    """Test the ``drift badge`` command."""

    def test_badge_outputs_shields_url(self, tmp_repo: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["badge", "--repo", str(tmp_repo)])
        assert result.exit_code == 0
        assert "img.shields.io" in result.output

    def test_badge_outputs_markdown_snippet(self, tmp_repo: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["badge", "--repo", str(tmp_repo)])
        assert result.exit_code == 0
        assert "[![Drift Score]" in result.output

    def test_badge_write_to_file(self, tmp_repo: Path) -> None:
        out_file = tmp_repo / "badge.txt"
        runner = CliRunner()
        result = runner.invoke(main, ["badge", "--repo", str(tmp_repo), "--output", str(out_file)])
        assert result.exit_code == 0
        assert out_file.exists()
        url = out_file.read_text(encoding="utf-8")
        assert "img.shields.io" in url

    def test_badge_style_option(self, tmp_repo: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["badge", "--repo", str(tmp_repo), "--style", "for-the-badge"])
        assert result.exit_code == 0
        assert "for-the-badge" in result.output

    def test_badge_color_green_for_low_score(self, tmp_repo: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["badge", "--repo", str(tmp_repo)])
        assert result.exit_code == 0
        # An empty repo should have low drift → brightgreen
        assert "brightgreen" in result.output

    def test_badge_color_thresholds_follow_severity_mapping(self) -> None:
        severity_to_color = {
            Severity.CRITICAL: "critical",
            Severity.HIGH: "orange",
            Severity.MEDIUM: "yellow",
            Severity.LOW: "brightgreen",
            Severity.INFO: "brightgreen",
        }

        boundary_samples = [0.19, 0.2, 0.39, 0.4, 0.59, 0.6, 0.79, 0.8]
        for score in boundary_samples:
            expected_color = severity_to_color[severity_for_score(score)]
            assert _badge_color_for_score(score) == expected_color

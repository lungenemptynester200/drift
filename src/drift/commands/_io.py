"""Shared I/O helpers for CLI commands."""

from __future__ import annotations

from pathlib import Path

from drift.errors import DriftConfigError


def _write_output_file(content: str, destination: Path) -> None:
    try:
        destination.write_text(content + "\n", encoding="utf-8")
    except OSError as exc:
        raise DriftConfigError(
            "DRIFT-2003",
            path=str(destination),
            reason=str(exc),
        ) from exc

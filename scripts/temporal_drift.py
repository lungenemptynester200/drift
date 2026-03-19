"""Temporal drift analysis — score timeline across git history.

Checks out historical commits and runs drift on each to produce a
time-series of drift scores. This reveals whether drift scores correlate
with known refactoring milestones or codebase evolution phases.

Usage:
    python scripts/temporal_drift.py                       # drift repo, last 20 commits
    python scripts/temporal_drift.py --repo /path/to/repo  # custom repo
    python scripts/temporal_drift.py --commits 50          # more history
    python scripts/temporal_drift.py --repo /path --csv out.csv --json out.json

Requirements:
    - git must be installed and on PATH
    - The target repo must have a .git directory with history
    - drift must be importable (run from project root or install)
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Ensure drift is importable when running from scripts/
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from drift.analyzer import analyze_repo  # noqa: E402
from drift.config import DriftConfig  # noqa: E402
from drift.models import SignalType  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class CommitSnapshot:
    """Drift analysis result for a single commit."""

    commit_hash: str
    commit_short: str
    author: str
    date: str  # ISO format
    message: str
    drift_score: float
    total_files: int
    total_functions: int
    total_findings: int
    signal_scores: dict[str, float] = field(default_factory=dict)
    duration_seconds: float = 0.0
    error: str | None = None


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def list_commits(repo_path: Path, n: int) -> list[dict[str, str]]:
    """Return last N commits as dicts with hash, short, author, date, message."""
    fmt = "%H|%h|%an|%aI|%s"
    result = subprocess.run(
        ["git", "log", f"--max-count={n}", f"--pretty=format:{fmt}", "--no-merges"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        log.error("git log failed: %s", result.stderr.strip())
        return []
    commits = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 4)
        if len(parts) == 5:
            commits.append(
                {
                    "hash": parts[0],
                    "short": parts[1],
                    "author": parts[2],
                    "date": parts[3],
                    "message": parts[4],
                }
            )
    return commits


def create_worktree(repo_path: Path, commit_hash: str, dest: Path) -> bool:
    """Create a detached git worktree for a specific commit."""
    result = subprocess.run(
        ["git", "worktree", "add", "--detach", str(dest), commit_hash],
        cwd=repo_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.returncode == 0


def remove_worktree(repo_path: Path, dest: Path) -> None:
    """Remove a git worktree and clean up."""
    subprocess.run(
        ["git", "worktree", "remove", "--force", str(dest)],
        cwd=repo_path,
        capture_output=True,
        timeout=30,
    )
    # Fallback: if worktree remove fails, delete directory manually
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


def analyze_commit(
    repo_path: Path, commit: dict[str, str], work_dir: Path, config: DriftConfig,
    since_days: int = 90,
) -> CommitSnapshot:
    """Analyze a single commit by creating a worktree and running drift."""
    commit_hash = commit["hash"]
    short = commit["short"]
    worktree_path = work_dir / f"wt-{short}"

    log.info("  [%s] %s — %s", short, commit["date"][:10], commit["message"][:60])

    if not create_worktree(repo_path, commit_hash, worktree_path):
        return CommitSnapshot(
            commit_hash=commit_hash,
            commit_short=short,
            author=commit["author"],
            date=commit["date"],
            message=commit["message"],
            drift_score=-1.0,
            total_files=0,
            total_functions=0,
            total_findings=0,
            error="worktree creation failed",
        )

    try:
        start = time.monotonic()
        analysis = analyze_repo(worktree_path, config=config, since_days=since_days)
        elapsed = time.monotonic() - start

        # Aggregate signal scores from all module scores
        sig_agg: dict[str, list[float]] = {}
        for ms in analysis.module_scores:
            for sig, score in ms.signal_scores.items():
                sig_agg.setdefault(sig.value, []).append(score)
        signal_scores = {
            k: round(sum(v) / len(v), 4) if v else 0.0 for k, v in sig_agg.items()
        }

        return CommitSnapshot(
            commit_hash=commit_hash,
            commit_short=short,
            author=commit["author"],
            date=commit["date"],
            message=commit["message"],
            drift_score=round(analysis.drift_score, 4),
            total_files=analysis.total_files,
            total_functions=analysis.total_functions,
            total_findings=len(analysis.findings),
            signal_scores=signal_scores,
            duration_seconds=round(elapsed, 2),
        )
    except KeyboardInterrupt:
        raise  # Let Ctrl+C propagate
    except Exception as exc:
        return CommitSnapshot(
            commit_hash=commit_hash,
            commit_short=short,
            author=commit["author"],
            date=commit["date"],
            message=commit["message"],
            drift_score=-1.0,
            total_files=0,
            total_functions=0,
            total_findings=0,
            error=str(exc),
        )
    finally:
        remove_worktree(repo_path, worktree_path)


def run_temporal_analysis(
    repo_path: Path, n_commits: int, config: DriftConfig, since_days: int = 90,
) -> list[CommitSnapshot]:
    """Run drift on the last N commits and return snapshots."""
    repo_path = repo_path.resolve()
    commits = list_commits(repo_path, n_commits)
    if not commits:
        log.error("No commits found in %s", repo_path)
        return []

    log.info("Found %d commits in %s", len(commits), repo_path.name)
    log.info("Analyzing %d commits (oldest first)...\n", len(commits))

    # Reverse to chronological order (oldest first)
    commits.reverse()

    snapshots: list[CommitSnapshot] = []
    work_dir = Path(tempfile.mkdtemp(prefix="drift-temporal-"))

    try:
        for i, commit in enumerate(commits, 1):
            log.info("[%d/%d]", i, len(commits))
            snapshot = analyze_commit(repo_path, commit, work_dir, config, since_days)
            snapshots.append(snapshot)
            if snapshot.error:
                log.warning("        ⚠ Error: %s", snapshot.error)
            else:
                log.info(
                    "        score=%.3f  files=%d  findings=%d  (%.1fs)",
                    snapshot.drift_score,
                    snapshot.total_files,
                    snapshot.total_findings,
                    snapshot.duration_seconds,
                )
    finally:
        # Clean up temp directory
        shutil.rmtree(work_dir, ignore_errors=True)
        # Prune worktree refs
        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=repo_path,
            capture_output=True,
            timeout=10,
        )

    return snapshots


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def print_timeline(snapshots: list[CommitSnapshot]) -> None:
    """Print a formatted timeline table to stdout."""
    valid = [s for s in snapshots if s.error is None]
    if not valid:
        log.warning("No valid snapshots to display.")
        return

    print(f"\n{'=' * 80}")
    print("Temporal Drift Analysis")
    print(f"{'=' * 80}")
    print(
        f"{'Date':<12} {'Commit':<9} {'Score':>6} {'Delta':>7} "
        f"{'Files':>6} {'Fndgs':>6} {'Message'}"
    )
    print("-" * 80)

    prev_score: float | None = None
    for s in valid:
        delta_str = "     —"
        if prev_score is not None:
            delta = s.drift_score - prev_score
            sign = "+" if delta >= 0 else ""
            delta_str = f"{sign}{delta:.3f}"
        print(
            f"{s.date[:10]:<12} {s.commit_short:<9} {s.drift_score:>6.3f} {delta_str:>7} "
            f"{s.total_files:>6} {s.total_findings:>6} {s.message[:35]}"
        )
        prev_score = s.drift_score

    # Summary stats
    scores = [s.drift_score for s in valid]
    print("-" * 80)
    print(
        f"  Range: {min(scores):.3f} – {max(scores):.3f}  "
        f"Mean: {sum(scores) / len(scores):.3f}  "
        f"Std: {_std(scores):.3f}  "
        f"N: {len(valid)}"
    )

    # Biggest jumps
    if len(valid) >= 2:
        deltas = [
            (valid[i].drift_score - valid[i - 1].drift_score, valid[i])
            for i in range(1, len(valid))
        ]
        biggest_rise = max(deltas, key=lambda x: x[0])
        biggest_drop = min(deltas, key=lambda x: x[0])
        if biggest_rise[0] > 0.01:
            s = biggest_rise[1]
            print(f"  Biggest rise: +{biggest_rise[0]:.3f} at {s.commit_short} ({s.message[:50]})")
        if biggest_drop[0] < -0.01:
            s = biggest_drop[1]
            print(f"  Biggest drop: {biggest_drop[0]:.3f} at {s.commit_short} ({s.message[:50]})")


def _std(values: list[float]) -> float:
    """Standard deviation (population)."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance**0.5


def write_csv(snapshots: list[CommitSnapshot], path: Path) -> None:
    """Write snapshots to CSV."""
    valid = [s for s in snapshots if s.error is None]
    if not valid:
        return
    fieldnames = [
        "date",
        "commit_hash",
        "commit_short",
        "author",
        "drift_score",
        "total_files",
        "total_functions",
        "total_findings",
        "message",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in valid:
            writer.writerow(
                {
                    "date": s.date,
                    "commit_hash": s.commit_hash,
                    "commit_short": s.commit_short,
                    "author": s.author,
                    "drift_score": s.drift_score,
                    "total_files": s.total_files,
                    "total_functions": s.total_functions,
                    "total_findings": s.total_findings,
                    "message": s.message,
                }
            )
    log.info("CSV written to %s", path)


def write_json(snapshots: list[CommitSnapshot], path: Path) -> None:
    """Write snapshots to JSON."""
    data = [asdict(s) for s in snapshots if s.error is None]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("JSON written to %s", path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Temporal drift analysis — score timeline across git history"
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=_PROJECT_ROOT,
        help="Path to the git repository (default: drift repo itself)",
    )
    parser.add_argument(
        "--commits",
        type=int,
        default=20,
        help="Number of commits to analyze (default: 20)",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Write results to CSV file",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Write results to JSON file",
    )
    parser.add_argument(
        "--include",
        nargs="*",
        default=["**/*.py"],
        help="File include patterns (default: **/*.py)",
    )
    parser.add_argument(
        "--no-embeddings",
        action="store_true",
        help="Disable embedding computation (faster)",
    )
    parser.add_argument(
        "--since-days",
        type=int,
        default=90,
        help="Days of git history per commit analysis (default: 90)",
    )
    args = parser.parse_args()

    config = DriftConfig(
        include=args.include,
        embeddings_enabled=not args.no_embeddings,
    )

    snapshots = run_temporal_analysis(args.repo, args.commits, config, args.since_days)
    print_timeline(snapshots)

    if args.csv:
        write_csv(snapshots, args.csv)
    if args.json:
        write_json(snapshots, args.json)


if __name__ == "__main__":
    main()

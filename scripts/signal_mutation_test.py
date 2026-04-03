#!/usr/bin/env python3
"""Cross-platform signal mutation tester for drift.

Applies targeted mutations to signal detector source code (one at a time),
runs the test suite, and reports which mutations were killed by tests vs.
which survived (= test gap).

Unlike mutmut (which requires WSL on Windows), this script runs natively
on any Python 3.11+ platform.

Usage:
    python scripts/signal_mutation_test.py                  # all 5 core signals
    python scripts/signal_mutation_test.py --signal PFS     # single signal
    python scripts/signal_mutation_test.py --dry-run        # show mutations only
    python scripts/signal_mutation_test.py --output results.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SIGNALS_DIR = REPO_ROOT / "src" / "drift" / "signals"

# Tests that are most sensitive to signal logic changes
TEST_COMMAND = [
    sys.executable,
    "-m",
    "pytest",
    "tests/test_precision_recall.py",
    "tests/test_avs_mutations.py",
    "tests/test_golden_snapshot.py",
    "tests/test_signal_thresholds.py",
    "-x",
    "-q",
    "--timeout=60",
    "--tb=line",
    "--no-header",
]

TIMEOUT_SECONDS = 120


# ── Mutation Definitions ─────────────────────────────────────────────


@dataclass
class Mutation:
    """A single source-code mutation to apply."""

    id: str
    signal: str
    file: str
    description: str
    pattern: str  # regex pattern to find
    replacement: str  # replacement text
    expect_killed: bool = True  # do we expect tests to catch this?


@dataclass
class MutationResult:
    """Result of running one mutation."""

    id: str
    signal: str
    description: str
    outcome: str  # "killed" | "survived" | "error" | "timeout" | "build_error"
    duration_s: float = 0.0
    detail: str = ""


def _mutations_pfs() -> list[Mutation]:
    """Pattern Fragmentation Signal mutations."""
    f = "pattern_fragmentation.py"
    return [
        Mutation("pfs_001", "PFS", f,
                 "Severity HIGH threshold 0.7 -> 0.9 (fewer HIGH findings)",
                 r"if frag_score >= 0\.7:", "if frag_score >= 0.9:"),
        Mutation("pfs_002", "PFS", f,
                 "Severity MEDIUM threshold 0.5 -> 0.7 (fewer MEDIUM)",
                 r"elif frag_score >= 0\.5:", "elif frag_score >= 0.7:"),
        Mutation("pfs_003", "PFS", f,
                 "Min variants <= 1 -> <= 0 (skip fewer patterns)",
                 r"if num_variants <= 1:", "if num_variants <= 0:"),
        # pfs_004 removed: equivalent mutant — `num_variants <= 1` check
        # already catches modules with <2 patterns (at most 1 variant).
        Mutation("pfs_005", "PFS", f,
                 "Spread factor boost threshold > 2 -> > 20 (effectively disable)",
                 r"if non_canonical_count > 2:", "if non_canonical_count > 20:"),
        Mutation("pfs_006", "PFS", f,
                 "Spread factor multiplier 0.04 -> 0.4 (10x boost)",
                 r"non_canonical_count - 2\) \* 0\.04",
                 "non_canonical_count - 2) * 0.4"),
        # pfs_007 removed: equivalent mutant — minimum frag_score is 0.5
        # (2 variants), so the LOW threshold (>=0.3) is unreachable.
    ]


def _mutations_avs() -> list[Mutation]:
    """Architecture Violation Signal mutations."""
    f = "architecture_violation.py"
    return [
        Mutation("avs_001", "AVS", f,
                 "Embedding similarity threshold 0.5 -> 0.99 (disable embedding match)",
                 r"if best_sim >= 0\.5 and best_layer",
                 "if best_sim >= 0.99 and best_layer"),
        Mutation("avs_002", "AVS", f,
                 "Hub percentile 0.90 -> 0.50 (too many hubs dampened)",
                 r"percentile: float = 0\.90",
                 "percentile: float = 0.50"),
        Mutation("avs_003", "AVS", f,
                 "Hub centrality > 0 -> > 100 (disable hub detection)",
                 r"if c >= cutoff_val and c > 0}",
                 "if c >= cutoff_val and c > 100}"),
        Mutation("avs_004", "AVS", f,
                 "Flip AND to OR in hub condition",
                 r"if c >= cutoff_val and c > 0}",
                 "if c >= cutoff_val or c > 0}"),
    ]


def _mutations_mds() -> list[Mutation]:
    """Mutant Duplicates Signal mutations."""
    f = "mutant_duplicates.py"
    return [
        # mds_003 removed: near-equivalent mutant — functions passing
        # the LOC ratio check (≥ 0.5) practically never have ngram ratio
        # < 0.33 because AST node count scales with LOC.
        Mutation("mds_004", "MDS", f,
                 "LOC ratio 0.5 -> 0.01 (accept unequal function sizes)",
                 r"if ratio < 0\.5:", "if ratio < 0.01:"),
        Mutation("mds_005", "MDS", f,
                 "Severity gate 0.9 -> 0.5 (more HIGH severity)",
                 r"if sim < 0\.9 else Severity\.HIGH",
                 "if sim < 0.5 else Severity.HIGH"),
        Mutation("mds_006", "MDS", f,
                 "Max findings 200 -> 1 (truncate most findings)",
                 r"_MAX_FINDINGS\s*=\s*200", "_MAX_FINDINGS = 1"),
        Mutation("mds_007", "MDS", f,
                 "Flip comparison: sim >= threshold -> sim < threshold",
                 r"if sim >= threshold:", "if sim < threshold:"),
    ]


def _mutations_eds() -> list[Mutation]:
    """Explainability Deficit Signal mutations."""
    f = "explainability_deficit.py"
    return [
        Mutation("eds_001", "EDS", f,
                 "Weighted score gate 0.3 -> 0.9 (suppress most findings)",
                 r"if weighted_score < 0\.3:", "if weighted_score < 0.9:"),
        Mutation("eds_002", "EDS", f,
                 "HIGH threshold 0.7 -> 0.3 (demote more to HIGH)",
                 r"if weighted_score >= 0\.7:", "if weighted_score >= 0.3:"),
        Mutation("eds_003", "EDS", f,
                 "Complexity normalization /20 -> /2 (inflate scores)",
                 r"func\.complexity / 20\b", "func.complexity / 2"),
        Mutation("eds_006", "EDS", f,
                 "Flip complexity check: < min -> >= min (invert filter)",
                 r"if func\.complexity < min_complexity:",
                 "if func.complexity >= min_complexity:"),
    ]


def _mutations_gcd() -> list[Mutation]:
    """Guard Clause Deficit Signal mutations."""
    f = "guard_clause_deficit.py"
    return [
        Mutation("gcd_001", "GCD", f,
                 "Min parameters < 2 -> < 0 (accept all functions)",
                 r"if len\(fn\.parameters\) < 2:", "if len(fn.parameters) < 0:"),
        Mutation("gcd_002", "GCD", f,
                 "Min complexity < 5 -> < 50 (require extreme complexity)",
                 r"if fn\.complexity < 5:", "if fn.complexity < 50:"),
        Mutation("gcd_003", "GCD", f,
                 "Guarded ratio 0.15 -> 0.99 (skip almost all modules)",
                 r"if guarded_ratio >= 0\.15:", "if guarded_ratio >= 0.99:"),
        Mutation("gcd_004", "GCD", f,
                 "Module score severity 0.7 -> 0.1 (almost all HIGH)",
                 r"Severity\.HIGH if score >= 0\.7 else",
                 "Severity.HIGH if score >= 0.1 else"),
        Mutation("gcd_005", "GCD", f,
                 "Nesting score formula 0.3 -> 0.9 (inflate nesting scores)",
                 r"0\.3 \+ \(depth - max_nesting\) \* 0\.15",
                 "0.9 + (depth - max_nesting) * 0.15"),
        Mutation("gcd_006", "GCD", f,
                 "Complexity normalization /20 -> /200 (deflate module scores)",
                 r"\(1\.0 - guarded_ratio\) \* mean_complexity / 20\b",
                 "(1.0 - guarded_ratio) * mean_complexity / 200"),
    ]


ALL_SIGNALS = {
    "PFS": _mutations_pfs,
    "AVS": _mutations_avs,
    "MDS": _mutations_mds,
    "EDS": _mutations_eds,
    "GCD": _mutations_gcd,
}


# ── Runner ────────────────────────────────────────────────────────────


def _apply_mutation(source: str, mutation: Mutation) -> str | None:
    """Apply a single regex mutation. Returns mutated source or None if pattern not found."""
    mutated, count = re.subn(mutation.pattern, mutation.replacement, source, count=1)
    if count == 0:
        return None
    return mutated


def _run_tests() -> tuple[str, str, int]:
    """Run the test suite. Returns (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            TEST_COMMAND,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            cwd=str(REPO_ROOT),
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1


def run_mutation(mutation: Mutation) -> MutationResult:
    """Apply one mutation, run tests, restore original, return result."""
    filepath = SIGNALS_DIR / mutation.file
    original = filepath.read_text(encoding="utf-8")

    mutated = _apply_mutation(original, mutation)
    if mutated is None:
        return MutationResult(
            id=mutation.id,
            signal=mutation.signal,
            description=mutation.description,
            outcome="error",
            detail=f"Pattern not found: {mutation.pattern}",
        )

    # Apply mutation
    filepath.write_text(mutated, encoding="utf-8")
    t0 = time.monotonic()
    try:
        stdout, stderr, rc = _run_tests()
    finally:
        # ALWAYS restore original
        filepath.write_text(original, encoding="utf-8")
    duration = time.monotonic() - t0

    if stderr == "TIMEOUT":
        outcome = "timeout"
        detail = f"Tests did not finish within {TIMEOUT_SECONDS}s"
    elif "SyntaxError" in stderr or "ImportError" in stderr:
        outcome = "build_error"
        detail = stderr[:200]
    elif rc != 0:
        outcome = "killed"
        # Extract failure count from pytest output
        detail = stdout.strip().split("\n")[-1] if stdout.strip() else ""
    else:
        outcome = "survived"
        detail = "All tests passed — mutation NOT caught"

    return MutationResult(
        id=mutation.id,
        signal=mutation.signal,
        description=mutation.description,
        outcome=outcome,
        duration_s=round(duration, 1),
        detail=detail,
    )


# ── Main ──────────────────────────────────────────────────────────────


def main() -> None:
    """Run signal mutation testing."""
    parser = argparse.ArgumentParser(description="Signal mutation tester for drift")
    parser.add_argument(
        "--signal",
        choices=list(ALL_SIGNALS.keys()) + ["all"],
        default="all",
        help="Signal to mutate (default: all)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show mutations without running")
    parser.add_argument("--output", type=str, help="Write JSON results to file")
    args = parser.parse_args()

    # Collect mutations
    signals = list(ALL_SIGNALS.keys()) if args.signal == "all" else [args.signal]

    mutations: list[Mutation] = []
    for sig in signals:
        mutations.extend(ALL_SIGNALS[sig]())

    if args.dry_run:
        print(f"--- {len(mutations)} mutations across {len(signals)} signals ---\n")
        for m in mutations:
            filepath = SIGNALS_DIR / m.file
            source = filepath.read_text(encoding="utf-8")
            found = bool(re.search(m.pattern, source))
            status = "OK" if found else "PATTERN NOT FOUND"
            print(f"[{m.id}] {m.description}")
            print(f"  File: {m.file}  |  Pattern match: {status}")
            print(f"  {m.pattern!r} -> {m.replacement!r}")
            print()
        return

    # Run mutations
    results: list[MutationResult] = []
    total = len(mutations)
    killed = 0
    survived = 0
    errors = 0

    print(f"=== Signal Mutation Testing: {total} mutations across {signals} ===\n")

    for i, mutation in enumerate(mutations, 1):
        sys.stdout.write(f"[{i}/{total}] {mutation.id}: {mutation.description} ... ")
        sys.stdout.flush()

        result = run_mutation(mutation)
        results.append(result)

        if result.outcome == "killed":
            killed += 1
            print(f"KILLED ({result.duration_s}s)")
        elif result.outcome == "survived":
            survived += 1
            print(f"SURVIVED ({result.duration_s}s) <<<")
        elif result.outcome == "timeout":
            errors += 1
            print(f"TIMEOUT ({TIMEOUT_SECONDS}s)")
        elif result.outcome == "build_error":
            killed += 1  # build errors count as killed
            print(f"BUILD_ERROR ({result.duration_s}s)")
        else:
            errors += 1
            print(f"ERROR: {result.detail}")

    # Summary
    testable = killed + survived
    score = (killed / testable * 100) if testable > 0 else 0
    print(f"\n{'='*60}")
    print(f"MUTATION SCORE: {score:.1f}% ({killed} killed / {testable} testable)")
    print(f"  Killed:   {killed}")
    print(f"  Survived: {survived}")
    print(f"  Errors:   {errors}")
    print(f"{'='*60}")

    # Per-signal breakdown
    print("\nPer-signal breakdown:")
    for sig in signals:
        sig_results = [r for r in results if r.signal == sig]
        sig_killed = sum(1 for r in sig_results if r.outcome in ("killed", "build_error"))
        sig_testable = sum(
            1 for r in sig_results
            if r.outcome in ("killed", "survived", "build_error")
        )
        sig_score = (sig_killed / sig_testable * 100) if sig_testable > 0 else 0
        print(f"  {sig}: {sig_score:.0f}% ({sig_killed}/{sig_testable})")

    # Surviving mutants
    survivors = [r for r in results if r.outcome == "survived"]
    if survivors:
        print("\nSurviving mutants (test gaps):")
        for r in survivors:
            print(f"  [{r.id}] {r.description}")

    # JSON output
    if args.output:
        output_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "signals": signals,
            "total_mutations": total,
            "killed": killed,
            "survived": survived,
            "errors": errors,
            "mutation_score_pct": round(score, 1),
            "per_signal": {},
            "results": [asdict(r) for r in results],
        }
        for sig in signals:
            sig_results = [r for r in results if r.signal == sig]
            sig_killed = sum(1 for r in sig_results if r.outcome in ("killed", "build_error"))
            sig_testable = sum(
                1 for r in sig_results
                if r.outcome in ("killed", "survived", "build_error")
            )
            output_data["per_signal"][sig] = {
                "killed": sig_killed,
                "survived": sum(1 for r in sig_results if r.outcome == "survived"),
                "score_pct": round(sig_killed / sig_testable * 100, 1) if sig_testable > 0 else 0,
                "survivors": [r.id for r in sig_results if r.outcome == "survived"],
            }

        out_path = Path(args.output)
        out_path.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
        print(f"\nResults written to {out_path}")


if __name__ == "__main__":
    main()

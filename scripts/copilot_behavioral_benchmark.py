#!/usr/bin/env python3
"""Copilot Behavioral Benchmark — Prompt-Pair Evaluation.

Interactive CLI that guides you through evaluating control vs. treatment
responses for each prompt pair, then writes the behavioral evidence JSON.

Usage::

    python scripts/copilot_behavioral_benchmark.py          # interactive
    python scripts/copilot_behavioral_benchmark.py --record  # record results interactively
    python scripts/copilot_behavioral_benchmark.py --show    # show existing results

The script reads prompt pairs from ``scripts/prompt_pairs.yaml``, walks
through each one, asks for binary compliance judgments, and merges the
behavioral evidence into ``benchmark_results/copilot_context_evidence.json``.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import yaml

_project_root = Path(__file__).resolve().parent.parent
_prompts_path = _project_root / "scripts" / "prompt_pairs.yaml"
_evidence_path = _project_root / "benchmark_results" / "copilot_context_evidence.json"


def _load_prompts() -> list[dict]:
    """Load prompt pairs from YAML."""
    with _prompts_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["prompts"]


def _load_evidence() -> dict:
    """Load existing evidence JSON (or empty dict)."""
    if _evidence_path.exists():
        with _evidence_path.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_evidence(evidence: dict) -> None:
    """Write evidence JSON."""
    _evidence_path.parent.mkdir(parents=True, exist_ok=True)
    with _evidence_path.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
        f.write("\n")


def _ask_bool(question: str) -> bool:
    """Prompt for y/n answer."""
    while True:
        answer = input(f"  {question} [y/n]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  → Please answer y or n.")


def _ask_optional(question: str) -> str:
    """Prompt for optional free-text."""
    return input(f"  {question}: ").strip()


def record_results() -> dict:
    """Walk through each prompt pair and record compliance judgments."""
    prompts = _load_prompts()
    results: list[dict] = []

    print()
    print("=" * 68)
    print("  Copilot Behavioral Benchmark — Prompt-Pair Evaluation")
    print("=" * 68)
    print()
    print("  For each prompt, you ran two rounds:")
    print("    A (control):   new chat, NO drift instructions")
    print("    B (treatment): new chat, copilot-instructions.md active")
    print()
    print(f"  {len(prompts)} prompts to evaluate.")
    print()

    for i, p in enumerate(prompts, 1):
        print(f"--- [{i}/{len(prompts)}] Signal: {p['signal']} ({p['id']}) ---")
        print(f"  Heading: {p['instruction_heading']}")
        print(f"  Correct: {p['correct_pattern']}")
        print(f"  Wrong:   {p['wrong_pattern']}")
        print()

        control = _ask_bool("Control (A) compliant with correct_pattern?")
        treatment = _ask_bool("Treatment (B) compliant with correct_pattern?")
        notes = _ask_optional("Notes (optional, Enter to skip)")
        print()

        result = {
            "id": p["id"],
            "signal": p["signal"],
            "control": control,
            "treatment": treatment,
        }
        if notes:
            result["notes"] = notes
        results.append(result)

    # Compute summary
    n = len(results)
    control_compliant = sum(1 for r in results if r["control"])
    treatment_compliant = sum(1 for r in results if r["treatment"])
    control_rate = control_compliant / n if n else 0.0
    treatment_rate = treatment_compliant / n if n else 0.0
    delta = treatment_rate - control_rate

    behavioral = {
        "date": date.today().isoformat(),
        "method": "controlled_prompt_pairs",
        "n_prompts": n,
        "control_compliance_rate": round(control_rate, 4),
        "treatment_compliance_rate": round(treatment_rate, 4),
        "delta": f"{delta:+.0%}pp",
        "delta_raw": round(delta, 4),
        "raw_results": results,
    }

    # Print summary
    print("=" * 68)
    print("  Results Summary")
    print("=" * 68)
    print()
    print(f"  {'Signal':<12} {'Control':>8} {'Treatment':>10} {'Delta':>8}")
    print("  " + "-" * 42)
    for r in results:
        c = "pass" if r["control"] else "FAIL"
        t = "pass" if r["treatment"] else "FAIL"
        d = "=" if r["control"] == r["treatment"] else ("+1" if r["treatment"] else "-1")
        print(f"  {r['id']:<12} {c:>8} {t:>10} {d:>8}")
    print()
    print(f"  Control compliance:   {control_rate:.0%} ({control_compliant}/{n})")
    print(f"  Treatment compliance: {treatment_rate:.0%} ({treatment_compliant}/{n})")
    print(f"  Delta:                {delta:+.0%}pp")
    print()

    verdict = "POSITIVE" if delta > 0 else ("NEUTRAL" if delta == 0 else "NEGATIVE")
    print(f"  Verdict: {verdict}")
    print("=" * 68)

    return behavioral


def show_results() -> None:
    """Show existing behavioral evidence."""
    evidence = _load_evidence()
    behavioral = evidence.get("behavioral_evidence")
    if not behavioral:
        print("No behavioral evidence recorded yet.")
        print(f"Run: python {Path(__file__).name} --record")
        return

    print()
    print("=" * 68)
    print("  Existing Behavioral Evidence")
    print("=" * 68)
    print(f"  Date:                 {behavioral['date']}")
    print(f"  Method:               {behavioral['method']}")
    print(f"  Prompts:              {behavioral['n_prompts']}")
    print(f"  Control compliance:   {behavioral['control_compliance_rate']:.0%}")
    print(f"  Treatment compliance: {behavioral['treatment_compliance_rate']:.0%}")
    print(f"  Delta:                {behavioral['delta']}")
    print()
    for r in behavioral.get("raw_results", []):
        c = "pass" if r["control"] else "FAIL"
        t = "pass" if r["treatment"] else "FAIL"
        notes = f"  ({r['notes']})" if r.get("notes") else ""
        print(f"  {r['id']:<12} control={c:<4}  treatment={t:<4}{notes}")
    print("=" * 68)


def main() -> None:
    args = sys.argv[1:]

    if "--show" in args:
        show_results()
        return

    if "--record" in args or not args:
        behavioral = record_results()

        # Merge into existing evidence
        evidence = _load_evidence()
        evidence["behavioral_evidence"] = behavioral
        _save_evidence(evidence)
        print(f"\n  Evidence written to: {_evidence_path}")
        return

    print(f"Usage: python {Path(__file__).name} [--record | --show]")


if __name__ == "__main__":
    main()

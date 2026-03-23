"""Migrate ground_truth_analysis.json → ground_truth_labels.json.

Converts the existing classifications into the key-based format that
evaluate_benchmark.py expects.

Usage:
    python scripts/migrate_ground_truth.py
"""

from __future__ import annotations

import json
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "benchmark_results" / "ground_truth_analysis.json"
DST = Path(__file__).resolve().parent.parent / "benchmark_results" / "ground_truth_labels.json"


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    labels = []
    for c in data.get("classifications", []):
        key = f"{c['repo']}::{c['title']}"
        labels.append({"key": key, "label": c["label"], "signal": c["signal"]})
    DST.write_text(json.dumps(labels, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Migrated {len(labels)} labels → {DST}")


if __name__ == "__main__":
    main()

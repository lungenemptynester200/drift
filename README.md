# Drift — Codebase Coherence Analyzer

**Detect architectural erosion from AI-generated code.**

Drift is a static analysis tool that measures how well a codebase maintains its architectural coherence over time — particularly as AI code-generation tools (Copilot, Cursor, ChatGPT) introduce code that solves local tasks correctly but weakens global design consistency.

## The Problem

AI coding assistants optimize for the _prompt context_, not the _codebase context_. The result: code that works but doesn't fit. Error handling fragments across 4 different patterns. Import boundaries erode. Near-duplicate functions accumulate. The codebase gradually loses the implicit contracts that made it maintainable.

**Drift doesn't detect bugs. It detects the loss of design intent.**

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Analyze a repository
drift analyze --repo /path/to/your/project

# CI check (exit code 1 if findings exceed threshold)
drift check --fail-on high

# Show pattern catalog
drift patterns

# JSON output for downstream tooling
drift analyze --format json
```

## pre-commit Hook

Add drift as a [pre-commit](https://pre-commit.com) hook so it runs before every commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/sauremilk/drift
    rev: v1
    hooks:
      - id: drift-check
        args: [--fail-on, high]
```

## GitHub Action

Add drift to any repository's CI pipeline in seconds:

```yaml
# .github/workflows/drift.yml
name: Drift

on: [push, pull_request]

jobs:
  drift:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write # required for upload-sarif

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # full git history for temporal signals

      - uses: sauremilk/drift@v1
        with:
          fail-on: high # exit 1 on high/critical findings
          upload-sarif: "true" # inline annotations in GitHub Code Scanning
```

| Input           | Default | Description                                                                      |
| --------------- | ------- | -------------------------------------------------------------------------------- |
| `fail-on`       | `high`  | Minimum severity that fails the build: `critical` \| `high` \| `medium` \| `low` |
| `upload-sarif`  | `false` | Upload SARIF to GitHub Code Scanning (requires `security-events: write`)         |
| `since`         | `90`    | Days of git history for temporal signals                                         |
| `format`        | `rich`  | Terminal output: `rich` \| `json` \| `sarif`                                     |
| `config`        | —       | Path to `drift.yaml` config file                                                 |
| `drift-version` | latest  | pip version spec, e.g. `drift-analyzer==0.2.0`                                   |

A full example workflow is available at [`examples/drift-check.yml`](examples/drift-check.yml).

## What Drift Detects

Drift measures 6 active detection signals, each targeting a different dimension of architectural erosion:

| Signal                      | Code | What it detects                                                                                  |
| --------------------------- | ---- | ------------------------------------------------------------------------------------------------ |
| **Pattern Fragmentation**   | PFS  | Same category of pattern (e.g. error handling) implemented N different ways within one module    |
| **Architecture Violations** | AVS  | Imports that cross layer boundaries (DB → API) or create circular dependencies                   |
| **Mutant Duplicates**       | MDS  | Near-identical functions that diverge in subtle ways (copy-paste-then-modify)                    |
| **Explainability Deficit**  | EDS  | Complex functions lacking docstrings, tests, or type annotations — especially when AI-attributed |
| **Temporal Volatility**     | TVS  | Files with anomalous change frequency, author diversity, or defect correlation                   |
| **System Misalignment**     | SMS  | Recently introduced imports/patterns foreign to their target module                              |

> **Phase 2 (not active):** Doc-Implementation Drift (DIA) — documented architecture that no longer matches actual code. Included in the codebase but excluded from the default pipeline (weight 0.0).

### Composite Drift Score

Individual signal scores (0.0–1.0) are combined into a weighted **composite drift score**:

```
Score = Σ (signal_weight × signal_score) / Σ weights
```

Default weights:

```yaml
weights:
  pattern_fragmentation: 0.22
  architecture_violation: 0.22
  mutant_duplicate: 0.17
  temporal_volatility: 0.17
  explainability_deficit: 0.12
  system_misalignment: 0.10
  doc_impl_drift: 0.00 # Phase 2 — not active
```

## Configuration

Create a `drift.yaml` in your project root:

```yaml
# File patterns
include:
  - "**/*.py"
exclude:
  - "**/node_modules/**"
  - "**/__pycache__/**"
  - "**/venv/**"

# Signal weights (normalised internally — don't need to sum to 1.0)
weights:
  pattern_fragmentation: 0.22
  architecture_violation: 0.22
  mutant_duplicate: 0.17
  temporal_volatility: 0.17
  explainability_deficit: 0.12
  system_misalignment: 0.10
  doc_impl_drift: 0.00

# Detection thresholds
thresholds:
  high_complexity: 10
  medium_complexity: 5
  min_function_loc: 10
  similarity_threshold: 0.80
  recency_days: 14
  volatility_z_threshold: 1.5

# Architecture boundaries
policies:
  layer_boundaries:
    - name: "No DB imports in API layer"
      from: "api/**"
      deny_import: ["db.*", "models.*"]
    - name: "No API imports in DB layer"
      from: "db/**"
      deny_import: ["api.*", "routes.*"]

# CI severity gate
fail_on: high # critical | high | medium | low
```

## CLI Commands

### `drift analyze`

Full repository analysis with Rich terminal output. Includes **actionable recommendations** — concrete, rule-based suggestions for fixing detected drift (no LLM required).

```bash
drift analyze --repo . --since 90 --format rich
```

| Flag           | Default | Description                     |
| -------------- | ------- | ------------------------------- |
| `--repo, -r`   | `.`     | Repository path                 |
| `--path, -p`   | —       | Restrict to subdirectory        |
| `--since, -s`  | `90`    | Days of git history             |
| `--format, -f` | `rich`  | Output: `rich`, `json`, `sarif` |
| `--config, -c` | —       | Config file path                |

### `drift check`

CI-optimized: analyze changed files, exit code 1 if severity threshold exceeded.

```bash
drift check --diff HEAD~1 --fail-on high --format sarif
```

### `drift patterns`

Display the pattern catalog — all discovered code patterns grouped by category.

```bash
drift patterns --category error_handling
```

### `drift trend`

Show drift score evolution over time with an **ASCII trend chart** when ≥3 snapshots exist.

```bash
drift trend --last 90
```

### `drift timeline`

**Root-cause analysis** — identifies _when_ drift began per module and correlates it with AI-attributed commits. Shows clean periods, drift onset dates, trigger commits, and AI burst detection.

```bash
drift timeline --repo . --since 90
```

| Flag           | Default | Description      |
| -------------- | ------- | ---------------- |
| `--repo, -r`   | `.`     | Repository path  |
| `--since, -s`  | `90`    | Days of history  |
| `--config, -c` | —       | Config file path |

## Output Formats

**Rich (default):** Color-coded terminal dashboard with score bars, module rankings, and finding details.

**JSON:** Machine-readable output for dashboards and downstream tools.

**SARIF:** GitHub Code Scanning integration — findings appear as code annotations in PRs.

## Architecture

```
drift/
├── cli.py              # Click CLI entry point
├── analyzer.py         # Orchestrator: discovery → parse → signals → score
├── cache.py            # Parse result caching (SHA-256 keyed)
├── config.py           # drift.yaml configuration loading
├── models.py           # Core data models (dataclasses)
├── timeline.py         # Root-cause analysis: when & why drift began
├── recommendations.py  # Rule-based actionable fix suggestions
├── ingestion/
│   ├── ast_parser.py   # Python AST parsing (built-in ast module)
│   ├── file_discovery.py
│   └── git_history.py  # Git log parsing + AI attribution heuristics
├── signals/
│   ├── base.py         # BaseSignal ABC
│   ├── pattern_fragmentation.py
│   ├── architecture_violation.py
│   ├── mutant_duplicates.py
│   ├── explainability_deficit.py
│   ├── temporal_volatility.py
│   ├── system_misalignment.py
│   └── doc_impl_drift.py  # Phase 2 stub
├── scoring/
│   └── engine.py       # Weighted composite scoring
└── output/
    ├── rich_output.py  # Terminal dashboard + timeline + trend chart
    └── json_output.py  # JSON + SARIF
```

### Key Design Decisions

1. **Deterministic core.** No LLM in the detection pipeline. All signals use AST analysis, graph algorithms, and statistical methods. Reproducible, fast, auditable.

2. **Python `ast` module for Python files.** Zero-dependency parsing, always available, simpler than tree-sitter for Python-only analysis. TypeScript support planned via optional tree-sitter dependency (Phase 2).

3. **Signal architecture.** Each signal is an independent analyzer implementing `BaseSignal`. Signals are composed, not chained — they run on the same parsed data.

4. **Fingerprint-based pattern matching.** Error handling, API endpoints, and other patterns are reduced to structural fingerprints (JSON dicts). Grouping and variant counting happens on these fingerprints, not source text.

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run with verbose output
pytest -v

# Analyze drift's own codebase
drift analyze --repo .
```

## Requirements

- Python 3.11+
- Git repository (for history analysis)

### Core Dependencies

- `click` — CLI framework
- `rich` — Terminal output
- `pyyaml` — Configuration
- `pydantic` — Config validation
- `gitpython` — Git history
- `networkx` — Import graph analysis

### Optional

- `tree-sitter` + `tree-sitter-typescript` — TypeScript/JSX support
- `sentence-transformers` + `faiss-cpu` — Embedding-based similarity (Phase 2)

## Roadmap

- **v0.1 (current):** 6 active detection signals, Python support, CLI + CI integration, parse caching, trend history with ASCII charts, timeline root-cause analysis, actionable recommendations
- **v0.2:** TypeScript support (tree-sitter), Doc-Impl Drift signal, embedding-based duplicate detection
- **v0.3:** IDE plugin (VS Code), ADR-to-code alignment, team dashboards
- **v0.4:** PR bot, auto-fix suggestions, historical drift tracking

## License

MIT

# Quick Start

## Analyze a Repository

```bash
drift analyze --repo /path/to/your/project
```

## CI Check

Exit with code 1 if findings exceed a severity threshold:

```bash
drift check --fail-on high
```

## Output Formats

```bash
# Rich terminal dashboard (default)
drift analyze --format rich

# Machine-readable JSON
drift analyze --format json

# GitHub Code Scanning (SARIF)
drift analyze --format sarif
```

## Self-Analysis Demo

Drift can analyze its own codebase — useful for verifying installation:

```bash
drift self
```

## Trend Tracking

Track drift score over time with ASCII charts:

```bash
drift trend --last 90
```

## Root-Cause Analysis

Identify when and why drift began per module:

```bash
drift timeline --repo . --since 90
```

# Drift — Codebase Coherence Analyzer

**Surface architectural drift patterns that often appear in fast-moving and AI-assisted codebases.**

Drift is a deterministic static analyzer for teams that want to catch architectural erosion before it becomes normal: fragmented patterns, boundary violations, near-duplicates, and unstable hotspots that accumulate when code is optimized for local delivery but not for global coherence.

## Start Here

```bash
pip install drift-analyzer
drift analyze --repo .
```

Recommended next steps:

- [Quick Start](getting-started/quickstart.md)
- [Team Rollout](getting-started/team-rollout.md)
- [Finding Triage](getting-started/finding-triage.md)

## What Drift Is Good At

- surfacing architecture and coherence issues that linters do not model
- complementing fast-moving or AI-assisted development with deterministic checks
- helping teams review hotspots, modules, and trends instead of isolated style violations

## What Drift Is Not

- not a bug finder
- not a security scanner
- not a type checker
- not a zero-false-positive oracle

## Trust Model

Drift earns trust through reproducible analysis, explicit methodology, and signal-by-signal interpretation.

- deterministic pipeline with no LLM in the core analysis path
- benchmark material and study artifacts kept in the repository
- guidance for gradual rollout instead of immediate hard gating
- clear limitations and interpretation notes in the docs

See [Benchmarking and Trust](benchmarking.md) for methodology, known limitations, and how to read findings conservatively.

## Documentation Map

- [Getting Started](getting-started/quickstart.md)
- [How It Works](algorithms/deep-dive.md)
- [Benchmarking and Trust](benchmarking.md)
- [Product Strategy](product-strategy.md)
- [Case Studies](case-studies/index.md)

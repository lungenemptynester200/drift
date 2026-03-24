# FAQ

## What is drift?

Drift is a deterministic static analyzer for architectural erosion and cross-file coherence problems in Python repositories.

## What does drift detect?

Drift detects six scoring signal families: pattern fragmentation, architecture violations, mutant duplicates, explainability deficit, temporal volatility, and system misalignment. DIA is visible as a report-only signal with weight 0.00.

See [Signal Reference](algorithms/signals.md).

## Is drift a bug finder or security scanner?

No. Drift is not positioned as a bug finder, a security scanner, or a type checker.

For those problems, use the dedicated tools already built for them.

## Why would a team use drift next to Ruff, Semgrep, or CodeQL?

Because those tools do not primarily model cross-file architectural coherence.

See [Drift vs Ruff](comparisons/drift-vs-ruff.md) and [Drift vs Semgrep and CodeQL](comparisons/drift-vs-semgrep-codeql.md).

## When should a team not use drift?

Avoid using drift as a first-day hard gate on tiny repositories or when the real need is bug detection, security review, or type-safety enforcement.

## How should a team introduce drift?

Start locally, then move to report-only CI, then gate only on `high` findings after reviewing real output.

See [Team Rollout](getting-started/team-rollout.md).

## Does drift use an LLM in the detector pipeline?

No. The detector path is deterministic.

See [Trust and Evidence](trust-evidence.md) and [Benchmarking and Trust](benchmarking.md).
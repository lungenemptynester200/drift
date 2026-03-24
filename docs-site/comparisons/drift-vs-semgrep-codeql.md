# Drift vs Semgrep and CodeQL

Semgrep, CodeQL, and drift are complementary.

Semgrep and CodeQL are strong at policy, security, and risky-flow detection. Drift is focused on deterministic architectural erosion and cross-file coherence.

## Short answer

Use Semgrep and CodeQL when you need to know whether code introduces a known bad pattern, vulnerability shape, or policy violation.

Use drift when you need to know whether the repository is slowly diverging from its own architectural patterns.

## Comparison

| Question | Semgrep / CodeQL | Drift |
|---|---|---|
| Security and risky flows | Yes | No |
| Policy violations | Yes | No |
| Cross-file architectural coherence | Limited, depending on rule design | Yes |
| Pattern fragmentation | No | Yes |
| Mutant duplicates | No | Yes |
| Layer-boundary erosion | Sometimes via custom rules | Yes, as a first-class signal |
| Composite architectural orientation score | No | Yes |

## Why teams combine them

These tools fail in different directions:

- Semgrep and CodeQL tell you whether code is dangerous or non-compliant.
- drift tells you whether the codebase is becoming harder to reason about structurally.

That makes them additive, not interchangeable.

## Good adoption sequence

1. Keep your existing security and policy checks.
2. Add drift in report-only mode.
3. Use drift findings to review hotspots that are not visible in security tooling.

## Where to go next

- [CI Architecture Checks with SARIF](../use-cases/ci-architecture-checks-sarif.md)
- [Trust and Evidence](../trust-evidence.md)
- [Case Studies](../case-studies/index.md)
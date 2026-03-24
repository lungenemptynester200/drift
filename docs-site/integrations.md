# Integrations

Drift is easiest to adopt when teams do not have to invent a workflow around it.

This page collects the current integration surfaces that make drift useful in local checks, CI, code scanning, and machine-readable review flows.

## GitHub Action

Drift ships a GitHub Action that supports report-only rollout, configurable severity gating, and SARIF upload for code scanning.

Use this when you want findings in pull requests before you enforce anything.

Key inputs:

- `fail-on`
- `since`
- `format`
- `config`
- `upload-sarif`

See [CI Architecture Checks with SARIF](use-cases/ci-architecture-checks-sarif.md) for rollout posture.

## CLI

The CLI is the fastest integration path for local analysis and simple automation.

Common entry points:

- `drift analyze --repo .`
- `drift check --fail-on none`
- `drift check --fail-on high`
- `drift analyze --format json`
- `drift analyze --format sarif`
- `drift trend --last 90`

See [Quick Start](getting-started/quickstart.md) for first-run guidance.

## SARIF and JSON outputs

Drift supports machine-readable outputs for review and automation:

- SARIF for GitHub code scanning and related workflows
- JSON for CI artifacts, downstream scripts, and historical comparison

See [API and Outputs](reference/api-outputs.md) for the documented surfaces.

## Python API

Teams that want to integrate drift programmatically can use the Python entry points already exposed by the project.

Current documented public analysis entry points include:

- `analyze_repo(...)`
- `analyze_diff(...)`

These are most useful when you want a custom orchestration layer without wrapping shell commands.

## Example workflow assets in the repository

- `action.yml` for the GitHub Action implementation
- `examples/drift-check.yml` for a ready-to-copy workflow
- `examples/demo-project/` for an intentionally drifted demo repository

## Recommended adoption order

1. CLI locally
2. report-only CI
3. SARIF visibility in pull requests
4. selective gating on `high`
5. deeper automation with JSON or Python API only where justified

## Related pages

- [Quick Start](getting-started/quickstart.md)
- [Team Rollout](getting-started/team-rollout.md)
- [CI Architecture Checks with SARIF](use-cases/ci-architecture-checks-sarif.md)
- [Trust and Evidence](trust-evidence.md)
# API and Outputs

Drift already exposes machine-consumable surfaces that are useful for automation, CI artifacts, and custom orchestration.

This page keeps the current surface area narrow and explicit.

## Python API entry points

The current analysis entry points are:

- `analyze_repo(repo_path, config=None, since_days=90, target_path=None, on_progress=None, workers=...)`
- `analyze_diff(repo_path, config=None, diff_ref="HEAD~1", workers=..., on_progress=None, since_days=90)`

Use these when you want to integrate drift as a library inside a Python workflow.

## When to prefer the Python API

Use the Python API when:

- you need direct access to structured analysis objects
- you want custom orchestration without shell parsing
- you want to embed drift inside a larger Python-based pipeline

Use the CLI when you only need stable commands in local or CI workflows.

## JSON output

`drift analyze --format json` serializes repository-level results into a structured payload that includes:

- version and repository path
- analyzed timestamp
- drift score and severity
- trend information when available
- summary counters
- module scores
- findings
- suppressed and context-tagged counts

This is the best current format for CI artifacts, snapshot comparison, and downstream scripts.

## SARIF output

`drift analyze --format sarif` exports findings in SARIF 2.1.0 format.

Use SARIF when you want findings to flow into code scanning or tooling that already understands SARIF as a review surface.

Drift includes:

- rule IDs per signal
- severity mapping to SARIF levels
- primary locations and related locations
- optional fix text in result messages
- context properties for tagged findings
- trend properties when available

## Current practical boundary

Drift does not currently document a public HTTP API or OpenAPI surface.

That is intentional. The current machine-consumable contract is the CLI, JSON output, SARIF output, and the Python analysis entry points.

## Best uses today

- save JSON outputs as CI artifacts for historical comparison
- upload SARIF to GitHub code scanning
- call the Python API from internal tooling when you need direct object access

## Related pages

- [Integrations](../integrations.md)
- [CI Architecture Checks with SARIF](../use-cases/ci-architecture-checks-sarif.md)
- [Trust and Evidence](../trust-evidence.md)
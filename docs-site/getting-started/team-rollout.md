# Team Rollout

This guide is optimized for small teams first.

The goal is not to turn drift into a hard gate on day one. The goal is to build trust, identify high-value findings, and only then tighten enforcement.

## Recommended rollout path

### Phase 1: Local exploration

Start locally and inspect the top findings before any CI policy change.

```bash
drift analyze --repo .
```

What to look for:

- repeated patterns inside one module
- findings that clearly point to architectural boundaries
- clusters with multiple supporting locations

Avoid tuning configuration before you have seen a few real results.

### Phase 2: CI visibility without blocking

Add drift to CI, but use it as a reporting signal first.

Recommended posture:

- publish rich or JSON output in CI artifacts
- review findings in pull requests and weekly maintenance windows
- record which signals feel high-trust and which need tuning

### Phase 3: Block only high-confidence problems

Once the team understands the output, begin with a narrow gate:

```bash
drift check --fail-on high
```

Why `high` first:

- it minimizes team frustration
- it forces attention on the most structural issues
- it gives space to calibrate lower-severity findings later

### Phase 4: Tune by repo shape

Only after reviewing real findings should you adjust policies or weights.

Typical tuning decisions:

- reduce weight on a noisy signal for your repository shape
- add architecture boundary rules where layers are explicit
- exclude generated or vendor-like code that distorts the signal

## Safe default policy

For many teams, this is the least risky adoption path:

1. Run `drift analyze` locally.
2. Add CI reporting.
3. Gate on `high` only.
4. Review noise after two or three real pull requests.
5. Tighten config only where evidence justifies it.

## How to avoid false-positive fatigue

- do not start with `medium` or `low` gates
- treat the first scans as calibration, not judgment
- prefer patterns with multiple corroborating locations over isolated weak signals
- document team-specific exclusions instead of arguing with every individual finding

## Suggested team policy

Use drift when:

- reviewing fast-moving modules
- integrating AI-assisted coding into an existing architecture
- checking whether new code matches established patterns

Do not rely on drift alone when:

- validating correctness
- enforcing security requirements
- replacing architectural review on critical changes

## Next steps

- [Finding Triage](finding-triage.md)
- [Configuration](configuration.md)
- [Benchmarking and Trust](../benchmarking.md)
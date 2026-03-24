# Benchmarking and Trust

Drift should be evaluated the same way teams evaluate any structural analyzer: conservatively, per signal, and with clear awareness of limitations.

## Trust model

Drift is designed to maximize reproducibility and technical traceability:

- deterministic analysis pipeline
- no LLMs in the core detector path
- documented benchmark artifacts in the repository
- raw study material available for inspection

This makes drift easier to audit than tools that rely on opaque model inference, but it does not eliminate the need for careful interpretation.

## How to read benchmark claims

Use benchmark numbers as evidence of maturity, not as proof that every finding in every repository is equally reliable.

Interpret results at three levels:

1. overall methodology
2. per-signal behavior
3. fit for your repository shape

The strongest posture is: trust the deterministic process, then calibrate signal trust on your own repository.

## Recommended evaluation questions

Before enabling hard gates, ask:

1. Which signals are consistently useful in our codebase?
2. Which signals create the clearest next action?
3. Which findings have enough supporting locations to justify intervention?
4. Which parts of our repository are generated, exceptional, or intentionally mixed-layer?

## Known limitations

Current limitations to communicate explicitly:

- not every signal is equally mature in every repository shape
- small repositories can feel noisy if teams expect strict, bug-finder-like precision
- temporal signals depend on repository history quality and clone depth
- the composite score is orientation, not a substitute for reviewing the signal breakdown

## Practical trust guidance

The most credible way to adopt drift is:

1. start with report-only usage
2. review findings per signal
3. gate only on the clearest high-severity cases
4. tune based on recurring evidence

## Where the detailed evidence lives

For full methodology, raw study framing, and benchmark details, see:

- [Study](study.md)
- [Case Studies](case-studies/index.md)
- [Algorithm Deep Dive](algorithms/deep-dive.md)

## What this page intentionally avoids

This page does not present a single headline metric as the product story.

That is deliberate.

For adoption, the critical question is not only "How good is drift overall?" but also "Which signals can we trust enough to act on today?"
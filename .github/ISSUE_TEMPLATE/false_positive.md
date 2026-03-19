---
name: "False Positive / False Negative"
about: "Drift is flagging something incorrectly, or missing a real issue"
title: "[FP/FN] "
labels: ["signal-quality"]
assignees: []
---

## Signal affected

<!-- Which signal produced the false result? -->
- [ ] Pattern Fragmentation (PFS)
- [ ] Architecture Violations (AVS)
- [ ] Mutant Duplicates (MDS)
- [ ] Explainability Deficit (EDS)
- [ ] Temporal Volatility (TVS)
- [ ] System Misalignment (SMS)

## False positive or false negative?

- [ ] False positive — drift flagged something that isn't a real issue
- [ ] False negative — drift missed something that is a real issue

## Code example

```python
# Paste the relevant code snippet here
```

## Why this is incorrect

Explain why drift's assessment is wrong in this case.

## drift.yaml config (if any)

```yaml
```

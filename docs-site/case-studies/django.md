# Case Study: Django — 10 Years of Structural Stability

**Repository:** [django/django](https://github.com/django/django)
**Releases Analyzed:** 17 (Django 1.8 → 6.0, spanning 10 years)
**Drift Score Range:** 0.535–0.563 (σ=0.004)

## Key Finding: Score Tracks Coherence, Not Size

Django's drift score plateaued at 0.553–0.563 across Django 2.0→5.2. Then it **dropped by 0.016 at Django 6.0** — correlating with 116 deprecation-removal commits that cleaned up legacy debt.

This confirms a critical property of the drift score: it measures **structural coherence**, not codebase size. Django grew significantly over this period, but its architecture remained consistent — until an intentional cleanup caused the score to improve.

## Temporal Stability

Consecutive commits show minimal score variation:

- **django:** σ=0.004 over 20 commits (range 0.535–0.546)
- **drift (self):** σ=0.012 over 10 commits (range 0.439–0.475)

This stability means the score is meaningful for trend tracking — a sudden change signals a real architectural shift, not noise.

## Interpretation

**Track trends, not absolute numbers.** A stable score means consistent architecture. A sudden drop after intentional cleanup means the tool is calibrated correctly. A gradual increase signals accumulating erosion.

Full analysis with score curves across all 17 releases: [STUDY.md §11.7](../study.md).

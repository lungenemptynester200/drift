# Drift — Codebase Coherence Analyzer

**Detect architectural erosion from AI-generated code.**

Drift is a static analysis tool that measures how well a codebase maintains its architectural coherence over time — particularly as AI code-generation tools (Copilot, Cursor, ChatGPT) introduce code that solves local tasks correctly but weakens global design consistency.

## Why Drift?

AI coding assistants optimize for the _prompt context_, not the _codebase context_. The result: code that works but doesn't fit. Error handling fragments across 4 different patterns. Import boundaries erode. Near-duplicate functions accumulate.

**Drift doesn't detect bugs. It detects the loss of design intent.**

## Quick Start

```bash
pip install drift-analyzer
drift analyze --repo /path/to/your/project
```

## Key Features

- **6 detection signals** covering pattern fragmentation, architecture violations, near-duplicates, explainability gaps, temporal volatility, and system misalignment
- **Deterministic analysis** — no LLM in the detection pipeline, fully reproducible
- **CI/CD integration** — GitHub Action, pre-commit hook, SARIF output
- **Sub-second to minutes** — parallel pipeline with caching, <5s for 500-file repos
- **Python + TypeScript** support (TypeScript via tree-sitter)

## Measured Results

| Repository | Drift Score | Findings | Time |
|---|---|---|---|
| FastAPI (1,118 files) | 0.690 HIGH | 661 | 2.3s |
| Pydantic (403 files) | 0.577 MEDIUM | 283 | 57.9s |
| httpx (60 files) | 0.472 MEDIUM | 46 | 3.3s |

80% precision, 86% recall on controlled benchmarks. [Full methodology →](study.md)

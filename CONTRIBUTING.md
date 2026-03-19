# Contributing to Drift

Thanks for your interest in contributing! Drift is under active development and welcomes bug fixes, new signals, and documentation improvements.

## Quick start

```bash
git clone https://github.com/sauremilk/drift.git
cd drift
pip install -e ".[dev]"
pytest
```

## What to work on

Check the [open issues](https://github.com/sauremilk/drift/issues) — issues labelled **`good first issue`** are a good entry point.

High-value contributions:
- **New detection signals** — see `src/drift/signals/base.py` for the interface
- **TypeScript support** — tree-sitter integration (see roadmap in README)
- **False positive fixes** — signal quality improvements are always welcome
- **Documentation** — usage examples, configuration how-tos

## Adding a new signal

1. Create `src/drift/signals/your_signal.py` implementing `BaseSignal`
2. Register it in `src/drift/analyzer.py`
3. Add a weight entry in `src/drift/config.py` (default `0.0` until stable)
4. Write tests in `tests/signals/test_your_signal.py`

Signals must be:
- **Deterministic** — same input always produces same output
- **LLM-free** — the core pipeline uses only AST analysis and statistics
- **Fast** — target < 500ms per 1 000 functions

## Code conventions

- Python 3.11+, type annotations everywhere
- `ruff check src/ tests/` must pass
- `pytest` must pass

## Submitting a PR

1. Open an issue first for non-trivial changes (saves everyone time)
2. Keep PRs focused — one concern per PR
3. Add tests for new behaviour
4. Update the README if you add a feature

## Reporting issues

Use the [issue templates](.github/ISSUE_TEMPLATE/) — they help reproduce problems quickly.

## License

By contributing you agree that your contributions will be licensed under the [MIT License](LICENSE).

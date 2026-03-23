# Installation

## From PyPI

```bash
pip install drift-analyzer
```

## From Source

```bash
git clone https://github.com/sauremilk/drift.git
cd drift
pip install -e ".[dev]"
```

## Optional Extras

```bash
# TypeScript/TSX support
pip install drift-analyzer[typescript]

# Embedding-based duplicate detection
pip install drift-analyzer[embeddings]

# All extras
pip install drift-analyzer[all]
```

## Requirements

- Python 3.11+
- Git (for history-based signals)

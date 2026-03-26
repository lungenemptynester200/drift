# Consistency Proxy Validation — 2026-03-26

## Scope

Validation artifact for the local feature push that includes:

- consistency proxy signal changes (`BEM`, `TPD`, `GCD`)
- DIA documentation/filter regressions
- BEM boundary-decorator false-positive fix

## Commands

Targeted regression after the BEM fix:

```bash
python -m pytest tests/test_precision_recall.py -k "bem_decorator_boundary_tn" tests/test_dia_enhanced.py -q --tb=short
```

Result:

- 1 passed
- 66 deselected
- 0 failed

Relevant feature-evidence test run:

```bash
python -m pytest tests/test_dia_enhanced.py tests/test_consistency_proxies.py tests/test_precision_recall.py -q --tb=short
```

Result:

- 93 passed
- 1 warning (`pytest_asyncio` deprecation warning)
- 0 failed

## Notes

- Added DIA regression coverage for noise-like path fragments such as `TypeScript`, `auth`, `db`, `8000`, `Basic`, and `Key`.
- Confirmed legitimate directory-like tokens such as `drift`, `ingestion`, `models`, `node_modules`, and `linters` still pass through the DIA filter.
- Fixed BEM module-level boundary detection so empty `__init__.py` files do not suppress decorator-based boundary recognition.
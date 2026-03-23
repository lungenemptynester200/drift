# Case Study: Pydantic

**Repository:** [pydantic/pydantic](https://github.com/pydantic/pydantic)
**Stats:** 403 files, 8,384 functions
**Drift Score:** 0.577 (MEDIUM) | **Time:** 57.9s

## Key Findings

### 117 Underdocumented Internal Functions (EDS)

Pydantic's `_internal/` package contains highly complex validation logic (cyclomatic complexity >15) with minimal docstrings. The Explainability Deficit Signal flags these as high-risk for maintainability.

This is understandable for internal code — but it creates a "bus factor" problem when contributors need to modify validation internals.

## Interpretation

Drift doesn't flag all undocumented functions — only those with high complexity that lack any of: docstrings, tests, or type annotations. The EDS signal targets the intersection of complexity and opacity.

**Recommendation:** Targeted docstrings for the 20 highest-complexity internal functions would significantly reduce the EDS score and improve contributor onboarding.

---
applyTo: "src/drift/**"
description: "Releases are automated via python-semantic-release in CI. Agents must use conventional commits (feat:/fix:/BREAKING:) — no manual release command needed."
---

# AUTOMATED RELEASE VIA PYTHON-SEMANTIC-RELEASE

## Rule: Use Conventional Commits — CI Handles the Rest

After any successful code change to `src/drift/`:

1. **Use conventional commit messages:**
   - `feat: ...` → MINOR bump
   - `fix: ...` → PATCH bump
   - `BREAKING: ...` → MAJOR bump
2. Tests passed ✓
3. Code committed ✓
4. **After push to main:** `.github/workflows/release.yml` runs python-semantic-release automatically

## What CI Does Automatically

- Analyzes commits since last tag
- Calculates next version
- Updates pyproject.toml + CHANGELOG.md
- Creates release commit + tag + GitHub Release
- Builds and publishes to PyPI

## Local Fallback (only if CI is unavailable)

```
python scripts/release_automation.py --full-release
```

## See Also

- Release Workflow: `.github/workflows/release.yml`
- PSR Configuration: `pyproject.toml` → `[tool.semantic_release]`
- Detailed Skill: `.github/skills/drift-release/SKILL.md`

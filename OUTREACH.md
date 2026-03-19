# Outreach Texte

Fertige Texte zum Copy-Paste für externe Plattformen.
Reihenfolge = empfohlene Priorität.

---

## 1. Show HN (Hacker News)

**Titel:**

```
Show HN: Drift – Detect architectural erosion from AI-generated code
```

**Text (im Kommentarfeld):**

```
I built a static analyzer that measures how much AI-generated code erodes your
codebase architecture over time.

The problem: Copilot, Cursor, and ChatGPT optimize for the prompt context, not
the codebase context. The result is code that works but doesn't fit — error
handling fragments across 4 different patterns, import boundaries erode, and
near-identical functions accumulate with subtle differences.

Drift doesn't detect bugs. It detects the loss of design intent.

It runs 6 detection signals:
- Pattern Fragmentation: same pattern implemented N different ways in one module
- Architecture Violations: imports crossing layer boundaries (DB → API, etc.)
- Mutant Duplicates: near-identical functions that diverged after copy-paste
- Explainability Deficit: complex functions without docs/types/tests
- Temporal Volatility: files changed by too many hands too fast
- System Misalignment: recently introduced patterns foreign to their module

All signals are deterministic, LLM-free, fast. Uses Python's built-in `ast`
module, so there are zero dependencies on ML infrastructure.

CLI:  pip install drift-analyzer && drift analyze --repo .
CI:   uses: sauremilk/drift@v1  (GitHub Action)
Hook: pre-commit hook available

Repo: https://github.com/sauremilk/drift
```

**Posting-Tipps:**

- Bester Zeitpunkt: Montag–Dienstag, 9–11 Uhr US Eastern (= 15–17 Uhr DE)
- URL: https://news.ycombinator.com/submitlink?u=https://github.com/sauremilk/drift

---

## 2. Reddit r/Python

**Titel:**

```
I built drift – a static analyzer to measure how much AI code erodes your architecture
```

**Text:**

```
TL;DR: `pip install drift-analyzer && drift analyze --repo .`

Copilot and Cursor write code that solves local tasks correctly but weakens
global design. Drift measures this with 6 signals:

1. Pattern Fragmentation – same thing done N ways in one module
2. Architecture Violations – wrong-direction imports
3. Mutant Duplicates – near-identical functions (copy-paste-then-modify)
4. Explainability Deficit – complex functions without docs or types
5. Temporal Volatility – files changed by too many authors too fast
6. System Misalignment – patterns foreign to their target module

No LLMs in the detection pipeline. Pure AST analysis + statistics.
Outputs: rich terminal dashboard, JSON, or SARIF for GitHub Code Scanning.

GitHub: https://github.com/sauremilk/drift
```

**Subreddits (alle posten):**

- r/Python
- r/programming
- r/softwarearchitecture
- r/devops

---

## 3. awesome-static-analysis PR

**Repo:** https://github.com/analysis-tools-dev/static-analysis/pulls

**Datei:** `data/tools/python.yml` (oder ähnlich, je nach Repo-Struktur)

**Eintrag:**

```yaml
- name: drift
  categories: [code-quality, architecture]
  languages: [python]
  description: >
    Detect architectural erosion from AI-generated code.
    Measures pattern fragmentation, architecture violations, mutant duplicates,
    explainability deficit, temporal volatility, and system misalignment.
  homepage: https://github.com/sauremilk/drift
  license: MIT
```

**PR-Titel:** `Add drift – architectural erosion detector for AI-generated code`

---

## 4. awesome-python PR

**Repo:** https://github.com/vinta/awesome-python/pulls

**Abschnitt:** `Code Analysis`

**Eintrag:**

```
* [drift](https://github.com/sauremilk/drift) - Detect architectural erosion from AI-generated code.
```

**PR-Titel:** `Add drift to Code Analysis section`

---

## 5. PyPI Publishing (einmalig)

```bash
# 1. Trusted Publisher auf PyPI konfigurieren:
#    https://pypi.org/manage/account/publishing/
#    GitHub repo: sauremilk/drift
#    Workflow: publish.yml
#    Environment: pypi

# 2. Dann einfach einen neuen GitHub Release erstellen:
gh release create v1.1.0 --title "v1.1.0" --generate-notes
# → GitHub Action publish.yml baut und pushed automatisch zu PyPI
```

---

## 6. pre-commit.ci (automatische Indexierung)

Nach dem Pushen von `.pre-commit-hooks.yaml` wird drift automatisch auf
https://pre-commit.ci indexiert. Kein weiterer Schritt nötig.

Das Icon erscheint dann auf der pre-commit.ci-Seite und in deren Suchfunktion.

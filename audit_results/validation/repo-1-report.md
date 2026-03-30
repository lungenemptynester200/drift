# Repo 1 — marshmallow-code/marshmallow

**Validation Engineer Report**  
**Datum:** 2026-03-30  
**Drift-Version:** 1.1.4  

## Kurzbeschreibung

Marshmallow ist eine Serialization/Deserialization-Bibliothek für Python mit ~5k LOC.
Flache, saubere Architektur mit Schema/Fields/Decorators-Kern.

## Analyseergebnisse

| Metrik | Wert |
|--------|------|
| Drift-Score | 0.334 |
| Severity | low |
| Findings gesamt | 63 |
| CI-Check (`--fail-on high`) | ✅ PASS |

### Verteilung nach Signal

| Signal | Anzahl |
|--------|--------|
| doc_impl_drift | 15 |
| dead_code_accumulation | 13 |
| explainability_deficit | 9 |
| architecture_violation | 6 |
| naming_contract_violation | 5 |
| mutant_duplicate | 4 |
| cohesion_deficit | 3 |
| temporal_volatility | 2 |
| cognitive_complexity | 2 |
| fan_out_explosion | 2 |
| pattern_fragmentation | 1 |
| co_change_coupling | 1 |

### Verteilung nach Severity

| Severity | Anzahl |
|----------|--------|
| high | 19 |
| medium | 22 |
| low | 19 |
| info | 3 |

## Top 10 Findings

| # | Severity | Signal | Title | File | Impact |
|---|----------|--------|-------|------|--------|
| 1 | high | PFS | error_handling: 32 variants in src/marshmallow/ | src/marshmallow | 0.719 |
| 2 | high | MDS | Exact duplicates: IP._serialize, IPInterface._serialize | fields.py:1783 | 0.198 |
| 3 | high | MDS | Exact duplicates: NestedSchema test methods | test_decorators.py:877 | 0.198 |
| 4 | high | MDS | Exact duplicates: MySchema.handle_error | test_schema.py:1666 | 0.198 |
| 5 | medium | AVS | Hidden coupling: fields.py ↔ test_deserialization.py | fields.py | 0.127 |
| 6 | high | AVS | God module candidate: base.py | tests/base.py | 0.114 |
| 7 | high | TVS | High volatility: fields.py [AI] | fields.py | 0.107 |
| 8 | high | TVS | High volatility: test_deserialization.py [AI] | test_deserialization.py | 0.097 |
| 9 | medium | EDS | Unexplained complexity: Schema._invoke_field_validators | schema.py:1125 | 0.059 |
| 10 | medium | COD | Cohesion deficit: utils.py | utils.py | 0.008 |

## Manuelle Stichproben-Verifikation

### ✅ Korrekt: MDS — IP._serialize / IPInterface._serialize (Finding #2)
Verifiziert: Beide Methoden haben identische AST-Struktur (Zeilen 1783-1788 vs 1845-1850). Legitimer Duplikat-Fund.

### ❌ False Positive: DIA — README references missing directories (Findings #28-39)
12 von 15 doc_impl_drift-Findings sind False Positives. Die „fehlenden Verzeichnisse" (ODM/, ORM/, assets/, github/, latest/ etc.) sind URL-Pfadsegmente in Badge-Links und beschreibendem Text, keine tatsächlichen Verzeichnis-Referenzen.

### ⚠️ Fragwürdig: NBV — Naming Contract Violations (Findings #23-27)
Funktionen wie `is_generator()`, `is_iterable_but_not_string()` folgen Standard-Python-TypeGuard-Konventionen. Die Namen beschreiben exakt, was die Funktionen tun. Schwaches Signal.

### ✅ Korrekt: AVS — God module base.py (Finding #6)
tests/base.py aggregiert gemeinsame Testfixtures mit 7 transitiven Abhängigen. Strukturell nachvollziehbar.

## Stärken

- **MDS (Mutant Duplicates)** liefert klare, verifizierbare Treffer mit konkreten Zeilen
- **PFS (Pattern Fragmentation)** quantifiziert Error-Handling-Varianten sinnvoll
- **EDS (Explainability Deficit)** markiert korrekt komplexe, undokumentierte Methoden
- Score 0.334 (low) passt zur tatsächlichen Codequalität — gute Kalibrierung

## Schwächen

- **DIA (Doc-Impl Drift)** erzeugt massive False Positives bei URL-Pfaden in READMEs (~80% FP-Rate hier)
- **NBV (Naming Contract)** flaggt korrekt benannte TypeGuard-Funktionen
- **AVS-Duplikate**: Mehrere Findings erscheinen doppelt (God module #6 = #8, Hidden coupling #5 = #7)
- **DCA (Dead Code)**: 121 „unused exports" in fields.py — bei einer Library mit __all__-Export-Pattern naturgemäß FP

## Nützlichkeit für Agenten

**Mittel.** Die fix_first-Liste ist brauchbar, aber:
- Agent müsste DIA-FPs selbst filtern
- MDS-Findings liefern konkrete, automatisierbare Merge-Aufgaben
- DCA-Findings bei Libraries systematisch irrelevant

## Zwischenfazit

**Mittel** — Drift erkennt echte Probleme (Duplikate, Kohäsion), aber die DIA- und DCA-False-Positives bei Libraries senken die Precision deutlich.

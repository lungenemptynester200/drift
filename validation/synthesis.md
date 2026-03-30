# Drift v1.1.4 — Synthese, Entscheidungen & Umsetzungsplanung

**Datum:** 2026-03-30  
**Validierungsbasis:** 3 externe Python-Repos (marshmallow, scrapy, paramiko)  
**Scope:** 1.052 Findings, 30 manuell klassifiziert, 5 Agent-Readiness-Bewertungen  
**Fix-Status:** AVS-Dedup + MDS-Remediation behobene (v3 verifiziert)

---

## 1. Executive Summary

Drift v1.1.4 liefert **glaubwürdige architektonische Einsichten** bei realen Python-Repositories. Die Score-Kalibrierung differenziert zuverlässig zwischen sauberen (0.334), gewachsenen (0.477) und komplexen (0.586) Codebasen. Die fix_first-Priorisierung erreicht ~73% Precision in den Top-5 Findings.

**Zwei kritische Bugs wurden während der Validierung gefunden und behoben:**
- AVS-Finding-Duplikate (verursacht durch SignalCache → Cache-Version gebrannt, Dedup in `analyze()` hinzugefügt)
- MDS-Remediation-Platzhalter `?` (verursacht durch abweichendes Metadaten-Format bei exakten Duplikaten)

**Nach Fixes: Precision Top-5 steigt von ~73% auf geschätzt ~80%** (3 AVS-Duplikate eliminiert, MDS-Empfehlungen vollständig benannt).

**Verbleibende Schwäche:** DCA bei Libraries (90%+ FP), DIA-URL-Parsing (~40% FP), PFS-Redundanz über Verzeichnisebenen.

**Gesamtbewertung:** 🟡 GELB → 🟢 GRÜN bedingt erreichbar innerhalb von 14 Tagen.

---

## 2. Konsolidierte Ergebnisse

### Validierte Stärken

| Signal | Precision | Bewertung |
|--------|-----------|-----------|
| MDS (Mutant Duplicates) | ~100% | Zuverlässigstes Signal. Exakte Zeilennummern, sofort umsetzbar. |
| AVS (Architecture Violation) | ~80% (nach Dedup) | Strategischer Wert: God Modules, Zones of Pain, Circular Deps. |
| EDS (Explainability Deficit) | >80% | Atomare, klare Aufgaben. Voll agent-tauglich. |
| fix_first Priorisierung | ~73% Top-5 | Architektur-Findings korrekt über Style-Findings priorisiert. |
| Score-Kalibrierung | ✅ plausibel | marshmallow < paramiko < scrapy — differenziert korrekt. |

### Validierte Schwächen

| Signal | FP-Rate | Ursache | Impact |
|--------|---------|---------|--------|
| DCA (Bibliotheken) | >90% | `__all__`, Plugin-Patterns, String-Imports ignoriert | Größter Glaubwürdigkeits-Defekt |
| DIA (URL-Parsing) | ~40% | README-Badge-URLs als fehlende Verzeichnisse interpretiert | Rauschen ohne Erkenntniswert |
| PFS (Directory-Tiers) | redundant | Gleicher Befund auf 5+ Verzeichnisebenen | fix_first-Dominanz bei großen Repos |
| NBV (Domain-Code) | ~50% | RFC/Framework-Konventionen als Violations flagged | Schadet bei Protokoll-Bibliotheken |

### Behobene Bugs (verifiziert)

| Bug | Ursache | Fix | Verification |
|-----|---------|-----|--------------|
| AVS-Duplikate (6→3 bei marshmallow) | Kein Dedup vor Return + SignalCache serviert alte Results | Dedup in `analyze()` + `_SIGNAL_CACHE_VERSION` 1→2 | ✅ v3 marshmallow: 3 unique AVS |
| MDS `?`-Platzhalter | `_recommend_mutant_duplicate()` liest nur `function_a/b`, nicht `functions`-Liste | Conditional für `functions`-List-Format | ✅ v3: alle 55 MDS-Titel korrekt |

---

## 3. Cross-Repo-Bewertung

| | marshmallow | paramiko | scrapy |
|---|---|---|---|
| **Typ** | Bibliothek (sauber) | Protokoll-Impl (historisch) | Framework (komplex) |
| **LOC** | ~5k | ~15k | ~30k |
| **Score** | 0.334 (low) | 0.477 (medium) | 0.586 (medium) |
| **Findings** | 63 | 275 | 714 |
| **CI-Check** | PASS | PASS | FAIL |
| **Top-Signal** | MDS (Duplikate in fields.py) | EDS (71 undokumentiert) | PFS (89 Error-Handling-Varianten) |
| **Stärke** | Sauberer Code → wenig Rauschen | God-Module + Zone-of-Pain korrekt | Kreisabhängigkeiten korrekt erkannt |
| **Schwäche** | DCA/DIA FP | DCA bei Exports (90% FP) | Finding-Volume überwältigend |

**Kern-Einsicht:** Drift differenziert korrekt zwischen Repo-Typen. Die Score-Abstufung ist nicht nur numerisch, sondern inhaltlich plausibel: marshmallow hat wenige echte Probleme, scrapy hat viele strukturelle.

---

## 4. Signalqualität — Detailbewertung

### Tier 1: Produktionsreif

- **MDS** — Exakte und Near-Duplikate korrekt, AST-basiert, reproduzierbar. Empfehlung klar. Agent-tauglich.
- **EDS** — Komplexitäts-Dokumentation. Atomare Aufgaben, klare Lokation. Voll agent-tauglich.
- **AVS** (nach Dedup-Fix) — God Modules, Zones of Pain, Blast Radius. Strategisch wertvoll. Agent: teilweise (Cluster fehlen).

### Tier 2: Brauchbar mit Einschränkungen

- **PFS** — Quantifiziert reale Fragmentierung, aber redundant über Verzeichnisebenen. Braucht Dedup.
- **TVS** — Temporal Volatility korrekt, aber niedrige Trefferquote bei wenig Git-History.
- **COD** — Cohesion Deficit valide, aber selten in Top-Findings.

### Tier 3: Verbesserungsbedarf

- **DCA** — Systematisch unzuverlässig bei Bibliotheken. Braucht Library-Heuristik.
- **DIA** — URL-Parsing-Fehler. Braucht URL-Fragment-Filter.
- **NBV** — Domain-spezifische Namenskonventionen nicht berücksichtigt. Braucht Allowlist.

---

## 5. Entscheidung: Soft-Rollout

### ENTSCHEIDUNG: ✅ JA — Soft-Rollout als CI-Visibility starten

**Begründung:**
- fix_first-Precision >70% nach Fixes rechtfertigt Sichtbarkeit
- Kein Blocking-Gate, nur JSON-Artefakt + optionaler PR-Kommentar
- Risiko bei False Positives gering, da continue-on-error: true
- Feedback-Loop notwendig für DCA/DIA-Verbesserung

**Sofort-Empfehlung:**
```yaml
# Phase A: Visibility Only (ab sofort)
- name: Drift Analysis
  run: drift analyze --repo . --format json --output drift-report.json --compact --fail-on critical
  continue-on-error: true
- uses: actions/upload-artifact@v4
  with:
    name: drift-report
    path: drift-report.json
```

**Phase B** (PR-Kommentar) erst nach DCA-Library-Heuristik implementiert (geschätzt: Tag 8–10 im Roadmap).

---

## 6. Entscheidung: Hard-Gating

### ENTSCHEIDUNG: ❌ NEIN — Noch nicht

**Begründung:**
- FP-Rate 23% (Ziel: <15%)
- DCA bei Libraries noch nicht suppressiert
- Kein Team hat 4+ Wochen Soft-Rollout-Erfahrung
- Baseline für "nur neue Findings" fehlt

**Voraussetzungen für Hard-Gate:**
1. FP-Rate < 15%
2. DCA-Library-Mode existiert
3. 4+ Wochen Soft-Rollout-Erfahrung
4. Delta-Only Gate (`--baseline` Flag)

**Frühester Zeitpunkt:** 12–16 Wochen nach Soft-Rollout-Start.

---

## 7. Entscheidung: Case Study publizieren

### ENTSCHEIDUNG: ✅ JA — Paramiko Case Study publizieren (nach Edits)

**Begründung:**
- Paramiko zeigt Stärken (God Module, Zone of Pain, MDS) und Schwächen (DCA) ehrlich
- 20+ Jahre altes Repo = glaubwürdige Referenz
- 60% der Findings agent-tauglich ← gutes Narrativ
- Transport.py (3.456 Zeilen, 132 Funktionen) ist eingängiges Beispiel

**Edits vor Publikation:**
1. DCA-Kritik transparent erwähnen: "DCA erkennt Library-Exports noch nicht korrekt"
2. AVS-Duplikate-Bug als "behoben in v1.X" kennzeichnen
3. Emphasis auf fix_first-Qualität (konkrete Empfehlungen zeigen)

---

## 8. Entscheidung: Outreach jetzt starten

### ENTSCHEIDUNG: 🟡 BEDINGT — Outreach erst nach DCA-Library-Heuristik

**Begründung:**
- DCA-False-Positives sind der größte Glaubwürdigkeits-Defekt
- Ein Library-Maintainer, der Drift testet und 90% FP bei DCA sieht, wird es nicht weiterempfehlen
- AVS-Dedup + MDS-Fix sind bereits behoben
- **Nach DCA-Fix (geschätzt Tag 6–8):** Outreach an 2–3 ausgewählte Maintainer

**Reihenfolge:**
1. DCA-Library-Heuristik implementieren
2. Re-Validierung an marshmallow/paramiko
3. Case Study finalisieren
4. Outreach an marshmallow + paramiko Maintainer (personalisiert mit Findings)

---

## 9. Entscheidung: Nächster Fokus

### ENTSCHEIDUNG: DCA-Library-Heuristik → DIA-URL-Filter → PFS-Dedup

**Begründung (Policy §6: Glaubwürdigkeit > Signalpräzision > FP-Reduktion):**

| Rang | Aufgabe | Policy-Kriterium | Aufwand | Impact |
|------|---------|------------------|---------|--------|
| 1 | DCA Library-Heuristik | Glaubwürdigkeit | 2–3 Tage | Eliminiert >90% DCA-FP bei Libraries |
| 2 | DIA URL-Fragment-Filter | Signalpräzision | 1 Tag | Eliminiert ~40% DIA-FP |
| 3 | PFS Directory-Tier-Dedup | FP-Reduktion | 1–2 Tage | Reduziert fix_first-Dominanz |
| 4 | NBV Domain-Allowlist | Einführbarkeit | 1 Tag | Protokoll-Libraries besser bedient |

---

## 10. Priorisierter 14-Tage-Roadmap

### Woche 1 (Tag 1–7): Glaubwürdigkeit sichern

| Tag | Aufgabe | Erwartetes Ergebnis |
|-----|---------|---------------------|
| 1–2 | **Release v1.X** mit AVS-Dedup + MDS-Fix + Cache-Bump | Bugs in Produktion behoben |
| 3–4 | **DCA Library-Heuristik**: Erkennung via `pyproject.toml`/`setup.py` Classifier; Suppress DCA bei `__all__`-Exports | DCA-FP bei Libraries < 20% |
| 5 | **DIA URL-Fragment-Filter**: URL-Pattern-Regex vor Directory-Lookup | DIA-FP < 15% |
| 6 | **Tests + Re-Validierung** marshmallow + paramiko mit Fixes | Neue Precision-Zahlen |
| 7 | **Release v1.X+1** mit DCA+DIA Fixes | Bereit für Outreach |

### Woche 2 (Tag 8–14): Einführbarkeit vorbereiten

| Tag | Aufgabe | Erwartetes Ergebnis |
|-----|---------|---------------------|
| 8–9 | **PFS Directory-Tier-Dedup**: Nur tiefstes Finding behalten | fix_first-Qualität bei großen Repos verbessert |
| 10 | **CI Workflow-Template** finalisieren (Phase A) | Copy-paste-ready für beliebige Repos |
| 11 | **Case Study** paramiko finalisieren mit aktualisierten Zahlen | Publikationsreife Referenz |
| 12 | **NBV Domain-Allowlist** (optional, wenn Zeit) | Protokoll-Libraries besser bedient |
| 13 | **Outreach-Draft** an marshmallow + paramiko Maintainer | Personalisierte Drift-Reports als Gesprächsöffner |
| 14 | **Go/No-Go Re-Evaluation** mit neuen Precision-Zahlen | Erwartung: 🟢 GRÜN wenn FP < 15% |

---

## Nicht jetzt (Parking Lot)

Die folgenden Punkte wurden bewusst zurückgestellt:

| Item | Grund für Zurückstellung |
|------|-------------------------|
| Hard-Gating in CI | Frühestens Woche 12–16, FP-Rate noch zu hoch |
| SARIF-Upload für GitHub Code Scanning | Erst relevant in Phase C (Woche 9+) |
| AVS Cycle-Graph-Output | Nützlich aber Policy Phase 4 (Skalierung) |
| PFS Target-Pattern-Vorschlag | Forschungsaufgabe, kein klarer ROI |
| Dashboard/Badge-Integration | Komfort-Feature, Policy-nachrangig |
| Embedding-basierte Semantic-Duplikat-Erkennung | Qualitätsverbesserung, aber Tier-2-Signal |
| Delta-Only Gate (`--baseline`) | Braucht 4+ Wochen History-Daten |
| Multi-Language-Support | Phase 4, aktuell nur Python |

---

## Nächste 3 konkrete Schritte

### Schritt 1: Release mit Bugfixes (sofort)
```bash
python scripts/release_automation.py --full-release
```
Enthält: AVS-Dedup (`architecture_violation.py`), MDS-Remediation-Fix (`recommendations.py`), Cache-Version-Bump (`cache.py`).

### Schritt 2: DCA Library-Heuristik implementieren (Tag 3–4)
- In `src/drift/signals/dead_code_accumulation.py`: `pyproject.toml`-Classifier prüfen
- Bei Library-Typ: `__all__`-Exports + `__init__.py`-Re-Exports nicht als Dead Code flaggen
- Test: marshmallow DCA-Findings < 5 (aktuell: 13, davon >90% FP)

### Schritt 3: DIA URL-Fragment-Filter (Tag 5)
- In `src/drift/signals/doc_impl_drift.py`: URL-Pattern-Regex (`https?://`, `://`, `badge`) vor Directory-Lookup
- Test: marshmallow DIA-FP eliminiert (aktuell: ~6 von 15 sind URL-basierte FP)

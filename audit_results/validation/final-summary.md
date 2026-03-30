# Final Summary — Drift-Validierung v1.1.4

**Lead Report**  
**Datum:** 2026-03-30  
**Drift-Version:** 1.1.4  
**Validierungsumfang:** 3 externe Python-Repos, 1.052 Findings, 30 manuell bewertet

---

## 1. Executive Summary

Drift v1.1.4 wurde gegen drei externe Python-Repositories validiert (marshmallow, scrapy, paramiko). Die Ergebnisse zeigen: **drift erkennt reale architektonische Probleme**, insbesondere bei historisch gewachsenem Code. Die Signalqualität ist im oberen Finding-Bereich gut (Precision ~73% für Top-5), fällt aber im Long Tail deutlich ab (~47% insgesamt). Systematische Schwächen bei Library/Framework-Repos (DCA, DIA) und Finding-Duplikate (AVS) senken die Glaubwürdigkeit bei Erstnutzern.

**Empfehlung:** Bedingt Go für kontrollierte Soft-Rollouts. Drei klar benennbare Blocker vor öffentlichem Outreach.

---

## 2. Auswahl der Repositories

| Repo | Typ | LOC | Score | Severity | Findings |
|------|-----|-----|-------|----------|----------|
| marshmallow | Bibliothek (klein) | ~5k | 0.334 | low | 63 |
| scrapy | Framework (mittel) | ~30k | 0.586 | medium | 714 |
| paramiko | Protocol-Impl. (historisch) | ~15k | 0.477 | medium | 275 |

Die Auswahl deckt drei Architekturmuster ab: flach/sauber, layered/komplex, monolithisch/gewachsen. Kein Repo war in vorherigen Benchmarks enthalten.

---

## 3. Wichtigste Validierungsergebnisse

### Was gut funktioniert:
- **Score-Kalibrierung** ist plausibel: marshmallow (sauber) < paramiko (gewachsen) < scrapy (komplex)
- **MDS (Mutant Duplicates)** findet reale Code-Duplikate mit exakten Zeilenangaben — zuverlässigstes Signal
- **AVS (Architecture Violation)** liefert strategisch wertvolle Insights: God modules, Zones of Pain, Circular deps
- **fix_first-Priorisierung** funktioniert: höchstpriorierten Findings haben bessere Precision
- **CI-Check-Ergebnis** passt zu erwarteter Codequalität

### Was nicht funktioniert:
- **DCA bei Libraries**: 90%+ False Positives (Library-Exports werden als Dead Code gewertet)
- **DIA bei URL-Pfaden**: README-Links werden als fehlende Verzeichnisse misinterpretiert
- **AVS-Duplikate**: Identische Findings erscheinen doppelt
- **PFS-Redundanz**: Gleicher Befund auf 5+ Verzeichnisebenen
- **Finding-Volumen**: 714 Findings bei scrapy — für Erstgespräch nicht handhabbar

---

## 4. Signalqualität und Precision

| Metrik | Wert |
|--------|------|
| Precision (insgesamt) | 63% (19/30 korrekt) |
| Precision (korrekt & hilfreich) | 47% (14/30) |
| Precision (Top-5 pro Repo) | ~73% (11/15) |
| Bestes Signal | MDS (~100% Precision) |
| Zweitbestes Signal | AVS (~80% Precision ohne Duplikate) |
| Schwächste Signale | DCA (<20% bei Libraries), DIA (~40% FP), NBV (~50% bei Domänencode) |

**Tendenz:** Precision ist stark Impact-abhängig. fix_first ist signifikant besser als der Long Tail.

---

## 5. Agent-Tauglichkeit

| Finding-Typ | Agent-ready? | Stärke |
|-------------|-------------|--------|
| MDS (Duplicates) | ✅ Ja | Konkrete Lokation, atomare Aktion |
| EDS (Explainability) | ✅ Ja | Docstring-Generierung ist ideal |
| AVS (God modules) | ⚠️ Bedingt | Richtung klar, Cluster fehlen |
| AVS (Circular deps) | ❌ Nein | Zu komplex für autonome Auflösung |
| PFS (Fragmentation) | ❌ Nein | Kein Zielpattern, zu abstrakt |

**Kernproblem:** Remediation-Felder enthalten Platzhalter ('?') statt Symbolnamen. Zweite Duplikat-Stelle fehlt bei MDS. Systemische Findings (Circular deps, PFS) sind nicht als „strategisch" vs. „sofort umsetzbar" unterschieden.

---

## 6. CI-Soft-Rollout-Empfehlung

Drei-Phasen-Rollout empfohlen:

| Phase | Zeitraum | Modus | Gate |
|-------|----------|-------|------|
| A: Visibility | Woche 1–4 | Artefakt-Upload, kein Kommentar | `continue-on-error: true` |
| B: PR-Kommentar | Woche 5–8 | Top-5 fix_first im PR | `continue-on-error: true` |
| C: Soft Gate | Woche 9–12 | Warning bei Score > 0.7 | Warning, kein Block |

Hard-Gate frühestens nach 12–16 Wochen und nur mit bereinigten FP-Raten.

---

## 7. Kernaussagen der Case Study (paramiko)

- transport.py (3.456 Zeilen, 132 Funktionen) als God Module korrekt erkannt
- Zone-of-Pain-Analyse (ssh_exception.py: I=0.04, D=0.96) liefert strategisch wertvolle Metriken
- MDS-Findings in Kex-Modulen sind sofort umsetzbar
- DCA ist bei Protocol-Libraries systematisch unzuverlässig
- ~60% der Findings sind agent-tauglich, 40% erfordern menschliche Architekturentscheidung

---

## 8. Go/No-Go für Outreach

### 🟡 BEDINGT GO

**Go für:**
- Kontrollierte Soft-Rollouts in 2–3 befreundeten Teams
- Application-Repos (nicht Libraries/Frameworks)
- Agent-Workflows mit MDS/EDS-Fokus

**No-Go für:**
- Öffentlicher Launch
- Library-Repos als Showcase
- Hard-Gate-Empfehlungen

**Upgrade zu 🟢 GRÜN wenn:**
1. DCA-Library-Heuristik implementiert
2. AVS-Finding-Deduplizierung implementiert
3. Remediation-Platzhalter ('?') durch echte Symbolnamen ersetzt
4. Precision bei erneuter Validierung > 70%

---

## 9. Offene Risiken

| # | Risiko | Schwere | Status |
|---|--------|---------|--------|
| 1 | DCA-FPs bei Libraries → Glaubwürdigkeitsverlust | Hoch | Offen — Blocker |
| 2 | AVS-Duplikate → überhöhtes Problemvolumen | Mittel | Offen — Blocker |
| 3 | Remediation-Platzhalter → schlechter Ersteindruck | Mittel | Offen — Blocker |
| 4 | DIA-URL-FPs bei READMEs | Mittel | Offen — nice-to-fix |
| 5 | PFS-Redundanz über Verzeichnisebenen | Mittel | Offen — nice-to-fix |
| 6 | 714 Findings bei großen Repos → Überforderung | Mittel | Gemildert durch --compact |
| 7 | NBV bei Domänencode (Krypto, Protocol) | Niedrig | Akzeptabel für v1 |

---

## 10. Nächste 3 konkrete Schritte

### Schritt 1: DCA-Library-Heuristik (Blocker)
- **Was:** Repos mit pyproject.toml/setup.py `packages`-Deklaration oder umfangreichen __init__.py-Re-Exports als Library erkennen
- **Effekt:** DCA-Findings in Library-Modulen supprimieren oder als „info" herabstufen
- **Erwartete Verbesserung:** Precision steigt um ~8–10 Prozentpunkte

### Schritt 2: AVS-Finding-Deduplizierung (Blocker)
- **Was:** Identische AVS-Findings (gleicher Titel, gleiche Datei) vor Ausgabe zusammenführen
- **Effekt:** Finding-Volumen sinkt um ~15–20%, kein Informationsverlust
- **Erwartete Verbesserung:** Glaubwürdigkeit bei Erstnutzern steigt deutlich

### Schritt 3: MDS-Remediation-Qualität (Blocker)
- **Was:** Platzhalter '?' in Remediation durch tatsächliche Symbolnamen und zweite Lokation ersetzen
- **Effekt:** MDS wird vollständig agent-tauglich
- **Erwartete Verbesserung:** Agent-Usability für das zuverlässigste Signal wird 100%

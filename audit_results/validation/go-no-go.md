# Go/No-Go — Outreach-Bereitschaft

**Rollout Analyst Report**  
**Datum:** 2026-03-30  
**Basiert auf:** Validierung von 3 Repos, 30 manuell bewertete Findings

---

## Status: 🟡 GELB — Bedingt bereit

---

## Entscheidungsgrundlage

### Signalqualität

| Metrik | Wert | Bewertung |
|--------|------|-----------|
| Precision (gesamt) | 63% (19/30) | ⚠️ Unter 70%-Zielwert |
| Precision (korrekt & hilfreich) | 47% (14/30) | ⚠️ Unter 50% |
| Precision Top-5 pro Repo | ~73% (11/15) | ✅ Akzeptabel |
| fix_first-Qualität | Gut | ✅ Priorisierung funktioniert |
| MDS-Precision | ~100% | ✅ Zuverlässigstes Signal |
| AVS-Precision (ohne Duplikate) | ~80% | ✅ Wertvollstes Signal |
| DCA/DIA-Precision bei Libraries | <20% | ❌ Systematische Schwäche |

### Agent-Tauglichkeit

| Kategorie | Bewertung |
|-----------|-----------|
| MDS (Duplicates) | ✅ Agent-ready |
| EDS (Explainability) | ✅ Agent-ready |
| AVS (God modules) | ⚠️ Bedingt |
| AVS (Circular deps) | ❌ Nicht agent-ready |
| PFS (Fragmentation) | ❌ Nicht agent-ready |

### CI-Tauglichkeit

| Aspekt | Bewertung |
|--------|-----------|
| Soft-Rollout | ✅ Machbar |
| Hard-Gate | ❌ Noch nicht (FP-Rate zu hoch) |
| compact-Modus | ✅ Brauchbar |
| fix_first als PR-Kommentar | ✅ Funktional |

---

## Größte Risiken

| # | Risiko | Schwere | Wahrscheinlichkeit |
|---|--------|---------|-------------------|
| 1 | DCA/DIA-FPs bei Libraries → Glaubwürdigkeitsverlust bei Erstnutzern | Hoch | Hoch |
| 2 | AVS-Duplikate suggerieren doppeltes Problemvolumen | Mittel | Hoch |
| 3 | PFS-Redundanz über Verzeichnisebenen → Information Overload | Mittel | Hoch |
| 4 | Remediation-Platzhalter ('?') → schlechter Ersteindruck | Mittel | Mittel |
| 5 | 714 Findings bei scrapy-artigem Repo → Überforderung | Mittel | Mittel |

---

## Empfohlene nächste Phase

### Vor Outreach beheben (Blocker):

1. **DCA-Library-Heuristik**: Repos mit __init__.py-Re-Exports oder setup.py/pyproject.toml als Library erkennen → DCA-Findings supprimieren
2. **AVS-Deduplizierung**: Identische Findings (gleicher Titel, gleiche Datei) zusammenführen
3. **Remediation-Platzhalter ersetzen**: '?' durch echte Symbolnamen in MDS-Remediations

### Vor Outreach wünschenswert (nicht blockierend):

4. DIA: URL-Pfade in READMEs von Verzeichnis-Referenzen unterscheiden
5. PFS: Verzeichnisebenen-Deduplizierung (nur tiefstes Finding behalten)
6. NBV: Domänenspezifische Terminologie-Whitelist

---

## Klare Empfehlung

### 🟡 BEDINGT GO — mit Einschränkungen

**Go** für:
- Kontrollierter Soft-Rollout in 2–3 befreundeten Teams (keine öffentlichen Repos)
- Fokus auf Repos mit Application-Architektur (nicht Libraries/Frameworks)
- Agent-Workflow mit MDS/EDS-fokussierter Pipeline
- Case-Study-Kommunikation basierend auf paramiko

**No-Go** für:
- Öffentlicher Launch / ProductHunt / Social Media
- Hard-Gate-Empfehlungen in Dokumentation
- Library-Repos als Showcase (DCA-Problematik)
- „Zero-Config" Versprechen (FP-Rate erfordert Tuning)

### Bedingung für Upgrade zu 🟢 GRÜN:

Die 3 Blocker (DCA-Library-Heuristik, AVS-Dedup, Remediation-Platzhalter) sind behoben und eine erneute Validierung zeigt Precision >70% bei Top-Findings.

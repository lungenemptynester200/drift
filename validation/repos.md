# Validation — Repository-Auswahl

**Erstellt von:** Repo Scout  
**Datum:** 2026-03-30  
**Status:** Freigegeben durch Lead  

## Auswahlkriterien

- Nicht in bestehenden Benchmarks enthalten (celery, django, fastapi, flask, httpx, poetry, pydantic, requests, rich, sanic, sqlmodel, starlette, uvicorn)
- Öffentlich auf GitHub verfügbar
- Rein Python
- Diverse Architekturmuster und Größen
- Aktiv gepflegt (letzte Commits < 6 Monate)

## Ausgewählte Repositories

### Repo 1 — Klein: `marshmallow-code/marshmallow`

| Eigenschaft | Wert |
|------------|-------|
| URL | https://github.com/marshmallow-code/marshmallow |
| Typ | Bibliothek (Serialization/Deserialization) |
| Größe | ~5k Python LOC |
| Python-Version | 3.8+ |
| Architektur | Flach mit klarem Kern (Schema, Fields, Decorators) |

**Warum geeignet:**
- Kleines, fokussiertes Repo mit klarer API-Oberfläche
- Enthält Field-Hierarchien, die Pattern Fragmentation provozieren können
- Validierungslogik mit Guards und Exception-Handling
- Gut testbar als Baseline für niedrige Drift-Scores

**Risiken:**
- Möglicherweise zu sauber für interessante Findings
- Geringe Git-History-Tiefe pro Modul

---

### Repo 2 — Mittel: `scrapy/scrapy`

| Eigenschaft | Wert |
|------------|-------|
| URL | https://github.com/scrapy/scrapy |
| Typ | Framework (Web Scraping) |
| Größe | ~30k Python LOC |
| Python-Version | 3.8+ |
| Architektur | Layered: Core → Spiders → Middleware → Pipelines → Extensions |

**Warum geeignet:**
- Klare Schichtarchitektur — ideale Testgrundlage für AVS (Architecture Violation)
- Middleware/Pipeline-Ketten bieten Potenzial für Pattern Fragmentation
- Multiple Extension-Points mit unterschiedlichen Implementierungsmustern
- Historisch gewachsenes Projekt mit regelmäßigen Refactorings
- Gute Balance zwischen Größe und Analysetiefe

**Risiken:**
- Twisted-basierte Async-Architektur kann AST-Parsing erschweren
- Einige Module sind sehr groß und könnten viele Low-Impact-Findings erzeugen

---

### Repo 3 — Historisch gewachsen: `paramiko/paramiko`

| Eigenschaft | Wert |
|------------|-------|
| URL | https://github.com/paramiko/paramiko |
| Typ | Bibliothek (SSH2 Protocol) |
| Größe | ~15k Python LOC |
| Python-Version | 3.6+ |
| Architektur | Monolithisch mit organisch gewachsenen Modulen |

**Warum geeignet:**
- 20+ Jahre Entwicklungsgeschichte — ideales Testobjekt für architektonische Erosion
- Kryptografie-Module mit heterogenen Exception-Patterns
- Transport/Channel/Auth als separate Concerns, aber mit bekannten Boundary-Verletzungen
- Hohe Wahrscheinlichkeit für Temporal Volatility, Mutant Duplicates, Broad Exception Monoculture
- Realwelt-Referenz für „gewachsene Codebasis"

**Risiken:**
- Einige Module verwenden C-Extensions (werden von drift ignoriert)
- Kryptografie-Code hat Pattern-Wiederholungen, die technisch korrekt, aber als Fragmentation erkannt werden könnten

---

## Diversitäts-Check

| Kriterium | marshmallow | scrapy | paramiko |
|-----------|-------------|--------|----------|
| Größe | Klein (~5k) | Mittel (~30k) | Mittel-Klein (~15k) |
| Alter | ~10 Jahre | ~15 Jahre | ~20 Jahre |
| Architektur | Flach | Layered | Monolithisch |
| Erwarteter Drift | Niedrig | Mittel | Hoch |
| Framework-Typ | Library | Framework | Protocol Impl. |

**Einschätzung Lead:** ✅ Auswahl ist ausreichend divers. Abdeckung von sauber bis erosiv, klein bis mittel, flach bis geschichtet.

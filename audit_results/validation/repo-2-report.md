# Repo 2 — scrapy/scrapy

**Validation Engineer Report**  
**Datum:** 2026-03-30  
**Drift-Version:** 1.1.4  

## Kurzbeschreibung

Scrapy ist ein Web-Scraping-Framework mit ~30k Python LOC.
Layered Architecture: Core → Spiders → Middleware → Pipelines → Extensions.
Twisted-basierte Async-Architektur, 15+ Jahre aktive Entwicklung.

## Analyseergebnisse

| Metrik | Wert |
|--------|------|
| Drift-Score | 0.586 |
| Severity | medium |
| Findings gesamt | 714 |
| CI-Check (`--fail-on high`) | ❌ FAIL |

### Verteilung nach Signal

| Signal | Anzahl |
|--------|--------|
| architecture_violation | 194 |
| dead_code_accumulation | 159 |
| circular_import | 131 |
| explainability_deficit | 39 |
| fan_out_explosion | 37 |
| temporal_volatility | 32 |
| cohesion_deficit | 30 |
| pattern_fragmentation | 18 |
| mutant_duplicate | 15 |
| bypass_accumulation | 14 |
| cognitive_complexity | 14 |
| system_misalignment | 12 |
| doc_impl_drift | 10 |
| test_polarity_deficit | 3 |
| naming_contract_violation | 3 |
| co_change_coupling | 3 |

### Verteilung nach Severity

| Severity | Anzahl |
|----------|--------|
| high | 305 |
| medium | 330 |
| low | 65 |
| info | 14 |

## Top 10 Findings

| # | Severity | Signal | Title | File/Module | Impact |
|---|----------|--------|-------|-------------|--------|
| 1 | high | PFS | error_handling: 89 variants in scrapy/ | scrapy/ | 0.961 |
| 2 | high | PFS | error_handling: 68 variants in tests/ | tests/ | 0.928 |
| 3 | high | AVS | God module: settings/default_settings.py | settings/ | 0.114 |
| 4 | high | PFS | error_handling: 17 variants in scrapy/core/ | scrapy/core/ | 0.602 |
| 5 | high | PFS | error_handling: 8 variants in extensions/ | scrapy/extensions/ | 0.462 |
| 6 | high | PFS | error_handling: 8 variants in pipelines/ | scrapy/pipelines/ | 0.431 |
| 7 | high | PFS | error_handling: 7 variants in downloader/handlers/ | scrapy/core/downloader/handlers/ | 0.404 |
| 8 | medium | AVS | Circular dependency (23 modules) | scrapy/addons.py | 0.397 |
| 9 | high | PFS | error_handling: 6 variants in commands/ | scrapy/commands/ | 0.372 |
| 10 | high | PFS | error_handling: 5 variants in downloader/ | scrapy/core/downloader/ | 0.334 |

## Manuelle Stichproben-Verifikation

### ✅ Korrekt: AVS — Circular dependency (23 modules) (Finding #8)
Verifiziert: crawler.py allein hat 17 interne Imports. Die zirkuläre Abhängigkeitskette ist real und ein bekanntes Scrapy-Architekturmuster (Twisted-bedingt).

### ✅ Korrekt: PFS — Error-Handling-Fragmentation
89 verschiedene Error-Handling-Varianten im Hauptmodul. Bei einem Framework dieser Größe plausibel — unterschiedliche Exception-Typen pro Subsystem (Downloader, Spider, Middleware) erzeugen tatsächlich heterogene Patterns.

### ✅ Korrekt: MDS — Duplicate test methods
Test-Klassen TestCrawlerProcessSubprocessBase.test_simple und TestCrawlerRunnerSubprocessBase.test_simple sind identisch. Typisches Copy-Paste-Pattern in Test-Suites.

### ⚠️ Grenzwertig: PFS-Dominanz
18 von 714 Findings sind PFS, aber sie dominieren fix_first — 7 der Top 10. Die Granularität (pro Unterverzeichnis) führt zu Redundanz: scrapy/ enthält scrapy/core/, scrapy/extensions/ etc., alle mit separaten PFS-Findings für dasselbe Grundproblem.

### ✅ Korrekt: circular_import (131 Findings)
Die hohe Zahl spiegelt reale Scrapy-Architektur wider. Twisted-basierte Frameworks neigen zu zirkulären Imports durch Lazy-Loading-Patterns.

## Stärken

- **AVS** erkennt korrekt die komplexe Abhängigkeitsstruktur mit 23-Modul-Zyklus
- **PFS** quantifiziert Error-Handling-Inkonsistenz sinnvoll
- **MDS** findet echte Test-Duplikate, die automatisierbar sind
- Score 0.586 (medium) spiegelt die bekannte Architekturkomplexität realistisch wider
- **CI-Check FAIL** ist bei diesem Repo nachvollziehbar — hier wäre ein Gate sinnvoll

## Schwächen

- **Finding-Volumen**: 714 Findings sind für ein Erstgespräch überwältigend
- **PFS-Redundanz**: Gleicher Error-Handling-Befund auf 5+ Granulartitätsstufen dupliziert
- **DCA**: 159 Findings — bei einem Framework mit Plugin-Architektur großteils FP
- **AVS-Duplikate**: Viele AVS-Findings erscheinen exakt doppelt
- **circular_import**: 131 Findings, aber die meisten zeigen denselben 23-Modul-Zyklus aus verschiedenen Perspektiven

## Nützlichkeit für Agenten

**Mittel-Hoch.** Fix_first ist brauchbar für Priorisierung, aber:
- Agent bräuchte PFS-Deduplizierung über Verzeichnishierarchien
- MDS-Findings sind direkt automatisierbar
- AVS-Zyklus-Finding ist strategisch wertvoll, aber nicht in einem Schritt behebbar
- 714 Findings überfordern Token-Budgets — compact-Modus ist Pflicht

## Zwischenfazit

**Hoch** — Drift liefert real wertvolle Architektur-Insights für ein komplexes Framework. Die Hauptprobleme sind Volumen und Redundanz, nicht Korrektheit.

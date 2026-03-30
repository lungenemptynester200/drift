# Repo 3 — paramiko/paramiko

**Validation Engineer Report**  
**Datum:** 2026-03-30  
**Drift-Version:** 1.1.4  

## Kurzbeschreibung

Paramiko ist eine SSH2-Protocol-Implementierung in Python mit ~15k LOC.
20+ Jahre Entwicklungsgeschichte, monolithisch gewachsene Architektur.
Kryptografie-Module, Transport/Channel/Auth als separate Concerns.

## Analyseergebnisse

| Metrik | Wert |
|--------|------|
| Drift-Score | 0.477 |
| Severity | medium |
| Findings gesamt | 275 |
| CI-Check (`--fail-on high`) | ✅ PASS |

### Verteilung nach Signal

| Signal | Anzahl |
|--------|--------|
| explainability_deficit | 71 |
| dead_code_accumulation | 51 |
| architecture_violation | 44 |
| naming_contract_violation | 29 |
| cognitive_complexity | 22 |
| circular_import | 17 |
| cohesion_deficit | 11 |
| doc_impl_drift | 10 |
| mutant_duplicate | 7 |
| fan_out_explosion | 6 |
| pattern_fragmentation | 3 |
| test_polarity_deficit | 2 |
| bypass_accumulation | 2 |

### Verteilung nach Severity

| Severity | Anzahl |
|----------|--------|
| high | 103 |
| medium | 118 |
| low | 51 |
| info | 3 |

## Top 10 Findings

| # | Severity | Signal | Title | File | Impact |
|---|----------|--------|-------|------|--------|
| 1 | high | PFS | error_handling: 62 variants in paramiko/ | paramiko/ | 0.874 |
| 2 | high | PFS | error_handling: 21 variants in tests/ | tests/ | 0.749 |
| 3 | high | PFS | error_handling: 8 variants in demos/ | demos/ | 0.462 |
| 4 | medium | AVS | Circular dependency (4 modules) | paramiko/hostkeys.py | 0.229 |
| 5 | high | MDS | Duplicates: NullServer.check_auth_gssapi_keyex / Server.check_auth_gssapi_keyex | demo_server.py:92 | 0.198 |
| 6 | high | MDS | Duplicates: KexGSSGex._generate_x / KexGex._generate_x | kex_gex.py:108 | 0.198 |
| 7 | high | MDS | Duplicates: ServiceRequestingTransport.handler / Transport.handler | transport.py:1640 | 0.198 |
| 8 | high | AVS | God module: common.py | paramiko/common.py | 0.112 |
| 9 | high | AVS | God module: transport.py | paramiko/transport.py | 0.112 |
| 10 | high | AVS | Zone of Pain: ssh_exception.py (I=0.04, D=0.96) | ssh_exception.py | 0.107 |

## Manuelle Stichproben-Verifikation

### ✅ Korrekt: AVS — God module transport.py (Finding #9)
Verifiziert: transport.py hat 3.456 Zeilen, 132 Funktionen und 4 Klassen. Eindeutiger God-Module-Befund.

### ✅ Korrekt: MDS — KexGSSGex._generate_x / KexGex._generate_x (Finding #6)
Verifiziert: KexGex._generate_x hat 8 Statements (Zeilen 108-124). Die Duplikate in Kex-Klassen sind ein bekanntes Paramiko-Pattern.

### ✅ Korrekt: AVS — Circular dependency (4 modules) (Finding #4)
Plausibel: hostkeys.py, transport.py und weitere Module haben wechselseitige Abhängigkeiten.

### ⚠️ Grenzwertig: AVS — God module common.py (Finding #8)
common.py hat nur 245 Zeilen und 3 Funktionen. Es ist eher eine Sammlung von Konstanten als ein God Module. Die hohe Fan-In-Zahl rechtfertigt den Befund strukturell, aber „God module" ist irreführend bei dieser Größe.

### ✅ Korrekt: AVS — Zone of Pain: ssh_exception.py
Instability=0.04, Distance=0.96 — fast reine Abstractness ohne eigene Abhängigkeiten. ssh_exception.py wird von vielen Modulen importiert, importiert selbst fast nichts. Korrekter Befund.

### ✅ Korrekt: EDS — Explainability Deficit (71 Findings)
transport.py und auth_handler.py enthalten hochkomplexen Krypto-Code ohne inline Dokumentation. Die hohe EDS-Zahl spiegelt reale Wartungsprobleme wider.

## Stärken

- **AVS** liefert die wertvollsten Findings: God modules, Zones of Pain, Circular Dependencies
- **MDS** findet reale Duplikate in Kryptografie-Modulen
- **EDS** markiert korrekt die undokumentierten Komplexitätszentren
- Score 0.477 (medium) ist realistisch für eine gewachsene Codebasis
- **Zone-of-Pain-Analyse** (Instability/Distance-Metriken) ist besonders aufschlussreich

## Schwächen

- **NBV (29 Findings)**: Viele Naming-Violations in Krypto-Code nutzen domänenspezifische Konventionen (RFC-Bezeichnungen), die drift als Verletzung wertet
- **DCA (51 Findings)**: Paramiko exportiert bewusst breit via __init__.py — hohe FP-Quote
- **AVS-Duplikate**: God module und Zone-of-Pain für common.py erscheinen jeweils doppelt
- **common.py als „God module"**: 245 Zeilen ist kein God Module — eher ein Constants-File mit hohem Fan-In

## Nützlichkeit für Agenten

**Hoch.** Die Findings sind architektonisch wertvoll:
- transport.py-Zerlegung ist als langfristiges Refactoring planbar
- MDS-Findings in kex_gex.py sind sofort umsetzbar
- Zone-of-Pain-Analyse liefert strategische Entscheidungsgrundlage
- EDS-Findings können als Dokumentationsaufträge delegiert werden

## Zwischenfazit

**Hoch** — Drift zeigt bei historisch gewachsenem Code seine größte Stärke. AVS-Findings (God modules, Zones of Pain) liefern echte architektonische Insights, die manuell schwer zu erfassen wären.

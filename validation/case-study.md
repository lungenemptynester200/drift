# Case Study — Drift-Validierung am Beispiel paramiko

**Rollout Analyst Report**  
**Datum:** 2026-03-30  

---

## Ausgangslage

**Repository:** paramiko/paramiko  
**Typ:** SSH2-Protocol-Implementierung, ~15k Python LOC  
**Geschichte:** 20+ Jahre, monolithisch gewachsen  
**Bekannte Probleme:** transport.py als Monolith, organisch gewachsene Exception-Hierarchie  

**Frage:** Kann drift architektonische Erosion in einer historisch gewachsenen Codebasis erkennen und priorisieren?

---

## Was drift gefunden hat

| Metrik | Wert |
|--------|------|
| Drift-Score | 0.477 (medium) |
| Gesamt-Findings | 275 |
| Davon high | 103 |
| Davon medium | 118 |
| CI-Check (--fail-on high) | PASS |

**Top-Signale:**
1. Explainability Deficit: 71 Findings (undokumentierter Krypto-Code)
2. Dead Code Accumulation: 51 Findings (Library-Exports)
3. Architecture Violation: 44 Findings (God modules, Zones of Pain, Circular deps)
4. Naming Contract Violation: 29 Findings (RFC-Konventionen)

---

## Welche Findings wirklich nützlich waren

### 1. God Module: transport.py (AVS)
- 3.456 Zeilen, 132 Funktionen, 4 Klassen
- Drift identifiziert dies korrekt als architektonisches Kernproblem
- **Wert:** Bestätigt bekannte Wartungslast, quantifiziert Impact

### 2. Zone of Pain: ssh_exception.py (AVS)
- Instability=0.04, Distance=0.96
- Hochstabil, aber von fast allen Modulen importiert
- **Wert:** Zeigt, wo eine Änderung maximale Blast-Radius hätte — strategisch wertvoll

### 3. Mutant Duplicates in Kex-Modulen (MDS)
- KexGSSGex._generate_x und KexGex._generate_x sind identisch
- ServiceRequestingTransport.handler und Transport.handler ebenso
- **Wert:** Konkret, verifizierbar, sofort umsetzbar

### 4. Circular Dependency (AVS)
- 4-Modul-Zyklus zwischen hostkeys, transport, auth-Modulen
- **Wert:** Erklärt Testfragilität und Import-Ordering-Probleme

### 5. Error-Handling Fragmentation (PFS)
- 62 verschiedene Error-Handling-Varianten im Hauptmodul
- **Wert:** Quantifiziert ein bekanntes Problem, macht refactoring-Aufwand planbar

---

## Welche Findings problematisch waren

### 1. DCA: 51 „unused exports" → ~90% False Positives
Paramiko exportiert bewusst breit via __init__.py für Nutzer-API. Drift erkennt dieses Pattern nicht.

### 2. NBV: 29 Naming Violations → ~50% False Positives
RFC-konforme Bezeichnungen (kex_, auth_handler, sftp_si) werden als Konventionsverletzung gewertet. Domänenspezifische Terminologie fehlt.

### 3. AVS-Duplikate: Finding-Verdopplung
God-module und Zone-of-Pain-Findings für common.py erscheinen jeweils doppelt — kein Informationsgewinn, aber erhöhtes Rauschen.

### 4. EDS: 71 Findings → Überflutung
Krypto-Code ist inhärent komplex. Ein Top-10-Filter oder Schwellwert-Anpassung wäre sinnvoller als 71 gleichwertige Findings.

---

## Welche Fixes möglich oder sinnvoll waren

| Finding | Fix möglich? | Aufwand | Sinnvoll? |
|---------|-------------|---------|-----------|
| MDS: KexGSSGex._generate_x | ✅ Ja | Low | ✅ Ja — Basisklassen-Extraktion |
| MDS: Transport.handler | ✅ Ja | Low | ✅ Ja — Methoden-Delegation |
| AVS: transport.py Split | ✅ Ja | High | ⚠️ Langfristig ja, Risiko hoch |
| EDS: Top-5 Dokumentation | ✅ Ja | Low | ✅ Ja — Wartbarkeit steigt |
| PFS: Error-Handling consolidation | ⚠️ Teilweise | High | ⚠️ Nur mit klarer Zielarchitektur |
| AVS: Circular dep break | ⚠️ Teilweise | Medium | ✅ Ja — aber erfordert Planung |

---

## Eignung für Vibe-Coding / Agenten-Workflows

### Gut geeignet (Agent kann direkt handeln):
- **MDS-Findings**: Agent navigiert zu Zeile, erkennt Duplikat, erstellt Basisklasse oder Delegation
- **EDS-Findings**: Agent liest Funktion, generiert Docstring, fügt ein

### Bedingt geeignet (Agent braucht Kontext):
- **AVS God-Module**: Agent kann Verantwortlichkeiten analysieren, aber Split erfordert Domänenwissen
- **AVS Circular Dep**: Agent kann Zyklus erkennen, aber Kanten-Break erfordert Architekturverständnis

### Nicht geeignet (zu abstrakt für autonome Umsetzung):
- **PFS Konsolidierung**: Agent weiß nicht, welches Pattern das Ziel ist
- **DCA Bereinigung**: In Libraries fast immer falscher Impuls

### Gesamturteil
Paramiko ist ein gutes Beispiel für ein Repo, in dem drift ~60% der Findings agent-tauglich macht. Die restlichen 40% sind strategischer Natur und erfordern menschliche Architekturentscheidungen.

---

## Fazit

Drift liefert bei paramiko echte Architektur-Insights, die manuell schwer zu erfassen wären. Die Zone-of-Pain-Analyse und God-Module-Erkennung sind die wertvollsten Features. Die Hauptschwäche liegt bei DCA/NBV-False-Positives, die bei Protocol-Libraries systematisch auftreten. Für einen Agent-Workflow sind MDS und EDS die zuverlässigsten Entry Points.

# Agent-Usability — Eignung des drift-Outputs für Coding-Agenten

**Signal Auditor Report**  
**Datum:** 2026-03-30  
**Drift-Version:** 1.1.4  

## Methode

5 exemplarische Findings aus den validierten Repos wurden daraufhin bewertet,
ob ein Coding-Agent (Copilot, Cursor, Aider etc.) mit dem drift-Output
direkt handeln kann — ohne menschliche Nachinterpretation.

---

## Finding 1: MDS — IP._serialize / IPInterface._serialize (marshmallow)

**drift-Output:**
```
signal: mutant_duplicate
title: Exact duplicates (2×): IP._serialize, IPInterface._serialize
file: src/marshmallow/fields.py:1783
impact: 0.198
remediation: Merge '?' and '?' (in ) (effort=low, impact=high)
next_step: N/A
```

**Was ein Agent wahrscheinlich tut:**
- Navigiert zu fields.py:1783
- Erkennt zwei identische _serialize-Methoden in Geschwisterklassen
- Extrahiert die Methode in eine gemeinsame Basisklasse oder erstellt einen Mixin

**Reicht der Output?** Teilweise.
- ✅ File und Zeilenangabe sind korrekt
- ✅ Signal-Typ ist eindeutig interpretierbar
- ❌ Remediation enthält Platzhalter ('?' statt tatsächliche Symbolnamen)
- ❌ Kein Hinweis auf die zweite Duplikat-Stelle (IPInterface._serialize Zeile nicht angegeben)

**Fehlende Information:** Zeilenangabe des zweiten Duplikats, konkrete Symbolnamen in der Remediation.

---

## Finding 2: AVS — Circular dependency 23 modules (scrapy)

**drift-Output:**
```
signal: architecture_violation
title: Circular dependency (23 modules)
file: scrapy/addons.py
impact: 0.397
remediation: Break circular dependency (effort=medium, impact=high)
next_step: N/A
```

**Was ein Agent wahrscheinlich tut:**
- Öffnet addons.py als Einstieg
- Versucht den Zyklus zu verstehen
- Scheitert wahrscheinlich: 23-Modul-Zyklus ist zu komplex für automtische Auflösung

**Reicht der Output?** Nein.
- ✅ Signal korrekt identifiziert
- ❌ Nur ein Modul des 23-Modul-Zyklus benannt
- ❌ Kein Zyklusgraph oder -pfad angegeben
- ❌ „Break circular dependency" ist als Handlungsanweisung zu unspezifisch
- ❌ Kein Vorschlag, welche Kante zu brechen wäre

**Fehlende Information:** Vollständiger Zykluspfad, Empfehlung für schwächste Kante, Modulliste.

---

## Finding 3: AVS — God module transport.py (paramiko)

**drift-Output:**
```
signal: architecture_violation
title: God module candidate: transport.py
file: paramiko/transport.py
impact: 0.112
next_step: Split transport.py by responsibility and extract stable interfaces to reduce fan-in and fan-out.
```

**Was ein Agent wahrscheinlich tut:**
- Öffnet transport.py (3.456 Zeilen)
- Analysiert Verantwortlichkeiten
- Schlägt Split in 3-4 Module vor (ggf. transport_core.py, transport_kex.py, transport_auth.py)
- Kann den Split planen, aber Umsetzung ist riskant ohne Tests

**Reicht der Output?** Teilweise.
- ✅ File korrekt, next_step gibt Richtung vor
- ✅ „Split by responsibility" ist eine brauchbare Anweisung
- ❌ Keine konkreten Verantwortlichkeits-Cluster benannt
- ❌ Keine Angabe, welche Methoden zusammengehören

**Fehlende Information:** Cluster-Vorschlag (welche Funktionen/Klassen in welches neue Modul), Fan-In/Fan-Out-Zahlen pro Cluster.

---

## Finding 4: PFS — 89 error_handling variants (scrapy)

**drift-Output:**
```
signal: pattern_fragmentation
title: error_handling: 89 variants in scrapy/
file: scrapy/
impact: 0.961
remediation: Consolidate 89 pattern variants in scrapy (effort=medium, impact=high)
next_step: N/A
```

**Was ein Agent wahrscheinlich tut:**
- Sucht nach Exception-Handling-Patterns im scrapy/-Verzeichnis
- Findet unterschiedliche try/except-Stile
- Weiß nicht, welche die „richtige" Variante ist
- Kann ohne Konvention-Referenz nicht konsolidieren

**Reicht der Output?** Nein.
- ✅ Problem korrekt quantifiziert
- ❌ Keine Beispiele der divergierenden Patterns
- ❌ Kein Vorschlag für Zielpattern
- ❌ „Consolidate 89 variants" ist bei einem Framework nicht in einem Schritt machbar
- ❌ Keine Unterscheidung zwischen funktional verschiedenen und redundanten Varianten

**Fehlende Information:** Exemplarische Pattern-Paare, dominantes Pattern als Konsolidierungsziel, konkrete Dateien.

---

## Finding 5: EDS — Unexplained complexity: Schema._invoke_field_validators (marshmallow)

**drift-Output:**
```
signal: explainability_deficit
title: Unexplained complexity: Schema._invoke_field_validators
file: src/marshmallow/schema.py:1125
impact: 0.059
remediation: Document 'Schema._invoke_field_validators' (effort=low, impact=medium)
next_step: N/A
```

**Was ein Agent wahrscheinlich tut:**
- Navigiert zu schema.py:1125
- Liest die Methode
- Generiert einen Docstring basierend auf Code-Analyse
- Fügt den Docstring ein

**Reicht der Output?** Ja.
- ✅ File und Zeile korrekt
- ✅ Aufgabe ist klar und atomar
- ✅ Effort-Einschätzung (low) ist realistisch
- ✅ Agent kann ohne zusätzliche Information handeln

**Fehlende Information:** Keine — dies ist der ideale Finding-Typ für Agenten.

---

## Zusammenfassung

### Agent-Tauglichkeit nach Kategorie

| Finding-Typ | Agent kann handeln? | Hauptgrund |
|-------------|---------------------|------------|
| MDS (Duplicates) | ✅ Ja, mit Einschränkung | Zweite Stelle fehlt |
| EDS (Explainability) | ✅ Ja | Atomare Aufgabe, klare Lokation |
| AVS (God module) | ⚠️ Teilweise | Richtung klar, aber Cluster fehlen |
| AVS (Circular dep) | ❌ Nein | Zu komplex, zu unspezifisch |
| PFS (Fragmentation) | ❌ Nein | Kein Zielpattern, zu abstrakt |

### Kernerkenntnis

**drift-Output ist agent-tauglich für atomare, lokalisierte Findings** (MDS, EDS, einzelne NBV).
**drift-Output ist nicht agent-tauglich für systemische Findings** (Circular deps, PFS-Konsolidierung, God-Module-Splits).

### Was für autonome Agent-Umsetzung fehlt

1. **Zweite Duplikat-Stelle bei MDS**: Agent braucht beide Locations
2. **Zykluspfad bei circular_import/AVS**: Agent braucht die Modulliste und schwächste Kante
3. **Platzhalter in Remediation entfernen**: '?' statt konkreter Symbolnamen ist unbrauchbar
4. **Pattern-Beispiele bei PFS**: Agent braucht exemplarische Code-Snippets
5. **Responsibility-Cluster bei God-Modules**: Agent braucht gruppierte Funktionslisten

### Empfehlung

Für einen **Agent-First-Modus** sollte drift:
- MDS-Findings um die zweite Lokation erweitern
- EDS-Findings priorisieren (höchste Agent-Tauglichkeit)
- Systemische Findings (PFS, Circular) als „strategisch" markieren statt als direkt umsetzbar
- Remediation-Platzhalter ('?') durch echte Symbolnamen ersetzen

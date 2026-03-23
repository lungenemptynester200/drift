# v0.2.0 — Precision & Robustness

### Kurzbeschreibung
Release v0.2.0 bringt mehrere signifikante Verbesserungen der Signalsuite: AST-basierte Markdown-Analyse für DIA, Omnilayer-Erkennung und Hub-Dämpfung für AVS sowie ein hybrides Ähnlichkeitsmodell (AST + Embeddings) für MDS. Diese Änderungen reduzieren False Positives deutlich und erhöhen die Signal-Präzision.

### Added
- Neues Modul: `drift.embeddings` — zentrale Embedding-Service-Schicht mit lazy loading (all-MiniLM-L6-v2), FAISS-Index-Builder und disk-backed `EmbeddingCache`. Optional; Fallbacks vorhanden.
- CLI-Flags: `--no-embeddings`, `--embedding-model` (für `analyze` und `check`).
- Konfigurationsfelder: `embeddings_enabled`, `embedding_model`, `embedding_batch_size`, `allowed_cross_layer`.
- Optionales Dependency-Group `[markdown]` für `mistune>=3.0` (bessere Markdown-AST-Parsing-Option).

### Changed
- DIA (Doc-Impl-Aware): Regex-basierte Markdown-Extraktion ersetzt durch `mistune` AST-Parsing; Link-URLs werden nun übersprungen; ~80 URL-Segment-Blacklist hinzugefügt.
- AVS (Architectural-View-Signal): Omnilayer-Erkennung für cross-cutting Verzeichnisse (config/, utils/, types/, common/, shared/). Hub-Module werden per NetworkX In-Degree Centrality gedämpft (90th percentile → ×0.3 score).
- MDS (Module-Duplication-Signal): Hybrides Similarity-Scoring (0.6 × AST Jaccard + 0.4 × cosine embedding) für robustere Duplikaterkennung.

### Fixed
- DIA: Entfernt falsche Findings aus Badge/CI/Registry-URLs (z. B. actions/, workflows/, blob/).
- AVS: Findings unter Score 0.15 werden gefiltert, um Rauschen zu reduzieren.
- Embedding-Cosine: Normalisierung mit L2-Norm (vorher rohes Skalarprodukt).

### Notes
- **Knowledge‑Graph (KG) heuristics included:** v0.2.0 integrates import/relationship graph analysis and layer‑inference heuristics (e.g., import graph construction, hub‑dampening, inferred layer checks) to improve architecture‑aware detection.
- **Optional RAG-style retrieval (Embeddings + FAISS):** The new `drift.embeddings` module provides vector embeddings and optional FAISS indexing to enable semantic retrieval workflows. This supplies the retrieval component required for RAG-like setups; however, Drift remains deterministic by default and does not bundle an LLM — connecting an LLM for generation is an opt-in integration for downstream tooling.

### Hinweise für Anwender
- Wenn keine Embeddings verfügbar sind, verwende `--no-embeddings` oder installiere die `[markdown]`/embedding-Abhängigkeiten für bessere Genauigkeit.
- Neue Konfigurationsoptionen in `config` ermöglichen Feintuning (z. B. `allowed_cross_layer` Muster).

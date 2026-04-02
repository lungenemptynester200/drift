# Demo Recording Workflow (Vhs)

This folder contains the reproducible terminal demo setup for Drift.

## Files

- `demo.tape`: Vhs script that records core CLI commands.
- `demo.gif`: Rendered artifact used in `README.md`.
- `agent-fix-plan.tape`: Agent baseline plus prioritized remediation tasks on the demo project.
- `agent-diff.tape`: Staged-change guardrail flow using `drift diff --staged-only` in a temporary git repo.
- `agent-copilot-context.tape`: Repo-specific Copilot instruction generation from drift findings.

## Prerequisites

**Option A — VHS** (Linux / macOS recommended):

```bash
# macOS
brew install vhs
# or via Scoop on Windows
scoop install vhs
```

If your setup requires it, install Chrome/Chromium for rendering.

**Option B — Python + Pillow** (Windows-compatible fallback):

```bash
pip install Pillow   # already included in the dev venv
```

## Render the GIF

### Option A — VHS

Run from repository root:

```powershell
vhs demos/demo.tape
vhs demos/agent-fix-plan.tape
vhs demos/agent-diff.tape
vhs demos/agent-copilot-context.tape
```

Or use the helper script (also falls back to Python on Windows when VHS is unavailable):

```powershell
./scripts/render_demo.ps1
```

### Option B — Python (Windows / CI fallback)

```bash
python scripts/make_demo_gif.py
```

This generates `demos/demo.gif` using Pillow with the Catppuccin Mocha colour theme,
terminal window decoration, and a typing-effect animation — no browser or VHS required.

The command updates `demos/demo.gif`.

The agent tapes render to:

- `demos/agent-fix-plan.gif`
- `demos/agent-diff.gif`
- `demos/agent-copilot-context.gif`

## Keep it deterministic

- Prefer commands that run quickly and produce stable output.
- Avoid machine-specific absolute paths.
- Re-record after major CLI output changes.
- The staged diff tape creates its own temporary git repo under `demos/.tmp_agent_diff_demo`.

"""
Generate a beautiful terminal-recording-style demo GIF for Drift.

Requirements: Pillow
Run from repo root: python scripts/make_demo_gif.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Terminal colour palette — Catppuccin Mocha
# ---------------------------------------------------------------------------
BG          = (30, 30, 46)          # #1e1e2e  Base
FG          = (205, 214, 244)       # #cdd6f4  Text
ACCENT_CYAN = (137, 220, 235)       # #89dceb  Sky
ACCENT_BLUE = (137, 180, 250)       # #89b4fa  Blue
ACCENT_RED  = (243, 139, 168)       # #f38ba8  Red
ACCENT_YEL  = (249, 226, 175)       # #f9e2af  Yellow
ACCENT_GRN  = (166, 227, 161)       # #a6e3a1  Green
ACCENT_MAV  = (203, 166, 247)       # #cba6f7  Mauve
DIM         = (108, 112, 134)       # #6c7086  Overlay0
BORDER      = (88, 91, 112)         # #585b70  Surface1
WIN_RED     = (235,  80,  80)
WIN_YEL     = (255, 189,  46)
WIN_GRN     = ( 40, 200,  80)


# ---------------------------------------------------------------------------
# Captured drift output  (run once, store here for determinism)
# ---------------------------------------------------------------------------
def run_drift(repo_root: Path) -> str:
    """Run drift analyze and return the plain-text output."""
    result = subprocess.run(
        [
            sys.executable, "-m", "drift", "analyze",
            "--repo", str(repo_root),
            "--exit-zero",
            "--no-color",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(repo_root),
        env={
            **__import__("os").environ,
            "COLUMNS": "90",
            "LINES": "40",
        },
    )
    return result.stdout or result.stderr


def run_drift_check(repo_root: Path) -> str:
    """Run drift check and return the plain-text output."""
    result = subprocess.run(
        [
            sys.executable, "-m", "drift", "check",
            "--fail-on", "high",
            "--no-color",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(repo_root),
    )
    out = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        exit_label = "exit 0  ✓"
    else:
        exit_label = f"exit {result.returncode}  (findings above threshold)"
    return out + f"\n\n{exit_label}"


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", text)


def _load_font(size: int):
    from PIL import ImageFont  # type: ignore[import-untyped]
    # Prefer JetBrains Mono, Consolas, Courier New in that order
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/courbd.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Single-frame rendering
# ---------------------------------------------------------------------------
W, H     = 960, 600
PADDING  = 20
FONT_SZ  = 13
LINE_H   = 19
TITLE_H  = 34    # window chrome height
PROMPT   = "PS drift> "


def _make_frame(lines: list[str], title: str = "drift analyze"):  # -> PIL.Image
    from PIL import Image, ImageDraw  # type: ignore[import-untyped]

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    font = _load_font(FONT_SZ)

    # ── window chrome ────────────────────────────────────────────────────
    chrome_bg = (24, 24, 37)     # darker than BG
    draw.rectangle([0, 0, W, TITLE_H], fill=chrome_bg)

    # traffic-light dots
    for i, col in enumerate([WIN_RED, WIN_YEL, WIN_GRN]):
        cx = 18 + i * 22
        cy = TITLE_H // 2
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=col)

    # title text
    tw = draw.textlength(title, font=font)
    draw.text(((W - tw) / 2, (TITLE_H - FONT_SZ) / 2), title, fill=DIM, font=font)

    # ── terminal body ─────────────────────────────────────────────────────
    y = TITLE_H + PADDING
    max_lines = (H - TITLE_H - PADDING * 2) // LINE_H

    visible = lines[-max_lines:] if len(lines) > max_lines else lines

    for raw_line in visible:
        line = _strip_ansi(raw_line)
        # simple colour hints based on content
        colour = FG
        lo = line.strip().lower()
        if lo.startswith("drift score") or "drift score" in lo:
            colour = ACCENT_CYAN
        elif lo.startswith("│ drift score") or "DRIFT SCORE" in line:
            colour = ACCENT_CYAN
        elif lo.startswith("signal:") or "signal:" in lo:
            colour = ACCENT_BLUE
        elif lo.startswith("trend:") or "trend:" in lo:
            colour = ACCENT_MAV
        elif "error" in lo or "CRITICAL" in line or "✗" in line:
            colour = ACCENT_RED
        elif any(k in lo for k in ("findings", "module drift", "score", "ranking")):
            colour = ACCENT_CYAN
        elif lo.startswith(PROMPT.lower()) or PROMPT in line:
            colour = ACCENT_GRN
        elif lo.startswith("$") or lo.startswith("ps "):
            colour = ACCENT_GRN
        elif "complete" in lo or "stable" in lo or "✓" in line:
            colour = ACCENT_GRN
        elif "high" in lo or "critical" in lo:
            colour = ACCENT_RED
        elif "medium" in lo:
            colour = ACCENT_YEL
        elif lo.startswith("│") or lo.startswith("|"):
            colour = FG
        elif lo.startswith("├") or lo.startswith("└") or lo.startswith("┬"):
            colour = BORDER

        draw.text((PADDING, y), line[:130], fill=colour, font=font)
        y += LINE_H
        if y > H - PADDING:
            break

    return img


# ---------------------------------------------------------------------------
# Build animation frames
# ---------------------------------------------------------------------------
def build_frames(analyze_output: str, check_output: str) -> list:
    frames = []

    analyze_lines_raw = analyze_output.splitlines()

    # filter out .tmp_launch_venv_local noise
    analyze_lines: list[str] = []
    for ln in analyze_lines_raw:
        # skip venv table rows and empty continuation rows inside those
        stripped = _strip_ansi(ln)
        if ".tmp_launch_venv" in stripped:
            continue
        analyze_lines.append(ln)

    # ── Phase 1: command prompt + typing ─────────────────────────────────
    prompt_frames: list[str] = []
    prompt = PROMPT + "drift analyze --repo . --exit-zero"
    for i in range(0, len(prompt) + 1, 2):
        prompt_frames.append(prompt[:i])

    for p in prompt_frames:
        frames.append((_make_frame([p], "drift — analyze"), 60))

    # pause at full command
    for _ in range(4):
        frames.append((_make_frame([prompt], "drift — analyze"), 80))

    # ── Phase 2: analysis output arriving in chunks ───────────────────────
    displayed: list[str] = [prompt, ""]
    # skip "Signal: ..." progress lines and blank lines within progress
    output_lines = [
        ln for ln in analyze_lines
        if not ln.strip().startswith("Signal:")
    ]

    # Add CHUNKS of lines, not every line individually, to keep frame count low
    chunk_size = max(1, len(output_lines) // 25)  # ~25 frames for body
    for i in range(0, len(output_lines), chunk_size):
        chunk = output_lines[i : i + chunk_size]
        displayed.extend(chunk)
        delay = 40 if i > 6 else 100
        frames.append((_make_frame(displayed, "drift — analyze"), delay))

    # hold final output
    for _ in range(12):
        frames.append((_make_frame(displayed, "drift — analyze"), 150))

    # ── Phase 3: second command ───────────────────────────────────────────
    displayed.append("")
    cmd2 = PROMPT + "drift check --fail-on high"
    for i in range(0, len(cmd2) + 1, 3):
        frames.append((_make_frame(displayed + [cmd2[:i]], "drift — check"), 50))

    for _ in range(3):
        frames.append((_make_frame(displayed + [cmd2], "drift — check"), 80))

    # check output lines
    check_displayed = displayed + [cmd2, ""]
    for line in check_output.splitlines():
        check_displayed.append(line)
        frames.append((_make_frame(check_displayed, "drift — check"), 60))

    # hold final frame
    for _ in range(25):
        frames.append((_make_frame(check_displayed, "drift — check"), 150))

    return frames


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    from PIL import Image  # type: ignore[import-untyped]

    repo_root = Path(__file__).parent.parent
    output    = repo_root / "demos" / "demo.gif"

    print("Running drift analyze (this takes ~15s) …")
    analyze_out = run_drift(repo_root)

    print("Running drift check …")
    check_out = run_drift_check(repo_root)

    print("Building frames …")
    frames = build_frames(analyze_out, check_out)

    print(f"Generated {len(frames)} frames — saving GIF …")
    imgs    = [f for f, _ in frames]
    delays  = [d for _, d in frames]

    # Quantise to 96-colour palette for a much smaller GIF (~3–4× smaller)
    def _quantise(img):
        return img.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=0)

    q0 = _quantise(imgs[0])
    q_rest = [_quantise(im) for im in imgs[1:]]

    q0.save(
        output,
        save_all=True,
        append_images=q_rest,
        optimize=True,
        loop=0,
        duration=delays,
    )
    print(f"Saved → {output}  ({output.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

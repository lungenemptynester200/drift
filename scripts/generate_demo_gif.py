#!/usr/bin/env python3
"""Generate a polished demo GIF from real drift CLI output."""

from __future__ import annotations

import re
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).parent.parent
OUT_GIF = REPO_ROOT / "demos" / "demo.gif"

WIDTH = 1200
HEIGHT = 700
PAD_X = 22
PAD_Y = 14
TITLEBAR_H = 34
PROMPT_H = 28
LINE_H = 16
MAX_COLS = 120
VISIBLE_LINES = (HEIGHT - TITLEBAR_H - PROMPT_H - PAD_Y * 2) // LINE_H

BG = (30, 30, 46)
TITLE_BG = (24, 24, 37)
TEXT = (205, 214, 244)
DIM = (166, 173, 200)
PROMPT = (137, 180, 250)
CMD = (166, 227, 161)
ERR = (243, 139, 168)
OK = (166, 227, 161)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


FONT_REG = load_font("C:/Windows/Fonts/Consola.ttf", 13)
FONT_BOLD = load_font("C:/Windows/Fonts/ConsolaBd.ttf", 13)
FONT_SM = load_font("C:/Windows/Fonts/Consola.ttf", 12)


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def run_cmd(args: list[str]) -> tuple[str, int]:
    result = subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (result.stdout or "") + (result.stderr or "")
    out = strip_ansi(out).replace("\r\n", "\n").replace("\r", "\n")
    return out, result.returncode


def to_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.split("\n"):
        if not raw:
            lines.append("")
            continue
        wrapped = textwrap.wrap(raw, width=MAX_COLS, replace_whitespace=False) or [""]
        lines.extend(wrapped)
    return lines


def draw_frame(title: str, prompt_text: str, cmd_text: str, lines: list[str]) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (WIDTH, TITLEBAR_H)], fill=TITLE_BG)
    for i, color in enumerate([(243, 139, 168), (249, 226, 175), (166, 227, 161)]):
        x = 16 + i * 20
        draw.ellipse([(x - 5, 12), (x + 5, 22)], fill=color)
    tw = draw.textlength(title, font=FONT_SM)
    draw.text(((WIDTH - tw) / 2, 10), title, fill=DIM, font=FONT_SM)

    y0 = TITLEBAR_H + 6
    draw.text((PAD_X, y0), prompt_text, fill=PROMPT, font=FONT_REG)
    x_off = PAD_X + draw.textlength(prompt_text, font=FONT_REG)
    draw.text((x_off, y0), cmd_text, fill=CMD, font=FONT_BOLD)

    y = TITLEBAR_H + PROMPT_H + PAD_Y
    for line in lines[:VISIBLE_LINES]:
        lc = line.lower()
        if "drift check failed" in lc or "error" in lc or "failed" in lc:
            color = ERR
        elif "drift check passed" in lc:
            color = OK
        elif line.startswith("Signal:") or "DRIFT SCORE" in line:
            color = CMD
        else:
            color = TEXT
        draw.text((PAD_X, y), line, fill=color, font=FONT_REG)
        y += LINE_H

    return img


def typing_frames(command: str, title: str) -> list[tuple[Image.Image, int]]:
    frames: list[tuple[Image.Image, int]] = []
    prompt_text = "PS C:\\Users\\mickg\\PWBS\\drift> "
    for n in [5, 12, 20, len(command)]:
        partial = command[:n] + ("_" if n < len(command) else "")
        frame = draw_frame(title, prompt_text, partial, [])
        frames.append((frame, 120 if n < len(command) else 300))
    return frames


def output_frames(
    command: str,
    title: str,
    lines: list[str],
    pauses: list[int],
) -> list[tuple[Image.Image, int]]:
    frames: list[tuple[Image.Image, int]] = []
    prompt_text = "PS C:\\Users\\mickg\\PWBS\\drift> "
    if len(lines) <= VISIBLE_LINES:
        frame = draw_frame(title, prompt_text, command, lines)
        return [(frame, pauses[-1] if pauses else 2000)]

    windows = [
        0,
        max(0, len(lines) // 4),
        max(0, len(lines) // 2),
        max(0, len(lines) - VISIBLE_LINES),
    ]
    used: list[int] = []
    for idx, start in enumerate(windows):
        if start in used:
            continue
        used.append(start)
        segment = lines[start:start + VISIBLE_LINES]
        frame = draw_frame(title, prompt_text, command, segment)
        dur = pauses[min(idx, len(pauses) - 1)] if pauses else 1800
        frames.append((frame, dur))
    return frames


def build_demo() -> None:
    print("[*] Running real commands...")
    analyze_out, analyze_rc = run_cmd(["drift", "analyze", "--repo", "."])
    check_out, check_rc = run_cmd(["drift", "check", "--fail-on", "high"])

    analyze_lines = to_lines(analyze_out)
    check_lines = to_lines(check_out)

    print(f"    analyze exit={analyze_rc}, lines={len(analyze_lines)}")
    print(f"    check   exit={check_rc}, lines={len(check_lines)}")

    frames: list[tuple[Image.Image, int]] = []
    cmd_analyze = "drift analyze --repo ."
    cmd_check = "drift check --fail-on high"

    # Start with real output immediately to avoid an empty-looking intro frame.
    frames.extend(
        output_frames(
            cmd_analyze,
            "drift demo - analyze",
            analyze_lines,
            [1800, 1800, 1900, 2300],
        )
    )
    frames.extend(typing_frames(cmd_check, "drift demo - check"))
    frames.extend(
        output_frames(
            cmd_check,
            "drift demo - check",
            check_lines,
            [1500, 1900, 2200, 3000],
        )
    )

    images = [f for f, _ in frames]
    durations = [d for _, d in frames]

    images[0].save(
        OUT_GIF,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )

    print(f"GIF written: {OUT_GIF}")
    print(f"size: {OUT_GIF.stat().st_size} bytes")
    print(f"frames: {len(images)}")
    print(f"resolution: {WIDTH}x{HEIGHT}")


if __name__ == "__main__":
    build_demo()
    sys.exit(0)

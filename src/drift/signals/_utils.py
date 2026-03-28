"""Shared utilities for signal implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_TS_LANGUAGES: frozenset[str] = frozenset(
    {"typescript", "tsx", "javascript", "jsx"},
)

_SUPPORTED_LANGUAGES: frozenset[str] = frozenset({"python"}) | _TS_LANGUAGES


def is_test_file(file_path: Path) -> bool:
    """Return True if *file_path* looks like a test file (by name / path).

    Covers Python, TypeScript / JavaScript and common JS test directories.
    """
    name = file_path.name.lower()
    if (
        name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith(".test.ts")
        or name.endswith(".test.tsx")
        or name.endswith(".test.js")
        or name.endswith(".test.jsx")
        or name.endswith(".spec.ts")
        or name.endswith(".spec.tsx")
        or name.endswith(".spec.js")
        or name.endswith(".spec.jsx")
    ):
        return True

    # Common JS test directory convention
    parts = file_path.as_posix().lower().split("/")
    return "__tests__" in parts


# ---------------------------------------------------------------------------
# Tree-sitter helpers (shared by GCD, NBV, and future TS-aware signals)
# ---------------------------------------------------------------------------


def ts_parse_source(source: str, language: str = "typescript") -> tuple[Any, bytes] | None:
    """Parse *source* with tree-sitter.  Returns ``(root_node, source_bytes)`` or *None*."""
    try:
        from drift.ingestion.ts_parser import _get_parser, tree_sitter_available

        if not tree_sitter_available():
            return None
        ts_lang = "tsx" if language in ("tsx", "jsx") else "typescript"
        parser = _get_parser(ts_lang)
        source_bytes = source.encode("utf-8")
        tree = parser.parse(source_bytes)
        return tree.root_node, source_bytes
    except Exception:
        return None


def ts_walk(node: Any) -> list[Any]:
    """Depth-first walk of all descendants of a tree-sitter node."""
    result: list[Any] = []
    stack = [node]
    while stack:
        n = stack.pop()
        result.append(n)
        stack.extend(reversed(n.children))
    return result


def ts_node_text(node: Any, source: bytes) -> str:
    """Extract the UTF-8 text of a tree-sitter node."""
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")

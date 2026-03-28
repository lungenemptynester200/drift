"""Signal 10: Guard Clause Deficit (GCD).

Detects modules where public, non-trivial functions uniformly lack
guard clauses — isinstance checks, assert statements, if-raise/return
patterns that validate inputs early.

This is a proxy for *consistent wrongness* (EPISTEMICS §2): when every
function blindly trusts its inputs, the codebase is structurally
vulnerable to a single incorrect assumption propagating everywhere.
"""

from __future__ import annotations

import ast
from pathlib import Path, PurePosixPath
from typing import Any

from drift.config import DriftConfig
from drift.models import (
    FileHistory,
    Finding,
    FunctionInfo,
    ParseResult,
    Severity,
    SignalType,
)
from drift.signals._utils import (
    _SUPPORTED_LANGUAGES,
    _TS_LANGUAGES,
    is_test_file,
    ts_node_text,
    ts_parse_source,
    ts_walk,
)
from drift.signals.base import BaseSignal, register_signal

# Decorators that indicate input validation is handled externally.
_VALIDATION_DECORATORS: frozenset[str] = frozenset({
    "validate",
    "validator",
    "validates",
    "check_params",
    "validate_arguments",
    "validate_call",
    "typechecked",
    "beartype",
    "enforce_types",
})


def _has_guard(stmt: ast.stmt, param_names: set[str]) -> bool:
    """Return True if *stmt* is a guard clause referencing a parameter."""
    # isinstance(param, ...)
    if (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Call)
        and isinstance(stmt.value.func, ast.Name)
        and stmt.value.func.id == "isinstance"
        and stmt.value.args
        and isinstance(stmt.value.args[0], ast.Name)
    ):
        return stmt.value.args[0].id in param_names
    # assert <param> ...
    if isinstance(stmt, ast.Assert):
        return _references_param(stmt.test, param_names)
    # if <cond>: raise/return (single-branch guard)
    if (
        isinstance(stmt, ast.If)
        and not stmt.orelse
        and any(isinstance(s, ast.Raise | ast.Return) for s in stmt.body)
    ):
        return _references_param(stmt.test, param_names)
    return False


def _references_param(node: ast.expr, param_names: set[str]) -> bool:
    """Return True if the expression references at least one parameter name."""
    return any(
        isinstance(child, ast.Name) and child.id in param_names
        for child in ast.walk(node)
    )


def _function_is_guarded(source: str, func_info: FunctionInfo, param_names: set[str]) -> bool:
    """Parse function body and check first 50% of statements for guards."""
    # Check for validation decorators first
    for dec in func_info.decorators:
        dec_lower = dec.lower()
        if any(vd in dec_lower for vd in _VALIDATION_DECORATORS):
            return True

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return True  # benefit of doubt

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        body = node.body
        if not body:
            return True
        check_count = max(1, len(body) * 50 // 100)
        return any(_has_guard(stmt, param_names) for stmt in body[:check_count])
    return True  # no function found — benefit of doubt


# ── TypeScript guard detection (tree-sitter) ─────────────────────


def _ts_references_param(node: Any, param_names: set[str], src: bytes) -> bool:
    """Return True if tree-sitter *node* references at least one parameter."""
    return any(
        child.type == "identifier" and ts_node_text(child, src) in param_names
        for child in ts_walk(node)
    )


def _ts_is_guard_stmt(stmt: Any, param_names: set[str], src: bytes) -> bool:
    """Return True if *stmt* is a single-branch guard referencing a parameter."""
    if stmt.type != "if_statement":
        return False
    # Must be single-branch (no else)
    if any(c.type == "else_clause" for c in stmt.children):
        return False
    # Consequence must contain throw or return
    consequence = stmt.child_by_field_name("consequence")
    if not consequence:
        return False
    if not any(
        c.type in ("throw_statement", "return_statement") for c in ts_walk(consequence)
    ):
        return False
    # Condition must reference a parameter
    condition = stmt.child_by_field_name("condition")
    if not condition:
        return False
    return _ts_references_param(condition, param_names, src)


def _ts_find_body_stmts(root: Any) -> list[Any]:
    """Return the top-level statements from the first function body."""
    for node in ts_walk(root):
        if node.type in (
            "function_declaration",
            "method_definition",
            "arrow_function",
        ):
            body = node.child_by_field_name("body")
            if body and body.type == "statement_block":
                return [c for c in body.children if c.type not in ("{", "}")]
    return []


def _ts_function_is_guarded(
    source: str, func_info: FunctionInfo, param_names: set[str], language: str,
) -> bool:
    """Parse TS function body via tree-sitter and check for guard clauses."""
    for dec in func_info.decorators:
        dec_lower = dec.lower()
        if any(vd in dec_lower for vd in _VALIDATION_DECORATORS):
            return True

    result = ts_parse_source(source, language)
    if result is None:
        return True  # benefit of doubt (tree-sitter unavailable)

    root, src = result
    body_stmts = _ts_find_body_stmts(root)
    if not body_stmts:
        return True

    check_count = max(1, len(body_stmts) * 50 // 100)
    return any(
        _ts_is_guard_stmt(stmt, param_names, src)
        for stmt in body_stmts[:check_count]
    )


@register_signal
class GuardClauseDeficitSignal(BaseSignal):
    """Detect modules with uniformly unguarded public functions."""

    @property
    def signal_type(self) -> SignalType:
        return SignalType.GUARD_CLAUSE_DEFICIT

    @property
    def name(self) -> str:
        return "Guard Clause Deficit"

    def analyze(
        self,
        parse_results: list[ParseResult],
        file_histories: dict[str, FileHistory],
        config: DriftConfig,
    ) -> list[Finding]:
        min_public = config.thresholds.gcd_min_public_functions

        # Group qualifying functions by module directory
        module_funcs: dict[str, list[tuple[FunctionInfo, ParseResult]]] = {}

        for pr in parse_results:
            if pr.language not in _SUPPORTED_LANGUAGES:
                continue
            if is_test_file(pr.file_path):
                continue
            if pr.file_path.name in (
                "__init__.py", "index.ts", "index.tsx", "index.js", "index.jsx",
            ):
                continue

            for fn in pr.functions:
                if fn.name.startswith("_"):
                    continue
                if len(fn.parameters) < 2:
                    continue
                if fn.complexity < 5:
                    continue

                module_key = PurePosixPath(pr.file_path.parent).as_posix()
                module_funcs.setdefault(module_key, []).append((fn, pr))

        findings: list[Finding] = []

        for module_key, func_list in module_funcs.items():
            if len(func_list) < min_public:
                continue

            guarded = 0
            total_complexity = 0

            for fn, pr in func_list:
                param_names = set(fn.parameters)
                # Read source for the specific function
                source = _read_function_source(pr.file_path, fn, self._repo_path)
                if source is None:
                    guarded += 1  # benefit of doubt
                    continue

                if pr.language in _TS_LANGUAGES:
                    is_guarded = _ts_function_is_guarded(
                        source, fn, param_names, pr.language,
                    )
                else:
                    is_guarded = _function_is_guarded(source, fn, param_names)

                if is_guarded:
                    guarded += 1
                else:
                    total_complexity += fn.complexity

            total = len(func_list)
            guarded_ratio = guarded / total

            if guarded_ratio >= 0.15:
                continue

            unguarded = total - guarded
            mean_complexity = total_complexity / max(1, unguarded)
            score = round(min(1.0, (1.0 - guarded_ratio) * mean_complexity / 20), 3)

            severity = Severity.HIGH if score >= 0.7 else Severity.MEDIUM

            findings.append(
                Finding(
                    signal_type=self.signal_type,
                    severity=severity,
                    score=score,
                    title=f"Guard clause deficit in {module_key}/",
                    description=(
                        f"{unguarded}/{total} public functions lack guard "
                        f"clauses (guarded ratio {guarded_ratio:.1%}, "
                        f"mean unguarded complexity {mean_complexity:.1f})."
                    ),
                    file_path=Path(module_key),
                    fix=(
                        f"Add guard clauses to {unguarded}/{total} unguarded functions in "
                        f"{module_key}/ (mean complexity {mean_complexity:.1f}): "
                        f"isinstance checks, None guards, or assert statements."
                    ),
                    metadata={
                        "total_qualifying": total,
                        "guarded_count": guarded,
                        "guarded_ratio": guarded_ratio,
                        "mean_unguarded_complexity": mean_complexity,
                    },
                )
            )

        return findings


def _read_function_source(
    file_path: Path, fn: FunctionInfo, repo_path: Path | None = None
) -> str | None:
    """Read source lines for a single function."""
    try:
        target = file_path
        if repo_path and not file_path.is_absolute():
            target = repo_path / file_path
        lines = target.read_text(encoding="utf-8").splitlines()
        start = fn.start_line - 1
        end = fn.end_line
        return "\n".join(lines[start:end])
    except (OSError, UnicodeDecodeError, AttributeError):
        return None

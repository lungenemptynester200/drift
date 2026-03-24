"""Resilience tests for disk-backed parse cache."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from drift.cache import ParseCache
from drift.models import ParseResult


def test_file_hash_uses_128_bit_prefix(tmp_path: Path) -> None:
    src = tmp_path / "a.py"
    src.write_text("print('ok')\n", encoding="utf-8")

    h = ParseCache.file_hash(src)
    assert len(h) == 32


def test_get_corrupted_cache_entry_returns_none_and_deletes_file(tmp_path: Path) -> None:
    cache = ParseCache(tmp_path)
    content_hash = "deadbeefdeadbeef"
    cache_file = tmp_path / "parse" / f"{content_hash}.json"
    cache_file.write_text("{not-valid-json", encoding="utf-8")

    result = cache.get(content_hash)

    assert result is None
    assert not cache_file.exists()


def test_put_swallows_oserror_on_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache = ParseCache(tmp_path)
    parse_result = ParseResult(file_path=Path("a.py"), language="python")

    def _raise_oserror(*_args: object, **_kwargs: object) -> str:
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", _raise_oserror)  # type: ignore[attr-defined]

    # Cache failures must never crash analysis.
    cache.put("cafebabecafebabe", parse_result)


def test_concurrent_put_get_does_not_crash(tmp_path: Path) -> None:
    cache = ParseCache(tmp_path)

    def _worker(i: int) -> None:
        h = f"{i:032x}"
        result = ParseResult(file_path=Path(f"f{i}.py"), language="python")
        cache.put(h, result)
        _ = cache.get(h)

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(_worker, range(64)))

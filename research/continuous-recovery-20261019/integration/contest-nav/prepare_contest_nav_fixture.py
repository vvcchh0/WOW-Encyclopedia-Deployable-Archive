"""Prepare a read-only before/after fixture for the contest nav repair."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
if ROOT.name != "WOW_Encyclopedia":
    raise RuntimeError(f"unexpected repository root: {ROOT}")
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import export_github_pages as exporter  # noqa: E402


INTEGRATION_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / ".scratch/pages-resources-20261018-v33"
NAV_ROUTE = "/shared/wow-com/includes-client/navtreefunctions.js"
PAGE_ROUTE = "/contests/05-05-25/winners.html"
FIXTURE_ROOT = INTEGRATION_ROOT / "fixtures"
DERIVED_PATH = FIXTURE_ROOT / "navtreefunctions.derived.js"
BINDINGS_PATH = INTEGRATION_ROOT / "browser-fixture-bindings.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != data:
            raise RuntimeError(f"refusing to overwrite changed fixture: {path}")
        return
    path.write_bytes(data)


def write_json_once(path: Path, value: object) -> None:
    data = (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing == value:
            return
        stable_keys = ("schema", "network_requests", "base_path", "source", "derived", "page")
        if all(existing.get(key) == value.get(key) for key in stable_keys):
            path.write_bytes(data)
            return
        raise RuntimeError(f"refusing to overwrite changed fixture bindings: {path}")
    write_once(path, data)


def main() -> int:
    source_path = OUTPUT_ROOT / NAV_ROUTE.lstrip("/")
    page_path = OUTPUT_ROOT / PAGE_ROUTE.lstrip("/")
    if not source_path.is_file() or not page_path.is_file():
        raise FileNotFoundError("frozen v33 navtree source or contest page is missing")
    source = source_path.read_bytes()
    page = page_path.read_bytes()
    derived_text, changed = exporter.rewrite_contest_navtree_fallback(
        source.decode("utf-8"), base_path=exporter.DEFAULT_BASE_PATH
    )
    if not changed:
        raise RuntimeError("contest fallback did not derive from the frozen source")
    derived = derived_text.encode("utf-8")
    if derived.count(b"offline-contest-nav-fallback-v1") != 1:
        raise RuntimeError("derived fixture marker count is not exactly one")
    if derived.count(b"tree(result);") != 1:
        raise RuntimeError("derived fixture tree target count is not exactly one")

    write_once(DERIVED_PATH, derived)
    bindings = {
        "schema": "contest-nav-browser-fixture-v1",
        "network_requests": 0,
        "base_path": exporter.DEFAULT_BASE_PATH,
        "source": {
            "path": source_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(source),
            "length": len(source),
            "route": NAV_ROUTE,
        },
        "derived": {
            "path": DERIVED_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256(derived),
            "length": len(derived),
            "route": NAV_ROUTE,
            "marker": "offline-contest-nav-fallback-v1",
        },
        "page": {
            "path": page_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(page),
            "length": len(page),
            "route": PAGE_ROUTE,
        },
        "exporter": {
            "path": "tools/export_github_pages.py",
            "sha256": sha256((ROOT / "tools/export_github_pages.py").read_bytes()),
        },
    }
    write_json_once(BINDINGS_PATH, bindings)
    print(json.dumps({"derived": bindings["derived"], "page": bindings["page"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

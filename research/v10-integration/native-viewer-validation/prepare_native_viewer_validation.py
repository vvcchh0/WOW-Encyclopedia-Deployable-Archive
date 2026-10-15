"""Prepare an offline validation artifact from the complete accepted viewer JS.

This script never writes production files.  It imports only the current
exporter helper, verifies the frozen implementation/CSS hashes, rewrites the
entire real 8432-byte source body in memory, and writes the derived source and
provenance below this validation directory.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW_VIEWER = ROOT / "research/continuous-recovery-20261015/network-mixed9/raw/03-screeniesimplified-js-replay-proxy.body"
MIXED9_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/mixed9-acceptance.json"
RECEIPT = ROOT / "research/continuous-recovery-20261015/viewer-derived-fixes/wrath-card-hitarea-011-receipt.json"
EXPORTER = ROOT / "tools/export_github_pages.py"
TESTS = ROOT / "tests/test_github_pages_export.py"
SOURCE_CSS = ROOT / "offline/site/wrath/css/master.css"
DERIVED = OUT / "derived-screeniesimplified.js"

EXPECTED_RAW_SHA256 = "43fe3ee08d5006620a34bb06dcb752e639d0c2fcbe156cdc92c1cb456d209f69"
EXPECTED_RAW_BYTES = 8432

ORIGINAL_FRAGMENT_RE = re.compile(
    r"(?:(?:var|let|const)\s+)?checkForSpecifiedShot\s*=\s*"
    r"window\.location\.href\.split\(\s*\x22s=\x22\s*\)\s*;\s*"
    r"(?:(?:var|let|const)\s+)?nowViewing\s*=\s*"
    r"\(\s*checkForSpecifiedShot\[1\]\s*\)\s*\?\s*"
    r"eval\(\s*checkForSpecifiedShot\[1\]\s*\)\s*:\s*0\s*;",
    re.I,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(path: Path) -> dict[str, object]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_exporter():
    spec = importlib.util.spec_from_file_location("native_viewer_current_exporter", EXPORTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import exporter: {EXPORTER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    raw = RAW_VIEWER.read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    if len(raw) != EXPECTED_RAW_BYTES or raw_sha != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"raw viewer evidence drift: bytes={len(raw)} sha256={raw_sha}")
    acceptance = json.loads(MIXED9_ACCEPTANCE.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if acceptance.get("accepted") is not True or acceptance.get("network_requests_by_acceptance") != 0:
        raise RuntimeError("mixed9 acceptance is not accepted/network-free")
    payload = next((item for item in acceptance.get("payloads") or [] if item.get("target") == "screeniesimplified-js"), None)
    if not payload or payload.get("body_sha256") != EXPECTED_RAW_SHA256 or payload.get("body_bytes") != EXPECTED_RAW_BYTES:
        raise RuntimeError("mixed9 accepted JS payload binding mismatch")
    receipt_scope = receipt.get("scope") or {}
    if receipt_scope.get("network_requests") != 0 or receipt_scope.get("build_export_browser_run") is not False:
        raise RuntimeError("viewer fix receipt is not an offline freeze")

    expected_impl = {item["path"]: item for item in receipt.get("implementation_files") or []}
    current_digests = {
        "exporter": digest(EXPORTER),
        "tests": digest(TESTS),
        "source_css": digest(SOURCE_CSS),
    }
    freeze_match = {
        "exporter": current_digests["exporter"]["sha256"] == expected_impl["tools/export_github_pages.py"]["sha256"] and current_digests["exporter"]["bytes"] == expected_impl["tools/export_github_pages.py"]["bytes"],
        "tests": current_digests["tests"]["sha256"] == expected_impl["tests/test_github_pages_export.py"]["sha256"] and current_digests["tests"]["bytes"] == expected_impl["tests/test_github_pages_export.py"]["bytes"],
        "source_css": current_digests["source_css"]["sha256"] == receipt["source_css_evidence"]["sha256"] and current_digests["source_css"]["bytes"] == receipt["source_css_evidence"]["bytes"],
    }
    if not all(freeze_match.values()):
        raise RuntimeError(f"freeze hash drift: {freeze_match}")

    text = raw.decode("utf-8")
    matches = list(ORIGINAL_FRAGMENT_RE.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one original query fragment, got {len(matches)}")
    match = matches[0]
    exporter = load_exporter()
    derived = exporter.rewrite_wrath_viewer_script(text)
    DERIVED.write_text(derived, encoding="utf-8", newline="")
    derived_match_count = len(ORIGINAL_FRAGMENT_RE.findall(derived))
    source_span = {
        "original_fragment_count": len(matches),
        "original_fragment_span": [match.start(), match.end()],
        "original_fragment_sha256": hashlib.sha256(match.group(0).encode("utf-8")).hexdigest(),
        "prefix_unchanged": derived[:match.start()] == text[:match.start()],
        "suffix_unchanged": derived.endswith(text[match.end():]),
        "original_eval_fragment_removed": derived_match_count == 0,
        "derived_url_search_params_count": derived.count('new URLSearchParams(window.location.search).getAll("s")'),
        "derived_safe_integer_check_count": derived.count("Number.isSafeInteger(parsedShot)"),
        "derived_omega_entry_count": derived.count("omegaLightBox(nowViewing-1);"),
        "derived_eval_count": len(re.findall(r"\beval\s*\(", derived)),
    }
    navigation_symbols = [
        "function prevScreen() {nextScreenshot();}",
        "function nextScreen() {prevScreenshot();}",
        "function nextScreenshot() { if(!animationLock) slideShowNextFader(); }",
        "function prevScreenshot() { if(!animationLock) slideShowPrevFader(); }",
    ]
    source_span["navigation_symbols_unchanged"] = all(symbol in text and symbol in derived for symbol in navigation_symbols)
    source_span["navigation_symbol_hashes"] = {
        symbol: {
            "original": hashlib.sha256(symbol.encode("utf-8")).hexdigest(),
            "derived": hashlib.sha256(symbol.encode("utf-8")).hexdigest(),
        }
        for symbol in navigation_symbols
    }
    required = {
        "prefix_unchanged": True,
        "suffix_unchanged": True,
        "original_eval_fragment_removed": True,
        "derived_url_search_params_count": 1,
        "derived_safe_integer_check_count": 1,
        "derived_omega_entry_count": 1,
        "derived_eval_count": 0,
        "navigation_symbols_unchanged": True,
    }
    for key, expected in required.items():
        if source_span.get(key) != expected:
            raise RuntimeError(f"derived source contract failed: {key}={source_span.get(key)!r}")

    provenance = {
        "schema": "native-viewer-vm-012-provenance/v1",
        "batch_id": "NATIVE-VIEWER-VM-012",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "network_requests": 0,
        "simulation": True,
        "inputs": {
            "mixed9_acceptance": {"path": str(MIXED9_ACCEPTANCE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(MIXED9_ACCEPTANCE), "accepted": acceptance.get("accepted"), "network_requests_by_acceptance": acceptance.get("network_requests_by_acceptance")},
            "raw_viewer": {**digest(RAW_VIEWER), "actual_memento": payload.get("actual_memento"), "captured_original_url": payload.get("captured_original_url")},
            "viewer_fix_receipt": {"path": str(RECEIPT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(RECEIPT), "schema": receipt.get("schema"), "network_requests": receipt_scope.get("network_requests"), "build_export_browser_run": receipt_scope.get("build_export_browser_run")},
        },
        "freeze": {"receipt_implementation_files": expected_impl, "current_digests": current_digests, "match": freeze_match},
        "source_transform": source_span,
        "derived": digest(DERIVED),
        "scope": "real complete accepted JS converted with current exporter helper; no synthetic parser fixture; no production write",
    }
    write_json(OUT / "source-validation.json", provenance)
    print(json.dumps({"mode": "offline_prepare", "network_requests": 0, "raw_bytes": len(raw), "raw_sha256": raw_sha, "derived": provenance["derived"], "freeze_match": freeze_match, "source_span": source_span}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

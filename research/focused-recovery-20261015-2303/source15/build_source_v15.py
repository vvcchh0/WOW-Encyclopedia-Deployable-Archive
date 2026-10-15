#!/usr/bin/env python3
"""Prepare or, only with explicit --build --go, build the one-entity v15 source mirror.

The default operation is preparation only. It reuses the accepted v14
offline_mirror argv, preserves the v14 source/alias/overlay baseline, and
waits for one root-accepted Aug07 source map before any fresh output is made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OWN = ROOT / "research" / "focused-recovery-20261015-2303" / "source15"
V14_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v14"
V15_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v15"
V14_MANIFEST = V14_DIR / "build-manifest.json"
V14_PLAN = ROOT / "research" / "v14-integration" / "source" / "v14-source-plan.json"
V14_RECEIPT = ROOT / "research" / "v14-integration" / "source" / "v14-source-receipt.json"
V14_BUILDER = ROOT / "research" / "v14-integration" / "source" / "build_source_v14.py"
FROZEN = ROOT / "offline" / "build-manifest.json"
ADDITIONS = OWN / "v15-additions-source-map.json"
PLAN = OWN / "v15-source-plan.json"
RECEIPT = OWN / "v15-source-receipt.json"

V14_MANIFEST_SHA = "fb4c7c2e3fd4d421c6894fe90d4bc926dbbe6bb90147dfed9d3a93a8865e54d8"
V14_PLAN_SHA = "deeb03d8d8f2fe479d0cfeea6b386505bc30c584b15df803841d612f4edf10b1"
V14_RECEIPT_SHA = "5e6fdf20eef8cfb4d27c36f1d1eec47dcd336f8dee13b6ddaa4a53b62a7c045f"
FROZEN_SHA = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
V14_COUNT = 8356
V15_COUNT = 8357
ALIAS_COUNT = 183
OVERLAY_COUNT = 38


class AdapterError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def base_guard():
    for path, expected in ((V14_MANIFEST, V14_MANIFEST_SHA), (V14_PLAN, V14_PLAN_SHA), (V14_RECEIPT, V14_RECEIPT_SHA), (FROZEN, FROZEN_SHA)):
        actual = sha(path)
        if actual != expected:
            raise AdapterError(f"baseline SHA changed: {rel(path)} {actual}")
    manifest = load(V14_MANIFEST)
    if len(manifest.get("files") or []) != V14_COUNT or len(manifest.get("route_aliases") or {}) != ALIAS_COUNT:
        raise AdapterError("v14 manifest count/alias baseline mismatch")
    return manifest


def v15_argv() -> list[str]:
    plan = load(V14_PLAN)
    argv = plan.get("build_argv")
    if not isinstance(argv, list) or not argv:
        raise AdapterError("v14 plan has no recorded build argv")
    result = [str(x).replace(".scratch/offline-navigation-20261015-v14", ".scratch/offline-navigation-20261015-v15") for x in argv]
    result.extend(["--extra-map", rel(ADDITIONS)])
    return result


def prepare() -> dict:
    manifest = base_guard()
    argv = v15_argv()
    plan = {
        "schema": "wow-recovery.core-source-v15-plan.v1",
        "status": "prepared_pending_root_accepted_aug07_source_and_explicit_go",
        "generated_utc": now(),
        "network_performed": False,
        "adapter": {"path": rel(Path(__file__)), "sha256": sha(Path(__file__))},
        "baseline": {
            "manifest": {"path": rel(V14_MANIFEST), "sha256": V14_MANIFEST_SHA, "source_records": V14_COUNT},
            "plan": {"path": rel(V14_PLAN), "sha256": V14_PLAN_SHA},
            "receipt": {"path": rel(V14_RECEIPT), "sha256": V14_RECEIPT_SHA},
            "aliases": ALIAS_COUNT,
            "overlay_recipes": OVERLAY_COUNT,
        },
        "selected_source": {"status": "pending_root_accepted_map", "path": None, "entry_count": 1},
        "expected_counts": {"prior_v14": V14_COUNT, "new": 1, "v15": V15_COUNT},
        "output": {"site": rel(V15_DIR / "site"), "manifest": rel(V15_DIR / "build-manifest.json"), "support": rel(V15_DIR / "support")},
        "additions_map": {"path": rel(ADDITIONS), "status": "not_created_until_accepted_map"},
        "build_argv_template": argv,
        "route_policy": "Use only accepted map proposed_route/target; do not guess an Aug07 route or alias. Preserve every v14 route and alias; root owns export/ZIP/browser.",
        "source_guard": "No production/source/raw/frozen v14 files are copied or rewritten during preparation. Build is refused without --go and one accepted selected map.",
    }
    write(PLAN, plan)
    return plan


def selected_entries(path: Path) -> list[dict]:
    value = load(path)
    if value.get("accepted") is False:
        raise AdapterError("selected map is not accepted")
    entries = value.get("entries") or value.get("items")
    if not isinstance(entries, list):
        entries = [value] if value.get("local_path") else []
    if len(entries) != 1:
        raise AdapterError(f"expected exactly one accepted Aug07 entry, got {len(entries)}")
    entry = entries[0]
    body = ROOT / str(entry.get("local_path") or "")
    headers = ROOT / str(entry.get("headers_local_path") or "")
    if not body.is_file() or not headers.is_file():
        raise AdapterError("accepted map body/header is missing")
    body_sha = sha(body)
    body_bytes = body.stat().st_size
    if body_sha != entry.get("body_sha256") or body_bytes != int(entry.get("body_bytes") or -1):
        raise AdapterError("accepted map body SHA/length mismatch")
    route = str(entry.get("proposed_route") or entry.get("target") or "")
    if not route.startswith("/"):
        raise AdapterError("accepted map must provide a leading-slash proposed_route/target")
    return [dict(entry, _body=body, _headers=headers, _route=route, _body_sha=body_sha, _body_bytes=body_bytes)]


def additions_map(selected_path: Path, entries: list[dict]) -> dict:
    mapped = []
    for entry in entries:
        body = entry["_body"]
        headers = entry["_headers"]
        logical = str(entry.get("logical_url") or entry.get("source_url") or entry.get("captured_original_url") or "")
        route = entry["_route"]
        item = {
            "logical_url": logical,
            "source_url": logical,
            "source_base_url": logical,
            "captured_original": entry.get("captured_original_url") or logical,
            "query_original_url": entry.get("query_original_url") or logical,
            "captured_original_url": entry.get("captured_original_url") or logical,
            "local_path": rel(body),
            "sha256": entry["_body_sha"],
            "content_length": entry["_body_bytes"],
            "actual_timestamp": entry.get("actual_timestamp"),
            "actual_memento": entry.get("actual_memento"),
            "derived_route": route,
            "route_aliases": [],
            "mime": entry.get("mime") or entry.get("content_type") or "text/html",
            "kind": "html",
            "role": entry.get("role") or "historical_news_aug07",
            "source_role": entry.get("role") or "historical_news_aug07",
            "temporal_class": "pre_anchor_historical_capture",
            "source_status": 200,
            "raw_body_path": rel(body),
            "raw_headers_path": rel(headers),
            "headers_local_path": rel(headers),
            "source_selection": "root_accepted_aug07_single_entity",
            "source_entities_unmodified": True,
            "cdx_digest": entry.get("cdx_digest"),
            "source_evidence": {"selected_input": rel(selected_path), "body_sha256": entry["_body_sha"], "body_bytes": entry["_body_bytes"], "raw_body_path": rel(body), "raw_headers_path": rel(headers)},
            "selection_provenance": {k: v for k, v in entry.items() if not k.startswith("_")},
        }
        mapped.append(item)
    return {"schema_version": "wow-recovery.core-source-v15-additions-map.v1", "status": "accepted_single_aug07_primary", "generated_utc": now(), "network_performed": False, "entry_count": 1, "selected_route_count": 1, "expected_prior_v14_source_records": V14_COUNT, "expected_v15_source_records": V15_COUNT, "entries": mapped, "files": mapped, "selected_input": {"path": rel(selected_path), "sha256": sha(selected_path)}}


def build(selected_path: Path, go: bool) -> dict:
    if not go:
        raise AdapterError("build requires explicit --go")
    base_manifest = base_guard()
    if V15_DIR.exists() or ADDITIONS.exists() or RECEIPT.exists():
        raise AdapterError("refusing to overwrite existing v15 output/artifacts")
    entries = selected_entries(selected_path)
    write(ADDITIONS, additions_map(selected_path, entries))
    support_src = V14_DIR / "support"
    support_dst = V15_DIR / "support"
    if support_src.is_dir():
        shutil.copytree(support_src, support_dst)
    argv = v15_argv()
    completed = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if completed.returncode != 0:
        raise AdapterError(f"offline_mirror failed: {completed.returncode}: {completed.stderr[-4000:]}")
    manifest = load(V15_DIR / "build-manifest.json")
    if len(manifest.get("files") or []) != V15_COUNT or len(manifest.get("route_aliases") or {}) != ALIAS_COUNT:
        raise AdapterError("v15 output count/alias mismatch")
    if sha(V14_MANIFEST) != V14_MANIFEST_SHA or sha(FROZEN) != FROZEN_SHA:
        raise AdapterError("v14 or frozen baseline changed during v15 build")
    receipt = {"schema": "wow-recovery.core-source-v15-receipt.v1", "status": "mirror_only_pending_root_export", "generated_utc": now(), "network_requests": 0, "source_count": {"prior_v14": V14_COUNT, "new": 1, "v15": V15_COUNT}, "selected_input": {"path": rel(selected_path), "sha256": sha(selected_path)}, "additions_map": {"path": rel(ADDITIONS), "sha256": sha(ADDITIONS)}, "baseline": {"manifest": {"path": rel(V14_MANIFEST), "sha256_before": V14_MANIFEST_SHA, "sha256_after": sha(V14_MANIFEST)}, "aliases": ALIAS_COUNT, "overlays_pending_root_export": OVERLAY_COUNT}, "output": {"manifest": rel(V15_DIR / "build-manifest.json"), "manifest_sha256": sha(V15_DIR / "build-manifest.json"), "source_records": len(manifest.get("files") or [])}, "build": {"argv": argv, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}}
    write(RECEIPT, receipt)
    return {"result": "PASS", "receipt": rel(RECEIPT), "source_records": V15_COUNT, "network_requests": 0}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--selected-map")
    args = parser.parse_args()
    if not args.build:
        print(json.dumps(prepare(), ensure_ascii=False))
        return 0
    if not args.selected_map:
        raise AdapterError("--build requires --selected-map")
    print(json.dumps(build((ROOT / args.selected_map).resolve(), args.go), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AdapterError as exc:
        print(f"build_source_v15: {exc}", file=sys.stderr)
        raise SystemExit(1)

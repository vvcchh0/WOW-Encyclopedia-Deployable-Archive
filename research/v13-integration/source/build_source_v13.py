#!/usr/bin/env python3
"""Build the bounded local-only v13 source mirror from the accepted v12 mirror.

This adapter deliberately reuses the recorded v12 offline_mirror command.  It
only stages the three accepted NET018 entities, redirects output to a fresh
v13 scratch directory, and records source-only provenance for root export.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RECOVERY = ROOT / "research" / "continuous-recovery-20261015"
OWN_DIR = ROOT / "research" / "v13-integration" / "source"
V12_SOURCE_DIR = ROOT / "research" / "v12-integration" / "source"
V12_PLAN = V12_SOURCE_DIR / "v12-source-plan.json"
V12_RECEIPT = V12_SOURCE_DIR / "v12-source-receipt.json"
V12_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v12"
V13_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v13"
V12_MANIFEST = V12_DIR / "build-manifest.json"
V13_MANIFEST = V13_DIR / "build-manifest.json"
V13_SITE = V13_DIR / "site"
V13_SUPPORT = V13_DIR / "support"
FROZEN_MANIFEST = ROOT / "offline" / "build-manifest.json"
SELECTED = RECOVERY / "selected-rss18-source-map.json"
ACCEPTANCE = RECOVERY / "rss18-acceptance.json"
ADDITIONS_MAP = OWN_DIR / "v13-additions-source-map.json"
PLAN = OWN_DIR / "v13-source-plan.json"
RECEIPT = OWN_DIR / "v13-source-receipt.json"

EXPECTED_SELECTED_SHA = "e3af3c2c9cb8c40b96bd5a6964d32faac92d4a2e6da158bcb34ad9b59313c591"
EXPECTED_ACCEPTANCE_SHA = "e5ed5e6ada59892ef211442eac60e8378742f8e3c95b9533188a8da0f290ca74"
EXPECTED_V12_PLAN_SHA = "f25c17fcfeb313f8b4930d3d62f8889a719985bde2e59276766a684a571dc573"
EXPECTED_V12_RECEIPT_SHA = "5b935a587487e6eaa25a2ea662710b57fd3a17a3fa72afa2589791591e8c95c1"
EXPECTED_V12_MANIFEST_SHA = "590f06cf30266d0b6fc02a365d9810a564693e9dd67e3051572bfc414a570b16"
EXPECTED_FROZEN_SHA = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
EXPECTED_V12_COUNT = 8344
EXPECTED_V13_COUNT = 8347
EXPECTED_ALIAS_COUNT = 183
EXPECTED_OVERLAY_COUNT = 38
ANCHOR = "20080512210044"


class SourceBuildError(RuntimeError):
    pass


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SourceBuildError(f"JSON root is not an object: {rel(path)}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def root_path(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise SourceBuildError(f"missing {field}")
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SourceBuildError(f"{field} escapes workspace: {value}") from exc
    return path


def header_evidence(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"^HTTP/\d(?:\.\d)?\s+200\s+OK\s*$", text, re.I | re.M):
        raise SourceBuildError(f"staged response is not HTTP 200: {rel(path)}")
    match = re.search(r"^memento-datetime:\s*(.+?)\s*$", text, re.I | re.M)
    parsed = parsedate_to_datetime(match.group(1)) if match else None
    return {
        "http_status": 200,
        "memento_header": parsed.isoformat() if parsed else None,
        "header_sha256": sha256_file(path),
        "header_bytes": path.stat().st_size,
    }


def capture_datetime(value: str) -> datetime:
    text = str(value or "").strip()
    if not re.fullmatch(r"\d{14}", text):
        raise SourceBuildError(f"invalid actual_timestamp: {value}")
    return datetime.strptime(text, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def validate_inputs() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    for path, expected in (
        (SELECTED, EXPECTED_SELECTED_SHA),
        (ACCEPTANCE, EXPECTED_ACCEPTANCE_SHA),
        (V12_PLAN, EXPECTED_V12_PLAN_SHA),
        (V12_RECEIPT, EXPECTED_V12_RECEIPT_SHA),
        (V12_MANIFEST, EXPECTED_V12_MANIFEST_SHA),
        (FROZEN_MANIFEST, EXPECTED_FROZEN_SHA),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise SourceBuildError(f"input SHA changed: {rel(path)}: {actual}")
    selected = load_json(SELECTED)
    acceptance = load_json(ACCEPTANCE)
    entries = selected.get("entries")
    if selected.get("entry_count") != 3 or not isinstance(entries, list) or len(entries) != 3:
        raise SourceBuildError("selected rss18 map must contain exactly three entries")
    accepted_by_target = {
        str(item.get("target") or item.get("route")): item
        for item in acceptance.get("entities", [])
        if isinstance(item, dict)
    }
    additions: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    routes: set[str] = set()
    for selected_entry in entries:
        if not isinstance(selected_entry, dict):
            raise SourceBuildError("selected entity is not an object")
        body = root_path(selected_entry.get("local_path"), "local_path")
        headers = root_path(selected_entry.get("headers_local_path"), "headers_local_path")
        if not body.is_file() or not headers.is_file():
            raise SourceBuildError(f"missing accepted body/header for {selected_entry.get('logical_url')}")
        actual_bytes = body.stat().st_size
        actual_sha = sha256_file(body)
        if actual_bytes != int(selected_entry.get("body_bytes") or -1) or actual_sha != selected_entry.get("body_sha256"):
            raise SourceBuildError(f"accepted body SHA/length mismatch: {rel(body)}")
        logical = str(selected_entry.get("logical_url") or "")
        target = str(selected_entry.get("target") or selected_entry.get("proposed_route") or "")
        accepted = accepted_by_target.get(target)
        if not accepted or accepted.get("sha256") != actual_sha or int(accepted.get("bytes") or -1) != actual_bytes:
            raise SourceBuildError(f"acceptance does not bind exact body: {target or logical}")
        timestamp = capture_datetime(str(selected_entry.get("actual_timestamp") or ""))
        memento = str(selected_entry.get("actual_memento") or "")
        if timestamp.isoformat() != memento.replace("Z", "+00:00"):
            raise SourceBuildError(f"timestamp/memento mismatch: {logical}")
        if timestamp >= capture_datetime(ANCHOR):
            raise SourceBuildError(f"non-pre-anchor entity selected: {logical}")
        headers_meta = header_evidence(headers)
        route = str(selected_entry.get("proposed_route") or "")
        if not route.startswith("/") or route in routes:
            raise SourceBuildError(f"invalid or duplicate route: {route}")
        routes.add(route)
        suffix = Path(route).suffix.casefold()
        kind = "css" if suffix == ".css" else "image" if suffix in {".gif", ".jpg", ".jpeg", ".png", ".webp"} else "other"
        role = str(selected_entry.get("role") or "historical_news_asset")
        map_entry: dict[str, Any] = {
            "logical_url": logical,
            "source_url": logical,
            "source_base_url": logical,
            "captured_original": selected_entry.get("captured_original_url") or logical,
            "query_original_url": selected_entry.get("query_original_url") or logical,
            "captured_original_url": selected_entry.get("captured_original_url") or logical,
            "local_path": selected_entry["local_path"],
            "sha256": actual_sha,
            "content_length": actual_bytes,
            "actual_timestamp": selected_entry["actual_timestamp"],
            "actual_memento": selected_entry["actual_memento"],
            "derived_route": route,
            "route_aliases": [],
            "mime": selected_entry.get("mime"),
            "kind": kind,
            "role": role,
            "source_role": role,
            "temporal_class": "pre_anchor_historical_capture",
            "source_status": 200,
            "raw_body_path": selected_entry["local_path"],
            "raw_headers_path": selected_entry["headers_local_path"],
            "headers_local_path": selected_entry["headers_local_path"],
            "source_batch": Path(str(selected_entry["local_path"])).parts[-3],
            "source_selection": "accepted_selected_rss18_preanchor",
            "source_entities_unmodified": True,
            "cdx_digest": selected_entry.get("cdx_digest"),
            "source_group": selected_entry.get("source_group"),
            "temporal_status": selected_entry.get("temporal_status"),
            "source_evidence": {
                "selected_input": rel(SELECTED),
                "acceptance": rel(ACCEPTANCE),
                "logical_url": logical,
                "captured_original_url": selected_entry.get("captured_original_url"),
                "body_sha256": actual_sha,
                "body_bytes": actual_bytes,
                "raw_body_path": selected_entry["local_path"],
                "raw_headers_path": selected_entry["headers_local_path"],
                "actual_timestamp": selected_entry["actual_timestamp"],
                "actual_memento": selected_entry["actual_memento"],
                "header_evidence": headers_meta,
            },
            "selection_provenance": selected_entry,
        }
        additions.append(map_entry)
        evidence.append(
            {
                "logical_url": logical,
                "route": route,
                "body_path": rel(body),
                "headers_path": rel(headers),
                "body_bytes": actual_bytes,
                "body_sha256": actual_sha,
                "actual_timestamp": selected_entry["actual_timestamp"],
                "actual_memento": selected_entry["actual_memento"],
                "http_status": 200,
                **headers_meta,
                "mime": selected_entry.get("mime"),
                "role": role,
            }
        )
    return selected, additions, evidence


def write_additions_map(selected: dict[str, Any], additions: list[dict[str, Any]]) -> dict[str, Any]:
    result = {
        "schema_version": "wow-recovery.core-source-v13-additions-map.v1",
        "status": "accepted_selected_rss18_expanded_html_primary_source_only",
        "generated_utc": now_utc(),
        "network_performed": False,
        "network_note": "No network request was made; all three expanded HTML bodies and headers were already staged and hash-validated.",
        "anchor_timestamp": ANCHOR,
        "entry_count": len(additions),
        "selected_target_count": len(additions),
        "selected_route_count": len({str(item["derived_route"]) for item in additions}),
        "expected_v12_source_records": EXPECTED_V12_COUNT,
        "expected_v13_source_records": EXPECTED_V13_COUNT,
        "entries": additions,
        "files": additions,
        "selected_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "acceptance_input": {"path": rel(ACCEPTANCE), "sha256": sha256_file(ACCEPTANCE)},
        "integration_policy": "Fresh v13 source mirror only; these are accepted primary expanded HTML entities, not late overlays; root owns Pages export and 38-overlay application.",
        "raw_entities_preserved": True,
    }
    write_json(ADDITIONS_MAP, result)
    return result


def v12_command(plan: dict[str, Any]) -> list[str]:
    original = plan.get("build_argv")
    if not isinstance(original, list) or not original:
        raise SourceBuildError("v12 plan has no recorded build_argv")
    command = [
        str(item).replace(
            ".scratch/offline-navigation-20261015-v12",
            ".scratch/offline-navigation-20261015-v13",
        )
        for item in original
    ]
    command.extend(["--extra-map", rel(ADDITIONS_MAP)])
    return command


def support_copy() -> list[dict[str, Any]]:
    source_support = V12_DIR / "support"
    if not source_support.is_dir():
        raise SourceBuildError("v12 support directory missing")
    V13_SUPPORT.mkdir(parents=True, exist_ok=False)
    migrations: list[dict[str, Any]] = []
    for name in ("compat.css", "compat.js"):
        source = source_support / name
        target = V13_SUPPORT / name
        if not source.is_file():
            raise SourceBuildError(f"v12 support file missing: {rel(source)}")
        shutil.copy2(source, target)
        migrations.append(
            {
                "route": "/__offline/" + name,
                "old_source_local_path": rel(source),
                "new_source_local_path": rel(target),
                "source_length": target.stat().st_size,
                "old_sha256": sha256_file(source),
                "new_sha256": sha256_file(target),
                "content_hash_preserved": sha256_file(source) == sha256_file(target),
            }
        )
    return migrations


def run_build(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    result = {"argv": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    if completed.returncode != 0:
        raise SourceBuildError(f"offline_mirror failed ({completed.returncode}): {completed.stderr[-6000:]}")
    return result


def validate_output(additions: list[dict[str, Any]], before_v12: str, before_frozen: str, support_migrations: list[dict[str, Any]], build: dict[str, Any]) -> dict[str, Any]:
    if not V13_MANIFEST.is_file() or not V13_SITE.is_dir():
        raise SourceBuildError("v13 output is incomplete")
    manifest = load_json(V13_MANIFEST)
    files = manifest.get("files") or []
    by_route = {str(item.get("route")): item for item in files if item.get("route")}
    if len(files) != EXPECTED_V13_COUNT or len(by_route) != EXPECTED_V13_COUNT:
        raise SourceBuildError(f"v13 source count mismatch: files={len(files)} routes={len(by_route)}")
    stats = manifest.get("stats") or {}
    if stats.get("derived_files") != EXPECTED_V13_COUNT or stats.get("routes") != EXPECTED_V13_COUNT:
        raise SourceBuildError(f"v13 stats mismatch: {stats}")
    v12_manifest = load_json(V12_MANIFEST)
    old_aliases = v12_manifest.get("route_aliases") or {}
    new_aliases = manifest.get("route_aliases") or {}
    if len(old_aliases) != EXPECTED_ALIAS_COUNT or len(new_aliases) != EXPECTED_ALIAS_COUNT:
        raise SourceBuildError(f"alias count mismatch: v12={len(old_aliases)} v13={len(new_aliases)}")
    if old_aliases != {key: new_aliases.get(key) for key in old_aliases}:
        raise SourceBuildError("v12 aliases changed in v13")
    added_routes: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for addition in additions:
        route = str(addition["derived_route"])
        record = by_route.get(route)
        if record is None:
            mismatches.append(route + ":missing_manifest_record")
            continue
        for key, expected in (
            ("source_sha256", addition["sha256"]),
            ("source_length", addition["content_length"]),
            ("source_base_url", addition["source_base_url"]),
            ("actual_timestamp", addition["actual_timestamp"]),
            ("mime", addition["mime"]),
            ("kind", addition["kind"]),
            ("role", addition["role"]),
        ):
            if record.get(key) != expected:
                mismatches.append(f"{route}:{key}")
        output = root_path(record.get("output_path"), f"{route}.output_path")
        source = root_path(addition["local_path"], f"{route}.local_path")
        if not output.is_file():
            mismatches.append(route + ":derived_missing")
        added_routes.append(
            {
                "route": route,
                "logical_url": addition["logical_url"],
                "source_path": rel(source),
                "source_bytes": source.stat().st_size,
                "source_sha256": sha256_file(source),
                "derived_path": rel(output) if output.is_file() else None,
                "derived_bytes": output.stat().st_size if output.is_file() else None,
                "derived_sha256": sha256_file(output) if output.is_file() else None,
                "actual_timestamp": addition["actual_timestamp"],
                "actual_memento": addition["actual_memento"],
                "header_path": addition["raw_headers_path"],
                "header_sha256": sha256_file(root_path(addition["raw_headers_path"], f"{route}.raw_headers_path")),
                "mime": addition["mime"],
                "role": addition["role"],
            }
        )
    if mismatches:
        raise SourceBuildError("v13 additions mismatch: " + ", ".join(mismatches))
    after_v12 = sha256_file(V12_MANIFEST)
    after_frozen = sha256_file(FROZEN_MANIFEST)
    if before_v12 != after_v12 or before_frozen != after_frozen:
        raise SourceBuildError("v12 or frozen manifest changed during v13 build")
    return {
        "v13_manifest_sha256": sha256_file(V13_MANIFEST),
        "v13_manifest_bytes": V13_MANIFEST.stat().st_size,
        "v13_source_records": len(files),
        "v13_route_records": len(by_route),
        "v13_alias_count": len(new_aliases),
        "added_routes": added_routes,
        "stats": stats,
        "support_path_migrations": support_migrations,
        "v12_manifest_before_sha256": before_v12,
        "v12_manifest_after_sha256": after_v12,
        "frozen_manifest_before_sha256": before_frozen,
        "frozen_manifest_after_sha256": after_frozen,
        "build_returncode": build["returncode"],
    }


def main() -> int:
    if ADDITIONS_MAP.exists() or PLAN.exists() or RECEIPT.exists() or V13_DIR.exists():
        raise SystemExit("refusing to overwrite existing v13 source artifacts")
    selected, additions, evidence = validate_inputs()
    v12_plan = load_json(V12_PLAN)
    before_v12 = sha256_file(V12_MANIFEST)
    before_frozen = sha256_file(FROZEN_MANIFEST)
    disk_before = shutil.disk_usage(ROOT)
    write_additions_map(selected, additions)
    support_migrations = support_copy()
    command = v12_command(v12_plan)
    plan = {
        "schema": "wow-recovery.core-source-v13-plan.v1",
        "status": "prepared_source_only_pending_build",
        "generated_utc": now_utc(),
        "network_performed": False,
        "source_selection": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED), "entry_count": len(additions)},
        "acceptance": {"path": rel(ACCEPTANCE), "sha256": sha256_file(ACCEPTANCE)},
        "v12_inputs": {
            "plan": {"path": rel(V12_PLAN), "sha256": sha256_file(V12_PLAN)},
            "receipt": {"path": rel(V12_RECEIPT), "sha256": sha256_file(V12_RECEIPT)},
            "manifest": {"path": rel(V12_MANIFEST), "sha256": before_v12, "source_records": EXPECTED_V12_COUNT},
        },
        "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256": before_frozen},
        "additions_map": {"path": rel(ADDITIONS_MAP), "sha256": sha256_file(ADDITIONS_MAP), "entry_count": len(additions)},
        "expected_counts": {"v12": EXPECTED_V12_COUNT, "new": len(additions), "v13": EXPECTED_V13_COUNT},
        "expected_alias_count": EXPECTED_ALIAS_COUNT,
        "expected_overlay_recipes": EXPECTED_OVERLAY_COUNT,
        "output": {"site": rel(V13_SITE), "manifest": rel(V13_MANIFEST), "support": rel(V13_SUPPORT)},
        "build_argv": command,
        "route_evidence": evidence,
        "support_path_migrations": support_migrations,
        "disk_free_before_bytes": disk_before.free,
        "source_guard": "Use the accepted v12 plan/manifest as the old-source identity baseline; run only tools/offline_mirror.py with the v13 additions map.",
    }
    write_json(PLAN, plan)
    build = run_build(command)
    validation = validate_output(additions, before_v12, before_frozen, support_migrations, build)
    disk_after = shutil.disk_usage(ROOT)
    plan.update({"status": "mirror_built_pending_root_export", "build_returncode": build["returncode"], "build_stdout": build["stdout"], "build_stderr": build["stderr"], "validation": validation, "disk_free_after_bytes": disk_after.free, "completed_utc": now_utc()})
    write_json(PLAN, plan)
    receipt = {
        "schema": "wow-recovery.core-source-v13-receipt.v1",
        "status": "mirror_only_pending_root_export",
        "generated_utc": now_utc(),
        "network_requests": 0,
        "source_count": {"prior_v12": EXPECTED_V12_COUNT, "new": len(additions), "v13": EXPECTED_V13_COUNT},
        "selected_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "acceptance_input": {"path": rel(ACCEPTANCE), "sha256": sha256_file(ACCEPTANCE)},
        "additions_map": {"path": rel(ADDITIONS_MAP), "sha256": sha256_file(ADDITIONS_MAP)},
        "plan": {"path": rel(PLAN), "sha256": sha256_file(PLAN)},
        "v12_inputs": {
            "plan": {"path": rel(V12_PLAN), "sha256": sha256_file(V12_PLAN)},
            "receipt": {"path": rel(V12_RECEIPT), "sha256": sha256_file(V12_RECEIPT)},
            "manifest_before_sha256": before_v12,
            "manifest_after_sha256": sha256_file(V12_MANIFEST),
            "source_records_preserved": EXPECTED_V12_COUNT,
        },
        "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256_before": before_frozen, "sha256_after": sha256_file(FROZEN_MANIFEST), "unchanged": before_frozen == sha256_file(FROZEN_MANIFEST)},
        "v13_output": {"site": rel(V13_SITE), "manifest": rel(V13_MANIFEST), "manifest_sha256": validation["v13_manifest_sha256"], "manifest_bytes": validation["v13_manifest_bytes"], "source_records": validation["v13_source_records"]},
        "added_routes": validation["added_routes"],
        "aliases": {"prior_v12": EXPECTED_ALIAS_COUNT, "v13": validation["v13_alias_count"], "preserved": validation["v13_alias_count"] == EXPECTED_ALIAS_COUNT},
        "overlay_recipe": {"accepted_count": EXPECTED_OVERLAY_COUNT, "applied_in_source_phase": False, "pending_root_export": True},
        "support_path_migrations": validation["support_path_migrations"],
        "build": {"argv": command, "returncode": build["returncode"], "stdout": build["stdout"], "stderr": build["stderr"], "stats": validation["stats"]},
        "disk_free": {"before_bytes": disk_before.free, "after_bytes": disk_after.free},
        "retention": {"raw_entities": "Preserved at the original RSS018 raw paths; no body copy was made in v13 output.", "derived_entities": "Three derived routes retain exact source SHA/length and are recorded in added_routes.", "old_source_identity": "All 8344 v12 source records are carried forward by the accepted v12 build maps."},
        "policies": {"new_entities": "accepted primary pre-anchor source entities, not late overlays", "network": "local staged bodies/headers only", "export": "root-owned; no Pages/export/ZIP performed"},
    }
    write_json(RECEIPT, receipt)
    print(json.dumps({"result": "PASS", "status": receipt["status"], "prior_v12": EXPECTED_V12_COUNT, "new": len(additions), "v13": EXPECTED_V13_COUNT, "v13_manifest_sha256": validation["v13_manifest_sha256"], "v12_manifest_unchanged": before_v12 == sha256_file(V12_MANIFEST), "frozen_manifest_unchanged": before_frozen == sha256_file(FROZEN_MANIFEST), "network_requests": 0, "receipt": rel(RECEIPT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SourceBuildError as exc:
        print(f"build_source_v13: {exc}", file=sys.stderr)
        raise SystemExit(1)

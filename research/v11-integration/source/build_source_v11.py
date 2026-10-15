#!/usr/bin/env python3
"""Build the bounded local-only v11 source mirror from the accepted v10 mirror.

This adapter deliberately reuses the recorded v10 offline_mirror command.  It
only stages the three accepted NET013 entities, redirects output to a fresh
v11 scratch directory, and records source-only provenance for root export.
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
OWN_DIR = ROOT / "research" / "v11-integration" / "source"
V10_SOURCE_DIR = ROOT / "research" / "v10-integration" / "source"
V10_PLAN = V10_SOURCE_DIR / "v10-source-plan.json"
V10_RECEIPT = V10_SOURCE_DIR / "v10-source-receipt.json"
V10_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v10"
V11_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v11"
V10_MANIFEST = V10_DIR / "build-manifest.json"
V11_MANIFEST = V11_DIR / "build-manifest.json"
V11_SITE = V11_DIR / "site"
V11_SUPPORT = V11_DIR / "support"
FROZEN_MANIFEST = ROOT / "offline" / "build-manifest.json"
SELECTED = RECOVERY / "selected-news-assets13-source-map.json"
ACCEPTANCE = RECOVERY / "news-assets13-acceptance.json"
ADDITIONS_MAP = OWN_DIR / "v11-additions-source-map.json"
PLAN = OWN_DIR / "v11-source-plan.json"
RECEIPT = OWN_DIR / "v11-source-receipt.json"

EXPECTED_SELECTED_SHA = "08f6e4bfc836eb56c4704c6f23582f1bc3f37a4d985d2dbde66ac281f649b8a3"
EXPECTED_ACCEPTANCE_SHA = "e9748d3a9f7a5d2483766262856c621fbfa05a8a2bb58d3ebd77b51161e5099c"
EXPECTED_V10_PLAN_SHA = "12aadc1925cc51f069084e5180a21168df3fbf22bb2e3358d89ba98037d9ee5f"
EXPECTED_V10_RECEIPT_SHA = "23b7e5cdfc9b26aea42e7fe8840670adb38c29d8e6e0486cb298a65911006cd5"
EXPECTED_V10_MANIFEST_SHA = "bc664a728da4bb6c5a49b2c2d46bc2837e2ae40e8a09f6e59c6dc755caa83d86"
EXPECTED_FROZEN_SHA = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
EXPECTED_V10_COUNT = 8338
EXPECTED_V11_COUNT = 8341
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
        (V10_PLAN, EXPECTED_V10_PLAN_SHA),
        (V10_RECEIPT, EXPECTED_V10_RECEIPT_SHA),
        (V10_MANIFEST, EXPECTED_V10_MANIFEST_SHA),
        (FROZEN_MANIFEST, EXPECTED_FROZEN_SHA),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise SourceBuildError(f"input SHA changed: {rel(path)}: {actual}")
    selected = load_json(SELECTED)
    acceptance = load_json(ACCEPTANCE)
    entries = selected.get("entries")
    if selected.get("entity_count") != 3 or not isinstance(entries, list) or len(entries) != 3:
        raise SourceBuildError("selected news-assets13 map must contain exactly three entries")
    accepted_by_url = {
        str(item.get("url")): item for item in acceptance.get("entities", []) if isinstance(item, dict)
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
        accepted = accepted_by_url.get(logical)
        if not accepted or accepted.get("sha256") != actual_sha or int(accepted.get("bytes") or -1) != actual_bytes:
            raise SourceBuildError(f"acceptance does not bind exact body: {logical}")
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
            "source_selection": "accepted_selected_news_assets13_preanchor",
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
        "schema_version": "wow-recovery.core-source-v11-additions-map.v1",
        "status": "accepted_selected_news_assets13_primary_source_only",
        "generated_utc": now_utc(),
        "network_performed": False,
        "network_note": "No network request was made; all three bodies and headers were already staged and hash-validated.",
        "anchor_timestamp": ANCHOR,
        "entry_count": len(additions),
        "selected_target_count": len(additions),
        "selected_route_count": len({str(item["derived_route"]) for item in additions}),
        "expected_v10_source_records": EXPECTED_V10_COUNT,
        "expected_v11_source_records": EXPECTED_V11_COUNT,
        "entries": additions,
        "files": additions,
        "selected_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "acceptance_input": {"path": rel(ACCEPTANCE), "sha256": sha256_file(ACCEPTANCE)},
        "integration_policy": "Fresh v11 source mirror only; these are accepted primary entities, not late overlays; root owns Pages export and 38-overlay application.",
        "raw_entities_preserved": True,
    }
    write_json(ADDITIONS_MAP, result)
    return result


def v10_command(plan: dict[str, Any]) -> list[str]:
    original = plan.get("build_argv")
    if not isinstance(original, list) or not original:
        raise SourceBuildError("v10 plan has no recorded build_argv")
    command = [str(item).replace(".scratch/offline-navigation-20261015-v10", ".scratch/offline-navigation-20261015-v11") for item in original]
    command.extend(["--extra-map", rel(ADDITIONS_MAP)])
    return command


def support_copy() -> list[dict[str, Any]]:
    source_support = V10_DIR / "support"
    if not source_support.is_dir():
        raise SourceBuildError("v10 support directory missing")
    V11_SUPPORT.mkdir(parents=True, exist_ok=False)
    migrations: list[dict[str, Any]] = []
    for name in ("compat.css", "compat.js"):
        source = source_support / name
        target = V11_SUPPORT / name
        if not source.is_file():
            raise SourceBuildError(f"v10 support file missing: {rel(source)}")
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


def validate_output(additions: list[dict[str, Any]], before_v10: str, before_frozen: str, support_migrations: list[dict[str, Any]], build: dict[str, Any]) -> dict[str, Any]:
    if not V11_MANIFEST.is_file() or not V11_SITE.is_dir():
        raise SourceBuildError("v11 output is incomplete")
    manifest = load_json(V11_MANIFEST)
    files = manifest.get("files") or []
    by_route = {str(item.get("route")): item for item in files if item.get("route")}
    if len(files) != EXPECTED_V11_COUNT or len(by_route) != EXPECTED_V11_COUNT:
        raise SourceBuildError(f"v11 source count mismatch: files={len(files)} routes={len(by_route)}")
    stats = manifest.get("stats") or {}
    if stats.get("derived_files") != EXPECTED_V11_COUNT or stats.get("routes") != EXPECTED_V11_COUNT:
        raise SourceBuildError(f"v11 stats mismatch: {stats}")
    v10_manifest = load_json(V10_MANIFEST)
    old_aliases = v10_manifest.get("route_aliases") or {}
    new_aliases = manifest.get("route_aliases") or {}
    if len(old_aliases) != EXPECTED_ALIAS_COUNT or len(new_aliases) != EXPECTED_ALIAS_COUNT:
        raise SourceBuildError(f"alias count mismatch: v10={len(old_aliases)} v11={len(new_aliases)}")
    if old_aliases != {key: new_aliases.get(key) for key in old_aliases}:
        raise SourceBuildError("v10 aliases changed in v11")
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
        raise SourceBuildError("v11 additions mismatch: " + ", ".join(mismatches))
    after_v10 = sha256_file(V10_MANIFEST)
    after_frozen = sha256_file(FROZEN_MANIFEST)
    if before_v10 != after_v10 or before_frozen != after_frozen:
        raise SourceBuildError("v10 or frozen manifest changed during v11 build")
    return {
        "v11_manifest_sha256": sha256_file(V11_MANIFEST),
        "v11_manifest_bytes": V11_MANIFEST.stat().st_size,
        "v11_source_records": len(files),
        "v11_route_records": len(by_route),
        "v11_alias_count": len(new_aliases),
        "added_routes": added_routes,
        "stats": stats,
        "support_path_migrations": support_migrations,
        "v10_manifest_before_sha256": before_v10,
        "v10_manifest_after_sha256": after_v10,
        "frozen_manifest_before_sha256": before_frozen,
        "frozen_manifest_after_sha256": after_frozen,
        "build_returncode": build["returncode"],
    }


def main() -> int:
    if ADDITIONS_MAP.exists() or PLAN.exists() or RECEIPT.exists() or V11_DIR.exists():
        raise SystemExit("refusing to overwrite existing v11 source artifacts")
    selected, additions, evidence = validate_inputs()
    v10_plan = load_json(V10_PLAN)
    before_v10 = sha256_file(V10_MANIFEST)
    before_frozen = sha256_file(FROZEN_MANIFEST)
    disk_before = shutil.disk_usage(ROOT)
    write_additions_map(selected, additions)
    support_migrations = support_copy()
    command = v10_command(v10_plan)
    plan = {
        "schema": "wow-recovery.core-source-v11-plan.v1",
        "status": "prepared_source_only_pending_build",
        "generated_utc": now_utc(),
        "network_performed": False,
        "source_selection": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED), "entry_count": len(additions)},
        "acceptance": {"path": rel(ACCEPTANCE), "sha256": sha256_file(ACCEPTANCE)},
        "v10_inputs": {
            "plan": {"path": rel(V10_PLAN), "sha256": sha256_file(V10_PLAN)},
            "receipt": {"path": rel(V10_RECEIPT), "sha256": sha256_file(V10_RECEIPT)},
            "manifest": {"path": rel(V10_MANIFEST), "sha256": before_v10, "source_records": EXPECTED_V10_COUNT},
        },
        "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256": before_frozen},
        "additions_map": {"path": rel(ADDITIONS_MAP), "sha256": sha256_file(ADDITIONS_MAP), "entry_count": len(additions)},
        "expected_counts": {"v10": EXPECTED_V10_COUNT, "new": len(additions), "v11": EXPECTED_V11_COUNT},
        "expected_alias_count": EXPECTED_ALIAS_COUNT,
        "expected_overlay_recipes": EXPECTED_OVERLAY_COUNT,
        "output": {"site": rel(V11_SITE), "manifest": rel(V11_MANIFEST), "support": rel(V11_SUPPORT)},
        "build_argv": command,
        "route_evidence": evidence,
        "support_path_migrations": support_migrations,
        "disk_free_before_bytes": disk_before.free,
    }
    write_json(PLAN, plan)
    build = run_build(command)
    validation = validate_output(additions, before_v10, before_frozen, support_migrations, build)
    disk_after = shutil.disk_usage(ROOT)
    plan.update({"status": "mirror_built_pending_root_export", "build_returncode": build["returncode"], "build_stdout": build["stdout"], "build_stderr": build["stderr"], "validation": validation, "disk_free_after_bytes": disk_after.free, "completed_utc": now_utc()})
    write_json(PLAN, plan)
    receipt = {
        "schema": "wow-recovery.core-source-v11-receipt.v1",
        "status": "mirror_only_pending_root_export",
        "generated_utc": now_utc(),
        "network_requests": 0,
        "source_count": {"prior_v10": EXPECTED_V10_COUNT, "new": len(additions), "v11": EXPECTED_V11_COUNT},
        "selected_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "acceptance_input": {"path": rel(ACCEPTANCE), "sha256": sha256_file(ACCEPTANCE)},
        "additions_map": {"path": rel(ADDITIONS_MAP), "sha256": sha256_file(ADDITIONS_MAP)},
        "plan": {"path": rel(PLAN), "sha256": sha256_file(PLAN)},
        "v10_inputs": {
            "plan": {"path": rel(V10_PLAN), "sha256": sha256_file(V10_PLAN)},
            "receipt": {"path": rel(V10_RECEIPT), "sha256": sha256_file(V10_RECEIPT)},
            "manifest_before_sha256": before_v10,
            "manifest_after_sha256": sha256_file(V10_MANIFEST),
            "source_records_preserved": EXPECTED_V10_COUNT,
        },
        "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256_before": before_frozen, "sha256_after": sha256_file(FROZEN_MANIFEST), "unchanged": before_frozen == sha256_file(FROZEN_MANIFEST)},
        "v11_output": {"site": rel(V11_SITE), "manifest": rel(V11_MANIFEST), "manifest_sha256": validation["v11_manifest_sha256"], "manifest_bytes": validation["v11_manifest_bytes"], "source_records": validation["v11_source_records"]},
        "added_routes": validation["added_routes"],
        "aliases": {"prior_v10": EXPECTED_ALIAS_COUNT, "v11": validation["v11_alias_count"], "preserved": validation["v11_alias_count"] == EXPECTED_ALIAS_COUNT},
        "overlay_recipe": {"accepted_count": EXPECTED_OVERLAY_COUNT, "applied_in_source_phase": False, "pending_root_export": True},
        "support_path_migrations": validation["support_path_migrations"],
        "build": {"argv": command, "returncode": build["returncode"], "stdout": build["stdout"], "stderr": build["stderr"], "stats": validation["stats"]},
        "disk_free": {"before_bytes": disk_before.free, "after_bytes": disk_after.free},
        "policies": {"new_entities": "accepted primary pre-anchor source entities, not late overlays", "network": "local staged bodies/headers only", "export": "root-owned; no Pages/export/ZIP performed"},
    }
    write_json(RECEIPT, receipt)
    print(json.dumps({"result": "PASS", "status": receipt["status"], "prior_v10": EXPECTED_V10_COUNT, "new": len(additions), "v11": EXPECTED_V11_COUNT, "v11_manifest_sha256": validation["v11_manifest_sha256"], "v10_manifest_unchanged": before_v10 == sha256_file(V10_MANIFEST), "frozen_manifest_unchanged": before_frozen == sha256_file(FROZEN_MANIFEST), "network_requests": 0, "receipt": rel(RECEIPT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SourceBuildError as exc:
        print(f"build_source_v11: {exc}", file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
"""Build the bounded local-only v14 source mirror from the accepted v13 mirror.

This adapter deliberately reuses the recorded v13 offline_mirror command.  It
only stages the nine accepted RSS14 entities, redirects output to a fresh
v14 scratch directory, and records source-only provenance for root export.
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
OWN_DIR = ROOT / "research" / "v14-integration" / "source"
V13_SOURCE_DIR = ROOT / "research" / "v13-integration" / "source"
V13_PLAN = V13_SOURCE_DIR / "v13-source-plan.json"
V13_RECEIPT = V13_SOURCE_DIR / "v13-source-receipt.json"
V13_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v13"
V14_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v14"
V13_MANIFEST = V13_DIR / "build-manifest.json"
V14_MANIFEST = V14_DIR / "build-manifest.json"
V14_SITE = V14_DIR / "site"
V14_SUPPORT = V14_DIR / "support"
FROZEN_MANIFEST = ROOT / "offline" / "build-manifest.json"
APPROVED_PLAN = RECOVERY / "source14-approved-plan.json"
PRODUCER = ROOT / "tools" / "offline_mirror.py"
SELECTED = RECOVERY / "selected-final-rss14-source-map.json"
ADDITIONS_MAP = OWN_DIR / "v14-additions-source-map.json"
PLAN = OWN_DIR / "v14-source-plan.json"
RECEIPT = OWN_DIR / "v14-source-receipt.json"

EXPECTED_SELECTED_SHA = "7019d82bca12be63f5ad832ae72729c1ac8b8fa3c4c4b6936f2d452f780d166b"
EXPECTED_APPROVED_PLAN_SHA = "67f85ee12fe1f5fecf96a26764f4c454f17306aefc55cb2f0011a1999983fe34"
EXPECTED_PRODUCER_SHA = "8171683dc6b74237d3a655697c9930932fe863f8200685f16da8d4c29c1c635a"
EXPECTED_V13_PLAN_SHA = "118d767da3a0f6ce4588ccde079a6832d3c93d5890991da3210af03bf5bc0ff1"
EXPECTED_V13_RECEIPT_SHA = "e3f2f51c4be9eaa10e30e0143fc301b166dbc4e84feb134933658f8e9d1befe2"
EXPECTED_V13_MANIFEST_SHA = "b9f26e1aa4544b5b1279c7a7e54acbf1306da5518c6a3b7aa685e05df9cfbdc9"
EXPECTED_FROZEN_SHA = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
EXPECTED_V13_COUNT = 8347
EXPECTED_V14_COUNT = 8356
EXPECTED_NEW_COUNT = 9
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
        (APPROVED_PLAN, EXPECTED_APPROVED_PLAN_SHA),
        (PRODUCER, EXPECTED_PRODUCER_SHA),
        (SELECTED, EXPECTED_SELECTED_SHA),
        (V13_PLAN, EXPECTED_V13_PLAN_SHA),
        (V13_RECEIPT, EXPECTED_V13_RECEIPT_SHA),
        (V13_MANIFEST, EXPECTED_V13_MANIFEST_SHA),
        (FROZEN_MANIFEST, EXPECTED_FROZEN_SHA),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise SourceBuildError(f"input SHA changed: {rel(path)}: {actual}")
    selected = load_json(SELECTED)
    approved_plan = load_json(APPROVED_PLAN)
    baseline = approved_plan.get("source_baseline") or {}
    selected_nine = approved_plan.get("selected_nine") or {}
    if approved_plan.get("expected_sources") != EXPECTED_V14_COUNT or approved_plan.get("aliases") != EXPECTED_ALIAS_COUNT or approved_plan.get("overlay_recipes") != EXPECTED_OVERLAY_COUNT:
        raise SourceBuildError("approved SOURCE14 counts do not match the bounded build")
    if baseline.get("manifest") != ".scratch/offline-navigation-20261015-v13/build-manifest.json" or baseline.get("sha256") != EXPECTED_V13_MANIFEST_SHA or baseline.get("sources") != EXPECTED_V13_COUNT:
        raise SourceBuildError("approved SOURCE14 baseline does not bind the accepted v13 manifest")
    if selected_nine.get("path") != rel(SELECTED) or selected_nine.get("sha256") != EXPECTED_SELECTED_SHA:
        raise SourceBuildError("approved SOURCE14 selection does not bind selected-final-rss14-source-map.json")
    entries = selected.get("entries")
    if selected.get("entry_count") != EXPECTED_NEW_COUNT or not isinstance(entries, list) or len(entries) != EXPECTED_NEW_COUNT or selected.get("accepted") is not True:
        raise SourceBuildError("selected RSS14 map must contain exactly nine accepted entries")
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
        if selected_entry.get("body_sha256") != actual_sha or int(selected_entry.get("body_bytes") or -1) != actual_bytes:
            raise SourceBuildError(f"selected map does not bind exact body: {target or logical}")
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
            "source_selection": "accepted_selected_rss14_preanchor",
            "source_entities_unmodified": True,
            "cdx_digest": selected_entry.get("cdx_digest"),
            "source_group": selected_entry.get("source_group"),
            "temporal_status": selected_entry.get("temporal_status"),
            "source_evidence": {
                "selected_input": rel(SELECTED),
                "acceptance": rel(SELECTED),
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
        "schema_version": "wow-recovery.core-source-v14-additions-map.v1",
        "status": "accepted_selected_rss14_expanded_html_primary_source_only",
        "generated_utc": now_utc(),
        "network_performed": False,
        "network_note": "No network request was made; all nine expanded HTML bodies and headers were already staged and hash-validated.",
        "anchor_timestamp": ANCHOR,
        "entry_count": len(additions),
        "selected_target_count": len(additions),
        "selected_route_count": len({str(item["derived_route"]) for item in additions}),
        "expected_v13_source_records": EXPECTED_V13_COUNT,
        "expected_v14_source_records": EXPECTED_V14_COUNT,
        "entries": additions,
        "files": additions,
        "selected_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "acceptance_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "integration_policy": "Fresh v14 source mirror only; these are accepted primary expanded HTML entities, not late overlays; root owns Pages export and 38-overlay application.",
        "raw_entities_preserved": True,
    }
    write_json(ADDITIONS_MAP, result)
    return result


def v13_command(plan: dict[str, Any]) -> list[str]:
    original = plan.get("build_argv")
    if not isinstance(original, list) or not original:
        raise SourceBuildError("v13 plan has no recorded build_argv")
    command = [
        str(item).replace(
            ".scratch/offline-navigation-20261015-v13",
            ".scratch/offline-navigation-20261015-v14",
        )
        for item in original
    ]
    command.extend(["--extra-map", rel(ADDITIONS_MAP)])
    return command


def support_copy() -> list[dict[str, Any]]:
    source_support = V13_DIR / "support"
    if not source_support.is_dir():
        raise SourceBuildError("v13 support directory missing")
    V14_SUPPORT.mkdir(parents=True, exist_ok=False)
    migrations: list[dict[str, Any]] = []
    for name in ("compat.css", "compat.js"):
        source = source_support / name
        target = V14_SUPPORT / name
        if not source.is_file():
            raise SourceBuildError(f"v13 support file missing: {rel(source)}")
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


def validate_output(additions: list[dict[str, Any]], before_v13: str, before_frozen: str, support_migrations: list[dict[str, Any]], build: dict[str, Any]) -> dict[str, Any]:
    if not V14_MANIFEST.is_file() or not V14_SITE.is_dir():
        raise SourceBuildError("v14 output is incomplete")
    manifest = load_json(V14_MANIFEST)
    files = manifest.get("files") or []
    by_route = {str(item.get("route")): item for item in files if item.get("route")}
    if len(files) != EXPECTED_V14_COUNT or len(by_route) != EXPECTED_V14_COUNT:
        raise SourceBuildError(f"v14 source count mismatch: files={len(files)} routes={len(by_route)}")
    stats = manifest.get("stats") or {}
    if stats.get("derived_files") != EXPECTED_V14_COUNT or stats.get("routes") != EXPECTED_V14_COUNT:
        raise SourceBuildError(f"v14 stats mismatch: {stats}")
    v13_manifest = load_json(V13_MANIFEST)
    old_aliases = v13_manifest.get("route_aliases") or {}
    new_aliases = manifest.get("route_aliases") or {}
    if len(old_aliases) != EXPECTED_ALIAS_COUNT or len(new_aliases) != EXPECTED_ALIAS_COUNT:
        raise SourceBuildError(f"alias count mismatch: v13={len(old_aliases)} v14={len(new_aliases)}")
    if old_aliases != {key: new_aliases.get(key) for key in old_aliases}:
        raise SourceBuildError("v13 aliases changed in v14")
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
        raise SourceBuildError("v14 additions mismatch: " + ", ".join(mismatches))
    after_v13 = sha256_file(V13_MANIFEST)
    after_frozen = sha256_file(FROZEN_MANIFEST)
    if before_v13 != after_v13 or before_frozen != after_frozen:
        raise SourceBuildError("v13 or frozen manifest changed during v14 build")
    return {
        "v14_manifest_sha256": sha256_file(V14_MANIFEST),
        "v14_manifest_bytes": V14_MANIFEST.stat().st_size,
        "v14_source_records": len(files),
        "v14_route_records": len(by_route),
        "v14_alias_count": len(new_aliases),
        "added_routes": added_routes,
        "stats": stats,
        "support_path_migrations": support_migrations,
        "v13_manifest_before_sha256": before_v13,
        "v13_manifest_after_sha256": after_v13,
        "frozen_manifest_before_sha256": before_frozen,
        "frozen_manifest_after_sha256": after_frozen,
        "build_returncode": build["returncode"],
    }


def main() -> int:
    if ADDITIONS_MAP.exists() or PLAN.exists() or RECEIPT.exists() or V14_DIR.exists():
        raise SystemExit("refusing to overwrite existing v14 source artifacts")
    selected, additions, evidence = validate_inputs()
    v13_plan = load_json(V13_PLAN)
    before_v13 = sha256_file(V13_MANIFEST)
    before_frozen = sha256_file(FROZEN_MANIFEST)
    disk_before = shutil.disk_usage(ROOT)
    write_additions_map(selected, additions)
    support_migrations = support_copy()
    command = v13_command(v13_plan)
    plan = {
        "schema": "wow-recovery.core-source-v14-plan.v1",
        "status": "prepared_source_only_pending_build",
        "generated_utc": now_utc(),
        "network_performed": False,
        "approved_plan": {"path": rel(APPROVED_PLAN), "sha256": sha256_file(APPROVED_PLAN)},
        "producer": {"path": rel(PRODUCER), "sha256": sha256_file(PRODUCER)},
        "source_selection": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED), "entry_count": len(additions)},
        "acceptance": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "v13_inputs": {
            "plan": {"path": rel(V13_PLAN), "sha256": sha256_file(V13_PLAN)},
            "receipt": {"path": rel(V13_RECEIPT), "sha256": sha256_file(V13_RECEIPT)},
            "manifest": {"path": rel(V13_MANIFEST), "sha256": before_v13, "source_records": EXPECTED_V13_COUNT},
        },
        "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256": before_frozen},
        "additions_map": {"path": rel(ADDITIONS_MAP), "sha256": sha256_file(ADDITIONS_MAP), "entry_count": len(additions)},
        "expected_counts": {"v13": EXPECTED_V13_COUNT, "new": len(additions), "v14": EXPECTED_V14_COUNT},
        "expected_alias_count": EXPECTED_ALIAS_COUNT,
        "expected_overlay_recipes": EXPECTED_OVERLAY_COUNT,
        "output": {"site": rel(V14_SITE), "manifest": rel(V14_MANIFEST), "support": rel(V14_SUPPORT)},
        "build_argv": command,
        "route_evidence": evidence,
        "support_path_migrations": support_migrations,
        "disk_free_before_bytes": disk_before.free,
        "source_guard": "Use the accepted v13 plan/manifest as the old-source identity baseline; run only tools/offline_mirror.py with the v14 additions map.",
    }
    write_json(PLAN, plan)
    build = run_build(command)
    validation = validate_output(additions, before_v13, before_frozen, support_migrations, build)
    disk_after = shutil.disk_usage(ROOT)
    plan.update({"status": "mirror_built_pending_root_export", "build_returncode": build["returncode"], "build_stdout": build["stdout"], "build_stderr": build["stderr"], "validation": validation, "disk_free_after_bytes": disk_after.free, "completed_utc": now_utc()})
    write_json(PLAN, plan)
    receipt = {
        "schema": "wow-recovery.core-source-v14-receipt.v1",
        "status": "mirror_only_pending_root_export",
        "generated_utc": now_utc(),
        "network_requests": 0,
        "approved_plan": {"path": rel(APPROVED_PLAN), "sha256": sha256_file(APPROVED_PLAN)},
        "producer": {"path": rel(PRODUCER), "sha256": sha256_file(PRODUCER)},
        "source_count": {"prior_v13": EXPECTED_V13_COUNT, "new": len(additions), "v14": EXPECTED_V14_COUNT},
        "selected_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "acceptance_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "additions_map": {"path": rel(ADDITIONS_MAP), "sha256": sha256_file(ADDITIONS_MAP)},
        "plan": {"path": rel(PLAN), "sha256": sha256_file(PLAN)},
        "v13_inputs": {
            "plan": {"path": rel(V13_PLAN), "sha256": sha256_file(V13_PLAN)},
            "receipt": {"path": rel(V13_RECEIPT), "sha256": sha256_file(V13_RECEIPT)},
            "manifest_before_sha256": before_v13,
            "manifest_after_sha256": sha256_file(V13_MANIFEST),
            "source_records_preserved": EXPECTED_V13_COUNT,
        },
        "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256_before": before_frozen, "sha256_after": sha256_file(FROZEN_MANIFEST), "unchanged": before_frozen == sha256_file(FROZEN_MANIFEST)},
        "v14_output": {"site": rel(V14_SITE), "manifest": rel(V14_MANIFEST), "manifest_sha256": validation["v14_manifest_sha256"], "manifest_bytes": validation["v14_manifest_bytes"], "source_records": validation["v14_source_records"]},
        "added_routes": validation["added_routes"],
        "aliases": {"prior_v13": EXPECTED_ALIAS_COUNT, "v14": validation["v14_alias_count"], "preserved": validation["v14_alias_count"] == EXPECTED_ALIAS_COUNT},
        "overlay_recipe": {"accepted_count": EXPECTED_OVERLAY_COUNT, "applied_in_source_phase": False, "pending_root_export": True},
        "support_path_migrations": validation["support_path_migrations"],
        "build": {"argv": command, "returncode": build["returncode"], "stdout": build["stdout"], "stderr": build["stderr"], "stats": validation["stats"]},
        "disk_free": {"before_bytes": disk_before.free, "after_bytes": disk_after.free},
        "retention": {"raw_entities": "Preserved at the original RSS020/RSS021 raw paths; no body copy was made in v14 output.", "derived_entities": "Nine derived routes retain exact source SHA/length and are recorded in added_routes.", "old_source_identity": "All 8347 v13 source records are carried forward by the accepted v13 build maps."},
        "policies": {"new_entities": "accepted primary pre-anchor source entities, not late overlays", "network": "local staged bodies/headers only", "export": "root-owned; no Pages/export/ZIP performed"},
    }
    write_json(RECEIPT, receipt)
    print(json.dumps({"result": "PASS", "status": receipt["status"], "prior_v13": EXPECTED_V13_COUNT, "new": len(additions), "v14": EXPECTED_V14_COUNT, "v14_manifest_sha256": validation["v14_manifest_sha256"], "v13_manifest_unchanged": before_v13 == sha256_file(V13_MANIFEST), "frozen_manifest_unchanged": before_frozen == sha256_file(FROZEN_MANIFEST), "network_requests": 0, "receipt": rel(RECEIPT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SourceBuildError as exc:
        print(f"build_source_v14: {exc}", file=sys.stderr)
        raise SystemExit(1)

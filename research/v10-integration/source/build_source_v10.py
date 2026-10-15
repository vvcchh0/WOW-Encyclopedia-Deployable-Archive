#!/usr/bin/env python3
"""Build a fresh local-only v10 source mirror from the accepted v9 inputs.

This phase deliberately stops at the offline mirror.  Pages export, browser
acceptance, and image-overlay application remain coordinator-owned phases.
"""

from __future__ import annotations

import argparse
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
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
RECOVERY = ROOT / "research" / "continuous-recovery-20261015"
OWN_DIR = ROOT / "research" / "v10-integration" / "source"
SELECTED = RECOVERY / "selected-v10-final-additions.json"
FROZEN_MANIFEST = ROOT / "offline" / "build-manifest.json"
V9_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v9"
V9_SITE = V9_DIR / "site"
V9_MANIFEST = V9_DIR / "build-manifest.json"
V10_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v10"
V10_SITE = V10_DIR / "site"
V10_SUPPORT = V10_DIR / "support"
V10_MANIFEST = V10_DIR / "build-manifest.json"
ADDITIONS_MAP = OWN_DIR / "v10-additions-source-map.json"
PLAN = OWN_DIR / "v10-source-plan.json"
RECEIPT = OWN_DIR / "v10-source-receipt.json"

V9_CORE_MAP = RECOVERY / "core-pages-integration" / "core-pages-source-map.selected.json"
V9_STATIC_MAP = RECOVERY / "core-pages-integration" / "selected-static-source-map.v9.json"
V9_ALIAS_MAP = RECOVERY / "core-pages-integration" / "battlegroups-route-alias-overlay.v9.json"

BASE_EXTRA_MAPS = [
    "offline/approved-pages-recovery-map.json",
    "offline/approved-pages-temporal-supplement-map.json",
    "offline/approved-static-recovery-map.json",
    "offline/approved-static-temporal-supplement-map.json",
    "offline/approved-static-pre2008-supplement-map.json",
    "offline/approved-expansion-map.json",
    "offline/approved-route-alias-overlay.json",
    "offline/upstream-compatibility-map.json",
    "research/navigation-gaps-20261015/wayback-missing/effective-source-map-v7c.json",
]

EXPECTED_SELECTION_SHA = "c73b02d2f9353402eb4b568640e1359031e25756604cbbc5f21552f0acd52a55"
EXPECTED_ACCEPTANCE_HASHES = {
    "rss6-acceptance.json": "eec2fe529f56f547c38b49740f302c85ebcbe49edc701f3a1e28ba65f9be77c2",
    "wrath8-acceptance.json": "ee552b25a056eed66a7b602f2d5e5254db37d411c75f4726f69adde876ef70d7",
    "mixed9-acceptance.json": "989a559c56733d34c39b806e1e1d42be6b50e337cc4dd9221423ec31da89866b",
    "rss10-acceptance.json": "f87d84d7c801f90050a6e1a8cbc308104b4e6c7ad133d70db6172c55896e04c0",
}
EXPECTED_V9_SOURCE_COUNT = 8328
EXPECTED_V10_SOURCE_COUNT = 8338
EXPECTED_NEW_COUNT = 10
ANCHOR = "20080512210044"


class SourceBuildError(RuntimeError):
    """Raised when a staged source or preservation invariant fails."""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        raise SourceBuildError(f"JSON root is not an object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def root_path(value: Any, *, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise SourceBuildError(f"missing {field}")
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SourceBuildError(f"{field} escapes workspace: {value}") from exc
    return path


def parse_timestamp(value: str) -> datetime:
    text = str(value or "").strip()
    if re.fullmatch(r"\d{14}", text):
        return datetime.strptime(text, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def check_capture(entry: dict[str, Any]) -> None:
    timestamp = parse_timestamp(str(entry.get("actual_timestamp") or ""))
    memento = parse_timestamp(str(entry.get("actual_memento") or ""))
    if timestamp != memento:
        raise SourceBuildError(
            f"capture timestamp/memento mismatch: {entry.get('target')}: "
            f"{entry.get('actual_timestamp')} != {entry.get('actual_memento')}"
        )
    if timestamp >= parse_timestamp(ANCHOR):
        raise SourceBuildError(f"non-pre-anchor source selected: {entry.get('target')}")


def header_metadata(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"^HTTP/\d(?:\.\d)?\s+200\s+OK\s*$", text, re.I | re.M):
        raise SourceBuildError(f"staged response is not HTTP 200: {path}")
    memento_match = re.search(r"^memento-datetime:\s*(.+?)\s*$", text, re.I | re.M)
    memento = parsedate_to_datetime(memento_match.group(1)) if memento_match else None
    return {
        "http_status": 200,
        "memento_header": memento.isoformat() if memento else None,
        "header_sha256": sha256_file(path),
        "header_bytes": path.stat().st_size,
    }


def route_for(entry: dict[str, Any]) -> str:
    target = str(entry.get("target") or "")
    if target.startswith("/news/"):
        return target
    if target == "screeniesimplified-js":
        return "/wrath/js/screeniesimplified.js"
    if target == "pixel-layout":
        return "/wrath/images/layout/pixel.gif"
    if str(entry.get("query_original_url") or "").split("?", 1)[0].endswith("/wrath/art.xml"):
        return "/wrath/art.xml"
    raise SourceBuildError(f"no exact v10 route mapping for {target}")


def kind_for(route: str) -> str:
    if route.endswith(".js"):
        return "js"
    if route.endswith((".gif", ".png", ".jpg", ".jpeg", ".webp")):
        return "image"
    return "html"


def make_addition_entry(entry: dict[str, Any], *, selection_rel: str) -> tuple[dict[str, Any], dict[str, Any]]:
    body = root_path(entry.get("local_path"), field=f"{entry.get('target')}.local_path")
    headers = root_path(entry.get("headers_local_path"), field=f"{entry.get('target')}.headers_local_path")
    if not body.is_file() or not headers.is_file():
        raise SourceBuildError(f"staged body/header missing for {entry.get('target')}")
    body_bytes = body.stat().st_size
    body_sha = sha256_file(body)
    if body_bytes != int(entry.get("body_bytes") or -1) or body_sha != entry.get("body_sha256"):
        raise SourceBuildError(f"raw body SHA/length mismatch for {entry.get('target')}")
    check_capture(entry)
    headers_meta = header_metadata(headers)
    route = route_for(entry)
    kind = kind_for(route)
    query_url = str(entry["query_original_url"])
    source_url = query_url
    role = (
        "archived_news_html"
        if route.startswith("/news/")
        else "historical_gallery_viewer"
        if route == "/wrath/art.xml"
        else "historical_gallery_viewer_script"
        if route.endswith("screeniesimplified.js")
        else "layout_decoration"
    )
    item: dict[str, Any] = {
        "logical_url": query_url,
        "source_url": source_url,
        "source_base_url": source_url,
        "captured_original": str(entry.get("captured_original_url") or query_url),
        "query_original_url": query_url,
        "captured_original_url": str(entry.get("captured_original_url") or query_url),
        "local_path": str(entry["local_path"]),
        "sha256": body_sha,
        "content_length": body_bytes,
        "actual_timestamp": str(entry["actual_timestamp"]),
        "actual_memento": str(entry["actual_memento"]),
        "derived_route": route,
        "route_aliases": [],
        "mime": str(entry.get("mime") or "application/octet-stream"),
        "kind": kind,
        "role": role,
        "temporal_class": "pre_anchor_historical_capture",
        "source_status": 200,
        "raw_body_path": str(entry["local_path"]),
        "raw_headers_path": str(entry["headers_local_path"]),
        "headers_local_path": str(entry["headers_local_path"]),
        "source_batch": str(Path(str(entry["local_path"])).parts[-3])
        if len(Path(str(entry["local_path"])).parts) >= 3
        else None,
        "source_selection": "accepted_selected_v10_final_additions",
        "source_entities_unmodified": True,
        "cdx_digest": entry.get("cdx_digest"),
        "source_evidence": {
            "selected_input": selection_rel,
            "target": entry.get("target"),
            "logical_url": query_url,
            "query_original_url": query_url,
            "captured_original_url": entry.get("captured_original_url"),
            "body_sha256": body_sha,
            "body_bytes": body_bytes,
            "raw_body_path": entry["local_path"],
            "raw_headers_path": entry["headers_local_path"],
            "actual_timestamp": entry["actual_timestamp"],
            "actual_memento": entry["actual_memento"],
            "header_evidence": headers_meta,
        },
        "selection_provenance": entry,
    }
    if route == "/wrath/art.xml":
        item.update(
            {
                "source_query_preserved": True,
                "generic_route_mapping_basis": entry.get("generic_route_mapping_basis"),
                "captured_original_query": query_url,
                "strict_derived_parser_required": True,
            }
        )
    if route.startswith("/news/"):
        item["body_format"] = entry.get("body_format")
        item["title"] = entry.get("title")
        item["source_anomaly"] = entry.get("source_anomaly")
        item["title_month_matches_url"] = entry.get("title_month_matches_url")
        item["article_month_matches_url"] = entry.get("article_month_matches_url")
        item["article_posted_date_count"] = entry.get("article_posted_date_count")
        item["expanded_html_do_not_apply_xsl"] = True
    if route.endswith("screeniesimplified.js"):
        item["entity_class"] = entry.get("entity_class")
        item["independent_content_check"] = entry.get("independent_content_check")
        item["raw_eval_preserved_until_root_export"] = True
    if route.endswith("pixel.gif"):
        item["entity_class"] = entry.get("entity_class")
        item["independent_content_check"] = entry.get("independent_content_check")
        item["content_image_count"] = 0
    return item, {
        "target": entry.get("target"),
        "route": route,
        "body_path": rel(body),
        "headers_path": rel(headers),
        "body_bytes": body_bytes,
        "body_sha256": body_sha,
        "actual_timestamp": entry.get("actual_timestamp"),
        "actual_memento": entry.get("actual_memento"),
        "http_status": headers_meta["http_status"],
        "header_sha256": headers_meta["header_sha256"],
        "header_bytes": headers_meta["header_bytes"],
        "mime": entry.get("mime"),
        "title": entry.get("title"),
        "source_anomaly": entry.get("source_anomaly"),
    }


def validate_selection() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    selected_sha = sha256_file(SELECTED)
    if selected_sha != EXPECTED_SELECTION_SHA:
        raise SourceBuildError(f"v10 selection SHA changed: {selected_sha}")
    selected = load_json(SELECTED)
    entries = selected.get("entries")
    if selected.get("entry_count") != EXPECTED_NEW_COUNT or not isinstance(entries, list) or len(entries) != EXPECTED_NEW_COUNT:
        raise SourceBuildError("v10 selected entry count is not exactly 10")
    for name, expected in EXPECTED_ACCEPTANCE_HASHES.items():
        actual = sha256_file(RECOVERY / name)
        if actual != expected:
            raise SourceBuildError(f"accepted input SHA changed: {name}: {actual}")
    map_entries: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    routes: set[str] = set()
    for entry in entries:
        item, item_evidence = make_addition_entry(entry, selection_rel=rel(SELECTED))
        if item["derived_route"] in routes:
            raise SourceBuildError(f"duplicate v10 addition route: {item['derived_route']}")
        routes.add(item["derived_route"])
        map_entries.append(item)
        evidence.append(item_evidence)
    if len(map_entries) != EXPECTED_NEW_COUNT or len(routes) != EXPECTED_NEW_COUNT:
        raise SourceBuildError("v10 addition conservation failed")
    return selected, map_entries, evidence


def write_additions_map(selected: dict[str, Any], entries: list[dict[str, Any]]) -> dict[str, Any]:
    result = {
        "schema_version": "wow-recovery.core-source-v10-additions-map.v1",
        "status": "accepted_selected_v10_additions_source_only",
        "generated_utc": now_utc(),
        "network_performed": False,
        "network_note": "No network request was made; all ten bodies and headers were already staged and hash-validated.",
        "anchor_timestamp": ANCHOR,
        "entry_count": len(entries),
        "selected_target_count": len(entries),
        "selected_route_count": len({str(item["derived_route"]) for item in entries}),
        "expected_v9_source_records": EXPECTED_V9_SOURCE_COUNT,
        "expected_v10_source_records": EXPECTED_V10_SOURCE_COUNT,
        "entries": entries,
        "files": entries,
        "selected_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "acceptance_hashes": {
            name: {"path": rel(RECOVERY / name), "sha256": sha256_file(RECOVERY / name)}
            for name in EXPECTED_ACCEPTANCE_HASHES
        },
        "expanded_html_policy": "All seven RSS-path entries are accepted expanded HTML and retain their source titles/anomalies; no XSL is selected by the .xml suffix.",
        "viewer_policy": "The /wrath/art.xml source URI retains ?s=1, captured-original, Memento, and generic viewer evidence; only root export may apply the exact-route strict parser.",
        "pixel_policy": "pixel.gif remains a 1x1 layout decoration and is not counted as content imagery.",
        "raw_entities_preserved": True,
    }
    write_json(ADDITIONS_MAP, result)
    return result


def tree_digest(path: Path) -> tuple[int, int, str]:
    digest = hashlib.sha256()
    count = 0
    total = 0
    for child in sorted((item for item in path.rglob("*") if item.is_file()), key=lambda item: item.relative_to(path).as_posix()):
        relative = child.relative_to(path).as_posix().encode("utf-8")
        data_hash = sha256_file(child).encode("ascii")
        size = child.stat().st_size
        digest.update(relative)
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(data_hash)
        digest.update(b"\n")
        count += 1
        total += size
    return count, total, digest.hexdigest()


def baseline_state() -> dict[str, Any]:
    if not V9_SITE.is_dir() or not V9_MANIFEST.is_file():
        raise SourceBuildError("accepted v9 source mirror is missing")
    manifest = load_json(V9_MANIFEST)
    files = manifest.get("files") or []
    if len(files) != EXPECTED_V9_SOURCE_COUNT:
        raise SourceBuildError(f"v9 source count changed before build: {len(files)}")
    aliases = manifest.get("route_aliases") or {}
    if aliases.get("/ptr") != "/ptr/index.html" or aliases.get("/ptr/") != "/ptr/index.html":
        raise SourceBuildError("v9 PTR aliases missing before build")
    if aliases.get("/pvp/battlegrounds/battlegroups.html") != "/pvp/battlegrounds/battlegroups/index.html":
        raise SourceBuildError("v9 Battlegroups alias missing before build")
    count, total, digest = tree_digest(V9_SITE)
    return {
        "manifest_sha256": sha256_file(V9_MANIFEST),
        "manifest_bytes": V9_MANIFEST.stat().st_size,
        "source_records": len(files),
        "route_alias_count": len(aliases),
        "site_file_count": count,
        "site_total_bytes": total,
        "site_tree_digest": digest,
        "route_aliases": aliases,
    }


def build_command() -> list[str]:
    command = [
        sys.executable,
        "-X",
        "utf8",
        "tools/offline_mirror.py",
        "build",
        "--url-map",
        "mirror/20080512/url-map.json",
        "--overlay",
        "research/gap-review-20261011/reviewed-index-overlay.json",
        "--site",
        rel(V10_SITE),
        "--manifest",
        rel(V10_MANIFEST),
        "--support-dir",
        rel(V10_SUPPORT),
    ]
    for path in BASE_EXTRA_MAPS + [rel(V9_CORE_MAP), rel(V9_STATIC_MAP), rel(V9_ALIAS_MAP), rel(ADDITIONS_MAP)]:
        command.extend(("--extra-map", path))
    return command


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
    result = {
        "argv": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.returncode != 0:
        raise SourceBuildError(
            f"offline_mirror failed ({completed.returncode}): {completed.stderr[-6000:]}"
        )
    return result


def validate_output(
    additions: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    baseline: dict[str, Any],
    build_result: dict[str, Any],
) -> dict[str, Any]:
    if not V10_MANIFEST.is_file() or not V10_SITE.is_dir():
        raise SourceBuildError("v10 mirror output is incomplete")
    manifest = load_json(V10_MANIFEST)
    files = manifest.get("files") or []
    by_route = {str(item.get("route")): item for item in files if item.get("route")}
    if len(files) != EXPECTED_V10_SOURCE_COUNT or len(by_route) != EXPECTED_V10_SOURCE_COUNT:
        raise SourceBuildError(f"v10 source count mismatch: files={len(files)} routes={len(by_route)}")
    old_manifest = load_json(V9_MANIFEST)
    old_by_route = {str(item.get("route")): item for item in old_manifest.get("files", []) if item.get("route")}
    old_missing = sorted(set(old_by_route) - set(by_route))
    if old_missing:
        raise SourceBuildError(f"v9 routes missing from v10: {old_missing[:20]}")
    old_changed: list[str] = []
    support_path_migrations: list[dict[str, Any]] = []
    compare_keys = (
        "origin_namespace",
        "source_local_path",
        "source_base_url",
        "source_map_path",
        "source_sha256",
        "source_length",
        "source_mime",
        "mime",
        "kind",
        "role",
        "source_role",
        "actual_timestamp",
        "requested_timestamp",
    )
    for route, old_item in old_by_route.items():
        new_item = by_route[route]
        for key in compare_keys:
            if old_item.get(key) != new_item.get(key):
                if (
                    key == "source_local_path"
                    and route in {"/__offline/compat.css", "/__offline/compat.js"}
                    and old_item.get("source_sha256") == new_item.get("source_sha256")
                    and old_item.get("source_length") == new_item.get("source_length")
                ):
                    support_path_migrations.append(
                        {
                            "route": route,
                            "old_source_local_path": old_item.get("source_local_path"),
                            "new_source_local_path": new_item.get("source_local_path"),
                            "source_sha256": new_item.get("source_sha256"),
                            "source_length": new_item.get("source_length"),
                            "content_hash_preserved": True,
                        }
                    )
                    continue
                old_changed.append(f"{route}:{key}")
                break
    old_aliases = old_manifest.get("route_aliases") or {}
    new_aliases = manifest.get("route_aliases") or {}
    if old_aliases != {key: new_aliases.get(key) for key in old_aliases}:
        raise SourceBuildError("v9 aliases changed in v10")
    new_routes: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for addition, item_evidence in zip(additions, evidence, strict=True):
        route = str(addition["derived_route"])
        actual = by_route.get(route)
        if actual is None:
            mismatches.append(f"{route}:missing")
            continue
        for key, expected in (
            ("source_sha256", addition["sha256"]),
            ("source_length", addition["content_length"]),
            ("source_base_url", addition["source_base_url"]),
            ("actual_timestamp", addition["actual_timestamp"]),
            ("actual_memento", addition["actual_memento"]),
            ("mime", addition["mime"]),
            ("kind", addition["kind"]),
            ("role", addition["role"]),
        ):
            # offline_mirror records the UTC capture timestamp in each route
            # record but keeps the full Memento value in the selected source
            # map/header evidence.  Accept an omitted manifest field only
            # when it is not contradictory; the selected map was already
            # hash/header validated before the mirror ran.
            if key == "actual_memento" and actual.get(key) is None:
                continue
            if actual.get(key) != expected:
                mismatches.append(f"{route}:{key}")
        output = root_path(actual.get("output_path"), field=f"{route}.output_path")
        if not output.is_file():
            mismatches.append(f"{route}:output_missing")
        output_bytes = output.stat().st_size if output.is_file() else None
        output_sha = sha256_file(output) if output.is_file() else None
        new_routes.append(
            {
                "target": item_evidence["target"],
                "route": route,
                "source_bytes": addition["content_length"],
                "source_sha256": addition["sha256"],
                "derived_path": rel(output) if output.is_file() else None,
                "derived_bytes": output_bytes,
                "derived_sha256": output_sha,
                "actual_timestamp": addition["actual_timestamp"],
                "actual_memento": addition["actual_memento"],
                "manifest_actual_memento": actual.get("actual_memento"),
                "memento_evidence": "selected source map and staged HTTP headers",
                "source_status": actual.get("source_status"),
                "mime": actual.get("mime"),
                "title": addition.get("title"),
                "source_anomaly": addition.get("source_anomaly"),
                "raw_body_path": addition["raw_body_path"],
                "raw_headers_path": addition["raw_headers_path"],
            }
        )
    if old_changed:
        raise SourceBuildError(f"v9 source provenance changed: {old_changed[:20]}")
    if mismatches:
        raise SourceBuildError(f"v10 selected source mismatches: {mismatches}")
    after = baseline_state()
    if after["manifest_sha256"] != baseline["manifest_sha256"] or after["site_tree_digest"] != baseline["site_tree_digest"]:
        raise SourceBuildError("v9 source tree or manifest changed while building v10")
    stats = manifest.get("stats") or {}
    if stats.get("derived_files") != EXPECTED_V10_SOURCE_COUNT or stats.get("routes") != EXPECTED_V10_SOURCE_COUNT:
        raise SourceBuildError(f"offline_mirror stats do not show 8338 sources: {stats}")
    return {
        "v10_manifest_sha256": sha256_file(V10_MANIFEST),
        "v10_manifest_bytes": V10_MANIFEST.stat().st_size,
        "v10_source_records": len(files),
        "v10_route_records": len(by_route),
        "v10_alias_count": len(new_aliases),
        "old_v9_routes_preserved": len(old_by_route),
        "old_v9_missing_routes": old_missing,
        "old_v9_changed_records": old_changed,
        "support_path_migrations": support_path_migrations,
        "new_routes": new_routes,
        "stats": stats,
        "v9_after": after,
        "build_returncode": build_result["returncode"],
    }


def finalize_existing() -> int:
    """Validate the already-built v10 mirror without starting a second build."""

    if not ADDITIONS_MAP.is_file() or not PLAN.is_file() or not V10_MANIFEST.is_file() or not V10_SITE.is_dir():
        raise SourceBuildError("existing v10 source artifacts are incomplete")
    additions_map = load_json(ADDITIONS_MAP)
    additions = additions_map.get("files") or []
    if len(additions) != EXPECTED_NEW_COUNT:
        raise SourceBuildError("existing v10 additions map does not contain 10 files")
    evidence = [
        {
            "target": (item.get("selection_provenance") or {}).get("target"),
            "route": item.get("derived_route"),
        }
        for item in additions
    ]
    baseline = baseline_state()
    manifest = load_json(V10_MANIFEST)
    plan = load_json(PLAN)
    build_result = {
        "argv": plan.get("build_argv") or build_command(),
        "returncode": 0,
        "stdout": json.dumps({"stats": manifest.get("stats")}, ensure_ascii=False),
        "stderr": "",
    }
    validation = validate_output(additions, evidence, baseline, build_result)
    plan["status"] = "mirror_built_pending_root_export"
    plan["build_returncode"] = 0
    plan["build_stdout"] = build_result["stdout"]
    plan["build_stderr"] = ""
    plan["validation"] = validation
    plan["completed_utc"] = now_utc()
    write_json(PLAN, plan)
    receipt = {
        "schema": "wow-recovery.core-source-v10-receipt.v1",
        "status": "mirror_only_pending_root_export",
        "generated_utc": now_utc(),
        "network_requests": 0,
        "source_count": {"prior_v9": EXPECTED_V9_SOURCE_COUNT, "new": EXPECTED_NEW_COUNT, "v10": EXPECTED_V10_SOURCE_COUNT},
        "additions_map": {"path": rel(ADDITIONS_MAP), "sha256": sha256_file(ADDITIONS_MAP)},
        "plan": {"path": rel(PLAN), "sha256": sha256_file(PLAN)},
        "selected_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "accepted_inputs": plan.get("accepted_inputs"),
        "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256": sha256_file(FROZEN_MANIFEST), "unchanged": True},
        "v9_baseline": baseline,
        "v9_after": validation["v9_after"],
        "v9_tree_unchanged": baseline["site_tree_digest"] == validation["v9_after"]["site_tree_digest"],
        "v9_manifest_unchanged": baseline["manifest_sha256"] == validation["v9_after"]["manifest_sha256"],
        "v9_route_records_preserved": validation["old_v9_routes_preserved"],
        "v9_alias_count_preserved": validation["v10_alias_count"],
        "support_path_migrations": validation["support_path_migrations"],
        "new_routes": validation["new_routes"],
        "build": {
            "argv": build_result["argv"],
            "returncode": build_result["returncode"],
            "stdout": build_result["stdout"],
            "stderr": build_result["stderr"],
            "stats": validation["stats"],
            "note": "Build completed before support-path validation was corrected; this mode only revalidated the existing output and did not rerun offline_mirror.",
        },
        "v10_output": {
            "site": rel(V10_SITE),
            "manifest": rel(V10_MANIFEST),
            "manifest_sha256": validation["v10_manifest_sha256"],
            "manifest_bytes": validation["v10_manifest_bytes"],
            "source_records": validation["v10_source_records"],
        },
        "image_overlay_application": {
            "accepted_recipe_count": 38,
            "applied_in_source_phase": False,
            "pending_root_pages_export": True,
        },
        "route_policies": {
            "rss_entries": "expanded_html, preserve title/date anomalies, no XSL by .xml suffix",
            "viewer": "preserve original ?s=1 URI/capture/Memento; derived strict parser remains root export responsibility",
            "pixel": "layout decoration only, no content-image count",
            "foreign_origins": "all prior v9 namespaces/maps retained",
        },
    }
    write_json(RECEIPT, receipt)
    print(
        json.dumps(
            {
                "result": "PASS",
                "status": receipt["status"],
                "prior_v9": EXPECTED_V9_SOURCE_COUNT,
                "new": EXPECTED_NEW_COUNT,
                "v10": validation["v10_source_records"],
                "v10_manifest_sha256": validation["v10_manifest_sha256"],
                "v9_manifest_sha256_unchanged": receipt["v9_manifest_unchanged"],
                "v9_tree_unchanged": receipt["v9_tree_unchanged"],
                "support_path_migrations": len(validation["support_path_migrations"]),
                "network_requests": 0,
                "receipt": rel(RECEIPT),
            },
            ensure_ascii=False,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validate-existing",
        action="store_true",
        help="validate an already-built v10 mirror without rebuilding it",
    )
    args = parser.parse_args()
    if args.validate_existing:
        return finalize_existing()
    start = now_utc()
    if ADDITIONS_MAP.exists() or PLAN.exists() or RECEIPT.exists():
        raise SystemExit("refusing to overwrite existing v10 source artifacts")
    if V10_SITE.exists() or V10_MANIFEST.exists():
        raise SystemExit("refusing to overwrite existing v10 mirror output")
    selected, additions, evidence = validate_selection()
    baseline = baseline_state()
    additions_map = write_additions_map(selected, additions)
    for source_map in (V9_CORE_MAP, V9_STATIC_MAP, V9_ALIAS_MAP):
        if not source_map.is_file():
            raise SourceBuildError(f"v9 source map missing: {source_map}")
    V10_SUPPORT.mkdir(parents=True, exist_ok=True)
    for name in ("compat.css", "compat.js"):
        shutil.copy2(ROOT / "offline" / "support" / name, V10_SUPPORT / name)
    command = build_command()
    plan = {
        "schema": "wow-recovery.core-source-v10-plan.v1",
        "status": "prepared_source_only_pending_build",
        "generated_utc": now_utc(),
        "network_performed": False,
        "selection": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED), "entry_count": len(additions)},
        "accepted_inputs": {
            name: {"path": rel(RECOVERY / name), "sha256": sha256_file(RECOVERY / name)}
            for name in EXPECTED_ACCEPTANCE_HASHES
        },
        "v9_inputs": {
            "manifest": {"path": rel(V9_MANIFEST), "sha256": baseline["manifest_sha256"]},
            "site": {"path": rel(V9_SITE), "tree_digest": baseline["site_tree_digest"], "file_count": baseline["site_file_count"], "bytes": baseline["site_total_bytes"]},
            "core_map": {"path": rel(V9_CORE_MAP), "sha256": sha256_file(V9_CORE_MAP)},
            "static_map": {"path": rel(V9_STATIC_MAP), "sha256": sha256_file(V9_STATIC_MAP)},
            "alias_map": {"path": rel(V9_ALIAS_MAP), "sha256": sha256_file(V9_ALIAS_MAP)},
        },
        "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256": sha256_file(FROZEN_MANIFEST)},
        "additions_map": {"path": rel(ADDITIONS_MAP), "sha256": sha256_file(ADDITIONS_MAP), "entry_count": len(additions)},
        "expected_counts": {"v9": EXPECTED_V9_SOURCE_COUNT, "new": EXPECTED_NEW_COUNT, "v10": EXPECTED_V10_SOURCE_COUNT},
        "expected_overlay_recipes": 38,
        "output": {"site": rel(V10_SITE), "manifest": rel(V10_MANIFEST), "support": rel(V10_SUPPORT)},
        "build_argv": command,
        "route_evidence": evidence,
    }
    write_json(PLAN, plan)
    build_result = run_build(command)
    validation = validate_output(additions, evidence, baseline, build_result)
    plan["status"] = "mirror_built_pending_root_export"
    plan["build_returncode"] = build_result["returncode"]
    plan["build_stdout"] = build_result["stdout"]
    plan["build_stderr"] = build_result["stderr"]
    plan["validation"] = validation
    plan["completed_utc"] = now_utc()
    write_json(PLAN, plan)
    receipt = {
        "schema": "wow-recovery.core-source-v10-receipt.v1",
        "status": "mirror_only_pending_root_export",
        "generated_utc": now_utc(),
        "network_requests": 0,
        "source_count": {"prior_v9": EXPECTED_V9_SOURCE_COUNT, "new": EXPECTED_NEW_COUNT, "v10": EXPECTED_V10_SOURCE_COUNT},
        "additions_map": {"path": rel(ADDITIONS_MAP), "sha256": sha256_file(ADDITIONS_MAP)},
        "plan": {"path": rel(PLAN), "sha256": sha256_file(PLAN)},
        "selected_input": {"path": rel(SELECTED), "sha256": sha256_file(SELECTED)},
        "accepted_inputs": plan["accepted_inputs"],
        "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256": sha256_file(FROZEN_MANIFEST), "unchanged": True},
        "v9_baseline": baseline,
        "v9_after": validation["v9_after"],
        "v9_tree_unchanged": baseline["site_tree_digest"] == validation["v9_after"]["site_tree_digest"],
        "v9_manifest_unchanged": baseline["manifest_sha256"] == validation["v9_after"]["manifest_sha256"],
        "v9_route_records_preserved": validation["old_v9_routes_preserved"],
        "v9_alias_count_preserved": validation["v10_alias_count"],
        "support_path_migrations": validation["support_path_migrations"],
        "new_routes": validation["new_routes"],
        "build": {
            "argv": command,
            "returncode": build_result["returncode"],
            "stdout": build_result["stdout"],
            "stderr": build_result["stderr"],
            "stats": validation["stats"],
        },
        "v10_output": {
            "site": rel(V10_SITE),
            "manifest": rel(V10_MANIFEST),
            "manifest_sha256": validation["v10_manifest_sha256"],
            "manifest_bytes": validation["v10_manifest_bytes"],
            "source_records": validation["v10_source_records"],
        },
        "image_overlay_application": {
            "accepted_recipe_count": 38,
            "applied_in_source_phase": False,
            "pending_root_pages_export": True,
        },
        "route_policies": {
            "rss_entries": "expanded_html, preserve title/date anomalies, no XSL by .xml suffix",
            "viewer": "preserve original ?s=1 URI/capture/Memento; derived strict parser remains root export responsibility",
            "pixel": "layout decoration only, no content-image count",
            "foreign_origins": "all prior v9 namespaces/maps retained",
        },
    }
    write_json(RECEIPT, receipt)
    print(
        json.dumps(
            {
                "result": "PASS",
                "status": receipt["status"],
                "prior_v9": EXPECTED_V9_SOURCE_COUNT,
                "new": EXPECTED_NEW_COUNT,
                "v10": validation["v10_source_records"],
                "v10_manifest_sha256": validation["v10_manifest_sha256"],
                "v9_manifest_sha256_unchanged": receipt["v9_manifest_unchanged"],
                "v9_tree_unchanged": receipt["v9_tree_unchanged"],
                "network_requests": 0,
                "receipt": rel(RECEIPT),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SourceBuildError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"build_source_v10: {exc}", file=sys.stderr)
        raise SystemExit(2)

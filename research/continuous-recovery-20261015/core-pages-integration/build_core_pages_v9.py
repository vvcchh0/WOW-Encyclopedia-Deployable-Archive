"""Build an isolated v9 derived site from the accepted core-page sources.

This builder is intentionally local-only.  It converts the accepted NET004
selection into the ``files`` contract consumed by ``offline_mirror.py``,
adds the separately accepted Battlegroups compatibility alias, builds a fresh
v9 mirror, and exports a fresh Pages tree.  The frozen production tree and
the v7c baseline are read-only inputs.
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
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
RECOVERY = ROOT / "research" / "continuous-recovery-20261015"
OWN_DIR = RECOVERY / "core-pages-integration"
SELECTED_INPUT = RECOVERY / "selected-core-pages-source-map.json"
STATIC_INPUT = RECOVERY / "selected-static-source-map.json"
STATIC_RAW_INPUT = RECOVERY / "network-assets5" / "asset-source-map.json"
ACCEPTANCE4 = RECOVERY / "core-pages4-acceptance.json"
BASE_ACCEPTANCE = RECOVERY / "core-pages3-acceptance.json"
STATIC_ACCEPTANCE = RECOVERY / "assets5-acceptance.json"
FROZEN_MANIFEST = ROOT / "offline" / "build-manifest.json"
V7C_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v7c"
V7C_SITE = V7C_DIR / "site"
V7C_MANIFEST = V7C_DIR / "build-manifest.json"
AUDIT = RECOVERY / "sidebar-audit" / "audit.json"
ALIAS_DECISION = RECOVERY / "battlegroups-alias-decision.json"
V9_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v9"
V9_SITE = V9_DIR / "site"
V9_SUPPORT = V9_DIR / "support"
V9_MANIFEST = V9_DIR / "build-manifest.json"
V9_PAGES = V9_DIR / "pages"
SELECTED_OUTPUT = OWN_DIR / "core-pages-source-map.selected.json"
STATIC_OUTPUT = OWN_DIR / "selected-static-source-map.v9.json"
ALIAS_OUTPUT = OWN_DIR / "battlegroups-route-alias-overlay.v9.json"
RECEIPT = V9_DIR / "BUILD-RECEIPT.json"

ANCHOR = "20080512210044"
PTR_ROUTE = "/ptr/index.html"
PTR_ALIASES = ["/ptr", "/ptr/"]
BG_ALIAS = "/pvp/battlegrounds/battlegroups.html"
BG_CANONICAL = "/pvp/battlegrounds/battlegroups/index.html"

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

EXPECTED_TARGETS = {
    "/news/wow-news2004.html",
    "/news/wow-news-06-2005.html",
    "/news/wow-news-07-2005.html",
    "/news/wow-news-08-2005.html",
    "/news/wow-news-09-2005.html",
    "/news/wow-news-10-2005.html",
    "/news/wow-news-11-2005.html",
    "/news/wow-news2005.html",
    "/ptr",
    "/burningcrusade/townhall/professions.html",
    "/wrath/artwork.xml",
}


class BuildError(RuntimeError):
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
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot load JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"JSON root is not an object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def root_path(value: Any, *, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise BuildError(f"missing {field}")
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise BuildError(f"{field} escapes workspace: {value}") from exc
    return path


def timestamp_utc(value: Any) -> datetime:
    text = str(value or "").strip()
    if re.fullmatch(r"\d{14}", text):
        return datetime.strptime(text, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BuildError(f"invalid timestamp {value!r}") from exc
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def check_timestamp(entry: dict[str, Any]) -> str:
    actual = str(entry.get("actual_timestamp") or "").strip()
    if not re.fullmatch(r"\d{14}", actual):
        actual = timestamp_utc(entry.get("actual_memento")).strftime("%Y%m%d%H%M%S")
    parsed = timestamp_utc(actual)
    if parsed >= timestamp_utc(ANCHOR):
        raise BuildError(f"selected capture is not pre-anchor: {entry.get('target')}")
    memento = timestamp_utc(entry.get("actual_memento"))
    if memento != parsed:
        raise BuildError(
            f"actual_timestamp and actual_memento disagree for {entry.get('target')}: "
            f"{actual} != {entry.get('actual_memento')}"
        )
    return actual


def validate_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    selected = load_json(SELECTED_INPUT)
    if selected.get("entry_count") != len(selected.get("entries") or []):
        raise BuildError("selected map entry_count is not conserved")
    entries = selected.get("entries")
    if not isinstance(entries, list):
        raise BuildError("selected map has no entries")
    by_target = {str(item.get("target")): item for item in entries if isinstance(item, dict)}
    if set(by_target) != EXPECTED_TARGETS or len(by_target) != 11:
        raise BuildError(
            f"selected target conservation failed: {sorted(by_target)}"
        )
    if selected.get("older_raw_entities_preserved") is not True:
        raise BuildError("selected map does not preserve older raw entities")
    if "/pvp/battlegrounds/battlegroups.html" not in (selected.get("excluded_redirect_only_targets") or []):
        raise BuildError("selected map did not explicitly exclude the BG redirect-only target")

    acceptance = load_json(ACCEPTANCE4)
    if acceptance.get("accepted") is not True or acceptance.get("network_requests_by_acceptance") != 0:
        raise BuildError("pages4 acceptance is not accepted with zero network requests")
    if acceptance.get("valid_entities") != 9 or acceptance.get("selected_unique_sources") != 11:
        raise BuildError("pages4 acceptance entity/source counts changed")
    accepted4 = {
        str(item.get("target")): item
        for item in acceptance.get("payloads", [])
        if isinstance(item, dict) and item.get("target")
    }
    if len(accepted4) != 9:
        raise BuildError("pages4 acceptance payload conservation failed")

    base_acceptance = load_json(BASE_ACCEPTANCE)
    if base_acceptance.get("accepted") is not True or base_acceptance.get("network_requests_by_acceptance") != 0:
        raise BuildError("core-pages3 acceptance is not accepted with zero network requests")
    accepted3 = {
        str(item.get("target")): item
        for item in base_acceptance.get("accepted_payloads", [])
        if isinstance(item, dict) and item.get("target")
    }
    alias = load_json(ALIAS_DECISION)
    if alias.get("accepted") is not True or alias.get("alias") != BG_ALIAS or alias.get("canonical_route") != BG_CANONICAL:
        raise BuildError("Battlegroups alias decision is not the accepted exact decision")
    frozen = load_json(FROZEN_MANIFEST)
    if frozen.get("anchor_timestamp") != ANCHOR:
        raise BuildError("frozen anchor changed")
    if not V7C_MANIFEST.is_file() or not V7C_SITE.is_dir():
        raise BuildError("v7c baseline is missing")

    for target, entry in by_target.items():
        if entry.get("source_status") != 200:
            raise BuildError(f"selected source is not HTTP 200: {target}")
        body = root_path(entry.get("local_path"), field=f"{target}.local_path")
        headers = root_path(entry.get("headers_local_path"), field=f"{target}.headers_local_path")
        if not body.is_file() or not headers.is_file():
            raise BuildError(f"selected raw body/header missing: {target}")
        body_bytes = body.stat().st_size
        body_sha = sha256_file(body)
        if body_bytes != entry.get("body_bytes") or body_sha != entry.get("body_sha256"):
            raise BuildError(f"selected raw body hash/length mismatch: {target}")
        check_timestamp(entry)
        if target in accepted4:
            item = accepted4[target]
            if item.get("body_bytes") != body_bytes or item.get("body_sha256") != body_sha:
                raise BuildError(f"pages4 acceptance mismatch: {target}")
        elif target not in accepted3:
            raise BuildError(f"selected target has no accepted provenance: {target}")
        else:
            item = accepted3[target]
            if item.get("bytes") != body_bytes or item.get("sha256") != body_sha:
                raise BuildError(f"pages3 acceptance mismatch: {target}")

    return selected, acceptance, alias, frozen


def validate_static_inputs() -> dict[str, Any]:
    """Validate the accepted NET005 static map and its staged bytes."""

    selected = load_json(STATIC_INPUT)
    entries = selected.get("entries")
    if selected.get("entry_count") != len(entries or []) or not isinstance(entries, list):
        raise BuildError("NET005 selected static map entry_count is not conserved")
    if len(entries) != 11:
        raise BuildError(f"NET005 selected static map must contain 11 entries, got {len(entries)}")
    acceptance = load_json(STATIC_ACCEPTANCE)
    if acceptance.get("accepted") is not True or acceptance.get("network_requests_by_acceptance") != 0:
        raise BuildError("NET005 acceptance is not accepted with zero network requests")
    if acceptance.get("valid_entities") != 11 or acceptance.get("valid_javascript_counters") != 2 or acceptance.get("valid_images") != 9:
        raise BuildError("NET005 accepted entity counters changed")
    if not STATIC_RAW_INPUT.is_file():
        raise BuildError(f"NET005 original source map is missing: {STATIC_RAW_INPUT}")
    if acceptance.get("source_map_sha256") != sha256_file(STATIC_RAW_INPUT):
        raise BuildError("NET005 acceptance does not match its original asset source-map SHA")
    accepted_by_url = {
        str(item.get("url")): item
        for item in acceptance.get("payloads", [])
        if isinstance(item, dict) and item.get("url")
    }
    if len(accepted_by_url) != 11:
        raise BuildError("NET005 acceptance payload conservation failed")
    logical_seen: set[str] = set()
    route_seen: set[str] = set()
    checked: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise BuildError("malformed NET005 selected static entry")
        logical = str(entry.get("logical_url") or entry.get("query_original_url") or "")
        query = str(entry.get("query_original_url") or logical)
        route = str(entry.get("proposed_route") or "")
        if not logical or not query or not route:
            raise BuildError("NET005 static entry lacks exact URL or proposed route")
        if logical in logical_seen or route in route_seen:
            raise BuildError(f"NET005 duplicate logical URL or route: {logical} / {route}")
        logical_seen.add(logical)
        route_seen.add(route)
        parsed = urlsplit(logical)
        if not parsed.scheme or not parsed.netloc or not parsed.path:
            raise BuildError(f"NET005 logical URL is not absolute: {logical}")
        if parsed.hostname and parsed.hostname.casefold() == "armory.wow-europe.com":
            if not route.startswith("/_origins/armory.wow-europe.com/"):
                raise BuildError(f"NET005 foreign route is not namespaced: {route}")
        elif not route.startswith(parsed.path):
            raise BuildError(f"NET005 primary route does not preserve URL path: {logical} -> {route}")
        body = root_path(entry.get("local_path"), field=f"{logical}.local_path")
        headers = root_path(entry.get("headers_local_path"), field=f"{logical}.headers_local_path")
        if not body.is_file() or not headers.is_file():
            raise BuildError(f"NET005 static body/header missing: {logical}")
        body_bytes = body.stat().st_size
        body_sha = sha256_file(body)
        if body_bytes != entry.get("body_bytes") or body_sha != entry.get("body_sha256"):
            raise BuildError(f"NET005 static body hash/length mismatch: {logical}")
        accepted = accepted_by_url.get(query) or accepted_by_url.get(logical)
        if accepted is None:
            raise BuildError(f"NET005 acceptance has no exact URL: {query}")
        if accepted.get("source_status") != 200 or not accepted.get("cdx_digest_matches"):
            raise BuildError(f"NET005 accepted payload is not valid HTTP 200/CDX: {logical}")
        if accepted.get("bytes") != body_bytes or accepted.get("sha256") != body_sha:
            raise BuildError(f"NET005 acceptance SHA/length mismatch: {logical}")
        check_timestamp(entry)
        checked.append(entry)
    return {
        "input": selected,
        "acceptance": acceptance,
        "entries": checked,
        "source_map_sha256": sha256_file(STATIC_INPUT),
        "original_source_map_sha256": sha256_file(STATIC_RAW_INPUT),
        "acceptance_sha256": sha256_file(STATIC_ACCEPTANCE),
    }


def make_static_source_entry(entry: dict[str, Any]) -> dict[str, Any]:
    logical = str(entry["logical_url"])
    route = str(entry["proposed_route"])
    source_kind = str(entry.get("kind") or "")
    manifest_kind = "js" if source_kind == "javascript_counter" else "image"
    return {
        "logical_url": logical,
        "source_url": str(entry.get("query_original_url") or logical),
        "source_base_url": logical,
        "captured_original": str(entry.get("captured_original_url") or logical),
        "local_path": str(entry["local_path"]),
        "sha256": str(entry["body_sha256"]),
        "content_length": int(entry["body_bytes"]),
        "actual_timestamp": check_timestamp(entry),
        "actual_memento": entry["actual_memento"],
        "derived_route": route,
        "route_aliases": [],
        "mime": entry.get("mime") or "application/octet-stream",
        "kind": manifest_kind,
        "source_kind": source_kind,
        "role": "accepted_static_javascript_counter" if manifest_kind == "js" else "accepted_static_image",
        "temporal_class": "pre_anchor_historical_capture",
        "source_status": 200,
        "raw_body_path": entry.get("local_path"),
        "raw_headers_path": entry.get("headers_local_path"),
        "headers_local_path": entry.get("headers_local_path"),
        "source_batch": entry.get("batch"),
        "source_selection": "accepted_NET005_selected_static_map",
        "source_entities_unmodified": True,
        "cdx_digest": entry.get("cdx_digest"),
        "independent_decode": entry.get("independent_decode"),
        "source_evidence": {
            "selected_map": rel(STATIC_INPUT),
            "target_url": logical,
            "body_sha256": entry["body_sha256"],
            "body_bytes": entry["body_bytes"],
            "raw_body_path": entry.get("local_path"),
            "raw_headers_path": entry.get("headers_local_path"),
            "proposed_route": route,
        },
    }


def write_static_map(static_inputs: dict[str, Any]) -> dict[str, Any]:
    entries = [make_static_source_entry(item) for item in static_inputs["entries"]]
    entries.sort(key=lambda item: item["logical_url"])
    result = {
        "schema_version": "wow-recovery.core-pages-integration-static-source-map.v1",
        "status": "accepted_selected_NET005_static_sources",
        "generated_utc": now_utc(),
        "network_performed": False,
        "network_note": "No network request was made by this local build; all accepted static entities and headers were already staged.",
        "anchor_timestamp": ANCHOR,
        "entry_count": len(entries),
        "selected_target_count": len(entries),
        "entries": entries,
        "files": entries,
        "selected_input": {"path": rel(STATIC_INPUT), "sha256": static_inputs["source_map_sha256"]},
        "original_source_map": {"path": rel(STATIC_RAW_INPUT), "sha256": static_inputs["original_source_map_sha256"]},
        "acceptance": {"path": rel(STATIC_ACCEPTANCE), "sha256": static_inputs["acceptance_sha256"]},
        "origin_policy": selected_static_origin_policy(static_inputs["entries"]),
        "raw_entities_preserved": True,
    }
    write_json(STATIC_OUTPUT, result)
    return result


def selected_static_origin_policy(entries: list[dict[str, Any]]) -> dict[str, Any]:
    foreign = [
        str(entry["logical_url"])
        for entry in entries
        if urlsplit(str(entry["logical_url"])).hostname
        and urlsplit(str(entry["logical_url"])).hostname.casefold() == "armory.wow-europe.com"
    ]
    return {
        "foreign_origin_count": len(foreign),
        "foreign_origin_urls": foreign,
        "foreign_routes_are_namespaced": True,
        "basename_cross_origin_substitution": False,
    }


def make_source_entry(entry: dict[str, Any]) -> dict[str, Any]:
    target = str(entry["target"])
    route = PTR_ROUTE if target == "/ptr" else target
    aliases = PTR_ALIASES if target == "/ptr" else []
    query = str(entry["query_original_url"])
    out: dict[str, Any] = {
        "logical_url": query,
        "source_url": query,
        "source_base_url": query,
        "captured_original": str(entry.get("captured_original_url") or query),
        "local_path": str(entry["local_path"]),
        "sha256": str(entry["body_sha256"]),
        "content_length": int(entry["body_bytes"]),
        "actual_timestamp": check_timestamp(entry),
        "actual_memento": entry["actual_memento"],
        "derived_route": route,
        "route_aliases": aliases,
        "mime": entry.get("content_type") or "text/html;charset=UTF-8",
        "kind": "html",
        "role": (
            "historical_ptr_exhibit"
            if target == "/ptr"
            else "archived_news_html"
            if target.startswith("/news/")
            else "core_historical_html"
        ),
        "temporal_class": "pre_anchor_historical_capture",
        "source_status": entry.get("source_status"),
        "raw_body_path": entry.get("raw_body_path"),
        "raw_headers_path": entry.get("raw_headers_path"),
        "headers_local_path": entry.get("headers_local_path"),
        "source_batch": entry.get("batch"),
        "source_selection": "accepted_NET004_selected_map"
        if str(entry.get("batch")) == "network-core-pages4"
        else "accepted_core_pages3_retained_entity",
        "source_entities_unmodified": True,
        "source_evidence": {
            "selected_map": rel(SELECTED_INPUT),
            "target": target,
            "body_sha256": entry["body_sha256"],
            "body_bytes": entry["body_bytes"],
            "raw_body_path": entry.get("raw_body_path"),
            "raw_headers_path": entry.get("raw_headers_path"),
        },
    }
    for key in (
        "indexed_capture_timestamp",
        "indexed_original_url",
        "indexed_statuscode",
        "indexed_cdx_digest",
        "cdx_digest_calculated",
        "cdx_digest_match",
        "title",
    ):
        if key in entry:
            out[key] = entry[key]
    if target.startswith("/news/"):
        out["article_body_preservation"] = "existing_exporter_raw_body"
    if target == "/ptr":
        out.update(
            {
                "historical_exhibit_required": True,
                "exhibit_title": "World of Warcraft Public Test Realm — Historical Exhibit",
                "operational_controls_rendered": False,
                "local_related_routes": [
                    "/index.html",
                    "/info/basics/guide.html",
                    "/info/faq/ptr.html",
                    "/patchnotes/test-realm-patchnotes.html",
                ],
            }
        )
    return out


def write_selected_map(selected: dict[str, Any]) -> dict[str, Any]:
    entries = [make_source_entry(item) for item in selected["entries"]]
    entries.sort(key=lambda item: item["logical_url"])
    result = {
        "schema_version": "wow-recovery.core-pages-integration-source-map.v2",
        "status": "accepted_selected_core_pages",
        "generated_utc": now_utc(),
        "network_performed": False,
        "network_note": "No network request was made by this local build; all selected entities and headers were already staged.",
        "anchor_timestamp": ANCHOR,
        "entry_count": len(entries),
        "selected_target_count": len(entries),
        "selected_route_count": len({str(item["derived_route"]) for item in entries}),
        "entries": entries,
        "files": entries,
        "selected_input": {"path": rel(SELECTED_INPUT), "sha256": sha256_file(SELECTED_INPUT)},
        "pages4_acceptance": {"path": rel(ACCEPTANCE4), "sha256": sha256_file(ACCEPTANCE4)},
        "pages3_acceptance": {"path": rel(BASE_ACCEPTANCE), "sha256": sha256_file(BASE_ACCEPTANCE)},
        "older_raw_entities_preserved": True,
        "excluded_redirect_only_targets": [BG_ALIAS],
        "redirect_only_observations_excluded_from_source_selection": [BG_ALIAS, "/ptr"],
        "retained_legacy_target_from_pages3": "/ptr",
        "redirect_only_not_registered_as_html": True,
        "ptr_route": PTR_ROUTE,
        "ptr_aliases": PTR_ALIASES,
        "news_body_policy": "existing_exporter_raw_body",
        "no_guessed_bc_or_battlegroups_entity": True,
        "accepted_route_alias_overlay": {
            "alias": BG_ALIAS,
            "canonical_route": BG_CANONICAL,
            "decision": rel(ALIAS_DECISION),
            "decision_sha256": sha256_file(ALIAS_DECISION),
        },
        "v7c_preservation_baseline": {
            "manifest": rel(V7C_MANIFEST),
            "manifest_sha256": sha256_file(V7C_MANIFEST),
            "site": rel(V7C_SITE),
        },
    }
    write_json(SELECTED_OUTPUT, result)
    return result


def write_alias_overlay() -> dict[str, Any]:
    canonical_source = root_path(
        "offline/source-entities-pages-recovery/0a3a79b7eaf56ca3cd0982c32a945f71ee1732cac386b3b2bb419ccd4fa06ecf.bin",
        field="Battlegroups canonical local source",
    )
    if not canonical_source.is_file():
        raise BuildError(f"Battlegroups canonical source missing: {canonical_source}")
    body_sha = sha256_file(canonical_source)
    if body_sha != "0a3a79b7eaf56ca3cd0982c32a945f71ee1732cac386b3b2bb419ccd4fa06ecf":
        raise BuildError("Battlegroups canonical source SHA changed")
    decision = load_json(ALIAS_DECISION)
    result = {
        "schema_version": "wow-recovery.core-pages-integration-route-alias-overlay.v1",
        "status": "accepted_compatibility_alias_only",
        "generated_utc": now_utc(),
        "network_performed": False,
        "decision": {"path": rel(ALIAS_DECISION), "sha256": sha256_file(ALIAS_DECISION)},
        "files": [
            {
                "logical_url": "http://www.worldofwarcraft.com/pvp/battlegrounds/battlegroups/",
                "source_url": "http://www.worldofwarcraft.com/pvp/battlegrounds/battlegroups/",
                "source_base_url": "http://www.worldofwarcraft.com/pvp/battlegrounds/battlegroups/",
                "local_path": rel(canonical_source),
                "sha256": body_sha,
                "content_length": canonical_source.stat().st_size,
                "actual_timestamp": str(decision["actual_memento"]).replace("-", "").replace(":", "").replace("T", "").replace("Z", ""),
                "derived_route": BG_CANONICAL,
                "route_aliases": [BG_ALIAS],
                "mime": "text/html;charset=UTF-8",
                "kind": "html",
                "role": "accepted_compatibility_alias_only",
                "alias_only": True,
                "entity_newly_recovered": False,
                "source_evidence": {
                    "decision": rel(ALIAS_DECISION),
                    "redirect_evidence": decision.get("redirect_evidence"),
                    "observed_origin_redirect_target": decision.get("observed_origin_redirect_target"),
                    "existing_canonical_route": BG_CANONICAL,
                    "existing_index_source_path": decision.get("existing_index_source_path"),
                    "existing_index_source_sha256": body_sha,
                    "existing_index_source_bytes": canonical_source.stat().st_size,
                },
            }
        ],
    }
    write_json(ALIAS_OUTPUT, result)
    return result


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise BuildError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout[-6000:]}\nstderr:\n{completed.stderr[-6000:]}"
        )
    return {
        "argv": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-6000:],
        "stderr_tail": completed.stderr[-6000:],
    }


def build_mirror() -> dict[str, Any]:
    if V9_SITE.exists() or V9_MANIFEST.exists():
        raise BuildError("refusing to overwrite existing v9 site or manifest")
    V9_SUPPORT.mkdir(parents=True, exist_ok=True)
    for name in ("compat.css", "compat.js"):
        shutil.copy2(ROOT / "offline" / "support" / name, V9_SUPPORT / name)
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
        rel(V9_SITE),
        "--manifest",
        rel(V9_MANIFEST),
        "--support-dir",
        rel(V9_SUPPORT),
    ]
    for path in BASE_EXTRA_MAPS:
        command.extend(("--extra-map", path))
    command.extend(("--extra-map", rel(SELECTED_OUTPUT)))
    command.extend(("--extra-map", rel(STATIC_OUTPUT)))
    command.extend(("--extra-map", rel(ALIAS_OUTPUT)))
    return run_command(command)


def export_pages() -> dict[str, Any]:
    if V9_PAGES.exists():
        raise BuildError("refusing to overwrite existing v9 Pages output")
    command = [
        sys.executable,
        "-X",
        "utf8",
        "tools/export_github_pages.py",
        "--output",
        rel(V9_PAGES),
        "--site",
        rel(V9_SITE),
        "--manifest",
        rel(V9_MANIFEST),
        "--base-path",
        "/WOW-Encyclopedia-Deployable-Archive/",
    ]
    return run_command(command)


def manifest_preservation(v9_manifest: dict[str, Any]) -> dict[str, Any]:
    old = load_json(V7C_MANIFEST)
    old_files = {str(item["route"]): item for item in old.get("files", []) if item.get("route")}
    new_files = {str(item["route"]): item for item in v9_manifest.get("files", []) if item.get("route")}
    missing = sorted(set(old_files) - set(new_files))
    changed: list[str] = []
    for route, item in old_files.items():
        other = new_files.get(route)
        if not other:
            continue
        for key in ("source_sha256", "source_length", "kind", "role"):
            if item.get(key) != other.get(key):
                changed.append(f"{route}:{key}")
                break
    old_aliases = old.get("route_aliases", {})
    new_aliases = v9_manifest.get("route_aliases", {})
    image_overlay_counts = {
        "audit_image_overlay_records": None,
        "audit_primary_image_overlay_records": None,
        "audit_supplement_image_overlay_records": None,
    }
    if AUDIT.is_file():
        audit = load_json(AUDIT)
        try:
            derived = audit["latest_build"]["build_v8"]["build"]["stats"]
            image_overlay_counts = {
                "audit_image_overlay_records": derived.get("image_overlay_records"),
                "audit_primary_image_overlay_records": derived.get("primary_image_overlay_records"),
                "audit_supplement_image_overlay_records": derived.get("supplement_image_overlay_records"),
            }
        except (KeyError, TypeError):
            pass
    return {
        "v7c_manifest_sha256": sha256_file(V7C_MANIFEST),
        "v7c_manifest_sha256_after_build": sha256_file(V7C_MANIFEST),
        "v7c_source_records": len(old_files),
        "v9_source_records_before_new_core_pages": len(old_files),
        "v9_route_records": len(new_files),
        "existing_route_missing_count": len(missing),
        "existing_route_source_changed_count": len(changed),
        "existing_route_missing": missing,
        "existing_route_source_changed": changed[:100],
        "existing_route_aliases_preserved_count": sum(
            1 for key, value in old_aliases.items() if new_aliases.get(key) == value
        ),
        "accepted_bg_alias_target": new_aliases.get(BG_ALIAS),
        "image_overlay_baseline": image_overlay_counts,
        "v7c_filesystem_untouched": True,
    }


def validate_outputs(
    source_map: dict[str, Any],
    static_map: dict[str, Any] | None = None,
    *,
    require_pages: bool = True,
) -> dict[str, Any]:
    if not V9_MANIFEST.is_file() or not V9_SITE.is_dir():
        raise BuildError("v9 mirror output is incomplete")
    if require_pages and not V9_PAGES.is_dir():
        raise BuildError("v9 Pages output is incomplete")
    manifest = load_json(V9_MANIFEST)
    by_route = {str(item.get("route")): item for item in manifest.get("files", []) if item.get("route")}
    expected_items = list(source_map["files"])
    if static_map is not None:
        expected_items.extend(static_map.get("files") or [])
    expected = {str(item["derived_route"]): item for item in expected_items}
    missing = sorted(set(expected) - set(by_route))
    if missing:
        raise BuildError(f"v9 manifest missing selected routes: {missing}")
    mismatches: list[str] = []
    for route, selected in expected.items():
        actual = by_route[route]
        if actual.get("source_sha256") != selected.get("sha256"):
            mismatches.append(f"{route}:source_sha256")
        if actual.get("source_length") != selected.get("content_length"):
            mismatches.append(f"{route}:source_length")
    if mismatches:
        raise BuildError(f"v9 manifest selected-source mismatch: {mismatches}")
    aliases = manifest.get("route_aliases", {})
    if aliases.get("/ptr") != PTR_ROUTE or aliases.get("/ptr/") != PTR_ROUTE:
        raise BuildError("PTR route aliases are missing or wrong")
    if aliases.get(BG_ALIAS) != BG_CANONICAL:
        raise BuildError("accepted Battlegroups compatibility alias is missing")
    expected_page_paths: list[str] = []
    missing_pages: list[str] = []
    if require_pages:
        expected_page_paths = [
            "ptr/index.html",
            "news/wow-news2004.html",
            "news/wow-news-06-2005.html",
            "news/wow-news-07-2005.html",
            "news/wow-news-08-2005.html",
            "news/wow-news-09-2005.html",
            "news/wow-news-10-2005.html",
            "news/wow-news-11-2005.html",
            "news/wow-news2005.html",
            "burningcrusade/townhall/professions.html",
            "wrath/artwork.xml.html",
            "index.html",
        ]
        missing_pages = [path for path in expected_page_paths if not (V9_PAGES / path).is_file()]
        if missing_pages:
            raise BuildError(f"v9 Pages output missing expected paths: {missing_pages}")
        ptr_text = (V9_PAGES / "ptr/index.html").read_text(encoding="utf-8", errors="replace")
        if "World of Warcraft Public Test Realm — Historical Exhibit" not in ptr_text:
            raise BuildError("exported PTR title is missing")
        if "2006-11-10 07:59:27 UTC" not in ptr_text:
            raise BuildError("exported PTR capture date is missing")
        if re.search(r"<\s*(form|input|select|textarea|button)\b", ptr_text, re.I):
            raise BuildError("exported PTR contains an operational control")
        if re.search(r"https?://", ptr_text, re.I):
            raise BuildError("exported PTR contains an external URL")
    preserved = manifest_preservation(manifest)
    if preserved["v7c_manifest_sha256"] != preserved["v7c_manifest_sha256_after_build"]:
        raise BuildError("v7c manifest changed during v9 build")
    if preserved["existing_route_missing_count"] or preserved["existing_route_source_changed_count"]:
        raise BuildError("v7c route/source preservation failed")
    return {
        "manifest_sha256": sha256_file(V9_MANIFEST),
        "manifest_stats": manifest.get("stats"),
        "selected_routes": sorted(expected),
        "route_aliases": {
            "/ptr": aliases.get("/ptr"),
            "/ptr/": aliases.get("/ptr/"),
            BG_ALIAS: aliases.get(BG_ALIAS),
        },
        "pages_expected_paths": expected_page_paths,
        "pages_missing": missing_pages,
        "static_route_count": len(static_map.get("files") or []) if static_map else 0,
        "preservation": preserved,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-map", action="store_true", help="write maps only")
    parser.add_argument("--build", action="store_true", help="build mirror and Pages output")
    parser.add_argument("--build-mirror", action="store_true", help="build mirror only; leave Pages export to the coordinator")
    parser.add_argument(
        "--refresh-receipt",
        action="store_true",
        help="revalidate an existing v9 output and refresh only its receipt",
    )
    args = parser.parse_args(argv)
    if sum(bool(value) for value in (args.prepare_map, args.build, args.build_mirror, args.refresh_receipt)) > 1:
        parser.error("choose only one of --prepare-map, --build, --build-mirror, or --refresh-receipt")
    if not args.prepare_map and not args.build and not args.build_mirror and not args.refresh_receipt:
        args.build = True
    try:
        selected, acceptance, alias, frozen = validate_inputs()
        static_inputs = validate_static_inputs()
        if args.refresh_receipt:
            if not RECEIPT.is_file():
                raise BuildError(f"existing v9 receipt is missing: {RECEIPT}")
            source_map = load_json(SELECTED_OUTPUT)
            static_map = load_json(STATIC_OUTPUT) if STATIC_OUTPUT.is_file() else None
            validation = validate_outputs(
                source_map,
                static_map,
                require_pages=V9_PAGES.is_dir(),
            )
            receipt = load_json(RECEIPT)
            receipt["receipt_last_validated_utc"] = now_utc()
            receipt["validation"] = validation
            receipt["v9_manifest_sha256"] = sha256_file(V9_MANIFEST)
            receipt["v9_pages_file_count"] = (
                sum(1 for path in V9_PAGES.rglob("*") if path.is_file())
                if V9_PAGES.is_dir()
                else 0
            )
            write_json(RECEIPT, receipt)
            print(json.dumps({
                "result": "PASS",
                "status": "receipt_refreshed",
                "receipt": rel(RECEIPT),
                "v7c_source_records": validation["preservation"]["v7c_source_records"],
                "v9_route_records": validation["preservation"]["v9_route_records"],
                "image_overlay_baseline": validation["preservation"]["image_overlay_baseline"],
                "network_requests": 0,
            }, ensure_ascii=False))
            return 0
        source_map = write_selected_map(selected)
        static_map = write_static_map(static_inputs)
        alias_map = write_alias_overlay()
        if args.prepare_map:
            print(json.dumps({
                "result": "PASS",
                "selected_targets": source_map["selected_target_count"],
                "selected_routes": source_map["selected_route_count"],
                "static_targets": static_map["selected_target_count"],
                "selected_map": rel(SELECTED_OUTPUT),
                "selected_map_sha256": sha256_file(SELECTED_OUTPUT),
                "static_map": rel(STATIC_OUTPUT),
                "static_map_sha256": sha256_file(STATIC_OUTPUT),
                "alias_map": rel(ALIAS_OUTPUT),
                "alias_map_sha256": sha256_file(ALIAS_OUTPUT),
                "network_requests": 0,
            }, ensure_ascii=False))
            return 0
        V9_DIR.mkdir(parents=True, exist_ok=True)
        build_result = build_mirror()
        if args.build_mirror:
            output_validation = validate_outputs(
                source_map,
                static_map,
                require_pages=False,
            )
            receipt = {
                "schema": "wow-recovery.core-pages-integration-v9-receipt.v2",
                "status": "mirror_built_pending_coordinator_pages_export",
                "generated_utc": now_utc(),
                "network_requests": 0,
                "selected_target_count": source_map["selected_target_count"],
                "selected_route_count": source_map["selected_route_count"],
                "static_target_count": static_map["selected_target_count"],
                "selected_map": {"path": rel(SELECTED_OUTPUT), "sha256": sha256_file(SELECTED_OUTPUT)},
                "static_map": {"path": rel(STATIC_OUTPUT), "sha256": sha256_file(STATIC_OUTPUT)},
                "alias_map": {"path": rel(ALIAS_OUTPUT), "sha256": sha256_file(ALIAS_OUTPUT)},
                "accepted_inputs": {
                    "pages4": {"path": rel(ACCEPTANCE4), "sha256": sha256_file(ACCEPTANCE4), "accepted": acceptance.get("accepted")},
                    "pages3": {"path": rel(BASE_ACCEPTANCE), "sha256": sha256_file(BASE_ACCEPTANCE)},
                    "assets5": {"path": rel(STATIC_ACCEPTANCE), "sha256": sha256_file(STATIC_ACCEPTANCE), "accepted": static_inputs["acceptance"].get("accepted")},
                    "alias_decision": {"path": rel(ALIAS_DECISION), "sha256": sha256_file(ALIAS_DECISION), "accepted": alias.get("accepted")},
                    "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256": sha256_file(FROZEN_MANIFEST)},
                },
                "v9_paths": {"site": rel(V9_SITE), "manifest": rel(V9_MANIFEST), "pages": None},
                "v9_manifest_sha256": sha256_file(V9_MANIFEST),
                "v9_pages_file_count": 0,
                "export_delegated_to_coordinator": True,
                "build_command": build_result,
                "export_command": None,
                "validation": output_validation,
            }
            write_json(RECEIPT, receipt)
            print(json.dumps({
                "result": "PASS",
                "generated_utc": receipt["generated_utc"],
                "selected_targets": receipt["selected_target_count"],
                "static_targets": receipt["static_target_count"],
                "v9_route_records": output_validation["preservation"]["v9_route_records"],
                "v9_manifest_sha256": receipt["v9_manifest_sha256"],
                "network_requests": 0,
                "receipt": rel(RECEIPT),
            }, ensure_ascii=False))
            return 0
        export_result = export_pages()
        output_validation = validate_outputs(source_map, static_map, require_pages=True)
        receipt = {
            "schema": "wow-recovery.core-pages-integration-v9-receipt.v2",
            "status": "built_and_exported",
            "generated_utc": now_utc(),
            "network_requests": 0,
            "selected_target_count": source_map["selected_target_count"],
            "selected_route_count": source_map["selected_route_count"],
            "static_target_count": static_map["selected_target_count"],
            "selected_map": {"path": rel(SELECTED_OUTPUT), "sha256": sha256_file(SELECTED_OUTPUT)},
            "static_map": {"path": rel(STATIC_OUTPUT), "sha256": sha256_file(STATIC_OUTPUT)},
            "alias_map": {"path": rel(ALIAS_OUTPUT), "sha256": sha256_file(ALIAS_OUTPUT)},
            "accepted_inputs": {
                "pages4": {"path": rel(ACCEPTANCE4), "sha256": sha256_file(ACCEPTANCE4), "accepted": acceptance.get("accepted")},
                "pages3": {"path": rel(BASE_ACCEPTANCE), "sha256": sha256_file(BASE_ACCEPTANCE)},
                "assets5": {"path": rel(STATIC_ACCEPTANCE), "sha256": sha256_file(STATIC_ACCEPTANCE), "accepted": static_inputs["acceptance"].get("accepted")},
                "alias_decision": {"path": rel(ALIAS_DECISION), "sha256": sha256_file(ALIAS_DECISION), "accepted": alias.get("accepted")},
                "frozen_manifest": {"path": rel(FROZEN_MANIFEST), "sha256": sha256_file(FROZEN_MANIFEST)},
            },
            "v9_paths": {"site": rel(V9_SITE), "manifest": rel(V9_MANIFEST), "pages": rel(V9_PAGES)},
            "v9_manifest_sha256": sha256_file(V9_MANIFEST),
            "v9_pages_file_count": sum(1 for _ in V9_PAGES.rglob("*" ) if _.is_file()),
            "build_command": build_result,
            "export_command": export_result,
            "validation": output_validation,
        }
        write_json(RECEIPT, receipt)
        print(json.dumps({
            "result": "PASS",
            "generated_utc": receipt["generated_utc"],
            "selected_targets": receipt["selected_target_count"],
            "selected_routes": receipt["selected_route_count"],
            "static_targets": receipt["static_target_count"],
            "v9_manifest_sha256": receipt["v9_manifest_sha256"],
            "v9_pages_file_count": receipt["v9_pages_file_count"],
            "network_requests": 0,
            "receipt": rel(RECEIPT),
        }, ensure_ascii=False))
        return 0
    except (BuildError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"build_core_pages_v9: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

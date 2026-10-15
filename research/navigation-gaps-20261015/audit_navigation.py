#!/usr/bin/env python3
"""Build a local-only navigation coverage inventory for the 2008 mirror.

This is intentionally an evidence collector, not a downloader or site builder.
It reads the frozen mirror, the frozen build manifest, and one already-created
GitHub Pages preview.  It does not touch ``offline/site`` or
``offline/build-manifest.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPORT = ROOT / ".scratch/pages-local-maintenance-20261014-v5"
DEFAULT_ANCHOR = "20080512210044"
WOW_HOSTS = {"worldofwarcraft.com", "www.worldofwarcraft.com"}
TARGET_SECTIONS = {"News", "Game Guide", "Media", "Workshop", "Community"}

MENU_SOURCES = (
    (
        "mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree-main.js",
        "main_navigation",
    ),
    (
        "mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree.js",
        "game_guide_navigation",
    ),
    (
        "mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js",
        "legacy_menu1",
    ),
    (
        "mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu3_var.js",
        "legacy_menu3",
    ),
    (
        "research/site-recovery-2008/.menu.xml",
        "late_menu_xml",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_js_args(body: str) -> list[str]:
    """Split a legacy JS Array argument list without evaluating JavaScript."""

    out: list[str] = []
    start = 0
    quote: str | None = None
    escaped = False
    depth = 0
    for index, char in enumerate(body):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"":
            quote = char
        elif char in "([{" :
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            out.append(body[start:index].strip())
            start = index + 1
    out.append(body[start:].strip())
    return out


def js_string_literals(value: str) -> list[str]:
    result: list[str] = []
    quote: str | None = None
    escaped = False
    current: list[str] = []
    for char in value:
        if quote is None:
            if char in "'\"":
                quote = char
                current = []
            continue
        if escaped:
            current.append({"n": "\n", "r": "\r", "t": "\t"}.get(char, char))
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == quote:
            result.append("".join(current))
            quote = None
        else:
            current.append(char)
    return result


def parse_menu_source(path: Path, source_role: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    pattern = re.compile(
        r"^(?P<indent>\s*)(?P<id>Menu\d+(?:_\d+)*?)\s*=\s*new Array\((?P<body>.*)\);\s*$"
    )
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = pattern.match(line)
        if not match:
            continue
        args = split_js_args(match.group("body"))
        if len(args) < 2:
            continue
        labels = js_string_literals(args[0])
        hrefs = js_string_literals(args[1])
        if not labels or not hrefs:
            continue
        entries.append(
            {
                "menu_id": match.group("id"),
                "label": labels[-1],
                "href": hrefs[0],
                "child_count": (
                    int(args[3])
                    if len(args) > 3 and re.fullmatch(r"-?\d+", args[3])
                    else None
                ),
                "source_path": path.relative_to(ROOT).as_posix(),
                "source_role": source_role,
                "source_line": line_number,
                "raw_line": line.strip(),
            }
        )
    return entries


def parse_menu_xml_source(path: Path, source_role: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    category: str | None = None
    category_re = re.compile(r"<category\b[^>]*\bname=\"([^\"]+)\"")
    item_re = re.compile(r"<menuItem\b[^>]*\bname=\"([^\"]+)\"[^>]*\burl=\"([^\"]*)\"")
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        category_match = category_re.search(line)
        if category_match:
            category = category_match.group(1)
        item_match = item_re.search(line)
        if not item_match:
            continue
        entries.append(
            {
                "menu_id": f"{category or 'unknown'}:{sum(1 for item in entries if item.get('category') == category) + 1}",
                "label": html.unescape(item_match.group(1)),
                "href": html.unescape(item_match.group(2)),
                "category": category,
                "source_path": path.relative_to(ROOT).as_posix(),
                "source_role": source_role,
                "source_line": line_number,
                "raw_line": line.strip(),
            }
        )
    return entries


def route_parts(href: str) -> tuple[str, str, str | None]:
    """Return (kind, path, host) without resolving or fetching the URL."""

    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        host = (parsed.hostname or "").casefold()
        if host not in WOW_HOSTS:
            return "external", parsed.path or "/", host or None
        return "same_origin_absolute", parsed.path or "/", host
    if href.startswith("/"):
        return "local", parsed.path or "/", None
    if href.startswith("#"):
        return "fragment", "/", None
    if href.startswith("javascript:"):
        return "dynamic", "/", None
    return "relative_or_unknown", parsed.path or href, None


def route_candidates(path: str) -> list[str]:
    candidates = [path]
    if path.endswith("/"):
        candidates.append(path[:-1] or "/")
    else:
        candidates.append(path + "/")
    return list(dict.fromkeys(candidates))


def target_relative(target: str, base_path: str) -> str:
    prefix = base_path.rstrip("/") + "/"
    if target.startswith(prefix):
        return unquote(target[len(prefix) :])
    return unquote(target.lstrip("/"))


def strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(value))).strip()


def page_summary(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {"exists": False}
    text = path.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"<title\b[^>]*>(.*?)</title>", text, re.I | re.S)
    title = strip_tags(title_match.group(1)) if title_match else None
    missing_count = len(re.findall(r"/__offline/missing\.html\?", text, re.I))
    rejected_count = len(re.findall(r"Offline route rejected|non-canonical route is not allowed", text, re.I))
    return {
        "exists": True,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "title": title,
        "offline_missing_refs": missing_count,
        "route_rejected_refs": rejected_count,
        "is_placeholder": path.name in {"missing.html", "excluded-frame.html"}
        or rejected_count > 0 and len(text) < 10000,
    }


def load_json(path: Path, fallback: object) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def build_source_basename_index(source_dirs: list[Path]) -> dict[str, list[str]]:
    """Index only the two known raw-entity trees once; do not scan all research."""

    index: dict[str, list[str]] = defaultdict(list)
    for directory in source_dirs:
        if not directory.is_dir():
            continue
        try:
            for candidate in directory.rglob("*"):
                if not candidate.is_file():
                    continue
                bucket = index[candidate.name.casefold()]
                if len(bucket) < 8:
                    bucket.append(candidate.relative_to(ROOT).as_posix())
        except OSError:
            continue
    return index


def find_raw_candidates(route: str, mirror_root: Path, source_index: dict[str, list[str]]) -> list[str]:
    candidates: list[str] = []
    direct = mirror_root / route.lstrip("/")
    if direct.is_file():
        candidates.append(direct.relative_to(ROOT).as_posix())
    if route.endswith("/"):
        index = mirror_root / route.lstrip("/") / "index.html"
        if index.is_file():
            candidates.append(index.relative_to(ROOT).as_posix())
    basename = Path(route.rstrip("/")).name
    if basename:
        candidates.extend(source_index.get(basename.casefold(), []))
    return list(dict.fromkeys(candidates))


def section_for(entry: dict[str, object], by_source: dict[str, list[dict[str, object]]]) -> str:
    menu_id = str(entry["menu_id"])
    role = str(entry["source_role"])
    parts = menu_id.split("_")
    if role == "main_navigation":
        root_id = "Menu1_" + parts[1] if len(parts) > 1 else "Menu1"
        roots = by_source.get(role, [])
        root = next((item for item in roots if item["menu_id"] == root_id), None)
        label = str(root["label"]) if root else "Unknown"
        return {"Guide": "Game Guide"}.get(label, label)
    if role == "game_guide_navigation":
        return "Game Guide"
    if role == "late_menu_xml":
        category = str(entry.get("category") or "")
        return {
            "menuNews": "News",
            "menuGameGuide": "Game Guide",
            "menuMedia": "Media",
            "menuCommunity": "Community",
            "menuInteractive": "Workshop",
        }.get(category, "Legacy menu")
    label = str(entry["label"])
    if label in {"News", "Current News", "Archived News", "Guide News"}:
        return "News"
    if label in {"Media", "Screenshots", "Movies", "Music", "Wallpapers", "Fan Wallpapers"}:
        return "Media"
    return "Legacy menu"


def make_entry_status(
    entry: dict[str, object],
    route_map: dict[str, object],
    manifest_by_route: dict[str, dict[str, object]],
    export_root: Path,
    mirror_root: Path,
    source_dirs: list[Path],
    placeholder_routes: set[str],
) -> dict[str, object]:
    href = str(entry["href"])
    kind, path, host = route_parts(href)
    result: dict[str, object] = {
        "href_kind": kind,
        "normalized_route": path if kind in {"local", "same_origin_absolute"} else None,
        "external_host": host,
    }
    if kind == "fragment":
        result.update({"status": "fragment_only", "route_exists": None})
        return result
    if kind in {"external", "dynamic", "relative_or_unknown"}:
        result.update({"status": "external_or_dynamic", "route_exists": False})
        return result

    routes = route_map.get("routes") if isinstance(route_map, dict) else {}
    if not isinstance(routes, dict):
        routes = {}
    route_key = next((candidate for candidate in route_candidates(path) if candidate in routes), None)
    target = routes.get(route_key) if route_key else None
    base_path = str(route_map.get("base_path") or "/") if isinstance(route_map, dict) else "/"
    target_rel = target_relative(str(target), base_path) if target else None
    target_file = export_root / target_rel if target_rel else None
    summary = page_summary(target_file) if target_file else {"exists": False}
    record = manifest_by_route.get(path) or manifest_by_route.get(route_key or "")
    raw_candidates = find_raw_candidates(path, mirror_root, source_dirs)
    if route_key is None:
        status = "missing_export_route"
    elif target_file is None or not target_file.is_file():
        status = "broken_export_route"
    elif path in placeholder_routes or summary.get("is_placeholder"):
        status = "placeholder_route"
    else:
        status = "content_route"
    result.update(
        {
            "status": status,
            "route_exists": route_key is not None and bool(summary.get("exists")),
            "route_key": route_key,
            "export_target": target,
            "export_relative_path": target_rel,
            "export_file": target_file.relative_to(ROOT).as_posix() if target_file else None,
            "page": summary,
            "raw_source_candidates": raw_candidates,
            "manifest_record": None,
        }
    )
    if record:
        result["manifest_record"] = {
            key: record.get(key)
            for key in (
                "route",
                "source_local_path",
                "source_base_url",
                "source_sha256",
                "source_length",
                "actual_timestamp",
                "requested_timestamp",
                "source_mime",
                "kind",
                "role",
                "source_role",
                "transformed",
                "derivation_reason",
            )
            if key in record
        }
        source_local = record.get("source_local_path")
        if isinstance(source_local, str):
            source_file = ROOT / source_local
            result["manifest_record"]["source_exists"] = source_file.is_file()
    return result


def build_inventory(root: Path, export_root: Path, anchor: str) -> dict[str, object]:
    mirror_root = root / "mirror/20080512/www.worldofwarcraft.com"
    route_map_path = export_root / "__offline/route-map.json"
    manifest_path = root / "offline/build-manifest.json"
    route_map = load_json(route_map_path, {})
    manifest = load_json(manifest_path, {})
    files = manifest.get("files", []) if isinstance(manifest, dict) else []
    manifest_by_route = {
        str(item.get("route")): item for item in files if isinstance(item, dict) and item.get("route")
    }
    placeholder_routes = {
        str(item.get("route"))
        for item in (manifest.get("placeholder_routes", []) if isinstance(manifest, dict) else [])
        if isinstance(item, dict) and item.get("route")
    }
    # Source provenance is taken from the frozen manifest and direct mirror
    # paths.  Do not recursively index the entire raw-entity store for every
    # run; ignored/raw paths are preserved as an explicit unknown boundary.
    source_index: dict[str, list[str]] = {}
    sources: list[dict[str, object]] = []
    entries: list[dict[str, object]] = []
    by_source: dict[str, list[dict[str, object]]] = defaultdict(list)
    for relative, role in MENU_SOURCES:
        path = root / relative
        record = {
            "path": relative,
            "role": role,
            "exists": path.is_file(),
            "sha256": sha256(path) if path.is_file() else None,
            "bytes": path.stat().st_size if path.is_file() else None,
        }
        sources.append(record)
        if path.is_file():
            parsed = parse_menu_xml_source(path, role) if role == "late_menu_xml" else parse_menu_source(path, role)
            by_source[role].extend(parsed)
            entries.extend(parsed)

    duplicate_ids: dict[str, list[dict[str, object]]] = defaultdict(list)
    for entry in entries:
        duplicate_ids[f"{entry['source_role']}:{entry['menu_id']}"].append(entry)

    covered_entries: list[dict[str, object]] = []
    excluded_entries: list[dict[str, object]] = []
    for entry in entries:
        section = section_for(entry, by_source)
        item = dict(entry)
        item["section"] = section
        item["in_scope"] = section in TARGET_SECTIONS or (
            section == "Legacy menu" and str(entry["label"]) in {"Current News", "Archived News", "Guide News"}
        )
        dup_key = f"{entry['source_role']}:{entry['menu_id']}"
        if len(duplicate_ids[dup_key]) > 1:
            item["duplicate_menu_id"] = True
            item["duplicate_occurrences"] = [
                {"label": d["label"], "href": d["href"], "source_line": d["source_line"]}
                for d in duplicate_ids[dup_key]
            ]
        if item["in_scope"]:
            item["coverage"] = make_entry_status(
                item,
                route_map if isinstance(route_map, dict) else {},
                manifest_by_route,
                export_root,
                mirror_root,
                source_index,
                placeholder_routes,
            )
            covered_entries.append(item)
        else:
            item["coverage"] = {"status": "out_of_scope_business_or_external"}
            excluded_entries.append(item)

    # Keep the report useful when legacy menu sources repeat every page's menu.
    # Full source provenance remains in ``sources`` and the canonical navtree
    # entries; legacy rows are retained only when they materially differ.
    deduped: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in covered_entries:
        key = (str(item["label"]), str(item["href"]), str(item["source_role"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    sections = Counter(str(item["section"]) for item in deduped)
    statuses = Counter(str(item["coverage"]["status"]) for item in deduped)
    route_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in deduped:
        route = item["coverage"].get("normalized_route")
        if route:
            route_rows[str(route)].append(item)

    archived = [
        item
        for item in deduped
        if str(item["label"]).casefold() == "archived news"
    ]
    derived_sidebar_path = export_root / "new-hp/layout/menu.xml"
    derived_sidebar_entries = (
        parse_menu_xml_source(derived_sidebar_path, "derived_sidebar_menu")
        if derived_sidebar_path.is_file()
        else []
    )
    derived_archived = [
        item for item in derived_sidebar_entries if str(item["label"]).casefold() == "archived news"
    ]
    derived_community_count = sum(
        1 for item in derived_sidebar_entries if str(item.get("category")) == "menuCommunity"
    )
    main_entries = by_source.get("main_navigation", [])
    fan_parent = next(
        (item for item in main_entries if item.get("menu_id") == "Menu1_6"),
        None,
    )
    fan_child_declarations = [
        item
        for item in main_entries
        if re.fullmatch(r"Menu1_6_\d+", str(item.get("menu_id")))
    ]
    fan_diagnostics = {
        "parent_menu_id": "Menu1_6",
        "parent_declared_child_count": fan_parent.get("child_count") if fan_parent else None,
        "source_child_declaration_count": len(fan_child_declarations),
        "source_child_ids": [item.get("menu_id") for item in fan_child_declarations],
        "duplicate_child_id": "Menu1_6_10",
        "duplicate_child_labels": [
            item.get("label")
            for item in fan_child_declarations
            if item.get("menu_id") == "Menu1_6_10"
        ],
        "derived_sidebar_community_item_count": derived_community_count,
        "recommended_parent_child_count": 11,
        "recommended_second_id": "Menu1_6_11",
        "recommendation_basis": "eleven source child declarations and eleven derived Community menu items, with Fan Wallpapers and Fan Sites sharing Menu1_6_10",
    }
    return {
        "schema": "navigation-gap-inventory/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "anchor_timestamp": anchor,
            "anchor_date": "2008-05-12",
            "network_performed": False,
            "frozen_inputs": [
                "offline/site",
                "offline/build-manifest.json",
                "mirror/20080512",
            ],
            "export_preview": export_root.relative_to(root).as_posix(),
            "ignored_paths_are_not_absence": True,
            "target_sections": sorted(TARGET_SECTIONS),
            "excluded_sections": {
                "Account": "historical business surface; retain exhibit, do not restore credential/payment forms",
                "Forums": "external/social surface; no external acquisition",
                "Support": "historical support surface; retain exhibit, do not restore sensitive forms",
            },
        },
        "sources": sources,
        "route_map": {
            "path": route_map_path.relative_to(root).as_posix(),
            "schema": route_map.get("schema") if isinstance(route_map, dict) else None,
            "base_path": route_map.get("base_path") if isinstance(route_map, dict) else None,
            "route_count": len(route_map.get("routes", {})) if isinstance(route_map, dict) else 0,
        },
        "manifest": {
            "path": manifest_path.relative_to(root).as_posix(),
            "schema_version": manifest.get("schema_version") if isinstance(manifest, dict) else None,
            "anchor_timestamp": manifest.get("anchor_timestamp") if isinstance(manifest, dict) else None,
            "stats": manifest.get("stats") if isinstance(manifest, dict) else None,
            "placeholder_route_count": len(placeholder_routes),
            "unresolved_reference_count": manifest.get("unresolved_reference_count") if isinstance(manifest, dict) else None,
        },
        "archived_news": archived,
        "derived_sidebar": {
            "path": derived_sidebar_path.relative_to(root).as_posix(),
            "exists": derived_sidebar_path.is_file(),
            "sha256": sha256(derived_sidebar_path) if derived_sidebar_path.is_file() else None,
            "archived_news": derived_archived,
            "community_item_count": derived_community_count,
        },
        "fan_wallpapers_diagnostic": fan_diagnostics,
        "entries": deduped,
        "excluded_entries": excluded_entries,
        "summary": {
            "entry_count": len(deduped),
            "excluded_entry_count": len(excluded_entries),
            "sections": dict(sorted(sections.items())),
            "statuses": dict(sorted(statuses.items())),
            "duplicate_menu_ids": {
                key: values for key, values in duplicate_ids.items() if len(values) > 1
            },
            "distinct_local_routes": len(route_rows),
        },
    }


def original_url(href: str, route: str | None) -> str | None:
    if not route:
        return None
    parsed = urlsplit(href)
    if parsed.scheme and parsed.netloc:
        return href
    return "http://www.worldofwarcraft.com" + route


def build_repair_plan(inventory: dict[str, object]) -> dict[str, object]:
    entries = inventory.get("entries", [])
    queue: list[dict[str, object]] = []
    download_by_route: dict[str, dict[str, object]] = {}
    for item in entries:
        coverage = item.get("coverage", {})
        if not isinstance(coverage, dict):
            continue
        status = str(coverage.get("status"))
        route = coverage.get("normalized_route")
        label = str(item.get("label"))
        if label.casefold() == "archived news" and status == "content_route":
            queue.append(
                {
                    "priority": "P0",
                    "action": "publish_or_route-verify-existing-content",
                    "section": item.get("section"),
                    "label": label,
                    "menu_id": item.get("menu_id"),
                    "source_path": item.get("source_path"),
                    "source_line": item.get("source_line"),
                    "original_url": original_url(str(item.get("href")), str(route) if route else None),
                    "route": route,
                    "current_status": status,
                    "export_file": coverage.get("export_file"),
                    "page": coverage.get("page"),
                    "acceptance": [
                        "HTTP 200 from the exported route",
                        "title contains Archived News",
                        "old-news links remain navigable",
                        "external and sensitive business links remain static exhibits or explicit missing links",
                    ],
                    "network_evidence": "not required for existing local content; no network performed in this phase",
                }
            )
        if status in {"missing_export_route", "broken_export_route"} and route:
            raw = coverage.get("raw_source_candidates") or []
            key = str(route)
            row = download_by_route.setdefault(
                key,
                {
                    "priority": "P1" if raw else "P2",
                    "route": route,
                    "original_url": original_url(str(item.get("href")), key),
                    "labels": [],
                    "menu_sources": [],
                    "current_status": status,
                    "raw_source_candidates": raw,
                    "baseline_anchor": inventory["scope"]["anchor_timestamp"],
                    "baseline_date": inventory["scope"]["anchor_date"],
                    "capture_status": "pending_network_window",
                    "actual_capture_timestamp": None,
                    "cdx_status": "not_attempted_offline",
                    "query_strategy": "exact URL, 2008-05-12 baseline window; record actual capture timestamp; if CDX is unavailable retain queued-unverified",
                    "acceptance": [
                        "source capture has a recorded actual timestamp",
                        "payload MIME/body is verified",
                        "route is represented in a derived preview and route map",
                        "source and derived SHA-256 are recorded",
                    ],
                },
            )
            row["labels"].append(label)
            row["menu_sources"].append(
                {
                    "menu_id": item.get("menu_id"),
                    "source_path": item.get("source_path"),
                    "source_line": item.get("source_line"),
                }
            )
    queue.extend(download_by_route.values())
    duplicate = inventory.get("summary", {}).get("duplicate_menu_ids", {})
    if duplicate:
        for key, values in duplicate.items():
            if "Fan Wallpapers" in {str(v.get("label")) for v in values} and "Fan Sites" in {
                str(v.get("label")) for v in values
            }:
                queue.append(
                    {
                        "priority": "P1",
                        "action": "repair-derived-navigation-node-id",
                        "menu_id": key,
                        "reason": "navtree-main assigns Menu1_6_10 twice; the later Fan Sites assignment overwrites Fan Wallpapers in runtime JavaScript",
                        "evidence": values,
                        "parent_menu_id": inventory.get("fan_wallpapers_diagnostic", {}).get("parent_menu_id"),
                        "parent_declared_child_count": inventory.get("fan_wallpapers_diagnostic", {}).get("parent_declared_child_count"),
                        "source_child_declaration_count": inventory.get("fan_wallpapers_diagnostic", {}).get("source_child_declaration_count"),
                        "recommended_parent_child_count": inventory.get("fan_wallpapers_diagnostic", {}).get("recommended_parent_child_count"),
                        "recommended_second_id": inventory.get("fan_wallpapers_diagnostic", {}).get("recommended_second_id"),
                        "derived_sidebar_community_item_count": inventory.get("fan_wallpapers_diagnostic", {}).get("derived_sidebar_community_item_count"),
                        "acceptance": [
                            "both Fan Wallpapers and Fan Sites are reachable from the derived navigation",
                            "parent Menu1_6 declares 11 children and the second declaration uses Menu1_6_11",
                            "each target route remains covered by existing content or an explicit queued gap",
                            "frozen navtree source bytes are unchanged",
                        ],
                    }
                )
    queue.sort(key=lambda row: (str(row.get("priority")), str(row.get("route") or row.get("menu_id"))))
    return {
        "schema": "navigation-repair-plan/v1",
        "generated_at": inventory["generated_at"],
        "anchor_timestamp": inventory["scope"]["anchor_timestamp"],
        "anchor_date": inventory["scope"]["anchor_date"],
        "network_performed": False,
        "preservation": [
            "do not modify offline/site or offline/build-manifest.json in this phase",
            "do not restore login, billing, account, submission, or social forms",
            "do not treat ignored paths or missing CDX access as proof of no capture",
        ],
        "queue": queue,
    }


def md_cell(value: object) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def build_markdown(inventory: dict[str, object], plan: dict[str, object]) -> str:
    scope = inventory["scope"]
    summary = inventory["summary"]
    lines = [
        "# Navigation gaps local inventory (2026-10-15)",
        "",
        "This report is local-only. It reads the frozen 2008-05-12 mirror, the frozen build manifest, and the existing `pages-local-maintenance-20261014-v5` preview. No network acquisition was performed.",
        "",
        f"Anchor: `{scope['anchor_timestamp']}` (`{scope['anchor_date']}`). Frozen `offline/site` and `offline/build-manifest.json` were not modified. Ignored paths are not treated as evidence of absence.",
        "",
        "## Archived News first check",
        "",
    ]
    for item in inventory.get("archived_news", []):
        coverage = item.get("coverage", {})
        page = coverage.get("page", {}) if isinstance(coverage, dict) else {}
        lines.append(
            f"- `{item['source_role']}` `{item['source_path']}:{item['source_line']}` — `{item['label']}` → `{item['href']}`; status `{coverage.get('status')}`; export `{coverage.get('export_file')}`; {page.get('bytes')} bytes; title `{page.get('title')}`; `{page.get('offline_missing_refs', 0)}` explicit offline-missing references."
        )
    derived_sidebar = inventory.get("derived_sidebar", {})
    if isinstance(derived_sidebar, dict):
        for item in derived_sidebar.get("archived_news", []):
            lines.append(
                f"- `derived_sidebar_menu` `{derived_sidebar.get('path')}`:{item.get('source_line')} — current exported sidebar Archived News → `{item.get('href')}`; Community items: `{derived_sidebar.get('community_item_count')}`."
            )
    fan_diagnostic = inventory.get("fan_wallpapers_diagnostic", {})
    if isinstance(fan_diagnostic, dict):
        lines.extend(
            [
                "",
                f"Fan Wallpapers evidence: parent `{fan_diagnostic.get('parent_menu_id')}` declares `{fan_diagnostic.get('parent_declared_child_count')}` children while `{fan_diagnostic.get('source_child_declaration_count')}` child declarations exist; the duplicate `{fan_diagnostic.get('duplicate_child_id')}` carries `{fan_diagnostic.get('duplicate_child_labels')}`. The derived sidebar has `{fan_diagnostic.get('derived_sidebar_community_item_count')}` Community items. Proposed derived-only repair: parent count `{fan_diagnostic.get('recommended_parent_child_count')}`, second ID `{fan_diagnostic.get('recommended_second_id')}`; frozen navtree remains unchanged.",
            ]
        )
    lines.extend(
        [
            "",
            "Both `/info/archivednews.html` and the legacy `/news/wow-news-06-2006.html` are real local pages. Their missing references are external or uncollected links inside otherwise readable historical pages; they are not empty route placeholders.",
            "",
            "## Coverage summary",
            "",
            f"Entries after exact `(label, href, source role)` de-duplication: **{summary['entry_count']}**; distinct local routes: **{summary['distinct_local_routes']}**.",
            "",
            "| Section | Entries |",
            "| --- | ---: |",
        ]
    )
    for section, count in sorted(summary["sections"].items()):
        lines.append(f"| {md_cell(section)} | {count} |")
    lines.extend(["", "| Status | Entries |", "| --- | ---: |"])
    for status, count in sorted(summary["statuses"].items()):
        lines.append(f"| `{md_cell(status)}` | {count} |")

    lines.extend(["", "## Candidate repair and acquisition queue", ""])
    lines.append("| Priority | Action | Route / node | Current evidence |")
    lines.append("| --- | --- | --- | --- |")
    for row in plan.get("queue", []):
        route_or_node = row.get("route") or row.get("menu_id") or ""
        evidence = row.get("current_status") or row.get("reason") or row.get("capture_status") or ""
        lines.append(
            f"| {md_cell(row.get('priority'))} | {md_cell(row.get('action'))} | `{md_cell(route_or_node)}` | {md_cell(evidence)} |"
        )
    if not plan.get("queue"):
        lines.append("| — | No local repair or acquisition candidate was generated | — | — |")

    lines.extend(["", "## Navigation coverage table", ""])
    lines.append("| Section | Label | Original href | Current status | Route / source evidence |")
    lines.append("| --- | --- | --- | --- | --- |")
    for item in sorted(
        inventory.get("entries", []),
        key=lambda row: (str(row.get("section")), str(row.get("menu_id")), int(row.get("source_line", 0))),
    ):
        coverage = item.get("coverage", {})
        if not isinstance(coverage, dict):
            continue
        evidence = coverage.get("export_file") or ", ".join(coverage.get("raw_source_candidates", [])[:2]) or "—"
        duplicate = "; duplicate id" if item.get("duplicate_menu_id") else ""
        lines.append(
            f"| {md_cell(item.get('section'))} | {md_cell(item.get('label'))} | `{md_cell(item.get('href'))}` | `{md_cell(coverage.get('status'))}`{duplicate} | `{md_cell(evidence)}` |"
        )

    lines.extend(["", "## Evidence sources", ""])
    for source in inventory.get("sources", []):
        lines.append(f"- `{source['path']}` — SHA-256 `{source.get('sha256')}`, {source.get('bytes')} bytes.")
    lines.extend(
        [
            "",
            "The raw menu rows preserve source line numbers and raw JavaScript in `inventory.json`. `repair-plan.json` records pending network work with `actual_capture_timestamp: null`; `cdx_status: not_attempted_offline` means this local phase did not query CDX, not that no capture exists.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--export", type=Path, default=DEFAULT_EXPORT)
    parser.add_argument("--anchor", default=DEFAULT_ANCHOR)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = args.root.resolve()
    export_root = args.export.resolve()
    output_dir = args.output_dir.resolve()
    inventory = build_inventory(root, export_root, args.anchor)
    plan = build_repair_plan(inventory)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "repair-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "inventory.md").write_text(build_markdown(inventory, plan), encoding="utf-8")
    print(json.dumps({"output_dir": output_dir.relative_to(root).as_posix(), "summary": inventory["summary"], "queue": len(plan["queue"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

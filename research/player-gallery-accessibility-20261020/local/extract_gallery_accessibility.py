#!/usr/bin/env python3
"""Build a bounded offline availability audit for the canonical 50 galleries.

This script deliberately reads only the frozen registry, the selected v39 and
source15 page/sidebar/runtime/provenance inputs, and the exact JPEG targets
declared by each gallery.  It does not crawl a directory, use the network, or
modify a site/export.  Guide preview images are retained as a separate layer
and never count as native gallery targets.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit

try:
    from PIL import Image
except Exception:  # pragma: no cover - the execution environment has Pillow
    Image = None  # type: ignore[assignment]


REPO = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = REPO / "research/continuous-recovery-20261016/local-audit/gallery-final-v7/gallery-prefix-registry-v7.json"
V39_ROOT = REPO / ".scratch/pages-resources-20261020-v39"
SOURCE15_ROOT = REPO / ".scratch/offline-navigation-20261015-v15/site"
ORIGINAL_ROOT = REPO / "offline/site"
V39_PROVENANCE_PATH = V39_ROOT / "export-provenance.json"
V39_ROUTE_MAP_PATH = V39_ROOT / "__offline/route-map.json"
V39_SIDEBAR_PATH = V39_ROOT / "info/index.html"
RUNTIME_PATH = ORIGINAL_ROOT / "new-hp/js/guidegallery-screenie.js"
DEPLOY_BASE = "/WOW-Encyclopedia-Deployable-Archive"
EXPECTED_V39_PROVENANCE_SHA256 = "02b1cd43766288f96c879ef464d7198bb09d1085008ae3e500773d594f6c7760"
EXPECTED_REGISTRY_SHA256 = "2579f66841bf6102d90f5dbfe819902337bff03f6e3ac7191239ae041e2d97d6"
EXPECTED_RUNTIME_SHA256 = "b0e619c361c315b60eca6d05c92f38efc3eed1f773bfbdb971af6c2deb3e0a4c"

PAGE_NUM_RE = re.compile(r"\bnumShots\s*=\s*(\d+)\s*;", re.IGNORECASE)
PAGE_ADDSHOTS_RE = re.compile(
    r"addshots\s*\(\s*(['\"])(.*?)\1\s*,\s*(['\"])(.*?)\3\s*,\s*numShots\s*\)",
    re.IGNORECASE | re.DOTALL,
)
REVERSE_RE = re.compile(r"\breverseOrder\s*=\s*(true|false)\s*;", re.IGNORECASE)
SCRIPT_SRC_RE = re.compile(r"/new-hp/js/guidegallery-screenie\.js(?:[?#][^\"']*)?$", re.IGNORECASE)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes(path: Path) -> tuple[bytes, dict[str, Any]]:
    data = path.read_bytes()
    return data, {"path": rel(path), "bytes": len(data), "sha256": sha256_bytes(data)}


def read_json(path: Path) -> tuple[Any, dict[str, Any]]:
    data, meta = read_bytes(path)
    return json.loads(data.decode("utf-8")), meta


def line_number(text: str, position: int | None) -> int | None:
    if position is None:
        return None
    return text.count("\n", 0, position) + 1


def without_comments(text: str) -> str:
    # HTML comments can carry old placeholders or examples.  Ignore them for
    # declarations, just as the browser ignores their markup.  Preserve line
    # breaks so declaration offsets still point at the original source lines.
    def blank(match: re.Match[str]) -> str:
        return "".join("\n" if char == "\n" else " " for char in match.group(0))

    text = re.sub(r"<!--.*?-->", blank, text, flags=re.DOTALL)
    return re.sub(r"/\*.*?\*/", blank, text, flags=re.DOTALL)


def strip_deploy_base(value: str) -> str:
    value = unquote(urlsplit(value).path or value)
    if value.startswith(DEPLOY_BASE):
        value = value[len(DEPLOY_BASE) :]
    if not value.startswith("/"):
        value = "/" + value
    return value or "/"


def normalize_route(value: str, page_route: str | None = None) -> str:
    value = (value or "").strip()
    if page_route and not value.startswith(("/", "http://", "https://", "//")):
        value = urljoin(page_route, value)
    return strip_deploy_base(value.split("#", 1)[0].split("?", 1)[0])


class GalleryHTMLParser(HTMLParser):
    """Small parser that excludes comments and separates preview sections."""

    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.static_images: list[dict[str, Any]] = []
        self.script_srcs: list[dict[str, Any]] = []
        self.wrappers: list[dict[str, Any]] = []
        self.preview_sections: list[dict[str, Any]] = []
        self._active_sections: list[dict[str, Any]] = []
        self._depth = 0

    @staticmethod
    def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {str(k).lower(): (v or "") for k, v in attrs}

    def _start(self, tag: str, attrs: list[tuple[str, str | None]], self_closing: bool = False) -> None:
        tag = tag.lower()
        ad = self.attrs_dict(attrs)
        line, col = self.getpos()
        if tag == "img" and "src" in ad:
            item = {"src": ad["src"], "line": line, "column": col}
            self.static_images.append(item)
            for section in self._active_sections:
                section["img_srcs"].append(ad["src"])
                section["img_lines"].append(line)
        if tag == "script" and "src" in ad:
            self.script_srcs.append({"src": ad["src"], "line": line, "column": col})
        if tag in {"div", "section", "main"} and ad.get("id") == "galleryPictures":
            self.wrappers.append(
                {"tag": tag, "id": ad.get("id"), "class": ad.get("class", ""), "line": line, "column": col}
            )
        if tag == "section":
            classes = set(ad.get("class", "").split())
            section_id = ad.get("id", "")
            if "offline-guide-preview-section" in classes or section_id.startswith("offline-preserved-guide-previews-"):
                raw_count = ad.get("data-guide-preview-count")
                try:
                    declared_count: int | None = int(raw_count) if raw_count else None
                except ValueError:
                    declared_count = None
                section = {
                    "id": section_id or None,
                    "group": ad.get("data-guide-preview-group") or None,
                    "declared_count": declared_count,
                    "img_srcs": [],
                    "img_lines": [],
                    "line": line,
                    "class": ad.get("class", ""),
                }
                self.preview_sections.append(section)
                self._active_sections.append(section)
        if not self_closing and tag not in self.VOID_TAGS:
            self._depth += 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, False)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, True)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "section" and self._active_sections:
            self._active_sections.pop()
        if tag not in self.VOID_TAGS:
            self._depth = max(0, self._depth - 1)


class SidebarParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.links: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        ad = {str(k).lower(): (v or "") for k, v in attrs}
        if "href" in ad:
            line, col = self.getpos()
            self.links.append({"href": ad["href"], "line": line, "column": col})


def parse_page(path: Path, page_route: str) -> dict[str, Any]:
    raw, meta = read_bytes(path)
    text = raw.decode("utf-8", errors="replace")
    semantic = without_comments(text)
    num_matches = list(PAGE_NUM_RE.finditer(semantic))
    add_matches = list(PAGE_ADDSHOTS_RE.finditer(semantic))
    reverse_matches = list(REVERSE_RE.finditer(semantic))
    parser = GalleryHTMLParser()
    parser.feed(text)
    num_match = num_matches[-1] if num_matches else None
    add_match = add_matches[-1] if add_matches else None
    reverse_match = reverse_matches[-1] if reverse_matches else None
    wrappers = parser.wrappers
    raw_directory = add_match.group(2) if add_match else None
    filename = add_match.group(4) if add_match else None
    normalized_directory = strip_deploy_base(raw_directory) if raw_directory is not None else None
    raw_script_srcs = [x["src"] for x in parser.script_srcs]
    runtime_scripts = [x for x in parser.script_srcs if SCRIPT_SRC_RE.search(urlsplit(x["src"]).path)]
    preview_sections: list[dict[str, Any]] = []
    for section in parser.preview_sections:
        preview_sections.append(
            {
                "id": section["id"],
                "group": section["group"],
                "declared_count": section["declared_count"],
                "actual_img_count": len(section["img_srcs"]),
                "img_routes": [normalize_route(src, page_route) for src in section["img_srcs"]],
                "img_lines": section["img_lines"],
                "line": section["line"],
                "class": section["class"],
            }
        )
    return {
        "path": rel(path),
        "sha256": meta["sha256"],
        "bytes": meta["bytes"],
        "text": text,
        "num_shots": int(num_match.group(1)) if num_match else None,
        "num_shots_line": line_number(text, num_match.start()) if num_match else None,
        "num_shots_match_count": len(num_matches),
        "addshots_raw_directory": raw_directory,
        "addshots_directory": normalized_directory,
        "addshots_filename": filename,
        "addshots_line": line_number(text, add_match.start()) if add_match else None,
        "addshots_match_count": len(add_matches),
        "reverse_order": (reverse_match.group(1).lower() == "true") if reverse_match else None,
        "reverse_order_line": line_number(text, reverse_match.start()) if reverse_match else None,
        "script_srcs": raw_script_srcs,
        "runtime_script_srcs": [x["src"] for x in runtime_scripts],
        "runtime_script_lines": [x["line"] for x in runtime_scripts],
        "wrappers": wrappers,
        "preview_sections": preview_sections,
        "static_img_srcs": [x["src"] for x in parser.static_images],
        "static_img_routes": [normalize_route(x["src"], page_route) for x in parser.static_images],
        "static_img_lines": [x["line"] for x in parser.static_images],
    }


def parse_sidebar(path: Path) -> dict[str, Any]:
    raw, meta = read_bytes(path)
    text = raw.decode("utf-8", errors="replace")
    parser = SidebarParser()
    parser.feed(text)
    links: list[dict[str, Any]] = []
    for link in parser.links:
        route = normalize_route(urljoin("/info/index.html", link["href"]))
        if route.endswith("gallery.html"):
            links.append({"href": link["href"], "route": route, "line": link["line"], "column": link["column"]})
    return {"path": rel(path), "sha256": meta["sha256"], "bytes": meta["bytes"], "gallery_links": links}


def inspect_file(path: Path, cache: dict[str, dict[str, Any]], read_stats: dict[str, int]) -> dict[str, Any]:
    key = str(path.resolve())
    if key in cache:
        return dict(cache[key])
    result: dict[str, Any] = {"path": rel(path), "exists": False}
    if not path.is_file():
        cache[key] = result
        return dict(result)
    data = path.read_bytes()
    read_stats["bytes"] += len(data)
    result.update({"exists": True, "bytes": len(data), "sha256": sha256_bytes(data)})
    result["valid_jpeg"] = False
    result["jpeg_format"] = None
    result["width"] = None
    result["height"] = None
    result["mode"] = None
    result["decode_error"] = None
    if Image is None:
        result["decode_error"] = "Pillow unavailable"
    else:
        try:
            with Image.open(path) as im:
                result["jpeg_format"] = im.format
                result["width"], result["height"] = im.size
                result["mode"] = im.mode
                im.verify()
            with Image.open(path) as im:
                im.load()
                result["valid_jpeg"] = im.format == "JPEG"
        except Exception as exc:  # malformed/non-JPEG exact target
            result["decode_error"] = f"{type(exc).__name__}: {exc}"
    cache[key] = result
    return dict(result)


def provenance_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "available": bool(entries),
        "entry_count": len(entries),
        "roles": sorted({str(x.get("role")) for x in entries if x.get("role")}),
        "kinds": sorted({str(x.get("kind")) for x in entries if x.get("kind")}),
        "derived_lengths": sorted({int(x["derived_length"]) for x in entries if x.get("derived_length") is not None}),
        "source_lengths": sorted({int(x["source_length"]) for x in entries if x.get("source_length") is not None}),
        "derived_sha256s": sorted({str(x["derived_sha256"]) for x in entries if x.get("derived_sha256")}),
        "source_sha256s": sorted({str(x["source_sha256"]) for x in entries if x.get("source_sha256")}),
        "source_offline_paths": sorted({str(x["source_offline_path"]) for x in entries if x.get("source_offline_path")}),
        "source_paths": sorted({str(x["source_path"]) for x in entries if x.get("source_path")}),
        "transformed_values": sorted({bool(x.get("transformed")) for x in entries}),
    }


def expected_routes(source_directory: str, filename: str, slot: int) -> tuple[str, str]:
    full = f"{source_directory}{filename}{slot}.jpg"
    thumb = f"{source_directory}{filename}{slot}-thumb.jpg"
    return full, thumb


def dump_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    registry, registry_meta = read_json(REGISTRY_PATH)
    provenance, provenance_meta = read_json(V39_PROVENANCE_PATH)
    route_map, route_map_meta = read_json(V39_ROUTE_MAP_PATH)
    runtime_bytes, runtime_meta = read_bytes(RUNTIME_PATH)
    runtime_text = runtime_bytes.decode("utf-8", errors="replace")
    v39_sidebar = parse_sidebar(V39_SIDEBAR_PATH)

    actual_registry_sha = registry_meta["sha256"].lower()
    actual_provenance_sha = provenance_meta["sha256"].lower()
    actual_runtime_sha = runtime_meta["sha256"].lower()
    if actual_registry_sha != EXPECTED_REGISTRY_SHA256:
        raise RuntimeError(f"registry hash conflict: {actual_registry_sha} != {EXPECTED_REGISTRY_SHA256}")
    if actual_provenance_sha != EXPECTED_V39_PROVENANCE_SHA256:
        raise RuntimeError(f"v39 provenance hash conflict: {actual_provenance_sha} != {EXPECTED_V39_PROVENANCE_SHA256}")
    if actual_runtime_sha != EXPECTED_RUNTIME_SHA256:
        raise RuntimeError(f"runtime hash conflict: {actual_runtime_sha} != {EXPECTED_RUNTIME_SHA256}")

    coverage_rows = registry.get("coverage_rows")
    if not isinstance(coverage_rows, list) or len(coverage_rows) != 50:
        raise RuntimeError(f"expected 50 registry rows, got {len(coverage_rows) if isinstance(coverage_rows, list) else type(coverage_rows).__name__}")
    if int(registry.get("stats", {}).get("declared_slots", -1)) != 1684:
        raise RuntimeError("registry declared_slots is not the frozen 1684")
    if int(registry.get("stats", {}).get("expected_direct_entities", -1)) != 3368:
        raise RuntimeError("registry expected_direct_entities is not the frozen 3368")

    # The selected runtime lines are the only URL-generation contract used by
    # this audit.  These checks keep a future parser change from silently
    # turning previews or unrelated images into native targets.
    if "shotList[i] = sourceDirectory + filename + (i+1) +\".jpg\"" not in runtime_text:
        raise RuntimeError("runtime addshots forward-order semantics changed")
    if 'thumbnail = shotList[n].replace(".jpg","-thumb.jpg")' not in runtime_text:
        raise RuntimeError("runtime thumbnail semantics changed")
    provenance_files = provenance.get("files", [])
    provenance_by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in provenance_files:
        route = entry.get("route")
        if isinstance(route, str):
            provenance_by_route[strip_deploy_base(route)].append(entry)
    route_map_routes = route_map.get("routes", {}) if isinstance(route_map, dict) else {}
    if not isinstance(route_map_routes, dict):
        raise RuntimeError("route-map routes is not an object")

    inspect_cache: dict[str, dict[str, Any]] = {}
    read_stats = {"bytes": 0}
    rows: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []
    validation_errors: list[str] = []
    sidebar_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for link in v39_sidebar["gallery_links"]:
        sidebar_map[link["route"]].append(link)

    for registry_row in coverage_rows:
        rank = int(registry_row["registry_rank"])
        gallery = str(registry_row["gallery"])
        page_route = str(registry_row["source_page_route"])
        declared_slots = int(registry_row["declared_slots"])
        source_evidence = registry_row["source_evidence"]
        source_directory = str(source_evidence["source_directory"])
        filename = str(source_evidence["filename_literal"])
        source_page_path = REPO / str(source_evidence["path"])
        current_page_path = V39_ROOT / page_route.lstrip("/")
        original_page_path = ORIGINAL_ROOT / page_route.lstrip("/")
        current_page = parse_page(current_page_path, page_route)
        source15_page = parse_page(source_page_path, page_route)
        original_page = parse_page(original_page_path, page_route) if original_page_path.is_file() else None

        page_errors: list[str] = []
        if source15_page["sha256"].lower() != str(source_evidence["sha256"]).lower():
            page_errors.append("source15 registry page sha256 mismatch")
        for label, parsed in (("current_v39", current_page), ("source15", source15_page)):
            if parsed["num_shots"] != declared_slots:
                page_errors.append(f"{label} numShots {parsed['num_shots']} != registry {declared_slots}")
            if parsed["addshots_directory"] != source_directory:
                page_errors.append(f"{label} source directory {parsed['addshots_directory']} != registry {source_directory}")
            if parsed["addshots_filename"] != filename:
                page_errors.append(f"{label} filename {parsed['addshots_filename']} != registry {filename}")
            if parsed["addshots_match_count"] != 1:
                page_errors.append(f"{label} addshots match count {parsed['addshots_match_count']}")
            if parsed["num_shots_match_count"] != 1:
                page_errors.append(f"{label} numShots match count {parsed['num_shots_match_count']}")
        if not current_page["runtime_script_srcs"]:
            page_errors.append("current v39 runtime script declaration missing")
        if len(current_page["wrappers"]) != 1:
            page_errors.append(f"current v39 gallery wrapper count {len(current_page['wrappers'])}")
        if page_errors:
            validation_errors.extend(f"rank {rank} {gallery}: {x}" for x in page_errors)

        full_set: set[str] = set()
        thumb_set: set[str] = set()
        for slot in range(1, declared_slots + 1):
            full, thumb = expected_routes(source_directory, filename, slot)
            full_set.add(full)
            thumb_set.add(thumb)
        static_routes = current_page["static_img_routes"]
        static_native_full = sorted(set(static_routes).intersection(full_set))
        static_native_thumb = sorted(set(static_routes).intersection(thumb_set))
        current_preview_sections = current_page["preview_sections"]
        addshots_has_deploy_base = bool(
            current_page["addshots_raw_directory"]
            and str(current_page["addshots_raw_directory"]).startswith(DEPLOY_BASE + "/")
        )
        addshots_placeholder = bool(
            current_page["addshots_raw_directory"]
            and re.search(r"(?:__offline/missing|missing\.html|placeholder)", str(current_page["addshots_raw_directory"]), re.IGNORECASE)
        )
        if addshots_placeholder:
            rewrite_status = "placeholder_detected"
        elif addshots_has_deploy_base:
            rewrite_status = "repaired_current_deploy_base"
        else:
            rewrite_status = "missing_current_deploy_base"

        page_row: dict[str, Any] = {
            "registry_rank": rank,
            "gallery": gallery,
            "category": registry_row["category"],
            "source_page_route": page_route,
            "declared_slots": declared_slots,
            "expected_direct_entities": declared_slots * 2,
            "source_directory": source_directory,
            "filename_literal": filename,
            "expected_url_rule": {
                "full": f"{source_directory}{filename}<slot>.jpg",
                "thumb": f"{source_directory}{filename}<slot>-thumb.jpg",
                "runtime_basis": "addshots() creates the full URL; printPages() replaces .jpg with -thumb.jpg in the same directory",
            },
            "current_v39": {
                "path": current_page["path"],
                "sha256": current_page["sha256"],
                "bytes": current_page["bytes"],
                "num_shots": current_page["num_shots"],
                "num_shots_line": current_page["num_shots_line"],
                "addshots_raw_directory": current_page["addshots_raw_directory"],
                "addshots_directory": current_page["addshots_directory"],
                "addshots_filename": current_page["addshots_filename"],
                "addshots_line": current_page["addshots_line"],
                "runtime_script_srcs": current_page["runtime_script_srcs"],
                "runtime_script_lines": current_page["runtime_script_lines"],
                "runtime_script_matches": bool(current_page["runtime_script_srcs"]),
                "reverse_order": current_page["reverse_order"],
                "wrapper": current_page["wrappers"][0] if current_page["wrappers"] else None,
                "static_img_count": len(current_page["static_img_routes"]),
                "static_native_full_count": len(static_native_full),
                "static_native_thumb_count": len(static_native_thumb),
                "dom_only_slider": bool(current_page["addshots_match_count"] == 1 and not static_native_full and not static_native_thumb),
                "addshots_rewrite_status": rewrite_status,
                "addshots_placeholder_detected": addshots_placeholder,
                "guide_preview_sections": current_preview_sections,
                "source_declaration_matches_registry": not any(
                    x in page_errors
                    for x in (
                        f"current_v39 source directory {current_page['addshots_directory']} != registry {source_directory}",
                        f"current_v39 filename {current_page['addshots_filename']} != registry {filename}",
                    )
                ),
            },
            "source15": {
                "path": source15_page["path"],
                "sha256": source15_page["sha256"],
                "bytes": source15_page["bytes"],
                "num_shots": source15_page["num_shots"],
                "num_shots_line": source15_page["num_shots_line"],
                "addshots_raw_directory": source15_page["addshots_raw_directory"],
                "addshots_directory": source15_page["addshots_directory"],
                "addshots_filename": source15_page["addshots_filename"],
                "addshots_line": source15_page["addshots_line"],
                "wrapper": source15_page["wrappers"][0] if source15_page["wrappers"] else None,
            },
            "original_offline": {
                "path": original_page["path"] if original_page else rel(original_page_path),
                "sha256": original_page["sha256"] if original_page else None,
                "bytes": original_page["bytes"] if original_page else None,
                "num_shots": original_page["num_shots"] if original_page else None,
                "addshots_directory": original_page["addshots_directory"] if original_page else None,
                "addshots_filename": original_page["addshots_filename"] if original_page else None,
                "wrapper": original_page["wrappers"][0] if original_page and original_page["wrappers"] else None,
            },
            "sidebar": {
                "current_route_present": page_route in sidebar_map,
                "links": sidebar_map.get(page_route, []),
            },
            "validation_errors": page_errors,
        }

        counts = Counter()
        for slot in range(1, declared_slots + 1):
            full_route, thumb_route = expected_routes(source_directory, filename, slot)
            for target_kind, route in (("full", full_route), ("thumb", thumb_route)):
                deploy_url = DEPLOY_BASE + route
                v39_path = V39_ROOT / route.lstrip("/")
                source15_path = SOURCE15_ROOT / route.lstrip("/")
                original_path = ORIGINAL_ROOT / route.lstrip("/")
                v39_file = inspect_file(v39_path, inspect_cache, read_stats)
                source15_file = inspect_file(source15_path, inspect_cache, read_stats)
                original_file = inspect_file(original_path, inspect_cache, read_stats)
                prov_entries = provenance_by_route.get(route, [])
                prov = provenance_summary(prov_entries)
                map_value = route_map_routes.get(route)
                route_available = isinstance(map_value, str)
                route_value_matches = map_value == deploy_url if route_available else False
                source15_missing = bool(source15_file.get("exists")) and not bool(v39_file.get("exists"))
                original_missing = bool(original_file.get("exists")) and not bool(v39_file.get("exists"))
                provenance_missing = bool(prov["available"]) and not bool(v39_file.get("exists"))
                counts[f"v39_{target_kind}_exists"] += int(v39_file.get("exists", False))
                counts[f"v39_{target_kind}_valid"] += int(v39_file.get("valid_jpeg", False))
                counts[f"source15_{target_kind}_exists"] += int(source15_file.get("exists", False))
                counts[f"original_{target_kind}_exists"] += int(original_file.get("exists", False))
                counts[f"source15_{target_kind}_missing"] += int(source15_missing)
                counts[f"original_{target_kind}_missing"] += int(original_missing)
                counts[f"provenance_{target_kind}_missing"] += int(provenance_missing)
                counts[f"route_{target_kind}_available"] += int(route_available)
                if v39_file.get("exists") and not prov["available"]:
                    counts[f"v39_{target_kind}_without_provenance"] += 1
                if v39_file.get("exists") and not route_available:
                    counts[f"v39_{target_kind}_without_route_map"] += 1
                target = {
                    "registry_rank": rank,
                    "gallery": gallery,
                    "category": registry_row["category"],
                    "source_page_route": page_route,
                    "slot": slot,
                    "target_kind": target_kind,
                    "expected_url": route,
                    "expected_deployed_url": deploy_url,
                    "expected_full_url": DEPLOY_BASE + full_route,
                    "expected_thumb_url": DEPLOY_BASE + thumb_route,
                    "v39_file": v39_file,
                    "source15_file": source15_file,
                    "original_offline_file": original_file,
                    "v39_provenance": prov,
                    "v39_route_map": {
                        "available": route_available,
                        "value": map_value,
                        "value_matches_expected": route_value_matches,
                    },
                    "source15_missing_from_v39": source15_missing,
                    "original_missing_from_v39": original_missing,
                    "provenance_target_missing_from_v39": provenance_missing,
                    "native_static_img_reference": route in static_routes,
                    "guide_preview_excluded": False,
                }
                targets.append(target)
        # Compute pair counts from the target slice just emitted for this row.
        row_targets = targets[-declared_slots * 2 :]
        by_slot: dict[int, dict[str, dict[str, Any]]] = defaultdict(dict)
        for target in row_targets:
            by_slot[int(target["slot"])][str(target["target_kind"])] = target
        for slot_map in by_slot.values():
            if all(slot_map.get(k, {}).get("v39_file", {}).get("exists") for k in ("full", "thumb")):
                counts["v39_complete_pairs_exists"] += 1
            if all(slot_map.get(k, {}).get("v39_file", {}).get("valid_jpeg") for k in ("full", "thumb")):
                counts["v39_complete_pairs_valid"] += 1
            if all(slot_map.get(k, {}).get("source15_file", {}).get("exists") for k in ("full", "thumb")):
                counts["source15_complete_pairs_exists"] += 1
            if all(slot_map.get(k, {}).get("original_offline_file", {}).get("exists") for k in ("full", "thumb")):
                counts["original_complete_pairs_exists"] += 1
        page_row["target_counts"] = dict(counts)
        page_row["target_counts"]["expected_full_targets"] = declared_slots
        page_row["target_counts"]["expected_thumb_targets"] = declared_slots
        page_row["target_counts"]["expected_entities"] = declared_slots * 2
        rows.append(page_row)

    if validation_errors:
        # Do not generate a superficially complete 3368-row result when the
        # frozen page/registry contract changed.  The caller can inspect the
        # explicit error in stderr and decide whether to revise the plan.
        raise RuntimeError("parser or source declaration conflicts:\n" + "\n".join(validation_errors))
    if len(targets) != 3368:
        raise RuntimeError(f"generated {len(targets)} targets, expected 3368")

    actual_page_preview_sections = [
        {
            "registry_rank": row["registry_rank"],
            "gallery": row["gallery"],
            "source_page_route": row["source_page_route"],
            "sections": row["current_v39"]["guide_preview_sections"],
        }
        for row in rows
        if row["current_v39"]["guide_preview_sections"]
    ]
    current_preview_img_count = sum(
        int(section.get("actual_img_count", 0))
        for page in actual_page_preview_sections
        for section in page["sections"]
    )
    current_preview_declared_count = sum(
        int(section["declared_count"] or 0)
        for page in actual_page_preview_sections
        for section in page["sections"]
    )

    # Aggregates are intentionally computed from target records, not copied
    # from the registry's historical audit statuses.
    target_count = Counter()
    for target in targets:
        target_count["v39_exists"] += int(target["v39_file"].get("exists", False))
        target_count["v39_valid_jpeg"] += int(target["v39_file"].get("valid_jpeg", False))
        target_count["source15_exists"] += int(target["source15_file"].get("exists", False))
        target_count["original_exists"] += int(target["original_offline_file"].get("exists", False))
        target_count["source15_missing_from_v39"] += int(target["source15_missing_from_v39"])
        target_count["original_missing_from_v39"] += int(target["original_missing_from_v39"])
        target_count["provenance_target_missing_from_v39"] += int(target["provenance_target_missing_from_v39"])
        target_count["provenance_available"] += int(target["v39_provenance"]["available"])
        target_count["route_map_available"] += int(target["v39_route_map"]["available"])
        target_count["route_map_value_matches"] += int(target["v39_route_map"]["value_matches_expected"])
        target_count["v39_without_provenance"] += int(target["v39_file"].get("exists", False) and not target["v39_provenance"]["available"])
        target_count["v39_without_route_map"] += int(target["v39_file"].get("exists", False) and not target["v39_route_map"]["available"])
    pair_counts = Counter()
    for row in rows:
        for key in ("v39_complete_pairs_exists", "v39_complete_pairs_valid", "source15_complete_pairs_exists", "original_complete_pairs_exists"):
            pair_counts[key] += int(row["target_counts"].get(key, 0))

    by_category: dict[str, dict[str, int]] = {}
    for row in rows:
        cat = str(row["category"])
        bucket = by_category.setdefault(cat, {"galleries": 0, "slots": 0, "expected_entities": 0, "v39_entities": 0, "v39_valid_entities": 0})
        bucket["galleries"] += 1
        bucket["slots"] += int(row["declared_slots"])
        bucket["expected_entities"] += int(row["expected_direct_entities"])
        bucket["v39_entities"] += int(row["target_counts"].get("v39_full_exists", 0) + row["target_counts"].get("v39_thumb_exists", 0))
        bucket["v39_valid_entities"] += int(row["target_counts"].get("v39_full_valid", 0) + row["target_counts"].get("v39_thumb_valid", 0))

    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    input_hashes = {
        "registry": registry_meta["sha256"],
        "v39_export_provenance": provenance_meta["sha256"],
        "v39_route_map": route_map_meta["sha256"],
        "v39_sidebar": v39_sidebar["sha256"],
        "runtime": runtime_meta["sha256"],
    }
    input_sizes = {
        "registry": registry_meta["bytes"],
        "v39_export_provenance": provenance_meta["bytes"],
        "v39_route_map": route_map_meta["bytes"],
        "v39_sidebar": v39_sidebar["bytes"],
        "runtime": runtime_meta["bytes"],
    }
    guide_metadata = {
        "v39_provenance_guide_previews": {
            "group_count": provenance.get("guide_previews", {}).get("group_count"),
            "preview_count": provenance.get("guide_previews", {}).get("preview_count"),
            "groups": [
                {
                    "group_id": x.get("group_id"),
                    "gallery_route": x.get("gallery_route"),
                    "preview_count": x.get("preview_count"),
                    "guide_route": x.get("guide_route"),
                }
                for x in provenance.get("guide_previews", {}).get("groups", [])
            ],
        },
        "v39_provenance_guide_image_collections": {
            "group_count": provenance.get("guide_image_collections", {}).get("group_count"),
            "image_count": provenance.get("guide_image_collections", {}).get("image_count"),
            "groups": [
                {
                    "group_id": x.get("group_id"),
                    "gallery_route": x.get("gallery_route"),
                    "image_count": x.get("image_count"),
                    "guide_route": x.get("guide_route"),
                }
                for x in provenance.get("guide_image_collections", {}).get("groups", [])
            ],
        },
        "current_v39_page_preview_sections": {
            "page_count": len(actual_page_preview_sections),
            "section_count": sum(len(x["sections"]) for x in actual_page_preview_sections),
            "actual_img_count": current_preview_img_count,
            "declared_count_sum": current_preview_declared_count,
            "pages": actual_page_preview_sections,
        },
        "separation_rule": "Nested thumbs, guide preview images, missing SVGs, comments, and expression URLs are excluded from the native target set; only the literal addshots()/printPages() JPEG rules generate native targets.",
    }
    method = {
        "scope": "all 50 canonical gallery registry rows; exact declared slot targets only",
        "no_network": True,
        "no_browser": True,
        "no_directory_scan": True,
        "selected_input_limit_boundary": "Metadata pages/provenance/route map were read as selected inputs; target file reads were limited to the 3368 exact full/thumb paths.",
        "runtime_path": rel(RUNTIME_PATH),
        "runtime_semantics_lines": {"addshots": 471, "full_url_assignment": 486, "thumbnail_rewrite": 506},
        "full_url_rule": "sourceDirectory + filename + (slot) + .jpg, for slots 1..numShots",
        "thumb_url_rule": "full URL with .jpg replaced by -thumb.jpg in the same directory",
        "default_reverse_order": False,
        "dom_only_slider_rule": "No exact native full/thumb <img> src in the page plus one valid literal addshots() declaration.",
        "guide_preview_rule": "Guide preview sections are retained and counted separately; their nested thumbs never enter the 3368 native target rows.",
        "provenance_rule": "A v39 provenance match is route-keyed and may have multiple entries; all roles and source paths are retained in compact form.",
    }
    source_refs = {
        "registry": {"path": rel(REGISTRY_PATH), "sha256": registry_meta["sha256"], "json_pointer": "/coverage_rows", "source_evidence_line_fields": ["numShots_line", "addshots_line"]},
        "v39_provenance": {"path": rel(V39_PROVENANCE_PATH), "sha256": provenance_meta["sha256"], "json_pointer": "/files", "guide_preview_pointer": "/guide_previews", "guide_collection_pointer": "/guide_image_collections"},
        "v39_route_map": {"path": rel(V39_ROUTE_MAP_PATH), "sha256": route_map_meta["sha256"], "json_pointer": "/routes"},
        "v39_sidebar": {"path": rel(V39_SIDEBAR_PATH), "sha256": v39_sidebar["sha256"], "gallery_link_line_numbers": True},
        "runtime": {"path": rel(RUNTIME_PATH), "sha256": runtime_meta["sha256"], "lines": {"addshots": 471, "full_assignment": 486, "thumb_rewrite": 506}},
    }
    source_boundaries = [
        "The registry is a frozen 50-gallery/1684-slot expectation and its historical CDX statuses are not reused as current file availability.",
        "A missing exact file, provenance entry, or route-map entry is reported as missing/unknown for this local checkout; it is not a remote 404 or proof of historical absence.",
        "Source15 and original offline files are compared only at exact native full/thumb target paths; guide collections and nested thumbs are counted separately.",
        "Pillow decode is local file evidence. It does not prove browser deployment, remote capture validity, or public reachability.",
        "No source manifest, ZIP, raw response, private page, or unrelated image directory was scanned.",
    ]

    package = {
        "schema": "player-gallery-accessibility/v1",
        "generated_at_utc": generated,
        "input_hashes": input_hashes,
        "input_sizes_bytes": input_sizes,
        "method": method,
        "source_refs": source_refs,
        "source_boundaries": source_boundaries,
        "registry": {
            "path": rel(REGISTRY_PATH),
            "gallery_count": len(coverage_rows),
            "declared_slots": sum(int(x["declared_slots"]) for x in coverage_rows),
            "expected_direct_entities": sum(int(x["declared_slots"]) * 2 for x in coverage_rows),
            "frozen_stats": registry.get("stats", {}),
        },
        "sidebar": {
            "path": v39_sidebar["path"],
            "sha256": v39_sidebar["sha256"],
            "gallery_link_count": len(v39_sidebar["gallery_links"]),
            "unique_gallery_route_count": len(sidebar_map),
            "registry_routes_present": sum(int(row["source_page_route"] in sidebar_map) for row in rows),
            "registry_routes_missing": [row["source_page_route"] for row in rows if row["source_page_route"] not in sidebar_map],
        },
        "guide_metadata": guide_metadata,
        "coverage": {
            "gallery_count": len(rows),
            "slot_count": sum(int(row["declared_slots"]) for row in rows),
            "expected_target_count": len(targets),
            "target_kind_counts": dict(Counter(str(x["target_kind"]) for x in targets)),
            "target_counts": dict(target_count),
            "pair_counts": dict(pair_counts),
            "by_category": by_category,
            "missing_from_deploy": {
                "source15_exact_native_targets": target_count["source15_missing_from_v39"],
                "original_exact_native_targets": target_count["original_missing_from_v39"],
                "provenance_backed_exact_targets": target_count["provenance_target_missing_from_v39"],
                "all_expected_exact_targets": len(targets) - target_count["v39_exists"],
            },
        },
        "rows": rows,
        "validation": {
            "registry_hash_matches_frozen": actual_registry_sha == EXPECTED_REGISTRY_SHA256,
            "v39_provenance_hash_matches_frozen": actual_provenance_sha == EXPECTED_V39_PROVENANCE_SHA256,
            "runtime_hash_matches_frozen": actual_runtime_sha == EXPECTED_RUNTIME_SHA256,
            "generated_target_rows": len(targets),
            "expected_target_rows": 3368,
            "all_rows_declaration_valid": not validation_errors,
            "all_current_pages_have_runtime": all(bool(row["current_v39"]["runtime_script_matches"]) for row in rows),
            "all_current_pages_deploy_rewrite": all(row["current_v39"]["addshots_rewrite_status"] == "repaired_current_deploy_base" for row in rows),
            "all_current_pages_dom_only_slider": sum(int(row["current_v39"]["dom_only_slider"]) for row in rows),
            "current_preview_page_count": len(actual_page_preview_sections),
            "current_preview_img_count": current_preview_img_count,
            "file_bytes_read_for_exact_targets": read_stats["bytes"],
            "pillow_available": Image is not None,
        },
    }

    package_path = OUT_DIR / "gallery-accessibility-50.json"
    targets_path = OUT_DIR / "gallery-targets-3368.csv"
    summary_path = OUT_DIR / "gallery-accessibility-summary.json"
    dump_json(package_path, package)
    csv_fields = [
        "registry_rank",
        "gallery",
        "category",
        "source_page_route",
        "slot",
        "target_kind",
        "expected_url",
        "expected_deployed_url",
        "expected_full_url",
        "expected_thumb_url",
        "v39_exists",
        "v39_bytes",
        "v39_sha256",
        "v39_valid_jpeg",
        "v39_jpeg_format",
        "v39_width",
        "v39_height",
        "v39_path",
        "v39_provenance_available",
        "v39_provenance_entry_count",
        "v39_provenance_roles",
        "v39_provenance_source_paths",
        "v39_route_map_available",
        "v39_route_map_value_matches",
        "source15_exists",
        "source15_bytes",
        "source15_sha256",
        "source15_valid_jpeg",
        "source15_path",
        "original_offline_exists",
        "original_offline_bytes",
        "original_offline_sha256",
        "original_offline_valid_jpeg",
        "original_offline_path",
        "source15_missing_from_v39",
        "original_missing_from_v39",
        "provenance_target_missing_from_v39",
        "native_static_img_reference",
        "guide_preview_excluded",
    ]
    with targets_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=csv_fields)
        writer.writeheader()
        for target in targets:
            vf, sf, of = target["v39_file"], target["source15_file"], target["original_offline_file"]
            prov = target["v39_provenance"]
            writer.writerow(
                {
                    "registry_rank": target["registry_rank"],
                    "gallery": target["gallery"],
                    "category": target["category"],
                    "source_page_route": target["source_page_route"],
                    "slot": target["slot"],
                    "target_kind": target["target_kind"],
                    "expected_url": target["expected_url"],
                    "expected_deployed_url": target["expected_deployed_url"],
                    "expected_full_url": target["expected_full_url"],
                    "expected_thumb_url": target["expected_thumb_url"],
                    "v39_exists": vf.get("exists", False),
                    "v39_bytes": vf.get("bytes"),
                    "v39_sha256": vf.get("sha256"),
                    "v39_valid_jpeg": vf.get("valid_jpeg", False),
                    "v39_jpeg_format": vf.get("jpeg_format"),
                    "v39_width": vf.get("width"),
                    "v39_height": vf.get("height"),
                    "v39_path": vf.get("path"),
                    "v39_provenance_available": prov["available"],
                    "v39_provenance_entry_count": prov["entry_count"],
                    "v39_provenance_roles": ";".join(prov["roles"]),
                    "v39_provenance_source_paths": ";".join(prov["source_paths"] + prov["source_offline_paths"]),
                    "v39_route_map_available": target["v39_route_map"]["available"],
                    "v39_route_map_value_matches": target["v39_route_map"]["value_matches_expected"],
                    "source15_exists": sf.get("exists", False),
                    "source15_bytes": sf.get("bytes"),
                    "source15_sha256": sf.get("sha256"),
                    "source15_valid_jpeg": sf.get("valid_jpeg", False),
                    "source15_path": sf.get("path"),
                    "original_offline_exists": of.get("exists", False),
                    "original_offline_bytes": of.get("bytes"),
                    "original_offline_sha256": of.get("sha256"),
                    "original_offline_valid_jpeg": of.get("valid_jpeg", False),
                    "original_offline_path": of.get("path"),
                    "source15_missing_from_v39": target["source15_missing_from_v39"],
                    "original_missing_from_v39": target["original_missing_from_v39"],
                    "provenance_target_missing_from_v39": target["provenance_target_missing_from_v39"],
                    "native_static_img_reference": target["native_static_img_reference"],
                    "guide_preview_excluded": target["guide_preview_excluded"],
                }
            )

    summary = {
        "schema": "player-gallery-accessibility-summary/v1",
        "generated_at_utc": generated,
        "package": rel(package_path),
        "targets_csv": rel(targets_path),
        "input_hashes": input_hashes,
        "coverage": package["coverage"],
        "guide_metadata": guide_metadata,
        "source_refs": source_refs,
        "method": method,
        "source_boundaries": source_boundaries,
        "validation": package["validation"],
    }
    dump_json(summary_path, summary)
    print(json.dumps({"package": rel(package_path), "targets_csv": rel(targets_path), "summary": rel(summary_path), "coverage": package["coverage"], "validation": package["validation"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

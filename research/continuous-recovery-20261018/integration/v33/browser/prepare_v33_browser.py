#!/usr/bin/env python3
"""Prepare the bounded v33 browser delta input.

The preparer is deliberately offline and preparation-only.  It reads the
already accepted v33 maps, impact estimate, source-receipts manifest, and
completed v33 provenance.  It never searches pending folders, performs HTTP,
starts a browser, or writes an export.  The resulting input is immutable and
is consumed by ``check_v33_browser.cjs`` only after root supplies a browser
GO gate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[5]
INTEGRATION = ROOT / "research/continuous-recovery-20261018/integration/v33"
BROWSER = INTEGRATION / "browser"
BUILDER = INTEGRATION / "build_pages_v33.py"
PRIMARY_MAP = INTEGRATION / "v33-primary-source-map.json"
SUPPLEMENT_MAP = INTEGRATION / "v33-supplement-source-map.json"
IMPACT = INTEGRATION / "v33-impact-estimate.json"
SOURCE_AUDIT = INTEGRATION / "v33-source-byte-audit.json"
PREPARATION = INTEGRATION / "v33-input-preparation.json"
PREFLIGHT = INTEGRATION / "v33-preflight.json"
SOURCE_MANIFEST = ROOT / "research/continuous-recovery-20261018/publication/root-v33-source-receipts-manifest-r2.json"
SOURCE15 = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
V32_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v32/export-provenance.json"
V33_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v33/export-provenance.json"
V32_BROWSER = ROOT / "research/continuous-recovery-20261018/publication/root-v32-browser-acceptance.json"
V32_CONTROLS = ROOT / "research/continuous-recovery-20261018/publication/root-v32-controls-browser-acceptance.json"
V32_CONTENT = ROOT / "research/continuous-recovery-20261018/publication/root-v32-content-browser-retry4-acceptance.json"
V32_CHART = ROOT / "research/continuous-recovery-20261018/publication/root-v32-chart-browser-acceptance.json"
ROOT_POPUP_TOOL = ROOT / "research/continuous-recovery-20261018/publication/root-popup-tool-acceptance.json"
ROOT_NAVIGATION_TOOL = ROOT / "research/continuous-recovery-20261018/publication/root-navigation-image-tool-acceptance.json"
ROOT_RETIRED_TOOL = ROOT / "research/continuous-recovery-20261018/publication/root-retired-armory-tool-acceptance.json"
ROOT_MASK_TOOL = ROOT / "research/continuous-recovery-20261018/publication/root-attunement-mask-tool-acceptance.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261018-v33"
INPUT = BROWSER / "v33-browser-input.json"
CHECKER = BROWSER / "check_v33_browser.cjs"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
EXPECTED_V32_BROWSER_SHA256 = "8fd8a2ba0179aec95236d08f6a14abb776d716c92fd1c2beb91bbdfe39c93307"
EXPECTED_V32_CONTROLS_SHA256 = "bd6542a2b42cab56e311c8f5db9fe66a96be3b903abef0b06acb2dbaf68d41a6"
EXPECTED_V32_CONTENT_SHA256 = "9718cb7ed0b713ecdbdd5ec4307c49c663f6269615a8e2231c888f62828cf83c"
EXPECTED_V32_CHART_SHA256 = "2740789c744743f871014bfd6862f0097d2f721e80d825c5dfcd527b0450c245"
EXPECTED_EXPORTER_SHA256 = "2a6fa4256ad0853797ae10748ef7842896614d419bdb7ad208d9b258dc8e6488"
IMAGE_EXTENSIONS = frozenset({".gif", ".png", ".jpg", ".jpeg", ".webp", ".bmp"})
PRIMARY_HOSTS = frozenset({"www.worldofwarcraft.com", "worldofwarcraft.com"})


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


def inside(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"{label} escapes workspace: {path}") from exc
    return resolved


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"invalid JSON for {label}: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


_MISSING = object()


def preflight_export_executed(preflight: dict) -> object:
    """Read the strict offline-export marker across the frozen preflight schema."""
    marker = preflight.get("export_executed", _MISSING)
    if marker is not _MISSING:
        return marker
    loader_preflight = preflight.get("loader_preflight")
    if isinstance(loader_preflight, dict):
        return loader_preflight.get("export_executed", _MISSING)
    return _MISSING


def binding(path: Path, expected: str | None = None) -> dict:
    path = inside(path, "binding")
    actual = sha256_file(path)
    if expected and actual.casefold() != expected.casefold():
        raise RuntimeError(f"binding SHA changed for {rel(path)}: {actual} != {expected}")
    return {"path": rel(path), "sha256": actual}


def load_exporter():
    """Load only the accepted exporter module; no exporter entry point runs."""

    if not (ROOT / "tools").is_dir():
        raise RuntimeError("missing tools directory")
    exporter_path = ROOT / "tools/export_github_pages.py"
    actual = sha256_file(exporter_path)
    if actual.casefold() != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError(f"accepted exporter SHA changed: {actual} != {EXPECTED_EXPORTER_SHA256}")
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("wow_v33_browser_exporter", exporter_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load accepted exporter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def origin_key(url: str) -> str:
    parsed = urlsplit(str(url))
    host = (parsed.hostname or "").casefold().rstrip(".")
    if host in PRIMARY_HOSTS:
        host = "www.worldofwarcraft.com"
    return f"{host}{parsed.path or '/'}"


def requested_from_target(target: str) -> str:
    try:
        values = parse_qs(urlsplit(target).query, keep_blank_values=True).get("requested", [])
        return unquote(values[-1]) if values else ""
    except (TypeError, ValueError):
        return ""


_POPUP_RE = re.compile(r"\bpopUpOmega\s*\(\s*(['\"])(?P<path>.*?)\1", re.I | re.S)
_NEWS_ENTRY_RE = re.compile(r"<(?P<tag>[A-Za-z][\w:-]*)\b(?P<attrs>[^>]*\bid\s*=\s*['\"](?P<id>news[^'\"]+)['\"][^>]*)>", re.I | re.S)


def popup_original(literal: str, source_base_url: str) -> str | None:
    """Resolve the first literal image argument of a historical popUpOmega call."""

    match = _POPUP_RE.search(str(literal))
    if not match:
        return None
    raw = match.group("path").replace("\\'", "'").replace('\\"', '"')
    resolved = urljoin(source_base_url, raw)
    parsed = urlsplit(resolved)
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        return None
    return resolved


def page_kind(route: str) -> str:
    lower = route.casefold()
    if lower.startswith("/news/"):
        return "news"
    if "/wallpaper" in lower or lower.startswith("/wallpapers"):
        return "wallpaper"
    if lower.startswith(("/info/", "/insider/", "/pvp/", "/burningcrusade/", "/community/")):
        return "guide_or_content"
    return "other"


def page_output_path(record: dict, exporter) -> str:
    route = str(record.get("route") or "")
    if not route.startswith("/"):
        raise RuntimeError(f"source record has no absolute route: {route!r}")
    return exporter.static_rel_for_route(route, record)


def news_toggle_ids(page_output: str) -> list[str]:
    """Capture the actual derived news entry ids used by the browser checker."""

    page = inside(OUTPUT / page_output, "news browser page")
    if not page.is_file():
        raise RuntimeError(f"news page is missing from v33 output: {page}")
    text = page.read_text(encoding="utf-8", errors="replace")
    result: list[str] = []
    for match in _NEWS_ENTRY_RE.finditer(text):
        attrs = match.group("attrs")
        classes = re.search(r"\bclass\s*=\s*(['\"])(.*?)\1", attrs, re.I | re.S)
        if classes and "news-collapse" in classes.group(2).casefold():
            result.append(match.group("id"))
    return list(dict.fromkeys(result))


def derive_image_route(original: str, exporter) -> tuple[str, str]:
    if exporter.mirror.is_primary_origin(original):
        route = exporter.mirror.route_path(original)
    else:
        route = exporter.mirror.origin_route(original)
    return route, exporter.static_rel_for_route(route)


def _record_reference_candidates(record: dict, reference: dict) -> list[tuple[str, str]]:
    """Return (kind, absolute URL) candidates without guessing URLs."""

    candidates: list[tuple[str, str]] = []
    literal = str(reference.get("literal") or "")
    base = str(record.get("source_base_url") or "")
    popup = popup_original(literal, base) if "popupomega" in literal.casefold() else None
    if popup:
        candidates.append(("popup", popup))
    resolved = str(reference.get("resolved_url") or "")
    if urlsplit(resolved).scheme.casefold() in {"http", "https"} and urlsplit(resolved).hostname:
        candidates.append(("resolved", resolved))
    requested = requested_from_target(str(reference.get("target") or ""))
    if urlsplit(requested).scheme.casefold() in {"http", "https"} and urlsplit(requested).hostname:
        candidates.append(("requested", requested))
    return candidates


def derive_references(records: list[dict], items: list[dict], exporter) -> dict:
    """Join source manifest references to accepted new originals by exact origin key."""

    by_origin = {origin_key(str(item.get("original") or item.get("logical_url") or "")): item for item in items}
    matches: list[dict] = []
    seen: set[tuple[str, str, str, str]] = set()
    for record in records:
        route = str(record.get("route") or "")
        if not route:
            continue
        output = page_output_path(record, exporter)
        for reference in record.get("references", []) or []:
            if not isinstance(reference, dict):
                continue
            target = str(reference.get("target") or "")
            target_path = urlsplit(target).path.casefold()
            for match_kind, candidate in _record_reference_candidates(record, reference):
                item = by_origin.get(origin_key(candidate))
                if item is None:
                    continue
                original = str(item.get("original") or item.get("logical_url") or "")
                key = (route, original, target, match_kind)
                if key in seen:
                    continue
                seen.add(key)
                is_navigation = target_path == "/__offline/missing.html" and str(reference.get("context") or "") == "navigation"
                is_svg_marker = target_path == "/__offline/missing-image.svg"
                is_popup = match_kind == "popup"
                matches.append({
                    "original": original,
                    "role": str(item.get("overlay_role") or ""),
                    "page_route": route,
                    "page_output": output,
                    "page_kind": page_kind(route),
                    "source_page_sha256": str(record.get("source_sha256") or ""),
                     "source_base_url": str(record.get("source_base_url") or ""),
                    "source_line": reference.get("line") or reference.get("line_number") or reference.get("source_line"),
                    "literal": str(reference.get("literal") or ""),
                    "resolved_url": str(reference.get("resolved_url") or ""),
                    "target": target,
                    "requested": requested_from_target(target),
                    "action": str(reference.get("action") or ""),
                    "context": str(reference.get("context") or ""),
                    "reason": str(reference.get("reason") or ""),
                    "match_kind": match_kind,
                    "popup_full_image": is_popup,
                    "ordinary_image_href": is_navigation,
                    "missing_image_svg_marker": is_svg_marker,
                    "static_render_candidate": str(reference.get("context") or "") in {"image", "css_url", "style", "background"},
                })
    popup_by_original: dict[str, dict] = {}
    ordinary_by_original: dict[str, dict] = {}
    static_by_original: dict[str, dict] = {}
    for row in matches:
        original = row["original"]
        if row["popup_full_image"]:
            popup_by_original.setdefault(original, row)
        if row["ordinary_image_href"]:
            ordinary_by_original.setdefault(original, row)
        if row["static_render_candidate"]:
            static_by_original.setdefault(original, row)
    return {
        "all_matches": matches,
        "popup_full_image_links": list(popup_by_original.values()),
        "ordinary_image_hrefs": list(ordinary_by_original.values()),
        "static_render_targets": list(static_by_original.values()),
        "popup_missing_originals": sorted(set(by_origin) - {origin_key(x) for x in popup_by_original}),
        "ordinary_missing_originals": sorted(set(by_origin) - {origin_key(x) for x in ordinary_by_original}),
    }


def load_new_items(primary: dict, supplement: dict) -> list[dict]:
    items: list[dict] = []
    for payload, expected_role in ((primary, "primary_image_overlay"), (supplement, "supplement_image_overlay")):
        for index, item in enumerate(payload.get("items") or []):
            if not isinstance(item, dict) or not item.get("original"):
                raise RuntimeError(f"v33 map {expected_role} item {index} is malformed")
            if str(item.get("overlay_role")) != expected_role:
                raise RuntimeError(f"v33 map role mismatch at {expected_role}[{index}]")
            local = inside(ROOT / str(item.get("local_path") or ""), "v33 accepted image")
            data = local.read_bytes()
            if len(data) != int(item.get("length", -1)) or sha256_bytes(data) != str(item.get("sha256") or "").casefold():
                raise RuntimeError(f"v33 map source bytes differ: {item.get('original')}")
            item = dict(item)
            item["_map_role"] = expected_role
            items.append(item)
    if len({origin_key(str(x["original"])) for x in items}) != len(items):
        raise RuntimeError("v33 new map originals overlap each other")
    return items


def load_frozen_v32_items(provenance: dict) -> list[dict]:
    """Read the accepted v32 image-overlay metadata for old href validation.

    These rows are already accepted by the v32 provenance receipt.  We keep
    them separate from ``new_originals`` so the browser delta does not count
    them as newly acquired HTTP images, while still allowing ordinary image
    hrefs healed by the v33 navigation route to be checked against the full
    frozen closure.
    """

    items: list[dict] = []
    for index, row in enumerate(provenance.get("files", []) or []):
        if not isinstance(row, dict) or str(row.get("kind")) != "image_overlay":
            continue
        if str(row.get("role")) != "image_overlay":
            raise RuntimeError(f"v32 provenance image row has unexpected role at {index}")
        original = str(row.get("original_url") or "")
        output_path = str(row.get("output_path") or "")
        length = row.get("derived_length")
        sha256 = str(row.get("derived_sha256") or "").casefold()
        if not original or not output_path or not sha256 or length is None:
            raise RuntimeError(f"v32 provenance image row is incomplete at {index}")
        if output_path.startswith("/") or ".." in output_path.replace("\\", "/").split("/"):
            raise RuntimeError(f"unsafe frozen v32 output path: {output_path!r}")
        items.append({
            "original": original,
            "overlay_role": "frozen_v32_image_overlay",
            "_map_role": "frozen_v32_image_overlay",
            "length": int(length),
            "sha256": sha256,
            "mime": str(row.get("mime") or ""),
            "dimensions": None,
            "served_route": str(row.get("route") or ""),
            "served_output_path": output_path,
            "served_url": str(row.get("static_url") or (BASE_PATH + output_path)),
            "served_sha256": sha256,
            "served_length": int(length),
            "origin_namespace": row.get("origin_namespace"),
            "actual_capture_timestamp": row.get("actual_capture_timestamp"),
        })
    if len({origin_key(str(item["original"])) for item in items}) != len(items):
        raise RuntimeError("frozen v32 image-overlay originals overlap")
    return items


def validate_frozen_v32_records(provenance: dict, items: list[dict]) -> list[dict]:
    """Bind old image routes to the v33 provenance without rehashing all old bytes."""

    by_origin = {}
    for row in provenance.get("files", []) or []:
        if not isinstance(row, dict):
            continue
        original = row.get("original_url") or row.get("original") or row.get("logical_url")
        if original:
            by_origin[origin_key(str(original))] = row
    result: list[dict] = []
    for item in items:
        original = str(item["original"])
        row = by_origin.get(origin_key(original))
        if row is None or str(row.get("kind")) != "image_overlay" or str(row.get("role")) != "image_overlay":
            raise RuntimeError(f"v33 provenance has no preserved v32 image overlay for {original}")
        if str(row.get("output_path") or "") != str(item["served_output_path"]):
            raise RuntimeError(f"v33 changed preserved v32 output route for {original}")
        if int(row.get("derived_length", -1)) != int(item["served_length"]):
            raise RuntimeError(f"v33 changed preserved v32 output length for {original}")
        if str(row.get("derived_sha256") or "").casefold() != str(item["served_sha256"]).casefold():
            raise RuntimeError(f"v33 changed preserved v32 output SHA for {original}")
        result.append(dict(item))
    return result


def provenance_records(provenance: dict, items: list[dict]) -> list[dict]:
    by_origin = {}
    for row in provenance.get("files", []) or []:
        if not isinstance(row, dict):
            continue
        original = row.get("original_url") or row.get("original") or row.get("logical_url")
        if original:
            by_origin[origin_key(str(original))] = row
    result: list[dict] = []
    for item in items:
        original = str(item["original"])
        row = by_origin.get(origin_key(original))
        if row is None or str(row.get("kind")) != "image_overlay":
            raise RuntimeError(f"v33 provenance has no image overlay for {original}")
        output_path = str(row.get("output_path") or "")
        if not output_path or output_path.startswith("/") or ".." in output_path.replace("\\", "/").split("/"):
            raise RuntimeError(f"unsafe v33 provenance output path for {original}: {output_path!r}")
        output_file = inside(OUTPUT / output_path, "v33 output image")
        if not output_file.is_file():
            raise RuntimeError(f"v33 output image is missing: {output_file}")
        data = output_file.read_bytes()
        if len(data) != int(item["length"]) or sha256_bytes(data) != str(item["sha256"]).casefold():
            raise RuntimeError(f"v33 output bytes differ for {original}")
        result.append({
            "original": original,
            "route": str(row.get("route") or ""),
            "output_path": output_path,
            "static_url": str(row.get("static_url") or (BASE_PATH + output_path)),
            "output_sha256": sha256_bytes(data),
            "output_length": len(data),
            "mime": str(row.get("mime") or item.get("mime") or ""),
            "dimensions": item.get("dimensions"),
            "actual_capture_timestamp": item.get("actual_timestamp"),
            "origin_namespace": row.get("origin_namespace"),
            "overlay_role": row.get("supplement_strategy") or row.get("role") or item.get("overlay_role"),
        })
    return result


def recovery_scope(impact: dict) -> dict:
    navigation = impact.get("navigation_href_recovery") or {}
    markers = impact.get("missing_image_svg_marker_recovery") or {}
    return {
        "navigation_href_recovery": {
            "count": int(navigation.get("count", len(navigation.get("references") or []))),
            "references": navigation.get("references") or [],
        },
        "missing_image_svg_marker_recovery": {
            "count": int(markers.get("count", len(markers.get("references") or []))),
            "references": markers.get("references") or [],
        },
        "scope_note": "All frozen v32 plus explicit v33 validated origins are allowed; navigation hrefs and SVG markers are counted separately and remain static estimates until browser evidence.",
    }


def build_input() -> dict:
    # This gate is intentionally strict: a browser delta cannot be prepared
    # from maps or pending receipts that root has not accepted and exported.
    required = [
        (SOURCE_MANIFEST, "root v33 source-receipts manifest"),
        (PRIMARY_MAP, "v33 primary map"),
        (SUPPLEMENT_MAP, "v33 supplement map"),
        (IMPACT, "v33 impact estimate"),
        (SOURCE_AUDIT, "v33 source byte audit"),
        (PREPARATION, "v33 input preparation"),
        (PREFLIGHT, "v33 preflight"),
        (V33_PROVENANCE, "v33 export provenance"),
        (OUTPUT / "export-provenance.json", "v33 export provenance in output"),
        (V32_PROVENANCE, "v32 provenance"),
        (V32_BROWSER, "v32 browser baseline"),
        (V32_CONTROLS, "v32 controls browser baseline"),
        (V32_CONTENT, "v32 content browser baseline"),
        (V32_CHART, "v32 chart browser baseline"),
        (ROOT_POPUP_TOOL, "root popup tool acceptance"),
        (ROOT_NAVIGATION_TOOL, "root navigation tool acceptance"),
        (ROOT_RETIRED_TOOL, "root retired Armory tool acceptance"),
        (ROOT_MASK_TOOL, "root attunement mask tool acceptance"),
    ]
    missing = [str(path) for path, _ in required if not path.is_file()]
    if missing:
        raise RuntimeError("v33 browser input gate is not ready; missing: " + ", ".join(missing))
    exporter = load_exporter()
    source = read_json(SOURCE_MANIFEST, "root v33 source-receipts manifest")
    if source.get("accepted") is not True or source.get("network_requests") not in {0, None} or source.get("export_executed") not in {False, None}:
        raise RuntimeError("root v33 source manifest is not an accepted offline input")
    primary = read_json(PRIMARY_MAP, "v33 primary map")
    supplement = read_json(SUPPLEMENT_MAP, "v33 supplement map")
    items = load_new_items(primary, supplement)
    source15 = read_json(SOURCE15, "source15 manifest")
    records = [row for row in source15.get("files", []) if isinstance(row, dict)]
    v32_provenance = read_json(V32_PROVENANCE, "v32 provenance")
    frozen_v32_items = load_frozen_v32_items(v32_provenance)
    provenance = read_json(V33_PROVENANCE, "v33 provenance")
    output_items = provenance_records(provenance, items)
    validated_v32_items = validate_frozen_v32_records(provenance, frozen_v32_items)
    ref_sets = derive_references(records, items, exporter)
    all_ref_sets = derive_references(records, validated_v32_items + items, exporter)
    impact = read_json(IMPACT, "v33 impact estimate")
    source_audit = read_json(SOURCE_AUDIT, "v33 source byte audit")
    prep = read_json(PREPARATION, "v33 preparation")
    preflight = read_json(PREFLIGHT, "v33 preflight")
    if source_audit.get("all_byte_match") is not True or int(source_audit.get("source_count", -1)) != len(items):
        raise RuntimeError("v33 source audit is not an exact all-byte-match audit for the new maps")
    if not str(prep.get("status") or "").startswith("prepared_waiting_root_v33") or not str(preflight.get("status") or "").startswith("preflight_passed_waiting_root_v33"):
        raise RuntimeError("v33 preparation/preflight status is not root-waiting")
    if preflight_export_executed(preflight) is not False or prep.get("export_executed") is not False:
        raise RuntimeError("v33 preparation records export activity")
    item_by_original = {str(row["original"]): row for row in output_items}
    popup_items = [row for row in ref_sets["popup_full_image_links"] if row["original"] in item_by_original]
    popup_expected = {
        str(item["original"])
        for item in items
        if "popup24" in str(item.get("source_acceptance_path") or "").casefold()
        or "popup24" in str(item.get("public_copy_acceptance_path") or "").casefold()
    }
    # The v33 delta also contains ordinary navigation and static images.  Only
    # rows explicitly bound to the root popup24 receipts are required to have
    # a popUpOmega source literal; ordinary/static rows are checked below by
    # their own reference classes.
    missing_popup = sorted(popup_expected - {row["original"] for row in popup_items})
    if missing_popup:
        raise RuntimeError("accepted v33 popup originals have no literal source reference: " + ", ".join(missing_popup))
    all_reference_rows = ref_sets["popup_full_image_links"] + ref_sets["ordinary_image_hrefs"] + ref_sets["static_render_targets"]
    news_reference_rows = ref_sets["popup_full_image_links"] + all_ref_sets["ordinary_image_hrefs"] + ref_sets["static_render_targets"]
    def first_page(predicate):
        return next((row["page_output"] for row in all_reference_rows if predicate(row)), None)
    screenshot_targets = [
        {"name": "news-august-v33.png", "page_output": first_page(lambda row: row["page_kind"] == "news" and "08" in row["page_route"]) or first_page(lambda row: row["page_kind"] == "news")},
        {"name": "popup-arena-v33.png", "page_output": first_page(lambda row: row["popup_full_image"] and "/arena" in row["page_route"])},
        {"name": "popup-silvermoon-v33.png", "page_output": first_page(lambda row: row["popup_full_image"] and "/silvermoon" in row["page_route"])},
        {"name": "guide-wallpaper-v33.png", "page_output": first_page(lambda row: row["page_kind"] in {"guide_or_content", "wallpaper"})},
    ]
    news_pages = sorted({row["page_output"] for row in news_reference_rows if row["page_kind"] == "news"})
    frozen_news_toggle_ids = {page: news_toggle_ids(page) for page in news_pages}
    browser_items: list[dict] = []
    for item, served in zip(items, output_items, strict=True):
        browser_items.append({
            "original": str(item["original"]),
            "role": str(item["_map_role"]),
            "actual_capture_timestamp": item.get("actual_timestamp"),
            "mime": item.get("mime"),
            "dimensions": item.get("dimensions"),
            "length": int(item["length"]),
            "sha256": str(item["sha256"]).casefold(),
            "map_source_path": str(item.get("local_path")),
            "served_route": served["route"],
            "served_output_path": served["output_path"],
            "served_url": served["static_url"],
            "served_sha256": served["output_sha256"],
            "served_length": served["output_length"],
            "origin_namespace": served["origin_namespace"],
            "source_acceptance_path": item.get("source_acceptance_path"),
            "public_copy_acceptance_path": item.get("public_copy_acceptance_path"),
        })
    frozen_browser_items = [
        {
            "original": str(item["original"]),
            "role": "frozen_v32_image_overlay",
            "actual_capture_timestamp": item.get("actual_capture_timestamp"),
            "mime": item.get("mime"),
            "dimensions": None,
            "length": int(item["length"]),
            "sha256": str(item["sha256"]).casefold(),
            "served_route": item["served_route"],
            "served_output_path": item["served_output_path"],
            "served_url": item["served_url"],
            "served_sha256": item["served_sha256"],
            "served_length": item["served_length"],
            "origin_namespace": item.get("origin_namespace"),
        }
        for item in validated_v32_items
    ]
    all_ordinary_by_original: dict[str, dict] = {}
    for row in all_ref_sets["ordinary_image_hrefs"]:
        all_ordinary_by_original.setdefault(str(row["original"]), row)
    all_ordinary_rows = list(all_ordinary_by_original.values())
    source_bindings = {"builder": binding(BUILDER), "primary_map": binding(PRIMARY_MAP), "supplement_map": binding(SUPPLEMENT_MAP), "impact": binding(IMPACT), "source_audit": binding(SOURCE_AUDIT), "preparation": binding(PREPARATION), "preflight": binding(PREFLIGHT), "source_receipts_manifest": binding(SOURCE_MANIFEST), "source15_manifest": binding(SOURCE15), "v32_provenance": binding(V32_PROVENANCE), "v33_provenance": binding(V33_PROVENANCE), "v32_browser_baseline": binding(V32_BROWSER, EXPECTED_V32_BROWSER_SHA256), "v32_controls_baseline": binding(V32_CONTROLS, EXPECTED_V32_CONTROLS_SHA256), "v32_content_baseline": binding(V32_CONTENT, EXPECTED_V32_CONTENT_SHA256), "v32_chart_baseline": binding(V32_CHART, EXPECTED_V32_CHART_SHA256), "popup_tool_acceptance": binding(ROOT_POPUP_TOOL), "navigation_tool_acceptance": binding(ROOT_NAVIGATION_TOOL), "retired_tool_acceptance": binding(ROOT_RETIRED_TOOL), "attunement_mask_tool_acceptance": binding(ROOT_MASK_TOOL), "exporter": binding(ROOT / "tools/export_github_pages.py"), "checker": binding(CHECKER)}
    return {
        "schema": "wow-recovery.integration.v33-browser-input.v1",
        "status": "prepared_waiting_root_v33_browser_go",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "network_requests": 0,
        "export_executed": False,
        "source_bindings": source_bindings,
        "output": {"path": rel(OUTPUT), "provenance": binding(V33_PROVENANCE), "base_path": BASE_PATH},
        "v32_baseline": {"browser_acceptance": source_bindings["v32_browser_baseline"], "controls": source_bindings["v32_controls_baseline"], "content": source_bindings["v32_content_baseline"], "chart": source_bindings["v32_chart_baseline"], "focused_tool_acceptance": [source_bindings["popup_tool_acceptance"], source_bindings["navigation_tool_acceptance"], source_bindings["retired_tool_acceptance"], source_bindings["attunement_mask_tool_acceptance"]], "rerun": False},
        "new_original_count": len(browser_items),
        "new_original_bytes": sum(int(row["length"]) for row in browser_items),
        "new_originals": browser_items,
        "validated_old_originals": frozen_browser_items,
        "source_references": {
            "popup_full_image_links": popup_items,
            "ordinary_image_hrefs": all_ordinary_rows,
            "new_ordinary_image_hrefs": ref_sets["ordinary_image_hrefs"],
            "static_render_targets": ref_sets["static_render_targets"],
            "all_matches": all_ref_sets["all_matches"],
        },
        "recovery_scope": recovery_scope(impact),
        "browser_plan": {
            "popup_full_image_links": {"required": len(popup_items), "activate_news_toggles": True, "pages": sorted({row["page_output"] for row in popup_items})},
            "ordinary_image_hrefs": {
                "required_unique_originals": len(all_ordinary_rows),
                "new_required_unique_originals": len({row["original"] for row in ref_sets["ordinary_image_hrefs"]}),
                "frozen_v32_required_unique_originals": len({row["original"] for row in all_ordinary_rows if row["original"] in {item["original"] for item in frozen_browser_items}}),
                "activate_news_toggles": True,
            },
            "static_render_targets": {"candidate_count": len(ref_sets["static_render_targets"]), "declaration_only_is_reported": True},
            "screenshot_targets": screenshot_targets,
            "news_toggle_ids": frozen_news_toggle_ids,
            "deadline_seconds": 480,
            "external_requests_allowed": False,
            "page_errors_allowed": False,
        },
        "accepted_root_gate_required": True,
    }


def write_once(path: Path, value: object) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite browser input: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args(argv)
    if not args.prepare:
        parser.error("browser preparer requires --prepare; it never runs Playwright")
    if INPUT.exists():
        raise RuntimeError(f"refusing existing browser input: {INPUT}")
    payload = build_input()
    write_once(INPUT, payload)
    print(json.dumps({"status": payload["status"], "input": rel(INPUT), "input_sha256": sha256_file(INPUT), "new_originals": payload["new_original_count"], "popup_links": payload["browser_plan"]["popup_full_image_links"]["required"], "network_requests": 0, "export_executed": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

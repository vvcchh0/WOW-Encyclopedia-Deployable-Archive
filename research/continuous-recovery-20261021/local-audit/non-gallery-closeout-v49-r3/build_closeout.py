from __future__ import annotations

import csv
import hashlib
import html
import json
import posixpath
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = "/WOW-Encyclopedia-Deployable-Archive"

INPUTS = [
    ("initial-browser", ROOT / "research/continuous-recovery-20261021/local-audit/browser/browser-audit-20261021.json", 10),
    ("phase2", ROOT / "research/continuous-recovery-20261021/local-audit/phase2/phase2-browser-receipt.json", 34),
    ("phase3", ROOT / "research/continuous-recovery-20261021/local-audit/phase3/phase3-browser-receipt.json", 14),
    ("phase4-v46", ROOT / "research/continuous-recovery-20261021/local-audit/phase4-v46/phase4-v46-browser-receipt.json", 55),
    ("encyclopedia-v48", ROOT / "research/continuous-recovery-20261021/local-audit/encyclopedia-v48/browser-receipt.json", 49),
    ("v49-completion", ROOT / "research/continuous-recovery-20261021/publication/root-v49-encyclopedia-completion.json", 3),
    ("v41-flash", ROOT / "research/continuous-recovery-20261021/publication/v41-browser-r2-result.json", 3),
    ("v42-blizzcast", ROOT / "research/continuous-recovery-20261021/publication/v42-browser-result.json", 5),
    ("v45-pages", ROOT / "research/continuous-recovery-20261021/publication/root-v45-browser-acceptance.json", 5),
    ("v46-talents", ROOT / "research/continuous-recovery-20261021/publication/root-v46-browser-acceptance.json", 9),
]
V46_TARGETS_PATH = ROOT / "research/continuous-recovery-20261021/publication/v46-talent-remaining-targets.json"
V41_ACCEPTANCE_PATH = ROOT / "research/continuous-recovery-20261021/publication/root-v41-browser-acceptance.json"
V42_ACCEPTANCE_PATH = ROOT / "research/continuous-recovery-20261021/publication/root-v42-browser-acceptance.json"
V45_ACCEPTANCE_PATH = ROOT / "research/continuous-recovery-20261021/publication/root-v45-browser-acceptance.json"
V46_ACCEPTANCE_PATH = ROOT / "research/continuous-recovery-20261021/publication/root-v46-browser-acceptance.json"
PROVENANCE_PATH = ROOT / ".scratch/pages-resources-20261021-v49/export-provenance.json"
ROUTE_MAP_PATH = ROOT / ".scratch/pages-resources-20261021-v49/__offline/route-map.json"
ROUTE_REVIEW_PATH = ROOT / "research/continuous-recovery-20261021/integration/available-resource-route-review/route-review.json"
CANDIDATE_V49_ROOT = ROOT / ".scratch/pages-resources-20261021-v49"
R2_SUMMARY_PATH = ROOT / "research/continuous-recovery-20261021/local-audit/non-gallery-closeout-v49-r2/summary.json"
T_GIF_TARGET = "/wrath/images/letters/T.gif"
T_GIF_SHA256 = "0a82046107b2f5a45b258143cd8f862030980507bad23190c54445b43b3a62ad"
T_GIF_LENGTH = 1419

KNOWN_V49_REPAIRS = {
    "/info/basics/factions/aldorscryers/images/button-horde.jpg",
    "/info/basics/factions/aldorscryers/images/button-alliance.jpg",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def route_review_evidence(route_review: dict):
    """Validate the two accepted local corrections used by this r3 receipt."""
    t = route_review.get("t_gif") or {}
    payload = t.get("payload") or {}
    evidence = t.get("evidence") or {}
    output_value = str(evidence.get("output_file") or "")
    output_path = ROOT / output_value.replace("/", "\\") if output_value else Path()
    t_checks = {
        "decision": t.get("decision"),
        "target_route": payload.get("source_route"),
        "output_path": output_value,
        "output_file": output_value,
        "output_file_exists": bool(output_path and output_path.is_file()),
        "output_file_length": output_path.stat().st_size if output_path.is_file() else None,
        "output_file_sha256": sha256_file(output_path) if output_path.is_file() else "",
        "expected_length": T_GIF_LENGTH,
        "expected_sha256": T_GIF_SHA256,
        "payload_length": payload.get("length"),
        "payload_sha256": payload.get("sha256"),
        "source_route": payload.get("source_route"),
        "output_route": payload.get("output_path"),
        "http_status": payload.get("http_status"),
        "content_valid": payload.get("content_valid"),
        "pillow_decode": payload.get("pillow_decode"),
    }
    t_checks["valid"] = bool(
        t_checks["decision"] == "propose_exact_single_slash_route_alias"
        and t_checks["target_route"] == "/wrath//images/letters/T.gif"
        and t_checks["output_file_exists"]
        and t_checks["output_file_length"] == T_GIF_LENGTH
        and t_checks["output_file_sha256"] == T_GIF_SHA256
        and t_checks["payload_length"] == T_GIF_LENGTH
        and t_checks["payload_sha256"] == T_GIF_SHA256
        and t_checks["content_valid"] is True
        and (t_checks["pillow_decode"] or {}).get("valid") is True
    )

    anomaly = route_review.get("community_anniversary_anomaly") or {}
    closeout = anomaly.get("closeout_record") or {}
    browser = anomaly.get("browser_evidence") or {}
    source_code = anomaly.get("source_code") or {}
    anomaly_checks = {
        "classification": anomaly.get("classification"),
        "confidence": anomaly.get("confidence"),
        "target_route": closeout.get("target_route"),
        "closeout_resolution": closeout.get("resolution"),
        "browser_receipt_path": browser.get("receipt_path"),
        "browser_receipt_sha256": browser.get("receipt_sha256"),
        "browser_row_index": browser.get("row_index"),
        "source_directory_statement": source_code.get("source_directory_statement"),
        "source_timeline_path": source_code.get("source_timeline_path"),
        "source_timeline_sha256": source_code.get("source_timeline_sha256"),
        "source_screenshot_path": source_code.get("source_screenshot_path"),
        "source_screenshot_sha256": source_code.get("source_screenshot_sha256"),
        "source_concat_line": source_code.get("source_concat_line"),
        "output_directory_statement": source_code.get("output_directory_statement"),
        "output_timeline_path": source_code.get("output_timeline_path"),
        "output_timeline_sha256": source_code.get("output_timeline_sha256"),
        "output_screenshot_path": source_code.get("output_screenshot_path"),
        "output_screenshot_sha256": source_code.get("output_screenshot_sha256"),
        "output_concat_line": source_code.get("output_concat_line"),
        "not_probe_concat": anomaly.get("not_probe_concat"),
        "exporter_transform": anomaly.get("exporter_transform"),
    }
    anomaly_checks["valid"] = bool(
        anomaly_checks["classification"] == "actual_export_transform_bug"
        and anomaly_checks["confidence"] == "high"
        and anomaly_checks["target_route"]
        and anomaly_checks["not_probe_concat"] is True
        and anomaly_checks["browser_receipt_path"]
        and anomaly_checks["source_directory_statement"]
        and anomaly_checks["output_directory_statement"]
    )
    return t_checks, anomaly_checks


def resolve_case_path(root: Path, relative: str):
    """Resolve a relative path and preserve the actual on-disk casing."""
    current = root
    relative = str(relative or "").replace("\\", "/").lstrip("/")
    if not relative:
        return current if current.exists() else None, "exact"
    case_parts = []
    for part in relative.split("/"):
        if not current.is_dir():
            return None, "not_found"
        try:
            children = list(current.iterdir())
        except OSError:
            return None, "not_found"
        exact = next((child for child in children if child.name == part), None)
        chosen = exact or next((child for child in children if child.name.casefold() == part.casefold()), None)
        if chosen is None:
            return None, "not_found"
        case_parts.append(chosen.name)
        current = chosen
    return current, ("exact" if case_parts == relative.split("/") else "case_insensitive")


def crosscheck_target_local(target: str, routes: dict, aliases: dict):
    """Cross-check a still-missing target against the v49 output tree only."""
    candidates = [target.lstrip("/")]
    for value in (routes.get(target), aliases.get(target)):
        if value:
            candidate = strip_base(str(value)).lstrip("/")
            if candidate not in candidates:
                candidates.append(candidate)
    checked = []
    found = []
    for relative in candidates:
        path, case_match = resolve_case_path(CANDIDATE_V49_ROOT, relative)
        entry = {"relative": relative, "case_match": case_match}
        if path is not None and path.is_file():
            entry.update({
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "placeholder": "__offline/missing" in str(path).replace("\\", "/").lower(),
            })
            found.append(entry)
        checked.append(entry)
    non_placeholder = [item for item in found if not item.get("placeholder")]
    if non_placeholder:
        status = "available_local_unmapped"
        actual = non_placeholder[0]
    elif found:
        status = "placeholder_only"
        actual = found[0]
    else:
        status = "not_found"
        actual = {}
    return {
        "target_route": target,
        "status": status,
        "candidate_count": len(candidates),
        "candidate_paths": ";".join(candidates),
        "actual_path": actual.get("path", ""),
        "actual_bytes": actual.get("bytes", ""),
        "actual_sha256": actual.get("sha256", ""),
        "actual_case_match": actual.get("case_match", ""),
        "checked": checked,
    }


def clean_path(value: str | None, page_route: str | None = None) -> str:
    """Convert a local/absolute/relative observation to a logical route."""
    if value is None:
        return ""
    text = html.unescape(str(value)).strip()
    if not text:
        return ""
    # A placeholder URL can contain an absolute loopback origin and a project prefix.
    sp = urlsplit(text)
    if sp.scheme or sp.netloc:
        path = sp.path
    elif text.startswith("//"):
        path = urlsplit("http:" + text).path
    else:
        path = text.split("#", 1)[0].split("?", 1)[0]
    path = unquote(path)
    if path.startswith(BASE + "/"):
        path = path[len(BASE):]
    elif path == BASE:
        path = "/"
    if not path.startswith("/"):
        base = page_route or "/"
        path = urlsplit(urljoin(base, path)).path
    path = posixpath.normpath(path or "/")
    return path if path.startswith("/") else "/" + path


def strip_base(value: str) -> str:
    value = value or ""
    if value.startswith(BASE + "/"):
        return value[len(BASE):]
    if value == BASE:
        return "/"
    return value if value.startswith("/") else "/" + value


def canonical_page(raw: str, routes: dict, aliases: dict) -> str:
    route = clean_path(raw)
    if not route:
        return ""
    route_keys = set(routes) | set(aliases)
    if route in route_keys:
        return route
    if route.endswith(".xml.html") and route[:-5] in route_keys:
        return route[:-5]
    # The v49 route map records logical route -> derived route. Map a local
    # .xml.html observation back to its logical source when possible.
    for key, value in list(routes.items()) + list(aliases.items()):
        if strip_base(value) == route:
            return key
    return route


def page_fields(source: str, record: dict, idx: int, routes: dict, aliases: dict):
    raw_route = record.get("route") or record.get("path") or record.get("output_path") or record.get("url") or ""
    route = canonical_page(raw_route, routes, aliases)
    status = record.get("status")
    outcome = record.get("outcome") or ""
    # Keep HTTP status and browser outcome in separate fields. In particular,
    # v46 uses outcome="checked" with accepted interaction states but records
    # no HTTP status; do not project that outcome into status.
    status_text = "" if status is None else str(status)
    title = str(record.get("title") or "")
    if not title and isinstance(record.get("content"), dict):
        title = str(record["content"].get("heading") or "")
    error_count = 0
    for key in ("page_errors", "pageerrors", "new_pageerrors", "failed_local_requests", "local_http_errors", "http_errors", "request_failures"):
        value = record.get(key)
        if isinstance(value, list):
            error_count += len(value)
    accepted_browser_evidence = bool(record.get("_accepted_browser_evidence"))
    # 200 with an explicit probe error is retained as an observation but not
    # treated as a successful completion until another receipt proves it.
    completed = accepted_browser_evidence or ((status == 200 or str(status) == "200") and outcome != "probe_error")
    if source == "phase3":
        completed = (status == 200 or str(status) == "200")
    excluded = page_scope_exclusion(route, record)
    return {
        "source": source,
        "record_index": idx,
        "receipt_ref": f"{source}#pages[{idx}]",
        "raw_route": str(raw_route),
        "canonical_route": route,
        "status": status_text,
        "outcome": str(outcome),
        "title": title,
        "error_count": error_count,
        "completed": completed,
        "completed_by_accepted_browser_evidence": accepted_browser_evidence,
        "completion_basis": "accepted_browser_evidence" if accepted_browser_evidence else ("status_200" if completed else ""),
        "excluded_reason": excluded,
        "exclusion_basis": prototype_exclusion_basis(record) if excluded == "prototype_intercept" else "",
    }


def page_scope_exclusion(route: str, record: dict | None = None) -> str:
    p = (route or "").lower()
    # Only explicit receipt fields can establish a prototype/intercept page.
    # A derived /__offline/ route (for example the accepted BlizzCast reader)
    # is a real local page and is retained.
    record = record or {}
    if any(record.get(key) is True for key in ("prototype", "intercepted", "prototype_intercept", "is_intercept")):
        return "prototype_intercept"
    if str(record.get("source_kind") or record.get("page_kind") or "").lower() in {"prototype", "intercept", "prototype_intercept"}:
        return "prototype_intercept"
    if "/gallery/" in p or p.startswith("/gallery/") or "/player-gallery/" in p:
        return "gallery"
    if "/media/" in p or "/screenshots/" in p or "/screenshot/" in p or "/ssotd/" in p:
        return "media_screenshot_ssotd"
    return ""


def prototype_exclusion_basis(record: dict | None = None) -> str:
    """Return the receipt fields that explicitly establish an intercept."""
    record = record or {}
    fields = [
        key for key in ("prototype", "intercepted", "prototype_intercept", "is_intercept")
        if record.get(key) is True
    ]
    kind = str(record.get("source_kind") or record.get("page_kind") or "").lower()
    if kind in {"prototype", "intercept", "prototype_intercept"}:
        fields.append("source_kind" if record.get("source_kind") else "page_kind")
    return ";".join(fields)


def marker_from_text(text: str, page_route: str, marker_class: str, source: str, idx: int):
    text = html.unescape(str(text))
    if "missing-image.svg" not in text.lower():
        return None
    m = re.search(r"(?:[?&])requested=([^&\"' )<>]+)", text, flags=re.I)
    requested = unquote(html.unescape(m.group(1))) if m else ""
    target = clean_path(requested, page_route) if requested else ""
    if not target:
        # Do not treat the placeholder itself as its missing target.
        return None
    return {
        "source": source,
        "record_index": idx,
        "page_route": page_route,
        "marker_class": marker_class,
        "requested": requested,
        "target_route": target,
        "evidence": "missing-image.svg",
    }


def marker_from_dict(item: dict, page_route: str, marker_class: str, source: str, idx: int):
    requested = item.get("requested")
    src = item.get("src") or item.get("background_image") or item.get("url") or ""
    if requested is None and src:
        m = re.search(r"(?:[?&])requested=([^&\"' )<>]+)", html.unescape(str(src)), flags=re.I)
        requested = unquote(html.unescape(m.group(1))) if m else ""
    requested = "" if requested is None else str(requested)
    target = clean_path(requested, page_route) if requested else ""
    if not target:
        return None
    return {
        "source": source,
        "record_index": idx,
        "page_route": page_route,
        "marker_class": marker_class,
        "requested": requested,
        "target_route": target,
        "evidence": "structured-placeholder",
    }


def walk_placeholder_strings(value, path=""):
    if isinstance(value, dict):
        for key, child in value.items():
            # Content and source excerpts can contain literal examples from the
            # page and are not browser observations.
            if key in {"content", "body_text", "body_excerpt", "source"}:
                continue
            yield from walk_placeholder_strings(child, path + "." + key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk_placeholder_strings(child, path + f"[{i}]")
    elif isinstance(value, str) and "missing-image.svg" in value.lower():
        yield value, path


def extract_markers(source: str, record: dict, page: dict) -> list[dict]:
    page_route = page["canonical_route"]
    out: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def add(item):
        if not item:
            return
        key = (item["marker_class"], item["target_route"])
        if key in seen:
            return
        seen.add(key)
        out.append(item)

    if source == "phase2":
        dom = record.get("dom") or {}
        for item in dom.get("missing_images") or []:
            add(marker_from_dict(item, page_route, "static_marker", source, page["record_index"]))
        for item in dom.get("css_background_placeholders") or []:
            add(marker_from_dict(item, page_route, "css_marker", source, page["record_index"]))
    elif source == "phase3":
        # Prefer the final state. Before/after duplicated placeholders are a
        # single page observation, not independent image failures.
        preferred = [k for k in record if k.startswith("after") or k in {"dom_after"}]
        preferred += [k for k in record if k.startswith("before") or k in {"dom_before"}]
        for key in preferred:
            value = record.get(key)
            if not isinstance(value, (dict, list)):
                continue
            for text, path in walk_placeholder_strings(value, key):
                marker_class = "css_marker" if any(token in path.lower() for token in ("style", "background", "css")) else "static_marker"
                add(marker_from_text(text, page_route, marker_class, source, page["record_index"]))
    elif source == "phase4-v46":
        for item in record.get("missing_placeholders") or []:
            add(marker_from_dict(item, page_route, "static_marker", source, page["record_index"]))
        for item in record.get("css_background_placeholders") or []:
            add(marker_from_dict(item, page_route, "css_marker", source, page["record_index"]))
    elif source == "encyclopedia-v48":
        for item in record.get("img_placeholder_markers") or []:
            add(marker_from_dict(item, page_route, "static_marker", source, page["record_index"]))
        for item in record.get("css_placeholder_markers") or []:
            add(marker_from_dict(item, page_route, "css_marker", source, page["record_index"]))

    # A 200 image placeholder is intentionally separate from a missing marker;
    # it is never counted as a recovered image.
    for item in record.get("images") or []:
        if item.get("placeholder") is True:
            marker = marker_from_dict(item, page_route, "placeholder_200", source, page["record_index"])
            if marker:
                add(marker)

    # Exact 404s are only collected from structured local-request errors.
    for key in ("local_http_errors", "failed_local_requests", "http_errors", "request_failures"):
        for item in record.get(key) or []:
            if not isinstance(item, dict):
                continue
            status = item.get("status") or item.get("status_code") or item.get("http_status")
            if str(status) != "404":
                continue
            url = item.get("url") or item.get("request") or item.get("target") or ""
            target = clean_path(str(url), page_route)
            if target:
                key2 = ("http404", target)
                if key2 not in seen:
                    seen.add(key2)
                    out.append({
                        "source": source,
                        "record_index": page["record_index"],
                        "page_route": page_route,
                        "marker_class": "http404",
                        "requested": str(url),
                        "target_route": target,
                        "evidence": "local-http-404",
                    })
    return out


def source_records(source: str, data: dict):
    if source in {"initial-browser", "phase2", "phase4-v46", "encyclopedia-v48", "v49-completion"}:
        return data.get("pages") or []
    if source == "phase3":
        return data.get("rows") or []
    if source == "v41-flash":
        return data.get("rows") or []
    if source == "v42-blizzcast":
        return [
            {
                "route": f"/__offline/related-sites/blizzcast/{item.get('name', 'unknown')}.html",
                "status": item.get("status"),
                "title": f"BlizzCast {item.get('name', 'unknown')}",
                "outcome": "checked",
                "late_supplement": item.get("late_supplement"),
                "blocks": item.get("blocks"),
                "accepted_reader": True,
            }
            for item in (data.get("readers") or [])
        ]
    if source == "v45-pages":
        out = []
        for item in data.get("pages") or []:
            copied = dict(item)
            # The accepted receipt explicitly validates browser behaviour for
            # the contest page even though that page has no HTTP status field.
            if data.get("accepted") is True:
                copied["_accepted_browser_evidence"] = True
            out.append(copied)
        return out
    if source == "v46-talents":
        # v46 acceptance stores the nine actual browser pages by class name;
        # the accepted v42 template paths establish the exact route convention.
        out = []
        for item in data.get("pages") or []:
            copied = dict(item)
            class_name = str(item.get("class_name") or "").strip().lower()
            copied["route"] = f"/info/classes/{class_name}/talents.html" if class_name else ""
            copied["title"] = f"{class_name.title()} Talent Calculator" if class_name else ""
            copied["outcome"] = "checked"
            # v46 records accepted initial/interaction/reset states rather than
            # an HTTP status. Preserve the absent status; this is browser
            # acceptance evidence, not an invented 200.
            if data.get("accepted") is True and isinstance(item.get("states"), dict) and item.get("states"):
                copied["_accepted_browser_evidence"] = True
            out.append(copied)
        return out
    return []


def scope_for_target(target: str, page_route: str) -> str:
    target_value = (target or "").lower()
    page_value = (page_route or "").lower()
    # News screenshots are ordinary article illustrations and remain in scope.
    if "/gallery/" in target_value or target_value.startswith("/gallery/") or "/player-gallery/" in target_value:
        return "gallery"
    if target_value.startswith("/news/"):
        return ""
    if "/media/" in target_value or "/screenshots/" in target_value or "/screenshot/" in target_value or "/ssotd/" in target_value:
        return "media_screenshot_ssotd"
    return ""


def v49_evidence(target: str, routes: dict, aliases: dict, provenance: dict):
    if BASE.lower() in target.lower() or "prototype" in target.lower():
        return "url_uncertain", "ambiguous_project_prefix_or_intercept_target"
    if target in KNOWN_V49_REPAIRS:
        return "supplemented_v49", "known_v49_aldor_button_repair"
    value = routes.get(target) or aliases.get(target)
    if value:
        local = strip_base(value)
        if "/__offline/missing-image.svg" not in local and "/__offline/missing.html" not in local:
            # Prefer explicit provenance classifications below.
            related = provenance.get("related_encyclopedia_images") or {}
            if target in (related.get("route_reuses") or {}):
                return "supplemented_v49", "related_encyclopedia_image"
            related = provenance.get("related_guide_images") or {}
            if target in (related.get("route_reuses") or {}):
                return "supplemented_v49", "related_guide_image_or_display_mapping"
            for group in ("talent_box_layout_compatibility", "layout_compatibility_reuse"):
                records = (provenance.get(group) or {}).get("records") or []
                if any(r.get("target_route") == target for r in records):
                    return "supplemented_v49", "layout_compatibility_reuse"
            return "supplemented_v49", "route_map_to_v49_asset"
    if not target:
        return "url_uncertain", "missing_requested_url"
    return "still_missing_local", "no_v49_route_or_provenance"


def csv_write(path: Path, rows: list[dict], fields: list[str]):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    route_data = read_json(ROUTE_MAP_PATH)
    routes = route_data.get("routes") or {}
    aliases = route_data.get("aliases") or {}
    provenance = read_json(PROVENANCE_PATH)
    route_review = read_json(ROUTE_REVIEW_PATH)
    t_gif_evidence, anniversary_evidence = route_review_evidence(route_review)
    anniversary_target = anniversary_evidence.get("target_route") or ""
    r2_summary = read_json(R2_SUMMARY_PATH)

    page_observations: list[dict] = []
    marker_observations: list[dict] = []
    input_receipts = []
    for source, path, claimed in INPUTS:
        data = read_json(path)
        recs = source_records(source, data)
        input_receipts.append({
            "label": source,
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
            "claimed_page_count": claimed,
            "receipt_record_count": len(recs),
        })
        for idx, record in enumerate(recs):
            page = page_fields(source, record, idx, routes, aliases)
            page_observations.append(page)
            marker_observations.extend(extract_markers(source, record, page))

    # This is an accepted v46 observation list, not a new browser pass. Keep
    # every path as an independent target evidence record; it is deliberately
    # not assigned static/CSS/HTTP404 marker counts.
    v46_target_manifest = read_json(V46_TARGETS_PATH)
    v46_target_paths = v46_target_manifest.get("paths") or []
    input_receipts.append({
        "label": "v46-talent-targets",
        "path": str(V46_TARGETS_PATH.relative_to(ROOT)),
        "sha256": sha256_file(V46_TARGETS_PATH),
        "claimed_page_count": 0,
        "receipt_record_count": len(v46_target_paths),
    })
    for idx, target in enumerate(v46_target_paths):
        marker_observations.append({
            "source": "v46-talent-targets",
            "record_index": idx,
            "page_route": "/info/classes/*/talents.html (nine accepted v46 DOMs)",
            "marker_class": "accepted_target_list",
            "requested": str(target),
            "target_route": clean_path(str(target)),
            "evidence": "accepted-v46-target-manifest",
        })

    # Completion records have no marker fields, but still form a real page
    # observation and resolve the v48 probe errors for these three routes.
    grouped = defaultdict(list)
    for page in page_observations:
        if page["canonical_route"]:
            grouped[page["canonical_route"]].append(page)

    coverage_rows = []
    excluded_routes = {}
    for route, observations in sorted(grouped.items()):
        excluded = Counter(o["excluded_reason"] for o in observations if o["excluded_reason"])
        if excluded:
            excluded_routes[route] = dict(excluded)
            # Keep the canonical page table scoped to the non-gallery audit.
            continue
        completed = [o for o in observations if o["completed"]]
        coverage_rows.append({
            "canonical_route": route,
            "title": next((o["title"] for o in observations if o["title"]), ""),
            "observation_count": len(observations),
            "completed_observation_count": len(completed),
            "first_source": observations[0]["source"],
            "source_rounds": ";".join(sorted({o["source"] for o in observations})),
            "status_values": ";".join(sorted({o["status"] for o in observations if o["status"]})),
            "outcome_values": ";".join(sorted({o["outcome"] for o in observations if o["outcome"]})),
            "page_errors_observed": sum(o["error_count"] for o in observations),
            "completed_in_v49_audit": "yes" if completed else "no",
            "completed_by_accepted_browser_evidence": "yes" if any(o.get("completed_by_accepted_browser_evidence") for o in observations) else "no",
            "accepted_browser_evidence_observation_count": sum(1 for o in observations if o.get("completed_by_accepted_browser_evidence")),
            "completion_basis_values": ";".join(sorted({o["completion_basis"] for o in observations if o["completion_basis"]})),
            "receipt_refs": ";".join(o["receipt_ref"] for o in observations),
        })

    # Carry an explicit page-level exclusion into marker evidence.  A local
    # /__offline/ path is not itself an exclusion: only the receipt fields
    # inspected by page_scope_exclusion may establish a prototype/intercept.
    page_index = {(p["source"], p["record_index"]): p for p in page_observations}
    target_groups = defaultdict(list)
    for marker in marker_observations:
        page = page_index.get((marker["source"], marker["record_index"]))
        marker["scope_exclusion"] = (page or {}).get("excluded_reason") or scope_for_target(
            marker["target_route"], marker["page_route"]
        )
        marker["resolution"], marker["resolution_reason"] = v49_evidence(
            marker["target_route"], routes, aliases, provenance
        )
        if marker["target_route"] == T_GIF_TARGET and t_gif_evidence.get("valid"):
            marker["resolution"] = "local_file_available_unrouted"
            marker["resolution_reason"] = "exact_v50_output_file_verified_but_v49_route_unmapped"
        elif marker["target_route"] == anniversary_target and anniversary_evidence.get("valid"):
            marker["resolution"] = "malformed_generated_navigation"
            marker["resolution_reason"] = "accepted_route_review_actual_export_transform_bug"
        target_groups[marker["target_route"]].append(marker)

    remaining_rows = []
    available_unrouted_rows = []
    malformed_navigation_rows = []
    target_stats = {}
    excluded_target_counts = Counter()
    excluded_target_routes = defaultdict(set)
    for target, markers in sorted(target_groups.items()):
        scope_exclusions = Counter(m["scope_exclusion"] for m in markers if m["scope_exclusion"])
        if scope_exclusions:
            for k, v in scope_exclusions.items():
                excluded_target_counts[k] += v
                excluded_target_routes[k].add(target)
            continue
        # Aldor buttons are deliberately excluded from remaining targets: v49
        # explicitly repaired both observed 404s.
        if target in KNOWN_V49_REPAIRS:
            excluded_target_counts["known_v49_repairs"] += len(markers)
            excluded_target_routes["known_v49_repairs"].add(target)
            continue
        classes = Counter(m["marker_class"] for m in markers)
        base_resolution = markers[0]["resolution"]
        base_reason = markers[0]["resolution_reason"]
        definite_classes = {"static_marker", "css_marker", "http404", "accepted_target_list"}
        if base_resolution in {"local_file_available_unrouted", "malformed_generated_navigation"}:
            resolution = base_resolution
            reason = base_reason
        elif base_resolution == "url_uncertain":
            resolution = "url_uncertain"
            reason = base_reason
        elif base_resolution == "supplemented_v49":
            resolution = "supplemented_v49"
            reason = base_reason
        elif any(classes.get(name, 0) for name in definite_classes):
            resolution = "still_missing_local"
            reason = "definite_missing_marker_without_v49_entity"
        elif classes.get("placeholder_200", 0):
            resolution = "unknown_200_placeholder"
            reason = "only_200_placeholder_observation_without_requested_entity"
        else:
            resolution = "still_missing_local"
            reason = "missing_marker_without_v49_entity"
        for marker in markers:
            marker["resolution"] = resolution
            marker["resolution_reason"] = reason
            marker["target_resolution"] = resolution
        classes = Counter(m["marker_class"] for m in markers)
        requested = sorted({m["requested"] for m in markers if m["requested"]})
        pages = sorted({m["page_route"] for m in markers})
        sources = sorted({m["source"] for m in markers})
        special_row = {
            "target_route": target,
            "resolution": resolution,
            "resolution_reason": reason,
            "marker_occurrences": len(markers),
            "static_marker_count": classes.get("static_marker", 0),
            "css_marker_count": classes.get("css_marker", 0),
            "http404_count": classes.get("http404", 0),
            "placeholder_200_count": classes.get("placeholder_200", 0),
            "accepted_target_list_count": classes.get("accepted_target_list", 0),
            "source_rounds": ";".join(sources),
            "page_routes": ";".join(pages),
            "observed_requested_values": " || ".join(requested),
            "evidence_types": ";".join(sorted(classes)),
            "receipt_refs": ";".join(f"{m['source']}#pages[{m['record_index']}]" for m in markers),
        }
        if resolution == "local_file_available_unrouted":
            special_row.update({
                "actual_file_path": t_gif_evidence.get("output_file", ""),
                "actual_file_sha256": t_gif_evidence.get("output_file_sha256", ""),
                "actual_file_bytes": t_gif_evidence.get("output_file_length", ""),
                "route_review_path": str(ROUTE_REVIEW_PATH.relative_to(ROOT)),
                "route_review_sha256": sha256_file(ROUTE_REVIEW_PATH),
                "source_route": t_gif_evidence.get("source_route", ""),
                "output_route": t_gif_evidence.get("output_route", ""),
                "source_capture_timestamp": (route_review.get("t_gif", {}).get("payload", {}) or {}).get("actual_timestamp", ""),
                "verification": "sha256_length_and_pillow_decode_verified",
            })
            available_unrouted_rows.append(special_row)
            continue
        if resolution == "malformed_generated_navigation":
            special_row.update({
                "route_review_path": str(ROUTE_REVIEW_PATH.relative_to(ROOT)),
                "route_review_sha256": sha256_file(ROUTE_REVIEW_PATH),
                "classification": anniversary_evidence.get("classification", ""),
                "confidence": anniversary_evidence.get("confidence", ""),
                "browser_receipt_path": anniversary_evidence.get("browser_receipt_path", ""),
                "browser_receipt_sha256": anniversary_evidence.get("browser_receipt_sha256", ""),
                "browser_row_index": anniversary_evidence.get("browser_row_index", ""),
                "not_probe_concat": anniversary_evidence.get("not_probe_concat", ""),
                "source_timeline_path": anniversary_evidence.get("source_timeline_path", ""),
                "source_timeline_sha256": anniversary_evidence.get("source_timeline_sha256", ""),
                "source_directory_statement": anniversary_evidence.get("source_directory_statement", ""),
                "source_screenshot_path": anniversary_evidence.get("source_screenshot_path", ""),
                "source_screenshot_sha256": anniversary_evidence.get("source_screenshot_sha256", ""),
                "source_concat_line": anniversary_evidence.get("source_concat_line", ""),
                "output_timeline_path": anniversary_evidence.get("output_timeline_path", ""),
                "output_timeline_sha256": anniversary_evidence.get("output_timeline_sha256", ""),
                "output_directory_statement": anniversary_evidence.get("output_directory_statement", ""),
                "output_screenshot_path": anniversary_evidence.get("output_screenshot_path", ""),
                "output_screenshot_sha256": anniversary_evidence.get("output_screenshot_sha256", ""),
                "output_concat_line": anniversary_evidence.get("output_concat_line", ""),
                "verification": "accepted_route_review_transform_bug_evidence",
            })
            malformed_navigation_rows.append(special_row)
            continue
        if resolution not in {"still_missing_local", "url_uncertain", "unknown_200_placeholder"}:
            continue
        row = {
            "target_route": target,
            "resolution": resolution,
            "resolution_reason": reason,
            "marker_occurrences": len(markers),
            "static_marker_count": classes.get("static_marker", 0),
            "css_marker_count": classes.get("css_marker", 0),
            "http404_count": classes.get("http404", 0),
            "placeholder_200_count": classes.get("placeholder_200", 0),
            "accepted_target_list_count": classes.get("accepted_target_list", 0),
            "source_rounds": ";".join(sources),
            "page_routes": ";".join(pages),
            "observed_requested_values": " || ".join(requested),
            "evidence_types": ";".join(sorted(classes)),
            "receipt_refs": ";".join(f"{m['source']}#pages[{m['record_index']}]" for m in markers),
        }
        remaining_rows.append(row)
        target_stats[target] = row

    crosscheck_rows = []
    for row in remaining_rows:
        check = crosscheck_target_local(row["target_route"], routes, aliases)
        row["local_crosscheck_status"] = check["status"]
        row["local_crosscheck_candidate_paths"] = check["candidate_paths"]
        row["local_crosscheck_actual_path"] = check["actual_path"]
        row["local_crosscheck_actual_bytes"] = check["actual_bytes"]
        row["local_crosscheck_actual_sha256"] = check["actual_sha256"]
        row["local_crosscheck_case_match"] = check["actual_case_match"]
        crosscheck_rows.append({k: v for k, v in check.items() if k != "checked"})

    crosscheck_status_counts = Counter(row["status"] for row in crosscheck_rows)
    accepted_evidence_only_routes = [
        row["canonical_route"]
        for row in coverage_rows
        if row.get("completed_by_accepted_browser_evidence") == "yes"
        and "200" not in {value for value in row.get("status_values", "").split(";") if value}
    ]

    # Count all marker observations, including excluded and repaired targets,
    # while keeping the output list limited to unresolved in-scope targets.
    marker_counts = Counter(m["marker_class"] for m in marker_observations)
    resolution_counts = Counter(m["resolution"] for m in marker_observations)
    unique_resolution_counts = Counter()
    for target, markers in target_groups.items():
        if any(m["scope_exclusion"] for m in markers) or target in KNOWN_V49_REPAIRS:
            continue
        state = markers[0]["resolution"]
        unique_resolution_counts[state] += 1

    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    summary = {
        "schema": "wow-continuous-recovery-non-gallery-closeout-v49-r3-v1",
        "generated_at_utc": generated,
        "audit_version": "v49-r3",
        "scope": "Deduplicated local browser observations, accepted v41/v42/v45/v46 browser receipts, the accepted v46 target manifest, v49 route/provenance metadata, and the accepted local route-review corrections; no network and no dynamic-state scan.",
        "inputs": input_receipts,
        "additional_acceptance_inputs": [
            {
                "label": label,
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
            }
            for label, path in (
                ("v41-browser-acceptance", V41_ACCEPTANCE_PATH),
                ("v42-browser-acceptance", V42_ACCEPTANCE_PATH),
                ("v45-browser-acceptance", V45_ACCEPTANCE_PATH),
                ("v46-browser-acceptance", V46_ACCEPTANCE_PATH),
            )
        ],
        "coverage": {
            "receipt_record_total": len(page_observations),
            "canonical_route_total_in_scope": len(coverage_rows),
            "canonical_route_total_all_observed": len(grouped),
            "duplicate_observation_count": len(page_observations) - len(grouped),
            "completed_route_count": sum(1 for row in coverage_rows if row["completed_in_v49_audit"] == "yes"),
            "routes_with_only_probe_or_error": sum(1 for row in coverage_rows if row["completed_in_v49_audit"] == "no"),
            "completed_by_accepted_browser_evidence_route_count": sum(1 for row in coverage_rows if row.get("completed_by_accepted_browser_evidence") == "yes"),
            "routes_completed_only_by_accepted_browser_evidence_count": len(accepted_evidence_only_routes),
            "routes_completed_only_by_accepted_browser_evidence": accepted_evidence_only_routes,
            "excluded_page_route_count": len(excluded_routes),
            "excluded_page_routes": excluded_routes,
            "excluded_page_evidence": [
                {
                    "receipt_ref": p["receipt_ref"],
                    "canonical_route": p["canonical_route"],
                    "excluded_reason": p["excluded_reason"],
                    "explicit_receipt_fields": p.get("exclusion_basis", ""),
                }
                for p in page_observations
                if p.get("excluded_reason")
            ],
            "requested_initial_page_count": 10,
            "initial_receipt_actual_page_count": input_receipts[0]["receipt_record_count"],
            "initial_receipt_count_discrepancy": "requested 10, final receipt contains 7; no unrecorded pages inferred",
            "accepted_v41_flash_page_count": 3,
            "accepted_v42_blizzcast_reader_page_count": 5,
            "accepted_v45_page_count": 5,
            "accepted_v46_talent_page_count": 9,
            "accepted_v46_missing_target_count": len(v46_target_paths),
            "http_status_not_recorded_for_accepted_evidence": sum(
                1 for page in page_observations
                if page.get("completed_by_accepted_browser_evidence") and not page.get("status")
            ),
        },
        "missing_resource_observations": {
            "marker_occurrence_total": len(marker_observations),
            "static_marker_count": marker_counts.get("static_marker", 0),
            "css_marker_count": marker_counts.get("css_marker", 0),
            "http404_count": marker_counts.get("http404", 0),
            "placeholder_200_count": marker_counts.get("placeholder_200", 0),
            "unique_target_route_total": len(target_groups),
            "resolution_observation_counts": dict(resolution_counts),
            "unique_target_resolution_counts": {
                key: unique_resolution_counts.get(key, 0)
                for key in (
                    "supplemented_v49", "still_missing_local", "unknown_200_placeholder", "url_uncertain",
                    "local_file_available_unrouted", "malformed_generated_navigation",
                )
            },
            "unresolved_in_scope_target_count": len(remaining_rows),
            "target_count_before_special_corrections": len(target_groups),
            "available_unrouted_count": len(available_unrouted_rows),
            "available_unrouted_targets": [row["target_route"] for row in available_unrouted_rows],
            "malformed_generated_navigation_count": len(malformed_navigation_rows),
            "malformed_generated_navigation_targets": [row["target_route"] for row in malformed_navigation_rows],
            "remaining_target_count_before_special_corrections": len(remaining_rows) + len(available_unrouted_rows) + len(malformed_navigation_rows),
            "filesystem_crosscheck": {
                "candidate_root": str(CANDIDATE_V49_ROOT.relative_to(ROOT)),
                "still_missing_target_count_checked": len(crosscheck_rows),
                "status_counts": dict(crosscheck_status_counts),
                "local_files_found_for_still_missing": sum(1 for row in crosscheck_rows if row["status"] == "available_local_unmapped"),
                "case_insensitive_matches_for_still_missing": sum(1 for row in crosscheck_rows if row.get("actual_case_match") == "case_insensitive"),
                "placeholder_only_matches": sum(1 for row in crosscheck_rows if row["status"] == "placeholder_only"),
                "not_found_count": sum(1 for row in crosscheck_rows if row["status"] == "not_found"),
            },
            "excluded_target_observation_counts": dict(excluded_target_counts),
            "excluded_target_routes": {key: sorted(values) for key, values in sorted(excluded_target_routes.items())},
        },
        "known_v49_repairs": {
            "aldor_button_404_targets_excluded": sorted(KNOWN_V49_REPAIRS),
            "aldor_button_repair_count": 2,
            "reason": "v49 provenance/route-map confirms these two phase4 404 observations were repaired; they are excluded from remaining-targets.csv.",
        },
        "v49_bindings": {
            "provenance_path": str(PROVENANCE_PATH.relative_to(ROOT)),
            "provenance_sha256": sha256_file(PROVENANCE_PATH),
            "route_map_path": str(ROUTE_MAP_PATH.relative_to(ROOT)),
            "route_map_sha256": sha256_file(ROUTE_MAP_PATH),
        },
        "route_review_corrections": {
            "path": str(ROUTE_REVIEW_PATH.relative_to(ROOT)),
            "sha256": sha256_file(ROUTE_REVIEW_PATH),
            "t_gif": t_gif_evidence,
            "anniversary": anniversary_evidence,
            "baseline_note": "The route review is used as local evidence for v49 closeout corrections; this receipt does not claim v51 publication.",
        },
        "r2_baseline_comparison": {
            "r2_summary_path": str(R2_SUMMARY_PATH.relative_to(ROOT)),
            "r2_summary_sha256": sha256_file(R2_SUMMARY_PATH),
            "r2_completed_route_count": (r2_summary.get("coverage") or {}).get("completed_route_count"),
            "r3_completed_route_count": (len([row for row in coverage_rows if row["completed_in_v49_audit"] == "yes"])),
            "r2_routes_with_only_probe_or_error": (r2_summary.get("coverage") or {}).get("routes_with_only_probe_or_error"),
            "r3_routes_with_only_probe_or_error": sum(1 for row in coverage_rows if row["completed_in_v49_audit"] == "no"),
            "r2_unresolved_in_scope_target_count": (r2_summary.get("missing_resource_observations") or {}).get("unresolved_in_scope_target_count"),
            "r3_unresolved_in_scope_target_count": len(remaining_rows),
            "r2_unique_target_resolution_counts": (r2_summary.get("missing_resource_observations") or {}).get("unique_target_resolution_counts"),
            "r3_unique_target_resolution_counts": {
                key: unique_resolution_counts.get(key, 0)
                for key in (
                    "supplemented_v49", "still_missing_local", "unknown_200_placeholder", "url_uncertain",
                    "local_file_available_unrouted", "malformed_generated_navigation",
                )
            },
            "correction_effect": "six previously probe/error-only routes are completed_by_accepted_browser_evidence; one T.gif is local_file_available_unrouted; one anniversary malformed navigation is separated; news screenshot01/02 remain still_missing_local.",
        },
        "verification": {
            "method": [
                "Loaded the six named local audit receipts, accepted v41/v42/v45/v46 browser receipts, the accepted v46 target manifest, and v49 export-provenance/route-map.",
                "Canonicalized .xml/.xml.html observations using the v49 route-map, then grouped exact logical routes.",
                "Extracted structured missing-image/CSS markers and exact local HTTP 404s; did not inspect or copy raw HTML, cookies, headers, or large DOM fields.",
                "Counted 200 placeholder observations separately and never treated them as recovered images.",
                "Excluded only gallery, Media/screenshot/SSOTD, and receipt-explicit prototype/intercept observations plus the two known v49 Aldor repairs; news/images screenshot targets remain in scope.",
                "Counted v45 contest and v46 accepted talent state observations as completed_by_accepted_browser_evidence while preserving blank HTTP status fields.",
                "Classified the accepted T.gif route-review evidence as local_file_available_unrouted and the anniversary route-review evidence as malformed_generated_navigation; neither is presented as a new network recovery.",
                "Cross-checked every remaining still_missing_local target against the case-preserving v49 output tree and recorded status, path, bytes, and SHA when an entity was found.",
            ],
            "network_requests": 0,
            "raw_payloads_exported": False,
            "dynamic_state_scan": False,
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    csv_write(OUT / "page-coverage.csv", coverage_rows, [
        "canonical_route", "title", "observation_count", "completed_observation_count", "first_source",
        "source_rounds", "status_values", "outcome_values", "page_errors_observed", "completed_in_v49_audit",
        "completed_by_accepted_browser_evidence", "accepted_browser_evidence_observation_count", "completion_basis_values", "receipt_refs",
    ])
    csv_write(OUT / "remaining-targets.csv", remaining_rows, [
        "target_route", "resolution", "resolution_reason", "marker_occurrences", "static_marker_count", "css_marker_count",
        "http404_count", "placeholder_200_count", "accepted_target_list_count", "source_rounds", "page_routes", "observed_requested_values",
        "evidence_types", "receipt_refs", "local_crosscheck_status", "local_crosscheck_candidate_paths",
        "local_crosscheck_actual_path", "local_crosscheck_actual_bytes", "local_crosscheck_actual_sha256", "local_crosscheck_case_match",
    ])
    csv_write(OUT / "available-unrouted.csv", available_unrouted_rows, [
        "target_route", "resolution", "resolution_reason", "marker_occurrences", "source_rounds", "page_routes",
        "observed_requested_values", "receipt_refs", "actual_file_path", "actual_file_sha256", "actual_file_bytes",
        "route_review_path", "route_review_sha256", "source_route", "output_route", "source_capture_timestamp", "verification",
    ])
    csv_write(OUT / "malformed-navigation.csv", malformed_navigation_rows, [
        "target_route", "resolution", "resolution_reason", "marker_occurrences", "source_rounds", "page_routes",
        "observed_requested_values", "receipt_refs", "route_review_path", "route_review_sha256", "classification", "confidence",
        "browser_receipt_path", "browser_receipt_sha256", "browser_row_index", "not_probe_concat",
        "source_timeline_path", "source_timeline_sha256", "source_directory_statement", "source_screenshot_path",
        "source_screenshot_sha256", "source_concat_line", "output_timeline_path", "output_timeline_sha256",
        "output_directory_statement", "output_screenshot_path", "output_screenshot_sha256", "output_concat_line", "verification",
    ])
    csv_write(OUT / "filesystem-crosscheck.csv", crosscheck_rows, [
        "target_route", "status", "candidate_count", "candidate_paths", "actual_path", "actual_bytes", "actual_sha256", "actual_case_match",
    ])

    readme = f"""# Non-gallery closeout v49-r3

Generated `{generated}` from the local audit receipts, accepted v41/v42/v45/v46
browser receipts, the independently accepted v46 259-path target manifest, the
v49 route/provenance files, and the accepted local route-review correction. This
records observed local states and accepted missing-target observations; it is not
a site-wide crawl or a claim about unobserved dynamic states.

The final initial-browser receipt contains **7** page records although the
requested batch was described as 10 pages. The closeout keeps the seven real
records and records the discrepancy in `summary.json`; it does not invent
three pages.

`page-coverage.csv` contains one row per canonical non-gallery route after
deduplicating exact logical routes and `.xml`/`.xml.html` aliases. The accepted
v41 Flash pages, v42 five-page BlizzCast reader, v45 topic pages, and v46 nine
class pages are retained with their receipt references. The v45 contest page and
v46 talent pages whose HTTP status was not recorded are marked
`completed_by_accepted_browser_evidence` from their accepted browser receipts;
their blank status fields remain blank and no HTTP 200 is invented.

News illustrations such as `/news/images/06-10/screenshot01.jpg` and
`screenshot02.jpg` remain in scope. Exclusions use path segments for the known
player gallery and Media/screenshot/SSOTD collections. Prototype/intercept
exclusion is applied only when a receipt explicitly sets a prototype/intercept
field; an anomalous `/__offline/` or project-prefixed requested value is kept as
`url_uncertain` when it cannot be identified from evidence. The exclusion basis
is recorded in `summary.json`.

`remaining-targets.csv` distinguishes `still_missing_local` (static/CSS/404 or
accepted v46 target evidence without a v49 entity), `unknown_200_placeholder`
(only a 200 placeholder was observed), and `url_uncertain`. A 200 placeholder
never counts as recovery. `available-unrouted.csv` separately records the exact
case-verified T.gif file present in the v50 output tree while its source route has
a double slash and the output route has one slash. `malformed-navigation.csv`
separately records the accepted anniversary export transform bug; the screenshot
directory itself remains uncollected. The accepted v46 target list is an
observation inventory, not a new browser pass or network request.

`filesystem-crosscheck.csv` records the v49 output-tree case-preserving check for
every remaining `still_missing_local` target. The check does not turn an observed
placeholder into a recovered asset, and it does not claim v51 publication.

No network request was made. Raw headers/cookies/HTML/large DOM payloads were
not copied. v49 is the fixed audit baseline; the route-review evidence is used
only to correct local classification of already-existing output and malformed
navigation. This receipt does not claim v51 publication.

The retained `build_closeout.py` is the local reproducibility helper; its
inputs and output directory are confined to this audit scope.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "canonical_routes_in_scope": len(coverage_rows),
        "all_observed_routes": len(grouped),
        "receipt_records": len(page_observations),
        "remaining_targets": len(remaining_rows),
        "marker_counts": dict(marker_counts),
        "excluded_targets": dict(excluded_target_counts),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""NET-WRATH-008 bounded historical Wrath artwork recovery.

Owns only this batch directory. Reuses accepted core-pages3 transport and the
accepted control7 gate. CDX index rows and replay entities stay separate.
Viewer scripts are observed as text only and are never executed.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import io
import json
import shutil
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except Exception:
    Image = None

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
GAP = ROOT / "research/continuous-recovery-20261015/wrath-artwork-viewer-gap.json"
SELECTED = ROOT / "research/continuous-recovery-20261015/selected-core-pages-source-map.json"
CONTROL_ACCEPT = ROOT / "research/continuous-recovery-20261015/control7-wrapper-acceptance.json"
DEPS = ROOT / "research/continuous-recovery-20261015/wrath-artwork-dependencies.json"
COUNTER_SUMMARY = ROOT / "research/continuous-recovery-20261015/network-assets5/sanitized-summary.json"
COUNTER_MAP = ROOT / "research/continuous-recovery-20261015/network-assets5/asset-source-map.json"
MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v9/build-manifest.json"
LAYOUT = ROOT / ".scratch/offline-navigation-20261015-v9/site/wrath/js/thumbnailslayout.js"
ART_PAGE = ROOT / "research/continuous-recovery-20261015/network-core-pages4/raw/06-wrath_artwork.xml-replay-proxy.body"
CORE3_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
CONTROL7_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"

BASE = "http://www.worldofwarcraft.com/wrath/art.xml"
FALLBACK = "http://www.worldofwarcraft.com/wrath/art.xml?s=1"
WAYBACK = "https://web.archive.org"
FROM_TS = "20040101000000"
ANCHOR = "20080512210044"
PROXY = "http://127.0.0.1:7890"
UA = "wow-recovery-wrath8/20261015"
NUMBERS = [11, 10, 8, 7, 5]
KNOWN = [1, 3, 6, 9, 12]
MAX_PRIMARY = 13
MAX_WITH_FALLBACK = 14
DECLARED_PRIMARY = 12
DECLARED_WITH_FALLBACK = 13
MAX_ATTEMPTS = 32
WINDOW = 480
INTERVAL = 1.25
MIN_FREE = 11_005_853_696
MAX_TOTAL = 64 * 1024 * 1024
MAX_ENTITY = 16 * 1024 * 1024
REDIRECTS = {301, 302, 303, 307, 308}
STOP_CODES = {429, 503}


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


core = load(CORE3_PATH, "wrath8_core3")
core.OUT = OUT
core.RAW = RAW
core.USER_AGENT = UA
core.MIN_INTERVAL_SECONDS = 0.0
gate_mod = load(CONTROL7_PATH, "wrath8_control7")
gate_mod.INTERVAL_SECONDS = INTERVAL


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"expected object {path}")
    return data


def rel(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def free() -> int:
    return int(shutil.disk_usage(OUT).free)


def b32_sha1(body: bytes) -> str | None:
    return base64.b32encode(hashlib.sha1(body).digest()).decode("ascii") if body else None


def body(attempt: dict[str, Any] | None) -> bytes:
    if not attempt:
        return b""
    path = OUT / str((attempt.get("raw") or {}).get("body") or "")
    return path.read_bytes() if path.exists() else b""


def input_digest(path: Path) -> dict[str, Any]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(path), "bytes": path.stat().st_size}


def page_entry() -> dict[str, Any]:
    data = read(SELECTED)
    for row in data.get("entries") or []:
        if row.get("target") == "/wrath/artwork.xml":
            return row
    raise RuntimeError("artwork source map entry missing")


def known_pairs() -> dict[str, Any]:
    data = read(MANIFEST)
    wanted = {f"ss{n}{s}.jpg" for n in KNOWN for s in ("", "-thumb")}
    out = {}
    for row in data.get("files") or []:
        route = str(row.get("route") or "")
        name = route.rsplit("/", 1)[-1]
        if route.startswith("/wrath/images/artwork/") and name in wanted:
            out[name] = {k: row.get(k) for k in (
                "route", "source_base_url", "source_local_path", "source_sha256",
                "source_length", "source_mime", "actual_timestamp",
                "requested_timestamp", "source_map_path", "role"
            )}
    if len(out) != len(wanted):
        raise RuntimeError("known existing pair evidence incomplete")
    return out


def evidence() -> dict[str, Any]:
    gap = read(GAP)
    counter = read(COUNTER_SUMMARY)
    page = page_entry()
    return {
        "gap": {"path": str(GAP.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(GAP),
                "source_page": gap.get("source_page"), "exact_viewer_candidates": gap.get("exact_viewer_candidates")},
        "artwork_page": {"path": str(ART_PAGE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(ART_PAGE),
                         "selected": {k: page.get(k) for k in ("target", "actual_memento", "body_sha256", "body_bytes", "local_path")},
                         "lines": [
                             {"line": 22, "text": "var roothost = \"/wrath/\";"},
                             {"line": 148, "text": "var whichImageviewer = art"},
                             {"line": 150, "text": "two artworkcounter.js references"},
                             {"line": 153, "text": "theCommonDirectory = ./images/artwork/"},
                             {"line": 161, "text": "screenshotsTotal = local + common"},
                             {"line": 168, "text": "screenshotsPerPage = 9"}]},
        "layout": {"path": str(LAYOUT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(LAYOUT),
                   "line": 4, "text": "massiveReplaceString += ... background-image:url(... ss + number + -thumb.jpg) ... src=\"'+roothost+'images/layout/ssborder1.png\" ..."},
        "counter_observations": [
            {k: item.get(k) for k in ("url", "status", "count_values", "api_names")}
            for item in counter.get("counter_count_observations") or []],
        "existing_pair_manifest": {"path": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
                                   "sha256": sha(MANIFEST), "records": known_pairs()},
    }


def entry(rank: int, key: str, kind: str, url: str, ev: dict[str, Any],
          conditional: bool = False, execute_if: str | None = None,
          number: int | None = None, suffix: str | None = None) -> dict[str, Any]:
    item = {"candidate_rank": rank, "target_key": key, "kind": kind,
            "conditional": conditional, "execute_if": execute_if,
            "query_original_url": url, "cdx_query_url": core.cdx_query_url(url),
            "replay_selection": "latest valid status-200-or-Wayback-redirect pre-anchor capture",
            "same_origin_policy": "same scheme/lowercase host; only default ports normalize; path/query literal",
            "evidence": ev}
    if number is not None:
        item["gallery_number"] = number
        item["gallery_suffix"] = suffix
        item["candidate_basis"] = {"literal": "ssN-thumb.jpg" if suffix else "same-origin existing ssN.jpg mode",
                                   "existing_examples": [f"ss{n}{suffix or ''}.jpg" for n in KNOWN],
                                   "actual_cdx_row_required": True}
    return item


def candidates() -> dict[str, Any]:
    ev = evidence()
    rows = [
        entry(1, "viewer-base", "viewer_html", BASE, ev),
        entry(2, "border-layout", "image_layout_dependency",
              "http://www.worldofwarcraft.com/wrath/images/layout/ssborder1.png", ev),
        entry(3, "viewer-fallback-s1", "viewer_html", FALLBACK, ev, True,
              "base viewer does not produce valid historical HTML"),
    ]
    rank = 4
    for number in NUMBERS:
        for suffix, kind in (("-thumb", "image_thumb"), ("", "image_original")):
            rows.append(entry(
                rank, f"gallery-ss{number}{suffix}", kind,
                f"http://www.worldofwarcraft.com/wrath/images/artwork/ss{number}{suffix}.jpg",
                ev, number=number, suffix=suffix))
            rank += 1
    paths = [GAP, SELECTED, CONTROL_ACCEPT, DEPS, COUNTER_SUMMARY, COUNTER_MAP,
             MANIFEST, LAYOUT, ART_PAGE, CORE3_PATH, CONTROL7_PATH]
    return {
        "schema": "continuous-wow-network-wrath8-candidates/v1",
        "batch_id": "NET-WRATH-008",
        "generated_utc": utc(),
        "network_requests": 0,
        "primary_target_count": DECLARED_PRIMARY,
        "conditional_target_count": DECLARED_WITH_FALLBACK,
        "fallback_policy": "art.xml?s=1 query only if base has no valid HTML replay",
        "gallery_order": NUMBERS,
        "gallery_interleave": "thumb then original",
        "prioritization_change": {
            "reason": "inserted exact border dependency after viewer and removed the last common ss4 thumb/original pair to remain within the 14-target cap",
            "inserted_target": "border-layout",
            "excluded_targets": [
                {"target_key": "gallery-ss4-thumb", "url": "http://www.worldofwarcraft.com/wrath/images/artwork/ss4-thumb.jpg", "category": "not_requested", "reason": "queue reduced after border priority"},
                {"target_key": "gallery-ss4", "url": "http://www.worldofwarcraft.com/wrath/images/artwork/ss4.jpg", "category": "not_requested", "reason": "queue reduced after border priority"}
            ],
            "actual_primary_target_count": DECLARED_PRIMARY,
            "actual_conditional_target_count": DECLARED_WITH_FALLBACK,
            "max_primary_target_count": MAX_PRIMARY,
            "max_with_fallback_target_count": MAX_WITH_FALLBACK
        },
        "input_digests": {str(p.relative_to(ROOT)).replace("\\", "/"): input_digest(p) for p in paths},
        "query_scope": {"endpoint": f"{WAYBACK}/cdx/search/cdx", "from": FROM_TS, "to": ANCHOR,
                        "anchor_timestamp": ANCHOR, "columns": core.CDX_COLUMNS, "limit": core.CDX_LIMIT,
                        "collapse": "digest", "matchType": "exact",
                        "actual_memento": "valid replay response header only"},
        "policy": {
            "direct_first": True, "proxy": PROXY,
            "direct_connect_timeout_seconds": 4, "direct_total_timeout_seconds": 12,
            "proxy_connect_timeout_seconds": 8, "proxy_total_timeout_seconds": 20,
            "max_distinct_targets_primary": MAX_PRIMARY,
            "max_distinct_targets_with_fallback": MAX_WITH_FALLBACK,
            "max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW,
            "minimum_dispatch_interval_seconds": INTERVAL, "minimum_free_bytes": MIN_FREE,
            "max_total_body_bytes": MAX_TOTAL, "max_entity_body_bytes": MAX_ENTITY,
            "automatic_redirects": 0, "manual_redirect_follow_hops": 0,
            "stop_http_codes": sorted(STOP_CODES), "tls_verification": "enabled_by_curl_default",
            "concurrent_source_requests": 1},
        "entries": rows,
    }


def prepare() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    data = candidates()
    write(OUT / "candidates.json", data)
    cand_sha = sha(OUT / "candidates.json")
    write(OUT / "config.json", {
        "schema": "continuous-wow-network-wrath8-config/v1", "batch_id": "NET-WRATH-008",
        "candidate_path": "research/continuous-recovery-20261015/network-wrath8/candidates.json",
        "candidate_sha256": cand_sha,
        "transport_helper": str(CORE3_PATH.relative_to(ROOT)).replace("\\", "/"),
        "dispatch_gate_helper": str(CONTROL7_PATH.relative_to(ROOT)).replace("\\", "/"),
        "network_requests": 0, "policy": data["policy"]})
    write(OUT / "plan.json", {
        "schema": "continuous-wow-network-wrath8-plan/v1", "batch_id": "NET-WRATH-008",
        "mode": "plan_only", "prepared_utc": utc(), "candidate_sha256": cand_sha,
        "disk_free_bytes": free(), "minimum_free_bytes": MIN_FREE, "network_requests": 0,
        "ready": free() >= MIN_FREE, "target_order": [x["target_key"] for x in data["entries"]]})
    print(json.dumps({"mode": "plan_only", "network_requests": 0, "candidate_count": len(data["entries"]),
                      "candidate_sha256": cand_sha, "disk_free_bytes": free()}, ensure_ascii=False))
    return 0


def public_attempt(item: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in item.items() if k not in {"cdx_records", "cdx_valid_records"}}


def body_metrics(attempt: dict[str, Any] | None, capture: dict[str, Any] | None) -> dict[str, Any]:
    raw = body(attempt)
    expected = str((capture or {}).get("digest") or "").upper() or None
    calculated = b32_sha1(raw)
    return {
        "body_bytes": len(raw), "body_sha256": hashlib.sha256(raw).hexdigest() if raw else None,
        "cdx_digest_expected": expected, "cdx_digest_calculated": calculated,
        "cdx_digest_match": bool(expected and calculated and expected == calculated),
        "cdx_length": int(capture["length"]) if capture and str(capture.get("length", "")).isdigit() else None,
        "actual_memento": attempt.get("memento_datetime") if attempt else None,
        "content_type": attempt.get("content_type") if attempt else None,
        "source_status": attempt.get("source_status") if attempt else None,
        "raw_body_path": (attempt.get("raw") or {}).get("body") if attempt else None,
        "raw_headers_path": (attempt.get("raw") or {}).get("headers") if attempt else None,
        "raw_trace_path": (attempt.get("raw") or {}).get("trace") if attempt else None}


def image_validation(raw: bytes) -> tuple[bool, dict[str, Any], str | None]:
    info = {"library": "Pillow", "verify": "not_run", "load": "not_run",
            "format": None, "width": None, "height": None, "mode": None, "error": None}
    if Image is None:
        info["error"] = "Pillow_unavailable"
        return False, info, "pillow_unavailable"
    if not raw:
        return False, info, "empty_body"
    try:
        with Image.open(io.BytesIO(raw)) as img:
            info["format"], info["width"], info["height"], info["mode"] = img.format, img.width, img.height, img.mode
            img.verify()
        info["verify"] = "passed"
        with Image.open(io.BytesIO(raw)) as img:
            img.load()
        info["load"] = "passed"
    except Exception as exc:
        info["error"] = type(exc).__name__ + ": " + str(exc)
        return False, info, "pillow_validation_failed"
    return True, info, None


def viewer_observation(raw: bytes) -> dict[str, Any]:
    text = raw[:2 * 1024 * 1024].decode("utf-8", errors="replace").lower()
    flags = {
        "which_imageviewer_art": 'whichimageviewer = "art"' in text or "whichimageviewer = 'art'" in text,
        "artwork_counter_reference": "artworkcounter.js" in text,
        "thumbnail_layout_reference": "thumbnailslayout.js" in text,
        "art_xml_reference": "art.xml" in text,
        "screenshots_total_reference": "screenshotstotal" in text,
        "screenshots_per_page_reference": "screenshotsperpage" in text}
    return {"scripts_executed": False, "text_bytes_observed": len(raw), "markers": flags,
            "marker_count": sum(bool(x) for x in flags.values())}


def classify(entry: dict[str, Any], replay: dict[str, Any] | None,
             capture: dict[str, Any] | None) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
    if replay is None or not replay.get("executed"):
        return "not_requested", {"reason": "replay_not_requested", "selected_capture": capture}, None
    status = replay.get("source_status")
    if replay.get("transport_error"):
        return "network_unknown", {"reason": replay.get("transport_reason") or "curl_or_tls_failure",
                                   "source_status": status, "selected_capture": capture}, None
    if status in STOP_CODES:
        return "rate_limited", {"reason": "endpoint_stop_status", "source_status": status,
                               "retry_after": replay.get("retry_after"), "selected_capture": capture}, None
    if status == 404:
        return "not_archived", {"reason": "replay_http_404", "source_status": status,
                               "selected_capture": capture}, None
    if status in REDIRECTS:
        return "redirect_unfollowed", {"reason": "manual_redirect_follow_hops_zero",
                                       "source_status": status, "location": replay.get("location"),
                                       "selected_capture": capture}, None
    if status != 200:
        return "http_response", {"reason": "non_200_replay", "source_status": status,
                                "selected_capture": capture}, None
    metrics = body_metrics(replay, capture)
    raw = body(replay)
    if not metrics["actual_memento"]:
        return "invalid_payload", {"reason": "missing_actual_memento_header",
                                   "validation": metrics, "selected_capture": capture}, None
    if entry["kind"] == "viewer_html":
        info = replay.get("html") or {}
        if not info.get("is_html"):
            return "soft404", {"reason": "viewer_body_not_html", "validation": metrics,
                               "selected_capture": capture}, None
        if set(info.get("markers") or []).intersection({"wayback_machine", "not_archived", "no_captures", "page_not_found", "page_cannot_be_found"}):
            return "not_archived", {"reason": "Wayback error or not-archived body",
                                    "html": info, "validation": metrics, "selected_capture": capture}, None
        if not raw:
            return "soft404", {"reason": "empty_html_body", "validation": metrics,
                               "selected_capture": capture}, None
        if not metrics["cdx_digest_match"]:
            return "invalid_payload", {"reason": "cdx_digest_mismatch", "validation": metrics,
                                       "selected_capture": capture}, None
        valid = {**metrics, "html": info, "viewer": viewer_observation(raw)}
        return "valid_html", valid, valid
    if not raw:
        return "soft404", {"reason": "empty_image_body", "validation": metrics,
                           "selected_capture": capture}, None
    if not metrics["cdx_digest_match"]:
        return "invalid_payload", {"reason": "cdx_digest_mismatch", "validation": metrics,
                                   "selected_capture": capture}, None
    ok, decoded, reason = image_validation(raw)
    valid = {**metrics, "decode": decoded}
    if not ok:
        return "invalid_image", {"reason": reason, "validation": valid, "selected_capture": capture}, None
    expected_format = "PNG" if entry["kind"] == "image_layout_dependency" else "JPEG"
    if decoded.get("format") != expected_format:
        return "invalid_image", {"reason": f"expected_{expected_format}_for_target",
                                 "validation": valid, "selected_capture": capture}, None
    return "valid_image", valid, valid


def result_for(item: dict[str, Any], queries: list[dict[str, Any]],
               selected: dict[str, Any] | None, replays: list[dict[str, Any]],
               forced_category: str | None = None,
               forced_detail: dict[str, Any] | None = None) -> dict[str, Any]:
    query = queries[-1] if queries else None
    replay = replays[-1] if replays else None
    records = (query or {}).get("cdx_records") or []
    valid_records = (query or {}).get("cdx_valid_records") or []
    validation = None
    if forced_category:
        category, detail = forced_category, forced_detail or {}
    elif query is None or not query.get("executed"):
        category, detail = "not_requested", {"reason": (query or {}).get("unrequested_reason", "query_not_requested")}
    elif query.get("transport_error"):
        category, detail = "network_unknown", {"reason": query.get("transport_reason") or "query_transport_error",
                                               "source_status": query.get("source_status")}
    elif query.get("source_status") in STOP_CODES:
        category, detail = "rate_limited", {"reason": "endpoint_stop_status",
                                            "source_status": query.get("source_status"),
                                            "retry_after": query.get("retry_after")}
    elif not query.get("cdx_parse_valid"):
        category, detail = "cdx_invalid", {"reason": query.get("cdx_parse_error") or "cdx_parse_failed",
                                           "source_status": query.get("source_status")}
    elif selected is None:
        category = "cdx_empty_in_range" if not records else "cdx_no_valid_capture"
        detail = {"reason": "no exact same-origin status-200-or-Wayback-redirect row",
                  "capture_index_count": len(records), "permanent_unarchived_claim": False}
    elif replay is None or not replay.get("executed"):
        category, detail = "not_requested", {
            "reason": (replay or {}).get("unrequested_reason") or "replay_not_requested_after_selected_capture",
            "selected_capture": selected}
    else:
        category, detail, validation = classify(item, replay, selected)
    actual = replay.get("memento_datetime") if replay and replay.get("executed") else None
    raw = body(replay)
    reason = None if category in {"valid_html", "valid_image"} else detail.get("reason")
    return {
        "candidate_rank": item["candidate_rank"], "target_key": item["target_key"],
        "kind": item["kind"], "conditional": item.get("conditional", False),
        "execute_if": item.get("execute_if"), "query_original_url": item["query_original_url"],
        "category": category, "detail": detail, "validation": validation,
        "cdx": {
            "query_url": item["cdx_query_url"],
            "attempts": [public_attempt(x) for x in queries],
            "source_status": query.get("source_status") if query else None,
            "source_response_count": sum(x.get("source_status") is not None for x in queries),
            "capture_index_count": len(records), "valid_capture_count": len(valid_records),
            "capture_records": records, "selected_capture": selected},
        "replay_attempt_count": sum(x.get("executed", False) for x in replays),
        "replay_source_response_count": sum(x.get("source_status") is not None for x in replays),
        "replay_hops": [public_attempt(x) for x in replays],
        "actual_memento_or_null": actual,
        "final_source_status": replay.get("source_status") if replay else None,
        "final_content_type": replay.get("content_type") if replay else None,
        "final_body_bytes": len(raw) if replay else 0,
        "final_body_sha256": hashlib.sha256(raw).hexdigest() if raw else None,
        "unrequested_reason": reason}


def source_map_entry(result: dict[str, Any]) -> dict[str, Any]:
    replay = (result.get("replay_hops") or [])[-1]
    capture = (result.get("cdx") or {}).get("selected_capture") or {}
    val = result.get("validation") or {}
    return {
        "target": result["target_key"], "query_original_url": result["query_original_url"],
        "actual_memento": result["actual_memento_or_null"],
        "source_status": result["final_source_status"], "content_type": result["final_content_type"],
        "body_bytes": result["final_body_bytes"], "body_sha256": result["final_body_sha256"],
        "raw_body_path": (replay.get("raw") or {}).get("body"),
        "raw_headers_path": (replay.get("raw") or {}).get("headers"),
        "captured_original_url": capture.get("original"),
        "indexed_capture_timestamp": capture.get("timestamp"),
        "indexed_statuscode": capture.get("statuscode"),
        "indexed_cdx_digest": capture.get("digest"), "indexed_cdx_length": capture.get("length"),
        "cdx_digest_calculated": val.get("cdx_digest_calculated"),
        "cdx_digest_match": val.get("cdx_digest_match"), "validation": val,
        "action": "review source mapping before any integration; entity remains only in this batch raw directory"}


def dispatch_ok(state: Any, started: float) -> tuple[bool, str | None]:
    if state.stop_reason:
        return False, state.stop_reason
    if state.attempts >= MAX_ATTEMPTS:
        return False, "attempt_limit"
    if time.monotonic() - started >= WINDOW:
        return False, "network_window_exhausted"
    if free() < MIN_FREE:
        return False, "disk_free_below_threshold"
    if state.total_body_bytes >= MAX_TOTAL:
        return False, "total_body_limit"
    return True, None


def request(url: str, transport: str, kind: str, key: str,
            state: Any, gate: Any, started: float) -> dict[str, Any]:
    ok, why = dispatch_ok(state, started)
    if not ok:
        return {"executed": False, "attempt": state.attempts + 1, "kind": kind,
                "target_key": key, "transport": transport, "url": url,
                "unrequested_reason": why or "limit_before_request"}
    number = state.attempts + 1
    gate_record = gate.before_dispatch(number, transport, key)
    item = core.run_request(url, transport, kind, key, state, number)
    item["dispatch_utc"] = gate_record["dispatch_utc"]
    item["dispatch_monotonic"] = gate_record["dispatch_monotonic"]
    item["dispatch_interval_seconds"] = gate_record["interval_since_previous_dispatch_seconds"]
    item["gate_persisted_before_transport"] = gate_record["persisted_before_transport"]
    raw = body(item)
    item["local_zero_byte_body_placeholder"] = bool(item.get("source_status") is None and not raw)
    item["body_is_source_response"] = item.get("source_status") is not None
    return item


def do_target(item: dict[str, Any], transport: str, state: Any,
              gate: Any, started: float) -> tuple[dict[str, Any], str]:
    queries: list[dict[str, Any]] = []
    replays: list[dict[str, Any]] = []
    selected = None
    ok, why = dispatch_ok(state, started)
    if not ok:
        queries.append({"executed": False, "target_key": item["target_key"],
                        "url": item["cdx_query_url"], "transport": transport,
                        "unrequested_reason": why or "limit_before_query"})
        return result_for(item, queries, None, replays), transport
    query = request(item["cdx_query_url"], transport, "cdx", item["target_key"], state, gate, started)
    queries.append(query)
    if query.get("executed"):
        records = query.get("cdx_records") or []
        valid = core.valid_cdx_records(records, item["query_original_url"])
        query["cdx_capture_index_count"] = len(records)
        query["cdx_valid_capture_count"] = len(valid)
        query["cdx_valid_records"] = valid
        selected = core.select_capture(valid)
        if selected is not None and not state.stop_reason:
            replays.append(request(core.replay_url(selected), transport, "replay",
                                   item["target_key"], state, gate, started))
    return result_for(item, queries, selected, replays), transport


def write_outputs(cands: dict[str, Any], results: list[dict[str, Any]], state: Any,
                  started_utc: str, finished_utc: str, updated_utc: str,
                  disk_before: int, disk_after: int, transport: str, gate: Any) -> None:
    counts: dict[str, int] = {}
    for item in results:
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    entities = [source_map_entry(item) for item in results if item["category"] in {"valid_html", "valid_image"}]
    intervals = [x["interval_since_previous_dispatch_seconds"] for x in gate.dispatches
                 if x["interval_since_previous_dispatch_seconds"] is not None]
    report = {
        "schema": "continuous-wow-network-wrath8-batch-report/v1", "batch_id": "NET-WRATH-008",
        "mode": "executed", "started_utc": started_utc, "finished_utc": finished_utc,
        "request_window_finished_utc": finished_utc, "report_updated_utc": updated_utc,
        "inputs": {"candidates": "research/continuous-recovery-20261015/network-wrath8/candidates.json",
                   "candidates_sha256": sha(OUT / "candidates.json"),
                   "input_digests": cands["input_digests"]},
        "target_declaration": {"primary_target_count": DECLARED_PRIMARY,
                                "conditional_target_count": DECLARED_WITH_FALLBACK,
                                "prioritization_change": cands["prioritization_change"]},
        "policy": cands["policy"],
        "preflight": {"drive": "D:", "disk_free_bytes_before": disk_before,
                      "disk_free_bytes_after": disk_after, "minimum_free_bytes": MIN_FREE},
        "transport": {"confirmed_transport_after_first_request": transport,
                      "curl": str(core.CURL),
                      "helper": str(CORE3_PATH.relative_to(ROOT)).replace("\\", "/"),
                      "dispatch_gate": str(CONTROL7_PATH.relative_to(ROOT)).replace("\\", "/")},
        "distinct_target_count": len({x["query_original_url"] for x in results}),
        "primary_target_count": DECLARED_PRIMARY, "conditional_target_count": DECLARED_WITH_FALLBACK,
        "max_distinct_targets_primary": MAX_PRIMARY,
        "max_distinct_targets_with_fallback": MAX_WITH_FALLBACK,
        "category_counts": counts,
        "capture_index_count": sum(x["cdx"]["capture_index_count"] for x in results),
        "valid_capture_count": sum(x["cdx"]["valid_capture_count"] for x in results),
        "valid_entity_count": len(entities),
        "cdx_source_response_count": sum(x["cdx"]["source_response_count"] for x in results),
        "replay_source_response_count": sum(x["replay_source_response_count"] for x in results),
        "source_request_count": state.attempts, "transport_attempt_count": state.attempts,
        "failed_attempt_count": state.failed_attempts, "source_response_count": state.source_responses,
        "total_body_bytes": state.total_body_bytes, "dispatch_count": len(gate.dispatches),
        "dispatch_min_interval_observed_seconds": min(intervals) if intervals else None,
        "stop_reason": state.stop_reason, "stop_detail": state.stop_detail, "rate_limit": state.rate_limit,
        "results": results,
        "raw_evidence_note": "Raw headers, traces, stderr and bodies remain below this batch raw directory. A zero-byte body after transport failure is a local placeholder, not source content. CONNECT 200 is excluded from source counts. CDX length is index metadata, never payload length."}
    write(OUT / "batch-report.json", report)
    targets = []
    for x in results:
        targets.append({"candidate_rank": x["candidate_rank"], "target_key": x["target_key"],
                        "kind": x["kind"], "conditional": x["conditional"],
                        "query_original_url": x["query_original_url"], "category": x["category"],
                        "cdx_source_status": x["cdx"]["source_status"],
                        "replay_source_status": x["final_source_status"],
                        "actual_memento_or_null": x["actual_memento_or_null"],
                        "body_bytes": x["final_body_bytes"], "body_sha256": x["final_body_sha256"],
                        "capture_index_count": x["cdx"]["capture_index_count"],
                        "valid_capture_count": x["cdx"]["valid_capture_count"],
                        "selected_capture_timestamp": (x["cdx"]["selected_capture"] or {}).get("timestamp"),
                        "unrequested_reason": x["unrequested_reason"], "validation": x["validation"]})
    summary = {
        "schema": "continuous-wow-network-wrath8-sanitized-summary/v1", "batch_id": "NET-WRATH-008",
        "mode": "executed", "report_sha256": sha(OUT / "batch-report.json"),
        "started_utc": started_utc, "finished_utc": finished_utc,
        "request_window_finished_utc": finished_utc, "report_updated_utc": updated_utc,
        "network_requests": state.attempts, "source_response_count": state.source_responses,
        "primary_target_count": DECLARED_PRIMARY, "conditional_target_count": DECLARED_WITH_FALLBACK,
        "max_distinct_targets_primary": MAX_PRIMARY,
        "max_distinct_targets_with_fallback": MAX_WITH_FALLBACK,
        "failed_attempt_count": state.failed_attempts, "capture_index_count": report["capture_index_count"],
        "valid_capture_count": report["valid_capture_count"], "valid_entity_count": len(entities),
        "category_counts": counts, "total_body_bytes": state.total_body_bytes,
        "target_declaration": {"primary_target_count": DECLARED_PRIMARY,
                                "conditional_target_count": DECLARED_WITH_FALLBACK,
                                "prioritization_change": cands["prioritization_change"]},
        "disk_free_bytes_before": disk_before, "disk_free_bytes_after": disk_after,
        "dispatch_count": len(gate.dispatches),
        "dispatch_min_interval_observed_seconds": report["dispatch_min_interval_observed_seconds"],
        "stop_reason": state.stop_reason, "targets": targets,
        "raw_evidence_note": report["raw_evidence_note"]}
    write(OUT / "sanitized-summary.json", summary)
    md_lines = [
        "# NET-WRATH-008 sanitized summary",
        "",
        f"- Network requests: `{state.attempts}`; source responses: `{state.source_responses}`.",
        f"- Capture index rows: `{report['capture_index_count']}`; valid entities: `{len(entities)}`.",
        f"- Primary targets: `{DECLARED_PRIMARY}`; conditional target declaration: `{DECLARED_WITH_FALLBACK}`.",
        f"- Dispatches: `{len(gate.dispatches)}`; minimum observed interval: `{report['dispatch_min_interval_observed_seconds']}` seconds.",
        f"- Stop reason: `{state.stop_reason or 'completed'}`.",
        "",
        "| Target | Kind | Category | Memento | Body bytes | SHA-256 |",
        "|---|---|---|---|---:|---|",
    ]
    for target in targets:
        md_lines.append(
            f"| `{target['target_key']}` | `{target['kind']}` | `{target['category']}` | "
            f"`{target['actual_memento_or_null'] or ''}` | `{target['body_bytes']}` | "
            f"`{target['body_sha256'] or ''}` |"
        )
    md_lines.extend(["", report["raw_evidence_note"]])
    (OUT / "sanitized-summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    write(OUT / "payload-source-map.json", {
        "schema": "continuous-wow-network-wrath8-payload-source-map/v1",
        "generated_utc": updated_utc, "only_real_valid_entities": True, "entries": entities})
    redirects = []
    for x in results:
        for hop in x.get("replay_hops") or []:
            if hop.get("source_status") in REDIRECTS:
                redirects.append({"target_key": x["target_key"], "query_original_url": x["query_original_url"],
                                  "selected_capture": x["cdx"]["selected_capture"],
                                  "source_status": hop.get("source_status"), "location": hop.get("location"),
                                  "manual_followed": False, "reason": "manual_redirect_follow_hops_zero"})
    write(OUT / "redirect-evidence.json", {"schema": "continuous-wow-network-wrath8-redirect-evidence/v1",
                                           "generated_utc": updated_utc, "manual_redirect_follow_hops": 0,
                                           "entries": redirects})


def execute() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    if not (OUT / "candidates.json").exists():
        prepare()
    cands = read(OUT / "candidates.json")
    if cands.get("network_requests") != 0 or len(cands.get("entries") or []) != DECLARED_WITH_FALLBACK:
        raise RuntimeError("candidate plan is not the expected 13-entry offline declaration")
    disk_before = free()
    if disk_before < MIN_FREE:
        raise RuntimeError(f"D free space {disk_before} below threshold {MIN_FREE}")
    started_utc = utc()
    window_started = time.monotonic()
    state = core.RunState(window_started)
    journal = {
        "schema": "continuous-wow-network-wrath8-dispatch-log/v1",
        "batch_id": "NET-WRATH-008",
        "simulation": False,
        "policy": {"minimum_dispatch_interval_seconds": INTERVAL,
                   "manual_redirect_follow_hops": 0, "max_attempts": MAX_ATTEMPTS,
                   "network_window_seconds": WINDOW},
        "disk_preflight": {"checked_utc": utc(), "disk_free_bytes": disk_before,
                           "minimum_free_bytes": MIN_FREE},
        "dispatches": []}
    gate = gate_mod.GateState(
        datetime.now(timezone.utc) - timedelta(seconds=1),
        journal_path=OUT / "dispatch-log.json", journal=journal)
    gate.persist()
    results: list[dict[str, Any]] = []
    transport = "unconfirmed"
    try:
        rows = cands["entries"]
        base_item = rows[0]
        base_queries: list[dict[str, Any]] = []
        base_replays: list[dict[str, Any]] = []
        selected = None
        first = request(base_item["cdx_query_url"], "direct", "cdx", base_item["target_key"],
                         state, gate, window_started)
        base_queries.append(first)
        if first.get("executed") and not first.get("transport_error"):
            transport = "direct"
        elif first.get("executed") and first.get("transport_error") and not state.stop_reason:
            second = request(base_item["cdx_query_url"], "proxy", "cdx", base_item["target_key"],
                             state, gate, window_started)
            base_queries.append(second)
            if second.get("executed"):
                transport = "proxy"
        else:
            transport = "proxy_not_attempted_after_limit"
        query = base_queries[-1]
        if query.get("executed"):
            records = query.get("cdx_records") or []
            valid = core.valid_cdx_records(records, base_item["query_original_url"])
            query["cdx_capture_index_count"] = len(records)
            query["cdx_valid_capture_count"] = len(valid)
            query["cdx_valid_records"] = valid
            selected = core.select_capture(valid)
            if selected is not None and not state.stop_reason:
                base_replays.append(request(
                    core.replay_url(selected),
                    transport if transport in {"direct", "proxy"} else "proxy",
                    "replay", base_item["target_key"], state, gate, window_started))
        base_result = result_for(base_item, base_queries, selected, base_replays)
        results.append(base_result)

        border_item = next(x for x in rows if x["target_key"] == "border-layout")
        border_result, transport = do_target(
            border_item, transport if transport in {"direct", "proxy"} else "proxy",
            state, gate, window_started)
        results.append(border_result)

        fallback_item = next(x for x in rows if x["target_key"] == "viewer-fallback-s1")
        if base_result["category"] == "valid_html":
            results.append(result_for(
                fallback_item, [], None, [],
                forced_category="not_requested",
                forced_detail={"reason": "conditional_fallback_not_needed_after_valid_base_html"}))
        else:
            fallback_result, transport = do_target(
                fallback_item, transport if transport in {"direct", "proxy"} else "proxy",
                state, gate, window_started)
            results.append(fallback_result)

        gallery_items = [x for x in rows if x["target_key"].startswith("gallery-")]
        for item in gallery_items:
            result, transport = do_target(
                item, transport if transport in {"direct", "proxy"} else "proxy",
                state, gate, window_started)
            results.append(result)

        finished = utc()
        updated = utc()
        write_outputs(cands, results, state, started_utc, finished, updated,
                      disk_before, free(), transport, gate)
        print(json.dumps({
            "batch_id": "NET-WRATH-008", "targets_reported": len(results),
            "attempts": state.attempts, "source_responses": state.source_responses,
            "failed_attempts": state.failed_attempts,
            "capture_index_count": sum(x["cdx"]["capture_index_count"] for x in results),
            "valid_entities": sum(x["category"] in {"valid_html", "valid_image"} for x in results),
            "category_counts": {key: sum(x["category"] == key for x in results)
                                for key in sorted({x["category"] for x in results})},
            "stop_reason": state.stop_reason, "confirmed_transport": transport,
            "network_requests": state.attempts}, ensure_ascii=False))
        return 0
    finally:
        gate_mod.persist_postflight(gate, state.attempts, free_fn=free)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.prepare == args.execute:
        parser.error("choose exactly one of --prepare or --execute")
    return prepare() if args.prepare else execute()


if __name__ == "__main__":
    raise SystemExit(main())








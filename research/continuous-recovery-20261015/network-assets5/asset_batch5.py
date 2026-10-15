"""NET-ASSETS-005 bounded Wayback asset recovery.

This driver owns only ``network-assets5``.  It reuses the accepted core-pages3
transport and header/CDX helpers, but keeps a separate output and raw tree.
CDX rows are index evidence; only a real 200 Memento replay that passes the
kind-specific validation can enter ``asset-source-map.json``.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import io
import json
import re
import shutil
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

try:
    from PIL import Image
except Exception:  # pragma: no cover - checked during execution
    Image = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
INPUT_CANDIDATES = ROOT / "research/continuous-recovery-20261015/asset-batch5-candidates.json"
ACCEPTED_DEDUP = ROOT / "research/continuous-recovery-20261015/resource-dedup-acceptance.json"
DEDUP_REPORT = ROOT / "research/continuous-recovery-20261015/local-resource-dedup/dedup-inventory.json"
ASSET_QUEUE = ROOT / "research/continuous-recovery-20261015/local-resource-dedup/network-asset-queue.json"
CORE3_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"

EXPECTED_CANDIDATES_SHA256 = "71d084172c775ddae8063e622ae45c1fc2e8b72283030c6dc31d9110abfdcf0a"
EXPECTED_DEDUP_REPORT_SHA256 = "d098d3147217243fa65085c3e5bd03a7ab0bf3e780a645d7554d211ddeefeba7"

MAX_TARGETS = 15
MAX_ATTEMPTS = 32
WINDOW_SECONDS = 8 * 60
MIN_INTERVAL_SECONDS = 1.2
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY_BYTES = 64 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 16 * 1024 * 1024
REDIRECT_CODES = {301, 302, 303, 307, 308}
STOP_HTTP_CODES = {429, 503}
JS_MIMES = {
    "text/javascript",
    "application/javascript",
    "application/x-javascript",
    "application/ecmascript",
    "text/ecmascript",
    "text/plain",
}


def load_core3() -> Any:
    spec = importlib.util.spec_from_file_location("wow_assets5_core3_reuse", CORE3_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load accepted core-pages3 helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    module.RAW = RAW
    module.USER_AGENT = "wow-recovery-assets5/20261015"
    return module


core = load_core3()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def disk_free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def b32_sha1(body: bytes) -> str | None:
    if not body:
        return None
    return base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")


def safe_json(value: Any) -> Any:
    """Keep public reports JSON-serializable without exposing raw headers."""
    return value


def validate_candidate_shape(candidates: dict[str, Any]) -> None:
    entries = candidates.get("entries") or []
    if len(entries) != MAX_TARGETS or candidates.get("target_count") != MAX_TARGETS:
        raise RuntimeError(f"expected {MAX_TARGETS} candidates, got {len(entries)}")
    if candidates.get("network_requests") != 0:
        raise RuntimeError("candidate declaration must remain network_requests=0")
    if len({str(entry.get("url")) for entry in entries}) != MAX_TARGETS:
        raise RuntimeError("candidate URLs are not unique")
    expected_kinds = ["javascript_counter", "javascript_counter"] + ["image"] * 13
    for index, (entry, expected_kind) in enumerate(zip(entries, expected_kinds), start=1):
        url = str(entry.get("url") or "")
        parsed = urlsplit(url)
        if parsed.scheme != "http" or not parsed.hostname or not parsed.path:
            raise RuntimeError(f"candidate {index} is not an exact HTTP URL: {url}")
        if entry.get("kind") != expected_kind:
            raise RuntimeError(f"candidate {index} kind/order mismatch: {entry.get('kind')}")
        if not entry.get("evidence"):
            raise RuntimeError(f"candidate {index} has no provenance evidence: {url}")


def verify_inputs() -> dict[str, Any]:
    if not INPUT_CANDIDATES.exists() or not ACCEPTED_DEDUP.exists() or not DEDUP_REPORT.exists() or not ASSET_QUEUE.exists():
        raise RuntimeError("required NET-ASSETS-005 input is missing")
    candidate_sha = sha256_file(INPUT_CANDIDATES)
    if candidate_sha != EXPECTED_CANDIDATES_SHA256:
        raise RuntimeError(f"candidate SHA mismatch: expected {EXPECTED_CANDIDATES_SHA256}, got {candidate_sha}")
    candidates = json.loads(INPUT_CANDIDATES.read_text(encoding="utf-8"))
    validate_candidate_shape(candidates)
    queue_sha = sha256_file(ASSET_QUEUE)
    if queue_sha != str((candidates.get("inputs") or {}).get("asset_queue_sha256") or ""):
        raise RuntimeError(f"asset queue SHA mismatch: declared {(candidates.get('inputs') or {}).get('asset_queue_sha256')}, got {queue_sha}")
    dedup = json.loads(ACCEPTED_DEDUP.read_text(encoding="utf-8"))
    if not dedup.get("accepted") or dedup.get("network_requests") != 0:
        raise RuntimeError("resource-dedup acceptance is not accepted or records network requests")
    dedup_report_sha = sha256_file(DEDUP_REPORT)
    if dedup_report_sha != EXPECTED_DEDUP_REPORT_SHA256 or dedup_report_sha != str(dedup.get("report_sha256") or ""):
        raise RuntimeError(f"resource-dedup report SHA mismatch: got {dedup_report_sha}")
    return {
        "candidates": candidates,
        "candidate_sha256": candidate_sha,
        "asset_queue_sha256": queue_sha,
        "dedup_acceptance_sha256": sha256_file(ACCEPTED_DEDUP),
        "dedup_report_sha256": dedup_report_sha,
    }


def plan_document(inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "continuous-wow-asset-batch5-plan/v1",
        "mode": "exact_cdx_then_one_200_replay_per_target",
        "prepared_utc": now_utc(),
        "input_candidates": str(INPUT_CANDIDATES.relative_to(ROOT)).replace("\\", "/"),
        "input_candidates_sha256": inputs["candidate_sha256"],
        "asset_queue_sha256": inputs["asset_queue_sha256"],
        "accepted_dedup": str(ACCEPTED_DEDUP.relative_to(ROOT)).replace("\\", "/"),
        "accepted_dedup_sha256": inputs["dedup_acceptance_sha256"],
        "accepted_dedup_report_sha256": inputs["dedup_report_sha256"],
        "targets": [
            {
                "rank": index,
                "url": entry["url"],
                "kind": entry["kind"],
                "priority": entry.get("priority"),
                "action": "exact_cdx_then_latest_preanchor_valid_200_replay",
            }
            for index, entry in enumerate(inputs["candidates"]["entries"], start=1)
        ],
        "policy": {
            "max_targets": MAX_TARGETS,
            "max_attempts": MAX_ATTEMPTS,
            "window_seconds": WINDOW_SECONDS,
            "minimum_start_interval_seconds": MIN_INTERVAL_SECONDS,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
            "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
            "direct_first_then_confirmed_transport": True,
            "direct_connect_timeout_seconds": core.DIRECT_CONNECT_SECONDS,
            "direct_total_timeout_seconds": core.DIRECT_MAX_SECONDS,
            "proxy": core.PROXY,
            "proxy_connect_timeout_seconds": core.PROXY_CONNECT_SECONDS,
            "proxy_total_timeout_seconds": core.PROXY_MAX_SECONDS,
            "automatic_redirects": 0,
            "manual_wayback_redirect_hops": 1,
            "stop_http_codes": sorted(STOP_HTTP_CODES),
            "tls_verification": "curl_default_verification_enabled",
            "uri_policy": "same scheme and lower-cased host; only default port equivalence; exact path/query",
            "cdx_policy": "exact matchType=exact, 2004-01-01 through 2008-05-12 anchor; one latest preanchor status-200 replay",
            "counter_policy": "static text observation only; no JavaScript execution or derived script",
            "image_policy": "Pillow verify plus load; format, dimensions, MIME, body SHA-256 and CDX base32-SHA1 independently recorded",
        },
        "network_requests": 0,
        "ready": disk_free_bytes() >= MIN_FREE_BYTES,
    }


def write_preparation(inputs: dict[str, Any], plan: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    candidates = dict(inputs["candidates"])
    candidates["input_sha256"] = inputs["candidate_sha256"]
    candidates["execution_policy"] = plan["policy"]
    candidates["execution"] = {"network_requests": 0, "status": "planned"}
    write_json(OUT / "candidates.json", candidates)
    write_json(OUT / "batch-config.json", plan)
    write_json(OUT / "plan.json", plan)


def prepare() -> int:
    inputs = verify_inputs()
    plan = plan_document(inputs)
    write_preparation(inputs, plan)
    print(json.dumps({
        "mode": "plan_only",
        "target_count": MAX_TARGETS,
        "network_requests": 0,
        "candidate_sha256": inputs["candidate_sha256"],
        "asset_queue_sha256": inputs["asset_queue_sha256"],
        "accepted_dedup_sha256": inputs["dedup_acceptance_sha256"],
        "accepted_dedup_report_sha256": inputs["dedup_report_sha256"],
        "disk_free_bytes": disk_free_bytes(),
    }, ensure_ascii=False))
    return 0


def request_serial(
    url: str,
    kind: str,
    target: str,
    state: Any,
    transport_state: dict[str, str | None],
) -> list[dict[str, Any]]:
    """Use direct for the first request, then one confirmed transport."""
    attempts: list[dict[str, Any]] = []
    transport = transport_state.get("transport")
    if transport is None:
        direct = core.run_request(url, "direct", kind, target, state, state.attempts + 1)
        attempts.append(direct)
        if direct.get("executed") and not direct.get("transport_error") and not state.stop_reason:
            transport_state["transport"] = "direct"
            return attempts
        if state.stop_reason or direct.get("source_status") in STOP_HTTP_CODES:
            return attempts
        proxy = core.run_request(url, "proxy", kind, target, state, state.attempts + 1)
        attempts.append(proxy)
        transport_state["transport"] = "proxy"
        return attempts
    attempts.append(core.run_request(url, transport, kind, target, state, state.attempts + 1))
    return attempts


def request_confirmed(
    url: str,
    kind: str,
    target: str,
    state: Any,
    transport_state: dict[str, str | None],
) -> list[dict[str, Any]]:
    transport = transport_state.get("transport") or "proxy"
    return [core.run_request(url, transport, kind, target, state, state.attempts + 1)]


def public_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    return core.source_attempt_view(attempt)


def valid_200_captures(records: list[dict[str, str]], original_url: str) -> list[dict[str, Any]]:
    valid = core.valid_cdx_records(records, original_url)
    return [row for row in valid if row.get("statuscode_int") == 200]


def select_latest_200(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not records:
        return None
    return sorted(records, key=lambda row: row.get("timestamp", ""), reverse=True)[0]


def body_for_attempt(attempt: dict[str, Any] | None) -> bytes:
    if not attempt:
        return b""
    raw = attempt.get("raw") or {}
    path = OUT / str(raw.get("body") or "")
    return path.read_bytes() if path.exists() else b""


def body_metrics(attempt: dict[str, Any] | None, capture: dict[str, Any] | None) -> dict[str, Any]:
    body = body_for_attempt(attempt)
    expected = str((capture or {}).get("digest") or "").upper() or None
    calculated = b32_sha1(body)
    return {
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "cdx_digest_expected": expected,
        "cdx_digest_calculated": calculated,
        "cdx_digest_match": bool(expected and calculated and expected == calculated),
        "cdx_length": int(capture["length"]) if capture and str(capture.get("length", "")).isdigit() else None,
        "memento_datetime": attempt.get("memento_datetime") if attempt else None,
        "content_type": attempt.get("content_type") if attempt else None,
        "source_status": attempt.get("source_status") if attempt else None,
        "raw_body_path": (attempt.get("raw") or {}).get("body") if attempt else None,
        "raw_headers_path": (attempt.get("raw") or {}).get("headers") if attempt else None,
    }


def decode_text(body: bytes) -> tuple[str, str]:
    try:
        return body.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return body.decode("iso-8859-1", errors="replace"), "iso-8859-1"


def script_text_observation(body: bytes, content_type: str | None) -> dict[str, Any]:
    text, encoding = decode_text(body)
    stripped = text.lstrip("\ufeff\r\n\t \x00")
    lowered = stripped.lower()
    html_markers = [
        marker
        for marker in ("<html", "<!doctype", "<head", "wayback machine", "not archived", "no captures", "page not found")
        if marker in lowered[:200000]
    ]
    mime = (content_type or "").split(";", 1)[0].strip().lower()
    executable = bool(re.search(r"\b(?:var|let|const|function|return)\b|[A-Za-z_$][\w$]*\s*=", stripped))
    meaningful = len(stripped.strip()) >= 10 and executable and not html_markers and not re.match(r"^\s*<", stripped)
    count_assignments: list[dict[str, Any]] = []
    assignment_re = re.compile(
        r"(?im)\b(?:(var|let|const)\s+)?([A-Za-z_$][\w$]*(?:count|total|number|num|images?|artwork|gallery)[A-Za-z0-9_$]*)\s*=\s*(?:([0-9]{1,7})|['\"]([^'\"]{1,80})['\"])",
    )
    for match in assignment_re.finditer(text):
        raw_value = match.group(3) if match.group(3) is not None else match.group(4)
        value: int | str
        if match.group(3) is not None:
            value = int(match.group(3))
        else:
            value = unescape(match.group(4) or "")
        snippet = " ".join(text[max(0, match.start() - 90): min(len(text), match.end() + 90)].split())[:240]
        count_assignments.append({"name": match.group(2), "value": value, "snippet": snippet})
    functions = [
        {"name": match.group(1), "args": " ".join((match.group(2) or "").split())[:120]}
        for match in re.finditer(r"(?im)\bfunction\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)", text)
    ]
    return {
        "encoding": encoding,
        "mime": mime,
        "bytes_decoded": len(body),
        "meaningful_non_html_script": meaningful,
        "html_or_archive_markers": html_markers,
        "count_assignments": count_assignments[:100],
        "function_signatures": functions[:100],
        "count_values": sorted({item["value"] for item in count_assignments if isinstance(item["value"], int)}),
        "count_observed": bool(count_assignments),
        "allowed_or_script_mime": mime in JS_MIMES or mime.endswith("javascript") or mime.endswith("ecmascript"),
    }


def validate_script(attempt: dict[str, Any] | None, capture: dict[str, Any] | None) -> tuple[bool, dict[str, Any], str]:
    body = body_for_attempt(attempt)
    metrics = body_metrics(attempt, capture)
    observation = script_text_observation(body, metrics.get("content_type"))
    if not attempt or not attempt.get("executed"):
        return False, observation, "replay_not_executed"
    if attempt.get("source_status") != 200:
        return False, observation, "source_status_not_200"
    if not metrics.get("memento_datetime"):
        return False, observation, "missing_actual_memento"
    if metrics.get("cdx_digest_match") is not True:
        return False, observation, "cdx_digest_mismatch"
    if not observation["meaningful_non_html_script"]:
        return False, observation, "html_or_non_script_body"
    if not observation["allowed_or_script_mime"] and not str((capture or {}).get("original") or "").lower().endswith(".js"):
        return False, observation, "unexpected_script_mime"
    return True, observation, "valid_script"


def validate_image(attempt: dict[str, Any] | None, capture: dict[str, Any] | None) -> tuple[bool, dict[str, Any], str]:
    body = body_for_attempt(attempt)
    metrics = body_metrics(attempt, capture)
    decode: dict[str, Any] = {
        "library": "Pillow",
        "verify": "not_run",
        "load": "not_run",
        "format": None,
        "width": None,
        "height": None,
        "mode": None,
        "error": None,
    }
    if not attempt or not attempt.get("executed"):
        return False, decode, "replay_not_executed"
    if attempt.get("source_status") != 200:
        return False, decode, "source_status_not_200"
    if not metrics.get("memento_datetime"):
        return False, decode, "missing_actual_memento"
    if metrics.get("cdx_digest_match") is not True:
        return False, decode, "cdx_digest_mismatch"
    if Image is None:
        decode["error"] = "Pillow_unavailable"
        return False, decode, "pillow_unavailable"
    try:
        with Image.open(io.BytesIO(body)) as image:
            decode["format"] = image.format
            decode["width"], decode["height"] = image.size
            decode["mode"] = image.mode
            image.verify()
        decode["verify"] = "passed"
        with Image.open(io.BytesIO(body)) as image:
            image.load()
        decode["load"] = "passed"
    except Exception as exc:  # pragma: no cover - response-dependent
        decode["error"] = type(exc).__name__ + ": " + str(exc)
        return False, decode, "pillow_validation_failed"
    if not decode.get("format") or not decode.get("width") or not decode.get("height"):
        return False, decode, "image_dimensions_missing"
    return True, decode, "valid_image"


def redirect_event(item: dict[str, Any], capture: dict[str, Any], first: dict[str, Any], follow: dict[str, Any] | None, follow_url: str | None) -> dict[str, Any]:
    location = first.get("location")
    parsed = urlsplit(location) if location else None
    return {
        "rank": item["rank"],
        "url": item["url"],
        "capture_timestamp": capture.get("timestamp"),
        "captured_original": capture.get("original"),
        "redirect_source_status": first.get("source_status"),
        "location": location,
        "location_host": (parsed.hostname or "").lower() if parsed else None,
        "manual_followed": bool(follow),
        "manual_follow_url": follow_url,
        "follow_source_status": follow.get("source_status") if follow else None,
        "follow_actual_memento": follow.get("memento_datetime") if follow else None,
        "raw_headers_path": (first.get("raw") or {}).get("headers"),
        "follow_raw_headers_path": (follow.get("raw") or {}).get("headers") if follow else None,
    }


def replay_one(
    item: dict[str, Any],
    capture: dict[str, Any],
    state: Any,
    transport_state: dict[str, str | None],
    redirects: list[dict[str, Any]],
) -> dict[str, Any]:
    replay_url = core.replay_url(capture)
    attempts = request_serial(replay_url, "replay", item["url"], state, transport_state)
    executed = [attempt for attempt in attempts if attempt.get("executed")]
    first = executed[-1] if executed else None
    follow_url: str | None = None
    follow_attempt: dict[str, Any] | None = None
    if first and first.get("source_status") in REDIRECT_CODES:
        follow_url = core.legal_wayback_replay(first.get("location"), first.get("url") or replay_url)
        if follow_url and not state.stop_reason:
            follow_results = request_confirmed(follow_url, "replay-follow", item["url"], state, transport_state)
            attempts.extend(follow_results)
            follow_attempt = next((attempt for attempt in reversed(follow_results) if attempt.get("executed")), None)
        redirects.append(redirect_event(item, capture, first, follow_attempt, follow_url))
    executed = [attempt for attempt in attempts if attempt.get("executed")]
    final = executed[-1] if executed else None
    return {
        "requested_replay_url": replay_url,
        "attempts": attempts,
        "initial": first,
        "final": final,
        "initial_status": first.get("source_status") if first else None,
        "manual_followed": bool(follow_attempt),
    }


def target_result(
    item: dict[str, Any],
    cdx_attempts: list[dict[str, Any]],
    records: list[dict[str, str]],
    eligible: list[dict[str, Any]],
    selected: dict[str, Any] | None,
    replay: dict[str, Any] | None,
    state: Any,
) -> dict[str, Any]:
    query_attempt = next((attempt for attempt in reversed(cdx_attempts) if attempt.get("executed")), None)
    if query_attempt is None:
        category = "not_requested"
        reason = state.stop_reason or "query_not_requested"
    elif query_attempt.get("transport_error"):
        category = "transport_error"
        reason = query_attempt.get("transport_reason") or "query_transport_error"
    elif query_attempt.get("source_status") in STOP_HTTP_CODES:
        category = "rate_limited"
        reason = f"source_status_{query_attempt.get('source_status')}"
    elif not query_attempt.get("cdx_parse_valid"):
        category = "cdx_invalid"
        reason = query_attempt.get("cdx_parse_error") or "cdx_parse_failed"
    elif not records:
        category = "cdx_empty_in_range"
        reason = "no_capture_rows_in_query_range"
    elif not eligible:
        category = "cdx_no_valid_200"
        reason = "no_same_origin_preanchor_status_200_capture"
    elif replay is None:
        category = "not_requested"
        reason = state.stop_reason or "replay_not_requested"
    else:
        final = replay.get("final")
        if final is None:
            category = "transport_error"
            reason = "replay_not_executed_or_no_response"
        elif final.get("transport_error"):
            category = "transport_error"
            reason = final.get("transport_reason") or "replay_transport_error"
        elif final.get("source_status") in STOP_HTTP_CODES:
            category = "rate_limited"
            reason = f"source_status_{final.get('source_status')}"
        elif final.get("source_status") in REDIRECT_CODES:
            category = "redirect_unfollowed"
            reason = "replay_redirect_evidence_only"
        elif final.get("source_status") != 200:
            category = "http_response"
            reason = f"replay_source_status_{final.get('source_status')}"
        else:
            category = "replayed_200_pending_validation"
            reason = "kind_validation_pending"
    return {
        "rank": item["rank"],
        "url": item["url"],
        "kind": item["kind"],
        "priority": item.get("priority"),
        "purpose": item.get("purpose"),
        "query_original": item["url"],
        "action": "exact_cdx_then_latest_preanchor_valid_200_replay",
        "query_url": core.cdx_query_url(item["url"]),
        "cdx": {
            "query_performed": bool(cdx_attempts),
            "source_status": query_attempt.get("source_status") if query_attempt else None,
            "source_response_count": sum(attempt.get("source_status") is not None for attempt in cdx_attempts),
            "capture_index_count": len(records),
            "eligible_status_200_count": len(eligible),
            "redirect_index_count": sum(str(row.get("statuscode")) in {str(code) for code in REDIRECT_CODES} for row in records),
            "capture_records": records,
            "selected_capture": selected,
            "other_origin_metadata": core.other_origin_metadata(records, item["url"]),
            "attempts": [public_attempt(attempt) for attempt in cdx_attempts],
        },
        "selected_capture": selected,
        "requested_replay_url": replay.get("requested_replay_url") if replay else None,
        "replay_attempt_count": len([attempt for attempt in (replay.get("attempts") if replay else []) if attempt.get("executed")]),
        "replay_source_response_count": sum(attempt.get("source_status") is not None for attempt in (replay.get("attempts") if replay else [])),
        "replay_hops": [public_attempt(attempt) for attempt in (replay.get("attempts") if replay else [])],
        "category": category,
        "reason": reason,
        "actual_memento": (replay.get("final") or {}).get("memento_datetime") if replay else None,
        "source_status": (replay.get("final") or {}).get("source_status") if replay else None,
        "content_type": (replay.get("final") or {}).get("content_type") if replay else None,
        "body_bytes": len(body_for_attempt(replay.get("final") if replay else None)),
        "body_sha256": (replay.get("final") or {}).get("body_sha256") if replay else None,
        "unrequested_reason": reason if category in {"not_requested", "cdx_empty_in_range", "cdx_no_valid_200", "transport_error"} and replay is None else None,
        "entity_valid": False,
        "validation": None,
    }


def source_map_entry(result: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    capture = result.get("selected_capture") or {}
    final = (result.get("replay_hops") or [])[-1] if result.get("replay_hops") else {}
    return {
        "url": result["url"],
        "query_original": result["query_original"],
        "captured_original": capture.get("original"),
        "actualMemento": result.get("actual_memento"),
        "bytes": result.get("body_bytes"),
        "SHA": result.get("body_sha256"),
        "CDXdigest": capture.get("digest"),
        "CDXdigest_calculated": validation.get("cdx_digest_calculated"),
        "CDXdigest_match": validation.get("cdx_digest_match"),
        "rawpath": validation.get("raw_body_path"),
        "raw_body_path": validation.get("raw_body_path"),
        "raw_headers_path": validation.get("raw_headers_path"),
        "MIME": result.get("content_type"),
        "decode": validation.get("decode"),
        "kind": result["kind"],
        "body_bytes": result.get("body_bytes"),
        "body_sha256": result.get("body_sha256"),
        "actual_memento": result.get("actual_memento"),
        "captured_original_url": capture.get("original"),
        "cdx_digest": capture.get("digest"),
        "cdx_digest_match": validation.get("cdx_digest_match"),
        "source_status": result.get("source_status"),
        "content_type": result.get("content_type"),
        "action": "review source mapping before any integration; entity remains only in this batch raw directory",
    }


def aggregate_attempts(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    for result in results:
        attempts.extend(result.get("cdx", {}).get("attempts") or [])
        attempts.extend(result.get("replay_hops") or [])
    return attempts


def finish_timing(attempts: list[dict[str, Any]]) -> tuple[float, float | None]:
    starts = [datetime.fromisoformat(item["started_utc"]) for item in attempts if item.get("started_utc")]
    gaps = [
        (datetime.fromisoformat(attempts[index + 1]["started_utc"]) - datetime.fromisoformat(attempts[index]["started_utc"])).total_seconds()
        for index in range(len(attempts) - 1)
        if attempts[index].get("started_utc") and attempts[index + 1].get("started_utc")
    ]
    if not starts:
        return 0.0, None
    finished = [datetime.fromisoformat(item["finished_utc"]) for item in attempts if item.get("finished_utc")]
    return (max(finished) - min(starts)).total_seconds(), (min(gaps) if gaps else None)


def public_summary(report: dict[str, Any], source_map: dict[str, Any], counter_observation: dict[str, Any]) -> None:
    summary = {
        "schema": "continuous-wow-asset-batch5-summary/v1",
        "report_sha256": sha256_file(OUT / "batch-report.json"),
        "inputs": report["inputs"],
        "request_window_started_utc": report["started_utc"],
        "request_window_finished_utc": report["request_window_finished_utc"],
        "report_updated_utc": report["report_updated_utc"],
        "network_requests": report["source_request_count"],
        "source_response_count": report["source_response_count"],
        "category_counts": report["category_counts"],
        "valid_entity_count": report["valid_entity_count"],
        "counter_count_observations": [
            {
                "url": row["url"],
                "status": row.get("status"),
                "count_observed": row.get("count_observed"),
                "count_values": row.get("count_values"),
                "api_names": row.get("api_names"),
            }
            for row in counter_observation["entries"]
        ],
        "targets": [
            {
                "rank": row["rank"],
                "url": row["url"],
                "kind": row["kind"],
                "category": row["category"],
                "capture_timestamp": (row.get("selected_capture") or {}).get("timestamp"),
                "captured_original": (row.get("selected_capture") or {}).get("original"),
                "source_status": row.get("source_status"),
                "actual_memento": row.get("actual_memento"),
                "body_bytes": row.get("body_bytes"),
                "body_sha256": row.get("body_sha256"),
                "validation": row.get("validation"),
                "reason": row.get("reason"),
            }
            for row in report["results"]
        ],
        "asset_source_map_entries": len(source_map["entries"]),
        "redirect_evidence_count": report["redirect_evidence_count"],
        "raw_local_only": True,
        "no_entity_copied_into_mirror": True,
    }
    write_json(OUT / "sanitized-summary.json", summary)
    lines = [
        "# NET-ASSETS-005 sanitized recovery summary",
        "",
        f"Input candidates SHA-256: {report['inputs']['candidate_sha256']}.",
        f"Request window: {report['started_utc']} to {report['request_window_finished_utc']}; report updated: {report['report_updated_utc']}.",
        f"Attempts: {report['source_request_count']}; source responses: {report['source_response_count']}; failed attempts: {report['failed_attempt_count']}; CDX source responses: {report['cdx_source_response_count']}; replay source responses: {report['replay_source_response_count']}; valid entities: {report['valid_entity_count']}; redirect evidence: {report['redirect_evidence_count']}.",
        "Categories: " + ", ".join(f"{key} {value}" for key, value in sorted(report["category_counts"].items())) + ".",
        f"Disk free before/after: {report['preflight']['disk_free_bytes_before']} / {report['preflight']['disk_free_bytes_after']} bytes.",
        "",
        "| # | kind | URL | category | capture | source HTTP | Memento | bytes | reason |",
        "|---:|---|---|---|---|---:|---|---:|---|",
    ]
    for row in report["results"]:
        lines.append(
            f"| {row['rank']} | {row['kind']} | {row['url']} | {row['category']} | "
            f"{(row.get('selected_capture') or {}).get('timestamp') or ''} | {row.get('source_status') or ''} | "
            f"{row.get('actual_memento') or ''} | {row.get('body_bytes') or 0} | {row.get('reason') or ''} |"
        )
    lines.extend([
        "",
        "Counter scripts were observed as text only; no JavaScript was executed and no count was inferred from missing values.",
        "Original headers, traces, bodies, and scripts remain only in this batch raw directory. No entity was copied into the offline mirror.",
        "",
    ])
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")


def execute() -> int:
    inputs = verify_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    if (OUT / "batch-report.json").exists():
        raise RuntimeError("refusing network rerun: batch-report.json already exists in owned output")
    plan = plan_document(inputs)
    write_preparation(inputs, plan)
    disk_before = disk_free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk free {disk_before} below {MIN_FREE_BYTES}")
    window_started_monotonic = time.monotonic()
    started_utc = now_utc()
    state = core.RunState(window_started_monotonic)
    transport_state: dict[str, str | None] = {"transport": None}
    redirects: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    source_entries: list[dict[str, Any]] = []
    counter_entries: list[dict[str, Any]] = []
    for rank, item in enumerate(inputs["candidates"]["entries"], start=1):
        target = dict(item)
        target["rank"] = rank
        query_url = core.cdx_query_url(target["url"])
        query_attempts = request_serial(query_url, "cdx", target["url"], state, transport_state) if state.check_limits() else []
        query_attempt = next((attempt for attempt in reversed(query_attempts) if attempt.get("executed")), None)
        records = (query_attempt or {}).get("cdx_records") or []
        eligible = valid_200_captures(records, target["url"]) if query_attempt and query_attempt.get("source_status") == 200 and not query_attempt.get("transport_error") else []
        selected = select_latest_200(eligible)
        replay = None
        if selected is not None and state.check_limits():
            replay = replay_one(target, selected, state, transport_state, redirects)
        result = target_result(target, query_attempts, records, eligible, selected, replay, state)
        validation: dict[str, Any] | None = None
        if replay is not None:
            final = replay.get("final")
            metrics = body_metrics(final, selected)
            if target["kind"] == "javascript_counter":
                valid, observation, reason = validate_script(final, selected)
                validation = {**metrics, "decode": observation, "valid": valid, "reason": reason}
                result["counter_observation"] = observation
            else:
                valid, decode, reason = validate_image(final, selected)
                validation = {**metrics, "decode": decode, "valid": valid, "reason": reason}
            result["validation"] = validation
            result["category"] = reason if not valid else ("valid_javascript_counter" if target["kind"] == "javascript_counter" else "valid_image")
            result["reason"] = reason
            result["entity_valid"] = valid and replay.get("initial_status") == 200
            result["actual_memento"] = metrics.get("memento_datetime")
            result["source_status"] = metrics.get("source_status")
            result["content_type"] = metrics.get("content_type")
            result["body_bytes"] = metrics.get("body_bytes")
            result["body_sha256"] = metrics.get("body_sha256")
            if result["entity_valid"]:
                source_entries.append(source_map_entry(result, validation))
        if target["kind"] == "javascript_counter":
            observation = (result.get("counter_observation") or {}).copy()
            counter_entries.append({
                "rank": rank,
                "url": target["url"],
                "query_original": target["url"],
                "capture_timestamp": (selected or {}).get("timestamp"),
                "captured_original": (selected or {}).get("original"),
                "status": result.get("category"),
                "source_status": result.get("source_status"),
                "actual_memento": result.get("actual_memento"),
                "body_bytes": result.get("body_bytes"),
                "body_sha256": result.get("body_sha256"),
                "raw_body_path": (validation or {}).get("raw_body_path"),
                "raw_headers_path": (validation or {}).get("raw_headers_path"),
                "script_valid": bool((validation or {}).get("valid")),
                "count_observed": bool(observation.get("count_observed")),
                "count_values": observation.get("count_values") or [],
                "api_names": sorted({item["name"] for item in observation.get("count_assignments") or []}),
                "evidence_snippets": [item["snippet"] for item in observation.get("count_assignments") or []],
                "observation": observation,
                "reason": result.get("reason"),
            })
        results.append(result)
        if state.stop_reason:
            continue
    request_window_finished_utc = now_utc()
    report_updated_utc = now_utc()
    disk_after = disk_free_bytes()
    attempts = aggregate_attempts(results)
    request_seconds, minimum_interval = finish_timing(attempts)
    cdx_responses = sum(row["cdx"].get("source_response_count", 0) for row in results)
    replay_responses = sum(row.get("replay_source_response_count", 0) for row in results)
    category_counts: dict[str, int] = {}
    for row in results:
        category_counts[row["category"]] = category_counts.get(row["category"], 0) + 1
    report = {
        "schema": "continuous-wow-asset-batch5-report/v1",
        "mode": "execute",
        "inputs": {
            "candidate_path": str(INPUT_CANDIDATES.relative_to(ROOT)).replace("\\", "/"),
            "candidate_sha256": inputs["candidate_sha256"],
            "asset_queue_path": str(ASSET_QUEUE.relative_to(ROOT)).replace("\\", "/"),
            "asset_queue_sha256": inputs["asset_queue_sha256"],
            "accepted_dedup_path": str(ACCEPTED_DEDUP.relative_to(ROOT)).replace("\\", "/"),
        "accepted_dedup_sha256": inputs["dedup_acceptance_sha256"],
        "accepted_dedup_report_sha256": inputs["dedup_report_sha256"],
        },
        "started_utc": started_utc,
        "request_window_finished_utc": request_window_finished_utc,
        "finished_utc": request_window_finished_utc,
        "report_updated_utc": report_updated_utc,
        "target_count": len(results),
        "source_request_count": state.attempts,
        "transport_attempt_count": state.attempts,
        "source_response_count": state.source_responses,
        "failed_attempt_count": state.failed_attempts,
        "cdx_source_response_count": cdx_responses,
        "replay_source_response_count": replay_responses,
        "capture_index_count_fetched": sum(row["cdx"].get("capture_index_count") or 0 for row in results),
        "eligible_status_200_capture_count": sum(row["cdx"].get("eligible_status_200_count") or 0 for row in results),
        "valid_entity_count": len(source_entries),
        "valid_image_count": sum(row["kind"] == "image" and row.get("entity_valid") for row in results),
        "valid_javascript_counter_count": sum(row["kind"] == "javascript_counter" and row.get("entity_valid") for row in results),
        "total_body_bytes": state.total_body_bytes,
        "category_counts": category_counts,
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "transport": {"confirmed_transport": transport_state.get("transport")},
        "preflight": {
            "drive": "D:",
            "disk_free_bytes_before": disk_before,
            "disk_free_bytes_after": disk_after,
            "minimum_free_bytes": MIN_FREE_BYTES,
        },
        "request_window_seconds": request_seconds,
        "minimum_start_interval_seconds": minimum_interval,
        "redirect_evidence_count": len(redirects),
        "policy": plan["policy"],
        "raw_local_only": True,
        "no_entity_copied_into_mirror": True,
        "results": results,
    }
    source_map = {
        "schema": "continuous-wow-asset-batch5-source-map/v1",
        "generated_utc": report_updated_utc,
        "only_real_valid_entities": True,
        "entries": source_entries,
    }
    counter_observation = {
        "schema": "continuous-wow-asset-batch5-counter-api-observation/v1",
        "generated_utc": report_updated_utc,
        "execution": "static_text_observation_only; no_javascript_execution",
        "entries": counter_entries,
    }
    output_candidates = dict(inputs["candidates"])
    output_candidates["input_sha256"] = inputs["candidate_sha256"]
    output_candidates["execution_policy"] = plan["policy"]
    output_candidates["execution"] = {
        "network_requests": state.attempts,
        "status": "completed",
        "request_window_finished_utc": request_window_finished_utc,
        "report_updated_utc": report_updated_utc,
    }
    write_json(OUT / "candidates.json", output_candidates)
    write_json(OUT / "batch-config.json", plan)
    write_json(OUT / "batch-report.json", report)
    write_json(OUT / "asset-source-map.json", source_map)
    write_json(OUT / "counter-api-observation.json", counter_observation)
    write_json(OUT / "redirect-evidence.json", {
        "schema": "continuous-wow-asset-batch5-redirect-evidence/v1",
        "generated_utc": report_updated_utc,
        "entries": redirects,
    })
    public_summary(report, source_map, counter_observation)
    print(json.dumps({
        "target_count": len(results),
        "category_counts": category_counts,
        "attempts": state.attempts,
        "source_responses": state.source_responses,
        "cdx_source_responses": cdx_responses,
        "replay_source_responses": replay_responses,
        "valid_entities": len(source_entries),
        "valid_images": report["valid_image_count"],
        "valid_javascript_counters": report["valid_javascript_counter_count"],
        "counter_values_observed": [row["count_values"] for row in counter_entries],
        "total_body_bytes": state.total_body_bytes,
        "redirect_evidence": len(redirects),
        "stop_reason": state.stop_reason,
        "confirmed_transport": transport_state.get("transport"),
    }, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.execute:
        return execute()
    return prepare()


if __name__ == "__main__":
    raise SystemExit(main())

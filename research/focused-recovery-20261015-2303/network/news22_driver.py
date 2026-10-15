#!/usr/bin/env python3
"""NEWS22: one bounded pre-anchor recovery probe for the August 2007 news page.

The driver reuses the accepted core transport/header parser, control7 gate, and
RSS016 full-body date observer.  It owns only this batch directory.  The first
operation is the exact anchor replay; availability and one scoped CDX query
are fallback evidence only, with no automatic redirects or late-window work.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import re
import shutil
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlencode, urlsplit


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
CURL = Path(r"C:\Windows\System32\curl.exe")
PROXY = "http://127.0.0.1:7890"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
RSS16_PATH = ROOT / "research/continuous-recovery-20261015/network-rss16/rss16_driver.py"

BATCH_ID = "NEWS22-AUG2007-20261015"
TARGET = "http://www.worldofwarcraft.com/news/rss-08-2007.xml"
ANCHOR = "20080512210044"
SCOPED_FROM = "20070801"
RAW_REPLAY_URL = f"https://web.archive.org/web/{ANCHOR}id_/{TARGET}"
AVAILABILITY_URL = "https://archive.org/wayback/available?" + urlencode(
    {"url": TARGET, "timestamp": ANCHOR, "closest": "1"}
)
CDX_FIELDS = ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
CDX_URL = "https://web.archive.org/cdx/search/cdx?" + urlencode(
    {
        "url": TARGET,
        "from": SCOPED_FROM,
        "to": ANCHOR,
        "output": "json",
        "fl": ",".join(CDX_FIELDS),
        "limit": "50",
        "matchType": "exact",
    }
)

AUTH_START = datetime.fromisoformat("2026-10-15T15:03:05+00:00")
AUTH_END = datetime.fromisoformat("2026-10-15T15:43:05+00:00")
MAX_ATTEMPTS = 8
WINDOW_SECONDS = 360
MIN_DISPATCH_MONOTONIC = 5.1
MIN_REQUEST_START_UTC = 5.0
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY_BYTES = 16 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 2 * 1024 * 1024
DIRECT_CONNECT_SECONDS = 8
DIRECT_MAX_SECONDS = 60
PROXY_CONNECT_SECONDS = 8
PROXY_MAX_SECONDS = 60
STOP_HTTP_CODES = {429, 503}
USER_AGENT = "wow-recovery-news22/20261015"

PLAN = OUT / "news22-plan.json"
CANDIDATES = OUT / "candidates.json"
CONFIG = OUT / "config.json"
JOURNAL = OUT / "dispatch-journal.json"
REPORT = OUT / "batch-report.json"
SUMMARY_JSON = OUT / "sanitized-summary.json"
SUMMARY_MD = OUT / "sanitized-summary.md"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load local helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_module(CORE_PATH, "news22_core_pages3")
gate_mod = load_module(GATE_PATH, "news22_control7_gate")
rss16 = load_module(RSS16_PATH, "news22_rss16_observer")

core.OUT = OUT
core.RAW = RAW
core.PROXY = PROXY
core.USER_AGENT = USER_AGENT
core.FROM_TIMESTAMP = SCOPED_FROM
core.TO_TIMESTAMP = ANCHOR
core.CDX_COLUMNS = CDX_FIELDS
core.CDX_LIMIT = 50
core.MIN_INTERVAL_SECONDS = 0.0
core.MAX_ATTEMPTS = MAX_ATTEMPTS
core.WINDOW_SECONDS = WINDOW_SECONDS
core.MIN_FREE_BYTES = MIN_FREE_BYTES
core.MAX_TOTAL_BODY_BYTES = MAX_TOTAL_BODY_BYTES
core.MAX_ENTITY_BODY_BYTES = MAX_ENTITY_BODY_BYTES
core.DIRECT_CONNECT_SECONDS = DIRECT_CONNECT_SECONDS
core.DIRECT_MAX_SECONDS = DIRECT_MAX_SECONDS
core.PROXY_CONNECT_SECONDS = PROXY_CONNECT_SECONDS
core.PROXY_MAX_SECONDS = PROXY_MAX_SECONDS
gate_mod.OUT = OUT
gate_mod.RAW = RAW
gate_mod.INTERVAL_SECONDS = MIN_DISPATCH_MONOTONIC
gate_mod.MIN_FREE_BYTES = MIN_FREE_BYTES
gate_mod.MAX_TOTAL_BODY_BYTES = MAX_TOTAL_BODY_BYTES
gate_mod.MAX_ENTITY_BYTES = MAX_ENTITY_BODY_BYTES
rss16.OUT = OUT
rss16.RAW = RAW


def now_dt() -> datetime:
    return datetime.now(timezone.utc)


def now_utc() -> str:
    return now_dt().isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.resolve().relative_to(OUT.resolve()).as_posix()


def free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def digest(path: Path) -> dict[str, Any]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def body_for(attempt: dict[str, Any] | None) -> bytes:
    if not attempt or not attempt.get("executed"):
        return b""
    raw = attempt.get("raw") or {}
    value = str(raw.get("body") or "")
    if not value:
        return b""
    path = (OUT / value).resolve()
    if OUT.resolve() not in path.parents:
        raise RuntimeError("body path escaped NEWS22 directory")
    return path.read_bytes() if path.is_file() else b""


def prepare() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    disk = free_bytes()
    candidates = {
        "schema": "wow-recovery.news22-candidates.v1",
        "batch_id": BATCH_ID,
        "network_requests": 0,
        "target": {
            "rank": 1,
            "exact_original_url": TARGET,
            "target": "/news/rss-08-2007.xml",
            "raw_replay_url": RAW_REPLAY_URL,
            "availability_url": AVAILABILITY_URL,
            "cdx_url": CDX_URL,
            "scope": {"from": SCOPED_FROM, "to": ANCHOR, "limit": 50, "fields": CDX_FIELDS},
            "selection": "pre-anchor actual Memento; same scheme/host/path/query with default-port normalization only",
        },
        "source_evidence": {"prior_news21_category": "transport_error", "prior_cdx_rows": 0, "prior_source_status": None},
        "policy": {
            "direct_first_then_proxy": True,
            "max_attempts": MAX_ATTEMPTS,
            "window_seconds": WINDOW_SECONDS,
            "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
            "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
            "direct_connect_seconds": DIRECT_CONNECT_SECONDS,
            "direct_max_seconds": DIRECT_MAX_SECONDS,
            "proxy_connect_seconds": PROXY_CONNECT_SECONDS,
            "proxy_max_seconds": PROXY_MAX_SECONDS,
            "request_start_minimum_seconds": MIN_REQUEST_START_UTC,
            "dispatch_monotonic_minimum_seconds": MIN_DISPATCH_MONOTONIC,
            "disk_floor_bytes": MIN_FREE_BYTES,
            "automatic_redirects": 0,
            "manual_location_follows": 1,
            "late_windows": 0,
            "stop_http_codes": sorted(STOP_HTTP_CODES),
            "tls_verification": "curl default verification enabled",
        },
        "authorization_window": {"start_utc": AUTH_START.isoformat(), "end_utc": AUTH_END.isoformat()},
    }
    config = {
        "schema": "wow-recovery.news22-config.v1",
        "batch_id": BATCH_ID,
        "prepared_utc": now_utc(),
        "network_requests": 0,
        "curl": str(CURL),
        "proxy": PROXY,
        "candidates_sha256": None,
        "disk_free_bytes": disk,
        "policy": candidates["policy"],
    }
    write_json(CANDIDATES, candidates)
    config["candidates_sha256"] = sha256_file(CANDIDATES)
    write_json(CONFIG, config)
    plan = {
        "schema": "wow-recovery.news22-plan.v1",
        "mode": "plan_only",
        "batch_id": BATCH_ID,
        "prepared_utc": now_utc(),
        "network_requests": 0,
        "input": {"prior_target": TARGET, "prior_result": "NEWS21 transport_error; no prior source HTTP status"},
        "outputs": {"raw": rel(RAW), "journal": rel(JOURNAL), "report": rel(REPORT), "summary": rel(SUMMARY_JSON)},
        "disk_free_bytes": disk,
        "minimum_free_bytes": MIN_FREE_BYTES,
        "candidates_sha256": sha256_file(CANDIDATES),
        "config_sha256": sha256_file(CONFIG),
        "authorization_window": {"start_utc": AUTH_START.isoformat(), "end_utc": AUTH_END.isoformat()},
        "request_sequence": ["raw_replay", "manual_same_origin_location_at_most_once", "availability_at_most_once", "scoped_cdx_at_most_once"],
    }
    write_json(PLAN, plan)
    print(json.dumps({"mode": "prepared", "batch_id": BATCH_ID, "network_requests": 0, "target": TARGET, "disk_free_bytes": disk}, ensure_ascii=False))
    return 0


def can_dispatch(state: Any, window_started: float) -> tuple[bool, str | None]:
    now = now_dt()
    if now < AUTH_START:
        return False, "authorization_window_not_open"
    if now >= AUTH_END:
        return False, "authorization_window_closed"
    if state.attempts >= MAX_ATTEMPTS:
        return False, "attempt_limit"
    if time.monotonic() - window_started >= WINDOW_SECONDS:
        return False, "network_window_exhausted"
    if free_bytes() < MIN_FREE_BYTES:
        return False, "disk_free_below_threshold"
    if state.total_body_bytes >= MAX_TOTAL_BODY_BYTES:
        return False, "total_body_limit"
    return True, None


def wait_request_wall(last_started: datetime | None) -> None:
    if last_started is None:
        return
    while True:
        remaining = MIN_REQUEST_START_UTC - (now_dt() - last_started).total_seconds()
        if remaining <= 0:
            return
        time.sleep(min(60.0, max(remaining, 0.01)))


def dispatch_one(
    url: str,
    kind: str,
    label: str,
    transport: str,
    state: Any,
    gate: Any,
    window_started: float,
    last_started: datetime | None,
) -> tuple[dict[str, Any] | None, datetime | None]:
    ok, reason = can_dispatch(state, window_started)
    if not ok:
        state.stop_reason = reason
        state.stop_detail = {"authorization_or_limit": reason}
        return None, last_started
    wait_request_wall(last_started)
    ok, reason = can_dispatch(state, window_started)
    if not ok:
        state.stop_reason = reason
        state.stop_detail = {"authorization_or_limit": reason}
        return None, last_started
    attempt_number = state.attempts + 1
    gate_record = gate.before_dispatch(attempt_number, transport, label)
    # A monotonic gate record is persisted before transport; recheck wall time
    # and cutoff immediately before curl as a separate request-start guard.
    wait_request_wall(last_started)
    if now_dt() >= AUTH_END or free_bytes() < MIN_FREE_BYTES:
        gate_record["not_executed_reason"] = "cutoff_or_disk_before_curl"
        gate.persist()
        state.stop_reason = "cutoff_or_disk_before_curl"
        return None, last_started
    attempt = core.run_request(url, transport, kind, label, state, attempt_number)
    attempt["dispatch"] = gate_record
    gate_record["request_start_utc"] = attempt.get("started_utc")
    gate_record["finished_utc"] = attempt.get("finished_utc")
    gate_record["source_status"] = attempt.get("source_status")
    gate_record["curl_exit"] = attempt.get("curl_exit")
    gate_record["body_bytes"] = attempt.get("body_bytes")
    gate_record["transport_error"] = attempt.get("transport_error")
    gate.persist()
    started = parse_iso(attempt.get("started_utc")) or last_started
    return attempt, started


def request_pair(
    url: str,
    kind: str,
    label: str,
    state: Any,
    gate: Any,
    window_started: float,
    last_started: datetime | None,
) -> tuple[list[dict[str, Any]], datetime | None]:
    attempts: list[dict[str, Any]] = []
    for transport in ("direct", "proxy"):
        attempt, last_started = dispatch_one(url, kind, label, transport, state, gate, window_started, last_started)
        if attempt is None:
            break
        attempts.append(attempt)
        if not attempt.get("transport_error"):
            break
        if state.stop_reason:
            break
    return attempts, last_started


def candidate_from_availability(body: bytes) -> dict[str, Any] | None:
    try:
        data = json.loads(body.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    closest = (data.get("archived_snapshots") or {}).get("closest") if isinstance(data, dict) else None
    if not isinstance(closest, dict) or closest.get("available") is not True:
        return None
    timestamp = str(closest.get("timestamp") or "")
    original = str(closest.get("url") or TARGET)
    if not re.fullmatch(r"\d{14}", timestamp) or timestamp > ANCHOR:
        return None
    if core.normalized_url_identity(original) != core.normalized_url_identity(TARGET):
        return None
    return {
        "timestamp": timestamp,
        "original": original,
        "mimetype": None,
        "statuscode": str(closest.get("status") or "200"),
        "digest": None,
        "length": None,
        "provenance": "archive.org_wayback_available",
    }


def cdx_capture(body: bytes) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records, parse_valid, parse_error = core.parse_cdx_body(body)
    decorated = core.valid_cdx_records(records, TARGET) if parse_valid else []
    eligible = [r for r in decorated if r.get("statuscode_int") == 200]
    selected = core.select_capture(eligible)
    return decorated, {"parse_valid": parse_valid, "parse_error": parse_error, "selected": selected, "eligible_count": len(eligible)}


def cdx_digest(body: bytes) -> str:
    encoded = base64.b32encode(hashlib.sha1(body).digest()).decode("ascii").rstrip("=")
    return encoded


def validate_replay(attempt: dict[str, Any] | None, capture: dict[str, Any], provenance: str) -> tuple[str, str, dict[str, Any] | None]:
    if not attempt or not attempt.get("executed"):
        return "not_requested", "replay_not_executed", None
    status = attempt.get("source_status")
    if attempt.get("transport_error") or status is None:
        return "transport_error", attempt.get("transport_reason") or "no_source_http_response", None
    if status in STOP_HTTP_CODES:
        return "rate_limited", f"source_status_{status}", {"retry_after": attempt.get("retry_after")}
    if status in core.REDIRECT_CODES:
        return "redirect_unfollowed", f"source_status_{status}", {"location": attempt.get("location")}
    if status == 404:
        return "not_archived", "replay_http_404", None
    if status != 200:
        return "http_response", f"source_status_{status}", None
    body = body_for(attempt)
    memento = parse_iso(attempt.get("memento_datetime"))
    capture_dt = core.parse_timestamp(str(capture.get("timestamp") or ""))
    html = attempt.get("html") or core.html_info(body, attempt.get("content_type"))
    observation = {"title": html.get("title")}
    month = rss16.html_month_evidence(body, observation, 2007, 8)
    title = str(html.get("title") or "")
    title_ok = bool(re.search(r"August\s*,?\s*2007", title, re.I))
    posted = month.get("posted_date_evidence") or {}
    posted_ok = posted.get("state") == "match" and int(month.get("article_posted_date_count") or 0) > 0
    memento_ok = bool(memento and memento <= datetime.strptime(ANCHOR, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc))
    markers = set(html.get("markers") or [])
    soft = bool(markers.intersection({"wayback_machine", "not_archived", "no_captures", "page_not_found", "not_found", "error_404", "page_cannot_be_found"}))
    digest_expected = capture.get("digest")
    digest_actual = cdx_digest(body) if digest_expected else None
    validation = {
        "provenance": provenance,
        "body_format": "html" if html.get("is_html") else "other",
        "valid": bool(html.get("is_html") and title_ok and posted_ok and memento_ok and not soft),
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "source_status": status,
        "content_type": attempt.get("content_type"),
        "actual_memento": attempt.get("memento_datetime"),
        "actual_memento_at_or_before_anchor": memento_ok,
        "capture_timestamp": capture.get("timestamp"),
        "cdx_digest_expected": digest_expected,
        "cdx_digest_calculated": digest_actual,
        "cdx_digest_match": bool(digest_expected and digest_actual == digest_expected),
        "cdx_digest_unavailable": digest_expected is None,
        "title": title,
        "title_matches_august_2007": title_ok,
        "h1_count": month.get("h1_count"),
        "posted_date_count": month.get("article_posted_date_count"),
        "posted_date_month_counts": month.get("article_posted_date_month_counts"),
        "posted_date_range": month.get("article_posted_date_range"),
        "posted_date_evidence": posted,
        "event_date_evidence": month.get("event_date_evidence"),
        "soft404_markers": sorted(markers),
        "raw_body_path": (attempt.get("raw") or {}).get("body"),
        "raw_headers_path": (attempt.get("raw") or {}).get("headers"),
    }
    if validation["valid"]:
        return "valid_html_payload", "title_and_full_posted_date_evidence_match", validation
    if soft:
        return "soft404", "archive_error_marker_or_wayback_page", validation
    return "content_mismatch", "html_observed_but_title_or_posted_month_failed", validation


def legal_location(location: str | None, base_url: str) -> str | None:
    candidate = core.legal_wayback_replay(location, base_url)
    if not candidate:
        return None
    parts = urlsplit(candidate)
    match = re.match(r"^/web/(\d{14})(?:id_)?/(.*)$", parts.path)
    if not match:
        return None
    timestamp, encoded_original = match.groups()
    original = unquote(encoded_original)
    if timestamp > ANCHOR or core.normalized_url_identity(original) != core.normalized_url_identity(TARGET):
        return None
    return candidate


def public_attempt(value: dict[str, Any]) -> dict[str, Any]:
    return core.source_attempt_view(value)


def sanitize_attempts(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [public_attempt(a) for a in attempts]


def write_summary(report: dict[str, Any]) -> None:
    summary = {
        "schema": "wow-recovery.news22-sanitized-summary.v1",
        "batch_id": BATCH_ID,
        "mode": report.get("mode"),
        "authorization_window": report.get("authorization_window"),
        "started_utc": report.get("started_utc"),
        "finished_utc": report.get("finished_utc"),
        "attempt_count": report.get("attempt_count"),
        "source_response_count": report.get("source_response_count"),
        "failed_attempt_count": report.get("failed_attempt_count"),
        "total_body_bytes": report.get("total_body_bytes"),
        "payload_body_bytes": report.get("payload_body_bytes"),
        "category": report.get("category"),
        "stop_reason": report.get("stop_reason"),
        "actual_memento": report.get("actual_memento"),
        "source_status": report.get("source_status"),
        "content_type": report.get("content_type"),
        "body_bytes": report.get("body_bytes"),
        "body_sha256": report.get("body_sha256"),
        "validation": report.get("validation"),
        "cdx": report.get("cdx"),
        "availability": report.get("availability"),
        "disk_preflight": report.get("disk_preflight"),
        "disk_postflight": report.get("disk_postflight"),
        "cadence": report.get("cadence"),
        "raw_evidence_note": "Raw headers, traces, stderr and bodies remain local. CONNECT status is excluded from source_response_count; no CDX digest is claimed for direct replay unless a fallback CDX row supplied one.",
    }
    write_json(SUMMARY_JSON, summary)
    lines = [
        "# NEWS22 sanitized summary",
        f"- Target: `{TARGET}`",
        f"- Window: `{report.get('started_utc')}` to `{report.get('finished_utc')}`; attempts `{report.get('attempt_count')}`, source HTTP responses `{report.get('source_response_count')}`.",
        f"- Category: `{report.get('category')}`; stop `{report.get('stop_reason')}`; payload bytes `{report.get('payload_body_bytes')}`.",
        f"- Actual Memento: `{report.get('actual_memento')}`; source status `{report.get('source_status')}`; body SHA256 `{report.get('body_sha256')}`.",
        "- Direct replay was attempted before the existing proxy; no automatic redirect or late window was used.",
        "- Raw headers, traces, stderr and bodies remain local; no entity was copied into v14 or exported.",
    ]
    write_text = SUMMARY_MD.write_text
    write_text("\n".join(lines) + "\n", encoding="utf-8")


def execute() -> int:
    if REPORT.exists():
        raise SystemExit("refusing to overwrite existing NEWS22 report")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    disk_before = free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise SystemExit("disk_free_below_threshold_before_dispatch")
    started_utc = now_utc()
    window_started = time.monotonic()
    state = core.RunState(window_started)
    journal: dict[str, Any] = {
        "schema": "wow-recovery.news22-dispatch-journal.v1",
        "batch_id": BATCH_ID,
        "simulation": False,
        "authorization_window": {"start_utc": AUTH_START.isoformat(), "end_utc": AUTH_END.isoformat()},
        "policy": {"max_attempts": MAX_ATTEMPTS, "min_dispatch_monotonic_seconds": MIN_DISPATCH_MONOTONIC, "min_request_start_utc_seconds": MIN_REQUEST_START_UTC, "disk_floor_bytes": MIN_FREE_BYTES},
        "disk_preflight": {"checked_utc": started_utc, "disk_free_bytes": disk_before, "minimum_free_bytes": MIN_FREE_BYTES},
        "dispatches": [],
    }
    write_json(JOURNAL, journal)
    gate = gate_mod.GateState(AUTH_START, journal_path=JOURNAL, journal=journal)
    last_started: datetime | None = None
    all_attempts: list[dict[str, Any]] = []
    operation_log: list[dict[str, Any]] = []
    final_attempt: dict[str, Any] | None = None
    final_capture: dict[str, Any] = {"timestamp": ANCHOR, "original": TARGET, "digest": None, "provenance": "anchor_raw_replay"}
    final_provenance = "anchor_raw_replay"
    category = "unknown"
    reason = "no_request"
    validation: dict[str, Any] | None = None
    cdx_info: dict[str, Any] | None = None
    availability_info: dict[str, Any] | None = None
    try:
        replay_attempts, last_started = request_pair(RAW_REPLAY_URL, "replay", "anchor-raw-replay", state, gate, window_started, last_started)
        all_attempts.extend(replay_attempts)
        operation_log.append({"operation": "anchor_raw_replay", "url": RAW_REPLAY_URL, "attempts": sanitize_attempts(replay_attempts)})
        final_attempt = replay_attempts[-1] if replay_attempts else None
        category, reason, validation = validate_replay(final_attempt, final_capture, final_provenance)
        if category == "valid_html_payload":
            pass
        else:
            # A source 3xx gets at most one legal same-origin Wayback follow.
            location_url = legal_location((final_attempt or {}).get("location"), RAW_REPLAY_URL)
            if location_url and final_attempt and not final_attempt.get("transport_error"):
                follow_attempt, last_started = dispatch_one(location_url, "manual-location", "manual-location", final_attempt.get("transport") or "proxy", state, gate, window_started, last_started)
                if follow_attempt:
                    all_attempts.append(follow_attempt)
                    operation_log.append({"operation": "manual_location_follow", "url": location_url, "attempts": [public_attempt(follow_attempt)]})
                    final_attempt = follow_attempt
                    follow_capture = dict(final_capture)
                    match = re.search(r"/web/(\d{14})", location_url)
                    if match:
                        follow_capture["timestamp"] = match.group(1)
                    category, reason, validation = validate_replay(final_attempt, follow_capture, "manual_same_origin_location")
                    if category == "valid_html_payload":
                        final_capture = follow_capture
                        final_provenance = "manual_same_origin_location"
            if category != "valid_html_payload" and not state.stop_reason:
                availability_attempts, last_started = request_pair(AVAILABILITY_URL, "availability", "availability", state, gate, window_started, last_started)
                all_attempts.extend(availability_attempts)
                operation_log.append({"operation": "availability", "url": AVAILABILITY_URL, "attempts": sanitize_attempts(availability_attempts)})
                availability_final = availability_attempts[-1] if availability_attempts else None
                availability_candidate = candidate_from_availability(body_for(availability_final)) if availability_final and availability_final.get("source_status") == 200 and not availability_final.get("transport_error") else None
                availability_info = {"source_status": availability_final.get("source_status") if availability_final else None, "candidate": availability_candidate, "body_bytes": len(body_for(availability_final)) if availability_final else 0}
                if availability_candidate and not state.stop_reason:
                    final_capture = availability_candidate
                    final_provenance = "archive.org_wayback_available"
                    availability_replay_url = core.replay_url(availability_candidate)
                    av_replay_attempts, last_started = request_pair(availability_replay_url, "replay", "availability-replay", state, gate, window_started, last_started)
                    all_attempts.extend(av_replay_attempts)
                    operation_log.append({"operation": "availability_replay", "url": availability_replay_url, "attempts": sanitize_attempts(av_replay_attempts)})
                    final_attempt = av_replay_attempts[-1] if av_replay_attempts else None
                    category, reason, validation = validate_replay(final_attempt, final_capture, final_provenance)
                if category != "valid_html_payload" and not state.stop_reason:
                    cdx_attempts, last_started = request_pair(CDX_URL, "cdx", "scoped-cdx", state, gate, window_started, last_started)
                    all_attempts.extend(cdx_attempts)
                    operation_log.append({"operation": "scoped_cdx", "url": CDX_URL, "attempts": sanitize_attempts(cdx_attempts)})
                    cdx_final = cdx_attempts[-1] if cdx_attempts else None
                    cdx_body = body_for(cdx_final)
                    records, cdx_info_parsed = cdx_capture(cdx_body) if cdx_final and cdx_final.get("source_status") == 200 and not cdx_final.get("transport_error") else ([], {"parse_valid": False, "parse_error": "no_source_200_response", "selected": None, "eligible_count": 0})
                    cdx_info = {**cdx_info_parsed, "source_status": cdx_final.get("source_status") if cdx_final else None, "body_bytes": len(cdx_body), "row_count": len(records), "records": records}
                    selected = cdx_info_parsed.get("selected")
                    if selected and not state.stop_reason:
                        final_capture = selected
                        final_provenance = "scoped_cdx_latest_preanchor"
                        cdx_replay_url = core.replay_url(selected)
                        cdx_replay_attempts, last_started = request_pair(cdx_replay_url, "replay", "cdx-replay", state, gate, window_started, last_started)
                        all_attempts.extend(cdx_replay_attempts)
                        operation_log.append({"operation": "cdx_replay", "url": cdx_replay_url, "attempts": sanitize_attempts(cdx_replay_attempts)})
                        final_attempt = cdx_replay_attempts[-1] if cdx_replay_attempts else None
                        category, reason, validation = validate_replay(final_attempt, final_capture, final_provenance)
                    elif cdx_info_parsed.get("parse_valid") and not records:
                        category, reason = "cdx_empty_in_scoped_window", "no_rows_in_20070801_to_anchor_scope"
                    elif cdx_info_parsed.get("parse_valid"):
                        category, reason = "cdx_rows_without_valid_200", "no_same_origin_status_200_candidate"
            if category == "unknown":
                category, reason = "transport_error", "no_valid_payload_or_scoped_index"
    finally:
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=free_bytes)
    if not state.stop_reason:
        state.stop_reason = "valid_payload_found" if category == "valid_html_payload" else "completed"
    finished_utc = now_utc()
    payload_bytes = int((validation or {}).get("body_bytes") or 0) if category == "valid_html_payload" else 0
    source_responses = sum(a.get("source_status") is not None for a in all_attempts)
    failed_attempts = sum(bool(a.get("transport_error")) for a in all_attempts)
    dispatches = journal.get("dispatches") or []
    dispatch_intervals = [float(x["dispatch_monotonic"] - dispatches[i - 1]["dispatch_monotonic"]) for i, x in enumerate(dispatches) if i > 0]
    request_times = [parse_iso(a.get("started_utc")) for a in all_attempts if parse_iso(a.get("started_utc"))]
    request_intervals = [(request_times[i] - request_times[i - 1]).total_seconds() for i in range(1, len(request_times))]
    report = {
        "schema": "wow-recovery.news22-batch-report.v1",
        "batch_id": BATCH_ID,
        "mode": "executed",
        "target": TARGET,
        "authorization_window": {"start_utc": AUTH_START.isoformat(), "end_utc": AUTH_END.isoformat()},
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "attempt_count": state.attempts,
        "source_response_count": source_responses,
        "failed_attempt_count": failed_attempts,
        "total_body_bytes": state.total_body_bytes,
        "payload_body_bytes": payload_bytes,
        "category": category,
        "reason": reason,
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "source_status": (validation or {}).get("source_status") if validation else None,
        "actual_memento": (validation or {}).get("actual_memento") if validation else None,
        "content_type": (validation or {}).get("content_type") if validation else None,
        "body_bytes": (validation or {}).get("body_bytes", 0) if validation else 0,
        "body_sha256": (validation or {}).get("body_sha256") if validation else None,
        "validation": validation,
        "final_capture": final_capture,
        "final_provenance": final_provenance,
        "cdx": cdx_info,
        "availability": availability_info,
        "operations": operation_log,
        "attempts": sanitize_attempts(all_attempts),
        "disk_preflight": journal.get("disk_preflight"),
        "disk_postflight": postflight,
        "cadence": {"dispatch_intervals": dispatch_intervals, "request_start_intervals": request_intervals, "min_dispatch_monotonic_seconds": min(dispatch_intervals) if dispatch_intervals else None, "min_request_start_utc_seconds": min(request_intervals) if request_intervals else None, "required_dispatch_monotonic_seconds": MIN_DISPATCH_MONOTONIC, "required_request_start_utc_seconds": MIN_REQUEST_START_UTC},
        "policy": {"max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW_SECONDS, "max_total_body_bytes": MAX_TOTAL_BODY_BYTES, "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES, "manual_location_follows": 1, "late_windows": 0, "automatic_redirects": 0, "tls_verification": "curl default verification enabled"},
        "input": {"target": TARGET, "raw_replay_url": RAW_REPLAY_URL, "availability_url": AVAILABILITY_URL, "cdx_url": CDX_URL},
        "dispatch_journal": rel(JOURNAL),
        "raw_evidence_note": "Raw headers, traces, stderr and bodies remain local. CONNECT status is excluded from source_response_count; direct replay without CDX carries no fabricated digest claim.",
    }
    write_json(REPORT, report)
    write_summary(report)
    journal["report_written_utc"] = now_utc()
    journal["report_sha256"] = sha256_file(REPORT)
    write_json(JOURNAL, journal)
    print(json.dumps({"mode": "executed", "batch_id": BATCH_ID, "exit": 0, "target": TARGET, "attempts": state.attempts, "source_responses": source_responses, "category": category, "stop_reason": state.stop_reason, "actual_memento": report["actual_memento"], "body_bytes": report["body_bytes"], "body_sha256": report["body_sha256"], "disk_free_before": disk_before, "disk_free_after": postflight["disk_free_bytes"]}, ensure_ascii=False))
    return 0


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

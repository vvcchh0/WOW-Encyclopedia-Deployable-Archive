#!/usr/bin/env python3
"""NEWS22-FOLLOW: bounded replay of the already-indexed February 2008 hop.

This adapter imports the accepted NEWS22/core transport, gate, and date
observer.  It owns only ``network/follow`` and never performs availability or
CDX requests.  A Location is followed only when its timestamp is one of the
seven already observed pre-anchor CDX captures for this exact URL.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
NEWS22_PATH = ROOT / "research/focused-recovery-20261015-2303/network/news22_driver.py"
NEWS22_REPORT = ROOT / "research/focused-recovery-20261015-2303/network/batch-report.json"

TARGET = "http://www.worldofwarcraft.com/news/rss-08-2007.xml"
ANCHOR = "20080512210044"
INITIAL_REPLAY_URL = "https://web.archive.org/web/20080225003657id_/http://www.worldofwarcraft.com/news/rss-08-2007.xml"
MAX_ATTEMPTS = 6
WINDOW_SECONDS = 240
MIN_DISPATCH_MONOTONIC = 5.1
MIN_REQUEST_START_UTC = 5.0
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY_BYTES = 8 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 2 * 1024 * 1024
STOP_HTTP_CODES = {429, 503}
USER_AGENT = "wow-recovery-news22-follow/20261015"

PLAN = OUT / "follow-plan.json"
CANDIDATES = OUT / "candidates.json"
CONFIG = OUT / "config.json"
JOURNAL = OUT / "dispatch-journal.json"
REPORT = OUT / "batch-report.json"
SUMMARY_JSON = OUT / "sanitized-summary.json"
SUMMARY_MD = OUT / "sanitized-summary.md"

CAPTURES: dict[str, dict[str, Any]] = {
    "20071012024202": {"timestamp": "20071012024202", "original": "http://www.worldofwarcraft.com:80/news/rss-08-2007.xml", "mimetype": "text/html", "statuscode": "200", "digest": "BLF6G2ODJTPTMJUIQAKVBXDKQ2W4BK2Q", "length": "20815"},
    "20071106163045": {"timestamp": "20071106163045", "original": "http://www.worldofwarcraft.com:80/news/rss-08-2007.xml", "mimetype": "text/html", "statuscode": "200", "digest": "BLF6G2ODJTPTMJUIQAKVBXDKQ2W4BK2Q", "length": "20816"},
    "20071202063720": {"timestamp": "20071202063720", "original": "http://www.worldofwarcraft.com:80/news/rss-08-2007.xml", "mimetype": "text/html", "statuscode": "200", "digest": "GZ2R57CX7KAYN6RD4QDH36AERNQFAISG", "length": "20984"},
    "20071225160125": {"timestamp": "20071225160125", "original": "http://www.worldofwarcraft.com:80/news/rss-08-2007.xml", "mimetype": "text/html", "statuscode": "200", "digest": "RGSVMFYW3GXIMAUXFHGYB3NW7PMPTWN2", "length": "20965"},
    "20080125074428": {"timestamp": "20080125074428", "original": "http://www.worldofwarcraft.com:80/news/rss-08-2007.xml", "mimetype": "text/html", "statuscode": "200", "digest": "FZDMFN5PCBNRART5WU6JLBCWNNURJSRW", "length": "20933"},
    "20080225003657": {"timestamp": "20080225003657", "original": "http://www.worldofwarcraft.com:80/news/rss-08-2007.xml", "mimetype": "text/html", "statuscode": "200", "digest": "IFAGAPDQBNAYS5OTEZLUVWRZEOGZNVUD", "length": "20891"},
    "20080402080419": {"timestamp": "20080402080419", "original": "http://www.worldofwarcraft.com/news/rss-08-2007.xml", "mimetype": "text/html", "statuscode": "200", "digest": "FS72VI4WDNLAV4UBSECF7DRISJHV3J3Z", "length": "20850"},
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


n = load_module(NEWS22_PATH, "news22_follow_news22")

# Rebind all accepted helper modules to this owned directory and this batch's
# smaller limits.  No helper writes to the prior NEWS22 directory after this.
n.OUT = OUT
n.RAW = RAW
n.TARGET = TARGET
n.ANCHOR = ANCHOR
n.MAX_ATTEMPTS = MAX_ATTEMPTS
n.WINDOW_SECONDS = WINDOW_SECONDS
n.MIN_DISPATCH_MONOTONIC = MIN_DISPATCH_MONOTONIC
n.MIN_REQUEST_START_UTC = MIN_REQUEST_START_UTC
n.MIN_FREE_BYTES = MIN_FREE_BYTES
n.MAX_TOTAL_BODY_BYTES = MAX_TOTAL_BODY_BYTES
n.MAX_ENTITY_BODY_BYTES = MAX_ENTITY_BODY_BYTES
n.STOP_HTTP_CODES = STOP_HTTP_CODES
n.USER_AGENT = USER_AGENT
n.REPORT = REPORT
n.JOURNAL = JOURNAL
n.SUMMARY_JSON = SUMMARY_JSON
n.SUMMARY_MD = SUMMARY_MD
n.core.OUT = OUT
n.core.RAW = RAW
n.core.USER_AGENT = USER_AGENT
n.core.MAX_ATTEMPTS = MAX_ATTEMPTS
n.core.WINDOW_SECONDS = WINDOW_SECONDS
n.core.MIN_FREE_BYTES = MIN_FREE_BYTES
n.core.MAX_TOTAL_BODY_BYTES = MAX_TOTAL_BODY_BYTES
n.core.MAX_ENTITY_BODY_BYTES = MAX_ENTITY_BODY_BYTES
n.core.MIN_INTERVAL_SECONDS = 0.0
n.core.STOP_HTTP_CODES = STOP_HTTP_CODES
n.gate_mod.OUT = OUT
n.gate_mod.RAW = RAW
n.gate_mod.INTERVAL_SECONDS = MIN_DISPATCH_MONOTONIC
n.gate_mod.MIN_FREE_BYTES = MIN_FREE_BYTES
n.gate_mod.MAX_TOTAL_BODY_BYTES = MAX_TOTAL_BODY_BYTES
n.gate_mod.MAX_ENTITY_BYTES = MAX_ENTITY_BODY_BYTES


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def rel(path: Path) -> str:
    return path.resolve().relative_to(OUT.resolve()).as_posix()


def digest(path: Path) -> dict[str, Any]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def prepare() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    disk = free_bytes()
    if disk < MIN_FREE_BYTES:
        raise SystemExit("disk_free_below_threshold_before_prepare")
    source_report_sha = sha256_file(NEWS22_REPORT)
    candidates = {
        "schema": "wow-recovery.news22-follow-candidates.v1",
        "batch_id": "NEWS22-FOLLOW-AUG2007-20261015",
        "network_requests": 0,
        "target": TARGET,
        "initial_replay_url": INITIAL_REPLAY_URL,
        "captured_location_evidence": "NEWS22 attempt 08 proxy Location; timestamp 20080225003657; same normalized origin",
        "eligible_capture_set": list(CAPTURES.values()),
        "source_report": {"path": str(NEWS22_REPORT.relative_to(ROOT)).replace("\\", "/"), "sha256": source_report_sha},
        "selection": "follow only Wayback Location timestamps in the seven already-observed pre-anchor CDX 200 rows",
        "policy": {"max_attempts": MAX_ATTEMPTS, "max_manual_follow_hops": 2, "window_seconds": WINDOW_SECONDS, "max_total_body_bytes": MAX_TOTAL_BODY_BYTES, "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES, "min_dispatch_monotonic_seconds": MIN_DISPATCH_MONOTONIC, "min_request_start_utc_seconds": MIN_REQUEST_START_UTC, "disk_floor_bytes": MIN_FREE_BYTES, "automatic_redirects": 0, "availability_requests": 0, "cdx_requests": 0, "tls_verification": "curl default verification enabled"},
    }
    config = {"schema": "wow-recovery.news22-follow-config.v1", "batch_id": candidates["batch_id"], "prepared_utc": n.now_utc(), "network_requests": 0, "disk_free_bytes": disk, "source_report_sha256": source_report_sha, "policy": candidates["policy"]}
    write_json(CANDIDATES, candidates)
    config["candidates_sha256"] = sha256_file(CANDIDATES)
    write_json(CONFIG, config)
    plan = {"schema": "wow-recovery.news22-follow-plan.v1", "mode": "plan_only", "batch_id": candidates["batch_id"], "prepared_utc": n.now_utc(), "network_requests": 0, "input": {"source_report": str(NEWS22_REPORT.relative_to(ROOT)).replace("\\", "/"), "source_report_sha256": source_report_sha}, "outputs": {"raw": rel(RAW), "journal": rel(JOURNAL), "report": rel(REPORT), "summary": rel(SUMMARY_JSON)}, "disk_free_bytes": disk, "minimum_free_bytes": MIN_FREE_BYTES, "request_sequence": ["20080225003657 replay", "at most two eligible same-origin Location hops"]}
    plan["candidates_sha256"] = sha256_file(CANDIDATES)
    plan["config_sha256"] = sha256_file(CONFIG)
    write_json(PLAN, plan)
    print(json.dumps({"mode": "prepared", "network_requests": 0, "disk_free_bytes": disk, "initial_replay_url": INITIAL_REPLAY_URL}, ensure_ascii=False))
    return 0


def legal_eligible_location(location: str | None) -> tuple[str | None, str | None]:
    candidate = n.legal_location(location, INITIAL_REPLAY_URL)
    if not candidate:
        return None, "not_a_legal_wayback_replay"
    parts = urlsplit(candidate)
    tail = parts.path[len("/web/"):] if parts.path.startswith("/web/") else ""
    timestamp = tail[:14] if len(tail) >= 14 and tail[:14].isdigit() else None
    if not timestamp or timestamp not in CAPTURES:
        return None, "timestamp_not_in_news22_seven_eligible_captures"
    encoded = tail[14:]
    if encoded.startswith("id_"):
        encoded = encoded[3:]
    observed_original = unquote(encoded)
    if n.core.normalized_url_identity(observed_original) != n.core.normalized_url_identity(TARGET):
        return None, "location_origin_or_path_mismatch"
    return candidate, None


def memento_capture_check(attempt: dict[str, Any] | None, capture: dict[str, Any]) -> dict[str, Any]:
    actual = n.parse_iso((attempt or {}).get("memento_datetime"))
    expected = n.core.parse_timestamp(str(capture.get("timestamp") or ""))
    return {"actual_memento": (attempt or {}).get("memento_datetime"), "capture_timestamp": capture.get("timestamp"), "actual_memento_matches_capture_timestamp": bool(actual and expected and actual == expected), "actual_memento_at_or_before_anchor": bool(actual and actual <= n.parse_iso("2008-05-12T21:00:44+00:00"))}


def write_summary(report: dict[str, Any]) -> None:
    summary = {"schema": "wow-recovery.news22-follow-sanitized-summary.v1", "batch_id": report["batch_id"], "authorization_window": report["authorization_window"], "started_utc": report["started_utc"], "finished_utc": report["finished_utc"], "attempt_count": report["attempt_count"], "source_response_count": report["source_response_count"], "failed_attempt_count": report["failed_attempt_count"], "total_body_bytes": report["total_body_bytes"], "payload_body_bytes": report["payload_body_bytes"], "category": report["category"], "reason": report["reason"], "stop_reason": report["stop_reason"], "source_status": report["source_status"], "actual_memento": report["actual_memento"], "body_bytes": report["body_bytes"], "body_sha256": report["body_sha256"], "validation": report["validation"], "capture": report["capture"], "memento_capture_check": report["memento_capture_check"], "cadence": report["cadence"], "disk_preflight": report["disk_preflight"], "disk_postflight": report["disk_postflight"], "raw_evidence_note": "Raw headers, traces, stderr and bodies remain local. CONNECT is excluded from source_response_count; no automatic redirects or availability/CDX requests were made."}
    write_json(SUMMARY_JSON, summary)
    SUMMARY_MD.write_text("\n".join(["# NEWS22-FOLLOW sanitized summary", f"- Target: `{TARGET}`", f"- Category: `{report['category']}`; source responses `{report['source_response_count']}`; attempts `{report['attempt_count']}`.", f"- Actual Memento: `{report['actual_memento']}`; body bytes `{report['body_bytes']}`; SHA256 `{report['body_sha256']}`.", f"- Capture provenance: `{report['capture']}`.", "- Raw headers, traces, stderr and bodies remain local; no source/export integration was performed."]) + "\n", encoding="utf-8")


def execute() -> int:
    if REPORT.exists():
        raise SystemExit("refusing to overwrite existing NEWS22-FOLLOW report")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    disk_before = free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise SystemExit("disk_free_below_threshold_before_dispatch")
    started_utc = n.now_utc()
    window_started = time.monotonic()
    state = n.core.RunState(window_started)
    journal: dict[str, Any] = {"schema": "wow-recovery.news22-follow-dispatch-journal.v1", "batch_id": "NEWS22-FOLLOW-AUG2007-20261015", "simulation": False, "authorization_window": {"start_utc": n.AUTH_START.isoformat(), "end_utc": n.AUTH_END.isoformat()}, "policy": {"max_attempts": MAX_ATTEMPTS, "max_manual_follow_hops": 2, "min_dispatch_monotonic_seconds": MIN_DISPATCH_MONOTONIC, "min_request_start_utc_seconds": MIN_REQUEST_START_UTC, "disk_floor_bytes": MIN_FREE_BYTES}, "disk_preflight": {"checked_utc": started_utc, "disk_free_bytes": disk_before, "minimum_free_bytes": MIN_FREE_BYTES}, "dispatches": []}
    write_json(JOURNAL, journal)
    gate = n.gate_mod.GateState(n.AUTH_START, journal_path=JOURNAL, journal=journal)
    last_started: datetime | None = None
    all_attempts: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    current_url = INITIAL_REPLAY_URL
    capture = CAPTURES["20080225003657"]
    final_attempt: dict[str, Any] | None = None
    category = "unknown"
    reason = "no_request"
    validation: dict[str, Any] | None = None
    location_rejections: list[dict[str, Any]] = []
    hop_count = 0
    try:
        while True:
            attempts, last_started = n.request_pair(current_url, "replay", f"follow-hop-{hop_count}", state, gate, window_started, last_started)
            all_attempts.extend(attempts)
            operations.append({"operation": "initial_replay" if hop_count == 0 else f"manual_location_follow_{hop_count}", "url": current_url, "capture": capture, "attempts": n.sanitize_attempts(attempts)})
            final_attempt = attempts[-1] if attempts else None
            category, reason, validation = n.validate_replay(final_attempt, capture, "NEWS22_CDX_CAPTURE_FOLLOW")
            if category == "valid_html_payload":
                break
            if category != "redirect_unfollowed":
                break
            if hop_count >= 2:
                state.stop_reason = "manual_location_follow_cap"
                state.stop_detail = {"max_manual_follow_hops": 2, "last_location": (final_attempt or {}).get("location")}
                break
            candidate, rejection = legal_eligible_location((final_attempt or {}).get("location"))
            if not candidate:
                location_rejections.append({"location": (final_attempt or {}).get("location"), "reason": rejection})
                state.stop_reason = rejection or "location_rejected"
                state.stop_detail = {"location": (final_attempt or {}).get("location")}
                break
            timestamp = urlsplit(candidate).path[len("/web/"):len("/web/") + 14]
            capture = CAPTURES[timestamp]
            current_url = candidate
            hop_count += 1
            if state.stop_reason:
                break
    finally:
        postflight = n.gate_mod.persist_postflight(gate, state.attempts, free_fn=free_bytes)
    if not state.stop_reason:
        if category == "valid_html_payload":
            state.stop_reason = "valid_payload_found"
        elif state.attempts >= MAX_ATTEMPTS:
            state.stop_reason = "attempt_limit"
            state.stop_detail = {"max_attempts": MAX_ATTEMPTS}
        else:
            state.stop_reason = "completed"
    payload_bytes = int((validation or {}).get("body_bytes") or 0) if category == "valid_html_payload" else 0
    source_responses = sum(a.get("source_status") is not None for a in all_attempts)
    failed_attempts = sum(bool(a.get("transport_error")) for a in all_attempts)
    dispatches = journal.get("dispatches") or []
    dispatch_intervals = [float(x["dispatch_monotonic"] - dispatches[i - 1]["dispatch_monotonic"]) for i, x in enumerate(dispatches) if i > 0]
    request_times = [n.parse_iso(a.get("started_utc")) for a in all_attempts if n.parse_iso(a.get("started_utc"))]
    request_intervals = [(request_times[i] - request_times[i - 1]).total_seconds() for i in range(1, len(request_times))]
    report = {"schema": "wow-recovery.news22-follow-batch-report.v1", "batch_id": "NEWS22-FOLLOW-AUG2007-20261015", "mode": "executed", "target": TARGET, "authorization_window": {"start_utc": n.AUTH_START.isoformat(), "end_utc": n.AUTH_END.isoformat()}, "started_utc": started_utc, "finished_utc": n.now_utc(), "attempt_count": state.attempts, "source_response_count": source_responses, "failed_attempt_count": failed_attempts, "total_body_bytes": state.total_body_bytes, "payload_body_bytes": payload_bytes, "category": category, "reason": reason, "stop_reason": state.stop_reason, "stop_detail": state.stop_detail, "source_status": (validation or {}).get("source_status") if validation else ((final_attempt or {}).get("source_status") if final_attempt else None), "actual_memento": (validation or {}).get("actual_memento") if validation else ((final_attempt or {}).get("memento_datetime") if final_attempt else None), "content_type": (validation or {}).get("content_type") if validation else ((final_attempt or {}).get("content_type") if final_attempt else None), "body_bytes": (validation or {}).get("body_bytes", 0) if validation else 0, "body_sha256": (validation or {}).get("body_sha256") if validation else ((final_attempt or {}).get("body_sha256") if final_attempt else None), "validation": validation, "capture": capture, "memento_capture_check": memento_capture_check(final_attempt, capture), "operations": operations, "location_rejections": location_rejections, "attempts": n.sanitize_attempts(all_attempts), "disk_preflight": journal.get("disk_preflight"), "disk_postflight": postflight, "cadence": {"dispatch_intervals": dispatch_intervals, "request_start_intervals": request_intervals, "min_dispatch_monotonic_seconds": min(dispatch_intervals) if dispatch_intervals else None, "min_request_start_utc_seconds": min(request_intervals) if request_intervals else None, "required_dispatch_monotonic_seconds": MIN_DISPATCH_MONOTONIC, "required_request_start_utc_seconds": MIN_REQUEST_START_UTC}, "policy": {"max_attempts": MAX_ATTEMPTS, "max_manual_follow_hops": 2, "window_seconds": WINDOW_SECONDS, "max_total_body_bytes": MAX_TOTAL_BODY_BYTES, "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES, "automatic_redirects": 0, "availability_requests": 0, "cdx_requests": 0, "tls_verification": "curl default verification enabled"}, "input": {"initial_replay_url": INITIAL_REPLAY_URL, "source_report": str(NEWS22_REPORT.relative_to(ROOT)).replace("\\", "/"), "source_report_sha256": sha256_file(NEWS22_REPORT)}, "dispatch_journal": rel(JOURNAL), "raw_evidence_note": "Raw headers, traces, stderr and bodies remain local. CONNECT status is excluded; digest and Memento are tied to the actual capture row."}
    write_json(REPORT, report)
    write_summary(report)
    journal["report_written_utc"] = n.now_utc()
    journal["report_sha256"] = sha256_file(REPORT)
    write_json(JOURNAL, journal)
    print(json.dumps({"mode": "executed", "batch_id": report["batch_id"], "exit": 0, "attempts": state.attempts, "source_responses": source_responses, "category": category, "stop_reason": state.stop_reason, "actual_memento": report["actual_memento"], "body_bytes": report["body_bytes"], "body_sha256": report["body_sha256"], "disk_free_before": disk_before, "disk_free_after": postflight["disk_free_bytes"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.prepare == args.execute:
        parser.error("choose exactly one of --prepare or --execute")
    raise SystemExit(prepare() if args.prepare else execute())

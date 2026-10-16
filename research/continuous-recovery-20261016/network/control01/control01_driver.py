from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[4]
NETWORK = ROOT / "research" / "continuous-recovery-20261016" / "network"
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
PROPOSAL = NETWORK / "diagnostic-20261016-v2" / "control-window-plan.json"
BATCH_ID = "WAYBACK-CONTROL01-20261016"
USER_AGENT = "wow-recovery-control01/20261016"
PROXY = "http://127.0.0.1:7890"
WINDOW_SECONDS = 120.0
MAX_TOTAL_BODY_BYTES = 2 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 1 * 1024 * 1024
MIN_DISPATCH_SECONDS = 5.1
MIN_REQUEST_START_SECONDS = 5.0
DISK_FLOOR_BYTES = 11_005_853_696
STOP_HTTP_CODES = {429, 503}
CDX_COLUMNS = ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
DIRECT_CONNECT_SECONDS = 4.0
DIRECT_MAX_SECONDS = 12.0
PROXY_CONNECT_SECONDS = 8.0
PROXY_MAX_SECONDS = 20.0


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None) -> str | None:
    return dt.isoformat().replace("+00:00", "Z") if dt else None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def atomic_write(path: Path, value: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def disk_free() -> int:
    return shutil.disk_usage(ROOT).free


def parse_http_code(stdout: str) -> int | None:
    value = stdout.strip().splitlines()[-1].strip() if stdout.strip() else ""
    if value.isdigit() and len(value) == 3:
        if value == "000":
            return None
        return int(value)


def parse_headers(path: Path) -> tuple[str | None, int | None]:
    content_type = None
    retry_after = None
    if not path.exists():
        return None, None
    for line in path.read_text(encoding="iso-8859-1", errors="replace").splitlines():
        lower = line.lower()
        if lower.startswith("content-type:") and content_type is None:
            content_type = line.split(":", 1)[1].strip().split(";", 1)[0].strip().lower()
        if lower.startswith("retry-after:") and retry_after is None:
            value = line.split(":", 1)[1].strip()
            if value.isdigit():
                retry_after = int(value)
    return content_type, retry_after


def parse_cdx_body(body: bytes) -> tuple[list[dict[str, str]], bool, str | None]:
    text = body.decode("utf-8", errors="replace")
    stripped = text.strip()
    if not stripped or stripped.lower() in {"[]", "no captures found", "no captures"}:
        return [], True, None
    records: list[dict[str, str]] = []
    try:
        payload = json.loads(text)
        if isinstance(payload, list):
            rows: list[Any] = payload
            if rows and isinstance(rows[0], list) and [str(x) for x in rows[0]] == CDX_COLUMNS:
                rows = rows[1:]
            for row in rows:
                if isinstance(row, dict):
                    records.append({key: str(row.get(key, "")) for key in CDX_COLUMNS})
                elif isinstance(row, list) and len(row) >= len(CDX_COLUMNS):
                    records.append({key: str(row[index]) for index, key in enumerate(CDX_COLUMNS)})
            return records, True, None
        if isinstance(payload, dict):
            rows = payload.get("records") or payload.get("captures") or []
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict):
                        records.append({key: str(row.get(key, "")) for key in CDX_COLUMNS})
                return records, True, None
        return [], False, "json_shape"
    except json.JSONDecodeError:
        return [], False, "json_decode"


def trace_state(trace_path: Path, stderr_path: Path) -> dict[str, Any]:
    trace = trace_path.read_text(encoding="utf-8", errors="replace") if trace_path.exists() else ""
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
    low = (trace + "\n" + stderr).lower()
    markers: list[str] = []

    def add(name: str) -> None:
        if name not in markers:
            markers.append(name)

    if "trying " in low:
        add("connection_attempt_logged")
    if "connection timed out" in low or "failed to connect" in low or "connection refused" in low:
        add("tcp_connect_failed_or_timed_out")
    if "connect phase completed" in low or "connection established" in low or "connect tunnel established" in low:
        add("proxy_connect_established")
    if "alpn: server accepted" in low or "ssl/tls connection renegotiated" in low:
        add("tls_handshake_completed")
    elif "failed to receive handshake" in low or "ssl/tls connection failed" in low:
        add("tls_handshake_failed")
    elif "alpn: curl offers" in low:
        add("tls_handshake_started")
    if "request completely sent off" in low:
        add("get_request_sent")
    if "<= recv header" in low and "http/1.1 200" in low:
        add("http_response_header_observed")
    if "closing connection" in low:
        add("connection_closed")
    if "curl: (35)" in low:
        error = "curl: (35) TLS handshake failed"
    elif "curl: (28)" in low:
        error = "curl: (28) connection timed out"
    elif "curl: (" in low:
        error = "curl transport error"
    else:
        error = ""
    if "could not resolve host" in low or "name or service not known" in low:
        boundary = "dns"
    elif "tcp_connect_failed_or_timed_out" in markers and "proxy_connect_established" not in markers:
        boundary = "tcp_connect"
    elif "tls_handshake_failed" in markers:
        boundary = "tls_handshake"
    elif "get_request_sent" in markers and "http_response_header_observed" not in markers:
        boundary = "get_sent_waiting_response"
    elif "http_response_header_observed" in markers:
        boundary = "source_response"
    elif "proxy_connect_established" in markers:
        boundary = "connect"
    else:
        boundary = "unknown"
    return {"markers": markers, "boundary": boundary, "error_excerpt": error}


def build_query() -> str:
    original = "http://www.worldofwarcraft.com/new-hp/images/smallcaps/h.gif"
    params = [
        ("url", original),
        ("from", "20060101000000"),
        ("to", "20080512210044"),
        ("output", "json"),
        ("fl", ",".join(CDX_COLUMNS)),
        ("limit", "250"),
        ("matchType", "exact"),
    ]
    return "https://web.archive.org/cdx/search/cdx?" + urlencode(params)


def safe_attempt(record: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "attempt", "target_key", "transport", "kind", "started_utc", "finished_utc",
        "curl_exit", "connect_status", "source_status", "content_type", "retry_after",
        "body_bytes", "duration_ms", "transport_error", "transport_reason",
        "cdx_json_valid", "cdx_record_count", "cdx_parse_error", "success_gate",
        "phase_boundary", "phase_markers", "sanitized_error_excerpt", "disk_free_before_bytes",
        "disk_floor_bytes", "disk_floor_passed", "dispatch_monotonic", "dispatch_utc",
        "dispatch_interval_seconds", "request_start_interval_seconds", "clamp",
    ]
    return {k: record.get(k) for k in keys}


proposal_sha = sha256(PROPOSAL)
proposal = load_json(PROPOSAL, {})
if proposal.get("target", {}).get("exact_original") != "http://www.worldofwarcraft.com/new-hp/images/smallcaps/h.gif":
    raise SystemExit("proposal target identity mismatch")

# Prepare durable state before any network operation. Existing completed state is never replayed.
attempt_path = OUT / "attempt-records.json"
dispatch_path = OUT / "dispatch-log.json"
progress_path = OUT / "progress.json"
report_path = OUT / "batch-report.json"
existing_attempts = load_json(attempt_path, [])
existing_dispatch = load_json(dispatch_path, [])
if report_path.exists() and load_json(report_path, {}).get("mode") == "executed":
    print(json.dumps({"mode": "already_completed", "network_requests_executed": 0, "report": rel(report_path)}))
    raise SystemExit(0)
if len(existing_attempts) >= 2 or len(existing_dispatch) >= 2:
    print(json.dumps({"mode": "attempt_cap_already_reserved", "network_requests_executed": 0, "attempts": len(existing_attempts), "dispatches": len(existing_dispatch)}))
    raise SystemExit(0)

started = utc_now()
state = {
    "schema": "wow-recovery.control01-state.v1",
    "batch_id": BATCH_ID,
    "mode": "prepared",
    "prepared_utc": iso(started),
    "window_started_utc": None,
    "window_seconds": WINDOW_SECONDS,
    "previous_allnews02_tail": 5,
    "previous_tail_preserved": True,
    "probe_failure_streak": 0,
    "attempts_reserved": len(existing_dispatch),
    "attempts_completed": len(existing_attempts),
    "stop_reason": None,
}
plan = {
    "schema": "wow-recovery.control01-plan.v1",
    "mode": "go_executed",
    "batch_id": BATCH_ID,
    "prepared_utc": iso(started),
    "proposal_path": rel(PROPOSAL),
    "proposal_sha256": proposal_sha,
    "target_key": "ALLNEWS01-R02-control",
    "exact_original": proposal["target"]["exact_original"],
    "query_url": build_query(),
    "query_identity": {
        "match_type": "exact", "from": "20060101000000", "to": "20080512210044",
        "limit": 250, "collapse": False, "output": "json", "fields": CDX_COLUMNS,
    },
    "control_only": True,
    "no_replay": True,
    "max_attempts": 2,
    "window_seconds": WINDOW_SECONDS,
    "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
    "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
    "direct_first": True,
    "proxy": PROXY,
    "tls_verification": True,
    "automatic_redirects": 0,
    "min_dispatch_monotonic_seconds": MIN_DISPATCH_SECONDS,
    "min_request_start_utc_seconds": MIN_REQUEST_START_SECONDS,
    "disk_floor_bytes": DISK_FLOOR_BYTES,
    "stop_http_codes": sorted(STOP_HTTP_CODES),
    "prior_tail": 5,
    "probe_streak_start": 0,
    "success_gate": "source HTTP 200 and valid JSON CDX with record_count < 250",
    "network_requests_executed_at_prepare": 0,
}
atomic_write(OUT / "plan.json", plan)
atomic_write(OUT / "preflight.json", {
    "schema": "wow-recovery.control01-preflight.v1",
    "checked_utc": iso(utc_now()),
    "not_before_utc": proposal.get("not_before_utc"),
    "not_before_satisfied": utc_now() >= datetime.fromisoformat(proposal["not_before_utc"].replace("Z", "+00:00")),
    "disk_free_bytes": disk_free(),
    "disk_floor_bytes": DISK_FLOOR_BYTES,
    "disk_floor_passed": disk_free() >= DISK_FLOOR_BYTES,
    "proposal_sha256": proposal_sha,
    "plan_sha256": sha256(OUT / "plan.json"),
})
atomic_write(progress_path, state)
atomic_write(attempt_path, existing_attempts)
atomic_write(dispatch_path, existing_dispatch)

preflight = load_json(OUT / "preflight.json", {})
if not preflight["not_before_satisfied"]:
    state["mode"] = "stopped"
    state["stop_reason"] = "not_before_not_reached"
    atomic_write(progress_path, state)
    atomic_write(report_path, {"schema": "wow-recovery.control01-batch-report.v1", **state, "network_requests": 0, "plan_sha256": sha256(OUT / "plan.json")})
    print(json.dumps({"mode": "stopped", "stop_reason": state["stop_reason"], "network_requests_executed": 0}))
    raise SystemExit(0)
if not preflight["disk_floor_passed"]:
    state["mode"] = "stopped"
    state["stop_reason"] = "disk_floor_failed"
    atomic_write(progress_path, state)
    atomic_write(report_path, {"schema": "wow-recovery.control01-batch-report.v1", **state, "network_requests": 0, "plan_sha256": sha256(OUT / "plan.json")})
    print(json.dumps({"mode": "stopped", "stop_reason": state["stop_reason"], "network_requests_executed": 0}))
    raise SystemExit(0)

window_start = utc_now()
window_start_monotonic = time.monotonic()
state["mode"] = "executing"
state["window_started_utc"] = iso(window_start)
atomic_write(progress_path, state)

last_dispatch_mono: float | None = None
last_request_start: datetime | None = None
attempts: list[dict[str, Any]] = existing_attempts[:]
dispatches: list[dict[str, Any]] = existing_dispatch[:]
source_success = False
stop_reason: str | None = None

for attempt_no in range(len(attempts) + 1, 3):
    now = time.monotonic()
    elapsed = now - window_start_monotonic
    remaining_window = WINDOW_SECONDS - elapsed
    if remaining_window <= 0:
        stop_reason = "window_exhausted_before_dispatch"
        break
    # Enforce both cadence clocks using the actual process monotonic and UTC start times.
    wait_mono = 0.0 if last_dispatch_mono is None else max(0.0, last_dispatch_mono + MIN_DISPATCH_SECONDS - time.monotonic())
    wait_wall = 0.0 if last_request_start is None else max(0.0, (last_request_start + timedelta(seconds=MIN_REQUEST_START_SECONDS) - utc_now()).total_seconds())
    wait_for = max(wait_mono, wait_wall)
    if wait_for > 0:
        time.sleep(wait_for)
    now = time.monotonic()
    elapsed = now - window_start_monotonic
    remaining_window = WINDOW_SECONDS - elapsed
    if remaining_window <= 0:
        stop_reason = "window_exhausted_before_dispatch"
        break
    free_before = disk_free()
    if free_before < DISK_FLOOR_BYTES:
        stop_reason = "disk_floor_failed_before_dispatch"
        break
    prior_body = sum(int(row.get("body_bytes") or 0) for row in attempts)
    total_remaining = max(0, MAX_TOTAL_BODY_BYTES - prior_body)
    entity_limit = min(MAX_ENTITY_BODY_BYTES, total_remaining)
    if entity_limit <= 0:
        stop_reason = "total_body_limit_before_dispatch"
        break
    transport = "direct" if attempt_no == 1 else "proxy"
    baseline_connect = DIRECT_CONNECT_SECONDS if transport == "direct" else PROXY_CONNECT_SECONDS
    baseline_max = DIRECT_MAX_SECONDS if transport == "direct" else PROXY_MAX_SECONDS
    effective_max = min(baseline_max, remaining_window)
    effective_connect = min(baseline_connect, effective_max)
    if effective_max <= 0.2 or effective_connect <= 0.2:
        stop_reason = "remaining_time_too_short_before_dispatch"
        break
    dispatch_utc = utc_now()
    dispatch_mono = time.monotonic()
    stem = f"{attempt_no:02d}-CONTROL01-R02-cdx-{transport}"
    headers = RAW / f"{stem}.headers.txt"
    body = RAW / f"{stem}.body"
    stderr = RAW / f"{stem}.stderr.txt"
    trace = RAW / f"{stem}.trace.txt"
    metrics = RAW / f"{stem}.metrics.txt"
    for path in (headers, body, stderr, trace, metrics):
        if path.exists():
            raise SystemExit(f"refusing to overwrite existing raw evidence: {path}")
    clamp = {
        "transport": transport,
        "total_body_bytes_before": prior_body,
        "total_body_remaining_before_bytes": total_remaining,
        "configured_entity_body_limit_bytes": MAX_ENTITY_BODY_BYTES,
        "entity_body_limit_before_bytes": entity_limit,
        "window_seconds": WINDOW_SECONDS,
        "window_remaining_seconds": remaining_window,
        "baseline_connect_timeout_seconds": baseline_connect,
        "baseline_max_timeout_seconds": baseline_max,
        "connect_timeout_seconds": effective_connect,
        "max_timeout_seconds": effective_max,
        "clamp_applied": effective_max < baseline_max or effective_connect < baseline_connect or entity_limit < MAX_ENTITY_BODY_BYTES,
        "dispatch_allowed": True,
    }
    dispatch = {
        "attempt": attempt_no, "batch_id": BATCH_ID, "target_key": "ALLNEWS01-R02-control",
        "kind": "cdx", "transport": transport, "dispatch_utc": iso(dispatch_utc),
        "dispatch_monotonic": dispatch_mono,
        "interval_since_previous_dispatch_seconds": None if not dispatches else dispatch_mono - float(dispatches[-1]["dispatch_monotonic"]),
        "request_start_interval_seconds": None,
        "persisted_before_transport": True,
        "disk_free_before_bytes": free_before,
        "disk_floor_bytes": DISK_FLOOR_BYTES,
        "disk_floor_passed": free_before >= DISK_FLOOR_BYTES,
        "raw": {"headers": rel(headers), "body": rel(body), "stderr": rel(stderr), "trace": rel(trace), "metrics": rel(metrics)},
        "clamp": clamp,
        "query_url": build_query(),
    }
    if dispatches:
        dispatch["request_start_interval_seconds"] = None if last_request_start is None else (utc_now() - last_request_start).total_seconds()
    dispatches.append(dispatch)
    atomic_write(dispatch_path, dispatches)
    atomic_write(progress_path, {**state, "attempts_reserved": len(dispatches), "last_dispatch_utc": iso(dispatch_utc), "probe_failure_streak": state.get("probe_failure_streak", 0)})
    command = [
        "curl.exe",
        "--proxy", "" if transport == "direct" else PROXY,
        "--noproxy", "*" if transport == "direct" else "",
        "--connect-timeout", f"{effective_connect:.3f}",
        "--max-time", f"{effective_max:.3f}",
        "--max-redirs", "0",
        "--max-filesize", str(entity_limit),
        "--silent", "--show-error",
        "--trace-time", "--trace-ascii", str(trace),
        "--dump-header", str(headers),
        "--output", str(body),
        "--write-out", "%{http_code}",
        "--user-agent", USER_AGENT,
        build_query(),
    ]
    started_req = utc_now()
    last_request_start = started_req
    last_dispatch_mono = dispatch_mono
    stdout = ""
    curl_exit: int | None = None
    exception_text = ""
    try:
        completed = subprocess.run(
            command, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=stderr.open("wb"),
            timeout=max(2.0, effective_max + 3.0), check=False,
        )
        stdout = completed.stdout.decode("ascii", errors="replace")
        curl_exit = completed.returncode
    except subprocess.TimeoutExpired:
        exception_text = "subprocess timeout guard"
        curl_exit = None
    except Exception as exc:
        exception_text = type(exc).__name__
        curl_exit = None
    finished_req = utc_now()
    if not headers.exists(): headers.write_text("", encoding="iso-8859-1")
    if not body.exists(): body.write_bytes(b"")
    if not trace.exists(): trace.write_text("", encoding="utf-8")
    if not stderr.exists(): stderr.write_text(exception_text, encoding="utf-8")
    body_size = body.stat().st_size
    status = parse_http_code(stdout)
    content_type, retry_after = parse_headers(headers)
    payload = body.read_bytes() if body_size <= MAX_ENTITY_BODY_BYTES else b""
    records: list[dict[str, str]] = []
    parse_valid = False
    parse_error: str | None = "no_200_source_response"
    if status == 200 and body_size <= MAX_ENTITY_BODY_BYTES:
        records, parse_valid, parse_error = parse_cdx_body(payload)
    success_gate = status == 200 and parse_valid and len(records) < 250
    phases = trace_state(trace, stderr)
    metrics.write_text(str(status or 0) + "\n", encoding="ascii")
    dispatch["request_start_interval_seconds"] = None if len(attempts) == 0 else (started_req - last_request_start).total_seconds() if False else dispatch["request_start_interval_seconds"]
    attempt = {
        "attempt": attempt_no,
        "batch_id": BATCH_ID,
        "target_key": "ALLNEWS01-R02-control",
        "original": "http://www.worldofwarcraft.com/new-hp/images/smallcaps/h.gif",
        "kind": "cdx", "transport": transport,
        "started_utc": iso(started_req), "finished_utc": iso(finished_req),
        "duration_ms": round((finished_req - started_req).total_seconds() * 1000, 3),
        "curl_exit": curl_exit, "connect_status": 200 if transport == "proxy" and "proxy_connect_established" in phases["markers"] else None,
        "source_status": status, "content_type": content_type, "retry_after": retry_after,
        "body_bytes": body_size, "body_sha256": sha256(body) if body_size else None,
        "transport_error": status is None, "transport_reason": "no_http_status" if status is None else None,
        "cdx_json_valid": parse_valid, "cdx_record_count": len(records) if parse_valid else 0,
        "cdx_parse_error": parse_error, "success_gate": success_gate,
        "phase_boundary": phases["boundary"], "phase_markers": phases["markers"],
        "sanitized_error_excerpt": phases["error_excerpt"],
        "disk_free_before_bytes": free_before, "disk_floor_bytes": DISK_FLOOR_BYTES, "disk_floor_passed": free_before >= DISK_FLOOR_BYTES,
        "dispatch_monotonic": dispatch_mono, "dispatch_utc": iso(dispatch_utc),
        "dispatch_interval_seconds": dispatch.get("interval_since_previous_dispatch_seconds"),
        "request_start_interval_seconds": None if len(attempts) == 0 else (started_req - datetime.fromisoformat(attempts[-1]["started_utc"].replace("Z", "+00:00"))).total_seconds(),
        "clamp": clamp,
        "raw": {"headers": rel(headers), "body": rel(body), "stderr": rel(stderr), "trace": rel(trace), "metrics": rel(metrics)},
    }
    attempts.append(attempt)
    atomic_write(attempt_path, attempts)
    state["attempts_reserved"] = len(dispatches)
    state["attempts_completed"] = len(attempts)
    state["last_attempt_finished_utc"] = iso(finished_req)
    state["last_source_status"] = status
    if status is None or not success_gate:
        state["probe_failure_streak"] = int(state.get("probe_failure_streak", 0)) + 1
    else:
        state["probe_failure_streak"] = 0
        source_success = True
    atomic_write(progress_path, state)
    if status in STOP_HTTP_CODES:
        stop_reason = f"endpoint_status_{status}"
        break
    if success_gate:
        stop_reason = "control_source_response_200_valid_cdx"
        break

if stop_reason is None:
    stop_reason = "two_attempts_exhausted_without_success"
state["mode"] = "completed"
state["stop_reason"] = stop_reason
state["source_success"] = source_success
state["attempts_reserved"] = len(dispatches)
state["attempts_completed"] = len(attempts)
state["finished_utc"] = iso(utc_now())
state["cooldown_required"] = any(r.get("source_status") in STOP_HTTP_CODES for r in attempts)
state["prior_allnews02_tail"] = 5
state["previous_tail_preserved"] = True
atomic_write(progress_path, state)

source_map = {
    "schema": "wow-recovery.control01-source-map.v1",
    "batch_id": BATCH_ID,
    "control_only": True,
    "accepted_payloads": [],
    "index_evidence": [
        {
            "target_key": r.get("target_key"),
            "source_status": r.get("source_status"),
            "cdx_json_valid": r.get("cdx_json_valid"),
            "cdx_record_count": r.get("cdx_record_count"),
            "success_gate": r.get("success_gate"),
            "raw": r.get("raw"),
        }
        for r in attempts
    ],
}
atomic_write(OUT / "source-map.json", source_map)

report = {
    "schema": "wow-recovery.control01-batch-report.v1",
    **state,
    "network_requests": len(attempts),
    "attempts": [safe_attempt(r) for r in attempts],
    "cadence": {
        "dispatch_intervals": [d.get("interval_since_previous_dispatch_seconds") for d in dispatches[1:]],
        "request_start_intervals": [r.get("request_start_interval_seconds") for r in attempts[1:]],
        "min_dispatch": min((d["interval_since_previous_dispatch_seconds"] for d in dispatches[1:] if d.get("interval_since_previous_dispatch_seconds") is not None), default=None),
        "min_request_start": min((r["request_start_interval_seconds"] for r in attempts[1:] if r.get("request_start_interval_seconds") is not None), default=None),
        "dispatch_passed": all((d.get("interval_since_previous_dispatch_seconds") or MIN_DISPATCH_SECONDS) >= MIN_DISPATCH_SECONDS for d in dispatches[1:]),
        "start_passed": all((r.get("request_start_interval_seconds") or MIN_REQUEST_START_SECONDS) >= MIN_REQUEST_START_SECONDS for r in attempts[1:]),
    },
    "policy": {
        "max_attempts": 2, "window_seconds": WINDOW_SECONDS,
        "max_total_body_bytes": MAX_TOTAL_BODY_BYTES, "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "direct_first": True, "proxy": PROXY, "tls_verification": True, "automatic_redirects": 0,
        "disk_floor_bytes": DISK_FLOOR_BYTES, "stop_http_codes": sorted(STOP_HTTP_CODES),
        "prior_allnews02_tail": 5, "probe_failure_streak_start": 0,
        "success_gate": "source HTTP 200 and valid JSON CDX with record_count < 250",
    },
    "plan_binding": {
        "proposal_path": rel(PROPOSAL), "proposal_sha256": proposal_sha,
        "plan_path": rel(OUT / "plan.json"), "plan_sha256": sha256(OUT / "plan.json"),
        "script_path": rel(Path(__file__)), "script_sha256": sha256(Path(__file__)),
    },
    "raw_evidence_note": "Raw headers, bodies, stderr and traces remain local; sanitized report excludes their content.",
}
atomic_write(report_path, report)
summary = {
    "schema": "wow-recovery.control01-sanitized-summary.v1",
    "batch_id": BATCH_ID,
    "network_requests": len(attempts),
    "source_success": source_success,
    "success_attempt": next((r.get("attempt") for r in attempts if r.get("success_gate")), None),
    "http_statuses": [r.get("source_status") for r in attempts],
    "curl_exits": [r.get("curl_exit") for r in attempts],
    "cdx_record_counts": [r.get("cdx_record_count") for r in attempts],
    "get_sent": ["get_request_sent" in (r.get("phase_markers") or []) for r in attempts],
    "stop_reason": stop_reason,
    "prior_tail_preserved": True,
    "prior_tail": 5,
    "probe_failure_streak": state.get("probe_failure_streak", 0),
    "plan_sha256": sha256(OUT / "plan.json"),
    "script_sha256": sha256(Path(__file__)),
}
atomic_write(OUT / "sanitized-summary.json", summary)
print(json.dumps({
    "mode": "executed", "batch_id": BATCH_ID,
    "network_requests": len(attempts), "source_success": source_success,
    "http_statuses": summary["http_statuses"], "cdx_record_counts": summary["cdx_record_counts"],
    "get_sent": summary["get_sent"], "stop_reason": stop_reason,
    "probe_failure_streak": summary["probe_failure_streak"],
    "plan_sha256": summary["plan_sha256"], "script_sha256": summary["script_sha256"],
}, ensure_ascii=False))

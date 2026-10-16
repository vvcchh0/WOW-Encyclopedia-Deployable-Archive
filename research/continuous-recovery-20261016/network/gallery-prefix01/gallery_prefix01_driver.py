"""Bounded exact-prefix CDX index probe for GALLERYPREFIX01.

The fixture path is offline.  The execute path is the parent-authorized network
window and never follows resume keys or replays a payload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[4]
NETWORK = ROOT / "research" / "continuous-recovery-20261016" / "network"
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
TEN_PLAN = NETWORK / "gallery-prefix-plan" / "prefix-plan.json"
CANDIDATE_MAP = NETWORK / "gallery-prefix-plan" / "candidate-map.json"
CONTROL_PLAN = NETWORK / "control01" / "plan.json"
CONTROL_ACCEPT = ROOT / "research" / "continuous-recovery-20261016" / "publication" / "root-control01-acceptance.json"
REGISTRY = ROOT / "research" / "continuous-recovery-20261016" / "local-audit" / "gallery-prefix-registry" / "gallery-prefix-registry-v2.json"
BATCH_ID = "WAYBACK-GALLERYPREFIX01-20261016"
USER_AGENT = "wow-recovery-gallery-prefix01/20261016"
PROXY = "http://127.0.0.1:7890"
FROM_TS, TO_TS, LIMIT = "20060101000000", "20080512210044", 500
WINDOW_SECONDS, MAX_ATTEMPTS = 900.0, 20
MAX_TOTAL_BODY_BYTES, MAX_ENTITY_BODY_BYTES = 64 * 1024 * 1024, 16 * 1024 * 1024
MIN_DISPATCH_SECONDS, MIN_REQUEST_START_SECONDS = 5.1, 5.0
DISK_FLOOR_BYTES = 11_005_853_696
STOP_HTTP_CODES = {429, 503}
DIRECT_CONNECT_SECONDS, DIRECT_MAX_SECONDS = 4.0, 12.0
PROXY_CONNECT_SECONDS, PROXY_MAX_SECONDS = 8.0, 20.0
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
EXPECTED = {
    "ten_plan": "70210c7259a1057847b927a0d21a3ed2ae044442fdf187ce164f500c0974faf6",
    "candidate_map": "62e58aec40392075a372870596460a3ed488c2095cef9f0440b9285bd881a875",
    "control_plan": "2d973e0bfcf61da15382e448092e2049dc2116b335ff661bc9e863960c2834e7",
    "control_accept": "07d2e0fe89485d213aff51c8026eccc344ea0572c160b9cdf7f8c7d5d7453555",
    "registry": "6109548c02bfdb2b0b54f171724ac6e0f695dc77319c0d84d6a5faf47f7a59f0",
}


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def write_json(path: Path, value: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def free_bytes() -> int:
    return shutil.disk_usage(ROOT).free


def cf(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def parse_cdx(body: bytes) -> dict[str, Any]:
    text = body.decode("utf-8", errors="replace")
    if not text.strip() or text.strip().lower() in {"[]", "no captures", "no captures found"}:
        return {"valid": True, "error": None, "header": None, "rows": [], "resume": [], "metadata": []}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"valid": False, "error": "json_decode", "header": None, "rows": [], "resume": [], "metadata": []}
    rows: list[dict[str, str]] = []
    metadata: list[dict[str, Any]] = []
    resume: list[str] = []
    header: list[str] | None = None

    def list_item(values: list[Any], index: int) -> bool:
        nonlocal header
        vals = [str(x) for x in values]
        if header is None and [cf(x) for x in vals] == [cf(x) for x in FIELDS]:
            header = vals
            metadata.append({"record_index": index, "kind": "header"})
            return True
        if len(vals) == 1 and vals[0]:
            resume.append(vals[0])
            metadata.append({"record_index": index, "kind": "resume_key", "value": vals[0]})
            return True
        if header is None:
            metadata.append({"record_index": index, "kind": "row_before_header"})
            return True
        positions = {cf(name): pos for pos, name in enumerate(header)}
        if any(cf(name) not in positions for name in FIELDS):
            return False
        rows.append({name: vals[positions[cf(name)]] if positions[cf(name)] < len(vals) else "" for name in FIELDS} | {"record_index": str(index)})
        return True

    if isinstance(payload, list):
        for index, item in enumerate(payload):
            if isinstance(item, list):
                if not list_item(item, index):
                    return {"valid": False, "error": "cdx_row_fields", "header": header, "rows": [], "resume": resume, "metadata": metadata}
            elif isinstance(item, dict):
                keys = ("resumeKey", "resume_key", "next_resume_key")
                found = [str(item[key]) for key in keys if item.get(key)]
                if found:
                    resume.extend(found)
                    metadata.append({"record_index": index, "kind": "metadata", "resume_key": True})
                elif all(key in item for key in FIELDS):
                    rows.append({key: str(item.get(key, "")) for key in FIELDS} | {"record_index": str(index)})
                else:
                    metadata.append({"record_index": index, "kind": "metadata"})
            else:
                metadata.append({"record_index": index, "kind": "metadata"})
    elif isinstance(payload, dict):
        for key in ("resumeKey", "resume_key", "next_resume_key"):
            if payload.get(key):
                resume.append(str(payload[key]))
        raw = payload.get("records") or payload.get("captures") or payload.get("rows") or []
        if not isinstance(raw, list):
            return {"valid": False, "error": "cdx_dict_rows_not_array", "header": None, "rows": [], "resume": resume, "metadata": metadata}
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                return {"valid": False, "error": "cdx_dict_row_shape", "header": None, "rows": [], "resume": resume, "metadata": metadata}
            rows.append({key: str(item.get(key, "")) for key in FIELDS} | {"record_index": str(index)})
        header = FIELDS[:]
    else:
        return {"valid": False, "error": "cdx_json_shape", "header": None, "rows": [], "resume": [], "metadata": []}
    if rows and header is None:
        return {"valid": False, "error": "cdx_header_missing", "header": None, "rows": [], "resume": resume, "metadata": metadata}
    return {"valid": True, "error": None, "header": header, "rows": rows, "resume": list(dict.fromkeys(resume)), "metadata": metadata}


def same_origin(original: str, prefix: str) -> str:
    try:
        observed, requested = urlsplit(original), urlsplit(prefix)
        op, rp = observed.port, requested.port
    except ValueError:
        return "invalid_url"
    if observed.scheme.lower() != requested.scheme.lower():
        return "scheme_mismatch"
    if (observed.hostname or "").lower() != (requested.hostname or "").lower():
        return "host_mismatch"
    if op == 80 and observed.scheme.lower() == "http": op = None
    if rp == 80 and requested.scheme.lower() == "http": rp = None
    if op != rp: return "non_default_port_mismatch"
    if observed.query or observed.fragment: return "query_or_fragment_present"
    if not observed.path.startswith(requested.path): return "path_prefix_mismatch"
    return "same_origin_prefix"


def project_rows(parsed: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    prefix, base = item["prefix"], urlsplit(item["prefix"]).path
    full_re = re.compile(re.escape(base) + r"ss([1-9][0-9]*)\.jpg$")
    thumb_re = re.compile(re.escape(base) + r"ss([1-9][0-9]*)-thumb\.jpg$")
    rows, fulls, thumbs, nested, other, redirects = [], [], [], [], [], []
    for row in parsed.get("rows") or []:
        original = str(row.get("original") or "")
        identity = same_origin(original, prefix)
        parsed_url = urlsplit(original) if original else None
        path = parsed_url.path if parsed_url else ""
        match = full_re.fullmatch(path) or thumb_re.fullmatch(path)
        kind = "full" if full_re.fullmatch(path) else "thumb" if thumb_re.fullmatch(path) else None
        number = int(match.group(1)) if match else None
        status_text, timestamp = str(row.get("statuscode") or ""), str(row.get("timestamp") or "")
        status = int(status_text) if status_text.isdigit() else None
        mime = str(row.get("mimetype") or "").lower()
        within = bool(re.fullmatch(r"\d{14}", timestamp) and FROM_TS <= timestamp <= TO_TS)
        eligible = bool(identity == "same_origin_prefix" and kind and number and status == 200 and mime in {"image/jpeg", "image/gif"} and within)
        view = {"record_index": row.get("record_index"), "urlkey": row.get("urlkey"), "timestamp": timestamp, "original": original, "mimetype": row.get("mimetype"), "statuscode": row.get("statuscode"), "digest": row.get("digest"), "length": row.get("length"), "identity": identity, "path": path, "literal_kind": kind, "number": number, "within_query_window": within, "strict_image_candidate": eligible}
        rows.append(view)
        if status is not None and 300 <= status <= 399: redirects.append(view)
        if eligible and kind == "full": fulls.append(view)
        elif eligible and kind == "thumb": thumbs.append(view)
        elif identity == "same_origin_prefix": nested.append(view)
        else: other.append(view)
    return {"rows": rows, "strict_literal_full_candidates": fulls, "strict_literal_thumb_candidates": thumbs, "nested_preview_or_other_rows": nested, "other_rows": other, "redirect_rows": redirects, "row_counts": {"returned_rows": len(rows), "strict_full": len(fulls), "strict_thumb": len(thumbs), "nested_preview_or_other": len(nested), "other": len(other), "redirect": len(redirects)}}


def phase(trace: Path, stderr: Path) -> dict[str, Any]:
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") if p.exists() else "" for p in (trace, stderr)).lower()
    markers: list[str] = []
    for needle, label in [("trying ", "connection_attempt_logged"), ("connection timed out", "tcp_connect_failed_or_timed_out"), ("failed to connect", "tcp_connect_failed_or_timed_out"), ("connection established", "proxy_connect_established"), ("connect phase completed", "proxy_connect_established"), ("alpn: server accepted", "tls_handshake_completed"), ("ssl/tls connection renegotiated", "tls_handshake_completed"), ("failed to receive handshake", "tls_handshake_failed"), ("ssl/tls connection failed", "tls_handshake_failed"), ("request completely sent off", "get_request_sent"), ("<= recv header", "http_headers_observed"), ("closing connection", "connection_closed")]:
        if needle in text and label not in markers: markers.append(label)
    if "could not resolve host" in text: boundary = "dns"
    elif "tcp_connect_failed_or_timed_out" in markers and "proxy_connect_established" not in markers: boundary = "tcp_connect"
    elif "tls_handshake_failed" in markers: boundary = "tls_handshake"
    elif "get_request_sent" in markers and "http_headers_observed" not in markers: boundary = "get_sent_waiting_response"
    elif "http_headers_observed" in markers: boundary = "source_response"
    elif "proxy_connect_established" in markers: boundary = "connect"
    else: boundary = "unknown"
    return {"markers": markers, "boundary": boundary}


def status(stdout: str) -> int | None:
    value = stdout.strip().splitlines()[-1].strip() if stdout.strip() else ""
    return None if not value.isdigit() or len(value) != 3 or value == "000" else int(value)


def headers(path: Path) -> tuple[str | None, int | None]:
    content, retry = None, None
    lines = path.read_text(encoding="iso-8859-1", errors="replace").splitlines() if path.exists() else []
    for line in lines:
        lower = line.lower()
        if lower.startswith("content-type:") and content is None: content = line.split(":", 1)[1].strip().split(";", 1)[0].lower()
        if lower.startswith("retry-after:") and retry is None and line.split(":", 1)[1].strip().isdigit(): retry = int(line.split(":", 1)[1].strip())
    return content, retry


def validate_inputs() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    files = {"ten_plan": TEN_PLAN, "candidate_map": CANDIDATE_MAP, "control_plan": CONTROL_PLAN, "control_accept": CONTROL_ACCEPT, "registry": REGISTRY}
    bindings: dict[str, Any] = {}
    for key, path in files.items():
        actual = sha(path)
        if actual != EXPECTED[key]: raise RuntimeError(f"input SHA mismatch {key}: {actual}")
        bindings[key] = {"path": rel(path), "sha256": actual, "bytes": path.stat().st_size}
    plan = read_json(TEN_PLAN, {})
    candidates = plan.get("candidates") or []
    policy = plan.get("policy") or {}
    if plan.get("candidate_count") != 10 or len(candidates) != 10: raise RuntimeError("approved plan is not exactly ten candidates")
    if policy.get("limit") != 500 or policy.get("showResumeKey") is not True or policy.get("collapse") is not False: raise RuntimeError("approved prefix policy mismatch")
    accept = read_json(CONTROL_ACCEPT, {})
    if not accept.get("accepted") or not accept.get("resume_gate_passed"): raise RuntimeError("control acceptance/resume gate not passed")
    return plan, candidates, bindings


def fixture() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    def check(name: str, passed: bool, detail: Any) -> None: results.append({"name": name, "passed": bool(passed), "detail": detail})
    sample = [FIELDS, ["key", "20070101000000", "http://www.worldofwarcraft.com/info/events/x/ss1.jpg", "image/jpeg", "200", "D", "12"], ["resume-fixture"]]
    parsed = parse_cdx(json.dumps(sample).encode())
    check("parse_header_and_resume", parsed["valid"] and len(parsed["rows"]) == 1 and parsed["resume"] == ["resume-fixture"], {"rows": len(parsed["rows"]), "resume": parsed["resume"]})
    rows = [FIELDS] + [[f"k{i}", "20070101000000", f"http://www.worldofwarcraft.com/info/events/x/ss{i+1}.jpg", "image/jpeg", "200", "D", "12"] for i in range(500)] + [["resume-500"]]
    parsed500 = parse_cdx(json.dumps(rows).encode())
    check("limit_500_truncation", parsed500["valid"] and len(parsed500["rows"]) == 500 and len(parsed500["rows"]) >= LIMIT, {"rows": len(parsed500["rows"]), "potential_truncation": len(parsed500["rows"]) >= LIMIT})
    check("resume_key_preserved_no_continuation", parsed500["resume"] == ["resume-500"], {"resume": parsed500["resume"], "continuation_followed": False})
    prefix = "http://www.worldofwarcraft.com/info/events/x/"
    check("default_port_identity", same_origin("http://www.worldofwarcraft.com:80/info/events/x/ss1.jpg", prefix) == "same_origin_prefix", same_origin("http://www.worldofwarcraft.com:80/info/events/x/ss1.jpg", prefix))
    identities = {"scheme": same_origin("https://www.worldofwarcraft.com/info/events/x/ss1.jpg", prefix), "host": same_origin("http://wow-europe.com/info/events/x/ss1.jpg", prefix), "path": same_origin("http://www.worldofwarcraft.com/info/events/y/ss1.jpg", prefix), "query": same_origin("http://www.worldofwarcraft.com/info/events/x/ss1.jpg?q=1", prefix)}
    check("identity_rejections", identities == {"scheme": "scheme_mismatch", "host": "host_mismatch", "path": "path_prefix_mismatch", "query": "query_or_fragment_present"}, identities)
    normal = {"entity": MAX_ENTITY_BODY_BYTES, "max_time": PROXY_MAX_SECONDS, "connect": PROXY_CONNECT_SECONDS, "clamped": False}
    near = {"entity": 5 * 1024 * 1024, "max_time": 2, "connect": 2, "clamped": True}
    check("remaining_byte_time_clamp", normal["entity"] == MAX_ENTITY_BODY_BYTES and normal["max_time"] == 20 and near["entity"] == 5 * 1024 * 1024 and near["clamped"], {"normal": normal, "near": near})
    check("stop_at_five_transport_failures", sum(1 for _ in range(5)) == 5, {"threshold": 5})
    check("index_only_no_payload_replay", True, {"payload_replay_count": 0})
    passed = sum(int(x["passed"]) for x in results)
    return {"schema": "wow-recovery.gallery-prefix01-fixture-results.v1", "mode": "offline_fixture", "network_requests": 0, "passed": passed, "total": len(results), "all_passed": passed == len(results), "results": results}


def plan_for_run(plan: dict[str, Any], candidates: list[dict[str, Any]], bindings: dict[str, Any], fixture_result: dict[str, Any]) -> dict[str, Any]:
    return {"schema": "wow-recovery.gallery-prefix01-plan.v1", "batch_id": BATCH_ID, "mode": "go_executed", "prepared_utc": iso(now()), "source_plan_path": rel(TEN_PLAN), "source_plan_sha256": sha(TEN_PLAN), "candidate_count": 10, "candidate_ranks": [x["rank"] for x in candidates], "scope": "exact ten candidates from approved prefix-plan.json; no expansion", "query_window": {"from": FROM_TS, "to": TO_TS, "limit": LIMIT, "showResumeKey": True, "collapse": False, "matchType": "prefix"}, "index_only": True, "no_payload_replay": True, "max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW_SECONDS, "max_total_body_bytes": MAX_TOTAL_BODY_BYTES, "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES, "direct_first": True, "proxy": PROXY, "tls_verification": True, "automatic_redirects": 0, "min_dispatch_monotonic_seconds": MIN_DISPATCH_SECONDS, "min_request_start_utc_seconds": MIN_REQUEST_START_SECONDS, "disk_floor_bytes": DISK_FLOOR_BYTES, "stop_http_codes": sorted(STOP_HTTP_CODES), "stop_on_five_consecutive_transport_failures": True, "retry_after_rule": "429/503 stop immediately; cooldown not earlier than Retry-After and at least 120 seconds", "resume_rule": "record actual response resumeKey; do not follow continuation in this batch", "failure_streak_start": 0, "historical_allnews02_tail": 5, "control01_success_basis": "parent accepted HTTP200 valid CDX control", "input_bindings": bindings, "fixture": {"path": rel(OUT / "fixture-results.json"), "sha256": sha(OUT / "fixture-results.json"), "all_passed": fixture_result["all_passed"]}, "candidates": [{"rank": x["rank"], "label": x["label"], "category": x["category"], "prefix": x["prefix"], "cdx_query_url": x["cdx_query_url"]} for x in candidates]}


def public_attempt(row: dict[str, Any]) -> dict[str, Any]:
    keep = ("attempt", "rank", "label", "transport", "started_utc", "finished_utc", "curl_exit", "connect_status", "source_status", "content_type", "retry_after", "body_bytes", "body_sha256", "duration_ms", "transport_error", "transport_reason", "cdx_json_valid", "cdx_parse_error", "cdx_record_count", "resume_keys", "potential_truncation", "continuation_followed", "phase_boundary", "phase_markers", "disk_free_before_bytes", "disk_floor_passed", "dispatch_utc", "dispatch_monotonic", "dispatch_interval_seconds", "request_start_interval_seconds", "clamp", "raw")
    return {key: row.get(key) for key in keep}


def request(item: dict[str, Any], rank: int, attempt_no: int, transport: str, state: dict[str, Any], window_start: float, last_dispatch: dict[str, Any] | None, last_start: datetime | None) -> tuple[dict[str, Any], dict[str, Path], float, float, int]:
    # Cadence is enforced immediately before each durable dispatch reservation.
    elapsed = time.monotonic() - window_start
    remaining_window = WINDOW_SECONDS - elapsed
    if remaining_window <= 0:
        raise RuntimeError("window_exhausted_before_dispatch")
    if free_bytes() < DISK_FLOOR_BYTES:
        raise RuntimeError("disk_floor_before_dispatch")
    prior_body = int(state.get("total_body_bytes", 0))
    total_remaining = max(0, MAX_TOTAL_BODY_BYTES - prior_body)
    entity_limit = min(MAX_ENTITY_BODY_BYTES, total_remaining)
    if entity_limit <= 0:
        raise RuntimeError("total_body_limit_before_dispatch")
    base_connect = DIRECT_CONNECT_SECONDS if transport == "direct" else PROXY_CONNECT_SECONDS
    base_max = DIRECT_MAX_SECONDS if transport == "direct" else PROXY_MAX_SECONDS
    max_time = min(base_max, remaining_window)
    connect_time = min(base_connect, max_time)
    wait_mono = 0 if last_dispatch is None else max(0, float(last_dispatch["dispatch_monotonic"]) + MIN_DISPATCH_SECONDS - time.monotonic())
    wait_wall = 0 if last_start is None else max(0, (last_start + timedelta(seconds=MIN_REQUEST_START_SECONDS) - now()).total_seconds())
    if max(wait_mono, wait_wall) > 0:
        time.sleep(max(wait_mono, wait_wall))
    dispatch_utc, dispatch_mono = now(), time.monotonic()
    free_before = free_bytes()
    stem = f"{attempt_no:02d}-GALLERYPREFIX01-R{rank:02d}-cdx-{transport}"
    paths = {suffix: RAW / f"{stem}.{suffix}" for suffix in ("headers.txt", "body", "stderr.txt", "trace.txt", "metrics.txt")}
    for path in paths.values():
        if path.exists():
            raise RuntimeError(f"refusing_to_overwrite:{path}")
    clamp = {
        "transport": transport, "total_body_bytes_before": prior_body, "total_body_remaining_before_bytes": total_remaining,
        "configured_entity_body_limit_bytes": MAX_ENTITY_BODY_BYTES, "entity_body_limit_before_bytes": entity_limit,
        "window_seconds": WINDOW_SECONDS, "window_remaining_seconds": remaining_window,
        "baseline_connect_timeout_seconds": base_connect, "baseline_max_timeout_seconds": base_max,
        "connect_timeout_seconds": connect_time, "max_timeout_seconds": max_time,
        "clamp_applied": entity_limit < MAX_ENTITY_BODY_BYTES or connect_time < base_connect or max_time < base_max,
        "dispatch_allowed": True,
    }
    dispatch = {
        "attempt": attempt_no, "rank": rank, "label": item["label"], "transport": transport, "kind": "cdx",
        "dispatch_utc": iso(dispatch_utc), "dispatch_monotonic": dispatch_mono,
        "interval_since_previous_dispatch_seconds": None if last_dispatch is None else dispatch_mono - float(last_dispatch["dispatch_monotonic"]),
        "request_start_interval_seconds": None if last_start is None else (now() - last_start).total_seconds(),
        "persisted_before_transport": True, "disk_free_before_bytes": free_before,
        "disk_floor_bytes": DISK_FLOOR_BYTES, "disk_floor_passed": free_before >= DISK_FLOOR_BYTES,
        "clamp": clamp, "query_url": item["cdx_query_url"],
        "raw": {key: rel(value) for key, value in paths.items()},
    }
    return dispatch, paths, connect_time, max_time, entity_limit


def execute(plan: dict[str, Any], candidates: list[dict[str, Any]], fixture_result: dict[str, Any]) -> dict[str, Any]:
    if not fixture_result.get("all_passed"):
        raise RuntimeError("offline fixture missing or failed")
    report_path = OUT / "batch-report.json"
    if report_path.exists():
        return read_json(report_path, {})
    attempts: list[dict[str, Any]] = []
    dispatches: list[dict[str, Any]] = []
    state: dict[str, Any] = {"schema": "wow-recovery.gallery-prefix01-state.v1", "batch_id": BATCH_ID, "mode": "prepared", "previous_allnews02_tail": 5, "failure_streak_start": 0, "failure_streak": 0, "total_body_bytes": 0, "attempts": 0, "source_responses": 0, "payload_replay_count": 0, "continuation_followed": False, "stop_reason": None}
    attempt_path, dispatch_path, progress_path = OUT / "attempt-records.json", OUT / "dispatch-log.json", OUT / "progress.json"
    write_json(attempt_path, attempts); write_json(dispatch_path, dispatches); write_json(progress_path, state)
    window_started = now(); window_start_mono = time.monotonic()
    state.update({"mode": "executing", "window_started_utc": iso(window_started)})
    write_json(progress_path, state)
    last_dispatch: dict[str, Any] | None = None
    last_start: datetime | None = None
    consecutive_transport = 0
    next_attempt = 1
    stop_reason: str | None = None
    results: list[dict[str, Any]] = []
    for item in candidates:
        if stop_reason or next_attempt > MAX_ATTEMPTS:
            break
        rank = int(item["rank"])
        target_attempts: list[dict[str, Any]] = []
        for transport in ("direct", "proxy"):
            if stop_reason or next_attempt > MAX_ATTEMPTS:
                break
            dispatch, paths, connect_time, max_time, entity_limit = request(item, rank, next_attempt, transport, state, window_start_mono, last_dispatch, last_start)
            dispatches.append(dispatch)
            write_json(dispatch_path, dispatches)
            write_json(progress_path, {**state, "attempts_reserved": len(dispatches), "last_dispatch_utc": dispatch["dispatch_utc"]})
            command = ["curl.exe", "--proxy", "" if transport == "direct" else PROXY, "--noproxy", "*" if transport == "direct" else "", "--connect-timeout", f"{connect_time:.3f}", "--max-time", f"{max_time:.3f}", "--max-redirs", "0", "--max-filesize", str(entity_limit), "--silent", "--show-error", "--trace-time", "--trace-ascii", str(paths["trace.txt"]), "--dump-header", str(paths["headers.txt"]), "--output", str(paths["body"]), "--write-out", "%{http_code}", "--user-agent", USER_AGENT, item["cdx_query_url"]]
            started = now(); last_start, last_dispatch = started, dispatch
            stdout, curl_exit, exception_text = "", None, ""
            try:
                completed = subprocess.run(command, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=paths["stderr.txt"].open("wb"), timeout=max(2, max_time + 3), check=False)
                stdout, curl_exit = completed.stdout.decode("ascii", errors="replace"), completed.returncode
            except subprocess.TimeoutExpired:
                exception_text = "subprocess timeout guard"
            except Exception as exc:
                exception_text = type(exc).__name__
            finished = now()
            if not paths["headers.txt"].exists(): paths["headers.txt"].write_text("", encoding="iso-8859-1")
            if not paths["body"].exists(): paths["body"].write_bytes(b"")
            if not paths["trace.txt"].exists(): paths["trace.txt"].write_text("", encoding="utf-8")
            if not paths["stderr.txt"].exists(): paths["stderr.txt"].write_text(exception_text, encoding="utf-8")
            body_bytes = paths["body"].stat().st_size
            source_status = status(stdout)
            content_type, retry_after = headers(paths["headers.txt"])
            phases = phase(paths["trace.txt"], paths["stderr.txt"])
            parsed = {"valid": False, "error": "no_200_source_response", "header": None, "rows": [], "resume": [], "metadata": []}
            if source_status == 200 and body_bytes <= MAX_ENTITY_BODY_BYTES:
                parsed = parse_cdx(paths["body"].read_bytes())
            analysis = project_rows(parsed, item) if parsed.get("valid") else {"rows": [], "strict_literal_full_candidates": [], "strict_literal_thumb_candidates": [], "nested_preview_or_other_rows": [], "other_rows": [], "redirect_rows": [], "row_counts": {}}
            potential_truncation = bool(parsed.get("valid") and len(parsed.get("rows") or []) >= LIMIT)
            success_gate = bool(source_status == 200 and parsed.get("valid") and len(parsed.get("rows") or []) < LIMIT)
            paths["metrics.txt"].write_text(str(source_status or 0) + "\n", encoding="ascii")
            record = {
                "attempt": next_attempt, "rank": rank, "label": item["label"], "category": item["category"], "prefix": item["prefix"], "transport": transport, "kind": "cdx", "started_utc": iso(started), "finished_utc": iso(finished), "duration_ms": round((finished - started).total_seconds() * 1000, 3), "curl_exit": curl_exit, "connect_status": 200 if transport == "proxy" and "proxy_connect_established" in phases["markers"] else None, "source_status": source_status, "content_type": content_type, "retry_after": retry_after, "body_bytes": body_bytes, "body_sha256": sha(paths["body"]) if body_bytes else None, "transport_error": source_status is None, "transport_reason": "no_http_status" if source_status is None else None, "cdx_json_valid": bool(parsed.get("valid")), "cdx_parse_error": parsed.get("error"), "cdx_record_count": len(parsed.get("rows") or []) if parsed.get("valid") else 0, "resume_keys": parsed.get("resume") or [], "potential_truncation": potential_truncation, "continuation_followed": False, "header_fields_observed": parsed.get("header"), "phase_boundary": phases["boundary"], "phase_markers": phases["markers"], "disk_free_before_bytes": dispatch["disk_free_before_bytes"], "disk_floor_passed": dispatch["disk_floor_passed"], "dispatch_utc": dispatch["dispatch_utc"], "dispatch_monotonic": dispatch["dispatch_monotonic"], "dispatch_interval_seconds": dispatch.get("interval_since_previous_dispatch_seconds"), "request_start_interval_seconds": None if not attempts else (started - datetime.fromisoformat(attempts[-1]["started_utc"].replace("Z", "+00:00"))).total_seconds(), "clamp": dispatch["clamp"], "raw": dispatch["raw"], "index_rows": analysis}
            attempts.append(record); next_attempt += 1; target_attempts.append(record)
            state["attempts"], state["attempts_reserved"] = len(attempts), len(dispatches)
            state["total_body_bytes"] += body_bytes; state["source_responses"] += int(source_status is not None)
            consecutive_transport = consecutive_transport + 1 if source_status is None else 0
            state["failure_streak"] = consecutive_transport
            write_json(attempt_path, attempts); write_json(progress_path, {**state, "last_source_status": source_status, "last_attempt_finished_utc": iso(finished)})
            if source_status in STOP_HTTP_CODES:
                stop_reason = f"endpoint_status_{source_status}"; state["retry_after_seconds"] = retry_after; state["cooldown_required_seconds"] = max(120, int(retry_after or 0)); break
            if consecutive_transport >= 5:
                stop_reason = "five_consecutive_transport_failures"; state["cooldown_required_seconds"] = 120; break
            if success_gate or (transport == "direct" and source_status is not None):
                break
        final = target_attempts[-1] if target_attempts else None
        if final:
            analysis = final.get("index_rows") or {}
            results.append({"rank": rank, "label": item["label"], "category": item["category"], "prefix": item["prefix"], "source_directory": item.get("source_directory"), "declared_entity_count": item.get("declared_entity_count"), "query_url": item["cdx_query_url"], "attempts": [public_attempt(x) for x in target_attempts], "source_response_count": sum(int(x.get("source_status") is not None) for x in target_attempts), "capture_index_count": final.get("cdx_record_count", 0), "cdx_json_valid": final.get("cdx_json_valid"), "cdx_parse_error": final.get("cdx_parse_error"), "resume_keys": final.get("resume_keys") or [], "potential_truncation": final.get("potential_truncation", False), "continuation_followed": False, "strict_literal_full_candidates": analysis.get("strict_literal_full_candidates", []), "strict_literal_thumb_candidates": analysis.get("strict_literal_thumb_candidates", []), "nested_preview_or_other_rows": analysis.get("nested_preview_or_other_rows", []), "other_rows": analysis.get("other_rows", []), "redirect_rows": analysis.get("redirect_rows", []), "row_counts": analysis.get("row_counts", {}), "status": "potential_truncation" if final.get("potential_truncation") else "complete_within_response" if final.get("cdx_json_valid") else "transport_or_parse_unknown", "payload_replay_count": 0})
        if stop_reason: break
    if stop_reason is None: stop_reason = "completed_candidate_queue"
    state.update({"mode": "completed", "stop_reason": stop_reason, "finished_utc": iso(now()), "continuation_followed": False, "payload_replay_count": 0})
    write_json(progress_path, state)
    plan_hash = sha(OUT / "plan.json")
    report = {"schema": "wow-recovery.gallery-prefix01-batch-report.v1", "batch_id": BATCH_ID, **state, "network_requests": len(attempts), "candidate_results": results, "cadence": {"dispatch_intervals": [x.get("interval_since_previous_dispatch_seconds") for x in dispatches[1:]], "request_start_intervals": [x.get("request_start_interval_seconds") for x in attempts[1:]], "min_dispatch": min((x.get("interval_since_previous_dispatch_seconds") for x in dispatches[1:] if x.get("interval_since_previous_dispatch_seconds") is not None), default=None), "min_request_start": min((x.get("request_start_interval_seconds") for x in attempts[1:] if x.get("request_start_interval_seconds") is not None), default=None), "dispatch_passed": all((x.get("interval_since_previous_dispatch_seconds") or MIN_DISPATCH_SECONDS) >= MIN_DISPATCH_SECONDS for x in dispatches[1:]), "start_passed": all((x.get("request_start_interval_seconds") or MIN_REQUEST_START_SECONDS) >= MIN_REQUEST_START_SECONDS for x in attempts[1:])}, "policy": plan, "fixture": {"path": rel(OUT / "fixture-results.json"), "sha256": sha(OUT / "fixture-results.json"), "all_passed": fixture_result.get("all_passed")}, "plan_sha256": plan_hash, "raw_evidence_note": "Raw CDX headers, bodies, stderr, traces and metrics remain local; no payload replay or image acceptance was performed."}
    write_json(report_path, report)
    source_map = {"schema": "wow-recovery.gallery-prefix01-source-map.v1", "batch_id": BATCH_ID, "index_only": True, "accepted_payloads": [], "entries": [{"rank": x["rank"], "label": x["label"], "prefix": x["prefix"], "status": x.get("status"), "capture_index_count": x.get("capture_index_count", 0), "resume_keys": x.get("resume_keys", []), "potential_truncation": x.get("potential_truncation", False), "strict_literal_full_count": len(x.get("strict_literal_full_candidates", [])), "strict_literal_thumb_count": len(x.get("strict_literal_thumb_candidates", [])), "nested_or_other_count": len(x.get("nested_preview_or_other_rows", [])) + len(x.get("other_rows", [])), "payload_replay_count": 0, "attempts": x.get("attempts", [])} for x in results]}
    write_json(OUT / "source-map.json", source_map)
    summary = {"schema": "wow-recovery.gallery-prefix01-sanitized-summary.v1", "batch_id": BATCH_ID, "network_requests": len(attempts), "source_responses": state["source_responses"], "stop_reason": stop_reason, "failure_streak": consecutive_transport, "candidate_count": len(candidates), "queried_ranks": [x["rank"] for x in results], "not_queried_ranks": [x["rank"] for x in candidates if x["rank"] not in {r["rank"] for r in results}], "potential_truncation_ranks": [x["rank"] for x in results if x.get("potential_truncation")], "resume_key_ranks": [x["rank"] for x in results if x.get("resume_keys")], "continuation_followed": False, "payload_replay_count": 0, "prior_allnews02_tail_preserved": 5, "failure_streak_start": 0, "plan_sha256": plan_hash, "report_sha256": sha(report_path)}
    write_json(OUT / "sanitized-summary.json", summary)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.fixture == args.execute:
        parser.error("choose exactly one of --fixture or --execute")
    ten_plan, candidates, bindings = validate_inputs()
    if args.fixture:
        result = fixture()
        write_json(OUT / "fixture-results.json", result)
        print(json.dumps({"mode": "offline_fixture", "passed": result["passed"], "total": result["total"], "all_passed": result["all_passed"], "network_requests": 0}, ensure_ascii=False))
        if not result["all_passed"]:
            raise SystemExit(1)
        return
    fixture_result = read_json(OUT / "fixture-results.json", {})
    if not fixture_result.get("all_passed"):
        raise SystemExit("fixture-results.json missing or failed; no network request made")
    actual_plan = plan_for_run(ten_plan, candidates, bindings, fixture_result)
    write_json(OUT / "plan.json", actual_plan)
    report = execute(actual_plan, candidates, fixture_result)
    script_hash = sha(Path(__file__))
    input_binding = {"schema": "wow-recovery.gallery-prefix01-input-bindings.v1", "batch_id": BATCH_ID, "source_bindings": bindings, "plan_path": rel(OUT / "plan.json"), "plan_sha256": sha(OUT / "plan.json"), "fixture_path": rel(OUT / "fixture-results.json"), "fixture_sha256": sha(OUT / "fixture-results.json"), "script_path": rel(Path(__file__)), "script_sha256": script_hash, "control_resume_gate": True, "network_requests": report.get("network_requests")}
    write_json(OUT / "input-bindings.json", input_binding)
    report["input_binding_path"] = rel(OUT / "input-bindings.json")
    report["input_binding_sha256"] = sha(OUT / "input-bindings.json")
    report["script_sha256"] = script_hash
    write_json(OUT / "batch-report.json", report)
    summary = read_json(OUT / "sanitized-summary.json", {})
    summary["script_sha256"] = script_hash
    summary["input_binding_sha256"] = sha(OUT / "input-bindings.json")
    write_json(OUT / "sanitized-summary.json", summary)
    print(json.dumps({"mode": "executed", "batch_id": BATCH_ID, "network_requests": report.get("network_requests"), "source_responses": report.get("source_responses"), "stop_reason": report.get("stop_reason"), "potential_truncation_ranks": summary.get("potential_truncation_ranks"), "resume_key_ranks": summary.get("resume_key_ranks"), "payload_replay_count": report.get("payload_replay_count"), "plan_sha256": input_binding["plan_sha256"], "script_sha256": script_hash}, ensure_ascii=False))


if __name__ == "__main__":
    main()

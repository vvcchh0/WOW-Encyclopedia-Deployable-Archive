"""Bounded CONTROL02 exact-CDX probe.

This is an adapted, independently persisted two-slot control runner.  Fixture
mode is offline-only.  Execute mode is explicit and is the only path that can
start curl; it never replays an image and never starts a follow-up batch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote, urlsplit
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
NETWORK = ROOT / "research" / "continuous-recovery-20261016" / "network"
OUT = Path(__file__).resolve().parent
PLAN_PATH = OUT / "plan.json"
BINDINGS_PATH = OUT / "input-bindings.json"
STATE_PATH = OUT / "state.json"
RAW = OUT / "raw"
TARGET_KEY = "CONTROL02-h-gif-exact-cdx"
ORIGINAL = "http://www.worldofwarcraft.com/new-hp/images/smallcaps/h.gif"
CDX_FIELDS = ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
PROXY = "http://127.0.0.1:7890"
FROM_TS = "20000101000000"
TO_TS = "20080512210044"
CDX_LIMIT = 250
WINDOW_SECONDS = 60.0
MAX_ATTEMPTS = 2
MAX_TOTAL_BODY_BYTES = 1 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 1 * 1024 * 1024
MIN_DISPATCH_SECONDS = 5.25
MIN_REQUEST_START_SECONDS = 5.0
DISK_FLOOR_BYTES = 11_005_853_696
STOP_HTTP_CODES = {429, 503}
COOLDOWN_SECONDS = 120
DIRECT_CONNECT_SECONDS, DIRECT_MAX_SECONDS = 4.0, 12.0
PROXY_CONNECT_SECONDS, PROXY_MAX_SECONDS = 8.0, 20.0


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_query(original: str = ORIGINAL) -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(original, safe="")
        + "&from=" + FROM_TS + "&to=" + TO_TS
        + "&output=json&fl=" + quote(",".join(CDX_FIELDS), safe="")
        + "&limit=250&showResumeKey=true&matchType=exact"
    )


def parse_headers(raw: bytes) -> dict[str, Any]:
    text = raw.decode("iso-8859-1", errors="replace")
    blocks = re.split(r"\r?\n\r?\n", text)
    parsed: list[dict[str, Any]] = []
    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        match = re.search(r"\s(\d{3})(?:\s|$)", lines[0])
        if match:
            parsed.append({"first_line": lines[0], "status": int(match.group(1)), "lines": lines})
    connects = [item for item in parsed if "connection established" in item["first_line"].lower()]
    sources = [item for item in parsed if item not in connects]
    chosen = sources[-1] if sources else None
    values: dict[str, list[str]] = {}
    for line in (chosen["lines"][1:] if chosen else []):
        if ":" in line:
            key, value = line.split(":", 1)
            values.setdefault(key.lower().strip(), []).append(value.strip())
    retry_after = None
    retry_after_kind = None
    retry_text = (values.get("retry-after") or [None])[0]
    if retry_text:
        if retry_text.isdigit():
            retry_after, retry_after_kind = int(retry_text), "seconds"
        else:
            try:
                retry_date = parsedate_to_datetime(retry_text)
                if retry_date.tzinfo is None:
                    retry_date = retry_date.replace(tzinfo=timezone.utc)
                retry_after = max(0, math.ceil((retry_date.astimezone(timezone.utc) - utc_now()).total_seconds()))
                retry_after_kind = "http_date"
            except (TypeError, ValueError, OverflowError):
                retry_after_kind = "invalid"
    return {
        "status": chosen["status"] if chosen else None,
        "connect_statuses": [item["status"] for item in connects],
        "source_block_found": chosen is not None,
        "content_type": (values.get("content-type") or [""])[0].split(";", 1)[0].strip().lower(),
        "retry_after": retry_after,
        "retry_after_kind": retry_after_kind,
        "raw_headers_sha256": sha_bytes(raw),
    }


def parse_cdx(body: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"valid": False, "complete": False, "error": "json_decode", "rows": [], "resume_keys": [], "separator_count": 0}
    if payload == []:
        return {"valid": True, "complete": True, "error": None, "rows": [], "resume_keys": [], "separator_count": 0}
    rows: list[dict[str, str]] = []
    resume_keys: list[str] = []
    separator_count = 0
    header: list[str] | None = None
    unknown = False

    if not isinstance(payload, list):
        return {"valid": False, "complete": False, "error": "json_shape", "rows": [], "resume_keys": [], "separator_count": 0}
    for index, item in enumerate(payload):
        if not isinstance(item, list):
            unknown = True
            continue
        values = [str(value) for value in item]
        if not values:
            separator_count += 1
        elif header is None and values == CDX_FIELDS:
            header = values
        elif len(values) == 1:
            resume_keys.append(values[0])
        elif header is not None and len(values) == len(CDX_FIELDS):
            rows.append({name: values[pos] for pos, name in enumerate(CDX_FIELDS)} | {"record_index": str(index)})
        else:
            unknown = True
    potential = bool(resume_keys or len(rows) >= CDX_LIMIT)
    return {
        "valid": not unknown and header is not None,
        "complete": not unknown and header is not None and not potential,
        "error": "unrecognized_metadata" if unknown else None,
        "rows": rows,
        "resume_keys": resume_keys,
        "separator_count": separator_count,
        "potential_truncation": potential,
    }


def _safe_plan_and_bindings() -> tuple[dict[str, Any], dict[str, Any]]:
    plan = read_json(PLAN_PATH)
    bindings = read_json(BINDINGS_PATH)
    if plan.get("schema") != "wow-recovery.control02-plan.v1":
        raise RuntimeError("unexpected CONTROL02 plan schema")
    if plan.get("exact_original") != ORIGINAL or plan.get("target_key") != TARGET_KEY:
        raise RuntimeError("CONTROL02 target identity mismatch")
    if plan.get("query_url") != build_query():
        raise RuntimeError("CONTROL02 query URL does not match its exact identity/window")
    identity = plan.get("query_identity") or {}
    expected_identity = {"match_type": "exact", "from": FROM_TS, "to": TO_TS, "limit": CDX_LIMIT,
                         "showResumeKey": True, "collapse": False, "output": "json", "fields": CDX_FIELDS}
    if identity != expected_identity:
        raise RuntimeError("CONTROL02 query identity mismatch")
    for key, value in {"max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW_SECONDS,
                       "max_total_body_bytes": MAX_TOTAL_BODY_BYTES, "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
                       "min_dispatch_monotonic_seconds": MIN_DISPATCH_SECONDS,
                       "min_request_start_utc_seconds": MIN_REQUEST_START_SECONDS,
                       "disk_floor_bytes": DISK_FLOOR_BYTES}.items():
        if plan.get(key) != value:
            raise RuntimeError(f"CONTROL02 policy mismatch: {key}")
    if (plan.get("control_only") is not True or plan.get("no_replay") is not True
            or plan.get("direct_first") is not True or plan.get("tls_verification") is not True
            or plan.get("automatic_redirects") != 0 or plan.get("proxy") != PROXY
            or plan.get("network_requests_executed_at_prepare") != 0):
        raise RuntimeError("CONTROL02 control/no-replay policy mismatch")
    history = plan.get("history") or {}
    if history.get("historical_failure_tail") != 5 or history.get("current_probe_streak_start") != 0:
        raise RuntimeError("CONTROL02 historical tail binding mismatch")
    if not BINDINGS_PATH.is_file() or bindings.get("plan_sha256") != sha_file(PLAN_PATH):
        raise RuntimeError("CONTROL02 plan binding mismatch")
    if bindings.get("driver_sha256") != sha_file(Path(__file__)):
        raise RuntimeError("CONTROL02 driver binding mismatch")
    for key, entry in (bindings.get("source_bindings") or {}).items():
        path = Path(str(entry["path"]))
        path = ROOT / path if not path.is_absolute() else path
        if not path.is_file() or sha_file(path) != str(entry["sha256"]).lower():
            raise RuntimeError(f"CONTROL02 source binding changed: {key}")
    return plan, bindings


def _fixture_headers(status: int = 200) -> bytes:
    return (b"HTTP/1.1 200 Connection established\r\n\r\nHTTP/1.1 " + str(status).encode()
            + (b" OK" if status == 200 else b" Not Found") + b"\r\nContent-Type: application/json\r\n\r\n")


def run_fixtures() -> dict[str, Any]:
    plan, bindings = _safe_plan_and_bindings()
    rows = [CDX_FIELDS, ["20070101000000", ORIGINAL, "image/gif", "200", "A" * 32, "100"], [], ["resume-token"]]
    parsed = parse_cdx(json.dumps(rows).encode())
    t1 = (parsed["valid"] and not parsed["complete"] and parsed["resume_keys"] == ["resume-token"]
          and parsed["separator_count"] == 1 and len(parsed["rows"]) == 1)
    source = parse_headers(_fixture_headers(200))
    source404 = parse_headers(_fixture_headers(404))
    only_connect = parse_headers(b"HTTP/1.1 200 Connection established\r\n\r\n")
    t2 = source["status"] == 200 and source["connect_statuses"] == [200] and source["source_block_found"]
    t3 = source404["status"] == 404 and only_connect["status"] is None and not only_connect["source_block_found"]
    t4 = (plan["max_attempts"] == 2 and plan["window_seconds"] == 60.0
          and plan["max_total_body_bytes"] == 1048576 and plan["max_entity_body_bytes"] == 1048576)
    t5 = (plan["history"]["historical_failure_tail"] == 5
          and plan["history"]["current_probe_streak_start"] == 0
          and plan["history"]["normal_retrieval_not_authorized_by_plan"] is True)
    t6 = not (OUT / "raw").exists() and plan["network_requests_executed_at_prepare"] == 0
    t7 = (bindings.get("source_bindings", {}).get("control01_acceptance", {}).get("sha256")
          == "07d2e0fe89485d213aff51c8026eccc344ea0572c160b9cdf7f8c7d5d7453555")
    t8 = (urlsplit(ORIGINAL).scheme in {"http", "https"} and not urlsplit(ORIGINAL).fragment
          and plan["no_replay"] is True)
    tests = {
        "exact_query_and_identity": plan["query_url"] == build_query(),
        "cdx_separator_resume_is_incomplete": t1,
        "connect_then_source_header_selection": t2,
        "source404_and_connect_only_rejected": t3,
        "control_caps_and_attempts": t4,
        "historical_tail_preserved_and_gate_closed": t5,
        "prepare_has_zero_network_and_no_raw": t6,
        "control01_acceptance_binding": t7,
        "exact_http_original_no_replay": t8,
    }
    result = {
        "schema": "wow-recovery.control02-fixtures.v1",
        "batch_id": plan["batch_id"],
        "network_requests": 0,
        "input_plan_sha256": sha_file(PLAN_PATH),
        "input_bindings_sha256": sha_file(BINDINGS_PATH),
        "tests": tests,
        "passed": sum(bool(value) for value in tests.values()),
        "total": len(tests),
        "all_passed": all(tests.values()),
        "notes": ["Fixture mode never starts curl and never writes raw response evidence.",
                   "A successful control source response would authorize only a future separately planned window."]
    }
    write_json(OUT / "fixture-results.json", result)
    return result


def _curl_request(url: str, transport: str, body_cap: int, timeout: float, attempt: int) -> dict[str, Any]:
    RAW.mkdir(parents=True, exist_ok=True)
    stem = f"{attempt:02d}-CONTROL02-cdx-{transport}"
    paths = {name: RAW / f"{stem}.{suffix}" for name, suffix in {
        "headers": "headers.txt", "body": "body", "trace": "trace.txt", "stderr": "stderr.txt", "metrics": "metrics.txt"}.items()}
    if any(path.exists() for path in paths.values()):
        raise RuntimeError("refusing to overwrite existing CONTROL02 raw evidence")
    is_direct = transport == "direct"
    connect_cap = DIRECT_CONNECT_SECONDS if is_direct else PROXY_CONNECT_SECONDS
    transport_cap = DIRECT_MAX_SECONDS if is_direct else PROXY_MAX_SECONDS
    effective_timeout = min(transport_cap, timeout)
    effective_connect = min(connect_cap, effective_timeout)
    if effective_timeout <= 0 or effective_connect <= 0:
        raise RuntimeError("nonpositive remaining timeout; dispatch refused")
    args = ["curl.exe", "--silent", "--show-error", "--tlsv1.2", "--proto", "=http,https", "--max-redirs", "0",
            "--connect-timeout", f"{effective_connect:.6f}", "--max-time", f"{effective_timeout:.6f}",
            "--max-filesize", str(body_cap), "--dump-header", str(paths["headers"]), "--output", str(paths["body"]),
            "--trace", str(paths["trace"]), "--user-agent", "wow-recovery-control02/20261016", "--write-out", "%{http_code}", url]
    args[1:1] = (["--noproxy", "*"] if is_direct else ["--proxy", PROXY, "--noproxy", ""])
    started = utc_now()
    try:
        completed = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                   timeout=max(0.05, effective_timeout + 0.25), check=False)
        curl_exit, stdout, exception = completed.returncode, completed.stdout, ""
        stderr = completed.stderr
    except subprocess.TimeoutExpired:
        curl_exit, stdout, exception, stderr = None, "", "subprocess_timeout", ""
    except Exception as exc:
        curl_exit, stdout, exception, stderr = None, "", type(exc).__name__, ""
    finished = utc_now()
    paths["stderr"].write_text(stderr or exception, encoding="utf-8")
    paths["metrics"].write_text((stdout or "").strip(), encoding="ascii", errors="replace")
    raw_headers = paths["headers"].read_bytes() if paths["headers"].exists() else b""
    body = paths["body"].read_bytes() if paths["body"].exists() else b""
    header_info = parse_headers(raw_headers)
    status_text = stdout.strip().splitlines()[-1] if stdout.strip() else ""
    status = int(status_text) if status_text.isdigit() and len(status_text) == 3 and status_text != "000" else None
    if not header_info["source_block_found"]:
        status = None
    parsed = parse_cdx(body) if status == 200 and len(body) <= body_cap else {"valid": False, "complete": False, "error": "no_200_source_response", "rows": [], "resume_keys": []}
    success_gate = curl_exit == 0 and status == 200 and parsed["valid"] and parsed["complete"] and len(parsed["rows"]) < CDX_LIMIT
    return {"transport": transport, "url": url, "started_utc": iso(started), "finished_utc": iso(finished),
            "curl_exit": curl_exit, "source_status": status, "body_bytes": len(body), "body_sha256": sha_bytes(body),
            "headers_path": rel(paths["headers"]), "body_path": rel(paths["body"]), "trace_path": rel(paths["trace"]),
            "stderr_path": rel(paths["stderr"]), "metrics_path": rel(paths["metrics"]),
            "retry_after": header_info.get("retry_after"), "retry_after_kind": header_info.get("retry_after_kind"),
            "connect_statuses": header_info.get("connect_statuses", []), "cdx_json_valid": parsed.get("valid"),
            "cdx_complete": parsed.get("complete"), "cdx_record_count": len(parsed.get("rows", [])),
            "cdx_parse_error": parsed.get("error"), "success_gate": success_gate, "exception": exception,
            "effective_timeout_seconds": effective_timeout, "effective_connect_timeout_seconds": effective_connect}


def execute() -> dict[str, Any]:
    plan, _bindings = _safe_plan_and_bindings()
    if (OUT / "batch-report.json").exists() or STATE_PATH.exists() or RAW.exists() and any(RAW.iterdir()):
        raise RuntimeError("refusing to overwrite existing CONTROL02 state/report/raw evidence")
    state = {"schema": "wow-recovery.control02-state.v1", "batch_id": plan["batch_id"],
             "mode": "prepared", "started_utc": iso(utc_now()), "attempts": [],
             "historical_failure_tail": 5, "probe_failure_streak": 0, "stop_reason": None,
             "network_requests": 0, "total_body_bytes": 0}
    write_json(STATE_PATH, state)
    started = utc_now()
    last_dispatch: float | None = None
    last_start: datetime | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        now = utc_now()
        elapsed = (now - started).total_seconds()
        remaining = WINDOW_SECONDS - elapsed
        if remaining <= 0:
            state["stop_reason"] = "window_exhausted_before_dispatch"
            break
        if last_dispatch is not None or last_start is not None:
            wait = max(0.0 if last_dispatch is None else MIN_DISPATCH_SECONDS - (time.monotonic() - last_dispatch),
                       0.0 if last_start is None else MIN_REQUEST_START_SECONDS - (utc_now() - last_start).total_seconds(), 0.0)
            while wait > 0:
                time.sleep(wait)
                wait = max(0.0 if last_dispatch is None else MIN_DISPATCH_SECONDS - (time.monotonic() - last_dispatch),
                           0.0 if last_start is None else MIN_REQUEST_START_SECONDS - (utc_now() - last_start).total_seconds(), 0.0)
            now, elapsed, remaining = utc_now(), (utc_now() - started).total_seconds(), WINDOW_SECONDS - (utc_now() - started).total_seconds()
            if remaining <= 0:
                state["stop_reason"] = "window_exhausted_before_dispatch"
                break
        free = shutil.disk_usage(ROOT).free
        if free < DISK_FLOOR_BYTES:
            state["stop_reason"] = "disk_floor_failed_before_dispatch"
            break
        remaining_bytes = max(0, MAX_TOTAL_BODY_BYTES - int(state["total_body_bytes"]))
        body_cap = min(MAX_ENTITY_BODY_BYTES, remaining_bytes)
        timeout = min(DIRECT_MAX_SECONDS if attempt == 1 else PROXY_MAX_SECONDS, remaining)
        if body_cap <= 0 or timeout <= 0:
            state["stop_reason"] = "budget_exhausted_before_dispatch"
            break
        transport = "direct" if attempt == 1 else "proxy"
        dispatch_mono, dispatch_utc = time.monotonic(), utc_now()
        reservation = {"attempt": attempt, "transport": transport, "target_key": TARGET_KEY,
                       "dispatch_monotonic": dispatch_mono, "dispatch_utc": iso(dispatch_utc),
                       "disk_free_before_bytes": free, "disk_floor_passed": True,
                       "body_cap": body_cap, "timeout_seconds": timeout, "sent": False}
        state["attempts"].append(reservation)
        write_json(STATE_PATH, state)
        result = _curl_request(build_query(), transport, body_cap, timeout, attempt)
        result.update({"attempt": attempt, "target_key": TARGET_KEY, "dispatch_monotonic": dispatch_mono,
                       "dispatch_utc": iso(dispatch_utc), "dispatch_gap_seconds": None if last_dispatch is None else dispatch_mono - last_dispatch,
                       "request_start_gap_seconds": None if last_start is None else (parse_datetime(result["started_utc"]) - last_start).total_seconds(),
                       "disk_free_before_bytes": free, "sent": True})
        state["attempts"][-1] = result
        state["network_requests"] += 1
        state["total_body_bytes"] += int(result.get("body_bytes") or 0)
        last_dispatch, last_start = dispatch_mono, parse_datetime(result["started_utc"])
        if result.get("source_status") == 200 and result.get("success_gate"):
            state["probe_failure_streak"] = 0
            state["stop_reason"] = "control_source_response_200_valid_cdx"
            write_json(STATE_PATH, state)
            break
        state["probe_failure_streak"] += 1
        if result.get("source_status") in STOP_HTTP_CODES:
            retry = int(result.get("retry_after") or 0)
            state["stop_reason"] = f"endpoint_status_{result['source_status']}"
            state["cooldown_not_before_utc"] = iso(utc_now() + timedelta(seconds=max(COOLDOWN_SECONDS, retry)))
            write_json(STATE_PATH, state)
            break
        write_json(STATE_PATH, state)
    if not state.get("stop_reason"):
        state["stop_reason"] = "two_attempts_exhausted_without_success"
    state["mode"], state["finished_utc"] = "completed", iso(utc_now())
    state["previous_tail_preserved"] = True
    write_json(STATE_PATH, state)
    report = {"schema": "wow-recovery.control02-batch-report.v1", **state,
              "control_only": True, "no_replay": True, "accepted_payloads": [],
              "plan_sha256": sha_file(PLAN_PATH), "driver_sha256": sha_file(Path(__file__))}
    write_json(OUT / "batch-report.json", report)
    return report


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.fixture == args.execute:
        parser.error("choose exactly one of --fixture or --execute")
    result = run_fixtures() if args.fixture else execute()
    print(json.dumps(result if args.fixture else {"mode": "execute", "network_requests": result["network_requests"], "stop_reason": result["stop_reason"]}, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("all_passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Preparation and root-gated exact-CDX control for the 2026-10-21 batch.

The default mode and ``--fixture`` are offline.  Only ``--execute --go PATH``
can start curl, and that mode refuses to run unless the supplied root GO binds
the exact plan, runner, fixture, source selection, input bindings, and latest 429
failure receipts.  The control query is a known-good news-image exact CDX
identity; it never replays an image, follows a redirect, paginates, or retries.
"""

from __future__ import annotations

import argparse
import math
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
PREP = Path(__file__).resolve().parent
PLAN = PREP / "plan.json"
INPUT_BINDINGS = PREP / "input-bindings.json"
FIXTURE = PREP / "root-offline-fixture.json"
SOURCE_SELECTION = PREP / "source-selection.json"
RUNNER = Path(__file__).resolve()
LATEST_ACCEPTANCE = ROOT / "research/player-gallery-accessibility-20261020/root/network-source-acceptance.json"
LATEST_CONTROL_REPORT = ROOT / "research/player-gallery-accessibility-20261020/network/control02-prep/runtime/control-report.json"
INTERVENING_ACCEPTANCE = ROOT / "research/continuous-recovery-20261021/publication/root-control01-source-acceptance.json"
INTERVENING_CONTROL_REPORT = ROOT / "research/continuous-recovery-20261021/network/runtime/control-report.json"
STATUS_PATH = ROOT / "research/continuous-recovery-20261021/status.json"
RUNTIME = PREP / "runtime"
REPORT = RUNTIME / "control-report.json"
RAW = RUNTIME / "raw"

ORIGINAL = "http://www.worldofwarcraft.com/news/images/08-02/02-14-08-2.jpg"
FROM_TS = "20000101000000"
TO_TS = "20080512210044"
CDX_FIELDS = ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
PROXY = "http://127.0.0.1:7890"
KNOWN_CAPTURE_TIMESTAMP = "20080402035201"
KNOWN_DIGEST = "TJ2TFHNGVSA64RRRP3UD2CQZCP4TTRND"
KNOWN_MIME = "image/jpeg"

DISK_FLOOR = 11_005_853_696
TOTAL_BODY_CAP = 1 * 1024 * 1024
ENTITY_BODY_CAP = 1 * 1024 * 1024
MAX_REQUESTS = 2
CHILD_SECONDS = 90.0
PARENT_SECONDS = 180.0
DISPATCH_SECONDS = 6.2
REQUEST_START_SECONDS = 6.2
CONNECT_SECONDS = 10
REQUEST_SECONDS = 35
STOP_STATUSES = {429, 503}
COOLDOWN_SECONDS = 120
MAX_TRANSPORT_FAILURES = 5
RETRY_AFTER_RE = re.compile(r"^retry-after:\s*(.+)$", re.I | re.M)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def disk_free() -> int:
    return shutil.disk_usage(ROOT).free


def require_disk(stage: str) -> int:
    free = disk_free()
    if free < DISK_FLOOR:
        raise RuntimeError(f"disk floor failed {stage}: {free} < {DISK_FLOOR}")
    return free


def query_url() -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?url="
        + quote(ORIGINAL, safe="")
        + f"&from={FROM_TS}&to={TO_TS}&output=json&fl="
        + quote(",".join(CDX_FIELDS), safe="")
        + "&limit=10&showResumeKey=true&matchType=exact"
    )


def curl_command(url: str, *, proxy: bool, body: Path, headers: Path, body_cap: int) -> list[str]:
    command = [
        "curl.exe",
        "--silent",
        "--show-error",
        "--tlsv1.2",
        "--proto",
        "=https",
        "--connect-timeout",
        str(CONNECT_SECONDS),
        "--max-time",
        str(REQUEST_SECONDS),
        "--max-filesize",
        str(body_cap),
        "--retry",
        "0",
        "--max-redirs",
        "0",
        "--dump-header",
        str(headers),
        "--output",
        str(body),
        "--write-out",
        "%{http_code}",
    ]
    command += ["--proxy", PROXY] if proxy else ["--noproxy", "*"]
    command.append(url)
    return command


def parse_retry_after(headers: str) -> str | None:
    match = RETRY_AFTER_RE.search(headers)
    return match.group(1).strip() if match else None


def retry_after_seconds(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return max(0, int(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        remaining = (retry_at.astimezone(timezone.utc) - utc_now()).total_seconds()
        return max(0, math.ceil(remaining))


def normalize_original(value: str) -> str:
    return value.replace(":80/", "/")


def parse_cdx(data: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"valid": False, "complete": False, "error": "json_decode", "rows": [], "resume_keys": []}
    if payload == []:
        return {"valid": True, "complete": True, "error": None, "rows": [], "resume_keys": []}
    if not isinstance(payload, list):
        return {"valid": False, "complete": False, "error": "json_shape", "rows": [], "resume_keys": []}

    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    resume_keys: list[str] = []
    unknown = False
    for item in payload:
        if isinstance(item, dict):
            if "resumeKey" in item:
                resume_keys.append(str(item["resumeKey"]))
            elif set(CDX_FIELDS).issubset(item):
                rows.append({name: str(item[name]) for name in CDX_FIELDS})
            else:
                unknown = True
            continue
        if not isinstance(item, list):
            unknown = True
            continue
        values = [str(value) for value in item]
        if header is None and values == CDX_FIELDS:
            header = values
        elif len(values) == 1:
            resume_keys.append(values[0])
        elif header is not None and len(values) == len(CDX_FIELDS):
            rows.append({name: values[pos] for pos, name in enumerate(CDX_FIELDS)})
        else:
            unknown = True
    valid = not unknown and (header == CDX_FIELDS or bool(rows) or payload == [])
    potential_truncation = bool(resume_keys or len(rows) >= 10)
    return {
        "valid": valid,
        "complete": valid and not potential_truncation,
        "error": "unrecognized_metadata" if unknown else None,
        "rows": rows,
        "resume_keys": resume_keys,
        "potential_truncation": potential_truncation,
    }


def known_row_matches(parsed: dict[str, Any]) -> bool:
    if not parsed.get("valid") or not parsed.get("complete") or parsed.get("resume_keys"):
        return False
    return any(
        row.get("timestamp") == KNOWN_CAPTURE_TIMESTAMP
        and normalize_original(row.get("original", "")) == ORIGINAL
        and row.get("mimetype") == KNOWN_MIME
        and row.get("statuscode") == "200"
        and row.get("digest") == KNOWN_DIGEST
        for row in parsed.get("rows", [])
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def validate_inputs(go_path: Path | None = None, *, enforce_schedule: bool = False) -> dict[str, Any]:
    plan = load_json(PLAN)
    acceptance = load_json(LATEST_ACCEPTANCE)
    private_report = load_json(LATEST_CONTROL_REPORT)
    if plan.get("mode") != "prepared_only" or plan.get("network_requests_executed_at_prepare") != 0:
        raise RuntimeError("plan is not preparation-only")
    if plan.get("query_url") != query_url() or plan.get("exact_original") != ORIGINAL:
        raise RuntimeError("exact query identity mismatch")
    if plan.get("known_positive", {}).get("timestamp") != KNOWN_CAPTURE_TIMESTAMP or plan.get("known_positive", {}).get("digest") != KNOWN_DIGEST:
        raise RuntimeError("known positive identity mismatch")
    if not acceptance.get("accepted") or acceptance.get("proxy", {}).get("http_status") != 429:
        raise RuntimeError("latest control02 acceptance is not the expected 429 stop")
    if acceptance.get("failure_finished_utc") != plan["latest_failure_authoritative"]["failure_finished_utc"]:
        raise RuntimeError("latest failure timestamp mismatch")
    if sha256(LATEST_ACCEPTANCE) != plan["latest_failure_authoritative"]["source_acceptance"]["sha256"]:
        raise RuntimeError("latest failure acceptance hash mismatch")
    if sha256(LATEST_CONTROL_REPORT) != plan["latest_failure_authoritative"]["control_report"]["sha256"]:
        raise RuntimeError("latest private control report hash mismatch")
    if private_report.get("network_requests") != 2 or private_report.get("records", [{}])[-1].get("http_status") != 429:
        raise RuntimeError("latest private control report is not the expected two-request 429 stop")
    intervening = load_json(INTERVENING_ACCEPTANCE)
    intervening_report = load_json(INTERVENING_CONTROL_REPORT)
    if not intervening.get("accepted") or intervening.get("proxy_http_status") != 429:
        raise RuntimeError("intervening 00:49 control acceptance is not the expected 429 stop")
    if sha256(INTERVENING_ACCEPTANCE) != plan["intervening_failure"]["source_acceptance"]["sha256"]:
        raise RuntimeError("intervening source acceptance hash mismatch")
    if sha256(INTERVENING_CONTROL_REPORT) != plan["intervening_failure"]["control_report"]["sha256"]:
        raise RuntimeError("intervening private control report hash mismatch")
    if intervening_report.get("network_requests") != 2 or intervening_report.get("records", [{}])[-1].get("http_status") != 429:
        raise RuntimeError("intervening private control report is not the expected two-request 429 stop")
    if sha256(STATUS_PATH) != plan["status_binding"]["sha256"]:
        raise RuntimeError("continuous recovery status hash mismatch")
    if sha256(RUNNER) != plan["frozen_runtime"]["preparation_runner"]["sha256"]:
        raise RuntimeError("runner SHA mismatch")
    source_entry = plan["source_selection"]
    if sha256(resolve(source_entry["path"])) != source_entry["sha256"]:
        raise RuntimeError("source selection hash mismatch")
    if RUNTIME.exists() or REPORT.exists() or RAW.exists():
        raise RuntimeError("refusing to reuse an existing control report or raw directory")
    require_disk("before prepare/execute")
    if enforce_schedule:
        schedule = plan["schedule"]
        start = datetime.fromisoformat(schedule["run_start_utc"].replace("Z", "+00:00"))
        stop = datetime.fromisoformat(schedule["network_stop_utc"].replace("Z", "+00:00"))
        now = utc_now()
        if now < start or now >= stop:
            raise RuntimeError("outside the bounded network schedule")
    if go_path is not None:
        go = load_json(go_path)
        required = {
            "accepted": True,
            "root_go": True,
            "plan_sha256": sha256(PLAN),
            "runner_sha256": sha256(RUNNER),
            "fixture_sha256": sha256(FIXTURE),
            "input_bindings_sha256": sha256(INPUT_BINDINGS),
            "source_selection_sha256": sha256(SOURCE_SELECTION),
            "latest_failure_source_acceptance_sha256": sha256(LATEST_ACCEPTANCE),
            "latest_failure_control_report_sha256": sha256(LATEST_CONTROL_REPORT),
            "intervening_failure_source_acceptance_sha256": sha256(INTERVENING_ACCEPTANCE),
            "intervening_failure_control_report_sha256": sha256(INTERVENING_CONTROL_REPORT),
            "status_sha256": sha256(STATUS_PATH),
        }
        for key, expected in required.items():
            if go.get(key) != expected:
                raise RuntimeError(f"new root GO mismatch: {key}")
    return plan


def fixture() -> int:
    plan = validate_inputs(None)
    direct = curl_command(query_url(), proxy=False, body=Path("DIRECT.body"), headers=Path("DIRECT.headers"), body_cap=ENTITY_BODY_CAP)
    proxied = curl_command(query_url(), proxy=True, body=Path("PROXY.body"), headers=Path("PROXY.headers"), body_cap=ENTITY_BODY_CAP)
    synthetic_known = json.dumps([CDX_FIELDS, [KNOWN_CAPTURE_TIMESTAMP, ORIGINAL, KNOWN_MIME, "200", KNOWN_DIGEST, "9971"]], separators=(",", ":")).encode()
    synthetic_invalid = b'{"ok":true}'
    known_parsed = parse_cdx(synthetic_known)
    invalid_parsed = parse_cdx(synthetic_invalid)
    retry_date = format_datetime(utc_now() + timedelta(seconds=300), usegmt=True)
    retry_date_seconds = retry_after_seconds(retry_date)
    tests = {
        "exact_query_and_no_pagination": plan["query_url"] == query_url() and "showResumeKey=true" in query_url() and "matchType=exact" in query_url() and "page=" not in query_url(),
        "direct_noproxy_first": "--noproxy" in direct and direct[direct.index("--noproxy") + 1] == "*",
        "proxy_fallback_only": "--proxy" in proxied and proxied[proxied.index("--proxy") + 1] == PROXY and "--noproxy" not in proxied,
        "tls_https_only": "--tlsv1.2" in direct and direct[direct.index("--proto") + 1] == "=https" and urlsplit(query_url()).scheme == "https",
        "no_retries_or_redirects": direct[direct.index("--retry") + 1] == "0" and direct[direct.index("--max-redirs") + 1] == "0",
        "request_and_connect_caps": direct[direct.index("--max-time") + 1] == str(REQUEST_SECONDS) and direct[direct.index("--connect-timeout") + 1] == str(CONNECT_SECONDS),
        "one_mib_entity_and_total_caps": ENTITY_BODY_CAP == TOTAL_BODY_CAP == 1 * 1024 * 1024,
        "cadence_policy": DISPATCH_SECONDS >= 6.2 and REQUEST_START_SECONDS >= 6.2,
        "known_row_positive_required": known_row_matches(known_parsed) and not known_row_matches(invalid_parsed),
        "resume_key_incomplete": parse_cdx(json.dumps([CDX_FIELDS, ["resume-token"]]).encode())["complete"] is False,
        "429_503_stop_and_retry_after_integer": parse_retry_after("HTTP/1.1 429 Too Many Requests\r\nRetry-After: 120\r\n") == "120" and retry_after_seconds("120") == 120 and STOP_STATUSES == {429, 503},
        "retry_after_future_http_date": retry_date_seconds is not None and 295 <= retry_date_seconds <= 301 and retry_after_seconds("not-a-date") is None,
        "disk_floor_before_and_after": disk_free() >= DISK_FLOOR,
        "runtime_absence_guard": not RUNTIME.exists() and not RAW.exists(),
        "new_root_go_required": plan["root_go_required"] is True,
        "no_network_entrypoint": True,
    }
    result = {
        "schema": "wow-recovery.wayback-control02-prep-fixture.v1",
        "batch_id": plan["batch_id"],
        "network_requests": 0,
        "raw_written": False,
        "all_passed": all(tests.values()),
        "cases": tests,
        "planned_commands": {"direct": direct, "proxy": proxied},
        "known_positive": plan["known_positive"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["all_passed"] else 1


def execute(go_path: Path) -> int:
    plan = validate_inputs(go_path, enforce_schedule=True)
    require_disk("before batch")
    RUNTIME.mkdir()
    RAW.mkdir()
    started_monotonic = time.monotonic()
    started_utc = utc_now().isoformat()
    records: list[dict[str, Any]] = []
    total_body = 0
    transport_failures = 0
    previous_start: float | None = None
    stop_reason = "completed_without_positive"
    cooldown_not_before: str | None = None
    try:
        for number, use_proxy in enumerate((False, True), 1):
            elapsed = time.monotonic() - started_monotonic
            if len(records) >= MAX_REQUESTS or elapsed >= CHILD_SECONDS or elapsed >= PARENT_SECONDS:
                stop_reason = "bounded_window_exhausted"
                break
            if previous_start is not None:
                wait = DISPATCH_SECONDS - (time.monotonic() - previous_start)
                if wait > 0:
                    time.sleep(wait)
            schedule_stop = datetime.fromisoformat(plan["schedule"]["network_stop_utc"].replace("Z", "+00:00"))
            latest_cooldown = datetime.fromisoformat(plan["execution_gate"]["cooldown_not_before_utc"].replace("Z", "+00:00"))
            now = utc_now()
            if now >= schedule_stop:
                stop_reason = "network_cutoff_before_request"
                break
            if now < latest_cooldown:
                stop_reason = "latest_provider_cooldown_active"
                break
            require_disk(f"before request {number}")
            previous_start = time.monotonic()
            request_started_utc = utc_now().isoformat()
            body = RAW / f"request-{number}.body"
            headers = RAW / f"request-{number}.headers"
            remaining_bytes = TOTAL_BODY_CAP - total_body
            if remaining_bytes <= 0:
                stop_reason = "total_body_cap_reached"
                break
            command = curl_command(query_url(), proxy=use_proxy, body=body, headers=headers, body_cap=min(ENTITY_BODY_CAP, remaining_bytes))
            completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=REQUEST_SECONDS + 5, check=False)
            request_finished_utc = utc_now().isoformat()
            status_text = completed.stdout.strip()
            status = int(status_text) if status_text.isdigit() and len(status_text) == 3 else None
            body_bytes = body.stat().st_size if body.exists() else 0
            total_body += body_bytes
            require_disk(f"after request {number}")
            if body_bytes > ENTITY_BODY_CAP or total_body > TOTAL_BODY_CAP:
                raise RuntimeError("body cap exceeded")
            header_text = headers.read_text(encoding="iso-8859-1", errors="replace") if headers.exists() else ""
            body_data = body.read_bytes() if body.exists() else b""
            parsed = parse_cdx(body_data) if status == 200 and body_data else {"valid": False, "complete": False, "rows": [], "resume_keys": [], "error": "no_200_body"}
            positive = status == 200 and known_row_matches(parsed)
            retry_after = parse_retry_after(header_text)
            if completed.returncode != 0 or status is None:
                classification = "transport_failure"
                transport_failures += 1
            elif status in STOP_STATUSES:
                classification = "endpoint_stop"
            elif positive:
                classification = "known_exact_cdx_row"
            elif status == 200 and parsed.get("valid"):
                classification = "cdx_json_200_without_known_row"
            else:
                classification = f"http_{status}"
            require_disk(f"before stderr write {number}")
            stderr_data = completed.stderr.encode("utf-8", errors="replace")
            (RAW / f"request-{number}.stderr.txt").write_bytes(stderr_data)
            record = {
                "request_number": number,
                "transport": "proxy" if use_proxy else "direct",
                "request_started_utc": request_started_utc,
                "request_finished_utc": request_finished_utc,
                "returncode": completed.returncode,
                "http_status": status,
                "classification": classification,
                "body_bytes": body_bytes,
                "body_sha256": hashlib.sha256(body_data).hexdigest(),
                "cdx_json_valid": parsed.get("valid"),
                "cdx_complete": parsed.get("complete"),
                "cdx_rows": len(parsed.get("rows", [])),
                "resume_keys": parsed.get("resume_keys", []),
                "positive_known_row": positive,
                "body_path": str(body.relative_to(ROOT)).replace("\\", "/"),
                "headers_path": str(headers.relative_to(ROOT)).replace("\\", "/"),
                "stderr_path": str((RAW / f"request-{number}.stderr.txt").relative_to(ROOT)).replace("\\", "/"),
                "stderr_bytes": len(stderr_data),
                "stderr_sha256": hashlib.sha256(stderr_data).hexdigest(),
                "retry_after": retry_after,
                "disk_free_after_bytes": disk_free(),
            }
            records.append(record)
            if status in STOP_STATUSES:
                retry_seconds = retry_after_seconds(retry_after)
                cooldown = utc_now() + timedelta(seconds=max(COOLDOWN_SECONDS, retry_seconds or 0))
                cooldown_not_before = cooldown.isoformat()
                stop_reason = f"endpoint_status_{status}"
                break
            if positive:
                stop_reason = "known_exact_cdx_row"
                break
            if not use_proxy and (completed.returncode == 0 and status is not None):
                stop_reason = "direct_http_without_known_row"
                break
            if transport_failures >= MAX_TRANSPORT_FAILURES:
                stop_reason = "transport_failure_limit"
                break
        require_disk("before report write")
        report = {
            "schema": "wow-recovery.wayback-control02-execution-report.v1",
            "batch_id": plan["batch_id"],
            "started_utc": started_utc,
            "finished_utc": utc_now().isoformat(),
            "network_requests": len(records),
            "records": records,
            "total_body_bytes": total_body,
            "transport_failures": transport_failures,
            "stop_statuses": sorted(STOP_STATUSES),
            "stop_reason": stop_reason,
            "control_positive": any(item["positive_known_row"] for item in records),
            "cooldown_not_before_utc": cooldown_not_before,
            "disk_free_after_bytes": disk_free(),
        }
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0
    except Exception:
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fixture", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--go", type=Path)
    args = parser.parse_args()
    if args.fixture:
        return fixture()
    if not args.execute:
        print(json.dumps({"mode": "prepared_only", "network_requests": 0, "execute_requires_new_root_go": True}, indent=2))
        return 0
    if args.go is None:
        raise SystemExit("--execute requires --go PATH")
    return execute(args.go)


if __name__ == "__main__":
    raise SystemExit(main())

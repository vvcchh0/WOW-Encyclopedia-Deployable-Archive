"""Root-GO-gated, metadata-only Common Crawl probe02.

Preparation and ``--fixture`` are offline.  ``--execute`` refuses to start
unless a future root GO receipt binds this plan, driver, fixture, and input
bindings.  The five requests are direct HTTPS index queries only: no
collinfo request, proxy fallback, retry, pagination, ARC read, image read, or
Wayback request is part of this packet.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "research" / "continuous-recovery-20261020"
PLAN_PATH = OUT / "plan.json"
BINDINGS_PATH = OUT / "input-bindings.json"
FIXTURE_PATH = OUT / "fixture-results.json"
GO_PATH = BASE / "publication" / "root-commoncrawl-probe02-execute-go.json"
RAW = OUT / "raw"
REPORT_PATH = OUT / "probe-report.json"
RECORDS_PATH = OUT / "index-records.jsonl"

QUEUE_PATH = ROOT / "research" / "continuous-recovery-20261020" / "local-audit" / "recovery-queue.json"
QUEUE_ACCEPTANCE_PATH = BASE / "publication" / "root-prepared-queue-acceptance.json"
CC01_ACCEPTANCE_PATH = BASE / "publication" / "root-commoncrawl-probe01-source-acceptance.json"
CC01_DRIVER_PATH = BASE / "network" / "commoncrawl-probe01" / "commoncrawl_probe01.py"
PARSER_PATH = ROOT / "research" / "continuous-recovery-20261016" / "network" / "control02-plan" / "control02_driver.py"

COLLECTION_ID = "CC-MAIN-2008-2009"
INDEX_ENDPOINT = "https://index.commoncrawl.org/CC-MAIN-2008-2009-index"
USER_AGENT = "wow-recovery-commoncrawl-probe02/20261020"
INDEX_LIMIT = 10
MAX_REQUESTS = 5
MAX_SECONDS = 180.0
PARENT_WATCHDOG_SECONDS = 240.0
SUBPROCESS_TIMEOUT_SECONDS = 20.0
MAX_TOTAL_BODY_BYTES = 1 * 1024 * 1024
MAX_BODY_BYTES_PER_ATTEMPT = 128 * 1024
MIN_REQUEST_START_SECONDS = 5.25
DISK_FLOOR_BYTES = 11_005_853_696
STOP_HTTP_CODES = {429, 503}
STOP_AFTER_GATEWAY_CODES = {502, 504}
STOP_GATEWAY_COUNT = 2
MIN_COOLDOWN_SECONDS = 120
NETWORK_CUTOFF_UTC = "2026-10-20T13:15:00Z"
PREPARATION_DEADLINE_UTC = "2026-10-20T12:28:00Z"

CC01_DRIVER_SHA256 = "c59493f4b14496edb0a5215e979147f3c6b57f46566baf71f2f3b11f3ca5b4e6"
PARSER_SHA256 = "85457ea1baa96c474e33ffc01210b4f6d96b3d6d276dc7a2b56aff3cd8376530"
QUEUE_SHA256 = "a4f7a8fed2de23fa65864a5d949f9af112694074f87318706c6b8e3ce484f03e"
CC01_ACCEPTANCE_SHA256 = "15b9934a179f7f60c6aedbc8a94c2c6f4f707af99988fb2dd133ef5104b406a7"
SOURCE_MANIFEST_SHA256 = "ff8b2d7aa9b94d47cdf9d67ed015c62e6bef7f7662ec15e20ff3c89105d2d708"

TARGET_IDENTITIES = [
    ("news-r121-fanart44", 121, "http://www.worldofwarcraft.com/news/images/04-10/fanart/fanart44.jpg"),
    ("news-r123-group-screenshots-ss01", 123, "http://www.worldofwarcraft.com/news/images/04-10/group-screenshots/ss01.jpg"),
    ("news-r126-endofbeta-ss07", 126, "http://www.worldofwarcraft.com/news/images/04-11/endofbeta/ss07.jpg"),
    ("news-r136-wowshirts", 136, "http://www.worldofwarcraft.com/news/images/04-12/wowshirts.jpg"),
    ("news-r137-battlegrounds-part2", 137, "http://www.worldofwarcraft.com/news/images/05-01/battlegrounds-part2.jpg"),
]


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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def build_index_url(target: dict[str, Any]) -> str:
    return (
        f"{INDEX_ENDPOINT}?url={quote(str(target['url']), safe='')}"
        f"&output=json&limit={INDEX_LIMIT}&matchType=exact&showResumeKey=true"
    )


def load_header_parser() -> Any:
    if sha_file(PARSER_PATH) != PARSER_SHA256:
        raise RuntimeError("frozen CC01 headers parser SHA mismatch")
    spec = importlib.util.spec_from_file_location("frozen_commoncrawl_headers02", PARSER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen headers parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bound_file(path: Path, expected_sha: str | None = None) -> None:
    if not path.is_file():
        raise RuntimeError(f"bound file missing: {rel(path)}")
    if expected_sha and sha_file(path) != expected_sha:
        raise RuntimeError(f"bound file SHA mismatch: {rel(path)}")


def parse_index_json_lines(body: bytes) -> dict[str, Any]:
    stripped = body.strip()
    if not stripped:
        return {"valid": True, "body_state": "empty", "rows": [], "row_count": 0, "resume_key": None, "incomplete": False}
    try:
        decoded = stripped.decode("utf-8-sig")
        rows: list[dict[str, Any]] = []
        resume_key: str | None = None
        if decoded.lstrip().startswith("["):
            values = json.loads(decoded)
            if not isinstance(values, list):
                return {"valid": False, "body_state": "invalid_json_shape", "rows": [], "row_count": 0, "resume_key": None, "incomplete": False}
            iterable = values
        else:
            iterable = []
            for line_number, line in enumerate(decoded.splitlines(), 1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    return {"valid": False, "body_state": f"non_object_line_{line_number}", "rows": [], "row_count": 0, "resume_key": None, "incomplete": False}
                iterable.append(value)
        for value in iterable:
            if not isinstance(value, dict):
                return {"valid": False, "body_state": "non_object_row", "rows": [], "row_count": 0, "resume_key": None, "incomplete": False}
            candidate = value.get("resumeKey", value.get("resume_key"))
            if candidate is not None and "url" not in value and "timestamp" not in value:
                resume_key = str(candidate)
                continue
            rows.append(value)
        incomplete = bool(resume_key) or len(rows) >= INDEX_LIMIT
        return {
            "valid": True,
            "body_state": "rows" if rows else "empty",
            "rows": rows,
            "row_count": len(rows),
            "resume_key": resume_key,
            "incomplete": incomplete,
        }
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "body_state": "invalid_json", "error": type(exc).__name__, "rows": [], "row_count": 0, "resume_key": None, "incomplete": False}


def normalize_capture(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "date": row.get("timestamp"),
        "timestamp": row.get("timestamp"),
        "url": row.get("url"),
        "status": row.get("status"),
        "digest": row.get("digest"),
        "filename": row.get("filename"),
        "offset": row.get("offset"),
        "length": row.get("length"),
        "mime": row.get("mime"),
        "mime-detected": row.get("mime-detected"),
        "record": row,
    }


def effective_cooldown_seconds(attempt: dict[str, Any]) -> int:
    """Apply the stop policy to parser-normalized integer or HTTP-date values."""
    parsed = attempt.get("retry_after")
    try:
        seconds = max(0, int(parsed)) if parsed is not None else 0
    except (TypeError, ValueError):
        seconds = 0
    return max(MIN_COOLDOWN_SECONDS, seconds)


def parse_attempt_body(attempt: dict[str, Any], body: bytes) -> dict[str, Any]:
    """Qualify a response before handing bytes to the JSON-line parser."""
    status = attempt.get("source_status")
    curl_success = attempt.get("curl_exit") == 0 and not attempt.get("exception")
    if status == 200 and curl_success:
        parsed = parse_index_json_lines(body)
        parsed["parse_eligible"] = True
        return parsed
    if status == 200:
        return {
            "valid": False,
            "body_state": "transport_or_body_limit",
            "rows": [],
            "row_count": 0,
            "resume_key": None,
            "incomplete": True,
            "parse_eligible": False,
        }
    return {
        "valid": False,
        "body_state": "transport_error" if status is None and (attempt.get("exception") or attempt.get("curl_exit") not in (None, 0)) else "http_status",
        "rows": [],
        "row_count": 0,
        "resume_key": None,
        "incomplete": False,
        "parse_eligible": False,
    }


def validate_local_inputs(check_artifacts: bool = True) -> tuple[dict[str, Any], dict[str, Any]]:
    plan = read_json(PLAN_PATH)
    bindings = read_json(BINDINGS_PATH)
    if plan.get("schema") != "wow-recovery.commoncrawl-probe02-plan.v1" or plan.get("mode") != "prepared" or plan.get("root_go_required") is not True:
        raise RuntimeError("plan must remain prepared and root-gated")
    provider = plan.get("provider", {})
    collection = provider.get("collection", {})
    if collection.get("id") != COLLECTION_ID or collection.get("index_endpoint") != INDEX_ENDPOINT:
        raise RuntimeError("collection identity mismatch")
    if provider.get("wayback_requests") is not False or provider.get("arc_payloads_requested") is not False or provider.get("image_payloads_requested") is not False:
        raise RuntimeError("provider scope permits an unexpected payload or Wayback request")
    query = plan.get("query", {})
    if query.get("endpoint") != INDEX_ENDPOINT or query.get("output") != "json" or query.get("limit") != INDEX_LIMIT:
        raise RuntimeError("query endpoint/output/limit mismatch")
    if query.get("match_types_allowed") != ["exact"] or query.get("pagination") is not False or query.get("show_resume_key") is not True:
        raise RuntimeError("query exact/no-pagination/resume-key policy mismatch")
    target_tuples = [(item.get("id"), item.get("rank"), item.get("url")) for item in plan.get("targets", [])]
    if target_tuples != TARGET_IDENTITIES:
        raise RuntimeError("target identity mismatch")
    if plan.get("execution_order") not in (None, [item[0] for item in TARGET_IDENTITIES]):
        raise RuntimeError("unexpected execution order")
    policy = plan.get("policy", {})
    expected_policy = {
        "maximum_logical_requests": MAX_REQUESTS,
        "maximum_http_attempts": MAX_REQUESTS,
        "maximum_seconds": int(MAX_SECONDS),
        "parent_watchdog_seconds": int(PARENT_WATCHDOG_SECONDS),
        "subprocess_timeout_seconds": int(SUBPROCESS_TIMEOUT_SECONDS),
        "maximum_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "maximum_body_bytes_per_attempt": MAX_BODY_BYTES_PER_ATTEMPT,
        "minimum_request_start_seconds": MIN_REQUEST_START_SECONDS,
        "disk_floor_bytes": DISK_FLOOR_BYTES,
        "direct_only": True,
        "process_proxy": None,
        "tls_verification": True,
        "automatic_redirects": False,
        "automatic_retries": False,
        "respect_retry_after": True,
        "no_arc_download": True,
        "no_image_download": True,
        "no_wayback_requests": True,
        "raw_http_private": True,
    }
    for key, expected in expected_policy.items():
        if policy.get(key) != expected:
            raise RuntimeError(f"policy mismatch: {key}")
    if set(policy.get("stop_http_codes", [])) != STOP_HTTP_CODES:
        raise RuntimeError("429/503 stop policy mismatch")
    if policy.get("minimum_cooldown_seconds") != MIN_COOLDOWN_SECONDS:
        raise RuntimeError("minimum cooldown policy mismatch")
    gateway = policy.get("stop_after_consecutive_http_codes", {})
    if set(gateway.get("codes", [])) != STOP_AFTER_GATEWAY_CODES or gateway.get("count") != STOP_GATEWAY_COUNT:
        raise RuntimeError("502/504 stop policy mismatch")
    schedule = plan.get("schedule", {})
    if schedule.get("network_cutoff_utc") != NETWORK_CUTOFF_UTC or schedule.get("preparation_deadline_utc") != PREPARATION_DEADLINE_UTC:
        raise RuntimeError("schedule mismatch")
    if plan.get("network_at_prepare", {}).get("http_requests") != 0 or plan.get("network_at_prepare", {}).get("raw_http_written") is not False:
        raise RuntimeError("preparation must record zero network requests and no raw output")
    if bindings.get("schema") != "wow-recovery.commoncrawl-probe02-input-bindings.v1":
        raise RuntimeError("unexpected binding schema")
    _bound_file(QUEUE_PATH, QUEUE_SHA256)
    _bound_file(QUEUE_ACCEPTANCE_PATH, bindings.get("queue_acceptance", {}).get("sha256"))
    _bound_file(CC01_ACCEPTANCE_PATH, CC01_ACCEPTANCE_SHA256)
    _bound_file(CC01_DRIVER_PATH, CC01_DRIVER_SHA256)
    _bound_file(PARSER_PATH, PARSER_SHA256)
    if bindings.get("queue", {}).get("sha256") != QUEUE_SHA256:
        raise RuntimeError("queue SHA binding mismatch")
    if bindings.get("source_manifest", {}).get("sha256") != SOURCE_MANIFEST_SHA256:
        raise RuntimeError("source manifest SHA binding mismatch")
    queue_acceptance = read_json(QUEUE_ACCEPTANCE_PATH)
    cc01_acceptance = read_json(CC01_ACCEPTANCE_PATH)
    if queue_acceptance.get("accepted") is not True or queue_acceptance.get("queue_sha256") != QUEUE_SHA256:
        raise RuntimeError("queue acceptance is not bound/accepted")
    if cc01_acceptance.get("accepted") is not True or cc01_acceptance.get("collection") != COLLECTION_ID:
        raise RuntimeError("CC01 metadata acceptance is not bound/accepted")
    if cc01_acceptance.get("collection_metadata", {}).get("cdx-api") != INDEX_ENDPOINT:
        raise RuntimeError("CC01 accepted endpoint mismatch")
    plan_binding = bindings.get("plan", {})
    if plan_binding.get("path") != rel(PLAN_PATH) or plan_binding.get("sha256") != sha_file(PLAN_PATH) or plan_binding.get("bytes") != PLAN_PATH.stat().st_size:
        raise RuntimeError("plan binding mismatch")
    if check_artifacts:
        for key, path in (("driver", Path(__file__)), ("fixture", FIXTURE_PATH), ("parent", OUT / "parent-execute-once.py")):
            item = bindings.get(key, {})
            _bound_file(path, item.get("sha256"))
            if item.get("path") != rel(path) or item.get("bytes") != path.stat().st_size:
                raise RuntimeError(f"{key} binding metadata mismatch")
    return plan, bindings


def disk_free() -> int:
    return shutil.disk_usage(ROOT).free


def assert_disk() -> int:
    free = disk_free()
    if free < DISK_FLOOR_BYTES:
        raise RuntimeError(f"disk floor failed: {free}")
    return free


def _fixture() -> dict[str, Any]:
    plan, _ = validate_local_inputs(check_artifacts=False)
    parser = load_header_parser()
    direct_200 = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
    status_404 = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
    status_429 = b"HTTP/1.1 429 Too Many Requests\r\nRetry-After: 30\r\n\r\n"
    status_429_date = ("HTTP/1.1 429 Too Many Requests\r\nRetry-After: " + format_datetime(utc_now() + timedelta(seconds=600), usegmt=True) + "\r\n\r\n").encode("ascii")
    sample_rows = b"".join(json.dumps({"timestamp": "20080509000000", "url": target["url"], "status": "200", "mime": "image/jpeg", "digest": "TESTDIGEST", "filename": "crawl-data/CC-MAIN-2008-2009/segments/example.warc", "offset": 123, "length": 456}, separators=(",", ":")).encode() + b"\n" for target in plan["targets"])
    sample_resume = sample_rows + b'{"resumeKey":"next-page"}\n'
    parsed = parse_index_json_lines(sample_resume)
    parsed_http_date = parser.parse_headers(status_429_date)
    failed_200 = parse_attempt_body({"source_status": 200, "curl_exit": 63, "exception": None}, b"")
    cases = {
        "exact_five_targets": len(plan["targets"]) == 5 and all(t["match_type"] == "exact" for t in plan["targets"]),
        "query_uses_output_json": all("output=json" in build_index_url(t) for t in plan["targets"]),
        "query_uses_limit_ten": all("limit=10" in build_index_url(t) for t in plan["targets"]),
        "query_uses_exact_match": all("matchType=exact" in build_index_url(t) for t in plan["targets"]),
        "query_requests_resume_key": all("showResumeKey=true" in build_index_url(t) for t in plan["targets"]),
        "direct_header_200": parser.parse_headers(direct_200)["status"] == 200,
        "404_is_index_status_only": parser.parse_headers(status_404)["status"] == 404 and parse_index_json_lines(b"")["body_state"] == "empty",
        "429_retry_after_minimum": parser.parse_headers(status_429)["status"] == 429 and parser.parse_headers(status_429)["retry_after"] == 30 and effective_cooldown_seconds({"retry_after": 30}) == 120,
        "429_retry_after_http_date": parsed_http_date["status"] == 429 and parsed_http_date["retry_after_kind"] == "http_date" and parsed_http_date["retry_after"] >= 120 and effective_cooldown_seconds(parsed_http_date) >= 120,
        "200_nonzero_exit_not_accepted": failed_200["valid"] is False and failed_200["body_state"] == "transport_or_body_limit" and failed_200["incomplete"] is True and failed_200["row_count"] == 0,
        "json_lines_preserve_capture_fields": parsed["valid"] and parsed["row_count"] == 5 and all(k in normalize_capture(parsed["rows"][0]) for k in ("date", "digest", "filename", "offset", "length")),
        "resume_key_marks_incomplete": parsed["resume_key"] == "next-page" and parsed["incomplete"] is True,
        "ten_rows_marks_incomplete": parse_index_json_lines(b"\n".join((sample_rows.splitlines() * 2)[:10]))["incomplete"] is True,
        "no_pagination": plan["query"]["pagination"] is False,
        "request_budget": MAX_REQUESTS == 5 and MAX_TOTAL_BODY_BYTES == 1048576 and MAX_BODY_BYTES_PER_ATTEMPT == 131072,
        "cadence_and_gateway_stop": MIN_REQUEST_START_SECONDS >= 5.25 and STOP_AFTER_GATEWAY_CODES == {502, 504} and STOP_GATEWAY_COUNT == 2 and MIN_COOLDOWN_SECONDS == 120 and plan["policy"]["minimum_cooldown_seconds"] == 120,
        "direct_only_no_proxy": plan["policy"]["direct_only"] is True and plan["policy"]["process_proxy"] is None,
        "no_wayback_targets": all("web.archive.org" not in t["url"] for t in plan["targets"]),
        "preparation_zero_requests": plan["network_at_prepare"]["http_requests"] == 0,
    }
    return {
        "schema": "wow-recovery.commoncrawl-probe02-fixtures.v1",
        "network_requests": 0,
        "raw_written": False,
        "all_passed": all(cases.values()),
        "case_count": len(cases),
        "cases": cases,
        "parser_sha256": PARSER_SHA256,
        "cc01_driver_sha256": CC01_DRIVER_SHA256,
        "checked_utc": plan["schedule"]["prepared_at_utc"],
    }


def run_fixture() -> int:
    result = _fixture()
    write_json(FIXTURE_PATH, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["all_passed"] else 1


def _go_gate() -> dict[str, Any]:
    if not GO_PATH.is_file():
        raise RuntimeError(f"missing future root GO receipt: {rel(GO_PATH)}")
    go = read_json(GO_PATH)
    if go.get("accepted") is not True or go.get("root_go") is not True:
        raise RuntimeError("root GO receipt is not accepted/root_go")
    expected = {
        "plan_sha256": sha_file(PLAN_PATH),
        "driver_sha256": sha_file(Path(__file__)),
        "fixture_sha256": sha_file(FIXTURE_PATH),
        "input_bindings_sha256": sha_file(BINDINGS_PATH),
    }
    for key, value in expected.items():
        if go.get(key) != value:
            raise RuntimeError(f"root GO {key} mismatch")
    if go.get("collection_id") != COLLECTION_ID or go.get("no_wayback_requests") is not True:
        raise RuntimeError("root GO collection/scope mismatch")
    return go


def _wait_for_cadence(last_start: float | None) -> None:
    if last_start is None:
        return
    remaining = MIN_REQUEST_START_SECONDS - (time.monotonic() - last_start)
    if remaining > 0:
        time.sleep(remaining)


def _parse_attempt_headers(header_path: Path) -> dict[str, Any]:
    parser = load_header_parser()
    raw = header_path.read_bytes() if header_path.exists() else b""
    return parser.parse_headers(raw)


def _direct_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        if key.lower().endswith("_proxy") or key.upper() in {"NO_PROXY", "CURL_PROXY"}:
            environment.pop(key, None)
    return environment


def _run_curl(url: str, attempt_number: int, label: str) -> dict[str, Any]:
    disk_before = assert_disk()
    body_path = RAW / f"{attempt_number:02d}-{label}.body"
    header_path = RAW / f"{attempt_number:02d}-{label}.headers.txt"
    stderr_path = RAW / f"{attempt_number:02d}-{label}.stderr.txt"
    metrics_path = RAW / f"{attempt_number:02d}-{label}.metrics.txt"
    args = [
        "curl.exe", "--silent", "--show-error", "--proto", "=https", "--tlsv1.2",
        "--connect-timeout", "8", "--max-time", str(int(SUBPROCESS_TIMEOUT_SECONDS)),
        "--max-redirs", "0", "--max-filesize", str(MAX_BODY_BYTES_PER_ATTEMPT),
        "--noproxy", "*", "--user-agent", USER_AGENT, "--dump-header", str(header_path),
        "--output", str(body_path), "--write-out", "%{http_code}\\n%{size_download}\\n", url,
    ]
    started = utc_now()
    started_mono = time.monotonic()
    curl_exit: int | None = None
    exception: str | None = None
    metrics = b""
    with stderr_path.open("wb") as stderr_handle:
        try:
            completed = subprocess.run(args, stdout=subprocess.PIPE, stderr=stderr_handle, timeout=SUBPROCESS_TIMEOUT_SECONDS + 1, check=False, env=_direct_environment())
            curl_exit = completed.returncode
            metrics = completed.stdout or b""
        except subprocess.TimeoutExpired as exc:
            curl_exit = 124
            exception = "TimeoutExpired"
            metrics = (exc.stdout or b"") if isinstance(exc.stdout, bytes) else b""
    metrics_path.write_bytes(metrics)
    finished = utc_now()
    body_bytes = body_path.stat().st_size if body_path.exists() else 0
    if body_bytes > MAX_BODY_BYTES_PER_ATTEMPT:
        raise RuntimeError(f"per-attempt body cap exceeded: {body_bytes}")
    headers = _parse_attempt_headers(header_path)
    status = headers.get("status")
    if status is None and metrics:
        first = metrics.decode("ascii", errors="ignore").splitlines()[:1]
        try:
            status = int(first[0]) if first and int(first[0]) > 0 else None
        except (ValueError, TypeError):
            status = None
    return {
        "attempt_number": attempt_number,
        "label": label,
        "url": url,
        "started_utc": iso(started),
        "finished_utc": iso(finished),
        "elapsed_seconds": round(time.monotonic() - started_mono, 6),
        "curl_exit": curl_exit,
        "exception": exception,
        "source_status": status,
        "header_statuses": headers.get("connect_statuses", []) + ([status] if status is not None else []),
        "retry_after": headers.get("retry_after"),
        "retry_after_kind": headers.get("retry_after_kind"),
        "body_bytes": body_bytes,
        "body_limit_bytes": MAX_BODY_BYTES_PER_ATTEMPT,
        "body_sha256": sha_file(body_path) if body_path.exists() else sha_bytes(b""),
        "disk_free_before_bytes": disk_before,
        "raw": {"body": rel(body_path), "headers": rel(header_path), "stderr": rel(stderr_path), "metrics": rel(metrics_path)},
    }


def _run_execute() -> int:
    plan, bindings = validate_local_inputs(check_artifacts=True)
    _go_gate()
    now = utc_now()
    cutoff = datetime.fromisoformat(NETWORK_CUTOFF_UTC.replace("Z", "+00:00"))
    if now >= cutoff:
        raise RuntimeError("network cutoff has passed")
    if REPORT_PATH.exists() or RECORDS_PATH.exists() or RAW.exists():
        raise RuntimeError("execute output/raw already exists; refusing rerun")
    assert_disk()
    RAW.mkdir(parents=True)
    started = utc_now()
    started_mono = time.monotonic()
    attempts: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    total_body_bytes = 0
    gateway_streak = 0
    last_start: float | None = None
    stop_reason: str | None = None
    cooldown_not_before: str | None = None
    for target in plan["targets"]:
        if len(attempts) >= MAX_REQUESTS:
            stop_reason = "maximum_http_requests"
            break
        if time.monotonic() - started_mono >= MAX_SECONDS:
            stop_reason = "batch_watchdog_elapsed"
            break
        if utc_now() >= cutoff:
            stop_reason = "network_cutoff_elapsed"
            break
        _wait_for_cadence(last_start)
        if time.monotonic() - started_mono >= MAX_SECONDS:
            stop_reason = "batch_watchdog_elapsed_after_cadence"
            break
        if utc_now() >= cutoff:
            stop_reason = "network_cutoff_elapsed_after_cadence"
            break
        if total_body_bytes + MAX_BODY_BYTES_PER_ATTEMPT > MAX_TOTAL_BODY_BYTES:
            stop_reason = "remaining_body_budget_below_per_attempt_cap"
            break
        query_url = build_index_url(target)
        last_start = time.monotonic()
        attempt = _run_curl(query_url, len(attempts) + 1, target["id"])
        attempts.append(attempt)
        total_body_bytes += attempt["body_bytes"]
        status = attempt.get("source_status")
        if status in STOP_HTTP_CODES:
            stop_reason = f"endpoint_status_{status}"
            retry_seconds = effective_cooldown_seconds(attempt)
            attempt["cooldown_seconds_applied"] = retry_seconds
            cooldown_not_before = iso(datetime.fromisoformat(attempt["finished_utc"].replace("Z", "+00:00")) + timedelta(seconds=retry_seconds))
        if status in STOP_AFTER_GATEWAY_CODES:
            gateway_streak += 1
        else:
            gateway_streak = 0
        if stop_reason is None and gateway_streak >= STOP_GATEWAY_COUNT:
            stop_reason = "two_consecutive_502_or_504"
        body_path = ROOT / attempt["raw"]["body"]
        body = body_path.read_bytes() if body_path.exists() else b""
        parsed = parse_attempt_body(attempt, body)
        target_result = {
            "target_id": target["id"], "rank": target["rank"], "url": target["url"], "query_url": query_url,
            "source_status": status, "body_state": parsed.get("body_state"), "valid_json_lines": parsed.get("valid", False),
            "row_count": parsed.get("row_count", 0), "resume_key": parsed.get("resume_key"), "incomplete": parsed.get("incomplete", False),
            "parse_eligible": parsed.get("parse_eligible", False), "curl_exit": attempt.get("curl_exit"), "exception": attempt.get("exception"),
            "pagination_attempted": False, "body_bytes": attempt["body_bytes"], "body_sha256": attempt["body_sha256"],
            "index_404_is_not_image_404": status == 404,
        }
        results.append(target_result)
        for row in parsed.get("rows", []):
            records.append({"target_id": target["id"], "collection": COLLECTION_ID, "match_type": "exact", "query_url": query_url, "source_status": status, **normalize_capture(row)})
        if stop_reason is not None:
            break
    RECORDS_PATH.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in records), encoding="utf-8")
    finished = utc_now()
    report = {
        "schema": "wow-recovery.commoncrawl-probe02-report.v1", "batch_id": plan["batch_id"], "provider": "commoncrawl",
        "collection_id": COLLECTION_ID, "started_utc": iso(started), "finished_utc": iso(finished),
        "plan_sha256": sha_file(PLAN_PATH), "driver_sha256": sha_file(Path(__file__)), "fixture_sha256": sha_file(FIXTURE_PATH),
        "input_bindings_sha256": sha_file(BINDINGS_PATH), "root_go_receipt": rel(GO_PATH), "root_go_sha256": sha_file(GO_PATH),
        "logical_requests_completed": len(attempts), "network_attempts_total": len(attempts), "wayback_requests": 0,
        "total_body_bytes": total_body_bytes, "target_results": results, "attempts": attempts,
        "index_records_path": rel(RECORDS_PATH), "index_records_count": len(records), "accepted_image_count": 0,
        "payload_replays": 0, "stop_reason": stop_reason or "completed", "cooldown_not_before_utc": cooldown_not_before,
        "raw_http_private": True, "direct_only": True, "disk_free_after_bytes": assert_disk(),
    }
    write_json(REPORT_PATH, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture", action="store_true", help="run offline parser and policy fixtures")
    group.add_argument("--execute", action="store_true", help="run only after a future root GO receipt")
    args = parser.parse_args()
    return run_fixture() if args.fixture else _run_execute()


if __name__ == "__main__":
    raise SystemExit(main())

"""Bounded Common Crawl metadata probe, prepared but root-GO gated.

Preparation and ``--fixture`` are offline.  Only ``--execute`` can invoke
curl, and it requires a future root GO receipt whose hashes bind this packet.
The probe asks Common Crawl for collection metadata and five JSON-line index
queries.  It never downloads an ARC record or an image and never contacts
Wayback.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "research" / "continuous-recovery-20261020"
PLAN_PATH = OUT / "plan.json"
BINDINGS_PATH = OUT / "input-bindings.json"
FIXTURE_PATH = OUT / "fixture-results.json"
GO_PATH = BASE / "publication" / "root-commoncrawl-probe01-execute-go.json"
PARSER_PATH = ROOT / "research" / "continuous-recovery-20261016" / "network" / "control02-plan" / "control02_driver.py"
RAW = OUT / "raw"
REPORT_PATH = OUT / "probe-report.json"
RECORDS_PATH = OUT / "index-records.jsonl"

COLLINFO_URL = "https://index.commoncrawl.org/collinfo.json"
COLLECTION_ID = "CC-MAIN-2008-2009"
INDEX_ENDPOINT = "https://index.commoncrawl.org/CC-MAIN-2008-2009-index"
PROXY = "http://127.0.0.1:7890"
USER_AGENT = "wow-recovery-commoncrawl-probe01/20261020"
INDEX_LIMIT = 100
MAX_LOGICAL_REQUESTS = 6
MAX_INDEX_QUERIES = 5
MAX_ATTEMPTS = 12
MAX_SECONDS = 600.0
SUBPROCESS_TIMEOUT_SECONDS = 20.0
MAX_TOTAL_BODY_BYTES = 4 * 1024 * 1024
MAX_BODY_BYTES_PER_ATTEMPT = 512 * 1024
MIN_REQUEST_START_SECONDS = 5.0
DISK_FLOOR_BYTES = 11_005_853_696
STOP_HTTP_CODES = {429, 503}
COOLDOWN_SECONDS = 120
MAX_CONSECUTIVE_TRANSPORT_FAILURES = 5
RUN_START_UTC = "2026-10-20T08:33:22Z"
NETWORK_STOP_UTC = "2026-10-20T13:15:00Z"
RUN_DEADLINE_UTC = "2026-10-20T14:33:22Z"
PARSER_SHA256 = "85457ea1baa96c474e33ffc01210b4f6d96b3d6d276dc7a2b56aff3cd8376530"
V3_DRIVER_SHA256 = "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955"
REGISTRY_SHA256 = "2579f66841bf6102d90f5dbfe819902337bff03f6e3ac7191239ae041e2d97d6"
REGISTRY_PATH = ROOT / "research" / "continuous-recovery-20261016" / "local-audit" / "gallery-final-v7" / "gallery-prefix-registry-v7.json"
V3_DRIVER_PATH = ROOT / "research" / "continuous-recovery-20261018" / "network" / "reusable-image-driver-v3" / "reusable_image_driver.py"
LATEST_FAILURE_REPORT_SHA256 = "c10060a5484e4f0092660087c15d72f04f13928efde4f1181b864f31083a93f3"
LATEST_FAILURE_SOURCE_SHA256 = "2420341b37eff901ecbe0288a12f738cd5380067e35a5c7f32268874730fd372"
LATEST_FAILURE_FINISHED_UTC = "2026-10-20T08:52:46.410236Z"
LATEST_FAILURE_COOLDOWN_UTC = "2026-10-20T08:54:46.410236Z"
LATEST_FAILURE_REPORT_PATH = ROOT / "research" / "continuous-recovery-20261020" / "network" / "control01" / "control-report.json"
LATEST_FAILURE_SOURCE_PATH = ROOT / "research" / "continuous-recovery-20261020" / "publication" / "root-control01-source-acceptance.json"
TARGETS = [
    {
        "id": "known-news-image-exact",
        "url": "http://www.worldofwarcraft.com/news/images/08-02/02-14-08-2.jpg",
        "match_type": "exact",
    },
    {
        "id": "news-images-prefix",
        "url": "http://www.worldofwarcraft.com/news/images/",
        "match_type": "prefix",
    },
    {
        "id": "karazhan-source-directory-prefix",
        "url": "http://www.worldofwarcraft.com/info/dungeons/images/karazhan/",
        "match_type": "prefix",
    },
    {
        "id": "blacktemple-source-directory-prefix",
        "url": "http://www.worldofwarcraft.com/info/dungeons/images/blacktemple/",
        "match_type": "prefix",
    },
    {
        "id": "encyclopedia-index-exact",
        "url": "http://www.worldofwarcraft.com/info/encyclopedia/index.xml",
        "match_type": "exact",
    },
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
        f"&output=json&limit={INDEX_LIMIT}&matchType={target['match_type']}"
    )


def load_header_parser() -> Any:
    if sha_file(PARSER_PATH) != PARSER_SHA256:
        raise RuntimeError("frozen headers parser SHA mismatch")
    spec = importlib.util.spec_from_file_location("frozen_commoncrawl_headers", PARSER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen headers parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _check_bound_file(item: dict[str, Any]) -> None:
    path = ROOT / item["path"]
    if not path.is_file():
        raise RuntimeError(f"bound file missing: {item['path']}")
    if sha_file(path) != item["sha256"]:
        raise RuntimeError(f"bound file SHA mismatch: {item['path']}")
    if path.stat().st_size != item["bytes"]:
        raise RuntimeError(f"bound file byte mismatch: {item['path']}")


def _check_bound_tree(value: Any) -> None:
    if isinstance(value, dict):
        if {"path", "sha256", "bytes"}.issubset(value):
            _check_bound_file(value)
        for child in value.values():
            _check_bound_tree(child)
    elif isinstance(value, list):
        for child in value:
            _check_bound_tree(child)


def validate_local_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    plan = read_json(PLAN_PATH)
    bindings = read_json(BINDINGS_PATH)
    if plan.get("schema") != "wow-recovery.commoncrawl-probe01-plan.v1":
        raise RuntimeError("unexpected Common Crawl plan schema")
    if plan.get("mode") != "prepared" or plan.get("root_go_required") is not True:
        raise RuntimeError("plan must remain prepared and root-gated")
    provider = plan.get("provider", {})
    collection = provider.get("collection", {})
    if provider.get("collection_metadata_url") != COLLINFO_URL:
        raise RuntimeError("collinfo endpoint mismatch")
    if collection.get("id") != COLLECTION_ID or collection.get("index_endpoint") != INDEX_ENDPOINT:
        raise RuntimeError("collection identity mismatch")
    query = plan.get("query", {})
    if query.get("endpoint") != INDEX_ENDPOINT or query.get("output") != "json":
        raise RuntimeError("index endpoint/output mismatch")
    if query.get("limit") != INDEX_LIMIT or query.get("pagination") is not False:
        raise RuntimeError("index limit/pagination policy mismatch")
    if query.get("match_types_allowed") != ["exact", "prefix"]:
        raise RuntimeError("match type policy mismatch")
    plan_targets = plan.get("targets", [])
    if plan_targets != [{**target, "category": plan_targets[i].get("category"), "purpose": plan_targets[i].get("purpose")} for i, target in enumerate(TARGETS)]:
        raise RuntimeError("target identity mismatch")
    if plan.get("execution_order") != ["collection_metadata"] + [t["id"] for t in TARGETS]:
        raise RuntimeError("execution order mismatch")
    for target in TARGETS:
        if plan_targets[[t["id"] for t in plan_targets].index(target["id"])].get("query_url") not in (None, build_index_url(target)):
            raise RuntimeError("unexpected stored query URL")
    policy = plan.get("policy", {})
    required_policy = {
        "maximum_logical_requests": MAX_LOGICAL_REQUESTS,
        "maximum_index_queries": MAX_INDEX_QUERIES,
        "maximum_http_attempts": MAX_ATTEMPTS,
        "maximum_seconds": int(MAX_SECONDS),
        "subprocess_timeout_seconds": int(SUBPROCESS_TIMEOUT_SECONDS),
        "maximum_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "maximum_body_bytes_per_attempt": MAX_BODY_BYTES_PER_ATTEMPT,
        "minimum_request_start_seconds": MIN_REQUEST_START_SECONDS,
        "disk_floor_bytes": DISK_FLOOR_BYTES,
        "cooldown_seconds": COOLDOWN_SECONDS,
        "maximum_consecutive_transport_failures": MAX_CONSECUTIVE_TRANSPORT_FAILURES,
        "automatic_redirects": False,
        "automatic_retries": False,
        "no_arc_download": True,
        "no_image_download": True,
        "no_wayback_requests": True,
        "direct_first": True,
        "proxy_only_after_transport_failure": True,
        "tls_verification": True,
        "process_proxy": PROXY,
    }
    for key, expected in required_policy.items():
        if policy.get(key) != expected:
            raise RuntimeError(f"policy mismatch: {key}")
    if set(policy.get("stop_http_codes", [])) != STOP_HTTP_CODES:
        raise RuntimeError("stop HTTP code policy mismatch")
    schedule = plan.get("schedule", {})
    for key, expected in {
        "run_start_utc": RUN_START_UTC,
        "network_stop_utc": NETWORK_STOP_UTC,
        "run_deadline_utc": RUN_DEADLINE_UTC,
    }.items():
        if schedule.get(key) != expected:
            raise RuntimeError(f"schedule mismatch: {key}")
    if bindings.get("schema") != "wow-recovery.commoncrawl-probe01-input-bindings.v1":
        raise RuntimeError("unexpected Common Crawl binding schema")
    plan_binding = bindings.get("plan", {})
    if plan_binding.get("path") != rel(PLAN_PATH) or plan_binding.get("sha256") != sha_file(PLAN_PATH) or plan_binding.get("bytes") != PLAN_PATH.stat().st_size:
        raise RuntimeError("plan binding mismatch")
    _check_bound_tree(bindings)
    latest = bindings.get("latest_failure", {})
    if latest.get("stop_reason") != "endpoint_status_429" or latest.get("finished_utc") != LATEST_FAILURE_FINISHED_UTC:
        raise RuntimeError("latest 429 failure binding mismatch")
    if latest.get("cooldown_not_before_utc") != LATEST_FAILURE_COOLDOWN_UTC:
        raise RuntimeError("latest 429 cooldown binding mismatch")
    if bindings.get("frozen_parser", {}).get("sha256") != PARSER_SHA256:
        raise RuntimeError("frozen parser binding mismatch")
    if bindings.get("frozen_transport_reference", {}).get("sha256") != V3_DRIVER_SHA256:
        raise RuntimeError("frozen transport reference mismatch")
    if plan.get("network_at_prepare", {}).get("http_requests") != 0:
        raise RuntimeError("preparation must record zero network requests")
    return plan, bindings


def disk_free() -> int:
    return shutil.disk_usage(ROOT).free


def assert_disk() -> int:
    free = disk_free()
    if free < DISK_FLOOR_BYTES:
        raise RuntimeError(f"disk floor failed: {free}")
    return free


def parse_index_json_lines(body: bytes) -> dict[str, Any]:
    stripped = body.strip()
    if not stripped:
        return {"valid": True, "body_state": "empty", "rows": [], "row_count": 0}
    try:
        decoded = stripped.decode("utf-8-sig")
        if decoded.lstrip().startswith("["):
            value = json.loads(decoded)
            if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
                return {"valid": False, "body_state": "invalid_json_shape", "rows": [], "row_count": 0}
            rows = value
        else:
            rows = []
            for line_number, line in enumerate(decoded.splitlines(), 1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    return {"valid": False, "body_state": f"non_object_line_{line_number}", "rows": [], "row_count": 0}
                rows.append(value)
        return {"valid": True, "body_state": "rows" if rows else "empty", "rows": rows, "row_count": len(rows)}
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "body_state": "invalid_json", "error": type(exc).__name__, "rows": [], "row_count": 0}


def parse_collinfo(body: bytes) -> dict[str, Any]:
    stripped = body.strip()
    if not stripped:
        return {"valid": False, "body_state": "empty", "collection_found": False}
    try:
        value = json.loads(stripped.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "body_state": "invalid_json", "error": type(exc).__name__, "collection_found": False}
    if not isinstance(value, list):
        return {"valid": False, "body_state": "invalid_json_shape", "collection_found": False}
    match = next((row for row in value if isinstance(row, dict) and row.get("id") == COLLECTION_ID), None)
    return {
        "valid": True,
        "body_state": "rows" if value else "empty",
        "collection_found": match is not None,
        "collection": match,
        "collection_count": len(value),
    }


def normalize_capture(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": row.get("timestamp"),
        "date": row.get("timestamp"),
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


def _fixture() -> dict[str, Any]:
    validate_local_inputs()
    parser = load_header_parser()
    direct_200 = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
    proxy_200 = b"HTTP/1.1 200 Connection established\r\n\r\nHTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
    status_404 = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
    status_429 = b"HTTP/1.1 429 Too Many Requests\r\nRetry-After: 120\r\n\r\n"
    sample = json.dumps({
        "timestamp": "20080509000000",
        "url": TARGETS[0]["url"],
        "mime": "image/jpeg",
        "status": "200",
        "digest": "TESTDIGEST",
        "filename": "crawl-data/CC-MAIN-2008-2009/segments/example.warc",
        "offset": 123,
        "length": 456,
    }, separators=(",", ":")).encode() + b"\n"
    collinfo = json.dumps([{"id": COLLECTION_ID, "name": "fixture"}], separators=(",", ":")).encode()
    parsed = parse_index_json_lines(sample)
    cases = {
        "all_targets_have_expected_query_mode": [t["match_type"] for t in TARGETS] == ["exact", "prefix", "prefix", "prefix", "exact"],
        "known_exact_query_url": build_index_url(TARGETS[0]).endswith("output=json&limit=100&matchType=exact"),
        "prefix_query_url": build_index_url(TARGETS[1]).endswith("output=json&limit=100&matchType=prefix"),
        "direct_header_200": parser.parse_headers(direct_200)["status"] == 200,
        "proxy_connect_header_200": parser.parse_headers(proxy_200)["status"] == 200 and parser.parse_headers(proxy_200)["connect_statuses"] == [200],
        "404_is_index_status_only": parser.parse_headers(status_404)["status"] == 404 and parse_index_json_lines(b"")["body_state"] == "empty",
        "429_retry_after": parser.parse_headers(status_429)["status"] == 429 and parser.parse_headers(status_429)["retry_after"] == 120,
        "json_lines_preserve_required_fields": parsed["valid"] and parsed["row_count"] == 1 and all(k in normalize_capture(parsed["rows"][0]) for k in ("date", "url", "status", "digest", "filename", "offset", "length")),
        "collinfo_selects_collection": parse_collinfo(collinfo)["collection_found"],
        "empty_query_is_bounded_evidence": parse_index_json_lines(b"")["valid"] and parse_index_json_lines(b"")["row_count"] == 0,
        "collection_metadata_precedes_indexes": MAX_LOGICAL_REQUESTS == 1 + MAX_INDEX_QUERIES,
        "attempt_cap_allows_direct_proxy_fallback": MAX_ATTEMPTS == 2 * MAX_LOGICAL_REQUESTS,
        "body_caps": MAX_BODY_BYTES_PER_ATTEMPT <= MAX_TOTAL_BODY_BYTES == 4 * 1024 * 1024,
        "cadence_and_stop_policy": MIN_REQUEST_START_SECONDS >= 5 and STOP_HTTP_CODES == {429, 503} and COOLDOWN_SECONDS >= 120,
        "transport_failure_stop": MAX_CONSECUTIVE_TRANSPORT_FAILURES == 5,
        "no_wayback_target": all("web.archive.org" not in t["url"] for t in TARGETS),
        "preparation_has_zero_requests": read_json(PLAN_PATH)["network_at_prepare"]["http_requests"] == 0,
    }
    return {
        "schema": "wow-recovery.commoncrawl-probe01-fixtures.v1",
        "network_requests": 0,
        "raw_written": False,
        "all_passed": all(cases.values()),
        "case_count": len(cases),
        "cases": cases,
        "parser_sha256": PARSER_SHA256,
        "checked_utc": iso(utc_now()),
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
    if go.get("collection_id", COLLECTION_ID) != COLLECTION_ID:
        raise RuntimeError("root GO collection mismatch")
    if go.get("no_wayback_requests", True) is not True:
        raise RuntimeError("root GO permits an unexpected Wayback request")
    if go.get("latest_failure_report_sha256", LATEST_FAILURE_REPORT_SHA256) != LATEST_FAILURE_REPORT_SHA256:
        raise RuntimeError("root GO latest failure binding mismatch")
    return go


def _wait_for_cadence(last_start: float | None) -> None:
    if last_start is None:
        return
    remaining = MIN_REQUEST_START_SECONDS - (time.monotonic() - last_start)
    if remaining > 0:
        time.sleep(remaining)


def _parse_attempt_headers(header_path: Path) -> dict[str, Any]:
    raw = header_path.read_bytes() if header_path.exists() else b""
    parser = load_header_parser()
    return parser.parse_headers(raw)


def _run_curl(url: str, transport: str, attempt_number: int, label: str, body_limit: int) -> dict[str, Any]:
    disk_before = assert_disk()
    body_path = RAW / f"{attempt_number:02d}-{label}-{transport}.body"
    header_path = RAW / f"{attempt_number:02d}-{label}-{transport}.headers.txt"
    stderr_path = RAW / f"{attempt_number:02d}-{label}-{transport}.stderr.txt"
    metrics_path = RAW / f"{attempt_number:02d}-{label}-{transport}.metrics.txt"
    args = [
        "curl.exe",
        "--silent",
        "--show-error",
        "--proto",
        "=https",
        "--tlsv1.2",
        "--connect-timeout",
        "8",
        "--max-time",
        str(int(SUBPROCESS_TIMEOUT_SECONDS)),
        "--max-redirs",
        "0",
        "--max-filesize",
        str(body_limit),
        "--user-agent",
        USER_AGENT,
        "--dump-header",
        str(header_path),
        "--output",
        str(body_path),
        "--write-out",
        "%{http_code}\\n%{size_download}\\n",
    ]
    if transport == "direct":
        args.extend(["--noproxy", "*"])
    elif transport == "proxy":
        args.extend(["--noproxy", "", "--proxy", PROXY])
    else:
        raise RuntimeError(f"unknown transport: {transport}")
    args.append(url)
    started = utc_now()
    started_mono = time.monotonic()
    curl_exit: int | None = None
    exception: str | None = None
    metrics = b""
    with stderr_path.open("wb") as stderr_handle:
        try:
            completed = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=stderr_handle,
                timeout=SUBPROCESS_TIMEOUT_SECONDS + 1,
                check=False,
            )
            curl_exit = completed.returncode
            metrics = completed.stdout or b""
        except subprocess.TimeoutExpired as exc:
            curl_exit = 124
            exception = "TimeoutExpired"
            metrics = (exc.stdout or b"") if isinstance(exc.stdout, bytes) else b""
    metrics_path.write_bytes(metrics)
    finished = utc_now()
    body_bytes = body_path.stat().st_size if body_path.exists() else 0
    if body_bytes > body_limit:
        raise RuntimeError(f"per-attempt body cap exceeded: {body_bytes}")
    headers = _parse_attempt_headers(header_path)
    source_status = headers.get("status")
    if source_status is None and metrics:
        first_line = metrics.decode("ascii", errors="ignore").splitlines()[0:1]
        try:
            source_status = int(first_line[0]) if first_line and int(first_line[0]) > 0 else None
        except (ValueError, TypeError):
            source_status = None
    attempt = {
        "attempt_number": attempt_number,
        "label": label,
        "url": url,
        "transport": transport,
        "started_utc": iso(started),
        "finished_utc": iso(finished),
        "elapsed_seconds": round(time.monotonic() - started_mono, 6),
        "curl_exit": curl_exit,
        "exception": exception,
        "source_status": source_status,
        "header_statuses": headers.get("connect_statuses", []) + ([source_status] if source_status is not None else []),
        "retry_after": headers.get("retry_after"),
        "body_bytes": body_bytes,
        "body_limit_bytes": body_limit,
        "body_sha256": sha_file(body_path) if body_path.exists() else sha_bytes(b""),
        "disk_free_before_bytes": disk_before,
        "transport_failed": source_status is None,
        "raw": {
            "body": rel(body_path),
            "headers": rel(header_path),
            "stderr": rel(stderr_path),
            "metrics": rel(metrics_path),
        },
    }
    return attempt


def _run_execute() -> int:
    plan, _bindings = validate_local_inputs()
    _go_gate()
    now = utc_now()
    start = datetime.fromisoformat(RUN_START_UTC.replace("Z", "+00:00"))
    stop = datetime.fromisoformat(NETWORK_STOP_UTC.replace("Z", "+00:00"))
    deadline = datetime.fromisoformat(RUN_DEADLINE_UTC.replace("Z", "+00:00"))
    if now < start:
        raise RuntimeError("recovery run has not started")
    if now >= stop:
        raise RuntimeError("network batch cutoff has passed")
    if now >= deadline:
        raise RuntimeError("recovery run deadline has passed")
    if REPORT_PATH.exists() or RECORDS_PATH.exists() or RAW.exists():
        raise RuntimeError("execute output/raw already exists; refusing rerun")
    assert_disk()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir()
    run_started = utc_now()
    run_started_mono = time.monotonic()
    attempts: list[dict[str, Any]] = []
    target_results: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    total_body_bytes = 0
    logical_completed = 0
    last_start_mono: float | None = None
    transport_streak = 0
    stop_reason: str | None = None
    cooldown_not_before: str | None = None

    def body_for(attempt: dict[str, Any]) -> bytes:
        path = ROOT / attempt["raw"]["body"]
        return path.read_bytes() if path.is_file() else b""

    def set_cooldown(attempt: dict[str, Any]) -> None:
        nonlocal cooldown_not_before
        retry_after = attempt.get("retry_after")
        try:
            retry_seconds = max(0, int(retry_after or 0))
        except (TypeError, ValueError):
            retry_seconds = 0
        cooldown_seconds = max(COOLDOWN_SECONDS, retry_seconds)
        attempt["cooldown_seconds_applied"] = cooldown_seconds
        cooldown_not_before = iso(datetime.fromisoformat(attempt["finished_utc"].replace("Z", "+00:00")) + timedelta(seconds=cooldown_seconds))

    def ready_for_dispatch() -> bool:
        nonlocal stop_reason
        if time.monotonic() - run_started_mono > MAX_SECONDS:
            stop_reason = "parent_watchdog_elapsed"
            return False
        current = utc_now()
        if current >= stop:
            stop_reason = "network_stop_elapsed"
            return False
        if current >= deadline:
            stop_reason = "run_deadline_elapsed"
            return False
        remaining = MAX_TOTAL_BODY_BYTES - total_body_bytes
        if remaining < MAX_BODY_BYTES_PER_ATTEMPT:
            stop_reason = "remaining_body_budget_below_per_attempt_cap"
            return False
        return True

    def request(label: str, url: str) -> dict[str, Any] | None:
        nonlocal last_start_mono, total_body_bytes, transport_streak, stop_reason, cooldown_not_before
        if len(attempts) >= MAX_ATTEMPTS:
            stop_reason = "maximum_http_attempts"
            return None
        if not ready_for_dispatch():
            return None
        _wait_for_cadence(last_start_mono)
        if not ready_for_dispatch():
            return None
        last_start_mono = time.monotonic()
        attempt_number = len(attempts) + 1
        result = _run_curl(url, "direct", attempt_number, label, min(MAX_BODY_BYTES_PER_ATTEMPT, MAX_TOTAL_BODY_BYTES - total_body_bytes))
        attempts.append(result)
        total_body_bytes += result["body_bytes"]
        if total_body_bytes > MAX_TOTAL_BODY_BYTES:
            stop_reason = "maximum_total_body_bytes"
            return None
        if result["transport_failed"]:
            transport_streak += 1
        else:
            transport_streak = 0
        if result["source_status"] in STOP_HTTP_CODES:
            stop_reason = f"endpoint_status_{result['source_status']}"
            set_cooldown(result)
            return result
        if transport_streak >= MAX_CONSECUTIVE_TRANSPORT_FAILURES:
            stop_reason = "five_consecutive_transport_failures"
            return result
        if not result["transport_failed"]:
            return result
        if len(attempts) >= MAX_ATTEMPTS:
            stop_reason = "maximum_http_attempts"
            return result
        if not ready_for_dispatch():
            return result
        _wait_for_cadence(last_start_mono)
        if not ready_for_dispatch():
            return result
        last_start_mono = time.monotonic()
        attempt_number = len(attempts) + 1
        fallback = _run_curl(url, "proxy", attempt_number, label, min(MAX_BODY_BYTES_PER_ATTEMPT, MAX_TOTAL_BODY_BYTES - total_body_bytes))
        attempts.append(fallback)
        total_body_bytes += fallback["body_bytes"]
        if total_body_bytes > MAX_TOTAL_BODY_BYTES:
            stop_reason = "maximum_total_body_bytes"
            return fallback
        if fallback["transport_failed"]:
            transport_streak += 1
        else:
            transport_streak = 0
        if fallback["source_status"] in STOP_HTTP_CODES:
            stop_reason = f"endpoint_status_{fallback['source_status']}"
            set_cooldown(fallback)
        elif transport_streak >= MAX_CONSECUTIVE_TRANSPORT_FAILURES:
            stop_reason = "five_consecutive_transport_failures"
        return fallback

    collection_attempt = request("collinfo", COLLINFO_URL)
    collection_summary: dict[str, Any] = {"valid": False, "collection_found": False}
    if collection_attempt is not None:
        collection_body = body_for(collection_attempt)
        if collection_attempt["source_status"] == 200:
            collection_summary = parse_collinfo(collection_body)
        else:
            collection_summary = {"valid": False, "body_state": "http_status", "collection_found": False}
        logical_completed += 1
    if stop_reason is None and (collection_attempt is None or collection_attempt["source_status"] != 200 or not collection_summary.get("valid") or not collection_summary.get("collection_found")):
        stop_reason = stop_reason or "collection_metadata_unconfirmed"

    if stop_reason is None:
        for target in TARGETS:
            result = request(target["id"], build_index_url(target))
            if result is None:
                break
            logical_completed += 1
            body = body_for(result)
            parsed = parse_index_json_lines(body) if result["source_status"] == 200 else {
                "valid": False,
                "body_state": "http_status",
                "rows": [],
                "row_count": 0,
            }
            target_result = {
                "target_id": target["id"],
                "url": target["url"],
                "match_type": target["match_type"],
                "query_url": build_index_url(target),
                "source_status": result["source_status"],
                "body_state": parsed.get("body_state"),
                "valid_json_lines": parsed.get("valid", False),
                "row_count": parsed.get("row_count", 0),
                "limit_reached": parsed.get("row_count", 0) >= INDEX_LIMIT,
                "more_rows_unknown": parsed.get("row_count", 0) >= INDEX_LIMIT,
                "body_bytes": result["body_bytes"],
                "body_sha256": result["body_sha256"],
                "index_404_is_not_image_404": result["source_status"] == 404,
            }
            target_results.append(target_result)
            for row in parsed.get("rows", []):
                normalized = normalize_capture(row)
                records.append({
                    "target_id": target["id"],
                    "collection": COLLECTION_ID,
                    "match_type": target["match_type"],
                    "query_url": build_index_url(target),
                    "source_status": result["source_status"],
                    **normalized,
                })
            if stop_reason is not None:
                break

    RECORDS_PATH.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in records), encoding="utf-8")
    finished = utc_now()
    report = {
        "schema": "wow-recovery.commoncrawl-probe01-report.v1",
        "batch_id": plan["batch_id"],
        "provider": "commoncrawl",
        "collection_id": COLLECTION_ID,
        "started_utc": iso(run_started),
        "finished_utc": iso(finished),
        "plan_sha256": sha_file(PLAN_PATH),
        "driver_sha256": sha_file(Path(__file__)),
        "fixture_sha256": sha_file(FIXTURE_PATH),
        "input_bindings_sha256": sha_file(BINDINGS_PATH),
        "root_go_receipt": rel(GO_PATH),
        "root_go_sha256": sha_file(GO_PATH),
        "logical_requests_completed": logical_completed,
        "network_attempts_total": len(attempts),
        "network_requests_total": len(attempts),
        "wayback_requests": 0,
        "total_body_bytes": total_body_bytes,
        "collection_metadata": collection_summary,
        "target_results": target_results,
        "attempts": attempts,
        "index_records_path": rel(RECORDS_PATH),
        "index_records_count": len(records),
        "accepted_image_count": 0,
        "payload_replays": 0,
        "stop_reason": stop_reason or "completed",
        "cooldown_not_before_utc": cooldown_not_before,
        "raw_http_private": True,
        "disk_free_after_bytes": assert_disk(),
    }
    write_json(REPORT_PATH, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture", action="store_true", help="run offline parser and constraint fixtures")
    group.add_argument("--execute", action="store_true", help="run only after the future root GO receipt exists")
    args = parser.parse_args()
    if args.fixture:
        return run_fixture()
    return _run_execute()


if __name__ == "__main__":
    raise SystemExit(main())

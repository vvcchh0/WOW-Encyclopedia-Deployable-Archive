"""Bounded post-503 exact-CDX control for the gallery-late-rest10b boundary.

This packet is deliberately independent of the completed 10b runner.  Importing
the module is offline; only ``--execute`` can invoke curl, and execute mode
requires a future root GO receipt whose hashes bind this packet.  The only
network operation is one exact CDX query, tried direct and then through the
approved process proxy.  It never replays an image, follows a redirect, or
continues a CDX page.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "research" / "continuous-recovery-20261019"
PLAN_PATH = OUT / "plan.json"
BINDINGS_PATH = OUT / "input-bindings.json"
FIXTURE_PATH = OUT / "fixture-results.json"
GO_PATH = BASE / "publication" / "root-control-after-rest10b-execute-go.json"
RAW = OUT / "raw"
REPORT_PATH = OUT / "control-report.json"
STATE_PATH = OUT / "state.json"
PARSER_PATH = ROOT / "research" / "continuous-recovery-20261016" / "network" / "control02-plan" / "control02_driver.py"

ORIGINAL = "http://www.worldofwarcraft.com/news/images/08-02/02-14-08-2.jpg"
FROM_TS = "20000101000000"
TO_TS = "20080512210044"
CDX_FIELDS = ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
PROXY = "http://127.0.0.1:7890"
TARGET_KEY = "CONTROL-AFTER-REST10B-known-news-image-exact-cdx"
MAX_REQUESTS = 2
MAX_SECONDS = 120.0
OUTER_WATCHDOG_SECONDS = 180.0
MAX_TOTAL_BODY_BYTES = 2 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 1 * 1024 * 1024
MIN_DISPATCH_SECONDS = 5.25
MIN_REQUEST_START_SECONDS = 5.0
DISK_FLOOR_BYTES = 11_005_853_696
COOLDOWN_SECONDS = 120
STOP_HTTP_CODES = {429, 503}
COOLDOWN_NOT_BEFORE = "2026-10-19T10:46:35.479615Z"
PARSER_SHA256 = "85457ea1baa96c474e33ffc01210b4f6d96b3d6d276dc7a2b56aff3cd8376530"
REPORT_SHA256 = "3a62951482e7a6ea8835fa76928aece1210745e09b5d11d46a43ed46828033d0"
PARTIAL_ACCEPTANCE_SHA256 = "73cfbbe8594357128cc658571a2681262628ca561c3d62b45eb11d1406c6059d"
KNOWN_CONTROL_SHA256 = "7145994e5663a28a4f808fb82586ab51b2da2054da087a821cc3fee4ec540cd8"
KNOWN_SOURCE_SHA256 = "1746b07c0359621975d81371034008045dd17f3a2548691c1b75b9a895dc9184"
KNOWN_CAPTURE_TIMESTAMP = "20080402035201"
KNOWN_DIGEST = "TJ2TFHNGVSA64RRRP3UD2CQZCP4TTRND"
KNOWN_MIME = "image/jpeg"


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


def build_query() -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(ORIGINAL, safe="")
        + "&from=" + FROM_TS + "&to=" + TO_TS
        + "&output=json&fl=" + quote(",".join(CDX_FIELDS), safe="")
        + "&limit=10&showResumeKey=true&matchType=exact"
    )


def load_parser():
    if sha_file(PARSER_PATH) != PARSER_SHA256:
        raise RuntimeError("frozen parser SHA mismatch")
    spec = importlib.util.spec_from_file_location("frozen_control02_parser_rest10b", PARSER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_original(value: str) -> str:
    return value.replace(":80/", "/")


def known_row_matches(parsed: dict[str, Any]) -> bool:
    if not parsed.get("valid") or not parsed.get("complete") or parsed.get("resume_keys"):
        return False
    for row in parsed.get("rows", []):
        if (
            row.get("timestamp") == KNOWN_CAPTURE_TIMESTAMP
            and normalize_original(row.get("original", "")) == ORIGINAL
            and row.get("mimetype") == KNOWN_MIME
            and row.get("statuscode") == "200"
            and row.get("digest") == KNOWN_DIGEST
        ):
            return True
    return False


def _check_bound_file(root: Path, item: dict[str, Any]) -> None:
    path = root / item["path"]
    if not path.is_file():
        raise RuntimeError(f"bound file missing: {item['path']}")
    if sha_file(path) != item["sha256"]:
        raise RuntimeError(f"bound file SHA mismatch: {item['path']}")
    if path.stat().st_size != item["bytes"]:
        raise RuntimeError(f"bound file byte mismatch: {item['path']}")


def validate_local_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    plan = read_json(PLAN_PATH)
    bindings = read_json(BINDINGS_PATH)
    if plan.get("schema") != "wow-recovery.control-after-rest10b-plan.v1":
        raise RuntimeError("unexpected plan schema")
    if plan.get("mode") != "prepared" or not plan.get("root_go_required"):
        raise RuntimeError("plan must remain prepared and root-gated")
    if plan.get("exact_original") != ORIGINAL or plan.get("target_key") != TARGET_KEY:
        raise RuntimeError("exact target identity mismatch")
    if plan.get("query_url") != build_query():
        raise RuntimeError("query URL identity mismatch")
    if plan.get("query", {}).get("limit") != 10 or plan["query"].get("match_type") != "exact":
        raise RuntimeError("query limit or exact mode mismatch")
    policy = plan.get("policy", {})
    required_policy = {
        "maximum_requests": MAX_REQUESTS,
        "maximum_seconds": MAX_SECONDS,
        "outer_watchdog_seconds": OUTER_WATCHDOG_SECONDS,
        "maximum_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "maximum_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "minimum_dispatch_seconds": MIN_DISPATCH_SECONDS,
        "minimum_request_start_seconds": MIN_REQUEST_START_SECONDS,
        "disk_floor_bytes": DISK_FLOOR_BYTES,
        "automatic_redirects": False,
        "payload_replay": False,
        "no_pagination": True,
        "no_image_replay": True,
    }
    for key, expected in required_policy.items():
        if policy.get(key) != expected:
            raise RuntimeError(f"policy mismatch: {key}")
    if bindings.get("schema") != "wow-recovery.control-after-rest10b-input-bindings.v1":
        raise RuntimeError("unexpected binding schema")
    plan_binding = bindings.get("plan", {})
    if plan_binding.get("sha256") != sha_file(PLAN_PATH) or plan_binding.get("bytes") != PLAN_PATH.stat().st_size:
        raise RuntimeError("plan binding mismatch")
    for section in ("latest_failure", "known_control", "frozen_parser"):
        values = bindings.get(section, {})
        for key, item in values.items():
            if isinstance(item, dict) and {"path", "sha256", "bytes"}.issubset(item):
                _check_bound_file(ROOT, item)
    runtime = bindings.get("future_runtime_files", {})
    for item in runtime.values():
        if isinstance(item, dict) and {"path", "sha256", "bytes"}.issubset(item):
            _check_bound_file(ROOT, item)
    failure = bindings["latest_failure"]
    if failure["batch_report"]["sha256"] != REPORT_SHA256 or failure["partial_source_acceptance"]["sha256"] != PARTIAL_ACCEPTANCE_SHA256:
        raise RuntimeError("latest 10b failure binding mismatch")
    if failure["stop_reason"] != "endpoint_status_503" or failure["resume_gate_passed"] is not False:
        raise RuntimeError("latest 10b is not the expected partial 503 state")
    if failure["cooldown_not_before_utc"] != COOLDOWN_NOT_BEFORE:
        raise RuntimeError("10b cooldown binding mismatch")
    if sha_file(PARSER_PATH) != PARSER_SHA256:
        raise RuntimeError("frozen parser SHA mismatch")
    known = bindings["known_control"]
    if known["report"]["sha256"] != KNOWN_CONTROL_SHA256:
        raise RuntimeError("known control SHA mismatch")
    if known["successful_original"] != ORIGINAL or known["successful_capture_timestamp"] != KNOWN_CAPTURE_TIMESTAMP:
        raise RuntimeError("known positive identity mismatch")
    return plan, bindings


def disk_free() -> int:
    return shutil.disk_usage(ROOT).free


def assert_disk() -> int:
    free = disk_free()
    if free < DISK_FLOOR_BYTES:
        raise RuntimeError(f"disk floor failed: {free}")
    return free


def _fixture() -> dict[str, Any]:
    parser = load_parser()
    synthetic_200 = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 1\r\n\r\n"
    synthetic_proxy = b"HTTP/1.1 200 Connection established\r\n\r\nHTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
    synthetic_503 = b"HTTP/1.1 503 Service Unavailable\r\nRetry-After: 120\r\n\r\n"
    known = json.dumps([
        CDX_FIELDS,
        [KNOWN_CAPTURE_TIMESTAMP, "http://www.worldofwarcraft.com:80/news/images/08-02/02-14-08-2.jpg", KNOWN_MIME, "200", KNOWN_DIGEST, "9971"],
    ], separators=(",", ":")).encode()
    resumed = json.dumps([CDX_FIELDS, ["resume-token"]], separators=(",", ":")).encode()
    empty = b"[]"
    cases = {
        "plan_query_is_exact_and_no_pagination": build_query().endswith("limit=10&showResumeKey=true&matchType=exact"),
        "direct_header_200": parser.parse_headers(synthetic_200)["status"] == 200,
        "proxy_connect_header_200": parser.parse_headers(synthetic_proxy)["status"] == 200 and parser.parse_headers(synthetic_proxy)["connect_statuses"] == [200],
        "503_retry_after_parser": parser.parse_headers(synthetic_503)["status"] == 503 and parser.parse_headers(synthetic_503)["retry_after"] == 120,
        "known_row_positive_with_port_normalization": known_row_matches(parser.parse_cdx(known)),
        "resume_key_is_incomplete": parser.parse_cdx(resumed)["complete"] is False and parser.parse_cdx(resumed)["resume_keys"] == ["resume-token"],
        "empty_cdx_is_complete": parser.parse_cdx(empty)["valid"] and parser.parse_cdx(empty)["complete"],
        "entity_and_total_caps": MAX_ENTITY_BODY_BYTES <= MAX_TOTAL_BODY_BYTES and MAX_TOTAL_BODY_BYTES == 2 * 1024 * 1024,
        "cadence_policy": MIN_DISPATCH_SECONDS >= 5.25 and MIN_REQUEST_START_SECONDS >= 5.0,
        "stop_policy": STOP_HTTP_CODES == {429, 503} and COOLDOWN_SECONDS >= 120,
        "disk_policy": DISK_FLOOR_BYTES == 11005853696,
        "fixture_has_no_network_entrypoint": True,
    }
    return {
        "schema": "wow-recovery.control-after-rest10b-fixtures.v1",
        "network_requests": 0,
        "raw_written": False,
        "all_passed": all(cases.values()),
        "case_count": len(cases),
        "cases": cases,
        "parser_sha256": PARSER_SHA256,
        "checked_utc": iso(utc_now()),
    }


def run_fixture() -> int:
    validate_local_inputs()
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
    if go.get("latest_failure_report_sha256") not in {None, REPORT_SHA256}:
        raise RuntimeError("root GO does not bind the latest 10b report")
    return go


def _wait_for_cadence(last_dispatch: float | None, last_start: float | None) -> None:
    while True:
        now = time.monotonic()
        remaining = 0.0
        if last_dispatch is not None:
            remaining = max(remaining, MIN_DISPATCH_SECONDS - (now - last_dispatch))
        if last_start is not None:
            remaining = max(remaining, MIN_REQUEST_START_SECONDS - (now - last_start))
        if remaining <= 0:
            return
        time.sleep(min(0.1, remaining))


def _run_execute() -> int:
    plan, bindings = validate_local_inputs()
    go = _go_gate()
    now = utc_now()
    if now < datetime.fromisoformat(COOLDOWN_NOT_BEFORE.replace("Z", "+00:00")):
        raise RuntimeError("10b cooldown has not elapsed")
    if REPORT_PATH.exists() or STATE_PATH.exists() or RAW.exists():
        raise RuntimeError("execute output/raw already exists; refusing rerun")
    assert_disk()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir()
    started = time.monotonic()
    first_dispatch: float | None = None
    last_start: float | None = None
    total = 0
    failure_streak = 0
    attempts: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "schema": "wow-recovery.control-after-rest10b-report.v1",
        "batch_id": plan["batch_id"],
        "started_utc": iso(now),
        "plan_sha256": sha_file(PLAN_PATH),
        "driver_sha256": sha_file(Path(__file__)),
        "fixture_sha256": sha_file(FIXTURE_PATH),
        "input_bindings_sha256": sha_file(BINDINGS_PATH),
        "root_go_receipt": rel(GO_PATH),
        "root_go_sha256": sha_file(GO_PATH),
        "latest_failure_report_sha256": REPORT_SHA256,
        "latest_failure_resume_gate_passed": False,
        "latest_failure_cooldown_not_before_utc": COOLDOWN_NOT_BEFORE,
        "exact_original": ORIGINAL,
        "query_url": build_query(),
        "maximum_requests": MAX_REQUESTS,
        "maximum_seconds": MAX_SECONDS,
        "maximum_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "maximum_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "attempts": attempts,
        "control_positive": False,
        "payload_replays": 0,
        "continuation_followed": False,
        "redirects_followed": False,
        "failure_streak_start": 0,
        "failure_streak_end": 0,
        "network_requests": 0,
        "source_responses": 0,
        "total_body_bytes": 0,
        "disk_floor_bytes": DISK_FLOOR_BYTES,
        "stop_reason": None,
        "cooldown_not_before_utc": None,
        "go_latest_failure_binding": go.get("latest_failure_report_sha256", REPORT_SHA256),
    }
    for transport in ("direct", "proxy"):
        if len(attempts) >= MAX_REQUESTS:
            break
        _wait_for_cadence(first_dispatch, last_start)
        elapsed = time.monotonic() - started
        remaining = MAX_SECONDS - elapsed
        if remaining <= 0:
            report["stop_reason"] = "control_window_exhausted"
            break
        disk_before = assert_disk()
        dispatch = time.monotonic()
        if first_dispatch is None:
            first_dispatch = dispatch
        # The first request-start measurement is taken immediately before curl;
        # the second is measured against the first actual subprocess start.
        request_start = time.monotonic()
        last_start = request_start
        stamp = utc_now()
        prefix = RAW / ("01-direct" if transport == "direct" else "02-proxy")
        body = prefix.with_suffix(".body")
        headers = prefix.with_suffix(".headers.txt")
        trace = prefix.with_suffix(".trace.txt")
        stderr = prefix.with_suffix(".stderr.txt")
        metrics = prefix.with_suffix(".metrics.txt")
        command = [
            "curl.exe", "--silent", "--show-error", "--trace-time", "--trace-ascii", str(trace),
            "--header", "Accept-Encoding: identity", "--connect-timeout", "4" if transport == "direct" else "8",
            "--max-time", str(max(1.0, min(12.0 if transport == "direct" else 20.0, remaining))),
            "--max-filesize", str(MAX_ENTITY_BODY_BYTES), "--max-redirs", "0", "--dump-header", str(headers),
            "--output", str(body), "--write-out", "%{http_code}\n%{time_connect}\n%{time_appconnect}\n%{time_starttransfer}\n%{time_total}",
            build_query(),
        ]
        if transport == "direct":
            command[1:1] = ["--noproxy", "*"]
        else:
            command[1:1] = ["--noproxy", "", "--proxy", PROXY]
        curl_exit: int | None = None
        stdout = b""
        exception = None
        with stderr.open("wb") as stream:
            try:
                completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=stream, timeout=max(1.0, min(25.0, remaining)), check=False)
                curl_exit, stdout = completed.returncode, completed.stdout or b""
            except subprocess.TimeoutExpired as exc:
                exception = "TimeoutExpired"
                stdout = exc.stdout or b""
        if isinstance(stdout, str):
            stdout = stdout.encode("utf-8", errors="replace")
        metrics.write_bytes(stdout)
        finished = utc_now()
        payload = body.read_bytes() if body.exists() else b""
        raw_headers = headers.read_bytes() if headers.exists() else b""
        parsed_headers = load_parser().parse_headers(raw_headers)
        status = parsed_headers.get("status")
        total += len(payload)
        if len(payload) > MAX_ENTITY_BODY_BYTES or total > MAX_TOTAL_BODY_BYTES:
            raise RuntimeError("body cap exceeded")
        if status is None:
            failure_streak += 1
        else:
            failure_streak = 0
            report["source_responses"] += 1
        parsed_cdx: dict[str, Any] = {"valid": False, "complete": False, "rows": [], "resume_keys": []}
        positive = False
        parse_error = None
        if curl_exit == 0 and status == 200:
            parsed_cdx = load_parser().parse_cdx(payload)
            positive = known_row_matches(parsed_cdx)
            if not parsed_cdx.get("valid"):
                parse_error = parsed_cdx.get("error")
        attempt = {
            "attempt": len(attempts) + 1,
            "transport": transport,
            "started_utc": iso(stamp),
            "finished_utc": iso(finished),
            "dispatch_monotonic": dispatch,
            "request_start_monotonic": request_start,
            "dispatch_interval_seconds": None if len(attempts) == 0 else dispatch - attempts[-1]["dispatch_monotonic"],
            "request_start_interval_seconds": None if len(attempts) == 0 else request_start - attempts[-1]["request_start_monotonic"],
            "curl_exit": curl_exit,
            "exception": exception,
            "source_status": status,
            "content_type": parsed_headers.get("content_type"),
            "retry_after": parsed_headers.get("retry_after"),
            "metrics": stdout.decode("utf-8", errors="replace"),
            "body_bytes": len(payload),
            "body_sha256": sha_bytes(payload),
            "cdx_valid": parsed_cdx.get("valid"),
            "cdx_complete": parsed_cdx.get("complete"),
            "cdx_rows": len(parsed_cdx.get("rows", [])),
            "resume_keys": parsed_cdx.get("resume_keys", []),
            "positive_known_row": positive,
            "disk_free_before_bytes": disk_before,
            "raw": {"body": rel(body), "headers": rel(headers), "trace": rel(trace), "stderr": rel(stderr), "metrics": rel(metrics)},
        }
        attempts.append(attempt)
        report["network_requests"] = len(attempts)
        report["total_body_bytes"] = total
        report["failure_streak_end"] = failure_streak
        if status in STOP_HTTP_CODES:
            cooldown = max(COOLDOWN_SECONDS, int(parsed_headers.get("retry_after") or 0))
            report["cooldown_not_before_utc"] = iso(utc_now() + timedelta(seconds=cooldown))
            report["stop_reason"] = f"endpoint_status_{status}"
            break
        if failure_streak >= 5:
            report["cooldown_not_before_utc"] = iso(utc_now() + timedelta(seconds=COOLDOWN_SECONDS))
            report["stop_reason"] = "five_transport_failures"
            break
        if positive:
            report["control_positive"] = True
            report["control_success_finished_utc"] = iso(finished)
            report["stop_reason"] = "known_exact_cdx_row"
            break
    if report["stop_reason"] is None:
        report["stop_reason"] = "completed_without_positive"
    report.update(
        finished_utc=iso(utc_now()),
        elapsed_seconds=time.monotonic() - started,
        disk_free_after_bytes=disk_free(),
        final_failure_streak=failure_streak,
    )
    assert report["elapsed_seconds"] <= MAX_SECONDS
    assert_disk()
    write_json(STATE_PATH, {
        "schema": "wow-recovery.control-after-rest10b-state.v1",
        "batch_id": plan["batch_id"],
        "network_requests": report["network_requests"],
        "source_responses": report["source_responses"],
        "control_positive": report["control_positive"],
        "stop_reason": report["stop_reason"],
        "failure_streak_end": report["failure_streak_end"],
        "cooldown_not_before_utc": report["cooldown_not_before_utc"],
        "tail_before": 0,
        "tail_after": report["failure_streak_end"],
        "resume_gate_passed": report["control_positive"] and report["failure_streak_end"] == 0,
        "report_sha256_after_write": None,
    })
    write_json(REPORT_PATH, report)
    state = read_json(STATE_PATH)
    state["report_sha256_after_write"] = sha_file(REPORT_PATH)
    write_json(STATE_PATH, state)
    print(json.dumps({key: value for key, value in report.items() if key != "attempts"}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.fixture:
        return run_fixture()
    return _run_execute()


if __name__ == "__main__":
    raise SystemExit(main())

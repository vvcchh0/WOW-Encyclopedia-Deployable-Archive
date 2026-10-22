#!/usr/bin/env python3
"""Offline preparation and fresh-root-GO-gated Wayback CDX positive control.

The default and --fixture modes are offline. Only --execute --go PATH can
open a socket. That mode is bound to one exact CDX query and at most two
attempts (direct, then the local proxy only after a transport failure). It
never follows redirects, paginates, retries an HTTP response, or fetches an
archived image payload.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import math
import re
import shutil
import socket
import ssl
import tempfile
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
PREP = Path(__file__).resolve().parent
PLAN = PREP / "plan.json"
INPUT_BINDINGS = PREP / "input-bindings.json"
FIXTURE = PREP / "root-offline-fixture.json"
SOURCE_SELECTION = PREP / "source-selection.json"
RUNNER = Path(__file__).resolve()
OFFLINE_VALIDATION = PREP / "offline-validation.json"
GO_PATH = ROOT / "research/continuous-recovery-20261022/root-wayback-control03-go.json"
RUNTIME = PREP / "runtime"
REPORT = RUNTIME / "control-report.json"
RAW = RUNTIME / "private/raw"

ORIGINAL = "http://www.worldofwarcraft.com/news/images/08-02/02-14-08-2.jpg"
ENDPOINT = "https://web.archive.org/cdx/search/cdx"
QUERY_URL = (
    "https://web.archive.org/cdx/search/cdx?url="
    "http%3A%2F%2Fwww.worldofwarcraft.com%2Fnews%2Fimages%2F08-02%2F02-14-08-2.jpg"
    "&from=20000101000000&to=20080512210044&output=json"
    "&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest%2Clength"
    "&limit=10&showResumeKey=true&matchType=exact"
)
CDX_FIELDS = ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
KNOWN_TIMESTAMP = "20080402035201"
KNOWN_DIGEST = "TJ2TFHNGVSA64RRRP3UD2CQZCP4TTRND"
KNOWN_MIME = "image/jpeg"
KNOWN_STATUS = "200"
KNOWN_CDX_LENGTH = "10259"
PAYLOAD_BYTES = 9971
PAYLOAD_SHA256 = "10fea360ed507351a75a9f46f43f44d09ebabc45fd6143614fe9f5def4fc7a57"
PROXY = "http://127.0.0.1:7890"
DISK_FLOOR = 11_005_853_696
ENTITY_BODY_CAP = 1_048_576
TOTAL_BODY_CAP = 1_048_576
MAX_LOGICAL_REQUESTS = 1
MAX_HTTP_ATTEMPTS = 2
CHILD_SECONDS = 90.0
PARENT_WATCHDOG_SECONDS = 180
MIN_REQUEST_START_SECONDS = 5.0
DISPATCH_SPACING_SECONDS = 8.0
CONNECT_SECONDS = 10
REQUEST_SECONDS = 35
STOP_STATUSES = {429, 503}
COOLDOWN_SECONDS = 120
MAX_CONSECUTIVE_TRANSPORT_FAILURES = 5
USER_AUTH_WINDOW_END = datetime(2026, 10, 22, 14, 51, 33, tzinfo=timezone.utc)
RETRY_AFTER_HEADER = "retry-after"


class IncompleteBodyRead(RuntimeError):
    def __init__(self, cause_name: str, partial: bytes):
        super().__init__(cause_name)
        self.cause_name = cause_name
        self.partial = partial


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_text(value: datetime | None = None) -> str:
    return (value or utc_now()).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("UTC timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def disk_free() -> int:
    return shutil.disk_usage(ROOT).free


def require_disk(stage: str) -> int:
    free = disk_free()
    if free < DISK_FLOOR:
        raise RuntimeError(f"D: disk floor failed {stage}: {free} < {DISK_FLOOR}")
    return free


def relative_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def parse_cdx(data: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"valid": False, "complete": False, "rows": [], "resume_keys": [], "error": "json_decode"}
    if payload == []:
        return {"valid": True, "complete": True, "rows": [], "resume_keys": [], "error": None}
    if not isinstance(payload, list):
        return {"valid": False, "complete": False, "rows": [], "resume_keys": [], "error": "json_shape"}

    header_seen = False
    rows: list[dict[str, str]] = []
    resume_keys: list[str] = []
    unknown = False
    for item in payload:
        if isinstance(item, dict):
            if "resumeKey" in item:
                resume_keys.append(str(item["resumeKey"]))
            elif all(field in item for field in CDX_FIELDS):
                rows.append({field: str(item[field]) for field in CDX_FIELDS})
            else:
                unknown = True
            continue
        if not isinstance(item, list):
            unknown = True
            continue
        values = [str(value) for value in item]
        if not header_seen and values == CDX_FIELDS:
            header_seen = True
        elif len(values) == 1:
            resume_keys.append(values[0])
        elif header_seen and len(values) == len(CDX_FIELDS):
            rows.append({field: values[index] for index, field in enumerate(CDX_FIELDS)})
        else:
            unknown = True
    valid = not unknown and (header_seen or bool(rows))
    truncated = bool(resume_keys) or len(rows) >= 10
    return {
        "valid": valid,
        "complete": valid and not truncated,
        "rows": rows,
        "resume_keys": resume_keys,
        "error": "unrecognized_metadata" if unknown else None,
    }


def positive_row_matches(parsed: dict[str, Any]) -> bool:
    if not parsed.get("valid") or not parsed.get("complete") or parsed.get("resume_keys"):
        return False
    return any(
        row.get("timestamp") == KNOWN_TIMESTAMP
        and row.get("original") == ORIGINAL
        and row.get("mimetype") == KNOWN_MIME
        and row.get("statuscode") == KNOWN_STATUS
        and row.get("digest") == KNOWN_DIGEST
        and row.get("length") == KNOWN_CDX_LENGTH
        for row in parsed.get("rows", [])
    )


def parse_retry_after(value: str | None, *, finished: datetime) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if re.fullmatch(r"\d+", value):
        return int(value)
    try:
        retry_at = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    return max(0, math.ceil((retry_at.astimezone(timezone.utc) - finished).total_seconds()))


def cooldown_not_before(status: int, retry_after: str | None, *, finished: datetime) -> datetime | None:
    if status not in STOP_STATUSES:
        return None
    retry_seconds = parse_retry_after(retry_after, finished=finished) or 0
    return finished + timedelta(seconds=max(COOLDOWN_SECONDS, retry_seconds))


def transport_failure_cooldown(streak: int, *, finished: datetime) -> datetime | None:
    if streak < MAX_CONSECUTIVE_TRANSPORT_FAILURES:
        return None
    return finished + timedelta(seconds=COOLDOWN_SECONDS)


def attempt_classification(*, status: int | None, positive: bool, transfer_error: bool, body_cap: bool) -> str:
    if status in STOP_STATUSES:
        return "endpoint_stop"
    if body_cap:
        return "body_cap_stop"
    if transfer_error:
        return "transport_failure"
    if positive:
        return "known_exact_cdx_row"
    if status is not None:
        return "http_response_without_positive_row"
    return "transport_failure"


def should_try_proxy(*, transport: str, classification: str) -> bool:
    return transport == "direct" and classification == "transport_failure"


def validate_static_inputs(*, require_runtime_absent: bool = True) -> dict[str, Any]:
    plan = load_json(PLAN)
    selection = load_json(SOURCE_SELECTION)
    bindings = load_json(INPUT_BINDINGS)
    if plan.get("mode") != "prepared_only" or plan.get("network_requests_executed_at_prepare") != 0:
        raise RuntimeError("plan is not offline preparation-only")
    if plan.get("exact_target", {}).get("query_url") != QUERY_URL:
        raise RuntimeError("exact CDX query mismatch")
    if plan.get("positive_control_identity", {}).get("cdx_record_length") != KNOWN_CDX_LENGTH:
        raise RuntimeError("plan CDX row length mismatch")
    if plan.get("positive_control_identity", {}).get("payload_identity_reference_only", {}).get("bytes") != PAYLOAD_BYTES:
        raise RuntimeError("separate payload length metadata mismatch")
    if selection.get("expected_cdx_row", {}).get("cdx_record_length") != KNOWN_CDX_LENGTH:
        raise RuntimeError("source-selection CDX row length mismatch")
    if selection.get("separate_payload_evidence", {}).get("bytes") != PAYLOAD_BYTES:
        raise RuntimeError("source-selection payload length mismatch")
    if sha256_file(SOURCE_SELECTION) != plan.get("source_selection", {}).get("sha256"):
        raise RuntimeError("source-selection hash mismatch")
    if sha256_file(INPUT_BINDINGS) != plan.get("input_bindings", {}).get("sha256"):
        raise RuntimeError("input-bindings hash mismatch")

    for item in bindings.get("bindings", []):
        path = ROOT / item["path"]
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"bound source hash mismatch: {item['path']}")
        if item.get("bytes") is not None and path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"bound source size mismatch: {item['path']}")

    positive_raw = ROOT / "research/continuous-recovery-20261018/network/control-after-gallery15/proxy.body"
    positive_parsed = parse_cdx(positive_raw.read_bytes())
    if not positive_row_matches(positive_parsed):
        raise RuntimeError("historical positive CDX body does not contain the exact 10259 row")
    if not any(row.get("length") == "10257" and row.get("original", "").startswith("https://") for row in positive_parsed["rows"]):
        raise RuntimeError("historical second HTTPS row missing from control evidence")

    accepted_payload = ROOT / "research/continuous-recovery-20261018/publication/accepted-images/news-unplanned-batch1/01-image.jpg"
    payload_data = accepted_payload.read_bytes()
    if len(payload_data) != PAYLOAD_BYTES or hashlib.sha256(payload_data).hexdigest() != PAYLOAD_SHA256:
        raise RuntimeError("accepted payload identity mismatch")
    if not payload_data.startswith(b"\xff\xd8\xff"):
        raise RuntimeError("accepted payload is not JPEG by signature")
    payload_acceptance = load_json(ROOT / "research/continuous-recovery-20261018/publication/root-news-unplanned-batch1-source-acceptance.json")
    accepted_record = next((x for x in payload_acceptance.get("accepted_images", []) if x.get("original") == ORIGINAL), None)
    if not accepted_record or accepted_record.get("length") != PAYLOAD_BYTES or accepted_record.get("sha256") != PAYLOAD_SHA256 or accepted_record.get("mime") != KNOWN_MIME:
        raise RuntimeError("root-accepted payload metadata mismatch")

    latest_acceptance = load_json(ROOT / "research/continuous-recovery-20261021/publication/root-control02-source-acceptance.json")
    latest_report = load_json(ROOT / "research/continuous-recovery-20261021/network/control02/runtime/control-report.json")
    if not latest_acceptance.get("accepted") or latest_acceptance.get("control_positive") is not False or latest_acceptance.get("stop_reason") != "endpoint_status_429":
        raise RuntimeError("latest historical acceptance is not the expected 429 stop")
    if latest_acceptance.get("historical_failure_tail_reset") is not False:
        raise RuntimeError("historical control02 acceptance unexpectedly reset the failure tail")
    if latest_report.get("network_requests") != 2 or latest_report.get("records", [{}])[-1].get("http_status") != 429:
        raise RuntimeError("latest private report is not the expected direct-timeout/proxy-429 result")

    old_plan = load_json(ROOT / "research/continuous-recovery-20261021/network/control02/plan.json")
    old_selection = load_json(ROOT / "research/continuous-recovery-20261021/network/control02/source-selection.json")
    if old_plan.get("known_positive", {}).get("length") != "9971" or old_selection.get("reuse_binding", {}).get("known_positive", {}).get("length") != "9971":
        raise RuntimeError("expected historical 9971 conflation not found; review the correction before proceeding")

    require_disk("offline validation")
    if require_runtime_absent and RUNTIME.exists():
        raise RuntimeError("runtime exists; refusing to overwrite or rerun this single-use package")
    return {"plan": plan, "selection": selection, "bindings": bindings}


def simulate_sequence(outcomes: list[dict[str, Any]], inherited_streak: int = 0) -> tuple[int, str, int]:
    attempts = 0
    stop = "attempt_limit"
    streak = inherited_streak
    prior_classification: str | None = None
    for outcome in outcomes:
        if attempts >= MAX_HTTP_ATTEMPTS:
            break
        if attempts == 0 and outcome.get("transport") != "direct":
            break
        if attempts > 0 and not should_try_proxy(transport="direct", classification=prior_classification or ""):
            break
        attempts += 1
        classification = outcome["classification"]
        status = outcome.get("status")
        if status in STOP_STATUSES:
            stop = f"endpoint_status_{status}"
            return attempts, stop, 0
        if classification == "transport_failure":
            streak += 1
            if streak >= MAX_CONSECUTIVE_TRANSPORT_FAILURES:
                stop = "five_consecutive_transport_failures"
                break
            prior_classification = classification
            stop = "transport_failure_attempt_cap" if attempts >= MAX_HTTP_ATTEMPTS else "transport_failure"
            continue
        streak = 0
        if classification == "positive":
            stop = "known_exact_cdx_row"
            break
        stop = f"http_{status}_without_positive" if status is not None else "nontransport_stop"
        break
    return attempts, stop, streak


def run_transport_stubs(fixture: dict[str, Any]) -> dict[str, bool]:
    """Exercise the real attempt writer/response parser with in-memory stubs."""

    class FakeSocket:
        def settimeout(self, _timeout: float) -> None:
            return None

    class FakeResponse:
        def __init__(self, status: int, headers: list[tuple[str, str]], body: bytes):
            self.status = status
            self.reason = "fixture"
            self._headers = headers
            self._body = body
            self.read_calls = 0

        def getheaders(self) -> list[tuple[str, str]]:
            return list(self._headers)

        def getheader(self, name: str) -> str | None:
            return next((value for key, value in self._headers if key.lower() == name.lower()), None)

        def read1(self, amount: int) -> bytes:
            self.read_calls += 1
            if not self._body:
                return b""
            value = self._body[:amount]
            self._body = self._body[amount:]
            return value

    class FakeConnection:
        def __init__(self, response: FakeResponse | None = None, fail_connect: bool = False):
            self.sock = FakeSocket()
            self.response = response
            self.fail_connect = fail_connect
            self.request_call: tuple[Any, ...] | None = None

        def connect(self) -> None:
            if self.fail_connect:
                raise OSError("fixture transport failure")

        def request(self, *args: Any, **kwargs: Any) -> None:
            self.request_call = (args, kwargs)

        def getresponse(self) -> FakeResponse:
            assert self.response is not None
            return self.response

        def close(self) -> None:
            return None

    positive_body = json.dumps(fixture["positive_response"], separators=(",", ":")).encode("utf-8")
    http_429 = FakeResponse(429, [("Retry-After", "120"), ("Set-Cookie", "session=fixture-only; Path=/")], b"429-body-not-read")
    http_200 = FakeResponse(200, [("Content-Type", "application/json"), ("Content-Length", str(len(positive_body)))], positive_body)
    responses = {False: http_429}
    fake_429 = FakeConnection(response=http_429)
    fake_200 = FakeConnection(response=http_200)
    fake_timeout = FakeConnection(fail_connect=True)
    temp_directory = tempfile.TemporaryDirectory(prefix="wayback-control03-offline-stub-", dir=PREP)
    temp_raw = Path(temp_directory.name) / "private" / "raw"
    temp_raw.mkdir(parents=True)
    old_raw = RAW
    old_make_connection = make_connection
    results: dict[str, bool] = {}
    try:
        globals()["RAW"] = temp_raw
        globals()["make_connection"] = lambda use_proxy, timeout: fake_429 if not use_proxy else fake_200
        first = perform_attempt(1, False, body_cap=ENTITY_BODY_CAP, child_deadline=time.monotonic() + 30)
        cookie_file = temp_raw / "request-1.cookies.json"
        results["actual_attempt_429_stops_body_read_and_keeps_set_cookie_private"] = (
            first["classification"] == "endpoint_stop" and http_429.read_calls == 0 and "session=fixture-only" in cookie_file.read_text(encoding="utf-8")
        )
        globals()["make_connection"] = lambda use_proxy, timeout: fake_200
        second = perform_attempt(2, True, body_cap=ENTITY_BODY_CAP, child_deadline=time.monotonic() + 30)
        results["actual_attempt_parser_accepts_exact_positive_row"] = second["classification"] == "known_exact_cdx_row" and second["positive_known_row"]
        results["actual_attempt_uses_frozen_target_and_never_sends_cookie"] = (
            fake_200.request_call is not None
            and fake_200.request_call[0][0] == "GET"
            and fake_200.request_call[0][1] == request_path()
            and fake_200.request_call[1]["headers"].get("Host") == "web.archive.org"
            and "Cookie" not in fake_200.request_call[1]["headers"]
        )
        globals()["make_connection"] = lambda use_proxy, timeout: fake_timeout
        failed = perform_attempt(1, False, body_cap=ENTITY_BODY_CAP, child_deadline=time.monotonic() + 30)
        results["actual_attempt_connection_error_is_transport_failure"] = failed["classification"] == "transport_failure" and failed["http_status"] is None
    finally:
        globals()["RAW"] = old_raw
        globals()["make_connection"] = old_make_connection
        temp_directory.cleanup()
    return results


def fixture_mode() -> int:
    values = validate_static_inputs()
    fixture = load_json(FIXTURE)
    positive = parse_cdx(json.dumps(fixture["positive_response"], separators=(",", ":")).encode())
    payload_length_error = parse_cdx(json.dumps(fixture["payload_length_misused_as_cdx_length_response"], separators=(",", ":")).encode())
    wrong_digest = parse_cdx(json.dumps(fixture["wrong_digest_response"], separators=(",", ":")).encode())
    wrong_original = parse_cdx(json.dumps(fixture["wrong_original_response"], separators=(",", ":")).encode())
    incomplete = parse_cdx(json.dumps(fixture["incomplete_response_with_resume_key"], separators=(",", ":")).encode())
    default_tls = ssl.create_default_context()

    sequences = {}
    for item in fixture["attempt_sequences"]:
        count, stop, streak_end = simulate_sequence(item["outcomes"], item.get("inherited_transport_failure_streak", 0))
        sequences[item["id"]] = {"attempts": count, "stop": stop, "transport_failure_streak_end": streak_end, "expected_attempts": item["expected_attempts"], "expected_stop": item["expected_stop"]}
    stub_cases = run_transport_stubs(fixture)

    cooldown_results = []
    cooldown_passed = True
    for item in fixture["cooldown_cases"]:
        finished = parse_utc(item["finished_utc"])
        stop = cooldown_not_before(item["status"], item["retry_after"], finished=finished)
        expected = parse_utc(item["minimum_not_before_utc"])
        passed = stop is not None and stop >= expected
        cooldown_passed = cooldown_passed and passed
        cooldown_results.append({"status": item["status"], "passed": passed, "not_before_utc": utc_text(stop) if stop else None})

    tests = {
        "exact_query_matches_frozen_source_selection": QUERY_URL == values["plan"]["exact_target"]["query_url"],
        "historical_positive_row_requires_cdx_length_10259": positive_row_matches(positive),
        "9971_payload_length_is_rejected_as_cdx_length": not positive_row_matches(payload_length_error),
        "wrong_digest_is_rejected": not positive_row_matches(wrong_digest),
        "wrong_original_and_https_neighbor_are_rejected": not positive_row_matches(wrong_original),
        "resume_key_makes_response_incomplete": incomplete["valid"] and not incomplete["complete"] and not positive_row_matches(incomplete),
        "direct_failure_then_proxy_positive_is_two_attempts": sequences["direct_transport_failure_then_proxy_positive"]["attempts"] == 2 and sequences["direct_transport_failure_then_proxy_positive"]["stop"] == "known_exact_cdx_row",
        "429_stops_without_proxy": sequences["direct_429_stops_without_proxy"]["attempts"] == 1 and sequences["direct_429_stops_without_proxy"]["stop"] == "endpoint_status_429",
        "other_http_response_stops_without_proxy": sequences["direct_http_500_stops_without_proxy"]["attempts"] == 1 and sequences["direct_http_500_stops_without_proxy"]["stop"] == "http_500_without_positive",
        "transport_failures_stop_at_two_attempt_cap": sequences["two_transport_failures_stop_at_attempt_cap"]["attempts"] == 2 and sequences["two_transport_failures_stop_at_attempt_cap"]["stop"] == "transport_failure_attempt_cap",
        "inherited_failure_tail_can_trigger_five_failure_stop": sequences["inherited_streak_reaches_five_on_first_attempt"]["attempts"] == 1 and sequences["inherited_streak_reaches_five_on_first_attempt"]["stop"] == "five_consecutive_transport_failures",
        "429_503_cooldown_uses_minimum_or_retry_after": cooldown_passed,
        "five_transport_failure_cooldown_is_at_least_120_seconds": transport_failure_cooldown(5, finished=parse_utc("2026-10-22T00:00:00Z")) == parse_utc("2026-10-22T00:02:00Z"),
        "default_tls_context_verifies_certificates": default_tls.verify_mode == ssl.CERT_REQUIRED and default_tls.check_hostname,
        "limits_and_cadence_are_bounded": MAX_HTTP_ATTEMPTS == 2 and MAX_LOGICAL_REQUESTS == 1 and CHILD_SECONDS == 90 and DISPATCH_SPACING_SECONDS >= MIN_REQUEST_START_SECONDS >= 5,
        "only_transport_failure_allows_proxy": should_try_proxy(transport="direct", classification="transport_failure") and not should_try_proxy(transport="direct", classification="http_response_without_positive_row"),
        "raw_http_and_cookie_material_is_private": "private/raw" in values["plan"]["runtime_paths"]["private_raw_directory"] and values["plan"]["policy"]["raw_body_headers_cookies_stderr_private"],
        "historical_failure_tail_is_not_reset": values["plan"]["policy"]["failure_tail_reset_by_runner"] is False and values["plan"]["history"]["previous_failure_tail_preserved"] is True,
        "no_redirect_retry_pagination_or_image_replay": values["plan"]["policy"]["no_redirects"] and values["plan"]["policy"]["no_automatic_retries"] and values["plan"]["policy"]["no_pagination"] and values["plan"]["policy"]["no_image_replay"],
        "D_disk_floor_and_empty_runtime": disk_free() >= DISK_FLOOR and not RUNTIME.exists(),
        "fixture_is_offline_only": fixture.get("network_requests") == 0 and fixture.get("raw_written") is False,
        **stub_cases,
    }
    result = {
        "schema": "wow-recovery-wayback-positive-control03-offline-validation.v1",
        "batch_id": values["plan"]["batch_id"],
        "checked_utc": utc_text(),
        "network_requests": 0,
        "raw_written": False,
        "temporary_stub_raw_written": True,
        "temporary_stub_raw_retained": False,
        "network_sockets_opened": 0,
        "all_passed": all(tests.values()),
        "test_count": len(tests),
        "cases": tests,
        "simulated_sequences": sequences,
        "stub_transport_cases": stub_cases,
        "cooldown_cases": cooldown_results,
        "disk_free_bytes": disk_free(),
        "disk_floor_bytes": DISK_FLOOR,
        "scope": "Offline validation only; no Wayback request was made.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["all_passed"] else 1


def go_hashes() -> dict[str, str]:
    return {
        "plan_sha256": sha256_file(PLAN),
        "runner_sha256": sha256_file(RUNNER),
        "fixture_sha256": sha256_file(FIXTURE),
        "input_bindings_sha256": sha256_file(INPUT_BINDINGS),
        "source_selection_sha256": sha256_file(SOURCE_SELECTION),
        "offline_validation_sha256": sha256_file(OFFLINE_VALIDATION),
        "latest_failure_acceptance_sha256": sha256_file(ROOT / "research/continuous-recovery-20261021/publication/root-control02-source-acceptance.json"),
        "latest_failure_report_sha256": sha256_file(ROOT / "research/continuous-recovery-20261021/network/control02/runtime/control-report.json"),
        "prior_failure_acceptance_sha256": sha256_file(ROOT / "research/continuous-recovery-20261021/publication/root-control01-source-acceptance.json"),
        "prior_failure_report_sha256": sha256_file(ROOT / "research/continuous-recovery-20261021/network/runtime/control-report.json"),
    }


def validate_go(go_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    static = validate_static_inputs()
    if not OFFLINE_VALIDATION.is_file():
        raise RuntimeError("offline-validation.json is missing")
    offline = load_json(OFFLINE_VALIDATION)
    if (
        offline.get("all_passed") is not True
        or offline.get("network_requests") != 0
        or offline.get("raw_written") is not False
        or offline.get("temporary_stub_raw_written") is not True
        or offline.get("temporary_stub_raw_retained") is not False
        or offline.get("network_sockets_opened") != 0
    ):
        raise RuntimeError("offline validation receipt is not a passing offline result")
    expected_go = GO_PATH.resolve()
    supplied_go = go_path.resolve()
    if supplied_go != expected_go:
        raise RuntimeError(f"GO must be at fixed path: {relative_path(expected_go)}")
    go = load_json(supplied_go)
    required_true = {
        "accepted": True,
        "root_go": True,
        "network_authorized": True,
        "historical_failure_tail_retained": True,
        "no_image_replay": True,
        "direct_first": True,
        "tls_verification": True,
        "no_automatic_retries": True,
        "no_redirects": True,
        "no_pagination": True,
    }
    for field, expected in required_true.items():
        if go.get(field) is not expected:
            raise RuntimeError(f"root GO missing required true field: {field}")
    for field, expected in go_hashes().items():
        if go.get(field) != expected:
            raise RuntimeError(f"root GO hash mismatch: {field}")
    if (
        go.get("maximum_logical_requests") != MAX_LOGICAL_REQUESTS
        or go.get("maximum_http_attempts") != MAX_HTTP_ATTEMPTS
        or go.get("parent_watchdog_seconds") != PARENT_WATCHDOG_SECONDS
        or go.get("maximum_seconds_child") != CHILD_SECONDS
        or go.get("maximum_body_bytes") != TOTAL_BODY_CAP
        or go.get("cdx_record_length") != KNOWN_CDX_LENGTH
        or go.get("mime") != KNOWN_MIME
        or go.get("digest") != KNOWN_DIGEST
    ):
        raise RuntimeError("root GO attempt/watchdog bounds mismatch")
    inherited_streak = go.get("inherited_transport_failure_streak")
    if not isinstance(inherited_streak, int) or inherited_streak < 0 or inherited_streak >= MAX_CONSECUTIVE_TRANSPORT_FAILURES:
        raise RuntimeError("root GO must confirm an inherited transport-failure streak from 0 through 4")
    if go.get("free_bytes_before", 0) < DISK_FLOOR:
        raise RuntimeError("root GO disk-free evidence is below floor")
    times = {name: parse_utc(go[name]) for name in ("authorized_at_utc", "not_before_utc", "expires_utc")}
    if times["not_before_utc"] < times["authorized_at_utc"] or times["expires_utc"] <= times["not_before_utc"]:
        raise RuntimeError("root GO time bounds are invalid")
    if times["expires_utc"] > USER_AUTH_WINDOW_END:
        raise RuntimeError("root GO exceeds the user-authorized 2026-10-22 14:51:33 UTC window")
    if utc_now() < times["not_before_utc"] or utc_now() >= times["expires_utc"]:
        raise RuntimeError("current time is outside the fresh root GO window")
    latest_cooldown = parse_utc("2026-10-21T12:13:48.894609Z")
    if times["not_before_utc"] < latest_cooldown:
        raise RuntimeError("root GO not-before precedes the latest historical cooldown")
    if RUNTIME.exists():
        raise RuntimeError("runtime exists; this package and GO are single-use")
    require_disk("after GO validation")
    return go, static["plan"]


def make_connection(use_proxy: bool, timeout: float) -> http.client.HTTPConnection:
    parsed = urlsplit(ENDPOINT)
    if parsed.scheme != "https" or parsed.hostname is None:
        raise RuntimeError("frozen endpoint must be HTTPS")
    context = ssl.create_default_context()
    if not use_proxy:
        connection = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, timeout=timeout, context=context)
        return connection

    proxy_parts = urlsplit(PROXY)
    if proxy_parts.scheme != "http" or proxy_parts.hostname != "127.0.0.1" or proxy_parts.port != 7890:
        raise RuntimeError("frozen proxy identity mismatch")
    connection = http.client.HTTPConnection(proxy_parts.hostname, proxy_parts.port, timeout=timeout)
    connection.set_tunnel(parsed.hostname, parsed.port or 443, headers={"Host": parsed.hostname})
    raw_connect = connection.connect

    def connect_proxy_tunnel() -> None:
        raw_connect()
        if connection.sock is None:
            raise OSError("proxy tunnel socket missing")
        connection.sock = context.wrap_socket(connection.sock, server_hostname=parsed.hostname)

    connection.connect = connect_proxy_tunnel  # type: ignore[method-assign]
    return connection


def raw_header_text(status: int | None, reason: str | None, headers: list[tuple[str, str]]) -> bytes:
    if status is None:
        return b""
    lines = [f"HTTP response status {status} {reason or ''}\r\n"]
    lines.extend(f"{name}: {value}\r\n" for name, value in headers)
    return ("".join(lines) + "\r\n").encode("iso-8859-1", errors="replace")


def request_path() -> str:
    parts = urlsplit(QUERY_URL)
    return parts.path + "?" + parts.query


def private_request_text(use_proxy: bool) -> bytes:
    lines = [
        f"GET {request_path()} HTTP/1.1",
        "Host: web.archive.org",
        "User-Agent: WOWEncyclopedia-recovery-control/1.0",
        "Accept: application/json",
        "Connection: close",
    ]
    if use_proxy:
        lines.append("Proxy route: process-local HTTP CONNECT through 127.0.0.1:7890")
    else:
        lines.append("Proxy route: direct, proxy bypassed")
    lines.append("Outbound Cookie header: absent")
    return ("\r\n".join(lines) + "\r\n\r\n").encode("utf-8")


def read_response_body(response: http.client.HTTPResponse, connection: http.client.HTTPConnection, *, deadline: float, cap: int) -> tuple[bytes, bool]:
    body = bytearray()
    content_length = response.getheader("Content-Length")
    if content_length and content_length.isdigit() and int(content_length) > cap:
        return b"", True
    while len(body) < cap:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("request deadline exceeded while reading body")
        if connection.sock is not None:
            connection.sock.settimeout(max(0.1, min(float(CONNECT_SECONDS), remaining)))
        try:
            chunk = response.read1(min(65536, cap - len(body)))
        except (socket.timeout, TimeoutError, ssl.SSLError, OSError, http.client.HTTPException) as exc:
            raise IncompleteBodyRead(type(exc).__name__, bytes(body)) from exc
        if not chunk:
            return bytes(body), False
        body.extend(chunk)
    # Reaching the configured byte cap is an inconclusive bounded stop; no
    # extra byte is fetched to test whether EOF follows.
    return bytes(body), True


def perform_attempt(number: int, use_proxy: bool, *, body_cap: int, child_deadline: float) -> dict[str, Any]:
    transport = "proxy" if use_proxy else "direct"
    request_started = utc_now()
    started_mono = time.monotonic()
    remaining = min(float(REQUEST_SECONDS), child_deadline - started_mono)
    result: dict[str, Any] = {
        "request_number": number,
        "transport": transport,
        "request_started_utc": utc_text(request_started),
        "request_finished_utc": None,
        "http_status": None,
        "classification": None,
        "transport_error_class": None,
        "body_cap_reached": False,
        "body_bytes": 0,
        "body_sha256": hashlib.sha256(b"").hexdigest(),
        "cdx_json_valid": False,
        "cdx_complete": False,
        "cdx_rows": 0,
        "resume_keys": [],
        "positive_known_row": False,
        "retry_after": None,
        "redirect_response": False,
        "redirect_chain": [],
        "request_cookie_header_present": False,
    }
    body_data = b""
    response_headers: list[tuple[str, str]] = []
    request_private = private_request_text(use_proxy)
    connection: http.client.HTTPConnection | None = None
    transfer_error = False
    if remaining <= 0:
        result["transport_error_class"] = "child_deadline_before_request"
        result["classification"] = "transport_failure"
        result["request_finished_utc"] = utc_text()
        return result
    try:
        connection = make_connection(use_proxy, min(float(CONNECT_SECONDS), remaining))
        connection.connect()
        if connection.sock is not None:
            connection.sock.settimeout(max(0.1, min(float(CONNECT_SECONDS), child_deadline - time.monotonic())))
        parts = urlsplit(QUERY_URL)
        connection.request(
            "GET",
            request_path(),
            headers={
                "Host": parts.hostname or "web.archive.org",
                "User-Agent": "WOWEncyclopedia-recovery-control/1.0",
                "Accept": "application/json",
                "Connection": "close",
            },
        )
        deadline = min(child_deadline, started_mono + REQUEST_SECONDS)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("request deadline exceeded before response headers")
        if connection.sock is not None:
            connection.sock.settimeout(max(0.1, min(float(CONNECT_SECONDS), remaining)))
        response = connection.getresponse()
        result["http_status"] = response.status
        response_headers = response.getheaders()
        result["redirect_response"] = 300 <= response.status < 400
        result["retry_after"] = next((value for name, value in response_headers if name.lower() == RETRY_AFTER_HEADER), None)
        if response.status not in STOP_STATUSES:
            body_data, body_cap_reached = read_response_body(response, connection, deadline=deadline, cap=body_cap)
            result["body_cap_reached"] = body_cap_reached
    except IncompleteBodyRead as exc:
        transfer_error = True
        result["transport_error_class"] = exc.cause_name
        body_data = exc.partial
    except (socket.timeout, TimeoutError, ssl.SSLError, OSError, http.client.HTTPException) as exc:
        transfer_error = True
        result["transport_error_class"] = type(exc).__name__
        partial = getattr(exc, "partial", b"")
        if isinstance(partial, bytes) and len(partial) <= body_cap:
            body_data += partial
    except Exception as exc:
        transfer_error = True
        result["transport_error_class"] = type(exc).__name__
    finally:
        if connection is not None:
            try:
                connection.close()
            except OSError:
                pass
    result["request_finished_utc"] = utc_text()
    result["body_bytes"] = len(body_data)
    result["body_sha256"] = hashlib.sha256(body_data).hexdigest()
    result["transfer_error"] = transfer_error
    parsed = parse_cdx(body_data) if result["http_status"] == 200 and body_data and not result["body_cap_reached"] else {"valid": False, "complete": False, "rows": [], "resume_keys": []}
    positive = result["http_status"] == 200 and positive_row_matches(parsed)
    result["cdx_json_valid"] = bool(parsed.get("valid"))
    result["cdx_complete"] = bool(parsed.get("complete"))
    result["cdx_rows"] = len(parsed.get("rows", []))
    result["resume_keys"] = parsed.get("resume_keys", [])
    result["positive_known_row"] = positive
    result["classification"] = attempt_classification(
        status=result["http_status"], positive=positive, transfer_error=transfer_error, body_cap=result["body_cap_reached"]
    )

    headers_data = raw_header_text(result["http_status"], None, response_headers)
    cookie_record = {
        "outbound_cookie_header_present": False,
        "response_set_cookie_headers": [value for name, value in response_headers if name.lower() == "set-cookie"],
    }
    private_files = {
        "request": RAW / f"request-{number}.request.txt",
        "headers": RAW / f"request-{number}.headers.txt",
        "cookies": RAW / f"request-{number}.cookies.json",
        "body": RAW / f"request-{number}.body",
        "stderr": RAW / f"request-{number}.stderr.txt",
    }
    stderr_data = (result["transport_error_class"] or "").encode("utf-8")
    for path, data in (
        (private_files["request"], request_private),
        (private_files["headers"], headers_data),
        (private_files["cookies"], json.dumps(cookie_record, ensure_ascii=False, indent=2).encode("utf-8")),
        (private_files["body"], body_data),
        (private_files["stderr"], stderr_data),
    ):
        require_disk(f"before private raw write {path.name}")
        path.write_bytes(data)
        require_disk(f"after private raw write {path.name}")
    result["private_raw_paths"] = {name: relative_path(path) for name, path in private_files.items()}
    result["private_raw_sha256"] = {name: sha256_file(path) for name, path in private_files.items()}
    result["disk_free_after_bytes"] = disk_free()
    return result


def enforce_request_spacing(previous_start: float | None) -> None:
    if previous_start is None:
        return
    target = previous_start + DISPATCH_SPACING_SECONDS
    while True:
        remaining = target - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 0.1))


def execute(go_path: Path) -> int:
    go, plan = validate_go(go_path)
    require_disk("before runtime directory creation")
    RUNTIME.mkdir(parents=True, exist_ok=False)
    RAW.mkdir(parents=True, exist_ok=False)
    batch_started = utc_now()
    batch_start_mono = time.monotonic()
    child_deadline = batch_start_mono + CHILD_SECONDS
    records: list[dict[str, Any]] = []
    total_body = 0
    transport_failures = 0
    transport_failure_streak_start = int(go["inherited_transport_failure_streak"])
    transport_failure_streak = transport_failure_streak_start
    stop_reason = "no_positive_row"
    cooldown: datetime | None = None
    previous_start: float | None = None
    disk_free_before = require_disk("before first request")
    for number, use_proxy in enumerate((False, True), start=1):
        if number > MAX_HTTP_ATTEMPTS or len(records) >= MAX_HTTP_ATTEMPTS:
            stop_reason = "attempt_cap"
            break
        if number == 2 and not records:
            stop_reason = "missing_direct_attempt"
            break
        if number == 2 and not should_try_proxy(transport="direct", classification=records[-1]["classification"]):
            stop_reason = "proxy_not_allowed_after_nontransport_result"
            break
        enforce_request_spacing(previous_start)
        # Recompute every budget after waiting; do not reuse a pre-wait value.
        now_mono = time.monotonic()
        remaining_seconds = child_deadline - now_mono
        if remaining_seconds <= REQUEST_SECONDS + 1:
            stop_reason = "child_budget_after_wait"
            break
        now_utc = utc_now()
        if now_utc >= parse_utc(go["expires_utc"]):
            stop_reason = "go_expired_before_request"
            break
        disk_before = require_disk(f"before request {number}")
        previous_start = time.monotonic()
        remaining_body = TOTAL_BODY_CAP - total_body
        if remaining_body <= 0:
            stop_reason = "total_body_cap_reached"
            break
        record = perform_attempt(number, use_proxy, body_cap=min(ENTITY_BODY_CAP, remaining_body), child_deadline=child_deadline)
        record["disk_free_before_bytes"] = disk_before
        records.append(record)
        total_body += int(record["body_bytes"])
        require_disk(f"after request {number}")
        if total_body > TOTAL_BODY_CAP:
            stop_reason = "total_body_cap_exceeded"
            break
        status = record["http_status"]
        if status in STOP_STATUSES:
            finished = parse_utc(record["request_finished_utc"])
            cooldown = cooldown_not_before(status, record.get("retry_after"), finished=finished)
            transport_failure_streak = 0
            stop_reason = f"endpoint_status_{status}"
            break
        if record["body_cap_reached"]:
            stop_reason = "entity_body_cap_reached"
            break
        if record["classification"] == "known_exact_cdx_row":
            transport_failure_streak = 0
            stop_reason = "known_exact_cdx_row"
            break
        if record["classification"] == "transport_failure":
            transport_failures += 1
            transport_failure_streak += 1
            if transport_failure_streak >= MAX_CONSECUTIVE_TRANSPORT_FAILURES:
                stop_reason = "five_consecutive_transport_failures"
                cooldown = transport_failure_cooldown(transport_failure_streak, finished=parse_utc(record["request_finished_utc"]))
                break
            if number >= MAX_HTTP_ATTEMPTS:
                stop_reason = "transport_failure_attempt_cap"
                break
            continue
        transport_failure_streak = 0
        stop_reason = f"http_{status}_without_positive" if status is not None else "transport_failure_attempt_cap"
        break

    actual_starts = [parse_utc(item["request_started_utc"]) for item in records]
    start_deltas = [(actual_starts[i] - actual_starts[i - 1]).total_seconds() for i in range(1, len(actual_starts))]
    spacing_passed = all(delta >= MIN_REQUEST_START_SECONDS for delta in start_deltas)
    if not spacing_passed:
        stop_reason = "request_spacing_acceptance_failed"
    require_disk("before sanitized report write")
    report = {
        "schema": "wow-recovery-wayback-positive-control03-execution-report.v1",
        "batch_id": plan["batch_id"],
        "started_utc": utc_text(batch_started),
        "finished_utc": utc_text(),
        "network_requests": len(records),
        "logical_requests": 1 if records else 0,
        "attempts": records,
        "total_body_bytes": total_body,
        "transport_failures_this_run": transport_failures,
        "transport_failure_streak_start": transport_failure_streak_start,
        "transport_failure_streak_end": transport_failure_streak,
        "stop_statuses": sorted(STOP_STATUSES),
        "stop_reason": stop_reason,
        "control_positive": any(item["positive_known_row"] for item in records),
        "positive_identity": {
            "timestamp": KNOWN_TIMESTAMP,
            "original": ORIGINAL,
            "mimetype": KNOWN_MIME,
            "statuscode": KNOWN_STATUS,
            "digest": KNOWN_DIGEST,
            "cdx_record_length": KNOWN_CDX_LENGTH,
        },
        "separate_payload_reference_only": {"bytes": PAYLOAD_BYTES, "sha256": PAYLOAD_SHA256, "mime": KNOWN_MIME, "replayed": False},
        "request_start_deltas_seconds": start_deltas,
        "minimum_request_start_interval_seconds": MIN_REQUEST_START_SECONDS,
        "dispatch_spacing_seconds": DISPATCH_SPACING_SECONDS,
        "request_spacing_passed": spacing_passed,
        "maximum_attempts": MAX_HTTP_ATTEMPTS,
        "direct_attempts": sum(item["transport"] == "direct" for item in records),
        "proxy_attempts": sum(item["transport"] == "proxy" for item in records),
        "proxy_used_only_after_transport_failure": all(
            item["transport"] != "proxy" or (index > 0 and records[index - 1]["classification"] == "transport_failure")
            for index, item in enumerate(records)
        ),
        "redirects_followed": 0,
        "pagination_used": False,
        "image_payload_replays": 0,
        "tls_verification": True,
        "raw_http_cookie_material_public": False,
        "historical_failure_tail_reset": False,
        "historical_failure_tail_prior_acceptance": plan["history"]["latest_failure_acceptance_path"],
        "historical_failure_tail_prior_acceptance_sha256": plan["history"]["latest_failure_acceptance_sha256"],
        "historical_failure_tail_prior_report": plan["history"]["latest_failure_private_report_path"],
        "historical_failure_tail_prior_report_sha256": plan["history"]["latest_failure_private_report_sha256"],
        "cooldown_not_before_utc": utc_text(cooldown) if cooldown else None,
        "disk_free_before_bytes": disk_free_before,
        "disk_free_after_bytes": disk_free(),
        "go_path": relative_path(GO_PATH),
        "go_sha256": sha256_file(GO_PATH),
        "raw_attempts_private_directory": relative_path(RAW),
    }
    require_disk("before report write")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    require_disk("after report write")
    print(json.dumps({
        "accepted": True,
        "batch_id": report["batch_id"],
        "network_requests": report["network_requests"],
        "control_positive": report["control_positive"],
        "stop_reason": report["stop_reason"],
        "direct_attempts": report["direct_attempts"],
        "proxy_attempts": report["proxy_attempts"],
        "total_body_bytes": report["total_body_bytes"],
        "cooldown_not_before_utc": report["cooldown_not_before_utc"],
        "disk_free_after_bytes": report["disk_free_after_bytes"],
        "sanitized_report_path": relative_path(REPORT),
        "raw_material_private": True,
        "historical_failure_tail_reset": False,
    }, ensure_ascii=False, indent=2))
    return 0 if report["control_positive"] and report["request_spacing_passed"] else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--fixture", action="store_true")
    modes.add_argument("--execute", action="store_true")
    parser.add_argument("--go", type=Path)
    args = parser.parse_args()
    if args.fixture:
        return fixture_mode()
    if not args.execute:
        plan = load_json(PLAN)
        print(json.dumps({
            "mode": "prepared_only",
            "batch_id": plan["batch_id"],
            "network_requests": 0,
            "fresh_root_go_required": True,
            "go_path": plan["root_go_path"],
            "offline_fixture_command": "python -X utf8 wayback_positive_control03.py --fixture",
        }, ensure_ascii=False, indent=2))
        return 0
    if args.go is None:
        raise SystemExit("--execute requires --go PATH")
    return execute(args.go)


if __name__ == "__main__":
    raise SystemExit(main())

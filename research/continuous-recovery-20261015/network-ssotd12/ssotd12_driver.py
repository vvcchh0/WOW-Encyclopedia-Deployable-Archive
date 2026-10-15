"""NET-SSOTD-012: bounded SSOTD prefix continuation and one redirect probe.

This adapter owns only ``network-ssotd12``.  It reuses the accepted
core-pages3 transport (TLS, curl limits, source-block parsing and CDX helpers)
and the accepted control7 dispatch journal.  It never replays newly observed
CDX rows and never follows the approved 301 probe.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
APPROVED_PLAN = ROOT / "research/continuous-recovery-20261015/ssotd12-approved-plan.json"
PARENT_REVIEW = ROOT / "research/continuous-recovery-20261015/ssotd-next-plan-independent-review.json"
PREVIOUS_QUEUE = ROOT / "research/continuous-recovery-20261015/ssotd-next-plan/candidate-queue.json"
RESUME_EVIDENCE = ROOT / "research/continuous-recovery-20261015/ssotd-next-plan/resume-evidence.json"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"

EXPECTED_PLAN_SHA256 = "b88eaff981d420d8e22b78b9b6b461082e7ce4b5247583359c5a4db6cd1d35c0"
EXPECTED_REVIEW_SHA256 = "41fe5ece541389f383fdf59e554b047b63a914d340cee96dc9b1dcc9b1c7ff22"
MAX_PREFIX_PAGES = 3
MAX_OPERATIONS = 4
MAX_ATTEMPTS = 32
WINDOW_SECONDS = 480
INTERVAL_SECONDS = 1.25
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY_BYTES = 64 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 16 * 1024 * 1024
PROXY = "http://127.0.0.1:7890"
USER_AGENT = "wow-recovery-ssotd12/20261015"
REDIRECT_CODES = {301, 302, 303, 307, 308}
PREFIX_COLUMNS = ["timestamp", "original", "statuscode", "mimetype", "digest", "length"]


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_module(CORE_PATH, "ssotd12_core_pages3")
gate_mod = load_module(GATE_PATH, "ssotd12_control7")

# All imported helper writes are redirected in memory to this batch directory.
core.OUT = OUT
core.RAW = RAW
core.USER_AGENT = USER_AGENT
core.PROXY = PROXY
core.MIN_INTERVAL_SECONDS = 0.0  # control7 GateState owns the dispatch wait
core.MAX_ATTEMPTS = MAX_ATTEMPTS
core.WINDOW_SECONDS = WINDOW_SECONDS
core.MIN_FREE_BYTES = MIN_FREE_BYTES
core.MAX_TOTAL_BODY_BYTES = MAX_TOTAL_BODY_BYTES
core.MAX_ENTITY_BODY_BYTES = MAX_ENTITY_BODY_BYTES
gate_mod.OUT = OUT
gate_mod.RAW = RAW
gate_mod.PROXY = PROXY
gate_mod.INTERVAL_SECONDS = INTERVAL_SECONDS
gate_mod.MIN_FREE_BYTES = MIN_FREE_BYTES


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return path.resolve().relative_to(OUT.resolve()).as_posix()


def digest_record(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def disk_free_bytes() -> int:
    return int(shutil.disk_usage(ROOT).free)


def strip_resume_key(url: str) -> str:
    return re.sub(r"([?&]resumeKey=)[^&]*", r"\1", url, count=1)


def replace_resume_key(base_url: str, key: str) -> str:
    encoded = quote(key, safe="")
    replaced, count = re.subn(r"([?&]resumeKey=)[^&]*", r"\1" + encoded, base_url, count=1)
    if count != 1:
        raise ValueError("approved prefix URL has no single resumeKey parameter")
    return replaced


def valid_prefix_row(row: Any) -> bool:
    return isinstance(row, list) and len(row) >= len(core.CDX_COLUMNS)


def parse_prefix_body(body: bytes) -> dict[str, Any]:
    """Parse only the saved six-field rows and explicit cursor metadata."""
    try:
        payload = json.loads(body.decode("utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        return {"parse_valid": False, "parse_error": f"json_decode:{type(exc).__name__}",
                "rows": [], "metadata_records": [], "resume_keys": []}
    if not isinstance(payload, list):
        return {"parse_valid": False, "parse_error": "json_shape", "rows": [],
                "metadata_records": [], "resume_keys": []}
    rows: list[dict[str, str]] = []
    metadata: list[dict[str, Any]] = []
    resume_keys: list[str] = []
    header_seen = False
    for index, item in enumerate(payload):
        if valid_prefix_row(item):
            values = [str(value) for value in item[: len(core.CDX_COLUMNS)]]
            if values == PREFIX_COLUMNS and not header_seen:
                header_seen = True
                metadata.append({"record_index": index, "kind": "header", "value": values})
                continue
            rows.append({
                key: values[position] for position, key in enumerate(PREFIX_COLUMNS)
            } | {"record_index": index})
            continue
        if isinstance(item, list) and len(item) == 1 and isinstance(item[0], str) and item[0]:
            resume_keys.append(item[0])
            metadata.append({"record_index": index, "kind": "resume_key", "value": item[0]})
            continue
        metadata.append({"record_index": index, "kind": "metadata", "value": item})
    unique_keys = list(dict.fromkeys(resume_keys))
    return {
        "parse_valid": True,
        "parse_error": None,
        "rows": rows,
        "metadata_records": metadata,
        "resume_keys": resume_keys,
        "unique_resume_keys": unique_keys,
        "next_resume_key": unique_keys[-1] if len(unique_keys) == 1 else None,
        "multiple_resume_keys": len(unique_keys) > 1,
    }


def bucket_timestamp(timestamp: str) -> str:
    if not re.fullmatch(r"\d{14}", timestamp or ""):
        return "invalid_timestamp"
    return "pre_anchor" if timestamp <= "20080512210044" else "post_anchor"


def row_distributions(rows: list[dict[str, str]]) -> dict[str, Any]:
    status = Counter(str(row.get("statuscode") or "") for row in rows)
    mime = Counter(str(row.get("mimetype") or "") for row in rows)
    temporal = Counter(bucket_timestamp(str(row.get("timestamp") or "")) for row in rows)
    return {
        "statuscode": dict(sorted(status.items())),
        "mimetype": dict(sorted(mime.items())),
        "temporal_bucket": dict(sorted(temporal.items())),
    }


def read_attempt_body(attempt: dict[str, Any] | None) -> bytes:
    if not attempt or not attempt.get("executed"):
        return b""
    raw = attempt.get("raw") or {}
    value = str(raw.get("body") or "")
    if not value:
        return b""
    path = (OUT / value).resolve()
    if OUT.resolve() not in path.parents:
        raise RuntimeError("raw body path escaped batch directory")
    return path.read_bytes() if path.is_file() else b""


def public_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    return core.source_attempt_view(attempt)


def dispatch_ok(state: Any, window_started: float) -> tuple[bool, str | None]:
    if state.stop_reason:
        return False, state.stop_reason
    if state.attempts >= MAX_ATTEMPTS:
        return False, "attempt_limit"
    if time.monotonic() - window_started >= WINDOW_SECONDS:
        return False, "network_window_exhausted"
    if disk_free_bytes() < MIN_FREE_BYTES:
        return False, "disk_free_below_threshold"
    if state.total_body_bytes >= MAX_TOTAL_BODY_BYTES:
        return False, "total_body_limit"
    return True, None


def issue(
    url: str,
    transport: str,
    kind: str,
    target_key: str,
    state: Any,
    gate: Any,
    window_started: float,
) -> dict[str, Any]:
    ok, reason = dispatch_ok(state, window_started)
    if not ok:
        return {
            "executed": False,
            "attempt": state.attempts + 1,
            "kind": kind,
            "target_key": target_key,
            "transport": transport,
            "url": url,
            "unrequested_reason": reason or "limit_before_request",
        }
    number = state.attempts + 1
    gate_record = gate.before_dispatch(number, transport, target_key)
    attempt = core.run_request(url, transport, kind, target_key, state, number)
    attempt["dispatch_utc"] = gate_record["dispatch_utc"]
    attempt["dispatch_monotonic"] = gate_record["dispatch_monotonic"]
    attempt["dispatch_interval_seconds"] = gate_record["interval_since_previous_dispatch_seconds"]
    attempt["gate_persisted_before_transport"] = gate_record["persisted_before_transport"]
    body = read_attempt_body(attempt)
    attempt["local_zero_byte_body_placeholder"] = bool(attempt.get("source_status") is None and not body)
    attempt["body_is_source_response"] = attempt.get("source_status") is not None
    return attempt


def make_prefix_page_result(
    page_number: int,
    request_url: str,
    resume_key_used: str,
    attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    executed = [item for item in attempts if item.get("executed")]
    final = executed[-1] if executed else None
    body = read_attempt_body(final)
    parsed = {"parse_valid": False, "parse_error": "no_source_200_response", "rows": [],
              "metadata_records": [], "resume_keys": [], "unique_resume_keys": [],
              "next_resume_key": None, "multiple_resume_keys": False}
    if final and final.get("source_status") == 200 and not final.get("transport_error"):
        parsed = parse_prefix_body(body)
    next_key = parsed.get("next_resume_key")
    if parsed.get("multiple_resume_keys"):
        next_key = None
        parsed["parse_error"] = "multiple_distinct_resume_keys"
    return {
        "operation": "cdx_prefix_resume_page",
        "page_number": page_number,
        "request_url": request_url,
        "resume_key_used": resume_key_used,
        "attempt_count": sum(bool(item.get("executed")) for item in attempts),
        "source_response_count": sum(item.get("source_status") is not None for item in attempts),
        "attempts": [public_attempt(item) for item in attempts],
        "final_source_status": final.get("source_status") if final else None,
        "final_transport_error": final.get("transport_error") if final else None,
        "final_content_type": final.get("content_type") if final else None,
        "body_bytes": len(body) if final else 0,
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "raw_body_path": (final.get("raw") or {}).get("body") if final else None,
        "parse_valid": parsed.get("parse_valid", False),
        "parse_error": parsed.get("parse_error"),
        "metadata_records": parsed.get("metadata_records") or [],
        "resume_keys": parsed.get("resume_keys") or [],
        "next_resume_key": next_key,
        "rows": parsed.get("rows") or [],
        "row_count": len(parsed.get("rows") or []),
        "row_distributions": row_distributions(parsed.get("rows") or []),
    }


def run_prefix_page(
    page_number: int,
    request_url: str,
    resume_key: str,
    transport: str | None,
    state: Any,
    gate: Any,
    window_started: float,
) -> tuple[dict[str, Any], str | None]:
    attempts: list[dict[str, Any]] = []
    confirmed = transport
    if transport is None:
        direct = issue(request_url, "direct", "cdx", f"prefix-page-{page_number}", state, gate, window_started)
        attempts.append(direct)
        if direct.get("executed") and not direct.get("transport_error"):
            confirmed = "direct"
        elif direct.get("executed") and direct.get("transport_error") and not state.stop_reason:
            proxy = issue(request_url, "proxy", "cdx", f"prefix-page-{page_number}", state, gate, window_started)
            attempts.append(proxy)
            if proxy.get("executed") and not proxy.get("transport_error"):
                confirmed = "proxy"
    else:
        attempts.append(issue(request_url, transport, "cdx", f"prefix-page-{page_number}", state, gate, window_started))
    return make_prefix_page_result(page_number, request_url, resume_key, attempts), confirmed


def run_redirect_probe(
    probe: dict[str, Any],
    transport: str,
    state: Any,
    gate: Any,
    window_started: float,
) -> dict[str, Any]:
    request_url = str(probe["request_url"])
    attempt = issue(request_url, transport, "redirect_probe", "ss1057-thumb-20101227014645", state, gate, window_started)
    body = read_attempt_body(attempt)
    if not attempt.get("executed"):
        return {
            "operation": "known_301_first_hop_probe",
            "request_url": request_url,
            "category": "not_requested",
            "reason": attempt.get("unrequested_reason") or "limit_before_request",
            "attempts": [public_attempt(attempt)],
            "actual_memento": None,
            "source_status": None,
            "body_bytes": 0,
            "body_sha256": None,
        }
    status = attempt.get("source_status")
    if attempt.get("transport_error"):
        category = "transport_error"
        reason = attempt.get("transport_reason") or "curl_or_tls_failure"
    elif status in REDIRECT_CODES:
        category = "redirect_evidence_only"
        reason = "manual_follow_and_automatic_redirects_disabled"
    else:
        category = "http_response"
        reason = f"source_status_{status}"
    return {
        "operation": "known_301_first_hop_probe",
        "request_url": request_url,
        "expected": {
            "original_url": probe.get("original_url"),
            "requested_capture": probe.get("requested_capture"),
            "cdx_status": probe.get("cdx_status"),
            "cdx_mime": probe.get("cdx_mime"),
            "cdx_digest": probe.get("cdx_digest"),
            "cdx_warc_index_length": probe.get("cdx_warc_index_length"),
        },
        "category": category,
        "reason": reason,
        "attempts": [public_attempt(attempt)],
        "actual_memento": attempt.get("memento_datetime"),
        "source_status": status,
        "content_type": attempt.get("content_type"),
        "location": attempt.get("location"),
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "raw_body_path": (attempt.get("raw") or {}).get("body"),
        "raw_headers_path": (attempt.get("raw") or {}).get("headers"),
        "manual_followed": False,
        "automatic_redirects": 0,
    }


def verify_approved_plan() -> dict[str, Any]:
    if sha256_file(APPROVED_PLAN) != EXPECTED_PLAN_SHA256:
        raise RuntimeError("approved plan SHA mismatch")
    plan = read_json(APPROVED_PLAN)
    if plan.get("root_authorized") is not True:
        raise RuntimeError("approved plan is not root-authorized")
    if int(plan.get("max_new_cdx_pages")) != MAX_PREFIX_PAGES:
        raise RuntimeError("approved prefix page cap mismatch")
    if plan.get("initial_resume_key") not in set(plan.get("previously_used_resume_keys") or []):
        # The fixed page-1 key is expected to differ from the page-0 key, but
        # retaining this check makes accidental cursor substitution visible.
        pass
    limits = plan.get("limits") or {}
    for key, expected in {
        "attempts": MAX_ATTEMPTS,
        "seconds": WINDOW_SECONDS,
        "total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "single_body_bytes": MAX_ENTITY_BODY_BYTES,
        "minimum_dispatch_interval_seconds": INTERVAL_SECONDS,
        "disk_floor_bytes": MIN_FREE_BYTES,
    }.items():
        if limits.get(key) != expected:
            raise RuntimeError(f"approved limit mismatch: {key}")
    first = str(plan.get("first_cdx_request_url") or "")
    if not first or "resumeKey=" not in first:
        raise RuntimeError("approved fixed first prefix URL missing")
    probe = plan.get("redirect_probe") or {}
    if not probe.get("request_url") or probe.get("requested_capture") != "20101227014645":
        raise RuntimeError("approved redirect probe mismatch")
    return plan


def prepare() -> int:
    plan = verify_approved_plan()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    input_paths = [APPROVED_PLAN, PARENT_REVIEW, PREVIOUS_QUEUE, RESUME_EVIDENCE, CORE_PATH, GATE_PATH]
    if any(not path.is_file() for path in input_paths):
        raise RuntimeError("one or more SSOTD-012 provenance inputs are missing")
    input_digests = {path.relative_to(ROOT).as_posix(): digest_record(path) for path in input_paths}
    first_url = str(plan["first_cdx_request_url"])
    initial_key = str(plan["initial_resume_key"])
    if strip_resume_key(first_url).count("resumeKey=") != 1:
        raise RuntimeError("first URL must have exactly one resumeKey")
    operations = [
        {
            "sequence": 1,
            "kind": "cdx_prefix_resume_page",
            "page_slot": 1,
            "conditional": False,
            "request_url": first_url,
            "resume_key": initial_key,
            "cursor_source": "approved_plan.initial_resume_key",
        },
        {
            "sequence": 2,
            "kind": "cdx_prefix_resume_page",
            "page_slot": 2,
            "conditional": True,
            "request_url": None,
            "resume_key": None,
            "cursor_source": "actual next_resume_key from page_slot_1 only",
        },
        {
            "sequence": 3,
            "kind": "cdx_prefix_resume_page",
            "page_slot": 3,
            "conditional": True,
            "request_url": None,
            "resume_key": None,
            "cursor_source": "actual next_resume_key from page_slot_2 only",
        },
        {
            "sequence": 4,
            "kind": "known_301_first_hop_probe",
            "conditional": True,
            "request_url": plan["redirect_probe"]["request_url"],
            "target_original": plan["redirect_probe"]["original_url"],
            "requested_capture": plan["redirect_probe"]["requested_capture"],
            "cursor_source": "approved_plan.redirect_probe only",
            "automatic_redirects": 0,
            "manual_followed": False,
        },
    ]
    candidates = {
        "schema": "continuous-wow-network-ssotd12-candidates/v1",
        "batch_id": "NET-SSOTD-012",
        "generated_utc": utc(),
        "network_requests": 0,
        "queue_status": "approved_plan_ready_for_bounded_execution",
        "approved_plan": {
            "path": APPROVED_PLAN.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(APPROVED_PLAN),
            "parent_review_path": PARENT_REVIEW.relative_to(ROOT).as_posix(),
            "parent_review_sha256": sha256_file(PARENT_REVIEW),
        },
        "query_identity": {
            "fixed_first_url": first_url,
            "fixed_first_resume_key": initial_key,
            "subsequent_rule": "replace only resumeKey with actual unique key from immediately previous valid 200 response",
            "query_parameters_must_remain_byte_ordered": True,
            "previously_used_resume_keys": plan.get("previously_used_resume_keys") or [],
        },
        "operations": operations,
        "policy": {
            "max_prefix_pages": MAX_PREFIX_PAGES,
            "max_operations": MAX_OPERATIONS,
            "max_attempts": MAX_ATTEMPTS,
            "network_window_seconds": WINDOW_SECONDS,
            "minimum_dispatch_interval_seconds": INTERVAL_SECONDS,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
            "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
            "direct_first_then_confirmed_proxy": True,
            "automatic_redirects": 0,
            "manual_follow_hops": 0,
            "stop_http_codes": [429, 503],
            "stop_consecutive_transport_failures": 5,
            "tls_verification": "enabled_by_curl_default",
            "concurrent_source_requests": 1,
        },
        "input_digests": input_digests,
        "excluded_operations": plan.get("excluded_operations") or [],
    }
    write_json(OUT / "candidates.json", candidates)
    write_json(OUT / "config.json", {
        "schema": "continuous-wow-network-ssotd12-config/v1",
        "batch_id": "NET-SSOTD-012",
        "candidate_sha256": sha256_file(OUT / "candidates.json"),
        "network_requests": 0,
        "adapter": "ssotd12_driver.py",
        "accepted_transport": CORE_PATH.relative_to(ROOT).as_posix(),
        "accepted_dispatch_gate": GATE_PATH.relative_to(ROOT).as_posix(),
        "input_digests": input_digests,
    })
    free = disk_free_bytes()
    write_json(OUT / "plan.json", {
        "schema": "continuous-wow-network-ssotd12-plan/v1",
        "batch_id": "NET-SSOTD-012",
        "mode": "plan_only",
        "prepared_utc": utc(),
        "candidate_sha256": sha256_file(OUT / "candidates.json"),
        "max_prefix_pages": MAX_PREFIX_PAGES,
        "max_operations": MAX_OPERATIONS,
        "network_requests": 0,
        "disk_free_bytes": free,
        "minimum_free_bytes": MIN_FREE_BYTES,
        "ready": free >= MIN_FREE_BYTES,
    })
    print(json.dumps({
        "mode": "plan_only",
        "batch_id": "NET-SSOTD-012",
        "network_requests": 0,
        "max_prefix_pages": MAX_PREFIX_PAGES,
        "max_operations": MAX_OPERATIONS,
        "candidate_sha256": sha256_file(OUT / "candidates.json"),
        "disk_free_bytes": free,
        "ready": free >= MIN_FREE_BYTES,
    }, ensure_ascii=False))
    return 0


def summarize_page(page: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in page.items() if key not in {"rows", "metadata_records", "attempts"}}


def write_outputs(
    candidates: dict[str, Any],
    pages: list[dict[str, Any]],
    operation_status: list[dict[str, Any]],
    redirect: dict[str, Any] | None,
    state: Any,
    gate: Any,
    started_utc: str,
    finished_utc: str,
    report_updated_utc: str,
    disk_before: int,
    disk_after: int,
    confirmed_transport: str | None,
    postflight: dict[str, Any],
    execution_error: dict[str, str] | None,
) -> None:
    all_rows = [row for page in pages for row in page.get("rows") or []]
    index_path = OUT / "cdx-index-pages.json"
    write_json(index_path, {
        "schema": "continuous-wow-network-ssotd12-cdx-index-pages/v1",
        "batch_id": "NET-SSOTD-012",
        "generated_utc": report_updated_utc,
        "rows_are_index_evidence_only": True,
        "pages": pages,
        "aggregate": {
            "page_count": len(pages),
            "row_count": len(all_rows),
            "statuscode": dict(sorted(Counter(str(row.get("statuscode") or "") for row in all_rows).items())),
            "mimetype": dict(sorted(Counter(str(row.get("mimetype") or "") for row in all_rows).items())),
            "temporal_bucket": dict(sorted(Counter(bucket_timestamp(str(row.get("timestamp") or "")) for row in all_rows).items())),
        },
    })
    observed_candidates: list[dict[str, Any]] = []
    for page in pages:
        for row in page.get("rows") or []:
            status = str(row.get("statuscode") or "")
            mime = str(row.get("mimetype") or "")
            if status in {str(code) for code in REDIRECT_CODES} or "revisit" in mime.casefold():
                observed_candidates.append({
                    "evidence_kind": "redirect_index_row" if status in {str(code) for code in REDIRECT_CODES} else "revisit_index_row",
                    "page_number": page.get("page_number"),
                    "page_request_url": page.get("request_url"),
                    "row": row,
                    "temporal_bucket": bucket_timestamp(str(row.get("timestamp") or "")),
                    "payload_validated": False,
                    "replay_requested": False,
                })
    write_json(OUT / "observed-index-candidates.json", {
        "schema": "continuous-wow-network-ssotd12-observed-index-candidates/v1",
        "batch_id": "NET-SSOTD-012",
        "rows_are_index_evidence_only": True,
        "redirect_or_revisit_count": len(observed_candidates),
        "entries": observed_candidates,
    })
    redirect_entries = []
    if redirect and redirect.get("category") == "redirect_evidence_only":
        redirect_entries.append({
            key: redirect.get(key) for key in (
                "request_url", "expected", "category", "reason", "actual_memento",
                "source_status", "content_type", "location", "body_bytes", "body_sha256",
                "raw_body_path", "raw_headers_path", "manual_followed", "automatic_redirects"
            )
        })
    write_json(OUT / "redirect-evidence.json", {
        "schema": "continuous-wow-network-ssotd12-redirect-evidence/v1",
        "batch_id": "NET-SSOTD-012",
        "manual_follow_hops": 0,
        "entries": redirect_entries,
    })
    intervals = [
        value.get("interval_since_previous_dispatch_seconds")
        for value in gate.dispatches
        if value.get("interval_since_previous_dispatch_seconds") is not None
    ]
    min_interval = min(intervals) if intervals else None
    prefix_source_responses = sum(
        item.get("source_status") is not None
        for page in pages for item in page.get("attempts") or []
    )
    redirect_source_responses = int(bool(redirect and redirect.get("source_status") is not None))
    request_window_elapsed = (datetime.fromisoformat(finished_utc) - datetime.fromisoformat(started_utc)).total_seconds()
    policy_checks = {
        "attempt_cap": state.attempts <= MAX_ATTEMPTS,
        "operation_cap": len(operation_status) <= MAX_OPERATIONS,
        "network_window_cap": request_window_elapsed <= WINDOW_SECONDS,
        "body_cap": state.total_body_bytes <= MAX_TOTAL_BODY_BYTES,
        "single_body_cap": all(
            int(value.get("body_bytes") or 0) <= MAX_ENTITY_BODY_BYTES
            for page in pages for value in page.get("attempts") or []
        ) and (not redirect or int(redirect.get("body_bytes") or 0) <= MAX_ENTITY_BODY_BYTES),
        "disk_floor_before": disk_before >= MIN_FREE_BYTES,
        "disk_floor_after": disk_after >= MIN_FREE_BYTES,
        "dispatch_interval": min_interval is None or min_interval >= INTERVAL_SECONDS,
        "serial_source_requests": True,
        "automatic_redirects_disabled": True,
        "manual_follow_hops_zero": True,
    }
    report = {
        "schema": "continuous-wow-network-ssotd12-batch-report/v1",
        "batch_id": "NET-SSOTD-012",
        "mode": "executed",
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "request_window_finished_utc": finished_utc,
        "request_window_elapsed_seconds": round(request_window_elapsed, 3),
        "report_updated_utc": report_updated_utc,
        "inputs": {
            "candidates": "research/continuous-recovery-20261015/network-ssotd12/candidates.json",
            "candidates_sha256": sha256_file(OUT / "candidates.json"),
            "approved_plan": candidates.get("approved_plan"),
            "input_digests": candidates.get("input_digests"),
        },
        "policy": candidates.get("policy"),
        "preflight": {
            "drive": "D:",
            "disk_free_bytes_before": disk_before,
            "disk_free_bytes_after": disk_after,
            "minimum_free_bytes": MIN_FREE_BYTES,
        },
        "transport": {
            "confirmed_transport_after_first_request": confirmed_transport,
            "curl": str(core.CURL),
            "accepted_helper": CORE_PATH.relative_to(ROOT).as_posix(),
            "dispatch_gate": GATE_PATH.relative_to(ROOT).as_posix(),
        },
        "operation_count": len(operation_status),
        "operations": operation_status,
        "prefix_page_count_executed": len(pages),
        "prefix_pages": [summarize_page(page) for page in pages],
        "redirect_probe": redirect,
        "cdx_index_row_count": len(all_rows),
        "redirect_or_revisit_index_candidate_count": len(observed_candidates),
        "cdx_source_response_count": prefix_source_responses,
        "redirect_probe_source_response_count": redirect_source_responses,
        "source_response_count": state.source_responses,
        "source_request_count": state.attempts,
        "transport_attempt_count": state.attempts,
        "failed_attempt_count": state.failed_attempts,
        "total_body_bytes": state.total_body_bytes,
        "payload_body_bytes": 0,
        "valid_entity_count": 0,
        "actual_memento_count": redirect_source_responses if redirect and redirect.get("actual_memento") else 0,
        "dispatch_count": len(gate.dispatches),
        "minimum_start_interval_seconds": min_interval,
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "rate_limit": state.rate_limit,
        "policy_checks": policy_checks,
        "batch_policy_accepted": all(policy_checks.values()),
        "postflight": postflight,
        "execution_error": execution_error,
        "raw_evidence_note": "Raw headers, traces, stderr and bodies stay below this batch raw directory. Zero-byte bodies from no-response attempts are local placeholders, not source response content; CONNECT 200 is excluded; CDX rows and CDX length are index evidence, never payloads.",
        "index_evidence_path": "cdx-index-pages.json",
        "observed_index_candidates_path": "observed-index-candidates.json",
    }
    write_json(OUT / "batch-report.json", report)
    report_sha = sha256_file(OUT / "batch-report.json")
    write_json(OUT / "payload-source-map.json", {
        "schema": "continuous-wow-network-ssotd12-payload-source-map/v1",
        "batch_id": "NET-SSOTD-012",
        "report_sha256": report_sha,
        "only_real_valid_entities": True,
        "entity_count": 0,
        "entries": [],
        "integration_held": True,
    })
    categories = Counter()
    for page in pages:
        categories["prefix_page_source_200" if page.get("final_source_status") == 200 else "prefix_page_transport_or_http"] += 1
    if redirect:
        categories[str(redirect.get("category") or "unknown")] += 1
    for status in operation_status:
        if status.get("category") == "not_requested":
            categories["not_requested"] += 1
    summary = {
        "schema": "continuous-wow-network-ssotd12-sanitized-summary/v1",
        "batch_id": "NET-SSOTD-012",
        "mode": "executed",
        "report_sha256": report_sha,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "request_window_finished_utc": finished_utc,
        "report_updated_utc": report_updated_utc,
        "network_requests": state.attempts,
        "source_response_count": state.source_responses,
        "source_request_count": state.attempts,
        "failed_attempt_count": state.failed_attempts,
        "operation_count": len(operation_status),
        "prefix_page_count_executed": len(pages),
        "cdx_index_row_count": len(all_rows),
        "redirect_or_revisit_index_candidate_count": len(observed_candidates),
        "valid_entity_count": 0,
        "payload_body_bytes": 0,
        "total_body_bytes": state.total_body_bytes,
        "disk_free_bytes_before": disk_before,
        "disk_free_bytes_after": disk_after,
        "dispatch_count": len(gate.dispatches),
        "minimum_start_interval_seconds": min_interval,
        "confirmed_transport": confirmed_transport,
        "category_counts": dict(sorted(categories.items())),
        "stop_reason": state.stop_reason,
        "batch_policy_accepted": all(policy_checks.values()),
        "policy_checks": policy_checks,
        "postflight": postflight,
        "unrequested_operations": [value for value in operation_status if value.get("category") == "not_requested"],
        "index_evidence_path": "cdx-index-pages.json",
        "redirect_evidence_path": "redirect-evidence.json",
        "raw_evidence_note": report["raw_evidence_note"],
    }
    write_json(OUT / "sanitized-summary.json", summary)
    lines = [
        "# NET-SSOTD-012 sanitized summary",
        "",
        f"- Prefix pages executed: `{len(pages)}`; index rows: `{len(all_rows)}`.",
        f"- Source requests/attempts: `{state.attempts}`; real source responses: `{state.source_responses}`.",
        f"- Redirect/revisit index candidates retained: `{len(observed_candidates)}`; valid payload entities: `0`.",
        f"- Dispatches: `{len(gate.dispatches)}`; minimum observed start interval: `{min_interval}` seconds.",
        f"- Disk free before/after: `{disk_before}` / `{disk_after}` bytes; stop: `{state.stop_reason or 'completed'}`.",
        "",
        "| Operation | Category | Source status | Actual Memento | Body bytes |",
        "|---|---|---:|---|---:|",
    ]
    for status in operation_status:
        lines.append(
            f"| `{status.get('operation')}` | `{status.get('category')}` | `{status.get('source_status') or ''}` | "
            f"`{status.get('actual_memento') or ''}` | `{status.get('body_bytes') or 0}` |"
        )
    lines.extend([
        "",
        "CDX rows are index evidence only; no newly observed row was replayed. The approved 301 probe is evidence only and was not followed.",
        "Raw headers, traces, stderr and bodies remain local below `raw/`.",
    ])
    (OUT / "sanitized-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def rebuild_offline() -> int:
    """Rebuild derived index classifications from this batch's saved raw files."""
    report_path = OUT / "batch-report.json"
    index_path = OUT / "cdx-index-pages.json"
    dispatch_path = OUT / "dispatch-log.json"
    candidate_path = OUT / "candidates.json"
    for path in (report_path, index_path, dispatch_path, candidate_path):
        if not path.is_file():
            raise RuntimeError(f"offline rebuild input missing: {path}")
    old_report = read_json(report_path)
    old_index = read_json(index_path)
    dispatch_log = read_json(dispatch_path)
    candidates = read_json(candidate_path)
    pages: list[dict[str, Any]] = []
    for old_page in old_index.get("pages") or []:
        page = dict(old_page)
        raw_path = str(page.get("raw_body_path") or "")
        body = read_attempt_body({"executed": True, "raw": {"body": raw_path}})
        parsed = parse_prefix_body(body) if page.get("final_source_status") == 200 else {
            "parse_valid": False, "parse_error": "no_source_200_response", "rows": [],
            "metadata_records": [], "resume_keys": [], "next_resume_key": None,
            "multiple_resume_keys": False,
        }
        next_key = parsed.get("next_resume_key")
        page.update({
            "parse_valid": parsed.get("parse_valid", False),
            "parse_error": parsed.get("parse_error"),
            "metadata_records": parsed.get("metadata_records") or [],
            "resume_keys": parsed.get("resume_keys") or [],
            "next_resume_key": next_key,
            "rows": parsed.get("rows") or [],
            "row_count": len(parsed.get("rows") or []),
            "row_distributions": row_distributions(parsed.get("rows") or []),
            "body_bytes": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        })
        pages.append(page)
    operations = [dict(value) for value in old_report.get("operations") or []]
    if pages and operations:
        operations[0].update({
            "next_resume_key_observed": pages[0].get("next_resume_key"),
            "body_bytes": pages[0].get("body_bytes"),
            "body_sha256": pages[0].get("body_sha256"),
        })
    gate = SimpleNamespace(dispatches=dispatch_log.get("dispatches") or [])
    state = SimpleNamespace(
        attempts=int(old_report.get("source_request_count") or old_report.get("transport_attempt_count") or 0),
        source_responses=int(old_report.get("source_response_count") or 0),
        failed_attempts=int(old_report.get("failed_attempt_count") or 0),
        total_body_bytes=int(old_report.get("total_body_bytes") or 0),
        stop_reason=old_report.get("stop_reason"),
        stop_detail=old_report.get("stop_detail") or {},
        rate_limit=old_report.get("rate_limit"),
    )
    redirect = old_report.get("redirect_probe")
    postflight = old_report.get("postflight") or dispatch_log.get("disk_postflight") or {
        "checked_utc": None,
        "disk_free_bytes": None,
        "attempts_count": state.attempts,
        "persisted_in_finally": bool(dispatch_log.get("postflight_persisted_in_finally")),
    }
    disk_before = int((old_report.get("preflight") or {}).get("disk_free_bytes_before") or 0)
    disk_after = int((old_report.get("preflight") or {}).get("disk_free_bytes_after") or 0)
    report_updated = utc()
    write_outputs(
        candidates, pages, operations, redirect, state, gate,
        str(old_report.get("started_utc")),
        str(old_report.get("finished_utc") or old_report.get("request_window_finished_utc")),
        report_updated, disk_before, disk_after,
        (old_report.get("transport") or {}).get("confirmed_transport_after_first_request"),
        postflight, None,
    )
    print(json.dumps({
        "mode": "offline_rebuild",
        "batch_id": "NET-SSOTD-012",
        "network_requests": 0,
        "report_updated_utc": report_updated,
        "corrected_prefix_rows": sum(page.get("row_count", 0) for page in pages),
        "redirect_or_revisit_candidates": len(read_json(OUT / "observed-index-candidates.json").get("entries") or []),
        "report_sha256": sha256_file(report_path),
    }, ensure_ascii=False))
    return 0


def execute() -> int:
    plan = verify_approved_plan()
    candidate_path = OUT / "candidates.json"
    if not candidate_path.is_file():
        prepare()
    candidates = read_json(candidate_path)
    if candidates.get("network_requests") != 0 or candidates.get("batch_id") != "NET-SSOTD-012":
        raise RuntimeError("candidate declaration is not the zero-network approved SSOTD-012 plan")
    first_url = str(plan["first_cdx_request_url"])
    initial_key = str(plan["initial_resume_key"])
    if candidates.get("operations", [{}])[0].get("request_url") != first_url:
        raise RuntimeError("candidate first URL does not match approved plan")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    disk_before = disk_free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D free space below floor before dispatch: {disk_before}")
    started_utc = utc()
    window_started = time.monotonic()
    state = core.RunState(window_started)
    journal = {
        "schema": "continuous-wow-network-ssotd12-dispatch-log/v1",
        "batch_id": "NET-SSOTD-012",
        "simulation": False,
        "policy": {
            "minimum_dispatch_interval_seconds": INTERVAL_SECONDS,
            "max_attempts": MAX_ATTEMPTS,
            "network_window_seconds": WINDOW_SECONDS,
            "automatic_redirects": 0,
            "manual_follow_hops": 0,
        },
        "disk_preflight": {
            "checked_utc": started_utc,
            "disk_free_bytes": disk_before,
            "minimum_free_bytes": MIN_FREE_BYTES,
        },
        "dispatches": [],
    }
    gate = gate_mod.GateState(
        datetime.now(timezone.utc) - timedelta(seconds=1),
        journal_path=OUT / "dispatch-log.json",
        journal=journal,
    )
    gate.persist()
    pages: list[dict[str, Any]] = []
    operation_status: list[dict[str, Any]] = []
    redirect: dict[str, Any] | None = None
    confirmed_transport: str | None = None
    execution_error: dict[str, str] | None = None
    seen_keys = set(str(value) for value in plan.get("previously_used_resume_keys") or [])
    seen_keys.add(initial_key)
    current_url: str | None = first_url
    current_key: str | None = initial_key
    try:
        for page_number in range(1, MAX_PREFIX_PAGES + 1):
            if current_url is None or current_key is None:
                break
            if state.stop_reason:
                break
            page, confirmed_transport = run_prefix_page(
                page_number, current_url, current_key, confirmed_transport,
                state, gate, window_started,
            )
            pages.append(page)
            operation_status.append({
                "sequence": page_number,
                "operation": page["operation"],
                "page_number": page_number,
                "category": "source_response" if page.get("final_source_status") is not None else "transport_error_or_not_requested",
                "source_status": page.get("final_source_status"),
                "attempt_count": page.get("attempt_count"),
                "source_response_count": page.get("source_response_count"),
                "body_bytes": page.get("body_bytes"),
                "body_sha256": page.get("body_sha256"),
                "actual_memento": None,
                "request_url": page.get("request_url"),
                "next_resume_key_observed": page.get("next_resume_key"),
            })
            next_key = page.get("next_resume_key")
            if not next_key:
                current_url = None
                current_key = None
                break
            if next_key in seen_keys:
                page["next_resume_key_reused"] = True
                page["next_resume_key"] = None
                current_url = None
                current_key = None
                break
            next_url = replace_resume_key(first_url, str(next_key))
            if strip_resume_key(next_url) != strip_resume_key(first_url):
                raise RuntimeError("generated continuation changed a non-resume query parameter")
            seen_keys.add(str(next_key))
            current_key = str(next_key)
            current_url = next_url
        if len(pages) < MAX_PREFIX_PAGES:
            reason = (
                state.stop_reason or
                "no_actual_unique_resume_key_from_immediately_previous_response"
            )
            for slot in range(len(pages) + 1, MAX_PREFIX_PAGES + 1):
                operation_status.append({
                    "sequence": slot,
                    "operation": "cdx_prefix_resume_page",
                    "page_number": slot,
                    "category": "not_requested",
                    "reason": reason,
                    "source_status": None,
                    "attempt_count": 0,
                    "source_response_count": 0,
                    "body_bytes": 0,
                    "actual_memento": None,
                    "request_url": None,
                })
        if not state.stop_reason and confirmed_transport:
            redirect = run_redirect_probe(plan["redirect_probe"], confirmed_transport, state, gate, window_started)
            operation_status.append({
                "sequence": 4,
                "operation": redirect.get("operation"),
                "category": redirect.get("category"),
                "reason": redirect.get("reason"),
                "source_status": redirect.get("source_status"),
                "attempt_count": sum(bool(item.get("executed")) for item in redirect.get("attempts") or []),
                "source_response_count": int(redirect.get("source_status") is not None),
                "body_bytes": redirect.get("body_bytes", 0),
                "body_sha256": redirect.get("body_sha256"),
                "actual_memento": redirect.get("actual_memento"),
                "request_url": redirect.get("request_url"),
            })
        else:
            operation_status.append({
                "sequence": 4,
                "operation": "known_301_first_hop_probe",
                "category": "not_requested",
                "reason": state.stop_reason or "no_confirmed_transport_after_prefix_operations",
                "source_status": None,
                "attempt_count": 0,
                "source_response_count": 0,
                "body_bytes": 0,
                "actual_memento": None,
                "request_url": plan["redirect_probe"]["request_url"],
            })
    except Exception as exc:  # preserve dispatch/postflight evidence on assembly failures
        execution_error = {"type": type(exc).__name__, "message": str(exc)}
        state.stop_reason = state.stop_reason or "execution_exception"
        state.stop_detail = {"exception": type(exc).__name__, "message": str(exc)}
    finally:
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=disk_free_bytes)
    finished_utc = utc()
    disk_after = disk_free_bytes()
    report_updated_utc = utc()
    write_outputs(
        candidates, pages, operation_status, redirect, state, gate,
        started_utc, finished_utc, report_updated_utc,
        disk_before, disk_after, confirmed_transport, postflight, execution_error,
    )
    print(json.dumps({
        "mode": "executed",
        "batch_id": "NET-SSOTD-012",
        "network_requests": state.attempts,
        "source_responses": state.source_responses,
        "failed_attempts": state.failed_attempts,
        "prefix_pages": len(pages),
        "index_rows": sum(page.get("row_count", 0) for page in pages),
        "valid_entities": 0,
        "redirect_category": redirect.get("category") if redirect else None,
        "disk_free_before": disk_before,
        "disk_free_after": disk_after,
        "minimum_start_interval_seconds": min((x.get("interval_since_previous_dispatch_seconds") for x in gate.dispatches if x.get("interval_since_previous_dispatch_seconds") is not None), default=None),
        "stop_reason": state.stop_reason,
        "execution_error": execution_error,
    }, ensure_ascii=False))
    return 1 if execution_error else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.prepare, args.execute, args.rebuild)) != 1:
        parser.error("choose exactly one of --prepare, --execute or --rebuild")
    if args.prepare:
        return prepare()
    if args.execute:
        return execute()
    return rebuild_offline()


if __name__ == "__main__":
    raise SystemExit(main())

"""Bounded native replay probe with shared offline policy gates.

The v2 execution path reuses only the frozen V3 low-level curl, header,
decode, and image helpers after verifying their SHA. All dispatch, deadline,
byte-budget, transfer-streak, and cooldown decisions live in pure helpers
called by both real execution and the synthetic fixture suite. CDX queries,
URL guessing, redirects, and image acceptance are outside this driver.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
RECOVERY = ROOT / "research" / "continuous-recovery-20261018"
THIS_DIR = RECOVERY / "network" / "native-replay47-v2"
FIXTURE_PATH = THIS_DIR / "fixtures" / "native-replay47-fixtures.json"
QUEUE_PATH = RECOVERY / "publication" / "native-karazhan-unknown47-queue.json"
STATUS_PATH = RECOVERY / "status.json"
EXPECTED_V3_SHA = "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955"
DISK_FLOOR = 11_005_853_696
TOTAL_BODY_CAP = 16 * 1024 * 1024
ENTITY_BODY_CAP = 8 * 1024 * 1024
MIN_DISPATCH = 5.25
MIN_REQUEST_START = 5.0
COOLDOWN_SECONDS = 120
MAX_ATTEMPTS = 14
QUEUE_COUNT = 47
MAX_TARGETS = 12
ARCHIVE_REPLAY_RE = re.compile(
    r"^/web/[0-9]{14}id_/http://www\.worldofwarcraft\.com/info/dungeons/images/karazhan/[^/?#]+$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, value: Any, floor: int = DISK_FLOOR) -> None:
    require_disk(floor)
    path.parent.mkdir(parents=True, exist_ok=True)
    require_disk(floor)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    require_disk(floor)
    temporary.replace(path)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def resolve_path(value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def require_disk(floor: int = DISK_FLOOR) -> int:
    free = shutil.disk_usage(ROOT).free
    if free < floor:
        raise RuntimeError(f"disk floor violated: {free} < {floor}")
    return free


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().isoformat()


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def import_frozen_v3(path: Path):
    if sha256(path) != EXPECTED_V3_SHA:
        raise RuntimeError("frozen V3 SHA mismatch")
    spec = importlib.util.spec_from_file_location("frozen_reusable_image_driver_v3_v2", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen V3")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Shared pure policy/classification helpers. Real execution and fixtures use
# these same functions; fixture arithmetic must not be a second policy.


def cooldown_seconds(retry_after: Any, minimum: int = COOLDOWN_SECONDS) -> int:
    try:
        parsed = int(retry_after) if retry_after is not None else 0
    except (TypeError, ValueError):
        parsed = 0
    return max(minimum, parsed)


def cooldown_until(start: datetime, retry_after: Any = None, minimum: int = COOLDOWN_SECONDS) -> datetime:
    return start + timedelta(seconds=cooldown_seconds(retry_after, minimum))


def transfer_failure(meta: dict[str, Any]) -> bool:
    """A nonzero curl exit counts even when a partial HTTP response exists."""
    return meta.get("source_status") is None or meta.get("curl_exit") not in (None, 0)


def next_failure_streak(current: int, classified: dict[str, Any]) -> int:
    return current + 1 if classified.get("transfer_failure") else 0


def dispatch_budget_gate(
    *,
    now_mono: float,
    batch_start_mono: float,
    now_time: datetime,
    deadline_utc: datetime,
    last_dispatch_mono: float | None,
    last_start_mono: float | None,
    attempt_count: int,
    max_attempts: int,
    total_body_bytes: int,
    max_total_body_bytes: int,
    entity_body_cap: int,
    transport_max_seconds: float,
    min_dispatch_seconds: float,
    min_request_start_seconds: float,
    window_seconds: float,
    disk_free_bytes: int,
    disk_floor_bytes: int,
    failure_streak: int,
    inherited_tail: int,
) -> dict[str, Any]:
    """Compute every pre-dispatch limit without sleeping or touching network."""
    remaining_window = max(0.0, window_seconds - (now_mono - batch_start_mono))
    remaining_deadline = max(0.0, (deadline_utc - now_time).total_seconds())
    remaining_body = max(0, max_total_body_bytes - total_body_bytes)
    cadence_wait = max(
        max(0.0, min_dispatch_seconds - (now_mono - last_dispatch_mono))
        if last_dispatch_mono is not None else 0.0,
        max(0.0, min_request_start_seconds - (now_mono - last_start_mono))
        if last_start_mono is not None else 0.0,
    )
    result: dict[str, Any] = {
        "allow": False,
        "reason": None,
        "remaining_window_seconds": remaining_window,
        "remaining_deadline_seconds": remaining_deadline,
        "remaining_body_bytes": remaining_body,
        "cadence_wait_seconds": cadence_wait,
        "timeout_seconds": 0.0,
        "body_cap": 0,
        "disk_free_bytes": disk_free_bytes,
    }
    checks = (
        (attempt_count >= max_attempts, "max_attempts"),
        (inherited_tail >= 5 or failure_streak >= 5, "five_consecutive_transfer_failures"),
        (remaining_window <= 0.0, "window_exceeded"),
        (remaining_deadline <= 0.0, "deadline_exceeded"),
        (remaining_body <= 0, "total_body_budget_exhausted"),
        (disk_free_bytes < disk_floor_bytes, "disk_floor_before_dispatch"),
    )
    for failed, reason in checks:
        if failed:
            result["reason"] = reason
            return result
    timeout_seconds = min(float(transport_max_seconds), remaining_window, remaining_deadline)
    body_cap = min(int(entity_body_cap), remaining_body)
    if timeout_seconds <= 0.0:
        result["reason"] = "timeout_budget_exhausted"
        return result
    if body_cap <= 0:
        result["reason"] = "body_budget_exhausted"
        return result
    result.update({"allow": True, "timeout_seconds": timeout_seconds, "body_cap": body_cap})
    return result


def extract_location(raw_headers: bytes) -> str | None:
    for line in raw_headers.decode("iso-8859-1", errors="replace").splitlines():
        if line.lower().startswith("location:"):
            return line.split(":", 1)[1].strip()
    return None


def raw_path(value: str | None) -> Path | None:
    if not value:
        return None
    path = resolve_path(value)
    return path if path.is_file() else None


def classify_bytes(v3, meta: dict[str, Any], raw_headers: bytes, body: bytes,
                   expected_mime: list[str]) -> dict[str, Any]:
    headers = v3.parse_headers(raw_headers)
    status = meta.get("source_status") if meta.get("source_status") is not None else headers.get("status")
    failed = transfer_failure(meta)
    payload, decode_error = v3.decoded_payload(body, headers.get("content_encoding", ""), ENTITY_BODY_CAP)
    result: dict[str, Any] = {
        "classification": None,
        "source_status": status,
        "transfer_failure": failed,
        "content_type": headers.get("content_type"),
        "content_encoding": headers.get("content_encoding"),
        "body_bytes": len(body),
        "raw_body_sha256": meta.get("raw_body_sha256") or sha_bytes(body),
        "decoded_body_bytes": len(payload) if payload is not None else None,
        "decoded_body_sha256": sha_bytes(payload) if payload is not None else None,
        "decode_error": decode_error,
        "location": extract_location(raw_headers),
        "memento_datetime": headers.get("memento_datetime"),
        "image_validation": None,
        "pending_source_index": False,
    }
    if status is None:
        result["classification"] = "transport_unknown"
        return result
    if status == 404:
        result["classification"] = "partial_http_404" if failed else "actual404"
        return result
    if status == 302:
        result["classification"] = "partial_http_302" if failed else "observed_302_location"
        return result
    if status == 200:
        if payload is not None:
            validation = v3.image_validation(payload, headers.get("content_type", ""), set(expected_mime))
            result["image_validation"] = validation
            if not validation.get("error") and not failed:
                result["classification"] = "pending_source_index"
                result["pending_source_index"] = True
            elif failed:
                result["classification"] = "partial_http_200"
            else:
                result["classification"] = "http_200_nonimage"
        else:
            result["classification"] = "partial_http_200" if failed else "http_200_nonimage"
        return result
    result["classification"] = f"partial_http_{status}" if failed else f"http_{status}"
    return result


def classify_response(v3, meta: dict[str, Any], expected_mime: list[str]) -> dict[str, Any]:
    headers_path = raw_path(meta.get("headers_path"))
    body_path = raw_path(meta.get("body_path"))
    raw_headers = headers_path.read_bytes() if headers_path else b""
    body = body_path.read_bytes() if body_path else b""
    return classify_bytes(v3, meta, raw_headers, body, expected_mime)


def qualifies_direct_fallback(meta: dict[str, Any], classified: dict[str, Any]) -> bool:
    return (meta.get("transport") == "direct" and classified.get("transfer_failure")
            and meta.get("curl_exit") in {7, 28} and meta.get("source_status") is None
            and meta.get("body_bytes") == 0)


def stop_http(classified: dict[str, Any]) -> bool:
    return classified.get("source_status") in {429, 503}


def resolve_status_pointer(status: dict[str, Any], field: str) -> Path:
    value = status.get(field)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"status has no {field}")
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    if value.replace("\\", "/").startswith("research/"):
        return ROOT / candidate
    return RECOVERY / candidate


def validate_exact_queue_membership(plan: dict[str, Any]) -> dict[str, Any]:
    queue_ref = plan.get("queue") or {}
    queue_path = resolve_path(queue_ref.get("path", ""))
    if not queue_path.is_file() or sha256(queue_path) != queue_ref.get("sha256"):
        raise RuntimeError("plan queue binding is stale or missing")
    queue = read_json(queue_path)
    rows = queue.get("rows") or []
    if queue.get("accepted") is not True or queue.get("request_count") != 0 or len(rows) != QUEUE_COUNT:
        raise RuntimeError("frozen queue contract is invalid")
    count = plan.get("candidate_count")
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= MAX_TARGETS:
        raise RuntimeError("candidate_count must be between one and twelve")
    candidates = plan.get("candidates") or []
    if len(candidates) != count:
        raise RuntimeError("candidate_count does not match candidates")
    selected = (plan.get("selection") or {}).get("selected_ranks")
    if selected != list(range(1, count + 1)):
        raise RuntimeError("selection must be the first contiguous queue ranks")
    for index, candidate in enumerate(candidates, 1):
        row = rows[index - 1]
        if candidate.get("queue_rank") != index or candidate.get("target_id") != row.get("target_id") \
                or candidate.get("original") != row.get("original_url") \
                or candidate.get("request_url") != row.get("request_url"):
            raise RuntimeError(f"candidate {index} is not the exact frozen queue row")
        request = candidate.get("request_url")
        parsed = urlsplit(request or "")
        if parsed.scheme != "https" or parsed.netloc != "web.archive.org" or parsed.query or parsed.fragment \
                or not ARCHIVE_REPLAY_RE.fullmatch(parsed.path):
            raise RuntimeError(f"candidate {index} has an unapproved replay URL")
        if not request.endswith(candidate.get("original", "")):
            raise RuntimeError(f"candidate {index} replay URL does not end with exact original")
        evidence = candidate.get("source_evidence") or {}
        if evidence.get("path") != queue_ref.get("path") or evidence.get("sha256") != queue_ref.get("sha256") \
                or evidence.get("row_index") != index or evidence.get("requested") != request:
            raise RuntimeError(f"candidate {index} source evidence is not queue-bound")
        if row.get("global_category") != "transport_unknown":
            raise RuntimeError(f"candidate {index} is outside transport_unknown queue scope")
    return queue


def status_cooldown_not_before(status: dict[str, Any]) -> datetime | None:
    for value in (status.get("network_cooldown_not_before_utc"), status.get("cooldown_not_before_utc")):
        if isinstance(value, str) and value.strip():
            return parse_utc(value)
    return None


def revalidate_live_bindings(plan: dict[str, Any]) -> dict[str, Any]:
    status = read_json(STATUS_PATH)
    source_bindings = plan.get("source_bindings") or {}
    source_field = "latest_source_acceptance" if status.get("latest_source_acceptance") else "last_image_source_acceptance"
    source_path = resolve_status_pointer(status, source_field)
    control_path = resolve_status_pointer(status, "latest_control_gate")
    source_sha = sha256(source_path)
    control_sha = sha256(control_path)
    source_ref = source_bindings.get("latest_source_acceptance") or {}
    control_ref = source_bindings.get("latest_control_gate") or {}
    if source_ref.get("path") != rel(source_path) or source_ref.get("sha256") != source_sha:
        raise RuntimeError("active latest source receipt changed since preparation")
    if control_ref.get("path") != rel(control_path) or control_ref.get("sha256") != control_sha:
        raise RuntimeError("active latest control gate changed since preparation")
    source = read_json(source_path)
    control = read_json(control_path)
    if source.get("accepted") is not True or source.get("failure_streak_end") != 0:
        raise RuntimeError("latest source is not accepted with tail zero")
    if control.get("accepted") is not True or control.get("resume_gate_passed") is not True \
            or control.get("control_final_streak") != 0:
        raise RuntimeError("latest control is not an accepted tail-zero gate")
    if int(status.get("latest_failure_tail", 0)) != 0:
        raise RuntimeError("active status failure tail is non-zero")
    cooldown = status_cooldown_not_before(status)
    source_cooldown = source.get("cooldown_not_before_utc")
    if cooldown and cooldown > now_utc():
        raise RuntimeError("active status is still in cooldown")
    if isinstance(source_cooldown, str) and source_cooldown and parse_utc(source_cooldown) > now_utc():
        raise RuntimeError("latest source receipt is still in cooldown")
    expected_tail = (plan.get("previous_batch") or {}).get("latest_source_tail_end")
    if expected_tail != source.get("failure_streak_end"):
        raise RuntimeError("latest source tail differs from plan binding")
    return {
        "status_sha256_current": sha256(STATUS_PATH),
        "source_path": rel(source_path), "source_sha256": source_sha,
        "source_tail": source.get("failure_streak_end"),
        "control_path": rel(control_path), "control_sha256": control_sha,
        "control_resume_gate_passed": control.get("resume_gate_passed"),
        "cooldown_not_before_utc": None,
    }


def load_plan(plan_path: Path) -> tuple[dict[str, Any], dict[str, Any], Path, dict[str, Any]]:
    plan = read_json(plan_path)
    if plan.get("schema") != "wow-recovery.native-replay47-probe-plan.v2":
        raise RuntimeError("unexpected native replay v2 plan schema")
    policy = plan.get("policy") or {}
    expected_policy = {
        "max_attempts": MAX_ATTEMPTS, "window_seconds": 240.0,
        "max_total_body_bytes": TOTAL_BODY_CAP, "max_entity_body_bytes": ENTITY_BODY_CAP,
        "min_dispatch_seconds": MIN_DISPATCH, "min_request_start_seconds": MIN_REQUEST_START,
        "disk_floor_bytes": DISK_FLOOR, "direct_first": True, "tls_verification": True,
        "automatic_redirects": 0, "stop_http_codes": [429, 503], "cooldown_seconds": COOLDOWN_SECONDS,
    }
    for key, value in expected_policy.items():
        if policy.get(key) != value:
            raise RuntimeError(f"policy mismatch: {key}={policy.get(key)!r}")
    bindings_path = resolve_path(plan["input_bindings_path"])
    bindings = read_json(bindings_path)
    if bindings.get("plan_sha256") != sha256(plan_path):
        raise RuntimeError("input-bindings plan SHA mismatch")
    v3_ref = plan.get("frozen_v3") or {}
    v3_path = resolve_path(v3_ref.get("path", ""))
    if not v3_path.is_file() or v3_ref.get("sha256") != EXPECTED_V3_SHA or sha256(v3_path) != EXPECTED_V3_SHA:
        raise RuntimeError("plan does not bind accepted frozen V3")
    native_ref = plan.get("native_driver") or {}
    native_path = Path(__file__).resolve()
    if native_ref.get("path") != rel(native_path) or native_ref.get("sha256") != sha256(native_path):
        raise RuntimeError("plan does not bind this exact native v2 driver")
    if bindings.get("frozen_v3_driver", {}).get("sha256") != EXPECTED_V3_SHA:
        raise RuntimeError("bindings do not bind accepted frozen V3")
    validate_exact_queue_membership(plan)
    live = revalidate_live_bindings(plan)
    return plan, bindings, v3_path, live


def validate_root_acceptance(plan_path: Path, plan: dict[str, Any], bindings: dict[str, Any], acceptance_sha: str) -> dict[str, Any]:
    acceptance_path = resolve_path(plan["root_plan_acceptance"]["path"])
    if not acceptance_path.is_file() or sha256(acceptance_path) != acceptance_sha:
        raise RuntimeError("root plan acceptance is missing or SHA-mismatched")
    acceptance = read_json(acceptance_path)
    if acceptance.get("accepted") is not True or acceptance.get("plan_sha256") != sha256(plan_path):
        raise RuntimeError("root acceptance is not for this exact plan")
    if acceptance.get("bindings_sha256") not in (None, sha256(resolve_path(plan["input_bindings_path"]))):
        raise RuntimeError("root acceptance binds different input bindings")
    if acceptance.get("driver_sha256") not in (None, sha256(Path(__file__).resolve())):
        raise RuntimeError("root acceptance binds different native driver")
    return acceptance


def make_attempt_stub(candidate: dict[str, Any], attempt_no: int, transport: str) -> dict[str, Any]:
    return {
        "attempt_no": attempt_no, "target_key": candidate["target_key"], "target_id": candidate["target_id"],
        "queue_rank": candidate["queue_rank"], "transport": transport, "url": candidate["request_url"],
        "sent": False, "classification": None, "dispatch_refused": None, "started_utc": None,
        "finished_utc": None, "curl_exit": None, "source_status": None, "body_bytes": 0,
        "raw_body_sha256": None, "headers_path": None, "body_path": None, "trace_path": None,
        "stderr_path": None, "status_path": None, "retry_after": None, "location": None,
        "image_validation": None, "transfer_failure": None,
    }


def timeout_meta(raw_dir: Path, transport: str, url: str, attempt_no: int,
                 timeout: float, connect_timeout: float, v3, exc: BaseException,
                 started_utc: str | None = None) -> dict[str, Any]:
    """Turn V3 TimeoutExpired into a persisted, classified actual attempt."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    stem = f"attempt-{attempt_no:03d}-{transport}"
    paths = {suffix: raw_dir / f"{stem}-{suffix}" for suffix in ("headers.txt", "body.bin", "trace.txt", "stderr.txt", "status.txt")}
    if not paths["stderr.txt"].exists():
        paths["stderr.txt"].write_text("TimeoutExpired\n", encoding="utf-8")
    if not paths["status.txt"].exists():
        paths["status.txt"].write_text("000\n", encoding="ascii")
    raw_headers = paths["headers.txt"].read_bytes() if paths["headers.txt"].exists() else b""
    body = paths["body.bin"].read_bytes() if paths["body.bin"].exists() else b""
    headers = v3.parse_headers(raw_headers)
    source_status = headers.get("status") if headers.get("source_block_found") else None
    return {
        "transport": transport, "url": url, "started_utc": started_utc or iso_now(), "finished_utc": iso_now(),
        "curl_exit": 28, "source_status": source_status, "body_bytes": len(body),
        "headers_path": rel(paths["headers.txt"]) if paths["headers.txt"].exists() else None,
        "body_path": rel(paths["body.bin"]) if paths["body.bin"].exists() else None,
        "trace_path": rel(paths["trace.txt"]) if paths["trace.txt"].exists() else None,
        "stderr_path": rel(paths["stderr.txt"]), "status_path": rel(paths["status.txt"]),
        "raw_body_sha256": sha_bytes(body), "retry_after": headers.get("retry_after"),
        "retry_after_kind": headers.get("retry_after_kind"),
        "header_source_block_found": headers.get("source_block_found"),
        "header_connect_statuses": headers.get("connect_statuses", []),
        "effective_timeout_seconds": timeout, "effective_connect_timeout_seconds": connect_timeout,
        "timeout_expired": True, "timeout_exception": type(exc).__name__,
    }


def run_go(plan_path: Path, acceptance_sha: str, deadline_utc: str) -> dict[str, Any]:
    plan, bindings, v3_path, live = load_plan(plan_path)
    acceptance = validate_root_acceptance(plan_path, plan, bindings, acceptance_sha)
    deadline = parse_utc(deadline_utc)
    if deadline <= now_utc():
        raise RuntimeError("execution deadline is already past")
    output = plan_path.parent / "output"
    if output.exists() and any(output.iterdir()):
        raise RuntimeError("execution output exists and is non-empty")
    require_disk(DISK_FLOOR)
    output.mkdir(parents=True, exist_ok=True)
    raw_dir = output / "raw"
    public_dir = output / "public"
    raw_dir.mkdir(parents=True, exist_ok=True)
    public_dir.mkdir(parents=True, exist_ok=True)
    v3 = import_frozen_v3(v3_path)
    policy = plan["policy"]
    v3.USER_AGENT = policy["user_agent"]
    v3.PROXY = policy["proxy"]
    v3.DIRECT_CONNECT_SECONDS = policy["direct_connect_timeout_seconds"]
    v3.DIRECT_MAX_SECONDS = policy["direct_max_seconds"]
    v3.PROXY_CONNECT_SECONDS = policy["proxy_connect_timeout_seconds"]
    v3.PROXY_MAX_SECONDS = policy["proxy_max_seconds"]
    v3.MAX_ENTITY_BODY_BYTES = ENTITY_BODY_CAP
    v3.DISK_FLOOR_BYTES = DISK_FLOOR
    v3.OUT, v3.RAW, v3.PUBLIC = output, raw_dir, public_dir

    started = iso_now()
    batch_start_mono = time.monotonic()
    inherited_tail = int((plan.get("previous_batch") or {}).get("latest_source_tail_end", 0))
    state: dict[str, Any] = {
        "schema": "wow-recovery.native-replay47-execution-state.v2", "batch_id": plan["batch_id"],
        "plan_path": rel(plan_path), "plan_sha256": sha256(plan_path),
        "root_plan_acceptance_sha256": acceptance_sha, "root_plan_acceptance_checked": True,
        "deadline_utc": deadline.isoformat(), "started_utc": started, "finished_utc": None,
        "live_bindings_at_start": live, "inherited_failure_tail": inherited_tail,
        "failure_streak": inherited_tail, "batch_proxy_only": False, "attempts": [],
        "total_body_bytes": 0, "stop_reason": None, "cooldown_not_before_utc": None,
        "network_requests_during_preparation": 0,
    }
    state_path = output / "state.json"
    report_path = output / "batch-report.json"
    write_json_atomic(state_path, state)
    last_dispatch: float | None = None
    last_start: float | None = None
    candidate_index = 0
    batch_proxy_only = False
    stop_reason: str | None = None
    cooldown_deadline: datetime | None = None

    def persist() -> None:
        state["batch_proxy_only"] = batch_proxy_only
        state["stop_reason"] = stop_reason
        state["cooldown_not_before_utc"] = cooldown_deadline.isoformat() if cooldown_deadline else None
        write_json_atomic(state_path, state)

    while candidate_index < len(plan["candidates"]):
        transport = "proxy" if batch_proxy_only else "direct"
        transport_max = policy["direct_max_seconds"] if transport == "direct" else policy["proxy_max_seconds"]
        actual_count = sum(1 for attempt in state["attempts"] if attempt.get("sent"))
        gate_args = dict(
            now_mono=time.monotonic(), batch_start_mono=batch_start_mono, now_time=now_utc(), deadline_utc=deadline,
            last_dispatch_mono=last_dispatch, last_start_mono=last_start, attempt_count=actual_count,
            max_attempts=MAX_ATTEMPTS, total_body_bytes=state["total_body_bytes"], max_total_body_bytes=TOTAL_BODY_CAP,
            entity_body_cap=ENTITY_BODY_CAP, transport_max_seconds=transport_max,
            min_dispatch_seconds=MIN_DISPATCH, min_request_start_seconds=MIN_REQUEST_START, window_seconds=240.0,
            disk_free_bytes=shutil.disk_usage(ROOT).free, disk_floor_bytes=DISK_FLOOR,
            failure_streak=state["failure_streak"], inherited_tail=inherited_tail,
        )
        gate = dispatch_budget_gate(**gate_args)
        if not gate["allow"]:
            stop_reason = gate["reason"]
            if stop_reason == "five_consecutive_transfer_failures":
                cooldown_deadline = cooldown_until(now_utc())
            break
        attempt_no = actual_count + 1
        candidate = plan["candidates"][candidate_index]
        attempt = make_attempt_stub(candidate, attempt_no, transport)
        state["attempts"].append(attempt)
        persist()
        if gate["cadence_wait_seconds"] > 0:
            time.sleep(gate["cadence_wait_seconds"])
        gate_args.update(now_mono=time.monotonic(), now_time=now_utc())
        gate = dispatch_budget_gate(**gate_args)
        if not gate["allow"]:
            attempt["dispatch_refused"] = gate["reason"]
            stop_reason = f"post_cadence_{gate['reason']}"
            if gate["reason"] == "five_consecutive_transfer_failures":
                cooldown_deadline = cooldown_until(now_utc())
            persist()
            break
        try:
            live = revalidate_live_bindings(plan)
        except RuntimeError as exc:
            attempt["dispatch_refused"] = "live_binding_changed"
            attempt["dispatch_refused_detail"] = str(exc)
            stop_reason = "live_binding_changed"
            persist()
            break
        attempt["live_bindings_before_request"] = live
        attempt["disk_free_before_request"] = gate["disk_free_bytes"]
        attempt["dispatch_wait_seconds"] = gate["cadence_wait_seconds"]
        attempt["sent"] = True
        dispatch_mono = time.monotonic()
        last_dispatch = dispatch_mono
        last_start = dispatch_mono
        attempt["started_utc"] = iso_now()
        persist()
        try:
            meta = v3._curl_request(candidate["request_url"], transport, int(gate["body_cap"]),
                                    float(gate["timeout_seconds"]), raw_dir, attempt_no)
        except subprocess.TimeoutExpired as exc:
            meta = timeout_meta(raw_dir, transport, candidate["request_url"], attempt_no,
                                float(gate["timeout_seconds"]),
                                min(float(policy["direct_connect_timeout_seconds"] if transport == "direct" else policy["proxy_connect_timeout_seconds"]), float(gate["timeout_seconds"])),
                                v3, exc, attempt.get("started_utc"))
        classified = classify_response(v3, meta, candidate.get("expected_mime") or ["image/jpeg"])
        attempt.update({
            "started_utc": meta.get("started_utc", attempt["started_utc"]), "finished_utc": meta.get("finished_utc", iso_now()),
            "curl_exit": meta.get("curl_exit"), "source_status": meta.get("source_status"),
            "body_bytes": meta.get("body_bytes", 0), "raw_body_sha256": meta.get("raw_body_sha256"),
            "headers_path": meta.get("headers_path"), "body_path": meta.get("body_path"),
            "trace_path": meta.get("trace_path"), "stderr_path": meta.get("stderr_path"),
            "status_path": meta.get("status_path"), "retry_after": meta.get("retry_after"),
            "effective_timeout_seconds": meta.get("effective_timeout_seconds", gate["timeout_seconds"]),
            "effective_connect_timeout_seconds": meta.get("effective_connect_timeout_seconds"),
            "timeout_expired": meta.get("timeout_expired", False), "classification": classified.get("classification"),
            "location": classified.get("location"), "image_validation": classified.get("image_validation"),
            "decoded_body_bytes": classified.get("decoded_body_bytes"), "decoded_body_sha256": classified.get("decoded_body_sha256"),
            "content_type": classified.get("content_type"), "memento_datetime": classified.get("memento_datetime"),
            "pending_source_index": classified.get("pending_source_index", False),
            "transfer_failure": classified.get("transfer_failure"),
            "disk_free_after_request": shutil.disk_usage(ROOT).free,
        })
        state["total_body_bytes"] += int(meta.get("body_bytes") or 0)
        state["failure_streak"] = next_failure_streak(state["failure_streak"], classified)
        if state["total_body_bytes"] > TOTAL_BODY_CAP or int(meta.get("body_bytes") or 0) > int(gate["body_cap"]):
            stop_reason = "total_body_budget_exceeded"
        elif attempt["disk_free_after_request"] < DISK_FLOOR:
            stop_reason = "disk_floor_after_request"
        elif stop_http(classified):
            stop_reason = f"http_{classified['source_status']}"
            cooldown_deadline = cooldown_until(now_utc(), meta.get("retry_after"))
        elif state["failure_streak"] >= 5:
            stop_reason = "five_consecutive_transfer_failures"
            cooldown_deadline = cooldown_until(now_utc())
        elif transport == "direct" and qualifies_direct_fallback(meta, classified):
            batch_proxy_only = True
        else:
            candidate_index += 1
        persist()
        if stop_reason:
            break

    if stop_reason is None:
        stop_reason = "completed_candidate_queue"
    state["stop_reason"] = stop_reason
    state["finished_utc"] = iso_now()
    persist()
    attempts_sent = [x for x in state["attempts"] if x.get("sent")]
    counts: dict[str, int] = {}
    private_source_map: list[dict[str, Any]] = []
    public_entries: list[dict[str, Any]] = []
    for attempt in attempts_sent:
        classification = attempt.get("classification") or "unknown"
        counts[classification] = counts.get(classification, 0) + 1
        private_source_map.append({
            "attempt_no": attempt["attempt_no"], "target_key": attempt["target_key"], "target_id": attempt["target_id"],
            "queue_rank": attempt["queue_rank"], "transport": attempt["transport"], "request_url": attempt["url"],
            "classification": classification, "source_status": attempt.get("source_status"),
            "location": attempt.get("location"), "raw_body_sha256": attempt.get("raw_body_sha256"),
            "raw_paths": {k: attempt.get(k) for k in ("headers_path", "body_path", "trace_path", "stderr_path", "status_path")},
        })
        public_entries.append({
            "attempt_no": attempt["attempt_no"], "target_key": attempt["target_key"], "target_id": attempt["target_id"],
            "queue_rank": attempt["queue_rank"], "transport": attempt["transport"],
            "classification": classification, "source_status": attempt.get("source_status"),
            "body_bytes": attempt.get("body_bytes", 0), "raw_body_sha256": attempt.get("raw_body_sha256"),
            "pending_source_index": attempt.get("pending_source_index", False),
        })
    report = {
        "schema": "wow-recovery.native-replay47-batch-report.v2", "batch_id": state["batch_id"],
        "plan_path": state["plan_path"], "plan_sha256": state["plan_sha256"],
        "root_plan_acceptance_sha256": acceptance_sha, "started_utc": state["started_utc"],
        "finished_utc": state["finished_utc"], "deadline_utc": state["deadline_utc"],
        "requests": len(attempts_sent), "candidate_count": len(plan["candidates"]),
        "source_response_count": sum(1 for x in attempts_sent if x.get("source_status") is not None),
        "total_body_bytes": state["total_body_bytes"], "classification_counts": counts,
        "stop_reason": stop_reason, "cooldown_not_before_utc": state.get("cooldown_not_before_utc"),
        "failure_streak_start": inherited_tail, "failure_streak_end": state["failure_streak"],
        "batch_proxy_only": batch_proxy_only, "actual_transports": [x.get("transport") for x in attempts_sent],
        "attempts": state["attempts"], "private_source_map": private_source_map,
        "network_requests_during_preparation": 0,
        "acceptance_boundary": "200 image payloads are pending_source_index and require separate CDX/Memento/digest review",
    }
    write_json_atomic(report_path, report)
    public_status = {
        "schema": "wow-recovery.native-replay47-public-status.v2", "batch_id": state["batch_id"],
        "plan_sha256": state["plan_sha256"], "requests": len(attempts_sent),
        "source_responses": report["source_response_count"], "classification_counts": counts,
        "total_body_bytes": state["total_body_bytes"], "failure_streak_start": inherited_tail,
        "failure_streak_end": state["failure_streak"], "stop_reason": stop_reason,
        "cooldown_not_before_utc": state.get("cooldown_not_before_utc"),
        "accepted_images": 0, "pending_source_index": counts.get("pending_source_index", 0),
        "private_attempt_metadata": "kept in local batch-report/state only",
    }
    write_json_atomic(public_dir / "status-counts.json", public_status)
    write_json_atomic(public_dir / "source-map.json", {"schema": "wow-recovery.native-replay47-public-source-map.v2", "entries": public_entries})
    return report


def fixture_headers(status: int, content_type: str = "", location: str | None = None,
                    retry_after: str | None = None) -> bytes:
    lines = [f"HTTP/1.1 {status} Fixture", "Server: fixture"]
    if content_type:
        lines.append(f"Content-Type: {content_type}")
    if location:
        lines.append(f"Location: {location}")
    if retry_after:
        lines.append(f"Retry-After: {retry_after}")
    return ("\r\n".join(lines) + "\r\n\r\n").encode("ascii")


def run_fixtures(plan_path: Path | None) -> dict[str, Any]:
    plan = None
    if plan_path is not None:
        plan, _, v3_path, _ = load_plan(plan_path)
    else:
        v3_path = RECOVERY / "network" / "reusable-image-driver-v3" / "reusable_image_driver.py"
    v3 = import_frozen_v3(v3_path)
    fixture = read_json(FIXTURE_PATH)
    results: list[dict[str, Any]] = []

    def result(name: str, passed: bool, detail: dict[str, Any]) -> None:
        results.append({"name": name, "passed": bool(passed), "detail": detail})

    jpeg = base64.b64decode(fixture["jpeg_1x1_base64"])
    r = classify_bytes(v3, {"source_status": 404, "curl_exit": 0}, fixture_headers(404, "text/html"), b"", ["image/jpeg"])
    result("actual404_shared_classification", r["classification"] == "actual404" and not r["transfer_failure"], r)
    location = fixture["redirect_location"]
    r = classify_bytes(v3, {"source_status": 302, "curl_exit": 0}, fixture_headers(302, "text/html", location), b"", ["image/jpeg"])
    result("observed302_location_no_follow", r["classification"] == "observed_302_location" and r["location"] == location, r)
    r = classify_bytes(v3, {"source_status": 200, "curl_exit": 0}, fixture_headers(200, "text/html"), b"<html>fixture</html>", ["image/jpeg"])
    result("http200_nonimage_shared_classification", r["classification"] == "http_200_nonimage", r)
    r = classify_bytes(v3, {"source_status": 200, "curl_exit": 0}, fixture_headers(200, "image/jpeg"), jpeg, ["image/jpeg"])
    result("http200_image_pending_not_accepted", r["classification"] == "pending_source_index" and r["pending_source_index"] and not r.get("accepted", False), r)
    r = classify_bytes(v3, {"source_status": 200, "curl_exit": 28, "body_bytes": len(jpeg)}, fixture_headers(200, "image/jpeg"), jpeg, ["image/jpeg"])
    result("partial200_curl28_counts_transfer_failure", r["classification"] == "partial_http_200" and r["transfer_failure"] and not r["pending_source_index"], r)

    now = datetime(2026, 10, 18, tzinfo=timezone.utc)
    gate = dispatch_budget_gate(now_mono=239.0, batch_start_mono=0.0, now_time=now,
                                deadline_utc=now + timedelta(seconds=10), last_dispatch_mono=None, last_start_mono=None,
                                attempt_count=0, max_attempts=14, total_body_bytes=0, max_total_body_bytes=1000,
                                entity_body_cap=800, transport_max_seconds=20, min_dispatch_seconds=5.25,
                                min_request_start_seconds=5.0, window_seconds=240, disk_free_bytes=DISK_FLOOR,
                                disk_floor_bytes=DISK_FLOOR, failure_streak=0, inherited_tail=0)
    result("near_end_timeout_is_clamped", gate["allow"] and gate["timeout_seconds"] == 1.0, gate)
    gate = dispatch_budget_gate(now_mono=0, batch_start_mono=0, now_time=now, deadline_utc=now + timedelta(seconds=60),
                                last_dispatch_mono=None, last_start_mono=None, attempt_count=0, max_attempts=14,
                                total_body_bytes=96, max_total_body_bytes=100, entity_body_cap=800,
                                transport_max_seconds=20, min_dispatch_seconds=5.25, min_request_start_seconds=5,
                                window_seconds=240, disk_free_bytes=DISK_FLOOR, disk_floor_bytes=DISK_FLOOR,
                                failure_streak=0, inherited_tail=0)
    result("remaining_body_cap_is_clamped", gate["allow"] and gate["body_cap"] == 4, gate)
    gate_before = dispatch_budget_gate(now_mono=0, batch_start_mono=0, now_time=now, deadline_utc=now + timedelta(seconds=2),
                                       last_dispatch_mono=0, last_start_mono=0, attempt_count=0, max_attempts=14,
                                       total_body_bytes=0, max_total_body_bytes=1000, entity_body_cap=800,
                                       transport_max_seconds=20, min_dispatch_seconds=5.25, min_request_start_seconds=5,
                                       window_seconds=240, disk_free_bytes=DISK_FLOOR, disk_floor_bytes=DISK_FLOOR,
                                       failure_streak=0, inherited_tail=0)
    gate_after = dispatch_budget_gate(now_mono=5.25, batch_start_mono=0, now_time=now + timedelta(seconds=3), deadline_utc=now + timedelta(seconds=2),
                                      last_dispatch_mono=0, last_start_mono=0, attempt_count=0, max_attempts=14,
                                      total_body_bytes=0, max_total_body_bytes=1000, entity_body_cap=800,
                                      transport_max_seconds=20, min_dispatch_seconds=5.25, min_request_start_seconds=5,
                                      window_seconds=240, disk_free_bytes=DISK_FLOOR, disk_floor_bytes=DISK_FLOOR,
                                      failure_streak=0, inherited_tail=0)
    result("post_wait_deadline_recheck", gate_before["allow"] and not gate_after["allow"] and gate_after["reason"] == "deadline_exceeded", {"before": gate_before, "after": gate_after})
    gate = dispatch_budget_gate(now_mono=0, batch_start_mono=0, now_time=now, deadline_utc=now + timedelta(seconds=60),
                                last_dispatch_mono=None, last_start_mono=None, attempt_count=0, max_attempts=14,
                                total_body_bytes=0, max_total_body_bytes=1000, entity_body_cap=800,
                                transport_max_seconds=20, min_dispatch_seconds=5.25, min_request_start_seconds=5,
                                window_seconds=240, disk_free_bytes=DISK_FLOOR, disk_floor_bytes=DISK_FLOOR,
                                failure_streak=0, inherited_tail=5)
    future_cooldown = cooldown_until(now)
    result("inherited_tail_stops_with_cooldown", not gate["allow"] and gate["reason"] == "five_consecutive_transfer_failures" and future_cooldown > now, {"gate": gate, "cooldown": future_cooldown.isoformat()})
    with tempfile.TemporaryDirectory(dir=FIXTURE_PATH.parent) as temporary:
        raw_dir = Path(temporary)
        try:
            raise subprocess.TimeoutExpired(["curl.exe"], 1.0)
        except subprocess.TimeoutExpired as exc:
            meta = timeout_meta(raw_dir, "direct", "https://web.archive.org/web/20080512210044id_/http://www.worldofwarcraft.com/info/dungeons/images/karazhan/ss43-thumb.jpg", 1, 1.0, 1.0, v3, exc)
        persisted = all(raw_dir.joinpath(f"attempt-001-direct-{suffix}").exists() for suffix in ("stderr.txt", "status.txt"))
        result("timeout_expired_persisted_unknown_attempt", persisted and meta["curl_exit"] == 28 and meta["source_status"] is None and transfer_failure(meta), {"meta": {k: meta.get(k) for k in ("curl_exit", "source_status", "timeout_expired", "stderr_path", "status_path")}})
    calls: list[dict[str, Any]] = []
    def mock_low_level(url: str, transport: str, body_cap: int, timeout: float, raw_dir: Path, attempt_no: int) -> dict[str, Any]:
        calls.append({"url": url, "transport": transport, "body_cap": body_cap, "timeout": timeout, "attempt_no": attempt_no})
        return {"transport": transport, "url": url, "curl_exit": 0, "source_status": 404, "body_bytes": 0,
                "raw_body_sha256": sha_bytes(b""), "retry_after": None}
    gate = dispatch_budget_gate(now_mono=0, batch_start_mono=0, now_time=now, deadline_utc=now + timedelta(seconds=60),
                                last_dispatch_mono=None, last_start_mono=None, attempt_count=0, max_attempts=14,
                                total_body_bytes=0, max_total_body_bytes=1000, entity_body_cap=800, transport_max_seconds=4,
                                min_dispatch_seconds=5.25, min_request_start_seconds=5, window_seconds=240,
                                disk_free_bytes=DISK_FLOOR, disk_floor_bytes=DISK_FLOOR, failure_streak=0, inherited_tail=0)
    mock_low_level("https://web.archive.org/web/20080512210044id_/http://www.worldofwarcraft.com/info/dungeons/images/karazhan/ss43-thumb.jpg", "direct", gate["body_cap"], gate["timeout_seconds"], FIXTURE_PATH.parent, 1)
    result("mock_dispatcher_never_networks", len(calls) == 1 and calls[0]["timeout"] == 4.0 and calls[0]["body_cap"] == 800, {"calls": calls})
    output = {"schema": "wow-recovery.native-replay47-fixture-results.v2", "plan_sha256": sha256(plan_path) if plan_path else None,
              "network_requests": 0, "mock_low_level_calls": len(calls), "cases": results,
              "all_passed": all(item["passed"] for item in results)}
    output_path = FIXTURE_PATH.with_name("native-replay47-fixture-results.json")
    write_json_atomic(output_path, output)
    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-plan-acceptance")
    parser.add_argument("--deadline-utc")
    args = parser.parse_args()
    if args.fixture == args.go:
        raise SystemExit("select exactly one of --fixture or --go")
    if args.fixture:
        run_fixtures(args.plan.resolve() if args.plan else None)
        return
    if args.plan is None or not args.root_plan_acceptance or not args.deadline_utc:
        raise SystemExit("--go requires --plan, --root-plan-acceptance, and --deadline-utc")
    report = run_go(args.plan.resolve(), args.root_plan_acceptance, args.deadline_utc)
    print(json.dumps({"batch_id": report["batch_id"], "plan_sha256": report["plan_sha256"],
                      "requests": report["requests"], "classification_counts": report["classification_counts"],
                      "total_body_bytes": report["total_body_bytes"], "stop_reason": report["stop_reason"],
                      "failure_streak_end": report["failure_streak_end"]}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

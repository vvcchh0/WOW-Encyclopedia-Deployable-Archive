#!/usr/bin/env python3
"""Reusable bounded exact-CDX/image-replay driver for ALLNEWS02.

The driver owns queue/spec orchestration and acceptance logic while reusing the
existing core curl/raw/status primitive.  It is intentionally smaller than the
historical NEWS02 batch script and performs no work until ``--execute`` is
explicitly selected.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import io
import json
import re
import shutil
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from PIL import Image, ImageSequence


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"

DEFAULT_FROM = "20060101000000"
DEFAULT_TO = "20080512210044"
DEFAULT_LIMIT = 250
DEFAULT_MAX_ORIGINALS = 20
DEFAULT_MAX_ATTEMPTS = 80
DEFAULT_WINDOW_SECONDS = 1800
DEFAULT_MAX_TOTAL = 128 * 1024 * 1024
DEFAULT_MAX_ENTITY = 16 * 1024 * 1024
DEFAULT_MIN_DISPATCH = 5.1
DEFAULT_MIN_START = 5.0
DEFAULT_MIN_FREE = 11_005_853_696
DEFAULT_PROXY = "http://127.0.0.1:7890"
DEFAULT_COOLDOWN = 120
STOP_HTTP = {429, 503}
IMAGE_MIMES = {"image/jpeg", "image/gif"}
COOLDOWN_STOP_REASONS = {
    "endpoint_status_429",
    "endpoint_status_503",
    "five_consecutive_tls_or_transport_failures",
    "inherited_five_consecutive_tls_or_transport_failures",
}
V2_SCHEMA = "wow-recovery.allnews02"
V2_MODES = {"cdx_only", "replay_only"}
# These are the shared-core defaults.  The v2 driver temporarily clamps the
# imported module before each request and restores the relevant baseline for
# the next request; the shared core file itself remains untouched.
CORE_DEFAULT_DIRECT_CONNECT = 4.0
CORE_DEFAULT_DIRECT_MAX = 12.0
CORE_DEFAULT_PROXY_CONNECT = 8.0
CORE_DEFAULT_PROXY_MAX = 20.0


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_module(CORE_PATH, "allnews02_core_20261016")
gate_mod = load_module(GATE_PATH, "allnews02_gate_20261016")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def disk_free(path: Path = OUT) -> int:
    return int(shutil.disk_usage(path).free)


def rel_root(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def rel_out(path: Path, out: Path = OUT) -> str:
    return path.relative_to(out).as_posix()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative_or_absolute(path: Path) -> str:
    resolved = path.resolve()
    try:
        return rel_root(resolved)
    except ValueError:
        return str(resolved)


def normalize_url_identity(value: str) -> tuple[str, str, int | None, str, str, str] | None:
    """Use the accepted shared-core identity rule without widening it here."""
    return core.normalized_url_identity(value)


def original_match_kind(observed: str, requested: str) -> str | None:
    return core.original_match_kind(observed, requested)


def cdx_query_url(original: str, spec: dict[str, Any]) -> str:
    from_ts = str(spec.get("cdx_from", DEFAULT_FROM))
    to_ts = str(spec.get("cdx_to", DEFAULT_TO))
    limit = int(spec.get("cdx_limit", DEFAULT_LIMIT))
    return (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(original, safe="")
        + f"&from={from_ts}&to={to_ts}&output=json"
        + "&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest%2Clength"
        + f"&limit={limit}&matchType=exact"
    )


def replay_url(capture: dict[str, Any]) -> str:
    return f"https://web.archive.org/web/{capture['timestamp']}id_/{capture['original']}"


def policy(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "max_originals": int(spec.get("max_originals", DEFAULT_MAX_ORIGINALS)),
        "max_attempts": int(spec.get("max_attempts", DEFAULT_MAX_ATTEMPTS)),
        "window_seconds": int(spec.get("window_seconds", DEFAULT_WINDOW_SECONDS)),
        "max_total_body_bytes": int(spec.get("max_total_body_bytes", DEFAULT_MAX_TOTAL)),
        "max_entity_body_bytes": int(spec.get("max_entity_body_bytes", DEFAULT_MAX_ENTITY)),
        "cdx_from": str(spec.get("cdx_from", DEFAULT_FROM)),
        "cdx_to": str(spec.get("cdx_to", DEFAULT_TO)),
        "cdx_limit": int(spec.get("cdx_limit", DEFAULT_LIMIT)),
        "cdx_collapse": False,
        "cdx_match_type": "exact",
        "direct_first": True,
        "proxy_fallback": str(spec.get("proxy", DEFAULT_PROXY)),
        "tls_verification": True,
        "automatic_redirects": 0,
        "min_dispatch_monotonic_seconds": float(spec.get("min_dispatch_monotonic_seconds", DEFAULT_MIN_DISPATCH)),
        "min_request_start_utc_seconds": float(spec.get("min_request_start_utc_seconds", DEFAULT_MIN_START)),
        "disk_floor_bytes": int(spec.get("disk_floor_bytes", DEFAULT_MIN_FREE)),
        "stop_http_codes": sorted(STOP_HTTP),
        "cooldown_seconds_after_stop": int(spec.get("cooldown_seconds", DEFAULT_COOLDOWN)),
        "same_identity_rule": "exact scheme/host/path/query; only default port equivalent",
        "eligible_mime": sorted(IMAGE_MIMES),
        "replay_mode": "replay_only queue entries reuse one saved exact CDX capture; cdx_only entries never replay",
        "remaining_byte_and_time_clamp": True,
    }


def validate_spec_queue(spec: dict[str, Any], queue: dict[str, Any]) -> list[dict[str, Any]]:
    if spec.get("schema") not in {"wow-recovery.allnews02-spec.v2", "wow-recovery.allnews-spec.v1"}:
        raise ValueError("unsupported spec schema")
    if spec.get("cdx_collapse", False) is not False:
        raise ValueError("collapse must be false")
    if int(spec.get("cdx_limit", DEFAULT_LIMIT)) != DEFAULT_LIMIT:
        raise ValueError(f"cdx_limit must be {DEFAULT_LIMIT}")
    if str(spec.get("cdx_match_type", "exact")) != "exact":
        raise ValueError("cdx_match_type must be exact")
    entries = queue.get("entries")
    if not isinstance(entries, list):
        raise ValueError("queue.entries must be a list")
    max_originals = int(spec.get("max_originals", DEFAULT_MAX_ORIGINALS))
    if len(entries) > max_originals:
        raise ValueError(f"queue exceeds max_originals={max_originals}")
    output: list[dict[str, Any]] = []
    keys: set[str] = set()
    originals: set[str] = set()
    for row in entries:
        target_key = str(row.get("target_key") or "")
        original = str(row.get("original") or "")
        if not target_key or target_key in keys:
            raise ValueError(f"duplicate or empty target_key: {target_key!r}")
        if not original or original in originals or normalize_url_identity(original) is None:
            raise ValueError(f"duplicate or invalid original: {original!r}")
        mode = str(row.get("mode") or "")
        if mode not in V2_MODES:
            raise ValueError(f"{target_key}: mode must be one of {sorted(V2_MODES)}")
        saved_capture = row.get("saved_capture")
        if mode == "replay_only":
            if not isinstance(saved_capture, dict):
                raise ValueError(f"{target_key}: replay_only requires saved_capture")
            for field in ("timestamp", "original", "mimetype", "statuscode", "digest"):
                if not str(saved_capture.get(field) or ""):
                    raise ValueError(f"{target_key}: saved_capture missing {field}")
            if original_match_kind(str(saved_capture.get("original")), original) is None:
                raise ValueError(f"{target_key}: saved_capture original identity mismatch")
            if int(saved_capture.get("statuscode")) != 200:
                raise ValueError(f"{target_key}: saved_capture must be status 200")
            if str(saved_capture.get("mimetype", "")).lower().split(";", 1)[0].strip() not in IMAGE_MIMES:
                raise ValueError(f"{target_key}: saved_capture MIME is not an accepted image type")
        keys.add(target_key)
        originals.add(original)
        normalized: dict[str, Any] = {"target_key": target_key, "original": original, "mode": mode}
        if saved_capture is not None:
            normalized["saved_capture"] = dict(saved_capture)
        for field in ("rank", "saved_cdx_source", "saved_cdx_source_sha256"):
            if field in row:
                normalized[field] = row[field]
        output.append(normalized)
    return output


def apply_remaining_clamp(
    state: Any,
    spec: dict[str, Any],
    transport: str,
    *,
    now_monotonic: float | None = None,
    now_utc_value: datetime | None = None,
) -> dict[str, Any]:
    """Clamp core request globals to the bytes/time left in this batch.

    The shared core reads these module globals when it builds curl's command.
    Setting them immediately before ``run_request`` makes the clamp effective
    without changing the shared core or its historical callers.  The returned
    record is persisted in the gate record before transport starts.
    """
    now_mono = time.monotonic() if now_monotonic is None else float(now_monotonic)
    now_dt = datetime.now(timezone.utc) if now_utc_value is None else now_utc_value
    max_total = int(spec.get("max_total_body_bytes", DEFAULT_MAX_TOTAL))
    max_entity = int(spec.get("max_entity_body_bytes", DEFAULT_MAX_ENTITY))
    total_before = int(getattr(state, "total_body_bytes", 0))
    total_remaining = max_total - total_before
    window_seconds = float(spec.get("window_seconds", DEFAULT_WINDOW_SECONDS))
    started_mono = float(getattr(state, "window_started_monotonic", now_mono))
    window_remaining = window_seconds - max(0.0, now_mono - started_mono)
    hard_cutoff = parse_iso(str(spec.get("hard_cutoff_utc") or ""))
    hard_remaining = (hard_cutoff - now_dt).total_seconds() if hard_cutoff else float("inf")
    baseline_connect = CORE_DEFAULT_DIRECT_CONNECT if transport == "direct" else CORE_DEFAULT_PROXY_CONNECT
    baseline_max = CORE_DEFAULT_DIRECT_MAX if transport == "direct" else CORE_DEFAULT_PROXY_MAX
    request_budget = min(baseline_max, window_remaining, hard_remaining)
    if total_remaining <= 0:
        state.stop_reason = state.stop_reason or "total_body_limit"
        state.stop_detail = {"max_total_body_bytes": max_total, "total_body_bytes": total_before}
    if request_budget <= 0:
        state.stop_reason = state.stop_reason or "network_window_exhausted"
        state.stop_detail = {"request_budget_seconds": request_budget, "window_remaining_seconds": window_remaining, "hard_cutoff_remaining_seconds": hard_remaining}
    entity_limit = max(0, min(max_entity, total_remaining))
    effective_connect = max(0.0, min(baseline_connect, request_budget))
    effective_max = max(0.0, request_budget)
    core.MAX_ENTITY_BODY_BYTES = entity_limit
    if transport == "direct":
        core.DIRECT_CONNECT_SECONDS = effective_connect
        core.DIRECT_MAX_SECONDS = effective_max
    else:
        core.PROXY_CONNECT_SECONDS = effective_connect
        core.PROXY_MAX_SECONDS = effective_max
    return {
        "transport": transport,
        "total_body_bytes_before": total_before,
        "total_body_remaining_before_bytes": max(0, total_remaining),
        "configured_entity_body_limit_bytes": max_entity,
        "entity_body_limit_before_bytes": entity_limit,
        "window_seconds": window_seconds,
        "window_remaining_seconds": max(0.0, window_remaining),
        "hard_cutoff_remaining_seconds": max(0.0, hard_remaining) if hard_remaining != float("inf") else None,
        "baseline_connect_timeout_seconds": baseline_connect,
        "baseline_max_timeout_seconds": baseline_max,
        "request_budget_seconds": max(0.0, request_budget),
        "connect_timeout_seconds": effective_connect,
        "max_timeout_seconds": effective_max,
        "clamp_applied": entity_limit < max_entity or effective_max < baseline_max,
        "dispatch_allowed": bool(total_remaining > 0 and request_budget > 0),
    }


def classify_result(mode: str, accepted: bool, cdx_attempts: list[dict[str, Any]], cdx_usable: bool, capture_counts: dict[str, Any] | None, replay_attempts: list[dict[str, Any]]) -> str:
    if accepted:
        return "valid_image"
    if mode == "cdx_only":
        if cdx_usable and capture_counts and capture_counts.get("potential_truncation"):
            return "cdx_potential_truncation"
        if cdx_usable:
            return "cdx_only_observed"
        if cdx_attempts:
            return "cdx_transport_unknown" if all(row.get("source_status") is None for row in cdx_attempts) else "cdx_no_usable_response"
        return "cdx_not_requested"
    if mode == "replay_only":
        if replay_attempts:
            if all(row.get("source_status") is None or row.get("transport_error") for row in replay_attempts):
                return "replay_transport_unknown"
            return "replay_no_valid_payload"
        return "replay_not_requested"
    return "not_requested"


def previous_tail(previous_path: Path | None) -> dict[str, Any]:
    if previous_path is None or not previous_path.exists():
        return {"available": False, "tail_transport_failure_count": 0, "new_batch_streak_starts_at": 0}
    report = load_json(previous_path)
    attempts = list(report.get("attempts") or [])
    trailing = 0
    for row in reversed(attempts):
        if row.get("transport_error"):
            trailing += 1
        else:
            break
    finished = parse_iso(str(report.get("finished_utc") or ""))
    stop_reason = str(report.get("stop_reason") or "")
    cooldown_required = stop_reason in COOLDOWN_STOP_REASONS
    cooldown = int(report.get("policy", {}).get("cooldown_seconds_after_stop", DEFAULT_COOLDOWN))
    ready = finished + timedelta(seconds=cooldown) if finished else None
    current = datetime.now(timezone.utc)
    return {
        "available": True,
        "batch_id": report.get("batch_id"),
        "report_path": rel_root(previous_path),
        "report_sha256": sha256_file(previous_path),
        "last_completed_utc": report.get("finished_utc"),
        "tail_transport_failure_count": trailing,
        "new_batch_streak_starts_at": trailing,
        "previous_stop_reason": stop_reason or None,
        "cooldown_required": cooldown_required,
        "cooldown_ready_utc": ready.isoformat() if ready else None,
        "cooldown_satisfied": (not cooldown_required) or bool(ready and current >= ready),
    }


def restore_failure_streak(records: list[dict[str, Any]], inherited_tail: int) -> dict[str, Any]:
    """Rebuild the current streak without discarding a prior-batch tail.

    An explicit successful/non-transport attempt resets the inherited tail.  If
    the resumed records contain only transfer failures (plus no successful
    source result), their trailing failures continue the prior tail.  A
    dispatch-only reservation is unknown and therefore does not count as a
    success.
    """
    current_tail = 0
    for row in reversed(records):
        if row.get("transport_error") is True:
            current_tail += 1
            continue
        break
    explicit_success = any(row.get("transport_error") is False for row in records)
    inherited = not explicit_success
    restored = current_tail + (int(inherited_tail) if inherited else 0)
    return {
        "inherited_tail": int(inherited_tail),
        "current_records_tail": current_tail,
        "explicit_success_seen": explicit_success,
        "inherited_into_resume": inherited,
        "restored_streak": restored,
    }


def prepare(spec_path: Path, queue_path: Path, out: Path) -> int:
    spec_path = spec_path.resolve()
    queue_path = queue_path.resolve()
    out = out.resolve()
    spec = load_json(spec_path)
    queue = load_json(queue_path)
    entries = validate_spec_queue(spec, queue)
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    if any(raw.iterdir()):
        raise RuntimeError("prepare refuses non-empty raw directory")
    previous_path = Path(spec["previous_report"]) if spec.get("previous_report") else None
    if previous_path and not previous_path.is_absolute():
        previous_path = ROOT / previous_path
    bindings = [
        {"path": relative_or_absolute(spec_path), "sha256": sha256_file(spec_path), "bytes": spec_path.stat().st_size},
        {"path": relative_or_absolute(queue_path), "sha256": sha256_file(queue_path), "bytes": queue_path.stat().st_size},
    ]
    if previous_path and previous_path.exists():
        bindings.append({"path": relative_or_absolute(previous_path), "sha256": sha256_file(previous_path), "bytes": previous_path.stat().st_size})
    normalized_spec = {**spec, "cdx_collapse": False, "cdx_match_type": "exact", "cdx_limit": DEFAULT_LIMIT}
    tasks = [{**entry, "cdx_query_url": cdx_query_url(entry["original"], normalized_spec), "replay_allowed": entry["mode"] == "replay_only"} for entry in entries]
    binding = {"driver_path": relative_or_absolute(Path(__file__)), "driver_sha256": sha256_file(Path(__file__)), "spec": relative_or_absolute(spec_path), "queue": relative_or_absolute(queue_path), "source_files": bindings}
    write_json(out / "queue-normalized.json", {"schema": "wow-recovery.allnews02-queue-normalized.v2", "entries": entries})
    write_json(out / "input-bindings.json", binding)
    preflight = {
        "schema": "wow-recovery.allnews02-preflight.v2",
        "prepared_utc": now_utc(),
        "disk_free_bytes": disk_free(out),
        "minimum_free_bytes": int(normalized_spec.get("disk_floor_bytes", DEFAULT_MIN_FREE)),
        "disk_floor_passed": disk_free(out) >= int(normalized_spec.get("disk_floor_bytes", DEFAULT_MIN_FREE)),
        "previous_batch": previous_tail(previous_path),
        "network_requests": 0,
    }
    write_json(out / "preflight.json", preflight)
    write_json(out / "candidates.json", {"schema": "wow-recovery.allnews02-candidates.v2", "batch_id": normalized_spec.get("batch_id"), "network_requests": 0, "tasks": tasks})
    write_json(out / "config.json", {"schema": "wow-recovery.allnews02-config.v2", "batch_id": normalized_spec.get("batch_id"), "network_requests": 0, "policy": policy(normalized_spec), "input_bindings": binding, "preflight": "preflight.json"})
    replay_target_count = sum(1 for entry in entries if entry["mode"] == "replay_only")
    write_json(out / "plan.json", {"schema": "wow-recovery.allnews02-plan.v2", "mode": "go_ready_offline_only", "batch_id": normalized_spec.get("batch_id"), "prepared_utc": now_utc(), "network_requests": 0, "original_count": len(entries), "modes": {mode: sum(1 for entry in entries if entry["mode"] == mode) for mode in sorted(V2_MODES)}, "replay": replay_target_count > 0, "replay_target_count": replay_target_count, "policy": policy(normalized_spec), "input_bindings": binding, "preflight_sha256": sha256_file(out / "preflight.json"), "execution_requires_parent_go": True})
    print(json.dumps({"mode": "prepared", "batch_id": normalized_spec.get("batch_id"), "original_count": len(entries), "network_requests": 0}, ensure_ascii=False))
    return 0


def validate_prepare_bindings(spec_path: Path, queue_path: Path, out: Path) -> dict[str, Any]:
    binding_path = out / "input-bindings.json"
    if not binding_path.exists():
        raise RuntimeError("input-bindings.json is missing; execute requires the matching prepare")
    binding = load_json(binding_path)
    expected_spec = relative_or_absolute(spec_path)
    expected_queue = relative_or_absolute(queue_path)
    if binding.get("spec") != expected_spec or binding.get("queue") != expected_queue:
        raise RuntimeError("prepare input path mismatch: spec/queue differ from input-bindings.json")
    source_files = {str(row.get("path")): str(row.get("sha256")) for row in binding.get("source_files", []) if isinstance(row, dict)}
    actual_spec_sha = sha256_file(spec_path)
    actual_queue_sha = sha256_file(queue_path)
    if source_files.get(expected_spec) != actual_spec_sha:
        raise RuntimeError("prepare spec SHA mismatch: refusing to execute a different spec")
    if source_files.get(expected_queue) != actual_queue_sha:
        raise RuntimeError("prepare queue SHA mismatch: refusing to execute a different queue")
    driver_path = Path(__file__).resolve()
    if binding.get("driver_path") != relative_or_absolute(driver_path) or binding.get("driver_sha256") != sha256_file(driver_path):
        raise RuntimeError("prepare driver binding mismatch: refusing to execute a changed driver")
    return {
        "binding_path": relative_or_absolute(binding_path),
        "spec_path": expected_spec,
        "queue_path": expected_queue,
        "spec_sha256": actual_spec_sha,
        "queue_sha256": actual_queue_sha,
        "driver_sha256": sha256_file(driver_path),
        "matched": True,
    }


def parse_capture_rows(attempt: dict[str, Any], out: Path = OUT) -> list[dict[str, str]]:
    rows = attempt.get("cdx_records")
    if isinstance(rows, list):
        return [{str(key): str(value) for key, value in row.items()} for row in rows if isinstance(row, dict)]
    raw = attempt.get("raw") or {}
    body_path = out / str(raw.get("body") or "")
    if attempt.get("source_status") != 200 or attempt.get("transport_error") or not body_path.exists():
        return []
    records, okay, error = core.parse_cdx_body(body_path.read_bytes())
    attempt["cdx_parse_valid"] = okay
    attempt["cdx_parse_error"] = error
    attempt["cdx_records"] = records
    return records if okay else []


def select_capture(records: list[dict[str, str]], original: str, spec: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    from_ts = str(spec.get("cdx_from", DEFAULT_FROM))
    to_ts = str(spec.get("cdx_to", DEFAULT_TO))
    limit = int(spec.get("cdx_limit", DEFAULT_LIMIT))
    counts: dict[str, Any] = {"records": len(records), "same_identity": 0, "status_200": 0, "allowed_mime": 0, "preanchor": 0, "eligible": 0, "potential_truncation": len(records) >= limit}
    candidates: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        value = dict(record)
        value["record_index"] = index
        timestamp = str(record.get("timestamp", ""))
        status = int(record.get("statuscode")) if str(record.get("statuscode", "")).isdigit() else None
        mime = str(record.get("mimetype", "")).lower().split(";", 1)[0].strip()
        match = original_match_kind(str(record.get("original", "")), original)
        value["original_match_kind"] = match
        value["statuscode_int"] = status
        value["mimetype_normalized"] = mime
        value["within_query_range"] = bool(re.fullmatch(r"\d{14}", timestamp) and from_ts <= timestamp <= to_ts)
        if match is None:
            continue
        counts["same_identity"] += 1
        if status != 200:
            continue
        counts["status_200"] += 1
        if mime not in IMAGE_MIMES:
            continue
        counts["allowed_mime"] += 1
        if not value["within_query_range"]:
            continue
        counts["preanchor"] += 1
        if not record.get("digest") or not timestamp:
            continue
        counts["eligible"] += 1
        value["replay_authorized"] = True
        candidates.append(value)
    if counts["potential_truncation"]:
        return None, counts
    candidates.sort(key=lambda row: str(row.get("timestamp", "")), reverse=True)
    return (candidates[0] if candidates else None), counts


def parse_header_text(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    text = path.read_text(encoding="iso-8859-1", errors="replace") if path.exists() else ""
    return core.parse_headers(text), core.source_blocks(text)


def response_header(path: Path, name: str) -> str | None:
    _, blocks = parse_header_text(path)
    return core.response_header(blocks, name)


def validate_payload(attempt: dict[str, Any], original: str, capture: dict[str, Any], out: Path = OUT) -> dict[str, Any]:
    raw = attempt.get("raw") or {}
    body_path = out / str(raw.get("body") or "")
    headers_path = out / str(raw.get("headers") or "")
    body = body_path.read_bytes() if body_path.exists() else b""
    _, blocks = parse_header_text(headers_path)
    status = attempt.get("source_status")
    content_type = attempt.get("content_type") or core.response_header(blocks, "content-type")
    mime = str(content_type or "").lower().split(";", 1)[0].strip()
    memento = attempt.get("memento_datetime") or core.memento_iso(core.response_header(blocks, "memento-datetime"))
    link = core.response_header(blocks, "link") or ""
    originals = re.findall(r"<([^>]+)>\s*;\s*rel=[\"']original[\"']", link, flags=re.I)
    original_match = next((original_match_kind(value, original) for value in originals if original_match_kind(value, original) is not None), None)
    digest = base64.b32encode(hashlib.sha1(body).digest()).decode("ascii").rstrip("=") if body else None
    decode: dict[str, Any] = {"verify": "not_run", "load": "not_run", "format": None, "size": None, "mode": None, "frame_count": None, "all_frames_load": "not_run", "error": None}
    pillow_ok = False
    try:
        with Image.open(io.BytesIO(body)) as image:
            decode["format"] = image.format
            decode["size"] = list(image.size)
            decode["mode"] = image.mode
            image.verify()
        decode["verify"] = "passed"
        with Image.open(io.BytesIO(body)) as image:
            if decode["format"] == "GIF":
                frame_count = 0
                for frame in ImageSequence.Iterator(image):
                    frame.load()
                    frame_count += 1
                decode["frame_count"] = frame_count
                decode["all_frames_load"] = "passed"
            else:
                image.load()
                decode["all_frames_load"] = "not_applicable"
        decode["load"] = "passed"
        pillow_ok = decode["format"] in {"JPEG", "GIF"} and bool(decode["size"] and decode["size"][0] and decode["size"][1])
    except Exception as exc:
        decode["error"] = f"{type(exc).__name__}: {exc}"
    expected_mime = str(capture.get("mimetype", "")).lower().split(";", 1)[0].strip()
    valid = bool(
        attempt.get("executed")
        and status == 200
        and not attempt.get("transport_error")
        and memento == core.memento_iso(datetime.strptime(str(capture["timestamp"]), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"))
        and original_match is not None
        and mime == expected_mime
        and pillow_ok
        and digest == capture.get("digest")
    )
    return {
        "valid": valid,
        "source_status": status,
        "transport_error": bool(attempt.get("transport_error")),
        "actual_memento": memento,
        "expected_memento": core.memento_iso(datetime.strptime(str(capture["timestamp"]), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")),
        "original_links": originals,
        "original_match_kind": original_match,
        "mime": mime,
        "expected_mime": expected_mime,
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "cdx_digest_expected": capture.get("digest"),
        "cdx_digest_calculated": digest,
        "cdx_digest_match": digest == capture.get("digest"),
        "decode": decode,
        "raw_body_path": raw.get("body"),
        "raw_headers_path": raw.get("headers"),
    }


def safe_target_key(row: dict[str, Any]) -> str:
    return str(row.get("target_key") or "")


def missing_transports(records: list[dict[str, Any]], target_key: str, kind: str, dispatches: list[dict[str, Any]] | None = None) -> list[str]:
    sent = {str(row.get("transport")) for row in records if row.get("target_key") == target_key and row.get("kind") == kind}
    sent.update(str(row.get("transport")) for row in (dispatches or []) if row.get("target_key") == target_key and row.get("kind") == kind)
    return [transport for transport in ("direct", "proxy") if transport not in sent]


def validate_cadence(dispatches: list[dict[str, Any]], attempts: list[dict[str, Any]], min_dispatch: float = DEFAULT_MIN_DISPATCH, min_start: float = DEFAULT_MIN_START) -> dict[str, Any]:
    dispatch_intervals = [float(dispatches[i]["dispatch_monotonic"]) - float(dispatches[i - 1]["dispatch_monotonic"]) for i in range(1, len(dispatches))]
    starts = [parse_iso(row.get("started_utc")) for row in attempts if parse_iso(row.get("started_utc"))]
    start_intervals = [(starts[i] - starts[i - 1]).total_seconds() for i in range(1, len(starts))]
    return {
        "dispatch_intervals": dispatch_intervals,
        "request_start_intervals": start_intervals,
        "min_dispatch": min(dispatch_intervals) if dispatch_intervals else None,
        "min_start": min(start_intervals) if start_intervals else None,
        "dispatch_passed": not dispatch_intervals or min(dispatch_intervals) >= min_dispatch,
        "start_passed": not start_intervals or min(start_intervals) >= min_start,
    }


def raw_paths_for_attempt(out: Path, attempt: int, target_key: str, kind: str, transport: str) -> dict[str, str]:
    stem = f"{attempt:02d}-{core.safe_name(target_key)}-{kind}-{transport}"
    return {key: f"raw/{stem}.{suffix}" for key, suffix in (("headers", "headers.txt"), ("body", "body"), ("stderr", "stderr.txt"), ("trace", "trace.txt"), ("metrics", "metrics.txt"))}


def persist_attempts(out: Path, records: list[dict[str, Any]]) -> None:
    write_json(out / "attempt-records.json", records)


def recover_orphans(out: Path, journal: dict[str, Any], records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    known = {int(row.get("attempt", 0)) for row in records}
    recovered = list(records)
    for dispatch in journal.get("dispatches", []):
        attempt_number = int(dispatch.get("attempt", 0))
        if attempt_number in known:
            continue
        target_key = str(dispatch.get("target_key") or dispatch.get("target") or "")
        kind = str(dispatch.get("kind") or "")
        transport = str(dispatch.get("transport") or "")
        raw = raw_paths_for_attempt(out, attempt_number, target_key, kind, transport)
        header_path = out / raw["headers"]
        body_path = out / raw["body"]
        if not header_path.exists() and not body_path.exists():
            # The dispatch journal is durable before curl starts.  Reserve this
            # transport on restart so a crash in that gap cannot resubmit it.
            recovered.append({
                "executed": False,
                "attempt": attempt_number,
                "kind": kind,
                "target_key": target_key,
                "transport": transport,
                "url": dispatch.get("url"),
                "dispatch_utc": dispatch.get("dispatch_utc"),
                "dispatch_only": True,
                "transport_error": None,
                "unrequested_reason": "dispatch_persisted_before_transport_no_raw",
                "raw": raw,
            })
            continue
        _, blocks = parse_header_text(header_path)
        metrics_path = out / raw["metrics"]
        stdout = metrics_path.read_text(encoding="ascii", errors="replace").strip() if metrics_path.exists() else ""
        status = core.response_status(blocks, stdout)
        body = body_path.read_bytes() if body_path.exists() else b""
        row: dict[str, Any] = {
            "executed": True,
            "attempt": attempt_number,
            "kind": kind,
            "target_key": target_key,
            "transport": transport,
            "url": dispatch.get("url"),
            "started_utc": dispatch.get("dispatch_utc"),
            "finished_utc": dispatch.get("dispatch_utc"),
            "curl_exit": None,
            "source_status": status,
            "content_type": core.response_header(blocks, "content-type"),
            "location": core.response_header(blocks, "location"),
            "retry_after": core.response_header(blocks, "retry-after"),
            "memento_datetime": core.memento_iso(core.response_header(blocks, "memento-datetime")),
            "redirects_requested": 0,
            "automatic_redirects": 0,
            "body_bytes": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
            "transport_error": status is None,
            "transport_reason": "recovered_from_orphan_raw",
            "raw": raw,
            "meta": dispatch.get("meta") or {},
            "recovered_from_orphan_raw": True,
        }
        if kind == "cdx" and status == 200 and not row["transport_error"]:
            parsed, okay, error = core.parse_cdx_body(body)
            row["cdx_parse_valid"] = okay
            row["cdx_parse_error"] = error
            row["cdx_records"] = parsed
        recovered.append(row)
    recovered.sort(key=lambda row: int(row.get("attempt", 0)))
    persist_attempts(out, recovered)
    return recovered


def apply_cooldown(reason: str | None, seconds: int) -> dict[str, Any]:
    if reason not in {"endpoint_status_429", "endpoint_status_503", "five_consecutive_tls_or_transport_failures", "inherited_five_consecutive_tls_or_transport_failures"}:
        return {"required": False, "seconds": 0, "applied": False}
    started = datetime.now(timezone.utc)
    remaining = float(seconds)
    while remaining > 0:
        sleep_for = min(60.0, remaining)
        time.sleep(sleep_for)
        remaining -= sleep_for
    return {"required": True, "seconds": seconds, "applied": True, "started_utc": started.isoformat(), "finished_utc": now_utc()}


def run_execute(spec: dict[str, Any], queue: list[dict[str, Any]], out: Path, prepare_binding: dict[str, Any] | None = None) -> dict[str, Any]:
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    max_attempts = int(spec.get("max_attempts", DEFAULT_MAX_ATTEMPTS))
    max_total = int(spec.get("max_total_body_bytes", DEFAULT_MAX_TOTAL))
    max_entity = int(spec.get("max_entity_body_bytes", DEFAULT_MAX_ENTITY))
    min_start = float(spec.get("min_request_start_utc_seconds", DEFAULT_MIN_START))
    min_dispatch = float(spec.get("min_dispatch_monotonic_seconds", DEFAULT_MIN_DISPATCH))
    min_free = int(spec.get("disk_floor_bytes", DEFAULT_MIN_FREE))
    proxy = str(spec.get("proxy", DEFAULT_PROXY))
    user_agent = str(spec.get("user_agent", "wow-recovery-allnews01/20261016"))
    core.OUT = out
    core.RAW = raw
    core.PROXY = proxy
    core.USER_AGENT = user_agent
    core.MAX_ATTEMPTS = max_attempts
    core.WINDOW_SECONDS = int(spec.get("window_seconds", DEFAULT_WINDOW_SECONDS))
    core.MIN_INTERVAL_SECONDS = min_start
    core.MIN_FREE_BYTES = min_free
    core.MAX_TOTAL_BODY_BYTES = max_total
    core.MAX_ENTITY_BODY_BYTES = max_entity
    core.DIRECT_CONNECT_SECONDS = CORE_DEFAULT_DIRECT_CONNECT
    core.DIRECT_MAX_SECONDS = CORE_DEFAULT_DIRECT_MAX
    core.PROXY_CONNECT_SECONDS = CORE_DEFAULT_PROXY_CONNECT
    core.PROXY_MAX_SECONDS = CORE_DEFAULT_PROXY_MAX
    core.STOP_HTTP_CODES = STOP_HTTP
    gate_mod.OUT = out
    gate_mod.RAW = raw
    gate_mod.PROXY = proxy
    gate_mod.INTERVAL_SECONDS = min_dispatch
    gate_mod.MIN_FREE_BYTES = min_free
    gate_mod.MAX_TOTAL_BODY_BYTES = max_total
    gate_mod.MAX_ENTITY_BYTES = max_entity
    gate_mod.STOP_HTTP_CODES = STOP_HTTP
    previous_path = Path(spec["previous_report"]) if spec.get("previous_report") else None
    if previous_path and not previous_path.is_absolute():
        previous_path = ROOT / previous_path
    prior_tail = previous_tail(previous_path)
    records = load_json(out / "attempt-records.json") if (out / "attempt-records.json").exists() else []
    journal = load_json(out / "dispatch-log.json") if (out / "dispatch-log.json").exists() else {
        "schema": "wow-recovery.allnews01-dispatch-log.v1",
        "batch_id": spec.get("batch_id"),
        "authorization": "parent ALLNEWS01 GO received",
        "window_started_utc": None,
        "hard_cutoff_utc": spec.get("hard_cutoff_utc"),
        "disk_preflight": {"checked_utc": now_utc(), "disk_free_bytes": disk_free(out), "minimum_free_bytes": min_free, "passed": disk_free(out) >= min_free},
        "dispatches": [],
        "previous_batch": prior_tail,
    }
    journal["window_started_utc"] = journal.get("window_started_utc") or now_utc()
    write_json(out / "dispatch-log.json", journal)
    records = recover_orphans(out, journal, records)
    first = parse_iso(records[0].get("started_utc")) if records else None
    elapsed = max((datetime.now(timezone.utc) - first).total_seconds(), 0.0) if first else 0.0
    state = core.RunState(time.monotonic() - elapsed)
    state.attempts = len(records)
    state.failed_attempts = sum(1 for row in records if row.get("transport_error"))
    state.source_responses = sum(1 for row in records if row.get("source_status") is not None)
    state.total_body_bytes = sum(int(row.get("body_bytes") or 0) for row in records)
    failure_resume = restore_failure_streak(records, int(prior_tail.get("tail_transport_failure_count", 0)))
    state.fail_streak = int(failure_resume["restored_streak"])
    if prior_tail.get("cooldown_required") and not prior_tail.get("cooldown_satisfied"):
        state.stop_reason = "previous_batch_cooldown_not_satisfied"
        state.stop_detail = {
            "previous_stop_reason": prior_tail.get("previous_stop_reason"),
            "cooldown_ready_utc": prior_tail.get("cooldown_ready_utc"),
        }
    elif state.fail_streak >= 5:
        state.stop_reason = "inherited_five_consecutive_tls_or_transport_failures" if not records else "five_consecutive_tls_or_transport_failures"
    gate = gate_mod.GateState(datetime.now(timezone.utc), journal_path=out / "dispatch-log.json", journal=journal)
    gate.dispatches = list(journal.get("dispatches") or [])
    gate.journal["dispatches"] = gate.dispatches
    if gate.dispatches:
        previous_dispatch = parse_iso(gate.dispatches[-1].get("dispatch_utc"))
        if previous_dispatch:
            gate.last_dispatch_mono = time.monotonic() - max((datetime.now(timezone.utc) - previous_dispatch).total_seconds(), 0.0)
    progress_path = out / "progress.json"
    progress = load_json(progress_path) if progress_path.exists() else {"targets": {}}
    network_started = records[0].get("started_utc") if records else None
    network_finished = records[-1].get("finished_utc") if records else None

    def dispatch(url: str, item: dict[str, str], kind: str, transport: str) -> dict[str, Any] | None:
        if datetime.now(timezone.utc) >= datetime.fromisoformat(str(spec.get("hard_cutoff_utc", "9999-12-31T23:59:59+00:00"))):
            state.stop_reason = state.stop_reason or "hard_network_cutoff"
            return None
        if disk_free(out) < min_free:
            state.stop_reason = state.stop_reason or "disk_free_below_threshold"
            return None
        number = state.attempts + 1
        target_key = item["target_key"]
        gate_record = gate.before_dispatch(number, transport, f"{target_key}-{kind}")
        disk_before = disk_free(out)
        gate_record.update({
            "url": url,
            "kind": kind,
            "target_key": target_key,
            "disk_free_before_bytes": disk_before,
            "disk_free_floor_bytes": min_free,
            "disk_free_floor_passed": disk_before >= min_free,
            "meta": {"target_key": target_key, "original": item["original"]},
        })
        clamp = apply_remaining_clamp(state, spec, transport)
        gate_record["clamp"] = clamp
        gate.persist()
        if disk_before < min_free or not clamp["dispatch_allowed"]:
            if not clamp["dispatch_allowed"] and not state.stop_reason:
                state.stop_reason = "request_budget_exhausted"
            state.stop_reason = state.stop_reason or "disk_free_below_threshold"
            state.stop_detail = {"disk_free_before_bytes": disk_before, "minimum_free_bytes": min_free, "dispatch_reserved_without_transport": True}
            records.append({
                "executed": False,
                "attempt": number,
                "kind": kind,
                "target_key": target_key,
                "transport": transport,
                "url": url,
                "dispatch_utc": gate_record.get("dispatch_utc"),
                "dispatch_only": True,
                "transport_error": None,
                "unrequested_reason": "disk_floor_failed_after_dispatch_gate" if disk_before < min_free else "remaining_budget_exhausted_after_dispatch_gate",
                "raw": raw_paths_for_attempt(out, number, target_key, kind, transport),
                "meta": gate_record["meta"],
                "dispatch": gate_record,
                "clamp": clamp,
            })
            state.attempts = number
            persist_attempts(out, records)
            return None
        try:
            attempt = core.run_request(url, transport, kind, target_key, state, number)
            attempt["dispatch"] = gate_record
            attempt["meta"] = gate_record["meta"]
            attempt["clamp"] = clamp
            records.append(attempt)
            persist_attempts(out, records)
            return attempt
        except Exception:
            journal["last_exception_utc"] = now_utc()
            journal["last_exception_target_key"] = target_key
            journal["last_exception_traceback"] = traceback.format_exc()
            gate.persist()
            raise

    try:
        for item in queue:
            target_key = item["target_key"]
            if target_key in progress.get("targets", {}):
                continue
            mode = str(item["mode"])
            cdx_attempts: list[dict[str, Any]] = []
            capture = None
            capture_counts: dict[str, Any] | None = None
            cdx_records: list[dict[str, str]] = []
            cdx_usable = False
            if mode == "replay_only":
                # The previous ALLNEWS01 CDX is a frozen local input.  This
                # mode deliberately spends attempts on replay only.
                capture = dict(item["saved_capture"])
                capture_counts = {"reused_saved_cdx": True, "potential_truncation": False, "records": 1}
                cdx_usable = True
            else:
                cdx_prior = [row for row in records if row.get("kind") == "cdx" and row.get("target_key") == target_key]
                cdx_attempts = list(cdx_prior)
                for row in cdx_prior:
                    if row.get("source_status") == 200 and not row.get("transport_error") and row.get("cdx_parse_valid"):
                        cdx_records = parse_capture_rows(row, out)
                        capture, capture_counts = select_capture(cdx_records, item["original"], spec)
                        cdx_usable = True
                        break
                if not cdx_usable and not state.stop_reason:
                    sent = {str(row.get("transport")) for row in cdx_prior}
                    sent.update(str(row.get("transport")) for row in journal.get("dispatches", []) if row.get("target_key") == target_key and row.get("kind") == "cdx")
                    for transport in ("direct", "proxy"):
                        if transport in sent or state.stop_reason:
                            continue
                        attempt = dispatch(cdx_query_url(item["original"], spec), item, "cdx", transport)
                        if attempt is None:
                            break
                        network_started = network_started or attempt.get("started_utc")
                        network_finished = attempt.get("finished_utc") or network_finished
                        cdx_attempts.append(attempt)
                        if attempt.get("source_status") in STOP_HTTP:
                            break
                        if attempt.get("source_status") == 200 and not attempt.get("transport_error") and attempt.get("cdx_parse_valid"):
                            cdx_records = parse_capture_rows(attempt, out)
                            capture, capture_counts = select_capture(cdx_records, item["original"], spec)
                            cdx_usable = True
                            break
            replay_attempts = [row for row in records if row.get("kind") == "replay" and row.get("target_key") == target_key]
            validation = None
            accepted = False
            if mode == "replay_only" and capture:
                sent_replays = {str(row.get("transport")) for row in replay_attempts}
                sent_replays.update(str(row.get("transport")) for row in journal.get("dispatches", []) if row.get("target_key") == target_key and row.get("kind") == "replay")
                for row in replay_attempts:
                    validation = validate_payload(row, item["original"], capture, out)
                    if validation["valid"]:
                        accepted = True
                        break
                if not accepted and not state.stop_reason:
                    for transport in ("direct", "proxy"):
                        if transport in sent_replays or state.stop_reason:
                            continue
                        attempt = dispatch(replay_url(capture), item, "replay", transport)
                        if attempt is None:
                            break
                        network_started = network_started or attempt.get("started_utc")
                        network_finished = attempt.get("finished_utc") or network_finished
                        replay_attempts.append(attempt)
                        validation = validate_payload(attempt, item["original"], capture, out)
                        if validation["valid"]:
                            accepted = True
                            break
                        if attempt.get("source_status") in STOP_HTTP:
                            break
            result = {
                "target_key": target_key,
                "original": item["original"],
                "mode": mode,
                "cdx_query_url": cdx_query_url(item["original"], spec),
                "cdx_attempts": [core.source_attempt_view(row) for row in cdx_attempts],
                "cdx_record_count": len(cdx_records),
                "cdx_counts": capture_counts,
                "selected_capture": capture,
                "replay_attempts": [core.source_attempt_view(row) for row in replay_attempts],
                "validation": validation,
                "accepted": accepted,
                "category": classify_result(mode, accepted, cdx_attempts, cdx_usable, capture_counts, replay_attempts),
            }
            progress.setdefault("targets", {})[target_key] = result
            write_json(progress_path, progress)
            if state.stop_reason:
                break
    finally:
        journal["disk_postflight"] = {"checked_utc": now_utc(), "disk_free_bytes": disk_free(out), "attempts_count": state.attempts, "persisted_in_finally": True}
        journal["final_attempt_count"] = state.attempts
        gate.persist()
    if not state.stop_reason:
        state.stop_reason = "completed"
    cooldown = apply_cooldown(state.stop_reason, int(spec.get("cooldown_seconds", DEFAULT_COOLDOWN)))
    all_results = [progress.get("targets", {}).get(item["target_key"]) for item in queue]
    all_results = [row for row in all_results if row]
    accepted = []
    for result in all_results:
        if result.get("accepted"):
            capture = result["selected_capture"]
            validation = result["validation"]
            accepted.append({"target_key": result["target_key"], "logical_url": result["original"], "captured_original_url": capture["original"], "capture_timestamp": capture["timestamp"], "actual_memento": validation["actual_memento"], "mime": validation["mime"], "body_bytes": validation["body_bytes"], "body_sha256": validation["body_sha256"], "cdx_digest": capture["digest"], "cdx_digest_calculated": validation["cdx_digest_calculated"], "raw_body_path": validation["raw_body_path"], "raw_headers_path": validation["raw_headers_path"], "decode": validation["decode"], "integration": "source evidence only; integration held"})
    attempts = [row for row in records]
    cadence = validate_cadence(journal.get("dispatches") or [], attempts, min_dispatch, min_start)
    report = {
        "schema": "wow-recovery.allnews02-batch-report.v2",
        "batch_id": spec.get("batch_id"),
        "mode": "executed",
        "started_utc": network_started,
        "finished_utc": network_finished or now_utc(),
        "unique_original_count": len(queue),
        "source_request_count": state.attempts,
        "source_response_count": state.source_responses,
        "failed_attempt_count": state.failed_attempts,
        "total_body_bytes": state.total_body_bytes,
        "valid_image_count": len(accepted),
        "results": all_results,
        "source_map_entries": accepted,
        "attempts": [core.source_attempt_view(row) for row in attempts],
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "rate_limit": state.rate_limit,
        "cooldown": cooldown,
        "previous_batch": prior_tail,
        "failure_streak_resume": failure_resume,
        "prepare_input_bindings": prepare_binding,
        "disk_preflight": journal.get("disk_preflight"),
        "disk_postflight": journal.get("disk_postflight"),
        "cadence": cadence,
        "policy": policy(spec),
        "raw_evidence_note": "Raw CDX/replay headers, bodies, stderr and traces remain local; no automatic redirects or integration.",
    }
    write_json(out / "batch-report.json", report)
    write_json(out / "source-map.json", {"schema": "wow-recovery.allnews02-source-map.v2", "batch_id": spec.get("batch_id"), "integration_held": True, "entries": accepted})
    write_json(out / "sanitized-summary.json", {"schema": "wow-recovery.allnews02-sanitized-summary.v2", "batch_id": spec.get("batch_id"), "source_request_count": state.attempts, "source_response_count": state.source_responses, "failed_attempt_count": state.failed_attempts, "valid_image_count": len(accepted), "stop_reason": state.stop_reason, "cooldown": cooldown, "cadence": cadence, "results": [{"target_key": row["target_key"], "original": row["original"], "mode": row["mode"], "category": row["category"], "accepted": row["accepted"], "selected_capture": row["selected_capture"], "validation": row["validation"]} for row in all_results]})
    journal["report_written_utc"] = now_utc()
    journal["report_sha256"] = sha256_file(out / "batch-report.json")
    write_json(out / "dispatch-log.json", journal)
    return report


def execute(spec_path: Path, queue_path: Path, out: Path) -> int:
    spec_path = spec_path.resolve()
    queue_path = queue_path.resolve()
    out = out.resolve()
    if (out / "batch-report.json").exists():
        raise RuntimeError("refusing rerun: batch-report.json already exists")
    binding = validate_prepare_bindings(spec_path, queue_path, out)
    spec = load_json(spec_path)
    queue = validate_spec_queue(spec, load_json(queue_path))
    if not (out / "plan.json").exists():
        raise RuntimeError("--prepare is required before --execute")
    report = run_execute(spec, queue, out, binding)
    print(json.dumps({"mode": "executed", "batch_id": report["batch_id"], "network_requests": report["source_request_count"], "valid_images": report["valid_image_count"], "stop_reason": report["stop_reason"], "min_dispatch": report["cadence"]["min_dispatch"], "min_request_start": report["cadence"]["min_start"]}, ensure_ascii=False))
    return 0


def main() -> int:
    global OUT, RAW
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if bool(args.prepare) == bool(args.execute):
        parser.error("choose exactly one of --prepare or --execute")
    OUT = args.out.resolve()
    RAW = OUT / "raw"
    if args.prepare:
        return prepare(args.spec, args.queue, args.out)
    return execute(args.spec, args.queue, args.out)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        error_out = OUT
        error_out.mkdir(parents=True, exist_ok=True)
        (error_out / "exception.json").write_text(json.dumps({"schema": "wow-recovery.allnews01-exception.v1", "occurred_utc": now_utc(), "type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"allnews_driver: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

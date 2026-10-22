"""Root-GO-gated retrieval of three pinned Coolwow2 JPEG Git blobs.

Offline fixture mode and preparation do not make HTTP requests.  Execution is
only available through ``--execute --go PATH`` and runs the worker beneath a
real Windows process-tree watchdog.  The transport implementation is imported
from the previously reviewed ArchiveCraft bounded downloader.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PLAN = OUT / "plan.json"
SELECTION = OUT / "source-selection.json"
TREE = ROOT / "research/continuous-recovery-20261022/coolwow2-selected-source-tree.json"
SOURCE_LEAD = ROOT / "research/continuous-recovery-20261022/coolwow2-source-lead.json"
BINDINGS = OUT / "input-bindings.json"
FIXTURE_SPEC = OUT / "offline-fixture-spec.json"
OFFLINE_VALIDATION = OUT / "offline-validation.json"
RUNTIME = OUT / "runtime"
WATCHDOG_DIR = OUT / "parent-watchdog-attempt01"
GO_REL = "research/continuous-recovery-20261022/root-coolwow2-item-icons01-go.json"
TRANSPORT_PATH = ROOT / "research/continuous-recovery-20261022/network/archivecraft-dungeons01/archivecraft_dungeons01.py"
PROXY = "http://127.0.0.1:7890"
BATCH_ID = "coolwow2-item-icons01"
PIN = "09c52b7673871b8048da92e5a13ed753fc08162f"
CADENCE = 6.2
MAX_LOGICAL = 3
MAX_ATTEMPTS = 6
WORKER_SECONDS = 220.0
PARENT_SECONDS = 240.0
WORKER_WATCHDOG_SECONDS = 225.0  # reserves up to 15 seconds for tree kill and receipt flush
REQUEST_SECONDS = 30.0
CONNECT_SECONDS = 10
PER_OBJECT_CAP = 1_048_576
TOTAL_CAP = 6_291_456
DISK_FLOOR = 11_005_853_696
MIN_COOLDOWN = 120
MAX_TRANSPORT_FAILURES = 5
STOP_HTTP = {429, 503}

TARGETS: list[dict[str, Any]] = [
    {
        "target_id": "coolwow2-item-icon-scroll-03",
        "repository_path": "images/item_icons/INV_Scroll_03.jpg",
        "expected_git_blob_sha1": "937b4f2d28526b5ab7ff8828af54095d204a970c",
        "expected_bytes": 1090,
    },
    {
        "target_id": "coolwow2-item-icon-scroll-06",
        "repository_path": "images/item_icons/INV_Scroll_06.jpg",
        "expected_git_blob_sha1": "ffa4f6e3dcb75d3ae0a0cb0f06380f29aaba4458",
        "expected_bytes": 1262,
    },
    {
        "target_id": "coolwow2-item-icon-wand-11",
        "repository_path": "images/item_icons/INV_Wand_11.jpg",
        "expected_git_blob_sha1": "660cbee0f7d36d9bdc8d2c67640c16e4e21f7fd2",
        "expected_bytes": 1235,
    },
]
for _target in TARGETS:
    _target["url"] = f"https://raw.githubusercontent.com/boom8866/coolwow2/{PIN}/{_target['repository_path']}"
    _target["mime_expected"] = "image/jpeg"


def import_transport():
    name = "archivecraft_dungeons01_reused_transport"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, TRANSPORT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load reviewed transport helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


TRANSPORT = import_transport()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def disk_free() -> int:
    return TRANSPORT.disk_free()


def require_disk(stage: str) -> int:
    free = disk_free()
    if free < DISK_FLOOR:
        raise RuntimeError(f"disk floor failed at {stage}: {free} < {DISK_FLOOR}")
    return free


def require_runtime_absent(runtime_path: Path) -> None:
    if runtime_path.exists():
        raise RuntimeError(f"refusing pre-existing runtime: {runtime_path}")


def target_projection(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "target_id": item["target_id"],
            "repository_path": item["repository_path"],
            "url": item["url"],
            "expected_git_blob_sha1": item["expected_git_blob_sha1"],
            "expected_bytes": item["expected_bytes"],
            "mime": item["mime_expected"],
        }
        for item in items
    ]


def validate_static_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    plan = load_json(PLAN)
    selection = load_json(SELECTION)
    tree = load_json(TREE)
    binding = load_json(BINDINGS)
    if plan.get("batch_id") != BATCH_ID or plan.get("mode") != "prepared_only" or plan.get("root_go_required") is not True:
        raise RuntimeError("plan is not prepared and root-GO gated")
    if plan.get("network_requests_at_prepare") != 0 or selection.get("network_requests") != 0:
        raise RuntimeError("prepare-time request count is not zero")
    if plan.get("source_selection_sha256") != sha256_file(SELECTION):
        raise RuntimeError("plan's source-selection digest does not match")
    if plan.get("selected_source_tree_sha256") != sha256_file(TREE):
        raise RuntimeError("plan's selected-tree digest does not match")
    if plan.get("source_lead_sha256") != sha256_file(SOURCE_LEAD):
        raise RuntimeError("plan's preliminary source-lead digest does not match")
    if tree.get("commit_sha") != PIN or tree.get("tree_truncated") is not False:
        raise RuntimeError("selected source tree pin or truncation flag changed")
    if tree.get("git_tree_sha") != plan.get("selected_source_git_tree_sha"):
        raise RuntimeError("selected Git tree object does not match the plan")
    if tree.get("original_capture_timestamp") is not None:
        raise RuntimeError("source record unexpectedly asserts an original capture time")
    selected = {
        (item.get("path"), item.get("sha"), item.get("size"))
        for item in tree.get("selected_entries", [])
        if isinstance(item, dict)
    }
    expected = {(item["repository_path"], item["expected_git_blob_sha1"], item["expected_bytes"]) for item in TARGETS}
    if selected != expected:
        raise RuntimeError("exact target paths/blob IDs/lengths do not match primary selected-tree entries")
    if selection.get("repository", {}).get("pinned_commit") != PIN:
        raise RuntimeError("source selection pin changed")
    primary = selection.get("primary_repository_tree_evidence", {})
    if (
        primary.get("path") != "research/continuous-recovery-20261022/coolwow2-selected-source-tree.json"
        or primary.get("sha256") != sha256_file(TREE)
        or primary.get("git_tree_sha") != tree.get("git_tree_sha")
        or primary.get("original_capture_timestamp") is not None
    ):
        raise RuntimeError("primary selected-tree evidence binding changed")
    selection_targets = selection.get("targets")
    if not isinstance(selection_targets, list) or len(selection_targets) != len(TARGETS):
        raise RuntimeError("source-selection target roster changed")
    if plan.get("targets") != target_projection(TARGETS):
        raise RuntimeError("plan target roster differs from fixed target list")
    for planned, selected_target in zip(TARGETS, selection_targets, strict=True):
        if (
            selected_target.get("repository_path") != planned["repository_path"]
            or selected_target.get("blob_sha1") != planned["expected_git_blob_sha1"]
            or selected_target.get("expected_bytes") != planned["expected_bytes"]
            or selected_target.get("raw_url") != planned["url"]
            or selected_target.get("evidence_origin") != "coolwow2-selected-source-tree.json selected_entries"
        ):
            raise RuntimeError("source-selection target differs from primary tree evidence")
    policy = plan.get("policy", {})
    fixed_policy = {
        "maximum_logical_requests": MAX_LOGICAL,
        "maximum_http_attempts": MAX_ATTEMPTS,
        "maximum_seconds_hard_parent": int(PARENT_SECONDS),
        "maximum_seconds_worker_target": int(WORKER_SECONDS),
        "per_request_timeout_seconds": int(REQUEST_SECONDS),
        "connect_timeout_seconds": CONNECT_SECONDS,
        "minimum_actual_request_start_interval_seconds": CADENCE,
        "dispatch_spacing_seconds": CADENCE,
        "maximum_entity_bytes_per_target": PER_OBJECT_CAP,
        "maximum_total_response_body_bytes": TOTAL_CAP,
        "disk_floor_bytes": DISK_FLOOR,
        "proxy": PROXY,
        "tls_verification": True,
        "transport_order": ["direct", "process-local proxy only after direct transport failure"],
        "curl_retry_count": 0,
        "redirects_followed": False,
        "pagination": False,
        "429_503_immediate_stop": True,
        "cooldown_minimum_seconds": MIN_COOLDOWN,
        "retry_after_respected": True,
        "stop_after_consecutive_transport_failures": MAX_TRANSPORT_FAILURES,
        "failure_tail_preserved": True,
        "raw_headers_cookies_stderr_private": True,
        "public_summary_excludes_raw_headers_cookies_and_commands": True,
    }
    for key, value in fixed_policy.items():
        if policy.get(key) != value:
            raise RuntimeError(f"policy mismatch: {key}")
    if plan.get("maximum_per_target_attempts") != 2:
        raise RuntimeError("per-target attempt cap changed")
    if plan.get("accepted_transport_reference", {}).get("sha256") != sha256_file(TRANSPORT_PATH):
        raise RuntimeError("reviewed transport helper hash changed")
    binding_values = {
        "plan_sha256": sha256_file(PLAN),
        "wrapper_sha256": sha256_file(Path(__file__)),
        "accepted_transport_runner_sha256": sha256_file(TRANSPORT_PATH),
        "source_selection_sha256": sha256_file(SELECTION),
        "selected_source_tree_sha256": sha256_file(TREE),
        "source_lead_sha256": sha256_file(SOURCE_LEAD),
        "fixture_sha256": sha256_file(FIXTURE_SPEC),
        "offline_validation_sha256": sha256_file(OFFLINE_VALIDATION),
    }
    for key, value in binding_values.items():
        if binding.get(key) != value:
            raise RuntimeError(f"input binding mismatch: {key}")
    if binding.get("targets") != target_projection(TARGETS):
        raise RuntimeError("input-binding target projection changed")
    if binding.get("network_requests_at_prepare") != 0:
        raise RuntimeError("input-binding prepare-time request count is nonzero")
    if plan.get("source_lead_role") != "preliminary screening only; the selected tree is primary for all three exact blobs":
        raise RuntimeError("source-lead role boundary changed")
    if plan.get("repository_commit_date_utc") != tree.get("commit_date_utc"):
        raise RuntimeError("repository commit date differs from selected-tree record")
    require_disk("static input validation")
    return plan, selection, tree, binding


def validate_go(go_path: Path, *, runtime_path: Path = RUNTIME) -> tuple[dict[str, Any], dict[str, Any]]:
    plan, _, _, binding = validate_static_inputs()
    require_runtime_absent(runtime_path)
    if not go_path.is_file() or go_path.resolve() != (ROOT / GO_REL).resolve():
        raise RuntimeError("GO missing or not at the fixed plan path")
    go = load_json(go_path)
    contract = plan["go_contract"]
    expected_true = contract["required_true_fields"]
    for key in expected_true:
        if go.get(key) is not True:
            raise RuntimeError(f"GO lacks explicit authorization field: {key}")
    hashes = {
        "plan_sha256": sha256_file(PLAN),
        "wrapper_sha256": sha256_file(Path(__file__)),
        "accepted_transport_runner_sha256": sha256_file(TRANSPORT_PATH),
        "source_selection_sha256": sha256_file(SELECTION),
        "selected_source_tree_sha256": sha256_file(TREE),
        "input_bindings_sha256": sha256_file(BINDINGS),
        "fixture_sha256": sha256_file(FIXTURE_SPEC),
        "offline_validation_sha256": sha256_file(OFFLINE_VALIDATION),
        "source_lead_sha256": sha256_file(SOURCE_LEAD),
    }
    for key in contract["required_hash_fields"]:
        if go.get(key) != hashes.get(key):
            raise RuntimeError(f"GO hash mismatch: {key}")
    if go.get("batch_id") != BATCH_ID:
        raise RuntimeError("GO batch ID mismatch")
    for key, expected_value in contract["expected"].items():
        if go.get(key) != expected_value:
            raise RuntimeError(f"GO policy mismatch: {key}")
    if go.get("maximum_body_bytes") != TOTAL_CAP:
        raise RuntimeError("GO body cap mismatch")
    if go.get("free_bytes_before", 0) < DISK_FLOOR or require_disk("GO preflight") < DISK_FLOOR:
        raise RuntimeError("disk space below GO floor")
    valid_until = go.get("valid_until")
    if not isinstance(valid_until, str) or datetime.fromisoformat(valid_until.replace("Z", "+00:00")) <= utc_now():
        raise RuntimeError("GO expired or missing valid_until")
    for key in contract["required_numeric_fields"]:
        value = go.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise RuntimeError(f"GO numeric authorization field missing: {key}")
    if go.get("go_id") in (None, ""):
        raise RuntimeError("GO must have a unique go_id")
    return plan, go


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def validate_jpeg(data: bytes) -> dict[str, Any]:
    from PIL import Image

    with Image.open(io.BytesIO(data)) as image:
        fmt = image.format
        width, height = image.size
        frames = int(getattr(image, "n_frames", 1))
        image.verify()
    with Image.open(io.BytesIO(data)) as image:
        if int(getattr(image, "n_frames", 1)) != frames:
            raise ValueError("frame count changed between verify and load")
        for index in range(frames):
            image.seek(index)
            image.load()
    if fmt != "JPEG":
        raise ValueError(f"decoded format is {fmt!r}, expected JPEG")
    return {"format": fmt, "width": width, "height": height, "frames": frames, "all_frames_loaded": True}


def validate_payload(target: dict[str, Any], record: dict[str, Any], data: bytes) -> tuple[bool, str, dict[str, Any]]:
    meta = record.get("header_parse", {})
    content_type = (meta.get("content_type") or "").split(";", 1)[0].strip().lower()
    actual_git_sha1 = git_blob_sha1(data)
    observed = {
        "content_type": content_type or None,
        "body_bytes": len(data),
        "body_sha256": sha256_bytes(data),
        "git_blob_sha1": actual_git_sha1,
        "expected_git_blob_sha1": target["expected_git_blob_sha1"],
        "expected_bytes": target["expected_bytes"],
        "content_length_header": meta.get("content_length"),
    }
    if record.get("http_status") != 200 or record.get("returncode") != 0:
        return False, "http_status_or_curl_exit_not_200", observed
    if content_type != "image/jpeg":
        return False, "unexpected_content_type", observed
    if len(data) != target["expected_bytes"]:
        return False, "exact_byte_length_mismatch", observed
    if meta.get("content_length") not in (None, len(data)):
        return False, "content_length_header_mismatch", observed
    if actual_git_sha1 != target["expected_git_blob_sha1"]:
        return False, "git_blob_sha1_mismatch", observed
    try:
        observed["jpeg"] = validate_jpeg(data)
    except Exception as exc:
        observed["jpeg_error_type"] = type(exc).__name__
        return False, "jpeg_integrity_failed", observed
    return True, "accepted", observed


def public_attempt(target: dict[str, Any], record: dict[str, Any], *, accepted: bool, reason: str, validation: dict[str, Any] | None) -> dict[str, Any]:
    base = {
        "target_id": target["target_id"],
        "repository_path": target["repository_path"],
        "url": target["url"],
        "repository": "boom8866/coolwow2",
        "commit": PIN,
        "repository_commit_date_utc": "2015-12-16T16:29:03Z",
        "original_capture_timestamp": None,
        "observed_at_utc": record.get("request_finished_utc"),
        "request_started_utc": record.get("request_started_utc"),
        "request_finished_utc": record.get("request_finished_utc"),
        "actual_start_interval_seconds": record.get("actual_start_interval_seconds"),
        "http_status": record.get("http_status"),
        "transport": record.get("transport"),
        "effective_url": record.get("effective_url") if record.get("effective_url") == target["url"] else None,
        "accepted": accepted,
        "reason": reason,
        "raw_http_private": True,
    }
    if validation:
        base.update(validation)
    return base


def run_batch(
    targets: list[dict[str, Any]],
    paths,
    *,
    max_attempts: int = MAX_ATTEMPTS,
    max_seconds: float = WORKER_SECONDS,
    cadence_seconds: float = CADENCE,
) -> dict[str, Any]:
    if len(targets) > MAX_LOGICAL or len({item["url"] for item in targets}) != len(targets):
        raise RuntimeError("logical target cap exceeded or duplicate URL")
    paths.runtime.mkdir(parents=True, exist_ok=False)
    paths.private.mkdir(parents=True, exist_ok=True)
    paths.raw.mkdir(parents=True, exist_ok=True)
    require_disk("batch start")
    started_utc = iso_now()
    batch_start = time.monotonic()
    attempts: list[dict[str, Any]] = []
    public: list[dict[str, Any]] = []
    total_bytes = 0
    transport_streak = 0
    failure_history: list[dict[str, Any]] = []
    last_start: float | None = None
    stop_reason = "completed"
    cooldown: str | None = None
    stop_batch = False
    per_target_body: dict[str, int] = {}

    for target in targets:
        success = False
        target_body = 0
        per_target_body[target["target_id"]] = 0
        for transport_name in ("direct", "proxy"):
            if len(attempts) >= max_attempts:
                stop_reason = "maximum_http_attempts_reached"
                stop_batch = True
                break
            remaining = min(PER_OBJECT_CAP - target_body, TOTAL_CAP - total_bytes)
            if remaining <= 0:
                stop_reason = "response_body_budget_exhausted"
                stop_batch = True
                break
            if transport_name == "proxy" and not attempts:
                raise RuntimeError("proxy attempt lacks a direct failure")
            record, last_start = TRANSPORT.run_attempt(
                {"target_id": target["target_id"], "url": target["url"]},
                len(attempts) + 1,
                transport_name == "proxy",
                last_start,
                batch_start,
                remaining,
                paths,
                cadence_seconds=cadence_seconds,
                batch_seconds=max_seconds,
            )
            attempts.append(record)
            response_bytes = int(record.get("body_bytes", 0))
            total_bytes += response_bytes
            target_body += response_bytes
            per_target_body[target["target_id"]] = target_body
            status_stop, suggested_cooldown = TRANSPORT.handle_status(record)
            if status_stop:
                stop_reason = status_stop
                cooldown = suggested_cooldown
                public.append(public_attempt(target, record, accepted=False, reason=status_stop, validation=None))
                stop_batch = True
                break
            if record.get("transport_failed") is True:
                transport_streak += 1
                failure_history.append(
                    {
                        "attempt": record["attempt"],
                        "target_id": target["target_id"],
                        "transport": record["transport"],
                        "request_started_utc": record["request_started_utc"],
                        "request_finished_utc": record["request_finished_utc"],
                        "http_status": record.get("http_status"),
                        "returncode": record.get("returncode"),
                        "timed_out": record.get("timed_out"),
                        "body_bytes": response_bytes,
                    }
                )
                if transport_streak >= MAX_TRANSPORT_FAILURES:
                    stop_reason = "five_consecutive_transport_failures"
                    cooldown = TRANSPORT.cooldown_from_record(record, MIN_COOLDOWN)
                    public.append(public_attempt(target, record, accepted=False, reason=stop_reason, validation=None))
                    stop_batch = True
                    break
                if transport_name == "direct":
                    continue
                public.append(public_attempt(target, record, accepted=False, reason="direct_and_proxy_transport_failed", validation=None))
                break

            # Any completed HTTP transaction breaks the consecutive transport-failure streak.
            transport_streak = 0
            if record.get("http_status") != 200:
                stop_reason = "http_status_not_200"
                public.append(public_attempt(target, record, accepted=False, reason=stop_reason, validation=None))
                stop_batch = True
                break
            body_path = Path(record["_body_file"])
            data = body_path.read_bytes()
            accepted, reason, validation = validate_payload(target, record, data)
            public.append(public_attempt(target, record, accepted=accepted, reason=reason, validation=validation))
            if not accepted:
                stop_reason = f"payload_validation_failed:{reason}"
                stop_batch = True
                break
            success = True
            break
        if stop_batch:
            break
        if not success and not any(item["target_id"] == target["target_id"] for item in public):
            public.append({"target_id": target["target_id"], "repository_path": target["repository_path"], "accepted": False, "reason": "not_fetched"})

    finished_utc = iso_now()
    private_report = {
        "schema": f"wow-recovery.{BATCH_ID}.private-report.v1",
        "batch_id": BATCH_ID,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "attempt_count": len(attempts),
        "logical_count": len(public),
        "total_body_bytes": total_bytes,
        "per_target_body_bytes": per_target_body,
        "stop_reason": stop_reason,
        "cooldown_not_before_utc": cooldown,
        "transport_failure_streak_end": transport_streak,
        "transport_failure_history_preserved": failure_history,
        "attempts": attempts,
        "raw_http_private": True,
        "cookies_private": True,
        "inherited_transport_streak": 0,
        "gate_boundary": "The prior Wayback 429 gate remains untouched; this is a separate pinned GitHub raw-content batch.",
    }
    public_summary = {
        "schema": f"wow-recovery.{BATCH_ID}.public-images.v1",
        "batch_id": BATCH_ID,
        "repository": "boom8866/coolwow2",
        "commit": PIN,
        "git_tree_sha": "5b3f74d7522aee7d57f8f9b554570a272836e869",
        "repository_commit_date_utc": "2015-12-16T16:29:03Z",
        "original_capture_timestamp": None,
        "complete": stop_reason == "completed" and len(public) == len(targets),
        "stop_reason": stop_reason,
        "cooldown_not_before_utc": cooldown,
        "attempt_count": len(attempts),
        "logical_count": len(public),
        "total_body_bytes": total_bytes,
        "records": public,
        "provenance_boundary": "Repository blob identity/commit history only; no original capture time, page association, historic screenshot claim, or in-game semantic mapping.",
        "raw_http_private": True,
        "network_requests_at_prepare": 0,
    }
    require_disk("before private report write")
    write_json(paths.report, private_report)
    require_disk("before public image summary write")
    write_json(paths.public, public_summary)
    require_disk("after batch outputs")
    return {"stop_reason": stop_reason, "cooldown_not_before_utc": cooldown, "attempt_count": len(attempts), "total_body_bytes": total_bytes, "records": public, "private_report": private_report}


def validate_execution_inputs(go_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    plan, go = validate_go(go_path)
    if not OFFLINE_VALIDATION.is_file() or load_json(OFFLINE_VALIDATION).get("all_passed") is not True:
        raise RuntimeError("offline validation is missing or failed")
    if load_json(OFFLINE_VALIDATION).get("network_requests") != 0:
        raise RuntimeError("offline fixture network request count is nonzero")
    if not WATCHDOG_DIR.is_dir():
        raise RuntimeError("parent watchdog marker absent; worker cannot run directly")
    marker_path = WATCHDOG_DIR / "go-consumed.json"
    if not marker_path.is_file():
        raise RuntimeError("parent watchdog GO marker is absent")
    marker = load_json(marker_path)
    if marker.get("go_sha256") != sha256_file(go_path) or marker.get("go_id") != go.get("go_id"):
        raise RuntimeError("parent watchdog marker does not bind this GO")
    if marker.get("parent_pid") != os.getppid():
        raise RuntimeError("worker was not launched by the GO-consuming parent watchdog")
    return plan, go


def worker_entry(go_path: Path) -> int:
    try:
        validate_execution_inputs(go_path)
        require_runtime_absent(RUNTIME)
        paths = TRANSPORT.make_paths(RUNTIME)
        result = run_batch(TARGETS, paths)
        return 0 if result["stop_reason"] == "completed" else 2
    except Exception as exc:
        if RUNTIME.exists():
            paths = TRANSPORT.make_paths(RUNTIME)
            require_disk("before error report")
            write_json(
                paths.report,
                {
                    "schema": f"wow-recovery.{BATCH_ID}.private-report.v1",
                    "batch_id": BATCH_ID,
                    "finished_utc": iso_now(),
                    "stop_reason": "worker_exception",
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                    "raw_http_private": True,
                },
            )
        return 3


def kill_process_tree(process: subprocess.Popen[bytes]) -> str:
    method = "process.kill"
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            method = "taskkill_tree"
        except Exception:
            method = "taskkill_failed_then_process_kill"
    if process.poll() is None:
        process.kill()
    return method


def supervise_process(command: list[str], watchdog_seconds: float) -> dict[str, Any]:
    started = time.monotonic()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    kill_method = None
    try:
        stdout, stderr = process.communicate(timeout=watchdog_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        kill_method = kill_process_tree(process)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate(timeout=2)
    return {
        "pid": process.pid,
        "returncode": process.returncode,
        "timed_out": timed_out,
        "kill_method": kill_method,
        "elapsed_seconds": time.monotonic() - started,
        "stdout": stdout,
        "stderr": stderr,
    }


def parent_execute(go_path: Path) -> int:
    invocation_started = time.monotonic()
    plan, go = validate_go(go_path)
    require_runtime_absent(RUNTIME)
    if WATCHDOG_DIR.exists():
        raise RuntimeError("parent-watchdog attempt directory already exists; GO is one-shot")
    require_disk("before parent watchdog output setup")
    WATCHDOG_DIR.mkdir(parents=False, exist_ok=False)
    private = WATCHDOG_DIR / "private"
    private.mkdir(parents=False, exist_ok=False)
    marker = {
        "schema": f"wow-recovery.{BATCH_ID}.go-consumed.v1",
        "batch_id": BATCH_ID,
        "go_id": go["go_id"],
        "go_sha256": sha256_file(go_path),
        "parent_pid": os.getpid(),
        "consumed_utc": iso_now(),
        "network_requests_at_marker": 0,
    }
    write_json(WATCHDOG_DIR / "go-consumed.json", marker)
    child = [sys.executable, str(Path(__file__).resolve()), "--worker", "--go", str(go_path.resolve())]
    parent_started = iso_now()
    available_for_worker = max(1.0, min(WORKER_WATCHDOG_SECONDS, PARENT_SECONDS - (time.monotonic() - invocation_started) - 15.0))
    watchdog = supervise_process(child, available_for_worker)
    (private / "worker-stdout.txt").write_bytes(watchdog.pop("stdout"))
    (private / "worker-stderr.txt").write_bytes(watchdog.pop("stderr"))
    require_disk("before parent watchdog receipt")
    runtime_report = RUNTIME / "private/report.json"
    receipt = {
        "schema": f"wow-recovery.{BATCH_ID}.parent-watchdog-receipt.v1",
        "batch_id": BATCH_ID,
        "parent_started_utc": parent_started,
        "parent_finished_utc": iso_now(),
        "go_id": go["go_id"],
        "go_sha256": sha256_file(go_path),
        "watchdog_seconds_configured": available_for_worker,
        "maximum_total_hard_seconds": PARENT_SECONDS,
        "worker": watchdog,
        "runtime_report_path": safe_rel(runtime_report) if runtime_report.is_file() else None,
        "runtime_exists_after_worker": RUNTIME.exists(),
        "disk_free_before_worker_bytes": go.get("free_bytes_before"),
        "disk_free_after_worker_bytes": disk_free(),
        "raw_http_private": True,
    }
    write_json(WATCHDOG_DIR / "watchdog-receipt.json", receipt)
    return int(watchdog.get("returncode") if watchdog.get("returncode") is not None else 3)


class FixtureTransport:
    def __init__(self, scenarios: dict[str, list[dict[str, Any]]], targets: list[dict[str, Any]]) -> None:
        self.scenarios = scenarios
        self.by_url = {target["url"]: target["target_id"] for target in targets}
        self.calls: list[dict[str, Any]] = []

    def __call__(self, command: list[str], *, capture_output: bool, timeout: float, check: bool, env: dict[str, str]):
        url = command[-1]
        target_id = self.by_url[url]
        queue = self.scenarios.setdefault(target_id, [])
        scenario = queue.pop(0) if queue else {"status": 200, "content_type": "image/jpeg", "body": b""}
        body_path = Path(command[command.index("--output") + 1])
        headers_path = Path(command[command.index("--dump-header") + 1])
        cookie_path = Path(command[command.index("--cookie-jar") + 1])
        body = scenario.get("body", b"")
        if isinstance(body, str):
            body = body.encode("utf-8")
        status = scenario.get("status")
        if status is None:
            headers_path.write_bytes(b"")
        else:
            lines = [f"HTTP/1.1 {status} Fixture"]
            if scenario.get("content_type"):
                lines.append(f"Content-Type: {scenario['content_type']}")
            if scenario.get("content_length", True):
                lines.append(f"Content-Length: {len(body)}")
            if scenario.get("retry_after"):
                lines.append(f"Retry-After: {scenario['retry_after']}")
            headers_path.write_bytes(("\r\n".join(lines) + "\r\n\r\n").encode("iso-8859-1"))
        if scenario.get("write_body", True):
            body_path.write_bytes(body)
        cookie_path.write_bytes(b"")
        rc = int(scenario.get("returncode", 0 if status is not None else 7))
        stdout = f"{status}\n{url}".encode("utf-8") if status is not None else b""
        self.calls.append({"target_id": target_id, "url": url, "transport": "proxy" if "--proxy" in command else "direct", "command": command, "timeout": timeout})
        return subprocess.CompletedProcess(command, rc, stdout=stdout, stderr=b"fixture stderr")


def fixture_jpeg() -> bytes:
    from PIL import Image

    stream = io.BytesIO()
    Image.new("RGB", (9, 7), (110, 70, 150)).save(stream, format="JPEG", quality=83)
    return stream.getvalue()


def fixture_target(target_id: str, url: str, body: bytes) -> dict[str, Any]:
    return {
        "target_id": target_id,
        "repository_path": f"fixtures/{target_id}.jpg",
        "url": url,
        "expected_git_blob_sha1": git_blob_sha1(body),
        "expected_bytes": len(body),
        "mime_expected": "image/jpeg",
    }


def run_fixture_batch(targets: list[dict[str, Any]], scenarios: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any], FixtureTransport]:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="coolwow2-icons-fixture-") as temp:
        paths = TRANSPORT.make_paths(Path(temp) / "runtime")
        stub = FixtureTransport(scenarios, targets)
        original = subprocess.run
        subprocess.run = stub  # type: ignore[assignment]
        try:
            result = run_batch(targets, paths, max_attempts=MAX_ATTEMPTS, max_seconds=20, cadence_seconds=0)
            return result, stub
        finally:
            subprocess.run = original  # type: ignore[assignment]


def offline_fixtures() -> dict[str, Any]:
    from PIL import Image  # noqa: F401 - assert Pillow is available before any GO
    import tempfile

    if RUNTIME.exists():
        raise RuntimeError("offline preparation refuses an existing batch runtime")
    checks: list[dict[str, Any]] = []
    jpeg = fixture_jpeg()
    first = fixture_target("fixture-direct-success", "https://raw.githubusercontent.com/fixture/repo/commit/a.jpg", jpeg)
    good, direct_stub = run_fixture_batch(
        [first],
        {first["target_id"]: [{"status": 200, "content_type": "image/jpeg", "body": jpeg}]},
    )
    assert good["stop_reason"] == "completed" and good["attempt_count"] == 1
    assert good["records"][0]["accepted"] is True
    direct_call = direct_stub.calls[0]
    assert direct_call["transport"] == "direct"
    assert "--tlsv1.2" in direct_call["command"] and "--retry" in direct_call["command"]
    assert direct_call["command"][direct_call["command"].index("--retry") + 1] == "0"
    assert "-L" not in direct_call["command"] and "--location" not in direct_call["command"]
    assert direct_call["command"][direct_call["command"].index("--noproxy") + 1] == "*"
    checks.append({"name": "direct_success_blob_and_all_jpeg_frames", "passed": True, "fixture_http_calls": 1})

    fallback = fixture_target("fixture-proxy-fallback", "https://raw.githubusercontent.com/fixture/repo/commit/b.jpg", jpeg)
    fallback_result, fallback_stub = run_fixture_batch(
        [fallback],
        {fallback["target_id"]: [
            {"status": None, "returncode": 7, "write_body": False},
            {"status": 200, "content_type": "image/jpeg", "body": jpeg},
        ]},
    )
    assert fallback_result["stop_reason"] == "completed" and fallback_result["attempt_count"] == 2
    assert [call["transport"] for call in fallback_stub.calls] == ["direct", "proxy"]
    assert fallback_stub.calls[1]["command"][fallback_stub.calls[1]["command"].index("--proxy") + 1] == PROXY
    checks.append({"name": "direct_transport_failure_then_local_proxy", "passed": True, "fixture_http_calls": 2})

    ratelimit = fixture_target("fixture-429", "https://raw.githubusercontent.com/fixture/repo/commit/c.jpg", jpeg)
    untouched = fixture_target("fixture-not-requested", "https://raw.githubusercontent.com/fixture/repo/commit/d.jpg", jpeg)
    limited, limited_stub = run_fixture_batch(
        [ratelimit, untouched],
        {ratelimit["target_id"]: [{"status": 429, "content_type": "text/plain", "body": b"slow down"}]},
    )
    assert limited["stop_reason"] == "endpoint_status_429" and len(limited_stub.calls) == 1
    not_before = datetime.fromisoformat(limited["cooldown_not_before_utc"].replace("Z", "+00:00"))
    finished = datetime.fromisoformat(limited_stub.calls and limited["records"][0]["observed_at_utc"].replace("Z", "+00:00"))
    assert not_before >= finished + timedelta(seconds=MIN_COOLDOWN)
    checks.append({"name": "429_immediate_stop_and_120_second_cooldown", "passed": True, "fixture_http_calls": 1})

    streak_targets = [
        fixture_target(f"fixture-streak-{index}", f"https://raw.githubusercontent.com/fixture/repo/commit/streak-{index}.jpg", jpeg)
        for index in range(1, 4)
    ]
    streak_scenarios = {
        streak_targets[0]["target_id"]: [
            {"status": None, "returncode": 7, "write_body": False},
            {"status": None, "returncode": 7, "write_body": False},
        ],
        streak_targets[1]["target_id"]: [
            {"status": None, "returncode": 7, "write_body": False},
            {"status": None, "returncode": 7, "write_body": False},
        ],
        streak_targets[2]["target_id"]: [
            {"status": None, "returncode": 7, "write_body": False},
        ],
    }
    streak_result, streak_stub = run_fixture_batch(streak_targets, streak_scenarios)
    assert streak_result["stop_reason"] == "five_consecutive_transport_failures"
    assert streak_result["attempt_count"] == 5 and len(streak_stub.calls) == 5
    assert [call["transport"] for call in streak_stub.calls] == ["direct", "proxy", "direct", "proxy", "direct"]
    assert len(streak_result["private_report"]["transport_failure_history_preserved"]) == 5
    fifth_finished = datetime.fromisoformat(streak_result["private_report"]["attempts"][-1]["request_finished_utc"].replace("Z", "+00:00"))
    streak_cooldown = datetime.fromisoformat(streak_result["cooldown_not_before_utc"].replace("Z", "+00:00"))
    assert streak_cooldown >= fifth_finished + timedelta(seconds=MIN_COOLDOWN)
    checks.append({"name": "five_transport_failures_across_three_logical_targets_stop_before_sixth_with_cooldown", "passed": True, "fixture_http_calls": 5})

    wrong = fixture_target("fixture-wrong-blob", "https://raw.githubusercontent.com/fixture/repo/commit/e.jpg", jpeg)
    wrong["expected_git_blob_sha1"] = "0" * 40
    wrong_result, wrong_stub = run_fixture_batch(
        [wrong], {wrong["target_id"]: [{"status": 200, "content_type": "image/jpeg", "body": jpeg}]}
    )
    assert wrong_result["stop_reason"] == "payload_validation_failed:git_blob_sha1_mismatch"
    assert len(wrong_stub.calls) == 1
    checks.append({"name": "wrong_git_blob_rejected", "passed": True, "fixture_http_calls": 1})

    wrong_length = fixture_target("fixture-wrong-size", "https://raw.githubusercontent.com/fixture/repo/commit/f.jpg", jpeg)
    wrong_length["expected_bytes"] += 1
    size_result, size_stub = run_fixture_batch(
        [wrong_length], {wrong_length["target_id"]: [{"status": 200, "content_type": "image/jpeg", "body": jpeg}]}
    )
    assert size_result["stop_reason"] == "payload_validation_failed:exact_byte_length_mismatch"
    assert len(size_stub.calls) == 1
    checks.append({"name": "wrong_length_rejected", "passed": True, "fixture_http_calls": 1})

    with tempfile.TemporaryDirectory(prefix="coolwow2-runtime-guard-") as temp:
        runtime = Path(temp) / "runtime"
        runtime.mkdir()
        sentinel = runtime / "keep.txt"
        sentinel.write_text("preserve", encoding="utf-8")
        before = sentinel.read_bytes()
        refused = False
        try:
            require_runtime_absent(runtime)
        except RuntimeError:
            refused = True
        assert refused and sentinel.read_bytes() == before and list(runtime.iterdir()) == [sentinel]
    assert not RUNTIME.exists()
    checks.append({"name": "existing_runtime_refused_without_mutation", "passed": True, "fixture_http_calls": 0})

    with tempfile.TemporaryDirectory(prefix="coolwow2-watchdog-fixture-") as temp:
        script = Path(temp) / "sleeper.py"
        script.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
        watched = supervise_process([sys.executable, str(script)], 0.35)
        assert watched["timed_out"] is True and watched["returncode"] is not None
        checks.append({"name": "actual_watchdog_timeout_and_process_kill", "passed": True, "fixture_http_calls": 0, "elapsed_seconds": round(watched["elapsed_seconds"], 3), "kill_method": watched["kill_method"]})

    mock_calls = sum(int(item.get("fixture_http_calls", 0)) for item in checks)
    return {
        "schema": f"wow-recovery.{BATCH_ID}.offline-validation.v1",
        "created_utc": iso_now(),
        "all_passed": all(item["passed"] for item in checks),
        "network_requests": 0,
        "mocked_http_calls": mock_calls,
        "checks": checks,
        "no_batch_runtime_created": not RUNTIME.exists(),
        "target_dimensions_hardcoded": False,
        "evidence_boundary": "Synthetic local fixtures only; they validate wrapper paths and do not establish remote availability or image contents.",
    }


def build_offline_validation() -> dict[str, Any]:
    result = offline_fixtures()
    result.update(
        {
            "plan_sha256": sha256_file(PLAN),
            "wrapper_sha256": sha256_file(Path(__file__)),
            "transport_runner_sha256": sha256_file(TRANSPORT_PATH),
            "source_selection_sha256": sha256_file(SELECTION),
            "selected_source_tree_sha256": sha256_file(TREE),
            "fixture_sha256": sha256_file(FIXTURE_SPEC),
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-fixtures", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--go", type=Path)
    args = parser.parse_args()
    if args.offline_fixtures:
        if args.execute or args.worker:
            raise SystemExit("offline fixture mode cannot be combined with execution")
        result = build_offline_validation()
        write_json(OFFLINE_VALIDATION, result)
        print(json.dumps({"all_passed": result["all_passed"], "network_requests": 0, "mocked_http_calls": result["mocked_http_calls"]}))
        return 0 if result["all_passed"] else 2
    if args.worker:
        if not args.go:
            raise SystemExit("worker requires --go")
        return worker_entry(args.go.resolve())
    if args.execute:
        if not args.go:
            raise SystemExit("--execute requires --go")
        return parent_execute(args.go.resolve())
    raise SystemExit("choose --offline-fixtures or --execute --go PATH")


if __name__ == "__main__":
    raise SystemExit(main())

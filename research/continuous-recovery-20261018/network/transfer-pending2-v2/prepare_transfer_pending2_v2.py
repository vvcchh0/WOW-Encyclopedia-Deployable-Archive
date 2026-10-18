"""Prepare one bounded, offline retry plan for two prior transfer failures.

This module only reads the immutable two-row retry queue, its cited local pages,
prior attempt receipts, and the current recovery source/control receipts.  It
never contacts the network and it never invokes the reusable image driver.
When explicitly run with ``--batch-index 1`` it writes one two-target plan
atomically; an existing batch directory is immutable and is refused.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
RECOVERY = ROOT / "research" / "continuous-recovery-20261018"
NETWORK = RECOVERY / "network"
FACTORY_ROOT = Path(__file__).resolve().parent

QUEUE_PATH = FACTORY_ROOT / "transfer-pending2-v2-queue.json"
STATUS_PATH = RECOVERY / "status.json"
V3_DRIVER_PATH = NETWORK / "reusable-image-driver-v3" / "reusable_image_driver.py"

EXPECTED_QUEUE_SHA = "8c6f14e2ee076649208465381751d722ccd55d3fafb7aa00243bbe79651f5786"
EXPECTED_DRIVER_SHA = "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955"
FROM_TS = "20000101000000"
TO_TS = "20080512210044"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
DISK_FLOOR = 11_005_853_696
BATCH_SIZE = 2
QUEUE_COUNT = 2
BATCH_COUNT = 1
PROXY = "http://127.0.0.1:7890"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_bytes(value) -> bytes:
    """Return the one canonical UTF-8/LF representation used for bindings."""
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value) -> None:
    # Path.write_text uses the Windows text newline translation. Bindings are
    # computed from LF bytes, so write the bytes explicitly to keep actual
    # files equal to their precomputed SHA/length on every platform.
    path.write_bytes(json_bytes(value))


def json_sha256(value) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def binding(path: Path, role: str) -> dict:
    return {"path": rel(path), "sha256": sha256(path), "bytes": path.stat().st_size, "role": role}


def _under_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def _under(path: Path, root: Path) -> bool:
    """Return whether the resolved path is contained by the resolved root."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _assert_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    if not _under(resolved, root):
        raise RuntimeError(f"{label} escapes its allowed root: {resolved}")
    return resolved


def _resolve_repo_path(value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("repository-relative source path is required")
    candidate = Path(value)
    if candidate.is_absolute():
        raise RuntimeError(f"source path must be repository-relative: {value}")
    resolved = (ROOT / candidate).resolve()
    if not _under_root(resolved):
        raise RuntimeError(f"source path escapes repository: {value}")
    return resolved


def _parse_url(value: str, label: str = "original"):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise RuntimeError(f"invalid {label}: {value!r}")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or not parsed.path:
        raise RuntimeError(f"{label} must be an exact HTTP(S) URL with a path: {value}")
    if parsed.username is not None or parsed.password is not None:
        raise RuntimeError(f"{label} must not contain credentials: {value}")
    if parsed.query or parsed.fragment:
        raise RuntimeError(f"{label} must not contain a query or fragment: {value}")
    try:
        port = parsed.port
    except ValueError as exc:
        raise RuntimeError(f"{label} has an invalid port: {value}") from exc
    if port not in (None, 80, 443):
        raise RuntimeError(f"{label} must use the default HTTP(S) port: {value}")
    return parsed


def _line_binds(line: str, original: str) -> str | None:
    """Return the matching evidence form used by the frozen driver contract."""
    if original in line:
        return "literal"
    encoded = quote(original, safe="")
    if encoded in line:
        return "url_encoded"
    return None


def validate_reference(ref: dict, original: str) -> dict:
    """Validate one queue citation and retain its complete local evidence."""
    if not isinstance(ref, dict):
        raise RuntimeError(f"reference is not an object: {original}")
    output_file = ref.get("output_file")
    line_number = ref.get("line")
    expected_sha = ref.get("source_page_sha256")
    if not isinstance(output_file, str) or not output_file:
        raise RuntimeError(f"reference has no output_file: {original}")
    if isinstance(line_number, bool) or not isinstance(line_number, int) or line_number < 1:
        raise RuntimeError(f"reference has invalid line: {original}")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise RuntimeError(f"reference has invalid source_page_sha256: {original}")
    try:
        int(expected_sha, 16)
    except ValueError as exc:
        raise RuntimeError(f"reference source_page_sha256 is not hexadecimal: {original}") from exc
    source_path = _resolve_repo_path(output_file)
    if not source_path.is_file():
        raise RuntimeError(f"citation file is missing: {source_path}")
    actual_sha = sha256(source_path)
    if actual_sha != expected_sha.lower():
        raise RuntimeError(f"citation page SHA mismatch: {source_path}")
    lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if line_number > len(lines):
        raise RuntimeError(f"citation line is outside file: {source_path}:{line_number}")
    match_kind = _line_binds(lines[line_number - 1], original)
    if match_kind is None:
        raise RuntimeError(f"citation line does not bind requested URL: {source_path}:{line_number}")
    return {
        "path": output_file.replace("\\", "/"),
        "line": line_number,
        "sha256": actual_sha,
        "source_page_sha256": actual_sha,
        "bytes": source_path.stat().st_size,
        "literal": original,
        "match": match_kind,
        "source_page": ref.get("source_page"),
        "reason": ref.get("reason"),
        "page": ref.get("page"),
    }


def _validate_alternates(row: dict, primary_original: str) -> list[dict]:
    context = []
    alternates = row.get("alternate_navigation_links") or []
    if not isinstance(alternates, list):
        raise RuntimeError(f"alternate_navigation_links is not a list: {primary_original}")
    seen = set()
    for alternate in alternates:
        if not isinstance(alternate, dict):
            raise RuntimeError(f"alternate navigation link is not an object: {primary_original}")
        original = alternate.get("original")
        _parse_url(original, "alternate original")
        if original == primary_original or original in seen:
            raise RuntimeError(f"duplicate alternate navigation original: {original}")
        seen.add(original)
        refs = alternate.get("references")
        if not isinstance(refs, list) or not refs:
            raise RuntimeError(f"alternate navigation link has no references: {original}")
        evidence = [validate_reference(ref, original) for ref in refs]
        context.append({
            "original": original,
            "references": copy.deepcopy(refs),
            "source_evidence": evidence,
            "role": "alternate_navigation_context_only",
        })
    return context


def validate_queue_document(queue: dict, queue_path: Path = QUEUE_PATH) -> tuple[list[dict], dict]:
    """Validate the actual frozen queue and return rows plus source bindings."""
    if queue.get("accepted") is not True or queue.get("network_requests") != 0:
        raise RuntimeError("transfer-pending2 queue is not an accepted offline queue")
    if queue.get("target_count") != QUEUE_COUNT:
        raise RuntimeError(f"transfer-pending2 queue target_count must be {QUEUE_COUNT}")
    rows = queue.get("rows")
    if not isinstance(rows, list) or len(rows) != QUEUE_COUNT:
        raise RuntimeError(f"transfer-pending2 queue must contain exactly {QUEUE_COUNT} rows")
    if any(not isinstance(row, dict) for row in rows):
        raise RuntimeError("transfer-pending2 queue row is not an object")
    rows = sorted(rows, key=lambda item: item.get("rank", -1))
    ranks = [row.get("rank") for row in rows]
    if ranks != list(range(1, QUEUE_COUNT + 1)):
        raise RuntimeError("transfer-pending2 queue ranks are not the expected 1..2 sequence")
    originals = []
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("transfer-pending2 queue row is not an object")
        original = row.get("original")
        _parse_url(original)
        if original in originals:
            raise RuntimeError(f"transfer-pending2 queue has duplicate original: {original}")
        originals.append(original)
        if row.get("recent_execution_record_count") not in (None, 0):
            raise RuntimeError(f"transfer-pending2 row has prior execution evidence: rank {row.get('rank')}")
        refs = row.get("references")
        if not isinstance(refs, list) or not refs:
            raise RuntimeError(f"transfer-pending2 row has no primary references: rank {row.get('rank')}")
        evidence = [validate_reference(ref, original) for ref in refs]
        alternates = _validate_alternates(row, original)
        normalized.append({
            "row": copy.deepcopy(row),
            "primary_evidence": evidence,
            "alternate_context": alternates,
        })

    source_bindings = {}
    for field, role in (("source_audit", "frozen prior NEWS transfer plan acceptance"),
                        ("source_provenance", "frozen prior NAVIGATION transfer plan acceptance")):
        entry = queue.get(field)
        if not isinstance(entry, dict):
            raise RuntimeError(f"navigation70 queue has no {field} binding")
        source_path = _resolve_repo_path(entry.get("path"))
        if not source_path.is_file():
            raise RuntimeError(f"queue {field} file is missing: {source_path}")
        actual = sha256(source_path)
        if actual != entry.get("sha256"):
            raise RuntimeError(f"queue {field} SHA mismatch: {source_path}")
        source_bindings[field] = binding(source_path, role)
    return normalized, source_bindings


def load_frozen_queue() -> tuple[dict, list[dict], dict]:
    if not QUEUE_PATH.is_file():
        raise RuntimeError(f"missing frozen queue: {QUEUE_PATH}")
    queue_sha = sha256(QUEUE_PATH)
    if queue_sha != EXPECTED_QUEUE_SHA:
        raise RuntimeError(f"frozen navigation queue SHA mismatch: {queue_sha}")
    queue = read_json(QUEUE_PATH)
    rows, source_bindings = validate_queue_document(queue, QUEUE_PATH)
    return queue, rows, source_bindings


def _resolve_status_pointer(status: dict, field: str) -> Path:
    value = status.get(field)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"recovery status has no {field}")
    candidate = Path(value)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    elif value.replace("\\", "/").startswith("research/"):
        resolved = (ROOT / candidate).resolve()
    else:
        resolved = (RECOVERY / candidate).resolve()
    if not _under_root(resolved):
        raise RuntimeError(f"status pointer escapes repository: {value}")
    return resolved


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError(f"invalid UTC timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise RuntimeError(f"timestamp must include timezone: {value}")
    return parsed.astimezone(timezone.utc)


def _not_in_cooldown(status: dict, receipt: dict, now: datetime) -> None:
    for label, value in (("status network cooldown", status.get("network_cooldown_not_before_utc")),
                         ("source receipt cooldown", receipt.get("cooldown_not_before_utc"))):
        deadline = _parse_time(value)
        if deadline and now < deadline:
            raise RuntimeError(f"{label} is still active until {value}")


def load_runtime_bindings() -> tuple[dict, dict, Path, dict, Path, dict, int]:
    """Read current status/source tail/CONTROL03; never alter them."""
    if not STATUS_PATH.is_file():
        raise RuntimeError(f"missing recovery status: {STATUS_PATH}")
    status = read_json(STATUS_PATH)
    status_sha = sha256(STATUS_PATH)
    if status.get("network_resume_gate_passed") is not True:
        raise RuntimeError("network resume gate is closed")
    source_field = "latest_source_acceptance" if status.get("latest_source_acceptance") else "last_image_source_acceptance"
    source_path = _resolve_status_pointer(status, source_field)
    if not source_path.is_file():
        raise RuntimeError(f"latest source receipt is missing: {source_path}")
    source = read_json(source_path)
    source_sha = sha256(source_path)
    if source.get("accepted") is not True:
        raise RuntimeError("latest source receipt is not accepted")
    tail = source.get("failure_streak_end")
    if isinstance(tail, bool) or not isinstance(tail, int) or not 0 <= tail <= 4:
        raise RuntimeError("latest source receipt has an invalid failure tail")
    status_tail = status.get("latest_failure_tail")
    if isinstance(status_tail, int) and not isinstance(status_tail, bool) and status_tail != tail:
        raise RuntimeError("status latest_failure_tail does not match latest source receipt")
    now = datetime.now(timezone.utc)
    _not_in_cooldown(status, source, now)

    control_path = _resolve_status_pointer(status, "latest_control_gate")
    if "control03" not in control_path.name.lower():
        raise RuntimeError(f"latest control gate is not CONTROL03: {control_path}")
    if not control_path.is_file():
        raise RuntimeError(f"CONTROL03 receipt is missing: {control_path}")
    control = read_json(control_path)
    control_sha = sha256(control_path)
    if not (control.get("accepted") is True and control.get("resume_gate_passed") is True
            and control.get("control_final_streak") == 0):
        raise RuntimeError("CONTROL03 gate is closed")
    if control.get("failure_streak_end") not in (None, 0):
        raise RuntimeError("CONTROL03 gate has a nonzero failure tail")
    if not V3_DRIVER_PATH.is_file():
        raise RuntimeError(f"missing frozen reusable image driver: {V3_DRIVER_PATH}")
    driver_sha = sha256(V3_DRIVER_PATH)
    if driver_sha != EXPECTED_DRIVER_SHA:
        raise RuntimeError(f"frozen V3 driver SHA mismatch: {driver_sha}")
    runtime = {
        "status": binding(STATUS_PATH, "current recovery status snapshot"),
        "status_sha256": status_sha,
        "latest_source_acceptance": binding(source_path, "freshest accepted source receipt selected from current status"),
        "latest_control_gate": binding(control_path, "current accepted CONTROL03 tail-zero gate"),
        "frozen_v3_driver": binding(V3_DRIVER_PATH, "frozen reusable-image-v3 driver"),
        "source_field": source_field,
        "latest_failure_tail": tail,
        "captured_utc": now.isoformat().replace("+00:00", "Z"),
        "network_requests_during_preparation": 0,
    }
    return status, source, source_path, control, control_path, runtime, tail


def expected_for(original: str) -> tuple[list[str], list[str], bool]:
    suffix = Path(urlsplit(original).path).suffix.lower()
    if suffix == ".gif":
        return ["image/gif"], ["GIF"], True
    if suffix == ".png":
        return ["image/png"], ["PNG"], False
    if suffix in {".jpg", ".jpeg"}:
        return ["image/jpeg"], ["JPEG"], False
    return ["image/jpeg", "image/gif", "image/png"], ["JPEG", "GIF", "PNG"], True


def query_url(original: str) -> str:
    return ("https://web.archive.org/cdx/search/cdx?url=" + quote(original, safe="")
            + f"&from={FROM_TS}&to={TO_TS}&output=json&fl={quote(','.join(FIELDS), safe='')}"
            + "&limit=500&showResumeKey=true&matchType=exact")


def select_batch(rows: list[dict], batch_index: int) -> list[dict]:
    if isinstance(batch_index, bool) or not isinstance(batch_index, int) or not 1 <= batch_index <= BATCH_COUNT:
        raise RuntimeError("--batch-index must be the integer 1")
    start = (batch_index - 1) * BATCH_SIZE
    chunk = rows[start:start + BATCH_SIZE]
    if len(chunk) != BATCH_SIZE:
        raise RuntimeError(f"batch {batch_index} does not contain exactly two targets")
    return chunk


def make_candidate(item: dict, batch_index: int, local_no: int, queue: dict,
                   queue_sha: str, runtime: dict, status_snapshot_ref: dict,
                   source_path: Path, source_sha: str, tail: int) -> dict:
    row = item["row"]
    original = row["original"]
    mime_types, pillow_formats, all_gif_frames = expected_for(original)
    evidence = item["primary_evidence"]
    primary = copy.deepcopy(evidence[0])
    return {
        "target_key": f"TRANSFER-PENDING2-V2-{batch_index:02d}-{local_no:02d}",
        "priority": local_no,
        "queue_rank": row["rank"],
        "kind": "image",
        "original": original,
        "literal": original,
        "expected": {
            "archive_query_required": True,
            "mime_types": mime_types,
            "pillow_formats": pillow_formats,
            "all_gif_frames": all_gif_frames,
            "reencode": False,
            "script_execution": False,
            "query_window": {"from": FROM_TS, "to": TO_TS},
        },
        "expected_mime": mime_types,
        "source_evidence": primary,
        # Deliberately contains only the row's same-original references;
        # alternate_navigation_links remain context below and are never merged.
        "all_references": copy.deepcopy(evidence),
        "source_page_context": {
            "candidate_file": rel(QUEUE_PATH),
            "candidate_file_sha256": queue_sha,
            "queue_rank": row.get("rank"),
            "source_role": row.get("source_role"),
            "source_pages": copy.deepcopy(row.get("source_pages") or []),
            "references": copy.deepcopy(row.get("references") or []),
            "validated_references": copy.deepcopy(evidence),
            "alternate_navigation_links": copy.deepcopy(item["alternate_context"]),
            "source_page_context_note": "Alternates are retained as provenance context only; they are not same-original all_references.",
            "original_source_context": {
                "source_page": primary.get("source_page"),
                "reason": primary.get("reason"),
                "page": primary.get("page"),
                "origin_host": urlsplit(original).hostname,
                "scheme": urlsplit(original).scheme,
            },
            "current_source_receipt": binding(source_path, "freshest actual source receipt at factory invocation"),
            "current_source_receipt_sha256": source_sha,
            "current_failure_tail": tail,
            "status_snapshot": status_snapshot_ref,
            "queue_row": copy.deepcopy(row),
        },
        "selection": {
            "max_distinct_digest_candidates": 2,
            "potential_truncation": "do_not_replay",
            "require_complete_index": True,
            "require_exact_original": True,
            "require_expected_mime": True,
            "require_nonempty_cdx_sha1_digest": True,
            "require_statuscode": 200,
            "same_digest_older_captures": "skip",
            "sort": "timestamp_desc_then_record_index_desc",
            "unknown_metadata": "incomplete_error",
        },
        "known_positive_cache_rows": [],
        "fallback_label": None,
        "cdx_mode": "fresh",
        "query": {
            "endpoint": "https://web.archive.org/cdx/search/cdx",
            "url": original,
            "from": FROM_TS,
            "to": TO_TS,
            "output": "json",
            "fields": FIELDS,
            "limit": 500,
            "showResumeKey": True,
            "collapse": False,
            "matchType": "exact",
            "query_url": query_url(original),
        },
        "replay": {
            "enabled": True,
            "id_url_template": "https://web.archive.org/web/{timestamp}id_/" + original,
            "max_candidates": 2,
            "no_redirects": True,
            "verify_tls": True,
            "acceptance": [
                "http_status_200",
                "memento_datetime_present_and_exact",
                "link_original_exact_default_port_only",
                "expected_image_content_type",
                "magic_and_pillow_decode",
                "all_gif_frames_loaded",
                "decoded_payload_sha1_matches_cdx_digest",
            ],
            "accepted_payloads_are_source_data_only": True,
        },
        "prior_local_evidence": [{
            "state": row.get("recent_execution_record_count", 0),
            "source": "transfer-pending2-v2-queue",
            "exact_entity_index_complete": False,
            "positive_row_count": 0,
        }],
        "prior_evidence_status": "transfer_pending2_prior_failure_bound; fresh_exact_cdx_required; no_bound_positive_fallback",
    }


def make_policy(tail: int) -> dict:
    return {
        "from": FROM_TS,
        "to": TO_TS,
        "limit": 500,
        "showResumeKey": True,
        "collapse": False,
        "matchType": "exact",
        # The frozen reusable-image driver has a fixed global contract of 20
        # originals per invocation.  This retry plan still selects exactly two
        # queue rows; the larger value is only the driver's accepted policy cap.
        "max_originals": 20,
        "max_attempts": 8,
        "window_seconds": 100.0,
        "max_total_body_bytes": 8 * 1024 * 1024,
        "max_entity_body_bytes": 4 * 1024 * 1024,
        "min_dispatch_seconds": 5.25,
        "min_request_start_seconds": 5.0,
        "disk_floor_bytes": DISK_FLOOR,
        "direct_first": True,
        "direct_attempt_budget": 4,
        "proxy_attempt_budget": 20,
        "direct_connect_seconds": 4.0,
        "proxy_timeout_seconds": 20.0,
        "proxy": PROXY,
        "tls_verification": True,
        "automatic_redirects": 0,
        "stop_http_codes": [429, 503],
        "cooldown_seconds": 120,
        "user_agent": "wow-recovery-reusable-image-v3/20261018-transfer-pending2-v2",
        "prior_failure_tail": tail,
        "transport_policy": "batch_after_direct_failure",
        "no_network_before_parent_go": True,
    }


def make_plan(batch_index: int, queue: dict, rows: list[dict], queue_sha: str,
              queue_source_bindings: dict, runtime: dict,
              status_snapshot_ref: dict, source_path: Path, source_sha: str,
              tail: int) -> tuple[dict, dict, dict, dict]:
    chunk = select_batch(rows, batch_index)
    candidates = [make_candidate(item, batch_index, local_no, queue, queue_sha,
                                  runtime, status_snapshot_ref, source_path,
                                  source_sha, tail)
                  for local_no, item in enumerate(chunk, 1)]
    batch_id = f"WAYBACK-CONTINUOUS-20261018-TRANSFER-PENDING2-V2-{batch_index:02d}"
    queue_ref = binding(QUEUE_PATH, "immutable two-target transfer-pending2 retry queue")
    runtime_refs = {
        "status": runtime["status"],
        "latest_source_acceptance": runtime["latest_source_acceptance"],
        "latest_control_gate": runtime["latest_control_gate"],
        "frozen_v3_driver": runtime["frozen_v3_driver"],
    }
    bindings = {"navigation70_queue": queue_ref, **queue_source_bindings,
                **runtime_refs, "status_snapshot": status_snapshot_ref}
    previous = {
        "name": "current_source_tail_and_CONTROL03",
        "prior_failure_tail": tail,
        "acceptance_receipt_path": rel(source_path),
        "acceptance_receipt_sha256": source_sha,
        "tail_receipt_path": rel(source_path),
        "tail_receipt_sha256": source_sha,
        "latest_successful_tail_end": tail,
        "historical_tail_is_preserved": True,
        "control_gate_receipt_path": runtime["latest_control_gate"]["path"],
        "control_gate_receipt_sha256": runtime["latest_control_gate"]["sha256"],
        "control_gate_required": tail == 0,
        "root_control_acceptance_bound": True,
        "parent_go_required": True,
    }
    plan = {
        "schema": "wow-recovery.reusable-image-plan.v1",
        "batch_id": batch_id,
        "prepared_utc": runtime["captured_utc"],
        "mode": "fresh_exact_cdx_then_id_replay_no_fallback",
        "network_authorized": None,
        "parent_go_required": True,
        "candidate_count": len(candidates),
        "output_dir": rel(FACTORY_ROOT / f"batch-{batch_index:02d}" / "output"),
        "execution_order": {
            "batch_number": batch_index,
            "batch_count": BATCH_COUNT,
            "predecessor_batch_required": batch_index > 1,
            "predecessor_tail_rebind_required_before_execute": False,
            "predecessor_tail_status": "bound_to_current_source_acceptance",
            "root_control_acceptance_bound": True,
            "root_control_acceptance_required_before_execute": False,
        },
        "selection_scope": {
            "name": f"transfer_pending2_v2_batch_{batch_index:02d}",
            "reason": "Two exact originals retained from prior transfer failures; each citation is locally SHA-bound and no positive cache fallback is allowed.",
            "queue_path": rel(QUEUE_PATH),
            "queue_sha256": queue_sha,
            "queue_target_count": QUEUE_COUNT,
            "queue_rank_range": [chunk[0]["row"]["rank"], chunk[-1]["row"]["rank"]],
            "selected_queue_ranks": [item["row"]["rank"] for item in chunk],
            "network_requests_during_preparation": 0,
            "alternate_links_are_context_only": True,
        },
        "candidates": candidates,
        "policy": make_policy(tail),
        "previous_batch": previous,
        "input_bindings": bindings,
        "source_bindings": bindings,
        "excluded_rows": {
            "selected_queue_ranks": [item["row"]["rank"] for item in chunk],
            "other_queue_batch_ranks": [item["row"]["rank"] for item in rows if item not in chunk],
            "known_positive_fallback_rows": [],
        },
        "identity_variant_policy": {
            "retain_in_cdx_report": True,
            "replay_identity_variants": False,
            "strict_identity": "exact_original_default_port_only",
            "scheme_or_host_variants_are_not_equivalent": True,
        },
        "execution_boundary": {
            "no_network_authorized_by_this_artifact": True,
            "requires_parent_GO": True,
            "requires_new_root_control_acceptance": False,
            "root_control_acceptance_bound": True,
            "driver_not_invoked_by_factory": True,
        },
    }
    bindings_doc = {
        "schema": "wow-recovery.reusable-image-input-bindings.v1",
        "batch_id": batch_id,
        "plan_path": rel(FACTORY_ROOT / f"batch-{batch_index:02d}" / "plan.json"),
        "plan_sha256": json_sha256(plan),
        "driver_path": rel(V3_DRIVER_PATH),
        "driver_sha256": EXPECTED_DRIVER_SHA,
        "selected_queue_ranks": [item["row"]["rank"] for item in chunk],
        "selected_originals": [item["row"]["original"] for item in chunk],
        "source_bindings": bindings,
        "network_requests_during_preparation": 0,
        "driver_execution": "not invoked by this factory",
    }
    cache = {
        "schema": "wow-recovery.transfer-pending2-v2-cache-status.v1",
        "generated_utc": runtime["captured_utc"],
        "network_requests": 0,
        "raw_exact_cdx_cache_present": False,
        "raw_exact_cdx_cache_bound": False,
        "fresh_exact_cdx_required": True,
        "known_positive_fallback_available": False,
        "fallback_policy": "none; source queue contains citations only",
        "targets": [{
            "target_key": c["target_key"],
            "queue_rank": c["queue_rank"],
            "original": c["original"],
            "cdx_mode": "fresh",
            "fresh_query_url": c["query"]["query_url"],
            "replay_after_fresh_only": True,
            "latest_unknown_on_transport_failure": True,
        } for c in candidates],
        "queue_split": {"full_queue_count": QUEUE_COUNT, "batch_number": batch_index,
                        "batch_count": BATCH_COUNT, "batch_size": BATCH_SIZE},
        "planned_request_bound": 8,
        "planned_batch_duration_seconds": 100.0,
        "planned_total_body_bytes": 8 * 1024 * 1024,
        "planned_entity_body_bytes": 4 * 1024 * 1024,
        "stop_conditions": [
            "HTTP 429 or 503: stop batch and cool down at least 120 seconds",
            "five consecutive transport failures: stop batch and preserve current tail",
            "disk free below 11005853696 bytes before any request/write: stop",
            "request, body, or duration budget clamp: stop and preserve unprocessed rows",
            "fresh CDX incomplete/resume-key/unknown metadata: do not replay that target",
            "no execution until parent issues plan GO",
        ],
        "source_bindings": bindings,
    }
    selection = {
        "schema": "wow-recovery.transfer-pending2-v2-selection.v1",
        "generated_utc": runtime["captured_utc"],
        "queue": queue_ref,
        "selected": [{
            "target_key": c["target_key"], "queue_rank": c["queue_rank"],
            "original": c["original"], "all_references": c["all_references"],
            "alternate_navigation_links": c["source_page_context"]["alternate_navigation_links"],
        } for c in candidates],
        "selection_scope": plan["selection_scope"],
    }
    return plan, bindings_doc, cache, selection


def ensure_batch_available(batch_dir: Path) -> None:
    if batch_dir.exists():
        raise RuntimeError(f"requested navigation batch already exists; refusing overwrite: {batch_dir}")


def write_batch_atomic(batch_index: int, documents: dict[str, dict]) -> dict:
    """Write a complete batch into a sibling temp dir, then atomically rename it."""
    if shutil.disk_usage(ROOT).free < DISK_FLOOR:
        raise RuntimeError("D-drive free space is below the required floor")
    factory_root = _assert_under(FACTORY_ROOT, ROOT, "factory root")
    factory_root.mkdir(parents=True, exist_ok=True)
    batch_dir = _assert_under(factory_root / f"batch-{batch_index:02d}", factory_root, "batch target")
    ensure_batch_available(batch_dir)
    temp_dir = _assert_under(
        Path(tempfile.mkdtemp(prefix=f".batch-{batch_index:02d}-", dir=factory_root)),
        factory_root,
        "atomic temporary directory",
    )
    try:
        hashes = {}
        for name, value in documents.items():
            path = _assert_under(temp_dir / name, temp_dir, f"document {name}")
            path.parent.mkdir(parents=True, exist_ok=True)
            write_json(path, value)
            hashes[name] = {"path": rel(batch_dir / name), "sha256": sha256(path), "bytes": path.stat().st_size}
        if shutil.disk_usage(ROOT).free < DISK_FLOOR:
            raise RuntimeError("D-drive free space fell below the required floor")
        # Recheck immediately before the rename so a concurrent creator cannot
        # turn the immutable-batch refusal into an overwrite.
        ensure_batch_available(batch_dir)
        _assert_under(temp_dir, factory_root, "atomic temporary directory")
        _assert_under(batch_dir, factory_root, "batch target")
        os.replace(temp_dir, batch_dir)
        return {"batch_dir": rel(batch_dir), "files": hashes, "network_requests": 0}
    except Exception:
        _assert_under(temp_dir, factory_root, "atomic cleanup directory")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def parse_batch_index() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-index", type=int, required=True, help="the single two-target retry batch (1)")
    args = parser.parse_args()
    if isinstance(args.batch_index, bool) or not 1 <= args.batch_index <= BATCH_COUNT:
        parser.error("--batch-index must be the integer 1")
    return args.batch_index


def main() -> None:
    batch_index = parse_batch_index()
    queue, rows, queue_sources = load_frozen_queue()
    status, source, source_path, control, control_path, runtime, tail = load_runtime_bindings()
    queue_sha = sha256(QUEUE_PATH)
    prepared_utc = runtime["captured_utc"]
    batch_dir = FACTORY_ROOT / f"batch-{batch_index:02d}"
    ensure_batch_available(batch_dir)
    status_snapshot = {
        "schema": "wow-recovery.transfer-pending2-v2-status-snapshot.v1",
        "captured_utc": prepared_utc,
        "active_status_path": rel(STATUS_PATH),
        "active_status_sha256": runtime["status_sha256"],
        "latest_source_acceptance": runtime["latest_source_acceptance"],
        "latest_control_gate": runtime["latest_control_gate"],
        "latest_failure_tail": tail,
        "network_cooldown_not_before_utc": status.get("network_cooldown_not_before_utc"),
        "source_receipt_cooldown_not_before_utc": source.get("cooldown_not_before_utc"),
        "network_requests_during_preparation": 0,
    }
    # The snapshot participates in the same atomic batch as the plan, so its
    # binding is filled after a temporary copy has been made below.
    plan, bindings_doc, cache, selection = make_plan(
        batch_index, queue, rows, queue_sha, queue_sources, runtime,
        {"path": rel(batch_dir / "status-snapshot.json"),
         "sha256": json_sha256(status_snapshot),
         "bytes": len(json_bytes(status_snapshot)),
         "role": "atomic batch-local status snapshot"},
        source_path, sha256(source_path), tail)
    documents = {
        "status-snapshot.json": status_snapshot,
        "plan.json": plan,
        "input-bindings.json": bindings_doc,
        "cache-status.json": cache,
        "selection-manifest.json": selection,
    }
    result = write_batch_atomic(batch_index, documents)
    print(json.dumps({
        "batch_index": batch_index,
        "batch_id": plan["batch_id"],
        "queue_sha256": queue_sha,
        "selected_queue_ranks": plan["selection_scope"]["selected_queue_ranks"],
        "latest_source_acceptance": runtime["latest_source_acceptance"],
        "latest_control_gate": runtime["latest_control_gate"],
        "driver_sha256": EXPECTED_DRIVER_SHA,
        "batch": result,
        "network_requests": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

"""Prepare bounded, offline fresh-CDX plans for the static40 frontier queue.

The factory validates the frozen local candidate evidence and the corrected
navigation exclusion, then prepares one ten-target batch. It never contacts
CDX, replays an archive, invokes the image driver, or treats preparation as a
parent GO. All JSON is written as explicit UTF-8/LF bytes so Windows newline
translation cannot invalidate bound hashes and lengths.
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
FACTORY_ROOT = NETWORK / "static40-v32"
QUEUE_PATH = FACTORY_ROOT / "static40-source-queue.json"
SOURCE_AUDIT_PATH = RECOVERY / "local-audit" / "static-frontier-v32" / "static-frontier-v32-candidates.json"
CORRECTION_PATH = RECOVERY / "local-audit" / "static-frontier-v32" / "static-frontier-v32-navigation-exclusion-correction.json"
STATUS_PATH = RECOVERY / "status.json"
V3_DRIVER_PATH = NETWORK / "reusable-image-driver-v3" / "reusable_image_driver.py"

EXPECTED_QUEUE_SHA = "8cd75a65935eb416ab12ed70fa1b2f86335939a409173df899bdb7f8d48d95f9"
EXPECTED_SOURCE_AUDIT_SHA = "72c00aa28e7c19c86de7f877983d049662f543be48960d2879a0f566bf15657f"
EXPECTED_CORRECTION_SHA = "cc665a6ba455977f267e5f7e22b8bf4907d58a9581809b695f2fbc1b92bc564d"
EXPECTED_DRIVER_SHA = "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955"
FROM_TS = "20000101000000"
TO_TS = "20080512210044"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
DISK_FLOOR = 11_005_853_696
BATCH_SIZE = 10
QUEUE_COUNT = 40
BATCH_COUNT = 4
PROXY = "http://127.0.0.1:7890"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_bytes())


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def json_sha256(value) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def binding(path: Path, role: str) -> dict:
    return {"path": rel(path), "sha256": sha256(path), "bytes": path.stat().st_size, "role": role}


def _under(path: Path, root: Path) -> bool:
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
    if not isinstance(value, str) or not value.strip() or Path(value).is_absolute():
        raise RuntimeError(f"repository-relative path required: {value!r}")
    return _assert_under(ROOT / value, ROOT, "repository path")


def _parse_url(value: str, label: str = "original"):
    if not isinstance(value, str) or not value or value != value.strip() or any(ch.isspace() for ch in value):
        raise RuntimeError(f"invalid {label}: {value!r}")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or not parsed.path:
        raise RuntimeError(f"{label} must be an exact HTTP(S) URL with a path: {value}")
    if parsed.username is not None or parsed.password is not None:
        raise RuntimeError(f"{label} must not contain credentials: {value}")
    if parsed.query or parsed.fragment:
        raise RuntimeError(f"{label} must not contain query or fragment: {value}")
    try:
        port = parsed.port
    except ValueError as exc:
        raise RuntimeError(f"{label} has an invalid port: {value}") from exc
    if port not in (None, 80, 443):
        raise RuntimeError(f"{label} must use the default HTTP(S) port: {value}")
    return parsed


def _line_binds(line: str, original: str) -> str | None:
    if original in line:
        return "literal"
    if quote(original, safe="") in line:
        return "url_encoded"
    return None


def validate_reference(ref: dict, original: str) -> dict:
    output_file = ref.get("output_file")
    line_number = ref.get("line")
    expected_sha = ref.get("source_page_sha256")
    if not isinstance(output_file, str) or not output_file:
        raise RuntimeError(f"reference has no output_file: {original}")
    if isinstance(line_number, bool) or not isinstance(line_number, int) or line_number < 1:
        raise RuntimeError(f"reference has invalid line: {original}")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise RuntimeError(f"reference has invalid source_page_sha256: {original}")
    source_path = _resolve_repo_path(output_file)
    if not source_path.is_file():
        raise RuntimeError(f"citation file is missing: {source_path}")
    actual_sha = sha256(source_path)
    if actual_sha != expected_sha.lower():
        raise RuntimeError(f"citation page SHA mismatch: {source_path}")
    lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if line_number > len(lines):
        raise RuntimeError(f"citation line is outside file: {source_path}:{line_number}")
    match = _line_binds(lines[line_number - 1], original)
    if match is None:
        raise RuntimeError(f"citation line does not bind requested URL: {source_path}:{line_number}")
    return {
        "path": output_file.replace("\\", "/"),
        "line": line_number,
        "sha256": actual_sha,
        "bytes": source_path.stat().st_size,
        "literal": original,
        "match": match,
        "source_page": ref.get("source_page"),
        "source_base_url": ref.get("source_base_url"),
        "reason": ref.get("reason"),
    }


def validate_candidate(row: dict) -> dict:
    candidate = row.get("candidate")
    if not isinstance(candidate, dict):
        raise RuntimeError("static40 queue row has no candidate record")
    original = row.get("requested_url")
    if original != candidate.get("requested_url") or row.get("normalized_identity") != candidate.get("normalized_identity"):
        raise RuntimeError(f"static40 queue row identity mismatch: {original}")
    _parse_url(original)
    refs = candidate.get("references")
    if not isinstance(refs, list) or not refs:
        raise RuntimeError(f"static40 candidate has no source references: {original}")
    verified = [validate_reference(ref, original) for ref in refs]
    source_output = candidate.get("source_output_page")
    source_output_sha = candidate.get("source_output_page_sha256")
    if not isinstance(source_output, str) or not isinstance(source_output_sha, str):
        raise RuntimeError(f"static40 candidate lacks source output binding: {original}")
    source_output_path = _resolve_repo_path(source_output)
    if sha256(source_output_path) != source_output_sha.lower():
        raise RuntimeError(f"source output SHA mismatch: {source_output_path}")
    return {
        "queue_rank": row.get("queue_rank"),
        "candidate_priority_rank": row.get("candidate_priority_rank"),
        "original": original,
        "normalized_identity": row.get("normalized_identity"),
        "candidate": copy.deepcopy(candidate),
        "verified_references": verified,
        "source_output_page": source_output,
        "source_output_page_sha256": source_output_sha.lower(),
    }


def _validate_audit_inputs(audit: dict) -> dict:
    inputs = audit.get("inputs")
    if not isinstance(inputs, dict):
        raise RuntimeError("static-frontier audit has no inputs")
    bindings = {}
    for key, value in inputs.items():
        if key.endswith("_sha256") or value is None:
            continue
        if not isinstance(value, str):
            continue
        path = _resolve_repo_path(value)
        expected = inputs.get(key + "_sha256")
        if path.is_file():
            if not isinstance(expected, str) or sha256(path) != expected.lower():
                raise RuntimeError(f"static-frontier input SHA mismatch: {path}")
            bindings[key] = binding(path, f"static-frontier audit input: {key}")
        elif path.is_dir():
            bindings[key] = {"path": rel(path), "sha256": None, "bytes": None, "role": f"static-frontier audit directory: {key}"}
        else:
            raise RuntimeError(f"static-frontier input is missing: {path}")
    return bindings


def validate_queue_document(queue: dict) -> tuple[list[dict], dict]:
    if queue.get("accepted") is not False or queue.get("preparation_only") is not True or queue.get("network_requests") != 0:
        raise RuntimeError("static40 queue must remain preparation-only and offline")
    if queue.get("target_count") != QUEUE_COUNT:
        raise RuntimeError(f"static40 queue target_count must be {QUEUE_COUNT}")
    audit_path = _resolve_repo_path(queue["source_audit"]["path"])
    correction_path = _resolve_repo_path(queue["navigation_exclusion_correction"]["path"])
    if sha256(audit_path) != EXPECTED_SOURCE_AUDIT_SHA or queue["source_audit"].get("sha256") != EXPECTED_SOURCE_AUDIT_SHA:
        raise RuntimeError("static-frontier source audit SHA mismatch")
    if sha256(correction_path) != EXPECTED_CORRECTION_SHA or queue["navigation_exclusion_correction"].get("sha256") != EXPECTED_CORRECTION_SHA:
        raise RuntimeError("navigation exclusion correction SHA mismatch")
    audit = read_json(audit_path)
    correction = read_json(correction_path)
    if len(audit.get("candidates") or []) != 41:
        raise RuntimeError("static-frontier source audit candidate count changed")
    _validate_audit_inputs(audit)
    if correction.get("corrected_navigation_queue", {}).get("sha256") != "6d981e640ee377cac493e69d8a6152725fffe9ff1aa1e0585035a170bebb31fc":
        raise RuntimeError("corrected navigation queue binding changed")
    navigation_ids = {item.get("normalized_identity") for item in correction["corrected_navigation_queue"].get("identities", [])}
    if len(navigation_ids) != 70:
        raise RuntimeError("corrected navigation exclusion identity count changed")
    rows = queue.get("rows")
    if not isinstance(rows, list) or len(rows) != QUEUE_COUNT:
        raise RuntimeError(f"static40 queue must contain exactly {QUEUE_COUNT} rows")
    normalized = []
    seen = set()
    for expected_rank, row in enumerate(rows, 1):
        if row.get("queue_rank") != expected_rank:
            raise RuntimeError("static40 queue ranks are not 1..40")
        item = validate_candidate(row)
        if item["original"] in seen or item["normalized_identity"] in seen:
            raise RuntimeError(f"static40 queue duplicate original: {item['original']}")
        if item["normalized_identity"] in navigation_ids:
            raise RuntimeError(f"static40 candidate overlaps corrected navigation exclusion: {item['original']}")
        seen.update({item["original"], item["normalized_identity"]})
        normalized.append(item)
    excluded = queue.get("excluded_targets") or []
    if len(excluded) != 1 or "small pets" not in excluded[0].get("requested_url", ""):
        raise RuntimeError("static40 literal-space exclusion is missing")
    return normalized, {
        "queue": binding(QUEUE_PATH, "prepared static40 source queue"),
        "source_audit": binding(audit_path, "frozen static-frontier-v32 audit"),
        "navigation_exclusion_correction": binding(correction_path, "frozen navigation exclusion correction"),
        "v32_provenance_sha256": audit["inputs"].get("v32_export_provenance_sha256"),
        "candidate_pool_count": len(audit["candidates"]),
        "excluded_literal_space_url": excluded[0]["requested_url"],
    }


def load_frozen_queue() -> tuple[dict, list[dict], dict]:
    if not QUEUE_PATH.is_file():
        raise RuntimeError(f"missing static40 queue: {QUEUE_PATH}")
    if sha256(QUEUE_PATH) != EXPECTED_QUEUE_SHA:
        raise RuntimeError("static40 queue SHA mismatch")
    queue = read_json(QUEUE_PATH)
    rows, sources = validate_queue_document(queue)
    return queue, rows, sources


def _resolve_status_pointer(status: dict, field: str) -> Path:
    value = status.get(field)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"recovery status has no {field}")
    path = Path(value)
    resolved = (ROOT / path if value.replace("\\", "/").startswith("research/") else RECOVERY / path).resolve()
    return _assert_under(resolved, ROOT, f"status pointer {field}")


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise RuntimeError(f"timestamp must include timezone: {value}")
    return parsed.astimezone(timezone.utc)


def load_runtime_bindings() -> tuple[dict, dict, Path, dict, Path, dict, int]:
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
        raise RuntimeError("latest source receipt has invalid failure tail")
    if isinstance(status.get("latest_failure_tail"), int) and status["latest_failure_tail"] != tail:
        raise RuntimeError("status/source failure tail mismatch")
    now = datetime.now(timezone.utc)
    for value in (status.get("network_cooldown_not_before_utc"), source.get("cooldown_not_before_utc")):
        deadline = _parse_time(value)
        if deadline and now < deadline:
            raise RuntimeError(f"network cooldown is active until {value}")
    control_path = _resolve_status_pointer(status, "latest_control_gate")
    if "control03" not in control_path.name.lower() or not control_path.is_file():
        raise RuntimeError(f"latest control gate is not CONTROL03: {control_path}")
    control = read_json(control_path)
    if not (control.get("accepted") is True and control.get("resume_gate_passed") is True and control.get("control_final_streak") == 0):
        raise RuntimeError("CONTROL03 gate is closed")
    if not V3_DRIVER_PATH.is_file() or sha256(V3_DRIVER_PATH) != EXPECTED_DRIVER_SHA:
        raise RuntimeError("frozen reusable-image-v3 driver SHA mismatch")
    runtime = {
        "status": binding(STATUS_PATH, "current recovery status snapshot"),
        "status_sha256": status_sha,
        "latest_source_acceptance": binding(source_path, "freshest accepted source receipt at factory invocation"),
        "latest_control_gate": binding(control_path, "current accepted CONTROL03 tail-zero gate"),
        "frozen_v3_driver": binding(V3_DRIVER_PATH, "frozen reusable-image-v3 driver"),
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
        raise RuntimeError("--batch-index must be an integer from 1 through 4")
    chunk = rows[(batch_index - 1) * BATCH_SIZE:batch_index * BATCH_SIZE]
    if len(chunk) != BATCH_SIZE:
        raise RuntimeError("static40 batch does not contain exactly ten targets")
    return chunk


def make_policy(tail: int) -> dict:
    return {
        "from": FROM_TS, "to": TO_TS, "limit": 500, "showResumeKey": True,
        "collapse": False, "matchType": "exact", "max_originals": 20,
        "max_attempts": 24, "window_seconds": 240.0,
        "max_total_body_bytes": 16 * 1024 * 1024,
        "max_entity_body_bytes": 8 * 1024 * 1024,
        "min_dispatch_seconds": 5.25, "min_request_start_seconds": 5.0,
        "disk_floor_bytes": DISK_FLOOR, "direct_first": True,
        "direct_attempt_budget": 4, "proxy_attempt_budget": 20,
        "proxy": PROXY, "tls_verification": True, "automatic_redirects": 0,
        "stop_http_codes": [429, 503], "cooldown_seconds": 120,
        "user_agent": "wow-recovery-reusable-image-v3/20261018-static40-v32",
        "prior_failure_tail": tail, "transport_policy": "batch_after_direct_failure",
        "no_network_before_parent_go": True,
    }


def make_candidate(item: dict, batch_index: int, local_no: int, queue: dict,
                   queue_sha: str, runtime: dict, status_ref: dict,
                   source_path: Path, source_sha: str, tail: int) -> dict:
    candidate = item["candidate"]
    original = item["original"]
    mime_types, formats, all_frames = expected_for(original)
    evidence = item["verified_references"]
    return {
        "target_key": f"STATIC40-V32-{batch_index:02d}-{local_no:02d}",
        "priority": local_no, "queue_rank": item["queue_rank"],
        "candidate_priority_rank": item["candidate_priority_rank"],
        "source_category": candidate.get("category"),
        "visual_role": candidate.get("visual_role"), "kind": "image",
        "original": original, "literal": original,
        "expected": {"archive_query_required": True, "mime_types": mime_types,
                      "pillow_formats": formats, "all_gif_frames": all_frames,
                      "reencode": False, "script_execution": False,
                      "query_window": {"from": FROM_TS, "to": TO_TS}},
        "expected_mime": mime_types,
        "source_evidence": {"path": evidence[0]["path"], "line": evidence[0]["line"],
                             "literal": original, "sha256": evidence[0]["sha256"],
                             "bytes": evidence[0]["bytes"], "source_page": evidence[0].get("source_page"),
                             "reason": evidence[0].get("reason"), "all_references": evidence},
        "source_page_context": {
            "candidate_file": rel(QUEUE_PATH), "candidate_file_sha256": queue_sha,
            "queue_rank": item["queue_rank"], "candidate_priority_rank": item["candidate_priority_rank"],
            "category": candidate.get("category"), "visual_role": candidate.get("visual_role"),
            "source_pages": copy.deepcopy(candidate.get("source_pages") or []),
            "source_output_page": candidate.get("source_output_page"),
            "source_output_page_sha256": candidate.get("source_output_page_sha256"),
            "references": copy.deepcopy(candidate.get("references") or []),
            "validated_references": evidence,
            "source_audit": queue.get("source_audit"),
            "navigation_exclusion_correction": queue.get("navigation_exclusion_correction"),
            "prior_attempt": candidate.get("prior_attempt"),
            "static_main01_cdx": copy.deepcopy(candidate.get("static_main01_cdx")),
            "existing_json_evidence": copy.deepcopy(candidate.get("existing_json_evidence")),
            "complete_cdx_cache": copy.deepcopy(candidate.get("complete_cdx_cache")),
            "current_source_receipt": binding(source_path, "freshest accepted source receipt at factory invocation"),
            "current_source_receipt_sha256": source_sha, "current_failure_tail": tail,
            "status_snapshot": status_ref,
        },
        "selection": {"max_distinct_digest_candidates": 2, "potential_truncation": "do_not_replay",
                       "require_complete_index": True, "require_exact_original": True,
                       "require_expected_mime": True, "require_nonempty_cdx_sha1_digest": True,
                       "require_statuscode": 200, "same_digest_older_captures": "skip",
                       "sort": "timestamp_desc_then_record_index_desc", "unknown_metadata": "incomplete_error"},
        "known_positive_cache_rows": [], "fallback_label": None, "cdx_mode": "fresh",
        "query": {"endpoint": "https://web.archive.org/cdx/search/cdx", "url": original,
                  "from": FROM_TS, "to": TO_TS, "output": "json", "fields": FIELDS,
                  "limit": 500, "showResumeKey": True, "collapse": False,
                  "matchType": "exact", "query_url": query_url(original)},
        "replay": {"enabled": True, "id_url_template": "https://web.archive.org/web/{timestamp}id_/" + original,
                   "max_candidates": 2, "no_redirects": True, "verify_tls": True,
                   "acceptance": ["http_status_200", "memento_datetime_present_and_exact",
                                  "link_original_exact_default_port_only", "expected_image_content_type",
                                  "magic_and_pillow_decode", "all_gif_frames_loaded",
                                  "decoded_payload_sha1_matches_cdx_digest"],
                   "accepted_payloads_are_source_data_only": True},
        "prior_local_evidence": [{"state": candidate.get("prior_attempt"),
                                  "source": "static-frontier-v32-candidates",
                                  "exact_entity_index_complete": False, "positive_row_count": 0}],
        "prior_evidence_status": "static40_v32_source_page_line_hash_bound; fresh_exact_cdx_required; no_bound_positive_fallback",
    }


def make_plan(batch_index: int, queue: dict, rows: list[dict], queue_sha: str,
              sources: dict, runtime: dict, status_ref: dict,
              source_path: Path, source_sha: str, tail: int) -> tuple[dict, dict, dict, dict]:
    chunk = select_batch(rows, batch_index)
    candidates = [make_candidate(item, batch_index, local_no, queue, queue_sha, runtime,
                                 status_ref, source_path, source_sha, tail)
                  for local_no, item in enumerate(chunk, 1)]
    batch_id = f"WAYBACK-CONTINUOUS-20261018-STATIC40-V32-{batch_index:02d}"
    batch_dir = FACTORY_ROOT / f"batch-{batch_index:02d}"
    bindings = {"static40_source_queue": sources["queue"],
                "static_frontier_v32_audit": sources["source_audit"],
                "navigation_exclusion_correction": sources["navigation_exclusion_correction"],
                "status": runtime["status"], "latest_source_acceptance": runtime["latest_source_acceptance"],
                "latest_control_gate": runtime["latest_control_gate"], "frozen_v3_driver": runtime["frozen_v3_driver"],
                "status_snapshot": status_ref}
    previous = {"name": "current_source_tail_and_CONTROL03", "prior_failure_tail": tail,
                "acceptance_receipt_path": rel(source_path), "acceptance_receipt_sha256": source_sha,
                "tail_receipt_path": rel(source_path), "tail_receipt_sha256": source_sha,
                "latest_successful_tail_end": tail, "historical_tail_is_preserved": True,
                "control_gate_receipt_path": runtime["latest_control_gate"]["path"],
                "control_gate_receipt_sha256": runtime["latest_control_gate"]["sha256"],
                "control_gate_required": True, "parent_go_required": True}
    plan = {"schema": "wow-recovery.reusable-image-plan.v1", "batch_id": batch_id,
            "prepared_utc": runtime["captured_utc"], "mode": "fresh_exact_cdx_then_id_replay_no_fallback",
            "network_authorized": None, "parent_go_required": True, "candidate_count": len(candidates),
            "output_dir": rel(batch_dir / "output"),
            "execution_order": {"batch_number": batch_index, "batch_count": BATCH_COUNT,
                                "predecessor_batch_required": batch_index > 1,
                                "predecessor_tail_rebind_required_before_execute": False,
                                "root_control_acceptance_bound": True, "parent_go_required": True},
            "selection_scope": {"name": f"static40_v32_batch_{batch_index:02d}",
                                "reason": "Ten exact originals from the prepared static40 queue; every page citation is locally SHA/line bound and the corrected navigation identities are excluded.",
                                "queue_path": rel(QUEUE_PATH), "queue_sha256": queue_sha,
                                "queue_target_count": QUEUE_COUNT,
                                "queue_rank_range": [chunk[0]["queue_rank"], chunk[-1]["queue_rank"]],
                                "selected_queue_ranks": [item["queue_rank"] for item in chunk],
                                "selected_candidate_priority_ranks": [item["candidate_priority_rank"] for item in chunk],
                                "network_requests_during_preparation": 0},
            "candidates": candidates, "policy": make_policy(tail), "previous_batch": previous,
            "input_bindings": bindings, "source_bindings": bindings,
            "excluded_rows": {"selected_queue_ranks": [item["queue_rank"] for item in chunk],
                              "other_queue_batch_ranks": [item["queue_rank"] for item in rows if item not in chunk],
                              "known_positive_fallback_rows": []},
            "identity_variant_policy": {"retain_in_cdx_report": True, "replay_identity_variants": False,
                                        "strict_identity": "exact_original_default_port_only",
                                        "scheme_or_host_variants_are_not_equivalent": True},
            "execution_boundary": {"no_network_authorized_by_this_artifact": True,
                                   "requires_parent_GO": True, "driver_not_invoked_by_factory": True}}
    bindings_doc = {"schema": "wow-recovery.reusable-image-input-bindings.v1", "batch_id": batch_id,
                    "plan_path": rel(batch_dir / "plan.json"), "plan_sha256": json_sha256(plan),
                    "driver_path": rel(V3_DRIVER_PATH), "driver_sha256": EXPECTED_DRIVER_SHA,
                    "selected_queue_ranks": [item["queue_rank"] for item in chunk],
                    "selected_originals": [item["original"] for item in candidates],
                    "source_bindings": bindings, "network_requests_during_preparation": 0,
                    "driver_execution": "not invoked by this factory"}
    cache = {"schema": "wow-recovery.static40-v32-cache-status.v1", "generated_utc": runtime["captured_utc"],
             "network_requests": 0, "raw_exact_cdx_cache_present": False, "raw_exact_cdx_cache_bound": False,
             "fresh_exact_cdx_required": True, "known_positive_fallback_available": False,
             "fallback_policy": "none; source queue contains page evidence only",
             "targets": [{"target_key": c["target_key"], "queue_rank": c["queue_rank"],
                          "original": c["original"], "cdx_mode": "fresh",
                          "fresh_query_url": c["query"]["query_url"], "replay_after_fresh_only": True,
                          "latest_unknown_on_transport_failure": True} for c in candidates],
             "queue_split": {"full_queue_count": QUEUE_COUNT, "batch_number": batch_index,
                             "batch_count": BATCH_COUNT, "batch_size": BATCH_SIZE},
             "planned_request_bound": 24, "planned_batch_duration_seconds": 240.0,
             "planned_total_body_bytes": 16 * 1024 * 1024, "planned_entity_body_bytes": 8 * 1024 * 1024,
             "stop_conditions": ["HTTP 429 or 503: stop and cool down at least 120 seconds",
                                 "five consecutive transport failures: stop and preserve tail",
                                 "disk free below 11005853696 bytes before request/write: stop",
                                 "fresh CDX incomplete/resume-key/unknown metadata: do not replay",
                                 "no execution until parent issues plan GO"], "source_bindings": bindings}
    selection = {"schema": "wow-recovery.static40-v32-selection.v1", "generated_utc": runtime["captured_utc"],
                 "queue": sources["queue"], "selected": [{"target_key": c["target_key"],
                 "queue_rank": c["queue_rank"], "candidate_priority_rank": c["candidate_priority_rank"],
                 "original": c["original"], "source_evidence": c["source_evidence"]} for c in candidates],
                 "selection_scope": plan["selection_scope"]}
    return plan, bindings_doc, cache, selection


def ensure_batch_available(batch_dir: Path) -> None:
    if batch_dir.exists():
        raise RuntimeError(f"requested static40 batch already exists; refusing overwrite: {batch_dir}")


def write_batch_atomic(batch_index: int, documents: dict[str, dict]) -> dict:
    if shutil.disk_usage(ROOT).free < DISK_FLOOR:
        raise RuntimeError("D-drive free space is below the required floor")
    factory_root = _assert_under(FACTORY_ROOT, ROOT, "factory root")
    factory_root.mkdir(parents=True, exist_ok=True)
    batch_dir = _assert_under(factory_root / f"batch-{batch_index:02d}", factory_root, "batch target")
    ensure_batch_available(batch_dir)
    temp_dir = _assert_under(Path(tempfile.mkdtemp(prefix=f".batch-{batch_index:02d}-", dir=factory_root)), factory_root, "atomic temporary directory")
    try:
        hashes = {}
        for name, value in documents.items():
            path = _assert_under(temp_dir / name, temp_dir, f"document {name}")
            path.parent.mkdir(parents=True, exist_ok=True)
            write_json(path, value)
            hashes[name] = {"path": rel(batch_dir / name), "sha256": sha256(path), "bytes": path.stat().st_size}
        if shutil.disk_usage(ROOT).free < DISK_FLOOR:
            raise RuntimeError("D-drive free space fell below the required floor")
        ensure_batch_available(batch_dir)
        _assert_under(temp_dir, factory_root, "atomic temporary directory")
        _assert_under(batch_dir, factory_root, "batch target")
        os.replace(temp_dir, batch_dir)
        return {"batch_dir": rel(batch_dir), "files": hashes, "network_requests": 0}
    except Exception:
        _assert_under(temp_dir, factory_root, "atomic cleanup directory")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def prepare_documents(batch_index: int) -> tuple[dict, dict[str, dict]]:
    queue, rows, sources = load_frozen_queue()
    status, source, source_path, control, control_path, runtime, tail = load_runtime_bindings()
    batch_dir = FACTORY_ROOT / f"batch-{batch_index:02d}"
    ensure_batch_available(batch_dir)
    snapshot = {"schema": "wow-recovery.static40-v32-status-snapshot.v1",
                "captured_utc": runtime["captured_utc"], "active_status_path": rel(STATUS_PATH),
                "active_status_sha256": runtime["status_sha256"],
                "latest_source_acceptance": runtime["latest_source_acceptance"],
                "latest_control_gate": runtime["latest_control_gate"],
                "latest_failure_tail": tail, "network_requests_during_preparation": 0}
    snapshot_ref = {"path": rel(batch_dir / "status-snapshot.json"), "sha256": json_sha256(snapshot),
                    "bytes": len(json_bytes(snapshot)), "role": "atomic batch-local status snapshot"}
    plan, bindings, cache, selection = make_plan(batch_index, queue, rows, sha256(QUEUE_PATH), sources,
                                                 runtime, snapshot_ref, source_path, sha256(source_path), tail)
    return plan, {"status-snapshot.json": snapshot, "plan.json": plan,
                  "input-bindings.json": bindings, "cache-status.json": cache,
                  "selection-manifest.json": selection}


def parse_batch_index() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-index", type=int, required=True, help="1-based ten-target batch index (1..4)")
    args = parser.parse_args()
    if isinstance(args.batch_index, bool) or not 1 <= args.batch_index <= BATCH_COUNT:
        parser.error("--batch-index must be an integer from 1 through 4")
    return args.batch_index


def main() -> None:
    batch_index = parse_batch_index()
    plan, documents = prepare_documents(batch_index)
    result = write_batch_atomic(batch_index, documents)
    print(json.dumps({"batch_index": batch_index, "batch_id": plan["batch_id"],
                      "queue_sha256": EXPECTED_QUEUE_SHA, "candidate_count": plan["candidate_count"],
                      "selected_queue_ranks": plan["selection_scope"]["selected_queue_ranks"],
                      "batch": result, "network_requests": 0}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

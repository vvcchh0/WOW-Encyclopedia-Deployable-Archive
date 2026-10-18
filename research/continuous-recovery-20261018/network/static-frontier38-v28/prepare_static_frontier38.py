"""Prepare one offline fresh-exact plan from the immutable static-frontier38 queue.

The factory only reads the root-accepted queue, local citation pages, recovery
status, and frozen reusable-image-v3/template inputs.  It writes a batch-local
status snapshot and a ten-target plan (eight targets in the final batch).  It
never starts curl; execution still requires an explicit parent GO.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
RECOVERY = ROOT / "research" / "continuous-recovery-20261018"
NETWORK = RECOVERY / "network"
FACTORY_ROOT = NETWORK / "static-frontier38-v28"

QUEUE_PATH = RECOVERY / "publication" / "static-frontier-selected38.json"
SOURCE_AUDIT_PATH = RECOVERY / "local-audit" / "static-frontier-v28" / "static-frontier-v28-candidates.json"
STATUS_PATH = RECOVERY / "status.json"
TEMPLATE_PLAN_PATH = NETWORK / "news-unplanned-v26" / "batch-02" / "plan.json"
V3_DRIVER_PATH = NETWORK / "reusable-image-driver-v3" / "reusable_image_driver.py"
CONTROL_PROBE_PATH = NETWORK / "control-after-gallery15" / "control-report.json"

FROM_TS = "20000101000000"
TO_TS = "20080512210044"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
DISK_FLOOR = 11_005_853_696
BATCH_SIZE = 10
QUEUE_COUNT = 38


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def binding(path: Path, role: str) -> dict:
    return {"path": rel(path), "sha256": sha256(path), "bytes": path.stat().st_size, "role": role}


def resolve_status_pointer(status: dict, field: str) -> Path:
    value = status.get(field)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"recovery status has no {field}")
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    if value.replace("\\", "/").startswith("research/"):
        return ROOT / candidate
    return RECOVERY / candidate


def load_latest_source() -> tuple[dict, str, Path, dict, str, int]:
    if not STATUS_PATH.is_file():
        raise RuntimeError(f"missing recovery status: {STATUS_PATH}")
    status = read_json(STATUS_PATH)
    status_sha = sha256(STATUS_PATH)
    source_field = "latest_source_acceptance" if status.get("latest_source_acceptance") else "last_image_source_acceptance"
    receipt_path = resolve_status_pointer(status, source_field)
    if not receipt_path.is_file():
        raise RuntimeError(f"latest source receipt is missing: {receipt_path}")
    receipt = read_json(receipt_path)
    receipt_sha = sha256(receipt_path)
    if receipt.get("accepted") is not True:
        raise RuntimeError(f"latest source receipt is not accepted: {receipt_path}")
    tail = receipt.get("failure_streak_end")
    if isinstance(tail, bool) or not isinstance(tail, int) or not 0 <= tail <= 4:
        raise RuntimeError(f"latest source receipt has an invalid failure tail: {receipt_path}")
    return status, status_sha, receipt_path, receipt, receipt_sha, tail


def load_latest_control_gate(status: dict) -> tuple[Path, dict, str]:
    gate_path = resolve_status_pointer(status, "latest_control_gate")
    if not gate_path.is_file():
        raise RuntimeError(f"latest control gate is missing: {gate_path}")
    gate = read_json(gate_path)
    gate_sha = sha256(gate_path)
    if (gate.get("accepted") is not True or gate.get("resume_gate_passed") is not True
            or gate.get("control_final_streak") != 0):
        raise RuntimeError(f"latest control gate is not an accepted tail-zero gate: {gate_path}")
    return gate_path, gate, gate_sha


def split_source_reference(ref: dict, original: str, expected_page_sha: str | None) -> dict:
    output_file = ref.get("output_file")
    line_number = ref.get("line")
    if not isinstance(output_file, str) or not output_file:
        raise RuntimeError(f"static citation has no output_file: {original}")
    if isinstance(line_number, bool) or not isinstance(line_number, int) or line_number < 1:
        raise RuntimeError(f"static citation has no valid line: {original}")
    path = ROOT / output_file
    if not path.is_file():
        raise RuntimeError(f"static citation file is missing: {path}")
    actual = sha256(path)
    if expected_page_sha and actual != expected_page_sha:
        raise RuntimeError(f"static citation SHA mismatch: {path}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    line = lines[line_number - 1] if line_number <= len(lines) else ""
    encoded = quote(original, safe="")
    if line_number > len(lines) or (original not in line and encoded not in line):
        raise RuntimeError(f"static citation line does not bind requested URL: {path}:{line_number}")
    return {
        "path": output_file.replace("\\", "/"),
        "line": line_number,
        "sha256": actual,
        "bytes": path.stat().st_size,
        "literal": original,
        "source_page": ref.get("source_page"),
        "reason": ref.get("reason"),
    }


def source_evidence(row: dict, original: str) -> tuple[dict, list[dict]]:
    refs = row.get("references") or []
    if not refs:
        raise RuntimeError(f"static queue row has no source references: {original}")
    page_sha = str(row.get("source_output_page_sha256") or "")
    verified = [split_source_reference(ref, original, page_sha) for ref in refs]
    primary = verified[0]
    evidence = {
        "path": primary["path"],
        "line": primary["line"],
        "literal": original,
        "sha256": primary["sha256"],
        "bytes": primary["bytes"],
        "source_page": primary.get("source_page"),
        "reason": primary.get("reason"),
        "all_references": verified,
    }
    return evidence, verified


def query_url(original: str) -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(original, safe="")
        + f"&from={FROM_TS}&to={TO_TS}&output=json&fl=" + quote(",".join(FIELDS), safe="")
        + "&limit=500&showResumeKey=true&matchType=exact"
    )


def expected_for(original: str) -> tuple[list[str], list[str], bool]:
    suffix = Path(urlsplit(original).path).suffix.lower()
    if suffix == ".gif":
        return ["image/gif"], ["GIF"], True
    if suffix == ".png":
        return ["image/png"], ["PNG"], False
    if suffix in {".jpg", ".jpeg"}:
        return ["image/jpeg"], ["JPEG"], False
    return ["image/jpeg", "image/gif", "image/png"], ["JPEG", "GIF", "PNG"], True


def prior_attempt_summary(row: dict) -> dict:
    return {
        "prior_attempt": row.get("prior_attempt"),
        "cdx_state": row.get("cdx_state"),
        "static_main01_cdx": copy.deepcopy(row.get("static_main01_cdx")),
        "known_cdx_or_replay_date": row.get("known_cdx_or_replay_date"),
        "complete_cdx_cache": copy.deepcopy(row.get("complete_cdx_cache")),
    }


def make_candidate(row: dict, batch_index: int, local_no: int, queue_sha: str,
                   queue: dict, status_snapshot_path: Path, status_snapshot_sha: str,
                   receipt_path: Path, receipt_sha: str, tail: int,
                   source_audit_ref: dict, control_probe_ref: dict) -> dict:
    original = str(row["requested_url"])
    mime_types, pillow_formats, all_gif_frames = expected_for(original)
    evidence, verified_refs = source_evidence(row, original)
    target_key = f"STATIC-FRONTIER-V28-{batch_index:02d}-{local_no:02d}"
    queue_row_provenance = {
        "rank": row.get("rank"),
        "priority_rank": row.get("priority_rank"),
        "requested_url": row.get("requested_url"),
        "normalized_identity": row.get("normalized_identity"),
        "category": row.get("category"),
        "visual_role": row.get("visual_role"),
        "source_pages": copy.deepcopy(row.get("source_pages") or []),
        "source_output_page": row.get("source_output_page"),
        "source_output_page_sha256": row.get("source_output_page_sha256"),
        "source_output_page_bytes": row.get("source_output_page_bytes"),
        "references": verified_refs,
        "prior_attempt": row.get("prior_attempt"),
        "static_main01_cdx": copy.deepcopy(row.get("static_main01_cdx")),
        "existing_json_evidence": copy.deepcopy(row.get("existing_json_evidence")),
        "complete_cdx_cache": copy.deepcopy(row.get("complete_cdx_cache")),
        "known_cdx_or_replay_date": row.get("known_cdx_or_replay_date"),
        "selection_note": row.get("selection_note"),
        "cdx_state": row.get("cdx_state"),
    }
    return {
        "target_key": target_key,
        "priority": local_no,
        "queue_rank": row["rank"],
        "static_priority_rank": row.get("priority_rank"),
        "source_category": row.get("category"),
        "visual_role": row.get("visual_role"),
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
        "source_evidence": evidence,
        "source_page_context": {
            "candidate_file": rel(QUEUE_PATH),
            "candidate_file_sha256": queue_sha,
            "queue_accepted": queue.get("accepted"),
            "queue_checked_utc": queue.get("checked_utc"),
            "queue_scope": queue.get("scope"),
            "static_queue_rank": row.get("rank"),
            "priority_rank": row.get("priority_rank"),
            "category": row.get("category"),
            "visual_role": row.get("visual_role"),
            "source_pages": copy.deepcopy(row.get("source_pages") or []),
            "source_output_page": row.get("source_output_page"),
            "source_output_page_sha256": row.get("source_output_page_sha256"),
            "source_output_page_bytes": row.get("source_output_page_bytes"),
            "references": verified_refs,
            "source_audit": source_audit_ref,
            "prior_attempt_summary": prior_attempt_summary(row),
            "previous_batch_tail_receipt": rel(receipt_path),
            "previous_batch_tail_receipt_sha256": receipt_sha,
            "previous_batch_tail_end": tail,
            "status_snapshot_path": rel(status_snapshot_path),
            "status_snapshot_sha256": status_snapshot_sha,
            "control_probe_after_retry2": control_probe_ref,
        },
        "queue_row_provenance": queue_row_provenance,
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
            "state": row.get("cdx_state"),
            "source": "static-frontier-selected38",
            "prior_attempt": prior_attempt_summary(row),
            "exact_entity_index_complete": False,
            "positive_row_count": 0,
        }],
        "prior_evidence_status": "static_frontier_v28_queue; source_page_line_hash_bound; fresh_exact_cdx_required; no_bound_positive_fallback",
    }


def make_policy(prior_tail: int) -> dict:
    return {
        "from": FROM_TS,
        "to": TO_TS,
        "limit": 500,
        "showResumeKey": True,
        "collapse": False,
        "matchType": "exact",
        "max_originals": 20,
        "max_attempts": 24,
        "window_seconds": 240.0,
        "max_total_body_bytes": 16 * 1024 * 1024,
        "max_entity_body_bytes": 8 * 1024 * 1024,
        "min_dispatch_seconds": 5.25,
        "min_request_start_seconds": 5.0,
        "disk_floor_bytes": DISK_FLOOR,
        "direct_first": True,
        "proxy": "http://127.0.0.1:7890",
        "tls_verification": True,
        "automatic_redirects": 0,
        "stop_http_codes": [429, 503],
        "cooldown_seconds": 120,
        "user_agent": "wow-recovery-reusable-image-v3/20261018-static-frontier-v28",
        "prior_failure_tail": prior_tail,
        "transport_policy": "batch_after_direct_failure",
        "no_network_before_parent_go": True,
    }


def parse_batch_index() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-index", type=int, required=True, help="1-based ten-target queue batch index")
    args = parser.parse_args()
    if args.batch_index < 1:
        parser.error("--batch-index must be >= 1")
    return args.batch_index


def main() -> None:
    batch_index = parse_batch_index()
    required = [QUEUE_PATH, SOURCE_AUDIT_PATH, STATUS_PATH, TEMPLATE_PLAN_PATH, V3_DRIVER_PATH, CONTROL_PROBE_PATH]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("missing bound input(s): " + ", ".join(missing))

    queue = read_json(QUEUE_PATH)
    rows = sorted(queue.get("rows") or [], key=lambda item: int(item["rank"]))
    if queue.get("accepted") is not True or queue.get("network_requests") != 0:
        raise RuntimeError("root-accepted static frontier queue is missing acceptance or is not offline")
    if len(rows) != QUEUE_COUNT:
        raise RuntimeError(f"expected exactly {QUEUE_COUNT} static frontier rows, got {len(rows)}")
    if [row.get("rank") for row in rows] != list(range(1, QUEUE_COUNT + 1)):
        raise RuntimeError("static frontier queue ranks are not the expected 1..38 sequence")
    originals = [row.get("requested_url") for row in rows]
    if any(not isinstance(url, str) or not url.startswith(("http://", "https://")) for url in originals):
        raise RuntimeError("static frontier queue contains a malformed original URL")
    if len(set(originals)) != QUEUE_COUNT:
        raise RuntimeError("static frontier queue contains duplicate requested URLs")
    queue_sha = sha256(QUEUE_PATH)
    source_audit_ref = binding(SOURCE_AUDIT_PATH, "frozen static-frontier-v28 source audit behind the accepted 38-row queue")

    status, status_sha, receipt_path, receipt, receipt_sha, prior_tail = load_latest_source()
    control_gate_path, control_gate, control_gate_sha = load_latest_control_gate(status)
    latest_ref = binding(receipt_path, "latest accepted image-source receipt selected from recovery status")
    control_ref = binding(control_gate_path, "fresh root-accepted tail-zero CONTROL03 gate selected from recovery status")
    control_probe_ref = binding(CONTROL_PROBE_PATH, "local CONTROL03 report retained as supplemental connectivity evidence")
    queue_ref = binding(QUEUE_PATH, "root-accepted immutable 38-row static-frontier queue")
    template_ref = binding(TEMPLATE_PLAN_PATH, "accepted V3-compatible reusable-image plan structure")
    driver_ref = binding(V3_DRIVER_PATH, "frozen reusable-image-v3 driver")
    prepared_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    batch_count = math.ceil(len(rows) / BATCH_SIZE)
    start = (batch_index - 1) * BATCH_SIZE
    if start >= len(rows):
        raise RuntimeError(f"batch index {batch_index} is outside the frozen queue")
    chunk = rows[start:start + BATCH_SIZE]
    if not chunk or len(chunk) > BATCH_SIZE:
        raise RuntimeError("selected static frontier batch is outside the ten-target bound")
    batch_dir = FACTORY_ROOT / f"batch-{batch_index:02d}"
    output_dir = batch_dir / "output"
    if output_dir.is_dir() and any(output_dir.iterdir()):
        raise RuntimeError(f"executed batch output is immutable; refusing to overwrite: {output_dir}")

    status_snapshot_path = batch_dir / "status-snapshot.json"
    status_snapshot = {
        "schema": "wow-recovery.static-frontier38-v28-status-snapshot.v1",
        "captured_utc": prepared_utc,
        "active_status_path": rel(STATUS_PATH),
        "active_status_sha256_audit": status_sha,
        "active_status_latest_source_acceptance_pointer": status.get("latest_source_acceptance"),
        "active_status_last_image_source_acceptance_pointer": status.get("last_image_source_acceptance"),
        "latest_source_acceptance": latest_ref,
        "latest_control_gate_from_status": control_ref,
        "control_probe_after_retry2": control_probe_ref,
        "root_control_acceptance_bound": True,
        "root_control_acceptance_required_before_execute": False,
        "parent_go_required": True,
        "latest_failure_tail": prior_tail,
        "latest_source_batch_id": receipt.get("batch_id"),
        "latest_control_batch_id": control_gate.get("batch_id"),
        "network_requests_during_preparation": 0,
    }
    write_json(status_snapshot_path, status_snapshot)
    status_snapshot_sha = sha256(status_snapshot_path)
    status_snapshot_ref = binding(status_snapshot_path, "immutable batch-local snapshot of status pointers and pending CONTROL03 rebind")

    batch_id = f"WAYBACK-CONTINUOUS-20261018-STATIC-FRONTIER-V28-{batch_index:02d}"
    candidates = [
        make_candidate(row, batch_index, local_no, queue_sha, queue, status_snapshot_path,
                       status_snapshot_sha, receipt_path, receipt_sha, prior_tail,
                       source_audit_ref, control_probe_ref)
        for local_no, row in enumerate(chunk, 1)
    ]
    bindings = {
        "static_frontier_selected38_queue": queue_ref,
        "static_frontier_v28_source_audit": source_audit_ref,
        "status_snapshot": status_snapshot_ref,
        "latest_actual_source_acceptance": latest_ref,
        "latest_control_gate_from_status": control_ref,
        "control_probe_after_retry2": control_probe_ref,
        "template_plan": template_ref,
        "frozen_v3_driver": driver_ref,
    }
    previous_batch = {
        "name": receipt.get("batch_id") or "latest_actual_source_acceptance",
        "prior_failure_tail": prior_tail,
        "acceptance_receipt_path": rel(receipt_path),
        "acceptance_receipt_sha256": receipt_sha,
        "tail_receipt_path": rel(receipt_path),
        "tail_receipt_sha256": receipt_sha,
        "latest_successful_tail_end": prior_tail,
        "historical_tail_is_preserved": True,
        "ordinary_retrieval_requires_new_control_gate": False,
        "control_gate_receipt_path": rel(control_gate_path),
        "control_gate_receipt_sha256": control_gate_sha,
        "control_gate_required": True,
        "control_gate_rebind_required_before_execute": False,
        "pending_control_probe_path": rel(CONTROL_PROBE_PATH),
        "pending_control_probe_sha256": sha256(CONTROL_PROBE_PATH),
        "pending_control_probe_positive": True,
        "root_control_acceptance_bound": True,
        "root_control_acceptance_required_before_execute": False,
        "parent_go_required": True,
    }
    plan = {
        "schema": "wow-recovery.reusable-image-plan.v1",
        "batch_id": batch_id,
        "prepared_utc": prepared_utc,
        "mode": "fresh_exact_cdx_then_id_replay_no_fallback",
        "network_authorized": None,
        "parent_go_required": True,
        "candidate_count": len(candidates),
        "output_dir": rel(output_dir),
        "execution_order": {
            "batch_number": batch_index,
            "batch_count": batch_count,
            "predecessor_batch_required": batch_index > 1,
            "predecessor_tail_rebind_required_before_execute": False,
            "predecessor_tail_status": "bound_to_latest_actual_source_acceptance",
            "root_control_acceptance_bound": True,
            "root_control_acceptance_required_before_execute": False,
            "parent_go_required": True,
        },
        "selection_scope": {
            "name": f"static_frontier38_v28_batch_{batch_index:02d}",
            "reason": "Consecutive exact originals from the root-accepted immutable static-frontier38 queue; every queue source page, line, and page hash is retained per candidate.",
            "queue_path": rel(QUEUE_PATH),
            "queue_sha256": queue_sha,
            "queue_checked_utc": queue.get("checked_utc"),
            "queue_scope": queue.get("scope"),
            "queue_selection": queue.get("selection"),
            "queue_target_count": len(rows),
            "queue_rank_range": [chunk[0]["rank"], chunk[-1]["rank"]],
            "selected_queue_ranks": [row["rank"] for row in chunk],
            "selected_categories": [row.get("category") for row in chunk],
            "source_audit": source_audit_ref,
            "no_complete_same_window_row_selected": True,
            "network_requests_during_preparation": 0,
            "split_reason": "Ten-target batches keep each window inside the 24-request/240-second/16MiB V3 envelope; the final batch contains eight rows.",
        },
        "candidates": candidates,
        "policy": make_policy(prior_tail),
        "previous_batch": previous_batch,
        "input_bindings": bindings,
        "source_bindings": bindings,
        "excluded_rows": {
            "selected_queue_ranks": [row["rank"] for row in chunk],
            "other_queue_batch_ranks": [row["rank"] for row in rows if row not in chunk],
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
            "control_probe_is_not_a_root_acceptance": True,
        },
    }
    plan_path = batch_dir / "plan.json"
    write_json(plan_path, plan)

    bindings_doc = {
        "schema": "wow-recovery.reusable-image-input-bindings.v1",
        "batch_id": batch_id,
        "plan_path": rel(plan_path),
        "plan_sha256": sha256(plan_path),
        "driver_path": rel(V3_DRIVER_PATH),
        "driver_sha256": sha256(V3_DRIVER_PATH),
        "fixture_mode": "not duplicated; use the already accepted V3 offline contract",
        "inherited_tail": {
            "latest_actual_source_tail": prior_tail,
            "prior_failure_tail": prior_tail,
            "tail_receipt": rel(receipt_path),
            "tail_receipt_sha256": receipt_sha,
            "status_snapshot": rel(status_snapshot_path),
            "status_snapshot_sha256": status_snapshot_sha,
            "active_status_sha256_audit": status_sha,
            "control_gate_receipt": rel(control_gate_path),
            "control_gate_sha256": control_gate_sha,
            "control_probe_after_retry2": rel(CONTROL_PROBE_PATH),
            "control_probe_sha256": sha256(CONTROL_PROBE_PATH),
            "root_control_acceptance_bound": True,
            "root_control_acceptance_required_before_execute": False,
            "parent_go_required": True,
        },
        "predecessor_tail_rebind_required_before_execute": False,
        "predecessor_tail_status": "bound_to_latest_actual_source_acceptance",
        "selected_queue_ranks": [row["rank"] for row in chunk],
        "selected_originals": [row["requested_url"] for row in chunk],
        "source_bindings": bindings,
        "driver_bytes": V3_DRIVER_PATH.stat().st_size,
        "network_requests_during_preparation": 0,
    }
    bindings_path = batch_dir / "input-bindings.json"
    write_json(bindings_path, bindings_doc)

    cache_status = {
        "schema": "wow-recovery.static-frontier38-v28-cache-status.v1",
        "generated_utc": prepared_utc,
        "network_requests": 0,
        "raw_exact_cdx_cache_present": False,
        "raw_exact_cdx_cache_bound": False,
        "reason": "The accepted static-frontier queue contains source-page evidence only. Each target requires a fresh exact CDX HTTP 200 before id_ replay.",
        "fresh_exact_cdx_required": True,
        "known_positive_fallback_available": False,
        "fallback_policy": "none; no bound positive rows in this queue",
        "latestness": "unknown_until_fresh_exact_cdx_http_200_complete_sub_limit_no_resume",
        "targets": [
            {
                "target_key": candidate["target_key"],
                "queue_rank": candidate["queue_rank"],
                "original": candidate["original"],
                "cdx_mode": "fresh",
                "fresh_query_url": candidate["query"]["query_url"],
                "known_positive_cache_rows": [],
                "replay_after_fresh_only": True,
                "latest_unknown_on_transport_failure": True,
            }
            for candidate in candidates
        ],
        "queue_split": {"full_queue_count": len(rows), "batch_number": batch_index, "batch_count": batch_count, "batch_size": BATCH_SIZE},
        "planned_request_bound": 24,
        "planned_batch_duration_seconds": 240.0,
        "planned_total_body_bytes": 16 * 1024 * 1024,
        "planned_entity_body_bytes": 8 * 1024 * 1024,
        "stop_conditions": [
            "HTTP 429 or 503: stop batch and cool down at least 120 seconds",
            "five consecutive transport failures: stop batch and preserve tail",
            "disk free below 11005853696 bytes before any request/write: stop",
            "request, body, or duration budget clamp: stop and preserve unprocessed queue rows",
            "fresh CDX incomplete/resume-key/unknown metadata: do not replay that target",
            "no execution until parent issues plan GO",
        ],
        "source_bindings": bindings,
    }
    cache_path = batch_dir / "cache-status.json"
    write_json(cache_path, cache_status)

    selection_manifest = {
        "schema": "wow-recovery.static-frontier38-v28-selection.v1",
        "generated_utc": prepared_utc,
        "queue": queue_ref,
        "source_audit": source_audit_ref,
        "selected": [
            {
                "target_key": candidate["target_key"],
                "queue_rank": candidate["queue_rank"],
                "priority_rank": candidate["static_priority_rank"],
                "category": candidate["source_category"],
                "original": candidate["original"],
                "source_page_context": candidate["source_page_context"],
            }
            for candidate in candidates
        ],
        "selection_scope": plan["selection_scope"],
        "excluded_from_this_batch": [row["rank"] for row in rows if row not in chunk],
    }
    selection_path = batch_dir / "selection-manifest.json"
    write_json(selection_path, selection_manifest)

    manifest = {
        "schema": "wow-recovery.static-frontier38-v28-plan-manifest.v1",
        "generated_utc": prepared_utc,
        "queue": queue_ref,
        "source_audit": source_audit_ref,
        "status_snapshot": status_snapshot_ref,
        "active_status_sha256_audit": status_sha,
        "latest_actual_source_acceptance": latest_ref,
        "latest_control_gate_from_status": control_ref,
        "control_probe_after_retry2": control_probe_ref,
        "frozen_v3_driver": driver_ref,
        "batch_index": batch_index,
        "batch_count": batch_count,
        "plan": {"path": rel(plan_path), "sha256": sha256(plan_path)},
        "bindings": {"path": rel(bindings_path), "sha256": sha256(bindings_path)},
        "cache_status": {"path": rel(cache_path), "sha256": sha256(cache_path)},
        "selection_manifest": {"path": rel(selection_path), "sha256": sha256(selection_path)},
        "network_requests_during_preparation": 0,
        "execution_boundary": {
            "no_network_authorized_by_this_artifact": True,
            "requires_parent_GO": True,
            "requires_new_root_control_acceptance": False,
            "root_control_acceptance_bound": True,
            "max_attempts": 24,
            "max_seconds": 240.0,
            "batch_size": BATCH_SIZE,
            "final_batch_size": len(rows) % BATCH_SIZE or BATCH_SIZE,
            "executed_batch_output_is_immutable": True,
        },
    }
    manifest_path = FACTORY_ROOT / "plan-manifest.json"
    write_json(manifest_path, manifest)
    print(json.dumps({
        "batch_index": batch_index,
        "batch_id": batch_id,
        "queue_sha256": queue_sha,
        "source_audit_sha256": source_audit_ref["sha256"],
        "latest_source_acceptance": latest_ref,
        "latest_control_gate_from_status": control_ref,
        "control_probe_after_retry2": control_probe_ref,
        "root_control_acceptance_bound": True,
        "root_control_acceptance_required_before_execute": False,
        "parent_go_required": True,
        "status_snapshot": status_snapshot_ref,
        "latest_source_tail": prior_tail,
        "plan": rel(plan_path),
        "plan_sha256": sha256(plan_path),
        "bindings": rel(bindings_path),
        "bindings_sha256": sha256(bindings_path),
        "cache_status": rel(cache_path),
        "selection_manifest": rel(selection_path),
        "manifest": rel(manifest_path),
        "driver_sha256": driver_ref["sha256"],
        "candidate_count": len(candidates),
        "selected_queue_ranks": [row["rank"] for row in chunk],
        "network_requests": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

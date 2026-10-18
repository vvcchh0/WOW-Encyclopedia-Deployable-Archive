"""Prepare popup24 batch plans from a frozen relative-argument queue.

This is an offline-only factory.  The queue's ``original`` values are
resolved from the literal ``popUpOmega`` arguments on the cited source pages;
the URL-list is therefore the primary exact-URL evidence and every source-page
reference is retained separately for the popup-specific gate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[4]
RECOVERY = ROOT / "research" / "continuous-recovery-20261018"
NETWORK = RECOVERY / "network"
FACTORY_ROOT = NETWORK / "popup24-v30"

QUEUE_PATH = RECOVERY / "publication" / "popup24-selected-queue.json"
ORIGINALS_PATH = RECOVERY / "publication" / "popup24-original-urls.txt"
STATUS_PATH = RECOVERY / "status.json"
TEMPLATE_PLAN_PATH = NETWORK / "next-frontier70-v29" / "batch-07" / "plan.json"
V3_DRIVER_PATH = NETWORK / "reusable-image-driver-v3" / "reusable_image_driver.py"

EXPECTED_QUEUE_SHA = "e3e708048aff5fce88cbb65f96fdc0ed6f08817f21598c71c0db7fff550153ad"
EXPECTED_ORIGINALS_SHA = "d64d8f6eddba957261d3b59fa8dac6544c05bd3c452d84abf6196967ab64d561"

FROM_TS = "20000101000000"
TO_TS = "20080512210044"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
DISK_FLOOR = 11_005_853_696
BATCH_SIZE = 10
QUEUE_COUNT = 24


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
    return {"path": rel(path), "sha256": sha256(path), "role": role}


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
    status = read_json(STATUS_PATH)
    status_sha = sha256(STATUS_PATH)
    field = "latest_source_acceptance" if status.get("latest_source_acceptance") else "last_image_source_acceptance"
    receipt_path = resolve_status_pointer(status, field)
    receipt = read_json(receipt_path)
    receipt_sha = sha256(receipt_path)
    if receipt.get("accepted") is not True:
        raise RuntimeError(f"latest source receipt is not accepted: {receipt_path}")
    tail = receipt.get("failure_streak_end")
    if isinstance(tail, bool) or not isinstance(tail, int) or not 0 <= tail <= 4:
        raise RuntimeError(f"invalid latest source failure tail: {receipt_path}")
    return status, status_sha, receipt_path, receipt, receipt_sha, tail


def load_latest_control_gate(status: dict) -> tuple[Path, dict, str]:
    path = resolve_status_pointer(status, "latest_control_gate")
    gate = read_json(path)
    gate_sha = sha256(path)
    if (gate.get("accepted") is not True or gate.get("resume_gate_passed") is not True
            or gate.get("control_final_streak") != 0):
        raise RuntimeError(f"latest control gate is not accepted tail-zero: {path}")
    return path, gate, gate_sha


def validate_source_reference(row: dict, ref: dict, original: str, literal: str) -> dict:
    relative_path = ref.get("output_file")
    line_number = ref.get("line")
    expected_page_sha = ref.get("source_page_sha256")
    source_page = ref.get("source_page")
    if not isinstance(relative_path, str) or not relative_path or Path(relative_path).is_absolute():
        raise RuntimeError(f"invalid source output_file for rank {row.get('rank')}")
    if isinstance(line_number, bool) or not isinstance(line_number, int) or line_number < 1:
        raise RuntimeError(f"invalid source line for rank {row.get('rank')}")
    if not isinstance(expected_page_sha, str) or len(expected_page_sha) != 64:
        raise RuntimeError(f"invalid source page SHA for rank {row.get('rank')}")
    if source_page != row.get("source_base_url"):
        raise RuntimeError(f"source page/base mismatch for rank {row.get('rank')}")
    path = ROOT / relative_path
    if not path.is_file():
        raise RuntimeError(f"missing cited source page: {path}")
    actual_page_sha = sha256(path)
    if actual_page_sha != expected_page_sha:
        raise RuntimeError(f"source page SHA mismatch for {path}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if line_number > len(lines):
        raise RuntimeError(f"source line is out of range: {path}:{line_number}")
    line = lines[line_number - 1]
    encoded_literal = quote(literal, safe="")
    if literal not in line and encoded_literal not in line:
        raise RuntimeError(f"source line does not contain popup literal: {path}:{line_number}")
    resolved = urljoin(row["source_base_url"], literal)
    if resolved != original:
        raise RuntimeError(f"urljoin mismatch for rank {row.get('rank')}: {resolved} != {original}")
    return {
        "reference_index": 1,
        "path": relative_path,
        "line": line_number,
        "sha256": actual_page_sha,
        "source_page_sha256": expected_page_sha,
        "source_page": source_page,
        "source_base_url": row["source_base_url"],
        "literal": literal,
        "popup_helper": ref.get("popup_helper"),
        "requested": original,
        "resolved_url": resolved,
        "resolved_matches_original": True,
        "source_line_contains_literal": True,
        "source_marker": "popup24_relative_popUpOmega_reference",
    }


def validate_queue(queue: dict) -> tuple[list[dict], list[str], str, list[str]]:
    if queue.get("accepted") is not True or queue.get("network_requests") != 0:
        raise RuntimeError("popup24 queue is not an accepted offline queue")
    if queue.get("target_count") != QUEUE_COUNT:
        raise RuntimeError(f"popup24 queue target_count is not {QUEUE_COUNT}")
    rows = sorted(queue.get("rows") or [], key=lambda item: int(item.get("rank", 0)))
    if len(rows) != QUEUE_COUNT or [r.get("rank") for r in rows] != list(range(1, QUEUE_COUNT + 1)):
        raise RuntimeError("popup24 queue ranks are not exactly 1..24")
    originals = [r.get("original") for r in rows]
    if len(set(originals)) != QUEUE_COUNT:
        raise RuntimeError("popup24 queue contains duplicate originals")
    list_lines = ORIGINALS_PATH.read_text(encoding="utf-8").splitlines()
    if len(list_lines) != QUEUE_COUNT:
        raise RuntimeError("popup24 original URL list is not exactly 24 lines")
    if any(not isinstance(url, str) or urlsplit(url).scheme not in {"http", "https"}
           or not urlsplit(url).netloc or not urlsplit(url).path
           or urlsplit(url).query or urlsplit(url).fragment for url in originals):
        raise RuntimeError("popup24 queue contains invalid exact original URL")
    if list_lines != originals:
        raise RuntimeError("popup24 URL-list does not exactly match queue originals")
    ref_counts = []
    for row in rows:
        original = row.get("original")
        base = row.get("source_base_url")
        literal = row.get("literal_popup_argument")
        line_number = row.get("resolved_url_list_line")
        refs = row.get("references")
        if not isinstance(base, str) or urlsplit(base).scheme not in {"http", "https"}:
            raise RuntimeError(f"rank {row.get('rank')} has invalid source_base_url")
        if (not isinstance(literal, str) or not literal or urlsplit(literal).scheme
                or literal.startswith("//")):
            raise RuntimeError(f"rank {row.get('rank')} does not contain a relative popup literal")
        if urljoin(base, literal) != original:
            raise RuntimeError(f"rank {row.get('rank')} does not resolve to original")
        if isinstance(line_number, bool) or not isinstance(line_number, int) or not 1 <= line_number <= QUEUE_COUNT:
            raise RuntimeError(f"rank {row.get('rank')} has invalid URL-list line")
        if list_lines[line_number - 1] != original:
            raise RuntimeError(f"rank {row.get('rank')} URL-list line is not exact")
        if not isinstance(refs, list) or not refs:
            raise RuntimeError(f"rank {row.get('rank')} has no source reference")
        verified = [validate_source_reference(row, ref, original, literal) for ref in refs]
        if len(verified) != len(refs):
            raise RuntimeError(f"rank {row.get('rank')} reference count mismatch")
        row["_verified_references"] = verified
        ref_counts.append(len(verified))
    return rows, list_lines, sha256(ORIGINALS_PATH), ref_counts


def query_url(original: str) -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(original, safe="")
        + "&from=" + FROM_TS + "&to=" + TO_TS
        + "&output=json&fl=" + quote(",".join(FIELDS), safe="")
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
        "user_agent": "wow-recovery-reusable-image-v3/20261018-popup24-v30",
        "prior_failure_tail": prior_tail,
        "transport_policy": "batch_after_direct_failure",
    }


def make_primary_evidence(row: dict, originals_sha: str) -> dict:
    original = row["original"]
    return {
        "kind": "derived_resolved_url_list",
        "path": rel(ORIGINALS_PATH),
        "line": row["resolved_url_list_line"],
        "literal": original,
        "requested": original,
        "sha256": originals_sha,
        "bytes": ORIGINALS_PATH.stat().st_size,
        "source": "popup24-original-urls.txt",
        "source_base_url": row["source_base_url"],
        "relative_popup_argument": row["literal_popup_argument"],
        "resolved_url": original,
        "resolution_method": "urllib.parse.urljoin",
        "resolution_verified": True,
        "queue_row_rank": row["rank"],
        "source_marker": "popup24_derived_url_list",
    }


def make_candidate(row: dict, batch_index: int, local_no: int, queue_sha: str,
                   queue: dict, originals_sha: str, status_snapshot_path: Path,
                   status_snapshot_sha: str, receipt_path: Path, receipt_sha: str,
                   prior_tail: int) -> dict:
    original = row["original"]
    mime_types, pillow_formats, all_gif_frames = expected_for(original)
    primary = make_primary_evidence(row, originals_sha)
    refs = copy.deepcopy(row["_verified_references"])
    source_context = {
        "context_kind": "popup24_actual_relative_popUpOmega_argument",
        "queue_path": rel(QUEUE_PATH),
        "queue_sha256": queue_sha,
        "queue_accepted": queue.get("accepted"),
        "queue_checked_utc": queue.get("checked_utc"),
        "queue_rank": row["rank"],
        "source_base_url": row["source_base_url"],
        "literal_popup_argument": row["literal_popup_argument"],
        "resolved_original": original,
        "urljoin_resolution_verified": True,
        "resolved_url_list_path": rel(ORIGINALS_PATH),
        "resolved_url_list_sha256": originals_sha,
        "resolved_url_list_line": row["resolved_url_list_line"],
        "resolved_url_list_literal": original,
        "references": refs,
        "all_references": refs,
        "source_evidence": primary,
        "no_path_guessing": True,
        "no_thumbnail_alias": True,
        "popup_helper": [ref.get("popup_helper") for ref in row.get("references", [])],
        "previous_batch_tail_receipt": rel(receipt_path),
        "previous_batch_tail_receipt_sha256": receipt_sha,
        "previous_batch_tail_end": prior_tail,
        "status_snapshot_path": rel(status_snapshot_path),
        "status_snapshot_sha256": status_snapshot_sha,
    }
    return {
        "target_key": f"POPUP24-V30-{batch_index:02d}-{local_no:02d}",
        "priority": local_no,
        "queue_rank": row["rank"],
        "kind": "image",
        "original": original,
        "literal": original,
        "source_base_url": row["source_base_url"],
        "popup_literal_argument": row["literal_popup_argument"],
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
        "all_references": refs,
        "source_page_context": source_context,
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
            "state": "derived_relative_popup_argument; no archive request during preparation",
            "source": "popup24-selected-queue",
            "exact_entity_index_complete": False,
            "positive_row_count": 0,
        }],
        "prior_evidence_status": "popup24_derived_relative_argument; fresh_exact_cdx_required; no_bound_positive_fallback",
    }


def parse_batch_index() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-index", type=int, required=True)
    args = parser.parse_args()
    if args.batch_index < 1:
        parser.error("--batch-index must be >= 1")
    return args.batch_index


def main() -> None:
    batch_index = parse_batch_index()
    required = [QUEUE_PATH, ORIGINALS_PATH, STATUS_PATH, TEMPLATE_PLAN_PATH, V3_DRIVER_PATH]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("missing bound input(s): " + ", ".join(missing))
    queue_sha = sha256(QUEUE_PATH)
    originals_sha = sha256(ORIGINALS_PATH)
    if queue_sha != EXPECTED_QUEUE_SHA:
        raise RuntimeError(f"popup24 queue SHA changed: {queue_sha}")
    if originals_sha != EXPECTED_ORIGINALS_SHA:
        raise RuntimeError(f"popup24 URL-list SHA changed: {originals_sha}")
    queue = read_json(QUEUE_PATH)
    rows, list_lines, originals_sha, ref_counts = validate_queue(queue)
    status, status_sha, receipt_path, receipt, receipt_sha, prior_tail = load_latest_source()
    control_gate_path, control_gate, control_gate_sha = load_latest_control_gate(status)
    driver_sha = sha256(V3_DRIVER_PATH)
    queue_ref = binding(QUEUE_PATH, "root-accepted immutable popup24 derived-URL queue")
    originals_ref = binding(ORIGINALS_PATH, "root-accepted derived exact original URL list")
    latest_ref = binding(receipt_path, "latest accepted image-source receipt selected from recovery status")
    control_ref = binding(control_gate_path, "latest accepted tail-zero connectivity control gate")
    template_ref = binding(TEMPLATE_PLAN_PATH, "accepted V3-compatible plan structure")
    driver_ref = binding(V3_DRIVER_PATH, "frozen reusable-image-v3 driver")
    prepared_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    batch_count = math.ceil(len(rows) / BATCH_SIZE)
    start = (batch_index - 1) * BATCH_SIZE
    if start >= len(rows):
        raise RuntimeError(f"batch index {batch_index} is outside popup24 queue")
    chunk = rows[start:start + BATCH_SIZE]
    batch_dir = FACTORY_ROOT / f"batch-{batch_index:02d}"
    output_dir = batch_dir / "output"
    if output_dir.is_dir() and any(output_dir.iterdir()):
        raise RuntimeError(f"executed batch output is immutable: {output_dir}")

    status_snapshot_path = batch_dir / "status-snapshot.json"
    status_snapshot = {
        "schema": "wow-recovery.popup24-v30-status-snapshot.v1",
        "captured_utc": prepared_utc,
        "active_status_path": rel(STATUS_PATH),
        "active_status_sha256_audit": status_sha,
        "active_status_latest_source_acceptance_pointer": status.get("latest_source_acceptance"),
        "active_status_latest_control_gate_pointer": status.get("latest_control_gate"),
        "latest_source_acceptance": latest_ref,
        "latest_control_gate": control_ref,
        "latest_failure_tail": prior_tail,
        "latest_source_batch_id": receipt.get("batch_id"),
        "latest_control_batch_id": control_gate.get("batch_id"),
        "network_requests_during_preparation": 0,
    }
    write_json(status_snapshot_path, status_snapshot)
    status_snapshot_sha = sha256(status_snapshot_path)
    status_snapshot_ref = binding(status_snapshot_path, "immutable batch-local snapshot of active status pointers")

    batch_id = f"WAYBACK-CONTINUOUS-20261018-POPUP24-V30-{batch_index:02d}"
    candidates = [
        make_candidate(row, batch_index, local_no, queue_sha, queue, originals_sha,
                       status_snapshot_path, status_snapshot_sha, receipt_path,
                       receipt_sha, prior_tail)
        for local_no, row in enumerate(chunk, 1)
    ]
    bindings = {
        "popup24_selected_queue": queue_ref,
        "popup24_original_url_list": originals_ref,
        "status_snapshot": status_snapshot_ref,
        "latest_actual_source_acceptance": latest_ref,
        "latest_control_gate": control_ref,
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
        "control_gate_required": prior_tail == 0,
        "control_gate_rebind_required_before_execute": False,
        "root_control_acceptance_bound": True,
        "root_control_acceptance_required_before_execute": False,
        "parent_go_required": True,
    }
    source_contract = {
        "kind": "popup24_actual_relative_popUpOmega_arguments",
        "primary_source_evidence": {
            "path": rel(ORIGINALS_PATH),
            "sha256": originals_sha,
            "line_field": "resolved_url_list_line",
            "literal_field": "original",
            "meaning": "derived resolved URL list; not archive availability evidence",
        },
        "resolution": "urllib.parse.urljoin(source_base_url, literal_popup_argument)",
        "page_reference_contract": "each reference keeps its own source_page_sha256, source_page, line and literal",
        "must_validate": ["urljoin(base,literal)==original", "source-page SHA and line", "URL-list line exact original"],
        "prohibitions": ["no path guessing", "no thumbnail alias substitution", "no scheme/host normalization", "no archive replay during preparation"],
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
        },
        "selection_scope": {
            "name": f"popup24_v30_batch_{batch_index:02d}",
            "reason": "Ten derived exact originals from the accepted popup24 queue; each relative popUpOmega argument is independently resolved against its cited source page.",
            "queue_path": rel(QUEUE_PATH),
            "queue_sha256": queue_sha,
            "queue_generated_utc": queue.get("checked_utc"),
            "queue_target_count": len(rows),
            "queue_rank_range": [chunk[0]["rank"], chunk[-1]["rank"]],
            "selected_queue_ranks": [row["rank"] for row in chunk],
            "original_url_list_path": rel(ORIGINALS_PATH),
            "original_url_list_sha256": originals_sha,
            "original_url_list_line_range": [chunk[0]["resolved_url_list_line"], chunk[-1]["resolved_url_list_line"]],
            "network_requests_during_preparation": 0,
            "derived_url_resolution_verified": True,
            "split_reason": "Ten-target batches keep each window within the 24-request/240-second cap.",
        },
        "popup24_source_contract": source_contract,
        "source_contract": source_contract,
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
            "popup24_special_gate_required": True,
            "preparation_network_requests": 0,
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
        "driver_sha256": driver_sha,
        "fixture_mode": "accepted frozen V3 offline contract; popup24 source gate is separate",
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
        },
        "predecessor_tail_rebind_required_before_execute": False,
        "predecessor_tail_status": "bound_to_latest_actual_source_acceptance",
        "selected_queue_ranks": [row["rank"] for row in chunk],
        "selected_originals": [row["original"] for row in chunk],
        "source_bindings": bindings,
        "source_contract": source_contract,
        "driver_bytes": V3_DRIVER_PATH.stat().st_size,
        "network_requests_during_preparation": 0,
    }
    bindings_path = batch_dir / "input-bindings.json"
    write_json(bindings_path, bindings_doc)
    cache_status = {
        "schema": "wow-recovery.popup24-v30-cache-status.v1",
        "generated_utc": prepared_utc,
        "network_requests": 0,
        "raw_exact_cdx_cache_present": False,
        "raw_exact_cdx_cache_bound": False,
        "reason": "popup24 has only offline derived URL and source-page evidence; each target requires a fresh exact CDX 200 response before id_ replay.",
        "fresh_exact_cdx_required": True,
        "known_positive_fallback_available": False,
        "fallback_policy": "none; no bound positive rows in popup24 queue",
        "latestness": "unknown_until_fresh_exact_cdx_http_200_complete_sub_limit_no_resume",
        "queue_source_contract": source_contract,
        "targets": [
            {
                "target_key": candidate["target_key"],
                "queue_rank": candidate["queue_rank"],
                "original": candidate["original"],
                "source_base_url": candidate["source_base_url"],
                "popup_literal_argument": candidate["popup_literal_argument"],
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
        ],
        "source_bindings": bindings,
    }
    cache_path = batch_dir / "cache-status.json"
    write_json(cache_path, cache_status)
    selection_manifest = {
        "schema": "wow-recovery.popup24-v30-selection.v1",
        "generated_utc": prepared_utc,
        "queue": queue_ref,
        "original_url_list": originals_ref,
        "selected": [
            {
                "target_key": candidate["target_key"],
                "queue_rank": candidate["queue_rank"],
                "original": candidate["original"],
                "source_base_url": candidate["source_base_url"],
                "popup_literal_argument": candidate["popup_literal_argument"],
                "source_evidence": candidate["source_evidence"],
                "all_references": candidate["all_references"],
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
        "schema": "wow-recovery.popup24-v30-plan-manifest.v1",
        "generated_utc": prepared_utc,
        "queue": queue_ref,
        "original_url_list": originals_ref,
        "status_snapshot": status_snapshot_ref,
        "active_status_sha256_audit": status_sha,
        "latest_actual_source_acceptance": latest_ref,
        "latest_control_gate": control_ref,
        "frozen_v3_driver": driver_ref,
        "template_plan": template_ref,
        "batch_index": batch_index,
        "batch_count": batch_count,
        "reference_count_per_selected_row": ref_counts[:len(chunk)],
        "plan": {"path": rel(plan_path), "sha256": sha256(plan_path)},
        "bindings": {"path": rel(bindings_path), "sha256": sha256(bindings_path)},
        "network_requests_during_preparation": 0,
        "execution_boundary": {
            "no_network_authorized_by_this_artifact": True,
            "requires_parent_GO": True,
            "popup24_special_gate_required": True,
            "max_attempts": 24,
            "max_seconds": 240.0,
            "batch_size": BATCH_SIZE,
            "unexecuted_batch_may_be_rebound": True,
            "executed_batch_output_is_immutable": True,
        },
    }
    manifest_path = FACTORY_ROOT / "plan-manifest.json"
    write_json(manifest_path, manifest)
    print(json.dumps({
        "batch_index": batch_index,
        "batch_id": batch_id,
        "factory": rel(Path(__file__)),
        "factory_sha256": sha256(Path(__file__)),
        "queue_sha256": queue_sha,
        "original_url_list_sha256": originals_sha,
        "latest_source_acceptance": latest_ref,
        "latest_control_gate": control_ref,
        "latest_source_tail": prior_tail,
        "selected_ranks": [row["rank"] for row in chunk],
        "plan": rel(plan_path),
        "plan_sha256": sha256(plan_path),
        "bindings": rel(bindings_path),
        "bindings_sha256": sha256(bindings_path),
        "cache_status": rel(cache_path),
        "selection_manifest": rel(selection_path),
        "manifest": rel(manifest_path),
        "driver_sha256": driver_sha,
        "network_requests": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

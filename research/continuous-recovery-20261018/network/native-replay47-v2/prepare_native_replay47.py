"""Offline-only preparation for the bounded native Karazhan replay probe.

This factory deliberately does not know how to query CDX and never invokes a
network client.  The queue already contains the exact replay URLs observed in
the historical audit.  Preparation freezes the queue, source/control receipts,
the active-status audit hash, and the first twelve transport-unknown rows.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
RECOVERY = ROOT / "research" / "continuous-recovery-20261018"
NETWORK = RECOVERY / "network"
FACTORY_ROOT = NETWORK / "native-replay47-v2"
QUEUE_PATH = RECOVERY / "publication" / "native-karazhan-unknown47-queue.json"
STATUS_PATH = RECOVERY / "status.json"
V3_DRIVER_PATH = NETWORK / "reusable-image-driver-v3" / "reusable_image_driver.py"

EXPECTED_QUEUE_SHA = "29b21d74f3253259a09be5d489291db12cf52782ce89b5a19c417817a8ea63cc"
EXPECTED_V3_SHA = "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955"
EXPECTED_SOURCE_SHA = "55f5879bca140ab0a9aeacadbd191f4f5745757210ce3abb142fc9f9121cb4d6"
EXPECTED_CONTROL_SHA = "caa309e2e0d4592755107814135e2288c2055a879c9b4ea012e12f0505ec185b"

DISK_FLOOR = 11_005_853_696
BATCH_SIZE = 12
QUEUE_COUNT = 47
ANCHOR_TIMESTAMP = "20080512210044"
PROXY = "http://127.0.0.1:7890"


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
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def binding(path: Path, role: str) -> dict:
    return {"path": rel(path), "sha256": sha256(path), "bytes": path.stat().st_size, "role": role}


def resolve_status_pointer(status: dict, field: str) -> Path:
    value = status.get(field)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"status has no {field}")
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    if value.replace("\\", "/").startswith("research/"):
        return ROOT / candidate
    return RECOVERY / candidate


def load_latest_receipts() -> tuple[dict, str, Path, dict, str, Path, dict, str, int]:
    status = read_json(STATUS_PATH)
    status_sha = sha256(STATUS_PATH)
    source_field = "latest_source_acceptance" if status.get("latest_source_acceptance") else "last_image_source_acceptance"
    source_path = resolve_status_pointer(status, source_field)
    control_path = resolve_status_pointer(status, "latest_control_gate")
    source = read_json(source_path)
    control = read_json(control_path)
    source_sha = sha256(source_path)
    control_sha = sha256(control_path)
    if source_sha != EXPECTED_SOURCE_SHA:
        raise RuntimeError(f"latest source is not the accepted popup batch-03 receipt: {source_path}")
    if control_sha != EXPECTED_CONTROL_SHA:
        raise RuntimeError(f"latest control is not CONTROL03: {control_path}")
    if source.get("accepted") is not True or source.get("failure_streak_end") != 0:
        raise RuntimeError("latest source receipt is not accepted with tail zero")
    if (control.get("accepted") is not True or control.get("resume_gate_passed") is not True
            or control.get("control_final_streak") != 0):
        raise RuntimeError("latest control receipt is not a tail-zero resume gate")
    for label, value in (("source", source.get("cooldown_not_before_utc")),
                         ("status", status.get("network_cooldown_not_before_utc") or status.get("cooldown_not_before_utc"))):
        if isinstance(value, str) and value.strip():
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            if parsed.astimezone(timezone.utc) > datetime.now(timezone.utc):
                raise RuntimeError(f"{label} cooldown has not elapsed")
    tail = int(source["failure_streak_end"])
    return status, status_sha, source_path, source, source_sha, control_path, control, control_sha, tail


def validate_source_page(row: dict) -> dict:
    source_page = row.get("source_page")
    if not isinstance(source_page, dict):
        raise RuntimeError(f"{row.get('target_id')} has no source_page")
    source_path_value = source_page.get("path")
    if not isinstance(source_path_value, str) or Path(source_path_value).is_absolute():
        raise RuntimeError(f"invalid source page path for {row.get('target_id')}")
    source_path = ROOT / source_path_value
    if not source_path.is_file():
        raise RuntimeError(f"missing source page: {source_path}")
    actual_sha = sha256(source_path)
    if actual_sha != source_page.get("sha256"):
        raise RuntimeError(f"source page SHA mismatch: {source_path}")
    line_number = source_page.get("line")
    lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if isinstance(line_number, bool) or not isinstance(line_number, int) or not 1 <= line_number <= len(lines):
        raise RuntimeError(f"invalid source page line for {row.get('target_id')}")
    if source_page.get("quote") and source_page["quote"] not in lines[line_number - 1]:
        raise RuntimeError(f"source page quote mismatch: {source_path}:{line_number}")
    return {
        "path": source_path_value.replace("\\", "/"),
        "line": line_number,
        "sha256": actual_sha,
        "bytes": source_path.stat().st_size,
        "literal": lines[line_number - 1],
        "quote": source_page.get("quote"),
    }


def validate_queue(queue: dict) -> list[dict]:
    if queue.get("accepted") is not True or queue.get("request_count") != 0:
        raise RuntimeError("native queue is not an accepted zero-request queue")
    rows = queue.get("rows")
    if not isinstance(rows, list) or len(rows) != QUEUE_COUNT:
        raise RuntimeError("native queue must contain exactly 47 rows")
    seen: set[str] = set()
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise RuntimeError(f"queue row {index} is not an object")
        target_id = row.get("target_id")
        original = row.get("original_url")
        request = row.get("request_url")
        if not isinstance(target_id, str) or not target_id or target_id in seen:
            raise RuntimeError(f"invalid or duplicate target_id at row {index}")
        seen.add(target_id)
        if row.get("global_category") != "transport_unknown":
            raise RuntimeError(f"row {target_id} is outside transport_unknown scope")
        if row.get("global_category") == "archive_404" or row.get("latest_observed_category") == "archive_404":
            raise RuntimeError(f"archive404 row leaked into native scope: {target_id}")
        if not isinstance(original, str) or urlsplit(original).scheme not in {"http", "https"}:
            raise RuntimeError(f"invalid original URL: {target_id}")
        if not isinstance(request, str) or not request.startswith("https://web.archive.org/web/"):
            raise RuntimeError(f"invalid recorded replay URL: {target_id}")
        if ANCHOR_TIMESTAMP not in request or "id_/" not in request:
            raise RuntimeError(f"replay URL is not the recorded anchor id_ URL: {target_id}")
        if not request.endswith(original):
            raise RuntimeError(f"replay URL does not bind exact original: {target_id}")
        validate_source_page(row)
    return rows


def expected_for(original: str) -> tuple[list[str], list[str]]:
    suffix = Path(urlsplit(original).path).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return ["image/jpeg"], ["JPEG"]
    if suffix == ".png":
        return ["image/png"], ["PNG"]
    if suffix == ".gif":
        return ["image/gif"], ["GIF"]
    return ["image/jpeg", "image/png", "image/gif"], ["JPEG", "PNG", "GIF"]


def make_candidate(row: dict, local_no: int, queue_sha: str, source_page_ref: dict,
                   status_snapshot_ref: dict, source_ref: dict, control_ref: dict,
                   source_tail: int) -> dict:
    original = row["original_url"]
    mime_types, formats = expected_for(original)
    source_history = copy.deepcopy(row.get("source_history") or [])
    return {
        "target_key": f"NATIVE-KARAZHAN47-01-{local_no:02d}",
        "priority": local_no,
        "queue_rank": local_no,
        "target_id": row["target_id"],
        "kind": row.get("kind"),
        "number": row.get("number"),
        "original": original,
        "literal": row["request_url"],
        "request_url": row["request_url"],
        "expected_mime": mime_types,
        "expected_formats": formats,
        "expected": {
            "archive_query_required": False,
            "mime_types": mime_types,
            "pillow_formats": formats,
            "reencode": False,
            "script_execution": False,
        },
        "source_evidence": {
            "kind": "frozen_native_replay_queue",
            "path": rel(QUEUE_PATH),
            "sha256": queue_sha,
            "row_index": local_no,
            "target_id": row["target_id"],
            "literal": row["request_url"],
            "requested": row["request_url"],
            "original_url": original,
            "global_category": row["global_category"],
            "no_cdx_query": True,
            "no_url_guessing": True,
        },
        "source_page_context": {
            "source_page": source_page_ref,
            "js_rule_evidence": copy.deepcopy(row.get("js_rule_evidence")),
            "source_request_exists_in_old_126": row.get("source_request_exists_in_old_126"),
            "source_history_summary": [
                {k: item.get(k) for k in ("batch", "observed_category", "source_status", "request_time_utc", "request_time_kind")}
                for item in source_history if isinstance(item, dict)
            ],
            "queue_latest_observed_category": row.get("latest_observed_category"),
            "queue_effective_status": row.get("effective_source_status"),
            "status_snapshot": status_snapshot_ref,
            "latest_source_acceptance": source_ref,
            "latest_control_gate": control_ref,
            "inherited_failure_tail": source_tail,
        },
        "replay": {
            "enabled": True,
            "request_url": row["request_url"],
            "original_url": original,
            "anchor_timestamp": ANCHOR_TIMESTAMP,
            "no_cdx_query": True,
            "no_url_guessing": True,
            "no_redirects": True,
            "tls_verification": True,
            "accept_200_image_as": "pending_source_index",
            "do_not_follow_location": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-index", type=int, default=1)
    args = parser.parse_args()
    if args.batch_index != 1:
        raise SystemExit("native-replay47-v2 currently prepares batch-index 1 only")
    if not QUEUE_PATH.is_file() or not STATUS_PATH.is_file() or not V3_DRIVER_PATH.is_file():
        raise SystemExit("missing immutable preparation input")
    queue_sha = sha256(QUEUE_PATH)
    driver_sha = sha256(V3_DRIVER_PATH)
    if queue_sha != EXPECTED_QUEUE_SHA:
        raise SystemExit(f"queue SHA mismatch: {queue_sha}")
    if driver_sha != EXPECTED_V3_SHA:
        raise SystemExit(f"frozen V3 SHA mismatch: {driver_sha}")
    queue = read_json(QUEUE_PATH)
    rows = validate_queue(queue)
    status, status_sha, source_path, source, source_sha, control_path, control, control_sha, source_tail = load_latest_receipts()

    batch_dir = FACTORY_ROOT / "batch-01"
    output_dir = batch_dir / "output"
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"refuse to prepare over non-empty execution output: {output_dir}")
    batch_dir.mkdir(parents=True, exist_ok=True)

    status_snapshot_path = batch_dir / "status-snapshot.json"
    status_snapshot = {
        "schema": "wow-recovery.native-replay47-status-snapshot.v2",
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "active_status_path": rel(STATUS_PATH),
        "active_status_sha256_audit": status_sha,
        "latest_source_acceptance": rel(source_path),
        "latest_source_acceptance_sha256": source_sha,
        "latest_source_failure_streak_end": source_tail,
        "latest_control_gate": rel(control_path),
        "latest_control_gate_sha256": control_sha,
        "control_resume_gate_passed": control.get("resume_gate_passed"),
        "network_requests_during_preparation": 0,
        "note": "Immutable batch snapshot; active status is audit-only at execution time.",
    }
    write_json(status_snapshot_path, status_snapshot)
    status_snapshot_ref = binding(status_snapshot_path, "immutable batch-local status pointer snapshot")
    source_ref = binding(source_path, "latest accepted popup24 batch-03 source receipt")
    control_ref = binding(control_path, "latest accepted CONTROL03 tail-zero gate")

    candidates = []
    for local_no, row in enumerate(rows[:BATCH_SIZE], 1):
        source_page = row["source_page"]
        source_page_path = ROOT / source_page["path"]
        page_ref = validate_source_page(row)
        candidates.append(make_candidate(row, local_no, queue_sha, page_ref, status_snapshot_ref,
                                         source_ref, control_ref, source_tail))

    batch_id = "WAYBACK-CONTINUOUS-20261018-NATIVE-REPLAY47-V2-01"
    plan_path = batch_dir / "plan.json"
    bindings_path = batch_dir / "input-bindings.json"
    plan = {
        "schema": "wow-recovery.native-replay47-probe-plan.v2",
        "batch_id": batch_id,
        "batch_index": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "queue": {"path": rel(QUEUE_PATH), "sha256": queue_sha, "rows": QUEUE_COUNT, "accepted": True},
        "selection": {
            "selected_ranks": list(range(1, BATCH_SIZE + 1)),
            "selected_count": BATCH_SIZE,
            "queue_count": QUEUE_COUNT,
            "scope": "first 12 frozen Karazhan transport_unknown rows",
            "excluded_scope": "all 79 actual archive404 targets and every non-transport_unknown row",
        },
        "policy": {
            "max_attempts": 14,
            "window_seconds": 240.0,
            "max_total_body_bytes": 16 * 1024 * 1024,
            "max_entity_body_bytes": 8 * 1024 * 1024,
            "min_dispatch_seconds": 5.25,
            "min_request_start_seconds": 5.0,
            "disk_floor_bytes": DISK_FLOOR,
            "direct_first": True,
            "direct_connect_timeout_seconds": 4.0,
            "direct_max_seconds": 4.0,
            "proxy": PROXY,
            "proxy_connect_timeout_seconds": 8.0,
            "proxy_max_seconds": 20.0,
            "tls_verification": True,
            "automatic_redirects": 0,
            "stop_http_codes": [429, 503],
            "cooldown_seconds": 120,
            "retry_after_honored": True,
            "transport_policy": "batch_after_direct_failure",
            "qualifying_direct_fallback": {"curl_exit": [7, 28], "source_status": None, "body_bytes": 0},
            "user_agent": "wow-recovery-native-replay47-v2/20261018",
            "inherited_failure_tail": source_tail,
        },
        "replay_contract": {
            "no_cdx_query": True,
            "no_url_guessing": True,
            "recorded_request_urls_only": True,
            "anchor_timestamp": ANCHOR_TIMESTAMP,
            "no_redirects": True,
            "classifications": ["actual404", "observed_302_location", "http_200_nonimage", "pending_source_index", "transport_unknown"],
            "pending_source_index_requires": "separate CDX/Memento/digest review",
            "200_image_is_not_accepted": True,
            "raw_evidence_local_only": True,
        },
        "source_bindings": {
            "status_snapshot": status_snapshot_ref,
            "latest_source_acceptance": source_ref,
            "latest_control_gate": control_ref,
            "active_status_sha256_audit": status_sha,
        },
        "frozen_v3": {"path": rel(V3_DRIVER_PATH), "sha256": driver_sha},
        "native_driver": {"path": rel(FACTORY_ROOT / "native_replay47_driver.py"),
                           "sha256": sha256(FACTORY_ROOT / "native_replay47_driver.py")},
        "fixture": {"path": rel(FACTORY_ROOT / "fixtures" / "native-replay47-fixtures.json"),
                    "sha256": sha256(FACTORY_ROOT / "fixtures" / "native-replay47-fixtures.json")},
        "input_bindings_path": rel(bindings_path),
        "root_plan_acceptance": {
            "path": rel(RECOVERY / "publication" / "root-native-replay47-v2-batch1-plan-acceptance.json"),
            "sha256": None,
            "accepted": False,
            "required_before_go": True,
        },
        "candidates": candidates,
        "candidate_count": len(candidates),
        "previous_batch": {
            "latest_source_tail_receipt": source_ref,
            "latest_source_tail_end": source_tail,
            "latest_control_gate": control_ref,
            "no_prior_native_replay_batch": True,
        },
        "execution_boundary": {
            "network_requests_during_preparation": 0,
            "requires_explicit_go": True,
            "requires_root_plan_acceptance_sha": True,
            "requires_future_deadline_utc": True,
            "requires_empty_output": True,
            "does_not_write_active_status": True,
            "does_not_modify_frozen_v3": True,
        },
    }
    write_json(plan_path, plan)

    bindings_doc = {
        "schema": "wow-recovery.native-replay47-input-bindings.v2",
        "batch_id": batch_id,
        "plan_path": rel(plan_path),
        "plan_sha256": sha256(plan_path),
        "native_driver_path": rel(FACTORY_ROOT / "native_replay47_driver.py"),
        "native_driver_sha256": sha256(FACTORY_ROOT / "native_replay47_driver.py") if (FACTORY_ROOT / "native_replay47_driver.py").is_file() else None,
        "frozen_v3_driver": {"path": rel(V3_DRIVER_PATH), "sha256": driver_sha, "role": "hash-pinned low-level transport/parser/image helpers"},
        "queue": binding(QUEUE_PATH, "accepted native replay queue"),
        "status_snapshot": status_snapshot_ref,
        "latest_source_acceptance": source_ref,
        "latest_control_gate": control_ref,
        "selected_ranks": list(range(1, BATCH_SIZE + 1)),
        "selected_target_ids": [row["target_id"] for row in rows[:BATCH_SIZE]],
        "fixture_path": rel(FACTORY_ROOT / "fixtures" / "native-replay47-fixtures.json"),
        "fixture_sha256": sha256(FACTORY_ROOT / "fixtures" / "native-replay47-fixtures.json"),
        "network_requests_during_preparation": 0,
        "execution_requires": ["explicit --go", "root acceptance SHA", "future deadline", "empty output", "disk floor"],
    }
    write_json(bindings_path, bindings_doc)

    cache_status = {
        "schema": "wow-recovery.native-replay47-cache-status.v2",
        "network_requests": 0,
        "cdx_query": False,
        "exact_cdx_cache": False,
        "replay_source": "frozen recorded request_url values",
        "complete_index_claim": False,
        "200_image_status": "pending_source_index",
        "raw_headers_bodies_traces": "future execution local-only",
        "selected_count": BATCH_SIZE,
        "queue_count": QUEUE_COUNT,
        "source_bindings": {"queue_sha256": queue_sha, "source_sha256": source_sha, "control_sha256": control_sha},
    }
    cache_path = batch_dir / "cache-status.json"
    write_json(cache_path, cache_status)

    selection = {
        "schema": "wow-recovery.native-replay47-selection.v2",
        "queue": binding(QUEUE_PATH, "frozen queue"),
        "selected": [{"rank": i, "target_id": row["target_id"], "request_url": row["request_url"], "original_url": row["original_url"]}
                     for i, row in enumerate(rows[:BATCH_SIZE], 1)],
        "excluded_archive404": "all 79 queue-external archive404 rows by frozen queue scope",
        "network_requests": 0,
    }
    selection_path = batch_dir / "selection-manifest.json"
    write_json(selection_path, selection)

    manifest = {
        "schema": "wow-recovery.native-replay47-plan-manifest.v2",
        "generated_utc": plan["generated_utc"],
        "queue": binding(QUEUE_PATH, "frozen queue"),
        "status_snapshot": status_snapshot_ref,
        "latest_source_acceptance": source_ref,
        "latest_control_gate": control_ref,
        "frozen_v3_driver": {"path": rel(V3_DRIVER_PATH), "sha256": driver_sha},
        "plan": {"path": rel(plan_path), "sha256": sha256(plan_path)},
        "bindings": {"path": rel(bindings_path), "sha256": sha256(bindings_path)},
        "cache_status": {"path": rel(cache_path), "sha256": sha256(cache_path)},
        "selection": {"path": rel(selection_path), "sha256": sha256(selection_path)},
        "fixture": {"path": rel(FACTORY_ROOT / "fixtures" / "native-replay47-fixtures.json"),
                    "sha256": sha256(FACTORY_ROOT / "fixtures" / "native-replay47-fixtures.json")},
        "fixture_results": ({"path": rel(FACTORY_ROOT / "fixtures" / "native-replay47-fixture-results.json"),
                             "sha256": sha256(FACTORY_ROOT / "fixtures" / "native-replay47-fixture-results.json")}
                            if (FACTORY_ROOT / "fixtures" / "native-replay47-fixture-results.json").is_file() else None),
        "network_requests_during_preparation": 0,
        "execution_boundary": "offline preparation only; parent GO plus root plan acceptance required",
    }
    manifest_path = FACTORY_ROOT / "plan-manifest.json"
    write_json(manifest_path, manifest)

    # Bind the native driver after it exists, but keep the plan itself stable.
    print(json.dumps({
        "batch_id": batch_id,
        "queue_sha256": queue_sha,
        "frozen_v3_sha256": driver_sha,
        "source_acceptance": source_ref,
        "control_gate": control_ref,
        "source_tail": source_tail,
        "selected": [row["target_id"] for row in rows[:BATCH_SIZE]],
        "plan": {"path": rel(plan_path), "sha256": sha256(plan_path)},
        "bindings": {"path": rel(bindings_path), "sha256": sha256(bindings_path)},
        "cache_status": {"path": rel(cache_path), "sha256": sha256(cache_path)},
        "manifest": {"path": rel(manifest_path), "sha256": sha256(manifest_path)},
        "network_requests_during_preparation": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

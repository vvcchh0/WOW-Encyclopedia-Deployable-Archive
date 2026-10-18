"""Prepare two offline 10-target plans for the v26 2008 news-body queue.

This is a small plan adapter.  It reuses the frozen reusable-image-v3 plan
contract and does not contain an acquisition path.  It only reads the local
queue, validates the cited source lines, and writes two independently bound
10-target plans.  The plans remain fresh exact-CDX then id_ replay plans and
must be reviewed before any execute invocation.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
RECOVERY = ROOT / "research" / "continuous-recovery-20261018"
NETWORK = RECOVERY / "network"
PLAN_ROOT = NETWORK / "news-body-2008-v26"

QUEUE_PATH = RECOVERY / "publication" / "news20-accepted-queue.json"
QUEUE_ACCEPTANCE_PATH = RECOVERY / "publication" / "root-news20-queue-acceptance.json"
LATEST_SOURCE_ACCEPTANCE_PATH = RECOVERY / "publication" / "root-news8-next-source-acceptance.json"
LATEST_PLAN_ACCEPTANCE_PATH = RECOVERY / "publication" / "root-news8-next-plan-acceptance.json"
CONTROL_GATE_PATH = ROOT / "research" / "continuous-recovery-20261016" / "publication" / "root-control03-acceptance.json"
TEMPLATE_PLAN_PATH = NETWORK / "news-static-v25-next10-v1" / "plan.json"
V3_DRIVER_PATH = NETWORK / "reusable-image-driver-v3" / "reusable_image_driver.py"

FROM_TS = "20000101000000"
TO_TS = "20080512210044"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
DISK_FLOOR = 11_005_853_696


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def split_source_ref(value: str) -> tuple[str, int]:
    path, separator, line = value.rpartition(":")
    if not separator or not line.isdigit():
        raise RuntimeError(f"source marker is missing a line number: {value}")
    return path, int(line)


def source_evidence(row: dict, original: str) -> dict:
    refs = row.get("v25_marker_refs") or []
    if not refs:
        raise RuntimeError(f"queue row has no source marker: {original}")
    ref = refs[0]
    relative_path, line = split_source_ref(ref["source"])
    path = ROOT / relative_path
    if not path.is_file():
        raise RuntimeError(f"citation file is missing: {path}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    encoded = quote(original, safe="")
    if line < 1 or line > len(lines) or (original not in lines[line - 1] and encoded not in lines[line - 1]):
        raise RuntimeError(f"citation line does not bind requested URL: {path}:{line}")
    return {
        "path": relative_path,
        "line": line,
        "literal": original,
        "sha256": sha256(path),
        "requested": original,
        "reason": ref.get("reason"),
        "source_marker": "v26_news_priority_queue_marker",
    }


def query_url(original: str) -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?url="
        + quote(original, safe="")
        + "&from="
        + FROM_TS
        + "&to="
        + TO_TS
        + "&output=json&fl="
        + quote(",".join(FIELDS), safe="")
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
    prior = row.get("prior_attempts") or {}
    return {
        "state": prior.get("state"),
        "network_requests_in_this_audit": prior.get("network_requests_in_this_audit", 0),
        "accepted_payload_in_prior_records": prior.get("accepted_payload_in_prior_records", False),
        "prior_news_pending_row": prior.get("prior_news_pending_row", False),
    }


def make_candidate(row: dict, batch_no: int, local_no: int, queue_sha: str,
                   queue: dict, latest_tail: dict, latest_tail_sha: str) -> dict:
    original = row["original"]
    mime_types, pillow_formats, all_gif_frames = expected_for(original)
    target_key = f"NEWS-BODY-V26-{batch_no:02d}-{local_no:02d}"
    refs = copy.deepcopy(row.get("v25_marker_refs") or [])
    source = source_evidence(row, original)
    return {
        "target_key": target_key,
        "priority": local_no,
        "queue_rank": row["rank"],
        "source_priority_band": row.get("priority_band"),
        "date_bucket": row.get("date_bucket"),
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
        "source_evidence": source,
        "source_page_context": {
            "candidate_file": rel(QUEUE_PATH),
            "candidate_file_sha256": queue_sha,
            "queue_schema": queue.get("schema"),
            "queue_generated_utc": queue.get("generated_utc"),
            "static_queue_rank": row.get("rank"),
            "priority_band": row.get("priority_band"),
            "date_bucket": row.get("date_bucket"),
            "occurrences_v25_news": row.get("occurrences_v25_news"),
            "v25_marker_refs": refs,
            "prior_attempt_summary": prior_attempt_summary(row),
            "cdx_state": row.get("cdx_state"),
            "selection_reason": row.get("selection_reason"),
            "previous_batch_tail_receipt": rel(LATEST_SOURCE_ACCEPTANCE_PATH),
            "previous_batch_tail_receipt_sha256": latest_tail_sha,
            "previous_batch_tail_end": latest_tail.get("failure_streak_end"),
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
            "state": row.get("cdx_state"),
            "source": "news-priority-queue-v26",
            "prior_attempt": prior_attempt_summary(row),
            "exact_entity_index_complete": False,
            "positive_row_count": 0,
        }],
        "prior_evidence_status": "v26_news_body_marker; fresh_exact_cdx_required; no_bound_positive_fallback",
    }


def evidence_binding(path: Path, role: str) -> dict:
    return {"path": rel(path), "sha256": sha256(path), "role": role}


def make_policy() -> dict:
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
        "user_agent": "wow-recovery-reusable-image-v3/20261018-news-body-v26",
        "prior_failure_tail": 0,
        "transport_policy": "batch_after_direct_failure",
    }


def main() -> None:
    required = [QUEUE_PATH, QUEUE_ACCEPTANCE_PATH, LATEST_SOURCE_ACCEPTANCE_PATH,
                LATEST_PLAN_ACCEPTANCE_PATH, CONTROL_GATE_PATH, TEMPLATE_PLAN_PATH,
                V3_DRIVER_PATH]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("missing bound input(s): " + ", ".join(missing))

    queue = read_json(QUEUE_PATH)
    rows = sorted(queue.get("rows") or [], key=lambda item: int(item["rank"]))
    if queue.get("selection", {}).get("target_count") != 20 or len(rows) != 20:
        raise RuntimeError(f"expected exactly 20 queue rows, got {len(rows)}")
    if queue.get("network_requests") != 0:
        raise RuntimeError("queue was not produced offline")
    queue_acceptance = read_json(QUEUE_ACCEPTANCE_PATH)
    queue_sha = sha256(QUEUE_PATH)
    if queue_acceptance.get("accepted") is not True or queue_acceptance.get("queue_sha256") != queue_sha:
        raise RuntimeError("root queue acceptance is missing or does not bind the frozen queue")
    if [row.get("type") for row in rows] != ["static_news_body"] * 20:
        raise RuntimeError("v26 queue contains a non-news-body row")
    originals = [row.get("original") for row in rows]
    if any(not isinstance(url, str) or not url.startswith("http://www.worldofwarcraft.com/news/images/") for url in originals):
        raise RuntimeError("queue contains an unexpected source host/path")
    if len(set(originals)) != 20:
        raise RuntimeError("queue contains duplicate originals")

    latest_tail = read_json(LATEST_SOURCE_ACCEPTANCE_PATH)
    if latest_tail.get("accepted") is not True or latest_tail.get("failure_streak_end") != 0:
        raise RuntimeError("latest NET03 source acceptance is not accepted/tail-zero")
    latest_tail_sha = sha256(LATEST_SOURCE_ACCEPTANCE_PATH)
    latest_plan_acceptance = read_json(LATEST_PLAN_ACCEPTANCE_PATH)
    if latest_plan_acceptance.get("accepted") is not True:
        raise RuntimeError("latest NET03 plan acceptance is not accepted")

    queue_acceptance_sha = sha256(QUEUE_ACCEPTANCE_PATH)
    latest_plan_acceptance_sha = sha256(LATEST_PLAN_ACCEPTANCE_PATH)
    control_sha = sha256(CONTROL_GATE_PATH)
    template_sha = sha256(TEMPLATE_PLAN_PATH)
    driver_sha = sha256(V3_DRIVER_PATH)
    prepared_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    tail_ref = evidence_binding(LATEST_SOURCE_ACCEPTANCE_PATH, "latest accepted NET03 source tail-zero receipt")
    tail_plan_ref = evidence_binding(LATEST_PLAN_ACCEPTANCE_PATH, "latest accepted NET03 plan receipt")
    control_ref = evidence_binding(CONTROL_GATE_PATH, "frozen control03 tail-zero gate")
    queue_ref = evidence_binding(QUEUE_PATH, "offline 20-target v26 news-body queue")
    queue_acceptance_ref = evidence_binding(QUEUE_ACCEPTANCE_PATH, "root acceptance of the frozen 20-target queue")
    template_ref = evidence_binding(TEMPLATE_PLAN_PATH, "prior accepted V3-compatible plan structure")
    driver_ref = evidence_binding(V3_DRIVER_PATH, "frozen reusable-image-v3 driver")

    plans = []
    for batch_no, chunk in ((1, rows[:10]), (2, rows[10:20])):
        batch_dir = PLAN_ROOT / f"batch-{batch_no:02d}"
        output_dir = batch_dir / "output"
        batch_id = f"WAYBACK-CONTINUOUS-20261018-NEWS-BODY-2008-V26-{batch_no:02d}"
        candidates = [
            make_candidate(row, batch_no, local_no, queue_sha, queue, latest_tail, latest_tail_sha)
            for local_no, row in enumerate(chunk, 1)
        ]
        bindings = {
            "news_queue_v26": queue_ref,
            "news_queue_v26_acceptance": queue_acceptance_ref,
            "latest_news8_source_acceptance": tail_ref,
            "latest_news8_plan_acceptance": tail_plan_ref,
            "control_gate": control_ref,
            "template_plan": template_ref,
            "frozen_v3_driver": driver_ref,
        }
        previous_batch = {
            "name": "WAYBACK-CONTINUOUS-20261018-NEWS-STATIC-V25-NEXT10-V2",
            "prior_failure_tail": 0,
            "acceptance_receipt_path": rel(LATEST_SOURCE_ACCEPTANCE_PATH),
            "acceptance_receipt_sha256": latest_tail_sha,
            "latest_successful_tail_end": latest_tail["failure_streak_end"],
            "historical_tail_is_preserved": True,
            "ordinary_retrieval_requires_new_control_gate": True,
            "control_gate_receipt_path": rel(CONTROL_GATE_PATH),
            "control_gate_receipt_sha256": control_sha,
            "control_gate_required": True,
        }
        plan = {
            "schema": "wow-recovery.reusable-image-plan.v1",
            "batch_id": batch_id,
            "prepared_utc": prepared_utc,
            "mode": "fresh_exact_cdx_then_id_replay_no_fallback",
            "network_authorized": None,
            "candidate_count": len(candidates),
            "output_dir": rel(output_dir),
            "execution_order": {
                "batch_number": batch_no,
                "batch_count": 2,
                "predecessor_batch_required": batch_no == 2,
                "predecessor_tail_rebind_required_before_execute": batch_no == 2,
                "predecessor_tail_status": "unknown_until_batch_01_actual_receipt" if batch_no == 2 else "not_applicable",
            },
            "selection_scope": {
                "name": f"news_priority_v26_2008_body_batch_{batch_no:02d}",
                "reason": "Ten consecutive exact originals from the offline v26 2008 news-body queue; queue citations and prior no-CDX state are preserved.",
                "queue_path": rel(QUEUE_PATH),
                "queue_sha256": queue_sha,
                "queue_acceptance_path": rel(QUEUE_ACCEPTANCE_PATH),
                "queue_acceptance_sha256": queue_acceptance_sha,
                "queue_generated_utc": queue.get("generated_utc"),
                "queue_target_count": 20,
                "queue_rank_range": [chunk[0]["rank"], chunk[-1]["rank"]],
                "selected_queue_ranks": [row["rank"] for row in chunk],
                "selected_priorities": [row["priority_band"] for row in chunk],
                "no_complete_same_window_row_selected": True,
                "network_requests_during_preparation": 0,
                "split_reason": "10+10 bounds each prepared batch to ten originals; the 24-request/240-second driver cap may preserve unprocessed replay candidates explicitly.",
            },
            "candidates": candidates,
            "policy": make_policy(),
            "previous_batch": previous_batch,
            "input_bindings": bindings,
            "source_bindings": {
                "news_queue_v26": queue_ref,
                "news_queue_v26_acceptance": queue_acceptance_ref,
                "latest_news8_source_acceptance": tail_ref,
                "latest_news8_plan_acceptance": tail_plan_ref,
                "control_gate": control_ref,
                "template_plan": template_ref,
                "v3_reference": driver_ref,
            },
            "excluded_rows": {
                "root_news9_accepted_count": queue.get("selection", {}).get("excluded_root_news9_accepted_count"),
                "root_news9_complete_empty_count": queue.get("selection", {}).get("excluded_root_news9_complete_empty_count"),
                "existing_overlay_url_count": queue.get("selection", {}).get("excluded_existing_overlay_url_count"),
                "complete_empty_urls": queue.get("selection", {}).get("complete_empty_urls", []),
                "other_queue_batch_ranks": [row["rank"] for row in rows if row not in chunk],
            },
            "identity_variant_policy": {
                "retain_in_cdx_report": True,
                "replay_identity_variants": False,
                "strict_identity": "exact_original_default_port_only",
                "scheme_or_host_variants_are_not_equivalent": True,
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
            "fixture_mode": "not duplicated; use the already accepted V3 offline contract",
            "inherited_tail": {
                "latest_net03_tail": latest_tail["failure_streak_end"],
                "prior_failure_tail": plan["policy"]["prior_failure_tail"],
                "tail_receipt": rel(LATEST_SOURCE_ACCEPTANCE_PATH),
                "tail_receipt_sha256": latest_tail_sha,
                "control_gate_receipt": rel(CONTROL_GATE_PATH),
                "control_gate_sha256": control_sha,
            },
            "predecessor_tail_rebind_required_before_execute": batch_no == 2,
            "predecessor_tail_status": "unknown_until_batch_01_actual_receipt" if batch_no == 2 else "not_applicable",
            "selected_queue_ranks": [row["rank"] for row in chunk],
            "selected_originals": [row["original"] for row in chunk],
            "source_bindings": bindings,
            "driver_bytes": V3_DRIVER_PATH.stat().st_size,
            "network_requests_during_preparation": 0,
        }
        bindings_path = batch_dir / "input-bindings.json"
        write_json(bindings_path, bindings_doc)
        cache_status = {
            "schema": "wow-recovery.news-body-v26-cache-status.v1",
            "generated_utc": prepared_utc,
            "network_requests": 0,
            "raw_exact_cdx_cache_present": False,
            "raw_exact_cdx_cache_bound": False,
            "reason": "The v26 queue contains only local marker citations. Every target requires a fresh exact CDX 200 response before id_ replay.",
            "fresh_exact_cdx_required": True,
            "known_positive_fallback_available": False,
            "fallback_policy": "none; no bound positive rows in this queue",
            "identity_variant_policy": plan["identity_variant_policy"],
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
            "queue_split": {"full_queue_count": 20, "batch_number": batch_no, "batch_count": 2},
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
            "schema": "wow-recovery.news-body-v26-selection.v1",
            "generated_utc": prepared_utc,
            "queue": queue_ref,
            "selected": [
                {
                    "target_key": candidate["target_key"],
                    "queue_rank": candidate["queue_rank"],
                    "priority_band": candidate["source_priority_band"],
                    "date_bucket": candidate["date_bucket"],
                    "original": candidate["original"],
                    "citation_refs": candidate["source_page_context"]["v25_marker_refs"],
                }
                for candidate in candidates
            ],
            "selection_scope": plan["selection_scope"],
            "excluded_from_this_batch": [row["rank"] for row in rows if row not in chunk],
        }
        selection_path = batch_dir / "selection-manifest.json"
        write_json(selection_path, selection_manifest)
        plans.append({
            "batch": batch_no,
            "plan": rel(plan_path),
            "plan_sha256": sha256(plan_path),
            "bindings": rel(bindings_path),
            "bindings_sha256": sha256(bindings_path),
            "cache_status": rel(cache_path),
            "cache_status_sha256": sha256(cache_path),
            "selection_manifest": rel(selection_path),
            "selection_manifest_sha256": sha256(selection_path),
            "candidate_count": len(candidates),
            "selected_queue_ranks": [row["rank"] for row in chunk],
            "network_requests": 0,
        })

    split_manifest = {
        "schema": "wow-recovery.news-body-v26-queue-split.v1",
        "generated_utc": prepared_utc,
        "queue": queue_ref,
        "queue_acceptance": queue_acceptance_ref,
        "queue_target_count": 20,
        "split": "10+10",
        "network_requests_during_preparation": 0,
        "latest_tail": tail_ref,
        "latest_plan_acceptance": tail_plan_ref,
        "control_gate": control_ref,
        "frozen_v3_driver": driver_ref,
        "plans": plans,
        "execution_boundary": {
            "no_network_authorized_by_this_artifact": True,
            "requires_parent_GO_per_batch": True,
            "no_fixture_repeated": True,
            "max_attempts_per_batch": 24,
            "max_seconds_per_batch": 240.0,
            "remainder_after_budget_is_preserved": True,
            "batch_02_requires_batch_01_actual_tail_rebind": True,
        },
    }
    split_path = PLAN_ROOT / "queue-split-manifest.json"
    write_json(split_path, split_manifest)
    print(json.dumps({"queue": queue_ref, "queue_sha256": queue_sha,
                      "split_manifest": rel(split_path), "split_manifest_sha256": sha256(split_path),
                      "plans": plans, "driver_sha256": driver_sha,
                      "network_requests": 0}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

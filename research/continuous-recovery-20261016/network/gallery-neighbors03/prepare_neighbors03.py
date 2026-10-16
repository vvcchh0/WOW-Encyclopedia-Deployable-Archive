from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(r"D:\WOW_Encyclopedia")
BASE = ROOT / "research" / "continuous-recovery-20261016"
NETWORK = BASE / "network"
BATCH = NETWORK / "gallery-neighbors03"
SOURCE = BASE / "local-audit" / "gallery-neighbors" / "remaining9-candidates.json"
ACCEPTANCE = BASE / "publication" / "root-gallery-neighbors-remaining-candidates-acceptance.json"
PRIOR_SOURCE = BASE / "publication" / "root-gallery-neighbors02-source-acceptance.json"
PRIOR_PLAN = NETWORK / "gallery-neighbors02" / "plan.json"
PRIOR_REPORT = NETWORK / "gallery-neighbors02" / "output" / "batch-report.json"
PRIOR_SOURCE_MAP = NETWORK / "gallery-neighbors02" / "output" / "source-map.json"
CONTROL03 = BASE / "publication" / "root-control03-acceptance.json"
PREFIX04 = BASE / "publication" / "root-gallery-prefix04-acceptance.json"
DRIVER = NETWORK / "reusable-image-driver-v2" / "reusable_image_driver.py"
DRIVER_ACCEPTANCE = BASE / "publication" / "root-reusable-v2-code-acceptance.json"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
FROM_TS = "20000101000000"
TO_TS = "20080512210044"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def binding(path: Path, role: str) -> dict[str, object]:
    return {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size, "role": role}


def cdx_url(original: str) -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?"
        f"url={quote(original, safe='')}&from={FROM_TS}&to={TO_TS}"
        f"&output=json&fl={quote(','.join(FIELDS), safe='')}&limit=500"
        "&showResumeKey=true&matchType=exact"
    )


def source_line(lines: list[str], literal: str) -> int:
    for number, line in enumerate(lines, 1):
        if literal in line or quote(literal, safe="") in line:
            return number
    raise RuntimeError(f"source literal missing: {literal}")


def make_candidate(item: dict[str, object], index: int, lines: list[str], source_sha: str, acceptance_sha: str) -> dict[str, object]:
    original = str(item["original"])
    source_evidence = item["source_evidence"]
    assert isinstance(source_evidence, dict)
    expected_mime = ["image/jpeg"]
    return {
        "target_key": f"GALLERY-NEIGHBOR03-{index:02d}",
        "priority": index,
        "kind": "image",
        "original": original,
        "literal": original,
        "filename_class": item.get("filename_class"),
        "expected_mime": expected_mime,
        "expected": {"mime_types": expected_mime, "pillow_formats": ["JPEG"],
                      "all_gif_frames": False, "reencode": False, "script_execution": False},
        "source_evidence": {
            "literal": original,
            "path": rel(SOURCE),
            "line": source_line(lines, original),
            "sha256": source_sha,
            "candidate_index": index,
            "source_acceptance_path": rel(ACCEPTANCE),
            "source_acceptance_sha256": acceptance_sha,
            "source_row_index": source_evidence.get("row_index"),
            "source_result_label": source_evidence.get("result_label"),
            "source_row": source_evidence.get("row"),
            "origin_evidence_path": source_evidence.get("path"),
            "origin_evidence_sha256": source_evidence.get("sha256"),
        },
        "source_page_context": {
            "gallery_context": item.get("gallery_context"),
            "state": item.get("state"),
            "relationship": item.get("relationship"),
            "source_acceptance_row_index": source_evidence.get("row_index"),
            "positive_rows": item.get("positive_rows", []),
        },
        "selection": {
            "require_complete_index": True,
            "potential_truncation": "do_not_replay",
            "require_exact_original": True,
            "require_expected_mime": True,
            "require_nonempty_cdx_sha1_digest": True,
            "require_statuscode": 200,
            "max_distinct_digest_candidates": 2,
            "sort": "timestamp_desc_then_record_index_desc",
            "same_digest_older_captures": "skip",
            "unknown_metadata": "incomplete_error",
        },
        "replay": {
            "enabled": True,
            "id_url_template": "https://web.archive.org/web/{timestamp}id_/" + original,
            "max_candidates": 2,
            "no_redirects": True,
            "verify_tls": True,
            "acceptance": ["http_status_200", "memento_datetime_present_and_exact",
                           "link_original_exact_default_port_only", "expected_image_content_type",
                           "magic_and_pillow_decode", "all_gif_frames_loaded",
                           "decoded_payload_sha1_matches_cdx_digest"],
            "accepted_payloads_are_source_data_only": True,
        },
        "prior_local_evidence": [{"status": "positive_index_not_local",
                                   "source_candidates_sha256": source_sha,
                                   "source_acceptance_sha256": acceptance_sha,
                                   "source_origin_evidence_sha256": source_evidence.get("sha256")}],
        "prior_evidence_status": "positive_index_not_local",
        "cdx_mode": "fresh",
        "known_positive_cache_rows": [],
        "query": {"endpoint": "https://web.archive.org/cdx/search/cdx", "url": original,
                  "from": FROM_TS, "to": TO_TS, "output": "json", "fields": FIELDS,
                  "limit": 500, "showResumeKey": True, "collapse": False, "matchType": "exact",
                  "query_url": cdx_url(original)},
        "fallback_label": None,
    }


def main() -> None:
    BATCH.mkdir(parents=True, exist_ok=True)
    source_data = json.loads(SOURCE.read_text(encoding="utf-8"))
    acceptance_data = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    source_sha = sha(SOURCE)
    acceptance_sha = sha(ACCEPTANCE)
    if source_data.get("candidate_count") != 9 or len(source_data.get("candidates", [])) != 9:
        raise RuntimeError("remaining9 input is not the accepted nine thumbnail candidates")
    if acceptance_data.get("accepted") is not True or acceptance_data.get("remaining9_sha256") != source_sha:
        raise RuntimeError("remaining9 acceptance does not bind this input")
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    old = json.loads((NETWORK / "gallery-neighbors02" / "plan.json").read_text(encoding="utf-8"))
    plan = copy.deepcopy(old)
    plan["batch_id"] = "GALLERY-NEIGHBORS03"
    plan["generated_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    plan["candidate_count"] = 9
    plan["candidates"] = [make_candidate(item, i, lines, source_sha, acceptance_sha)
                           for i, item in enumerate(source_data["candidates"], 1)]
    plan["scope"] = "Nine root-approved remaining Lunar Festival thumbnail-or-other originals. Exact fresh CDX then exact Memento replay only; preserve original default-port identity and do not infer dynamic gallery aliases."
    plan["candidate_order_note"] = "Candidates retain the exact order of the root-approved remaining9 file; no full-image or unknown-transport target is included."
    plan["source_plan_path"] = rel(SOURCE)
    plan["source_plan_sha256"] = source_sha
    plan["source_acceptance_path"] = rel(ACCEPTANCE)
    plan["source_acceptance_sha256"] = acceptance_sha
    plan["output_dir"] = "research/continuous-recovery-20261016/network/gallery-neighbors03/output"
    plan["mode"] = "prepared_not_executed_pending_root_go"
    plan["network_authorized"] = False
    plan["no_network_before_parent_go"] = True
    plan["excluded_due_to_prior_acceptance"] = {
        "count": 13,
        "relationship": "Neighbors02 exact payloads are excluded; the separate unknown-transport full-image retry remains outside this thumbnail-only batch.",
    }
    plan["pending_root_acceptance"] = {
        "required_before_dispatch": True,
        "note": "Offline preparation only; dispatch requires root acceptance of this exact nine-thumbnail plan and explicit GO.",
        "required_receipts": ["root-gallery-neighbors03-plan-acceptance.json"],
    }
    plan["policy"].update({
        "max_attempts": 60,
        "max_total_body_bytes": 32 * 1024 * 1024,
        "max_entity_body_bytes": 8 * 1024 * 1024,
        "window_seconds": 900.0,
        "prior_failure_tail": 0,
        "transport_policy": "batch_after_direct_failure",
    })
    plan["previous_batch"] = {
        "status": "neighbors02_source_accepted_tail0",
        "prior_failure_tail": 0,
        "latest_tail_receipt_path": rel(PRIOR_SOURCE),
        "latest_tail_receipt_sha256": sha(PRIOR_SOURCE),
        "latest_tail_value": 0,
        "control_gate_receipt_path": rel(CONTROL03),
        "control_gate_receipt_sha256": sha(CONTROL03),
        "prior_batch_plan_path": rel(PRIOR_PLAN),
        "prior_batch_plan_sha256": sha(PRIOR_PLAN),
        "prior_batch_report_path": rel(PRIOR_REPORT),
        "prior_batch_report_sha256": sha(PRIOR_REPORT),
        "prior_batch_source_map_path": rel(PRIOR_SOURCE_MAP),
        "prior_batch_source_map_sha256": sha(PRIOR_SOURCE_MAP),
        "note": "Neighbors02 produced a root-accepted source result with end tail zero and no subsequent stop; CONTROL03 remains the prior successful control gate required by frozen V2 validation.",
    }
    plan["input_bindings"] = {
        "remaining9_candidates": binding(SOURCE, "root-approved nine exact thumbnail originals"),
        "remaining_candidates_acceptance": binding(ACCEPTANCE, "root acceptance conserving remaining20 and remaining9"),
        "prior_neighbors02_source_acceptance": binding(PRIOR_SOURCE, "latest root-accepted neighbors02 source result and tail-zero receipt"),
        "prior_neighbors02_plan": binding(PRIOR_PLAN, "previous exact-neighbor plan"),
        "prior_neighbors02_report": binding(PRIOR_REPORT, "previous completed source report"),
        "prior_neighbors02_source_map": binding(PRIOR_SOURCE_MAP, "previous source map"),
        "control03_acceptance": binding(CONTROL03, "accepted control gate for prior tail zero"),
        "prior_prefix04_acceptance": binding(PREFIX04, "positive index evidence source for remaining thumbnails"),
        "reusable_v2_driver": binding(DRIVER, "frozen reusable image V2 driver"),
        "reusable_v2_code_acceptance": binding(DRIVER_ACCEPTANCE, "root acceptance of frozen V2 core"),
    }
    write_json(BATCH / "plan.json", plan)
    plan_sha = sha(BATCH / "plan.json")
    write_json(BATCH / "input-bindings.json", {
        "schema": "wow-recovery.gallery-neighbors03-input-bindings.v1",
        "batch_id": plan["batch_id"],
        "mode": "prepared_not_executed_pending_root_go",
        "network_requests": 0,
        "plan_sha256": plan_sha,
        "driver_sha256": sha(DRIVER),
        "source_bindings": plan["input_bindings"],
        "network_authorized": False,
        "required_before_dispatch": ["root accepts this exact neighbors03 plan", "parent gives explicit GO"],
        "latest_tail_binding": {"path": rel(PRIOR_SOURCE), "sha256": sha(PRIOR_SOURCE), "tail": 0,
                                "role": "latest accepted neighbors02 source result and prior tail-zero evidence"},
        "fixture_results": {"path": rel(BATCH / "fixture-results.json"), "pending": True},
    })
    print(json.dumps({"plan_sha256": plan_sha, "driver_sha256": sha(DRIVER),
                      "source_sha256": source_sha, "acceptance_sha256": acceptance_sha,
                      "candidate_count": len(plan["candidates"]), "max_attempts": plan["policy"]["max_attempts"],
                      "window_seconds": plan["policy"]["window_seconds"],
                      "max_total_body_bytes": plan["policy"]["max_total_body_bytes"],
                      "network_authorized": False}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

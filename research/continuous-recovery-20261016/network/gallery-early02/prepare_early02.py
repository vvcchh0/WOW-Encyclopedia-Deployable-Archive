from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(r"D:\WOW_Encyclopedia")
BASE = ROOT / "research" / "continuous-recovery-20261016"
NETWORK = BASE / "network"
BATCH = NETWORK / "gallery-early02"
SOURCE = BASE / "local-audit" / "gallery-followup-plans" / "early-gaps-24-v1.json"
FOLLOWUP_ACCEPTANCE = BASE / "publication" / "root-gallery-followups-acceptance.json"
REGISTRY = BASE / "local-audit" / "gallery-prefix-registry-v5" / "gallery-prefix-registry-v5.json"
LATEST_ACCEPTANCE = BASE / "publication" / "root-gallery-early01-acceptance.json"
LATEST_PLAN = NETWORK / "gallery-early01" / "execution-plan.json"
LATEST_REPORT = NETWORK / "gallery-early01" / "batch-report.json"
LATEST_SOURCE_MAP = NETWORK / "gallery-early01" / "source-map.json"
HISTORICAL_PREFIX03 = BASE / "publication" / "root-gallery-prefix03-acceptance.json"
PREFIX05_ACCEPTANCE = BASE / "publication" / "root-gallery-prefix05-acceptance.json"
PREFIX05_PLAN = NETWORK / "gallery-prefix05" / "plan.json"
PREFIX05_DRIVER = NETWORK / "gallery-prefix05" / "gallery_prefix_driver_v5.py"
PREFIX05_FIXTURE = NETWORK / "gallery-prefix05" / "fixture-results.json"
DRIVER = BATCH / "gallery_prefix_driver_v6.py"
FROM_TS = "20000101000000"
ANCHOR_TO_TS = "20080512210044"
LIMIT = 500


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def binding(path: Path, role: str) -> dict[str, object]:
    return {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size, "role": role}


def cdx_url(prefix: str, to_ts: str) -> str:
    fields = "urlkey,timestamp,original,mimetype,statuscode,digest,length"
    return (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(prefix, safe="")
        + "&matchType=prefix&output=json&fl=" + quote(fields, safe="")
        + f"&from={FROM_TS}&to={to_ts}&limit={LIMIT}&showResumeKey=true"
    )


def load_driver():
    spec = importlib.util.spec_from_file_location("gallery_early02_v6_prepare", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load V6 driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_candidate(item: dict[str, object], rank: int) -> dict[str, object]:
    candidate = copy.deepcopy(item)
    window = copy.deepcopy(item["query_window"])
    candidate.update({
        "rank": rank,
        "target_key": f"GALLERY-EARLY02-{rank:02d}",
        "query_window": window,
        "cdx_query_url": cdx_url(str(item["prefix"]), str(window["to"])),
        "query_mode": "absolute HTTP prefix index only",
        "payload_recovery": False,
        "no_filename_guess": True,
        "status": "prepared_not_executed",
    })
    return candidate


def main() -> None:
    BATCH.mkdir(parents=True, exist_ok=True)
    source_data = json.loads(SOURCE.read_text(encoding="utf-8"))
    followup_acceptance = json.loads(FOLLOWUP_ACCEPTANCE.read_text(encoding="utf-8"))
    latest_acceptance = json.loads(LATEST_ACCEPTANCE.read_text(encoding="utf-8"))
    source_sha = sha(SOURCE)
    if source_sha != "767c9dfe7280ac6d708b5be5661b0970e67ef8ac292672c9802aeddc75218e90":
        raise RuntimeError("early-gap source SHA changed")
    if source_data.get("schema") != "gallery-followup-plan-v1" or source_data.get("count") != 24:
        raise RuntimeError("early-gap source is not the accepted 24-item plan")
    if followup_acceptance.get("accepted") is not True or followup_acceptance.get("early_gap_plan_sha256") != source_sha or followup_acceptance.get("early_batches") != [20, 4]:
        raise RuntimeError("root followup acceptance does not bind the 20+4 early-gap split")
    selected_items = [x for x in source_data["items"] if x.get("followup_batch") == "early_gap_batch_2_of_2_4_items"]
    if len(selected_items) != 4:
        raise RuntimeError("early-gap batch two is not exactly four items")
    candidates = [make_candidate(item, rank) for rank, item in enumerate(selected_items, 1)]

    latest_plan_sha = sha(LATEST_PLAN)
    latest_report_sha = sha(LATEST_REPORT)
    latest_source_map_sha = sha(LATEST_SOURCE_MAP)
    if latest_acceptance.get("accepted") is not True or latest_acceptance.get("batch_report_sha256") != latest_report_sha or latest_acceptance.get("failure_streak_end") != 0:
        raise RuntimeError("latest EARLY01 acceptance does not bind tail zero")
    if json.loads(LATEST_REPORT.read_text(encoding="utf-8")).get("failure_streak") != 0:
        raise RuntimeError("latest EARLY01 report tail is not two")

    template = {
        "schema": "wow-recovery.gallery-early02-plan.v1",
        "batch_id": "WAYBACK-GALLERYEARLY02-20261016",
        "prepared_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "offline_prepared_until_root_GO",
        "execution_status": "prepared_not_executed",
        "network_authorized": False,
        "network_requests": 0,
        "scope": "Four root-approved early-gap absolute HTTP prefix CDX index queries; each candidate keeps its source-bound to value; no later complete-window repeat, pagination, payload replay, or filename expansion.",
        "source_plan_path": rel(SOURCE),
        "source_plan_sha256": source_sha,
        "source_plan_selection": {"followup_batch": "early_gap_batch_2_of_2_4_items", "count": 4, "remaining_batch_count": 4},
        "candidate_count": 4,
        "prior_failure_tail": 0,
        "latest_tail_value": 0,
        "historical_gallery_tail": 5,
        "historical_gallery_tail_preserved": 5,
        "latest_tail_basis": {"path": rel(LATEST_ACCEPTANCE), "sha256": sha(LATEST_ACCEPTANCE), "failure_streak_end": 0, "role": "latest EARLY01 accepted source receipt; inherited current tail"},
        "control_basis": "EARLY01 tail zero is inherited directly; historical CONTROL03 is not used to reset this batch to zero.",
        "previous_batch": {
            "status": "neighbors-other4_source_accepted_tail0",
            "prior_failure_tail": 0,
            "latest_tail_receipt_path": rel(LATEST_ACCEPTANCE),
            "latest_tail_receipt_sha256": sha(LATEST_ACCEPTANCE),
            "latest_tail_value": 0,
            "latest_batch_plan_path": rel(LATEST_PLAN),
            "latest_batch_plan_sha256": latest_plan_sha,
            "latest_batch_report_path": rel(LATEST_REPORT),
            "latest_batch_report_sha256": latest_report_sha,
            "latest_batch_source_map_path": rel(LATEST_SOURCE_MAP),
            "latest_batch_source_map_sha256": latest_source_map_sha,
            "historical_prefix03_acceptance_path": rel(HISTORICAL_PREFIX03),
            "historical_prefix03_acceptance_sha256": sha(HISTORICAL_PREFIX03),
            "note": "Inherit the EARLY01 end tail zero. The historical prefix03 tail five remains metadata only; no zero reset or CONTROL03 gate is used.",
        },
        "policy": {
            "from": FROM_TS,
            "to": "per_item_source_window",
            "limit": LIMIT,
            "showResumeKey": True,
            "collapse": False,
            "matchType": "prefix",
            "max_attempts": 40,
            "window_seconds": 900.0,
            "max_total_body_bytes": 16 * 1024 * 1024,
            "max_entity_body_bytes": 8 * 1024 * 1024,
            "min_dispatch_seconds": 5.25,
            "min_request_start_seconds": 5.0,
            "disk_floor_bytes": 11_005_853_696,
            "direct_first": True,
            "proxy": "http://127.0.0.1:7890",
            "tls_verification": True,
            "automatic_redirects": 0,
            "stop_http_codes": [429, 503],
            "stop_on_five_consecutive_transport_failures": True,
            "stop_after_new_transport_failures": 5,
            "cooldown_seconds": 120,
            "payload_replay": False,
            "index_only": True,
            "prefix_only": True,
            "no_pagination": True,
            "remaining_time_and_byte_clamp": True,
            "retry_after_rule": "429/503 stop; not-before is at least 120 seconds and any Retry-After",
            "prior_failure_tail": 0,
        },
        "input_bindings": {},
        "candidates": candidates,
        "pending_root_acceptance": {"required_before_dispatch": True, "required_receipt": "root-gallery-early02-plan-acceptance.json", "network_requests": 0},
    }
    bindings = {
        "early_gap_plan": binding(SOURCE, "root-approved 24-item early-gap source; batch-2 selects 20"),
        "root_gallery_followups_acceptance": binding(FOLLOWUP_ACCEPTANCE, "root acceptance of early-gap source and 20+4 split"),
        "gallery_registry_v5": binding(REGISTRY, "registry referenced by the accepted early-gap source"),
        "root_gallery_early01_acceptance": binding(LATEST_ACCEPTANCE, "latest accepted source result with inherited tail zero"),
        "gallery_early01_batch_report": binding(LATEST_REPORT, "latest EARLY01 report bound to the tail receipt"),
        "gallery_early01_source_map": binding(LATEST_SOURCE_MAP, "latest EARLY01 source map bound to the tail receipt"),
        "root_gallery_prefix05_acceptance": binding(PREFIX05_ACCEPTANCE, "accepted V5 prefix core predecessor"),
        "gallery_prefix05_plan": binding(PREFIX05_PLAN, "frozen V5 predecessor plan"),
        "gallery_prefix05_driver_v5": binding(PREFIX05_DRIVER, "frozen V5 driver used as the adaptation base"),
        "gallery_prefix05_fixture": binding(PREFIX05_FIXTURE, "frozen V5 offline fixture baseline"),
        "historical_prefix03_acceptance": binding(HISTORICAL_PREFIX03, "historical gallery tail five preserved for metadata only"),
    }
    seen_source_paths: set[str] = set()
    for rank, candidate in enumerate(candidates, 1):
        source_path = ROOT / str(candidate["source_evidence"]["path"])
        key = f"source_page_{rank:02d}"
        if rel(source_path) not in seen_source_paths:
            bindings[key] = binding(source_path, f"source page literal for early-gap candidate {rank:02d}")
            seen_source_paths.add(rel(source_path))
        else:
            bindings[key] = {"path": rel(source_path), "sha256": sha(source_path), "bytes": source_path.stat().st_size, "role": f"shared source page literal for early-gap candidate {rank:02d}"}
    template["input_bindings"] = bindings
    write_json(BATCH / "plan.json", template)
    plan_sha = sha(BATCH / "plan.json")
    write_json(BATCH / "input-bindings.json", {
        "schema": "wow-recovery.gallery-early02-input-bindings.v1",
        "batch_id": template["batch_id"],
        "plan_path": rel(BATCH / "plan.json"),
        "plan_sha256": plan_sha,
        "driver_path": rel(DRIVER),
        "driver_sha256": sha(DRIVER),
        "source_bindings": bindings,
        "network_authorized": False,
        "network_requests": 0,
        "latest_tail_binding": {"path": rel(LATEST_ACCEPTANCE), "sha256": sha(LATEST_ACCEPTANCE), "tail": 0},
        "fixture_results": {"path": rel(BATCH / "fixture-results.json"), "pending": True},
    })
    module = load_driver()
    prepared, normalized, _ = module.validate_inputs()
    if len(normalized) != 4 or prepared.get("prior_failure_tail") != 0 or any(x["query_window"]["to"] == ANCHOR_TO_TS for x in normalized):
        raise RuntimeError("offline V6 validation did not preserve 20 per-item early windows")
    print(json.dumps({"plan_sha256": plan_sha, "driver_sha256": sha(DRIVER), "source_sha256": source_sha, "candidate_count": len(normalized), "query_end_counts": {to: sum(x["query_window"]["to"] == to for x in normalized) for to in sorted({x["query_window"]["to"] for x in normalized})}, "prior_failure_tail": 0, "network_requests": 0, "validation": "passed"}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

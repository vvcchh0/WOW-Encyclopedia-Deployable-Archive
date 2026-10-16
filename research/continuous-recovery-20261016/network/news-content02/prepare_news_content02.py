from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\WOW_Encyclopedia")
BASE = ROOT / "research" / "continuous-recovery-20261016"
NETWORK = BASE / "network"
OUT = NETWORK / "news-content02"
PLAN_PATH = OUT / "plan.json"
BINDINGS_PATH = OUT / "input-bindings.json"
SOURCE = BASE / "local-audit" / "v23-news-frontier" / "v23-news-frontier-candidates20.json"
SOURCE_ACCEPTANCE = BASE / "publication" / "root-v23-news-frontier-candidates-acceptance.json"
V23_PROVENANCE = ROOT / ".scratch" / "pages-resources-20261016-v23" / "export-provenance.json"
DRIVER = NETWORK / "reusable-image-driver-v2" / "reusable_image_driver.py"
DRIVER_FIXTURE = NETWORK / "reusable-image-driver-v2" / "fixture-results-v2.json"
EARLY03_ACCEPTANCE = BASE / "publication" / "root-gallery-early03-acceptance.json"
EARLY03_REPORT = NETWORK / "gallery-early03" / "batch-report.json"
EARLY03_SOURCE_MAP = NETWORK / "gallery-early03" / "source-map.json"
EARLY03_EXECUTION_PLAN = NETWORK / "gallery-early03" / "execution-plan.json"
CONTROL03 = BASE / "publication" / "root-control03-acceptance.json"
FROM_TS = "20000101000000"
TO_TS = "20080512210044"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def bind(path: Path, role: str) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"missing binding input: {path}")
    return {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size, "role": role}


def load_driver_module():
    spec = importlib.util.spec_from_file_location("reusable_image_driver_v2_news_content02", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load accepted reusable driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_evidence(item: dict[str, object], rank: int) -> tuple[dict[str, object], list[dict[str, object]], Path]:
    records = item.get("source_evidence") or []
    if not isinstance(records, list) or not records or not isinstance(records[0], dict):
        raise RuntimeError(f"candidate {rank} has no source evidence records")
    record = dict(records[0])
    path = ROOT / str(record.get("path") or "")
    original = str(item.get("original") or "")
    if not path.is_file() or sha(path) != str(record.get("sha256") or "").lower():
        raise RuntimeError(f"candidate {rank} source evidence hash/path mismatch")
    line = int(record.get("line") or 0)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if line < 1 or line > len(lines):
        raise RuntimeError(f"candidate {rank} source evidence line is outside file")
    encoded = original.replace(":", "%3A").replace("/", "%2F")
    if original not in lines[line - 1] and encoded not in lines[line - 1]:
        raise RuntimeError(f"candidate {rank} source evidence literal is absent")
    evidence = {
        "path": record["path"],
        "line": line,
        "literal": original,
        "requested": record.get("requested", original),
        "sha256": str(record["sha256"]).lower(),
        "element": record.get("element"),
        "parent_href": record.get("parent_href"),
        "underlying_source": record.get("underlying_source"),
        "underlying_source_line": record.get("underlying_source_line"),
    }
    return evidence, [dict(x) for x in records if isinstance(x, dict)], path


def build_candidate(item: dict[str, object], rank: int, driver) -> tuple[dict[str, object], Path]:
    original = str(item.get("original") or "")
    evidence, records, source_path = source_evidence(item, rank)
    query_url = driver.cdx_query_url(original, from_ts=FROM_TS, to_ts=TO_TS, limit=500, show_resume=True, fields=FIELDS)
    expected = {
        "archive_query_required": True,
        "mime_types": ["image/jpeg", "image/gif", "image/png"],
        "pillow_formats": ["JPEG", "GIF", "PNG"],
        "all_gif_frames": True,
        "reencode": False,
        "script_execution": False,
        "query_window": {"from": FROM_TS, "to": TO_TS},
    }
    candidate = {
        "target_key": f"NEWS-CONTENT02-{rank:02d}",
        "priority": rank,
        "rank": rank,
        "kind": "image",
        "original": original,
        "canonical": item.get("canonical", original),
        "literal": original,
        "expected": expected,
        "expected_mime": expected["mime_types"],
        "origin": item.get("origin"),
        "page_count_v23": item.get("page_count_v23"),
        "pages_v23": item.get("pages_v23"),
        "reference_count_v23": item.get("reference_count_v23"),
        "selection_reason": item.get("selection_reason"),
        "source_evidence": evidence,
        "source_evidence_records": records,
        "source_evidence_verified": True,
        "source_page_context": {
            "v23_candidate_rank": rank,
            "v23_pages": item.get("pages_v23"),
            "selection_reason": item.get("selection_reason"),
            "root_candidate_acceptance": rel(SOURCE_ACCEPTANCE),
        },
        "cdx_mode": "fresh",
        "current_state": "prepared_not_executed",
        "network_scope": "fresh exact CDX only; no cache fallback, no automatic pagination, no URL expansion",
        "known_bad_capture": None,
        "known_positive_cache_rows": [],
        "fallback_label": None,
        "cache": {
            "mode": "disabled",
            "reason": "NEWS-CONTENT02 is exact fresh-only; no positive cache fallback is authorized",
        },
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
            "query_url": query_url,
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
        "prior_evidence": item.get("prior_search"),
        "source_candidate_sha256": sha(SOURCE),
        "network_performed_in_this_plan": False,
    }
    return candidate, source_path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / "output"
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise RuntimeError("NEWS-CONTENT02 output directory is not empty")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    acceptance = json.loads(SOURCE_ACCEPTANCE.read_text(encoding="utf-8"))
    if acceptance.get("accepted") is not True or acceptance.get("candidate_count") != 20:
        raise RuntimeError("v23 candidate acceptance is not the exact 20-item acceptance")
    if acceptance.get("plan_sha256") != sha(SOURCE):
        raise RuntimeError("v23 source acceptance SHA mismatch")
    if source.get("candidate_count") != 20 or len(source.get("candidates") or []) != 20:
        raise RuntimeError("v23 source candidate count is not 20")
    if sha(V23_PROVENANCE) != str(acceptance.get("source_provenance_sha256") or "").lower():
        raise RuntimeError("v23 provenance SHA mismatch")
    early03 = json.loads(EARLY03_ACCEPTANCE.read_text(encoding="utf-8"))
    if early03.get("accepted") is not True or early03.get("failure_streak_end") != 0:
        raise RuntimeError("EARLY03 latest tail is not accepted zero")
    control03 = json.loads(CONTROL03.read_text(encoding="utf-8"))
    if not (control03.get("accepted") is True and control03.get("resume_gate_passed") is True and control03.get("control_final_streak") == 0):
        raise RuntimeError("CONTROL03 is not a valid zero-tail control gate")
    driver = load_driver_module()
    candidates = []
    source_bindings: dict[str, dict[str, object]] = {
        "v23_candidates": bind(SOURCE, "root-accepted exact twenty fresh v23 body-illustration candidates"),
        "v23_candidates_acceptance": bind(SOURCE_ACCEPTANCE, "root acceptance of exact twenty fresh candidates"),
        "v23_export_provenance": bind(V23_PROVENANCE, "accepted v23 export provenance"),
        "early03_acceptance": bind(EARLY03_ACCEPTANCE, "latest root-accepted EARLY03 tail-zero receipt"),
        "early03_batch_report": bind(EARLY03_REPORT, "EARLY03 actual report and latest source response evidence"),
        "early03_source_map": bind(EARLY03_SOURCE_MAP, "EARLY03 sanitized source map"),
        "early03_execution_plan": bind(EARLY03_EXECUTION_PLAN, "EARLY03 actual execution plan"),
        "control03_acceptance": bind(CONTROL03, "last accepted successful control gate after historical stop"),
        "reusable_v2_driver": bind(DRIVER, "root-accepted reusable V2 transport and image acceptance core"),
        "reusable_v2_fixture": bind(DRIVER_FIXTURE, "root-accepted reusable V2 offline fixture contract"),
    }
    source_page_bindings: dict[str, dict[str, object]] = {}
    for rank, item in enumerate(source["candidates"], 1):
        candidate, source_path = build_candidate(item, rank, driver)
        candidates.append(candidate)
        source_page_bindings[f"source_page_{rank:02d}"] = bind(source_path, f"v23 source literal evidence for NEWS-CONTENT02-{rank:02d}")
    source_bindings.update(source_page_bindings)
    latest_receipt_sha = sha(EARLY03_ACCEPTANCE)
    control_sha = sha(CONTROL03)
    policy = {
        "from": FROM_TS,
        "to": TO_TS,
        "limit": 500,
        "showResumeKey": True,
        "collapse": False,
        "matchType": "exact",
        "max_originals": 20,
        "max_attempts": 60,
        "window_seconds": 900.0,
        "max_total_body_bytes": 64 * 1024 * 1024,
        "max_entity_body_bytes": 8 * 1024 * 1024,
        "min_dispatch_seconds": 5.25,
        "min_request_start_seconds": 5.0,
        "disk_floor_bytes": 11_005_853_696,
        "direct_first": True,
        "proxy": "http://127.0.0.1:7890",
        "tls_verification": True,
        "automatic_redirects": 0,
        "stop_http_codes": [429, 503],
        "cooldown_seconds": 120,
        "user_agent": "wow-recovery-reusable-image-v1/20261016",
        "prior_failure_tail": 0,
        "transport_policy": "batch_after_direct_failure",
        "fresh_exact_only": True,
        "cache_fallback": False,
        "no_automatic_pagination": True,
    }
    plan = {
        "schema": "wow-recovery.reusable-image-plan.v1",
        "batch_id": "WAYBACK-NEWS-CONTENT02-20261016",
        "prepared_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "prepared_not_executed",
        "execution_status": "prepared_not_executed",
        "network_authorized": False,
        "network_requests": 0,
        "candidate_count": 20,
        "candidates": candidates,
        "cached_targets": [],
        "fresh_targets": 20,
        "output_dir": rel(output),
        "policy": policy,
        "previous_batch": {
            "name": "WAYBACK-GALLERYEARLY03-20261016",
            "prior_failure_tail": 0,
            "tail_receipt_path": rel(EARLY03_ACCEPTANCE),
            "tail_receipt_sha256": latest_receipt_sha,
            "tail_report_path": rel(EARLY03_REPORT),
            "tail_report_sha256": sha(EARLY03_REPORT),
            "control_gate_receipt_path": rel(CONTROL03),
            "control_gate_receipt_sha256": control_sha,
            "control_gate_required": True,
            "historical_news_tail_preserved": 5,
            "latest_tail_source": "root-accepted EARLY03 source receipt; no later stop occurred",
        },
        "input_bindings": source_bindings,
        "source_plan_path": rel(SOURCE),
        "source_plan_sha256": sha(SOURCE),
        "source_acceptance_path": rel(SOURCE_ACCEPTANCE),
        "source_acceptance_sha256": sha(SOURCE_ACCEPTANCE),
        "scope": "exact twenty fresh v23 NEWS body-illustration originals; no NEWS-CONTENT01 repeat, cache fallback, pagination, or URL expansion",
        "selection_rule": "fresh exact CDX latest valid pre-anchor image capture, then at most two distinct digest replay candidates",
        "payload_status": "pending_root",
        "accepted_payloads_are_source_data_only": True,
    }
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bindings = {
        "schema": "wow-recovery.reusable-image-input-bindings.v1",
        "batch_id": plan["batch_id"],
        "plan_path": rel(PLAN_PATH),
        "plan_sha256": sha(PLAN_PATH),
        "driver_path": rel(DRIVER),
        "driver_sha256": sha(DRIVER),
        "fixture_mode": "offline_only_until_parent_GO",
        "network_authorized": False,
        "network_requests": 0,
        "prepared_only": True,
        "source_bindings": source_bindings,
        "latest_tail": {
            "receipt_path": rel(EARLY03_ACCEPTANCE),
            "receipt_sha256": latest_receipt_sha,
            "failure_streak_end": 0,
        },
        "control_gate": {
            "receipt_path": rel(CONTROL03),
            "receipt_sha256": control_sha,
            "resume_gate_passed": True,
            "control_final_streak": 0,
        },
    }
    BINDINGS_PATH.write_text(json.dumps(bindings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    driver.configure_from_plan(PLAN_PATH)
    validated_plan, _ = driver.load_and_validate_inputs()
    print(json.dumps({
        "batch_id": plan["batch_id"],
        "candidate_count": len(validated_plan["candidates"]),
        "fresh_targets": plan["fresh_targets"],
        "prior_failure_tail": plan["previous_batch"]["prior_failure_tail"],
        "latest_tail_receipt_sha256": latest_receipt_sha,
        "control_gate_sha256": control_sha,
        "plan_sha256": sha(PLAN_PATH),
        "bindings_sha256": sha(BINDINGS_PATH),
        "driver_sha256": sha(DRIVER),
        "network_requests": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

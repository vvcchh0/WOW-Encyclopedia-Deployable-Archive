from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit


ROOT = Path(r"D:\WOW_Encyclopedia")
BASE = ROOT / "research" / "continuous-recovery-20261016"
NETWORK = BASE / "network"
BATCH = NETWORK / "gallery-neighbors-other4"
SOURCE = BASE / "local-audit" / "gallery-neighbors" / "transport-unknown-other4-candidates.json"
ACCEPTANCE = BASE / "publication" / "root-gallery-neighbors-other4-candidates-acceptance.json"
PRIOR_SOURCE = BASE / "publication" / "root-gallery-neighbors-full15-source-acceptance.json"
PRIOR_PLAN = NETWORK / "gallery-neighbors-full15" / "plan.json"
PRIOR_REPORT = NETWORK / "gallery-neighbors-full15" / "output" / "batch-report.json"
PRIOR_SOURCE_MAP = NETWORK / "gallery-neighbors-full15" / "output" / "source-map.json"
CONTROL03 = BASE / "publication" / "root-control03-acceptance.json"
PREFIX04 = BASE / "publication" / "root-gallery-prefix04-acceptance.json"
DRIVER = NETWORK / "reusable-image-driver-v2" / "reusable_image_driver.py"
DRIVER_ACCEPTANCE = BASE / "publication" / "root-reusable-v2-code-acceptance.json"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
FROM_TS = "20000101000000"
TO_TS = "20080512210044"

# The first and third other4 targets have complete, SHA-bound exact CDX
# responses from the prior neighboring run.  Their image replays were
# transport-unknown, so the CDX is reusable evidence while the image replay is
# deliberately retried in this one bounded window.  The other two targets had
# no usable CDX response and remain fresh exact-CDX targets.
CACHED_SOURCES = {
    1: {"batch": "gallery-neighbors03", "attempt": 10, "target_key": "GALLERY-NEIGHBOR03-05"},
    3: {"batch": "gallery-neighbors03", "attempt": 13, "target_key": "GALLERY-NEIGHBOR03-07"},
}


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
    encoded = quote(literal, safe="")
    for number, line in enumerate(lines, 1):
        if literal in line or encoded in line:
            return number
    raise RuntimeError(f"source literal missing: {literal}")


def load_driver():
    spec = importlib.util.spec_from_file_location("reusable_v2_other4", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen V2 driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scalar_prior_attempts(target: str) -> list[dict[str, object]]:
    """Keep compact prior transport evidence, never headers/body content."""
    result: list[dict[str, object]] = []
    for batch in ("gallery-neighbors01", "gallery-neighbors02", "gallery-neighbors03", "gallery-neighbors-full15"):
        state_path = NETWORK / batch / "output" / "state.json"
        if not state_path.is_file():
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        for attempt in state.get("attempts", []):
            url = str(attempt.get("url") or "")
            cdx_target = parse_qs(urlsplit(url).query).get("url", [""])[0]
            is_cdx = "/cdx/search/cdx?" in url and cdx_target == target
            is_replay = "/web/" in url and url.rsplit("id_/", 1)[-1] == target
            if not (is_cdx or is_replay):
                continue
            result.append({
                "batch": batch,
                "attempt": attempt.get("attempt"),
                "label": attempt.get("label"),
                "phase": "cdx" if is_cdx else "replay",
                "transport": attempt.get("transport"),
                "curl_exit": attempt.get("curl_exit"),
                "source_status": attempt.get("source_status"),
                "body_bytes": attempt.get("body_bytes"),
                "headers_path": attempt.get("headers_path"),
                "body_path": attempt.get("body_path"),
                "finished_utc": attempt.get("finished_utc"),
            })
    return result


def cached_metadata(module, candidate: dict[str, object], info: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    batch = str(info["batch"])
    out = NETWORK / batch / "output"
    state = json.loads((out / "state.json").read_text(encoding="utf-8"))
    report = json.loads((out / "batch-report.json").read_text(encoding="utf-8"))
    attempt = next(item for item in state["attempts"] if item.get("attempt") == info["attempt"])
    result = next(item for item in report["results"] if item.get("target_key") == info["target_key"])
    body_path = ROOT / str(attempt["body_path"])
    headers_path = ROOT / str(attempt["headers_path"])
    source_report = out / "batch-report.json"
    if not body_path.is_file() or not headers_path.is_file() or not source_report.is_file():
        raise RuntimeError(f"cached evidence files missing for {candidate['target_key']}")
    parsed = module.parse_cdx(body_path.read_bytes(), 500)
    if not (parsed.get("valid") and parsed.get("complete") and not parsed.get("resume_keys")
            and not parsed.get("potential_truncation") and len(parsed.get("rows", [])) < 500):
        raise RuntimeError(f"cached evidence is not complete for {candidate['target_key']}")
    classified = module.classify_cdx(parsed, candidate)
    if not classified.get("selected"):
        raise RuntimeError(f"cached evidence has no strict selected row for {candidate['target_key']}")
    selected_view = classified["selected"][0]
    selected_raw = next(
        row for row in parsed["rows"]
        if str(row.get("timestamp")) == str(selected_view.get("timestamp"))
        and str(row.get("digest")) == str(selected_view.get("digest"))
        and str(row.get("original")) == str(selected_view.get("original"))
    )
    cached = {
        "body_bytes": body_path.stat().st_size,
        "body_sha256": sha(body_path),
        "coverage_window": {"coverage_complete_for_global_window": True, "from": FROM_TS, "to": TO_TS},
        "evidence_note": "SHA-bound exact CDX was HTTP 200, below limit, and had no resume key; prior replay ended transport-unknown. Cache is replay evidence only.",
        "original": candidate["original"],
        "potential_truncation": False,
        "query_url": candidate["query"]["query_url"],
        "raw_body_path": rel(body_path),
        "raw_headers_path": rel(headers_path),
        "raw_headers_sha256": sha(headers_path),
        "record_count": len(parsed["rows"]),
        "resume_keys": [],
        "rows": parsed["rows"],
        "selected": selected_raw,
        "source_curl_exit": 0,
        "source_report_path": rel(source_report),
        "source_report_sha256": sha(source_report),
        "source_status": 200,
        "source_target_key": info["target_key"],
        "source_transport": attempt.get("transport"),
    }
    module._validate_cached_evidence(candidate, candidate["query"], cached)
    replay_results = result.get("replay_results") or []
    return cached, {
        "batch": batch,
        "attempt": attempt.get("attempt"),
        "target_key": info["target_key"],
        "raw_body_path": rel(body_path),
        "raw_body_sha256": cached["body_sha256"],
        "raw_headers_path": rel(headers_path),
        "raw_headers_sha256": cached["raw_headers_sha256"],
        "source_report_path": rel(source_report),
        "source_report_sha256": cached["source_report_sha256"],
        "record_count": cached["record_count"],
        "selected_timestamp": cached["selected"]["timestamp"],
        "selected_digest": cached["selected"]["digest"],
        "prior_replay_status": [r.get("reasons", ["unknown"]) for r in replay_results],
    }


def make_candidate(module, item: dict[str, object], index: int, lines: list[str], source_sha: str,
                   acceptance_sha: str) -> tuple[dict[str, object], dict[str, object] | None]:
    original = str(item["original"])
    origin = item["source_evidence"]
    if not isinstance(origin, dict):
        raise RuntimeError(f"source evidence missing for {original}")
    expected_mime = ["image/jpeg"]
    candidate: dict[str, object] = {
        "target_key": f"GALLERY-NEIGHBORS-OTHER4-{index:02d}",
        "priority": index,
        "kind": "image",
        "original": original,
        "literal": original,
        "filename_class": item.get("filename_class"),
        "expected_mime": expected_mime,
        "expected": {"mime_types": expected_mime, "pillow_formats": ["JPEG"], "all_gif_frames": False, "reencode": False, "script_execution": False},
        "source_evidence": {
            "literal": original,
            "path": rel(SOURCE),
            "line": source_line(lines, original),
            "sha256": source_sha,
            "candidate_index": index,
            "source_acceptance_path": rel(ACCEPTANCE),
            "source_acceptance_sha256": acceptance_sha,
            "source_row_index": origin.get("row_index"),
            "source_result_label": origin.get("result_label"),
            "source_row": origin.get("row"),
            "origin_evidence_path": origin.get("path"),
            "origin_evidence_sha256": origin.get("sha256"),
        },
        "source_page_context": {
            "gallery_context": item.get("gallery_context"),
            "state": item.get("state"),
            "relationship": item.get("relationship"),
            "source_acceptance_row_index": origin.get("row_index"),
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
            "acceptance": ["http_status_200", "memento_datetime_present_and_exact", "link_original_exact_default_port_only", "expected_image_content_type", "magic_and_pillow_decode", "all_gif_frames_loaded", "decoded_payload_sha1_matches_cdx_digest"],
            "accepted_payloads_are_source_data_only": True,
        },
        "prior_local_evidence": scalar_prior_attempts(original),
        "prior_evidence_status": "prior_replay_transport_unknown; complete_exact_cdx_cache_bound" if index in CACHED_SOURCES else "prior_transport_unknown_preserved; fresh_exact_cdx_required",
        "cdx_mode": "cached" if index in CACHED_SOURCES else "fresh",
        "known_positive_cache_rows": [],
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
            "query_url": cdx_url(original),
        },
        "fallback_label": None,
    }
    cache_summary = None
    if index in CACHED_SOURCES:
        cached, cache_summary = cached_metadata(module, candidate, CACHED_SOURCES[index])
        candidate["cached_cdx"] = cached
    return candidate, cache_summary


def main() -> None:
    BATCH.mkdir(parents=True, exist_ok=True)
    source_data = json.loads(SOURCE.read_text(encoding="utf-8"))
    acceptance_data = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    source_sha = sha(SOURCE)
    acceptance_sha = sha(ACCEPTANCE)
    if source_sha != "de9514eabd28be041a91283fc60521444f28983cf6f4ef27f1b5cc0837720626":
        raise RuntimeError("other4 candidate source hash changed")
    if acceptance_data.get("accepted") is not True or acceptance_data.get("candidate_sha256") != source_sha:
        raise RuntimeError("other4 acceptance does not bind the candidate source")
    if source_data.get("candidate_count") != 4 or len(source_data.get("candidates", [])) != 4:
        raise RuntimeError("other4 source is not exactly the accepted four")
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    module = load_driver()
    template = json.loads((NETWORK / "gallery-neighbors03" / "plan.json").read_text(encoding="utf-8"))
    plan = copy.deepcopy(template)
    candidates: list[dict[str, object]] = []
    cache_summaries: list[dict[str, object]] = []
    for index, item in enumerate(source_data["candidates"], 1):
        candidate, cache_summary = make_candidate(module, item, index, lines, source_sha, acceptance_sha)
        candidates.append(candidate)
        if cache_summary is not None:
            cache_summaries.append(cache_summary)

    plan.update({
        "batch_id": "GALLERY-NEIGHBORS-OTHER4",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "candidate_count": 4,
        "candidates": candidates,
        "scope": "One bounded retry for three Lunar Festival dress/model views and one thumbnail with prior transport-unknown outcomes; two exact CDX responses are reused only as SHA-bound complete caches and the other two targets use fresh exact CDX. Numeric full-image originals remain outside this batch.",
        "candidate_order_note": "Candidates retain the root-accepted other4 order: sswdress1-thumb, sswdress1, sswdress2, sswdress3.",
        "source_plan_path": rel(SOURCE),
        "source_plan_sha256": source_sha,
        "source_acceptance_path": rel(ACCEPTANCE),
        "source_acceptance_sha256": acceptance_sha,
        "output_dir": rel(BATCH / "output"),
        "mode": "prepared_not_executed_pending_root_go",
        "network_authorized": False,
        "no_network_before_parent_go": True,
        "excluded_due_to_prior_acceptance": {
            "unknown_numeric_full_count": 7,
            "relationship": "The seven still-unknown numeric full originals remain excluded; this retry is limited to the four root-approved Lunar Festival dress/model neighboring materials.",
        },
        "pending_root_acceptance": {
            "required_before_dispatch": True,
            "note": "Offline preparation only; dispatch requires root acceptance of this exact plan, bindings, and fixture evidence plus explicit GO.",
            "required_receipts": ["root-gallery-neighbors-other4-plan-acceptance.json"],
        },
    })
    plan["policy"].update({
        "cdx_mode": "cached_exact_for_two_fresh_exact_for_two",
        "from": FROM_TS,
        "to": TO_TS,
        "limit": 500,
        "showResumeKey": True,
        "collapse": False,
        "matchType": "exact",
        "max_attempts": 24,
        "max_originals": 20,
        "window_seconds": 600.0,
        "max_total_body_bytes": 16 * 1024 * 1024,
        "max_entity_body_bytes": 8 * 1024 * 1024,
        "prior_failure_tail": 0,
        "transport_policy": "batch_after_direct_failure",
    })
    plan["previous_batch"] = {
        "status": "neighbors-full15_source_accepted_tail0",
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
        "note": "Latest NETWORK27 full15 source acceptance ended with tail zero. CONTROL03 remains the accepted successful control gate required by frozen V2 validation; earlier stopped tails remain preserved in frozen receipts.",
    }
    plan["input_bindings"] = {
        "other4_candidates": binding(SOURCE, "root-approved four exact neighboring originals"),
        "other4_candidates_acceptance": binding(ACCEPTANCE, "root acceptance of the four-target retry boundary"),
        "latest_neighbors_full15_source_acceptance": binding(PRIOR_SOURCE, "latest accepted NETWORK27 source result and tail-zero binding"),
        "prior_neighbors_full15_plan": binding(PRIOR_PLAN, "frozen previous exact-neighbor plan"),
        "prior_neighbors_full15_report": binding(PRIOR_REPORT, "frozen previous source report"),
        "prior_neighbors_full15_source_map": binding(PRIOR_SOURCE_MAP, "frozen previous source map"),
        "control03_acceptance": binding(CONTROL03, "accepted control gate for prior tail zero"),
        "prefix04_acceptance": binding(PREFIX04, "positive exact neighboring-index source evidence"),
        "reusable_v2_driver": binding(DRIVER, "frozen reusable image V2 driver"),
        "reusable_v2_code_acceptance": binding(DRIVER_ACCEPTANCE, "root acceptance of frozen V2 core"),
    }
    for index, candidate in enumerate(candidates, 1):
        if candidate.get("cdx_mode") != "cached":
            continue
        cached = candidate["cached_cdx"]
        for label, path_key in (("body", "raw_body_path"), ("headers", "raw_headers_path"), ("source_report", "source_report_path")):
            path = ROOT / str(cached[path_key])
            plan["input_bindings"][f"cached_{index:02d}_{label}"] = binding(path, f"SHA-bound cached CDX {index:02d} {label}")
    write_json(BATCH / "plan.json", plan)
    plan_sha = sha(BATCH / "plan.json")
    write_json(BATCH / "input-bindings.json", {
        "schema": "wow-recovery.gallery-neighbors-other4-input-bindings.v1",
        "batch_id": plan["batch_id"],
        "mode": plan["mode"],
        "network_requests": 0,
        "plan_sha256": plan_sha,
        "driver_sha256": sha(DRIVER),
        "source_bindings": plan["input_bindings"],
        "network_authorized": False,
        "required_before_dispatch": ["root accepts this exact other4 plan and fixtures", "parent gives explicit GO"],
        "latest_tail_binding": {"path": rel(PRIOR_SOURCE), "sha256": sha(PRIOR_SOURCE), "tail": 0, "role": "latest root-accepted NETWORK27 source result and prior tail-zero evidence"},
        "historical_tail_preserved": {"prefix03": 5, "role": "historical stopped tail remains in its frozen receipt; current start tail is bound to NETWORK27 zero"},
        "cache_split": {"cached_count": len(cache_summaries), "fresh_count": len(candidates) - len(cache_summaries), "cached_indices": sorted(CACHED_SOURCES), "cached_evidence": cache_summaries},
        "fixture_results": {"path": rel(BATCH / "fixture-results.json"), "pending": True},
    })
    module.configure_from_plan(BATCH / "plan.json")
    validated, _ = module.load_and_validate_inputs()
    if [x["original"] for x in validated["candidates"]] != [x["original"] for x in candidates]:
        raise RuntimeError("production candidate order changed during validation")
    print(json.dumps({
        "plan_sha256": plan_sha,
        "driver_sha256": sha(DRIVER),
        "source_sha256": source_sha,
        "acceptance_sha256": acceptance_sha,
        "candidate_count": len(candidates),
        "cached_count": len(cache_summaries),
        "fresh_count": len(candidates) - len(cache_summaries),
        "cached_indices": sorted(CACHED_SOURCES),
        "production_validation": "passed",
        "network_requests": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

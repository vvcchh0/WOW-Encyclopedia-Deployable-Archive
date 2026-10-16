from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\WOW_Encyclopedia")
BASE = ROOT / "research" / "continuous-recovery-20261016"
NETWORK = BASE / "network"
OUT = NETWORK / "news-content03"
PLAN_PATH = OUT / "plan.json"
BINDINGS_PATH = OUT / "input-bindings.json"
SOURCE_PLAN = NETWORK / "news-content02" / "plan.json"
SOURCE_OUTPUT = NETWORK / "news-content02" / "output"
SOURCE_STATE = SOURCE_OUTPUT / "state.json"
SOURCE_REPORT = SOURCE_OUTPUT / "batch-report.json"
SOURCE_MAP = SOURCE_OUTPUT / "source-map.json"
SOURCE_ACCEPTANCE = BASE / "publication" / "root-news-content02-source-acceptance.json"
DRIVER = NETWORK / "reusable-image-driver-v2" / "reusable_image_driver.py"
DRIVER_FIXTURE = NETWORK / "reusable-image-driver-v2" / "fixture-results-v2.json"
FROM_TS = "20000101000000"
TO_TS = "20080512210044"
RETRY_RANKS = [2, 3, 5, 7, 10, 11, 13, 14, 18, 20]
CACHED_RANKS = {10, 11, 20}
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def bind(path: Path, role: str) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"missing binding input: {path}")
    return {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size, "role": role}


def load_driver():
    spec = importlib.util.spec_from_file_location("reusable_image_driver_v2_news_content03", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load accepted V2 driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / "output"
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise RuntimeError("NEWS-CONTENT03 output directory is not empty")
    plan02 = json.loads(SOURCE_PLAN.read_text(encoding="utf-8"))
    state02 = json.loads(SOURCE_STATE.read_text(encoding="utf-8"))
    report02 = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    acceptance02 = json.loads(SOURCE_ACCEPTANCE.read_text(encoding="utf-8"))
    if acceptance02.get("accepted") is not True or acceptance02.get("failure_streak_end") != 1:
        raise RuntimeError("NEWS-CONTENT02 acceptance does not bind actual tail one")
    if acceptance02.get("batch_report_sha256") != sha(SOURCE_REPORT):
        raise RuntimeError("NEWS-CONTENT02 acceptance/report SHA mismatch")
    if len(plan02.get("candidates") or []) != 20:
        raise RuntimeError("NEWS-CONTENT02 source plan is not the accepted twenty-target plan")
    result_by_rank = {int(item["target_key"].rsplit("-", 1)[1]): item for item in report02.get("results", [])}
    if set(result_by_rank) != set(range(1, 21)):
        raise RuntimeError("NEWS-CONTENT02 report does not contain all twenty outcomes")
    for rank in RETRY_RANKS:
        result = result_by_rank[rank]
        if rank in CACHED_RANKS:
            cdx = result.get("cdx") or {}
            # CONTENT02's accepted report encodes completeness in cdx.status;
            # the raw CDX is still reparsed below and must independently be
            # valid, complete, non-resumed, and below the limit.
            if result.get("status") != "complete_with_replay_candidates" or cdx.get("status") != "complete_with_replay_candidates":
                raise RuntimeError(f"cached target {rank} lacks complete exact CDX evidence")
        elif result.get("status") != "transport_or_http_unknown":
            raise RuntimeError(f"fresh retry target {rank} is not transport unknown")
    driver = load_driver()
    old_by_rank = {int(item["rank"]): item for item in plan02["candidates"]}
    state_attempts = state02.get("attempts") or []
    cached_evidence: dict[int, dict[str, object]] = {}
    for rank in sorted(CACHED_RANKS):
        old = old_by_rank[rank]
        label = f"NEWS-CONTENT02-{rank:02d}:cdx"
        matching = [a for a in state_attempts if a.get("label") == label and a.get("sent") is True]
        if not matching:
            raise RuntimeError(f"no sent CDX attempt for cached target {rank}")
        attempt = matching[-1]
        if attempt.get("curl_exit") != 0 or attempt.get("source_status") != 200:
            raise RuntimeError(f"cached CDX source was not HTTP 200 for target {rank}")
        body_path = ROOT / str(attempt.get("body_path") or "")
        headers_path = ROOT / str(attempt.get("headers_path") or "")
        if not body_path.is_file() or not headers_path.is_file():
            raise RuntimeError(f"cached raw CDX evidence missing for target {rank}")
        parsed = driver.parse_cdx(body_path.read_bytes(), int(old["query"]["limit"]))
        if not parsed.get("valid") or not parsed.get("complete") or parsed.get("resume_keys") or parsed.get("potential_truncation"):
            raise RuntimeError(f"cached CDX evidence is incomplete for target {rank}")
        if len(parsed.get("rows") or []) >= int(old["query"]["limit"]):
            raise RuntimeError(f"cached CDX evidence reaches limit for target {rank}")
        result = result_by_rank[rank]
        selected = ((result.get("cdx") or {}).get("selected") or [])
        if not selected:
            raise RuntimeError(f"cached target {rank} has no selected row")
        selected_meta = selected[0]
        selected_index = str(selected_meta.get("record_index", ""))
        # CONTENT02's report projection omits urlkey, while the raw CDX
        # parser preserves it. Re-bind the report selection to the exact raw
        # row using the record index and all projected capture fields.
        selected_row = next(
            (
                row for row in parsed.get("rows", [])
                if str(row.get("record_index", "")) == selected_index
                and all(str(row.get(field, "")) == str(selected_meta.get(field, ""))
                        for field in FIELDS if field != "urlkey")
            ),
            None,
        )
        if selected_row is None:
            raise RuntimeError(f"cached selected row is absent from raw CDX for target {rank}")
        cached_evidence[rank] = {
            "query_url": old["query"]["query_url"],
            "original": old["original"],
            "source_report_path": rel(SOURCE_REPORT),
            "source_report_sha256": sha(SOURCE_REPORT),
            "raw_body_path": rel(body_path),
            "body_sha256": sha(body_path),
            "body_bytes": body_path.stat().st_size,
            "raw_headers_path": rel(headers_path),
            "raw_headers_sha256": sha(headers_path),
            "source_curl_exit": int(attempt["curl_exit"]),
            "coverage_window": {"from": old["query"]["from"], "to": old["query"]["to"], "coverage_complete_for_global_window": True},
            "record_count": len(parsed["rows"]),
            "rows": parsed["rows"],
            "selected": selected_row,
            "source_attempt": int(attempt["attempt"]),
        }
    candidates: list[dict[str, object]] = []
    for rank in RETRY_RANKS:
        candidate = copy.deepcopy(old_by_rank[rank])
        candidate["target_key"] = f"NEWS-CONTENT03-{rank:02d}"
        candidate["rank"] = rank
        candidate["current_state"] = "prepared_not_executed"
        candidate["network_performed_in_this_plan"] = False
        candidate["network_scope"] = "NEWS-CONTENT03 bounded retry; exact identity only"
        candidate["retry_of"] = {"batch_id": plan02["batch_id"], "target_key": old_by_rank[rank]["target_key"], "rank": rank, "outcome": result_by_rank[rank].get("status")}
        if rank in CACHED_RANKS:
            candidate["cdx_mode"] = "cached"
            candidate["cached_cdx"] = cached_evidence[rank]
            candidate["cache"] = {"mode": "cached_bound_complete_exact_cdx", "source_attempt": cached_evidence[rank]["source_attempt"], "latestness": "exact global 2000..anchor CDX; no replay success in prior batch"}
        else:
            candidate["cdx_mode"] = "fresh"
            candidate.pop("cached_cdx", None)
            candidate["known_positive_cache_rows"] = []
            candidate["fallback_label"] = None
            candidate["cache"] = {"mode": "disabled", "reason": "fresh exact retry only; no positive fallback or new URL"}
        candidates.append(candidate)
    old_bindings = plan02.get("input_bindings") or {}
    input_bindings = {key: copy.deepcopy(value) for key, value in old_bindings.items()}
    input_bindings.update({
        "news_content02_plan": bind(SOURCE_PLAN, "frozen NEWS-CONTENT02 input plan"),
        "news_content02_state": bind(SOURCE_STATE, "frozen NEWS-CONTENT02 sent-attempt state"),
        "news_content02_batch_report": bind(SOURCE_REPORT, "root-accepted NEWS-CONTENT02 report; tail one"),
        "news_content02_source_map": bind(SOURCE_MAP, "frozen NEWS-CONTENT02 source map"),
        "news_content02_source_acceptance": bind(SOURCE_ACCEPTANCE, "root acceptance binding actual tail one"),
        "reusable_v2_driver": bind(DRIVER, "unchanged accepted V2 transport/image core"),
        "reusable_v2_fixture": bind(DRIVER_FIXTURE, "accepted V2 offline fixture contract"),
    })
    for rank, cached in cached_evidence.items():
        input_bindings[f"cached_{rank:02d}_body"] = bind(ROOT / cached["raw_body_path"], f"complete exact CDX raw body for retry target {rank}")
        input_bindings[f"cached_{rank:02d}_headers"] = bind(ROOT / cached["raw_headers_path"], f"complete exact CDX raw headers for retry target {rank}")
    policy = {
        "from": FROM_TS, "to": TO_TS, "limit": 500, "showResumeKey": True, "collapse": False, "matchType": "exact",
        "max_originals": 20, "max_attempts": 40, "window_seconds": 600.0,
        "max_total_body_bytes": 32 * 1024 * 1024, "max_entity_body_bytes": 8 * 1024 * 1024,
        "min_dispatch_seconds": 5.25, "min_request_start_seconds": 5.0, "disk_floor_bytes": 11_005_853_696,
        "direct_first": True, "proxy": "http://127.0.0.1:7890", "tls_verification": True, "automatic_redirects": 0,
        "stop_http_codes": [429, 503], "cooldown_seconds": 120, "user_agent": "wow-recovery-reusable-image-v1/20261016",
        "prior_failure_tail": 1, "transport_policy": "batch_after_direct_failure", "fresh_exact_only": True,
        "cache_fallback": False, "no_automatic_pagination": True, "stop_after_new_transport_failures": 4,
    }
    plan = {
        "schema": "wow-recovery.reusable-image-plan.v1", "batch_id": "WAYBACK-NEWS-CONTENT03-20261016",
        "prepared_utc": datetime.now(timezone.utc).isoformat(), "mode": "prepared_not_executed",
        "execution_status": "prepared_not_executed", "network_authorized": False, "network_requests": 0,
        "candidate_count": 10, "candidates": candidates, "cached_targets": sorted(CACHED_RANKS), "fresh_targets": len(RETRY_RANKS) - len(CACHED_RANKS),
        "output_dir": rel(output), "policy": policy, "input_bindings": input_bindings,
        "previous_batch": {
            "name": plan02["batch_id"], "prior_failure_tail": 1,
            "tail_receipt_path": rel(SOURCE_ACCEPTANCE), "tail_receipt_sha256": sha(SOURCE_ACCEPTANCE),
            "tail_report_path": rel(SOURCE_REPORT), "tail_report_sha256": sha(SOURCE_REPORT),
            "historical_news_tail_preserved": 5, "latest_tail_source": "root-accepted NEWS-CONTENT02 source receipt; no later stop",
        },
        "scope": "exact ten NEWS-CONTENT02 unknown originals only; three use SHA-bound complete exact CDX, seven use fresh exact CDX; no successes or new URL expansion",
        "retry_ranks": RETRY_RANKS, "cached_cdx_ranks": sorted(CACHED_RANKS), "fresh_cdx_ranks": [x for x in RETRY_RANKS if x not in CACHED_RANKS],
        "accepted_payloads_are_source_data_only": True, "payload_status": "pending_root",
    }
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bindings = {
        "schema": "wow-recovery.reusable-image-input-bindings.v1", "batch_id": plan["batch_id"],
        "plan_path": rel(PLAN_PATH), "plan_sha256": sha(PLAN_PATH), "driver_path": rel(DRIVER), "driver_sha256": sha(DRIVER),
        "fixture_mode": "offline_only_until_parent_GO", "network_authorized": False, "network_requests": 0, "prepared_only": True,
        "source_bindings": input_bindings,
        "previous_batch": {"batch_id": plan02["batch_id"], "tail_receipt_path": rel(SOURCE_ACCEPTANCE), "tail_receipt_sha256": sha(SOURCE_ACCEPTANCE), "failure_streak_end": 1, "report_sha256": sha(SOURCE_REPORT)},
        "retry_scope": {"ranks": RETRY_RANKS, "cached_complete_cdx_ranks": sorted(CACHED_RANKS), "fresh_cdx_ranks": [x for x in RETRY_RANKS if x not in CACHED_RANKS]},
    }
    BINDINGS_PATH.write_text(json.dumps(bindings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    driver.configure_from_plan(PLAN_PATH)
    validated, _ = driver.load_and_validate_inputs()
    print(json.dumps({
        "batch_id": plan["batch_id"], "candidate_count": len(validated["candidates"]), "retry_ranks": RETRY_RANKS,
        "cached_complete_cdx_ranks": sorted(CACHED_RANKS), "fresh_cdx_ranks": [x for x in RETRY_RANKS if x not in CACHED_RANKS],
        "prior_failure_tail": plan["previous_batch"]["prior_failure_tail"], "new_failures_to_stop": 4,
        "plan_sha256": sha(PLAN_PATH), "bindings_sha256": sha(BINDINGS_PATH), "driver_sha256": sha(DRIVER), "network_requests": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

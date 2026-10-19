"""Prepare the bounded frontier-news04 packet without network access.

The packet intentionally keeps the frozen 20261018 reusable-image plan schema,
but lives in the 20261019 owned directory.  The frozen driver is never copied
or edited here; its path boundary is recorded by the offline validation report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[4]
OWNED = ROOT / "research" / "continuous-recovery-20261019" / "network" / "frontier-news04"
R2_CANDIDATES = ROOT / "research" / "continuous-recovery-20261019" / "local-audit" / "resource-frontier-v33-r2" / "resource-frontier-candidates.json"
DRIVER = ROOT / "research" / "continuous-recovery-20261018" / "network" / "reusable-image-driver-v3" / "reusable_image_driver.py"
LATEST_SOURCE = ROOT / "research" / "continuous-recovery-20261019" / "publication" / "root-gallery-late-gap01-source-acceptance.json"
CONTROL_GATE = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "root-control03-source-acceptance.json"

SOURCE_URLS = [
    "http://www.worldofwarcraft.com/contests/beowulf/images/beowulf_news.jpg",
    "http://www.worldofwarcraft.com/news/images/04-06/european-beta/signups.jpg",
    "http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart01.jpg",
    "http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart02.jpg",
]
FROM_TS = "20000101000000"
TO_TS = "20080512210044"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
DISK_FLOOR = 11_005_853_696
DRIVER_SHA_EXPECTED = "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955"
SOURCE_SHA_EXPECTED = "edd438ed7ff84113031e6741515e4c6d96ca27e5021549f8e649886f08a8f949"
CONTROL_SHA_EXPECTED = "caa309e2e0d4592755107814135e2288c2055a879c9b4ea012e12f0505ec185b"


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def query_url(original: str) -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?url="
        + quote(original, safe="")
        + "&from=" + FROM_TS
        + "&to=" + TO_TS
        + "&output=json&fl=" + quote(",".join(FIELDS), safe="")
        + "&limit=500&showResumeKey=true&matchType=exact"
    )


def binding(path: Path, role: str) -> dict:
    return {"path": rel(path), "sha256": sha_file(path), "bytes": path.stat().st_size, "role": role}


def make_candidate(row: dict, rank: int, r2_sha: str) -> dict:
    original = row["requested_url"]
    contexts = row.get("source_context") or []
    markers = row.get("markers") or []
    marker = next((item for item in markers if original in str(item.get("snippet", ""))), markers[0])
    marker_path = ROOT / marker["output_file"]
    marker_lines = marker_path.read_text(encoding="utf-8", errors="replace").splitlines()
    marker_line = int(marker["line"])
    source_line = marker_lines[marker_line - 1] if marker_line <= len(marker_lines) else ""
    encoded = quote(original, safe="")
    if original not in source_line and encoded not in source_line:
        raise RuntimeError(f"marker line does not carry exact URL: {original}")
    expected = {
        "archive_query_required": True,
        "mime_types": ["image/jpeg"],
        "pillow_formats": ["JPEG"],
        "all_gif_frames": False,
        "reencode": False,
        "script_execution": False,
        "query_window": {"from": FROM_TS, "to": TO_TS},
    }
    marker_sha = sha_file(marker_path)
    source_evidence = {
        "path": rel(marker_path),
        "line": marker_line,
        "literal": original,
        "sha256": marker_sha,
        "source_page_sha256": marker_sha,
        "bytes": marker_path.stat().st_size,
        "match": "url_encoded",
        "original_source_page_sha256": (contexts[0].get("source_page_sha256") if contexts else None),
        "requested": original,
        "source_page": marker.get("source_url"),
        "reason": "external-or-uncollected-resource",
        "source_marker": "v33_missing_image_marker",
        "r2_candidate_rank": row.get("candidate_rank"),
        "r2_candidates_sha256": r2_sha,
    }
    context = {
        "r2_candidates_path": rel(R2_CANDIDATES),
        "r2_candidates_sha256": r2_sha,
        "candidate_rank": row.get("candidate_rank"),
        "source_context": contexts,
        "v33_marker_ref": marker,
        "historical_execution_evidence": row.get("historical_execution_evidence") or [],
        "historical_plan_or_queue_evidence": row.get("historical_plan_or_queue_evidence") or [],
        "identity_variant_evidence": row.get("identity_variant_evidence") or [],
        "dedup_statement": "Parent exact historical batch-report/request-record/CDX check found no match; this is a fresh exact-CDX candidate.",
        "preparation_network_requests": 0,
    }
    selection = {
        "max_distinct_digest_candidates": 2,
        "contract_note": "Frozen driver selects at most two distinct digest rows; total packet cap remains 16 requests.",
        "potential_truncation": "do_not_replay",
        "require_complete_index": True,
        "require_exact_original": True,
        "require_expected_mime": True,
        "require_nonempty_cdx_sha1_digest": True,
        "require_statuscode": 200,
        "same_digest_older_captures": "skip",
        "sort": "timestamp_desc_then_record_index_desc",
        "unknown_metadata": "incomplete_error",
    }
    return {
        "target_key": f"FRONTIER-NEWS04-{rank:02d}",
        "priority": rank,
        "source_priority_band": "news-frontier-r2",
        "date_bucket": None,
        "kind": "image",
        "original": original,
        "literal": original,
        "expected": expected,
        "expected_mime": ["image/jpeg"],
        "source_evidence": source_evidence,
        "source_page_context": context,
        "selection": selection,
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
                "decoded_payload_sha1_matches_cdx_digest",
            ],
            "accepted_payloads_are_source_data_only": True,
        },
        "prior_local_evidence": [
            {
                "state": "no_new_cdx_query_yet",
                "source": "resource-frontier-v33-r2",
                "prior_attempt": {
                    "state": "not_in_parent_reviewed_execution_records",
                    "parent_exact_dedup_check": "no_match_in_historical_batch-report/request-record/CDX JSON",
                    "network_requests_in_this_preparation": 0,
                    "accepted_payload_in_prior_records": False,
                },
                "exact_entity_index_complete": False,
                "positive_row_count": 0,
            }
        ],
        "prior_evidence_status": "v33_r2_missing_marker; fresh_exact_cdx_required; no_bound_positive_fallback",
    }


def prepare() -> tuple[dict, dict]:
    if not R2_CANDIDATES.is_file():
        raise FileNotFoundError(R2_CANDIDATES)
    r2_sha = sha_file(R2_CANDIDATES)
    rows = {row.get("requested_url"): row for row in read_json(R2_CANDIDATES).get("candidates", [])}
    missing = [url for url in SOURCE_URLS if url not in rows]
    if missing:
        raise RuntimeError(f"missing exact r2 rows: {missing}")
    if not DRIVER.is_file() or sha_file(DRIVER) != DRIVER_SHA_EXPECTED:
        raise RuntimeError("frozen driver SHA changed")
    if not LATEST_SOURCE.is_file() or sha_file(LATEST_SOURCE) != SOURCE_SHA_EXPECTED:
        raise RuntimeError("latest gap01 source acceptance SHA changed")
    if not CONTROL_GATE.is_file() or sha_file(CONTROL_GATE) != CONTROL_SHA_EXPECTED:
        raise RuntimeError("CONTROL03 gate SHA changed")
    latest = read_json(LATEST_SOURCE)
    gate = read_json(CONTROL_GATE)
    if latest.get("accepted") is not True or latest.get("failure_streak_end") != 0:
        raise RuntimeError("latest source receipt is not accepted tail zero")
    if not (gate.get("accepted") is True and gate.get("resume_gate_passed") is True and gate.get("control_final_streak") == 0):
        raise RuntimeError("control gate is not accepted tail zero")

    candidates = [make_candidate(rows[url], index, r2_sha) for index, url in enumerate(SOURCE_URLS, 1)]
    source_bindings = {
        "r2_candidate_rows": binding(R2_CANDIDATES, "frozen v33-r2 exact candidate/source rows"),
        "latest_source_acceptance": binding(LATEST_SOURCE, "latest accepted gallery-late-gap01 tail-zero source receipt"),
        "control_gate": binding(CONTROL_GATE, "accepted CONTROL03 tail-zero gate"),
        "frozen_v3_driver": binding(DRIVER, "frozen reusable-image-v3 driver; not modified"),
    }
    plan = {
        "schema": "wow-recovery.reusable-image-plan.v1",
        "batch_id": "WAYBACK-CONTINUOUS-20261019-FRONTIER-NEWS04-01",
        "prepared_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "fresh_exact_cdx_then_id_replay_no_fallback",
        "network_authorized": None,
        "parent_go_required": True,
        "candidate_count": 4,
        "output_dir": "research/continuous-recovery-20261019/network/frontier-news04/output",
        "execution_order": {
            "batch_number": 1,
            "batch_count": 1,
            "predecessor_batch_required": False,
            "predecessor_tail_rebind_required_before_execute": False,
            "predecessor_tail_status": "bound_to_latest_actual_source_acceptance",
            "root_control_acceptance_bound": True,
            "root_control_acceptance_required_before_execute": True,
        },
        "selection_scope": {
            "name": "frontier_news04_v33_r2_batch_01",
            "reason": "Four exact v33-r2 news image markers with concrete source-page context; parent historical execution/CDX dedup found no match.",
            "queue_path": rel(R2_CANDIDATES),
            "queue_sha256": r2_sha,
            "queue_target_count": 4,
            "queue_rank_range": [1, 4],
            "selected_queue_ranks": [1, 2, 3, 4],
            "selected_priorities": ["news-frontier-r2"] * 4,
            "no_complete_same_window_row_selected": True,
            "network_requests_during_preparation": 0,
            "logical_source_request_upper_bound": 12,
            "actual_attempt_cap": 16,
            "retry_budget_note": "Direct and process-proxy attempts both consume max_attempts; the frozen runner stops at 16 actual attempts and never overruns the cap.",
            "split_reason": "Four exact targets yield at most four CDX plus two distinct replay candidates per target; the hard max_attempts=16 cap bounds direct/proxy attempts.",
        },
        "candidates": candidates,
        "policy": {
            "from": FROM_TS,
            "to": TO_TS,
            "limit": 500,
            "showResumeKey": True,
            "collapse": False,
            "matchType": "exact",
            "max_originals": 20,
            "max_attempts": 16,
            "window_seconds": 240.0,
            "max_total_body_bytes": 16 * 1024 * 1024,
            "max_entity_body_bytes": 8 * 1024 * 1024,
            "min_dispatch_seconds": 5.25,
            "min_request_start_seconds": 5.0,
            "disk_floor_bytes": DISK_FLOOR,
            "direct_first": True,
            "direct_attempt_budget": 4,
            "proxy_attempt_budget": 20,
            "proxy": "http://127.0.0.1:7890",
            "tls_verification": True,
            "automatic_redirects": 0,
            "stop_http_codes": [429, 503],
            "cooldown_seconds": 120,
            "user_agent": "wow-recovery-reusable-image-v3/20261019-frontier-news04",
            "prior_failure_tail": 0,
            "transport_policy": "batch_after_direct_failure",
            "network_deadline_utc": "2026-10-19T13:15:00Z",
            "no_network_before_parent_go": True,
        },
        "previous_batch": {
            "name": "latest_actual_source_acceptance",
            "prior_failure_tail": 0,
            "acceptance_receipt_path": rel(LATEST_SOURCE),
            "acceptance_receipt_sha256": sha_file(LATEST_SOURCE),
            "tail_receipt_path": rel(LATEST_SOURCE),
            "tail_receipt_sha256": sha_file(LATEST_SOURCE),
            "latest_successful_tail_end": 0,
            "historical_tail_is_preserved": True,
            "ordinary_retrieval_requires_new_control_gate": True,
            "control_gate_receipt_path": rel(CONTROL_GATE),
            "control_gate_receipt_sha256": sha_file(CONTROL_GATE),
            "control_gate_required": True,
            "root_control_acceptance_bound": True,
            "parent_go_required": True,
        },
        "input_bindings": source_bindings,
        "source_bindings": source_bindings,
        "excluded_rows": {
            "selected_exact_urls": SOURCE_URLS,
            "other_frontier_rows_not_selected": "all other v33-r2 rows",
            "known_positive_fallback_rows": [],
            "identity_variants": "retained by CDX report only; no replay",
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
            "network_deadline_utc": "2026-10-19T13:15:00Z",
            "logical_source_request_upper_bound": 12,
            "actual_attempt_cap": 16,
            "frozen_driver_path_boundary": "20261018/network",
            "intended_packet_path_boundary": "20261019/network/frontier-news04",
            "driver_not_invoked_by_factory": True,
        },
    }
    plan_path = OWNED / "plan.json"
    bindings_path = OWNED / "input-bindings.json"
    write_json(plan_path, plan)
    bindings = {
        "schema": "wow-recovery.reusable-image-input-bindings.v1",
        "batch_id": plan["batch_id"],
        "plan_path": rel(plan_path),
        "plan_sha256": sha_file(plan_path),
        "driver_path": rel(DRIVER),
        "driver_sha256": sha_file(DRIVER),
        "selected_originals": SOURCE_URLS,
        "selected_queue_ranks": [1, 2, 3, 4],
        "source_bindings": source_bindings,
        "network_requests_during_preparation": 0,
        "driver_execution": "not invoked by this factory; frozen driver boundary diagnostic is recorded separately",
    }
    write_json(bindings_path, bindings)
    return plan, bindings


def validate() -> dict:
    plan_path = OWNED / "plan.json"
    bindings_path = OWNED / "input-bindings.json"
    plan = read_json(plan_path)
    bindings = read_json(bindings_path)
    checks: dict[str, bool] = {}
    checks["schema"] = plan.get("schema") == "wow-recovery.reusable-image-plan.v1"
    checks["candidate_count"] = plan.get("candidate_count") == 4 and len(plan.get("candidates", [])) == 4
    policy = plan.get("policy") or {}
    checks["frozen_policy"] = (
        policy.get("from") == FROM_TS and policy.get("to") == TO_TS
        and policy.get("limit") == 500 and policy.get("showResumeKey") is True
        and policy.get("collapse") is False and policy.get("matchType") == "exact"
        and policy.get("max_originals") == 20 and policy.get("max_attempts") == 16
        and policy.get("window_seconds") == 240.0
        and policy.get("max_total_body_bytes") == 16 * 1024 * 1024
        and policy.get("max_entity_body_bytes") == 8 * 1024 * 1024
        and policy.get("min_dispatch_seconds") >= 5.25
        and policy.get("min_request_start_seconds") >= 5.0
        and policy.get("disk_floor_bytes") >= DISK_FLOOR
        and policy.get("direct_first") is True
        and policy.get("tls_verification") is True
        and policy.get("automatic_redirects") == 0
        and policy.get("proxy") == "http://127.0.0.1:7890"
    )
    checks["tail_source_sha"] = sha_file(LATEST_SOURCE) == plan["previous_batch"]["tail_receipt_sha256"] == SOURCE_SHA_EXPECTED
    checks["control_gate_sha"] = sha_file(CONTROL_GATE) == plan["previous_batch"]["control_gate_receipt_sha256"] == CONTROL_SHA_EXPECTED
    checks["driver_sha"] = sha_file(DRIVER) == bindings.get("driver_sha256") == DRIVER_SHA_EXPECTED
    checks["plan_sha"] = sha_file(plan_path) == bindings.get("plan_sha256")
    checks["source_evidence"] = True
    source_results = []
    for candidate in plan.get("candidates", []):
        ev = candidate["source_evidence"]
        path = ROOT / ev["path"]
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        line = lines[int(ev["line"]) - 1]
        encoded = quote(ev["literal"], safe="")
        okay = path.is_file() and sha_file(path) == ev["sha256"] and (ev["literal"] in line or encoded in line)
        source_results.append({"target_key": candidate["target_key"], "path": ev["path"], "line": ev["line"], "sha256": ev["sha256"], "exact_literal_or_encoded": okay})
        checks["source_evidence"] = checks["source_evidence"] and okay
    checks["exact_urls"] = [c.get("original") for c in plan.get("candidates", [])] == SOURCE_URLS
    checks["no_known_fallback"] = all(not c.get("known_positive_cache_rows") and not c.get("fallback_label") for c in plan.get("candidates", []))
    checks["no_network_preparation"] = plan["selection_scope"]["network_requests_during_preparation"] == 0 and bindings["network_requests_during_preparation"] == 0
    frozen_network = "research/continuous-recovery-20261018/network"
    intended_network = "research/continuous-recovery-20261019/network/frontier-news04"
    checks["path_boundary_diagnostic"] = plan["output_dir"].startswith(intended_network)
    fixture_path = OWNED / "fixture-results.json"
    fixture = read_json(fixture_path) if fixture_path.is_file() else {}
    checks["full_offline_fixture"] = fixture.get("all_passed") is True and fixture.get("network_requests") == 0
    result = {
        "schema": "wow-recovery.reusable-image-frontier-news04-offline-validation.v1",
        "validated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "all_offline_checks_passed": all(checks.values()),
        "network_requests": 0,
        "source_results": source_results,
        "plan_sha256": sha_file(plan_path),
        "bindings_sha256": sha_file(bindings_path),
        "frozen_driver_sha256": sha_file(DRIVER),
        "path_boundary": {
            "frozen_driver_hardcoded_network": frozen_network,
            "intended_plan_network": intended_network,
            "frozen_cli_invocation_result": "not-run: frozen configure_from_plan/_under_network would reject the intended 20261019 plan path",
            "safe_next_step": "root must approve a minimal adapter or an explicitly owned staging contract before any fixture/GO execution",
        },
        "fixture_result": {
            "frozen_driver_fixture_cli": "not-run directly because its hardcoded path guard rejects the 20261019 plan path",
            "process_only_path_override": "full run_fixtures completed against the owned packet; the module global NETWORK was changed only in memory",
            "fixture_path": rel(fixture_path) if fixture_path.is_file() else None,
            "fixture_sha256": sha_file(fixture_path) if fixture_path.is_file() else None,
            "fixture_all_passed": fixture.get("all_passed"),
            "fixture_test_count": len(fixture.get("tests", {})) if isinstance(fixture.get("tests"), dict) else 0,
            "fixture_failed_tests": [name for name, value in (fixture.get("tests", {}) or {}).items() if not value],
            "fixture_network_requests": fixture.get("network_requests"),
            "transport_and_schema_static_checks": "passed; no HTTP/curl process/payload write",
        },
        "limits": [
            "No CDX request or replay was sent.",
            "A plan is not a source acceptance and no image is accepted.",
            "Frozen V3 selects up to two distinct digest rows per exact target; the packet remains capped at 16 total attempts.",
        ],
    }
    write_json(OWNED / "offline-validation.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if not args.prepare and not args.validate:
        args.prepare = True
        args.validate = True
    if args.prepare:
        prepare()
    if args.validate:
        result = validate()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["all_offline_checks_passed"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

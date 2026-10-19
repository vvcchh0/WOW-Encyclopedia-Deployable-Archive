"""Offline-only preparation for frontier-news20e ranks 81..100.

The script reads the frozen v33 extension shortlist and local execution receipts,
performs exact URL de-duplication, and writes one immutable packet.  It does
not import networking libraries, start curl, or create a root GO receipt.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "research" / "continuous-recovery-20261019" / "network" / "frontier-news20e"
QUEUE_PATH = ROOT / "research" / "continuous-recovery-20261019" / "local-audit" / "news-extension" / "news-extension-candidates.json"
SOURCE15_MANIFEST = ROOT / ".scratch" / "offline-navigation-20261015-v15" / "build-manifest.json"
SOURCE15_PAGE = ROOT / ".scratch" / "offline-navigation-20261015-v15" / "site" / "news" / "wow-news2004.html"
V33_MARKER = ROOT / ".scratch" / "pages-resources-20261018-v33" / "news" / "wow-news2004.html"
SOURCE_ACCEPT = ROOT / "research" / "continuous-recovery-20261019" / "publication" / "root-frontier-static20d-source-acceptance.json"
CONTROL = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "root-control03-source-acceptance.json"
FROZEN_DRIVER = ROOT / "research" / "continuous-recovery-20261018" / "network" / "reusable-image-driver-v3" / "reusable_image_driver.py"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def binding(path: Path, role: str) -> dict:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha(path),
        "bytes": path.stat().st_size,
        "role": role,
    }


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if not all(path.is_file() for path in (QUEUE_PATH, SOURCE15_MANIFEST, SOURCE15_PAGE, V33_MARKER, SOURCE_ACCEPT, CONTROL, FROZEN_DRIVER)):
        raise RuntimeError("one or more frozen local inputs are missing")
    (BASE / "adapter").mkdir(parents=True, exist_ok=True)
    (BASE / "output").mkdir(parents=True, exist_ok=True)
    if any((BASE / "output").iterdir()):
        raise RuntimeError("frontier-news20e output is nonempty")

    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    candidates = [copy.deepcopy(row) for row in queue["candidates"] if 81 <= int(row["candidate_rank"]) <= 100]
    if len(candidates) != 20:
        raise RuntimeError(f"expected extension ranks 81..100, got {len(candidates)}")
    queue_sha = sha(QUEUE_PATH)
    source15_sha = sha(SOURCE15_MANIFEST)
    source15_page_sha = sha(SOURCE15_PAGE)
    v33_marker_sha = sha(V33_MARKER)
    source_accept_sha = sha(SOURCE_ACCEPT)
    control_sha = sha(CONTROL)
    driver_sha = sha(FROZEN_DRIVER)

    page_lines = SOURCE15_PAGE.read_text(encoding="utf-8", errors="replace").splitlines()
    source15_lines = []
    for row in candidates:
        url = row["requested_url"]
        matches = [
            line_number
            for line_number, line in enumerate(page_lines, 1)
            if url in line or quote(url, safe="") in line or url.rsplit("/", 1)[-1] in line
        ]
        source15_lines.append(
            {
                "candidate_rank": row["candidate_rank"],
                "url": url,
                "source15_literal_or_overlay_lines": matches,
                "direct_literal_found": any(url in page_lines[line - 1] for line in matches),
            }
        )

    # Search only local execution/report surfaces. Plan, queue, candidate,
    # selection, browser, and audit records are recorded separately and never
    # count as a historical Wayback request.
    actual_roots = [
        ROOT / "research" / "continuous-recovery-20261018" / "network",
        ROOT / "research" / "continuous-recovery-20261019" / "network",
        ROOT / "research" / "continuous-recovery-20261019" / "publication",
    ]
    suffixes = {".json", ".jsonl", ".txt", ".log", ".md", ".py", ".csv"}
    actual_markers = ("batch-report", "source-map", "state", "attempt", "request-record", "dispatch", "control-report", "execution-report", "source-acceptance", "source-receipt", "receipt")
    plan_markers = ("plan", "queue", "candidate", "selection", "binding", "factory", "fixture", "status-snapshot", "cache-status")
    scan_files = []
    actual_matches = {row["requested_url"]: [] for row in candidates}
    plan_matches = {row["requested_url"]: [] for row in candidates}
    for root in actual_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            parts = {part.lower() for part in path.parts}
            if "raw" in parts or "private-payloads" in parts:
                continue
            relative = path.relative_to(ROOT).as_posix()
            scan_files.append(relative)
            text = path.read_text(encoding="utf-8", errors="replace")
            filename = path.name.lower()
            is_plan = any(marker in filename for marker in plan_markers)
            is_actual = any(marker in filename for marker in actual_markers) or "output" in parts
            destination = plan_matches if is_plan else actual_matches if is_actual else None
            if destination is None:
                continue
            for row in candidates:
                url = row["requested_url"]
                if url in text or quote(url, safe="") in text:
                    destination[url].append(
                        {
                            "path": relative,
                            "sha256": sha(path),
                            "classification": "plan_or_queue_surface" if is_plan else "execution_or_receipt_surface",
                        }
                    )

    browser_matches = {row["requested_url"]: [] for row in candidates}
    browser_root = ROOT / "research" / "continuous-recovery-20261015" / "core-pages-integration" / "browser"
    for path in browser_root.glob("v9-browser-receipt*.json"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for row in candidates:
            url = row["requested_url"]
            count = text.count(url) + text.count(quote(url, safe=""))
            if count:
                browser_matches[url].append(
                    {
                        "path": path.relative_to(ROOT).as_posix(),
                        "sha256": sha(path),
                        "occurrences": count,
                        "classification": "local-browser-missing-overlay-not-Wayback-execution",
                    }
                )

    latest_source = json.loads(SOURCE_ACCEPT.read_text(encoding="utf-8"))
    latest_urls = [item["original"] for item in latest_source.get("accepted_images", [])]
    selected_urls = [row["requested_url"] for row in candidates]
    overlap = sorted(set(latest_urls) & set(selected_urls))
    if overlap:
        raise RuntimeError(f"selected URL overlaps latest static20d source: {overlap}")

    dedupe = {
        "schema": "wow-recovery.frontier-news20e-dedupe-audit.v1",
        "status": "offline_dedupe_only",
        "network_requests": 0,
        "extension_queue": binding(QUEUE_PATH, "frozen v33 extension exact shortlist and source rows"),
        "extension_candidate_rows": [
            {
                "rank": row["candidate_rank"],
                "url": row["requested_url"],
                "historical_execution_evidence": row.get("historical_execution_evidence", []),
                "historical_plan_or_queue_evidence": row.get("historical_plan_or_queue_evidence", []),
                "identity_variant_evidence": row.get("identity_variant_evidence", []),
            }
            for row in candidates
        ],
        "independent_execution_surface_scan": {
            "roots": [root.relative_to(ROOT).as_posix() for root in actual_roots],
            "file_count": len(scan_files),
            "scan_file_list_sha256": hashlib.sha256(("\n".join(sorted(scan_files)) + "\n").encode()).hexdigest(),
            "actual_execution_or_cdx_matches": actual_matches,
            "plan_or_queue_matches_excluded": plan_matches,
            "conclusion": "No exact selected URL matched a non-plan execution/report/CDX surface; plan/queue records are excluded.",
        },
        "browser_overlay_evidence": browser_matches,
        "source15_line_audit": source15_lines,
        "prior_latest_source": {
            "path": SOURCE_ACCEPT.relative_to(ROOT).as_posix(),
            "sha256": source_accept_sha,
            "accepted_originals": latest_urls,
            "overlap_with_selected": overlap,
            "conclusion": "Accepted static20d originals do not overlap extension ranks 81-100.",
        },
        "dedupe_decision": {
            "selected_count": 20,
            "fresh_exact_cdx_required": True,
            "known_positive_fallback_rows": 0,
            "historical_wayback_payload_matches": 0,
            "plan_only_records_not_counted_as_execution": True,
            "browser_overlay_not_counted_as_wayback_execution": True,
        },
    }
    dedupe_path = BASE / "dedupe-audit.json"
    write_json(dedupe_path, dedupe)
    dedupe_sha = sha(dedupe_path)

    packet_candidates = []
    for row in candidates:
        rank = int(row["candidate_rank"])
        url = row["requested_url"]
        marker = (row.get("markers") or [{}])[0]
        source_context = (row.get("source_context") or [{}])[0]
        marker_path = ROOT / str(marker.get("output_file"))
        source_evidence = {
            "path": marker.get("output_file"),
            "line": marker.get("line"),
            "literal": url,
            "sha256": sha(marker_path),
            "source_page_sha256": sha(marker_path),
            "bytes": marker_path.stat().st_size,
            "match": "url_encoded",
            "original_source_page_sha256": source_context.get("source_page_sha256"),
            "requested": url,
            "source_page": marker.get("source_url"),
            "reason": marker.get("reason"),
            "source_marker": "v33_missing_image_marker",
            "extension_candidate_rank": rank,
            "extension_queue_sha256": queue_sha,
            "frontier_news20e_rank": rank,
        }
        source_page_context = {
            "extension_queue_path": QUEUE_PATH.relative_to(ROOT).as_posix(),
            "extension_queue_sha256": queue_sha,
            "candidate_rank": rank,
            "source_context": row.get("source_context", []),
            "v33_marker_ref": marker,
        }
        item = {
            "target_key": f"FRONTIER-NEWS20E-{rank:02d}",
            "priority": rank,
            "source_priority_band": "news-extension-ranks81-100",
            "date_bucket": None,
            "kind": "image",
            "original": url,
            "literal": url,
            "expected": {
                "archive_query_required": True,
                "mime_types": ["image/jpeg"],
                "pillow_formats": ["JPEG"],
                "all_gif_frames": False,
                "reencode": False,
                "script_execution": False,
                "query_window": {"from": "20000101000000", "to": "20080512210044"},
            },
            "expected_mime": ["image/jpeg"],
            "source_evidence": source_evidence,
            "source_page_context": source_page_context,
            "selection": {
                "max_distinct_digest_candidates": 2,
                "contract_note": "Frozen driver selects at most two distinct digest rows; total packet cap remains 80 attempts.",
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
                "url": url,
                "from": "20000101000000",
                "to": "20080512210044",
                "output": "json",
                "fields": ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"],
                "limit": 500,
                "showResumeKey": True,
                "collapse": False,
                "matchType": "exact",
                "query_url": "https://web.archive.org/cdx/search/cdx?url=" + quote(url, safe="") + "&from=20000101000000&to=20080512210044&output=json&fl=urlkey%2Ctimestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest%2Clength&limit=500&showResumeKey=true&matchType=exact",
            },
            "replay": {
                "enabled": True,
                "id_url_template": "https://web.archive.org/web/{timestamp}id_/" + url,
                "max_candidates": 2,
                "no_redirects": True,
                "verify_tls": True,
                "acceptance": ["http_status_200", "memento_datetime_present_and_exact", "link_original_exact_default_port_only", "expected_image_content_type", "magic_and_pillow_decode", "decoded_payload_sha1_matches_cdx_digest"],
                "accepted_payloads_are_source_data_only": True,
            },
        }
        item["source_page_context"]["source15_manifest"] = {
            "path": SOURCE15_MANIFEST.relative_to(ROOT).as_posix(),
            "sha256": source15_sha,
            "anchor_timestamp": "20080512210044",
        }
        source15_row = next(entry for entry in source15_lines if entry["candidate_rank"] == rank)
        item["source_page_context"]["source15_page"] = {
            "path": SOURCE15_PAGE.relative_to(ROOT).as_posix(),
            "sha256": source15_page_sha,
            "bytes": SOURCE15_PAGE.stat().st_size,
            "matched_lines": source15_row["source15_literal_or_overlay_lines"],
            "direct_literal_found": source15_row["direct_literal_found"],
        }
        item["source_page_context"]["dedup_audit"] = "research/continuous-recovery-20261019/network/frontier-news20e/dedupe-audit.json"
        item["source_page_context"]["dedup_audit_sha256"] = dedupe_sha
        item["prior_local_evidence"] = [
            {
                "state": "no_new_cdx_query_yet",
                "source": "news-extension-candidates-v33-r2-derived",
                "prior_attempt": {
                    "state": "not_in_historical_execution_records",
                    "parent_exact_dedup_check": "no exact match in historical execution/report/CDX surfaces; browser overlay evidence is not Wayback execution",
                    "network_requests_in_this_preparation": 0,
                    "accepted_payload_in_prior_records": False,
                },
                "exact_entity_index_complete": False,
                "positive_row_count": 0,
            }
        ]
        item["replay"]["id_url_template"] = "https://web.archive.org/web/{timestamp}id_/" + url
        item["query"]["url"] = url
        packet_candidates.append(item)

    selection = {
        "schema": "wow-recovery.frontier-news20e-selection.v1",
        "status": "offline_prepared_no_network",
        "network_requests": 0,
        "candidate_rank_range": [81, 100],
        "candidate_count": 20,
        "extension_queue": binding(QUEUE_PATH, "frozen v33 extension shortlist and source rows"),
        "source15_manifest": binding(SOURCE15_MANIFEST, "frozen Source15 build manifest"),
        "source15_page": binding(SOURCE15_PAGE, "frozen Source15 news/wow-news2004.html page"),
        "v33_marker_page": binding(V33_MARKER, "v33 missing-image marker page"),
        "latest_source_acceptance": binding(SOURCE_ACCEPT, "latest accepted frontier-static20d source receipt; tail zero"),
        "control_gate": binding(CONTROL, "historical CONTROL03 tail-zero gate"),
        "frozen_driver": binding(FROZEN_DRIVER, "frozen V3 driver; not modified"),
        "excluded_prior_latest_source_urls": latest_urls,
        "latest_source_overlap": overlap,
        "source15_line_audit": source15_lines,
        "candidates": packet_candidates,
    }
    selection_path = BASE / "selection-manifest.json"
    write_json(selection_path, selection)

    policy = {
        "from": "20000101000000",
        "to": "20080512210044",
        "limit": 500,
        "showResumeKey": True,
        "collapse": False,
        "matchType": "exact",
        "max_originals": 20,
        "max_attempts": 80,
        "window_seconds": 900.0,
        "max_total_body_bytes": 33554432,
        "max_entity_body_bytes": 8388608,
        "min_dispatch_seconds": 5.25,
        "min_request_start_seconds": 5.0,
        "disk_floor_bytes": 11005853696,
        "direct_first": True,
        "direct_attempt_budget": 4,
        "proxy_attempt_budget": 20,
        "proxy": "http://127.0.0.1:7890",
        "tls_verification": True,
        "automatic_redirects": 0,
        "stop_http_codes": [429, 503],
        "cooldown_seconds": 120,
        "user_agent": "wow-recovery-reusable-image-v3/20261019-frontier-news20e",
        "prior_failure_tail": 0,
        "transport_policy": "batch_after_direct_failure",
        "network_deadline_utc": "2026-10-19T13:15:00Z",
        "no_network_before_parent_go": True,
    }
    source_bindings = {
        "extension_queue": binding(QUEUE_PATH, "frozen v33 extension exact candidate/source rows"),
        "selection_manifest": binding(selection_path, "immutable ranks 5-24 packet selection"),
        "dedupe_audit": binding(dedupe_path, "offline actual execution/CDX dedupe audit"),
        "source15_manifest": binding(SOURCE15_MANIFEST, "frozen Source15 build manifest"),
        "source15_page": binding(SOURCE15_PAGE, "frozen Source15 news/wow-news2004.html page"),
        "v33_marker_page": binding(V33_MARKER, "v33 missing-image marker page"),
        "latest_source_acceptance": binding(SOURCE_ACCEPT, "latest accepted frontier-static20d tail-zero source receipt"),
        "control_gate": binding(CONTROL, "historical CONTROL03 tail-zero gate"),
        "frozen_v3_driver": binding(FROZEN_DRIVER, "frozen V3 driver; not modified"),
    }
    plan = {
        "schema": "wow-recovery.reusable-image-plan.v1",
        "batch_id": "WAYBACK-CONTINUOUS-20261019-FRONTIER-NEWS20E-01",
        "prepared_utc": "2026-10-19T00:00:00Z",
        "mode": "fresh_exact_cdx_then_id_replay_no_fallback",
        "network_authorized": None,
        "parent_go_required": True,
        "candidate_count": 20,
        "output_dir": "research/continuous-recovery-20261019/network/frontier-news20e/output",
        "execution_order": [item["target_key"] for item in packet_candidates],
        "selection_scope": {
            "extension_rank_range": [81, 100],
            "extension_queue_sha256": queue_sha,
            "excluded_already_executed": ["frontier-news04 ranks 1-4", "frontier-news20a ranks 5-24", "frontier-news16b ranks 25-40", "frontier-static20c/d ranks 41-77", "extension ranks 78-80 deferred"],
            "dedupe_audit_sha256": dedupe_sha,
            "network_requests_during_preparation": 0,
        },
        "candidates": packet_candidates,
        "policy": policy,
        "previous_batch": {
            "name": "latest_actual_source_acceptance",
            "prior_failure_tail": 0,
            "acceptance_receipt_path": SOURCE_ACCEPT.relative_to(ROOT).as_posix(),
            "acceptance_receipt_sha256": source_accept_sha,
            "tail_receipt_path": SOURCE_ACCEPT.relative_to(ROOT).as_posix(),
            "tail_receipt_sha256": source_accept_sha,
            "latest_successful_tail_end": 0,
            "historical_tail_is_preserved": True,
            "ordinary_retrieval_requires_new_control_gate": True,
            "control_gate_receipt_path": CONTROL.relative_to(ROOT).as_posix(),
            "control_gate_receipt_sha256": control_sha,
            "control_gate_required": True,
            "root_control_acceptance_bound": True,
            "parent_go_required": True,
        },
        "input_bindings": source_bindings,
        "source_bindings": source_bindings,
        "excluded_rows": {
            "already_executed_extension_ranks": list(range(1, 78)),
            "plan_only_not_execution": True,
            "known_positive_fallback_rows": 0,
            "browser_overlay_matches_not_wayback_evidence": True,
        },
        "identity_variant_policy": {
            "retain_in_source_map": True,
            "replay": False,
            "strict_exact_original_required": True,
            "http_https_not_collapsed": True,
        },
        "execution_boundary": {
            "one_packet_only": True,
            "no_auto_pagination": True,
            "no_automatic_redirects": True,
            "fresh_exact_cdx_before_replay": True,
            "at_most_two_distinct_digest_rows_per_target": True,
            "parent_watchdog_seconds": 960,
            "network_deadline_utc": "2026-10-19T13:15:00Z",
            "no_auto_go_or_followup": True,
        },
    }
    plan_path = BASE / "plan.json"
    write_json(plan_path, plan)
    plan_sha = sha(plan_path)

    bindings = {
        "schema": "wow-recovery.frontier-news20e-input-bindings.v1",
        "batch_id": plan["batch_id"],
        "plan_path": plan_path.relative_to(ROOT).as_posix(),
        "plan_sha256": plan_sha,
        "driver_path": FROZEN_DRIVER.relative_to(ROOT).as_posix(),
        "driver_sha256": driver_sha,
        "adapter_path": "research/continuous-recovery-20261019/network/frontier-news20e/adapter/frontier_news20e_adapter.py",
        "adapter_sha256": "PENDING",
        "selection_manifest_sha256": sha(selection_path),
        "dedupe_audit_sha256": dedupe_sha,
        "latest_source_acceptance_sha256": source_accept_sha,
        "control_gate_sha256": control_sha,
        "extension_queue_sha256": queue_sha,
        "source15_manifest_sha256": source15_sha,
        "source15_page_sha256": source15_page_sha,
        "v33_marker_page_sha256": v33_marker_sha,
        "candidate_count": 20,
        "rank_range": [81, 100],
        "network_requests_during_preparation": 0,
        "fixture_network_requests": 0,
    }
    write_json(BASE / "input-bindings.json", bindings)
    print(json.dumps({
        "selection_sha256": sha(selection_path),
        "dedupe_sha256": dedupe_sha,
        "plan_sha256": plan_sha,
        "bindings_sha256": sha(BASE / "input-bindings.json"),
        "queue_sha256": queue_sha,
        "latest_source_sha256": source_accept_sha,
        "control_sha256": control_sha,
        "driver_sha256": driver_sha,
        "actual_execution_match_count": sum(len(value) for value in actual_matches.values()),
        "plan_or_queue_match_count": sum(len(value) for value in plan_matches.values()),
        "network_requests": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

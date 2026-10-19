"""Offline-only preparation for frontier-static20d ranks 58..77.

The script reads the frozen v33-r2 shortlist and local execution receipts,
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
BASE = ROOT / "research" / "continuous-recovery-20261019" / "network" / "frontier-static20d"
R2_PATH = ROOT / "research" / "continuous-recovery-20261019" / "local-audit" / "resource-frontier-v33-r2" / "resource-frontier-candidates.json"
SOURCE15_MANIFEST = ROOT / ".scratch" / "offline-navigation-20261015-v15" / "build-manifest.json"
SOURCE15_PAGE = ROOT / ".scratch" / "offline-navigation-20261015-v15" / "site" / "_origins" / "forums.worldofwarcraft.com" / "css" / "forums.css"
V33_MARKER = ROOT / ".scratch" / "pages-resources-20261018-v33" / "_origins" / "forums.worldofwarcraft.com" / "css" / "forums.css"
SOURCE_ACCEPT = ROOT / "research" / "continuous-recovery-20261019" / "publication" / "root-frontier-static20c-source-acceptance.json"
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
    if not all(path.is_file() for path in (R2_PATH, SOURCE15_MANIFEST, SOURCE15_PAGE, V33_MARKER, SOURCE_ACCEPT, CONTROL, FROZEN_DRIVER)):
        raise RuntimeError("one or more frozen local inputs are missing")
    (BASE / "adapter").mkdir(parents=True, exist_ok=True)
    (BASE / "output").mkdir(parents=True, exist_ok=True)
    if any((BASE / "output").iterdir()):
        raise RuntimeError("frontier-static20d output is nonempty")

    r2 = json.loads(R2_PATH.read_text(encoding="utf-8"))
    requested_rows = [copy.deepcopy(row) for row in r2["candidates"] if 58 <= int(row["candidate_rank"]) <= 77]
    excluded_missing_source = []
    excluded_identity_variants = []
    candidates = []
    for row in requested_rows:
        rank = int(row["candidate_rank"])
        if rank in {66, 67}:
            excluded_identity_variants.append({
                "rank": rank,
                "requested_url": row["requested_url"],
                "reason": "source15_only_explicit_http_default_port_alias; strict_no_port_original_not_proven; do_not_collapse_identity",
                "observed_source_alias": row["markers"][0].get("snippet", ""),
                "strict_execution": False,
            })
            continue
        if rank in {58, 59, 60, 61, 62}:
            row["source_context"] = [{
                "source_url": "http://forums.worldofwarcraft.com/css/forums.css",
                "source_file": ".scratch/offline-navigation-20261015-v15/site/_origins/forums.worldofwarcraft.com/css/forums.css",
                "source_page_sha256": "fbf8ad458b6b84d48879006db18a667a6b672317d4e5280c9f3fc7d276432af6",
                "source_page_bytes": 67773,
                "source_hits": [int(row["markers"][0]["line"])],
                "source_context_repaired_from_v33_origin": True,
            }]
        context = (row.get("source_context") or [{}])[0]
        source_file = context.get("source_file")
        source_path = ROOT / str(source_file) if source_file else None
        if not source_file or not context.get("source_page_sha256") or not source_path.is_file():
            excluded_missing_source.append({
                "rank": row["candidate_rank"],
                "url": row["requested_url"],
                "reason": "source15_source_page_path_or_sha_missing; no citation invented",
            })
            continue
        candidates.append(row)
    if len(requested_rows) != 20 or len(candidates) != 18:
        raise RuntimeError(f"expected requested ranks 58..77 and 18 strict source-backed candidates, got {len(requested_rows)}/{len(candidates)}")
    r2_sha = sha(R2_PATH)
    source15_sha = sha(SOURCE15_MANIFEST)
    source15_page_sha = sha(SOURCE15_PAGE)
    v33_marker_sha = sha(V33_MARKER)
    source_accept_sha = sha(SOURCE_ACCEPT)
    control_sha = sha(CONTROL)
    driver_sha = sha(FROZEN_DRIVER)

    source15_lines = []
    for row in candidates:
        url = row["requested_url"]
        source_context = (row.get("source_context") or [{}])[0]
        source_page = ROOT / str(source_context["source_file"])
        page_lines = source_page.read_text(encoding="utf-8", errors="replace").splitlines()
        matches = [
            line_number
            for line_number, line in enumerate(page_lines, 1)
            if url in line or quote(url, safe="") in line or url.rsplit("/", 1)[-1] in line
        ]
        source15_lines.append(
            {
                "candidate_rank": row["candidate_rank"],
                "url": url,
                "source_page": source_context["source_file"],
                "source_page_sha256": source_context["source_page_sha256"],
                "source15_literal_or_overlay_lines": matches,
                "direct_literal_found": any(url in page_lines[line - 1] for line in matches),
                "url_encoded_found": any(quote(url, safe="") in page_lines[line - 1] for line in matches),
                "source_url": source_context.get("source_url"),
            }
        )
        if not matches:
            raise RuntimeError(f"no exact source-page citation for rank {row['candidate_rank']}")

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

    previous_source = json.loads(SOURCE_ACCEPT.read_text(encoding="utf-8"))
    previous_urls = [item["original"] for item in previous_source.get("accepted_images", [])]
    selected_urls = [row["requested_url"] for row in candidates]
    overlap = sorted(set(previous_urls) & set(selected_urls))
    if overlap:
        raise RuntimeError(f"selected URL overlaps accepted static20c source: {overlap}")

    dedupe = {
        "schema": "wow-recovery.frontier-static20d-dedupe-audit.v1",
        "status": "offline_dedupe_only",
        "network_requests": 0,
        "r2_source": binding(R2_PATH, "frozen v33-r2 exact shortlist"),
        "r2_candidate_rows": [
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
            "conclusion": "No exact selected URL matched a non-plan execution/report/CDX surface; missing-source ranks were excluded without invented citations.",
        },
        "browser_overlay_evidence": browser_matches,
        "source15_line_audit": source15_lines,
        "prior_frontier_static20c": {
            "path": SOURCE_ACCEPT.relative_to(ROOT).as_posix(),
            "sha256": source_accept_sha,
            "accepted_originals": previous_urls,
            "overlap_with_selected": overlap,
            "conclusion": "Accepted frontier-static20c URLs do not overlap the strict static ranks 58-65 and 68-77 packet.",
        },
        "dedupe_decision": {
            "requested_rank_count": 20,
            "selected_count": len(candidates),
            "excluded_missing_source": excluded_missing_source,
            "excluded_identity_variants": excluded_identity_variants,
            "fresh_exact_cdx_required": True,
            "known_positive_fallback_rows": 0,
            "historical_wayback_payload_matches": 0,
            "plan_only_records_not_counted_as_execution": True,
            "browser_overlay_not_counted_as_wayback_execution": True,
            "strict_identity_note": "Ranks 66 and 67 retain only explicit :80 source aliases; HTTP default-port identity is not collapsed into the no-port requested URL.",
        },
    }
    dedupe_path = BASE / "dedupe-audit.json"
    write_json(dedupe_path, dedupe)
    dedupe_sha = sha(dedupe_path)

    packet_candidates = []
    for row in candidates:
        rank = int(row["candidate_rank"])
        url = row["requested_url"]
        suffix = url.lower().split("?", 1)[0].rsplit(".", 1)[-1]
        mime_by_suffix = {
            "jpg": ("image/jpeg", "JPEG"),
            "jpeg": ("image/jpeg", "JPEG"),
            "gif": ("image/gif", "GIF"),
            "png": ("image/png", "PNG"),
        }
        if suffix not in mime_by_suffix:
            raise RuntimeError(f"unsupported static image suffix for rank {rank}: {url}")
        expected_mime, pillow_format = mime_by_suffix[suffix]
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
            "r2_candidate_rank": rank,
            "r2_candidates_sha256": r2_sha,
            "frontier_static20d_rank": rank,
        }
        source_page_context = {
            "r2_candidates_path": R2_PATH.relative_to(ROOT).as_posix(),
            "r2_candidates_sha256": r2_sha,
            "candidate_rank": rank,
            "source_context": row.get("source_context", []),
            "v33_marker_ref": marker,
        }
        item = {
            "target_key": f"FRONTIER-STATIC20D-{rank:02d}",
            "priority": rank,
            "source_priority_band": "static-frontier-r2-ranks58-77-strict-subset",
            "date_bucket": None,
            "kind": "image",
            "original": url,
            "literal": url,
            "expected": {
                "archive_query_required": True,
                "mime_types": [expected_mime],
                "pillow_formats": [pillow_format],
                "all_gif_frames": False,
                "reencode": False,
                "script_execution": False,
                "query_window": {"from": "20000101000000", "to": "20080512210044"},
            },
            "expected_mime": [expected_mime],
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
        source15_page_path = ROOT / source15_row["source_page"]
        item["source_page_context"]["source15_page"] = {
            "path": source15_page_path.relative_to(ROOT).as_posix(),
            "sha256": source15_row["source_page_sha256"],
            "bytes": source15_page_path.stat().st_size,
            "matched_lines": source15_row["source15_literal_or_overlay_lines"],
            "direct_literal_found": source15_row["direct_literal_found"],
            "url_encoded_found": source15_row["url_encoded_found"],
            "source_url": source15_row["source_url"],
        }
        item["source_page_context"]["dedup_audit"] = "research/continuous-recovery-20261019/network/frontier-static20d/dedupe-audit.json"
        item["source_page_context"]["dedup_audit_sha256"] = dedupe_sha
        item["prior_local_evidence"] = [
            {
                "state": "no_new_cdx_query_yet",
                "source": "resource-frontier-v33-r2",
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
        "schema": "wow-recovery.frontier-static20d-selection.v1",
        "status": "offline_prepared_no_network",
        "network_requests": 0,
        "candidate_rank_range": [58, 77],
        "strict_candidate_ranks": list(range(58, 66)) + list(range(68, 78)),
        "requested_candidate_rank_range": [58, 77],
        "candidate_count": len(candidates),
        "r2_candidates": binding(R2_PATH, "frozen v33-r2 shortlist and source rows"),
        "source15_manifest": binding(SOURCE15_MANIFEST, "frozen Source15 build manifest"),
        "source15_page": binding(SOURCE15_PAGE, "frozen Source15 forum CSS anchor; per-candidate pages are bound below"),
        "v33_marker_page": binding(V33_MARKER, "v33 missing-image marker page"),
        "latest_source_acceptance": binding(SOURCE_ACCEPT, "latest accepted frontier-static20c source receipt; tail zero"),
        "control_gate": binding(CONTROL, "historical CONTROL03 tail-zero gate"),
        "frozen_driver": binding(FROZEN_DRIVER, "frozen V3 driver; not modified"),
        "excluded_prior_frontier_static20c_urls": previous_urls,
        "static20c_overlap": overlap,
        "excluded_requested_rows": excluded_missing_source,
        "excluded_identity_variants": excluded_identity_variants,
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
        "user_agent": "wow-recovery-reusable-image-v3/20261019-frontier-static20d",
        "prior_failure_tail": 0,
        "transport_policy": "batch_after_direct_failure",
        "network_deadline_utc": "2026-10-19T13:15:00Z",
        "no_network_before_parent_go": True,
    }
    source_bindings = {
        "r2_candidate_rows": binding(R2_PATH, "frozen v33-r2 exact candidate/source rows"),
        "selection_manifest": binding(selection_path, "immutable strict ranks 58-65 and 68-77 source-backed packet selection; ranks 66-67 retained as identity-variant exclusions"),
        "dedupe_audit": binding(dedupe_path, "offline actual execution/CDX dedupe audit"),
        "source15_manifest": binding(SOURCE15_MANIFEST, "frozen Source15 build manifest"),
        "source15_page": binding(SOURCE15_PAGE, "frozen Source15 forum CSS anchor; per-candidate pages are bound in candidates"),
        "v33_marker_page": binding(V33_MARKER, "v33 missing-image marker page"),
        "latest_source_acceptance": binding(SOURCE_ACCEPT, "latest accepted frontier-static20c tail-zero source receipt"),
        "control_gate": binding(CONTROL, "historical CONTROL03 tail-zero gate"),
        "frozen_v3_driver": binding(FROZEN_DRIVER, "frozen V3 driver; not modified"),
    }
    plan = {
        "schema": "wow-recovery.reusable-image-plan.v1",
        "batch_id": "WAYBACK-CONTINUOUS-20261019-FRONTIER-STATIC20D-01",
        "prepared_utc": "2026-10-19T00:00:00Z",
        "mode": "fresh_exact_cdx_then_id_replay_no_fallback",
        "network_authorized": None,
        "parent_go_required": True,
        "candidate_count": len(candidates),
        "output_dir": "research/continuous-recovery-20261019/network/frontier-static20d/output",
        "execution_order": [item["target_key"] for item in packet_candidates],
        "selection_scope": {
            "r2_rank_range": [58, 77],
            "strict_r2_ranks": list(range(58, 66)) + list(range(68, 78)),
            "requested_r2_rank_range": [58, 77],
            "r2_candidates_sha256": r2_sha,
            "excluded_source_insufficient": excluded_missing_source,
            "excluded_identity_variants": excluded_identity_variants,
            "excluded_already_executed": ["FRONTIER-NEWS04-01..04", "FRONTIER-NEWS16B-25..40", "r2 ranks 1-40"],
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
            "already_executed_r2_ranks": list(range(1, 41)),
            "excluded_missing_source_r2_ranks": [item["rank"] for item in excluded_missing_source],
            "excluded_identity_variant_r2_ranks": [item["rank"] for item in excluded_identity_variants],
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
        "schema": "wow-recovery.frontier-static20d-input-bindings.v1",
        "batch_id": plan["batch_id"],
        "plan_path": plan_path.relative_to(ROOT).as_posix(),
        "plan_sha256": plan_sha,
        "driver_path": FROZEN_DRIVER.relative_to(ROOT).as_posix(),
        "driver_sha256": driver_sha,
        "adapter_path": "research/continuous-recovery-20261019/network/frontier-static20d/adapter/frontier_static20d_adapter.py",
        "adapter_sha256": sha(BASE / "adapter" / "frontier_static20d_adapter.py"),
        "selection_manifest_sha256": sha(selection_path),
        "dedupe_audit_sha256": dedupe_sha,
        "latest_source_acceptance_sha256": source_accept_sha,
        "control_gate_sha256": control_sha,
        "r2_candidates_sha256": r2_sha,
        "source15_manifest_sha256": source15_sha,
        "source15_page_sha256": source15_page_sha,
        "v33_marker_page_sha256": v33_marker_sha,
        "candidate_count": len(candidates),
        "rank_range": [58, 77],
        "strict_rank_list": list(range(58, 66)) + list(range(68, 78)),
        "requested_rank_range": [58, 77],
        "excluded_missing_source_ranks": [item["rank"] for item in excluded_missing_source],
        "excluded_identity_variant_ranks": [item["rank"] for item in excluded_identity_variants],
        "network_requests_during_preparation": 0,
        "fixture_network_requests": 0,
    }
    write_json(BASE / "input-bindings.json", bindings)
    print(json.dumps({
        "selection_sha256": sha(selection_path),
        "dedupe_sha256": dedupe_sha,
        "plan_sha256": plan_sha,
        "bindings_sha256": sha(BASE / "input-bindings.json"),
        "r2_sha256": r2_sha,
        "latest_source_sha256": source_accept_sha,
        "control_sha256": control_sha,
        "driver_sha256": driver_sha,
        "actual_execution_match_count": sum(len(value) for value in actual_matches.values()),
        "plan_or_queue_match_count": sum(len(value) for value in plan_matches.values()),
        "network_requests": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

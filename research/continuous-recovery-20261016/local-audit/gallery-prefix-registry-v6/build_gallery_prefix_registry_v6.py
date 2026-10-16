from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()
BASE = ROOT / "research" / "continuous-recovery-20261016"
V5_REL = "research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v5/gallery-prefix-registry-v5.json"
P5_ACCEPT_REL = "research/continuous-recovery-20261016/publication/root-gallery-prefix05-acceptance.json"
P5_DIR_REL = "research/continuous-recovery-20261016/network/gallery-prefix05"
P5_PLAN_REL = f"{P5_DIR_REL}/plan.json"
P5_EXEC_REL = f"{P5_DIR_REL}/execution-plan.json"
P5_REPORT_REL = f"{P5_DIR_REL}/batch-report.json"
P5_MAP_REL = f"{P5_DIR_REL}/source-map.json"
P5_INPUT_REL = f"{P5_DIR_REL}/input-bindings.json"
P5_SUMMARY_REL = f"{P5_DIR_REL}/sanitized-summary.json"
P5_FIXTURE_REL = f"{P5_DIR_REL}/fixture-results.json"
P5_DRIVER_REL = f"{P5_DIR_REL}/gallery_prefix_driver_v5.py"
OUT_DIR_REL = "research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v6"
REGISTRY_REL = f"{OUT_DIR_REL}/gallery-prefix-registry-v6.json"
PUBLIC_REL = f"{OUT_DIR_REL}/gallery-prefix-registry-v6-public-summary.json"
VERIFY_REL = f"{OUT_DIR_REL}/gallery-prefix-registry-v6-verification.json"


def load_rel(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_binding(relative: str, role: str) -> dict:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"missing required input: {relative}")
    return {
        "path": relative.replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
        "role": role,
    }


def write_new(relative: str, value) -> None:
    path = ROOT / relative
    if path.exists():
        raise RuntimeError(f"refusing to overwrite existing v6 output: {relative}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compact_attempt(attempt: dict) -> dict:
    keys = (
        "attempt",
        "rank",
        "label",
        "transport",
        "curl_exit",
        "connect_status",
        "source_status",
        "content_type",
        "body_bytes",
        "body_sha256",
        "transport_error",
        "transport_reason",
        "cdx_json_valid",
        "cdx_parse_error",
        "cdx_record_count",
        "resume_keys",
        "potential_truncation",
        "continuation_followed",
        "phase_boundary",
        "started_utc",
        "finished_utc",
        "raw",
    )
    return {key: copy.deepcopy(attempt[key]) for key in keys if key in attempt}


def main() -> None:
    v5 = load_rel(V5_REL)
    acceptance = load_rel(P5_ACCEPT_REL)
    plan = load_rel(P5_PLAN_REL)
    execution = load_rel(P5_EXEC_REL)
    report = load_rel(P5_REPORT_REL)
    source_map = load_rel(P5_MAP_REL)
    input_bindings = load_rel(P5_INPUT_REL)
    summary = load_rel(P5_SUMMARY_REL)
    fixture = load_rel(P5_FIXTURE_REL)

    if acceptance.get("accepted") is not True:
        raise AssertionError("prefix05 root acceptance is not accepted")
    if report.get("batch_id") != "WAYBACK-GALLERYPREFIX05-20261016":
        raise AssertionError("unexpected prefix05 batch id")
    if source_map.get("batch_id") != report.get("batch_id"):
        raise AssertionError("prefix05 source-map batch mismatch")
    if source_map.get("index_only") is not True:
        raise AssertionError("prefix05 source-map is not index-only")
    if acceptance.get("network_requests") != 14 or acceptance.get("source_responses") != 7:
        raise AssertionError("unexpected prefix05 accepted request/response counts")
    if acceptance.get("index_rows") != 17 or acceptance.get("body_bytes") != 3993:
        raise AssertionError("unexpected prefix05 accepted index/body counts")
    if acceptance.get("image_index_rows") != 2:
        raise AssertionError("unexpected prefix05 image-index count")
    if acceptance.get("payload_replays") != 0 or report.get("payload_replay_count") != 0:
        raise AssertionError("prefix05 contains a payload replay")
    if fixture.get("all_passed") is not True:
        raise AssertionError("prefix05 fixture receipt is not all_passed")

    result_by_label = {item["label"]: item for item in acceptance.get("results", [])}
    report_by_label = {item["label"]: item for item in report.get("candidate_results", [])}
    map_by_label = {item["label"]: item for item in source_map.get("entries", [])}
    plan_by_label = {item["gallery"]: item for item in plan.get("candidates", [])}
    labels = set(result_by_label)
    if labels != set(report_by_label) or labels != set(map_by_label) or labels != set(plan_by_label):
        raise AssertionError("prefix05 label sets differ across acceptance/report/map/plan")
    if len(labels) != 7:
        raise AssertionError(f"expected seven prefix05 labels, got {len(labels)}")
    if execution.get("candidate_count") != 7 or execution.get("candidate_ranks") != list(range(1, 8)):
        raise AssertionError("prefix05 execution candidate set changed")
    query_window = copy.deepcopy(execution.get("query_window"))
    expected_window = {
        "from": "20000101000000",
        "to": "20080512210044",
        "limit": 500,
        "showResumeKey": True,
        "collapse": False,
        "matchType": "prefix",
    }
    if query_window != expected_window:
        raise AssertionError(f"unexpected prefix05 query window: {query_window!r}")

    acceptance_binding = file_binding(P5_ACCEPT_REL, "root accepted prefix05 index-only result")
    plan_binding = file_binding(P5_PLAN_REL, "prefix05 literal query plan")
    execution_binding = file_binding(P5_EXEC_REL, "prefix05 execution window/policy")
    report_binding = file_binding(P5_REPORT_REL, "prefix05 raw batch report")
    map_binding = file_binding(P5_MAP_REL, "prefix05 source-map attempt/result ledger")
    input_binding = file_binding(P5_INPUT_REL, "prefix05 input bindings")
    summary_binding = file_binding(P5_SUMMARY_REL, "prefix05 sanitized summary")
    fixture_binding = file_binding(P5_FIXTURE_REL, "prefix05 offline fixture receipt")
    driver_binding = file_binding(P5_DRIVER_REL, "prefix05 driver source")

    latest_by_label = {}
    for label in sorted(labels, key=lambda name: result_by_label[name].get("rank", 999)):
        result = result_by_label[label]
        report_result = report_by_label[label]
        map_entry = map_by_label[label]
        plan_candidate = plan_by_label[label]
        complete = (
            result.get("valid_index") is True
            and report_result.get("status") == "complete_within_response"
            and map_entry.get("status") == "complete_within_response"
            and not result.get("resume_keys")
            and not report_result.get("potential_truncation")
            and not map_entry.get("potential_truncation")
            and result.get("prefix") == report_result.get("prefix") == map_entry.get("prefix")
            and plan_candidate.get("prefix") == result.get("prefix")
        )
        if not complete:
            raise AssertionError(f"prefix05 result is not a complete index window: {label}")
        candidate_window = copy.deepcopy(plan_candidate.get("query_window") or query_window)
        if candidate_window != query_window:
            raise AssertionError(f"prefix05 per-candidate query window differs: {label}")
        latest_by_label[label] = {
            "kind": "prefix_index_only",
            "batch_id": report["batch_id"],
            "label": label,
            "prefix": result["prefix"],
            "status": "valid_complete_index",
            "window": candidate_window,
            "index_only": True,
            "payload_replay": False,
            "source_responses": 1,
            "index_rows": result.get("index_rows", 0),
            "image_index_rows": result.get("image_index_rows", 0),
            "resume_keys": copy.deepcopy(result.get("resume_keys", [])),
            "potential_truncation": False,
            "complete_prefix_evidence": True,
            "acceptance": copy.deepcopy(acceptance_binding),
            "batch_report": copy.deepcopy(report_binding),
            "plan": copy.deepcopy(plan_binding),
            "execution_plan": copy.deepcopy(execution_binding),
            "source_map": copy.deepcopy(map_binding),
            "input_bindings": copy.deepcopy(input_binding),
            "sanitized_summary": copy.deepcopy(summary_binding),
            "fixture": copy.deepcopy(fixture_binding),
            "acceptance_result": {
                "valid_index": True,
                "index_rows": result.get("index_rows", 0),
                "image_index_rows": result.get("image_index_rows", 0),
                "resume_keys": copy.deepcopy(result.get("resume_keys", [])),
            },
            "report_result": {
                "status": report_result.get("status"),
                "capture_index_count": map_entry.get("capture_index_count"),
                "strict_literal_full_count": map_entry.get("strict_literal_full_count"),
                "strict_literal_thumb_count": map_entry.get("strict_literal_thumb_count"),
                "nested_or_other_count": map_entry.get("nested_or_other_count"),
                "payload_replay_count": map_entry.get("payload_replay_count"),
                "potential_truncation": report_result.get("potential_truncation"),
            },
            "attempts": [compact_attempt(item) for item in report_result.get("attempts", [])],
        }

    rows = copy.deepcopy(v5["coverage_rows"])
    row_by_label = {row["gallery"]: row for row in rows}
    if labels - set(row_by_label):
        raise AssertionError("prefix05 has a gallery absent from v5 registry")
    for label, latest in latest_by_label.items():
        row = row_by_label[label]
        row.setdefault("actual_prefix_windows", []).append(copy.deepcopy(latest))
        row["latest_prefix_record"] = {
            "batch_id": latest["batch_id"],
            "status": latest["status"],
            "complete_prefix_evidence": True,
            "acceptance": copy.deepcopy(latest["acceptance"]),
            "batch_report": copy.deepcopy(latest["batch_report"]),
            "source_map": copy.deepcopy(latest["source_map"]),
        }
        row["coverage_class"] = "reviewed_window_complete"
        row["coverage_status"] = "prefix05_valid_complete_index"
        row["coverage_source_latest"] = "root accepted prefix05 index-only result; no payload replay"
        row["prewindow_gap"] = None

    status_counts = copy.deepcopy(v5["stats"]["entity_audit_status_counts"])
    if status_counts != {"archive_404": 79, "never_requested": 3242, "transport_unknown": 47}:
        raise AssertionError(f"direct entity status counts changed: {status_counts}")
    if sum(status_counts.values()) != 3368:
        raise AssertionError("direct entity status counts do not conserve")
    limited = [row for row in rows if row.get("coverage_class") == "reviewed_window_complete"]
    incomplete = [row for row in rows if row.get("coverage_class") != "reviewed_window_complete"]
    if len(limited) != 50 or incomplete:
        raise AssertionError(f"unexpected v6 coverage partition: {len(limited)} complete / {len(incomplete)} incomplete")

    prefix03 = set(v5["followup_partition"]["prefix03_full_window_excluded"])
    prefix04 = set(v5["followup_partition"]["prefix04_full_window_excluded"])
    if len(prefix03) != 5 or len(prefix04) != 14:
        raise AssertionError("frozen v5 full-window partitions changed")
    early_gap = list(v5["followup_partition"]["early_gap_labels"])
    if len(early_gap) != 24:
        raise AssertionError("frozen v5 early-gap count changed")

    out = copy.deepcopy(v5)
    out["schema"] = "gallery-prefix-registry-v6-local26"
    out["generated_utc"] = datetime.now(timezone.utc).isoformat()
    out["scope"] = "Independent local merge of frozen v5 registry with root-accepted prefix05 index evidence; no network or payload replay."
    out["coverage_rows"] = rows
    out["stats"] = {
        "gallery_count": 50,
        "declared_slots": 1684,
        "expected_direct_entities": 3368,
        "coverage_group_counts": {
            "limited_complete": 50,
            "incomplete_or_unknown": 0,
            "reviewed_window_complete": 50,
            "not_complete_or_unknown": 0,
        },
        "prefix03_complete_groups_preserved": len(prefix03),
        "prefix04_complete_groups_added": len(prefix04),
        "prefix04_unknown_groups_added": 6,
        "prefix05_complete_groups_added": len(labels),
        "prefix05_complete_groups": len(labels),
        "incomplete_groups_after_prefix05": len(incomplete),
        "early_gap_followup_groups": len(early_gap),
        "excluded_from_early_gap_followup_prefix03_full_window": len(prefix03),
        "excluded_from_early_gap_followup_prefix04_full_window": len(prefix04),
        "excluded_from_early_gap_followup_prefix05_full_window": len(labels),
        "full_window_complete_groups": len(prefix03 | prefix04 | labels),
        "entity_audit_status_counts": status_counts,
    }
    out["conservation"] = {
        "groups": len(rows) == 50,
        "slots": sum(row["declared_slots"] for row in rows) == 1684,
        "entities": sum(row["expected_direct_entities"] for row in rows) == 3368,
        "status_entities": sum(status_counts.values()) == 3368,
        "prefix04_partition": len(prefix04) + 6 == 20,
        "prefix05_partition": len(labels) == 7,
        "all_limited_window_complete": len(limited) == 50,
        "full_window_partition": len(prefix03 | prefix04 | labels) == 26,
        "early_gap_partition": len(early_gap) == 24,
    }
    out["followup_partition"] = {
        "incomplete_labels": [],
        "early_gap_labels": early_gap,
        "prefix03_full_window_excluded": sorted(prefix03),
        "prefix04_full_window_excluded": sorted(prefix04),
        "prefix05_full_window_excluded": sorted(labels),
    }
    out["prefix05_binding"] = {
        "acceptance": acceptance_binding,
        "plan": plan_binding,
        "execution_plan": execution_binding,
        "batch_report": report_binding,
        "source_map": map_binding,
        "input_bindings": input_binding,
        "sanitized_summary": summary_binding,
        "fixture": fixture_binding,
        "driver": driver_binding,
        "batch_id": report["batch_id"],
        "network_requests": acceptance["network_requests"],
        "source_responses": acceptance["source_responses"],
        "index_rows": acceptance["index_rows"],
        "body_bytes": acceptance["body_bytes"],
        "image_index_rows": acceptance["image_index_rows"],
        "payload_replays": acceptance["payload_replays"],
        "scope": acceptance.get("scope"),
    }
    out["input_hashes"] = copy.deepcopy(v5.get("input_hashes", {}))
    out["input_hashes"][V5_REL] = file_binding(V5_REL, "frozen v5 source registry")
    out["input_hashes"].update(
        {
            P5_ACCEPT_REL: acceptance_binding,
            P5_PLAN_REL: plan_binding,
            P5_EXEC_REL: execution_binding,
            P5_REPORT_REL: report_binding,
            P5_MAP_REL: map_binding,
            P5_INPUT_REL: input_binding,
            P5_SUMMARY_REL: summary_binding,
            P5_FIXTURE_REL: fixture_binding,
            P5_DRIVER_REL: driver_binding,
        }
    )
    out["notes"] = list(v5.get("notes", [])) + [
        "LOCAL26 appends seven root-accepted prefix05 complete index-only windows; no payload replay or direct entity status was changed.",
        "All 50 groups now have a reviewed limited prefix window; 26 groups have a complete 2000-to-anchor window from prefix03, prefix04, or prefix05, while 24 retain an earlier-window gap.",
        "Prefix05 Amani War Bear image rows are nested/non-dynamic bear-thumb evidence; they are not promoted to ssN entities.",
        "The 79 archive_404, 47 transport_unknown, and 3242 never_requested direct-entity counts remain copied from v5 and are independent of prefix-index coverage.",
    ]
    write_new(REGISTRY_REL, out)
    registry_binding = file_binding(REGISTRY_REL, "new LOCAL26 merged v6 registry")

    public = {
        "schema": "gallery-prefix-registry-v6-public-summary",
        "generated_utc": out["generated_utc"],
        "network_performed": False,
        "git_performed": False,
        "coverage": {
            "groups": 50,
            "declared_slots": 1684,
            "dynamic_entities": 3368,
            "limited_window_complete": 50,
            "full_window_2000_to_anchor": 26,
            "early_window_gap_remaining": 24,
            "prefix05_added": 7,
        },
        "direct_entity_status_counts": status_counts,
        "prefix05_labels": sorted(labels),
        "registry": registry_binding,
        "prefix05_acceptance": acceptance_binding,
        "boundary": "Prefix-index evidence records indexed captures only; it does not recover direct image payloads or alter direct full/thumb status.",
    }
    write_new(PUBLIC_REL, public)
    public_binding = file_binding(PUBLIC_REL, "new LOCAL26 sanitized public summary")

    verification = {
        "schema": "gallery-prefix-registry-v6-verification",
        "generated_utc": out["generated_utc"],
        "network_performed": False,
        "git_performed": False,
        "command": "python.exe -X utf8 research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v6/build_gallery_prefix_registry_v6.py",
        "inputs": {
            "v5_registry": file_binding(V5_REL, "frozen v5 source registry"),
            "prefix05_acceptance": acceptance_binding,
            "prefix05_plan": plan_binding,
            "prefix05_execution_plan": execution_binding,
            "prefix05_report": report_binding,
            "prefix05_source_map": map_binding,
            "prefix05_input_bindings": input_binding,
            "prefix05_sanitized_summary": summary_binding,
            "prefix05_fixture": fixture_binding,
            "prefix05_driver": driver_binding,
        },
        "checks": {
            "gallery_count_50": len(rows) == 50,
            "declared_slots_1684": sum(row["declared_slots"] for row in rows) == 1684,
            "direct_entities_3368": sum(row["expected_direct_entities"] for row in rows) == 3368,
            "all_50_limited_window_complete": len(limited) == 50 and not incomplete,
            "full_window_groups_26": len(prefix03 | prefix04 | labels) == 26,
            "early_gap_groups_24": len(early_gap) == 24,
            "prefix05_complete_groups_7": len(labels) == 7,
            "prefix05_query_window_2000_to_anchor": query_window == expected_window,
            "direct_status_archive_404_79": status_counts["archive_404"] == 79,
            "direct_status_transport_unknown_47": status_counts["transport_unknown"] == 47,
            "direct_status_never_requested_3242": status_counts["never_requested"] == 3242,
            "direct_status_total_3368": sum(status_counts.values()) == 3368,
            "no_payload_replay": acceptance["payload_replays"] == 0,
            "fixture_all_passed": fixture.get("all_passed") is True,
        },
        "outputs": {
            "registry": registry_binding,
            "public_summary": public_binding,
        },
        "notes": [
            "This receipt is a local merge only; it did not issue network requests, replay payloads, or change frozen v5 evidence.",
            "The seven prefix05 result rows are accepted complete index responses, including two non-dynamic image-index rows; none is promoted to a direct ssN payload.",
        ],
    }
    write_new(VERIFY_REL, verification)
    verification_binding = file_binding(VERIFY_REL, "new LOCAL26 v6 verification receipt")
    print(
        json.dumps(
            {
                "registry": registry_binding,
                "public_summary": public_binding,
                "verification": verification_binding,
                "counts": {
                    "groups": len(rows),
                    "slots": sum(row["declared_slots"] for row in rows),
                    "entities": sum(row["expected_direct_entities"] for row in rows),
                    "limited_complete": len(limited),
                    "full_window": len(prefix03 | prefix04 | labels),
                    "early_gap": len(early_gap),
                    "prefix05": len(labels),
                    "direct_status": status_counts,
                },
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

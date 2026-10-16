from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path.cwd()
BASE = ROOT / "research" / "continuous-recovery-20261016"
V4_REL = "research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v4/gallery-prefix-registry-v4.json"
P4_ACCEPT_REL = "research/continuous-recovery-20261016/publication/root-gallery-prefix04-acceptance.json"
P4_DIR_REL = "research/continuous-recovery-20261016/network/gallery-prefix04"
P4_PLAN_REL = f"{P4_DIR_REL}/plan.json"
P4_EXEC_REL = f"{P4_DIR_REL}/execution-plan.json"
P4_REPORT_REL = f"{P4_DIR_REL}/batch-report.json"
P4_MAP_REL = f"{P4_DIR_REL}/source-map.json"
P4_INPUT_REL = f"{P4_DIR_REL}/input-bindings.json"
P4_SUMMARY_REL = f"{P4_DIR_REL}/sanitized-summary.json"
V5_REL = "research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v5/gallery-prefix-registry-v5.json"
PUBLIC_REL = "research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v5/gallery-prefix-registry-v5-public-summary.json"
VERIFY_REL = "research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v5/gallery-prefix-registry-v5-verification.json"
INCOMPLETE_REL = "research/continuous-recovery-20261016/local-audit/gallery-followup-plans/incomplete-prefixes-full-window-v1.json"
EARLY_REL = "research/continuous-recovery-20261016/local-audit/gallery-followup-plans/early-gaps-24-v1.json"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_rel(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_binding(relative: str, role: str) -> dict:
    p = ROOT / relative
    return {"path": relative.replace("\\", "/"), "bytes": p.stat().st_size, "sha256": sha256_path(p), "role": role}


def write_new(relative: str, value) -> None:
    p = ROOT / relative
    if p.exists():
        raise RuntimeError(f"refusing to overwrite existing LOCAL21 output: {relative}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    return {k: copy.deepcopy(attempt[k]) for k in keys if k in attempt}


def compact_window(window: dict) -> dict:
    out = {}
    for key in (
        "kind",
        "evidence_id",
        "batch_id",
        "status",
        "label",
        "prefix",
        "window",
        "direct_entity_rows",
        "status200_image_rows",
        "nested_excluded_rows",
        "prefix_pages",
        "direct_exact_candidates",
        "direct_variant_candidates",
        "image_index_rows",
        "index_rows",
        "source_responses",
        "payload_replays",
        "resume_keys",
        "actual_attempt_numbers",
        "potential_truncation",
        "complete_prefix_evidence",
        "index_only_note",
        "report_quote",
    ):
        if key in window:
            out[key] = copy.deepcopy(window[key])
    if "acceptance" in window:
        out["acceptance"] = copy.deepcopy(window["acceptance"])
    for key in ("batch_report", "source_map", "execution_plan"):
        if key in window:
            out[key] = copy.deepcopy(window[key])
    if "evidence_paths" in window:
        out["evidence_paths"] = copy.deepcopy(window["evidence_paths"])
    if "source_response_attempt" in window:
        sra = window["source_response_attempt"]
        out["source_response_attempt"] = {
            k: copy.deepcopy(sra[k])
            for k in ("transport", "source_status", "body_bytes", "body_sha256", "cdx_record_count", "raw")
            if k in sra
        }
    return out


def subtract_one_second(timestamp: str) -> str:
    dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S") - timedelta(seconds=1)
    return dt.strftime("%Y%m%d%H%M%S")


def absolute_prefix(source_evidence: dict) -> str:
    directory = source_evidence.get("directory_literal") or source_evidence.get("source_directory")
    if not directory:
        raise AssertionError("source evidence has no literal directory")
    if not directory.startswith("/"):
        raise AssertionError(f"source directory is not root-relative: {directory!r}")
    host = source_evidence.get("origin_host") or "www.worldofwarcraft.com"
    scheme = (source_evidence.get("origin_schemes") or ["http"])[0]
    if scheme != "http" or host != "www.worldofwarcraft.com":
        raise AssertionError(f"unexpected gallery origin: {scheme}://{host}")
    return f"http://{host}{directory}"


def source_evidence(row: dict) -> dict:
    # The source evidence is already compact, literal, and SHA-bound in v4.
    return copy.deepcopy(row["source_evidence"])


def compact_prior_attempts(row: dict, map_by_batch_label: dict) -> list[dict]:
    attempts = []
    seen = set()
    for window in row.get("actual_prefix_windows", []):
        batch_id = window.get("batch_id")
        if not batch_id:
            continue
        entry = map_by_batch_label.get((batch_id, row["gallery"]))
        if not entry:
            continue
        for attempt in entry.get("attempts", []):
            key = (batch_id, attempt.get("attempt"))
            if key in seen:
                continue
            seen.add(key)
            item = compact_attempt(attempt)
            item["batch_id"] = batch_id
            attempts.append(item)
    return attempts


def main() -> None:
    v4 = load_rel(V4_REL)
    p4_accept = load_rel(P4_ACCEPT_REL)
    p4_plan = load_rel(P4_PLAN_REL)
    p4_exec = load_rel(P4_EXEC_REL)
    p4_report = load_rel(P4_REPORT_REL)
    p4_map = load_rel(P4_MAP_REL)

    if p4_accept.get("accepted") is not True:
        raise AssertionError("prefix04 root acceptance is not accepted")
    if p4_accept.get("network_requests") != 40:
        raise AssertionError("unexpected prefix04 accepted request count")
    if p4_report.get("batch_id") != "WAYBACK-GALLERYPREFIX04-20261016":
        raise AssertionError("unexpected prefix04 batch id")
    if p4_map.get("batch_id") != p4_report.get("batch_id"):
        raise AssertionError("prefix04 report/source-map batch mismatch")

    p4_results = {x["label"]: x for x in p4_accept.get("results", [])}
    p4_report_results = {x["label"]: x for x in p4_report.get("candidate_results", [])}
    p4_map_entries = {x["label"]: x for x in p4_map.get("entries", [])}
    p4_plan_candidates = {x["gallery"]: x for x in p4_plan.get("candidates", [])}
    if set(p4_results) != set(p4_report_results) or set(p4_results) != set(p4_map_entries):
        raise AssertionError("prefix04 result/report/source-map label sets differ")
    if set(p4_results) != set(p4_plan_candidates):
        raise AssertionError("prefix04 plan/result label sets differ")

    p4_complete_labels = set()
    p4_unknown_labels = set()
    latest_by_label = {}
    p4_accept_binding = file_binding(P4_ACCEPT_REL, "root accepted prefix04 index-only result")
    p4_report_binding = file_binding(P4_REPORT_REL, "prefix04 raw batch report")
    p4_plan_binding = file_binding(P4_PLAN_REL, "prefix04 literal query plan")
    p4_exec_binding = file_binding(P4_EXEC_REL, "prefix04 execution window/policy")
    p4_map_binding = file_binding(P4_MAP_REL, "prefix04 source-map attempt/result ledger")

    for label, result in p4_results.items():
        report_result = p4_report_results[label]
        map_entry = p4_map_entries[label]
        plan_candidate = p4_plan_candidates[label]
        complete = (
            report_result.get("status") == "complete_within_response"
            and result.get("valid_index") is True
            and not result.get("resume_keys")
            and not report_result.get("potential_truncation")
            and map_entry.get("status") == "complete_within_response"
        )
        if complete:
            p4_complete_labels.add(label)
        else:
            p4_unknown_labels.add(label)
        query_window = copy.deepcopy(plan_candidate.get("query_window") or p4_exec.get("query_window"))
        if not query_window:
            raise AssertionError(f"missing prefix04 query window for {label}")
        attempt_summaries = [compact_attempt(a) for a in map_entry.get("attempts", [])]
        latest_by_label[label] = {
            "kind": "prefix_index_only",
            "batch_id": p4_report["batch_id"],
            "label": label,
            "prefix": result["prefix"],
            "status": "valid_complete_index" if complete else "transport_or_parse_unknown",
            "window": query_window,
            "index_only": True,
            "payload_replay": False,
            "source_responses": 1 if complete else 0,
            "index_rows": result.get("index_rows", 0),
            "image_index_rows": result.get("image_index_rows", 0),
            "resume_keys": copy.deepcopy(result.get("resume_keys", [])),
            "potential_truncation": bool(report_result.get("potential_truncation", False)),
            "complete_prefix_evidence": complete,
            "acceptance": copy.deepcopy(p4_accept_binding),
            "batch_report": copy.deepcopy(p4_report_binding),
            "plan": copy.deepcopy(p4_plan_binding),
            "execution_plan": copy.deepcopy(p4_exec_binding),
            "source_map": copy.deepcopy(p4_map_binding),
            "acceptance_result": {
                "valid_index": bool(result.get("valid_index")),
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
            "attempts": attempt_summaries,
        }

    if len(p4_complete_labels) != 14 or len(p4_unknown_labels) != 6:
        raise AssertionError(f"unexpected prefix04 partition: {len(p4_complete_labels)} / {len(p4_unknown_labels)}")

    rows = copy.deepcopy(v4["coverage_rows"])
    v4_by_label = {x["gallery"]: x for x in rows}
    if set(p4_results) - set(v4_by_label):
        raise AssertionError("prefix04 has a gallery absent from v4 registry")
    for row in rows:
        label = row["gallery"]
        if label not in latest_by_label:
            continue
        latest = latest_by_label[label]
        row.setdefault("actual_prefix_windows", []).append(copy.deepcopy(latest))
        row["latest_prefix_record"] = {
            "batch_id": latest["batch_id"],
            "status": latest["status"],
            "complete_prefix_evidence": latest["complete_prefix_evidence"],
            "acceptance": copy.deepcopy(latest["acceptance"]),
            "batch_report": copy.deepcopy(latest["batch_report"]),
            "source_map": copy.deepcopy(latest["source_map"]),
        }
        row["coverage_class"] = "reviewed_window_complete" if latest["complete_prefix_evidence"] else "not_complete_or_unknown"
        row["coverage_status"] = "prefix04_valid_complete_index" if latest["complete_prefix_evidence"] else "prefix04_transport_or_parse_unknown"
        row["coverage_source_latest"] = "root accepted prefix04 index-only result; no payload replay"
        if latest["complete_prefix_evidence"]:
            row["prewindow_gap"] = None

    status_counts = {
        "archive_404": v4["stats"]["entity_audit_status_counts"]["archive_404"],
        "never_requested": v4["stats"]["entity_audit_status_counts"]["never_requested"],
        "transport_unknown": v4["stats"]["entity_audit_status_counts"]["transport_unknown"],
    }
    if sum(status_counts.values()) != 3368:
        raise AssertionError("v4 entity status counts do not conserve")
    limited_complete = [x for x in rows if x["coverage_class"] == "reviewed_window_complete"]
    incomplete = [x for x in rows if x["coverage_class"] != "reviewed_window_complete"]
    if len(limited_complete) != 43 or len(incomplete) != 7:
        raise AssertionError(f"unexpected v5 coverage partition: {len(limited_complete)} / {len(incomplete)}")

    prefix03_complete = {
        x["gallery"]
        for x in v4["coverage_rows"]
        if x.get("coverage_status") == "prefix03_valid_complete_index"
    }
    if len(prefix03_complete) != 5:
        raise AssertionError(f"expected five prefix03 complete groups, got {len(prefix03_complete)}")
    if len(p4_complete_labels) != 14:
        raise AssertionError("prefix04 complete count changed")

    map_by_batch_label = {}
    for batch_dir in ("gallery-prefix01", "gallery-prefix02", "gallery-prefix03", "gallery-prefix04"):
        map_path = BASE / "network" / batch_dir / "source-map.json"
        if not map_path.exists():
            continue
        batch_map = json.loads(map_path.read_text(encoding="utf-8"))
        batch_id = batch_map.get("batch_id")
        for entry in batch_map.get("entries", []):
            map_by_batch_label[(batch_id, entry.get("label"))] = entry

    def plan_item(row: dict, reason: str, query: dict, group: str) -> dict:
        prefix = absolute_prefix(row["source_evidence"])
        directory = row["source_evidence"].get("directory_literal") or row["source_evidence"].get("source_directory")
        expected = f"http://www.worldofwarcraft.com{directory}"
        if prefix != expected:
            raise AssertionError(f"prefix mismatch for {row['gallery']}: {prefix}")
        prior_windows = [compact_window(w) for w in row.get("actual_prefix_windows", [])]
        prior_attempts = compact_prior_attempts(row, map_by_batch_label)
        return {
            "registry_rank": row["registry_rank"],
            "gallery": row["gallery"],
            "category": row["category"],
            "source_page_route": row["source_page_route"],
            "declared_slots": row["declared_slots"],
            "expected_direct_entities": row["expected_direct_entities"],
            "prefix": prefix,
            "origin": {"scheme": "http", "host": "www.worldofwarcraft.com", "default_port": 80},
            "source_evidence": source_evidence(row),
            "prior_coverage": {
                "coverage_class": row.get("coverage_class"),
                "coverage_status": row.get("coverage_status"),
                "coverage_source": row.get("coverage_source"),
                "coverage_source_latest": row.get("coverage_source_latest"),
                "prior_windows": prior_windows,
                "prior_attempts": prior_attempts,
            },
            "followup_group": group,
            "reason": reason,
            "query_window": copy.deepcopy(query),
            "query_mode": "absolute HTTP prefix index only",
            "payload_recovery": False,
            "execution_status": "prepared_not_executed",
            "network_performed_in_this_plan": False,
            "no_filename_guess": True,
        }

    full_window = {
        "from": "20000101000000",
        "to": "20080512210044",
        "limit": 500,
        "showResumeKey": True,
        "collapse": False,
        "matchType": "prefix",
    }
    incomplete_labels = {x["gallery"] for x in incomplete}
    expected_incomplete = p4_unknown_labels | {"Amani War Bear"}
    if incomplete_labels != expected_incomplete:
        raise AssertionError(f"unexpected incomplete labels: {sorted(incomplete_labels)}")
    incomplete_items = []
    for row in sorted(incomplete, key=lambda x: x["registry_rank"]):
        reason = (
            "prefix04 index request returned transport_or_parse_unknown; rerun the complete 2000-to-anchor prefix window"
            if row["gallery"] in p4_unknown_labels
            else "Amani prior prefix01 attempt remained transport_unknown; run a complete 2000-to-anchor prefix window"
        )
        incomplete_items.append(plan_item(row, reason, full_window, "incomplete_prefixes_full_2000_anchor"))

    # The early-gap group is exactly the old v4 complete set except the five
    # prefix03 full-window groups and the fourteen new prefix04 full-window groups.
    old_complete = [x for x in v4["coverage_rows"] if x.get("coverage_class") == "reviewed_window_complete"]
    early_rows = [x for x in old_complete if x["gallery"] not in prefix03_complete and x["gallery"] not in p4_complete_labels]
    if len(early_rows) != 24:
        raise AssertionError(f"expected 24 early-gap groups, got {len(early_rows)}")
    early_items = []
    for row in sorted(early_rows, key=lambda x: x["registry_rank"]):
        complete_windows = [
            w for w in row.get("actual_prefix_windows", [])
            if w.get("complete_prefix_evidence") and w.get("window", {}).get("from")
        ]
        if not complete_windows:
            raise AssertionError(f"no complete prior window for early-gap row {row['gallery']}")
        earliest = min(w["window"]["from"] for w in complete_windows)
        if earliest <= full_window["from"]:
            raise AssertionError(f"early-gap row already has a full-window start: {row['gallery']}")
        early_query = dict(full_window)
        early_query["to"] = subtract_one_second(earliest)
        reason = f"No complete saved prefix query before earliest complete window starting {earliest}; query only the earlier data gap."
        item = plan_item(row, reason, early_query, "early_gap_before_earliest_complete_window")
        item["earliest_complete_prior_window_start"] = earliest
        item["early_gap_end_exclusive"] = earliest
        item["early_gap_query_end"] = early_query["to"]
        early_items.append(item)

    # The requested 20+4 split follows the actual query end derived from each
    # earliest complete window: nineteen 2006-start groups plus Karazhan's
    # pre-2007 interval form batch 1; the three 2004-start groups and Fishing's
    # pre-2008 interval form batch 2.  The individual query bounds remain per
    # row and are not widened to force a common window.
    for item in early_items:
        item["followup_batch"] = (
            "early_gap_batch_1_of_2_20_items"
            if item["query_window"]["to"] in {"20051231235959", "20061231235959"}
            else "early_gap_batch_2_of_2_4_items"
        )
    early_batch_1 = [x for x in early_items if x["followup_batch"] == "early_gap_batch_1_of_2_20_items"]
    early_batch_2 = [x for x in early_items if x["followup_batch"] == "early_gap_batch_2_of_2_4_items"]
    if len(early_batch_1) != 20 or len(early_batch_2) != 4:
        raise AssertionError(f"unexpected 20+4 early-gap split: {len(early_batch_1)} / {len(early_batch_2)}")

    prefix03_excluded = sorted(prefix03_complete)
    prefix04_excluded = sorted(p4_complete_labels)
    v5 = {
        "schema": "gallery-prefix-registry-v5-local21",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "network_performed": False,
        "git_performed": False,
        "scope": "Independent local merge of frozen v4 registry with root-accepted prefix04 index evidence; data-only follow-up plans; no network or payload replay.",
        "query_policy": {
            "origin": "http://www.worldofwarcraft.com",
            "default_port_normalization_only": True,
            "query_window_for_followups": full_window,
            "prefix_query_is_capture_index_evidence": True,
            "cdx_rows_are_not_payload_recovery": True,
            "no_filename_guess": True,
        },
        "input_hashes": copy.deepcopy(v4.get("input_hashes", {})),
        "stats": {
            "gallery_count": 50,
            "declared_slots": 1684,
            "expected_direct_entities": 3368,
            "coverage_group_counts": {
                "limited_complete": len(limited_complete),
                "incomplete_or_unknown": len(incomplete),
                "reviewed_window_complete": len(limited_complete),
                "not_complete_or_unknown": len(incomplete),
            },
            "prefix03_complete_groups_preserved": len(prefix03_complete),
            "prefix04_complete_groups_added": len(p4_complete_labels),
            "prefix04_unknown_groups_added": len(p4_unknown_labels),
            "incomplete_groups_after_prefix04": len(incomplete),
            "early_gap_followup_groups": len(early_items),
            "excluded_from_early_gap_followup_prefix03_full_window": len(prefix03_complete),
            "excluded_from_early_gap_followup_prefix04_full_window": len(p4_complete_labels),
            "entity_audit_status_counts": status_counts,
        },
        "conservation": {
            "groups": len(rows) == 50,
            "slots": sum(x["declared_slots"] for x in rows) == 1684,
            "entities": sum(x["expected_direct_entities"] for x in rows) == 3368,
            "status_entities": sum(status_counts.values()) == 3368,
            "prefix04_partition": len(p4_complete_labels) + len(p4_unknown_labels) == 20,
        },
        "coverage_rows": rows,
        "followup_partition": {
            "incomplete_labels": sorted(incomplete_labels),
            "early_gap_labels": [x["gallery"] for x in early_items],
            "prefix03_full_window_excluded": prefix03_excluded,
            "prefix04_full_window_excluded": prefix04_excluded,
        },
        "prefix04_binding": {
            "acceptance": p4_accept_binding,
            "plan": p4_plan_binding,
            "execution_plan": p4_exec_binding,
            "batch_report": p4_report_binding,
            "source_map": p4_map_binding,
            "historical_network_requests": p4_accept.get("network_requests"),
            "historical_source_responses": p4_accept.get("source_responses"),
            "historical_index_rows": p4_accept.get("index_rows"),
            "historical_body_bytes": p4_accept.get("body_bytes"),
            "historical_scope": p4_accept.get("scope"),
        },
        "notes": [
            "v4 rows and root amendment remain frozen; prefix04 evidence is appended as a latest record per matching gallery.",
            "The fourteen prefix04 complete results are limited complete index windows, not recovered direct image payloads.",
            "The six prefix04 transport_or_parse_unknown rows and Amani War Bear are the seven incomplete groups.",
            "Entity audit counts are copied unchanged from v4: prefix index queries do not change direct full/thumb entity status.",
            "The twenty-four early-gap plans target only the pre-window interval of already-reviewed non-prefix03 groups; prefix03 five and prefix04 fourteen are excluded because they already have a 2000-to-anchor query.",
        ],
    }
    for relpath, role in (
        (P4_ACCEPT_REL, "root accepted prefix04 index-only result"),
        (P4_PLAN_REL, "prefix04 query plan"),
        (P4_EXEC_REL, "prefix04 execution plan"),
        (P4_REPORT_REL, "prefix04 batch report"),
        (P4_MAP_REL, "prefix04 source map"),
        (P4_INPUT_REL, "prefix04 input bindings"),
        (P4_SUMMARY_REL, "prefix04 sanitized summary"),
    ):
        v5["input_hashes"][relpath] = file_binding(relpath, role)

    write_new(V5_REL, v5)
    v5_binding = file_binding(V5_REL, "new LOCAL21 merged v5 registry")

    incomplete_plan = {
        "schema": "gallery-followup-plan-v1",
        "generated_utc": v5["generated_utc"],
        "network_performed": False,
        "git_performed": False,
        "execution_status": "prepared_not_executed",
        "scope": "Seven incomplete gallery prefixes: full absolute HTTP prefix-window query from 2000-01-01 through the frozen anchor.",
        "source_registry": v5_binding,
        "query_policy": v5["query_policy"],
        "count": len(incomplete_items),
        "items": incomplete_items,
        "conservation": {
            "expected_count": 7,
            "actual_count": len(incomplete_items),
            "labels": sorted(incomplete_labels),
            "all_absolute_http": all(x["prefix"].startswith("http://www.worldofwarcraft.com/") for x in incomplete_items),
            "no_payload_replay": all(not x["payload_recovery"] for x in incomplete_items),
        },
        "notes": [
            "The six prefix04 unknown entries reflect the accepted prefix04 attempts; their capture-index result was not complete/valid.",
            "Amani preserves its prior prefix01 transport-unknown evidence and is not conflated with never-requested.",
            "No direct ssN full/thumb URLs are generated by this plan.",
        ],
    }
    early_plan = {
        "schema": "gallery-followup-plan-v1",
        "generated_utc": v5["generated_utc"],
        "network_performed": False,
        "git_performed": False,
        "execution_status": "prepared_not_executed",
        "scope": "Twenty-four previously checked gallery prefixes: query only the interval from 2000-01-01 through one second before each actual earliest complete prior window.",
        "source_registry": v5_binding,
        "query_policy": v5["query_policy"],
        "count": len(early_items),
        "batch_split": {
            "basis": "Each item ends one second before its actual earliest complete prior window; batch 1 contains the nineteen 2006-start gaps plus Karazhan's 2007-start gap, while batch 2 retains the three 2004-start gaps and Fishing's 2008-start gap.",
            "batch_1": {
                "label": "early_gap_batch_1_of_2_20_items",
                "count": len(early_batch_1),
                "query_end_values": {v: sum(x["query_window"]["to"] == v for x in early_batch_1) for v in sorted({x["query_window"]["to"] for x in early_batch_1})},
            },
            "batch_2": {
                "label": "early_gap_batch_2_of_2_4_items",
                "count": len(early_batch_2),
                "query_end_values": {v: sum(x["query_window"]["to"] == v for x in early_batch_2) for v in sorted({x["query_window"]["to"] for x in early_batch_2})},
            },
        },
        "excluded_full_window_groups": {
            "prefix03": prefix03_excluded,
            "prefix04": prefix04_excluded,
            "count": len(prefix03_excluded) + len(prefix04_excluded),
        },
        "items": early_items,
        "conservation": {
            "expected_count": 24,
            "actual_count": len(early_items),
            "all_absolute_http": all(x["prefix"].startswith("http://www.worldofwarcraft.com/") for x in early_items),
            "all_have_earliest_complete_start": all("earliest_complete_prior_window_start" in x for x in early_items),
            "no_payload_replay": all(not x["payload_recovery"] for x in early_items),
        },
        "notes": [
            "The early-gap plan does not recheck the five prefix03 and fourteen prefix04 full-window groups.",
            "A CDX index row remains evidence of an indexed capture only; this plan does not claim payload recovery.",
            "Historical saved windows have no network attempt in this plan; any attempt summaries present are copied from existing source-map evidence.",
        ],
    }
    write_new(INCOMPLETE_REL, incomplete_plan)
    write_new(EARLY_REL, early_plan)
    incomplete_binding = file_binding(INCOMPLETE_REL, "new LOCAL21 seven-incomplete follow-up plan")
    early_binding = file_binding(EARLY_REL, "new LOCAL21 twenty-four early-gap follow-up plan")

    public = {
        "schema": "gallery-prefix-registry-v5-public-summary",
        "generated_utc": v5["generated_utc"],
        "network_performed": False,
        "git_performed": False,
        "coverage": {
            "groups": 50,
            "declared_slots": 1684,
            "dynamic_entities": 3368,
            "limited_complete": 43,
            "incomplete_or_unknown": 7,
            "prefix03_full_window_excluded_from_early_gap": 5,
            "prefix04_full_window_excluded_from_early_gap": 14,
            "early_gap_followup": 24,
            "early_gap_followup_batches": {"batch_1": 20, "batch_2": 4},
        },
        "entity_audit_status_counts": status_counts,
        "incomplete_labels": sorted(incomplete_labels),
        "plan_bindings": {"registry": v5_binding, "incomplete": incomplete_binding, "early_gap": early_binding},
        "boundary": "Prefix-index evidence is not direct image-payload recovery; no network or payload replay was performed in LOCAL21.",
    }
    write_new(PUBLIC_REL, public)
    public_binding = file_binding(PUBLIC_REL, "new LOCAL21 sanitized public summary")

    verification = {
        "schema": "gallery-prefix-registry-v5-verification",
        "generated_utc": v5["generated_utc"],
        "network_performed": False,
        "git_performed": False,
        "command": "python.exe -X utf8 research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v5/build_gallery_prefix_registry_v5.py",
        "inputs": {
            "v4_registry": file_binding(V4_REL, "frozen v4 registry"),
            "prefix04_acceptance": p4_accept_binding,
            "prefix04_plan": p4_plan_binding,
            "prefix04_execution_plan": p4_exec_binding,
            "prefix04_report": p4_report_binding,
            "prefix04_source_map": p4_map_binding,
        },
        "outputs": {
            "registry": v5_binding,
            "incomplete_plan": incomplete_binding,
            "early_gap_plan": early_binding,
            "public_summary": public_binding,
        },
        "checks": {
            "groups": len(rows) == 50,
            "slots": sum(x["declared_slots"] for x in rows) == 1684,
            "entities": sum(x["expected_direct_entities"] for x in rows) == 3368,
            "limited_complete": len(limited_complete) == 43,
            "incomplete_or_unknown": len(incomplete) == 7,
            "prefix04_complete": len(p4_complete_labels) == 14,
            "prefix04_unknown": len(p4_unknown_labels) == 6,
            "prefix03_excluded": len(prefix03_complete) == 5,
            "early_gap_plan": len(early_items) == 24,
            "early_gap_batch_1": len(early_batch_1) == 20,
            "early_gap_batch_2": len(early_batch_2) == 4,
            "entity_status_archive_404": status_counts["archive_404"] == 79,
            "entity_status_never_requested": status_counts["never_requested"] == 3242,
            "entity_status_transport_unknown": status_counts["transport_unknown"] == 47,
            "entity_status_total": sum(status_counts.values()) == 3368,
            "all_followup_prefixes_absolute_http": all(
                x["prefix"].startswith("http://www.worldofwarcraft.com/") for x in incomplete_items + early_items
            ),
            "all_followups_unexecuted": all(
                x["execution_status"] == "prepared_not_executed" for x in incomplete_items + early_items
            ),
            "no_payload_replay": all(not x["payload_recovery"] for x in incomplete_items + early_items),
        },
        "coverage_sets": {
            "prefix03_full_window_excluded": prefix03_excluded,
            "prefix04_full_window_excluded": prefix04_excluded,
            "incomplete": sorted(incomplete_labels),
            "early_gap": [x["gallery"] for x in early_items],
            "early_gap_batch_1": [x["gallery"] for x in early_batch_1],
            "early_gap_batch_2": [x["gallery"] for x in early_batch_2],
        },
    }
    write_new(VERIFY_REL, verification)

    print(json.dumps({
        "registry": v5_binding,
        "incomplete_plan": incomplete_binding,
        "early_gap_plan": early_binding,
        "public_summary": public_binding,
        "verification": file_binding(VERIFY_REL, "new LOCAL21 verification receipt"),
        "counts": {
            "groups": len(rows),
            "slots": sum(x["declared_slots"] for x in rows),
            "entities": sum(x["expected_direct_entities"] for x in rows),
            "limited_complete": len(limited_complete),
            "incomplete": len(incomplete),
            "prefix04_complete": len(p4_complete_labels),
            "prefix04_unknown": len(p4_unknown_labels),
            "early_gap": len(early_items),
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

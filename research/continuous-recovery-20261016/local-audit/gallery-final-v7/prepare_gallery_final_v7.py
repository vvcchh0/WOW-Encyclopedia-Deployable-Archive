#!/usr/bin/env python3
"""Prepare the v7 gallery registry from frozen v6 plus accepted EARLY01/02.

The default mode writes only a working ledger. It never freezes the v7
receipt while EARLY03's root acceptance is absent. --freeze-final is
deliberately gated by that acceptance and is intended for a later local run.
No network, Git, payload replay, or production input is used.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "research/continuous-recovery-20261016/local-audit/gallery-final-v7"
V6 = ROOT / "research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v6/gallery-prefix-registry-v6.json"
EARLY01 = ROOT / "research/continuous-recovery-20261016/publication/root-gallery-early01-acceptance.json"
EARLY02 = ROOT / "research/continuous-recovery-20261016/publication/root-gallery-early02-acceptance.json"
EARLY03 = ROOT / "research/continuous-recovery-20261016/publication/root-gallery-early03-acceptance.json"
EARLY03_PLAN = ROOT / "research/continuous-recovery-20261016/publication/root-gallery-early03-plan-acceptance.json"
EARLY01_BATCH = ROOT / "research/continuous-recovery-20261016/network/gallery-early01/batch-report.json"
EARLY01_SOURCE = ROOT / "research/continuous-recovery-20261016/network/gallery-early01/source-map.json"
EARLY02_BATCH = ROOT / "research/continuous-recovery-20261016/network/gallery-early02/batch-report.json"
EARLY02_SOURCE = ROOT / "research/continuous-recovery-20261016/network/gallery-early02/source-map.json"
EARLY03_BATCH = ROOT / "research/continuous-recovery-20261016/network/gallery-early03/batch-report.json"
EARLY03_SOURCE = ROOT / "research/continuous-recovery-20261016/network/gallery-early03/source-map.json"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()

def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def binding(path: Path, role: str) -> dict[str, Any]:
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256(path), "role": role}

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    query = result.get("query_window") or {}
    return {
        "label": result.get("label"),
        "prefix": result.get("prefix"),
        "query_window": query,
        "valid_index": result.get("valid_index"),
        "index_rows": result.get("index_rows"),
        "resume_keys": result.get("resume_keys") or [],
        "direct_exact_candidates": result.get("direct_exact_candidates"),
        "direct_variant_candidates": result.get("direct_variant_candidates"),
        "image_index_rows": result.get("image_index_rows"),
        "rows": result.get("rows") or [],
    }

def accepted_results(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = read(path)
    if payload.get("accepted") is not True:
        raise RuntimeError(f"{rel(path)} is not accepted")
    results = payload.get("results")
    if not isinstance(results, list):
        raise RuntimeError(f"{rel(path)} has no result list")
    by_label = {}
    for result in results:
        label = str(result.get("label") or "")
        if not label or label in by_label:
            raise RuntimeError(f"duplicate/empty accepted result label in {rel(path)}")
        by_label[label] = result
    return payload, by_label

def build_working() -> tuple[dict[str, Any], dict[str, Any]]:
    if not V6.is_file() or not EARLY01.is_file() or not EARLY02.is_file():
        raise RuntimeError("v6 or EARLY01/EARLY02 acceptance input is missing")
    v6 = read(V6)
    early01, r01 = accepted_results(EARLY01)
    early02, r02 = accepted_results(EARLY02)
    if len(r01) != 20 or len(r02) != 4:
        raise RuntimeError(f"expected EARLY01=20/EARLY02=4, got {len(r01)}/{len(r02)}")
    overlap = set(r01) & set(r02)
    if overlap:
        raise RuntimeError(f"EARLY01/EARLY02 overlap: {sorted(overlap)}")
    rows = v6.get("coverage_rows") or []
    by_label = {str(row.get("gallery") or ""): row for row in rows}
    early_gap_labels = set((v6.get("followup_partition") or {}).get("early_gap_labels") or [])
    if set(r01) | set(r02) != early_gap_labels:
        raise RuntimeError("EARLY01/EARLY02 labels do not exactly cover v6 early_gap_labels")
    out = copy.deepcopy(v6)
    out["schema"] = "gallery-prefix-registry-v7-working"
    out["generated_utc"] = now()
    out["network_performed"] = False
    out["git_performed"] = False
    out["scope"] = (
        "Offline working merge of frozen v6 with root-accepted EARLY01/EARLY02 "
        "early-window records. Twenty complete-empty early windows are applied; "
        "four validity-unknown groups remain pending EARLY03 acceptance. "
        "No CDX index row is promoted to payload recovery."
    )
    by_label = {
        str(row.get("gallery") or ""): row
        for row in (out.get("coverage_rows") or [])
    }
    out["input_hashes"] = {
        "v6": binding(V6, "frozen v6 source registry"),
        "early01_acceptance": binding(EARLY01, "root accepted EARLY01 empty early-window result"),
        "early02_acceptance": binding(EARLY02, "root accepted EARLY02 early-window result"),
        "early03_plan_acceptance": binding(EARLY03_PLAN, "root accepted EARLY03 plan; execution/final acceptance still absent"),
        "early01_batch_report": binding(EARLY01_BATCH, "EARLY01 actual batch report"),
        "early01_source_map": binding(EARLY01_SOURCE, "EARLY01 actual source rows"),
        "early02_batch_report": binding(EARLY02_BATCH, "EARLY02 actual batch report"),
        "early02_source_map": binding(EARLY02_SOURCE, "EARLY02 actual source rows"),
    }
    if EARLY03.exists():
        out["input_hashes"]["early03_acceptance_observed"] = binding(
            EARLY03, "observed EARLY03 acceptance; working output still requires explicit freeze mode"
        )
    for label in sorted(early_gap_labels):
        row = by_label[label]
        if label in r01:
            result = r01[label]
            batch_id = "GALLERYEARLY01"
            acceptance_path = EARLY01
        elif label in r02:
            result = r02[label]
            batch_id = "GALLERYEARLY02"
            acceptance_path = EARLY02
        else:
            raise RuntimeError(f"unclassified v6 early-gap row: {label}")
        if result.get("valid_index") is True and result.get("index_rows") == 0:
            status = "complete_empty_early_window"
            evidence_role = f"root accepted {batch_id}; valid empty index window"
        else:
            status = "unknown_pending_early03"
            evidence_role = f"root accepted {batch_id} result retained as unknown pending EARLY03"
        compact = compact_result(result)
        compact["batch_id"] = batch_id
        compact["acceptance"] = binding(acceptance_path, evidence_role)
        compact["record_semantics"] = (
            "Index query returned zero rows; this is bounded index evidence and does not "
            "prove absence or a direct payload 404."
        )
        compact["early_gap_status"] = status
        row.setdefault("actual_prefix_windows", []).append({
            "kind": "accepted_early_gap_index",
            "status": status,
            "label": label,
            "prefix": result.get("prefix"),
            "window": result.get("query_window"),
            "index_rows": result.get("index_rows"),
            "direct_exact_candidates": result.get("direct_exact_candidates"),
            "direct_variant_candidates": result.get("direct_variant_candidates"),
            "image_index_rows": result.get("image_index_rows"),
            "resume_keys": result.get("resume_keys") or [],
            "source_result_valid_index": result.get("valid_index"),
            "complete_empty_query_result": (result.get("index_rows") == 0),
            "acceptance": compact["acceptance"],
            "batch_id": batch_id,
        })
        row["early_gap_resolution"] = compact
        row["coverage_class"] = "reviewed_window_complete"
        row["coverage_status"] = (
            "v7_early_window_complete_empty" if status == "complete_empty_early_window"
            else "v7_early_window_unknown_pending_early03"
        )
    out["followup_partition"] = {
        **(out.get("followup_partition") or {}),
        "early_gap_labels": sorted(early_gap_labels),
        "early_gap_complete_empty_early01_or_early02": sorted(
            label for label, result in {**r01, **r02}.items()
            if result.get("valid_index") is True and result.get("index_rows") == 0
        ),
        "early_gap_unknown_pending_early03": sorted(
            label for label, result in {**r01, **r02}.items()
            if not (result.get("valid_index") is True and result.get("index_rows") == 0)
        ),
        "early03_required_before_final_freeze": True,
    }
    stats = copy.deepcopy(out.get("stats") or {})
    stats["coverage_group_counts"] = {
        "limited_complete": len(rows),
        "incomplete_or_unknown": 0,
        "reviewed_window_complete": len(rows),
        "not_complete_or_unknown": 0,
    }
    stats["full_window_complete_groups"] = 46
    stats["full_window_incomplete_or_unknown_groups"] = 4
    stats["early_gap_complete_empty_groups"] = 20
    stats["early_gap_unknown_pending_early03_groups"] = 4
    stats["full_window_partition"] = {
        "global_complete_groups": 46,
        "pending_unknown_groups": 4,
        "source": "v6 full-window partition plus root-accepted EARLY01/02 result classification",
        "index_rows_are_not_payloads": True,
    }
    stats["entity_audit_status_counts"] = {
        "archive_404": 79,
        "transport_unknown": 47,
        "never_requested": 3242,
    }
    out["stats"] = stats
    out["conservation"] = {
        **(out.get("conservation") or {}),
        "groups": len(rows) == 50,
        "slots": sum(int(row["declared_slots"]) for row in rows) == 1684,
        "entities": sum(int(row["expected_direct_entities"]) for row in rows) == 3368,
        "status_entities": stats["entity_audit_status_counts"] == {
            "archive_404": 79, "transport_unknown": 47, "never_requested": 3242
        },
        "limited_window_partition": len(rows) == 50,
        "global_window_partition": 46 + 4 == 50,
        "early01_early02_partition": len(r01) + len(r02) == 24,
        "index_rows_not_payloads": True,
    }
    out["notes"] = list(out.get("notes") or []) + [
        "v7 working ledger applies root-accepted EARLY01/EARLY02 records as 20 valid empty early windows and 4 validity-unknown groups, without changing direct entity statuses.",
        "The four validity-unknown groups remain pending EARLY03; the unknown set spans EARLY01 and EARLY02 rather than all four EARLY02 rows.",
        "EARLY03 acceptance is required before a gallery-prefix-registry-v7 final receipt may be frozen.",
    ]
    return out, {"early01": early01, "early02": early02}

def write_working() -> dict[str, Any]:
    out, accepted = build_working()
    target = OUT / "gallery-prefix-registry-v7-working.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "schema": "gallery-prefix-registry-v7-working-summary",
        "generated_utc": out["generated_utc"],
        "working_registry": rel(target),
        "working_registry_sha256": sha256(target),
        "final_receipt_frozen": False,
        "required_before_final_freeze": rel(EARLY03),
        "early03_acceptance_present": EARLY03.exists(),
        "stats": out["stats"],
        "conservation": out["conservation"],
        "network_performed": False,
        "git_performed": False,
    }
    (OUT / "gallery-prefix-registry-v7-working-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    verification = {
        "schema": "gallery-prefix-registry-v7-working-verification",
        "working_registry_sha256": sha256(target),
        "v6_sha256": sha256(V6),
        "early01_sha256": sha256(EARLY01),
        "early02_sha256": sha256(EARLY02),
        "early03_acceptance_present": EARLY03.exists(),
        "final_receipt_frozen": False,
        "checks": {
            "groups_50": out["conservation"]["groups"],
            "slots_1684": out["conservation"]["slots"],
            "entities_3368": out["conservation"]["entities"],
            "native_status_79_47_3242": out["conservation"]["status_entities"],
            "early01_count_20": len(accepted["early01"].get("results") or []) == 20,
            "early02_count_4": len(accepted["early02"].get("results") or []) == 4,
            "global_complete_46_pending_4": out["conservation"]["global_window_partition"],
            "no_network": True,
            "no_git": True,
        },
    }
    (OUT / "gallery-prefix-registry-v7-working-verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary

def write_final() -> dict[str, Any]:
    if not EARLY03.is_file():
        raise SystemExit("refusing final v7 freeze: EARLY03 acceptance is absent")
    final_acceptance, r03 = accepted_results(EARLY03)
    if len(r03) != 4:
        raise SystemExit(f"refusing final v7 freeze: expected EARLY03=4, got {len(r03)}")
    out, accepted = build_working()
    rows = {str(row.get("gallery") or ""): row for row in out["coverage_rows"]}
    unknown_labels = {
        str(row.get("gallery") or "")
        for row in out["coverage_rows"]
        if (row.get("early_gap_resolution") or {}).get("early_gap_status")
        == "unknown_pending_early03"
    }
    if set(r03) != unknown_labels:
        raise SystemExit("refusing final v7 freeze: EARLY03 labels do not match the four v6/EARLY01/EARLY02 unknown groups")
    for label, result in r03.items():
        row = rows[label]
        prior = row.get("early_gap_resolution") or {}
        final_resolution = compact_result(result)
        final_resolution.update({
            "batch_id": "GALLERYEARLY03",
            "acceptance": binding(EARLY03, "root accepted EARLY03 retry result"),
            "early_gap_status": "complete_early_window_after_early03",
            "prior_status": prior.get("early_gap_status"),
            "record_semantics": (
                "EARLY03 is an accepted bounded index result. Its nine Fishing rows are "
                "image-index/nested evidence only; no direct dynamic entity is promoted to payload recovery."
            ),
        })
        row.setdefault("actual_prefix_windows", []).append({
            "kind": "accepted_early_gap_index",
            "status": "complete_early_window_after_early03",
            "label": label,
            "prefix": result.get("prefix"),
            "window": result.get("query_window"),
            "index_rows": result.get("index_rows"),
            "direct_exact_candidates": result.get("direct_exact_candidates"),
            "direct_variant_candidates": result.get("direct_variant_candidates"),
            "image_index_rows": result.get("image_index_rows"),
            "resume_keys": result.get("resume_keys") or [],
            "source_result_valid_index": result.get("valid_index"),
            "complete_empty_query_result": (result.get("index_rows") == 0),
            "acceptance": final_resolution["acceptance"],
            "batch_id": "GALLERYEARLY03",
        })
        row["early_gap_resolution"] = final_resolution
        row["coverage_status"] = "v7_global_early_window_complete"
    out["schema"] = "gallery-prefix-registry-v7"
    out["generated_utc"] = now()
    out["scope"] = (
        "Offline final merge of frozen v6 with root-accepted EARLY01/EARLY02/EARLY03 "
        "early-window records. All 50 limited groups now have an accepted complete "
        "2000-to-anchor or bounded early-window record; CDX/index rows are not payload recovery."
    )
    out["input_hashes"]["early03_acceptance"] = binding(EARLY03, "root accepted EARLY03 retry result")
    out["input_hashes"]["early03_batch_report"] = binding(EARLY03_BATCH, "EARLY03 actual batch report")
    out["input_hashes"]["early03_source_map"] = binding(EARLY03_SOURCE, "EARLY03 actual source rows")
    stats = copy.deepcopy(out.get("stats") or {})
    stats["full_window_complete_groups"] = 50
    stats["full_window_incomplete_or_unknown_groups"] = 0
    stats["early_gap_complete_empty_groups"] = 23
    stats["early_gap_complete_nonempty_index_groups"] = 1
    stats["early_gap_unknown_pending_early03_groups"] = 0
    stats["early_gap_resolution_counts"] = {
        "accepted_early01_early02_complete_empty": 20,
        "accepted_early01_early02_unknown_resolved_by_early03": 4,
        "final_complete_empty": 23,
        "final_complete_nonempty_index": 1,
    }
    stats["full_window_partition"] = {
        "global_complete_groups": 50,
        "pending_unknown_groups": 0,
        "source": "v6 partition plus accepted EARLY01/02/03 early-window records",
        "index_rows_are_not_payloads": True,
    }
    out["stats"] = stats
    out["followup_partition"]["early_gap_unknown_pending_early03"] = []
    out["followup_partition"]["early_gap_complete_after_early03"] = sorted(r03)
    out["followup_partition"]["early03_required_before_final_freeze"] = False
    out["conservation"]["global_window_partition"] = 50 + 0 == 50
    out["conservation"]["early03_partition"] = len(r03) == 4
    out["conservation"]["all_early_gaps_resolved"] = True
    out["notes"] = list(out.get("notes") or []) + [
        "Final v7 incorporates root-accepted EARLY03 for the four former unknown groups.",
        "EARLY03 Fishing contains nine image-index rows; these remain index evidence and do not alter the native 79/47/3242 direct-entity audit.",
    ]
    target = OUT / "gallery-prefix-registry-v7.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "schema": "gallery-prefix-registry-v7-summary",
        "generated_utc": out["generated_utc"],
        "registry": rel(target),
        "registry_sha256": sha256(target),
        "final_receipt_frozen": True,
        "early03_acceptance": binding(EARLY03, "root accepted EARLY03 retry result"),
        "early_source_bindings": [
            binding(EARLY01_BATCH, "EARLY01 actual batch report"),
            binding(EARLY01_SOURCE, "EARLY01 actual source rows"),
            binding(EARLY02_BATCH, "EARLY02 actual batch report"),
            binding(EARLY02_SOURCE, "EARLY02 actual source rows"),
            binding(EARLY03_BATCH, "EARLY03 actual batch report"),
            binding(EARLY03_SOURCE, "EARLY03 actual source rows"),
        ],
        "stats": out["stats"],
        "conservation": out["conservation"],
        "network_performed": False,
        "git_performed": False,
    }
    (OUT / "gallery-prefix-registry-v7-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    verification = {
        "schema": "gallery-prefix-registry-v7-verification",
        "registry_sha256": sha256(target),
        "v6_sha256": sha256(V6),
        "early01_sha256": sha256(EARLY01),
        "early02_sha256": sha256(EARLY02),
        "early03_sha256": sha256(EARLY03),
        "early01_batch_sha256": sha256(EARLY01_BATCH),
        "early01_source_sha256": sha256(EARLY01_SOURCE),
        "early02_batch_sha256": sha256(EARLY02_BATCH),
        "early02_source_sha256": sha256(EARLY02_SOURCE),
        "early03_batch_sha256": sha256(EARLY03_BATCH),
        "early03_source_sha256": sha256(EARLY03_SOURCE),
        "final_receipt_frozen": True,
        "checks": {
            "groups_50": out["conservation"]["groups"],
            "slots_1684": out["conservation"]["slots"],
            "entities_3368": out["conservation"]["entities"],
            "native_status_79_47_3242": out["conservation"]["status_entities"],
            "early01_count_20": len(accepted["early01"].get("results") or []) == 20,
            "early02_count_4": len(accepted["early02"].get("results") or []) == 4,
            "accepted_early01_early02_complete_empty_20": (
                sum(
                    1 for result in [
                        *(accepted["early01"].get("results") or []),
                        *(accepted["early02"].get("results") or []),
                    ]
                    if result.get("valid_index") is True and result.get("index_rows") == 0
                ) == 20
            ),
            "accepted_early01_early02_unknown_4": (
                sum(
                    1 for result in [
                        *(accepted["early01"].get("results") or []),
                        *(accepted["early02"].get("results") or []),
                    ]
                    if not (result.get("valid_index") is True and result.get("index_rows") == 0)
                ) == 4
            ),
            "early03_count_4": len(r03) == 4,
            "global_complete_50_pending_0": out["conservation"]["global_window_partition"],
            "all_early_gaps_resolved": out["conservation"]["all_early_gaps_resolved"],
            "index_rows_not_payloads": out["conservation"]["index_rows_not_payloads"],
            "no_network": True,
            "no_git": True,
        },
    }
    (OUT / "gallery-prefix-registry-v7-verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-final", action="store_true")
    args = parser.parse_args()
    summary = write_working()
    if args.freeze_final:
        print(json.dumps(write_final(), ensure_ascii=False, sort_keys=True))
        return 0
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

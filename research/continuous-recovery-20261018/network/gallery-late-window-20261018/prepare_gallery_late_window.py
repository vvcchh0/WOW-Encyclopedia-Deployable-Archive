"""Prepare the three-prefix late native-gallery CDX index window offline."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
REGISTRY = ROOT / "research" / "continuous-recovery-20261016" / "local-audit" / "gallery-final-v7" / "gallery-prefix-registry-v7.json"
REGISTRY_ACCEPTANCE = ROOT / "research" / "continuous-recovery-20261016" / "publication" / "root-gallery-registry-v7-acceptance.json"
TEMPLATE_DRIVER = ROOT / "research" / "continuous-recovery-20261016" / "network" / "gallery-prefix04" / "gallery_prefix_driver_v4.py"
TEMPLATE_PLAN = ROOT / "research" / "continuous-recovery-20261016" / "network" / "gallery-prefix04" / "plan.json"
TEMPLATE_ACCEPTANCE = ROOT / "research" / "continuous-recovery-20261016" / "publication" / "root-gallery-prefix04-acceptance.json"
TEMPLATE_FIXTURE = ROOT / "research" / "continuous-recovery-20261016" / "network" / "gallery-prefix04" / "fixture-results.json"
LATEST_SOURCE = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "root-news-unplanned-batch4-source-acceptance.json"
CONTROL_GATE = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "root-dns-connectivity-control-acceptance.json"
DRIVER = OUT / "gallery_late_window_driver_v1.py"
PLAN = OUT / "plan.json"
FIXTURE = OUT / "fixture-results.json"
BINDINGS = OUT / "input-bindings.json"
MANIFEST = OUT / "plan-manifest.json"

FROM_TS = "20080512210045"
TO_TS = "20101207235959"
LIMIT = 500
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
TARGETS = ["Karazhan", "Zul'Aman", "Black Temple"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bind(path: Path, role: str) -> dict:
    return {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size, "role": role}


def query_url(prefix: str, from_ts: str, to_ts: str) -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(prefix, safe="")
        + "&matchType=prefix&output=json&fl=" + quote(",".join(FIELDS), safe="")
        + f"&from={from_ts}&to={to_ts}&limit={LIMIT}&showResumeKey=true"
    )


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")


def complete_prior_intervals(prior: list[dict]) -> list[tuple[datetime, datetime, dict]]:
    intervals = []
    for entry in prior:
        window = entry.get("window") or {}
        complete = entry.get("complete_prefix_evidence") is True or entry.get("status") in {
            "valid_complete_index", "executed_complete_prefix", "executed_prefix_only_no_valid_direct_entity",
        }
        if not complete or not window.get("from") or not window.get("to"):
            continue
        try:
            start, end = parse_timestamp(str(window["from"])), parse_timestamp(str(window["to"]))
        except ValueError:
            continue
        intervals.append((start, end, entry))
    return intervals


def merge_intervals(intervals: list[tuple[datetime, datetime, dict]]) -> list[tuple[datetime, datetime, list[dict]]]:
    merged: list[tuple[datetime, datetime, list[dict]]] = []
    for start, end, evidence in sorted(intervals, key=lambda item: (item[0], item[1])):
        if not merged or start > merged[-1][1] + timedelta(seconds=1):
            merged.append((start, end, [evidence]))
            continue
        old_start, old_end, old_evidence = merged[-1]
        merged[-1] = (old_start, max(old_end, end), old_evidence + [evidence])
    return merged


def uncovered_gaps(prior: list[dict]) -> tuple[list[dict], list[dict]]:
    target_start, target_end = parse_timestamp(FROM_TS), parse_timestamp(TO_TS)
    relevant: list[dict] = []
    clipped = []
    for start, end, evidence in complete_prior_intervals(prior):
        if end < target_start - timedelta(seconds=1) or start > target_end:
            continue
        overlap_start, overlap_end = max(start, target_start), min(end, target_end)
        relevant.append({
            "from": timestamp(start),
            "to": timestamp(end),
            "relation_to_target": "adjacent_before_target" if end == target_start - timedelta(seconds=1) else "overlap",
            "clipped_to_target": None if end < target_start else {"from": timestamp(overlap_start), "to": timestamp(overlap_end)},
            "evidence": evidence,
        })
        if end < target_start:
            continue
        clipped.append((max(start, target_start), min(end, target_end), evidence))
    merged = merge_intervals(clipped)
    gaps: list[dict] = []
    cursor = target_start
    for start, end, evidence in merged:
        if cursor < start:
            gaps.append({"from": timestamp(cursor), "to": timestamp(start - timedelta(seconds=1)), "excluded_prior_windows": evidence})
        cursor = max(cursor, end + timedelta(seconds=1))
    if cursor <= target_end:
        gaps.append({"from": timestamp(cursor), "to": timestamp(target_end), "excluded_prior_windows": []})
    return gaps, relevant


def prior_window_summary(row: dict) -> list[dict]:
    summary = []
    for window in row.get("actual_prefix_windows") or []:
        query = window.get("window") or {}
        entry = {
            "kind": window.get("kind"),
            "evidence_id": window.get("evidence_id"),
            "batch_id": window.get("batch_id"),
            "status": window.get("status"),
            "prefix": window.get("prefix"),
            "window": query,
            "complete_prefix_evidence": window.get("complete_prefix_evidence"),
            "source_responses": window.get("source_responses"),
            "index_rows": window.get("index_rows"),
            "direct_entity_rows": window.get("direct_entity_rows"),
            "status200_image_rows": window.get("status200_image_rows"),
            "nested_excluded_rows": window.get("nested_excluded_rows"),
            "direct_exact_candidates": window.get("direct_exact_candidates"),
            "direct_variant_candidates": window.get("direct_variant_candidates"),
            "acceptance": window.get("acceptance"),
            "batch_report": window.get("batch_report"),
            "source_map": window.get("source_map"),
            "evidence_paths": window.get("evidence_paths"),
            "report_quote": window.get("report_quote"),
        }
        summary.append(entry)
    return summary


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    registry = read(REGISTRY)
    rows = registry.get("coverage_rows") or []
    bindings = {
        "gallery_final_v7_registry": bind(REGISTRY, "frozen v7 native-gallery directory registry and source-page literals"),
        "root_gallery_registry_v7_acceptance": bind(REGISTRY_ACCEPTANCE, "root accepted frozen v7 registry"),
        "template_gallery_prefix04_driver_v4": bind(TEMPLATE_DRIVER, "accepted v4 index-only transport/parser template"),
        "template_gallery_prefix04_plan": bind(TEMPLATE_PLAN, "accepted v4 plan shape and cadence reference"),
        "template_gallery_prefix04_acceptance": bind(TEMPLATE_ACCEPTANCE, "accepted v4 index-only execution reference"),
        "template_gallery_prefix04_fixture": bind(TEMPLATE_FIXTURE, "accepted v4 offline fixture reference"),
        "latest_image_source_acceptance": bind(LATEST_SOURCE, "latest root accepted image batch tail-zero source receipt"),
        "latest_control_gate": bind(CONTROL_GATE, "latest root accepted tail-zero connectivity control gate"),
    }
    candidates = []
    prior_coverage = {}
    gap_summary = {}
    for gallery in TARGETS:
        row = next((x for x in rows if x.get("gallery") == gallery), None)
        if row is None:
            raise RuntimeError(f"missing frozen v7 row: {gallery}")
        source = row["source_evidence"]
        prefix = f"http://www.worldofwarcraft.com{source['source_directory']}"
        prior = prior_window_summary(row)
        prior_coverage[gallery] = prior
        gaps, excluded = uncovered_gaps(prior)
        if not gaps:
            raise RuntimeError(f"requested late window already complete for {gallery}: {excluded}")
        gap_summary[gallery] = {"target": {"from": FROM_TS, "to": TO_TS}, "excluded_complete_intervals": excluded, "uncovered_gaps": gaps}
        for gap_index, gap in enumerate(gaps, 1):
            rank = len(candidates) + 1
            qwindow = {"from": gap["from"], "to": gap["to"], "limit": LIMIT, "showResumeKey": True, "collapse": False, "matchType": "prefix"}
            candidates.append({
                "rank": rank,
                "target_key": f"GALLERY-LATE-WINDOW-{rank:02d}",
                "gallery_segment_index": gap_index,
                "gallery_segment_count": len(gaps),
                "gallery": gallery,
                "registry_rank": row["registry_rank"],
                "category": row["category"],
                "source_page_route": row["source_page_route"],
                "declared_slots": row["declared_slots"],
                "expected_direct_entities": row["expected_direct_entities"],
                "origin_host": row["origin_host_from_entity_urls"],
                "origin_schemes": row["origin_schemes_from_entity_urls"],
                "prefix": prefix,
                "source_evidence": source,
                "query_url": query_url(prefix, gap["from"], gap["to"]),
                "query_window": qwindow,
                "prior_window_evidence": prior,
                "prior_window_exact_target_complete": False,
                "coverage_exclusion": excluded,
                "uncovered_gap": gap,
                "status": "not_executed",
                "index_only": True,
                "payload_replay": False,
                "no_filename_guess": True,
            })
    plan = {
        "schema": "wow-recovery.gallery-late-window-plan.v1",
        "batch_id": "WAYBACK-GALLERY-LATE-WINDOW-20261018",
        "prepared_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "prepared",
        "network_requests": 0,
        "network_authorized_by_this_file": None,
        "parent_go_required": True,
        "candidate_count": len(candidates),
        "target_gallery_count": len(TARGETS),
        "target_galleries": TARGETS,
        "scope": "Exact Karazhan, Zul'Aman, and Black Temple native US gallery prefixes from frozen gallery-final-v7 source-page literals; subtract each gallery's prior complete prefix intervals and query only explicit uncovered gaps; CDX index only, no replay or automatic pagination.",
        "registry_path": rel(REGISTRY),
        "registry_sha256": sha(REGISTRY),
        "registry_acceptance_path": rel(REGISTRY_ACCEPTANCE),
        "registry_acceptance_sha256": sha(REGISTRY_ACCEPTANCE),
        "query_window": {"from": "per_candidate", "to": TO_TS, "target_from": FROM_TS, "limit": LIMIT, "showResumeKey": True, "collapse": False, "matchType": "prefix"},
        "index_only": True,
        "payload_replay": False,
        "no_filename_guess": True,
        "policy": {
            "from": "per_candidate", "to": TO_TS, "target_from": FROM_TS, "limit": LIMIT, "showResumeKey": True,
            "collapse": False, "matchType": "prefix", "max_attempts": 8,
            "window_seconds": 180.0, "max_total_body_bytes": 16 * 1024 * 1024,
            "max_entity_body_bytes": 8 * 1024 * 1024, "min_dispatch_seconds": 5.25,
            "min_request_start_seconds": 5.0, "disk_floor_bytes": 11_005_853_696,
            "direct_first": True, "proxy": "http://127.0.0.1:7890", "tls_verification": True,
            "automatic_redirects": 0, "stop_http_codes": [429, 503],
            "cooldown_seconds": 120, "stop_on_five_consecutive_transport_failures": True,
            "resume_rule": "record resumeKey and mark incomplete; never follow it in this batch",
        },
        "prior_failure_tail": 0,
        "control_basis": {
            "latest_image_source_acceptance": rel(LATEST_SOURCE),
            "latest_image_source_acceptance_sha256": sha(LATEST_SOURCE),
            "latest_control_gate": rel(CONTROL_GATE),
            "latest_control_gate_sha256": sha(CONTROL_GATE),
            "tail": 0,
        },
        "prior_window_check": {
            "requested_window": {"from": FROM_TS, "to": TO_TS},
            "exact_target_complete_for_any": False,
            "overlap_exists": {name: bool(gap_summary[name]["excluded_complete_intervals"]) for name in TARGETS},
            "gap_summary": gap_summary,
            "evidence": prior_coverage,
        },
        "input_bindings": bindings,
        "fixture": {"path": rel(FIXTURE), "sha256": None, "all_passed": None, "network_requests": 0},
        "driver_path": rel(DRIVER),
        "candidates": candidates,
    }
    write(PLAN, plan)
    spec = importlib.util.spec_from_file_location("gallery_late_window_driver", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load late-window driver")
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    fixture = driver.fixture()
    write(FIXTURE, fixture)
    if not fixture.get("all_passed"):
        raise RuntimeError("late-window fixture failed")
    plan["fixture"] = {"path": rel(FIXTURE), "sha256": sha(FIXTURE), "all_passed": True, "network_requests": 0}
    write(PLAN, plan)
    prepared_bindings = {
        "schema": "wow-recovery.gallery-late-window-prepared-bindings.v1",
        "batch_id": plan["batch_id"],
        "plan_path": rel(PLAN),
        "plan_sha256": sha(PLAN),
        "driver_path": rel(DRIVER),
        "driver_sha256": sha(DRIVER),
        "fixture_path": rel(FIXTURE),
        "fixture_sha256": sha(FIXTURE),
        "source_bindings": bindings,
        "network_requests_during_preparation": 0,
    }
    write(BINDINGS, prepared_bindings)
    manifest = {
        "schema": "wow-recovery.gallery-late-window-plan-manifest.v1",
        "batch_id": plan["batch_id"],
        "network_requests": 0,
        "plan": {"path": rel(PLAN), "sha256": sha(PLAN)},
        "bindings": {"path": rel(BINDINGS), "sha256": sha(BINDINGS)},
        "fixture": {"path": rel(FIXTURE), "sha256": sha(FIXTURE), "all_passed": True},
        "driver": {"path": rel(DRIVER), "sha256": sha(DRIVER)},
        "scope": plan["scope"],
        "requires_parent_go": True,
    }
    write(MANIFEST, manifest)
    print(json.dumps({"plan": rel(PLAN), "plan_sha256": sha(PLAN), "bindings": rel(BINDINGS), "bindings_sha256": sha(BINDINGS), "fixture_sha256": sha(FIXTURE), "driver_sha256": sha(DRIVER), "network_requests": 0, "candidate_count": len(candidates), "galleries": TARGETS}, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create the offline-only Batch-B gallery prefix registry v2.

This file deliberately creates a new artifact.  It never edits the accepted v1
registry and it never performs a network request.  The input plan is the source
of truth for the ten candidate prefixes, their source-page literals, query
windows, and execution policy.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PLAN_REL = Path("research/continuous-recovery-20261016/network/gallery-prefix-plan/prefix-plan.json")
OLD_REL = Path(
    "research/continuous-recovery-20261016/local-audit/gallery-prefix-registry/gallery-prefix-registry.json"
)
OUT_DIR_REL = Path("research/continuous-recovery-20261016/local-audit/gallery-prefix-registry")
OUT_REL = OUT_DIR_REL / "gallery-prefix-registry-v2.json"
MD_REL = OUT_DIR_REL / "gallery-prefix-registry-v2.md"
VERIFY_REL = OUT_DIR_REL / "verification-v2.json"
EXPECTED_PLAN_SHA = "70210c7259a1057847b927a0d21a3ed2ae044442fdf187ce164f500c0974faf6"
EXPECTED_OLD_SHA = "d356992afb97633801f69aeb9c0a9e2a3ee933acd812d7cda386ad40a9aa51da"
DISK_FLOOR = 11005853696


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_and_validate_plan(root: Path) -> tuple[dict[str, Any], Path, Path]:
    plan_path = root / PLAN_REL
    old_path = root / OLD_REL
    if not plan_path.is_file():
        fail(f"missing plan: {plan_path}")
    if not old_path.is_file():
        fail(f"missing frozen v1 registry: {old_path}")
    plan_sha = sha256(plan_path)
    if plan_sha != EXPECTED_PLAN_SHA:
        fail(f"plan SHA changed: {plan_sha} != {EXPECTED_PLAN_SHA}")
    old_sha = sha256(old_path)
    if old_sha != EXPECTED_OLD_SHA:
        fail(f"frozen v1 registry SHA changed: {old_sha} != {EXPECTED_OLD_SHA}")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("schema") != "wow-recovery.gallery-prefix-index-plan.v1":
        fail(f"unexpected plan schema: {plan.get('schema')!r}")
    if plan.get("mode") != "offline_plan_only":
        fail(f"plan is not offline_plan_only: {plan.get('mode')!r}")
    if plan.get("network_requests") != 0:
        fail(f"plan network_requests is not zero: {plan.get('network_requests')!r}")
    if plan.get("execution_requires_parent_go") is not True:
        fail("plan does not require parent GO")
    candidates = plan.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 10:
        fail(f"expected ten candidates, got {len(candidates) if isinstance(candidates, list) else None}")
    if [c.get("rank") for c in candidates] != list(range(1, 11)):
        fail("candidate ranks are not exactly 1..10")
    for candidate in candidates:
        if candidate.get("local_audit_status_counts") != {"never_requested": candidate.get("declared_entity_count")}:  # noqa: E501
            fail(f"candidate {candidate.get('label')} has unexpected local audit status counts")
        for key in ("prefix", "source_directory", "source_page", "cdx_query_url", "selection", "truncation_rule"):
            if key not in candidate:
                fail(f"candidate {candidate.get('label')} is missing {key}")
    for binding in plan.get("input_bindings", []):
        input_path = root / binding["path"]
        if not input_path.is_file():
            fail(f"missing plan input binding: {input_path}")
        actual_sha = sha256(input_path)
        if actual_sha != binding["sha256"]:
            fail(f"input binding SHA changed: {binding['path']}: {actual_sha} != {binding['sha256']}")
        if input_path.stat().st_size != binding["bytes"]:
            fail(f"input binding size changed: {binding['path']}")
    return plan, plan_path, old_path


def make_registry(root: Path, plan: dict[str, Any], plan_path: Path, old_path: Path) -> dict[str, Any]:
    candidates = copy.deepcopy(plan["candidates"])
    expected_entities = sum(int(c["declared_entity_count"]) for c in candidates)
    expected_full = sum(int(c["declared_full_count"]) for c in candidates)
    expected_thumb = sum(int(c["declared_thumb_count"]) for c in candidates)
    categories: dict[str, int] = {}
    for c in candidates:
        categories[c["category"]] = categories.get(c["category"], 0) + 1

    return {
        "schema": "wow-recovery.gallery-prefix-registry.v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "network_performed": False,
        "execution_status": "not_executed",
        "mode": "offline_plan_only",
        "parent_go_required": True,
        "scope": {
            "batch_id": plan["batch_id"],
            "source_gallery_count": plan["source_entity_count"],
            "candidate_count": len(candidates),
            "candidate_entity_count": expected_entities,
            "candidate_full_count": expected_full,
            "candidate_thumb_count": expected_thumb,
            "source_entity_scope": "3368 direct full/thumb entities; this v2 artifact binds only the ten pending Batch-B prefixes",
            "known_scope_excluded": [
                "Karazhan and Fishing prefix evidence already saved in discovery-002; not repeated",
                "Black Temple, Serpentshrine Cavern, and Magister's Terrace accepted by NET015; not repeated",
                "REG01 EU origin is a separate www.wow-europe.com origin and is not mixed into this www.worldofwarcraft.com registry",
                "nested guide previews, parent directory rows, and sibling guide resources are not promoted to dynamic direct entities",
            ],
            "status_boundary": "Candidate local_audit_status_counts are report-local states from the bound audit; never_requested is not a global request-history assertion.",
        },
        "input_hashes": [
            {
                "path": rel(root, plan_path),
                "bytes": plan_path.stat().st_size,
                "sha256": sha256(plan_path),
                "role": "exact Batch-B ten-prefix plan",
            },
            *copy.deepcopy(plan["input_bindings"]),
            {
                "path": rel(root, old_path),
                "bytes": old_path.stat().st_size,
                "sha256": sha256(old_path),
                "role": "frozen v1 registry integrity anchor; not modified",
            },
        ],
        "plan_binding": {
            "path": rel(root, plan_path),
            "sha256": sha256(plan_path),
            "schema": plan["schema"],
            "batch_id": plan["batch_id"],
            "network_requests": plan["network_requests"],
            "execution_requires_parent_go": plan["execution_requires_parent_go"],
            "candidate_count": plan["candidate_count"],
            "source_entity_count": plan["source_entity_count"],
        },
        "origin_and_window_boundary": {
            "original_origin_host": "www.worldofwarcraft.com",
            "original_schemes": ["http"],
            "query_host": "web.archive.org",
            "date_window": {"from": plan["policy"]["from"], "to": plan["policy"]["to"]},
            "selection_boundary": "preserve each candidate's exact original http scheme, www.worldofwarcraft.com host, and path prefix; actual returned CDX rows only",
            "valid_row_boundary": "statuscode=200 and image/jpeg or image/gif; no payload replay in this index-only batch",
            "truncation_boundary": "if actual rows reach limit=500, preserve the actual response resumeKey and mark potential_truncation; do not claim complete/latest or replay",
        },
        "execution_boundary": {
            "network_requests": 0,
            "response_rows": 0,
            "payloads_replayed": 0,
            "payloads_available": False,
            "prefix_rows_status": "unknown_until_parent_go",
            "direct_entity_rows_status": "unknown_until_parent_go",
            "resume_key": "none observed because no request was executed",
            "no_network_or_payload_claim": True,
        },
        "policy": copy.deepcopy(plan["policy"]),
        "excluded_existing_prefixes": copy.deepcopy(plan["excluded_existing_prefixes"]),
        "source_limit": copy.deepcopy(plan["source_limit"]),
        "candidates": candidates,
        "stats": {
            "candidate_count": len(candidates),
            "candidate_entity_count": expected_entities,
            "declared_full_count": expected_full,
            "declared_thumb_count": expected_thumb,
            "category_counts": categories,
            "local_audit_status_counts": {"never_requested": expected_entities},
            "prefix_execution_status_counts": {"not_executed": len(candidates)},
            "actual_response_row_count": 0,
            "actual_direct_entity_row_count": 0,
            "actual_payload_count": 0,
        },
        "notes": [
            "This is an independent v2 registration of exactly the ten candidates in the supplied Batch-B plan; the accepted v1 registry remains frozen.",
            "All ten candidates are offline plan entries only. Their CDX rows, response status, direct entity rows, resume keys, and payloads remain unknown until a parent-approved execution.",
            "The plan's never_requested counts are retained as prior local audit state and do not establish global request history.",
            "The original HTTP origin, archive query host, date window, response filters, truncation rule, and no-payload-replay boundary are preserved verbatim from the plan.",
        ],
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def make_markdown(root: Path, registry: dict[str, Any]) -> str:
    s = registry["stats"]
    lines = [
        "# Gallery prefix registry v2 (offline Batch-B registration)",
        "",
        f"- Schema: `{registry['schema']}`",
        f"- Batch: `{registry['scope']['batch_id']}`",
        f"- Status: `{registry['execution_status']}`; network requests: `{registry['execution_boundary']['network_requests']}`",
        f"- Candidate prefixes: `{s['candidate_count']}`; declared entities: `{s['candidate_entity_count']}` (`{s['declared_full_count']}` full + `{s['declared_thumb_count']}` thumb)",
        f"- Plan: `{registry['plan_binding']['path']}`; SHA-256 `{registry['plan_binding']['sha256']}`",
        "- The accepted v1 registry is an integrity anchor only and is not edited by this artifact.",
        "",
        "## Fixed evidence boundary",
        "",
        "The exact original HTTP origin and path prefixes, `web.archive.org` CDX query host, 2006-01-01 through 2008-05-12 window, status-200 image/jpeg or image/gif selection, limit 500, resume-key rule, and no-payload-replay rule are preserved from the supplied plan. Rows and payloads are unknown until parent-approved execution.",
        "",
        "## Ten pending candidates",
        "",
        "| Rank | Candidate | Category | Prefix | Declared full/thumb | Prior local status | Source evidence | CDX query |",
        "|---:|---|---|---|---:|---|---|---|",
    ]
    for c in registry["candidates"]:
        lines.append(
            f"| {c['rank']} | {c['label']} | {c['category']} | `{c['prefix']}` | {c['declared_full_count']}/{c['declared_thumb_count']} | `not_executed`; `{c['local_audit_status_counts']}` report-local | `{c['source_page']['path']}:{c['source_page']['line']}` | `{c['cdx_query_url']}` |"
        )
    lines.extend(
        [
            "",
            "## Exclusions",
            "",
            "Existing Karazhan, Fishing, Black Temple, Serpentshrine Cavern, and Magister's Terrace prefix evidence is excluded from this pending batch. REG01 EU rows remain separate by origin and are not mixed into the US 50-gallery entity set.",
            "",
            "## Execution gate",
            "",
            "`execution_requires_parent_go=true`. This artifact contains no CDX response rows, resume keys, payload bytes, or recovery claims.",
            "",
        ]
    )
    return "\n".join(lines)


def make_verification(root: Path, plan_path: Path, old_path: Path, out_path: Path, md_path: Path, registry: dict[str, Any]) -> dict[str, Any]:
    plan_sha = sha256(plan_path)
    old_sha_before = sha256(old_path)
    registry_sha = sha256(out_path)
    md_sha = sha256(md_path)
    free_bytes = shutil.disk_usage(root).free
    candidates = registry["candidates"]
    forbidden_observation_keys = [
        key
        for key in registry.get("execution_boundary", {})
        if key in {"response_rows_data", "payloads", "replayed_payloads"}
    ]
    checks = {
        "plan_sha256_expected": plan_sha == EXPECTED_PLAN_SHA,
        "old_registry_sha256_expected_before": old_sha_before == EXPECTED_OLD_SHA,
        "candidate_count_10": len(candidates) == 10,
        "ranks_exact_1_to_10": [c.get("rank") for c in candidates] == list(range(1, 11)),
        "all_execution_status_not_executed": registry["execution_status"] == "not_executed" and all(registry["execution_status"] == "not_executed" for _ in candidates),
        "network_requests_zero": registry["execution_boundary"]["network_requests"] == 0,
        "response_rows_zero": registry["execution_boundary"]["response_rows"] == 0,
        "payload_replay_zero": registry["execution_boundary"]["payloads_replayed"] == 0,
        "payloads_unavailable": registry["execution_boundary"]["payloads_available"] is False,
        "no_forbidden_payload_data_keys": not forbidden_observation_keys,
        "aggregate_entities_1052": registry["stats"]["candidate_entity_count"] == 1052,
        "aggregate_full_526": registry["stats"]["declared_full_count"] == 526,
        "aggregate_thumb_526": registry["stats"]["declared_thumb_count"] == 526,
        "local_status_count_1052_report_local": registry["stats"]["local_audit_status_counts"] == {"never_requested": 1052},
        "prefix_status_not_executed_10": registry["stats"]["prefix_execution_status_counts"] == {"not_executed": 10},
        "plan_binding_exact": registry["plan_binding"]["sha256"] == EXPECTED_PLAN_SHA and registry["plan_binding"]["candidate_count"] == 10,
        "disk_free_above_floor": free_bytes >= DISK_FLOOR,
    }
    old_sha_after = sha256(old_path)
    checks["old_registry_unchanged_after"] = old_sha_after == old_sha_before == EXPECTED_OLD_SHA
    return {
        "schema": "wow-recovery.gallery-prefix-registry-v2.verification.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "network_performed": False,
        "command_scope": "offline local plan registration and static integrity verification only",
        "artifacts": {
            "registry": {"path": rel(root, out_path), "sha256": registry_sha, "bytes": out_path.stat().st_size},
            "markdown": {"path": rel(root, md_path), "sha256": md_sha, "bytes": md_path.stat().st_size},
            "plan": {"path": rel(root, plan_path), "sha256": plan_sha, "bytes": plan_path.stat().st_size},
            "old_registry": {"path": rel(root, old_path), "sha256_before": old_sha_before, "sha256_after": old_sha_after, "bytes": old_path.stat().st_size},
        },
        "counts": {
            "candidate_count": len(candidates),
            "declared_entities": registry["stats"]["candidate_entity_count"],
            "declared_full": registry["stats"]["declared_full_count"],
            "declared_thumb": registry["stats"]["declared_thumb_count"],
            "actual_response_rows": registry["stats"]["actual_response_row_count"],
            "actual_payloads": registry["stats"]["actual_payload_count"],
        },
        "disk": {"free_bytes": free_bytes, "floor_bytes": DISK_FLOOR, "above_floor": free_bytes >= DISK_FLOOR},
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "limitations": [
            "No network request was made; all ten prefix results remain unknown until parent GO.",
            "The plan-local never_requested values are not interpreted as a global request-history result.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    root = args.root.resolve()
    out_dir = root / OUT_DIR_REL
    out_path = root / OUT_REL
    md_path = root / MD_REL
    verify_path = root / VERIFY_REL
    for p in (out_path, md_path, verify_path):
        if p.exists():
            fail(f"refusing to overwrite existing v2 artifact: {p}")
    plan, plan_path, old_path = load_and_validate_plan(root)
    registry = make_registry(root, plan, plan_path, old_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_path, registry)
    md_path.write_text(make_markdown(root, registry), encoding="utf-8", newline="\n")
    verification = make_verification(root, plan_path, old_path, out_path, md_path, registry)
    write_json(verify_path, verification)
    if not verification["all_checks_pass"]:
        fail(f"verification failed: {verification['checks']}")
    print(json.dumps({
        "registry": rel(root, out_path),
        "registry_sha256": verification["artifacts"]["registry"]["sha256"],
        "markdown": rel(root, md_path),
        "markdown_sha256": verification["artifacts"]["markdown"]["sha256"],
        "verification": rel(root, verify_path),
        "all_checks_pass": verification["all_checks_pass"],
        "candidate_count": verification["counts"]["candidate_count"],
        "declared_entities": verification["counts"]["declared_entities"],
        "network_performed": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

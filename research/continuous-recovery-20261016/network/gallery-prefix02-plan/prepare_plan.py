from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[4]
REG_PATH = ROOT / "research/continuous-recovery-20261016/local-audit/gallery-prefix-registry/gallery-prefix-registry.json"
OUT = ROOT / "research/continuous-recovery-20261016/network/gallery-prefix02-plan"
FROM_TS = "20060101000000"
TO_TS = "20080512210044"
FIELDS = "urlkey,timestamp,original,mimetype,statuscode,digest,length"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def query(prefix: str) -> str:
    return (
        "https://web.archive.org/cdx/search/cdx?url="
        + quote(prefix, safe="")
        + "&matchType=prefix&output=json&fl="
        + quote(FIELDS, safe="")
        + f"&from={FROM_TS}&to={TO_TS}&limit=500&showResumeKey=true"
    )


def binding(key: str, path: Path, role: str) -> tuple[str, dict[str, object]]:
    return key, {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size, "role": role}


def main() -> None:
    registry = json.loads(REG_PATH.read_text(encoding="utf-8"))
    rows = registry["rows"]
    # Registry order is the deterministic selection rule.  These rows are the
    # first ten eligible after the prior-prefix/historical exclusions.
    chosen_indices = [2, 3, 5, 6, 8, 10, 11, 13, 14, 15]
    excluded_success = [
        "City Attacks", "Warsong Gulch", "Hallow's End", "Brewfest",
        "Zul'Aman", "Hellfire Citadel - The Shattered Halls",
        "Tempest Keep - The Arcatraz", "Isle of Quel'Danas", "TCG Gallery",
    ]
    historical = ["Karazhan", "Fishing", "Black Temple", "Serpentshrine Cavern", "Magister's Terrace"]
    source_bindings = dict([
        binding("registry", REG_PATH, "50-gallery prefix registry"),
        binding("direct_entity_audit", ROOT / "research/continuous-recovery-20261016/local-audit/v2/gallery-direct-entity-audit-v2.json", "3368 direct full/thumb entity status join"),
        binding("route_inventory", ROOT / "research/local-maintenance-20261014/gallery-route-entity-recheck.json", "50-gallery addshots route/slot inventory"),
        binding("prior_gallery_prefix01_report", ROOT / "research/continuous-recovery-20261016/network/gallery-prefix01/batch-report.json", "frozen prior prefix execution and tail=2"),
        binding("prior_gallery_prefix01_source_map", ROOT / "research/continuous-recovery-20261016/network/gallery-prefix01/source-map.json", "frozen prior index-only results"),
        binding("prior_gallery_prefix01_deviation", ROOT / "research/continuous-recovery-20261016/network/gallery-prefix01/execution-deviation.json", "frozen cadence deviation diagnosis"),
    ])
    prior = json.loads((ROOT / source_bindings["prior_gallery_prefix01_report"]["path"]).read_text(encoding="utf-8"))
    if prior.get("failure_streak") != 2:
        raise RuntimeError("frozen GALLERYPREFIX01 tail is not 2")

    candidates: list[dict[str, object]] = []
    for batch_rank, idx in enumerate(chosen_indices, 1):
        row = rows[idx]
        source = row["source_evidence"]
        source_dir = source["source_directory"]
        prefix = "http://www.worldofwarcraft.com" + source_dir
        identity_variants = []
        for scheme, host in (("http", "www.worldofwarcraft.com"), ("https", "www.worldofwarcraft.com"), ("http", "worldofwarcraft.com"), ("https", "worldofwarcraft.com")):
            identity_variants.append({
                "variant_key": f"{scheme}://{host}",
                "base_url": f"{scheme}://{host}{source_dir}",
                "full_pattern": f"{scheme}://{host}{source_dir}ssN.jpg",
                "thumb_pattern": f"{scheme}://{host}{source_dir}ssN-thumb.jpg",
                "scheme": scheme,
                "host": host,
                "identity_status": "distinct_exact_original_candidate",
                "automatic_alias": False,
                "replay_requires_exact_memento_and_digest": True,
            })
        candidates.append({
            "rank": batch_rank,
            "registry_rank": idx + 1,
            "target_key": f"GALLERY-PREFIX02-{batch_rank:02d}",
            "label": row["gallery"],
            "category": row["category"],
            "prefix": prefix,
            "source_directory": source_dir,
            "identity_variants": identity_variants,
            "filename_literal": source["filename_literal"],
            "full_pattern": source_dir + "ssN.jpg",
            "thumb_pattern": source_dir + "ssN-thumb.jpg",
            "declared_slots": row["declared_slots"],
            "expected_full_count": row["declared_slots"],
            "expected_thumb_count": row["declared_slots"],
            "expected_direct_entities": row["expected_direct_entities"],
            "source_page": {
                "path": source["path"],
                "sha256": source["sha256"],
                "addshots_line": source["addshots_line"],
                "addshots_literal": source["addshots_literal"],
                "source_directory": source_dir,
                "filename_literal": source["filename_literal"],
                "numShots_line": source["numShots_line"],
                "numShots_literal": source["numShots_literal"],
            },
            "registry_reference": {
                "path": rel(REG_PATH),
                "sha256": sha(REG_PATH),
                "row_number": idx + 1,
                "prefix_review_status": row["prefix_review_status"],
                "entity_audit_status_counts": row["entity_audit_status_counts"],
            },
            "report_references": row["report_references"],
            "query_parameters": {
                "url": prefix, "matchType": "prefix", "output": "json", "fl": FIELDS,
                "from": FROM_TS, "to": TO_TS, "limit": "500", "showResumeKey": "true",
            },
            "cdx_query_url": query(prefix),
            "selection_reason": "first eligible unreviewed registry row after explicit prior-prefix exclusions; no Amani transport-unknown row included",
        })

    batch_id = "WAYBACK-GALLERYPREFIX02-20261016"
    plan = {
        "schema": "wow-recovery.gallery-prefix02-plan.v1",
        "batch_id": batch_id,
        "prepared_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "offline_plan_only",
        "network_performed": False,
        "execution_status": "prepared",
        "parent_go_required": True,
        "scope": {
            "registry_path": rel(REG_PATH), "registry_sha256": sha(REG_PATH),
            "registry_gallery_count": registry["stats"]["gallery_count"],
            "registry_row_count": len(rows), "source_origin": "http://www.worldofwarcraft.com",
            "exact_identity_rule": "exact scheme/host/path; default HTTP port 80 may be equivalent; no scheme/host/path broadening",
        },
        "selection_rule": "Registry row order after excluding prior GALLERYPREFIX01 success rows, five historical prefix-evidence rows, and Amani transport-unknown; choose first ten remaining rows. This is a plan-only selection, not network evidence.",
        "excluded_existing_prefixes": {
            "gallery_prefix01_success": excluded_success,
            "historical_saved_evidence": historical,
            "deferred_transport_unknown": ["Amani War Bear"],
            "reason": "avoid repeat same prefix and defer unresolved transport; candidate source evidence remains local",
        },
        "candidate_count": 10,
        "expected_full_count": sum(int(c["expected_full_count"]) for c in candidates),
        "expected_thumb_count": sum(int(c["expected_thumb_count"]) for c in candidates),
        "expected_direct_entities": sum(int(c["expected_direct_entities"]) for c in candidates),
        "policy": {
            "max_candidates": 10, "max_attempts": 20, "window_seconds": 900,
            "max_total_body_bytes": 67108864, "max_entity_body_bytes": 16777216,
            "from": FROM_TS, "to": TO_TS, "limit": 500, "showResumeKey": True,
            "collapse": False, "matchType": "prefix", "direct_first": True,
            "proxy": "http://127.0.0.1:7890", "tls_verification": True,
            "automatic_redirects": 0, "min_dispatch_monotonic_seconds": 5.25,
            "acceptance_dispatch_floor_seconds": 5.1,
            "min_request_start_utc_seconds": 5.0, "disk_floor_bytes": 11005853696,
            "stop_http_codes": [429, 503], "stop_on_five_consecutive_transport_failures": True,
            "cooldown_seconds_after_stop": 120,
            "retry_after_rule": "429/503 stop immediately; do not resume before max(Retry-After,120s)",
            "remaining_byte_and_time_clamp": True, "per_request_disk_floor_recorded": True,
            "payload_replay": False, "follow_resume_key": False,
        },
        "inherited_state": {
            "prior_batch_id": prior["batch_id"],
            "prior_batch_finished_utc": prior["finished_utc"],
            "prior_batch_failure_streak": prior["failure_streak"],
            "prior_batch_tail_preserved": 2, "new_batch_streak_start": 2,
            "historical_allnews02_tail_preserved_separately": 5,
        },
        "input_bindings": source_bindings,
        "candidates": candidates,
        "identity_variants": [
            {**variant, "candidate_rank": c["rank"], "registry_rank": c["registry_rank"], "label": c["label"]}
            for c in candidates for variant in c["identity_variants"]
        ],
        "execution_boundary": {
            "no_network_until_parent_go": True, "index_only": True,
            "no_payload_replay": True, "no_pagination": True,
            "no_auto_redirect": True, "stop_after_this_batch": True,
            "no_same_point_repeat": True,
        },
        "identity_variant_policy": {
            "listed_separately": True,
            "variants": "same source path with http/https and www/bare host combinations, direct ssN.jpg and ssN-thumb.jpg patterns",
            "automatic_alias": False,
            "acceptance": "a variant requires its own exact Memento, original identity, CDX digest, and payload validation; prefix rows are index evidence only",
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    selection = {
        "schema": "wow-recovery.gallery-prefix02-selection-map.v1",
        "batch_id": batch_id, "selection_rule": plan["selection_rule"],
        "source_registry": source_bindings["registry"],
        "excluded_existing_prefixes": plan["excluded_existing_prefixes"],
        "candidates": [{
            "rank": c["rank"], "registry_rank": c["registry_rank"], "target_key": c["target_key"],
            "label": c["label"], "category": c["category"], "prefix": c["prefix"],
            "source_page": c["source_page"], "expected_full_count": c["expected_full_count"],
            "expected_thumb_count": c["expected_thumb_count"], "expected_direct_entities": c["expected_direct_entities"],
            "identity_variants": c["identity_variants"],
            "cdx_query_url": c["cdx_query_url"],
        } for c in candidates],
    }
    (OUT / "selection-map.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_sha = sha(OUT / "plan.json")
    bindings = {
        "schema": "wow-recovery.gallery-prefix02-input-bindings.v1", "batch_id": batch_id,
        "plan_path": rel(OUT / "plan.json"), "plan_sha256": plan_sha,
        "source_bindings": source_bindings,
        "prior_tail_verification": {
            "report_path": source_bindings["prior_gallery_prefix01_report"]["path"],
            "reported_failure_streak": prior["failure_streak"],
            "reported_finished_utc": prior["finished_utc"], "inherited_nonzero_tail": True,
        },
    }
    (OUT / "input-bindings.json").write_text(json.dumps(bindings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme = """# GALLERYPREFIX02 offline plan

This directory is a plan-only artifact. It contains ten exact http://www.worldofwarcraft.com prefix candidates selected from the frozen 50-row registry after explicit prior-prefix exclusions. The plan performs no CDX request, follows no resume key, and replays no payload.

The later execution must use the v3 driver only after parent GO. It inherits the frozen GALLERYPREFIX01 trailing transport-failure count of 2 as evidence; a successful source response may reset the current window streak, but the prior tail remains in the receipt.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({"plan": rel(OUT / "plan.json"), "plan_sha256": plan_sha, "candidate_count": len(candidates), "expected_full_count": plan["expected_full_count"], "expected_thumb_count": plan["expected_thumb_count"], "expected_direct_entities": plan["expected_direct_entities"], "registry_sha256": sha(REG_PATH)}, ensure_ascii=False))
    for c in candidates:
        print(c["rank"], c["registry_rank"], c["label"], c["prefix"], c["expected_full_count"])


if __name__ == "__main__":
    main()

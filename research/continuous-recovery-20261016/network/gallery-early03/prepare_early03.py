"""Prepare-only EARLY03: four exact saved transport-unknown CDX retries."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(r"D:\WOW_Encyclopedia")
BASE = ROOT / "research" / "continuous-recovery-20261016"
NETWORK = BASE / "network"
OUT = NETWORK / "gallery-early03"
DRIVER = OUT / "gallery_prefix_driver_v6.py"
SOURCE = BASE / "local-audit" / "gallery-followup-plans" / "early-gaps-24-v1.json"
FOLLOWUP = BASE / "publication" / "root-gallery-followups-acceptance.json"
REGISTRY = BASE / "local-audit" / "gallery-prefix-registry-v5" / "gallery-prefix-registry-v5.json"
FROM_TS = "20000101000000"
LIMIT = 500


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def binding(path: Path, role: str) -> dict[str, object]:
    return {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size, "role": role}


def cdx_url(prefix: str, to_ts: str) -> str:
    fields = "urlkey,timestamp,original,mimetype,statuscode,digest,length"
    return (
        "https://web.archive.org/cdx/search/cdx?url="
        + quote(prefix, safe="")
        + "&matchType=prefix&output=json&fl="
        + quote(fields, safe="")
        + f"&from={FROM_TS}&to={to_ts}&limit={LIMIT}&showResumeKey=true"
    )


def patch_driver() -> None:
    text = DRIVER.read_text(encoding="utf-8")
    # The preparer may be rerun after a plan-only correction.  The first run
    # already replaced the v6 validation/fixture gates; do not try to locate
    # the pre-patch gate again and accidentally rewrite the adapted driver.
    if (
        "exact four saved-query transport-unknown retry targets offline" in text
        and "retry_plan_four_saved_unknown_queries" in text
        and "inherited_tail_two_three_new_failures_stop" in text
    ):
        return
    start = text.index("def validate_inputs()")
    end = text.index("\n\nclass _FixtureClock", start)
    validate = r'''def validate_inputs() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """Validate the exact four saved-query transport-unknown retry targets offline."""
    plan = read_json(PLAN_PATH, {})
    if plan.get("schema") != "wow-recovery.gallery-early03-plan.v1":
        raise RuntimeError("unsupported early03 plan schema")
    candidates = plan.get("candidates") or []
    policy = plan.get("policy") or {}
    if plan.get("candidate_count") != 4 or len(candidates) != 4:
        raise RuntimeError("early03 plan is not exactly four retry candidates")
    expected_policy = {
        "from": FROM_TS, "to": "per_item_source_window", "limit": LIMIT,
        "showResumeKey": True, "collapse": False, "matchType": "prefix",
        "max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW_SECONDS,
        "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "min_dispatch_seconds": MIN_DISPATCH_SECONDS,
        "min_request_start_seconds": MIN_REQUEST_START_SECONDS,
        "disk_floor_bytes": DISK_FLOOR_BYTES, "direct_first": True,
        "tls_verification": True, "automatic_redirects": 0,
        "payload_replay": False, "prior_failure_tail": PRIOR_FAILURE_TAIL,
    }
    if any(policy.get(key) != value for key, value in expected_policy.items()):
        raise RuntimeError("early03 policy mismatch")
    if policy.get("proxy") != PROXY or policy.get("stop_http_codes") != [429, 503]:
        raise RuntimeError("early03 transport policy mismatch")
    if policy.get("stop_after_new_transport_failures") != 3:
        raise RuntimeError("early03 inherited-tail stop policy mismatch")
    bindings: dict[str, Any] = {}
    for key, entry in (plan.get("input_bindings") or {}).items():
        if not isinstance(entry, dict) or not entry.get("path") or not entry.get("sha256"):
            raise RuntimeError(f"invalid input binding {key}")
        path = ROOT / str(entry["path"])
        if not path.is_file():
            raise RuntimeError(f"input missing {key}: {path}")
        actual = sha(path)
        if actual != str(entry["sha256"]):
            raise RuntimeError(f"input SHA mismatch {key}: {actual}")
        bindings[key] = {"path": rel(path), "sha256": actual, "bytes": path.stat().st_size, "role": entry.get("role")}
    required = {
        "early_gap_plan", "root_gallery_followups_acceptance", "gallery_registry_v5",
        "root_gallery_early01_acceptance", "gallery_early01_batch_report",
        "gallery_early01_source_map", "gallery_early01_execution_plan",
        "root_gallery_early02_acceptance", "gallery_early02_batch_report",
        "gallery_early02_source_map", "gallery_early02_execution_plan",
        "root_gallery_prefix05_acceptance", "gallery_prefix05_driver_v5", "gallery_prefix05_fixture",
    }
    if not required.issubset(bindings):
        raise RuntimeError(f"required bindings missing: {sorted(required - set(bindings))}")
    source_entry = bindings["early_gap_plan"]
    source_path = ROOT / source_entry["path"]
    source_plan = read_json(source_path, {})
    if sha(source_path) != str(plan.get("source_plan_sha256") or "") or rel(source_path) != str(plan.get("source_plan_path") or ""):
        raise RuntimeError("early-gap source plan path/SHA mismatch")
    source_items = source_plan.get("items") or []
    if source_plan.get("schema") != "gallery-followup-plan-v1" or source_plan.get("count") != 24 or len(source_items) != 24:
        raise RuntimeError("bound early-gap plan is not the accepted 24-item source")
    followup = read_json(ROOT / bindings["root_gallery_followups_acceptance"]["path"], {})
    if followup.get("accepted") is not True or followup.get("early_gap_plan_sha256") != sha(source_path) or followup.get("early_batches") != [20, 4]:
        raise RuntimeError("root early-gap acceptance is not bound to the 20+4 source")
    registry_path = ROOT / bindings["gallery_registry_v5"]["path"]
    if source_plan.get("source_registry", {}).get("sha256") != sha(registry_path):
        raise RuntimeError("source registry SHA mismatch")
    latest = read_json(ROOT / bindings["root_gallery_early02_acceptance"]["path"], {})
    if latest.get("accepted") is not True or latest.get("failure_streak_end") != LATEST_TAIL:
        raise RuntimeError("latest EARLY02 source receipt does not bind tail two")
    if latest.get("batch_report_sha256") != plan.get("previous_batch", {}).get("latest_batch_report_sha256"):
        raise RuntimeError("latest EARLY02 report SHA is not bound")
    if plan.get("prior_failure_tail") != PRIOR_FAILURE_TAIL or plan.get("latest_tail_value") != LATEST_TAIL:
        raise RuntimeError("early03 prior/latest tail mismatch")
    latest_basis = plan.get("latest_tail_basis") or {}
    if latest_basis.get("path") != bindings["root_gallery_early02_acceptance"]["path"] or latest_basis.get("sha256") != bindings["root_gallery_early02_acceptance"]["sha256"]:
        raise RuntimeError("early03 latest-tail receipt binding mismatch")
    if plan.get("historical_gallery_tail") != HISTORICAL_GALLERY_TAIL or plan.get("historical_gallery_tail_preserved") != HISTORICAL_GALLERY_TAIL:
        raise RuntimeError("early03 historical gallery tail mismatch")
    source_by_registry = {int(item["registry_rank"]): item for item in source_items}
    expected_registry = [7, 12, 14, 38]
    if plan.get("retry_scope", {}).get("registry_ranks") != expected_registry:
        raise RuntimeError("early03 retry registry scope changed")
    if plan.get("retry_scope", {}).get("saved_batch_ranks") != {"EARLY01": [6, 9, 11], "EARLY02": [4]}:
        raise RuntimeError("early03 saved batch-rank scope changed")
    normalized: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    seen_origins: set[tuple[str, int]] = set()
    for rank, candidate in enumerate(candidates, 1):
        retry = candidate.get("retry_source") or {}
        original_rank = int(retry.get("original_rank") or 0)
        origin_key = (str(retry.get("batch_id")), int(retry.get("rank") or 0))
        if original_rank not in expected_registry or origin_key in seen_origins:
            raise RuntimeError(f"unsafe or duplicate retry source: {candidate.get('target_key')!r}")
        seen_origins.add(origin_key)
        source_item = source_by_registry.get(original_rank)
        if source_item is None:
            raise RuntimeError(f"retry source registry rank missing: {original_rank}")
        for field in ("registry_rank", "gallery", "category", "source_page_route", "declared_slots", "expected_direct_entities", "prefix", "followup_group", "reason"):
            if candidate.get(field) != source_item.get(field):
                raise RuntimeError(f"candidate does not equal source item {rank}:{field}")
        prefix = str(candidate.get("prefix") or "")
        parsed_prefix = urlsplit(prefix)
        if parsed_prefix.scheme != "http" or parsed_prefix.hostname != "www.worldofwarcraft.com" or parsed_prefix.port not in (None, 80) or not parsed_prefix.path.endswith("/") or parsed_prefix.query or parsed_prefix.fragment:
            raise RuntimeError(f"candidate origin widened or malformed: {prefix!r}")
        source = candidate.get("source_evidence") or {}
        source_expected = source_item.get("source_evidence") or {}
        for field in ("path", "sha256", "addshots_line", "addshots_literal", "source_directory", "filename_literal", "numShots_line", "numShots_literal"):
            if source.get(field) != source_expected.get(field):
                raise RuntimeError(f"candidate source evidence mismatch {rank}:{field}")
        source_page = ROOT / str(source.get("path") or "")
        if not source_page.is_file() or sha(source_page) != str(source.get("sha256") or ""):
            raise RuntimeError(f"candidate source hash mismatch: {candidate.get('target_key')!r}")
        lines = source_page.read_text(encoding="iso-8859-1", errors="replace").splitlines()
        add_line, num_line = int(source.get("addshots_line") or 0), int(source.get("numShots_line") or 0)
        if add_line < 1 or num_line < 1 or add_line > len(lines) or num_line > len(lines):
            raise RuntimeError(f"candidate source line out of range: {candidate.get('target_key')!r}")
        if str(source.get("addshots_literal")) not in lines[add_line - 1] or str(source.get("numShots_literal")) not in lines[num_line - 1]:
            raise RuntimeError(f"candidate source literal missing: {candidate.get('target_key')!r}")
        if source.get("source_directory") != parsed_prefix.path or source.get("filename_literal") != "ss":
            raise RuntimeError(f"candidate source literal mismatch: {candidate.get('target_key')!r}")
        key = str(candidate.get("target_key") or "")
        if not re.fullmatch(r"GALLERY-EARLY03-[0-9]{2}", key) or key in seen_keys:
            raise RuntimeError(f"unsafe or duplicate target key: {key!r}")
        seen_keys.add(key)
        source_window = source_item.get("query_window") or {}
        candidate_window = candidate.get("query_window") or {}
        if candidate_window != source_window or candidate_window != retry.get("query_window") or candidate_window.get("from") != FROM_TS or candidate_window.get("limit") != LIMIT or candidate_window.get("showResumeKey") is not True or candidate_window.get("collapse") is not False or candidate_window.get("matchType") != "prefix":
            raise RuntimeError(f"saved query window mismatch: {key}")
        query_url = str(candidate.get("cdx_query_url") or "")
        if query_url != str(retry.get("query_url") or "") or query_url != canonical_query_url(prefix, FROM_TS, str(candidate_window.get("to") or "")):
            raise RuntimeError(f"saved exact query mismatch: {key}")
        report_key = "gallery_early01_batch_report" if retry.get("batch_id") == "WAYBACK-GALLERYEARLY01-20261016" else "gallery_early02_batch_report"
        report = read_json(ROOT / bindings[report_key]["path"], {})
        result = next((x for x in report.get("candidate_results", []) if int(x.get("rank") or 0) == int(retry.get("rank") or 0)), None)
        if result is None or result.get("status") != "transport_or_parse_unknown" or result.get("source_response_count") != 0 or result.get("query_url") != query_url or result.get("query_window") != candidate_window:
            raise RuntimeError(f"saved retry report evidence mismatch: {key}")
        if retry.get("report_sha256") != bindings[report_key]["sha256"]:
            raise RuntimeError(f"saved retry report SHA mismatch: {key}")
        normalized_item = dict(candidate)
        normalized_item.update({"rank": rank, "target_key": key, "label": candidate.get("label") or candidate.get("gallery") or f"candidate-{rank:02d}", "category": candidate.get("category") or "root-gallery-retry", "cdx_query_url": query_url, "source_directory": source.get("source_directory"), "declared_entity_count": candidate.get("declared_slots"), "query_window": candidate_window, "retry_source": retry})
        normalized.append(normalized_item)
    if {(x["retry_source"]["batch_id"], int(x["retry_source"]["rank"])) for x in normalized} != {
        ("WAYBACK-GALLERYEARLY01-20261016", 6),
        ("WAYBACK-GALLERYEARLY01-20261016", 9),
        ("WAYBACK-GALLERYEARLY01-20261016", 11),
        ("WAYBACK-GALLERYEARLY02-20261016", 4),
    }:
        raise RuntimeError("early03 retry union changed")
    return plan, normalized, bindings
'''
    text = text[:start] + validate + text[end:]
    gate_start = text.index("    # The remaining four-item plan is checked offline")
    gate_end = text.index('    passed = sum(int(x["passed"]) for x in results)', gate_start)
    gate = r'''    # The four saved-query retry targets are checked offline; no fixture path invokes curl.
    try:
        prepared_plan, prepared_candidates, _ = validate_inputs()
        plan_gate = {
            "candidate_count": len(prepared_candidates),
            "all_absolute_http": all(x["prefix"].startswith("http://www.worldofwarcraft.com/") for x in prepared_candidates),
            "from": prepared_plan["policy"]["from"],
            "max_attempts": prepared_plan["policy"]["max_attempts"],
            "max_entity_body_bytes": prepared_plan["policy"]["max_entity_body_bytes"],
            "prior_failure_tail": prepared_plan["policy"]["prior_failure_tail"],
            "saved_unknown_queries": all(x.get("retry_source", {}).get("status") == "transport_or_parse_unknown" for x in prepared_candidates),
            "retry_union": sorted((x["retry_source"]["batch_id"], int(x["retry_source"]["rank"])) for x in prepared_candidates),
        }
        expected_union = sorted([("WAYBACK-GALLERYEARLY01-20261016", 6), ("WAYBACK-GALLERYEARLY01-20261016", 9), ("WAYBACK-GALLERYEARLY01-20261016", 11), ("WAYBACK-GALLERYEARLY02-20261016", 4)])
        check("retry_plan_four_saved_unknown_queries", plan_gate == {"candidate_count": 4, "all_absolute_http": True, "from": FROM_TS, "max_attempts": 40, "max_entity_body_bytes": 8 * 1024 * 1024, "prior_failure_tail": 2, "saved_unknown_queries": True, "retry_union": expected_union}, plan_gate)
    except Exception as exc:
        check("retry_plan_four_saved_unknown_queries", False, {"error": f"{type(exc).__name__}:{exc}"})
'''
    text = text[:gate_start] + gate + text[gate_end:]
    text = text.replace("inherited_tail = PRIOR_FAILURE_TAIL\n    new_failures = [inherited_tail + i for i in range(1, 6)]\n    check(\"inherited_tail_zero_five_new_failures_stop\", inherited_tail == 0 and new_failures[-1] == 5", "inherited_tail = PRIOR_FAILURE_TAIL\n    new_failures = [inherited_tail + i for i in range(1, 4)]\n    check(\"inherited_tail_two_three_new_failures_stop\", inherited_tail == 2 and new_failures[-1] == 5")
    text = text.replace(
        '"exact four absolute HTTP prefixes from the root-approved remaining early-gap batch; per-item source query windows; no expansion"',
        '"exact four previously transport-unknown saved query windows; no valid-window repeat or query expansion"',
    )
    text = text.replace(
        '"control_basis": "latest root-accepted EARLY01 source receipt tail end 0; no historical control reset is used"',
        '"control_basis": "latest root-accepted EARLY02 source receipt tail end 2; EARLY01 unknown evidence remains bound for this retry union"',
    )
    DRIVER.write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "raw").mkdir(exist_ok=True)
    patch_driver()
    source_doc = json.loads(SOURCE.read_text(encoding="utf-8"))
    source_items = {int(x["registry_rank"]): x for x in source_doc["items"]}
    # The old batch rank is the saved report row; registry_rank is the
    # corresponding source-literal item in the accepted 24-item ledger.
    specs = [
        (7, "WAYBACK-GALLERYEARLY01-20261016", 6, "gallery-early01"),
        (12, "WAYBACK-GALLERYEARLY01-20261016", 9, "gallery-early01"),
        (14, "WAYBACK-GALLERYEARLY01-20261016", 11, "gallery-early01"),
        (38, "WAYBACK-GALLERYEARLY02-20261016", 4, "gallery-early02"),
    ]
    source_bindings = {
        "early_gap_plan": binding(SOURCE, "root-approved 24-item source; exact retry union"),
        "root_gallery_followups_acceptance": binding(FOLLOWUP, "root acceptance of 20+4 split"),
        "gallery_registry_v5": binding(REGISTRY, "accepted source registry"),
        "root_gallery_prefix05_acceptance": binding(BASE / "publication/root-gallery-prefix05-acceptance.json", "accepted V5 predecessor"),
        "gallery_prefix05_plan": binding(NETWORK / "gallery-prefix05/plan.json", "frozen V5 predecessor plan"),
        "gallery_prefix05_driver_v5": binding(NETWORK / "gallery-prefix05/gallery_prefix_driver_v5.py", "frozen V5 predecessor driver"),
        "gallery_prefix05_fixture": binding(NETWORK / "gallery-prefix05/fixture-results.json", "frozen V5 fixture"),
        "historical_prefix03_acceptance": binding(BASE / "publication/root-gallery-prefix03-acceptance.json", "historical tail-five metadata"),
        "root_gallery_early01_acceptance": binding(BASE / "publication/root-gallery-early01-acceptance.json", "EARLY01 acceptance for three retry targets"),
        "gallery_early01_batch_report": binding(NETWORK / "gallery-early01/batch-report.json", "EARLY01 saved unknown queries"),
        "gallery_early01_source_map": binding(NETWORK / "gallery-early01/source-map.json", "EARLY01 saved source map"),
        "gallery_early01_execution_plan": binding(NETWORK / "gallery-early01/execution-plan.json", "EARLY01 exact query plan"),
        "root_gallery_early02_acceptance": binding(BASE / "publication/root-gallery-early02-acceptance.json", "latest EARLY02 acceptance; inherited tail two"),
        "gallery_early02_batch_report": binding(NETWORK / "gallery-early02/batch-report.json", "EARLY02 saved Fishing unknown query"),
        "gallery_early02_source_map": binding(NETWORK / "gallery-early02/source-map.json", "EARLY02 saved source map"),
        "gallery_early02_execution_plan": binding(NETWORK / "gallery-early02/execution-plan.json", "EARLY02 exact query plan"),
    }
    candidates = []
    saved = []
    for rank, (registry_rank, batch_id, old_rank, batch_dir) in enumerate(specs, 1):
        item = dict(source_items[registry_rank])
        report_path = NETWORK / batch_dir / "batch-report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        result = next(x for x in report["candidate_results"] if int(x["rank"]) == old_rank)
        acceptance_path = BASE / f"publication/root-{batch_dir.replace('gallery-', 'gallery-')}-acceptance.json"
        source_map_path = NETWORK / batch_dir / "source-map.json"
        execution_plan_path = NETWORK / batch_dir / "execution-plan.json"
        # The receipt filename is stable and differs only by batch directory.
        acceptance_path = BASE / f"publication/root-{batch_dir}-acceptance.json"
        retry = {
            "batch_id": batch_id, "rank": old_rank, "original_rank": registry_rank,
            "query_url": result["query_url"], "query_window": result["query_window"],
            "status": result["status"], "report_sha256": sha(report_path),
            "source_map_sha256": sha(source_map_path), "execution_plan_sha256": sha(execution_plan_path),
            "acceptance_sha256": sha(acceptance_path), "attempt_count": len(result.get("attempts") or []),
        }
        item.update({
            "rank": rank, "target_key": f"GALLERY-EARLY03-{rank:02d}",
            "label": item["gallery"], "cdx_query_url": result["query_url"],
            "query_window": result["query_window"], "status": "prepared_not_executed",
            "execution_status": "prepared_not_executed", "network_performed_in_this_plan": False,
            "retry_source": retry,
        })
        candidates.append(item)
        source_bindings[f"source_page_{rank:02d}"] = binding(ROOT / item["source_evidence"]["path"], f"source literal for retry target {rank}")
        saved.append(retry)
    latest_acceptance = BASE / "publication/root-gallery-early02-acceptance.json"
    latest_report = NETWORK / "gallery-early02/batch-report.json"
    latest_map = NETWORK / "gallery-early02/source-map.json"
    latest_plan = NETWORK / "gallery-early02/execution-plan.json"
    policy = {
        "from": FROM_TS, "to": "per_item_source_window", "limit": LIMIT, "showResumeKey": True, "collapse": False, "matchType": "prefix",
        "max_attempts": 40, "window_seconds": 900.0, "max_total_body_bytes": 16 * 1024 * 1024, "max_entity_body_bytes": 8 * 1024 * 1024,
        "min_dispatch_seconds": 5.25, "min_request_start_seconds": 5.0, "disk_floor_bytes": 11_005_853_696, "direct_first": True,
        "proxy": "http://127.0.0.1:7890", "tls_verification": True, "automatic_redirects": 0, "stop_http_codes": [429, 503],
        "stop_on_five_consecutive_transport_failures": True, "stop_after_new_transport_failures": 3, "cooldown_seconds": 120,
        "payload_replay": False, "index_only": True, "prefix_only": True, "no_pagination": True,
        "remaining_time_and_byte_clamp": True, "retry_after_rule": "429/503 stop; not-before is at least 120 seconds and any Retry-After",
        "prior_failure_tail": 2,
    }
    plan = {
        "schema": "wow-recovery.gallery-early03-plan.v1", "batch_id": "WAYBACK-GALLERYEARLY03-20261016",
        "prepared_utc": datetime.now(timezone.utc).isoformat(), "source_plan_path": rel(SOURCE), "source_plan_sha256": sha(SOURCE),
        "scope": "exact union of four previously transport-unknown saved query windows; no valid 20 empty-window repeat",
        "mode": "prepared_not_executed", "execution_status": "prepared_not_executed", "network_authorized": False, "network_requests": 0,
        "pending_root_acceptance": True, "candidate_count": 4, "candidate_ranks": [1, 2, 3, 4],
        "retry_scope": {
            "registry_ranks": [7, 12, 14, 38],
            "saved_batch_ranks": {"EARLY01": [6, 9, 11], "EARLY02": [4]},
            "excluded_valid_empty_windows": {"EARLY01": [1, 2, 3, 4, 5, 7, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20], "EARLY02": [1, 2, 3]},
        },
        "query_window": {"from": FROM_TS, "to": "per_saved_source_window", "limit": LIMIT, "showResumeKey": True, "collapse": False, "matchType": "prefix"},
        "index_only": True, "no_payload_replay": True, "max_attempts": 40, "window_seconds": 900.0,
        "max_total_body_bytes": 16 * 1024 * 1024, "max_entity_body_bytes": 8 * 1024 * 1024, "direct_first": True, "proxy": "http://127.0.0.1:7890",
        "tls_verification": True, "automatic_redirects": 0, "min_dispatch_monotonic_seconds": 5.25, "acceptance_dispatch_floor_seconds": 5.25,
        "min_request_start_utc_seconds": 5.0, "disk_floor_bytes": 11_005_853_696, "stop_http_codes": [429, 503],
        "stop_on_five_consecutive_transport_failures": True, "stop_after_new_transport_failures": 3,
        "retry_after_rule": "429/503 stop; cooldown not earlier than Retry-After and at least 120 seconds",
        "resume_rule": "reuse exact saved query URL; record any response resumeKey; do not follow continuation",
        "failure_streak_start": 2, "prior_failure_tail": 2, "historical_gallery_tail": 5, "historical_gallery_tail_preserved": 5, "latest_tail_value": 2,
        "latest_tail_basis": {"path": rel(latest_acceptance), "sha256": sha(latest_acceptance), "failure_streak_end": 2, "role": "latest root-accepted EARLY02 source receipt; inherited current tail"},
        "control_basis": "latest root-accepted EARLY02 source receipt tail end 2; EARLY01 unknown evidence remains bound for this retry union",
        "previous_batch": {"batch_id": "WAYBACK-GALLERYEARLY02-20261016", "latest_batch_plan_path": rel(latest_plan), "latest_batch_plan_sha256": sha(latest_plan), "latest_batch_report_path": rel(latest_report), "latest_batch_report_sha256": sha(latest_report), "latest_batch_source_map_path": rel(latest_map), "latest_batch_source_map_sha256": sha(latest_map), "latest_root_acceptance_path": rel(latest_acceptance), "latest_root_acceptance_sha256": sha(latest_acceptance), "failure_streak_end": 2},
        "policy": policy,
        "input_bindings": source_bindings, "candidates": candidates, "saved_retry_evidence": saved,
    }
    plan_path = OUT / "plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    base_ast = json.loads((NETWORK / "gallery-early02/ast-diff.json").read_text(encoding="utf-8"))
    ast_doc = {
        "schema": "wow-recovery.gallery-early03-ast-diff.v1", "prepared_utc": datetime.now(timezone.utc).isoformat(),
        "base": {"path": rel(NETWORK / "gallery-prefix05/gallery_prefix_driver_v5.py"), "sha256": sha(NETWORK / "gallery-prefix05/gallery_prefix_driver_v5.py")},
        "new": {"path": rel(DRIVER), "sha256": sha(DRIVER)}, "adaptation_scope": ["exact union of four saved transport-unknown CDX queries", "latest EARLY02 tail-two binding", "valid EARLY01/EARLY02 empty windows excluded", "new batch identifiers only"],
        "ast_functions_unchanged": base_ast["ast_functions_unchanged"], "ast_functions_changed": base_ast["ast_functions_changed"], "ast_classes_unchanged": base_ast["ast_classes_unchanged"], "ast_classes_changed": base_ast["ast_classes_changed"],
        "transport_core_preserved": True, "transport_core_functions_checked": base_ast["transport_core_functions_checked"], "transport_core_functions_unchanged": base_ast["transport_core_functions_unchanged"],
        "changed_contracts": ["validate_inputs accepts exact four saved transport-unknown queries and receipt-bound tail2", "project_rows and canonical_query_url preserve saved per-item windows", "execute starts failure streak at inherited tail2 and preserves global five-stop semantics", "fixture checks saved retry union and three new failures reaching global five"],
        "offline_only": True, "network_requests": 0,
    }
    ast_path = OUT / "ast-diff.json"
    ast_path.write_text(json.dumps(ast_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bindings = {
        "schema": "wow-recovery.gallery-early03-input-bindings.v1", "batch_id": "WAYBACK-GALLERYEARLY03-20261016",
        "plan_path": rel(plan_path), "plan_sha256": sha(plan_path), "driver_path": rel(DRIVER), "driver_sha256": sha(DRIVER),
        "source_bindings": source_bindings, "network_authorized": False, "network_requests": 0, "prepared_only": True,
        "ast_diff": {"path": rel(ast_path), "sha256": sha(ast_path), "bytes": ast_path.stat().st_size, "role": "V5-to-EARLY03 static adaptation diff"},
        "retry_scope": {"registry_ranks": [7, 12, 14, 38], "saved_batch_ranks": {"EARLY01": [6, 9, 11], "EARLY02": [4]}, "excluded_valid_empty_windows": {"EARLY01": [1, 2, 3, 4, 5, 7, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20], "EARLY02": [1, 2, 3]}},
    }
    (OUT / "input-bindings.json").write_text(json.dumps(bindings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"driver_sha256": sha(DRIVER), "plan_sha256": sha(plan_path), "ast_sha256": sha(ast_path), "bindings_sha256": sha(OUT / "input-bindings.json"), "retry_union": [(x["batch_id"], x["rank"]) for x in saved]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Bounded saved-CDX follow-up recovery for the 11 CORE-PAGES-004 targets.

The 003 worker is imported only for its tested request, header, CDX, and
content-classification helpers.  This driver owns a separate output directory,
keeps all requests serial, and never writes the accepted 003 raw/entity tree.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
INPUT_CANDIDATES = ROOT / "research/continuous-recovery-20261015/core-pages4-candidates.json"
ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/core-pages3-acceptance.json"
OLD_REPORT = ROOT / "research/continuous-recovery-20261015/network-core-pages3/batch-report.json"
OLD_SOURCE_MAP = ROOT / "research/continuous-recovery-20261015/network-core-pages3/payload-source-map.json"
CORE3_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"

EXPECTED_CANDIDATES_SHA256 = "27887d30d5b4f34ed1451b2d81e7671e58f6851be46153772e3bb0b097d935a5"
MAX_TARGETS = 12
WINDOW_SECONDS = 8 * 60
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY_BYTES = 64 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 16 * 1024 * 1024
MIN_INTERVAL_SECONDS = 1.2


def load_core3() -> Any:
    spec = importlib.util.spec_from_file_location("wow_core_pages3_reuse", CORE3_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load accepted core-pages3 helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    module.RAW = RAW
    module.USER_AGENT = "wow-recovery-core-pages4/20261015"
    return module


core = load_core3()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def b32_sha1(body: bytes) -> str | None:
    if not body:
        return None
    return base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")


def disk_free_bytes() -> int:
    return int(__import__("shutil").disk_usage(OUT).free)


def verify_inputs() -> dict[str, Any]:
    if not INPUT_CANDIDATES.exists() or not ACCEPTANCE.exists():
        raise RuntimeError("required CORE-PAGES-004 input is missing")
    candidate_sha = sha256_file(INPUT_CANDIDATES)
    if candidate_sha != EXPECTED_CANDIDATES_SHA256:
        raise RuntimeError(f"candidate SHA mismatch: expected {EXPECTED_CANDIDATES_SHA256}, got {candidate_sha}")
    acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    if not acceptance.get("accepted") or acceptance.get("network_requests_by_acceptance") != 0:
        raise RuntimeError("003 acceptance is not accepted or records network requests")
    accepted_report_sha = str(acceptance.get("report_sha256") or "")
    if sha256_file(OLD_REPORT) != accepted_report_sha:
        raise RuntimeError("003 batch report no longer matches accepted report SHA")
    candidates = json.loads(INPUT_CANDIDATES.read_text(encoding="utf-8"))
    targets = candidates.get("targets") or []
    if len(targets) != 11:
        raise RuntimeError(f"expected 11 declared targets, got {len(targets)}")
    if candidates.get("network_requests") != 0 or not candidates.get("default_port_normalization_only"):
        raise RuntimeError("004 declaration has unexpected network or normalization policy")
    old_map = json.loads(OLD_SOURCE_MAP.read_text(encoding="utf-8"))
    old_entries = old_map.get("entries") or []
    if len(old_entries) != 7:
        raise RuntimeError(f"expected 7 accepted 003 payloads, got {len(old_entries)}")
    for entry in old_entries:
        body_path = ROOT / "research/continuous-recovery-20261015/network-core-pages3" / entry["raw_body_path"]
        if not body_path.exists() or sha256_file(body_path) != entry["body_sha256"]:
            raise RuntimeError(f"accepted 003 body changed: {entry.get('target')}")
    return {
        "candidate_sha256": candidate_sha,
        "acceptance_sha256": sha256_file(ACCEPTANCE),
        "accepted_report_sha256": accepted_report_sha,
        "old_source_map_sha256": sha256_file(OLD_SOURCE_MAP),
        "old_payload_count": len(old_entries),
        "candidates": candidates,
    }


def target_item(entry: dict[str, Any], rank: int) -> dict[str, Any]:
    item = dict(entry)
    item["candidate_rank"] = rank
    item["query_original_url"] = str(entry["query_original_url"])
    action = str(entry.get("action") or "")
    capture = entry.get("candidate")
    if action == "replay_saved_cdx_candidate":
        if not isinstance(capture, dict):
            raise RuntimeError(f"saved target has no candidate: {entry.get('target')}")
        capture = dict(capture)
        if core.normalized_url_identity(capture["original"]) != core.normalized_url_identity(item["query_original_url"]):
            raise RuntimeError(f"saved candidate is not a strict same-origin/default-port match: {entry.get('target')}")
        if int(capture["statuscode"]) not in ({200} | core.REDIRECT_CODES):
            raise RuntimeError(f"saved candidate has unsupported status: {entry.get('target')}")
        if not re.fullmatch(r"\d{14}", str(capture["timestamp"])) or str(capture["timestamp"]) > core.ANCHOR_TIMESTAMP:
            raise RuntimeError(f"saved candidate timestamp is outside anchor: {entry.get('target')}")
        item["candidate"] = capture
    elif action == "retry_failed_exact_cdx_query":
        if "query_url" not in entry:
            raise RuntimeError(f"retry target has no exact query URL: {entry.get('target')}")
        item["candidate"] = None
    else:
        raise RuntimeError(f"unsupported declaration action: {action}")
    return item


def plan_document(inputs: dict[str, Any]) -> dict[str, Any]:
    targets = [target_item(entry, index) for index, entry in enumerate(inputs["candidates"]["targets"], start=1)]
    return {
        "schema": "continuous-wow-core-pages-followup-plan/v1",
        "mode": "bounded_saved_cdx_replay",
        "prepared_utc": now_utc(),
        "input_candidates": str(INPUT_CANDIDATES.relative_to(ROOT)).replace("\\", "/"),
        "input_candidates_sha256": inputs["candidate_sha256"],
        "derived_from_acceptance": str(ACCEPTANCE.relative_to(ROOT)).replace("\\", "/"),
        "acceptance_sha256": inputs["acceptance_sha256"],
        "targets": [
            {
                "candidate_rank": item["candidate_rank"],
                "target": item["target"],
                "action": item["action"],
                "query_original_url": item["query_original_url"],
                "saved_capture": item.get("candidate"),
                "query_url": item.get("query_url"),
            }
            for item in targets
        ],
        "policy": {
            "max_targets": MAX_TARGETS,
            "max_attempts": 32,
            "window_seconds": WINDOW_SECONDS,
            "minimum_start_interval_seconds": MIN_INTERVAL_SECONDS,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
            "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
            "direct_first_only_then_confirmed_transport": True,
            "direct_connect_timeout_seconds": core.DIRECT_CONNECT_SECONDS,
            "direct_total_timeout_seconds": core.DIRECT_MAX_SECONDS,
            "proxy": core.PROXY,
            "proxy_connect_timeout_seconds": core.PROXY_CONNECT_SECONDS,
            "proxy_total_timeout_seconds": core.PROXY_MAX_SECONDS,
            "automatic_redirects": 0,
            "manual_wayback_redirect_hops": 1,
            "stop_http_codes": sorted(core.STOP_HTTP_CODES),
            "tls_verification": "curl_default_verification_enabled",
            "uri_policy": "same scheme and lower-cased host; only HTTP:80/HTTPS:443 default ports normalize; path/query remain literal",
            "cdx_policy": "only retry the declared exact /news/wow-news2005.html query; no other CDX queries",
        },
        "network_requests": 0,
        "ready": disk_free_bytes() >= MIN_FREE_BYTES,
    }


def prepare() -> int:
    inputs = verify_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    plan = plan_document(inputs)
    output_candidates = dict(inputs["candidates"])
    output_candidates["input_sha256"] = inputs["candidate_sha256"]
    output_candidates["execution_policy"] = plan["policy"]
    output_candidates["execution"] = {"network_requests": 0, "status": "planned"}
    write_json(OUT / "candidates.json", output_candidates)
    write_json(OUT / "batch-config.json", plan)
    write_json(OUT / "plan.json", plan)
    print(json.dumps({
        "mode": "plan_only",
        "target_count": len(plan["targets"]),
        "network_requests": 0,
        "input_candidates_sha256": inputs["candidate_sha256"],
        "old_payload_count_preserved": inputs["old_payload_count"],
        "disk_free_bytes": disk_free_bytes(),
    }, ensure_ascii=False))
    return 0


def public_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    return core.source_attempt_view(attempt)


def request_serial(
    url: str,
    kind: str,
    target: str,
    state: Any,
    transport_state: dict[str, str | None],
) -> list[dict[str, Any]]:
    """Use direct only for the first source request, then the confirmed stream."""
    attempts: list[dict[str, Any]] = []
    transport = transport_state.get("transport")
    if transport is None:
        direct = core.run_request(url, "direct", kind, target, state, state.attempts + 1)
        attempts.append(direct)
        if direct.get("executed") and not direct.get("transport_error") and not state.stop_reason:
            transport_state["transport"] = "direct"
            return attempts
        if state.stop_reason or direct.get("source_status") in core.STOP_HTTP_CODES:
            return attempts
        proxy = core.run_request(url, "proxy", kind, target, state, state.attempts + 1)
        attempts.append(proxy)
        transport_state["transport"] = "proxy"
        return attempts
    attempts.append(core.run_request(url, transport, kind, target, state, state.attempts + 1))
    return attempts


def request_confirmed(
    url: str,
    kind: str,
    target: str,
    state: Any,
    transport_state: dict[str, str | None],
) -> list[dict[str, Any]]:
    transport = transport_state.get("transport") or "proxy"
    return [core.run_request(url, transport, kind, target, state, state.attempts + 1)]


def body_metrics(final: dict[str, Any] | None, capture: dict[str, Any] | None) -> dict[str, Any]:
    if not final or not final.get("executed"):
        return {
            "body_bytes": 0,
            "body_sha256": None,
            "cdx_digest_expected": (capture or {}).get("digest"),
            "cdx_digest_calculated": None,
            "cdx_digest_match": None,
            "cdx_length": int(capture["length"]) if capture and str(capture.get("length", "")).isdigit() else None,
            "mime": None,
            "title": None,
            "actual_memento": None,
        }
    raw = final.get("raw") or {}
    body_path = OUT / str(raw.get("body"))
    body = body_path.read_bytes() if body_path.exists() else b""
    calculated = b32_sha1(body)
    expected = str((capture or {}).get("digest") or "").upper() or None
    return {
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "cdx_digest_expected": expected,
        "cdx_digest_calculated": calculated,
        "cdx_digest_match": bool(expected and calculated and expected == calculated),
        "cdx_length": int(capture["length"]) if capture and str(capture.get("length", "")).isdigit() else None,
        "mime": final.get("content_type"),
        "title": ((final.get("html") or {}).get("title") or None),
        "actual_memento": final.get("memento_datetime"),
        "source_status": final.get("source_status"),
        "raw_body_path": raw.get("body"),
        "raw_headers_path": raw.get("headers"),
        "raw_trace_path": raw.get("trace"),
    }


def redirect_event(
    item: dict[str, Any],
    capture: dict[str, Any] | None,
    attempt: dict[str, Any],
    follow_url: str | None,
    followed: bool,
    follow_reason: str | None,
    follow_attempt: dict[str, Any] | None,
) -> dict[str, Any]:
    location = attempt.get("location")
    parsed = urlsplit(location) if location else None
    if follow_url:
        location_kind = "same_wayback_followed" if followed else "same_wayback_not_followed"
    elif location:
        location_kind = "external_or_non_wayback_registered_only"
    else:
        location_kind = "missing_location"
    return {
        "candidate_rank": item["candidate_rank"],
        "target": item["target"],
        "query_original_url": item["query_original_url"],
        "capture_timestamp": (capture or {}).get("timestamp"),
        "capture_original": (capture or {}).get("original"),
        "redirect_source_status": attempt.get("source_status"),
        "location": location,
        "location_host": (parsed.hostname or "").lower() if parsed else None,
        "location_kind": location_kind,
        "manual_followed": followed,
        "manual_follow_url": follow_url,
        "follow_reason": follow_reason,
        "follow_source_status": (follow_attempt or {}).get("source_status"),
        "follow_actual_memento": (follow_attempt or {}).get("memento_datetime"),
        "raw_headers_path": (attempt.get("raw") or {}).get("headers"),
        "follow_raw_headers_path": ((follow_attempt or {}).get("raw") or {}).get("headers"),
    }


def replay_capture(
    item: dict[str, Any],
    capture: dict[str, Any],
    state: Any,
    transport_state: dict[str, str | None],
    redirect_events: list[dict[str, Any]],
) -> dict[str, Any]:
    replay_url = core.replay_url(capture)
    attempts = request_serial(replay_url, "replay", item["target"], state, transport_state)
    executed = [attempt for attempt in attempts if attempt.get("executed")]
    first = executed[-1] if executed else None
    redirect_note: str | None = None
    if first and first.get("source_status") in core.REDIRECT_CODES:
        follow_url = core.legal_wayback_replay(first.get("location"), first.get("url") or replay_url)
        follow_attempt: dict[str, Any] | None = None
        followed = False
        if follow_url and not state.stop_reason:
            follow = request_confirmed(follow_url, "replay-follow", item["target"], state, transport_state)
            attempts.extend(follow)
            follow_attempt = next((attempt for attempt in reversed(follow) if attempt.get("executed")), None)
            followed = follow_attempt is not None
            if not followed:
                redirect_note = (follow[-1].get("unrequested_reason") if follow else None) or "manual_wayback_follow_not_executed"
        elif follow_url:
            redirect_note = state.stop_reason or "limit_before_manual_redirect_follow"
        else:
            redirect_note = "redirect_location_not_same_wayback_host"
        redirect_events.append(redirect_event(item, capture, first, follow_url, followed, redirect_note, follow_attempt))
    executed = [attempt for attempt in attempts if attempt.get("executed")]
    final = executed[-1] if executed else None
    initial_status = first.get("source_status") if first else None
    if first is None:
        category = "not_requested"
        detail = {"reason": attempts[-1].get("unrequested_reason") if attempts else "replay_not_requested"}
    elif initial_status in core.REDIRECT_CODES:
        if len(executed) > 1:
            followed_category, followed_detail = core.classify_replay(final, redirect_note)
            category = f"redirect_followed_{followed_category}"
            detail = {"reason": "302_is_redirect_evidence_not_direct_entity", "followed_classification": followed_category, **followed_detail}
        else:
            category = "redirect_unfollowed"
            detail = {"reason": redirect_note or "redirect_follow_not_available", "location": first.get("location")}
    else:
        category, detail = core.classify_replay(final, redirect_note)
    metrics = body_metrics(final, capture)
    entity_valid = (
        initial_status == 200
        and category in {"valid_html", "valid_xml", "valid_content"}
        and bool(metrics.get("actual_memento"))
        and metrics.get("cdx_digest_match") is True
    )
    if category in {"valid_html", "valid_xml", "valid_content"} and not entity_valid:
        if not metrics.get("actual_memento"):
            category = "valid_source_missing_memento"
        elif metrics.get("cdx_digest_match") is not True:
            category = "payload_digest_mismatch"
        detail = {
            **detail,
            "entity_rejected": True,
            "actual_memento": metrics.get("actual_memento"),
            "cdx_digest_match": metrics.get("cdx_digest_match"),
        }
    return {
        "requested_replay_url": replay_url,
        "attempts": attempts,
        "initial": first,
        "final": final,
        "initial_status": initial_status,
        "category": category,
        "detail": detail,
        "metrics": metrics,
        "entity_valid": entity_valid,
    }


def cdx_info_for_saved(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "query_performed": False,
        "query_url": None,
        "query_original_url": item["query_original_url"],
        "source_status": None,
        "source_response_count": 0,
        "capture_index_count": None,
        "valid_capture_count": 1,
        "capture_records": [],
        "selected_capture": item["candidate"],
        "selection_source": "declared_saved_cdx_candidate",
        "unrequested_reason": "saved_cdx_candidate_replay_no_cdx_query",
        "attempts": [],
    }


def cdx_retry(
    item: dict[str, Any],
    state: Any,
    transport_state: dict[str, str | None],
) -> tuple[dict[str, Any], dict[str, Any] | None, list[dict[str, Any]]]:
    query_attempts = request_serial(item["query_url"], "cdx", item["target"], state, transport_state)
    executed = [attempt for attempt in query_attempts if attempt.get("executed")]
    query_attempt = executed[-1] if executed else None
    records = query_attempt.get("cdx_records") or [] if query_attempt else []
    valid = core.valid_cdx_records(records, item["query_original_url"]) if query_attempt and query_attempt.get("source_status") == 200 and not query_attempt.get("transport_error") else []
    selected = core.select_capture(valid)
    if query_attempt:
        query_attempt["cdx_capture_index_count"] = len(records)
        query_attempt["cdx_valid_capture_count"] = len(valid)
        query_attempt["cdx_valid_records"] = valid
    info = {
        "query_performed": True,
        "query_url": item["query_url"],
        "query_original_url": item["query_original_url"],
        "source_status": query_attempt.get("source_status") if query_attempt else None,
        "source_response_count": sum(attempt.get("source_status") is not None for attempt in query_attempts),
        "capture_index_count": len(records),
        "valid_capture_count": len(valid),
        "capture_records": records,
        "selected_capture": selected,
        "selection_source": "retry_exact_cdx_query",
        "unrequested_reason": None,
        "attempts": query_attempts,
    }
    return info, selected, query_attempts


def result_record(
    item: dict[str, Any],
    cdx: dict[str, Any],
    replay: dict[str, Any] | None,
    redirect_events: list[dict[str, Any]],
    state: Any,
) -> dict[str, Any]:
    if replay is None:
        query_attempt = next((attempt for attempt in reversed(cdx.get("attempts") or []) if attempt.get("executed")), None)
        if query_attempt is None and cdx.get("query_performed") is False:
            category = "not_requested" if state.stop_reason else "not_requested"
            detail = {"reason": cdx.get("unrequested_reason") or "replay_not_started"}
        elif query_attempt and query_attempt.get("transport_error"):
            category = "transport_error"
            detail = {"reason": query_attempt.get("transport_reason") or "query_transport_error"}
        elif cdx.get("selected_capture") is None:
            category = "cdx_empty_in_range" if not cdx.get("capture_index_count") else "cdx_no_valid_capture"
            detail = {"reason": "no_valid_same_origin_capture", "permanent_unarchived_claim": False}
        else:
            category = "not_requested"
            detail = {"reason": "replay_not_started"}
        final = None
        metrics = body_metrics(None, cdx.get("selected_capture"))
        replay_attempts: list[dict[str, Any]] = []
        actual = None
    else:
        category = replay["category"]
        detail = replay["detail"]
        final = replay["final"]
        metrics = replay["metrics"]
        replay_attempts = replay["attempts"]
        actual = metrics.get("actual_memento")
    selected = cdx.get("selected_capture")
    unrequested_reason = None
    if category in {"not_requested", "cdx_empty_in_range", "cdx_no_valid_capture", "transport_error"} and not replay_attempts:
        unrequested_reason = detail.get("reason")
    return {
        "candidate_rank": item["candidate_rank"],
        "target": item["target"],
        "action": item["action"],
        "query_original_url": item["query_original_url"],
        "candidate_declaration": item.get("candidate"),
        "cdx": {
            **{key: value for key, value in cdx.items() if key != "capture_records"},
            "capture_records": cdx.get("capture_records") or [],
            "attempts": [public_attempt(attempt) for attempt in cdx.get("attempts") or []],
        },
        "selected_capture": selected,
        "requested_replay_url": replay.get("requested_replay_url") if replay else None,
        "replay_attempt_count": len([attempt for attempt in replay_attempts if attempt.get("executed")]),
        "replay_source_response_count": sum(attempt.get("source_status") is not None for attempt in replay_attempts),
        "replay_hops": [public_attempt(attempt) for attempt in replay_attempts],
        "redirect_evidence_count": sum(event["candidate_rank"] == item["candidate_rank"] for event in redirect_events),
        "category": category,
        "detail": detail,
        "actual_memento_or_null": actual,
        "final_source_status": final.get("source_status") if final else None,
        "final_content_type": final.get("content_type") if final else None,
        "final_body_bytes": metrics.get("body_bytes", 0),
        "final_body_sha256": metrics.get("body_sha256"),
        "payload_metrics": metrics,
        "unrequested_reason": unrequested_reason,
        "entity_valid": bool(replay and replay.get("entity_valid")),
    }


def source_map_entry(result: dict[str, Any]) -> dict[str, Any] | None:
    if not result.get("entity_valid"):
        return None
    capture = result.get("selected_capture") or {}
    metrics = result.get("payload_metrics") or {}
    return {
        "target": result["target"],
        "query_original_url": result["query_original_url"],
        "indexed_capture_timestamp": capture.get("timestamp"),
        "indexed_original_url": capture.get("original"),
        # Keep the observed CDX identity under the compatibility name used by
        # the 003 source-map consumer.  This is the literal URL from the
        # selected capture; it is not a normalized or inferred alias.
        "captured_original_url": capture.get("original"),
        "indexed_statuscode": capture.get("statuscode"),
        "indexed_cdx_digest": capture.get("digest"),
        "indexed_cdx_length": capture.get("length"),
        "actual_memento": result["actual_memento_or_null"],
        "source_status": result["final_source_status"],
        "content_type": result["final_content_type"],
        "title": metrics.get("title"),
        "body_bytes": result["final_body_bytes"],
        "body_sha256": result["final_body_sha256"],
        "cdx_digest_calculated": metrics.get("cdx_digest_calculated"),
        "cdx_digest_match": metrics.get("cdx_digest_match"),
        "raw_body_path": metrics.get("raw_body_path"),
        "raw_headers_path": metrics.get("raw_headers_path"),
        "raw_trace_path": metrics.get("raw_trace_path"),
        "action": "review source mapping before any integration; entity remains only in this batch raw directory",
    }


def public_summary(report: dict[str, Any], source_map: dict[str, Any], redirects: list[dict[str, Any]]) -> None:
    summary = {
        "schema": "continuous-wow-core-pages-followup-summary/v1",
        "report_sha256": sha256_file(OUT / "batch-report.json"),
        "inputs": report["inputs"],
        "request_window_started_utc": report["started_utc"],
        "request_window_finished_utc": report["request_window_finished_utc"],
        "report_updated_utc": report["report_updated_utc"],
        "network_requests": report["source_request_count"],
        "source_response_count": report["source_response_count"],
        "category_counts": report["category_counts"],
        "valid_entity_count": report["valid_entity_count"],
        "targets": [
            {
                "candidate_rank": result["candidate_rank"],
                "target": result["target"],
                "action": result["action"],
                "category": result["category"],
                "query_original_url": result["query_original_url"],
                "selected_capture_timestamp": (result.get("selected_capture") or {}).get("timestamp"),
                "selected_capture_original": (result.get("selected_capture") or {}).get("original"),
                "source_status": result.get("final_source_status"),
                "actual_memento_or_null": result.get("actual_memento_or_null"),
                "body_bytes": result.get("final_body_bytes"),
                "body_sha256": result.get("final_body_sha256"),
                "cdx_digest_match": (result.get("payload_metrics") or {}).get("cdx_digest_match"),
                "redirect_evidence_count": result.get("redirect_evidence_count"),
                "unrequested_reason": result.get("unrequested_reason"),
            }
            for result in report["results"]
        ],
        "redirect_evidence_count": len(redirects),
        "old_003_entities_preserved": True,
        "payload_source_map_entries": len(source_map["entries"]),
    }
    write_json(OUT / "sanitized-summary.json", summary)
    lines = [
        "# CORE-PAGES-004 sanitized recovery summary",
        "",
        f"Input candidates SHA-256: {report['inputs']['candidate_sha256']}.",
        f"Request window: {report['started_utc']} to {report['request_window_finished_utc']}; report updated: {report['report_updated_utc']}.",
        f"Attempts: {report['source_request_count']}; source responses: {report['source_response_count']}; failed attempts: {report['failed_attempt_count']}; CDX source responses: {report['cdx_source_response_count']}; replay source responses: {report['replay_source_response_count']}; valid entities: {report['valid_entity_count']}; redirect evidence: {len(redirects)}.",
        "Categories: " + ", ".join(f"{key} {value}" for key, value in sorted(report["category_counts"].items())) + ".",
        f"Disk free before/after: {report['preflight']['disk_free_bytes_before']} / {report['preflight']['disk_free_bytes_after']} bytes.",
        "",
        "| # | target | action | category | capture timestamp | source HTTP | actual Memento | bytes | digest match | reason |",
        "|---:|---|---|---|---|---:|---|---:|---|---|",
    ]
    for result in report["results"]:
        lines.append(
            f"| {result['candidate_rank']} | {result['target']} | {result['action']} | {result['category']} | "
            f"{(result.get('selected_capture') or {}).get('timestamp') or ''} | {result.get('final_source_status') or ''} | "
            f"{result.get('actual_memento_or_null') or ''} | {result.get('final_body_bytes') or 0} | "
            f"{(result.get('payload_metrics') or {}).get('cdx_digest_match')} | {result.get('unrequested_reason') or ''} |"
        )
    lines.extend([
        "",
        "Original headers, traces, and bodies remain only in this batch raw directory. No entity was copied into the offline mirror; the seven accepted 003 entities remain in their original tree.",
        "",
    ])
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")


def execute() -> int:
    inputs = verify_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    plan = plan_document(inputs)
    output_candidates = dict(inputs["candidates"])
    output_candidates["input_sha256"] = inputs["candidate_sha256"]
    output_candidates["execution_policy"] = plan["policy"]
    output_candidates["execution"] = {"network_requests": None, "status": "executing"}
    write_json(OUT / "candidates.json", output_candidates)
    write_json(OUT / "batch-config.json", plan)
    disk_before = disk_free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk free {disk_before} below {MIN_FREE_BYTES}")
    window_started_monotonic = time.monotonic()
    started_utc = now_utc()
    state = core.RunState(window_started_monotonic)
    transport_state: dict[str, str | None] = {"transport": None}
    redirect_events: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    source_entries: list[dict[str, Any]] = []
    target_items = [target_item(entry, index) for index, entry in enumerate(inputs["candidates"]["targets"], start=1)]

    for item in target_items:
        if item["action"] == "retry_failed_exact_cdx_query":
            if state.check_limits():
                cdx, selected, _ = cdx_retry(item, state, transport_state)
            else:
                cdx = {
                    "query_performed": False,
                    "query_url": item.get("query_url"),
                    "query_original_url": item["query_original_url"],
                    "source_status": None,
                    "source_response_count": 0,
                    "capture_index_count": None,
                    "valid_capture_count": 0,
                    "capture_records": [],
                    "selected_capture": None,
                    "selection_source": "blocked_before_exact_cdx_retry",
                    "unrequested_reason": state.stop_reason or "limit_before_cdx_retry",
                    "attempts": [],
                }
                selected = None
            replay = None
            if selected is not None and not state.stop_reason:
                replay = replay_capture(item, selected, state, transport_state, redirect_events)
            result = result_record(item, cdx, replay, redirect_events, state)
        else:
            cdx = cdx_info_for_saved(item)
            replay = None
            if state.check_limits():
                replay = replay_capture(item, item["candidate"], state, transport_state, redirect_events)
            result = result_record(item, cdx, replay, redirect_events, state)
        results.append(result)
        mapped = source_map_entry(result)
        if mapped is not None:
            source_entries.append(mapped)
        if state.stop_reason:
            continue

    request_window_finished_utc = now_utc()
    report_updated_utc = now_utc()
    disk_after = disk_free_bytes()
    all_attempts: list[dict[str, Any]] = []
    for result in results:
        all_attempts.extend(result["cdx"].get("attempts") or [])
        all_attempts.extend(result.get("replay_hops") or [])
    # Public attempts contain enough timing/status data for aggregate validation.
    starts = [datetime.fromisoformat(attempt["started_utc"]) for attempt in all_attempts if attempt.get("started_utc")]
    start_gaps = [
        (datetime.fromisoformat(all_attempts[index + 1]["started_utc"]) - datetime.fromisoformat(all_attempts[index]["started_utc"])).total_seconds()
        for index in range(len(all_attempts) - 1)
        if all_attempts[index].get("started_utc") and all_attempts[index + 1].get("started_utc")
    ]
    cdx_source_responses = sum(result["cdx"].get("source_response_count", 0) for result in results)
    replay_source_responses = sum(result.get("replay_source_response_count", 0) for result in results)
    category_counts: dict[str, int] = {}
    for result in results:
        category_counts[result["category"]] = category_counts.get(result["category"], 0) + 1
    report = {
        "schema": "continuous-wow-core-pages-followup-report/v1",
        "mode": "execute",
        "inputs": {
            "candidate_path": str(INPUT_CANDIDATES.relative_to(ROOT)).replace("\\", "/"),
            "candidate_sha256": inputs["candidate_sha256"],
            "acceptance_path": str(ACCEPTANCE.relative_to(ROOT)).replace("\\", "/"),
            "acceptance_sha256": inputs["acceptance_sha256"],
            "accepted_003_report_sha256": inputs["accepted_report_sha256"],
            "accepted_003_source_map_sha256": inputs["old_source_map_sha256"],
        },
        "started_utc": started_utc,
        "request_window_finished_utc": request_window_finished_utc,
        "finished_utc": request_window_finished_utc,
        "report_updated_utc": report_updated_utc,
        "target_count": len(results),
        "source_request_count": state.attempts,
        "transport_attempt_count": state.attempts,
        "source_response_count": state.source_responses,
        "failed_attempt_count": state.failed_attempts,
        "cdx_source_response_count": cdx_source_responses,
        "replay_source_response_count": replay_source_responses,
        "capture_index_count_fetched": sum(result["cdx"].get("capture_index_count") or 0 for result in results if result["cdx"].get("query_performed")),
        "saved_capture_candidate_count": sum(result["action"] == "replay_saved_cdx_candidate" for result in results),
        "valid_entity_count": len(source_entries),
        "total_body_bytes": state.total_body_bytes,
        "category_counts": category_counts,
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "transport": {"confirmed_transport": transport_state.get("transport")},
        "preflight": {
            "drive": "D:",
            "disk_free_bytes_before": disk_before,
            "disk_free_bytes_after": disk_after,
            "minimum_free_bytes": MIN_FREE_BYTES,
        },
        "request_window_seconds": (
            (max(datetime.fromisoformat(attempt["finished_utc"]) for attempt in all_attempts if attempt.get("finished_utc")) - min(starts)).total_seconds()
            if all_attempts and starts else 0
        ),
        "minimum_start_interval_seconds": min(start_gaps) if start_gaps else None,
        "redirect_evidence_count": len(redirect_events),
        "old_003_entities_preserved": True,
        "policy": plan["policy"],
        "results": results,
    }
    output_candidates["execution"] = {
        "network_requests": state.attempts,
        "status": "completed",
        "request_window_finished_utc": request_window_finished_utc,
        "report_updated_utc": report_updated_utc,
    }
    write_json(OUT / "candidates.json", output_candidates)
    write_json(OUT / "batch-config.json", plan)
    write_json(OUT / "batch-report.json", report)
    source_map = {
        "schema": "continuous-wow-core-pages-followup-payload-source-map/v1",
        "generated_utc": report_updated_utc,
        "only_real_valid_entities": True,
        "prior_accepted_003_source_map": str(OLD_SOURCE_MAP.relative_to(ROOT)).replace("\\", "/"),
        "prior_accepted_003_entities_preserved": inputs["old_payload_count"],
        "entries": source_entries,
    }
    write_json(OUT / "payload-source-map.json", source_map)
    write_json(OUT / "redirect-evidence.json", {
        "schema": "continuous-wow-core-pages-followup-redirect-evidence/v1",
        "generated_utc": report_updated_utc,
        "entries": redirect_events,
    })
    public_summary(report, source_map, redirect_events)
    print(json.dumps({
        "target_count": len(results),
        "category_counts": category_counts,
        "attempts": state.attempts,
        "source_responses": state.source_responses,
        "cdx_source_responses": cdx_source_responses,
        "replay_source_responses": replay_source_responses,
        "valid_entities": len(source_entries),
        "total_body_bytes": state.total_body_bytes,
        "redirect_evidence": len(redirect_events),
        "stop_reason": state.stop_reason,
        "confirmed_transport": transport_state.get("transport"),
    }, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.execute:
        return execute()
    return prepare()


if __name__ == "__main__":
    raise SystemExit(main())

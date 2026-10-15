"""NET-RSS-018 bounded RSS/archive recovery adapter.

This adapter imports the accepted RSS016 transport, corrected HTML date
parser, CDX parser and dispatch gate.  It owns only this batch's outputs and
does not continue CDX pages or follow redirects.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
PLAN = ROOT / "research/continuous-recovery-20261015/rss18-approved-plan.json"
PROPOSAL = ROOT / "research/continuous-recovery-20261015/remaining-rss13-next8-proposal.json"
CONTROL17_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/control17-acceptance.json"
RSS16_DRIVER = ROOT / "research/continuous-recovery-20261015/network-rss16/rss16_driver.py"
PROXY = "http://127.0.0.1:7890"
FROM_TS = "20040101000000"
ANCHOR = "20080512210044"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
REDIRECT_CODES = {301, 302, 303, 307, 308}
STOP_CODES = {429, 503}
MAX_TARGETS = 8
MAX_ATTEMPTS = 32
WINDOW_SECONDS = 480
MIN_INTERVAL = 1.35
MIN_FREE = 11_005_853_696
MAX_TOTAL = 64 * 1024 * 1024
MAX_ENTITY = 16 * 1024 * 1024
USER_AGENT = "wow-recovery-rss18/20261015"
PLAN_SHA = "e7bb2e9601f2b684c5eb3ae68a315e14b39cb9bc6c9a6f3b8a5d82693d2f4267"
PROPOSAL_SHA = "d5a87f58abc40c95aae1c760e8ea19f79cc3bcc137993c592b297bb7e5bdf206"
CONTROL17_ACCEPTANCE_SHA = "4d21363fb91da834c1956df578e2593565f9871aaaf11738b348460532eea26c"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load accepted RSS016 driver: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rss16 = load_module(RSS16_DRIVER, "rss18_rss16_helpers")
core = rss16.core
gate_mod = rss16.gate_mod
rss6 = rss16.rss6

# Rebind the accepted helpers to this batch's output and exact policy.
rss16.OUT, rss16.RAW, rss16.PROXY, rss16.USER_AGENT = OUT, RAW, PROXY, USER_AGENT
rss16.FROM_TS, rss16.ANCHOR, rss16.FIELDS = FROM_TS, ANCHOR, FIELDS
rss16.REDIRECT_CODES, rss16.STOP_CODES = REDIRECT_CODES, STOP_CODES
rss16.MAX_TARGETS, rss16.MAX_ATTEMPTS = MAX_TARGETS, MAX_ATTEMPTS
rss16.WINDOW_SECONDS, rss16.MIN_INTERVAL = WINDOW_SECONDS, MIN_INTERVAL
rss16.MIN_FREE, rss16.MAX_TOTAL, rss16.MAX_ENTITY = MIN_FREE, MAX_TOTAL, MAX_ENTITY
core.OUT, core.RAW, core.PROXY, core.USER_AGENT = OUT, RAW, PROXY, USER_AGENT
core.FROM_TIMESTAMP, core.TO_TIMESTAMP, core.CDX_COLUMNS, core.CDX_LIMIT = FROM_TS, ANCHOR, FIELDS, 1000
core.MAX_ATTEMPTS, core.WINDOW_SECONDS, core.MIN_INTERVAL_SECONDS = MAX_ATTEMPTS, WINDOW_SECONDS, 0.0
core.MIN_FREE_BYTES, core.MAX_TOTAL_BODY_BYTES, core.MAX_ENTITY_BODY_BYTES = MIN_FREE, MAX_TOTAL, MAX_ENTITY
rss6.OUT, rss6.RAW, rss6.core = OUT, RAW, core
gate_mod.OUT, gate_mod.RAW, gate_mod.INTERVAL_SECONDS = OUT, RAW, MIN_INTERVAL


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def digest(path: Path) -> dict[str, Any]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def build_cdx_url(parameters: dict[str, Any]) -> str:
    ordered = [(str(key), str(value)) for key, value in parameters.items()]
    if any(key == "collapse" for key, _ in ordered):
        raise RuntimeError("RSS018 CDX declaration must not contain collapse")
    return f"https://web.archive.org/cdx/search/cdx?{urlencode(ordered)}"


def verify_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    if sha256_file(PLAN) != PLAN_SHA:
        raise RuntimeError("RSS018 approved plan SHA mismatch")
    if sha256_file(PROPOSAL) != PROPOSAL_SHA:
        raise RuntimeError("RSS018 proposal SHA mismatch")
    if sha256_file(CONTROL17_ACCEPTANCE) != CONTROL17_ACCEPTANCE_SHA:
        raise RuntimeError("CONTROL017 acceptance SHA mismatch")
    plan = read_json(PLAN)
    proposal = read_json(PROPOSAL)
    health = read_json(CONTROL17_ACCEPTANCE)
    if plan.get("task_id") != "NET-RSS-018" or len(plan.get("queue") or []) != MAX_TARGETS:
        raise RuntimeError("RSS018 plan identity or queue length mismatch")
    if plan.get("proposal", {}).get("sha256") != PROPOSAL_SHA or plan.get("health_gate", {}).get("sha256") != CONTROL17_ACCEPTANCE_SHA:
        raise RuntimeError("RSS018 plan input binding mismatch")
    if health.get("accepted") is not True or health.get("network_requests_by_acceptance") != 0 or health.get("new_recovered_resources") != 0:
        raise RuntimeError("CONTROL017 health gate is not accepted")
    health_report = ROOT / str(health["report"]["path"])
    health_journal = ROOT / str(health["journal"]["path"])
    if sha256_file(health_report) != health["report"]["sha256"] or sha256_file(health_journal) != health["journal"]["sha256"]:
        raise RuntimeError("CONTROL017 accepted report or journal drift")
    if health.get("body_sha256") != "69915a4eea19ec455a60b89c64ed661fc55d48bc3a724bdffcc91bd2d617aa7b" or health.get("knownCSS_bytes") != 109:
        raise RuntimeError("CONTROL017 known CSS health identity mismatch")
    expected_params = {"matchType": "exact", "from": "20040101", "to": "20080512210044", "output": "json", "fl": ",".join(FIELDS), "limit": "1000", "showResumeKey": "true"}
    for rank, item in enumerate(plan["queue"], start=1):
        if item.get("rank") != rank or not item.get("target") or not item.get("exact_original_url", "").startswith("http://www.worldofwarcraft.com/news/rss-"):
            raise RuntimeError(f"RSS018 queue identity drift at rank {rank}")
        if item.get("operation") == "replay_saved_capture_without_CDX":
            if rank != 1 or not item.get("replay_url") or not item.get("selected_capture") or item.get("cdx_query_parameters") is not None:
                raise RuntimeError("RSS018 saved replay declaration drift")
        else:
            params = item.get("cdx_query_parameters") or {}
            if any(str(params.get(key)) != value for key, value in expected_params.items()) or "collapse" in params:
                raise RuntimeError(f"RSS018 CDX parameter drift at rank {rank}")
            if item.get("replay_url") is not None or item.get("selected_capture") is not None:
                raise RuntimeError(f"RSS018 CDX target has preselected replay at rank {rank}")
    inputs = {
        "approved_plan": digest(PLAN),
        "proposal": digest(PROPOSAL),
        "control17_acceptance": digest(CONTROL17_ACCEPTANCE),
        "control17_report": digest(health_report),
        "control17_journal": digest(health_journal),
        "rss16_corrected_driver": digest(RSS16_DRIVER),
    }
    return plan, {"proposal": proposal, "health": health, "input_digests": inputs}


def build_candidates(plan: dict[str, Any], aux: dict[str, Any]) -> dict[str, Any]:
    targets: list[dict[str, Any]] = []
    for item in plan["queue"]:
        original = str(item["exact_original_url"])
        match = __import__("re").search(r"rss-(\d{2})-(\d{4})\.xml$", original)
        if not match:
            raise RuntimeError(f"cannot derive declared year/month from {original}")
        params = item.get("cdx_query_parameters")
        targets.append({
            "rank": item["rank"],
            "target": item["target"],
            "query_original": original,
            "year": int(match.group(2)),
            "month": int(match.group(1)),
            "operation": item["operation"],
            "state": item.get("state"),
            "prior": item.get("prior") or [],
            "menu_evidence": item.get("menu_evidence") or [],
            "cdx_query_parameters": params,
            "cdx_query_url": build_cdx_url(params) if params else None,
            "saved_capture": item.get("selected_capture"),
            "saved_replay_url": item.get("replay_url"),
        })
    return {
        "schema": "continuous-wow-net-rss18-candidates/v1",
        "batch_id": "NET-RSS-018",
        "generated_utc": utc(),
        "approved_plan_sha256": PLAN_SHA,
        "proposal_sha256": PROPOSAL_SHA,
        "health_gate_sha256": CONTROL17_ACCEPTANCE_SHA,
        "network_requests": 0,
        "targets": targets,
        "policy": plan.get("limits"),
        "selection": plan.get("selection"),
    }


def prepare() -> int:
    plan, aux = verify_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    candidates = build_candidates(plan, aux)
    config = {
        "schema": "continuous-wow-net-rss18-config/v1",
        "batch_id": "NET-RSS-018",
        "prepared_utc": utc(),
        "network_requests": 0,
        "inputs": aux["input_digests"],
        "targets": [{"rank": item["rank"], "target": item["target"], "operation": item["operation"], "cdx_query_url": item["cdx_query_url"], "saved_replay_url": item["saved_replay_url"]} for item in candidates["targets"]],
        "policy": {"max_targets": MAX_TARGETS, "max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW_SECONDS, "minimum_dispatch_seconds": MIN_INTERVAL, "minimum_free_bytes": MIN_FREE, "max_total_body_bytes": MAX_TOTAL, "max_entity_body_bytes": MAX_ENTITY, "direct_first_then_confirmed_transport": True, "automatic_redirects": 0, "manual_redirect_follow": 0, "late_windows": 0, "continuation_pages": 0, "tls_verification": "curl default verification enabled"},
    }
    write_json(OUT / "candidates.json", candidates)
    write_json(OUT / "config.json", config)
    print(json.dumps({"mode": "prepared", "network_requests": 0, "targets": [item["target"] for item in candidates["targets"]], "plan_sha256": PLAN_SHA, "health_gate_sha256": CONTROL17_ACCEPTANCE_SHA, "disk_free_bytes": free_bytes()}, ensure_ascii=False))
    return 0


def blank_result(item: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "rank": item["rank"], "target": item["target"], "query_original": item["query_original"], "year": item["year"], "month": item["month"], "operation": item["operation"], "source_menu": item["menu_evidence"], "query_url": item["cdx_query_url"],
        "cdx": {"query_performed": False, "source_status": None, "source_response_count": 0, "capture_index_count": 0, "eligible_status_200_count": 0, "redirect_index_count": 0, "capture_records": [], "selected_capture": None, "attempts": [], "resume_keys_observed": [], "resume_key_used": None, "continuation_followed": False},
        "selected_capture": None, "replay_attempt_count": 0, "replay_source_response_count": 0, "replay_hops": [], "category": "not_requested", "reason": reason, "actual_memento": None, "source_status": None, "content_type": None, "body_bytes": 0, "body_sha256": None, "validation": None, "entity_valid": False, "unrequested_reason": reason,
    }


def collect_attempts(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    for result in results:
        attempts.extend(result.get("cdx", {}).get("attempts") or [])
        for hop in result.get("replay_hops") or []:
            attempts.extend(hop.get("attempts") or [])
    return attempts


def gate_validation(results: list[dict[str, Any]], gate: Any, disk_before: int, disk_after: int) -> dict[str, Any]:
    attempts = collect_attempts(results)
    starts = sorted(datetime.fromisoformat(str(value["started_utc"]).replace("Z", "+00:00")).timestamp() for value in attempts if value.get("started_utc"))
    start_intervals = [starts[index] - starts[index - 1] for index in range(1, len(starts))]
    dispatch_intervals = [value.get("interval_since_previous_dispatch_seconds") for value in gate.dispatches if value.get("interval_since_previous_dispatch_seconds") is not None]
    compliant = all(float(value) >= MIN_INTERVAL for value in start_intervals + dispatch_intervals)
    return {"min_dispatch_interval_seconds": min(dispatch_intervals, default=None), "min_request_start_interval_seconds": min(start_intervals, default=None), "required_minimum_seconds": MIN_INTERVAL, "dispatch_intervals_compliant": all(float(value) >= MIN_INTERVAL for value in dispatch_intervals), "request_start_intervals_compliant": all(float(value) >= MIN_INTERVAL for value in start_intervals), "batch_policy_accepted": compliant and disk_before >= MIN_FREE and disk_after >= MIN_FREE, "dispatch_count": len(gate.dispatches), "dispatch_intervals": dispatch_intervals, "request_start_intervals": start_intervals}


def enrich_source_map(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for entry in entries:
        entry["batch_id"] = "NET-RSS-018"
        entry["action"] = "hold for parent review; entity remains only in this batch raw directory"
        evidence = entry.get("html_month_evidence") or {}
        if evidence:
            entry["article_month_evidence"] = evidence.get("article_month_evidence")
            entry["posted_date_count"] = evidence.get("article_posted_date_count")
            entry["posted_date_range"] = evidence.get("article_posted_date_range")
            entry["posted_date_month_counts"] = evidence.get("article_posted_date_month_counts")
            entry["h1_count"] = evidence.get("h1_count")
            entry["event_date_evidence"] = evidence.get("event_date_evidence")
    return entries


def render_summary(report: dict[str, Any], entries: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    targets: list[dict[str, Any]] = []
    for result in report["results"]:
        validation = result.get("validation") or {}
        observation = validation.get("body_observation") or {}
        evidence = validation.get("html_month_evidence") if validation.get("body_format") == "html" else observation.get("month_evidence")
        targets.append({"rank": result["rank"], "target": result["target"], "query_original": result["query_original"], "operation": result["operation"], "category": result["category"], "reason": result["reason"], "body_format": validation.get("body_format"), "title": observation.get("title"), "root": observation.get("root"), "item_count": observation.get("item_count"), "pubdates": observation.get("pubdates"), "month_evidence": evidence, "html_month_evidence": validation.get("html_month_evidence"), "capture_index_count": result["cdx"].get("capture_index_count"), "eligible_status_200_count": result["cdx"].get("eligible_status_200_count"), "redirect_index_count": result["cdx"].get("redirect_index_count"), "selected_capture_timestamp": (result.get("selected_capture") or {}).get("timestamp"), "actual_memento": result.get("actual_memento"), "source_status": result.get("source_status"), "content_type": result.get("content_type"), "body_bytes": result.get("body_bytes", 0), "body_sha256": result.get("body_sha256")})
    summary = {"schema": "continuous-wow-net-rss18-sanitized-summary/v1", "batch_id": "NET-RSS-018", "mode": "executed", "started_utc": report["started_utc"], "request_window_finished_utc": report["request_window_finished_utc"], "finished_utc": report["finished_utc"], "report_updated_utc": report["report_updated_utc"], "network_requests": report["transport_attempt_count"], "source_request_count": report["source_request_count"], "source_response_count": report["source_response_count"], "failed_attempt_count": report["failed_attempt_count"], "target_count": len(targets), "cdx_target_count": report["cdx_target_count"], "saved_replay_target_count": report["saved_replay_target_count"], "capture_index_count": report["capture_index_count"], "valid_payload_count": report["valid_entity_count"], "valid_rss_count": report["valid_rss_count"], "valid_html_count": report["valid_html_count"], "total_body_bytes": report["total_body_bytes"], "payload_body_bytes": report["payload_body_bytes"], "category_counts": report["category_counts"], "stop_reason": report["stop_reason"], "confirmed_transport": report["confirmed_transport"], "gate_validation": report["gate_validation"], "disk_free_bytes_before": report["preflight"]["disk_free_bytes_before"], "disk_free_bytes_after": report["preflight"]["disk_free_bytes_after"], "targets": targets, "valid_payloads": entries, "scope_note": "CDX classifications are limited to the declared exact pre-anchor window; the saved September 2006 replay uses its approved capture. No all-time absence claim is made; no late window or continuation was requested.", "raw_evidence_note": "Raw headers, traces, stderr and bodies remain local. Zero-byte no-response bodies are local placeholders, not source content; CONNECT responses are excluded; CDX length is index metadata, not payload bytes."}
    lines = ["# NET-RSS-018 sanitized summary", "", f"- Window: `{report['started_utc']}` to `{report['request_window_finished_utc']}`; report updated `{report['report_updated_utc']}`.", f"- Targets: {len(targets)} ({report['cdx_target_count']} CDX, {report['saved_replay_target_count']} saved replay); attempts {report['transport_attempt_count']}; source responses {report['source_response_count']}; CDX rows {report['capture_index_count']}; valid payloads {report['valid_entity_count']}.", f"- Body bytes total `{report['total_body_bytes']}`, valid payloads `{report['payload_body_bytes']}`; stop `{report['stop_reason']}`.", f"- Gate min dispatch `{report['gate_validation']['min_dispatch_interval_seconds']}`, min request-start `{report['gate_validation']['min_request_start_interval_seconds']}`, accepted `{report['gate_validation']['batch_policy_accepted']}`.", "", "| Rank | Target | Operation | Category | Format | CDX rows | Selected | Memento | PubDate/title evidence |", "|---:|---|---|---|---|---:|---|---|---|"]
    for target in targets:
        evidence = target.get("month_evidence") or {}
        state = evidence.get("state") or ((evidence.get("article_month_evidence") or {}).get("state")) or ((evidence.get("posted_date_evidence") or {}).get("state")) or "unknown"
        lines.append(f"| {target['rank']} | `{target['target']}` | `{target['operation']}` | `{target['category']}` | `{target.get('body_format') or ''}` | {target.get('capture_index_count') or 0} | `{target.get('selected_capture_timestamp') or ''}` | `{target.get('actual_memento') or ''}` | `{state}` |")
    for target in targets:
        if target.get("body_format") == "html":
            evidence = target.get("html_month_evidence") or {}
            lines.append(f"- HTML `{target['target']}`: title `{target.get('title') or ''}`; full h1 `{evidence.get('h1_count') or 0}`, posted-date `{evidence.get('article_posted_date_count') or 0}`, months `{json.dumps(evidence.get('article_posted_date_month_counts') or {}, sort_keys=True)}`, range `{json.dumps(evidence.get('article_posted_date_range'), sort_keys=True)}`; event/description dates kept separately `{json.dumps((evidence.get('event_date_tokens') or [])[:5], ensure_ascii=False)}`.")
        elif target.get("body_format") == "rss_xml":
            evidence = target.get("month_evidence") or {}
            lines.append(f"- RSS/XML `{target['target']}`: root `{target.get('root') or ''}`, title `{target.get('title') or ''}`, items `{target.get('item_count') or 0}`, pubDate count `{len(target.get('pubdates') or [])}`, month state `{evidence.get('state') or 'unknown'}`; body format was determined from the payload.")
    lines.extend(["", "No CDX continuation, late-window request, redirect follow, or integration was performed. Valid entities remain isolated for parent review."])
    return summary, "\n".join(lines) + "\n"


def execute() -> int:
    if not (OUT / "candidates.json").is_file() or not (OUT / "config.json").is_file():
        raise RuntimeError("run --prepare before --execute")
    if (OUT / "batch-report.json").exists():
        raise RuntimeError("refusing to repeat NET-RSS-018 after batch-report.json exists")
    plan, aux = verify_inputs()
    candidates = read_json(OUT / "candidates.json")
    if candidates.get("approved_plan_sha256") != PLAN_SHA or candidates.get("network_requests") != 0 or len(candidates.get("targets") or []) != MAX_TARGETS:
        raise RuntimeError("RSS018 candidate declaration drift")
    disk_before = free_bytes()
    if disk_before < MIN_FREE:
        raise RuntimeError(f"D free space below floor: {disk_before}")
    started_utc = utc()
    window_started = time.monotonic()
    state = core.RunState(window_started)
    gate_not_before = datetime.now(timezone.utc) - timedelta(seconds=1)
    journal = {"schema": "continuous-wow-net-rss18-dispatch-log/v1", "batch_id": "NET-RSS-018", "simulation": False, "policy": {"minimum_dispatch_interval_seconds": MIN_INTERVAL, "max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW_SECONDS, "redirects": 0, "late_windows": 0, "continuation_pages": 0}, "health_gate": {"path": str(CONTROL17_ACCEPTANCE.relative_to(ROOT)).replace("\\", "/"), "sha256": CONTROL17_ACCEPTANCE_SHA, "accepted": True}, "disk_preflight": {"checked_utc": started_utc, "disk_free_bytes": disk_before, "minimum_free_bytes": MIN_FREE}, "dispatches": []}
    gate = gate_mod.GateState(gate_not_before, journal_path=OUT / "dispatch-log.json", journal=journal)
    gate.persist()
    results: list[dict[str, Any]] = []
    transport = "direct"
    execution_error: str | None = None
    try:
        for item in candidates["targets"]:
            if state.stop_reason:
                results.append(blank_result(item, state.stop_reason))
                continue
            if item.get("cdx_query_url") is None:
                result, transport = rss16.known_replay_result(item, transport, state, gate, window_started)
                result["cdx"]["saved_capture_source"] = "rss18-approved-plan.selected_capture"
            else:
                query_attempts, transport = rss16.issue_confirmed(item["cdx_query_url"], "cdx", item["query_original"], transport, state, gate, window_started)
                result, transport = rss16.result_from_query(item, query_attempts, transport, state, gate, window_started)
            results.append(result)
    except Exception as exc:  # pragma: no cover - transport/OS dependent
        execution_error = f"{type(exc).__name__}: {exc}"
        for item in candidates["targets"][len(results):]:
            results.append(blank_result(item, "execution_error_before_request"))
    finally:
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=free_bytes)
    request_window_finished = utc()
    disk_after = free_bytes()
    entries = enrich_source_map(rss16.source_map(results))
    categories = dict(sorted(Counter(str(result.get("category")) for result in results).items()))
    payload_bytes = sum(int(entry.get("body_bytes") or 0) for entry in entries)
    gate_info = gate_validation(results, gate, disk_before, disk_after)
    cdx_target_count = sum(bool(result.get("cdx", {}).get("query_performed")) for result in results)
    saved_replay_count = sum(result.get("operation") == "replay_saved_capture_without_CDX" for result in results)
    valid_rss_count = sum(result.get("category") == "valid_rss_payload" for result in results)
    valid_html_count = sum(result.get("category") == "valid_html_payload" for result in results)
    stop_reason = state.stop_reason or ("execution_error" if execution_error else "completed")
    report = {"schema": "continuous-wow-net-rss18-batch-report/v1", "batch_id": "NET-RSS-018", "mode": "executed", "started_utc": started_utc, "request_window_finished_utc": request_window_finished, "finished_utc": request_window_finished, "report_updated_utc": utc(), "inputs": aux["input_digests"], "policy": candidates["policy"], "transport": {"confirmed_transport": transport, "curl": r"C:\Windows\System32\curl.exe", "proxy": PROXY, "tls_verification": "curl default verification enabled"}, "confirmed_transport": transport, "preflight": {"disk_free_bytes_before": disk_before, "disk_free_bytes_after": disk_after, "minimum_free_bytes": MIN_FREE}, "postflight": postflight, "target_count": len(results), "unique_target_count": len({result["query_original"] for result in results}), "cdx_target_count": cdx_target_count, "saved_replay_target_count": saved_replay_count, "category_counts": categories, "transport_attempt_count": state.attempts, "source_request_count": state.attempts, "failed_attempt_count": state.failed_attempts, "source_response_count": state.source_responses, "cdx_source_response_count": sum(result.get("cdx", {}).get("source_response_count", 0) for result in results), "replay_source_response_count": sum(result.get("replay_source_response_count", 0) for result in results), "capture_index_count": sum(result.get("cdx", {}).get("capture_index_count", 0) for result in results), "valid_entity_count": len(entries), "valid_rss_count": valid_rss_count, "valid_html_count": valid_html_count, "total_body_bytes": state.total_body_bytes, "payload_body_bytes": payload_bytes, "stop_reason": stop_reason, "stop_detail": state.stop_detail, "rate_limit": state.rate_limit, "execution_error": execution_error, "gate_validation": gate_info, "resume_key_policy": {"observed_saved": True, "used": False, "continuation_pages_requested": 0}, "dispatch_log": relative(OUT / "dispatch-log.json"), "results": results, "raw_evidence_note": "Raw headers, traces, stderr and bodies remain only below this batch raw directory. A zero-byte no-response body is a local placeholder, not source content; CONNECT is excluded; CDX length is index metadata, not payload bytes."}
    write_json(OUT / "batch-report.json", report)
    report_sha = sha256_file(OUT / "batch-report.json")
    write_json(OUT / "payload-source-map.json", {"schema": "continuous-wow-net-rss18-payload-source-map/v1", "batch_id": "NET-RSS-018", "report_sha256": report_sha, "entries": entries, "entity_count": len(entries), "integration_held": True})
    redirects: list[dict[str, Any]] = []
    for result in results:
        for row in result.get("cdx", {}).get("capture_records") or []:
            if row.get("statuscode_int") in REDIRECT_CODES:
                redirects.append({"evidence_type": "cdx_index_redirect_row", "target": result["target"], "timestamp": row.get("timestamp"), "original": row.get("original"), "statuscode": row.get("statuscode"), "mimetype": row.get("mimetype"), "action": "index evidence only; no replay/follow"})
        for hop in result.get("replay_hops") or []:
            for attempt in hop.get("attempts") or []:
                if attempt.get("source_status") in REDIRECT_CODES:
                    redirects.append({"evidence_type": "replay_redirect", "target": result["target"], "source_status": attempt.get("source_status"), "location": attempt.get("location"), "action": "redirect observed; no follow"})
    write_json(OUT / "redirect-evidence.json", {"schema": "continuous-wow-net-rss18-redirect-evidence/v1", "entries": redirects})
    summary, markdown = render_summary(report, entries)
    write_json(OUT / "sanitized-summary.json", summary)
    (OUT / "sanitized-summary.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"mode": "executed", "batch_id": "NET-RSS-018", "attempts": state.attempts, "source_responses": state.source_responses, "cdx_rows": report["capture_index_count"], "valid_entities": len(entries), "valid_rss": valid_rss_count, "valid_html": valid_html_count, "categories": categories, "stop_reason": stop_reason, "min_dispatch_interval": gate_info["min_dispatch_interval_seconds"], "min_request_start_interval": gate_info["min_request_start_interval_seconds"], "execution_error": execution_error}, ensure_ascii=False))
    return 1 if execution_error else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if bool(args.prepare) == bool(args.execute):
        parser.error("choose exactly one")
    return prepare() if args.prepare else execute()


if __name__ == "__main__":
    raise SystemExit(main())

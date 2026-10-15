"""NET-CONTROL-017: one bounded CSS replay using the accepted control14 transport.

Preparation is offline.  Execution has one fixed replay target, direct first
and then one existing proxy attempt only after a transport failure.  The
accepted core transport and control7 dispatch gate are imported; this file
owns the new output and journal directories.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
PLAN = ROOT / "research/continuous-recovery-20261015/control17-approved-plan.json"
RSS16_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/rss16-acceptance.json"
RSS16_REPORT = ROOT / "research/continuous-recovery-20261015/network-rss16/batch-report.json"
RSS16_JOURNAL = ROOT / "research/continuous-recovery-20261015/network-rss16/dispatch-log.json"
CONTROL14 = ROOT / "research/continuous-recovery-20261015/network-control14/control14.py"
PROXY = "http://127.0.0.1:7890"
PLAN_SHA = "3c1ba8c3c0f8ee680c68a2eb73f7a1eb332203f8d46c48b605a53be64b867f9a"
NOT_BEFORE = "2026-10-15T12:11:30.115333+00:00"
TARGET = "http://www.worldofwarcraft.com/news/newsarchive.css"
CAPTURED_ORIGINAL = "http://www.worldofwarcraft.com:80/news/newsarchive.css"
REPLAY_URL = "https://web.archive.org/web/20070322234302id_/http://www.worldofwarcraft.com:80/news/newsarchive.css"
EXPECTED_BYTES = 109
EXPECTED_SHA256 = "69915a4eea19ec455a60b89c64ed661fc55d48bc3a724bdffcc91bd2d617aa7b"
EXPECTED_MIME = "text/css"
EXPECTED_MEMENTO = "2007-03-22T23:43:02+00:00"
EXPECTED_CDX_DIGEST = "67KDGC7ADIDSHVIZKCXTAZYR24FOAYWP"
MAX_ATTEMPTS = 2
WINDOW_SECONDS = 120
INTERVAL_SECONDS = 1.35
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY_BYTES = 16 * 1024
MAX_ENTITY_BODY_BYTES = 16 * 1024
STOP_HTTP_CODES = {429, 503}
USER_AGENT = "wow-recovery-control17/20261015"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load accepted helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import control14 once and reuse its accepted core3 transport and control7 gate.
accepted = load_module(CONTROL14, "control17_control14_helpers")
core = accepted.core
gate_mod = accepted.gate_mod
core.OUT, core.RAW, core.PROXY, core.USER_AGENT = OUT, RAW, PROXY, USER_AGENT
core.MAX_ATTEMPTS = MAX_ATTEMPTS
core.WINDOW_SECONDS = WINDOW_SECONDS
core.MIN_INTERVAL_SECONDS = 0.0
core.MIN_FREE_BYTES = MIN_FREE_BYTES
core.MAX_TOTAL_BODY_BYTES = MAX_TOTAL_BODY_BYTES
core.MAX_ENTITY_BODY_BYTES = MAX_ENTITY_BODY_BYTES
gate_mod.OUT, gate_mod.RAW, gate_mod.INTERVAL_SECONDS = OUT, RAW, INTERVAL_SECONDS


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


def body(attempt: dict[str, Any] | None) -> bytes:
    if not attempt or not attempt.get("executed"):
        return b""
    raw_path = str((attempt.get("raw") or {}).get("body") or "")
    path = (OUT / raw_path).resolve()
    if OUT.resolve() not in path.parents:
        raise RuntimeError("raw body path escaped control17 directory")
    return path.read_bytes() if path.is_file() else b""


def guard_snapshot() -> dict[str, Any]:
    checked = datetime.now(timezone.utc)
    not_before = datetime.fromisoformat(NOT_BEFORE)
    remaining = (not_before - checked).total_seconds()
    return {
        "checked_utc": checked.isoformat(),
        "checked_monotonic": time.monotonic(),
        "not_before_utc": NOT_BEFORE,
        "remaining_seconds": max(0.0, remaining),
        "satisfied": checked >= not_before,
    }


def verify_inputs() -> dict[str, Any]:
    if sha256_file(PLAN) != PLAN_SHA:
        raise RuntimeError("control17 approved plan SHA mismatch")
    plan = read_json(PLAN)
    acceptance = read_json(RSS16_ACCEPTANCE)
    if plan.get("task_id") != "NET-CONTROL-017" or plan.get("replay_url") != REPLAY_URL:
        raise RuntimeError("control17 plan identity or replay URL mismatch")
    if plan.get("guard", {}).get("not_before_utc") != NOT_BEFORE:
        raise RuntimeError("control17 not-before guard drift")
    expected = plan.get("expected") or {}
    if expected.get("source_HTTP") != 200 or expected.get("bytes") != EXPECTED_BYTES or expected.get("sha256") != EXPECTED_SHA256 or expected.get("mime") != EXPECTED_MIME or expected.get("actual_memento") != EXPECTED_MEMENTO:
        raise RuntimeError("control17 expected CSS identity drift")
    limits = plan.get("limits") or {}
    if limits.get("max_attempts") != MAX_ATTEMPTS or limits.get("CDX_queries") != 0 or limits.get("redirects") != 0:
        raise RuntimeError("control17 limits drift")
    if acceptance.get("accepted") is not True or acceptance.get("network_requests_by_acceptance") != 0:
        raise RuntimeError("RSS016 acceptance is not accepted offline evidence")
    if sha256_file(RSS16_REPORT) != acceptance.get("report_sha256"):
        raise RuntimeError("RSS016 report SHA does not match acceptance")
    if sha256_file(RSS16_JOURNAL) != acceptance.get("journal_sha256"):
        raise RuntimeError("RSS016 journal SHA does not match acceptance")
    return {
        "plan": digest(PLAN),
        "rss16_acceptance": digest(RSS16_ACCEPTANCE),
        "rss16_report": digest(RSS16_REPORT),
        "rss16_journal": digest(RSS16_JOURNAL),
        "control14_driver": digest(CONTROL14),
        "acceptance": acceptance,
    }


def prepare() -> int:
    inputs = verify_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    guard = guard_snapshot()
    policy = {
        "direct_first": True,
        "proxy": PROXY,
        "max_attempts": MAX_ATTEMPTS,
        "network_window_seconds": WINDOW_SECONDS,
        "minimum_dispatch_monotonic_seconds": INTERVAL_SECONDS,
        "minimum_free_bytes": MIN_FREE_BYTES,
        "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "tls_verification": "curl default verification enabled",
        "redirects": 0,
        "cdx_queries": 0,
        "stop_http_codes": sorted(STOP_HTTP_CODES),
    }
    write_json(OUT / "config.json", {"schema": "continuous-wow-network-control17-config/v1", "batch_id": "NET-CONTROL-017", "prepared_utc": utc(), "network_requests": 0, "not_before_utc": NOT_BEFORE, "guard_snapshot": guard, "target": TARGET, "captured_original_url": CAPTURED_ORIGINAL, "replay_url": REPLAY_URL, "expected": {"source_HTTP": 200, "mime": EXPECTED_MIME, "bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256, "actual_memento": EXPECTED_MEMENTO, "cdx_digest_reference": EXPECTED_CDX_DIGEST}, "policy": policy, "inputs": inputs})
    write_json(OUT / "candidates.json", {"schema": "continuous-wow-network-control17-candidates/v1", "batch_id": "NET-CONTROL-017", "network_requests": 0, "target": TARGET, "captured_original_url": CAPTURED_ORIGINAL, "replay_url": REPLAY_URL, "source_evidence": {"approved_plan": inputs["plan"], "rss16_acceptance": inputs["rss16_acceptance"], "accepted_cdx_digest": EXPECTED_CDX_DIGEST}})
    print(json.dumps({"mode": "prepared", "network_requests": 0, "guard": guard, "plan_sha256": inputs["plan"]["sha256"]}, ensure_ascii=False))
    return 0


def issue(transport: str, state: Any, gate: Any, window_started: float) -> dict[str, Any]:
    if not state.check_limits() or time.monotonic() - window_started >= WINDOW_SECONDS:
        return {"executed": False, "attempt": state.attempts + 1, "kind": "replay", "target_key": TARGET, "transport": transport, "url": REPLAY_URL, "unrequested_reason": state.stop_reason or "limit_before_request"}
    attempt_number = state.attempts + 1
    gate_record = gate.before_dispatch(attempt_number, transport, TARGET)
    result = core.run_request(REPLAY_URL, transport, "replay", TARGET, state, attempt_number)
    result.update({"dispatch_utc": gate_record["dispatch_utc"], "dispatch_monotonic": gate_record["dispatch_monotonic"], "dispatch_interval_seconds": gate_record["interval_since_previous_dispatch_seconds"], "gate_persisted_before_transport": gate_record["persisted_before_transport"]})
    result["local_zero_byte_body_placeholder"] = bool(result.get("source_status") is None and not body(result))
    result["body_is_source_response"] = result.get("source_status") is not None
    return result


def validate_css(attempt: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    payload = body(attempt)
    content_type = attempt.get("content_type")
    mime = str(content_type or "").split(";", 1)[0].strip().lower() or None
    html_info = core.html_info(payload, content_type)
    validation: dict[str, Any] = {"body_bytes": len(payload), "body_sha256": hashlib.sha256(payload).hexdigest() if payload else None, "content_type": content_type, "mime": mime, "actual_memento": attempt.get("memento_datetime"), "html_info": html_info, "expected_bytes": EXPECTED_BYTES, "expected_sha256": EXPECTED_SHA256, "expected_mime": EXPECTED_MIME, "expected_memento": EXPECTED_MEMENTO}
    if attempt.get("transport_error") or attempt.get("source_status") is None:
        return "transport_error", attempt.get("transport_reason") or "no_source_http_response", validation
    if attempt.get("source_status") in STOP_HTTP_CODES:
        validation["retry_after"] = attempt.get("retry_after")
        return "rate_limited", f"source_status_{attempt.get('source_status')}", validation
    if attempt.get("source_status") != 200:
        return "soft404", f"source_status_{attempt.get('source_status')}", validation
    if attempt.get("memento_datetime") != EXPECTED_MEMENTO:
        return "soft404", "actual_memento_mismatch", validation
    if mime != EXPECTED_MIME or html_info.get("is_html") or html_info.get("markers"):
        return "soft404", "not_text_css_or_html_error", validation
    if len(payload) != EXPECTED_BYTES or hashlib.sha256(payload).hexdigest() != EXPECTED_SHA256:
        return "soft404", "body_length_or_sha256_mismatch", validation
    validation["css_nonempty"] = bool(payload.strip())
    return "valid_stylesheet", "validated_expected_css_source", validation


def public_attempt(value: dict[str, Any]) -> dict[str, Any]:
    output = accepted.public(value)
    output["gate_persisted_before_transport"] = value.get("gate_persisted_before_transport")
    output["body_is_source_response"] = value.get("body_is_source_response")
    output["local_zero_byte_body_placeholder"] = value.get("local_zero_byte_body_placeholder")
    return output


def write_outputs(inputs: dict[str, Any], attempts: list[dict[str, Any]], result: dict[str, Any], state: Any, gate: Any, guard: dict[str, Any], disk_before: int, disk_after: int, started_utc: str, finished_utc: str, postflight: dict[str, Any], execution_error: str | None) -> None:
    starts = [datetime.fromisoformat(str(value["started_utc"])) for value in attempts if value.get("started_utc")]
    start_intervals = [(starts[index] - starts[index - 1]).total_seconds() for index in range(1, len(starts))]
    gate_intervals = [value.get("interval_since_previous_dispatch_seconds") for value in gate.dispatches if value.get("interval_since_previous_dispatch_seconds") is not None]
    start_min = min(start_intervals) if start_intervals else None
    gate_min = min(gate_intervals) if gate_intervals else None
    entity = None
    if result.get("category") == "valid_stylesheet":
        final = next((value for value in reversed(attempts) if value.get("source_status") is not None), {})
        entity = {"target": TARGET, "query_original_url": TARGET, "captured_original_url": CAPTURED_ORIGINAL, "actual_memento": result.get("actual_memento"), "source_status": result.get("source_status"), "content_type": result.get("content_type"), "body_bytes": result.get("body_bytes"), "body_sha256": result.get("body_sha256"), "raw_body_path": (final.get("raw") or {}).get("body"), "raw_headers_path": (final.get("raw") or {}).get("headers"), "capture_timestamp": "20070322234302", "cdx_digest": EXPECTED_CDX_DIGEST, "cdx_digest_source": "approved NET013/NET014 evidence; no CDX request in NET017", "validation": result.get("validation"), "integration": "control evidence only; no integration"}
    elapsed = (datetime.fromisoformat(finished_utc) - datetime.fromisoformat(started_utc)).total_seconds()
    report = {"schema": "continuous-wow-network-control17-report/v1", "batch_id": "NET-CONTROL-017", "mode": "executed", "started_utc": started_utc, "finished_utc": finished_utc, "request_window_finished_utc": finished_utc, "request_window_elapsed_seconds": round(elapsed, 3), "report_updated_utc": utc(), "inputs": inputs, "guard": guard, "target": TARGET, "replay_url": REPLAY_URL, "captured_original_url": CAPTURED_ORIGINAL, "expected": {"source_HTTP": 200, "bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256, "mime": EXPECTED_MIME, "actual_memento": EXPECTED_MEMENTO, "cdx_digest_reference": EXPECTED_CDX_DIGEST}, "attempts": [public_attempt(value) for value in attempts], "source_response_count": sum(value.get("source_status") is not None for value in attempts), "source_request_count": state.attempts, "transport_attempt_count": state.attempts, "failed_attempt_count": state.failed_attempts, "total_body_bytes": state.total_body_bytes, "payload_body_bytes": result.get("body_bytes", 0) if result.get("category") == "valid_stylesheet" else 0, "category": result.get("category"), "reason": result.get("reason"), "actual_memento": result.get("actual_memento"), "source_status": result.get("source_status"), "content_type": result.get("content_type"), "body_bytes": result.get("body_bytes"), "body_sha256": result.get("body_sha256"), "validation": result.get("validation"), "preflight": {"disk_free_bytes_before": disk_before, "disk_free_bytes_after": disk_after, "minimum_free_bytes": MIN_FREE_BYTES}, "dispatch_count": len(gate.dispatches), "minimum_request_start_interval_seconds": start_min, "gate_dispatch_minimum_interval_seconds": gate_min, "minimum_dispatch_interval_required_seconds": INTERVAL_SECONDS, "batch_policy_accepted": guard["satisfied"] and state.attempts <= MAX_ATTEMPTS and (start_min is None or start_min >= INTERVAL_SECONDS) and (gate_min is None or gate_min >= INTERVAL_SECONDS) and disk_before >= MIN_FREE_BYTES and disk_after >= MIN_FREE_BYTES, "postflight": postflight, "stop_reason": state.stop_reason or ("completed" if result.get("category") == "valid_stylesheet" else result.get("reason")), "rate_limit": state.rate_limit, "execution_error": execution_error, "source_map_entry": entity, "raw_evidence_note": "No CDX query or redirect was performed. Zero-byte no-response body is a local placeholder, not source response content; CONNECT 200 is excluded."}
    write_json(OUT / "control-report.json", report)
    report_sha = sha256_file(OUT / "control-report.json")
    source_map = {"schema": "continuous-wow-network-control17-source-map/v1", "batch_id": "NET-CONTROL-017", "report_sha256": report_sha, "entries": [entity] if entity else [], "entity_count": 1 if entity else 0, "integration_held": True}
    write_json(OUT / "control-source-map.json", source_map)
    summary = {"schema": "continuous-wow-network-control17-sanitized-summary/v1", "batch_id": "NET-CONTROL-017", "report_sha256": report_sha, "finished_utc": finished_utc, "report_updated_utc": report["report_updated_utc"], "network_requests": state.attempts, "source_response_count": report["source_response_count"], "failed_attempt_count": state.failed_attempts, "category": result.get("category"), "reason": result.get("reason"), "actual_memento": result.get("actual_memento"), "source_status": result.get("source_status"), "content_type": result.get("content_type"), "body_bytes": result.get("body_bytes"), "body_sha256": result.get("body_sha256"), "disk_free_bytes_before": disk_before, "disk_free_bytes_after": disk_after, "guard_satisfied": guard["satisfied"], "minimum_request_start_interval_seconds": start_min, "gate_dispatch_minimum_interval_seconds": gate_min, "batch_policy_accepted": report["batch_policy_accepted"], "stop_reason": report["stop_reason"], "raw_evidence_note": report["raw_evidence_note"]}
    write_json(OUT / "sanitized-summary.json", summary)
    rows = ["# NET-CONTROL-017 sanitized summary", "", f"Category: `{result.get('category')}`; source responses: `{report['source_response_count']}`; attempts: `{state.attempts}`.", f"Actual Memento: `{result.get('actual_memento') or ''}`; MIME: `{result.get('content_type') or ''}`; bytes: `{result.get('body_bytes')}`; SHA256: `{result.get('body_sha256') or ''}`.", f"Guard satisfied: `{guard['satisfied']}`; request-start minimum: `{start_min}`; gate dispatch minimum: `{gate_min}`; policy accepted: `{report['batch_policy_accepted']}`.", "", "| attempt | transport | source status | curl exit | bytes | Memento |", "|---:|---|---:|---:|---:|---|"]
    rows.extend(f"| {value.get('attempt')} | {value.get('transport')} | {value.get('source_status') or ''} | {value.get('curl_exit')} | {value.get('body_bytes')} | {value.get('memento_datetime') or ''} |" for value in attempts)
    rows.extend(["", "No CDX query, redirect follow, or integration was performed. Raw headers, traces and bodies remain local; zero-byte no-response bodies are local placeholders."])
    (OUT / "sanitized-summary.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def execute() -> int:
    if not (OUT / "config.json").is_file() or not (OUT / "candidates.json").is_file():
        raise RuntimeError("run --prepare before --execute")
    if (OUT / "control-report.json").exists():
        raise RuntimeError("refusing to repeat NET-CONTROL-017 after report exists")
    inputs = verify_inputs()
    config = read_json(OUT / "config.json")
    if config.get("network_requests") != 0 or config.get("replay_url") != REPLAY_URL:
        raise RuntimeError("prepared config drift")
    guard = guard_snapshot()
    if not guard["satisfied"]:
        raise RuntimeError("not_before guard is not satisfied; no network dispatched")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    disk_before = free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError("disk free below threshold")
    started_utc = utc()
    window_started = time.monotonic()
    state = core.RunState(window_started)
    journal = {"schema": "continuous-wow-network-control17-dispatch-log/v1", "batch_id": "NET-CONTROL-017", "simulation": False, "policy": {"minimum_dispatch_monotonic_seconds": INTERVAL_SECONDS, "max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW_SECONDS, "redirects": 0, "cdx_queries": 0}, "guard_preflight": guard, "disk_preflight": {"checked_utc": started_utc, "disk_free_bytes": disk_before, "minimum_free_bytes": MIN_FREE_BYTES}, "dispatches": []}
    gate = gate_mod.GateState(datetime.fromisoformat(NOT_BEFORE), journal_path=OUT / "dispatch-log.json", journal=journal)
    gate.persist()
    attempts: list[dict[str, Any]] = []
    postflight: dict[str, Any] = {}
    execution_error: str | None = None
    try:
        direct = issue("direct", state, gate, window_started)
        attempts.append(direct)
        if direct.get("executed") and direct.get("transport_error") and direct.get("source_status") is None and not state.stop_reason:
            attempts.append(issue("proxy", state, gate, window_started))
    except Exception as exc:  # pragma: no cover - transport/OS dependent
        execution_error = f"{type(exc).__name__}: {exc}"
    finally:
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=free_bytes)
    final = next((value for value in reversed(attempts) if value.get("executed")), attempts[-1] if attempts else {})
    if final.get("executed"):
        category, reason, validation = validate_css(final)
        result = {"category": category, "reason": reason, "validation": validation, "actual_memento": final.get("memento_datetime"), "source_status": final.get("source_status"), "content_type": final.get("content_type"), "body_bytes": len(body(final)), "body_sha256": hashlib.sha256(body(final)).hexdigest() if body(final) else None}
    else:
        result = {"category": "not_requested", "reason": final.get("unrequested_reason", "no_attempt"), "validation": None, "actual_memento": None, "source_status": None, "content_type": None, "body_bytes": 0, "body_sha256": None}
    finished_utc = utc()
    disk_after = free_bytes()
    write_outputs(inputs, attempts, result, state, gate, guard, disk_before, disk_after, started_utc, finished_utc, postflight, execution_error)
    print(json.dumps({"mode": "executed", "batch_id": "NET-CONTROL-017", "network_requests": state.attempts, "source_responses": state.source_responses, "failed_attempts": state.failed_attempts, "category": result["category"], "actual_memento": result["actual_memento"], "body_bytes": result["body_bytes"], "body_sha256": result["body_sha256"], "disk_free_before": disk_before, "disk_free_after": disk_after, "execution_error": execution_error}, ensure_ascii=False))
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

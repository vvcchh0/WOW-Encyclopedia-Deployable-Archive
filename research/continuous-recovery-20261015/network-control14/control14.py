from __future__ import annotations
import argparse, hashlib, importlib.util, json, shutil, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
ACCEPT = ROOT / "research/continuous-recovery-20261015/news-assets13-acceptance.json"
SELECTED = ROOT / "research/continuous-recovery-20261015/selected-news-assets13-source-map.json"
REPORT = ROOT / "research/continuous-recovery-20261015/network-news-assets13/batch-report.json"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
ACCEPT_SHA = "e9748d3a9f7a5d2483766262856c621fbfa05a8a2bb58d3ebd77b51161e5099c"
SELECTED_SHA = "08f6e4bfc836eb56c4704c6f23582f1bc3f37a4d985d2dbde66ac281f649b8a3"
REPORT_SHA = "64b750567be81b246e770547b05555244726643874dcd93412a544307f3e29db"
NOT_BEFORE = "2026-10-15T11:32:57.032434+00:00"
TARGET = "http://www.worldofwarcraft.com/news/newsarchive.css"
CAPTURED_ORIGINAL = "http://www.worldofwarcraft.com:80/news/newsarchive.css"
REPLAY_URL = "https://web.archive.org/web/20070322234302id_/http://www.worldofwarcraft.com:80/news/newsarchive.css"
EXPECTED_MEMENTO = "2007-03-22T23:43:02+00:00"
EXPECTED_BYTES = 109
EXPECTED_SHA256 = "69915a4eea19ec455a60b89c64ed661fc55d48bc3a724bdffcc91bd2d617aa7b"
EXPECTED_MIME = "text/css"
EXPECTED_CDX_DIGEST = "67KDGC7ADIDSHVIZKCXTAZYR24FOAYWP"
PROXY = "http://127.0.0.1:7890"
UA = "wow-recovery-control14/20261015"
MAX_ATTEMPTS, WINDOW, INTERVAL = 2, 120, 1.35
MIN_FREE, MAX_TOTAL, MAX_ENTITY = 11_005_853_696, 16 * 1024, 16 * 1024
STOP = {429, 503}

def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load " + str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

core = load(CORE_PATH, "control14_core")
gate_mod = load(GATE_PATH, "control14_gate")
core.OUT, core.RAW, core.USER_AGENT, core.PROXY = OUT, RAW, UA, PROXY
core.MAX_ATTEMPTS, core.WINDOW_SECONDS, core.MIN_INTERVAL_SECONDS = MAX_ATTEMPTS, WINDOW, 0.0
core.MIN_FREE_BYTES, core.MAX_TOTAL_BODY_BYTES, core.MAX_ENTITY_BODY_BYTES = MIN_FREE, MAX_TOTAL, MAX_ENTITY
gate_mod.OUT, gate_mod.RAW, gate_mod.INTERVAL_SECONDS = OUT, RAW, INTERVAL

def utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def free() -> int:
    return int(shutil.disk_usage(OUT).free)

def body(x: dict[str, Any] | None) -> bytes:
    if not x:
        return b""
    p = OUT / str((x.get("raw") or {}).get("body") or "")
    return p.read_bytes() if p.exists() else b""

def inputs() -> dict[str, Any]:
    return {
        "news-assets13-acceptance.json": {"path": str(ACCEPT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(ACCEPT), "bytes": ACCEPT.stat().st_size},
        "selected-news-assets13-source-map.json": {"path": str(SELECTED.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(SELECTED), "bytes": SELECTED.stat().st_size},
        "news-assets13-batch-report.json": {"path": str(REPORT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(REPORT), "bytes": REPORT.stat().st_size},
    }

def verify_inputs() -> dict[str, Any]:
    got = inputs()
    if got["news-assets13-acceptance.json"]["sha256"] != ACCEPT_SHA:
        raise RuntimeError("NET013 acceptance SHA drift")
    if got["selected-news-assets13-source-map.json"]["sha256"] != SELECTED_SHA:
        raise RuntimeError("NET013 selected source-map SHA drift")
    if got["news-assets13-batch-report.json"]["sha256"] != REPORT_SHA:
        raise RuntimeError("NET013 batch report SHA drift")
    acc = read(ACCEPT)
    if acc.get("accepted") is not True or acc.get("payloads_accepted") is not True:
        raise RuntimeError("NET013 payload acceptance missing")
    if acc.get("next_control_not_before_utc") != NOT_BEFORE:
        raise RuntimeError("NET013 cooldown evidence mismatch")
    source = read(SELECTED)
    entry = next((x for x in source.get("entries") or [] if x.get("logical_url") == TARGET), None)
    if not entry:
        raise RuntimeError("accepted CSS source-map entry missing")
    if entry.get("captured_original_url") != CAPTURED_ORIGINAL or entry.get("actual_timestamp") != "20070322234302":
        raise RuntimeError("captured original/timestamp mismatch")
    if entry.get("body_bytes") != EXPECTED_BYTES or entry.get("body_sha256") != EXPECTED_SHA256 or entry.get("mime") != EXPECTED_MIME:
        raise RuntimeError("accepted CSS expected entity mismatch")
    return {"input_digests": got, "acceptance": acc, "source_entry": entry}

def guard_snapshot() -> dict[str, Any]:
    checked_utc = datetime.now(timezone.utc)
    not_before = datetime.fromisoformat(NOT_BEFORE)
    remaining = max(0.0, (not_before - checked_utc).total_seconds())
    return {"checked_utc": checked_utc.isoformat(), "checked_monotonic": time.monotonic(), "not_before_utc": NOT_BEFORE, "remaining_seconds": remaining, "satisfied": checked_utc >= not_before}

def public(x: dict[str, Any]) -> dict[str, Any]:
    return {k: x.get(k) for k in ("attempt", "kind", "transport", "url", "started_utc", "finished_utc", "dispatch_utc", "dispatch_monotonic", "dispatch_interval_seconds", "curl_exit", "source_status", "connect_status", "content_type", "location", "retry_after", "memento_datetime", "body_bytes", "body_sha256", "transport_error", "transport_reason", "local_zero_byte_body_placeholder", "body_is_source_response", "raw")}

def valid_css(x: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    b = body(x)
    mime = (x.get("content_type") or "").split(";", 1)[0].strip().lower()
    html = core.html_info(b, x.get("content_type"))
    val = {"body_bytes": len(b), "body_sha256": hashlib.sha256(b).hexdigest() if b else None, "content_type": x.get("content_type"), "mime": mime or None, "actual_memento": x.get("memento_datetime"), "html_info": html, "expected_bytes": EXPECTED_BYTES, "expected_sha256": EXPECTED_SHA256, "expected_memento": EXPECTED_MEMENTO}
    if x.get("transport_error") or x.get("source_status") is None:
        return "transport_error", x.get("transport_reason") or "curl_or_tls_failure", val
    if x.get("source_status") in STOP:
        val["retry_after"] = x.get("retry_after")
        return "rate_limited", "source_status_" + str(x.get("source_status")), val
    if x.get("source_status") != 200:
        return "soft404", "source_status_" + str(x.get("source_status")), val
    if x.get("memento_datetime") != EXPECTED_MEMENTO:
        return "soft404", "actual_memento_mismatch", val
    if mime != EXPECTED_MIME or html.get("is_html") or html.get("markers"):
        return "soft404", "not_text_css_or_html_error", val
    if len(b) != EXPECTED_BYTES or hashlib.sha256(b).hexdigest() != EXPECTED_SHA256:
        return "soft404", "body_length_or_sha256_mismatch", val
    val["css_nonempty"] = bool(b.strip())
    return "valid_stylesheet", "validated_expected_css_source", val

def request(transport: str, state: Any, gate: Any, started: float) -> dict[str, Any]:
    if state.stop_reason or state.attempts >= MAX_ATTEMPTS or time.monotonic() - started >= WINDOW or free() < MIN_FREE:
        return {"executed": False, "attempt": state.attempts + 1, "kind": "replay", "target_key": TARGET, "transport": transport, "url": REPLAY_URL, "unrequested_reason": state.stop_reason or "limit_before_request"}
    number = state.attempts + 1
    g = gate.before_dispatch(number, transport, TARGET)
    x = core.run_request(REPLAY_URL, transport, "replay", TARGET, state, number)
    x.update({"dispatch_utc": g["dispatch_utc"], "dispatch_monotonic": g["dispatch_monotonic"], "dispatch_interval_seconds": g["interval_since_previous_dispatch_seconds"], "gate_persisted_before_transport": g["persisted_before_transport"]})
    b = body(x)
    x["local_zero_byte_body_placeholder"] = bool(x.get("source_status") is None and not b)
    x["body_is_source_response"] = x.get("source_status") is not None
    return x

def write_outputs(inp: dict[str, Any], attempts: list[dict[str, Any]], result: dict[str, Any], state: Any, gate: Any, guard: dict[str, Any], before: int, after: int, started_utc: str, finished_utc: str, postflight: dict[str, Any]) -> None:
    starts = [datetime.fromisoformat(x["started_utc"]) for x in attempts if x.get("started_utc")]
    start_intervals = [(starts[i] - starts[i - 1]).total_seconds() for i in range(1, len(starts))]
    gate_intervals = [x.get("interval_since_previous_dispatch_seconds") for x in gate.dispatches if x.get("interval_since_previous_dispatch_seconds") is not None]
    start_min = min(start_intervals) if start_intervals else None
    gate_min = min(gate_intervals) if gate_intervals else None
    policy = guard["satisfied"] and state.attempts <= MAX_ATTEMPTS and (start_min is None or start_min >= INTERVAL)
    elapsed = (datetime.fromisoformat(finished_utc) - datetime.fromisoformat(started_utc)).total_seconds()
    entity = None
    if result.get("category") == "valid_stylesheet":
        replay = next((x for x in reversed(attempts) if x.get("source_status") is not None), {})
        val = result.get("validation") or {}
        entity = {"target": TARGET, "query_original_url": TARGET, "captured_original_url": CAPTURED_ORIGINAL, "actual_memento": result.get("actual_memento"), "source_status": result.get("source_status"), "content_type": result.get("content_type"), "body_bytes": result.get("body_bytes"), "body_sha256": result.get("body_sha256"), "raw_body_path": (replay.get("raw") or {}).get("body"), "raw_headers_path": (replay.get("raw") or {}).get("headers"), "capture_timestamp": "20070322234302", "cdx_digest": EXPECTED_CDX_DIGEST, "cdx_digest_source": "NET013 accepted selected capture; no CDX request in NET014", "validation": val, "integration": "control evidence only; no integration"}
    report = {"schema": "continuous-wow-network-control14-report/v1", "batch_id": "NET-CONTROL-014", "mode": "executed", "started_utc": started_utc, "finished_utc": finished_utc, "request_window_finished_utc": finished_utc, "request_window_elapsed_seconds": round(elapsed, 3), "report_updated_utc": utc(), "inputs": inp["input_digests"], "guard": guard, "target": TARGET, "replay_url": REPLAY_URL, "captured_original_url": CAPTURED_ORIGINAL, "expected": {"bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256, "mime": EXPECTED_MIME, "actual_memento": EXPECTED_MEMENTO}, "attempts": [public(x) for x in attempts], "source_response_count": sum(x.get("source_status") is not None for x in attempts), "source_request_count": state.attempts, "transport_attempt_count": state.attempts, "failed_attempt_count": state.failed_attempts, "total_body_bytes": state.total_body_bytes, "payload_body_bytes": result.get("body_bytes", 0) if result.get("category") == "valid_stylesheet" else 0, "category": result.get("category"), "reason": result.get("reason"), "actual_memento": result.get("actual_memento"), "source_status": result.get("source_status"), "content_type": result.get("content_type"), "body_bytes": result.get("body_bytes"), "body_sha256": result.get("body_sha256"), "validation": result.get("validation"), "preflight": {"disk_free_bytes_before": before, "disk_free_bytes_after": after, "minimum_free_bytes": MIN_FREE}, "dispatch_count": len(gate.dispatches), "minimum_request_start_interval_seconds": start_min, "gate_dispatch_minimum_interval_seconds": gate_min, "minimum_dispatch_interval_required_seconds": INTERVAL, "batch_policy_accepted": policy, "postflight": postflight, "source_map_entry": entity, "raw_evidence_note": "No CDX query or redirect was performed. Zero-byte no-response body is a local placeholder, not source content; CONNECT 200 is excluded."}
    write(OUT / "control-report.json", report)
    smap = {"schema": "continuous-wow-network-control14-source-map/v1", "batch_id": "NET-CONTROL-014", "report_sha256": sha(OUT / "control-report.json"), "entries": [entity] if entity else [], "entity_count": 1 if entity else 0, "integration_held": True}
    write(OUT / "control-source-map.json", smap)
    summary = {"schema": "continuous-wow-network-control14-sanitized-summary/v1", "batch_id": "NET-CONTROL-014", "report_sha256": sha(OUT / "control-report.json"), "finished_utc": finished_utc, "report_updated_utc": report["report_updated_utc"], "network_requests": state.attempts, "source_response_count": report["source_response_count"], "failed_attempt_count": state.failed_attempts, "category": result.get("category"), "reason": result.get("reason"), "actual_memento": result.get("actual_memento"), "source_status": result.get("source_status"), "content_type": result.get("content_type"), "body_bytes": result.get("body_bytes"), "body_sha256": result.get("body_sha256"), "disk_free_bytes_before": before, "disk_free_bytes_after": after, "guard_satisfied": guard["satisfied"], "minimum_request_start_interval_seconds": start_min, "gate_dispatch_minimum_interval_seconds": gate_min, "batch_policy_accepted": policy, "raw_evidence_note": report["raw_evidence_note"]}
    write(OUT / "sanitized-summary.json", summary)
    (OUT / "sanitized-summary.md").write_text("\n".join(["# NET-CONTROL-014 sanitized summary", "", f"Category: {result.get('category')}; source responses: {report['source_response_count']}; attempts: {state.attempts}.", f"Actual Memento: {result.get('actual_memento') or ''}; bytes: {result.get('body_bytes')}; SHA256: {result.get('body_sha256') or ''}.", f"Guard satisfied: {guard['satisfied']}; request-start minimum: {start_min}; gate dispatch minimum: {gate_min}; policy accepted: {policy}.", "The replay used the accepted captured original URL with :80. No CDX query, redirect, or integration was performed.", "", "| attempt | transport | source status | curl exit | bytes | Memento |", "|---:|---|---:|---:|---:|---|"] + [f"| {x.get('attempt')} | {x.get('transport')} | {x.get('source_status') or ''} | {x.get('curl_exit')} | {x.get('body_bytes')} | {x.get('memento_datetime') or ''} |" for x in attempts] + ["", "Raw headers/traces/body remain local. A zero-byte no-response body is a local placeholder, not source content."]) + "\n", encoding="utf-8")

def prepare():
    inp = verify_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    guard = guard_snapshot()
    config = {"schema": "continuous-wow-network-control14-config/v1", "batch_id": "NET-CONTROL-014", "prepared_utc": utc(), "network_requests": 0, "input_digests": inp["input_digests"], "not_before_utc": NOT_BEFORE, "guard_snapshot": guard, "target": TARGET, "captured_original_url": CAPTURED_ORIGINAL, "replay_url": REPLAY_URL, "expected": {"bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256, "mime": EXPECTED_MIME, "actual_memento": EXPECTED_MEMENTO}, "policy": {"max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW, "minimum_dispatch_interval_seconds": INTERVAL, "minimum_free_bytes": MIN_FREE, "max_total_body_bytes": MAX_TOTAL, "max_entity_body_bytes": MAX_ENTITY, "no_cdx": True, "no_redirects": True, "no_integration": True}}
    write(OUT / "config.json", config)
    write(OUT / "candidates.json", {"schema": "continuous-wow-network-control14-candidates/v1", "batch_id": "NET-CONTROL-014", "network_requests": 0, "target": TARGET, "captured_original_url": CAPTURED_ORIGINAL, "replay_url": REPLAY_URL, "source_evidence": {"acceptance": str(ACCEPT.relative_to(ROOT)).replace("\\", "/"), "selected_source_map": str(SELECTED.relative_to(ROOT)).replace("\\", "/"), "cdx_digest": EXPECTED_CDX_DIGEST}})
    print(json.dumps({"mode": "prepared", "network_requests": 0, "guard": guard, "input_digests": inp["input_digests"]}, ensure_ascii=False))

def execute():
    inp = verify_inputs()
    guard = guard_snapshot()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    before = free()
    if before < MIN_FREE:
        raise RuntimeError("disk free below threshold")
    if not guard["satisfied"]:
        raise RuntimeError("not_before guard is not satisfied; no network dispatched")
    started_utc, started = utc(), time.monotonic()
    state = core.RunState(started)
    journal = {"schema": "continuous-wow-network-control14-dispatch-log/v1", "batch_id": "NET-CONTROL-014", "simulation": False, "policy": {"minimum_dispatch_interval_seconds": INTERVAL, "max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW}, "guard_preflight": guard, "disk_preflight": {"checked_utc": started_utc, "disk_free_bytes": before, "minimum_free_bytes": MIN_FREE}, "dispatches": []}
    gate = gate_mod.GateState(datetime.fromisoformat(NOT_BEFORE), journal_path=OUT / "dispatch-log.json", journal=journal)
    gate.persist()
    attempts, postflight = [], {}
    try:
        direct = request("direct", state, gate, started)
        attempts.append(direct)
        if direct.get("executed") and direct.get("transport_error") and direct.get("source_status") is None and not state.stop_reason:
            proxy = request("proxy", state, gate, started)
            attempts.append(proxy)
    finally:
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=free)
    final = next((x for x in reversed(attempts) if x.get("executed")), attempts[-1] if attempts else {})
    category, reason, val = valid_css(final) if final.get("executed") else ("not_requested", final.get("unrequested_reason", "limit_before_request"), None)
    result = {"category": category, "reason": reason, "validation": val, "actual_memento": final.get("memento_datetime") if final.get("executed") else None, "source_status": final.get("source_status") if final.get("executed") else None, "content_type": final.get("content_type") if final.get("executed") else None, "body_bytes": len(body(final)) if final.get("executed") else 0, "body_sha256": hashlib.sha256(body(final)).hexdigest() if final.get("executed") and body(final) else None}
    finished_utc, after = utc(), free()
    write_outputs(inp, attempts, result, state, gate, guard, before, after, started_utc, finished_utc, postflight)
    print(json.dumps({"mode": "executed", "batch_id": "NET-CONTROL-014", "network_requests": state.attempts, "source_responses": state.source_responses, "failed_attempts": state.failed_attempts, "category": category, "actual_memento": result["actual_memento"], "body_bytes": result["body_bytes"], "body_sha256": result["body_sha256"], "disk_free_before": before, "disk_free_after": after}, ensure_ascii=False))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--prepare", action="store_true")
    p.add_argument("--execute", action="store_true")
    a = p.parse_args()
    if bool(a.prepare) == bool(a.execute):
        p.error("choose exactly one")
    (prepare if a.prepare else execute)()


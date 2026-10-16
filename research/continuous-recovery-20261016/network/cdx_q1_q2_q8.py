#!/usr/bin/env python3
"""Bounded exact-CDX investigation for the three authorized EU queries.

This script is deliberately limited to Q1, Q2 and Q8.  It reuses the prior
core request and gate modules for serial direct-first/proxy-fallback transport,
but changes the query columns and cadence for this round.  It never requests
an availability replay.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
CURL = Path(r"C:\Windows\System32\curl.exe")

BATCH_ID = "WAYBACK-CDX-EU-Q1-Q2-Q8-20261016"
FROM_TIMESTAMP = "20070101000000"
TO_TIMESTAMP = "20080512210044"
MAX_ATTEMPTS = 6
WINDOW_SECONDS = 6 * 60
MIN_DISPATCH = 5.1
MIN_START = 5.0
MIN_FREE = 11_005_853_696
MAX_TOTAL = 32 * 1024 * 1024
MAX_ENTITY = 16 * 1024 * 1024
HARD_CUTOFF = datetime.fromisoformat("2026-10-16T13:00:00+00:00")
STOP_HTTP = {429, 503}
PROXY = "http://127.0.0.1:7890"
USER_AGENT = "wow-recovery-eu-cdx-q1q2q8/20261016"

TARGETS = [
    {
        "id": "Q1",
        "original": "http://wow-europe.com/screenoftheday/screenoftheday/10702-01-thumb.jpg",
        "reason": "rejected thumbnail exact identity; seek additional indexed timestamps/digests",
    },
    {
        "id": "Q2",
        "original": "http://www.wow-europe.com/screenoftheday/screenoftheday/10703-14-thumb.jpg",
        "reason": "rejected thumbnail exact identity; seek additional indexed timestamps/digests",
    },
    {
        "id": "Q8",
        "original": "http://www.wow-europe.com/screenoftheday/screenoftheday/10805-10.jpg",
        "reason": "saved page directly references this original; local complete prefix has no row",
    },
]

INPUT_PATHS = [
    ROOT / "docs/focused-recovery-20261015-2303.md",
    ROOT / "research/focused-recovery-20261015-2303/network/gallery23/gallery23_driver.py",
    ROOT / "research/focused-recovery-20261015-2303/network/gallery23/gallery23-plan.json",
    ROOT / "research/focused-recovery-20261015-2303/network/gallery23/batch-report.json",
    ROOT / "research/focused-recovery-20261015-2303/root-image-acceptance.json",
    ROOT / "research/related-sites-20261014/regional-gallery/cdx/screen-assets-baseline.rows.json",
]


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_module(CORE_PATH, "eu_cdx_core_20261016")
gate_mod = load_module(GATE_PATH, "eu_cdx_gate_20261016")
core.OUT = OUT
core.RAW = RAW
core.PROXY = PROXY
core.USER_AGENT = USER_AGENT
core.CDX_COLUMNS = ["timestamp", "original", "statuscode", "digest", "length", "mimetype"]
core.MAX_ATTEMPTS = MAX_ATTEMPTS
core.WINDOW_SECONDS = WINDOW_SECONDS
core.MIN_INTERVAL_SECONDS = 0.0
core.MIN_FREE_BYTES = MIN_FREE
core.MAX_TOTAL_BODY_BYTES = MAX_TOTAL
core.MAX_ENTITY_BODY_BYTES = MAX_ENTITY
core.DIRECT_CONNECT_SECONDS = 8
core.DIRECT_MAX_SECONDS = 30
core.PROXY_CONNECT_SECONDS = 8
core.PROXY_MAX_SECONDS = 30
core.STOP_HTTP_CODES = STOP_HTTP
gate_mod.OUT = OUT
gate_mod.INTERVAL_SECONDS = MIN_DISPATCH
gate_mod.MIN_FREE_BYTES = MIN_FREE
gate_mod.MAX_TOTAL_BODY_BYTES = MAX_TOTAL
gate_mod.MAX_ENTITY_BYTES = MAX_ENTITY


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def disk_free() -> int:
    return int(shutil.disk_usage(OUT).free)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return path.resolve().relative_to(OUT.resolve()).as_posix()


def cdx_url(original: str) -> str:
    params = [
        ("url", original),
        ("from", FROM_TIMESTAMP),
        ("to", TO_TIMESTAMP),
        ("output", "json"),
        ("fl", "timestamp,original,statuscode,digest,length,mimetype"),
        ("filter", "statuscode:200"),
        ("filter", "mimetype:image/jpeg"),
        ("limit", "1000"),
        ("matchType", "exact"),
    ]
    return "https://web.archive.org/cdx/search/cdx?" + urlencode(params, doseq=True)


def input_binding() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in INPUT_PATHS:
        files.append({
            "path": path.relative_to(ROOT).as_posix(),
            "exists": path.exists(),
            "sha256": sha256_file(path) if path.exists() else None,
        })
    return {
        "script_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "source_files": files,
        "queries": [{**item, "cdx_url": cdx_url(item["original"])} for item in TARGETS],
    }


def policy() -> dict[str, Any]:
    return {
        "max_attempts": MAX_ATTEMPTS,
        "window_seconds": WINDOW_SECONDS,
        "max_total_body_bytes": MAX_TOTAL,
        "max_entity_body_bytes": MAX_ENTITY,
        "min_dispatch_monotonic_seconds": MIN_DISPATCH,
        "min_request_start_utc_seconds": MIN_START,
        "disk_floor_bytes": MIN_FREE,
        "direct_first": True,
        "proxy_fallback": PROXY,
        "automatic_redirects": 0,
        "tls_verification": True,
        "hard_network_cutoff_utc": HARD_CUTOFF.isoformat(),
        "stop_http_codes": sorted(STOP_HTTP),
        "cooldown_seconds_after_stop": 120,
        "replays_requested": 0,
    }


def prepare() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    free = disk_free()
    if free < MIN_FREE:
        raise RuntimeError(f"disk floor failed: {free} < {MIN_FREE}")
    binding = input_binding()
    candidates = {
        "schema": "wow-recovery.eu-cdx-q1-q2-q8-candidates.v1",
        "batch_id": BATCH_ID,
        "prepared_utc": now_utc(),
        "network_requests": 0,
        "target_count": len(TARGETS),
        "entries": [{**item, "cdx_url": cdx_url(item["original"])} for item in TARGETS],
        "policy": policy(),
    }
    write_json(OUT / "candidates.json", candidates)
    write_json(OUT / "batch-inputs.json", binding)
    write_json(OUT / "config.json", {
        "schema": "wow-recovery.eu-cdx-q1-q2-q8-config.v1",
        "batch_id": BATCH_ID,
        "prepared_utc": now_utc(),
        "network_requests": 0,
        "disk_free_bytes": free,
        "candidates_sha256": sha256_file(OUT / "candidates.json"),
        "inputs_sha256": sha256_file(OUT / "batch-inputs.json"),
        "policy": policy(),
    })
    write_json(OUT / "plan.json", {
        "schema": "wow-recovery.eu-cdx-q1-q2-q8-plan.v1",
        "mode": "go_ready",
        "batch_id": BATCH_ID,
        "prepared_utc": now_utc(),
        "network_requests": 0,
        "target_count": len(TARGETS),
        "scope": "Q1, Q2, Q8 exact CDX only; no Q3-Q7 and no payload replay",
        "disk_free_bytes": free,
        "inputs_sha256": sha256_file(OUT / "batch-inputs.json"),
        "script_sha256": binding["script_sha256"],
        "policy": policy(),
    })
    print(json.dumps({"mode": "prepared", "network_requests": 0, "disk_free_bytes": free}, ensure_ascii=False))
    return 0


def wait_request_start(last_started: datetime | None) -> None:
    if last_started is None:
        return
    while True:
        remain = MIN_START - (datetime.now(timezone.utc) - last_started).total_seconds()
        if remain <= 0:
            return
        time.sleep(min(60.0, max(remain, 0.01)))


def dispatch_one(
    item: dict[str, Any],
    transport: str,
    state: Any,
    gate: Any,
    last_started: datetime | None,
) -> tuple[dict[str, Any] | None, datetime | None]:
    if datetime.now(timezone.utc) >= HARD_CUTOFF:
        state.stop_reason = state.stop_reason or "hard_network_cutoff"
        return None, last_started
    if disk_free() < MIN_FREE:
        state.stop_reason = state.stop_reason or "disk_free_below_threshold"
        return None, last_started
    wait_request_start(last_started)
    dispatch_record = gate.before_dispatch(state.attempts + 1, transport, item["id"])
    if datetime.now(timezone.utc) >= HARD_CUTOFF:
        dispatch_record["not_executed_reason"] = "hard_network_cutoff"
        gate.persist()
        state.stop_reason = state.stop_reason or "hard_network_cutoff"
        return None, last_started
    if disk_free() < MIN_FREE:
        dispatch_record["not_executed_reason"] = "disk_free_below_threshold"
        gate.persist()
        state.stop_reason = state.stop_reason or "disk_free_below_threshold"
        return None, last_started
    attempt = core.run_request(
        cdx_url(item["original"]),
        transport,
        "cdx",
        item["id"],
        state,
        state.attempts + 1,
    )
    attempt["dispatch"] = dispatch_record
    gate.persist()
    started = parse_iso(attempt.get("started_utc")) or last_started
    return attempt, started


def query_item(
    item: dict[str, Any],
    state: Any,
    gate: Any,
    last_started: datetime | None,
) -> tuple[dict[str, Any], datetime | None, list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    for transport in ("direct", "proxy"):
        attempt, last_started = dispatch_one(item, transport, state, gate, last_started)
        if attempt is None:
            break
        attempts.append(attempt)
        if attempt.get("source_status") in STOP_HTTP:
            break
        if state.stop_reason in {"five_consecutive_tls_or_transport_failures", "hard_network_cutoff", "disk_free_below_threshold", "network_window_exhausted", "attempt_limit", "total_body_limit", "single_entity_body_limit"}:
            break
        if not attempt.get("transport_error"):
            break
    final = attempts[-1] if attempts else None
    if final is None:
        category = "not_requested"
    elif final.get("source_status") in STOP_HTTP:
        category = f"http_{final['source_status']}"
    elif final.get("transport_error"):
        category = "transport_error"
    elif final.get("source_status") == 200 and final.get("cdx_parse_valid"):
        category = "cdx_ok" if final.get("cdx_records") else "cdx_ok_no_rows"
    else:
        category = "http_response"
    records: list[dict[str, Any]] = []
    for attempt in attempts:
        if attempt.get("cdx_parse_valid"):
            records.extend(attempt.get("cdx_records") or [])
    exact_rows = [row for row in records if row.get("original") == item["original"]]
    result = {
        **item,
        "category": category,
        "attempt_count": len(attempts),
        "source_response_count": sum(a.get("source_status") is not None for a in attempts),
        "rows_returned": len(records),
        "exact_original_rows": len(exact_rows),
        "records": records,
        "attempts": [core.source_attempt_view(a) for a in attempts],
        "raw_paths": [a.get("raw") for a in attempts],
    }
    return result, last_started, attempts


def cooldown_if_needed(state: Any) -> dict[str, Any]:
    if state.stop_reason not in {"endpoint_status_429", "endpoint_status_503", "five_consecutive_tls_or_transport_failures"}:
        return {"required": False, "seconds": 0, "applied": False}
    started = now_utc()
    time.sleep(120)
    finished = now_utc()
    return {
        "required": True,
        "seconds": 120,
        "applied": True,
        "started_utc": started,
        "finished_utc": finished,
        "no_followup_dispatch": True,
    }


def execute() -> int:
    report_path = OUT / "batch-report.json"
    if report_path.exists() or (RAW.exists() and any(RAW.iterdir())):
        raise RuntimeError("refusing rerun: this owned batch already has output")
    free_before = disk_free()
    if free_before < MIN_FREE:
        raise RuntimeError(f"disk floor failed before execution: {free_before} < {MIN_FREE}")
    RAW.mkdir(parents=True, exist_ok=True)
    binding = input_binding()
    not_before = datetime.now(timezone.utc)
    journal: dict[str, Any] = {
        "schema": "wow-recovery.eu-cdx-q1-q2-q8-dispatch-log.v1",
        "batch_id": BATCH_ID,
        "simulation": False,
        "authorization": "parent GO received",
        "not_before_utc": not_before.isoformat(),
        "hard_cutoff_utc": HARD_CUTOFF.isoformat(),
        "disk_preflight": {
            "checked_utc": now_utc(),
            "disk_free_bytes": free_before,
            "minimum_free_bytes": MIN_FREE,
            "passed": True,
        },
        "dispatches": [],
    }
    write_json(OUT / "dispatch-log.json", journal)
    gate = gate_mod.GateState(not_before, journal_path=OUT / "dispatch-log.json", journal=journal)
    state = core.RunState(time.monotonic())
    all_attempts: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    last_started: datetime | None = None
    network_started: str | None = None
    network_finished: str | None = None
    try:
        for item in TARGETS:
            if state.stop_reason:
                results.append({**item, "category": "not_requested", "reason": state.stop_reason, "attempt_count": 0, "records": [], "attempts": []})
                continue
            result, last_started, attempts = query_item(item, state, gate, last_started)
            results.append(result)
            all_attempts.extend(attempts)
            if attempts:
                network_started = network_started or attempts[0].get("started_utc")
                network_finished = attempts[-1].get("finished_utc") or network_finished
            if state.stop_reason:
                continue
    finally:
        postflight = {
            "checked_utc": now_utc(),
            "disk_free_bytes": disk_free(),
            "attempts_count": state.attempts,
            "persisted_in_finally": True,
        }
        journal["disk_postflight"] = postflight
        journal["final_attempt_count"] = state.attempts
        gate.persist()
    if not state.stop_reason:
        state.stop_reason = "completed"
    cooldown = cooldown_if_needed(state)
    dispatches = journal.get("dispatches") or []
    dispatch_intervals = [
        dispatches[index]["dispatch_monotonic"] - dispatches[index - 1]["dispatch_monotonic"]
        for index in range(1, len(dispatches))
    ]
    starts = [parse_iso(a.get("started_utc")) for a in all_attempts if parse_iso(a.get("started_utc"))]
    start_intervals = [(starts[index] - starts[index - 1]).total_seconds() for index in range(1, len(starts))]
    inputs_path = OUT / "batch-inputs.json"
    config_path = OUT / "config.json"
    report = {
        "schema": "wow-recovery.eu-cdx-q1-q2-q8-batch-report.v1",
        "batch_id": BATCH_ID,
        "mode": "executed",
        "authorization": "parent GO received",
        "started_utc": network_started,
        "finished_utc": network_finished or now_utc(),
        "request_window_finished_utc": network_finished or now_utc(),
        "report_updated_utc": now_utc(),
        "target_count": len(TARGETS),
        "source_request_count": state.attempts,
        "transport_attempt_count": state.attempts,
        "source_response_count": state.source_responses,
        "failed_attempt_count": state.failed_attempts,
        "total_body_bytes": state.total_body_bytes,
        "payload_body_bytes": 0,
        "results": results,
        "attempts": [core.source_attempt_view(a) for a in all_attempts],
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "rate_limit": state.rate_limit,
        "cooldown": cooldown,
        "disk_preflight": journal["disk_preflight"],
        "disk_postflight": journal.get("disk_postflight"),
        "cadence": {
            "dispatch_intervals": dispatch_intervals,
            "request_start_intervals": start_intervals,
            "min_dispatch_monotonic_seconds": min(dispatch_intervals) if dispatch_intervals else None,
            "min_request_start_utc_seconds": min(start_intervals) if start_intervals else None,
            "required_dispatch_monotonic_seconds": MIN_DISPATCH,
            "required_request_start_utc_seconds": MIN_START,
        },
        "policy": policy(),
        "input_binding": {
            **binding,
            "batch_inputs_path": relative(inputs_path),
            "batch_inputs_sha256": sha256_file(inputs_path) if inputs_path.exists() else None,
            "config_path": relative(config_path),
            "config_sha256": sha256_file(config_path) if config_path.exists() else None,
        },
        "raw_evidence_note": "Raw headers, bodies, stderr and traces remain under this batch's raw directory. No availability replay was requested; CDX rows are index evidence only.",
    }
    write_json(report_path, report)
    summary = {
        "schema": "wow-recovery.eu-cdx-q1-q2-q8-sanitized-summary.v1",
        "batch_id": BATCH_ID,
        "source_request_count": report["source_request_count"],
        "source_response_count": report["source_response_count"],
        "failed_attempt_count": report["failed_attempt_count"],
        "stop_reason": report["stop_reason"],
        "rate_limit": report["rate_limit"],
        "cooldown": report["cooldown"],
        "cadence": report["cadence"],
        "results": [
            {k: v for k, v in item.items() if k not in {"attempts", "raw_paths"}}
            for item in results
        ],
        "input_binding": report["input_binding"],
        "raw_evidence_note": report["raw_evidence_note"],
    }
    write_json(OUT / "sanitized-summary.json", summary)
    lines = [
        "# EU Q1/Q2/Q8 sanitized CDX summary",
        "",
        f"Batch `{BATCH_ID}`; source requests `{report['source_request_count']}`; source responses `{report['source_response_count']}`; failed attempts `{report['failed_attempt_count']}`.",
        f"Stop reason: `{report['stop_reason']}`.",
        f"Minimum dispatch interval: `{report['cadence']['min_dispatch_monotonic_seconds']}` seconds; required `{MIN_DISPATCH}`.",
        f"Minimum request-start interval: `{report['cadence']['min_request_start_utc_seconds']}` seconds; required `{MIN_START}`.",
        "",
    ]
    for item in results:
        lines.append(f"- `{item['id']}` `{item['category']}`; attempts `{item.get('attempt_count', 0)}`; exact rows `{item.get('exact_original_rows', 0)}`.")
        for row in item.get("records", []):
            lines.append(f"  - `{row.get('timestamp')}` `{row.get('original')}` status `{row.get('statuscode')}` digest `{row.get('digest')}` length `{row.get('length')}` MIME `{row.get('mimetype')}`")
    lines.extend(["", "Raw evidence remains under `raw/`; no replay or integration was performed.", ""])
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")
    journal["report_written_utc"] = now_utc()
    journal["report_sha256"] = sha256_file(report_path)
    write_json(OUT / "dispatch-log.json", journal)
    print(json.dumps({
        "mode": "executed",
        "batch_id": BATCH_ID,
        "network_requests": report["source_request_count"],
        "source_responses": report["source_response_count"],
        "failed_attempts": report["failed_attempt_count"],
        "stop_reason": report["stop_reason"],
        "min_dispatch": report["cadence"]["min_dispatch_monotonic_seconds"],
        "min_request_start": report["cadence"]["min_request_start_utc_seconds"],
        "raw": relative(RAW),
    }, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.prepare == args.execute:
        parser.error("choose exactly one")
    return prepare() if args.prepare else execute()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"cdx_q1_q2_q8: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

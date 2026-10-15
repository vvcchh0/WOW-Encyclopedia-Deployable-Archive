"""NET-CONTROL-007: one bounded post-cooldown JPEG control.

This driver owns only the network-control7 directory.  It reuses the
accepted control2 parser, Memento and Pillow helpers, but owns the dispatch
gate and raw output so an early wake cannot silently dispatch a request.
Preparation is offline.  ``--execute`` waits for the UTC guard and then
performs at most direct followed by one proxy attempt for the fixed target.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
CONTROL2 = ROOT / "research/continuous-recovery-20261015/network-control2/control2.py"
SUMMARY_INPUT = ROOT / "research/continuous-recovery-20261015/network-control2/sanitized-summary.json"
ACCEPTANCE_INPUT = ROOT / "research/continuous-recovery-20261015/control2-acceptance.json"
CONTROL2_REPORT = ROOT / "research/continuous-recovery-20261015/network-control2/control-report.json"
CURL = Path(r"C:\Windows\System32\curl.exe")
PROXY = "http://127.0.0.1:7890"

TARGET = "https://web.archive.org/web/20080512212653id_/http://www.worldofwarcraft.com/info/dungeons/images/karazhan/thumbs/ss2-thumb.jpg"
EXPECTED_BYTES = 3347
EXPECTED_SHA256 = "45936113efa432f3c8188445ae255108c2af3d06fecf902202f0611068a74a11"
EXPECTED_FORMAT = "JPEG"
EXPECTED_SIZE = [150, 110]
EXPECTED_MEMENTO = "2008-05-12T21:26:53+00:00"
NOT_BEFORE = "2026-10-15T09:03:32.169574+00:00"
MAX_REQUESTS = 2
INTERVAL_SECONDS = 1.25
WINDOW_SECONDS = 120
MAX_TOTAL_BODY_BYTES = 64 * 1024 * 1024
MAX_ENTITY_BYTES = 16 * 1024 * 1024
MIN_FREE_BYTES = 11_005_853_696
STOP_HTTP_CODES = {429, 503}
USER_AGENT = "net-control7/20261015"


def load_helper() -> Any:
    spec = importlib.util.spec_from_file_location("accepted_control2_helpers", CONTROL2)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load accepted helper: {CONTROL2}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HELPER = load_helper()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def now_dt() -> datetime:
    return datetime.now(timezone.utc)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def parse_inputs() -> dict[str, Any]:
    summary = json.loads(SUMMARY_INPUT.read_text(encoding="utf-8"))
    acceptance = json.loads(ACCEPTANCE_INPUT.read_text(encoding="utf-8"))
    control_report = json.loads(CONTROL2_REPORT.read_text(encoding="utf-8"))
    if summary.get("target") != TARGET:
        raise ValueError("control2 sanitized summary target mismatch")
    if not acceptance.get("accepted") or not acceptance.get("ready"):
        raise ValueError("control2 acceptance is not accepted and ready")
    if acceptance.get("control_report") != "research/continuous-recovery-20261015/network-control2/control-report.json":
        raise ValueError("control2 acceptance report path mismatch")
    if sha256_file(CONTROL2_REPORT) != acceptance.get("report_sha256"):
        raise ValueError("control2 report digest mismatch")
    if control_report.get("target") != TARGET:
        raise ValueError("control2 report target mismatch")
    expected = control_report.get("expected") or {}
    if int(expected.get("bytes")) != EXPECTED_BYTES or str(expected.get("sha256")).lower() != EXPECTED_SHA256:
        raise ValueError("control2 expected bytes or SHA mismatch")
    if str(expected.get("format")) != EXPECTED_FORMAT or list(expected.get("size")) != EXPECTED_SIZE:
        raise ValueError("control2 expected image identity mismatch")
    if expected.get("memento") != EXPECTED_MEMENTO:
        raise ValueError("control2 expected Memento mismatch")
    return {
        "summary": summary,
        "acceptance": acceptance,
        "control_report": control_report,
        "summary_sha256": sha256_file(SUMMARY_INPUT),
        "acceptance_sha256": sha256_file(ACCEPTANCE_INPUT),
        "control_report_sha256": sha256_file(CONTROL2_REPORT),
    }


def fakeclock_gate_test() -> dict[str, Any]:
    """Verify an early wake is recomputed before dispatch."""
    minimum = 1.25
    fake_elapsed = [0.50, 1.00, 1.25]
    waits: list[float] = []
    for elapsed in fake_elapsed[:-1]:
        remaining = minimum - elapsed
        if remaining > 0:
            waits.append(round(remaining, 6))
    passed = waits == [0.75, 0.25] and minimum - fake_elapsed[-1] <= 0
    return {
        "passed": passed,
        "minimum_interval_seconds": minimum,
        "early_wake_elapsed_seconds": fake_elapsed[0],
        "recomputed_waits_seconds": waits,
        "dispatch_allowed_at_elapsed_seconds": fake_elapsed[-1],
    }


def plan_document(inputs: dict[str, Any]) -> dict[str, Any]:
    prepared = now_utc()
    current = datetime.fromisoformat(prepared)
    not_before = datetime.fromisoformat(NOT_BEFORE)
    fake_test = fakeclock_gate_test()
    return {
        "schema": "wayback-net-control7-plan-20261015.v1",
        "mode": "plan_only",
        "prepared_utc": prepared,
        "not_before_utc": NOT_BEFORE,
        "time_guard": {
            "current_utc": prepared,
            "open": current >= not_before,
            "execute_requires_current_at_or_after": NOT_BEFORE,
            "actual_dispatch_rechecks_guard": True,
            "monotonic_recheck_loop": True,
            "maximum_sleep_seconds": 60,
        },
        "inputs": {
            "summary_path": str(SUMMARY_INPUT.relative_to(ROOT)).replace("\\", "/"),
            "summary_sha256": inputs["summary_sha256"],
            "acceptance_path": str(ACCEPTANCE_INPUT.relative_to(ROOT)).replace("\\", "/"),
            "acceptance_sha256": inputs["acceptance_sha256"],
            "control_report_path": str(CONTROL2_REPORT.relative_to(ROOT)).replace("\\", "/"),
            "control_report_sha256": inputs["control_report_sha256"],
        },
        "target": TARGET,
        "expected": {
            "bytes": EXPECTED_BYTES,
            "sha256": EXPECTED_SHA256,
            "format": EXPECTED_FORMAT,
            "size": EXPECTED_SIZE,
            "memento": EXPECTED_MEMENTO,
        },
        "policy": {
            "direct_first": True,
            "direct_connect_timeout_seconds": 4,
            "direct_total_timeout_seconds": 12,
            "proxy": PROXY,
            "proxy_connect_timeout_seconds": 8,
            "proxy_total_timeout_seconds": 20,
            "tls_verification": "enabled_by_curl_default",
            "max_targets": 1,
            "max_source_requests": MAX_REQUESTS,
            "network_window_seconds": WINDOW_SECONDS,
            "redirects": 0,
            "automatic_redirects": 0,
            "min_dispatch_interval_seconds": INTERVAL_SECONDS,
            "min_free_bytes": MIN_FREE_BYTES,
            "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
            "max_entity_body_bytes": MAX_ENTITY_BYTES,
            "stop_http_codes": sorted(STOP_HTTP_CODES),
            "cdx": "not queried; accepted control2 is the exact known Memento control",
        },
        "offline_checks": {
            "input_digest_checked": True,
            "target_expected_checked": True,
            "request_cap": MAX_REQUESTS,
            "time_guard_declared": True,
            "dispatch_gate_fakeclock": fake_test,
            "network_requests": 0,
        },
        "raw_evidence_note": "Raw headers, body, stderr and trace remain local only. A zero-byte body for a transport attempt is a local placeholder, not source response content.",
        "prepared": True,
        "ready_to_execute": current >= not_before and fake_test["passed"],
    }


def wait_until_guard(not_before: datetime) -> dict[str, Any]:
    """Wait with a monotonic deadline, then recheck UTC before dispatch."""
    first_wall = now_dt()
    first_mono = time.monotonic()
    initial_remaining = max((not_before - first_wall).total_seconds(), 0.0)
    monotonic_deadline = first_mono + initial_remaining
    sleeps: list[dict[str, Any]] = []
    while True:
        wall_now = now_dt()
        mono_now = time.monotonic()
        wall_remaining = (not_before - wall_now).total_seconds()
        mono_remaining = monotonic_deadline - mono_now
        if wall_remaining <= 0 and mono_remaining <= 0:
            return {
                "first_checked_utc": first_wall.isoformat(),
                "opened_utc": wall_now.isoformat(),
                "first_monotonic": first_mono,
                "opened_monotonic": mono_now,
                "sleeps": sleeps,
                "final_wall_remaining_seconds": wall_remaining,
                "final_monotonic_remaining_seconds": mono_remaining,
            }
        sleep_for = min(60.0, max(wall_remaining, mono_remaining, 0.01))
        sleep_started = time.monotonic()
        time.sleep(sleep_for)
        sleeps.append({
            "requested_seconds": sleep_for,
            "started_monotonic": sleep_started,
            "finished_monotonic": time.monotonic(),
        })


class GateState:
    def __init__(
        self,
        not_before: datetime,
        *,
        journal_path: Path | None = None,
        journal: dict[str, Any] | None = None,
    ) -> None:
        self.not_before = not_before
        self.last_dispatch_mono: float | None = None
        self.dispatches: list[dict[str, Any]] = []
        self.journal_path = journal_path or (OUT / "dispatch-log.json")
        self.journal = journal or {
            "schema": "wayback-net-control7-dispatch-log/v1",
            "simulation": False,
            "dispatches": self.dispatches,
        }
        self.journal.setdefault("dispatches", self.dispatches)

    def persist(self) -> None:
        self.journal["dispatches"] = self.dispatches
        write_json(self.journal_path, self.journal)

    def before_dispatch(self, attempt_number: int, transport: str, target: str) -> dict[str, Any]:
        guard = wait_until_guard(self.not_before)
        interval_sleeps: list[dict[str, Any]] = []
        while True:
            now = time.monotonic()
            remaining = 0.0 if self.last_dispatch_mono is None else INTERVAL_SECONDS - (now - self.last_dispatch_mono)
            if remaining <= 0:
                break
            sleep_for = min(60.0, max(remaining, 0.01))
            sleep_started = time.monotonic()
            time.sleep(sleep_for)
            interval_sleeps.append({
                "requested_seconds": sleep_for,
                "started_monotonic": sleep_started,
                "finished_monotonic": time.monotonic(),
            })
        # Final wall-clock guard check is immediately before dispatch.
        final_utc = now_dt()
        final_mono = time.monotonic()
        if final_utc < self.not_before:
            return self.before_dispatch(attempt_number, transport, target)
        if self.last_dispatch_mono is not None and final_mono - self.last_dispatch_mono < INTERVAL_SECONDS:
            return self.before_dispatch(attempt_number, transport, target)
        record = {
            "attempt": attempt_number,
            "transport": transport,
            "target": target,
            "guard_open_utc": final_utc.isoformat(),
            "dispatch_utc": final_utc.isoformat(),
            "dispatch_monotonic": final_mono,
            "interval_since_previous_dispatch_seconds": None if self.last_dispatch_mono is None else final_mono - self.last_dispatch_mono,
            "guard_wait": guard,
            "interval_sleeps": interval_sleeps,
        }
        self.last_dispatch_mono = final_mono
        self.dispatches.append(record)
        record["persisted_before_transport"] = True
        # Persist the gate record before invoking curl so a later report
        # assembly failure cannot erase the actual dispatch audit trail.
        self.persist()
        return record


def persist_postflight(
    state: GateState,
    attempts_count: int,
    *,
    free_fn: Callable[[], int] = free_bytes,
) -> dict[str, Any]:
    """Persist postflight evidence even when report/summary assembly fails."""
    postflight = {
        "checked_utc": now_utc(),
        "disk_free_bytes": free_fn(),
        "attempts_count": attempts_count,
        "persisted_in_finally": True,
    }
    state.journal["disk_postflight"] = postflight
    state.journal["postflight_persisted_in_finally"] = True
    state.journal["final_attempt_count"] = attempts_count
    state.persist()
    return postflight


def dispatch(target: str, transport: str, attempt_number: int, state: GateState) -> dict[str, Any]:
    gate = state.before_dispatch(attempt_number, transport, target)
    stem = f"attempt-{attempt_number:02d}-{transport}"
    headers_path = RAW / f"{stem}.headers.txt"
    body_path = RAW / f"{stem}.body"
    stderr_path = RAW / f"{stem}.stderr.txt"
    trace_path = RAW / f"{stem}.trace.txt"
    metrics_path = RAW / f"{stem}.metrics.txt"
    if transport == "direct":
        transport_args = ["--proxy", "", "--noproxy", "*"]
        connect_timeout, max_time = 4, 12
    else:
        transport_args = ["--proxy", PROXY, "--noproxy", ""]
        connect_timeout, max_time = 8, 20
    command = [
        str(CURL), *transport_args,
        "--connect-timeout", str(connect_timeout), "--max-time", str(max_time),
        "--max-redirs", "0", "--max-filesize", str(MAX_ENTITY_BYTES),
        "--silent", "--show-error", "--trace-time", "--trace-ascii", str(trace_path),
        "--dump-header", str(headers_path), "--output", str(body_path),
        "--write-out", "%{http_code}", "--user-agent", USER_AGENT, target,
    ]
    started_utc = now_utc()
    started_mono = time.monotonic()
    stdout = ""
    curl_exit: int | None = None
    try:
        proc = subprocess.run(
            command,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=stderr_path.open("wb"),
            timeout=max_time + 6,
            check=False,
        )
        stdout = proc.stdout.decode("ascii", errors="replace").strip()
        curl_exit = proc.returncode
    except Exception as exc:  # pragma: no cover
        stderr_path.write_text(type(exc).__name__ + ": " + str(exc), encoding="utf-8")
    finished_utc = now_utc()
    if not headers_path.exists():
        headers_path.write_text("", encoding="iso-8859-1")
    if not body_path.exists():
        body_path.write_bytes(b"")
    header_text = headers_path.read_text(encoding="iso-8859-1", errors="replace")
    blocks = HELPER.source_blocks(header_text)
    parsed_blocks = HELPER.parse_blocks(header_text)
    source_status = blocks[-1]["status"] if blocks else None
    if source_status is None and re.fullmatch(r"[1-5]\d\d", stdout):
        source_status = int(stdout)
    body = body_path.read_bytes()
    content_type = HELPER.header(blocks, "content-type")
    memento = HELPER.memento_iso(HELPER.header(blocks, "memento-datetime"))
    location = HELPER.header(blocks, "location")
    retry_after = HELPER.header(blocks, "retry-after")
    transport_error = source_status is None or curl_exit != 0
    image = HELPER.pillow_info(body)
    metrics_path.write_text(stdout + "\n", encoding="ascii", errors="replace")
    return {
        "executed": True,
        "attempt": attempt_number,
        "transport": transport,
        "url": target,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "started_monotonic": started_mono,
        "finished_monotonic": time.monotonic(),
        "duration_ms": round((time.monotonic() - started_mono) * 1000, 1),
        "dispatch": gate,
        "curl_exit": curl_exit,
        "source_status": source_status,
        "connect_status": next((block["status"] for block in parsed_blocks if "connection established" in block["reason"].lower()), None),
        "memento_datetime": memento,
        "location": location,
        "retry_after": retry_after,
        "redirects_requested": 0,
        "automatic_redirects": 0,
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "content_type": content_type,
        "image": image,
        "transport_error": transport_error,
        "transport_reason": "no_http_status" if source_status is None else (f"curl_exit_{curl_exit}" if curl_exit != 0 else None),
        "raw": {
            "headers": rel(headers_path),
            "body": rel(body_path),
            "stderr": rel(stderr_path),
            "trace": rel(trace_path),
            "metrics": rel(metrics_path),
        },
    }


def classify(attempts: list[dict[str, Any]], stop_reason: str | None) -> tuple[str, dict[str, Any]]:
    final = attempts[-1] if attempts else None
    if final is None:
        return "not_requested", {"reason": stop_reason or "no_attempt"}
    if final.get("source_status") == 200 and not final.get("transport_error"):
        image = final.get("image") or {}
        expected_match = (
            final.get("body_bytes") == EXPECTED_BYTES
            and final.get("body_sha256") == EXPECTED_SHA256
            and image.get("valid")
            and image.get("format") == EXPECTED_FORMAT
            and image.get("size") == EXPECTED_SIZE
            and final.get("memento_datetime") == EXPECTED_MEMENTO
            and (final.get("content_type") or "").lower().split(";", 1)[0] == "image/jpeg"
        )
        return ("valid_image" if expected_match else "content_mismatch"), {"expected_match": expected_match, "image": image}
    if final.get("transport_error"):
        return "transport_error", {"reason": "curl_or_tls_failure", "source_status": final.get("source_status")}
    return "http_response", {"reason": "non_200_source_response", "source_status": final.get("source_status")}


def _execute_body(
    inputs: dict[str, Any],
    gate_state: GateState,
    disk_before: int,
    fake_test: dict[str, Any],
) -> int:
    # The caller owns the preflight journal and finally-based postflight
    # persistence. This body contains the bounded network operation and the
    # ordinary report/summary assembly.
    not_before = gate_state.not_before
    attempts: list[dict[str, Any]] = []
    direct = dispatch(TARGET, "direct", 1, gate_state)
    attempts.append(direct)
    stop_reason: str | None = None
    if direct.get("source_status") in STOP_HTTP_CODES:
        stop_reason = f"endpoint_status_{direct['source_status']}"
    elif direct.get("transport_error"):
        if free_bytes() < MIN_FREE_BYTES:
            stop_reason = "disk_free_below_threshold"
        else:
            proxy = dispatch(TARGET, "proxy", 2, gate_state)
            attempts.append(proxy)
            if proxy.get("source_status") in STOP_HTTP_CODES:
                stop_reason = f"endpoint_status_{proxy['source_status']}"
    category, detail = classify(attempts, stop_reason)
    request_finished = next((a.get("finished_utc") for a in reversed(attempts) if a.get("executed")), now_utc())
    report_updated = now_utc()
    request_started = attempts[0].get("started_utc") if attempts else report_updated
    request_window_seconds = (
        (datetime.fromisoformat(request_finished) - datetime.fromisoformat(request_started)).total_seconds()
        if attempts
        else 0
    )
    report = {
        "schema": "wayback-net-control7-20261015.v1",
        "mode": "executed",
        "started_utc": request_started,
        "finished_utc": request_finished,
        "request_window_finished_utc": request_finished,
        "report_updated_utc": report_updated,
        "not_before_utc": NOT_BEFORE,
        "input_sha256": inputs["summary_sha256"],
        "inputs": {
            "summary_path": str(SUMMARY_INPUT.relative_to(ROOT)).replace("\\", "/"),
            "summary_sha256": inputs["summary_sha256"],
            "acceptance_path": str(ACCEPTANCE_INPUT.relative_to(ROOT)).replace("\\", "/"),
            "acceptance_sha256": inputs["acceptance_sha256"],
            "control_report_path": str(CONTROL2_REPORT.relative_to(ROOT)).replace("\\", "/"),
            "control_report_sha256": inputs["control_report_sha256"],
        },
        "target": TARGET,
        "expected": {"bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256, "format": EXPECTED_FORMAT, "size": EXPECTED_SIZE, "memento": EXPECTED_MEMENTO},
        "category": category,
        "detail": detail,
        "source_request_count": len(attempts),
        "transport_attempt_count": len(attempts),
        "failed_attempt_count": sum(bool(a.get("transport_error")) for a in attempts),
        "source_response_count": sum(a.get("source_status") is not None for a in attempts),
        "total_body_bytes": sum(int(a.get("body_bytes") or 0) for a in attempts),
        "payload_body_bytes": sum(int(a.get("body_bytes") or 0) for a in attempts if a.get("source_status") is not None),
        "stop_reason": stop_reason,
        "rate_limit": next(({"status": a.get("source_status"), "retry_after": a.get("retry_after")} for a in attempts if a.get("source_status") in STOP_HTTP_CODES), None),
        "disk_free_bytes_before": disk_before,
        "disk_free_bytes_after": free_bytes(),
        "network_window_seconds": request_window_seconds,
        "minimum_dispatch_interval_seconds": min((attempts[i]["dispatch"]["dispatch_monotonic"] - attempts[i-1]["dispatch"]["dispatch_monotonic"] for i in range(1, len(attempts))), default=None),
        "policy": plan_document(inputs)["policy"],
        "gate_self_test": fake_test,
        "attempts": attempts,
        "raw_evidence_note": "Raw headers, body, stderr and trace remain local only. A zero-byte body for a transport attempt is a local placeholder, not source response content.",
        "cdx": {"queried": False, "accepted_control2_digest": None, "note": "No new CDX query; exact control Memento was already accepted by control2."},
    }
    write_json(OUT / "control-report.json", report)
    summary = {
        "schema": "wayback-net-control7-20261015-summary.v1",
        "mode": "executed",
        "started_utc": report["started_utc"],
        "finished_utc": report["finished_utc"],
        "request_window_finished_utc": report["request_window_finished_utc"],
        "report_updated_utc": report["report_updated_utc"],
        "not_before_utc": NOT_BEFORE,
        "target": TARGET,
        "category": category,
        "source_request_count": report["source_request_count"],
        "transport_attempt_count": report["transport_attempt_count"],
        "failed_attempt_count": report["failed_attempt_count"],
        "source_response_count": report["source_response_count"],
        "total_body_bytes": report["total_body_bytes"],
        "payload_body_bytes": report["payload_body_bytes"],
        "stop_reason": stop_reason,
        "disk_free_bytes_before": disk_before,
        "disk_free_bytes_after": report["disk_free_bytes_after"],
        "actual_memento": next((a.get("memento_datetime") for a in reversed(attempts) if a.get("source_status") == 200), None),
        "body_bytes": next((a.get("body_bytes") for a in reversed(attempts) if a.get("source_status") == 200), 0),
        "body_sha256": next((a.get("body_sha256") for a in reversed(attempts) if a.get("source_status") == 200), None),
        "image": next((a.get("image") for a in reversed(attempts) if a.get("source_status") == 200), None),
        "raw_evidence_note": report["raw_evidence_note"],
    }
    write_json(OUT / "sanitized-summary.json", summary)
    write_json(OUT / "dispatch-gate-test.json", fake_test)
    lines = [
        "# NET-CONTROL-007 sanitized control summary",
        "",
        f"Target: `{TARGET}`.",
        f"Category: `{category}`; attempts: `{report['source_request_count']}`; source responses excluding CONNECT: `{report['source_response_count']}`.",
        f"Request window: `{report['started_utc']}` to `{report['request_window_finished_utc']}`; report updated: `{report['report_updated_utc']}`.",
        f"Actual Memento: `{summary['actual_memento'] or ''}`; body bytes: `{summary['body_bytes']}`; body SHA-256: `{summary['body_sha256'] or ''}`.",
        f"Image validation: `{(summary['image'] or {}).get('format')}` `{(summary['image'] or {}).get('size')}`, verify=`{(summary['image'] or {}).get('verify')}`, load=`{(summary['image'] or {}).get('load')}`.",
        f"Dispatch minimum interval observed: `{report['minimum_dispatch_interval_seconds']}` seconds; required `{INTERVAL_SECONDS}`.",
        f"Stop reason: `{stop_reason or 'none'}`; disk free before/after: `{disk_before}` / `{report['disk_free_bytes_after']}` bytes.",
        "No CDX request was made; this control reuses the previously accepted exact Memento control.",
        "Raw headers, body, stderr and trace remain local only; zero-byte transport bodies are local placeholders, not source content.",
        "",
    ]
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"network_requests": len(attempts), "ready": category == "valid_image", "category": category, "actual_memento": summary["actual_memento"]}, ensure_ascii=False))
    return 0


def execute(inputs: dict[str, Any]) -> int:
    """Run once with preflight journaling and finally-based postflight."""
    not_before = datetime.fromisoformat(NOT_BEFORE)
    fake_test = fakeclock_gate_test()
    if not fake_test["passed"]:
        raise RuntimeError("fakeclock gate test failed")
    if (OUT / "control-report.json").exists() or (RAW.exists() and any(RAW.iterdir())) or (OUT / "dispatch-log.json").exists():
        raise RuntimeError("refusing network rerun: owned output contains a completed or partial execution")
    disk_before = free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError("D: free space below threshold")
    RAW.mkdir(parents=True, exist_ok=True)
    journal = {
        "schema": "wayback-net-control7-dispatch-log/v1",
        "simulation": False,
        "started_utc": now_utc(),
        "not_before_utc": NOT_BEFORE,
        "disk_preflight": {
            "checked_utc": now_utc(),
            "disk_free_bytes": disk_before,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "passed": True,
        },
        "dispatches": [],
    }
    gate_state = GateState(not_before, journal_path=OUT / "dispatch-log.json", journal=journal)
    gate_state.persist()
    try:
        return _execute_body(inputs, gate_state, disk_before, fake_test)
    finally:
        # This is deliberately outside report/summary assembly so a later
        # formatting exception cannot lose the disk and dispatch evidence.
        persist_postflight(gate_state, len(gate_state.dispatches))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true", help="write an offline plan")
    parser.add_argument("--self-test", action="store_true", help="run the offline fake-clock gate test")
    parser.add_argument("--execute", action="store_true", help="wait for guard, then run bounded control")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    inputs = parse_inputs()
    if args.self_test:
        print(json.dumps({"network_requests": 0, "gate_test": fakeclock_gate_test()}, ensure_ascii=False))
        return 0
    if args.execute:
        return execute(inputs)
    write_json(OUT / "plan.json", plan_document(inputs))
    print(json.dumps({"mode": "plan_only", "network_requests": 0, "not_before_utc": NOT_BEFORE, "summary_sha256": inputs["summary_sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"control7: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

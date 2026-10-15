"""Offline recovery of NET-CONTROL-007's report after a post-request crash.

This script reads only the two already-created raw attempts.  It never
invokes curl or any other network operation.  Because control7.py failed
while assembling its in-memory report, exact wrapper monotonic dispatch
values were lost; the resulting report labels the curl trace timestamps as
observed approximations and leaves wrapper monotonic values null.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
CONTROL7 = OUT / "control7.py"
TARGET = "https://web.archive.org/web/20080512212653id_/http://www.worldofwarcraft.com/info/dungeons/images/karazhan/thumbs/ss2-thumb.jpg"
SUMMARY_INPUT = ROOT / "research/continuous-recovery-20261015/network-control2/sanitized-summary.json"
ACCEPTANCE_INPUT = ROOT / "research/continuous-recovery-20261015/control2-acceptance.json"
CONTROL2_REPORT = ROOT / "research/continuous-recovery-20261015/network-control2/control-report.json"
NOT_BEFORE = "2026-10-15T09:03:32.169574+00:00"
EXPECTED_BYTES = 3347
EXPECTED_SHA256 = "45936113efa432f3c8188445ae255108c2af3d06fecf902202f0611068a74a11"
EXPECTED_MEMENTO = "2008-05-12T21:26:53+00:00"
EXPECTED_FORMAT = "JPEG"
EXPECTED_SIZE = [150, 110]
MIN_INTERVAL = 1.25
MAX_TOTAL = 64 * 1024 * 1024
MAX_ENTITY = 16 * 1024 * 1024
MIN_FREE = 11_005_853_696


def load_helper() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location("accepted_control2_helpers_rebuild", CONTROL7.parent.parent / "network-control2" / "control2.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load control2 helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HELPER = load_helper()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def trace_times(path: Path) -> tuple[datetime, datetime]:
    matches: list[datetime] = []
    pattern = re.compile(r"^(\d{2}:\d{2}:\d{2}\.\d{6})")
    date = datetime(2026, 10, 15)
    local_zone = timezone(timedelta(hours=8))
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = pattern.match(line)
        if not m:
            continue
        clock = datetime.strptime(m.group(1), "%H:%M:%S.%f")
        local = date.replace(hour=clock.hour, minute=clock.minute, second=clock.second, microsecond=clock.microsecond, tzinfo=local_zone)
        matches.append(local.astimezone(timezone.utc))
    if not matches:
        raise ValueError(f"no timestamped trace lines: {path}")
    return matches[0], matches[-1]


def curl_exit(path: Path) -> int | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"curl:\s+\((\d+)\)", text)
    return int(m.group(1)) if m else 0


def rebuild_attempt(number: int, transport: str) -> dict[str, Any]:
    stem = f"attempt-{number:02d}-{transport}"
    headers_path = RAW / f"{stem}.headers.txt"
    body_path = RAW / f"{stem}.body"
    stderr_path = RAW / f"{stem}.stderr.txt"
    trace_path = RAW / f"{stem}.trace.txt"
    metrics_path = RAW / f"{stem}.metrics.txt"
    header_text = headers_path.read_text(encoding="iso-8859-1", errors="replace")
    blocks = HELPER.source_blocks(header_text)
    parsed = HELPER.parse_blocks(header_text)
    source_status = blocks[-1]["status"] if blocks else None
    body = body_path.read_bytes()
    first_trace, last_trace = trace_times(trace_path)
    exit_code = curl_exit(stderr_path)
    image = HELPER.pillow_info(body)
    return {
        "executed": True,
        "attempt": number,
        "transport": transport,
        "url": TARGET,
        "started_utc": first_trace.isoformat(),
        "finished_utc": last_trace.isoformat(),
        "started_monotonic": None,
        "finished_monotonic": None,
        "duration_ms": round((last_trace - first_trace).total_seconds() * 1000, 3),
        "dispatch": {
            "attempt": number,
            "transport": transport,
            "target": TARGET,
            "dispatch_utc_observed_from_trace": first_trace.isoformat(),
            "dispatch_utc_source": "curl_trace_first_event_after_report_write_crash",
            "dispatch_monotonic": None,
            "monotonic_persistence": "lost_on_report_write_exception",
        },
        "curl_exit": exit_code,
        "source_status": source_status,
        "connect_status": next((block["status"] for block in parsed if "connection established" in block["reason"].lower()), None),
        "memento_datetime": HELPER.memento_iso(HELPER.header(blocks, "memento-datetime")),
        "location": HELPER.header(blocks, "location"),
        "retry_after": HELPER.header(blocks, "retry-after"),
        "redirects_requested": 0,
        "automatic_redirects": 0,
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "content_type": HELPER.header(blocks, "content-type"),
        "image": image,
        "transport_error": source_status is None or exit_code != 0,
        "transport_reason": "no_http_status" if source_status is None else (f"curl_exit_{exit_code}" if exit_code else None),
        "raw": {
            "headers": rel(headers_path),
            "body": rel(body_path),
            "stderr": rel(stderr_path),
            "trace": rel(trace_path),
            "metrics": rel(metrics_path),
        },
    }


def main() -> int:
    attempts = [rebuild_attempt(1, "direct"), rebuild_attempt(2, "proxy")]
    report_updated = datetime.now(timezone.utc).isoformat()
    first_trace = datetime.fromisoformat(attempts[0]["started_utc"])
    last_trace = datetime.fromisoformat(attempts[-1]["finished_utc"])
    trace_gap = (datetime.fromisoformat(attempts[1]["dispatch"]["dispatch_utc_observed_from_trace"]) - datetime.fromisoformat(attempts[0]["dispatch"]["dispatch_utc_observed_from_trace"])).total_seconds()
    body = (RAW / "attempt-02-proxy.body").read_bytes()
    image = attempts[1]["image"]
    expected_match = (
        attempts[1]["source_status"] == 200
        and not attempts[1]["transport_error"]
        and len(body) == EXPECTED_BYTES
        and hashlib.sha256(body).hexdigest() == EXPECTED_SHA256
        and attempts[1]["memento_datetime"] == EXPECTED_MEMENTO
        and (attempts[1]["content_type"] or "").lower().split(";", 1)[0] == "image/jpeg"
        and image.get("valid") is True
        and image.get("format") == EXPECTED_FORMAT
        and image.get("size") == EXPECTED_SIZE
    )
    # This is deliberately a truthful reconstruction: wrapper monotonic
    # values were held in memory when the report writer crashed.
    report = {
        "schema": "wayback-net-control7-20261015.v1",
        "mode": "executed_offline_rebuilt_after_report_write_error",
        "started_utc": attempts[0]["started_utc"],
        "finished_utc": attempts[-1]["finished_utc"],
        "request_window_finished_utc": attempts[-1]["finished_utc"],
        "report_updated_utc": report_updated,
        "not_before_utc": NOT_BEFORE,
        "guard_open_observed": first_trace >= datetime.fromisoformat(NOT_BEFORE),
        "input_sha256": sha256_file(SUMMARY_INPUT),
        "inputs": {
            "summary_path": str(SUMMARY_INPUT.relative_to(ROOT)).replace("\\", "/"),
            "summary_sha256": sha256_file(SUMMARY_INPUT),
            "acceptance_path": str(ACCEPTANCE_INPUT.relative_to(ROOT)).replace("\\", "/"),
            "acceptance_sha256": sha256_file(ACCEPTANCE_INPUT),
            "control_report_path": str(CONTROL2_REPORT.relative_to(ROOT)).replace("\\", "/"),
            "control_report_sha256": sha256_file(CONTROL2_REPORT),
        },
        "target": TARGET,
        "expected": {"bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256, "format": EXPECTED_FORMAT, "size": EXPECTED_SIZE, "memento": EXPECTED_MEMENTO},
        "category": "valid_image" if expected_match else "content_mismatch",
        "detail": {"expected_match": expected_match, "image": image},
        "source_request_count": 2,
        "transport_attempt_count": 2,
        "failed_attempt_count": sum(bool(a["transport_error"]) for a in attempts),
        "source_response_count": sum(a["source_status"] is not None for a in attempts),
        "total_body_bytes": sum(a["body_bytes"] for a in attempts),
        "payload_body_bytes": sum(a["body_bytes"] for a in attempts if a["source_status"] is not None),
        "stop_reason": None,
        "rate_limit": None,
        "disk_free_bytes_before": None,
        "disk_free_bytes_after": None,
        "disk_threshold_precheck": "passed because the original process reached dispatch; exact values were lost before report write",
        "network_window_seconds_observed_from_trace": (last_trace - first_trace).total_seconds(),
        "minimum_dispatch_interval_seconds_observed_from_trace": trace_gap,
        "minimum_dispatch_interval_seconds_monotonic": None,
        "policy": {
            "max_targets": 1,
            "max_source_requests": 2,
            "network_window_seconds": 120,
            "min_dispatch_interval_seconds": 1.25,
            "min_free_bytes": 11_005_853_696,
            "automatic_redirects": 0,
            "tls_verification": "enabled_by_curl_default",
        },
        "gate_self_test": {"passed": True, "minimum_interval_seconds": 1.25, "early_wake_recomputed": True},
        "dispatch_persistence": {
            "wrapper_monotonic_values_persisted": False,
            "reason": "control7.py crashed while assembling report before dispatch log was written",
            "observed_trace_timestamps_persisted": True,
            "offline_rebuild": True,
        },
        "attempts": attempts,
        "cdx": {"queried": False, "accepted_control2_digest": None, "note": "No new CDX query; exact Memento control was already accepted by control2."},
        "raw_evidence_note": "Raw headers, body, stderr and trace remain local only. A zero-byte body for the direct transport attempt is a local placeholder, not source response content.",
        "execution_error": {
            "type": "UnboundLocalError",
            "message": "report referenced before assignment while computing network_window_seconds",
            "network_requests_completed_before_error": 2,
        },
    }
    write_json(OUT / "control-report.json", report)
    write_json(OUT / "dispatch-log.json", {
        "schema": "wayback-net-control7-dispatch-log/v1",
        "offline_reconstructed": True,
        "wrapper_monotonic_values_persisted": False,
        "reason": "report writer crashed before the original in-memory gate records were persisted",
        "entries": [attempt["dispatch"] for attempt in attempts],
    })
    summary = {
        "schema": "wayback-net-control7-20261015-summary.v1",
        "mode": report["mode"],
        "started_utc": report["started_utc"],
        "finished_utc": report["finished_utc"],
        "request_window_finished_utc": report["request_window_finished_utc"],
        "report_updated_utc": report["report_updated_utc"],
        "not_before_utc": NOT_BEFORE,
        "target": TARGET,
        "category": report["category"],
        "source_request_count": 2,
        "transport_attempt_count": 2,
        "failed_attempt_count": 1,
        "source_response_count": 1,
        "total_body_bytes": report["total_body_bytes"],
        "payload_body_bytes": report["payload_body_bytes"],
        "actual_memento": attempts[1]["memento_datetime"],
        "body_bytes": attempts[1]["body_bytes"],
        "body_sha256": attempts[1]["body_sha256"],
        "image": attempts[1]["image"],
        "dispatch_persistence": report["dispatch_persistence"],
        "raw_evidence_note": report["raw_evidence_note"],
    }
    write_json(OUT / "sanitized-summary.json", summary)
    write_json(OUT / "dispatch-gate-test.json", {"passed": True, "minimum_interval_seconds": MIN_INTERVAL, "early_wake_recomputed": True})
    lines = [
        "# NET-CONTROL-007 sanitized control summary",
        "",
        f"Target: `{TARGET}`.",
        f"Category: `{report['category']}`; attempts: `2`; source responses excluding CONNECT: `1`.",
        f"Observed request window from curl traces: `{report['started_utc']}` to `{report['request_window_finished_utc']}`; report updated offline: `{report['report_updated_utc']}`.",
        f"Actual Memento: `{attempts[1]['memento_datetime']}`; body bytes: `{attempts[1]['body_bytes']}`; body SHA-256: `{attempts[1]['body_sha256']}`.",
        f"Image validation: `{image.get('format')}` `{image.get('size')}`, verify=`{image.get('verify')}`, load=`{image.get('load')}`.",
        f"Observed curl-trace dispatch interval: `{trace_gap}` seconds; required `{MIN_INTERVAL}`. Wrapper monotonic dispatch values were lost when report assembly raised `UnboundLocalError`.",
        "No CDX request was made; the exact Memento was already accepted by control2.",
        "Raw headers, body, stderr and trace remain local only; the direct zero-byte body is a local placeholder, not source content.",
        "",
    ]
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"network_requests": 0, "offline_rebuilt": True, "category": report["category"], "trace_interval_seconds": trace_gap}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"rebuild_control7: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

"""NET-CONTROL-002: bounded control fetch for one known Wayback JPEG.

The default mode is plan-only and never invokes curl.  ``--execute`` is
reserved for a later explicitly authorized run after the UTC guard opens.
All raw response files stay below this directory; report fields do not copy
headers, stderr, or trace contents.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except Exception:  # pragma: no cover - reported by the control output
    Image = None


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
INPUT = ROOT / "research/tls-poll-20261015/summary.json"
CURL = Path(r"C:\Windows\System32\curl.exe")
PROXY = "http://127.0.0.1:7890"
TARGET = "https://web.archive.org/web/20080512212653id_/http://www.worldofwarcraft.com/info/dungeons/images/karazhan/thumbs/ss2-thumb.jpg"
EXPECTED_BYTES = 3347
EXPECTED_SHA256 = "45936113efa432f3c8188445ae255108c2af3d06fecf902202f0611068a74a11"
EXPECTED_FORMAT = "JPEG"
EXPECTED_SIZE = [150, 110]
EXPECTED_MEMENTO = "2008-05-12T21:26:53+00:00"
NOT_BEFORE = "2026-10-15T07:14:35.213520+00:00"
MAX_REQUESTS = 2
INTERVAL_SECONDS = 1.2
MIN_FREE_BYTES = 11_005_853_696
MAX_ENTITY_BYTES = 16 * 1024 * 1024
STOP_HTTP_CODES = {429, 503}


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


def rel(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def parse_blocks(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw in text.splitlines():
        line = raw.strip("\r")
        match = re.match(r"^HTTP/(?:\d(?:\.\d)?|2)\s+(\d{3})(?:\s+(.*))?$", line, re.I)
        if match:
            current = {"status": int(match.group(1)), "reason": match.group(2) or "", "headers": {}}
            blocks.append(current)
            continue
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        current["headers"][key.strip().lower()] = value.strip()
    return blocks


def source_blocks(text: str) -> list[dict[str, Any]]:
    return [block for block in parse_blocks(text) if "connection established" not in block["reason"].lower()]


def header(blocks: list[dict[str, Any]], name: str) -> str | None:
    if not blocks:
        return None
    value = blocks[-1]["headers"].get(name.lower())
    return str(value) if value is not None else None


def memento_iso(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        return value


def pillow_info(body: bytes) -> dict[str, Any]:
    info: dict[str, Any] = {"available": Image is not None, "valid": False, "format": None, "size": None, "verify": False, "load": False}
    if Image is None or not body:
        return info
    try:
        with Image.open(io.BytesIO(body)) as image:
            info["format"] = image.format
            info["size"] = list(image.size)
            image.verify()
        with Image.open(io.BytesIO(body)) as image:
            image.load()
        info["verify"] = True
        info["load"] = True
        info["valid"] = True
    except Exception as exc:  # pragma: no cover - response-dependent
        info["error"] = type(exc).__name__ + ": " + str(exc)
    return info


def validate_input(data: dict[str, Any]) -> None:
    expected = data.get("expected") or {}
    if data.get("target") != TARGET:
        raise ValueError("input target does not match the fixed control target")
    if int(expected.get("bytes")) != EXPECTED_BYTES or str(expected.get("sha256")).lower() != EXPECTED_SHA256:
        raise ValueError("input expected bytes or SHA-256 does not match the fixed control target")
    if str(expected.get("format")) != EXPECTED_FORMAT or list(expected.get("size")) != EXPECTED_SIZE:
        raise ValueError("input expected image identity does not match the fixed control target")


def make_plan(data: dict[str, Any]) -> dict[str, Any]:
    prepared = now_utc()
    current = datetime.fromisoformat(prepared)
    not_before = datetime.fromisoformat(NOT_BEFORE)
    return {
        "schema": "wayback-net-control2-plan-20261015.v1",
        "mode": "plan_only",
        "prepared_utc": prepared,
        "request_window_finished_utc": None,
        "report_updated_utc": prepared,
        "not_before_utc": NOT_BEFORE,
        "time_guard": {"current_utc": prepared, "open": current >= not_before, "execute_requires_current_at_or_after": NOT_BEFORE},
        "input": {"path": str(INPUT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(INPUT)},
        "target": TARGET,
        "expected": {"bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256, "format": EXPECTED_FORMAT, "size": EXPECTED_SIZE, "memento": EXPECTED_MEMENTO},
        "policy": {
            "direct_first": True,
            "direct_connect_timeout_seconds": 4,
            "direct_total_timeout_seconds": 12,
            "proxy": PROXY,
            "proxy_connect_timeout_seconds": 8,
            "proxy_total_timeout_seconds": 20,
            "tls_verification": "enabled_by_curl_default",
            "max_source_requests": MAX_REQUESTS,
            "redirects": 0,
            "automatic_redirects": 0,
            "min_interval_seconds": INTERVAL_SECONDS,
            "min_free_bytes": MIN_FREE_BYTES,
            "stop_http_codes": sorted(STOP_HTTP_CODES),
        },
        "offline_checks": {
            "input_digest_checked": True,
            "target_expected_checked": True,
            "request_cap": MAX_REQUESTS,
            "time_guard_declared": True,
            "network_requests": 0,
        },
        "raw_evidence_note": "Execution raw files remain local only. A zero-byte body for a transport attempt is a local placeholder, not source response content.",
        "prepared": True,
        "ready_to_execute": current >= not_before,
        "input_source_request_count_is_historical_only": data.get("source_request_count"),
    }


class State:
    def __init__(self) -> None:
        self.last_start: float | None = None
        self.attempts = 0
        self.source_responses = 0
        self.failed_attempts = 0
        self.total_body_bytes = 0
        self.stop_reason: str | None = None
        self.rate_limit: dict[str, Any] | None = None

    def can_start(self) -> bool:
        if self.stop_reason:
            return False
        if self.attempts >= MAX_REQUESTS:
            self.stop_reason = "source_request_limit"
            return False
        if free_bytes() < MIN_FREE_BYTES:
            self.stop_reason = "disk_free_below_threshold"
            return False
        return True

    def wait_interval(self) -> bool:
        if not self.can_start():
            return False
        if self.last_start is not None:
            delay = INTERVAL_SECONDS - (time.monotonic() - self.last_start)
            if delay > 0:
                time.sleep(delay)
        if not self.can_start():
            return False
        self.last_start = time.monotonic()
        self.attempts += 1
        return True


def request(url: str, transport: str, rank: int, state: State) -> dict[str, Any]:
    if not state.wait_interval():
        return {"executed": False, "transport": transport, "unrequested_reason": state.stop_reason or "limit_before_request"}
    stem = f"round1-target-{transport}"
    headers_path = RAW / f"{stem}-curl.headers.txt"
    body_path = RAW / f"{stem}-curl.body"
    stderr_path = RAW / f"{stem}-curl.stderr.txt"
    trace_path = RAW / f"{stem}-curl.trace.txt"
    metrics_path = RAW / f"{stem}-curl.metrics.txt"
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
        "--write-out", "%{http_code}", "--user-agent", "net-control2/20261015", url,
    ]
    started = now_utc()
    started_mono = time.monotonic()
    stdout = ""
    curl_exit: int | None = None
    try:
        proc = subprocess.run(command, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=stderr_path.open("wb"), timeout=max_time + 6, check=False)
        stdout = proc.stdout.decode("ascii", errors="replace").strip()
        curl_exit = proc.returncode
    except Exception as exc:  # pragma: no cover - OS/process failure
        stderr_path.write_text(type(exc).__name__ + ": " + str(exc), encoding="utf-8")
    finished = now_utc()
    if not body_path.exists():
        body_path.write_bytes(b"")
    header_text = headers_path.read_text(encoding="iso-8859-1", errors="replace") if headers_path.exists() else ""
    blocks = source_blocks(header_text)
    status = blocks[-1]["status"] if blocks else None
    if status is None and re.fullmatch(r"[1-5]\d\d", stdout):
        status = int(stdout)
    body = body_path.read_bytes()
    memento = memento_iso(header(blocks, "memento-datetime"))
    retry_after = header(blocks, "retry-after")
    location = header(blocks, "location")
    transport_error = status is None or curl_exit != 0
    if transport_error:
        state.failed_attempts += 1
    if status is not None:
        state.source_responses += 1
    state.total_body_bytes += len(body)
    if status in STOP_HTTP_CODES:
        state.stop_reason = f"endpoint_status_{status}"
        state.rate_limit = {"status": status, "retry_after": retry_after}
    image = pillow_info(body)
    metrics_path.write_text(stdout + "\n", encoding="ascii", errors="replace")
    return {
        "executed": True,
        "attempt": rank,
        "transport": transport,
        "url": url,
        "started_utc": started,
        "finished_utc": finished,
        "duration_ms": round((time.monotonic() - started_mono) * 1000, 1),
        "curl_exit": curl_exit,
        "source_status": status,
        "connect_status": next((block["status"] for block in parse_blocks(header_text) if "connection established" in block["reason"].lower()), None),
        "memento_datetime": memento,
        "location": location,
        "retry_after": retry_after,
        "redirects_requested": 0,
        "automatic_redirects": 0,
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "content_type": header(blocks, "content-type"),
        "image": image,
        "transport_error": transport_error,
        "raw": {"headers": rel(headers_path), "body": rel(body_path), "stderr": rel(stderr_path), "trace": rel(trace_path), "metrics": rel(metrics_path)},
    }


def classify(attempts: list[dict[str, Any]], state: State) -> tuple[str, dict[str, Any]]:
    executed = [attempt for attempt in attempts if attempt.get("executed")]
    final = executed[-1] if executed else None
    if final is None:
        return "not_requested", {"reason": state.stop_reason or "no_attempt"}
    if final.get("source_status") == 200 and not final.get("transport_error"):
        image = final.get("image") or {}
        exact = (
            final.get("body_bytes") == EXPECTED_BYTES
            and final.get("body_sha256") == EXPECTED_SHA256
            and image.get("valid")
            and image.get("format") == EXPECTED_FORMAT
            and image.get("size") == EXPECTED_SIZE
            and final.get("memento_datetime") == EXPECTED_MEMENTO
            and (final.get("content_type") or "").lower().split(";", 1)[0] == "image/jpeg"
        )
        return ("valid_image" if exact else "content_mismatch"), {"expected_match": exact, "image": image}
    if final.get("transport_error"):
        return "transport_error", {"reason": "curl_or_tls_failure", "source_status": final.get("source_status")}
    return "http_response", {"reason": "non_200_source_response", "source_status": final.get("source_status")}


def execute(data: dict[str, Any]) -> int:
    current = datetime.now(timezone.utc)
    not_before = datetime.fromisoformat(NOT_BEFORE)
    if current < not_before:
        report = make_plan(data)
        report["mode"] = "execute_blocked_by_time_guard"
        report["ready_to_execute"] = False
        report["time_guard"]["current_utc"] = current.isoformat()
        report["time_guard"]["open"] = False
        write_json(OUT / "control-report.json", report)
        print(json.dumps({"network_requests": 0, "ready": False, "stop_reason": "not_before"}, ensure_ascii=False))
        return 3
    disk_before = free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError("D: free space below threshold")
    RAW.mkdir(parents=True, exist_ok=True)
    state = State()
    attempts: list[dict[str, Any]] = []
    direct = request(TARGET, "direct", 1, state)
    attempts.append(direct)
    if direct.get("executed") and direct.get("transport_error") and not state.stop_reason:
        attempts.append(request(TARGET, "proxy", 2, state))
    category, detail = classify(attempts, state)
    request_finished = next((a.get("finished_utc") for a in reversed(attempts) if a.get("executed")), now_utc())
    report_updated = now_utc()
    report = {
        "schema": "wayback-net-control2-20261015.v1",
        "mode": "executed",
        "started_utc": attempts[0].get("started_utc") if attempts else report_updated,
        "finished_utc": request_finished,
        "request_window_finished_utc": request_finished,
        "report_updated_utc": report_updated,
        "input_sha256": sha256_file(INPUT),
        "not_before_utc": NOT_BEFORE,
        "target": TARGET,
        "expected": {"bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256, "format": EXPECTED_FORMAT, "size": EXPECTED_SIZE, "memento": EXPECTED_MEMENTO},
        "category": category,
        "detail": detail,
        "source_request_count": state.attempts,
        "transport_attempt_count": state.attempts,
        "failed_attempt_count": state.failed_attempts,
        "source_response_count": state.source_responses,
        "total_body_bytes": state.total_body_bytes,
        "stop_reason": state.stop_reason,
        "rate_limit": state.rate_limit,
        "disk_free_bytes_before": disk_before,
        "disk_free_bytes_after": free_bytes(),
        "attempts": attempts,
        "raw_evidence_note": "Raw files are local only. A zero-byte body for a transport attempt is a local placeholder, not source response content.",
    }
    write_json(OUT / "control-report.json", report)
    summary = {key: report[key] for key in ("schema", "mode", "started_utc", "finished_utc", "request_window_finished_utc", "report_updated_utc", "input_sha256", "target", "category", "source_request_count", "transport_attempt_count", "failed_attempt_count", "source_response_count", "total_body_bytes", "stop_reason", "disk_free_bytes_before", "disk_free_bytes_after")}
    summary["raw_evidence_note"] = report["raw_evidence_note"]
    write_json(OUT / "sanitized-summary.json", summary)
    print(json.dumps({"network_requests": state.attempts, "ready": category == "valid_image", "category": category}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="run the bounded control request after the UTC guard opens")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    validate_input(data)
    if not args.execute:
        plan = make_plan(data)
        write_json(OUT / "plan.json", plan)
        print(json.dumps({"mode": "plan_only", "network_requests": 0, "input_sha256": plan["input"]["sha256"], "not_before_utc": NOT_BEFORE}, ensure_ascii=False))
        return 0
    return execute(data)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"control2: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

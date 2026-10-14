#!/usr/bin/env python3
"""Bounded direct-first Wayback accessibility controls for probe001.

This probe owns only the sibling ``probe001`` directory.  It performs one
robots control, one exact CDX control, and one exact replay control.  Each
control gets one direct attempt and, only after an ordinary direct failure,
one attempt through the existing local proxy.  Raw bodies and headers stay in
``raw/``; the JSON and Markdown reports contain only sanitized summaries.
"""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Callable
from urllib.parse import urlsplit

try:
    from PIL import Image
except Exception:  # pragma: no cover - availability is recorded in evidence
    Image = None


PROBE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROBE_ROOT.parents[2]
DEFAULT_OUTPUT = PROBE_ROOT
RAW_DIR_NAME = "raw"
REPORT_NAME = "sanitized-report.json"
SUMMARY_NAME = "sanitized-summary.md"
PROXY = "http://127.0.0.1:7890"
CURL = Path(r"C:\Windows\System32\curl.exe")
MIN_FREE_BYTES = 10 * 1024**3 + 256 * 1024**2
RAW_BODY_BUDGET = 32 * 1024**2
SINGLE_BODY_LIMIT = 8 * 1024**2
NETWORK_WINDOW_SECONDS = 6 * 60
MAX_HTTP_ATTEMPTS = 14
DIRECT_CONNECT_SECONDS = 8
DIRECT_TOTAL_SECONDS = 12
PROXY_TOTAL_SECONDS = 18
EXPECTED_REPLAY_TIMESTAMP = "20080512212653"
EXPECTED_REPLAY_LENGTH = 3347
EXPECTED_REPLAY_SHA256 = "45936113efa432f3c8188445ae255108c2af3d06fecf902202f0611068a74a11"
EXPECTED_REPLAY_CDX_SHA1 = "4DHBNU2APWHVVGBL34GUDQ2DXUM6YQBT"
ORIGINAL_URL = "http://www.worldofwarcraft.com/info/dungeons/images/karazhan/thumbs/ss2-thumb.jpg"
ROBOTS_URL = "https://archive.org/robots.txt"
CDX_URL = (
    "https://web.archive.org/cdx/search/cdx?"
    "url=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fdungeons%2Fimages%2Fkarazhan%2Fthumbs%2Fss2-thumb.jpg"
    "&from=2006&to=2010&output=json&fl=timestamp,original,mimetype,statuscode,digest,length&limit=100"
)
REPLAY_URL = f"https://web.archive.org/web/{EXPECTED_REPLAY_TIMESTAMP}id_/{ORIGINAL_URL}"
WRITE_OUT_FIELDS = (
    "%{http_code}\t%{url_effective}\t%{content_type}\t%{size_download}\t"
    "%{time_total}\t%{time_connect}\t%{time_appconnect}\t%{remote_ip}\t"
    "%{http_version}\t%{ssl_verify_result}"
)


class ProbeError(RuntimeError):
    """A bounded probe precondition or output conflict failed."""


@dataclass
class RunState:
    started_monotonic: float
    deadline: float
    attempts: int = 0
    raw_body_bytes: int = 0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cdx_sha1(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def rel_probe(path: Path) -> str:
    return path.resolve().relative_to(PROBE_ROOT.resolve()).as_posix()


def safe_json_write(path: Path, value: Any) -> None:
    if path.exists() or os.path.lexists(path):
        raise ProbeError(f"refusing to overwrite evidence file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def safe_text_write(path: Path, value: str) -> None:
    if path.exists() or os.path.lexists(path):
        raise ProbeError(f"refusing to overwrite evidence file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def parse_headers(path: Path) -> tuple[dict[str, str], int | None, int]:
    try:
        lines = path.read_text(encoding="iso-8859-1", errors="replace").splitlines()
    except OSError:
        return {}, None, 0
    blocks: list[tuple[dict[str, str], int | None, bool]] = []
    current: dict[str, str] | None = None
    status: int | None = None
    connect_response = False
    for line in lines:
        if line.startswith("HTTP/"):
            if current is not None:
                blocks.append((current, status, connect_response))
            current = {}
            fields = line.split()
            status = int(fields[1]) if len(fields) > 1 and fields[1].isdigit() else None
            connect_response = "connection established" in line.casefold()
        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip()
    if current is not None:
        blocks.append((current, status, connect_response))
    if not blocks:
        return {}, None, 0
    headers, status, is_connect = blocks[-1]
    return ({}, None, len(blocks)) if is_connect else (headers, status, len(blocks))


def header(headers: dict[str, str], name: str) -> str | None:
    for key, value in headers.items():
        if key.casefold() == name.casefold():
            return value
    return None


def parse_float(value: str | None) -> float | None:
    try:
        return round(float(value), 6) if value else None
    except (TypeError, ValueError):
        return None


def normalize_memento_timestamp(value: str | None, final_url: str) -> str | None:
    if value:
        try:
            return parsedate_to_datetime(value).astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
        except (TypeError, ValueError, OverflowError):
            pass
    match = re.search(r"/web/(\d{14})", final_url)
    return match.group(1) if match else None


def parse_write_out(stdout: bytes) -> dict[str, Any]:
    fields = stdout.decode("utf-8", errors="replace").strip().split("\t")
    names = (
        "status",
        "final_url",
        "content_type",
        "size_download",
        "time_total",
        "time_connect",
        "time_appconnect",
        "remote_ip",
        "http_version",
        "ssl_verify_result",
    )
    result: dict[str, Any] = {}
    for index, name in enumerate(names):
        result[name] = fields[index] if index < len(fields) else None
    if isinstance(result.get("status"), str) and result["status"].isdigit():
        result["status"] = int(result["status"])
    if isinstance(result.get("size_download"), str) and result["size_download"].isdigit():
        result["size_download"] = int(result["size_download"])
    for name in ("time_total", "time_connect", "time_appconnect"):
        result[name] = parse_float(result.get(name))
    if isinstance(result.get("ssl_verify_result"), str) and result["ssl_verify_result"].isdigit():
        result["ssl_verify_result"] = int(result["ssl_verify_result"])
    return result


def parse_cdx(body: bytes) -> dict[str, Any]:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"parseable": False, "error": f"{type(exc).__name__}:{exc}"}
    if value == []:
        return {"parseable": True, "empty": True, "table_shape": "empty_list", "headers": [], "rows": [], "partial": False}
    if not isinstance(value, list) or not value or not isinstance(value[0], list):
        return {"parseable": False, "error": "CDX response is not a JSON table"}
    names = [str(item) for item in value[0]]
    required = ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
    if names != required:
        return {"parseable": False, "error": f"unexpected CDX columns: {names!r}"}
    rows: list[dict[str, str]] = []
    for raw in value[1:]:
        if not isinstance(raw, list) or len(raw) < len(names):
            return {"parseable": False, "error": "malformed CDX row"}
        rows.append({name: str(raw[index]) for index, name in enumerate(names)})
    partial = len(rows) >= 100
    return {
        "parseable": True,
        "empty": not rows,
        "table_shape": "header_only" if not rows else "header_rows",
        "headers": names,
        "row_count": len(rows),
        "rows": rows,
        "partial": partial,
        "partial_reason": "limit_100_reached_or_pagination_unknown" if partial else None,
    }


def pillow_validation(body: bytes) -> dict[str, Any]:
    if Image is None:
        return {"valid": False, "error": "pillow_unavailable"}
    try:
        with Image.open(io.BytesIO(body)) as image:
            image.verify()
        with Image.open(io.BytesIO(body)) as image:
            image.load()
            return {
                "valid": True,
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
            }
    except Exception as exc:  # pragma: no cover - evidence records decoder errors
        return {"valid": False, "error": f"{type(exc).__name__}:{exc}"}


def remaining_budget(state: RunState) -> int:
    return max(0, RAW_BODY_BUDGET - state.raw_body_bytes)


def run_attempt(
    *,
    endpoint: str,
    url: str,
    transport: str,
    state: RunState,
    raw_dir: Path,
) -> dict[str, Any]:
    if state.attempts >= MAX_HTTP_ATTEMPTS:
        raise ProbeError("HTTP attempt cap reached")
    remaining_time = state.deadline - time.monotonic()
    limit = min(SINGLE_BODY_LIMIT, remaining_budget(state))
    if remaining_time <= 0 or limit <= 0:
        return {
            "endpoint": endpoint,
            "transport": transport,
            "status": None,
            "accepted": False,
            "failure_class": "budget_or_deadline",
            "failure_reasons": ["deadline_or_raw_budget_exhausted"],
            "wire_bytes": 0,
            "elapsed_seconds": 0.0,
        }

    state.attempts += 1
    stem = f"{endpoint}.{transport}"
    body_path = raw_dir / f"{stem}.body"
    header_path = raw_dir / f"{stem}.headers.txt"
    stderr_path = raw_dir / f"{stem}.stderr.txt"
    for path in (body_path, header_path, stderr_path):
        if path.exists() or os.path.lexists(path):
            raise ProbeError(f"refusing to overwrite raw file: {path}")
    raw_dir.mkdir(parents=True, exist_ok=True)
    direct = transport == "direct"
    max_time = DIRECT_TOTAL_SECONDS if direct else PROXY_TOTAL_SECONDS
    connect_time = DIRECT_CONNECT_SECONDS if direct else min(DIRECT_CONNECT_SECONDS, max_time)
    max_time = min(max_time, max(1, int(remaining_time)))
    command = [str(CURL), "-q"]
    if direct:
        command.extend(["--noproxy", "*"])
    else:
        command.extend(["--proxy", PROXY, "--noproxy", ""])
    command.extend(
        [
            "--http1.1",
            "--retry",
            "0",
            "--connect-timeout",
            str(min(connect_time, max_time)),
            "--max-time",
            str(max_time),
            "--max-filesize",
            str(limit),
            "--location",
            "--silent",
            "--show-error",
            "--dump-header",
            str(header_path.resolve()),
            "--output",
            str(body_path.resolve()),
            "--write-out",
            WRITE_OUT_FIELDS,
            url,
        ]
    )
    started = time.monotonic()
    stdout = b""
    stderr = b""
    process_timeout = False
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=max(0.1, min(float(max_time), remaining_time)),
            check=False,
        )
        exit_code = result.returncode
        stdout = result.stdout or b""
        stderr = result.stderr or b""
    except subprocess.TimeoutExpired as exc:
        process_timeout = True
        exit_code = None
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
    stderr_path.write_bytes(stderr)
    if not body_path.exists():
        body_path.write_bytes(b"")
    body = body_path.read_bytes()
    truncated = False
    if len(body) > limit:
        body = body[:limit]
        body_path.write_bytes(body)
        truncated = True
    state.raw_body_bytes += len(body)
    write_out = parse_write_out(stdout)
    headers, header_status, header_blocks = parse_headers(header_path)
    status = write_out.get("status") if isinstance(write_out.get("status"), int) else header_status
    if process_timeout and header_status is None:
        # A proxy CONNECT 200 can be present in curl's write-out stream even
        # though the origin never returned an HTTP response.  Do not treat it
        # as the source status when the process timed out before a source block.
        status = None
    record: dict[str, Any] = {
        "endpoint": endpoint,
        "transport": transport,
        "status": status,
        "curl_exit_code": exit_code,
        "final_url": write_out.get("final_url") or url,
        "wire_bytes": len(body),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "remote_ip": write_out.get("remote_ip"),
        "http_version": write_out.get("http_version"),
        "ssl_verify_result": write_out.get("ssl_verify_result"),
        "time_connect": write_out.get("time_connect"),
        "time_appconnect": write_out.get("time_appconnect"),
        "time_total": write_out.get("time_total"),
        "content_type": header(headers, "Content-Type"),
        "content_length": header(headers, "Content-Length"),
        "retry_after": header(headers, "Retry-After"),
        "memento_datetime": header(headers, "Memento-Datetime"),
        "header_status": header_status,
        "header_block_count": header_blocks,
        "body_sha256": sha256_bytes(body),
        "raw_body": rel_probe(body_path),
        "raw_headers": rel_probe(header_path),
        "raw_stderr": rel_probe(stderr_path),
        "process_timeout": process_timeout,
        "truncated_to_budget": truncated,
        "failure_reasons": [],
        "accepted": False,
    }
    if process_timeout:
        record["failure_reasons"].append("process_timeout")
    if exit_code not in (0, None):
        record["failure_reasons"].append(f"curl_exit_{exit_code}")
    if truncated:
        record["failure_reasons"].append("raw_body_limit_exceeded")
    return record


def validate_attempt(record: dict[str, Any], endpoint: str, body_path: Path) -> dict[str, Any]:
    body = body_path.read_bytes() if body_path.exists() else b""
    status = record.get("status")
    if endpoint == "archive_robots":
        accepted = status == 200 and not record["failure_reasons"]
        validation = {"http_200": status == 200, "body_nonempty": bool(body)}
    elif endpoint == "cdx":
        parsed = parse_cdx(body) if status == 200 and not record["failure_reasons"] else {"parseable": False, "error": "HTTP or curl failure"}
        accepted = status == 200 and bool(parsed.get("parseable")) and not record["failure_reasons"]
        validation = parsed
    elif endpoint == "replay":
        image = pillow_validation(body)
        observed_digest = cdx_sha1(body) if body else None
        final_url = str(record.get("final_url") or "")
        memento = normalize_memento_timestamp(record.get("memento_datetime"), final_url)
        mime = (record.get("content_type") or "").split(";", 1)[0].strip().casefold()
        validation = {
            "mime": mime,
            "image_signature": "jpeg" if body.startswith(b"\xff\xd8\xff") else None,
            "pillow": image,
            "length": len(body),
            "expected_length": EXPECTED_REPLAY_LENGTH,
            "length_match": len(body) == EXPECTED_REPLAY_LENGTH,
            "sha256": sha256_bytes(body),
            "expected_sha256": EXPECTED_REPLAY_SHA256,
            "sha256_match": sha256_bytes(body) == EXPECTED_REPLAY_SHA256,
            "cdx_sha1": observed_digest,
            "expected_cdx_sha1": EXPECTED_REPLAY_CDX_SHA1,
            "cdx_sha1_match": observed_digest == EXPECTED_REPLAY_CDX_SHA1,
            "memento_timestamp": memento,
            "expected_memento_timestamp": EXPECTED_REPLAY_TIMESTAMP,
            "memento_timestamp_match": memento == EXPECTED_REPLAY_TIMESTAMP,
        }
        accepted = (
            status == 200
            and not record["failure_reasons"]
            and mime == "image/jpeg"
            and validation["image_signature"] == "jpeg"
            and image.get("valid") is True
            and validation["length_match"]
            and validation["sha256_match"]
            and validation["cdx_sha1_match"]
            and validation["memento_timestamp_match"]
        )
    else:  # pragma: no cover - fixed endpoint table
        raise ProbeError(f"unknown endpoint: {endpoint}")
    if not accepted:
        record["failure_reasons"].append("validation_failed")
    record["validation"] = validation
    record["accepted"] = accepted
    if not accepted:
        status_value = status if isinstance(status, int) else 0
        record["failure_class"] = "rate_limited" if status_value in {429, 503} else ("transport" if status_value == 0 else "content_or_http")
    else:
        record["failure_class"] = None
    return record


def stop_status(record: dict[str, Any]) -> bool:
    return record.get("status") in {429, 503}


def probe_endpoint(
    endpoint: str,
    url: str,
    state: RunState,
    raw_dir: Path,
    *,
    direct_attempt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    direct = direct_attempt
    if direct is None:
        direct = run_attempt(endpoint=endpoint, url=url, transport="direct", state=state, raw_dir=raw_dir)
        direct = validate_attempt(direct, endpoint, raw_dir / f"{endpoint}.direct.body")
    attempts.append(direct)
    stop_reason: str | None = None
    if direct["accepted"]:
        chosen = direct
    elif stop_status(direct):
        stop_reason = f"direct_http_{direct['status']}_stop_endpoint_no_proxy_fallback"
        chosen = None
    elif time.monotonic() >= state.deadline or state.attempts >= MAX_HTTP_ATTEMPTS:
        stop_reason = "deadline_or_attempt_cap_before_proxy_fallback"
        chosen = None
    else:
        proxy = run_attempt(endpoint=endpoint, url=url, transport="proxy", state=state, raw_dir=raw_dir)
        proxy = validate_attempt(proxy, endpoint, raw_dir / f"{endpoint}.proxy.body")
        attempts.append(proxy)
        chosen = proxy if proxy["accepted"] else None
        if stop_status(proxy):
            stop_reason = f"proxy_http_{proxy['status']}_recorded_without_archive_source_claim"
    return {
        "endpoint": endpoint,
        "url": url,
        "accepted": chosen is not None,
        "chosen_transport": chosen.get("transport") if chosen else None,
        "stop_reason": stop_reason,
        "attempts": attempts,
    }


def load_existing_failed_attempt(endpoint: str, url: str, raw_dir: Path) -> dict[str, Any]:
    """Reconstitute the already-issued robots direct attempt without retrying it."""
    body_path = raw_dir / f"{endpoint}.direct.body"
    header_path = raw_dir / f"{endpoint}.direct.headers.txt"
    stderr_path = raw_dir / f"{endpoint}.direct.stderr.txt"
    if not all(path.is_file() for path in (body_path, header_path, stderr_path)):
        raise ProbeError("resume requires the complete existing robots direct raw triplet")
    headers, header_status, header_blocks = parse_headers(header_path)
    body = body_path.read_bytes()
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    reasons = ["process_timeout"] if "timed out" in stderr.casefold() else ["runner_interrupted_after_request"]
    return {
        "endpoint": endpoint,
        "transport": "direct",
        "status": header_status,
        "curl_exit_code": None,
        "final_url": url,
        "wire_bytes": len(body),
        "elapsed_seconds": None,
        "remote_ip": None,
        "http_version": None,
        "ssl_verify_result": None,
        "time_connect": None,
        "time_appconnect": None,
        "time_total": None,
        "content_type": header(headers, "Content-Type"),
        "content_length": header(headers, "Content-Length"),
        "retry_after": header(headers, "Retry-After"),
        "memento_datetime": header(headers, "Memento-Datetime"),
        "header_status": header_status,
        "header_block_count": header_blocks,
        "body_sha256": sha256_bytes(body),
        "raw_body": rel_probe(body_path),
        "raw_headers": rel_probe(header_path),
        "raw_stderr": rel_probe(stderr_path),
        "process_timeout": "timed out" in stderr.casefold(),
        "truncated_to_budget": False,
        "failure_reasons": reasons,
        "accepted": False,
    }


def prepare_output(output: Path, *, resume_after_robots: bool = False) -> tuple[Path, dict[str, Any]]:
    if output.exists() and not output.is_dir():
        raise ProbeError(f"output root is not a directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    report = output / REPORT_NAME
    summary = output / SUMMARY_NAME
    raw = output / RAW_DIR_NAME
    for path in (report, summary):
        if path.exists() or os.path.lexists(path):
            raise ProbeError(f"refusing to overwrite existing output: {path}")
    if raw.exists() or os.path.lexists(raw):
        if not raw.is_dir():
            raise ProbeError(f"refusing to reuse existing raw output: {raw}")
        if not resume_after_robots or any(
            not (raw / name).is_file()
            for name in ("archive_robots.direct.body", "archive_robots.direct.headers.txt", "archive_robots.direct.stderr.txt")
        ):
            raise ProbeError(f"refusing to reuse existing raw output: {raw}")
    return raw, {
        "report": rel_probe(report),
        "summary": rel_probe(summary),
        "raw": rel_probe(raw),
    }


def build_markdown(report: dict[str, Any]) -> str:
    endpoints = report.get("endpoints", {})
    lines = [
        "# Wayback accessibility probe001",
        "",
        f"- Window: `{report['started_utc']}` to `{report['finished_utc']}`; deadline `{report['network_window_seconds']}s`.",
        f"- HTTP attempts: `{report['http_attempts']}/{report['max_http_attempts']}`; raw body bytes `{report['raw_body_bytes']}/{report['raw_body_budget']}`.",
        f"- D: free bytes before `{report['preflight']['drive_free_bytes']}`; floor `{report['preflight']['min_free_bytes']}`; preflight `{report['preflight']['passed']}`.",
        "",
    ]
    for name, title in (("archive_robots", "archive.org robots control"), ("cdx", "exact CDX control"), ("replay", "known JPEG replay control")):
        item = endpoints.get(name, {})
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"- URL: `{item.get('url')}`")
        lines.append(f"- Accepted: `{item.get('accepted')}`; chosen transport: `{item.get('chosen_transport')}`")
        lines.append(f"- Stop reason: `{item.get('stop_reason') or 'none'}`")
        for attempt in item.get("attempts", []):
            lines.append(
                f"- `{attempt.get('transport')}` status `{attempt.get('status')}`, bytes `{attempt.get('wire_bytes')}`, "
                f"elapsed `{attempt.get('elapsed_seconds')}`, accepted `{attempt.get('accepted')}`, "
                f"failure `{','.join(attempt.get('failure_reasons') or []) or 'none'}`."
            )
        lines.append("")
    outcome = report.get("outcome", {})
    lines.extend(
        [
            "## Outcome",
            "",
            f"- CDX control available: `{outcome.get('cdx_available')}`; replay body available: `{outcome.get('replay_available')}`.",
            f"- Current download availability: `{outcome.get('current_download_availability')}`.",
            f"- Follow-up inventory/plan targets executed: `{report['follow_up']['executed']}` ({report['follow_up']['reason']}).",
            "- Raw response headers remain local under `raw/`; this summary contains no raw header text.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def run(output: Path, *, resume_after_robots: bool = False) -> int:
    started_utc = utc_now()
    raw_dir, output_paths = prepare_output(output, resume_after_robots=resume_after_robots)
    if not CURL.is_file():
        raise ProbeError(f"curl executable missing: {CURL}")
    drive_free = int(shutil.disk_usage(REPO_ROOT).free)
    preflight = {
        "drive_free_bytes": drive_free,
        "min_free_bytes": MIN_FREE_BYTES,
        "raw_body_budget": RAW_BODY_BUDGET,
        "passed": drive_free - RAW_BODY_BUDGET >= MIN_FREE_BYTES,
        "output": str(output.resolve()),
    }
    if not preflight["passed"]:
        raise ProbeError(f"D: free-space floor failed: {preflight}")
    state = RunState(time.monotonic(), time.monotonic() + NETWORK_WINDOW_SECONDS)
    endpoints: dict[str, Any] = {}
    print("STAGE archive.org robots control", flush=True)
    if resume_after_robots:
        state.attempts = 1
        existing = load_existing_failed_attempt("archive_robots", ROBOTS_URL, raw_dir)
        existing = validate_attempt(existing, "archive_robots", raw_dir / "archive_robots.direct.body")
        endpoints["archive_robots"] = probe_endpoint("archive_robots", ROBOTS_URL, state, raw_dir, direct_attempt=existing)
    else:
        endpoints["archive_robots"] = probe_endpoint("archive_robots", ROBOTS_URL, state, raw_dir)
    print(json.dumps({"stage": "archive_robots", "accepted": endpoints["archive_robots"]["accepted"], "attempts": len(endpoints["archive_robots"]["attempts"])}, ensure_ascii=False), flush=True)
    print("STAGE Wayback CDX exact control", flush=True)
    endpoints["cdx"] = probe_endpoint("cdx", CDX_URL, state, raw_dir)
    print(json.dumps({"stage": "cdx", "accepted": endpoints["cdx"]["accepted"], "attempts": len(endpoints["cdx"]["attempts"])}, ensure_ascii=False), flush=True)
    print("STAGE Wayback known JPEG replay control", flush=True)
    endpoints["replay"] = probe_endpoint("replay", REPLAY_URL, state, raw_dir)
    print(json.dumps({"stage": "replay", "accepted": endpoints["replay"]["accepted"], "attempts": len(endpoints["replay"]["attempts"])}, ensure_ascii=False), flush=True)
    cdx_validation = [a.get("validation", {}) for a in endpoints["cdx"].get("attempts", []) if a.get("accepted")]
    replay_validation = [a.get("validation", {}) for a in endpoints["replay"].get("attempts", []) if a.get("accepted")]
    finished_utc = utc_now()
    report: dict[str, Any] = {
        "schema": "wow-encyclopedia-wayback-accessibility-probe/v1",
        "probe": "screenshot-accessibility-20261014/probe001",
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "network_window_seconds": NETWORK_WINDOW_SECONDS,
        "max_http_attempts": MAX_HTTP_ATTEMPTS,
        "http_attempts": state.attempts,
        "raw_body_budget": RAW_BODY_BUDGET,
        "raw_body_bytes": state.raw_body_bytes,
        "single_body_limit": SINGLE_BODY_LIMIT,
        "preflight": preflight,
        "proxy": PROXY,
        "policy": {
            "direct": "curl --noproxy '*' first",
            "fallback": "only after ordinary direct failure, curl --proxy existing-local --noproxy ''",
            "tls_validation": "curl default TLS verification; no --insecure",
            "retry": "curl --retry 0; one direct and at most one proxy attempt per control",
            "rate_limit": "HTTP 429/503 stops that endpoint; proxy rate limits are not attributed to Archive without source evidence",
        },
        "endpoints": endpoints,
        "cdx_control": cdx_validation[-1] if cdx_validation else None,
        "replay_control": replay_validation[-1] if replay_validation else None,
        "outcome": {
            "cdx_available": bool(endpoints["cdx"]["accepted"]),
            "replay_available": bool(endpoints["replay"]["accepted"]),
            "current_download_availability": "known_replay_valid" if endpoints["replay"]["accepted"] else "known_replay_unavailable",
        },
        "follow_up": {
            "executed": False,
            "reason": "inventory/plan.json target list was not supplied; controls only",
        },
        "output": output_paths,
        "resume_after_local_runner_error": resume_after_robots,
    }
    safe_json_write(output / REPORT_NAME, report)
    safe_text_write(output / SUMMARY_NAME, build_markdown(report))
    print(json.dumps({"completed": True, "http_attempts": state.attempts, "outcome": report["outcome"], "report": output_paths["report"]}, ensure_ascii=False), flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--resume-after-robots", action="store_true", help="reuse the already-issued robots direct raw attempt")
    args = parser.parse_args(argv)
    try:
        return run(args.output_root.resolve(), resume_after_robots=args.resume_after_robots)
    except Exception as exc:
        print(f"wayback_control_probe: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

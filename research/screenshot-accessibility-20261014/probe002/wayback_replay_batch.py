"""Bounded four-item Wayback replay probe driven entirely by probe002-plan.json."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

try:
    from PIL import Image
except Exception:  # pragma: no cover - recorded as an evidence limitation
    Image = None


REPO_ROOT = Path(__file__).resolve().parents[3]
PROBE_ROOT = Path(__file__).resolve().parent
PLAN_PATH = REPO_ROOT / "research" / "screenshot-accessibility-20261014" / "probe002-plan.json"
RAW_ROOT = PROBE_ROOT / "raw"
REPORT_PATH = PROBE_ROOT / "sanitized-report.json"
SUMMARY_PATH = PROBE_ROOT / "sanitized-summary.md"
CURL = Path(r"C:\Windows\System32\curl.exe")
PROXY = "http://127.0.0.1:7890"
MAX_HTTP_ATTEMPTS = 8
NETWORK_WINDOW_SECONDS = 180
DIRECT_CONNECT_SECONDS = 8
DIRECT_TOTAL_SECONDS = 12
PROXY_TOTAL_SECONDS = 18
RAW_BODY_BUDGET = 32 * 1024 * 1024
SINGLE_BODY_LIMIT = 8 * 1024 * 1024
MIN_FREE_BYTES = 10 * 1024**3 + 256 * 1024**2
WRITE_OUT_FIELDS = "\t".join(
    (
        "%{http_code}",
        "%{url_effective}",
        "%{content_type}",
        "%{size_download}",
        "%{time_total}",
        "%{time_connect}",
        "%{time_appconnect}",
        "%{remote_ip}",
        "%{http_version}",
        "%{ssl_verify_result}",
    )
) + "\n"


class ProbeError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha1_base32(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def relative(path: Path) -> str:
    return path.resolve().relative_to(PROBE_ROOT.resolve()).as_posix()


def parse_float(value: str | None) -> float | None:
    try:
        return round(float(value), 6) if value else None
    except (TypeError, ValueError):
        return None


def parse_write_out(stdout: bytes) -> dict[str, Any]:
    fields = stdout.decode("utf-8", errors="replace").strip().split("\t")
    names = (
        "status",
        "final_url",
        "content_type_writeout",
        "size_download",
        "time_total",
        "time_connect",
        "time_appconnect",
        "remote_ip",
        "http_version",
        "ssl_verify_result",
    )
    result: dict[str, Any] = {name: (fields[index] if index < len(fields) else None) for index, name in enumerate(names)}
    if isinstance(result.get("status"), str) and result["status"].isdigit():
        result["status"] = int(result["status"])
    for name in ("time_total", "time_connect", "time_appconnect"):
        result[name] = parse_float(result.get(name))
    if isinstance(result.get("ssl_verify_result"), str) and result["ssl_verify_result"].isdigit():
        result["ssl_verify_result"] = int(result["ssl_verify_result"])
    return result


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


def normalize_timestamp(value: str | None, final_url: str) -> tuple[str | None, str | None]:
    if value:
        try:
            return parsedate_to_datetime(value).astimezone(timezone.utc).strftime("%Y%m%d%H%M%S"), "header"
        except (TypeError, ValueError, OverflowError):
            pass
    # The capture timestamp in the requested/final URL is only a lookup hint.
    # Without Memento-Datetime there is no observed capture date to report.
    return None, None


def pillow_validation(body: bytes) -> dict[str, Any]:
    if Image is None:
        return {"valid": False, "error": "pillow_unavailable"}
    try:
        with Image.open(io.BytesIO(body)) as image:
            image.verify()
        with Image.open(io.BytesIO(body)) as image:
            image.load()
            return {"valid": True, "format": image.format, "width": image.width, "height": image.height, "mode": image.mode}
    except Exception as exc:  # pragma: no cover - evidence records decoder errors
        return {"valid": False, "error": f"{type(exc).__name__}:{exc}"}


def load_plan() -> tuple[dict[str, Any], str]:
    if not PLAN_PATH.is_file():
        raise ProbeError(f"plan missing: {PLAN_PATH}")
    plan_bytes = PLAN_PATH.read_bytes()
    plan = json.loads(plan_bytes.decode("utf-8"))
    if plan.get("max_http_attempts") != MAX_HTTP_ATTEMPTS or plan.get("network_window_seconds") != NETWORK_WINDOW_SECONDS:
        raise ProbeError("plan budget does not match probe002 contract")
    items = plan.get("items")
    if not isinstance(items, list) or len(items) != 4:
        raise ProbeError("plan must contain exactly four items")
    required = {"id", "category", "original", "timestamp", "known_good", "local_source"}
    for item in items:
        if not required.issubset(item):
            raise ProbeError(f"plan item missing fields: {item!r}")
        if not re.fullmatch(r"\d{14}", str(item["timestamp"])):
            raise ProbeError(f"invalid capture timestamp: {item!r}")
    return plan, sha256_bytes(plan_bytes)


def precompute_local_expectations(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    expected: dict[str, dict[str, Any]] = {}
    for item in plan["items"]:
        item_id = str(item["id"])
        local = item.get("local_source")
        if not item.get("known_good"):
            expected[item_id] = {}
            continue
        if not isinstance(local, str) or not local:
            raise ProbeError(f"known_good item has no local source: {item_id}")
        source = REPO_ROOT / Path(local)
        if not source.is_file():
            raise ProbeError(f"known_good local source missing: {source}")
        data = source.read_bytes()
        expected[item_id] = {
            "local_source": local,
            "local_source_resolved": str(source.resolve()),
            "local_length": len(data),
            "local_sha256": sha256_bytes(data),
            "local_sha1_base32": sha1_base32(data),
        }
    return expected


def classify_attempt(item: dict[str, Any], record: dict[str, Any], body: bytes, local_expectation: dict[str, Any]) -> dict[str, Any]:
    status = record.get("status")
    mime = (record.get("content_type") or "").split(";", 1)[0].strip().casefold()
    image = pillow_validation(body) if body.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF8")) else {"valid": False, "error": "not_an_image_signature"}
    memento_timestamp, timestamp_source = normalize_timestamp(record.get("memento_datetime"), str(record.get("final_url") or ""))
    observed = {
        "mime": mime,
        "image_signature": "jpeg" if body.startswith(b"\xff\xd8\xff") else ("png" if body.startswith(b"\x89PNG\r\n\x1a\n") else None),
        "pillow": image,
        "length": len(body),
        "sha256": sha256_bytes(body),
        "sha1_base32": sha1_base32(body) if body else None,
        "memento_datetime_observed": record.get("memento_datetime"),
        "memento_timestamp": memento_timestamp,
        "memento_timestamp_source": timestamp_source,
        "actual_capture_timestamp": memento_timestamp,
        "requested_url_timestamp_hint": str(item["timestamp"]),
    }
    known_good = bool(item.get("known_good"))
    if known_good:
        expected_length = item.get("expected_length")
        expected_sha256 = item.get("expected_sha256")
        observed.update(
            {
                "expected_length": expected_length,
                "expected_sha256": expected_sha256,
                "expected_sha1_base32": local_expectation.get("local_sha1_base32"),
                "length_match": len(body) == expected_length,
                "sha256_match": sha256_bytes(body) == expected_sha256,
                "sha1_match": bool(body) and sha1_base32(body) == local_expectation.get("local_sha1_base32"),
                "memento_timestamp_match": memento_timestamp == item.get("timestamp"),
            }
        )
        restored = (
            status == 200
            and mime == "image/jpeg"
            and observed["image_signature"] == "jpeg"
            and image.get("valid") is True
            and observed["length_match"]
            and observed["sha256_match"]
            and observed["sha1_match"]
            and observed["memento_timestamp_match"]
        )
        observed["classification"] = "known_good_retrieved" if restored else ("http_404" if status == 404 else "invalid_known_good_response")
        observed["known_good_retrieved"] = restored
        observed["image_retrieved"] = restored
        observed["new_unique_resources"] = 0
        observed["restored"] = restored
        return observed

    if status == 404:
        observed["classification"] = "expected_missing_404"
        observed["interpretation"] = "current replay returned HTTP 404/page indicating this requested capture is unavailable; this does not establish that all dates or all gallery images are absent"
    elif status == 200 and observed["image_signature"] == "jpeg" and image.get("valid") is True:
        observed["classification"] = "reachable_candidate"
    elif status == 200:
        observed["classification"] = "error_html_200" if "html" in mime or not observed["image_signature"] else "non_jpeg_200"
    elif status is None or status == 0:
        observed["classification"] = "transport_unavailable"
    else:
        observed["classification"] = f"http_{status}"
    observed["new_unique_resources"] = 0
    observed["restored"] = False
    return observed


def run_attempt(item: dict[str, Any], transport: str, state: dict[str, Any], raw_dir: Path, local_expectation: dict[str, Any]) -> dict[str, Any]:
    if state["attempts"] >= MAX_HTTP_ATTEMPTS:
        raise ProbeError("HTTP attempt cap reached")
    remaining = state["deadline"] - time.monotonic()
    if remaining <= 0:
        raise ProbeError("network deadline reached")
    state["attempts"] += 1
    item_id = str(item["id"])
    original = str(item["original"])
    timestamp = str(item["timestamp"])
    url = f"https://web.archive.org/web/{timestamp}id_/{original}"
    stem = f"{item_id}.{transport}"
    body_path, headers_path, stderr_path = (raw_dir / f"{stem}.{suffix}" for suffix in ("body", "headers.txt", "stderr.txt"))
    for path in (body_path, headers_path, stderr_path):
        if path.exists() or os.path.lexists(path):
            raise ProbeError(f"refusing to overwrite raw evidence: {path}")
    max_time = min(DIRECT_TOTAL_SECONDS if transport == "direct" else PROXY_TOTAL_SECONDS, max(1, int(remaining)))
    command = [str(CURL), "-q"]
    command.extend(["--noproxy", "*"] if transport == "direct" else ["--proxy", PROXY, "--noproxy", ""])
    command.extend(
        [
            "--http1.1",
            "--retry",
            "0",
            "--connect-timeout",
            str(min(DIRECT_CONNECT_SECONDS, max_time)),
            "--max-time",
            str(max_time),
            "--max-filesize",
            str(min(SINGLE_BODY_LIMIT, max(0, RAW_BODY_BUDGET - state["raw_body_bytes"]))),
            "--location",
            "--silent",
            "--show-error",
            "--dump-header",
            str(headers_path.resolve()),
            "--output",
            str(body_path.resolve()),
            "--write-out",
            WRITE_OUT_FIELDS,
            url,
        ]
    )
    started = time.monotonic()
    process_timeout = False
    exit_code: int | None = None
    stdout = b""
    stderr = b""
    try:
        result = subprocess.run(command, capture_output=True, timeout=max(0.1, min(float(max_time), remaining)), check=False)
        exit_code, stdout, stderr = result.returncode, result.stdout or b"", result.stderr or b""
    except subprocess.TimeoutExpired as exc:
        process_timeout = True
        stdout, stderr = exc.stdout or b"", exc.stderr or b""
    stderr_path.write_bytes(stderr)
    if not body_path.exists():
        body_path.write_bytes(b"")
    body = body_path.read_bytes()
    truncated = False
    if len(body) > SINGLE_BODY_LIMIT:
        body = body[:SINGLE_BODY_LIMIT]
        body_path.write_bytes(body)
        truncated = True
    state["raw_body_bytes"] += len(body)
    if state["raw_body_bytes"] > RAW_BODY_BUDGET:
        raise ProbeError("raw body budget exceeded")
    writeout = parse_write_out(stdout)
    headers, header_status, header_blocks = parse_headers(headers_path)
    status = writeout.get("status") if isinstance(writeout.get("status"), int) else header_status
    if process_timeout and header_status is None:
        status = None
    final_url = writeout.get("final_url") or url
    record: dict[str, Any] = {
        "item_id": item_id,
        "transport": transport,
        "requested_url": url,
        "original": original,
        "requested_capture_timestamp": timestamp,
        "status": status,
        "curl_exit_code": exit_code,
        "final_url": final_url,
        "wire_bytes": len(body),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "remote_ip": writeout.get("remote_ip"),
        "http_version": writeout.get("http_version"),
        "ssl_verify_result": writeout.get("ssl_verify_result"),
        "time_connect": writeout.get("time_connect"),
        "time_appconnect": writeout.get("time_appconnect"),
        "time_total": writeout.get("time_total"),
        "content_type": header(headers, "Content-Type") or writeout.get("content_type_writeout"),
        "content_length": header(headers, "Content-Length"),
        "retry_after": header(headers, "Retry-After"),
        "memento_datetime": header(headers, "Memento-Datetime"),
        "header_status": header_status,
        "header_block_count": header_blocks,
        "body_sha256": sha256_bytes(body),
        "raw_body": relative(body_path),
        "raw_headers": relative(headers_path),
        "raw_stderr": relative(stderr_path),
        "process_timeout": process_timeout,
        "truncated_to_budget": truncated,
        "failure_reasons": [],
        "raw_body_bytes": len(body),
    }
    if process_timeout:
        record["failure_reasons"].append("process_timeout")
    if exit_code not in (0, None):
        record["failure_reasons"].append(f"curl_exit_{exit_code}")
    if status in (429, 503):
        record["failure_reasons"].append(f"http_{status}_stop_batch")
    if truncated:
        record["failure_reasons"].append("single_body_limit_exceeded")
    record["validation"] = classify_attempt(item, record, body, local_expectation)
    record["accepted"] = bool(record["validation"].get("restored"))
    if not record["accepted"] and not (status in (429, 503)):
        record["failure_reasons"].append("validation_failed")
    record["failure_class"] = "rate_limited" if status in (429, 503) else ("transport" if status in (None, 0) else (None if record["accepted"] else "content_or_http"))
    return record


def build_summary(report: dict[str, Any]) -> str:
    lines = [
        "# Wayback replay probe002",
        "",
        f"- HTTP attempts: `{report['http_attempts']}/{report['max_http_attempts']}`; network window `{report['network_window_seconds']}s`.",
        f"- Raw body bytes: `{report['raw_body_bytes']}/{report['raw_body_budget']}`; D preflight `{report['preflight']['passed']}` with `{report['preflight']['drive_free_bytes']}` free bytes.",
        f"- Batch stop: `{report['batch_stop_reason'] or 'none'}`.",
        f"- Known-good items retrieved: `{report.get('known_good_retrieved', 0)}`; new unique resources: `{report.get('new_unique_resources', 0)}`.",
        "",
        "## Items",
        "",
    ]
    for item in report["items"]:
        lines.append(f"### `{item['id']}` — {item['category']}")
        lines.append("")
        lines.append(f"- Original: `{item['original']}`; requested capture: `{item['timestamp']}`; known good: `{item['known_good']}`.")
        lines.append(f"- Outcome: `{item['outcome']['classification']}`; image retrieved: `{item['outcome'].get('image_retrieved', False)}`; new unique resources: `{item.get('new_unique_resources', 0)}`; actual capture: `{item['outcome'].get('actual_capture_timestamp')}`; URL timestamp hint: `{item['outcome'].get('requested_url_timestamp_hint')}`.")
        if item['outcome']['classification'] == 'expected_missing_404':
            lines.append("- Interpretation: current replay 404/page indication for this requested capture only; it does not establish that all dates or all gallery images are absent.")
        for attempt in item["attempts"]:
            lines.append(f"- `{attempt['transport']}` status `{attempt['status']}`, bytes `{attempt['wire_bytes']}`, elapsed `{attempt['elapsed_seconds']}`, class `{attempt['failure_class']}`, failures `{','.join(attempt['failure_reasons']) or 'none'}`.")
        lines.append("")
    lines.extend(
        [
            "## Scope",
            "",
            "- Only the four plan targets were attempted; no CDX or Availability request was repeated.",
            "- Unknown targets are recorded as candidates or missing/error responses and are not integrated.",
            "- Raw response headers and bodies remain local under `raw/`; this summary contains no raw header text.",
            "",
        ]
    )
    return "\n".join(lines)


def run() -> int:
    if REPORT_PATH.exists() or SUMMARY_PATH.exists():
        raise ProbeError("refusing to overwrite existing sanitized outputs")
    plan, plan_sha256 = load_plan()
    local_expectations = precompute_local_expectations(plan)
    if not CURL.is_file():
        raise ProbeError(f"curl missing: {CURL}")
    free = int(shutil.disk_usage(REPO_ROOT).free)
    preflight = {
        "drive_free_bytes": free,
        "min_free_bytes": MIN_FREE_BYTES,
        "raw_body_budget": RAW_BODY_BUDGET,
        "passed": free - RAW_BODY_BUDGET >= MIN_FREE_BYTES,
        "output": str(PROBE_ROOT.resolve()),
    }
    if not preflight["passed"]:
        raise ProbeError(f"D free-space floor failed: {preflight}")
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    state = {"started_monotonic": time.monotonic(), "deadline": time.monotonic() + NETWORK_WINDOW_SECONDS, "attempts": 0, "raw_body_bytes": 0}
    item_reports: list[dict[str, Any]] = []
    batch_stop_reason: str | None = None
    for item in plan["items"]:
        if batch_stop_reason:
            break
        item_id = str(item["id"])
        attempts: list[dict[str, Any]] = []
        direct = run_attempt(item, "direct", state, RAW_ROOT, local_expectations.get(item_id, {}))
        attempts.append(direct)
        if direct["status"] in (429, 503):
            batch_stop_reason = f"{item_id}: direct HTTP {direct['status']} stops entire replay batch"
        elif direct["accepted"] or direct["validation"].get("classification") in {"expected_missing_404", "reachable_candidate", "error_html_200", "non_jpeg_200"}:
            pass
        else:
            if state["attempts"] >= MAX_HTTP_ATTEMPTS or time.monotonic() >= state["deadline"]:
                batch_stop_reason = f"{item_id}: budget/deadline before proxy fallback"
            else:
                proxy = run_attempt(item, "proxy", state, RAW_ROOT, local_expectations.get(item_id, {}))
                attempts.append(proxy)
                if proxy["status"] in (429, 503):
                    batch_stop_reason = f"{item_id}: proxy HTTP {proxy['status']} stops entire replay batch"
        selected = next((a for a in attempts if a["accepted"]), attempts[-1])
        outcome = selected["validation"].copy()
        outcome["restored"] = any(a["accepted"] for a in attempts)
        item_reports.append({
            "id": item_id,
            "category": item["category"],
            "original": item["original"],
            "timestamp": item["timestamp"],
            "known_good": bool(item["known_good"]),
            "local_source": item.get("local_source"),
            "local_expectation": local_expectations.get(item_id, {}),
            "attempts": attempts,
            "outcome": outcome,
            "new_unique_resources": 0,
        })
    finished = utc_now()
    report: dict[str, Any] = {
        "schema": "wow-encyclopedia-wayback-replay-probe/v1",
        "probe": "screenshot-accessibility-20261014/probe002",
        "started_utc": started,
        "finished_utc": finished,
        "network_window_seconds": NETWORK_WINDOW_SECONDS,
        "max_http_attempts": MAX_HTTP_ATTEMPTS,
        "http_attempts": state["attempts"],
        "raw_body_budget": RAW_BODY_BUDGET,
        "raw_body_bytes": state["raw_body_bytes"],
        "single_body_limit": SINGLE_BODY_LIMIT,
        "preflight": preflight,
        "plan": {"path": str(PLAN_PATH.resolve()), "sha256": plan_sha256, "anchor": plan.get("anchor")},
        "proxy": PROXY,
        "policy": {
            "direct": "curl -q --noproxy '*' first",
            "fallback": "proxy only after item direct validation/transport failure",
            "tls_validation": "curl default TLS verification; no --insecure",
            "retry": "curl --retry 0; at most one direct and one proxy attempt per item",
            "rate_limit": "HTTP 429/503 on either transport stops the entire replay batch",
        },
        "batch_stop_reason": batch_stop_reason,
        "items": item_reports,
        "new_unique_resources": 0,
        "known_good_retrieved": sum(1 for item in item_reports if item["outcome"].get("known_good_retrieved")),
        "unexecuted": ["remaining plan items after batch stop" ] if batch_stop_reason and len(item_reports) < len(plan["items"]) else [],
        "output": {"raw": "raw", "report": REPORT_PATH.name, "summary": SUMMARY_PATH.name},
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    SUMMARY_PATH.write_text(build_summary(report) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"completed": True, "http_attempts": state["attempts"], "batch_stop_reason": batch_stop_reason, "report": str(REPORT_PATH)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except Exception as exc:
        print(f"wayback_replay_batch: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

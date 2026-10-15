"""Bounded exact-CDX replay for the pre-2008 PvP flash-rewards page.

This run is intentionally isolated from the earlier TLS poll.  It makes at
most two source requests: direct first, then proxy only after a direct
transport failure.  Redirects are never followed.  Raw bodies are retained;
headers, traces and stderr remain local ignored evidence because they may
contain cookies.  The JSON summary contains only redacted request metadata.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
INPUT_SUMMARY = OUT.parent / "summary.json"
CURL = r"C:\Windows\System32\curl.exe"
PROXY = "http://127.0.0.1:7890"
TIMESTAMP = "20070115223911"
ORIGINAL = "http://www.worldofwarcraft.com:80/pvp/flash-rewards/"
LOGICAL_URL = "http://www.worldofwarcraft.com/pvp/flash-rewards/"
REPLAY_URL = f"https://web.archive.org/web/{TIMESTAMP}id_/{quote(ORIGINAL, safe=":/?&=%;,+$'@~") }"
MAX_SOURCE_REQUESTS = 2
MAX_BODY_BYTES = 2 * 1024 * 1024
MAX_TOTAL_SECONDS = 120
DIRECT_CONNECT_SECONDS = 4
DIRECT_TOTAL_SECONDS = 6
PROXY_CONNECT_SECONDS = 15
PROXY_TOTAL_SECONDS = 15
USER_AGENT = "WOW-Encyclopedia/pvp-pre2008-control-replay-20261015"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cdx_digest(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_cdx_row() -> dict[str, str]:
    data = json.loads(INPUT_SUMMARY.read_text(encoding="utf-8"))
    for request in data.get("requests", []):
        table = request.get("table") if isinstance(request, dict) else None
        if not isinstance(table, list) or not table:
            continue
        for row in table[1:]:
            if not isinstance(row, list) or len(row) < 6:
                continue
            values = [str(value) for value in row[:6]]
            if values[0] == TIMESTAMP and values[1] == ORIGINAL:
                result = dict(zip(("timestamp", "original", "statuscode", "mimetype", "digest", "length"), values))
                if result["statuscode"] != "200":
                    raise ValueError("exact CDX row is not status 200")
                return result
    raise ValueError(f"exact CDX row not found for {TIMESTAMP} {ORIGINAL}")


def parse_header_blocks(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^HTTP/(\d(?:\.\d)?)\s+(\d{3})(?:\s+(.*))?$", stripped, re.I)
        if match:
            reason = match.group(3) or ""
            current = {
                "http_version": match.group(1),
                "status": int(match.group(2)),
                "reason": reason,
                "headers": {},
                "is_connect": "connection established" in reason.casefold(),
            }
            blocks.append(current)
            continue
        if current is not None and ":" in line:
            key, value = line.split(":", 1)
            current["headers"][key.strip().casefold()] = value.strip()
    return blocks


def source_block(blocks: list[dict[str, Any]]) -> dict[str, Any] | None:
    sources = [block for block in blocks if not block.get("is_connect")]
    return sources[-1] if sources else None


def header(block: dict[str, Any] | None, name: str) -> str | None:
    if not block:
        return None
    return block.get("headers", {}).get(name.casefold())


def normalize_memento(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
    except (TypeError, ValueError, OverflowError):
        return None


def parse_metrics(text: str) -> dict[str, Any]:
    keys = [
        "http_code",
        "time_namelookup",
        "time_connect",
        "time_appconnect",
        "time_pretransfer",
        "time_starttransfer",
        "time_total",
        "remote_ip",
        "http_version",
    ]
    values = text.strip().split("\t")
    result: dict[str, Any] = {}
    for key, value in zip(keys, values):
        if key in {"http_code", "remote_ip", "http_version"}:
            result[key] = value
            continue
        try:
            result[key] = float(value)
        except ValueError:
            result[key] = None
    return result


def phase_record(
    *,
    transport: str,
    blocks: list[dict[str, Any]],
    metrics: dict[str, Any],
    error: str | None,
    exit_code: int | None,
) -> dict[str, Any]:
    source = source_block(blocks)
    source_status = source.get("status") if source else None
    connect_blocks = [block for block in blocks if block.get("is_connect")]
    connect = connect_blocks[-1].get("status") if connect_blocks else None
    error_text = (error or "").casefold()
    if source_status is not None:
        outcome = "source_http"
    elif any(marker in error_text for marker in ("ssl", "tls", "handshake", "schannel", "certificate", "eof")):
        outcome = "tls_failed"
    elif any(marker in error_text for marker in ("timed out", "timeout", "failed to connect", "couldn't connect", "connection refused")):
        outcome = "tcp_or_timeout_failed"
    elif error_text or exit_code not in (0, None):
        outcome = "transport_failed"
    else:
        outcome = "no_source_status"
    return {
        "outcome": outcome,
        "dns": {"completed": bool(metrics.get("time_namelookup")), "seconds": metrics.get("time_namelookup")},
        "tcp": {"completed": bool(metrics.get("time_connect")), "seconds": metrics.get("time_connect")},
        "connect": {"status": connect, "completed": connect is not None} if transport == "proxy" else {"status": None, "completed": None},
        "tls": {"completed": bool(metrics.get("time_appconnect")), "seconds": metrics.get("time_appconnect")},
        "http": {"source_status": source_status, "memento_datetime": header(source, "memento-datetime")},
    }


def title_from_html(body: bytes) -> str | None:
    text = body.decode("utf-8", errors="replace")
    match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", text, re.I | re.S)
    if not match:
        return None
    cleaned = re.sub(r"<[^>]+>", " ", match.group(1))
    return re.sub(r"\s+", " ", html.unescape(cleaned)).strip() or None


def validate_content(body: bytes, source: dict[str, Any] | None, expected: dict[str, str]) -> dict[str, Any]:
    mime = (header(source, "content-type") or "").split(";", 1)[0].strip().casefold()
    text = body.decode("utf-8", errors="replace")
    lowered = text.casefold()
    title = title_from_html(body)
    title_lower = (title or "").casefold()
    soft404_markers = (
        "world of warcraft - 404 file not found",
        "404 file not found",
        "the requested url was not found",
        "wayback machine error",
        "no archived snapshot",
        "page cannot be displayed",
        "memento not found",
        "got an http 404 response",
    )
    soft404_marker = next((marker for marker in soft404_markers if marker in lowered or marker in title_lower), None)
    if soft404_marker is None and re.search(r"\b(?:404|file\s+not\s+found|page\s+not\s+found)\b", title_lower):
        soft404_marker = "error_title"
    pvp_markers = tuple(marker for marker in ("pvp", "player vs. player", "player versus player", "honor", "arena", "battleground") if marker in lowered)
    target_markers = tuple(marker for marker in ("flash", "reward", "rewards") if marker in lowered)
    html_shape = bool(re.search(r"<(?:html|body|head|title)\b", lowered))
    if soft404_marker:
        content_class = "error_page"
        valid = False
    elif mime in {"text/html", "application/xhtml+xml"} and html_shape and pvp_markers and target_markers:
        content_class = "pvp_html_page"
        valid = True
    else:
        content_class = "non_pvp_or_unclassified"
        valid = False
    return {
        "valid": valid,
        "content_class": content_class,
        "mime": mime,
        "title": title,
        "html_shape": html_shape,
        "pvp_markers": list(pvp_markers),
        "target_markers": list(target_markers),
        "soft404_marker": soft404_marker,
    }


def run_curl(*, transport: str, request_id: str, connect_timeout: int, total_timeout: int) -> dict[str, Any]:
    stem = f"{transport}"
    headers_path = RAW / f"{stem}.headers.txt"
    body_path = RAW / f"{stem}.body"
    stderr_path = RAW / f"{stem}.stderr.txt"
    trace_path = RAW / f"{stem}.trace.txt"
    metrics_path = RAW / f"{stem}.metrics.txt"
    command = [
        CURL,
        "--proxy", PROXY if transport == "proxy" else "",
        "--noproxy", "" if transport == "proxy" else "*",
        "--connect-timeout", str(connect_timeout),
        "--max-time", str(total_timeout),
        "--max-redirs", "0",
        "--max-filesize", str(MAX_BODY_BYTES),
        "--silent", "--show-error",
        "--trace-time", "--trace-ascii", str(trace_path),
        "--dump-header", str(headers_path),
        "--output", str(body_path),
        "--write-out", "%{http_code}\t%{time_namelookup}\t%{time_connect}\t%{time_appconnect}\t%{time_pretransfer}\t%{time_starttransfer}\t%{time_total}\t%{remote_ip}\t%{http_version}",
        "--user-agent", USER_AGENT,
        REPLAY_URL,
    ]
    started = time.perf_counter()
    exit_code: int | None = None
    stdout = ""
    try:
        with stderr_path.open("wb") as stderr_file:
            result = subprocess.run(
                command,
                cwd=OUT,
                stdout=subprocess.PIPE,
                stderr=stderr_file,
                timeout=total_timeout + 3,
                check=False,
            )
        exit_code = result.returncode
        stdout = result.stdout.decode("ascii", "replace")
    except Exception as exc:  # pragma: no cover - process failure is evidence
        stdout = ""
        stderr_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
    metrics_path.write_text(stdout, encoding="utf-8")
    headers_text = headers_path.read_text(encoding="iso-8859-1", errors="replace") if headers_path.exists() else ""
    body = body_path.read_bytes() if body_path.exists() else b""
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
    blocks = parse_header_blocks(headers_text)
    source = source_block(blocks)
    metrics = parse_metrics(stdout)
    phase = phase_record(transport=transport, blocks=blocks, metrics=metrics, error=stderr, exit_code=exit_code)
    source_status = source.get("status") if source else None
    memento_raw = header(source, "memento-datetime")
    actual_timestamp = normalize_memento(memento_raw)
    content = validate_content(body, source, expected={}) if source_status == 200 else {
        "valid": False,
        "content_class": "no_source_200",
        "mime": (header(source, "content-type") or "").split(";", 1)[0].strip().casefold(),
        "title": None,
        "html_shape": False,
        "pvp_markers": [],
        "target_markers": [],
        "soft404_marker": None,
    }
    result = {
        "request_id": request_id,
        "transport": transport,
        "url": REPLAY_URL,
        "started_utc": utc_now(),
        "duration_ms": round((time.perf_counter() - started) * 1000, 1),
        "curl_exit": exit_code,
        "curl_error": stderr[-2000:] if stderr else None,
        "metrics": metrics,
        "phase": phase,
        "connect_status": next((block["status"] for block in blocks if block.get("is_connect")), None),
        "source_status": source_status,
        "memento_datetime": memento_raw,
        "actual_timestamp": actual_timestamp,
        "redirects_requested": 0,
        "automatic_redirects": 0,
        "location": header(source, "location"),
        "body_bytes": len(body),
        "body_sha256": sha256(body) if body else None,
        "cdx_digest_observed": cdx_digest(body) if body else None,
        "content": content,
        "raw": {
            "headers": str(headers_path.relative_to(OUT)),
            "body": str(body_path.relative_to(OUT)),
            "stderr": str(stderr_path.relative_to(OUT)),
            "trace": str(trace_path.relative_to(OUT)),
            "metrics": str(metrics_path.relative_to(OUT)),
        },
        "header_block_count": len(blocks),
        "header_connect_block_count": sum(1 for block in blocks if block.get("is_connect")),
    }
    return result


def assess(requests: list[dict[str, Any]], expected: dict[str, str]) -> dict[str, Any]:
    selected = next((item for item in reversed(requests) if item.get("source_status") is not None or item.get("body_bytes")), requests[-1] if requests else {})
    observed_digest = selected.get("cdx_digest_observed")
    content = selected.get("content") or {}
    checks = {
        "real_http_200": selected.get("source_status") == 200,
        "memento_present": selected.get("actual_timestamp") is not None,
        "memento_matches_requested": selected.get("actual_timestamp") == TIMESTAMP,
        "cdx_digest_matches": observed_digest == expected.get("digest"),
        "body_length_matches_cdx": selected.get("body_bytes") == int(expected.get("length") or 0),
        "mime_is_html": content.get("mime") in {"text/html", "application/xhtml+xml"},
        "real_pvp_page": content.get("valid") is True and content.get("content_class") == "pvp_html_page",
        "not_soft404": not bool(content.get("soft404_marker")),
        "no_automatic_redirect": selected.get("automatic_redirects") == 0,
    }
    required_checks = [
        "real_http_200",
        "memento_present",
        "memento_matches_requested",
        "cdx_digest_matches",
        "mime_is_html",
        "real_pvp_page",
        "not_soft404",
        "no_automatic_redirect",
    ]
    return {
        "selected_request": selected.get("request_id"),
        "selected_transport": selected.get("transport"),
        "checks": checks,
        "required_checks": required_checks,
        "informational_checks": ["body_length_matches_cdx"],
        "ready": all(checks[name] for name in required_checks),
        "observed": {
            "source_status": selected.get("source_status"),
            "actual_timestamp": selected.get("actual_timestamp"),
            "memento_datetime": selected.get("memento_datetime"),
            "body_bytes": selected.get("body_bytes"),
            "body_sha256": selected.get("body_sha256"),
            "cdx_digest_observed": observed_digest,
            "content": content,
        },
    }


def build_files_map(selected: dict[str, Any], expected: dict[str, str]) -> dict[str, Any]:
    body_path = str((OUT / str(selected["raw"]["body"])).resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    content = selected.get("content") or {}
    return {
        "schema_version": 1,
        "kind": "pvp_pre2008_exact_cdx_files_map",
        "status": "validated_source_entities_only",
        "generated_utc": utc_now(),
        "network_performed": True,
        "files": [
            {
                "logical_url": LOGICAL_URL,
                "original": ORIGINAL,
                "source_url": ORIGINAL,
                "source_base_url": LOGICAL_URL,
                "local_path": body_path,
                "mime": selected["content"].get("mime") or "text/html",
                "response_content_type": selected["content"].get("mime") or "text/html",
                "kind": "html",
                "role": "pvp_pre2008_exact_cdx_replay",
                "sha256": selected["body_sha256"],
                "content_length": selected["body_bytes"],
                "length": selected["body_bytes"],
                "actual_timestamp": selected["actual_timestamp"],
                "entity_observed_capture_timestamp": selected["actual_timestamp"],
                "indexed_capture_timestamp": TIMESTAMP,
                "requested_timestamp": TIMESTAMP,
                "memento_datetime": selected["memento_datetime"],
                "actual_url": selected["url"],
                "requested_url": selected["url"],
                "http_status": selected["source_status"],
                "content_valid": True,
                "content_class": content.get("content_class"),
                "title": content.get("title"),
                "temporal_class": "pre_2008",
                "cdx_digest": expected["digest"],
                "cdx_length": expected["length"],
                "supplement_note": "Exact pre-2008 CDX replay; public PvP page bytes only, no dynamic expansion.",
            }
        ],
    }


def write_outputs(row: dict[str, str], requests: list[dict[str, Any]], *, stop_reason: str) -> dict[str, Any]:
    assessment = assess(requests, row)
    summary = {
        "schema_version": 1,
        "kind": "pvp_pre2008_exact_replay",
        "generated_utc": utc_now(),
        "network_performed": True,
        "target": {
            "logical_url": LOGICAL_URL,
            "original": ORIGINAL,
            "requested_timestamp": TIMESTAMP,
            "replay_url": REPLAY_URL,
        },
        "cdx": row,
        "transport_contract": {
            "direct_first": True,
            "proxy": PROXY,
            "direct_connect_timeout_seconds": DIRECT_CONNECT_SECONDS,
            "direct_total_timeout_seconds": DIRECT_TOTAL_SECONDS,
            "proxy_connect_timeout_seconds": PROXY_CONNECT_SECONDS,
            "proxy_total_timeout_seconds": PROXY_TOTAL_SECONDS,
            "tls_verification": "enabled",
            "automatic_redirects": 0,
        },
        "budgets": {
            "source_requests": len(requests),
            "max_source_requests": MAX_SOURCE_REQUESTS,
            "max_body_bytes": MAX_BODY_BYTES,
            "max_total_seconds": MAX_TOTAL_SECONDS,
        },
        "requests": requests,
        "source_request_count": len(requests),
        "stop_reason": stop_reason,
        "assessment": assessment,
        "files_map": "files-map.json" if assessment["ready"] else None,
        "redaction": "headers, cookies, traces and body snippets are omitted from this JSON; raw headers/traces are local ignored evidence",
    }
    write_json(OUT / "summary.json", summary)
    if assessment["ready"]:
        write_json(OUT / "files-map.json", build_files_map(next(item for item in reversed(requests) if item.get("request_id") == assessment["selected_request"]), row))
    lines = [
        "# PvP flash-rewards exact replay — 2026-10-15",
        "",
        f"Target: `{LOGICAL_URL}`; requested capture `{TIMESTAMP}`; original `{ORIGINAL}`.",
        f"Exact CDX row: HTTP `{row['statuscode']}`, MIME `{row['mimetype']}`, length `{row['length']}`, digest `{row['digest']}`.",
        f"Requests: `{len(requests)}/{MAX_SOURCE_REQUESTS}`; automatic redirects: `0`; stop: `{stop_reason}`.",
        f"Result: `{'ready' if assessment['ready'] else 'replay_invalid'}` via `{assessment.get('selected_transport')}`.",
        "",
    ]
    for request in requests:
        phase = request.get("phase", {})
        lines.append(
            f"- `{request['transport']}`: outcome `{phase.get('outcome')}`, CONNECT `{request.get('connect_status')}`, "
            f"source HTTP `{request.get('source_status')}`, TLS `{phase.get('tls', {}).get('seconds')}`, "
            f"body `{request.get('body_bytes')}` bytes, Memento `{request.get('actual_timestamp')}`, "
            f"CDX digest `{request.get('cdx_digest_observed')}`; raw body `{request['raw']['body']}`."
        )
    observed = assessment["observed"]
    content = observed.get("content") or {}
    lines.extend(
        [
            "",
            f"Content classification: `{content.get('content_class')}`; title `{content.get('title')}`; "
            f"PvP markers `{content.get('pvp_markers')}`; target markers `{content.get('target_markers')}`; "
            f"soft-404 marker `{content.get('soft404_marker')}`.",
            f"Checks: `{json.dumps(assessment['checks'], ensure_ascii=False, sort_keys=True)}`; "
            "CDX length is retained as metadata and is not used as the content gate when the exact CDX digest matches.",
            "",
            "Raw body is retained under `raw/`; headers, traces, stderr and metrics are local ignored evidence.",
        ]
    )
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def run_network() -> dict[str, Any]:
    started = time.perf_counter()
    row = read_cdx_row()
    RAW.mkdir(parents=True, exist_ok=True)
    requests: list[dict[str, Any]] = []
    direct = run_curl(transport="direct", request_id="target", connect_timeout=DIRECT_CONNECT_SECONDS, total_timeout=DIRECT_TOTAL_SECONDS)
    requests.append(direct)
    if direct.get("source_status") in {429, 503}:
        stop_reason = f"endpoint_status_{direct['source_status']}"
    elif direct.get("source_status") is None and direct.get("curl_exit") not in (0,) and time.perf_counter() - started < MAX_TOTAL_SECONDS:
        proxy = run_curl(transport="proxy", request_id="target", connect_timeout=PROXY_CONNECT_SECONDS, total_timeout=PROXY_TOTAL_SECONDS)
        requests.append(proxy)
        if proxy.get("source_status") in {429, 503}:
            stop_reason = f"endpoint_status_{proxy['source_status']}"
        elif proxy.get("source_status") is None and proxy.get("curl_exit") not in (0, None):
            stop_reason = "two_transport_failures"
        else:
            stop_reason = "completed"
    else:
        stop_reason = "completed"
    return write_outputs(row, requests, stop_reason=stop_reason)


def run_offline() -> dict[str, Any]:
    existing = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    return write_outputs(existing["cdx"], list(existing.get("requests") or []), stop_reason=str(existing.get("stop_reason") or "offline_reclassification"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="perform the bounded direct-then-proxy replay")
    parser.add_argument("--offline", action="store_true", help="reclassify saved raw/request evidence without networking")
    args = parser.parse_args()
    if args.offline:
        result = run_offline()
    elif args.run:
        result = run_network()
    else:
        parser.error("pass --run or --offline")
    print(json.dumps({"source_request_count": result["source_request_count"], "stop_reason": result["stop_reason"], "ready": result["assessment"]["ready"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

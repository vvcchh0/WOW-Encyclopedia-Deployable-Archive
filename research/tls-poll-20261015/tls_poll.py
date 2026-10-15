"""Bounded Wayback TLS availability poll for one known JPEG.

The first round is deliberately small: direct curl, then proxy curl when the
direct request fails.  A proxy TLS failure gets one urllib cross-check and one
archive.org robots comparison.  No request follows redirects, and CONNECT
responses are kept separate from the source HTTP response.

The script also contains a pure offline fixture mode.  Raw headers, bodies,
stderr, curl traces and metrics are local evidence and are ignored by Git;
summary.json and summary.md contain only redacted metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import socket
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except Exception:  # pragma: no cover - environment-dependent evidence
    Image = None


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
SUMMARY_JSON = ROOT / "summary.json"
SUMMARY_MD = ROOT / "summary.md"
CURL = r"C:\Windows\System32\curl.exe"
PROXY = "http://127.0.0.1:7890"
TARGET = (
    "https://web.archive.org/web/20080512212653id_/"
    "http://www.worldofwarcraft.com/info/dungeons/images/karazhan/thumbs/ss2-thumb.jpg"
)
ROBOTS = "https://archive.org/robots.txt"
HOST = "web.archive.org"
EXPECTED = {
    "bytes": 3347,
    "sha256": "45936113efa432f3c8188445ae255108c2af3d06fecf902202f0611068a74a11",
    "format": "JPEG",
    "size": [150, 110],
}
MAX_BODY = 1024 * 1024
MAX_SOURCE_REQUESTS = 12
MAX_ROUNDS = 4
CONNECT_TIMEOUT_DIRECT = 4
TOTAL_TIMEOUT_DIRECT = 6
CONNECT_TIMEOUT_PROXY = 8
TOTAL_TIMEOUT_PROXY = 20


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def parse_header_blocks(text: str) -> list[dict[str, Any]]:
    """Parse every HTTP block, including an HTTP CONNECT response."""

    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in text.splitlines():
        match = re.match(r"^HTTP/(\d(?:\.\d)?)\s+(\d{3})(?:\s+(.*))?$", line.strip(), re.I)
        if match:
            reason = match.group(3) or ""
            current = {
                "http_version": match.group(1),
                "status": int(match.group(2)),
                "reason": reason,
                "headers": {},
                "is_connect": "connection established" in reason.lower(),
            }
            blocks.append(current)
            continue
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        current["headers"][key.strip().lower()] = value.strip()
    return blocks


def source_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove proxy CONNECT status from source HTTP interpretation."""

    return [block for block in blocks if not block.get("is_connect")]


def source_status(blocks: list[dict[str, Any]]) -> int | None:
    blocks = source_blocks(blocks)
    return blocks[-1]["status"] if blocks else None


def source_headers(blocks: list[dict[str, Any]]) -> dict[str, str]:
    blocks = source_blocks(blocks)
    return blocks[-1].get("headers", {}) if blocks else {}


def connect_status(blocks: list[dict[str, Any]]) -> int | None:
    connects = [block for block in blocks if block.get("is_connect")]
    return connects[-1]["status"] if connects else None


def memento_datetime(headers: dict[str, str]) -> str | None:
    return headers.get("memento-datetime")


def decode_image(body: bytes) -> dict[str, Any]:
    result: dict[str, Any] = {"available": Image is not None, "valid": False}
    if Image is None or not body:
        return result
    try:
        with Image.open(io.BytesIO(body)) as image:
            image_format = image.format
            image_size = list(image.size)
            image.verify()
        with Image.open(io.BytesIO(body)) as loaded:
            loaded.load()
        result.update({"valid": True, "format": image_format, "size": image_size, "verify": True, "load": True})
    except Exception as exc:  # pragma: no cover - malformed remote payload
        result.update({"verify": False, "load": False, "error": f"{type(exc).__name__}: {exc}"})
    return result


def expected_match(status: int | None, body: bytes, image: dict[str, Any]) -> bool:
    return (
        status == 200
        and len(body) == EXPECTED["bytes"]
        and hashlib.sha256(body).hexdigest() == EXPECTED["sha256"]
        and image.get("valid") is True
        and image.get("format") == EXPECTED["format"]
        and image.get("size") == EXPECTED["size"]
    )


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
        if key in {"http_code", "http_version"} or key == "remote_ip":
            result[key] = value
        else:
            try:
                result[key] = float(value)
            except ValueError:
                result[key] = None
    return result


def curl_phase(error_text: str, metrics: dict[str, Any], blocks: list[dict[str, Any]], transport: str) -> dict[str, Any]:
    """Describe transport stages without treating CONNECT 200 as source 200."""

    error = error_text.lower()
    status = source_status(blocks)
    connect = connect_status(blocks)
    dns = metrics.get("time_namelookup")
    tcp = metrics.get("time_connect")
    tls = metrics.get("time_appconnect")
    if status is not None:
        outcome = "source_http"
    elif any(token in error for token in ("ssl", "tls", "handshake", "schannel", "unexpected_eof", "certificate")):
        outcome = "tls_failed"
    elif connect is not None and transport == "proxy":
        outcome = "post_connect_no_source_http"
    elif any(token in error for token in ("resolve host", "could not resolve", "name or service")):
        outcome = "dns_failed"
    elif any(token in error for token in ("failed to connect", "timed out", "timeout", "connection refused", "couldn't connect")):
        outcome = "tcp_or_timeout_failed"
    elif error:
        outcome = "curl_failed"
    else:
        outcome = "no_source_status"
    return {
        "outcome": outcome,
        "dns": {"completed": dns is not None and dns > 0, "seconds": dns},
        "tcp": {"completed": tcp is not None and tcp > 0, "seconds": tcp},
        "connect": {"status": connect, "completed": connect is not None} if transport == "proxy" else {"status": None, "completed": None},
        "tls": {"completed": tls is not None and tls > 0, "seconds": tls},
        "http": {"source_status": status, "memento_datetime": memento_datetime(source_headers(blocks))},
    }


def dns_observation(host: str) -> dict[str, Any]:
    started = time.perf_counter()
    addresses: list[str] = []
    error: str | None = None
    try:
        for entry in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM):
            address = entry[4][0]
            if address not in addresses:
                addresses.append(address)
    except OSError as exc:
        error = f"{type(exc).__name__}: {exc}"
    return {
        "host": host,
        "resolver": "system_getaddrinfo",
        "addresses": addresses,
        "error": error,
        "duration_ms": round((time.perf_counter() - started) * 1000, 1),
    }


def previous_summary() -> dict[str, Any]:
    if not SUMMARY_JSON.exists():
        return {"source_request_count": 0, "rounds": []}
    try:
        parsed = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
        return parsed if isinstance(parsed, dict) else {"source_request_count": 0, "rounds": []}
    except (OSError, json.JSONDecodeError):
        return {"source_request_count": 0, "rounds": []}


def write_raw(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data[:MAX_BODY])
    else:
        path.write_text(data[-10000:], encoding="utf-8", errors="replace")


def run_curl(
    *,
    round_number: int,
    request_id: str,
    url: str,
    transport: str,
    connect_timeout: int,
    total_timeout: int,
) -> dict[str, Any]:
    """Run one no-redirect curl request and persist raw evidence."""

    stem = safe_name(f"round{round_number}-{request_id}-{transport}-curl")
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
        "--max-filesize", str(MAX_BODY),
        "--silent", "--show-error",
        "--trace-time", "--trace-ascii", str(trace_path),
        "--dump-header", str(headers_path),
        "--output", str(body_path),
        "--write-out", "%{http_code}\t%{time_namelookup}\t%{time_connect}\t%{time_appconnect}\t%{time_pretransfer}\t%{time_starttransfer}\t%{time_total}\t%{remote_ip}\t%{http_version}",
        "--user-agent", "wow-tls-poll/20261015",
        url,
    ]
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=stderr_path.open("wb"),
            timeout=total_timeout + 3,
            check=False,
        )
        curl_exit = proc.returncode
        stdout = proc.stdout.decode("ascii", "replace")
    except Exception as exc:  # pragma: no cover - OS/process failure evidence
        curl_exit = None
        stdout = ""
        write_raw(stderr_path, f"{type(exc).__name__}: {exc}")
    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    headers_text = headers_path.read_text(encoding="iso-8859-1", errors="replace") if headers_path.exists() else ""
    body = body_path.read_bytes()[:MAX_BODY] if body_path.exists() else b""
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
    write_raw(metrics_path, stdout)
    blocks = parse_header_blocks(headers_text)
    metrics = parse_metrics(stdout)
    source = source_status(blocks)
    image = decode_image(body) if source == 200 else {"available": Image is not None, "valid": False}
    phase = curl_phase(stderr, metrics, blocks, transport)
    return {
        "request_id": request_id,
        "transport": transport,
        "url": url,
        "started_utc": utc_now(),
        "duration_ms": duration_ms,
        "curl_exit": curl_exit,
        "curl_error": stderr[-2000:] if stderr else None,
        "metrics": metrics,
        "phase": phase,
        "connect_status": connect_status(blocks),
        "source_status": source,
        "memento_datetime": memento_datetime(source_headers(blocks)),
        "redirects_requested": 0,
        "automatic_redirects": 0,
        "location": source_headers(blocks).get("location"),
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "image": image,
        "ready": expected_match(source, body, image),
        "raw": {
            "headers": str(headers_path.relative_to(ROOT)),
            "body": str(body_path.relative_to(ROOT)),
            "stderr": str(stderr_path.relative_to(ROOT)),
            "trace": str(trace_path.relative_to(ROOT)),
            "metrics": str(metrics_path.relative_to(ROOT)),
        },
        "header_block_count": len(blocks),
        "header_connect_block_count": sum(1 for block in blocks if block.get("is_connect")),
    }


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: urllib.request.Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def run_urllib(*, round_number: int, request_id: str, url: str, transport: str) -> dict[str, Any]:
    """One default-certificate-verification urllib cross-check."""

    stem = safe_name(f"round{round_number}-{request_id}-{transport}-urllib")
    headers_path = RAW / f"{stem}.headers.txt"
    body_path = RAW / f"{stem}.body"
    stderr_path = RAW / f"{stem}.stderr.txt"
    started = time.perf_counter()
    proxy_handler = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY} if transport == "proxy" else {})
    https_handler = urllib.request.HTTPSHandler(context=ssl.create_default_context())
    opener = urllib.request.build_opener(proxy_handler, https_handler, NoRedirectHandler())
    request = urllib.request.Request(url, headers={"User-Agent": "wow-tls-poll/20261015"})
    source = None
    headers_text = ""
    body = b""
    error: str | None = None
    try:
        with opener.open(request, timeout=TOTAL_TIMEOUT_PROXY if transport == "proxy" else TOTAL_TIMEOUT_DIRECT) as response:
            source = response.status
            headers_text = "HTTP/1.1 %s %s\n%s" % (response.status, response.reason, response.headers)
            body = response.read(MAX_BODY + 1)[:MAX_BODY]
    except urllib.error.HTTPError as exc:
        source = exc.code
        headers_text = "HTTP/1.1 %s %s\n%s" % (exc.code, exc.reason, exc.headers)
        body = exc.read(MAX_BODY + 1)[:MAX_BODY]
        error = f"HTTPError: {exc}"
    except Exception as exc:  # expected for a TLS cross-check failure
        error = f"{type(exc).__name__}: {exc}"
    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    write_raw(headers_path, headers_text)
    write_raw(body_path, body)
    write_raw(stderr_path, error or "")
    image = decode_image(body) if source == 200 else {"available": Image is not None, "valid": False}
    return {
        "request_id": request_id,
        "transport": transport,
        "url": url,
        "started_utc": utc_now(),
        "duration_ms": duration_ms,
        "client": "urllib",
        "tls_verification": "default_ssl_context",
        "curl_exit": None,
        "curl_error": error,
        "metrics": {},
        "phase": {"outcome": "source_http" if source is not None else "urllib_error", "http": {"source_status": source}},
        "connect_status": None,
        "source_status": source,
        "memento_datetime": None,
        "redirects_requested": 0,
        "automatic_redirects": 0,
        "location": None,
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "image": image,
        "ready": expected_match(source, body, image),
        "raw": {
            "headers": str(headers_path.relative_to(ROOT)),
            "body": str(body_path.relative_to(ROOT)),
            "stderr": str(stderr_path.relative_to(ROOT)),
        },
    }


def fixture_check() -> dict[str, Any]:
    cases = {
        "connect_only": "HTTP/1.1 200 Connection established\r\nProxy-Agent: fixture\r\n\r\n",
        "real_404": "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n",
        "connect_then_200": "HTTP/1.1 200 Connection established\r\n\r\nHTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n",
    }
    results = {}
    for name, text in cases.items():
        blocks = parse_header_blocks(text)
        results[name] = {
            "connect_status": connect_status(blocks),
            "source_status": source_status(blocks),
            "source_block_count": len(source_blocks(blocks)),
        }
    assert results["connect_only"]["source_status"] is None
    assert results["real_404"]["source_status"] == 404
    assert results["connect_then_200"]["source_status"] == 200
    return {"passed": True, "cases": results}


def summarize_round(round_number: int, requests: list[dict[str, Any]], dns: list[dict[str, Any]], fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    ready = any(item.get("ready") for item in requests)
    return {
        "round": round_number,
        "started_utc": requests[0].get("started_utc") if requests else utc_now(),
        "finished_utc": utc_now(),
        "ready": ready,
        "dns": dns,
        "request_count": len(requests),
        "requests": requests,
        "fixture": fixture,
    }


def write_summary(round_record: dict[str, Any], prior: dict[str, Any]) -> dict[str, Any]:
    rounds = [item for item in prior.get("rounds", []) if item.get("round") != round_record.get("round")]
    rounds.append(round_record)
    rounds.sort(key=lambda item: item.get("round", 0))
    total_requests = sum(int(item.get("request_count", 0)) for item in rounds)
    summary = {
        "schema": "wayback-tls-poll-20261015.v1",
        "target": TARGET,
        "expected": EXPECTED,
        "proxy": "127.0.0.1:7890",
        "tls_verification": "enabled",
        "max_rounds": MAX_ROUNDS,
        "max_source_requests": MAX_SOURCE_REQUESTS,
        "source_request_count": total_requests,
        "automatic_redirect_count": sum(sum(int(req.get("automatic_redirects", 0)) for req in item.get("requests", [])) for item in rounds),
        "rounds": rounds,
        "last_round": round_record.get("round"),
        "availability": "ready" if any(item.get("ready") for item in rounds) else "not_ready_or_unconfirmed",
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Wayback TLS poll — 2026-10-15",
        "",
        "This record covers the known JPEG control target and preserves CONNECT status separately from source HTTP status.",
        "",
        f"Target: `{TARGET}`",
        f"Expected payload: {EXPECTED['bytes']} bytes, JPEG {EXPECTED['size'][0]}x{EXPECTED['size'][1]}, SHA-256 `{EXPECTED['sha256']}`.",
        f"Rounds recorded: {len(rounds)}; source requests: {total_requests}/{MAX_SOURCE_REQUESTS}; automatic redirects: {summary['automatic_redirect_count']}; availability: `{summary['availability']}`.",
        "",
    ]
    for item in rounds:
        lines.append(f"## Round {item['round']}")
        lines.append("")
        lines.append(f"Ready: `{item.get('ready')}`; requests: {item.get('request_count', 0)}.")
        for req in item.get("requests", []):
            phase = req.get("phase", {})
            lines.append(
                f"- `{req.get('request_id')}` via `{req.get('transport')}`: outcome `{phase.get('outcome')}`, "
                f"CONNECT `{req.get('connect_status')}`, source HTTP `{req.get('source_status')}`, "
                f"decode `{req.get('image', {}).get('valid')}`, bytes `{req.get('body_bytes')}`, ready `{req.get('ready')}`, "
                f"redirects `{req.get('automatic_redirects', 0)}`. Raw evidence: `{req.get('raw', {}).get('trace', req.get('raw', {}).get('stderr', ''))}`.",
            )
        for dns_item in item.get("dns", []):
            lines.append(f"- DNS `{dns_item.get('host')}` via `{dns_item.get('resolver')}`: addresses `{dns_item.get('addresses')}`, error `{dns_item.get('error')}`.")
        if item.get("fixture"):
            lines.append(f"- Offline parser fixtures: `{item['fixture'].get('passed')}`.")
        lines.append("")
    lines.extend(
        [
            "Raw headers, bodies, stderr, curl traces and metrics are local ignored evidence under `raw/`; summary fields are redacted metadata.",
            "A proxy `200 Connection established` is never counted as source HTTP 200. Only source HTTP 200 plus exact payload hash, byte length and image decode is `ready`.",
            "",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")
    return summary


def run_round(round_number: int) -> dict[str, Any]:
    if not 1 <= round_number <= MAX_ROUNDS:
        raise SystemExit(f"round must be 1..{MAX_ROUNDS}")
    ROOT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    prior = previous_summary()
    prior_count = int(prior.get("source_request_count", 0))
    if prior_count >= MAX_SOURCE_REQUESTS:
        raise SystemExit("source request budget already exhausted")
    dns = [dns_observation(HOST)]
    requests: list[dict[str, Any]] = []
    if round_number in {1, 4}:
        direct = run_curl(round_number=round_number, request_id="target", url=TARGET, transport="direct", connect_timeout=CONNECT_TIMEOUT_DIRECT, total_timeout=TOTAL_TIMEOUT_DIRECT)
        requests.append(direct)
        direct_failed = direct.get("source_status") is None or direct.get("curl_exit") not in (0, None)
        if direct_failed and prior_count + len(requests) < MAX_SOURCE_REQUESTS:
            proxy = run_curl(round_number=round_number, request_id="target", url=TARGET, transport="proxy", connect_timeout=CONNECT_TIMEOUT_PROXY, total_timeout=TOTAL_TIMEOUT_PROXY)
            requests.append(proxy)
        else:
            proxy = None
    else:
        proxy = run_curl(round_number=round_number, request_id="target", url=TARGET, transport="proxy", connect_timeout=CONNECT_TIMEOUT_PROXY, total_timeout=TOTAL_TIMEOUT_PROXY)
        requests.append(proxy)
    fixture = fixture_check()
    if any(item.get("phase", {}).get("outcome") == "tls_failed" for item in requests) and prior_count + len(requests) < MAX_SOURCE_REQUESTS:
        tls_item = requests[-1]
        cross = run_urllib(round_number=round_number, request_id="target", url=TARGET, transport=tls_item.get("transport", "proxy"))
        requests.append(cross)
        if prior_count + len(requests) < MAX_SOURCE_REQUESTS and tls_item.get("transport") == "proxy":
            robots = run_curl(round_number=round_number, request_id="robots", url=ROBOTS, transport="proxy", connect_timeout=CONNECT_TIMEOUT_PROXY, total_timeout=TOTAL_TIMEOUT_PROXY)
            requests.append(robots)
    record = summarize_round(round_number, requests, dns, fixture)
    return write_summary(record, prior)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true", help="run only offline CONNECT/source status fixtures")
    parser.add_argument("--round", type=int, default=1, help="bounded poll round, 1..4")
    args = parser.parse_args(argv)
    if args.fixture:
        result = fixture_check()
        print(json.dumps(result, ensure_ascii=False))
        return 0
    result = run_round(args.round)
    print(json.dumps({"last_round": result.get("last_round"), "source_request_count": result.get("source_request_count"), "availability": result.get("availability")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

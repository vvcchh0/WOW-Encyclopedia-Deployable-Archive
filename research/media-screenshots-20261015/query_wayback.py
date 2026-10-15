#!/usr/bin/env python3
"""Bounded, serial Wayback CDX and replay survey for MEDIA SSOTD.

The request list begins with evidence-backed US source paths. It does not
repeat the parent's empty exact index.html query, and it never invents a
numeric screenshot path before a CDX prefix row supplies one.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "wayback-window"
RAW = OUT / "raw"
CURL = r"C:\Windows\System32\curl.exe"
PROXY = "http://127.0.0.1:7890"
MAX_SOURCE_REQUESTS = 25
MAX_TOTAL_BODY = 64 * 1024 * 1024
MAX_BODY = 8 * 1024 * 1024
START_INTERVAL = 1.1
TIMEOUT = 30


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return value[:100].strip("._") or "request"


def request_url(target: str, **params: str) -> str:
    defaults = {
        "url": target,
        "matchType": "exact",
        "output": "json",
        "fl": "timestamp,original,statuscode,mimetype,digest,length",
        "showResumeKey": "true",
        "limit": "1000",
    }
    defaults.update(params)
    return "https://web.archive.org/cdx/search/cdx?" + urlencode(defaults)


def parse_headers(path: Path) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in path.read_text(encoding="iso-8859-1", errors="replace").splitlines():
        match = re.match(r"^HTTP/\d(?:\.\d)?\s+(\d{3})(?:\s+(.*))?$", line.strip(), re.I)
        if match:
            current = {"status": int(match.group(1)), "reason": match.group(2) or "", "headers": {}}
            blocks.append(current)
            continue
        if current is not None and ":" in line:
            key, value = line.split(":", 1)
            current["headers"][key.strip().lower()] = value.strip()
    return blocks


def effective_block(blocks: list[dict[str, Any]]) -> dict[str, Any] | None:
    usable = [
        block for block in blocks
        if not (
            block.get("status") == 200
            and "connection established" in str(block.get("reason", "")).lower()
        )
    ]
    return usable[-1] if usable else None


def parse_cdx(body: bytes) -> tuple[list[dict[str, Any]], str | None, Any]:
    if not body:
        return [], None, None
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}", None
    if not isinstance(payload, list):
        return [], "CDX JSON root is not a list", payload
    if not payload:
        return [], None, payload
    if isinstance(payload[0], list):
        header = [str(value) for value in payload[0]]
        rows = [
            {key: value for key, value in zip(header, row)}
            for row in payload[1:]
            if isinstance(row, list)
        ]
        return rows, None, payload
    return [], "CDX JSON has no header row", payload


def pillow_probe(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"exists": path.is_file(), "decoded": False, "format": None, "width": None, "height": None, "error": None}
    if not path.is_file():
        return result
    try:
        if Image is None:
            result["error"] = "Pillow unavailable"
            return result
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            result.update({"decoded": True, "format": image.format, "width": image.width, "height": image.height})
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


class Window:
    def __init__(self) -> None:
        OUT.mkdir(parents=True, exist_ok=True)
        RAW.mkdir(parents=True, exist_ok=True)
        self.records: list[dict[str, Any]] = []
        self.source_requests = 0
        self.total_body = 0
        self.last_start = 0.0
        self.transport_failures = 0
        self.stop_reason: str | None = None

    def run(self, label: str, url: str, kind: str, parse_json: bool = False) -> dict[str, Any]:
        if self.stop_reason:
            return {"label": label, "executed": False, "reason": self.stop_reason}
        if self.source_requests >= MAX_SOURCE_REQUESTS:
            self.stop_reason = "source_request_budget"
            return {"label": label, "executed": False, "reason": self.stop_reason}
        delay = START_INTERVAL - (time.monotonic() - self.last_start)
        if delay > 0:
            time.sleep(delay)
        self.last_start = time.monotonic()
        self.source_requests += 1
        index = self.source_requests
        stem = f"{index:02d}-{safe_name(label)}"
        body_path = RAW / f"{stem}.body"
        headers_path = RAW / f"{stem}.headers.txt"
        stderr_path = RAW / f"{stem}.stderr.txt"
        trace_path = RAW / f"{stem}.trace.txt"
        command = [
            CURL,
            "--proxy", PROXY,
            "--noproxy", "",
            "--http1.1",
            "--connect-timeout", "8",
            "--max-time", str(TIMEOUT),
            "--max-redirs", "0",
            "--max-filesize", str(MAX_BODY),
            "--silent", "--show-error",
            "--trace-time", "--trace-ascii", str(trace_path),
            "--dump-header", str(headers_path),
            "--output", str(body_path),
            "--write-out", "%{http_code}",
            "--user-agent", "WOW-Encyclopedia-media-screenshots/20261015",
            url,
        ]
        started = time.monotonic()
        try:
            process = subprocess.run(
                command,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=stderr_path.open("wb"),
                timeout=TIMEOUT + 5,
                check=False,
            )
            curl_code = process.returncode
            write_out = process.stdout.decode("ascii", "replace").strip()
        except Exception as exc:  # pragma: no cover
            curl_code = None
            write_out = ""
            stderr_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        body = body_path.read_bytes() if body_path.is_file() else b""
        headers = parse_headers(headers_path) if headers_path.is_file() else []
        block = effective_block(headers)
        status = block.get("status") if block else (int(write_out) if write_out.isdigit() and write_out != "000" else None)
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.is_file() else ""
        transport_error = curl_code != 0 or status is None
        if transport_error:
            self.transport_failures += 1
        else:
            self.transport_failures = 0
        self.total_body += len(body)
        if status in (429, 503):
            self.stop_reason = f"endpoint_status_{status}"
        elif self.transport_failures >= 5:
            self.stop_reason = "five_consecutive_transport_failures"
        elif self.total_body > MAX_TOTAL_BODY:
            self.stop_reason = "total_body_limit"
        rows: list[dict[str, Any]] = []
        parse_error = None
        parsed = None
        if parse_json and body:
            rows, parse_error, parsed = parse_cdx(body)
        record: dict[str, Any] = {
            "request_index": index,
            "label": label,
            "kind": kind,
            "request_url": url,
            "started_utc": datetime.fromtimestamp(started + (time.time() - time.monotonic()), timezone.utc).isoformat(),
            "finished_utc": now(),
            "duration_seconds": round(time.monotonic() - started, 3),
            "status": status,
            "curl_exit": curl_code,
            "transport_error": transport_error,
            "stderr_tail": stderr[-2000:],
            "body_bytes": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
            "headers_path": str(headers_path.relative_to(OUT)).replace("\\", "/"),
            "body_path": str(body_path.relative_to(OUT)).replace("\\", "/"),
            "trace_path": str(trace_path.relative_to(OUT)).replace("\\", "/"),
            "headers": block.get("headers", {}) if block else {},
            "rows": rows,
            "rows_count": len(rows),
            "parse_error": parse_error,
            "raw_json_root": parsed if parsed is not None and not rows else None,
        }
        self.records.append(record)
        return record


def cdx_target_url(target: str, match_type: str = "exact", **params: str) -> str:
    if "from_" in params:
        params["from"] = params.pop("from_")
    return request_url(target, matchType=match_type, **params)


def choose_image_rows(rows: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    full: list[dict[str, Any]] = []
    thumbs: list[dict[str, Any]] = []
    for row in rows:
        original = str(row.get("original", ""))
        mime = str(row.get("mimetype", "")).lower()
        if row.get("statuscode") != "200" or not mime.startswith("image/"):
            continue
        path = original.split("?", 1)[0].rstrip("/").lower()
        if re.search(r"/ss\d+\.jpg$", path):
            full.append(row)
        elif re.search(r"/ss\d+-thumb\.jpg$", path):
            thumbs.append(row)
    # Prefer a 2008 capture where the CDX row supplies one; otherwise earliest
    # observed row. This is selection, not a guessed path.
    def rank(row: dict[str, Any]) -> tuple[int, str]:
        stamp = str(row.get("timestamp", ""))
        return (0 if stamp.startswith("2008") else 1, stamp)
    return (sorted(full, key=rank)[0] if full else None, sorted(thumbs, key=rank)[0] if thumbs else None)


def replay_url(row: dict[str, Any]) -> str:
    timestamp = str(row["timestamp"])
    original = str(row["original"])
    return f"https://web.archive.org/web/{timestamp}id_/{original}"


def main() -> int:
    window = Window()
    us_host = "http://www.worldofwarcraft.com"
    # The local page embeds the trailing-slash source identity; the JS supplies
    # the images/screens path. Parent's index.html exact query is intentionally
    # absent here.
    calls = [
        ("entry_trailing_slash_all", cdx_target_url(f"{us_host}/downloads/ssotd/"), "cdx", True),
        ("entry_trailing_slash_2006_2010", cdx_target_url(f"{us_host}/downloads/ssotd/", from_="2006", to="2010"), "cdx", True),
        ("ssotd_prefix_pages_all", cdx_target_url(f"{us_host}/downloads/ssotd/", match_type="prefix", showNumPages="true"), "cdx", True),
        ("ssotd_images_prefix_pages_all", cdx_target_url(f"{us_host}/downloads/ssotd/images/", match_type="prefix", showNumPages="true"), "cdx", True),
        ("ssotd_screens_prefix_pages_all", cdx_target_url(f"{us_host}/downloads/ssotd/images/screens/", match_type="prefix", showNumPages="true"), "cdx", True),
        ("anachronos_exact_all", cdx_target_url(f"{us_host}/downloads/ssotd/anachronos.xml"), "cdx", True),
    ]
    # Use no more than one first-page request for each prefix. If a response
    # contains a row, later exact/replay requests are selected from that row.
    image_rows: list[dict[str, Any]] = []
    for label, url, kind, parse_json in calls:
        result = window.run(label, url, kind, parse_json)
        image_rows.extend(result.get("rows", []))
        if window.stop_reason:
            break
    full_row, thumb_row = choose_image_rows(image_rows)
    selected_rows: list[dict[str, Any]] = []
    for row in (full_row, thumb_row):
        if row and row not in selected_rows:
            selected_rows.append(row)
    for row in selected_rows:
        original = str(row["original"])
        label = "image_exact_" + safe_name(original)
        window.run(label, cdx_target_url(original), "cdx_image_exact", True)
        if window.stop_reason:
            break
        replay = window.run(label + "_replay", replay_url(row), "memento_replay", False)
        replay["selected_cdx_row"] = row
        replay_path = RAW / f"{replay['request_index']:02d}-{safe_name(label)}_replay_validation.json"
        body_path = OUT / replay["body_path"]
        probe = pillow_probe(body_path)
        replay["payload_probe"] = probe
        replay_path.write_text(json.dumps(replay, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if window.stop_reason:
            break
    summary = {
        "schema_version": 1,
        "started_utc": window.records[0]["started_utc"] if window.records else now(),
        "finished_utc": now(),
        "proxy": PROXY,
        "serial": True,
        "minimum_interval_seconds": START_INTERVAL,
        "max_source_requests": MAX_SOURCE_REQUESTS,
        "source_requests": window.source_requests,
        "total_body_bytes": window.total_body,
        "stop_reason": window.stop_reason or "plan_complete",
        "transport_failure_streak_at_stop": window.transport_failures,
        "records_file": "request-records.json",
        "raw_directory": "raw/",
        "selected_rows": selected_rows,
        "interpretation": [
            "CDX JSON rows are index evidence only.",
            "A Memento replay is separately recorded; CONNECT 200 blocks are excluded from source status.",
            "Empty/invalid CDX bodies are retained with status, body hash, and parse_error; they are not treated as an empty index unless JSON parses to [].",
            "No guessed screenshot number was queried; exact image targets came from a status-200 image row returned by a prefix query.",
        ],
    }
    (OUT / "request-records.json").write_text(json.dumps(window.records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_requests": window.source_requests,
        "total_body_bytes": window.total_body,
        "stop_reason": summary["stop_reason"],
        "cdx_rows_observed": sum(record["rows_count"] for record in window.records),
        "full_row": full_row,
        "thumb_row": thumb_row,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

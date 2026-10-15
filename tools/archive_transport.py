#!/usr/bin/env python3
"""Direct-first, bounded Wayback image recovery for the EU gallery evidence.

This runner is deliberately narrower than the first regional-gallery runner. It
uses the already captured CDX prefix, retries only the three local curl-23
records, and then selects a small origin-aware supplement batch. Every request
is tried directly first. A proxy request is made only when the direct result is
not a valid replay; a local output error is never sent through the proxy.

The module keeps the transport and validation functions small enough for unit
tests. Running it from the repository root writes only beneath the supplied
output directory.
"""

from __future__ import annotations

import argparse
import base64
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from email.utils import parsedate_to_datetime
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Callable, Iterable
from urllib.parse import urlsplit, urlunsplit

try:
    from PIL import Image
except Exception:  # pragma: no cover - the workspace runtime supplies Pillow
    Image = None


ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "20080512210044"
BASELINE_START = "20080101000000"
PROXY = "http://127.0.0.1:7890"
MAX_ENTITIES = 18
MAX_RESPONSE_BYTES = 64 * 1024 * 1024
MAX_ENTITY_BYTES = 16 * 1024 * 1024
NETWORK_WINDOW_SECONDS = 8 * 60
MIN_FREE_BYTES = 11_005_853_696  # 10 GiB + 256 MiB safety threshold
INTERVAL_SECONDS = 1.0
CDX_DIGEST_RE = re.compile(r"^[A-Z2-7]{32}$")
TIMESTAMP_RE = re.compile(r"^\d{14}$")
JPEG_PATH_RE = re.compile(r"^/screenoftheday/screenoftheday/.+\.jpg$", re.I)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cdx_digest(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii")


def workspace_bytes(root: Path) -> int:
    total = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in {"__pycache__"}]
        for name in files:
            try:
                total += (Path(current) / name).stat().st_size
            except OSError:
                continue
    return total


def drive_free_bytes(path: Path) -> int:
    return int(shutil.disk_usage(path).free)


def parse_cdx_table(path: Path) -> list[dict[str, str]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or not value or not isinstance(value[0], list):
        raise ValueError("CDX table must be a header row followed by rows")
    names = [str(item) for item in value[0]]
    return [
        {names[index]: str(item[index]) for index in range(min(len(names), len(item)))}
        for item in value[1:]
        if isinstance(item, list)
    ]


def origin_namespace(url: str) -> str:
    parsed = urlsplit(url)
    return (parsed.hostname or "").casefold().rstrip(".")


def origin_route(url: str) -> str:
    parsed = urlsplit(url)
    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path
    return f"/_origins/{origin_namespace(url)}{path}"


def route_key(url: str) -> str:
    return origin_route(url).casefold()


def temporal_class(timestamp: str) -> str:
    if timestamp < BASELINE_START:
        return "pre_2008"
    if timestamp <= ANCHOR:
        return "baseline_2008"
    return "late_2008"


def normalize_original(row: dict[str, str]) -> str:
    original = row.get("original", "")
    parsed = urlsplit(original)
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"invalid original URL: {original!r}")
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError(f"unsafe original URL: {original!r}")
    if not parsed.path.startswith("/"):
        raise ValueError(f"invalid original path: {original!r}")
    return urlunsplit((parsed.scheme.casefold(), parsed.netloc, parsed.path, "", ""))


def candidate_from_row(row: dict[str, str]) -> dict[str, Any] | None:
    try:
        original = normalize_original(row)
    except ValueError:
        return None
    parsed = urlsplit(original)
    timestamp = row.get("timestamp", "")
    digest = row.get("digest", "").upper()
    if (
        row.get("statuscode") != "200"
        or row.get("mimetype", "").split(";", 1)[0].casefold() != "image/jpeg"
        or not JPEG_PATH_RE.fullmatch(parsed.path)
        or not TIMESTAMP_RE.fullmatch(timestamp)
        or timestamp > ANCHOR
        or not CDX_DIGEST_RE.fullmatch(digest)
        or not row.get("length", "").isdigit()
    ):
        return None
    return {
        "actual_timestamp": timestamp,
        "cdx_digest": digest,
        "cdx_length": int(row["length"]),
        "cdx_metadata": "research/related-sites-20261014/regional-gallery/cdx/screen-assets-baseline.rows.json",
        "indexed_capture_timestamp": timestamp,
        "kind": "image",
        "logical_url": original,
        "mime": "image/jpeg",
        "original": original,
        "path": parsed.path,
        "origin_namespace": origin_namespace(original),
        "temporal_class": temporal_class(timestamp),
    }


def select_latest_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        candidate = candidate_from_row(row)
        if candidate is not None:
            grouped[route_key(candidate["original"])].append(candidate)
    selected: list[dict[str, Any]] = []
    for items in grouped.values():
        selected.append(max(items, key=lambda item: item["actual_timestamp"]))
    return selected


def _pair_key(item: dict[str, Any]) -> str:
    name = Path(item["path"]).name
    filename = name[:-10].casefold() + ".jpg" if name.casefold().endswith("-thumb.jpg") else name.casefold()
    return f"{item['origin_namespace']}:{filename}"


def select_new_candidates(
    rows: Iterable[dict[str, str]],
    *,
    existing_routes: set[str],
    attempted_routes: set[str],
    limit: int = MAX_ENTITIES,
) -> list[dict[str, Any]]:
    selected = [
        item
        for item in select_latest_rows(rows)
        if route_key(item["original"]) not in existing_routes
        and route_key(item["original"]) not in attempted_routes
    ]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in selected:
        groups[_pair_key(item)].append(item)
    paired: list[dict[str, Any]] = []
    unpaired: list[dict[str, Any]] = []
    for items in groups.values():
        names = {Path(item["path"]).name.casefold() for item in items}
        has_full = any(not name.endswith("-thumb.jpg") for name in names)
        has_thumb = any(name.endswith("-thumb.jpg") for name in names)
        (paired if has_full and has_thumb else unpaired).extend(items)

    def rank(item: dict[str, Any]) -> tuple[int, int, int, str]:
        return (
            0 if item["temporal_class"] == "baseline_2008" else 1,
            -int(item["actual_timestamp"]),
            1 if Path(item["path"]).name.casefold().endswith("-thumb.jpg") else 0,
            item["path"],
        )

    paired.sort(
        key=lambda item: (
            0 if item["temporal_class"] == "baseline_2008" else 1,
            -max(int(peer["actual_timestamp"]) for peer in groups[_pair_key(item)]),
            1 if Path(item["path"]).name.casefold().endswith("-thumb.jpg") else 0,
            item["path"],
        )
    )
    unpaired.sort(key=rank)
    # Keep pairs together when the limit permits it.  A pair may be split only
    # at the exact cap, where the higher ranked entity is still useful alone.
    ordered = paired + unpaired
    return ordered[:limit]


def load_routes(manifest_path: Path, provenance_path: Path) -> set[str]:
    routes: set[str] = set()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for record in manifest.get("files", []) if isinstance(manifest, dict) else []:
        if isinstance(record, dict) and isinstance(record.get("route"), str):
            routes.add(record["route"].casefold())
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    for record in provenance.get("files", []) if isinstance(provenance, dict) else []:
        if isinstance(record, dict) and isinstance(record.get("route"), str):
            routes.add(record["route"].casefold())
    return routes


def load_old_retry_items(meta_dir: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(meta_dir.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if int(record.get("curl_exit_code") or 0) != 23:
            continue
        if not record.get("logical_url") or not record.get("expected_cdx_digest"):
            continue
        result.append(
            {
                "actual_timestamp": str(record["selected_timestamp"]),
                "cdx_digest": str(record["expected_cdx_digest"]).upper(),
                "cdx_length": int(record.get("expected_cdx_length") or 0),
                "cdx_metadata": "research/related-sites-20261014/regional-gallery/cdx/screen-assets-baseline.rows.json",
                "indexed_capture_timestamp": str(record["selected_timestamp"]),
                "kind": "image",
                "logical_url": str(record["original"]),
                "mime": "image/jpeg",
                "original": str(record["original"]),
                "path": urlsplit(str(record["original"])).path,
                "origin_namespace": origin_namespace(str(record["original"])),
                "temporal_class": str(record.get("temporal_class") or temporal_class(str(record["selected_timestamp"]))),
                "retry_source": str(path),
            }
        )
    return result


def filter_retry_items(items: Iterable[dict[str, Any]], existing_routes: set[str]) -> list[dict[str, Any]]:
    """Keep only retry records whose origin-aware route is not already present."""

    return [item for item in items if route_key(str(item.get("original") or "")) not in existing_routes]


def parse_headers(path: Path) -> tuple[dict[str, str], int | None, int]:
    try:
        lines = path.read_text(encoding="iso-8859-1", errors="replace").splitlines()
    except OSError:
        return {}, None, 0
    blocks: list[tuple[dict[str, str], int | None, bool]] = []
    current: dict[str, str] | None = None
    status: int | None = None
    is_connect = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("HTTP/"):
            if current is not None:
                blocks.append((current, status, is_connect))
            current, status, is_connect = {}, None, False
            fields = stripped.split()
            if len(fields) > 1 and fields[1].isdigit():
                status = int(fields[1])
                is_connect = "connection established" in " ".join(fields[2:]).casefold()
        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip()
    if current is not None:
        blocks.append((current, status, is_connect))
    source_blocks = [block for block in blocks if not block[2]]
    return (*source_blocks[-1][:2], len(blocks)) if source_blocks else ({}, None, len(blocks))


def header(headers: dict[str, str], name: str) -> str | None:
    for key, value in headers.items():
        if key.casefold() == name.casefold():
            return value
    return None


def memento_timestamp(headers: dict[str, str], final_url: str) -> str | None:
    value = header(headers, "Memento-Datetime")
    if value:
        try:
            return parsedate_to_datetime(value).astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
        except (TypeError, ValueError, OverflowError):
            pass
    return None


def pillow_info(data: bytes) -> dict[str, Any]:
    if Image is None:
        return {"valid": False, "error": "pillow_unavailable"}
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            return {"valid": True, "format": image.format, "width": image.width, "height": image.height, "mode": image.mode}
    except Exception as exc:  # pragma: no cover - validation evidence
        return {"valid": False, "error": f"{type(exc).__name__}:{exc}"}


def validate_replay(item: dict[str, Any], body: bytes, headers: dict[str, str], final_url: str, exit_code: int, reported_type: str | None) -> dict[str, Any]:
    status_header = header(headers, ":status")
    del status_header  # curl headers use the parsed status return value below
    mime = (header(headers, "Content-Type") or reported_type or "").split(";", 1)[0].strip().casefold()
    memento = memento_timestamp(headers, final_url)
    image = pillow_info(body)
    digest = cdx_digest(body) if body else None
    expected_digest = str(item["cdx_digest"]).upper()
    expected_length = int(item.get("cdx_length") or 0)
    response_length = header(headers, "Content-Length")
    response_length_match = (
        not response_length
        or not response_length.isdigit()
        or int(response_length) == len(body)
    )
    reasons: list[str] = []
    if exit_code != 0:
        reasons.append(f"curl_exit_{exit_code}")
    # status is supplied by the caller after parsing the final header block.
    return {
        "curl_exit_code": exit_code,
        "mime": mime,
        "memento_datetime": header(headers, "Memento-Datetime"),
        "actual_timestamp": memento,
        "wire_length": len(body),
        "wire_sha256": sha256_bytes(body),
        "observed_cdx_digest": digest,
        "expected_cdx_digest": expected_digest,
        "expected_cdx_length": expected_length,
        "cdx_digest_match": digest == expected_digest,
        "cdx_length_match": len(body) == expected_length,
        "response_content_length": response_length,
        "response_content_length_match": response_length_match,
        "magic": "jpeg" if body.startswith(b"\xff\xd8\xff") else None,
        "pillow": image,
        "memento_timestamp_match": memento == item["actual_timestamp"],
        "failure_reasons": reasons,
    }


def classify_failure(record: dict[str, Any]) -> str:
    reasons = set(record.get("failure_reasons") or [])
    if any(reason == "local_write_error" or reason.startswith("curl_exit_23") for reason in reasons):
        return "local_write_error"
    if any(reason.startswith("curl_exit_") for reason in reasons) or record.get("status") in {None, 0}:
        return "transport"
    status = record.get("status")
    if isinstance(status, int) and status not in {0, 200}:
        return "http"
    if "memento_timestamp" in reasons:
        return "memento"
    if "cdx_digest" in reasons or "cdx_length" in reasons:
        return "digest"
    if "magic" in reasons or "pillow" in reasons or "mime" in reasons:
        return "content"
    return "http"


def archive_url(item: dict[str, Any]) -> str:
    return f"https://web.archive.org/web/{item['actual_timestamp']}id_/{item['original']}"


def _curl_command(
    item: dict[str, Any],
    transport: str,
    header_path: Path,
    body_path: Path,
    remaining_bytes: int,
    remaining_seconds: int | None = None,
) -> list[str]:
    limit = min(MAX_ENTITY_BYTES, max(1, remaining_bytes))
    command = [r"C:\Windows\System32\curl.exe"]
    if transport == "direct":
        command.extend(["--noproxy", "*"])
        connect_timeout, max_time = 8, 15
    elif transport == "proxy":
        command.extend(["--proxy", PROXY])
        connect_timeout, max_time = 10, 30
    else:
        raise ValueError(f"unknown transport: {transport}")
    if remaining_seconds is not None:
        max_time = max(1, min(max_time, remaining_seconds))
        connect_timeout = min(connect_timeout, max_time)
    command.extend(
        [
            "--http1.1",
            "--retry", "0",
            "--connect-timeout", str(connect_timeout),
            "--max-time", str(max_time),
            "--max-filesize", str(limit),
            "--location", "--silent", "--show-error",
            "--dump-header", str(header_path.resolve()),
            "--output", str(body_path.resolve()),
            "--write-out", "%{http_code}\t%{url_effective}\t%{content_type}\t%{size_download}\t%{time_total}",
            archive_url(item),
        ]
    )
    return command


def run_attempt(
    item: dict[str, Any],
    *,
    transport: str,
    rank: int,
    output: Path,
    remaining_bytes: int,
    deadline: float | None = None,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", item["path"].strip("/"))
    stem = f"{rank:03d}-{slug}"
    attempt_dir = output / "entities" / "attempts"
    header_path = output / "entities" / "headers" / f"{stem}-{transport}.txt"
    stderr_path = output / "entities" / "headers" / f"{stem}-{transport}.stderr.txt"
    body_path = attempt_dir / f"{stem}-{transport}.bin"
    for path in (header_path, stderr_path, body_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    remaining_float = None if deadline is None else deadline - time.monotonic()
    if remaining_float is not None and remaining_float <= 0:
        return {
            "transport": transport,
            "status": None,
            "curl_exit_code": None,
            "final_url": archive_url(item),
            "body_path": str(body_path),
            "header_path": str(header_path),
            "stderr_path": str(stderr_path),
            "elapsed_seconds": 0.0,
            "wire_bytes": 0,
            "failure_reasons": ["deadline_exhausted"],
            "validation": {},
            "accepted": False,
            "failure_class": "transport",
        }
    remaining_seconds = None if remaining_float is None else max(1, int(remaining_float))
    command = _curl_command(item, transport, header_path, body_path, remaining_bytes, remaining_seconds)
    started = time.monotonic()
    try:
        default_max_time = 15 if transport == "direct" else 30
        max_time = default_max_time if remaining_seconds is None else min(default_max_time, remaining_seconds)
        timeout = max_time + 5 if remaining_float is None else min(max_time + 5, max(0.1, remaining_float))
        result = runner(command, capture_output=True, timeout=timeout, check=False)
        stdout = getattr(result, "stdout", b"") or b""
        stderr = getattr(result, "stderr", b"") or b""
        stderr_path.write_bytes(stderr)
        fields = stdout.decode("utf-8", errors="replace").strip().split("\t")
        exit_code = int(getattr(result, "returncode", 1))
        status = int(fields[0]) if fields and fields[0].isdigit() else None
        final_url = fields[1] if len(fields) > 1 and fields[1] else archive_url(item)
        reported_type = fields[2] if len(fields) > 2 else None
        size_download = int(fields[3]) if len(fields) > 3 and fields[3].isdigit() else None
        time_total = fields[4] if len(fields) > 4 else None
    except subprocess.TimeoutExpired as exc:
        stderr_path.write_text(str(exc), encoding="utf-8")
        partial = body_path.read_bytes() if body_path.is_file() else b""
        return {
            "transport": transport,
            "status": None,
            "curl_exit_code": None,
            "final_url": archive_url(item),
            "body_path": str(body_path),
            "header_path": str(header_path),
            "stderr_path": str(stderr_path),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "wire_bytes": len(partial),
            "wire_sha256": sha256_bytes(partial),
            "failure_reasons": ["process_timeout"],
            "validation": {},
            "accepted": False,
            "failure_class": "transport",
        }
    headers, header_status, status_lines = parse_headers(header_path)
    body = body_path.read_bytes() if body_path.is_file() else b""
    status = status if status is not None else header_status
    validation = validate_replay(item, body, headers, final_url, exit_code, reported_type)
    reasons = list(validation["failure_reasons"])
    if status != 200:
        reasons.append(f"http_{status}")
    if validation["mime"] != "image/jpeg":
        reasons.append("mime")
    if validation["magic"] != "jpeg":
        reasons.append("magic")
    if not validation["pillow"].get("valid"):
        reasons.append("pillow")
    if not validation["cdx_digest_match"]:
        reasons.append("cdx_digest")
    # CDX ``length`` is the archived record length and may include WARC or
    # replay framing.  It is recorded for comparison only; the acceptance
    # gate is the decoded body plus the indexed CDX SHA-1 digest.
    if not validation["response_content_length_match"]:
        reasons.append("content_length")
    if not validation["memento_timestamp_match"]:
        reasons.append("memento_timestamp")
    if exit_code == 23:
        reasons.append("local_write_error")
    accepted = not reasons
    record = {
        "transport": transport,
        "status": status,
        "curl_exit_code": exit_code,
        "final_url": final_url,
        "reported_content_type": reported_type,
        "size_download_reported": size_download,
        "time_total": time_total,
        "header_status": header_status,
        "status_line_count": status_lines,
        "body_path": str(body_path),
        "header_path": str(header_path),
        "stderr_path": str(stderr_path),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "wire_bytes": len(body),
        "validation": validation,
        "failure_reasons": sorted(set(reasons)),
        "accepted": accepted,
        "failure_class": None if accepted else classify_failure({"failure_reasons": reasons, "status": status}),
    }
    return record


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def make_source_entry(item: dict[str, Any], raw_path: Path) -> dict[str, Any]:
    info = pillow_info(raw_path.read_bytes())
    input_map = ROOT / item["cdx_metadata"]
    return {
        "actual_timestamp": item["actual_timestamp"],
        "cdx_digest": item["cdx_digest"],
        "cdx_metadata": item["cdx_metadata"],
        "dimensions": [info["width"], info["height"]],
        "indexed_capture_timestamp": item["indexed_capture_timestamp"],
        "kind": "image",
        "length": raw_path.stat().st_size,
        "local_path": _relative(raw_path),
        "logical_url": item["logical_url"],
        "mime": "image/jpeg",
        "origin_namespace": item["origin_namespace"],
        "original": item["original"],
        "route": origin_route(item["logical_url"]),
        "schema_version": 1,
        "sha256": sha256_file(raw_path),
        "source_page": "research/related-sites-20261014/regional-gallery/pages/screen-page-20080510105954.html",
        "source_relationship": "complete-prefix-directory-enumerated; direct-first bounded supplement",
        "temporal_class": item["temporal_class"],
        "integration_input_map": item["cdx_metadata"],
        "integration_input_map_sha256": sha256_file(input_map),
    }


def preflight(root: Path, output: Path, max_workspace_bytes: int | None = None) -> dict[str, Any]:
    current = workspace_bytes(root)
    free = drive_free_bytes(root)
    if max_workspace_bytes is not None and current + MAX_RESPONSE_BYTES > max_workspace_bytes:
        raise RuntimeError("workspace cap would be exceeded by the bounded response budget")
    if free - MAX_RESPONSE_BYTES < MIN_FREE_BYTES:
        raise RuntimeError("D: free-space safety threshold would be exceeded by the bounded response budget")
    return {
        "kind": "direct_first_archive_transport_preflight",
        "generated_utc": now_utc(),
        "workspace_bytes": current,
        "drive_free_bytes": free,
        "max_workspace_bytes": max_workspace_bytes,
        "min_free_bytes": MIN_FREE_BYTES,
        "response_budget_bytes": MAX_RESPONSE_BYTES,
        "output": _relative(output),
    }


def run_batch(
    *,
    cdx_path: Path,
    old_meta_dir: Path,
    manifest_path: Path,
    provenance_path: Path,
    output: Path,
    interval: float = INTERVAL_SECONDS,
    max_workspace_bytes: int | None = None,
) -> dict[str, Any]:
    if output.exists():
        if not output.is_dir() or any(output.iterdir()):
            raise RuntimeError(f"output directory must be new or empty: {output}")
    else:
        output.mkdir(parents=True, exist_ok=False)
    pre = preflight(ROOT, output, max_workspace_bytes=max_workspace_bytes)
    atomic_json(output / "preflight.json", pre)
    existing_routes = load_routes(manifest_path, provenance_path)
    retry_candidates = load_old_retry_items(old_meta_dir)
    old_retry = filter_retry_items(retry_candidates, existing_routes)
    attempted_routes = {route_key(item["original"]) for item in old_retry}
    rows = parse_cdx_table(cdx_path)
    new_items = select_new_candidates(rows, existing_routes=existing_routes, attempted_routes=attempted_routes, limit=MAX_ENTITIES - len(old_retry))
    selected = old_retry + new_items
    atomic_json(
        output / "selection.json",
        {
            "schema_version": 1,
            "anchor_timestamp": ANCHOR,
            "old_local_write_retries": len(old_retry),
            "old_local_write_retry_candidates": len(retry_candidates),
            "old_local_write_retry_excluded_existing": len(retry_candidates) - len(old_retry),
            "new_candidates": len(new_items),
            "selected": len(selected),
            "existing_route_count": len(existing_routes),
            "rows": len(rows),
            "retry_items": old_retry,
            "new_items": new_items,
        },
    )

    started: float | None = None
    started_utc: str | None = None
    previous_request: float | None = None
    response_used = 0
    results: list[dict[str, Any]] = []
    accepted_items: list[tuple[dict[str, Any], Path, dict[str, Any]]] = []
    final_failure_class: str | None = None
    final_failure_streak = 0
    stop_reason: str | None = None
    for rank, item in enumerate(selected, 1):
        if started is None:
            started = time.monotonic()
            started_utc = now_utc()
        if time.monotonic() - started >= NETWORK_WINDOW_SECONDS:
            stop_reason = "network_window_exhausted"
            break
        if response_used >= MAX_RESPONSE_BYTES:
            stop_reason = "response_budget_exhausted"
            break
        if previous_request is not None:
            wait = interval - (time.monotonic() - previous_request)
            if wait > 0:
                time.sleep(wait)
        attempt_records: list[dict[str, Any]] = []
        deadline = started + NETWORK_WINDOW_SECONDS
        direct = run_attempt(item, transport="direct", rank=rank, output=output, remaining_bytes=MAX_RESPONSE_BYTES - response_used, deadline=deadline)
        previous_request = time.monotonic()
        response_used += int(direct.get("wire_bytes") or 0)
        attempt_records.append(direct)
        chosen: dict[str, Any] | None = direct if direct.get("accepted") else None
        if direct.get("failure_class") == "local_write_error":
            stop_reason = "local_output_error"
        elif chosen is None and response_used < MAX_RESPONSE_BYTES:
            if time.monotonic() >= deadline:
                stop_reason = "network_window_exhausted"
                attempt_records.append({
                    "transport": "proxy",
                    "status": None,
                    "accepted": False,
                    "failure_class": "transport",
                    "failure_reasons": ["deadline_exhausted"],
                    "wire_bytes": 0,
                })
                proxy = None
            else:
                proxy = run_attempt(item, transport="proxy", rank=rank, output=output, remaining_bytes=MAX_RESPONSE_BYTES - response_used, deadline=deadline)
                previous_request = time.monotonic()
                response_used += int(proxy.get("wire_bytes") or 0)
                attempt_records.append(proxy)
                chosen = proxy if proxy.get("accepted") else None
                if proxy.get("failure_class") == "local_write_error":
                    stop_reason = "local_output_error"
        record = {
            "item": item,
            "attempts": attempt_records,
            "accepted": chosen is not None,
            "chosen_transport": chosen.get("transport") if chosen else None,
            "failure_class": None if chosen else (attempt_records[-1].get("failure_class") or "unknown"),
            "finished_utc": now_utc(),
        }
        results.append(record)
        if chosen is not None:
            body_path = Path(chosen["body_path"])
            final_path = output / "entities" / "raw" / f"{rank:03d}-{re.sub(r'[^A-Za-z0-9._-]+', '_', item['path'].strip('/'))}.jpg"
            final_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(body_path), str(final_path))
            chosen["body_path"] = str(final_path)
            chosen["raw_path"] = str(final_path)
            accepted_items.append((item, final_path, record))
            final_failure_class = None
            final_failure_streak = 0
        else:
            current_class = record["failure_class"] or "unknown"
            if current_class == final_failure_class:
                final_failure_streak += 1
            else:
                final_failure_class = current_class
                final_failure_streak = 1
            if final_failure_streak >= 3:
                stop_reason = f"three_consecutive_final_failures:{current_class}"
        if stop_reason:
            break

    source_map_path = output / "image-source-map.json"
    entries: list[dict[str, Any]] = []
    # The map hash is filled after writing the content.  Keep the map itself
    # self-contained and avoid inventing a hash before the final bytes exist.
    for item, final_path, _ in accepted_items:
        entries.append(make_source_entry(item, final_path))
    atomic_json(source_map_path, {"schema_version": 1, "kind": "related_official_image_integration_map", "items": entries})
    accepted_bytes = sum(int(item[1].stat().st_size) for item in accepted_items)
    final_workspace = workspace_bytes(ROOT)
    final_free = drive_free_bytes(ROOT)
    state = {
        "schema_version": 1,
        "kind": "direct_first_archive_transport_batch",
        "started_utc": started_utc,
        "finished_utc": now_utc(),
        "anchor_timestamp": ANCHOR,
        "selected": len(selected),
        "attempted": len(results),
        "accepted": len(accepted_items),
        "accepted_bytes": accepted_bytes,
        "response_bytes": response_used,
        "direct_attempts": sum(1 for record in results for attempt in record["attempts"] if attempt.get("transport") == "direct"),
        "proxy_attempts": sum(1 for record in results for attempt in record["attempts"] if attempt.get("transport") == "proxy"),
        "direct_accepted": sum(1 for record in results if record.get("chosen_transport") == "direct"),
        "proxy_accepted": sum(1 for record in results if record.get("chosen_transport") == "proxy"),
        "stop_reason": stop_reason,
        "workspace_bytes_after": final_workspace,
        "drive_free_bytes_after": final_free,
        "source_map": _relative(source_map_path),
        "results": results,
    }
    atomic_json(output / "batch-state.json", state)
    summary = {
        "schema_version": 1,
        "kind": "direct_first_archive_transport_summary",
        "selected": len(selected),
        "attempted": len(results),
        "accepted": len(accepted_items),
        "accepted_bytes": accepted_bytes,
        "response_bytes": response_used,
        "direct_attempts": state["direct_attempts"],
        "proxy_attempts": state["proxy_attempts"],
        "direct_accepted": state["direct_accepted"],
        "proxy_accepted": state["proxy_accepted"],
        "stop_reason": stop_reason,
        "source_map": state["source_map"],
        "network_policy": "direct --noproxy '*' first; proxy fallback only for non-local direct failure; no automatic curl retry",
    }
    atomic_json(output / "sanitized-summary.json", summary)
    (output / "sanitized-summary.md").write_text(
        "# Direct-first archive transport\n\n"
        f"Selected `{len(selected)}` entities and accepted `{len(accepted_items)}` (`{accepted_bytes}` bytes).\n\n"
        f"Direct attempts: `{state['direct_attempts']}`; proxy attempts: `{state['proxy_attempts']}`; "
        f"chosen direct: `{state['direct_accepted']}`; chosen proxy: `{state['proxy_accepted']}`.\n\n"
        f"Stop reason: `{stop_reason or 'selected batch completed'}`.\n",
        encoding="utf-8",
    )
    return state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cdx", type=Path, default=ROOT / "research/related-sites-20261014/regional-gallery/cdx/screen-assets-baseline.rows.json")
    parser.add_argument("--old-meta", type=Path, default=ROOT / "research/related-sites-20261014/regional-gallery/entities/meta")
    parser.add_argument("--manifest", type=Path, default=ROOT / "offline/build-manifest.json")
    parser.add_argument("--provenance", type=Path, default=ROOT / ".scratch/pages-resources-20261014-next/export-provenance.json")
    parser.add_argument("--output", type=Path, default=ROOT / "research/related-sites-20261014/regional-gallery-next")
    parser.add_argument("--interval", type=float, default=INTERVAL_SECONDS)
    parser.add_argument(
        "--max-workspace-bytes",
        type=int,
        default=None,
        help="optional workspace cap; omitted by default, while the D: free-space threshold remains enforced",
    )
    args = parser.parse_args(argv)
    try:
        state = run_batch(
            cdx_path=args.cdx.resolve(),
            old_meta_dir=args.old_meta.resolve(),
            manifest_path=args.manifest.resolve(),
            provenance_path=args.provenance.resolve(),
            output=args.output.resolve(),
            interval=max(0.0, args.interval),
            max_workspace_bytes=args.max_workspace_bytes,
        )
    except Exception as exc:
        print(f"archive_transport: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({key: state[key] for key in ("selected", "attempted", "accepted", "accepted_bytes", "response_bytes", "direct_attempts", "proxy_attempts", "direct_accepted", "proxy_accepted", "stop_reason")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

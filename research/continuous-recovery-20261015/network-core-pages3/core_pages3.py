"""Bounded CDX and replay recovery for the twelve LOCAL35 page targets.

This worker owns only the network-core-pages3 directory.  ``--prepare`` reads
the accepted local reconciliation and writes the exact candidate/query plan
without network access.  ``--execute`` performs the separately authorized
serial CDX/replay batch, keeping raw response evidence local and reports
sanitized.
"""

from __future__ import annotations

import argparse
import hashlib
import html as html_module
import json
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit, urlencode

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
RECONCILIATION = ROOT / "research/continuous-recovery-20261015/local-target-reconcile/reconciliation.json"
CURL = Path(r"C:\Windows\System32\curl.exe")
PROXY = "http://127.0.0.1:7890"
WAYBACK_HOSTS = {"web.archive.org", "wwwb-app0.archive.org"}
WAYBACK_BASE = "https://web.archive.org"
USER_AGENT = "wow-recovery-core-pages3/20261015"
EXPECTED_RECONCILIATION_SHA256 = "81f346c89100204d35448e5c1d20fcfa7532f3e9b7569b5edff2ea1886735016"

ANCHOR_TIMESTAMP = "20080512210044"
FROM_TIMESTAMP = "20040101000000"
TO_TIMESTAMP = ANCHOR_TIMESTAMP
CDX_LIMIT = 1000
CDX_COLUMNS = ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
REDIRECT_CODES = {301, 302, 303, 307, 308}
STOP_HTTP_CODES = {429, 503}

MAX_TARGETS = 12
MAX_ATTEMPTS = 32
WINDOW_SECONDS = 8 * 60
MIN_INTERVAL_SECONDS = 1.2
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY_BYTES = 64 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 16 * 1024 * 1024
DIRECT_CONNECT_SECONDS = 4
DIRECT_MAX_SECONDS = 12
PROXY_CONNECT_SECONDS = 8
PROXY_MAX_SECONDS = 20

NEWS_TARGETS = [
    "/news/wow-news2005.html",
    "/news/wow-news2004.html",
    "/news/wow-news-06-2005.html",
    "/news/wow-news-07-2005.html",
    "/news/wow-news-08-2005.html",
    "/news/wow-news-09-2005.html",
    "/news/wow-news-10-2005.html",
    "/news/wow-news-11-2005.html",
]
OTHER_TARGETS = [
    "/pvp/battlegrounds/battlegroups.html",
    "/burningcrusade/townhall/professions.html",
    "/ptr",
    "/wrath/artwork.xml",
]
TARGET_ORDER = NEWS_TARGETS + OTHER_TARGETS


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


def relative(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")[:160]


def disk_free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def parse_headers(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip("\r")
        match = re.match(r"^HTTP/(?:\d(?:\.\d)?|2)\s+(\d{3})(?:\s+(.*))?$", line, re.I)
        if match:
            current = {"status": int(match.group(1)), "reason": match.group(2) or "", "headers": {}}
            blocks.append(current)
            continue
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key in current["headers"]:
            current["headers"][key] = f"{current['headers'][key]}, {value}"
        else:
            current["headers"][key] = value
    return blocks


def source_blocks(header_text: str) -> list[dict[str, Any]]:
    return [block for block in parse_headers(header_text) if "connection established" not in block["reason"].lower()]


def response_header(blocks: list[dict[str, Any]], name: str) -> str | None:
    if not blocks:
        return None
    value = blocks[-1]["headers"].get(name.lower())
    return str(value) if value is not None else None


def response_status(blocks: list[dict[str, Any]], stdout: str) -> int | None:
    if blocks:
        return int(blocks[-1]["status"])
    match = re.fullmatch(r"[1-5]\d\d", stdout.strip())
    return int(match.group(0)) if match else None


def memento_iso(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        return value


def parse_timestamp(value: str | None) -> datetime | None:
    if not value or not re.fullmatch(r"\d{14}", value):
        return None
    try:
        return datetime.strptime(value, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def is_in_query_range(value: str | None) -> bool:
    return bool(value and FROM_TIMESTAMP <= value <= TO_TIMESTAMP)


def normalized_url_identity(value: str) -> tuple[str, str, int | None, str, str, str] | None:
    """Match only URL identity variants accepted by the recovery policy.

    HTTP default port 80 (and HTTPS default port 443) is equivalent to an
    omitted port within the same scheme and exact lower-cased host.  Bare and
    ``www`` official hosts remain separate origins, as do HTTP and HTTPS.
    Paths, query strings, and trailing slashes remain literal.
    """
    try:
        parsed = urlsplit(value)
        scheme = parsed.scheme.lower()
        host = (parsed.hostname or "").lower()
        if scheme not in {"http", "https"} or not host:
            return None
        port = parsed.port
        if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            port = None
        return (scheme, host, port, parsed.path, parsed.query, parsed.fragment)
    except ValueError:
        return None


def original_match_kind(observed: str, requested: str) -> str | None:
    if observed == requested:
        return "exact"
    observed_parts = urlsplit(observed)
    requested_parts = urlsplit(requested)
    if normalized_url_identity(observed) != normalized_url_identity(requested):
        return None
    variants: list[str] = []
    observed_port = observed_parts.port
    requested_port = requested_parts.port
    if observed_port != requested_port:
        if observed_parts.scheme.lower() == "http" and {observed_port, requested_port} == {None, 80}:
            variants.append("default_port_80")
        elif observed_parts.scheme.lower() == "https" and {observed_port, requested_port} == {None, 443}:
            variants.append("default_port_443")
        else:
            variants.append("normalized_default_port")
    return "+".join(variants) if variants else "normalized_equivalent"


def origin_exclusion_reason(observed: str, requested: str) -> str | None:
    """Explain why a captured original is excluded from same-origin candidates."""
    try:
        observed_parts = urlsplit(observed)
        requested_parts = urlsplit(requested)
    except ValueError:
        return "invalid_url"
    observed_scheme = observed_parts.scheme.lower()
    requested_scheme = requested_parts.scheme.lower()
    observed_host = (observed_parts.hostname or "").lower()
    requested_host = (requested_parts.hostname or "").lower()
    if not observed_scheme or not observed_host:
        return "invalid_url"
    if observed_scheme != requested_scheme:
        return "scheme_mismatch"
    if observed_host != requested_host:
        return "host_mismatch"
    if (
        observed_parts.path,
        observed_parts.query,
        observed_parts.fragment,
    ) != (
        requested_parts.path,
        requested_parts.query,
        requested_parts.fragment,
    ):
        return "path_query_fragment_mismatch"
    if normalized_url_identity(observed) == normalized_url_identity(requested):
        return None
    return "non_default_port_mismatch"


def other_origin_metadata(records: list[dict[str, str]], requested: str) -> dict[str, Any]:
    """Retain excluded origins as CDX metadata without making them candidates."""
    excluded: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        original = record.get("original", "")
        reason = origin_exclusion_reason(original, requested)
        if reason not in {"host_mismatch", "scheme_mismatch", "non_default_port_mismatch", "origin_mismatch"}:
            continue
        value = dict(record)
        value["record_index"] = index
        value["origin_exclusion_reason"] = reason
        excluded.append(value)
    return {
        "excluded_from_eligible_candidates": True,
        "record_count": len(excluded),
        "original_identities": sorted({row.get("original") for row in excluded if row.get("original")}),
        "records": excluded,
        "policy": {
            "same_scheme_required": True,
            "same_lower_cased_host_required": True,
            "only_default_port_equivalence": True,
            "bare_www_are_separate_origins": True,
            "http_https_are_separate_origins": True,
        },
    }


class TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.parts.append(data)


def html_info(body: bytes, content_type: str | None) -> dict[str, Any]:
    prefix = body.lstrip()[:200].lower()
    mime = (content_type or "").lower().split(";", 1)[0].strip()
    looks_html = mime in {"text/html", "application/xhtml+xml"} or prefix.startswith((b"<!doctype html", b"<html", b"<head"))
    info: dict[str, Any] = {"is_html": looks_html, "markers": [], "title": None, "parse_ok": None}
    if not looks_html:
        return info
    text = body[:2 * 1024 * 1024].decode("utf-8", errors="replace")
    lowered = text.lower()
    marker_probes = (
        ("wayback_machine", "wayback machine"),
        ("not_archived", "not archived"),
        ("no_captures", "no captures"),
        ("page_not_found", "page not found"),
        ("not_found", "not found"),
        ("error_404", "404"),
        ("page_cannot_be_found", "page cannot be found"),
    )
    info["markers"] = [name for name, needle in marker_probes if needle in lowered]
    parser = TitleParser()
    try:
        parser.feed(text)
        parser.close()
        info["parse_ok"] = True
        title = " ".join("".join(parser.parts).split())
        info["title"] = title or None
    except Exception as exc:  # pragma: no cover - response-dependent
        info["parse_ok"] = False
        info["parse_error"] = type(exc).__name__
    return info


def xml_info(body: bytes, content_type: str | None) -> dict[str, Any]:
    mime = (content_type or "").lower().split(";", 1)[0].strip()
    prefix = body.lstrip()[:200].lower()
    looks_xml = mime in {"application/xml", "text/xml", "application/rss+xml", "application/atom+xml"} or prefix.startswith(b"<?xml")
    info: dict[str, Any] = {"is_xml": looks_xml, "parse_ok": None, "root": None}
    if not looks_xml:
        return info
    try:
        root = ET.fromstring(body)
        info["parse_ok"] = True
        info["root"] = str(root.tag)
    except Exception as exc:  # pragma: no cover - response-dependent
        info["parse_ok"] = False
        info["parse_error"] = type(exc).__name__
    return info


def cdx_query_url(original_url: str) -> str:
    params = [
        ("url", original_url),
        ("from", FROM_TIMESTAMP),
        ("to", TO_TIMESTAMP),
        ("output", "json"),
        ("fl", ",".join(CDX_COLUMNS)),
        ("limit", str(CDX_LIMIT)),
        ("collapse", "digest"),
        ("matchType", "exact"),
    ]
    return f"{WAYBACK_BASE}/cdx/search/cdx?{urlencode(params)}"


def replay_url(capture: dict[str, Any]) -> str:
    return f"{WAYBACK_BASE}/web/{capture['timestamp']}id_/{capture['original']}"


def legal_wayback_replay(location: str | None, base_url: str) -> str | None:
    if not location:
        return None
    candidate = urljoin(base_url, location)
    parsed = urlsplit(candidate)
    if parsed.scheme not in {"http", "https"}:
        return None
    if (parsed.hostname or "").lower() not in WAYBACK_HOSTS:
        return None
    if not parsed.path.startswith("/web/"):
        return None
    return candidate


def parse_cdx_body(body: bytes) -> tuple[list[dict[str, str]], bool, str | None]:
    text = body.decode("utf-8", errors="replace")
    stripped = text.strip()
    if not stripped or stripped.lower() in {"[]", "no captures found", "no captures"}:
        return [], True, None
    records: list[dict[str, str]] = []
    try:
        payload = json.loads(text)
        if isinstance(payload, list):
            rows: list[Any] = payload
            if rows and isinstance(rows[0], list) and [str(x) for x in rows[0]] == CDX_COLUMNS:
                rows = rows[1:]
            for row in rows:
                if isinstance(row, dict):
                    records.append({key: str(row.get(key, "")) for key in CDX_COLUMNS})
                elif isinstance(row, list) and len(row) >= len(CDX_COLUMNS):
                    records.append({key: str(row[index]) for index, key in enumerate(CDX_COLUMNS)})
            return records, True, None
        if isinstance(payload, dict):
            rows = payload.get("records") or payload.get("captures") or []
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict):
                        records.append({key: str(row.get(key, "")) for key in CDX_COLUMNS})
                return records, True, None
        return [], False, "json_shape"
    except json.JSONDecodeError:
        pass
    lines = [line for line in text.splitlines() if line.strip()]
    for line in lines:
        fields = line.split("\t")
        if len(fields) < len(CDX_COLUMNS):
            return [], False, "non_json_cdx_row"
        records.append({key: fields[index] for index, key in enumerate(CDX_COLUMNS)})
    return records, True, None


def valid_cdx_records(records: list[dict[str, str]], original_url: str) -> list[dict[str, Any]]:
    valid: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        value = dict(record)
        value["record_index"] = index
        value["statuscode_int"] = int(record["statuscode"]) if record.get("statuscode", "").isdigit() else None
        value["within_query_range"] = is_in_query_range(record.get("timestamp"))
        value["original_match_kind"] = original_match_kind(record.get("original", ""), original_url)
        value["exact_original_match"] = value["original_match_kind"] == "exact"
        value["valid_replay_candidate"] = (
            value["within_query_range"]
            and value["original_match_kind"] is not None
            and value["statuscode_int"] in ({200} | REDIRECT_CODES)
            and parse_timestamp(record.get("timestamp")) is not None
        )
        if value["valid_replay_candidate"]:
            valid.append(value)
    return valid


def select_capture(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not records:
        return None
    return sorted(
        records,
        key=lambda row: (row["timestamp"], 1 if row.get("statuscode_int") == 200 else 0),
        reverse=True,
    )[0]


class RunState:
    def __init__(self, window_started_monotonic: float) -> None:
        self.window_started_monotonic = window_started_monotonic
        self.last_start_monotonic: float | None = None
        self.attempts = 0
        self.failed_attempts = 0
        self.source_responses = 0
        self.total_body_bytes = 0
        self.fail_streak = 0
        self.stop_reason: str | None = None
        self.stop_detail: dict[str, Any] = {}
        self.rate_limit: dict[str, Any] | None = None

    def check_limits(self) -> bool:
        if self.stop_reason:
            return False
        if self.attempts >= MAX_ATTEMPTS:
            self.stop_reason = "attempt_limit"
            self.stop_detail = {"max_attempts": MAX_ATTEMPTS}
            return False
        if time.monotonic() - self.window_started_monotonic >= WINDOW_SECONDS:
            self.stop_reason = "network_window_exhausted"
            self.stop_detail = {"window_seconds": WINDOW_SECONDS}
            return False
        if disk_free_bytes() < MIN_FREE_BYTES:
            self.stop_reason = "disk_free_below_threshold"
            self.stop_detail = {"minimum_free_bytes": MIN_FREE_BYTES}
            return False
        if self.total_body_bytes >= MAX_TOTAL_BODY_BYTES:
            self.stop_reason = "total_body_limit"
            self.stop_detail = {"max_total_body_bytes": MAX_TOTAL_BODY_BYTES}
            return False
        return True

    def start_slot(self) -> bool:
        if not self.check_limits():
            return False
        if self.last_start_monotonic is not None:
            wait = MIN_INTERVAL_SECONDS - (time.monotonic() - self.last_start_monotonic)
            if wait > 0:
                time.sleep(wait)
        if not self.check_limits():
            return False
        self.last_start_monotonic = time.monotonic()
        self.attempts += 1
        return True

    def note(self, status: int | None, curl_exit: int | None, body_bytes: int, transport_error: bool, retry_after: str | None) -> None:
        self.source_responses += int(status is not None)
        self.failed_attempts += int(transport_error)
        self.total_body_bytes += body_bytes
        if transport_error:
            self.fail_streak += 1
        else:
            self.fail_streak = 0
        if status in STOP_HTTP_CODES:
            self.rate_limit = {"status": status, "retry_after": retry_after}
            self.stop_reason = f"endpoint_status_{status}"
            self.stop_detail = {"status": status, "retry_after": retry_after}
        elif self.fail_streak >= 5:
            self.stop_reason = "five_consecutive_tls_or_transport_failures"
            self.stop_detail = {"failure_streak": self.fail_streak, "last_curl_exit": curl_exit, "last_source_status": status}
        elif body_bytes > MAX_ENTITY_BODY_BYTES:
            self.stop_reason = "single_entity_body_limit"
            self.stop_detail = {"body_bytes": body_bytes, "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES}
        elif self.total_body_bytes > MAX_TOTAL_BODY_BYTES:
            self.stop_reason = "total_body_limit"
            self.stop_detail = {"total_body_bytes": self.total_body_bytes, "max_total_body_bytes": MAX_TOTAL_BODY_BYTES}


def run_request(url: str, transport: str, kind: str, target_key: str, state: RunState, rank: int) -> dict[str, Any]:
    """Run one source request.  Every call consumes one global attempt slot."""
    if not state.start_slot():
        return {
            "executed": False,
            "transport": transport,
            "kind": kind,
            "target_key": target_key,
            "url": url,
            "attempt": rank,
            "unrequested_reason": state.stop_reason or "limit_before_request",
        }
    stem = f"{rank:02d}-{safe_name(target_key)}-{kind}-{transport}"
    headers_path = RAW / f"{stem}.headers.txt"
    body_path = RAW / f"{stem}.body"
    stderr_path = RAW / f"{stem}.stderr.txt"
    trace_path = RAW / f"{stem}.trace.txt"
    metrics_path = RAW / f"{stem}.metrics.txt"
    if transport == "direct":
        transport_args = ["--proxy", "", "--noproxy", "*"]
        connect_timeout, max_time = DIRECT_CONNECT_SECONDS, DIRECT_MAX_SECONDS
    else:
        transport_args = ["--proxy", PROXY, "--noproxy", ""]
        connect_timeout, max_time = PROXY_CONNECT_SECONDS, PROXY_MAX_SECONDS
    command = [
        str(CURL),
        *transport_args,
        "--connect-timeout", str(connect_timeout),
        "--max-time", str(max_time),
        "--max-redirs", "0",
        "--max-filesize", str(MAX_ENTITY_BODY_BYTES),
        "--silent", "--show-error",
        "--trace-time", "--trace-ascii", str(trace_path),
        "--dump-header", str(headers_path),
        "--output", str(body_path),
        "--write-out", "%{http_code}",
        "--user-agent", USER_AGENT,
        url,
    ]
    started = now_utc()
    start_monotonic = time.monotonic()
    stdout = ""
    curl_exit: int | None = None
    try:
        completed = subprocess.run(
            command,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=stderr_path.open("wb"),
            timeout=max_time + 6,
            check=False,
        )
        stdout = completed.stdout.decode("ascii", errors="replace").strip()
        curl_exit = completed.returncode
    except Exception as exc:  # pragma: no cover - OS/process dependent
        stderr_path.write_text(type(exc).__name__ + ": " + str(exc), encoding="utf-8")
    finished = now_utc()
    if not headers_path.exists():
        headers_path.write_text("", encoding="iso-8859-1")
    if not body_path.exists():
        body_path.write_bytes(b"")
    header_text = headers_path.read_text(encoding="iso-8859-1", errors="replace")
    parsed_blocks = parse_headers(header_text)
    blocks = source_blocks(header_text)
    status = response_status(blocks, stdout)
    body = body_path.read_bytes()
    content_type = response_header(blocks, "content-type")
    location = response_header(blocks, "location")
    retry_after = response_header(blocks, "retry-after")
    memento = memento_iso(response_header(blocks, "memento-datetime"))
    transport_error = status is None or curl_exit != 0
    state.note(status, curl_exit, len(body), transport_error, retry_after)
    metrics_path.write_text(stdout + "\n", encoding="ascii", errors="replace")
    record: dict[str, Any] = {
        "executed": True,
        "attempt": rank,
        "kind": kind,
        "target_key": target_key,
        "transport": transport,
        "url": url,
        "started_utc": started,
        "finished_utc": finished,
        "duration_ms": round((time.monotonic() - start_monotonic) * 1000, 1),
        "curl_exit": curl_exit,
        "source_status": status,
        "connect_status": next((block["status"] for block in parsed_blocks if "connection established" in block["reason"].lower()), None),
        "content_type": content_type,
        "location": location,
        "retry_after": retry_after,
        "memento_datetime": memento,
        "redirects_requested": 0,
        "automatic_redirects": 0,
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "transport_error": transport_error,
        "transport_reason": ("no_http_status" if status is None else f"curl_exit_{curl_exit}") if transport_error else None,
        "raw": {
            "headers": relative(headers_path),
            "body": relative(body_path),
            "stderr": relative(stderr_path),
            "trace": relative(trace_path),
            "metrics": relative(metrics_path),
        },
    }
    if kind == "cdx":
        records, parse_valid, parse_error = parse_cdx_body(body) if status == 200 and not transport_error else ([], False, "no_200_source_response")
        record["cdx_parse_valid"] = parse_valid
        record["cdx_parse_error"] = parse_error
        record["cdx_records"] = records
    else:
        record["html"] = html_info(body, content_type)
        record["xml"] = xml_info(body, content_type)
    return record


def source_attempt_view(attempt: dict[str, Any]) -> dict[str, Any]:
    """Drop parsed CDX rows from the public per-attempt report; raw remains local."""
    return {key: value for key, value in attempt.items() if key not in {"cdx_records", "cdx_valid_records"}}


def derive_candidates() -> dict[str, Any]:
    observed_sha = sha256_file(RECONCILIATION)
    if observed_sha != EXPECTED_RECONCILIATION_SHA256:
        raise RuntimeError(f"reconciliation SHA mismatch: expected {EXPECTED_RECONCILIATION_SHA256}, got {observed_sha}")
    data = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    rows = {str(row.get("target")): row for row in data.get("rows", [])}
    selected: list[dict[str, Any]] = []
    for rank, target in enumerate(TARGET_ORDER, start=1):
        if target not in rows:
            raise RuntimeError(f"missing LOCAL35 target row: {target}")
        row = rows[target]
        menu = row.get("source_menu") or []
        if not menu:
            raise RuntimeError(f"target has no source_menu evidence: {target}")
        trimmed_hrefs = [str(item.get("href") or "").strip() for item in menu]
        if target == "/ptr":
            if "/ptr/" not in trimmed_hrefs:
                raise RuntimeError("PTR raw menu href /ptr/ missing")
            raw_href = "/ptr/"
        else:
            matches = [href for href in trimmed_hrefs if href == target]
            if not matches:
                raise RuntimeError(f"raw menu href does not exactly match target: {target} / {trimmed_hrefs}")
            raw_href = matches[0]
        if not raw_href.startswith("/") or any(char in raw_href for char in "\r\n"):
            raise RuntimeError(f"invalid raw menu href: {raw_href!r}")
        query_original_url = "http://www.worldofwarcraft.com" + raw_href
        evidence = [
            {
                "record_id": item.get("record_id"),
                "source_menu": item.get("source_menu"),
                "source_line": item.get("source_line"),
                "label": item.get("label"),
                "href": item.get("href"),
                "source_role": item.get("source_role"),
            }
            for item in menu
        ]
        selected.append(
            {
                "candidate_rank": rank,
                "target": target,
                "normalized_target": target,
                "row_exact_original_url": row.get("exact_original_url"),
                "query_original_url": query_original_url,
                "raw_menu_href": raw_href,
                "classification": row.get("classification"),
                "priority": row.get("priority"),
                "source_menu": evidence,
                "recommended_capture_constraints": row.get("recommended_capture_constraints"),
                "next_action": row.get("next_action"),
                "cdx_query_url": cdx_query_url(query_original_url),
            }
        )
    if len(selected) != MAX_TARGETS:
        raise RuntimeError(f"expected {MAX_TARGETS} candidates, got {len(selected)}")
    return {
        "schema": "wow-recovery.network-core-pages3-candidates.v1",
        "selection": {
            "source_reconciliation": str(RECONCILIATION.relative_to(ROOT)).replace("\\", "/"),
            "source_reconciliation_sha256": observed_sha,
            "criteria": "LOCAL35 accepted exact menu targets; eight News HTML first, then battlegroups, BC professions, PTR, Wrath artwork",
            "target_count": len(selected),
            "rss_targets_deferred": 23,
        },
        "query_scope": {
            "endpoint": f"{WAYBACK_BASE}/cdx/search/cdx",
            "from": FROM_TIMESTAMP,
            "to": TO_TIMESTAMP,
            "anchor_timestamp": ANCHOR_TIMESTAMP,
            "columns": CDX_COLUMNS,
            "limit": CDX_LIMIT,
            "collapse": "digest",
            "matchType": "exact",
            "selection_rule": "same-origin normalized match within query range: scheme and lower-cased host must match; only default port is normalized; path/query/fragment remain literal; status 200 or Wayback redirect; closest timestamp at or before anchor",
            "empty_valid_set_semantics": "query-range evidence only; does not assert permanent unarchived status",
        },
        "selected": selected,
    }


def prepare() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    candidates = derive_candidates()
    write_json(OUT / "candidates.json", candidates)
    disk = disk_free_bytes()
    write_json(
        OUT / "plan.json",
        {
            "schema": "wow-recovery.network-core-pages3-plan.v1",
            "mode": "plan_only",
            "prepared_utc": now_utc(),
            "input_sha256": {"reconciliation": candidates["selection"]["source_reconciliation_sha256"]},
            "disk_free_bytes": disk,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "network_requests": 0,
            "policy": {
                "direct_first_cd_x": True,
                "direct_connect_timeout_seconds": DIRECT_CONNECT_SECONDS,
                "direct_total_timeout_seconds": DIRECT_MAX_SECONDS,
                "proxy": PROXY,
                "proxy_connect_timeout_seconds": PROXY_CONNECT_SECONDS,
                "proxy_total_timeout_seconds": PROXY_MAX_SECONDS,
                "max_attempts": MAX_ATTEMPTS,
                "window_seconds": WINDOW_SECONDS,
                "minimum_interval_seconds": MIN_INTERVAL_SECONDS,
                "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
                "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
                "redirects_requested": 0,
                "max_manual_wayback_replay_redirect_hops": 1,
                "stop_http_codes": sorted(STOP_HTTP_CODES),
                "tls_verification": "enabled_by_curl_default",
            },
            "ready": disk >= MIN_FREE_BYTES,
        },
    )
    print(json.dumps({"mode": "plan_only", "target_count": len(candidates["selected"]), "network_requests": 0, "input_sha256": candidates["selection"]["source_reconciliation_sha256"]}, ensure_ascii=False))
    return 0


def classify_replay(final: dict[str, Any] | None, redirect_note: str | None = None) -> tuple[str, dict[str, Any]]:
    if final is None:
        return "not_requested", {"reason": redirect_note or "no_replay_request"}
    status = final.get("source_status")
    if final.get("transport_error"):
        return "transport_error", {"reason": final.get("transport_reason") or "curl_or_tls_failure", "source_status": status}
    if status in STOP_HTTP_CODES:
        return "rate_limited", {"source_status": status, "retry_after": final.get("retry_after")}
    if status == 404:
        return "not_archived", {"reason": "replay_http_404", "source_status": status, "content_type": final.get("content_type")}
    if status in REDIRECT_CODES:
        return "redirect_unfollowed", {"reason": redirect_note or "redirect_follow_not_available", "source_status": status, "location": final.get("location")}
    if status != 200:
        return "http_response", {"reason": "non_200_replay", "source_status": status, "content_type": final.get("content_type")}
    html_info_value = final.get("html") or {}
    xml_info_value = final.get("xml") or {}
    markers = set(html_info_value.get("markers") or [])
    if markers.intersection({"wayback_machine", "not_archived", "no_captures", "page_not_found", "page_cannot_be_found"}):
        return "not_archived", {"reason": "wayback_not_archived_or_error_body", "source_status": status, "content_type": final.get("content_type"), "html": html_info_value}
    if html_info_value.get("is_html"):
        if not final.get("body_bytes"):
            return "soft404", {"reason": "empty_html_body", "source_status": status, "html": html_info_value}
        return "valid_html", {"source_status": status, "content_type": final.get("content_type"), "html": html_info_value}
    if xml_info_value.get("is_xml"):
        if xml_info_value.get("parse_ok"):
            return "valid_xml", {"source_status": status, "content_type": final.get("content_type"), "xml": xml_info_value}
        return "soft404", {"reason": "xml_parse_failed", "source_status": status, "content_type": final.get("content_type"), "xml": xml_info_value}
    if final.get("body_bytes") == 0:
        return "soft404", {"reason": "empty_200_body", "source_status": status, "content_type": final.get("content_type")}
    return "valid_content", {"source_status": status, "content_type": final.get("content_type"), "body_prefix": "opaque"}


def target_result(candidate: dict[str, Any], query_attempts: list[dict[str, Any]], selected: dict[str, Any] | None, replay_attempts: list[dict[str, Any]], redirect_note: str | None, query_note: str | None = None) -> dict[str, Any]:
    query_attempt = query_attempts[-1] if query_attempts else None
    executed_replays = [attempt for attempt in replay_attempts if attempt.get("executed")]
    final = executed_replays[-1] if executed_replays else None
    if query_attempt is None:
        category = "not_requested"
        detail = {"reason": query_note or "query_not_requested"}
    elif not query_attempt.get("executed"):
        category = "not_requested"
        detail = {"reason": query_attempt.get("unrequested_reason") or query_note or "query_not_requested"}
    elif query_attempt.get("transport_error"):
        category = "transport_error"
        detail = {"reason": query_attempt.get("transport_reason") or "query_transport_error", "source_status": query_attempt.get("source_status")}
    elif query_attempt.get("source_status") in STOP_HTTP_CODES:
        category = "rate_limited"
        detail = {"source_status": query_attempt.get("source_status"), "retry_after": query_attempt.get("retry_after")}
    elif not query_attempt.get("cdx_parse_valid"):
        category = "cdx_invalid"
        detail = {"reason": query_attempt.get("cdx_parse_error") or "cdx_parse_failed", "source_status": query_attempt.get("source_status")}
    elif selected is None:
        records = query_attempt.get("cdx_records") or []
        category = "cdx_empty_in_range" if not records else "cdx_no_valid_capture"
        detail = {
            "reason": "no exact status-200-or-wayback-redirect capture in requested range",
            "capture_index_count": len(records),
            "permanent_unarchived_claim": False,
        }
    elif final is None:
        category = "not_requested"
        detail = {"reason": redirect_note or "replay_not_requested", "selected_capture": selected}
    else:
        category, detail = classify_replay(final, redirect_note)
        detail = {**detail, "selected_capture": selected}
    actual = final.get("memento_datetime") if final else None
    if executed_replays:
        unrequested_reason = redirect_note
    elif query_attempt is None or not query_attempt.get("executed"):
        unrequested_reason = query_note or query_attempt.get("unrequested_reason") if query_attempt else (query_note or "query_not_requested")
    elif query_attempt.get("transport_error"):
        unrequested_reason = "no_replay_after_query_transport_error"
    elif selected is None:
        unrequested_reason = "no_replay_after_no_valid_cdx_capture"
    else:
        unrequested_reason = redirect_note or "replay_not_requested"
    return {
        "candidate_rank": candidate["candidate_rank"],
        "target": candidate["target"],
        "normalized_target": candidate["normalized_target"],
        "row_exact_original_url": candidate["row_exact_original_url"],
        "query_original_url": candidate["query_original_url"],
        "raw_menu_href": candidate["raw_menu_href"],
        "classification_local": candidate["classification"],
        "priority": candidate["priority"],
        "source_menu": candidate["source_menu"],
        "category": category,
        "detail": detail,
        "cdx": {
            "query_url": candidate["cdx_query_url"],
            "attempts": [source_attempt_view(attempt) for attempt in query_attempts],
            "source_status": query_attempt.get("source_status") if query_attempt else None,
            "source_response_count": sum(attempt.get("source_status") is not None for attempt in query_attempts),
            "capture_index_count": query_attempt.get("cdx_capture_index_count", len(query_attempt.get("cdx_records") or [])) if query_attempt else 0,
            "valid_capture_count": query_attempt.get("cdx_valid_capture_count", sum(bool(row.get("valid_replay_candidate")) for row in (query_attempt.get("cdx_records") or []))) if query_attempt else None,
            "capture_records": (query_attempt.get("cdx_records") or []) if query_attempt else [],
            "selected_capture": selected,
        },
        "replay_attempt_count": len(executed_replays),
        "replay_source_response_count": sum(attempt.get("source_status") is not None for attempt in replay_attempts),
        "replay_hops": [source_attempt_view(attempt) for attempt in replay_attempts],
        "actual_memento_or_null": actual,
        "final_source_status": final.get("source_status") if final else None,
        "final_content_type": final.get("content_type") if final else None,
        "final_body_bytes": final.get("body_bytes", 0) if final else 0,
        "final_body_sha256": final.get("body_sha256") if final else None,
        "unrequested_reason": unrequested_reason,
    }


def public_mapping(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for result in results:
        if result["category"] not in {"valid_html", "valid_xml", "valid_content"}:
            continue
        hops = result.get("replay_hops") or []
        final = hops[-1] if hops else {}
        values.append(
            {
                "target": result["target"],
                "query_original_url": result["query_original_url"],
                "actual_memento": result["actual_memento_or_null"],
                "source_status": result["final_source_status"],
                "content_type": result["final_content_type"],
                "body_bytes": result["final_body_bytes"],
                "body_sha256": result["final_body_sha256"],
                "raw_body_path": (final.get("raw") or {}).get("body"),
                "raw_headers_path": (final.get("raw") or {}).get("headers"),
                "action": "review source mapping before any integration; entity remains only in this batch raw directory",
            }
        )
    return values


def same_capture(left: dict[str, Any] | None, right: dict[str, Any] | None) -> bool:
    if not left or not right:
        return False
    return all(left.get(key) == right.get(key) for key in ("timestamp", "original", "statuscode", "digest"))


def reconcile_offline_cdx_result(result: dict[str, Any]) -> dict[str, Any]:
    """Reconcile already captured CDX rows without changing replay evidence."""
    cdx = result.setdefault("cdx", {})
    records = cdx.get("capture_records") or []
    literal_count = cdx.get("literal_valid_capture_count_before_normalization", cdx.get("valid_capture_count") or 0)
    eligible = valid_cdx_records(records, result["query_original_url"])
    preferred = select_capture(eligible)
    cdx["literal_valid_capture_count_before_normalization"] = literal_count
    cdx["valid_capture_count"] = len(eligible)
    cdx["eligible_capture_records"] = eligible
    cdx["corrected_preferred_candidate"] = preferred
    cdx["observed_original_identities"] = sorted({row.get("original") for row in eligible if row.get("original")})
    cdx["other_origin_metadata"] = other_origin_metadata(records, result["query_original_url"])
    cdx["original_match_policy"] = {
        "http_default_port_equivalent": True,
        "https_default_port_equivalent": True,
        "official_www_bare_host_equivalent_for_matching": False,
        "official_www_bare_host_separate_origins": True,
        "http_https_separate_origins": True,
        "host_case_fold": True,
        "observed_original_preserved": True,
        "path_and_trailing_slash_literal": True,
        "query_and_fragment_literal": True,
    }
    previous_selected = cdx.get("selected_capture")
    if previous_selected is not None:
        cdx["selection_limitation"] = (
            "Replay binding preserved from the original execution; normalized preferred candidate agrees with it."
            if same_capture(previous_selected, preferred)
            else "Replay binding preserved from the original execution; corrected preferred candidate was not applied offline."
        )
    elif preferred is not None:
        cdx["selection_limitation"] = "Corrected CDX candidate retained for parent review; no replay was issued during offline correction."
    else:
        cdx["selection_limitation"] = "No normalized eligible CDX candidate in the requested query range."
    result["corrected_candidate_only"] = bool(result.get("corrected_candidate_only")) or result.get("category") == "indexed_candidates_not_replayed"
    if result.get("category") == "cdx_no_valid_capture" and preferred is not None:
        result["category"] = "indexed_candidates_not_replayed"
        result["corrected_candidate_only"] = True
        result["detail"] = {
            "reason": "normalized CDX candidates available; replay deferred for parent decision",
            "capture_index_count": len(records),
            "literal_valid_capture_count_before_normalization": literal_count,
            "valid_capture_count": len(eligible),
            "permanent_unarchived_claim": False,
            "corrected_preferred_candidate": preferred,
            "selection_limitation": cdx["selection_limitation"],
        }
        result["unrequested_reason"] = "replay_deferred_for_parent_decision_after_normalized_cdx_candidate"
    return result


def write_outputs(candidates: dict[str, Any], results: list[dict[str, Any]], state: RunState, started_utc: str, request_window_finished_utc: str, report_updated_utc: str, disk_before: int, disk_after: int, confirmed_transport: str) -> None:
    counts: dict[str, int] = {}
    for result in results:
        counts[result["category"]] = counts.get(result["category"], 0) + 1
    query_records = sum(result["cdx"]["capture_index_count"] for result in results)
    selected_count = sum(result["cdx"]["selected_capture"] is not None for result in results)
    valid_entities = public_mapping(results)
    cdx_source_responses = sum(result["cdx"]["source_response_count"] for result in results)
    replay_source_responses = sum(result["replay_source_response_count"] for result in results)
    report = {
        "schema": "wow-recovery.network-core-pages3-batch-report.v1",
        "mode": "executed",
        "started_utc": started_utc,
        "finished_utc": request_window_finished_utc,
        "request_window_finished_utc": request_window_finished_utc,
        "report_updated_utc": report_updated_utc,
        "inputs": {
            "reconciliation": str(RECONCILIATION.relative_to(ROOT)).replace("\\", "/"),
            "reconciliation_sha256": sha256_file(RECONCILIATION),
            "candidates": "research/continuous-recovery-20261015/network-core-pages3/candidates.json",
            "candidates_sha256": sha256_file(OUT / "candidates.json"),
        },
        "policy": {
            "direct_first_cd_x": True,
            "direct_connect_timeout_seconds": DIRECT_CONNECT_SECONDS,
            "direct_total_timeout_seconds": DIRECT_MAX_SECONDS,
            "proxy": PROXY,
            "tls_verification": "enabled_by_curl_default",
            "max_attempts": MAX_ATTEMPTS,
            "window_seconds": WINDOW_SECONDS,
            "minimum_interval_seconds": MIN_INTERVAL_SECONDS,
            "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
            "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
            "max_manual_wayback_replay_redirect_hops": 1,
            "redirects_requested": 0,
            "stop_http_codes": sorted(STOP_HTTP_CODES),
        },
        "preflight": {
            "drive": "D:",
            "disk_free_bytes_before": disk_before,
            "disk_free_bytes_after": disk_after,
            "minimum_free_bytes": MIN_FREE_BYTES,
        },
        "transport": {"confirmed_transport_after_first_cdx": confirmed_transport, "curl": str(CURL)},
        "target_count": len(results),
        "unique_target_count": len({result["target"] for result in results}),
        "category_counts": counts,
        "capture_index_count": query_records,
        "selected_capture_count": selected_count,
        "valid_entity_count": len(valid_entities),
        "cdx_source_response_count": cdx_source_responses,
        "replay_source_response_count": replay_source_responses,
        "source_request_count": state.attempts,
        "transport_attempt_count": state.attempts,
        "failed_attempt_count": state.failed_attempts,
        "source_response_count": state.source_responses,
        "total_body_bytes": state.total_body_bytes,
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "rate_limit": state.rate_limit,
        "results": results,
        "payload_source_map_count": len(valid_entities),
        "raw_evidence_note": "Raw headers, traces, stderr, and bodies remain only below this batch raw directory. A zero-byte body created after a transport failure is a local placeholder, not a source response body. CDX length fields are capture-index metadata and are never used as payload byte lengths.",
    }
    write_json(OUT / "batch-report.json", report)
    summary = {
        "schema": "wow-recovery.network-core-pages3-sanitized-summary.v1",
        "mode": "executed",
        "started_utc": started_utc,
        "finished_utc": request_window_finished_utc,
        "request_window_finished_utc": request_window_finished_utc,
        "report_updated_utc": report_updated_utc,
        "input_sha256": {"reconciliation": sha256_file(RECONCILIATION)},
        "target_count": len(results),
        "category_counts": counts,
        "capture_index_count": query_records,
        "selected_capture_count": selected_count,
        "valid_entity_count": len(valid_entities),
        "cdx_source_response_count": cdx_source_responses,
        "replay_source_response_count": replay_source_responses,
        "source_request_count": state.attempts,
        "transport_attempt_count": state.attempts,
        "failed_attempt_count": state.failed_attempts,
        "source_response_count": state.source_responses,
        "total_body_bytes": state.total_body_bytes,
        "disk_free_bytes_before": disk_before,
        "disk_free_bytes_after": disk_after,
        "stop_reason": state.stop_reason,
        "confirmed_transport_after_first_cdx": confirmed_transport,
        "targets": [
            {
                "candidate_rank": result["candidate_rank"],
                "target": result["target"],
                "query_original_url": result["query_original_url"],
                "category": result["category"],
                "cdx_source_status": result["cdx"]["source_status"],
                "cdx_source_response_count": result["cdx"]["source_response_count"],
                "source_status": result["final_source_status"],
                "actual_memento_or_null": result["actual_memento_or_null"],
                "content_type": result["final_content_type"],
                "body_bytes": result["final_body_bytes"],
                "body_sha256": result["final_body_sha256"],
                "capture_index_count": result["cdx"]["capture_index_count"],
                "valid_capture_count": result["cdx"]["valid_capture_count"],
                "selected_capture_timestamp": (result["cdx"]["selected_capture"] or {}).get("timestamp"),
                "unrequested_reason": result["unrequested_reason"],
            }
            for result in results
        ],
        "raw_evidence_note": report["raw_evidence_note"],
    }
    write_json(OUT / "sanitized-summary.json", summary)
    write_json(
        OUT / "payload-source-map.json",
        {
            "schema": "wow-recovery.network-core-pages3-payload-source-map.v1",
            "generated_utc": report_updated_utc,
            "only_real_valid_entities": True,
            "entries": valid_entities,
        },
    )
    lines = [
        "# Network core pages 3 — sanitized recovery summary",
        "",
        f"Accepted LOCAL35 reconciliation SHA-256: `{sha256_file(RECONCILIATION)}`.",
        f"Request window: `{started_utc}` to `{request_window_finished_utc}`; report updated: `{report_updated_utc}`.",
        f"Attempts: `{state.attempts}`; source HTTP responses: `{state.source_responses}`; failed attempts: `{state.failed_attempts}`; CDX capture-index rows: `{query_records}`; selected captures: `{selected_count}`; valid entities: `{len(valid_entities)}`.",
        f"Categories: " + ", ".join(f"`{key}` {value}" for key, value in sorted(counts.items())) + ".",
        f"Disk free before/after: `{disk_before}` / `{disk_after}` bytes; stop reason: `{state.stop_reason or 'batch completed'}`.",
        "",
        "Actual Memento values below come only from valid replay response headers. CDX timestamps and request hints are recorded separately.",
        "",
        "| # | target | query original URL | category | CDX HTTP | replay HTTP | actual Memento | payload bytes | payload SHA-256 | CDX rows | unrequested reason |",
        "|---:|---|---|---|---:|---:|---|---:|---|---:|---|",
    ]
    for result in results:
        lines.append(
            f"| {result['candidate_rank']} | `{result['target']}` | `{result['query_original_url']}` | `{result['category']}` | "
            f"{result['cdx']['source_status'] or ''} | {result['final_source_status'] or ''} | `{result['actual_memento_or_null'] or ''}` | {result['final_body_bytes']} | "
            f"`{result['final_body_sha256'] or ''}` | {result['cdx']['capture_index_count']} | `{result['unrequested_reason'] or ''}` |"
        )
    lines.extend([
        "",
        "Bodies and original headers/traces remain only below this batch's raw directory. Valid entities are listed in `payload-source-map.json` for review; no entity was copied into the offline mirror.",
        "",
    ])
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")


def execute() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    candidates = derive_candidates()
    write_json(OUT / "candidates.json", candidates)
    disk_before = disk_free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D: free space {disk_before} below threshold {MIN_FREE_BYTES}")
    window_started_monotonic = time.monotonic()
    started_utc = now_utc()
    state = RunState(window_started_monotonic)
    results: list[dict[str, Any]] = []
    confirmed_transport = "unconfirmed"

    for index, candidate in enumerate(candidates["selected"]):
        query_attempts: list[dict[str, Any]] = []
        replay_attempts: list[dict[str, Any]] = []
        selected: dict[str, Any] | None = None
        redirect_note: str | None = None
        query_note: str | None = None
        if not state.check_limits():
            query_note = state.stop_reason or "limit_before_query"
            results.append(target_result(candidate, [], None, [], state.stop_reason, query_note))
            continue

        if index == 0:
            direct = run_request(candidate["cdx_query_url"], "direct", "cdx", candidate["target"], state, state.attempts + 1)
            query_attempts.append(direct)
            if not direct.get("executed"):
                confirmed_transport = "proxy_after_direct_not_requested"
            elif direct.get("source_status") in STOP_HTTP_CODES:
                confirmed_transport = "direct_rate_limited"
            elif direct.get("transport_error"):
                if state.stop_reason:
                    confirmed_transport = "proxy_not_attempted_after_stop"
                else:
                    proxy = run_request(candidate["cdx_query_url"], "proxy", "cdx", candidate["target"], state, state.attempts + 1)
                    query_attempts.append(proxy)
                    if proxy.get("executed"):
                        confirmed_transport = "proxy"
            else:
                confirmed_transport = "direct"
        else:
            transport = "proxy" if confirmed_transport.startswith("proxy") else confirmed_transport
            if transport not in {"direct", "proxy"}:
                transport = "proxy"
            query_attempts.append(run_request(candidate["cdx_query_url"], transport, "cdx", candidate["target"], state, state.attempts + 1))

        query_attempt = query_attempts[-1] if query_attempts else None
        if query_attempt and query_attempt.get("executed"):
            records = query_attempt.get("cdx_records") or []
            valid = valid_cdx_records(records, candidate["query_original_url"])
            query_attempt["cdx_capture_index_count"] = len(records)
            query_attempt["cdx_valid_capture_count"] = len(valid)
            query_attempt["cdx_valid_records"] = valid
            selected = select_capture(valid)
            if query_attempt.get("source_status") in STOP_HTTP_CODES:
                query_note = state.stop_reason
            elif selected is not None and not state.stop_reason:
                replay = run_request(replay_url(selected), confirmed_transport if confirmed_transport in {"direct", "proxy"} else "proxy", "replay", candidate["target"], state, state.attempts + 1)
                replay_attempts.append(replay)
                while replay.get("executed") and not replay.get("transport_error") and replay.get("source_status") in REDIRECT_CODES:
                    next_url = legal_wayback_replay(replay.get("location"), replay.get("url") or "")
                    if not next_url:
                        redirect_note = "redirect_location_not_same_wayback_host"
                        break
                    if len([item for item in replay_attempts if item.get("executed")]) >= 2:
                        redirect_note = "manual_wayback_redirect_hop_limit"
                        break
                    if not state.check_limits():
                        redirect_note = state.stop_reason or "limit_before_manual_redirect_follow"
                        break
                    replay = run_request(next_url, replay.get("transport") or "proxy", "replay-follow", candidate["target"], state, state.attempts + 1)
                    replay_attempts.append(replay)
                    if not replay.get("executed"):
                        redirect_note = replay.get("unrequested_reason")
                        break
        result = target_result(candidate, query_attempts, selected, replay_attempts, redirect_note, query_note)
        results.append(result)
        if state.stop_reason:
            continue

    results.sort(key=lambda item: item["candidate_rank"])
    request_window_finished_utc = now_utc()
    report_updated_utc = now_utc()
    disk_after = disk_free_bytes()
    write_outputs(candidates, results, state, started_utc, request_window_finished_utc, report_updated_utc, disk_before, disk_after, confirmed_transport)
    print(json.dumps({
        "target_count": len(results),
        "category_counts": {key: sum(item["category"] == key for item in results) for key in sorted({item["category"] for item in results})},
        "attempts": state.attempts,
        "source_responses": state.source_responses,
        "capture_index_count": sum(item["cdx"]["capture_index_count"] for item in results),
        "valid_entities": sum(item["category"] in {"valid_html", "valid_xml", "valid_content"} for item in results),
        "total_body_bytes": state.total_body_bytes,
        "stop_reason": state.stop_reason,
        "confirmed_transport": confirmed_transport,
    }, ensure_ascii=False))
    return 0


def augment_existing() -> int:
    """Repair derived report semantics from local JSON only; never invokes curl."""
    report_path = OUT / "batch-report.json"
    summary_path = OUT / "sanitized-summary.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    request_finished = report.get("request_window_finished_utc") or report.get("finished_utc")
    report_updated = now_utc()
    cdx_source_responses = 0
    replay_source_responses = 0
    for result in report.get("results") or []:
        reconcile_offline_cdx_result(result)
        cdx = result.setdefault("cdx", {})
        query_attempts = cdx.get("attempts") or []
        cdx["source_status"] = query_attempts[-1].get("source_status") if query_attempts else None
        cdx["source_response_count"] = sum(attempt.get("source_status") is not None for attempt in query_attempts)
        result["replay_source_response_count"] = sum(attempt.get("source_status") is not None for attempt in (result.get("replay_hops") or []))
        if result.get("category") == "indexed_candidates_not_replayed":
            result["unrequested_reason"] = "replay_deferred_for_parent_decision_after_normalized_cdx_candidate"
        if not result.get("unrequested_reason"):
            if result.get("replay_attempt_count", 0) == 0:
                if result.get("category") == "transport_error":
                    result["unrequested_reason"] = "no_replay_after_query_transport_error"
                elif result.get("category") in {"cdx_no_valid_capture", "cdx_empty_in_range"}:
                    result["unrequested_reason"] = "no_replay_after_no_valid_cdx_capture"
                elif result.get("category") == "cdx_invalid":
                    result["unrequested_reason"] = "no_replay_after_invalid_cdx"
                elif result.get("category") == "not_requested":
                    result["unrequested_reason"] = "query_not_requested"
        cdx_source_responses += cdx["source_response_count"]
        replay_source_responses += result["replay_source_response_count"]
    counts: dict[str, int] = {}
    for result in report.get("results") or []:
        counts[result["category"]] = counts.get(result["category"], 0) + 1
    normalized_eligible_count = sum(len(result["cdx"].get("eligible_capture_records") or []) for result in report.get("results") or [])
    other_origin_count = sum((result["cdx"].get("other_origin_metadata") or {}).get("record_count", 0) for result in report.get("results") or [])
    corrected_candidate_only_count = sum(bool(result.get("corrected_candidate_only")) for result in report.get("results") or [])
    corrected_preferred_count = sum(result["cdx"].get("corrected_preferred_candidate") is not None for result in report.get("results") or [])
    selected_count = sum(result["cdx"].get("selected_capture") is not None for result in report.get("results") or [])
    candidates_path = OUT / "candidates.json"
    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    candidates["query_scope"]["selection_rule"] = (
        "same-origin normalized match within query range: scheme and lower-cased host must match; "
        "only default port is normalized; path/query/fragment remain literal; status 200 or "
        "Wayback redirect; closest timestamp at or before anchor"
    )
    candidates["query_scope"]["candidate_match_policy"] = {
        "http_default_port_equivalent": True,
        "https_default_port_equivalent": True,
        "official_www_bare_host_equivalent_for_matching": False,
        "official_www_bare_host_separate_origins": True,
        "http_https_separate_origins": True,
        "host_case_fold": True,
        "observed_original_preserved": True,
        "path_and_trailing_slash_literal": True,
        "query_and_fragment_literal": True,
    }
    candidates["selection"]["offline_index_correction"] = {
        "network_requests": 0,
        "reason": "CDX rows with default ports were reconciled from existing raw index bodies; bare/www and HTTP/HTTPS origins remain separate",
        "corrected_candidate_only_count": corrected_candidate_only_count,
        "corrected_preferred_candidate_count": corrected_preferred_count,
        "targets": [
            {
                "candidate_rank": result["candidate_rank"],
                "target": result["target"],
                "literal_valid_capture_count_before_normalization": result["cdx"].get("literal_valid_capture_count_before_normalization"),
                "normalized_eligible_capture_count": len(result["cdx"].get("eligible_capture_records") or []),
                "corrected_preferred_candidate": result["cdx"].get("corrected_preferred_candidate"),
                "observed_original_identities": result["cdx"].get("observed_original_identities") or [],
                "other_origin_metadata": result["cdx"].get("other_origin_metadata") or {},
                "replay_deferred": result.get("replay_attempt_count", 0) == 0 and result["cdx"].get("corrected_preferred_candidate") is not None,
            }
            for result in report.get("results") or []
            if result["cdx"].get("corrected_preferred_candidate") is not None
        ],
    }
    write_json(candidates_path, candidates)
    report["finished_utc"] = request_finished
    report["request_window_finished_utc"] = request_finished
    report["report_updated_utc"] = report_updated
    report["cdx_source_response_count"] = cdx_source_responses
    report["replay_source_response_count"] = replay_source_responses
    report["category_counts"] = counts
    report["capture_index_count"] = sum(result["cdx"].get("capture_index_count", 0) for result in report.get("results") or [])
    report["selected_capture_count"] = selected_count
    report["corrected_preferred_candidate_count"] = corrected_preferred_count
    report["corrected_candidate_only_count"] = corrected_candidate_only_count
    report["normalized_eligible_capture_count"] = normalized_eligible_count
    report["other_origin_capture_count"] = other_origin_count
    report["inputs"]["candidates_sha256"] = sha256_file(candidates_path)
    write_json(report_path, report)

    by_rank = {result.get("candidate_rank"): result for result in report.get("results") or []}
    for target in summary.get("targets") or []:
        result = by_rank.get(target.get("candidate_rank"))
        if result is None:
            continue
        target["cdx_source_status"] = result["cdx"].get("source_status")
        target["cdx_source_response_count"] = result["cdx"].get("source_response_count")
        target["unrequested_reason"] = result.get("unrequested_reason")
        target["literal_valid_capture_count_before_normalization"] = result["cdx"].get("literal_valid_capture_count_before_normalization")
        target["normalized_eligible_capture_count"] = len(result["cdx"].get("eligible_capture_records") or [])
        target["corrected_preferred_candidate_timestamp"] = (result["cdx"].get("corrected_preferred_candidate") or {}).get("timestamp")
        target["corrected_preferred_candidate_original"] = (result["cdx"].get("corrected_preferred_candidate") or {}).get("original")
        target["observed_original_identities"] = result["cdx"].get("observed_original_identities") or []
        target["other_origin_metadata"] = result["cdx"].get("other_origin_metadata") or {}
        target["selection_limitation"] = result["cdx"].get("selection_limitation")
    summary["finished_utc"] = request_finished
    summary["request_window_finished_utc"] = request_finished
    summary["report_updated_utc"] = report_updated
    summary["cdx_source_response_count"] = cdx_source_responses
    summary["replay_source_response_count"] = replay_source_responses
    summary["category_counts"] = counts
    summary["capture_index_count"] = report["capture_index_count"]
    summary["selected_capture_count"] = selected_count
    summary["corrected_preferred_candidate_count"] = corrected_preferred_count
    summary["corrected_candidate_only_count"] = corrected_candidate_only_count
    summary["normalized_eligible_capture_count"] = normalized_eligible_count
    summary["other_origin_capture_count"] = other_origin_count
    write_json(summary_path, summary)

    source_map_path = OUT / "payload-source-map.json"
    source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
    source_map["generated_utc"] = report_updated
    source_map["report_updated_utc"] = report_updated
    write_json(source_map_path, source_map)

    counts = report.get("category_counts") or {}
    lines = [
        "# Network core pages 3 — sanitized recovery summary",
        "",
        f"Accepted LOCAL35 reconciliation SHA-256: `{report['inputs']['reconciliation_sha256']}`.",
        f"Request window: `{report.get('started_utc')}` to `{request_finished}`; report updated offline: `{report_updated}`.",
        f"Attempts: `{report.get('source_request_count')}`; source HTTP responses: `{report.get('source_response_count')}`; failed attempts: `{report.get('failed_attempt_count')}`; CDX source responses: `{cdx_source_responses}`; replay source responses: `{replay_source_responses}`; CDX capture-index rows: `{report.get('capture_index_count')}`; normalized eligible rows: `{report.get('normalized_eligible_capture_count')}`; other-origin rows retained as metadata: `{report.get('other_origin_capture_count')}`; selected captures: `{report.get('selected_capture_count')}`; corrected preferred candidates: `{corrected_preferred_count}`; corrected candidate-only targets: `{corrected_candidate_only_count}`; valid entities: `{report.get('valid_entity_count')}`.",
        "Categories: " + ", ".join(f"`{key}` {value}" for key, value in sorted(counts.items())) + ".",
        f"Disk free before/after: `{report['preflight']['disk_free_bytes_before']}` / `{report['preflight']['disk_free_bytes_after']}` bytes; stop reason: `{report.get('stop_reason') or 'batch completed'}`.",
        "",
        "Actual Memento values below come only from valid replay response headers. CDX timestamps and request hints are recorded separately.",
        "",
        "| # | target | query original URL | category | CDX HTTP | replay HTTP | corrected candidate | actual Memento | payload bytes | CDX rows | unrequested reason |",
        "|---:|---|---|---|---:|---:|---|---|---:|---:|---|",
    ]
    for result in report.get("results") or []:
        lines.append(
            f"| {result['candidate_rank']} | `{result['target']}` | `{result['query_original_url']}` | `{result['category']}` | "
            f"{result['cdx'].get('source_status') or ''} | {result.get('final_source_status') or ''} | `" 
            f"{(result['cdx'].get('corrected_preferred_candidate') or {}).get('timestamp') or ''}` | "
            f"`{result.get('actual_memento_or_null') or ''}` | {result.get('final_body_bytes') or 0} | "
            f"{result['cdx'].get('capture_index_count') or 0} | `{result.get('unrequested_reason') or ''}` |"
        )
    lines.extend([
        "",
        "Bodies and original headers/traces remain only below this batch's raw directory. Valid entities are listed in `payload-source-map.json` for review; no entity was copied into the offline mirror.",
        "",
    ])
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"mode": "offline_augment", "network_requests": 0, "request_window_finished_utc": request_finished, "report_updated_utc": report_updated, "cdx_source_response_count": cdx_source_responses, "replay_source_response_count": replay_source_responses}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true", help="write candidates and plan without network")
    parser.add_argument("--execute", action="store_true", help="perform the bounded CDX/replay batch")
    parser.add_argument("--augment", action="store_true", help="repair derived reports from local JSON only")
    args = parser.parse_args()
    if args.augment:
        return augment_existing()
    if args.execute:
        return execute()
    return prepare()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"core_pages3: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

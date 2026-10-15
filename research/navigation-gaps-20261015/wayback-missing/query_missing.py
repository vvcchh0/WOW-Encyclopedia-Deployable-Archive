#!/usr/bin/env python3
"""Bounded exact-CDX and replay evidence for three missing navigation pages.

This script is intentionally finite.  It performs at most one baseline CDX
request per target, one optional through-2010 CDX request for a target without
a baseline candidate, and one replay request for the selected candidate.  It
keeps CDX selection facts separate from replay/Memento observations and only
puts a page in ``source-map.json`` after body validation.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import html
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ANCHOR = "20080512210044"
BASELINE_FROM = "20080101000000"
LATE_TO = "20101231235959"
MAX_REQUESTS = 9
MAX_TOTAL_RESPONSE_BYTES = 16 * 1024 * 1024
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
INTERVAL_SECONDS = 1.0
TIMEOUT_SECONDS = 30.0
USER_AGENT = "WOW-Encyclopedia-navigation-gap-research/1.0"
TARGETS: tuple[dict[str, str], ...] = (
    {
        "id": "pvp_flash_rewards",
        "route": "/pvp/flash-rewards/",
        "original": "http://www.worldofwarcraft.com/pvp/flash-rewards/",
        "expected": "html",
        "note": "public historical PvP minisite page; no submission or account flow is restored",
    },
    {
        "id": "burningcrusade_trial",
        "route": "/burningcrusade/trial/index.html",
        "original": "http://www.worldofwarcraft.com/burningcrusade/trial/index.html?referrer=WORLDOFWARCRAFT&source=wowhome&promo=1",
        "expected": "html",
        "note": "public historical trial information page only; forms and transaction behavior are not restored",
    },
    {
        "id": "wrath_wallpapers",
        "route": "/wrath/wallpapers.xml",
        "original": "http://www.worldofwarcraft.com/wrath/wallpapers.xml",
        "expected": "xml_or_html",
        "note": "historical wallpapers data/page route; CSS and image expansion are out of scope",
    },
)

ERROR_MARKERS = (
    "wayback machine error",
    "no archived snapshot",
    "this url has been excluded",
    "the requested url was not found",
    "got an http 404 response",
    "got an http 429 response",
    "got an http 5xx response",
    "memento not found",
    "timetravel error",
    "page cannot be displayed",
)
HTML_MIMES = {"text/html", "application/xhtml+xml"}
XML_MIMES = {"text/xml", "application/xml", "application/xhtml+xml", "application/rss+xml", "application/atom+xml"}
PAGE_MIMES = HTML_MIMES | XML_MIMES | {"text/plain"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return default


def target_by_id(target_id: str) -> dict[str, str]:
    for target in TARGETS:
        if target["id"] == target_id:
            return dict(target)
    raise SystemExit(f"unknown target id: {target_id}")


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")[:120] or "item"


def mime_base(value: Any) -> str:
    return str(value or "").split(";", 1)[0].strip().casefold()


def canonical_identity(value: str) -> tuple[str, str, str] | None:
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        return None
    host = parsed.hostname.casefold().rstrip(".")
    port = parsed.port
    if port is not None and not ((parsed.scheme.casefold() == "http" and port == 80) or (parsed.scheme.casefold() == "https" and port == 443)):
        host = f"{host}:{port}"
    return host, parsed.path or "/", parsed.query


def build_cdx_url(original: str, *, to_value: str) -> str:
    params = [
        ("url", original),
        ("matchType", "exact"),
        ("output", "json"),
        ("fl", "timestamp,original,statuscode,digest,length,mimetype"),
        ("filter", "statuscode:200"),
        ("from", BASELINE_FROM),
        ("to", to_value),
        ("limit", "1000"),
        ("page", "0"),
        ("gzip", "false"),
    ]
    return "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(params)


def build_replay_url(timestamp: str, original: str) -> str:
    target = urllib.parse.quote(original, safe=":/?&=%;,+$'@~")
    return f"https://web.archive.org/web/{timestamp}id_/{target}"


def headers_dict(headers: Any) -> dict[str, str]:
    return {str(key): str(value) for key, value in headers.items()} if headers is not None else {}


def header_value(headers: dict[str, str], name: str) -> str | None:
    wanted = name.casefold()
    for key, value in headers.items():
        if key.casefold() == wanted:
            return value
    return None


def memento_timestamp(headers: dict[str, str], final_url: str | None) -> str | None:
    value = header_value(headers, "Memento-Datetime")
    if value:
        try:
            parsed = parsedate_to_datetime(value)
            if parsed is not None:
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
        except (TypeError, ValueError, OverflowError):
            pass
    if final_url:
        match = re.search(r"/web/(\d{14})(?:id_|/)", final_url)
        if match:
            return match.group(1)
    return None


def response_body(response: Any, remaining: int) -> tuple[bytes, bool]:
    cap = min(MAX_RESPONSE_BYTES, max(0, remaining))
    if cap <= 0:
        return b"", True
    body = response.read(cap + 1)
    return body[:cap], len(body) > cap


def request_state() -> dict[str, Any]:
    state = read_json(OUT / "request-state.json", {})
    if not isinstance(state, dict):
        state = {}
    state.setdefault("started_at", now())
    state.setdefault("request_count", 0)
    state.setdefault("response_bytes", 0)
    state.setdefault("tls_failures", 0)
    state.setdefault("stop_reason", None)
    state.setdefault("last_request_finished_monotonic", None)
    return state


def persist_state(state: dict[str, Any]) -> None:
    write_json(OUT / "request-state.json", state)


def append_request(record: dict[str, Any]) -> None:
    path = OUT / "request-log.json"
    existing = read_json(path, [])
    if not isinstance(existing, list):
        existing = []
    existing.append(record)
    write_json(path, existing)


def fetch(url: str, *, purpose: str, state: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
    if state.get("stop_reason"):
        return {"purpose": purpose, "url": url, "status": None, "error": "network_stopped:" + str(state["stop_reason"])}, b""
    if int(state.get("request_count") or 0) >= MAX_REQUESTS:
        state["stop_reason"] = "max_requests"
        persist_state(state)
        return {"purpose": purpose, "url": url, "status": None, "error": "network_stopped:max_requests"}, b""
    last_finished = state.get("last_request_finished_monotonic")
    if isinstance(last_finished, (int, float)):
        wait = INTERVAL_SECONDS - (time.monotonic() - float(last_finished))
        if wait > 0:
            time.sleep(wait)
    started = time.monotonic()
    requested_at = now()
    record: dict[str, Any] = {
        "purpose": purpose,
        "requested_at": requested_at,
        "request_url": url,
        "transport": "urllib_system_proxy",
        "proxy_connect_status_recorded": False,
        "status": None,
        "final_url": None,
        "response_headers": {},
        "response_bytes": 0,
        "response_sha256": None,
        "truncated": False,
        "error": None,
    }
    body = b""
    remaining = MAX_TOTAL_RESPONSE_BYTES - int(state.get("response_bytes") or 0)
    try:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,text/xml;q=0.8,*/*;q=0.1",
                "Accept-Encoding": "identity",
                "User-Agent": USER_AGENT,
            },
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            record["status"] = int(response.status)
            record["final_url"] = response.geturl()
            record["response_headers"] = headers_dict(response.headers)
            body, truncated = response_body(response, remaining)
            record["truncated"] = truncated
    except urllib.error.HTTPError as exc:
        record["status"] = int(exc.code)
        record["final_url"] = exc.geturl()
        record["response_headers"] = headers_dict(exc.headers)
        try:
            body, truncated = response_body(exc, remaining)
            record["truncated"] = truncated
        except Exception as body_exc:  # pragma: no cover - transport dependent
            record["error"] = f"http_error_body:{type(body_exc).__name__}:{body_exc}"
    except Exception as exc:  # pragma: no cover - transport dependent
        record["error"] = f"{type(exc).__name__}:{exc}"
    finished = time.monotonic()
    record["finished_at"] = now()
    record["duration_seconds"] = round(finished - started, 3)
    record["response_bytes"] = len(body)
    record["response_sha256"] = sha256(body) if body else None
    state["request_count"] = int(state.get("request_count") or 0) + 1
    state["response_bytes"] = int(state.get("response_bytes") or 0) + len(body)
    state["last_request_finished_monotonic"] = finished
    status = record.get("status")
    error_text = str(record.get("error") or "")
    tls_error = any(marker in error_text.casefold() for marker in ("ssl", "tls", "certificate", "connectionreset", "eoferror"))
    if tls_error:
        state["tls_failures"] = int(state.get("tls_failures") or 0) + 1
    else:
        state["tls_failures"] = 0
    if status in {429, 503}:
        state["stop_reason"] = f"http_{status}"
    elif int(state.get("tls_failures") or 0) >= 5:
        state["stop_reason"] = "five_consecutive_tls_failures"
    persist_state(state)
    append_request(record)
    return record, body


def cdx_rows(body: bytes) -> list[dict[str, str]]:
    try:
        value = json.loads(body.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return []
    if not isinstance(value, list) or not value:
        return []
    if isinstance(value[0], list):
        header = [str(item) for item in value[0]]
        return [
            {header[index]: str(item[index]) for index in range(min(len(header), len(item)))}
            for item in value[1:]
            if isinstance(item, list)
        ]
    return [item for item in value if isinstance(item, dict)]


def valid_page_mime(value: Any) -> bool:
    base = mime_base(value)
    return base in PAGE_MIMES or base.endswith("+xml")


def select_row(target: dict[str, str], rows: list[dict[str, str]], *, maximum: str) -> dict[str, str] | None:
    identity = canonical_identity(target["original"])
    candidates: list[dict[str, str]] = []
    for row in rows:
        original = str(row.get("original") or row.get("url") or "")
        timestamp = str(row.get("timestamp") or "")
        if canonical_identity(original) != identity:
            continue
        if str(row.get("statuscode") or row.get("status") or "") != "200":
            continue
        if not re.fullmatch(r"\d{14}", timestamp) or timestamp > maximum:
            continue
        if not valid_page_mime(row.get("mimetype") or row.get("mime")):
            continue
        candidates.append({str(key): str(value) for key, value in row.items()})
    return max(candidates, key=lambda row: row["timestamp"]) if candidates else None


def body_error_marker(body: bytes) -> str | None:
    sample = body[:256 * 1024].decode("utf-8", errors="ignore").casefold()
    for marker in ERROR_MARKERS:
        if marker in sample:
            return marker
    return None


def title_from_html(body: bytes) -> str | None:
    text = body.decode("utf-8", errors="replace")
    match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", text, re.I | re.S)
    if not match:
        return None
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", match.group(1)))).strip() or None


def xml_root(body: bytes) -> str | None:
    try:
        root = ET.fromstring(body)
    except (ET.ParseError, ValueError, UnicodeError):
        return None
    return str(root.tag)


def validate_page(target: dict[str, str], body: bytes, headers: dict[str, str]) -> dict[str, Any]:
    mime = mime_base(header_value(headers, "Content-Type"))
    marker = body_error_marker(body)
    title = title_from_html(body)
    root = xml_root(body)
    if title and re.search(r"\b(?:404|file\s+not\s+found|not\s+found|error)\b", title, re.I):
        marker = marker or "error_title"
    if marker:
        return {"valid": False, "content_class": "error_page", "error_marker": marker, "mime": mime, "title": title, "xml_root": root}
    if root is not None and (mime in XML_MIMES or target["expected"] == "xml_or_html"):
        return {"valid": True, "content_class": "xml_document", "mime": mime, "title": title, "xml_root": root}
    if title and (mime in HTML_MIMES or target["expected"] in {"html", "xml_or_html"}):
        return {"valid": True, "content_class": "html_page", "mime": mime, "title": title, "xml_root": root}
    return {"valid": False, "content_class": "unclassified", "mime": mime, "title": title, "xml_root": root, "error_marker": None}


def target_cdx_path(target_id: str, window: str) -> Path:
    return OUT / "cdx" / f"{target_id}-{window}.json"


def target_cdx_meta_path(target_id: str, window: str) -> Path:
    return OUT / "cdx" / f"{target_id}-{window}.meta.json"


def run_cdx(target: dict[str, str], *, window: str, state: dict[str, Any]) -> dict[str, Any]:
    out_path = target_cdx_path(target["id"], window)
    meta_path = target_cdx_meta_path(target["id"], window)
    existing = read_json(meta_path, None)
    if isinstance(existing, dict) and out_path.is_file():
        return existing
    if window == "baseline":
        to_value = ANCHOR
        temporal_window = {"from": BASELINE_FROM, "to": ANCHOR, "class": "baseline_2008"}
    else:
        to_value = LATE_TO
        temporal_window = {"from": BASELINE_FROM, "to": LATE_TO, "class": "late_or_post_2008_supplement"}
    request_url = build_cdx_url(target["original"], to_value=to_value)
    record, body = fetch(request_url, purpose=f"cdx_{window}:{target['id']}", state=state)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(body)
    rows = cdx_rows(body) if record.get("status") == 200 and not record.get("truncated") else []
    result = {
        "schema_version": 1,
        "target_id": target["id"],
        "original": target["original"],
        "window": window,
        "query_contract": {
            "matchType": "exact",
            "from": temporal_window["from"],
            "to": temporal_window["to"],
            "page": 0,
            "limit": 1000,
            "pagination": "page=0; page count not requested to avoid a separate query",
        },
        "request_url": request_url,
        "response": record,
        "row_count": len(rows),
        "rows": rows,
        "raw_file": str(out_path.relative_to(ROOT)).replace("\\", "/"),
        "raw_sha256": sha256(body) if body else None,
        "queried_at": now(),
    }
    write_json(meta_path, result)
    return result


def select_candidates(state: dict[str, Any], targets: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    selections: dict[str, dict[str, Any]] = {}
    overrides = read_json(OUT / "selection-overrides.json", {})
    if not isinstance(overrides, dict):
        overrides = {}
    for target in targets:
        baseline = read_json(target_cdx_meta_path(target["id"], "baseline"), {})
        row = select_row(target, list(baseline.get("rows") or []), maximum=ANCHOR) if isinstance(baseline, dict) else None
        if row is not None:
            selections[target["id"]] = {"target": target, "window": "baseline", "row": row, "cdx": baseline}
        else:
            late = read_json(target_cdx_meta_path(target["id"], "late"), {})
            late_rows = list(late.get("rows") or []) if isinstance(late, dict) else []
            override_timestamp = str(overrides.get(target["id"]) or "")
            row = next((candidate for candidate in late_rows if str(candidate.get("timestamp")) == override_timestamp), None) if override_timestamp else None
            selections[target["id"]] = {"target": target, "window": "late" if row is not None else "late_pending", "row": row, "cdx": late if row is not None else baseline}
    return selections


def prepare_retry_override(target_id: str) -> str:
    """Choose the next late CDX row after an already-invalid replay."""

    target = target_by_id(target_id)
    late = read_json(target_cdx_meta_path(target_id, "late"), {})
    rows = list(late.get("rows") or []) if isinstance(late, dict) else []
    existing_replays = sorted((OUT / "replays").glob(f"{safe_name(target_id)}-*.json"))
    attempted = {path.stem.rsplit("-", 1)[-1] for path in existing_replays}
    candidates = [row for row in rows if str(row.get("timestamp") or "") not in attempted]
    candidates.sort(key=lambda row: str(row.get("timestamp") or ""), reverse=True)
    if not candidates:
        raise SystemExit(f"no unattempted late CDX candidate remains for {target_id}")
    timestamp = str(candidates[0]["timestamp"])
    overrides = read_json(OUT / "selection-overrides.json", {})
    if not isinstance(overrides, dict):
        overrides = {}
    overrides[target_id] = timestamp
    write_json(OUT / "selection-overrides.json", overrides)
    return timestamp


def replay_selected(selection: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    target = selection["target"]
    row = selection["row"]
    window = selection["window"]
    if row is None:
        return {"status": "not_selected", "reason": "no_valid_200_page_mime_cdx_row"}
    timestamp = str(row["timestamp"])
    original = str(row.get("original") or target["original"])
    replay_url = build_replay_url(timestamp, original)
    existing_path = OUT / "replays" / f"{safe_name(target['id'])}-{timestamp}.json"
    existing = read_json(existing_path, None)
    if isinstance(existing, dict):
        raw_value = existing.get("raw_file")
        raw_path = ROOT / str(raw_value).replace("/", "\\") if raw_value else None
        raw_body = raw_path.read_bytes() if raw_path and raw_path.is_file() else b""
        response = dict(existing.get("response") or {})
        validation = validate_page(target, raw_body, dict(response.get("response_headers") or {})) if response.get("status") == 200 and not response.get("truncated") else {"valid": False, "content_class": "truncated_or_non_200"}
        existing["status"] = "accepted" if response.get("status") == 200 and validation.get("valid") else "replay_invalid"
        existing["validation"] = validation
        existing["raw_length"] = len(raw_body)
        existing["raw_sha256"] = sha256(raw_body) if raw_body else None
        write_json(existing_path, existing)
        return existing
    response, body = fetch(replay_url, purpose=f"replay_{window}:{target['id']}", state=state)
    raw_dir = OUT / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{safe_name(target['id'])}-{timestamp}.bin"
    raw_path.write_bytes(body)
    validation = validate_page(target, body, dict(response.get("response_headers") or {})) if response.get("status") == 200 and not response.get("truncated") else {"valid": False, "content_class": "truncated_or_non_200"}
    memento = memento_timestamp(dict(response.get("response_headers") or {}), response.get("final_url"))
    result = {
        "status": "accepted" if response.get("status") == 200 and validation.get("valid") else "replay_invalid",
        "target_id": target["id"],
        "original": target["original"],
        "cdx_original": original,
        "requested_timestamp": timestamp,
        "indexed_capture_timestamp": timestamp,
        "requested_url": replay_url,
        "response": response,
        "memento_datetime": header_value(dict(response.get("response_headers") or {}), "Memento-Datetime"),
        "actual_timestamp": memento,
        "memento_timestamp_match": bool(memento and memento == timestamp),
        "validation": validation,
        "raw_file": str(raw_path.relative_to(ROOT)).replace("\\", "/"),
        "raw_sha256": sha256(body) if body else None,
        "raw_length": len(body),
        "temporal_class": "baseline_2008" if timestamp <= ANCHOR else "post_2008",
        "request_hint": {
            "requested_timestamp": timestamp,
            "source": "CDX selected timestamp; not substituted for Memento actual_timestamp",
        },
        "retrieved_at": now(),
    }
    write_json(existing_path, result)
    return result


def build_source_map(results: list[dict[str, Any]]) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for result in results:
        if result.get("status") != "accepted":
            continue
        target = target_by_id(str(result["target_id"]))
        response = dict(result.get("response") or {})
        headers = dict(response.get("response_headers") or {})
        validation = dict(result.get("validation") or {})
        files.append(
            {
                "logical_url": target["original"],
                "original": target["original"],
                "source_url": result["cdx_original"],
                "source_base_url": result["cdx_original"],
                "local_path": result["raw_file"],
                "mime": header_value(headers, "Content-Type") or validation.get("mime") or "",
                "response_content_type": header_value(headers, "Content-Type"),
                "kind": "html" if validation.get("content_class") == "html_page" else "xml",
                "role": "navigation_gap_recovery",
                "sha256": result["raw_sha256"],
                "content_length": result["raw_length"],
                "actual_timestamp": result.get("actual_timestamp") or result["requested_timestamp"],
                "entity_observed_capture_timestamp": result.get("actual_timestamp"),
                "indexed_capture_timestamp": result["indexed_capture_timestamp"],
                "requested_timestamp": result["requested_timestamp"],
                "memento_datetime": result.get("memento_datetime"),
                "actual_url": response.get("final_url"),
                "requested_url": result["requested_url"],
                "http_status": response.get("status"),
                "content_valid": True,
                "content_class": validation.get("content_class"),
                "title": validation.get("title"),
                "xml_root": validation.get("xml_root"),
                "temporal_class": result["temporal_class"],
                "cdx_digest": str(result.get("cdx_digest") or "") or None,
                "cdx_length": result.get("cdx_length"),
                "supplement_note": target["note"],
            }
        )
    return {
        "schema_version": 1,
        "kind": "navigation_gap_page_integration_map",
        "status": "validated_source_entities_only",
        "generated_utc": now(),
        "network_performed": True,
        "anchor_timestamp": ANCHOR,
        "files": files,
    }


def redacted_url(target: dict[str, str]) -> str:
    parsed = urllib.parse.urlsplit(target["original"])
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "<query-redacted>" if parsed.query else "", ""))


def write_report(targets: list[dict[str, str]], cdx_results: list[dict[str, Any]], replay_results: list[dict[str, Any]], state: dict[str, Any]) -> None:
    by_target = {str(item.get("target_id")): item for item in replay_results}
    lines = [
        "# Wayback missing navigation pages",
        "",
        f"Local bounded run at {now()}; network requests: {state.get('request_count', 0)}; response bytes: {state.get('response_bytes', 0)}.",
        "CDX request parameters keep exact URL identity, `from=20080101000000`, `to` per window, `matchType=exact`, and `page=0`; replay Memento observations are recorded separately.",
        "",
    ]
    for target in targets:
        baseline = next((item for item in cdx_results if item.get("target_id") == target["id"] and item.get("window") == "baseline"), None)
        late = next((item for item in cdx_results if item.get("target_id") == target["id"] and item.get("window") == "late"), None)
        result = by_target.get(target["id"], {})
        validation = result.get("validation") or {}
        lines.extend(
            [
                f"## {target['route']}",
                "",
                f"- Query identity: `{redacted_url(target)}`",
                f"- Baseline CDX: `{baseline.get('response', {}).get('status') if baseline else 'not queried'}`; rows `{baseline.get('row_count') if baseline else 0}`; raw `{baseline.get('raw_file') if baseline else 'n/a'}`.",
                f"- Through-2010 CDX: `{late.get('response', {}).get('status') if late else 'not needed'}`; rows `{late.get('row_count') if late else 0}`; raw `{late.get('raw_file') if late else 'n/a'}`.",
                f"- Replay status: `{result.get('status', 'not attempted')}`; content class `{validation.get('content_class', 'n/a')}`; title/root `{validation.get('title') or validation.get('xml_root') or 'n/a'}`.",
                f"- Capture evidence: indexed `{result.get('indexed_capture_timestamp', 'n/a')}`; Memento actual `{result.get('actual_timestamp', 'n/a')}`; match `{result.get('memento_timestamp_match', 'n/a')}`.",
                f"- Integration: `{result.get('raw_file', 'no accepted source')}`; trial/business handling remains static historical content only.",
                "",
            ]
        )
    lines.extend(
        [
            "## Stop and scope",
            "",
            f"- Stop reason: `{state.get('stop_reason') or 'plan_complete'}`.",
            "- CONNECT proxy status lines are excluded from source status; only end-to-end response status is recorded.",
            "- No CSS or image expansion was requested. Raw bytes remain under this ignored research directory; this report does not include body snippets or form fields.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sanitized_summary(
    targets: list[dict[str, str]],
    cdx_results: list[dict[str, Any]],
    replay_results: list[dict[str, Any]],
    state: dict[str, Any],
) -> None:
    """Write a review summary without response headers or cookie values."""

    cdx_by_target = {(str(item.get("target_id")), str(item.get("window"))): item for item in cdx_results}
    replay_by_target = {str(item.get("target_id")): item for item in replay_results}

    def replay_attempts(target_id: str) -> list[dict[str, Any]]:
        """Return every locally saved replay attempt without response headers."""

        attempts: list[dict[str, Any]] = []
        for path in sorted((OUT / "replays").glob(f"{safe_name(target_id)}-*.json")):
            item = read_json(path, {})
            if not isinstance(item, dict):
                continue
            validation = dict(item.get("validation") or {})
            response = dict(item.get("response") or {})
            attempts.append(
                {
                    "status": item.get("status"),
                    "requested_timestamp": item.get("requested_timestamp"),
                    "indexed_capture_timestamp": item.get("indexed_capture_timestamp"),
                    "actual_timestamp": item.get("actual_timestamp"),
                    "memento_timestamp_match": item.get("memento_timestamp_match"),
                    "temporal_class": item.get("temporal_class"),
                    "http_status": response.get("status"),
                    "content_class": validation.get("content_class"),
                    "title": validation.get("title"),
                    "xml_root": validation.get("xml_root"),
                    "raw_file": item.get("raw_file"),
                    "raw_sha256": item.get("raw_sha256"),
                    "raw_length": item.get("raw_length"),
                    "cdx_digest": item.get("cdx_digest"),
                    "cdx_length": item.get("cdx_length"),
                }
            )
        return attempts

    target_rows: list[dict[str, Any]] = []
    for target in targets:
        replay = replay_by_target.get(target["id"], {})
        validation = dict(replay.get("validation") or {})
        target_rows.append(
            {
                "target_id": target["id"],
                "route": target["route"],
                "original_url": target["original"],
                "baseline_cdx": {
                    "status": (cdx_by_target.get((target["id"], "baseline")) or {}).get("response", {}).get("status"),
                    "row_count": (cdx_by_target.get((target["id"], "baseline")) or {}).get("row_count", 0),
                    "raw_file": (cdx_by_target.get((target["id"], "baseline")) or {}).get("raw_file"),
                },
                "late_cdx": {
                    "status": (cdx_by_target.get((target["id"], "late")) or {}).get("response", {}).get("status"),
                    "row_count": (cdx_by_target.get((target["id"], "late")) or {}).get("row_count", 0),
                    "raw_file": (cdx_by_target.get((target["id"], "late")) or {}).get("raw_file"),
                },
                "replay": {
                    "status": replay.get("status"),
                    "http_status": (replay.get("response") or {}).get("status"),
                    "indexed_capture_timestamp": replay.get("indexed_capture_timestamp"),
                    "actual_timestamp": replay.get("actual_timestamp"),
                    "memento_timestamp_match": replay.get("memento_timestamp_match"),
                    "temporal_class": replay.get("temporal_class"),
                    "content_class": validation.get("content_class"),
                    "title": validation.get("title"),
                    "xml_root": validation.get("xml_root"),
                    "raw_file": replay.get("raw_file"),
                    "raw_sha256": replay.get("raw_sha256"),
                    "raw_length": replay.get("raw_length"),
                    "cdx_digest": replay.get("cdx_digest"),
                    "cdx_length": replay.get("cdx_length"),
                },
                "replay_attempts": replay_attempts(target["id"]),
                "integration_status": "accepted source-map file" if replay.get("status") == "accepted" else "not included in source-map",
                "scope_note": target["note"],
            }
        )
    summary = {
        "schema_version": 1,
        "kind": "sanitized_wayback_missing_summary",
        "generated_utc": now(),
        "network_performed": True,
        "anchor_timestamp": ANCHOR,
        "request_count": state.get("request_count"),
        "response_bytes": state.get("response_bytes"),
        "max_requests": MAX_REQUESTS,
        "max_response_bytes": MAX_TOTAL_RESPONSE_BYTES,
        "stop_reason": state.get("stop_reason") or "plan_complete",
        "transport_evidence": {
            "transport": "urllib_system_proxy",
            "direct_attempted": False,
            "proxy_fallback": False,
            "proxy_connect_status_recorded": False,
            "note": "This run used the configured HTTPS proxy from urllib.request.getproxies; it does not establish direct-first success or failure.",
        },
        "targets": target_rows,
        "source_map": "research/navigation-gaps-20261015/wayback-missing/source-map.json",
        "raw_summary": "research/navigation-gaps-20261015/wayback-missing/summary.json",
        "redaction": "response_headers, Set-Cookie, Cookie, Authorization, and body snippets are omitted",
    }
    write_json(OUT / "sanitized-summary.json", summary)
    lines = [
        "# Sanitized Wayback missing-page summary",
        "",
        f"Generated {summary['generated_utc']}. Requests: {summary['request_count']}; response bytes: {summary['response_bytes']}; stop: `{summary['stop_reason']}`.",
        "",
        "Transport evidence: the run used `urllib_system_proxy` from the configured HTTPS proxy. No direct-first attempt was made, so this record makes no direct transport claim. CONNECT status lines are excluded.",
        "",
    ]
    for item in target_rows:
        replay = item["replay"]
        lines.extend(
            [
                f"## {item['route']}",
                "",
                f"- Baseline CDX: HTTP `{item['baseline_cdx']['status']}`; rows `{item['baseline_cdx']['row_count']}`.",
                f"- Late CDX: HTTP `{item['late_cdx']['status']}`; rows `{item['late_cdx']['row_count']}`.",
                f"- Replay: `{replay['status']}`; HTTP `{replay['http_status']}`; class `{replay['content_class']}`; title/root `{replay['title'] or replay['xml_root'] or 'n/a'}`.",
                f"- Capture: indexed `{replay['indexed_capture_timestamp']}`; Memento actual `{replay['actual_timestamp']}`; match `{replay['memento_timestamp_match']}`; temporal class `{replay['temporal_class']}`.",
                f"- Replay attempts: " + "; ".join(
                    f"{attempt.get('requested_timestamp')}: {attempt.get('status')}; {attempt.get('content_class')}; {attempt.get('title') or attempt.get('xml_root') or 'n/a'}"
                    for attempt in item["replay_attempts"]
                ) + ".",
                f"- Integration: {item['integration_status']}; raw path `{replay['raw_file'] or 'n/a'}`.",
                f"- Scope: {item['scope_note']}.",
                "",
            ]
        )
    lines.extend(
        [
            "Raw response headers and any cookie values remain only in local `summary.json`/request metadata; this sanitized summary contains no response headers or body snippets.",
            "",
        ]
    )
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")


def run(target_ids: list[str], *, cdx_only: bool) -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "raw").mkdir(exist_ok=True)
    (OUT / "replays").mkdir(exist_ok=True)
    (OUT / "cdx").mkdir(exist_ok=True)
    write_json(OUT / "targets.json", {"schema_version": 1, "anchor_timestamp": ANCHOR, "targets": list(TARGETS)})
    state = request_state()
    targets = [target_by_id(item) for item in target_ids]
    cdx_results: list[dict[str, Any]] = []
    for target in targets:
        cdx_results.append(run_cdx(target, window="baseline", state=state))
    if cdx_only:
        write_report(targets, cdx_results, [], state)
        write_json(OUT / "source-map.json", build_source_map([]))
        write_json(OUT / "summary.json", {"schema_version": 1, "network_performed": True, "request_count": state.get("request_count"), "targets": cdx_results, "stop_reason": state.get("stop_reason")})
        write_sanitized_summary(targets, cdx_results, [], state)
        return {"request_count": state.get("request_count"), "stop_reason": state.get("stop_reason"), "cdx": cdx_results}
    # Preserve a previously queried late-window CDX result in every rerun.
    # Candidate overrides otherwise make select_candidates() reuse the late
    # row without adding its evidence back to the newly written summary.
    for target in targets:
        late_path = target_cdx_meta_path(target["id"], "late")
        late = read_json(late_path, None)
        if isinstance(late, dict) and target_cdx_path(target["id"], "late").is_file():
            cdx_results.append(late)
    selections = select_candidates(state, targets)
    for target in targets:
        selection = selections[target["id"]]
        if selection["row"] is None and not state.get("stop_reason"):
            late = run_cdx(target, window="late", state=state)
            if not any(
                item.get("target_id") == late.get("target_id")
                and item.get("window") == late.get("window")
                for item in cdx_results
            ):
                cdx_results.append(late)
            row = select_row(target, list(late.get("rows") or []), maximum=LATE_TO)
            if row is not None:
                selection["window"] = "late"
                selection["row"] = row
                selection["cdx"] = late
    replay_results: list[dict[str, Any]] = []
    for target in targets:
        selection = selections[target["id"]]
        if selection["row"] is None or state.get("stop_reason"):
            replay_results.append({"status": "not_attempted", "target_id": target["id"], "reason": "no_selected_cdx_or_network_stop"})
            continue
        row = selection["row"]
        replay_result = replay_selected(selection, state)
        replay_result["cdx_digest"] = row.get("digest")
        replay_result["cdx_length"] = row.get("length")
        replay_results.append(replay_result)
    source_map = build_source_map(replay_results)
    write_json(OUT / "source-map.json", source_map)
    write_report(targets, cdx_results, replay_results, state)
    summary = {
        "schema_version": 1,
        "network_performed": True,
        "anchor_timestamp": ANCHOR,
        "baseline_window": {"from": BASELINE_FROM, "to": ANCHOR},
        "late_window": {"from": BASELINE_FROM, "to": LATE_TO, "only_when_baseline_has_no_valid_page_row": True},
        "request_count": state.get("request_count"),
        "response_bytes": state.get("response_bytes"),
        "max_requests": MAX_REQUESTS,
        "max_response_bytes": MAX_TOTAL_RESPONSE_BYTES,
        "stop_reason": state.get("stop_reason") or "plan_complete",
        "cdx_results": cdx_results,
        "replays": replay_results,
        "accepted_files": len(source_map["files"]),
        "request_log": "research/navigation-gaps-20261015/wayback-missing/request-log.json",
        "source_map": "research/navigation-gaps-20261015/wayback-missing/source-map.json",
        "scope": "three exact navigation pages; no CSS/image expansion; business trial content remains static historical material",
    }
    write_json(OUT / "summary.json", summary)
    write_sanitized_summary(targets, cdx_results, replay_results, state)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", action="append", dest="targets", choices=[target["id"] for target in TARGETS])
    parser.add_argument("--cdx-only", action="store_true", help="query baseline CDX only and stop before late queries/replays")
    parser.add_argument("--retry-invalid", choices=[target["id"] for target in TARGETS], help="select the next saved late CDX row after a locally rejected replay")
    args = parser.parse_args(argv)
    if args.retry_invalid:
        print(json.dumps({"retry_target": args.retry_invalid, "selected_timestamp": prepare_retry_override(args.retry_invalid)}, ensure_ascii=False))
    target_ids = args.targets or [target["id"] for target in TARGETS]
    result = run(target_ids, cdx_only=bool(args.cdx_only))
    print(json.dumps({"request_count": result.get("request_count"), "stop_reason": result.get("stop_reason"), "accepted_files": result.get("accepted_files")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

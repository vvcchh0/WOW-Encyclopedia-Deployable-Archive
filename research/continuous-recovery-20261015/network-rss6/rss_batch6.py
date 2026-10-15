"""NET-RSS-006 bounded exact RSS archive recovery.

The driver selects the newest twelve exact RSS originals from the accepted
local reconciliation, queries each exact URL in CDX, and replays at most one
latest pre-anchor status-200 capture.  It reuses the accepted core-pages3
transport and keeps all raw response material in this owned directory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
RECONCILIATION = ROOT / "research/continuous-recovery-20261015/local-target-reconcile/reconciliation.json"
ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/local-target-reconcile-acceptance.json"
CORE3_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"

EXPECTED_RECONCILIATION_SHA256 = "81f346c89100204d35448e5c1d20fcfa7532f3e9b7569b5edff2ea1886735016"
EXPECTED_ACCEPTANCE_REPORT_SHA256 = EXPECTED_RECONCILIATION_SHA256
MAX_TARGETS = 12
MAX_ATTEMPTS = 32
WINDOW_SECONDS = 8 * 60
MIN_INTERVAL_SECONDS = 1.2
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY_BYTES = 64 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 16 * 1024 * 1024
REDIRECT_CODES = {301, 302, 303, 307, 308}
STOP_HTTP_CODES = {429, 503}
RSS_RE = re.compile(r"^/news/rss-(\d{2})-(\d{4})\.xml$")


def load_core3() -> Any:
    spec = importlib.util.spec_from_file_location("wow_rss6_core3_reuse", CORE3_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load accepted core-pages3 helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    module.RAW = RAW
    module.USER_AGENT = "wow-recovery-rss6/20261015"
    return module


core = load_core3()


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


def disk_free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def parse_rss_month(target: str, original: str) -> tuple[int, int]:
    target_match = RSS_RE.fullmatch(target)
    original_match = re.fullmatch(r"http://www\.worldofwarcraft\.com/news/rss-(\d{2})-(\d{4})\.xml", original)
    if not target_match or not original_match:
        raise RuntimeError(f"RSS target/original is not exact expected form: {target} / {original}")
    if target_match.groups() != (original_match.group(1), original_match.group(2)):
        raise RuntimeError(f"RSS target/original month mismatch: {target} / {original}")
    month = int(target_match.group(1))
    year = int(target_match.group(2))
    if not 1 <= month <= 12:
        raise RuntimeError(f"invalid RSS month: {target}")
    return year, month


def verify_inputs() -> dict[str, Any]:
    if not RECONCILIATION.exists() or not ACCEPTANCE.exists():
        raise RuntimeError("RSS reconciliation input is missing")
    reconciliation_sha = sha256_file(RECONCILIATION)
    if reconciliation_sha != EXPECTED_RECONCILIATION_SHA256:
        raise RuntimeError(f"reconciliation SHA mismatch: expected {EXPECTED_RECONCILIATION_SHA256}, got {reconciliation_sha}")
    acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    if not acceptance.get("accepted") or acceptance.get("network_requests") != 0:
        raise RuntimeError("local-target reconciliation acceptance is not accepted or records network")
    if acceptance.get("report_sha256") != EXPECTED_ACCEPTANCE_REPORT_SHA256:
        raise RuntimeError("acceptance report SHA does not match the frozen reconciliation")
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    if reconciliation.get("network_performed") or reconciliation.get("network_request_count") != 0:
        raise RuntimeError("reconciliation input unexpectedly records network activity")
    rss_rows: list[dict[str, Any]] = []
    for row in reconciliation.get("rows") or []:
        target = str(row.get("target") or "")
        original = str(row.get("exact_original_url") or "")
        if RSS_RE.fullmatch(target):
            year, month = parse_rss_month(target, original)
            if not row.get("source_menu"):
                raise RuntimeError(f"RSS row has no source_menu evidence: {target}")
            value = dict(row)
            value["year"] = year
            value["month"] = month
            value["query_original"] = original
            rss_rows.append(value)
    if len(rss_rows) != 23:
        raise RuntimeError(f"expected 23 RSS reconciliation rows, got {len(rss_rows)}")
    if len({row["query_original"] for row in rss_rows}) != 23:
        raise RuntimeError("RSS exact originals are not unique")
    selected = sorted(rss_rows, key=lambda row: (row["year"], row["month"], row["query_original"]), reverse=True)[:MAX_TARGETS]
    if len(selected) != MAX_TARGETS:
        raise RuntimeError("unable to select twelve RSS targets")
    return {
        "reconciliation": reconciliation,
        "acceptance": acceptance,
        "reconciliation_sha256": reconciliation_sha,
        "acceptance_sha256": sha256_file(ACCEPTANCE),
        "rss_total": rss_rows,
        "selected": selected,
    }


def plan_document(inputs: dict[str, Any]) -> dict[str, Any]:
    selected = inputs["selected"]
    return {
        "schema": "continuous-wow-rss6-plan/v1",
        "mode": "exact_cdx_then_latest_preanchor_200_replay",
        "prepared_utc": now_utc(),
        "inputs": {
            "reconciliation": str(RECONCILIATION.relative_to(ROOT)).replace("\\", "/"),
            "reconciliation_sha256": inputs["reconciliation_sha256"],
            "acceptance": str(ACCEPTANCE.relative_to(ROOT)).replace("\\", "/"),
            "acceptance_sha256": inputs["acceptance_sha256"],
            "rss_total": len(inputs["rss_total"]),
        },
        "selection": {
            "rule": "sort exact originals by URL-declared year/month descending; retain twelve distinct exact originals",
            "selected_count": len(selected),
            "excluded_count": len(inputs["rss_total"]) - len(selected),
            "excluded_targets": [row["target"] for row in inputs["rss_total"] if row not in selected],
        },
        "targets": [
            {
                "rank": rank,
                "target": row["target"],
                "query_original": row["query_original"],
                "year": row["year"],
                "month": row["month"],
                "source_menu": row["source_menu"],
            }
            for rank, row in enumerate(selected, start=1)
        ],
        "policy": {
            "max_targets": MAX_TARGETS,
            "max_attempts": MAX_ATTEMPTS,
            "window_seconds": WINDOW_SECONDS,
            "minimum_start_interval_seconds": MIN_INTERVAL_SECONDS,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
            "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
            "direct_first_then_confirmed_transport": True,
            "direct_connect_timeout_seconds": core.DIRECT_CONNECT_SECONDS,
            "direct_total_timeout_seconds": core.DIRECT_MAX_SECONDS,
            "proxy": core.PROXY,
            "proxy_connect_timeout_seconds": core.PROXY_CONNECT_SECONDS,
            "proxy_total_timeout_seconds": core.PROXY_MAX_SECONDS,
            "automatic_redirects": 0,
            "manual_redirect_follow": 0,
            "stop_http_codes": sorted(STOP_HTTP_CODES),
            "tls_verification": "curl_default_verification_enabled",
            "uri_policy": "same scheme and lower-cased host; only default ports normalize; bare/www and http/https remain separate",
            "cdx_policy": "exact matchType=exact, 2004-01-01 through 2008-05-12 anchor; one latest preanchor status-200 replay",
            "body_policy": "parse real body as RSS/XML or HTML; .xml extension never substitutes for body format",
            "script_policy": "do not execute body scripts",
        },
        "network_requests": 0,
        "ready": disk_free_bytes() >= MIN_FREE_BYTES,
    }


def write_preparation(inputs: dict[str, Any], plan: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    candidates = {
        "schema": "continuous-wow-rss6-candidates/v1",
        "generated_utc": now_utc(),
        "source_reconciliation_sha256": inputs["reconciliation_sha256"],
        "source_acceptance_sha256": inputs["acceptance_sha256"],
        "source_rss_target_count": len(inputs["rss_total"]),
        "selection_rule": plan["selection"],
        "network_requests": 0,
        "targets": plan["targets"],
        "execution_policy": plan["policy"],
        "execution": {"network_requests": 0, "status": "planned"},
    }
    write_json(OUT / "candidates.json", candidates)
    write_json(OUT / "batch-config.json", plan)
    write_json(OUT / "plan.json", plan)


def prepare() -> int:
    inputs = verify_inputs()
    plan = plan_document(inputs)
    write_preparation(inputs, plan)
    print(json.dumps({
        "mode": "plan_only",
        "source_rss_target_count": len(inputs["rss_total"]),
        "selected_target_count": len(inputs["selected"]),
        "selected_targets": [row["target"] for row in inputs["selected"]],
        "network_requests": 0,
        "reconciliation_sha256": inputs["reconciliation_sha256"],
        "disk_free_bytes": disk_free_bytes(),
    }, ensure_ascii=False))
    return 0


def request_serial(url: str, kind: str, target: str, state: Any, transport_state: dict[str, str | None]) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    transport = transport_state.get("transport")
    if transport is None:
        direct = core.run_request(url, "direct", kind, target, state, state.attempts + 1)
        attempts.append(direct)
        if direct.get("executed") and not direct.get("transport_error") and not state.stop_reason:
            transport_state["transport"] = "direct"
            return attempts
        if state.stop_reason or direct.get("source_status") in STOP_HTTP_CODES:
            return attempts
        proxy = core.run_request(url, "proxy", kind, target, state, state.attempts + 1)
        attempts.append(proxy)
        transport_state["transport"] = "proxy"
        return attempts
    attempts.append(core.run_request(url, transport, kind, target, state, state.attempts + 1))
    return attempts


def body_for_attempt(attempt: dict[str, Any] | None) -> bytes:
    if not attempt:
        return b""
    path = OUT / str((attempt.get("raw") or {}).get("body") or "")
    return path.read_bytes() if path.exists() else b""


def b32_sha1(body: bytes) -> str | None:
    import base64

    return base64.b32encode(hashlib.sha1(body).digest()).decode("ascii") if body else None


def body_metrics(attempt: dict[str, Any] | None, capture: dict[str, Any] | None) -> dict[str, Any]:
    body = body_for_attempt(attempt)
    expected = str((capture or {}).get("digest") or "").upper() or None
    calculated = b32_sha1(body)
    return {
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "cdx_digest_expected": expected,
        "cdx_digest_calculated": calculated,
        "cdx_digest_match": bool(expected and calculated and expected == calculated),
        "cdx_length": int(capture["length"]) if capture and str(capture.get("length", "")).isdigit() else None,
        "actual_memento": attempt.get("memento_datetime") if attempt else None,
        "source_status": attempt.get("source_status") if attempt else None,
        "content_type": attempt.get("content_type") if attempt else None,
        "raw_body_path": (attempt.get("raw") or {}).get("body") if attempt else None,
        "raw_headers_path": (attempt.get("raw") or {}).get("headers") if attempt else None,
    }


class TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = []
        self.headings: list[tuple[str, list[str]]] = []
        self._title = False
        self._heading: tuple[str, list[str]] | None = None
        self.visible: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name == "title":
            self._title = True
        elif name in {"h1", "h2", "h3"}:
            self._heading = (name, [])

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name == "title":
            self._title = False
        elif self._heading is not None and name == self._heading[0]:
            heading, parts = self._heading
            self.headings.append((heading, parts))
            self._heading = None

    def handle_data(self, data: str) -> None:
        clean = " ".join(data.split())
        if not clean:
            return
        if self._title:
            self.title.append(clean)
        if self._heading is not None:
            self._heading[1].append(clean)
        self.visible.append(clean)


def decode_text(body: bytes) -> tuple[str, str]:
    try:
        return body.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return body.decode("iso-8859-1", errors="replace"), "iso-8859-1"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def element_text(element: ET.Element | None) -> str | None:
    if element is None:
        return None
    value = " ".join("".join(element.itertext()).split())
    return value or None


def descendants(element: ET.Element, names: set[str]) -> list[ET.Element]:
    return [node for node in element.iter() if local_name(str(node.tag)) in names]


def parse_date_month(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    match = re.search(r"\b(19\d{2}|20\d{2})[-/]([01]\d)\b", value)
    if match:
        return int(match.group(1)), int(match.group(2))
    try:
        parsed = parsedate_to_datetime(value)
        return parsed.year, parsed.month
    except (TypeError, ValueError, OverflowError):
        return None


def month_evidence(pubdates: list[str], expected_year: int, expected_month: int) -> dict[str, Any]:
    matching: list[str] = []
    mismatch: list[str] = []
    unparseable: list[str] = []
    for value in pubdates:
        parsed = parse_date_month(value)
        if parsed is None:
            unparseable.append(value)
        elif parsed == (expected_year, expected_month):
            matching.append(value)
        else:
            mismatch.append(value)
    if matching and not mismatch:
        state = "match"
    elif matching and mismatch:
        state = "mixed"
    elif mismatch:
        state = "mismatch"
    else:
        state = "unknown"
    return {
        "expected_year": expected_year,
        "expected_month": expected_month,
        "date_field_count": len(pubdates),
        "matching_count": len(matching),
        "mismatch_count": len(mismatch),
        "unparseable_count": len(unparseable),
        "matching_examples": matching[:10],
        "mismatch_examples": mismatch[:10],
        "unparseable_examples": unparseable[:10],
        "state": state,
    }


def rss_observation(body: bytes, content_type: str | None, expected_year: int, expected_month: int) -> dict[str, Any]:
    text, encoding = decode_text(body)
    root_name: str | None = None
    root: ET.Element | None = None
    parse_error: str | None = None
    try:
        root = ET.fromstring(body)
        root_name = local_name(str(root.tag))
    except (ET.ParseError, ValueError) as exc:
        parse_error = type(exc).__name__ + ": " + str(exc)
    rss_like = root_name in {"rss", "rdf", "feed", "channel"}
    if not root or not rss_like:
        return {
            "encoding": encoding,
            "mime": (content_type or "").split(";", 1)[0].strip().lower(),
            "root": root_name,
            "parse_ok": bool(root),
            "parse_error": parse_error,
            "rss_like": False,
            "title": None,
            "link": None,
            "item_count": 0,
            "pubdates": [],
            "month_evidence": month_evidence([], expected_year, expected_month),
        }
    channel = root if root_name in {"channel", "feed"} else next(iter(descendants(root, {"channel"})), root)
    title = element_text(next(iter(descendants(channel, {"title"})), None))
    link = element_text(next(iter(descendants(channel, {"link"})), None))
    items = [node for node in channel.iter() if local_name(str(node.tag)) in {"item", "entry"}]
    pubdates: list[str] = []
    for item in items:
        date_node = next(iter(descendants(item, {"pubdate", "published", "updated", "date"})), None)
        value = element_text(date_node)
        if value:
            pubdates.append(value)
    return {
        "encoding": encoding,
        "mime": (content_type or "").split(";", 1)[0].strip().lower(),
        "root": root_name,
        "parse_ok": True,
        "parse_error": None,
        "rss_like": True,
        "title": title,
        "link": link,
        "item_count": len(items),
        "pubdates": pubdates[:200],
        "month_evidence": month_evidence(pubdates, expected_year, expected_month),
    }


def html_observation(body: bytes, content_type: str | None) -> dict[str, Any]:
    text, encoding = decode_text(body)
    parser = TextHTMLParser()
    parse_ok = True
    parse_error = None
    try:
        parser.feed(text[:4 * 1024 * 1024])
        parser.close()
    except Exception as exc:  # pragma: no cover - response-dependent
        parse_ok = False
        parse_error = type(exc).__name__ + ": " + str(exc)
    visible = " ".join(parser.visible)
    info = core.html_info(body, content_type)
    return {
        "encoding": encoding,
        "mime": (content_type or "").split(";", 1)[0].strip().lower(),
        "parse_ok": parse_ok,
        "parse_error": parse_error,
        "title": " ".join(parser.title)[:500] or None,
        "headings": [{"tag": tag, "text": " ".join(parts)[:500]} for tag, parts in parser.headings[:50]],
        "content_identity_sha256": hashlib.sha256(visible.encode("utf-8")).hexdigest() if visible else None,
        "content_preview": visible[:500] if visible else None,
        "archive_markers": info.get("markers") or [],
        "is_html": bool(info.get("is_html")),
    }


def validate_body(attempt: dict[str, Any] | None, capture: dict[str, Any], expected_year: int, expected_month: int) -> tuple[bool, str, dict[str, Any]]:
    body = body_for_attempt(attempt)
    metrics = body_metrics(attempt, capture)
    if not attempt or not attempt.get("executed"):
        return False, "replay_not_executed", metrics
    if attempt.get("source_status") != 200:
        return False, "source_status_not_200", metrics
    if not metrics.get("actual_memento"):
        return False, "missing_actual_memento", metrics
    if metrics.get("cdx_digest_match") is not True:
        return False, "cdx_digest_mismatch", metrics
    rss = rss_observation(body, metrics.get("content_type"), expected_year, expected_month)
    if rss.get("rss_like") and rss.get("parse_ok"):
        state = rss["month_evidence"]["state"]
        metrics["body_format"] = "rss_xml"
        metrics["body_observation"] = rss
        return True, f"valid_rss_month_{state}", metrics
    html = html_observation(body, metrics.get("content_type"))
    metrics["body_observation"] = html
    if html.get("is_html"):
        if set(html.get("archive_markers") or []).intersection({"wayback_machine", "not_archived", "no_captures", "page_not_found", "page_cannot_be_found"}):
            return False, "not_archived_or_error_html", metrics
        metrics["body_format"] = "html"
        return True, "valid_html_payload", metrics
    if body.lstrip().startswith(b"<") or metrics.get("content_type", "").lower().split(";", 1)[0] in {"application/xml", "text/xml", "application/rss+xml"}:
        metrics["body_format"] = "xml_other_or_invalid"
        return False, "xml_not_rss_or_parse_failed", metrics
    metrics["body_format"] = "opaque"
    return False, "unrecognized_body_format", metrics


def valid_200_captures(records: list[dict[str, str]], original_url: str) -> list[dict[str, Any]]:
    return [row for row in core.valid_cdx_records(records, original_url) if row.get("statuscode_int") == 200]


def select_latest(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    return sorted(records, key=lambda row: row.get("timestamp", ""), reverse=True)[0] if records else None


def public_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    return core.source_attempt_view(attempt)


def target_result(item: dict[str, Any], query_attempts: list[dict[str, Any]], records: list[dict[str, str]], eligible: list[dict[str, Any]], selected: dict[str, Any] | None, replay_attempts: list[dict[str, Any]], validation: dict[str, Any] | None, category: str, reason: str) -> dict[str, Any]:
    query_attempt = next((attempt for attempt in reversed(query_attempts) if attempt.get("executed")), None)
    final = next((attempt for attempt in reversed(replay_attempts) if attempt.get("executed")), None)
    return {
        "rank": item["rank"],
        "target": item["target"],
        "query_original": item["query_original"],
        "year": item["year"],
        "month": item["month"],
        "source_menu": item["source_menu"],
        "query_url": core.cdx_query_url(item["query_original"]),
        "cdx": {
            "query_performed": bool(query_attempts),
            "source_status": query_attempt.get("source_status") if query_attempt else None,
            "source_response_count": sum(attempt.get("source_status") is not None for attempt in query_attempts),
            "capture_index_count": len(records),
            "eligible_status_200_count": len(eligible),
            "redirect_index_count": sum(str(row.get("statuscode")) in {str(code) for code in REDIRECT_CODES} for row in records),
            "capture_records": records,
            "selected_capture": selected,
            "other_origin_metadata": core.other_origin_metadata(records, item["query_original"]),
            "attempts": [public_attempt(attempt) for attempt in query_attempts],
        },
        "selected_capture": selected,
        "replay_attempt_count": len([attempt for attempt in replay_attempts if attempt.get("executed")]),
        "replay_source_response_count": sum(attempt.get("source_status") is not None for attempt in replay_attempts),
        "replay_hops": [public_attempt(attempt) for attempt in replay_attempts],
        "category": category,
        "reason": reason,
        "actual_memento": final.get("memento_datetime") if final else None,
        "source_status": final.get("source_status") if final else None,
        "content_type": final.get("content_type") if final else None,
        "body_bytes": len(body_for_attempt(final)),
        "body_sha256": final.get("body_sha256") if final else None,
        "validation": validation,
        "entity_valid": bool(validation and validation.get("valid")),
        "unrequested_reason": reason if not replay_attempts and category in {"not_requested", "cdx_empty_in_range", "cdx_no_valid_200", "transport_error"} else None,
    }


def source_map_entry(result: dict[str, Any]) -> dict[str, Any]:
    capture = result["selected_capture"] or {}
    metrics = result["validation"] or {}
    observation = metrics.get("body_observation") or {}
    return {
        "target": result["target"],
        "query_original": result["query_original"],
        "captured_original": capture.get("original"),
        "actual_memento": result.get("actual_memento"),
        "source_status": result.get("source_status"),
        "content_type": result.get("content_type"),
        "body_bytes": result.get("body_bytes"),
        "body_sha256": result.get("body_sha256"),
        "cdx_digest": capture.get("digest"),
        "cdx_digest_calculated": metrics.get("cdx_digest_calculated"),
        "cdx_digest_match": metrics.get("cdx_digest_match"),
        "raw_body_path": metrics.get("raw_body_path"),
        "raw_headers_path": metrics.get("raw_headers_path"),
        "capture_timestamp": capture.get("timestamp"),
        "capture_mimetype": capture.get("mimetype"),
        "cdx_length": metrics.get("cdx_length"),
        "body_format": metrics.get("body_format"),
        "rss_observation": observation if metrics.get("body_format") == "rss_xml" else None,
        "html_observation": observation if metrics.get("body_format") == "html" else None,
        "selection": "latest pre-anchor same-origin status-200 CDX row; review before any integration",
    }


def redirect_index_entries(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for result in results:
        for row in result.get("cdx", {}).get("capture_records") or []:
            if str(row.get("statuscode")) in {str(code) for code in REDIRECT_CODES}:
                entries.append({
                    "evidence_type": "cdx_index_redirect_row",
                    "target": result["target"],
                    "query_original": result["query_original"],
                    "capture": row,
                    "replayed": False,
                    "followed": False,
                })
    for result in results:
        for hop in result.get("replay_hops") or []:
            if hop.get("source_status") in REDIRECT_CODES:
                entries.append({
                    "evidence_type": "replay_redirect_response",
                    "target": result["target"],
                    "query_original": result["query_original"],
                    "source_status": hop.get("source_status"),
                    "location": hop.get("location"),
                    "actual_memento": hop.get("memento_datetime"),
                    "replayed": True,
                    "followed": False,
                    "raw_headers_path": (hop.get("raw") or {}).get("headers"),
                })
    return entries


def aggregate_attempts(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    for result in results:
        attempts.extend(result.get("cdx", {}).get("attempts") or [])
        attempts.extend(result.get("replay_hops") or [])
    return attempts


def timing(attempts: list[dict[str, Any]]) -> tuple[float, float | None]:
    starts = [datetime.fromisoformat(item["started_utc"]) for item in attempts if item.get("started_utc")]
    finished = [datetime.fromisoformat(item["finished_utc"]) for item in attempts if item.get("finished_utc")]
    gaps = [
        (datetime.fromisoformat(attempts[index + 1]["started_utc"]) - datetime.fromisoformat(attempts[index]["started_utc"])).total_seconds()
        for index in range(len(attempts) - 1)
        if attempts[index].get("started_utc") and attempts[index + 1].get("started_utc")
    ]
    if not starts or not finished:
        return 0.0, min(gaps) if gaps else None
    return (max(finished) - min(starts)).total_seconds(), min(gaps) if gaps else None


def public_summary(report: dict[str, Any], source_map: dict[str, Any], redirects: list[dict[str, Any]]) -> None:
    summary = {
        "schema": "continuous-wow-rss6-summary/v1",
        "report_sha256": sha256_file(OUT / "batch-report.json"),
        "inputs": report["inputs"],
        "request_window_started_utc": report["started_utc"],
        "request_window_finished_utc": report["request_window_finished_utc"],
        "report_updated_utc": report["report_updated_utc"],
        "network_requests": report["source_request_count"],
        "source_response_count": report["source_response_count"],
        "category_counts": report["category_counts"],
        "valid_entity_count": report["valid_entity_count"],
        "targets": [
            {
                "rank": row["rank"],
                "target": row["target"],
                "category": row["category"],
                "capture_timestamp": (row.get("selected_capture") or {}).get("timestamp"),
                "captured_original": (row.get("selected_capture") or {}).get("original"),
                "source_status": row.get("source_status"),
                "actual_memento": row.get("actual_memento"),
                "body_bytes": row.get("body_bytes"),
                "body_sha256": row.get("body_sha256"),
                "body_format": (row.get("validation") or {}).get("body_format"),
                "month_evidence": ((row.get("validation") or {}).get("body_observation") or {}).get("month_evidence"),
                "reason": row.get("reason"),
            }
            for row in report["results"]
        ],
        "source_map_entries": len(source_map["entries"]),
        "redirect_evidence_count": len(redirects),
        "raw_local_only": True,
        "no_entity_copied_into_mirror": True,
    }
    write_json(OUT / "sanitized-summary.json", summary)
    lines = [
        "# NET-RSS-006 sanitized recovery summary",
        "",
        f"Reconciliation SHA-256: {report['inputs']['reconciliation_sha256']}.",
        f"Request window: {report['started_utc']} to {report['request_window_finished_utc']}; report updated: {report['report_updated_utc']}.",
        f"Attempts: {report['source_request_count']}; source responses: {report['source_response_count']}; failed attempts: {report['failed_attempt_count']}; CDX responses: {report['cdx_source_response_count']}; replay responses: {report['replay_source_response_count']}; valid entities: {report['valid_entity_count']}; redirect evidence: {len(redirects)}.",
        "Categories: " + ", ".join(f"{key} {value}" for key, value in sorted(report["category_counts"].items())) + ".",
        f"Disk free before/after: {report['preflight']['disk_free_bytes_before']} / {report['preflight']['disk_free_bytes_after']} bytes.",
        "",
        "| # | target | category | capture | source HTTP | Memento | format | items | month state | bytes | reason |",
        "|---:|---|---|---|---:|---|---|---:|---|---:|---|",
    ]
    for row in report["results"]:
        observation = (row.get("validation") or {}).get("body_observation") or {}
        lines.append(
            f"| {row['rank']} | {row['target']} | {row['category']} | {(row.get('selected_capture') or {}).get('timestamp') or ''} | {row.get('source_status') or ''} | {row.get('actual_memento') or ''} | {(row.get('validation') or {}).get('body_format') or ''} | {observation.get('item_count') or ''} | {(observation.get('month_evidence') or {}).get('state') or ''} | {row.get('body_bytes') or 0} | {row.get('reason') or ''} |"
        )
    lines.extend([
        "",
        "RSS/XML and .xml-served HTML were classified from the real body. No body script was executed; redirects remain separate evidence.",
        "Original headers, traces, and bodies remain only in this batch raw directory. No entity was copied into the offline mirror.",
        "",
    ])
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")


def execute() -> int:
    inputs = verify_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    if (OUT / "batch-report.json").exists():
        raise RuntimeError("refusing network rerun: batch-report.json already exists in owned output")
    plan = plan_document(inputs)
    write_preparation(inputs, plan)
    disk_before = disk_free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk free {disk_before} below {MIN_FREE_BYTES}")
    state = core.RunState(time.monotonic())
    started_utc = now_utc()
    transport_state: dict[str, str | None] = {"transport": None}
    results: list[dict[str, Any]] = []
    for rank, row in enumerate(inputs["selected"], start=1):
        item = {
            "rank": rank,
            "target": row["target"],
            "query_original": row["query_original"],
            "year": row["year"],
            "month": row["month"],
            "source_menu": row["source_menu"],
        }
        query_url = core.cdx_query_url(item["query_original"])
        query_attempts = request_serial(query_url, "cdx", item["query_original"], state, transport_state) if state.check_limits() else []
        query_attempt = next((attempt for attempt in reversed(query_attempts) if attempt.get("executed")), None)
        records = (query_attempt or {}).get("cdx_records") or []
        eligible = valid_200_captures(records, item["query_original"]) if query_attempt and query_attempt.get("source_status") == 200 and not query_attempt.get("transport_error") else []
        selected = select_latest(eligible)
        replay_attempts: list[dict[str, Any]] = []
        validation: dict[str, Any] | None = None
        if query_attempt is None:
            category, reason = "not_requested", state.stop_reason or "query_not_requested"
        elif query_attempt.get("transport_error"):
            category, reason = "transport_error", query_attempt.get("transport_reason") or "query_transport_error"
        elif query_attempt.get("source_status") in STOP_HTTP_CODES:
            category, reason = "rate_limited", f"source_status_{query_attempt.get('source_status')}"
        elif not query_attempt.get("cdx_parse_valid"):
            category, reason = "cdx_invalid", query_attempt.get("cdx_parse_error") or "cdx_parse_failed"
        elif not records:
            category, reason = "cdx_empty_in_range", "no_capture_rows_in_query_range"
        elif not eligible:
            category, reason = "cdx_no_valid_200", "no_same_origin_preanchor_status_200_capture"
        elif not state.check_limits():
            category, reason = "not_requested", state.stop_reason or "limit_before_replay"
        else:
            replay_attempts = request_serial(core.replay_url(selected), "replay", item["query_original"], state, transport_state)
            final = next((attempt for attempt in reversed(replay_attempts) if attempt.get("executed")), None)
            if final and final.get("source_status") in REDIRECT_CODES:
                category, reason = "redirect_unfollowed", "redirect_evidence_only_no_automatic_follow"
            elif final and final.get("transport_error"):
                category, reason = "transport_error", final.get("transport_reason") or "replay_transport_error"
            elif final and final.get("source_status") in STOP_HTTP_CODES:
                category, reason = "rate_limited", f"source_status_{final.get('source_status')}"
            elif final and final.get("source_status") != 200:
                category, reason = "http_response", f"replay_source_status_{final.get('source_status')}"
            elif final:
                valid, body_category, metrics = validate_body(final, selected, item["year"], item["month"])
                metrics["valid"] = valid
                metrics["body_category"] = body_category
                validation = metrics
                category, reason = body_category, body_category
            else:
                category, reason = "transport_error", "replay_not_executed_or_no_response"
        result = target_result(item, query_attempts, records, eligible, selected, replay_attempts, validation, category, reason)
        if validation and validation.get("valid"):
            result["actual_memento"] = validation.get("actual_memento")
            result["source_status"] = validation.get("source_status")
            result["content_type"] = validation.get("content_type")
            result["body_bytes"] = validation.get("body_bytes")
            result["body_sha256"] = validation.get("body_sha256")
            result["entity_valid"] = True
        results.append(result)
        if state.stop_reason:
            continue
    request_window_finished_utc = now_utc()
    report_updated_utc = now_utc()
    disk_after = disk_free_bytes()
    attempts = aggregate_attempts(results)
    request_seconds, minimum_interval = timing(attempts)
    redirects = redirect_index_entries(results)
    categories: dict[str, int] = {}
    for result in results:
        categories[result["category"]] = categories.get(result["category"], 0) + 1
    source_entries = [source_map_entry(result) for result in results if result.get("entity_valid")]
    cdx_responses = sum(result["cdx"].get("source_response_count", 0) for result in results)
    replay_responses = sum(result.get("replay_source_response_count", 0) for result in results)
    report = {
        "schema": "continuous-wow-rss6-report/v1",
        "mode": "execute",
        "inputs": {
            "reconciliation_path": str(RECONCILIATION.relative_to(ROOT)).replace("\\", "/"),
            "reconciliation_sha256": inputs["reconciliation_sha256"],
            "acceptance_path": str(ACCEPTANCE.relative_to(ROOT)).replace("\\", "/"),
            "acceptance_sha256": inputs["acceptance_sha256"],
            "source_rss_target_count": len(inputs["rss_total"]),
            "selected_target_count": len(inputs["selected"]),
        },
        "selection": plan["selection"],
        "started_utc": started_utc,
        "request_window_finished_utc": request_window_finished_utc,
        "finished_utc": request_window_finished_utc,
        "report_updated_utc": report_updated_utc,
        "target_count": len(results),
        "source_request_count": state.attempts,
        "transport_attempt_count": state.attempts,
        "source_response_count": state.source_responses,
        "failed_attempt_count": state.failed_attempts,
        "cdx_source_response_count": cdx_responses,
        "replay_source_response_count": replay_responses,
        "capture_index_count_fetched": sum(result["cdx"].get("capture_index_count") or 0 for result in results),
        "eligible_status_200_capture_count": sum(result["cdx"].get("eligible_status_200_count") or 0 for result in results),
        "valid_entity_count": len(source_entries),
        "valid_rss_count": sum(result.get("validation", {}).get("body_format") == "rss_xml" for result in results if result.get("validation")),
        "valid_html_count": sum(result.get("validation", {}).get("body_format") == "html" for result in results if result.get("validation")),
        "total_body_bytes": state.total_body_bytes,
        "payload_body_bytes": sum(result.get("body_bytes") or 0 for result in results if result.get("entity_valid")),
        "category_counts": categories,
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "transport": {"confirmed_transport": transport_state.get("transport")},
        "preflight": {
            "drive": "D:",
            "disk_free_bytes_before": disk_before,
            "disk_free_bytes_after": disk_after,
            "minimum_free_bytes": MIN_FREE_BYTES,
        },
        "request_window_seconds": request_seconds,
        "minimum_start_interval_seconds": minimum_interval,
        "redirect_evidence_count": len(redirects),
        "policy": plan["policy"],
        "raw_local_only": True,
        "no_entity_copied_into_mirror": True,
        "results": results,
    }
    source_map = {
        "schema": "continuous-wow-rss6-source-map/v1",
        "generated_utc": report_updated_utc,
        "only_real_valid_payloads": True,
        "entries": source_entries,
    }
    output_candidates = {
        "schema": "continuous-wow-rss6-candidates/v1",
        "generated_utc": now_utc(),
        "source_reconciliation_sha256": inputs["reconciliation_sha256"],
        "source_acceptance_sha256": inputs["acceptance_sha256"],
        "source_rss_target_count": len(inputs["rss_total"]),
        "selection_rule": plan["selection"],
        "network_requests": state.attempts,
        "targets": plan["targets"],
        "execution_policy": plan["policy"],
        "execution": {"network_requests": state.attempts, "status": "completed", "request_window_finished_utc": request_window_finished_utc, "report_updated_utc": report_updated_utc},
    }
    write_json(OUT / "candidates.json", output_candidates)
    write_json(OUT / "batch-config.json", plan)
    write_json(OUT / "batch-report.json", report)
    write_json(OUT / "rss-source-map.json", source_map)
    write_json(OUT / "redirect-evidence.json", {"schema": "continuous-wow-rss6-redirect-evidence/v1", "generated_utc": report_updated_utc, "entries": redirects})
    public_summary(report, source_map, redirects)
    print(json.dumps({
        "target_count": len(results),
        "category_counts": categories,
        "attempts": state.attempts,
        "source_responses": state.source_responses,
        "cdx_source_responses": cdx_responses,
        "replay_source_responses": replay_responses,
        "valid_entities": len(source_entries),
        "valid_rss": report["valid_rss_count"],
        "valid_html": report["valid_html_count"],
        "payload_body_bytes": report["payload_body_bytes"],
        "total_body_bytes": state.total_body_bytes,
        "redirect_evidence": len(redirects),
        "stop_reason": state.stop_reason,
        "confirmed_transport": transport_state.get("transport"),
    }, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.execute:
        return execute()
    return prepare()


if __name__ == "__main__":
    raise SystemExit(main())

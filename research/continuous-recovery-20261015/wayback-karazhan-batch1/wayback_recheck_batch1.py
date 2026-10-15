"""Bounded direct-first Wayback recheck for the first 30 Karazhan TLS unknowns.

This worker is intentionally self-contained and writes only below its own
research directory.  It preserves raw HTTP evidence locally while keeping
the JSON/Markdown reports free of raw header and trace contents.
"""

from __future__ import annotations

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
from urllib.parse import urljoin, urlsplit

try:
    from PIL import Image
except Exception:  # pragma: no cover - reported in output
    Image = None


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
INPUT_REPORT = ROOT / "research/karazhan-recheck-20261015/batch-report.final.json"
INPUT_DOC = ROOT / "docs/karazhan-tls-recheck-20261015.md"
CURL = Path(r"C:\Windows\System32\curl.exe")
PROXY = "http://127.0.0.1:7890"
USER_AGENT = "karazhan-wayback-batch1/20261015"
MAX_TARGETS = 30
MAX_SOURCE_REQUESTS = 32
WINDOW_SECONDS = 8 * 60
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY = 64 * 1024 * 1024
MAX_ENTITY_BODY = 16 * 1024 * 1024
INTERVAL_SECONDS = 1.2
DIRECT_CONNECT_SECONDS = 4
DIRECT_MAX_SECONDS = 12
PROXY_CONNECT_SECONDS = 8
PROXY_MAX_SECONDS = 20
WAYBACK_HOSTS = {"web.archive.org", "wwwb-app0.archive.org"}
REDIRECT_CODES = {301, 302, 303, 307, 308}
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


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def relative(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def disk_free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def parse_headers(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip("\r")
        match = re.match(r"^HTTP/(?:\d(?:\.\d)?|2)\s+(\d{3})(?:\s+(.*))?$", line, re.I)
        if match:
            current = {
                "status": int(match.group(1)),
                "reason": match.group(2) or "",
                "headers": {},
            }
            blocks.append(current)
            continue
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key in current["headers"]:
            current["headers"][key] = current["headers"][key] + ", " + value
        else:
            current["headers"][key] = value
    return blocks


def source_blocks(header_text: str) -> list[dict[str, Any]]:
    return [
        block
        for block in parse_headers(header_text)
        if "connection established" not in str(block.get("reason", "")).lower()
    ]


def iso_memento(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        return value


def response_header(blocks: list[dict[str, Any]], name: str) -> str | None:
    if not blocks:
        return None
    value = blocks[-1].get("headers", {}).get(name.lower())
    return str(value) if value is not None else None


def response_status(blocks: list[dict[str, Any]], stdout: str) -> int | None:
    if blocks:
        return int(blocks[-1]["status"])
    match = re.search(r"(?<!\d)(\d{3})(?!\d)", stdout)
    if match and match.group(1) != "000":
        return int(match.group(1))
    return None


def memento_follow_url(location: str | None, base_url: str) -> str | None:
    if not location:
        return None
    candidate = urljoin(base_url, location)
    parts = urlsplit(candidate)
    if parts.scheme not in {"http", "https"}:
        return None
    if (parts.hostname or "").lower() not in WAYBACK_HOSTS:
        return None
    if not parts.path.startswith("/web/"):
        return None
    return candidate


def pillow_info(body: bytes) -> dict[str, Any]:
    result: dict[str, Any] = {
        "available": Image is not None,
        "verify": False,
        "load": False,
        "format": None,
        "size": None,
    }
    if Image is None or not body:
        return result
    try:
        with Image.open(io.BytesIO(body)) as image:
            result["format"] = image.format
            result["size"] = list(image.size)
            image.verify()
        with Image.open(io.BytesIO(body)) as image:
            image.load()
        result["verify"] = True
        result["load"] = True
    except Exception as exc:  # pragma: no cover - depends on response bytes
        result["error"] = type(exc).__name__ + ": " + str(exc)
    return result


def html_markers(body: bytes, content_type: str | None) -> dict[str, Any]:
    is_html = (content_type or "").lower().split(";", 1)[0].strip() in {
        "text/html",
        "application/xhtml+xml",
    }
    if not is_html and not body.lstrip().lower().startswith((b"<!doctype html", b"<html", b"<head")):
        return {"is_html": False, "markers": []}
    text = body[:2 * 1024 * 1024].decode("utf-8", errors="replace").lower()
    probes = (
        ("wayback_machine", "wayback machine"),
        ("not_archived", "not archived"),
        ("no_captures", "no captures"),
        ("not_found", "not found"),
        ("error_404", "404"),
        ("page_cannot_be_found", "page cannot be found"),
    )
    return {
        "is_html": True,
        "markers": [name for name, needle in probes if needle in text],
    }


def classify(final: dict[str, Any] | None, redirect_follow_skipped: str | None = None) -> tuple[str, dict[str, Any]]:
    if final is None:
        return "not_requested", {"reason": redirect_follow_skipped or "no_source_request"}
    status = final.get("source_status")
    content_type = final.get("content_type") or ""
    image = final.get("pillow") or {}
    html = final.get("html") or {}
    if final.get("transport_error"):
        return "transport_error", {
            "reason": final.get("transport_reason") or "curl_or_tls_failure",
            "source_status": status,
        }
    if status == 200 and content_type.lower().split(";", 1)[0].strip().startswith("image/"):
        if image.get("verify") and image.get("load"):
            return "valid_image", {
                "content_type": content_type,
                "source_status": status,
                "pillow": image,
            }
        return "soft404", {
            "reason": "image_mime_but_pillow_rejected_body",
            "content_type": content_type,
            "source_status": status,
            "pillow": image,
        }
    markers = set(html.get("markers") or [])
    if status == 404 or markers.intersection({"wayback_machine", "not_archived", "no_captures"}):
        return "not_archived", {
            "reason": "wayback_not_archived_or_404",
            "content_type": content_type,
            "source_status": status,
            "pillow": image,
            "html": html,
        }
    return "soft404", {
        "reason": "non_image_or_soft404_response",
        "content_type": content_type,
        "source_status": status,
        "pillow": image,
        "html": html,
        "redirect_follow_skipped": redirect_follow_skipped,
    }


class RunState:
    def __init__(self, started_monotonic: float) -> None:
        self.started_monotonic = started_monotonic
        self.last_start: float | None = None
        self.source_requests = 0
        self.source_responses = 0
        self.transport_attempts = 0
        self.failed_attempts = 0
        self.total_body_bytes = 0
        self.fail_streak = 0
        self.stop_reason: str | None = None
        self.stop_detail: dict[str, Any] = {}
        self.rate_limit: dict[str, Any] | None = None

    def check_limits(self) -> bool:
        if self.stop_reason:
            return False
        if disk_free_bytes() < MIN_FREE_BYTES:
            self.stop_reason = "disk_free_below_threshold"
            return False
        if time.monotonic() - self.started_monotonic >= WINDOW_SECONDS:
            self.stop_reason = "network_window_exhausted"
            return False
        if self.source_requests >= MAX_SOURCE_REQUESTS:
            self.stop_reason = "source_request_limit"
            return False
        if self.total_body_bytes >= MAX_TOTAL_BODY:
            self.stop_reason = "total_body_limit"
            return False
        return True

    def wait_for_interval(self) -> bool:
        if not self.check_limits():
            return False
        if self.last_start is not None:
            wait = INTERVAL_SECONDS - (time.monotonic() - self.last_start)
            if wait > 0:
                time.sleep(wait)
        if not self.check_limits():
            return False
        self.last_start = time.monotonic()
        self.source_requests += 1
        return True

    def note(self, status: int | None, curl_exit: int | None, body_bytes: int, transport_error: bool, retry_after: str | None) -> None:
        self.transport_attempts += 1
        if status is not None:
            self.source_responses += 1
        if transport_error:
            self.failed_attempts += 1
        self.total_body_bytes += body_bytes
        if transport_error:
            self.fail_streak += 1
        else:
            self.fail_streak = 0
        if status in STOP_HTTP_CODES:
            self.rate_limit = {"status": status, "retry_after": retry_after}
            self.stop_reason = f"endpoint_status_{status}"
            self.stop_detail = {"status": status, "retry_after": retry_after}
        elif self.fail_streak >= 5 and not self.stop_reason:
            self.stop_reason = "five_consecutive_tls_or_transport_failures"
            self.stop_detail = {
                "failure_streak": self.fail_streak,
                "last_source_status": status,
                "last_curl_exit": curl_exit,
            }
        elif self.total_body_bytes > MAX_TOTAL_BODY and not self.stop_reason:
            self.stop_reason = "total_body_limit"
        if body_bytes > MAX_ENTITY_BODY and not self.stop_reason:
            self.stop_reason = "single_entity_body_limit"
        del curl_exit  # retained in the individual hop record


def run_request(url: str, transport: str, stem: str, hop: int, state: RunState) -> dict[str, Any]:
    if not state.wait_for_interval():
        return {
            "executed": False,
            "transport": transport,
            "hop": hop,
            "url": url,
            "unrequested_reason": state.stop_reason or "limit_before_source_request",
        }
    prefix = f"{safe_name(stem)}.{transport}.h{hop}"
    headers_path = RAW / f"{prefix}.headers.txt"
    body_path = RAW / f"{prefix}.body"
    stderr_path = RAW / f"{prefix}.stderr.txt"
    trace_path = RAW / f"{prefix}.trace.txt"
    if transport == "direct":
        connect_timeout = DIRECT_CONNECT_SECONDS
        max_time = DIRECT_MAX_SECONDS
        transport_args = ["--proxy", "", "--noproxy", "*"]
    else:
        connect_timeout = PROXY_CONNECT_SECONDS
        max_time = PROXY_MAX_SECONDS
        transport_args = ["--proxy", PROXY, "--noproxy", ""]
    command = [
        str(CURL),
        *transport_args,
        "--connect-timeout", str(connect_timeout),
        "--max-time", str(max_time),
        "--max-redirs", "0",
        "--max-filesize", str(MAX_ENTITY_BODY),
        "--silent", "--show-error",
        "--trace-time", "--trace-ascii", str(trace_path),
        "--dump-header", str(headers_path),
        "--output", str(body_path),
        "--write-out", "%{http_code}",
        "--user-agent", USER_AGENT,
        url,
    ]
    started = time.monotonic()
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
    except Exception as exc:  # pragma: no cover - OS/process failure
        curl_exit = None
        stderr_path.write_text(type(exc).__name__ + ": " + str(exc), encoding="utf-8")
    duration_ms = round((time.monotonic() - started) * 1000, 1)
    header_text = headers_path.read_text(encoding="iso-8859-1", errors="replace") if headers_path.exists() else ""
    blocks = source_blocks(header_text)
    if not body_path.exists():
        body_path.write_bytes(b"")
    body = body_path.read_bytes() if body_path.exists() else b""
    status = response_status(blocks, stdout)
    curl_transport_error = status is None or curl_exit != 0
    content_type = response_header(blocks, "content-type")
    location = response_header(blocks, "location")
    memento = iso_memento(response_header(blocks, "memento-datetime"))
    retry_after = response_header(blocks, "retry-after")
    image = pillow_info(body)
    html = html_markers(body, content_type)
    transport_reason = None
    if curl_transport_error:
        transport_reason = "no_http_status" if status is None else f"curl_exit_{curl_exit}"
    state.note(status, curl_exit, len(body), curl_transport_error, retry_after)
    record = {
        "executed": True,
        "transport": transport,
        "hop": hop,
        "url": url,
        "curl_exit": curl_exit,
        "duration_ms": duration_ms,
        "source_status": status,
        "content_type": content_type,
        "location": location,
        "retry_after": retry_after,
        "memento_datetime": memento,
        "body_path": relative(body_path),
        "headers_path": relative(headers_path),
        "stderr_path": relative(stderr_path),
        "trace_path": relative(trace_path),
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "transport_error": curl_transport_error,
        "transport_reason": transport_reason,
        "pillow": image,
        "html": html,
    }
    return record


def old_source_statuses(item: dict[str, Any]) -> list[Any]:
    statuses: list[Any] = []
    for hop in item.get("hops") or []:
        statuses.append(hop.get("source_status"))
    return statuses


def old_evidence_pointers(item: dict[str, Any]) -> list[dict[str, Any]]:
    pointers: list[dict[str, Any]] = []
    for hop in item.get("hops") or []:
        for key in ("body_path", "headers_path", "stderr_path", "trace_path"):
            value = hop.get(key)
            if value:
                pointers.append({"kind": key.removesuffix("_path"), "path": value})
    return pointers


def select_candidates(report: dict[str, Any]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for report_index, item in enumerate(report.get("results") or []):
        statuses = old_source_statuses(item)
        original_url = str(item.get("original_url") or "")
        if item.get("category") != "transport_error":
            continue
        if any(status is not None for status in statuses):
            continue
        if not original_url or original_url in seen_urls:
            continue
        seen_urls.add(original_url)
        selected.append(
            {
                "candidate_rank": len(selected) + 1,
                "report_index": report_index,
                "old_target_id": item.get("target_id"),
                "number": item.get("number"),
                "kind": item.get("kind"),
                "original_url": original_url,
                "request_url": item.get("request_url"),
                "request_hint": item.get("request_hint"),
                "old_category": item.get("category"),
                "old_source_statuses": statuses,
                "old_evidence_pointers": old_evidence_pointers(item),
            }
        )
        if len(selected) >= MAX_TARGETS:
            break
    return selected


def make_candidates(report: dict[str, Any], disk_before: int) -> dict[str, Any]:
    selected = select_candidates(report)
    if len(selected) != MAX_TARGETS:
        raise RuntimeError(f"expected {MAX_TARGETS} candidates, found {len(selected)}")
    value = {
        "schema": "wayback-karazhan-batch1-candidates-20261015.v1",
        "selection": {
            "source_report": str(INPUT_REPORT.relative_to(ROOT)).replace("\\", "/"),
            "source_report_sha256": sha256_file(INPUT_REPORT),
            "source_tls_doc": str(INPUT_DOC.relative_to(ROOT)).replace("\\", "/"),
            "source_tls_doc_sha256": sha256_file(INPUT_DOC),
            "criteria": "category=transport_error and every prior hop source_status is null; first 30 distinct original_url in report order",
            "excluded_explicit_not_archived": 59,
            "selected_count": len(selected),
        },
        "preflight": {
            "generated_utc": now_utc(),
            "drive": "D:",
            "free_bytes_before": disk_before,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "within_threshold": disk_before >= MIN_FREE_BYTES,
        },
        "selected": selected,
    }
    write_json(OUT / "candidates.json", value)
    return value


def result_record(candidate: dict[str, Any], attempts: list[dict[str, Any]], redirect_skip: str | None = None) -> dict[str, Any]:
    executed = [attempt for attempt in attempts if attempt.get("executed")]
    final = executed[-1] if executed else None
    category, detail = classify(final, redirect_skip)
    return {
        "candidate_rank": candidate["candidate_rank"],
        "report_index": candidate["report_index"],
        "target_id": candidate["old_target_id"],
        "number": candidate["number"],
        "kind": candidate["kind"],
        "original_url": candidate["original_url"],
        "request_url": candidate["request_url"],
        "request_hint": candidate["request_hint"],
        "old_target_id": candidate["old_target_id"],
        "old_category": candidate["old_category"],
        "old_source_statuses": candidate["old_source_statuses"],
        "old_evidence_pointers": candidate["old_evidence_pointers"],
        "category": category,
        "detail": detail,
        "attempt_count": len(executed),
        "hops": [
            {
                key: value
                for key, value in attempt.items()
                if key not in {"pillow", "html"}
            }
            | {
                "decode": attempt.get("pillow"),
                "decoded_size": (attempt.get("pillow") or {}).get("size"),
                "html_markers": attempt.get("html"),
            }
            for attempt in attempts
        ],
        "actual_memento": final.get("memento_datetime") if final else None,
        "actual_memento_or_null": final.get("memento_datetime") if final else None,
        "final_source_status": final.get("source_status") if final else None,
        "final_content_type": final.get("content_type") if final else None,
        "final_body_bytes": final.get("body_bytes") if final else 0,
        "final_body_sha256": final.get("body_sha256") if final else None,
        "unrequested_reason": (
            next((a.get("unrequested_reason") for a in attempts if not a.get("executed")), None)
            if not executed
            else redirect_skip
        ),
    }


def sanitized_entity(result: dict[str, Any]) -> dict[str, Any]:
    final = (result.get("hops") or [])[-1] if result.get("hops") else {}
    return {
        "candidate_rank": result.get("candidate_rank"),
        "target_id": result.get("target_id"),
        "original_url": result.get("original_url"),
        "category": result.get("category"),
        "source_status": result.get("final_source_status"),
        "actual_memento_or_null": result.get("actual_memento_or_null"),
        "content_type": result.get("final_content_type"),
        "body_bytes": result.get("final_body_bytes", 0),
        "body_sha256": result.get("final_body_sha256"),
        "raw_body_path": final.get("body_path"),
        "pillow": result.get("detail", {}).get("pillow"),
        "decoded_size": result.get("detail", {}).get("decoded_size"),
        "unrequested_reason": result.get("unrequested_reason"),
    }


def write_summaries(
    candidates: dict[str, Any],
    results: list[dict[str, Any]],
    state: RunState,
    started_utc: str,
    disk_before: int,
    disk_after: int,
    confirmed_transport: str,
    request_window_finished_utc: str | None = None,
    report_updated_utc: str | None = None,
) -> None:
    counts: dict[str, int] = {}
    for result in results:
        counts[result["category"]] = counts.get(result["category"], 0) + 1
    valid_images = [result for result in results if result["category"] == "valid_image"]
    mapping_suggestions = [
        {
            "target_id": result["target_id"],
            "original_url": result["original_url"],
            "actual_memento": result["actual_memento_or_null"],
            "raw_body_path": (result.get("hops") or [])[-1].get("body_path"),
            "body_sha256": result.get("final_body_sha256"),
            "action": "review source mapping before any integration; entity remains only in this raw directory",
        }
        for result in valid_images
    ]
    request_window_finished_utc = request_window_finished_utc or now_utc()
    report_updated_utc = report_updated_utc or now_utc()
    report = {
        "schema": "wayback-karazhan-batch1-20261015.v1",
        "started_utc": started_utc,
        "finished_utc": request_window_finished_utc,
        "request_window_finished_utc": request_window_finished_utc,
        "report_updated_utc": report_updated_utc,
        "inputs": {
            "batch_report": str(INPUT_REPORT.relative_to(ROOT)).replace("\\", "/"),
            "batch_report_sha256": sha256_file(INPUT_REPORT),
            "tls_doc": str(INPUT_DOC.relative_to(ROOT)).replace("\\", "/"),
            "tls_doc_sha256": sha256_file(INPUT_DOC),
            "candidates": "research/continuous-recovery-20261015/wayback-karazhan-batch1/candidates.json",
        },
        "policy": {
            "direct_first_only_for_first_target": True,
            "direct_connect_timeout_seconds": DIRECT_CONNECT_SECONDS,
            "direct_total_timeout_seconds": DIRECT_MAX_SECONDS,
            "proxy": "127.0.0.1:7890",
            "tls_verification": "enabled_by_curl_default",
            "interval_seconds_minimum": INTERVAL_SECONDS,
            "max_source_requests": MAX_SOURCE_REQUESTS,
            "window_seconds": WINDOW_SECONDS,
            "max_total_body_bytes": MAX_TOTAL_BODY,
            "max_entity_body_bytes": MAX_ENTITY_BODY,
            "max_wayback_redirect_hops": 1,
            "stop_http_codes": sorted(STOP_HTTP_CODES),
        },
        "preflight": {
            "drive": "D:",
            "free_bytes_before": disk_before,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "free_bytes_after": disk_after,
        },
        "transport": {
            "confirmed_transport_after_first_target": confirmed_transport,
            "proxy_endpoint": PROXY,
            "curl": str(CURL),
        },
        "target_count": len(results),
        "unique_target_count": len({result["target_id"] for result in results}),
        "category_counts": counts,
        "completed_count": sum(result["category"] != "not_requested" for result in results),
        "unrequested_count": sum(result["category"] == "not_requested" for result in results),
        "source_request_count": state.source_requests,
        "transport_attempt_count": state.transport_attempts,
        "failed_attempt_count": state.failed_attempts,
        "source_response_count": state.source_responses,
        "transport_unknown_count": sum(result["category"] == "transport_error" for result in results),
        "total_body_bytes": state.total_body_bytes,
        "consecutive_transport_failure_streak_at_stop": state.fail_streak,
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "rate_limit": state.rate_limit,
        "results": results,
        "source_mapping_suggestions": mapping_suggestions,
        "raw_evidence_note": "For transport attempts where curl created no output file, the offline augment step created a zero-byte local raw/*.body placeholder. These files are local evidence placeholders and are not source response bodies.",
    }
    write_json(OUT / "batch-report.json", report)

    summary = {
        "schema": "wayback-karazhan-batch1-sanitized-summary-20261015.v1",
        "started_utc": started_utc,
        "finished_utc": request_window_finished_utc,
        "request_window_finished_utc": request_window_finished_utc,
        "report_updated_utc": report_updated_utc,
        "input_sha256": {
            "batch_report_final_json": sha256_file(INPUT_REPORT),
            "karazhan_tls_recheck_md": sha256_file(INPUT_DOC),
        },
        "selected_count": len(candidates["selected"]),
        "target_count": len(results),
        "category_counts": counts,
        "confirmed_transport_after_first_target": confirmed_transport,
        "source_request_count": state.source_requests,
        "transport_attempt_count": state.transport_attempts,
        "failed_attempt_count": state.failed_attempts,
        "source_response_count": state.source_responses,
        "total_body_bytes": state.total_body_bytes,
        "disk_free_bytes_before": disk_before,
        "disk_free_bytes_after": disk_after,
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "rate_limit": state.rate_limit,
        "targets": [sanitized_entity(result) for result in results],
        "source_mapping_suggestions": mapping_suggestions,
        "raw_evidence_note": "Raw headers, traces, stderr, and bodies remain only under this batch's raw/ directory; no body was copied into the offline mirror. A zero-byte raw/*.body created for a transport attempt is a local placeholder, not a source response body.",
    }
    write_json(OUT / "sanitized-summary.json", summary)

    lines = [
        "# Karazhan Wayback TLS unknown recheck — batch 1",
        "",
        "This bounded serial recheck selected the first 30 distinct original URLs whose prior category was `transport_error` and whose prior source statuses were empty.",
        "",
        f"Input report SHA-256: `{sha256_file(INPUT_REPORT)}`; TLS diagnostic SHA-256: `{sha256_file(INPUT_DOC)}`.",
        f"Request window finished: `{request_window_finished_utc}`; report updated offline: `{report_updated_utc}`.",
        f"Transport after the first target: `{confirmed_transport}`; source requests: `{state.source_requests}`; transport attempts: `{state.transport_attempts}`; failed attempts: `{state.failed_attempts}`; source HTTP responses: `{state.source_responses}`; body bytes: `{state.total_body_bytes}`.",
        f"Categories: " + ", ".join(f"`{key}` {value}" for key, value in sorted(counts.items())) + ".",
        f"Disk free before/after: `{disk_before}` / `{disk_after}` bytes; stop reason: `{state.stop_reason or 'selected batch completed'}`.",
        "",
        "Actual Memento values below come only from response `Memento-Datetime` headers. The replay request hint is never used as an actual capture timestamp.",
        "",
        "| # | target | category | HTTP | actual Memento | bytes | decoded size | SHA-256 | unrequested reason |",
        "|---:|---|---|---:|---|---:|---|---|---|",
    ]
    for result in results:
        sha = result.get("final_body_sha256") or ""
        memento = result.get("actual_memento_or_null") or ""
        decoded_size = result.get("detail", {}).get("decoded_size")
        reason = result.get("unrequested_reason") or ""
        lines.append(
            f"| {result['candidate_rank']} | `{result['target_id']}` | `{result['category']}` | "
            f"{result.get('final_source_status') or ''} | `{memento}` | {result.get('final_body_bytes') or 0} | "
            f"`{decoded_size}` | `{sha}` | `{reason}` |"
        )
    lines.extend(
        [
            "",
            "Valid image bodies, if any, are retained under `raw/` with their headers, trace, and digest evidence. Source mapping suggestions are recorded for review; no entity was copied into production or the offline mirror.",
            "",
        ]
    )
    (OUT / "sanitized-summary.md").write_text("\n".join(lines), encoding="utf-8")


def run() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    disk_before = disk_free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D: free space {disk_before} is below required threshold {MIN_FREE_BYTES}")
    report = json.loads(INPUT_REPORT.read_text(encoding="utf-8"))
    candidates = make_candidates(report, disk_before)
    started_monotonic = time.monotonic()
    started_utc = now_utc()
    state = RunState(started_monotonic)
    results: list[dict[str, Any]] = []
    confirmed_transport = "unconfirmed"

    for index, candidate in enumerate(candidates["selected"]):
        attempts: list[dict[str, Any]] = []
        redirect_skip: str | None = None
        if not state.check_limits():
            results.append(result_record(candidate, [{"executed": False, "unrequested_reason": state.stop_reason}], state.stop_reason))
            continue

        if index == 0:
            direct = run_request(candidate["request_url"], "direct", candidate["old_target_id"], 1, state)
            attempts.append(direct)
            if not direct.get("executed"):
                confirmed_transport = "proxy_after_direct_not_requested"
            elif direct.get("source_status") in STOP_HTTP_CODES:
                confirmed_transport = "direct_rate_limited"
            elif direct.get("transport_error"):
                if state.stop_reason and state.stop_reason != "five_consecutive_tls_or_transport_failures":
                    confirmed_transport = "proxy_not_attempted_after_stop"
                else:
                    proxy = run_request(candidate["request_url"], "proxy", candidate["old_target_id"], 1, state)
                    attempts.append(proxy)
                    confirmed_transport = "proxy"
            else:
                confirmed_transport = "direct"
        else:
            transport = "proxy" if confirmed_transport.startswith("proxy") or confirmed_transport == "unconfirmed" else confirmed_transport
            attempts.append(run_request(candidate["request_url"], transport, candidate["old_target_id"], 1, state))

        while attempts and attempts[-1].get("executed") and not attempts[-1].get("transport_error"):
            final_attempt = attempts[-1]
            status = final_attempt.get("source_status")
            location = final_attempt.get("location")
            next_url = memento_follow_url(location, final_attempt.get("url") or candidate["request_url"])
            if status not in REDIRECT_CODES or not next_url:
                if status in REDIRECT_CODES and location and not next_url:
                    redirect_skip = "redirect_not_a_legal_wayback_replay"
                break
            if len([a for a in attempts if a.get("executed")]) >= 2:
                redirect_skip = "redirect_hop_limit"
                break
            if not state.check_limits():
                redirect_skip = state.stop_reason or "source_limit_before_redirect"
                break
            attempts.append(run_request(next_url, final_attempt.get("transport") or "proxy", candidate["old_target_id"], 2, state))
            if not attempts[-1].get("executed"):
                redirect_skip = attempts[-1].get("unrequested_reason")
                break

        results.append(result_record(candidate, attempts, redirect_skip))
        if state.stop_reason:
            # All remaining candidates receive explicit not_requested records.
            continue

    for result in results:
        del result  # preserve loop variable only for clarity
    by_id = {result["target_id"]: result for result in results}
    for candidate in candidates["selected"]:
        if candidate["old_target_id"] not in by_id:
            results.append(result_record(candidate, [{"executed": False, "unrequested_reason": state.stop_reason or "not_scheduled"}], state.stop_reason or "not_scheduled"))
    results.sort(key=lambda value: value["candidate_rank"])
    disk_after = disk_free_bytes()
    write_summaries(candidates, results, state, started_utc, disk_before, disk_after, confirmed_transport)
    print(
        json.dumps(
            {
                "target_count": len(results),
                "category_counts": {category: sum(item["category"] == category for item in results) for category in sorted({item["category"] for item in results})},
                "source_requests": state.source_requests,
                "source_responses": state.source_responses,
                "total_body_bytes": state.total_body_bytes,
                "stop_reason": state.stop_reason,
                "confirmed_transport": confirmed_transport,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except Exception as exc:
        print(f"wayback_recheck_batch1: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

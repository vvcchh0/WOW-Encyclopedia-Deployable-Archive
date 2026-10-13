#!/usr/bin/env python3
"""Serial proxy recovery for the Round002 TLS failures.

This runner deliberately handles only the finite failed set from Round002.  It
uses one curl.exe request at a time through the already approved local proxy,
with no curl retry and an explicit three-identical-failure stop rule.  The
successful Round003 transport probe is copied into the new source map without
issuing another request.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
import zlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research" / "resource-resume-20261013"
ROUND2 = BASE / "round002"
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(ROUND2) not in sys.path:
    sys.path.insert(0, str(ROUND2))

import wayback_backup as wb  # noqa: E402
from run_round002_impl import (  # noqa: E402
    _magic,
    _pillow,
    choose_entity,
    cdx_digest,
    parse_cdx,
    query_url,
)

PROBE = BASE / "round003-transport-probe"
OUT = BASE / "round003"

PLAN = BASE / "round002-plan.json"
PROXY = "http://127.0.0.1:7890"
MAX_REQUESTS = 80
MAX_CDX_BYTES = 4 * 1024 * 1024
MAX_ENTITY_BYTES = 16 * 1024 * 1024
BODY_BUDGET = 128 * 1024 * 1024
MAX_WORKSPACE = 14_000_000_000
MIN_FREE = 11_000_000_000
RESERVE = 256 * 1024 * 1024
REQUEST_TIMEOUT = 60
CONNECT_TIMEOUT = 15
DEADLINE = 1200
INTERVAL = 1.0
EXPECTED_TLS_ERROR = "network_error:[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)"
TIMESTAMP_RE = re.compile(r"^\d{14}$")


def now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    partial.write_bytes(data)
    os.replace(partial, path)


def atomic_json(path: Path, value: Any) -> None:
    atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return default


def safe_name(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def headers_from_file(path: Path) -> tuple[dict[str, str], int | None, int]:
    """Return only the final response block; raw headers stay in the file."""

    try:
        lines = path.read_text(encoding="iso-8859-1", errors="replace").splitlines()
    except OSError:
        return {}, None, 0
    blocks: list[tuple[dict[str, str], int | None]] = []
    current: dict[str, str] | None = None
    status: int | None = None
    for line in lines:
        if line.startswith("HTTP/"):
            if current is not None:
                blocks.append((current, status))
            current = {}
            status = None
            parts = line.split()
            if len(parts) > 1 and parts[1].isdigit():
                status = int(parts[1])
            continue
        if current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip()
    if current is not None:
        blocks.append((current, status))
    if not blocks:
        return {}, None, 0
    final, status = blocks[-1]
    return final, status, len(blocks)


def decode_payload(data: bytes, encoding: str | None) -> tuple[bytes | None, str | None]:
    if not encoding or encoding.casefold().strip() in {"", "identity"}:
        return data, None
    lower = encoding.casefold()
    try:
        if "gzip" in lower:
            return gzip.decompress(data), None
        if "deflate" in lower:
            try:
                return zlib.decompress(data), None
            except zlib.error:
                return zlib.decompress(data, -15), None
        if "br" in lower:
            try:
                import brotli  # type: ignore
            except Exception as exc:  # pragma: no cover - depends on runtime
                return None, f"brotli_unavailable:{exc}"
            return brotli.decompress(data), None
    except Exception as exc:
        return None, f"content_decode_error:{type(exc).__name__}:{exc}"
    return None, f"unsupported_content_encoding:{encoding}"


def parse_writeout(data: bytes) -> dict[str, Any]:
    text = data.decode("utf-8", errors="replace").strip()
    parts = text.split("\t")
    status: int | None = None
    if parts and parts[0].isdigit():
        try:
            status = int(parts[0])
        except ValueError:
            status = None
    size: int | None = None
    if len(parts) > 3 and parts[3].isdigit():
        size = int(parts[3])
    return {
        "http_status": status,
        "final_url": parts[1] if len(parts) > 1 else None,
        "content_type_reported": parts[2] if len(parts) > 2 else None,
        "size_download_reported": size,
        "time_total": parts[4] if len(parts) > 4 else None,
        "writeout_text_present": bool(text),
    }


def guard_for_run() -> wb.BudgetGuard:
    return wb.BudgetGuard(ROOT, MAX_WORKSPACE, MIN_FREE, RESERVE)


def load_failed_cdx() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((ROUND2 / "cdx" / "meta").glob("*.json")):
        value = load_json(path)
        if not isinstance(value, dict):
            continue
        error = value.get("error") or {}
        if value.get("status") == "transport_or_http_error" and str(error.get("error")) == EXPECTED_TLS_ERROR:
            value["previous_metadata"] = rel(path)
            records.append(value)
    return sorted(records, key=lambda item: int(item.get("rank", 0)))


def load_failed_entity() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((ROUND2 / "entity" / "meta").glob("*.json")):
        value = load_json(path)
        if not isinstance(value, dict):
            continue
        error = value.get("error") or {}
        if value.get("status") == "transport_or_http_error" and str(error.get("error")) == EXPECTED_TLS_ERROR:
            value["previous_metadata"] = rel(path)
            records.append(value)
    return sorted(records, key=lambda item: int(item.get("rank", 0)))


def load_round2_entity_plan() -> dict[str, dict[str, Any]]:
    value = load_json(ROUND2 / "entity-plan.json", {})
    items = value.get("items", []) if isinstance(value, dict) else []
    return {str(item.get("logical_url")): dict(item) for item in items if isinstance(item, dict) and item.get("logical_url")}


def probe_validation() -> dict[str, Any]:
    value = load_json(PROBE / "probe-validation.json")
    if not isinstance(value, dict) or not value.get("validation", {}).get("strict_probe_checks_passed"):
        raise SystemExit("round003 transport probe is missing or not strictly accepted")
    return value


def copy_probe(probe: dict[str, Any], guard: wb.BudgetGuard) -> dict[str, Any]:
    body_source = ROOT / str(probe["local_capture"]["body_path"])
    headers_source = ROOT / str(probe["local_capture"]["headers_path"])
    body = body_source.read_bytes()
    guard.check(extra_bytes=len(body) + 2 * 1024 * 1024)
    digest = str(probe["validation"]["body_sha256"])
    raw_path = OUT / "entity" / "raw" / f"reused-rank002-{digest[:20]}.bin"
    headers_path = OUT / "entity" / "headers" / "reused-rank002.txt"
    atomic_bytes(raw_path, body)
    atomic_bytes(headers_path, headers_source.read_bytes())
    item = {
        "schema_version": 2,
        "kind": "resource_resume_round003_entity",
        "rank": 2,
        "logical_url": probe["request"]["logical_url"],
        "original": probe["request"]["original"] if "original" in probe["request"] else probe["request"]["logical_url"],
        "selected_timestamp": probe["request"]["selected_timestamp"],
        "expected_cdx_digest": probe["request"]["expected_cdx_digest"],
        "temporal_class": "baseline_2008",
        "requested_at": None,
        "finished_at": now(),
        "status": "accepted",
        "network_attempts": 0,
        "reused_probe": True,
        "probe_source": rel(PROBE / "probe-validation.json"),
        "http_status": 200,
        "final_url": probe["curl"]["final_url"],
        "memento_datetime": probe["validation"]["memento_datetime"],
        "actual_timestamp": probe["validation"]["actual_timestamp"],
        "body_length": len(body),
        "wire_length": len(body),
        "decoded_length": len(body),
        "body_sha256": digest,
        "observed_cdx_digest": probe["validation"]["observed_cdx_sha1_base32"],
        "cdx_digest_match": True,
        "mime": probe["validation"]["mime"],
        "mime_ok": True,
        "magic": probe["validation"]["magic"],
        "pillow": {"available": True, "valid": True, "format": probe["validation"]["pillow_format"], "size": probe["validation"]["pillow_size"]},
        "content_length_match": True,
        "actual_timestamp_match": True,
        "raw_path": rel(raw_path),
        "headers_path": rel(headers_path),
        "metadata_path": rel(OUT / "entity" / "meta" / "002-reused-probe.json"),
    }
    atomic_json(OUT / "entity" / "meta" / "002-reused-probe.json", item)
    return item


class Runner:
    def __init__(self, max_requests: int, deadline_seconds: int, interval_seconds: float, proxy: str) -> None:
        self.guard = guard_for_run()
        self.max_requests = max_requests
        self.deadline_seconds = deadline_seconds
        self.deadline = time.monotonic() + max(1, deadline_seconds)
        self.interval_seconds = max(0.0, interval_seconds)
        self.proxy = proxy
        self.last_request: float | None = None
        self.requests = 0
        self.response_bytes = 0
        self.failure_signature: str | None = None
        self.failure_streak = 0
        self.stop = False
        self.stop_reason: str | None = None
        self.records_cdx: list[dict[str, Any]] = []
        self.records_entity: list[dict[str, Any]] = []
        self.accepted: list[dict[str, Any]] = []

    def emit(self, event: str, record: dict[str, Any]) -> None:
        safe = {
            "event": event,
            "request_number": self.requests,
            "kind": record.get("kind"),
            "rank": record.get("rank"),
            "logical_url": record.get("logical_url"),
            "status": record.get("status"),
            "http_status": record.get("http_status"),
            "wire_length": record.get("wire_length"),
            "decoded_length": record.get("decoded_length"),
            "complete": record.get("complete"),
            "accepted": record.get("status") == "accepted",
            "failure_signature": record.get("failure_signature"),
            "failure_streak": self.failure_streak,
            "stop": self.stop,
        }
        print(json.dumps(safe, ensure_ascii=False), flush=True)

    def update_failure_stop(self, record: dict[str, Any]) -> None:
        status = str(record.get("status", ""))
        success = status in {"complete", "accepted"}
        if success:
            self.failure_signature = None
            self.failure_streak = 0
            return
        signature = str(record.get("failure_signature") or status)
        if signature == self.failure_signature:
            self.failure_streak += 1
        else:
            self.failure_signature = signature
            self.failure_streak = 1
        if self.failure_streak >= 3:
            self.stop = True
            self.stop_reason = "three_consecutive_same_failure"

    def wait_interval(self) -> None:
        if self.last_request is not None:
            remaining = self.interval_seconds - (time.monotonic() - self.last_request)
            if remaining > 0:
                time.sleep(remaining)
        self.last_request = time.monotonic()

    def pre_request(self, cap: int) -> str | None:
        if self.stop:
            return self.stop_reason or "stopped"
        if self.requests >= self.max_requests:
            self.stop = True
            self.stop_reason = "max_requests"
            return self.stop_reason
        if time.monotonic() >= self.deadline:
            self.stop = True
            self.stop_reason = "deadline_before_request"
            return self.stop_reason
        if self.response_bytes + cap > BODY_BUDGET:
            self.stop = True
            self.stop_reason = "response_body_budget"
            return self.stop_reason
        try:
            self.guard.check(extra_bytes=cap + 2 * 1024 * 1024)
        except wb.BudgetExceeded as exc:
            self.stop = True
            self.stop_reason = f"budget:{exc}"
            return self.stop_reason
        self.wait_interval()
        self.requests += 1
        return None

    def request_once(self, kind: str, item: dict[str, Any], rank: int) -> dict[str, Any]:
        logical = str(item.get("logical_url") or item.get("original") or "")
        original = str(item.get("original") or logical)
        if kind == "cdx":
            request_url = query_url(logical)
            cap = MAX_CDX_BYTES
            base = OUT / "cdx"
            expected_timestamp = None
            expected_digest = None
        else:
            selected_timestamp = str(item.get("timestamp") or item.get("selected_timestamp") or "")
            request_url = wb.build_archive_url(selected_timestamp, original)
            cap = MAX_ENTITY_BYTES
            base = OUT / "entity"
            expected_timestamp = selected_timestamp
            expected_digest = str(item.get("cdx_digest") or item.get("expected_cdx_digest") or "").upper()
        name = f"{int(rank):03d}-{safe_name(logical)}"
        wire_path = base / "wire" / f"{name}.bin"
        headers_path = base / "headers" / f"{name}.txt"
        stderr_path = base / "headers" / f"{name}.stderr.txt"
        raw_suffix = ".json" if kind == "cdx" else ".bin"
        raw_path = base / "raw" / f"{name}{raw_suffix}"
        meta_path = base / "meta" / f"{name}.json"
        record: dict[str, Any] = {
            "schema_version": 1,
            "kind": f"resource_resume_round003_{kind}",
            "rank": rank,
            "logical_url": logical,
            "original": original,
            "request_url": request_url,
            "selected_timestamp": expected_timestamp,
            "expected_cdx_digest": expected_digest,
            "requested_at": now(),
            "status": "not_started",
            "network_attempts": 0,
            "wire_path": rel(wire_path),
            "headers_path": rel(headers_path),
            "stderr_path": rel(stderr_path),
            "previous_metadata": item.get("previous_metadata"),
            "transport": {"tool": "curl.exe", "proxy": self.proxy, "http_version": "1.1", "retry": 0, "connect_timeout_seconds": CONNECT_TIMEOUT, "max_time_seconds": REQUEST_TIMEOUT, "ssl_verification": True},
        }
        reason = self.pre_request(cap)
        if reason:
            record.update({"status": "not_attempted_stop", "failure_signature": reason, "stop_reason": reason})
            record["finished_at"] = now()
            atomic_json(meta_path, record)
            return record
        command = [
            "curl.exe",
            "--proxy",
            self.proxy,
            "--http1.1",
            "--retry",
            "0",
            "--connect-timeout",
            str(CONNECT_TIMEOUT),
            "--max-time",
            str(REQUEST_TIMEOUT),
            "--max-filesize",
            str(cap),
            "--location",
            "--silent",
            "--show-error",
            "--dump-header",
            str(headers_path.resolve()),
            "--output",
            str(wire_path.resolve()),
            "--write-out",
            "%{http_code}\t%{url_effective}\t%{content_type}\t%{size_download}\t%{time_total}",
            request_url,
        ]
        record["command_contract"] = {"proxy": self.proxy, "http_version": "1.1", "retry": 0, "connect_timeout": CONNECT_TIMEOUT, "max_time": REQUEST_TIMEOUT, "max_filesize": cap}
        record["network_attempts"] = 1
        try:
            completed = subprocess.run(command, capture_output=True, timeout=REQUEST_TIMEOUT + 5, check=False)
            stdout = completed.stdout or b""
            stderr = completed.stderr or b""
            atomic_bytes(stderr_path, stderr)
            writeout = parse_writeout(stdout)
            record.update(writeout)
            record["curl_exit_code"] = int(completed.returncode)
            record["curl_stderr_bytes"] = len(stderr)
        except subprocess.TimeoutExpired as exc:
            atomic_bytes(stderr_path, (exc.stderr or b"") if isinstance(exc.stderr, bytes) else str(exc.stderr or "").encode())
            record.update({"status": "process_timeout", "failure_signature": "process_timeout", "curl_exit_code": None, "error": "curl subprocess exceeded bounded process timeout"})
            record["finished_at"] = now()
            atomic_json(meta_path, record)
            return record
        except Exception as exc:
            record.update({"status": "curl_process_error", "failure_signature": "curl_process_error", "error": f"{type(exc).__name__}:{exc}", "traceback": traceback.format_exc()})
            record["finished_at"] = now()
            atomic_json(meta_path, record)
            return record

        wire = wire_path.read_bytes() if wire_path.is_file() else b""
        record["wire_length"] = len(wire)
        record["wire_sha256"] = sha_bytes(wire)
        headers, header_status, status_line_count = headers_from_file(headers_path)
        record["response_headers"] = headers
        record["header_status"] = header_status
        record["status_line_count"] = status_line_count
        if record.get("http_status") is None:
            record["http_status"] = header_status
        if record.get("final_url") is None:
            record["final_url"] = request_url
        if len(wire) >= cap and (record.get("curl_exit_code") == 63 or len(wire) > cap):
            record.update({"status": "object_exceeds_max_bytes", "truncated": True, "failure_signature": "object_exceeds_max_bytes", "error": f"wire response reached object cap {cap}"})
            record["finished_at"] = now()
            self.response_bytes += len(wire)
            atomic_json(meta_path, record)
            return record
        if int(record.get("curl_exit_code") or 0) != 0:
            exit_code = record.get("curl_exit_code")
            record.update({"status": "transport_or_http_error", "failure_signature": f"curl_exit_{exit_code}", "error_type": "curl_exit", "error": f"curl_exit_{exit_code}"})
            record["finished_at"] = now()
            self.response_bytes += len(wire)
            atomic_json(meta_path, record)
            return record
        http_status = record.get("http_status")
        if http_status != 200:
            record.update({"status": "transport_or_http_error", "failure_signature": f"http_{http_status}", "error_type": "http_status", "error": f"HTTP status {http_status}"})
            record["finished_at"] = now()
            self.response_bytes += len(wire)
            atomic_json(meta_path, record)
            return record
        encoding = wb._header_value(headers, "Content-Encoding")
        decoded, decode_error = decode_payload(wire, encoding)
        record["content_encoding"] = encoding
        record["decoded_length"] = len(decoded) if decoded is not None else None
        record["decoded_sha256"] = sha_bytes(decoded) if decoded is not None else None
        record["content_encoding_decode_error"] = decode_error
        if decode_error or decoded is None:
            record.update({"status": "decode_error", "failure_signature": "decode_error", "error": decode_error})
            record["finished_at"] = now()
            self.response_bytes += len(wire)
            atomic_json(meta_path, record)
            return record
        if len(decoded) > cap:
            record.update({"status": "object_exceeds_max_bytes", "truncated": True, "failure_signature": "object_exceeds_max_bytes", "error": f"decoded response exceeded object cap {cap}"})
            record["finished_at"] = now()
            self.response_bytes += len(decoded)
            atomic_json(meta_path, record)
            return record
        self.response_bytes += len(decoded)
        record["response_body_budget_bytes"] = BODY_BUDGET
        if self.response_bytes > BODY_BUDGET:
            record.update({"status": "response_body_budget", "failure_signature": "response_body_budget", "error": "decoded response body budget exceeded"})
            record["finished_at"] = now()
            atomic_json(meta_path, record)
            self.stop = True
            self.stop_reason = "response_body_budget"
            return record
        atomic_bytes(raw_path, decoded)
        record["raw_path"] = rel(raw_path)
        record["body_sha256"] = sha_bytes(decoded)
        if kind == "cdx":
            rows, complete, parse_error = parse_cdx(decoded)
            record.update({"row_count": len(rows), "candidate_rows": rows, "complete": complete, "parse_error": parse_error})
            if not complete:
                record.update({"status": "parse_error", "failure_signature": "parse_error", "error": parse_error})
            else:
                record.update({"status": "complete", "failure_signature": None})
        else:
            mime = wb._header_value(headers, "Content-Type") or ""
            actual = wb._actual_timestamp(headers, record.get("final_url"))
            expected_length = wb._header_value(headers, "Content-Length")
            content_scope = "wire" if encoding and encoding.casefold().strip() not in {"", "identity"} else "decoded"
            compare_length = len(wire) if content_scope == "wire" else len(decoded)
            length_ok = True
            if expected_length:
                try:
                    length_ok = int(expected_length) == compare_length
                except ValueError:
                    length_ok = False
            observed_digest = cdx_digest(decoded)
            magic = _magic(decoded)
            pillow = _pillow(decoded)
            digest_ok = observed_digest == expected_digest
            mime_ok = mime.casefold().split(";", 1)[0].startswith("image/")
            actual_ok = actual == expected_timestamp
            valid = bool(digest_ok and mime_ok and magic is not None and pillow.get("valid") and actual and actual_ok and length_ok)
            reasons = []
            if not digest_ok:
                reasons.append("cdx_digest")
            if not mime_ok:
                reasons.append("mime")
            if magic is None:
                reasons.append("magic")
            if not pillow.get("valid"):
                reasons.append("pillow")
            if not actual_ok:
                reasons.append("memento_timestamp")
            if not length_ok:
                reasons.append("content_length")
            record.update({"status": "accepted" if valid else "validation_failed", "failure_signature": None if valid else "validation_failed", "mime": mime, "mime_ok": mime_ok, "actual_timestamp": actual, "actual_timestamp_match": actual_ok, "memento_datetime": wb._header_value(headers, "Memento-Datetime"), "expected_content_length": expected_length, "content_length_scope": content_scope, "content_length_match": length_ok, "observed_cdx_digest": observed_digest, "cdx_digest_match": digest_ok, "magic": magic, "pillow": pillow, "validation_failure_reasons": reasons})
            if valid:
                self.accepted.append(record)
        record["finished_at"] = now()
        record["metadata_path"] = rel(meta_path)
        atomic_json(meta_path, record)
        return record

    def process(self, kind: str, item: dict[str, Any], rank: int) -> dict[str, Any]:
        record = self.request_once(kind, item, rank)
        self.update_failure_stop(record)
        if kind == "cdx":
            self.records_cdx.append(record)
        else:
            self.records_entity.append(record)
        self.emit(kind, record)
        return record


def accepted_source_map(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        if record.get("status") != "accepted":
            continue
        key = (str(record.get("logical_url")), str(record.get("actual_timestamp") or record.get("selected_timestamp")))
        unique.setdefault(key, {
            "logical_url": record.get("logical_url"),
            "original": record.get("original"),
            "local_path": record.get("raw_path"),
            "mime": record.get("mime"),
            "kind": "image",
            "role": "finite_image_entity",
            "sha256": record.get("body_sha256"),
            "actual_timestamp": record.get("actual_timestamp"),
            "indexed_capture_timestamp": record.get("selected_timestamp"),
            "cdx_digest": record.get("expected_cdx_digest"),
            "temporal_class": record.get("temporal_class", "baseline_2008"),
            "source_metadata": record.get("metadata_path"),
            "reused_probe": bool(record.get("reused_probe")),
        })
    return sorted(unique.values(), key=lambda value: (str(value.get("logical_url")), str(value.get("actual_timestamp"))))


def build_zip() -> dict[str, Any] | None:
    sources = []
    for path in sorted(OUT.rglob("*")):
        if not path.is_file():
            continue
        if path.name.endswith(".partial") or path.name.startswith("evidence") and path.suffix == ".zip":
            continue
        if path.name == "evidence-verification.json":
            continue
        sources.append(path)
    if not sources:
        return None
    guard = guard_for_run()
    total = sum(path.stat().st_size for path in sources)
    guard.check(extra_bytes=total + 4 * 1024 * 1024)
    zip_path = OUT / "evidence.zip"
    if zip_path.exists():
        index = 2
        while (OUT / f"evidence-{index:03d}.zip").exists():
            index += 1
        zip_path = OUT / f"evidence-{index:03d}.zip"
    partial = zip_path.with_name(zip_path.name + ".partial")
    members: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(partial, "w", allowZip64=True) as archive:
            for source in sources:
                arcname = source.relative_to(OUT).as_posix()
                stored = "/raw/" in f"/{arcname}" or "/wire/" in f"/{arcname}"
                archive.write(source, arcname=arcname, compress_type=zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)
        os.replace(partial, zip_path)
        with zipfile.ZipFile(zip_path, "r") as archive:
            bad = archive.testzip()
            if bad is not None:
                raise wb.RecoveryError(f"evidence ZIP CRC failure: {bad}")
            for info in archive.infolist():
                source = OUT / Path(info.filename)
                digest = hashlib.sha256()
                with archive.open(info, "r") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                if not source.is_file() or source.stat().st_size != info.file_size or sha_file(source) != digest.hexdigest():
                    raise wb.RecoveryError(f"evidence ZIP source mismatch: {info.filename}")
                members.append({"member": info.filename, "source": rel(source), "size": info.file_size, "crc32": f"{info.CRC:08x}", "sha256": digest.hexdigest(), "compression": info.compress_type})
        result = {"schema_version": 1, "kind": "resource_resume_round003_evidence_zip_verification", "generated_utc": now(), "zip_path": rel(zip_path), "zip_sha256": sha_file(zip_path), "zip_bytes": zip_path.stat().st_size, "member_count": len(members), "source_bytes": total, "crc_verified": True, "sha256_verified": True, "members": members}
        atomic_json(OUT / "evidence-verification.json", result)
        return result
    finally:
        if partial.exists():
            partial.unlink()


def counts(records: list[dict[str, Any]]) -> dict[str, int]:
    status_values = [str(item.get("status")) for item in records]
    return {
        "planned": len(records),
        "attempted": sum(int(item.get("network_attempts", 0) or 0) for item in records),
        "complete": sum(item.get("status") == "complete" for item in records),
        "complete_empty": sum(item.get("status") == "complete" and int(item.get("row_count", 0) or 0) == 0 for item in records),
        "accepted": sum(item.get("status") == "accepted" for item in records),
        "validation_failed": sum(item.get("status") == "validation_failed" for item in records),
        "transport_or_http_error": sum(item.get("status") == "transport_or_http_error" for item in records),
        "parse_error": sum(item.get("status") == "parse_error" for item in records),
        "not_attempted": sum(status_values.count(value) for value in {"not_attempted_stop", "not_attempted_max_requests"}),
    }


def histogram(records: list[dict[str, Any]]) -> dict[str, Any]:
    error_types: dict[str, int] = {}
    http_statuses: dict[str, int] = {}
    failures: dict[str, int] = {}
    for record in records:
        status = str(record.get("status"))
        http = str(record.get("http_status")) if record.get("http_status") is not None else "null"
        http_statuses[http] = http_statuses.get(http, 0) + 1
        if status not in {"complete", "accepted"}:
            signature = str(record.get("failure_signature") or status)
            failures[signature] = failures.get(signature, 0) + 1
            error_type = str(record.get("error_type") or status)
            error_types[error_type] = error_types.get(error_type, 0) + 1
    return {"http_status_histogram": http_statuses, "failure_signature_histogram": failures, "error_type_histogram": error_types}


def make_sanitized_summary(runner: Runner, entity_plan: dict[str, Any] | None, evidence: dict[str, Any] | None, reused_probe: bool) -> tuple[dict[str, Any], str]:
    cdx_records = runner.records_cdx
    entity_records = runner.records_entity
    accepted = accepted_source_map(([runner._probe_record] if hasattr(runner, "_probe_record") else []) + entity_records)
    summary = {
        "schema_version": 1,
        "kind": "resource_resume_round003_sanitized_summary",
        "generated_utc": now(),
        "scope": {"source_round": rel(ROUND2), "proxy": runner.proxy, "workers": 1, "max_requests": runner.max_requests, "deadline_seconds": runner.deadline_seconds, "interval_seconds": runner.interval_seconds, "request_timeout_seconds": REQUEST_TIMEOUT, "connect_timeout_seconds": CONNECT_TIMEOUT, "retry": 0, "ssl_verification": True, "raw_headers_or_body_included": False},
        "cdx": {"counts": counts(cdx_records), **histogram(cdx_records), "candidate_entity_count": len((entity_plan or {}).get("items", [])), "reused_complete_cdx": 20},
        "entity": {"counts": counts(entity_records), **histogram(entity_records), "reused_probe_without_get": reused_probe, "round2_accepted_skipped": 1},
        "accepted_resources": accepted,
        "request_total": runner.requests,
        "decoded_response_bytes": runner.response_bytes,
        "stop_reason": runner.stop_reason or "planned_recovery_completed",
        "same_failure_stop_rule": {"implemented_in_round003": True, "stopped_after_three_same_failure": runner.stop_reason == "three_consecutive_same_failure", "failure_streak_at_stop": runner.failure_streak},
        "evidence": {"zip_path": evidence.get("zip_path"), "zip_bytes": evidence.get("zip_bytes"), "member_count": evidence.get("member_count"), "crc_verified": evidence.get("crc_verified"), "sha256_verified": evidence.get("sha256_verified")} if evidence else None,
        "local_only": {"raw_capture_directory": rel(OUT), "no_round2_files_overwritten": True},
    }
    md = "\n".join([
        "# Round003 serial transport recovery",
        "",
        "This summary contains no raw response headers, Cookie values, or response-body content. Raw captures remain local under `round003`. The run used one serial curl request at a time through `http://127.0.0.1:7890`, HTTP/1.1, retry 0, 15s connect timeout, 60s request timeout, and TLS verification.",
        "",
        f"CDX counts: {json.dumps(counts(cdx_records), ensure_ascii=False, sort_keys=True)}.",
        f"Entity counts: {json.dumps(counts(entity_records), ensure_ascii=False, sort_keys=True)}.",
        f"Total curl requests: `{runner.requests}`; decoded response bytes: `{runner.response_bytes}`; stop reason: `{runner.stop_reason or 'planned_recovery_completed'}`.",
        "",
        "The round stops before starting another item after three consecutive failures with the same failure signature. Existing complete CDX records and the Round002 accepted border-bot entity were skipped; the successful rank-2 proxy probe was copied locally and reused without another GET.",
        "",
        "Accepted resources are listed in `sanitized-summary.json`; raw headers and bodies are stored only inside the round003 directory and are excluded from this report.",
        "",
    ])
    return summary, md


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    parser.add_argument("--deadline-seconds", type=int, default=DEADLINE)
    parser.add_argument("--interval-seconds", type=float, default=INTERVAL)
    parser.add_argument("--proxy", default=PROXY)
    args = parser.parse_args()
    if args.max_requests < 1 or args.max_requests > MAX_REQUESTS:
        raise SystemExit(f"--max-requests must be 1..{MAX_REQUESTS}")
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ("cdx/raw", "cdx/wire", "cdx/headers", "cdx/meta", "entity/raw", "entity/wire", "entity/headers", "entity/meta"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    failed_cdx = load_failed_cdx()
    failed_entity = load_failed_entity()
    if len(failed_cdx) != 30:
        raise SystemExit(f"expected 30 Round002 TLS-failed CDX records, found {len(failed_cdx)}")
    if len(failed_entity) != 18:
        raise SystemExit(f"expected 18 Round002 TLS-failed entity records, found {len(failed_entity)}")
    probe = probe_validation()
    probe_url = str(probe["request"]["logical_url"])
    failed_entity_network = [item for item in failed_entity if str(item.get("logical_url")) != probe_url]
    state = {
        "schema_version": 1,
        "kind": "resource_resume_round003_state",
        "generated_utc": now(),
        "source_plan": rel(PLAN),
        "source_round": rel(ROUND2),
        "failed_cdx_inputs": len(failed_cdx),
        "failed_entity_inputs": len(failed_entity),
        "failed_entity_network_items": len(failed_entity_network),
        "reused_probe": probe_url,
        "skipped_round2_complete_cdx": 20,
        "skipped_round2_accepted_entity": 1,
        "constraints": {"workers": 1, "max_requests": args.max_requests, "deadline_seconds": args.deadline_seconds, "interval_seconds": args.interval_seconds, "request_timeout_seconds": REQUEST_TIMEOUT, "connect_timeout_seconds": CONNECT_TIMEOUT, "retry": 0, "max_cdx_bytes": MAX_CDX_BYTES, "max_entity_bytes": MAX_ENTITY_BYTES, "response_body_budget_bytes": BODY_BUDGET, "workspace_max_bytes": MAX_WORKSPACE, "disk_free_reserve_bytes": MIN_FREE, "reserve_bytes": RESERVE, "proxy": args.proxy, "ssl_verification": True},
        "phase": "cdx",
        "requests": 0,
        "response_bytes": 0,
        "failure_streak": 0,
        "stop": False,
    }
    atomic_json(OUT / "round003-state.json", state)
    atomic_json(OUT / "cdx-request-plan.json", {"schema_version": 1, "kind": "resource_resume_round003_cdx_request_plan", "generated_utc": now(), "items": [{"rank": int(item["rank"]), "logical_url": item["logical_url"], "query_url": query_url(str(item["logical_url"])), "previous_metadata": item.get("previous_metadata")} for item in failed_cdx]})
    runner = Runner(args.max_requests, args.deadline_seconds, args.interval_seconds, args.proxy)
    existing_cdx = {str(value.get("logical_url")): value for path in sorted((OUT / "cdx" / "meta").glob("*.json")) if isinstance((value := load_json(path)), dict) and value.get("logical_url")}
    for item in failed_cdx:
        if runner.stop:
            break
        if str(item.get("logical_url")) in existing_cdx:
            record = dict(existing_cdx[str(item["logical_url"])])
            runner.records_cdx.append(record)
            if record.get("status") == "complete":
                runner.failure_signature = None
                runner.failure_streak = 0
            continue
        runner.process("cdx", item, int(item["rank"]))
    cdx_summary = {"schema_version": 1, "kind": "resource_resume_round003_cdx_summary", "generated_utc": now(), "source_round": rel(ROUND2), "records": runner.records_cdx, "counts": counts(runner.records_cdx), "response_body_bytes": runner.response_bytes, "stop_reason": runner.stop_reason or "planned_cdx_completed"}
    atomic_json(OUT / "cdx-summary.json", cdx_summary)
    if runner.stop:
        entity_plan = {"schema_version": 1, "kind": "resource_resume_round003_entity_plan", "generated_utc": now(), "items": [], "stop_reason": runner.stop_reason}
        atomic_json(OUT / "entity-plan.json", entity_plan)
    else:
        round2_items = load_round2_entity_plan()
        selections: list[dict[str, Any]] = []
        for record in sorted(runner.records_cdx, key=lambda value: int(value.get("rank", 0))):
            if record.get("status") != "complete" or not isinstance(record.get("candidate_rows"), list):
                continue
            selected = choose_entity(record["candidate_rows"], str(record.get("logical_url")), str(record.get("metadata_path", "")), str(record.get("raw_path", "")))
            if selected:
                selected["source_cdx_rank"] = record.get("rank")
                selections.append(selected)
        reused_item = dict(round2_items.get(probe_url, {}))
        reused_item.update({"reused_probe": True, "probe_source": rel(PROBE / "probe-validation.json"), "temporal_class": "baseline_2008"})
        entity_items: list[dict[str, Any]] = [reused_item]
        old_urls = {str(item.get("logical_url")) for item in failed_entity_network}
        for item in failed_entity_network:
            source = dict(round2_items.get(str(item.get("logical_url")), {}))
            source.update({"logical_url": item.get("logical_url"), "original": item.get("original"), "timestamp": item.get("selected_timestamp"), "cdx_digest": item.get("expected_cdx_digest"), "cdx_mime": item.get("mime"), "cdx_length": None, "temporal_class": item.get("temporal_class", "baseline_2008"), "previous_metadata": item.get("previous_metadata")})
            entity_items.append(source)
        seen_urls = {str(item.get("logical_url")) for item in entity_items}
        for selected in selections:
            logical = str(selected.get("logical_url"))
            if logical in seen_urls:
                continue
            seen_urls.add(logical)
            entity_items.append(selected)
        entity_plan = {"schema_version": 1, "kind": "resource_resume_round003_entity_plan", "generated_utc": now(), "source_round": rel(ROUND2), "anchor_timestamp": "20080512210044", "items": entity_items, "reused_probe_count": 1, "network_items": len(entity_items) - 1, "new_cdx_selection_count": len([item for item in entity_items if item.get("source_cdx_rank") is not None]), "selection_counts": {"baseline_2008": sum(item.get("temporal_class") == "baseline_2008" for item in entity_items), "late_2008": sum(item.get("temporal_class") == "late_2008" for item in entity_items)}}
        atomic_json(OUT / "entity-plan.json", entity_plan)
        runner._probe_record = copy_probe(probe, runner.guard)
        runner.accepted.append(runner._probe_record)
        existing_entity = {str(value.get("logical_url")): value for path in sorted((OUT / "entity" / "meta").glob("*.json")) if isinstance((value := load_json(path)), dict) and value.get("logical_url")}
        for index, item in enumerate(entity_items[1:], 1):
            if runner.stop:
                break
            logical = str(item.get("logical_url"))
            if logical in existing_entity:
                record = dict(existing_entity[logical])
                runner.records_entity.append(record)
                if record.get("status") == "accepted":
                    runner.accepted.append(record)
                else:
                    runner.update_failure_stop(record)
                continue
            record = runner.process("entity", item, index + 2)
            record["temporal_class"] = item.get("temporal_class", "baseline_2008")
            record["source_metadata"] = item.get("source_metadata")
            record["source_raw"] = item.get("source_raw")
            atomic_json(OUT / "entity" / "meta" / f"{index + 3:03d}-{safe_name(logical)}.json", record)
        entity_summary = {"schema_version": 1, "kind": "resource_resume_round003_entity_summary", "generated_utc": now(), "source_round": rel(ROUND2), "records": runner.records_entity + [runner._probe_record], "counts": counts(runner.records_entity + [runner._probe_record]), "response_body_bytes": runner.response_bytes, "stop_reason": runner.stop_reason or "planned_entity_recovery_completed"}
        atomic_json(OUT / "entity-summary.json", entity_summary)
    accepted = accepted_source_map(([runner._probe_record] if hasattr(runner, "_probe_record") else []) + runner.records_entity)
    atomic_json(OUT / "entity-source-map.json", {"schema_version": 1, "kind": "resource_resume_round003_entity_source_map", "generated_utc": now(), "source_round": rel(ROUND2), "unique_accepted_count": len(accepted), "items": accepted})
    state.update({"phase": "complete", "requests": runner.requests, "response_bytes": runner.response_bytes, "failure_streak": runner.failure_streak, "stop": runner.stop, "stop_reason": runner.stop_reason, "finished_utc": now(), "cdx_counts": counts(runner.records_cdx), "entity_counts": counts(runner.records_entity + ([runner._probe_record] if hasattr(runner, "_probe_record") else []))})
    atomic_json(OUT / "round003-state.json", state)
    evidence = build_zip()
    summary, markdown = make_sanitized_summary(runner, load_json(OUT / "entity-plan.json", {}), evidence, hasattr(runner, "_probe_record"))
    atomic_json(OUT / "sanitized-summary.json", summary)
    atomic_bytes(OUT / "sanitized-summary.md", markdown.encode("utf-8"))
    if evidence is not None:
        state["evidence"] = {"path": evidence.get("zip_path"), "verification": rel(OUT / "evidence-verification.json")}
        atomic_json(OUT / "round003-state.json", state)
    print(json.dumps({"phase": "round003", "requests": runner.requests, "cdx": counts(runner.records_cdx), "entity": counts(runner.records_entity + ([runner._probe_record] if hasattr(runner, "_probe_record") else [])), "unique_accepted": len(accepted), "stop_reason": runner.stop_reason or "planned_recovery_completed", "evidence": evidence.get("zip_path") if evidence else None}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

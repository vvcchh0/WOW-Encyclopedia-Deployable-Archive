#!/usr/bin/env python3
"""Implementation for the bounded Round002 CDX/entity phases.

The public wrapper remains dry-run by default.  Network phases require the
parent's explicit release token and use the reviewed pooled Archive transport
with one attempt per item, raw evidence retention, and shared byte/disk
guards.  This module is intentionally local to the Round002 ownership area.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import hashlib
import io
import json
import os
import re
import sys
import threading
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import wayback_backup as wb  # noqa: E402
import wayback_pooled_transport as pooled  # noqa: E402

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore

BASE = ROOT / "research" / "resource-resume-20261013"
PLAN = BASE / "round002-plan.json"
OUT = BASE / "round002"
FROM = "20080101000000"
TO = "20081231235959"
ANCHOR = "20080512210044"
MAX_ITEMS = 50
MAX_WORKERS = 4
MAX_CDX_BYTES = 4 * 1024 * 1024
MAX_ENTITY_BYTES = 16 * 1024 * 1024
BODY_BUDGET = 128 * 1024 * 1024
DEADLINE = 1200
REQUEST_TIMEOUT = 60
MAX_WORKSPACE = 14_000_000_000
MIN_FREE = 11_000_000_000
RESERVE = 256 * 1024 * 1024
TIMESTAMP_RE = re.compile(r"^\d{14}$")
CDX_DIGEST_RE = re.compile(r"^[A-Z2-7]{32}$")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cdx_digest(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".partial")
    part.write_bytes(data)
    os.replace(part, path)


def atomic_json(path: Path, value: object) -> None:
    atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def query_url(logical_url: str) -> str:
    return "https://web.archive.org/cdx/search/cdx?" + urlencode({
        "url": logical_url,
        "from": FROM,
        "to": TO,
        "matchType": "exact",
        "output": "json",
    })


def _status(row: dict[str, object]) -> str:
    for key in ("status", "statuscode", "status_code", "http_status"):
        if row.get(key) is not None:
            return str(row[key])
    return ""


def _mime(row: dict[str, object]) -> str:
    for key in ("mime", "mimetype", "mime_type", "content_type"):
        if row.get(key) is not None:
            return str(row[key])
    return ""


def _timestamp(row: dict[str, object]) -> str:
    return str(row.get("timestamp", row.get("capture_timestamp", "")))


def _original(row: dict[str, object]) -> str:
    for key in ("original", "url", "original_url"):
        if row.get(key) is not None:
            return str(row[key])
    return ""


def _normalise_row(row: object, headers: list[str] | None) -> dict[str, object]:
    if isinstance(row, dict):
        return {str(k): v for k, v in row.items()}
    if not isinstance(row, list):
        raise ValueError("CDX row is neither object nor array")
    names = headers or ["timestamp", "original", "statuscode", "digest", "length", "mimetype"]
    return {names[i] if i < len(names) else f"column_{i}": value for i, value in enumerate(row)}


def parse_cdx(data: bytes) -> tuple[list[dict[str, object]], bool, str | None]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [], False, f"json_parse_error:{exc}"
    if not isinstance(value, list):
        return [], False, "json_root_not_array"
    if not value:
        return [], True, None
    headers: list[str] | None = None
    if isinstance(value[0], list) and any(str(x).casefold() in {"timestamp", "original", "statuscode", "mimetype", "digest"} for x in value[0]):
        headers = [str(x) for x in value[0]]
        value = value[1:]
    try:
        rows = [_normalise_row(row, headers) for row in value]
    except ValueError as exc:
        return [], False, f"row_parse_error:{exc}"
    return rows, True, None


class SharedBudget:
    """Reserve aggregate decoded response bytes across worker streams."""

    def __init__(self, limit: int, initial: int = 0) -> None:
        self.limit = int(limit)
        self.used = int(initial)
        self.reserved = 0
        self.lock = threading.Lock()

    def reserve(self, amount: int) -> int:
        with self.lock:
            if self.used + self.reserved + amount > self.limit:
                raise wb.BudgetExceeded(f"response body budget exceeded ({self.used}+{self.reserved}+{amount}>{self.limit})")
            self.reserved += amount
        return amount

    def note(self, amount: int) -> None:
        with self.lock:
            if amount > self.reserved:
                raise wb.BudgetExceeded("decoded response exceeded reservation")
            self.reserved -= amount
            self.used += amount

    def finish(self, reservation: int, observed: int) -> None:
        with self.lock:
            self.reserved = max(0, self.reserved - max(0, reservation - observed))


def make_guard() -> wb.BudgetGuard:
    return wb.BudgetGuard(ROOT, MAX_WORKSPACE, MIN_FREE, RESERVE)


def _safe(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def _headers(result: object) -> dict[str, str]:
    return wb._headers_dict(getattr(result, "headers", None))


def _error(exc: BaseException) -> dict[str, object]:
    out: dict[str, object] = {"error_type": type(exc).__name__, "error": str(exc)}
    for key in ("reason", "status", "final_url", "headers", "body_preview", "exception_traceback"):
        value = getattr(exc, key, None)
        if value is not None:
            out[key] = value
    return out


def _guard_write(guard: wb.BudgetGuard, size: int) -> None:
    guard.check(extra_bytes=max(0, size) + 64 * 1024)


def choose_entity(rows: list[dict[str, object]], logical_url: str, source_meta: str, source_raw: str) -> dict[str, object] | None:
    candidates: list[dict[str, object]] = []
    for row in rows:
        timestamp = _timestamp(row)
        original = _original(row)
        mime = _mime(row)
        digest = str(row.get("digest", "")).upper()
        if _status(row) != "200" or not mime.casefold().split(";", 1)[0].startswith("image/"):
            continue
        if not TIMESTAMP_RE.fullmatch(timestamp) or not original or not CDX_DIGEST_RE.fullmatch(digest):
            continue
        candidates.append({
            "logical_url": logical_url,
            "original": original,
            "timestamp": timestamp,
            "status": _status(row),
            "cdx_mime": mime,
            "cdx_digest": digest,
            "cdx_length": row.get("length"),
            "raw_row": row,
            "source_metadata": source_meta,
            "source_raw": source_raw,
        })
    if not candidates:
        return None
    before = [x for x in candidates if str(x["timestamp"]) <= ANCHOR]
    if before:
        result = max(before, key=lambda x: str(x["timestamp"]))
        temporal = "baseline_2008"
    else:
        result = min(candidates, key=lambda x: str(x["timestamp"]))
        temporal = "late_2008"
    result = dict(result)
    result.update({
        "role": "finite_image_entity",
        "temporal_class": temporal,
        "baseline_eligible": temporal == "baseline_2008",
        "selected_reason": "latest_status200_image_not_after_anchor" if temporal == "baseline_2008" else "earliest_status200_image_after_anchor",
    })
    return result


def _plan_items(path: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("items"), list):
        raise SystemExit("plan must contain an items array")
    items = [x for x in value["items"] if isinstance(x, dict)]
    if len(items) != len(value["items"]) or len(items) > MAX_ITEMS:
        raise SystemExit(f"plan must contain at most {MAX_ITEMS} object items")
    urls = [str(x.get("logical_url", "")) for x in items]
    if len(set(urls)) != len(urls):
        raise SystemExit("Round002 plan has duplicate logical URLs")
    return value, items


def _existing_cdx(out: Path) -> dict[str, dict[str, object]]:
    directory = out / "cdx" / "meta"
    found: dict[str, dict[str, object]] = {}
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and isinstance(value.get("logical_url"), str):
            value.setdefault("metadata_path", rel(path))
            found[value["logical_url"]] = value
    return found


def _cdx_one(item: dict[str, object], rank: int, out: Path, deadline: float, shared: SharedBudget, guard: wb.BudgetGuard, stop: threading.Event) -> dict[str, object]:
    logical = str(item["logical_url"])
    requested = query_url(logical)
    record: dict[str, object] = {
        "schema_version": 2,
        "kind": "resource_resume_round002_cdx_query",
        "rank": rank,
        "logical_url": logical,
        "query_url": requested,
        "query_window": {"from": FROM, "to": TO},
        "query_contract": {"matchType": "exact", "output": "json", "status_filter": None, "mime_filter": None, "collapse": None, "showNumPages": None},
        "requested_at": now(),
        "status": "not_started",
        "complete": False,
        "truncated": False,
        "network_attempts": 0,
    }
    reservation: int | None = None
    observed = 0
    try:
        if stop.is_set():
            record["status"] = "skipped_global_stop"
        elif time.monotonic() >= deadline:
            stop.set()
            record["status"] = "deadline_before_request"
        else:
            guard.check(extra_bytes=MAX_CDX_BYTES + 64 * 1024)
            reservation = shared.reserve(MAX_CDX_BYTES)
            record["network_attempts"] = 1
            with pooled.PooledArchiveTransport(fallback_to_urllib=False) as transport:
                def progress(delta: int) -> None:
                    nonlocal observed
                    shared.note(delta)
                    observed += delta
                result = transport.fetch_once(requested, MAX_CDX_BYTES, progress, timeout=REQUEST_TIMEOUT, deadline=deadline)
            body = result.body
            record.update({"status": "http_200", "http_status": result.status, "final_url": result.final_url, "response_headers": _headers(result), "body_length": len(body), "body_sha256": sha_bytes(body), "body_bytes_observed": observed})
            if len(body) > MAX_CDX_BYTES:
                record.update({"status": "truncated", "truncated": True})
            else:
                raw_path = out / "cdx" / "raw" / f"{rank:03d}-{_safe(logical)}.json"
                _guard_write(guard, len(body))
                atomic_bytes(raw_path, body)
                rows, complete, parse_error = parse_cdx(body)
                record.update({"raw_path": rel(raw_path), "candidate_rows": rows, "row_count": len(rows), "complete": complete})
                if parse_error:
                    record.update({"status": "parse_error", "parse_error": parse_error})
                else:
                    record["status"] = "complete"
    except wb.BudgetExceeded as exc:
        stop.set()
        record.update({"status": "budget_exceeded", "error": _error(exc), "body_bytes_observed": observed})
    except wb.DeadlineExceeded as exc:
        stop.set()
        record.update({"status": "deadline", "error": _error(exc), "body_bytes_observed": observed})
    except wb.FetchError as exc:
        if time.monotonic() >= deadline:
            stop.set()
        record.update({"status": "transport_or_http_error", "error": _error(exc), "body_bytes_observed": observed})
        if exc.status is not None:
            record["http_status"] = exc.status
        if exc.final_url:
            record["final_url"] = exc.final_url
        if exc.headers:
            record["response_headers"] = dict(exc.headers)
        if str(getattr(exc, "reason", "")).startswith("object_exceeds_max_bytes"):
            record["truncated"] = True
    except Exception as exc:
        stop.set()
        record.update({"status": "unexpected_error", "error": _error(exc), "traceback": traceback.format_exc(), "body_bytes_observed": observed})
    finally:
        if reservation is not None:
            shared.finish(reservation, observed)
    record["finished_at"] = now()
    meta_path = out / "cdx" / "meta" / f"{rank:03d}-{_safe(logical)}.json"
    try:
        _guard_write(guard, len(json.dumps(record, ensure_ascii=False).encode("utf-8")))
        record["metadata_path"] = rel(meta_path)
        atomic_json(meta_path, record)
    except (OSError, wb.BudgetExceeded) as exc:
        record["metadata_write_error"] = _error(exc)
    return record


def run_cdx(plan_path: Path, out: Path, items: list[dict[str, object]], workers: int, max_requests: int, deadline_seconds: int) -> int:
    workers = max(1, min(MAX_WORKERS, workers))
    existing = _existing_cdx(out)
    records: list[dict[str, object]] = []
    pending: list[tuple[int, dict[str, object]]] = []
    for rank, item in enumerate(items, 1):
        logical = str(item["logical_url"])
        if logical in existing:
            prior = dict(existing[logical])
            prior["resume_action"] = "reused_existing_record_no_retry"
            records.append(prior)
        elif len(pending) < max_requests:
            pending.append((rank, item))
        else:
            records.append({"rank": rank, "logical_url": logical, "status": "not_attempted_max_requests", "complete": False, "truncated": False, "network_attempts": 0})
    out.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + max(1, deadline_seconds)
    shared = SharedBudget(BODY_BUDGET)
    guard = make_guard()
    stop = threading.Event()
    if pending:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers, thread_name_prefix="round002-cdx") as pool:
            futures = [pool.submit(_cdx_one, item, rank, out, deadline, shared, guard, stop) for rank, item in pending]
            records.extend(future.result() for future in futures)
    records.sort(key=lambda x: int(x.get("rank", 0)))
    selections: list[dict[str, object]] = []
    for record in records:
        rows = record.get("candidate_rows")
        if record.get("complete") and isinstance(rows, list):
            chosen = choose_entity(rows, str(record.get("logical_url", "")), str(record.get("metadata_path", "")), str(record.get("raw_path", "")))
            if chosen:
                selections.append(chosen)
    entity_plan = {
        "schema_version": 1,
        "kind": "resource_resume_round002_entity_plan",
        "generated_utc": now(),
        "anchor_timestamp": ANCHOR,
        "source_plan": rel(plan_path),
        "source_plan_sha256": sha(plan_path),
        "query_window": {"from": FROM, "to": TO},
        "items": selections,
        "selection_counts": {"baseline_2008": sum(x.get("temporal_class") == "baseline_2008" for x in selections), "late_2008": sum(x.get("temporal_class") == "late_2008" for x in selections)},
        "network_performed": any(int(x.get("network_attempts", 0)) > 0 for x in records),
    }
    compact_records = []
    for record in records:
        compact = dict(record)
        # The raw response is the lossless all-status evidence.  Keeping every
        # parsed row again in the aggregate summary could multiply a near-4 MiB
        # response into an unnecessarily large metadata file; per-query meta
        # retains candidate_rows for selection/audit.
        compact.pop("candidate_rows", None)
        if record.get("complete"):
            compact["all_rows_retained_in_raw"] = True
        compact_records.append(compact)
    summary = {
        "schema_version": 2,
        "kind": "resource_resume_round002_cdx_summary",
        "generated_utc": now(),
        "source_plan": rel(plan_path),
        "source_plan_sha256": sha(plan_path),
        "query_window": {"from": FROM, "to": TO},
        "records": compact_records,
        "counts": {
            "planned": len(items),
            "attempted": sum(int(x.get("network_attempts", 0)) for x in records),
            "complete": sum(bool(x.get("complete")) for x in records),
            "complete_empty": sum(bool(x.get("complete")) and int(x.get("row_count", 0)) == 0 for x in records),
            "complete_with_rows": sum(bool(x.get("complete")) and int(x.get("row_count", 0)) > 0 for x in records),
            "errors": sum(x.get("status") in {"budget_exceeded", "deadline", "transport_or_http_error", "unexpected_error", "parse_error"} for x in records),
            "not_attempted": sum(str(x.get("status", "")).startswith("not_attempted") for x in records),
        },
        "response_body_bytes": shared.used,
        "response_body_budget_bytes": BODY_BUDGET,
        "entity_plan_path": rel(out / "entity-plan.json"),
        "stop_reason": "global_stop_or_deadline" if stop.is_set() else "planned_requests_completed",
    }
    summary_bytes = (json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    entity_bytes = (json.dumps(entity_plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    cdx_state = {"schema_version": 2, "kind": "resource_resume_round002_cdx_state", "phase": "cdx", "network_performed": any(int(x.get("network_attempts", 0)) > 0 for x in records), "source_plan": rel(plan_path), "source_plan_sha256": sha(plan_path), "generated_utc": now(), "workers": workers, "max_requests": max_requests, "deadline_seconds": deadline_seconds, "summary_path": rel(out / "cdx-summary.json"), "entity_plan_path": rel(out / "entity-plan.json")}
    _guard_write(guard, len(summary_bytes) + len(entity_bytes) + 64 * 1024)
    atomic_bytes(out / "cdx-summary.json", summary_bytes)
    atomic_bytes(out / "entity-plan.json", entity_bytes)
    atomic_json(out / "cdx-state.json", cdx_state)
    print(json.dumps({"phase": "cdx", "attempted": summary["counts"]["attempted"], "complete": summary["counts"]["complete"], "entity_plan": len(selections), "network": True}, ensure_ascii=False))
    return 0


def _magic(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9"):
        return "jpeg"
    if data.startswith(b"BM"):
        return "bmp"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "webp"
    return None


def _pillow(data: bytes) -> dict[str, object]:
    if Image is None:
        return {"available": False, "valid": False, "error": "Pillow unavailable"}
    try:
        with Image.open(io.BytesIO(data)) as image:
            fmt = image.format
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            size = list(image.size)
        return {"available": True, "valid": True, "format": fmt, "size": size}
    except Exception as exc:
        return {"available": True, "valid": False, "error": f"{type(exc).__name__}:{exc}"}


def build_evidence_zip(out: Path, guard: wb.BudgetGuard) -> dict[str, object] | None:
    """Package this run's raw CDX/meta/entity evidence without re-encoding.

    The ZIP is intentionally produced only after an entity phase has run. JSON
    metadata is deflated; original entity bytes are stored. Verification reads
    every member back, checks ZIP CRC/size, and independently compares its
    SHA-256 to the source file. The verification JSON remains outside the ZIP
    so it cannot create a self-referential checksum.
    """
    roots = [out / "cdx" / "raw", out / "cdx" / "meta", out / "entity" / "raw", out / "entity" / "meta"]
    extra_names = ("cdx-request-plan.json", "cdx-summary.json", "cdx-state.json", "entity-plan.json", "entity-summary.json", "entity-source-map.json", "entity-state.json")
    sources: list[Path] = []
    for directory in roots:
        if directory.is_dir():
            sources.extend(sorted(x for x in directory.glob("*.json") if x.is_file()))
            if directory.name == "raw":
                sources.extend(sorted(x for x in directory.glob("*.bin") if x.is_file()))
    sources.extend(out / name for name in extra_names if (out / name).is_file())
    sources = sorted({path.resolve() for path in sources})
    if not any("/entity/raw/" in path.as_posix().casefold() or "\\entity\\raw\\" in str(path).casefold() for path in sources):
        return None
    total = sum(path.stat().st_size for path in sources)
    guard.check(extra_bytes=total + 4 * 1024 * 1024)
    zip_path = out / "evidence.zip"
    if zip_path.exists():
        index = 2
        while (out / f"evidence-{index:03d}.zip").exists():
            index += 1
        zip_path = out / f"evidence-{index:03d}.zip"
    partial = zip_path.with_name(zip_path.name + ".partial")
    members: list[dict[str, object]] = []
    try:
        with zipfile.ZipFile(partial, "w", allowZip64=True) as archive:
            for source in sources:
                arcname = source.relative_to(out).as_posix()
                compression = zipfile.ZIP_STORED if "/entity/raw/" in f"/{arcname}" or arcname.startswith("entity/raw/") else zipfile.ZIP_DEFLATED
                archive.write(source, arcname=arcname, compress_type=compression)
        guard.check(extra_bytes=partial.stat().st_size + 512 * 1024)
        os.replace(partial, zip_path)
        with zipfile.ZipFile(zip_path, "r") as archive:
            bad = archive.testzip()
            if bad is not None:
                raise wb.RecoveryError(f"evidence ZIP CRC failure: {bad}")
            for info in archive.infolist():
                digest = hashlib.sha256()
                with archive.open(info, "r") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                source = out / Path(info.filename)
                if not source.is_file() or source.stat().st_size != info.file_size or sha(source) != digest.hexdigest():
                    raise wb.RecoveryError(f"evidence ZIP source mismatch: {info.filename}")
                members.append({"member": info.filename, "source": rel(source), "size": info.file_size, "crc32": f"{info.CRC:08x}", "sha256": digest.hexdigest(), "compression": info.compress_type})
        verification = {"schema_version": 1, "kind": "resource_resume_round002_evidence_zip_verification", "generated_utc": now(), "zip_path": rel(zip_path), "zip_sha256": sha(zip_path), "zip_bytes": zip_path.stat().st_size, "member_count": len(members), "source_bytes": total, "crc_verified": True, "sha256_verified": True, "members": members}
        guard.check(extra_bytes=len(json.dumps(verification, ensure_ascii=False).encode("utf-8")) + 64 * 1024)
        atomic_json(out / "evidence-verification.json", verification)
        return verification
    finally:
        if partial.exists():
            partial.unlink()


def _entity_one(item: dict[str, object], rank: int, out: Path, deadline: float, shared: SharedBudget, guard: wb.BudgetGuard, stop: threading.Event) -> dict[str, object]:
    original = str(item.get("original", ""))
    timestamp = str(item.get("timestamp", ""))
    expected = str(item.get("cdx_digest", "")).upper()
    replay = wb.build_archive_url(timestamp, original)
    record: dict[str, object] = {"schema_version": 2, "kind": "resource_resume_round002_entity", "rank": rank, "logical_url": item.get("logical_url"), "original": original, "selected_timestamp": timestamp, "replay_url": replay, "expected_cdx_digest": expected, "temporal_class": item.get("temporal_class"), "requested_at": now(), "status": "not_started", "network_attempts": 0, "truncated": False}
    reservation: int | None = None
    observed = 0
    try:
        if stop.is_set():
            record["status"] = "skipped_global_stop"
        elif time.monotonic() >= deadline:
            stop.set()
            record["status"] = "deadline_before_request"
        else:
            guard.check(extra_bytes=MAX_ENTITY_BYTES + 128 * 1024)
            reservation = shared.reserve(MAX_ENTITY_BYTES)
            record["network_attempts"] = 1
            with pooled.PooledArchiveTransport(fallback_to_urllib=False) as transport:
                def progress(delta: int) -> None:
                    nonlocal observed
                    shared.note(delta)
                    observed += delta
                # Do not pass expected digest; a mismatch body is evidence and must be retained.
                result = transport.fetch_once(replay, MAX_ENTITY_BYTES, progress, timeout=REQUEST_TIMEOUT, deadline=deadline)
            body = result.body
            headers = _headers(result)
            mime = wb._header_value(headers, "Content-Type") or ""
            actual = wb._actual_timestamp(headers, result.final_url)
            observed_digest = cdx_digest(body)
            magic = _magic(body)
            pillow = _pillow(body)
            length_header = wb._header_value(headers, "Content-Length")
            length_ok = True
            if length_header:
                try:
                    length_ok = int(length_header) == len(body)
                except ValueError:
                    length_ok = False
            digest_ok = observed_digest == expected
            mime_ok = mime.casefold().split(";", 1)[0].startswith("image/")
            actual_ok = actual == timestamp
            valid = bool(result.status == 200 and digest_ok and mime_ok and magic is not None and pillow.get("valid") and actual and actual_ok and length_ok)
            raw_path = out / "entity" / "raw" / f"{rank:03d}-{sha_bytes(body)[:20]}.bin"
            _guard_write(guard, len(body))
            atomic_bytes(raw_path, body)
            record.update({"status": "accepted" if valid else "validation_failed", "http_status": result.status, "final_url": result.final_url, "response_headers": headers, "memento_datetime": wb._header_value(headers, "Memento-Datetime"), "actual_timestamp": actual, "body_length": len(body), "body_bytes_observed": observed, "body_sha256": sha_bytes(body), "observed_cdx_digest": observed_digest, "cdx_digest_match": digest_ok, "mime": mime, "mime_ok": mime_ok, "magic": magic, "pillow": pillow, "content_length_match": length_ok, "actual_timestamp_match": actual_ok, "raw_path": rel(raw_path)})
    except wb.BudgetExceeded as exc:
        stop.set()
        record.update({"status": "budget_exceeded", "error": _error(exc), "body_bytes_observed": observed})
    except wb.DeadlineExceeded as exc:
        stop.set()
        record.update({"status": "deadline", "error": _error(exc), "body_bytes_observed": observed})
    except wb.FetchError as exc:
        if time.monotonic() >= deadline:
            stop.set()
        record.update({"status": "transport_or_http_error", "error": _error(exc), "body_bytes_observed": observed})
        if exc.status is not None:
            record["http_status"] = exc.status
        if exc.final_url:
            record["final_url"] = exc.final_url
        if exc.headers:
            record["response_headers"] = dict(exc.headers)
    except Exception as exc:
        stop.set()
        record.update({"status": "unexpected_error", "error": _error(exc), "traceback": traceback.format_exc(), "body_bytes_observed": observed})
    finally:
        if reservation is not None:
            shared.finish(reservation, observed)
    record["finished_at"] = now()
    meta = out / "entity" / "meta" / f"{rank:03d}-{_safe(original)}.json"
    try:
        _guard_write(guard, len(json.dumps(record, ensure_ascii=False).encode("utf-8")))
        record["metadata_path"] = rel(meta)
        atomic_json(meta, record)
    except (OSError, wb.BudgetExceeded) as exc:
        record["metadata_write_error"] = _error(exc)
    return record


def run_entity(plan_path: Path, out: Path, entity_path: Path, workers: int, max_requests: int, deadline_seconds: int) -> int:
    value = json.loads(entity_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("items"), list):
        raise SystemExit("entity plan must contain an items array")
    items = [x for x in value["items"] if isinstance(x, dict)]
    if len(items) != len(value["items"]) or len(items) > MAX_ITEMS:
        raise SystemExit("invalid entity plan item set")
    items = items[:max_requests]
    out.mkdir(parents=True, exist_ok=True)
    guard = make_guard()
    entity_state = {"schema_version": 1, "kind": "resource_resume_round002_entity_state", "phase": "entity", "generated_utc": now(), "network_performed": False, "source_plan": rel(plan_path), "source_entity_plan": rel(entity_path), "max_requests": max_requests, "workers": workers, "deadline_seconds": deadline_seconds}
    _guard_write(guard, len(json.dumps(entity_state, ensure_ascii=False).encode("utf-8")))
    atomic_json(out / "entity-state.json", entity_state)
    existing: dict[str, dict[str, object]] = {}
    directory = out / "entity" / "meta"
    if directory.is_dir():
        for path in directory.glob("*.json"):
            try:
                prior = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if isinstance(prior, dict) and isinstance(prior.get("logical_url"), str):
                existing[prior["logical_url"]] = prior
    pending = [x for x in items if str(x.get("logical_url", "")) not in existing]
    initial = 0
    try:
        summary = json.loads((out / "cdx-summary.json").read_text(encoding="utf-8"))
        if isinstance(summary, dict):
            initial = int(summary.get("response_body_bytes", 0) or 0)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        pass
    shared = SharedBudget(BODY_BUDGET, initial)
    stop = threading.Event()
    deadline = time.monotonic() + max(1, deadline_seconds)
    records = list(existing.values())
    if pending:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(MAX_WORKERS, workers)), thread_name_prefix="round002-entity") as pool:
            futures = [pool.submit(_entity_one, item, index + 1, out, deadline, shared, guard, stop) for index, item in enumerate(pending)]
            records.extend(future.result() for future in futures)
    records.sort(key=lambda x: int(x.get("rank", 0)))
    accepted = [x for x in records if x.get("status") == "accepted"]
    source_map = {"schema_version": 1, "kind": "resource_resume_round002_entity_source_map", "generated_utc": now(), "source_entity_plan": rel(entity_path), "items": [{"logical_url": x.get("logical_url"), "original": x.get("original"), "local_path": x.get("raw_path"), "mime": x.get("mime"), "kind": "image", "role": "finite_image_entity", "sha256": x.get("body_sha256"), "actual_timestamp": x.get("actual_timestamp"), "indexed_capture_timestamp": x.get("selected_timestamp"), "cdx_digest": x.get("expected_cdx_digest"), "temporal_class": x.get("temporal_class"), "source_metadata": x.get("metadata_path")} for x in accepted]}
    final = {"schema_version": 2, "kind": "resource_resume_round002_entity_summary", "generated_utc": now(), "source_plan": rel(plan_path), "source_entity_plan": rel(entity_path), "network_performed": any(int(x.get("network_attempts", 0)) > 0 for x in records), "records": records, "counts": {"planned": len(items), "attempted": sum(int(x.get("network_attempts", 0)) for x in records), "accepted": len(accepted), "validation_failed": sum(x.get("status") == "validation_failed" for x in records), "transport_or_http_error": sum(x.get("status") == "transport_or_http_error" for x in records), "not_attempted": sum(str(x.get("status", "")).startswith("not_attempted") for x in records)}, "response_body_bytes": shared.used, "response_body_budget_bytes": BODY_BUDGET, "stop_reason": "global_stop_or_deadline" if stop.is_set() else "planned_entities_completed"}
    final_bytes = (json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    source_bytes = (json.dumps(source_map, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _guard_write(guard, len(final_bytes) + len(source_bytes) + 64 * 1024)
    atomic_bytes(out / "entity-summary.json", final_bytes)
    atomic_bytes(out / "entity-source-map.json", source_bytes)
    entity_state.update({"network_performed": bool(final.get("network_performed")), "finished_utc": now(), "summary_path": rel(out / "entity-summary.json"), "source_map_path": rel(out / "entity-source-map.json")})
    _guard_write(guard, len(json.dumps(entity_state, ensure_ascii=False).encode("utf-8")))
    atomic_json(out / "entity-state.json", entity_state)
    evidence = build_evidence_zip(out, guard) if accepted else None
    if evidence is not None:
        final["evidence_zip"] = evidence["zip_path"]
        final["evidence_verification"] = rel(out / "evidence-verification.json")
        entity_state["evidence_zip"] = evidence["zip_path"]
        entity_state["evidence_verification"] = rel(out / "evidence-verification.json")
        _guard_write(guard, len(json.dumps(final, ensure_ascii=False).encode("utf-8")) + len(json.dumps(entity_state, ensure_ascii=False).encode("utf-8")))
        atomic_json(out / "entity-summary.json", final)
        atomic_json(out / "entity-state.json", entity_state)
    print(json.dumps({"phase": "entity", "attempted": final["counts"]["attempted"], "accepted": len(accepted), "network": True}, ensure_ascii=False))
    return 0


def self_test() -> int:
    data = json.dumps([["timestamp", "original", "statuscode", "digest", "length", "mimetype"], ["20080501000000", "http://www.worldofwarcraft.com/a.gif", "404", "X", "1", "text/html"], ["20080401000000", "http://www.worldofwarcraft.com/a.gif", "200", "A" * 32, "4", "image/gif"], ["20080601000000", "http://www.worldofwarcraft.com/a.gif", "200", "B" * 32, "4", "image/gif"]]).encode()
    rows, complete, error = parse_cdx(data)
    assert complete and error is None and len(rows) == 3
    chosen = choose_entity(rows, "http://www.worldofwarcraft.com/a.gif", "meta", "raw")
    assert chosen and chosen["timestamp"] == "20080401000000" and chosen["temporal_class"] == "baseline_2008"
    late = choose_entity([rows[-1]], "http://www.worldofwarcraft.com/a.gif", "meta", "raw")
    assert late and late["temporal_class"] == "late_2008"
    assert parse_cdx(b"[]")[1] is True and parse_cdx(b"bad")[1] is False
    print(json.dumps({"self_test": "pass", "rows": len(rows), "baseline": chosen["timestamp"], "late": late["timestamp"]}, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phase", choices=("preflight", "cdx-plan", "cdx", "entity"), default="preflight")
    ap.add_argument("--plan", type=Path, default=PLAN)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--entity-plan", type=Path)
    ap.add_argument("--allow-network", action="store_true")
    ap.add_argument("--parent-release-token")
    ap.add_argument("--workers", type=int, default=MAX_WORKERS)
    ap.add_argument("--max-requests", type=int, default=MAX_ITEMS)
    ap.add_argument("--deadline-seconds", type=int, default=DEADLINE)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    plan_path = args.plan if args.plan.is_absolute() else ROOT / args.plan
    out = args.out if args.out.is_absolute() else ROOT / args.out
    _, items = _plan_items(plan_path)
    if args.workers < 1 or args.workers > MAX_WORKERS:
        raise SystemExit(f"--workers must be 1..{MAX_WORKERS}")
    out.mkdir(parents=True, exist_ok=True)
    state = {"schema_version": 2, "kind": "resource_resume_round002_state", "generated_utc": now(), "network_performed": False, "plan": rel(plan_path), "plan_sha256": sha(plan_path), "items": len(items), "constraints": {"archive_streams_max": MAX_WORKERS, "entity_max_bytes": MAX_ENTITY_BYTES, "cdx_max_bytes": MAX_CDX_BYTES, "response_body_budget_bytes": BODY_BUDGET, "per_request_timeout_seconds": REQUEST_TIMEOUT, "deadline_seconds": DEADLINE, "workspace_max_bytes": MAX_WORKSPACE, "disk_free_reserve_bytes": MIN_FREE, "reserve_bytes": RESERVE, "retries": 0}, "phase": args.phase, "allow_network": bool(args.allow_network)}
    if args.phase == "preflight":
        state.update({"status": "preflight_only", "note": "No network operation; wait for parent Pages/network release."})
        atomic_json(out / "preflight.json", state)
        print(json.dumps({"phase": args.phase, "items": len(items), "network": False}, ensure_ascii=False))
        return 0
    if args.phase == "cdx-plan":
        state.update({"status": "cdx_plan_ready", "planned_queries": len(items), "requests": [{"rank": rank, "logical_url": str(item["logical_url"]), "query_url": query_url(str(item["logical_url"])), "query_window": {"from": FROM, "to": TO}, "query_contract": {"matchType": "exact", "output": "json", "status_filter": None, "mime_filter": None, "collapse": None, "showNumPages": None}, "network_performed": False} for rank, item in enumerate(items, 1)]})
        atomic_json(out / "cdx-request-plan.json", state)
        print(json.dumps({"phase": args.phase, "planned_queries": len(items), "network": False}, ensure_ascii=False))
        return 0
    if not args.allow_network or not args.parent_release_token:
        raise SystemExit(f"{args.phase} phase requires explicit --allow-network and --parent-release-token")
    if args.max_requests < 1 or args.max_requests > MAX_ITEMS:
        raise SystemExit(f"--max-requests must be 1..{MAX_ITEMS}")
    if args.phase == "cdx":
        return run_cdx(plan_path, out, items, args.workers, args.max_requests, args.deadline_seconds)
    entity_path = args.entity_plan or (out / "entity-plan.json")
    if not entity_path.is_absolute():
        entity_path = ROOT / entity_path
    if not entity_path.is_file():
        raise SystemExit("entity phase requires a CDX-validated finite --entity-plan")
    return run_entity(plan_path, out, entity_path, args.workers, args.max_requests, args.deadline_seconds)


if __name__ == "__main__":
    raise SystemExit(main())

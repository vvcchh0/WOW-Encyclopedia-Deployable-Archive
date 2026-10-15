"""NET-GUIDE-PREFIX-015: bounded unfiltered gallery-prefix CDX probe.

This is a small batch-specific adapter.  It reuses the accepted core3 curl and
source-header parser, plus the accepted control7 dispatch gate.  Preparation is
offline.  Execution issues one exact, unfiltered pre-anchor CDX query per
approved prefix and replays only rows that the response itself proves to be
one full and one thumbnail image per gallery.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import io
import json
import re
import shutil
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
PLAN = ROOT / "research/continuous-recovery-20261015/guide-prefix15-approved-plan.json"
GALLERY_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/guide-gallery-plan-acceptance.json"
GALLERY_PLAN = ROOT / "research/continuous-recovery-20261015/guide-gallery-plan/guide-gallery-plan.json"
CONTROL_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/control14-acceptance.json"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
PROXY = "http://127.0.0.1:7890"
ANCHOR = "20080512210044"
FROM_TS = "20040101000000"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
REDIRECT_CODES = {301, 302, 303, 307, 308}
STOP_CODES = {429, 503}
MAX_ATTEMPTS = 32
WINDOW_SECONDS = 480
MIN_INTERVAL = 1.35
MIN_FREE = 11_005_853_696
MAX_TOTAL = 64 * 1024 * 1024
MAX_ENTITY = 16 * 1024 * 1024
MAX_PAYLOADS = 6
EXPECTED_PLAN_SHA = "479819f3cfb44bd1321bffa6e6a07c0c0ee7211a7853ae5658c7be8cbd1d2135"
EXPECTED_GALLERY_PLAN_SHA = "1e93a84cecb229c2fd4b795c91fa3943e85e8ad5cb71f53ad31bfce46b9279be"
EXPECTED_GALLERY_ACCEPTANCE_SHA = "536320b2f501795880c00505122bbe99d677ad23f73a376edd5baf929dc83b68"
EXPECTED_CONTROL_ACCEPTANCE_SHA = "e4c963c038a9e58a07f8bab47e28f44700b3d893a3f9e4424bd585146ab29fc7"
USER_AGENT = "wow-recovery-guide-prefix15/20261015"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_module(CORE_PATH, "guide_prefix15_core3")
gate_mod = load_module(GATE_PATH, "guide_prefix15_control7")
core.OUT = OUT
core.RAW = RAW
core.PROXY = PROXY
core.USER_AGENT = USER_AGENT
core.MIN_INTERVAL_SECONDS = 0.0
core.MAX_ATTEMPTS = MAX_ATTEMPTS
core.WINDOW_SECONDS = WINDOW_SECONDS
core.MIN_FREE_BYTES = MIN_FREE
core.MAX_TOTAL_BODY_BYTES = MAX_TOTAL
core.MAX_ENTITY_BODY_BYTES = MAX_ENTITY
core.DIRECT_CONNECT_SECONDS = 4
core.DIRECT_MAX_SECONDS = 12
core.PROXY_CONNECT_SECONDS = 8
core.PROXY_MAX_SECONDS = 20
gate_mod.OUT = OUT
gate_mod.RAW = RAW
gate_mod.INTERVAL_SECONDS = MIN_INTERVAL


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def digest_info(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def validate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    paths = [PLAN, GALLERY_ACCEPTANCE, GALLERY_PLAN, CONTROL_ACCEPTANCE]
    if any(not path.is_file() for path in paths):
        raise RuntimeError("one or more approved NET015 inputs are missing")
    observed = {str(path): sha256_file(path) for path in paths}
    if observed[str(PLAN)] != EXPECTED_PLAN_SHA:
        raise RuntimeError(f"approved plan SHA mismatch: {observed[str(PLAN)]}")
    if observed[str(GALLERY_PLAN)] != EXPECTED_GALLERY_PLAN_SHA:
        raise RuntimeError(f"guide gallery plan SHA mismatch: {observed[str(GALLERY_PLAN)]}")
    if observed[str(GALLERY_ACCEPTANCE)] != EXPECTED_GALLERY_ACCEPTANCE_SHA:
        raise RuntimeError(f"guide gallery acceptance SHA mismatch: {observed[str(GALLERY_ACCEPTANCE)]}")
    if observed[str(CONTROL_ACCEPTANCE)] != EXPECTED_CONTROL_ACCEPTANCE_SHA:
        raise RuntimeError(f"control14 acceptance SHA mismatch: {observed[str(CONTROL_ACCEPTANCE)]}")
    plan = read_json(PLAN)
    acceptance = read_json(GALLERY_ACCEPTANCE)
    gallery_plan = read_json(GALLERY_PLAN)
    control = read_json(CONTROL_ACCEPTANCE)
    if acceptance.get("accepted") is not True or acceptance.get("network_requests_by_review") != 0:
        raise RuntimeError("guide gallery acceptance is not accepted and network-free")
    if gallery_plan.get("network_requests") != 0:
        raise RuntimeError("guide gallery plan records unexpected network activity")
    if control.get("accepted") is not True or control.get("errors") not in (None, []):
        raise RuntimeError("control14 acceptance is not accepted")
    if plan.get("task_id") != "NET-GUIDE-PREFIX-015" or len(plan.get("queries") or []) != 3:
        raise RuntimeError("approved plan identity or query count mismatch")
    caps = plan.get("caps") or {}
    for key, expected in {
        "prefixes": 3,
        "pages_per_prefix": 1,
        "continuation_pages": 0,
        "limit_per_page": 1000,
        "max_payloads_total": MAX_PAYLOADS,
        "max_attempts_including_direct_proxy": MAX_ATTEMPTS,
    }.items():
        if caps.get(key) != expected:
            raise RuntimeError(f"plan cap mismatch: {key}={caps.get(key)!r}")
    return plan, {
        "gallery_acceptance": acceptance,
        "gallery_plan": gallery_plan,
        "control14_acceptance": control,
        "input_digests": {str(path.relative_to(ROOT)).replace("\\", "/"): digest_info(path) for path in paths},
    }


def build_candidates(plan: dict[str, Any], aux: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for rank, item in enumerate(plan["queries"], start=1):
        params = item["query_parameters"]
        required = {
            "matchType": "prefix",
            "output": "json",
            "fl": ",".join(FIELDS),
            "from": "20040101",
            "to": "20080512210044",
            "limit": "1000",
            "showResumeKey": "true",
        }
        if any(str(params.get(key)) != value for key, value in required.items()):
            raise RuntimeError(f"query parameters drifted for {item['label']}")
        if item.get("filter") is not None or item.get("collapse") is not None:
            raise RuntimeError(f"approved query unexpectedly filtered/collapsed: {item['label']}")
        rows.append({
            "rank": rank,
            "label": item["label"],
            "gallery": urlsplit(item["prefix"]).path.rstrip("/").rsplit("/", 1)[-1],
            "prefix": item["prefix"],
            "declared_slots": item["declared_slots"],
            "full_pattern": item["full_pattern"],
            "thumb_pattern": item["thumb_pattern"],
            "source_page": item["source_page"],
            "source_page_sha256": item["source_page_sha256"],
            "addshots_markup": item["addshots_markup"],
            "query_parameters": params,
            "cdx_query_url": item["cdx_url"],
            "collapse": None,
            "filter": None,
            "resume_key_used": None,
            "continuation_allowed": False,
            "prior_coverage_note": item.get("prior_coverage_note"),
        })
    return {
        "schema": "wow-recovery.net-guide-prefix15-candidates.v1",
        "batch_id": "NET-GUIDE-PREFIX-015",
        "mode": "prepared",
        "generated_utc": utc(),
        "network_requests": 0,
        "approved_plan_sha256": sha256_file(PLAN),
        "input_digests": aux["input_digests"],
        "policy": {
            "prefixes": 3,
            "pages_per_prefix": 1,
            "continuation_pages": 0,
            "max_payloads_per_group": 2,
            "max_payloads_total": MAX_PAYLOADS,
            "from": FROM_TS,
            "to": ANCHOR,
            "query_output": "json",
            "query_fields": FIELDS,
            "collapse": None,
            "selection": "actual CDX rows only; exact HTTP www origin with default :80 normalization; status 200 image MIME; ssN.jpg and ssN-thumb.jpg; N within declared slots; latest pre-anchor per kind",
            "redirect_follow": 0,
            "integration": "hold all new entities for parent review; do not modify v11/source/export",
        },
        "targets": rows,
    }


def prepare() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    plan, aux = validate_inputs()
    candidates = build_candidates(plan, aux)
    config = {
        "schema": "wow-recovery.net-guide-prefix15-config.v1",
        "batch_id": "NET-GUIDE-PREFIX-015",
        "mode": "prepared",
        "generated_utc": utc(),
        "approved_plan": digest_info(PLAN),
        "inputs": aux["input_digests"],
        "helpers": {
            "core3": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"),
            "control7": str(GATE_PATH.relative_to(ROOT)).replace("\\", "/"),
            "curl": r"C:\Windows\System32\curl.exe",
            "proxy": PROXY,
        },
        "policy": {
            "direct_first_then_confirmed_proxy": True,
            "direct_connect_timeout_seconds": 4,
            "direct_total_timeout_seconds": 12,
            "proxy_connect_timeout_seconds": 8,
            "proxy_total_timeout_seconds": 20,
            "tls_verification": "curl default verification enabled",
            "automatic_redirects": 0,
            "manual_redirect_follow": 0,
            "max_attempts": MAX_ATTEMPTS,
            "window_seconds": WINDOW_SECONDS,
            "minimum_dispatch_interval_seconds": MIN_INTERVAL,
            "minimum_free_bytes": MIN_FREE,
            "max_total_body_bytes": MAX_TOTAL,
            "max_entity_body_bytes": MAX_ENTITY,
            "stop_http_codes": sorted(STOP_CODES),
            "concurrent_source_requests": 1,
        },
        "network_requests": 0,
        "prepared": True,
        "raw_note": "raw headers, trace, stderr and bodies remain local; a zero-byte body after no source status is a local placeholder, not source content",
    }
    write_json(OUT / "candidates.json", candidates)
    write_json(OUT / "config.json", config)
    print(json.dumps({"mode": "prepared", "targets": 3, "network_requests": 0, "candidates": relative(OUT / "candidates.json"), "config": relative(OUT / "config.json")}, ensure_ascii=False))
    return 0


def canonical_field(value: Any) -> str | None:
    aliases = {
        "urlkey": "urlkey", "timestamp": "timestamp", "original": "original", "url": "original",
        "mimetype": "mimetype", "mime": "mimetype", "mime_type": "mimetype",
        "statuscode": "statuscode", "status": "statuscode", "status_code": "statuscode",
        "digest": "digest", "length": "length",
    }
    token = str(value).strip().lower().replace("-", "_")
    return aliases.get(token)


def parse_records_with_header(header: list[str], rows: list[Any]) -> tuple[list[dict[str, str]], bool, str | None]:
    positions: dict[str, int] = {}
    observed = [str(x) for x in header]
    for index, value in enumerate(observed):
        key = canonical_field(value)
        if key and key not in positions:
            positions[key] = index
    if any(key not in positions for key in FIELDS):
        return [], False, "cdx_header_missing_required_field"
    records: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, list):
            return [], False, "cdx_row_not_array"
        records.append({key: str(row[index]) if index < len(row) else "" for key, index in positions.items()})
    return records, True, None


def parse_cdx_body(body: bytes) -> dict[str, Any]:
    text = body.decode("utf-8", errors="replace")
    if not text.strip() or text.strip().lower() in {"[]", "no captures", "no captures found"}:
        return {"parse_valid": True, "parse_error": None, "header_fields_observed": None, "rows": [], "resume_keys": [], "metadata_records": []}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return {"parse_valid": False, "parse_error": f"json_decode:{type(exc).__name__}", "header_fields_observed": None, "rows": [], "resume_keys": [], "metadata_records": []}
    rows: list[dict[str, str]] = []
    metadata: list[dict[str, Any]] = []
    resume_keys: list[str] = []
    header: list[str] | None = None
    if isinstance(payload, list):
        for index, item in enumerate(payload):
            if isinstance(item, list):
                values = [str(x) for x in item]
                if header is None and [canonical_field(x) for x in values] == FIELDS:
                    header = values
                    metadata.append({"record_index": index, "kind": "header", "value": values})
                    continue
                if len(values) == 1 and values[0]:
                    resume_keys.append(values[0])
                    metadata.append({"record_index": index, "kind": "resume_key", "value": values[0]})
                    continue
                if header is None:
                    metadata.append({"record_index": index, "kind": "row_before_header", "value": values})
                else:
                    record, good, error = parse_records_with_header(header, [item])
                    if not good:
                        return {"parse_valid": False, "parse_error": error, "header_fields_observed": header, "rows": [], "resume_keys": resume_keys, "metadata_records": metadata}
                    record[0]["record_index"] = str(index)
                    rows.extend(record)
                continue
            if isinstance(item, dict):
                for key in ("resumeKey", "resume_key", "next_resume_key"):
                    value = item.get(key)
                    if value:
                        resume_keys.append(str(value))
                        metadata.append({"record_index": index, "kind": "resume_key", "value": str(value)})
                metadata.append({"record_index": index, "kind": "metadata", "value": {str(k): str(v) for k, v in item.items() if k not in {"resumeKey", "resume_key", "next_resume_key"}}})
                continue
            metadata.append({"record_index": index, "kind": "metadata", "value": item})
    elif isinstance(payload, dict):
        for key in ("resumeKey", "resume_key", "next_resume_key"):
            value = payload.get(key)
            if value:
                resume_keys.append(str(value))
        raw_rows = payload.get("records") or payload.get("captures") or payload.get("rows") or []
        if not isinstance(raw_rows, list):
            return {"parse_valid": False, "parse_error": "cdx_dict_rows_not_array", "header_fields_observed": None, "rows": [], "resume_keys": resume_keys, "metadata_records": metadata}
        if raw_rows and all(isinstance(row, dict) for row in raw_rows):
            fields = list(dict.fromkeys(str(key) for row in raw_rows for key in row.keys()))
            header = fields
            positions = {canonical_field(key): key for key in fields if canonical_field(key)}
            if any(key not in positions for key in FIELDS):
                return {"parse_valid": False, "parse_error": "cdx_dict_missing_required_field", "header_fields_observed": header, "rows": [], "resume_keys": resume_keys, "metadata_records": metadata}
            for index, row in enumerate(raw_rows):
                records = {key: str(row.get(raw_key, "")) for key, raw_key in positions.items()}
                records["record_index"] = str(index)
                rows.append(records)
        else:
            return {"parse_valid": False, "parse_error": "cdx_dict_row_shape", "header_fields_observed": header, "rows": [], "resume_keys": resume_keys, "metadata_records": metadata}
    else:
        return {"parse_valid": False, "parse_error": "cdx_json_shape", "header_fields_observed": None, "rows": [], "resume_keys": [], "metadata_records": []}
    if header is None and rows:
        return {"parse_valid": False, "parse_error": "cdx_header_missing", "header_fields_observed": None, "rows": [], "resume_keys": resume_keys, "metadata_records": metadata}
    unique_resume = list(dict.fromkeys(resume_keys))
    return {
        "parse_valid": True,
        "parse_error": None,
        "header_fields_observed": header,
        "rows": rows,
        "resume_keys": resume_keys,
        "unique_resume_keys": unique_resume,
        "metadata_records": metadata,
    }


def body_for(attempt: dict[str, Any] | None) -> bytes:
    if not attempt or not attempt.get("executed"):
        return b""
    raw = attempt.get("raw") or {}
    value = str(raw.get("body") or "")
    if not value:
        return b""
    path = (OUT / value).resolve()
    if OUT.resolve() not in path.parents:
        raise RuntimeError("raw body path escaped batch directory")
    return path.read_bytes() if path.is_file() else b""


def attempt_public(attempt: dict[str, Any]) -> dict[str, Any]:
    value = dict(attempt)
    value.pop("cdx_records", None)
    value.pop("cdx_valid_records", None)
    return value


def dispatch_ok(state: Any, window_started: float) -> tuple[bool, str | None]:
    if state.stop_reason:
        return False, state.stop_reason
    if state.attempts >= MAX_ATTEMPTS:
        return False, "attempt_limit"
    if time.monotonic() - window_started >= WINDOW_SECONDS:
        return False, "network_window_exhausted"
    if free_bytes() < MIN_FREE:
        return False, "disk_free_below_threshold"
    if state.total_body_bytes >= MAX_TOTAL:
        return False, "total_body_limit"
    return True, None


def issue(url: str, transport: str, kind: str, target_key: str, state: Any, gate: Any, window_started: float) -> dict[str, Any]:
    ok, reason = dispatch_ok(state, window_started)
    if not ok:
        return {"executed": False, "attempt": state.attempts + 1, "kind": kind, "target_key": target_key, "transport": transport, "url": url, "unrequested_reason": reason or "limit_before_request"}
    number = state.attempts + 1
    gate_record = gate.before_dispatch(number, transport, target_key)
    attempt = core.run_request(url, transport, kind, target_key, state, number)
    attempt["dispatch_utc"] = gate_record["dispatch_utc"]
    attempt["dispatch_monotonic"] = gate_record["dispatch_monotonic"]
    attempt["dispatch_interval_seconds"] = gate_record["interval_since_previous_dispatch_seconds"]
    attempt["gate_persisted_before_transport"] = gate_record["persisted_before_transport"]
    raw = body_for(attempt)
    attempt["local_zero_byte_body_placeholder"] = bool(attempt.get("source_status") is None and not raw)
    attempt["body_is_source_response"] = attempt.get("source_status") is not None
    return attempt


def issue_confirmed(url: str, kind: str, target_key: str, transport: str, state: Any, gate: Any, window_started: float) -> tuple[list[dict[str, Any]], str]:
    attempts: list[dict[str, Any]] = []
    current = transport
    first = issue(url, current, kind, target_key, state, gate, window_started)
    attempts.append(first)
    if current == "direct" and first.get("executed") and first.get("transport_error") and not state.stop_reason:
        second = issue(url, "proxy", kind, target_key, state, gate, window_started)
        attempts.append(second)
        if second.get("executed") and not second.get("transport_error"):
            current = "proxy"
    return attempts, current


def same_origin_prefix(original: str, prefix: str) -> str:
    try:
        observed = urlsplit(original)
        requested = urlsplit(prefix)
        observed_port = observed.port
        requested_port = requested.port
    except ValueError:
        return "invalid_url"
    if observed.scheme.lower() != requested.scheme.lower():
        return "scheme_mismatch"
    if (observed.hostname or "").lower() != (requested.hostname or "").lower():
        return "host_mismatch"
    if observed_port == 80 and observed.scheme.lower() == "http":
        observed_port = None
    if requested_port == 80 and requested.scheme.lower() == "http":
        requested_port = None
    if observed_port != requested_port:
        return "non_default_port_mismatch"
    if observed.query or observed.fragment:
        return "query_or_fragment_present"
    if not observed.path.startswith(requested.path):
        return "path_prefix_mismatch"
    return "same_origin_prefix"


def decorate_rows(rows: list[dict[str, str]], item: dict[str, Any]) -> list[dict[str, Any]]:
    prefix = item["prefix"]
    gallery = item["gallery"]
    path_base = urlsplit(prefix).path
    full_re = re.compile(re.escape(path_base) + r"ss([1-9][0-9]*)\.jpg$")
    thumb_re = re.compile(re.escape(path_base) + r"ss([1-9][0-9]*)-thumb\.jpg$")
    decorated: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        original = str(row.get("original") or "")
        origin_kind = same_origin_prefix(original, prefix)
        parsed = urlsplit(original) if original else None
        path = parsed.path if parsed else ""
        full = full_re.fullmatch(path)
        thumb = thumb_re.fullmatch(path)
        number = int((full or thumb).group(1)) if (full or thumb) else None
        status_value = str(row.get("statuscode") or "")
        status = int(status_value) if status_value.isdigit() else None
        timestamp = str(row.get("timestamp") or "")
        image_mime = str(row.get("mimetype") or "").lower().startswith("image/")
        kind = "full" if full else "thumb" if thumb else None
        eligible = bool(
            origin_kind == "same_origin_prefix"
            and kind
            and number is not None
            and 1 <= number <= int(item["declared_slots"])
            and status == 200
            and image_mime
            and re.fullmatch(r"\d{14}", timestamp)
            and FROM_TS <= timestamp <= ANCHOR
        )
        decorated.append({
            **row,
            "record_index": index,
            "statuscode_int": status,
            "origin_match": origin_kind,
            "path": path,
            "gallery": gallery,
            "kind": kind,
            "number": number,
            "image_mime": image_mime,
            "within_preanchor": bool(re.fullmatch(r"\d{14}", timestamp) and FROM_TS <= timestamp <= ANCHOR),
            "eligible": eligible,
        })
    return decorated


def select_latest(rows: list[dict[str, Any]], kind: str) -> dict[str, Any] | None:
    candidates = [row for row in rows if row.get("eligible") and row.get("kind") == kind]
    return max(candidates, key=lambda row: (str(row.get("timestamp") or ""), -int(row.get("record_index") or 0))) if candidates else None


def parse_memento(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None
    return parsed.isoformat()


def b32_sha1(body: bytes) -> str:
    return base64.b32encode(hashlib.sha1(body).digest()).decode("ascii").rstrip("=")


def validate_image(attempt: dict[str, Any], capture: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    body = body_for(attempt)
    status = attempt.get("source_status")
    content_type = str(attempt.get("content_type") or "")
    memento = parse_memento(attempt.get("memento_datetime"))
    common: dict[str, Any] = {
        "source_status": status,
        "content_type": content_type,
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "actual_memento": memento,
        "cdx_digest": capture.get("digest"),
        "cdx_length": capture.get("length"),
        "cdx_digest_calculated": b32_sha1(body) if body else None,
        "cdx_digest_match": bool(body and capture.get("digest") and b32_sha1(body).upper() == str(capture.get("digest")).strip().upper().rstrip("=")),
        "cdx_length_is_capture_metadata": True,
        "raw_body_path": (attempt.get("raw") or {}).get("body"),
        "raw_headers_path": (attempt.get("raw") or {}).get("headers"),
    }
    if attempt.get("transport_error") or status is None:
        return "transport_error", {**common, "reason": attempt.get("transport_reason") or "no_source_http_response"}
    if status in STOP_CODES:
        return "rate_limited", {**common, "retry_after": attempt.get("retry_after")}
    if status in REDIRECT_CODES:
        return "redirect_unfollowed", {**common, "location": attempt.get("location")}
    if status != 200:
        return "soft404", {**common, "reason": "non_200_source_response"}
    if not memento:
        return "soft404", {**common, "reason": "missing_or_invalid_actual_memento"}
    try:
        if datetime.fromisoformat(memento) > datetime.strptime(ANCHOR, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc):
            return "soft404", {**common, "reason": "actual_memento_after_anchor"}
    except ValueError:
        return "soft404", {**common, "reason": "actual_memento_parse_failed"}
    if not content_type.lower().startswith("image/"):
        return "soft404", {**common, "reason": "non_image_source_mime"}
    if not body:
        return "soft404", {**common, "reason": "empty_200_body"}
    try:
        from PIL import Image

        with Image.open(io.BytesIO(body)) as image:
            image.verify()
        with Image.open(io.BytesIO(body)) as image:
            image.load()
            common["decode"] = {"format": image.format, "width": image.width, "height": image.height, "mode": image.mode}
    except Exception as exc:
        return "soft404", {**common, "reason": "pillow_verify_or_load_failed", "error_type": type(exc).__name__}
    if not common["cdx_digest_match"]:
        return "soft404", {**common, "reason": "cdx_digest_mismatch"}
    return "valid_image", common


def summarize_index(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "statuscode": dict(sorted(Counter(str(row.get("statuscode") or "") for row in rows).items())),
        "mimetype": dict(sorted(Counter(str(row.get("mimetype") or "") for row in rows).items())),
        "origin_match": dict(sorted(Counter(str(row.get("origin_match") or "") for row in rows).items())),
        "kind": dict(sorted(Counter(str(row.get("kind") or "other") for row in rows).items())),
        "redirect_count": sum(int(row.get("statuscode_int") in REDIRECT_CODES) for row in rows),
        "preanchor_count": sum(int(bool(row.get("within_preanchor"))) for row in rows),
        "eligible_count": sum(int(bool(row.get("eligible"))) for row in rows),
    }


def run_query(item: dict[str, Any], transport: str, state: Any, gate: Any, window_started: float, rank: int) -> tuple[dict[str, Any], str]:
    attempts, confirmed = issue_confirmed(item["cdx_query_url"], "cdx", f"prefix-{rank}-{item['gallery']}", transport, state, gate, window_started)
    executed = [attempt for attempt in attempts if attempt.get("executed")]
    final = executed[-1] if executed else None
    body = body_for(final)
    parsed = {"parse_valid": False, "parse_error": "no_source_200_response", "header_fields_observed": None, "rows": [], "resume_keys": [], "metadata_records": []}
    if final and final.get("source_status") == 200 and not final.get("transport_error"):
        parsed = parse_cdx_body(body)
    rows = decorate_rows(parsed.get("rows") or [], item) if parsed.get("parse_valid") else []
    unique_resume = list(dict.fromkeys(parsed.get("resume_keys") or []))
    if not rows and parsed.get("parse_valid") and not parsed.get("resume_keys"):
        category = "cdx_empty_in_scoped_window"
    elif not parsed.get("parse_valid"):
        category = "cdx_invalid"
    else:
        category = "cdx_rows_without_valid_200"
    result = {
        "rank": rank,
        "label": item["label"],
        "gallery": item["gallery"],
        "prefix": item["prefix"],
        "cdx_query_url": item["cdx_query_url"],
        "query_parameters": item["query_parameters"],
        "collapse": None,
        "filter": None,
        "attempts": [attempt_public(value) for value in attempts],
        "attempt_count": len([value for value in attempts if value.get("executed")]),
        "source_response_count": sum(value.get("source_status") is not None for value in attempts),
        "final_source_status": final.get("source_status") if final else None,
        "final_content_type": final.get("content_type") if final else None,
        "final_body_bytes": len(body) if final else 0,
        "final_body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "final_raw_body_path": (final.get("raw") or {}).get("body") if final else None,
        "parse_valid": parsed.get("parse_valid"),
        "parse_error": parsed.get("parse_error"),
        "header_fields_observed": parsed.get("header_fields_observed"),
        "metadata_records": parsed.get("metadata_records") or [],
        "resume_keys_observed": parsed.get("resume_keys") or [],
        "unique_resume_keys": unique_resume,
        "resume_key_used": None,
        "continuation_followed": False,
        "capture_index_count": len(rows),
        "capture_records": rows,
        "index_distribution": summarize_index(rows),
        "category": category,
        "confirmed_transport_after_query": confirmed,
    }
    return result, confirmed


def replay_selected(query: dict[str, Any], state: Any, gate: Any, window_started: float, transport: str) -> tuple[list[dict[str, Any]], str]:
    selected = [select_latest(query["capture_records"], "full"), select_latest(query["capture_records"], "thumb")]
    replays: list[dict[str, Any]] = []
    current = transport
    for capture in selected:
        if capture is None or len(replays) >= MAX_PAYLOADS:
            continue
        replay_url = core.replay_url(capture)
        attempts, current = issue_confirmed(replay_url, "replay", f"{query['gallery']}-{capture['kind']}-ss{capture['number']}", current, state, gate, window_started)
        executed = [attempt for attempt in attempts if attempt.get("executed")]
        final = executed[-1] if executed else None
        if final is None:
            category, validation = "not_requested", {"reason": "limit_before_replay"}
        else:
            category, validation = validate_image(final, capture)
        replays.append({
            "kind": capture["kind"],
            "number": capture["number"],
            "query_original_url": capture["original"],
            "replay_url": replay_url,
            "captured_original_url": capture["original"],
            "capture": capture,
            "attempts": [attempt_public(value) for value in attempts],
            "attempt_count": len(executed),
            "category": category,
            "validation": validation,
            "actual_memento": validation.get("actual_memento") if validation else None,
            "source_status": validation.get("source_status") if validation else None,
            "content_type": validation.get("content_type") if validation else None,
            "body_bytes": validation.get("body_bytes", 0) if validation else 0,
            "body_sha256": validation.get("body_sha256") if validation else None,
        })
        if state.stop_reason:
            break
    return replays, current


def payload_map(queries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for query in queries:
        for replay in query.get("replays") or []:
            if replay.get("category") != "valid_image":
                continue
            val = replay["validation"]
            cap = replay["capture"]
            output.append({
                "target": replay["query_original_url"],
                "query_original_url": replay["query_original_url"],
                "captured_original_url": replay["captured_original_url"],
                "actual_memento": val.get("actual_memento"),
                "source_status": val.get("source_status"),
                "content_type": val.get("content_type"),
                "body_bytes": val.get("body_bytes"),
                "body_sha256": val.get("body_sha256"),
                "raw_body_path": val.get("raw_body_path"),
                "raw_headers_path": val.get("raw_headers_path"),
                "capture_timestamp": cap.get("timestamp"),
                "cdx_digest": cap.get("digest"),
                "cdx_length": cap.get("length"),
                "cdx_digest_calculated": val.get("cdx_digest_calculated"),
                "cdx_digest_match": val.get("cdx_digest_match"),
                "decode": val.get("decode"),
                "action": "hold for parent review; entity remains only in this batch raw directory",
            })
    return output


def render_summary(report: dict[str, Any], maps: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    targets = []
    for result in report["prefix_results"]:
        targets.append({
            "rank": result["rank"],
            "label": result["label"],
            "prefix": result["prefix"],
            "category": result["category"],
            "capture_index_count": result["capture_index_count"],
            "eligible_full_count": sum(int(row.get("eligible") and row.get("kind") == "full") for row in result["capture_records"]),
            "eligible_thumb_count": sum(int(row.get("eligible") and row.get("kind") == "thumb") for row in result["capture_records"]),
            "redirect_count": result["index_distribution"].get("redirect_count", 0),
            "resume_keys_observed": result["unique_resume_keys"],
            "resume_key_used": None,
            "continuation_followed": False,
            "replays": [
                {"kind": x["kind"], "number": x["number"], "category": x["category"], "actual_memento": x.get("actual_memento"), "body_bytes": x.get("body_bytes", 0), "body_sha256": x.get("body_sha256")}
                for x in result.get("replays") or []
            ],
        })
    summary = {
        "schema": "wow-recovery.net-guide-prefix15-sanitized-summary.v1",
        "batch_id": "NET-GUIDE-PREFIX-015",
        "mode": "executed",
        "started_utc": report["started_utc"],
        "request_window_finished_utc": report["request_window_finished_utc"],
        "finished_utc": report["finished_utc"],
        "report_updated_utc": report["report_updated_utc"],
        "target_count": len(targets),
        "attempt_count": report["transport_attempt_count"],
        "source_response_count": report["source_response_count"],
        "capture_index_count": report["capture_index_count"],
        "valid_entity_count": report["valid_entity_count"],
        "total_body_bytes": report["total_body_bytes"],
        "payload_body_bytes": report["payload_body_bytes"],
        "category_counts": report["category_counts"],
        "stop_reason": report["stop_reason"],
        "confirmed_transport": report["confirmed_transport"],
        "min_dispatch_interval_seconds": report["gate_validation"]["min_dispatch_interval_seconds"],
        "min_request_start_interval_seconds": report["gate_validation"]["min_request_start_interval_seconds"],
        "batch_policy_accepted": report["gate_validation"]["batch_policy_accepted"],
        "disk_free_bytes_before": report["preflight"]["disk_free_bytes_before"],
        "disk_free_bytes_after": report["preflight"]["disk_free_bytes_after"],
        "targets": targets,
        "valid_payloads": maps,
        "raw_evidence_note": "Raw headers, traces, stderr and bodies remain only in this batch directory. A zero-byte body after a transport failure is a local placeholder, not source response content. CDX rows and CDX length are index evidence, not payload bytes.",
    }
    lines = [
        "# NET-GUIDE-PREFIX-015 sanitized summary",
        "",
        f"- Window: `{report['started_utc']}` to `{report['request_window_finished_utc']}`; report updated `{report['report_updated_utc']}`.",
        f"- Prefixes: {len(targets)}; transport attempts: {report['transport_attempt_count']}; real source responses: {report['source_response_count']}; CDX rows: {report['capture_index_count']}; validated image entities: {report['valid_entity_count']}.",
        f"- Body bytes: total `{report['total_body_bytes']}`, validated payloads `{report['payload_body_bytes']}`. Stop: `{report['stop_reason']}`.",
        f"- Gate: min dispatch interval `{report['gate_validation']['min_dispatch_interval_seconds']}`; min request-start interval `{report['gate_validation']['min_request_start_interval_seconds']}`; accepted `{report['gate_validation']['batch_policy_accepted']}`.",
        "",
        "| Prefix | Category | CDX rows | Eligible full | Eligible thumb | Redirect rows | Replays |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for target in targets:
        replay_text = ", ".join(f"{x['kind']} ss{x['number']}={x['category']}" for x in target["replays"]) or "none requested"
        lines.append(f"| `{target['label']}` | `{target['category']}` | {target['capture_index_count']} | {target['eligible_full_count']} | {target['eligible_thumb_count']} | {target['redirect_count']} | {replay_text} |")
    lines.extend(["", "No continuation page was requested or followed; observed resume keys are retained in the JSON report. New entities are held for parent review and were not integrated."])
    return summary, "\n".join(lines) + "\n"


def execute() -> int:
    if not (OUT / "candidates.json").is_file() or not (OUT / "config.json").is_file():
        raise RuntimeError("run --prepare before --execute")
    if (OUT / "batch-report.json").exists():
        raise RuntimeError("refusing to repeat NET015 after batch-report.json exists")
    plan, aux = validate_inputs()
    candidates = read_json(OUT / "candidates.json")
    if candidates.get("approved_plan_sha256") != EXPECTED_PLAN_SHA:
        raise RuntimeError("candidate plan digest mismatch")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    disk_before = free_bytes()
    if disk_before < MIN_FREE:
        raise RuntimeError(f"D free space below floor: {disk_before}")
    started_utc = utc()
    window_started = time.monotonic()
    state = core.RunState(window_started)
    journal = {
        "schema": "wow-recovery.net-guide-prefix15-dispatch-log.v1",
        "batch_id": "NET-GUIDE-PREFIX-015",
        "simulation": False,
        "policy": {"minimum_dispatch_interval_seconds": MIN_INTERVAL, "max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW_SECONDS, "redirects": 0},
        "disk_preflight": {"checked_utc": utc(), "disk_free_bytes": disk_before, "minimum_free_bytes": MIN_FREE},
        "dispatches": [],
    }
    gate = gate_mod.GateState(datetime.now(timezone.utc) - timedelta(seconds=1), journal_path=OUT / "dispatch-log.json", journal=journal)
    gate.persist()
    prefix_results: list[dict[str, Any]] = []
    transport = "direct"
    try:
        for rank, item in enumerate(candidates["targets"], start=1):
            if state.stop_reason:
                prefix_results.append({"rank": rank, "label": item["label"], "gallery": item["gallery"], "prefix": item["prefix"], "cdx_query_url": item["cdx_query_url"], "category": "not_requested", "unrequested_reason": state.stop_reason, "capture_index_count": 0, "capture_records": [], "index_distribution": {}, "unique_resume_keys": [], "resume_key_used": None, "continuation_followed": False, "attempts": [], "attempt_count": 0, "source_response_count": 0, "replays": []})
                continue
            result, transport = run_query(item, transport, state, gate, window_started, rank)
            if result.get("parse_valid") and not state.stop_reason and result.get("capture_records"):
                replays, transport = replay_selected(result, state, gate, window_started, transport)
            else:
                replays = []
            result["replays"] = replays
            result["selected_full"] = select_latest(result.get("capture_records") or [], "full")
            result["selected_thumb"] = select_latest(result.get("capture_records") or [], "thumb")
            result["payload_count"] = sum(int(x.get("category") == "valid_image") for x in replays)
            prefix_results.append(result)
            if state.stop_reason:
                continue
    finally:
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=free_bytes)
    request_window_finished = utc()
    disk_after = free_bytes()
    dispatch_intervals = [x.get("interval_since_previous_dispatch_seconds") for x in gate.dispatches if x.get("interval_since_previous_dispatch_seconds") is not None]
    request_starts: list[float] = []
    for result in prefix_results:
        for attempt in result.get("attempts") or []:
            if attempt.get("started_utc"):
                request_starts.append(datetime.fromisoformat(str(attempt["started_utc"]).replace("Z", "+00:00")).timestamp())
        for replay in result.get("replays") or []:
            for attempt in replay.get("attempts") or []:
                if attempt.get("started_utc"):
                    request_starts.append(datetime.fromisoformat(str(attempt["started_utc"]).replace("Z", "+00:00")).timestamp())
    request_starts.sort()
    start_intervals = [request_starts[i] - request_starts[i - 1] for i in range(1, len(request_starts))]
    gate_validation = {
        "min_dispatch_interval_seconds": min(dispatch_intervals, default=None),
        "min_request_start_interval_seconds": min(start_intervals, default=None),
        "required_minimum_seconds": MIN_INTERVAL,
        "dispatch_intervals_compliant": all(value >= MIN_INTERVAL for value in dispatch_intervals),
        "request_start_intervals_compliant": all(value >= MIN_INTERVAL for value in start_intervals),
        "batch_policy_accepted": all(value >= MIN_INTERVAL for value in dispatch_intervals) and all(value >= MIN_INTERVAL for value in start_intervals),
        "dispatch_count": len(gate.dispatches),
    }
    maps = payload_map(prefix_results)
    categories = Counter(str(result.get("category")) for result in prefix_results)
    payload_body_bytes = sum(int(item.get("body_bytes") or 0) for item in maps)
    report = {
        "schema": "wow-recovery.net-guide-prefix15-batch-report.v1",
        "batch_id": "NET-GUIDE-PREFIX-015",
        "mode": "executed",
        "started_utc": started_utc,
        "request_window_finished_utc": request_window_finished,
        "finished_utc": request_window_finished,
        "report_updated_utc": utc(),
        "inputs": {"approved_plan": digest_info(PLAN), "candidates": digest_info(OUT / "candidates.json"), **aux["input_digests"]},
        "policy": {"max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW_SECONDS, "minimum_dispatch_interval_seconds": MIN_INTERVAL, "max_total_body_bytes": MAX_TOTAL, "max_entity_body_bytes": MAX_ENTITY, "minimum_free_bytes": MIN_FREE, "automatic_redirects": 0, "manual_redirect_follow": 0, "direct_first_then_confirmed_proxy": True, "tls_verification": "curl default verification enabled"},
        "preflight": {"disk_free_bytes_before": disk_before, "disk_free_bytes_after": disk_after, "minimum_free_bytes": MIN_FREE},
        "postflight": postflight,
        "confirmed_transport": transport,
        "target_count": len(prefix_results),
        "unique_target_count": len({result.get("prefix") for result in prefix_results}),
        "category_counts": dict(sorted(categories.items())),
        "transport_attempt_count": state.attempts,
        "source_request_count": state.attempts,
        "failed_attempt_count": state.failed_attempts,
        "source_response_count": state.source_responses,
        "capture_index_count": sum(int(result.get("capture_index_count") or 0) for result in prefix_results),
        "selected_capture_count": sum(int(result.get("selected_full") is not None) + int(result.get("selected_thumb") is not None) for result in prefix_results),
        "valid_entity_count": len(maps),
        "total_body_bytes": state.total_body_bytes,
        "payload_body_bytes": payload_body_bytes,
        "stop_reason": state.stop_reason or "completed",
        "stop_detail": state.stop_detail,
        "rate_limit": state.rate_limit,
        "gate_validation": gate_validation,
        "prefix_results": prefix_results,
        "resume_key_policy": {"observed_saved": True, "used": False, "continuation_pages_requested": 0},
        "dispatch_log": relative(OUT / "dispatch-log.json"),
        "raw_evidence_note": "Raw headers, traces, stderr and bodies remain only below this batch raw directory. A zero-byte body after a transport failure is a local placeholder, not source response content. CDX length is capture-index metadata and is never used as payload byte length.",
    }
    write_json(OUT / "batch-report.json", report)
    write_json(OUT / "payload-source-map.json", {"schema": "wow-recovery.net-guide-prefix15-payload-source-map.v1", "batch_id": "NET-GUIDE-PREFIX-015", "entries": maps})
    redirects = []
    for result in prefix_results:
        for row in result.get("capture_records") or []:
            if row.get("statuscode_int") in REDIRECT_CODES:
                redirects.append({"prefix": result["prefix"], "record_index": row.get("record_index"), "timestamp": row.get("timestamp"), "original": row.get("original"), "statuscode": row.get("statuscode"), "mimetype": row.get("mimetype"), "action": "index evidence only; no replay/follow"})
    write_json(OUT / "redirect-evidence.json", {"schema": "wow-recovery.net-guide-prefix15-redirect-evidence.v1", "entries": redirects})
    summary, markdown = render_summary(report, maps)
    write_json(OUT / "sanitized-summary.json", summary)
    (OUT / "sanitized-summary.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"mode": "executed", "attempts": state.attempts, "source_responses": state.source_responses, "capture_index_count": report["capture_index_count"], "valid_entities": len(maps), "stop_reason": report["stop_reason"], "min_dispatch_interval": gate_validation["min_dispatch_interval_seconds"], "min_request_start_interval": gate_validation["min_request_start_interval_seconds"]}, ensure_ascii=False))
    return 0


def rebuild_offline() -> int:
    """Correct only derived labels after execution; never reads the network."""
    report_path = OUT / "batch-report.json"
    map_path = OUT / "payload-source-map.json"
    if not report_path.is_file() or not map_path.is_file():
        raise RuntimeError("cannot rebuild before an executed report exists")
    report = read_json(report_path)
    changed = 0
    for result in report.get("prefix_results") or []:
        rows = result.get("capture_records") or []
        if result.get("category") == "indexed_candidates" and rows and not any(row.get("eligible") for row in rows):
            result["category"] = "cdx_rows_without_valid_200"
            result["unrequested_reason"] = "index_rows_without_same_origin_status_200_image_capture"
            changed += 1
    report["category_counts"] = dict(sorted(Counter(str(result.get("category")) for result in report.get("prefix_results") or []).items()))
    report["report_updated_utc"] = utc()
    report["offline_rebuild"] = {
        "performed": True,
        "network_requests": 0,
        "changed_prefix_labels": changed,
        "reason": "rows were present but none met the approved same-origin status-200 image filename rule; empty rows remain cdx_empty_in_scoped_window",
    }
    write_json(report_path, report)
    maps = (read_json(map_path).get("entries") or [])
    summary, markdown = render_summary(report, maps)
    summary["offline_rebuild"] = report["offline_rebuild"]
    write_json(OUT / "sanitized-summary.json", summary)
    (OUT / "sanitized-summary.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"mode": "offline_rebuild", "network_requests": 0, "changed_prefix_labels": changed, "report_updated_utc": report["report_updated_utc"]}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.prepare, args.execute, args.rebuild)) != 1:
        parser.error("choose exactly one of --prepare, --execute or --rebuild")
    if args.prepare:
        return prepare()
    if args.execute:
        return execute()
    return rebuild_offline()


if __name__ == "__main__":
    raise SystemExit(main())

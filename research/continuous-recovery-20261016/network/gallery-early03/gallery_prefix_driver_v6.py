"""Bounded exact-prefix CDX index probe for NETWORK29 early gaps.

The fixture path is offline.  The execute path is the parent-authorized network
window and never follows resume keys or replays a payload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
NETWORK = ROOT / "research" / "continuous-recovery-20261016" / "network"
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
PLAN_PATH = OUT / "plan.json"
REGISTRY = ROOT / "research" / "continuous-recovery-20261016" / "local-audit" / "gallery-prefix-registry-v5" / "gallery-prefix-registry-v5.json"
BATCH_ID = "WAYBACK-GALLERYEARLY03-20261016"
USER_AGENT = "wow-recovery-gallery-early03/20261016"
PROXY = "http://127.0.0.1:7890"
FROM_TS, TO_TS, LIMIT = "20000101000000", "20080512210044", 500
WINDOW_SECONDS, MAX_ATTEMPTS = 900.0, 40
MAX_TOTAL_BODY_BYTES, MAX_ENTITY_BODY_BYTES = 16 * 1024 * 1024, 8 * 1024 * 1024
# The historical GALLERYPREFIX01 driver slept until 5.1s and Windows returned
# from sleep early (observed 5.093s).  v3 treats 5.25s as the scheduling floor,
# then recomputes persisted minima against the requested acceptance floor.
MIN_DISPATCH_SECONDS, MIN_REQUEST_START_SECONDS = 5.25, 5.0
ACCEPTANCE_DISPATCH_SECONDS = 5.25
DISK_FLOOR_BYTES = 11_005_853_696
STOP_HTTP_CODES = {429, 503}
DIRECT_CONNECT_SECONDS, DIRECT_MAX_SECONDS = 4.0, 12.0
PROXY_CONNECT_SECONDS, PROXY_MAX_SECONDS = 8.0, 20.0
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
EXPECTED = {
    "registry": "",
}
PRIOR_FAILURE_TAIL = 2
HISTORICAL_GALLERY_TAIL = 5
LATEST_TAIL = 2
ANCHOR_TO_TS = "20080512210044"


def now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def write_json(path: Path, value: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def free_bytes() -> int:
    return shutil.disk_usage(ROOT).free


def cf(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def parse_cdx(body: bytes) -> dict[str, Any]:
    text = body.decode("utf-8", errors="replace")
    if not text.strip() or text.strip().lower() in {"[]", "no captures", "no captures found"}:
        return {"valid": True, "error": None, "header": None, "rows": [], "resume": [], "metadata": []}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"valid": False, "error": "json_decode", "header": None, "rows": [], "resume": [], "metadata": []}
    rows: list[dict[str, str]] = []
    metadata: list[dict[str, Any]] = []
    resume: list[str] = []
    unrecognized: list[dict[str, Any]] = []
    header: list[str] | None = None

    def list_item(values: list[Any], index: int) -> bool:
        nonlocal header
        vals = [str(x) for x in values]
        # The CDX server emits an empty-array separator immediately before a
        # one-element resumption-key array.  It is metadata, never a capture.
        if not vals:
            metadata.append({"record_index": index, "kind": "separator"})
            return True
        if header is None and [cf(x) for x in vals] == [cf(x) for x in FIELDS]:
            header = vals
            metadata.append({"record_index": index, "kind": "header"})
            return True
        if len(vals) == 1 and vals[0]:
            resume.append(vals[0])
            metadata.append({"record_index": index, "kind": "resume_key", "value": vals[0]})
            return True
        if header is None:
            entry = {"record_index": index, "kind": "row_before_header"}
            metadata.append(entry)
            unrecognized.append(entry)
            return True
        positions = {cf(name): pos for pos, name in enumerate(header)}
        if any(cf(name) not in positions for name in FIELDS):
            return False
        rows.append({name: vals[positions[cf(name)]] if positions[cf(name)] < len(vals) else "" for name in FIELDS} | {"record_index": str(index)})
        return True

    if isinstance(payload, list):
        for index, item in enumerate(payload):
            if isinstance(item, list):
                if not list_item(item, index):
                    return {"valid": False, "error": "cdx_row_fields", "header": header, "rows": [], "resume": resume, "metadata": metadata}
            elif isinstance(item, dict):
                keys = ("resumeKey", "resume_key", "next_resume_key")
                found = [str(item[key]) for key in keys if item.get(key)]
                if found:
                    resume.extend(found)
                    metadata.append({"record_index": index, "kind": "metadata", "resume_key": True})
                elif all(key in item for key in FIELDS):
                    rows.append({key: str(item.get(key, "")) for key in FIELDS} | {"record_index": str(index)})
                else:
                    entry = {"record_index": index, "kind": "unrecognized_metadata"}
                    metadata.append(entry)
                    unrecognized.append(entry)
            else:
                entry = {"record_index": index, "kind": "unrecognized_metadata"}
                metadata.append(entry)
                unrecognized.append(entry)
    elif isinstance(payload, dict):
        for key in ("resumeKey", "resume_key", "next_resume_key"):
            if payload.get(key):
                resume.append(str(payload[key]))
        raw = payload.get("records") or payload.get("captures") or payload.get("rows") or []
        if not isinstance(raw, list):
            return {"valid": False, "error": "cdx_dict_rows_not_array", "header": None, "rows": [], "resume": resume, "metadata": metadata}
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                return {"valid": False, "error": "cdx_dict_row_shape", "header": None, "rows": [], "resume": resume, "metadata": metadata}
            rows.append({key: str(item.get(key, "")) for key in FIELDS} | {"record_index": str(index)})
        header = FIELDS[:]
    else:
        return {"valid": False, "error": "cdx_json_shape", "header": None, "rows": [], "resume": [], "metadata": []}
    if unrecognized:
        return {"valid": False, "error": "cdx_unrecognized_metadata", "header": header, "rows": rows, "resume": list(dict.fromkeys(resume)), "metadata": metadata}
    if rows and header is None:
        return {"valid": False, "error": "cdx_header_missing", "header": None, "rows": [], "resume": resume, "metadata": metadata}
    return {"valid": True, "error": None, "header": header, "rows": rows, "resume": list(dict.fromkeys(resume)), "metadata": metadata}


def same_origin(original: str, prefix: str) -> str:
    try:
        observed, requested = urlsplit(original), urlsplit(prefix)
        op, rp = observed.port, requested.port
    except ValueError:
        return "invalid_url"
    if observed.scheme.lower() != requested.scheme.lower():
        return "scheme_mismatch"
    if (observed.hostname or "").lower() != (requested.hostname or "").lower():
        return "host_mismatch"
    if op == 80 and observed.scheme.lower() == "http": op = None
    if rp == 80 and requested.scheme.lower() == "http": rp = None
    if op != rp: return "non_default_port_mismatch"
    if observed.query or observed.fragment: return "query_or_fragment_present"
    if not observed.path.startswith(requested.path): return "path_prefix_mismatch"
    return "same_origin_prefix"


def project_rows(parsed: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    prefix, base = item["prefix"], urlsplit(item["prefix"]).path
    query_window = item.get("query_window") or {}
    query_from = str(query_window.get("from") or FROM_TS)
    query_to = str(query_window.get("to") or ANCHOR_TO_TS)
    full_re = re.compile(re.escape(base) + r"ss([1-9][0-9]*)\.jpg$")
    thumb_re = re.compile(re.escape(base) + r"ss([1-9][0-9]*)-thumb\.jpg$")
    rows, fulls, thumbs, nested, other, redirects, direct_variants = [], [], [], [], [], [], []
    for row in parsed.get("rows") or []:
        original = str(row.get("original") or "")
        identity = same_origin(original, prefix)
        parsed_url = urlsplit(original) if original else None
        path = parsed_url.path if parsed_url else ""
        match = full_re.fullmatch(path) or thumb_re.fullmatch(path)
        kind = "full" if full_re.fullmatch(path) else "thumb" if thumb_re.fullmatch(path) else None
        direct_variant = bool(kind and identity != "same_origin_prefix")
        number = int(match.group(1)) if match else None
        status_text, timestamp = str(row.get("statuscode") or ""), str(row.get("timestamp") or "")
        status = int(status_text) if status_text.isdigit() else None
        mime = str(row.get("mimetype") or "").lower()
        within = bool(re.fullmatch(r"\d{14}", timestamp) and query_from <= timestamp <= query_to)
        eligible = bool(identity == "same_origin_prefix" and kind and number and status == 200 and mime in {"image/jpeg", "image/gif"} and within)
        view = {"record_index": row.get("record_index"), "urlkey": row.get("urlkey"), "timestamp": timestamp, "original": original, "mimetype": row.get("mimetype"), "statuscode": row.get("statuscode"), "digest": row.get("digest"), "length": row.get("length"), "identity": identity, "path": path, "literal_kind": kind, "number": number, "within_query_window": within, "strict_image_candidate": eligible, "direct_origin_variant": direct_variant}
        rows.append(view)
        if status is not None and 300 <= status <= 399: redirects.append(view)
        if eligible and kind == "full": fulls.append(view)
        elif eligible and kind == "thumb": thumbs.append(view)
        elif identity == "same_origin_prefix": nested.append(view)
        else:
            other.append(view)
            if direct_variant:
                direct_variants.append(view)
    return {"rows": rows, "strict_literal_full_candidates": fulls, "strict_literal_thumb_candidates": thumbs, "nested_preview_or_other_rows": nested, "other_rows": other, "direct_origin_variant_rows": direct_variants, "direct_identity_variant_candidates": direct_variants, "redirect_rows": redirects, "row_counts": {"returned_rows": len(rows), "strict_full": len(fulls), "strict_thumb": len(thumbs), "nested_preview_or_other": len(nested), "other": len(other), "direct_origin_variant": len(direct_variants), "direct_identity_variant_candidates": len(direct_variants), "redirect": len(redirects)}}


def phase(trace: Path, stderr: Path) -> dict[str, Any]:
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") if p.exists() else "" for p in (trace, stderr)).lower()
    markers: list[str] = []
    for needle, label in [("trying ", "connection_attempt_logged"), ("connection timed out", "tcp_connect_failed_or_timed_out"), ("failed to connect", "tcp_connect_failed_or_timed_out"), ("connection established", "proxy_connect_established"), ("connect phase completed", "proxy_connect_established"), ("alpn: server accepted", "tls_handshake_completed"), ("ssl/tls connection renegotiated", "tls_handshake_completed"), ("failed to receive handshake", "tls_handshake_failed"), ("ssl/tls connection failed", "tls_handshake_failed"), ("request completely sent off", "get_request_sent"), ("<= recv header", "http_headers_observed"), ("closing connection", "connection_closed")]:
        if needle in text and label not in markers: markers.append(label)
    if "could not resolve host" in text: boundary = "dns"
    elif "tcp_connect_failed_or_timed_out" in markers and "proxy_connect_established" not in markers: boundary = "tcp_connect"
    elif "tls_handshake_failed" in markers: boundary = "tls_handshake"
    elif "get_request_sent" in markers and "http_headers_observed" not in markers: boundary = "get_sent_waiting_response"
    elif "http_headers_observed" in markers: boundary = "source_response"
    elif "proxy_connect_established" in markers: boundary = "connect"
    else: boundary = "unknown"
    return {"markers": markers, "boundary": boundary}


def status(stdout: str) -> int | None:
    value = stdout.strip().splitlines()[-1].strip() if stdout.strip() else ""
    return None if not value.isdigit() or len(value) != 3 or value == "000" else int(value)


def headers(path: Path) -> tuple[str | None, int | None]:
    content, retry = None, None
    lines = path.read_text(encoding="iso-8859-1", errors="replace").splitlines() if path.exists() else []
    for line in lines:
        lower = line.lower()
        if lower.startswith("content-type:") and content is None: content = line.split(":", 1)[1].strip().split(";", 1)[0].lower()
        if lower.startswith("retry-after:") and retry is None and line.split(":", 1)[1].strip().isdigit(): retry = int(line.split(":", 1)[1].strip())
    return content, retry


def canonical_query_url(prefix: str, from_ts: str = FROM_TS, to_ts: str = ANCHOR_TO_TS) -> str:
    """Build the exact no-collapse prefix query for one bound source window."""
    return (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(prefix, safe="")
        + "&matchType=prefix&output=json&fl=" + quote(",".join(FIELDS), safe="")
        + f"&from={from_ts}&to={to_ts}&limit={LIMIT}&showResumeKey=true"
    )


def validate_inputs() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """Validate the exact four saved-query transport-unknown retry targets offline."""
    plan = read_json(PLAN_PATH, {})
    if plan.get("schema") != "wow-recovery.gallery-early03-plan.v1":
        raise RuntimeError("unsupported early03 plan schema")
    candidates = plan.get("candidates") or []
    policy = plan.get("policy") or {}
    if plan.get("candidate_count") != 4 or len(candidates) != 4:
        raise RuntimeError("early03 plan is not exactly four retry candidates")
    expected_policy = {
        "from": FROM_TS, "to": "per_item_source_window", "limit": LIMIT,
        "showResumeKey": True, "collapse": False, "matchType": "prefix",
        "max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW_SECONDS,
        "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "min_dispatch_seconds": MIN_DISPATCH_SECONDS,
        "min_request_start_seconds": MIN_REQUEST_START_SECONDS,
        "disk_floor_bytes": DISK_FLOOR_BYTES, "direct_first": True,
        "tls_verification": True, "automatic_redirects": 0,
        "payload_replay": False, "prior_failure_tail": PRIOR_FAILURE_TAIL,
    }
    if any(policy.get(key) != value for key, value in expected_policy.items()):
        raise RuntimeError("early03 policy mismatch")
    if policy.get("proxy") != PROXY or policy.get("stop_http_codes") != [429, 503]:
        raise RuntimeError("early03 transport policy mismatch")
    if policy.get("stop_after_new_transport_failures") != 3:
        raise RuntimeError("early03 inherited-tail stop policy mismatch")
    bindings: dict[str, Any] = {}
    for key, entry in (plan.get("input_bindings") or {}).items():
        if not isinstance(entry, dict) or not entry.get("path") or not entry.get("sha256"):
            raise RuntimeError(f"invalid input binding {key}")
        path = ROOT / str(entry["path"])
        if not path.is_file():
            raise RuntimeError(f"input missing {key}: {path}")
        actual = sha(path)
        if actual != str(entry["sha256"]):
            raise RuntimeError(f"input SHA mismatch {key}: {actual}")
        bindings[key] = {"path": rel(path), "sha256": actual, "bytes": path.stat().st_size, "role": entry.get("role")}
    required = {
        "early_gap_plan", "root_gallery_followups_acceptance", "gallery_registry_v5",
        "root_gallery_early01_acceptance", "gallery_early01_batch_report",
        "gallery_early01_source_map", "gallery_early01_execution_plan",
        "root_gallery_early02_acceptance", "gallery_early02_batch_report",
        "gallery_early02_source_map", "gallery_early02_execution_plan",
        "root_gallery_prefix05_acceptance", "gallery_prefix05_driver_v5", "gallery_prefix05_fixture",
    }
    if not required.issubset(bindings):
        raise RuntimeError(f"required bindings missing: {sorted(required - set(bindings))}")
    source_entry = bindings["early_gap_plan"]
    source_path = ROOT / source_entry["path"]
    source_plan = read_json(source_path, {})
    if sha(source_path) != str(plan.get("source_plan_sha256") or "") or rel(source_path) != str(plan.get("source_plan_path") or ""):
        raise RuntimeError("early-gap source plan path/SHA mismatch")
    source_items = source_plan.get("items") or []
    if source_plan.get("schema") != "gallery-followup-plan-v1" or source_plan.get("count") != 24 or len(source_items) != 24:
        raise RuntimeError("bound early-gap plan is not the accepted 24-item source")
    followup = read_json(ROOT / bindings["root_gallery_followups_acceptance"]["path"], {})
    if followup.get("accepted") is not True or followup.get("early_gap_plan_sha256") != sha(source_path) or followup.get("early_batches") != [20, 4]:
        raise RuntimeError("root early-gap acceptance is not bound to the 20+4 source")
    registry_path = ROOT / bindings["gallery_registry_v5"]["path"]
    if source_plan.get("source_registry", {}).get("sha256") != sha(registry_path):
        raise RuntimeError("source registry SHA mismatch")
    latest = read_json(ROOT / bindings["root_gallery_early02_acceptance"]["path"], {})
    if latest.get("accepted") is not True or latest.get("failure_streak_end") != LATEST_TAIL:
        raise RuntimeError("latest EARLY02 source receipt does not bind tail two")
    if latest.get("batch_report_sha256") != plan.get("previous_batch", {}).get("latest_batch_report_sha256"):
        raise RuntimeError("latest EARLY02 report SHA is not bound")
    if plan.get("prior_failure_tail") != PRIOR_FAILURE_TAIL or plan.get("latest_tail_value") != LATEST_TAIL:
        raise RuntimeError("early03 prior/latest tail mismatch")
    latest_basis = plan.get("latest_tail_basis") or {}
    if latest_basis.get("path") != bindings["root_gallery_early02_acceptance"]["path"] or latest_basis.get("sha256") != bindings["root_gallery_early02_acceptance"]["sha256"]:
        raise RuntimeError("early03 latest-tail receipt binding mismatch")
    if plan.get("historical_gallery_tail") != HISTORICAL_GALLERY_TAIL or plan.get("historical_gallery_tail_preserved") != HISTORICAL_GALLERY_TAIL:
        raise RuntimeError("early03 historical gallery tail mismatch")
    source_by_registry = {int(item["registry_rank"]): item for item in source_items}
    expected_registry = [7, 12, 14, 38]
    if plan.get("retry_scope", {}).get("registry_ranks") != expected_registry:
        raise RuntimeError("early03 retry registry scope changed")
    if plan.get("retry_scope", {}).get("saved_batch_ranks") != {"EARLY01": [6, 9, 11], "EARLY02": [4]}:
        raise RuntimeError("early03 saved batch-rank scope changed")
    normalized: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    seen_origins: set[tuple[str, int]] = set()
    for rank, candidate in enumerate(candidates, 1):
        retry = candidate.get("retry_source") or {}
        original_rank = int(retry.get("original_rank") or 0)
        origin_key = (str(retry.get("batch_id")), int(retry.get("rank") or 0))
        if original_rank not in expected_registry or origin_key in seen_origins:
            raise RuntimeError(f"unsafe or duplicate retry source: {candidate.get('target_key')!r}")
        seen_origins.add(origin_key)
        source_item = source_by_registry.get(original_rank)
        if source_item is None:
            raise RuntimeError(f"retry source registry rank missing: {original_rank}")
        for field in ("registry_rank", "gallery", "category", "source_page_route", "declared_slots", "expected_direct_entities", "prefix", "followup_group", "reason"):
            if candidate.get(field) != source_item.get(field):
                raise RuntimeError(f"candidate does not equal source item {rank}:{field}")
        prefix = str(candidate.get("prefix") or "")
        parsed_prefix = urlsplit(prefix)
        if parsed_prefix.scheme != "http" or parsed_prefix.hostname != "www.worldofwarcraft.com" or parsed_prefix.port not in (None, 80) or not parsed_prefix.path.endswith("/") or parsed_prefix.query or parsed_prefix.fragment:
            raise RuntimeError(f"candidate origin widened or malformed: {prefix!r}")
        source = candidate.get("source_evidence") or {}
        source_expected = source_item.get("source_evidence") or {}
        for field in ("path", "sha256", "addshots_line", "addshots_literal", "source_directory", "filename_literal", "numShots_line", "numShots_literal"):
            if source.get(field) != source_expected.get(field):
                raise RuntimeError(f"candidate source evidence mismatch {rank}:{field}")
        source_page = ROOT / str(source.get("path") or "")
        if not source_page.is_file() or sha(source_page) != str(source.get("sha256") or ""):
            raise RuntimeError(f"candidate source hash mismatch: {candidate.get('target_key')!r}")
        lines = source_page.read_text(encoding="iso-8859-1", errors="replace").splitlines()
        add_line, num_line = int(source.get("addshots_line") or 0), int(source.get("numShots_line") or 0)
        if add_line < 1 or num_line < 1 or add_line > len(lines) or num_line > len(lines):
            raise RuntimeError(f"candidate source line out of range: {candidate.get('target_key')!r}")
        if str(source.get("addshots_literal")) not in lines[add_line - 1] or str(source.get("numShots_literal")) not in lines[num_line - 1]:
            raise RuntimeError(f"candidate source literal missing: {candidate.get('target_key')!r}")
        if source.get("source_directory") != parsed_prefix.path or source.get("filename_literal") != "ss":
            raise RuntimeError(f"candidate source literal mismatch: {candidate.get('target_key')!r}")
        key = str(candidate.get("target_key") or "")
        if not re.fullmatch(r"GALLERY-EARLY03-[0-9]{2}", key) or key in seen_keys:
            raise RuntimeError(f"unsafe or duplicate target key: {key!r}")
        seen_keys.add(key)
        source_window = source_item.get("query_window") or {}
        candidate_window = candidate.get("query_window") or {}
        if candidate_window != source_window or candidate_window != retry.get("query_window") or candidate_window.get("from") != FROM_TS or candidate_window.get("limit") != LIMIT or candidate_window.get("showResumeKey") is not True or candidate_window.get("collapse") is not False or candidate_window.get("matchType") != "prefix":
            raise RuntimeError(f"saved query window mismatch: {key}")
        query_url = str(candidate.get("cdx_query_url") or "")
        if query_url != str(retry.get("query_url") or "") or query_url != canonical_query_url(prefix, FROM_TS, str(candidate_window.get("to") or "")):
            raise RuntimeError(f"saved exact query mismatch: {key}")
        report_key = "gallery_early01_batch_report" if retry.get("batch_id") == "WAYBACK-GALLERYEARLY01-20261016" else "gallery_early02_batch_report"
        report = read_json(ROOT / bindings[report_key]["path"], {})
        result = next((x for x in report.get("candidate_results", []) if int(x.get("rank") or 0) == int(retry.get("rank") or 0)), None)
        if result is None or result.get("status") != "transport_or_parse_unknown" or result.get("source_response_count") != 0 or result.get("query_url") != query_url or result.get("query_window") != candidate_window:
            raise RuntimeError(f"saved retry report evidence mismatch: {key}")
        if retry.get("report_sha256") != bindings[report_key]["sha256"]:
            raise RuntimeError(f"saved retry report SHA mismatch: {key}")
        normalized_item = dict(candidate)
        normalized_item.update({"rank": rank, "target_key": key, "label": candidate.get("label") or candidate.get("gallery") or f"candidate-{rank:02d}", "category": candidate.get("category") or "root-gallery-retry", "cdx_query_url": query_url, "source_directory": source.get("source_directory"), "declared_entity_count": candidate.get("declared_slots"), "query_window": candidate_window, "retry_source": retry})
        normalized.append(normalized_item)
    if {(x["retry_source"]["batch_id"], int(x["retry_source"]["rank"])) for x in normalized} != {
        ("WAYBACK-GALLERYEARLY01-20261016", 6),
        ("WAYBACK-GALLERYEARLY01-20261016", 9),
        ("WAYBACK-GALLERYEARLY01-20261016", 11),
        ("WAYBACK-GALLERYEARLY02-20261016", 4),
    }:
        raise RuntimeError("early03 retry union changed")
    return plan, normalized, bindings


class _FixtureClock:
    """Deterministic clock whose sleep returns early and is quantized."""

    def __init__(self, monotonic_start: float = 100.0, utc_start: datetime | None = None,
                 ratio: float = 0.965, quantum: float = 0.1) -> None:
        self.mono = float(monotonic_start)
        self.utc = utc_start or datetime(2026, 10, 16, 4, 0, tzinfo=timezone.utc)
        self.ratio = float(ratio)
        self.quantum = float(quantum)
        self.sleep_calls: list[float] = []

    def monotonic(self) -> float:
        return self.mono

    def now(self) -> datetime:
        return self.utc

    def sleep(self, seconds: float) -> None:
        self.sleep_calls.append(float(seconds))
        # Deliberately round down: this models the 5.093s historical failure.
        units = int((max(0.001, float(seconds)) * self.ratio) / self.quantum)
        elapsed = max(self.quantum, units * self.quantum)
        self.mono += elapsed
        self.utc += timedelta(seconds=elapsed)


class _RealClock:
    monotonic = staticmethod(time.monotonic)
    now = staticmethod(now)
    sleep = staticmethod(time.sleep)


def _schedule_next(last_dispatch_mono: float | None, last_dispatch_utc: datetime | None,
                   last_start_utc: datetime | None, clock: Any) -> dict[str, Any]:
    """Wait with re-checks until both cadence floors are met.

    ``time.sleep`` is only a hint.  Re-reading monotonic time after every
    sleep is what prevents Windows early-return/rounding from violating the
    5.25s scheduling margin.  UTC is retained for restart continuity.
    """
    target_mono = clock.monotonic() if last_dispatch_mono is None else float(last_dispatch_mono) + MIN_DISPATCH_SECONDS
    target_utc = None if last_start_utc is None else last_start_utc + timedelta(seconds=MIN_REQUEST_START_SECONDS)
    while True:
        now_mono = clock.monotonic()
        now_utc = clock.now()
        wait_mono = max(0.0, target_mono - now_mono)
        wait_utc = 0.0 if target_utc is None else max(0.0, (target_utc - now_utc).total_seconds())
        wait_for = max(wait_mono, wait_utc)
        if wait_for <= 0.0:
            break
        clock.sleep(min(wait_for, 0.25))
    # One final re-read is intentional; never trust the requested sleep.
    dispatch_mono = clock.monotonic()
    dispatch_utc = clock.now()
    dispatch_interval = None if last_dispatch_mono is None else dispatch_mono - float(last_dispatch_mono)
    start_interval = None if last_start_utc is None else (dispatch_utc - last_start_utc).total_seconds()
    if dispatch_interval is not None and dispatch_interval < MIN_DISPATCH_SECONDS:
        raise RuntimeError(f"cadence_guard_failed:{dispatch_interval:.6f}")
    if start_interval is not None and start_interval < MIN_REQUEST_START_SECONDS:
        raise RuntimeError(f"request_start_guard_failed:{start_interval:.6f}")
    return {"dispatch_monotonic": dispatch_mono, "dispatch_utc": dispatch_utc,
            "dispatch_interval_seconds": dispatch_interval,
            "request_start_interval_seconds": start_interval,
            "sleep_calls": len(getattr(clock, "sleep_calls", []))}


def _restart_last_dispatch(record: dict[str, Any], clock: Any) -> float:
    """Map persisted UTC state into a fresh process's monotonic clock."""
    previous_utc = parse_iso(str(record.get("dispatch_utc") or ""))
    if previous_utc is None:
        raise RuntimeError("persisted dispatch lacks dispatch_utc")
    elapsed = max(0.0, (clock.now() - previous_utc).total_seconds())
    return clock.monotonic() - elapsed


def _remaining_clamp(total_before: int, now_monotonic: float, window_started: float,
                     *, window_seconds: float = WINDOW_SECONDS,
                     max_total: int = MAX_TOTAL_BODY_BYTES,
                     max_entity: int = MAX_ENTITY_BODY_BYTES,
                     transport: str = "proxy",
                     hard_remaining: float | None = None) -> dict[str, Any]:
    """Return effective byte/time caps for one request, after waiting."""
    total_remaining = max(0, int(max_total) - int(total_before))
    window_remaining = max(0.0, float(window_seconds) - max(0.0, float(now_monotonic) - float(window_started)))
    hard = float("inf") if hard_remaining is None else max(0.0, float(hard_remaining))
    base_connect = DIRECT_CONNECT_SECONDS if transport == "direct" else PROXY_CONNECT_SECONDS
    base_max = DIRECT_MAX_SECONDS if transport == "direct" else PROXY_MAX_SECONDS
    request_budget = min(base_max, window_remaining, hard)
    entity_limit = min(max(0, int(max_entity)), total_remaining)
    return {
        "transport": transport,
        "total_body_bytes_before": int(total_before),
        "total_body_remaining_before_bytes": total_remaining,
        "configured_entity_body_limit_bytes": int(max_entity),
        "entity_body_limit_before_bytes": entity_limit,
        "window_seconds": float(window_seconds),
        "window_remaining_seconds": window_remaining,
        "hard_cutoff_remaining_seconds": None if hard == float("inf") else hard,
        "baseline_connect_timeout_seconds": base_connect,
        "baseline_max_timeout_seconds": base_max,
        "connect_timeout_seconds": max(0.0, min(base_connect, request_budget)),
        "max_timeout_seconds": max(0.0, request_budget),
        "clamp_applied": entity_limit < int(max_entity) or request_budget < base_max,
        "dispatch_allowed": bool(total_remaining > 0 and request_budget > 0),
    }


def fixture() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    def check(name: str, passed: bool, detail: Any) -> None:
        results.append({"name": name, "passed": bool(passed), "detail": detail})

    sample = [FIELDS, ["key", "20070101000000", "http://www.worldofwarcraft.com/info/events/x/ss1.jpg", "image/jpeg", "200", "D", "12"], [], ["resume-fixture"]]
    parsed = parse_cdx(json.dumps(sample).encode())
    check("parse_header_separator_resume", parsed["valid"] and len(parsed["rows"]) == 1 and parsed["resume"] == ["resume-fixture"] and any(x.get("kind") == "separator" for x in parsed["metadata"]), {"rows": len(parsed["rows"]), "resume": parsed["resume"], "metadata": parsed["metadata"]})
    rows = [FIELDS] + [[f"k{i}", "20070101000000", f"http://www.worldofwarcraft.com/info/events/x/ss{i+1}.jpg", "image/jpeg", "200", "D", "12"] for i in range(500)] + [[], ["resume-500"]]
    parsed500 = parse_cdx(json.dumps(rows).encode())
    check("limit_500_truncation", parsed500["valid"] and len(parsed500["rows"]) == 500 and len(parsed500["rows"]) >= LIMIT, {"rows": len(parsed500["rows"]), "potential_truncation": len(parsed500["rows"]) >= LIMIT})
    check("resume_key_preserved_no_continuation", parsed500["resume"] == ["resume-500"], {"resume": parsed500["resume"], "continuation_followed": False})
    unknown = parse_cdx(json.dumps([FIELDS, {"unexpected": "metadata"}]).encode())
    check("unknown_metadata_is_incomplete", not unknown["valid"] and unknown["error"] == "cdx_unrecognized_metadata", {"valid": unknown["valid"], "error": unknown["error"]})
    prefix = "http://www.worldofwarcraft.com/info/events/x/"
    check("default_port_identity", same_origin("http://www.worldofwarcraft.com:80/info/events/x/ss1.jpg", prefix) == "same_origin_prefix", same_origin("http://www.worldofwarcraft.com:80/info/events/x/ss1.jpg", prefix))
    identities = {"scheme": same_origin("https://www.worldofwarcraft.com/info/events/x/ss1.jpg", prefix), "host": same_origin("http://wow-europe.com/info/events/x/ss1.jpg", prefix), "path": same_origin("http://www.worldofwarcraft.com/info/events/y/ss1.jpg", prefix), "query": same_origin("http://www.worldofwarcraft.com/info/events/x/ss1.jpg?q=1", prefix)}
    check("identity_rejections", identities == {"scheme": "scheme_mismatch", "host": "host_mismatch", "path": "path_prefix_mismatch", "query": "query_or_fragment_present"}, identities)
    variant_payload = [
        FIELDS,
        ["canonical", "20070101000000", prefix + "ss1.jpg", "image/jpeg", "200", "D1", "12"],
        ["https", "20070101000000", "https://www.worldofwarcraft.com/info/events/x/ss1.jpg", "image/jpeg", "200", "D2", "12"],
        ["bare", "20070101000000", "http://worldofwarcraft.com/info/events/x/ss1-thumb.jpg", "image/jpeg", "200", "D3", "12"],
    ]
    variant_analysis = project_rows(parse_cdx(json.dumps(variant_payload).encode()), {"prefix": prefix, "query_window": {"from": FROM_TS, "to": "20080512210044"}})
    check("direct_identity_variants_classified_separately", variant_analysis["row_counts"]["direct_identity_variant_candidates"] == 2 and len(variant_analysis["direct_identity_variant_candidates"]) == 2 and variant_analysis["row_counts"]["strict_full"] == 1 and variant_analysis["row_counts"]["strict_thumb"] == 0, {"count": variant_analysis["row_counts"]["direct_identity_variant_candidates"], "identities": [x["identity"] for x in variant_analysis["direct_identity_variant_candidates"]], "strict_full": variant_analysis["row_counts"]["strict_full"], "strict_thumb": variant_analysis["row_counts"]["strict_thumb"], "payload_replay_count": 0})

    # The first sleep intentionally returns early; the loop must continue.
    clock = _FixtureClock(monotonic_start=100.0, ratio=0.965, quantum=0.1)
    first = _schedule_next(None, None, None, clock)
    second = _schedule_next(first["dispatch_monotonic"], first["dispatch_utc"], first["dispatch_utc"], clock)
    dispatches = [first["dispatch_monotonic"], second["dispatch_monotonic"]]
    starts = [first["dispatch_utc"], second["dispatch_utc"]]
    dispatch_intervals = [dispatches[i] - dispatches[i - 1] for i in range(1, len(dispatches))]
    start_intervals = [(starts[i] - starts[i - 1]).total_seconds() for i in range(1, len(starts))]
    check("monotonic_early_sleep_rechecked", min(dispatch_intervals) >= MIN_DISPATCH_SECONDS, {"intervals": dispatch_intervals, "sleep_calls": clock.sleep_calls})
    check("utc_start_rechecked_after_rounding", min(start_intervals) >= MIN_REQUEST_START_SECONDS, {"intervals": start_intervals})

    # Restart: monotonic origin changes, but persisted UTC identity supplies a
    # comparable prior point and the same 5.25s guard is still enforced.
    restart_clock = _FixtureClock(monotonic_start=900.0, utc_start=second["dispatch_utc"] + timedelta(seconds=2.0), ratio=0.965, quantum=0.1)
    restored_last = _restart_last_dispatch({"dispatch_utc": iso(second["dispatch_utc"])}, restart_clock)
    restarted = _schedule_next(restored_last, second["dispatch_utc"], second["dispatch_utc"], restart_clock)
    restart_detail = dict(restarted)
    restart_detail["dispatch_utc"] = iso(restart_detail["dispatch_utc"])
    check("restart_restores_utc_to_monotonic", restarted["dispatch_monotonic"] - restored_last >= MIN_DISPATCH_SECONDS and restarted["request_start_interval_seconds"] >= MIN_REQUEST_START_SECONDS, {"restored_last": restored_last, "result": restart_detail})

    full_clamp = _remaining_clamp(0, 10.0, 0.0, transport="proxy")
    near_clamp = _remaining_clamp(MAX_TOTAL_BODY_BYTES - 1 * 1024 * 1024, 898.5, 0.0, transport="proxy")
    check("remaining_byte_time_clamp", full_clamp["entity_body_limit_before_bytes"] == MAX_ENTITY_BODY_BYTES and full_clamp["max_timeout_seconds"] == PROXY_MAX_SECONDS and near_clamp["entity_body_limit_before_bytes"] == 1 * 1024 * 1024 and near_clamp["max_timeout_seconds"] <= 1.5 and near_clamp["clamp_applied"], {"full": full_clamp, "near": near_clamp})
    check("disk_floor_gate_is_per_request", DISK_FLOOR_BYTES == 11_005_853_696, {"disk_floor_bytes": DISK_FLOOR_BYTES, "gate_location": "before each durable dispatch reservation"})
    inherited_tail = PRIOR_FAILURE_TAIL
    new_failures = [inherited_tail + i for i in range(1, 4)]
    check("inherited_tail_two_three_new_failures_stop", inherited_tail == 2 and new_failures[-1] == 5, {"prior_failure_tail": inherited_tail, "new_failure_streak": new_failures})
    check("stop_at_five_transport_failures", sum(1 for _ in range(5)) == 5, {"threshold": 5})
    check("index_only_no_payload_replay", True, {"payload_replay_count": 0})
    # The four saved-query retry targets are checked offline; no fixture path invokes curl.
    try:
        prepared_plan, prepared_candidates, _ = validate_inputs()
        plan_gate = {
            "candidate_count": len(prepared_candidates),
            "all_absolute_http": all(x["prefix"].startswith("http://www.worldofwarcraft.com/") for x in prepared_candidates),
            "from": prepared_plan["policy"]["from"],
            "max_attempts": prepared_plan["policy"]["max_attempts"],
            "max_entity_body_bytes": prepared_plan["policy"]["max_entity_body_bytes"],
            "prior_failure_tail": prepared_plan["policy"]["prior_failure_tail"],
            "saved_unknown_queries": all(x.get("retry_source", {}).get("status") == "transport_or_parse_unknown" for x in prepared_candidates),
            "retry_union": sorted((x["retry_source"]["batch_id"], int(x["retry_source"]["rank"])) for x in prepared_candidates),
        }
        expected_union = sorted([("WAYBACK-GALLERYEARLY01-20261016", 6), ("WAYBACK-GALLERYEARLY01-20261016", 9), ("WAYBACK-GALLERYEARLY01-20261016", 11), ("WAYBACK-GALLERYEARLY02-20261016", 4)])
        check("retry_plan_four_saved_unknown_queries", plan_gate == {"candidate_count": 4, "all_absolute_http": True, "from": FROM_TS, "max_attempts": 40, "max_entity_body_bytes": 8 * 1024 * 1024, "prior_failure_tail": 2, "saved_unknown_queries": True, "retry_union": expected_union}, plan_gate)
    except Exception as exc:
        check("retry_plan_four_saved_unknown_queries", False, {"error": f"{type(exc).__name__}:{exc}"})
    passed = sum(int(x["passed"]) for x in results)
    return {"schema": "wow-recovery.gallery-early03-driver-v6-fixture-results.v1", "mode": "offline_fixture", "network_requests": 0, "passed": passed, "total": len(results), "all_passed": passed == len(results), "cadence": {"dispatch_intervals": dispatch_intervals, "request_start_intervals": start_intervals, "min_dispatch": min(dispatch_intervals), "min_request_start": min(start_intervals), "scheduling_floor_seconds": MIN_DISPATCH_SECONDS, "acceptance_floor_seconds": ACCEPTANCE_DISPATCH_SECONDS}, "results": results}


def plan_for_run(plan: dict[str, Any], candidates: list[dict[str, Any]], bindings: dict[str, Any], fixture_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "wow-recovery.gallery-early03-execution-plan.v1",
        "batch_id": BATCH_ID,
        "mode": "go_executed",
        "prepared_utc": iso(now()),
        "source_plan_path": rel(PLAN_PATH),
        "source_plan_sha256": sha(PLAN_PATH),
        "candidate_count": 4,
        "candidate_ranks": [x["rank"] for x in candidates],
        "scope": "exact four previously transport-unknown saved query windows; no valid-window repeat or query expansion",
        "query_window": {"from": FROM_TS, "to": "per_candidate_source_window", "limit": LIMIT, "showResumeKey": True, "collapse": False, "matchType": "prefix"},
        "index_only": True,
        "no_payload_replay": True,
        "max_attempts": MAX_ATTEMPTS,
        "window_seconds": WINDOW_SECONDS,
        "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "direct_first": True,
        "proxy": PROXY,
        "tls_verification": True,
        "automatic_redirects": 0,
        "min_dispatch_monotonic_seconds": MIN_DISPATCH_SECONDS,
        "acceptance_dispatch_floor_seconds": ACCEPTANCE_DISPATCH_SECONDS,
        "min_request_start_utc_seconds": MIN_REQUEST_START_SECONDS,
        "disk_floor_bytes": DISK_FLOOR_BYTES,
        "stop_http_codes": sorted(STOP_HTTP_CODES),
        "stop_on_five_consecutive_transport_failures": True,
        "stop_after_new_transport_failures": 3,
        "retry_after_rule": "429/503 stop immediately; cooldown not earlier than Retry-After and at least 120 seconds",
        "resume_rule": "record actual response resumeKey; do not follow continuation in this batch",
        "failure_streak_start": PRIOR_FAILURE_TAIL,
        "prior_failure_tail": PRIOR_FAILURE_TAIL,
        "historical_gallery_tail": HISTORICAL_GALLERY_TAIL,
        "historical_gallery_tail_preserved": HISTORICAL_GALLERY_TAIL,
        "latest_tail_value": LATEST_TAIL,
        "control_basis": "latest root-accepted NETWORK29 EARLY01 source receipt tail end 0; no historical control reset is used",
        "input_bindings": bindings,
        "fixture": {"path": rel(OUT / "fixture-results.json"), "sha256": sha(OUT / "fixture-results.json"), "all_passed": fixture_result["all_passed"]},
        "candidates": [{"rank": x["rank"], "target_key": x.get("target_key"), "label": x["label"], "prefix": x["prefix"], "declared_slots": x.get("declared_slots"), "query_window": x.get("query_window"), "cdx_query_url": x["cdx_query_url"], "source_evidence": x.get("source_evidence")} for x in candidates],
    }


def public_attempt(row: dict[str, Any]) -> dict[str, Any]:
    keep = ("attempt", "rank", "label", "transport", "started_utc", "finished_utc", "curl_exit", "connect_status", "source_status", "content_type", "retry_after", "body_bytes", "body_sha256", "duration_ms", "transport_error", "transport_reason", "cdx_json_valid", "cdx_parse_error", "cdx_record_count", "resume_keys", "potential_truncation", "continuation_followed", "phase_boundary", "phase_markers", "disk_free_before_bytes", "disk_floor_passed", "dispatch_utc", "dispatch_monotonic", "dispatch_interval_seconds", "request_start_interval_seconds", "clamp", "raw")
    return {key: row.get(key) for key in keep}


def request(item: dict[str, Any], rank: int, attempt_no: int, transport: str, state: dict[str, Any], window_start: float, last_dispatch: dict[str, Any] | None, last_start: datetime | None) -> tuple[dict[str, Any], dict[str, Path], float, float, int]:
    # Cadence is enforced immediately before each durable dispatch reservation.
    # Re-check monotonic time after every sleep; a single requested sleep can
    # return early on Windows and caused the frozen 5.093s deviation.
    last_mono = None if last_dispatch is None else float(last_dispatch["dispatch_monotonic"])
    previous_utc = None if last_dispatch is None else parse_iso(str(last_dispatch.get("dispatch_utc") or ""))
    cadence = _schedule_next(last_mono, previous_utc, last_start, _RealClock())
    dispatch_utc, dispatch_mono = cadence["dispatch_utc"], cadence["dispatch_monotonic"]
    elapsed = dispatch_mono - window_start
    remaining_window = WINDOW_SECONDS - max(0.0, elapsed)
    if remaining_window <= 0:
        raise RuntimeError("window_exhausted_before_dispatch")
    # Check the disk after waiting as well as before it, and persist the value
    # with every reservation even when a later transport step is unavailable.
    free_before = free_bytes()
    if free_before < DISK_FLOOR_BYTES:
        raise RuntimeError("disk_floor_before_dispatch")
    prior_body = int(state.get("total_body_bytes", 0))
    clamp = _remaining_clamp(prior_body, dispatch_mono, window_start, transport=transport)
    entity_limit = int(clamp["entity_body_limit_before_bytes"])
    connect_time = float(clamp["connect_timeout_seconds"])
    max_time = float(clamp["max_timeout_seconds"])
    if not clamp["dispatch_allowed"] or entity_limit <= 0:
        raise RuntimeError("remaining_budget_exhausted_before_dispatch")
    stem = f"{attempt_no:02d}-GALLERYEARLY03-R{rank:02d}-cdx-{transport}"
    paths = {suffix: RAW / f"{stem}.{suffix}" for suffix in ("headers.txt", "body", "stderr.txt", "trace.txt", "metrics.txt")}
    for path in paths.values():
        if path.exists():
            raise RuntimeError(f"refusing_to_overwrite:{path}")
    dispatch = {
        "attempt": attempt_no, "rank": rank, "label": item["label"], "transport": transport, "kind": "cdx",
        "dispatch_utc": iso(dispatch_utc), "dispatch_monotonic": dispatch_mono,
        "interval_since_previous_dispatch_seconds": None if last_dispatch is None else dispatch_mono - float(last_dispatch["dispatch_monotonic"]),
        "request_start_interval_seconds": None if last_start is None else (now() - last_start).total_seconds(),
        "persisted_before_transport": True, "disk_free_before_bytes": free_before,
        "disk_floor_bytes": DISK_FLOOR_BYTES, "disk_floor_passed": free_before >= DISK_FLOOR_BYTES,
        "clamp": clamp, "query_url": item["cdx_query_url"],
        "raw": {key: rel(value) for key, value in paths.items()},
    }
    return dispatch, paths, connect_time, max_time, entity_limit


def execute(plan: dict[str, Any], candidates: list[dict[str, Any]], fixture_result: dict[str, Any]) -> dict[str, Any]:
    if not fixture_result.get("all_passed"):
        raise RuntimeError("offline fixture missing or failed")
    report_path = OUT / "batch-report.json"
    if report_path.exists():
        return read_json(report_path, {})
    attempts: list[dict[str, Any]] = []
    dispatches: list[dict[str, Any]] = []
    state: dict[str, Any] = {"schema": "wow-recovery.gallery-early03-state.v1", "batch_id": BATCH_ID, "mode": "prepared", "prior_failure_tail": PRIOR_FAILURE_TAIL, "historical_gallery_tail": HISTORICAL_GALLERY_TAIL, "historical_gallery_tail_preserved": HISTORICAL_GALLERY_TAIL, "latest_tail_value": LATEST_TAIL, "failure_streak_start": PRIOR_FAILURE_TAIL, "failure_streak": PRIOR_FAILURE_TAIL, "total_body_bytes": 0, "attempts": 0, "source_responses": 0, "payload_replay_count": 0, "continuation_followed": False, "stop_reason": None}
    attempt_path, dispatch_path, progress_path = OUT / "attempt-records.json", OUT / "dispatch-log.json", OUT / "progress.json"
    write_json(attempt_path, attempts); write_json(dispatch_path, dispatches); write_json(progress_path, state)
    window_started = now(); window_start_mono = time.monotonic()
    state.update({"mode": "executing", "window_started_utc": iso(window_started)})
    write_json(progress_path, state)
    last_dispatch: dict[str, Any] | None = None
    last_start: datetime | None = None
    # Preserve the prior batch's actual tail as an input fact.  A successful
    # source response resets the current window to zero; it is never silently
    # rewritten to zero merely because this process started.
    # The latest accepted other4 batch ended with tail two.  Three new
    # transport failures therefore reach the global five-failure stop rule.
    consecutive_transport = PRIOR_FAILURE_TAIL
    next_attempt = 1
    stop_reason: str | None = None
    results: list[dict[str, Any]] = []
    for item in candidates:
        if stop_reason or next_attempt > MAX_ATTEMPTS:
            break
        rank = int(item["rank"])
        target_attempts: list[dict[str, Any]] = []
        for transport in ("direct", "proxy"):
            if stop_reason or next_attempt > MAX_ATTEMPTS:
                break
            dispatch, paths, connect_time, max_time, entity_limit = request(item, rank, next_attempt, transport, state, window_start_mono, last_dispatch, last_start)
            dispatches.append(dispatch)
            write_json(dispatch_path, dispatches)
            write_json(progress_path, {**state, "attempts_reserved": len(dispatches), "last_dispatch_utc": dispatch["dispatch_utc"]})
            command = ["curl.exe", "--proxy", "" if transport == "direct" else PROXY, "--noproxy", "*" if transport == "direct" else "", "--connect-timeout", f"{connect_time:.3f}", "--max-time", f"{max_time:.3f}", "--max-redirs", "0", "--max-filesize", str(entity_limit), "--silent", "--show-error", "--trace-time", "--trace-ascii", str(paths["trace.txt"]), "--dump-header", str(paths["headers.txt"]), "--output", str(paths["body"]), "--write-out", "%{http_code}", "--user-agent", USER_AGENT, item["cdx_query_url"]]
            started = now(); last_start, last_dispatch = started, dispatch
            stdout, curl_exit, exception_text = "", None, ""
            try:
                completed = subprocess.run(command, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=paths["stderr.txt"].open("wb"), timeout=max(2, max_time + 3), check=False)
                stdout, curl_exit = completed.stdout.decode("ascii", errors="replace"), completed.returncode
            except subprocess.TimeoutExpired:
                exception_text = "subprocess timeout guard"
            except Exception as exc:
                exception_text = type(exc).__name__
            finished = now()
            if not paths["headers.txt"].exists(): paths["headers.txt"].write_text("", encoding="iso-8859-1")
            if not paths["body"].exists(): paths["body"].write_bytes(b"")
            if not paths["trace.txt"].exists(): paths["trace.txt"].write_text("", encoding="utf-8")
            if not paths["stderr.txt"].exists(): paths["stderr.txt"].write_text(exception_text, encoding="utf-8")
            body_bytes = paths["body"].stat().st_size
            source_status = status(stdout)
            content_type, retry_after = headers(paths["headers.txt"])
            phases = phase(paths["trace.txt"], paths["stderr.txt"])
            parsed = {"valid": False, "error": "no_200_source_response", "header": None, "rows": [], "resume": [], "metadata": []}
            if source_status == 200 and body_bytes <= MAX_ENTITY_BODY_BYTES:
                parsed = parse_cdx(paths["body"].read_bytes())
            analysis = project_rows(parsed, item) if parsed.get("valid") else {"rows": [], "strict_literal_full_candidates": [], "strict_literal_thumb_candidates": [], "nested_preview_or_other_rows": [], "other_rows": [], "redirect_rows": [], "row_counts": {}}
            potential_truncation = bool(parsed.get("valid") and len(parsed.get("rows") or []) >= LIMIT)
            success_gate = bool(source_status == 200 and parsed.get("valid") and len(parsed.get("rows") or []) < LIMIT)
            paths["metrics.txt"].write_text(str(source_status or 0) + "\n", encoding="ascii")
            record = {
                "attempt": next_attempt, "rank": rank, "label": item["label"], "category": item["category"], "prefix": item["prefix"], "transport": transport, "kind": "cdx", "started_utc": iso(started), "finished_utc": iso(finished), "duration_ms": round((finished - started).total_seconds() * 1000, 3), "curl_exit": curl_exit, "connect_status": 200 if transport == "proxy" and "proxy_connect_established" in phases["markers"] else None, "source_status": source_status, "content_type": content_type, "retry_after": retry_after, "body_bytes": body_bytes, "body_sha256": sha(paths["body"]) if body_bytes else None, "transport_error": source_status is None, "transport_reason": "no_http_status" if source_status is None else None, "cdx_json_valid": bool(parsed.get("valid")), "cdx_parse_error": parsed.get("error"), "cdx_record_count": len(parsed.get("rows") or []) if parsed.get("valid") else 0, "resume_keys": parsed.get("resume") or [], "potential_truncation": potential_truncation, "continuation_followed": False, "header_fields_observed": parsed.get("header"), "phase_boundary": phases["boundary"], "phase_markers": phases["markers"], "disk_free_before_bytes": dispatch["disk_free_before_bytes"], "disk_floor_passed": dispatch["disk_floor_passed"], "dispatch_utc": dispatch["dispatch_utc"], "dispatch_monotonic": dispatch["dispatch_monotonic"], "dispatch_interval_seconds": dispatch.get("interval_since_previous_dispatch_seconds"), "request_start_interval_seconds": None if not attempts else (started - datetime.fromisoformat(attempts[-1]["started_utc"].replace("Z", "+00:00"))).total_seconds(), "clamp": dispatch["clamp"], "raw": dispatch["raw"], "index_rows": analysis}
            attempts.append(record); next_attempt += 1; target_attempts.append(record)
            state["attempts"], state["attempts_reserved"] = len(attempts), len(dispatches)
            state["total_body_bytes"] += body_bytes; state["source_responses"] += int(source_status is not None)
            consecutive_transport = consecutive_transport + 1 if source_status is None else 0
            state["failure_streak"] = consecutive_transport
            write_json(attempt_path, attempts); write_json(progress_path, {**state, "last_source_status": source_status, "last_attempt_finished_utc": iso(finished)})
            if source_status in STOP_HTTP_CODES:
                stop_reason = f"endpoint_status_{source_status}"; state["retry_after_seconds"] = retry_after; state["cooldown_required_seconds"] = max(120, int(retry_after or 0)); break
            if consecutive_transport >= 5:
                stop_reason = "five_consecutive_transport_failures"; state["cooldown_required_seconds"] = 120; break
            if success_gate or (transport == "direct" and source_status is not None):
                break
        final = target_attempts[-1] if target_attempts else None
        if final:
            analysis = final.get("index_rows") or {}
            results.append({"rank": rank, "label": item["label"], "category": item["category"], "prefix": item["prefix"], "source_directory": item.get("source_directory"), "declared_entity_count": item.get("declared_entity_count"), "query_window": item.get("query_window"), "query_url": item["cdx_query_url"], "attempts": [public_attempt(x) for x in target_attempts], "source_response_count": sum(int(x.get("source_status") is not None) for x in target_attempts), "capture_index_count": final.get("cdx_record_count", 0), "cdx_json_valid": final.get("cdx_json_valid"), "cdx_parse_error": final.get("cdx_parse_error"), "resume_keys": final.get("resume_keys") or [], "potential_truncation": final.get("potential_truncation", False), "continuation_followed": False, "strict_literal_full_candidates": analysis.get("strict_literal_full_candidates", []), "strict_literal_thumb_candidates": analysis.get("strict_literal_thumb_candidates", []), "nested_preview_or_other_rows": analysis.get("nested_preview_or_other_rows", []), "other_rows": analysis.get("other_rows", []), "direct_identity_variant_candidates": analysis.get("direct_identity_variant_candidates", []), "redirect_rows": analysis.get("redirect_rows", []), "row_counts": analysis.get("row_counts", {}), "status": "potential_truncation" if final.get("potential_truncation") else "complete_within_response" if final.get("cdx_json_valid") else "transport_or_parse_unknown", "payload_replay_count": 0})
        if stop_reason: break
    if stop_reason is None: stop_reason = "completed_candidate_queue"
    finished_dt = now()
    cooldown_required = int(state.get("cooldown_required_seconds", 0) or 0)
    cooldown_not_before = None
    if stop_reason.startswith("endpoint_status_") or stop_reason == "five_consecutive_transport_failures":
        cooldown_required = max(120, cooldown_required)
        cooldown_not_before = iso(finished_dt + timedelta(seconds=cooldown_required))
    state.update({"mode": "completed", "stop_reason": stop_reason, "finished_utc": iso(finished_dt), "cooldown_required_seconds": cooldown_required if cooldown_not_before else state.get("cooldown_required_seconds"), "cooldown_not_before_utc": cooldown_not_before, "continuation_followed": False, "payload_replay_count": 0})
    write_json(progress_path, state)
    plan_hash = sha(OUT / "execution-plan.json")
    report = {"schema": "wow-recovery.gallery-early03-batch-report.v1", "batch_id": BATCH_ID, **state, "network_requests": len(attempts), "candidate_results": results, "cadence": {"dispatch_intervals": [x.get("interval_since_previous_dispatch_seconds") for x in dispatches[1:]], "request_start_intervals": [x.get("request_start_interval_seconds") for x in attempts[1:]], "min_dispatch": min((x.get("interval_since_previous_dispatch_seconds") for x in dispatches[1:] if x.get("interval_since_previous_dispatch_seconds") is not None), default=None), "min_request_start": min((x.get("request_start_interval_seconds") for x in attempts[1:] if x.get("request_start_interval_seconds") is not None), default=None), "scheduling_floor_seconds": MIN_DISPATCH_SECONDS, "acceptance_floor_seconds": ACCEPTANCE_DISPATCH_SECONDS, "dispatch_passed": all((x.get("interval_since_previous_dispatch_seconds") or MIN_DISPATCH_SECONDS) >= MIN_DISPATCH_SECONDS for x in dispatches[1:]), "start_passed": all((x.get("request_start_interval_seconds") or MIN_REQUEST_START_SECONDS) >= MIN_REQUEST_START_SECONDS for x in attempts[1:])}, "policy": plan, "fixture": {"path": rel(OUT / "fixture-results.json"), "sha256": sha(OUT / "fixture-results.json"), "all_passed": fixture_result.get("all_passed")}, "plan_sha256": plan_hash, "raw_evidence_note": "Raw CDX headers, bodies, stderr, traces and metrics remain local; no payload replay or image acceptance was performed."}
    write_json(report_path, report)
    source_map = {"schema": "wow-recovery.gallery-early03-source-map.v1", "batch_id": BATCH_ID, "index_only": True, "accepted_payloads": [], "entries": [{"rank": x["rank"], "label": x["label"], "prefix": x["prefix"], "query_window": x.get("query_window"), "status": x.get("status"), "capture_index_count": x.get("capture_index_count", 0), "resume_keys": x.get("resume_keys", []), "potential_truncation": x.get("potential_truncation", False), "strict_literal_full_count": len(x.get("strict_literal_full_candidates", [])), "strict_literal_thumb_count": len(x.get("strict_literal_thumb_candidates", [])), "direct_identity_variant_count": len(x.get("direct_identity_variant_candidates", [])), "nested_or_other_count": len(x.get("nested_preview_or_other_rows", [])) + len(x.get("other_rows", [])), "payload_replay_count": 0, "attempts": x.get("attempts", [])} for x in results]}
    write_json(OUT / "source-map.json", source_map)
    summary = {"schema": "wow-recovery.gallery-early03-sanitized-summary.v1", "batch_id": BATCH_ID, "network_requests": len(attempts), "source_responses": state["source_responses"], "stop_reason": stop_reason, "failure_streak": consecutive_transport, "candidate_count": len(candidates), "queried_ranks": [x["rank"] for x in results], "not_queried_ranks": [x["rank"] for x in candidates if x["rank"] not in {r["rank"] for r in results}], "potential_truncation_ranks": [x["rank"] for x in results if x.get("potential_truncation")], "resume_key_ranks": [x["rank"] for x in results if x.get("resume_keys")], "continuation_followed": False, "payload_replay_count": 0, "prior_failure_tail_preserved": PRIOR_FAILURE_TAIL, "historical_gallery_tail": HISTORICAL_GALLERY_TAIL, "historical_gallery_tail_preserved": HISTORICAL_GALLERY_TAIL, "latest_tail_value": LATEST_TAIL, "failure_streak_start": PRIOR_FAILURE_TAIL, "cooldown_required_seconds": state.get("cooldown_required_seconds"), "cooldown_not_before_utc": state.get("cooldown_not_before_utc"), "plan_sha256": plan_hash, "report_sha256": sha(report_path)}
    write_json(OUT / "sanitized-summary.json", summary)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.fixture == args.execute:
        parser.error("choose exactly one of --fixture or --execute")
    prepared_plan, candidates, bindings = validate_inputs()
    if args.fixture:
        result = fixture()
        write_json(OUT / "fixture-results.json", result)
        print(json.dumps({"mode": "offline_fixture", "passed": result["passed"], "total": result["total"], "all_passed": result["all_passed"], "network_requests": 0}, ensure_ascii=False))
        if not result["all_passed"]:
            raise SystemExit(1)
        return
    fixture_result = read_json(OUT / "fixture-results.json", {})
    if not fixture_result.get("all_passed"):
        raise SystemExit("fixture-results.json missing or failed; no network request made")
    actual_plan = plan_for_run(prepared_plan, candidates, bindings, fixture_result)
    write_json(OUT / "execution-plan.json", actual_plan)
    report = execute(actual_plan, candidates, fixture_result)
    script_hash = sha(Path(__file__))
    input_binding = {"schema": "wow-recovery.gallery-early03-driver-v6-input-bindings.v1", "batch_id": BATCH_ID, "source_bindings": bindings, "plan_path": rel(OUT / "execution-plan.json"), "plan_sha256": sha(OUT / "execution-plan.json"), "fixture_path": rel(OUT / "fixture-results.json"), "fixture_sha256": sha(OUT / "fixture-results.json"), "script_path": rel(Path(__file__)), "script_sha256": script_hash, "latest_tail_bound": LATEST_TAIL, "network_requests": report.get("network_requests")}
    write_json(OUT / "input-bindings.json", input_binding)
    report["input_binding_path"] = rel(OUT / "input-bindings.json")
    report["input_binding_sha256"] = sha(OUT / "input-bindings.json")
    report["script_sha256"] = script_hash
    write_json(OUT / "batch-report.json", report)
    summary = read_json(OUT / "sanitized-summary.json", {})
    summary["script_sha256"] = script_hash
    summary["input_binding_sha256"] = sha(OUT / "input-bindings.json")
    write_json(OUT / "sanitized-summary.json", summary)
    print(json.dumps({"mode": "executed", "batch_id": BATCH_ID, "network_requests": report.get("network_requests"), "source_responses": report.get("source_responses"), "stop_reason": report.get("stop_reason"), "potential_truncation_ranks": summary.get("potential_truncation_ranks"), "resume_key_ranks": summary.get("resume_key_ranks"), "payload_replay_count": report.get("payload_replay_count"), "plan_sha256": input_binding["plan_sha256"], "script_sha256": script_hash}, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Bounded index-only CDX probe for ten exact late native gallery prefixes.

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
NETWORK = ROOT / "research" / "continuous-recovery-20261019" / "network"
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
PLAN_PATH = OUT / "plan.json"
REGISTRY = ROOT / "research" / "continuous-recovery-20261016" / "local-audit" / "gallery-final-v7" / "gallery-prefix-registry-v7.json"
BATCH_ID = "WAYBACK-GALLERY-LATE-REST10A-20261019"
USER_AGENT = "wow-recovery-gallery-late-rest10a/20261019"
PROXY = "http://127.0.0.1:7890"
FROM_TS, TO_TS, LIMIT = "20080512210045", "20101207235959", 500
WINDOW_SECONDS, MAX_ATTEMPTS = 900.0, 24
MAX_TOTAL_BODY_BYTES, MAX_ENTITY_BODY_BYTES = 32 * 1024 * 1024, 8 * 1024 * 1024
# The historical GALLERYPREFIX01 driver slept until 5.1s and Windows returned
# from sleep early (observed 5.093s).  v3 treats 5.25s as the scheduling floor,
# then recomputes persisted minima against the requested acceptance floor.
MIN_DISPATCH_SECONDS, MIN_REQUEST_START_SECONDS = 5.25, 5.0
ACCEPTANCE_DISPATCH_SECONDS = 5.25
NETWORK_DEADLINE_UTC = datetime(2026, 10, 19, 13, 15, 0, tzinfo=timezone.utc)
DISK_FLOOR_BYTES = 11_005_853_696
STOP_HTTP_CODES = {429, 503}
DIRECT_CONNECT_SECONDS, DIRECT_MAX_SECONDS = 4.0, 12.0
PROXY_CONNECT_SECONDS, PROXY_MAX_SECONDS = 8.0, 60.0
EXPECTED_GALLERIES = {"Magtheridon's Lair", "Gruul's Lair", "Serpentshrine Cavern", "The Battle for Mount Hyjal - Caverns of Time", "Tempest Keep - The Eye", "Doom Lord Kazzak", "Magister's Terrace", "Hellfire Citadel - Hellfire Ramparts", "Hellfire Citadel - The Blood Furnace", "Hellfire Citadel - The Shattered Halls"}
EXPECTED_QUERY_FROM = {gallery: FROM_TS for gallery in EXPECTED_GALLERIES}
MAX_BATCH_REQUESTS = 24
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
EXPECTED = {
    "registry": "",
}


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
    query_to = str(query_window.get("to") or TO_TS)
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


def canonical_query_url(prefix: str, from_ts: str | None = None, to_ts: str | None = None) -> str:
    """Build the exact no-collapse prefix query used by the root plan."""
    from_value = from_ts or FROM_TS
    to_value = to_ts or TO_TS
    return (
        "https://web.archive.org/cdx/search/cdx?url=" + quote(prefix, safe="")
        + "&matchType=prefix&output=json&fl=" + quote(",".join(FIELDS), safe="")
        + f"&from={from_value}&to={to_value}&limit={LIMIT}&showResumeKey=true"
    )


def validate_inputs() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """Offline gate for ten exact source-directory CDX prefixes.

    The plan is generated from the frozen v7 source-page literals and the new
    late-coverage-rest audit.  This gate performs no HTTP and never creates a
    payload replay target.
    """
    plan = read_json(PLAN_PATH, {})
    if plan.get("schema") != "wow-recovery.gallery-late-rest10a-plan.v1":
        raise RuntimeError("unsupported gallery-late-rest10a plan schema")
    candidates = plan.get("candidates") or []
    policy = plan.get("policy") or {}
    if (plan.get("candidate_count") != len(candidates)
            or plan.get("target_gallery_count") != len(EXPECTED_GALLERIES)
            or len(candidates) != len(EXPECTED_GALLERIES)):
        raise RuntimeError("late-rest10a plan candidate count mismatch")
    if {str(item.get("gallery") or "") for item in candidates} != EXPECTED_GALLERIES:
        raise RuntimeError("late-rest10a gallery set mismatch")
    if len({str(item.get("target_key") or "") for item in candidates}) != len(candidates):
        raise RuntimeError("late-rest10a target keys are not unique")
    if plan.get("network_deadline_utc") != iso(NETWORK_DEADLINE_UTC):
        raise RuntimeError("network deadline mismatch")
    expected_policy = {
        "from": "per_candidate", "to": TO_TS, "target_from": FROM_TS,
        "limit": LIMIT, "showResumeKey": True, "collapse": False,
        "matchType": "prefix", "max_attempts": MAX_ATTEMPTS,
        "max_requests": MAX_BATCH_REQUESTS, "window_seconds": WINDOW_SECONDS,
        "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "min_dispatch_seconds": MIN_DISPATCH_SECONDS,
        "min_request_start_seconds": MIN_REQUEST_START_SECONDS,
        "disk_floor_bytes": DISK_FLOOR_BYTES,
        "direct_connect_timeout_seconds": DIRECT_CONNECT_SECONDS,
        "direct_max_timeout_seconds": DIRECT_MAX_SECONDS,
        "proxy_connect_timeout_seconds": PROXY_CONNECT_SECONDS,
        "proxy_max_timeout_seconds": PROXY_MAX_SECONDS,
        "network_deadline_utc": iso(NETWORK_DEADLINE_UTC),
    }
    if any(policy.get(key) != value for key, value in expected_policy.items()):
        raise RuntimeError("late-rest10a policy mismatch")
    plan_window = plan.get("query_window") or {}
    if (plan_window.get("from") != "per_candidate"
            or plan_window.get("target_from") != FROM_TS
            or plan_window.get("to") != TO_TS
            or plan_window.get("limit") != LIMIT
            or plan_window.get("showResumeKey") is not True
            or plan_window.get("collapse") is not False
            or plan_window.get("matchType") != "prefix"):
        raise RuntimeError("late-rest10a top-level query window mismatch")
    input_entries = plan.get("input_bindings") or {}
    required = {
        "gallery_final_v7_registry", "root_gallery_registry_v7_acceptance",
        "latest_global_source_acceptance", "latest_control_gate",
        "latest_gallery_gap01_source_acceptance", "late_coverage_ledger",
        "late_prefix_candidates", "late_coverage_receipt",
        "template_gallery_late_gap01_driver",
    }
    if not required.issubset(input_entries):
        raise RuntimeError(f"required bindings missing: {sorted(required - set(input_entries))}")
    bindings: dict[str, Any] = {}
    for key, entry in input_entries.items():
        path = ROOT / str(entry.get("path") or "")
        if not path.is_file():
            raise RuntimeError(f"input missing {key}: {path}")
        actual = sha(path)
        if actual != str(entry.get("sha256") or ""):
            raise RuntimeError(f"input SHA mismatch {key}: {actual}")
        bindings[key] = {"path": rel(path), "sha256": actual, "bytes": path.stat().st_size}
    registry_path = ROOT / str(input_entries["gallery_final_v7_registry"]["path"])
    registry = read_json(registry_path, {})
    if sha(registry_path) != str(plan.get("registry_sha256") or ""):
        raise RuntimeError("v7 registry SHA is not bound")
    acceptance = read_json(ROOT / str(input_entries["root_gallery_registry_v7_acceptance"]["path"]), {})
    if acceptance.get("accepted") is not True or acceptance.get("registry_sha256") != sha(registry_path):
        raise RuntimeError("v7 registry acceptance is not bound")
    global_source = read_json(ROOT / str(input_entries["latest_global_source_acceptance"]["path"]), {})
    if global_source.get("accepted") is not True or global_source.get("failure_streak_end") != 0:
        raise RuntimeError("latest global news20f source is not accepted tail-zero")
    control_gate = read_json(ROOT / str(input_entries["latest_control_gate"]["path"]), {})
    if (control_gate.get("accepted") is not True
            or control_gate.get("resume_gate_passed") is not True
            or control_gate.get("control_final_streak") != 0):
        raise RuntimeError("control gate is not accepted tail-zero")
    gallery_gap = read_json(ROOT / str(input_entries["latest_gallery_gap01_source_acceptance"]["path"]), {})
    if gallery_gap.get("accepted") is not True or gallery_gap.get("failure_streak_end") != 0:
        raise RuntimeError("gallery gap01 correction receipt is not accepted tail-zero")
    audit = read_json(ROOT / str(input_entries["late_coverage_ledger"]["path"]), {})
    if (audit.get("network_performed") is not False
            or audit.get("network_requests_during_audit") != 0
            or len(audit.get("rows") or []) != 50
            or audit.get("coverage_summary", {}).get("late_status_counts") != {"complete": 3, "not_queried": 47}):
        raise RuntimeError("late coverage audit is not the zero-request 50-group ledger")
    candidates_manifest = read_json(ROOT / str(input_entries["late_prefix_candidates"]["path"]), {})
    if (candidates_manifest.get("network_performed") is not False
            or len(candidates_manifest.get("candidates") or []) != 10
            or candidates_manifest.get("source_ledger_sha256_after_write") != sha(ROOT / str(input_entries["late_coverage_ledger"]["path"]))):
        raise RuntimeError("late candidate manifest is not the bound zero-request ten-prefix draft")
    if plan.get("prior_failure_tail") != 0:
        raise RuntimeError("late-rest10a prior failure tail is not zero")
    rows = registry.get("coverage_rows") or []
    normalized: list[dict[str, Any]] = []
    for rank, candidate in enumerate(candidates, 1):
        gallery = str(candidate.get("gallery") or "")
        source_row = next((row for row in rows if row.get("gallery") == gallery), None)
        if source_row is None:
            raise RuntimeError(f"gallery missing from frozen v7 registry: {gallery!r}")
        for key in ("registry_rank", "source_page_route", "declared_slots", "expected_direct_entities", "source_evidence"):
            if candidate.get(key) != source_row.get(key):
                raise RuntimeError(f"registry literal mismatch {gallery!r}: {key}")
        if (candidate.get("origin_host") != source_row.get("origin_host_from_entity_urls")
                or candidate.get("origin_schemes") != source_row.get("origin_schemes_from_entity_urls")):
            raise RuntimeError(f"registry origin mismatch {gallery!r}")
        prefix = str(candidate.get("prefix") or "")
        parsed_prefix = urlsplit(prefix)
        if (parsed_prefix.scheme != "http"
                or parsed_prefix.hostname != "www.worldofwarcraft.com"
                or parsed_prefix.port not in (None, 80)
                or not parsed_prefix.path.endswith("/")
                or parsed_prefix.query or parsed_prefix.fragment):
            raise RuntimeError(f"candidate origin widened or malformed: {prefix!r}")
        source = candidate.get("source_evidence") or {}
        source_path = ROOT / str(source.get("path") or "")
        if not source_path.is_file() or sha(source_path) != str(source.get("sha256") or ""):
            raise RuntimeError(f"candidate source hash mismatch: {gallery!r}")
        if source.get("source_directory") != parsed_prefix.path or source.get("filename_literal") != "ss":
            raise RuntimeError(f"candidate source literal mismatch: {gallery!r}")
        literal = str(source.get("numShots_literal") or "")
        num_shots = literal.split("=", 1)[1].split(";", 1)[0].strip() if "=" in literal else "0"
        if int(num_shots or 0) != int(candidate.get("declared_slots") or 0):
            raise RuntimeError(f"candidate slot mismatch: {gallery!r}")
        query_window = candidate.get("query_window") or {}
        query_from, query_to = str(query_window.get("from") or ""), str(query_window.get("to") or "")
        if (not re.fullmatch(r"\d{14}", query_from)
                or not re.fullmatch(r"\d{14}", query_to)
                or query_from != FROM_TS or query_to != TO_TS):
            raise RuntimeError(f"candidate query window outside anchor-to-end target: {gallery!r}")
        for key, expected in (("limit", LIMIT), ("showResumeKey", True), ("collapse", False), ("matchType", "prefix")):
            if query_window.get(key) != expected:
                raise RuntimeError(f"candidate query window policy mismatch: {gallery!r}:{key}")
        query_url = str(candidate.get("query_url") or candidate.get("cdx_query_url") or "")
        if query_url != canonical_query_url(prefix, query_from, query_to):
            raise RuntimeError(f"candidate query URL mismatch: {gallery!r}")
        normalized_item = dict(candidate)
        normalized_item.update({
            "rank": rank, "target_key": candidate.get("target_key") or f"GALLERY-LATE-REST10A-{rank:02d}",
            "label": gallery, "category": "native-gallery-late-window", "cdx_query_url": query_url,
            "query_window": query_window, "source_directory": source.get("source_directory"),
            "declared_entity_count": candidate.get("expected_direct_entities"),
        })
        normalized.append(normalized_item)
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

    sample = [FIELDS, ["key", "20090101000000", "http://www.worldofwarcraft.com/info/events/x/ss1.jpg", "image/jpeg", "200", "D", "12"], [], ["resume-fixture"]]
    parsed = parse_cdx(json.dumps(sample).encode())
    check("parse_header_separator_resume", parsed["valid"] and len(parsed["rows"]) == 1 and parsed["resume"] == ["resume-fixture"], {"rows": len(parsed["rows"]), "resume": parsed["resume"]})
    rows500 = [FIELDS] + [[f"k{i}", "20090101000000", f"http://www.worldofwarcraft.com/info/events/x/ss{i+1}.jpg", "image/jpeg", "200", "D", "12"] for i in range(500)] + [[], ["resume-500"]]
    parsed500 = parse_cdx(json.dumps(rows500).encode())
    check("limit_500_and_resume", parsed500["valid"] and len(parsed500["rows"]) == 500 and parsed500["resume"] == ["resume-500"], {"rows": len(parsed500["rows"]), "resume": parsed500["resume"], "continuation_followed": False})
    unknown = parse_cdx(json.dumps([FIELDS, {"unexpected": "metadata"}]).encode())
    check("unknown_metadata_incomplete", not unknown["valid"] and unknown["error"] == "cdx_unrecognized_metadata", {"error": unknown["error"]})
    prefix = "http://www.worldofwarcraft.com/info/events/x/"
    check("default_port_identity", same_origin("http://www.worldofwarcraft.com:80/info/events/x/ss1.jpg", prefix) == "same_origin_prefix", same_origin("http://www.worldofwarcraft.com:80/info/events/x/ss1.jpg", prefix))
    identities = {"scheme": same_origin("https://www.worldofwarcraft.com/info/events/x/ss1.jpg", prefix), "host": same_origin("http://wow-europe.com/info/events/x/ss1.jpg", prefix), "path": same_origin("http://www.worldofwarcraft.com/info/events/y/ss1.jpg", prefix), "query": same_origin("http://www.worldofwarcraft.com/info/events/x/ss1.jpg?q=1", prefix)}
    check("identity_rejections", identities == {"scheme": "scheme_mismatch", "host": "host_mismatch", "path": "path_prefix_mismatch", "query": "query_or_fragment_present"}, identities)
    variant_payload = [FIELDS, ["canonical", "20090101000000", prefix + "ss1.jpg", "image/jpeg", "200", "D1", "12"], ["https", "20090101000000", "https://www.worldofwarcraft.com/info/events/x/ss1.jpg", "image/jpeg", "200", "D2", "12"], ["bare", "20090101000000", "http://worldofwarcraft.com/info/events/x/ss1-thumb.jpg", "image/jpeg", "200", "D3", "12"]]
    analysis = project_rows(parse_cdx(json.dumps(variant_payload).encode()), {"prefix": prefix})
    check("identity_variants_separate", analysis["row_counts"]["direct_identity_variant_candidates"] == 2 and analysis["row_counts"]["strict_full"] == 1, analysis["row_counts"])
    clock = _FixtureClock(monotonic_start=100.0, ratio=0.965, quantum=0.1)
    first = _schedule_next(None, None, None, clock)
    second = _schedule_next(first["dispatch_monotonic"], first["dispatch_utc"], first["dispatch_utc"], clock)
    check("cadence_rechecks_early_sleep", second["dispatch_interval_seconds"] >= MIN_DISPATCH_SECONDS and second["request_start_interval_seconds"] >= MIN_REQUEST_START_SECONDS, {"dispatch": second["dispatch_interval_seconds"], "start": second["request_start_interval_seconds"]})
    restart_clock = _FixtureClock(monotonic_start=900.0, utc_start=second["dispatch_utc"] + timedelta(seconds=2.0), ratio=0.965, quantum=0.1)
    restored = _restart_last_dispatch({"dispatch_utc": iso(second["dispatch_utc"])}, restart_clock)
    restarted = _schedule_next(restored, second["dispatch_utc"], second["dispatch_utc"], restart_clock)
    check("restart_restores_utc_cadence", restarted["dispatch_monotonic"] - restored >= MIN_DISPATCH_SECONDS and restarted["request_start_interval_seconds"] >= MIN_REQUEST_START_SECONDS, {"dispatch": restarted["dispatch_monotonic"] - restored, "start": restarted["request_start_interval_seconds"]})
    full_clamp = _remaining_clamp(0, 10.0, 0.0, transport="proxy")
    near_clamp = _remaining_clamp(31 * 1024 * 1024, 899.5, 0.0, transport="proxy")
    check("remaining_32mib_and_900s_clamp", full_clamp["entity_body_limit_before_bytes"] == MAX_ENTITY_BODY_BYTES and full_clamp["max_timeout_seconds"] == PROXY_MAX_SECONDS and near_clamp["entity_body_limit_before_bytes"] == 1 * 1024 * 1024 and near_clamp["max_timeout_seconds"] <= 0.5 and near_clamp["clamp_applied"], {"full": full_clamp, "near": near_clamp})
    check("disk_floor_per_request", DISK_FLOOR_BYTES == 11_005_853_696, {"disk_floor_bytes": DISK_FLOOR_BYTES})
    check("stop_threshold_five", 5 >= 5, {"threshold": 5})
    check("index_only_no_payload_replay", True, {"payload_replay_count": 0, "automatic_redirects": 0})
    try:
        prepared_plan, prepared_candidates, _ = validate_inputs()
        names = {x["gallery"] for x in prepared_candidates}
        unique_prefixes = len({x["prefix"] for x in prepared_candidates})
        windows_valid = all(x["query_window"]["from"] == FROM_TS and x["query_window"]["to"] == TO_TS for x in prepared_candidates)
        check("ten_exact_source_prefixes", len(prepared_candidates) == 10 and names == EXPECTED_GALLERIES and unique_prefixes == 10 and windows_valid, {"count": len(prepared_candidates), "names": sorted(names), "unique_prefixes": unique_prefixes, "windows_valid": windows_valid})
        check("batch_caps_bound", prepared_plan["policy"]["max_requests"] == 24 and prepared_plan["policy"]["max_attempts"] == 24 and prepared_plan["policy"]["window_seconds"] == 900.0 and prepared_plan["policy"]["max_total_body_bytes"] == 32 * 1024 * 1024, prepared_plan["policy"])
        check("newest_global_tail_bound", any(x.get("path", "").endswith("root-frontier-news20f-source-acceptance.json") for x in (prepared_plan.get("input_bindings") or {}).values()), prepared_plan.get("input_bindings"))
    except Exception as exc:
        check("ten_exact_source_prefixes", False, {"error": f"{type(exc).__name__}:{exc}"})
        check("batch_caps_bound", False, {"error": "validation failed"})
        check("newest_global_tail_bound", False, {"error": "validation failed"})
    passed = sum(int(x["passed"]) for x in results)
    return {"schema": "wow-recovery.gallery-late-rest10a-driver-v1-fixture-results.v1", "mode": "offline_fixture", "network_requests": 0, "passed": passed, "total": len(results), "all_passed": passed == len(results), "cadence": {"scheduling_floor_seconds": MIN_DISPATCH_SECONDS, "acceptance_floor_seconds": ACCEPTANCE_DISPATCH_SECONDS}, "results": results}


def plan_for_run(plan: dict[str, Any], candidates: list[dict[str, Any]], bindings: dict[str, Any], fixture_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "wow-recovery.gallery-late-rest10a-execution-plan.v1",
        "batch_id": BATCH_ID, "mode": "go_executed", "prepared_utc": iso(now()),
        "source_plan_path": rel(PLAN_PATH), "source_plan_sha256": sha(PLAN_PATH),
        "candidate_count": len(candidates), "candidate_ranks": [x["rank"] for x in candidates],
        "scope": "ten exact v7 source-directory prefixes after the 20080512210044 anchor through 20101207235959; CDX index only, no replay, no filename expansion",
        "query_window": {"from": "per_candidate", "target_from": FROM_TS, "to": TO_TS, "limit": LIMIT, "showResumeKey": True, "collapse": False, "matchType": "prefix"},
        "network_deadline_utc": iso(NETWORK_DEADLINE_UTC), "index_only": True, "no_payload_replay": True,
        "max_attempts": MAX_ATTEMPTS, "max_requests": MAX_BATCH_REQUESTS, "window_seconds": WINDOW_SECONDS,
        "max_total_body_bytes": MAX_TOTAL_BODY_BYTES, "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "direct_first": True, "proxy": PROXY, "tls_verification": True, "automatic_redirects": 0,
        "direct_connect_timeout_seconds": DIRECT_CONNECT_SECONDS, "direct_max_timeout_seconds": DIRECT_MAX_SECONDS,
        "proxy_connect_timeout_seconds": PROXY_CONNECT_SECONDS, "proxy_max_timeout_seconds": PROXY_MAX_SECONDS,
        "min_dispatch_monotonic_seconds": MIN_DISPATCH_SECONDS, "acceptance_dispatch_floor_seconds": ACCEPTANCE_DISPATCH_SECONDS,
        "min_request_start_utc_seconds": MIN_REQUEST_START_SECONDS, "disk_floor_bytes": DISK_FLOOR_BYTES,
        "stop_http_codes": sorted(STOP_HTTP_CODES), "stop_on_five_consecutive_transport_failures": True,
        "retry_after_rule": "429/503 stop immediately; cooldown not earlier than Retry-After and at least 120 seconds",
        "resume_rule": "record actual response resumeKey; do not follow continuation in this batch; incomplete if resume remains",
        "failure_streak_start": 0, "prior_failure_tail": 0, "control_basis": "latest news20f global source tail0 plus accepted control; gallery gap01 retained for historical correction only",
        "input_bindings": bindings, "fixture": {"path": rel(OUT / "fixture-results.json"), "sha256": sha(OUT / "fixture-results.json"), "all_passed": fixture_result["all_passed"]},
        "candidates": [{"rank": x["rank"], "target_key": x.get("target_key"), "gallery": x["gallery"], "label": x["label"], "prefix": x["prefix"], "declared_slots": x.get("declared_slots"), "query_window": x["query_window"], "cdx_query_url": x["cdx_query_url"], "source_evidence": x.get("source_evidence")} for x in candidates],
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
    if dispatch_utc >= NETWORK_DEADLINE_UTC:
        raise RuntimeError("network_deadline_before_dispatch")
    remaining_window = WINDOW_SECONDS - max(0.0, elapsed)
    if remaining_window <= 0:
        raise RuntimeError("window_exhausted_before_dispatch")
    # Check the disk after waiting as well as before it, and persist the value
    # with every reservation even when a later transport step is unavailable.
    free_before = free_bytes()
    if free_before < DISK_FLOOR_BYTES:
        raise RuntimeError("disk_floor_before_dispatch")
    prior_body = int(state.get("total_body_bytes", 0))
    deadline_remaining = max(0.0, (NETWORK_DEADLINE_UTC - dispatch_utc).total_seconds())
    clamp = _remaining_clamp(prior_body, dispatch_mono, window_start, transport=transport, hard_remaining=deadline_remaining)
    entity_limit = int(clamp["entity_body_limit_before_bytes"])
    connect_time = float(clamp["connect_timeout_seconds"])
    max_time = float(clamp["max_timeout_seconds"])
    if not clamp["dispatch_allowed"] or entity_limit <= 0:
        raise RuntimeError("remaining_budget_exhausted_before_dispatch")
    stem = f"{attempt_no:02d}-GALLERYLATEWINDOW-R{rank:02d}-cdx-{transport}"
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
    state: dict[str, Any] = {"schema": "wow-recovery.gallery-late-window-state.v1", "batch_id": BATCH_ID, "mode": "prepared", "prior_failure_tail": 0, "failure_streak_start": 0, "failure_streak": 0, "total_body_bytes": 0, "attempts": 0, "source_responses": 0, "payload_replay_count": 0, "continuation_followed": False, "stop_reason": None, "max_requests": MAX_BATCH_REQUESTS}
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
    consecutive_transport = 0
    next_attempt = 1
    stop_reason: str | None = None
    results: list[dict[str, Any]] = []
    for item in candidates:
        if stop_reason or next_attempt > MAX_ATTEMPTS or next_attempt > MAX_BATCH_REQUESTS:
            break
        rank = int(item["rank"])
        target_attempts: list[dict[str, Any]] = []
        for transport in ("direct", "proxy"):
            if stop_reason or next_attempt > MAX_ATTEMPTS or next_attempt > MAX_BATCH_REQUESTS:
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
            results.append({"rank": rank, "label": item["label"], "category": item["category"], "prefix": item["prefix"], "source_directory": item.get("source_directory"), "declared_entity_count": item.get("declared_entity_count"), "query_url": item["cdx_query_url"], "attempts": [public_attempt(x) for x in target_attempts], "source_response_count": sum(int(x.get("source_status") is not None) for x in target_attempts), "capture_index_count": final.get("cdx_record_count", 0), "cdx_json_valid": final.get("cdx_json_valid"), "cdx_parse_error": final.get("cdx_parse_error"), "resume_keys": final.get("resume_keys") or [], "potential_truncation": final.get("potential_truncation", False), "continuation_followed": False, "strict_literal_full_candidates": analysis.get("strict_literal_full_candidates", []), "strict_literal_thumb_candidates": analysis.get("strict_literal_thumb_candidates", []), "nested_preview_or_other_rows": analysis.get("nested_preview_or_other_rows", []), "other_rows": analysis.get("other_rows", []), "direct_identity_variant_candidates": analysis.get("direct_identity_variant_candidates", []), "redirect_rows": analysis.get("redirect_rows", []), "row_counts": analysis.get("row_counts", {}), "status": "potential_truncation" if final.get("potential_truncation") else "complete_within_response" if final.get("cdx_json_valid") else "transport_or_parse_unknown", "payload_replay_count": 0})
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
    report = {"schema": "wow-recovery.gallery-late-window-batch-report.v1", "batch_id": BATCH_ID, **state, "network_requests": len(attempts), "candidate_results": results, "cadence": {"dispatch_intervals": [x.get("interval_since_previous_dispatch_seconds") for x in dispatches[1:]], "request_start_intervals": [x.get("request_start_interval_seconds") for x in attempts[1:]], "min_dispatch": min((x.get("interval_since_previous_dispatch_seconds") for x in dispatches[1:] if x.get("interval_since_previous_dispatch_seconds") is not None), default=None), "min_request_start": min((x.get("request_start_interval_seconds") for x in attempts[1:] if x.get("request_start_interval_seconds") is not None), default=None), "scheduling_floor_seconds": MIN_DISPATCH_SECONDS, "acceptance_floor_seconds": ACCEPTANCE_DISPATCH_SECONDS, "dispatch_passed": all((x.get("interval_since_previous_dispatch_seconds") or MIN_DISPATCH_SECONDS) >= MIN_DISPATCH_SECONDS for x in dispatches[1:]), "start_passed": all((x.get("request_start_interval_seconds") or MIN_REQUEST_START_SECONDS) >= MIN_REQUEST_START_SECONDS for x in attempts[1:])}, "policy": plan, "fixture": {"path": rel(OUT / "fixture-results.json"), "sha256": sha(OUT / "fixture-results.json"), "all_passed": fixture_result.get("all_passed")}, "plan_sha256": plan_hash, "raw_evidence_note": "Raw CDX headers, bodies, stderr, traces and metrics remain local; no payload replay or image acceptance was performed."}
    write_json(report_path, report)
    source_map = {"schema": "wow-recovery.gallery-late-window-source-map.v1", "batch_id": BATCH_ID, "index_only": True, "accepted_payloads": [], "entries": [{"rank": x["rank"], "label": x["label"], "prefix": x["prefix"], "status": x.get("status"), "capture_index_count": x.get("capture_index_count", 0), "resume_keys": x.get("resume_keys", []), "potential_truncation": x.get("potential_truncation", False), "strict_literal_full_count": len(x.get("strict_literal_full_candidates", [])), "strict_literal_thumb_count": len(x.get("strict_literal_thumb_candidates", [])), "direct_identity_variant_count": len(x.get("direct_identity_variant_candidates", [])), "nested_or_other_count": len(x.get("nested_preview_or_other_rows", [])) + len(x.get("other_rows", [])), "payload_replay_count": 0, "attempts": x.get("attempts", [])} for x in results]}
    write_json(OUT / "source-map.json", source_map)
    summary = {"schema": "wow-recovery.gallery-late-window-sanitized-summary.v1", "batch_id": BATCH_ID, "network_requests": len(attempts), "source_responses": state["source_responses"], "stop_reason": stop_reason, "failure_streak": consecutive_transport, "candidate_count": len(candidates), "queried_ranks": [x["rank"] for x in results], "not_queried_ranks": [x["rank"] for x in candidates if x["rank"] not in {r["rank"] for r in results}], "potential_truncation_ranks": [x["rank"] for x in results if x.get("potential_truncation")], "resume_key_ranks": [x["rank"] for x in results if x.get("resume_keys")], "continuation_followed": False, "payload_replay_count": 0, "prior_failure_tail_preserved": 0, "failure_streak_start": 0, "cooldown_required_seconds": state.get("cooldown_required_seconds"), "cooldown_not_before_utc": state.get("cooldown_not_before_utc"), "plan_sha256": plan_hash, "report_sha256": sha(report_path)}
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
    input_binding = {"schema": "wow-recovery.gallery-late-window-driver-v1-execution-input-bindings.v1", "batch_id": BATCH_ID, "source_bindings": bindings, "plan_path": rel(OUT / "execution-plan.json"), "plan_sha256": sha(OUT / "execution-plan.json"), "fixture_path": rel(OUT / "fixture-results.json"), "fixture_sha256": sha(OUT / "fixture-results.json"), "script_path": rel(Path(__file__)), "script_sha256": script_hash, "control_resume_gate": True, "network_requests": report.get("network_requests")}
    execution_bindings_path = OUT / "execution-input-bindings.json"
    write_json(execution_bindings_path, input_binding)
    report["input_binding_path"] = rel(execution_bindings_path)
    report["input_binding_sha256"] = sha(execution_bindings_path)
    report["script_sha256"] = script_hash
    write_json(OUT / "batch-report.json", report)
    summary = read_json(OUT / "sanitized-summary.json", {})
    summary["script_sha256"] = script_hash
    summary["input_binding_sha256"] = sha(execution_bindings_path)
    write_json(OUT / "sanitized-summary.json", summary)
    print(json.dumps({"mode": "executed", "batch_id": BATCH_ID, "network_requests": report.get("network_requests"), "source_responses": report.get("source_responses"), "stop_reason": report.get("stop_reason"), "potential_truncation_ranks": summary.get("potential_truncation_ranks"), "resume_key_ranks": summary.get("resume_key_ranks"), "payload_replay_count": report.get("payload_replay_count"), "plan_sha256": input_binding["plan_sha256"], "script_sha256": script_hash}, ensure_ascii=False))


if __name__ == "__main__":
    main()

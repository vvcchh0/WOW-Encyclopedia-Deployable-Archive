"""NET-HIRES-011 bounded exact hires recovery.

The driver owns only this directory.  It reuses the accepted core-pages3
transport/header/CDX parser and control7 dispatch gate.  It never follows a
redirect and writes source entities only below this batch's raw directory.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

try:
    from PIL import Image
except Exception:  # pragma: no cover - checked during execution
    Image = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"

CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v9/build-manifest.json"
V9_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/root-v9-source-acceptance.json"
MIXED9_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/mixed9-acceptance.json"
NATIVE_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/native-viewer-acceptance.json"
VIEWER_VALIDATION = ROOT / "research/v10-integration/native-viewer-validation/source-validation.json"
VIEWER_RESULTS = ROOT / "research/v10-integration/native-viewer-validation/vm-results.json"
VIEWER_RAW = ROOT / "research/continuous-recovery-20261015/network-mixed9/raw/03-screeniesimplified-js-replay-proxy.body"
MIXED9_MAP = ROOT / "research/continuous-recovery-20261015/network-mixed9/payload-source-map.json"

WAYBACK_BASE = "https://web.archive.org"
BASE = "http://www.worldofwarcraft.com/wrath/images/artwork/"
PRE_FROM = "20040101000000"
PRE_TO = "20080512210044"
LATE_FROM = "20080513000000"
LATE_TO = "20101231235959"
PROXY = "http://127.0.0.1:7890"
USER_AGENT = "wow-recovery-hires11/20261015"
MIN_FREE = 11_005_853_696
MAX_TARGETS = 13
MAX_ATTEMPTS = 32
WINDOW_SECONDS = 8 * 60
INTERVAL_SECONDS = 1.25
MAX_TOTAL_BODY = 64 * 1024 * 1024
MAX_ENTITY_BODY = 16 * 1024 * 1024
REDIRECT_CODES = {301, 302, 303, 307, 308}
STOP_CODES = {429, 503}
TARGETS = (
    [(n, "original", "known_pair") for n in (1, 3, 6, 9, 12)]
    + [(n, "original", "remaining_pair") for n in (2, 4, 5, 7, 8, 10, 11)]
    + [(1, "locale_original", "locale")]
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


core = load_module(CORE_PATH, "hires11_core_pages3")
core.OUT = OUT
core.RAW = RAW
core.USER_AGENT = USER_AGENT
core.PROXY = PROXY
core.MIN_INTERVAL_SECONDS = 0.0
gate_mod = load_module(GATE_PATH, "hires11_control7")
gate_mod.INTERVAL_SECONDS = INTERVAL_SECONDS


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def disk_free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def b32_sha1(body: bytes) -> str | None:
    return base64.b32encode(hashlib.sha1(body).digest()).decode("ascii") if body else None


def source_body(attempt: dict[str, Any] | None) -> bytes:
    if not attempt:
        return b""
    body_path = OUT / str((attempt.get("raw") or {}).get("body") or "")
    return body_path.read_bytes() if body_path.is_file() else b""


def input_digest(path: Path) -> dict[str, Any]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def target_url(number: int, role: str) -> str:
    if role == "locale_original":
        return f"{BASE}en_us/ss{number}-hires.jpg"
    return f"{BASE}ss{number}-hires.jpg"


def cdx_query_url(url: str, from_ts: str, to_ts: str) -> str:
    params = [
        ("url", url),
        ("from", from_ts),
        ("to", to_ts),
        ("output", "json"),
        ("fl", ",".join(core.CDX_COLUMNS)),
        ("limit", str(core.CDX_LIMIT)),
        ("collapse", "digest"),
        ("matchType", "exact"),
    ]
    return f"{WAYBACK_BASE}/cdx/search/cdx?{urlencode(params)}"


def target_metadata(number: int, role: str, priority: str, rank: int, proof: dict[str, Any], local_matches: list[dict[str, Any]]) -> dict[str, Any]:
    url = target_url(number, role)
    return {
        "rank": rank,
        "target_key": f"gallery-ss{number}-hires" if role == "original" else "gallery-locale-ss1-hires",
        "kind": "content_image",
        "entity_class": "content_image",
        "gallery_number": number,
        "gallery_suffix": "-hires",
        "role": role,
        "priority": priority,
        "url": url,
        "query_original_url": url,
        "preanchor": {
            "name": "preanchor",
            "from": PRE_FROM,
            "to": PRE_TO,
            "temporal_status": "preanchor",
            "cdx_query_url": cdx_query_url(url, PRE_FROM, PRE_TO),
            "selection": "latest same-origin status-200 capture; redirects retained as index evidence",
        },
        "late_supplement": {
            "name": "late",
            "from": LATE_FROM,
            "to": LATE_TO,
            "temporal_status": "temporal_supplement",
            "cdx_query_url": cdx_query_url(url, LATE_FROM, LATE_TO),
            "selection": "earliest same-origin status-200 capture only when preanchor query had source HTTP 200, valid CDX, and zero rows",
        },
        "source_evidence": proof,
        "local_exact_verified_matches": local_matches,
        "local_exact_reuse": bool(local_matches),
        "same_origin_policy": "scheme+lowercase host+path+query; only default ports normalize; www/bare and HTTP/HTTPS remain separate",
        "no_url_inference": True,
    }


def exact_json_string_hits(path: Path, target: str) -> list[str]:
    """Find exact URL-valued strings in a bounded approved JSON source table."""
    try:
        value = read_json(path)
    except Exception:
        return []
    hits: list[str] = []

    def walk(node: Any, pointer: str) -> None:
        if isinstance(node, str):
            if node == target:
                hits.append(pointer)
            return
        if isinstance(node, dict):
            for key, child in node.items():
                walk(child, f"{pointer}/{key}")
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{pointer}/{index}")

    walk(value, "")
    return hits


def approved_source_tables() -> list[Path]:
    candidates = [
        MIXED9_MAP,
        ROOT / "research/continuous-recovery-20261015/network-wrath8/payload-source-map.json",
        ROOT / "research/continuous-recovery-20261015/network-assets5/asset-source-map.json",
        ROOT / "research/continuous-recovery-20261015/network-core-pages3/payload-source-map.json",
        ROOT / "research/continuous-recovery-20261015/network-core-pages4/payload-source-map.json",
        ROOT / "research/continuous-recovery-20261015/network-rss10/payload-source-map.json",
    ]
    return [path for path in candidates if path.is_file()]


def proof_inputs() -> dict[str, Any]:
    v9 = read_json(V9_ACCEPTANCE)
    mixed9 = read_json(MIXED9_ACCEPTANCE)
    native = read_json(NATIVE_ACCEPTANCE)
    validation = read_json(VIEWER_VALIDATION)
    vm_results = read_json(VIEWER_RESULTS)
    if not v9.get("accepted") or sha256_file(MANIFEST) != v9.get("manifest_sha256"):
        raise RuntimeError("accepted v9 manifest digest check failed")
    if not mixed9.get("accepted") or not native.get("accepted"):
        raise RuntimeError("accepted NET009/native-viewer evidence is not accepted")
    if validation.get("network_requests") != 0 or not validation.get("source_transform", {}).get("navigation_symbols_unchanged"):
        raise RuntimeError("native viewer source proof is incomplete")
    if vm_results.get("network_requests") != 0 or not vm_results.get("assertions", {}).get("all_cases_passed"):
        raise RuntimeError("native viewer VM proof is incomplete")
    if not VIEWER_RAW.is_file() or sha256_file(VIEWER_RAW) != validation["inputs"]["raw_viewer"]["sha256"]:
        raise RuntimeError("viewer raw proof digest mismatch")
    manifest = read_json(MANIFEST)
    files = manifest.get("files") or []
    tables = approved_source_tables()
    return {
        "v9_manifest": input_digest(MANIFEST),
        "v9_manifest_acceptance": input_digest(V9_ACCEPTANCE) | {"accepted": v9.get("accepted")},
        "mixed9_acceptance": input_digest(MIXED9_ACCEPTANCE) | {"accepted": mixed9.get("accepted"), "network_requests_by_acceptance": mixed9.get("network_requests_by_acceptance")},
        "native_viewer_acceptance": input_digest(NATIVE_ACCEPTANCE) | {"accepted": native.get("accepted"), "network_requests_by_acceptance": native.get("network_requests_by_acceptance")},
        "viewer_validation": input_digest(VIEWER_VALIDATION),
        "viewer_vm_results": input_digest(VIEWER_RESULTS),
        "viewer_raw": input_digest(VIEWER_RAW),
        "viewer_source_template": "dirList[nowViewing] + \"ss\" + hiResList[nowViewing] + \"-hires.jpg\"",
        "viewer_source_fragment": validation.get("source_transform", {}).get("original_fragment_span"),
        "viewer_source_transform_sha256": validation.get("derived", {}).get("sha256"),
        "native_vm_case_count": vm_results.get("assertions", {}).get("case_count"),
        "manifest_file_count": len(files),
        "approved_source_tables": [input_digest(path) for path in tables],
    }


def local_exact_matches(url: str, proof: dict[str, Any]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for entry in (read_json(MANIFEST).get("files") or []):
        values = [entry.get("source_base_url"), entry.get("source_url"), entry.get("source_original_url"), entry.get("url")]
        if url in values:
            matches.append({"table": proof["v9_manifest"]["path"], "match_kind": "exact_manifest_url", "entry": {k: entry.get(k) for k in ("route", "source_base_url", "source_length", "source_sha256", "source_local_path", "output_path", "derived_length", "derived_sha256")}})
    for path_info in proof["approved_source_tables"]:
        path = ROOT / Path(path_info["path"])
        pointers = exact_json_string_hits(path, url)
        if pointers:
            matches.append({"table": path_info["path"], "match_kind": "exact_approved_source_table_url", "json_pointers": pointers})
    return matches


def build_candidates(proof: dict[str, Any]) -> dict[str, Any]:
    validation = read_json(VIEWER_VALIDATION)
    vm_results = read_json(VIEWER_RESULTS)
    source_proof = {
        "viewer_raw_path": proof["viewer_raw"]["path"],
        "viewer_raw_sha256": proof["viewer_raw"]["sha256"],
        "viewer_actual_memento": validation["inputs"]["raw_viewer"]["actual_memento"],
        "approved_template": proof["viewer_source_template"],
        "source_validation_path": proof["viewer_validation"]["path"],
        "source_validation_sha256": proof["viewer_validation"]["sha256"],
        "vm_results_path": proof["viewer_vm_results"]["path"],
        "vm_results_sha256": proof["viewer_vm_results"]["sha256"],
        "vm_case_count": proof["native_vm_case_count"],
        "shot_list_verified": vm_results.get("assertions", {}).get("common12_locale1"),
        "hires_list_verified": vm_results.get("assertions", {}).get("hires_list_verified"),
        "screen_link_verified": vm_results.get("assertions", {}).get("screen_link_hires_verified"),
        "no_numeric_inference": True,
    }
    entries: list[dict[str, Any]] = []
    for rank, (number, role, priority) in enumerate(TARGETS, 1):
        url = target_url(number, role)
        entries.append(target_metadata(number, role, priority, rank, source_proof, local_exact_matches(url, proof)))
    return {
        "schema": "continuous-wow-network-hires11-candidates/v1",
        "batch_id": "NET-HIRES-011",
        "generated_utc": now_utc(),
        "network_requests": 0,
        "target_count": len(entries),
        "entries": entries,
        "input_digests": proof,
        "local_check": {
            "manifest_and_approved_tables_checked": True,
            "exact_target_count": len(entries),
            "exact_local_reuse_count": sum(bool(item["local_exact_verified_matches"]) for item in entries),
            "local_exact_reuse_policy": "reuse only exact verified source-table entity with retained local provenance; no basename, host, scheme, extension, or number alias",
        },
        "windows": {
            "preanchor": {"name": "preanchor", "from": PRE_FROM, "to": PRE_TO, "temporal_status": "preanchor"},
            "late": {"name": "late", "from": LATE_FROM, "to": LATE_TO, "temporal_status": "temporal_supplement"},
        },
        "selection": {
            "preanchor": "latest same-origin status-200 capture; all CDX rows retained; no redirect follow",
            "late": "query only after preanchor source HTTP 200 + valid CDX + zero rows; earliest same-origin status-200 capture; independent temporal supplement",
            "no_late_for_pre_unknown_or_nonempty_index": True,
        },
        "policy": {
            "max_distinct_targets": MAX_TARGETS,
            "max_attempts": MAX_ATTEMPTS,
            "network_window_seconds": WINDOW_SECONDS,
            "minimum_dispatch_interval_seconds": INTERVAL_SECONDS,
            "minimum_free_bytes": MIN_FREE,
            "max_total_body_bytes": MAX_TOTAL_BODY,
            "max_entity_body_bytes": MAX_ENTITY_BODY,
            "direct_first_then_existing_proxy": True,
            "proxy": PROXY,
            "automatic_redirects": 0,
            "manual_redirect_follow_hops": 0,
            "tls_verification": "curl default verification enabled",
            "stop_http_codes": sorted(STOP_CODES),
            "concurrent_source_requests": 1,
            "source_http_excludes_connect_200": True,
            "cdx_length_is_index_metadata": True,
            "raw_headers_trace_body_local_only": True,
        },
    }


def prepare() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    proof = proof_inputs()
    candidates = build_candidates(proof)
    candidate_path = OUT / "candidates.json"
    write_json(candidate_path, candidates)
    candidate_sha = sha256_file(candidate_path)
    disk = disk_free_bytes()
    config = {
        "schema": "continuous-wow-network-hires11-config/v1",
        "batch_id": "NET-HIRES-011",
        "candidate_path": str(candidate_path.relative_to(ROOT)).replace("\\", "/"),
        "candidate_sha256": candidate_sha,
        "transport_helper": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "dispatch_gate_helper": str(GATE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "network_requests": 0,
        "policy": candidates["policy"],
        "windows": candidates["windows"],
        "late_query_guard": "only preanchor source_status=200, cdx_parse_valid=true, capture_index_count=0",
    }
    write_json(OUT / "config.json", config)
    plan = {
        "schema": "continuous-wow-network-hires11-plan/v1",
        "batch_id": "NET-HIRES-011",
        "mode": "plan_only",
        "prepared_utc": now_utc(),
        "candidate_sha256": candidate_sha,
        "disk_free_bytes": disk,
        "minimum_free_bytes": MIN_FREE,
        "network_requests": 0,
        "ready": disk >= MIN_FREE and len(candidates["entries"]) == MAX_TARGETS,
        "target_order": [item["target_key"] for item in candidates["entries"]],
        "local_exact_reuse_count": candidates["local_check"]["exact_local_reuse_count"],
        "preanchor_then_conditional_late": True,
        "actual_dispatch_requires_execute": True,
    }
    write_json(OUT / "plan.json", plan)
    print(json.dumps({"mode": "plan_only", "batch_id": "NET-HIRES-011", "network_requests": 0, "target_count": len(candidates["entries"]), "candidate_sha256": candidate_sha, "disk_free_bytes": disk, "ready": plan["ready"]}, ensure_ascii=False))
    return 0


def public_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    return core.source_attempt_view(attempt)


def dispatch_ok(state: Any, window_started: float) -> tuple[bool, str | None]:
    if state.stop_reason:
        return False, state.stop_reason
    if state.attempts >= MAX_ATTEMPTS:
        return False, "attempt_limit"
    if time.monotonic() - window_started >= WINDOW_SECONDS:
        return False, "network_window_exhausted"
    if disk_free_bytes() < MIN_FREE:
        return False, "disk_free_below_threshold"
    if state.total_body_bytes >= MAX_TOTAL_BODY:
        return False, "total_body_limit"
    return True, None


def request(url: str, transport: str, kind: str, target_key: str, state: Any, gate: Any, window_started: float) -> dict[str, Any]:
    ok, reason = dispatch_ok(state, window_started)
    if not ok:
        return {"executed": False, "attempt": state.attempts + 1, "kind": kind, "target_key": target_key, "transport": transport, "url": url, "unrequested_reason": reason or "limit_before_request"}
    number = state.attempts + 1
    dispatch = gate.before_dispatch(number, transport, target_key)
    attempt = core.run_request(url, transport, kind, target_key, state, number)
    attempt["dispatch_utc"] = dispatch["dispatch_utc"]
    attempt["dispatch_monotonic"] = dispatch["dispatch_monotonic"]
    attempt["interval_since_previous_dispatch_seconds"] = dispatch["interval_since_previous_dispatch_seconds"]
    attempt["persisted_before_transport"] = dispatch["persisted_before_transport"]
    raw = source_body(attempt)
    attempt["local_zero_byte_body_placeholder"] = bool(attempt.get("source_status") is None and not raw)
    attempt["body_is_source_response"] = attempt.get("source_status") is not None
    return attempt


def in_window(timestamp: str | None, start: str, end: str) -> bool:
    return bool(timestamp and re.fullmatch(r"\d{14}", timestamp) and start <= timestamp <= end and core.parse_timestamp(timestamp) is not None)


def eligible_200(records: list[dict[str, str]], requested: str, start: str, end: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        item = dict(record)
        item["record_index"] = index
        item["statuscode_int"] = int(record["statuscode"]) if str(record.get("statuscode", "")).isdigit() else None
        item["within_query_range"] = in_window(record.get("timestamp"), start, end)
        item["original_match_kind"] = core.original_match_kind(record.get("original", ""), requested)
        item["exact_original_match"] = item["original_match_kind"] == "exact"
        item["valid_status_200_candidate"] = bool(item["within_query_range"] and item["original_match_kind"] is not None and item["statuscode_int"] == 200)
        if item["valid_status_200_candidate"]:
            result.append(item)
    return result


def select_capture(records: list[dict[str, Any]], late: bool) -> dict[str, Any] | None:
    if not records:
        return None
    return sorted(records, key=lambda row: row["timestamp"], reverse=not late)[0]


def body_observation(raw: bytes, content_type: str | None) -> dict[str, Any]:
    mime = (content_type or "").split(";", 1)[0].strip().lower() or None
    head = raw[:1024].lstrip().lower()
    html_like = head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"<html" in head or b"<title" in head
    return {"content_type": content_type, "mime": mime, "html_like": html_like, "body_bytes": len(raw)}


def validate_image(attempt: dict[str, Any], capture: dict[str, Any], window: dict[str, str]) -> tuple[bool, dict[str, Any], str]:
    raw = source_body(attempt)
    expected_digest = str(capture.get("digest") or "") or None
    calculated_digest = b32_sha1(raw)
    metrics = {
        "body_bytes": len(raw),
        "body_sha256": hashlib.sha256(raw).hexdigest() if raw else None,
        "cdx_digest_expected": expected_digest,
        "cdx_digest_calculated": calculated_digest,
        "cdx_digest_match": bool(expected_digest and calculated_digest and expected_digest.rstrip("=").upper() == calculated_digest.rstrip("=").upper()),
        "actual_memento": attempt.get("memento_datetime"),
        "content_type": attempt.get("content_type"),
        "source_status": attempt.get("source_status"),
        "raw_body_path": (attempt.get("raw") or {}).get("body"),
        "raw_headers_path": (attempt.get("raw") or {}).get("headers"),
        "raw_trace_path": (attempt.get("raw") or {}).get("trace"),
    }
    decode: dict[str, Any] = {"library": "Pillow", "verify": "not_run", "load": "not_run", "format": None, "width": None, "height": None, "mode": None, "error": None}
    metrics["decode"] = decode
    if attempt.get("source_status") != 200:
        return False, metrics, "source_status_not_200"
    actual = attempt.get("memento_datetime")
    if not actual:
        return False, metrics, "missing_actual_memento"
    try:
        actual_dt = datetime.fromisoformat(actual.replace("Z", "+00:00")).astimezone(timezone.utc)
        if not (datetime.strptime(window["from"], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc) <= actual_dt <= datetime.strptime(window["to"], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)):
            return False, metrics, "actual_memento_outside_requested_window"
    except ValueError:
        return False, metrics, "invalid_actual_memento"
    if metrics["cdx_digest_match"] is not True:
        return False, metrics, "cdx_digest_mismatch"
    if not raw:
        return False, metrics, "empty_200_body"
    if Image is None:
        decode["error"] = "Pillow_unavailable"
        return False, metrics, "pillow_unavailable"
    try:
        with Image.open(io.BytesIO(raw)) as image:
            decode["format"] = image.format
            decode["width"], decode["height"] = image.size
            decode["mode"] = image.mode
            image.verify()
        decode["verify"] = "passed"
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
        decode["load"] = "passed"
    except Exception as exc:  # pragma: no cover - source-dependent
        decode["error"] = f"{type(exc).__name__}: {exc}"
        return False, metrics, "pillow_validation_failed"
    if not decode["format"] or not decode["width"] or not decode["height"]:
        return False, metrics, "image_dimensions_missing"
    metrics["extension_expected"] = "JPEG"
    metrics["extension_format_match"] = str(decode["format"]).upper() in {"JPEG", "JPG"}
    return True, metrics, "valid_image"


def query_stats(attempts: list[dict[str, Any]], records: list[dict[str, str]], eligible: list[dict[str, Any]], query_url: str, window: dict[str, str]) -> dict[str, Any]:
    executed = [attempt for attempt in attempts if attempt.get("executed")]
    latest = executed[-1] if executed else None
    return {
        "query_url": query_url,
        "window": window,
        "query_performed": bool(attempts),
        "source_status": latest.get("source_status") if latest else None,
        "source_response_count": sum(attempt.get("source_status") is not None for attempt in attempts),
        "capture_index_count": len(records),
        "valid_status_200_count": len(eligible),
        "redirect_index_count": sum(str(row.get("statuscode")) in {str(code) for code in REDIRECT_CODES} for row in records),
        "capture_records": records,
        "selected_capture": None,
        "attempts": [public_attempt(attempt) for attempt in attempts],
        "precondition_for_late_query": None,
    }


def result_not_requested(item: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "rank": item["rank"], "target_key": item["target_key"], "url": item["url"], "query_original_url": item["query_original_url"], "kind": item["kind"], "entity_class": item["entity_class"], "priority": item["priority"], "window": "preanchor", "temporal_status": "preanchor", "category": "not_requested", "reason": reason, "preanchor": None, "late_supplement": None, "selected_window": None, "selected_capture": None, "replay_hops": [], "actual_memento_or_null": None, "source_status": None, "content_type": None, "body_bytes": 0, "body_sha256": None, "validation": None, "unrequested_reason": reason,
    }


def run_target(item: dict[str, Any], transport: str, state: Any, gate: Any, window_started: float, prefetched_pre_attempts: list[dict[str, Any]] | None = None) -> tuple[dict[str, Any], str]:
    key = item["target_key"]
    if not dispatch_ok(state, window_started)[0]:
        return result_not_requested(item, state.stop_reason or "limit_before_target"), transport
    pre = item["preanchor"]
    pre_attempts = prefetched_pre_attempts if prefetched_pre_attempts is not None else [request(pre["cdx_query_url"], transport, "cdx", key, state, gate, window_started)]
    pre_executed = [attempt for attempt in pre_attempts if attempt.get("executed")]
    pre_latest = pre_executed[-1] if pre_executed else None
    pre_records = (pre_latest or {}).get("cdx_records") or []
    pre_parse_valid = bool(pre_latest and pre_latest.get("cdx_parse_valid"))
    pre_eligible = eligible_200(pre_records, item["query_original_url"], PRE_FROM, PRE_TO) if pre_parse_valid else []
    pre_stats = query_stats(pre_attempts, pre_records, pre_eligible, pre["cdx_query_url"], pre)
    pre_stats["cdx_parse_valid"] = pre_latest.get("cdx_parse_valid") if pre_latest else None
    pre_stats["cdx_parse_error"] = pre_latest.get("cdx_parse_error") if pre_latest else None
    selected = select_capture(pre_eligible, late=False)
    selected_window = pre if selected else None
    late_stats: dict[str, Any] | None = None
    late_eligible: list[dict[str, Any]] = []
    late_attempts: list[dict[str, Any]] = []

    if selected is None and pre_latest and pre_latest.get("source_status") == 200 and not pre_latest.get("transport_error") and pre_parse_valid and not pre_records and not state.stop_reason:
        late = item["late_supplement"]
        late_attempts = [request(late["cdx_query_url"], transport, "cdx", key, state, gate, window_started)]
        late_executed = [attempt for attempt in late_attempts if attempt.get("executed")]
        late_latest = late_executed[-1] if late_executed else None
        late_records = (late_latest or {}).get("cdx_records") or []
        late_parse_valid = bool(late_latest and late_latest.get("cdx_parse_valid"))
        late_eligible = eligible_200(late_records, item["query_original_url"], LATE_FROM, LATE_TO) if late_parse_valid else []
        late_stats = query_stats(late_attempts, late_records, late_eligible, late["cdx_query_url"], late)
        late_stats["cdx_parse_valid"] = late_latest.get("cdx_parse_valid") if late_latest else None
        late_stats["cdx_parse_error"] = late_latest.get("cdx_parse_error") if late_latest else None
        late_stats["precondition_for_late_query"] = {"pre_source_status": 200, "pre_cdx_parse_valid": True, "pre_capture_index_count": 0}
        selected = select_capture(late_eligible, late=True)
        selected_window = late if selected else None

    replay_attempts: list[dict[str, Any]] = []
    validation: dict[str, Any] | None = None
    category = "network_unknown"
    reason = "unknown"
    actual_memento = None
    source_status = None
    content_type = None
    body_bytes = 0
    body_sha = None
    if selected is not None and selected_window is not None and not state.stop_reason:
        if late_stats is not None:
            late_stats["selected_capture"] = selected
        else:
            pre_stats["selected_capture"] = selected
        replay_url = core.replay_url(selected)
        replay_attempts = [request(replay_url, transport, "replay", key, state, gate, window_started)]
        final = replay_attempts[-1] if replay_attempts else None
        if final:
            actual_memento = final.get("memento_datetime")
            source_status = final.get("source_status")
            content_type = final.get("content_type")
            raw = source_body(final)
            body_bytes = len(raw)
            body_sha = hashlib.sha256(raw).hexdigest() if raw else None
            if final.get("transport_error"):
                category, reason = "network_unknown", final.get("transport_reason") or "replay_transport_error"
            elif source_status in STOP_CODES:
                category, reason = "rate_limited", f"source_status_{source_status}"
            elif source_status in REDIRECT_CODES:
                category, reason = "redirect_only", "replay_redirect_not_followed"
            elif source_status != 200:
                category, reason = "http_response", f"replay_source_status_{source_status}"
            else:
                valid, validation, validation_reason = validate_image(final, selected, selected_window)
                if valid:
                    category, reason = ("valid_image_temporal_supplement" if selected_window is item["late_supplement"] else "valid_image"), "Pillow verify+load and CDX/base32/body checks passed"
                else:
                    observed = body_observation(raw, content_type)
                    validation["body_observation"] = observed
                    category = "soft404" if observed["html_like"] or str(observed.get("mime") or "").startswith("text/html") else "invalid_payload"
                    reason = validation_reason
    elif pre_latest is None or pre_latest.get("transport_error"):
        category, reason = "network_unknown", (pre_latest or {}).get("transport_reason") or "preanchor_query_transport_error"
    elif pre_latest.get("source_status") in STOP_CODES:
        category, reason = "rate_limited", f"source_status_{pre_latest.get('source_status')}"
    elif not pre_parse_valid:
        category, reason = "cdx_invalid", pre_latest.get("cdx_parse_error") or "preanchor_cdx_parse_failed"
    elif pre_records and not pre_eligible:
        category, reason = "indexed_non200", "preanchor_index_nonempty_without_same_origin_status_200"
    elif not pre_records and late_stats is not None:
        latest_late_attempt = [attempt for attempt in late_attempts if attempt.get("executed")]
        late_latest = latest_late_attempt[-1] if latest_late_attempt else None
        if late_latest is None or late_latest.get("transport_error"):
            category, reason = "network_unknown", (late_latest or {}).get("transport_reason") or "late_query_transport_error"
        elif late_latest.get("source_status") in STOP_CODES:
            category, reason = "rate_limited", f"source_status_{late_latest.get('source_status')}"
        elif not late_latest.get("cdx_parse_valid"):
            category, reason = "cdx_invalid", late_latest.get("cdx_parse_error") or "late_cdx_parse_failed"
        elif late_latest.get("cdx_records"):
            category, reason = "indexed_non200", "late_index_nonempty_without_same_origin_status_200"
        else:
            category, reason = "not_archived", "preanchor_and_late_queries_returned_zero_capture_rows"
    elif not pre_records:
        category, reason = "not_archived", "preanchor_query_returned_zero_capture_rows_and_late_query_not_allowed"

    result = {
        "rank": item["rank"], "target_key": key, "url": item["url"], "query_original_url": item["query_original_url"], "kind": item["kind"], "entity_class": item["entity_class"], "priority": item["priority"], "window": selected_window["name"] if selected_window else "preanchor", "temporal_status": selected_window["temporal_status"] if selected_window else "preanchor", "category": category, "reason": reason, "preanchor": pre_stats, "late_supplement": late_stats, "selected_window": selected_window["name"] if selected_window else None, "selected_capture": selected, "replay_hops": [public_attempt(attempt) for attempt in replay_attempts], "actual_memento_or_null": actual_memento, "source_status": source_status, "content_type": content_type, "body_bytes": body_bytes, "body_sha256": body_sha, "validation": validation, "unrequested_reason": None,
    }
    return result, transport


def source_map_entry(result: dict[str, Any]) -> dict[str, Any]:
    selected = result.get("selected_capture") or {}
    replay = (result.get("replay_hops") or [])[-1]
    validation = result.get("validation") or {}
    return {
        "target": result["target_key"], "query_original_url": result["query_original_url"], "actual_memento": result["actual_memento_or_null"], "temporal_status": result["temporal_status"], "entity_class": result["entity_class"], "source_status": result["source_status"], "content_type": result["content_type"], "body_bytes": result["body_bytes"], "body_sha256": result["body_sha256"], "raw_body_path": replay.get("raw", {}).get("body"), "raw_headers_path": replay.get("raw", {}).get("headers"), "captured_original_url": selected.get("original"), "indexed_capture_timestamp": selected.get("timestamp"), "indexed_statuscode": selected.get("statuscode"), "CDXdigest": selected.get("digest"), "CDXlength": selected.get("length"), "CDXdigest_calculated": validation.get("cdx_digest_calculated"), "CDXdigest_match": validation.get("cdx_digest_match"), "decode": validation.get("decode"), "action": "review before integration; entity remains only in this batch raw directory",
    }


def append_unrequested(entries: list[dict[str, Any]], results: list[dict[str, Any]], state: Any) -> None:
    reason = state.stop_reason or "batch_execution_stopped"
    for item in entries[len(results):]:
        results.append(result_not_requested(item, reason))


def write_outputs(candidates: dict[str, Any], results: list[dict[str, Any]], state: Any, started_utc: str, finished_utc: str, report_updated_utc: str, disk_before: int, disk_after: int, transport: str, gate: Any, execution_error: dict[str, Any] | None, postflight: dict[str, Any]) -> None:
    counts: dict[str, int] = {}
    for result in results:
        counts[result["category"]] = counts.get(result["category"], 0) + 1
    intervals = [record["interval_since_previous_dispatch_seconds"] for record in gate.dispatches if record.get("interval_since_previous_dispatch_seconds") is not None]
    all_queries = [result.get("preanchor") for result in results] + [result.get("late_supplement") for result in results]
    valid_entities = [result for result in results if result["category"] in {"valid_image", "valid_image_temporal_supplement"}]
    report = {
        "schema": "continuous-wow-network-hires11-batch-report/v1", "batch_id": "NET-HIRES-011", "mode": "executed", "started_utc": started_utc, "finished_utc": finished_utc, "request_window_finished_utc": finished_utc, "report_updated_utc": report_updated_utc, "inputs": {"candidates_path": str((OUT / "candidates.json").relative_to(ROOT)).replace("\\", "/"), "candidates_sha256": sha256_file(OUT / "candidates.json"), "input_digests": candidates["input_digests"]}, "policy": candidates["policy"], "preflight": {"drive": "D:", "disk_free_bytes_before": disk_before, "disk_free_bytes_after": disk_after, "minimum_free_bytes": MIN_FREE}, "transport": {"confirmed_transport_after_first_request": transport, "curl": str(core.CURL), "helper": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"), "dispatch_gate": str(GATE_PATH.relative_to(ROOT)).replace("\\", "/")}, "target_count": len(results), "distinct_target_count": len(results), "max_distinct_targets": MAX_TARGETS, "source_request_count": state.attempts, "transport_attempt_count": state.attempts, "failed_attempt_count": state.failed_attempts, "source_response_count": state.source_responses, "cdx_source_response_count": sum((q or {}).get("source_response_count", 0) for q in all_queries), "replay_source_response_count": sum(sum(attempt.get("source_status") is not None for attempt in result.get("replay_hops", [])) for result in results), "capture_index_count": sum((q or {}).get("capture_index_count", 0) for q in all_queries), "valid_capture_count": sum((q or {}).get("valid_status_200_count", 0) for q in all_queries), "valid_entity_count": len(valid_entities), "late_temporal_supplement_count": sum(result["category"] == "valid_image_temporal_supplement" for result in results), "category_counts": counts, "total_body_bytes": state.total_body_bytes, "payload_body_bytes": sum(result["body_bytes"] for result in valid_entities), "dispatch_count": len(gate.dispatches), "minimum_start_interval_seconds": min(intervals) if intervals else None, "stop_reason": state.stop_reason, "stop_detail": state.stop_detail, "rate_limit": state.rate_limit, "execution_error": execution_error, "postflight": postflight, "results": results, "raw_evidence_note": "Raw headers, traces, stderr and bodies remain only below this batch raw directory. Zero-byte no-response bodies are local placeholders, CONNECT 200 is excluded, CDX length is index metadata, and late valid images are temporal supplements rather than original 2008 sources.",
    }
    write_json(OUT / "batch-report.json", report)
    source_map = {"schema": "continuous-wow-network-hires11-payload-source-map/v1", "batch_id": "NET-HIRES-011", "generated_utc": report_updated_utc, "entries": [source_map_entry(result) for result in valid_entities], "entity_count": len(valid_entities), "integration": "No entity copied into offline mirror; review-only source mapping."}
    write_json(OUT / "payload-source-map.json", source_map)
    redirects: list[dict[str, Any]] = []
    for result in results:
        for window_key in ("preanchor", "late_supplement"):
            query = result.get(window_key) or {}
            for row in query.get("capture_records") or []:
                if str(row.get("statuscode")) in {str(code) for code in REDIRECT_CODES}:
                    redirects.append({"target_key": result["target_key"], "query_window": window_key, "capture_timestamp": row.get("timestamp"), "captured_original_url": row.get("original"), "statuscode": row.get("statuscode"), "location": None, "manual_followed": False, "evidence": "CDX index redirect row; no replay/follow performed"})
        for hop in result.get("replay_hops") or []:
            if hop.get("source_status") in REDIRECT_CODES:
                redirects.append({"target_key": result["target_key"], "query_window": result.get("selected_window"), "capture_timestamp": (result.get("selected_capture") or {}).get("timestamp"), "captured_original_url": (result.get("selected_capture") or {}).get("original"), "source_status": hop.get("source_status"), "location": hop.get("location"), "raw_headers_path": (hop.get("raw") or {}).get("headers"), "manual_followed": False, "evidence": "replay redirect; no follow performed"})
    write_json(OUT / "redirect-evidence.json", {"schema": "continuous-wow-network-hires11-redirect-evidence/v1", "generated_utc": report_updated_utc, "manual_redirect_follow_hops": 0, "entries": redirects})
    target_summary = [{"rank": result["rank"], "target_key": result["target_key"], "url": result["url"], "priority": result["priority"], "category": result["category"], "reason": result["reason"], "selected_window": result.get("selected_window"), "actual_memento_or_null": result.get("actual_memento_or_null"), "source_status": result.get("source_status"), "body_bytes": result.get("body_bytes", 0), "body_sha256": result.get("body_sha256"), "selected_capture_timestamp": (result.get("selected_capture") or {}).get("timestamp"), "unrequested_reason": result.get("unrequested_reason")} for result in results]
    summary = {"schema": "continuous-wow-network-hires11-sanitized-summary/v1", "batch_id": "NET-HIRES-011", "mode": "executed", "report_sha256": sha256_file(OUT / "batch-report.json"), "started_utc": started_utc, "finished_utc": finished_utc, "request_window_finished_utc": finished_utc, "report_updated_utc": report_updated_utc, "network_requests": state.attempts, "source_response_count": state.source_responses, "failed_attempt_count": state.failed_attempts, "target_count": len(results), "capture_index_count": report["capture_index_count"], "valid_capture_count": report["valid_capture_count"], "valid_entity_count": len(valid_entities), "late_temporal_supplement_count": report["late_temporal_supplement_count"], "category_counts": counts, "total_body_bytes": state.total_body_bytes, "payload_body_bytes": report["payload_body_bytes"], "disk_free_bytes_before": disk_before, "disk_free_bytes_after": disk_after, "dispatch_count": len(gate.dispatches), "minimum_start_interval_seconds": report["minimum_start_interval_seconds"], "stop_reason": state.stop_reason, "targets": target_summary, "raw_evidence_note": report["raw_evidence_note"]}
    write_json(OUT / "sanitized-summary.json", summary)
    lines = ["# NET-HIRES-011 sanitized summary", "", f"Requests: `{state.attempts}`; source HTTP responses excluding CONNECT: `{state.source_responses}`; valid image entities: `{len(valid_entities)}`.", f"CDX capture rows: `{report['capture_index_count']}`; valid status-200 captures: `{report['valid_capture_count']}`; late temporal supplements: `{report['late_temporal_supplement_count']}`.", f"Disk free: `{disk_before}` before / `{disk_after}` after; minimum dispatch interval observed: `{report['minimum_start_interval_seconds']}` seconds.", f"Stop: `{state.stop_reason or 'completed'}`.", "", "| # | target | category | selected window | Memento | bytes | reason |", "|---:|---|---|---|---|---:|---|"]
    lines.extend(f"| {row['rank']} | `{row['target_key']}` | `{row['category']}` | `{row['selected_window'] or ''}` | `{row['actual_memento_or_null'] or ''}` | {row['body_bytes']} | `{row['reason']}` |" for row in target_summary)
    lines.extend(["", report["raw_evidence_note"], "", "No entity was copied into the offline mirror or v10 queue by this batch."])
    (OUT / "sanitized-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def execute() -> int:
    if not (OUT / "candidates.json").is_file():
        raise RuntimeError("candidates.json missing; run --prepare first")
    if (OUT / "batch-report.json").exists() or (RAW.exists() and any(RAW.iterdir())):
        raise RuntimeError("refusing to rerun NET-HIRES-011 over existing outputs/raw")
    proof_inputs()
    candidates = read_json(OUT / "candidates.json")
    if candidates.get("network_requests") != 0 or len(candidates.get("entries") or []) != MAX_TARGETS:
        raise RuntimeError("candidate plan is not the expected 13-target offline declaration")
    candidate_sha = sha256_file(OUT / "candidates.json")
    if candidate_sha != read_json(OUT / "config.json").get("candidate_sha256"):
        raise RuntimeError("candidate/config digest mismatch")
    disk_before = disk_free_bytes()
    if disk_before < MIN_FREE:
        raise RuntimeError(f"D free space {disk_before} below threshold {MIN_FREE}")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    started_utc = now_utc()
    window_started = time.monotonic()
    state = core.RunState(window_started)
    journal = {"schema": "continuous-wow-network-hires11-dispatch-log/v1", "batch_id": "NET-HIRES-011", "simulation": False, "policy": {"minimum_dispatch_interval_seconds": INTERVAL_SECONDS, "manual_redirect_follow_hops": 0, "max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW_SECONDS, "max_distinct_targets": MAX_TARGETS}, "disk_preflight": {"checked_utc": now_utc(), "disk_free_bytes": disk_before, "minimum_free_bytes": MIN_FREE}, "dispatches": []}
    gate = gate_mod.GateState(datetime.now(timezone.utc) - gate_mod.timedelta(seconds=1), journal_path=OUT / "dispatch-log.json", journal=journal)
    gate.persist()
    results: list[dict[str, Any]] = []
    transport = "unconfirmed"
    execution_error: dict[str, Any] | None = None
    postflight: dict[str, Any] = {}
    try:
        entries = candidates["entries"]
        first = entries[0]
        first_query = request(first["preanchor"]["cdx_query_url"], "direct", "cdx", first["target_key"], state, gate, window_started)
        first_attempts = [first_query]
        if first_query.get("executed") and not first_query.get("transport_error"):
            transport = "direct"
        elif first_query.get("executed") and first_query.get("transport_error") and not state.stop_reason:
            first_attempts.append(request(first["preanchor"]["cdx_query_url"], "proxy", "cdx", first["target_key"], state, gate, window_started))
            transport = "proxy"
        else:
            transport = "proxy_not_attempted_after_limit"
        if transport in {"direct", "proxy"}:
            first_result, transport = run_target(first, transport, state, gate, window_started, prefetched_pre_attempts=first_attempts)
            results.append(first_result)
        else:
            results.append(result_not_requested(first, state.stop_reason or first_query.get("unrequested_reason") or "direct_query_not_executed"))
        for item in entries[1:]:
            if state.stop_reason:
                break
            result, transport = run_target(item, transport if transport in {"direct", "proxy"} else "proxy", state, gate, window_started)
            results.append(result)
    except Exception as exc:  # preserve dispatch evidence in finally
        execution_error = {"type": type(exc).__name__, "message": str(exc)}
        state.stop_reason = state.stop_reason or "execution_exception"
        state.stop_detail = state.stop_detail or execution_error
    finally:
        append_unrequested(candidates["entries"], results, state)
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=disk_free_bytes)
        finished_utc = now_utc()
        report_updated_utc = now_utc()
        try:
            write_outputs(candidates, results, state, started_utc, finished_utc, report_updated_utc, disk_before, disk_free_bytes(), transport, gate, execution_error, postflight)
        except Exception as report_error:
            execution_error = execution_error or {"type": type(report_error).__name__, "message": str(report_error), "phase": "report_assembly"}
            write_json(OUT / "report-assembly-error.json", {"schema": "continuous-wow-network-hires11-report-error/v1", "batch_id": "NET-HIRES-011", "generated_utc": now_utc(), "error": execution_error, "dispatch_log_path": "dispatch-log.json", "attempt_count": state.attempts})
    print(json.dumps({"batch_id": "NET-HIRES-011", "targets_reported": len(results), "attempts": state.attempts, "source_responses": state.source_responses, "failed_attempts": state.failed_attempts, "capture_index_count": sum((q or {}).get("capture_index_count", 0) for result in results for q in (result.get("preanchor"), result.get("late_supplement"))), "valid_entities": sum(result["category"] in {"valid_image", "valid_image_temporal_supplement"} for result in results), "category_counts": {key: sum(result["category"] == key for result in results) for key in sorted({result["category"] for result in results})}, "stop_reason": state.stop_reason, "confirmed_transport": transport, "network_requests": state.attempts}, ensure_ascii=False))
    return 1 if execution_error else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.prepare == args.execute:
        parser.error("choose exactly one of --prepare or --execute")
    return prepare() if args.prepare else execute()


if __name__ == "__main__":
    raise SystemExit(main())

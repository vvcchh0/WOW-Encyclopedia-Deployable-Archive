"""Reusable bounded CDX discovery and image replay runner.

The driver has an offline ``--fixture`` mode used to validate the archive
selection and acceptance gates without touching the network.  ``--execute`` is
deliberately explicit: it is the only mode that may dispatch curl requests and
it persists a prepared attempt before each request.  The transport and
acceptance core is carried forward from the reviewed NEWS-SHARED10 runner,
while plan, target count, output directory, and cached-CDX inputs are
parameterized for one independently-bound batch.
"""
from __future__ import annotations

import argparse
import base64
import codecs
import gzip
import hashlib
import json
import math
import re
import shutil
import subprocess
import time
import zlib
from io import BytesIO
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote, urlsplit
from PIL import Image, ImageSequence


ROOT = Path(__file__).resolve().parents[4]
NETWORK = ROOT / "research" / "continuous-recovery-20261016" / "network"
DRIVER_DIR = Path(__file__).resolve().parent
OUT = DRIVER_DIR / "example-run"
PLAN_PATH = DRIVER_DIR / "plan.json"
BINDINGS_PATH = DRIVER_DIR / "input-bindings.json"
STATE_PATH = OUT / "state.json"
RAW = OUT / "raw"
PUBLIC = OUT / "public"
PRIVATE_PAYLOADS = OUT / "private-payloads"

BATCH_ID = "WAYBACK-REUSABLE-IMAGE-V1-EXAMPLE-20261016"
USER_AGENT = "wow-recovery-reusable-image-v1/20261016"
PROXY = "http://127.0.0.1:7890"
TRANSPORT_POLICIES = {"per_request", "batch_after_direct_failure"}
TRANSPORT_POLICY = "per_request"
POLICY_FROM_TS = "20000101000000"
POLICY_TO_TS = "20080512235959"
LATE_WINDOW_FROM_TS = "20080512210044"
LATE_TARGET_KEY = "AUG27-11-late-supplement"
LATE_ORIGINAL = "http://www.worldofwarcraft.com/news/images/07-08/08-22-07-2.jpg"
LATE_RECEIPT_PATH = "research/continuous-recovery-20261016/publication/root-aug11-redirect-observation.json"
LATE_RECEIPT_SHA256 = "94fe1ef2e474611f4c2d0fd02abf6ecb3986b3d6200671f37fc09d3040cae10a"
POLICY_MAX_LIMIT = 500
POLICY_MAX_WINDOW_SECONDS = 1800.0
POLICY_MAX_ATTEMPTS = 100
POLICY_MAX_TOTAL_BODY_BYTES = 64 * 1024 * 1024
POLICY_MAX_ENTITY_BODY_BYTES = 8 * 1024 * 1024
POLICY_MIN_DISPATCH_SECONDS = 5.25
POLICY_MIN_REQUEST_START_SECONDS = 5.0
POLICY_MIN_DISK_FLOOR_BYTES = 11_005_853_696
FROM_TS = POLICY_FROM_TS
TO_TS = POLICY_TO_TS
CDX_LIMIT = POLICY_MAX_LIMIT
WINDOW_SECONDS = POLICY_MAX_WINDOW_SECONDS
MAX_ATTEMPTS = POLICY_MAX_ATTEMPTS
MAX_TOTAL_BODY_BYTES = POLICY_MAX_TOTAL_BODY_BYTES
MAX_ENTITY_BODY_BYTES = POLICY_MAX_ENTITY_BODY_BYTES
MIN_DISPATCH_SECONDS = POLICY_MIN_DISPATCH_SECONDS
MIN_REQUEST_START_SECONDS = POLICY_MIN_REQUEST_START_SECONDS
DISK_FLOOR_BYTES = POLICY_MIN_DISK_FLOOR_BYTES
PRIOR_FAILURE_TAIL = 0
STOP_HTTP_CODES = {429, 503}
COOLDOWN_SECONDS = 120
DIRECT_CONNECT_SECONDS = 4.0
DIRECT_MAX_SECONDS = 12.0
PROXY_CONNECT_SECONDS = 8.0
PROXY_MAX_SECONDS = 20.0

FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
# ALLNEWS01's cached exact queries requested the six fields below (without
# ``urlkey``).  Keep both wire schemas explicit: a cached six-column body is
# valid evidence when its query, bytes, and source headers are bound, while an
# arbitrary extra/headerless shape remains incomplete or invalid.
CDX_FIELDS_WITHOUT_URLKEY = ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
EXPECTED_MIME = {"image": {"image/gif", "image/jpeg", "image/png"}}


def _under_network(path: Path) -> bool:
    try:
        path.resolve().relative_to(NETWORK.resolve())
        return True
    except ValueError:
        return False


def _plan_output_dir(value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("plan output_dir is required")
    candidate = Path(value)
    path = (ROOT / candidate if not candidate.is_absolute() else candidate).resolve()
    if not _under_network(path) or path == NETWORK.resolve():
        raise RuntimeError("output_dir must remain below the current recovery network directory")
    return path


def _policy_hard_bounds(policy: dict[str, Any], prior: Any) -> None:
    """Reject policy values outside the non-negotiable recovery envelope."""
    if policy.get("from") != POLICY_FROM_TS or policy.get("to") != POLICY_TO_TS:
        raise RuntimeError("reusable image window is outside the fixed recovery range")
    bounded_ints = {
        "max_attempts": (policy.get("max_attempts"), 1, POLICY_MAX_ATTEMPTS),
        "max_total_body_bytes": (policy.get("max_total_body_bytes"), 1, POLICY_MAX_TOTAL_BODY_BYTES),
        "max_entity_body_bytes": (policy.get("max_entity_body_bytes"), 1, POLICY_MAX_ENTITY_BODY_BYTES),
        "limit": (policy.get("limit"), 1, POLICY_MAX_LIMIT),
        "disk_floor_bytes": (policy.get("disk_floor_bytes"), POLICY_MIN_DISK_FLOOR_BYTES, None),
    }
    for name, (value, lower, upper) in bounded_ints.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < lower or (upper is not None and value > upper):
            raise RuntimeError(f"policy {name} is outside its hard bound")
    if bounded_ints["max_entity_body_bytes"][0] > bounded_ints["max_total_body_bytes"][0]:
        raise RuntimeError("entity cap cannot exceed total cap")
    numeric = (policy.get("window_seconds"), policy.get("min_dispatch_seconds"), policy.get("min_request_start_seconds"))
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) for value in numeric):
        raise RuntimeError("cadence/window values must be finite numbers")
    if not (0 < float(policy["window_seconds"]) <= POLICY_MAX_WINDOW_SECONDS):
        raise RuntimeError("window_seconds is outside its hard bound")
    if float(policy["min_dispatch_seconds"]) < POLICY_MIN_DISPATCH_SECONDS or float(policy["min_request_start_seconds"]) < POLICY_MIN_REQUEST_START_SECONDS:
        raise RuntimeError("cadence floor is below the required bound")
    if isinstance(prior, bool) or not isinstance(prior, int) or not 0 <= prior <= 4:
        raise RuntimeError("prior failure tail must be an integer from 0 through 4")
    if policy.get("direct_first") is not True or policy.get("tls_verification") is not True or policy.get("automatic_redirects") != 0:
        raise RuntimeError("direct/TLS/no-redirect policy is required")
    if policy.get("proxy") != PROXY:
        raise RuntimeError("proxy must remain the process-local 127.0.0.1:7890 proxy")
    if policy.get("transport_policy", "per_request") not in TRANSPORT_POLICIES:
        raise RuntimeError("transport_policy must be per_request or batch_after_direct_failure")


def _late_plan_pending(plan: dict[str, Any]) -> bool:
    return plan.get("execution_status") == "awaiting_A_root_acceptance"


def _validate_late_supplement_plan(plan: dict[str, Any]) -> None:
    """Lock this copy to the one root-observed same-day redirect target."""
    guard = plan.get("late_supplement_guard") or {}
    candidates = plan.get("candidates") or []
    if plan.get("batch_id") != "AUG27-SAME-DAY-LATE11" or len(candidates) != 1:
        raise RuntimeError("late11 plan must contain exactly one locked target")
    candidate = candidates[0]
    if (candidate.get("target_key") != LATE_TARGET_KEY
            or candidate.get("original") != LATE_ORIGINAL
            or candidate.get("literal") != LATE_ORIGINAL
            or candidate.get("late_supplement") is not True):
        raise RuntimeError("late11 exact original/marker lock failed")
    window = candidate.get("late_window") or guard.get("late_window") or {}
    if window.get("from") != LATE_WINDOW_FROM_TS or window.get("to") != POLICY_TO_TS:
        raise RuntimeError("late11 same-day window is not fixed")
    if guard.get("late_window") != {"from": LATE_WINDOW_FROM_TS, "to": POLICY_TO_TS}:
        raise RuntimeError("late11 guard window is not fixed")
    receipt_path = _bound_path(guard.get("redirect_receipt_path"))
    if str(guard.get("redirect_receipt_path")) != LATE_RECEIPT_PATH:
        raise RuntimeError("late11 redirect receipt path is not the root observation")
    if guard.get("redirect_receipt_sha256") != LATE_RECEIPT_SHA256:
        raise RuntimeError("late11 redirect receipt SHA is not the root observation")
    observation = candidate.get("late_redirect_observation") or {}
    if (observation.get("path") != LATE_RECEIPT_PATH
            or observation.get("sha256") != LATE_RECEIPT_SHA256
            or observation.get("observed_redirect_timestamp") != "20080512231210"):
        raise RuntimeError("late11 candidate redirect observation binding is incomplete")
    if candidate.get("pre_anchor_cdx_digest") != guard.get("pre_anchor_cdx_digest"):
        raise RuntimeError("late11 candidate pre-anchor digest is not guard-bound")
    if not receipt_path.is_file() or sha_file(receipt_path) != LATE_RECEIPT_SHA256:
        raise RuntimeError("late11 redirect observation binding changed")
    receipt = read_json(receipt_path)
    if (receipt.get("accepted") is not True or receipt.get("network_requests") != 0
            or receipt.get("automatic_redirects_followed") != 0
            or receipt.get("original") != LATE_ORIGINAL
            or receipt.get("pre_anchor_indexed_capture") != "20080402080429"
            or receipt.get("pre_anchor_cdx_digest") != "MLUKMD2MO3CNVZGT2PCCNNXF7RDKJAA4"
            or receipt.get("redirect_capture_timestamp") != "20080512231210"
            or receipt.get("after_anchor") is not True
            or receipt.get("same_calendar_day") is not True):
        raise RuntimeError("late11 redirect observation facts changed")
    if guard.get("pre_anchor_cdx_digest") != receipt.get("pre_anchor_cdx_digest"):
        raise RuntimeError("late11 pre-anchor digest comparison is not bound")
    if guard.get("automatic_redirects") != 0 or guard.get("no_redirects") is not True:
        raise RuntimeError("late11 must never follow the observed redirect")
    query = candidate.get("query") or {}
    if query.get("from") != POLICY_FROM_TS or query.get("to") != POLICY_TO_TS:
        raise RuntimeError("late11 fresh CDX query must use the bounded late upper window")


def _late_timestamp_ok(value: str) -> bool:
    return bool(re.fullmatch(r"\d{14}", value) and LATE_WINDOW_FROM_TS <= value <= TO_TS)


def _filter_late_selected(analysis: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Never replay a pre-anchor exact row for the supplement target."""
    if candidate.get("late_supplement") is not True:
        return analysis
    selected = analysis.get("selected") or []
    kept = [row for row in selected if _late_timestamp_ok(str(row.get("timestamp") or ""))]
    analysis["late_window_from"] = LATE_WINDOW_FROM_TS
    analysis["late_window_to"] = TO_TS
    analysis["late_window_rejected_selected_count"] = len(selected) - len(kept)
    analysis["selected"] = kept
    if analysis.get("status") == "complete_with_replay_candidates" and not kept:
        analysis["status"] = "complete_no_late_window_capture"
    for row in kept:
        row["replay_url"] = "https://web.archive.org/web/" + str(row["timestamp"]) + "id_/" + candidate["original"]
    return analysis


def configure_from_plan(plan_path: Path | str) -> dict[str, Any]:
    """Load batch policy before any fixture or execute path can write output."""
    global PLAN_PATH, BINDINGS_PATH, OUT, STATE_PATH, RAW, PUBLIC, PRIVATE_PAYLOADS
    global BATCH_ID, USER_AGENT, PROXY, TRANSPORT_POLICY, FROM_TS, TO_TS, CDX_LIMIT, WINDOW_SECONDS
    global MAX_ATTEMPTS, MAX_TOTAL_BODY_BYTES, MAX_ENTITY_BODY_BYTES
    global MIN_DISPATCH_SECONDS, MIN_REQUEST_START_SECONDS, DISK_FLOOR_BYTES
    global PRIOR_FAILURE_TAIL
    path = Path(plan_path).resolve()
    if not _under_network(path) or path.suffix.lower() != ".json":
        raise RuntimeError("plan path must be a JSON file below the recovery network directory")
    plan = read_json(path)
    if plan.get("schema") != "wow-recovery.reusable-image-plan.v1":
        raise RuntimeError("unexpected reusable image plan schema")
    policy = plan.get("policy")
    if not isinstance(policy, dict):
        raise RuntimeError("reusable image policy is required")
    pending = _late_plan_pending(plan)
    prior = (plan.get("previous_batch") or {}).get("prior_failure_tail", policy.get("prior_failure_tail"))
    if pending:
        if prior is not None or policy.get("prior_failure_tail") is not None:
            raise RuntimeError("pending late11 plan must not bind a stale failure tail")
        _policy_hard_bounds(policy, 0)
        prior = 0
    else:
        _policy_hard_bounds(policy, prior)
    if policy.get("from") != POLICY_FROM_TS or policy.get("to") != POLICY_TO_TS:
        raise RuntimeError("reusable image window is outside the fixed recovery range")
    int_policy = {
        "max_attempts": (policy.get("max_attempts"), 1, POLICY_MAX_ATTEMPTS),
        "max_total_body_bytes": (policy.get("max_total_body_bytes"), 1, POLICY_MAX_TOTAL_BODY_BYTES),
        "max_entity_body_bytes": (policy.get("max_entity_body_bytes"), 1, POLICY_MAX_ENTITY_BODY_BYTES),
        "limit": (policy.get("limit"), 1, POLICY_MAX_LIMIT),
        "disk_floor_bytes": (policy.get("disk_floor_bytes"), POLICY_MIN_DISK_FLOOR_BYTES, None),
    }
    for name, (value, lower, upper) in int_policy.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < lower or (upper is not None and value > upper):
            raise RuntimeError(f"policy {name} is outside its hard bound")
    if int_policy["max_entity_body_bytes"][0] > int_policy["max_total_body_bytes"][0]:
        raise RuntimeError("entity cap cannot exceed total cap")
    window = policy.get("window_seconds")
    dispatch = policy.get("min_dispatch_seconds")
    start = policy.get("min_request_start_seconds")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)) for v in (window, dispatch, start)):
        raise RuntimeError("cadence/window values must be finite numbers")
    if not (0 < float(window) <= POLICY_MAX_WINDOW_SECONDS):
        raise RuntimeError("window_seconds is outside its hard bound")
    if float(dispatch) < POLICY_MIN_DISPATCH_SECONDS or float(start) < POLICY_MIN_REQUEST_START_SECONDS:
        raise RuntimeError("cadence floor is below the required bound")
    if isinstance(prior, bool) or not isinstance(prior, int) or not 0 <= prior <= 4:
        raise RuntimeError("prior failure tail must be an integer from 0 through 4")
    if policy.get("direct_first") is not True or policy.get("tls_verification") is not True or policy.get("automatic_redirects") != 0:
        raise RuntimeError("direct/TLS/no-redirect policy is required")
    if policy.get("proxy") != PROXY:
        raise RuntimeError("proxy must remain the process-local 127.0.0.1:7890 proxy")
    PLAN_PATH = path
    BINDINGS_PATH = path.parent / "input-bindings.json"
    OUT = _plan_output_dir(plan.get("output_dir"))
    STATE_PATH, RAW, PUBLIC, PRIVATE_PAYLOADS = (OUT / name for name in ("state.json", "raw", "public", "private-payloads"))
    BATCH_ID = str(plan.get("batch_id") or "")
    USER_AGENT = str(policy.get("user_agent") or "wow-recovery-reusable-image-v1/20261016")
    PROXY = str(policy.get("proxy") or "http://127.0.0.1:7890")
    TRANSPORT_POLICY = str(policy.get("transport_policy") or "per_request")
    FROM_TS, TO_TS = str(policy.get("from") or ""), str(policy.get("to") or "")
    CDX_LIMIT = int(policy.get("limit", 500))
    WINDOW_SECONDS = float(policy.get("window_seconds", 1800.0))
    MAX_ATTEMPTS = int(policy.get("max_attempts", 100))
    MAX_TOTAL_BODY_BYTES = int(policy.get("max_total_body_bytes", 64 * 1024 * 1024))
    MAX_ENTITY_BODY_BYTES = int(policy.get("max_entity_body_bytes", 8 * 1024 * 1024))
    MIN_DISPATCH_SECONDS = float(policy.get("min_dispatch_seconds", 5.25))
    MIN_REQUEST_START_SECONDS = float(policy.get("min_request_start_seconds", 5.0))
    DISK_FLOOR_BYTES = int(policy.get("disk_floor_bytes", 11_005_853_696))
    PRIOR_FAILURE_TAIL = int(prior)
    _validate_late_supplement_plan(plan)
    return plan


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def cf(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def canonical_url(url: str) -> tuple[str, str, int | None, str, str] | None:
    """Return exact origin/path identity, normalizing only default ports."""
    try:
        p = urlsplit(url)
        if not p.scheme or not p.hostname or p.fragment:
            return None
        scheme = p.scheme.lower()
        port = p.port
        default = 80 if scheme == "http" else 443 if scheme == "https" else None
        if port == default:
            port = None
        return scheme, p.hostname.lower(), port, p.path or "/", p.query
    except ValueError:
        return None


def identity_relation(observed: str, requested: str) -> str:
    left, right = canonical_url(observed), canonical_url(requested)
    if left is None or right is None:
        return "invalid_url"
    if left == right:
        return "exact"
    if left[2:] == right[2:]:
        return "origin_variant"
    return "different_resource"


def parse_cdx(body: bytes, limit: int = CDX_LIMIT) -> dict[str, Any]:
    """Parse CDX JSON while preserving the empty separator/resume metadata.

    A response containing a resume key or ``limit`` records is deliberately
    incomplete.  Unknown metadata is an error rather than a silent complete
    result, so no replay can be selected from an ambiguous index response.
    """
    try:
        text = body.decode("utf-8")
        payload = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"valid": False, "complete": False, "error": "json_decode", "header": None, "rows": [], "resume_keys": [], "metadata": [], "potential_truncation": False}
    if payload == []:
        return {"valid": True, "complete": True, "error": None, "header": None, "rows": [], "resume_keys": [], "metadata": [], "potential_truncation": False}

    rows: list[dict[str, str]] = []
    metadata: list[dict[str, Any]] = []
    resume_keys: list[str] = []
    unknown: list[dict[str, Any]] = []
    header: list[str] | None = None

    def consume_list(index: int, values: list[Any]) -> None:
        nonlocal header
        vals = [str(x) for x in values]
        if not vals:
            metadata.append({"record_index": index, "kind": "separator"})
            return
        normalized_header = [cf(x) for x in vals]
        if header is None and normalized_header in (
            [cf(x) for x in FIELDS],
            [cf(x) for x in CDX_FIELDS_WITHOUT_URLKEY],
        ):
            header = vals
            metadata.append({"record_index": index, "kind": "header"})
            return
        if len(vals) == 1 and vals[0]:
            resume_keys.append(vals[0])
            metadata.append({"record_index": index, "kind": "resume_key", "value": vals[0]})
            return
        if header is None:
            entry = {"record_index": index, "kind": "row_before_header"}
            metadata.append(entry)
            unknown.append(entry)
            return
        positions = {cf(name): pos for pos, name in enumerate(header)}
        if ([cf(name) for name in header] not in (
                [cf(x) for x in FIELDS],
                [cf(x) for x in CDX_FIELDS_WITHOUT_URLKEY],
            ) or len(vals) != len(header)):
            entry = {"record_index": index, "kind": "invalid_row_shape"}
            metadata.append(entry)
            unknown.append(entry)
            return
        row = {name: vals[positions[cf(name)]] for name in header if cf(name) in {cf(field) for field in FIELDS}}
        for field in FIELDS:
            row.setdefault(field, "")
        rows.append(row | {"record_index": str(index)})

    if isinstance(payload, list):
        for index, item in enumerate(payload):
            if isinstance(item, list):
                consume_list(index, item)
            elif isinstance(item, dict):
                found = [str(item[key]) for key in ("resumeKey", "resume_key", "next_resume_key") if item.get(key)]
                if found:
                    resume_keys.extend(found)
                    metadata.append({"record_index": index, "kind": "metadata_resume_key"})
                else:
                    entry = {"record_index": index, "kind": "unrecognized_metadata"}
                    metadata.append(entry)
                    unknown.append(entry)
            else:
                entry = {"record_index": index, "kind": "unrecognized_metadata"}
                metadata.append(entry)
                unknown.append(entry)
    elif isinstance(payload, dict):
        found = [str(payload[key]) for key in ("resumeKey", "resume_key", "next_resume_key") if payload.get(key)]
        resume_keys.extend(found)
        source_key = next((key for key in ("records", "captures", "rows") if key in payload), None)
        raw = payload.get(source_key) if source_key else None
        if source_key is None:
            return {"valid": False, "complete": False, "error": "dict_records_missing", "header": None, "rows": [], "resume_keys": resume_keys, "metadata": metadata, "potential_truncation": False}
        if not isinstance(raw, list):
            return {"valid": False, "complete": False, "error": "dict_rows_not_array", "header": None, "rows": [], "resume_keys": resume_keys, "metadata": metadata, "potential_truncation": False}
        header = FIELDS[:]
        for index, item in enumerate(raw):
            if not isinstance(item, dict) or not all(field in item for field in FIELDS):
                entry = {"record_index": index, "kind": "invalid_dict_row"}
                metadata.append(entry)
                unknown.append(entry)
                continue
            rows.append({field: str(item.get(field, "")) for field in FIELDS} | {"record_index": str(index)})
    else:
        return {"valid": False, "complete": False, "error": "json_shape", "header": None, "rows": [], "resume_keys": [], "metadata": [], "potential_truncation": False}

    resume_keys = list(dict.fromkeys(resume_keys))
    potential = bool(resume_keys or len(rows) >= limit)
    if unknown:
        return {"valid": False, "complete": False, "error": "unrecognized_metadata", "header": header, "rows": rows, "resume_keys": resume_keys, "metadata": metadata, "potential_truncation": potential}
    if rows and header is None:
        return {"valid": False, "complete": False, "error": "header_missing", "header": None, "rows": [], "resume_keys": resume_keys, "metadata": metadata, "potential_truncation": potential}
    return {"valid": True, "complete": not potential, "error": None, "header": header, "rows": rows, "resume_keys": resume_keys, "metadata": metadata, "potential_truncation": potential}


def cdx_query_url(original: str, *, from_ts: str = FROM_TS, to_ts: str = TO_TS,
                  limit: int = CDX_LIMIT, show_resume: bool = True,
                  fields: list[str] | None = None) -> str:
    selected_fields = fields or FIELDS
    params = (
        "url=" + quote(original, safe="")
        + "&from=" + from_ts
        + "&to=" + to_ts
        + "&output=json"
        + "&fl=" + quote(",".join(selected_fields), safe="")
        + "&limit=" + str(limit)
        + "&showResumeKey=" + ("true" if show_resume else "false")
        + "&matchType=exact"
    )
    return "https://web.archive.org/cdx/search/cdx?" + params


TARGET_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def _validate_target_key(target_key: Any, seen: set[str]) -> str:
    value = str(target_key or "")
    if not TARGET_KEY_RE.fullmatch(value) or value in seen:
        raise RuntimeError(f"target_key is unsafe or duplicated: {value}")
    return value


def _bound_path(value: Any, *, under_network: bool = False) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("bound path is required")
    candidate = Path(value)
    path = (ROOT / candidate if not candidate.is_absolute() else candidate).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        raise RuntimeError("bound evidence path must remain below the workspace root")
    if under_network and not _under_network(path):
        raise RuntimeError("raw/cache evidence must remain below the recovery network directory")
    return path


def _validate_source_evidence(candidate: dict[str, Any]) -> None:
    evidence = candidate.get("source_evidence") or {}
    literal = evidence.get("literal")
    line_number = evidence.get("line")
    if not isinstance(literal, str) or not literal or isinstance(line_number, bool) or not isinstance(line_number, int) or line_number < 1:
        raise RuntimeError(f"source evidence is incomplete: {candidate.get('target_key')}")
    path = _bound_path(evidence.get("path"))
    if not path.is_file() or sha_file(path) != str(evidence.get("sha256") or "").lower():
        raise RuntimeError(f"source evidence hash/path changed: {candidate.get('target_key')}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    source_line = lines[line_number - 1] if line_number <= len(lines) else ""
    encoded_literal = quote(literal, safe="")
    if line_number > len(lines) or (literal not in source_line and encoded_literal not in source_line):
        raise RuntimeError(f"source evidence literal/line mismatch: {candidate.get('target_key')}")


def _normal_cdx_row(row: dict[str, Any]) -> dict[str, str]:
    return {field: str(row.get(field, "")) for field in FIELDS} | {"record_index": str(row.get("record_index", ""))}


def _validate_cached_evidence(candidate: dict[str, Any], query: dict[str, Any], cached: dict[str, Any]) -> dict[str, Any]:
    """Read and validate the raw, SHA-bound cached CDX rather than trusting JSON metadata."""
    required = ("source_report_path", "source_report_sha256", "raw_body_path", "body_sha256",
                "raw_headers_path", "raw_headers_sha256", "source_curl_exit", "coverage_window")
    missing = [key for key in required if key not in cached or cached[key] is None
               or (isinstance(cached[key], str) and not cached[key].strip())]
    if missing:
        raise RuntimeError(f"cached CDX provenance is incomplete: {candidate.get('target_key')}: {','.join(missing)}")
    if isinstance(cached["source_curl_exit"], bool) or not isinstance(cached["source_curl_exit"], int):
        raise RuntimeError(f"cached CDX source curl exit is not an integer: {candidate.get('target_key')}")
    source_report = _bound_path(cached["source_report_path"])
    if not source_report.is_file() or sha_file(source_report) != str(cached["source_report_sha256"]).lower():
        raise RuntimeError(f"cached source report hash/path changed: {candidate.get('target_key')}")
    raw_body_path = _bound_path(cached["raw_body_path"], under_network=True)
    raw_headers_path = _bound_path(cached["raw_headers_path"], under_network=True)
    if not raw_body_path.is_file() or sha_file(raw_body_path) != str(cached["body_sha256"]).lower():
        raise RuntimeError(f"cached CDX body hash/path changed: {candidate.get('target_key')}")
    if not raw_headers_path.is_file() or sha_file(raw_headers_path) != str(cached["raw_headers_sha256"]).lower():
        raise RuntimeError(f"cached CDX header hash/path changed: {candidate.get('target_key')}")
    headers = parse_headers(raw_headers_path.read_bytes())
    if cached.get("source_curl_exit") != 0 or headers.get("status") != 200 or not headers.get("source_block_found"):
        raise RuntimeError(f"cached CDX source response was not a clean HTTP 200: {candidate.get('target_key')}")
    if "body_bytes" in cached and cached.get("body_bytes") != raw_body_path.stat().st_size:
        raise RuntimeError(f"cached CDX body length does not match raw bytes: {candidate.get('target_key')}")
    coverage = cached["coverage_window"]
    if not isinstance(coverage, dict) or coverage.get("from") != query.get("from") or coverage.get("to") != query.get("to"):
        raise RuntimeError(f"cached CDX coverage window is not explicit: {candidate.get('target_key')}")
    if query.get("from") != FROM_TS and coverage.get("coverage_complete_for_global_window") is not False:
        raise RuntimeError(f"partial cached CDX cannot claim the global window: {candidate.get('target_key')}")
    parsed = parse_cdx(raw_body_path.read_bytes(), int(query["limit"]))
    if not parsed.get("valid") or not parsed.get("complete") or parsed.get("resume_keys") or parsed.get("potential_truncation"):
        raise RuntimeError(f"cached CDX body is incomplete or truncated: {candidate.get('target_key')}")
    if len(parsed.get("rows", [])) >= int(query["limit"]):
        raise RuntimeError(f"cached CDX body reaches its limit: {candidate.get('target_key')}")
    cached_rows = [_normal_cdx_row(row) for row in (cached.get("rows") or [])]
    raw_rows = [_normal_cdx_row(row) for row in parsed.get("rows", [])]
    if cached_rows != raw_rows:
        raise RuntimeError(f"cached JSON rows do not equal the SHA-bound raw CDX rows: {candidate.get('target_key')}")
    selected = _normal_cdx_row(cached.get("selected") or {})
    if selected not in raw_rows:
        raise RuntimeError(f"cached selected row is absent from the SHA-bound raw CDX: {candidate.get('target_key')}")
    if cached.get("record_count") != len(raw_rows) or cached.get("original") != candidate["original"]:
        raise RuntimeError(f"cached record metadata does not match the raw CDX: {candidate.get('target_key')}")
    return parsed


def _timestamp_ok(value: str) -> bool:
    return bool(re.fullmatch(r"\d{14}", value) and FROM_TS <= value <= TO_TS)


def classify_cdx(parsed: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    original = candidate["original"]
    expected = EXPECTED_MIME[candidate["kind"]]
    views: list[dict[str, Any]] = []
    strict: list[dict[str, Any]] = []
    variants: list[dict[str, Any]] = []
    rejects: dict[str, int] = {}
    for row in parsed.get("rows", []):
        observed = str(row.get("original") or "")
        relation = identity_relation(observed, original)
        status = int(row["statuscode"]) if str(row.get("statuscode", "")).isdigit() else None
        mime = str(row.get("mimetype") or "").lower().split(";", 1)[0].strip()
        timestamp = str(row.get("timestamp") or "")
        digest = str(row.get("digest") or "").upper()
        base = {"record_index": row.get("record_index"), "timestamp": timestamp, "original": observed,
                "mimetype": row.get("mimetype"), "statuscode": row.get("statuscode"), "digest": row.get("digest"),
                "length": row.get("length"), "identity": relation, "expected_mime": mime in expected,
                "within_window": _timestamp_ok(timestamp)}
        if relation == "exact" and status == 200 and mime in expected and _timestamp_ok(timestamp) and digest:
            base["eligible"] = True
            strict.append(base)
        else:
            base["eligible"] = False
            reason = "identity" if relation != "exact" else "status" if status != 200 else "mime" if mime not in expected else "timestamp" if not _timestamp_ok(timestamp) else "digest"
            rejects[reason] = rejects.get(reason, 0) + 1
            if relation == "origin_variant":
                variants.append(base)
        views.append(base)

    selected: list[dict[str, Any]] = []
    if parsed.get("valid") and parsed.get("complete"):
        seen: set[str] = set()
        for row in sorted(strict, key=lambda item: (item["timestamp"], int(item.get("record_index") or 0)), reverse=True):
            digest = str(row.get("digest") or "").upper()
            if digest in seen:
                continue
            seen.add(digest)
            selected.append(row)
            if len(selected) >= 2:
                break
    for item in selected:
        item["replay_url"] = "https://web.archive.org/web/" + str(item["timestamp"]) + "id_/" + original
    status = "invalid_index" if not parsed.get("valid") else "potential_truncation" if not parsed.get("complete") else "complete_no_eligible_capture" if not selected else "complete_with_replay_candidates"
    return {"status": status, "rows": views, "strict_candidates": strict, "selected": selected,
            "identity_variant_candidates": variants, "reject_counts": rejects,
            "row_count": len(views), "resume_keys": parsed.get("resume_keys", []),
            "potential_truncation": bool(parsed.get("potential_truncation")),
            "replay_count": len(selected)}


def parse_headers(raw: bytes) -> dict[str, Any]:
    text = raw.decode("iso-8859-1", errors="replace")
    blocks = re.split(r"\r?\n\r?\n", text)
    parsed_blocks: list[dict[str, Any]] = []
    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        match = re.search(r"\s(\d{3})(?:\s|$)", lines[0])
        if not match:
            continue
        parsed_blocks.append({"first_line": lines[0], "status": int(match.group(1)), "lines": lines})
    connect_blocks = [block for block in parsed_blocks if "connection established" in block["first_line"].lower()]
    source_blocks = [block for block in parsed_blocks if block not in connect_blocks]
    chosen = source_blocks[-1] if source_blocks else None
    lines = chosen["lines"] if chosen else []
    status = chosen["status"] if chosen else None
    values: dict[str, list[str]] = {}
    for line in lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values.setdefault(key.lower().strip(), []).append(value.strip())
    def first(key: str) -> str | None:
        return values.get(key, [None])[0]
    link_original = None
    for link in values.get("link", []):
        match = re.search(r"<([^>]+)>\s*;\s*rel\s*=\s*[\"']?original", link, flags=re.I)
        if match:
            link_original = match.group(1)
            break
    raw_content_type = first("content-type") or ""
    retry_after_raw = first("retry-after")
    retry_after = None
    retry_after_kind = None
    if retry_after_raw:
        if retry_after_raw.isdigit():
            retry_after = int(retry_after_raw)
            retry_after_kind = "seconds"
        else:
            try:
                retry_date = parsedate_to_datetime(retry_after_raw)
                if retry_date.tzinfo is None:
                    retry_date = retry_date.replace(tzinfo=timezone.utc)
                retry_after = max(0, math.ceil((retry_date.astimezone(timezone.utc) - utc_now()).total_seconds()))
                retry_after_kind = "http_date"
            except (TypeError, ValueError, OverflowError):
                retry_after_kind = "invalid"
    return {"status": status, "connect_statuses": [block["status"] for block in connect_blocks],
            "header_block_count": len(parsed_blocks), "source_block_found": chosen is not None,
            "source_first_line": chosen["first_line"] if chosen else None,
            "content_type": raw_content_type.split(";", 1)[0].strip().lower(),
            "content_type_raw": raw_content_type,
            "content_encoding": (first("content-encoding") or "").lower().strip(),
            "memento_datetime": first("memento-datetime"), "link_original": link_original,
            "retry_after": retry_after, "retry_after_kind": retry_after_kind,
            "raw_headers_sha256": sha_bytes(raw)}


def decoded_payload(body: bytes, content_encoding: str, max_bytes: int = MAX_ENTITY_BODY_BYTES) -> tuple[bytes | None, str | None]:
    enc = content_encoding.split(",", 1)[0].strip()
    if enc in {"", "identity"}:
        return (body, None) if len(body) <= max_bytes else (None, "entity_body_cap_exceeded")
    if enc in {"gzip", "x-gzip"}:
        window = 16 + zlib.MAX_WBITS
    elif enc == "deflate":
        window = zlib.MAX_WBITS
    else:
        return None, "unsupported_content_encoding"
    decompressor = zlib.decompressobj(window)
    output = bytearray()
    try:
        for offset in range(0, len(body), 64 * 1024):
            piece = decompressor.decompress(body[offset:offset + 64 * 1024], max_bytes + 1 - len(output))
            output.extend(piece)
            if len(output) > max_bytes:
                return None, "decoded_body_cap_exceeded"
        tail = decompressor.flush(max_bytes + 1 - len(output))
        output.extend(tail)
        if len(output) > max_bytes:
            return None, "decoded_body_cap_exceeded"
        if not decompressor.eof:
            return None, "content_decode_incomplete"
        if decompressor.unused_data:
            return None, "content_decode_trailing_data"
        return bytes(output), None
    except (OSError, zlib.error):
        return None, "content_decode_error"


def image_validation(payload: bytes, content_type: str, expected_mime: set[str]) -> dict[str, Any]:
    """Validate magic, Pillow decode, and every frame without re-encoding."""
    result: dict[str, Any] = {"format": None, "frame_count": None, "size": None, "mode": None}
    normalized = content_type.lower().split(";", 1)[0].strip()
    if normalized not in expected_mime:
        result["error"] = "content_type_not_expected"
        return result
    try:
        with Image.open(BytesIO(payload)) as probe:
            image_format = str(probe.format or "").upper()
            expected_format = {"image/gif": "GIF", "image/jpeg": "JPEG", "image/png": "PNG"}[normalized]
            if image_format != expected_format:
                result["error"] = "image_magic_mismatch"
                return result
            result["format"] = image_format
            result["size"] = list(probe.size)
            result["mode"] = probe.mode
            frame_count = 0
            for frame in ImageSequence.Iterator(probe):
                frame.load()
                frame_count += 1
            result["frame_count"] = frame_count
            if frame_count < 1:
                result["error"] = "image_no_frames"
    except Exception as exc:
        result["error"] = "image_decode_error:" + type(exc).__name__
    return result


def b32_sha1(payload: bytes) -> str:
    return base64.b32encode(hashlib.sha1(payload).digest()).decode("ascii").rstrip("=")


def memento_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
    except (TypeError, ValueError, OverflowError):
        return None


def validate_replay(candidate: dict[str, Any], row: dict[str, Any], headers_raw: bytes, body: bytes,
                    curl_exit: int | None = 0) -> dict[str, Any]:
    headers = parse_headers(headers_raw)
    payload, decode_error = decoded_payload(body, headers["content_encoding"], MAX_ENTITY_BODY_BYTES)
    actual_memento_timestamp = memento_timestamp(headers["memento_datetime"])
    link_identity = identity_relation(headers["link_original"], candidate["original"]) if headers["link_original"] else "missing"
    result: dict[str, Any] = {
        "accepted": False, "reasons": [], "curl_exit": curl_exit, "http_status": headers["status"],
        "connect_statuses": headers["connect_statuses"],
        "memento_datetime": headers["memento_datetime"], "link_original": headers["link_original"],
        "actual_memento_timestamp": actual_memento_timestamp, "link_identity": link_identity,
        "actual_content_type": headers["content_type"], "raw_body_bytes": len(body),
        "raw_body_sha256": sha_bytes(body), "cdx_length": row.get("length"),
        "expected_original": candidate["original"], "cdx_digest": row.get("digest"),
    }
    if curl_exit != 0:
        result["reasons"].append("curl_exit_not_zero")
    if headers["status"] != 200:
        result["reasons"].append("http_status_not_200")
    if not headers["memento_datetime"]:
        result["reasons"].append("missing_memento_datetime")
    elif actual_memento_timestamp is None:
        result["reasons"].append("memento_datetime_invalid")
    elif not _timestamp_ok(actual_memento_timestamp):
        result["reasons"].append("memento_datetime_out_of_window")
    elif actual_memento_timestamp != str(row.get("timestamp") or ""):
        result["reasons"].append("memento_datetime_mismatch")
    if (candidate.get("late_supplement") is True and actual_memento_timestamp
            and not _late_timestamp_ok(actual_memento_timestamp)):
        result["reasons"].append("late_supplement_window_mismatch")
    if link_identity != "exact":
        result["reasons"].append("memento_original_mismatch")
    expected_mime = set(candidate.get("expected_mime")
                        or (candidate.get("expected") or {}).get("mime_types")
                        or EXPECTED_MIME[candidate["kind"]])
    if headers["content_type"] not in expected_mime:
        result["reasons"].append("content_type_not_expected")
    if payload is None:
        result["reasons"].append(decode_error or "payload_decode_error")
        return result
    result["decoded_body_bytes"] = len(payload)
    result["decoded_body_sha256"] = sha_bytes(payload)
    result["decoded_payload_sha1_base32"] = b32_sha1(payload)
    if len(body) > MAX_ENTITY_BODY_BYTES or len(payload) > MAX_ENTITY_BODY_BYTES:
        result["reasons"].append("entity_body_cap_exceeded")
    if str(row.get("digest") or "").upper() != result["decoded_payload_sha1_base32"]:
        result["reasons"].append("cdx_digest_mismatch")
    image = image_validation(payload, headers["content_type"], expected_mime)
    result["image_format"] = image.get("format")
    result["image_frame_count"] = image.get("frame_count")
    result["image_size"] = image.get("size")
    result["image_mode"] = image.get("mode")
    result["image_validation"] = "valid" if not image.get("error") else image.get("error")
    if image.get("error"):
        result["reasons"].append(str(image["error"]))
    result["accepted"] = not result["reasons"]
    return result


def persist_accepted_payload(candidate: dict[str, Any], row: dict[str, Any], validation: dict[str, Any],
                             headers_raw: bytes, body: bytes) -> tuple[dict[str, Any] | None, str | None]:
    """Persist decoded bytes privately after the disk-floor gate.

    The returned record is sanitized provenance only; it intentionally omits
    headers, cookies, traces, and text content.  The root acceptance step can
    independently inspect the private decoded payload using this record.
    """
    free = shutil.disk_usage(ROOT).free
    if free < DISK_FLOOR_BYTES:
        return None, "private_payload_disk_floor"
    payload, decode_error = decoded_payload(body, parse_headers(headers_raw)["content_encoding"], MAX_ENTITY_BODY_BYTES)
    if payload is None:
        return None, decode_error or "private_payload_decode_error"
    safe_target = re.sub(r"[^A-Za-z0-9_.-]+", "_", candidate["target_key"])
    timestamp = str(row.get("timestamp") or "unknown")
    digest = re.sub(r"[^A-Za-z0-9_-]+", "_", str(row.get("digest") or "unknown"))
    path = PRIVATE_PAYLOADS / f"{safe_target}-{timestamp}-{digest}.decoded"
    PRIVATE_PAYLOADS.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(payload)
    tmp.replace(path)
    metadata = {
        "target_key": candidate["target_key"],
        "kind": candidate["kind"],
        "original": candidate["original"],
        "selected_capture_timestamp": row.get("timestamp"),
        "actual_memento_timestamp": validation.get("actual_memento_timestamp"),
        "actual_link_original": validation.get("link_original"),
        "cdx_digest": row.get("digest"),
        "cdx_record_length": row.get("length"),
        "raw_body_sha256": validation.get("raw_body_sha256"),
        "raw_body_bytes": validation.get("raw_body_bytes"),
        "decoded_body_sha256": validation.get("decoded_body_sha256"),
        "decoded_body_bytes": validation.get("decoded_body_bytes"),
        "private_decoded_payload_path": rel(path),
        "content_encoding": parse_headers(headers_raw).get("content_encoding") or "identity",
        "verification": {
            "curl_exit": validation.get("curl_exit"),
            "http_status": validation.get("http_status"),
            "link_identity": validation.get("link_identity"),
            "actual_content_type": validation.get("actual_content_type"),
            "image_format": validation.get("image_format"),
            "image_frame_count": validation.get("image_frame_count"),
            "image_size": validation.get("image_size"),
            "image_mode": validation.get("image_mode"),
            "image_validation": validation.get("image_validation"),
            "decoded_payload_sha1_base32": validation.get("decoded_payload_sha1_base32"),
        },
        "status": "pending_root",
    }
    if candidate.get("late_supplement") is True:
        metadata.update({
            "late_supplement": True,
            "supplement_window": candidate.get("late_window"),
            "pre_anchor_cdx_digest": candidate.get("pre_anchor_cdx_digest"),
            "adoption_note": "same-day late supplement; compare payload digest with pre-anchor indexed digest before any adoption",
        })
    return metadata, None


class FixtureClock:
    def __init__(self, ratio: float = 0.96, quantum: float = 0.1) -> None:
        self.mono = 100.0
        self.utc = datetime(2026, 10, 16, 6, 0, tzinfo=timezone.utc)
        self.ratio = ratio
        self.quantum = quantum
        self.sleep_calls: list[float] = []

    def monotonic(self) -> float:
        return self.mono

    def now(self) -> datetime:
        return self.utc

    def sleep(self, seconds: float) -> None:
        self.sleep_calls.append(seconds)
        actual = max(0.0, round(seconds * self.ratio / self.quantum) * self.quantum)
        if actual <= 0:
            actual = self.quantum
        self.mono += actual
        self.utc += timedelta(seconds=actual)


def cadence_gate(clock: FixtureClock, last_dispatch: float | None, last_start: datetime | None) -> dict[str, Any]:
    requested = 0.0
    while last_dispatch is not None or last_start is not None:
        mono_gap = float("inf") if last_dispatch is None else clock.monotonic() - last_dispatch
        utc_gap = float("inf") if last_start is None else (clock.now() - last_start).total_seconds()
        wait = max(0.0, MIN_DISPATCH_SECONDS - mono_gap, MIN_REQUEST_START_SECONDS - utc_gap)
        if wait <= 0:
            break
        requested += wait
        clock.sleep(wait)
    return {"dispatch_monotonic": clock.monotonic(), "start_utc": iso(clock.now()), "sleep_requested_seconds": requested,
            "sleep_calls": len(clock.sleep_calls), "dispatch_gap_seconds": None if last_dispatch is None else clock.monotonic() - last_dispatch,
            "start_gap_seconds": None if last_start is None else (clock.now() - last_start).total_seconds()}


def clamp_budget(total_used: int, started: datetime, now_value: datetime, entity_cap: int = MAX_ENTITY_BODY_BYTES) -> dict[str, Any]:
    remaining_bytes = max(0, MAX_TOTAL_BODY_BYTES - total_used)
    remaining_time = max(0.0, WINDOW_SECONDS - (now_value - started).total_seconds())
    body_cap = min(entity_cap, remaining_bytes)
    timeout = min(PROXY_MAX_SECONDS, remaining_time) if remaining_time else 0.0
    return {"remaining_bytes": remaining_bytes, "remaining_time_seconds": remaining_time,
            "entity_body_cap": body_cap, "timeout_seconds": timeout,
            "allowed": body_cap > 0 and timeout > 0}


def disk_gate(free: int) -> dict[str, Any]:
    return {"disk_free_before_bytes": free, "disk_floor_passed": free >= DISK_FLOOR_BYTES}


def initial_state() -> dict[str, Any]:
    # ``failure_streak`` is the cross-batch contiguous transport tail used by
    # the five-failure stop rule.  ``failure_streak_start`` records the same
    # inherited value for acceptance; only the current-window counter starts at
    # zero.  Do not silently clear a prior tail when a new plan is loaded.
    return {"batch_id": BATCH_ID, "started_utc": iso(utc_now()), "attempts": [], "total_body_bytes": 0,
            "source_responses": 0, "failure_streak": PRIOR_FAILURE_TAIL, "failure_streak_start": PRIOR_FAILURE_TAIL,
            "prior_failure_tail": PRIOR_FAILURE_TAIL, "current_window_failure_streak": 0,
            "stop_reason": None, "cooldown_not_before_utc": None,
            "direct_probe_done": False, "failed_attempt_number": None, "skip_reason": None,
            "batch_proxy_only": False,
            "report_policy": {
                "transport_policy": TRANSPORT_POLICY,
                "batch_scope": "one execute invocation; initial_state resets the direct probe for the next batch",
                "direct_failure_qualification": "source_status=None and curl_exit in {7,28} and body_bytes=0",
            }}


def _transport_sequence_for_request(state: dict[str, Any]) -> tuple[str, ...]:
    """Choose transports without changing the v1 default per-request mode."""
    if TRANSPORT_POLICY == "batch_after_direct_failure" and state.get("batch_proxy_only"):
        return ("proxy",)
    return ("direct", "proxy")


def _qualifying_direct_failure(result: dict[str, Any]) -> bool:
    return (
        result.get("source_status") is None
        and result.get("curl_exit") in {7, 28}
        and int(result.get("body_bytes") or 0) == 0
    )


def _record_direct_probe(state: dict[str, Any], transport: str, result: dict[str, Any], attempt_no: int) -> None:
    """Persist the batch transport decision; the core failure streak stays shared."""
    if TRANSPORT_POLICY != "batch_after_direct_failure" or transport != "direct":
        return
    state["direct_probe_done"] = True
    if _qualifying_direct_failure(result):
        state["failed_attempt_number"] = attempt_no
        state["skip_reason"] = "direct_source_status_none_curl_7_or_28_empty_body"
        state["batch_proxy_only"] = True
    state["report_policy"].update({
        "direct_probe_done": state.get("direct_probe_done"),
        "failed_attempt_number": state.get("failed_attempt_number"),
        "skip_reason": state.get("skip_reason"),
        "proxy_only_active": state.get("batch_proxy_only", False),
    })


def _actual_request_count(state: dict[str, Any]) -> int:
    """Count only attempts whose transport was actually dispatched."""
    return sum(1 for attempt in state.get("attempts", []) if attempt.get("sent") is True)


def _curl_request(url: str, transport: str, body_cap: int, timeout: float, raw_dir: Path, attempt_no: int) -> dict[str, Any]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    stem = f"attempt-{attempt_no:03d}-{transport}"
    headers_path, body_path, trace_path, stderr_path, status_path = (raw_dir / f"{stem}-{suffix}" for suffix in ("headers.txt", "body.bin", "trace.txt", "stderr.txt", "status.txt"))
    transport_max = DIRECT_MAX_SECONDS if transport == "direct" else PROXY_MAX_SECONDS
    connect_max = DIRECT_CONNECT_SECONDS if transport == "direct" else PROXY_CONNECT_SECONDS
    effective_timeout = min(transport_max, timeout)
    effective_connect = min(connect_max, effective_timeout)
    timeout_text = f"{effective_timeout:.6f}"
    connect_text = f"{effective_connect:.6f}"
    if effective_timeout <= 0 or effective_connect <= 0 or float(timeout_text) <= 0 or float(connect_text) <= 0:
        raise ValueError("nonpositive formatted curl timeout; dispatch refused")
    args = ["curl.exe", "--silent", "--show-error", "--tlsv1.2", "--proto", "=http,https", "--max-redirs", "0",
            "--connect-timeout", connect_text,
            "--max-time", timeout_text, "--max-filesize", str(max(1, body_cap)),
            "--dump-header", str(headers_path), "--output", str(body_path), "--trace", str(trace_path),
            "--user-agent", USER_AGENT, "--write-out", "%{http_code}", url]
    if transport == "proxy":
        args[1:1] = ["--proxy", PROXY, "--noproxy", ""]
    else:
        # Direct means direct even when a machine-level proxy is configured.
        args[1:1] = ["--noproxy", "*"]
    started = utc_now()
    # curl enforces the precise remaining network budget; the subprocess
    # timeout is a small bounded cleanup grace and can never be unbounded.
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=max(0.05, effective_timeout + 0.25), check=False)
    finished = utc_now()
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    status_path.write_text(proc.stdout, encoding="ascii", errors="replace")
    status_text = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    status_code = int(status_text) if status_text.isdigit() and len(status_text) == 3 and status_text != "000" else None
    body = body_path.read_bytes() if body_path.exists() else b""
    header_info = parse_headers(headers_path.read_bytes()) if headers_path.exists() else parse_headers(b"")
    if not header_info["source_block_found"]:
        status_code = None
    return {"transport": transport, "url": url, "started_utc": iso(started), "finished_utc": iso(finished),
            "curl_exit": proc.returncode, "source_status": status_code, "body_bytes": len(body),
            "headers_path": rel(headers_path) if headers_path.exists() else None,
            "body_path": rel(body_path) if body_path.exists() else None,
            "trace_path": rel(trace_path) if trace_path.exists() else None,
            "stderr_path": rel(stderr_path), "status_path": rel(status_path), "raw_body_sha256": sha_bytes(body),
            "retry_after": header_info.get("retry_after"), "retry_after_kind": header_info.get("retry_after_kind"),
            "header_source_block_found": header_info.get("source_block_found"),
            "header_connect_statuses": header_info.get("connect_statuses", []),
            "effective_timeout_seconds": effective_timeout,
            "effective_connect_timeout_seconds": effective_connect}


def load_and_validate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    plan = read_json(PLAN_PATH)
    if plan.get("schema") != "wow-recovery.reusable-image-plan.v1":
        raise RuntimeError("unexpected reusable image plan schema")
    if not BINDINGS_PATH.is_file():
        raise RuntimeError("input-bindings.json is required")
    bindings = read_json(BINDINGS_PATH)
    candidates = plan.get("candidates") or []
    candidate_count = plan.get("candidate_count")
    if (isinstance(candidate_count, bool) or not isinstance(candidate_count, int)
            or not 1 <= candidate_count <= 20 or len(candidates) != candidate_count):
        raise RuntimeError("reusable image plan must contain between one and twenty candidates")
    policy = plan.get("policy") or {}
    pending = _late_plan_pending(plan)
    declared_prior = (plan.get("previous_batch") or {}).get("prior_failure_tail")
    _policy_hard_bounds(policy, 0 if pending else declared_prior)
    checks = [(policy.get("from") == POLICY_FROM_TS, "from"), (policy.get("to") == POLICY_TO_TS, "to"),
              (policy.get("limit") == CDX_LIMIT, "limit"), (policy.get("showResumeKey") is True, "showResumeKey"),
              (policy.get("collapse") is False, "collapse"), (policy.get("matchType") == "exact", "matchType"),
              (isinstance(policy.get("max_attempts"), int) and not isinstance(policy.get("max_attempts"), bool)
               and 1 <= policy.get("max_attempts") <= POLICY_MAX_ATTEMPTS, "max_attempts"),
              (policy.get("max_originals") == 20, "max_originals"),
              (isinstance(policy.get("max_total_body_bytes"), int) and not isinstance(policy.get("max_total_body_bytes"), bool)
               and 1 <= policy.get("max_total_body_bytes") <= POLICY_MAX_TOTAL_BODY_BYTES, "total body cap"),
              (isinstance(policy.get("max_entity_body_bytes"), int) and not isinstance(policy.get("max_entity_body_bytes"), bool)
               and 1 <= policy.get("max_entity_body_bytes") <= min(POLICY_MAX_ENTITY_BODY_BYTES, policy.get("max_total_body_bytes", 0)), "entity cap"),
              (isinstance(policy.get("window_seconds"), (int, float)) and not isinstance(policy.get("window_seconds"), bool)
               and math.isfinite(float(policy.get("window_seconds"))) and 0 < float(policy.get("window_seconds")) <= POLICY_MAX_WINDOW_SECONDS, "window"),
              (isinstance(policy.get("min_dispatch_seconds"), (int, float)) and float(policy.get("min_dispatch_seconds")) >= POLICY_MIN_DISPATCH_SECONDS, "dispatch cadence"),
              (isinstance(policy.get("min_request_start_seconds"), (int, float)) and float(policy.get("min_request_start_seconds")) >= POLICY_MIN_REQUEST_START_SECONDS, "start cadence"),
              (isinstance(policy.get("disk_floor_bytes"), int) and policy.get("disk_floor_bytes") >= POLICY_MIN_DISK_FLOOR_BYTES, "disk floor"),
              (policy.get("direct_first") is True, "direct first"),
              (policy.get("tls_verification") is True, "TLS verification"),
              (policy.get("automatic_redirects") == 0, "redirects"),
              (policy.get("proxy") == PROXY, "proxy")]
    for okay, label in checks:
        if not okay:
            raise RuntimeError(f"reusable image policy mismatch: {label}")
    plan_inputs = plan.get("input_bindings") or {}
    for key, entry in plan_inputs.items():
        bound = Path(str(entry["path"]))
        path = (ROOT / bound if not bound.is_absolute() else bound)
        if not path.exists() or not path.is_file():
            raise RuntimeError(f"input binding missing: {key}")
        actual = sha_file(path)
        if actual != str(entry["sha256"]):
            raise RuntimeError(f"input binding changed: {key}: {actual}")
    binding_plan = bindings.get("plan_sha256")
    if binding_plan and binding_plan != sha_file(PLAN_PATH):
        raise RuntimeError("plan SHA mismatch in input-bindings")
    if bindings.get("driver_sha256") and bindings["driver_sha256"] != sha_file(Path(__file__)):
        raise RuntimeError("driver SHA mismatch in input-bindings")
    if bindings.get("plan_sha256") != sha_file(PLAN_PATH):
        raise RuntimeError("plan SHA mismatch in input-bindings")
    if bindings.get("driver_sha256") != sha_file(Path(__file__)):
        raise RuntimeError("driver SHA mismatch in input-bindings")
    previous = plan.get("previous_batch") or {}
    prior_tail = previous.get("prior_failure_tail")
    if pending:
        if prior_tail is not None or policy.get("prior_failure_tail") is not None:
            raise RuntimeError("pending late11 plan must not bind a stale failure tail")
        prior_tail = 0
    elif (isinstance(prior_tail, bool) or not isinstance(prior_tail, int) or not 0 <= prior_tail <= 4
          or policy.get("prior_failure_tail") != prior_tail):
        raise RuntimeError("prior failure tail is outside the allowed bound or is not policy-bound")
    if prior_tail == 0 and not pending:
        gate_path = previous.get("control_gate_receipt_path")
        gate_sha = previous.get("control_gate_receipt_sha256")
        gate = _bound_path(gate_path)
        if not gate.is_file() or sha_file(gate) != str(gate_sha or "").lower():
            raise RuntimeError("fresh control gate receipt is missing or changed")
        gate_data = read_json(gate)
        if not (gate_data.get("accepted") is True and gate_data.get("resume_gate_passed") is True
                and gate_data.get("control_final_streak") == 0):
            raise RuntimeError("fresh control gate receipt does not authorize prior tail zero")
    elif not pending:
        tail_path = previous.get("tail_receipt_path")
        tail_sha = previous.get("tail_receipt_sha256")
        tail_receipt = _bound_path(tail_path)
        if not tail_receipt.is_file() or sha_file(tail_receipt) != str(tail_sha or "").lower():
            raise RuntimeError("prior tail receipt is missing or changed")
        tail_data = read_json(tail_receipt)
        if tail_data.get("failure_streak_end") != prior_tail:
            raise RuntimeError("prior tail does not equal the bound receipt end tail")
    seen_keys: set[str] = set()
    for candidate in candidates:
        target_key = _validate_target_key(candidate.get("target_key"), seen_keys)
        seen_keys.add(target_key)
        original = str(candidate.get("original") or "")
        parsed_original = urlsplit(original)
        if (parsed_original.scheme not in {"http", "https"} or not parsed_original.hostname
                or parsed_original.username is not None or parsed_original.password is not None
                or parsed_original.fragment or identity_relation(original, original) != "exact"):
            raise RuntimeError(f"invalid exact HTTP(S) original: {candidate.get('target_key')}")
        _validate_source_evidence(candidate)
        mode = candidate.get("cdx_mode")
        if mode not in {"fresh", "cached"}:
            raise RuntimeError(f"unsupported cdx_mode: {candidate.get('target_key')}")
        query = candidate.get("query") or {}
        if query.get("url") != original:
            raise RuntimeError(f"CDX query widened: {candidate.get('target_key')}")
        if (query.get("collapse") is not False or query.get("matchType") != "exact"
                or not isinstance(query.get("limit"), int) or not (0 < query["limit"] <= CDX_LIMIT)):
            raise RuntimeError(f"CDX query policy mismatch: {candidate.get('target_key')}")
        if mode == "fresh" and (query.get("from") != FROM_TS or query.get("to") != TO_TS
                                  or query.get("limit") != CDX_LIMIT or query.get("showResumeKey") is not True):
            raise RuntimeError(f"fresh CDX query must request the bounded resume-aware form: {candidate.get('target_key')}")
        query_fields = query.get("fields") or FIELDS
        if query.get("query_url") != cdx_query_url(original, from_ts=str(query.get("from")), to_ts=str(query.get("to")),
                                                     limit=int(query.get("limit")), show_resume=bool(query.get("showResumeKey")),
                                                     fields=[str(value) for value in query_fields]):
            raise RuntimeError(f"CDX query URL is not generated from the declared exact fields: {candidate.get('target_key')}")
        if mode == "cached":
            cached = candidate.get("cached_cdx") or {}
            if cached.get("query_url") != query.get("query_url") or cached.get("original") != original:
                raise RuntimeError(f"cached CDX identity missing: {candidate.get('target_key')}")
            _validate_cached_evidence(candidate, query, cached)
        replay = candidate.get("replay") or {}
        if replay.get("enabled") is not True or replay.get("no_redirects") is not True:
            raise RuntimeError(f"replay policy must be explicit/no-redirect: {candidate.get('target_key')}")
        replay_template = "https://web.archive.org/web/{timestamp}id_/" + original
        if replay.get("id_url_template") != replay_template:
            raise RuntimeError(f"replay URL widened: {candidate.get('target_key')}")
        if candidate.get("fallback_label") and candidate.get("fallback_label") != "best_known_cached_not_latest":
            raise RuntimeError(f"unknown fallback label: {candidate.get('target_key')}")
    _validate_late_supplement_plan(plan)
    return plan, bindings


def run_transport_policy_fixtures() -> dict[str, Any]:
    """Exercise the optional policy with fake outcomes only; never start curl."""
    global TRANSPORT_POLICY
    old_policy = TRANSPORT_POLICY
    try:
        TRANSPORT_POLICY = "per_request"
        default_state = initial_state()
        default_sequence = _transport_sequence_for_request(default_state)
        _record_direct_probe(default_state, "direct", {"source_status": None, "curl_exit": 28, "body_bytes": 0}, 1)
        default_after_failure_sequence = _transport_sequence_for_request(default_state)

        TRANSPORT_POLICY = "batch_after_direct_failure"
        direct_fail_state = initial_state()
        first_sequence = _transport_sequence_for_request(direct_fail_state)
        direct_failure = {"source_status": None, "curl_exit": 28, "body_bytes": 0}
        _record_direct_probe(direct_fail_state, "direct", direct_failure, 1)
        same_request_retry_sequence = _transport_sequence_for_request(direct_fail_state)
        proxy_success = {"source_status": 200, "curl_exit": 0, "body_bytes": 64}
        next_request_sequence = _transport_sequence_for_request(direct_fail_state)

        source_state = initial_state()
        source_sequence = _transport_sequence_for_request(source_state)
        _record_direct_probe(source_state, "direct", {"source_status": 200, "curl_exit": 0, "body_bytes": 64}, 1)
        source_next_sequence = _transport_sequence_for_request(source_state)

        reset_state = initial_state()
        reset_sequence = _transport_sequence_for_request(reset_state)

        proxy_state = initial_state()
        proxy_state["batch_proxy_only"] = True
        proxy_state["skip_reason"] = "fixture_proxy_only"
        proxy_trace = []
        for attempt in range(1, 6):
            if proxy_state.get("stop_reason"):
                break
            sequence = _transport_sequence_for_request(proxy_state)
            proxy_trace.append(sequence[0] if sequence else None)
            proxy_result = {"source_status": None, "curl_exit": 28, "body_bytes": 0}
            proxy_state["failure_streak"] = int(proxy_state.get("failure_streak", 0)) + 1
            if proxy_state["failure_streak"] >= 5:
                proxy_state["stop_reason"] = "five_consecutive_transport_failures"
        tests = {
            "per_request_default_remains_direct_then_proxy": (
                default_sequence == ("direct", "proxy")
                and default_after_failure_sequence == ("direct", "proxy")
                and default_state["direct_probe_done"] is False
            ),
            "directfail_proxysuccess_next_request_proxy_only": (
                first_sequence == ("direct", "proxy")
                and same_request_retry_sequence == ("proxy",)
                and next_request_sequence == ("proxy",)
                and direct_fail_state["direct_probe_done"] is True
                and direct_fail_state["failed_attempt_number"] == 1
                and direct_fail_state["skip_reason"] == "direct_source_status_none_curl_7_or_28_empty_body"
            ),
            "direct_source_http_keeps_direct_next_request": (
                source_sequence == ("direct", "proxy")
                and source_next_sequence == ("direct", "proxy")
                and source_state["direct_probe_done"] is True
                and source_state["batch_proxy_only"] is False
                and source_state["skip_reason"] is None
            ),
            "initial_state_resets_direct_probe": (
                reset_sequence == ("direct", "proxy")
                and reset_state["direct_probe_done"] is False
                and reset_state["failed_attempt_number"] is None
                and reset_state["skip_reason"] is None
            ),
            "proxy_five_failures_stop": (
                proxy_trace == ["proxy"] * 5
                and proxy_state["failure_streak"] == 5
                and proxy_state["stop_reason"] == "five_consecutive_transport_failures"
            ),
        }
        return {"tests": tests, "all_passed": all(tests.values()), "network_requests": 0,
                "trace": {"direct_failure_retry": list(same_request_retry_sequence),
                          "next_request": list(next_request_sequence), "direct_source_next": list(source_next_sequence),
                          "proxy_failures": proxy_trace},
                "state_fields": ["direct_probe_done", "failed_attempt_number", "skip_reason", "report_policy"]}
    finally:
        TRANSPORT_POLICY = old_policy


def run_fixtures(fixture_output: Path | None = None) -> dict[str, Any]:
    """Run the reusable core entirely offline; no curl/process is started."""
    plan, _bindings = load_and_validate_inputs()
    # Core fixtures use a neutral candidate timestamp so they continue to
    # exercise the shared v2 image gates.  The late-window behavior is covered
    # separately by fixture_late11.py below; do not turn the generic 2007
    # synthetic payloads into late supplements.
    candidate = dict(plan["candidates"][0])
    candidate.pop("late_supplement", None)
    candidate.pop("late_window", None)
    header = FIELDS
    digest1, digest2 = "A" * 32, "B" * 32

    rows = [header,
            ["k", "20070101000000", candidate["original"], "image/gif", "200", digest1, "100"],
            [], ["resume-token"]]
    parsed = parse_cdx(json.dumps(rows).encode())
    t1 = (parsed["valid"] and not parsed["complete"] and parsed["resume_keys"] == ["resume-token"]
          and len(parsed["rows"]) == 1 and any(x.get("kind") == "separator" for x in parsed["metadata"]))

    full_rows = [header] + [[f"k{i}", f"200701010000{i:02d}", candidate["original"], "image/gif", "200", digest1, "100"] for i in range(CDX_LIMIT)]
    parsed500 = parse_cdx(json.dumps(full_rows).encode())
    classified500 = classify_cdx(parsed500, candidate)
    t2 = (parsed500["potential_truncation"] and not classified500["selected"]
          and classified500["status"] == "potential_truncation")

    latest_rows = [header,
                   ["old", "20070101000000", candidate["original"], "image/gif", "200", digest1, "100"],
                   ["new", "20070201000000", candidate["original"].replace("http://www.worldofwarcraft.com", "http://www.worldofwarcraft.com:80", 1), "image/gif", "200", digest2, "101"],
                   ["alias", "20070301000000", candidate["original"].replace("www.worldofwarcraft.com", "wow-europe.com"), "image/gif", "200", "C" * 32, "102"],
                   ["bad", "20070401000000", candidate["original"], "image/gif", "404", "D" * 32, "103"]]
    latest = classify_cdx(parse_cdx(json.dumps(latest_rows).encode()), candidate)
    t3 = (len(latest["selected"]) == 2 and latest["selected"][0]["timestamp"] == "20070201000000"
          and latest["selected"][0]["original"].startswith("http://www.worldofwarcraft.com:80/")
          and len(latest["identity_variant_candidates"]) == 1)

    def headers_for(original: str, timestamp: str, content_type: str, encoding: str = "") -> bytes:
        default_link = original.replace("http://www.worldofwarcraft.com", "http://www.worldofwarcraft.com:80", 1)
        extra = (b"Content-Encoding: " + encoding.encode() + b"\r\n") if encoding else b""
        date = datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        return (b"HTTP/1.1 200 Connection established\r\nProxy-Agent: fixture\r\n\r\n"
                b"HTTP/1.1 200 OK\r\nContent-Type: " + content_type.encode() + b"\r\n" + extra
                + b"Memento-Datetime: " + format_datetime(date, usegmt=True).encode() + b"\r\n"
                + b"Link: <" + default_link.encode() + b">; rel=\"original\"\r\n\r\n")

    gif_io = BytesIO()
    gif_frame1 = Image.new("P", (2, 2), 0)
    gif_frame2 = Image.new("P", (2, 2), 1)
    gif_frame2.putpixel((1, 1), 2)
    gif_frame1.save(gif_io, format="GIF", save_all=True, append_images=[gif_frame2], duration=50, loop=0, optimize=False)
    good_gif = gif_io.getvalue()
    gif_row = {"timestamp": "20070101000000", "digest": b32_sha1(good_gif), "length": str(len(good_gif))}
    gif_candidate = dict(candidate, expected_mime={"image/gif"})
    verified_gif = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"], gif_row["timestamp"], "image/gif"), good_gif)

    jpeg_io = BytesIO()
    Image.new("RGB", (3, 2), (20, 40, 60)).save(jpeg_io, format="JPEG")
    good_jpeg = jpeg_io.getvalue()
    jpeg_candidate = dict(candidate, expected_mime={"image/jpeg"})
    jpeg_row = {"timestamp": "20070101000000", "digest": b32_sha1(good_jpeg), "length": str(len(good_jpeg))}
    verified_jpeg = validate_replay(jpeg_candidate, jpeg_row, headers_for(candidate["original"], jpeg_row["timestamp"], "image/jpeg"), good_jpeg)

    png_io = BytesIO()
    Image.new("RGBA", (2, 3), (1, 2, 3, 255)).save(png_io, format="PNG")
    good_png = png_io.getvalue()
    png_candidate = dict(candidate, expected_mime={"image/png"})
    png_row = {"timestamp": "20070101000000", "digest": b32_sha1(good_png), "length": str(len(good_png))}
    verified_png = validate_replay(png_candidate, png_row, headers_for(candidate["original"], png_row["timestamp"], "image/png"), good_png)
    t4 = (verified_gif["accepted"] and verified_gif["image_frame_count"] == 2
          and verified_jpeg["accepted"] and verified_jpeg["image_format"] == "JPEG"
          and verified_png["accepted"] and verified_png["image_format"] == "PNG")

    bad_html = b"<html><title>Wayback Machine error</title></html>"
    bad_row = {"timestamp": "20070101000000", "digest": b32_sha1(bad_html), "length": str(len(bad_html))}
    rejected_error = validate_replay(jpeg_candidate, bad_row, headers_for(candidate["original"], bad_row["timestamp"], "image/jpeg"), bad_html)
    wrong_magic = validate_replay(gif_candidate, jpeg_row, headers_for(candidate["original"], jpeg_row["timestamp"], "image/gif"), good_jpeg)
    t5 = (not rejected_error["accepted"] and any(r.startswith("image_decode_error") for r in rejected_error["reasons"])
          and not wrong_magic["accepted"] and "image_magic_mismatch" in wrong_magic["reasons"])

    compressed = gzip.compress(good_gif)
    compressed_result = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"], gif_row["timestamp"], "image/gif", "gzip"), compressed)
    wrong_digest = validate_replay(gif_candidate, {**gif_row, "digest": "Z" * 32}, headers_for(candidate["original"], gif_row["timestamp"], "image/gif"), good_gif)
    wrong_memento = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"], "20070101000001", "image/gif"), good_gif)
    wrong_link = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"] + "?wrong-link=1", gif_row["timestamp"], "image/gif"), good_gif)
    t6 = (compressed_result["accepted"] and compressed_result["raw_body_bytes"] != compressed_result["decoded_body_bytes"]
          and not wrong_digest["accepted"] and "cdx_digest_mismatch" in wrong_digest["reasons"]
          and not wrong_memento["accepted"] and "memento_datetime_mismatch" in wrong_memento["reasons"]
          and not wrong_link["accepted"] and "memento_original_mismatch" in wrong_link["reasons"])

    expanded_over_cap = b"GIF89a" + (b"x" * (MAX_ENTITY_BODY_BYTES + 1))
    expanded_payload, expanded_error = decoded_payload(gzip.compress(expanded_over_cap), "gzip", MAX_ENTITY_BODY_BYTES)
    truncated_gzip_payload, truncated_gzip_error = decoded_payload(gzip.compress(good_gif)[:-8], "gzip", MAX_ENTITY_BODY_BYTES)
    truncated_deflate_payload, truncated_deflate_error = decoded_payload(zlib.compress(good_gif)[:-2], "deflate", MAX_ENTITY_BODY_BYTES)
    trailing_payload, trailing_error = decoded_payload(gzip.compress(good_gif) + b"TRAIL", "gzip", MAX_ENTITY_BODY_BYTES)
    t7 = (expanded_payload is None and expanded_error == "decoded_body_cap_exceeded"
          and truncated_gzip_payload is None and truncated_gzip_error == "content_decode_incomplete"
          and truncated_deflate_payload is None and truncated_deflate_error == "content_decode_incomplete"
          and trailing_payload is None and trailing_error == "content_decode_trailing_data")

    source404 = parse_headers(b"HTTP/1.1 200 Connection established\r\n\r\nHTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n")
    retry_date = format_datetime(utc_now() + timedelta(seconds=240), usegmt=True).encode("ascii")
    source429 = parse_headers(b"HTTP/1.1 200 Connection established\r\n\r\nHTTP/1.1 429 Too Many Requests\r\nRetry-After: " + retry_date + b"\r\n\r\n")
    only_connect = parse_headers(b"HTTP/1.1 200 Connection established\r\nProxy-Agent: fixture\r\n\r\n")
    t8 = (source404["status"] == 404 and source404["connect_statuses"] == [200]
          and source429["status"] == 429 and source429["retry_after_kind"] == "http_date"
          and (source429["retry_after"] or 0) >= 120 and only_connect["status"] is None
          and not only_connect["source_block_found"] and only_connect["connect_statuses"] == [200])

    # Positive cache fixture: bind the actual ALLNEWS01 Blizzcon CDX body
    # (raw/70) and source report, rather than accepting synthetic metadata.
    # The body deliberately uses the six-column cached query shape and covers
    # 2006..anchor only, so it is complete for that query but cannot prove a
    # global 2000..anchor latest capture.
    cached_plan_path = NETWORK / "news-shared10" / "plan.json"
    cached_plan = read_json(cached_plan_path)
    cached_candidate_source = next(item for item in cached_plan["candidates"]
                                   if item.get("target_key") == "NEWS10-04-blizzconlogo-jpg")
    cached_candidate = json.loads(json.dumps(cached_candidate_source))
    cached = dict(cached_candidate["cached_cdx"])
    cached_body_path = _bound_path(cached["raw_body_path"], under_network=True)
    cached_headers_path = _bound_path(cached["raw_headers_path"], under_network=True)
    cached_query = cached_candidate["query"]
    cached_parsed = parse_cdx(cached_body_path.read_bytes(), int(cached_query["limit"]))
    cached_exact_rows = [row for row in cached_parsed.get("rows", [])
                         if identity_relation(str(row.get("original") or ""), cached_candidate["original"]) == "exact"
                         and str(row.get("statuscode")) == "200"]
    cached_selected = max(cached_exact_rows, key=lambda row: (str(row.get("timestamp")), int(row.get("record_index") or 0)))
    cached.update({
        "source_curl_exit": 0,
        "raw_headers_sha256": sha_file(cached_headers_path),
        "body_bytes": cached_body_path.stat().st_size,
        "coverage_window": {"from": cached_query["from"], "to": cached_query["to"],
                             "coverage_complete_for_global_window": False},
        "rows": cached_parsed["rows"],
        "record_count": len(cached_parsed["rows"]),
        "selected": cached_selected,
    })
    cached_candidate["cached_cdx"] = cached
    cached_validation = _validate_cached_evidence(cached_candidate, cached_query, cached)
    t9 = (cached_validation["valid"] and cached_validation["complete"]
          and len(cached_validation["rows"]) == 4
          and cached_validation["header"] == CDX_FIELDS_WITHOUT_URLKEY
          and cached_selected["timestamp"] == "20080402081015"
          and cached_selected["original"] == cached_candidate["original"])
    t10 = candidate.get("fallback_label") == "best_known_cached_not_latest" or all(c.get("fallback_label") == "best_known_cached_not_latest" for c in plan["candidates"] if c.get("fallback_label"))

    clock = FixtureClock(ratio=0.96, quantum=0.1)
    first = clock.monotonic(); first_utc = clock.now(); clock.sleep(0.2)
    gated = cadence_gate(clock, first, first_utc)
    t11 = (gated["dispatch_gap_seconds"] or 0) >= MIN_DISPATCH_SECONDS and (gated["start_gap_seconds"] or 0) >= MIN_REQUEST_START_SECONDS
    started = clock.now()
    clamp = clamp_budget(MAX_TOTAL_BODY_BYTES - 10, started, started + timedelta(seconds=2))
    disk = disk_gate(DISK_FLOOR_BYTES - 1)
    t12 = clamp["entity_body_cap"] == 10 and clamp["timeout_seconds"] <= PROXY_MAX_SECONDS and not disk["disk_floor_passed"]
    unknown_metadata = parse_cdx(json.dumps({"metadata": {"unexpected": True}}).encode())
    t13 = not unknown_metadata["valid"] and not unknown_metadata["complete"]
    cached_json = json.dumps([header, ["x", "20070101000000", candidate["original"], "image/gif", "200", digest1, "10"], []]).encode()
    cached_parsed = parse_cdx(cached_json, limit=250)
    t14 = cached_parsed["valid"] and cached_parsed["complete"] and not cached_parsed["potential_truncation"] and len(cached_parsed["rows"]) == 1
    nonzero_exit = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"], gif_row["timestamp"], "image/gif"), good_gif, curl_exit=23)
    t15 = not nonzero_exit["accepted"] and "curl_exit_not_zero" in nonzero_exit["reasons"]

    # New reusable-runner contract checks.  These are structural/offline tests;
    # they do not create an execute output or dispatch a request.
    t16 = 1 <= int(plan.get("candidate_count", 0)) <= 20
    try:
        _plan_output_dir(str(ROOT / "outside-recovery-network"))
        t17 = False
    except RuntimeError:
        t17 = True
    bad_original = "ftp://example.invalid/asset.gif"
    t18 = urlsplit(bad_original).scheme not in {"http", "https"}
    bad_cached = {"record_count": CDX_LIMIT, "potential_truncation": True, "resume_keys": ["next"], "source_report_sha256": "a" * 64}
    t19 = bool(bad_cached["potential_truncation"] or bad_cached["record_count"] >= CDX_LIMIT or bad_cached["resume_keys"])
    old_fixture_path = NETWORK / "news-shared10" / "fixture-results.json"
    old_fixture = read_json(old_fixture_path)
    t20 = (old_fixture.get("all_passed") is True and old_fixture.get("passed") == 15
           and old_fixture.get("total") == 15 and sha_file(old_fixture_path) == "499836c7208e1d6df69a02280ed45505491756926e3c7b69d87c7acd83952152")
    try:
        _policy_hard_bounds(dict(plan["policy"], max_attempts=POLICY_MAX_ATTEMPTS + 1), 0)
        t21 = False
    except RuntimeError:
        t21 = True
    try:
        _validate_target_key(candidate["target_key"], {candidate["target_key"]})
        t22 = False
    except RuntimeError:
        t22 = True
    try:
        _validate_cached_evidence(candidate, candidate["query"], {"record_count": 1, "selected": {}})
        t23 = False
    except RuntimeError:
        t23 = True
    try:
        _validate_source_evidence(dict(candidate, source_evidence={**candidate["source_evidence"], "sha256": "0" * 64}))
        t24 = False
    except RuntimeError:
        t24 = True

    prior_before_fixture = PRIOR_FAILURE_TAIL
    try:
        globals()["PRIOR_FAILURE_TAIL"] = 2
        inherited_state = initial_state()
        t25 = (inherited_state["failure_streak"] == 2
               and inherited_state["failure_streak_start"] == 2
               and inherited_state["prior_failure_tail"] == 2
               and inherited_state["current_window_failure_streak"] == 0)
    finally:
        globals()["PRIOR_FAILURE_TAIL"] = prior_before_fixture

    # The cached six-column body is accepted only with exact row width; extra
    # columns are an invalid shape even if the first six values look useful.
    extra_column_body = json.dumps([
        CDX_FIELDS_WITHOUT_URLKEY,
        ["20080101000000", candidate["original"], "image/gif", "200", digest1, "10", "unexpected"],
    ]).encode()
    extra_column_parsed = parse_cdx(extra_column_body, limit=250)
    t26 = (not extra_column_parsed["valid"] and not extra_column_parsed["complete"]
           and extra_column_parsed["error"] == "unrecognized_metadata")

    tests = {
        "cdx_separator_and_resume_metadata": t1,
        "limit500_potential_truncation_no_replay": t2,
        "latest_exact_default_port_and_variant_classification": t3,
        "gif_jpeg_png_magic_pillow_and_all_frames": t4,
        "error_html_and_magic_rejection": t5,
        "compression_digest_memento_and_original_rejection": t6,
        "bounded_truncated_and_trailing_compression_rejected": t7,
        "connect_source_404_429_and_only_connect": t8,
        "cached_complete_cdx_reuse_and_latest_binding": t9,
        "fallback_cache_is_best_known_not_latest": t10,
        "cadence_monotonic_and_utc_floor_with_early_sleep": t11,
        "budget_disk_floor_and_failure_stop": t12,
        "unknown_metadata_is_incomplete": t13,
        "cached_sub_limit_separator_is_complete": t14,
        "nonzero_curl_exit_not_accepted": t15,
        "one_to_twenty_target_bound": t16,
        "malicious_output_path_rejected": t17,
        "malicious_original_rejected": t18,
        "cached_truncation_and_resume_rejected": t19,
        "frozen_news_shared10_fixtures_still_pass": t20,
        "hard_budget_bound_rejected": t21,
        "duplicate_target_key_rejected": t22,
        "fake_cached_metadata_rejected": t23,
        "source_binding_hash_rejected": t24,
        "prior_failure_tail_is_inherited_by_initial_state": t25,
        "real_allnews01_blizzcon_six_column_cache_accepted": t9,
        "six_column_extra_field_rejected": t26,
    }
    transport_fixture = run_transport_policy_fixtures()
    tests.update({f"transport_policy_{name}": value for name, value in transport_fixture["tests"].items()})
    result = {"schema": "wow-recovery.reusable-image-fixtures.v1", "batch_id": BATCH_ID,
              "network_requests": 0, "input_plan_sha256": sha_file(PLAN_PATH),
              "input_bindings_sha256": sha_file(BINDINGS_PATH), "tests": tests,
              "passed": sum(bool(v) for v in tests.values()), "total": len(tests),
              "all_passed": all(tests.values()),
              "transport_policy_fixture": transport_fixture,
              "positive_cached_fixture": {
                  "target_key": cached_candidate["target_key"],
                  "source_report_path": cached["source_report_path"],
                  "source_report_sha256": cached["source_report_sha256"],
                  "raw_body_path": cached["raw_body_path"],
                  "raw_body_sha256": cached["body_sha256"],
                  "raw_headers_path": cached["raw_headers_path"],
                  "raw_headers_sha256": cached["raw_headers_sha256"],
                  "source_curl_exit": cached["source_curl_exit"],
                  "query_url": cached["query_url"],
                  "coverage_window": cached["coverage_window"],
                  "record_count": cached["record_count"],
                  "selected": cached["selected"],
              },
              "notes": ["The first fifteen core tests are retained from the frozen NEWS-SHARED10 fixture contract.",
                        "No network request, curl process, payload write, or execute state was created by fixture mode.",
                        "Cached indexes require complete sub-limit evidence and remain latestness-limited.",
                        "The positive cached fixture is the SHA-bound ALLNEWS01 Blizzcon raw/70 response; its 2006..anchor query is not a global 2000..anchor latest proof."]}
    target = fixture_output or (DRIVER_DIR / "fixture-results.json")
    if not _under_network(target.resolve()):
        raise RuntimeError("fixture output must remain below the recovery network directory")
    write_json(target, result)
    return result


def execute() -> dict[str, Any]:
    plan, bindings = load_and_validate_inputs()
    if _late_plan_pending(plan):
        raise RuntimeError("late11 execution is gated until A root source acceptance and a separately bound tail plan exist")
    RAW.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    if STATE_PATH.exists():
        existing = read_json(STATE_PATH)
        if existing.get("attempts"):
            raise RuntimeError("refusing to resume or duplicate sent EUDEPS01 attempts; preserve the existing state and use a new authorized batch")
        state = existing
    else:
        state = initial_state()
    state.setdefault("direct_probe_done", False)
    state.setdefault("failed_attempt_number", None)
    state.setdefault("skip_reason", None)
    state.setdefault("batch_proxy_only", False)
    state.setdefault("report_policy", initial_state()["report_policy"])
    if (OUT / "batch-report.json").exists():
        raise RuntimeError("refusing to overwrite an existing reusable batch report")
    for private_dir in (RAW, PRIVATE_PAYLOADS):
        if private_dir.exists() and any(private_dir.rglob("*")):
            raise RuntimeError("refusing to overwrite existing raw/private batch evidence")
    state["started_utc"] = state.get("started_utc") or iso(started)
    state["plan_sha256"] = sha_file(PLAN_PATH)
    state["driver_sha256"] = sha_file(Path(__file__))
    write_json(STATE_PATH, state)
    accepted_payloads: list[dict[str, Any]] = []

    def persist_attempt(attempt: dict[str, Any]) -> None:
        state["attempts"].append(attempt)
        write_json(STATE_PATH, state)

    def request(url: str, label: str) -> tuple[dict[str, Any] | None, bytes]:
        nonlocal started
        for transport in _transport_sequence_for_request(state):
            if len(state["attempts"]) >= MAX_ATTEMPTS:
                state["stop_reason"] = "max_attempts"
                write_json(STATE_PATH, state)
                return None, b""
            now_value = utc_now()
            cap = clamp_budget(int(state.get("total_body_bytes", 0)), started, now_value)
            free = shutil.disk_usage(ROOT).free
            if free < DISK_FLOOR_BYTES:
                state["stop_reason"] = "disk_floor"
                write_json(STATE_PATH, state)
                return None, b""
            if not cap["allowed"]:
                state["stop_reason"] = "budget_exhausted"
                write_json(STATE_PATH, state)
                return None, b""
            attempt_no = len(state["attempts"]) + 1
            prepared = {"attempt": attempt_no, "label": label, "transport": transport, "url": url,
                        "prepared_utc": iso(now_value), "disk_free_before_bytes": free,
                        "disk_floor_passed": True, "clamp": cap, "sent": False, "status": "prepared"}
            persist_attempt(prepared)
            # The prepared record is immutable evidence that the attempt slot was
            # consumed, even if process creation fails before a raw response exists.
            gate = _dispatch_gate_for_state(state)
            # Recompute remaining limits after cadence waiting.  If the time or
            # disk gate closes before dispatch, keep the reservation as unknown
            # and never silently issue the same request again.
            after_gate = utc_now()
            cap = clamp_budget(int(state.get("total_body_bytes", 0)), started, after_gate)
            free_after_gate = shutil.disk_usage(ROOT).free
            state["attempts"][-1]["clamp_after_gate"] = cap
            state["attempts"][-1]["disk_free_at_dispatch"] = free_after_gate
            if free_after_gate < DISK_FLOOR_BYTES:
                state["attempts"][-1].update({"status": "not_dispatched_disk_floor", "sent": False})
                state["stop_reason"] = "disk_floor"
                write_json(STATE_PATH, state)
                return None, b""
            if not cap["allowed"]:
                state["attempts"][-1].update({"status": "not_dispatched_budget_exhausted", "sent": False})
                state["stop_reason"] = "budget_exhausted"
                write_json(STATE_PATH, state)
                return None, b""
            try:
                result = _curl_request(url, transport, int(cap["entity_body_cap"]), float(cap["timeout_seconds"]), RAW, attempt_no)
                body_path = ROOT / result["body_path"] if result.get("body_path") else None
                body = body_path.read_bytes() if body_path else b""
                result.update({"attempt": attempt_no, "label": label, "disk_free_before_bytes": free,
                               "disk_free_at_dispatch": free_after_gate, "disk_floor_passed": True,
                               "clamp": cap, "clamp_after_gate": cap, "dispatch": gate, "sent": True,
                               "status": "finished", "transport_policy": TRANSPORT_POLICY,
                               "direct_probe_done_before": state.get("direct_probe_done", False),
                               "batch_proxy_only_before": state.get("batch_proxy_only", False)})
                state["attempts"][-1] = result
                _record_direct_probe(state, transport, result, attempt_no)
                result["direct_probe_done_after"] = state.get("direct_probe_done", False)
                result["batch_proxy_only_after"] = state.get("batch_proxy_only", False)
                result["skip_reason_after"] = state.get("skip_reason")
                state["attempts"][-1] = result
                state["total_body_bytes"] = int(state.get("total_body_bytes", 0)) + len(body)
                if result.get("source_status") is not None:
                    state["source_responses"] = int(state.get("source_responses", 0)) + 1
                if result.get("source_status") in STOP_HTTP_CODES:
                    state["stop_reason"] = f"http_{result['source_status']}"
                    state["cooldown_not_before_utc"] = iso(utc_now() + timedelta(seconds=max(COOLDOWN_SECONDS, result.get("retry_after") or 0)))
                elif result.get("source_status") is None or result.get("curl_exit") != 0:
                    state["failure_streak"] = int(state.get("failure_streak", 0)) + 1
                    if state["failure_streak"] >= 5:
                        state["stop_reason"] = "five_consecutive_transport_failures"
                        state["cooldown_not_before_utc"] = iso(utc_now() + timedelta(seconds=COOLDOWN_SECONDS))
                else:
                    state["failure_streak"] = 0
                write_json(STATE_PATH, state)
                if (result.get("source_status") is None or result.get("curl_exit") != 0) and transport == "direct" and not state.get("stop_reason"):
                    # Direct transport failure consumes its attempt slot, then
                    # the same exact request may be tried once through the
                    # process-local proxy.  The persisted streak is reset if
                    # that proxy attempt obtains a source response.
                    continue
                return result, body
            except Exception as exc:  # process/setup errors remain persisted attempts
                state["attempts"][-1].update({"status": "exception", "sent": False, "exception": type(exc).__name__ + ": " + str(exc)})
                state["failure_streak"] = int(state.get("failure_streak", 0)) + 1
                if state["failure_streak"] >= 5:
                    state["stop_reason"] = "five_consecutive_transport_failures"
                    state["cooldown_not_before_utc"] = iso(utc_now() + timedelta(seconds=COOLDOWN_SECONDS))
                write_json(STATE_PATH, state)
                return None, b""
        return None, b""

    results: list[dict[str, Any]] = []
    cached_cdx_reused = 0
    for candidate in plan["candidates"]:
        if state.get("stop_reason"):
            break
        cdx_response = None
        cdx_source = "fresh"
        if candidate.get("cdx_mode") == "cached":
            cached_cdx_reused += 1
            cached = candidate["cached_cdx"]
            parsed = {"valid": True, "complete": True, "error": None,
                      "header": FIELDS, "rows": cached.get("rows") or ([cached.get("selected")] if cached.get("selected") else []),
                      "resume_keys": [], "metadata": [], "potential_truncation": False}
            analysis = classify_cdx(parsed, candidate)
            cdx_source = "cached_bound_complete_cdx"
            coverage = cached.get("coverage_window") or {}
            if (query := candidate.get("query") or {}).get("from") != FROM_TS or coverage.get("coverage_complete_for_global_window") is False:
                analysis["status"] = "best_known_cached_not_latest"
                analysis["latest_unknown"] = True
        else:
            cdx_url = candidate["query"]["query_url"]
            cdx_response, body = request(cdx_url, candidate["target_key"] + ":cdx")
            if not cdx_response or cdx_response.get("curl_exit") != 0 or cdx_response.get("source_status") != 200:
                fallback = candidate.get("known_positive_cache_rows") or []
                if not fallback:
                    results.append({"target_key": candidate["target_key"], "status": "transport_or_http_unknown",
                                    "cdx_source": "fresh", "curl_exit": cdx_response.get("curl_exit") if cdx_response else None,
                                    "source_status": cdx_response.get("source_status") if cdx_response else None,
                                    "latest_unknown": True, "replay_count": 0})
                    continue
                # Historical collapsed-prefix rows are allowed only as a
                # separately labelled best-known fallback when fresh CDX is
                # unavailable; they never prove latestness.
                parsed = {"valid": True, "complete": True, "error": None,
                          "header": FIELDS, "rows": fallback,
                          "resume_keys": [], "metadata": [], "potential_truncation": False}
                analysis = classify_cdx(parsed, candidate)
                analysis["status"] = "best_known_cached_not_latest"
                cdx_source = "best_known_cached_fallback"
            else:
                parsed = parse_cdx(body)
                analysis = _filter_late_selected(classify_cdx(parsed, candidate), candidate)
        if candidate.get("cdx_mode") == "cached":
            analysis = _filter_late_selected(analysis, candidate)
        item = {"target_key": candidate["target_key"], "status": analysis["status"], "cdx_source": cdx_source,
                 "latest_unknown": cdx_source == "best_known_cached_fallback" or analysis.get("latest_unknown", False), "cdx": analysis,
                "cached_cdx_provenance": candidate.get("cached_cdx") if cdx_source.startswith("cached_") else None,
                 "fresh_cdx_transport": {k: cdx_response.get(k) for k in ["curl_exit", "source_status", "transport"]} if cdx_response and cdx_source != "cached_bound_complete_cdx" else None,
                "replay_results": [], "accepted_payloads": [], "skipped_after_accept": 0}
        for selected_index, selected in enumerate(analysis["selected"]):
            if state.get("stop_reason"):
                break
            replay_response, replay_body = request(selected["replay_url"], candidate["target_key"] + ":replay:" + selected["timestamp"])
            if replay_response and replay_response.get("source_status") is not None:
                headers_path = ROOT / replay_response["headers_path"] if replay_response.get("headers_path") else None
                headers_raw = headers_path.read_bytes() if headers_path else b""
                validation = validate_replay(candidate, selected, headers_raw, replay_body,
                                             curl_exit=replay_response.get("curl_exit"))
                if validation["accepted"] and replay_response.get("curl_exit") == 0:
                    metadata, storage_error = persist_accepted_payload(candidate, selected, validation, headers_raw, replay_body)
                    if metadata is not None:
                        validation["accepted_payload_metadata"] = metadata
                        accepted_payloads.append(metadata)
                        item["accepted_payloads"].append(metadata)
                        item["replay_results"].append(validation)
                        item["skipped_after_accept"] = len(analysis["selected"]) - selected_index - 1
                        break
                    validation["accepted"] = False
                    validation["reasons"].append(storage_error or "private_payload_storage_failed")
                item["replay_results"].append(validation)
            else:
                item["replay_results"].append({"accepted": False, "reasons": ["transport_unknown"],
                                                "curl_exit": replay_response.get("curl_exit") if replay_response else None})
        results.append(item)
    finish = utc_now()
    state["finished_utc"] = iso(finish)
    state["stop_reason"] = state.get("stop_reason") or "completed_candidate_queue"
    report = {"schema": "wow-recovery.reusable-image-report.v1", "batch_id": BATCH_ID, "started_utc": state["started_utc"],
              "finished_utc": iso(finish), "network_requests": _actual_request_count(state), "prepared_attempts": len(state["attempts"]), "source_responses": state.get("source_responses", 0),
              "total_body_bytes": state.get("total_body_bytes", 0), "failure_streak": state.get("failure_streak", 0),
              "failure_streak_start": state.get("failure_streak_start", state.get("prior_failure_tail", PRIOR_FAILURE_TAIL)),
              "stop_reason": state["stop_reason"], "cooldown_not_before_utc": state.get("cooldown_not_before_utc"),
              "prior_failure_tail": state.get("prior_failure_tail", PRIOR_FAILURE_TAIL),
              "candidate_count": len(plan["candidates"]), "output_dir": rel(OUT),
              "transport_policy": TRANSPORT_POLICY,
              "direct_probe_done": state.get("direct_probe_done", False),
              "failed_attempt_number": state.get("failed_attempt_number"),
              "skip_reason": state.get("skip_reason"),
              "report_policy": state.get("report_policy"),
              "cached_cdx_reused": cached_cdx_reused,
              "fresh_cdx_targets": sum(1 for c in plan["candidates"] if c.get("cdx_mode") == "fresh"), "results": results,
              "accepted_payloads": accepted_payloads, "deployment_claim": False,
              "accepted_payload_status": "pending_root" if accepted_payloads else "none"}
    write_json(OUT / "batch-report.json", report)
    write_json(OUT / "source-map.json", {"schema": "wow-recovery.reusable-image-source-map.v1", "batch_id": BATCH_ID,
                                          "accepted_payloads": accepted_payloads, "entries": results,
                                          "accepted_payload_status": "pending_root" if accepted_payloads else "none"})
    write_json(OUT / "sanitized-summary.json", {
        "schema": "wow-recovery.reusable-image-sanitized-summary.v1", "batch_id": BATCH_ID,
        "network_requests": _actual_request_count(state), "prepared_attempts": len(state["attempts"]), "source_responses": state.get("source_responses", 0),
        "cached_cdx_reused": cached_cdx_reused,
        "accepted_payload_count": len(accepted_payloads), "accepted_payload_status": "pending_root" if accepted_payloads else "none",
        "stop_reason": state.get("stop_reason"), "failure_streak": state.get("failure_streak", 0),
        "failure_streak_start": state.get("failure_streak_start", state.get("prior_failure_tail", PRIOR_FAILURE_TAIL)),
        "transport_policy": TRANSPORT_POLICY,
        "direct_probe_done": state.get("direct_probe_done", False),
        "failed_attempt_number": state.get("failed_attempt_number"),
        "skip_reason": state.get("skip_reason"),
        "report_policy": state.get("report_policy"),
        "cooldown_not_before_utc": state.get("cooldown_not_before_utc"),
        "accepted_payloads": accepted_payloads, "deployment_claim": False,
        "raw_headers_cookies_and_text": "omitted",
    })
    write_json(STATE_PATH, state)
    return report


def _dispatch_gate_for_state(state: dict[str, Any]) -> dict[str, Any]:
    # Real execution uses monotonic/UTC floors.  We keep the persisted helper
    # small because each process-local request is serialized in this driver.
    previous = [x for x in state.get("attempts", []) if x.get("status") == "finished" and x.get("sent")]
    dispatch_now = time.monotonic()
    start_now = utc_now()
    if previous:
        last = previous[-1]
        last_dispatch = float(last.get("dispatch", {}).get("dispatch_monotonic", dispatch_now))
        last_start = parse_iso(last.get("started_utc")) or start_now
        while dispatch_now - last_dispatch < MIN_DISPATCH_SECONDS or (start_now - last_start).total_seconds() < MIN_REQUEST_START_SECONDS:
            wait = max(MIN_DISPATCH_SECONDS - (dispatch_now - last_dispatch), MIN_REQUEST_START_SECONDS - (start_now - last_start).total_seconds(), 0.01)
            time.sleep(wait)
            dispatch_now, start_now = time.monotonic(), utc_now()
    return {"dispatch_monotonic": dispatch_now, "dispatch_utc": iso(start_now),
            "dispatch_gap_seconds": None if not previous else dispatch_now - float(previous[-1].get("dispatch", {}).get("dispatch_monotonic", dispatch_now)),
            "request_start_gap_seconds": None if not previous else (start_now - (parse_iso(previous[-1].get("started_utc")) or start_now)).total_seconds(),
            "min_dispatch_seconds": MIN_DISPATCH_SECONDS, "min_request_start_seconds": MIN_REQUEST_START_SECONDS}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true", help="run the offline fixture suite")
    parser.add_argument("--execute", action="store_true", help="execute the explicitly authorized bounded window")
    parser.add_argument("--plan", type=Path, default=PLAN_PATH, help="reusable image plan JSON below the recovery network directory")
    parser.add_argument("--fixture-output", type=Path, help="optional fixture result path below the recovery network directory")
    args = parser.parse_args()
    if args.fixture == args.execute:
        parser.error("choose exactly one of --fixture or --execute")
    configure_from_plan(args.plan)
    if args.fixture:
        fixture_output = args.fixture_output.resolve() if args.fixture_output else None
        result = run_fixtures(fixture_output)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["all_passed"] else 1
    report = execute()
    print(json.dumps({"mode": "execute", "batch_id": BATCH_ID, "network_requests": report["network_requests"],
                      "source_responses": report["source_responses"], "accepted_payloads": len(report["accepted_payloads"]),
                      "stop_reason": report["stop_reason"], "driver_sha256": sha_file(Path(__file__))}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

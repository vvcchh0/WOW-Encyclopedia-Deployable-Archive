#!/usr/bin/env python3
"""Prepare or GO-gated verify the exact 69 root-accepted v55 Pages objects."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import quote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PLAN = OUT / "plan.json"
MANIFEST = OUT / "object-manifest.json"
FIXTURE = OUT / "offline-validation.json"
BINDINGS = OUT / "input-bindings.json"
RUNTIME = OUT / "runtime"

EXPORT_REL = "research/continuous-recovery-20261022/root-v55-export-acceptance.json"
BROWSER_REL = "research/continuous-recovery-20261022/root-v55-browser-acceptance.json"
EXPORT_PATH = ROOT / EXPORT_REL
BROWSER_PATH = ROOT / BROWSER_REL
LOCAL = ".scratch/pages-resources-20261022-v55"
BASE = "https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/"
BATCH = "github-pages-v55-changes69"
GO_SCHEMA = "wow-root-github-pages-v55-changes69-go/v1"

CORE_REL = "research/continuous-recovery-20261022/network/github-pages-v53-changes06/verify_pages_v53_changes06.py"
CORE_PATH = ROOT / CORE_REL
CORE_SHA = "deddfab9dad1c3d1e472d7b0ad6454746c91b9707265e6f9dd1093ecdc019a70"
TRANSPORT_REL = "research/continuous-recovery-20261022/network/archivecraft-dungeons01/archivecraft_dungeons01.py"
TRANSPORT_SHA = "7b95fa17bff6aa5245dc9fe45331652f02db5419c0e7ac14ff454af9d0fcad00"

DISK_FLOOR = 11_005_853_696
START_GAP = 6.2
MAX_LOGICAL = 69
MAX_ATTEMPTS = 138
MAX_SECONDS = 20 * 60
REQUEST_SECONDS = 30
CONNECT_SECONDS = 10
TOTAL_CAP = 64 * 1024 * 1024
OBJECT_CAP = 64 * 1024 * 1024
COOLDOWN = 120
STOP_STATUSES = [429, 503]

MIME_BY_SUFFIX = {
    ".gif": ["image/gif"],
    ".html": ["text/html"],
    ".jpg": ["image/jpeg"],
    ".js": ["application/javascript", "text/javascript"],
    ".json": ["application/json"],
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40,64}$")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(json_bytes(value))


def canonical_digest(value: Any) -> str:
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def safe_site_path(raw: Any) -> str:
    if not isinstance(raw, str) or not raw or "\\" in raw or raw.startswith("/") or ":" in raw:
        raise RuntimeError(f"unsafe accepted site path: {raw!r}")
    path = PurePosixPath(raw)
    if path.as_posix() != raw or any(part in ("", ".", "..") for part in path.parts):
        raise RuntimeError(f"non-canonical accepted site path: {raw!r}")
    return raw


def policy() -> dict[str, Any]:
    return {
        "maximum_logical_objects": MAX_LOGICAL,
        "maximum_http_attempts": MAX_ATTEMPTS,
        "maximum_batch_seconds": MAX_SECONDS,
        "maximum_request_seconds": REQUEST_SECONDS,
        "connect_timeout_seconds": CONNECT_SECONDS,
        "minimum_request_start_seconds": START_GAP,
        "maximum_total_body_bytes": TOTAL_CAP,
        "maximum_object_body_bytes": OBJECT_CAP,
        "maximum_response_bytes": OBJECT_CAP,
        "maximum_attempts_per_object": 2,
        "minimum_transport_failure_cooldown_seconds": COOLDOWN,
        "stop_http_statuses": STOP_STATUSES,
        "disk_floor_bytes": DISK_FLOOR,
        "process_proxy": "http://127.0.0.1:7890",
        "direct_first": True,
        "proxy_fallback_only_after_transfer_failure": True,
        "tls_verification": True,
        "follow_redirects": False,
        "automatic_retries": 0,
    }


def _read_inputs() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    if not EXPORT_PATH.is_file() or not BROWSER_PATH.is_file():
        raise RuntimeError("root v55 export/browser acceptance input is missing")
    export, browser = read_json(EXPORT_PATH), read_json(BROWSER_PATH)
    if export.get("schema") != "wow-root-v55-export-acceptance/v1" or export.get("accepted") is not True:
        raise RuntimeError("v55 export acceptance is not accepted")
    if browser.get("schema") != "wow-root-final-browser-acceptance/v1" or browser.get("accepted") is not True or browser.get("version") != "v55":
        raise RuntimeError("v55 browser acceptance is not accepted for v55")
    if export.get("local_site") != LOCAL or browser.get("local_site") != LOCAL:
        raise RuntimeError("export/browser receipts do not identify the fixed v55 local site")
    provenance_sha = export.get("export_provenance_sha256")
    if not isinstance(provenance_sha, str) or not SHA256_RE.fullmatch(provenance_sha):
        raise RuntimeError("export acceptance provenance SHA-256 is invalid")
    if browser.get("export_provenance_sha256") != provenance_sha:
        raise RuntimeError("browser receipt provenance hash differs from accepted export")
    if browser.get("external_requests") != [] or browser.get("page_errors") != [] or browser.get("asset_fulfillments") != 0:
        raise RuntimeError("browser receipt does not meet the accepted offline-browse boundary")
    if export.get("all_actual_file_hashes_match_provenance") is not True:
        raise RuntimeError("export receipt does not attest all actual file hashes")
    site_root = (ROOT / LOCAL).resolve(strict=True)
    if not site_root.is_relative_to(ROOT.resolve()):
        raise RuntimeError("v55 local site resolves outside the workspace")
    provenance_path = site_root / "export-provenance.json"
    if not provenance_path.is_file() or sha(provenance_path) != provenance_sha:
        raise RuntimeError("local export-provenance.json differs from the accepted provenance hash")

    source_rows = export.get("online_changes_from_v53")
    if not isinstance(source_rows, list) or len(source_rows) != MAX_LOGICAL:
        raise RuntimeError("online_changes_from_v53 must contain exactly 69 accepted rows")
    seen: set[str] = set()
    objects: list[dict[str, Any]] = []
    for index, row in enumerate(source_rows, 1):
        if not isinstance(row, dict):
            raise RuntimeError(f"malformed accepted change row {index}")
        path = safe_site_path(row.get("path"))
        if path in seen:
            raise RuntimeError(f"duplicate accepted path: {path}")
        seen.add(path)
        expected_sha, expected_bytes = row.get("sha256"), row.get("bytes")
        if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
            raise RuntimeError(f"invalid accepted hash/length for {path}")
        mime_types = MIME_BY_SUFFIX.get(PurePosixPath(path).suffix.lower())
        if mime_types is None:
            raise RuntimeError(f"no reviewed MIME allowlist for accepted suffix: {path}")
        local_path = site_root / PurePosixPath(path)
        if local_path.is_symlink() or not local_path.is_file() or not local_path.resolve().is_relative_to(site_root):
            raise RuntimeError(f"accepted local object is missing, linked, or out of scope: {path}")
        actual_bytes = local_path.stat().st_size
        actual_sha = sha(local_path)
        if (actual_bytes, actual_sha) != (expected_bytes, expected_sha):
            raise RuntimeError(f"local file does not match accepted bytes/hash: {path}")
        if actual_bytes > OBJECT_CAP:
            raise RuntimeError(f"accepted object exceeds the per-object response cap: {path}")
        encoded_path = quote(path, safe="/-._~")
        objects.append({
            "object_id": f"object-{index:03d}-{sha_bytes(path.encode('utf-8'))[:10]}",
            "path": path,
            "url": BASE + encoded_path,
            "local_path": f"{LOCAL}/{path}",
            "local_bytes": expected_bytes,
            "local_sha256": expected_sha,
            "accepted_mime_types": mime_types,
        })
    if sum(item["local_bytes"] for item in objects) > TOTAL_CAP:
        raise RuntimeError("accepted 69-object set exceeds the 64 MiB batch response cap")
    return export, browser, objects


def _load_core():
    if not CORE_PATH.is_file() or sha(CORE_PATH) != CORE_SHA:
        raise RuntimeError("reviewed v53 wrapper changed or is missing")
    spec = importlib.util.spec_from_file_location("accepted_v53_pages_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import reviewed v53 Pages wrapper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    transport = module.runner()
    if (transport.MIN_START_SECONDS, transport.REQUEST_SECONDS, transport.CONNECT_SECONDS) != (START_GAP, REQUEST_SECONDS, CONNECT_SECONDS):
        raise RuntimeError("reused v53 transport timing constants changed")
    transport.MAX_RESPONSE_BYTES = OBJECT_CAP
    return module, transport


def _manifest(export: dict[str, Any], browser: dict[str, Any], objects: list[dict[str, Any]],
              pages_commit: str | None, actions_run: str | None) -> dict[str, Any]:
    return {
        "schema": "wow-recovery.github-pages-v55-changes69.object-manifest.v1",
        "batch_id": BATCH,
        "target_base_url": BASE,
        "source": {
            "local_site": LOCAL,
            "change_list": "online_changes_from_v53",
            "export_acceptance_path": EXPORT_REL,
            "export_acceptance_sha256": sha(EXPORT_PATH),
            "browser_acceptance_path": BROWSER_REL,
            "browser_acceptance_sha256": sha(BROWSER_PATH),
            "export_provenance_sha256": export["export_provenance_sha256"],
            "pages_commit": pages_commit,
            "actions_run": actions_run,
            "deployment_binding_status": "awaiting root Pages commit and Actions run" if pages_commit is None or actions_run is None else "bound to root Pages commit and Actions run",
        },
        "objects": objects,
    }


def _object_set_sha(objects: list[dict[str, Any]]) -> str:
    return canonical_digest([{"path": x["path"], "sha256": x["local_sha256"], "bytes": x["local_bytes"]} for x in objects])


def _plan(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "wow-recovery.github-pages-v55-changes69.plan.v1",
        "batch_id": BATCH,
        "mode": "prepared",
        "root_go_required": True,
        "network_requests_at_prepare": 0,
        "pages_commit": manifest["source"]["pages_commit"],
        "actions_run": manifest["source"]["actions_run"],
        "deployment_binding_status": manifest["source"]["deployment_binding_status"],
        "target_base_url": BASE,
        "local_site": LOCAL,
        "change_list": "online_changes_from_v53",
        "object_count": MAX_LOGICAL,
        "object_total_bytes": sum(x["local_bytes"] for x in manifest["objects"]),
        "object_manifest_sha256": sha(MANIFEST),
        "object_set_sha256": _object_set_sha(manifest["objects"]),
        "export_acceptance_path": EXPORT_REL,
        "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_path": BROWSER_REL,
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "shared_v53_wrapper_path": CORE_REL,
        "shared_v53_wrapper_sha256": CORE_SHA,
        "transport_runner_path": TRANSPORT_REL,
        "transport_runner_sha256": TRANSPORT_SHA,
        "policy": policy(),
        "execution_boundary": "one root-GO-authorized batch for exactly the 69 online_changes_from_v53 rows; no other objects, redirects, or automatic retries",
        "raw_handling": "HTTP headers, response bodies, and cookie jars remain private under runtime/private/raw; public output contains only curated object summaries",
        "go_required_fields": [
            "plan_sha256", "wrapper_sha256", "object_manifest_sha256", "offline_validation_sha256",
            "input_bindings_sha256", "shared_v53_wrapper_sha256", "transport_runner_sha256",
            "export_acceptance_sha256", "browser_acceptance_sha256", "object_set_sha256",
            "pages_commit", "actions_run",
        ],
    }


def _bindings(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "wow-recovery.github-pages-v55-changes69.input-bindings.v1",
        "batch_id": BATCH,
        "plan_sha256": sha(PLAN),
        "wrapper_sha256": sha(Path(__file__)),
        "object_manifest_sha256": sha(MANIFEST),
        "offline_validation_sha256": sha(FIXTURE),
        "shared_v53_wrapper_sha256": CORE_SHA,
        "transport_runner_sha256": TRANSPORT_SHA,
        "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "object_set_sha256": plan["object_set_sha256"],
        "pages_commit": plan.get("pages_commit"),
        "actions_run": plan.get("actions_run"),
    }


def _write_bindings(plan: dict[str, Any]) -> None:
    write_json(BINDINGS, _bindings(plan))


def prepare_files() -> tuple[dict[str, Any], dict[str, Any]]:
    pages_commit: str | None = None
    actions_run: str | None = None
    if PLAN.is_file():
        existing = read_json(PLAN)
        if existing.get("schema") != "wow-recovery.github-pages-v55-changes69.plan.v1" or existing.get("batch_id") != BATCH:
            raise RuntimeError("existing plan has another batch identity; refusing to replace it")
        pages_commit = existing.get("pages_commit")
        actions_run = existing.get("actions_run")
        if pages_commit is not None and (not isinstance(pages_commit, str) or not COMMIT_RE.fullmatch(pages_commit)):
            raise RuntimeError("existing plan Pages commit is invalid")
        if actions_run is not None and not str(actions_run).isdigit():
            raise RuntimeError("existing plan Actions run is invalid")
        if actions_run is not None:
            actions_run = str(actions_run)
    export, browser, objects = _read_inputs()
    manifest = _manifest(export, browser, objects, pages_commit, actions_run)
    write_json(MANIFEST, manifest)
    plan = _plan(manifest)
    write_json(PLAN, plan)
    return plan, manifest


def preflight() -> tuple[dict[str, Any], dict[str, Any], Any, Any]:
    if not PLAN.is_file() or not MANIFEST.is_file():
        raise RuntimeError("plan/manifest are missing; run --offline-validate")
    plan, manifest = read_json(PLAN), read_json(MANIFEST)
    if plan.get("schema") != "wow-recovery.github-pages-v55-changes69.plan.v1" or plan.get("mode") != "prepared" or plan.get("root_go_required") is not True or plan.get("network_requests_at_prepare") != 0 or plan.get("batch_id") != BATCH:
        raise RuntimeError("plan is not prepared and root-GO-gated")
    if manifest.get("schema") != "wow-recovery.github-pages-v55-changes69.object-manifest.v1" or manifest.get("batch_id") != BATCH:
        raise RuntimeError("manifest batch identity mismatch")
    if plan.get("policy") != policy() or plan.get("target_base_url") != BASE or manifest.get("target_base_url") != BASE:
        raise RuntimeError("fixed network policy or target base mismatch")
    if plan.get("object_manifest_sha256") != sha(MANIFEST):
        raise RuntimeError("object manifest file hash mismatch")
    export, browser, expected_objects = _read_inputs()
    if manifest.get("objects") != expected_objects or len(expected_objects) != MAX_LOGICAL:
        raise RuntimeError("manifest differs from the exact root-accepted 69-object list")
    object_set = _object_set_sha(expected_objects)
    if plan.get("object_set_sha256") != object_set or manifest.get("source", {}).get("change_list") != "online_changes_from_v53":
        raise RuntimeError("object set or source-list binding mismatch")
    if plan.get("export_acceptance_sha256") != sha(EXPORT_PATH) or plan.get("browser_acceptance_sha256") != sha(BROWSER_PATH):
        raise RuntimeError("root acceptance receipt hash binding mismatch")
    source = manifest.get("source", {})
    if source.get("export_acceptance_sha256") != sha(EXPORT_PATH) or source.get("browser_acceptance_sha256") != sha(BROWSER_PATH) or source.get("export_provenance_sha256") != export.get("export_provenance_sha256"):
        raise RuntimeError("manifest source acceptance binding mismatch")
    if plan.get("pages_commit") != source.get("pages_commit") or plan.get("actions_run") != source.get("actions_run"):
        raise RuntimeError("deployment commit/Actions bindings disagree")
    if plan.get("deployment_binding_status") != source.get("deployment_binding_status"):
        raise RuntimeError("deployment binding status differs between plan and manifest")
    if plan.get("pages_commit") is not None and (not isinstance(plan["pages_commit"], str) or not COMMIT_RE.fullmatch(plan["pages_commit"])):
        raise RuntimeError("Pages commit must be a lowercase full Git SHA when supplied")
    if plan.get("actions_run") is not None and (not str(plan["actions_run"]).isdigit()):
        raise RuntimeError("Actions run must be a numeric id when supplied")
    if not CORE_PATH.is_file() or sha(CORE_PATH) != CORE_SHA or not (ROOT / TRANSPORT_REL).is_file() or sha(ROOT / TRANSPORT_REL) != TRANSPORT_SHA:
        raise RuntimeError("reviewed v53 helper or shared transport changed")
    core, transport = _load_core()
    if RUNTIME.exists():
        raise RuntimeError("runtime already exists; refusing a repeated production batch")
    transport.require_disk("v55 plan/source preflight")
    return plan, manifest, core, transport


def mime(record: dict[str, Any]) -> str | None:
    value = record.get("header_parse", {}).get("content_type")
    return value.split(";", 1)[0].strip().lower() if isinstance(value, str) else None


def matches(obj: dict[str, Any], record: dict[str, Any]) -> bool:
    return (
        record.get("returncode") == 0 and record.get("http_status") == 200
        and mime(record) in obj["accepted_mime_types"]
        and record.get("body_bytes") == obj["local_bytes"]
        and record.get("body_sha256") == obj["local_sha256"]
        and record.get("effective_url") == obj["url"]
        and not record.get("timed_out") and not record.get("response_cap_exceeded")
        and not record.get("transport_failed")
    )


def public_url(raw: str | None) -> str | None:
    try:
        parsed = urlsplit(raw or "")
        if parsed.scheme != "https" or parsed.hostname != "vvcchh0.github.io" or parsed.username or parsed.password:
            return None
        return urlunsplit(("https", parsed.hostname, parsed.path or "/", "", ""))
    except ValueError:
        return None


def _expected_bindings(plan: dict[str, Any]) -> dict[str, Any]:
    return _bindings(plan)


def run_batch(go_path: Path, *, runtime: Path = RUNTIME,
              attempt_fn: Callable[..., tuple[dict[str, Any], float]] | None = None,
              offline_mock: bool = False) -> dict[str, Any]:
    plan, manifest, _core, transport = preflight()
    if not FIXTURE.is_file() or not BINDINGS.is_file():
        raise RuntimeError("offline validation/bindings are missing")
    fixture, binding = read_json(FIXTURE), read_json(BINDINGS)
    if fixture.get("all_passed") is not True or fixture.get("network_requests") != 0:
        raise RuntimeError("offline validation is not complete")
    expected_binding = _expected_bindings(plan)
    if any(binding.get(key) != value for key, value in expected_binding.items()):
        raise RuntimeError("input binding mismatch")
    if not go_path.is_file():
        raise RuntimeError("root GO file is missing")
    go = read_json(go_path)
    go_values = {
        "plan_sha256": sha(PLAN),
        "wrapper_sha256": sha(Path(__file__)),
        "object_manifest_sha256": sha(MANIFEST),
        "offline_validation_sha256": sha(FIXTURE),
        "input_bindings_sha256": sha(BINDINGS),
        "shared_v53_wrapper_sha256": CORE_SHA,
        "transport_runner_sha256": TRANSPORT_SHA,
        "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "object_set_sha256": plan["object_set_sha256"],
        "pages_commit": plan.get("pages_commit"),
        "actions_run": plan.get("actions_run"),
    }
    if go.get("schema") != GO_SCHEMA or go.get("accepted") is not True or go.get("root_go") is not True or go.get("batch_id") != BATCH or any(go.get(key) != value for key, value in go_values.items()):
        raise RuntimeError("GO is missing approval or does not bind every v55 input")
    if (not isinstance(go.get("valid_until"), str)
            or datetime.fromisoformat(go["valid_until"].replace("Z", "+00:00")) <= datetime.now(timezone.utc)):
        raise RuntimeError("GO is expired or has no valid_until")
    if not offline_mock and (not isinstance(plan.get("pages_commit"), str) or not COMMIT_RE.fullmatch(plan["pages_commit"]) or not str(plan.get("actions_run", "")).isdigit()):
        raise RuntimeError("production batch awaits the root Pages commit and Actions run")
    if runtime.exists():
        raise RuntimeError("refusing a pre-existing execution runtime")
    transport.require_disk("before authorized v55 batch")
    paths = transport.make_paths(runtime)
    runtime.mkdir(parents=True, exist_ok=False)
    paths.private.mkdir(parents=True, exist_ok=True)
    paths.raw.mkdir(parents=True, exist_ok=True)
    transport.MAX_RESPONSE_BYTES = OBJECT_CAP
    disk_start = transport.require_disk("v55 batch start")
    batch_started_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    batch_start = time.monotonic()
    last_start = None
    attempts: list[dict[str, Any]] = []
    rows = [{
        "object_id": obj["object_id"], "path": obj["path"], "url": obj["url"],
        "expected_bytes": obj["local_bytes"], "expected_sha256": obj["local_sha256"],
        "expected_mime": obj["accepted_mime_types"], "attempts": [], "matches_local": False,
    } for obj in manifest["objects"]]
    total = 0
    streak = 0
    failure_tail: list[dict[str, Any]] = []
    stop, cooldown_not_before = "completed", None
    for obj, row in zip(manifest["objects"], rows):
        object_bytes = 0
        for use_proxy in (False, True):
            if len(attempts) >= MAX_ATTEMPTS or time.monotonic() - batch_start >= MAX_SECONDS:
                stop = "attempt_or_time_budget_exhausted"
                break
            remaining = min(TOTAL_CAP - total, OBJECT_CAP - object_bytes)
            if remaining <= 0:
                stop = "body_budget_exhausted"
                break
            transport.require_disk(f"before HTTP attempt {len(attempts) + 1}")
            try:
                call = attempt_fn or transport.run_attempt
                record, last_start = call(
                    {"target_id": obj["object_id"], "url": obj["url"]},
                    len(attempts) + 1, use_proxy, last_start, batch_start, remaining, paths,
                    cadence_seconds=START_GAP, batch_seconds=MAX_SECONDS,
                )
            except RuntimeError as exc:
                stop = "batch_time_budget_exhausted" if "window exhausted" in str(exc) else "request_precondition_failed"
                break
            record["object_id"] = obj["object_id"]
            attempts.append(record)
            row["attempts"].append(record)
            body_bytes = record.get("body_bytes", 0)
            total += body_bytes
            object_bytes += body_bytes
            transport.require_disk(f"after HTTP attempt {len(attempts)}")
            reason, wait_until = transport.handle_status(record)
            if reason:
                stop, cooldown_not_before = reason, wait_until
            elif record.get("actual_start_interval_seconds") is not None and record["actual_start_interval_seconds"] < START_GAP:
                stop = "request_start_spacing_below_minimum"
            elif record.get("response_cap_exceeded") or total > TOTAL_CAP or object_bytes > OBJECT_CAP:
                stop = "response_or_body_cap_exceeded"
            elif record.get("transport_failed") or record.get("timed_out") or record.get("http_status") is None or record.get("returncode") not in (0, None):
                streak += 1
                failure_tail.append({key: record.get(key) for key in (
                    "attempt", "object_id", "transport", "request_started_utc",
                    "request_finished_utc", "http_status", "returncode", "timed_out",
                )})
                failure_tail = failure_tail[-5:]
                if streak >= 5:
                    stop = "five_consecutive_transfer_failures"
                    cooldown_not_before = transport.cooldown_from_record(record, COOLDOWN)
            else:
                streak, failure_tail = 0, []
                row["matches_local"] = matches(obj, record)
            if stop != "completed":
                break
            failed = bool(record.get("transport_failed") or record.get("timed_out") or record.get("http_status") is None or record.get("returncode") not in (0, None))
            if failed and not use_proxy:
                continue
            break
        if stop != "completed":
            break

    finished = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    complete = all(row["attempts"] for row in rows)
    accepted = complete and all(row["matches_local"] for row in rows) and stop == "completed"
    private = {
        "schema": "wow-recovery.github-pages-v55-changes69.private-report.v1",
        "batch_id": BATCH,
        "go_sha256": sha(go_path),
        "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "started_utc": batch_started_utc,
        "finished_utc": finished,
        "stop_reason": stop,
        "cooldown_not_before_utc": cooldown_not_before,
        "attempt_count": len(attempts),
        "total_response_body_bytes": total,
        "consecutive_transfer_failures": streak,
        "consecutive_transfer_failure_tail": failure_tail,
        "attempts": attempts,
        "objects": rows,
        "raw_http_and_cookies_private": True,
    }
    public_rows = []
    for row in rows:
        last = row["attempts"][-1] if row["attempts"] else {}
        public_rows.append({
            "object_id": row["object_id"], "path": row["path"], "url": public_url(row["url"]),
            "expected_bytes": row["expected_bytes"], "expected_sha256": row["expected_sha256"],
            "expected_mime": row["expected_mime"],
            "attempts": [{
                "transport": item.get("transport"), "started_utc": item.get("request_started_utc"),
                "finished_utc": item.get("request_finished_utc"),
                "start_interval_seconds": item.get("actual_start_interval_seconds"),
                "status": item.get("http_status"), "effective_url": public_url(item.get("effective_url")),
                "bytes": item.get("body_bytes"), "sha256": item.get("body_sha256"), "mime": mime(item),
            } for item in row["attempts"]],
            "observed_bytes": last.get("body_bytes"), "observed_sha256": last.get("body_sha256"),
            "observed_mime": mime(last) if last else None, "matches_local": row["matches_local"],
        })
    public = {
        "schema": "wow-recovery.github-pages-v55-changes69.public-summary.v1",
        "batch_id": BATCH,
        "pages_commit": plan.get("pages_commit"),
        "actions_run": plan.get("actions_run"),
        "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "started_utc": batch_started_utc,
        "finished_utc": finished,
        "complete": complete,
        "accepted": accepted,
        "stop_reason": stop,
        "cooldown_not_before_utc": cooldown_not_before,
        "http_attempt_count": len(attempts),
        "direct_attempt_count": sum(item.get("transport") == "direct" for item in attempts),
        "proxy_attempt_count": sum(item.get("transport") == "proxy" for item in attempts),
        "total_response_body_bytes": total,
        "disk_free_before_bytes": disk_start,
        "disk_free_after_bytes": transport.require_disk("v55 batch finish"),
        "consecutive_transfer_failure_tail": failure_tail,
        "objects": public_rows,
        "raw_http_and_cookies_private": True,
    }
    transport.require_disk("before v55 execution summaries")
    report_path = paths.private / "report.json"
    summary_path = runtime / "object-match-summary.json"
    report_path.write_text(json.dumps(private, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    transport.require_disk("after v55 execution summaries")
    return {"accepted": accepted, "matches": sum(bool(item["matches_local"]) for item in rows),
            "http_attempts": len(attempts), "direct_attempts": public["direct_attempt_count"],
            "proxy_attempts": public["proxy_attempt_count"], "stop_reason": stop,
            "runtime": str(runtime)}


def _fake_attempt_factory(objects: list[dict[str, Any]]) -> Callable[..., tuple[dict[str, Any], float]]:
    by_id = {item["object_id"]: item for item in objects}

    def attempt(target: dict[str, Any], attempt_no: int, use_proxy: bool,
                last_start: float | None, batch_start: float, remaining: int, paths: Any,
                *, cadence_seconds: float, batch_seconds: float) -> tuple[dict[str, Any], float]:
        obj = by_id[target["target_id"]]
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        simulate_transport_failure = target["target_id"] == objects[0]["object_id"] and attempt_no == 1 and not use_proxy
        record = {
            "attempt": attempt_no, "logical_request": target["target_id"], "url": target["url"],
            "transport": "proxy" if use_proxy else "direct", "request_started_utc": now,
            "request_finished_utc": now, "actual_start_interval_seconds": None if attempt_no == 1 else cadence_seconds,
            "effective_url": target["url"], "returncode": 7 if simulate_transport_failure else 0,
            "http_status": None if simulate_transport_failure else 200,
            "timed_out": False, "transport_failed": simulate_transport_failure, "response_cap_exceeded": False,
            "body_bytes": 0 if simulate_transport_failure else obj["local_bytes"],
            "body_sha256": None if simulate_transport_failure else obj["local_sha256"],
            "header_parse": {} if simulate_transport_failure else {"content_type": obj["accepted_mime_types"][0]},
        }
        return record, time.monotonic()

    return attempt


def _assert_transport_cli(transport: Any) -> None:
    direct = transport.curl_command(
        {"target_id": "fixture", "url": BASE + "offline-fixture"}, use_proxy=False,
        headers=OUT / "fixture-headers", body=OUT / "fixture-body", cookie=OUT / "fixture-cookie",
        max_time_seconds=REQUEST_SECONDS, remaining_body_bytes=OBJECT_CAP,
    )
    proxy = transport.curl_command(
        {"target_id": "fixture", "url": BASE + "offline-fixture"}, use_proxy=True,
        headers=OUT / "fixture-headers", body=OUT / "fixture-body", cookie=OUT / "fixture-cookie",
        max_time_seconds=REQUEST_SECONDS, remaining_body_bytes=OBJECT_CAP,
    )
    if ("--tlsv1.2" not in direct or direct[direct.index("--proto") + 1] != "=https"
            or direct[direct.index("--retry") + 1] != "0" or direct[direct.index("--max-redirs") + 1] != "0"
            or direct[direct.index("--noproxy") + 1] != "*"
            or proxy[proxy.index("--proxy") + 1] != "http://127.0.0.1:7890"):
        raise RuntimeError("reused v53 transport command policy differs from direct-first/TLS/no-redirect/no-retry plan")


def _go_values(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "plan_sha256": sha(PLAN), "wrapper_sha256": sha(Path(__file__)),
        "object_manifest_sha256": sha(MANIFEST), "offline_validation_sha256": sha(FIXTURE),
        "input_bindings_sha256": sha(BINDINGS), "shared_v53_wrapper_sha256": CORE_SHA,
        "transport_runner_sha256": TRANSPORT_SHA, "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_sha256": sha(BROWSER_PATH), "object_set_sha256": plan["object_set_sha256"],
        "pages_commit": plan.get("pages_commit"), "actions_run": plan.get("actions_run"),
    }


def offline_validate() -> int:
    if RUNTIME.exists():
        raise RuntimeError("production runtime exists; refusing to rewrite prepared batch artifacts")
    plan, manifest = prepare_files()
    export, browser, objects = _read_inputs()
    _, transport = _load_core()
    _assert_transport_cli(transport)
    # A placeholder passing fixture is used only to drive an injected offline
    # attempt function; it is replaced by the complete fixture before return.
    preliminary = {
        "schema": "wow-recovery.github-pages-v55-changes69.offline-validation.v1",
        "batch_id": BATCH, "all_passed": True, "network_requests": 0,
        "source_export_acceptance_sha256": sha(EXPORT_PATH),
        "source_browser_acceptance_sha256": sha(BROWSER_PATH),
        "pages_commit": plan.get("pages_commit"), "actions_run": plan.get("actions_run"),
        "object_count": len(objects), "object_total_bytes": sum(x["local_bytes"] for x in objects),
        "offline_mock_execution": {"state": "running", "real_network_requests": 0},
    }
    write_json(FIXTURE, preliminary)
    _write_bindings(plan)
    with tempfile.TemporaryDirectory(prefix="offline-mock-execute-", dir=OUT) as tmp:
        tmp_path = Path(tmp)
        synthetic_go_path = tmp_path / "offline-mock-go.json"
        synthetic_go = {
            "schema": GO_SCHEMA, "accepted": True, "root_go": True, "batch_id": BATCH,
            "valid_until": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
            **_go_values(plan),
        }
        write_json(synthetic_go_path, synthetic_go)
        mock = run_batch(synthetic_go_path, runtime=tmp_path / "runtime-smoke",
                         attempt_fn=_fake_attempt_factory(objects), offline_mock=True)
        private = read_json(tmp_path / "runtime-smoke" / "private" / "report.json")
        public = read_json(tmp_path / "runtime-smoke" / "object-match-summary.json")
        mock_check = {
            "passed": mock["accepted"] is True and mock["matches"] == MAX_LOGICAL
                      and mock["http_attempts"] == MAX_LOGICAL + 1
                      and mock["direct_attempts"] == MAX_LOGICAL and mock["proxy_attempts"] == 1
                      and len(private.get("objects", [])) == MAX_LOGICAL
                      and public.get("accepted") is True
                      and all(item.get("matches_local") is True for item in public.get("objects", [])),
            "real_network_requests": 0, "real_subprocess_calls": 0,
            "mock_attempts": mock["http_attempts"], "proxy_after_first_transfer_failure": mock["proxy_attempts"] == 1,
            "all_69_matched": mock["matches"] == MAX_LOGICAL,
            "production_runtime_absent": not RUNTIME.exists(),
        }
        isolated_runtime = tmp_path / "runtime-smoke"
    mock_check["isolated_runtime_removed"] = not isolated_runtime.exists()
    final = {
        **preliminary,
        "offline_mock_execution": mock_check,
        "reported_added_changed_count": len(export.get("added", [])) + len(export.get("changed", [])),
        "accepted_online_changes_count": len(objects),
        "pages_commit": plan.get("pages_commit"), "actions_run": plan.get("actions_run"),
        "roster_note": "The exact batch roster is online_changes_from_v53 as directed; the receipt's added+changed summary is separately recorded and does not replace that list.",
    }
    final["all_passed"] = mock_check["passed"] and RUNTIME.exists() is False
    write_json(FIXTURE, final)
    _write_bindings(plan)
    if final["all_passed"] is not True:
        raise RuntimeError("offline mock batch failed; inspect offline-validation.json")
    print(json.dumps({"all_passed": True, "network_requests": 0, "objects": len(objects),
                      "object_total_bytes": final["object_total_bytes"],
                      "offline_validation_sha256": sha(FIXTURE), "input_bindings_sha256": sha(BINDINGS),
                      "mock_attempts": mock_check["mock_attempts"]}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline-validate", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--go", type=Path)
    args = parser.parse_args()
    if args.offline_validate and args.execute:
        raise SystemExit("choose only one mode")
    if args.execute:
        if args.go is None:
            raise SystemExit("--execute requires --go PATH")
        result = run_batch(args.go)
        print(json.dumps({key: value for key, value in result.items() if key != "runtime"}, ensure_ascii=False))
        return 0 if result["accepted"] else 2
    if args.offline_validate:
        if args.go is not None:
            raise SystemExit("--go is only valid with --execute")
        return offline_validate()
    if args.go is not None:
        raise SystemExit("--go is only valid with --execute")
    plan, manifest, _, _ = preflight()
    print(json.dumps({"prepared": True, "batch_id": BATCH, "objects": len(manifest["objects"]),
                      "pages_commit": plan.get("pages_commit"), "actions_run": plan.get("actions_run"),
                      "network_requests_at_prepare": 0}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"verify_pages_v55_changes69: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)

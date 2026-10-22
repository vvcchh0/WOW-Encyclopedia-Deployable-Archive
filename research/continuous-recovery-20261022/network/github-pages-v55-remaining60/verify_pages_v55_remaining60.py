#!/usr/bin/env python3
"""Prepare or GO-gated verify only the 60 v55 Pages objects still unverified."""
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
PARTIAL_REL = "research/continuous-recovery-20261022/root-v55-online-partial-acceptance9.json"
ORIGINAL_MANIFEST_REL = "research/continuous-recovery-20261022/network/github-pages-v55-changes69/object-manifest.json"
PRIOR_PUBLIC_SUMMARY_REL = "research/continuous-recovery-20261022/network/github-pages-v55-changes69/runtime/object-match-summary.json"
EXPORT_PATH = ROOT / EXPORT_REL
BROWSER_PATH = ROOT / BROWSER_REL
PARTIAL_PATH = ROOT / PARTIAL_REL
ORIGINAL_MANIFEST_PATH = ROOT / ORIGINAL_MANIFEST_REL
PRIOR_PUBLIC_SUMMARY_PATH = ROOT / PRIOR_PUBLIC_SUMMARY_REL
LOCAL = ".scratch/pages-resources-20261022-v55"
BASE = "https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/"
BATCH = "github-pages-v55-remaining60"
GO_SCHEMA = "wow-root-github-pages-v55-remaining60-go/v1"
PARTIAL_SHA = "b31b5918ce9e2dce4d34358924c9997eff55645943e6357c5ebc69b1f1ea40a0"
ORIGINAL_MANIFEST_SHA = "951ac6924f84fa82710bfd8563ced83627a3012bf030f3cd6833cb9980808f6e"
PRIOR_PUBLIC_SUMMARY_SHA = "656f621ebbd5c4676ff8fd9e525471440d26885b5a0227554a4a249a37f1cfec"

CORE_REL = "research/continuous-recovery-20261022/network/github-pages-v53-changes06/verify_pages_v53_changes06.py"
CORE_PATH = ROOT / CORE_REL
CORE_SHA = "deddfab9dad1c3d1e472d7b0ad6454746c91b9707265e6f9dd1093ecdc019a70"
TRANSPORT_REL = "research/continuous-recovery-20261022/network/archivecraft-dungeons01/archivecraft_dungeons01.py"
TRANSPORT_SHA = "7b95fa17bff6aa5245dc9fe45331652f02db5419c0e7ac14ff454af9d0fcad00"

DISK_FLOOR = 11_005_853_696
SCHEDULE_TARGET_SECONDS = 6.4
MIN_ACTUAL_SECONDS = 5.0
TRANSPORT_DEFAULT_SECONDS = 6.2
MAX_LOGICAL = 60
MAX_ATTEMPTS = 120
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
        "request_start_schedule_target_seconds": SCHEDULE_TARGET_SECONDS,
        "minimum_actual_request_start_seconds": MIN_ACTUAL_SECONDS,
        "reused_transport_default_cadence_seconds": TRANSPORT_DEFAULT_SECONDS,
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
    required = (EXPORT_PATH, BROWSER_PATH, PARTIAL_PATH, ORIGINAL_MANIFEST_PATH, PRIOR_PUBLIC_SUMMARY_PATH)
    if any(not path.is_file() for path in required):
        raise RuntimeError("one or more root v55 receipts or prior-batch bindings are missing")
    if sha(PARTIAL_PATH) != PARTIAL_SHA or sha(ORIGINAL_MANIFEST_PATH) != ORIGINAL_MANIFEST_SHA:
        raise RuntimeError("partial acceptance or original 69-object manifest hash changed")
    if sha(PRIOR_PUBLIC_SUMMARY_PATH) != PRIOR_PUBLIC_SUMMARY_SHA:
        raise RuntimeError("prior 69-object execution summary hash changed")
    export, browser = read_json(EXPORT_PATH), read_json(BROWSER_PATH)
    partial = read_json(PARTIAL_PATH)
    original = read_json(ORIGINAL_MANIFEST_PATH)
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

    if partial.get("schema") != "wow-root-v55-online-partial-acceptance/v1" or partial.get("accepted_for_online_objects") is not True:
        raise RuntimeError("root partial acceptance is missing or not accepted for online objects")
    if partial.get("local_site") != LOCAL or partial.get("objects_verified") != 9 or partial.get("remaining_count") != MAX_LOGICAL:
        raise RuntimeError("root partial acceptance does not bind the expected v55 site and 9/60 split")
    if partial.get("prior_batch_accepted") is not False or partial.get("prior_batch_report_sha256") != PRIOR_PUBLIC_SUMMARY_SHA:
        raise RuntimeError("failed original 69-object batch provenance differs from the pinned report")
    if partial.get("wayback_resume_gate_passed") is not False or partial.get("raw_http_and_cookies_public") is not False:
        raise RuntimeError("partial receipt has unexpected scope or raw-data exposure state")
    if original.get("schema") != "wow-recovery.github-pages-v55-changes69.object-manifest.v1" or original.get("batch_id") != "github-pages-v55-changes69":
        raise RuntimeError("pinned original manifest is not the v55 69-object manifest")
    if original.get("source", {}).get("export_acceptance_sha256") != sha(EXPORT_PATH) or original.get("source", {}).get("browser_acceptance_sha256") != sha(BROWSER_PATH):
        raise RuntimeError("original manifest was prepared from different root acceptance receipts")
    if original.get("source", {}).get("pages_commit") != partial.get("pages_commit") or original.get("source", {}).get("actions_run") != str(partial.get("actions_run")):
        raise RuntimeError("partial receipt deployment identifiers differ from the original manifest")

    source_rows = export.get("online_changes_from_v53")
    original_rows = original.get("objects")
    if not isinstance(source_rows, list) or len(source_rows) != 69 or not isinstance(original_rows, list) or len(original_rows) != 69:
        raise RuntimeError("accepted export and original manifest must each contain the exact 69-object set")
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
    original_projection = [{key: item[key] for key in ("object_id", "path", "url", "local_path", "local_bytes", "local_sha256", "accepted_mime_types")} for item in original_rows]
    if original_projection != objects:
        raise RuntimeError("original 69-object manifest differs from the accepted export roster")

    verified = partial.get("objects")
    remaining = partial.get("remaining")
    if not isinstance(verified, list) or len(verified) != 9 or not isinstance(remaining, list) or len(remaining) != MAX_LOGICAL:
        raise RuntimeError("partial receipt does not contain exactly nine verified and sixty remaining rows")
    for index, receipt_row in enumerate(verified):
        original_row = objects[index]
        expected = {
            "path": original_row["path"], "url": original_row["url"],
            "sha256": original_row["local_sha256"], "bytes": original_row["local_bytes"],
        }
        if not isinstance(receipt_row, dict) or any(receipt_row.get(key) != value for key, value in expected.items()):
            raise RuntimeError(f"partial receipt verified row {index + 1} differs from the original manifest")
        if receipt_row.get("status") != 200 or receipt_row.get("transport") != "direct" or receipt_row.get("mime") not in original_row["accepted_mime_types"]:
            raise RuntimeError(f"partial receipt verified row {index + 1} lacks the accepted transport/status/MIME")

    remaining_objects: list[dict[str, Any]] = []
    for offset, receipt_row in enumerate(remaining):
        original_row = objects[offset + 9]
        expected = {"path": original_row["path"], "sha256": original_row["local_sha256"], "bytes": original_row["local_bytes"]}
        if not isinstance(receipt_row, dict) or any(receipt_row.get(key) != value for key, value in expected.items()):
            raise RuntimeError(f"remaining row {offset + 1} is not the exact next row from the pinned manifest")
        remaining_objects.append(original_row)
    if sum(item["local_bytes"] for item in remaining_objects) > TOTAL_CAP:
        raise RuntimeError("remaining 60-object set exceeds the 64 MiB batch response cap")
    if {x["path"] for x in remaining_objects}.intersection(x["path"] for x in objects[:9]):
        raise RuntimeError("remaining batch overlaps the nine objects already verified")
    return export, browser, remaining_objects


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
    if (transport.MIN_START_SECONDS, transport.REQUEST_SECONDS, transport.CONNECT_SECONDS) != (TRANSPORT_DEFAULT_SECONDS, REQUEST_SECONDS, CONNECT_SECONDS):
        raise RuntimeError("reused v53 transport defaults changed")
    transport.MAX_RESPONSE_BYTES = OBJECT_CAP
    return module, transport


def _manifest(export: dict[str, Any], browser: dict[str, Any], objects: list[dict[str, Any]],
              pages_commit: str | None, actions_run: str | None) -> dict[str, Any]:
    partial = read_json(PARTIAL_PATH)
    return {
        "schema": "wow-recovery.github-pages-v55-remaining60.object-manifest.v1",
        "batch_id": BATCH,
        "target_base_url": BASE,
        "source": {
            "local_site": LOCAL,
            "change_list": "root partial acceptance remaining list",
            "partial_acceptance_path": PARTIAL_REL,
            "partial_acceptance_sha256": sha(PARTIAL_PATH),
            "original_manifest_path": ORIGINAL_MANIFEST_REL,
            "original_manifest_sha256": sha(ORIGINAL_MANIFEST_PATH),
            "prior_public_summary_path": PRIOR_PUBLIC_SUMMARY_REL,
            "prior_public_summary_sha256": sha(PRIOR_PUBLIC_SUMMARY_PATH),
            "prior_batch_stop_reason": partial["prior_batch_stop_reason"],
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
        "schema": "wow-recovery.github-pages-v55-remaining60.plan.v1",
        "batch_id": BATCH,
        "mode": "prepared",
        "root_go_required": True,
        "network_requests_at_prepare": 0,
        "pages_commit": manifest["source"]["pages_commit"],
        "actions_run": manifest["source"]["actions_run"],
        "deployment_binding_status": manifest["source"]["deployment_binding_status"],
        "target_base_url": BASE,
        "local_site": LOCAL,
        "change_list": "root partial acceptance remaining list",
        "object_count": MAX_LOGICAL,
        "object_total_bytes": sum(x["local_bytes"] for x in manifest["objects"]),
        "object_manifest_sha256": sha(MANIFEST),
        "object_set_sha256": _object_set_sha(manifest["objects"]),
        "export_acceptance_path": EXPORT_REL,
        "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_path": BROWSER_REL,
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "partial_acceptance_path": PARTIAL_REL,
        "partial_acceptance_sha256": sha(PARTIAL_PATH),
        "original_manifest_path": ORIGINAL_MANIFEST_REL,
        "original_manifest_sha256": sha(ORIGINAL_MANIFEST_PATH),
        "prior_public_summary_path": PRIOR_PUBLIC_SUMMARY_REL,
        "prior_public_summary_sha256": sha(PRIOR_PUBLIC_SUMMARY_PATH),
        "shared_v53_wrapper_path": CORE_REL,
        "shared_v53_wrapper_sha256": CORE_SHA,
        "transport_runner_path": TRANSPORT_REL,
        "transport_runner_sha256": TRANSPORT_SHA,
        "policy": policy(),
        "execution_boundary": "one root-GO-authorized batch for exactly partial.remaining (60 rows); never re-request the nine objects in partial.objects; no redirects or automatic retries",
        "raw_handling": "HTTP headers, response bodies, and cookie jars remain private under runtime/private/raw; public output contains only curated object summaries",
        "go_required_fields": [
            "plan_sha256", "wrapper_sha256", "object_manifest_sha256", "offline_validation_sha256",
            "input_bindings_sha256", "shared_v53_wrapper_sha256", "transport_runner_sha256",
            "export_acceptance_sha256", "browser_acceptance_sha256", "object_set_sha256",
            "partial_acceptance_sha256", "original_manifest_sha256", "prior_public_summary_sha256",
            "pages_commit", "actions_run",
        ],
    }


def _bindings(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "wow-recovery.github-pages-v55-remaining60.input-bindings.v1",
        "batch_id": BATCH,
        "plan_sha256": sha(PLAN),
        "wrapper_sha256": sha(Path(__file__)),
        "object_manifest_sha256": sha(MANIFEST),
        "offline_validation_sha256": sha(FIXTURE),
        "shared_v53_wrapper_sha256": CORE_SHA,
        "transport_runner_sha256": TRANSPORT_SHA,
        "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "partial_acceptance_sha256": sha(PARTIAL_PATH),
        "original_manifest_sha256": sha(ORIGINAL_MANIFEST_PATH),
        "prior_public_summary_sha256": sha(PRIOR_PUBLIC_SUMMARY_PATH),
        "object_set_sha256": plan["object_set_sha256"],
        "pages_commit": plan.get("pages_commit"),
        "actions_run": plan.get("actions_run"),
    }


def _write_bindings(plan: dict[str, Any]) -> None:
    write_json(BINDINGS, _bindings(plan))


def prepare_files() -> tuple[dict[str, Any], dict[str, Any]]:
    export, browser, objects = _read_inputs()
    partial = read_json(PARTIAL_PATH)
    pages_commit = partial["pages_commit"]
    actions_run = str(partial["actions_run"])
    if PLAN.is_file():
        existing = read_json(PLAN)
        if existing.get("schema") != "wow-recovery.github-pages-v55-remaining60.plan.v1" or existing.get("batch_id") != BATCH:
            raise RuntimeError("existing plan has another batch identity; refusing to replace it")
        if existing.get("pages_commit") != pages_commit or existing.get("actions_run") != actions_run:
            raise RuntimeError("existing plan deployment pins differ from the accepted partial receipt")
    manifest = _manifest(export, browser, objects, pages_commit, actions_run)
    write_json(MANIFEST, manifest)
    plan = _plan(manifest)
    write_json(PLAN, plan)
    return plan, manifest


def preflight() -> tuple[dict[str, Any], dict[str, Any], Any, Any]:
    if not PLAN.is_file() or not MANIFEST.is_file():
        raise RuntimeError("plan/manifest are missing; run --offline-validate")
    plan, manifest = read_json(PLAN), read_json(MANIFEST)
    if plan.get("schema") != "wow-recovery.github-pages-v55-remaining60.plan.v1" or plan.get("mode") != "prepared" or plan.get("root_go_required") is not True or plan.get("network_requests_at_prepare") != 0 or plan.get("batch_id") != BATCH:
        raise RuntimeError("plan is not prepared and root-GO-gated")
    if manifest.get("schema") != "wow-recovery.github-pages-v55-remaining60.object-manifest.v1" or manifest.get("batch_id") != BATCH:
        raise RuntimeError("manifest batch identity mismatch")
    if plan.get("policy") != policy() or plan.get("target_base_url") != BASE or manifest.get("target_base_url") != BASE:
        raise RuntimeError("fixed network policy or target base mismatch")
    if plan.get("object_manifest_sha256") != sha(MANIFEST):
        raise RuntimeError("object manifest file hash mismatch")
    export, browser, expected_objects = _read_inputs()
    if manifest.get("objects") != expected_objects or len(expected_objects) != MAX_LOGICAL:
        raise RuntimeError("manifest differs from the exact accepted remaining-60 list")
    object_set = _object_set_sha(expected_objects)
    if plan.get("object_set_sha256") != object_set or manifest.get("source", {}).get("change_list") != "root partial acceptance remaining list":
        raise RuntimeError("object set or source-list binding mismatch")
    if plan.get("export_acceptance_sha256") != sha(EXPORT_PATH) or plan.get("browser_acceptance_sha256") != sha(BROWSER_PATH):
        raise RuntimeError("root acceptance receipt hash binding mismatch")
    for field, value in (
        ("partial_acceptance_sha256", sha(PARTIAL_PATH)),
        ("original_manifest_sha256", sha(ORIGINAL_MANIFEST_PATH)),
        ("prior_public_summary_sha256", sha(PRIOR_PUBLIC_SUMMARY_PATH)),
    ):
        if plan.get(field) != value or manifest.get("source", {}).get(field) != value:
            raise RuntimeError(f"partial/prior batch binding mismatch: {field}")
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
    transport.require_disk("v55 remaining-60 plan/source preflight")
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
        "partial_acceptance_sha256": sha(PARTIAL_PATH),
        "original_manifest_sha256": sha(ORIGINAL_MANIFEST_PATH),
        "prior_public_summary_sha256": sha(PRIOR_PUBLIC_SUMMARY_PATH),
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
    transport.require_disk("before authorized v55 remaining-60 batch")
    paths = transport.make_paths(runtime)
    runtime.mkdir(parents=True, exist_ok=False)
    paths.private.mkdir(parents=True, exist_ok=True)
    paths.raw.mkdir(parents=True, exist_ok=True)
    transport.MAX_RESPONSE_BYTES = OBJECT_CAP
    disk_start = transport.require_disk("v55 remaining-60 batch start")
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
                    cadence_seconds=SCHEDULE_TARGET_SECONDS, batch_seconds=MAX_SECONDS,
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
            elif record.get("actual_start_interval_seconds") is not None and record["actual_start_interval_seconds"] < MIN_ACTUAL_SECONDS:
                stop = "actual_request_start_below_five_second_hard_minimum"
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
        "schema": "wow-recovery.github-pages-v55-remaining60.private-report.v1",
        "batch_id": BATCH,
        "go_sha256": sha(go_path),
        "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "partial_acceptance_sha256": sha(PARTIAL_PATH),
        "original_manifest_sha256": sha(ORIGINAL_MANIFEST_PATH),
        "prior_public_summary_sha256": sha(PRIOR_PUBLIC_SUMMARY_PATH),
        "schedule_target_seconds": SCHEDULE_TARGET_SECONDS,
        "minimum_actual_user_seconds": MIN_ACTUAL_SECONDS,
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
        "schema": "wow-recovery.github-pages-v55-remaining60.public-summary.v1",
        "batch_id": BATCH,
        "pages_commit": plan.get("pages_commit"),
        "actions_run": plan.get("actions_run"),
        "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "partial_acceptance_sha256": sha(PARTIAL_PATH),
        "original_manifest_sha256": sha(ORIGINAL_MANIFEST_PATH),
        "prior_public_summary_sha256": sha(PRIOR_PUBLIC_SUMMARY_PATH),
        "schedule_target_seconds": SCHEDULE_TARGET_SECONDS,
        "minimum_actual_user_seconds": MIN_ACTUAL_SECONDS,
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
    transport.require_disk("before v55 remaining-60 execution summaries")
    report_path = paths.private / "report.json"
    summary_path = runtime / "object-match-summary.json"
    report_path.write_text(json.dumps(private, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    transport.require_disk("after v55 remaining-60 execution summaries")
    return {"accepted": accepted, "matches": sum(bool(item["matches_local"]) for item in rows),
            "http_attempts": len(attempts), "direct_attempts": public["direct_attempt_count"],
            "proxy_attempts": public["proxy_attempt_count"], "stop_reason": stop,
            "runtime": str(runtime)}


def _fake_attempt_factory(objects: list[dict[str, Any]], *, interval_seconds: float = 6.39,
                          fail_first_direct: bool = True) -> Callable[..., tuple[dict[str, Any], float]]:
    by_id = {item["object_id"]: item for item in objects}

    def attempt(target: dict[str, Any], attempt_no: int, use_proxy: bool,
                last_start: float | None, batch_start: float, remaining: int, paths: Any,
                *, cadence_seconds: float, batch_seconds: float) -> tuple[dict[str, Any], float]:
        if cadence_seconds != SCHEDULE_TARGET_SECONDS:
            raise AssertionError(f"schedule target was not passed to transport: {cadence_seconds}")
        obj = by_id[target["target_id"]]
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        simulate_transport_failure = fail_first_direct and target["target_id"] == objects[0]["object_id"] and attempt_no == 1 and not use_proxy
        record = {
            "attempt": attempt_no, "logical_request": target["target_id"], "url": target["url"],
            "transport": "proxy" if use_proxy else "direct", "request_started_utc": now,
            "request_finished_utc": now, "actual_start_interval_seconds": None if attempt_no == 1 else interval_seconds,
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
        "browser_acceptance_sha256": sha(BROWSER_PATH),
        "partial_acceptance_sha256": sha(PARTIAL_PATH),
        "original_manifest_sha256": sha(ORIGINAL_MANIFEST_PATH),
        "prior_public_summary_sha256": sha(PRIOR_PUBLIC_SUMMARY_PATH),
        "object_set_sha256": plan["object_set_sha256"],
        "pages_commit": plan.get("pages_commit"), "actions_run": plan.get("actions_run"),
    }


def offline_validate() -> int:
    if RUNTIME.exists():
        raise RuntimeError("production runtime exists; refusing to rewrite prepared batch artifacts")
    plan, manifest = prepare_files()
    export, browser, objects = _read_inputs()
    _, transport = _load_core()
    _assert_transport_cli(transport)
    preliminary = {
        "schema": "wow-recovery.github-pages-v55-remaining60.offline-validation.v1",
        "batch_id": BATCH, "all_passed": True, "network_requests": 0,
        "source_export_acceptance_sha256": sha(EXPORT_PATH),
        "source_browser_acceptance_sha256": sha(BROWSER_PATH),
        "source_partial_acceptance_sha256": sha(PARTIAL_PATH),
        "source_original_manifest_sha256": sha(ORIGINAL_MANIFEST_PATH),
        "source_prior_public_summary_sha256": sha(PRIOR_PUBLIC_SUMMARY_PATH),
        "schedule_target_seconds": SCHEDULE_TARGET_SECONDS,
        "minimum_actual_user_seconds": MIN_ACTUAL_SECONDS,
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
        success_runtime = tmp_path / "runtime-success-6p39"
        success = run_batch(synthetic_go_path, runtime=success_runtime,
                            attempt_fn=_fake_attempt_factory(objects, interval_seconds=6.39), offline_mock=True)
        success_private = read_json(success_runtime / "private" / "report.json")
        success_public = read_json(success_runtime / "object-match-summary.json")
        success_intervals = [x["actual_start_interval_seconds"] for x in success_private["attempts"]
                             if x.get("actual_start_interval_seconds") is not None]
        cadence_check = (
            success["accepted"] is True and success["matches"] == MAX_LOGICAL
            and success["http_attempts"] == MAX_LOGICAL + 1
            and success["direct_attempts"] == MAX_LOGICAL and success["proxy_attempts"] == 1
            and len(success_private.get("objects", [])) == MAX_LOGICAL
            and success_public.get("accepted") is True
            and all(item.get("matches_local") is True for item in success_public.get("objects", []))
            and success_private.get("schedule_target_seconds") == SCHEDULE_TARGET_SECONDS
            and success_private.get("minimum_actual_user_seconds") == MIN_ACTUAL_SECONDS
            and len(success_intervals) == MAX_LOGICAL and min(success_intervals) == 6.39
            and min(success_intervals) < SCHEDULE_TARGET_SECONDS and min(success_intervals) >= MIN_ACTUAL_SECONDS
        )
        success_runtime_removed = not success_runtime.exists()

        boundary_runtime = tmp_path / "runtime-hard-stop-4p99"
        boundary = run_batch(synthetic_go_path, runtime=boundary_runtime,
                             attempt_fn=_fake_attempt_factory(objects, interval_seconds=4.99, fail_first_direct=False),
                             offline_mock=True)
        boundary_private = read_json(boundary_runtime / "private" / "report.json")
        boundary_public = read_json(boundary_runtime / "object-match-summary.json")
        boundary_check = (
            boundary["accepted"] is False and boundary["matches"] == 1
            and boundary["http_attempts"] == 2 and boundary["direct_attempts"] == 2
            and boundary["proxy_attempts"] == 0
            and boundary["stop_reason"] == "actual_request_start_below_five_second_hard_minimum"
            and boundary_private["attempts"][1]["actual_start_interval_seconds"] == 4.99
            and boundary_public["stop_reason"] == "actual_request_start_below_five_second_hard_minimum"
        )
        boundary_runtime_removed = not boundary_runtime.exists()

    success_runtime_removed = not success_runtime.exists()
    boundary_runtime_removed = not boundary_runtime.exists()
    mock_check = {
        "passed": cadence_check and boundary_check and success_runtime_removed and boundary_runtime_removed,
        "real_network_requests": 0,
        "real_subprocess_calls": 0,
        "success_fixture": {
            "all_60_matched": success["matches"] == MAX_LOGICAL,
            "logical_objects": MAX_LOGICAL,
            "http_attempts": success["http_attempts"],
            "direct_attempts": success["direct_attempts"],
            "proxy_attempts": success["proxy_attempts"],
            "proxy_after_first_transfer_failure": success["proxy_attempts"] == 1,
            "schedule_target_seconds": SCHEDULE_TARGET_SECONDS,
            "recorded_actual_interval_seconds": sorted(set(success_intervals)),
            "6p39_passes_five_second_hard_limit": cadence_check,
            "isolated_runtime_removed": success_runtime_removed,
        },
        "hard_stop_fixture": {
            "recorded_actual_interval_seconds": 4.99,
            "stop_reason": boundary["stop_reason"],
            "http_attempts": boundary["http_attempts"],
            "matches_before_stop": boundary["matches"],
            "4p99_stops": boundary_check,
            "isolated_runtime_removed": boundary_runtime_removed,
        },
        "production_runtime_absent": not RUNTIME.exists(),
    }
    final = {
        **preliminary,
        "offline_mock_execution": mock_check,
        "remaining_objects_count": len(objects),
        "pages_commit": plan.get("pages_commit"), "actions_run": plan.get("actions_run"),
        "roster_note": "Only the sixty rows in the root-accepted partial receipt remaining list are in this batch; the nine already verified rows are excluded.",
    }
    final["all_passed"] = mock_check["passed"] and RUNTIME.exists() is False
    write_json(FIXTURE, final)
    _write_bindings(plan)
    if final["all_passed"] is not True:
        raise RuntimeError("offline remaining-60 mock validation failed; inspect offline-validation.json")
    print(json.dumps({"all_passed": True, "network_requests": 0, "objects": len(objects),
                      "object_total_bytes": final["object_total_bytes"],
                      "offline_validation_sha256": sha(FIXTURE), "input_bindings_sha256": sha(BINDINGS),
                      "success_mock_attempts": success["http_attempts"],
                      "hard_stop_mock_attempts": boundary["http_attempts"]}))
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
        print(f"verify_pages_v55_remaining60: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)

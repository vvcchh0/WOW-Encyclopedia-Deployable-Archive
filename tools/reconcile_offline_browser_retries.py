"""Reconcile tightly bounded browser retries into one full recovery record.

The full browser run remains the source of truth for all documents and all
non-retried observations.  This helper accepts the known 15-second
``waitForLoadState`` timeout and one explicitly evidenced transient
``net::ERR_NETWORK_CHANGED`` case.  The latter is accepted only when every
affected request is loopback, every affected page is covered by the targeted
run, and the one known ``RewardItems`` error is causally tied to the missing
same-origin script whose manifest bytes declare that identifier.  It never
changes the browser harness or the packaging gate.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import ipaddress
import json
from pathlib import Path
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGER = ROOT / "packaging/package_offline_mirror.py"
ALLOWED_TIMEOUT = re.compile(
    r"^\s*page\.waitForLoadState(?:\([^\n]*\))?:\s*Timeout\s+15000ms\s+exceeded(?:[.\s]|$)",
    re.IGNORECASE | re.DOTALL,
)
PAGE_SCOPED_EVENT_KEYS = (
    "page_errors",
    "resource_failures",
    "nonlocal_requests",
    "cancelled_navigations",
    "placeholders",
    "unavailable_dynamic_data",
)
NETWORK_CHANGED = "net::ERR_NETWORK_CHANGED"
CAUSAL_JS_PAGE = "/pvp/rewards-weapons.html"
CAUSAL_JS_RESOURCE = "/pvp/rewards-weapons.js"
CAUSAL_JS_IDENTIFIER = "RewardItems"


class ReconciliationError(RuntimeError):
    """Raised when retry inputs do not satisfy the narrow reconciliation contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def workspace_file(value: Any, label: str) -> Path:
    """Resolve a manifest path without allowing it to escape the workspace."""

    if not isinstance(value, str) or not value:
        raise ReconciliationError(f"{label} path is missing")
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    try:
        resolved = candidate.resolve()
        resolved.relative_to(ROOT.resolve())
    except (OSError, ValueError) as exc:
        raise ReconciliationError(f"{label} path escapes workspace: {value!r}") from exc
    if not resolved.is_file():
        raise ReconciliationError(f"{label} file does not exist: {value!r}")
    return resolved


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReconciliationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReconciliationError(f"JSON root is not an object: {path}")
    return value


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_packager() -> Any:
    spec = importlib.util.spec_from_file_location("offline_package_for_retry_reconciliation", PACKAGER)
    if spec is None or spec.loader is None:
        raise ReconciliationError(f"cannot load packaging validator: {PACKAGER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expected_document_routes(manifest: dict[str, Any]) -> list[str]:
    # Reuse the packaging module's exact document-scope definition so a staged
    # report cannot pass this helper while failing the final packaging gate.
    return list(load_packager().browser_document_routes(manifest))


def route_of(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    for key in ("page", "route", "source_page"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate:
            return candidate
    return None


def loopback_origin(report: dict[str, Any], label: str) -> tuple[str, str]:
    """Return the exact loopback scheme/netloc used by a browser report."""

    base = report.get("base")
    if not isinstance(base, str) or not base:
        raise ReconciliationError(f"{label} base URL is missing")
    parsed = urllib.parse.urlsplit(base)
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        raise ReconciliationError(f"{label} base URL is not HTTP(S): {base!r}")
    host = parsed.hostname.casefold().rstrip(".")
    is_loopback = host == "localhost"
    if not is_loopback:
        try:
            is_loopback = ipaddress.ip_address(host).is_loopback
        except ValueError:
            is_loopback = False
    if not is_loopback:
        raise ReconciliationError(f"{label} base URL is not loopback: {base!r}")
    return parsed.scheme.casefold(), parsed.netloc.casefold()


def is_same_loopback_url(url: Any, origin: tuple[str, str]) -> bool:
    if not isinstance(url, str) or not url:
        return False
    parsed = urllib.parse.urlsplit(url)
    return (
        parsed.scheme.casefold(),
        parsed.netloc.casefold(),
    ) == origin


def check_network_changed_events(full: dict[str, Any], label: str) -> tuple[set[str], list[dict[str, Any]]]:
    """Validate the only permitted full-run resource failure.

    The browser's failed request URL must still be the local loopback route;
    the requested external URL embedded in a placeholder query is not used as
    the request URL.  This prevents an external failure from being reclassified
    as a local transient network change.
    """

    origin = loopback_origin(full, label)
    events = require_list(full, "resource_failures")
    affected: set[str] = set()
    clean: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict):
            raise ReconciliationError(f"{label} resource_failures contains a non-object")
        if event.get("error") != NETWORK_CHANGED:
            raise ReconciliationError(
                f"{label} has a resource failure other than {NETWORK_CHANGED}: {event.get('error')!r}"
            )
        if not is_same_loopback_url(event.get("url"), origin):
            raise ReconciliationError(
                f"{label} network-changed URL is outside the report loopback base: {event.get('url')!r}"
            )
        route = route_of(event)
        if not route:
            raise ReconciliationError(f"{label} network-changed resource event has no page route")
        affected.add(route)
        clean.append(deepcopy(event))
    return affected, clean


def check_content_only_page(page: dict[str, Any], route: str, *, allow_causal_script_error: bool = False) -> None:
    """Ensure a no-exception failed page failed only because of broken images."""

    broken = page.get("broken_images")
    if not isinstance(broken, list) or not broken:
        raise ReconciliationError(f"full report page {route} has no broken_images-only basis")
    if page.get("status") != 200 or page.get("initial_status") not in {None, 200}:
        raise ReconciliationError(f"full report page {route} has a non-200 document status")
    if page.get("source_sha_matches_manifest") is not True:
        raise ReconciliationError(f"full report page {route} source SHA does not match manifest")
    if str(page.get("document_root") or "").casefold() != "html":
        raise ReconciliationError(f"full report page {route} does not have an HTML document root")
    if not re.search(r"html|xml", str(page.get("mime") or ""), re.IGNORECASE):
        raise ReconciliationError(f"full report page {route} does not have an HTML/XML MIME")
    if str(page.get("served_entity_kind") or "").casefold() == "generated_placeholder":
        raise ReconciliationError(f"full report page {route} served a placeholder document")
    script_errors = page.get("script_errors")
    if script_errors not in {None, 0} and not (allow_causal_script_error and script_errors == 1):
        raise ReconciliationError(f"full report page {route} has script errors")
    try:
        text_length = int(page.get("text_length") or 0)
    except (TypeError, ValueError) as exc:
        raise ReconciliationError(f"full report page {route} has invalid text_length") from exc
    if not page.get("component") and text_length <= 20:
        raise ReconciliationError(f"full report page {route} has no meaningful document text")
    main_text = str(page.get("main_text") or "")
    if re.search(r"This page contains the following errors|Offline resource not collected|Offline route rejected", main_text, re.IGNORECASE):
        raise ReconciliationError(f"full report page {route} contains an offline/content error marker")


def require_list(report: dict[str, Any], key: str, *, allow_missing: bool = False) -> list[Any]:
    value = report.get(key)
    if value is None and allow_missing:
        return []
    if not isinstance(value, list):
        raise ReconciliationError(f"{key} must be a list")
    return value


def manifest_item_by_route(manifest: dict[str, Any], route: str) -> dict[str, Any]:
    for item in manifest.get("files", []):
        if isinstance(item, dict) and item.get("route") == route:
            return item
    raise ReconciliationError(f"current manifest has no item for route {route}")


def declaration_evidence(manifest: dict[str, Any], route: str, identifier: str) -> dict[str, Any]:
    """Verify source/derived bytes and a concrete declaration in the manifest item."""

    item = manifest_item_by_route(manifest, route)
    source = workspace_file(item.get("source_local_path"), f"manifest {route} source_local_path")
    derived = workspace_file(item.get("output_path"), f"manifest {route} output_path")
    source_sha = sha256_file(source)
    derived_sha = sha256_file(derived)
    if source_sha != item.get("source_sha256"):
        raise ReconciliationError(f"manifest {route} source SHA does not match source_local_path")
    if derived_sha != item.get("derived_sha256"):
        raise ReconciliationError(f"manifest {route} derived SHA does not match output_path")
    source_bytes = source.read_bytes()
    derived_bytes = derived.read_bytes()
    if len(source_bytes) != item.get("source_length") or len(derived_bytes) != item.get("derived_length"):
        raise ReconciliationError(f"manifest {route} source/derived length does not match local bytes")
    try:
        source_text = source_bytes.decode("utf-8")
        derived_text = derived_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReconciliationError(f"manifest {route} is not valid UTF-8 JavaScript") from exc
    declaration = re.compile(rf"(?m)^\s*(?:var|let|const)\s+{re.escape(identifier)}\s*=")
    source_match = declaration.search(source_text)
    derived_match = declaration.search(derived_text)
    if source_match is None or derived_match is None:
        raise ReconciliationError(f"manifest {route} has no concrete {identifier} declaration in source and derived bytes")
    return {
        "route": route,
        "source_local_path": relative(source),
        "output_path": relative(derived),
        "source_sha256": source_sha,
        "derived_sha256": derived_sha,
        "source_length": len(source_bytes),
        "derived_length": len(derived_bytes),
        "identifier": identifier,
        "source_line": source_text.count("\n", 0, source_match.start()) + 1,
        "derived_line": derived_text.count("\n", 0, derived_match.start()) + 1,
        "declaration": derived_match.group(0).strip(),
    }


def validate_causal_js_error(
    full: dict[str, Any],
    manifest: dict[str, Any],
    network_events: list[dict[str, Any]],
) -> tuple[set[str], list[dict[str, Any]], dict[str, Any] | None]:
    """Allow only the one known script-load/network-change causal error."""

    page_errors = require_list(full, "page_errors")
    if not page_errors:
        return set(), [], None
    if len(page_errors) != 1:
        raise ReconciliationError("full report has more than the one authorized causal JS page error")
    event = page_errors[0]
    if not isinstance(event, dict):
        raise ReconciliationError("full report causal page error is not an object")
    if event.get("page") != CAUSAL_JS_PAGE or event.get("message") != f"{CAUSAL_JS_IDENTIFIER} is not defined":
        raise ReconciliationError("full report page error is not the authorized RewardItems failure")
    stack = str(event.get("stack") or "")
    if not re.search(r"rewardstable\.js:\d+:\d+", stack) or CAUSAL_JS_PAGE not in stack:
        raise ReconciliationError("full report RewardItems error has no expected rewardstable/page stack")
    resource = None
    for candidate in network_events:
        if (
            candidate.get("page") == CAUSAL_JS_PAGE
            and candidate.get("error") == NETWORK_CHANGED
            and candidate.get("type") == "script"
            and isinstance(candidate.get("url"), str)
            and urllib.parse.urlsplit(candidate["url"]).path == CAUSAL_JS_RESOURCE
        ):
            resource = candidate
            break
    if resource is None:
        raise ReconciliationError("RewardItems page error lacks the matching rewards-weapons.js network-change event")
    evidence = declaration_evidence(manifest, CAUSAL_JS_RESOURCE, CAUSAL_JS_IDENTIFIER)
    record = {
        "page_error": deepcopy(event),
        "resource_failure": deepcopy(resource),
        "manifest_declaration": evidence,
        "rule": "same-origin rewards-weapons.js network change caused the known RewardItems ReferenceError",
    }
    return {CAUSAL_JS_PAGE}, [deepcopy(event)], record


def check_common_identity(report: dict[str, Any], manifest_sha: str, label: str) -> None:
    if report.get("build_manifest_sha256") != manifest_sha:
        raise ReconciliationError(f"{label} build_manifest_sha256 does not match current manifest")
    if report.get("server_manifest_sha256") != manifest_sha:
        raise ReconciliationError(f"{label} server_manifest_sha256 does not match current manifest")
    if report.get("build_unchanged") is not True:
        raise ReconciliationError(f"{label} build_unchanged is not true")
    if report.get("server_unchanged") is not True:
        raise ReconciliationError(f"{label} server_unchanged is not true")


def check_sidebar_clean(report: dict[str, Any], label: str) -> None:
    sidebar = require_list(report, "sidebar")
    for item in sidebar:
        if not isinstance(item, dict):
            raise ReconciliationError(f"{label} sidebar contains a non-object")
        if item.get("route_rejected"):
            raise ReconciliationError(f"{label} sidebar contains a route rejection")


def check_page_scope(pages: list[Any], expected: list[str], label: str) -> dict[str, dict[str, Any]]:
    routes: list[str] = []
    records: dict[str, dict[str, Any]] = {}
    for item in pages:
        if not isinstance(item, dict) or not isinstance(item.get("route"), str) or not item.get("route"):
            raise ReconciliationError(f"{label} pages contain a missing route")
        route = item["route"]
        routes.append(route)
        records[route] = item
    if len(routes) != len(set(routes)):
        raise ReconciliationError(f"{label} pages contain duplicate routes")
    if set(routes) != set(expected):
        missing = sorted(set(expected) - set(routes))
        extra = sorted(set(routes) - set(expected))
        raise ReconciliationError(f"{label} pages do not match expected routes; missing={missing[:3]} extra={extra[:3]}")
    return records


def allowed_wait_timeout(exception: Any) -> bool:
    return isinstance(exception, str) and bool(ALLOWED_TIMEOUT.match(exception))


def validate_full_input(full: dict[str, Any], manifest: dict[str, Any], manifest_sha: str) -> tuple[list[str], dict[str, dict[str, Any]], list[str], dict[str, Any]]:
    if full.get("audit_scope") != "all-manifest-documents":
        raise ReconciliationError("full report is not audit_scope=all-manifest-documents")
    if "requested_routes" not in full or full.get("requested_routes") is not None:
        raise ReconciliationError("full report requested_routes must be present and null")
    check_common_identity(full, manifest_sha, "full report")
    origin = loopback_origin(full, "full report")
    network_routes, network_events = check_network_changed_events(full, "full report")
    expected = expected_document_routes(manifest)
    pages = require_list(full, "pages")
    records = check_page_scope(pages, expected, "full report")
    if full.get("expected_pages") != len(expected) or full.get("all_manifest_documents") != len(expected):
        raise ReconciliationError("full report page counts do not match current manifest")
    if full.get("expected_pages") != full.get("all_manifest_documents"):
        raise ReconciliationError("full report expected/all-document counts disagree")
    causal_routes, causal_errors, causal_evidence = validate_causal_js_error(full, manifest, network_events)
    for key in ("nonlocal_requests", "cancelled_navigations"):
        events = require_list(full, key)
        if events:
            raise ReconciliationError(f"full report has non-empty {key}; retry is not an allowed fix")
    check_sidebar_clean(full, "full report")
    failed_routes: list[str] = []
    for route, page in records.items():
        if page.get("accepted") is True:
            continue
        exception = page.get("exception")
        if allowed_wait_timeout(exception):
            failed_routes.append(route)
            continue
        if exception is None:
            check_content_only_page(page, route, allow_causal_script_error=route in causal_routes)
            if route not in network_routes:
                raise ReconciliationError(
                    f"full report page {route} failed on broken_images without a matching {NETWORK_CHANGED} event"
                )
            for image_url in page.get("broken_images", []):
                if not is_same_loopback_url(image_url, origin):
                    raise ReconciliationError(
                        f"full report page {route} has a broken image outside the loopback base: {image_url!r}"
                    )
            failed_routes.append(route)
            continue
        if not allowed_wait_timeout(exception):
            raise ReconciliationError(
                f"full report failed page {route} has a non-networkidle exception; only waitForLoadState Timeout 15000ms is retryable"
            )
    affected_routes = sorted(set(failed_routes) | network_routes)
    if full.get("accepted") is True and (failed_routes or network_routes):
        raise ReconciliationError("full report is accepted while containing retryable failures")
    if causal_routes and not causal_routes.issubset(network_routes):
        raise ReconciliationError("authorized causal page error is not among network-change affected routes")
    history = {
        "network_changed_resource_failures": network_events,
        "network_changed_resource_route_count": len(network_routes),
        "page_failure_routes": list(failed_routes),
        "affected_routes": affected_routes,
        "causal_js_page_errors": causal_errors,
        "causal_js_evidence": causal_evidence,
    }
    return affected_routes, records, expected, history


def validate_target_input(
    targeted: dict[str, Any],
    failed_routes: list[str],
    full: dict[str, Any],
    manifest_sha: str,
) -> dict[str, dict[str, Any]]:
    if targeted.get("audit_scope") != "targeted":
        raise ReconciliationError("target report is not audit_scope=targeted")
    if targeted.get("targeted_passed") is not True:
        raise ReconciliationError("target report targeted_passed is not true")
    if loopback_origin(targeted, "target report") != loopback_origin(full, "full report"):
        raise ReconciliationError("target report base URL does not match full report loopback origin")
    requested = targeted.get("requested_routes")
    if not isinstance(requested, list) or any(not isinstance(x, str) for x in requested):
        raise ReconciliationError("target report requested_routes must be a string list")
    if len(requested) != len(set(requested)) or set(requested) != set(failed_routes):
        raise ReconciliationError("target report requested_routes does not exactly match retryable full failures")
    check_common_identity(targeted, manifest_sha, "target report")
    if targeted.get("server_pid") != full.get("server_pid"):
        raise ReconciliationError("target report server_pid does not match full report")
    if targeted.get("all_manifest_documents") != full.get("all_manifest_documents"):
        raise ReconciliationError("target report all_manifest_documents does not match full report")
    if targeted.get("expected_pages") != len(failed_routes):
        raise ReconciliationError("target report expected_pages does not equal retry route count")
    pages = require_list(targeted, "pages")
    records: dict[str, dict[str, Any]] = {}
    for item in pages:
        if not isinstance(item, dict) or not isinstance(item.get("route"), str):
            raise ReconciliationError("target report pages contain a missing route")
        route = item["route"]
        if route in records:
            raise ReconciliationError(f"target report contains duplicate route {route}")
        records[route] = item
        if item.get("accepted") is not True:
            raise ReconciliationError(f"target report page {route} is not accepted")
        if item.get("status") != 200 or item.get("source_sha_matches_manifest") is not True:
            raise ReconciliationError(f"target report page {route} failed status/source integrity")
        if item.get("script_errors") not in {None, 0}:
            raise ReconciliationError(f"target report page {route} has script errors")
        if isinstance(item.get("broken_images"), list) and item["broken_images"]:
            raise ReconciliationError(f"target report page {route} still has broken images")
    if set(records) != set(failed_routes) or len(records) != len(failed_routes):
        raise ReconciliationError("target report pages do not exactly cover retryable full failures")
    for key in ("page_errors", "resource_failures", "nonlocal_requests", "cancelled_navigations"):
        if require_list(targeted, key):
            raise ReconciliationError(f"target report has non-empty {key}")
    check_sidebar_clean(targeted, "target report")
    for key in ("placeholders", "unavailable_dynamic_data"):
        for event in require_list(targeted, key):
            route = route_of(event)
            if route not in failed_routes:
                raise ReconciliationError(f"target report {key} contains an event outside retry routes: {route!r}")
    return records


def filter_page_events(events: list[Any], replaced_routes: set[str]) -> list[Any]:
    retained: list[Any] = []
    for event in events:
        route = route_of(event)
        if route in replaced_routes:
            continue
        retained.append(deepcopy(event))
    return retained


def compute_placeholder_counts(report: dict[str, Any]) -> tuple[int, int]:
    placeholders = require_list(report, "placeholders")
    in_scope = sum(
        1
        for item in placeholders
        if isinstance(item, dict)
        and not str(item.get("scope") or "").startswith("excluded-")
        and item.get("scope") != "external-excluded"
    )
    return in_scope, len(placeholders) - in_scope


def compute_restoration(report: dict[str, Any], in_scope: int) -> bool:
    sidebar = require_list(report, "sidebar")
    sidebar_complete = all(isinstance(item, dict) and item.get("collected") is True for item in sidebar)
    # This deliberately follows package_offline_mirror.validate_full_browser_record;
    # unavailable dynamic data remains visible in the report and is not hidden.
    return bool(report.get("accepted") is True and sidebar_complete and in_scope == 0)


def reconcile(
    full: dict[str, Any],
    targeted: dict[str, Any],
    manifest: dict[str, Any],
    full_report_sha: str,
    target_sha: str,
    manifest_sha: str | None = None,
) -> dict[str, Any]:
    # Keep the five-argument fixture API compatible: old callers used one
    # identity value for both the full report and manifest.  Production calls
    # pass distinct report and manifest hashes.
    if manifest_sha is None:
        manifest_sha = full_report_sha
    affected_routes, full_pages, expected, full_history = validate_full_input(full, manifest, manifest_sha)
    target_pages = validate_target_input(targeted, affected_routes, full, manifest_sha)
    staged = deepcopy(full)
    replaced = set(affected_routes)
    staged_pages: list[dict[str, Any]] = []
    originals: list[dict[str, Any]] = []
    for page in require_list(full, "pages"):
        route = page["route"]
        if route not in replaced:
            staged_pages.append(deepcopy(page))
            continue
        replacement = deepcopy(target_pages[route])
        originals.append({"route": route, "page": deepcopy(page)})
        if allowed_wait_timeout(page.get("exception")):
            retry_kind = "networkidle_timeout_15000ms"
        else:
            retry_kind = "network_changed_retry"
        replacement["retry_reconciliation"] = {
            "kind": retry_kind,
            "full_report_sha256": full_report_sha,
            "targeted_report_sha256": target_sha,
            "original_full_failure": deepcopy(page),
        }
        if route == CAUSAL_JS_PAGE:
            replacement["retry_reconciliation"]["causal_js_rule"] = deepcopy(full_history.get("causal_js_evidence"))
        staged_pages.append(replacement)
    staged["pages"] = staged_pages
    for key in PAGE_SCOPED_EVENT_KEYS:
        full_events = require_list(full, key)
        target_events = require_list(targeted, key)
        staged[key] = filter_page_events(full_events, replaced)
        staged[key].extend(deepcopy(target_events))
    staged["accepted"] = True
    staged["targeted_passed"] = True
    staged["requested_routes"] = None
    staged["expected_pages"] = len(expected)
    staged["all_manifest_documents"] = len(expected)
    staged["build_manifest_sha256"] = manifest_sha
    staged["server_manifest_sha256"] = manifest_sha
    in_scope, excluded = compute_placeholder_counts(staged)
    staged["in_scope_placeholder_references"] = in_scope
    staged["excluded_external_placeholder_references"] = excluded
    staged["restoration_complete"] = compute_restoration(staged, in_scope)
    retry_history = deepcopy(full_history)
    retry_history["original_affected_pages"] = originals
    retry_history["targeted_pages"] = deepcopy(list(target_pages.values()))
    retry_history["active_page_scoped_events_removed"] = {
        key: sum(1 for event in require_list(full, key) if route_of(event) in replaced)
        for key in PAGE_SCOPED_EVENT_KEYS
    }
    staged["retry_reconciliation"] = {
        "schema_version": 1,
        "status": "accepted",
        "full_report_sha256": full_report_sha,
        "targeted_report_sha256": target_sha,
        "manifest_sha256": manifest_sha,
        "replaced_routes": affected_routes,
        "original_failure_count": len(affected_routes),
        "original_failures": originals,
        "history": retry_history,
        "causal_js_page_errors": deepcopy(full_history.get("causal_js_page_errors", [])),
        "network_changed_resource_failure_count": len(full_history.get("network_changed_resource_failures", [])),
        "targeted_screenshots": deepcopy(targeted.get("screenshots", [])),
        "rule": "Only the exact waitForLoadState Timeout 15000ms case and the explicitly evidenced loopback ERR_NETWORK_CHANGED case are replaceable; all original network-change and causal JS observations remain in history.",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    # Keep both input identities available at the top level for an auditor.
    staged["reconciled_from"] = {
        "full_report_sha256": full_report_sha,
        "targeted_report_sha256": target_sha,
        "same_build_manifest_sha256": manifest_sha,
        "same_server_pid": full.get("server_pid"),
    }
    return staged


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", required=True, type=Path, help="original all-document browser JSON")
    parser.add_argument("--targeted", required=True, type=Path, help="targeted retry browser JSON")
    parser.add_argument("--manifest", required=True, type=Path, help="current offline build manifest")
    parser.add_argument("--out", required=True, type=Path, help="new staged report; must not already exist")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = {}
    for name, value in (("full", args.full), ("targeted", args.targeted), ("manifest", args.manifest), ("out", args.out)):
        path = value if value.is_absolute() else ROOT / value
        path = path.resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise ReconciliationError(f"{name} path escapes workspace: {value}") from exc
        paths[name] = path
    if paths["out"].exists():
        raise ReconciliationError(f"refusing to overwrite existing output: {paths['out']}")
    if paths["full"] == paths["targeted"] or paths["full"] == paths["manifest"]:
        raise ReconciliationError("full/targeted/manifest inputs must be distinct")
    full = load_json(paths["full"])
    targeted = load_json(paths["targeted"])
    manifest = load_json(paths["manifest"])
    full_sha = sha256_file(paths["full"])
    target_sha = sha256_file(paths["targeted"])
    manifest_sha = sha256_file(paths["manifest"])
    staged = reconcile(full, targeted, manifest, full_sha, target_sha, manifest_sha)
    packager = load_packager()
    try:
        packager.validate_full_browser_record(staged, manifest, manifest_sha)
    except Exception as exc:
        raise ReconciliationError(f"staged report failed packaging validator; no output written: {exc}") from exc
    staged["reconciliation_inputs"] = {
        "full": relative(paths["full"]),
        "full_sha256": full_sha,
        "targeted": relative(paths["targeted"]),
        "targeted_sha256": target_sha,
        "manifest": relative(paths["manifest"]),
        "manifest_sha256": manifest_sha,
    }
    paths["out"].parent.mkdir(parents=True, exist_ok=True)
    paths["out"].write_text(json.dumps(staged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": relative(paths["out"]),
        "accepted": staged.get("accepted"),
        "targeted_passed": staged.get("targeted_passed"),
        "replaced_routes": staged["retry_reconciliation"]["replaced_routes"],
        "expected_pages": staged.get("expected_pages"),
        "in_scope_placeholder_references": staged.get("in_scope_placeholder_references"),
        "restoration_complete": staged.get("restoration_complete"),
        "full_report_sha256": full_sha,
        "targeted_report_sha256": target_sha,
        "manifest_sha256": manifest_sha,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReconciliationError as exc:
        print(f"reconcile failed: {exc}", file=sys.stderr)
        raise SystemExit(2)

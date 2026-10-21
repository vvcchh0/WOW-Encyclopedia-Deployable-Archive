"""Shared, parameterized paths and local helpers for the 2026-10-21 v52 release.

Importing this module is offline.  The release scripts perform GitHub calls
only after an operator explicitly invokes their respective CLI entry point.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[4]
RUN_DATE = "20261021"
SOURCE_DATE = "20261021"
FLOOR = 11005853696
REPO = "vvcchh0/WOW-Encyclopedia-Deployable-Archive"
TAG = "archive-20080512-browser-20261021-v52"
VERSION_RE = re.compile(r"v\d+\Z")
FINAL_ACCEPTANCE_REL = (
    "research/continuous-recovery-20261021/publication/root-v52-final-acceptance.json"
)
ALDOR_SCRYERS_SMOKE_PATHS = (
    "__offline/aldor-scryers-lore.js",
    "info/basics/factions/aldorscryers/aldor-scryers.xml.html",
    "info/basics/factions/aldorscryers/aldor-scryers-tokens.xml.html",
)


def validate_version(version: str) -> str:
    if not VERSION_RE.fullmatch(version):
        raise ValueError("version must match vNN, for example v32")
    return version


def release_paths(version: str) -> dict[str, Path]:
    version = validate_version(version)
    assert version == "v52", "This frozen release adapter is pinned to v52"
    publication = ROOT / f"research/continuous-recovery-{RUN_DATE}/publication"
    source_publication = ROOT / f"research/continuous-recovery-{SOURCE_DATE}/publication"
    site = ROOT / f".scratch/pages-resources-{SOURCE_DATE}-{version}"
    archive = ROOT / f"artifacts/WOW_Encyclopedia_20080512_browser_{SOURCE_DATE}_{version}.zip"
    return {
        "publication": publication,
        "site": site,
        "archive": archive,
        "sidecar": archive.with_name(archive.name + ".sha256"),
        "local": source_publication / f"root-{version}-local-acceptance.json",
        "export": source_publication / f"root-{version}-export-acceptance.json",
        "browser": source_publication / f"root-{version}-browser-acceptance.json",
        "pages_online": source_publication / f"root-{version}-pages-online-acceptance.json",
        "package_report": source_publication / f"{version}-portable-package-report.json",
        "portable": publication / f"root-{version}-portable-acceptance.json",
        "draft": publication / f"{version}-release-draft.json",
        "notes": publication / f"{version}-release-notes.md",
        "publication_report": publication / f"root-{version}-release-publication.json",
        "extract": ROOT / f".scratch/local bundle smoke {RUN_DATE} {version}",
        "server_log": publication / f"{version}-portable-server-local.log",
        "final_acceptance": ROOT / FINAL_ACCEPTANCE_REL,
    }


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def safe_site_path(raw: str) -> PurePosixPath:
    path = PurePosixPath(str(raw).lstrip("/"))
    assert not path.is_absolute() and ".." not in path.parts and "\\" not in str(raw), raw
    assert path.parts and ":" not in path.parts[0], raw
    return path


def canonical_route(raw: str) -> str:
    """Canonicalize an archived route, retaining the root route as ``""``."""
    if raw in ("", "/"):
        return ""
    return safe_site_path(raw).as_posix()


def local_object_paths(local: dict) -> set[str]:
    """Derive local smoke objects without depending on old receipt counters."""
    paths = {
        str(item["path"])
        for item in local.get("objects", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    for key, value in local.items():
        if key.startswith("changed_since_live_") and isinstance(value, list):
            paths.update(str(item) for item in value if isinstance(item, str))
    return {safe_site_path(path).as_posix() for path in paths}


def _object_paths(value: object) -> set[str]:
    """Collect only explicit object ``path`` fields from nested gate data."""
    paths: set[str] = set()
    if isinstance(value, dict):
        raw = value.get("path")
        if isinstance(raw, str) and raw and not raw.startswith(("http://", "https://")):
            paths.add(safe_site_path(raw).as_posix())
        for child in value.values():
            paths.update(_object_paths(child))
    elif isinstance(value, list):
        for child in value:
            paths.update(_object_paths(child))
    return paths


def provenance_route_outputs(provenance: dict) -> dict[str, str]:
    """Map archived route keys to their actual derived output paths.

    Most routes retain their suffix, but an archived XML route is emitted as
    ``.xml.html``.  Smoke validation must use the derived output path rather
    than reconstructing a filename from the route.
    """
    mapping: dict[str, str] = {}
    for item in provenance.get("files", []):
        if not isinstance(item, dict):
            continue
        route = item.get("route")
        output = item.get("output_path")
        if not isinstance(route, str) or not isinstance(output, str):
            continue
        route_path = canonical_route(route)
        output_path = safe_site_path(output).as_posix()
        previous = mapping.setdefault(route_path, output_path)
        assert previous == output_path, (route_path, previous, output_path)
    return mapping


def output_path_for_route(route: str, route_outputs: dict[str, str]) -> str:
    route_path = canonical_route(route)
    assert route_path in route_outputs, route
    return route_outputs[route_path]


def output_path_for_recorded_path(raw: str, route_outputs: dict[str, str]) -> str:
    """Resolve a provenance path that may be stored as a route or output path."""
    candidate = safe_site_path(raw).as_posix()
    if candidate in route_outputs.values():
        return candidate
    route_path = canonical_route(candidate)
    if route_path in route_outputs:
        return route_outputs[route_path]
    # Some gate metadata retains the source page's .html spelling while the
    # older route map stores the extensionless canonical route.
    if route_path.casefold().endswith(".html"):
        extensionless = canonical_route(route_path[:-5])
        if extensionless in route_outputs:
            return route_outputs[extensionless]
    raise AssertionError(raw)


def guide_paths(provenance: dict) -> tuple[set[str], int, int]:
    collection = provenance.get("guide_image_collections") or {}
    groups = collection.get("groups") or []
    assert collection.get("group_count") == len(groups)
    route_outputs = provenance_route_outputs(provenance)
    paths: set[str] = set()
    image_count = 0
    for group in groups:
        for key in ("guide_route", "gallery_route"):
            paths.add(output_path_for_route(group[key], route_outputs))
        images = group.get("images") or []
        assert group.get("image_count") == len(images)
        image_count += len(images)
        for image in images:
            paths.add(output_path_for_route(image["route"], route_outputs))
    assert collection.get("image_count") == image_count
    return paths, len(groups), image_count


def browser_paths(browser: dict, provenance: dict | None = None) -> set[str]:
    paths: set[str] = set()
    route_outputs = provenance_route_outputs(provenance) if provenance is not None else {}
    checks = []
    for key in ("checks", "pages", "objects"):
        value = browser.get(key, [])
        if isinstance(value, list):
            checks.extend(value)
    for check in checks:
        if not isinstance(check, dict):
            continue
        for key in ("page", "path", "route"):
            value = check.get(key)
            if isinstance(value, str) and value and not value.startswith(("http://", "https://")):
                canonical = canonical_route(value)
                paths.add(route_outputs.get(canonical, canonical))
    return paths


def pages_online_paths(pages_online: dict, provenance: dict) -> set[str]:
    paths: set[str] = set()
    route_outputs = provenance_route_outputs(provenance)
    for item in pages_online.get("objects", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            continue
        canonical = canonical_route(item["path"])
        paths.add(route_outputs.get(canonical, canonical))
    return paths


FIXED_SMOKE_PATHS = (
    "index.html",
    "__offline/route-map.json",
    "__offline/pages_runtime.js",
)
OPTIONAL_SMOKE_PATHS = (
    "info/encyclopedia/index.xml.html",
    "news/rss-08-2007.xml.html",
    "info/dungeons/karazhan-gallery.html",
)


def provenance_smoke_paths(provenance: dict) -> tuple[set[str], dict[str, int]]:
    """Select release-critical objects from provenance rather than old counts.

    The selector deliberately keeps the required historical categories visible:
    all Flash/WASM payloads, nine talent pages and their catalogs, the three
    encyclopedia pages plus TheBroken when present, Source16 pages, BlizzCast,
    and the existing guide collections.
    """
    route_outputs = provenance_route_outputs(provenance)
    paths: set[str] = set()
    categories = {
        "flash_or_wasm": set(),
        "talent": set(),
        "encyclopedia": set(),
        "thebroken": set(),
        "source16_pages": set(),
        "blizzcast": set(),
    }
    for item in provenance.get("files", []):
        if not isinstance(item, dict):
            continue
        route = str(item.get("route") or "")
        output_raw = item.get("output_path")
        if not isinstance(output_raw, str):
            continue
        output = safe_site_path(output_raw).as_posix()
        low_route = route.casefold()
        low_output = output.casefold()
        if any(f"/encyclopedia/{number}" in low_route for number in ("315", "349", "474")):
            if low_output.endswith(".html"):
                categories["encyclopedia"].add(output)
        if ("thebroken" in low_route or "the-broken" in low_route or
                "thebroken" in low_output or "the-broken" in low_output or
                "unbroken" in low_route or "unbroken" in low_output):
            if item.get("role") != "route_alias" and low_output.endswith((".html", ".xml")):
                categories["thebroken"].add(output)
        if item.get("role") == "source16_main_page":
            categories["source16_pages"].add(output)
        if "blizzcast" in low_route or "blizzcast" in low_output:
            categories["blizzcast"].add(output)

    # Flash exhibits are explicitly pinned in provenance.  This avoids
    # treating unrelated historical business SWFs as one of the three
    # manually validated players while still deriving the runtime WASM
    # members from the same provenance object.
    flash_exhibits = provenance.get("flash_exhibits") or {}
    original_swfs = flash_exhibits.get("original_swfs") or {}
    runtime_files = flash_exhibits.get("files") or []
    if original_swfs or runtime_files:
        for entry in original_swfs.values():
            if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                categories["flash_or_wasm"].add(
                    output_path_for_recorded_path(entry["path"], route_outputs)
                )
        for entry in runtime_files:
            if not isinstance(entry, dict) or entry.get("kind") != "flash_runtime":
                continue
            output_raw = entry.get("output_path")
            if isinstance(output_raw, str) and output_raw.casefold().endswith(".wasm"):
                categories["flash_or_wasm"].add(
                    output_path_for_recorded_path(output_raw, route_outputs)
                )
    else:
        # Keep a strict fallback for older receipts that predate the
        # structured exhibit block; v52 receipts are expected to carry it.
        for item in provenance.get("files", []):
            if not isinstance(item, dict) or not isinstance(item.get("output_path"), str):
                continue
            output = safe_site_path(item["output_path"]).as_posix()
            if output.casefold().endswith((".swf", ".wasm")):
                categories["flash_or_wasm"].add(output)

    # The nine talent pages are recorded by the accepted box-layout bundle;
    # catalogs are recorded by the two related-talent bundles.  The metadata
    # keeps this selector independent of broad substring matches in image
    # filenames and aliases.
    talent_layout = provenance.get("talent_box_layout_compatibility") or {}
    talent_records = talent_layout.get("records") or []
    talent_page_routes = {
        route
        for record in talent_records
        if isinstance(record, dict)
        for route in (record.get("page_routes") or [])
        if isinstance(route, str)
    }
    for route in talent_page_routes:
        categories["talent"].add(output_path_for_recorded_path(route, route_outputs))
    for key in ("related_talent_icons", "related_talent_ui"):
        catalog = provenance.get(key) or {}
        catalog_path = catalog.get("catalog_path")
        if isinstance(catalog_path, str):
            categories["talent"].add(
                output_path_for_recorded_path(catalog_path, route_outputs)
            )
    if not talent_page_routes:
        # Compatibility fallback for pre-bundle receipts.  Restrict it to
        # HTML/JSON outputs so icon payloads never inflate this page category.
        for item in provenance.get("files", []):
            if not isinstance(item, dict) or not isinstance(item.get("output_path"), str):
                continue
            output = safe_site_path(item["output_path"]).as_posix()
            if "talent" in output.casefold() and output.casefold().endswith((".html", ".json")):
                categories["talent"].add(output)

    # v52 adds one source-backed dynamic address for The Broken.  The target
    # is intentionally a route-map reuse, so smoke the canonical JPEG and
    # public catalog but never fabricate a second target file.
    related_guide = provenance.get("related_guide_images") or {}
    related_guide_paths: set[str] = set()
    catalog_path = related_guide.get("catalog_path")
    if isinstance(catalog_path, str):
        related_guide_paths.add(output_path_for_recorded_path(catalog_path, route_outputs))
    for source_route in (related_guide.get("route_reuses") or {}).values():
        if isinstance(source_route, str):
            related_guide_paths.add(output_path_for_recorded_path(source_route, route_outputs))

    paths.update(*(categories[key] for key in categories))
    paths.update(related_guide_paths)
    guide, groups, images = guide_paths(provenance)
    paths.update(guide)
    counts = {key: len(value) for key, value in categories.items()}
    counts.update({"groups": groups, "images": images,
                   "related_guide_reuses": len(related_guide.get("route_reuses") or {})})
    return paths, counts


def smoke_paths(provenance: dict, local: dict, browser: dict, pages_online: dict,
                site: Path | None = None) -> tuple[list[str], dict[str, int]]:
    paths = local_object_paths(local)
    derived, counts = provenance_smoke_paths(provenance)
    paths.update(derived)
    paths.update(browser_paths(browser, provenance))
    paths.update(pages_online_paths(pages_online, provenance))
    paths.update(FIXED_SMOKE_PATHS)
    if site is not None:
        paths.update(path for path in OPTIONAL_SMOKE_PATHS if (site / safe_site_path(path)).is_file())
        aldor_gate = aldor_scryers_gate(site)
        if aldor_gate["status"] == "accepted":
            paths.update(aldor_gate["smoke_paths"])
        counts["aldor_scryers"] = len(aldor_gate["smoke_paths"])
    else:
        counts["aldor_scryers"] = 0
    return sorted(paths), counts


def aldor_scryers_gate(site: Path) -> dict[str, object]:
    """Return the explicit v52 final-acceptance gate for the new lore smoke.

    The source adapter acceptance is deliberately insufficient.  New lore
    bytes and the two existing faction pages enter the portable smoke set only
    when the separate v52 final acceptance record explicitly accepts the
    integration and lists the exact routes.  A missing or malformed record is
    a recorded non-gate, never an implicit pass.
    """
    result: dict[str, object] = {
        "path": FINAL_ACCEPTANCE_REL,
        "status": "missing",
        "smoke_paths": [],
        "required_paths": list(ALDOR_SCRYERS_SMOKE_PATHS),
    }
    gate_path = ROOT / FINAL_ACCEPTANCE_REL
    if not gate_path.is_file():
        return result
    try:
        data = read_json(gate_path)
    except (OSError, UnicodeError, json.JSONDecodeError):
        result["status"] = "invalid_json"
        return result
    gate = data.get("aldor_scryers_lore")
    if data.get("accepted") is not True or not isinstance(gate, dict):
        result["status"] = "not_accepted"
        return result
    if gate.get("accepted") is not True:
        result["status"] = "lore_gate_not_accepted"
        return result
    if gate.get("version") not in (None, "v52"):
        result["status"] = "wrong_version"
        return result
    if gate.get("generated_relative") != ALDOR_SCRYERS_SMOKE_PATHS[0]:
        result["status"] = "wrong_generated_path"
        return result
    listed = gate.get("page_paths")
    if not isinstance(listed, list) or set(listed) != set(ALDOR_SCRYERS_SMOKE_PATHS[1:]):
        result["status"] = "page_paths_not_exact"
        return result
    missing = [path for path in ALDOR_SCRYERS_SMOKE_PATHS
               if not (site / safe_site_path(path)).is_file()]
    if missing:
        result["status"] = "accepted_gate_missing_site_objects"
        result["missing_site_objects"] = missing
        return result
    result["status"] = "accepted"
    result["smoke_paths"] = list(ALDOR_SCRYERS_SMOKE_PATHS)
    result["acceptance_sha256"] = sha_path(gate_path)
    return result


def run_local(args: list[str], *, cwd: Path = ROOT, timeout: int = 60) -> str:
    from datetime import datetime, timezone
    remaining = (datetime(2026, 10, 21, 14, 10, tzinfo=timezone.utc) - datetime.now(timezone.utc)).total_seconds()
    if remaining <= 0:
        raise RuntimeError("release operation cutoff reached")
    return subprocess.check_output(args, cwd=cwd, text=True, timeout=min(timeout, remaining)).strip()


def disk_floor_ok(path: Path = ROOT) -> bool:
    return shutil.disk_usage(path).free >= FLOOR

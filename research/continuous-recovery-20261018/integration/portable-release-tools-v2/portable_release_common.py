"""Shared, parameterized paths and local helpers for a future 2026-10-18 release.

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
RUN_DATE = "20261018"
FLOOR = 11005853696
REPO = "vvcchh0/WOW-Encyclopedia-Deployable-Archive"
TAG = "archive-20080512-browser-20261018"
VERSION_RE = re.compile(r"v\d+\Z")


def validate_version(version: str) -> str:
    if not VERSION_RE.fullmatch(version):
        raise ValueError("version must match vNN, for example v32")
    return version


def release_paths(version: str) -> dict[str, Path]:
    version = validate_version(version)
    publication = ROOT / f"research/continuous-recovery-{RUN_DATE}/publication"
    site = ROOT / f".scratch/pages-resources-{RUN_DATE}-{version}"
    archive = ROOT / f"artifacts/WOW_Encyclopedia_20080512_browser_{RUN_DATE}_{version}.zip"
    return {
        "publication": publication,
        "site": site,
        "archive": archive,
        "sidecar": archive.with_name(archive.name + ".sha256"),
        "local": publication / f"root-{version}-local-acceptance.json",
        "export": publication / f"root-{version}-export-acceptance.json",
        "browser": publication / f"root-{version}-browser-acceptance.json",
        "pages_online": publication / f"root-{version}-pages-online-acceptance.json",
        "package_report": publication / f"{version}-portable-package-report.json",
        "portable": publication / f"root-{version}-portable-acceptance.json",
        "draft": publication / f"{version}-release-draft.json",
        "notes": publication / f"{version}-release-notes.md",
        "publication_report": publication / f"root-{version}-release-publication.json",
        "extract": ROOT / f".scratch/local bundle smoke {RUN_DATE} {version}",
        "server_log": publication / f"{version}-portable-server-local.log",
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
    """Derive changed/new smoke objects from the final local receipt."""
    paths = {
        str(item["path"])
        for item in local.get("objects", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    for key, value in local.items():
        if key.startswith("changed_since_live_") and isinstance(value, list):
            paths.update(str(item) for item in value if isinstance(item, str))
    return {safe_site_path(path).as_posix() for path in paths}


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
    checks = browser.get("checks", [])
    if not isinstance(checks, list):
        checks = []
    for check in checks:
        if not isinstance(check, dict):
            continue
        for key in ("page", "path", "route"):
            value = check.get(key)
            if isinstance(value, str) and value and not value.startswith(("http://", "https://")):
                canonical = canonical_route(value)
                paths.add(route_outputs.get(canonical, canonical))
    return paths


FIXED_SMOKE_PATHS = (
    "index.html",
    "info/encyclopedia/index.xml.html",
    "news/rss-08-2007.xml.html",
    "__offline/route-map.json",
    "__offline/pages_runtime.js",
)
OPTIONAL_SMOKE_PATHS = ("info/dungeons/karazhan-gallery.html",)


def smoke_paths(provenance: dict, local: dict, browser: dict, pages_online: dict,
                site: Path | None = None) -> tuple[list[str], dict[str, int]]:
    paths = local_object_paths(local)
    guide, groups, images = guide_paths(provenance)
    paths.update(guide)
    paths.update(browser_paths(browser, provenance))
    for item in pages_online.get("objects", []):
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            canonical = canonical_route(item["path"])
            paths.add(provenance_route_outputs(provenance).get(canonical, canonical))
    paths.update(FIXED_SMOKE_PATHS)
    if site is not None:
        paths.update(path for path in OPTIONAL_SMOKE_PATHS if (site / safe_site_path(path)).is_file())
    return sorted(paths), {"groups": groups, "images": images}


def run_local(args: list[str], *, cwd: Path = ROOT, timeout: int = 60) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True, timeout=timeout).strip()


def disk_floor_ok(path: Path = ROOT) -> bool:
    return shutil.disk_usage(path).free >= FLOOR

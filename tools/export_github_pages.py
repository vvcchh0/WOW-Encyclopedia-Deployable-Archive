#!/usr/bin/env python3
"""Export the frozen offline mirror as a GitHub Pages compatible tree.

The loopback mirror can choose a response MIME type and resolve aliases at
request time.  GitHub Pages cannot do either, so this exporter writes HTML
variants for historical ``.xml`` pages, concrete alias stubs, and a small
client side route adapter.  The input ``offline/site`` and its build
manifest are read-only; the output is built in a new directory and then
renamed atomically.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import io
import json
import mimetypes
import os
import posixpath
import re
import shutil
import sys
import time
import urllib.parse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = ROOT / "offline/site"
DEFAULT_MANIFEST = ROOT / "offline/build-manifest.json"
DEFAULT_OUTPUT = ROOT / ".scratch/pages-preview"
DEFAULT_BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
DEFAULT_MAX_BYTES: int | None = None
DEFAULT_MIN_FREE_BYTES = 11_005_853_696
PAGES_CSP = (
    "default-src 'self' data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; connect-src 'self'; form-action 'self'; "
    "frame-src 'self'; object-src 'none'"
)

if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
import offline_mirror as mirror  # noqa: E402
import historical_exhibits  # noqa: E402
import guide_previews  # noqa: E402
import guide_image_collections  # noqa: E402
import non_gallery_compat  # noqa: E402
import offline_flash  # noqa: E402
import blizzcast_reader  # noqa: E402
import talent_compat  # noqa: E402
import related_talent_icons  # noqa: E402
import source16_layout_compat  # noqa: E402
from toplist_compat import ToplistCompatError, rewrite_toplist_script  # noqa: E402


class PagesExportError(RuntimeError):
    """Raised when a frozen source or safe output invariant fails."""


_PROMOTION_RETRY_WINERRORS = frozenset({5, 32, 33})
_PROMOTION_MAX_SECONDS = 10.0
_PROMOTION_MAX_ATTEMPTS = 8


def _path_exists_including_broken_link(path: Path) -> bool:
    """Return whether a destination pathname already occupies a directory entry."""

    return os.path.lexists(os.fspath(path))


def _windows_error_code(error: OSError) -> int | None:
    """Read a Windows sharing/permission code while remaining testable off Windows."""

    winerror = getattr(error, "winerror", None)
    return int(winerror) if winerror is not None else None


def _promote_partial_output(
    partial: Path,
    output: Path,
    *,
    replace=None,
    sleep=None,
    monotonic=None,
    max_seconds: float = _PROMOTION_MAX_SECONDS,
) -> None:
    """Promote a complete partial tree with bounded Windows transient retries.

    The destination is checked before every attempt and is never intentionally
    overwritten.  Only Windows permission/sharing errors are retried.  The
    caller owns cleanup; if this helper raises, ``partial`` is deliberately
    left in place for recovery or inspection.
    """

    replace_fn = replace or Path.replace
    sleep_fn = sleep or time.sleep
    monotonic_fn = monotonic or time.monotonic
    deadline = monotonic_fn() + min(float(max_seconds), _PROMOTION_MAX_SECONDS)
    attempts = 0
    delays = (0.10, 0.20, 0.40, 0.80, 1.60, 3.20, 3.70)
    while True:
        if _path_exists_including_broken_link(output):
            raise PagesExportError(f"refusing to overwrite existing output during promotion: {output}")
        attempts += 1
        try:
            replace_fn(partial, output)
            return
        except OSError as exc:
            if _windows_error_code(exc) not in _PROMOTION_RETRY_WINERRORS:
                raise
            now = monotonic_fn()
            if attempts >= _PROMOTION_MAX_ATTEMPTS or now >= deadline:
                raise
            remaining = deadline - now
            if remaining <= 0:
                raise
            sleep_fn(min(delays[min(attempts - 1, len(delays) - 1)], remaining))


HTML_KINDS = {"html", "menu_html"}
TEXT_KINDS = HTML_KINDS | {"css", "js", "xsl", "xml", "legacy_component", "support"}
_ROOT_LITERAL_RE = re.compile(
    r"(?P<quote>['\"])(?P<url>/[^'\"\s<>]+)(?P<trailing>\s*)(?P=quote)"
)
_XML_BARE_AMP_RE = re.compile(
    r"&(?!#(?:x[0-9A-Fa-f]+|[0-9]+);|(?:amp|lt|gt|quot|apos);)"
)
COMPATIBILITY_ROUTE_ALIASES: dict[str, str] = {
    "/info/basics/dailyquests.shtml": "/info/basics/dailyquests.html",
    "/info/basics/titles.shtml": "/info/basics/titles.html",
    "/info/basics/benice.shtml": "/info/basics/benice.html",
    "/info/credits.shtml": "/info/credits.html",
    "/info/info/items/armorsets/": "/info/items/armorsets/index.html",
    "/wrath/wallpapers.xml": "/wrath//wallpapers.xml",
}
_NAVIGATION_RASTER_EXTENSIONS = frozenset({".gif", ".png", ".jpg", ".jpeg"})


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return mirror.sha256_file(path)


def normalize_base_path(value: str) -> str:
    value = "/" + value.strip() + "/"
    value = re.sub(r"/{2,}", "/", value)
    if not value.startswith("/") or ".." in value.split("/"):
        raise PagesExportError(f"unsafe project base path: {value!r}")
    return value


def safe_route(route: str) -> str:
    if not isinstance(route, str) or not route.startswith("/"):
        raise PagesExportError(f"route is not absolute: {route!r}")
    if "\x00" in route or "\\" in route:
        raise PagesExportError(f"unsafe route: {route!r}")
    parts = route.split("/")
    if ".." in parts:
        raise PagesExportError(f"route traversal: {route!r}")
    return route


def is_html_record(record: dict[str, Any]) -> bool:
    if record.get("kind") in HTML_KINDS:
        return True
    mime = str(record.get("mime") or record.get("source_mime") or "").split(";", 1)[0].strip().casefold()
    return mime == "text/html"


def static_rel_for_route(route: str, record: dict[str, Any] | None = None) -> str:
    route = safe_route(route)
    if route == "/":
        return "index.html"
    # A few historical logical routes contain repeated separators.  Preserve
    # the logical route key for lookup, but emit a canonical filesystem path
    # so Windows and Pages do not disagree about the actual resource name.
    path = re.sub(r"/{2,}", "/", route.lstrip("/"))
    if path.endswith("/"):
        return path + "index.html"
    if record is not None and is_html_record(record):
        lower = path.casefold()
        if not (lower.endswith(".html") or lower.endswith(".htm")):
            path += ".html"
    return path


def static_url(base_path: str, relative: str) -> str:
    return base_path + relative.lstrip("/")


def workspace_size(root: Path, excluded: Path | None = None) -> int:
    total = 0
    excluded = excluded.resolve() if excluded else None
    for current, dirs, files in os.walk(root):
        current_path = Path(current).resolve()
        if excluded and (current_path == excluded or excluded in current_path.parents):
            dirs[:] = []
            continue
        for name in files:
            try:
                total += (current_path / name).stat().st_size
            except OSError:
                continue
    return total


def output_estimate(records: list[dict[str, Any]], extra_bytes: int = 0) -> int:
    source_total = sum(int(item.get("derived_length") or 0) for item in records) + int(extra_bytes)
    # URL rewriting, route stubs, provenance and a conservative 25% growth
    # allowance are included.  This is intentionally larger than the known
    # source tree and is checked again after the export.
    return source_total + source_total // 4 + 128 * 1024 * 1024


_OVERLAY_MIMES = {"image/gif": "GIF", "image/png": "PNG", "image/jpeg": "JPEG"}
_OVERLAY_URL_HOSTS = {"www.worldofwarcraft.com", "worldofwarcraft.com"}
_ARMORY_SUPPLEMENT_HOSTS = {"www.wowarmory.com", "armory.wow-europe.com"}
_SUPPLEMENT_OVERLAY_URL_HOSTS = _OVERLAY_URL_HOSTS | {
    "www.wow-europe.com", "wow-europe.com", "www.blizzard.com", *_ARMORY_SUPPLEMENT_HOSTS,
}
_OVERLAY_TIMESTAMP_RE = re.compile(r"^2008\d{10}$")


def _workspace_path(path: Path, workspace_root: Path, *, label: str) -> Path:
    """Resolve a supplied overlay path while keeping it inside the workspace."""

    resolved = path.resolve()
    try:
        resolved.relative_to(workspace_root)
    except ValueError as exc:
        raise PagesExportError(f"{label} escapes workspace: {path}") from exc
    return resolved


def _overlay_url(
    value: Any,
    *,
    label: str,
    allowed_hosts: set[str] | frozenset[str] = frozenset(_OVERLAY_URL_HOSTS),
) -> tuple[str, urllib.parse.SplitResult]:
    if not isinstance(value, str) or not value:
        raise PagesExportError(f"image overlay {label} URL is missing")
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise PagesExportError(f"image overlay {label} URL is invalid: {value!r}") from exc
    scheme = parsed.scheme.casefold()
    raw_host = (parsed.hostname or "").casefold()
    host = raw_host.rstrip(".")
    if scheme not in {"http", "https"} or host not in allowed_hosts:
        raise PagesExportError(f"image overlay {label} URL is not an approved image origin: {value!r}")
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    if parsed.username or parsed.password or (port is not None and not default_port) or parsed.query or parsed.fragment:
        raise PagesExportError(f"image overlay {label} URL has unsafe authority or suffix: {value!r}")
    if not parsed.path.startswith("/") or "\\" in parsed.path or "\x00" in parsed.path:
        raise PagesExportError(f"image overlay {label} URL path is unsafe: {value!r}")
    decoded_path = urllib.parse.unquote(parsed.path)
    if "\\" in decoded_path or "\x00" in decoded_path or ":" in decoded_path:
        raise PagesExportError(f"image overlay {label} decoded URL path is unsafe: {value!r}")
    parts = decoded_path.split("/")
    if any(part in {".", ".."} for part in parts[1:]) or any(part == "" for part in parts[1:-1]):
        raise PagesExportError(f"image overlay {label} URL path has dot segments or double slashes: {value!r}")
    if any(part and part[-1] in {".", " "} for part in parts[1:]):
        raise PagesExportError(f"image overlay {label} URL path is non-canonical: {value!r}")
    if host in _ARMORY_SUPPLEMENT_HOSTS:
        if raw_host != host:
            raise PagesExportError(f"image overlay {label} Armory host is not exact: {value!r}")
        if not decoded_path.startswith("/images/icons/"):
            raise PagesExportError(
                f"image overlay {label} Armory supplement path must start with /images/icons/: {value!r}"
            )
    return value, parsed


def _verify_overlay_image(data: bytes, declared_mime: str, *, label: str) -> str:
    mime = declared_mime.split(";", 1)[0].strip().casefold()
    expected_format = _OVERLAY_MIMES.get(mime)
    if expected_format is None:
        raise PagesExportError(f"image overlay {label} MIME is not an accepted image type: {declared_mime!r}")
    if expected_format == "GIF" and data[:6] not in {b"GIF87a", b"GIF89a"}:
        raise PagesExportError(f"image overlay {label} GIF magic mismatch")
    if expected_format == "PNG" and data[:8] != b"\x89PNG\r\n\x1a\n":
        raise PagesExportError(f"image overlay {label} PNG magic mismatch")
    if expected_format == "JPEG" and not data.startswith(b"\xff\xd8\xff"):
        raise PagesExportError(f"image overlay {label} JPEG magic mismatch")
    try:
        from PIL import Image

        with Image.open(io.BytesIO(data)) as image:
            detected = image.format
            image.verify()
        if detected != expected_format:
            raise PagesExportError(f"image overlay {label} Pillow format mismatch: {detected!r}")
    except PagesExportError:
        raise
    except Exception as exc:
        raise PagesExportError(f"image overlay {label} failed image verification") from exc
    return mime


def _overlay_relative_source(map_path: Path, local_path: str, workspace_root: Path, *, label: str) -> Path:
    if not isinstance(local_path, str) or not local_path:
        raise PagesExportError(f"image overlay {label} local_path is missing")
    candidate = Path(local_path)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        # Existing source maps use repository-relative paths.  The fallback
        # keeps small, workspace-local maps convenient without weakening the
        # containment check below.
        resolved = (workspace_root / candidate).resolve()
        if not resolved.exists():
            resolved = (map_path.parent / candidate).resolve()
    return _workspace_path(resolved, workspace_root, label=f"image overlay {label} local_path")


def _overlay_temporal_class(
    actual_dt: datetime,
    anchor_dt: datetime,
    *,
    allow_later_image_supplements: bool = False,
) -> str:
    year_start = datetime(2008, 1, 1)
    year_end = datetime(2008, 12, 31, 23, 59, 59)
    if actual_dt < year_start:
        return "pre_2008"
    if actual_dt <= anchor_dt:
        return "baseline_2008"
    if actual_dt <= year_end:
        return "late_2008"
    if allow_later_image_supplements:
        return "post_2008"
    raise PagesExportError(f"image supplement capture is after 2008: {actual_dt:%Y%m%d%H%M%S}")


def _load_image_overlay_maps(
    image_source_maps: list[Path] | tuple[Path, ...],
    *,
    workspace_root: Path,
    anchor_timestamp: str,
    frozen_routes: set[str],
    frozen_static_paths: set[str],
    supplement: bool,
    allow_later_image_supplements: bool = False,
) -> tuple[list[dict[str, Any]], int]:
    """Validate primary or explicit supplement image maps.

    The primary loader remains restricted to the two canonical WoW hosts and
    the fixed 2008 anchor.  Supplement maps have their own explicit host and
    date policy; they never enter this path implicitly.
    """

    if not image_source_maps:
        return [], 0
    if not isinstance(anchor_timestamp, str) or not re.fullmatch(r"\d{14}", anchor_timestamp):
        raise PagesExportError(f"manifest anchor timestamp is invalid: {anchor_timestamp!r}")
    try:
        anchor_dt = datetime.strptime(anchor_timestamp, "%Y%m%d%H%M%S")
    except ValueError as exc:
        raise PagesExportError(f"manifest anchor timestamp is not a real date: {anchor_timestamp!r}") from exc
    entries: list[dict[str, Any]] = []
    by_route: dict[str, dict[str, Any]] = {}
    source_map_hashes: dict[Path, str] = {}
    static_paths = {str(path).casefold() for path in frozen_static_paths}
    allowed_hosts = _SUPPLEMENT_OVERLAY_URL_HOSTS if supplement else _OVERLAY_URL_HOSTS
    strategy = "explicit_supplement_image_overlay" if supplement else "primary_image_overlay"
    total_bytes = 0
    for raw_map in image_source_maps:
        map_path = _workspace_path(Path(raw_map), workspace_root, label="image source map")
        if not map_path.is_file():
            raise PagesExportError(f"image source map is missing: {map_path}")
        try:
            payload = json.loads(map_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise PagesExportError(f"image source map is not valid JSON: {map_path}") from exc
        items = payload.get("items") if isinstance(payload, dict) else None
        if not isinstance(items, list):
            raise PagesExportError(f"image source map has no items list: {map_path}")
        source_map_sha256 = source_map_hashes.get(map_path)
        if source_map_sha256 is None:
            source_map_sha256 = sha256_file(map_path)
            source_map_hashes[map_path] = source_map_sha256
        for index, item in enumerate(items):
            label = f"{map_path.name}[{index}]"
            if not isinstance(item, dict) or str(item.get("kind") or "").casefold() != "image":
                raise PagesExportError(f"{label} is not an image entity")
            logical_url = item.get("logical_url") or item.get("original")
            logical_url, _ = _overlay_url(logical_url, label=label, allowed_hosts=allowed_hosts)
            original = item.get("original") or logical_url
            original, _ = _overlay_url(original, label=label, allowed_hosts=allowed_hosts)
            if mirror.origin_key(logical_url) != mirror.origin_key(original):
                raise PagesExportError(f"{label} logical_url and original disagree")
            is_primary = mirror.is_primary_origin(logical_url)
            route = mirror.route_path(logical_url) if is_primary else mirror.origin_route(logical_url)
            if route in frozen_routes or route.startswith("/__offline/") or route in {"/404.html", "/README.md"}:
                raise PagesExportError(f"{label} would override an existing route: {route}")
            if not route.casefold().endswith((".gif", ".png", ".jpg", ".jpeg")):
                raise PagesExportError(f"{label} image route has no supported extension: {route!r}")
            relative = static_rel_for_route(route)
            recovery_method = item.get("recovery_method")
            if recovery_method not in (None, "payload_digest_reuse"):
                raise PagesExportError(f"{label} recovery_method is unsupported: {recovery_method!r}")
            is_digest_reuse = recovery_method == "payload_digest_reuse"
            actual = str(item.get("actual_timestamp") or "")
            indexed = str(item.get("indexed_capture_timestamp") or "")
            if not re.fullmatch(r"\d{14}", indexed):
                raise PagesExportError(f"{label} indexed capture timestamp is invalid: {indexed!r}")
            try:
                indexed_dt = datetime.strptime(indexed, "%Y%m%d%H%M%S")
            except ValueError as exc:
                raise PagesExportError(f"{label} indexed capture timestamp is not a real date: {indexed!r}") from exc
            payload_source: dict[str, Any] | None = None
            if is_digest_reuse:
                # A reused payload has two independent dates: the target CDX
                # index date and the accepted local payload's real capture
                # date.  The former controls the target's temporal policy;
                # the latter is retained only as source evidence.
                if item.get("actual_timestamp") not in (None, ""):
                    raise PagesExportError(f"{label} digest reuse must omit actual_timestamp")
                raw_payload_source = item.get("payload_source")
                if not isinstance(raw_payload_source, dict):
                    raise PagesExportError(f"{label} payload_source evidence is missing")
                payload_original, _ = _overlay_url(
                    raw_payload_source.get("original_url"),
                    label=f"{label} payload_source",
                    allowed_hosts=allowed_hosts,
                )
                payload_capture = raw_payload_source.get("actual_capture_timestamp")
                if not isinstance(payload_capture, str) or not re.fullmatch(r"\d{14}", payload_capture):
                    raise PagesExportError(f"{label} payload_source actual timestamp is invalid: {payload_capture!r}")
                try:
                    payload_capture_dt = datetime.strptime(payload_capture, "%Y%m%d%H%M%S")
                except ValueError as exc:
                    raise PagesExportError(
                        f"{label} payload_source actual timestamp is not a real date: {payload_capture!r}"
                    ) from exc
                payload_sha = str(raw_payload_source.get("sha256") or "").casefold()
                if not re.fullmatch(r"[0-9a-f]{64}", payload_sha):
                    raise PagesExportError(f"{label} payload_source SHA-256 evidence is missing or invalid")
                try:
                    payload_length = int(raw_payload_source.get("length"))
                except (TypeError, ValueError) as exc:
                    raise PagesExportError(f"{label} payload_source length evidence is invalid") from exc
                if payload_length < 1:
                    raise PagesExportError(f"{label} payload_source length evidence is invalid")
                payload_source = {
                    "original_url": payload_original,
                    "actual_capture_timestamp": payload_capture,
                    "sha256": payload_sha,
                    "length": payload_length,
                }
                actual = ""
            else:
                if not re.fullmatch(r"\d{14}", actual) or actual != indexed:
                    raise PagesExportError(f"{label} capture timestamp is invalid or differs: {actual!r}/{indexed!r}")
                try:
                    actual_dt = datetime.strptime(actual, "%Y%m%d%H%M%S")
                except ValueError as exc:
                    raise PagesExportError(f"{label} capture timestamp is not a real date: {actual!r}/{indexed!r}") from exc
                if indexed_dt != actual_dt:
                    raise PagesExportError(f"{label} capture timestamp is invalid or differs: {actual!r}/{indexed!r}")
            if supplement:
                temporal_class = _overlay_temporal_class(
                    indexed_dt,
                    anchor_dt,
                    allow_later_image_supplements=allow_later_image_supplements,
                )
                declared_class = str(item.get("temporal_class") or "")
                if declared_class != temporal_class:
                    raise PagesExportError(
                        f"{label} temporal_class does not match capture date: {declared_class!r}/{temporal_class!r}"
                    )
            else:
                if not _OVERLAY_TIMESTAMP_RE.fullmatch(indexed) or indexed_dt.year != 2008 or indexed_dt > anchor_dt:
                    raise PagesExportError(f"{label} capture timestamp is outside the 2008 baseline: {actual!r}/{indexed!r}")
                temporal_class = "baseline_2008"
                declared_class = str(item.get("temporal_class") or "")
                if declared_class and declared_class != temporal_class:
                    raise PagesExportError(
                        f"{label} temporal_class is not allowed on the primary baseline entry: {declared_class!r}"
                    )
            digest = item.get("cdx_digest")
            if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[A-Z2-7]+", digest.upper())):
                raise PagesExportError(f"{label} CDX digest is invalid")
            if is_digest_reuse and not isinstance(digest, str):
                raise PagesExportError(f"{label} digest reuse requires cdx_digest evidence")
            source = _overlay_relative_source(map_path, item.get("local_path"), workspace_root, label=label)
            if not source.is_file():
                raise PagesExportError(f"{label} source file is missing: {source}")
            data = source.read_bytes()
            expected_sha = str(item.get("sha256") or "").casefold()
            actual_sha = hashlib.sha256(data).hexdigest()
            if not re.fullmatch(r"[0-9a-f]{64}", expected_sha) or actual_sha != expected_sha:
                raise PagesExportError(f"{label} source SHA-256 mismatch")
            expected_length = item.get("length", item.get("source_length"))
            if expected_length is not None:
                try:
                    expected_length = int(expected_length)
                except (TypeError, ValueError) as exc:
                    raise PagesExportError(f"{label} source length is invalid") from exc
                if expected_length != len(data):
                    raise PagesExportError(f"{label} source length mismatch")
            mime = _verify_overlay_image(data, str(item.get("mime") or ""), label=label)
            if digest is not None:
                actual_cdx = base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")
                if actual_cdx != digest.upper():
                    raise PagesExportError(f"{label} CDX SHA-1 digest mismatch")
            if is_digest_reuse:
                if payload_source["sha256"] != actual_sha:
                    raise PagesExportError(f"{label} payload_source SHA-256 does not match copied bytes")
                if payload_source["length"] != len(data):
                    raise PagesExportError(f"{label} payload_source length does not match copied bytes")
            entry = {
                "route": route,
                "relative": relative,
                "data": data,
                "source": source,
                "map_path": map_path,
                "logical_url": logical_url,
                "original_url": original,
                "actual_timestamp": actual,
                "indexed_capture_timestamp": indexed,
                "temporal_class": temporal_class,
                "origin_namespace": mirror.origin_namespace_host(logical_url),
                "supplement_strategy": strategy,
                "cdx_digest": digest.upper() if isinstance(digest, str) else None,
                "mime": mime,
                "source_sha256": actual_sha,
                "source_length": len(data),
                "role": "image_overlay",
                "source_map_sha256": source_map_sha256,
            }
            if is_digest_reuse:
                entry.update(
                    {
                        "actual_timestamp": None,
                        "recovery_method": "payload_digest_reuse",
                        "payload_source": payload_source,
                        "capture_timestamp_basis": "target_cdx_digest",
                    }
                )
            previous = by_route.get(route)
            if previous is not None:
                if previous["source_sha256"] != actual_sha:
                    raise PagesExportError(f"{label} conflicts with another overlay for route: {route}")
                continue
            if relative.casefold() in static_paths:
                raise PagesExportError(f"{label} would collide with static output path: {relative}")
            by_route[route] = entry
            entries.append(entry)
            static_paths.add(relative.casefold())
            total_bytes += len(data)
    return entries, total_bytes


def load_image_overlays(
    image_source_maps: list[Path] | tuple[Path, ...],
    *,
    workspace_root: Path,
    anchor_timestamp: str,
    frozen_routes: set[str],
    frozen_static_paths: set[str],
) -> tuple[list[dict[str, Any]], int]:
    """Validate strict pre-anchor primary-origin image overlays."""

    return _load_image_overlay_maps(
        image_source_maps,
        workspace_root=workspace_root,
        anchor_timestamp=anchor_timestamp,
        frozen_routes=frozen_routes,
        frozen_static_paths=frozen_static_paths,
        supplement=False,
        allow_later_image_supplements=False,
    )


def load_supplement_image_overlays(
    supplement_image_source_maps: list[Path] | tuple[Path, ...],
    *,
    workspace_root: Path,
    anchor_timestamp: str,
    frozen_routes: set[str],
    frozen_static_paths: set[str],
    allow_later_image_supplements: bool = False,
) -> tuple[list[dict[str, Any]], int]:
    """Validate explicit related-site image overlays with an opt-in later-capture policy."""

    return _load_image_overlay_maps(
        supplement_image_source_maps,
        workspace_root=workspace_root,
        anchor_timestamp=anchor_timestamp,
        frozen_routes=frozen_routes,
        frozen_static_paths=frozen_static_paths,
        supplement=True,
        allow_later_image_supplements=allow_later_image_supplements,
    )


def _context_for_literal(raw: str) -> str:
    lower = raw.casefold().split("?", 1)[0].split("#", 1)[0]
    if re.search(r"\.(?:gif|jpe?g|png|webp|svg|swf|ico)$", lower):
        return "image"
    if lower.endswith(".css"):
        return "stylesheet"
    if lower.endswith((".js", ".mjs", ".htc")):
        return "script"
    return "navigation"


class PagesLocalizer:
    """Adapt offline_mirror's safe localizer to project-prefixed URLs."""

    def __init__(
        self,
        *,
        route_to_static: dict[str, str],
        aliases: dict[str, str],
        origin_index: dict[str, str],
        base_path: str,
        validated_navigation_image_routes: set[str] | frozenset[str] = frozenset(),
        validated_related_page_routes: set[str] | frozenset[str] = frozenset(),
    ) -> None:
        self.route_to_static = route_to_static
        self.aliases = aliases
        self.origin_index = origin_index
        self.base_path = base_path
        self.validated_navigation_image_routes = frozenset(validated_navigation_image_routes)
        self.validated_related_page_routes = frozenset(validated_related_page_routes)
        # ``offline_mirror.rewrite_css`` uses this explicit capability only
        # for frozen missing-image placeholders.  Its normal loopback
        # Localizer behavior remains unchanged.
        self.relocalize_image_placeholders = True

    def _static_for_route(self, route: str) -> str | None:
        return self.route_to_static.get(route) or self.aliases.get(route)

    def _validated_navigation_image_target(self, requested: str) -> str | None:
        """Resolve only an exact-origin raster route accepted by an image map."""

        try:
            parsed = urllib.parse.urlsplit(requested)
            port = parsed.port
        except ValueError:
            return None
        scheme = parsed.scheme.casefold()
        if scheme not in {"http", "https"} or not parsed.hostname:
            return None
        default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
        if parsed.username is not None or parsed.password is not None or (port is not None and not default_port):
            return None
        if parsed.query or parsed.fragment:
            return None
        requested_path = mirror.route_path(requested)
        if not requested_path.casefold().endswith(tuple(_NAVIGATION_RASTER_EXTENSIONS)):
            return None
        route = self.origin_index.get(mirror.origin_key(requested))
        if route is None or route not in self.validated_navigation_image_routes:
            return None
        if not mirror.route_path(route).casefold().endswith(tuple(_NAVIGATION_RASTER_EXTENSIONS)):
            return None
        target = self._static_for_route(route)
        if not target or not urllib.parse.urlsplit(target).path.casefold().endswith(tuple(_NAVIGATION_RASTER_EXTENSIONS)):
            return None
        return target

    def _placeholder(self, raw: str, base_url: str, context: str, reason: str) -> str:
        if context in {"image", "background", "css_url", "srcset"}:
            route = "/__offline/missing-image.svg"
        elif context in {"script", "script_url"}:
            route = "/__offline/empty.js"
        elif context in {"stylesheet", "css_import"}:
            route = "/__offline/empty.css"
        else:
            route = "/__offline/missing.html"
        target = self._static_for_route(route)
        if not target:
            raise PagesExportError(f"placeholder route missing from export map: {route}")
        query = mirror.encoded_missing_query(base_url, raw, reason)
        return target + "?" + query

    def _validated_related_page_target(self, requested: str) -> str | None:
        """Recover a former missing link only through an accepted exact origin."""

        try:
            parsed = urllib.parse.urlsplit(requested)
            port = parsed.port
        except ValueError:
            return None
        scheme = parsed.scheme.casefold()
        if scheme not in {"http", "https"} or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
            return None
        if port is not None and port != (80 if scheme == "http" else 443):
            return None
        route = self.origin_index.get(mirror.origin_key(requested))
        if route not in self.validated_related_page_routes:
            return None
        return self._static_for_route(route)

    def localize(self, raw: str, *, base_url: str, context: str, recorder: Any) -> str:
        literal = str(raw).strip()
        if not literal:
            recorder.add(raw, base_url, "preserved", raw, context, "empty reference")
            return raw
        lowered = literal.casefold()
        if lowered.startswith(("#", "javascript:", "mailto:", "tel:", "data:", "about:")):
            recorder.add(raw, base_url, "preserved", raw, context, "non-network reference")
            return raw
        if literal.startswith(self.base_path):
            recorder.add(raw, literal, "preserved", literal, context, "already Pages-prefixed")
            return literal
        try:
            absolute = urllib.parse.urljoin(base_url, literal)
            parsed = urllib.parse.urlsplit(absolute)
        except ValueError:
            absolute = literal
            parsed = urllib.parse.SplitResult("", "", literal, "", "")
        if parsed.scheme.casefold() not in {"http", "https"}:
            target = self._placeholder(literal, base_url, context, "unresolved-relative")
            recorder.add(raw, absolute, "placeholder", target, context, "unresolved-relative")
            return target
        # Earlier mirror passes may already have replaced an image with the
        # local missing-image marker while retaining the original URL in its
        # ``requested`` query parameter.  A validated image overlay can heal
        # that marker without changing the frozen source tree.
        if mirror.route_path(absolute).casefold() == "/__offline/missing-image.svg":
            requested_values = urllib.parse.parse_qs(parsed.query, keep_blank_values=True).get("requested", [])
            requested = requested_values[-1] if requested_values else ""
            if requested:
                try:
                    requested_path = mirror.route_path(requested)
                except Exception:
                    requested_path = ""
                if requested_path.casefold() != "/__offline/missing-image.svg":
                    recovered = self.localize(requested, base_url=base_url, context=context, recorder=recorder)
                    recorder.add(raw, requested, "localized", recovered, context, "recovered requested URL from missing-image marker")
                    return recovered
        if mirror.route_path(absolute).casefold() == "/__offline/missing.html":
            requested_values = urllib.parse.parse_qs(parsed.query, keep_blank_values=True).get("requested", [])
            requested = requested_values[-1] if requested_values else ""
            if requested:
                try:
                    requested_path = mirror.route_path(requested)
                except Exception:
                    requested_path = ""
                if requested_path in COMPATIBILITY_ROUTE_ALIASES:
                    recovered = self.localize(requested, base_url=base_url, context=context, recorder=recorder)
                    recorder.add(
                        raw,
                        requested,
                        "localized",
                        recovered,
                        context,
                        "recovered verified Archived News compatibility alias from missing marker",
                    )
                    return recovered
                if context == "navigation":
                    recovered = self._validated_related_page_target(requested)
                    if recovered is not None:
                        recorder.add(raw, requested, "localized", recovered, context,
                                     "recovered accepted exact-origin historical reading page")
                        return recovered
                    recovered = self._validated_navigation_image_target(requested)
                    if recovered is not None:
                        recorder.add(
                            raw,
                            requested,
                            "localized",
                            recovered,
                            context,
                            "recovered validated exact-origin raster navigation image",
                        )
                        return recovered
        # compat.js intentionally builds this query in a JavaScript string
        # prefix.  Pages has a concrete index document for it; preserve the
        # query suffix so the client page can echo the intended target.
        if mirror.route_path(absolute).rstrip("/").casefold() == "/__offline/uncollected":
            target = self._static_for_route("/__offline/uncollected/index.html")
            if target:
                suffix = ("?" + parsed.query if parsed.query else "") + ("#" + parsed.fragment if parsed.fragment else "")
                result = target + suffix
                recorder.add(raw, absolute, "localized", result, context, "Pages static uncollected route")
                return result
        route: str | None = None
        key = mirror.origin_key(absolute)
        route = self.origin_index.get(key)
        if route is None:
            path = mirror.route_path(absolute)
            # An uncollected regional or third-party image can have the same
            # path as a main-site file.  Only exact origin entries may join
            # those sites; frozen local support/namespaced paths remain valid.
            explicit_local = literal.startswith("/") and not literal.startswith("//") and path.startswith(("/__offline/", "/_origins/"))
            if mirror.is_primary_origin(absolute) or explicit_local:
                route = self.aliases.get(path) or (path if path in self.route_to_static else None)
        target = self._static_for_route(route) if route else None
        if target:
            suffix = ("?" + parsed.query if parsed.query else "") + ("#" + parsed.fragment if parsed.fragment else "")
            result = target + suffix
            recorder.add(raw, absolute, "localized", result, context, "Pages route map")
            return result
        target = self._placeholder(absolute, base_url, context, "external-or-uncollected-resource")
        if parsed.fragment:
            target += "#" + parsed.fragment
        recorder.add(raw, absolute, "placeholder", target, context, "external-or-uncollected-resource")
        return target


def rewrite_root_literals(text: str, *, base_url: str, localizer: PagesLocalizer, recorder: Any) -> str:
    """Rewrite complete root-relative JS strings without touching expressions.

    offline_mirror intentionally leaves root-relative JS strings alone for a
    loopback origin.  A project Pages site has a prefix, so complete literals
    must be prefixed here.  A literal followed by ``+`` is a dynamic prefix and
    remains untouched to avoid changing JavaScript syntax or URL composition.
    """

    def replace(match: re.Match[str]) -> str:
        raw = match.group("url")
        if raw == "//" or raw.startswith("//") or raw.startswith(localizer.base_path):
            return match.group(0)
        # Wrath uses roothost as a directory for resource concatenation.
        # Its navigation alias resolves to index.html, which is not a base
        # directory and would produce e.g. index.htmlimages/layout/....
        before = text[max(0, match.start() - 80):match.start()]
        if (
            raw == "/wrath/"
            and re.search(r"\bvar\s+roothost\s*=\s*$", before)
            and mirror.is_primary_origin(base_url)
            and urllib.parse.urlsplit(base_url).path.startswith("/wrath/")
        ):
            target = localizer.base_path + "wrath/"
            recorder.add(raw, urllib.parse.urljoin(base_url, raw), "localized", target,
                         "javascript-directory-base", "preserve verified Wrath resource directory")
            return match.group("quote") + target + match.group("trailing") + match.group("quote")
        after = text[match.end() :].lstrip()
        if after.startswith("+") and not raw.casefold().startswith(("/__offline/uncollected", "/search/")):
            return match.group(0)
        local = localizer.localize(raw, base_url=base_url, context=_context_for_literal(raw), recorder=recorder)
        q = match.group("quote")
        return q + local.replace(q, "%22") + match.group("trailing") + q

    return _ROOT_LITERAL_RE.sub(replace, text)


_GALLERY_ADDSHOTS_RE = re.compile(
    r"(?P<call>\baddshots\s*\(\s*)"
    r"(?P<quote>['\"])(?P<directory>/[^'\"\r\n<>]*?/?)"
    r"(?P=quote)"
    r"(?P<comma1>\s*,\s*)(?P<filequote>['\"])(?P<filename>ss)(?P=filequote)"
    r"(?P<comma2>\s*,\s*)(?P<count>numShots|currentShotNumber)\b",
    re.I,
)


def rewrite_gallery_addshots(
    text: str,
    *,
    base_path: str,
    base_url: str,
    recorder: Any,
) -> str:
    """Keep the historical screenshot directory under the Pages prefix.

    Only the exact, bounded ``addshots(directory, "ss", numShots)`` call is
    eligible.  The runtime still resolves each resulting full/thumbnail URL
    through the concrete route map, so preserving a directory never invents
    a collected resource.
    """

    def replace(match: re.Match[str]) -> str:
        directory = match.group("directory")
        try:
            safe_route(directory)
        except PagesExportError:
            return match.group(0)
        if "?" in directory or "#" in directory or "\\" in directory:
            return match.group(0)
        if directory.startswith(base_path):
            return match.group(0)
        prefixed = base_path + directory.lstrip("/")
        recorder.add(
            directory,
            urllib.parse.urljoin(base_url, directory),
            "localized",
            prefixed,
            "gallery_directory",
            "Pages gallery addshots directory",
        )
        quote = match.group("quote")
        return (
            match.group("call")
            + quote + prefixed + quote
            + match.group("comma1")
            + match.group("filequote") + match.group("filename") + match.group("filequote")
            + match.group("comma2") + match.group("count")
        )

    return _GALLERY_ADDSHOTS_RE.sub(replace, text)


def rewrite_inline_scripts(
    text: str,
    *,
    base_url: str,
    localizer: PagesLocalizer,
    recorder: Any,
) -> str:
    """Prefix complete route literals in inline script bodies.

    ``offline_mirror.rewrite_html`` already localizes element attributes and
    performs its historical script compatibility edits.  It intentionally
    leaves root-relative JavaScript string literals alone because its loopback
    server has no project prefix.  Pages needs those literals prefixed too,
    including the ``topicsArray[*].linkString`` values used by the exact-title
    search shim.  Restrict the pass to script raw-text bodies so CSS, visible
    text, and HTML attributes are not rewritten a second time.
    """

    script_re = re.compile(r"(<script\b[^>]*>)(.*?)(</script\s*>)", re.I | re.S)

    def replace(match: re.Match[str]) -> str:
        body = match.group(2)
        if not body:
            return match.group(0)
        body = rewrite_gallery_addshots(
            body,
            base_path=localizer.base_path,
            base_url=base_url,
            recorder=recorder,
        )
        body = rewrite_root_literals(
            body,
            base_url=base_url,
            localizer=localizer,
            recorder=recorder,
        )
        return match.group(1) + body + match.group(3)

    return script_re.sub(replace, text)


_RETIRED_ARMORY_TOOLTIP_ROUTE = "/new-hp/js/enhancedtip.js"
_RETIRED_ARMORY_TOOLTIP_MESSAGE = (
    "Historical exhibit: the retired Armory item-details service is unavailable in this archive."
)
_RETIRED_ARMORY_REQUESTHTML_RE = re.compile(
    r"function\s+requestHTML\s*\(\s*thisID\s*\)\s*\{.*?\r?\n\}",
    re.I | re.S,
)
_RETIRED_ARMORY_REQUESTHTML_GUARDS = (
    "if(portalOpen)",
    "darkPortal.requestXml(thisID)",
    "xmlRetrievalFrame = document.createElement(\"iframe\")",
    "xmlRetrievalFrame.name = \"darkPortalFrame\"",
    "xmlRetrievalFrame.id = \"xmlPortal\"",
    "document.domain = currentDomain",
    "xmlRetrievalFrame.src = xmlFrameTarget",
)


def rewrite_retired_armory_tooltip(text: str, route: str) -> tuple[str, bool]:
    """Replace only the retired Armory request function on its exact route.

    ``enhancedXmlTTip`` still displays an already cached item node.  A missing
    node used to create a cross-origin iframe and assign ``document.domain``;
    the service is retired, so the request function becomes a static exhibit
    caption.  A target-route source with a missing or duplicated complete
    function signature fails loudly rather than receiving a broad rewrite.
    """

    if route != _RETIRED_ARMORY_TOOLTIP_ROUTE:
        return text, False
    signature_count = len(
        re.findall(r"function\s+requestHTML\s*\(\s*thisID\s*\)", text, re.I)
    )
    if signature_count != 1:
        raise PagesExportError(
            f"retired Armory tooltip rewrite expected one requestHTML(thisID) signature on {route}, "
            f"found {signature_count}"
        )
    matches = list(_RETIRED_ARMORY_REQUESTHTML_RE.finditer(text))
    if len(matches) != 1:
        raise PagesExportError(
            f"retired Armory tooltip rewrite expected one requestHTML(thisID) function on {route}, "
            f"found {len(matches)}"
        )
    match = matches[0]
    block = match.group(0)
    if _RETIRED_ARMORY_TOOLTIP_MESSAGE in block and "showTip(" in block:
        return text, False
    missing = [guard for guard in _RETIRED_ARMORY_REQUESTHTML_GUARDS if guard not in block]
    if missing:
        raise PagesExportError(
            f"retired Armory tooltip source signature changed on {route}; missing guards: {', '.join(missing)}"
        )
    newline = "\r\n" if "\r\n" in block else "\n"
    replacement = (
        f"function requestHTML(thisID){newline}"
        f"{{{newline}"
        f"\tshowTip('{_RETIRED_ARMORY_TOOLTIP_MESSAGE}');{newline}"
        "}"
    )
    return text[: match.start()] + replacement + text[match.end() :], True


_PVP_FLASH_ROUTE = "/pvp/flash-rewards/"
_PVP_SUBNAV_MARKER = "<!---Subnav----->"
_PVP_INTRO_OBJECT_RE = re.compile(
    r"<object\b(?=[^>]*\bid\s*=\s*(?:\"intro\"|'intro'|intro)(?=\s|/?>))[^>]*>.*?</object\s*>",
    re.I | re.S,
)
_PVP_SOURCE_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.I | re.S)


def rewrite_pvp_mini_site(
    text: str,
    *,
    route: str,
    base_path: str,
) -> tuple[str, bool]:
    """Derive a readable static panel for the captured 2007 PvP mini-site.

    The source route is an exact, known Flash mini-site page.  Its navigation
    and related-link blocks are generated by obsolete scripts, while the
    central panel is an ``intro.swf`` object.  Replace only when the complete
    source signature is present; an incomplete or unrelated page is returned
    byte-for-byte unchanged so a future capture cannot be blanked accidentally.
    """

    if route != _PVP_FLASH_ROUTE:
        return text, False

    marker_start = text.find(_PVP_SUBNAV_MARKER)
    if marker_start < 0:
        return text, False
    marker_end = marker_start + len(_PVP_SUBNAV_MARKER)
    center_match = re.search(r"<center\b[^>]*>", text[marker_end:], re.I)
    if center_match is None:
        return text, False
    center_start = marker_end + center_match.start()

    object_matches = [match for match in _PVP_INTRO_OBJECT_RE.finditer(text) if match.start() >= center_start]
    if len(object_matches) != 1:
        return text, False
    intro_object = object_matches[0]
    object_text = intro_object.group(0)
    if not re.search(r"<embed\b", object_text, re.I):
        return text, False
    if not re.search(r"intro\.swf", object_text, re.I):
        return text, False

    # These signatures identify the preserved static frame around the Flash
    # object.  They keep the transform route-specific if a future source only
    # happens to reuse the old marker or object id.
    required_signatures = (
        "World of Warcraft PvP Mini Site",
        "ss-border-top-bg.gif",
        "ss-border-left.gif",
    )
    if any(signature.casefold() not in text.casefold() for signature in required_signatures):
        return text, False
    script_open_count = len(re.findall(r"<script\b", text, re.I))
    script_close_count = len(re.findall(r"</script\s*>", text, re.I))
    if script_open_count == 0 or script_open_count != script_close_count:
        return text, False

    prefix = base_path if base_path.startswith("/") else "/" + base_path
    if not prefix.endswith("/"):
        prefix += "/"
    home_href = html.escape(prefix, quote=True)
    guide_href = html.escape(prefix + "info/index.html", quote=True)
    navigation = (
        '\n<nav class="offline-pvp-mini-nav" aria-label="Archive navigation" '
        'style="margin:12px auto; padding:8px 12px; text-align:center; '
        'background:#111; border:1px solid #8a6a21; color:#fff; font:14px Arial,sans-serif;">'
        f'<a href="{home_href}" style="color:#e9c46a;">Archive home</a>'
        '<span aria-hidden="true"> | </span>'
        f'<a href="{guide_href}" style="color:#e9c46a;">Game Guide</a>'
        "</nav>\n"
    )
    static_panel = (
        '\n<section class="offline-pvp-mini-panel" data-archive-flash-unavailable="true" '
        'aria-labelledby="offline-pvp-mini-title" '
        'style="box-sizing:border-box; min-height:220px; margin:24px auto; padding:36px 28px; '
        'max-width:900px; background:#111; border:2px solid #c9a44a; color:#fff; '
        'font:16px Arial,sans-serif; text-align:center;">'
        '<h2 id="offline-pvp-mini-title" style="margin:0 0 18px; color:#e9c46a; '
        'font-size:28px;">2007 PvP Mini Site</h2>'
        '<p style="margin:0; line-height:1.6;">The original interactive panel depended on Flash; '
        '<code>intro.swf</code> has not been recovered.</p>'
        "</section>\n"
    )

    # Remove the obsolete sub-navigation block through the next center tag,
    # retaining that center tag and everything that follows as the static
    # frame.  Then replace only the confirmed intro object and its embed.
    derived = text[:marker_start] + navigation + text[center_start:]
    # Re-find the object after the bounded prefix replacement instead of
    # relying on arithmetic over the removed block's length.
    rewritten_object = next(
        (match for match in _PVP_INTRO_OBJECT_RE.finditer(derived) if match.start() >= derived.find("<center", marker_start)),
        None,
    )
    if rewritten_object is None:
        # This is defensive only; all guards above matched the same source.
        return text, False
    derived = derived[:rewritten_object.start()] + static_panel + derived[rewritten_object.end():]
    # The old page's remaining scripts generate the related mail links and
    # depend on the deleted menu globals.  Runtime injection happens later in
    # the exporter, so remove only these source script elements now.
    derived = _PVP_SOURCE_SCRIPT_RE.sub("", derived)
    if re.search(r"mailto:", derived, re.I):
        return text, False
    return derived, True


_NAVTREE_COMMUNITY_PARENT_RE = re.compile(
    r'(?m)^(?P<prefix>\s*Menu1_6\s*=\s*new\s+Array\([^\r\n]*?,\s*["\']/community/["\']\s*,\s*["\']{2}\s*,\s*)'
    r'(?P<count>10|11)(?P<suffix>\s*,)'
)
_NAVTREE_FAN_SITES_RE = re.compile(
    r'(?m)^(?P<indent>\s*)Menu1_6_10(?P<rest>\s*=\s*new\s+Array\(\s*bulletImg\s*\+\s*["\']Fan Sites["\']\s*\+\s*underLine\s*,)'
)
_CONTEST_NAVTREE_MARKER = "offline-contest-nav-fallback-v1"
_CONTEST_NAVTREE_TREE_RE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)tree\s*\(\s*result\s*\)\s*;[ \t]*$"
)


def rewrite_navtree_community_ids(text: str) -> tuple[str, bool]:
    """Expose both Community fan links in the derived navtree script.

    The frozen source declares eleven Community children but uses
    ``Menu1_6_10`` for both Fan Wallpapers and Fan Sites.  Runtime JavaScript
    therefore overwrites the first value.  Keep the source bytes untouched and
    repair only the derived script: parent count 10 -> 11 and the later Fan
    Sites declaration 10 -> 11.  Already-derived text is accepted unchanged
    so an export pass is idempotent.
    """

    parent_matches = list(_NAVTREE_COMMUNITY_PARENT_RE.finditer(text))
    fan_sites_matches = list(_NAVTREE_FAN_SITES_RE.finditer(text))
    if len(parent_matches) > 1 or len(fan_sites_matches) > 1:
        raise PagesExportError("ambiguous Community navtree repair targets")
    changed = False
    if parent_matches:
        match = parent_matches[0]
        if match.group("count") == "10":
            start, end = match.span("count")
            text = text[:start] + "11" + text[end:]
            changed = True
    if fan_sites_matches:
        match = fan_sites_matches[0]
        start, end = match.span(0)
        prefix_end = match.start("rest")
        text = text[:start] + match.group("indent") + "Menu1_6_11" + text[prefix_end:]
        changed = True
    return text, changed


def rewrite_contest_navtree_fallback(text: str, *, base_path: str) -> tuple[str, bool]:
    """Repair the one archived contest page whose legacy URL is not its menu URL.

    ``findNode`` compares both a stripped label and the normalized URL.  The
    historical winners page is therefore left without ``result`` even though
    the loaded ``Menu1_6_4`` node is the correct Contests parent.  Inject one
    route- and node-guarded assignment immediately before the existing
    ``tree(result)`` call.  The source menu, ``pageId``, and ``findNode`` are
    untouched; repeated application is a no-op.
    """

    tree_matches = list(_CONTEST_NAVTREE_TREE_RE.finditer(text))
    if len(tree_matches) > 1:
        raise PagesExportError("ambiguous contest navtree tree(result) target")

    marker_count = text.count(_CONTEST_NAVTREE_MARKER)
    if marker_count > 1:
        raise PagesExportError("ambiguous contest navtree fallback markers")
    if marker_count == 1:
        return text, False
    if not tree_matches:
        return text, False

    expected_path = normalize_base_path(base_path) + "contests/05-05-25/winners.html"
    path_literal = json.dumps(expected_path, ensure_ascii=True)
    newline = "\r\n" if "\r\n" in text else "\n"
    indent = tree_matches[0].group("indent")
    block = newline.join(
        (
            f"{indent}/* {_CONTEST_NAVTREE_MARKER}: exact historical winners route only */",
            f'{indent}if (typeof result === "undefined" &&',
            f'{indent}    typeof document !== "undefined" && document.location &&',
            f'{indent}    document.location.pathname === {path_literal} &&',
            f'{indent}    typeof Menu1_6_4 !== "undefined" && Menu1_6_4 &&',
            f'{indent}    typeof stripId === "function" && stripId(Menu1_6_4[0]) === "Contests") {{',
            f'{indent}    result = "1_6_4";',
            f"{indent}}}",
            "",
        )
    )
    start = tree_matches[0].start()
    return text[:start] + block + text[start:], True


def ssotd_current_shot_number(text: str, actual_timestamp: str) -> int:
    """Derive the SSOTD index from this page's recorded UTC capture time."""

    start_match = re.search(r"\bstartDate\s*=\s*(\d+)\s*;", text)
    if not start_match:
        raise PagesExportError("SSOTD startDate is missing")
    start_date = int(start_match.group(1))
    if start_date != 12671:
        raise PagesExportError(f"unexpected SSOTD startDate: {start_date}")
    try:
        capture = datetime.strptime(str(actual_timestamp), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise PagesExportError(f"invalid SSOTD actual capture timestamp: {actual_timestamp!r}") from exc
    return int(capture.timestamp() // 86400) - start_date


_SSOTD_HEAD_CLOCK_RE = re.compile(
    r"(?ms)^(?P<indent>[ \t]*)function\s+checkRequestHeader\s*\(\s*\)\s*\{.*?"
    r"^[ \t]*xmlTimeVerification\.send\s*\(\s*null\s*\)\s*;[ \t]*\r?$"
)


def rewrite_ssotd_clock(text: str, *, actual_timestamp: str) -> tuple[str, bool, int]:
    """Replace only SSOTD's live HEAD clock with its recorded capture clock.

    The original ``addshots`` call remains in place immediately after the
    derived number, so gallery pagination and hash deep links continue to use
    the historical JavaScript unchanged.
    """

    shot_number = ssotd_current_shot_number(text, actual_timestamp)
    match = _SSOTD_HEAD_CLOCK_RE.search(text)
    if not match:
        if "xmlTimeVerification" not in text and re.search(r"\bcurrentShotNumber\s*=\s*\d+", text):
            return text, False, shot_number
        raise PagesExportError("SSOTD HEAD clock block is missing or ambiguous")
    newline = "\r\n" if "\r\n" in text else "\n"
    replacement = (
        f"{match.group('indent')}currentShotNumber = {shot_number};{newline}"
        f"{match.group('indent')}addshots(\"/downloads/ssotd/images/screens\",\"ss\",currentShotNumber);"
    )
    rewritten = text[: match.start()] + replacement + text[match.end() :]
    if "xmlTimeVerification" in rewritten or re.search(r"\.open\s*\(\s*[\"']HEAD", rewritten, re.I):
        raise PagesExportError("SSOTD derived page still contains a live HEAD clock")
    return rewritten, True, shot_number


_SSOTD_THUMB_ASSIGNMENT_RE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)thumbnail\s*=\s*shotList\[n\]\.replace\(\s*[\"']\.jpg[\"']\s*,\s*[\"']-thumb\.jpg[\"']\s*\)\s*;?\s*$",
)


def ssotd_thumbnail_fallbacks(
    route_to_static: dict[str, str],
    *,
    base_path: str,
) -> dict[str, str]:
    """Return full-image static URLs whose verified thumbnail is absent."""

    fallbacks: dict[str, str] = {}
    for route, target in sorted(route_to_static.items()):
        if not re.fullmatch(r"/downloads/ssotd/images/screens/ss\d+\.jpg", route):
            continue
        thumb_route = route[:-4] + "-thumb.jpg"
        if thumb_route not in route_to_static:
            full_static = target if target.startswith(base_path) else static_url(base_path, route.lstrip("/"))
            fallbacks[full_static] = full_static
    return fallbacks


def rewrite_ssotd_thumbnail_fallback(
    text: str,
    *,
    route_to_static: dict[str, str],
    base_path: str,
) -> tuple[str, bool, dict[str, str]]:
    """Use a verified full image only when its SSOTD thumbnail is absent."""

    fallbacks = ssotd_thumbnail_fallbacks(route_to_static, base_path=base_path)
    marker = "__WOW_SSOTD_THUMB_FALLBACK"
    if marker in text:
        return text, False, fallbacks
    if not fallbacks:
        return text, False, fallbacks
    match = _SSOTD_THUMB_ASSIGNMENT_RE.search(text)
    if not match:
        raise PagesExportError("SSOTD thumbnail assignment is missing or has an unexpected shape")
    indent = match.group("indent")
    mapping = json.dumps(fallbacks, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    declaration = f"var {marker} = {mapping};"
    replacement = (
        f"{indent}{declaration}\n"
        f"{indent}thumbnail = {marker}[shotList[n]] || shotList[n].replace(\".jpg\",\"-thumb.jpg\");"
    )
    rewritten = text[: match.start()] + replacement + text[match.end() :]
    return rewritten, True, fallbacks


def rewrite_iframe_fallbacks(text: str, *, base_url: str, localizer: PagesLocalizer, recorder: Any) -> str:
    """Localize archival iframe fallback markup even when Python treats it as raw text."""

    class FallbackParser(mirror.LocalizingHTMLParser):
        CDATA_CONTENT_ELEMENTS = ("script", "style")

    def replace(match: re.Match[str]) -> str:
        parser = FallbackParser(base_url=base_url, localizer=localizer, recorder=recorder, marker="")
        try:
            parser.feed(match.group(2))
            parser.close()
        except Exception as exc:
            raise PagesExportError(f"iframe fallback localization failed for {base_url}") from exc
        return match.group(1) + parser.output() + match.group(3)

    return re.sub(r"(<iframe\b[^>]*>)(.*?)(</iframe\s*>)", replace, text, flags=re.I | re.S)


def rewrite_compat_script(text: str) -> str:
    """Make the compatibility search's exact-topic jump synchronous on Pages.

    The injected Pages runtime is loaded before the frozen compatibility
    support script.  Calling its route mapper here avoids the asynchronous
    ``topicsArray`` repair race that otherwise briefly navigates to the old
    ``.xml`` URL and lets Pages return 404.
    """

    rewritten, count = re.subn(
        r"window\.location\.href\s*=\s*exactTopic\s*;",
        "window.location.href = window.__WOWPages.mapHref(exactTopic);",
        text,
        count=1,
    )
    return rewritten if count else text


def rewrite_cascade_script(text: str) -> str:
    """Map the encyclopedia avatar background before assigning it.

    Chrome does not expose ``backgroundImage`` consistently on
    ``CSSStyleDeclaration.prototype``.  The historical cascade expression
    also receives an absolute topic link after Pages rewriting.  Reduce it
    to the final basename, construct the original relative icon path, and
    pass the complete CSS value through the runtime's synchronous mapper.
    """

    old = (
        'document.getElementById("avatarImageContainer").style.backgroundImage = '
        '"url(images/icons/"+topicsArray[topicsArray[document.title].parentString].linkString.'
        'split(".xml")[0]+".jpg)";'
    )
    new = (
        'document.getElementById("avatarImageContainer").style.backgroundImage = '
        'window.__WOWPages.mapCssImages("url(images/icons/" + '
        'String(topicsArray[topicsArray[document.title].parentString].linkString).'
        'split("/").pop().split(".xml")[0] + ".jpg)");'
    )
    return text.replace(old, new)


def escape_xml_bare_ampersands(text: str) -> str:
    """Make rewritten XML/XSL query strings well-formed without double-escaping.

    The generic mirror localizer returns URL query separators as ordinary
    ``&`` characters.  They are valid in HTML but must be ``&amp;`` in the
    four preserved XML feeds and XSL attributes.  Existing named/numeric
    entities are left intact.
    """

    return _XML_BARE_AMP_RE.sub("&amp;", text)


def normalize_html_charset(text: str) -> str:
    def replace_meta(match: re.Match[str]) -> str:
        tag = match.group(0)
        if not re.search(r"charset\s*=|charset\s*['\"]?\s*", tag, re.I):
            return tag
        tag = re.sub(r"(charset\s*=\s*['\"]?)[^\s;>'\"]+", r"\1utf-8", tag, flags=re.I)
        return tag

    text = re.sub(r"<meta\b[^>]*>", replace_meta, text, flags=re.I)
    head = re.search(r"<head\b[^>]*>", text, flags=re.I)
    if head and not re.search(r"<meta\b[^>]*charset", text[: text.lower().find("</head>")] if "</head>" in text.lower() else text, re.I):
        text = text[: head.end()] + '\n<meta charset="utf-8">' + text[head.end() :]
    return text


def normalize_html_prolog(text: str) -> str:
    """Remove BOMs stranded before the document's real HTML prolog only."""

    document_start = re.search(
        r"<!doctype\b|<html\b|<head\b", text, flags=re.I
    )
    if document_start is None:
        return text
    prolog = text[: document_start.start()]
    if "\ufeff" not in prolog:
        return text
    return prolog.replace("\ufeff", "") + text[document_start.start() :]


def source16_main_page_reference(record: dict[str, Any]) -> dict[str, Any] | None:
    """Keep accepted original-entity metadata alongside the derived page hash."""

    if record.get("role") != "source16_main_page":
        return None
    url = str(record.get("source_base_url") or "")
    parsed = urllib.parse.urlsplit(url)
    try:
        valid_origin = (
            parsed.scheme in {"http", "https"}
            and parsed.hostname == "www.worldofwarcraft.com"
            and parsed.port in {None, 80 if parsed.scheme == "http" else 443}
            and parsed.username is None and parsed.password is None
            and not parsed.query and not parsed.fragment
            and parsed.path.startswith("/") and ";jsessionid" not in url.casefold()
        )
    except ValueError:
        valid_origin = False
    timestamp = str(record.get("actual_timestamp") or "")
    digest = str(record.get("source_sha256") or "")
    length = record.get("source_length")
    arc = record.get("source_arc")
    if not valid_origin or not re.fullmatch(r"\d{14}", timestamp):
        raise PagesExportError("invalid Source16 original URL or capture date")
    try:
        datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    except ValueError as exc:
        raise PagesExportError("invalid Source16 capture date") from exc
    if timestamp > "20080512210044" or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise PagesExportError("Source16 capture or original digest outside accepted scope")
    if type(length) is not int or length <= 0 or not isinstance(arc, dict):
        raise PagesExportError("invalid Source16 original length or ARC metadata")
    filename = str(arc.get("filename") or "")
    if (
        not filename.startswith("crawl-") or not filename.endswith(".arc.gz")
        or "\\" in filename or ".." in filename.split("/")
        or urllib.parse.urlsplit(filename).query
        or type(arc.get("offset")) is not int or arc["offset"] < 0
        or type(arc.get("length")) is not int or arc["length"] <= 0
        or not re.fullmatch(r"[0-9a-f]{64}", str(arc.get("compressed_sha256") or ""))
    ):
        raise PagesExportError("invalid Source16 ARC coordinates")
    return {
        "source_kind": "commoncrawl_arc", "collection": "CC-MAIN-2008-2009",
        "original_url": url, "actual_capture_timestamp": timestamp,
        "sha256": digest, "length": length,
        "source_arc": {key: arc[key] for key in ("filename", "offset", "length", "compressed_sha256")},
    }


def annotate_source16_main_page(text: str, reference: dict[str, Any] | None) -> str:
    if reference is None:
        return text
    parser = _MarkupTokenParser(text)
    parser.feed(text)
    parser.close()
    body = next((t for t in parser.tokens if t.kind == "start" and t.name == "body"), None)
    captured = datetime.strptime(reference["actual_capture_timestamp"], "%Y%m%d%H%M%S")
    note = (
        '<aside id="__offline-source16-note" role="note" '
        'style="background:#eee4ca;color:#302618;padding:6px 10px;font:12px Arial,sans-serif">'
        f'Historical page · Common Crawl capture: {captured:%Y-%m-%d %H:%M:%S} UTC'
        '</aside>'
    )
    if body is None:
        raise PagesExportError("derived Source16 page has no parsed body")
    return text[:body.end] + "\n" + note + text[body.end:]


def annotate_related_talent_icons(text: str, *, route: str, notice_html: str) -> tuple[str, bool]:
    """Label only the nine preserved calculators that use related-source icons."""

    allowed = {f"/info/classes/{name}/talents.html" for name in related_talent_icons.ALLOWED_CLASSES}
    if route not in allowed:
        return text, False
    parser = _MarkupTokenParser(text)
    parser.feed(text)
    parser.close()
    body = next((token for token in parser.tokens if token.kind == "start" and token.name == "body"), None)
    if body is None:
        raise PagesExportError("talent calculator has no parsed body for its source notice")
    note = (
        '<aside id="__offline-related-talent-icons" role="note" '
        'style="background:#eee4ca;color:#302618;padding:6px 10px;font:12px Arial,sans-serif">'
        + notice_html + '</aside>'
    )
    return text[:body.end] + "\n" + note + text[body.end:], True


def inject_html_runtime(text: str, *, base_path: str, source_sha: str) -> str:
    def first_real_start_tag(value: str, name: str) -> _MarkupToken | None:
        """Return the first parsed start tag, excluding script/raw-text strings."""

        parser = _MarkupTokenParser(value)
        try:
            parser.feed(value)
            parser.close()
        except Exception as exc:
            raise PagesExportError("HTML tokenization failed during runtime injection") from exc
        return next(
            (token for token in parser.tokens if token.kind == "start" and token.name == name),
            None,
        )

    insertion = (
        f'\n<meta http-equiv="Content-Security-Policy" content="{html.escape(PAGES_CSP, quote=True)}">'
        f'\n<script src="{base_path}__offline/pages_runtime.js"></script>\n'
    )
    if not re.search(r"pages_runtime\.js", text, re.I):
        head = first_real_start_tag(text, "head")
        if head:
            text = text[: head.end] + insertion + text[head.end :]
        else:
            text = "<!doctype html><html><head>" + insertion + "</head><body>" + text + "</body></html>"
    banner = (
        '<div id="__offline-pages-banner" style="background:#241b0b;color:#f7e7b0;'
        'font:12px/1.4 Arial,sans-serif;padding:6px 10px;text-align:center;position:relative;z-index:2147483647">'
        "Unofficial historical educational preservation (not affiliated with Blizzard) • "
        "Archive reconstruction based on 2008-05-12 • "
        "no user data collection</div>"
    )
    if "__offline-pages-banner" not in text:
        # Reparse after head insertion because the source offsets have shifted.
        body = first_real_start_tag(text, "body")
        if body:
            text = text[: body.end] + "\n" + banner + text[body.end :]
        else:
            text = banner + text
    if source_sha and "offline derived from source SHA-256" not in text:
        text = "<!-- offline Pages derived from source SHA-256 " + source_sha + " -->\n" + text
    return text


@dataclass(frozen=True)
class _MarkupToken:
    """A source-positioned HTML token used by the derived form pass.

    ``HTMLParser`` gives us reliable tag boundaries even for the malformed
    table/form nesting found in the historical pages.  The output pass only
    replaces the tokens that carry submit semantics; all other source slices
    remain byte-for-byte equal to the already localized HTML.
    """

    kind: str
    name: str
    start: int
    end: int
    raw: str
    attrs: tuple[tuple[str, str | None], ...] = ()
    self_closing: bool = False


class _MarkupTokenParser(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.tokens: list[_MarkupToken] = []
        self._line_starts = [0]
        self._line_starts.extend(match.end() for match in re.finditer("\n", text))

    def _offset(self) -> int:
        line, column = self.getpos()
        return self._line_starts[line - 1] + column

    def _start_token(self, tag: str, attrs: list[tuple[str, str | None]], *, self_closing: bool) -> None:
        start = self._offset()
        raw = self.get_starttag_text() or "<" + tag + ">"
        self.tokens.append(_MarkupToken("start", tag.casefold(), start, start + len(raw), raw, tuple(attrs), self_closing))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start_token(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start_token(tag, attrs, self_closing=True)

    def handle_endtag(self, tag: str) -> None:
        start = self._offset()
        end = self.text.find(">", start)
        if end < 0:
            end = len(self.text)
        else:
            end += 1
        self.tokens.append(_MarkupToken("end", tag.casefold(), start, end, self.text[start:end]))


_HTML_ATTRIBUTE_SPAN_RE = re.compile(
    r"\s+(?P<name>[^\s\"'<>/=]+)"
    r"(?:\s*=\s*(?P<value>\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+))?",
    re.I,
)


def _is_historical_flash_cab_url(value: str) -> bool:
    """Recognize only the old Macromedia/Adobe Flash CAB install URL."""

    try:
        parsed = urllib.parse.urlsplit(html.unescape(value).strip())
    except ValueError:
        return False
    if parsed.scheme.casefold() not in {"http", "https"}:
        return False
    hostname = (parsed.hostname or "").casefold().rstrip(".")
    if not (
        hostname == "macromedia.com"
        or hostname.endswith(".macromedia.com")
        or hostname == "adobe.com"
        or hostname.endswith(".adobe.com")
    ):
        return False
    path = parsed.path.casefold()
    return bool(re.search(r"/shockwave/cabs/flash/[^/]+\.cab$", path))


def rename_flash_codebase_metadata(text: str, recorder: mirror.ReferenceRecorder | None = None) -> str:
    """Rename real object Flash installer attributes in the derived HTML.

    ``HTMLParser`` supplies source positions for actual start tags, so script
    strings, comments, visible prose, CSS, and ordinary object ``codebase``
    values never enter the attribute rewrite.  The matched URL bytes stay
    unchanged as historical metadata.
    """

    parser = _MarkupTokenParser(text)
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        raise PagesExportError("Flash codebase tokenization failed") from exc

    replacements: list[tuple[int, int, str, str]] = []
    for token in parser.tokens:
        if token.kind != "start" or token.name != "object":
            continue
        codebase_values = [value for name, value in token.attrs if name.casefold() == "codebase" and value is not None]
        if not codebase_values:
            continue
        header = re.match(r"<\s*object\b", token.raw, re.I)
        if header is None:
            continue
        # Consume every complete attribute, including quoted values.  Looking
        # only for whitespace followed by `codebase` could match prose inside
        # another attribute's value and leave the real installer active.
        for match in _HTML_ATTRIBUTE_SPAN_RE.finditer(token.raw, header.end()):
            if match.group("name").casefold() != "codebase":
                continue
            raw_value = match.group("value")
            if raw_value is None:
                continue
            unquoted = raw_value[1:-1] if len(raw_value) >= 2 and raw_value[0] in "\"'" and raw_value[-1] == raw_value[0] else raw_value
            if not _is_historical_flash_cab_url(unquoted):
                continue
            name_start = token.start + match.start("name")
            name_end = token.start + match.end("name")
            replacements.append((name_start, name_end, "data-archive-codebase", html.unescape(unquoted)))

    if not replacements:
        return text
    for start, end, replacement, value in reversed(replacements):
        text = text[:start] + replacement + text[end:]
        if recorder is not None:
            recorder.add(
                value,
                value,
                "flash_codebase_renamed",
                value,
                "html_object_codebase",
                "preserved historical Flash CAB installer metadata",
            )
    return text


_FORM_CONTROL_TAGS = {"input", "select", "textarea", "button"}
_VOID_HTML_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr",
}
_FORM_ALLOWED_IDS = {"topsearch", "formdropdownlang", "searchform1", "searchform2"}
_LOCAL_BROWSER_FORM_ROUTES = {
    "/info/basics/factions/arathi/index.html",
    "/info/basics/factions/argent/index.html",
    "/info/basics/factions/badgesofjustice/badges-of-justice2.html",
    "/info/basics/factions/warsong/index.html",
    "/pvp/rewards-arena-class-armor.html",
    "/pvp/rewards-class-armor.html",
    "/pvp/rewards-vindicators-armor.html",
    "/pvp/rewards-weapons.html",
}
_LOCAL_BROWSER_BRACKET_HANDLER_RE = re.compile(
    r"\s*levelBracket\s*=\s*this\.form\.bracketSelector\.options\[this\.form\.bracketSelector\.selectedIndex\]\.value\s*;\s*reloadTable\s*\(\s*\)\s*;?\s*",
    re.I | re.S,
)
_LOCAL_BROWSER_ARGENT_HANDLER_RE = re.compile(
    r"\s*(?:changeQuestForRealThisTime|changeQuest|changeProfession)\s*\(\s*this\.value\s*\)\s*;?\s*",
    re.I,
)
_SENSITIVE_FIELD_RE = re.compile(
    r"(?:password|passwd|passcode|ssn|social[ _-]*security|credit[ _-]*card|card[ _-]*number|cvv|cvc|security[ _-]*code|billing|account[ _-]*number)",
    re.I,
)
_BUSINESS_EVENT_RE = re.compile(
    r"(?:directsubmit|undisable|commentarticle|confirmredeem|validation|setanon|nameopt|\.submit\s*\(|\bsubmit\s*\()",
    re.I,
)
_STATIC_FORM_NOTICE = "Historical form — display only. Submissions are unavailable."


def _attrs_map(attrs: tuple[tuple[str, str | None], ...] | list[tuple[str, str | None]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, value in attrs:
        if value is not None:
            result.setdefault(name.casefold(), value)
    return result


_ATTUNEMENT_MASK_ROUTE = "/bcattunement/index.html"
_ATTUNEMENT_MASK_PIXEL_REQUESTED = "https://www.worldofwarcraft.com/bcattunement/images/pixel.gif"
_ATTUNEMENT_MASK_SOURCE = "/shared/wow-com/includes/images/pixel.gif"


def _attunement_mask_pixel_placeholder(value: str, *, base_path: str) -> bool:
    """Recognize only the derived missing-image value for the attunement mask."""

    try:
        parsed = urllib.parse.urlsplit(html.unescape(value).strip())
        query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    except ValueError:
        return False
    expected_marker = f"{base_path}__offline/missing-image.svg"
    if parsed.scheme or parsed.netloc or parsed.path != expected_marker:
        return False
    requested = query.get("requested", [])
    source = query.get("source", [])
    return requested == [_ATTUNEMENT_MASK_PIXEL_REQUESTED] and source == ["https://www.worldofwarcraft.com/bcattunement/"]


def rewrite_attunement_mask_pixel(text: str, *, route: str, base_path: str) -> tuple[str, bool]:
    """Mask three visible attunement placeholders with the collected pixel.

    The old page uses a large missing-image SVG as the ``#mapPixel`` image.  It
    sits above the restored chart and path controls, so the opaque placeholder
    hides the useful map.  Two visible CSS masks use the same placeholder.  This
    narrow source-position rewrite touches only the exact route, the real
    ``img#mapPixel`` token, and the ``background:`` declarations inside the
    actual ``.coverDivStyle1``/``.coverDivStyle2`` style rules.  The legacy
    ``_background:`` declaration and every other pixel reference remain
    byte-for-byte unchanged.
    """

    if route != _ATTUNEMENT_MASK_ROUTE:
        return text, False
    parser = _MarkupTokenParser(text)
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        raise PagesExportError("attunement mask pixel tokenization failed") from exc

    replacements: list[tuple[int, int, str]] = []
    map_pixel_replacements = 0
    css_replacements: dict[str, int] = {"coverDivStyle1": 0, "coverDivStyle2": 0}
    target = base_path + _ATTUNEMENT_MASK_SOURCE.lstrip("/")
    for token in parser.tokens:
        if token.kind == "start" and token.name == "img":
            attrs = _attrs_map(token.attrs)
            if attrs.get("id", "").casefold() != "mappixel":
                continue
            src = attrs.get("src", "")
            if not _attunement_mask_pixel_placeholder(src, base_path=base_path):
                continue
            matches = [
                match
                for match in _HTML_ATTRIBUTE_SPAN_RE.finditer(token.raw)
                if match.group("name").casefold() == "src" and match.group("value") is not None
            ]
            if len(matches) != 1:
                raise PagesExportError("attunement mapPixel src attribute is not uniquely addressable")
            match = matches[0]
            raw_value = match.group("value") or ""
            if len(raw_value) >= 2 and raw_value[0] in "\"'" and raw_value[-1] == raw_value[0]:
                replacement = raw_value[0] + target + raw_value[-1]
            else:
                replacement = target
            replacements.append((token.start + match.start("value"), token.start + match.end("value"), replacement))
            map_pixel_replacements += 1

        if token.kind != "start" or token.name != "style":
            continue
        end_token = next(
            (
                candidate
                for candidate in parser.tokens
                if candidate.kind == "end" and candidate.name == "style" and candidate.start >= token.end
            ),
            None,
        )
        if end_token is None:
            raise PagesExportError("attunement style token has no closing tag")
        style_text = text[token.end : end_token.start]
        for class_name in css_replacements:
            class_pattern = re.compile(
                rf"(?P<selector>\.{class_name}\b[^{{]*\{{)(?P<body>[^{{}}]*)(?P<close>\}})",
                flags=re.I | re.S,
            )
            for class_match in class_pattern.finditer(style_text):
                body = class_match.group("body")
                url_matches = list(
                    re.finditer(
                        r"(?<![\w-])background\s*:\s*url\(\s*(?P<quote>[\"']?)(?P<value>[^)\"']+)(?P=quote)\s*\)",
                        body,
                        flags=re.I,
                    )
                )
                for url_match in url_matches:
                    value = url_match.group("value")
                    if not _attunement_mask_pixel_placeholder(value, base_path=base_path):
                        continue
                    css_replacements[class_name] += 1
                    replacements.append(
                        (
                            token.end + class_match.start("body") + url_match.start("value"),
                            token.end + class_match.start("body") + url_match.end("value"),
                            target,
                        )
                    )
    if map_pixel_replacements > 1:
        raise PagesExportError("attunement route contains multiple matching mapPixel placeholders")
    if any(count > 1 for count in css_replacements.values()):
        raise PagesExportError("attunement route contains duplicate visible CSS mask placeholders")
    if not replacements:
        return text, False
    for start, end, replacement in sorted(replacements, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text, True


def _form_identity(attrs: tuple[tuple[str, str | None], ...]) -> set[str]:
    values: set[str] = set()
    for key in ("id", "name", "class"):
        value = _attrs_map(attrs).get(key, "")
        for part in re.split(r"[\s,]+", value):
            if part:
                folded = part.casefold()
                values.add(folded)
                values.add(re.sub(r"[^a-z0-9]", "", folded))
    return values


def _form_kind(attrs: tuple[tuple[str, str | None], ...], route: str) -> str:
    """Return ``allowed``, ``layout`` or ``business`` for one form token."""

    values = _attrs_map(attrs)
    identity = _form_identity(attrs)
    if identity & _FORM_ALLOWED_IDS:
        return "allowed"
    route_lower = route.casefold().rstrip("/")
    if route_lower == "/toplist" or route_lower.startswith("/toplist/"):
        # Toplist has a browser-side filter shell whose form deliberately
        # submits false.  It is a local browsing interaction, not a service
        # submission.  Keep it even when the frozen markup has no id.
        if "toplistfilters" in identity or values.get("onsubmit", "").strip().casefold() in {"return false", "return false;"}:
            return "allowed"
    if route_lower == "/contests/05-12-giveaway/contest.html" and "form3" in identity:
        # The historical form3 wraps only the date-header table and is left
        # as a non-form layout container.  It has no controls or submit path.
        return "layout"
    return "business"


def _is_local_browser_form(
    tokens: list[_MarkupToken],
    start_index: int,
    end_index: int | None,
    route: str,
) -> bool:
    """Recognize the small, source-confirmed family of local filter forms.

    These forms are anonymous in the frozen HTML, so identity-only allowlists
    cannot preserve them.  Require both the exact route family and the
    expected select body/handler; a random anonymous form or a POST form with
    a select remains business content.
    """

    route_lower = route.casefold().rstrip("/")
    if route_lower not in _LOCAL_BROWSER_FORM_ROUTES:
        return False
    form_attrs = _attrs_map(tokens[start_index].attrs)
    if any(name in form_attrs for name in ("action", "method", "enctype", "id", "name")):
        return False
    if any(name.casefold().startswith("on") for name, _ in tokens[start_index].attrs):
        return False
    limit = end_index if end_index is not None else len(tokens)
    controls = [
        token
        for token_index, token in enumerate(tokens)
        if start_index < token_index < limit
        and token.kind == "start"
        and token.name in _FORM_CONTROL_TAGS
    ]
    if not controls or any(token.name != "select" for token in controls):
        return False
    for token in controls:
        values = _attrs_map(token.attrs)
        onchange = values.get("onchange", "")
        if route_lower == "/info/basics/factions/argent/index.html":
            if not _LOCAL_BROWSER_ARGENT_HANDLER_RE.fullmatch(onchange):
                return False
        else:
            if values.get("name", "").casefold() != "bracketselector":
                return False
            if not _LOCAL_BROWSER_BRACKET_HANDLER_RE.fullmatch(onchange):
                return False
    return True


def _safe_render_attrs(
    tag: str,
    attrs: tuple[tuple[str, str | None], ...],
    *,
    drop_events: bool = False,
    drop_submit: bool = False,
    extra_class: str | None = None,
) -> str:
    kept: list[tuple[str, str | None]] = []
    seen: set[str] = set()
    drop_submit_names = {
        "action", "method", "enctype", "encoding", "target", "formenctype", "formmethod", "formtarget", "formaction",
        "accept-charset", "novalidate",
    }
    for name, value in attrs:
        lname = name.casefold()
        if lname in seen:
            continue
        if drop_events and lname.startswith("on"):
            continue
        if drop_submit and lname in drop_submit_names:
            continue
        if drop_submit and lname == "autocomplete":
            continue
        if drop_submit and lname == "form":
            continue
        if lname == "class" and extra_class:
            value = ((value or "").strip() + " " + extra_class).strip()
        kept.append((name, value))
        seen.add(lname)
    if extra_class and "class" not in seen:
        kept.append(("class", extra_class))
    rendered: list[str] = []
    for name, value in kept:
        rendered.append(name if value is None else f'{name}="{html.escape(value, quote=True)}"')
    return (" " + " ".join(rendered)) if rendered else ""


def _static_span(label: str, kind: str) -> str:
    return '<span class="offline-archive-control" data-offline-control="' + html.escape(kind, quote=True) + '">' + html.escape(label) + "</span>"


def _plain_visible_text(text: str) -> str:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<[^>]*>", " ", text, flags=re.S)
    return " ".join(html.unescape(text).split())


def _selected_option_text(text: str) -> str:
    options = list(re.finditer(r"<option\b(?P<attrs>[^>]*)>(?P<body>.*?)</option\s*>", text, re.I | re.S))
    if not options:
        return _plain_visible_text(text)
    selected = next((option for option in options if re.search(r"\bselected(?:\s*=|\s*$)", option.group("attrs"), re.I)), options[0])
    return _plain_visible_text(selected.group("body"))


def _sensitive_attrs(attrs: tuple[tuple[str, str | None], ...]) -> bool:
    values = _attrs_map(attrs)
    field_type = values.get("type", "text").casefold()
    return field_type == "password" or bool(_SENSITIVE_FIELD_RE.search(" ".join(values.get(key, "") for key in ("name", "id", "autocomplete", "aria-label"))))


def _static_control_replacement(token: _MarkupToken, text: str, end_token: _MarkupToken | None) -> str:
    values = _attrs_map(token.attrs)
    tag = token.name
    field_type = values.get("type", "text").casefold()
    sensitive = _sensitive_attrs(token.attrs)
    if tag == "input":
        if field_type == "hidden":
            return ""
        if field_type == "image":
            image_attrs: list[tuple[str, str | None]] = []
            for name, value in token.attrs:
                lname = name.casefold()
                if lname in {"src", "alt", "title", "width", "height", "class", "style", "border", "align", "hspace", "vspace"}:
                    image_attrs.append((name, value))
            return "<img" + _safe_render_attrs("img", tuple(image_attrs)) + " />"
        if field_type == "file":
            label = "File upload unavailable in archive"
        elif sensitive:
            label = "Unavailable"
        elif field_type in {"checkbox", "radio"}:
            label = "Selected" if "checked" in {name.casefold() for name, _ in token.attrs} else "Not selected"
        else:
            label = values.get("value", "") or values.get("placeholder", "") or "—"
        return _static_span(label, "input")
    inner = ""
    if end_token is not None:
        inner = text[token.end:end_token.start]
    if tag == "select":
        label = _selected_option_text(inner)
        return _static_span(label or "—", "select")
    if tag == "textarea":
        label = "Unavailable" if sensitive else (_plain_visible_text(inner) or "—")
        return _static_span(label, "textarea")
    if tag == "button":
        label = _plain_visible_text(inner) or values.get("value", "") or "—"
        return _static_span(label, "button")
    return _static_span("Field", tag)


def disable_sensitive_forms(text: str, route: str = "") -> str:
    """Render non-search forms as inert archive content.

    This is deliberately a token/position pass instead of a ``<form>...</form>``
    regular expression.  The preserved pages contain forms inside tables,
    nested form tags, controls with an external ``form=`` binding, and
    malformed/unclosed forms.  ``HTMLParser`` provides tag boundaries while
    the original localized text is retained for every untouched range.
    """

    parser = _MarkupTokenParser(text)
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        raise PagesExportError(f"form safety tokenization failed for {route or '<unknown-route>'}") from exc
    tokens = parser.tokens
    if not any(token.name == "form" and token.kind == "start" for token in tokens):
        return text

    form_kinds: dict[int, str] = {}
    form_ids: dict[str, str] = {}
    form_start_stack: list[int] = []
    form_end_for_start: dict[int, int] = {}
    form_start_for_end: dict[int, int] = {}
    for index, token in enumerate(tokens):
        if token.kind == "start" and token.name == "form":
            kind = _form_kind(token.attrs, route)
            form_kinds[index] = kind
            values = _attrs_map(token.attrs)
            for key in (values.get("id", ""), values.get("name", "")):
                if key:
                    form_ids[key.casefold()] = kind
            if not token.self_closing:
                form_start_stack.append(index)
        elif token.kind == "end" and token.name == "form":
            if form_start_stack:
                start_index = form_start_stack.pop()
                form_end_for_start[start_index] = index
                form_start_for_end[index] = start_index

    # Some preserved browsing filters use anonymous <form> wrappers.  Keep
    # only the source-confirmed family whose exact route and select handler
    # prove that it is a local view switch; unknown anonymous forms stay
    # business forms and are rendered inert below.
    for start_index, kind in list(form_kinds.items()):
        if kind == "business" and _is_local_browser_form(tokens, start_index, form_end_for_start.get(start_index), route):
            form_kinds[start_index] = "allowed"

    # ``form3`` is a known date-header layout wrapper, but keep the decision
    # evidence-based: if a future capture places any control inside it (or
    # binds a control to it from outside), treat it as a business form.
    for start_index, kind in list(form_kinds.items()):
        if kind != "layout":
            continue
        form_token = tokens[start_index]
        end_index = form_end_for_start.get(start_index)
        limit = end_index if end_index is not None else len(tokens)
        has_control = any(
            token.kind == "start"
            and token.name in _FORM_CONTROL_TAGS
            and (
                start_index < token_index < limit
                or _attrs_map(token.attrs).get("form", "").casefold() in _form_identity(form_token.attrs)
            )
            for token_index, token in enumerate(tokens)
        )
        if has_control:
            form_kinds[start_index] = "business"

    # Rebuild bindings after the evidence-based form3 decision.
    form_ids.clear()
    for start_index, kind in form_kinds.items():
        values = _attrs_map(tokens[start_index].attrs)
        for key in (values.get("id", ""), values.get("name", "")):
            if key:
                form_ids[key.casefold()] = kind

    # Pair regular controls for whole-region replacements.  Void elements are
    # intentionally excluded; an explicit legacy </input> is handled below.
    tag_stack: list[tuple[str, int]] = []
    pair_end_for_start: dict[int, int] = {}
    for index, token in enumerate(tokens):
        if token.kind == "start":
            if not token.self_closing and token.name not in _VOID_HTML_TAGS:
                tag_stack.append((token.name, index))
        elif token.kind == "end":
            for stack_index in range(len(tag_stack) - 1, -1, -1):
                name, start_index = tag_stack[stack_index]
                if name == token.name:
                    pair_end_for_start[start_index] = index
                    del tag_stack[stack_index:]
                    break

    # A few old pages use </input>.  Pair only the immediately relevant
    # closing token so an unclosed input cannot swallow later controls.
    for index, token in enumerate(tokens):
        if token.kind != "start" or token.name != "input" or token.self_closing:
            continue
        for candidate in range(index + 1, len(tokens)):
            other = tokens[candidate]
            if other.kind == "start" and other.name == "input":
                break
            if other.kind == "end" and other.name == "input":
                pair_end_for_start[index] = candidate
                break

    # Determine the nearest business form for every token.  Layout-only
    # form3 is not pushed, so its unclosed tag cannot accidentally capture the
    # remainder of the page.  Explicit form= bindings always take precedence.
    active_forms: list[tuple[int, str]] = []
    owner_kind: dict[int, str | None] = {}
    for index, token in enumerate(tokens):
        if token.kind == "start" and token.name == "form":
            kind = form_kinds.get(index, "business")
            if kind != "layout":
                active_forms.append((index, kind))
        elif token.kind == "end" and token.name == "form":
            start_index = form_start_for_end.get(index)
            if start_index is not None:
                for stack_index in range(len(active_forms) - 1, -1, -1):
                    if active_forms[stack_index][0] == start_index:
                        del active_forms[stack_index:]
                        break
        if token.kind == "start" and token.name in _FORM_CONTROL_TAGS:
            values = _attrs_map(token.attrs)
            explicit_form = values.get("form", "").casefold()
            if explicit_form and explicit_form in form_ids:
                owner_kind[index] = form_ids[explicit_form]
            elif active_forms:
                owner_kind[index] = active_forms[-1][1]
            else:
                owner_kind[index] = None

    replacements: list[tuple[int, int, str]] = []
    covered_controls: list[tuple[int, int]] = []
    business_form_indices = {index for index, kind in form_kinds.items() if kind == "business"}
    layout_form_indices = {index for index, kind in form_kinds.items() if kind == "layout"}

    for index, token in enumerate(tokens):
        if token.kind == "start" and token.name == "form":
            kind = form_kinds.get(index, "business")
            if kind == "allowed":
                continue
            if kind == "layout":
                replacement = "<div" + _safe_render_attrs("div", token.attrs, drop_events=True, drop_submit=True, extra_class="offline-archive-layout") + ">"
            else:
                replacement = (
                    "<div"
                    + _safe_render_attrs("div", token.attrs, drop_events=True, drop_submit=True, extra_class="offline-archive-form offline-business-form")
                    + ' data-offline-form="static" data-offline-static-form="true">'
                    + '<p class="offline-archive-notice offline-form-notice">'
                    + _STATIC_FORM_NOTICE
                    + "</p>"
                )
            replacements.append((token.start, token.end, replacement))
        elif token.kind == "end" and token.name == "form":
            start_index = form_start_for_end.get(index)
            if start_index in business_form_indices or start_index in layout_form_indices:
                replacements.append((token.start, token.end, "</div>"))

    # Select/textarea/button regions are replaced as one range, so no option,
    # event or nested control survives inside the static span.
    for index, token in enumerate(tokens):
        if token.kind != "start" or token.name not in _FORM_CONTROL_TAGS:
            continue
        owner = owner_kind.get(index)
        values = _attrs_map(token.attrs)
        event_text = " ".join(value or "" for name, value in token.attrs if name.casefold().startswith("on"))
        if owner == "allowed":
            continue
        outside_business = owner != "business" and bool(_BUSINESS_EVENT_RE.search(event_text))
        suspicious_outside = owner != "business" and (
            _sensitive_attrs(token.attrs)
            or values.get("type", "").casefold() in {"password", "file", "hidden", "submit", "reset", "image"}
        )
        if owner != "business" and not outside_business and not suspicious_outside:
            continue
        end_index = pair_end_for_start.get(index)
        end_token = tokens[end_index] if end_index is not None else None
        end_offset = end_token.end if end_token is not None else token.end
        replacements.append((token.start, end_offset, _static_control_replacement(token, text, end_token)))
        covered_controls.append((token.start, end_offset))

    def is_covered(start: int, end: int) -> bool:
        return any(start >= covered_start and end <= covered_end for covered_start, covered_end in covered_controls)

    # Remove direct business event attributes from ordinary descendants that
    # remain visible in a staticized form.  Search/navigation forms are never
    # in this branch and retain their historical local behavior.
    active_business: list[int] = []
    for index, token in enumerate(tokens):
        if token.kind == "start" and token.name == "form":
            kind = form_kinds.get(index, "business")
            if kind == "business":
                active_business.append(index)
        elif token.kind == "end" and token.name == "form":
            start_index = form_start_for_end.get(index)
            if start_index is not None:
                for stack_index in range(len(active_business) - 1, -1, -1):
                    if active_business[stack_index] == start_index:
                        del active_business[stack_index:]
                        break
        if token.kind != "start" or not active_business or token.name == "form" or is_covered(token.start, token.end):
            continue
        event_text = " ".join(value or "" for name, value in token.attrs if name.casefold().startswith("on"))
        if not event_text and not any(name.casefold() in {"formaction", "formenctype", "formmethod", "formtarget"} for name, _ in token.attrs):
            continue
        replacements.append((token.start, token.end, "<" + token.name + _safe_render_attrs(token.name, token.attrs, drop_events=True, drop_submit=True) + (" />" if token.self_closing else ">")))

    if not replacements:
        return text
    replacements.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    output: list[str] = []
    cursor = 0
    for start, end, replacement in replacements:
        if start < cursor:
            continue
        output.append(text[cursor:start])
        output.append(replacement)
        cursor = end
    output.append(text[cursor:])
    return "".join(output)


def rewrite_wrath_thumbnails_script(text: str) -> str:
    """Harden Wrath thumbnail pagination without changing other expansions."""

    query_pattern = re.compile(
        r"var\s+query\s*=\s*window\.location\.search\.substring\(1\)\s*;"
        r"\s*var\s+vars\s*=\s*query\.split\(\"s=\"\)\s*;"
        r"\s*/\*.*?\*/\s*"
        r"var\s+queryCurrentPage\s*=\s*vars\[1\]\s*;\s*"
        r"var\s+queryTotalPages\s*;\s*"
        r"if\s*\(\s*!queryCurrentPage\s*\)\s*\{\s*"
        r"queryCurrentPage\s*=\s*1\s*;\s*queryTotalPages\s*=\s*1\s*;\s*\}\s*",
        re.I | re.S,
    )
    query_replacement = """var queryParams = new URLSearchParams(window.location.search);
var queryValues = queryParams.getAll(\"s\");
var queryCurrentPage = 1;
if (queryValues.length === 1 && /^[1-9][0-9]*$/.test(queryValues[0])) {
\tvar parsedPage = Number(queryValues[0]);
\tif (Number.isSafeInteger(parsedPage) && parsedPage >= 1)
\t\tqueryCurrentPage = parsedPage;
}
var queryTotalPages = 1;
"""
    text, query_count = query_pattern.subn(query_replacement, text, count=1)
    if query_count != 1:
        raise PagesExportError("Wrath thumbnails script query parser did not match the expected fragment")

    entry_pattern = re.compile(r"function\s+printPageNumbers\s*\(\s*\)\s*\{", re.I)
    entry_replacement = """function printPageNumbers() {
\tvar actualPages = Number(pages);
\tif (!Number.isSafeInteger(actualPages) || actualPages < 1)
\t\tactualPages = 1;
\tqueryTotalPages = actualPages;
\tif (!Number.isSafeInteger(queryCurrentPage) || queryCurrentPage < 1 || queryCurrentPage > actualPages)
\t\tqueryCurrentPage = 1;
\tcurrentPage = queryCurrentPage;
"""
    text, entry_count = entry_pattern.subn(entry_replacement, text, count=1)
    if entry_count != 1:
        raise PagesExportError("Wrath thumbnails script printPageNumbers entry did not match the expected fragment")

    previous_pattern = re.compile(r"var\s+calcPreviousPage\s*=\s*eval\(\s*queryCurrentPage\s*\)\s*-\s*1\s*;", re.I)
    text, previous_count = previous_pattern.subn("var calcPreviousPage = queryCurrentPage - 1;", text, count=1)
    next_pattern = re.compile(r"var\s+calcNextPage\s*=\s*eval\(\s*queryCurrentPage\s*\)\s*\+\s*1\s*;", re.I)
    text, next_count = next_pattern.subn("var calcNextPage = queryCurrentPage + 1;", text, count=1)
    if previous_count != 1 or next_count != 1:
        raise PagesExportError("Wrath thumbnails script page calculations did not match the expected eval fragments")
    return text


def rewrite_wrath_viewer_script(text: str) -> str:
    """Replace the unsafe Wrath viewer query fragment with a strict parser.

    The viewer's historical fragment used eval on everything after s=.
    Match that exact fragment once so a source drift or duplicate occurrence
    stops the export instead of receiving a guessed rewrite.
    """

    query_pattern = re.compile(
        r"(?:(?:var|let|const)\s+)?checkForSpecifiedShot\s*=\s*"
        r"window\.location\.href\.split\(\s*\x22s=\x22\s*\)\s*;\s*"
        r"(?:(?:var|let|const)\s+)?nowViewing\s*=\s*"
        r"\(\s*checkForSpecifiedShot\[1\]\s*\)\s*\?\s*"
        r"eval\(\s*checkForSpecifiedShot\[1\]\s*\)\s*:\s*0\s*;",
        re.I,
    )
    matches = list(query_pattern.finditer(text))
    if len(matches) != 1:
        raise PagesExportError(
            "Wrath viewer script query parser expected exactly one original fragment"
        )
    replacement = """checkForSpecifiedShot = new URLSearchParams(window.location.search).getAll("s");
nowViewing = 1;
if (checkForSpecifiedShot.length === 1 && /^[0-9]+$/.test(checkForSpecifiedShot[0])) {
	var parsedShot = Number(checkForSpecifiedShot[0]);
	if (Number.isSafeInteger(parsedShot) &&
		parsedShot >= 1 &&
		typeof shotList !== "undefined" &&
		parsedShot <= shotList.length)
		nowViewing = parsedShot;
}
"""
    return query_pattern.sub(replacement, text, count=1)


_WRATH_CARD_HIT_AREA_ROUTES = frozenset({
    "/wrath/artwork.xml",
    "/wrath/screenshots.xml",
})
_WRATH_CARD_HIT_AREA_MARKER = 'data-archive-derived="wrath-card-hit-area-v1"'
_WRATH_CARD_HIT_AREA_STYLE = """<style data-archive-derived="wrath-card-hit-area-v1">
/* Derived layout fallback only: local source CSS sets .ssborder to 243x193. */
.ssborder a {
    display: block;
    width: 243px;
    height: 193px;
}
.ssborder img[src*="missing-image.svg"][src*="ssborder1.png"] {
    visibility: hidden;
}
</style>"""


def rewrite_wrath_card_hit_area(text: str, *, route: str) -> tuple[str, bool]:
    """Restore the verified Wrath card hit area on the two gallery routes.

    This is a derived layout fallback, not an image recovery.  The narrow
    image selector hides only the shared decorative fallback when both source
    fragments are present; content-image placeholders and a real border image
    remain visible.
    """

    if route not in _WRATH_CARD_HIT_AREA_ROUTES:
        return text, False
    marker_count = text.count(_WRATH_CARD_HIT_AREA_MARKER)
    if marker_count > 1:
        raise PagesExportError("Wrath card hit-area style marker occurs more than once")
    if marker_count == 1:
        return text, False
    head_matches = list(re.finditer(r"</head\s*>", text, flags=re.I))
    if len(head_matches) != 1:
        raise PagesExportError("Wrath card hit-area style requires exactly one closing head tag")
    insertion = "\n" + _WRATH_CARD_HIT_AREA_STYLE + "\n"
    match = head_matches[0]
    return text[:match.start()] + insertion + text[match.start():], True


_NEWS_TOGGLE_ANCHOR_MARKER = 'data-archive-derived="news-toggle-anchor-v1"'
_NEWS_TOGGLE_STYLE_MARKER = 'data-archive-derived="news-toggle-anchor-style-v1"'
_NEWS_TOGGLE_ANCHOR_STYLE = f"""<style {_NEWS_TOGGLE_STYLE_MARKER}>
/* Derived pointer repair only: the matched historical news toggle anchor is 14x11. */
.news-toggle a[{_NEWS_TOGGLE_ANCHOR_MARKER}] {{
    display: block;
    width: 14px;
    height: 11px;
}}
</style>"""
_NEWS_TOGGLE_CALL_RE = re.compile(
    r"^\s*(?P<prefix>(?i:javascript)\s*:\s*)?toggleEntry\s*\(\s*"
    r"(?P<id_quote>['\"])(?P<entry_id>[A-Za-z0-9_-]+)(?P=id_quote)\s*,\s*"
    r"(?P<alt_quote>['\"])(?P<alt>[A-Za-z0-9_-]*)(?P=alt_quote)\s*\)\s*;?\s*$",
)


def _normalize_news_toggle_call(
    value: str | None,
    *,
    require_javascript_prefix: bool = False,
) -> tuple[str, str] | None:
    """Return the exact two simple toggle arguments without changing values."""

    if not value:
        return None
    match = _NEWS_TOGGLE_CALL_RE.fullmatch(value)
    if not match or (require_javascript_prefix and match.group("prefix") is None):
        return None
    return match.group("entry_id"), match.group("alt")


def _token_has_class(token: _MarkupToken, class_name: str) -> bool:
    values = _attrs_map(token.attrs).get("class", "")
    return class_name.casefold() in {part.casefold() for part in re.split(r"\s+", values) if part}


def _news_toggle_anchor_tag(token: _MarkupToken) -> str:
    raw = token.raw
    if token.self_closing:
        close = re.search(r"\s*/\s*>$", raw)
        if close is None:
            raise PagesExportError("news toggle anchor self-closing tag has no stable end")
        position = close.start()
    else:
        position = raw.rfind(">")
        if position < 0:
            raise PagesExportError("news toggle anchor tag has no stable end")
    return raw[:position] + f' onclick="event.stopPropagation();" {_NEWS_TOGGLE_ANCHOR_MARKER}' + raw[position:]


def rewrite_news_toggle_anchors(text: str) -> tuple[str, bool, int]:
    """Give only paired historical news-toggle anchors one click owner.

    The source uses the same ``toggleEntry`` call in a narrow anchor's
    ``javascript:`` href and its nearest ``.hoverContainer`` onclick.  A
    pointer or Enter activation of that anchor otherwise invokes both paths.
    The derived anchor stops propagation while retaining the original href,
    so its default historical call runs exactly once.  Non-matching anchors,
    title links, forms, and ordinary list items are left untouched.
    """

    if "news-toggle" not in text or "toggleEntry" not in text:
        return text, False, 0

    parser = _MarkupTokenParser(text)
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        raise PagesExportError("news toggle anchor tokenization failed") from exc

    ancestors: list[_MarkupToken] = []
    anchor_replacements: list[tuple[int, int, str]] = []
    matched = 0
    for token in parser.tokens:
        if token.kind == "start":
            if token.name == "a":
                attrs = _attrs_map(token.attrs)
                href_call = _normalize_news_toggle_call(
                    attrs.get("href"), require_javascript_prefix=True
                )
                if href_call is not None and _token_has_class_any(ancestors, "li", "news-toggle"):
                    hover = _nearest_token_with_class(ancestors, "hoverContainer")
                    parent_call = _normalize_news_toggle_call(
                        _attrs_map(hover.attrs).get("onclick") if hover is not None else None
                    )
                    existing_onclick = attrs.get("onclick")
                    if hover is not None and parent_call == href_call and not existing_onclick:
                        if _NEWS_TOGGLE_ANCHOR_MARKER not in token.raw:
                            anchor_replacements.append((token.start, token.end, _news_toggle_anchor_tag(token)))
                            matched += 1
            if token.name not in _VOID_HTML_TAGS:
                ancestors.append(token)
        elif token.kind == "end":
            for index in range(len(ancestors) - 1, -1, -1):
                if ancestors[index].name == token.name:
                    del ancestors[index:]
                    break

    if not anchor_replacements:
        return text, False, 0

    for start, end, replacement in reversed(anchor_replacements):
        text = text[:start] + replacement + text[end:]

    if _NEWS_TOGGLE_STYLE_MARKER not in text:
        head_matches = list(re.finditer(r"</head\s*>", text, flags=re.I))
        if len(head_matches) != 1:
            raise PagesExportError("news toggle anchor style requires exactly one closing head tag")
        match = head_matches[0]
        text = text[:match.start()] + "\n" + _NEWS_TOGGLE_ANCHOR_STYLE + "\n" + text[match.start():]
    return text, True, matched


def _token_has_class_any(ancestors: list[_MarkupToken], tag: str, class_name: str) -> bool:
    return any(token.name == tag and _token_has_class(token, class_name) for token in ancestors)


def _nearest_token_with_class(ancestors: list[_MarkupToken], class_name: str) -> _MarkupToken | None:
    for token in reversed(ancestors):
        if _token_has_class(token, class_name):
            return token
    return None


def runtime_js(base_path: str, route_map: dict[str, str] | None = None) -> str:
    encoded = json.dumps(base_path)
    encoded_routes = json.dumps(route_map or {}, ensure_ascii=False, separators=(",", ":"))
    return f"""/* GitHub Pages route adapter; no network outside this project. */
(function (window, document) {{
    "use strict";
    var PREFIX = {encoded};
    // Embed the frozen route map so synchronous document.write/style/image
    // side effects are localized before the asynchronous fetch completes.
    var routes = {encoded_routes};
    var routeMapReady = true;
    var ready = fetch(PREFIX + "__offline/route-map.json", {{credentials: "same-origin"}})
        .then(function (r) {{ return r.ok ? r.json() : {{}}; }})
        .then(function (data) {{
            var loaded = data.routes || {{}};
            var key;
            for (key in loaded) if (Object.prototype.hasOwnProperty.call(loaded, key)) routes[key] = loaded[key];
            return data;
        }})
        .catch(function () {{ return {{}}; }});
    function mapHref(raw) {{
        if (!raw || /^(?:#|javascript:|mailto:|tel:|data:|about:)/i.test(raw)) return raw;
        var url;
        try {{ url = new URL(raw, document.baseURI); }} catch (e) {{ return raw; }}
        if (url.origin !== window.location.origin) return raw;
        var lookupPath = url.pathname;
        var alreadyPrefixed = lookupPath.indexOf(PREFIX) === 0;
        if (alreadyPrefixed) lookupPath = "/" + lookupPath.slice(PREFIX.length);
        var target = routes[lookupPath] || routes[lookupPath.replace(/\\/+$/, "")] || null;
        if (alreadyPrefixed && !target) return raw;
        if (!target) return raw;
        return target + url.search + url.hash;
    }}
    function missingImage(raw) {{
        return PREFIX + "__offline/missing-image.svg?source=" +
            encodeURIComponent(window.location.href) + "&requested=" +
            encodeURIComponent(String(raw)) + "&reason=dynamic-image-uncollected";
    }}
    function mapImage(raw) {{
        if (!raw || /^(?:data:|blob:)/i.test(String(raw)) || /^about:blank$/i.test(String(raw))) return raw;
        if (!routeMapReady) return raw;
        var mapped = mapHref(raw);
        if (mapped && mapped !== raw) return mapped;
        var url;
        try {{ url = new URL(raw, document.baseURI); }} catch (e) {{ return missingImage(raw); }}
        if (url.origin !== window.location.origin) return missingImage(raw);
        var lookupPath = url.pathname;
        if (lookupPath.indexOf(PREFIX) === 0) lookupPath = "/" + lookupPath.slice(PREFIX.length);
        var target = routes[lookupPath] || routes[lookupPath.replace(/\\/+$/, "")] || null;
        if (target) return target + url.search + url.hash;
        return missingImage(raw);
    }}
    function isPopupImageInput(raw) {{
        if (typeof raw !== "string") return false;
        var value = String(raw).trim();
        if (!value || /^(?:javascript:|data:|blob:|about:)/i.test(value)) return false;
        var url;
        try {{ url = new URL(value, document.baseURI); }} catch (e) {{ return false; }}
        var pathname = url.pathname || "";
        if (pathname.indexOf(PREFIX) === 0) pathname = "/" + pathname.slice(PREFIX.length);
        if (/\/__offline\/missing-image\.svg$/i.test(pathname)) return true;
        return /(?:^|\/)[^\/?#]+\.(?:jpe?g|png|gif|webp|bmp)$/i.test(pathname);
    }}
    function isProjectImageUrl(value) {{
        var url;
        try {{ url = new URL(value, document.baseURI); }} catch (e) {{ return false; }}
        return url.origin === window.location.origin && url.pathname.indexOf(PREFIX) === 0;
    }}
    function installPopupImageAdapter() {{
        if (window.__pagesPopupImageAdapter) return true;
        var original = window.popUpOmega;
        if (typeof original !== "function") return false;
        if (original.__pagesPopupImageAdapter) {{
            window.__pagesPopupImageAdapter = true;
            return true;
        }}
        var wrapped = function () {{
            var raw = arguments.length ? arguments[0] : "";
            if (isPopupImageInput(raw)) {{
                var mapped = mapImage(raw);
                if (isProjectImageUrl(mapped)) return window.open(mapped, "_blank", "noopener,noreferrer");
                return null;
            }}
            return original.apply(this, arguments);
        }};
        wrapped.__pagesPopupImageAdapter = true;
        window.popUpOmega = wrapped;
        window.__pagesPopupImageAdapter = true;
        return true;
    }}
    function mapExistingImages() {{
        if (!document.images) return;
        for (var i = 0; i < document.images.length; i++) {{
            var image = document.images[i];
            var pending = image.__pagesPendingImageSrc;
            var raw = pending !== undefined ? pending : (image.getAttribute("src") || image.src);
            var mapped = mapImage(raw);
            if (pending !== undefined || (mapped && mapped !== raw)) image.setAttribute("src", mapped);
            try {{ delete image.__pagesPendingImageSrc; }} catch (e) {{ image.__pagesPendingImageSrc = undefined; }}
        }}
    }}
    function mapCssImages(value) {{
        var css = String(value || "");
        return css.replace(/url\\(\\s*(["']?)(.*?)\\1\\s*\\)/ig, function (full, quote, raw) {{
            var mapped = mapImage(raw);
            return "url(" + quote + mapped + quote + ")";
        }});
    }}
    function mapDynamicMarkup(markup) {{
        // Historical document.write calls often assemble a quoted URL from
        // JavaScript fragments.  The resulting value can contain spaces
        // (for example ``icon_player interaction.jpg``), so the quoted arm
        // must not use the unquoted token grammar.
        var attr = /(\\b(?:src|href|background|poster)\\s*=\\s*)(?:(['"])([^'"<>]*)\\2|([^\\s'"<>]+))/ig;
        return String(markup).replace(attr, function (full, lead, quote, quotedRaw, bareRaw) {{
            var raw = quote ? quotedRaw : bareRaw;
            var mapped = /href\\s*=\\s*$/i.test(lead) ? mapHref(raw) : mapImage(raw);
            var delimiter = quote || "";
            return lead + delimiter + mapped + delimiter;
        }});
    }}
    function installMarkupAdapter() {{
        var owner = window.Element && window.Element.prototype;
        if (!owner || owner.__pagesMarkupAdapter) return;
        var descriptor = Object.getOwnPropertyDescriptor(owner, "innerHTML");
        if (descriptor && descriptor.get && descriptor.set) Object.defineProperty(owner, "innerHTML", {{
            configurable: descriptor.configurable,
            enumerable: descriptor.enumerable,
            get: descriptor.get,
            set: function (value) {{ return descriptor.set.call(this, mapDynamicMarkup(value)); }}
        }});
        owner.__pagesMarkupAdapter = true;
    }}
    function installDocumentAdapter() {{
        if (document.__pagesWriteAdapter) return;
        var originalWrite = document.write;
        var originalWriteln = document.writeln;
        function mappedWriteArgs(args, newline) {{
            var values = Array.prototype.slice.call(args).map(function (value) {{
                return mapDynamicMarkup(value);
            }});
            if (newline) {{
                if (!values.length) values.push("\\n");
                else values[values.length - 1] = String(values[values.length - 1]) + "\\n";
            }}
            return values;
        }}
        if (originalWrite) document.write = function (markup) {{
            return originalWrite.apply(document, mappedWriteArgs(arguments, false));
        }};
        if (originalWriteln) document.writeln = function (markup) {{
            return originalWriteln.apply(document, mappedWriteArgs(arguments, true));
        }};
        document.__pagesWriteAdapter = true;
    }}
    function installStyleAdapter() {{
        var proto = window.CSSStyleDeclaration && window.CSSStyleDeclaration.prototype;
        if (!proto || proto.__pagesStyleAdapter) return;
        var descriptor = Object.getOwnPropertyDescriptor(proto, "backgroundImage");
        if (descriptor && descriptor.get && descriptor.set) Object.defineProperty(proto, "backgroundImage", {{
            configurable: descriptor.configurable,
            enumerable: descriptor.enumerable,
            get: descriptor.get,
            set: function (value) {{ descriptor.set.call(this, mapCssImages(value)); }}
        }});
        proto.__pagesStyleAdapter = true;
    }}
    function installImageAdapter() {{
        var proto = window.HTMLImageElement && window.HTMLImageElement.prototype;
        if (!proto || proto.__pagesImageAdapter) return;
        var descriptor = Object.getOwnPropertyDescriptor(proto, "src");
        if (descriptor && descriptor.get && descriptor.set) {{
            Object.defineProperty(proto, "src", {{
                configurable: descriptor.configurable,
                enumerable: descriptor.enumerable,
                get: descriptor.get,
                set: function (value) {{
                    if (!routeMapReady) {{ this.__pagesPendingImageSrc = value; return; }}
                    descriptor.set.call(this, mapImage(value));
                }}
            }});
        }}
        var originalSetAttribute = proto.setAttribute;
        if (originalSetAttribute) {{
            proto.setAttribute = function (name, value) {{
                if (String(name).toLowerCase() === "src") {{
                    if (!routeMapReady) {{ this.__pagesPendingImageSrc = value; return; }}
                    value = mapImage(value);
                }}
                return originalSetAttribute.call(this, name, value);
            }};
        }}
        proto.__pagesImageAdapter = true;
    }}
    window.__WOWPages = {{ prefix: PREFIX, ready: ready, mapHref: mapHref, mapCssImages: mapCssImages, mapImage: mapImage, mapDynamicMarkup: mapDynamicMarkup }};
    installDocumentAdapter();
    installMarkupAdapter();
    installStyleAdapter();
    installImageAdapter();
    installPopupImageAdapter();
    document.addEventListener("click", function (event) {{
        var node = event.target;
        while (node && node.tagName !== "A") node = node.parentNode;
        if (!node || !node.getAttribute) return;
        var href = node.getAttribute("href");
        var mapped = mapHref(href);
        if (mapped && mapped !== href) {{
            event.preventDefault();
            window.location.href = mapped;
        }}
    }}, true);
    function wrapExactTopic() {{
        if (typeof window.exactTopic !== "function" || window.exactTopic.__pagesWrapped) return;
        var original = window.exactTopic;
        var wrapped = function () {{
            var args = Array.prototype.slice.call(arguments).map(function (value) {{
                return typeof value === "string" ? mapHref(value) : value;
            }});
            return original.apply(this, args);
        }};
        wrapped.__pagesWrapped = true;
        window.exactTopic = wrapped;
    }}
    function mapTopicLinks(callback, receiver) {{
        var topics = window.topicsArray;
        var key;
        if (!topics) return callback ? callback.call(receiver) : undefined;
        if (!callback) return;
        var saved = [];
        for (key in topics) {{
            if (Object.prototype.hasOwnProperty.call(topics, key) && topics[key] && topics[key].linkString) {{
                saved.push([topics[key], topics[key].linkString]);
                topics[key].linkString = mapHref(topics[key].linkString);
            }}
        }}
        try {{ return callback.call(receiver); }} finally {{
            for (var i = 0; i < saved.length; i++) saved[i][0].linkString = saved[i][1];
        }}
    }}
    function wrapSearchCall() {{
        if (typeof window.searchCall !== "function" || window.searchCall.__pagesWrapped) return;
        var original = window.searchCall;
        var wrapped = function () {{
            var self = this;
            var args = arguments;
            return mapTopicLinks(function () {{ return original.apply(self, args); }}, self);
        }};
        wrapped.__pagesWrapped = true;
        window.searchCall = wrapped;
    }}
    function repair404() {{
        var marker = document.querySelector('meta[name="offline-pages-404"]');
        if (!marker) return;
        var current = location.pathname + location.search + location.hash;
        var mapped = mapHref(current);
        if (mapped && mapped !== current) location.replace(mapped);
    }}
    ready.then(function () {{ wrapSearchCall(); mapExistingImages(); repair404(); installPopupImageAdapter(); }});
    setTimeout(wrapExactTopic, 0);
    setTimeout(wrapExactTopic, 250);
    setTimeout(wrapSearchCall, 0);
    setTimeout(wrapSearchCall, 250);
    setTimeout(wrapSearchCall, 1000);
    setTimeout(mapExistingImages, 250);
    setTimeout(installPopupImageAdapter, 0);
    setTimeout(installPopupImageAdapter, 250);
    setTimeout(installPopupImageAdapter, 1000);
}}(window, document));
"""


def generated_uncollected(base_path: str, title: str = "Offline route") -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<meta http-equiv="Content-Security-Policy" content="{html.escape(PAGES_CSP, quote=True)}">
<script src="{base_path}__offline/pages_runtime.js"></script></head><body>
<div id="__offline-pages-banner" style="background:#241b0b;color:#f7e7b0;padding:6px 10px;font:12px Arial">Unofficial historical educational preservation (not affiliated with Blizzard) • Archive reconstruction based on 2008-05-12 • no user data collection</div>
<main style="max-width:760px;margin:2em auto;font:16px sans-serif"><h1>{html.escape(title)}</h1>
<p>This route was not collected in the verified archive. GitHub Pages will not fetch it from the Internet.</p>
<dl id="details"></dl></main>
<script>(function(){{var d=document.getElementById("details"),p=new URLSearchParams(location.search);["kind","target","query","source","requested","reason"].forEach(function(k){{if(p.has(k)){{var dt=document.createElement("dt"),dd=document.createElement("dd");dt.textContent=k;dd.textContent=p.get(k);d.appendChild(dt);d.appendChild(dd);}}}})}}());</script>
</body></html>"""


def generated_redirect(base_path: str, target: str) -> str:
    escaped = html.escape(target, quote=True)
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={escaped}">
<meta http-equiv="Content-Security-Policy" content="{html.escape(PAGES_CSP, quote=True)}">
<script src="{base_path}__offline/pages_runtime.js"></script></head><body>
<div id="__offline-pages-banner" style="background:#241b0b;color:#f7e7b0;padding:6px 10px;font:12px Arial">Unofficial historical educational preservation (not affiliated with Blizzard) • Archive reconstruction based on 2008-05-12 • no user data collection</div>
<p>Redirecting to <a href="{escaped}">{escaped}</a>.</p></body></html>"""


def generated_related_images_index(base_path: str, overlays: list[dict[str, Any]]) -> str:
    """Render a small local catalog for explicit non-primary image supplements."""

    cards: list[str] = []
    for overlay in overlays:
        image_url = static_url(base_path, str(overlay["relative"]))
        original_url = str(overlay["original_url"])
        capture_timestamp = overlay.get("actual_timestamp") or overlay.get("indexed_capture_timestamp")
        capture_date = datetime.strptime(str(capture_timestamp), "%Y%m%d%H%M%S")
        captured = capture_date.strftime("%Y-%m-%d %H:%M:%S UTC")
        temporal_label = {
            "baseline_2008": "2008 baseline",
            "pre_2008": "Earlier capture",
            "late_2008": "Later 2008 capture",
            "post_2008": "Post-2008 capture",
        }[str(overlay["temporal_class"])]
        if overlay.get("recovery_method") == "payload_digest_reuse":
            payload_capture = datetime.strptime(
                str(overlay["payload_source"]["actual_capture_timestamp"]), "%Y%m%d%H%M%S"
            ).strftime("%Y-%m-%d %H:%M:%S UTC")
            capture_markup = (
                f"<span>Target indexed capture: {html.escape(captured)}; "
                f"payload source capture: {html.escape(payload_capture)}</span>"
            )
        else:
            capture_markup = (
                f"<time datetime=\"{capture_date:%Y-%m-%dT%H:%M:%SZ}\">{captured}</time>"
            )
        cards.append(
            f"<article class=\"related-image-card\" data-temporal-class=\"{html.escape(str(overlay['temporal_class']), quote=True)}\">"
            f"<a href=\"{html.escape(image_url, quote=True)}\"><img loading=\"lazy\" src=\"{html.escape(image_url, quote=True)}\" alt=\"{html.escape(original_url, quote=True)}\"></a>"
            f"<p><code>{html.escape(str(overlay['origin_namespace']))}</code> "
            f"{capture_markup} <span>{temporal_label}</span></p>"
            f"<p class=\"source\">{html.escape(original_url)}</p>"
            "</article>"
        )
    body = "\n".join(cards) or "<p>No supplement images were accepted.</p>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Related image supplements</title>
<meta http-equiv="Content-Security-Policy" content="{html.escape(PAGES_CSP, quote=True)}">
<script src="{base_path}__offline/pages_runtime.js"></script>
<style>body{{margin:0;background:#f3ead4;color:#2d2418;font:15px/1.45 Arial,sans-serif}}main{{max-width:1100px;margin:0 auto;padding:24px}}h1{{font-size:26px}}.notice{{background:#fff8e8;border:1px solid #c9b68f;padding:12px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:18px;margin-top:20px}}.related-image-card{{background:#fff;border:1px solid #d2c4a6;padding:10px;overflow:hidden}}.related-image-card img{{display:block;max-width:100%;height:auto;margin:0 auto}}.related-image-card p{{margin:8px 0 0;word-break:break-word}}.related-image-card code{{font-size:12px}}.source{{font-size:12px;color:#665b4a}}</style></head><body>
<div id="__offline-pages-banner" style="background:#241b0b;color:#f7e7b0;font:12px/1.4 Arial,sans-serif;padding:6px 10px;text-align:center">Unofficial historical educational preservation (not affiliated with Blizzard) • material catalog only • no user data collection</div>
<main><h1>Related site images</h1><p class="notice">Recovered images from historical World of Warcraft sites. Dates show each file's capture time in UTC.</p><section class="grid">{body}</section></main></body></html>"""


def generated_404(base_path: str) -> str:
    return (
        generated_uncollected(base_path, "Page not in this archive")
        .replace(
            "This route was not collected in the verified archive. GitHub Pages will not fetch it from the Internet.",
            "This page was not saved in the available archive.",
            1,
        )
        .replace(
            "<meta charset=\"utf-8\">",
            '<meta charset="utf-8"><meta name="offline-pages-404" content="true">',
            1,
        )
    )


def export_pages(
    *,
    source_site: Path = DEFAULT_SITE,
    manifest_path: Path = DEFAULT_MANIFEST,
    output: Path = DEFAULT_OUTPUT,
    base_path: str = DEFAULT_BASE_PATH,
    workspace_root: Path = ROOT,
    max_bytes: int | None = DEFAULT_MAX_BYTES,
    min_free_bytes: int = DEFAULT_MIN_FREE_BYTES,
    image_source_maps: list[Path] | tuple[Path, ...] = (),
    supplement_image_source_maps: list[Path] | tuple[Path, ...] = (),
    allow_later_image_supplements: bool = False,
    guide_preview_map: Path | None = None,
    guide_image_collection_map: Path | None = None,
    flash_runtime_archive: Path | None = None,
    blizzcast_source_map: Path | None = None,
    related_talent_icon_map: Path | None = None,
    source16_layout_map: Path | None = None,
) -> dict[str, Any]:
    source_site = source_site.resolve()
    manifest_path = manifest_path.resolve()
    output = output.resolve()
    workspace_root = workspace_root.resolve()
    base_path = normalize_base_path(base_path)
    if output.exists():
        raise PagesExportError(f"refusing to overwrite existing output: {output}")
    partial = output.with_name(output.name + ".partial")
    if partial.exists():
        raise PagesExportError(f"refusing to reuse existing partial output: {partial}")
    if not source_site.is_dir() or not manifest_path.is_file():
        raise PagesExportError("source site or build manifest is missing")
    manifest_sha = sha256_file(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = list(manifest.get("files") or [])
    if not records:
        raise PagesExportError("manifest has no files")
    before_workspace = workspace_size(workspace_root, output) if max_bytes is not None else None
    free_before = shutil.disk_usage(output.parent).free

    route_records: dict[str, dict[str, Any]] = {}
    route_to_static: dict[str, str] = {}
    relative_paths: set[str] = set()
    for record in records:
        route = safe_route(str(record.get("route") or ""))
        if route in route_records:
            raise PagesExportError(f"duplicate manifest route: {route}")
        route_records[route] = record
        relative = static_rel_for_route(route, record)
        if relative in relative_paths:
            raise PagesExportError(f"static route collision at {relative}")
        relative_paths.add(relative)
        route_to_static[route] = static_url(base_path, relative)

    raw_aliases = manifest.get("route_aliases") or {}
    primary_overlays, primary_overlay_bytes = load_image_overlays(
        tuple(image_source_maps),
        workspace_root=workspace_root,
        anchor_timestamp=str(manifest.get("anchor_timestamp") or ""),
        frozen_routes=set(route_records) | {str(alias) for alias in raw_aliases},
        frozen_static_paths=set(relative_paths),
    )
    overlay_routes = set(route_records) | {str(alias) for alias in raw_aliases} | {str(item["route"]) for item in primary_overlays}
    overlay_static_paths = set(relative_paths) | {str(item["relative"]) for item in primary_overlays}
    supplement_overlays, supplement_overlay_bytes = load_supplement_image_overlays(
        tuple(supplement_image_source_maps),
        workspace_root=workspace_root,
        anchor_timestamp=str(manifest.get("anchor_timestamp") or ""),
        frozen_routes=overlay_routes,
        frozen_static_paths=overlay_static_paths,
        allow_later_image_supplements=allow_later_image_supplements,
    )
    overlays = primary_overlays + supplement_overlays
    overlay_bytes = primary_overlay_bytes + supplement_overlay_bytes
    # The optional emulator is a derived browser dependency.  Its conservative
    # allowance is separate from original image payloads and checked before any
    # output is staged.
    flash_estimate = 80 * 1024 * 1024 if flash_runtime_archive is not None else 0
    blizzcast_bundle: blizzcast_reader.BlizzcastBundle | None = None
    blizzcast_map_sha: str | None = None
    if blizzcast_source_map is not None:
        reader_map = Path(blizzcast_source_map)
        if not reader_map.is_absolute():
            reader_map = workspace_root / reader_map
        try:
            blizzcast_bundle = blizzcast_reader.load_blizzcast_bundle(
                reader_map, workspace_root, base_path,
            )
        except blizzcast_reader.BlizzcastReaderError as exc:
            raise PagesExportError(str(exc)) from exc
        blizzcast_map_sha = sha256_file(reader_map)
        for generated in blizzcast_bundle.generated_files:
            route = safe_route(str(generated["path"]))
            relative = route.lstrip("/")
            if route in route_to_static or route in raw_aliases or relative in relative_paths:
                raise PagesExportError(f"BlizzCast reading route collides with frozen input: {route}")
            route_to_static[route] = static_url(base_path, relative)
            relative_paths.add(relative)
    reader_estimate = blizzcast_bundle.estimated_bytes if blizzcast_bundle else 0
    talent_icon_bundle: related_talent_icons.RelatedTalentBundle | None = None
    if related_talent_icon_map is not None:
        icon_map = Path(related_talent_icon_map)
        if not icon_map.is_absolute():
            icon_map = workspace_root / icon_map
        try:
            talent_icon_bundle = related_talent_icons.load_related_talent_bundle(icon_map, workspace_root, base_path)
        except related_talent_icons.RelatedTalentIconError as exc:
            raise PagesExportError(str(exc)) from exc
        candidates = [(asset.route, asset.relative) for asset in talent_icon_bundle.assets]
        candidates.append(("/" + talent_icon_bundle.catalog_relative, talent_icon_bundle.catalog_relative))
        for route, relative in candidates:
            if route in route_to_static or route in raw_aliases or route in overlay_routes or relative in relative_paths or relative in overlay_static_paths:
                raise PagesExportError(f"related talent icon collides with an existing resource: {route}")
        for route, relative in candidates:
            route_to_static[route] = static_url(base_path, relative)
            relative_paths.add(relative)
    talent_icon_estimate = talent_icon_bundle.estimated_bytes if talent_icon_bundle else 0
    estimate = output_estimate(records, overlay_bytes + flash_estimate + reader_estimate + talent_icon_estimate)
    if max_bytes is not None and before_workspace + estimate >= max_bytes:
        raise PagesExportError(f"workspace budget exceeded before export: {before_workspace}+{estimate} >= {max_bytes}")
    if free_before - estimate < min_free_bytes:
        raise PagesExportError(f"disk reserve would be breached before export: {free_before}-{estimate} < {min_free_bytes}")

    for overlay in overlays:
        route = str(overlay["route"])
        relative = str(overlay["relative"])
        route_to_static[route] = static_url(base_path, relative)
        relative_paths.add(relative)
    related_image_overlays = [
        overlay for overlay in supplement_overlays if not mirror.is_primary_origin(str(overlay["logical_url"]))
    ]
    related_images_route = "/__offline/related-images/index.html"
    if related_image_overlays:
        route_to_static[related_images_route] = static_url(base_path, related_images_route.lstrip("/"))
    layout_bundle: source16_layout_compat.LayoutCompatibilityBundle | None = None
    if source16_layout_map is not None:
        try:
            layout_bundle = source16_layout_compat.load_layout_compatibility_bundle(
                source16_layout_map, workspace_root, source_site, manifest_path, manifest,
            )
        except source16_layout_compat.LayoutCompatibilityError as exc:
            raise PagesExportError(str(exc)) from exc
        for target, source_route in layout_bundle.route_reuses.items():
            if target in route_to_static or target in raw_aliases:
                raise PagesExportError(f"layout reuse target collides with an existing resource: {target}")
            if source_route not in route_to_static:
                raise PagesExportError(f"layout reuse source has no static route: {source_route}")
        # These routes point to existing image objects.  They are deliberately
        # absent from aliases, so no redirect HTML or duplicate image is emitted.
        for target, source_route in layout_bundle.route_reuses.items():
            route_to_static[target] = route_to_static[source_route]
    guide_preview_bundle: guide_previews.GuidePreviewBundle | None = None
    if guide_preview_map is not None:
        try:
            guide_preview_bundle = guide_previews.load_guide_preview_map(
                Path(guide_preview_map),
                workspace_root=workspace_root,
                source_site=source_site,
                manifest_path=manifest_path,
                manifest=manifest,
                route_to_static=route_to_static,
            )
        except guide_previews.GuidePreviewError as exc:
            raise PagesExportError(str(exc)) from exc
    guide_image_collection_bundle: guide_image_collections.GuideImageCollectionBundle | None = None
    if guide_image_collection_map is not None:
        try:
            guide_image_collection_bundle = guide_image_collections.load_guide_image_collection_map(
                Path(guide_image_collection_map),
                workspace_root=workspace_root,
                manifest_path=manifest_path,
                manifest=manifest,
                overlays=overlays,
                route_to_static=route_to_static,
                base_path=base_path,
            )
        except guide_image_collections.GuideImageCollectionError as exc:
            raise PagesExportError(str(exc)) from exc
    aliases: dict[str, str] = {}
    alias_routes: dict[str, str] = {}
    for alias, target in raw_aliases.items():
        alias = safe_route(str(alias))
        target = safe_route(str(target))
        target_url = route_to_static.get(target)
        if target_url:
            aliases[alias] = target_url
            alias_routes[alias] = target
    compatibility_aliases: set[str] = set()
    for alias, target in COMPATIBILITY_ROUTE_ALIASES.items():
        target_url = route_to_static.get(target) or aliases.get(target)
        if not target_url:
            continue
        aliases[alias] = target_url
        alias_routes[alias] = target
        compatibility_aliases.add(alias)
    # Root is always a real static jump page, rather than an implicit server
    # alias.  /index.xml remains a separate .xml.html HTML entity.
    root_target = aliases.get("/") or route_to_static.get("/index.xml") or route_to_static.get("/info/encyclopedia/index.xml")
    if not root_target:
        raise PagesExportError("manifest has no homepage target")
    aliases["/"] = static_url(base_path, "index.html")
    aliases["/index.html"] = static_url(base_path, "index.html")
    alias_routes["/"] = "/"
    alias_routes["/index.html"] = "/index.html"
    # Keep a route-level lookup table for the localizer; aliases are static
    # URLs here, while canonical routes are also exposed as static URLs.
    route_lookup = dict(route_to_static)
    route_lookup["/"] = aliases["/"]
    route_lookup["/index.html"] = aliases["/index.html"]
    for alias, target in list(aliases.items()):
        if alias in {"/", "/index.html"}:
            continue
        if target in route_to_static.values():
            # A trailing slash whose target is an index file already works on
            # Pages; non-trailing aliases receive a tiny concrete redirect.
            if alias.endswith("/"):
                continue
            route_lookup[alias] = target
        else:
            route_lookup[alias] = target
    # Generated Pages support routes do not occur in the frozen source
    # manifest, but source scripts may construct them dynamically (for
    # example compat.js's uncollected search target).  Register their final
    # static paths before any source text is localized.
    generated_routes = [
        "/__offline/uncollected/index.html",
        "/__offline/missing.html",
        "/__offline/pages_runtime.js",
        "/__offline/route-map.json",
        "/404.html",
    ]
    if related_image_overlays:
        generated_routes.append(related_images_route)
    for generated_route in generated_routes:
        route_lookup.setdefault(generated_route, static_url(base_path, generated_route.lstrip("/")))

    origin_index = {str(k): str(v) for k, v in (manifest.get("origin_index") or {}).items()}
    for overlay in overlays:
        key = mirror.origin_key(str(overlay["logical_url"]))
        existing = origin_index.get(key)
        route = str(overlay["route"])
        if existing is not None and existing != route:
            raise PagesExportError(f"image overlay origin index conflicts with frozen route: {key}")
        origin_index[key] = route
    if blizzcast_bundle is not None:
        for original_url, route in blizzcast_bundle.origin_routes.items():
            key = mirror.origin_key(original_url)
            if key in origin_index and origin_index[key] != route:
                raise PagesExportError(f"BlizzCast origin conflicts with frozen source: {key}")
            origin_index[key] = route
    if talent_icon_bundle is not None:
        for asset in talent_icon_bundle.assets:
            key = mirror.origin_key("http://www.worldofwarcraft.com" + asset.route)
            if key in origin_index and origin_index[key] != asset.route:
                raise PagesExportError(f"related talent icon origin conflicts with frozen source: {key}")
            origin_index[key] = asset.route
    if layout_bundle is not None:
        for target in layout_bundle.route_reuses:
            key = mirror.origin_key("http://www.worldofwarcraft.com" + target)
            if key in origin_index and origin_index[key] != target:
                raise PagesExportError(f"layout reuse origin conflicts with frozen source: {key}")
            origin_index[key] = target
    validated_navigation_image_routes = frozenset(str(item["route"]) for item in overlays)
    localizer = PagesLocalizer(
        route_to_static=route_lookup,
        aliases=alias_routes,
        origin_index=origin_index,
        base_path=base_path,
        validated_navigation_image_routes=validated_navigation_image_routes,
        validated_related_page_routes=frozenset(blizzcast_bundle.origin_routes.values()) if blizzcast_bundle else frozenset(),
    )
    provenance: list[dict[str, Any]] = []
    stats: Counter[str] = Counter()
    if layout_bundle is not None:
        stats["layout_compatibility_reused_target_paths"] = len(layout_bundle.route_reuses)
    if guide_image_collection_bundle is not None:
        # Count curated source images once even though each is rendered on its
        # guide page and its related gallery page.
        stats["guide_image_collection_images"] = guide_image_collection_bundle.image_count
    partial.mkdir(parents=True, exist_ok=False)
    promotion_attempted = False
    flash_bundle: dict[str, Any] | None = None
    try:
        if talent_icon_bundle is not None:
            for asset in talent_icon_bundle.assets:
                if shutil.disk_usage(output.parent).free < min_free_bytes + len(asset.data):
                    raise PagesExportError("disk reserve would be breached while writing related talent icons")
                out = partial / asset.relative
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(asset.data)
                source_reference = dict(talent_icon_bundle.source_metadata) | {
                    "source_kind": "related_git_repository",
                    "repository_path": asset.relative,
                    "git_blob_sha1": asset.metadata["git_blob_sha1"],
                }
                provenance.append({
                    "route": asset.route, "static_url": static_url(base_path, asset.relative),
                    "output_path": asset.relative, "source_offline_path": None,
                    "source_manifest_sha256": None, "source_manifest_length": None,
                    "source_sha256": asset.metadata["sha256"], "source_length": len(asset.data),
                    "derived_sha256": asset.metadata["sha256"], "derived_length": len(asset.data),
                    "mime": asset.mime, "kind": "related_talent_icon", "role": "later_related_talent_icon",
                    "transformed": False, "source_refs": [source_reference],
                })
                stats["related_talent_icons"] += 1
            if shutil.disk_usage(output.parent).free < min_free_bytes + len(talent_icon_bundle.catalog_bytes):
                raise PagesExportError("disk reserve would be breached while writing the related icon catalog")
            relative = talent_icon_bundle.catalog_relative
            out = partial / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(talent_icon_bundle.catalog_bytes)
            provenance.append({
                "route": "/" + relative, "static_url": static_url(base_path, relative), "output_path": relative,
                "source_offline_path": None, "source_manifest_sha256": None, "source_manifest_length": None,
                "source_sha256": None, "source_length": None,
                "derived_sha256": sha256_bytes(talent_icon_bundle.catalog_bytes),
                "derived_length": len(talent_icon_bundle.catalog_bytes),
                "mime": "application/json; charset=UTF-8", "kind": "related_talent_icon_catalog",
                "role": "later_related_talent_icon_catalog", "transformed": True,
            })
        if blizzcast_bundle is not None:
            for generated in blizzcast_bundle.generated_files:
                if shutil.disk_usage(output.parent).free < min_free_bytes + int(generated["bytes"]):
                    raise PagesExportError("disk reserve would be breached while writing BlizzCast reader")
                route = str(generated["path"])
                relative = route.lstrip("/")
                data = str(generated["data"]).encode("utf-8")
                out = partial / relative
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
                is_page = relative.endswith(".html")
                provenance.append({
                    "route": route, "static_url": static_url(base_path, relative), "output_path": relative,
                    "source_offline_path": None, "source_manifest_sha256": None, "source_manifest_length": None,
                    "source_sha256": None, "source_length": None,
                    "derived_sha256": sha256_bytes(data), "derived_length": len(data),
                    "mime": "text/html; charset=UTF-8" if is_page else "text/css; charset=UTF-8",
                    "kind": "related_reading_page" if is_page else "related_reading_style",
                    "role": "historical_blizzcast_reading_view", "transformed": True,
                    "source_map_sha256": blizzcast_map_sha, "curated_sources": generated["curated_sources"],
                })
                stats["blizzcast_reading_pages" if is_page else "blizzcast_reading_styles"] += 1
        if flash_runtime_archive is not None:
            # All three archived movies must already be exact frozen inputs.
            # This opt-in never introduces an arbitrary SWF or plugin loader.
            for exhibit in offline_flash.SWF_EXHIBITS.values():
                source_record = route_records.get("/" + exhibit["path"])
                if source_record is None or source_record.get("derived_sha256") != exhibit["sha256"]:
                    raise PagesExportError(f"validated Flash source is absent or differs: {exhibit['path']}")
            try:
                staged_flash = offline_flash.stage_runtime(
                    partial,
                    archive_path=Path(flash_runtime_archive),
                    base_path=base_path,
                    min_free_bytes=min_free_bytes,
                )
            except offline_flash.OfflineFlashError as exc:
                raise PagesExportError(str(exc)) from exc
            runtime_rows = []
            for runtime_file in staged_flash["files"]:
                relative = str(runtime_file["output_path"])
                runtime_route = "/" + relative
                if relative in relative_paths or runtime_route in route_lookup:
                    raise PagesExportError(f"Flash runtime collides with a source route: {relative}")
                relative_paths.add(relative)
                route_lookup[runtime_route] = static_url(base_path, relative)
                provenance.append({
                    "route": runtime_route,
                    "static_url": static_url(base_path, relative),
                    "output_path": relative,
                    "source_offline_path": None,
                    "source_manifest_sha256": None,
                    "source_manifest_length": None,
                    "source_sha256": runtime_file["source_sha256"],
                    "source_length": runtime_file["length"],
                    "derived_sha256": runtime_file["sha256"],
                    "derived_length": runtime_file["length"],
                    "mime": runtime_file["mime"],
                    "kind": runtime_file["kind"],
                    "role": "optional_flash_exhibit_compatibility",
                    "transformed": False,
                    "source_member": runtime_file.get("source_member"),
                    "runtime_version": staged_flash["runtime_version"],
                })
                runtime_rows.append({key: runtime_file[key] for key in ("output_path", "sha256", "length", "kind")})
            flash_bundle = {
                "runtime_version": staged_flash["runtime_version"],
                "archive_sha256": staged_flash["archive_sha256"],
                "runtime_release": "https://github.com/ruffle-rs/ruffle/releases/tag/v0.7.1",
                "runtime_license": "MIT OR Apache-2.0",
                "files": runtime_rows,
                "original_swfs": offline_flash.SWF_EXHIBITS,
                "policy": "manual players on three exact pages; no global polyfill or historical business Flash",
            }
            stats["flash_runtime_files"] = len(runtime_rows)
        # Copy/derive every frozen entity.  Verification is against the
        # derived bytes named by offline/build-manifest.json, not an inferred
        # source path, so ZIP-backed and generated source records are safe.
        for record in records:
            route = str(record["route"])
            source_rel = str(record.get("output_path") or "")
            source = (workspace_root / source_rel).resolve()
            try:
                source.relative_to(source_site)
            except ValueError as exc:
                raise PagesExportError(f"manifest output escapes frozen site: {source_rel}") from exc
            if not source.is_file():
                raise PagesExportError(f"frozen entity missing: {source_rel}")
            source_length = source.stat().st_size
            source_sha = sha256_file(source)
            expected_length = record.get("derived_length")
            if expected_length is None or source_length != int(expected_length) or source_sha != record.get("derived_sha256"):
                raise PagesExportError(f"frozen entity SHA/length mismatch: {route}")
            data = source.read_bytes()
            derived = data
            kind = str(record.get("kind") or "other")
            base_url = str(record.get("source_base_url") or ("http://www.worldofwarcraft.com" + route))
            recorder = mirror.ReferenceRecorder(route, base_url)
            derivation_notes: list[str] = []
            main_page_reference = source16_main_page_reference(record)
            # A few frozen support placeholders are explicitly typed as
            # generated_placeholder but still carry text/html MIME.  Emit
            # those through the same UTF-8/CSP/banner path so every static
            # HTML response remains self-describing on Pages.
            if kind in HTML_KINDS or is_html_record(record):
                text = data.decode(mirror.charset_for(str(record.get("mime") or ""), data), errors="replace")
                text = mirror.rewrite_html(text, base_url=base_url, localizer=localizer, recorder=recorder, source_sha=source_sha, compat_assets=[])
                if route == _ATTUNEMENT_MASK_ROUTE:
                    text, changed = rewrite_attunement_mask_pixel(text, route=route, base_path=base_path)
                    if changed:
                        derivation_notes.append(
                            "derived attunement map mask repair: replaced #mapPixel plus the exact visible "
                            ".coverDivStyle1/.coverDivStyle2 background placeholders for the original "
                            "bcattunement/images/pixel.gif with the collected transparent shared pixel; "
                            "legacy _background and all other pixel references remain unchanged; no original "
                            "attunement pixel payload was recovered"
                        )
                        stats["attunement_mask_pixel_repaired"] += 1
                if route == _PVP_FLASH_ROUTE:
                    text, changed = rewrite_pvp_mini_site(text, route=route, base_path=base_path)
                    if changed:
                        derivation_notes.append(
                            "derived PvP mini-site repair: replaced the obsolete generated subnav and Flash intro "
                            "with local Archive home/Game Guide links and a static 2007 panel; frozen source unchanged"
                        )
                        stats["pvp_mini_site_repaired"] += 1
                if route == "/downloads/ssotd/index.html":
                    text, changed, shot_number = rewrite_ssotd_clock(
                        text,
                        actual_timestamp=str(record.get("actual_timestamp") or ""),
                    )
                    if changed:
                        derivation_notes.append(
                            "SSOTD currentShotNumber derived from manifest actual_timestamp "
                            f"{record.get('actual_timestamp')} UTC using floor(epoch_days) - startDate(12671) = {shot_number}; "
                            "this does not verify the raw screenshot total"
                        )
                        stats["ssotd_clock_repaired"] += 1
                text = rename_flash_codebase_metadata(text, recorder=recorder)
                text = rewrite_iframe_fallbacks(text, base_url=base_url, localizer=localizer, recorder=recorder)
                text = rewrite_inline_scripts(text, base_url=base_url, localizer=localizer, recorder=recorder)
                text = normalize_html_charset(text)
                text = disable_sensitive_forms(text, route=route)
                text = historical_exhibits.transform_derived_page(
                    text,
                    route,
                    base_path=base_path,
                    source_metadata={"actual_timestamp": str(record.get("actual_timestamp") or "")},
                )
                try:
                    text, compat_stats = non_gallery_compat.transform_html(text, route=route)
                except non_gallery_compat.NonGalleryCompatError as exc:
                    raise PagesExportError(str(exc)) from exc
                if compat_stats["changed"]:
                    stats["non_gallery_compat_pages"] += 1
                    stats["downloads_hover_repaired"] += compat_stats["downloads_hover_fixes"]
                    stats["menu_header_labels_repaired"] += compat_stats["menu_label_count"]
                    derivation_notes.append(
                        "derived shared menu labels and exact measured downloads hover repair; historical source unchanged"
                    )
                if flash_bundle is not None:
                    try:
                        text, flash_stats = offline_flash.rewrite_page(
                            text, route="/" + static_rel_for_route(route, record), base_path=base_path,
                        )
                    except offline_flash.OfflineFlashError as exc:
                        raise PagesExportError(str(exc)) from exc
                    if flash_stats.get("helper_injected"):
                        stats["flash_exhibit_pages"] += 1
                        derivation_notes.append(
                            "manual Ruffle compatibility for byte-verified preserved Flash content on this exact page"
                        )
                if guide_preview_bundle is not None:
                    guide_group = guide_preview_bundle.group_for_gallery(route)
                    if guide_group is not None:
                        try:
                            text = guide_previews.insert_gallery_section(text, guide_group)
                        except guide_previews.GuidePreviewError as exc:
                            raise PagesExportError(str(exc)) from exc
                        derivation_notes.append(
                            f"inserted {len(guide_group.previews)} accepted guide previews before gallery body "
                            f"from {guide_preview_bundle.map_path.as_posix()}; no dynamic gallery aliases changed"
                        )
                        stats["guide_preview_gallery_pages"] += 1
                        stats["guide_preview_count"] += len(guide_group.previews)
                if guide_image_collection_bundle is not None:
                    guide_image_page = guide_image_collection_bundle.group_for_route(route)
                    if guide_image_page is not None:
                        guide_image_group, page_role = guide_image_page
                        try:
                            text = guide_image_collections.insert_guide_image_section(
                                text,
                                guide_image_group,
                                page_role,
                            )
                        except guide_image_collections.GuideImageCollectionError as exc:
                            raise PagesExportError(str(exc)) from exc
                        derivation_notes.append(
                            f"inserted {len(guide_image_group.images)} validated guide images on {page_role} page "
                            f"from {guide_image_collection_bundle.map_path.as_posix()}; no native gallery aliases changed"
                        )
                        stats["guide_image_collection_pages"] += 1
                text, changed = rewrite_wrath_card_hit_area(text, route=route)
                if changed:
                    derivation_notes.append(
                        "derived Wrath card hit-area fallback on the exact artwork/screenshots route: "
                        "243x193 anchor geometry and narrowly hidden missing decorative ssborder image; "
                        "no image payload recovered"
                    )
                    stats["wrath_card_hit_area_repaired"] += 1
                text, changed, toggle_count = rewrite_news_toggle_anchors(text)
                if changed:
                    derivation_notes.append(
                        "derived news-toggle anchor repair: only anchors whose javascript toggleEntry href "
                        "matches the nearest hoverContainer onclick receive stopPropagation and a 14x11 hit area; "
                        "original href/default action preserved"
                    )
                    stats["news_toggle_anchor_repaired"] += toggle_count
                text = normalize_html_prolog(text)
                text = inject_html_runtime(text, base_path=base_path, source_sha=source_sha)
                text = annotate_source16_main_page(text, main_page_reference)
                if main_page_reference is not None:
                    stats["source16_main_pages"] += 1
                if talent_icon_bundle is not None:
                    text, has_icon_notice = annotate_related_talent_icons(
                        text, route=route, notice_html=talent_icon_bundle.notice_html,
                    )
                    if has_icon_notice:
                        stats["related_talent_icon_notice_pages"] += 1
                derived = text.encode("utf-8")
                stats["html_derived"] += 1
            elif kind == "css" or (kind == "support" and source.suffix.casefold() == ".css"):
                text = data.decode(mirror.charset_for(str(record.get("mime") or ""), data), errors="replace")
                derived = mirror.rewrite_css(text, base_url=base_url, localizer=localizer, recorder=recorder).encode("utf-8")
                stats["css_derived"] += 1
            elif kind == "js" or (kind == "support" and source.suffix.casefold() in {".js", ".htc"}):
                text = data.decode(mirror.charset_for(str(record.get("mime") or ""), data), errors="replace")
                if route == "/shared/wow-com/includes-client/navtree-main.js":
                    text, changed = rewrite_navtree_community_ids(text)
                    if changed:
                        derivation_notes.append(
                            "derived Community nav repair: Menu1_6 child count 10 -> 11 and Fan Sites Menu1_6_10 -> Menu1_6_11; frozen navtree source unchanged"
                        )
                        stats["navtree_community_repaired"] += 1
                if route == "/new-hp/js/ssotd-screenie.js":
                    text, changed, fallbacks = rewrite_ssotd_thumbnail_fallback(
                        text,
                        route_to_static=route_to_static,
                        base_path=base_path,
                    )
                    if changed:
                        derivation_notes.append(
                            "SSOTD thumbnail fallback uses verified full static URLs only for "
                            f"{len(fallbacks)} shot(s) whose -thumb route is absent; no image payload is invented"
                        )
                        stats["ssotd_thumbnail_fallback_repaired"] += 1
                if route == "/wrath/js/screeniesimplified.js":
                    text = rewrite_wrath_viewer_script(text)
                    derivation_notes.append(
                        "Wrath viewer query parser accepts one safe decimal s value "
                        "within shotList.length; invalid or repeated values fall back to 1"
                    )
                    stats["wrath_viewer_query_repaired"] += 1
                try:
                    text, toplist_handled = rewrite_toplist_script(
                        text,
                        route,
                        source_sha,
                        base_url,
                        localizer,
                        recorder,
                    )
                except ToplistCompatError as exc:
                    raise PagesExportError(str(exc)) from exc
                if toplist_handled:
                    if route == "/toplist/includes-client/js/prototype.js":
                        derivation_notes.append(
                            "derived Toplist compatibility guard preserved the exact Source15 Prototype text "
                            "and skipped generic JavaScript URL rewrites"
                        )
                    else:
                        derivation_notes.append(
                            "derived Toplist compatibility guard replaced exactly five escaped pixel src values "
                            "with local image URLs and skipped generic JavaScript URL rewrites"
                        )
                    stats["toplist_compat_repaired"] += 1
                else:
                    try:
                        text, talent_handled, talent_stats = talent_compat.rewrite_talent_script(
                            text, route, source_sha, base_path,
                            lambda raw, *, context: localizer.localize(
                                raw, base_url=base_url, context=context, recorder=recorder,
                            ),
                        )
                    except talent_compat.TalentCompatError as exc:
                        raise PagesExportError(str(exc)) from exc
                    if talent_handled:
                        derivation_notes.append(
                            "exact Source15 talent script guard preserved quoted CSS/dynamic paths and "
                            "skipped generic JavaScript rewrites; " + json.dumps(talent_stats, sort_keys=True)
                        )
                        stats["talent_compat_scripts"] += 1
                    else:
                        text = mirror.rewrite_script(text, base_url=base_url, localizer=localizer, recorder=recorder)
                        text = rewrite_root_literals(text, base_url=base_url, localizer=localizer, recorder=recorder)
                if route == "/shared/wow-com/includes-client/navtreefunctions.js":
                    text, changed = rewrite_contest_navtree_fallback(text, base_path=base_path)
                    if changed:
                        derivation_notes.append(
                            "derived contest nav fallback: exact project-prefixed /contests/05-05-25/winners.html "
                            "path may use verified Menu1_6_4 only when stripId(Menu1_6_4[0]) is Contests; "
                            "findNode/pageId/source menu remain unchanged"
                        )
                        stats["contest_navtree_fallback_repaired"] += 1
                if route == _RETIRED_ARMORY_TOOLTIP_ROUTE:
                    text, changed = rewrite_retired_armory_tooltip(text, route)
                    if changed:
                        derivation_notes.append(
                            "derived retired Armory tooltip exhibit: replaced the exact requestHTML iframe/domain "
                            "request with a historical static caption; cached enhancedXmlTTip nodes remain unchanged"
                        )
                        stats["retired_armory_tooltip_repaired"] += 1
                if route == "/__offline/compat.js":
                    text = rewrite_compat_script(text)
                if route == "/info/encyclopedia/scripts/cascade.js":
                    text = rewrite_cascade_script(text)
                if route == "/wrath/js/thumbnailslayout.js":
                    text = rewrite_wrath_thumbnails_script(text)
                derived = text.encode("utf-8")
                stats["js_derived"] += 1
            elif kind in {"xsl", "xml", "legacy_component"}:
                text = data.decode(mirror.charset_for(str(record.get("mime") or ""), data), errors="replace")
                text = mirror.rewrite_generic_markup(text, base_url=base_url, localizer=localizer, recorder=recorder)
                text = rewrite_root_literals(text, base_url=base_url, localizer=localizer, recorder=recorder)
                text = escape_xml_bare_ampersands(text)
                derived = text.encode("utf-8")
                stats["markup_derived"] += 1
            else:
                stats["binary_copied"] += 1
            relative = static_rel_for_route(route, record)
            out = partial / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(derived)
            out_sha = sha256_bytes(derived)
            item = {
                "route": route,
                "static_url": static_url(base_path, relative),
                "output_path": relative,
                "source_offline_path": source_rel,
                "source_manifest_sha256": record.get("derived_sha256"),
                "source_manifest_length": record.get("derived_length"),
                "source_sha256": source_sha,
                "source_length": source_length,
                "derived_sha256": out_sha,
                "derived_length": len(derived),
                "mime": "text/html; charset=UTF-8" if kind in HTML_KINDS else (record.get("mime") or mimetypes.guess_type(relative)[0] or "application/octet-stream"),
                "kind": kind,
                "role": record.get("role"),
                "transformed": bool(derived != data),
                "reference_counts": dict(recorder.counts),
            }
            if derivation_notes:
                item["derivation_reason"] = "; ".join(derivation_notes)
            if main_page_reference is not None:
                item["source_refs"] = [main_page_reference]
            if layout_bundle is not None and route in layout_bundle.per_page_records:
                item["layout_reuse_refs"] = list(layout_bundle.per_page_records[route])
                stats["layout_compatibility_pages"] += 1
            provenance.append(item)

        for overlay in overlays:
            route = str(overlay["route"])
            relative = str(overlay["relative"])
            out = partial / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            data = bytes(overlay["data"])
            out.write_bytes(data)
            overlay_provenance = {
                "route": route,
                "static_url": static_url(base_path, relative),
                "output_path": relative,
                "source_offline_path": None,
                "source_manifest_sha256": None,
                "source_manifest_length": None,
                "source_sha256": overlay["source_sha256"],
                "source_length": overlay["source_length"],
                "derived_sha256": sha256_bytes(data),
                "derived_length": len(data),
                "mime": overlay["mime"],
                "kind": "image_overlay",
                "role": "image_overlay",
                "transformed": False,
                "source_map": str(Path(overlay["map_path"]).relative_to(workspace_root).as_posix()),
                "source_map_sha256": overlay["source_map_sha256"],
                "source_path": str(Path(overlay["source"]).relative_to(workspace_root).as_posix()),
                "origin_namespace": overlay["origin_namespace"],
                "temporal_class": overlay["temporal_class"],
                "supplement_strategy": overlay["supplement_strategy"],
                "original_url": overlay["original_url"],
                "actual_capture_timestamp": overlay["actual_timestamp"],
                "indexed_capture_timestamp": overlay["indexed_capture_timestamp"],
                "cdx_digest": overlay["cdx_digest"],
            }
            if overlay.get("recovery_method") == "payload_digest_reuse":
                overlay_provenance.update(
                    {
                        "recovery_method": "payload_digest_reuse",
                        "payload_source": dict(overlay["payload_source"]),
                        "capture_timestamp_basis": "target_cdx_digest",
                    }
                )
            provenance.append(overlay_provenance)
            stats["image_overlay"] += 1

        # Concrete redirect files for aliases that Pages cannot infer from a
        # request path.  Existing index files are reused rather than replaced.
        existing = {item["output_path"] for item in provenance}
        for alias, target_url in list(aliases.items()):
            if alias in {"/", "/index.html"} or (
                alias.endswith("/") and alias not in compatibility_aliases
            ):
                continue
            # An XML compatibility alias can point directly at the exported
            # HTML entity.  Emitting an HTML redirect at the .xml path would
            # make local preview servers and strict XML clients treat the
            # alias as an XML document and may trigger MIME/nosniff failures.
            if (
                alias in compatibility_aliases
                and alias.casefold().endswith(".xml")
                and target_url.casefold().endswith(".xml.html")
            ):
                continue
            if alias.endswith("/"):
                rel = alias.lstrip("/") + "index.html"
            elif alias in compatibility_aliases and Path(alias).suffix:
                rel = alias.lstrip("/")
            else:
                rel = alias.lstrip("/") + ".html" if not alias.casefold().endswith(".html") else alias.lstrip("/")
            rel = re.sub(r"/{2,}", "/", rel)
            if not rel or rel in existing:
                continue
            out = partial / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            data = generated_redirect(base_path, target_url).encode("utf-8")
            out.write_bytes(data)
            route_lookup[alias] = static_url(base_path, rel)
            aliases[alias] = static_url(base_path, rel)
            provenance.append({"route": alias, "static_url": aliases[alias], "output_path": rel, "source_offline_path": None, "source_manifest_sha256": None, "source_manifest_length": None, "source_sha256": None, "source_length": None, "derived_sha256": sha256_bytes(data), "derived_length": len(data), "mime": "text/html; charset=UTF-8", "kind": "generated_redirect", "role": "route_alias", "transformed": True, "derivation_reason": "explicit compatibility alias for a verified Archived News internal link" if alias in compatibility_aliases else None})
            existing.add(rel)

        # Root jump page is deliberately generated after aliases are known.
        root_out = partial / "index.html"
        root_data = generated_redirect(base_path, root_target).encode("utf-8")
        root_out.write_bytes(root_data)
        provenance.append({"route": "/", "static_url": aliases["/"], "output_path": "index.html", "source_offline_path": None, "source_manifest_sha256": None, "source_manifest_length": None, "source_sha256": None, "source_length": None, "derived_sha256": sha256_bytes(root_data), "derived_length": len(root_data), "mime": "text/html; charset=UTF-8", "kind": "generated_root_redirect", "role": "pages_root", "transformed": True})

        offline_dir = partial / "__offline"
        offline_dir.mkdir(parents=True, exist_ok=True)
        route_payload = {"schema": "github-pages-route-map/v1", "base_path": base_path, "routes": dict(route_lookup), "aliases": dict(aliases), "root": aliases["/"]}
        route_data = (json.dumps(route_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        (offline_dir / "route-map.json").write_bytes(route_data)
        runtime_data = runtime_js(base_path, route_lookup).encode("utf-8")
        (offline_dir / "pages_runtime.js").write_bytes(runtime_data)
        (offline_dir / "uncollected").mkdir(parents=True, exist_ok=True)
        uncollected_data = generated_uncollected(base_path, "Offline route not collected").encode("utf-8")
        (offline_dir / "uncollected/index.html").write_bytes(uncollected_data)
        # A static missing page handles arbitrary placeholder query strings.
        (offline_dir / "missing.html").write_bytes(generated_uncollected(base_path, "Offline resource missing").encode("utf-8"))
        (partial / "404.html").write_bytes(generated_404(base_path).encode("utf-8"))
        generated_support = [
            ("__offline/route-map.json", route_data, "pages_route_map"),
            ("__offline/pages_runtime.js", runtime_data, "pages_runtime"),
            ("__offline/uncollected/index.html", uncollected_data, "pages_uncollected"),
            ("__offline/missing.html", (offline_dir / "missing.html").read_bytes(), "pages_missing"),
            ("404.html", (partial / "404.html").read_bytes(), "pages_404"),
        ]
        if related_image_overlays:
            related_images_data = generated_related_images_index(base_path, supplement_overlays).encode("utf-8")
            related_images_path = partial / related_images_route.lstrip("/")
            related_images_path.parent.mkdir(parents=True, exist_ok=True)
            related_images_path.write_bytes(related_images_data)
            generated_support.append((related_images_route.lstrip("/"), related_images_data, "related_images_index"))
        for rel, data, kind in generated_support:
            route = "/" + rel
            mime = "application/json" if rel.endswith(".json") else ("application/javascript; charset=UTF-8" if rel.endswith(".js") else "text/html; charset=UTF-8")
            generated_record = {
                "route": route,
                "static_url": static_url(base_path, rel),
                "output_path": rel,
                "source_offline_path": None,
                "source_manifest_sha256": None,
                "source_manifest_length": None,
                "source_sha256": None,
                "source_length": None,
                "derived_sha256": sha256_bytes(data),
                "derived_length": len(data),
                "mime": mime,
                "kind": kind,
                "role": "github_pages_support",
                "transformed": True,
            }
            # A frozen placeholder may already occupy the final pathname
            # (notably __offline/missing.html).  Keep one provenance record per
            # emitted path and retain its source SHA/length while recording the
            # generated Pages representation as the derived bytes.
            prior = next((item for item in provenance if item.get("output_path") == rel), None)
            if prior is None:
                provenance.append(generated_record)
            else:
                source_fields = {
                    key: prior.get(key)
                    for key in ("source_offline_path", "source_manifest_sha256", "source_manifest_length", "source_sha256", "source_length")
                }
                prior.update(generated_record)
                prior.update(source_fields)
            if kind == "related_images_index":
                stats["related_images_index"] += 1

        # Keep GitHub Pages from treating the generated ``__offline`` support
        # tree as a Jekyll input.  This marker is metadata only and contains no
        # source entity bytes.
        nojekyll = b""
        (partial / ".nojekyll").write_bytes(nojekyll)
        provenance.append({"route": "/.nojekyll", "static_url": static_url(base_path, ".nojekyll"), "output_path": ".nojekyll", "source_offline_path": None, "source_manifest_sha256": None, "source_manifest_length": None, "source_sha256": None, "source_length": None, "derived_sha256": sha256_bytes(nojekyll), "derived_length": 0, "mime": "application/octet-stream", "kind": "pages_metadata", "role": "github_pages_jekyll_bypass", "transformed": True})

        readme = ("# WOW Encyclopedia historical Pages mirror\n\n"
                  "This is an unofficial educational archive reconstruction based on 2008-05-12, "
                  "not affiliated with Blizzard. "
                  "It is a static GitHub Pages export under the project path; it performs no external fetching "
                  "and collects no user data. The archive retains known gaps and "
                  "does not claim a complete reconstruction.\n\n"
                  "The source `offline/site` and build manifest remain the frozen provenance inputs. HTML/XML "
                  "pages are emitted as UTF-8 HTML variants so GitHub Pages can parse them, while binary assets "
                  "are copied byte-for-byte.\n")
        # ``Path.write_text`` uses the host newline policy on Windows.  The
        # provenance hash is over the exact published bytes, so write UTF-8
        # explicitly to keep LF stable across hosts.
        readme_data = readme.encode("utf-8")
        (partial / "README.md").write_bytes(readme_data)
        provenance.append({"route": "/README.md", "static_url": static_url(base_path, "README.md"), "output_path": "README.md", "source_offline_path": None, "source_manifest_sha256": None, "source_manifest_length": None, "source_sha256": None, "source_length": None, "derived_sha256": sha256_bytes(readme_data), "derived_length": len(readme_data), "mime": "text/markdown; charset=UTF-8", "kind": "pages_readme", "role": "pages_documentation", "transformed": True})

        provenance_payload = {
            "schema": "github-pages-export-provenance/v1",
            "generated_at": utc_now(),
            "anchor_timestamp": manifest.get("anchor_timestamp"),
            "base_path": base_path,
            "source_site": str(source_site.relative_to(workspace_root).as_posix()),
            "source_manifest": str(manifest_path.relative_to(workspace_root).as_posix()),
            "source_manifest_sha256": manifest_sha,
            "files": provenance,
            "stats": dict(stats) | {
                "source_records": len(records),
                "image_overlay_records": len(overlays),
                "primary_image_overlay_records": len(primary_overlays),
                "supplement_image_overlay_records": len(supplement_overlays),
                "output_files": len(provenance),
                "route_aliases": len(aliases),
            },
            "security": {"external_fetches": False, "project_prefix": base_path, "source_unchanged": True, "path_traversal_rejected": True},
        }
        if guide_preview_bundle is not None:
            provenance_payload["guide_previews"] = guide_preview_bundle.provenance()
        if guide_image_collection_bundle is not None:
            provenance_payload["guide_image_collections"] = guide_image_collection_bundle.provenance()
        if flash_bundle is not None:
            provenance_payload["flash_exhibits"] = flash_bundle
        if blizzcast_bundle is not None:
            provenance_payload["blizzcast_reading"] = {
                "source_map_sha256": blizzcast_map_sha,
                "sources": blizzcast_bundle.source_records,
                "origin_routes": blizzcast_bundle.origin_routes,
                "unrestored_resources": [
                    {key: item[key] for key in ("source_entity_id", "kind", "requested_url")}
                    for item in blizzcast_bundle.dependency_inventory
                    if not item["restored"] and item["kind"] in {"image", "audio", "stylesheet", "object"}
                ],
                "presentation": "Five static reading pages; May 15 home/archive sources marked as later supplements",
            }
        if talent_icon_bundle is not None:
            provenance_payload["related_talent_icons"] = {
                "source": dict(talent_icon_bundle.source_metadata),
                "icon_count": len(talent_icon_bundle.assets),
                "class_counts": dict(talent_icon_bundle.per_class_counts),
                "catalog_path": talent_icon_bundle.catalog_relative,
                "source_map_sha256": talent_icon_bundle.map_sha256,
                "original_2008_images_recovered": 0,
            }
        if layout_bundle is not None:
            provenance_payload["layout_compatibility_reuse"] = {
                "classification": "layout_compatibility_reuse",
                "source_map_sha256": layout_bundle.map_sha256,
                "decision_sha256": layout_bundle.decision_sha256,
                "source_manifest_sha256": layout_bundle.source_manifest_sha256,
                "reused_target_paths": len(layout_bundle.route_reuses),
                "new_image_payloads": 0,
                "target_original_images_recovered": 0,
                "records": list(layout_bundle.public_records),
            }
        prov_data = (json.dumps(provenance_payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        (partial / "export-provenance.json").write_bytes(prov_data)
        after_workspace = workspace_size(workspace_root, output) if max_bytes is not None else None
        free_after = shutil.disk_usage(output.parent).free
        if (max_bytes is not None and after_workspace >= max_bytes) or free_after < min_free_bytes:
            raise PagesExportError(f"budget exceeded after export: workspace={after_workspace}, free={free_after}")
        promotion_attempted = True
        _promote_partial_output(partial, output)
        return {
            "output": str(output),
            "output_files": len(provenance),
            "manifest_sha256": manifest_sha,
            "base_path": base_path,
            "workspace_bytes": after_workspace,
            "disk_free_bytes": free_after,
            "estimated_bytes": estimate,
            "stats": dict(stats) | {
                "source_records": len(records),
                "image_overlay_records": len(overlays),
                "primary_image_overlay_records": len(primary_overlays),
                "supplement_image_overlay_records": len(supplement_overlays),
            },
        }
    except Exception:
        if not promotion_attempted:
            shutil.rmtree(partial, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH)
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help="Optional total workspace limit; the disk free-space reserve always applies")
    parser.add_argument("--min-free-bytes", type=int, default=DEFAULT_MIN_FREE_BYTES)
    parser.add_argument("--image-source-map", dest="image_source_maps", action="append", type=Path, default=[])
    parser.add_argument("--supplement-image-source-map", dest="supplement_image_source_maps", action="append", type=Path, default=[])
    parser.add_argument(
        "--flash-runtime-archive", type=Path, default=None,
        help="Optional hash-pinned Ruffle 0.7.1 self-hosted ZIP for three preserved Flash exhibits",
    )
    parser.add_argument(
        "--blizzcast-source-map", type=Path, default=None,
        help="Optional accepted five-source BlizzCast map for static historical reading pages",
    )
    parser.add_argument(
        "--related-talent-icon-map", type=Path, default=None,
        help="Optional pinned same-path talent icons from a separately attributed later repository",
    )
    parser.add_argument(
        "--source16-layout-map", type=Path, default=None,
        help="Optional accepted same-site layout route reuses for two Source16 pages",
    )
    parser.add_argument(
        "--allow-later-image-supplements",
        action="store_true",
        help="Accept explicit supplement images captured after 2008 when their source-map class is post_2008",
    )
    parser.add_argument(
        "--guide-preview-map",
        type=Path,
        default=None,
        help="Optional strict map of accepted guide-page previews to insert on their five gallery pages",
    )
    parser.add_argument(
        "--guide-image-collection-map",
        type=Path,
        default=None,
        help="Optional strict map of validated guide-image supplement collections for guide and gallery pages",
    )
    args = parser.parse_args(argv)
    try:
        result = export_pages(output=args.output, source_site=args.site, manifest_path=args.manifest, base_path=args.base_path, max_bytes=args.max_bytes, min_free_bytes=args.min_free_bytes, image_source_maps=args.image_source_maps, supplement_image_source_maps=args.supplement_image_source_maps, allow_later_image_supplements=args.allow_later_image_supplements, guide_preview_map=args.guide_preview_map, guide_image_collection_map=args.guide_image_collection_map, flash_runtime_archive=args.flash_runtime_archive, blizzcast_source_map=args.blizzcast_source_map, related_talent_icon_map=args.related_talent_icon_map, source16_layout_map=args.source16_layout_map)
    except PagesExportError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


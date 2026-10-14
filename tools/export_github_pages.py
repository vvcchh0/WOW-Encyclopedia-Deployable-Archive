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


class PagesExportError(RuntimeError):
    """Raised when a frozen source or safe output invariant fails."""


HTML_KINDS = {"html", "menu_html"}
TEXT_KINDS = HTML_KINDS | {"css", "js", "xsl", "xml", "legacy_component", "support"}
_ROOT_LITERAL_RE = re.compile(
    r"(?P<quote>['\"])(?P<url>/[^'\"\s<>]+)(?P<trailing>\s*)(?P=quote)"
)
_XML_BARE_AMP_RE = re.compile(
    r"&(?!#(?:x[0-9A-Fa-f]+|[0-9]+);|(?:amp|lt|gt|quot|apos);)"
)


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
_SUPPLEMENT_OVERLAY_URL_HOSTS = _OVERLAY_URL_HOSTS | {"www.wow-europe.com", "wow-europe.com"}
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
    host = (parsed.hostname or "").casefold().rstrip(".")
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


def _overlay_temporal_class(actual_dt: datetime, anchor_dt: datetime) -> str:
    year_start = datetime(2008, 1, 1)
    year_end = datetime(2008, 12, 31, 23, 59, 59)
    if actual_dt < year_start:
        return "pre_2008"
    if actual_dt <= anchor_dt:
        return "baseline_2008"
    if actual_dt <= year_end:
        return "late_2008"
    raise PagesExportError(f"image supplement capture is after 2008: {actual_dt:%Y%m%d%H%M%S}")


def _load_image_overlay_maps(
    image_source_maps: list[Path] | tuple[Path, ...],
    *,
    workspace_root: Path,
    anchor_timestamp: str,
    frozen_routes: set[str],
    frozen_static_paths: set[str],
    supplement: bool,
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
            actual = str(item.get("actual_timestamp") or "")
            indexed = str(item.get("indexed_capture_timestamp") or "")
            if not re.fullmatch(r"\d{14}", actual) or not re.fullmatch(r"\d{14}", indexed) or actual != indexed:
                raise PagesExportError(f"{label} capture timestamp is invalid or differs: {actual!r}/{indexed!r}")
            try:
                actual_dt = datetime.strptime(actual, "%Y%m%d%H%M%S")
                indexed_dt = datetime.strptime(indexed, "%Y%m%d%H%M%S")
            except ValueError as exc:
                raise PagesExportError(f"{label} capture timestamp is not a real date: {actual!r}/{indexed!r}") from exc
            if indexed_dt != actual_dt:
                raise PagesExportError(f"{label} capture timestamp is invalid or differs: {actual!r}/{indexed!r}")
            if supplement:
                temporal_class = _overlay_temporal_class(actual_dt, anchor_dt)
                declared_class = str(item.get("temporal_class") or "")
                if declared_class != temporal_class:
                    raise PagesExportError(
                        f"{label} temporal_class does not match capture date: {declared_class!r}/{temporal_class!r}"
                    )
            else:
                if not _OVERLAY_TIMESTAMP_RE.fullmatch(actual) or actual_dt.year != 2008 or actual_dt > anchor_dt:
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
    )


def load_supplement_image_overlays(
    supplement_image_source_maps: list[Path] | tuple[Path, ...],
    *,
    workspace_root: Path,
    anchor_timestamp: str,
    frozen_routes: set[str],
    frozen_static_paths: set[str],
) -> tuple[list[dict[str, Any]], int]:
    """Validate explicit 2008 related-site and late-capture image overlays."""

    return _load_image_overlay_maps(
        supplement_image_source_maps,
        workspace_root=workspace_root,
        anchor_timestamp=anchor_timestamp,
        frozen_routes=frozen_routes,
        frozen_static_paths=frozen_static_paths,
        supplement=True,
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
    ) -> None:
        self.route_to_static = route_to_static
        self.aliases = aliases
        self.origin_index = origin_index
        self.base_path = base_path
        # ``offline_mirror.rewrite_css`` uses this explicit capability only
        # for frozen missing-image placeholders.  Its normal loopback
        # Localizer behavior remains unchanged.
        self.relocalize_image_placeholders = True

    def _static_for_route(self, route: str) -> str | None:
        return self.route_to_static.get(route) or self.aliases.get(route)

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
        after = text[match.end() :].lstrip()
        if after.startswith("+") and not raw.casefold().startswith(("/__offline/uncollected", "/search/")):
            return match.group(0)
        local = localizer.localize(raw, base_url=base_url, context=_context_for_literal(raw), recorder=recorder)
        q = match.group("quote")
        return q + local.replace(q, "%22") + match.group("trailing") + q

    return _ROOT_LITERAL_RE.sub(replace, text)


_GALLERY_ADDSHOTS_RE = re.compile(
    r"(?P<call>\baddshots\s*\(\s*)"
    r"(?P<quote>['\"])(?P<directory>/[^'\"\r\n<>]*?/)(?P=quote)"
    r"(?P<comma1>\s*,\s*)(?P<filequote>['\"])(?P<filename>ss)(?P=filequote)"
    r"(?P<comma2>\s*,\s*)(?P<count>numShots)\b",
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


def inject_html_runtime(text: str, *, base_path: str, source_sha: str) -> str:
    insertion = (
        f'\n<meta http-equiv="Content-Security-Policy" content="{html.escape(PAGES_CSP, quote=True)}">'
        f'\n<script src="{base_path}__offline/pages_runtime.js"></script>\n'
    )
    if not re.search(r"pages_runtime\.js", text, re.I):
        head = re.search(r"<head\b[^>]*>", text, flags=re.I)
        if head:
            text = text[: head.end()] + insertion + text[head.end() :]
        else:
            text = "<!doctype html><html><head>" + insertion + "</head><body>" + text + "</body></html>"
    banner = (
        '<div id="__offline-pages-banner" style="background:#241b0b;color:#f7e7b0;'
        'font:12px/1.4 Arial,sans-serif;padding:6px 10px;text-align:center;position:relative;z-index:2147483647">'
        "Unofficial historical educational preservation (not affiliated with Blizzard) • "
        "2008-05-12 21:00:44 snapshot • "
        "no user data collection</div>"
    )
    if "__offline-pages-banner" not in text:
        body = re.search(r"<body\b[^>]*>", text, flags=re.I)
        if body:
            text = text[: body.end()] + "\n" + banner + text[body.end() :]
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
    ready.then(function () {{ wrapSearchCall(); mapExistingImages(); repair404(); }});
    setTimeout(wrapExactTopic, 0);
    setTimeout(wrapExactTopic, 250);
    setTimeout(wrapSearchCall, 0);
    setTimeout(wrapSearchCall, 250);
    setTimeout(wrapSearchCall, 1000);
    setTimeout(mapExistingImages, 250);
}}(window, document));
"""


def generated_uncollected(base_path: str, title: str = "Offline route") -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<meta http-equiv="Content-Security-Policy" content="{html.escape(PAGES_CSP, quote=True)}">
<script src="{base_path}__offline/pages_runtime.js"></script></head><body>
<div id="__offline-pages-banner" style="background:#241b0b;color:#f7e7b0;padding:6px 10px;font:12px Arial">Unofficial historical educational preservation (not affiliated with Blizzard) • 2008-05-12 21:00:44 • no user data collection</div>
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
<div id="__offline-pages-banner" style="background:#241b0b;color:#f7e7b0;padding:6px 10px;font:12px Arial">Unofficial historical educational preservation (not affiliated with Blizzard) • 2008-05-12 21:00:44 • no user data collection</div>
<p>Redirecting to <a href="{escaped}">{escaped}</a>.</p></body></html>"""


def generated_related_images_index(base_path: str, overlays: list[dict[str, Any]]) -> str:
    """Render a small local catalog for explicit non-primary image supplements."""

    cards: list[str] = []
    for overlay in overlays:
        image_url = static_url(base_path, str(overlay["relative"]))
        original_url = str(overlay["original_url"])
        capture_date = datetime.strptime(str(overlay["actual_timestamp"]), "%Y%m%d%H%M%S")
        captured = capture_date.strftime("%Y-%m-%d %H:%M:%S UTC")
        temporal_label = {"baseline_2008": "2008 baseline", "pre_2008": "Earlier capture", "late_2008": "Later 2008 capture"}[str(overlay["temporal_class"])]
        cards.append(
            f"<article class=\"related-image-card\" data-temporal-class=\"{html.escape(str(overlay['temporal_class']), quote=True)}\">"
            f"<a href=\"{html.escape(image_url, quote=True)}\"><img loading=\"lazy\" src=\"{html.escape(image_url, quote=True)}\" alt=\"{html.escape(original_url, quote=True)}\"></a>"
            f"<p><code>{html.escape(str(overlay['origin_namespace']))}</code> "
            f"<time datetime=\"{capture_date:%Y-%m-%dT%H:%M:%SZ}\">{captured}</time> "
            f"<span>{temporal_label}</span></p>"
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
    before_workspace = workspace_size(workspace_root, output)
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
    )
    overlays = primary_overlays + supplement_overlays
    overlay_bytes = primary_overlay_bytes + supplement_overlay_bytes
    estimate = output_estimate(records, overlay_bytes)
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
    aliases: dict[str, str] = {}
    alias_routes: dict[str, str] = {}
    for alias, target in raw_aliases.items():
        alias = safe_route(str(alias))
        target = safe_route(str(target))
        target_url = route_to_static.get(target)
        if target_url:
            aliases[alias] = target_url
            alias_routes[alias] = target
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
    localizer = PagesLocalizer(route_to_static=route_lookup, aliases=alias_routes, origin_index=origin_index, base_path=base_path)
    provenance: list[dict[str, Any]] = []
    stats: Counter[str] = Counter()
    partial.mkdir(parents=True, exist_ok=False)
    try:
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
            # A few frozen support placeholders are explicitly typed as
            # generated_placeholder but still carry text/html MIME.  Emit
            # those through the same UTF-8/CSP/banner path so every static
            # HTML response remains self-describing on Pages.
            if kind in HTML_KINDS or is_html_record(record):
                text = data.decode(mirror.charset_for(str(record.get("mime") or ""), data), errors="replace")
                text = mirror.rewrite_html(text, base_url=base_url, localizer=localizer, recorder=recorder, source_sha=source_sha, compat_assets=[])
                text = rename_flash_codebase_metadata(text, recorder=recorder)
                text = rewrite_iframe_fallbacks(text, base_url=base_url, localizer=localizer, recorder=recorder)
                text = rewrite_inline_scripts(text, base_url=base_url, localizer=localizer, recorder=recorder)
                text = normalize_html_charset(text)
                text = disable_sensitive_forms(text, route=route)
                text = historical_exhibits.transform_derived_page(text, route, base_path=base_path)
                text = normalize_html_prolog(text)
                text = inject_html_runtime(text, base_path=base_path, source_sha=source_sha)
                derived = text.encode("utf-8")
                stats["html_derived"] += 1
            elif kind == "css" or (kind == "support" and source.suffix.casefold() == ".css"):
                text = data.decode(mirror.charset_for(str(record.get("mime") or ""), data), errors="replace")
                derived = mirror.rewrite_css(text, base_url=base_url, localizer=localizer, recorder=recorder).encode("utf-8")
                stats["css_derived"] += 1
            elif kind == "js" or (kind == "support" and source.suffix.casefold() in {".js", ".htc"}):
                text = data.decode(mirror.charset_for(str(record.get("mime") or ""), data), errors="replace")
                text = mirror.rewrite_script(text, base_url=base_url, localizer=localizer, recorder=recorder)
                text = rewrite_root_literals(text, base_url=base_url, localizer=localizer, recorder=recorder)
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
            provenance.append(item)

        for overlay in overlays:
            route = str(overlay["route"])
            relative = str(overlay["relative"])
            out = partial / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            data = bytes(overlay["data"])
            out.write_bytes(data)
            provenance.append({
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
            })
            stats["image_overlay"] += 1

        # Concrete redirect files for aliases that Pages cannot infer from a
        # request path.  Existing index files are reused rather than replaced.
        existing = {item["output_path"] for item in provenance}
        for alias, target_url in list(aliases.items()):
            if alias in {"/", "/index.html"} or alias.endswith("/"):
                continue
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
            provenance.append({"route": alias, "static_url": aliases[alias], "output_path": rel, "source_offline_path": None, "source_manifest_sha256": None, "source_manifest_length": None, "source_sha256": None, "source_length": None, "derived_sha256": sha256_bytes(data), "derived_length": len(data), "mime": "text/html; charset=UTF-8", "kind": "generated_redirect", "role": "route_alias", "transformed": True})
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
                  "This is an unofficial educational preservation of the 2008-05-12 21:00:44 capture, "
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
        prov_data = (json.dumps(provenance_payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        (partial / "export-provenance.json").write_bytes(prov_data)
        after_workspace = workspace_size(workspace_root, output)
        free_after = shutil.disk_usage(output.parent).free
        if (max_bytes is not None and after_workspace >= max_bytes) or free_after < min_free_bytes:
            raise PagesExportError(f"budget exceeded after export: workspace={after_workspace}, free={free_after}")
        partial.replace(output)
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
    args = parser.parse_args(argv)
    try:
        result = export_pages(output=args.output, source_site=args.site, manifest_path=args.manifest, base_path=args.base_path, max_bytes=args.max_bytes, min_free_bytes=args.min_free_bytes, image_source_maps=args.image_source_maps, supplement_image_source_maps=args.supplement_image_source_maps)
    except PagesExportError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

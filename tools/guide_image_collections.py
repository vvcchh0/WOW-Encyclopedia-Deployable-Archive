#!/usr/bin/env python3
"""Validate and render the independent guide-image collection sections.

Guide-image collections are explicit supplement overlays whose original
routes are known from the preserved guide literals.  They are shown in both
the guide and its related gallery page.  This module never creates an
``ssN`` alias, changes ``addshots``/pagination JavaScript, or accepts a
collection image that was not already validated by the supplement overlay
loader.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


class GuideImageCollectionError(ValueError):
    """Raised when a guide-image collection map is incomplete or unsafe."""


EXPECTED_COLLECTIONS: dict[str, tuple[str, str, str, int, str]] = {
    "love-is-in-the-air": (
        "Love is in the Air",
        "/info/events/loveisintheair/index.html",
        "/info/events/loveisintheair/gallery.html",
        12,
        "/info/events/loveisintheair/images/ss{number}.jpg",
    ),
    "lunar-festival": (
        "Lunar Festival",
        "/info/events/lunarnewyears/index.html",
        "/info/events/lunarnewyears/gallery.html",
        21,
        "/info/events/lunarnewyears/images/ss{number}.jpg",
    ),
    "world-pvp": (
        "World PvP",
        "/pvp/worldpvp/index.xml",
        "/pvp/worldpvp/worldpvp-gallery.html",
        16,
        "/pvp/worldpvp/images/ss{number}.jpg",
    ),
}

_MIN_CAPTURE = "20000101000000"
_MAX_GROUPS = len(EXPECTED_COLLECTIONS)


@dataclass(frozen=True)
class GuideImage:
    route: str
    original: str
    sha256: str
    length: int
    capture_timestamp: str
    static_url: str


@dataclass(frozen=True)
class GuideImageCollectionGroup:
    group_id: str
    label: str
    guide_route: str
    gallery_route: str
    guide_static_url: str
    gallery_static_url: str
    images: tuple[GuideImage, ...]


@dataclass(frozen=True)
class GuideImageCollectionBundle:
    map_path: Path
    map_sha256: str
    source_manifest_path: str
    source_manifest_sha256: str
    source_acceptances: tuple[dict[str, str], ...]
    anchor_timestamp: str
    groups: tuple[GuideImageCollectionGroup, ...]
    map_schema: str = "wow-recovery.guide-image-collections.v1"

    @property
    def image_count(self) -> int:
        return sum(len(group.images) for group in self.groups)

    def group_for_route(self, route: str) -> tuple[GuideImageCollectionGroup, str] | None:
        for group in self.groups:
            if group.guide_route == route:
                return group, "guide"
            if group.gallery_route == route:
                return group, "gallery"
        return None

    def provenance(self) -> dict[str, Any]:
        return {
            "schema": "github-pages-guide-image-collections-provenance/v1",
            "source_map": self.map_path.as_posix(),
            "source_map_sha256": self.map_sha256,
            "source_manifest": self.source_manifest_path,
            "source_manifest_sha256": self.source_manifest_sha256,
            "source_acceptances": [dict(item) for item in self.source_acceptances],
            "anchor_timestamp": self.anchor_timestamp,
            "group_count": len(self.groups),
            "image_count": self.image_count,
            "groups": [
                {
                    "group_id": group.group_id,
                    "label": group.label,
                    "guide_route": group.guide_route,
                    "gallery_route": group.gallery_route,
                    "image_count": len(group.images),
                    "images": [
                        {
                            "route": image.route,
                            "original": image.original,
                            "static_url": image.static_url,
                            "sha256": image.sha256,
                            "length": image.length,
                            "actual_capture_timestamp": image.capture_timestamp,
                        }
                        for image in group.images
                    ],
                }
                for group in self.groups
            ],
        }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside(path: Path, root: Path, *, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise GuideImageCollectionError(f"{label} escapes workspace: {path}") from exc
    return resolved


def _read_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GuideImageCollectionError(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise GuideImageCollectionError(f"{label} must contain an object")
    return value


def _binding(root: Path, raw: Any, *, label: str) -> tuple[Path, str]:
    if not isinstance(raw, dict):
        raise GuideImageCollectionError(f"{label} must be an object")
    relative = raw.get("path")
    expected = str(raw.get("sha256") or "").casefold()
    if not isinstance(relative, str) or not relative:
        raise GuideImageCollectionError(f"{label}.path is missing")
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise GuideImageCollectionError(f"{label}.sha256 is invalid")
    path = _inside(root / relative, root, label=label)
    if not path.is_file():
        raise GuideImageCollectionError(f"{label} file is missing: {path}")
    actual = _sha256(path)
    if actual != expected:
        raise GuideImageCollectionError(f"{label} SHA-256 mismatch")
    return path, actual


def _route(raw: Any, *, label: str) -> str:
    if not isinstance(raw, str) or not raw.startswith("/"):
        raise GuideImageCollectionError(f"{label} is not an absolute route")
    if "\\" in raw or "\x00" in raw or "//" in raw or ".." in raw.split("/"):
        raise GuideImageCollectionError(f"{label} is unsafe: {raw!r}")
    return raw


def _timestamp(raw: Any, *, label: str) -> str:
    value = str(raw or "")
    if not re.fullmatch(r"\d{14}", value):
        raise GuideImageCollectionError(f"{label} is not a 14-digit timestamp")
    try:
        datetime.strptime(value, "%Y%m%d%H%M%S")
    except ValueError as exc:
        raise GuideImageCollectionError(f"{label} is not a real timestamp") from exc
    return value


def _original_parts(raw: Any, *, label: str) -> tuple[str, str]:
    if not isinstance(raw, str) or not raw:
        raise GuideImageCollectionError(f"{label} original is missing")
    try:
        parsed = urllib.parse.urlsplit(raw)
        port = parsed.port
    except ValueError as exc:
        raise GuideImageCollectionError(f"{label} original URL is invalid") from exc
    scheme = parsed.scheme.casefold()
    host = (parsed.hostname or "").casefold().rstrip(".")
    if scheme not in {"http", "https"} or host != "www.worldofwarcraft.com":
        raise GuideImageCollectionError(f"{label} original URL has an unapproved origin")
    default_port = (scheme == "http" and port in {None, 80}) or (scheme == "https" and port in {None, 443})
    if not default_port or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise GuideImageCollectionError(f"{label} original URL has unsafe authority or suffix")
    path = parsed.path or "/"
    if not path.startswith("/") or "\\" in path or "\x00" in path or ".." in path.split("/"):
        raise GuideImageCollectionError(f"{label} original URL path is unsafe")
    return raw, f"{scheme}://www.worldofwarcraft.com{path}"


def _canonical_original(raw: Any, *, label: str) -> str:
    """Return the comparison identity while preserving the source literal elsewhere."""

    return _original_parts(raw, label=label)[1]


def _record_is_page(record: dict[str, Any], *, label: str, xml_ok: bool) -> None:
    kind = str(record.get("kind") or "").casefold()
    mime = str(record.get("mime") or "").casefold()
    allowed_kinds = {"html", "menu_html"} | ({"xml", "legacy_component"} if xml_ok else set())
    allowed_mimes = ("text/html", "application/xhtml", "application/xml", "text/xml") if xml_ok else ("text/html", "application/xhtml")
    if kind not in allowed_kinds and not mime.startswith(allowed_mimes):
        raise GuideImageCollectionError(f"{label} is not a browsable HTML/XML manifest page")


def _actual_capture(item: dict[str, Any], *, label: str) -> str:
    return _timestamp(
        item.get("actual_capture_timestamp", item.get("actualcapture", item.get("capture_timestamp"))),
        label=label,
    )


def _accepted_image_records(
    root: Path,
    receipt_path: Path,
    receipt: dict[str, Any],
) -> dict[tuple[str, str | None, str], dict[str, Any]]:
    if receipt.get("accepted") is not True:
        raise GuideImageCollectionError(f"source acceptance is not accepted: {receipt_path}")
    raw_items = receipt.get("accepted_images")
    if not isinstance(raw_items, list):
        raise GuideImageCollectionError(f"source acceptance has no accepted_images list: {receipt_path}")
    result: dict[tuple[str, str | None, str], dict[str, Any]] = {}
    identity_records: dict[tuple[str, str | None], dict[str, Any]] = {}
    for index, raw in enumerate(raw_items):
        label = f"{receipt_path.name}.accepted_images[{index}]"
        if not isinstance(raw, dict) or raw.get("accepted") is not True:
            raise GuideImageCollectionError(f"{label} is not accepted")
        original_literal, original = _original_parts(raw.get("original"), label=label)
        route_raw = raw.get("route")
        route = _route(route_raw, label=f"{label}.route") if route_raw is not None else None
        sha = str(raw.get("sha256") or "").casefold()
        if not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise GuideImageCollectionError(f"{label}.sha256 is invalid")
        try:
            length = int(raw.get("length"))
        except (TypeError, ValueError) as exc:
            raise GuideImageCollectionError(f"{label}.length is invalid") from exc
        if length < 1:
            raise GuideImageCollectionError(f"{label}.length is invalid")
        capture = _actual_capture(raw, label=f"{label}.actual_capture_timestamp")
        payload_raw = raw.get("private_payload_path") or raw.get("local_path") or raw.get("payload_path")
        if payload_raw is not None:
            payload = _inside(root / str(payload_raw), root, label=f"{label}.payload")
            if not payload.is_file():
                raise GuideImageCollectionError(f"{label}.payload is missing: {payload}")
            payload_data = payload.read_bytes()
            if len(payload_data) != length or hashlib.sha256(payload_data).hexdigest() != sha:
                raise GuideImageCollectionError(f"{label}.payload SHA/length mismatch")
        identity_key = (original, route)
        previous = identity_records.get(identity_key)
        if previous is not None and (previous["sha256"], previous["length"], previous["capture_timestamp"]) != (sha, length, capture):
            raise GuideImageCollectionError(f"{label} conflicts with a duplicate accepted image")
        record = {
            "original": original,
            "original_literal": original_literal,
            "route": route,
            "sha256": sha,
            "length": length,
            "capture_timestamp": capture,
            "receipt_path": receipt_path,
        }
        identity_records[identity_key] = record
        result[(original, route, sha)] = record
    return result


def load_guide_image_collection_map(
    map_path: Path,
    *,
    workspace_root: Path,
    manifest_path: Path,
    manifest: dict[str, Any],
    overlays: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    route_to_static: dict[str, str],
    base_path: str = "",
) -> GuideImageCollectionBundle:
    """Load a strict v1 collection map after supplement overlays are loaded."""

    root = workspace_root.resolve()
    map_path = _inside(Path(map_path), root, label="guide image collection map")
    if not map_path.is_file():
        raise GuideImageCollectionError(f"guide image collection map is missing: {map_path}")
    payload = _read_json(map_path, label="guide image collection map")
    if payload.get("schema") != "wow-recovery.guide-image-collections.v1":
        raise GuideImageCollectionError("guide image collection map schema is unsupported")
    map_sha = _sha256(map_path)

    manifest_path = manifest_path.resolve()
    manifest_ref, manifest_sha = _binding(root, payload.get("source_manifest"), label="source_manifest")
    if manifest_ref != manifest_path or manifest_sha != _sha256(manifest_path):
        raise GuideImageCollectionError("guide image collection map source_manifest does not bind to exporter manifest")
    anchor = _timestamp(manifest.get("anchor_timestamp"), label="manifest anchor_timestamp")
    map_anchor = _timestamp(payload.get("anchor_timestamp"), label="guide image map anchor_timestamp")
    if map_anchor != anchor:
        raise GuideImageCollectionError("guide image map anchor_timestamp differs from manifest")

    raw_acceptances = payload.get("source_acceptances")
    if isinstance(raw_acceptances, dict):
        raw_acceptances = [raw_acceptances]
    if not isinstance(raw_acceptances, list) or not raw_acceptances:
        raise GuideImageCollectionError("guide image map must bind one or more source_acceptances")
    source_acceptances: list[dict[str, str]] = []
    accepted_records: dict[Path, dict[tuple[str, str | None, str], dict[str, Any]]] = {}
    receipt_paths: set[Path] = set()
    for index, raw_ref in enumerate(raw_acceptances):
        receipt_path, receipt_sha = _binding(root, raw_ref, label=f"source_acceptances[{index}]")
        if receipt_path in receipt_paths:
            raise GuideImageCollectionError("source_acceptances contains a duplicate receipt")
        receipt_paths.add(receipt_path)
        receipt = _read_json(receipt_path, label=f"source acceptance {receipt_path}")
        receipt_records = _accepted_image_records(root, receipt_path, receipt)
        accepted_records[receipt_path] = receipt_records
        source_acceptances.append({"path": receipt_path.relative_to(root).as_posix(), "sha256": receipt_sha})

    route_records = {str(item.get("route")): item for item in (manifest.get("files") or []) if isinstance(item, dict)}
    overlay_by_route: dict[str, dict[str, Any]] = {}
    for overlay in overlays:
        route = str(overlay.get("route") or "")
        if route in overlay_by_route and overlay_by_route[route].get("source_sha256") != overlay.get("source_sha256"):
            raise GuideImageCollectionError(f"overlay route has conflicting sources: {route}")
        overlay_by_route[route] = overlay

    raw_groups = payload.get("groups")
    if not isinstance(raw_groups, list) or not 1 <= len(raw_groups) <= _MAX_GROUPS:
        raise GuideImageCollectionError("guide image map must contain one to three groups")
    seen_groups: set[str] = set()
    seen_pages: set[str] = set()
    seen_images: set[str] = set()
    groups: list[GuideImageCollectionGroup] = []
    for group_index, raw_group in enumerate(raw_groups):
        label_prefix = f"groups[{group_index}]"
        if not isinstance(raw_group, dict):
            raise GuideImageCollectionError(f"{label_prefix} is not an object")
        group_id = str(raw_group.get("group_id") or "")
        if group_id not in EXPECTED_COLLECTIONS or group_id in seen_groups:
            raise GuideImageCollectionError(f"{label_prefix} group identity is invalid or duplicated")
        seen_groups.add(group_id)
        expected_label, expected_guide, expected_gallery, max_images, route_template = EXPECTED_COLLECTIONS[group_id]
        if raw_group.get("label") != expected_label or raw_group.get("guide_route") != expected_guide or raw_group.get("gallery_route") != expected_gallery:
            raise GuideImageCollectionError(f"{group_id} does not match its fixed guide/gallery identity")
        guide_route = _route(expected_guide, label=f"{group_id}.guide_route")
        gallery_route = _route(expected_gallery, label=f"{group_id}.gallery_route")
        if guide_route in seen_pages or gallery_route in seen_pages:
            raise GuideImageCollectionError(f"{group_id} duplicates a guide/gallery page")
        seen_pages.update({guide_route, gallery_route})
        guide_record = route_records.get(guide_route)
        gallery_record = route_records.get(gallery_route)
        if guide_record is None or gallery_record is None:
            raise GuideImageCollectionError(f"{group_id} guide/gallery route is absent from manifest")
        _record_is_page(guide_record, label=f"{group_id}.guide_route", xml_ok=guide_route.endswith((".xml", ".xml.html")))
        _record_is_page(gallery_record, label=f"{group_id}.gallery_route", xml_ok=False)
        guide_static = route_to_static.get(guide_route)
        gallery_static = route_to_static.get(gallery_route)
        if not guide_static or not gallery_static:
            raise GuideImageCollectionError(f"{group_id} guide/gallery route is absent from Pages route map")
        raw_images = raw_group.get("images")
        if not isinstance(raw_images, list) or not 1 <= len(raw_images) <= max_images:
            raise GuideImageCollectionError(f"{group_id}.images must contain one to {max_images} images")
        images: list[GuideImage] = []
        for image_index, raw_image in enumerate(raw_images):
            image_label = f"{group_id}.images[{image_index}]"
            if not isinstance(raw_image, dict):
                raise GuideImageCollectionError(f"{image_label} is not an object")
            route = _route(raw_image.get("route"), label=f"{image_label}.route")
            if route in seen_images:
                raise GuideImageCollectionError(f"{image_label}.route is duplicated")
            match = re.fullmatch(re.escape(route_template).replace(r"\{number\}", r"(\d+)"), route)
            if match is None or not 1 <= int(match.group(1)) <= max_images:
                raise GuideImageCollectionError(f"{image_label}.route is not an accepted exact full-image route")
            if "/thumb" in route.casefold() or "/ss/" in route.casefold() or not route.casefold().endswith(".jpg"):
                raise GuideImageCollectionError(f"{image_label}.route is not an exact full-image route")
            seen_images.add(route)
            original_literal, original = _original_parts(raw_image.get("original"), label=image_label)
            if urllib.parse.urlsplit(original).path != route:
                raise GuideImageCollectionError(f"{image_label}.original path does not match route")
            sha = str(raw_image.get("sha256") or "").casefold()
            if not re.fullmatch(r"[0-9a-f]{64}", sha):
                raise GuideImageCollectionError(f"{image_label}.sha256 is invalid")
            try:
                length = int(raw_image.get("length"))
            except (TypeError, ValueError) as exc:
                raise GuideImageCollectionError(f"{image_label}.length is invalid") from exc
            if length < 1:
                raise GuideImageCollectionError(f"{image_label}.length is invalid")
            capture = _actual_capture(raw_image, label=f"{image_label}.actual_capture_timestamp")
            if capture < _MIN_CAPTURE or capture > anchor:
                raise GuideImageCollectionError(f"{image_label}.capture is outside 2000-to-anchor window")
            acceptance_path_raw = raw_image.get("source_acceptance_path")
            if not isinstance(acceptance_path_raw, str) or not acceptance_path_raw:
                raise GuideImageCollectionError(f"{image_label}.source_acceptance_path is missing")
            acceptance_path = _inside(root / acceptance_path_raw, root, label=f"{image_label}.source_acceptance_path")
            if acceptance_path not in receipt_paths:
                raise GuideImageCollectionError(f"{image_label}.source_acceptance_path is not a bound receipt")
            receipt_records = accepted_records.get(acceptance_path, {})
            accepted = receipt_records.get((original, route, sha))
            if accepted is None:
                accepted = receipt_records.get((original, None, sha))
            if accepted is None or accepted["receipt_path"] != acceptance_path:
                raise GuideImageCollectionError(f"{image_label} is absent from the bound root accepted_images")
            if (accepted["sha256"], accepted["length"], accepted["capture_timestamp"]) != (sha, length, capture):
                raise GuideImageCollectionError(f"{image_label} differs from root accepted_images")
            overlay = overlay_by_route.get(route)
            if overlay is None:
                raise GuideImageCollectionError(f"{image_label} is absent from loaded supplement overlays")
            if overlay.get("supplement_strategy") != "explicit_supplement_image_overlay":
                raise GuideImageCollectionError(f"{image_label} did not come from a validated supplement map")
            overlay_original = _canonical_original(overlay.get("original_url"), label=f"{image_label}.overlay_original")
            if overlay_original != original or str(overlay.get("source_sha256") or "").casefold() != sha or int(overlay.get("source_length", -1)) != length or str(overlay.get("actual_timestamp") or "") != capture:
                raise GuideImageCollectionError(f"{image_label} differs from loaded overlay")
            data = overlay.get("data")
            if not isinstance(data, (bytes, bytearray)) or len(data) != length or hashlib.sha256(bytes(data)).hexdigest() != sha:
                raise GuideImageCollectionError(f"{image_label} loaded overlay bytes do not match")
            static_url = route_to_static.get(route)
            if not static_url:
                raise GuideImageCollectionError(f"{image_label} route is absent from Pages route map")
            images.append(GuideImage(route, original_literal, sha, length, capture, static_url))
        groups.append(GuideImageCollectionGroup(group_id, expected_label, guide_route, gallery_route, guide_static, gallery_static, tuple(images)))

    if len(seen_groups) != len(raw_groups):
        raise GuideImageCollectionError("guide image collection group conservation failed")
    return GuideImageCollectionBundle(
        map_path=map_path.relative_to(root),
        map_sha256=map_sha,
        source_manifest_path=manifest_ref.relative_to(root).as_posix(),
        source_manifest_sha256=manifest_sha,
        source_acceptances=tuple(source_acceptances),
        anchor_timestamp=anchor,
        groups=tuple(groups),
    )


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _display_capture(value: str) -> str:
    parsed = datetime.strptime(value, "%Y%m%d%H%M%S")
    return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")


def render_guide_image_section(group: GuideImageCollectionGroup, page_role: str) -> str:
    """Render one deterministic section for a guide or its related gallery."""

    if page_role not in {"guide", "gallery"}:
        raise GuideImageCollectionError(f"unsupported guide image page role: {page_role}")
    section_id = f"offline-guide-images-{_slug(group.group_id)}-{page_role}"
    guide_url = html.escape(group.guide_static_url, quote=True)
    cards: list[str] = []
    for index, image in enumerate(group.images, 1):
        image_url = html.escape(image.static_url, quote=True)
        route = html.escape(image.route, quote=True)
        cards.append(
            '<figure class="offline-guide-image-card">'
            f'<a href="{image_url}" data-guide-image-route="{route}" data-guide-image-original="{route}">'
            f'<img src="{image_url}" alt="{html.escape(group.label, quote=True)} guide image {index}" loading="lazy" '
            'style="display:block;max-width:100%;height:auto;">'
            "</a>"
            f'<figcaption>Captured {_display_capture(image.capture_timestamp)} · '
            f'<a href="{image_url}">Open original size</a></figcaption>'
            "</figure>"
        )
    return (
        f'<section id="{section_id}" class="offline-guide-image-collection" '
        f'data-guide-image-collection="{html.escape(group.group_id, quote=True)}" '
        f'data-guide-image-count="{len(group.images)}" '
        'style="box-sizing:border-box;margin:18px auto 24px;padding:16px;max-width:960px;'
        'border:1px solid #8d7542;background:#fff9e8;color:#2d2418;font:14px/1.45 Arial,sans-serif;">'
        '<style>'
        f'#{section_id} .offline-guide-image-heading{{margin:0 0 7px;color:#5a3e21;font:700 22px/1.2 Georgia,serif;}}'
        f'#{section_id} .offline-guide-image-note{{margin:0 0 11px;}}'
        f'#{section_id} .offline-guide-image-guide{{display:inline-block;margin:0 0 13px;color:#234c83;}}'
        f'#{section_id} .offline-guide-image-grid{{display:flex;flex-wrap:wrap;gap:12px;}}'
        f'#{section_id} .offline-guide-image-card{{box-sizing:border-box;width:min(100%,260px);margin:0;padding:8px;background:#fff;border:1px solid #c8b58e;}}'
        f'#{section_id} .offline-guide-image-card figcaption{{margin-top:6px;font-size:12px;}}'
        f'#{section_id} .offline-guide-image-card a{{color:#234c83;}}'
        "</style>"
        '<h2 class="offline-guide-image-heading">Guide images</h2>'
        f'<p class="offline-guide-image-note">Images preserved from the {html.escape(group.label)} guide. Open an image to view its original size.</p>'
        f'<a class="offline-guide-image-guide" href="{guide_url}">View guide page</a>'
        f'<div class="offline-guide-image-grid">{"".join(cards)}</div>'
        "</section>"
    )


def insert_guide_image_section(text: str, group: GuideImageCollectionGroup, page_role: str) -> str:
    """Insert one independent guide-image section immediately after ``<body>``."""

    section_id = f"offline-guide-images-{_slug(group.group_id)}-{page_role}"
    if len(re.findall(rf"id=[\"']{re.escape(section_id)}[\"']", text, flags=re.IGNORECASE)):
        raise GuideImageCollectionError(f"guide image section already exists: {section_id}")
    match = re.search(r"<body\b[^>]*>", text, flags=re.IGNORECASE)
    if match is None:
        raise GuideImageCollectionError(f"page has no body element: {group.group_id}/{page_role}")
    section = "\n" + render_guide_image_section(group, page_role) + "\n"
    derived = text[: match.end()] + section + text[match.end() :]
    if len(re.findall(rf"id=[\"']{re.escape(section_id)}[\"']", derived, flags=re.IGNORECASE)) != 1:
        raise GuideImageCollectionError(f"guide image section insertion count is not one: {section_id}")
    return derived


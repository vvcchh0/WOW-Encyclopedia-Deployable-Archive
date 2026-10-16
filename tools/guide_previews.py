#!/usr/bin/env python3
"""Validate and render the accepted guide-page preview collection.

The guide previews are existing manifest image routes.  This module never
creates a full-image alias, changes the dynamic gallery script, or copies image
bytes.  It only validates a curated map against the frozen manifest and
inserts a local preview section into the fixed gallery pages for the selected
map schema.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class GuidePreviewError(ValueError):
    """Raised when the curated guide-preview map is incomplete or unsafe."""


EXPECTED_GROUPS_V1: dict[str, tuple[str, str, str]] = {
    "fishing": ("Fishing", "/info/professions/fishing-gallery.html", "/info/professions/fishing.html"),
    "hallows-end": ("Hallow's End", "/info/events/hallowsend/gallery.html", "/info/events/hallowsend/index.html"),
    "brewfest": ("Brewfest", "/info/events/brewfest/gallery.html", "/info/events/brewfest/index.html"),
    "winters-veil": ("Winter's Veil", "/info/events/winterveil/gallery.html", "/info/events/winterveil/index.html"),
    "zulaman": ("Zul'Aman", "/info/dungeons/zulaman-gallery.html", "/info/dungeons/zulaman.xml"),
}

EXPECTED_GROUPS_V2: dict[str, tuple[str, str, str]] = {
    **EXPECTED_GROUPS_V1,
    "city-attacks": ("City Attacks", "/pvp/worldpvp/cityattacks-gallery.html", "/info/basics/pvpcombat.html"),
}

# Keep the historical public name bound to the strict v1 set.  The original
# five-group builder and callers importing this name must not gain City
# implicitly.
EXPECTED_GROUPS = EXPECTED_GROUPS_V1

CITY_PREVIEW_ROUTES = frozenset(
    {
        "/pvp/worldpvp/images/city/thumbs/thumb-1.jpg",
        "/pvp/worldpvp/images/city/thumbs/thumb-2.jpg",
        "/pvp/worldpvp/images/city/thumbs/thumb-3.jpg",
    }
)

_MAP_SPECS: dict[str, dict[str, Any]] = {
    "wow-recovery.guide-preview-source-map.v1": {
        "groups": EXPECTED_GROUPS_V1,
        "group_count": 5,
        "preview_count": 19,
        "version_label": "five",
    },
    "wow-recovery.guide-preview-source-map.v2": {
        "groups": EXPECTED_GROUPS_V2,
        "group_count": 6,
        "preview_count": 22,
        "version_label": "six",
    },
}


@dataclass(frozen=True)
class GuidePreview:
    route: str
    sha256: str
    length: int
    capture_timestamp: str
    static_url: str


@dataclass(frozen=True)
class GuidePreviewGroup:
    group_id: str
    label: str
    gallery_route: str
    guide_route: str
    gallery_static_url: str
    guide_static_url: str
    previews: tuple[GuidePreview, ...]


@dataclass(frozen=True)
class GuidePreviewBundle:
    map_path: Path
    map_sha256: str
    source_acceptance_path: str
    source_acceptance_sha256: str
    source_audit_path: str
    source_audit_sha256: str
    source_manifest_path: str
    source_manifest_sha256: str
    anchor_timestamp: str
    groups: tuple[GuidePreviewGroup, ...]
    map_schema: str = "wow-recovery.guide-preview-source-map.v1"

    @property
    def preview_count(self) -> int:
        return sum(len(group.previews) for group in self.groups)

    def group_for_gallery(self, route: str) -> GuidePreviewGroup | None:
        for group in self.groups:
            if group.gallery_route == route:
                return group
        return None

    def provenance(self) -> dict[str, Any]:
        payload = {
            "schema": (
                "github-pages-guide-preview-provenance/v2"
                if self.map_schema == "wow-recovery.guide-preview-source-map.v2"
                else "github-pages-guide-preview-provenance/v1"
            ),
            "source_map": self.map_path.as_posix(),
            "source_map_sha256": self.map_sha256,
            "source_acceptance": self.source_acceptance_path,
            "source_acceptance_sha256": self.source_acceptance_sha256,
            "source_audit": self.source_audit_path,
            "source_audit_sha256": self.source_audit_sha256,
            "source_manifest": self.source_manifest_path,
            "source_manifest_sha256": self.source_manifest_sha256,
            "anchor_timestamp": self.anchor_timestamp,
            "group_count": len(self.groups),
            "preview_count": self.preview_count,
            "groups": [
                {
                    "group_id": group.group_id,
                    "label": group.label,
                    "gallery_route": group.gallery_route,
                    "guide_route": group.guide_route,
                    "preview_count": len(group.previews),
                    "previews": [
                        {
                            "route": preview.route,
                            "static_url": preview.static_url,
                            "source_sha256": preview.sha256,
                            "source_length": preview.length,
                            "capture_timestamp": preview.capture_timestamp,
                        }
                        for preview in group.previews
                    ],
                }
                for group in self.groups
            ],
        }
        if self.map_schema != "wow-recovery.guide-preview-source-map.v1":
            payload["source_map_schema"] = self.map_schema
        return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside(path: Path, root: Path, *, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise GuidePreviewError(f"{label} escapes workspace: {path}") from exc
    return resolved


def _map_path(root: Path, raw: Any, *, label: str) -> tuple[Path, str]:
    if not isinstance(raw, dict):
        raise GuidePreviewError(f"{label} must be an object")
    relative = raw.get("path")
    expected = str(raw.get("sha256") or "").casefold()
    if not isinstance(relative, str) or not relative:
        raise GuidePreviewError(f"{label}.path is missing")
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise GuidePreviewError(f"{label}.sha256 is invalid")
    path = _inside(root / relative, root, label=label)
    if not path.is_file():
        raise GuidePreviewError(f"{label} file is missing: {path}")
    actual = _sha256(path)
    if actual != expected:
        raise GuidePreviewError(f"{label} SHA-256 mismatch")
    return path, actual


def _route(raw: Any, *, label: str) -> str:
    if not isinstance(raw, str) or not raw.startswith("/"):
        raise GuidePreviewError(f"{label} is not an absolute route")
    if "\\" in raw or "\x00" in raw or "//" in raw or ".." in raw.split("/"):
        raise GuidePreviewError(f"{label} is unsafe: {raw!r}")
    return raw


def _timestamp(raw: Any, *, label: str) -> str:
    value = str(raw or "")
    if not re.fullmatch(r"\d{14}", value):
        raise GuidePreviewError(f"{label} is not a 14-digit timestamp")
    try:
        datetime.strptime(value, "%Y%m%d%H%M%S")
    except ValueError as exc:
        raise GuidePreviewError(f"{label} is not a real timestamp") from exc
    return value


def _read_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GuidePreviewError(f"{label} is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise GuidePreviewError(f"{label} must contain an object")
    return payload


class _GuideAnchorParser(HTMLParser):
    """Collect exact anchor href + image src pairs from one guide page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._anchor: dict[str, Any] | None = None
        self.pairs: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {str(key).casefold(): value or "" for key, value in attrs}
        if tag.casefold() == "a":
            self._anchor = {"href": attrs_dict.get("href", ""), "img": None}
        elif tag.casefold() == "img" and self._anchor is not None:
            self._anchor["img"] = attrs_dict.get("src", "")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "a" and self._anchor is not None:
            href = str(self._anchor.get("href") or "")
            image = str(self._anchor.get("img") or "")
            if href and image:
                self.pairs.append((href, image))
            self._anchor = None


_BUSINESS_QUERY_RE = re.compile(
    r"(?:^|[&;])(?:jsessionid|sessionid|session|token|sid|auth|signature|sig|cookie)\s*=",
    re.IGNORECASE,
)


def _parent_path_part(raw: str, *, guide_source_base_url: str, label: str) -> str:
    """Accept root-relative links or same-origin default-port absolute links."""

    value = html.unescape(str(raw or "")).strip()
    if not value:
        raise GuidePreviewError(f"{label} is empty")
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError as exc:
        raise GuidePreviewError(f"{label} is invalid") from exc
    if value.startswith("//"):
        raise GuidePreviewError(f"{label} is protocol-relative and cannot establish a local parent")
    if parsed.scheme or parsed.netloc:
        try:
            guide_origin = urllib.parse.urlsplit(guide_source_base_url)
            raw_port = parsed.port
            guide_port = guide_origin.port
        except ValueError as exc:
            raise GuidePreviewError(f"{label} has an invalid origin") from exc
        scheme = parsed.scheme.casefold()
        host = (parsed.hostname or "").casefold().rstrip(".")
        guide_host = (guide_origin.hostname or "").casefold().rstrip(".")
        default_raw_port = (scheme == "http" and raw_port in {None, 80}) or (scheme == "https" and raw_port in {None, 443})
        default_guide_port = (guide_origin.scheme.casefold() == "http" and guide_port in {None, 80}) or (guide_origin.scheme.casefold() == "https" and guide_port in {None, 443})
        if (
            scheme not in {"http", "https"}
            or scheme != guide_origin.scheme.casefold()
            or host != guide_host
            or not default_raw_port
            or not default_guide_port
            or parsed.username
            or parsed.password
        ):
            raise GuidePreviewError(f"{label} is cross-origin or uses a non-default port")
        # Absolute parent links with a query can carry session/business state;
        # reject them even when their host matches.  The frozen source uses
        # root-relative links, so this remains a strict compatibility path.
        if parsed.query or parsed.fragment and _BUSINESS_QUERY_RE.search(parsed.query):
            raise GuidePreviewError(f"{label} contains a query-bearing absolute URL")
        if not parsed.path.startswith("/"):
            raise GuidePreviewError(f"{label} absolute path is not root-relative")
        return parsed.path
    if not value.startswith("/"):
        raise GuidePreviewError(f"{label} is not a safe root-relative URL")
    if _BUSINESS_QUERY_RE.search(parsed.query):
        raise GuidePreviewError(f"{label} contains a business/session query")
    return parsed.path


def _raw_path_for_matching(raw: str) -> str:
    """Extract only a comparison path before strict parent validation.

    The path is used to ignore unrelated page anchors (for example the
    frozen footer's external privacy links and JavaScript video controls).
    A pair whose path could establish the requested gallery/preview relation
    is still passed through ``_parent_path_part`` so an external same-path
    URL cannot be accepted by this selector.
    """

    value = html.unescape(str(raw or "")).strip()
    try:
        return urllib.parse.urlsplit(value).path
    except ValueError:
        return ""


def _assert_parent_reference(
    guide_text: str,
    group: GuidePreviewGroup,
    route: str,
    *,
    guide_source_base_url: str,
) -> None:
    parser = _GuideAnchorParser()
    try:
        parser.feed(guide_text)
        parser.close()
    except Exception as exc:
        raise GuidePreviewError(f"guide HTML cannot be parsed: {group.guide_route}") from exc
    pairs: set[tuple[str, str]] = set()
    for index, (href, image) in enumerate(parser.pairs):
        href_candidate = _raw_path_for_matching(href)
        image_candidate = _raw_path_for_matching(image)
        if href_candidate != group.gallery_route and image_candidate != route:
            continue
        href_path = _parent_path_part(href, guide_source_base_url=guide_source_base_url, label=f"{group.group_id} parent href[{index}]")
        image_path = _parent_path_part(image, guide_source_base_url=guide_source_base_url, label=f"{group.group_id} parent img[{index}]")
        pairs.add((href_path, image_path))
    if not any(href == group.gallery_route for href, _image in pairs):
        raise GuidePreviewError(
            f"{group.group_id} guide lacks the real gallery href: {group.guide_route} -> {group.gallery_route}"
        )
    if (group.gallery_route, route) not in pairs:
        raise GuidePreviewError(
            f"{group.group_id} guide lacks parent gallery href + image route: {group.gallery_route} + {route}"
        )


def _record_for(route_records: dict[str, dict[str, Any]], route: str, *, label: str) -> dict[str, Any]:
    record = route_records.get(route)
    if record is None:
        raise GuidePreviewError(f"{label} route is absent from the frozen manifest: {route}")
    return record


def load_guide_preview_map(
    map_path: Path,
    *,
    workspace_root: Path,
    source_site: Path,
    manifest_path: Path,
    manifest: dict[str, Any],
    route_to_static: dict[str, str],
) -> GuidePreviewBundle:
    """Load and strictly validate one accepted guide-preview map."""

    workspace_root = workspace_root.resolve()
    source_site = source_site.resolve()
    manifest_path = manifest_path.resolve()
    map_path = _inside(Path(map_path), workspace_root, label="guide preview map")
    if not map_path.is_file():
        raise GuidePreviewError(f"guide preview map is missing: {map_path}")
    map_payload = _read_json(map_path, label="guide preview map")
    map_schema = str(map_payload.get("schema") or "")
    map_spec = _MAP_SPECS.get(map_schema)
    if map_spec is None:
        raise GuidePreviewError("guide preview map schema is unsupported")
    expected_groups: dict[str, tuple[str, str, str]] = map_spec["groups"]
    expected_group_count = int(map_spec["group_count"])
    expected_preview_count = int(map_spec["preview_count"])
    is_v2 = map_schema == "wow-recovery.guide-preview-source-map.v2"
    map_sha = _sha256(map_path)

    acceptance_path, acceptance_sha = _map_path(workspace_root, map_payload.get("source_acceptance"), label="source_acceptance")
    acceptance = _read_json(acceptance_path, label="source acceptance")
    if acceptance.get("accepted") is not True or acceptance.get("network_requests") != 0:
        raise GuidePreviewError("source acceptance is not accepted local-only evidence")
    checked = acceptance.get("checked")
    if not isinstance(checked, list) or len(checked) != expected_preview_count:
        raise GuidePreviewError(
            f"source acceptance does not contain exactly {expected_preview_count} accepted previews"
        )
    accepted_by_route: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(checked):
        if not isinstance(item, dict):
            raise GuidePreviewError(f"source acceptance checked[{index}] is invalid")
        route = _route(item.get("route"), label=f"source acceptance checked[{index}].route")
        if route in accepted_by_route:
            raise GuidePreviewError(f"source acceptance repeats route: {route}")
        accepted_by_route[route] = item
        if item.get("accepted") is not True:
            raise GuidePreviewError(f"source acceptance rejects route: {route}")
    declared_acceptance_sha = str(map_payload.get("source_acceptance_sha256") or acceptance_sha).casefold()
    if declared_acceptance_sha != acceptance_sha:
        raise GuidePreviewError("guide preview map source_acceptance_sha256 mismatch")

    manifest_ref_path, declared_manifest_sha = _map_path(workspace_root, map_payload.get("source_manifest"), label="source_manifest")
    manifest_sha = _sha256(manifest_path)
    if manifest_ref_path != manifest_path and declared_manifest_sha != manifest_sha:
        raise GuidePreviewError("guide preview map source_manifest does not bind to the exporter manifest")
    if declared_manifest_sha != manifest_sha:
        raise GuidePreviewError("guide preview map source_manifest_sha256 mismatch")
    anchor = _timestamp(manifest.get("anchor_timestamp"), label="manifest anchor_timestamp")
    if _timestamp(map_payload.get("anchor_timestamp"), label="guide preview map anchor_timestamp") != anchor:
        raise GuidePreviewError("guide preview map anchor_timestamp differs from manifest")

    audit_path, audit_sha = _map_path(workspace_root, map_payload.get("source_audit"), label="source_audit")
    declared_audit_sha = str(map_payload.get("source_audit_sha256") or audit_sha).casefold()
    if declared_audit_sha != audit_sha:
        raise GuidePreviewError("guide preview map source_audit_sha256 mismatch")
    if acceptance.get("audit_sha256") and str(acceptance["audit_sha256"]).casefold() != audit_sha:
        raise GuidePreviewError("source acceptance audit_sha256 does not match source audit")
    audit = _read_json(audit_path, label="source audit")
    if audit.get("counts", {}).get("target_count") != expected_preview_count:
        raise GuidePreviewError(f"source audit target count is not {expected_preview_count}")

    raw_groups = map_payload.get("groups")
    if not isinstance(raw_groups, list) or len(raw_groups) != expected_group_count:
        raise GuidePreviewError(
            f"guide preview map must contain exactly {map_spec['version_label']} groups"
        )
    route_records = {str(item.get("route")): item for item in (manifest.get("files") or []) if isinstance(item, dict)}
    seen_ids: set[str] = set()
    seen_routes: set[str] = set()
    groups: list[GuidePreviewGroup] = []
    for raw_group in raw_groups:
        if not isinstance(raw_group, dict):
            raise GuidePreviewError("guide preview group is not an object")
        group_id = str(raw_group.get("group_id") or "")
        if group_id not in expected_groups or group_id in seen_ids:
            raise GuidePreviewError(f"guide preview group identity is invalid or duplicated: {group_id!r}")
        seen_ids.add(group_id)
        expected_label, expected_gallery, expected_guide = expected_groups[group_id]
        label = raw_group.get("label")
        gallery_route = _route(raw_group.get("gallery_route"), label=f"{group_id}.gallery_route")
        guide_route = _route(raw_group.get("guide_route"), label=f"{group_id}.guide_route")
        if label != expected_label or gallery_route != expected_gallery or guide_route != expected_guide:
            raise GuidePreviewError(f"{group_id} does not match its fixed gallery/guide identity")
        if gallery_route in seen_routes:
            raise GuidePreviewError(f"gallery route is duplicated: {gallery_route}")
        seen_routes.add(gallery_route)
        gallery_record = _record_for(route_records, gallery_route, label=f"{group_id}.gallery")
        guide_record = _record_for(route_records, guide_route, label=f"{group_id}.guide")
        if not str(gallery_record.get("kind") or "").casefold() in {"html", "menu_html"} and not str(gallery_record.get("mime") or "").casefold().startswith("text/html"):
            raise GuidePreviewError(f"{group_id}.gallery is not an HTML manifest record")
        if not str(guide_record.get("kind") or "").casefold() in {"html", "menu_html", "xml", "legacy_component"} and not str(guide_record.get("mime") or "").casefold().startswith(("text/html", "application/xml", "text/xml")):
            raise GuidePreviewError(f"{group_id}.guide is not an HTML/XML manifest record")
        guide_source_rel = str(guide_record.get("output_path") or "")
        guide_source = _inside(workspace_root / guide_source_rel, source_site, label=f"{group_id}.guide source")
        if not guide_source.is_file():
            raise GuidePreviewError(f"{group_id}.guide source is missing: {guide_source}")
        guide_text = guide_source.read_text(encoding="utf-8", errors="replace")
        gallery_static = route_to_static.get(gallery_route)
        guide_static = route_to_static.get(guide_route)
        if not gallery_static or not guide_static:
            raise GuidePreviewError(f"{group_id} gallery/guide route is not in the Pages route map")
        raw_previews = raw_group.get("previews")
        if not isinstance(raw_previews, list) or not raw_previews:
            raise GuidePreviewError(f"{group_id}.previews is empty")
        previews: list[GuidePreview] = []
        seen_preview_routes: set[str] = set()
        for index, raw_preview in enumerate(raw_previews):
            label_prefix = f"{group_id}.previews[{index}]"
            if not isinstance(raw_preview, dict):
                raise GuidePreviewError(f"{label_prefix} is not an object")
            if is_v2 and any(
                field in raw_preview
                for field in ("dynamic_full_candidate", "full_route", "slot", "slot_index", "dynamic_route")
            ):
                raise GuidePreviewError(
                    f"{label_prefix} contains a dynamic/full-image candidate field"
                )
            preview_route = _route(raw_preview.get("route"), label=f"{label_prefix}.route")
            if preview_route in seen_preview_routes or preview_route in {gallery_route, guide_route}:
                raise GuidePreviewError(f"{label_prefix}.route is duplicated or collides")
            seen_preview_routes.add(preview_route)
            if is_v2 and group_id == "city-attacks":
                if preview_route not in CITY_PREVIEW_ROUTES:
                    raise GuidePreviewError(f"{label_prefix}.route is not an accepted City Attacks preview route")
            elif "/thumbs/" not in preview_route or not preview_route.casefold().endswith("-thumb.jpg"):
                raise GuidePreviewError(f"{label_prefix}.route is not an existing thumbnail route")
            accepted = accepted_by_route.get(preview_route)
            if accepted is None:
                raise GuidePreviewError(
                    f"{label_prefix}.route is not in the accepted {expected_preview_count}"
                )
            expected_sha = str(raw_preview.get("sha256") or "").casefold()
            if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
                raise GuidePreviewError(f"{label_prefix}.sha256 is invalid")
            try:
                expected_length = int(raw_preview.get("length"))
            except (TypeError, ValueError) as exc:
                raise GuidePreviewError(f"{label_prefix}.length is invalid") from exc
            capture = _timestamp(raw_preview.get("capture_timestamp"), label=f"{label_prefix}.capture_timestamp")
            if expected_sha != str(accepted.get("sha256") or "").casefold() or expected_length != int(accepted.get("length")) or capture != str(accepted.get("capture_from_frozen_manifest") or ""):
                raise GuidePreviewError(f"{label_prefix} disagrees with source acceptance")
            if capture > anchor:
                raise GuidePreviewError(f"{label_prefix} capture is after manifest anchor")
            record = _record_for(route_records, preview_route, label=label_prefix)
            if str(record.get("kind") or "").casefold() != "image" or bool(record.get("transformed")):
                raise GuidePreviewError(f"{label_prefix} manifest record is not an untransformed image")
            if not str(record.get("mime") or record.get("source_mime") or "").casefold().startswith("image/"):
                raise GuidePreviewError(f"{label_prefix} manifest record is not an image MIME")
            if str(record.get("derived_sha256") or "").casefold() != expected_sha or int(record.get("derived_length", -1)) != expected_length:
                raise GuidePreviewError(f"{label_prefix} does not match manifest SHA/length")
            if record.get("source_sha256") is not None and str(record.get("source_sha256") or "").casefold() != expected_sha:
                raise GuidePreviewError(f"{label_prefix} does not match manifest source SHA")
            if record.get("source_length") is not None and int(record.get("source_length")) != expected_length:
                raise GuidePreviewError(f"{label_prefix} does not match manifest source length")
            if str(record.get("actual_timestamp") or "") != capture:
                raise GuidePreviewError(f"{label_prefix} does not match manifest actual_timestamp")
            source_rel = str(record.get("output_path") or "")
            source = _inside(workspace_root / source_rel, source_site, label=f"{label_prefix} source")
            if not source.is_file():
                raise GuidePreviewError(f"{label_prefix} source file is missing: {source}")
            data = source.read_bytes()
            if len(data) != expected_length or hashlib.sha256(data).hexdigest() != expected_sha:
                raise GuidePreviewError(f"{label_prefix} source bytes do not match accepted SHA/length")
            _assert_parent_reference(
                guide_text,
                GuidePreviewGroup(group_id, label, gallery_route, guide_route, gallery_static, guide_static, ()),
                preview_route,
                guide_source_base_url=str(guide_record.get("source_base_url") or ""),
            )
            static_url = route_to_static.get(preview_route)
            if not static_url:
                raise GuidePreviewError(f"{label_prefix} route is not in the Pages route map")
            previews.append(GuidePreview(preview_route, expected_sha, expected_length, capture, static_url))
        groups.append(GuidePreviewGroup(group_id, label, gallery_route, guide_route, gallery_static, guide_static, tuple(previews)))
    if seen_ids != set(expected_groups):
        raise GuidePreviewError(
            f"guide preview map does not contain all {expected_group_count} fixed groups"
        )
    if (
        sum(len(group.previews) for group in groups) != expected_preview_count
        or set(accepted_by_route) != {preview.route for group in groups for preview in group.previews}
    ):
        raise GuidePreviewError("guide preview route conservation failed")
    return GuidePreviewBundle(
        map_path=map_path.relative_to(workspace_root),
        map_sha256=map_sha,
        source_acceptance_path=acceptance_path.relative_to(workspace_root).as_posix(),
        source_acceptance_sha256=acceptance_sha,
        source_audit_path=audit_path.relative_to(workspace_root).as_posix(),
        source_audit_sha256=audit_sha,
        source_manifest_path=manifest_ref_path.relative_to(workspace_root).as_posix(),
        source_manifest_sha256=manifest_sha,
        anchor_timestamp=anchor,
        groups=tuple(groups),
        map_schema=map_schema,
    )


def _slug(group_id: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", group_id.casefold()).strip("-")


def render_gallery_section(group: GuidePreviewGroup) -> str:
    """Render one deterministic, local-only section for a gallery page."""

    section_id = f"offline-preserved-guide-previews-{_slug(group.group_id)}"
    cards = []
    for preview in group.previews:
        image_url = html.escape(preview.static_url, quote=True)
        cards.append(
            '<figure class="offline-guide-preview-card">'
            f'<a href="{image_url}" data-guide-preview-route="{html.escape(preview.route, quote=True)}">'
            f'<img src="{image_url}" alt="Preserved guide preview" loading="lazy">'
            "</a>"
            '<figcaption><a class="offline-guide-preview-open" '
            f'href="{image_url}">Open preserved preview</a></figcaption>'
            "</figure>"
        )
    guide_url = html.escape(group.guide_static_url, quote=True)
    return (
        f'<section id="{section_id}" class="offline-guide-preview-section" '
        f'data-guide-preview-group="{html.escape(group.group_id, quote=True)}" '
        f'data-guide-preview-count="{len(group.previews)}" '
        'style="box-sizing:border-box; margin:18px auto 24px; padding:16px; '
        'max-width:960px; border:1px solid #8d7542; background:#fff9e8; color:#2d2418; '
        'font:14px/1.45 Arial,sans-serif;">'
        '<style>'
        f'#{section_id} .offline-guide-preview-heading{{margin:0 0 7px;color:#5a3e21;font:700 22px/1.2 Georgia,serif;}}'
        f'#{section_id} .offline-guide-preview-note{{margin:0 0 11px;}}'
        f'#{section_id} .offline-guide-preview-guide{{display:inline-block;margin:0 0 13px;color:#234c83;}}'
        f'#{section_id} .offline-guide-preview-grid{{display:flex;flex-wrap:wrap;gap:12px;}}'
        f'#{section_id} .offline-guide-preview-card{{box-sizing:border-box;width:min(100%,210px);margin:0;padding:8px;background:#fff;border:1px solid #c8b58e;}}'
        f'#{section_id} .offline-guide-preview-card img{{display:block;width:100%;height:auto;}}'
        f'#{section_id} .offline-guide-preview-open{{display:inline-block;margin-top:6px;color:#234c83;}}'
        '</style>'
        '<h2 class="offline-guide-preview-heading">Preserved guide previews</h2>'
        '<p class="offline-guide-preview-note">These previews survive in the original guide pages. Full-size gallery images are still incomplete.</p>'
        f'<a class="offline-guide-preview-guide" href="{guide_url}">View original guide</a>'
        f'<div class="offline-guide-preview-grid">{"".join(cards)}</div>'
        "</section>"
    )


def insert_gallery_section(text: str, group: GuidePreviewGroup) -> str:
    """Insert one section immediately after ``<body>`` and assert idempotency."""

    section_id = f"offline-preserved-guide-previews-{_slug(group.group_id)}"
    if len(re.findall(rf"id=[\"']{re.escape(section_id)}[\"']", text, flags=re.I)):
        raise GuidePreviewError(f"guide preview section already exists: {section_id}")
    match = re.search(r"<body\b[^>]*>", text, flags=re.I)
    if match is None:
        raise GuidePreviewError(f"gallery page has no body element: {group.gallery_route}")
    section = "\n" + render_gallery_section(group) + "\n"
    derived = text[: match.end()] + section + text[match.end() :]
    if len(re.findall(rf"id=[\"']{re.escape(section_id)}[\"']", derived, flags=re.I)) != 1:
        raise GuidePreviewError(f"guide preview section insertion count is not one: {section_id}")
    return derived


def build_source_map_from_audit(
    *,
    output: Path,
    acceptance_path: Path,
    audit_path: Path,
    manifest_path: Path,
    workspace_root: Path,
) -> Path:
    """Materialize the curated five-group map from accepted local evidence."""

    root = workspace_root.resolve()
    acceptance_path = _inside(Path(acceptance_path), root, label="source acceptance")
    audit_path = _inside(Path(audit_path), root, label="source audit")
    manifest_path = _inside(Path(manifest_path), root, label="source manifest")
    output = _inside(Path(output), root, label="guide preview map output")
    input_paths = {acceptance_path, audit_path, manifest_path}
    if output in input_paths:
        raise GuidePreviewError("guide preview map output must differ from every source input")
    if output.exists():
        raise GuidePreviewError(f"guide preview map output already exists: {output}")
    acceptance = _read_json(acceptance_path, label="source acceptance")
    audit = _read_json(audit_path, label="source audit")
    checked = acceptance.get("checked")
    items = audit.get("items")
    if acceptance.get("accepted") is not True or acceptance.get("network_requests") != 0:
        raise GuidePreviewError("cannot build map from an unaccepted or network-derived receipt")
    if not isinstance(checked, list) or len(checked) != 19 or not isinstance(items, list) or len(items) != 19:
        raise GuidePreviewError("accepted and audit inputs must each contain exactly 19 records")
    checked_by_route = {_route(item.get("route"), label="accepted route"): item for item in checked if isinstance(item, dict)}
    if len(checked_by_route) != 19:
        raise GuidePreviewError("accepted receipt contains duplicate or invalid routes")
    groups: list[dict[str, Any]] = []
    for group_id, (label, gallery_route, guide_route) in EXPECTED_GROUPS.items():
        group_items = [item for item in items if isinstance(item, dict) and item.get("gallery") == label]
        if not group_items:
            raise GuidePreviewError(f"audit has no items for fixed group: {group_id}")
        previews = []
        for item in group_items:
            route = _route(item.get("route"), label=f"{group_id} audit route")
            accepted = checked_by_route.get(route)
            if accepted is None or accepted.get("accepted") is not True:
                raise GuidePreviewError(f"audit route is absent from accepted receipt: {route}")
            previews.append(
                {
                    "route": route,
                    "sha256": str(accepted.get("sha256") or "").casefold(),
                    "length": int(accepted.get("length")),
                    "capture_timestamp": str(accepted.get("capture_from_frozen_manifest") or ""),
                }
            )
        groups.append(
            {
                "group_id": group_id,
                "label": label,
                "gallery_route": gallery_route,
                "guide_route": guide_route,
                "previews": previews,
            }
        )
    if sum(len(group["previews"]) for group in groups) != 19:
        raise GuidePreviewError("curated map route conservation failed")
    manifest_sha = _sha256(manifest_path)
    acceptance_sha = _sha256(acceptance_path)
    audit_sha = _sha256(audit_path)
    payload = {
        "schema": "wow-recovery.guide-preview-source-map.v1",
        "purpose": "Accepted local guide-page preview bytes shown in five gallery pages; no dynamic full/thumb aliases or gallery-script changes.",
        "source_acceptance": {
            "path": acceptance_path.relative_to(root).as_posix(),
            "sha256": acceptance_sha,
        },
        "source_acceptance_sha256": acceptance_sha,
        "source_audit": {
            "path": audit_path.relative_to(root).as_posix(),
            "sha256": audit_sha,
        },
        "source_audit_sha256": audit_sha,
        "source_manifest": {
            "path": manifest_path.relative_to(root).as_posix(),
            "sha256": manifest_sha,
        },
        "source_manifest_sha256": manifest_sha,
        "anchor_timestamp": str(_read_json(manifest_path, label="source manifest").get("anchor_timestamp") or ""),
        "groups": groups,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-map", action="store_true", help="Build the curated map from accepted local evidence")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--workspace-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    if not args.build_map:
        parser.error("--build-map is required")
    try:
        output = build_source_map_from_audit(
            output=args.output,
            acceptance_path=args.acceptance,
            audit_path=args.audit,
            manifest_path=args.manifest,
            workspace_root=args.workspace_root,
        )
    except GuidePreviewError as exc:
        parser.error(str(exc))
    print(json.dumps({"output": str(output), "sha256": _sha256(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())


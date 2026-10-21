"""Small, source-bounded compatibility rewrites for non-gallery pages.

The historical pages still use image sprites for their left menu and one
downloads hover handler points at the wrong image global.  This module keeps
those repairs deliberately narrow: comments and unrelated routes are left
byte-for-byte unchanged, and route query strings are rejected instead of
being allowed to select a different rewrite path.
"""

from __future__ import annotations

import html
import re
from typing import Any


MENU_LABELS = {
    "menuNews-header": "News",
    "menuAccount-header": "Account",
    "menuGameGuide-header": "Game Guide",
    "menuInteractive-header": "Workshop",
    "menuMedia-header": "Media",
    "menuForums-header": "Forums",
    "menuCommunity-header": "Community",
    "menuSupport-header": "Support",
}


class NonGalleryCompatError(ValueError):
    """Raised when a compatibility route is ambiguous or malformed."""


def _normalise_route(route: str) -> str:
    if not isinstance(route, str) or not route:
        raise NonGalleryCompatError("route must be a non-empty string")
    if any(token in route for token in ("?", "#")):
        raise NonGalleryCompatError("route queries and fragments are not accepted")
    if "\\" in route or "\x00" in route:
        raise NonGalleryCompatError("route must use a local URL path")
    raw = "/" + route.lstrip("/")
    if raw.startswith("//") or any(part == ".." for part in raw.split("/")):
        raise NonGalleryCompatError("route must not escape the local route root")
    return raw


_COMMENT_RE = re.compile(r"<!--.*?(?:-->|$)", re.DOTALL)
_INERT_RE = re.compile(
    r"<!--.*?(?:-->|$)|<(?:script|style)\b[^>]*>.*?</(?:script|style)\s*>",
    re.IGNORECASE | re.DOTALL,
)
_ANCHOR_RE = re.compile(r"<a\b[^>]*>.*?</a\s*>", re.IGNORECASE | re.DOTALL)
_IMG_RE = re.compile(r"<img\b(?P<attrs>[^>]*)>", re.IGNORECASE | re.DOTALL)
_ATTR_RE = re.compile(
    r"(?P<name>[A-Za-z_:][A-Za-z0-9_.:-]*)\s*=\s*(?P<quote>[\"'])(?P<value>.*?)\2",
    re.DOTALL,
)
_MENU_ANCHOR_RE = re.compile(
    r"<a(?P<attrs>[^>]*)>(?P<body>\s*<em\b[^>]*>\s*Game Guide\s*</em>\s*)</a\s*>",
    re.IGNORECASE | re.DOTALL,
)
_EM_TEXT_RE = re.compile(
    r"(?P<open><em\b[^>]*>)\s*Game Guide\s*(?P<close></em\s*>)",
    re.IGNORECASE | re.DOTALL,
)


def _attrs(attrs: str) -> dict[str, str]:
    return {match.group("name").lower(): match.group("value") for match in _ATTR_RE.finditer(attrs)}


def _rewrite_menu_segment(segment: str, stats: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        attr_map = _attrs(attrs)
        element_id = attr_map.get("id")
        label = MENU_LABELS.get(element_id or "")
        if label is None:
            return match.group(0)
        if label == "Game Guide" and "aria-label" in attr_map:
            return match.group(0)
        body = _EM_TEXT_RE.sub(
            lambda em: em.group("open") + html.escape(label) + em.group("close"),
            match.group("body"),
            count=1,
        )
        new_attrs = attrs
        if "aria-label" not in attr_map:
            new_attrs = new_attrs.rstrip() + ' aria-label="' + html.escape(label, quote=True) + '"'
            stats["menu_aria_added"] += 1
        stats["menu_labels"][element_id] = stats["menu_labels"].get(element_id, 0) + 1
        return "<a" + new_attrs + ">" + body + "</a>"

    return _MENU_ANCHOR_RE.sub(replace, segment)


def _rewrite_downloads_segment(segment: str, stats: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        anchor = match.group(0)
        if not re.search(r"document\s*\.\s*goblue6\s*\.\s*src\s*=\s*goblueroll\.src", anchor, re.I):
            return anchor
        if not re.search(r"document\s*\.\s*goblue8\s*\.\s*src\s*=\s*gobluedef\.src", anchor, re.I):
            return anchor
        image_match = _IMG_RE.search(anchor)
        if image_match is None:
            return anchor
        image_attrs = _attrs(image_match.group("attrs"))
        if image_attrs.get("name") != "goblue6" or image_attrs.get("id") != "goblue6":
            return anchor
        fixed, count = re.subn(
            r"document\s*\.\s*goblue8\s*\.\s*src",
            "document.goblue6.src",
            anchor,
            count=1,
            flags=re.IGNORECASE,
        )
        if count == 1:
            stats["downloads_hover_fixes"] += 1
            return fixed
        return anchor

    return _ANCHOR_RE.sub(replace, segment)


def _rewrite_outside_comments(text: str, route: str, stats: dict[str, Any]) -> str:
    pieces: list[str] = []
    cursor = 0
    for inert in _INERT_RE.finditer(text):
        visible = text[cursor : inert.start()]
        visible = _rewrite_menu_segment(visible, stats)
        if route == "/downloads/index.html":
            visible = _rewrite_downloads_segment(visible, stats)
        pieces.append(visible)
        pieces.append(inert.group(0))
        cursor = inert.end()
    visible = text[cursor:]
    visible = _rewrite_menu_segment(visible, stats)
    if route == "/downloads/index.html":
        visible = _rewrite_downloads_segment(visible, stats)
    pieces.append(visible)
    return "".join(pieces)


def transform_html(text: str, *, route: str) -> tuple[str, dict[str, Any]]:
    """Apply the measured non-gallery HTML repairs.

    The menu label repair is available on pages containing the shared menu;
    the downloads hover repair is restricted to ``/downloads/index.html``.
    """

    if not isinstance(text, str):
        raise NonGalleryCompatError("text must be a string")
    normalised = _normalise_route(route)
    stats: dict[str, Any] = {
        "route": normalised,
        "changed": False,
        "downloads_hover_fixes": 0,
        "menu_labels": {},
        "menu_aria_added": 0,
    }
    new_text = _rewrite_outside_comments(text, normalised, stats)
    stats["changed"] = new_text != text
    stats["menu_label_count"] = sum(stats["menu_labels"].values())
    return new_text, stats


__all__ = ["MENU_LABELS", "NonGalleryCompatError", "transform_html"]

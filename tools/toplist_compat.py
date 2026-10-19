"""Narrow compatibility rewrites for the frozen Toplist JavaScript assets.

The historical Toplist scripts contain both JavaScript regular-expression
literals and HTML fragments embedded in JavaScript strings.  The generic
root-literal pass cannot safely distinguish those forms, so these two exact
Source15 assets receive a source-hash-guarded bounded rewrite instead.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


TOPLIST_PROTOTYPE_ROUTE = "/toplist/includes-client/js/prototype.js"
TOPLIST_PROTOTYPE_SOURCE_SHA256 = "4efde4e87b2db7b8cb6b81f70ab4972c3cfbcd7d329d0752ad223abe67fa9120"
TOPLIST_LOGIC_ROUTE = "/toplist/includes-client/js/logic.js"
TOPLIST_LOGIC_SOURCE_SHA256 = "1c0a50ff5fd1af19663b925e502c3a3b2dab0eb905874d95966e8bf35504eabe"

_LOGIC_PIXEL_LITERAL = 'src=\\"/toplist/images/pixel.gif\\"'
_LOGIC_PIXEL_RE = re.compile(re.escape(_LOGIC_PIXEL_LITERAL))
_LOGIC_PIXEL_EXPECTED_COUNT = 5
_LOGIC_TABLE_RE = re.compile(r"url\(/toplist/images/table-(left|right)\.jpg\)")
_LOGIC_TABLE_EXPECTED_COUNTS = {"left": 1, "right": 1}
_LOGIC_DATA_DIR_LITERAL = 'var dataDir = "/toplist/data/" + lang;'
_LOGIC_EMPTY_LABEL_LITERAL = "infoSpan.innerHTML = labelNoDataAvail;"
_LOGIC_HISTORICAL_EMPTY_LABEL = "Historical ranking data for this date has not been recovered."
_TOPLIST_DATA_ROUTE_RE = re.compile(r"^/toplist/data/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+\.js$")


class ToplistCompatError(RuntimeError):
    """Raised when a guarded Toplist source no longer matches its contract."""


def _assert_source(route: str, source_sha256: str, text: str, expected_sha256: str) -> None:
    if source_sha256.casefold() != expected_sha256:
        raise ToplistCompatError(
            f"Toplist compatibility source SHA mismatch for {route}: "
            f"expected {expected_sha256}, got {source_sha256}"
        )
    actual_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ToplistCompatError(
            f"Toplist compatibility text SHA mismatch for {route}: "
            f"expected {expected_sha256}, got {actual_sha256}"
        )


def _accepted_data_routes(localizer: Any) -> dict[str, str]:
    """Return only exact local Toplist data routes accepted by the loader."""

    source_routes = getattr(localizer, "route_to_static", {})
    if source_routes is None:
        source_routes = {}
    if not isinstance(source_routes, dict):
        raise ToplistCompatError("Toplist compatibility localizer route_to_static must be a mapping")
    accepted: dict[str, str] = {}
    for route, target in source_routes.items():
        if not isinstance(route, str) or not _TOPLIST_DATA_ROUTE_RE.fullmatch(route):
            continue
        if not isinstance(target, str) or not target or not target.startswith("/") or target.startswith("//"):
            raise ToplistCompatError(f"Toplist data route is not a local static path: {route!r}")
        accepted[route] = target
    return accepted


def _inject_data_route_guard(text: str, localizer: Any) -> str:
    count = text.count(_LOGIC_DATA_DIR_LITERAL)
    if count != 1:
        raise ToplistCompatError(
            f"Toplist compatibility dataDir literal count mismatch: expected 1, got {count}"
        )
    route_map = _accepted_data_routes(localizer)
    serialized = json.dumps(route_map, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    injected = (
        _LOGIC_DATA_DIR_LITERAL
        + "\nvar topListLocalDataRoutes = "
        + serialized
        + ";"
    )
    return text.replace(_LOGIC_DATA_DIR_LITERAL, injected, 1)


def _rewrite_ajax_data_request(text: str) -> str:
    pattern = re.compile(
        r"(?P<i>[ \t]*)var xhr = createXMLHttpRequest\(\);\r?\n"
        r"(?:[ \t]*\r?\n)?"
        r"(?P=i)var id = feed\.substr\(feed\.length-11, 8\);"
    )
    replacement = (
        "{i}var id = feed.substr(feed.length-11, 8);\n"
        "{i}var topListDataRequest = dataDir + \"/\" + feed;\n"
        "{i}var topListDataRoute = topListLocalDataRoutes[topListDataRequest];\n"
        "{i}if (!topListDataRoute) {{\n"
        "{i}    removeTable(pos); dataMissing += id; injectTable(id, pos);\n"
        "{i}    return;\n"
        "{i}}}\n"
        "{i}var xhr = createXMLHttpRequest();\n"
        "{i}"
    )

    def expand(match: re.Match[str]) -> str:
        return replacement.format(i=match.group("i"))

    rewritten, replaced = pattern.subn(expand, text)
    if replaced != 1:
        raise ToplistCompatError(
            f"Toplist compatibility ajax request guard count mismatch: expected 1, got {replaced}"
        )
    open_literal = 'xhr.open("GET", dataDir + "/" + feed, true);'
    if rewritten.count(open_literal) != 1:
        raise ToplistCompatError(
            "Toplist compatibility ajax open expression count mismatch: expected 1"
        )
    return rewritten.replace(open_literal, 'xhr.open("GET", topListDataRoute, true);', 1)


def _rewrite_table_assets(text: str, base_url: str, localizer: Any, recorder: Any) -> str:
    counts = {side: len(re.findall(rf"url\(/toplist/images/table-{side}\.jpg\)", text)) for side in _LOGIC_TABLE_EXPECTED_COUNTS}
    if counts != _LOGIC_TABLE_EXPECTED_COUNTS:
        raise ToplistCompatError(
            "Toplist compatibility table asset count mismatch: "
            f"expected {_LOGIC_TABLE_EXPECTED_COUNTS}, got {counts}"
        )

    def replace(match: re.Match[str]) -> str:
        raw = f"/toplist/images/table-{match.group(1)}.jpg"
        local_url = localizer.localize(
            raw,
            base_url=base_url,
            context="css_url",
            recorder=recorder,
        )
        if not isinstance(local_url, str) or not local_url:
            raise ToplistCompatError(f"Toplist compatibility localizer returned an empty CSS URL: {raw}")
        return f"url({local_url})"

    rewritten, replaced = _LOGIC_TABLE_RE.subn(replace, text)
    if replaced != 2:
        raise ToplistCompatError(f"Toplist compatibility table replacement count mismatch: expected 2, got {replaced}")
    return rewritten


def _rewrite_empty_data_label(text: str) -> str:
    count = text.count(_LOGIC_EMPTY_LABEL_LITERAL)
    if count != 1:
        raise ToplistCompatError(
            "Toplist compatibility empty-label assignment count mismatch: expected 1, "
            f"got {count}"
        )
    replacement = (
        'infoSpan.innerHTML = (dataMissing.indexOf(id) != -1) '
        f'? "{_LOGIC_HISTORICAL_EMPTY_LABEL}" : labelNoDataAvail;'
    )
    return text.replace(_LOGIC_EMPTY_LABEL_LITERAL, replacement, 1)


def rewrite_toplist_script(
    text: str,
    route: str,
    source_sha256: str,
    base_url: str,
    localizer: Any,
    recorder: Any,
) -> tuple[str, bool]:
    """Apply the exact Source15 Toplist compatibility rewrite.

    Unknown routes are returned unchanged so the normal exporter path remains
    responsible for every other script.  The Prototype source is returned
    byte-for-byte unchanged after its route and source-hash guard.  The logic
    source receives five escaped pixel ``src`` replacements, two exact table
    CSS URL replacements, and a catalog-backed data request guard. Unknown
    historical feeds use the original empty-table path with an archive notice;
    captured feeds retain the original loader through their local URL.
    """

    if route == TOPLIST_PROTOTYPE_ROUTE:
        _assert_source(route, source_sha256, text, TOPLIST_PROTOTYPE_SOURCE_SHA256)
        return text, True

    if route != TOPLIST_LOGIC_ROUTE:
        return text, False

    _assert_source(route, source_sha256, text, TOPLIST_LOGIC_SOURCE_SHA256)
    count = len(_LOGIC_PIXEL_RE.findall(text))
    if count != _LOGIC_PIXEL_EXPECTED_COUNT:
        raise ToplistCompatError(
            f"Toplist compatibility pixel literal count mismatch for {route}: "
            f"expected {_LOGIC_PIXEL_EXPECTED_COUNT}, got {count}"
        )

    def replace(match: re.Match[str]) -> str:
        local_url = localizer.localize(
            "/toplist/images/pixel.gif",
            base_url=base_url,
            context="image",
            recorder=recorder,
        )
        if not isinstance(local_url, str) or not local_url:
            raise ToplistCompatError("Toplist compatibility localizer returned an empty pixel URL")
        return 'src=\\"' + local_url + '\\"'

    rewritten, replaced = _LOGIC_PIXEL_RE.subn(replace, text)
    if replaced != _LOGIC_PIXEL_EXPECTED_COUNT:
        raise ToplistCompatError(
            f"Toplist compatibility replacement count mismatch for {route}: "
            f"expected {_LOGIC_PIXEL_EXPECTED_COUNT}, got {replaced}"
        )
    rewritten = _rewrite_table_assets(rewritten, base_url, localizer, recorder)
    rewritten = _inject_data_route_guard(rewritten, localizer)
    rewritten = _rewrite_ajax_data_request(rewritten)
    rewritten = _rewrite_empty_data_label(rewritten)
    return rewritten, True


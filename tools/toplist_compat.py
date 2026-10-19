"""Narrow compatibility rewrites for the frozen Toplist JavaScript assets.

The historical Toplist scripts contain both JavaScript regular-expression
literals and HTML fragments embedded in JavaScript strings.  The generic
root-literal pass cannot safely distinguish those forms, so these two exact
Source15 assets receive a source-hash-guarded bounded rewrite instead.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


TOPLIST_PROTOTYPE_ROUTE = "/toplist/includes-client/js/prototype.js"
TOPLIST_PROTOTYPE_SOURCE_SHA256 = "4efde4e87b2db7b8cb6b81f70ab4972c3cfbcd7d329d0752ad223abe67fa9120"
TOPLIST_LOGIC_ROUTE = "/toplist/includes-client/js/logic.js"
TOPLIST_LOGIC_SOURCE_SHA256 = "1c0a50ff5fd1af19663b925e502c3a3b2dab0eb905874d95966e8bf35504eabe"

_LOGIC_PIXEL_LITERAL = 'src=\\"/toplist/images/pixel.gif\\"'
_LOGIC_PIXEL_RE = re.compile(re.escape(_LOGIC_PIXEL_LITERAL))
_LOGIC_PIXEL_EXPECTED_COUNT = 5


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
    source receives exactly five replacements of the escaped HTML ``src``
    literal; all other JavaScript expressions and dynamic data paths remain
    untouched.
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
    return rewritten, True


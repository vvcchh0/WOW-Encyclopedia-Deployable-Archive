"""Source-bounded repair for the historical Aldor/Scryers reward table.

The reward table JavaScript assigns two button backgrounds with document
relative URLs (``url(images/button-*.jpg)``).  The page includes the script
from ``rewardstable/scripts`` but the exact existing images live in the
shared ``rewardstable/images`` directory.  In a GitHub Pages subpath the
document-relative assignment therefore requests the wrong directory.

This module changes only those two reviewed string literals in the exact
rewardstable-new.js source.  It does not copy images, alter page HTML, or
repair the separate Wrath bestiary resources.
"""

from __future__ import annotations

import hashlib
from typing import Any


REWARDSTABLE_ROUTE = "/info/basics/factions/rewardstable/scripts/rewardstable-new.js"
REWARDSTABLE_SCRIPT_ROUTE = REWARDSTABLE_ROUTE
ALLIANCE_IMAGE_ROUTE = "/info/basics/factions/rewardstable/images/button-alliance.jpg"
HORDE_IMAGE_ROUTE = "/info/basics/factions/rewardstable/images/button-horde.jpg"

# Source16 retains the UTF-8 BOM.  v46 has the same script body with only that
# BOM absent after the earlier derived export.  Both hashes are accepted so a
# read-only v46 prototype can exercise the same precise transform without
# weakening the guard to arbitrary JavaScript.  The exporter decodes a BOM
# using ``utf-8-sig`` before invoking a text transform, so the Source16 byte
# SHA is also explicitly bound to this one known BOM-less body.
SOURCE16_REWARDSTABLE_SOURCE_SHA256 = "7c73724e2c6cc60d4ee7f0efd57fc0f3a31a0818f84c23a75a1960f60ee35855"
V46_REWARDSTABLE_DERIVED_SHA256 = "70e2e31df0adca6e65992127ec6ea3c863d2c8443cbba489a027d76d965bdf22"
ACCEPTED_SOURCE_SHA256 = frozenset(
    {
        SOURCE16_REWARDSTABLE_SOURCE_SHA256,
        V46_REWARDSTABLE_DERIVED_SHA256,
    }
)

_ALLIANCE_LITERAL = "url(images/button-alliance.jpg)"
_HORDE_LITERAL = "url(images/button-horde.jpg)"


class RewardstableCompatError(ValueError):
    """Raised when the exact reward table source or local path is invalid."""


def _normalize_route(route: str) -> str | None:
    if not isinstance(route, str) or "?" in route or "#" in route:
        return None
    if "\\" in route or "\x00" in route:
        return None
    if route.startswith("//"):
        return None
    normalized = "/" + route.lstrip("/")
    if normalized.startswith("//"):
        return None
    return normalized if normalized == REWARDSTABLE_ROUTE else None


def _normalize_base_path(base_path: str) -> str:
    if not isinstance(base_path, str) or not base_path:
        raise RewardstableCompatError("base_path must be a non-empty local path")
    if "?" in base_path or "#" in base_path or "\\" in base_path or "\x00" in base_path:
        raise RewardstableCompatError("base_path must not contain query, fragment, backslash, or NUL")
    if not base_path.startswith("/") or base_path.startswith("//"):
        raise RewardstableCompatError("base_path must be root-relative")
    if any(part == ".." for part in base_path.split("/")):
        raise RewardstableCompatError("base_path must not contain parent traversal")
    return "/" + base_path.strip("/") + "/" if base_path.strip("/") else "/"


def _actual_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _source_variant(source_sha256: str, actual_sha256: str) -> str:
    if (
        source_sha256 == SOURCE16_REWARDSTABLE_SOURCE_SHA256
        and actual_sha256 == V46_REWARDSTABLE_DERIVED_SHA256
    ):
        return "source16_utf8_bom_decoded"
    if source_sha256 == SOURCE16_REWARDSTABLE_SOURCE_SHA256:
        return "source16_utf8_bom"
    if (
        source_sha256 == V46_REWARDSTABLE_DERIVED_SHA256
        and actual_sha256 == V46_REWARDSTABLE_DERIVED_SHA256
    ):
        return "v46_bomless_same_script_body"
    return "unknown"


def rewrite_rewardstable_script(
    text: str,
    route: str,
    source_sha256: str,
    base_path: str,
) -> tuple[str, bool, dict[str, Any]]:
    """Rewrite the two exact reward table button URLs.

    An unrelated route is returned byte-for-byte unchanged and is not
    source-guarded.  The exact route requires both the caller's source SHA and
    the text's computed SHA to be one of the two reviewed source variants.
    ``base_path`` is normalized to one local root-relative prefix; query and
    fragment bypasses are rejected.
    """

    if not isinstance(text, str):
        raise RewardstableCompatError("text must be a string")
    normalized = _normalize_route(route)
    stats: dict[str, Any] = {
        "route": normalized or route,
        "handled": False,
        "changed": False,
        "source_sha256": str(source_sha256 or "").casefold(),
        "actual_source_sha256": None,
        "source_variant": "unknown",
        "alliance_replacements": 0,
        "horde_replacements": 0,
        "absolute_button_replacements": 0,
    }
    if normalized is None:
        return text, False, stats

    supplied = str(source_sha256 or "").casefold()
    actual = _actual_sha256(text)
    stats["actual_source_sha256"] = actual
    if supplied not in ACCEPTED_SOURCE_SHA256:
        raise RewardstableCompatError(
            f"rewardstable source SHA mismatch: expected one of {sorted(ACCEPTED_SOURCE_SHA256)}, got {supplied}"
        )
    # Source16's recorded bytes include a BOM, while the exporter passes the
    # utf-8-sig-decoded text to this hook.  Permit only the exact known body
    # represented by the v46 hash; all other supplied/text combinations are
    # source drift.
    allowed_actual = {supplied}
    if supplied == SOURCE16_REWARDSTABLE_SOURCE_SHA256:
        allowed_actual.add(V46_REWARDSTABLE_DERIVED_SHA256)
    if actual not in allowed_actual:
        raise RewardstableCompatError(
            f"rewardstable text SHA mismatch: expected {sorted(allowed_actual)}, got {actual}"
        )
    stats["source_variant"] = _source_variant(supplied, actual)

    prefix = _normalize_base_path(base_path)
    alliance_count = text.count(_ALLIANCE_LITERAL)
    horde_count = text.count(_HORDE_LITERAL)
    if alliance_count != 1 or horde_count != 1:
        raise RewardstableCompatError(
            "rewardstable button literal count mismatch: "
            f"alliance={alliance_count}, horde={horde_count}; expected one each"
        )

    rewritten = text.replace(
        _ALLIANCE_LITERAL,
        f"url({prefix}{ALLIANCE_IMAGE_ROUTE.lstrip('/')})",
        1,
    ).replace(
        _HORDE_LITERAL,
        f"url({prefix}{HORDE_IMAGE_ROUTE.lstrip('/')})",
        1,
    )
    stats["alliance_replacements"] = 1
    stats["horde_replacements"] = 1
    stats["absolute_button_replacements"] = 2
    stats["handled"] = True
    stats["changed"] = rewritten != text
    if not stats["changed"]:
        raise RewardstableCompatError("rewardstable rewrite produced no change")
    return rewritten, True, stats


__all__ = [
    "ACCEPTED_SOURCE_SHA256",
    "ALLIANCE_IMAGE_ROUTE",
    "HORDE_IMAGE_ROUTE",
    "REWARDSTABLE_ROUTE",
    "REWARDSTABLE_SCRIPT_ROUTE",
    "RewardstableCompatError",
    "SOURCE16_REWARDSTABLE_SOURCE_SHA256",
    "V46_REWARDSTABLE_DERIVED_SHA256",
    "rewrite_rewardstable_script",
]

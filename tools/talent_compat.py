"""Bounded compatibility rewrites for the historical talent calculator scripts.

The two talent include scripts are frozen Source15 JavaScript.  A generic
root-literal/CSS pass can mistake an escaped CSS quote in a JavaScript string
for the end of that string.  This module therefore accepts only the two exact
Source15 bytes and performs the small, auditable URL repair needed by the
Pages export.  The dynamic talent-tree expressions remain source text,
including the ``... treeName + '/background.jpg'`` composition.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from typing import Any


LOCALIZE_ROUTE = "/shared/global/talents/includes/localize.js"
PRINTOUTTOP_ROUTE = "/shared/global/talents/includes/printOutTop.js"

# These are the bytes used by the frozen local Source15 site (offline/site),
# rather than the later v39/v41 derived bytes.  Keep the guard strict so a
# future source or a previously-derived script cannot silently receive this
# narrow rewrite.
LOCALIZE_SOURCE_SHA256 = "e13769500cc7853b7c4d835f0380cf971cbec5f8fc061c3f1f83cf3dea1e6972"
PRINTOUTTOP_SOURCE_SHA256 = "618c92c0d00c960f651aad4364a05e93cfb785df38b2b63902febaeb06d26f04"

# Descriptive aliases make provenance callers less likely to copy a route's
# hash into the wrong call site.
TALENT_LOCALIZE_SOURCE_SHA256 = LOCALIZE_SOURCE_SHA256
TALENT_PRINTOUTTOP_SOURCE_SHA256 = PRINTOUTTOP_SOURCE_SHA256


class TalentCompatError(RuntimeError):
    """Raised when a guarded talent script no longer matches its contract."""


_TEMPLATE_LITERAL = '"/info/classes/index.html"+ nlclass +"/talents.html'
_IMG_PATH_LITERAL = 'var imgPath = "/shared/global/talents";'
_BACKGROUND_EXPRESSION = "imgPath +'/'+ nlclass +'/images/'+ imgDir + treeName +'/background.jpg"

# Only complete, reviewed fixed URLs in localize.js are localized.  The
# printOutTop.js paths all intentionally contain a runtime expression rooted
# at imgPath and are left untouched.
_FIXED_LOCALIZE_PATHS = (
    "/info/classes/includes-new/images/bot-box/top-left.gif",
    "/info/classes/includes-new/images/bot-box/top.gif",
    "/info/classes/includes-new/images/bot-box/top-right.gif",
    "/info/classes/includes-new/images/bot-box/left.gif",
    "/info/classes/includes-new/images/bot-box/right.gif",
    "/info/classes/includes-new/images/bot-box/bot-left.gif",
    "/info/classes/includes-new/images/bot-box/bot.gif",
    "/info/classes/includes-new/images/bot-box/bot-right.gif",
    "/shared/wow-com/images/layout/pixel.gif",
    "/links/images/border-right.gif",
)
_FIXED_PATH_RE = re.compile(
    "|".join(re.escape(path) for path in sorted(_FIXED_LOCALIZE_PATHS, key=len, reverse=True))
)


def _normalize_route(route: str) -> str | None:
    """Normalize one leading slash while rejecting query/hash bypasses."""

    if not isinstance(route, str) or "?" in route or "#" in route:
        return None
    normalized = "/" + route.lstrip("/")
    return normalized if normalized in {LOCALIZE_ROUTE, PRINTOUTTOP_ROUTE} else None


def _normalize_base_path(base_path: str) -> str:
    if not isinstance(base_path, str) or not base_path:
        raise TalentCompatError("talent compatibility base_path must be a non-empty local path")
    if "?" in base_path or "#" in base_path or "\\" in base_path:
        raise TalentCompatError("talent compatibility base_path must not contain query, fragment, or backslash")
    if not base_path.startswith("/") or base_path.startswith("//"):
        raise TalentCompatError("talent compatibility base_path must be root-relative")
    prefix = "/" + base_path.strip("/") + "/" if base_path.strip("/") else "/"
    return prefix


def _assert_source(route: str, source_sha256: str, text: str, expected_sha256: str) -> None:
    supplied = str(source_sha256 or "").casefold()
    if supplied != expected_sha256:
        raise TalentCompatError(
            f"Talent compatibility source SHA mismatch for {route}: "
            f"expected {expected_sha256}, got {supplied}"
        )
    actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if actual != expected_sha256:
        raise TalentCompatError(
            f"Talent compatibility text SHA mismatch for {route}: "
            f"expected {expected_sha256}, got {actual}"
        )


def _safe_localized_url(localized: Any, raw: str) -> str:
    if not isinstance(localized, str) or not localized:
        raise TalentCompatError(f"localize_url_callback returned an empty URL for {raw}")
    if "\r" in localized or "\n" in localized or "'" in localized or '"' in localized or "\\" in localized:
        raise TalentCompatError(f"localize_url_callback returned an unsafe JavaScript URL for {raw}")
    if not localized.startswith("/") or localized.startswith("//"):
        raise TalentCompatError(f"localize_url_callback returned a non-local URL for {raw}: {localized!r}")
    return localized


def _call_localizer(
    callback: Callable[..., str],
    raw: str,
    *,
    context: str,
) -> str:
    """Call the deliberately small URL callback protocol.

    Exporter callers normally provide ``lambda raw, context: ...``.  A
    one-argument callback remains accepted for small fixture and audit tools.
    """

    try:
        result = callback(raw, context=context)
    except TypeError as first_error:
        try:
            result = callback(raw)
        except TypeError:
            raise TalentCompatError(
                "localize_url_callback must accept (raw, *, context) or (raw)"
            ) from first_error
    return _safe_localized_url(result, raw)


def _rewrite_js_string_literals(
    text: str,
    *,
    callback: Callable[..., str],
    stats: dict[str, Any],
) -> str:
    """Rewrite reviewed fixed paths inside real JS strings only.

    The small scanner skips line/block comments and honors JavaScript escape
    pairs.  This matters for ``url(\'/links/...\')``: the escaped quote is
    copied byte-for-byte while only the URL token changes.
    """

    pieces: list[str] = []
    i = 0
    n = len(text)
    replacements = 0
    by_context: dict[str, int] = {"image": 0, "css_url": 0}

    while i < n:
        if text.startswith("//", i):
            end = text.find("\n", i)
            if end < 0:
                pieces.append(text[i:])
                break
            pieces.append(text[i:end])
            i = end
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end < 0:
                raise TalentCompatError("unterminated JavaScript block comment")
            end += 2
            pieces.append(text[i:end])
            i = end
            continue
        if text[i] not in {"'", '"'}:
            pieces.append(text[i])
            i += 1
            continue

        quote = text[i]
        i += 1
        content_parts: list[str] = []
        while i < n:
            char = text[i]
            if char == "\\":
                if i + 1 >= n:
                    raise TalentCompatError("unterminated JavaScript string escape")
                content_parts.append(text[i : i + 2])
                i += 2
                continue
            if char == quote:
                break
            content_parts.append(char)
            i += 1
        if i >= n:
            raise TalentCompatError("unterminated JavaScript string literal")
        content = "".join(content_parts)

        def replace(match: re.Match[str]) -> str:
            nonlocal replacements
            raw = match.group(0)
            context = "css_url" if raw == "/links/images/border-right.gif" else "image"
            localized = _call_localizer(callback, raw, context=context)
            replacements += 1
            by_context[context] += 1
            return localized

        rewritten_content = _FIXED_PATH_RE.sub(replace, content)
        pieces.append(quote + rewritten_content + quote)
        i += 1

    stats["fixed_url_replacements"] = replacements
    stats["fixed_url_context_counts"] = by_context
    return "".join(pieces)


def _rewrite_localize(text: str, *, base_path: str, callback: Callable[..., str], stats: dict[str, Any]) -> str:
    # The prior generic pass incorrectly treated this dynamic directory as the
    # /info/classes/index.html route.  Keep nlclass and the query/template
    # suffix untouched, but make the local directory valid in the archive.
    template_count = text.count(_TEMPLATE_LITERAL)
    if template_count != 2:
        raise TalentCompatError(
            "Talent localize template literal count mismatch: expected 2, "
            f"got {template_count}"
        )
    fixed_template = f'"{base_path}info/classes/"+ nlclass +"/talents.html'
    text = text.replace(_TEMPLATE_LITERAL, fixed_template)
    stats["template_links_repaired"] = template_count

    if text.count(_IMG_PATH_LITERAL) != 1:
        raise TalentCompatError(
            "Talent localize imgPath literal count mismatch: expected 1, "
            f"got {text.count(_IMG_PATH_LITERAL)}"
        )
    text = text.replace(
        _IMG_PATH_LITERAL,
        f'var imgPath = "{base_path}shared/global/talents";',
        1,
    )
    stats["img_path_prefix_replacements"] = 1

    return _rewrite_js_string_literals(text, callback=callback, stats=stats)


def rewrite_talent_script(
    text: str,
    route: str,
    source_sha256: str,
    base_path: str,
    localize_url_callback: Callable[..., str],
) -> tuple[str, bool, dict[str, Any]]:
    """Apply the exact Source15 talent compatibility rewrite.

    ``route`` may omit its leading slash, but query and fragment variants are
    never accepted.  Unknown routes are returned unchanged with ``handled``
    false.  ``localize.js`` receives fixed URL localization and the two valid
    ``.../classes/<nlclass>/talents.html`` template links.  ``printOutTop.js``
    is source-hash checked and preserved byte-for-byte so its dynamic image
    concatenation cannot be damaged by a generic URL pass.
    """

    normalized = _normalize_route(route)
    if normalized is None:
        return text, False, {"route": route, "handled": False, "reason": "route-not-in-scope"}
    prefix = _normalize_base_path(base_path)
    expected = LOCALIZE_SOURCE_SHA256 if normalized == LOCALIZE_ROUTE else PRINTOUTTOP_SOURCE_SHA256
    _assert_source(normalized, source_sha256, text, expected)
    stats: dict[str, Any] = {
        "route": normalized,
        "handled": True,
        "source_sha256": expected,
        "source_length": len(text.encode("utf-8")),
        "changed": False,
    }

    if normalized == LOCALIZE_ROUTE:
        rewritten = _rewrite_localize(
            text,
            base_path=prefix,
            callback=localize_url_callback,
            stats=stats,
        )
    else:
        if text.count(_BACKGROUND_EXPRESSION) != 1:
            raise TalentCompatError(
                "Talent printOutTop dynamic background expression count mismatch: expected 1, "
                f"got {text.count(_BACKGROUND_EXPRESSION)}"
            )
        stats["dynamic_background_expressions_preserved"] = 1
        stats["fixed_url_replacements"] = 0
        stats["fixed_url_context_counts"] = {"image": 0, "css_url": 0}
        rewritten = text

    stats["changed"] = rewritten != text
    stats["output_length"] = len(rewritten.encode("utf-8"))
    return rewritten, True, stats


__all__ = [
    "LOCALIZE_ROUTE",
    "PRINTOUTTOP_ROUTE",
    "LOCALIZE_SOURCE_SHA256",
    "PRINTOUTTOP_SOURCE_SHA256",
    "TALENT_LOCALIZE_SOURCE_SHA256",
    "TALENT_PRINTOUTTOP_SOURCE_SHA256",
    "TalentCompatError",
    "rewrite_talent_script",
]

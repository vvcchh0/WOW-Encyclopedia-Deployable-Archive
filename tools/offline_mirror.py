#!/usr/bin/env python3
"""Build and serve a bounded, derived offline copy of the 2008 encyclopedia.

The source tree and backup archives are treated as read-only.  ``build`` copies
the verified files named by ``mirror/20080512/url-map.json`` into a separate
site tree, rewriting only the derived copies.  ``serve`` exposes that tree on
loopback with a small route and request-log API; it never fetches missing
resources.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import mimetypes
import os
import posixpath
import re
import shutil
import socket
import sys
import threading
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL_MAP = ROOT / "mirror/20080512/url-map.json"
DEFAULT_OVERLAY = ROOT / "research/gap-review-20261011/reviewed-index-overlay.json"
DEFAULT_SITE = ROOT / "offline/site"
DEFAULT_MANIFEST = ROOT / "offline/build-manifest.json"
DEFAULT_SUPPORT = ROOT / "offline/support"
DEFAULT_MENU_META = ROOT / "research/gap-review-20261011/late/entity/01-menu-xml-20080914055020.json"

# ``navtreefunctions.js`` resolves a page by both its display label and the
# normalized URL.  A few preserved pages have a valid label but no exact
# node in the 2008 menu tree, so the historical script leaves ``result``
# unset and later calls ``tree(undefined)``.  These are deliberately
# compatibility-only ancestor/known-node fallbacks from the runtime audits;
# they do not rewrite the page's source ``pageId`` or claim that the node is
# an exact match.
_NAVTREE_COMPAT_NODES = {
    # These two pages carry historical labels/locations that do not match the
    # 2008 guide tree's URL test.  The corresponding nodes are present in the
    # loaded navtree.js: Player vs Player (1_9) and Dressing Room (1_5_7).
    "/info/faq/pvppage.html": "1_9",
    "/info/underdev/dressingroom.html": "1_5_7",
    "/downloads/wallpapers/valentines/index.html": "1_8_6",
    "/community/chinaicoke.html": "1_6",
    "/community/comics/2008-05.html": "1_6_2",
    "/gadgetzantimes/archives.html": "1_8_8",
    "/info/faq/parentalcontrols.xml": "1_10_14",
    "/pvp/rewards-arena-weapons.html": "1_9_11_4",
    "/pvp/rewards-general-armor.html": "1_9_11_2",
    "/pvp/rewards-arena-class-armor.html": "1_9_11",
    "/pvp/rewards-class-armor.html": "1_9_11",
    "/pvp/rewards-veterans-armor.html": "1_9_11",
}

_NAVTREE_COMPAT_MARKER = "offline-nav-alias-fallback-v1"
_MOUNTS_FOOTER_GUARD_MARKER = "offline-mounts-footer-guard-v1"
_FORUM_OPERA_COMPAT_MARKER = "offline-forum-opera-compat-v1"
_POLICY_RUNTIME_GUARD_MARKER = "offline-policy-runtime-guards-v1"

_META_REFRESH_URL_RE = re.compile(
    r"(?P<prefix>\burl\s*=\s*)"
    r"(?P<quote>['\"]?)"
    r"(?P<url>[^'\";]*?)"
    r"(?P=quote)"
    r"(?P<suffix>\s*(?:;.*)?$)",
    re.I,
)
DEFAULT_CSP = (
    "default-src 'self' data: blob:; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "connect-src 'self'; frame-src 'self'; object-src 'none'"
)


class MirrorError(RuntimeError):
    """Raised when a source map or derived site cannot be validated."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_to_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def file_mime(mime: str | None, path: str) -> str:
    """Return the source-declared MIME, with a safe standard fallback."""

    if mime:
        return mime
    guessed, _ = mimetypes.guess_type(path)
    if guessed:
        return guessed
    return "application/octet-stream"


def mime_base(mime: str) -> str:
    return mime.split(";", 1)[0].strip().casefold()


def charset_for(mime: str, data: bytes) -> str:
    match = re.search(r"charset\s*=\s*['\"]?([A-Za-z0-9._-]+)", mime, re.I)
    if match:
        return match.group(1)
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    return "utf-8"


def host_of(url: str) -> str:
    try:
        return (urllib.parse.urlsplit(url).hostname or "").casefold().rstrip(".")
    except ValueError:
        return ""


def is_site_host(host: str) -> bool:
    host = host.casefold().rstrip(".")
    return host == "worldofwarcraft.com" or host.endswith(".worldofwarcraft.com")


def is_allowed_source_host(host: str) -> bool:
    host = host.casefold().rstrip(".")
    return is_site_host(host) or host == "blizzard.com" or host.endswith(".blizzard.com")


def canonical_url(url: str) -> str:
    """Normalize only host case and default ports for map lookups."""

    parsed = urllib.parse.urlsplit(url)
    if not parsed.scheme or not parsed.netloc:
        return url
    host = (parsed.hostname or "").casefold()
    try:
        port = parsed.port
    except ValueError:
        port = None
    default = (parsed.scheme.casefold() == "http" and port == 80) or (
        parsed.scheme.casefold() == "https" and port == 443
    )
    netloc = host if not parsed.username and not parsed.password else parsed.netloc
    if port is not None and not default:
        netloc = f"{netloc}:{port}"
    return urllib.parse.urlunsplit(
        (parsed.scheme.casefold(), netloc, parsed.path or "/", parsed.query, parsed.fragment)
    )


_PRIMARY_ORIGIN_HOST = "www.worldofwarcraft.com"


def origin_namespace_host(url: str) -> str:
    """Return the stable host namespace used by origin-aware local routes.

    ``worldofwarcraft.com`` and ``www.worldofwarcraft.com`` are the same
    historical site origin.  Other approved hosts stay isolated.  A
    non-default port is retained in a filesystem-safe form so two mapped
    origins cannot collide accidentally.
    """

    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").casefold().rstrip(".")
    if host in {"worldofwarcraft.com", "www.worldofwarcraft.com"}:
        host = _PRIMARY_ORIGIN_HOST
    try:
        port = parsed.port
    except ValueError:
        port = None
    default_port = (parsed.scheme.casefold() == "http" and port == 80) or (
        parsed.scheme.casefold() == "https" and port == 443
    )
    if port is not None and not default_port:
        host = f"{host}_{port}"
    return host


def origin_key(url: str) -> str:
    """Return a host+path key for localizer lookups, excluding query/fragment."""

    return f"{origin_namespace_host(url)}{route_path(url)}"


def is_primary_origin(url: str) -> bool:
    return origin_namespace_host(url) == _PRIMARY_ORIGIN_HOST


def origin_route(url: str) -> str:
    """Namespace a non-primary source URL beneath ``/_origins``."""

    path = route_path(url)
    if path == "/":
        path = "/index.html"
    return f"/_origins/{origin_namespace_host(url)}{path}"


def route_path(url: str) -> str:
    path = urllib.parse.urlsplit(url).path or "/"
    if not path.startswith("/"):
        path = "/" + path
    return path


def canonical_request_path(
    path: str,
    *,
    route_keys: Iterable[str],
    aliases: Iterable[str],
    special_routes: Iterable[str],
) -> tuple[str, bool]:
    """Return a safe local route for harmless URL spelling variations.

    Historical menu code emits duplicate slashes, ``./`` segments, trailing
    spaces, and directory links with a trailing slash.  These spellings do
    not grant access outside the site because traversal and backslashes are
    rejected before this function runs.  Prefer a known manifest/alias route
    when one exists; otherwise use the normalized route so an uncollected
    path receives the ordinary local missing-page response instead of a
    misleading security rejection.
    """

    cleaned = path.strip(" \t\r\n") or "/"
    collapsed = re.sub(r"/{2,}", "/", cleaned)
    normalized = posixpath.normpath(collapsed)
    if normalized == ".":
        normalized = "/"
    known = set(route_keys) | set(aliases) | set(special_routes)
    candidates: list[str] = []
    for candidate in (cleaned, collapsed, normalized, collapsed.rstrip("/") or "/"):
        if candidate not in candidates:
            candidates.append(candidate)
    for candidate in candidates:
        if candidate in known:
            return candidate, candidate != path
    return normalized, normalized != path


def ensure_safe_site_path(site: Path, candidate: Path) -> None:
    site_resolved = site.resolve()
    candidate_resolved = candidate.resolve()
    try:
        candidate_resolved.relative_to(site_resolved)
    except ValueError as exc:
        raise MirrorError(f"derived path escapes site: {candidate}") from exc


def safe_source_path(path: Path) -> None:
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError as exc:
        raise MirrorError(f"source path escapes workspace: {path}") from exc


def encoded_missing_query(source_url: str, requested_url: str, reason: str) -> str:
    values = {
        "source": source_url[:512],
        "requested": requested_url[:512],
        "reason": reason,
    }
    return urllib.parse.urlencode(values, quote_via=urllib.parse.quote)


class ReferenceRecorder:
    """Collect bounded evidence about rewritten resource references."""

    def __init__(self, source_route: str, source_url: str):
        self.source_route = source_route
        self.source_url = source_url
        self.records: list[dict[str, Any]] = []
        self.counts: Counter[str] = Counter()

    def add(
        self,
        literal: str,
        resolved: str,
        action: str,
        target: str,
        context: str,
        reason: str | None = None,
    ) -> None:
        self.counts[action] += 1
        # Keep the manifest useful without allowing a pathological script to
        # grow it without bound.
        if len(self.records) < 400:
            self.records.append(
                {
                    "literal": literal[:512],
                    "resolved_url": resolved[:1024],
                    "action": action,
                    "target": target,
                    "context": context,
                    "reason": reason,
                }
            )


class Localizer:
    """Resolve source URLs to local routes or explicit offline placeholders."""

    def __init__(
        self,
        route_entries: dict[str, dict[str, Any]],
        invalid_urls: set[str],
        *,
        root_target: str = "/info/encyclopedia/index.xml",
        route_aliases: dict[str, str] | None = None,
        origin_index: dict[str, str] | None = None,
    ):
        self.route_entries = route_entries
        self.invalid_urls = invalid_urls
        self.root_target = root_target
        self.route_aliases = dict(route_aliases or {})
        self.origin_index = dict(origin_index or {})
        # Extra validated maps may contain explicitly acquired subdomains
        # (for example an armory or Blizzard host).  Track only hosts present
        # in the supplied maps; this keeps unknown external URLs on the
        # placeholder path while allowing mapped resources to be localized.
        self.mapped_hosts = {
            (urllib.parse.urlsplit(str(item.get("logical_url", ""))).hostname or "").casefold().rstrip(".")
            for item in route_entries.values()
            if item.get("logical_url")
        }
        self.mapped_hosts.update(
            (urllib.parse.urlsplit(str(item.get("source_base_url", ""))).hostname or "").casefold().rstrip(".")
            for item in route_entries.values()
            if item.get("source_base_url")
        )

    def _lookup(self, absolute: str) -> tuple[str, dict[str, Any]] | None:
        parsed = urllib.parse.urlsplit(absolute)
        if parsed.scheme.casefold() not in {"http", "https"}:
            return None
        host = (parsed.hostname or "").casefold().rstrip(".")
        if not (is_allowed_source_host(host) or host in self.mapped_hosts):
            return None
        path = route_path(absolute)
        # Prefer the explicit host+path index.  A forum resource and a main
        # site resource may legitimately share a path; path-only lookup is
        # only the compatibility fallback after this exact-origin attempt.
        origin_target = self.origin_index.get(origin_key(absolute))
        target_path = origin_target or self.route_aliases.get(path, path)
        entry = self.route_entries.get(target_path)
        def same_origin_host(candidate: dict[str, Any]) -> bool:
            candidate_host = host_of(str(candidate.get("logical_url", "")))
            main_hosts = {"worldofwarcraft.com", "www.worldofwarcraft.com"}
            return host == candidate_host or (host in main_hosts and candidate_host in main_hosts)
        # Routes are local paths, but an unrelated official host may use the
        # same path. Never substitute the WoW homepage for Blizzard's root.
        # An origin_index entry is an explicitly recorded source_base_url
        # alias (for example forum-coc.html served from the forums host), so
        # it is allowed to point at a page whose logical URL uses the main
        # host.  Path-only fallback still requires same-origin protection.
        if entry and not origin_target and not same_origin_host(entry):
            entry = None
        # The original site used the domain root as a common home link, while
        # the verified map's canonical homepage entity lives under the
        # encyclopedia path.  Preserve that navigation locally through the
        # same explicit alias that the server exposes.
        if not entry and path == "/":
            homepage = self.route_entries.get(self.root_target)
            if homepage and same_origin_host(homepage):
                suffix = ""
                if parsed.query:
                    suffix += "?" + parsed.query
                if parsed.fragment:
                    suffix += "#" + parsed.fragment
                target = self.root_target + suffix
                return target, homepage
        if not entry:
            return None
        entry_url = canonical_url(entry["logical_url"])
        if entry_url in self.invalid_urls:
            return None
        suffix = ""
        if parsed.query:
            suffix += "?" + parsed.query
        if parsed.fragment:
            suffix += "#" + parsed.fragment
        return target_path + suffix, entry

    def localize(
        self,
        raw: str,
        *,
        base_url: str,
        context: str,
        recorder: ReferenceRecorder,
    ) -> str:
        literal = raw.strip()
        if not literal:
            recorder.add(raw, base_url, "preserved", raw, context, "empty reference")
            return raw
        lowered = literal.casefold()
        if lowered.startswith(("#", "javascript:", "mailto:", "tel:", "data:", "about:")):
            recorder.add(raw, base_url, "preserved", raw, context, "non-network reference")
            return raw
        try:
            absolute = urllib.parse.urljoin(base_url, literal)
            parsed = urllib.parse.urlsplit(absolute)
        except ValueError:
            absolute = literal
            parsed = urllib.parse.SplitResult("", "", literal, "", "")
        if parsed.scheme.casefold() not in {"http", "https"}:
            target = self._placeholder(literal, base_url, context, reason="unresolved-relative")
            recorder.add(raw, absolute, "placeholder", target, context, "unresolved-relative")
            return target
        if context == "frame" and (parsed.hostname or "").casefold() == "ads.blizzard.com":
            target = "/__offline/excluded-frame.html?" + encoded_missing_query(base_url, absolute, "excluded-dynamic-advertisement")
            recorder.add(raw, absolute, "placeholder", target, context, "excluded-dynamic-advertisement")
            return target
        found = self._lookup(absolute)
        if found:
            target, _ = found
            recorder.add(raw, absolute, "localized", target, context, "verified local source")
            return target

        reason = "invalid-overlay-or-uncollected-site-resource" if is_site_host(parsed.hostname or "") else "external-or-uncollected-resource"
        target = self._placeholder(absolute, base_url, context, reason=reason)
        recorder.add(raw, absolute, "placeholder", target, context, reason)
        return target

    @staticmethod
    def _placeholder(raw: str, source_url: str, context: str, *, reason: str) -> str:
        query = encoded_missing_query(source_url, raw, reason)
        if context in {"image", "background", "css_url", "srcset"}:
            return "/__offline/missing-image.svg?" + query
        if context in {"script", "script_url"}:
            return "/__offline/empty.js?" + query
        if context in {"stylesheet", "css_import"}:
            return "/__offline/empty.css?" + query
        return "/__offline/missing.html?" + query


def rewrite_css(text: str, *, base_url: str, localizer: Localizer, recorder: ReferenceRecorder) -> str:
    url_re = re.compile(r"url\(\s*(?P<quote>['\"]?)(?P<url>.*?)(?P=quote)\s*\)", re.I | re.S)

    # Protect imports while rewriting ordinary CSS url() values.  An import
    # is a stylesheet dependency and must use the empty.css placeholder when
    # unavailable; treating it as an image makes the browser abort the
    # stylesheet load.  Tokens keep the generic url() pass from processing an
    # already-localized import a second time.
    protected_imports: list[tuple[str, str]] = []

    import_url_re = re.compile(
        r"(?P<prefix>@import\s+url\(\s*)(?P<quote>['\"]?)(?P<url>.*?)(?P=quote)(?P<suffix>\s*\))",
        re.I | re.S,
    )
    import_string_re = re.compile(
        r"(?P<prefix>@import\s+)(?P<quote>['\"])(?P<url>.*?)(?P=quote)",
        re.I | re.S,
    )

    def protect_import(match: re.Match[str]) -> str:
        raw = match.group("url")
        local = localizer.localize(raw, base_url=base_url, context="css_import", recorder=recorder)
        quote = match.group("quote")
        replacement = (
            match.group("prefix")
            + quote
            + (local.replace(quote, "%22") if quote else local)
            + quote
            + match.groupdict().get("suffix", "")
        )
        token = f"__OFFLINE_CSS_IMPORT_{len(protected_imports)}__"
        protected_imports.append((token, replacement))
        return token

    text = import_url_re.sub(protect_import, text)
    text = import_string_re.sub(protect_import, text)

    def url_replace(match: re.Match[str]) -> str:
        raw = match.group("url")
        if raw.strip().casefold().startswith("/__offline/"):
            return match.group(0)
        local = localizer.localize(raw, base_url=base_url, context="css_url", recorder=recorder)
        return "url(\"" + local.replace('"', "%22") + "\")"

    text = url_re.sub(url_replace, text)
    for token, replacement in protected_imports:
        text = text.replace(token, replacement)
    return text


def rewrite_generic_markup(text: str, *, base_url: str, localizer: Localizer, recorder: ReferenceRecorder) -> str:
    attr_re = re.compile(
        r"(?P<lead>\b(?P<name>src|href|data|background|action|poster|url)\s*=\s*)"
        r"(?P<quote>['\"]?)(?P<value>[^\s>\"']+)(?P=quote)",
        re.I,
    )

    def attr_replace(match: re.Match[str]) -> str:
        name = match.group("name").casefold()
        context = "image" if name in {"background", "poster"} else "resource"
        if name == "src":
            context = "image" if re.search(r"\.(?:gif|jpe?g|png|webp|swf)(?:[?#]|$)", match.group("value"), re.I) else "script_url"
        if name == "href":
            context = "stylesheet" if re.search(r"\.css(?:[?#]|$)", match.group("value"), re.I) else "navigation"
        local = localizer.localize(match.group("value"), base_url=base_url, context=context, recorder=recorder)
        return match.group("lead") + '"' + local.replace('"', "%22") + '"'

    return attr_re.sub(attr_replace, text)


def rewrite_mounts_footer_optional_guards(
    text: str,
    *,
    base_url: str,
    recorder: ReferenceRecorder,
) -> str:
    """Guard only the known optional footer fragments on the mounts page.

    ``/info/basics/mounts.html`` has no pageId/navtree setup in its preserved
    source, while its shared footer still assumes those globals exist.  The
    historical footer is optional decoration; leave it untouched when its
    dependencies are present and skip only the individual fragment when they
    are absent.  This is deliberately route- and-pattern-scoped rather than a
    global exception handler.
    """

    if route_path(base_url).casefold() != "/info/basics/mounts.html":
        return text
    if _MOUNTS_FOOTER_GUARD_MARKER in text:
        return text

    original = text
    details: list[str] = []
    strategy_guard = re.compile(
        r"\bif\s*\(\s*stripId\s*\(\s*Menu1\s*\[\s*0\s*\]\s*\)\s*==\s*['\"]Game Guide['\"]\s*\)",
        re.I,
    )
    text, count = strategy_guard.subn(
        'if (typeof stripId == "function" && typeof Menu1 != "undefined" && Menu1 && Menu1[0] && '
        'typeof pageId != "undefined" && stripId(Menu1[0]) == "Game Guide")',
        text,
        count=1,
    )
    if count:
        details.append("strategy mailto fragment: guard stripId/Menu1/pageId")

    error_guard = re.compile(
        r"\bif\s*\(\s*document\.location\.href\.indexOf\(\s*['\"]\/account\/['\"]\s*\)\s*==\s*-1\s*"
        r"&&\s*document\.location\.href\.indexOf\(\s*['\"]\/loginsupport\/['\"]\s*\)\s*==\s*-1\s*\)",
        re.I,
    )
    text, count = error_guard.subn(
        'if (typeof stripId == "function" && typeof pageId != "undefined" && '
        'document.location.href.indexOf("/account/") == -1 && '
        'document.location.href.indexOf("/loginsupport/") == -1)',
        text,
        count=1,
    )
    if count:
        details.append("error-report mailto fragment: guard stripId/pageId")

    subnav_guard = re.compile(r"\bprintSubNav\s*\(\s*result\s*,\s*2\s*\)\s*;?", re.I)
    text, count = subnav_guard.subn(
        'if (typeof printSubNav == "function" && typeof result != "undefined") printSubNav(result,2);',
        text,
        count=1,
    )
    if count:
        details.append("related-navigation fragment: guard printSubNav/result")

    related_guard = re.compile(r"\bprintRelatedLinks\s*\(\s*result\s*\)\s*;?", re.I)
    text, count = related_guard.subn(
        'if (typeof printRelatedLinks == "function" && typeof result != "undefined") printRelatedLinks(result);',
        text,
        count=1,
    )
    if count:
        details.append("related-links fragment: guard printRelatedLinks/result")

    if text == original:
        return text
    recorder.add(
        "<mounts-footer-optional-fragments>",
        base_url,
        "patched",
        _MOUNTS_FOOTER_GUARD_MARKER,
        "script",
        "runtime-page-audit-round4; " + "; ".join(details) +
        "; source bytes unchanged and no fallback functions were introduced",
    )
    return "/* " + _MOUNTS_FOOTER_GUARD_MARKER + " */\n" + text


def rewrite_policy_runtime_optional_guards(
    text: str,
    *,
    base_url: str,
    recorder: ReferenceRecorder,
) -> str:
    """Guard optional support-page calls when its uncollected JS is empty.

    ``/policy/`` references six ``/support/js`` files that are not present in
    the preserved maps.  The derived page therefore receives empty.js and the
    historical inline code raises before the article can finish loading.  We
    do not invent browser globals or no-op implementations: each optional
    branch runs unchanged when its historical dependency exists, and is
    skipped only when the expected function/flag is genuinely unavailable.
    """

    if (host_of(base_url) not in {"www.worldofwarcraft.com", "worldofwarcraft.com"}
            or route_path(base_url).rstrip("/").casefold() != "/policy"):
        return text
    if _POLICY_RUNTIME_GUARD_MARKER in text:
        return text

    original = text
    details: list[str] = []
    detection_guards = [
        (
            r"\bif\s*\(\s*is_ie6\s*&&\s*!is_ie7\s*\)",
            'if (typeof is_ie6 != "undefined" && is_ie6 && typeof is_ie7 != "undefined" && !is_ie7)',
            "is_ie6/is_ie7 conditional",
        ),
        (
            r"\bif\s*\(\s*is_ie7\s*\)",
            'if (typeof is_ie7 != "undefined" && is_ie7)',
            "is_ie7 conditional",
        ),
        (
            r"\bif\s*\(\s*is_opera\s*\)",
            'if (typeof is_opera != "undefined" && is_opera)',
            "is_opera conditional",
        ),
        (
            r"\bif\s*\(\s*is_safari\s*\)",
            'if (typeof is_safari != "undefined" && is_safari)',
            "is_safari conditional",
        ),
    ]
    for pattern, replacement, detail in detection_guards:
        text, count = re.subn(pattern, replacement, text, count=1, flags=re.I)
        if count:
            details.append("guarded " + detail)

    callback = re.compile(
        r"\baddEvent\(\s*window\s*,\s*(?P<quote>['\"])load(?P=quote)\s*,\s*function\s*\(\)\s*\{",
        re.I,
    )
    text, count = callback.subn(
        lambda match: (
            'if (typeof addEvent == "function" && typeof $ == "function") '
            + "addEvent(window, "
            + match.group("quote")
            + "load"
            + match.group("quote")
            + ", function () {"
        ),
        text,
        count=1,
    )
    if count:
        details.append("guarded menu load callback on addEvent/$")

    simple_calls = re.compile(
        r"(?P<call>\baddEvent\(\s*window\s*,\s*(?P<quote>['\"])load(?P=quote)\s*,\s*"
        r"(?P<function>bla|stretchContainer|addValues1|addValues2)\s*\)\s*;)",
        re.I,
    )

    def guard_simple(match: re.Match[str]) -> str:
        function_name = match.group("function")
        if function_name.casefold() == "bla":
            condition = 'typeof addEvent == "function" && typeof $ == "function"'
        else:
            condition = f'typeof addEvent == "function" && typeof {function_name} == "function"'
        return f"if ({condition}) {match.group('call')}"

    text, count = simple_calls.subn(guard_simple, text)
    if count:
        details.append("guarded optional load callbacks: " + ", ".join(sorted(set(
            match.group("function") for match in simple_calls.finditer(original)
        ))))

    if text == original:
        return text
    recorder.add(
        "<policy-support-runtime>",
        base_url,
        "patched",
        _POLICY_RUNTIME_GUARD_MARKER,
        "script",
        "runtime-page-audit-round7; missing /support/js dependencies are represented by empty.js; "
        + "; ".join(details)
        + "; no global shim or invented function was added; source bytes unchanged",
    )
    return "/* " + _POLICY_RUNTIME_GUARD_MARKER + " */\n" + text


def rewrite_script(text: str, *, base_url: str, localizer: Localizer, recorder: ReferenceRecorder) -> str:
    if re.search(r"(?i)(?:\b_gat\b|_getTracker|_trackPageview|google-analytics)", text):
        recorder.add(
            "<analytics-script>",
            base_url,
            "removed",
            "",
            "script",
            "offline build neutralized analytics tracker; no external beacon is allowed",
        )
        return "/* offline analytics tracker removed; no external request is made */\n"

    text = rewrite_policy_runtime_optional_guards(text, base_url=base_url, recorder=recorder)

    if route_path(base_url).rstrip("/").casefold() in {"/calendar", "/calendar/index.html"}:
        # The historical raid calendar has a year table ending in 2014.
        # Its preserved view must use the snapshot date, not today's year.
        text, count = re.subn(r"\btodate\s*=\s*new\s+Date\s*\(\s*\)",
                             "todate = new Date(2008, 4, 12, 21, 0, 44)", text, count=1)
        if count:
            recorder.add("<calendar-clock>", base_url, "patched", "2008-05-12", "script",
                         "historical raid calendar uses snapshot calendar date; original bytes preserved")
    if route_path(base_url).casefold() == "/community/fansites.html":
        text, count = re.subn(r'(\bpageId\s*=\s*[\"\'])Fansites([\"\'])', r'\1Fan Sites\2', text, count=1)
        if count:
            recorder.add("<fansites-pageId>", base_url, "patched", "Fan Sites", "script",
                         "historical label corrected to match preserved navigation; runtime-page-audit evidence")
    if route_path(base_url).casefold() == "/info/basics/mounts.html":
        text = rewrite_mounts_footer_optional_guards(text, base_url=base_url, recorder=recorder)
    if (host_of(base_url) in {"www.worldofwarcraft.com", "worldofwarcraft.com"}
            and route_path(base_url).casefold() == "/toplist/includes-client/js/logic.js"):
        # Both the initial date and the reset inside calculateDays determine
        # which historical data feeds are requested. Keep cookie expiry and
        # explicitly supplied dates on their original clocks.
        text, count = re.subn(r"\btoday\s*=\s*new\s+Date\s*\(\s*\)",
                             "today = new Date(2008, 4, 12, 21, 0, 44)", text)
        if count:
            recorder.add("<toplist-data-clock>", base_url, "patched", "2008-05-12", "script",
                         "historical Toplist feed selection uses snapshot date in initial and reset assignments; "
                         "cookie expiry and original entity bytes preserved; no statistics are fabricated")
    # The forum policy page is preserved under the main-site logical route
    # ``/policy/forum-coc.html`` but its verified source URL is the forum
    # origin ``/forum-coc.html``.  Its August 2008 detection.js defines the
    # namespaced ``Browser.opera`` property; the page's older inline fragment
    # still reads the removed global ``is_opera`` name.  Patch that one
    # condition only for this source alias, preferring the historical global
    # when a period-matched detection script supplies it and falling back to
    # the August namespace when it does not.  Do not add a global shim: the
    # archived detection script remains the sole source of the browser flag.
    forum_source = (
        host_of(base_url) == "forums.worldofwarcraft.com"
        and route_path(base_url).casefold() in {"/forum-coc.html", "/policy/forum-coc.html"}
    )
    if forum_source and _FORUM_OPERA_COMPAT_MARKER not in text:
        forum_opera = re.compile(r"\bif\s*\(\s*is_opera\s*\)", re.I)
        text, count = forum_opera.subn(
            'if (typeof is_opera != "undefined" ? is_opera : (typeof Browser != "undefined" && Browser && Browser.opera))',
            text,
            count=1,
        )
        if count:
            recorder.add(
                "if (is_opera)",
                base_url,
                "patched",
                "is_opera -> Browser.opera",
                "script",
                "runtime-page-audit-round6; logical /policy/forum-coc.html uses forum source alias /forum-coc.html; "
                "August detection.js defines Browser.opera; preserve the source entity and add no global shim",
            )
    if (host_of(base_url) in {"www.worldofwarcraft.com", "worldofwarcraft.com"}
            and route_path(base_url).casefold() in {"/", "/index.xml", "/index.html"}):
        # The original homepage derives the screenshot number from a HEAD
        # response's Date header. A loopback HTTP server correctly reports
        # today's date, which otherwise selects a nonexistent modern image.
        text, count = re.subn(
            r'\bxmlServerDate\s*=\s*new\s+Date\s*\(\s*xmlTimeVerification\.getResponseHeader\(\s*["\']Date["\']\s*\)\s*\)',
            "xmlServerDate = new Date(Date.UTC(2008, 4, 12, 21, 0, 44))",
            text, count=1,
        )
        if count:
            recorder.add("<homepage-ssotd-clock>", base_url, "patched", "2008-05-12T21:00:44Z", "script",
                         "snapshot clock replaces live HTTP Date for historical screenshot selection; original source bytes preserved")

    # functions.js is loaded from the historical page head, before the
    # search form exists in the DOM.  Its original unconditional assignment
    # therefore raises in a browser on every encyclopedia page.  Keep the
    # behavior, but schedule it after DOM construction and retain a null guard
    # for pages that do not render the shared form.
    if route_path(base_url).casefold().endswith("/new-hp/js/functions.js"):
        search_init = re.compile(
            r"if\s*\(\s*document\.location\.href\.indexOf\(\s*[\"']encyclopedia[\"']\s*\)\s*>\s*-?\s*1\s*\|\|\s*"
            r"document\.location\.href\.indexOf\(\s*[\"']Encyclopedia[\"']\s*\)\s*>\s*-?\s*1\s*\)\s*"
            r"document\.getElementById\(\s*[\"']searchType[\"']\s*\)\.selectedIndex\s*=\s*1\s*;?",
            re.I,
        )
        replacement = """(function () {
\tfunction setOfflineSearchType() {
\t\tif (document.location.href.indexOf(\"encyclopedia\") > -1 || document.location.href.indexOf(\"Encyclopedia\") > -1) {
\t\t\tvar searchType = document.getElementById(\"searchType\");
\t\t\tif (searchType) searchType.selectedIndex = 1;
\t\t}
\t}
\tif (document.readyState === \"loading\" && document.addEventListener)
\t\tdocument.addEventListener(\"DOMContentLoaded\", setOfflineSearchType, false);
\telse
\t\tsetOfflineSearchType();
}());"""
        patched, count = search_init.subn(replacement, text, count=1)
        if count:
            text = patched
            recorder.add(
                "<searchType-init>",
                base_url,
                "patched",
                "",
                "script",
                "guarded historical search form initialization until DOMContentLoaded",
            )
    # Menu scripts contain HTML fragments with both quoted and unquoted src
    # attributes.  Rewrite only URL-bearing attributes and CSS url(...) calls;
    # do not execute or evaluate the JavaScript.
    embedded = re.compile(
        r"(?P<lead>\b(?P<name>src|href|background|poster)\s*=\s*)"
        r"(?P<quote>['\"]?)(?P<value>(?:https?:)?//[^\s\"'<>]+|/[^\s\"'<>]+)"
        r"(?P<trailing>\s*)(?P=quote)",
        re.I,
    )

    def embedded_replace(match: re.Match[str]) -> str:
        name = match.group("name").casefold()
        value = match.group("value")
        if (value.startswith("/") and not value.startswith("//")
                and text[match.end():].lstrip().startswith("+")):
            # This is a JS URL prefix, e.g. img.src = "/icons/news-" +
            # expansion + ".gif". It already resolves on the local origin.
            # Localizing the prefix alone would splice a missing-page query
            # into the computed image URL.
            return match.group(0)
        if name in {"background", "poster"}:
            context = "image"
        elif name == "href":
            context = "stylesheet" if re.search(r"\.css(?:[?#]|$)", value, re.I) else "navigation"
        elif name == "src":
            if re.search(r"\.(?:gif|jpe?g|png|webp|svg|swf)(?:[?#]|$)", value, re.I):
                context = "image"
            elif re.search(r"\.(?:css)(?:[?#]|$)", value, re.I):
                context = "stylesheet"
            elif re.search(r"\.(?:js|mjs)(?:[?#]|$)", value, re.I):
                context = "script"
            else:
                context = "navigation"
        else:
            context = "navigation"
        local = localizer.localize(value, base_url=base_url, context=context, recorder=recorder)
        quote = match.group("quote")
        escaped = local.replace(quote, "%22") if quote else local
        return match.group("lead") + quote + escaped + match.group("trailing") + quote

    text = embedded.sub(embedded_replace, text)

    # JavaScript commonly builds CSS values dynamically, for example
    # ``"url('" + image.src + "')"``.  Treating the contents between
    # ``url(...)`` as a standalone URL would turn the expression into an
    # offline placeholder and, worse, insert a new quote into the surrounding
    # JavaScript string.  Leave CSS expressions in JavaScript untouched.  A
    # literal absolute URL is still handled by the quoted-string pass below;
    # root-relative paths are already local paths when served by this mirror.

    # Quoted full URLs are also commonly assigned to menu/link variables.  A
    # known source path is rewritten precisely; unknown absolute URLs become a
    # local missing-page route, preventing a browser network request.
    quoted = re.compile(
        r"(?P<quote>['\"])(?P<url>(?:https?:)?//[^'\"\s<>]+|/[^'\"\s<>]+)"
        r"(?P<trailing>\s*)(?P=quote)"
    )

    def quoted_replace(match: re.Match[str]) -> str:
        raw = match.group("url")
        # The embedded-attribute pass may have produced an offline
        # placeholder.  Do not feed that derived URL through the resolver a
        # second time (which would turn a missing-image placeholder into an
        # empty-script placeholder and can also grow its query recursively).
        if raw.casefold().startswith("/__offline/"):
            return match.group(0)
        # A bare protocol separator is ordinary JavaScript data (for example
        # ``urlString.indexOf("//")``), not a protocol-relative URL.  It has
        # no host and must never be rewritten as a root-relative route.
        if raw == "//" or (raw.startswith("//") and not urllib.parse.urlsplit(raw).netloc):
            return match.group(0)
        # Root-relative strings need no rewriting: they resolve against the
        # loopback mirror just as they did against the original site.  Only
        # absolute-origin strings require replacement to prevent an external
        # request.
        if raw.startswith("/") and not raw.startswith("//"):
            return match.group(0)
        if re.search(r"\.(?:gif|jpe?g|png|webp|svg|swf)(?:[?#]|$)", raw, re.I):
            context = "image"
        elif re.search(r"\.css(?:[?#]|$)", raw, re.I):
            context = "stylesheet"
        elif re.search(r"\.(?:js|mjs)(?:[?#]|$)", raw, re.I):
            context = "script"
        else:
            context = "script_url"
        local = localizer.localize(raw, base_url=base_url, context=context, recorder=recorder)
        return match.group("quote") + local.replace(match.group("quote"), "%22") + match.group("trailing") + match.group("quote")

    text = quoted.sub(quoted_replace, text)

    # ``findNode`` historically requires both the page label and a matching
    # normalized URL.  Some preserved child pages have no exact menu node, so
    # the subsequent ``tree(result)`` call receives ``undefined``.  Keep this
    # narrowly scoped to the original navtreefunctions.js and only fill an
    # unset result when the audited route has a loaded Menu node.  The source
    # pageId and body remain untouched; parent-only mappings intentionally
    # remain compatibility aliases rather than exact page identities.
    nav_route = route_path(base_url).casefold()
    if (
        nav_route == "/shared/wow-com/includes-client/navtreefunctions.js"
        and _NAVTREE_COMPAT_MARKER not in text
    ):
        find_call = re.compile(
            r"findNode\(\s*['\"]1['\"]\s*,\s*['\"]_['\"]\s*,\s*pageId\s*\)\s*;",
            re.I,
        )
        find_match = find_call.search(text)
        if find_match:
            fallback_lines = [
                f"\n/* {_NAVTREE_COMPAT_MARKER}: audited compatibility fallback; pageId/source bytes unchanged */\n",
                "if (typeof result === \"undefined\" || !result) {\n",
                "    var offlineNavPath = \"\";\n",
                "    if (typeof document !== \"undefined\" && document.location) {\n",
                "        offlineNavPath = String(document.location.pathname || \"\").toLowerCase();\n",
                "    }\n",
                "    var offlineNavNode = \"\";\n",
            ]
            for route, node in _NAVTREE_COMPAT_NODES.items():
                fallback_lines.append(
                    f'    if (offlineNavPath === "{route}") offlineNavNode = "{node}";\n'
                )
            fallback_lines.extend(
                [
                    "    if (offlineNavNode && typeof window !== \"undefined\" && window[\"Menu\" + offlineNavNode]) {\n",
                    "        result = offlineNavNode;\n",
                    "    }\n",
                    "}\n",
                ]
            )
            fallback = "".join(fallback_lines)
            text = text[:find_match.end()] + fallback + text[find_match.end():]
            node_details = ", ".join(
                f"{route}->{node}" for route, node in _NAVTREE_COMPAT_NODES.items()
            )
            recorder.add(
                "findNode('1','_',pageId);",
                base_url,
                "patched",
                "navtree-compatibility-fallback",
                "navigation",
                "runtime-page-audit-round2/nav-alias-audit.json; "
                "runtime-page-audit-round4/compatibility-evidence.json; "
                "navtree-recovery-20261012/diagnosis.json; "
                "only sets result when unset and window Menu node exists; "
                "pageId/source bytes unchanged; mappings=" + node_details,
            )

    return text


class LocalizingHTMLParser(HTMLParser):
    def __init__(self, *, base_url: str, localizer: Localizer, recorder: ReferenceRecorder, marker: str):
        super().__init__(convert_charrefs=False)
        self.base_url = base_url
        self.localizer = localizer
        self.recorder = recorder
        self.marker = marker
        self.parts: list[str] = []
        self.stack: list[str] = []

    def _localize_meta_refresh_content(self, content: str) -> str:
        """Localize only the URL in a ``meta http-equiv=refresh`` value.

        The historical delay and all content outside the URL are retained.
        This deliberately does not touch ordinary ``meta content`` values or
        any other metadata attribute.
        """

        match = _META_REFRESH_URL_RE.search(content)
        if not match:
            return content
        raw_url = match.group("url")
        stripped_url = raw_url.strip()
        if not stripped_url:
            return content
        leading = raw_url[: len(raw_url) - len(raw_url.lstrip())]
        trailing = raw_url[len(raw_url.rstrip()) :]
        localized = self.localizer.localize(
            stripped_url,
            base_url=self.base_url,
            context="navigation",
            recorder=self.recorder,
        )
        replacement = (
            match.group("prefix")
            + match.group("quote")
            + leading
            + localized
            + trailing
            + match.group("quote")
            + match.group("suffix")
        )
        return content[: match.start()] + replacement + content[match.end() :]

    def _render_attrs(self, tag: str, attrs: list[tuple[str, str | None]]) -> str:
        rendered: list[str] = []
        rel_values: set[str] = set()
        for name, value in attrs:
            if name.casefold() == "rel" and value:
                rel_values.update(str(value).casefold().split())
        is_meta_refresh = tag.casefold() == "meta" and any(
            name.casefold() == "http-equiv"
            and value is not None
            and str(value).strip().casefold() == "refresh"
            for name, value in attrs
        )
        for name, value in attrs:
            lname = name.casefold()
            if (tag.casefold() == "img" and lname == "scr" and
                    route_path(self.base_url).casefold() == "/info/basics/gettingstarted.html" and
                    value == "/shared/wow-com/images/layout/pixel.gif"):
                self.recorder.add(value, self.base_url, "patched", value, "image",
                                  "historical spacer scr attribute corrected to src; runtime-page-audit evidence")
                name = lname = "src"
            if value is None:
                rendered.append(name)
                continue
            if is_meta_refresh and lname == "content":
                value = self._localize_meta_refresh_content(value)
            context = "navigation"
            if lname in {"src", "poster", "background"}:
                context = "image" if tag.casefold() in {"img", "input", "body"} or lname in {"poster", "background"} else "script"
                if tag.casefold() == "iframe":
                    context = "frame"
                if tag.casefold() == "object":
                    context = "resource"
            elif lname == "href":
                context = "stylesheet" if "stylesheet" in rel_values else "navigation"
                if tag.casefold() == "base":
                    context = "navigation"
            elif lname == "data":
                context = "resource"
            elif lname == "action":
                context = "navigation"
            elif lname == "srcset":
                pieces = []
                for candidate in value.split(","):
                    bits = candidate.strip().split(None, 1)
                    if not bits:
                        continue
                    localized = self.localizer.localize(bits[0], base_url=self.base_url, context="srcset", recorder=self.recorder)
                    pieces.append(localized + (" " + bits[1] if len(bits) == 2 else ""))
                value = ", ".join(pieces)
            elif lname == "style":
                value = rewrite_css(value, base_url=self.base_url, localizer=self.localizer, recorder=self.recorder)
            if lname in {"src", "href", "data", "background", "action", "poster"}:
                value = self.localizer.localize(value, base_url=self.base_url, context=context, recorder=self.recorder)
            rendered.append(f'{name}="{html.escape(value, quote=True)}"')
        return (" " + " ".join(rendered)) if rendered else ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append("<" + tag + self._render_attrs(tag, attrs) + ">")
        self.stack.append(tag.casefold())

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append("<" + tag + self._render_attrs(tag, attrs) + " />")

    def handle_endtag(self, tag: str) -> None:
        self.parts.append("</" + tag + ">")
        if self.stack:
            try:
                index = len(self.stack) - 1 - self.stack[::-1].index(tag.casefold())
                del self.stack[index:]
            except ValueError:
                pass

    def handle_data(self, data: str) -> None:
        current = self.stack[-1] if self.stack else ""
        if current == "style":
            self.parts.append(rewrite_css(data, base_url=self.base_url, localizer=self.localizer, recorder=self.recorder))
        elif current == "script":
            self.parts.append(rewrite_script(data, base_url=self.base_url, localizer=self.localizer, recorder=self.recorder))
        else:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append("&" + name + ";")

    def handle_charref(self, name: str) -> None:
        self.parts.append("&#" + name + ";")

    def handle_comment(self, data: str) -> None:
        self.parts.append("<!--" + data + "-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append("<!" + decl + ">")

    def handle_pi(self, data: str) -> None:
        if data.casefold().startswith("xml-stylesheet"):
            self.parts.append(self.marker)
        else:
            self.parts.append("<!-- offline removed processing instruction: " + html.escape(data) + " -->")

    def handle_unknown_decl(self, data: str) -> None:
        self.parts.append("<![" + data + "]>")

    def output(self) -> str:
        return "".join(self.parts)


def rewrite_html(
    text: str,
    *,
    base_url: str,
    localizer: Localizer,
    recorder: ReferenceRecorder,
    source_sha: str,
    compat_assets: list[str],
) -> str:
    marker = f"<!-- offline derived from source SHA-256 {source_sha}; XML stylesheet PI handled as HTML -->"
    parser = LocalizingHTMLParser(base_url=base_url, localizer=localizer, recorder=recorder, marker=marker)
    try:
        parser.feed(text)
        parser.close()
        output = parser.output()
    except Exception as exc:  # malformed historical markup should remain viewable
        recorder.add("<parser>", base_url, "fallback", "", "html", f"HTMLParser fallback: {exc}")
        output = rewrite_generic_markup(text, base_url=base_url, localizer=localizer, recorder=recorder)
        output = marker + "\n" + output
    if compat_assets:
        injection = "\n".join(f'<link rel="stylesheet" href="{a}">' if a.endswith(".css") else f'<script src="{a}"></script>' for a in compat_assets)
        output = inject_compat_before_head(output, injection)
    return output


def inject_compat_before_head(text: str, injection: str) -> str:
    """Insert compatibility assets at the document head boundary.

    Historical inline scripts sometimes contain a literal ``</head>`` inside
    a string passed to ``document.write``.  A document-wide regex would treat
    that data as the real head close and inject markup into JavaScript.  Walk
    only the lightweight HTML raw-text boundaries so head markers inside
    script/style bodies remain untouched.
    """

    token_re = re.compile(
        r"</head\s*>|<script\b[^>]*>|</script\s*>|<style\b[^>]*>|</style\s*>",
        re.I,
    )
    raw_tag: str | None = None
    for match in token_re.finditer(text):
        token = match.group(0).casefold()
        if token.startswith("</head"):
            if raw_tag is None:
                return text[: match.start()] + injection + "\n" + text[match.start() :]
            continue
        if token.startswith("<script") and raw_tag is None:
            raw_tag = "script"
        elif token.startswith("<style") and raw_tag is None:
            raw_tag = "style"
        elif token.startswith("</script") and raw_tag == "script":
            raw_tag = None
        elif token.startswith("</style") and raw_tag == "style":
            raw_tag = None
    return injection + "\n" + text


def rewrite_text(
    text: str,
    *,
    base_url: str,
    kind: str,
    localizer: Localizer,
    recorder: ReferenceRecorder,
    source_sha: str,
    compat_assets: list[str],
) -> str:
    if kind in {"html", "menu_html"}:
        return rewrite_html(text, base_url=base_url, localizer=localizer, recorder=recorder, source_sha=source_sha, compat_assets=compat_assets)
    if kind == "css":
        return rewrite_css(text, base_url=base_url, localizer=localizer, recorder=recorder)
    if kind == "js":
        return rewrite_script(text, base_url=base_url, localizer=localizer, recorder=recorder)
    return rewrite_generic_markup(text, base_url=base_url, localizer=localizer, recorder=recorder)


def load_overlay(path: Path) -> tuple[dict[str, Any], set[str], set[str]]:
    if not path.exists():
        return {}, set(), set()
    data = json.loads(path.read_text(encoding="utf-8"))
    invalid: set[str] = set()
    supplement_only: set[str] = set()
    for item in data.get("items", []):
        url = canonical_url(str(item.get("logical_url", "")))
        state = item.get("reviewed_state") or item.get("baseline_state")
        if url and state == "invalid":
            invalid.add(url)
        if url and state == "supplement-only":
            supplement_only.add(url)
    return data, invalid, supplement_only


def load_menu_supplement(root: Path = ROOT) -> tuple[dict[str, Any], bytes] | None:
    meta_path = root / DEFAULT_MENU_META.relative_to(ROOT)
    if not meta_path.exists():
        return None
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("status") != "success" or meta.get("http_status") != 200:
        return None
    if not str(meta.get("declared_mime", "")).casefold().startswith("application/xml"):
        return None
    zip_path = root / str(meta["zip_file"])
    with zipfile.ZipFile(zip_path) as archive:
        data = archive.read(str(meta["zip_entry"]))
    if len(data) != int(meta.get("content_length", len(data))) or sha256_bytes(data) != meta.get("sha256"):
        raise MirrorError("late menu.xml supplement failed ZIP SHA/length validation")
    return meta, data


def placeholder_bytes() -> dict[str, tuple[bytes, str, str]]:
    return {
        "__offline/excluded-frame.html": (
            b'<!doctype html><html><head><meta charset="utf-8"><title>Archived advertisement omitted</title>'
            b'<style>body{margin:4px;color:#aaa;background:transparent;font:10px sans-serif}</style></head>'
            b'<body>Archived advertisement omitted.</body></html>\n',
            "text/html; charset=UTF-8",
            "explicitly excluded dynamic advertisement frame; no historical content substituted",
        ),
        "__offline/missing.html": (
            b"<!doctype html><html><head><meta charset=\"utf-8\"><title>Offline resource not collected</title></head>"
            b"<body><h1>Offline resource not collected</h1><p>This local route is an explicit placeholder."
            b" The original resource was not used as a substitute.</p></body></html>\n",
            "text/html; charset=UTF-8",
            "generated local missing-page placeholder; no network fallback",
        ),
        "__offline/missing-image.svg": (
            b"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" viewBox=\"0 0 16 16\">"
            b"<rect width=\"16\" height=\"16\" fill=\"#e4e4e4\"/><path d=\"M0 0L16 16M16 0L0 16\" stroke=\"#b00\"/></svg>\n",
            "image/svg+xml",
            "generated local image placeholder for missing or invalid image entity",
        ),
        "__offline/empty.js": (
            b"/* offline local no-op for an unavailable script; no network request is made */\n",
            "application/javascript; charset=UTF-8",
            "generated local no-op script for unavailable external or invalid script",
        ),
        "__offline/empty.css": (
            b"/* offline local empty stylesheet for an unavailable stylesheet */\n",
            "text/css; charset=UTF-8",
            "generated local empty stylesheet for unavailable external or invalid CSS",
        ),
    }


def infer_kind(source: dict[str, Any], mime: str, route: str) -> str:
    """Infer a text kind for compatible extra-map records.

    The primary map carries an explicit ``kind``.  Expansion maps produced by
    the acquisition/index phase may only carry the response MIME, so MIME is
    authoritative here; the route suffix is a conservative fallback for
    records without a declared type.
    """

    explicit = source.get("kind") or source.get("source_kind")
    if explicit:
        return str(explicit)
    base = mime_base(mime)
    if base in {"text/html", "application/xhtml+xml"}:
        return "html"
    if base == "text/css":
        return "css"
    if "javascript" in base or base in {"application/ecmascript", "text/ecmascript"}:
        return "js"
    suffix = posixpath.splitext(route.casefold())[1]
    if suffix in {".html", ".htm", ".xhtml", ".xml"}:
        return "html"
    if suffix == ".css":
        return "css"
    if suffix in {".js", ".mjs", ".htc"}:
        return "js"
    return "other"


def is_upstream_compatibility_entry(source: dict[str, Any]) -> bool:
    """Identify an explicitly marked non-WoW compatibility source."""

    return isinstance(source.get("upstream_compatibility"), dict)


def source_entry_classification(source: dict[str, Any]) -> str:
    """Return the manifest/statistics class without inferring provenance."""

    return "upstream_compatibility" if is_upstream_compatibility_entry(source) else "wow_source"


def upstream_compatibility_record_fields(source: dict[str, Any]) -> dict[str, Any]:
    """Select optional compatibility provenance for verbatim manifest copy."""

    return {
        key: source[key]
        for key in ("classification", "supplement_note", "upstream_compatibility")
        if key in source
    }


def build_site(
    *,
    url_map_path: Path = DEFAULT_URL_MAP,
    overlay_path: Path = DEFAULT_OVERLAY,
    site_dir: Path = DEFAULT_SITE,
    manifest_path: Path = DEFAULT_MANIFEST,
    support_dir: Path = DEFAULT_SUPPORT,
    include_menu_supplement: bool = True,
    extra_map_paths: Iterable[Path] = (),
) -> dict[str, Any]:
    """Build a derived site and return its manifest object."""

    url_map_path = url_map_path.resolve()
    overlay_path = overlay_path.resolve()
    site_dir = site_dir.resolve()
    manifest_path = manifest_path.resolve()
    support_dir = support_dir.resolve()
    extra_map_paths = tuple(Path(path).resolve() for path in extra_map_paths)
    if not url_map_path.exists():
        raise MirrorError(f"URL map not found: {url_map_path}")
    url_map = json.loads(url_map_path.read_text(encoding="utf-8"))
    overlay, invalid_urls, supplement_only = load_overlay(overlay_path)
    entries: list[dict[str, Any]] = []
    route_entries: dict[str, dict[str, Any]] = {}
    skipped_invalid: list[dict[str, Any]] = []
    extra_map_metadata: list[dict[str, Any]] = []
    sources: list[tuple[dict[str, Any], Path | None]] = [
        (dict(source), None) for source in url_map.get("files", [])
    ]
    for extra_path in extra_map_paths:
        if not extra_path.exists():
            raise MirrorError(f"extra map not found: {extra_path}")
        extra_data = json.loads(extra_path.read_text(encoding="utf-8"))
        extra_files = extra_data.get("files")
        if not isinstance(extra_files, list):
            raise MirrorError(f"extra map has no files array: {extra_path}")
        extra_map_metadata.append(
            {
                "path": rel_to_root(extra_path),
                "sha256": sha256_file(extra_path),
                "file_count": len(extra_files),
            }
        )
        sources.extend((dict(source), extra_path) for source in extra_files if isinstance(source, dict))

    skipped_extra: list[dict[str, Any]] = []
    extra_loaded = 0
    upstream_compatibility_count = 0
    extra_loaded_wow = 0
    extra_root_route: str | None = None
    explicit_route_aliases: dict[str, str] = {}
    # A source map may contain the same path on multiple approved hosts.  The
    # derived route is namespaced for non-primary hosts unless the map gives a
    # deliberate route, while this index keeps localizer lookup keyed by the
    # original origin rather than by path alone.
    origin_index_candidates: list[dict[str, Any]] = []

    def register_aliases(aliases: list[str], target: str) -> list[str]:
        registered: list[str] = []
        for alias in aliases:
            alias_path = route_path(alias) if "://" in alias else (alias if alias.startswith("/") else "/" + alias)
            if alias_path == target:
                continue
            prior = explicit_route_aliases.get(alias_path)
            if prior and prior != target:
                raise MirrorError(f"duplicate derived route alias: {alias_path}")
            explicit_route_aliases[alias_path] = target
            registered.append(alias_path)
        return sorted(set(registered))

    for source, source_map_path in sources:
        logical_raw = source.get("logical_url") or source.get("original")
        logical = canonical_url(str(logical_raw or ""))
        if not logical:
            if source_map_path is None:
                raise MirrorError("primary URL map entry has no logical_url/original")
            skipped_extra.append({"map": rel_to_root(source_map_path), "reason": "missing logical_url"})
            continue
        original_route = route_path(logical)
        route = original_route
        explicit_route = source.get("derived_route") or source.get("output_route")
        if explicit_route:
            route = str(explicit_route)
            if not route.startswith("/") or ".." in route.split("/"):
                raise MirrorError(f"invalid derived route for {logical}: {route}")
        elif not is_primary_origin(logical):
            route = origin_route(logical)
        # The primary encyclopedia map has no domain-root entity.  Expansion
        # maps may add one; materialize it as a file beneath the derived site
        # so it cannot collide with the site directory itself.  The server's
        # root alias is updated below to point at this explicit entity.
        if source_map_path is not None and original_route == "/" and is_primary_origin(logical):
            route = "/index.html"
        local_raw = source.get("local_path") or source.get("source_file")
        if not local_raw:
            if source_map_path is None:
                raise MirrorError(f"primary URL map entry has no local_path: {logical}")
            skipped_extra.append({"map": rel_to_root(source_map_path), "logical_url": logical, "reason": "missing local_path"})
            continue
        source_file = (ROOT / str(local_raw)).resolve()
        safe_source_path(source_file)
        if not source_file.is_file():
            if source_map_path is None:
                raise MirrorError(f"source entity missing: {source_file}")
            skipped_extra.append({"map": rel_to_root(source_map_path), "logical_url": logical, "local_path": str(local_raw), "reason": "source file missing"})
            continue
        actual_sha = sha256_file(source_file)
        expected_sha = source.get("sha256")
        if expected_sha and actual_sha != expected_sha:
            raise MirrorError(f"source SHA mismatch for {logical}: {actual_sha} != {source.get('sha256')}")
        if not expected_sha:
            expected_sha = actual_sha
        item = dict(source)
        item.update(
            {
                "logical_url": logical,
                "route": route,
                "origin_namespace": origin_namespace_host(logical),
                "source_path": source_file,
                "source_sha256": expected_sha,
                "source_length": source_file.stat().st_size,
                "source_map_path": rel_to_root(source_map_path) if source_map_path else rel_to_root(url_map_path),
                "source_sha_inferred": not bool(source.get("sha256")),
            }
        )
        if logical in invalid_urls:
            skipped_invalid.append({"logical_url": logical, "source_sha256": actual_sha, "reason": "invalid overlay; never copied as a usable resource"})
            continue
        aliases_for_item: list[str] = []
        raw_aliases = source.get("route_aliases") or source.get("aliases") or []
        if isinstance(raw_aliases, dict):
            aliases_for_item.extend(str(key) for key, value in raw_aliases.items() if str(value) in {route, logical})
        elif isinstance(raw_aliases, (list, tuple, set)):
            aliases_for_item.extend(str(value) for value in raw_aliases)
        # Verified directory captures can share an entity with index.html.
        if explicit_route and original_route.rstrip("/") and not posixpath.splitext(original_route)[1]:
            aliases_for_item.extend([original_route, original_route.rstrip("/") + "/"])
        if route in route_entries:
            if source_map_path is not None:
                prior_item = route_entries[route]
                retained: list[str] = []
                if prior_item["source_sha256"] == actual_sha:
                    retained = register_aliases(aliases_for_item, route)
                    if retained:
                        prior_item.setdefault("route_alias_sources", []).append({
                            "logical_url": logical, "source_map_path": rel_to_root(source_map_path),
                            "source_sha256": actual_sha, "actual_timestamp": source.get("actual_timestamp"),
                            "aliases": retained, "reason": "verified duplicate entity with identical SHA256",
                        })
                skipped_extra.append({"map": rel_to_root(source_map_path), "logical_url": logical, "route": route,
                                      "reason": "route already supplied by an earlier map", "retained_aliases": retained})
                continue
            raise MirrorError(f"duplicate derived route: {route}")
        item["kind"] = infer_kind(item, file_mime(item.get("mime") or item.get("declared_mime") or item.get("source_mime"), route), route)
        route_entries[route] = item
        entries.append(item)
        entry_classification = source_entry_classification(item)
        if entry_classification == "upstream_compatibility":
            upstream_compatibility_count += 1
        origin_index_candidates.append({
            "key": origin_key(logical),
            "route": route,
            "kind": "logical",
            "logical_url": logical,
            "source_map_path": item.get("source_map_path"),
        })
        source_base = source.get("source_base_url") or source.get("base_url")
        if source_base:
            origin_index_candidates.append({
                "key": origin_key(str(source_base)),
                "route": route,
                "kind": "source_base_url",
                "logical_url": logical,
                "source_base_url": str(source_base),
                "source_map_path": item.get("source_map_path"),
            })
        register_aliases(aliases_for_item, route)
        if source_map_path is not None:
            extra_loaded += 1
            if entry_classification == "wow_source":
                extra_loaded_wow += 1
            if original_route == "/" and is_primary_origin(logical):
                extra_root_route = route

    supplement: dict[str, Any] | None = None
    if include_menu_supplement:
        loaded = load_menu_supplement(ROOT)
        if loaded:
            meta, data = loaded
            logical = canonical_url(str(meta["original"]))
            route = route_path(logical)
            supplement = {
                "logical_url": logical,
                "route": route,
                "origin_namespace": origin_namespace_host(logical),
                "source_path": None,
                "source_local_path": str(meta["zip_file"]) + "#" + str(meta["zip_entry"]),
                "source_sha256": meta["sha256"],
                "source_length": len(data),
                "source_mime": meta.get("declared_mime"),
                "kind": "xml",
                "role": "reconstruction_supplement",
                "source_role": "late_menu_xml_supplement",
                "actual_timestamp": meta.get("actual_timestamp"),
                "requested_timestamp": meta.get("requested_timestamp"),
                "content": data,
                "supplement_note": "Valid late menu.xml only; explicit reconstruction supplement, not the anchor snapshot.",
            }
            route_entries[route] = supplement
            entries.append(supplement)
            origin_index_candidates.append({
                "key": origin_key(logical),
                "route": route,
                "kind": "logical",
                "logical_url": logical,
                "source_map_path": "late_menu_supplement",
            })

    route_aliases = dict(explicit_route_aliases)
    # An expansion map may expose the real site homepage as /index.xml (or a
    # similar route) and explicitly alias "/" to it.  Preserve that alias;
    # only fall back to the encyclopedia entry when no expansion map supplied
    # a homepage target.  A domain-root entity remains the strongest explicit
    # homepage source because it is materialized as /index.html above.
    root_target = extra_root_route or route_aliases.get("/") or "/info/encyclopedia/index.xml"
    route_aliases["/"] = root_target
    if not extra_root_route and "/index.html" not in route_entries:
        route_aliases["/index.html"] = root_target
    origin_index: dict[str, str] = {}
    origin_index_conflicts: list[dict[str, Any]] = []
    # Logical URLs are authoritative.  Add all of them first so a later
    # source_base_url alias cannot hide a real entity on the same host/path.
    for candidate in (item for item in origin_index_candidates if item.get("kind") == "logical"):
        key = str(candidate["key"])
        route = str(candidate["route"])
        prior = origin_index.get(key)
        if prior and prior != route:
            origin_index_conflicts.append({"key": key, "prior_route": prior, "route": route, "candidate": candidate})
        else:
            origin_index[key] = route
    for candidate in (item for item in origin_index_candidates if item.get("kind") != "logical"):
        key = str(candidate["key"])
        route = str(candidate["route"])
        prior = origin_index.get(key)
        if prior and prior != route:
            origin_index_conflicts.append({"key": key, "prior_route": prior, "route": route, "candidate": candidate, "reason": "source_base_alias_did_not_override_logical_entity"})
        elif not prior:
            origin_index[key] = route

    localizer = Localizer(
        route_entries,
        invalid_urls,
        root_target=root_target,
        route_aliases=route_aliases,
        origin_index=origin_index,
    )
    generated_at = utc_now()
    if site_dir.exists():
        if site_dir == ROOT or site_dir == ROOT / "mirror" or site_dir == ROOT / "backups":
            raise MirrorError(f"refusing to clear source-like path: {site_dir}")
        shutil.rmtree(site_dir)
    site_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    files_out: list[dict[str, Any]] = []
    route_manifest: dict[str, dict[str, Any]] = {}
    global_references: list[dict[str, Any]] = []
    stats: Counter[str] = Counter()

    compat_assets: list[str] = []
    support_records: list[dict[str, Any]] = []
    for name in ("compat.css", "compat.js"):
        support_path = support_dir / name
        if support_path.is_file():
            data = support_path.read_bytes()
            route = "/__offline/" + name
            out = site_dir / route.lstrip("/")
            ensure_safe_site_path(site_dir, out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            record = {
                "route": route,
                "output_path": rel_to_root(out),
                "source_local_path": rel_to_root(support_path),
                "source_sha256": sha256_bytes(data),
                "source_length": len(data),
                "derived_sha256": sha256_bytes(data),
                "derived_length": len(data),
                "mime": "text/css; charset=UTF-8" if name.endswith(".css") else "application/javascript; charset=UTF-8",
                "kind": "support",
                "role": "compatibility_support",
                "derivation_reason": "copied optional frontend compatibility support; injected into derived HTML",
                "transformed": False,
            }
            files_out.append(record)
            route_manifest[route] = record
            support_records.append(record)
            compat_assets.append(route)

    for item in entries:
        route = item["route"]
        out = site_dir / route.lstrip("/")
        ensure_safe_site_path(site_dir, out)
        out.parent.mkdir(parents=True, exist_ok=True)
        source_data = item.get("content") if item.get("source_path") is None else item["source_path"].read_bytes()
        source_sha = item["source_sha256"]
        source_mime = file_mime(item.get("mime") or item.get("declared_mime") or item.get("source_mime"), route)
        kind = str(item.get("kind") or "other")
        recorder = ReferenceRecorder(route, item["logical_url"])
        transformed = kind in {"html", "menu_html", "css", "js", "xsl", "legacy_component", "xml"}
        data = source_data
        reason = "copied verified preserved entity bytes without transformation"
        if transformed:
            charset = charset_for(source_mime, source_data)
            text = source_data.decode(charset, errors="replace")
            text = rewrite_text(
                text,
                base_url=item.get("source_base_url") or item.get("base_url") or item["logical_url"],
                kind=kind,
                localizer=localizer,
                recorder=recorder,
                source_sha=source_sha,
                compat_assets=compat_assets if kind in {"html", "menu_html"} else [],
            )
            data = text.encode(charset, errors="replace")
            reason = "derived local copy; rewritten site URLs/resources and removed or localized external requests"
            if kind in {"html", "menu_html"}:
                reason += "; historical .xml entity is served as its recorded HTML MIME"
        if item.get("supplement_note"):
            reason = item["supplement_note"] + " URLs localized in the derived copy."
        out.write_bytes(data)
        record = {
            "route": route,
            "origin_namespace": item.get("origin_namespace") or origin_namespace_host(item["logical_url"]),
            "output_path": rel_to_root(out),
            "source_local_path": item.get("local_path") or item.get("source_local_path"),
            "source_base_url": item.get("source_base_url") or item.get("base_url") or item.get("logical_url"),
            "source_map_path": item.get("source_map_path"),
            "source_sha_inferred": bool(item.get("source_sha_inferred", False)),
            "source_sha256": source_sha,
            "source_length": len(source_data),
            "derived_sha256": sha256_bytes(data),
            "derived_length": len(data),
            "source_mime": item.get("response_content_type") or source_mime,
            "mime": source_mime,
            "kind": kind,
            "role": item.get("role"),
            "source_role": item.get("source_role"),
            "actual_timestamp": item.get("actual_timestamp"),
            "requested_timestamp": item.get("requested_timestamp"),
            "transformed": transformed,
            "derivation_reason": reason,
            "reference_counts": dict(recorder.counts),
            "references": recorder.records,
            "references_truncated": max(0, sum(recorder.counts.values()) - len(recorder.records)),
            # Upstream compatibility notes are provenance, not a historical
            # WoW reconstruction supplement and must not inflate that count.
            "supplement": bool(item.get("supplement_note")) and not is_upstream_compatibility_entry(item),
        }
        # Preserve upstream provenance verbatim.  This is an explicit
        # compatibility source, never a WoW capture assertion.
        record.update(upstream_compatibility_record_fields(item))
        if "route_alias_evidence" in item:
            # Preserve this optional provenance verbatim for the build
            # manifest; absent source-map fields must not become null noise on
            # every entity record.
            record["route_alias_evidence"] = item["route_alias_evidence"]
        if item.get("route_alias_sources"):
            record["route_alias_sources"] = item["route_alias_sources"]
        files_out.append(record)
        route_manifest[route] = record
        global_references.extend({"source_route": route, **ref} for ref in recorder.records if ref["action"] == "placeholder")
        stats["transformed" if transformed else "copied"] += 1

    for relative, (data, mime, reason) in placeholder_bytes().items():
        route = "/" + relative
        out = site_dir / relative
        ensure_safe_site_path(site_dir, out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        record = {
            "route": route,
            "output_path": rel_to_root(out),
            "source_local_path": None,
            "source_sha256": None,
            "source_length": None,
            "derived_sha256": sha256_bytes(data),
            "derived_length": len(data),
            "source_mime": None,
            "mime": mime,
            "kind": "generated_placeholder",
            "role": "offline_support",
            "transformed": True,
            "derivation_reason": reason,
            "reference_counts": {},
            "references": [],
            "references_truncated": 0,
            "supplement": False,
        }
        files_out.append(record)
        route_manifest[route] = record

    # A root route and any directory spellings are server aliases rather than
    # extra copies of the source entities.
    aliases = route_aliases
    manifest = {
        "schema_version": 1,
        "generated_at": generated_at,
        "anchor_timestamp": url_map.get("anchor"),
        "source_map": rel_to_root(url_map_path),
        "source_map_sha256": sha256_file(url_map_path),
        "extra_maps": extra_map_metadata,
        "extra_map_skipped_entries": skipped_extra,
        "overlay": rel_to_root(overlay_path) if overlay_path.exists() else None,
        "overlay_sha256": sha256_file(overlay_path) if overlay_path.exists() else None,
        "site_root": rel_to_root(site_dir),
        "source_entities_unmodified": bool(url_map.get("unmodified_entities")),
        "invalid_overlay_urls_excluded": sorted(invalid_urls),
        "supplement_only_overlay_urls": sorted(supplement_only),
        "skipped_invalid_source_entries": skipped_invalid,
        "route_aliases": aliases,
        "origin_index": origin_index,
        "origin_index_conflicts": origin_index_conflicts,
        "files": files_out,
        "placeholder_routes": [r for r, rec in route_manifest.items() if rec.get("kind") == "generated_placeholder"],
        "supplements": [rec for rec in files_out if rec.get("supplement")],
        "unresolved_reference_count": len(global_references),
        "unresolved_references": global_references[:2000],
        "stats": {
            "source_entries": len(url_map.get("files", [])),
            "extra_map_entries": sum(item["file_count"] for item in extra_map_metadata),
            "extra_map_loaded": extra_loaded,
            "extra_map_loaded_wow_sources": extra_loaded_wow,
            "extra_map_skipped": len(skipped_extra),
            "derived_files": len(files_out),
            "routes": len(route_manifest),
            "transformed": stats["transformed"],
            "copied": stats["copied"],
            "supplements": sum(1 for rec in files_out if rec.get("supplement")),
            "placeholders": sum(1 for rec in files_out if rec.get("kind") == "generated_placeholder"),
            "invalid_entries_excluded": len(skipped_invalid),
            "compat_assets": len(support_records),
            "upstream_compatibility_entries": upstream_compatibility_count,
        },
        "security": {
            "external_fetches": False,
            "path_traversal_protection": True,
            "serve_default_host": "127.0.0.1",
            "csp": DEFAULT_CSP,
        },
        "notes": [
            "This is a derived browsing tree; source entities and ZIPs remain unchanged.",
            "worldofwarcraft.com and www.worldofwarcraft.com share one origin namespace; other approved hosts use /_origins/<hostname>/ routes and host+path lookup.",
            "Missing or invalid image references use an explicit local placeholder and never reuse HTML error entities.",
            "Only the validated late menu.xml is included as an explicitly marked reconstruction supplement.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


class OfflineRequestHandler(BaseHTTPRequestHandler):
    server_version = "OfflineMirror/1.0"

    def do_HEAD(self) -> None:  # noqa: N802
        self._handle(send_body=False)

    def do_GET(self) -> None:  # noqa: N802
        self._handle(send_body=True)

    def log_message(self, format: str, *args: Any) -> None:
        # Keep the standard server quiet; every request is recorded in the
        # structured log exposed by /__offline/api/log.
        return

    def _record(self, entry: dict[str, Any]) -> None:
        state = self.server  # type: ignore[assignment]
        canonicalized_from = getattr(self, "_canonicalized_from", None)
        if canonicalized_from:
            entry.setdefault("canonicalized_from", canonicalized_from)
        state.request_log_lock.acquire()
        try:
            state.request_log.append(entry)
            if len(state.request_log) > 2000:
                del state.request_log[:-2000]
            if state.log_file:
                with state.log_file.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        finally:
            state.request_log_lock.release()

    def _headers(
        self,
        *,
        mime: str,
        length: int,
        status: int,
        source_sha: str | None = None,
        derived_sha: str | None = None,
        entity_kind: str,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(length))
        self.send_header("Content-Security-Policy", DEFAULT_CSP)
        self.send_header("X-Content-Type-Options", "nosniff")
        # The body may be a verified source entity, a generated placeholder,
        # or an explicit uncollected fallback.  Keep this classification on
        # the wire so browser checks do not count every HTTP 200 as restored.
        self.send_header("X-Offline-Entity-Kind", entity_kind)
        if source_sha:
            self.send_header("X-Offline-Source-SHA256", source_sha)
        if derived_sha:
            self.send_header("X-Offline-Derived-SHA256", derived_sha)
            # Explicitly name the bytes sent on the wire for clients that
            # previously used the mislabeled source header as a body digest.
            self.send_header("X-Offline-Served-SHA256", derived_sha)
        self.end_headers()

    def _send_bytes(
        self,
        data: bytes,
        *,
        mime: str,
        status: int,
        route: str,
        source_sha: str | None,
        derived_sha: str | None = None,
        kind: str,
        send_body: bool,
    ) -> None:
        derived_sha = derived_sha or sha256_bytes(data)
        client_disconnected = False
        try:
            self._headers(
                mime=mime,
                length=len(data),
                status=status,
                source_sha=source_sha,
                derived_sha=derived_sha,
                entity_kind=kind,
            )
            if send_body:
                self.wfile.write(data)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # Browsers routinely cancel outstanding subresource responses when
            # navigating to the next page.  This is a normal client lifecycle
            # event; keep it in the structured log without emitting a server
            # traceback.  Other I/O and programming errors still propagate.
            client_disconnected = True
        finally:
            self._record(
                {
                    "at": utc_now(),
                    "method": self.command,
                    "request": self.path,
                    "route": route,
                    "status": status,
                    "mime": mime,
                    "bytes": len(data),
                    "kind": kind,
                    "source_sha256": source_sha,
                    "derived_sha256": derived_sha,
                    "served_sha256": derived_sha,
                    "client_disconnected": client_disconnected,
                }
            )

    def _json(self, value: Any, *, status: int = 200, send_body: bool = True, route: str = "") -> None:
        data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        self._send_bytes(data, mime="application/json; charset=UTF-8", status=status, route=route, source_sha=None, kind="api", send_body=send_body)

    def _reject(self, message: str, *, status: int = 400, send_body: bool = True) -> None:
        body = (
            "<!doctype html><meta charset=\"utf-8\"><title>Offline route rejected</title>"
            f"<h1>Offline route rejected</h1><p>{html.escape(message)}</p>"
        ).encode("utf-8")
        self._send_bytes(body, mime="text/html; charset=UTF-8", status=status, route="/__offline/rejected", source_sha=None, kind="security", send_body=send_body)

    def _handle(self, *, send_body: bool) -> None:
        state = self.server  # type: ignore[assignment]
        parsed = urllib.parse.urlsplit(self.path)
        raw_path = parsed.path or "/"
        try:
            decoded = urllib.parse.unquote(raw_path, errors="strict")
        except Exception:
            self._reject("invalid URL escaping", send_body=send_body)
            return
        if "\x00" in decoded or "\\" in decoded or any(part == ".." for part in decoded.split("/")):
            self._reject("path traversal is not allowed", send_body=send_body)
            return
        if not decoded.startswith("/"):
            self._reject("path must be absolute", send_body=send_body)
            return
        # Toplist loads executable data feeds through XHR and has a real
        # status-404 branch that renders its original "no data" table. A
        # successful no-op JS placeholder would instead enter eval/import
        # and falsely imply that statistics were recovered. The empty
        # language/category forms also occur in the preserved bare landing
        # page. Admit only this finite feed grammar, after traversal checks,
        # and let any future verified manifest entity take precedence.
        if (decoded not in state.manifest_routes and re.fullmatch(
                r"/toplist/data/(?:en|de|fr|es)?/(?:auctionsold|spellcreate|killedby|gameobjloot|unitloot|questcomplete|undefined)?_\d{8}\.js",
                decoded)):
            self._send_bytes(
                b"Historical Toplist statistics were not collected in this offline mirror.\n",
                mime="text/plain; charset=UTF-8", status=404, route=decoded,
                source_sha=None, kind="uncollected-dynamic-data", send_body=send_body,
            )
            return
        original_decoded = decoded
        decoded, canonicalized = canonical_request_path(
            decoded,
            route_keys=state.manifest_routes,
            aliases=state.manifest.get("route_aliases", {}),
            special_routes={
                "/",
                "/__offline/api/log",
                "/__offline/api/url-map",
                "/__offline/build-manifest.json",
                "/__offline/missing.html",
                "/__offline/uncollected",
            },
        )
        if canonicalized:
            self._canonicalized_from = original_decoded
        if decoded == "/__offline/api/log":
            with state.request_log_lock:
                log = list(state.request_log)
            self._json({"entries": log, "count": len(log)}, route=decoded, send_body=send_body)
            return
        if decoded == "/__offline/api/health":
            self._json({"server_pid": os.getpid(), "build_manifest_sha256": state.manifest_sha256,
                        "routes": len(state.manifest_routes)}, route=decoded, send_body=send_body)
            return
        if decoded == "/__offline/api/url-map":
            query_url = urllib.parse.parse_qs(parsed.query).get("url", [""])[0]
            query_path = urllib.parse.parse_qs(parsed.query).get("path", [""])[0]
            matches: list[dict[str, Any]] = []
            if query_url:
                query_route = route_path(query_url)
            else:
                query_route = query_path or ""
            item = state.manifest_routes.get(query_route)
            if item:
                matches.append(item)
            self._json({"query": query_url or query_path, "route": query_route, "matches": matches, "aliases": state.manifest.get("route_aliases", {})}, route=decoded, send_body=send_body)
            return
        if decoded == "/__offline/build-manifest.json":
            self._json(state.manifest, route=decoded, send_body=send_body)
            return
        if decoded == "/":
            location = state.manifest.get("route_aliases", {}).get("/", "/info/encyclopedia/index.xml")
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", location)
            self.send_header("Content-Security-Policy", DEFAULT_CSP)
            self.send_header("Content-Length", "0")
            self.end_headers()
            self._record({"at": utc_now(), "method": self.command, "request": self.path, "route": "/", "status": 302, "mime": None, "bytes": 0, "kind": "alias", "location": location})
            return
        if decoded == "/__offline/missing.html":
            params = urllib.parse.parse_qs(parsed.query)
            requested = params.get("requested", [""])[0]
            source = params.get("source", [""])[0]
            body = (
                "<!doctype html><html><head><meta charset=\"utf-8\"><title>Offline resource not collected</title></head>"
                "<body><h1>Offline resource not collected</h1>"
                f"<p>Requested: <code>{html.escape(requested)}</code></p>"
                f"<p>Source: <code>{html.escape(source)}</code></p>"
                "<p>This derived mirror does not contact the network.</p></body></html>\n"
            ).encode("utf-8")
            self._send_bytes(body, mime="text/html; charset=UTF-8", status=200, route=decoded, source_sha=None, kind="generated_placeholder", send_body=send_body)
            return
        if decoded == "/__offline/uncollected":
            # Compatibility support uses this route for searches and other
            # dynamic features whose historical endpoint is outside the
            # verified mirror.  Keep the explanation local and explicit so a
            # click never falls through to a browser/network error page.
            params = urllib.parse.parse_qs(parsed.query)
            kind = params.get("kind", ["resource"])[0]
            target = params.get("target", [""])[0]
            query = params.get("query", [""])[0]
            body = (
                "<!doctype html><html><head><meta charset=\"utf-8\"><title>Offline feature not collected</title></head>"
                "<body><h1>Offline feature not collected</h1>"
                f"<p>Feature: <code>{html.escape(kind)}</code></p>"
                f"<p>Target: <code>{html.escape(target)}</code></p>"
                f"<p>Query: <code>{html.escape(query)}</code></p>"
                "<p>This derived mirror does not contact the network.</p></body></html>\n"
            ).encode("utf-8")
            self._send_bytes(body, mime="text/html; charset=UTF-8", status=200, route=decoded, source_sha=None, kind="uncollected-feature", send_body=send_body)
            return
        if decoded in state.manifest.get("route_aliases", {}) and decoded != "/":
            location = state.manifest["route_aliases"][decoded]
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", location)
            self.send_header("Content-Security-Policy", DEFAULT_CSP)
            self.send_header("Content-Length", "0")
            self.end_headers()
            self._record({"at": utc_now(), "method": self.command, "request": self.path, "route": decoded, "status": 302, "mime": None, "bytes": 0, "kind": "alias", "location": location})
            return

        rel = decoded.lstrip("/")
        candidate = (state.site_dir / rel).resolve()
        try:
            candidate.relative_to(state.site_dir.resolve())
        except ValueError:
            self._reject("route escapes offline site", status=403, send_body=send_body)
            return
        item = state.manifest_routes.get(decoded)
        if candidate.is_file() and item:
            data = candidate.read_bytes()
            self._send_bytes(
                data,
                mime=item.get("mime") or file_mime(None, decoded),
                status=200,
                route=decoded,
                source_sha=item.get("source_sha256"),
                derived_sha=item.get("derived_sha256"),
                kind=str(item.get("kind") or "file"),
                send_body=send_body,
            )
            return
        # A few historical scripts construct resource paths at runtime.  A
        # path absent from the verified map must stay local and explicit; a
        # browser should receive a typed placeholder rather than attempting a
        # network fallback or reporting a misleading remote 404.  Navigation
        # paths without a recognized extension continue to use the 404 page
        # below so typos and traversal probes remain visible.
        suffix = posixpath.splitext(decoded.casefold())[1]
        fallback: tuple[bytes, str, str] | None = None
        if suffix in {".js", ".htc"}:
            data, mime, _ = placeholder_bytes()["__offline/empty.js"]
            fallback = (data, mime, "uncollected-script-placeholder")
        elif suffix == ".css":
            data, mime, _ = placeholder_bytes()["__offline/empty.css"]
            fallback = (data, mime, "uncollected-stylesheet-placeholder")
        elif suffix in {".gif", ".jpg", ".jpeg", ".png", ".webp", ".svg", ".swf", ".ico"}:
            data, mime, _ = placeholder_bytes()["__offline/missing-image.svg"]
            fallback = (data, mime, "uncollected-image-placeholder")
        elif suffix in {".html", ".htm", ".xml", ".xhtml"}:
            data, mime, _ = placeholder_bytes()["__offline/missing.html"]
            fallback = (data, mime, "uncollected-page-placeholder")
        if fallback:
            data, mime, kind = fallback
            self._send_bytes(data, mime=mime, status=200, route=decoded, source_sha=None, kind=kind, send_body=send_body)
            return
        self._send_bytes(
            (
                "<!doctype html><meta charset=\"utf-8\"><title>Offline route not collected</title>"
                f"<h1>Offline route not collected</h1><p><code>{html.escape(decoded)}</code></p>"
            ).encode("utf-8"),
            mime="text/html; charset=UTF-8",
            status=404,
            route=decoded,
            source_sha=None,
            kind="not-found",
            send_body=send_body,
        )


class OfflineHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = sys.platform != "win32"
    # Chrome opens several subresources in parallel.  The stdlib default
    # backlog is small enough to cause transient connection refusals during
    # the first page load on Windows.
    request_queue_size = 128

    def __init__(self, address: tuple[str, int], *, site_dir: Path, manifest: dict[str, Any], log_file: Path | None = None,
                 manifest_sha256: str | None = None):
        self.site_dir = site_dir.resolve()
        self.manifest = manifest
        self.manifest_sha256 = manifest_sha256
        self.manifest_routes = {str(item["route"]): item for item in manifest.get("files", [])}
        self.request_log: list[dict[str, Any]] = []
        self.request_log_lock = threading.Lock()
        self.log_file = log_file.resolve() if log_file else None
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(address, OfflineRequestHandler)

    def server_bind(self) -> None:
        if sys.platform == "win32":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def run_server(*, site_dir: Path = DEFAULT_SITE, manifest_path: Path = DEFAULT_MANIFEST, host: str = "127.0.0.1", port: int = 8765, log_file: Path | None = None) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    site_dir = site_dir.resolve()
    if not site_dir.is_dir():
        raise MirrorError(f"offline site not found: {site_dir}")
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise MirrorError("offline server binds only to loopback hosts")
    server = OfflineHTTPServer((host, port), site_dir=site_dir, manifest=manifest, log_file=log_file,
                               manifest_sha256=sha256_file(manifest_path))
    print(f"offline mirror serving http://{host}:{server.server_port}/ PID={os.getpid()} manifest={server.manifest_sha256}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build the derived offline site")
    build.add_argument("--url-map", type=Path, default=DEFAULT_URL_MAP)
    build.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    build.add_argument("--site", type=Path, default=DEFAULT_SITE)
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    build.add_argument("--support-dir", type=Path, default=DEFAULT_SUPPORT)
    build.add_argument(
        "--extra-map",
        type=Path,
        action="append",
        default=[],
        help="additional validated files-map JSON; may be supplied more than once",
    )
    build.add_argument("--no-menu-supplement", action="store_true")
    serve = sub.add_parser("serve", help="serve the derived site on loopback")
    serve.add_argument("--site", type=Path, default=DEFAULT_SITE)
    serve.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--log-file", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        if args.command == "build":
            manifest = build_site(
                url_map_path=args.url_map,
                overlay_path=args.overlay,
                site_dir=args.site,
                manifest_path=args.manifest,
                support_dir=args.support_dir,
                include_menu_supplement=not args.no_menu_supplement,
                extra_map_paths=args.extra_map,
            )
            print(json.dumps({"site": manifest["site_root"], "manifest": rel_to_root(args.manifest.resolve()), "stats": manifest["stats"]}, ensure_ascii=False))
            return 0
        run_server(site_dir=args.site, manifest_path=args.manifest, host=args.host, port=args.port, log_file=args.log_file)
        return 0
    except (MirrorError, OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"offline_mirror: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

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
import html
import json
import mimetypes
import os
import posixpath
import re
import shutil
import sys
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = ROOT / "offline/site"
DEFAULT_MANIFEST = ROOT / "offline/build-manifest.json"
DEFAULT_OUTPUT = ROOT / ".scratch/pages-preview"
DEFAULT_BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
DEFAULT_MAX_BYTES = 14_000_000_000
DEFAULT_MIN_FREE_BYTES = 11_005_853_696
PAGES_CSP = (
    "default-src 'self' data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; connect-src 'self'; form-action 'self'; "
    "frame-src 'self'; object-src 'none'"
)

if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
import offline_mirror as mirror  # noqa: E402


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
        dirs[:] = [d for d in dirs if d not in {".git"}]
        for name in files:
            try:
                total += (current_path / name).stat().st_size
            except OSError:
                continue
    return total


def output_estimate(records: list[dict[str, Any]]) -> int:
    source_total = sum(int(item.get("derived_length") or 0) for item in records)
    # URL rewriting, route stubs, provenance and a conservative 25% growth
    # allowance are included.  This is intentionally larger than the known
    # source tree and is checked again after the export.
    return source_total + source_total // 4 + 128 * 1024 * 1024


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
        body = rewrite_root_literals(
            body,
            base_url=base_url,
            localizer=localizer,
            recorder=recorder,
        )
        return match.group(1) + body + match.group(3)

    return script_re.sub(replace, text)


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
        "3358 known resource gaps • no user data collection</div>"
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


def disable_sensitive_forms(text: str) -> str:
    """Disable credential/account/payment forms in the derived copy.

    Historical pages sometimes carry account or support forms even though the
    corresponding endpoint was never collected.  The static export must not
    turn those forms into a confusing local submission flow.  Search forms
    and ordinary navigation forms remain unchanged.
    """

    form_re = re.compile(r"<form\b(?P<attrs>[^>]*)>(?P<body>.*?)</form\s*>", re.I | re.S)
    sensitive_re = re.compile(
        r"(?:type\s*=\s*['\"]?(?:password|credit-card|creditcard)['\"]?)|"
        r"(?:name\s*=\s*['\"]?[^'\"]*(?:password|passwd|card|cvv|account|payment|billing)[^'\"]*['\"]?)|"
        r"(?:action\s*=\s*['\"]?[^'\"]*(?:/account|/login|/payment|/billing|/checkout)[^'\"]*['\"]?)",
        re.I,
    )

    def form_replace(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        body = match.group("body")
        block = match.group(0)
        if not sensitive_re.search(attrs + body):
            return block
        if "data-offline-disabled" not in attrs.casefold():
            attrs += ' data-offline-disabled="true" onsubmit="return false"'
        def disable_control(control: re.Match[str]) -> str:
            tag = control.group(0)
            if re.search(r"\bdisabled\s*=", tag, re.I):
                return tag
            return tag[:-1] + ' disabled="disabled">'
        body = re.sub(r"<input\b[^>]*?(?:type\s*=\s*['\"]?(?:password|credit-card|creditcard)['\"]?|name\s*=\s*['\"]?[^'\"]*(?:password|passwd|card|cvv|account|payment|billing)[^'\"]*['\"]?)[^>]*>", disable_control, body, flags=re.I)
        body = re.sub(r"<button\b[^>]*\btype\s*=\s*['\"]?submit['\"]?[^>]*>", disable_control, body, flags=re.I)
        body = re.sub(r"<input\b[^>]*\btype\s*=\s*['\"]?submit['\"]?[^>]*>", disable_control, body, flags=re.I)
        return "<form" + attrs + ">" + body + "</form>"

    return form_re.sub(form_replace, text)


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
        var attr = /(\\b(?:src|href|background|poster)\\s*=\\s*)(["']?)([^"'<>\\s]+)\\2/ig;
        return String(markup).replace(attr, function (full, lead, quote, raw) {{
            var mapped = /href\\s*=\\s*$/i.test(lead) ? mapHref(raw) : mapImage(raw);
            return lead + quote + mapped + quote;
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
<div id="__offline-pages-banner" style="background:#241b0b;color:#f7e7b0;padding:6px 10px;font:12px Arial">Unofficial historical educational preservation (not affiliated with Blizzard) • 2008-05-12 21:00:44 • 3358 known resource gaps • no user data collection</div>
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
<div id="__offline-pages-banner" style="background:#241b0b;color:#f7e7b0;padding:6px 10px;font:12px Arial">Unofficial historical educational preservation (not affiliated with Blizzard) • 2008-05-12 21:00:44 • 3358 known resource gaps • no user data collection</div>
<p>Redirecting to <a href="{escaped}">{escaped}</a>.</p></body></html>"""


def generated_404(base_path: str) -> str:
    return generated_uncollected(base_path, "Offline route not found").replace(
        "<meta charset=\"utf-8\">",
        '<meta charset="utf-8"><meta name="offline-pages-404" content="true">',
        1,
    )


def export_pages(
    *,
    source_site: Path = DEFAULT_SITE,
    manifest_path: Path = DEFAULT_MANIFEST,
    output: Path = DEFAULT_OUTPUT,
    base_path: str = DEFAULT_BASE_PATH,
    workspace_root: Path = ROOT,
    max_bytes: int = DEFAULT_MAX_BYTES,
    min_free_bytes: int = DEFAULT_MIN_FREE_BYTES,
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
    estimate = output_estimate(records)
    before_workspace = workspace_size(workspace_root, output)
    free_before = shutil.disk_usage(output.parent).free
    if before_workspace + estimate >= max_bytes:
        raise PagesExportError(f"workspace budget exceeded before export: {before_workspace}+{estimate} >= {max_bytes}")
    if free_before - estimate < min_free_bytes:
        raise PagesExportError(f"disk reserve would be breached before export: {free_before}-{estimate} < {min_free_bytes}")

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
    for generated_route in (
        "/__offline/uncollected/index.html",
        "/__offline/missing.html",
        "/__offline/pages_runtime.js",
        "/__offline/route-map.json",
        "/404.html",
    ):
        route_lookup.setdefault(generated_route, static_url(base_path, generated_route.lstrip("/")))

    origin_index = {str(k): str(v) for k, v in (manifest.get("origin_index") or {}).items()}
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
                text = rewrite_inline_scripts(text, base_url=base_url, localizer=localizer, recorder=recorder)
                text = normalize_html_charset(text)
                text = disable_sensitive_forms(text)
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
                  "and collects no user data. The archive retains known gaps (3358 resource references) and "
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
            "stats": dict(stats) | {"source_records": len(records), "output_files": len(provenance), "route_aliases": len(aliases)},
            "security": {"external_fetches": False, "project_prefix": base_path, "source_unchanged": True, "path_traversal_rejected": True},
        }
        prov_data = (json.dumps(provenance_payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        (partial / "export-provenance.json").write_bytes(prov_data)
        after_workspace = workspace_size(workspace_root, output)
        free_after = shutil.disk_usage(output.parent).free
        if after_workspace >= max_bytes or free_after < min_free_bytes:
            raise PagesExportError(f"budget exceeded after export: workspace={after_workspace}, free={free_after}")
        partial.replace(output)
        return {"output": str(output), "output_files": len(provenance), "manifest_sha256": manifest_sha, "base_path": base_path, "workspace_bytes": after_workspace, "disk_free_bytes": free_after, "estimated_bytes": estimate, "stats": dict(stats)}
    except Exception:
        shutil.rmtree(partial, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH)
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--min-free-bytes", type=int, default=DEFAULT_MIN_FREE_BYTES)
    args = parser.parse_args(argv)
    try:
        result = export_pages(output=args.output, source_site=args.site, manifest_path=args.manifest, base_path=args.base_path, max_bytes=args.max_bytes, min_free_bytes=args.min_free_bytes)
    except PagesExportError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

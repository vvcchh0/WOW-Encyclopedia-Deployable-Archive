"""Turn retired account and business pages into explicit historical exhibits.

The frozen mirror deliberately keeps the captured source pages unchanged.  This
module is used only by the GitHub Pages exporter, after URL localization and
the existing form-staticization pass.  The three VISA reward routes receive a
small self-contained exhibit so a deep link cannot present an old credential
or payment workflow as a live service.  A smaller, route-scoped text pass adds
the same historical context to selected business and download pages.
"""

from __future__ import annotations

import html
import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Iterable


VISA_ROUTE = "/visa/index.html"
VISA_IMAGE_ROUTES = (
    "/visa/images/credit_back_1.jpg",
    "/visa/images/credit_back_2.jpg",
    "/visa/images/credit_back_3-2.jpg",
    "/visa/images/credit_back_3.jpg",
    "/visa/images/title_1.png",
    "/visa/images/title_2.png",
)


P0_ROUTES = frozenset(
    {
        VISA_ROUTE,
        "/visa/reward/index.html",
        "/visa/reward/login.html",
        "/visa/reward/wow-login.html",
    }
)

# These are manifest aliases, but keeping the mapping here makes direct unit
# tests and future exporters agree on which page is the canonical exhibit.
P0_ALIASES = {
    "/visa": VISA_ROUTE,
    "/visa/": VISA_ROUTE,
    "/visa/reward": "/visa/reward/index.html",
    "/visa/reward/": "/visa/reward/index.html",
    "/visa/reward/login": "/visa/reward/login.html",
    "/visa/reward/wow-login": "/visa/reward/wow-login.html",
}

P1_ROUTES = frozenset(
    {
        "/visa/index.html",
        "/misc/deals.html",
        "/misc/beta-signup.html",
        "/misc/promotion.html",
        "/community/stories/submit.html",
        "/contests/l70etc-musicvideo/submit.html",
        "/policy/index.html",
        "/downloads/index.html",
        "/downloads/other-downloads.html",
        "/downloads/languagepack-en.xml",
        "/downloads/languagepack-es.xml",
        "/ui/index.html",
    }
)

TRIAL_ROUTE = "/burningcrusade/trial/index.html"
NEWS_UPGRADE_ROUTE = "/news/rss-02-2007.xml"
NEWS_UPGRADE_ENTRY_ID = "news2-1-07-1212"
PTR_ROUTE = "/ptr/index.html"
PTR_ALIASES = {
    "/ptr": PTR_ROUTE,
    "/ptr/": PTR_ROUTE,
    PTR_ROUTE: PTR_ROUTE,
}

_HISTORICAL_ACCOUNT_TARGETS = {
    ("signup.worldofwarcraft.com", "/"): "Historical: Create Account",
    ("www.worldofwarcraft.com", "/account/"): "Historical: Manage Account",
    ("www.worldofwarcraft.com", "/loginsupport/"): "Historical: Retrieve Password",
    ("www.worldofwarcraft.com", "/loginsupport/password.html"): "Historical: Retrieve Password",
}
_HISTORICAL_ACCOUNT_LABELS = frozenset({"Create Account", "Manage Account", "Retrieve Password"})


def canonical_exhibit_route(route: str) -> str | None:
    """Return a P0 canonical route for a canonical or manifest alias."""

    normalized = "/" + route.lstrip("/")
    if normalized in PTR_ALIASES:
        return PTR_ALIASES[normalized]
    return P0_ALIASES.get(normalized, normalized if normalized in P0_ROUTES else None)


def is_historical_exhibit_route(route: str) -> bool:
    return canonical_exhibit_route(route) is not None


_EXHIBIT_CSS = """
html, body { margin: 0; padding: 0; }
body { background: #f2e6ca; color: #2a2117; font: 16px/1.55 Georgia, serif; }
.historical-exhibit { box-sizing: border-box; max-width: 820px; margin: 0 auto; padding: 20px 16px 48px; }
.historical-exhibit .kicker { color: #765b2f; font: 13px/1.3 Arial, sans-serif; letter-spacing: .04em; text-transform: uppercase; }
.historical-exhibit h1 { margin: 7px 0 14px; color: #234c83; font: 30px/1.15 Georgia, serif; }
.historical-exhibit h2 { margin: 24px 0 8px; color: #5a3e21; font-size: 21px; }
.historical-exhibit p { max-width: 700px; }
.historical-exhibit .notice { background: #fff8e6; border: 1px solid #c8ad76; border-radius: 3px; padding: 13px 15px; }
.historical-exhibit .history-list { margin: 8px 0 0; padding-left: 23px; }
.historical-exhibit .exhibit-links { display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 0; }
.historical-exhibit .exhibit-link { display: inline-block; border: 1px solid #8b632c; border-radius: 3px; background: #f7d28a; color: #382510; padding: 8px 12px; text-decoration: none; }
.historical-exhibit .exhibit-link:hover, .historical-exhibit .exhibit-link:focus { background: #ffe4ad; }
.historical-exhibit figure { display: inline-block; vertical-align: top; width: min(100%, 340px); margin: 10px 16px 10px 0; padding: 10px; background: #fff; border: 1px solid #c8b58e; box-sizing: border-box; }
.historical-exhibit figure img { display: block; max-width: 100%; height: auto; margin: 0 auto 8px; }
.historical-exhibit figcaption { color: #554735; font: 13px/1.4 Arial, sans-serif; }
.historical-exhibit dl { margin: 10px 0; }
.historical-exhibit dt { margin-top: 8px; color: #5a3e21; font-weight: bold; }
.historical-exhibit dd { margin: 2px 0 0 18px; }
.historical-exhibit .return { margin-top: 30px; font: 14px/1.4 Arial, sans-serif; }
@media (max-width: 560px) {
  .historical-exhibit { padding: 16px 12px 34px; }
  .historical-exhibit h1 { font-size: 25px; }
  .historical-exhibit .exhibit-links { display: block; }
  .historical-exhibit .exhibit-link { display: block; margin: 8px 0; }
}
""".strip()


def _local(base_path: str, route: str) -> str:
    prefix = base_path or ""
    if prefix and not prefix.startswith("/"):
        prefix = "/" + prefix
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    return prefix + route.lstrip("/")


def _render_trial_exhibit(base_path: str, route: str) -> str:
    """Render the captured 2008 trial selector as a static local exhibit.

    The source capture is intentionally kept as the original binary.  This
    page describes the two choices shown by that capture while removing its
    retired account target, tracking script, cookie initializer, and image
    dependencies that were not recovered with the page.
    """

    home = _local(base_path, "/")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2008 World of Warcraft Trial Selector — Historical Exhibit</title>
<meta name="description" content="Historical exhibit of the 2008 World of Warcraft trial selector">
<style>{_EXHIBIT_CSS}</style></head><body>
<main class="historical-exhibit" data-exhibit-route="{html.escape(route, quote=True)}">
<div class="kicker">2008 archive · Historical exhibit</div>
<h1>2008 World of Warcraft trial selector</h1>
<p class="notice">This page preserves the captured trial selector as a static historical exhibit. The former trial service and its account destinations are retired.</p>
<p>The capture presented two side-by-side choices for visitors who wanted to learn about a ten-day trial:</p>
<div class="exhibit-links" aria-label="Choices shown in the 2008 capture">
  <div class="exhibit-link"><strong>Burning Crusade</strong><br><span>The left-hand choice in the captured selector.</span></div>
  <div class="exhibit-link"><strong>World of Warcraft</strong><br><span>The right-hand choice in the captured selector.</span></div>
</div>
<h2>What remains missing</h2>
<p>The split-panel and footer artwork referenced under <code>images/</code> has not been recovered.</p>
<p>Registration is unavailable in this historical exhibit.</p>
<p class="return"><a href="{html.escape(home, quote=True)}">Return to the local archive home</a></p>
</main></body></html>'''


def _ptr_verified_facts(source_text: str, source_metadata: dict[str, object] | None) -> list[str]:
    """Return only source-backed PTR statements suitable for a static exhibit."""

    # The accepted original body is the authority for exhibit facts.  Metadata
    # carries provenance such as the capture timestamp, but never arbitrary
    # replacement copy supplied by a caller.
    plain = html.unescape(re.sub(r"<[^>]+>", " ", source_text or ""))
    plain = " ".join(plain.split())
    facts: list[str] = []
    if re.search(r"Public Test Realms.*?test upcoming content patches.*?live realms", plain, re.I):
        facts.append(
            "The Public Test Realms were used to test upcoming content patches in a public environment before release to live realms."
        )
    if re.search(r"feedback from the public test.*?test realm forum", plain, re.I):
        facts.append(
            "Feedback came from the public test and the test realm forum."
        )
    return facts


def _format_ptr_capture(source_metadata: dict[str, object] | None) -> str | None:
    """Format the accepted manifest timestamp as a human UTC capture date."""

    metadata = source_metadata or {}
    actual_timestamp = str(metadata.get("actual_timestamp") or "").strip()
    if re.fullmatch(r"\d{14}", actual_timestamp):
        try:
            captured = datetime.strptime(actual_timestamp, "%Y%m%d%H%M%S").replace(
                tzinfo=timezone.utc
            )
            return captured.strftime("%Y-%m-%d %H:%M:%S UTC")
        except ValueError:
            pass
    for key in ("actual_memento", "capture"):
        value = str(metadata.get(key) or "").strip()
        if not value:
            continue
        try:
            captured = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if captured.tzinfo is None:
                captured = captured.replace(tzinfo=timezone.utc)
            return captured.astimezone(timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        except ValueError:
            return value
    return None


def _render_ptr_exhibit(
    base_path: str,
    route: str,
    *,
    source_text: str = "",
    source_metadata: dict[str, object] | None = None,
) -> str:
    """Render the PTR capture as a neutral, static historical exhibit.

    Operational character-copy, download, form, and script behavior from the
    captured page is intentionally omitted.  Only facts found in the selected
    source text or an accepted source manifest are described.
    """

    # Pages emits the generated archive root at index.html; the captured
    # /index.xml entity is a separate static XML/HTML output and is not the
    # archive home link.
    home = _local(base_path, "/index.html")
    guide = _local(base_path, "/info/basics/guide.html")
    faq = _local(base_path, "/info/faq/ptr.html")
    patchnotes = _local(base_path, "/patchnotes/test-realm-patchnotes.html")
    capture = _format_ptr_capture(source_metadata)
    capture_note = (
        "Selected archival capture: " + html.escape(str(capture)) + "."
        if capture
        else "The selected source capture is preserved in the local archive."
    )
    facts = _ptr_verified_facts(source_text, source_metadata)
    facts_markup = "".join(f"<li>{html.escape(fact)}</li>" for fact in facts)
    if not facts_markup:
        facts_markup = "<li>The selected source is presented here as a static historical exhibit.</li>"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>World of Warcraft Public Test Realm — Historical Exhibit</title>
<meta name="description" content="Historical exhibit of a World of Warcraft Public Test Realm capture">
<style>{_EXHIBIT_CSS}</style></head><body>
<main class="historical-exhibit" data-exhibit-route="{html.escape(PTR_ROUTE, quote=True)}">
<div class="kicker">Historical exhibit</div>
<h1>World of Warcraft Public Test Realm</h1>
<p class="notice">{capture_note} This historical exhibit preserves the capture as archival material; former operational controls are not enabled.</p>
<h2>About the Public Test Realm</h2>
<ul class="history-list">{facts_markup}</ul>
<h2>Related archived pages</h2>
<div class="exhibit-links" aria-label="Related archived pages">
  <a class="exhibit-link" href="{html.escape(faq, quote=True)}">PTR F.A.Q.</a>
  <a class="exhibit-link" href="{html.escape(patchnotes, quote=True)}">Test Realm Patch Notes</a>
  <a class="exhibit-link" href="{html.escape(guide, quote=True)}">Local Game Guide</a>
</div>
<p class="return"><a href="{html.escape(home, quote=True)}">Archive home</a></p>
</main></body></html>'''


def _p0_shell(*, base_path: str, route: str, title: str, heading: str, intro: str, body: str) -> str:
    parent = _local(base_path, "/visa/reward/index.html")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="Historical exhibit of the 2008 World of Warcraft rewards site">
<style>{_EXHIBIT_CSS}</style></head><body>
<main class="historical-exhibit" data-exhibit-route="{html.escape(route, quote=True)}">
<div class="kicker">2008 archive · Historical exhibit</div>
<h1>{html.escape(heading)}</h1>
<p class="notice">{html.escape(intro)}</p>
{body}
<p class="return"><a href="{html.escape(parent, quote=True)}">View the 2008 rewards service exhibit</a></p>
</main></body></html>'''


def _render_p0_index(base_path: str, route: str) -> str:
    wow = _local(base_path, "/visa/reward/wow-login.html")
    card = _local(base_path, "/visa/reward/login.html")
    wow_image = _local(base_path, "/visa/reward/images/button-have3.gif")
    card_image = _local(base_path, "/visa/reward/images/button-donthave3.gif")
    body = f'''<p>This page preserves the retired 2008 rewards-site selection screen as a static exhibit. The service no longer accepts accounts, card details, or reward requests.</p>
<div class="exhibit-links">
  <a class="exhibit-link" href="{html.escape(wow, quote=True)}">View the 2008 World of Warcraft account-sign-in exhibit</a>
  <a class="exhibit-link" href="{html.escape(card, quote=True)}">View the 2008 card-rewards identity exhibit</a>
</div>
<h2>Interface artwork from the capture</h2>
<figure><img src="{html.escape(wow_image, quote=True)}" alt="Archived 2008 rewards interface artwork"><figcaption>The first image is retained as historical interface artwork. It is not an active sign-in control.</figcaption></figure>
<figure><img src="{html.escape(card_image, quote=True)}" alt="Archived 2008 card rewards interface artwork"><figcaption>The second image is retained as historical interface artwork. It is not an active card or payment service.</figcaption></figure>
<p>No personal, account, or payment information is requested here.</p>'''
    return _p0_shell(
        base_path=base_path,
        route=route,
        title="2008 World of Warcraft Rewards Service — Historical Exhibit",
        heading="2008 World of Warcraft Rewards service",
        intro="This independent archive displays a retired 2008 Blizzard website page. The rewards service is historical and unavailable.",
        body=body,
    )


def _render_p0_identity(base_path: str, route: str) -> str:
    body = '''<p>The captured 2008 interface was used for a card-rewards identity check. The service has been retired and this exhibit contains no editable fields, sign-in action, or current account workflow.</p>
<h2>What the historical interface showed</h2>
<dl><dt>Fields visible in the capture</dt><dd>The page contained a full name, postal code, date of birth, last four digits of a Social Security Number, and a security-code field.</dd>
<dt>Historical purpose</dt><dd>Those labels belonged to the former rewards service’s identity-check flow in the 2008 capture.</dd></dl>
<p>No personal, account, or payment information is requested here. Please treat the labels above as archival description only.</p>'''
    return _p0_shell(
        base_path=base_path,
        route=route,
        title="2008 Card Rewards Identity Page — Historical Exhibit",
        heading="2008 card-rewards identity page",
        intro="This independent archive displays the retired identity page as a historical exhibit. The former rewards service is unavailable.",
        body=body,
    )


def _render_p0_wow(base_path: str, route: str) -> str:
    body = '''<p>The captured 2008 interface was used for the World of Warcraft rewards account sign-in. The service has been retired and this exhibit contains no editable fields, sign-in action, or current account workflow.</p>
<h2>What the historical interface showed</h2>
<dl><dt>Fields visible in the capture</dt><dd>The page contained labels for an account name and password.</dd>
<dt>Historical purpose</dt><dd>Those labels belonged to the former rewards service’s account sign-in flow in the 2008 capture.</dd></dl>
<p>No personal or account information is requested here. Please treat the labels above as archival description only.</p>'''
    return _p0_shell(
        base_path=base_path,
        route=route,
        title="2008 World of Warcraft Account Sign-In — Historical Exhibit",
        heading="2008 World of Warcraft account sign-in page",
        intro="This independent archive displays the retired account page as a historical exhibit. The former rewards service is unavailable.",
        body=body,
    )


def _render_visa_exhibit(base_path: str, route: str) -> str:
    """Render the recovered Visa promotion as non-interactive exhibit art."""

    home = _local(base_path, "/")
    reward = _local(base_path, "/visa/reward/index.html")
    captions = {
        "credit_back_1.jpg": "2008 promotion — upper frame",
        "credit_back_2.jpg": "2008 promotion — lower frame",
        "credit_back_3-2.jpg": "2008 promotion — historical offer panel",
        "credit_back_3.jpg": "2008 promotion — alternate offer panel",
        "title_1.png": "2008 promotion — title heading",
        "title_2.png": "2008 promotion — alternate title heading",
    }
    figures: list[str] = []
    for image_route in VISA_IMAGE_ROUTES:
        name = image_route.rsplit("/", 1)[-1]
        image = html.escape(_local(base_path, image_route), quote=True)
        label = html.escape(captions[name], quote=True)
        artwork_name = html.escape(name, quote=True)
        figures.append(
            f'''<figure data-visa-artwork="{artwork_name}">
  <img src="{image}" alt="{label}">
  <figcaption>{label}</figcaption>
</figure>'''
        )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2008 World of Warcraft Rewards Visa promotion — Historical Exhibit</title>
<meta name="description" content="Historical exhibit of the 2008 World of Warcraft Rewards Visa promotion">
<style>{_EXHIBIT_CSS}</style></head><body>
<main class="historical-exhibit" data-exhibit-route="{html.escape(route, quote=True)}">
<div class="kicker">2008 archive · Historical exhibit</div>
<h1>2008 World of Warcraft Rewards Visa promotion</h1>
<p class="notice">Images from a 2008 World of Warcraft Rewards Visa promotion, preserved as a historical exhibit. Applications and reward accounts are unavailable here.</p>
<section aria-label="Recovered 2008 promotional artwork">
{''.join(figures)}
</section>
<p class="return"><a href="{html.escape(home, quote=True)}">Archive home</a> · <a href="{html.escape(reward, quote=True)}">View the 2008 rewards service exhibit</a></p>
</main></body></html>'''


def render_historical_exhibit(
    text: str,
    route: str,
    *,
    base_path: str = "",
    source_metadata: dict[str, object] | None = None,
) -> str:
    """Return a standalone historical exhibit, or the original derived HTML."""

    canonical = canonical_exhibit_route(route)
    if canonical is None:
        return text
    if canonical == PTR_ROUTE:
        return _render_ptr_exhibit(
            base_path,
            canonical,
            source_text=text,
            source_metadata=source_metadata,
        )
    if canonical == VISA_ROUTE:
        return _render_visa_exhibit(base_path, canonical)
    if canonical.endswith("/index.html"):
        return _render_p0_index(base_path, canonical)
    if canonical.endswith("/login.html"):
        return _render_p0_identity(base_path, canonical)
    return _render_p0_wow(base_path, canonical)


class _VisibleTextParser(HTMLParser):
    """Collect source spans for visible text while skipping script/style data."""

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.text = text
        self._line_starts = [0]
        self._line_starts.extend(match.end() for match in re.finditer("\n", text))
        self._skip_depth = 0
        self.parts: list[tuple[int, int, str]] = []

    def _offset(self) -> int:
        line, column = self.getpos()
        return self._line_starts[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in {"script", "style"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth and data:
            start = self._offset()
            self.parts.append((start, start + len(data), data))

    def handle_entityref(self, name: str) -> None:
        if not self._skip_depth:
            start = self._offset()
            raw = "&" + name + ";"
            self.parts.append((start, start + len(raw), html.unescape(raw)))

    def handle_charref(self, name: str) -> None:
        if not self._skip_depth:
            start = self._offset()
            raw = "&#" + name + ";"
            self.parts.append((start, start + len(raw), html.unescape(raw)))


@dataclass
class _HistoricalAccountAnchor:
    attrs: dict[str, str]
    parts: list[tuple[int, int, str]]
    depth: int


class _HistoricalAccountAnchorParser(HTMLParser):
    """Collect visible labels from anchors without inspecting script/style."""

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.text = text
        self._line_starts = [0]
        self._line_starts.extend(match.end() for match in re.finditer("\n", text))
        self._skip_depth = 0
        self._tag_depth = 0
        self._anchors: list[tuple[_HistoricalAccountAnchor, int, int | None]] = []
        self.completed: list[tuple[_HistoricalAccountAnchor, int, int]] = []

    def _offset(self) -> int:
        line, column = self.getpos()
        return self._line_starts[line - 1] + column

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {name.casefold(): value for name, value in attrs if value is not None}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        folded = tag.casefold()
        start = self._offset()
        if folded in {"script", "style"}:
            self._skip_depth += 1
        if folded == "a" and not self._skip_depth:
            raw = self.get_starttag_text() or "<a>"
            anchor = _HistoricalAccountAnchor(self._attrs(attrs), [], self._tag_depth)
            self._anchors.append((anchor, start, start + len(raw)))
        self._tag_depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        folded = tag.casefold()
        self._tag_depth = max(0, self._tag_depth - 1)
        if folded == "a" and self._anchors:
            anchor, start, start_end = self._anchors.pop()
            self.completed.append((anchor, start, self._offset()))
        if folded in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1

    def _append_part(self, start: int, end: int, value: str) -> None:
        if not self._skip_depth and self._anchors and value:
            self._anchors[-1][0].parts.append((start, end, value))

    def handle_data(self, data: str) -> None:
        start = self._offset()
        self._append_part(start, start + len(data), data)

    def handle_entityref(self, name: str) -> None:
        start = self._offset()
        raw = "&" + name + ";"
        self._append_part(start, start + len(raw), html.unescape(raw))

    def handle_charref(self, name: str) -> None:
        start = self._offset()
        raw = "&#" + name + ";"
        self._append_part(start, start + len(raw), html.unescape(raw))


def _local_missing_path(base_path: str) -> str | None:
    """Return the exact local missing marker path for one Pages base path."""

    prefix = base_path.strip()
    if not prefix:
        return "/__offline/missing.html"
    if not prefix.startswith("/") or ".." in prefix.split("/"):
        return None
    return prefix.rstrip("/") + "/__offline/missing.html"


def _historical_account_target(
    href: str, *, base_path: str = ""
) -> tuple[str, str] | None:
    """Return an approved missing-resource target from one local anchor."""

    try:
        parsed = urllib.parse.urlsplit(html.unescape(href))
    except ValueError:
        return None
    local_missing_path = _local_missing_path(base_path)
    if (
        local_missing_path is None
        or parsed.scheme
        or parsed.netloc
        or parsed.path != local_missing_path
    ):
        return None
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    requested_values = query.get("requested")
    if not requested_values or len(requested_values) != 1:
        return None
    try:
        requested = urllib.parse.urlsplit(requested_values[0])
    except ValueError:
        return None
    host = (requested.hostname or "").casefold().rstrip(".")
    path = requested.path or "/"
    if requested.scheme.casefold() not in {"http", "https"}:
        return None
    if requested.username or requested.password or requested.query or requested.fragment:
        return None
    if requested.port not in {None, 80, 443}:
        return None
    if (host, path) not in _HISTORICAL_ACCOUNT_TARGETS:
        return None
    return host, path


def rewrite_historical_account_links(text: str, *, base_path: str = "") -> str:
    """Label only approved missing account-service anchors as historical.

    The href is deliberately untouched.  Matching requires both the exact
    visible label and the decoded ``requested`` host/path in the local missing
    marker, so ordinary articles, unrelated links, and script/style strings
    remain unchanged.
    """

    parser = _HistoricalAccountAnchorParser(text)
    try:
        parser.feed(text)
        parser.close()
    except Exception:
        return text
    replacements: list[tuple[int, int, str]] = []
    for anchor, _anchor_start, _anchor_end in parser.completed:
        values = anchor.attrs
        target = _historical_account_target(
            values.get("href", ""), base_path=base_path
        )
        if target is None or not anchor.parts:
            continue
        visible = "".join(part for _start, _end, part in anchor.parts)
        label = " ".join(visible.split())
        if label not in _HISTORICAL_ACCOUNT_LABELS:
            continue
        label_start = len(visible) - len(visible.lstrip())
        label_end = len(visible.rstrip())
        char_ranges: list[tuple[int, int]] = []
        for start, end, part in anchor.parts:
            if end - start == len(part):
                char_ranges.extend((start + index, start + index + 1) for index in range(len(part)))
            else:
                char_ranges.extend((start, end) for _ in part)
        if label_start >= len(char_ranges) or label_end <= label_start:
            continue
        replacements.append((char_ranges[label_start][0], char_ranges[label_end - 1][1], html.escape(_HISTORICAL_ACCOUNT_TARGETS[target])))
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


@dataclass(frozen=True)
class _TextRule:
    old: str
    new: str


_P1_RULES: dict[str, tuple[_TextRule, ...]] = {
    "/visa/index.html": (
        _TextRule("Continue to the Rewards Site", "View the retired 2008 rewards-site exhibit"),
        _TextRule("Apply now!", "2008 application page — historical exhibit"),
        _TextRule("In order to apply, you must be of legal age and have a U.S. address.", "The 2008 page described application eligibility for a service that is now retired."),
        _TextRule("Click here for additional Card benefits and services.", "The 2008 page described additional card benefits and services; that service is retired."),
    ),
    "/misc/deals.html": (
        _TextRule("Apply now!", "2008 offer page — historical exhibit"),
        _TextRule("Check out some of the discounts we currently have available.", "This page preserves discounts described in the 2008 capture; the offers are retired."),
        _TextRule("Sign up for AT&T High Speed Internet and Receive 3 Months of WoW FREE!", "2008 AT&T offer — historical exhibit"),
        _TextRule("AT&T is now offering 3 FREE months of World of Warcraft game time as an incentive to sign up for their High Speed Internet service. Qualifying subscribers will receive a game code by mail redeemable through account management for the free game time. Check out the full details of the offer by clicking here.", "The 2008 offer described promotional game time with an internet service; the offer and its redemption service are retired."),
        _TextRule("Blizzard Entertainment has teamed up with First National Bank of Omaha to bring you a Visa card that rewards you with World of Warcraft game time. Sign up today, and once your application is approved, you will be eligible for special card rewards and benefits. Also check out the World of Warcraft Rewards Visa FAQ to learn more.", "The 2008 page described a promotional rewards card and its eligibility terms; the card service is retired."),
    ),
    "/misc/beta-signup.html": (
        _TextRule("Welcome to the Future Beta Sign-Up Form!", "Welcome to the archived beta sign-up page from 2008."),
        _TextRule("we welcome you to enter your code now and confirm your spot!", "the 2008 page described a code-based beta registration process that has ended."),
        _TextRule("Along with the Beta Sign-up code, please enter a valid eMail address that will be active for some time.", "The 2008 page described a beta code and an email address for its invitation process; that registration service has ended."),
        _TextRule("Once you enter your information, you should receive a confirmation eMail. We will eMail you again once invitations are being sent; the eMail you receive at that point will contain further instructions.", "The 2008 page described confirmation email messages; no registration or email service is active in this exhibit."),
    ),
    "/misc/promotion.html": (
        _TextRule("Promotion Code Retrieval", "2008 Promotion Code Retrieval — Historical Exhibit"),
        _TextRule("you can use this page to generate an in-game code that will allow you to retrieve your reward.", "the 2008 service could generate an in-game code for a reward; that service is retired."),
        _TextRule("To get the in-game code, you will have to select your region and your realm in the code retrieval frame below. Once you've selected the correct region and realm, you can enter your promotion code in the appropriate fields. You will also need to enter the security input in the field below. Make sure that all the information is correct, and then hit submit. This will take you to another page with your in-game code. Write this code down or print it out; you will need it later.", "The 2008 instructions described selecting a region and realm, entering a promotion code and security input, and receiving an in-game code; the service is retired."),
        _TextRule("then hit submit.", "the original instructions then described submission; this exhibit has no submission service."),
        _TextRule("How to redeem your item", "How the 2008 service described redemption"),
    ),
    "/community/stories/submit.html": (
        _TextRule("Story Submission", "Story Submission — 2008 Historical Exhibit"),
        _TextRule('clicking the "I accept" button', 'the original page described an "I accept" step'),
        _TextRule("Grant of License.", "Historical grant-of-license text from 2008."),
    ),
    "/contests/l70etc-musicvideo/submit.html": (
        _TextRule("Level 70 Elite Tauren Chieftain Music Video Contest", "Level 70 Elite Tauren Chieftain Music Video Contest — 2008 Historical Exhibit"),
        _TextRule("Files must be", "The 2008 contest instructions specified files"),
        _TextRule("Please allow some time for large files to upload completely.", "The original page described upload timing; this archived copy accepts no uploads."),
    ),
    "/policy/index.html": (
        _TextRule("Account Management", "Account Management — historical policy index"),
        _TextRule("Account Creation", "Account Creation — historical policy entry"),
        _TextRule("Password Recovery", "Password Recovery — historical policy entry"),
    ),
    "/downloads/index.html": (
        _TextRule("To download the World of Warcraft game client, click here. (Requires World of Warcraft account)", "The 2008 page described a game-client download requiring an account; the download service is unavailable."),
    ),
    "/downloads/other-downloads.html": (
        _TextRule("you can download the game client and expansion upgrades", "the 2008 page described game-client and expansion downloads"),
        _TextRule("In order to download the game client, a World of Warcraft account is required. To create a new trial account visit Warcraft.com. To upgrade to a full World of Warcraft or Burning Crusade account click here to visit Account Management.", "The original page described account-gated game-client downloads and account upgrades; those services are retired."),
        _TextRule("download our World of Warcraft IAK now.", "the 2008 page described a World of Warcraft IAK download; the software is not included in this archive."),
    ),
    "/downloads/languagepack-en.xml": (
        _TextRule("Download Language Pack:", "Download Language Pack — 2008 historical exhibit"),
        _TextRule("To participate, please download the language pack. For additional information, please refer to the FAQ below.", "The 2008 beta page described downloading a language pack; the package is not included in this archive."),
        _TextRule("To get started, please download the Latin American-Spanish language pack. Once the installer has finished downloading, just click the install button.", "The 2008 page described installing the Latin American-Spanish language pack; the installer is not included in this archive."),
        _TextRule("How do I install the language pack?", "How the 2008 page described language-pack installation"),
        _TextRule("After the language pack has been installed, your game version will be taken back to 2.0, so you'll have to update your game to the latest version available. You can do this simply by logging in, which starts the patching process.", "The 2008 page described a version reset and account sign-in as part of installation; no installer or sign-in service is available here."),
        _TextRule("Yes, you can simply create a trial account and download the language pack to begin testing the Latin American-Spanish version of World of Warcraft.", "The 2008 page described a trial account and language-pack download; registration and downloads are unavailable here."),
        _TextRule("Before entering the game, start the launcher and click the \"Options\" button. At the bottom of the page you can choose which language to use. Inside the game, if you go to the interface setting you also can change the language, but then you will need to restart the game for it to take effect.", "The 2008 page described how language settings were changed after installation; no installation service is available here."),
    ),
    "/downloads/languagepack-es.xml": (
        _TextRule("Paquete de Idiomas", "Paquete de Idiomas — exposición histórica de 2008"),
        _TextRule("versión beta del paquete de idiomas", "la versión beta del paquete de idiomas descrita en la captura de 2008"),
        _TextRule("Para participar, por favor descarga el paquete de idiomas. Para mayor información, no olvides revisar el FAQ.", "La página de 2008 describía una descarga de prueba; el paquete no está incluido en este archivo histórico."),
        _TextRule("Sí, solamente debes crear una cuenta de prueba y descargar el paquete de idiomas para comenzar a probar la versión de World of Warcraft en español para América Latina.", "La página de 2008 describía una cuenta de prueba y una descarga; este archivo no acepta registros ni descargas."),
        _TextRule("Para instalarlo, solamente debes descargar el paquete de idiomas para América Latina en español. Una vez que la descarga del instalador haya finalizado, haz clic en él para que se inicie la instalación.", "La página de 2008 describía la instalación del paquete de idiomas; el instalador no está incluido en este archivo histórico."),
    ),
    "/ui/index.html": (
        _TextRule("User Interface Customization tool", "User Interface Customization tool — 2008 historical exhibit"),
        _TextRule("We welcome our advanced users to download this free tool and explore the possibilities.", "The 2008 page described a free customization tool; the software is not included in this archive."),
        _TextRule("Download for PC", "PC interface tool — 2008 software reference"),
        _TextRule("Download for Mac", "Mac interface tool — 2008 software reference"),
        _TextRule("Download EditingUI.zip", "EditingUI.zip — 2008 software reference"),
        _TextRule("Download WowIPC_SDK.zip", "WowIPC_SDK.zip — 2008 software reference"),
        _TextRule("Repair Utility", "Repair Utility — historical software entry"),
        _TextRule("We have a repair utility that can check your files and replace corrupted files as well.", "The 2008 page described a repair utility; no installer is provided here."),
        _TextRule("You can get the latest version available here.", "The original page linked to a latest repair-utility version; no installer is provided here."),
    ),
}


def _apply_text_rules(text: str, rules: Iterable[_TextRule]) -> str:
    rules = tuple(rules)
    if not rules or not text:
        return text
    # Apply one rule at a time and rebuild the visible projection after each
    # change.  A historical sentence often crosses an anchor (for example,
    # ``please <a>download</a> ...``). Replace only the visible text spans
    # that participate in the match; keep every intervening tag in place so
    # an old capture cannot become structurally malformed.
    for rule in rules:
        if not rule.old:
            continue
        parser = _VisibleTextParser(text)
        try:
            parser.feed(text)
            parser.close()
        except Exception:
            return text
        visible_parts = parser.parts
        visible: list[str] = []
        char_ranges: list[tuple[int, int]] = []
        part_ranges: list[tuple[int, int]] = []
        visible_offset = 0
        for start, end, part in visible_parts:
            part_start = visible_offset
            visible.append(part)
            part_ranges.append((part_start, part_start + len(part)))
            visible_offset += len(part)
            if end - start == len(part):
                char_ranges.extend((start + offset, start + offset + 1) for offset in range(len(part)))
            else:
                # Character/entity references occupy several source
                # characters but represent one visible character.
                char_ranges.extend((start, end) for _ in part)
        projected = "".join(visible)
        # HTML often puts a block or anchor boundary between words without
        # preserving a literal space in the source text.  The route-specific
        # phrases below are long enough to remain unambiguous when whitespace
        # is allowed to collapse at those boundaries.
        pattern_parts = [re.escape(part) if not part.isspace() else r"\s*" for part in re.split(r"(\s+)", rule.old) if part]
        pattern = re.compile("".join(pattern_parts))
        matches = list(pattern.finditer(projected))
        if not matches:
            continue
        replacements: list[tuple[int, int, str]] = []
        for match in matches:
            if match.start() >= len(char_ranges) or match.end() <= 0:
                continue
            affected_parts: list[tuple[int, int]] = []
            for part_start, part_end in part_ranges:
                overlap_start = max(match.start(), part_start)
                overlap_end = min(match.end(), part_end)
                if overlap_start < overlap_end:
                    affected_parts.append((overlap_start, overlap_end))
            for index, (overlap_start, overlap_end) in enumerate(affected_parts):
                source_ranges = char_ranges[overlap_start:overlap_end]
                if not source_ranges:
                    continue
                replacement = html.escape(rule.new) if index == 0 else ""
                replacements.append((source_ranges[0][0], source_ranges[-1][1], replacement))
        replacements.sort(key=lambda item: (item[0], item[1]))
        non_overlapping: list[tuple[int, int, str]] = []
        for replacement in replacements:
            if non_overlapping and replacement[0] < non_overlapping[-1][1]:
                continue
            non_overlapping.append(replacement)
        for start, end, replacement in reversed(non_overlapping):
            text = text[:start] + replacement + text[end:]
    return text


_NEWS_UPGRADE_RULES: tuple[_TextRule, ...] = (
    _TextRule(
        "Burning Crusade Direct Online Upgrade Now Available",
        "Burning Crusade Direct Online Upgrade — 2007 Historical Exhibit",
    ),
    _TextRule(
        "You can now buy account-upgrade keys and download the game client for World of Warcraft: The Burning Crusade directly through the account-management section of www.worldofwarcraft.com. The direct online upgrade method is the most convenient way to upgrade to The Burning Crusade and join the millions of players who are already adventuring beyond the Dark Portal.",
        "The February 2007 notice described a former account-upgrade and game-client distribution service for World of Warcraft: The Burning Crusade; those services are retired.",
    ),
    _TextRule(
        "All you need to do is:",
        "Historical steps described in the February 2007 notice:",
    ),
    _TextRule(
        "Login to the former account-management page",
        "The notice described a former account-management sign-in step.",
    ),
    _TextRule(
        'Click The Burning Crusade "Download Now" button',
        "The notice described a Burning Crusade client-download step.",
    ),
    _TextRule(
        "Enter your credit card information",
        "The notice described a payment-information step.",
    ),
    _TextRule(
        "Follow the link to download The Burning Crusade game client",
        "The notice described a game-client distribution step.",
    ),
    _TextRule(
        "That's it! If you haven't upgraded your account yet, now's your chance to take your World of Warcraft experience to the next level, whenever you want.",
        "The notice closed with a 2007 Burning Crusade promotion; account, payment, and download operations are retired.",
    ),
)

_NEWS_UPGRADE_LOGIN_ANCHOR = re.compile(
    r"(?P<prefix>\bLogin\s+to\s*)<a\b[^>]*>\s*"
    r"(?:Historical:\s*)?(?:Manage Account|Account Management)\s*</a>",
    flags=re.I | re.S,
)
_NEWS_UPGRADE_EMPTY_ACTION = re.compile(
    r"<div\b(?P<attrs>[^>]*)>\s*<a\b[^>]*>\s*</a>\s*</div>",
    flags=re.I | re.S,
)
_NEWS_UPGRADE_LOCAL_IMAGE = (
    re.compile(
        r"<img\b[^>]*\bsrc\s*=\s*([\"'])(?P<src>[^\"']*upgradenow\.gif)[\"']",
        flags=re.I | re.S,
    ),
    re.compile(
        r"url\(\s*([\"'])(?P<src>[^\"']*upgradenow\.gif)[\"']\s*\)",
        flags=re.I | re.S,
    ),
)
_NEWS_UPGRADE_STYLE = re.compile(
    r"<style\b[^>]*>.*?</style\s*>",
    flags=re.I | re.S,
)
_NEWS_UPGRADE_CSS_RULE = re.compile(
    r"[^{}]*\.upgradenow\b[^{}]*\{[^{}]*\}",
    flags=re.I | re.S,
)


class _NewsUpgradeEntryParser(HTMLParser):
    """Locate the balanced target news entry without rewriting its siblings."""

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.text = text
        self._line_starts = [0]
        self._line_starts.extend(match.end() for match in re.finditer("\n", text))
        self._div_depth = 0
        self._target_depth: int | None = None
        self.start: int | None = None
        self.end: int | None = None

    def _offset(self) -> int:
        line, column = self.getpos()
        return self._line_starts[line - 1] + column

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        folded = tag.casefold()
        if folded == "div":
            values = {name.casefold(): value for name, value in attrs if value is not None}
            if (
                self._target_depth is None
                and values.get("id") == NEWS_UPGRADE_ENTRY_ID
            ):
                self.start = self._offset()
                self._target_depth = self._div_depth
            self._div_depth += 1

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        # A self-closing div does not contribute to the balanced div depth.
        return None

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() != "div":
            return
        if (
            self._target_depth is not None
            and self.end is None
            and self._div_depth == self._target_depth + 1
        ):
            close_start = self._offset()
            close_end = self.text.find(">", close_start)
            if close_end >= 0:
                self.end = close_end + 1
        self._div_depth = max(0, self._div_depth - 1)


def _news_upgrade_entry_bounds(text: str) -> tuple[int, int] | None:
    parser = _NewsUpgradeEntryParser(text)
    try:
        parser.feed(text)
        parser.close()
    except Exception:
        return None
    if parser.start is None or parser.end is None or parser.end <= parser.start:
        return None
    return parser.start, parser.end


def _rewrite_news_upgrade_login_anchor(text: str) -> str:
    """Remove only the account-management action anchor in the target notice."""

    return _NEWS_UPGRADE_LOGIN_ANCHOR.sub(
        lambda match: match.group("prefix") + "the former account-management page",
        text,
        count=1,
    )


def _news_upgrade_local_image_src(text: str) -> str | None:
    """Return the resolver-local upgradenow GIF URL, never a remote URL."""

    for pattern in _NEWS_UPGRADE_LOCAL_IMAGE:
        match = pattern.search(text)
        if not match:
            continue
        source = html.unescape(match.group("src"))
        parsed = urllib.parse.urlsplit(source)
        if parsed.scheme or parsed.netloc or not source.startswith("/"):
            continue
        if not parsed.path.casefold().endswith("/news/images/07-02/upgradenow.gif"):
            continue
        return source
    return None


def _rewrite_news_upgrade_artwork(text: str) -> str:
    """Replace the empty upgrade action with a static two-state artwork figure."""

    source = _news_upgrade_local_image_src(text)
    if source is None:
        return text
    figure = (
        '<figure class="historical-news-artwork" '
        'data-historical-exhibit="news-upgrade-artwork" '
        'style="box-sizing:border-box;width:100%;max-width:377px;margin:1em auto;text-align:center;">\n'
        f'<img src="{html.escape(source, quote=True)}" width="377" height="148" '
        'alt="Archived 2007 Burning Crusade upgrade artwork" '
        'style="display:block;width:100%;max-width:377px;height:auto;margin:0 auto;">\n'
        '<figcaption style="margin-top:.5em;line-height:1.4;">Historical 2007 artwork from the Burning Crusade upgrade notice. '
        'The original two-state graphic is preserved as static exhibit artwork; '
        'no account, payment, upgrade, or download action is available.</figcaption>\n'
        '</figure>'
    )

    replaced = False

    def replace(match: re.Match[str]) -> str:
        nonlocal replaced
        attrs = match.group("attrs")
        class_match = re.search(
            r"\bclass\s*=\s*([\"'])(?P<classes>[^\"']*)\1",
            attrs,
            flags=re.I | re.S,
        )
        if (
            replaced
            or not class_match
            or "upgradenow" not in class_match.group("classes").casefold().split()
        ):
            return match.group(0)
        replaced = True
        return figure

    rewritten = _NEWS_UPGRADE_EMPTY_ACTION.sub(replace, text)
    if not replaced:
        return text
    # The original CSS makes the empty anchor an operational hover target. It
    # is route-local and can be removed once the static figure is installed.
    def remove_upgrade_rules(match: re.Match[str]) -> str:
        block = match.group(0)
        opening = re.match(r"<style\b[^>]*>", block, flags=re.I | re.S)
        closing = re.search(r"</style\s*>$", block, flags=re.I | re.S)
        if opening is None or closing is None:
            return block
        body_start = opening.end()
        body_end = closing.start()
        body = block[body_start:body_end]
        cleaned = _NEWS_UPGRADE_CSS_RULE.sub("", body)
        if cleaned == body:
            return block
        if not cleaned.strip():
            return ""
        return block[:body_start] + cleaned + block[body_end:]

    return _NEWS_UPGRADE_STYLE.sub(remove_upgrade_rules, rewritten)


def transform_news_upgrade_page(text: str) -> str:
    """Turn the known February 2007 upgrade notice into a static exhibit."""

    rewritten = _rewrite_news_upgrade_login_anchor(text)
    rewritten = _apply_text_rules(rewritten, _NEWS_UPGRADE_RULES)
    return _rewrite_news_upgrade_artwork(rewritten)


def _transform_news_upgrade_entry(text: str) -> str:
    """Rewrite only the balanced target entry inside the February 2007 feed."""

    bounds = _news_upgrade_entry_bounds(text)
    if bounds is None:
        return text
    start, end = bounds
    entry = text[start:end]
    entry = transform_news_upgrade_page(entry)
    return text[:start] + entry + text[end:]


_PROMOTION_REDEMPTION_LIST = re.compile(
    r"(?:<p\s*/?>\s*)?In order to claim your in-game item,\s*"
    r"please follow these five steps:\s*<ol\b[^>]*>.*?(?=</td\s*>)",
    flags=re.I | re.S,
)


def _rewrite_promotion_redemption_list(text: str) -> str:
    """Replace the captured redemption list before its enclosing table cell."""

    replacement = (
        '<p class="historical-redemption-note">The 2008 page listed five steps '
        "for redemption; this exhibit has no redemption workflow.</p>"
    )
    return _PROMOTION_REDEMPTION_LIST.sub(replacement, text, count=1)


def _p1_banner(route: str) -> str:
    title = {
        "/visa/index.html": "2008 card promotion page",
        "/misc/deals.html": "2008 offers page",
        "/misc/beta-signup.html": "2008 beta registration page",
        "/misc/promotion.html": "2008 promotion-code page",
        "/community/stories/submit.html": "2008 story submission page",
        "/contests/l70etc-musicvideo/submit.html": "2008 music-video contest page",
        "/policy/index.html": "2008 policy page",
        "/downloads/index.html": "2008 downloads page",
        "/downloads/other-downloads.html": "2008 additional downloads page",
        "/downloads/languagepack-en.xml": "2008 language-pack page",
        "/downloads/languagepack-es.xml": "página del paquete de idiomas de 2008",
        "/ui/index.html": "2008 interface-tools page",
    }[route]
    return '<aside class="historical-exhibit-context" data-historical-exhibit="p1" style="box-sizing:border-box;width:100vw;max-width:none;margin:10px 0;padding:10px 14px;background:#fff8e6;border:1px solid #c8ad76;color:#2a2117;font:14px/1.45 Arial,sans-serif"><strong>Historical exhibit:</strong> ' + html.escape(title) + ' from the independent 2008 archive. Retired services and software installers are unavailable; this page accepts no submissions, credentials, or files.</aside>'


def transform_p1_page(text: str, route: str) -> str:
    """Add a route-specific historical context and exact visible substitutions."""

    route = "/" + route.lstrip("/")
    if route not in P1_ROUTES:
        return text
    rewritten = _apply_text_rules(text, _P1_RULES.get(route, ()))
    if route == "/misc/promotion.html":
        rewritten = _rewrite_promotion_redemption_list(rewritten)
    if not re.search(
        r'<meta\b(?=[^>]*\bname\s*=\s*["\']viewport["\'])[^>]*>',
        rewritten,
        flags=re.I,
    ):
        head = re.search(r"<head\b[^>]*>", rewritten, flags=re.I)
        if head:
            rewritten = (
                rewritten[: head.end()]
                + '\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                + rewritten[head.end() :]
            )
    if 'data-historical-exhibit="p1"' in rewritten:
        return rewritten
    banner = _p1_banner(route)
    body = re.search(r"<body\b[^>]*>", rewritten, flags=re.I)
    if body:
        return rewritten[: body.end()] + "\n" + banner + rewritten[body.end() :]
    return banner + rewritten


def _disable_story_submission_scripts(text: str) -> str:
    """Remove only the two retired story-form initialization calls."""

    disabled = (
        "<!-- Historical exhibit: retired story submission behavior disabled. -->"
    )
    script_pattern = re.compile(r"<script\b[^>]*>.*?</script\s*>", flags=re.I | re.S)

    def replace(match: re.Match[str]) -> str:
        block = match.group(0)
        if re.search(
            r"\b(?:nameopt|circumsize)\s*\(\s*document\.getElementById\s*\(",
            block,
            flags=re.I,
        ):
            return disabled
        return block

    return script_pattern.sub(replace, text)


def transform_derived_page(
    text: str,
    route: str,
    *,
    base_path: str = "",
    source_metadata: dict[str, object] | None = None,
) -> str:
    """Apply route-specific replacements, then the narrow P1 historical pass."""

    if is_historical_exhibit_route(route):
        return render_historical_exhibit(
            text,
            route,
            base_path=base_path,
            source_metadata=source_metadata,
        )
    normalized_route = "/" + route.lstrip("/")
    if normalized_route == TRIAL_ROUTE:
        return _render_trial_exhibit(base_path, TRIAL_ROUTE)
    rewritten = transform_p1_page(
        rewrite_historical_account_links(text, base_path=base_path), route
    )
    if normalized_route == NEWS_UPGRADE_ROUTE:
        return _transform_news_upgrade_entry(rewritten)
    if normalized_route == "/community/stories/submit.html":
        rewritten = _disable_story_submission_scripts(rewritten)
    return rewritten

"""Load an isolated visa-exhibit candidate without changing production code."""

from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "tools" / "historical_exhibits.py"

VISA_IMAGE_ROUTES = (
    "/visa/images/credit_back_1.jpg",
    "/visa/images/credit_back_2.jpg",
    "/visa/images/credit_back_3-2.jpg",
    "/visa/images/credit_back_3.jpg",
    "/visa/images/title_1.png",
    "/visa/images/title_2.png",
)

VISA_ROUTE_BLOCK = '''VISA_ROUTE = "/visa/index.html"
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
)'''
VISA_ROUTE_BLOCK_OLD = '''P0_ROUTES = frozenset(
    {
        "/visa/reward/index.html",
        "/visa/reward/login.html",
        "/visa/reward/wow-login.html",
    }
)'''

VISA_ALIAS_BLOCK = '''P0_ALIASES = {
    "/visa": VISA_ROUTE,
    "/visa/": VISA_ROUTE,
    "/visa/reward": "/visa/reward/index.html",
    "/visa/reward/": "/visa/reward/index.html",
    "/visa/reward/login": "/visa/reward/login.html",
    "/visa/reward/wow-login": "/visa/reward/wow-login.html",
}'''
VISA_ALIAS_BLOCK_OLD = '''P0_ALIASES = {
    "/visa/reward": "/visa/reward/index.html",
    "/visa/reward/": "/visa/reward/index.html",
    "/visa/reward/login": "/visa/reward/login.html",
    "/visa/reward/wow-login": "/visa/reward/wow-login.html",
}'''

VISA_RENDER_FUNCTION = r"""def _render_visa_exhibit(base_path: str, route: str) -> str:
    # Render the 2008 Visa promotion as non-interactive archival artwork.

    home = _local(base_path, "/")
    reward = _local(base_path, "/visa/reward/index.html")
    figures: list[str] = []
    for image_route in VISA_IMAGE_ROUTES:
        name = image_route.rsplit("/", 1)[-1]
        image = html.escape(_local(base_path, image_route), quote=True)
        label = html.escape(name, quote=True)
        figures.append(
            f'''<figure data-visa-artwork="{label}">
  <img src="{image}" alt="Archived 2008 Rewards Visa promotional artwork: {label}">
  <figcaption>This 2008 promotional image fragment is preserved as static historical artwork; it has no interactive or transaction function.</figcaption>
</figure>'''
        )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2008 World of Warcraft Rewards Visa Promotion — Historical Exhibit</title>
<meta name="description" content="Historical exhibit of the 2008 World of Warcraft Rewards Visa promotion">
<style>{_EXHIBIT_CSS}</style></head><body>
<main class="historical-exhibit" data-exhibit-route="{html.escape(route, quote=True)}">
<div class="kicker">2008 archive · Historical exhibit</div>
<h1>2008 World of Warcraft Rewards Visa promotion</h1>
<p class="notice">This page preserves six recovered image fragments from a 2008 World of Warcraft Rewards Visa promotion. The offer and its associated services were historical and are unavailable.</p>
<p>The captured page described promotional card artwork and offer language. This exhibit displays the original image bytes as non-interactive archival material.</p>
<section aria-label="Recovered 2008 promotional artwork">
{''.join(figures)}
</section>
<p class="return"><a href="{html.escape(home, quote=True)}">Archive home</a> · <a href="{html.escape(reward, quote=True)}">View the 2008 rewards service exhibit</a></p>
</main></body></html>'''
"""

DISPATCH_OLD = '''    if canonical == PTR_ROUTE:
        return _render_ptr_exhibit(
            base_path,
            canonical,
            source_text=text,
            source_metadata=source_metadata,
        )
    if canonical.endswith("/index.html"):
        return _render_p0_index(base_path, canonical)'''
DISPATCH_NEW = '''    if canonical == PTR_ROUTE:
        return _render_ptr_exhibit(
            base_path,
            canonical,
            source_text=text,
            source_metadata=source_metadata,
        )
    if canonical == VISA_ROUTE:
        return _render_visa_exhibit(base_path, canonical)
    if canonical.endswith("/index.html"):
        return _render_p0_index(base_path, canonical)'''


def source_sha256() -> str:
    return hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def patched_source() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    if source.count(VISA_ROUTE_BLOCK_OLD) != 1:
        raise RuntimeError("visa P0 route context is absent or ambiguous")
    if source.count(VISA_ALIAS_BLOCK_OLD) != 1:
        raise RuntimeError("visa P0 alias context is absent or ambiguous")
    if source.count("def render_historical_exhibit(\n") != 1:
        raise RuntimeError("historical exhibit render insertion point is absent or ambiguous")
    if source.count(DISPATCH_OLD) != 1:
        raise RuntimeError("historical exhibit dispatch context is absent or ambiguous")
    rewritten = source.replace(VISA_ROUTE_BLOCK_OLD, VISA_ROUTE_BLOCK, 1)
    rewritten = rewritten.replace(VISA_ALIAS_BLOCK_OLD, VISA_ALIAS_BLOCK, 1)
    rewritten = rewritten.replace(
        "def render_historical_exhibit(\n",
        VISA_RENDER_FUNCTION + "\n\ndef render_historical_exhibit(\n",
        1,
    )
    return rewritten.replace(DISPATCH_OLD, DISPATCH_NEW, 1)


def load_candidate() -> types.ModuleType:
    name = "historical_exhibits_visa_candidate"
    module = types.ModuleType(name)
    module.__file__ = str(SOURCE)
    module.__package__ = ""
    sys.modules[name] = module
    exec(compile(patched_source(), str(SOURCE), "exec"), module.__dict__)
    return module

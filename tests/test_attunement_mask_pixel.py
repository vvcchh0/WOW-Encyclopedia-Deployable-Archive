"""Focused regression tests for the exact attunement map mask repair."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import export_github_pages as pages  # noqa: E402


BASE = "/WOW-Encyclopedia-Deployable-Archive/"
MISSING = (
    BASE
    + "__offline/missing-image.svg?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Fbcattunement%2F"
    + "&requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Fbcattunement%2Fimages%2Fpixel.gif"
    + "&reason=external-or-uncollected-resource"
)
OTHER_MISSING = MISSING.replace("bcattunement%2Fimages%2Fpixel.gif", "bcattunement%2Fimages%2Fchart.jpg")
PIXEL = BASE + "shared/wow-com/includes/images/pixel.gif"


class AttunementMaskPixelTests(unittest.TestCase):
    def test_only_real_map_pixel_placeholder_is_replaced_and_attributes_survive(self) -> None:
        source = f"""<!doctype html><html><body>
<style>
.coverDivStyle1 {{ width:120px; background:url("{MISSING}"); _background:url("{MISSING}"); }}
.coverDivStyle2 {{ width:100px; background:url("{MISSING}"); }}
.coverDivStyle1x {{ background:url("{MISSING}"); }}
</style>
<script>var literal = '<img id=\"mapPixel\" src=\"{MISSING}\">';</script>
<img id=\"otherPixel\" src=\"{MISSING}\" width=\"2\">
<img class=\"map\" id=\"mapPixel\" src=\"{MISSING}\" width=\"1226\" height=\"701\" border=\"0\" usemap=\"#attunement_mask_Map_1\" onmouseover=\"showTip(1)\" onclick=\"return false;\">
</body></html>"""

        derived, changed = pages.rewrite_attunement_mask_pixel(
            source,
            route="/bcattunement/index.html",
            base_path=BASE,
        )

        self.assertTrue(changed)
        self.assertEqual(derived.count(PIXEL), 3)
        self.assertIn(f'.coverDivStyle1 {{ width:120px; background:url("{PIXEL}"); _background:url("{MISSING}"); }}', derived)
        self.assertIn(f'.coverDivStyle2 {{ width:100px; background:url("{PIXEL}"); }}', derived)
        self.assertIn(f'.coverDivStyle1x {{ background:url("{MISSING}"); }}', derived)
        self.assertIn(f'id="otherPixel" src="{MISSING}"', derived)
        self.assertIn(f'''var literal = '<img id="mapPixel" src="{MISSING}">';''', derived)
        target_start = derived.index('<img class="map" id="mapPixel"')
        target_end = derived.index(">", target_start) + 1
        target = derived[target_start:target_end]
        self.assertIn(f'src="{PIXEL}"', target)
        for attribute in (
            'width="1226"',
            'height="701"',
            'border="0"',
            'usemap="#attunement_mask_Map_1"',
            'onmouseover="showTip(1)"',
            'onclick="return false;"',
        ):
            self.assertIn(attribute, target)

    def test_route_and_requested_path_guards_are_noops(self) -> None:
        ordinary = f'<img id="mapPixel" src="{OTHER_MISSING}" width="1226">'
        already_local = f'<img id="mapPixel" src="{PIXEL}" width="1226">'

        for route, source in (
            ("/other/index.html", ordinary),
            ("/bcattunement/index.html", ordinary),
            ("/bcattunement/index.html", already_local),
        ):
            derived, changed = pages.rewrite_attunement_mask_pixel(
                source,
                route=route,
                base_path=BASE,
            )
            self.assertFalse(changed)
            self.assertEqual(derived, source)


if __name__ == "__main__":
    unittest.main()

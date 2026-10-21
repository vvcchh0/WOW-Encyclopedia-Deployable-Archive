from __future__ import annotations

import sys
import unittest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import non_gallery_compat  # noqa: E402


class NonGalleryCompatibilityTests(unittest.TestCase):
    def test_downloads_repairs_only_measured_goblue6_anchor(self) -> None:
        source = """
<!-- <a onmouseout=\"document.goblue8.src=gobluedef.src\"><img name=\"goblue6\" id=\"goblue6\"></a> -->
<a href=\"/other\" onmouseover=\"document.goblue6.src=goblueroll.src\" onmouseout=\"document.goblue8.src=gobluedef.src\"><img name=\"goblue6\" id=\"goblue6\"></a>
<a href=\"/fan\" onmouseover=\"document.goblue5.src=goblueroll.src\" onmouseout=\"document.goblue5.src=gobluedef.src\"><img name=\"goblue5\" id=\"goblue5\"></a>
<a href=\"/cast\" onmouseover=\"document.goblue7.src=goblueroll.src\" onmouseout=\"document.goblue7.src=gobluedef.src\"><img name=\"goblue7\" id=\"goblue5\"></a>
"""
        rewritten, stats = non_gallery_compat.transform_html(source, route="downloads/index.html")
        self.assertEqual(stats["downloads_hover_fixes"], 1)
        self.assertIn('onmouseout="document.goblue6.src=gobluedef.src"', rewritten)
        self.assertIn('onmouseout="document.goblue5.src=gobluedef.src"', rewritten)
        self.assertIn('onmouseout="document.goblue7.src=gobluedef.src"', rewritten)
        self.assertIn('document.goblue8.src=gobluedef.src', rewritten.split("-->", 1)[0])

    def test_shared_menu_labels_add_aria_without_touching_toggle(self) -> None:
        source = "".join(
            f'<a class="header" id="{element_id}" onclick="toggleNewMenu(1)"><em>Game Guide</em></a>'
            for element_id in non_gallery_compat.MENU_LABELS
        )
        rewritten, stats = non_gallery_compat.transform_html(source, route="/info/index.html")
        self.assertEqual(stats["menu_label_count"], 8)
        self.assertEqual(stats["menu_aria_added"], 8)
        for element_id, label in non_gallery_compat.MENU_LABELS.items():
            self.assertIn(f'id="{element_id}"', rewritten)
            self.assertIn(f'<em>{label}</em>', rewritten)
            self.assertIn(f'aria-label="{label}"', rewritten)
        self.assertEqual(rewritten.count('onclick="toggleNewMenu(1)"'), 8)
        again, second_stats = non_gallery_compat.transform_html(rewritten, route="info/index.html")
        self.assertEqual(again, rewritten)
        self.assertFalse(second_stats["changed"])
        self.assertEqual(second_stats["menu_label_count"], 0)

    def test_comments_and_unrelated_route_are_preserved(self) -> None:
        comment = '<!-- <a id="menuNews-header"><em>Game Guide</em></a> -->'
        script = '<script>var fake = \'<a id="menuNews-header"><em>Game Guide</em></a>\';</script>'
        style = '<style>.fake{content:"<a id=\\"menuNews-header\\"><em>Game Guide</em></a>"}</style>'
        source = comment + script + style + '<a id="menuNews-header"><em>Game Guide</em></a>'
        rewritten, stats = non_gallery_compat.transform_html(source, route="info/index.html")
        self.assertTrue(stats["changed"])
        self.assertIn(comment, rewritten)
        self.assertIn(script, rewritten)
        self.assertIn(style, rewritten)
        self.assertIn('<a id="menuNews-header" aria-label="News"><em>News</em></a>', rewritten)
        unchanged, unrelated = non_gallery_compat.transform_html(source, route="/news/index.html")
        self.assertEqual(unchanged, rewritten)
        self.assertEqual(unrelated["menu_label_count"], 1)

    def test_query_routes_are_rejected(self) -> None:
        with self.assertRaises(non_gallery_compat.NonGalleryCompatError):
            non_gallery_compat.transform_html("<p>safe</p>", route="/downloads/index.html?x=1")
        with self.assertRaises(non_gallery_compat.NonGalleryCompatError):
            non_gallery_compat.transform_html("<p>safe</p>", route="/downloads/index.html#x")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import talent_compat  # noqa: E402


BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"

SOURCE15_FIXTURE_ROOT = ROOT / "tests/fixtures/talent_source15"
SOURCE15_FIXTURES = {
    talent_compat.LOCALIZE_ROUTE: SOURCE15_FIXTURE_ROOT / "localize.js",
    talent_compat.PRINTOUTTOP_ROUTE: SOURCE15_FIXTURE_ROOT / "printOutTop.js",
}
SOURCE15_SHA256 = {
    talent_compat.LOCALIZE_ROUTE: "e13769500cc7853b7c4d835f0380cf971cbec5f8fc061c3f1f83cf3dea1e6972",
    talent_compat.PRINTOUTTOP_ROUTE: "618c92c0d00c960f651aad4364a05e93cfb785df38b2b63902febaeb06d26f04",
}


class _Localizer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def __call__(self, raw: str, *, context: str) -> str:
        self.calls.append((raw, context))
        if raw == "/links/images/border-right.gif":
            return BASE_PATH + "__offline/missing-image.svg?source=talent-test&requested=border-right.gif"
        return BASE_PATH + raw.lstrip("/")


def _source(route: str) -> tuple[str, str]:
    path = SOURCE15_FIXTURES[route]
    data = path.read_bytes()
    source_sha = hashlib.sha256(data).hexdigest()
    if source_sha != SOURCE15_SHA256[route]:
        raise AssertionError(f"Source15 fixture SHA mismatch for {route}: {source_sha}")
    return data.decode("utf-8"), source_sha


def _node_check(text: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "talent.js"
        path.write_bytes(text.encode("utf-8"))
        return subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
        )


class TalentCompatibilityTests(unittest.TestCase):
    def test_localize_repairs_urls_without_breaking_css_escape_or_template(self) -> None:
        source, source_sha = _source(talent_compat.LOCALIZE_ROUTE)
        localizer = _Localizer()
        rewritten, handled, stats = talent_compat.rewrite_talent_script(
            source,
            talent_compat.LOCALIZE_ROUTE,
            source_sha,
            BASE_PATH,
            localizer,
        )

        self.assertTrue(handled)
        self.assertTrue(stats["changed"])
        self.assertEqual(stats["template_links_repaired"], 2)
        self.assertEqual(stats["img_path_prefix_replacements"], 1)
        self.assertEqual(stats["fixed_url_replacements"], 12)
        self.assertEqual(stats["fixed_url_context_counts"], {"image": 11, "css_url": 1})
        self.assertEqual(len(localizer.calls), 12)
        self.assertIn(("/links/images/border-right.gif", "css_url"), localizer.calls)

        self.assertIn(
            'background-image: url(\\\'/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?',
            rewritten,
        )
        self.assertIn(
            'var theURLtoCopy = "/WOW-Encyclopedia-Deployable-Archive/info/classes/"+ nlclass +"/talents.html";',
            rewritten,
        )
        self.assertIn(
            'w.document.write("/WOW-Encyclopedia-Deployable-Archive/info/classes/"+ nlclass +"/talents.html?" +templateString);',
            rewritten,
        )
        self.assertNotIn("/info/classes/index.html\"+ nlclass", rewritten)
        self.assertNotIn("__offline/missing.html", rewritten)
        self.assertIn("rankPointsMax - rankPoints", rewritten)

        checked = _node_check(rewritten)
        self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_printouttop_is_guarded_and_keeps_dynamic_background_expression(self) -> None:
        source, source_sha = _source(talent_compat.PRINTOUTTOP_ROUTE)
        rewritten, handled, stats = talent_compat.rewrite_talent_script(
            source,
            talent_compat.PRINTOUTTOP_ROUTE,
            source_sha,
            BASE_PATH,
            _Localizer(),
        )

        self.assertTrue(handled)
        self.assertEqual(rewritten, source)
        self.assertFalse(stats["changed"])
        self.assertEqual(stats["dynamic_background_expressions_preserved"], 1)
        self.assertIn(
            "imgPath +'/'+ nlclass +'/images/'+ imgDir + treeName +'/background.jpg",
            rewritten,
        )
        checked = _node_check(rewritten)
        self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_route_is_narrow_and_query_cannot_bypass_it(self) -> None:
        source, source_sha = _source(talent_compat.LOCALIZE_ROUTE)
        localizer = _Localizer()
        for route in ("/other.js", "shared/global/talents/includes/localize.js?x=1"):
            rewritten, handled, stats = talent_compat.rewrite_talent_script(
                source,
                route,
                "0" * 64,
                BASE_PATH,
                localizer,
            )
            self.assertFalse(handled)
            self.assertEqual(rewritten, source)
            self.assertFalse(stats["handled"])
        self.assertEqual(localizer.calls, [])

    def test_source_and_text_hash_guards_reject_drift(self) -> None:
        source, source_sha = _source(talent_compat.LOCALIZE_ROUTE)
        with self.assertRaisesRegex(talent_compat.TalentCompatError, "source SHA mismatch"):
            talent_compat.rewrite_talent_script(source, talent_compat.LOCALIZE_ROUTE, "0" * 64, BASE_PATH, _Localizer())
        with self.assertRaisesRegex(talent_compat.TalentCompatError, "text SHA mismatch"):
            talent_compat.rewrite_talent_script(source + "\n", talent_compat.LOCALIZE_ROUTE, source_sha, BASE_PATH, _Localizer())

    def test_js_string_scanner_does_not_rewrite_comments(self) -> None:
        calls: list[str] = []

        def callback(raw: str, *, context: str) -> str:
            calls.append(raw)
            return BASE_PATH + raw.lstrip("/")

        value = (
            '// "/links/images/border-right.gif"\n'
            'var value = "/links/images/border-right.gif"; /* "/links/images/border-right.gif" */\n'
        )
        stats: dict[str, object] = {}
        rewritten = talent_compat._rewrite_js_string_literals(value, callback=callback, stats=stats)
        self.assertIn('// "/links/images/border-right.gif"', rewritten)
        self.assertIn('var value = "/WOW-Encyclopedia-Deployable-Archive/links/images/border-right.gif";', rewritten)
        self.assertIn('/* "/links/images/border-right.gif" */', rewritten)
        self.assertEqual(calls, ["/links/images/border-right.gif"])

    def test_callback_cannot_inject_unescaped_markup(self) -> None:
        source, source_sha = _source(talent_compat.LOCALIZE_ROUTE)

        def unsafe(raw: str, *, context: str) -> str:
            return "/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?x='broken"

        with self.assertRaisesRegex(talent_compat.TalentCompatError, "unsafe JavaScript URL"):
            talent_compat.rewrite_talent_script(source, talent_compat.LOCALIZE_ROUTE, source_sha, BASE_PATH, unsafe)


if __name__ == "__main__":
    unittest.main()

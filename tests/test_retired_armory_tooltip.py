#!/usr/bin/env python3
"""Focused tests for the retired Armory item-details tooltip route."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TESTS = ROOT / "tests"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

import export_github_pages as pages  # noqa: E402
from test_github_pages_export import GithubPagesExportTests  # noqa: E402


SOURCE = ROOT / ".scratch/offline-navigation-20261015-v15/site/new-hp/js/enhancedtip.js"
ROUTE = "/new-hp/js/enhancedtip.js"


class RetiredArmoryTooltipTests(unittest.TestCase):
    def _source(self) -> str:
        return SOURCE.read_text(encoding="utf-8")

    def _node(self) -> Path | None:
        command = shutil.which("node")
        if command:
            return Path(command)
        bundled = Path(
            "C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/"
            "dependencies/node/bin/node.exe"
        )
        return bundled if bundled.is_file() else None

    def test_real_source_replaces_only_complete_request_function(self) -> None:
        source = self._source()
        rewritten, changed = pages.rewrite_retired_armory_tooltip(source, ROUTE)
        self.assertTrue(changed)
        self.assertIn(pages._RETIRED_ARMORY_TOOLTIP_MESSAGE, rewritten)
        self.assertNotIn("darkPortal.requestXml(thisID)", rewritten)
        self.assertNotIn('document.createElement("iframe")', rewritten)
        self.assertNotIn("document.domain = currentDomain", rewritten)
        self.assertIn("function enhancedXmlTTip(thisID)", rewritten)
        self.assertIn("showTip(document.getElementById(thisID).innerHTML);", rewritten)
        self.assertIn("function openPortal()", rewritten)

        changed_again, did_change_again = pages.rewrite_retired_armory_tooltip(rewritten, ROUTE)
        self.assertFalse(did_change_again)
        self.assertEqual(changed_again, rewritten)

        match = pages._RETIRED_ARMORY_REQUESTHTML_RE.search(source)
        rewritten_match = pages._RETIRED_ARMORY_REQUESTHTML_RE.search(rewritten)
        self.assertIsNotNone(match)
        self.assertIsNotNone(rewritten_match)
        assert match is not None
        assert rewritten_match is not None
        self.assertEqual(source[: match.start()], rewritten[: rewritten_match.start()])
        self.assertEqual(source[match.end() :], rewritten[rewritten_match.end() :])

    def test_route_scope_duplicate_and_changed_signature_guards(self) -> None:
        source = self._source()
        unchanged, changed = pages.rewrite_retired_armory_tooltip(source, "/other/script.js")
        self.assertFalse(changed)
        self.assertEqual(unchanged, source)

        function = pages._RETIRED_ARMORY_REQUESTHTML_RE.search(source)
        self.assertIsNotNone(function)
        assert function is not None
        with self.assertRaisesRegex(pages.PagesExportError, "expected one requestHTML"):
            pages.rewrite_retired_armory_tooltip(source + "\r\n" + function.group(0), ROUTE)

        altered = source.replace("document.domain = currentDomain;", "document.domain = otherDomain;", 1)
        with self.assertRaisesRegex(pages.PagesExportError, "missing guards"):
            pages.rewrite_retired_armory_tooltip(altered, ROUTE)

    def test_node_missing_request_is_static_and_cached_nodes_still_render(self) -> None:
        node = self._node()
        if node is None:
            self.skipTest("Node.js is unavailable for the tooltip VM regression")
        rewritten, changed = pages.rewrite_retired_armory_tooltip(self._source(), ROUTE)
        self.assertTrue(changed)
        driver = f"""
const vm = require("node:vm");
const code = {json.dumps(rewritten)};
const missingCalls = [];
const missingContext = {{
    showTip: function (value) {{ missingCalls.push(String(value)); }},
    fetch: function () {{ throw new Error("network must not be called"); }}
}};
vm.createContext(missingContext);
vm.runInContext(code, missingContext);
missingContext.requestHTML("missing-item");
const cachedCalls = [];
const cachedContext = {{
    showTip: function (value) {{ cachedCalls.push(String(value)); }},
    document: {{ getElementById: function (id) {{ return id === "cached-item" ? {{innerHTML: "<b>cached</b>"}} : null; }} }},
    fetch: function () {{ throw new Error("network must not be called"); }}
}};
vm.createContext(cachedContext);
vm.runInContext(code, cachedContext);
cachedContext.enhancedXmlTTip("cached-item");
process.stdout.write(JSON.stringify({{missingCalls, cachedCalls}}));
"""
        result = subprocess.run(
            [str(node), "-e", driver],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        observed = json.loads(result.stdout)
        self.assertEqual(observed["missingCalls"], [pages._RETIRED_ARMORY_TOOLTIP_MESSAGE])
        self.assertEqual(observed["cachedCalls"], ["<b>cached</b>"])

    def test_runtime_injection_ignores_pseudo_head_and_body_inside_script(self) -> None:
        script_body = (
            '\nconst pseudo = "<head data-fake=\\"1\\"><body data-fake=\\"1\\">";\n'
            '// <!-- <body class="comment-fake"> -->\n'
            'document.write("<body class=\\\'js-fake\\\'>");\n'
        )
        script_block = '<script id="legacy-script">' + script_body + "</script>"
        source = (
            '<!doctype html><!-- <head data-comment="1"><body data-comment="1"> -->\n'
            '<HTML><HEAD data-real="yes">\n'
            + script_block
            + '<TITLE>Story</TITLE></HEAD>\n'
            + '<BODY class="real">before\nafter</BODY></HTML>'
        )
        derived = pages.inject_html_runtime(
            source,
            base_path=pages.DEFAULT_BASE_PATH,
            source_sha="fixture-story",
        )

        self.assertEqual(derived.count("__offline-pages-banner"), 1)
        body = re.search(r'<body\s+class="real">', derived, flags=re.I)
        self.assertIsNotNone(body)
        assert body is not None
        banner = derived.index("__offline-pages-banner")
        script_start = derived.index(script_block)
        self.assertGreater(banner, body.end())
        self.assertGreater(banner, script_start)
        self.assertIn(
            pages.DEFAULT_BASE_PATH + "__offline/pages_runtime.js",
            derived,
        )
        head_start = derived.casefold().index("<head data-real=\"yes\">")
        runtime = derived.index("pages_runtime.js")
        self.assertGreater(runtime, head_start)
        self.assertLess(runtime, derived.casefold().index("</head>"))
        self.assertLess(runtime, script_start)
        self.assertEqual(derived.count(script_block), 1)

        node = self._node()
        if node is None:
            self.skipTest("Node.js is unavailable for the HTML script syntax regression")
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".js",
            delete=False,
        ) as handle:
            handle.write(script_body)
            script_path = Path(handle.name)
        try:
            result = subprocess.run(
                [str(node), "--check", str(script_path)],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
        finally:
            script_path.unlink(missing_ok=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_export_js_branch_records_derivation_stat_and_reason(self) -> None:
        source_bytes = SOURCE.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = GithubPagesExportTests()._fixture(Path(tmp))
            relative = Path("new-hp/js/enhancedtip.js")
            target = site / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source_bytes)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            route = "/" + relative.as_posix()
            payload["files"].append(
                {
                    "route": route,
                    "output_path": "offline/site/" + relative.as_posix(),
                    "derived_sha256": hashlib.sha256(source_bytes).hexdigest(),
                    "derived_length": len(source_bytes),
                    "mime": "application/javascript",
                    "kind": "js",
                    "role": "historical_armory_tooltip",
                    "source_base_url": "http://www.worldofwarcraft.com" + route,
                }
            )
            payload["origin_index"]["www.worldofwarcraft.com" + route] = route
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            self.assertEqual(result["stats"]["retired_armory_tooltip_repaired"], 1)
            derived_path = base / "pages" / relative
            derived = derived_path.read_text(encoding="utf-8")
            self.assertIn(pages._RETIRED_ARMORY_TOOLTIP_MESSAGE, derived)
            self.assertNotIn("darkPortal.requestXml(thisID)", derived)
            self.assertNotIn("document.domain = currentDomain", derived)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            record = next(item for item in provenance["files"] if item.get("route") == route)
            self.assertIn("retired Armory tooltip exhibit", record.get("derivation_reason", ""))
            self.assertEqual(target.read_bytes(), source_bytes)


if __name__ == "__main__":
    unittest.main()

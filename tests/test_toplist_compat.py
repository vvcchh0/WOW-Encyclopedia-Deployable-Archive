from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import export_github_pages as pages  # noqa: E402
import toplist_compat  # noqa: E402


# Keep the focused test independent of ignored historical worktrees.  These are
# byte-preserving Source15 fixtures; the provenance is recorded beside them.
SOURCE_SITE = ROOT / "tests/fixtures/toplist-source15"
PROTOTYPE_ROUTE = toplist_compat.TOPLIST_PROTOTYPE_ROUTE
LOGIC_ROUTE = toplist_compat.TOPLIST_LOGIC_ROUTE
PIXEL_LITERAL = 'src=\\"/toplist/images/pixel.gif\\"'


class _RecordingLocalizer:
    def __init__(
        self,
        value: str = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=fixture",
        route_to_static: dict[str, str] | None = None,
    ):
        self.value = value
        self.route_to_static = dict(route_to_static or {})
        self.calls: list[dict[str, str]] = []

    def localize(self, raw: str, *, base_url: str, context: str, recorder) -> str:
        self.calls.append({"raw": raw, "base_url": base_url, "context": context})
        return self.value


class ToplistCompatibilityTests(unittest.TestCase):
    def _source_path(self, route: str) -> Path:
        return SOURCE_SITE / Path(route).name

    def _source_text(self, route: str) -> str:
        return self._source_path(route).read_bytes().decode("utf-8")

    def _append_source_record(self, manifest: Path, route: str) -> None:
        source = self._source_path(route)
        data = source.read_bytes()
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["files"].append(
            {
                "route": route,
                "output_path": "offline/site/" + route.lstrip("/"),
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": "application/javascript",
                "kind": "js",
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            }
        )
        manifest.write_text(json.dumps(payload), encoding="utf-8")

    def test_actual_source15_assets_export_and_node_check(self) -> None:
        """The exporter branch handles both frozen files without generic rewrites."""

        with tempfile.TemporaryDirectory() as tmp:
            from test_github_pages_export import GithubPagesExportTests

            base, site, manifest = GithubPagesExportTests()._fixture(Path(tmp))
            for route in (PROTOTYPE_ROUTE, LOGIC_ROUTE):
                source = self._source_path(route)
                destination = site / route.lstrip("/")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
                self._append_source_record(manifest, route)

            output = base / "pages"
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=output,
                workspace_root=base,
                max_bytes=None,
                min_free_bytes=0,
            )
            self.assertGreaterEqual(result["stats"].get("toplist_compat_repaired", 0), 2)

            prototype_output = output / PROTOTYPE_ROUTE.lstrip("/")
            logic_output = output / LOGIC_ROUTE.lstrip("/")
            self.assertEqual(prototype_output.read_bytes().decode("utf-8"), self._source_text(PROTOTYPE_ROUTE))

            source_logic = self._source_text(LOGIC_ROUTE)
            derived_logic = logic_output.read_bytes().decode("utf-8")
            self.assertEqual(source_logic.count(PIXEL_LITERAL), 5)
            self.assertEqual(derived_logic.count(PIXEL_LITERAL), 0)
            urls = re.findall(r'src=\\"([^"\\]+)\\"', derived_logic)
            self.assertEqual(len(urls), 5)
            self.assertEqual(len(set(urls)), 1)
            self.assertTrue(urls[0].startswith("/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?"))
            replacement = 'src=\\"' + urls[0] + '\\"'
            self.assertEqual(derived_logic.count(replacement), 5)
            self.assertEqual(derived_logic.count("url(/toplist/images/table-left.jpg)"), 0)
            self.assertEqual(derived_logic.count("url(/toplist/images/table-right.jpg)"), 0)
            self.assertIn("var topListLocalDataRoutes = {};", derived_logic)
            self.assertIn(toplist_compat._LOGIC_HISTORICAL_EMPTY_LABEL, derived_logic)

            node = "node"
            for path in (prototype_output, logic_output):
                checked = subprocess.run(
                    [node, "--check", str(path)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=15,
                )
                self.assertEqual(checked.returncode, 0, checked.stderr)

            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            rows = {row["route"]: row for row in provenance["files"] if row["route"] in {PROTOTYPE_ROUTE, LOGIC_ROUTE}}
            self.assertIn("Toplist compatibility guard preserved", rows[PROTOTYPE_ROUTE].get("derivation_reason", ""))
            self.assertIn("exactly five escaped pixel", rows[LOGIC_ROUTE].get("derivation_reason", ""))

    def test_source_and_route_guards(self) -> None:
        prototype = self._source_text(PROTOTYPE_ROUTE)
        localizer = _RecordingLocalizer()
        rewritten, handled = toplist_compat.rewrite_toplist_script(
            prototype,
            PROTOTYPE_ROUTE,
            toplist_compat.TOPLIST_PROTOTYPE_SOURCE_SHA256,
            "http://www.worldofwarcraft.com" + PROTOTYPE_ROUTE,
            localizer,
            None,
        )
        self.assertTrue(handled)
        self.assertEqual(rewritten, prototype)
        self.assertEqual(localizer.calls, [])

        with self.assertRaisesRegex(toplist_compat.ToplistCompatError, "source SHA mismatch"):
            toplist_compat.rewrite_toplist_script(
                prototype,
                PROTOTYPE_ROUTE,
                "0" * 64,
                "http://www.worldofwarcraft.com" + PROTOTYPE_ROUTE,
                _RecordingLocalizer(),
                None,
            )
        with self.assertRaisesRegex(toplist_compat.ToplistCompatError, "text SHA mismatch"):
            toplist_compat.rewrite_toplist_script(
                prototype + "\n",
                PROTOTYPE_ROUTE,
                toplist_compat.TOPLIST_PROTOTYPE_SOURCE_SHA256,
                "http://www.worldofwarcraft.com" + PROTOTYPE_ROUTE,
                _RecordingLocalizer(),
                None,
            )

        unrelated, handled = toplist_compat.rewrite_toplist_script(
            "var value = '/toplist/images/pixel.gif';",
            "/other/script.js",
            "0" * 64,
            "http://www.worldofwarcraft.com/other/script.js",
            _RecordingLocalizer(),
            None,
        )
        self.assertFalse(handled)
        self.assertEqual(unrelated, "var value = '/toplist/images/pixel.gif';")

    def test_logic_count_guard_and_localizer_context(self) -> None:
        source = self._source_text(LOGIC_ROUTE)
        mutated = source.replace(PIXEL_LITERAL, "", 1)
        mutated_sha = hashlib.sha256(mutated.encode("utf-8")).hexdigest()
        localizer = _RecordingLocalizer()
        with mock.patch.object(toplist_compat, "TOPLIST_LOGIC_SOURCE_SHA256", mutated_sha):
            with self.assertRaisesRegex(toplist_compat.ToplistCompatError, "pixel literal count mismatch"):
                toplist_compat.rewrite_toplist_script(
                    mutated,
                    LOGIC_ROUTE,
                    mutated_sha,
                    "http://www.worldofwarcraft.com" + LOGIC_ROUTE,
                    localizer,
                    None,
                )
        self.assertEqual(localizer.calls, [])

        localizer = _RecordingLocalizer()
        rewritten, handled = toplist_compat.rewrite_toplist_script(
            source,
            LOGIC_ROUTE,
            toplist_compat.TOPLIST_LOGIC_SOURCE_SHA256,
            "http://www.worldofwarcraft.com" + LOGIC_ROUTE,
            localizer,
            None,
        )
        self.assertTrue(handled)
        self.assertEqual(len(localizer.calls), 7)
        self.assertEqual([call["raw"] for call in localizer.calls[:5]], ["/toplist/images/pixel.gif"] * 5)
        self.assertEqual([call["context"] for call in localizer.calls[:5]], ["image"] * 5)
        self.assertEqual(
            [call["raw"] for call in localizer.calls[5:]],
            ["/toplist/images/table-left.jpg", "/toplist/images/table-right.jpg"],
        )
        self.assertEqual([call["context"] for call in localizer.calls[5:]], ["css_url", "css_url"])
        self.assertEqual(rewritten.count(PIXEL_LITERAL), 0)
        self.assertEqual(rewritten.count('src=\\"/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=fixture\\"'), 5)
        self.assertIn(toplist_compat._LOGIC_HISTORICAL_EMPTY_LABEL, rewritten)

    def test_data_route_guard_runtime_and_historical_empty_label(self) -> None:
        source = self._source_text(LOGIC_ROUTE)
        local_route = "/WOW-Encyclopedia-Deployable-Archive/toplist/data/en/known_10052008.js"
        localizer = _RecordingLocalizer(
            route_to_static={"/toplist/data/en/known_10052008.js": local_route}
        )
        rewritten, handled = toplist_compat.rewrite_toplist_script(
            source,
            LOGIC_ROUTE,
            toplist_compat.TOPLIST_LOGIC_SOURCE_SHA256,
            "http://www.worldofwarcraft.com" + LOGIC_ROUTE,
            localizer,
            None,
        )
        self.assertTrue(handled)
        self.assertIn('var topListLocalDataRoutes = {"/toplist/data/en/known_10052008.js":"' + local_route + '"};', rewritten)
        self.assertIn(toplist_compat._LOGIC_HISTORICAL_EMPTY_LABEL, rewritten)

        start = rewritten.index("var dataDir =")
        end = rewritten.index("    document.spells =", start)
        snippet = rewritten[start:end]
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "toplist-data-guard.js"
            script.write_text(
                "const vm = require('vm');\n"
                "const state = {factory: 0, open: [], send: 0, removed: [], injected: []};\n"
                "const context = {\n"
                "  lang: 'en',\n"
                "  createXMLHttpRequest() { state.factory++; return {\n"
                "    open(method, url) { state.open.push({method, url}); },\n"
                "    send() { state.send++; }\n"
                "  }; },\n"
                "  removeTable(pos) { state.removed.push(pos); },\n"
                "  injectTable(id, pos) { state.injected.push({id, pos}); }\n"
                "};\n"
                "vm.runInNewContext(" + json.dumps(snippet) + ", context);\n"
                "context.createXMLHttpRequest = function() { state.factory++; return {\n"
                "  open(method, url) { state.open.push({method, url}); },\n"
                "  send() { state.send++; }\n"
                "}; };\n"
                "context.ajaxCall('killedby_10052008.js', 3);\n"
                "const unknown = {factory: state.factory, open: state.open.length, send: state.send, "
                "injected: state.injected.slice(), dataMissing: context.dataMissing};\n"
                "context.ajaxCall('known_10052008.js', 4);\n"
                "process.stdout.write(JSON.stringify({unknown, known: {factory: state.factory, open: state.open, send: state.send}}));\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["node", str(script)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=15,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        observed = json.loads(result.stdout)
        self.assertEqual(observed["unknown"]["factory"], 0)
        self.assertEqual(observed["unknown"]["open"], 0)
        self.assertEqual(observed["unknown"]["send"], 0)
        self.assertEqual(observed["unknown"]["injected"], [{"id": "10052008", "pos": 3}])
        self.assertIn("10052008", observed["unknown"]["dataMissing"])
        self.assertEqual(observed["known"]["factory"], 1)
        self.assertEqual(observed["known"]["send"], 1)
        self.assertEqual(observed["known"]["open"], [{"method": "GET", "url": local_route}])

    def test_table_asset_count_guard_rejects_source_drift(self) -> None:
        source = self._source_text(LOGIC_ROUTE)
        mutated = source.replace("url(/toplist/images/table-left.jpg)", "url(/toplist/images/table-left-drift.jpg)", 1)
        mutated_sha = hashlib.sha256(mutated.encode("utf-8")).hexdigest()
        with mock.patch.object(toplist_compat, "TOPLIST_LOGIC_SOURCE_SHA256", mutated_sha):
            with self.assertRaisesRegex(toplist_compat.ToplistCompatError, "table asset count mismatch"):
                toplist_compat.rewrite_toplist_script(
                    mutated,
                    LOGIC_ROUTE,
                    mutated_sha,
                    "http://www.worldofwarcraft.com" + LOGIC_ROUTE,
                    _RecordingLocalizer(),
                    None,
                )


if __name__ == "__main__":
    unittest.main()


"""Focused runtime tests for the historical popUpOmega image viewer."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import export_github_pages as pages  # noqa: E402


class PopupImageViewerTests(unittest.TestCase):
    def _node(self) -> Path | None:
        command = shutil.which("node")
        if command:
            return Path(command)
        bundled = Path(
            "C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/"
            "dependencies/node/bin/node.exe"
        )
        return bundled if bundled.is_file() else None

    def test_late_helper_maps_only_local_images_and_is_idempotent(self) -> None:
        node = self._node()
        if node is None:
            self.skipTest("Node.js is unavailable for the popup image runtime regression")

        base_path = pages.DEFAULT_BASE_PATH
        route_map = {
            "/legacy/story/collected.jpg": base_path + "legacy/story/collected.jpg",
            "/legacy/story/orig.png": base_path + "_origins/www.blizzard.com/legacy/story/orig.png",
        }
        runtime = pages.runtime_js(base_path, route_map)
        driver = f"""
const vm = require("node:vm");
const code = {json.dumps(runtime)};
const opened = [];
const fallback = [];
const window = {{
    location: {{
        origin: "https://pages.test",
        href: "https://pages.test{base_path}legacy/story.html",
        pathname: "{base_path}legacy/story.html",
        search: "",
        hash: ""
    }},
    Element: undefined,
    CSSStyleDeclaration: undefined,
    HTMLImageElement: undefined,
    open: function (url, target, features) {{
        opened.push({{url: String(url), target: String(target), features: String(features)}});
        return {{url: url}};
    }}
}};
const document = {{
    baseURI: window.location.href,
    write: function () {{}},
    writeln: function () {{}},
    addEventListener: function () {{}},
    querySelector: function () {{ return null; }},
    images: []
}};
const context = {{
    window: window,
    document: document,
    location: window.location,
    URL: URL,
    fetch: function () {{
        return Promise.resolve({{ok: true, json: function () {{ return Promise.resolve({{routes: {json.dumps(route_map)}}}); }}}});
    }},
    setTimeout: setTimeout,
    clearTimeout: clearTimeout,
    console: console
}};
vm.createContext(context);
vm.runInContext(code, context);
setTimeout(function () {{
    window.popUpOmega = function (value) {{
        fallback.push(String(value));
        return "legacy:" + String(value);
    }};
}}, 10);
setTimeout(function () {{
    const before = window.popUpOmega;
    const one = window.popUpOmega("story/collected.jpg");
    const two = window.popUpOmega("/legacy/story/orig.png?state=old#frame");
    const three = window.popUpOmega("unknown-frame.jpg");
    const four = window.popUpOmega("{base_path}__offline/missing-image.svg?source=fixture");
    const five = window.popUpOmega("https://cdn.example.invalid/remote.png");
    const six = window.popUpOmega("legacy/topic.html");
    const seven = window.popUpOmega("javascript:alert(1)");
    const after = window.popUpOmega;
    process.stdout.write(JSON.stringify({{
        opened: opened,
        fallback: fallback,
        sameWrapperAfterDuplicateInstall: before === after,
        marker: Boolean(after.__pagesPopupImageAdapter),
        results: [one, two, three, four, five, six, seven]
    }}));
}}, 400);
"""
        result = subprocess.run(
            [str(node), "-e", driver],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        observed = json.loads(result.stdout)
        self.assertTrue(observed["sameWrapperAfterDuplicateInstall"])
        self.assertTrue(observed["marker"])
        opened = observed["opened"]
        self.assertEqual(len(opened), 5)
        self.assertEqual(opened[0]["url"], base_path + "legacy/story/collected.jpg")
        self.assertEqual(opened[1]["target"], "_blank")
        self.assertEqual(opened[1]["features"], "noopener,noreferrer")
        self.assertIn(base_path + "_origins/www.blizzard.com/legacy/story/orig.png", opened[1]["url"])
        self.assertTrue(
            all(
                item["url"].startswith(base_path)
                or item["url"].startswith("https://pages.test" + base_path)
                for item in opened
            )
        )
        self.assertNotIn("https://cdn.example.invalid/remote.png", [item["url"] for item in opened])
        self.assertIn(base_path + "__offline/missing-image.svg?", opened[2]["url"])
        self.assertIn(base_path + "__offline/missing-image.svg?", opened[3]["url"])
        self.assertIn(base_path + "__offline/missing-image.svg?", opened[4]["url"])
        self.assertEqual(observed["fallback"], ["legacy/topic.html", "javascript:alert(1)"])
        self.assertEqual(observed["results"][5], "legacy:legacy/topic.html")
        self.assertEqual(observed["results"][6], "legacy:javascript:alert(1)")

    def test_runtime_source_keeps_wrapper_scope_and_fallback_contract(self) -> None:
        runtime = pages.runtime_js(pages.DEFAULT_BASE_PATH, {})
        self.assertEqual(runtime.count("function installPopupImageAdapter()"), 1)
        self.assertEqual(runtime.count("window.open("), 1)
        self.assertNotIn("installPopupImageAdapter: installPopupImageAdapter", runtime)
        self.assertIn('window.open(mapped, "_blank", "noopener,noreferrer")', runtime)
        self.assertIn("return original.apply(this, arguments);", runtime)
        self.assertIn("setTimeout(installPopupImageAdapter, 1000);", runtime)
        self.assertNotIn("window.open(raw", runtime)
        self.assertNotIn("window.open(value", runtime)


if __name__ == "__main__":
    unittest.main()

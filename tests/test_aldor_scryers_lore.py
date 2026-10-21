from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import aldor_scryers_lore  # noqa: E402


class AldorScryersLoreTests(unittest.TestCase):
    def _fixture(self, root: Path) -> dict[str, object]:
        site = root / "site"
        script_dir = site / "info" / "basics" / "factions" / "aldorscryers" / "scripts"
        script_dir.mkdir(parents=True)
        token_text = (
            "// A comment containing loreTexts[\"alliance\"] = \"ignored\";\n"
            "loreTexts[\"alliance\"] = \"<h3>The Aldor</h3>Shattrath says \\\"light\\\".<br /><br />\\\n"
            "More Aldor text\";\n"
            "loreTexts[\"horde\"] = \"<h3>The Scryers</h3>Scryer text.<br /><br />\\\n"
            "More Scryer text\";\n"
            "function RewardItem() { return 1; }\n"
        ).encode("utf-8")
        main_bytes = b"var loreTexts = new Object(); var RewardItems = [];\n"
        page_bytes = b'<html><body><div id="loreText"></div></body></html>\n'
        paths = {
            "tokens": script_dir / "rewards-aldor-scryers-tokens.js",
            "main": script_dir / "rewards-aldor-scryers.js",
            "page": site / "info" / "basics" / "factions" / "aldorscryers" / "aldor-scryers.xml",
        }
        paths["page"].parent.mkdir(parents=True, exist_ok=True)
        paths["tokens"].write_bytes(token_text)
        paths["main"].write_bytes(main_bytes)
        paths["page"].write_bytes(page_bytes)

        def record(route: str, path: Path, kind: str, timestamp: str) -> dict[str, object]:
            data = path.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            return {
                "route": route,
                "output_path": path.relative_to(root).as_posix(),
                "source_sha256": sha,
                "source_length": len(data),
                "derived_sha256": sha,
                "derived_length": len(data),
                "mime": "application/x-javascript" if kind == "js" else "text/html",
                "kind": kind,
                "role": "fixture",
                "actual_timestamp": timestamp,
            }

        manifest: dict[str, object] = {
            "schema_version": 1,
            "site_root": "site",
            "source16": {"network_requests": 0},
            "files": [
                record(aldor_scryers_lore.PAGE_ROUTE, paths["page"], "html", "20080402033105"),
                record(aldor_scryers_lore.MAIN_ROUTE, paths["main"], "js", "20080402011507"),
                record(aldor_scryers_lore.TOKENS_ROUTE, paths["tokens"], "js", "20080402014948"),
            ],
        }
        manifest_path = root / "build-manifest.json"
        manifest_path.write_bytes(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        return {
            "root": root,
            "site": site,
            "manifest_path": manifest_path,
            "manifest": manifest,
            "manifest_sha": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "token_sha": hashlib.sha256(token_text).hexdigest(),
            "token_length": len(token_text),
            "main_sha": hashlib.sha256(main_bytes).hexdigest(),
            "main_length": len(main_bytes),
            "paths": paths,
        }

    def _load(self, fixture: dict[str, object]):
        with mock.patch.multiple(
            aldor_scryers_lore,
            EXPECTED_MANIFEST_SHA256=fixture["manifest_sha"],
            TOKENS_SHA256=fixture["token_sha"],
            TOKENS_LENGTH=fixture["token_length"],
            MAIN_SHA256=fixture["main_sha"],
            MAIN_LENGTH=fixture["main_length"],
        ):
            return aldor_scryers_lore.load_lore_bundle(
                fixture["root"],
                fixture["site"],
                fixture["manifest_path"],
                fixture["manifest"],
            )

    def test_fixture_extracts_only_lore_and_preserves_source_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            before = {name: path.read_bytes() for name, path in fixture["paths"].items()}
            bundle = self._load(fixture)
            helper = bundle.generated_file.data.decode("utf-8")
            self.assertEqual(bundle.expected_page_route, aldor_scryers_lore.PAGE_ROUTE)
            self.assertEqual(bundle.generated_file.relative, "__offline/aldor-scryers-lore.js")
            self.assertEqual(bundle.generated_file.mime, "application/javascript")
            self.assertIn("<h3>The Aldor</h3>Shattrath says \\\"light\\\".", helper)
            self.assertIn("<h3>The Scryers</h3>Scryer text.", helper)
            self.assertNotIn("RewardItem", helper)
            self.assertNotIn("RewardItems", helper)
            self.assertFalse((fixture["root"] / "__offline" / "aldor-scryers-lore.js").exists())
            self.assertEqual(before, {name: path.read_bytes() for name, path in fixture["paths"].items()})
            self.assertEqual(bundle.source_metadata["classification"], "source16_text_reuse")
            self.assertEqual(bundle.source_metadata["lore_keys"], ["alliance", "horde"])

    def test_helper_only_fills_missing_values_and_empty_lore_node(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            helper = self._load(fixture).generated_file.data.decode("utf-8")
            alliance_guard = 'if (typeof target.alliance === "undefined" || target.alliance === null || target.alliance === "")'
            horde_guard = 'if (typeof target.horde === "undefined" || target.horde === null || target.horde === "")'
            self.assertIn(alliance_guard, helper)
            self.assertIn(horde_guard, helper)
            self.assertIn('if (current && current !== "undefined" && current !== "null") return;', helper)
            self.assertIn('document.getElementById("hordeRewards")', helper)
            self.assertNotIn("switchClick =", helper)

    def test_parser_ignores_comments_and_strings_but_rejects_duplicate_assignment(self) -> None:
        sample = (
            '// loreTexts["alliance"] = "ignored";\n'
            'var fake = "loreTexts[\\"horde\\"] = \\"ignored\\";";\n'
            'loreTexts["alliance"] = "<h3>The Aldor</h3>A";\n'
            '/* loreTexts["horde"] = "ignored"; */\n'
            'loreTexts["horde"] = "<h3>The Scryers</h3>H";\n'
        )
        values = aldor_scryers_lore._extract_lore_assignments(sample)
        self.assertEqual(values["alliance"], "<h3>The Aldor</h3>A")
        self.assertEqual(values["horde"], "<h3>The Scryers</h3>H")
        with self.assertRaisesRegex(aldor_scryers_lore.AldorScryersLoreError, "duplicate"):
            aldor_scryers_lore._extract_lore_assignments(sample + 'loreTexts["alliance"] = "again";')

    def test_source_drift_and_manifest_binding_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            token_path = fixture["paths"]["tokens"]
            token_path.write_bytes(token_path.read_bytes() + b"\n")
            with self.assertRaisesRegex(aldor_scryers_lore.AldorScryersLoreError, "derived bytes mismatch"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            altered = dict(fixture["manifest"])
            altered["source16"] = {"network_requests": 1}
            with self.assertRaisesRegex(aldor_scryers_lore.AldorScryersLoreError, "does not match"):
                with mock.patch.multiple(
                    aldor_scryers_lore,
                    EXPECTED_MANIFEST_SHA256=fixture["manifest_sha"],
                    TOKENS_SHA256=fixture["token_sha"],
                    TOKENS_LENGTH=fixture["token_length"],
                    MAIN_SHA256=fixture["main_sha"],
                    MAIN_LENGTH=fixture["main_length"],
                ):
                    aldor_scryers_lore.load_lore_bundle(
                        fixture["root"], fixture["site"], fixture["manifest_path"], altered
                    )


if __name__ == "__main__":
    unittest.main()

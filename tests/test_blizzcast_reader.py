"""Self-contained contract tests for the BlizzCast reader.

These tests use a tiny synthetic five-source fixture. The accepted real
payloads and their 50 transcript blocks are checked separately by
integration/blizzcast-reader/actual_source_checks.py.
"""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from tools import blizzcast_reader


XHTML = "http://www.w3.org/1999/xhtml"
EXPECTED_URLS = {
    "BC01": "http://us.blizzard.com/blizzcast/_content/en-US/rss.xml",
    "BC02": "http://us.blizzard.com/blizzcast/archive/episode1.xml",
    "BC03": "http://us.blizzard.com/blizzcast/archive/episode2.xml",
    "BC04": "http://us.blizzard.com/blizzcast/archive.xml",
    "BC05": "http://us.blizzard.com/blizzcast/index.xml",
}


def _xhtml(body: str, title: str) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>'
        + title
        + "</title><style>ignored { color: red; }</style></head><body>"
        + body
        + "</body></html>"
    )


def _fixture_payloads() -> dict[str, tuple[str, str, str, int, int]]:
    rss = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel>
  <title>Fixture BlizzCast &amp; feed</title>
  <description>Captured &lt;reading&gt; feed</description>
  <item><title>Episode 1</title><pubDate>Wed, 09 Jan 2008 00:00:00 GMT</pubDate>
    <description>Read &lt;captured&gt; text</description>
    <link>http://us.blizzard.com/blizzcast/archive/episode1.xml</link>
    <enclosure url="http://us.media.blizzard.com/blizzcast/episode1.mp3" type="audio/mpeg" />
  </item>
  <item><title>Episode 2</title><pubDate>Thu, 10 Jan 2008 00:00:00 GMT</pubDate>
    <description>Second fixture entry</description>
    <link>http://us.blizzard.com/blizzcast/archive/episode2.xml</link>
    <enclosure url="http://us.media.blizzard.com/blizzcast/episode2.mp3" type="audio/mpeg" />
  </item>
</channel></rss>
"""
    episode1 = _xhtml(
        """
<script>alert('removed')</script><form><input name="secret" /></form>
<div class="trans"><div class="int"><span class="highlight">Fixture Speaker:</span>
  <p class="block">Hello &amp; &lt;fixture&gt; text <a href="javascript:seek('00:01')">time</a>
  <img src="http://example.invalid/episode1.png" alt="unrestored" />
  <audio><source src="http://example.invalid/episode1.mp3" /></audio></p>
  <span class="timecode"><span>[</span> 00:01 <span>]</span></span>
</div></div>
""",
        "Fixture Episode 1",
    )
    episode2 = _xhtml(
        """
<div class="trans"><div class="int"><span class="highlight">Second Speaker:</span>
  <p class="block">Second &lt;episode&gt; text <a href="http://example.invalid/outside">outside</a></p>
  <span class="timecode">[ 00:02 ]</span>
</div></div>
""",
        "Fixture Episode 2",
    )
    archive = _xhtml(
        '<div id="archive"><p>Archive <a href="http://us.blizzard.com/blizzcast/archive/episode1.xml">Episode 1</a></p></div>',
        "Fixture Archive",
    )
    index = _xhtml(
        '<div class="lcol"><p>Overview <a href="http://example.invalid/feedback">feedback</a></p></div>'
        '<div class="rcol"><p>Current <a href="http://us.blizzard.com/blizzcast/archive/episode2.xml">Episode 2</a></p></div>',
        "Fixture Index",
    )
    return {
        "BC01": (EXPECTED_URLS["BC01"], rss, "20080109120000", 0, 2),
        "BC02": (EXPECTED_URLS["BC02"], episode1, "20080109120100", 1, 0),
        "BC03": (EXPECTED_URLS["BC03"], episode2, "20080109120200", 1, 0),
        "BC04": (EXPECTED_URLS["BC04"], archive, "20080515224116", 0, 0),
        "BC05": (EXPECTED_URLS["BC05"], index, "20080515210412", 0, 0),
    }


def _build_fixture(root: Path) -> Path:
    source_dir = root / "sources"
    source_dir.mkdir()
    records: list[dict[str, object]] = []
    acceptance_entities: list[dict[str, object]] = []
    for entity_id in ("BC01", "BC02", "BC03", "BC04", "BC05"):
        url, text, timestamp, transcript_blocks, rss_items = _fixture_payloads()[entity_id]
        payload = source_dir / f"{entity_id}.xml"
        raw = text.encode("utf-8")
        payload.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        records.append({
            "entity_id": entity_id,
            "original_url": url,
            "actual_capture_timestamp": timestamp,
            "temporal_relation": "after_20080512_reference_window" if entity_id in {"BC04", "BC05"} else "before_20080512_reference_window",
            "mime": "text/xml" if entity_id == "BC01" else "application/xhtml+xml",
            "payload_path": f"sources/{entity_id}.xml",
            "sha256": digest,
            "length": len(raw),
            "sha1_base32": f"FIXTURE-{entity_id}",
            "title": f"Fixture {entity_id}",
            "xml_root": "rss" if entity_id == "BC01" else "{http://www.w3.org/1999/xhtml}html",
            "xml_nodes": 0,
            "transcript_blocks": transcript_blocks,
            "rss_items": rss_items,
        })
        acceptance_entities.append(copy.deepcopy(records[-1]))

    # This fixture covers two tiny transcript blocks. Actual historical
    # source coverage (19 + 31 blocks) is checked by the integration audit.
    acceptance = {
        "schema": "wow-blizzcast-source-acceptance/v1",
        "accepted": True,
        "actual_transcript_blocks": sum(item["transcript_blocks"] for item in records),
        "fixture_note": "minimal self-contained contract fixture; real 50-block validation is integration-only",
        "entities": acceptance_entities,
    }
    acceptance_path = root / "acceptance.json"
    acceptance_path.write_text(json.dumps(acceptance, indent=2) + "\n", encoding="utf-8")
    source_map = {
        "schema": "wow-blizzcast-reader-input/v1",
        "accepted": True,
        "source_acceptance": "acceptance.json",
        "source_acceptance_sha256": hashlib.sha256(acceptance_path.read_bytes()).hexdigest(),
        "records": records,
    }
    map_path = root / "input-map.json"
    map_path.write_text(json.dumps(source_map, indent=2) + "\n", encoding="utf-8")
    return map_path


class BlizzcastReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.fixture_root = Path(self.temp_dir.name)
        self.map_path = _build_fixture(self.fixture_root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def load(self, base_path: str = "") -> blizzcast_reader.BlizzcastBundle:
        return blizzcast_reader.load_blizzcast_bundle(self.map_path, self.fixture_root, base_path)

    def pages(self, bundle: blizzcast_reader.BlizzcastBundle) -> dict[str, dict[str, object]]:
        return {item["path"]: item for item in bundle.generated_files if item["mime"] == "application/xhtml+xml"}

    def test_fixed_routes_and_source_alias_scope(self) -> None:
        bundle = self.load("/WOW-Encyclopedia-Deployable-Archive")
        self.assertEqual(
            [item["path"] for item in bundle.generated_files],
            [
                "/__offline/related-sites/blizzcast/index.html",
                "/__offline/related-sites/blizzcast/archive.html",
                "/__offline/related-sites/blizzcast/episode1.html",
                "/__offline/related-sites/blizzcast/episode2.html",
                "/__offline/related-sites/blizzcast/feed.html",
                "/__offline/related-sites/blizzcast/reader.css",
            ],
        )
        self.assertEqual(bundle.base_path, "/WOW-Encyclopedia-Deployable-Archive/")
        self.assertEqual(len(bundle.origin_routes), 7)
        self.assertEqual(
            bundle.origin_routes["http://us.blizzard.com/blizzcast"],
            "/__offline/related-sites/blizzcast/index.html",
        )
        self.assertEqual(
            bundle.origin_routes["http://us.blizzard.com/blizzcast/"],
            "/__offline/related-sites/blizzcast/index.html",
        )
        self.assertNotIn("http://us.blizzard.com/blizzcast/archive", bundle.origin_routes)

    def test_generated_xhtml_is_namespaced_and_non_executable(self) -> None:
        bundle = self.load()
        pages = self.pages(bundle)
        self.assertEqual(len(pages), 5)
        for item in pages.values():
            data = item["data"]
            root = ET.fromstring(data.encode("utf-8"))
            self.assertEqual(root.tag, f"{{{XHTML}}}html")
            lowered = data.casefold()
            for forbidden in ("<script", "<form", "<input", "<iframe", "<object", "<embed", "javascript:", " style="):
                self.assertNotIn(forbidden, lowered)
            for forbidden_media in ("<img", "<audio", "<video"):
                self.assertNotIn(forbidden_media, lowered)
            self.assertNotRegex(data, r"<a\b[^>]*?/>")
            self.assertIn("/__offline/related-sites/blizzcast/reader.css", data)
        self.assertIn('class="nav-separator">·</span>', pages["/__offline/related-sites/blizzcast/episode1.html"]["data"])
        css = next(item for item in bundle.generated_files if item["path"].endswith("reader.css"))
        self.assertNotIn("http://", css["data"])
        self.assertIn("main a { margin-inline-end", css["data"])

    def test_fixture_transcript_blocks_and_timecodes_survive(self) -> None:
        bundle = self.load()
        pages = self.pages(bundle)
        episode1 = pages["/__offline/related-sites/blizzcast/episode1.html"]["data"]
        episode2 = pages["/__offline/related-sites/blizzcast/episode2.html"]["data"]
        self.assertEqual(episode1.count('class="transcript-block"'), 1)
        self.assertEqual(episode2.count('class="transcript-block"'), 1)
        self.assertIn("Fixture Speaker:", episode1)
        self.assertIn("[ 00:01 ]", episode1)
        self.assertIn("Second Speaker:", episode2)
        self.assertIn("[ 00:02 ]", episode2)
        self.assertNotIn('<a id="time-', episode1)

    def test_late_pages_navigation_and_rss_text_entries(self) -> None:
        bundle = self.load()
        pages = self.pages(bundle)
        for route in ("/__offline/related-sites/blizzcast/index.html", "/__offline/related-sites/blizzcast/archive.html"):
            self.assertIn("Late supplement", pages[route]["data"])
            self.assertIn("Archive home", pages[route]["data"])
            self.assertIn("BlizzCast index", pages[route]["data"])
        feed = pages["/__offline/related-sites/blizzcast/feed.html"]["data"]
        self.assertEqual(feed.count('class="feed-entry"'), 2)
        self.assertIn("Episode 1", feed)
        self.assertIn("Episode 2", feed)
        self.assertEqual(feed.count("Audio not restored offline"), 2)

    def test_dependency_inventory_is_structured_and_localized(self) -> None:
        bundle = self.load("/WOW-Encyclopedia-Deployable-Archive")
        self.assertGreater(len(bundle.dependency_inventory), 0)
        self.assertTrue(any(item["kind"] == "image" for item in bundle.dependency_inventory))
        audio = [item for item in bundle.dependency_inventory if item["kind"] == "audio"]
        self.assertTrue(any("episode2.mp3" in item["requested_url"] for item in audio))
        self.assertTrue(all(item["missing_route"].startswith("/WOW-Encyclopedia-Deployable-Archive/") for item in audio if not item["restored"]))
        self.assertTrue(any(item["restored"] and item["local_route"].endswith("episode1.html") for item in bundle.dependency_inventory))
        self.assertEqual(sum(int(item.get("transcript_blocks", 0)) for item in bundle.source_records), 2)
        self.assertEqual(bundle.estimated_bytes, sum(item["bytes"] for item in bundle.generated_files))

    def test_hash_and_path_mismatch_are_rejected(self) -> None:
        original = json.loads(self.map_path.read_text(encoding="utf-8"))
        bad_hash = copy.deepcopy(original)
        bad_hash["records"][0]["sha256"] = "0" * 64
        bad_hash_path = self.fixture_root / "bad-hash-map.json"
        bad_hash_path.write_text(json.dumps(bad_hash), encoding="utf-8")
        with self.assertRaises(blizzcast_reader.BlizzcastReaderError):
            self.load_map(bad_hash_path)
        bad_path = copy.deepcopy(original)
        bad_path["records"][0]["payload_path"] = "../outside.xml"
        bad_path_file = self.fixture_root / "bad-path-map.json"
        bad_path_file.write_text(json.dumps(bad_path), encoding="utf-8")
        with self.assertRaises(blizzcast_reader.BlizzcastReaderError):
            self.load_map(bad_path_file)

    def load_map(self, path: Path) -> blizzcast_reader.BlizzcastBundle:
        return blizzcast_reader.load_blizzcast_bundle(path, self.fixture_root)

    def test_entity_markup_is_rejected_without_dtd_loading(self) -> None:
        xml_path = self.fixture_root / "entity.xml"
        xml_path.write_text("<!DOCTYPE html [<!ENTITY x 'bad'>]><html/>", encoding="utf-8")
        with self.assertRaises(blizzcast_reader.BlizzcastReaderError):
            blizzcast_reader._parse_xml(xml_path)

    def test_only_reviewed_blizzard_origins_can_share_a_reader_route(self) -> None:
        origins = self.load().origin_routes
        path = "/blizzcast/archive/episode1.xml"
        expected = blizzcast_reader.ROUTES_BY_ENTITY["BC02"]
        for prefix in ("http://us.blizzard.com", "https://www.blizzard.com", "https://us.blizzard.com:443"):
            self.assertEqual(blizzcast_reader._route_for_url(prefix + path, origins), expected)
        for url in (
            "https://example.invalid" + path, "https://us.blizzard.com:444" + path,
            "https://name@us.blizzard.com" + path, "https://us.blizzard.com" + path + "?login=1",
            "https://us.blizzard.com" + path + "#unknown", "https://us.blizzard.com:bad" + path,
        ):
            self.assertIsNone(blizzcast_reader._route_for_url(url, origins), url)

    def test_captured_date_cannot_be_changed_without_source_acceptance(self) -> None:
        source_map = json.loads(self.map_path.read_text(encoding="utf-8"))
        source_map["records"][4]["actual_capture_timestamp"] = "20080512120000"
        changed = self.fixture_root / "wrong-date.json"
        changed.write_text(json.dumps(source_map), encoding="utf-8")
        with self.assertRaisesRegex(blizzcast_reader.BlizzcastReaderError, "actual_capture_timestamp"):
            self.load_map(changed)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from tools import blizzcast_audio, blizzcast_reader, export_github_pages


XHTML = blizzcast_reader.XHTML_NS
SOURCE_URLS = {
    "episode1": "http://us.media.blizzard.com/blizzcast/blizzcast_episode1.mp3",
    "episode2": "http://us.media.blizzard.com/blizzcast/blizzcast_episode2.mp3",
}
BASE = "/project/"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _build_fixture(root: Path) -> tuple[Path, Path, Path]:
    rss_path = root / "rss.xml"
    rss = (
        '<rss><channel><item><enclosure url="' + SOURCE_URLS["episode2"] + '" length="22" type="audio/mpeg" />'
        '</item><item><enclosure url="' + SOURCE_URLS["episode1"] + '" length="17" type="audio/mpeg" />'
        '</item></channel></rss>'
    ).encode()
    rss_path.write_bytes(rss)
    acceptance_path = root / "reader-acceptance.json"
    acceptance = {"accepted": True, "fixture": True}
    acceptance_path.write_text(json.dumps(acceptance), encoding="utf-8")
    reader_map_path = root / "reader-map.json"
    reader_map = {
        "schema": "wow-blizzcast-reader-input/v1",
        "accepted": True,
        "source_acceptance": "reader-acceptance.json",
        "source_acceptance_sha256": _sha(acceptance_path.read_bytes()),
        "records": [
            {"entity_id": "BC01", "original_url": "http://us.blizzard.com/blizzcast/_content/en-US/rss.xml", "payload_path": "rss.xml", "sha256": _sha(rss), "length": len(rss)},
            {"entity_id": "BC02"}, {"entity_id": "BC03"}, {"entity_id": "BC04"}, {"entity_id": "BC05"},
        ],
    }
    reader_map_path.write_text(json.dumps(reader_map), encoding="utf-8")
    audio_accept_path = root / "audio-acceptance.json"
    bodies = {
        "episode1": b"ID3fixture-episode-one",
        "episode2": b"ID3fixture-episode-two-longer",
    }
    accepted_records = []
    for episode_id, body in bodies.items():
        accepted_records.append({
            "id": episode_id,
            "url": SOURCE_URLS[episode_id],
            "bytes": len(body),
            "sha256": _sha(body),
            "rss_length": 17 if episode_id == "episode1" else 22,
            "classification": "current_origin_audio_copy",
            "eligible_for_derived_player": True,
            "historical_byte_identity": "unknown; RSS has no MP3 hash",
        })
    audio_acceptance = {
        "schema": "wow-root-blizzcast-current-origin-audio-acceptance/v1",
        "accepted_as_current_origin_audio": True,
        "accepted_as_2008_byte_identical": False,
        "original_bytes_unchanged": True,
        "records": accepted_records,
    }
    audio_accept_path.write_text(json.dumps(audio_acceptance), encoding="utf-8")
    zip_path = root / "source-payloads.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as archive:
        for episode_id in ("episode1", "episode2"):
            archive.writestr(f"__offline/related-sites/blizzcast/audio/{episode_id}.mp3", bodies[episode_id])
    records = []
    for episode_id in ("episode1", "episode2"):
        body = bodies[episode_id]
        route = f"/__offline/related-sites/blizzcast/audio/{episode_id}.mp3"
        records.append({
            "id": episode_id,
            "original_url": SOURCE_URLS[episode_id],
            "canonical_path": route,
            "payload_zip_member": route.lstrip("/"),
            "mime": "audio/mpeg",
            "bytes": len(body),
            "sha256": _sha(body),
            "rss_enclosure_length": 17 if episode_id == "episode1" else 22,
            "current_origin_length_delta_bytes": len(body) - (17 if episode_id == "episode1" else 22),
            "classification": "current_origin_audio_copy",
            "historical_byte_identity": "unknown; the accepted 2008 RSS has no MP3 digest",
        })
    audio_map = {
        "schema": "wow-blizzcast-current-origin-audio-input/v1",
        "accepted": True,
        "source_acquired_date": "2026-10-24",
        "classification": "current_origin_audio_copy",
        "historical_byte_identity": "unknown; no original MP3 digest is present in the 2008 RSS",
        "blizzcast_source_map": "reader-map.json",
        "blizzcast_source_map_sha256": _sha(reader_map_path.read_bytes()),
        "blizzcast_source_acceptance_sha256": reader_map["source_acceptance_sha256"],
        "blizzcast_rss_sha256": _sha(rss),
        "current_origin_acceptance": "audio-acceptance.json",
        "current_origin_acceptance_sha256": _sha(audio_accept_path.read_bytes()),
        "payload_zip": "source-payloads.zip",
        "payload_zip_sha256": _sha(zip_path.read_bytes()),
        "payload_zip_bytes": zip_path.stat().st_size,
        "records": records,
    }
    audio_map_path = root / "audio-map.json"
    audio_map_path.write_text(json.dumps(audio_map, indent=2), encoding="utf-8")
    return reader_map_path, audio_map_path, zip_path


def _reader_fixture() -> blizzcast_reader.BlizzcastBundle:
    pages = []
    for entity_id in blizzcast_reader.EXPECTED_IDS:
        route = blizzcast_reader.ROUTES_BY_ENTITY[entity_id]
        body = '<h1>Fixture heading</h1><p class="unrestored-notice">Images, audio, and interactive media are not restored in this offline reading view. <a href="/missing">Open a local missing-resource note</a></p>'
        if entity_id == "BC01":
            body = (
                '<p>This RSS capture is converted into two text entries. Audio files are referenced in the dependency inventory but are not restored here.</p>'
                '<article class="feed-entry"><h2>Episode 2</h2><p class="unrestored-notice">Audio not restored offline.</p></article>'
                '<article class="feed-entry"><h2>Episode 1</h2><p class="unrestored-notice">Audio not restored offline.</p></article>'
            )
        if entity_id in {"BC02", "BC03"}:
            body += '<div id="transcript"><p class="transcript-paragraph">Speaker: [ 00:01 ] Transcript &amp; exact.</p></div>'
        text = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<html xmlns="{XHTML}"><head><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'self\'; base-uri \'none\'; form-action \'none\'" /></head>'
            f'<body><main id="reader-content">{body}</main><footer>Historical reading edition. Original images and audio remain to be recovered.</footer></body></html>\n'
        )
        pages.append({"path": route, "data": text, "mime": "application/xhtml+xml", "bytes": len(text.encode()), "curated_sources": []})
    css = {"path": blizzcast_reader.CSS_ROUTE, "data": "body {}\n", "mime": "text/css", "bytes": 9, "curated_sources": []}
    audio_inventory = []
    for episode_id in ("episode2", "episode1"):
        audio_inventory.append({
            "source_entity_id": "BC01", "page_route": blizzcast_reader.ROUTES_BY_ENTITY["BC01"],
            "kind": "audio", "requested_url": SOURCE_URLS[episode_id], "restored": False,
            "local_route": None, "missing_route": "/missing", "reason": "not-restored-in-reader-bundle",
        })
    return blizzcast_reader.BlizzcastBundle(pages + [css], {}, sum(x["bytes"] for x in pages + [css]), audio_inventory, [], BASE)


class BlizzcastAudioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.reader_map, self.audio_map, self.zip_path = _build_fixture(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def load(self) -> blizzcast_audio.BlizzcastAudioBundle:
        return blizzcast_audio.load_blizzcast_audio_bundle(self.audio_map, self.root, self.reader_map)

    def test_fixed_map_bindings_whitelist_hashes_and_catalog_privacy(self) -> None:
        bundle = self.load()
        self.assertEqual([item["path"] for item in bundle.assets], [item["canonical_path"] for item in json.loads(self.audio_map.read_text())["records"]])
        self.assertEqual(bundle.origin_routes, {item["original_url"]: item["canonical_path"] for item in json.loads(self.audio_map.read_text())["records"]})
        self.assertIn('"audio_restored": true', bundle.catalog_bytes.decode())
        self.assertIn('"current_origin_audio_copy"', bundle.catalog_bytes.decode())
        self.assertIn('"rss_enclosure_length": 17', bundle.catalog_bytes.decode())
        self.assertNotIn("raw_path", bundle.catalog_bytes.decode())
        self.assertNotIn("Cookie", bundle.catalog_bytes.decode())
        self.assertEqual(bundle.estimated_bytes, sum(len(item["data"]) for item in bundle.assets) + len(bundle.catalog_bytes))

    def test_old_reader_map_sha_is_required(self) -> None:
        original = json.loads(self.audio_map.read_text(encoding="utf-8"))
        original["blizzcast_source_map_sha256"] = "0" * 64
        changed = self.root / "bad-binding.json"
        changed.write_text(json.dumps(original), encoding="utf-8")
        with self.assertRaisesRegex(blizzcast_audio.BlizzcastAudioError, "different BlizzCast reader map"):
            blizzcast_audio.load_blizzcast_audio_bundle(changed, self.root, self.reader_map)

    def test_zip_whitelist_and_storage_are_enforced(self) -> None:
        extra_zip = self.root / "extra-member.zip"
        with zipfile.ZipFile(self.zip_path, "r") as source, zipfile.ZipFile(extra_zip, "w", compression=zipfile.ZIP_STORED) as archive:
            for item in source.infolist():
                archive.writestr(item.filename, source.read(item))
            archive.writestr("unexpected.txt", b"not an allowed audio member")
        compressed_zip = self.root / "deflated.zip"
        with zipfile.ZipFile(self.zip_path, "r") as source, zipfile.ZipFile(compressed_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for item in source.infolist():
                archive.writestr(item.filename, source.read(item))
        original = json.loads(self.audio_map.read_text(encoding="utf-8"))
        for zip_path, expected_error in (
            (extra_zip, "exactly the two whitelisted MP3 members"),
            (compressed_zip, "ZIP_STORED bytes"),
        ):
            changed = copy.deepcopy(original)
            changed["payload_zip"] = zip_path.name
            changed["payload_zip_bytes"] = zip_path.stat().st_size
            changed["payload_zip_sha256"] = _sha(zip_path.read_bytes())
            map_path = self.root / f"map-for-{zip_path.stem}.json"
            map_path.write_text(json.dumps(changed), encoding="utf-8")
            with self.subTest(zip=zip_path.name), self.assertRaisesRegex(blizzcast_audio.BlizzcastAudioError, expected_error):
                blizzcast_audio.load_blizzcast_audio_bundle(map_path, self.root, self.reader_map)

    def test_transcripts_feed_routes_players_and_csp(self) -> None:
        bundle = self.load()
        reader = _reader_fixture()
        routes = {item["path"]: item for item in reader.generated_files if item["mime"] == "application/xhtml+xml"}
        transcript_before = {}
        for route, item in routes.items():
            root = ET.fromstring(item["data"].encode())
            transcript = next((node for node in root.iter() if node.attrib.get("id") == "transcript"), None)
            transcript_before[route] = "".join(transcript.itertext()) if transcript is not None else ""
        blizzcast_audio.augment_reader_bundle(reader, bundle)
        self.assertEqual(len(routes), 5)
        for route, item in routes.items():
            data = item["data"]
            root = ET.fromstring(data.encode())
            self.assertEqual(data.count(blizzcast_audio.SOURCE_NOTE), 1)
            self.assertTrue(
                "Images and interactive media remain unrestored" in data
                or "Original images and interactive media remain" in data
            )
            transcript = next((node for node in root.iter() if node.attrib.get("id") == "transcript"), None)
            self.assertEqual("".join(transcript.itertext()) if transcript is not None else "", transcript_before[route])
            policies = [node.attrib["content"] for node in root.iter() if node.tag == f"{{{XHTML}}}meta" and node.attrib.get("http-equiv") == "Content-Security-Policy"]
            self.assertEqual(len(policies), 1)
            self.assertIn("default-src 'none'", policies[0])
            if route in {blizzcast_reader.ROUTES_BY_ENTITY["BC02"], blizzcast_reader.ROUTES_BY_ENTITY["BC03"]}:
                self.assertIn("media-src 'self'", policies[0])
                self.assertNotIn("script-src", policies[0])
                self.assertEqual(data.count("<audio"), 1)
                self.assertIn('controls="controls" preload="none"', data)
                self.assertIn('type="audio/mpeg"', data)
                self.assertIn('download="episode', data)
            else:
                self.assertNotIn("media-src", policies[0])
                self.assertNotIn("<audio", data)
            self.assertNotIn("Audio not restored offline", data)
        feed = routes[blizzcast_reader.ROUTES_BY_ENTITY["BC01"]]["data"]
        self.assertIn("local audio downloads for the current-origin copies", feed)
        self.assertIn("Download Episode 2 audio (MP3 current copy)", feed)
        self.assertIn("Download Episode 1 audio (MP3 current copy)", feed)
        self.assertEqual([item["local_route"] for item in reader.dependency_inventory], [
            "/__offline/related-sites/blizzcast/audio/episode2.mp3",
            "/__offline/related-sites/blizzcast/audio/episode1.mp3",
        ])
        self.assertEqual(reader.origin_routes[SOURCE_URLS["episode1"]], "/__offline/related-sites/blizzcast/audio/episode1.mp3")

    def test_audio_option_requires_existing_accepted_reader_map(self) -> None:
        with self.assertRaisesRegex(export_github_pages.PagesExportError, "requires the accepted BlizzCast source map"):
            export_github_pages.export_pages(blizzcast_audio_map=self.audio_map)


if __name__ == "__main__":
    unittest.main()

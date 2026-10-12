from __future__ import annotations

import base64
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.parse
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_recovery_sources as validator  # noqa: E402


class RecoverySourceValidationTests(unittest.TestCase):
    def _gif_bytes(self) -> bytes:
        image = validator.load_pillow()
        first = image.new("RGB", (2, 2), color=(255, 0, 0))
        second = image.new("RGB", (2, 2), color=(0, 0, 255))
        output = io.BytesIO()
        first.save(output, format="GIF", save_all=True, append_images=[second], duration=[10, 20], loop=0, disposal=2)
        return output.getvalue()

    def _item(self, *, url: str, local: Path, data: bytes, mime: str, timestamp: str, entry: str, kind: str | None = None) -> dict:
        return {
            "logical_url": url,
            "local_path": local.relative_to(ROOT).as_posix(),
            "mime": mime,
            "kind": kind or ("image" if mime.startswith("image/") else "html"),
            "sha256": hashlib.sha256(data).hexdigest(),
            "content_length": len(data),
            "actual_timestamp": timestamp,
            "cdx_digest": validator.cdx_sha1_digest(data),
            "zip_file": "tests/.scratch-recovery/sources.zip",
            "zip_entry": entry,
        }

    def _fixture(self) -> tuple[Path, dict]:
        directory = Path(tempfile.mkdtemp(prefix="recovery-sources-", dir=ROOT / "tests"))
        self.addCleanup(shutil.rmtree, directory, ignore_errors=True)
        zip_path = directory / "sources.zip"
        html = b"<!doctype html><html><head><title>Guide</title></head><body>History</body></html>\n"
        xml = b'<?xml version="1.0"?><root><?xml-stylesheet type="text/xsl" href="/layout.xsl"?><item>ok</item></root>\n'
        gif = self._gif_bytes()
        files: list[tuple[str, bytes, str, str, str]] = [
            ("guide.html", html, "http://www.worldofwarcraft.com/info/guide.html", "text/html; charset=UTF-8", "20080512210044"),
            ("layout.xml", xml, "https://us.blizzard.com/info/layout.xml", "application/xml", "20080301010101"),
            ("animated.gif", gif, "http://www.worldofwarcraft.com/images/animated.gif", "image/gif", "20080501010101"),
        ]
        items: list[dict] = []
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data, url, mime, timestamp in files:
                local = directory / name
                local.write_bytes(data)
                entry = "objects/" + name
                archive.writestr(entry, data)
                item = self._item(url=url, local=local, data=data, mime=mime, timestamp=timestamp, entry=entry, kind="xml" if name.endswith(".xml") else None)
                item["zip_file"] = zip_path.relative_to(ROOT).as_posix()
                items.append(item)
        map_path = directory / "source-map.json"
        map_path.write_text(json.dumps({"schema_version": 1, "anchor_timestamp": validator.ANCHOR_TIMESTAMP, "files": items}, indent=2), encoding="utf-8")
        return map_path, {"directory": directory, "items": items, "zip": zip_path}

    def _rewrite_map(self, map_path: Path, items: list[dict]) -> None:
        map_path.write_text(json.dumps({"schema_version": 1, "anchor_timestamp": validator.ANCHOR_TIMESTAMP, "files": items}, indent=2), encoding="utf-8")

    def _prepare_legacy_lf_item(self, fixture: dict, *, suffix: bytes = b"\n", note: str | None = "CDX digest verified over payload plus one ARC framing LF.") -> bytes:
        info = self._mark_pre2008_static_image(fixture)
        item = info["item"]
        original = (ROOT / item["local_path"]).read_bytes()
        # The saved entity is the original payload.  Only the expected CDX
        # digest uses the virtual ARC framing suffix.
        item["cdx_digest"] = validator.cdx_sha1_digest(original + suffix)
        item["cdx_digest_mode"] = validator.LEGACY_ARC_LF_FRAMING_MODE
        if note is not None:
            item["cdx_framing_note"] = note
        return original

    def test_valid_html_xml_and_multiframe_gif_with_zip_provenance(self) -> None:
        map_path, fixture = self._fixture()
        result = validator.validate_maps([map_path], allow_no_zip=False)
        self.assertTrue(result["accepted"], result["errors"])
        self.assertEqual(result["summary"]["items_accepted"], 3)
        self.assertEqual(result["summary"]["at_anchor_count"], 1)
        evidence = result["maps"][0]["item_evidence"]
        xml_evidence = next(item for item in evidence if item["logical_url"].endswith("layout.xml"))
        self.assertTrue(xml_evidence["content"]["genuine_xml"])
        self.assertEqual(xml_evidence["content"]["xml_root"], "root")
        self.assertEqual(xml_evidence["content"]["xml_stylesheet_dependencies"], ["/layout.xsl"])
        gif_evidence = next(item for item in evidence if item["logical_url"].endswith("animated.gif"))
        self.assertTrue(gif_evidence["content"]["pillow_verified"])
        self.assertGreaterEqual(gif_evidence["content"]["frame_count"], 2)
        self.assertEqual(gif_evidence["zip_provenance"], "verified")
        xhtml = b'<?xml version="1.0"?><html xmlns="http://www.w3.org/1999/xhtml"><body><p>ok</p></body></html>'
        xhtml_content = validator.validate_content(xhtml, {"mime": "application/xhtml+xml", "kind": "page"})
        self.assertEqual(xhtml_content["content_status"], "valid_xml")
        self.assertTrue(xhtml_content["genuine_xml"])

    def test_hard_failures_cover_wrong_year_soft404_and_synthetic_url(self) -> None:
        map_path, fixture = self._fixture()
        items = fixture["items"]
        items[0]["actual_timestamp"] = "20101203214958"
        items[1]["logical_url"] = "http://www.worldofwarcraft.com/__offline/missing.html"
        items[2]["mime"] = "image/png"
        items[2]["cdx_digest"] = "-"
        self._rewrite_map(map_path, items)
        result = validator.validate_maps([map_path], allow_no_zip=False)
        self.assertFalse(result["accepted"])
        failures = [error for item in result["maps"][0]["item_evidence"] for error in item["errors"]]
        self.assertTrue(any("not a 2008 capture" in error for error in failures))
        self.assertTrue(any("synthetic offline route" in error for error in failures))
        self.assertTrue(any("Pillow verify/load failed" in error or "MIME image/png" in error for error in failures))
        with self.assertRaises(validator.ValidationFailure):
            validator.validate_content(b"<!doctype html><title>404 File Not Found</title>", {"mime": "text/html", "kind": "html"})

    def test_allow_no_zip_is_explicit_and_old_map_comparison_only(self) -> None:
        map_path, fixture = self._fixture()
        for item in fixture["items"]:
            item.pop("zip_file", None)
            item.pop("zip_entry", None)
        map_path.write_text(json.dumps({"files": fixture["items"]}), encoding="utf-8")
        rejected = validator.validate_maps([map_path], allow_no_zip=False)
        self.assertFalse(rejected["accepted"])
        accepted = validator.validate_maps([map_path], allow_no_zip=True)
        self.assertTrue(accepted["accepted"], accepted["errors"])
        self.assertEqual(accepted["maps"][0]["item_evidence"][0]["zip_provenance"], "omitted_by_allow_no_zip")

    def test_official_host_and_cdx_digest_checks(self) -> None:
        map_path, fixture = self._fixture()
        fixture["items"][0]["logical_url"] = "https://example.invalid/guide.html"
        fixture["items"][1]["cdx_digest"] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        self._rewrite_map(map_path, fixture["items"])
        result = validator.validate_maps([map_path], allow_no_zip=False)
        self.assertFalse(result["accepted"])
        failures = [error for item in result["maps"][0]["item_evidence"] for error in item["errors"]]
        self.assertTrue(any("official public host" in error for error in failures))
        self.assertTrue(any("CDX digest mismatch" in error for error in failures))

    def test_zip_member_absolute_path_is_rejected(self) -> None:
        map_path, fixture = self._fixture()
        fixture["items"][0]["zip_entry"] = "/objects/guide.html"
        self._rewrite_map(map_path, fixture["items"])
        result = validator.validate_maps([map_path], allow_no_zip=False)
        self.assertFalse(result["accepted"])
        errors = result["maps"][0]["item_evidence"][0]["errors"]
        self.assertTrue(any("zip_entry is unsafe" in error for error in errors))

    def _mark_pre2008_static_image(self, fixture: dict) -> dict:
        """Create a schema-faithful empty full-2008 CDX evidence fixture."""

        item = fixture["items"][2]
        evidence_dir = fixture["directory"] / "early-images-58-cdx"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        raw_fd, raw_name = tempfile.mkstemp(prefix="test-pre2008-", suffix=".raw", dir=evidence_dir)
        os.close(raw_fd)
        meta_fd, meta_name = tempfile.mkstemp(prefix="test-pre2008-", suffix=".meta.json", dir=evidence_dir)
        os.close(meta_fd)
        raw_path = Path(raw_name)
        evidence_path = Path(meta_name)
        self.addCleanup(raw_path.unlink, missing_ok=True)
        self.addCleanup(evidence_path.unlink, missing_ok=True)

        raw_data = b"[]"
        raw_path.write_bytes(raw_data)
        original = item["logical_url"]
        query_url = (
            "https://web.archive.org/cdx/search/cdx?url="
            + urllib.parse.quote(original, safe="")
            + "&matchType=exact&from=20080101000000&to=20081231235959"
            + "&output=json&fl=timestamp%2Coriginal%2Cstatuscode%2Cdigest%2Clength%2Cmimetype&limit=10000"
        )
        metadata = {
            "sequence": 999,
            "original": original,
            "canonical_url": "//" + urllib.parse.urlsplit(original).netloc + urllib.parse.urlsplit(original).path,
            "query_url": query_url,
            "status": "success",
            "raw_path": raw_path.relative_to(ROOT).as_posix(),
            "metadata_path": evidence_path.relative_to(ROOT).as_posix(),
            "http_status": 200,
            "final_url": query_url,
            "body_length": len(raw_data),
            "body_sha256": hashlib.sha256(raw_data).hexdigest(),
            "coverage_status": "complete_empty",
            "truncated": False,
            "row_count": 0,
            "candidate_rows": [],
            "parse_error": None,
        }
        evidence_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        item = fixture["items"][2]
        item.update(
            {
                "actual_timestamp": "20070101010101",
                "kind": "image",
                "mime": "image/gif",
                "temporal_class": "pre2008_static_supplement",
                "supplement_note": "Earlier static icon retained as an explicit reconstruction supplement.",
                "year_fallback_evidence": evidence_path.relative_to(ROOT).as_posix(),
                "year_fallback_evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
            }
        )
        return {"meta_path": evidence_path, "raw_path": raw_path, "item": item}

    def _refresh_pre2008_evidence(self, info: dict, *, raw: bytes | None = None, mutate=None) -> None:
        if raw is not None:
            info["raw_path"].write_bytes(raw)
        metadata = json.loads(info["meta_path"].read_text(encoding="utf-8"))
        if raw is not None:
            metadata["body_length"] = len(raw)
            metadata["body_sha256"] = hashlib.sha256(raw).hexdigest()
        if mutate is not None:
            mutate(metadata)
        info["meta_path"].write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        info["item"]["year_fallback_evidence_sha256"] = hashlib.sha256(info["meta_path"].read_bytes()).hexdigest()

    def test_pre2008_static_supplement_requires_opt_in_and_keeps_separate_bucket(self) -> None:
        map_path, fixture = self._fixture()
        self._mark_pre2008_static_image(fixture)
        self._rewrite_map(map_path, fixture["items"])

        strict = validator.validate_maps([map_path], allow_no_zip=False)
        self.assertFalse(strict["accepted"])
        strict_error = strict["maps"][0]["item_evidence"][2]["errors"]
        self.assertTrue(any("not a 2008 capture" in error for error in strict_error))

        allowed = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
        )
        self.assertTrue(allowed["accepted"], allowed["errors"])
        self.assertEqual(allowed["summary"]["before_2008_static_supplement_count"], 1)
        self.assertEqual(allowed["summary"]["at_anchor_count"], 1)
        supplement = allowed["maps"][0]["item_evidence"][2]
        self.assertEqual(supplement["time_bucket"], "before_2008_static_supplement")
        self.assertEqual(supplement["baseline_status"], "supplement_only_before_2008")
        self.assertEqual(supplement["pre2008_static_supplement"]["temporal_class"], "pre2008_static_supplement")
        pre2008_evidence = supplement["pre2008_static_supplement"]
        self.assertIn("tests", pre2008_evidence["evidence_metadata_path"])
        self.assertIn("from=20080101000000", pre2008_evidence["evidence_query_url"])
        self.assertIn("to=20081231235959", pre2008_evidence["evidence_query_url"])
        self.assertEqual(pre2008_evidence["evidence_cdx_row_count"], 0)
        self.assertEqual(pre2008_evidence["evidence_raw_length"], 2)
        self.assertEqual(len(pre2008_evidence["evidence_raw_sha256"]), 64)
        self.assertEqual(pre2008_evidence["evidence_metadata_sha256"], fixture["items"][2]["year_fallback_evidence_sha256"])
        self.assertEqual(supplement["zip_provenance"], "verified")
        self.assertTrue(supplement["content"]["pillow_verified"])

    def test_pre2008_opt_in_still_rejects_later_html_and_missing_evidence(self) -> None:
        map_path, fixture = self._fixture()
        self._mark_pre2008_static_image(fixture)
        fixture["items"][2]["actual_timestamp"] = "20101203214958"
        self._rewrite_map(map_path, fixture["items"])
        later = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
        )
        self.assertFalse(later["accepted"])
        self.assertTrue(any("not a 2008 capture" in error for error in later["maps"][0]["item_evidence"][2]["errors"]))

        map_path, fixture = self._fixture()
        self._mark_pre2008_static_image(fixture)
        fixture["items"][2]["kind"] = "html"
        fixture["items"][2]["mime"] = "text/html"
        self._rewrite_map(map_path, fixture["items"])
        html_result = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
        )
        self.assertFalse(html_result["accepted"])
        html_errors = html_result["maps"][0]["item_evidence"][2]["errors"]
        self.assertTrue(any("requires kind=image" in error for error in html_errors))
        self.assertTrue(any("requires image/* MIME" in error for error in html_errors))

        map_path, fixture = self._fixture()
        self._mark_pre2008_static_image(fixture)
        fixture["items"][2].pop("year_fallback_evidence")
        self._rewrite_map(map_path, fixture["items"])
        missing_evidence = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
        )
        self.assertFalse(missing_evidence["accepted"])
        missing_errors = missing_evidence["maps"][0]["item_evidence"][2]["errors"]
        self.assertTrue(any("requires year_fallback_evidence" in error for error in missing_errors))

    def test_pre2008_evidence_rejects_changed_raw_body(self) -> None:
        map_path, fixture = self._fixture()
        info = self._mark_pre2008_static_image(fixture)
        self._refresh_pre2008_evidence(info, raw=b"[ ]")
        # Keep metadata's declared hash stale to isolate the raw-integrity gate.
        metadata = json.loads(info["meta_path"].read_text(encoding="utf-8"))
        metadata["body_sha256"] = hashlib.sha256(b"[]").hexdigest()
        metadata["body_length"] = 2
        info["meta_path"].write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        info["item"]["year_fallback_evidence_sha256"] = hashlib.sha256(info["meta_path"].read_bytes()).hexdigest()
        self._rewrite_map(map_path, fixture["items"])
        result = validator.validate_maps([map_path], allow_no_zip=False, allow_pre2008_static_supplement=True)
        self.assertFalse(result["accepted"])
        errors = result["maps"][0]["item_evidence"][2]["errors"]
        self.assertTrue(any("raw length mismatch" in error or "raw SHA256 mismatch" in error for error in errors))

    def test_pre2008_evidence_rejects_anchor_only_window(self) -> None:
        map_path, fixture = self._fixture()
        info = self._mark_pre2008_static_image(fixture)
        self._refresh_pre2008_evidence(
            info,
            mutate=lambda metadata: metadata.update(
                {
                    "query_url": metadata["query_url"].replace("to=20081231235959", "to=20080512210044"),
                    "final_url": metadata["final_url"].replace("to=20081231235959", "to=20080512210044"),
                }
            ),
        )
        self._rewrite_map(map_path, fixture["items"])
        result = validator.validate_maps([map_path], allow_no_zip=False, allow_pre2008_static_supplement=True)
        self.assertFalse(result["accepted"])
        errors = result["maps"][0]["item_evidence"][2]["errors"]
        self.assertTrue(any("end at 20081231235959" in error for error in errors))

    def test_pre2008_evidence_rejects_nonempty_cdx_rows(self) -> None:
        map_path, fixture = self._fixture()
        info = self._mark_pre2008_static_image(fixture)
        self._refresh_pre2008_evidence(
            info,
            raw=b'[["timestamp","original"],["20080101000000","x"]]',
            mutate=lambda metadata: metadata.update(
                {
                    "coverage_status": "success_rows",
                    "row_count": 1,
                    "candidate_rows": [{"timestamp": "20080101000000"}],
                }
            ),
        )
        self._rewrite_map(map_path, fixture["items"])
        result = validator.validate_maps([map_path], allow_no_zip=False, allow_pre2008_static_supplement=True)
        self.assertFalse(result["accepted"])
        errors = result["maps"][0]["item_evidence"][2]["errors"]
        self.assertTrue(any("contains CDX rows" in error or "coverage is not complete_empty" in error for error in errors))

    def test_pre2008_evidence_rejects_wrong_original_url(self) -> None:
        map_path, fixture = self._fixture()
        info = self._mark_pre2008_static_image(fixture)
        self._refresh_pre2008_evidence(
            info,
            mutate=lambda metadata: metadata.update(
                {"original": "http://www.worldofwarcraft.com/images/other.gif"}
            ),
        )
        self._rewrite_map(map_path, fixture["items"])
        result = validator.validate_maps([map_path], allow_no_zip=False, allow_pre2008_static_supplement=True)
        self.assertFalse(result["accepted"])
        errors = result["maps"][0]["item_evidence"][2]["errors"]
        self.assertTrue(any("original does not match" in error for error in errors))

    def test_pre2008_evidence_requires_archive_cdx_endpoint_and_single_parameters(self) -> None:
        map_path, fixture = self._fixture()
        info = self._mark_pre2008_static_image(fixture)
        self._refresh_pre2008_evidence(
            info,
            mutate=lambda metadata: metadata.update(
                {
                    "query_url": metadata["query_url"].replace(
                        "web.archive.org/cdx/search/cdx", "example.invalid/not-cdx"
                    ),
                    "final_url": metadata["final_url"].replace(
                        "web.archive.org/cdx/search/cdx", "example.invalid/not-cdx"
                    ),
                }
            ),
        )
        self._rewrite_map(map_path, fixture["items"])
        wrong_endpoint = validator.validate_maps(
            [map_path], allow_no_zip=False, allow_pre2008_static_supplement=True
        )
        self.assertFalse(wrong_endpoint["accepted"])
        endpoint_errors = wrong_endpoint["maps"][0]["item_evidence"][2]["errors"]
        self.assertTrue(any("query host must be web.archive.org" in error for error in endpoint_errors))

        map_path, fixture = self._fixture()
        info = self._mark_pre2008_static_image(fixture)
        self._refresh_pre2008_evidence(
            info,
            mutate=lambda metadata: metadata.update(
                {
                    "query_url": metadata["query_url"] + "&from=20080101000000",
                    "final_url": metadata["final_url"] + "&from=20080101000000",
                }
            ),
        )
        self._rewrite_map(map_path, fixture["items"])
        duplicate_parameter = validator.validate_maps(
            [map_path], allow_no_zip=False, allow_pre2008_static_supplement=True
        )
        self.assertFalse(duplicate_parameter["accepted"])
        duplicate_errors = duplicate_parameter["maps"][0]["item_evidence"][2]["errors"]
        self.assertTrue(any("from parameter must be single-valued" in error for error in duplicate_errors))

    def test_legacy_arc_lf_default_rejects_payload_mismatch(self) -> None:
        map_path, fixture = self._fixture()
        self._prepare_legacy_lf_item(fixture)
        self._rewrite_map(map_path, fixture["items"])
        result = validator.validate_maps(
            [map_path], allow_no_zip=False, allow_pre2008_static_supplement=True
        )
        self.assertFalse(result["accepted"])
        item_evidence = result["maps"][0]["item_evidence"][2]
        self.assertTrue(any("CDX digest mismatch" in error for error in item_evidence["errors"]))

    def test_legacy_arc_lf_requires_mode_and_explicit_flag(self) -> None:
        map_path, fixture = self._fixture()
        self._prepare_legacy_lf_item(fixture)
        fixture["items"][2].pop("cdx_digest_mode")
        self._rewrite_map(map_path, fixture["items"])
        no_mode = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
            allow_legacy_arc_lf_framing=True,
        )
        self.assertFalse(no_mode["accepted"])

        map_path, fixture = self._fixture()
        self._prepare_legacy_lf_item(fixture)
        self._rewrite_map(map_path, fixture["items"])
        no_flag = validator.validate_maps(
            [map_path], allow_no_zip=False, allow_pre2008_static_supplement=True
        )
        self.assertFalse(no_flag["accepted"])

    def test_legacy_arc_lf_accepts_single_lf_without_mutating_source(self) -> None:
        map_path, fixture = self._fixture()
        original = self._prepare_legacy_lf_item(fixture)
        item = fixture["items"][2]
        local_path = ROOT / item["local_path"]
        zip_path = ROOT / item["zip_file"]
        before = local_path.read_bytes()
        zip_before = zip_path.read_bytes()
        self._rewrite_map(map_path, fixture["items"])
        result = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
            allow_legacy_arc_lf_framing=True,
        )
        self.assertTrue(result["accepted"], result["errors"])
        evidence = result["maps"][0]["item_evidence"][2]
        self.assertEqual(local_path.read_bytes(), before)
        self.assertEqual(zip_path.read_bytes(), zip_before)
        self.assertEqual(before, original)
        self.assertTrue(evidence["cdx_digest_match"])
        self.assertEqual(evidence["cdx_digest_match_mode"], validator.LEGACY_ARC_LF_FRAMING_MODE)
        legacy = evidence["legacy_arc_lf_framing"]
        self.assertEqual(legacy["raw_payload_digest"], validator.cdx_sha1_digest(original))
        self.assertNotEqual(legacy["raw_payload_digest"], item["cdx_digest"])
        self.assertEqual(legacy["framed_digest"], item["cdx_digest"])
        self.assertEqual(legacy["verified_digest"], item["cdx_digest"])
        self.assertEqual(legacy["mode"], validator.LEGACY_ARC_LF_FRAMING_MODE)
        self.assertEqual(legacy["suffix_hex0a"], "0a")
        self.assertTrue(legacy["accepted"])

    def test_legacy_arc_lf_rejects_double_lf(self) -> None:
        map_path, fixture = self._fixture()
        self._prepare_legacy_lf_item(fixture, suffix=b"\n\n")
        self._rewrite_map(map_path, fixture["items"])
        result = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
            allow_legacy_arc_lf_framing=True,
        )
        self.assertFalse(result["accepted"])
        legacy = result["maps"][0]["item_evidence"][2]["legacy_arc_lf_framing"]
        self.assertFalse(legacy["accepted"])

    def test_legacy_arc_lf_rejects_non_pre2008_non_image_and_missing_note(self) -> None:
        map_path, fixture = self._fixture()
        self._prepare_legacy_lf_item(fixture)
        fixture["items"][2]["actual_timestamp"] = "20080501010101"
        self._rewrite_map(map_path, fixture["items"])
        non_pre2008 = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
            allow_legacy_arc_lf_framing=True,
        )
        self.assertFalse(non_pre2008["accepted"])

        map_path, fixture = self._fixture()
        self._prepare_legacy_lf_item(fixture)
        fixture["items"][2]["kind"] = "html"
        fixture["items"][2]["mime"] = "text/html"
        self._rewrite_map(map_path, fixture["items"])
        non_image = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
            allow_legacy_arc_lf_framing=True,
        )
        self.assertFalse(non_image["accepted"])

        map_path, fixture = self._fixture()
        self._prepare_legacy_lf_item(fixture, note=None)
        self._rewrite_map(map_path, fixture["items"])
        missing_note = validator.validate_maps(
            [map_path],
            allow_no_zip=False,
            allow_pre2008_static_supplement=True,
            allow_legacy_arc_lf_framing=True,
        )
        self.assertFalse(missing_note["accepted"])

    def test_pre2008_cli_flag_is_explicit(self) -> None:
        args = validator.parse_args(["--map", "tests/example.json", "--allow-pre2008-static-supplement"])
        self.assertTrue(args.allow_pre2008_static_supplement)
        legacy_args = validator.parse_args(
            ["--map", "tests/example.json", "--allow-legacy-arc-lf-framing"]
        )
        self.assertTrue(legacy_args.allow_legacy_arc_lf_framing)


if __name__ == "__main__":
    unittest.main()

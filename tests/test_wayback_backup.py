from __future__ import annotations

import gzip
import base64
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock
import urllib.parse
import zipfile


TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import wayback_backup as wb  # noqa: E402


ARCHIVE_BASE = "https://web.archive.org/web/20101203214958id_/"


class FakeFetcher:
    def __init__(self, routes: dict[str, object]):
        self.routes = routes
        self.calls: list[str] = []

    def __call__(self, url: str, max_bytes: int, on_chunk):
        self.calls.append(url)
        original = urllib.parse.unquote(url.split("id_/", 1)[1])
        value = self.routes[original]
        if isinstance(value, Exception):
            raise value
        if not isinstance(value, wb.FetchResult):
            raise AssertionError(f"bad fake route: {value!r}")
        for start in range(0, len(value.body), 64 * 1024):
            on_chunk(min(64 * 1024, len(value.body) - start))
        return value


def result(original: str, body: bytes, *, status: int = 200, final_url: str | None = None, headers=None):
    return wb.FetchResult(
        requested_url=ARCHIVE_BASE + original,
        final_url=final_url or ARCHIVE_BASE + original,
        status=status,
        headers=headers or {"memento-datetime": "Fri, 03 Dec 2010 21:49:58 GMT", "X-Test": "yes"},
        body=body,
    )


def item(path: str, timestamp: str = "20101203214958") -> wb.PlanItem:
    return wb.PlanItem("http://www.worldofwarcraft.com" + path, timestamp, "core")


def config(root: Path, **kwargs) -> wb.BackupConfig:
    values = dict(
        out_dir=root / "backups" / "run",
        budget_root=root,
        max_bytes=10_000_000,
        min_free_bytes=0,
        max_requests=20,
        max_object_bytes=wb.DEFAULT_OBJECT_BYTES,
        volume_bytes=10_000,
        volume_objects=100,
        reserve_bytes=0,
    )
    values.update(kwargs)
    return wb.BackupConfig(**values)


class WaybackBackupTests(unittest.TestCase):
    def test_transport_failure_keeps_traceback_in_attempt_evidence(self):
        opener = mock.Mock()
        opener.open.side_effect = wb.urllib.error.URLError(FileNotFoundError(2, "diagnostic path missing"))
        with mock.patch.object(wb.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(wb.FetchError) as caught:
                wb.fetch_once(ARCHIVE_BASE + "http://www.worldofwarcraft.com/test.jpg", 1000)
        error = caught.exception
        self.assertIsNone(error.status)
        self.assertTrue(error.retryable_site_failure)
        self.assertIn("URLError", error.exception_traceback)
        self.assertIn("diagnostic path missing", error.exception_traceback)
        record = wb.BackupRunner._attempt_record(1, error=error)
        self.assertEqual(record["exception_traceback"], error.exception_traceback)
        self.assertNotIn("archive_or_origin_error", record["reason"])

    def test_success_deduplicates_and_resume_skips_network(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = item("/a")
            second = item("/b")
            payload = b"same entity bytes\n"
            fake = FakeFetcher({first.original: result(first.original, payload), second.original: result(second.original, payload)})
            summary = wb.BackupRunner(first.timestamp, [first, second], config(root), fetcher=fake).run()
            self.assertEqual(summary["stats"]["success"], 2)
            self.assertEqual(len(fake.calls), 2)

            records = [json.loads(line) for line in (config(root).out_dir / "manifest.jsonl").read_text().splitlines()]
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["zip_entry"], records[1]["zip_entry"])
            self.assertEqual(records[0]["actual_timestamp"], "20101203214958")
            self.assertEqual(records[0]["content_length"], len(payload))
            self.assertEqual(len(list(config(root).out_dir.glob("objects-*.zip"))), 1)

            no_network = FakeFetcher({})
            resumed = wb.BackupRunner(first.timestamp, [first, second], config(root), fetcher=no_network).run()
            self.assertEqual(resumed["stats"]["resumed"], 2)
            self.assertEqual(resumed["stats"]["success"], 2)
            self.assertEqual(no_network.calls, [])
            all_records = [json.loads(line) for line in (config(root).out_dir / "manifest.jsonl").read_text().splitlines()]
            self.assertTrue(all(record.get("skipped") for record in all_records[2:]))

    def test_error_page_status_and_external_final_are_not_success(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            error_item = item("/error")
            status_item = item("/missing")
            external_item = item("/external")
            fake = FakeFetcher({
                error_item.original: result(error_item.original, b"<html>Wayback Machine Error</html>"),
                status_item.original: result(status_item.original, b"not found", status=404),
                external_item.original: result(
                    external_item.original,
                    b"ok",
                    final_url="https://evil.example/escape",
                ),
            })
            summary = wb.BackupRunner(
                error_item.timestamp,
                [error_item, status_item, external_item],
                config(root),
                fetcher=fake,
            ).run()
            self.assertEqual(summary["stats"]["success"], 0)
            self.assertEqual(summary["stats"]["failed"], 3)
            self.assertEqual(list(config(root).out_dir.glob("objects-*.zip")), [])
            records = [json.loads(line) for line in (config(root).out_dir / "manifest.jsonl").read_text().splitlines()]
            self.assertTrue(all(record["status"] == "failed" for record in records))
            self.assertIn("wayback_error_page", records[0]["failure_reason"])
            self.assertIn("archive_external_final_url", records[2]["failure_reason"])

    def test_budget_stops_during_stream_and_disk_threshold_blocks_start(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            planned = item("/large")
            fake = FakeFetcher({planned.original: result(planned.original, b"x" * 2_000_000)})
            limited = config(root, max_bytes=1_500_000, max_object_bytes=3_000_000)
            summary = wb.BackupRunner(planned.timestamp, [planned], limited, fetcher=fake).run()
            self.assertEqual(summary["stop_reason"], "budget_exceeded")
            self.assertEqual(summary["stats"]["failed"], 1)
            self.assertEqual(len(fake.calls), 1)

            blocked_root = root / "other"
            blocked_root.mkdir()
            blocked = config(blocked_root, out_dir=blocked_root / "out", min_free_bytes=1)
            with self.assertRaises(wb.BudgetExceeded):
                wb.BackupRunner(
                    planned.timestamp,
                    [planned],
                    blocked,
                    fetcher=FakeFetcher({}),
                    disk_usage_fn=lambda _path: shutil._ntuple_diskusage(100, 100, 0),
                ).run()

    def test_corrupt_volume_and_manifest_reference_fail_recovery(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            planned = item("/recover")
            fake = FakeFetcher({planned.original: result(planned.original, b"recover me")})
            cfg = config(root)
            wb.BackupRunner(planned.timestamp, [planned], cfg, fetcher=fake).run()
            volume = next(cfg.out_dir.glob("objects-*.zip"))
            raw = volume.read_bytes()
            volume.write_bytes(raw[:-12])
            with self.assertRaises(wb.RecoveryError):
                wb.BackupRunner(planned.timestamp, [planned], cfg, fetcher=FakeFetcher({})).run()

            # Rebuild a clean run, then alter a manifest reference.
            shutil.rmtree(cfg.out_dir)
            wb.BackupRunner(planned.timestamp, [planned], cfg, fetcher=fake).run()
            manifest = cfg.out_dir / "manifest.jsonl"
            text = manifest.read_text()
            text = text.replace("objects/", "objects/" + "f" * 64 + "/", 1)
            manifest.write_text(text)
            with self.assertRaises(wb.RecoveryError):
                wb.BackupRunner(planned.timestamp, [planned], cfg, fetcher=FakeFetcher({})).run()

    def test_volume_threshold_and_object_limit_split(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            items = [item(f"/item-{index}") for index in range(4)]
            fake = FakeFetcher({
                current.original: result(current.original, f"payload-{index}".encode())
                for index, current in enumerate(items)
            })
            cfg = config(root, volume_bytes=10_000, volume_objects=2)
            wb.BackupRunner(items[0].timestamp, items, cfg, fetcher=fake).run()
            volumes = sorted(cfg.out_dir.glob("objects-*.zip"))
            self.assertEqual(len(volumes), 2)
            for volume in volumes:
                with zipfile.ZipFile(volume) as zf:
                    self.assertLessEqual(len(zf.infolist()), 2)

    def test_retry_after_is_capped_and_short_retry_is_used(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            planned = item("/rate-limited")
            calls = 0
            sleeps: list[float] = []

            def fake(url, max_bytes, on_chunk):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise wb.FetchError(
                        "rate_limited",
                        status=429,
                        final_url=url,
                        headers={"Retry-After": "45"},
                        retryable_site_failure=True,
                    )
                on_chunk(2)
                return result(planned.original, b"ok")

            summary = wb.BackupRunner(
                planned.timestamp,
                [planned],
                config(root),
                fetcher=fake,
                sleep_fn=sleeps.append,
            ).run()
            self.assertEqual(summary["stats"]["success"], 1)
            self.assertEqual(calls, 2)
            self.assertEqual(sleeps, [30.0])

    def test_gzip_entity_decode_and_fragment_encoding(self):
        body = b"decoded body"
        compressed = gzip.compress(body)

        class Response:
            headers = {"cOnTeNt-EnCoDiNg": "gzip"}

            def __init__(self):
                self.data = compressed

            def read(self, count):
                value, self.data = self.data[:count], self.data[count:]
                return value

        self.assertEqual(wb._read_entity(Response(), 1000), body)
        url = wb.build_archive_url("20101203214958", "http://www.worldofwarcraft.com/a#fragment")
        self.assertIn("%23fragment", url)
        self.assertTrue(wb._is_archive_url(url))

    def test_truncated_gzip_is_not_a_preserved_entity(self):
        class Response:
            headers = {"Content-Encoding": "gzip"}

            def __init__(self):
                self.data = gzip.compress(b"must not accept a truncated entity")[:-5]

            def read(self, count):
                value, self.data = self.data[:count], self.data[count:]
                return value

        with self.assertRaisesRegex(wb.FetchError, "truncated_compressed_entity"):
            wb._read_entity(Response(), 1000)

    def test_mislabeled_gzip_requires_matching_independent_cdx_digest(self):
        payload = b"<!DOCTYPE html><html>archived source</html>"
        digest = base64.b32encode(hashlib.sha1(payload).digest()).decode("ascii")

        class Response:
            headers = {"Content-Encoding": "gzip"}
            def __init__(self): self.data = payload
            def read(self, count):
                value, self.data = self.data[:count], self.data[count:]
                return value

        note = {}
        self.assertEqual(wb._read_entity(Response(), 1000, expected_cdx_digest=digest,
                                        interpretation=note), payload)
        self.assertIn("verified_by_cdx_sha1", note["value"])
        with self.assertRaisesRegex(wb.FetchError, "cdx_digest_mismatch"):
            wb._read_entity(Response(), 1000, expected_cdx_digest="A" * 32)
        with self.assertRaisesRegex(wb.FetchError, "content_decode_error"):
            wb._read_entity(Response(), 1000)

    def test_wire_evidence_faq_fallback_matches_recorded_capture(self):
        evidence = Path(__file__).resolve().parents[1] / "research/site-recovery-2008/wire-diagnostics"
        result_path = evidence / "20080509123843_burningcrusade_faq.result.json"
        if not result_path.exists():
            self.skipTest("local historical diagnostic fixture absent")
        proof = json.loads(result_path.read_text(encoding="utf-8"))
        wire = (evidence / "20080509123843_burningcrusade_faq.wire.bin").read_bytes()
        class Response:
            headers = proof["response_headers"]
            def __init__(self): self.data = wire
            def read(self, count):
                value, self.data = self.data[:count], self.data[count:]
                return value
        self.assertEqual(wb._read_entity(Response(), 1_000_000,
                                        expected_cdx_digest=proof["expected_cdx_digest"]), wire)

    def test_identity_request_and_decoding_failure_preserve_response_metadata(self):
        url = ARCHIVE_BASE + "http://www.worldofwarcraft.com/pvp/battlegrounds/"

        class Response:
            headers = {"Content-Encoding": "gzip", "Memento-Datetime": "Fri, 03 Dec 2010 21:49:58 GMT"}
            data = b"<html>incorrectly marked gzip</html>"

            def getcode(self): return 200
            def geturl(self): return url
            def close(self): pass
            def read(self, count):
                value, self.data = self.data[:count], self.data[count:]
                return value

        opener = mock.Mock()
        opener.open.return_value = Response()
        with mock.patch.object(wb.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(wb.FetchError) as caught:
                wb.fetch_once(url, 1000)
        self.assertEqual(opener.open.call_args.args[0].get_header("Accept-encoding"), "identity")
        self.assertEqual(caught.exception.status, 200)
        self.assertEqual(caught.exception.final_url, url)
        self.assertEqual(caught.exception.headers["Content-Encoding"], "gzip")
        self.assertIn("content_decode_error", caught.exception.reason)
        preview = json.loads(caught.exception.body_preview)
        self.assertTrue(preview["wire_prefix_hex"].startswith(b"<html>".hex()))
        self.assertEqual(preview["content_encoding"], "gzip")


if __name__ == "__main__":
    unittest.main()

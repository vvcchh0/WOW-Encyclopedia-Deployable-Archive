from __future__ import annotations

import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import archive_transport as transport  # noqa: E402


def _jpeg() -> bytes:
    output = io.BytesIO()
    with Image.new("RGB", (7, 5), (30, 80, 120)) as image:
        image.save(output, format="JPEG", quality=92)
    return output.getvalue()


class ArchiveTransportTests(unittest.TestCase):
    def _row(self, timestamp: str, original: str, *, digest: str | None = None, length: int = 100) -> dict[str, str]:
        return {
            "timestamp": timestamp,
            "original": original,
            "statuscode": "200",
            "digest": digest or "A" * 32,
            "length": str(length),
            "mimetype": "image/jpeg",
        }

    def test_new_selection_is_origin_aware_and_excludes_existing_and_attempted_routes(self) -> None:
        rows = [
            self._row("20080501000000", "http://www.wow-europe.com:80/screenoftheday/screenoftheday/2008-01.jpg"),
            self._row("20080501000001", "http://www.wow-europe.com:80/screenoftheday/screenoftheday/2008-01-thumb.jpg"),
            self._row("20080502000000", "http://www.wow-europe.com:80/screenoftheday/screenoftheday/2008-02.jpg"),
            self._row("20080502000001", "http://www.wow-europe.com:80/screenoftheday/screenoftheday/2008-02-thumb.jpg"),
            self._row("20070401000000", "http://www.wow-europe.com:80/screenoftheday/screenoftheday/2007-01.jpg"),
            self._row("20080503000000", "http://wow-europe.com:80/screenoftheday/screenoftheday/2008-01.jpg"),
        ]
        existing = {transport.route_key("http://www.wow-europe.com/screenoftheday/screenoftheday/2008-02.jpg")}
        attempted = {transport.route_key("http://www.wow-europe.com/screenoftheday/screenoftheday/2007-01.jpg")}
        selected = transport.select_new_candidates(rows, existing_routes=existing, attempted_routes=attempted, limit=3)

        routes = {transport.route_key(item["original"]) for item in selected}
        self.assertNotIn(next(iter(existing)), routes)
        self.assertNotIn(next(iter(attempted)), routes)
        self.assertEqual(len(selected), 3)
        self.assertEqual([item["origin_namespace"] for item in selected].count("wow-europe.com"), 1)
        # The paired full/thumb entries from the www origin are kept together
        # before the unpaired bare-host entry.
        self.assertEqual([Path(item["path"]).name for item in selected[:2]], ["2008-01.jpg", "2008-01-thumb.jpg"])

    def test_transport_commands_make_direct_the_first_explicit_choice(self) -> None:
        item = {
            "actual_timestamp": "20080501000000",
            "original": "http://www.wow-europe.com:80/screenoftheday/screenoftheday/x.jpg",
        }
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            direct = transport._curl_command(item, "direct", base / "direct.h", base / "direct.b", 1000)
            proxy = transport._curl_command(item, "proxy", base / "proxy.h", base / "proxy.b", 1000)
        self.assertIn("--noproxy", direct)
        self.assertIn("*", direct)
        self.assertNotIn("--proxy", direct)
        self.assertIn("--proxy", proxy)
        self.assertIn(transport.PROXY, proxy)
        self.assertIn("8", direct)
        self.assertIn("10", proxy)

    def test_parse_headers_excludes_connect_only_and_preserves_block_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "connect-only.headers"
            path.write_text(
                "HTTP/1.1 200 Connection established\r\n"
                "Proxy-Agent: fixture\r\n\r\n",
                encoding="iso-8859-1",
            )
            headers, status, block_count = transport.parse_headers(path)
        self.assertEqual(headers, {})
        self.assertIsNone(status)
        self.assertEqual(block_count, 1)

    def test_parse_headers_uses_last_non_connect_source_block(self) -> None:
        fixtures = {
            404: (
                "HTTP/1.1 200 Connection established\r\n\r\n"
                "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
            ),
            200: (
                "HTTP/1.1 200 Connection established\r\n\r\n"
                "HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n"
            ),
        }
        for expected_status, text in fixtures.items():
            with self.subTest(expected_status=expected_status), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "response.headers"
                path.write_text(text, encoding="iso-8859-1")
                headers, status, block_count = transport.parse_headers(path)
            self.assertEqual(status, expected_status)
            self.assertEqual(block_count, 2)
            self.assertTrue(headers)

    def test_missing_or_invalid_memento_does_not_use_url_timestamp(self) -> None:
        final_url = "https://web.archive.org/web/20080512212653id_/http://example.test/x.jpg"
        body = _jpeg()
        item = {
            "actual_timestamp": "20080512212653",
            "cdx_digest": transport.cdx_digest(body),
            "cdx_length": len(body),
        }
        for headers in ({}, {"Memento-Datetime": "not-a-date"}):
            with self.subTest(headers=headers):
                self.assertIsNone(transport.memento_timestamp(headers, final_url))
                validation = transport.validate_replay(item, body, headers, final_url, 0, "image/jpeg")
                self.assertIsNone(validation["actual_timestamp"])

    def test_run_attempt_accepts_only_a_matching_replay(self) -> None:
        body = _jpeg()
        item = {
            "actual_timestamp": "20070218110247",
            "cdx_digest": base64.b32encode(hashlib.sha1(body).digest()).decode("ascii"),
            # CDX length is intentionally different from the decoded JPEG
            # body length: it is archived-record metadata, not wire length.
            "cdx_length": len(body) + 160,
            "original": "http://www.wow-europe.com:80/screenoftheday/screenoftheday/10702-01.jpg",
            "path": "/screenoftheday/screenoftheday/10702-01.jpg",
        }

        def fake_runner(command: list[str], **_: object) -> SimpleNamespace:
            header_path = Path(command[command.index("--dump-header") + 1])
            body_path = Path(command[command.index("--output") + 1])
            header_path.write_text(
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: image/jpeg\r\n"
                "Content-Length: " + str(len(body)) + "\r\n"
                "Memento-Datetime: Sun, 18 Feb 2007 11:02:47 GMT\r\n\r\n",
                encoding="iso-8859-1",
            )
            body_path.write_bytes(body)
            return SimpleNamespace(
                returncode=0,
                stdout=(f"200\thttps://web.archive.org/web/20070218110247id_/x\timage/jpeg\t{len(body)}\t0.1").encode(),
                stderr=b"",
            )

        with tempfile.TemporaryDirectory() as tmp:
            record = transport.run_attempt(
                item,
                transport="direct",
                rank=1,
                output=Path(tmp),
                remaining_bytes=transport.MAX_RESPONSE_BYTES,
                runner=fake_runner,
            )
        self.assertTrue(record["accepted"])
        self.assertEqual(record["transport"], "direct")
        self.assertEqual(record["failure_reasons"], [])
        self.assertEqual(record["validation"]["observed_cdx_digest"], item["cdx_digest"])
        self.assertFalse(record["validation"]["cdx_length_match"])

    def test_local_write_error_is_classified_without_proxy_fallback(self) -> None:
        record = {"failure_reasons": ["curl_exit_23", "local_write_error"], "status": None}
        self.assertEqual(transport.classify_failure(record), "local_write_error")

    def test_http_rate_limit_is_not_classified_as_digest(self) -> None:
        self.assertEqual(transport.classify_failure({"failure_reasons": ["http_429", "cdx_digest"], "status": 429}), "http")
        self.assertEqual(transport.classify_failure({"failure_reasons": ["curl_exit_28"], "status": 0}), "transport")

    def test_timeout_counts_partial_body_bytes(self) -> None:
        item = {
            "actual_timestamp": "20070218110247",
            "original": "http://www.wow-europe.com/screenoftheday/screenoftheday/partial.jpg",
            "path": "/screenoftheday/screenoftheday/partial.jpg",
        }

        def fake_runner(command: list[str], **_: object) -> SimpleNamespace:
            body_path = Path(command[command.index("--output") + 1])
            body_path.write_bytes(b"partial")
            raise subprocess.TimeoutExpired(command, timeout=1)

        with tempfile.TemporaryDirectory() as tmp:
            record = transport.run_attempt(
                item,
                transport="direct",
                rank=1,
                output=Path(tmp),
                remaining_bytes=transport.MAX_RESPONSE_BYTES,
                runner=fake_runner,
            )
        self.assertEqual(record["wire_bytes"], 7)
        self.assertEqual(record["failure_class"], "transport")

    def test_final_failure_streak_stops_after_three_proxy_rate_limits(self) -> None:
        items = [
            {
                "actual_timestamp": f"2008050100000{i}",
                "indexed_capture_timestamp": f"2008050100000{i}",
                "cdx_digest": "A" * 32,
                "cdx_length": 1,
                "cdx_metadata": "research/related-sites-20261014/regional-gallery/cdx/screen-assets-baseline.rows.json",
                "logical_url": f"http://www.wow-europe.com/screenoftheday/screenoftheday/streak-{i}.jpg",
                "original": f"http://www.wow-europe.com/screenoftheday/screenoftheday/streak-{i}.jpg",
                "path": f"/screenoftheday/screenoftheday/streak-{i}.jpg",
                "origin_namespace": "www.wow-europe.com",
                "temporal_class": "baseline_2008",
            }
            for i in range(1, 5)
        ]
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as tmp:
            output = Path(tmp) / "batch"
            calls: list[str] = []

            def fake_attempt(item: dict[str, object], *, transport: str, **_: object) -> dict[str, object]:
                calls.append(transport)
                return {
                    "transport": transport,
                    "status": 0 if transport == "direct" else 429,
                    "accepted": False,
                    "failure_class": "transport" if transport == "direct" else "http",
                    "failure_reasons": ["curl_exit_28"] if transport == "direct" else ["http_429"],
                    "wire_bytes": 0 if transport == "direct" else 162,
                }

            with patch.object(transport, "preflight", return_value={"kind": "test"}), \
                patch.object(transport, "load_routes", return_value=set()), \
                patch.object(transport, "load_old_retry_items", return_value=[]), \
                patch.object(transport, "parse_cdx_table", return_value=[]), \
                patch.object(transport, "select_new_candidates", return_value=items), \
                patch.object(transport, "run_attempt", side_effect=fake_attempt), \
                patch.object(transport, "workspace_bytes", return_value=100), \
                patch.object(transport, "drive_free_bytes", return_value=20_000_000_000):
                state = transport.run_batch(
                    cdx_path=ROOT / "offline/build-manifest.json",
                    old_meta_dir=ROOT,
                    manifest_path=ROOT / "offline/build-manifest.json",
                    provenance_path=ROOT / "offline/build-manifest.json",
                    output=output,
                    interval=0,
                )

        self.assertEqual(state["attempted"], 3)
        self.assertEqual(state["stop_reason"], "three_consecutive_final_failures:http")
        self.assertEqual(calls, ["direct", "proxy"] * 3)

    def test_successful_body_is_moved_out_of_attempt_directory(self) -> None:
        body = _jpeg()
        item = {
            "actual_timestamp": "20080501000000",
            "indexed_capture_timestamp": "20080501000000",
            "cdx_digest": base64.b32encode(hashlib.sha1(body).digest()).decode("ascii"),
            "cdx_length": len(body) + 200,
            "cdx_metadata": "research/related-sites-20261014/regional-gallery/cdx/screen-assets-baseline.rows.json",
            "logical_url": "http://www.wow-europe.com/screenoftheday/screenoftheday/moved.jpg",
            "original": "http://www.wow-europe.com/screenoftheday/screenoftheday/moved.jpg",
            "path": "/screenoftheday/screenoftheday/moved.jpg",
            "origin_namespace": "www.wow-europe.com",
            "temporal_class": "baseline_2008",
        }
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as tmp:
            output = Path(tmp) / "batch"

            def fake_attempt(_: dict[str, object], *, output: Path, **__: object) -> dict[str, object]:
                body_path = output / "entities" / "attempts" / "accepted.bin"
                body_path.parent.mkdir(parents=True, exist_ok=True)
                body_path.write_bytes(body)
                return {"transport": "direct", "status": 200, "accepted": True, "failure_class": None, "wire_bytes": len(body), "body_path": str(body_path)}

            with patch.object(transport, "preflight", return_value={"kind": "test"}), \
                patch.object(transport, "load_routes", return_value=set()), \
                patch.object(transport, "load_old_retry_items", return_value=[]), \
                patch.object(transport, "parse_cdx_table", return_value=[]), \
                patch.object(transport, "select_new_candidates", return_value=[item]), \
                patch.object(transport, "run_attempt", side_effect=fake_attempt), \
                patch.object(transport, "workspace_bytes", return_value=100), \
                patch.object(transport, "drive_free_bytes", return_value=20_000_000_000):
                state = transport.run_batch(
                    cdx_path=ROOT / "offline/build-manifest.json",
                    old_meta_dir=ROOT,
                    manifest_path=ROOT / "offline/build-manifest.json",
                    provenance_path=ROOT / "offline/build-manifest.json",
                    output=output,
                    interval=0,
                )

            final_path = next((output / "entities" / "raw").glob("*.jpg"))
            self.assertTrue(final_path.is_file())
            self.assertFalse((output / "entities" / "attempts" / "accepted.bin").exists())
            self.assertEqual(state["accepted"], 1)

    def test_retry_items_are_filtered_by_current_origin_route(self) -> None:
        existing_item = {"original": "http://www.wow-europe.com/screenoftheday/screenoftheday/already.jpg"}
        new_item = {"original": "http://wow-europe.com/screenoftheday/screenoftheday/new.jpg"}
        existing = {transport.route_key(existing_item["original"])}
        self.assertEqual(transport.filter_retry_items([existing_item, new_item], existing), [new_item])

    def test_nonempty_output_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as tmp:
            output = Path(tmp) / "batch"
            output.mkdir()
            (output / "sentinel").write_text("keep", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                transport.run_batch(
                    cdx_path=ROOT / "offline/build-manifest.json",
                    old_meta_dir=ROOT,
                    manifest_path=ROOT / "offline/build-manifest.json",
                    provenance_path=ROOT / "offline/build-manifest.json",
                    output=output,
                )


if __name__ == "__main__":
    unittest.main()

"""Real loopback HTTP checks for the portable MP3 seek path."""
import http.client
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AudioRangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / ".scratch", prefix="audio-range-test-")
        site = Path(cls.temp.name)
        (site / "export-provenance.json").write_text(json.dumps({"base_path": "/archive/"}), "utf-8")
        (site / "index.html").write_bytes(b"<title>Archive</title>")
        (site / "404.html").write_bytes(b"Missing")
        cls.payload = bytes(range(256)) * 2048
        (site / "episode.mp3").write_bytes(cls.payload)
        cls.process = subprocess.Popen(
            [sys.executable, "-B", str(ROOT / "tools/serve_pages_preview.py"), "--site", str(site), "--port", "0"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        line = cls.process.stdout.readline()
        cls.port = int(re.search(r"127\.0\.0\.1:(\d+)", line).group(1))

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=10)
        cls.process.stdout.close()
        cls.temp.cleanup()

    def request(self, target="episode.mp3", method="GET", range_value=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            connection.request(method, "/archive/" + target, headers={"Range": range_value} if range_value else {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_full_get_and_head(self):
        status, headers, body = self.request()
        self.assertEqual((status, headers["Content-Type"], body), (200, "audio/mpeg", self.payload))
        status, headers, body = self.request(method="HEAD", range_value="bytes=5-9")
        self.assertEqual((status, int(headers["Content-Length"]), body), (200, len(self.payload), b""))

    def test_seek_ranges(self):
        for value, first, last in [("bytes=1024-2047", 1024, 2047), ("bytes=524280-", 524280, 524287), ("bytes=-7", 524281, 524287), ("bytes=524280-999999", 524280, 524287)]:
            with self.subTest(value=value):
                status, headers, body = self.request(range_value=value)
                self.assertEqual(status, 206)
                self.assertEqual(headers["Content-Range"], f"bytes {first}-{last}/{len(self.payload)}")
                self.assertEqual(body, self.payload[first:last + 1])

    def test_unsatisfiable_ranges(self):
        for value in ["bytes=524288-", "bytes=9-2", "bytes=-0", "bytes=1-2,4-5", "bytes=nope", "bytes=" + "9" * 5000 + "-"]:
            with self.subTest(value=value):
                status, headers, body = self.request(range_value=value)
                self.assertEqual((status, headers["Content-Range"], body), (416, f"bytes */{len(self.payload)}", b""))

    def test_html_missing_and_outside_routes_keep_status(self):
        self.assertEqual(self.request("index.html", range_value="bytes=1-2")[::2], (200, b"<title>Archive</title>"))
        self.assertEqual(self.request("absent.mp3", range_value="bytes=1-2")[::2], (404, b"Missing"))
        self.assertEqual(self.request("../episode.mp3")[0], 404)


if __name__ == "__main__":
    unittest.main()

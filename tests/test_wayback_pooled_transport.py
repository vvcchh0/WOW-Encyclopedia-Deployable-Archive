"""Loopback and structural tests for the opt-in pooled Wayback transport."""

from __future__ import annotations

import base64
import gzip
import hashlib
import http.server
import socket
import threading
import time
import unittest
import urllib.parse
import zlib
from pathlib import Path
from unittest import mock
import sys


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import wayback_backup as wb  # noqa: E402
import wayback_pooled_transport as pooled  # noqa: E402


def digest(body: bytes) -> str:
    return base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")


class FixtureServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), FixtureHandler)
        self._lock = threading.Lock()
        self._ids: dict[socket.socket, int] = {}
        self.accepted = 0
        self.requests: list[dict[str, int | str]] = []

    def get_request(self):  # type: ignore[no-untyped-def]
        connection, address = super().get_request()
        with self._lock:
            self.accepted += 1
            self._ids[connection] = self.accepted
        return connection, address

    def connection_id(self, connection: socket.socket) -> int:
        with self._lock:
            return self._ids.get(connection, -1)

    def record(self, path: str, connection: socket.socket) -> None:
        with self._lock:
            self.requests.append({"path": path, "connection_id": self._ids.get(connection, -1)})

    def handle_error(self, request: object, client_address: object) -> None:
        # Deadline/stale-connection tests intentionally abort a local socket;
        # the client-side FetchError is the evidence of interest.
        return


class FixtureHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "PooledTransportFixture/1"

    def log_message(self, format: str, *args: object) -> None:
        return

    @property
    def fixture(self) -> FixtureServer:
        return self.server  # type: ignore[return-value]

    def _send(self, body: bytes, *, status: int = 200, headers: dict[str, str] | None = None, close: bool = False) -> None:
        self.send_response(status)
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close" if close else "keep-alive")
        self.end_headers()
        try:
            if body:
                self.wfile.write(body)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        if close:
            self.close_connection = True

    def do_GET(self) -> None:  # noqa: N802
        route = urllib.parse.urlsplit(self.path).path
        self.fixture.record(route, self.connection)
        if route == "/identity":
            self._send(b"identity fixture body")
        elif route == "/close":
            self._send(b"close fixture body", close=True)
        elif route == "/gzip":
            payload = b"gzip payload " * 80
            self._send(gzip.compress(payload, mtime=0), headers={"Content-Encoding": "gzip"})
        elif route == "/deflate":
            payload = b"deflate payload " * 80
            self._send(zlib.compress(payload), headers={"Content-Encoding": "deflate"})
        elif route == "/gzip-truncated":
            wire = gzip.compress(b"truncated payload", mtime=0)[:-5]
            self._send(wire, headers={"Content-Encoding": "gzip"})
        elif route == "/oversize":
            self._send(b"x" * 1024)
        elif route == "/redirect":
            self._send(b"", status=302, headers={"Location": "/identity"})
        elif route == "/external-redirect":
            self._send(b"", status=302, headers={"Location": "https://example.invalid/outside"})
        elif route == "/status500":
            self._send(b"fixture status error", status=500, headers={"X-Fixture": "status500"})
        elif route == "/slow":
            body = b"slow body"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.flush()
            time.sleep(0.45)
            try:
                self.wfile.write(body)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
        else:
            self._send(b"not found", status=404)


class FakeSocket:
    def __init__(self) -> None:
        self.timeouts: list[float | None] = []

    def settimeout(self, value: float | None) -> None:
        self.timeouts.append(value)


class FakeResponse:
    status = 200
    version = 11
    will_close = False

    def __init__(self, body: bytes = b"proxy fixture body") -> None:
        self.headers = {"Content-Length": str(len(body)), "Connection": "keep-alive"}
        self._body = body
        self._read = False
        self.closed = False

    def read(self, amount: int = -1) -> bytes:
        if self._read:
            return b""
        self._read = True
        return self._body

    def close(self) -> None:
        self.closed = True


class FakeHttpsConnection:
    instances: list["FakeHttpsConnection"] = []

    def __init__(self, host: str, port: int, *, timeout: float, context: object) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.context = context
        self.sock = FakeSocket()
        self.tunnel: tuple[str, int, dict[str, str]] | None = None
        self.requests: list[tuple[str, str, dict[str, str]]] = []
        self.closed = False
        self.__class__.instances.append(self)

    def set_tunnel(self, host: str, port: int, headers: dict[str, str]) -> None:
        self.tunnel = (host, port, headers)

    def request(self, method: str, target: str, headers: dict[str, str]) -> None:
        self.requests.append((method, target, headers))

    def getresponse(self) -> FakeResponse:
        return FakeResponse()

    def close(self) -> None:
        self.closed = True


class PooledTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = FixtureServer()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = int(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    @classmethod
    def url(cls, route: str) -> str:
        return f"http://127.0.0.1:{cls.port}{route}"

    @staticmethod
    def local_guard(url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        return parsed.scheme == "http" and parsed.hostname == "127.0.0.1"

    def make_transport(self) -> pooled.PooledArchiveTransport:
        return pooled.PooledArchiveTransport(proxies={}, url_guard=self.local_guard)

    def test_two_requests_reuse_one_connection(self) -> None:
        transport = self.make_transport()
        try:
            before = self.server.accepted
            first = transport.fetch_once(self.url("/identity"), 1024)
            second = transport.fetch_once(self.url("/identity"), 1024)
            self.assertEqual(first.body, second.body)
            self.assertEqual(self.server.accepted - before, 1)
            records = self.server.requests[-2:]
            self.assertEqual(records[0]["connection_id"], records[1]["connection_id"])
        finally:
            transport.close()

    def test_server_close_forces_new_connection(self) -> None:
        transport = self.make_transport()
        try:
            before = self.server.accepted
            transport.fetch_once(self.url("/close"), 1024)
            self.assertEqual(len(transport._connections), 0)
            transport.fetch_once(self.url("/identity"), 1024)
            self.assertEqual(self.server.accepted - before, 2)
            records = self.server.requests[-2:]
            self.assertNotEqual(records[0]["connection_id"], records[1]["connection_id"])
        finally:
            transport.close()

    def test_stale_connection_failure_is_visible_without_retry(self) -> None:
        transport = self.make_transport()
        try:
            transport.fetch_once(self.url("/identity"), 1024)
            entry = next(iter(transport._connections.values()))
            assert entry.connection.sock is not None
            entry.connection.sock.close()
            with self.assertRaises(wb.FetchError) as ctx:
                transport.fetch_once(self.url("/identity"), 1024)
            self.assertTrue(ctx.exception.reason.startswith("network_error:"))
            self.assertTrue(ctx.exception.exception_traceback)
        finally:
            transport.close()

    def test_gzip_deflate_truncation_size_and_digest(self) -> None:
        transport = self.make_transport()
        try:
            gzip_body = b"gzip payload " * 80
            gzip_result = transport.fetch_once(self.url("/gzip"), 16 * 1024 * 1024, expected_cdx_digest=digest(gzip_body))
            self.assertEqual(gzip_result.body, gzip_body)
            deflate_body = b"deflate payload " * 80
            self.assertEqual(transport.fetch_once(self.url("/deflate"), 16 * 1024 * 1024).body, deflate_body)
            with self.assertRaises(wb.FetchError) as ctx:
                transport.fetch_once(self.url("/gzip-truncated"), 16 * 1024 * 1024)
            self.assertIn("truncated_compressed_entity", ctx.exception.reason)
            with self.assertRaises(wb.FetchError) as ctx:
                transport.fetch_once(self.url("/oversize"), 128)
            self.assertTrue(ctx.exception.reason.startswith("object_exceeds_max_bytes"))
            with self.assertRaises(wb.FetchError) as ctx:
                transport.fetch_once(self.url("/identity"), 1024, expected_cdx_digest="A" * 32)
            self.assertIn("cdx_digest_mismatch", ctx.exception.reason)
        finally:
            transport.close()

    def test_deadline_updates_read_timeout(self) -> None:
        transport = self.make_transport()
        try:
            started = time.monotonic()
            with self.assertRaises(wb.DeadlineExceeded):
                transport.fetch_once(self.url("/slow"), 1024, timeout=2, deadline=time.monotonic() + 0.1)
            self.assertLess(time.monotonic() - started, 1.0)
        finally:
            transport.close()

    def test_deadline_does_not_extend_socket_timeout(self) -> None:
        response = mock.Mock()
        connection = mock.Mock()
        wrapped = pooled._DeadlineResponse(response, connection, time.monotonic() + 900, 2.5)
        wrapped.read(1)
        connection.sock.settimeout.assert_called_once_with(2.5)

    def test_redirect_guard_and_http_error_metadata(self) -> None:
        transport = self.make_transport()
        try:
            result = transport.fetch_once(self.url("/redirect"), 1024)
            self.assertTrue(result.final_url.endswith("/identity"))
            with self.assertRaises(wb.FetchError) as ctx:
                transport.fetch_once(self.url("/external-redirect"), 1024)
            self.assertEqual(ctx.exception.reason, "external_redirect_rejected")
            self.assertEqual(ctx.exception.status, 302)
            with self.assertRaises(wb.FetchError) as ctx:
                transport.fetch_once(self.url("/status500"), 1024)
            self.assertEqual(ctx.exception.status, 500)
            self.assertTrue(ctx.exception.retryable_site_failure)
            self.assertEqual(ctx.exception.headers.get("X-Fixture"), "status500")
            self.assertIn("fixture status error", ctx.exception.body_preview or "")
        finally:
            transport.close()

        archive_transport = pooled.PooledArchiveTransport(proxies={})
        with self.assertRaises(wb.FetchError) as ctx:
            archive_transport.fetch_once(self.url("/identity"), 1024)
        self.assertEqual(ctx.exception.reason, "archive_external_initial_url")

    def test_proxy_is_read_and_http_connect_is_configured(self) -> None:
        FakeHttpsConnection.instances.clear()
        with mock.patch.object(pooled.urllib.request, "getproxies", return_value={"https": "http://proxy.local:8080"}):
            transport = pooled.PooledArchiveTransport()
        self.assertEqual(transport.proxy_summary, {"scheme": "http", "host": "proxy.local", "port": 8080, "has_credentials": False})
        with mock.patch.object(pooled.http.client, "HTTPSConnection", FakeHttpsConnection):
            first = transport.fetch_once("https://web.archive.org/web/20080512000000id_/https://www.worldofwarcraft.com/", 1024)
            second = transport.fetch_once("https://web.archive.org/web/20080512000000id_/https://www.worldofwarcraft.com/", 1024)
        self.assertEqual(first.body, second.body)
        self.assertEqual(len(FakeHttpsConnection.instances), 1)
        self.assertIsNotNone(FakeHttpsConnection.instances[0].tunnel)
        assert FakeHttpsConnection.instances[0].tunnel is not None
        self.assertEqual(FakeHttpsConnection.instances[0].tunnel[0:2], ("web.archive.org", 443))
        self.assertEqual(len(FakeHttpsConnection.instances[0].requests), 2)
        transport.close()

    def test_unsupported_proxy_can_fail_or_explicitly_fallback(self) -> None:
        transport = pooled.PooledArchiveTransport(proxies={"https": "socks5://127.0.0.1:1"})
        with self.assertRaises(pooled.PooledTransportUnsupported):
            transport.fetch_once("https://web.archive.org/web/20080512000000id_/https://www.worldofwarcraft.com/", 1024)

        fallback = pooled.PooledArchiveTransport(proxies={"https": "socks5://127.0.0.1:1"}, fallback_to_urllib=True)
        sentinel = object()
        with mock.patch.object(wb, "fetch_once", return_value=sentinel) as original:
            result = fallback.fetch_once("https://web.archive.org/web/20080512000000id_/https://www.worldofwarcraft.com/", 1024)
        self.assertIs(result, sentinel)
        self.assertEqual(len(fallback.fallback_events), 1)
        original.assert_called_once()

    def test_module_entrypoint_is_compatibility_delegate_without_pool(self) -> None:
        sentinel = object()
        with mock.patch.object(wb, "fetch_once", return_value=sentinel) as original:
            result = pooled.fetch_once(
                "https://web.archive.org/web/20080512000000id_/https://www.worldofwarcraft.com/",
                1024,
                timeout=30,
            )
        self.assertIs(result, sentinel)
        original.assert_called_once()


if __name__ == "__main__":
    unittest.main()


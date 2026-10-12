"""Opt-in pooled HTTP transport for bounded Wayback downloads.

This module is deliberately separate from :mod:`wayback_backup`.  It is a
reviewable candidate, not the default downloader.  A ``PooledArchiveTransport``
instance belongs to one worker/request stream.  It keeps at most one
``http.client`` connection per target origin (or CONNECT proxy tunnel), while
delegating decoded-byte, object-size, and CDX digest handling to the existing
``wayback_backup._read_entity`` implementation.

The production default only permits ``https://web.archive.org``.  Tests can
inject a loopback URL guard; doing so is the only reason this module can be
used against a local fixture without touching the network.
"""

from __future__ import annotations

import base64
import http.client
import socket
import ssl
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
import wayback_backup as wb  # noqa: E402


REDIRECT_CODES = {301, 302, 303, 307, 308}
DEFAULT_MAX_REDIRECTS = 10
REDIRECT_DRAIN_BYTES = 64 * 1024
DEFAULT_USER_AGENT = "WOW-Encyclopedia-Backup/1.0"
DEADLINE_TIMEOUT_TOLERANCE = 0.01


class PooledTransportUnsupported(wb.BackupError):
    """The configured proxy/transport cannot be represented safely here."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class _Proxy:
    scheme: str
    host: str
    port: int
    authorization: str | None = None

    @property
    def summary(self) -> dict[str, Any]:
        # Never expose proxy credentials in reports or exception messages.
        return {"scheme": self.scheme, "host": self.host, "port": self.port, "has_credentials": self.authorization is not None}


@dataclass
class _PooledConnection:
    connection: http.client.HTTPConnection
    key: tuple[Any, ...]
    target_url: str


def _authority(parsed: urllib.parse.SplitResult) -> str:
    if parsed.hostname is None:
        raise PooledTransportUnsupported("target URL has no hostname")
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    port = parsed.port
    if port is None or port == (443 if parsed.scheme.casefold() == "https" else 80):
        return host
    return f"{host}:{port}"


def _normalise_proxy(raw: str) -> _Proxy:
    value = str(raw).strip()
    if "://" not in value:
        value = "http://" + value
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError as exc:
        raise PooledTransportUnsupported("invalid_proxy_url") from exc
    scheme = parsed.scheme.casefold()
    if scheme != "http":
        raise PooledTransportUnsupported(f"unsupported_proxy_scheme:{scheme or 'missing'}")
    if parsed.hostname is None:
        raise PooledTransportUnsupported("proxy_url_has_no_host")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise PooledTransportUnsupported("proxy_url_has_path_or_query")
    try:
        port = parsed.port or 80
    except ValueError as exc:
        raise PooledTransportUnsupported("proxy_url_has_invalid_port") from exc
    authorization: str | None = None
    if parsed.username is not None or parsed.password is not None:
        user = urllib.parse.unquote(parsed.username or "")
        password = urllib.parse.unquote(parsed.password or "")
        token = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
        authorization = f"Basic {token}"
    return _Proxy(scheme=scheme, host=parsed.hostname, port=port, authorization=authorization)


def _pick_proxy(proxies: Mapping[str, str]) -> _Proxy | None:
    # urllib's getproxies() may return upper-case keys on Windows.  Prefer an
    # HTTPS-specific proxy for Wayback HTTPS, then the HTTP proxy fallback.
    folded = {str(key).casefold(): value for key, value in proxies.items() if value}
    raw = folded.get("https") or folded.get("http")
    if not raw:
        return None
    return _normalise_proxy(str(raw))


def _connection_header_is_close(headers: Mapping[str, str]) -> bool:
    value = (wb._header_value(headers, "Connection") or "").casefold()
    return any(part.strip() == "close" for part in value.split(","))


class _DeadlineResponse:
    """Small response adapter that refreshes socket timeout before each read."""

    def __init__(self, response: http.client.HTTPResponse, connection: http.client.HTTPConnection, deadline: float | None, timeout: float) -> None:
        self._response = response
        self._connection = connection
        self._deadline = deadline
        self._timeout = timeout
        self.headers = response.headers

    def _set_read_timeout(self) -> None:
        if self._deadline is None:
            return
        remaining = self._deadline - time.monotonic()
        if remaining <= 0:
            raise wb.DeadlineExceeded("transport deadline exceeded while reading entity")
        sock_obj = getattr(self._connection, "sock", None)
        if sock_obj is not None:
            sock_obj.settimeout(min(self._timeout, remaining))

    def read(self, amount: int = -1) -> bytes:
        self._set_read_timeout()
        try:
            return self._response.read(amount)
        except (socket.timeout, TimeoutError) as exc:
            if self._deadline is not None and time.monotonic() + DEADLINE_TIMEOUT_TOLERANCE >= self._deadline:
                raise wb.DeadlineExceeded("transport deadline exceeded while reading entity") from exc
            raise

    def close(self) -> None:
        self._response.close()


class PooledArchiveTransport:
    """Opt-in per-worker connection pool with Archive-only URL policy.

    ``proxies=None`` reads the process's existing settings with
    ``urllib.request.getproxies``.  Tests or callers that intentionally want a
    direct fixture may pass ``proxies={}``.  Only plain HTTP proxies are
    supported: HTTPS Archive targets use an HTTP CONNECT tunnel and the target
    TLS context remains the standard verifying context.  Unsupported proxy
    forms fail explicitly unless ``fallback_to_urllib=True`` is selected.
    """

    def __init__(
        self,
        *,
        proxies: Mapping[str, str] | None = None,
        url_guard: Callable[[str], bool] | None = None,
        ssl_context: ssl.SSLContext | None = None,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        fallback_to_urllib: bool = False,
    ) -> None:
        self.proxies = dict(urllib.request.getproxies() if proxies is None else proxies)
        self.url_guard = url_guard or wb._is_archive_url
        self.ssl_context = ssl_context or ssl.create_default_context()
        self.max_redirects = max_redirects
        self.fallback_to_urllib = fallback_to_urllib
        self.fallback_events: list[dict[str, str]] = []
        self._connections: dict[tuple[Any, ...], _PooledConnection] = {}
        self._proxy_error: PooledTransportUnsupported | None = None
        try:
            self.proxy = _pick_proxy(self.proxies)
        except PooledTransportUnsupported as exc:
            self.proxy = None
            self._proxy_error = exc

    @property
    def proxy_summary(self) -> dict[str, Any] | None:
        return self.proxy.summary if self.proxy is not None else None

    @property
    def proxy_error(self) -> str | None:
        return self._proxy_error.reason if self._proxy_error is not None else None

    def close(self) -> None:
        entries = list(self._connections.values())
        self._connections.clear()
        for entry in entries:
            try:
                entry.connection.close()
            except OSError:
                pass

    def __enter__(self) -> "PooledArchiveTransport":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback_value: Any) -> None:
        self.close()

    @staticmethod
    def _remaining(timeout: float, deadline: float | None) -> float:
        if deadline is None:
            return max(0.001, float(timeout))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise wb.DeadlineExceeded("transport deadline exceeded before request")
        return max(0.001, min(float(timeout), remaining))

    @staticmethod
    def _set_timeout(connection: http.client.HTTPConnection, timeout: float) -> None:
        connection.timeout = timeout
        sock_obj = getattr(connection, "sock", None)
        if sock_obj is not None:
            sock_obj.settimeout(timeout)

    def _target_key(self, parsed: urllib.parse.SplitResult) -> tuple[Any, ...]:
        if parsed.hostname is None:
            raise PooledTransportUnsupported("target URL has no hostname")
        target_port = parsed.port or (443 if parsed.scheme.casefold() == "https" else 80)
        if self.proxy is None:
            return ("direct", parsed.scheme.casefold(), parsed.hostname.casefold(), target_port)
        # CONNECT tunnels cannot be retargeted after establishment. Include the
        # origin in the key even when the same proxy serves several hosts.
        return (
            "connect",
            self.proxy.host.casefold(),
            self.proxy.port,
            parsed.scheme.casefold(),
            parsed.hostname.casefold(),
            target_port,
        )

    def _get_connection(self, parsed: urllib.parse.SplitResult, timeout: float) -> _PooledConnection:
        if parsed.scheme.casefold() not in {"http", "https"} or parsed.hostname is None:
            raise PooledTransportUnsupported("unsupported_target_scheme_or_host")
        key = self._target_key(parsed)
        existing = self._connections.get(key)
        if existing is not None:
            self._set_timeout(existing.connection, timeout)
            return existing
        target_port = parsed.port or (443 if parsed.scheme.casefold() == "https" else 80)
        if self.proxy is None:
            if parsed.scheme.casefold() == "https":
                connection: http.client.HTTPConnection = http.client.HTTPSConnection(
                    parsed.hostname,
                    target_port,
                    timeout=timeout,
                    context=self.ssl_context,
                )
            else:
                connection = http.client.HTTPConnection(parsed.hostname, target_port, timeout=timeout)
        else:
            if parsed.scheme.casefold() != "https":
                raise PooledTransportUnsupported("proxy_forwarding_for_http_not_enabled")
            # HTTPSConnection opens a plain socket to the HTTP proxy, sends
            # CONNECT, then wraps the tunnel in the verifying target context.
            connection = http.client.HTTPSConnection(
                self.proxy.host,
                self.proxy.port,
                timeout=timeout,
                context=self.ssl_context,
            )
            tunnel_headers = {"Host": _authority(parsed)}
            if self.proxy.authorization:
                tunnel_headers["Proxy-Authorization"] = self.proxy.authorization
            connection.set_tunnel(parsed.hostname, target_port, headers=tunnel_headers)
        entry = _PooledConnection(connection=connection, key=key, target_url=parsed.geturl())
        self._connections[key] = entry
        return entry

    def _drop_connection(self, key: tuple[Any, ...]) -> None:
        entry = self._connections.pop(key, None)
        if entry is not None:
            try:
                entry.connection.close()
            except OSError:
                pass

    def _drain_redirect(
        self,
        response: http.client.HTTPResponse,
        connection: http.client.HTTPConnection,
        *,
        max_bytes: int,
        deadline: float | None,
        timeout: float,
    ) -> None:
        content_length: int | None = None
        raw_length = wb._header_value(wb._headers_dict(response.headers), "Content-Length")
        if raw_length:
            try:
                content_length = int(raw_length)
            except ValueError:
                raise wb.FetchError("redirect_invalid_content_length")
            if content_length < 0:
                raise wb.FetchError("redirect_invalid_content_length")
            if content_length > min(max_bytes, REDIRECT_DRAIN_BYTES):
                raise wb.FetchError("redirect_body_exceeds_drain_limit")
        limit = min(max_bytes, REDIRECT_DRAIN_BYTES)
        wrapped = _DeadlineResponse(response, connection, deadline, timeout)
        data = wrapped.read(limit + 1)
        if len(data) > limit:
            raise wb.FetchError("redirect_body_exceeds_drain_limit")
        if content_length is not None and len(data) != content_length:
            raise wb.FetchError("redirect_body_truncated")

    def fetch_once(
        self,
        requested_url: str,
        max_bytes: int,
        on_chunk: Callable[[int], None] | None = None,
        *,
        timeout: int | float = wb.DEFAULT_TIMEOUT_SECONDS,
        expected_cdx_digest: str | None = None,
        deadline: float | None = None,
    ) -> wb.FetchResult:
        """Fetch one URL with one attempt and pooled keep-alive connections."""

        if not self.url_guard(requested_url):
            raise wb.FetchError("archive_external_initial_url", final_url=requested_url)
        if max_bytes < 0:
            raise wb.FetchError("invalid_max_bytes")
        if self._proxy_error is not None:
            if not self.fallback_to_urllib:
                raise self._proxy_error
            self.fallback_events.append({"requested_url": requested_url, "reason": self._proxy_error.reason})
            fallback_callback = on_chunk
            if deadline is not None:
                if time.monotonic() >= deadline:
                    raise wb.DeadlineExceeded("transport deadline exceeded before urllib fallback")

                def fallback_progress(decoded_bytes: int) -> None:
                    if time.monotonic() >= deadline:
                        raise wb.DeadlineExceeded("transport deadline exceeded during urllib fallback")
                    if on_chunk is not None:
                        on_chunk(decoded_bytes)

                fallback_callback = fallback_progress
            return wb.fetch_once(
                requested_url,
                max_bytes,
                fallback_callback,
                timeout=max(1, int(round(float(timeout)))),
                expected_cdx_digest=expected_cdx_digest,
            )

        current_url = requested_url
        for redirect_count in range(self.max_redirects + 1):
            if not self.url_guard(current_url):
                raise wb.FetchError("archive_external_redirect_target", final_url=current_url)
            parsed = urllib.parse.urlsplit(current_url)
            response: http.client.HTTPResponse | None = None
            entry: _PooledConnection | None = None
            headers: dict[str, str] = {}
            try:
                remaining = self._remaining(float(timeout), deadline)
                entry = self._get_connection(parsed, remaining)
                self._set_timeout(entry.connection, remaining)
                target = urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
                entry.connection.request(
                    "GET",
                    target,
                    headers={
                        "Accept-Encoding": "identity",
                        "User-Agent": DEFAULT_USER_AGENT,
                        "Host": _authority(parsed),
                    },
                )
                response = entry.connection.getresponse()
                status = int(response.status)
                headers = wb._headers_dict(response.headers)
                if status in REDIRECT_CODES:
                    location = wb._header_value(headers, "Location")
                    if not location:
                        raise wb.FetchError("redirect_missing_location", status=status, final_url=current_url, headers=headers)
                    next_url = urllib.parse.urljoin(current_url, location)
                    if not self.url_guard(next_url):
                        raise wb.FetchError(
                            "external_redirect_rejected",
                            status=status,
                            final_url=next_url,
                            headers=headers,
                            body_preview=f"redirect target: {next_url}",
                        )
                    self._drain_redirect(response, entry.connection, max_bytes=max_bytes, deadline=deadline, timeout=float(timeout))
                    response.close()
                    if getattr(response, "will_close", False) or _connection_header_is_close(headers):
                        self._drop_connection(entry.key)
                    current_url = next_url
                    continue

                wrapped = _DeadlineResponse(response, entry.connection, deadline, float(timeout))
                interpretation: dict[str, str] = {}

                def progress(decoded_bytes: int) -> None:
                    if deadline is not None and time.monotonic() >= deadline:
                        raise wb.DeadlineExceeded("transport deadline exceeded while reading entity")
                    if on_chunk is not None:
                        on_chunk(decoded_bytes)

                try:
                    body = wb._read_entity(
                        wrapped,
                        max_bytes,
                        progress,
                        expected_cdx_digest=expected_cdx_digest,
                        interpretation=interpretation,
                    )
                except wb.FetchError as exc:
                    raise wb.FetchError(
                        exc.reason,
                        status=status,
                        final_url=current_url,
                        headers=headers,
                        retryable_site_failure=exc.retryable_site_failure,
                        body_preview=exc.body_preview,
                    ) from exc
                finally:
                    response.close()

                if not self.url_guard(current_url):
                    raise wb.FetchError("archive_external_final_url", status=status, final_url=current_url, headers=headers)
                if status != 200:
                    marker = wb._wayback_error_marker(body)
                    reason = f"http_status:{status}"
                    if marker:
                        reason = f"wayback_error_page:{marker}"
                    raise wb.FetchError(
                        reason,
                        status=status,
                        final_url=current_url,
                        headers=headers,
                        retryable_site_failure=(status == 429 or 500 <= status <= 599),
                        body_preview=wb._body_preview(body),
                    )
                marker = wb._wayback_error_marker(body)
                if marker:
                    raise wb.FetchError(f"wayback_error_page:{marker}", status=status, final_url=current_url, headers=headers, body_preview=wb._body_preview(body))
                if getattr(response, "will_close", False) or _connection_header_is_close(headers):
                    self._drop_connection(entry.key)
                return wb.FetchResult(
                    requested_url=requested_url,
                    final_url=current_url,
                    status=status,
                    headers=headers,
                    body=body,
                    content_encoding_interpretation=interpretation.get("value"),
                )
            except wb.DeadlineExceeded:
                if response is not None:
                    response.close()
                if entry is not None:
                    self._drop_connection(entry.key)
                raise
            except wb.FetchError:
                if response is not None:
                    response.close()
                if entry is not None:
                    self._drop_connection(entry.key)
                raise
            except (urllib.error.HTTPError, OSError, TimeoutError, socket.timeout, http.client.HTTPException) as exc:
                if response is not None:
                    response.close()
                if entry is not None:
                    self._drop_connection(entry.key)
                if deadline is not None and time.monotonic() + DEADLINE_TIMEOUT_TOLERANCE >= deadline:
                    raise wb.DeadlineExceeded("transport deadline exceeded during response") from exc
                raise wb.FetchError(
                    f"network_error:{exc}",
                    final_url=current_url,
                    retryable_site_failure=True,
                    exception_traceback="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
                ) from exc
        raise wb.FetchError("too_many_redirects", final_url=current_url)


def fetch_once(
    requested_url: str,
    max_bytes: int,
    on_chunk: Callable[[int], None] | None = None,
    *,
    timeout: int | float = wb.DEFAULT_TIMEOUT_SECONDS,
    expected_cdx_digest: str | None = None,
    deadline: float | None = None,
    transport: PooledArchiveTransport | None = None,
) -> wb.FetchResult:
    """Compatibility entry point; pooling is opt-in through ``transport``.

    Without an explicit transport this delegates to the unchanged downloader,
    so importing this module cannot silently alter production behavior.
    """

    if transport is None:
        return wb.fetch_once(
            requested_url,
            max_bytes,
            on_chunk,
            timeout=int(timeout),
            expected_cdx_digest=expected_cdx_digest,
        )
    return transport.fetch_once(
        requested_url,
        max_bytes,
        on_chunk,
        timeout=timeout,
        expected_cdx_digest=expected_cdx_digest,
        deadline=deadline,
    )


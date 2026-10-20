"""Pure, bounded parsing for one legacy Common Crawl ARC gzip member.

The parser deliberately treats the bytes after the stored HTTP header as an
opaque payload.  ARC framing is decoded, but ``Content-Encoding`` and
``Transfer-Encoding`` in the captured response are only metadata: following
either header would change the bytes whose digest is being checked.
"""

from __future__ import annotations

import base64
import hashlib
import re
import zlib
from dataclasses import dataclass


DEFAULT_MAX_DECOMPRESSED_BYTES = 1 << 20
_ARC_FIRST_LINE = re.compile(
    rb"^(\S+) (\S+) (\d{14}) (\S+) ([0-9]+)$"
)
_HTTP_STATUS = re.compile(rb"^HTTP/\d(?:\.\d)? ([1-5][0-9]{2})(?: (.*))?$")


class ArcParseError(ValueError):
    """The compressed member or its ARC/HTTP framing is invalid."""


class ArcFramingError(ArcParseError):
    """The ARC record length or permitted trailing newline is invalid."""


class ArcValidationError(ArcParseError):
    """A caller-supplied URL, date, status, or digest does not match."""


@dataclass(frozen=True)
class StoredHttpResponse:
    """The stored HTTP header block and its byte-preserved payload."""

    raw_header: bytes
    status_line: bytes
    status: int
    headers: tuple[tuple[bytes, bytes], ...]
    payload: bytes

    def values(self, name: bytes | str) -> tuple[bytes, ...]:
        """Return stored values for *name* without touching the payload."""

        wanted = name.encode("ascii") if isinstance(name, str) else name
        wanted = wanted.lower()
        return tuple(value for key, value in self.headers if key == wanted)


@dataclass(frozen=True)
class ArcRecord:
    """A parsed ARC record with the original payload bytes preserved."""

    url: str
    ip: str
    timestamp: str
    mime: str
    declared_length: int
    record_body: bytes
    trailing: bytes
    http: StoredHttpResponse
    payload_sha1_base32: str
    decompressed_bytes: int


def _sha1_base32(payload: bytes) -> str:
    return base64.b32encode(hashlib.sha1(payload).digest()).decode("ascii").rstrip("=")


def _normalise_digest(value: str) -> str:
    return value.strip().rstrip("=").upper()


def decompress_gzip_member(
    compressed: bytes,
    *,
    max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES,
) -> bytes:
    """Decompress exactly one gzip member under a hard output bound.

    ``zlib`` stops at the end of the first gzip member.  Any unused input is
    rejected so a caller cannot accidentally parse a second member or an
    unbounded suffix as part of the same ARC record.
    """

    if max_decompressed_bytes <= 0:
        raise ValueError("max_decompressed_bytes must be positive")
    if not isinstance(compressed, (bytes, bytearray, memoryview)):
        raise TypeError("compressed must be bytes-like")

    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    output = bytearray()
    view = memoryview(compressed)
    try:
        for offset in range(0, len(view), 64 * 1024):
            remaining = max_decompressed_bytes + 1 - len(output)
            if remaining <= 0:
                raise ArcParseError("decompressed output exceeds configured limit")
            piece = decompressor.decompress(view[offset : offset + 64 * 1024], remaining)
            output.extend(piece)
            if len(output) > max_decompressed_bytes or decompressor.unconsumed_tail:
                raise ArcParseError("decompressed output exceeds configured limit")
        remaining = max_decompressed_bytes + 1 - len(output)
        if remaining <= 0:
            raise ArcParseError("decompressed output exceeds configured limit")
        output.extend(decompressor.flush(remaining))
    except (zlib.error, ValueError) as exc:
        if isinstance(exc, ArcParseError):
            raise
        raise ArcParseError(f"invalid gzip member: {exc}") from exc

    if len(output) > max_decompressed_bytes:
        raise ArcParseError("decompressed output exceeds configured limit")
    if not decompressor.eof:
        raise ArcParseError("truncated gzip member")
    if decompressor.unused_data:
        raise ArcParseError("unexpected bytes after gzip member")
    return bytes(output)


def _parse_http_record(record_body: bytes) -> StoredHttpResponse:
    separator = record_body.find(b"\r\n\r\n")
    if separator < 0:
        raise ArcFramingError("stored HTTP header block has no CRLFCRLF separator")
    raw_header = record_body[:separator]
    payload = record_body[separator + 4 :]
    lines = raw_header.split(b"\r\n")
    if not lines or not lines[0]:
        raise ArcParseError("stored HTTP status line is missing")
    status_match = _HTTP_STATUS.fullmatch(lines[0])
    if status_match is None:
        raise ArcParseError("stored HTTP status line is malformed")
    headers: list[tuple[bytes, bytes]] = []
    for line in lines[1:]:
        if not line or b":" not in line:
            raise ArcParseError("stored HTTP header line is malformed")
        name, value = line.split(b":", 1)
        if not name or any(byte in b" \t" for byte in name):
            raise ArcParseError("stored HTTP header name is malformed")
        headers.append((name.lower(), value.lstrip(b" \t")))
    return StoredHttpResponse(
        raw_header=raw_header,
        status_line=lines[0],
        status=int(status_match.group(1)),
        headers=tuple(headers),
        payload=payload,
    )


def parse_arc_record(
    decompressed: bytes,
    *,
    expected_url: str | None = None,
    expected_timestamp: str | None = None,
    expected_status: int | None = None,
    expected_digest: str | None = None,
) -> ArcRecord:
    """Parse one decompressed ARC record and validate optional expectations."""

    if not isinstance(decompressed, (bytes, bytearray, memoryview)):
        raise TypeError("decompressed must be bytes-like")
    data = bytes(decompressed)
    line_end = data.find(b"\n")
    if line_end < 0:
        raise ArcFramingError("ARC first line is missing")
    first_line = data[:line_end]
    if first_line.endswith(b"\r"):
        first_line = first_line[:-1]
    match = _ARC_FIRST_LINE.fullmatch(first_line)
    if match is None:
        raise ArcFramingError("ARC first line must be URL IP timestamp MIME declaredLength")
    try:
        url = match.group(1).decode("ascii")
        ip = match.group(2).decode("ascii")
        timestamp = match.group(3).decode("ascii")
        mime = match.group(4).decode("ascii")
    except UnicodeDecodeError as exc:
        raise ArcFramingError("ARC first line is not ASCII") from exc
    declared_length = int(match.group(5))

    remainder = data[line_end + 1 :]
    if len(remainder) < declared_length:
        raise ArcFramingError(
            f"ARC record is truncated: declared {declared_length}, got {len(remainder)}"
        )
    record_body = remainder[:declared_length]
    trailing = remainder[declared_length:]
    if trailing not in (b"", b"\n"):
        raise ArcFramingError("only one ARC trailing newline is permitted")
    http = _parse_http_record(record_body)
    digest = _sha1_base32(http.payload)

    if expected_url is not None and url != expected_url:
        raise ArcValidationError(f"ARC URL mismatch: {url!r}")
    if expected_timestamp is not None and timestamp != expected_timestamp:
        raise ArcValidationError(f"ARC timestamp mismatch: {timestamp!r}")
    if expected_status is not None and http.status != expected_status:
        raise ArcValidationError(f"stored HTTP status mismatch: {http.status}")
    if expected_digest is not None and digest != _normalise_digest(expected_digest):
        raise ArcValidationError(f"payload digest mismatch: {digest}")

    return ArcRecord(
        url=url,
        ip=ip,
        timestamp=timestamp,
        mime=mime,
        declared_length=declared_length,
        record_body=record_body,
        trailing=trailing,
        http=http,
        payload_sha1_base32=digest,
        decompressed_bytes=len(data),
    )


def parse_arc_gzip_member(
    compressed: bytes,
    *,
    expected_url: str | None = None,
    expected_timestamp: str | None = None,
    expected_status: int | None = None,
    expected_digest: str | None = None,
    max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES,
) -> ArcRecord:
    """Decompress and parse one bounded ARC gzip member."""

    data = decompress_gzip_member(
        compressed, max_decompressed_bytes=max_decompressed_bytes
    )
    return parse_arc_record(
        data,
        expected_url=expected_url,
        expected_timestamp=expected_timestamp,
        expected_status=expected_status,
        expected_digest=expected_digest,
    )


__all__ = [
    "ArcFramingError",
    "ArcParseError",
    "ArcRecord",
    "ArcValidationError",
    "DEFAULT_MAX_DECOMPRESSED_BYTES",
    "StoredHttpResponse",
    "decompress_gzip_member",
    "parse_arc_gzip_member",
    "parse_arc_record",
]

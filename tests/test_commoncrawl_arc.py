from __future__ import annotations

import gzip
from pathlib import Path

import pytest

from tools.commoncrawl_arc import (
    ArcFramingError,
    ArcParseError,
    ArcValidationError,
    parse_arc_gzip_member,
)


ROOT = Path(__file__).resolve().parents[1]
REAL_BODY = (
    ROOT
    / "research/continuous-recovery-20261020/network/commoncrawl-arc01/raw/attempt01-direct.body"
)
EXPECTED_URL = "http://www.worldofwarcraft.com/info/encyclopedia/index.xml"
EXPECTED_TIMESTAMP = "20080720173556"
EXPECTED_DIGEST = "J5QKGA7VRIUFZPBPEDKOT6REERJJJJXS"


def _synthetic_member(
    *,
    url: str = "http://example.test/page.html",
    timestamp: str = "20080720173556",
    status: int = 200,
    payload: bytes = b"4\r\nAB\r\n0\r\n\r\n",
    trailer: bytes = b"\n",
    declared_delta: int = 0,
) -> bytes:
    status_line = f"HTTP/1.1 {status} Example".encode("ascii")
    record_body = (
        status_line
        + b"\r\nContent-Encoding: gzip\r\nTransfer-Encoding: chunked\r\n"
        + b"X-Test: literal\r\n\r\n"
        + payload
    )
    declared = len(record_body) + declared_delta
    first = f"{url} 192.0.2.10 {timestamp} text/html {declared}\n".encode("ascii")
    return gzip.compress(first + record_body + trailer)


@pytest.mark.skipif(not REAL_BODY.is_file(), reason="private fixture is unavailable")
def test_real_accepted_commoncrawl_range_is_parsed_without_rewriting_payload() -> None:
    compressed = REAL_BODY.read_bytes()
    assert len(compressed) == 6601

    record = parse_arc_gzip_member(
        compressed,
        expected_url=EXPECTED_URL,
        expected_timestamp=EXPECTED_TIMESTAMP,
        expected_status=200,
        expected_digest=EXPECTED_DIGEST,
    )

    assert record.ip == "12.129.242.22"
    assert record.mime == "text/html"
    assert record.declared_length == 52955
    assert len(record.record_body) == 52955
    assert record.trailing == b"\n"
    assert record.decompressed_bytes == 53060
    assert len(record.http.payload) == 52400
    assert record.http.payload.startswith(b"<?xml-stylesheet")
    assert record.http.values("content-encoding") == (b"gzip",)
    assert record.http.values("transfer-encoding") == (b"chunked",)
    assert record.payload_sha1_base32 == EXPECTED_DIGEST


def test_synthetic_record_accepts_only_one_arc_newline_and_preserves_bytes() -> None:
    payload = b"4\r\nAB\r\n0\r\n\r\n"
    member = _synthetic_member(payload=payload)
    record = parse_arc_gzip_member(
        member,
        expected_url="http://example.test/page.html",
        expected_timestamp="20080720173556",
        expected_status=200,
    )
    assert record.http.payload == payload
    assert record.trailing == b"\n"

    with pytest.raises(ArcFramingError, match="only one ARC trailing newline"):
        parse_arc_gzip_member(_synthetic_member(payload=payload, trailer=b"\r\n"))


def test_truncated_declared_arc_record_is_rejected() -> None:
    with pytest.raises(ArcFramingError, match="truncated"):
        parse_arc_gzip_member(_synthetic_member(declared_delta=1, trailer=b""))


def test_decompression_cap_is_enforced_before_large_payload_is_returned() -> None:
    with pytest.raises(ArcParseError, match="exceeds configured limit"):
        parse_arc_gzip_member(
            _synthetic_member(payload=b"x" * 512), max_decompressed_bytes=128
        )


@pytest.mark.parametrize(
    ("keyword", "value"),
    [
        ("url", "http://example.test/other.html"),
        ("timestamp", "20080721000000"),
        ("status", 404),
        ("digest", "A" * 32),
    ],
)
def test_expected_identity_and_digest_mismatches_are_rejected(keyword: str, value: object) -> None:
    member = _synthetic_member()
    kwargs = {
        "expected_url": None,
        "expected_timestamp": None,
        "expected_status": None,
        "expected_digest": None,
    }
    kwargs[f"expected_{keyword}"] = value
    with pytest.raises(ArcValidationError):
        parse_arc_gzip_member(member, **kwargs)


def test_extra_first_line_field_is_rejected() -> None:
    member = _synthetic_member()
    raw = gzip.decompress(member)
    first, rest = raw.split(b"\n", 1)
    broken = gzip.compress(first + b" extra\n" + rest)
    with pytest.raises(ArcFramingError, match="first line"):
        parse_arc_gzip_member(broken)

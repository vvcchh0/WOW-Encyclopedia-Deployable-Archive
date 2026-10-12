"""Bounded, resumable backups of Wayback identity replays.

The command line interface deliberately has no crawling logic.  It consumes a
finite JSON plan and stores successful HTTP entity bytes in ZIP volumes while
keeping one manifest record for every planned URL/timestamp relationship.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import datetime as _datetime
import email.utils
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import socket
import sys
import tempfile
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
import zlib
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence


ARCHIVE_HOST = "web.archive.org"
ARCHIVE_SCHEME = "https"
DEFAULT_MAX_BYTES = 14_000_000_000
DEFAULT_MIN_FREE_BYTES = 10_737_418_240
DEFAULT_OBJECT_BYTES = 16 * 1024 * 1024
DEFAULT_VOLUME_BYTES = 64 * 1024 * 1024
DEFAULT_VOLUME_OBJECTS = 100
DEFAULT_RESERVE_BYTES = 256 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRY_DELAY_SECONDS = 0.25
MAX_RETRY_AFTER_SECONDS = 30.0
MAX_ATTEMPTS_PER_ITEM = 2
CHUNK_BYTES = 64 * 1024
ZIP_WRITE_HEADROOM = 1 * 1024 * 1024
TIMESTAMP_RE = re.compile(r"^\d{14}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VOLUME_RE = re.compile(r"^objects-(\d+)\.zip$")


class BackupError(Exception):
    """Base class for errors that should be reported by the CLI."""


class PlanError(BackupError):
    pass


class RecoveryError(BackupError):
    pass


class BudgetExceeded(BackupError):
    pass


class DeadlineExceeded(BackupError):
    pass


class FetchError(BackupError):
    """A failed HTTP attempt with enough metadata for a manifest/error log."""

    def __init__(
        self,
        reason: str,
        *,
        status: int | None = None,
        final_url: str | None = None,
        headers: Mapping[str, str] | None = None,
        retryable_site_failure: bool = False,
        body_preview: str | None = None,
        exception_traceback: str | None = None,
    ) -> None:
        super().__init__(reason)
        self.reason = reason
        self.status = status
        self.final_url = final_url
        self.headers = dict(headers or {})
        self.retryable_site_failure = retryable_site_failure
        self.body_preview = body_preview
        self.exception_traceback = exception_traceback


@dataclass(frozen=True)
class PlanItem:
    original: str
    timestamp: str
    role: str
    cdx_digest: str | None = None

    @property
    def key(self) -> tuple[str, str]:
        # Role is descriptive metadata.  The URL/capture pair is the durable
        # identity, so two roles can safely share one downloaded blob.
        return self.original, self.timestamp


@dataclass
class FetchResult:
    requested_url: str
    final_url: str
    status: int
    headers: dict[str, str]
    body: bytes
    content_encoding_interpretation: str | None = None


@dataclass(frozen=True)
class BlobRef:
    sha256: str
    zip_part: str
    zip_entry: str
    content_length: int
    compressed_length: int


@dataclass
class VolumeInfo:
    index: int
    path: Path
    entry_count: int
    start_dir: int


def _headers_dict(headers: Any) -> dict[str, str]:
    if headers is None:
        return {}
    if hasattr(headers, "items"):
        return {str(k): str(v) for k, v in headers.items()}
    return {str(k): str(v) for k, v in headers}


def _header_value(headers: Mapping[str, str], name: str) -> str | None:
    wanted = name.casefold()
    for key, value in headers.items():
        if str(key).casefold() == wanted:
            return str(value)
    return None


def _is_archive_url(url: str | None) -> bool:
    if not url:
        return False
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    return (
        parsed.scheme.casefold() == ARCHIVE_SCHEME
        and parsed.hostname is not None
        and parsed.hostname.casefold() == ARCHIVE_HOST
    )


def _is_allowed_original(url: str) -> bool:
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        return False
    # Credentials could leak into the request path or logs, and are not part
    # of the permitted source URL set.
    if parsed.username is not None or parsed.password is not None:
        return False
    host = parsed.hostname.rstrip(".").casefold()
    return any(host == root or host.endswith("." + root) for root in (
        "worldofwarcraft.com",
        "blizzard.com",
    ))


def build_archive_url(timestamp: str, original: str) -> str:
    """Build the only URL form issued by the downloader."""

    # Keep the target URL's path/query syntax, but encode a fragment so it is
    # not interpreted as a fragment of the outer archive URL.
    target = urllib.parse.quote(original, safe=":/?&=%;,+$'@~")
    return f"{ARCHIVE_SCHEME}://{ARCHIVE_HOST}/web/{timestamp}id_/{target}"


def _parse_timestamp(value: Any, field: str) -> str:
    result = str(value)
    if not TIMESTAMP_RE.fullmatch(result):
        raise PlanError(f"{field} must be a 14-digit timestamp")
    return result


def load_plan(path: Path) -> tuple[str, list[PlanItem]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PlanError(f"cannot read plan {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise PlanError("plan must be a JSON object")
    anchor = _parse_timestamp(raw.get("anchor_timestamp"), "anchor_timestamp")
    raw_items = raw.get("items")
    if not isinstance(raw_items, list):
        raise PlanError("plan.items must be a JSON array")
    items: list[PlanItem] = []
    for index, value in enumerate(raw_items):
        if not isinstance(value, dict):
            raise PlanError(f"items[{index}] must be an object")
        original = value.get("original")
        if not isinstance(original, str) or not _is_allowed_original(original):
            raise PlanError(
                f"items[{index}].original must be an HTTP(S) worldofwarcraft.com "
                "or blizzard.com URL (including subdomains)"
            )
        timestamp = _parse_timestamp(value.get("timestamp"), f"items[{index}].timestamp")
        role = value.get("role", "core")
        if not isinstance(role, str) or not role:
            raise PlanError(f"items[{index}].role must be a non-empty string")
        cdx_digest = value.get("cdx_digest")
        if cdx_digest is not None and not re.fullmatch(r"[A-Z2-7]{32}", str(cdx_digest)):
            raise PlanError(f"items[{index}].cdx_digest must be a SHA1 Base32 CDX digest")
        items.append(PlanItem(original=original, timestamp=timestamp, role=role, cdx_digest=cdx_digest))
    return anchor, items


def _actual_timestamp(headers: Mapping[str, str], final_url: str | None) -> str | None:
    memento = _header_value(headers, "Memento-Datetime")
    if memento:
        try:
            parsed = email.utils.parsedate_to_datetime(memento)
            if parsed is not None:
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=_datetime.timezone.utc)
                return parsed.astimezone(_datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
        except (TypeError, ValueError, OverflowError):
            pass
    if final_url:
        match = re.search(r"/web/(\d{14})(?:id_|/)", final_url)
        if match:
            return match.group(1)
    return None


def _wayback_error_marker(body: bytes) -> str | None:
    text = body[:128 * 1024].decode("utf-8", errors="ignore").casefold()
    markers = (
        "wayback machine error",
        "no archived snapshot",
        "this url has been excluded",
        "the requested url was not found",
        "got an http 404 response",
        "got an http 429 response",
        "got an http 5xx response",
        "memento not found",
        "timetravel error",
    )
    for marker in markers:
        if marker in text:
            return marker
    return None


def _body_preview(body: bytes) -> str:
    return body[:512].decode("utf-8", errors="replace").replace("\x00", "")


def _retry_delay_seconds(error: FetchError, default: float = DEFAULT_RETRY_DELAY_SECONDS) -> float:
    """Return a bounded delay for a retryable failure.

    Wayback's Retry-After may be either seconds or an HTTP date.  A malformed
    value falls back to a short delay, and no server value can make a run wait
    longer than the documented 30-second cap.
    """

    value = _header_value(error.headers, "Retry-After")
    delay: float | None = None
    if value:
        try:
            delay = max(0.0, float(value.strip()))
        except ValueError:
            try:
                when = email.utils.parsedate_to_datetime(value)
                if when is not None:
                    if when.tzinfo is None:
                        when = when.replace(tzinfo=_datetime.timezone.utc)
                    delay = (when - _datetime.datetime.now(_datetime.timezone.utc)).total_seconds()
            except (TypeError, ValueError, OverflowError):
                delay = None
    if delay is None:
        delay = default
    return min(MAX_RETRY_AFTER_SECONDS, max(0.0, delay))


def _read_entity(
    response: Any,
    max_bytes: int,
    on_chunk: Callable[[int], None] | None = None,
    *,
    expected_cdx_digest: str | None = None,
    interpretation: dict[str, str] | None = None,
) -> bytes:
    encoding_header = _header_value(_headers_dict(getattr(response, "headers", None)), "Content-Encoding")
    encoding = (encoding_header or "identity").strip().casefold()
    decoder: zlib.decompressobj | None = None
    if encoding in {"", "identity"}:
        pass
    elif encoding == "gzip":
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    elif encoding == "deflate":
        decoder = zlib.decompressobj()
    else:
        raise FetchError(f"unsupported_content_encoding:{encoding}")

    output: list[bytes] = []
    total = 0
    first_chunk = True
    mislabeled_gzip = False

    def accept(chunk: bytes) -> None:
        nonlocal total
        if not chunk:
            return
        total += len(chunk)
        if total > max_bytes:
            raise FetchError(
                f"object_exceeds_max_bytes:{max_bytes}",
                body_preview=f"decoded entity length exceeded {max_bytes}",
            )
        if on_chunk is not None:
            on_chunk(len(chunk))
        output.append(chunk)

    while True:
        raw = response.read(CHUNK_BYTES)
        if not raw:
            break
        if first_chunk:
            first_chunk = False
            # Some identity replays retain the historical gzip header after
            # pywb has already decoded the representation. Accept this only
            # with an independent CDX payload digest, checked after full read.
            if encoding == "gzip" and not raw.startswith(b"\x1f\x8b") and expected_cdx_digest:
                decoder = None
                mislabeled_gzip = True
        if decoder is None:
            accept(raw)
        else:
            try:
                # The one-byte allowance makes a too-large expansion fail
                # without asking zlib to allocate an unbounded output buffer.
                accept(decoder.decompress(raw, max_bytes - total + 1))
            except zlib.error as exc:
                raise FetchError(
                    f"content_decode_error:{exc}",
                    body_preview=json.dumps({
                        "content_encoding": encoding,
                        "wire_prefix_hex": raw[:32].hex(),
                        "wire_preview": _body_preview(raw),
                    }, ensure_ascii=False),
                ) from exc
    if decoder is not None:
        try:
            accept(decoder.flush())
        except zlib.error as exc:
            raise FetchError(f"content_decode_error:{exc}") from exc
        if not decoder.eof:
            raise FetchError("content_decode_error:truncated_compressed_entity")
    body = b"".join(output)
    if expected_cdx_digest:
        actual = base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")
        if actual != expected_cdx_digest:
            raise FetchError(f"cdx_digest_mismatch:expected={expected_cdx_digest},actual={actual}")
    if mislabeled_gzip and interpretation is not None:
        interpretation["value"] = "identity_bytes_with_gzip_header_verified_by_cdx_sha1"
    return body


class _ArchiveRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> Any:
        if not _is_archive_url(newurl):
            raise FetchError(
                "external_redirect_rejected",
                status=code,
                final_url=newurl,
                headers=_headers_dict(headers),
                body_preview=f"redirect target: {newurl}",
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_once(
    requested_url: str,
    max_bytes: int,
    on_chunk: Callable[[int], None] | None = None,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    expected_cdx_digest: str | None = None,
) -> FetchResult:
    """Fetch one archive URL, with redirect and response validation."""

    request = urllib.request.Request(
        requested_url,
        headers={
            # Identity replays already preserve historical representation
            # metadata. Avoid an extra transport-compression layer where
            # possible; still decode and validate it if the server supplies it.
            "Accept-Encoding": "identity",
            "User-Agent": "WOW-Encyclopedia-Backup/1.0",
        },
        method="GET",
    )
    opener = urllib.request.build_opener(_ArchiveRedirectHandler())
    response: Any | None = None
    interpretation: dict[str, str] = {}
    try:
        try:
            response = opener.open(request, timeout=timeout)
            status = int(response.getcode() or getattr(response, "status", 0))
            headers = _headers_dict(response.headers)
            final_url = response.geturl()
            try:
                body = _read_entity(response, max_bytes, on_chunk,
                                    expected_cdx_digest=expected_cdx_digest,
                                    interpretation=interpretation)
            except FetchError as exc:
                # A decoding error must retain the capture's response metadata
                # so a failed entity can be investigated instead of looking
                # like an attempt with no HTTP response.
                raise FetchError(
                    exc.reason, status=status, final_url=final_url,
                    headers=headers, retryable_site_failure=exc.retryable_site_failure,
                    body_preview=exc.body_preview,
                ) from exc
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            headers = _headers_dict(exc.headers)
            final_url = exc.geturl()
            try:
                body = _read_entity(exc, max_bytes, on_chunk)
            except FetchError as body_exc:
                if body_exc.reason.startswith("object_exceeds_max_bytes"):
                    raise
                body = b""
            marker = _wayback_error_marker(body)
            reason = f"http_status:{status}"
            if marker:
                reason = f"wayback_error_page:{marker}"
            raise FetchError(
                reason,
                status=status,
                final_url=final_url,
                headers=headers,
                retryable_site_failure=(status == 429 or 500 <= status <= 599),
                body_preview=_body_preview(body),
            )
        except FetchError:
            raise
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
            raise FetchError(
                f"network_error:{exc}",
                final_url=getattr(response, "geturl", lambda: None)() if response else requested_url,
                retryable_site_failure=True,
                exception_traceback="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            ) from exc
    finally:
        if response is not None:
            response.close()

    if not _is_archive_url(final_url):
        raise FetchError("archive_external_final_url", status=status, final_url=final_url, headers=headers)
    if status != 200:
        marker = _wayback_error_marker(body)
        reason = f"http_status:{status}"
        if marker:
            reason = f"wayback_error_page:{marker}"
        raise FetchError(
            reason,
            status=status,
            final_url=final_url,
            headers=headers,
            retryable_site_failure=(status == 429 or 500 <= status <= 599),
            body_preview=_body_preview(body),
        )
    marker = _wayback_error_marker(body)
    if marker:
        raise FetchError(
            f"wayback_error_page:{marker}",
            status=status,
            final_url=final_url,
            headers=headers,
            body_preview=_body_preview(body),
        )
    return FetchResult(
        requested_url=requested_url,
        final_url=final_url,
        status=status,
        headers=headers,
        body=body,
        content_encoding_interpretation=interpretation.get("value"),
    )


def _tree_size(root: Path) -> int:
    total = 0
    try:
        pending = [os.fspath(root)]
        while pending:
            directory = pending.pop()
            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        try:
                            if entry.is_symlink():
                                continue
                            if entry.is_dir(follow_symlinks=False):
                                pending.append(entry.path)
                            elif entry.is_file(follow_symlinks=False):
                                # Windows directory enumeration already has
                                # the size; DirEntry reuses it instead of
                                # opening each file repeatedly via pathlib.
                                total += entry.stat(follow_symlinks=False).st_size
                        except FileNotFoundError:
                            continue
            except FileNotFoundError:
                # Other workers atomically replace small reports/directories.
                continue
    except OSError as exc:
        raise BudgetExceeded(f"cannot measure budget root {root}: {exc}") from exc
    return total


class BudgetGuard:
    """Conservative budget checks against the whole configured filesystem tree."""

    def __init__(
        self,
        budget_root: Path,
        max_bytes: int,
        min_free_bytes: int,
        reserve_bytes: int,
        *,
        disk_usage_fn: Callable[[str], Any] = shutil.disk_usage,
    ) -> None:
        self.budget_root = budget_root.resolve()
        self.max_bytes = max_bytes
        self.min_free_bytes = min_free_bytes
        self.reserve_bytes = reserve_bytes
        self.disk_usage_fn = disk_usage_fn
        if max_bytes < 0 or min_free_bytes < 0 or reserve_bytes < 0:
            raise PlanError("storage budgets must be non-negative")
        if not self.budget_root.exists() or not self.budget_root.is_dir():
            raise PlanError(f"budget root is not a directory: {budget_root}")

    def check(self, extra_bytes: int = 0) -> None:
        if extra_bytes < 0:
            raise ValueError("extra_bytes must be non-negative")
        used = _tree_size(self.budget_root)
        projected = used + extra_bytes + self.reserve_bytes
        if projected > self.max_bytes:
            raise BudgetExceeded(
                f"budget root usage {used} + pending {extra_bytes} + reserve "
                f"{self.reserve_bytes} exceeds max {self.max_bytes}"
            )
        try:
            free = int(self.disk_usage_fn(str(self.budget_root)).free)
        except (AttributeError, OSError, ValueError) as exc:
            raise BudgetExceeded(f"cannot measure free disk space: {exc}") from exc
        if free < self.min_free_bytes + self.reserve_bytes + extra_bytes:
            raise BudgetExceeded(
                f"free disk {free} is below minimum {self.min_free_bytes} + "
                f"pending {extra_bytes} + reserve {self.reserve_bytes}"
            )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file_member(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> str:
    digest = hashlib.sha256()
    with zf.open(info, "r") as stream:
        while True:
            chunk = stream.read(CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _deflated_payload_size(data: bytes, name: str) -> int:
    compressor = zlib.compressobj(6, zlib.DEFLATED, -zlib.MAX_WBITS)
    compressed = compressor.compress(data) + compressor.flush()
    name_length = len(name.encode("utf-8"))
    # Local header + compressed bytes + central-directory record.  The final
    # end record is accounted for by _candidate_volume_size.
    return (30 + name_length + len(compressed)) + (46 + name_length)


class ZipVolumeStore:
    """A set of appendable ZIP_DEFLATED/ZIP64 volumes with SHA deduplication."""

    def __init__(
        self,
        out_dir: Path,
        guard: BudgetGuard,
        *,
        volume_bytes: int = DEFAULT_VOLUME_BYTES,
        volume_objects: int = DEFAULT_VOLUME_OBJECTS,
    ) -> None:
        if volume_bytes <= 0 or volume_objects <= 0:
            raise PlanError("volume limits must be positive")
        self.out_dir = out_dir
        self.guard = guard
        self.volume_bytes = volume_bytes
        self.volume_objects = volume_objects
        self.parts: dict[int, VolumeInfo] = {}
        self.refs: dict[str, BlobRef] = {}
        self._load_existing()

    def _paths(self) -> list[tuple[int, Path]]:
        result: list[tuple[int, Path]] = []
        for path in self.out_dir.glob("objects-*.zip"):
            match = VOLUME_RE.fullmatch(path.name)
            if match:
                result.append((int(match.group(1)), path))
        return sorted(result)

    def _load_existing(self) -> None:
        for index, path in self._paths():
            if not path.is_file():
                raise RecoveryError(f"managed ZIP volume is not a file: {path}")
            try:
                with zipfile.ZipFile(path, "r", allowZip64=True) as zf:
                    bad = zf.testzip()
                    if bad is not None:
                        raise RecoveryError(f"ZIP CRC validation failed in {path}: {bad}")
                    infos = zf.infolist()
                    names: set[str] = set()
                    for info in infos:
                        if info.filename in names:
                            raise RecoveryError(f"duplicate ZIP entry in {path}: {info.filename}")
                        names.add(info.filename)
                        match = re.fullmatch(r"objects/([0-9a-f]{64})\.bin", info.filename)
                        if not match:
                            continue
                        digest = _sha256_file_member(zf, info)
                        expected = match.group(1)
                        if digest != expected:
                            raise RecoveryError(
                                f"object SHA mismatch in {path}:{info.filename}: "
                                f"expected {expected}, got {digest}"
                            )
                        if expected in self.refs:
                            previous = self.refs[expected]
                            raise RecoveryError(
                                f"duplicate SHA object in {previous.zip_part} and {path.name}: {expected}"
                            )
                        self.refs[expected] = BlobRef(
                            sha256=expected,
                            zip_part=path.name,
                            zip_entry=info.filename,
                            content_length=info.file_size,
                            compressed_length=info.compress_size,
                        )
                    self.parts[index] = VolumeInfo(
                        index=index,
                        path=path,
                        entry_count=len(infos),
                        start_dir=int(getattr(zf, "start_dir", path.stat().st_size)),
                    )
            except RecoveryError:
                raise
            except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
                raise RecoveryError(f"cannot validate ZIP volume {path}: {exc}") from exc

    def reference(self, sha256: str) -> BlobRef | None:
        return self.refs.get(sha256)

    def verify_reference(self, ref: BlobRef) -> None:
        path = self.out_dir / ref.zip_part
        try:
            with zipfile.ZipFile(path, "r", allowZip64=True) as zf:
                info = zf.getinfo(ref.zip_entry)
                if info.file_size != ref.content_length or info.compress_size != ref.compressed_length:
                    raise RecoveryError(f"ZIP length mismatch for {ref.zip_part}:{ref.zip_entry}")
                actual = _sha256_file_member(zf, info)
                if actual != ref.sha256:
                    raise RecoveryError(f"ZIP SHA mismatch for {ref.zip_part}:{ref.zip_entry}")
        except KeyError as exc:
            raise RecoveryError(f"missing ZIP entry {ref.zip_part}:{ref.zip_entry}") from exc
        except (OSError, zipfile.BadZipFile) as exc:
            raise RecoveryError(f"cannot read ZIP entry {ref.zip_part}:{ref.zip_entry}: {exc}") from exc

    def _candidate_volume_size(self, volume: VolumeInfo, entry_size: int, name: str) -> int:
        # start_dir points to the first byte of the current central directory;
        # append mode removes that directory and writes a new one.
        central_size = 46 + len(name.encode("utf-8"))
        return volume.start_dir + (entry_size - central_size) + (volume.entry_count + 1) * central_size + 22

    def _new_volume(self) -> VolumeInfo:
        index = max(self.parts.keys(), default=0) + 1
        path = self.out_dir / f"objects-{index:04d}.zip"
        return VolumeInfo(index=index, path=path, entry_count=0, start_dir=0)

    def _choose_volume(self, entry_size: int, name: str) -> VolumeInfo:
        if not self.parts:
            return self._new_volume()
        current = self.parts[max(self.parts)]
        candidate = self._candidate_volume_size(current, entry_size, name)
        if current.entry_count >= self.volume_objects or (
            current.entry_count > 0 and candidate > self.volume_bytes
        ):
            return self._new_volume()
        return current

    def add_blob(self, data: bytes, sha256: str) -> BlobRef:
        existing = self.refs.get(sha256)
        if existing is not None:
            return existing
        name = f"objects/{sha256}.bin"
        entry_size = _deflated_payload_size(data, name)
        volume = self._choose_volume(entry_size, name)
        self.guard.check(extra_bytes=len(data) + ZIP_WRITE_HEADROOM)
        info = zipfile.ZipInfo(name)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.date_time = (1980, 1, 1, 0, 0, 0)
        mode = "a" if volume.path.exists() else "w"
        try:
            with zipfile.ZipFile(
                volume.path,
                mode=mode,
                compression=zipfile.ZIP_DEFLATED,
                allowZip64=True,
            ) as zf:
                zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
            with volume.path.open("r+b") as stream:
                os.fsync(stream.fileno())
        except (OSError, RuntimeError, ValueError, zipfile.BadZipFile) as exc:
            raise RecoveryError(f"failed writing ZIP volume {volume.path}: {exc}") from exc

        try:
            with zipfile.ZipFile(volume.path, "r", allowZip64=True) as zf:
                info = zf.getinfo(name)
                actual = _sha256_file_member(zf, info)
                if actual != sha256 or info.file_size != len(data):
                    raise RecoveryError(f"new ZIP entry failed validation: {volume.path.name}:{name}")
                refreshed = VolumeInfo(
                    index=volume.index,
                    path=volume.path,
                    entry_count=len(zf.infolist()),
                    start_dir=int(getattr(zf, "start_dir", volume.path.stat().st_size)),
                )
                ref = BlobRef(
                    sha256=sha256,
                    zip_part=volume.path.name,
                    zip_entry=name,
                    content_length=info.file_size,
                    compressed_length=info.compress_size,
                )
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            raise RecoveryError(f"new ZIP volume failed validation {volume.path}: {exc}") from exc
        self.parts[volume.index] = refreshed
        self.refs[sha256] = ref
        return ref


class JsonlAppender:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, record: Mapping[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        try:
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(line)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError as exc:
            raise BackupError(f"cannot append {self.path}: {exc}") from exc


def _atomic_json_write(path: Path, value: Mapping[str, Any]) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except OSError as exc:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise BackupError(f"cannot write {path}: {exc}") from exc


def _iso_now() -> str:
    return _datetime.datetime.now(_datetime.timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class BackupConfig:
    out_dir: Path
    budget_root: Path
    max_bytes: int = DEFAULT_MAX_BYTES
    min_free_bytes: int = DEFAULT_MIN_FREE_BYTES
    max_requests: int | None = None
    max_object_bytes: int = DEFAULT_OBJECT_BYTES
    volume_bytes: int = DEFAULT_VOLUME_BYTES
    volume_objects: int = DEFAULT_VOLUME_OBJECTS
    reserve_bytes: int = DEFAULT_RESERVE_BYTES
    deadline_seconds: float | None = None
    retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS


class BackupRunner:
    def __init__(
        self,
        anchor_timestamp: str,
        items: Sequence[PlanItem],
        config: BackupConfig,
        *,
        fetcher: Callable[..., FetchResult] = fetch_once,
        disk_usage_fn: Callable[[str], Any] = shutil.disk_usage,
        clock: Callable[[], float] = time.monotonic,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self.anchor_timestamp = anchor_timestamp
        self.items = list(items)
        self.config = config
        self.fetcher = fetcher
        self.clock = clock
        self.sleep_fn = sleep_fn
        self.started_monotonic = clock()
        self.guard = BudgetGuard(
            config.budget_root,
            config.max_bytes,
            config.min_free_bytes,
            config.reserve_bytes,
            disk_usage_fn=disk_usage_fn,
        )
        self.run_id = _datetime.datetime.now(_datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        self.site_failure_streak = 0

    def _check_deadline(self) -> None:
        limit = self.config.deadline_seconds
        if limit is not None and self.clock() - self.started_monotonic >= limit:
            raise DeadlineExceeded(f"deadline of {limit} seconds reached")

    def _load_manifest(self, store: ZipVolumeStore, path: Path) -> dict[tuple[str, str], dict[str, Any]]:
        latest: dict[tuple[str, str], dict[str, Any]] = {}
        if not path.exists():
            return latest
        try:
            with path.open("r", encoding="utf-8") as stream:
                for line_number, line in enumerate(stream, start=1):
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise RecoveryError(f"invalid manifest JSON at line {line_number}: {exc}") from exc
                    if not isinstance(record, dict):
                        raise RecoveryError(f"manifest line {line_number} is not an object")
                    if "original" not in record or "requested_timestamp" not in record:
                        raise RecoveryError(f"manifest line {line_number} lacks URL/timestamp identity")
                    key = (str(record["original"]), str(record["requested_timestamp"]))
                    if record.get("status") == "success":
                        sha = record.get("sha256")
                        if not isinstance(sha, str) or not SHA256_RE.fullmatch(sha):
                            raise RecoveryError(f"manifest line {line_number} has invalid SHA")
                        ref = store.reference(sha)
                        if ref is None:
                            raise RecoveryError(
                                f"manifest line {line_number} references missing object {sha}"
                            )
                        if (
                            record.get("zip_part") != ref.zip_part
                            or record.get("zip_entry") != ref.zip_entry
                            or int(record.get("content_length", -1)) != ref.content_length
                        ):
                            raise RecoveryError(
                                f"manifest line {line_number} does not match {ref.zip_part}:{ref.zip_entry}"
                            )
                        store.verify_reference(ref)
                    latest[key] = record
        except OSError as exc:
            raise RecoveryError(f"cannot read manifest {path}: {exc}") from exc
        return latest

    @staticmethod
    def _attempt_record(attempt: int, result: FetchResult | None = None, error: FetchError | None = None) -> dict[str, Any]:
        if result is not None:
            memento = _header_value(result.headers, "Memento-Datetime")
            return {
                "attempt": attempt,
                "status": result.status,
                "final_url": result.final_url,
                "memento_datetime": memento,
                "actual_timestamp": _actual_timestamp(result.headers, result.final_url),
                "response_headers": result.headers,
            }
        assert error is not None
        return {
            "attempt": attempt,
            "status": error.status,
            "final_url": error.final_url,
            "memento_datetime": _header_value(error.headers, "Memento-Datetime"),
            "actual_timestamp": _actual_timestamp(error.headers, error.final_url),
            "response_headers": error.headers,
            "reason": error.reason,
            "body_preview": error.body_preview,
            "retryable_site_failure": error.retryable_site_failure,
            "exception_traceback": error.exception_traceback,
        }

    def _success_record(
        self,
        item: PlanItem,
        requested_url: str,
        result: FetchResult,
        sha256: str,
        ref: BlobRef,
        attempts: list[dict[str, Any]],
        *,
        skipped: bool = False,
        skip_reason: str | None = None,
    ) -> dict[str, Any]:
        actual_timestamp = _actual_timestamp(result.headers, result.final_url)
        record: dict[str, Any] = {
            "run_id": self.run_id,
            "recorded_at": _iso_now(),
            "status": "success",
            "skipped": skipped,
            "original": item.original,
            "role": item.role,
            "requested_timestamp": item.timestamp,
            "requested_url": requested_url,
            "actual_url": result.final_url,
            "http_status": result.status,
            "memento_datetime": _header_value(result.headers, "Memento-Datetime"),
            "actual_timestamp": actual_timestamp,
            "timestamp_drift": actual_timestamp is not None and actual_timestamp != item.timestamp,
            "response_headers": result.headers,
            "sha256": sha256,
            "content_length": len(result.body),
            "zip_part": ref.zip_part,
            "zip_entry": ref.zip_entry,
            "zip_compressed_length": ref.compressed_length,
            "attempts": attempts,
            "cdx_digest": item.cdx_digest,
            "content_encoding_interpretation": result.content_encoding_interpretation,
        }
        if skip_reason:
            record["skip_reason"] = skip_reason
        return record

    def _resumed_record(self, item: PlanItem, previous: Mapping[str, Any]) -> dict[str, Any]:
        sha = str(previous["sha256"])
        ref = BlobRef(
            sha256=sha,
            zip_part=str(previous["zip_part"]),
            zip_entry=str(previous["zip_entry"]),
            content_length=int(previous["content_length"]),
            compressed_length=int(previous.get("zip_compressed_length", -1)),
        )
        result = FetchResult(
            requested_url=build_archive_url(item.timestamp, item.original),
            final_url=str(previous.get("actual_url") or previous.get("requested_url")),
            status=int(previous.get("http_status", 200)),
            headers=dict(previous.get("response_headers") or {}),
            body=b"",
            content_encoding_interpretation=previous.get("content_encoding_interpretation"),
        )
        record = self._success_record(
            item,
            result.requested_url,
            result,
            sha,
            ref,
            list(previous.get("attempts") or []),
            skipped=True,
            skip_reason="verified_existing",
        )
        # The body is intentionally absent on a resumed record; content_length
        # remains the verified stored length from the prior record.
        record["content_length"] = int(previous["content_length"])
        if "zip_compressed_length" in previous:
            record["zip_compressed_length"] = previous["zip_compressed_length"]
        return record

    def _append_jsonl(self, appender: JsonlAppender, record: Mapping[str, Any]) -> None:
        encoded_length = len((json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
        self.guard.check(extra_bytes=encoded_length)
        appender.append(record)

    def _base_summary(self, max_requests: int) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "run_id": self.run_id,
            "started_at": _iso_now(),
            "finished_at": None,
            "anchor_timestamp": self.anchor_timestamp,
            "planned_items": len(self.items),
            "config": {
                "budget_root": str(self.config.budget_root.resolve()),
                "max_bytes": self.config.max_bytes,
                "min_free_bytes": self.config.min_free_bytes,
                "reserve_bytes": self.config.reserve_bytes,
                "max_object_bytes": self.config.max_object_bytes,
                "volume_bytes": self.config.volume_bytes,
                "volume_objects": self.config.volume_objects,
                "max_requests": max_requests,
                "deadline_seconds": self.config.deadline_seconds,
                "retry_delay_seconds": self.config.retry_delay_seconds,
            },
            "stats": {
                "success": 0,
                "failed": 0,
                "resumed": 0,
                "requests_started": 0,
                "content_bytes": 0,
                "compressed_bytes": 0,
            },
            "failures": [],
            "missing": [],
            "stop_reason": None,
        }

    def _write_summary(self, path: Path, summary: Mapping[str, Any]) -> None:
        # Summary replacement is a small metadata write.  The guard accounts
        # for a complete temporary copy before os.replace.
        encoded = len(json.dumps(summary, ensure_ascii=False).encode("utf-8"))
        self.guard.check(extra_bytes=encoded + 4096)
        _atomic_json_write(path, summary)

    def run(self) -> dict[str, Any]:
        out_dir = self.config.out_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        self.guard.check()
        manifest_path = out_dir / "manifest.jsonl"
        errors_path = out_dir / "errors.jsonl"
        summary_path = out_dir / "summary.json"
        store = ZipVolumeStore(
            out_dir,
            self.guard,
            volume_bytes=self.config.volume_bytes,
            volume_objects=self.config.volume_objects,
        )
        latest = self._load_manifest(store, manifest_path)
        max_requests = self.config.max_requests
        if max_requests is None:
            max_requests = len(self.items) * MAX_ATTEMPTS_PER_ITEM
        if max_requests < 0:
            raise PlanError("max_requests must be non-negative")
        summary = self._base_summary(max_requests)
        manifest = JsonlAppender(manifest_path)
        errors = JsonlAppender(errors_path)
        requests_started = 0
        stop_reason: str | None = None

        try:
            self._write_summary(summary_path, summary)
        except BackupError:
            # A pre-existing summary can consume the exact metadata headroom;
            # the manifest remains the authoritative recovery record.
            pass

        for item_index, item in enumerate(self.items):
            if stop_reason is not None:
                summary["missing"].append({
                    "index": item_index,
                    "original": item.original,
                    "requested_timestamp": item.timestamp,
                    "reason": stop_reason,
                })
                continue
            try:
                self._check_deadline()
                self.guard.check()
            except (DeadlineExceeded, BudgetExceeded) as exc:
                stop_reason = "deadline_exceeded" if isinstance(exc, DeadlineExceeded) else "budget_exceeded"
                summary["stop_reason"] = stop_reason
                summary["missing"].append({
                    "index": item_index,
                    "original": item.original,
                    "requested_timestamp": item.timestamp,
                    "reason": stop_reason,
                })
                continue

            previous = latest.get(item.key)
            if previous and previous.get("status") == "success":
                record = self._resumed_record(item, previous)
                self._append_jsonl(manifest, record)
                summary["stats"]["success"] += 1
                summary["stats"]["resumed"] += 1
                summary["stats"]["content_bytes"] += int(previous["content_length"])
                summary["stats"]["compressed_bytes"] += int(previous.get("zip_compressed_length", 0))
                latest[item.key] = record
                try:
                    self._write_summary(summary_path, summary)
                except BackupError:
                    pass
                continue

            requested_url = build_archive_url(item.timestamp, item.original)
            attempts: list[dict[str, Any]] = []
            success_result: FetchResult | None = None
            success_ref: BlobRef | None = None
            success_sha: str | None = None
            final_error: FetchError | None = None
            pending_stop: str | None = None

            for attempt in range(1, MAX_ATTEMPTS_PER_ITEM + 1):
                try:
                    self._check_deadline()
                    self.guard.check()
                except DeadlineExceeded:
                    pending_stop = "deadline_exceeded"
                    break
                except BudgetExceeded:
                    pending_stop = "budget_exceeded"
                    break
                if requests_started >= max_requests:
                    pending_stop = "max_requests"
                    break
                requests_started += 1
                summary["stats"]["requests_started"] = requests_started
                pending_bytes = 0

                def on_chunk(count: int) -> None:
                    nonlocal pending_bytes
                    self._check_deadline()
                    pending_bytes += count
                    self.guard.check(extra_bytes=pending_bytes + ZIP_WRITE_HEADROOM)

                try:
                    if item.cdx_digest:
                        result = self.fetcher(requested_url, self.config.max_object_bytes, on_chunk,
                                              expected_cdx_digest=item.cdx_digest)
                    else:
                        result = self.fetcher(requested_url, self.config.max_object_bytes, on_chunk)
                    if not isinstance(result, FetchResult):
                        raise FetchError("fetcher_returned_invalid_result")
                    if result.status != 200:
                        raise FetchError(
                            f"http_status:{result.status}",
                            status=result.status,
                            final_url=result.final_url,
                            headers=result.headers,
                            retryable_site_failure=(result.status == 429 or 500 <= result.status <= 599),
                        )
                    if not _is_archive_url(result.final_url):
                        raise FetchError(
                            "archive_external_final_url",
                            status=result.status,
                            final_url=result.final_url,
                            headers=result.headers,
                        )
                    marker = _wayback_error_marker(result.body)
                    if marker:
                        raise FetchError(
                            f"wayback_error_page:{marker}",
                            status=result.status,
                            final_url=result.final_url,
                            headers=result.headers,
                            body_preview=_body_preview(result.body),
                        )
                    if len(result.body) > self.config.max_object_bytes:
                        raise FetchError(
                            f"object_exceeds_max_bytes:{self.config.max_object_bytes}",
                            status=result.status,
                            final_url=result.final_url,
                            headers=result.headers,
                        )
                    self._check_deadline()
                    self.guard.check(extra_bytes=len(result.body) + ZIP_WRITE_HEADROOM)
                    digest = _sha256_bytes(result.body)
                    ref = store.add_blob(result.body, digest)
                    success_result = result
                    success_ref = ref
                    success_sha = digest
                    attempts.append(self._attempt_record(attempt, result=result))
                    self.site_failure_streak = 0
                    break
                except BudgetExceeded as exc:
                    final_error = FetchError(str(exc))
                    attempts.append(self._attempt_record(attempt, error=final_error))
                    pending_stop = "budget_exceeded"
                    break
                except DeadlineExceeded as exc:
                    final_error = FetchError(str(exc))
                    attempts.append(self._attempt_record(attempt, error=final_error))
                    pending_stop = "deadline_exceeded"
                    break
                except FetchError as exc:
                    final_error = exc
                    attempts.append(self._attempt_record(attempt, error=exc))
                    if not exc.retryable_site_failure:
                        break
                    if attempt < MAX_ATTEMPTS_PER_ITEM:
                        try:
                            self._check_deadline()
                            delay = _retry_delay_seconds(exc, self.config.retry_delay_seconds)
                            if self.config.deadline_seconds is not None:
                                remaining = self.config.deadline_seconds - (
                                    self.clock() - self.started_monotonic
                                )
                                if remaining <= 0:
                                    raise DeadlineExceeded(
                                        f"deadline of {self.config.deadline_seconds} seconds reached"
                                    )
                                delay = min(delay, remaining)
                            if delay > 0:
                                self.sleep_fn(delay)
                        except DeadlineExceeded as deadline_exc:
                            pending_stop = "deadline_exceeded"
                            final_error = FetchError(str(deadline_exc))
                            break

            if success_result is not None and success_ref is not None and success_sha is not None:
                record = self._success_record(
                    item,
                    requested_url,
                    success_result,
                    success_sha,
                    success_ref,
                    attempts,
                )
                self._append_jsonl(manifest, record)
                latest[item.key] = record
                summary["stats"]["success"] += 1
                summary["stats"]["content_bytes"] += len(success_result.body)
                summary["stats"]["compressed_bytes"] += success_ref.compressed_length
            else:
                reason = pending_stop or (final_error.reason if final_error else "request_not_attempted")
                failure_record = {
                    "run_id": self.run_id,
                    "recorded_at": _iso_now(),
                    "status": "failed",
                    "original": item.original,
                    "role": item.role,
                    "requested_timestamp": item.timestamp,
                    "requested_url": requested_url,
                    "failure_reason": reason,
                    "attempts": attempts,
                }
                try:
                    self._append_jsonl(manifest, failure_record)
                    latest[item.key] = failure_record
                except BackupError:
                    # The summary's missing list still records this item if
                    # metadata can no longer be written under the hard cap.
                    pass
                summary["stats"]["failed"] += 1
                summary["failures"].append({
                    "index": item_index,
                    "original": item.original,
                    "requested_timestamp": item.timestamp,
                    "reason": reason,
                })
                summary["missing"].append({
                    "index": item_index,
                    "original": item.original,
                    "requested_timestamp": item.timestamp,
                    "reason": reason,
                })
                if final_error is not None and final_error.retryable_site_failure:
                    self.site_failure_streak += 1
                else:
                    self.site_failure_streak = 0
                try:
                    self._append_jsonl(errors, {
                        **failure_record,
                        "error_type": "fetch",
                    })
                except BackupError:
                    pass
                if pending_stop in {"budget_exceeded", "deadline_exceeded", "max_requests"}:
                    stop_reason = pending_stop
                elif self.site_failure_streak >= 3:
                    stop_reason = "three_consecutive_site_failures"
            try:
                self._write_summary(summary_path, summary)
            except BackupError:
                pass
            if stop_reason is not None:
                summary["stop_reason"] = stop_reason

        summary["finished_at"] = _iso_now()
        summary["stop_reason"] = stop_reason
        try:
            self._write_summary(summary_path, summary)
        except BackupError:
            pass
        return summary


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--budget-root", type=Path, default=Path.cwd())
    parser.add_argument("--max-bytes", type=_positive_int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--min-free-bytes", type=int, default=DEFAULT_MIN_FREE_BYTES)
    parser.add_argument("--max-requests", type=int)
    parser.add_argument("--max-object-bytes", type=_positive_int, default=DEFAULT_OBJECT_BYTES)
    parser.add_argument("--volume-bytes", type=_positive_int, default=DEFAULT_VOLUME_BYTES)
    parser.add_argument("--volume-objects", type=_positive_int, default=DEFAULT_VOLUME_OBJECTS)
    parser.add_argument("--reserve-bytes", type=int, default=DEFAULT_RESERVE_BYTES)
    parser.add_argument("--deadline-seconds", type=float)
    parser.add_argument("--retry-delay-seconds", type=float, default=DEFAULT_RETRY_DELAY_SECONDS)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        anchor, items = load_plan(args.plan)
        config = BackupConfig(
            out_dir=args.out,
            budget_root=args.budget_root,
            max_bytes=args.max_bytes,
            min_free_bytes=args.min_free_bytes,
            max_requests=args.max_requests,
            max_object_bytes=args.max_object_bytes,
            volume_bytes=args.volume_bytes,
            volume_objects=args.volume_objects,
            reserve_bytes=args.reserve_bytes,
            deadline_seconds=args.deadline_seconds,
            retry_delay_seconds=args.retry_delay_seconds,
        )
        summary = BackupRunner(anchor, items, config).run()
    except (BackupError, OSError, ValueError) as exc:
        print(f"wayback_backup: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    if summary.get("stats", {}).get("failed", 0) or summary.get("missing"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

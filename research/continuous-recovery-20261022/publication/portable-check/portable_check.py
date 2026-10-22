#!/usr/bin/env python3
"""Independently verify a portable site ZIP and smoke-test its loopback server.

This tool is read-only with respect to the archive, accepted export, package
report, and root browser acceptance. It writes only a new versioned extraction
under ``.scratch`` and a new receipt named in the root-supplied config.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path, PureWindowsPath
import queue
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
from typing import Any, BinaryIO, Mapping, Sequence
from urllib.parse import quote, unquote, urlsplit
import zipfile
import zlib


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
TOOLS_ROOT = REPOSITORY_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import package_pages_archive as packager  # noqa: E402


CONFIG_SCHEMA = "wow-portable-check-config/v1"
RECEIPT_SCHEMA = "wow-portable-check-receipt/v1"
PACKAGE_SCHEMA = "wow-encyclopedia-portable-archive/v1"
MIN_FREE_BYTES = 11_005_853_696
LARGE_WRITE_THRESHOLD_BYTES = 16 * 1024 * 1024
READ_CHUNK_BYTES = 1024 * 1024
SERVER_READY_SECONDS = 60.0
SERVER_STOP_SECONDS = 4.0
MAX_REDIRECTS = 4
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION_RE = re.compile(r"^v([0-9]+)$")
PACKAGE_SITE_ROOT = "site"
PACKAGE_SUPPORT_FILES = ("tools/serve_pages_preview.py", "NOTICE.md")
PACKAGE_GENERATED_FILES = (
    "README.md", "START_BROWSE.cmd", "archive-metadata.json", "FILE_SHA256SUMS.txt",
)


class PortableCheckError(RuntimeError):
    """Raised for an invalid input, archive, extraction, or smoke check."""


@dataclass(frozen=True)
class ExpectedFile:
    name: str
    source: Path
    source_kind: str
    sha256: str
    length: int

    def source_record(self) -> dict[str, Any]:
        return {
            "path": self.name,
            "source_kind": self.source_kind,
            "source_path": self.name,
            "source_sha256": self.sha256,
            "source_bytes": self.length,
        }


def _fail(message: str) -> PortableCheckError:
    return PortableCheckError(message)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_stream(stream: BinaryIO) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    total = 0
    crc = 0
    for chunk in iter(lambda: stream.read(READ_CHUNK_BYTES), b""):
        digest.update(chunk)
        crc = zlib.crc32(chunk, crc)
        total += len(chunk)
    return digest.hexdigest(), total, crc & 0xFFFFFFFF


def _hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    length = 0
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(READ_CHUNK_BYTES), b""):
                digest.update(chunk)
                length += len(chunk)
    except OSError as exc:
        raise _fail(f"cannot read file {path}: {exc}") from exc
    return digest.hexdigest(), length


def _is_reparse_or_link(path: Path, entry: os.DirEntry[str] | None = None) -> bool:
    try:
        if path.is_symlink():
            return True
        details = entry.stat(follow_symlinks=False) if entry is not None else path.stat(follow_symlinks=False)
    except OSError as exc:
        raise _fail(f"cannot inspect filesystem entry {path}: {exc}") from exc
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(details, "st_file_attributes", 0) & reparse_flag)


def _regular_file(path: Path, label: str) -> None:
    if _is_reparse_or_link(path):
        raise _fail(f"{label} is a symlink or reparse point: {path}")
    try:
        details = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise _fail(f"cannot inspect {label}: {exc}") from exc
    if not stat.S_ISREG(details.st_mode):
        raise _fail(f"{label} is not a regular file: {path}")


def _safe_relative(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise _fail(f"{label} must be a non-empty relative POSIX path")
    if "\x00" in value or "\\" in value or value.startswith("/") or PureWindowsPath(value).is_absolute():
        raise _fail(f"{label} is absolute or contains unsafe separators")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts) or ":" in parts[0]:
        raise _fail(f"{label} contains traversal or drive syntax")
    try:
        normalized = packager.safe_member_name(value)
    except packager.ArchiveError as exc:
        raise _fail(f"{label} is not an allowed package member: {exc}") from exc
    if normalized != value:
        raise _fail(f"{label} is not a canonical slash path")
    return value


def _resolve_path(value: Any, label: str, *, must_exist: bool) -> Path:
    if not isinstance(value, str) or not value:
        raise _fail(f"{label} must be a path string")
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = REPOSITORY_ROOT / candidate
    try:
        resolved = candidate.resolve(strict=must_exist)
        resolved.relative_to(REPOSITORY_ROOT)
    except (OSError, ValueError) as exc:
        raise _fail(f"{label} must resolve inside the repository: {value}") from exc
    # Check each existing path component so an input cannot escape through a
    # symlink/reparse point before resolve() canonicalizes it.
    try:
        lexical = candidate.absolute().relative_to(REPOSITORY_ROOT)
    except ValueError as exc:
        raise _fail(f"{label} is outside the repository") from exc
    current = REPOSITORY_ROOT
    for part in lexical.parts:
        current = current / part
        if current.exists() and _is_reparse_or_link(current):
            raise _fail(f"{label} traverses a symlink or reparse point")
    if must_exist and not resolved.exists():
        raise _fail(f"{label} does not exist: {value}")
    return resolved


def _read_json(path: Path, label: str) -> dict[str, Any]:
    _regular_file(path, label)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise _fail(f"{label} must contain a JSON object")
    return data


def _json_pointer(document: Any, pointer: str, label: str) -> Any:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise _fail(f"{label} JSON pointer must start with '/'")
    current = document
    for raw_part in pointer[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        try:
            current = current[int(part)] if isinstance(current, list) else current[part]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise _fail(f"{label} JSON pointer not found: {pointer}") from exc
    return current


def _load_config(path: Path) -> dict[str, Any]:
    _regular_file(path, "config")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"config is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(config, dict) or config.get("schema") != CONFIG_SCHEMA:
        raise _fail(f"config schema must be {CONFIG_SCHEMA}")
    version = config.get("version")
    match = VERSION_RE.fullmatch(version) if isinstance(version, str) else None
    if not match or int(match.group(1)) < 54:
        raise _fail("version must be v54 or later")
    for key in ("accepted_site", "archive", "package_report", "export", "root_browser_acceptance", "output_receipt", "smoke_paths"):
        if key not in config:
            raise _fail(f"config is missing required field: {key}")
    if not isinstance(config.get("export"), dict) or not isinstance(config.get("root_browser_acceptance"), dict):
        raise _fail("export and root_browser_acceptance must be objects")
    if not isinstance(config.get("smoke_paths"), list) or not config["smoke_paths"]:
        raise _fail("smoke_paths must be a non-empty list")
    return config


def _disk_free() -> int:
    try:
        return shutil.disk_usage(REPOSITORY_ROOT).free
    except OSError as exc:
        raise _fail(f"cannot inspect D: free space: {exc}") from exc


def _require_disk_floor(label: str) -> int:
    free = _disk_free()
    if free < MIN_FREE_BYTES:
        raise _fail(f"D: free space below required floor at {label}: {free} < {MIN_FREE_BYTES}")
    return free


def _walk_site(site: Path) -> list[tuple[str, Path]]:
    if not site.is_dir() or _is_reparse_or_link(site):
        raise _fail(f"accepted_site must be a normal directory: {site}")
    found: list[tuple[str, Path]] = []
    pending = [site]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name.casefold())
        except OSError as exc:
            raise _fail(f"cannot enumerate accepted_site: {exc}") from exc
        for entry in entries:
            path = Path(entry.path)
            if _is_reparse_or_link(path, entry):
                raise _fail(f"accepted_site contains a symlink or reparse point: {path}")
            relative = path.relative_to(site).as_posix()
            member_name = _safe_relative(f"site/{relative}", "accepted site member")
            try:
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif entry.is_file(follow_symlinks=False):
                    found.append((member_name, path))
                else:
                    raise _fail(f"accepted_site contains a non-file entry: {path}")
            except OSError as exc:
                raise _fail(f"cannot inspect accepted_site entry: {exc}") from exc
    names = [name.casefold() for name, _ in found]
    if len(names) != len(set(names)):
        raise _fail("accepted_site has case-insensitive member collisions")
    return sorted(found, key=lambda pair: pair[0])


def _expected_source_files(accepted_site: Path) -> tuple[list[ExpectedFile], dict[str, Any], str, str]:
    provenance_path = accepted_site / "export-provenance.json"
    _regular_file(provenance_path, "accepted export provenance")
    provenance = _read_json(provenance_path, "accepted export provenance")
    prefix = provenance.get("base_path")
    if not isinstance(prefix, str) or not prefix.startswith("/") or not prefix.endswith("/") or ".." in prefix or "\\" in prefix:
        raise _fail("accepted export provenance has an invalid project base_path")
    provenance_sha, provenance_bytes = _hash_file(provenance_path)
    if provenance_bytes <= 0:
        raise _fail("accepted export provenance is empty")

    sources: list[ExpectedFile] = []
    for name, path in _walk_site(accepted_site):
        digest, length = _hash_file(path)
        sources.append(ExpectedFile(name, path, "site", digest, length))
    for name in PACKAGE_SUPPORT_FILES:
        source_path = REPOSITORY_ROOT / name
        _regular_file(source_path, f"package support source {name}")
        digest, length = _hash_file(source_path)
        sources.append(ExpectedFile(name, source_path, "support", digest, length))
    names = [item.name for item in sources]
    if len(names) != len(set(names)):
        raise _fail("accepted site and support members collide")
    return sorted(sources, key=lambda item: item.name), provenance, provenance_sha, prefix


def _canonical_source_manifest(sources: Sequence[ExpectedFile]) -> bytes:
    lines = [f"{item.sha256}  {item.length}  {item.name}" for item in sorted(sources, key=lambda item: item.name)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _expected_package_names(sources: Sequence[ExpectedFile]) -> set[str]:
    return {item.name for item in sources} | set(PACKAGE_GENERATED_FILES)


def _validate_zip_infos(infos: Sequence[zipfile.ZipInfo], expected_names: set[str]) -> dict[str, zipfile.ZipInfo]:
    names = [info.filename for info in infos]
    if len(names) != len(set(names)) or len({name.casefold() for name in names}) != len(names):
        raise _fail("ZIP contains duplicate or case-colliding member names")
    observed: dict[str, zipfile.ZipInfo] = {}
    for info in infos:
        name = _safe_relative(info.filename, "ZIP member path")
        if name != info.filename:
            raise _fail(f"ZIP member path is not canonical: {info.filename!r}")
        if info.is_dir() or name.endswith("/"):
            raise _fail(f"ZIP contains a directory entry: {name}")
        if info.flag_bits & 0x1:
            raise _fail(f"ZIP contains an encrypted member: {name}")
        if info.compress_type != zipfile.ZIP_DEFLATED:
            raise _fail(f"ZIP member is not DEFLATE compressed: {name}")
        mode = (info.external_attr >> 16) & 0xFFFF
        file_type = stat.S_IFMT(mode)
        if file_type not in (0, stat.S_IFREG):
            raise _fail(f"ZIP member is not a regular file: {name}")
        folded_parts = {part.casefold() for part in name.split("/")}
        evidence_suffixes = (".cookies.txt", ".headers", ".stderr.txt", ".body", ".warc", ".cdx", ".pcap")
        if "rawresearch" in folded_parts or ".git" in folded_parts or "private" in folded_parts or name.casefold().endswith(evidence_suffixes):
            raise _fail(f"ZIP contains a raw or runtime evidence path: {name}")
        observed[name] = info
    if set(observed) != expected_names:
        missing = sorted(expected_names - set(observed))
        extra = sorted(set(observed) - expected_names)
        raise _fail(f"ZIP whitelist mismatch: missing={missing[:5]}, extra={extra[:5]}")
    return observed


def _read_zip_member(zip_handle: zipfile.ZipFile, info: zipfile.ZipInfo, *, keep: bool = False) -> tuple[str, int, int, bytes | None]:
    digest = hashlib.sha256()
    total = 0
    crc = 0
    chunks: list[bytes] | None = [] if keep else None
    try:
        with zip_handle.open(info, "r") as stream:
            for chunk in iter(lambda: stream.read(READ_CHUNK_BYTES), b""):
                digest.update(chunk)
                crc = zlib.crc32(chunk, crc)
                total += len(chunk)
                if total > info.file_size:
                    raise _fail(f"ZIP member expanded beyond recorded size: {info.filename}")
                if keep and total > 16 * 1024 * 1024:
                    raise _fail(f"generated package metadata member exceeds 16 MiB: {info.filename}")
                if chunks is not None:
                    chunks.append(chunk)
    except (OSError, RuntimeError, zipfile.BadZipFile, EOFError) as exc:
        raise _fail(f"cannot read ZIP member {info.filename}: {exc}") from exc
    if total != info.file_size:
        raise _fail(f"ZIP member length mismatch: {info.filename}")
    return digest.hexdigest(), total, crc & 0xFFFFFFFF, b"".join(chunks) if chunks is not None else None


def _parse_checksums(payload: bytes) -> dict[str, tuple[str, int]]:
    try:
        lines = payload.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise _fail("FILE_SHA256SUMS.txt is not UTF-8") from exc
    if not lines or lines[0] != "# SHA-256  bytes  path":
        raise _fail("FILE_SHA256SUMS.txt has an invalid header")
    result: dict[str, tuple[str, int]] = {}
    for line in lines[1:]:
        if not line:
            continue
        parts = line.split("  ", 2)
        if len(parts) != 3 or not SHA256_RE.fullmatch(parts[0]):
            raise _fail("FILE_SHA256SUMS.txt has a malformed entry")
        try:
            length = int(parts[1])
        except ValueError as exc:
            raise _fail("FILE_SHA256SUMS.txt has an invalid length") from exc
        if length < 0:
            raise _fail("FILE_SHA256SUMS.txt has a negative length")
        name = _safe_relative(parts[2], "checksum path")
        if name in result:
            raise _fail(f"duplicate checksum path: {name}")
        result[name] = (parts[0], length)
    return result


def _read_root_acceptance(config: Mapping[str, Any], accepted_site: Path,
                          provenance_sha: str) -> tuple[str, dict[str, Any]]:
    root_spec = config["root_browser_acceptance"]
    if not isinstance(root_spec.get("path"), str):
        raise _fail("root_browser_acceptance.path is required")
    path = _resolve_path(root_spec["path"], "root browser acceptance", must_exist=True)
    record = _read_json(path, "root browser acceptance")
    if record.get("schema") != "wow-root-final-browser-acceptance/v1" or record.get("accepted") is not True:
        raise _fail("root browser acceptance is not accepted=true")
    expected_local_site = accepted_site.relative_to(REPOSITORY_ROOT).as_posix()
    if record.get("local_site") != expected_local_site:
        raise _fail("root browser acceptance local_site differs from configured accepted_site")
    if record.get("export_provenance_sha256") != provenance_sha:
        raise _fail("root browser acceptance provenance SHA does not match accepted export")
    if (record.get("external_requests") != [] or record.get("page_errors") != []
            or record.get("asset_fulfillments") != 0
            or ("request_failures" in record and record.get("request_failures") != [])):
        raise _fail("root browser acceptance includes external requests, page errors, request failures, or fulfilled assets")
    if not isinstance(record.get("pages"), list) or not isinstance(record.get("evidence"), list):
        raise _fail("root browser acceptance pages/evidence must be lists")
    for item in record["evidence"]:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str):
            raise _fail("root browser acceptance evidence entries must contain path and sha256")
        evidence_path = _resolve_path(item["path"], "root browser acceptance evidence", must_exist=True)
        _regular_file(evidence_path, "root browser acceptance evidence")
        if _hash_file(evidence_path)[0] != item["sha256"]:
            raise _fail("root browser acceptance evidence hash mismatch")
    return _hash_file(path)[0], record


def _read_export_acceptance(config: Mapping[str, Any], accepted_site: Path,
                            sources: Sequence[ExpectedFile], provenance_sha: str) -> str:
    export_spec = config["export"]
    if not isinstance(export_spec, dict) or not isinstance(export_spec.get("path"), str):
        raise _fail("export.path is required")
    path = _resolve_path(export_spec["path"], "export acceptance", must_exist=True)
    record = _read_json(path, "export acceptance")
    if record.get("accepted") is not True:
        raise _fail("export acceptance is not accepted=true")
    expected_local_site = accepted_site.relative_to(REPOSITORY_ROOT).as_posix()
    if record.get("local_site") != expected_local_site:
        raise _fail("export acceptance local_site differs from configured accepted_site")
    if record.get("export_provenance_sha256") != provenance_sha:
        raise _fail("export acceptance provenance SHA does not match accepted export")
    if record.get("published") is True:
        raise _fail("export acceptance records that the site was published")
    site_sources = [item for item in sources if item.source_kind == "site"]
    actual_files = record.get("actual_files")
    if isinstance(actual_files, bool) or not isinstance(actual_files, int) or actual_files != len(site_sources):
        raise _fail("export acceptance actual_files count differs from accepted site")
    objects = record.get("objects")
    if not isinstance(objects, list):
        raise _fail("export acceptance objects must be a list")
    observed: dict[str, tuple[str, int]] = {}
    for item in objects:
        if not isinstance(item, dict):
            raise _fail("export acceptance object must be an object")
        relative = _safe_relative(item.get("path"), "export acceptance object path")
        digest = item.get("sha256")
        length = item.get("bytes")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest) or not isinstance(length, int) or length < 0:
            raise _fail(f"export acceptance object has invalid SHA/length: {relative}")
        if relative in observed:
            raise _fail(f"duplicate export acceptance object: {relative}")
        observed[relative] = (digest, length)
    expected = {
        item.name.removeprefix("site/"): (item.sha256, item.length)
        for item in site_sources
    }
    for relative, file_digest in observed.items():
        if expected.get(relative) != file_digest:
            raise _fail(f"export acceptance object differs from accepted site: {relative}")
    if "added" in record or "changed" in record:
        added, changed = record.get("added"), record.get("changed")
        if (not isinstance(added, list) or not isinstance(changed, list)
                or any(not isinstance(item, str) for item in added + changed)
                or len(set(added + changed)) != len(added) + len(changed)
                or set(observed) != set(added + changed)):
            raise _fail("export acceptance objects differ from its added/changed path lists")
    return _hash_file(path)[0]


def _read_package_report(path: Path, archive: Path, provenance: Mapping[str, Any],
                         sources: Sequence[ExpectedFile], expected_names: set[str],
                         observed: Mapping[str, Mapping[str, Any]]) -> tuple[dict[str, Any], str]:
    report = _read_json(path, "package report")
    if report.get("schema") != PACKAGE_SCHEMA or report.get("network_performed") is not False:
        raise _fail("package report schema or no-network assertion is invalid")
    if report.get("archive") != archive.name:
        raise _fail("package report archive name differs from configured archive")
    if report.get("project_prefix") != provenance.get("base_path"):
        raise _fail("package report project prefix differs from accepted export")
    source_manifest_sha = _sha256_bytes(_canonical_source_manifest(sources))
    if report.get("source_manifest_sha256") != source_manifest_sha:
        raise _fail("package report source manifest SHA differs from accepted site/support members")
    if report.get("source_member_count") != len(sources):
        raise _fail("package report source member count mismatch")
    if report.get("site_member_count") != sum(item.source_kind == "site" for item in sources):
        raise _fail("package report site member count mismatch")
    if report.get("package_member_count") != len(expected_names):
        raise _fail("package report package member count mismatch")
    compression = report.get("compression")
    if not isinstance(compression, dict) or compression.get("method") != "DEFLATE" or compression.get("images_reencoded") is not False:
        raise _fail("package report compression/source-byte assertion is invalid")

    verification = report.get("verification")
    if not isinstance(verification, dict):
        raise _fail("package report is missing verification results")
    for key in ("crc_sha_length_all_passed", "whitelist_exact", "checksums_exact"):
        if verification.get(key) is not True:
            raise _fail(f"package report verification {key} is not true")
    if verification.get("member_count") != len(expected_names):
        raise _fail("package report verified member count mismatch")
    report_members = verification.get("members")
    if not isinstance(report_members, list):
        raise _fail("package report verification members must be a list")
    report_by_name = {item.get("path"): item for item in report_members if isinstance(item, dict)}
    if len(report_by_name) != len(report_members) or set(report_by_name) != set(expected_names):
        raise _fail("package report member list does not exactly match the package whitelist")
    for name, actual in observed.items():
        reported = report_by_name[name]
        if (reported.get("sha256"), reported.get("bytes"), reported.get("crc32"), reported.get("compressed_bytes")) != (
            actual["sha256"], actual["bytes"], actual["crc32"], actual["compressed_bytes"]
        ):
            raise _fail(f"package report member digest/length/CRC mismatch: {name}")

    archive_sha, archive_bytes = _hash_file(archive)
    if (verification.get("archive_sha256"), verification.get("archive_bytes")) != (archive_sha, archive_bytes):
        raise _fail("package report archive SHA/length mismatch")
    sidecar_name = archive.name + ".sha256"
    if report.get("sidecar") != sidecar_name:
        raise _fail("package report sidecar name mismatch")
    sidecar = archive.with_name(sidecar_name)
    _regular_file(sidecar, "package checksum sidecar")
    sidecar_sha, sidecar_bytes = _hash_file(sidecar)
    if (report.get("sidecar_sha256"), report.get("sidecar_bytes")) != (sidecar_sha, sidecar_bytes):
        raise _fail("package report sidecar SHA/length mismatch")
    try:
        sidecar_text = sidecar.read_text(encoding="ascii")
    except (OSError, UnicodeError) as exc:
        raise _fail(f"package checksum sidecar is not ASCII: {exc}") from exc
    if sidecar_text != f"{archive_sha}  {archive.name}\n":
        raise _fail("package checksum sidecar does not match the archive")
    return report, _hash_file(path)[0]


def _verify_archive(archive: Path, sources: Sequence[ExpectedFile], provenance: Mapping[str, Any],
                    report_path: Path) -> tuple[dict[str, Any], dict[str, bytes], str]:
    expected_names = _expected_package_names(sources)
    expected_sites = {f"site/{item.name[5:]}": item for item in sources if item.source_kind == "site"}
    expected_support = {item.name: item for item in sources if item.source_kind == "support"}
    try:
        archive_handle = zipfile.ZipFile(archive, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise _fail(f"configured archive cannot be opened: {exc}") from exc

    observed: dict[str, dict[str, Any]] = {}
    special: dict[str, bytes] = {}
    with archive_handle as zf:
        by_name = _validate_zip_infos(zf.infolist(), expected_names)
        for name, info in by_name.items():
            digest, length, crc, payload = _read_zip_member(zf, info, keep=name in {
                "FILE_SHA256SUMS.txt", "archive-metadata.json", "README.md", "START_BROWSE.cmd",
            })
            if crc != info.CRC:
                raise _fail(f"ZIP member CRC mismatch: {name}")
            observed[name] = {
                "path": name,
                "sha256": digest,
                "bytes": length,
                "crc32": f"{crc:08x}",
                "compressed_bytes": info.compress_size,
            }
            if name in expected_sites:
                source = expected_sites[name]
                if (digest, length) != (source.sha256, source.length):
                    raise _fail(f"accepted site file differs from ZIP member: {name}")
            elif name in expected_support:
                source = expected_support[name]
                if (digest, length) != (source.sha256, source.length):
                    raise _fail(f"package support file differs from checkout: {name}")
            elif payload is not None:
                special[name] = payload

        checksum_data = special.get("FILE_SHA256SUMS.txt")
        metadata_data = special.get("archive-metadata.json")
        if checksum_data is None or metadata_data is None:
            raise _fail("ZIP lacks readable checksums or archive metadata")
        parsed_checksums = _parse_checksums(checksum_data)
        checksum_expected = {
            name: (data["sha256"], data["bytes"])
            for name, data in observed.items()
            if name != "FILE_SHA256SUMS.txt"
        }
        if parsed_checksums != checksum_expected:
            raise _fail("FILE_SHA256SUMS.txt does not exactly match package members")

        try:
            metadata = json.loads(metadata_data.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise _fail(f"archive-metadata.json is invalid: {exc}") from exc
        if not isinstance(metadata, dict) or metadata.get("schema") != PACKAGE_SCHEMA:
            raise _fail("archive-metadata.json schema is invalid")
        prefix = provenance.get("base_path")
        if metadata.get("project_prefix") != prefix:
            raise _fail("archive-metadata.json project prefix mismatch")
        if metadata.get("baseline_timestamp") != provenance.get("anchor_timestamp"):
            raise _fail("archive-metadata.json baseline timestamp differs from accepted export")
        if metadata.get("network_performed") is not False or metadata.get("checksum_file") != "FILE_SHA256SUMS.txt":
            raise _fail("archive-metadata.json package assertions are invalid")
        if metadata.get("member_count") != len(expected_names) or metadata.get("source_member_count") != len(sources):
            raise _fail("archive-metadata.json member count mismatch")
        site_count = sum(item.source_kind == "site" for item in sources)
        if metadata.get("site_member_count") != site_count:
            raise _fail("archive-metadata.json site member count mismatch")

        expected_generated = [
            {"path": name, "sha256": observed[name]["sha256"], "bytes": observed[name]["bytes"]}
            for name in ("README.md", "START_BROWSE.cmd")
        ]
        if metadata.get("generated_members") != expected_generated:
            raise _fail("archive-metadata.json generated members differ from package payloads")

        expected_records = [item.source_record() for item in sorted(sources, key=lambda item: item.name)]
        if metadata.get("source_members") != expected_records:
            raise _fail("archive-metadata.json source members differ from accepted export and support files")
        manifest_sha = _sha256_bytes(_canonical_source_manifest(sources))
        if metadata.get("source_manifest_sha256") != manifest_sha:
            raise _fail("archive-metadata.json source manifest SHA mismatch")

        try:
            launcher_expected = packager.make_launcher()
            readme_expected = packager.make_readme(dict(provenance), str(metadata["processed_date"]), site_count)
        except (KeyError, TypeError, ValueError) as exc:
            raise _fail(f"archive metadata cannot regenerate its generated members: {exc}") from exc
        if (special.get("START_BROWSE.cmd"), special.get("README.md")) != (launcher_expected, readme_expected):
            raise _fail("generated README or launcher differs from packager output")

    # Re-read per-member checksums from the package report and tie them to the
    # independently streamed ZIP results.
    report, report_sha = _read_package_report(report_path, archive, provenance, sources, expected_names, observed)
    verification = report["verification"]
    if report.get("processed_date") != metadata.get("processed_date"):
        raise _fail("package report processed date differs from archive metadata")
    if report.get("baseline_timestamp") != metadata.get("baseline_timestamp"):
        raise _fail("package report baseline timestamp differs from archive metadata")
    actual_archive_sha = _hash_file(archive)[0]
    if verification["archive_sha256"] != actual_archive_sha:
        raise _fail("package report and independently read archive hash differ")
    member_records = [observed[name] for name in sorted(observed)]
    return {
        "archive_sha256": actual_archive_sha,
        "archive_bytes": verification["archive_bytes"],
        "member_count": len(observed),
        "whitelist_exact": True,
        "checksums_exact": True,
        "crc_sha_length_all_passed": True,
        "member_inventory_sha256": _sha256_bytes(json.dumps(
            member_records, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")),
        "members": member_records,
        "package_report_sha256": report_sha,
        "package_metadata_sha256": observed["archive-metadata.json"]["sha256"],
        "checksum_file_sha256": observed["FILE_SHA256SUMS.txt"]["sha256"],
    }, special, report_sha


def _extract_verified(archive: Path, destination: Path, expected_names: set[str],
                      expected_members: Sequence[Mapping[str, Any]]) -> int:
    # _verify_archive returns an ordered JSON member list, not an index.
    member_index = {item["path"]: item for item in expected_members}
    if len(member_index) != len(expected_members) or set(member_index) != expected_names:
        raise _fail("verified extraction inventory differs from the exact member list")
    before = _require_disk_floor("before extraction")
    if destination.exists():
        raise _fail(f"refusing to overwrite existing smoke extraction: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir(parents=False, exist_ok=False)
    written = 0
    with zipfile.ZipFile(archive, "r") as zf:
        infos = _validate_zip_infos(zf.infolist(), expected_names)
        for name, info in infos.items():
            if info.file_size >= LARGE_WRITE_THRESHOLD_BYTES:
                _require_disk_floor(f"before large extraction write {name}")
            target = destination.joinpath(*name.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                with zf.open(info, "r") as source, target.open("xb") as output:
                    digest = hashlib.sha256()
                    crc = 0
                    total = 0
                    for chunk in iter(lambda: source.read(READ_CHUNK_BYTES), b""):
                        output.write(chunk)
                        digest.update(chunk)
                        crc = zlib.crc32(chunk, crc)
                        total += len(chunk)
                        if total > info.file_size:
                            raise _fail(f"extraction expanded beyond recorded size: {name}")
            except (OSError, RuntimeError, zipfile.BadZipFile, EOFError) as exc:
                raise _fail(f"cannot extract verified member {name}: {exc}") from exc
            actual = member_index.get(name)
            if actual is None or total != info.file_size or (crc & 0xFFFFFFFF) != info.CRC:
                raise _fail(f"extracted member length/CRC mismatch: {name}")
            if digest.hexdigest() != actual.get("sha256") or total != actual.get("bytes") or f"{crc & 0xFFFFFFFF:08x}" != actual.get("crc32"):
                raise _fail(f"archive member changed between verification and extraction: {name}")
            written += total
    return written


def _start_server(package_root: Path, base_path: str) -> tuple[subprocess.Popen[str], str]:
    script = package_root / "tools" / "serve_pages_preview.py"
    site = package_root / "site"
    _regular_file(script, "packaged preview server")
    if not site.is_dir() or _is_reparse_or_link(site):
        raise _fail("extracted package site directory is missing or unsafe")
    process = subprocess.Popen(
        [sys.executable, str(script), "--site", str(site), "--port", "0"],
        cwd=package_root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    lines: queue.Queue[str | None] = queue.Queue()

    def collect() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            lines.put(line.rstrip("\r\n"))
        lines.put(None)

    threading.Thread(target=collect, daemon=True, name="portable-preview-output").start()
    deadline = time.monotonic() + SERVER_READY_SECONDS
    pattern = re.compile(r"^Archive preview: http://127\.0\.0\.1:(\d+)(/.*)$")
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise _fail(f"packaged preview server exited before readiness ({process.returncode})")
        try:
            line = lines.get(timeout=min(0.25, max(0.01, deadline - time.monotonic())))
        except queue.Empty:
            continue
        if line is None:
            break
        match = pattern.fullmatch(line)
        if match:
            if match.group(2) != base_path:
                _stop_server(process)
                raise _fail("packaged preview server announced a different project prefix")
            return process, f"http://127.0.0.1:{match.group(1)}"
    _stop_server(process)
    raise _fail("packaged preview server did not become ready within 60 seconds")


def _stop_server(process: subprocess.Popen[str]) -> int | None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=SERVER_STOP_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=SERVER_STOP_SECONDS)
    return process.poll()


def _http_request(origin: str, method: str, url_path: str, *, follow_redirects: bool = True) -> tuple[int, Mapping[str, str], bytes, str]:
    parsed_origin = urlsplit(origin)
    if parsed_origin.hostname != "127.0.0.1" or parsed_origin.port is None:
        raise _fail("preview server origin is not loopback")
    request_path = url_path
    for redirect_count in range(MAX_REDIRECTS + 1):
        conn = http.client.HTTPConnection("127.0.0.1", parsed_origin.port, timeout=8)
        try:
            conn.request(method, request_path)
            response = conn.getresponse()
            headers = {key.casefold(): value for key, value in response.getheaders()}
            body = response.read()
            if follow_redirects and response.status in {301, 302, 303, 307, 308}:
                location = headers.get("location")
                if location is None or redirect_count == MAX_REDIRECTS:
                    raise _fail(f"HTTP redirect limit/Location error for {request_path}")
                parsed_location = urlsplit(location)
                next_path = parsed_location.path
                if parsed_location.scheme or parsed_location.netloc or not next_path.startswith("/"):
                    raise _fail("preview server returned an external or malformed redirect")
                request_path = next_path + (("?" + parsed_location.query) if parsed_location.query else "")
                continue
            return response.status, headers, body, request_path
        except OSError as exc:
            raise _fail(f"local preview HTTP {method} failed for {request_path}: {exc}") from exc
        finally:
            conn.close()
    raise _fail(f"HTTP redirect limit exceeded for {url_path}")


def _smoke_check(package_root: Path, accepted_site: Path, base_path: str,
                 smoke_paths: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    process, origin = _start_server(package_root, base_path)
    results: list[dict[str, Any]] = []
    try:
        root_status, root_headers, _, _ = _http_request(origin, "GET", "/", follow_redirects=False)
        if root_status != 302 or root_headers.get("location") != base_path:
            raise _fail("server root does not redirect into the accepted project prefix")
        results.append({"method": "GET", "request_path": "/", "status": root_status,
                        "location": root_headers.get("location"), "prefix_redirect_passed": True})
        for entry in smoke_paths:
            if not isinstance(entry, dict):
                raise _fail("each smoke_paths entry must be an object")
            url_path = entry.get("url_path")
            site_relative = _safe_relative(entry.get("site_relative"), "smoke site_relative")
            mime = entry.get("expected_mime")
            parsed_url = urlsplit(url_path) if isinstance(url_path, str) else None
            if (parsed_url is None or parsed_url.scheme or parsed_url.netloc or parsed_url.query or parsed_url.fragment
                    or not parsed_url.path.startswith(base_path) or "\\" in url_path or "\x00" in url_path):
                raise _fail(f"smoke URL must stay beneath the accepted project prefix: {url_path}")
            expected_url_path = base_path + quote(site_relative, safe="/-._~")
            if parsed_url.path != expected_url_path or unquote(parsed_url.path) != base_path + site_relative:
                raise _fail(f"smoke URL does not map exactly to site_relative: {url_path}")
            if not isinstance(mime, str) or not mime:
                raise _fail(f"smoke path has no expected MIME: {url_path}")
            methods = entry.get("methods", ["GET", "HEAD"])
            if methods != ["GET", "HEAD"]:
                raise _fail(f"smoke path methods must be exactly GET and HEAD: {url_path}")
            expected_file = accepted_site.joinpath(*site_relative.split("/"))
            expected_file = expected_file.resolve(strict=True)
            if not expected_file.is_relative_to(accepted_site.resolve()) or not expected_file.is_file():
                raise _fail(f"smoke expected file is missing or escapes accepted_site: {site_relative}")
            _regular_file(expected_file, "smoke expected site file")
            expected_sha, expected_len = _hash_file(expected_file)
            expected_bytes = expected_file.read_bytes()
            for method in methods:
                status, headers, body, final_path = _http_request(origin, method, url_path)
                if status != 200:
                    raise _fail(f"smoke {method} returned HTTP {status}: {url_path}")
                if not final_path.startswith(base_path):
                    raise _fail(f"smoke redirect escaped project prefix: {url_path}")
                if headers.get("content-type", "").casefold() != mime.casefold():
                    raise _fail(f"smoke MIME mismatch for {url_path}: {headers.get('content-type')!r} != {mime!r}")
                if headers.get("content-length") != str(expected_len):
                    raise _fail(f"smoke Content-Length mismatch for {url_path}")
                if method == "GET":
                    if body != expected_bytes or _sha256_bytes(body) != expected_sha:
                        raise _fail(f"smoke GET bytes differ from accepted_site: {url_path}")
                elif body:
                    raise _fail(f"smoke HEAD returned a body: {url_path}")
                results.append({
                    "method": method,
                    "request_path": url_path,
                    "final_path": final_path,
                    "status": status,
                    "mime": headers.get("content-type"),
                    "bytes": expected_len,
                    "sha256": expected_sha,
                    "body_matches_accepted_site": method == "GET",
                })
    finally:
        _stop_server(process)
    return results


def _check_smoke_paths(smoke_paths: Any, prefix: str, accepted_site: Path) -> None:
    if not isinstance(smoke_paths, list) or not smoke_paths:
        raise _fail("smoke_paths must be a non-empty list")
    seen: set[str] = set()
    for entry in smoke_paths:
        if not isinstance(entry, dict):
            raise _fail("each smoke_paths entry must be an object")
        url_path = entry.get("url_path")
        if not isinstance(url_path, str):
            raise _fail(f"smoke URL is outside accepted project prefix: {url_path}")
        parsed_url = urlsplit(url_path)
        if (parsed_url.scheme or parsed_url.netloc or parsed_url.query or parsed_url.fragment
                or not parsed_url.path.startswith(prefix) or "\\" in url_path or "\x00" in url_path):
            raise _fail(f"smoke URL is outside accepted project prefix: {url_path}")
        if url_path in seen:
            raise _fail(f"duplicate smoke URL path: {url_path}")
        seen.add(url_path)
        relative = _safe_relative(entry.get("site_relative"), "smoke site_relative")
        if parsed_url.path != prefix + quote(relative, safe="/-._~") or unquote(parsed_url.path) != prefix + relative:
            raise _fail(f"smoke URL does not map exactly to site_relative: {url_path}")
        expected = accepted_site.joinpath(*relative.split("/"))
        try:
            expected_resolved = expected.resolve(strict=True)
            expected_resolved.relative_to(accepted_site.resolve())
        except (OSError, ValueError) as exc:
            raise _fail(f"smoke site_relative is missing or escapes accepted_site: {relative}") from exc
        _regular_file(expected_resolved, "smoke expected site file")
        if not isinstance(entry.get("expected_mime"), str) or not entry["expected_mime"]:
            raise _fail(f"smoke expected_mime is required: {url_path}")
        if entry.get("methods", ["GET", "HEAD"]) != ["GET", "HEAD"]:
            raise _fail(f"smoke methods must be exactly GET and HEAD: {url_path}")


def _write_receipt(path: Path, receipt: Mapping[str, Any]) -> None:
    _require_disk_floor("before output receipt write")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise _fail(f"refusing to overwrite output receipt: {path}") from exc
    except OSError as exc:
        raise _fail(f"cannot write output receipt: {exc}") from exc


def run_check(config_path: Path) -> dict[str, Any]:
    config_path = _resolve_path(str(config_path), "config", must_exist=True)
    config = _load_config(config_path)
    accepted_site = _resolve_path(config["accepted_site"], "accepted_site", must_exist=True)
    archive = _resolve_path(config["archive"], "archive", must_exist=True)
    package_report_path = _resolve_path(config["package_report"], "package_report", must_exist=True)
    export_acceptance_path = _resolve_path(config["export"]["path"], "export acceptance", must_exist=True)
    root_acceptance_path = _resolve_path(config["root_browser_acceptance"]["path"], "root browser acceptance", must_exist=True)
    output_receipt = _resolve_path(config["output_receipt"], "output_receipt", must_exist=False)
    if not accepted_site.is_dir():
        raise _fail("accepted_site must be a directory")
    _regular_file(archive, "portable archive")
    _regular_file(package_report_path, "package report")
    if output_receipt.exists():
        raise _fail(f"refusing to overwrite output receipt: {output_receipt}")

    version = str(config["version"])
    smoke_root = REPOSITORY_ROOT / ".scratch" / f"portable smoke 20261022 {version}"
    if smoke_root.exists():
        raise _fail(f"refusing to overwrite existing smoke extraction: {smoke_root}")
    try:
        smoke_root.resolve(strict=False).relative_to(REPOSITORY_ROOT)
    except ValueError as exc:
        raise _fail("smoke extraction path escapes the repository") from exc
    input_paths = {
        config_path,
        archive,
        package_report_path,
        export_acceptance_path,
        root_acceptance_path,
        archive.with_name(archive.name + ".sha256"),
    }
    if output_receipt in input_paths or output_receipt == accepted_site:
        raise _fail("output receipt collides with an input path")
    if (output_receipt.is_relative_to(accepted_site) or output_receipt.is_relative_to(smoke_root)
            or archive.is_relative_to(output_receipt) or package_report_path.is_relative_to(output_receipt)):
        raise _fail("output receipt must stay outside accepted_site and smoke extraction")

    disk_before = _require_disk_floor("before batch")
    sources, provenance, provenance_sha, prefix = _expected_source_files(accepted_site)
    _check_smoke_paths(config["smoke_paths"], prefix, accepted_site)
    export_acceptance_sha = _read_export_acceptance(config, accepted_site, sources, provenance_sha)
    acceptance_sha, _acceptance = _read_root_acceptance(config, accepted_site, provenance_sha)

    expected_names = _expected_package_names(sources)
    verification, special_payloads, package_report_sha = _verify_archive(
        archive, sources, provenance, package_report_path,
    )
    # Support and site sources are re-hashed after ZIP validation to catch a
    # concurrent change between inventory collection and verification.
    for source in sources:
        current_sha, current_len = _hash_file(source.source)
        if (current_sha, current_len) != (source.sha256, source.length):
            raise _fail(f"accepted source changed during verification: {source.name}")

    disk_before_extract = _require_disk_floor("before extraction batch")
    extracted_bytes = _extract_verified(archive, smoke_root, expected_names, verification["members"])
    smoke_results = _smoke_check(smoke_root, accepted_site, prefix, config["smoke_paths"])
    disk_after_smoke = _require_disk_floor("after local preview smoke")

    report_digest, report_length = _hash_file(package_report_path)
    sidecar_sha, sidecar_length = _hash_file(archive.with_name(archive.name + ".sha256"))
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "checked_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "accepted",
        "version": version,
        "network_performed": False,
        "accepted_site": str(accepted_site.relative_to(REPOSITORY_ROOT).as_posix()),
        "accepted_export_provenance_sha256": provenance_sha,
        "export_acceptance_sha256": export_acceptance_sha,
        "root_browser_acceptance_sha256": acceptance_sha,
        "project_prefix": prefix,
        "archive": {
            "path": archive.relative_to(REPOSITORY_ROOT).as_posix(),
            "sha256": verification["archive_sha256"],
            "bytes": verification["archive_bytes"],
            "member_count": verification["member_count"],
            "whitelist_exact": verification["whitelist_exact"],
            "checksums_exact": verification["checksums_exact"],
            "crc_sha_length_all_passed": verification["crc_sha_length_all_passed"],
            "member_inventory_sha256": verification["member_inventory_sha256"],
            "archive_metadata_sha256": verification["package_metadata_sha256"],
            "checksum_file_sha256": verification["checksum_file_sha256"],
            "sidecar_sha256": sidecar_sha,
            "sidecar_bytes": sidecar_length,
        },
        "package_report": {
            "path": package_report_path.relative_to(REPOSITORY_ROOT).as_posix(),
            "sha256": report_digest,
            "bytes": report_length,
            "bound_sha256": package_report_sha,
        },
        "smoke_extraction": smoke_root.relative_to(REPOSITORY_ROOT).as_posix(),
        "output_receipt": output_receipt.relative_to(REPOSITORY_ROOT).as_posix(),
        "extracted_bytes": extracted_bytes,
        "smoke_paths": smoke_results,
        "disk_free_bytes": {
            "before_batch": disk_before,
            "before_extraction": disk_before_extract,
            "after_smoke": disk_after_smoke,
            "required_floor": MIN_FREE_BYTES,
        },
    }
    _write_receipt(output_receipt, receipt)
    disk_after_receipt = _require_disk_floor("after output receipt")
    receipt["disk_free_bytes"]["after_receipt"] = disk_after_receipt
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="root-authored v54+ portable-check config JSON")
    args = parser.parse_args(argv)
    try:
        receipt = run_check(args.config)
    except (PortableCheckError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"portable_check: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": receipt["status"],
        "version": receipt["version"],
        "archive_sha256": receipt["archive"]["sha256"],
        "member_count": receipt["archive"]["member_count"],
        "smoke_paths": len(receipt["smoke_paths"]),
        "receipt": receipt["output_receipt"],
        "disk_free_after_receipt": receipt["disk_free_bytes"]["after_receipt"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

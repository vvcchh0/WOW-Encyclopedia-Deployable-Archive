#!/usr/bin/env python3
"""Build a portable, browse-only ZIP of a generated static site.

The package contains the supplied site under ``site/``, the loopback preview
server, a notice, and small generated launch, README, metadata, and checksum
files.  It is deliberately one-shot: output, partial output, sidecar, and
report paths must all be new.  No network access is performed.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import zlib
import zipfile
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNK_SIZE = 1024 * 1024
DEFLATE_LEVEL = 6
MIN_FREE_BYTES = 10 * 1024**3 + 256 * 1024**2
ZIP_MARGIN_BYTES = 16 * 1024 * 1024
PACKAGE_SCHEMA = "wow-encyclopedia-portable-archive/v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXCLUDED_COMPONENTS = {".git", "rawresearch"}
EXCLUDED_SUFFIXES = {".zip", ".7z", ".rar"}
SUPPORT_FILES = ("tools/serve_pages_preview.py", "NOTICE.md")


class ArchiveError(RuntimeError):
    """A recoverable packaging or validation error."""


@dataclass
class Member:
    name: str
    source: Path | None
    source_kind: str
    sha256: str
    bytes: int
    payload: bytes | None = None

    def metadata(self) -> dict[str, Any]:
        return {
            "path": self.name,
            "source_kind": self.source_kind,
            "source_path": self.name if self.source is not None else "generated",
            "source_sha256": self.sha256,
            "source_bytes": self.bytes,
        }


def _is_reparse_or_link(path: Path, *, entry: os.DirEntry[str] | None = None) -> bool:
    if path.is_symlink():
        return True
    try:
        details = entry.stat(follow_symlinks=False) if entry is not None else path.stat(follow_symlinks=False)
    except OSError as exc:
        raise ArchiveError(f"cannot inspect source member: {path}") from exc
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(details, "st_file_attributes", 0) & reparse_flag)


def safe_member_name(value: str) -> str:
    """Return a ZIP-safe slash path or reject traversal/special syntax."""

    normalized = value.replace("\\", "/")
    if not normalized or normalized.startswith("/"):
        raise ArchiveError(f"unsafe ZIP member path: {value!r}")
    if ":" in normalized.split("/", 1)[0]:
        raise ArchiveError(f"unsafe ZIP member path: {value!r}")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ArchiveError(f"unsafe ZIP member path: {value!r}")
    if any("\x00" in part for part in parts):
        raise ArchiveError(f"unsafe ZIP member path: {value!r}")
    if any(part.casefold() in EXCLUDED_COMPONENTS for part in parts):
        raise ArchiveError(f"excluded archive member path: {value!r}")
    if Path(parts[-1]).suffix.casefold() in EXCLUDED_SUFFIXES:
        raise ArchiveError(f"historical archive member is excluded: {value!r}")
    return normalized


def _assert_regular_file(path: Path) -> None:
    if _is_reparse_or_link(path):
        raise ArchiveError(f"symlink or reparse point is not allowed: {path}")
    try:
        details = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise ArchiveError(f"cannot inspect source file: {path}") from exc
    if not stat.S_ISREG(details.st_mode):
        raise ArchiveError(f"source member is not a regular file: {path}")


def _hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
                digest.update(chunk)
                total += len(chunk)
    except OSError as exc:
        raise ArchiveError(f"cannot read source file: {path}") from exc
    return digest.hexdigest(), total


def _member_from_file(name: str, source: Path, source_kind: str) -> Member:
    _assert_regular_file(source)
    digest, length = _hash_file(source)
    return Member(name, source, source_kind, digest, length)


def _member_from_bytes(name: str, payload: bytes) -> Member:
    return Member(
        name=name,
        source=None,
        source_kind="generated",
        sha256=hashlib.sha256(payload).hexdigest(),
        bytes=len(payload),
        payload=payload,
    )


def _walk_site(site: Path) -> list[tuple[str, Path]]:
    if not site.is_dir() or _is_reparse_or_link(site):
        raise ArchiveError(f"site must be a normal directory: {site}")
    found: list[tuple[str, Path]] = []
    pending = [site]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name.casefold())
        except OSError as exc:
            raise ArchiveError(f"cannot enumerate site directory: {directory}") from exc
        for entry in entries:
            path = Path(entry.path)
            if _is_reparse_or_link(path, entry=entry):
                raise ArchiveError(f"symlink or reparse point is not allowed: {path}")
            relative = path.relative_to(site).as_posix()
            member_name = safe_member_name(f"site/{relative}")
            try:
                is_directory = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except OSError as exc:
                raise ArchiveError(f"cannot inspect site member: {path}") from exc
            if is_directory:
                pending.append(path)
            elif is_file:
                found.append((member_name, path))
            else:
                raise ArchiveError(f"unsupported site member: {path}")
    return sorted(found, key=lambda item: item[0])


def _load_provenance(site: Path) -> dict[str, Any]:
    path = site / "export-provenance.json"
    _assert_regular_file(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ArchiveError("site/export-provenance.json is not valid UTF-8 JSON") from exc
    if not isinstance(data, dict):
        raise ArchiveError("site/export-provenance.json must contain an object")
    anchor = data.get("anchor_timestamp")
    prefix = data.get("base_path")
    if not isinstance(anchor, str) or not re.fullmatch(r"\d{14}", anchor):
        raise ArchiveError("provenance anchor_timestamp is invalid")
    if not isinstance(prefix, str) or not prefix.startswith("/") or not prefix.endswith("/") or ".." in prefix:
        raise ArchiveError("provenance base_path is invalid")
    if "\x00" in prefix:
        raise ArchiveError("provenance base_path contains NUL")
    return data


def collect_source_members(site: Path, project_root: Path) -> tuple[list[Member], dict[str, Any]]:
    provenance = _load_provenance(site)
    members = [
        _member_from_file(name, path, "site")
        for name, path in _walk_site(site)
    ]
    for relative in SUPPORT_FILES:
        source = project_root / relative
        name = safe_member_name(relative)
        members.append(_member_from_file(name, source, "support"))
    names = [item.name for item in members]
    if len(names) != len(set(names)):
        raise ArchiveError("source member names are not unique")
    return sorted(members, key=lambda item: item.name), provenance


def _canonical_manifest(members: Iterable[Member]) -> bytes:
    lines = [f"{item.sha256}  {item.bytes}  {item.name}" for item in members]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _format_gap_note(provenance: dict[str, Any]) -> str:
    stats = provenance.get("stats")
    if isinstance(stats, dict) and isinstance(stats.get("output_files"), int):
        return (
            f"The current reconstruction contains {stats['output_files']:,} derived files; "
            "some historical resources remain unavailable and are marked in the site."
        )
    return "Some historical resources remain unavailable and are marked in the site."


def make_readme(provenance: dict[str, Any], processed_date: str, site_count: int) -> bytes:
    prefix = provenance["base_path"]
    text = (
        "# World of Warcraft Encyclopedia historical archive\n\n"
        f"A portable, browse-only reconstruction based on the 2008-05-12 21:00:44 "
        f"Wayback Machine capture. This package was processed on {processed_date}.\n\n"
        f"The generated site contains {site_count:,} static files and keeps its project "
        f"prefix `{prefix}`. It presents the preserved pages and media as a historical "
        "exhibit; retired account services and software installers are not active.\n\n"
        "## Browse locally\n\n"
        "Windows users can double-click `START_BROWSE.cmd`. It uses Python 3, starts "
        "the loopback server on an available port, and opens the project prefix in "
        "the default browser. Close the command window to stop the server.\n\n"
        "On other systems, run:\n\n"
        "```sh\n"
        "python tools/serve_pages_preview.py --site site --port 0 --open-browser\n"
        "```\n\n"
        f"{_format_gap_note(provenance)}\n"
    )
    return text.encode("utf-8")


def make_launcher() -> bytes:
    text = (
        "@echo off\r\n"
        "setlocal\r\n"
        "cd /d \"%~dp0\"\r\n"
        "where py >nul 2>&1\r\n"
        "if not errorlevel 1 goto use_py\r\n"
        "where python >nul 2>&1\r\n"
        "if errorlevel 1 goto no_python\r\n"
        "python \"tools\\serve_pages_preview.py\" --site \"site\" --port 0 --open-browser\r\n"
        "set \"status=%errorlevel%\"\r\n"
        "goto finish\r\n"
        ":use_py\r\n"
        "py -3 \"tools\\serve_pages_preview.py\" --site \"site\" --port 0 --open-browser\r\n"
        "set \"status=%errorlevel%\"\r\n"
        "goto finish\r\n"
        ":no_python\r\n"
        "echo Python 3 was not found.\r\n"
        "set \"status=1\"\r\n"
        ":finish\r\n"
        "if not \"%status%\"==\"0\" echo Browser server exited with code %status%.\r\n"
        "exit /b %status%\r\n"
    )
    return text.encode("utf-8")


def make_metadata(
    source_members: list[Member],
    provenance: dict[str, Any],
    processed_date: str,
    readme: Member,
    launcher: Member,
) -> bytes:
    source_manifest = _canonical_manifest(source_members)
    metadata: dict[str, Any] = {
        "schema": PACKAGE_SCHEMA,
        "baseline_timestamp": provenance["anchor_timestamp"],
        "processed_date": processed_date,
        "project_prefix": provenance["base_path"],
        "site_member_count": sum(item.source_kind == "site" for item in source_members),
        "source_member_count": len(source_members),
        "member_count": len(source_members) + 4,
        "source_manifest_sha256": hashlib.sha256(source_manifest).hexdigest(),
        "source_members": [item.metadata() for item in source_members],
        "generated_members": [
            {"path": readme.name, "sha256": readme.sha256, "bytes": readme.bytes},
            {"path": launcher.name, "sha256": launcher.sha256, "bytes": launcher.bytes},
        ],
        "checksum_file": "FILE_SHA256SUMS.txt",
        "network_performed": False,
    }
    return (json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def make_checksums(members: list[Member]) -> bytes:
    lines = ["# SHA-256  bytes  path"]
    for item in sorted(members, key=lambda member: member.name):
        if item.name == "FILE_SHA256SUMS.txt":
            continue
        lines.append(f"{item.sha256}  {item.bytes}  {item.name}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_member_set(
    source_members: list[Member],
    provenance: dict[str, Any],
    processed_date: str,
) -> list[Member]:
    readme = _member_from_bytes(
        "README.md",
        make_readme(provenance, processed_date, sum(item.source_kind == "site" for item in source_members)),
    )
    launcher = _member_from_bytes("START_BROWSE.cmd", make_launcher())
    metadata = _member_from_bytes(
        "archive-metadata.json",
        make_metadata(source_members, provenance, processed_date, readme, launcher),
    )
    without_checksums = source_members + [readme, launcher, metadata]
    checksums = _member_from_bytes("FILE_SHA256SUMS.txt", make_checksums(without_checksums))
    members = without_checksums + [checksums]
    names = [item.name for item in members]
    if len(names) != len(set(names)):
        raise ArchiveError("package member names are not unique")
    return sorted(members, key=lambda item: item.name)


def _parse_processed_date(value: str) -> tuple[str, tuple[int, int, int]]:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ArchiveError("processed date must be YYYY-MM-DD") from exc
    if parsed.year < 1980 or parsed.year > 2107:
        raise ArchiveError("processed date must be representable in ZIP timestamps")
    return parsed.isoformat(), (parsed.year, parsed.month, parsed.day)


def _zip_info(name: str, package_date: tuple[int, int, int]) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(*package_date, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    # Supplying a ZipInfo bypasses ZipFile's constructor-level compression
    # default in some Python versions. Set the private field intentionally so
    # every streamed member uses the requested DEFLATE level.
    info._compresslevel = DEFLATE_LEVEL
    info.create_system = 0
    info.external_attr = 0o100644 << 16
    return info


def _write_member(zf: zipfile.ZipFile, member: Member, package_date: tuple[int, int, int]) -> None:
    with zf.open(_zip_info(member.name, package_date), "w", force_zip64=True) as target:
        if member.payload is not None:
            target.write(member.payload)
            return
        if member.source is None:
            raise ArchiveError(f"member has no source: {member.name}")
        digest = hashlib.sha256()
        total = 0
        try:
            with member.source.open("rb") as source:
                for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
                    digest.update(chunk)
                    total += len(chunk)
                    target.write(chunk)
        except OSError as exc:
            raise ArchiveError(f"source changed or became unreadable: {member.name}") from exc
        if digest.hexdigest() != member.sha256 or total != member.bytes:
            raise ArchiveError(f"source changed while packaging: {member.name}")


def _open_exclusive(path: Path):
    """Create a new binary file without truncating a competitor's file."""

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError:
        raise FileExistsError(f"refusing an existing temporary output: {path}")
    return os.fdopen(descriptor, "w+b")


def _publish_no_clobber(temp: Path, final: Path) -> None:
    """Atomically create ``final`` from ``temp`` while refusing a race."""

    try:
        os.link(temp, final)
    except FileExistsError:
        raise FileExistsError(f"refusing to overwrite a competing output: {final}")
    except OSError as exc:
        raise ArchiveError(f"cannot publish without overwrite protection: {final}") from exc
    try:
        temp.unlink()
    except OSError as exc:
        raise ArchiveError(f"published output but could not remove owned temporary file: {temp}") from exc


def verify_sources_unchanged(members: Iterable[Member]) -> None:
    for member in members:
        if member.source is None:
            continue
        _assert_regular_file(member.source)
        digest, length = _hash_file(member.source)
        if digest != member.sha256 or length != member.bytes:
            raise ArchiveError(f"source changed during packaging: {member.name}")


def verify_site_unchanged(site: Path, members: Iterable[Member]) -> None:
    """Re-enumerate the site and detect added, removed, or changed files."""

    expected = {
        item.name: item
        for item in members
        if item.source_kind == "site"
    }
    current = {
        name: path
        for name, path in _walk_site(site)
    }
    if set(current) != set(expected):
        added = sorted(set(current) - set(expected))
        removed = sorted(set(expected) - set(current))
        raise ArchiveError(f"site file set changed during packaging: added={added[:5]}, removed={removed[:5]}")
    for name, path in current.items():
        digest, length = _hash_file(path)
        original = expected[name]
        if digest != original.sha256 or length != original.bytes:
            raise ArchiveError(f"site source changed during packaging: {name}")


def estimate_zip_upper_bound(members: Iterable[Member]) -> int:
    items = list(members)
    raw_bytes = sum(item.bytes for item in items)
    return raw_bytes + len(items) * 512 + ZIP_MARGIN_BYTES


def preflight(archive: Path, members: list[Member]) -> dict[str, Any]:
    if not archive.parent.exists():
        archive.parent.mkdir(parents=True, exist_ok=True)
    try:
        usage = shutil.disk_usage(archive.parent)
    except OSError as exc:
        raise ArchiveError(f"cannot inspect free space for archive target: {archive.parent}") from exc
    estimate = estimate_zip_upper_bound(members)
    free_after = usage.free - estimate
    result = {
        "disk_free_bytes_before": usage.free,
        "estimated_new_zip_bytes": estimate,
        "projected_disk_free_bytes": free_after,
        "minimum_free_bytes": MIN_FREE_BYTES,
        "disk_free_check": free_after > MIN_FREE_BYTES,
    }
    if not result["disk_free_check"]:
        raise ArchiveError(json.dumps({"preflight_failed": True, **result}, sort_keys=True))
    return result


def _read_member_stream(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    total = 0
    crc = 0
    with zf.open(info, "r") as source:
        for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
            digest.update(chunk)
            crc = zlib.crc32(chunk, crc)
            total += len(chunk)
    return digest.hexdigest(), total, crc & 0xFFFFFFFF


def parse_checksums(payload: bytes) -> dict[str, tuple[str, int]]:
    try:
        lines = payload.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ArchiveError("FILE_SHA256SUMS.txt is not UTF-8") from exc
    if not lines or lines[0] != "# SHA-256  bytes  path":
        raise ArchiveError("FILE_SHA256SUMS.txt has an invalid header")
    result: dict[str, tuple[str, int]] = {}
    for line in lines[1:]:
        if not line:
            continue
        parts = line.split("  ", 2)
        if len(parts) != 3 or not SHA256_RE.fullmatch(parts[0]):
            raise ArchiveError("FILE_SHA256SUMS.txt has a malformed entry")
        try:
            length = int(parts[1])
        except ValueError as exc:
            raise ArchiveError("FILE_SHA256SUMS.txt has an invalid length") from exc
        name = safe_member_name(parts[2])
        if name in result:
            raise ArchiveError(f"duplicate checksum path: {name}")
        result[name] = (parts[0], length)
    return result


def verify_archive(
    archive: Path,
    members: list[Member],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    expected = {item.name: item for item in members}
    observed: list[dict[str, Any]] = []
    try:
        zf = zipfile.ZipFile(archive, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise ArchiveError("generated ZIP cannot be opened") from exc
    with zf:
        infos = zf.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ArchiveError("ZIP contains duplicate member names")
        if set(names) != set(expected):
            missing = sorted(set(expected) - set(names))
            extra = sorted(set(names) - set(expected))
            raise ArchiveError(f"ZIP whitelist mismatch: missing={missing[:5]}, extra={extra[:5]}")
        for info in infos:
            safe_member_name(info.filename)
            if info.compress_type != zipfile.ZIP_DEFLATED:
                raise ArchiveError(f"ZIP member is not DEFLATE compressed: {info.filename}")
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode) or stat.S_ISDIR(mode):
                raise ArchiveError(f"ZIP member is not a regular file: {info.filename}")
            digest, length, crc = _read_member_stream(zf, info)
            expected_member = expected[info.filename]
            if digest != expected_member.sha256 or length != expected_member.bytes or crc != info.CRC:
                raise ArchiveError(f"ZIP member CRC/SHA/length mismatch: {info.filename}")
            observed.append(
                {
                    "path": info.filename,
                    "sha256": digest,
                    "bytes": length,
                    "crc32": f"{crc:08x}",
                    "compressed_bytes": info.compress_size,
                }
            )

        checksum_data = zf.read("FILE_SHA256SUMS.txt")
        parsed_checksums = parse_checksums(checksum_data)
        expected_checksums = {
            item.name: (item.sha256, item.bytes)
            for item in members
            if item.name != "FILE_SHA256SUMS.txt"
        }
        if parsed_checksums != expected_checksums:
            raise ArchiveError("FILE_SHA256SUMS.txt does not exactly cover package members")

        try:
            metadata = json.loads(zf.read("archive-metadata.json").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError) as exc:
            raise ArchiveError("archive-metadata.json is invalid") from exc
        if not isinstance(metadata, dict) or not isinstance(metadata.get("source_members"), list):
            raise ArchiveError("archive-metadata.json has an invalid source member list")
        source_expected = {
            item.name: (item.sha256, item.bytes)
            for item in members
            if item.source is not None
        }
        source_observed = {
            item.get("path"): (item.get("source_sha256"), item.get("source_bytes"))
            for item in metadata.get("source_members", [])
            if isinstance(item, dict)
        }
        if source_observed != source_expected:
            raise ArchiveError("archive-metadata.json source records do not match package")
        if metadata.get("project_prefix") != provenance["base_path"]:
            raise ArchiveError("archive-metadata.json project prefix mismatch")
        if metadata.get("member_count") != len(members):
            raise ArchiveError("archive-metadata.json member count mismatch")

    archive_sha, archive_bytes = _hash_file(archive)
    return {
        "archive_sha256": archive_sha,
        "archive_bytes": archive_bytes,
        "member_count": len(observed),
        "members": sorted(observed, key=lambda item: item["path"]),
        "crc_sha_length_all_passed": True,
        "whitelist_exact": True,
        "checksums_exact": True,
    }


def _paths_inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _ensure_new_outputs(
    site: Path,
    archive: Path,
    report: Path,
) -> tuple[Path, Path, Path, Path]:
    sidecar = archive.with_name(archive.name + ".sha256")
    partial = archive.with_name(archive.name + ".partial")
    sidecar_partial = sidecar.with_name(sidecar.name + ".partial")
    report_partial = report.with_name(report.name + ".partial")
    targets = [archive, sidecar, partial, sidecar_partial, report, report_partial]
    if len({path.resolve() for path in targets}) != len(targets):
        raise ArchiveError("archive, sidecar, partial, and report paths must be distinct")
    if any(os.path.lexists(path) for path in targets):
        raise FileExistsError("refusing to overwrite an existing output, partial, sidecar, or report")
    if _paths_inside(archive, site) or _paths_inside(report, site):
        raise ArchiveError("archive and report must be outside the source site")
    return sidecar, partial, report_partial, archive


def _write_report_atomic(path: Path, report_partial: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _write_bytes_no_clobber(report_partial, path, payload)


def _write_bytes_no_clobber(temp: Path, final: Path, payload: bytes) -> None:
    handle = None
    created = False
    try:
        handle = _open_exclusive(temp)
        created = True
        handle.write(payload)
        handle.flush()
        handle.close()
        handle = None
        _publish_no_clobber(temp, final)
    except Exception:
        if handle is not None:
            handle.close()
        if created and os.path.lexists(temp):
            temp.unlink()
        raise


def build_archive(
    *,
    site: Path,
    archive: Path,
    report: Path,
    processed_date: str,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    site = site.resolve()
    archive = archive.resolve()
    report = report.resolve()
    project_root = project_root.resolve()
    processed, package_date = _parse_processed_date(processed_date)
    if not site.is_dir():
        raise ArchiveError(f"site directory does not exist: {site}")
    sidecar, partial, report_partial, _ = _ensure_new_outputs(site, archive, report)
    source_members, provenance = collect_source_members(site, project_root)
    members = build_member_set(source_members, provenance, processed)
    preflight_info = preflight(archive, members)

    partial_handle = None
    partial_created = False
    try:
        partial_handle = _open_exclusive(partial)
        partial_created = True
        with zipfile.ZipFile(
            partial_handle,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=DEFLATE_LEVEL,
            allowZip64=True,
        ) as zf:
            for member in members:
                _write_member(zf, member, package_date)
        partial_handle.close()
        partial_handle = None
        verify_sources_unchanged(source_members)
        verify_site_unchanged(site, source_members)
        verification = verify_archive(partial, members, provenance)
        _publish_no_clobber(partial, archive)
        partial_created = False
    except Exception:
        if partial_handle is not None:
            partial_handle.close()
        if partial_created and os.path.lexists(partial):
            partial.unlink()
        raise

    sidecar_partial = sidecar.with_name(sidecar.name + ".partial")
    if sidecar_partial.exists():
        raise ArchiveError("refusing an existing sidecar partial")
    try:
        _write_bytes_no_clobber(
            sidecar_partial,
            sidecar,
            f"{verification['archive_sha256']}  {archive.name}\n".encode("ascii"),
        )
        sidecar_sha, sidecar_bytes = _hash_file(sidecar)
        source_manifest = _canonical_manifest(source_members)
        report_data = {
            "schema": PACKAGE_SCHEMA,
            "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "network_performed": False,
            "archive": archive.name,
            "sidecar": sidecar.name,
            "sidecar_sha256": sidecar_sha,
            "sidecar_bytes": sidecar_bytes,
            "processed_date": processed,
            "baseline_timestamp": provenance["anchor_timestamp"],
            "project_prefix": provenance["base_path"],
            "source_manifest_sha256": hashlib.sha256(source_manifest).hexdigest(),
            "source_member_count": len(source_members),
            "site_member_count": sum(item.source_kind == "site" for item in source_members),
            "package_member_count": len(members),
            "compression": {"method": "DEFLATE", "level": DEFLATE_LEVEL, "images_reencoded": False},
            "preflight": preflight_info,
            "verification": verification,
        }
        _write_report_atomic(report, report_partial, report_data)
    except Exception:
        raise
    return report_data


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True, help="generated static site directory")
    parser.add_argument("--archive", type=Path, required=True, help="new ZIP output path")
    parser.add_argument("--report", type=Path, required=True, help="new JSON report path")
    parser.add_argument("--processed-date", required=True, help="processing date in YYYY-MM-DD form")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = build_archive(
            site=args.site,
            archive=args.archive,
            report=args.report,
            processed_date=args.processed_date,
        )
    except (ArchiveError, OSError) as exc:
        print(f"package_pages_archive: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "archive": report["archive"],
                "archive_bytes": report["verification"]["archive_bytes"],
                "archive_sha256": report["verification"]["archive_sha256"],
                "members": report["package_member_count"],
                "report": str(args.report),
                "all_verified": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

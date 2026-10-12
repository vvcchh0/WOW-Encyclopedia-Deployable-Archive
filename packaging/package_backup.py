#!/usr/bin/env python3
"""Create and verify a portable snapshot ZIP for the local workspace.

The command is intentionally local-only.  It snapshots the selected source
files before writing, keeps the previous final archive while a uniquely named
partial archive is built, and replaces the final archive only after ZIP CRC
and per-source SHA-256 verification succeed.

Run from the workspace root with::

    python .\\packaging\\package_backup.py

The output is written below ``artifacts/``.  That directory is never part of
the source snapshot, and no existing final archive is removed on failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import time
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "WOW_Encyclopedia_20101203_source.zip"
OUTPUT_DIR = ROOT / "artifacts"
FINAL_ZIP = OUTPUT_DIR / PACKAGE_NAME
SHA_FILE = OUTPUT_DIR / f"{PACKAGE_NAME}.sha256"
VERIFICATION_FILE = OUTPUT_DIR / "package-verification.json"

SOURCE_DIRS = ("docs", "tools", "tests", "research", "backups", "packaging")
OPTIONAL_ROOT_FILES = ("README.md",)
INTERNAL_PREFIX = "WOW_Encyclopedia"
SUMS_NAME = f"{INTERNAL_PREFIX}/FILE_SHA256SUMS.txt"

# These are deliberately decimal workspace bytes and binary reserve bytes,
# matching the packaging contract supplied by the parent agent.
MAX_WORKSPACE_BYTES = 14_000_000_000
MIN_FREE_BYTES = 10 * 1024**3
RESERVE_BYTES = 64 * 1024**2
METADATA_RESERVE_BYTES = 4 * 1024**2
CHUNK_BYTES = 1024 * 1024

TEXT_SUFFIXES = {
    ".asm",
    ".c",
    ".cfg",
    ".conf",
    ".cpp",
    ".css",
    ".csv",
    ".h",
    ".hpp",
    ".htm",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".ps1",
    ".py",
    ".rst",
    ".sh",
    ".sql",
    ".svg",
    ".tex",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".xsl",
    ".yaml",
    ".yml",
}


class PackageError(RuntimeError):
    """Expected, actionable packaging failure."""


class SourceChangedError(PackageError):
    """A source file changed while the fixed snapshot was being packaged."""


@dataclass(frozen=True)
class SourceFile:
    path: Path
    relative: str
    size: int
    mtime_ns: int

    @property
    def internal_name(self) -> str:
        return f"{INTERNAL_PREFIX}/{self.relative}"


@dataclass(frozen=True)
class SourceSnapshot:
    files: tuple[SourceFile, ...]
    rawsourcebytes: int
    excluded: tuple[str, ...]


@dataclass
class WriteState:
    source_hashes: dict[str, str]
    source_bytes: int = 0
    partial_bytes: int = 0
    minimum_free_bytes: int | None = None
    last_free_bytes: int | None = None
    minimum_workspace_bytes: int | None = None
    last_workspace_bytes: int | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def disk_free_bytes() -> int:
    return int(shutil.disk_usage(ROOT).free)


def workspace_tree_size() -> int:
    """Return bytes occupied by files below ROOT without following symlink dirs."""
    total = 0
    pending = [ROOT]
    while pending:
        directory = pending.pop()
        try:
            entries = list(os.scandir(directory))
        except FileNotFoundError as exc:
            raise PackageError(f"workspace entry disappeared while measuring tree: {directory}") from exc
        except OSError as exc:
            raise PackageError(f"cannot scan workspace tree at {directory}: {exc}") from exc
        for entry in entries:
            try:
                if entry.is_symlink():
                    # Count the link itself but never follow it outside ROOT.
                    total += entry.stat(follow_symlinks=False).st_size
                elif entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
            except FileNotFoundError as exc:
                raise PackageError(f"workspace entry disappeared while measuring tree: {entry.path}") from exc
            except OSError as exc:
                raise PackageError(f"cannot stat workspace entry {entry.path}: {exc}") from exc
    return total


def safe_relative(path: Path) -> str:
    try:
        relative = path.resolve().relative_to(ROOT.resolve())
    except ValueError as exc:
        raise PackageError(f"source path escapes workspace: {path}") from exc
    return relative.as_posix()


def should_exclude(path: Path) -> bool:
    relative = safe_relative(path)
    parts = relative.split("/")
    return "artifacts" in parts or "__pycache__" in parts or path.suffix.casefold() == ".pyc"


def check_regular_source(path: Path) -> None:
    if path.is_symlink():
        raise PackageError(f"refusing symlink source (fixed snapshot requires regular files): {path}")
    try:
        mode = path.stat().st_mode
    except OSError as exc:
        raise PackageError(f"cannot stat source {path}: {exc}") from exc
    if not stat.S_ISREG(mode):
        raise PackageError(f"source is not a regular file: {path}")


def iter_tree_files(directory: Path) -> Iterator[Path]:
    """Yield regular files without following symlink directories."""
    if not directory.exists():
        return
    if directory.is_symlink():
        raise PackageError(f"refusing symlink source directory: {directory}")
    for entry in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
        if should_exclude(entry):
            continue
        if entry.is_dir():
            yield from iter_tree_files(entry)
        else:
            check_regular_source(entry)
            yield entry


def collect_sources() -> SourceSnapshot:
    files: list[SourceFile] = []
    excluded: list[str] = []
    seen: set[str] = set()

    for directory_name in SOURCE_DIRS:
        directory = ROOT / directory_name
        if not directory.exists():
            raise PackageError(f"required source directory is missing: {directory}")
        for path in iter_tree_files(directory):
            relative = safe_relative(path)
            if relative in seen:
                raise PackageError(f"duplicate source path: {relative}")
            seen.add(relative)
            st = path.stat()
            files.append(SourceFile(path=path, relative=relative, size=st.st_size, mtime_ns=st.st_mtime_ns))

    for filename in OPTIONAL_ROOT_FILES:
        path = ROOT / filename
        if not path.exists():
            continue
        check_regular_source(path)
        relative = safe_relative(path)
        if relative not in seen:
            st = path.stat()
            files.append(SourceFile(path=path, relative=relative, size=st.st_size, mtime_ns=st.st_mtime_ns))
            seen.add(relative)

    files.sort(key=lambda item: item.internal_name.casefold())
    rawsourcebytes = sum(item.size for item in files)
    return SourceSnapshot(files=tuple(files), rawsourcebytes=rawsourcebytes, excluded=tuple(excluded))


def source_stat_matches(item: SourceFile) -> bool:
    try:
        st = item.path.stat()
    except OSError:
        return False
    return st.st_size == item.size and st.st_mtime_ns == item.mtime_ns and not item.path.is_symlink()


def ensure_workspace_budget(snapshot: SourceSnapshot, estimated_temp: int, *, phase: str) -> tuple[int, int, int]:
    if snapshot.rawsourcebytes > MAX_WORKSPACE_BYTES:
        raise PackageError(
            f"{phase}: raw source bytes {snapshot.rawsourcebytes} exceed workspace budget {MAX_WORKSPACE_BYTES}"
        )
    existing_tree_bytes = workspace_tree_size()
    workspace_peak = existing_tree_bytes + estimated_temp + METADATA_RESERVE_BYTES
    if workspace_peak > MAX_WORKSPACE_BYTES:
        raise PackageError(
            f"{phase}: estimated workspace peak {workspace_peak} exceeds budget {MAX_WORKSPACE_BYTES}"
        )
    free = disk_free_bytes()
    required_free = MIN_FREE_BYTES + RESERVE_BYTES + METADATA_RESERVE_BYTES
    if free < required_free:
        raise PackageError(
            f"{phase}: free disk {free} is below required {required_free} "
            f"(10GiB + 64MiB reserve + {METADATA_RESERVE_BYTES} metadata guard bytes)"
        )
    return free, existing_tree_bytes, workspace_peak


def estimate_temp_bytes(snapshot: SourceSnapshot, sums_bytes: int) -> int:
    # A conservative upper bound: input bytes plus the ZIP local header,
    # central-directory, data-descriptor, and generated-sums overhead for each
    # source.  The extra 1 MiB covers ZIP64 records and filesystem slack.
    name_overhead = sum(512 + len(item.internal_name.encode("utf-8")) for item in snapshot.files)
    return snapshot.rawsourcebytes + sums_bytes + name_overhead + 1024 * 1024


def compression_for(path: Path) -> int:
    if path.suffix.casefold() == ".zip":
        return zipfile.ZIP_STORED
    if path.suffix.casefold() in TEXT_SUFFIXES:
        return zipfile.ZIP_DEFLATED
    return zipfile.ZIP_STORED


def zip_datetime(item: SourceFile) -> tuple[int, int, int, int, int, int]:
    try:
        local = time.localtime(item.path.stat().st_mtime)
        year = min(max(local.tm_year, 1980), 2107)
        return year, local.tm_mon, local.tm_mday, local.tm_hour, local.tm_min, local.tm_sec
    except (OSError, OverflowError, ValueError):
        return 1980, 1, 1, 0, 0, 0


def new_zip_info(item: SourceFile) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(filename=item.internal_name, date_time=zip_datetime(item))
    info.compress_type = compression_for(item.path)
    info.create_system = 3
    try:
        info.external_attr = (item.path.stat().st_mode & 0o777) << 16
    except OSError:
        info.external_attr = 0o644 << 16
    return info


def guard_workspace(snapshot: SourceSnapshot, state: WriteState, *, phase: str) -> tuple[int, int]:
    free = disk_free_bytes()
    actual_tree_bytes = workspace_tree_size()
    state.last_free_bytes = free
    state.minimum_free_bytes = free if state.minimum_free_bytes is None else min(state.minimum_free_bytes, free)
    state.last_workspace_bytes = actual_tree_bytes
    state.minimum_workspace_bytes = actual_tree_bytes if state.minimum_workspace_bytes is None else min(state.minimum_workspace_bytes, actual_tree_bytes)
    if actual_tree_bytes + METADATA_RESERVE_BYTES > MAX_WORKSPACE_BYTES:
        raise PackageError(
            f"{phase}: workspace tree {actual_tree_bytes} + metadata guard "
            f"{METADATA_RESERVE_BYTES} exceeds {MAX_WORKSPACE_BYTES}"
        )
    required_free = MIN_FREE_BYTES + RESERVE_BYTES + METADATA_RESERVE_BYTES
    if free < required_free:
        raise PackageError(
            f"{phase}: free disk {free} below required {required_free} "
            f"(current workspace tree is already included in this check)"
        )
    return actual_tree_bytes, free


def guard_during_write(snapshot: SourceSnapshot, partial_path: Path, state: WriteState) -> None:
    try:
        partial_size = partial_path.stat().st_size
    except OSError as exc:
        raise PackageError(f"cannot stat partial archive during write: {exc}") from exc
    state.partial_bytes = partial_size
    guard_workspace(snapshot, state, phase="write guard")


def write_source_entry(
    archive: zipfile.ZipFile,
    item: SourceFile,
    snapshot: SourceSnapshot,
    partial_path: Path,
    state: WriteState,
) -> str:
    if not source_stat_matches(item):
        raise SourceChangedError(f"source changed before read: {item.relative}")
    digest = hashlib.sha256()
    read_bytes = 0
    info = new_zip_info(item)
    with item.path.open("rb") as source, archive.open(info, "w", force_zip64=True) as target:
        while True:
            chunk = source.read(CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
            target.write(chunk)
            read_bytes += len(chunk)
            guard_during_write(snapshot, partial_path, state)
    if read_bytes != item.size or not source_stat_matches(item):
        raise SourceChangedError(f"source changed while read: {item.relative}")
    state.source_bytes += read_bytes
    return digest.hexdigest()


def sums_text(snapshot: SourceSnapshot, hashes: dict[str, str]) -> bytes:
    lines = [f"{hashes[item.relative]}  {item.internal_name}" for item in snapshot.files]
    return ("\n".join(lines) + "\n").encode("utf-8")


def verify_archive(
    archive_path: Path,
    snapshot: SourceSnapshot,
    hashes: dict[str, str],
    sums_bytes: bytes,
) -> tuple[int, int]:
    """Verify ZIP CRC, every source hash, and the generated sums entry."""
    with zipfile.ZipFile(archive_path, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise PackageError(f"ZIP CRC verification failed at {bad}")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise PackageError("ZIP contains duplicate entry names")
        expected_names = {item.internal_name for item in snapshot.files}
        expected_names.add(SUMS_NAME)
        if set(names) != expected_names:
            missing = sorted(expected_names - set(names))
            extra = sorted(set(names) - expected_names)
            raise PackageError(f"ZIP entry set mismatch; missing={missing[:3]} extra={extra[:3]}")

        sums_info = archive.getinfo(SUMS_NAME)
        if archive.read(sums_info) != sums_bytes:
            raise PackageError("FILE_SHA256SUMS.txt content mismatch")

        for item in snapshot.files:
            info = archive.getinfo(item.internal_name)
            expected_compression = compression_for(item.path)
            if info.compress_type != expected_compression:
                raise PackageError(
                    f"compression mismatch for {item.internal_name}: "
                    f"expected {expected_compression}, got {info.compress_type}"
                )
            if not source_stat_matches(item):
                raise SourceChangedError(f"source changed during archive verification: {item.relative}")
            expected_hash = hashes[item.relative]
            source_hash = hashlib.sha256()
            source_bytes = 0
            with item.path.open("rb") as source:
                while True:
                    chunk = source.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    source_hash.update(chunk)
                    source_bytes += len(chunk)
            if source_bytes != item.size or source_hash.hexdigest() != expected_hash:
                raise SourceChangedError(f"source digest changed during archive verification: {item.relative}")
            with archive.open(item.internal_name, "r") as entry:
                archive_hash = hashlib.sha256()
                archive_bytes = 0
                while True:
                    chunk = entry.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    archive_hash.update(chunk)
                    archive_bytes += len(chunk)
            if archive_bytes != item.size or archive_hash.hexdigest() != expected_hash:
                raise PackageError(f"archive SHA-256 mismatch: {item.internal_name}")
        return len(names), archive.getinfo(SUMS_NAME).file_size


def archive_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def write_atomic_text(path: Path, content: str) -> None:
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.partial")
    try:
        temp.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temp, path)
    except Exception:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass
        raise


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build and verify artifacts/WOW_Encyclopedia_20101203_source.zip "
            "from the fixed local workspace snapshot."
        )
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def run() -> dict[str, object]:
    if not zipfile.zlib:
        raise PackageError("Python zlib support is required for ZIP_DEFLATED text entries")
    snapshot = collect_sources()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUT_DIR.is_symlink():
        raise PackageError(f"refusing symlink output directory: {OUTPUT_DIR}")
    if FINAL_ZIP.is_symlink():
        raise PackageError(f"refusing symlink final archive: {FINAL_ZIP}")
    existing_size = FINAL_ZIP.stat().st_size if FINAL_ZIP.exists() else 0
    # The sums file is generated from one line per source.  Account for its
    # own content plus a conservative ZIP record allowance before writing.
    estimated_sums = sum(80 + len(item.internal_name) for item in snapshot.files) + 1
    estimated_temp = estimate_temp_bytes(snapshot, estimated_sums)
    preflight_free, preflight_tree_bytes, estimated_peak_workspace = ensure_workspace_budget(
        snapshot, estimated_temp, phase="preflight"
    )

    partial_path = OUTPUT_DIR / f".{PACKAGE_NAME}.{os.getpid()}.{uuid.uuid4().hex}.partial.zip"
    state = WriteState(source_hashes={})
    sums_bytes = b""
    replaced = False
    try:
        with zipfile.ZipFile(
            partial_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
            allowZip64=True,
        ) as archive:
            for item in snapshot.files:
                state.source_hashes[item.relative] = write_source_entry(
                    archive, item, snapshot, partial_path, state
                )
            sums_bytes = sums_text(snapshot, state.source_hashes)
            sums_info = zipfile.ZipInfo(SUMS_NAME, date_time=(1980, 1, 1, 0, 0, 0))
            sums_info.compress_type = zipfile.ZIP_DEFLATED
            sums_info.create_system = 3
            sums_info.external_attr = 0o644 << 16
            archive.writestr(sums_info, sums_bytes)
            guard_during_write(snapshot, partial_path, state)

        # Recheck source names before replacing the final archive.  This also
        # catches a file added or removed after the fixed list was collected.
        current = collect_sources()
        if tuple(item.relative for item in current.files) != tuple(item.relative for item in snapshot.files):
            raise SourceChangedError("source file set changed after snapshot collection")
        if current.rawsourcebytes != snapshot.rawsourcebytes:
            raise SourceChangedError("source byte total changed after snapshot collection")
        archive_entries, sums_size = verify_archive(partial_path, snapshot, state.source_hashes, sums_bytes)
        before_replace_free = disk_free_bytes()
        guard_during_write(snapshot, partial_path, state)
        partial_sha = archive_sha256(partial_path)
        os.replace(partial_path, FINAL_ZIP)
        replaced = True

        final_zip_bytes = FINAL_ZIP.stat().st_size
        final_sha = archive_sha256(FINAL_ZIP)
        if final_sha != partial_sha:
            raise PackageError("final archive hash changed during atomic replacement")
        sha_content = f"{final_sha}  {PACKAGE_NAME}\n"
        write_atomic_text(SHA_FILE, sha_content)
        after_replace_free = disk_free_bytes()
        after_sha_workspace_bytes, after_sha_free = guard_workspace(
            snapshot, state, phase="before verification metadata"
        )
        verification = {
            "schema_version": 1,
            "generated_at": utc_now(),
            "source_root": str(ROOT),
            "internal_prefix": INTERNAL_PREFIX,
            "source_dirs": list(SOURCE_DIRS),
            "optional_root_files": list(OPTIONAL_ROOT_FILES),
            "excluded": ["artifacts/**", "**/__pycache__/**", "**/*.pyc"],
            "rawsourcebytes": snapshot.rawsourcebytes,
            "filecount": len(snapshot.files),
            "workspace_bytes": after_sha_workspace_bytes,
            "zip_bytes": final_zip_bytes,
            "zipbytes": final_zip_bytes,
            "sha": final_sha,
            "sha256": final_sha,
            "diskfree": {
                "preflight": preflight_free,
                "preflight_workspace_bytes": preflight_tree_bytes,
                "minimum_during_write": state.minimum_free_bytes,
                "minimum_workspace_during_write": state.minimum_workspace_bytes,
                "before_replace": before_replace_free,
                "after_replace": after_replace_free,
                "after_sha": after_sha_free,
            },
            "taskbytes": after_sha_workspace_bytes,
            "taskbytes_detail": {
                "estimated_peak_transient": estimated_peak_workspace,
                "actual_new_zip": final_zip_bytes,
                "retained_old_final_during_write": existing_size,
                "workspace_peak_estimate": estimated_peak_workspace,
                "metadata_reserve": METADATA_RESERVE_BYTES,
            },
            "budget": {
                "max_workspace_bytes": MAX_WORKSPACE_BYTES,
                "minimum_free_bytes": MIN_FREE_BYTES,
                "reserve_bytes": RESERVE_BYTES,
                "metadata_reserve_bytes": METADATA_RESERVE_BYTES,
            },
            "zip": {
                "crc_verified": True,
                "archive_entries": archive_entries,
                "sha_manifest_entry": SUMS_NAME,
                "sha_manifest_bytes": sums_size,
                "sha_manifest_excludes_itself": True,
                "text_compression": "ZIP_DEFLATED",
                "existing_zip_compression": "ZIP_STORED",
                "other_binary_compression": "ZIP_STORED",
            },
            "verification": {
                "source_hashes_match_archive": True,
                "source_files_unchanged_at_verify": True,
                "workspace_tree_measured_after_metadata": True,
                "atomic_replace": True,
                "final_zip": str(FINAL_ZIP.relative_to(ROOT)).replace("\\", "/"),
                "sha_file": str(SHA_FILE.relative_to(ROOT)).replace("\\", "/"),
            },
        }
        # The verification file itself occupies workspace bytes.  Write it,
        # measure the tree, then rewrite the measured value; the short loop
        # settles the digit count while keeping the final value exact.
        previous_workspace_bytes: int | None = None
        for _ in range(3):
            write_atomic_text(VERIFICATION_FILE, json.dumps(verification, ensure_ascii=False, indent=2) + "\n")
            measured_workspace_bytes, measured_free = guard_workspace(
                snapshot, state, phase="after verification metadata"
            )
            verification["workspace_bytes"] = measured_workspace_bytes
            verification["taskbytes"] = measured_workspace_bytes
            verification["diskfree"]["after_metadata"] = measured_free
            if measured_workspace_bytes == previous_workspace_bytes:
                break
            previous_workspace_bytes = measured_workspace_bytes
        else:
            raise PackageError("workspace byte count did not stabilize after metadata writes")
        return verification
    except Exception:
        if not replaced:
            try:
                partial_path.unlink()
            except FileNotFoundError:
                pass
        raise


def main(argv: Iterable[str] | None = None) -> int:
    parse_args(argv)
    try:
        result = run()
    except SourceChangedError as exc:
        print(f"SOURCE_CHANGED: {exc}", file=sys.stderr)
        return 2
    except PackageError as exc:
        print(f"PACKAGE_STOPPED: {exc}", file=sys.stderr)
        return 2
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"PACKAGE_IO_ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"PACKAGE_UNEXPECTED_ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "output": str(FINAL_ZIP.relative_to(ROOT)).replace("\\", "/"),
                "verification": str(VERIFICATION_FILE.relative_to(ROOT)).replace("\\", "/"),
                "rawsourcebytes": result["rawsourcebytes"],
                "filecount": result["filecount"],
                "workspace_bytes": result["workspace_bytes"],
                "zip_bytes": result["zip_bytes"],
                "zipbytes": result["zipbytes"],
                "sha": result["sha"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

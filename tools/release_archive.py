#!/usr/bin/env python3
"""Split, verify, and join a large release archive using only the stdlib.

The split files are byte ranges of one ZIP stream.  They are not independent
ZIP archives; a downloader must verify all parts and join them in the recorded
order before extraction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_LIMIT = 14_000_000_000
MIN_FREE_BYTES = 10 * 1024**3 + 256 * 1024**2
PREFLIGHT_MARGIN_BYTES = 64 * 1024**2
CHUNK_BYTES = 1024 * 1024
SCHEMA = "github-release-assets-v1"


class ArchiveError(RuntimeError):
    """A release archive operation cannot safely continue."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def workspace_bytes() -> int:
    total = 0
    for directory, dirnames, filenames in os.walk(PROJECT_ROOT):
        # A Git object database is part of the workspace budget if present.
        # Ignore only transient Python bytecode, which is not release input and
        # can otherwise change while the command is running.
        for filename in filenames:
            if filename.endswith(".pyc"):
                continue
            try:
                total += (Path(directory) / filename).stat().st_size
            except OSError as exc:
                raise ArchiveError(f"cannot stat workspace file: {Path(directory) / filename}") from exc
    return total


def free_bytes() -> int:
    return shutil.disk_usage(PROJECT_ROOT).free


def safe_relative_name(name: str, *, field: str) -> str:
    """Return a safe relative ZIP/release asset name or raise."""

    if not isinstance(name, str) or not name or "\x00" in name:
        raise ArchiveError(f"{field} must be a non-empty path string")
    normalized = name.replace("\\", "/")
    windows = PureWindowsPath(name)
    posix = PurePosixPath(normalized)
    if normalized.startswith("/") or windows.is_absolute() or windows.drive:
        raise ArchiveError(f"{field} must not be absolute: {name!r}")
    if any(part in ("", ".", "..") for part in posix.parts):
        raise ArchiveError(f"{field} contains an unsafe path component: {name!r}")
    return "/".join(posix.parts)


def safe_child(parent: Path, name: str, *, field: str) -> Path:
    relative = safe_relative_name(name, field=field)
    candidate = (parent / Path(*relative.split("/"))).resolve()
    parent_resolved = parent.resolve()
    try:
        candidate.relative_to(parent_resolved)
    except ValueError as exc:
        raise ArchiveError(f"{field} escapes its manifest directory: {name!r}") from exc
    current = parent_resolved
    for component in Path(*relative.split("/")).parts:
        current = current / component
        if current.is_symlink():
            raise ArchiveError(f"{field} traverses a symlink: {name!r}")
    return candidate


def ensure_regular_file(path: Path, *, label: str) -> Path:
    if not path.exists():
        raise ArchiveError(f"{label} is missing: {path}")
    if path.is_symlink() or not path.is_file():
        raise ArchiveError(f"{label} must be a regular file: {path}")
    return path


def read_manifest(path: Path) -> tuple[dict[str, Any], Path, list[dict[str, Any]]]:
    path = ensure_regular_file(path.resolve(), label="manifest")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ArchiveError(f"cannot read manifest {path}") from exc
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ArchiveError("unsupported or missing release manifest schema")
    source = data.get("source")
    if not isinstance(source, dict):
        raise ArchiveError("manifest source must be an object")
    source_name = source.get("filename")
    if not isinstance(source_name, str) or Path(source_name).name != source_name:
        raise ArchiveError("manifest source filename must be a basename")
    source_length = source.get("length")
    source_sha = source.get("sha256")
    if not isinstance(source_length, int) or isinstance(source_length, bool) or source_length < 0:
        raise ArchiveError("manifest source length is invalid")
    if not isinstance(source_sha, str) or len(source_sha) != 64 or any(c not in "0123456789abcdef" for c in source_sha.lower()):
        raise ArchiveError("manifest source SHA256 is invalid")
    part_bytes = data.get("part_bytes")
    if not isinstance(part_bytes, int) or isinstance(part_bytes, bool) or part_bytes <= 0:
        raise ArchiveError("manifest part_bytes is invalid")
    parts = data.get("parts")
    if not isinstance(parts, list) or len(parts) != 3:
        raise ArchiveError("manifest must contain exactly three parts")
    seen: set[str] = set()
    normalized_parts: list[dict[str, Any]] = []
    for expected_index, item in enumerate(parts, start=1):
        if not isinstance(item, dict):
            raise ArchiveError("manifest part entry must be an object")
        name = safe_relative_name(item.get("name"), field="part name")
        if name in seen:
            raise ArchiveError(f"duplicate part name: {name}")
        seen.add(name)
        index = item.get("index")
        length = item.get("length")
        digest = item.get("sha256")
        if index != expected_index:
            raise ArchiveError("part indices must be 1, 2, 3 in order")
        if not isinstance(length, int) or isinstance(length, bool) or length < 0 or length > part_bytes:
            raise ArchiveError(f"invalid length for part {name}")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            raise ArchiveError(f"invalid SHA256 for part {name}")
        normalized_parts.append({"index": index, "name": name, "length": length, "sha256": digest.lower()})
    if sum(item["length"] for item in normalized_parts) != source_length:
        raise ArchiveError("part lengths do not equal source length")
    return data, path.parent, normalized_parts


def stream_digest(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    length = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
            length += len(chunk)
            digest.update(chunk)
    return length, digest.hexdigest()


def verify_parts(manifest_path: Path, *, include_source: bool = True) -> dict[str, Any]:
    data, directory, parts = read_manifest(manifest_path)
    source = data["source"]
    part_results: list[dict[str, Any]] = []
    combined = hashlib.sha256()
    combined_length = 0
    for part in parts:
        path = safe_child(directory, part["name"], field="part name")
        ensure_regular_file(path, label=f"part {part['name']}")
        digest = hashlib.sha256()
        length = 0
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
                length += len(chunk)
                digest.update(chunk)
                combined.update(chunk)
                combined_length += len(chunk)
        actual_sha = digest.hexdigest()
        result = {
            "index": part["index"],
            "name": part["name"],
            "expected_length": part["length"],
            "actual_length": length,
            "expected_sha256": part["sha256"],
            "actual_sha256": actual_sha,
            "accepted": length == part["length"] and actual_sha == part["sha256"],
        }
        part_results.append(result)
        if not result["accepted"]:
            raise ArchiveError(f"part verification failed: {part['name']}")
    combined_sha = combined.hexdigest()
    source_result = {
        "expected_length": source["length"],
        "actual_length": combined_length,
        "expected_sha256": source["sha256"].lower(),
        "actual_sha256": combined_sha,
        "accepted": combined_length == source["length"] and combined_sha == source["sha256"].lower(),
    }
    if not source_result["accepted"]:
        raise ArchiveError("combined release parts do not match source digest")
    return {
        "schema": "github-release-assets-verification-v1",
        "accepted": True,
        "manifest": manifest_path.resolve().name,
        "source": source_result,
        "parts": part_results,
        "part_count": len(part_results),
        "streamed_without_join_output": True,
    }


def preflight_split(source: Path, output: Path, part_bytes: int) -> dict[str, Any]:
    source = ensure_regular_file(source.resolve(), label="source archive")
    output = output.resolve()
    if output.exists():
        raise ArchiveError(f"refusing to use existing output directory: {output}")
    if part_bytes <= 0:
        raise ArchiveError("--part-bytes must be positive")
    source_length = source.stat().st_size
    part_count = math.ceil(source_length / part_bytes) if source_length else 0
    if part_count != 3:
        raise ArchiveError(f"split requires exactly three parts; source would need {part_count}")
    before_workspace = workspace_bytes()
    before_free = free_bytes()
    projected_workspace = before_workspace + source_length + PREFLIGHT_MARGIN_BYTES
    projected_free = before_free - source_length - PREFLIGHT_MARGIN_BYTES
    checks = {
        "source_regular_file": True,
        "output_absent": True,
        "exactly_three_parts": part_count == 3,
        "workspace_plus_parts_with_margin_under_limit": projected_workspace < WORKSPACE_LIMIT,
        "disk_free_minus_parts_with_margin_meets_reserve": projected_free >= MIN_FREE_BYTES,
    }
    if not all(checks.values()):
        raise ArchiveError("split budget preflight failed: " + json.dumps(checks, sort_keys=True))
    return {
        "schema": "github-release-publication-preflight-v1",
        "created_utc": utc_now(),
        "source_filename": source.name,
        "source_length": source_length,
        "source_sha256": None,
        "output_directory": output.name,
        "part_bytes": part_bytes,
        "part_count": part_count,
        "workspace_bytes_before": before_workspace,
        "projected_workspace_bytes_with_parts_and_margin": projected_workspace,
        "workspace_limit_bytes": WORKSPACE_LIMIT,
        "disk_free_bytes_before": before_free,
        "projected_disk_free_after_parts_and_margin": projected_free,
        "disk_reserve_floor_bytes": MIN_FREE_BYTES,
        "margin_bytes": PREFLIGHT_MARGIN_BYTES,
        "checks": checks,
        "split_started": False,
        "failure_policy": "new partials remain in the new output directory and are reported; existing files are never overwritten",
    }


def split_archive(source: Path, output: Path, part_bytes: int) -> dict[str, Any]:
    preflight = preflight_split(source, output, part_bytes)
    output.mkdir(parents=True, exist_ok=False)
    preflight_path = output / "publication-preflight.json"
    preflight_path.write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")
    source = source.resolve()
    part_records: list[dict[str, Any]] = []
    source_digest = hashlib.sha256()
    source_length = 0
    part_index = 1
    remaining = source.stat().st_size
    try:
        with source.open("rb") as source_handle:
            while remaining:
                part_name = f"{source.name}.{part_index:03d}"
                part_path = output / part_name
                if part_path.exists():
                    raise ArchiveError(f"refusing to overwrite part: {part_path}")
                digest = hashlib.sha256()
                written = 0
                with part_path.open("xb") as part_handle:
                    while written < part_bytes and remaining:
                        chunk = source_handle.read(min(CHUNK_BYTES, part_bytes - written, remaining))
                        if not chunk:
                            raise ArchiveError("source ended before its advertised length")
                        part_handle.write(chunk)
                        digest.update(chunk)
                        source_digest.update(chunk)
                        written += len(chunk)
                        source_length += len(chunk)
                        remaining -= len(chunk)
                part_records.append({"index": part_index, "name": part_name, "length": written, "sha256": digest.hexdigest()})
                part_index += 1
        if len(part_records) != 3:
            raise ArchiveError(f"split produced {len(part_records)} parts instead of exactly three")
        source_sha = source_digest.hexdigest()
        manifest = {
            "schema": SCHEMA,
            "created_utc": utc_now(),
            "source": {"filename": source.name, "length": source_length, "sha256": source_sha},
            "part_bytes": part_bytes,
            "parts": part_records,
            "total_part_bytes": sum(item["length"] for item in part_records),
            "checksums": "SHA256SUMS.txt",
            "verification": "verify this manifest before joining; parts are byte ranges of the source ZIP and are not standalone ZIP archives",
        }
        manifest_path = output / "release-assets.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        checksums = [f"{source_sha}  {source.name}"] + [f"{item['sha256']}  {item['name']}" for item in part_records]
        (output / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n", encoding="ascii")
        preflight.update({
            "source_sha256": source_sha,
            "source_length_actual": source_length,
            "parts": part_records,
            "split_started": True,
            "split_completed": True,
            "manifest": "release-assets.json",
            "checksums": "SHA256SUMS.txt",
            "finished_utc": utc_now(),
        })
        preflight_path.write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")
        verification = verify_parts(manifest_path)
        return {"accepted": True, "output_directory": output.name, "manifest": manifest, "verification": verification}
    except Exception as exc:
        preflight.update({"split_started": True, "split_completed": False, "error": f"{type(exc).__name__}: {exc}", "finished_utc": utc_now()})
        preflight_path.write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")
        raise


def join_archive(manifest_path: Path, output: Path) -> dict[str, Any]:
    data, directory, parts = read_manifest(manifest_path)
    output = output.resolve()
    if output.exists():
        raise ArchiveError(f"refusing to overwrite existing output: {output}")
    partial = output.with_name(output.name + ".partial")
    if partial.exists():
        raise ArchiveError(f"refusing to reuse existing partial output: {partial}")
    output.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    total = 0
    created_partial = False
    try:
        with partial.open("xb") as target:
            created_partial = True
            for part in parts:
                path = safe_child(directory, part["name"], field="part name")
                ensure_regular_file(path, label=f"part {part['name']}")
                part_digest = hashlib.sha256()
                part_total = 0
                with path.open("rb") as source:
                    for chunk in iter(lambda: source.read(CHUNK_BYTES), b""):
                        target.write(chunk)
                        digest.update(chunk)
                        part_digest.update(chunk)
                        total += len(chunk)
                        part_total += len(chunk)
                if part_total != part["length"] or part_digest.hexdigest() != part["sha256"]:
                    raise ArchiveError(f"part verification failed during join: {part['name']}")
        combined_sha = digest.hexdigest()
        source = data["source"]
        if total != source["length"] or combined_sha != source["sha256"].lower():
            raise ArchiveError("joined stream does not match source digest")
        if output.exists():
            raise ArchiveError(f"refusing to overwrite output created during join: {output}")
        os.replace(partial, output)
        created_partial = False
        return {"accepted": True, "output": output.name, "length": total, "sha256": combined_sha, "partial_cleaned": True}
    except Exception:
        if created_partial and partial.exists():
            try:
                partial.unlink()
            except OSError:
                pass
        raise


def command_error(exc: Exception) -> int:
    payload = {"accepted": False, "error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(payload, ensure_ascii=False))
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    split = sub.add_parser("split", help="split one ZIP stream into exactly three parts")
    split.add_argument("--archive", required=True, type=Path)
    split.add_argument("--output", required=True, type=Path)
    split.add_argument("--part-bytes", required=True, type=int)
    verify = sub.add_parser("verify", help="stream-verify all parts and the combined digest")
    verify.add_argument("--manifest", required=True, type=Path)
    join = sub.add_parser("join", help="stream-join verified parts into a new ZIP")
    join.add_argument("--manifest", required=True, type=Path)
    join.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "split":
            result = split_archive(args.archive, args.output, args.part_bytes)
        elif args.command == "verify":
            result = verify_parts(args.manifest)
        else:
            result = join_archive(args.manifest, args.output)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ArchiveError, OSError, ValueError) as exc:
        return command_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deduplicate historical Pages exports while preserving exact restorable trees.

The store contains one ZIP64/DEFLATE object per SHA-256 plus a gzip manifest for
each source tree. Builds never modify or delete source trees. A failed run keeps
its named staging directory; only an atomically published store has a receipt.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import uuid
import zipfile
import zlib
from typing import Any, Callable

CHUNK_SIZE = 1024 * 1024
DEFAULT_FLOOR_BYTES = 11_005_853_696
DEFLATE_LEVEL = 6
STORE_SCHEMA = "wow-historical-export-store/v1"
MANIFEST_SCHEMA = "wow-historical-export-manifest/v1"
ACCEPTANCE_SCHEMA = "wow-historical-export-store-acceptance/v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REPARSE_ATTRIBUTE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
RESERVED_DOS = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


class StoreError(RuntimeError):
    """Invalid source, damaged store, unsafe path, or insufficient space."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _safe_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/") or "\x00" in value:
        raise StoreError(f"unsafe manifest path: {value!r}")
    if ":" in value:
        raise StoreError(f"drive and alternate-stream syntax is not allowed: {value!r}")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise StoreError(f"unsafe manifest path: {value!r}")
    for part in parts:
        if part[-1:] in {".", " "} or any(ord(ch) < 32 or ch in '<>"|?*' for ch in part):
            raise StoreError(f"path cannot be restored safely on Windows: {value!r}")
        if part.split(".", 1)[0].upper() in RESERVED_DOS:
            raise StoreError(f"reserved Windows path component: {value!r}")
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or parsed.as_posix() != value:
        raise StoreError(f"non-canonical manifest path: {value!r}")
    return value


def _assert_no_case_collision(path: str, seen: dict[str, str]) -> None:
    key = path.casefold()
    if key in seen:
        raise StoreError(f"case-insensitive path collision: {seen[key]!r} and {path!r}")
    seen[key] = path


def _is_reparse_or_link(path: Path) -> bool:
    try:
        details = os.stat(path, follow_symlinks=False)
    except OSError as exc:
        raise StoreError(f"cannot inspect path: {path}") from exc
    return stat.S_ISLNK(details.st_mode) or bool(getattr(details, "st_file_attributes", 0) & REPARSE_ATTRIBUTE)


def _assert_no_reparse_path(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    parts = absolute.parts
    current = Path(parts[0])
    for component in parts[1:]:
        current = current / component
        if os.path.lexists(current) and _is_reparse_or_link(current):
            raise StoreError(f"reparse point or symlink is not allowed: {current}")


def _path_is_within(path: Path, parent: Path) -> bool:
    """Return whether an absolute path is equal to or nested under parent."""
    path_text = os.path.normcase(os.path.abspath(path))
    parent_text = os.path.normcase(os.path.abspath(parent))
    try:
        return os.path.commonpath((path_text, parent_text)) == parent_text
    except ValueError:
        # Different Windows drives have no common path.
        return False


def _stat_dir(path: Path) -> os.stat_result:
    if _is_reparse_or_link(path):
        raise StoreError(f"reparse point or symlink is not allowed: {path}")
    try:
        details = os.stat(path, follow_symlinks=False)
    except OSError as exc:
        raise StoreError(f"cannot inspect directory: {path}") from exc
    if not stat.S_ISDIR(details.st_mode):
        raise StoreError(f"expected a real directory: {path}")
    return details


def _stat_file(path: Path) -> os.stat_result:
    if _is_reparse_or_link(path):
        raise StoreError(f"reparse point or symlink is not allowed: {path}")
    try:
        details = os.stat(path, follow_symlinks=False)
    except OSError as exc:
        raise StoreError(f"cannot inspect file: {path}") from exc
    if not stat.S_ISREG(details.st_mode):
        raise StoreError(f"expected a regular file: {path}")
    return details


def _same_identity(a: os.stat_result, b: os.stat_result) -> bool:
    return (a.st_size, a.st_mtime_ns, a.st_dev, a.st_ino) == (b.st_size, b.st_mtime_ns, b.st_dev, b.st_ino)


def _hash_file(path: Path) -> tuple[str, int, os.stat_result]:
    before = _stat_file(path)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    digest = hashlib.sha256()
    total = 0
    try:
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as source:
            opened = os.fstat(source.fileno())
            if not stat.S_ISREG(opened.st_mode) or not _same_identity(before, opened):
                raise StoreError(f"source changed while opening: {path}")
            for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
                digest.update(chunk)
                total += len(chunk)
            after = os.fstat(source.fileno())
    except OSError as exc:
        raise StoreError(f"cannot read source file: {path}") from exc
    after_path = _stat_file(path)
    if total != before.st_size or not _same_identity(before, after) or not _same_identity(before, after_path):
        raise StoreError(f"source changed while hashing: {path}")
    return digest.hexdigest(), total, before


def _tree_records(tree: Path) -> tuple[os.stat_result, list[dict[str, Any]], list[dict[str, Any]], dict[str, tuple[Path, int]]]:
    root_stat = _stat_dir(tree)
    seen: dict[str, str] = {}
    directories: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    objects: dict[str, tuple[Path, int]] = {}
    stack: list[tuple[Path, str]] = [(tree, "")]
    while stack:
        parent, relative = stack.pop()
        _stat_dir(parent)
        try:
            with os.scandir(parent) as entries:
                children = sorted(list(entries), key=lambda entry: (entry.name.casefold(), entry.name))
        except OSError as exc:
            raise StoreError(f"cannot enumerate source directory: {parent}") from exc
        subdirectories: list[tuple[Path, str]] = []
        for entry in children:
            rel = _safe_relative_path(f"{relative}/{entry.name}" if relative else entry.name)
            _assert_no_case_collision(rel, seen)
            path = parent / entry.name
            try:
                details = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise StoreError(f"cannot inspect source entry: {path}") from exc
            if stat.S_ISLNK(details.st_mode) or bool(getattr(details, "st_file_attributes", 0) & REPARSE_ATTRIBUTE):
                raise StoreError(f"reparse point or symlink is not allowed: {path}")
            if stat.S_ISDIR(details.st_mode):
                directories.append({"path": rel, "mtime_ns": int(details.st_mtime_ns)})
                subdirectories.append((path, rel))
            elif stat.S_ISREG(details.st_mode):
                digest, length, fresh_stat = _hash_file(path)
                files.append({"path": rel, "bytes": length, "sha256": digest, "mtime_ns": int(fresh_stat.st_mtime_ns)})
                prior = objects.get(digest)
                if prior is not None and prior[1] != length:
                    raise StoreError(f"same SHA-256 has conflicting lengths: {digest}")
                if prior is None:
                    objects[digest] = (path, length)
            else:
                raise StoreError(f"non-regular source entry is not allowed: {path}")
        stack.extend(reversed(subdirectories))
    directories.sort(key=lambda item: (item["path"].casefold(), item["path"]))
    files.sort(key=lambda item: (item["path"].casefold(), item["path"]))
    return root_stat, directories, files, objects


def _validate_nodes(directories: list[dict[str, Any]], files: list[dict[str, Any]]) -> None:
    nodes: dict[str, str] = {}
    case_paths: dict[str, str] = {}
    for item in directories:
        path = _safe_relative_path(item.get("path"))
        _assert_no_case_collision(path, case_paths)
        nodes[path] = "directory"
    for item in files:
        path = _safe_relative_path(item.get("path"))
        _assert_no_case_collision(path, case_paths)
        nodes[path] = "file"
    for path in nodes:
        parts = path.split("/")
        for i in range(1, len(parts)):
            parent = "/".join(parts[:i])
            if nodes.get(parent) != "directory":
                raise StoreError(f"manifest omits a parent directory or has a file ancestor: {parent!r}")


def _disk_free(path: Path) -> int:
    probe = path
    while not os.path.exists(probe):
        probe = probe.parent
    try:
        return int(shutil.disk_usage(probe).free)
    except OSError as exc:
        raise StoreError(f"cannot inspect disk space near {path}") from exc


def _preflight(path: Path, floor: int, reserve: int, label: str) -> int:
    free = _disk_free(path)
    required = floor + max(0, reserve)
    if free < required:
        raise StoreError(f"disk-space preflight failed ({label}): free={free}, required={required}, floor={floor}, reserve={reserve}")
    return free


def _safe_tree(repo_root: Path, relative: str) -> Path:
    relative = _safe_relative_path(relative)
    parts = relative.split("/")
    if len(parts) != 2 or parts[0] != ".scratch" or not parts[1].startswith("pages-"):
        raise StoreError(f"tree must be a direct .scratch/pages-* directory: {relative!r}")
    candidate = repo_root.joinpath(*parts)
    _assert_no_reparse_path(candidate)
    if not candidate.is_dir():
        raise StoreError(f"source tree does not exist: {relative}")
    _stat_dir(candidate)
    return candidate


def _load_plan(plan: Path) -> list[str]:
    try:
        value = json.loads(plan.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StoreError(f"cannot read JSON plan: {plan}") from exc
    trees = value if isinstance(value, list) else value.get("trees") if isinstance(value, dict) else None
    if not isinstance(trees, list) or not trees:
        raise StoreError("plan must be a non-empty array or an object with a non-empty 'trees' array")
    normalized = [_safe_relative_path(item.get("path") if isinstance(item, dict) else item) for item in trees]
    if len(set(normalized)) != len(normalized):
        raise StoreError("plan contains duplicate trees")
    basenames = [Path(item).name.casefold() for item in normalized]
    if len(set(basenames)) != len(basenames):
        raise StoreError("source tree basenames must be unique")
    return normalized


def _hash_path(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    length = 0
    try:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
                digest.update(chunk)
                length += len(chunk)
    except OSError as exc:
        raise StoreError(f"cannot read file: {path}") from exc
    return digest.hexdigest(), length


def _write_object(archive: zipfile.ZipFile, digest: str, path: Path, length: int) -> dict[str, Any]:
    before = _stat_file(path)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    hasher = hashlib.sha256()
    total = 0
    try:
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as source:
            opened = os.fstat(source.fileno())
            if not _same_identity(before, opened) or not stat.S_ISREG(opened.st_mode):
                raise StoreError(f"source changed before object write: {path}")
            info = zipfile.ZipInfo(f"objects/{digest}")
            info.compress_type = zipfile.ZIP_DEFLATED
            info.file_size = length
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info._compresslevel = DEFLATE_LEVEL
            with archive.open(info, "w", force_zip64=True) as output:
                for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
                    output.write(chunk)
                    hasher.update(chunk)
                    total += len(chunk)
            after = os.fstat(source.fileno())
    except OSError as exc:
        raise StoreError(f"cannot write object {digest} from {path}") from exc
    after_path = _stat_file(path)
    if total != length or hasher.hexdigest() != digest or not _same_identity(before, after) or not _same_identity(before, after_path):
        raise StoreError(f"source changed or object hash mismatch during ZIP write: {path}")
    return {"sha256": digest, "bytes": total, "path": f"objects/{digest}"}


def _load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StoreError(f"cannot read {label}: {path}") from exc


def _read_manifest(store: Path, item: dict[str, Any]) -> dict[str, Any]:
    rel = _safe_relative_path(item.get("path"))
    if not rel.startswith("manifests/") or not rel.endswith(".json.gz"):
        raise StoreError(f"invalid manifest location: {rel!r}")
    path = store.joinpath(*rel.split("/"))
    digest, length = _hash_path(path)
    if digest != item.get("sha256") or length != item.get("bytes"):
        raise StoreError(f"manifest digest or length mismatch: {rel}")
    try:
        manifest = json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
    except (OSError, EOFError, UnicodeDecodeError, json.JSONDecodeError, zlib.error) as exc:
        raise StoreError(f"cannot decode manifest: {rel}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("version_id") != item.get("version_id"):
        raise StoreError(f"manifest schema or version mismatch: {rel}")
    return manifest


def _validate_manifest(manifest: dict[str, Any]) -> tuple[dict[str, int], set[str], set[str]]:
    version_id = _safe_relative_path(manifest.get("version_id"))
    parts = version_id.split("/")
    if len(parts) != 2 or parts[0] != ".scratch" or not parts[1].startswith("pages-"):
        raise StoreError(f"invalid manifest version id: {version_id!r}")
    if manifest.get("schema") != MANIFEST_SCHEMA or not isinstance(manifest.get("tree_mtime_ns"), int):
        raise StoreError("invalid manifest schema or tree timestamp")
    directories, files = manifest.get("directories"), manifest.get("files")
    if not isinstance(directories, list) or not isinstance(files, list):
        raise StoreError("manifest directories and files must be arrays")
    for item in directories:
        if not isinstance(item, dict) or not isinstance(item.get("mtime_ns"), int):
            raise StoreError("invalid manifest directory record")
    for item in files:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("bytes"), int)
            or item["bytes"] < 0
            or not isinstance(item.get("sha256"), str)
            or not SHA256_RE.fullmatch(item["sha256"])
            or not isinstance(item.get("mtime_ns"), int)
        ):
            raise StoreError("invalid manifest file record")
    _validate_nodes(directories, files)
    lengths: dict[str, int] = {}
    for item in files:
        digest, length = item["sha256"], item["bytes"]
        if digest in lengths and lengths[digest] != length:
            raise StoreError(f"same digest has inconsistent lengths: {digest}")
        lengths[digest] = length
    return lengths, {item["path"] for item in directories}, {item["path"] for item in files}


def _store_inventory(store: Path) -> set[str]:
    observed: set[str] = set()

    def raise_walk_error(error: OSError) -> None:
        raise StoreError(f"cannot enumerate store: {error}") from error

    for root, dirs, files in os.walk(store, topdown=True, followlinks=False, onerror=raise_walk_error):
        root_path = Path(root)
        _assert_no_reparse_path(root_path)
        for name in list(dirs):
            path = root_path / name
            if _is_reparse_or_link(path):
                raise StoreError(f"store contains a reparse point: {path}")
            observed.add(path.relative_to(store).as_posix() + "/")
        for name in files:
            path = root_path / name
            if _is_reparse_or_link(path):
                raise StoreError(f"store contains a reparse point: {path}")
            observed.add(path.relative_to(store).as_posix())
    return observed


def build_store(
    *, plan: Path, store: Path, repo_root: Path, floor_bytes: int = DEFAULT_FLOOR_BYTES,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    repo_root = Path(os.path.abspath(repo_root))
    _assert_no_reparse_path(repo_root)
    if not repo_root.is_dir() or floor_bytes < 0:
        raise StoreError("repository root is unavailable or floor-bytes is negative")
    store = Path(os.path.abspath(store if store.is_absolute() else repo_root / store))
    try:
        store.relative_to(repo_root)
    except ValueError as exc:
        raise StoreError("store path must be inside the repository") from exc
    if store == repo_root:
        raise StoreError(f"refusing to use repository root as store: {store}")
    trees = _load_plan(plan)
    sources = [(relative, _safe_tree(repo_root, relative)) for relative in trees]
    plan_abs = Path(os.path.abspath(plan))
    for version_id, tree in sources:
        if _path_is_within(plan_abs, tree):
            raise StoreError(f"plan must not be inside a source tree: {version_id}")
    staging = store.with_name(f".{store.name}.building.{uuid.uuid4().hex}")
    for version_id, tree in sources:
        if _path_is_within(store, tree) or _path_is_within(staging, tree):
            raise StoreError(f"store and staging paths must be outside every source tree: {version_id}")
    if os.path.lexists(store):
        raise StoreError(f"refusing to overwrite existing store: {store}")
    existing_staging = sorted(store.parent.glob(f".{store.name}.building.*"))
    if existing_staging:
        raise StoreError("incomplete staging store exists; inspect it before retrying: " + ", ".join(map(str, existing_staging)))
    _assert_no_reparse_path(store.parent)
    store.parent.mkdir(parents=True, exist_ok=True)
    _assert_no_reparse_path(store.parent)
    _preflight(store.parent, floor_bytes, 0, "initial store preflight")
    staging.mkdir()
    all_objects: dict[str, tuple[Path, int]] = {}
    versions: list[dict[str, Any]] = []
    logical_bytes = 0
    try:
        manifests_dir = staging / "manifests"
        manifests_dir.mkdir()
        (staging / "build-state.json").write_bytes(_json_bytes({"schema": STORE_SCHEMA, "status": "building", "started_utc": _utc_now()}))
        for index, (version_id, tree) in enumerate(sources, 1):
            root_stat, directories, files, tree_objects = _tree_records(tree)
            for digest, value in tree_objects.items():
                previous = all_objects.get(digest)
                if previous is not None and previous[1] != value[1]:
                    raise StoreError(f"same SHA-256 has conflicting lengths: {digest}")
                all_objects.setdefault(digest, value)
            manifest = {"schema": MANIFEST_SCHEMA, "version_id": version_id, "tree_mtime_ns": root_stat.st_mtime_ns, "directories": directories, "files": files}
            raw_manifest = _json_bytes(manifest)
            estimate = len(raw_manifest) + len(raw_manifest) // 500 + 64 * 1024
            _preflight(store.parent, floor_bytes, estimate, f"manifest {index}/{len(sources)} preflight")
            manifest_rel = f"manifests/{hashlib.sha256(version_id.encode('utf-8')).hexdigest()}.json.gz"
            manifest_path = staging.joinpath(*manifest_rel.split("/"))
            compressed = gzip.compress(raw_manifest, compresslevel=9, mtime=0)
            with manifest_path.open("xb") as output:
                output.write(compressed)
            _preflight(store.parent, floor_bytes, 0, f"manifest {index}/{len(sources)} postflight")
            digest = hashlib.sha256(compressed).hexdigest()
            record = {
                "version_id": version_id, "tree_path": version_id,
                "manifest_path": manifest_rel, "manifest_bytes": len(compressed), "manifest_sha256": digest,
                "file_count": len(files), "directory_count": len(directories),
                "logical_bytes": sum(item["bytes"] for item in files),
            }
            versions.append(record)
            logical_bytes += record["logical_bytes"]
            if progress:
                progress(f"manifest {index}/{len(sources)}: {version_id}; files={len(files)}; directories={len(directories)}; bytes={record['logical_bytes']}")

        unique_bytes = sum(length for _path, length in all_objects.values())
        _preflight(store.parent, floor_bytes, unique_bytes + 32 * 1024 * 1024, "unique-object ZIP upper bound")
        archive_path = staging / "objects.zip"
        object_records: list[dict[str, Any]] = []
        remaining = unique_bytes
        object_items = sorted(all_objects.items())
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=DEFLATE_LEVEL, allowZip64=True) as archive:
            for index, (digest, (source, length)) in enumerate(object_items, 1):
                _preflight(store.parent, floor_bytes, remaining + 16 * 1024 * 1024, f"object {index}/{len(object_items)} preflight")
                object_records.append(_write_object(archive, digest, source, length))
                remaining -= length
                _preflight(store.parent, floor_bytes, remaining + 16 * 1024 * 1024, f"object {index}/{len(object_items)} postflight")
        objects_sha, objects_length = _hash_path(archive_path)
        manifest_index = [
            {"path": row["manifest_path"], "bytes": row["manifest_bytes"], "sha256": row["manifest_sha256"], "version_id": row["version_id"]}
            for row in versions
        ]
        catalog = {
            "schema": STORE_SCHEMA, "created_utc": _utc_now(), "object_archive": "objects.zip",
            "object_count": len(object_records), "object_uncompressed_bytes": unique_bytes,
            "logical_version_bytes": logical_bytes, "deduplicated_bytes": logical_bytes - unique_bytes,
            "versions": versions, "manifests": manifest_index, "objects": object_records,
        }
        catalog_payload = _json_bytes(catalog)
        _preflight(store.parent, floor_bytes, len(catalog_payload) + 1024 * 1024, "catalog write preflight")
        catalog_path = staging / "catalog.json"
        catalog_path.write_bytes(catalog_payload)
        _preflight(store.parent, floor_bytes, 0, "catalog write postflight")
        catalog_sha = hashlib.sha256(catalog_payload).hexdigest()
        receipt = {
            "schema": ACCEPTANCE_SCHEMA, "accepted": True, "created_utc": _utc_now(),
            "catalog": {"path": "catalog.json", "bytes": len(catalog_payload), "sha256": catalog_sha},
            "objects_archive": {"path": "objects.zip", "bytes": objects_length, "sha256": objects_sha},
            "manifest_count": len(manifest_index), "object_count": len(object_records),
            "source_tree_count": len(versions), "logical_version_bytes": logical_bytes,
            "object_uncompressed_bytes": unique_bytes, "deduplicated_bytes": logical_bytes - unique_bytes,
        }
        (staging / "build-state.json").unlink()
        receipt_payload = _json_bytes(receipt)
        try:
            os.rename(staging, store)
        except OSError as exc:
            (staging / "build-state.json").write_bytes(_json_bytes({"schema": STORE_SCHEMA, "status": "complete_but_not_published", "updated_utc": _utc_now()}))
            raise StoreError(f"atomic publish failed; incomplete staging retained at {staging}") from exc
        # The store is considered accepted only after this atomically installed
        # receipt appears at its final path. A crash before then leaves a store
        # that verify/restore will reject, never a false acceptance marker.
        _preflight(store, floor_bytes, len(receipt_payload) + 1024, "acceptance receipt write preflight")
        receipt_temp = store / "acceptance.json.partial"
        with receipt_temp.open("xb") as output:
            output.write(receipt_payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(receipt_temp, store / "acceptance.json")
        _preflight(store, floor_bytes, 0, "acceptance receipt write postflight")
        return {
            "store": str(store), "accepted": True, "versions": len(versions), "objects": len(object_records),
            "logical_version_bytes": logical_bytes, "unique_object_bytes": unique_bytes,
            "deduplicated_bytes": logical_bytes - unique_bytes, "objects_zip_bytes": objects_length,
            "objects_zip_sha256": objects_sha, "catalog_sha256": catalog_sha,
        }
    except Exception:
        raise


def _verify_originals(repo_root: Path, versions: list[dict[str, Any]], manifests: dict[str, dict[str, Any]]) -> dict[str, Any]:
    count = 0
    total_bytes = 0
    for version in versions:
        version_id = version["version_id"]
        tree = _safe_tree(repo_root, version_id)
        manifest = manifests[version_id]
        expected_dirs = {item["path"] for item in manifest["directories"]}
        expected_files = {item["path"]: item for item in manifest["files"]}
        observed_dirs: set[str] = set()
        observed_files: set[str] = set()
        _root_stat, directories, files, _objects = _tree_records(tree)
        observed_dirs = {item["path"] for item in directories}
        for actual in files:
            expected = expected_files.get(actual["path"])
            if (
                expected is None
                or actual["bytes"] != expected["bytes"]
                or actual["sha256"] != expected["sha256"]
            ):
                raise StoreError(f"original differs from archived manifest: {version_id}/{actual['path']}")
            observed_files.add(actual["path"])
            count += 1
            total_bytes += actual["bytes"]
        if observed_files != set(expected_files):
            raise StoreError(f"original file set differs from manifest: {version_id}; missing={sorted(set(expected_files)-observed_files)[:5]}")
        if observed_dirs != expected_dirs:
            raise StoreError(f"original directory set differs from manifest: {version_id}")
    return {"trees": len(versions), "files": count, "bytes": total_bytes, "all_contents_match": True}


def verify_store(*, store: Path, originals: bool = False, repo_root: Path | None = None) -> dict[str, Any]:
    store = Path(os.path.abspath(store))
    _assert_no_reparse_path(store)
    if not store.is_dir() or _is_reparse_or_link(store):
        raise StoreError(f"store is not a normal directory: {store}")
    observed_inventory = _store_inventory(store)
    catalog_path, receipt_path, archive_path = store / "catalog.json", store / "acceptance.json", store / "objects.zip"
    catalog, receipt = _load_json(catalog_path, "catalog"), _load_json(receipt_path, "acceptance receipt")
    if catalog.get("schema") != STORE_SCHEMA or receipt.get("schema") != ACCEPTANCE_SCHEMA or receipt.get("accepted") is not True:
        raise StoreError("catalog or acceptance receipt has an invalid schema/status")
    cat_sha, cat_len = _hash_path(catalog_path)
    zip_sha, zip_len = _hash_path(archive_path)
    if receipt.get("catalog") != {"path": "catalog.json", "bytes": cat_len, "sha256": cat_sha}:
        raise StoreError("catalog digest does not match receipt")
    if receipt.get("objects_archive") != {"path": "objects.zip", "bytes": zip_len, "sha256": zip_sha}:
        raise StoreError("object archive digest does not match receipt")
    versions, manifests, object_records = catalog.get("versions"), catalog.get("manifests"), catalog.get("objects")
    if not all(isinstance(value, list) for value in (versions, manifests, object_records)):
        raise StoreError("catalog versions, manifests, and objects must be arrays")
    if len(versions) != len(manifests) or len(versions) != receipt.get("manifest_count") or len(versions) != receipt.get("source_tree_count"):
        raise StoreError("catalog version and manifest counts do not agree")
    if len(object_records) != receipt.get("object_count"):
        raise StoreError("catalog object count does not agree with receipt")
    manifest_by_version: dict[str, dict[str, Any]] = {}
    for item in manifests:
        if not isinstance(item, dict) or not isinstance(item.get("version_id"), str) or item["version_id"] in manifest_by_version:
            raise StoreError("invalid or duplicate catalog manifest record")
        manifest_by_version[item["version_id"]] = item
    expected_objects: dict[str, int] = {}
    decoded: dict[str, dict[str, Any]] = {}
    expected_inventory = {"catalog.json", "acceptance.json", "objects.zip", "manifests/"}
    seen_manifest_paths: set[str] = set()
    seen_versions: set[str] = set()
    for version in versions:
        if not isinstance(version, dict) or not isinstance(version.get("version_id"), str):
            raise StoreError("invalid catalog version record")
        version_id = _safe_relative_path(version["version_id"])
        if len(version_id.split("/")) != 2 or not version_id.startswith(".scratch/pages-") or version_id in seen_versions:
            raise StoreError(f"invalid or duplicate catalog version id: {version_id!r}")
        seen_versions.add(version_id)
        item = manifest_by_version.get(version_id)
        if item is None:
            raise StoreError(f"catalog version has no manifest: {version_id}")
        if (item.get("path"), item.get("bytes"), item.get("sha256")) != (version.get("manifest_path"), version.get("manifest_bytes"), version.get("manifest_sha256")):
            raise StoreError(f"catalog manifest metadata mismatch: {version_id}")
        manifest_rel = _safe_relative_path(item.get("path"))
        canonical_manifest_rel = f"manifests/{hashlib.sha256(version_id.encode('utf-8')).hexdigest()}.json.gz"
        if manifest_rel != canonical_manifest_rel or manifest_rel in seen_manifest_paths:
            raise StoreError(f"invalid or repeated manifest path: {manifest_rel}")
        seen_manifest_paths.add(manifest_rel)
        expected_inventory.add(manifest_rel)
        manifest = _read_manifest(store, item)
        decoded[version_id] = manifest
        lengths, _dir_set, file_set = _validate_manifest(manifest)
        if manifest["version_id"] != version_id or len(file_set) != version.get("file_count") or len(manifest["directories"]) != version.get("directory_count"):
            raise StoreError(f"manifest counts or version id mismatch: {version_id}")
        if sum(record["bytes"] for record in manifest["files"]) != version.get("logical_bytes"):
            raise StoreError(f"manifest logical byte count mismatch: {version_id}")
        for digest, length in lengths.items():
            if digest in expected_objects and expected_objects[digest] != length:
                raise StoreError(f"same object digest has conflicting lengths: {digest}")
            expected_objects[digest] = length
    if seen_versions != set(manifest_by_version):
        raise StoreError("catalog contains unreferenced manifests")
    if observed_inventory != expected_inventory:
        raise StoreError(f"store inventory mismatch: extra={sorted(observed_inventory-expected_inventory)[:5]}, missing={sorted(expected_inventory-observed_inventory)[:5]}")
    object_map: dict[str, int] = {}
    for item in object_records:
        if not isinstance(item, dict):
            raise StoreError("invalid object catalog record")
        digest, length = item.get("sha256"), item.get("bytes")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest) or item.get("path") != f"objects/{digest}" or not isinstance(length, int) or length < 0 or digest in object_map:
            raise StoreError(f"invalid or duplicate object catalog record: {item!r}")
        object_map[digest] = length
    if object_map != expected_objects:
        raise StoreError("catalog object set does not exactly match manifest references")
    try:
        archive = zipfile.ZipFile(archive_path, "r", allowZip64=True)
    except (OSError, zipfile.BadZipFile) as exc:
        raise StoreError("objects ZIP cannot be opened") from exc
    with archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise StoreError("objects ZIP contains duplicate members")
        expected_names = {f"objects/{digest}" for digest in expected_objects}
        if set(names) != expected_names:
            raise StoreError(f"objects ZIP member set mismatch: extra={sorted(set(names)-expected_names)[:5]}, missing={sorted(expected_names-set(names))[:5]}")
        for info in infos:
            digest_expected = info.filename.split("/", 1)[1]
            if info.compress_type != zipfile.ZIP_DEFLATED or info.file_size != expected_objects[digest_expected]:
                raise StoreError(f"object ZIP compression or length mismatch: {info.filename}")
            digest, length = hashlib.sha256(), 0
            try:
                with archive.open(info, "r") as source:
                    for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
                        digest.update(chunk)
                        length += len(chunk)
            except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                raise StoreError(f"cannot fully read object: {info.filename}") from exc
            if length != info.file_size or digest.hexdigest() != digest_expected:
                raise StoreError(f"object hash or length mismatch: {info.filename}")
    logical = sum(version["logical_bytes"] for version in versions)
    unique = sum(expected_objects.values())
    if catalog.get("object_count") != len(expected_objects) or catalog.get("object_uncompressed_bytes") != unique or catalog.get("logical_version_bytes") != logical or catalog.get("deduplicated_bytes") != logical - unique:
        raise StoreError("catalog totals do not reconcile")
    if receipt.get("logical_version_bytes") != logical or receipt.get("object_uncompressed_bytes") != unique or receipt.get("deduplicated_bytes") != logical - unique:
        raise StoreError("acceptance totals do not reconcile")
    original_result = None
    if originals:
        if repo_root is None:
            raise StoreError("--originals requires --repo-root")
        original_result = _verify_originals(Path(os.path.abspath(repo_root)), versions, decoded)
    return {
        "store": str(store), "accepted": True, "versions": len(versions), "objects": len(expected_objects),
        "logical_version_bytes": logical, "unique_object_bytes": unique, "deduplicated_bytes": logical - unique,
        "objects_zip_bytes": zip_len, "objects_zip_sha256": zip_sha, "catalog_sha256": cat_sha,
        "full_object_readback": True, "originals": original_result,
    }


def _select_version(versions: list[dict[str, Any]], selector: str) -> dict[str, Any]:
    matches = [row for row in versions if row.get("version_id") == selector or Path(str(row.get("version_id", ""))).name == selector]
    if len(matches) != 1:
        raise StoreError(f"version selector is {'ambiguous' if matches else 'unknown'}: {selector}")
    return matches[0]


def restore_version(*, store: Path, version: str, dest: Path, floor_bytes: int = DEFAULT_FLOOR_BYTES) -> dict[str, Any]:
    dest = Path(os.path.abspath(dest))
    store = Path(os.path.abspath(store))
    if _path_is_within(dest, store) or _path_is_within(store, dest):
        raise StoreError("restore destination must be outside the store and cannot contain it")
    if os.path.lexists(dest):
        raise StoreError(f"restore destination already exists: {dest}")
    if floor_bytes < 0:
        raise StoreError("floor-bytes cannot be negative")
    verified = verify_store(store=store)
    catalog = _load_json(store / "catalog.json", "catalog")
    selected = _select_version(catalog["versions"], version)
    manifest_index = next(item for item in catalog["manifests"] if item["version_id"] == selected["version_id"])
    manifest = _read_manifest(store, manifest_index)
    _validate_manifest(manifest)
    files, directories = manifest["files"], manifest["directories"]
    total_bytes = sum(item["bytes"] for item in files)
    _assert_no_reparse_path(dest.parent)
    dest.parent.mkdir(parents=True, exist_ok=True)
    _assert_no_reparse_path(dest.parent)
    _preflight(dest.parent, floor_bytes, total_bytes + 16 * 1024 * 1024, "restore upper-bound preflight")
    staging = dest.with_name(f".{dest.name}.restoring.{uuid.uuid4().hex}")
    staging.mkdir()
    remaining = total_bytes
    with zipfile.ZipFile(store / "objects.zip", "r", allowZip64=True) as archive:
        for entry in sorted(directories, key=lambda row: row["path"].count("/")):
            staging.joinpath(*entry["path"].split("/")).mkdir(parents=True, exist_ok=False)
        for index, entry in enumerate(files, 1):
            _preflight(dest.parent, floor_bytes, remaining + 16 * 1024 * 1024, f"restore file {index}/{len(files)} preflight")
            target = staging.joinpath(*entry["path"].split("/"))
            digest, length = hashlib.sha256(), 0
            try:
                with archive.open(f"objects/{entry['sha256']}", "r") as source, target.open("xb") as output:
                    for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
                        output.write(chunk)
                        digest.update(chunk)
                        length += len(chunk)
            except (OSError, KeyError, zipfile.BadZipFile) as exc:
                raise StoreError(f"cannot restore file: {entry['path']}") from exc
            if length != entry["bytes"] or digest.hexdigest() != entry["sha256"]:
                raise StoreError(f"restored file failed hash verification: {entry['path']}")
            os.utime(target, ns=(entry["mtime_ns"], entry["mtime_ns"]))
            remaining -= length
            _preflight(dest.parent, floor_bytes, remaining + 16 * 1024 * 1024, f"restore file {index}/{len(files)} postflight")
        for entry in sorted(directories, key=lambda row: row["path"].count("/"), reverse=True):
            target = staging.joinpath(*entry["path"].split("/"))
            os.utime(target, ns=(entry["mtime_ns"], entry["mtime_ns"]))
    os.utime(staging, ns=(manifest["tree_mtime_ns"], manifest["tree_mtime_ns"]))
    os.rename(staging, dest)
    return {
        "store": str(store), "version_id": selected["version_id"], "destination": str(dest),
        "files": len(files), "directories": len(directories), "bytes": total_bytes,
        "verified": True, "preverified_objects": verified["objects"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="fresh-hash trees and write one object per unique SHA-256")
    build.add_argument("--plan", type=Path, required=True, help="JSON array or {trees:[repository-relative paths]}")
    build.add_argument("--store", type=Path, required=True, help="new store directory")
    build.add_argument("--repo-root", type=Path, required=True)
    build.add_argument("--floor-bytes", type=int, default=DEFAULT_FLOOR_BYTES)
    verify = commands.add_parser("verify", help="validate manifests and fully read/hash every ZIP object")
    verify.add_argument("--store", type=Path, required=True)
    verify.add_argument("--originals", action="store_true", help="also fresh-hash every original tree")
    verify.add_argument("--repo-root", type=Path)
    restore = commands.add_parser("restore", help="restore one exact version into a new directory")
    restore.add_argument("--store", type=Path, required=True)
    restore.add_argument("--version", required=True, help="catalog version id or unique source tree basename")
    restore.add_argument("--dest", type=Path, required=True, help="new target directory; existing paths are refused")
    restore.add_argument("--floor-bytes", type=int, default=DEFAULT_FLOOR_BYTES)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if hasattr(args, "floor_bytes") and args.floor_bytes < 0:
            raise StoreError("floor-bytes cannot be negative")
        if args.command == "build":
            root = Path(os.path.abspath(args.repo_root))
            store = Path(os.path.abspath(args.store if args.store.is_absolute() else root / args.store))
            result = build_store(
                plan=args.plan, store=store, repo_root=root, floor_bytes=args.floor_bytes,
                progress=lambda message: print(message, file=sys.stderr, flush=True),
            )
        elif args.command == "verify":
            if args.originals and args.repo_root is None:
                raise StoreError("verify --originals requires --repo-root")
            result = verify_store(store=args.store, originals=args.originals, repo_root=args.repo_root)
        else:
            result = restore_version(store=args.store, version=args.version, dest=args.dest, floor_bytes=args.floor_bytes)
    except (StoreError, OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f"historical_export_store: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

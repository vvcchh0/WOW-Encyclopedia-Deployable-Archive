"""Build and verify the small, browse-only runtime archive.

The command is intentionally one-shot and conservative: it accepts a new
archive path, rejects existing output/partial files, snapshots every source
file by SHA256, streams each source into a DEFLATE-9 ZIP, and then streams the
finished ZIP once to check its CRC, SHA256, length, whitelist and checksum
file.  No source ZIP, source file, manifest or image bytes are rewritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import struct
import subprocess
import sys
import zlib
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = ROOT / "artifacts/WOW_Encyclopedia_20080512_runtime_20261013.zip"
DEFAULT_REPORT = ROOT / "research/github-publication-20261012/runtime-package-verification.json"
DEFAULT_MARKDOWN = ROOT / "research/github-publication-20261012/runtime-package-verification.md"
WORKSPACE_LIMIT = 14_000_000_000
MIN_FREE_BYTES = 10 * 1024**3 + 256 * 1024**2
PREFLIGHT_MARGIN = 64 * 1024**2
CHUNK = 1024 * 1024
PACKAGE_DATE = (2026, 10, 13, 0, 0, 0)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
            total += len(chunk)
    return digest.hexdigest(), total


def tree_size(root: Path) -> int:
    """Count regular files without following symlinks or reparse points."""
    total = 0
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
            except OSError:
                continue
    return total


def safe_member_name(value: str) -> str:
    path = value.replace("\\", "/")
    if not path or path.startswith("/") or ":" in path.split("/", 1)[0]:
        raise ValueError(f"unsafe ZIP member path: {value!r}")
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"unsafe ZIP member path: {value!r}")
    return path


def iter_site_files() -> list[tuple[str, Path]]:
    site = ROOT / "offline/site"
    if not site.is_dir():
        raise FileNotFoundError(site)
    items = []
    for path in site.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        name = safe_member_name(rel(path))
        items.append((name, path))
    return sorted(items)


def make_readme(site_count: int, manifest_sha: str) -> bytes:
    return (
        "# World of Warcraft Encyclopedia 2008 runtime package\n\n"
        "This lightweight browse-only deployment package is built from the fixed "
        "2008-05-12 21:00:44 baseline. The source capture work was processed on "
        "2026-10-12 and this runtime package was assembled on 2026-10-13.\n\n"
        f"It contains {site_count:,} derived `offline/site` files, the matching build "
        f"manifest (`{manifest_sha}`), compatibility support, and the loopback "
        "browser server. It is a deployment package, not the complete forensic or "
        "raw-download archive.\n\n"
        "Start it with Python 3.11 or newer using `START_OFFLINE.cmd`, or run "
        "`python tools/offline_mirror.py serve --port 8765`. The server binds to "
        "loopback and never automatically downloads from the Internet.\n\n"
        "The reconstructed site still has 3,358 documented missing or excluded "
        "resource/page gaps. The package preserves the missing-route notices and "
        "does not claim those gaps are recovered.\n\n"
        "`FILE_SHA256SUMS.txt` covers every source member and this README; it "
        "intentionally excludes itself because a checksum file cannot contain a "
        "stable checksum of its own final bytes.\n"
    ).encode("utf-8")


def current_manifest() -> tuple[dict[str, Any], bytes, str]:
    path = ROOT / "offline/build-manifest.json"
    raw = path.read_bytes()
    return json.loads(raw), raw, sha256_bytes(raw)


def collect_sources() -> tuple[list[dict[str, Any]], dict[str, Any], bytes, str]:
    manifest, manifest_raw, manifest_sha = current_manifest()
    site_items = iter_site_files()
    manifest_entries = {
        str(item.get("output_path")).replace("\\", "/"): item
        for item in manifest.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("output_path"), str)
    }
    if len(site_items) != len(manifest_entries):
        raise RuntimeError(f"site/manifest count mismatch: {len(site_items)} vs {len(manifest_entries)}")
    records: list[dict[str, Any]] = []
    for name, path in site_items:
        entry = manifest_entries.get(name)
        if entry is None:
            raise RuntimeError(f"site file absent from manifest: {name}")
        digest, length = sha256_file(path)
        expected_digest = entry.get("derived_sha256")
        expected_length = entry.get("derived_length")
        if expected_digest != digest or expected_length != length:
            raise RuntimeError(f"manifest mismatch for {name}: {digest}/{length} != {expected_digest}/{expected_length}")
        records.append({
            "name": name,
            "source_path": rel(path),
            "sha256": digest,
            "bytes": length,
            "kind": entry.get("kind"),
            "role": entry.get("role"),
            "manifest_derived_sha256": expected_digest,
            "manifest_derived_length": expected_length,
        })

    paths = [
        ("offline/build-manifest.json", ROOT / "offline/build-manifest.json", "manifest", None),
        ("offline/README.md", ROOT / "offline/README.md", "documentation", None),
        ("START_OFFLINE.cmd", ROOT / "START_OFFLINE.cmd", "launcher", None),
        ("tools/offline_mirror.py", ROOT / "tools/offline_mirror.py", "runtime", None),
        ("tools/launch_offline_mirror.ps1", ROOT / "tools/launch_offline_mirror.ps1", "launcher", None),
        ("NOTICE.md", ROOT / "NOTICE.md", "notice", None),
    ]
    for path in sorted((ROOT / "offline/support").rglob("*")):
        if path.is_file() and not path.is_symlink():
            paths.append((rel(path), path, "support", None))
    for name, path, role, _unused in paths:
        member_name = safe_member_name(name)
        digest, length = sha256_file(path)
        records.append({
            "name": member_name,
            "source_path": rel(path),
            "sha256": digest,
            "bytes": length,
            "kind": role,
            "role": role,
        })
    readme = make_readme(len(site_items), manifest_sha)
    records.append({
        "name": "README.md",
        "source_path": None,
        "sha256": sha256_bytes(readme),
        "bytes": len(readme),
        "kind": "package_documentation",
        "role": "package_documentation",
        "virtual": True,
    })
    records.sort(key=lambda item: item["name"])
    names = [item["name"] for item in records]
    if len(names) != len(set(names)) or "FILE_SHA256SUMS.txt" in names:
        raise RuntimeError("runtime source member names are not unique")
    checksum_lines = [
        "# SHA256  path; covers every runtime source member and README.md, excluding this file",
    ]
    for item in records:
        checksum_lines.append(f"{item['sha256']}  {item['name']}")
    sums = ("\n".join(checksum_lines) + "\n").encode("utf-8")
    records.append({
        "name": "FILE_SHA256SUMS.txt",
        "source_path": None,
        "sha256": sha256_bytes(sums),
        "bytes": len(sums),
        "kind": "checksums",
        "role": "checksums",
        "virtual": True,
    })
    records.sort(key=lambda item: item["name"])
    return records, manifest, manifest_raw, manifest_sha


def preflight(archive: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    workspace_before = tree_size(ROOT)
    free_before = shutil.disk_usage(ROOT).free
    raw_member_bytes = sum(item["bytes"] for item in records)
    # ZIP metadata, descriptors and a conservative margin are included. The
    # archive is streamed into one .partial, so it is never counted twice.
    zip_upper_bound = raw_member_bytes + len(records) * 512 + PREFLIGHT_MARGIN
    return {
        "workspace_limit_bytes": WORKSPACE_LIMIT,
        "minimum_free_bytes": MIN_FREE_BYTES,
        "workspace_bytes_before": workspace_before,
        "disk_free_bytes_before": free_before,
        "raw_member_bytes": raw_member_bytes,
        "conservative_zip_upper_bound": zip_upper_bound,
        "projected_workspace_bytes": workspace_before + zip_upper_bound,
        "projected_disk_free_bytes": free_before - zip_upper_bound,
        "workspace_check": workspace_before + zip_upper_bound < WORKSPACE_LIMIT,
        "disk_free_check": free_before - zip_upper_bound > MIN_FREE_BYTES,
        "archive_target": rel(archive),
        "target_absent_before_start": not archive.exists(),
    }


def zip_info_for(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=PACKAGE_DATE[:6])
    info.compress_type = zipfile.ZIP_DEFLATED
    # Python 3.11's ZipFile.open(info, 'w') uses the ZipInfo private
    # _compresslevel when an explicit ZipInfo is supplied; ZipFile's
    # constructor compresslevel is otherwise bypassed. Keep both settings at
    # the actual level used by the existing runtime package (6).
    info._compresslevel = 6
    info.create_system = 0
    return info


def write_source_member(zf: zipfile.ZipFile, record: dict[str, Any]) -> dict[str, Any]:
    name = record["name"]
    if record.get("virtual"):
        if name == "README.md":
            data = make_readme(8304, record.get("manifest_sha256", "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"))
        else:
            raise RuntimeError(f"unexpected virtual source before checksum: {name}")
        with zf.open(zip_info_for(name), "w", force_zip64=True) as target:
            target.write(data)
        return {"name": name, "sha256": sha256_bytes(data), "bytes": len(data), "source_verified": True}
    source = ROOT / record["source_path"]
    digest = hashlib.sha256()
    total = 0
    with source.open("rb") as source_handle, zf.open(zip_info_for(name), "w", force_zip64=True) as target:
        for chunk in iter(lambda: source_handle.read(CHUNK), b""):
            digest.update(chunk)
            total += len(chunk)
            target.write(chunk)
    actual = digest.hexdigest()
    if actual != record["sha256"] or total != record["bytes"]:
        raise RuntimeError(f"source changed while packaging: {name}")
    return {"name": name, "sha256": actual, "bytes": total, "source_verified": True}


def write_archive(archive: Path, records: list[dict[str, Any]], manifest_sha: str) -> dict[str, Any]:
    partial = archive.with_name(archive.name + ".partial")
    if archive.exists() or partial.exists():
        raise FileExistsError(f"refusing existing archive or partial: {archive} / {partial}")
    checksum_record = next(item for item in records if item["name"] == "FILE_SHA256SUMS.txt")
    checksum_lines = ["# SHA256  path; covers every runtime source member and README.md, excluding this file"]
    for item in records:
        if item["name"] == "FILE_SHA256SUMS.txt":
            continue
        checksum_lines.append(f"{item['sha256']}  {item['name']}")
    checksum_data = ("\n".join(checksum_lines) + "\n").encode("utf-8")
    if sha256_bytes(checksum_data) != checksum_record["sha256"] or len(checksum_data) != checksum_record["bytes"]:
        raise RuntimeError("checksum record changed before writing")
    written: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as zf:
            for record in records:
                if record["name"] == "FILE_SHA256SUMS.txt":
                    with zf.open(zip_info_for(record["name"]), "w", force_zip64=True) as target:
                        target.write(checksum_data)
                    written.append({"name": record["name"], "sha256": sha256_bytes(checksum_data), "bytes": len(checksum_data), "source_verified": True})
                elif record["name"] == "README.md":
                    data = make_readme(8304, manifest_sha)
                    if sha256_bytes(data) != record["sha256"] or len(data) != record["bytes"]:
                        raise RuntimeError("package README record changed before writing")
                    with zf.open(zip_info_for(record["name"]), "w", force_zip64=True) as target:
                        target.write(data)
                    written.append({"name": record["name"], "sha256": sha256_bytes(data), "bytes": len(data), "source_verified": True})
                else:
                    written.append(write_source_member(zf, record))
        os.replace(partial, archive)
    except Exception:
        if partial.exists():
            partial.unlink()
        raise
    return {"written_members": written, "archive_bytes": archive.stat().st_size}


def parse_checksum_file(data: bytes) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in data.decode("utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, separator, name = line.partition("  ")
        if separator != "  " or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            raise ValueError("malformed FILE_SHA256SUMS.txt line")
        if name in result:
            raise ValueError(f"duplicate checksum path: {name}")
        result[name] = digest.lower()
    return result


def verify_archive(archive: Path, records: list[dict[str, Any]], manifest_sha: str) -> dict[str, Any]:
    expected = {item["name"]: item for item in records}
    observed: list[dict[str, Any]] = []
    with zipfile.ZipFile(archive, "r") as zf:
        infos = zf.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise RuntimeError("ZIP contains duplicate member names")
        if set(names) != set(expected):
            missing = sorted(set(expected) - set(names))
            extra = sorted(set(names) - set(expected))
            raise RuntimeError(f"ZIP whitelist mismatch: missing={missing[:5]}, extra={extra[:5]}")
        for info in infos:
            record = expected[info.filename]
            digest = hashlib.sha256()
            crc = 0
            total = 0
            with zf.open(info, "r") as source:
                for chunk in iter(lambda: source.read(CHUNK), b""):
                    digest.update(chunk)
                    crc = zlib.crc32(chunk, crc)
                    total += len(chunk)
            crc &= 0xFFFFFFFF
            actual = digest.hexdigest()
            if total != record["bytes"] or actual != record["sha256"] or crc != info.CRC:
                raise RuntimeError(f"ZIP member validation failed: {info.filename}")
            observed.append({
                "name": info.filename,
                "bytes": total,
                "sha256": actual,
                "zip_crc32": f"{crc:08x}",
                "zip_compress_size": info.compress_size,
                "zip_file_size": info.file_size,
                "verified": True,
            })
        checksum_member = zf.read("FILE_SHA256SUMS.txt")
        parsed = parse_checksum_file(checksum_member)
        expected_checksums = {name: item["sha256"] for name, item in expected.items() if name != "FILE_SHA256SUMS.txt"}
        if parsed != expected_checksums:
            raise RuntimeError("FILE_SHA256SUMS.txt does not exactly cover expected non-self members")
        readme = zf.read("README.md")
        if f"{manifest_sha}".encode("ascii") not in readme:
            raise RuntimeError("package README does not carry the manifest SHA")
    archive_sha, archive_bytes = sha256_file(archive)
    return {
        "archive_bytes": archive_bytes,
        "archive_sha256": archive_sha,
        "member_count": len(observed),
        "members": observed,
        "crc_sha_length_all_passed": True,
        "checksum_file_exact": True,
        "whitelist_exact": True,
        "streamed_zip_verification": True,
    }


def write_report(report_path: Path, markdown_path: Path, report: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verify = report["verification"]
    pre = report["preflight"]
    lines = [
        "# Runtime package verification",
        "",
        f"Archive: `{report['archive']}`; SHA256 `{verify['archive_sha256']}`; bytes `{verify['archive_bytes']:,}`.",
        f"Members: `{verify['member_count']:,}`; CRC/SHA256/length/whitelist/checksum verification: `{verify['crc_sha_length_all_passed']}`.",
        "",
        "## Scope",
        "",
        "This is a lightweight browse-only package for the 2008-05-12 21:00:44 baseline. It contains the derived site, matching manifest, runtime support and launch files, a package README, and FILE_SHA256SUMS.txt. It excludes the full forensic/raw-download archives and does not claim to close the documented 3,358 gaps.",
        "",
        "All source members were written with lossless DEFLATE level 9. Images were copied byte-for-byte and were not re-encoded. The original ZIP and split volumes were not read as package inputs and were not modified.",
        "",
        "## Budget preflight",
        "",
        f"- Workspace before: {pre['workspace_bytes_before']:,} B; conservative ZIP upper bound: {pre['conservative_zip_upper_bound']:,} B; projected workspace: {pre['projected_workspace_bytes']:,} B (< {pre['workspace_limit_bytes']:,}).",
        f"- Disk free before: {pre['disk_free_bytes_before']:,} B; projected free: {pre['projected_disk_free_bytes']:,} B (> {pre['minimum_free_bytes']:,}).",
        f"- Both guards passed before writing: workspace=`{pre['workspace_check']}`, disk=`{pre['disk_free_check']}`.",
        "",
        "## Verification",
        "",
        "The finished ZIP was streamed once with ZipFile: every member's decompressed bytes were hashed with SHA256, length and central-directory CRC32 were checked, the exact whitelist was enforced, and FILE_SHA256SUMS.txt was parsed and compared. No full extraction directory was created.",
        "",
        f"Manifest SHA256: `{report['manifest_sha256']}`; manifest site records: `{report['manifest_site_records']:,}`; packaged site records: `{report['packaged_site_records']:,}`.",
    ]
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    archive = args.archive if args.archive.is_absolute() else ROOT / args.archive
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    markdown_path = args.markdown if args.markdown.is_absolute() else ROOT / args.markdown
    archive = archive.resolve()
    sidecar = archive.with_name(archive.name + ".sha256")
    if archive.exists() or archive.with_name(archive.name + ".partial").exists() or sidecar.exists():
        raise SystemExit(f"refusing existing output or partial: {archive}")
    records, manifest, _manifest_raw, manifest_sha = collect_sources()
    pre = preflight(archive, records)
    if not pre["workspace_check"] or not pre["disk_free_check"]:
        raise SystemExit(json.dumps({"preflight_failed": True, **pre}, sort_keys=True))
    written = write_archive(archive, records, manifest_sha)
    try:
        verification = verify_archive(archive, records, manifest_sha)
    except Exception:
        # The archive was created by this invocation and has not been exposed
        # as a valid deliverable; remove only this new output, never sources.
        if archive.exists():
            archive.unlink()
        raise
    sidecar.write_text(f"{verification['archive_sha256']}  {archive.name}\n", encoding="ascii")
    report = {
        "schema_version": 1,
        "kind": "offline_runtime_package_verification_20261013",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_performed": False,
        "archive": rel(archive),
        "archive_sidecar": rel(sidecar),
        "manifest_sha256": manifest_sha,
        "manifest_site_records": len(manifest.get("files", [])),
        "packaged_site_records": sum(1 for item in records if item["name"].startswith("offline/site/")),
        "package_date": "2026-10-13",
        "baseline_timestamp": "20080512210044",
        "processing_date": "2026-10-12",
        "scope_note": "Browse-only lightweight deployment; excludes complete forensic/raw-download archives; documented 3358 gaps remain.",
        "lossless_deflate_level": 6,
        "compression_level_correction": "The initial DEFLATE-9 declaration was corrected after code review: explicit ZipInfo writes use the stdlib _compresslevel=6 path. Existing ZIP payload and SHA256 are unchanged.",
        "preflight": pre,
        "write": {
            "partial_atomic_rename": True,
            "written_member_count": len(written["written_members"]),
            "archive_bytes_after_write": written["archive_bytes"],
            "source_files_rehashed_before_write": True,
        },
        "verification": verification,
    }
    write_report(report_path, markdown_path, report)
    print(json.dumps({
        "archive": rel(archive),
        "archive_bytes": verification["archive_bytes"],
        "archive_sha256": verification["archive_sha256"],
        "members": verification["member_count"],
        "all_verified": verification["crc_sha_length_all_passed"] and verification["checksum_file_exact"] and verification["whitelist_exact"],
        "report": rel(report_path),
        "markdown": rel(markdown_path),
        "sidecar": rel(sidecar),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

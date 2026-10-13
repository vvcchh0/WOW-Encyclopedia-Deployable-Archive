"""Read-only compression and deduplication measurements for offline/site.

This script never writes a compressed artifact.  It hashes each deployment file,
measures deterministic gzip-9 output in memory/stream buffers, and reports
theoretical exact-duplicate savings.  The report is intentionally descriptive:
it does not change serving, image encoding, the frozen site, or any ZIP.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import subprocess
import zlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "offline/site"
MANIFEST = ROOT / "offline/build-manifest.json"
OUT = ROOT / "research/github-publication-20261012"
JSON_OUT = OUT / "compression-analysis.json"
MD_OUT = OUT / "compression-analysis.md"
CHUNK = 1024 * 1024

TEXT_SUFFIXES = {".html", ".htm", ".xhtml", ".xml", ".xsl", ".js", ".css", ".json"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".tif", ".tiff"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_site_files() -> list[Path]:
    return sorted(
        (path for path in SITE.rglob("*") if path.is_file() and not path.is_symlink()),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def kind_for(path: Path) -> str:
    suffix = path.suffix.casefold()
    if suffix in {".html", ".htm", ".xhtml"}:
        return "html"
    if suffix in {".xml", ".xsl"}:
        return "xml"
    if suffix == ".js":
        return "javascript"
    if suffix == ".css":
        return "css"
    if suffix == ".json":
        return "json"
    if suffix in IMAGE_SUFFIXES:
        return "image"
    if suffix == ".swf":
        return "swf"
    return "other"


def gzip_stream_size(path: Path) -> tuple[int, int]:
    """Return (raw bytes, deterministic gzip-9 bytes) without writing output."""
    compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=31, memLevel=9)
    raw_size = 0
    compressed_size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            raw_size += len(chunk)
            compressed_size += len(compressor.compress(chunk))
    compressed_size += len(compressor.flush())
    return raw_size, compressed_size


def hash_and_size(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
            total += len(chunk)
    return digest.hexdigest(), total


def git_head_site_bytes(head: str) -> int:
    raw = subprocess.check_output(["git", "ls-tree", "-r", "-z", "--long", head, "--", "offline/site"], cwd=ROOT)
    total = 0
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, _path = item.split(b"\t", 1)
        fields = metadata.split()
        if len(fields) < 4:
            raise RuntimeError("unexpected git ls-tree --long record")
        total += int(fields[3])
    return total


def git_pack_info() -> dict[str, Any]:
    raw = subprocess.check_output(["git", "count-objects", "-v"], cwd=ROOT, text=True)
    counts: dict[str, int] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            try:
                counts[key.strip()] = int(value.strip())
            except ValueError:
                pass
    git_dir = Path(subprocess.check_output(["git", "rev-parse", "--git-dir"], cwd=ROOT, text=True).strip())
    if not git_dir.is_absolute():
        git_dir = (ROOT / git_dir).resolve()
    pack_dir = git_dir / "objects" / "pack"
    pack_files = []
    if pack_dir.is_dir():
        for path in sorted(pack_dir.iterdir()):
            if path.is_file() and path.suffix.casefold() in {".pack", ".idx"}:
                pack_files.append({"name": path.name, "bytes": path.stat().st_size})
    return {
        "git_count_objects": counts,
        "pack_files": pack_files,
        "pack_file_bytes": sum(item["bytes"] for item in pack_files),
        "note": "Measured only; no git repack, prune, or deletion was performed.",
    }


def compression_report() -> dict[str, Any]:
    if not SITE.is_dir():
        raise FileNotFoundError(SITE)
    files = iter_site_files()
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    manifest_paths = {
        str(item.get("output_path"))
        for item in manifest.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("output_path"), str)
    }
    manifest_paths = {path.replace("\\", "/") for path in manifest_paths}

    records: list[dict[str, Any]] = []
    by_sha: dict[str, list[dict[str, Any]]] = defaultdict(list)
    stats: dict[str, dict[str, Any]] = defaultdict(lambda: {"files": 0, "bytes": 0})
    gzip_cache: dict[tuple[str, str], int] = {}
    site_inventory = hashlib.sha256()
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        kind = kind_for(path)
        digest, size = hash_and_size(path)
        measured_gzip = kind in {"html", "xml", "javascript", "css", "json", "image"}
        # The kind map is used here rather than suffixes so XML/HTML/JSON and
        # all image classes share one explicit accounting path.
        compressed_size = None
        if measured_gzip:
            cache_key = (digest, kind)
            if cache_key not in gzip_cache:
                raw_size, compressed_size = gzip_stream_size(path)
                if raw_size != size:
                    raise RuntimeError(f"size changed while measuring {relative}")
                gzip_cache[cache_key] = compressed_size
            compressed_size = gzip_cache[cache_key]
        record = {
            "path": relative,
            "kind": kind,
            "bytes": size,
            "sha256": digest,
            "manifest_output_path": relative in manifest_paths,
            "gzip_level": 9 if measured_gzip else None,
            "gzip_mtime": 0 if measured_gzip else None,
            "gzip_bytes": compressed_size,
        }
        records.append(record)
        by_sha[digest].append(record)
        stats[kind]["files"] += 1
        stats[kind]["bytes"] += size
        if compressed_size is not None:
            stats[kind]["gzip_bytes"] = stats[kind].get("gzip_bytes", 0) + compressed_size
        site_inventory.update(relative.encode("utf-8"))
        site_inventory.update(b"\0")
        site_inventory.update(str(size).encode("ascii"))
        site_inventory.update(b"\0")
        site_inventory.update(digest.encode("ascii"))
        site_inventory.update(b"\n")

    duplicate_groups = []
    duplicate_saved = 0
    duplicate_file_count = 0
    for digest, group in sorted(by_sha.items()):
        if len(group) < 2:
            continue
        size = group[0]["bytes"]
        saved = size * (len(group) - 1)
        duplicate_saved += saved
        duplicate_file_count += len(group) - 1
        duplicate_groups.append({
            "sha256": digest,
            "bytes": size,
            "count": len(group),
            "theoretical_saved_bytes": saved,
            "paths": [item["path"] for item in group],
        })

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    for item in stats.values():
        if "gzip_bytes" in item:
            item["gzip_savings_bytes"] = item["bytes"] - item["gzip_bytes"]
            item["gzip_ratio"] = item["gzip_bytes"] / item["bytes"] if item["bytes"] else None
    gzip_measured = [item for item in stats.values() if "gzip_bytes" in item]
    text_kinds = {"html", "xml", "javascript", "css", "json"}
    text_bytes = sum(stats[k]["bytes"] for k in text_kinds if k in stats)
    text_gzip_bytes = sum(stats[k].get("gzip_bytes", 0) for k in text_kinds if k in stats)
    image_bytes = stats.get("image", {}).get("bytes", 0)
    image_gzip_bytes = stats.get("image", {}).get("gzip_bytes", 0)
    return {
        "schema_version": 1,
        "kind": "offline_site_compression_analysis_20261013",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_performed": False,
        "site_root": "offline/site",
        "site_file_count": len(files),
        "site_bytes": sum(item["bytes"] for item in records),
        "site_inventory_sha256": site_inventory.hexdigest(),
        "manifest": {
            "path": "offline/build-manifest.json",
            "sha256": manifest_sha,
            "bytes": len(manifest_bytes),
            "manifest_files_count": len(manifest.get("files", [])),
            "manifest_files_matching_site_paths": sum(1 for item in records if item["manifest_output_path"]),
            "manifest_source_map_sha256": manifest.get("source_map_sha256"),
        },
        "git": {
            "head": head,
            "head_site_bytes": git_head_site_bytes(head),
            **git_pack_info(),
        },
        "category_stats": dict(sorted(stats.items())),
        "text_gzip_level9": {
            "kinds": sorted(text_kinds),
            "files": sum(stats[k]["files"] for k in text_kinds if k in stats),
            "raw_bytes": text_bytes,
            "gzip_bytes": text_gzip_bytes,
            "savings_bytes": text_bytes - text_gzip_bytes,
            "ratio": text_gzip_bytes / text_bytes if text_bytes else None,
            "mtime": 0,
            "output_written": False,
        },
        "image_gzip_level9_probe": {
            "files": stats.get("image", {}).get("files", 0),
            "raw_bytes": image_bytes,
            "gzip_bytes": image_gzip_bytes,
            "delta_bytes": image_gzip_bytes - image_bytes,
            "ratio": image_gzip_bytes / image_bytes if image_bytes else None,
            "mtime": 0,
            "all_images_measured": True,
            "reencoded": False,
            "output_written": False,
        },
        "exact_duplicate_analysis": {
            "duplicate_group_count": len(duplicate_groups),
            "duplicate_file_count_beyond_one_copy": duplicate_file_count,
            "theoretical_max_saved_bytes": duplicate_saved,
            "groups": duplicate_groups,
            "note": "Savings assume one copy per identical SHA256 payload can be referenced by multiple paths; no deduplicated storage was created.",
        },
        "method": {
            "hash": "SHA256 per file, streamed in 1 MiB chunks",
            "gzip": "zlib gzip wrapper, level 9, mtime=0, streamed in memory; no compressed artifact persisted",
            "images": "All recognized image suffixes measured with gzip only; pixels were not re-encoded",
            "archive": "No tar.gz or ZIP was written",
            "limits": [
                "Gzip size is a transport/storage measurement and does not change the current HTTP serving behavior.",
                "Exact duplicate savings are theoretical unless a deployment layer implements content addressing or hard links.",
                "Git pack size reflects the current repository object store; no repack/prune was performed.",
            ],
        },
        "files": records,
    }


def write_report(report: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text = report["text_gzip_level9"]
    image = report["image_gzip_level9_probe"]
    dup = report["exact_duplicate_analysis"]
    lines = [
        "# Offline deployment compression analysis",
        "",
        f"Input: `{report['site_root']}` ({report['site_file_count']:,} files, {report['site_bytes']:,} bytes). Manifest SHA256: `{report['manifest']['sha256']}`; site inventory SHA256: `{report['site_inventory_sha256']}`.",
        "This is a read-only measurement. No site file, manifest, ZIP, compressed artifact, or serving behavior was changed.",
        "",
        "## Categories",
        "",
        "| Kind | Files | Raw bytes | Gzip-9 bytes | Delta |",
        "|---|---:|---:|---:|---:|",
    ]
    for kind, item in report["category_stats"].items():
        gz = item.get("gzip_bytes", "n/a")
        delta = item.get("gzip_savings_bytes", "n/a")
        lines.append(f"| {kind} | {item['files']:,} | {item['bytes']:,} | {gz if isinstance(gz, str) else f'{gz:,}'} | {delta if isinstance(delta, str) else f'{delta:,}'} |")
    lines.extend([
        "",
        "## Main measurements",
        "",
        f"- HTML/XML/JS/CSS/JSON gzip-9: {text['raw_bytes']:,} → {text['gzip_bytes']:,} bytes; theoretical reduction {text['savings_bytes']:,} bytes ({(1 - text['ratio']) * 100:.2f}% when nonzero).",
        f"- Images gzip-9 probe: {image['raw_bytes']:,} → {image['gzip_bytes']:,} bytes; delta {image['delta_bytes']:+,} bytes. Images were not re-encoded and no output was saved.",
        f"- Exact SHA256 duplicates: {dup['duplicate_group_count']:,} groups; retaining one payload per group could save at most {dup['theoretical_max_saved_bytes']:,} bytes across {dup['duplicate_file_count_beyond_one_copy']:,} duplicate paths.",
        f"- Git object pack files: {report['git']['pack_file_bytes']:,} bytes; HEAD site tree reports {report['git']['head_site_bytes']:,} bytes. No repack/prune/delete was run.",
        "",
        "## Recommendation",
        "",
        "The current Git object store already uses zlib compression and content-addressed objects. Static text gzip can materially reduce transfer size, but it requires an explicit serving/deployment decision and is not enabled by this measurement. Exact duplicate savings are a storage optimization opportunity only if the deployment layer supports shared payloads; the current site keeps separate paths. Images should remain in their original lossless/lossy encoding because gzip is not an image re-encoder and the probe measures little or negative benefit.",
        "",
        "The JSON contains every file's relative path, kind, raw byte length, SHA256 and measured gzip size where applicable, plus duplicate groups and Git/manifest provenance.",
    ])
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = compression_report()
    write_report(report)
    print(json.dumps({
        "json": str(JSON_OUT.relative_to(ROOT)).replace("\\", "/"),
        "markdown": str(MD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "files": report["site_file_count"],
        "site_bytes": report["site_bytes"],
        "text_raw_bytes": report["text_gzip_level9"]["raw_bytes"],
        "text_gzip_bytes": report["text_gzip_level9"]["gzip_bytes"],
        "image_raw_bytes": report["image_gzip_level9_probe"]["raw_bytes"],
        "image_gzip_bytes": report["image_gzip_level9_probe"]["gzip_bytes"],
        "duplicate_groups": report["exact_duplicate_analysis"]["duplicate_group_count"],
        "duplicate_saved_bytes": report["exact_duplicate_analysis"]["theoretical_max_saved_bytes"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

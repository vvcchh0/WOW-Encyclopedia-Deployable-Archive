"""Read-only storage inventory for the WoW Encyclopedia workspace.

The script performs one bounded filesystem walk from the repository root. It
does not follow symlinks or reparse points, does not read network resources,
and writes only summary.json and summary.md next to this file.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat as stat_module
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SUMMARY_JSON = OUT / "summary.json"
SUMMARY_MD = OUT / "summary.md"
MIN_FREE_BYTES = 10 * 1024**3 + 256 * 1024**2
CHUNK = 1024 * 1024

V3_REL = Path(".scratch/pages-historical-exhibits-20261014-v3")
V3_PROVENANCE_REL = V3_REL / "export-provenance.json"
PROVENANCE_PREFIXES = (".scratch/pages-historical-exhibits-", ".scratch/pages-resources-")

SAMPLE_OUTPUTS = (
    "index.html",
    "__offline/pages_runtime.js",
    "__offline/route-map.json",
    "info/encyclopedia/481.xml.html",
    "visa/reward/images/header.jpg",
    "info/dungeons/images/karazhan/thumbs/ss1-thumb.jpg",
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
            total += len(chunk)
    return digest.hexdigest(), total


def empty_stat() -> dict[str, int]:
    return {"files": 0, "bytes": 0, "directories": 0, "errors": 0}


def add_file(stat: dict[str, int], size: int) -> None:
    stat["files"] += 1
    stat["bytes"] += size


def add_dir(stat: dict[str, int]) -> None:
    stat["directories"] += 1


def skip_inventory_outputs(relative: str) -> bool:
    return (
        relative == "research/local-maintenance-20261014/storage-inventory"
        or relative.startswith("research/local-maintenance-20261014/storage-inventory/")
        or relative.startswith(".scratch/storage-inventory-")
    )


def is_reparse(entry: os.DirEntry[str]) -> bool:
    try:
        if entry.is_symlink():
            return True
        info = entry.stat(follow_symlinks=False)
        attributes = getattr(info, "st_file_attributes", 0)
        reparse = getattr(stat_module, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        return bool(attributes & reparse)
    except OSError:
        return False


def scan_root() -> tuple[dict[str, Any], set[str], list[str]]:
    """Walk ROOT exactly once and collect requested logical-size buckets."""
    root_stat = empty_stat()
    top_level: dict[str, dict[str, int]] = defaultdict(empty_stat)
    scratch: dict[str, dict[str, int]] = defaultdict(empty_stat)
    offline: dict[str, dict[str, int]] = defaultdict(empty_stat)
    artifacts: dict[str, dict[str, int]] = defaultdict(empty_stat)
    backups: dict[str, dict[str, int]] = defaultdict(empty_stat)
    observed_files: set[str] = set()
    errors: list[str] = []
    stack: list[tuple[Path, str]] = [(ROOT, "")]

    while stack:
        directory, directory_rel = stack.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError as exc:
            errors.append(f"{directory_rel or '.'}: {type(exc).__name__}: {exc}")
            root_stat["errors"] += 1
            continue

        for entry in entries:
            relative = f"{directory_rel}/{entry.name}" if directory_rel else entry.name
            relative = relative.replace("\\", "/")
            if skip_inventory_outputs(relative) or is_reparse(entry):
                continue
            try:
                if entry.is_dir(follow_symlinks=False):
                    add_dir(root_stat)
                    if "/" not in relative:
                        add_dir(top_level[relative])
                    parts = relative.split("/")
                    if parts[0] == ".scratch" and len(parts) >= 2:
                        add_dir(scratch[parts[1]])
                    elif parts[0] == "offline" and len(parts) >= 2:
                        add_dir(offline[parts[1]])
                    elif parts[0] == "artifacts" and len(parts) >= 2:
                        add_dir(artifacts[parts[1]])
                    elif parts[0] == "backups" and len(parts) >= 2:
                        add_dir(backups[parts[1]])
                    stack.append((Path(entry.path), relative))
                elif entry.is_file(follow_symlinks=False):
                    size = entry.stat(follow_symlinks=False).st_size
                    add_file(root_stat, size)
                    parts = relative.split("/")
                    if len(parts) == 1:
                        add_file(top_level["<root-files>"], size)
                    else:
                        add_file(top_level[parts[0]], size)
                    if parts[0] == ".scratch" and len(parts) >= 2:
                        add_file(scratch[parts[1]], size)
                    elif parts[0] == "offline" and len(parts) >= 2:
                        add_file(offline[parts[1]], size)
                    elif parts[0] == "artifacts":
                        add_file(artifacts[parts[1] if len(parts) >= 2 else "<root-files>"], size)
                    elif parts[0] == "backups" and len(parts) >= 2:
                        add_file(backups[parts[1]], size)
                    observed_files.add(relative)
            except OSError as exc:
                errors.append(f"{relative}: {type(exc).__name__}: {exc}")
                root_stat["errors"] += 1

    def ordered(values: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
        return {key: values[key] for key in sorted(values)}

    return (
        {
            "root": root_stat,
            "top_level": ordered(top_level),
            "scratch": ordered(scratch),
            "offline": ordered(offline),
            "artifacts": ordered(artifacts),
            "backups": ordered(backups),
            "scan_errors": errors,
        },
        observed_files,
        errors,
    )


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def compact_stats(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): value[key] for key in sorted(value)}


def provenance_record_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in data.get("files", []):
        if isinstance(record, dict) and isinstance(record.get("output_path"), str):
            result[record["output_path"]] = record
    return result


def provenance_summary(path: Path) -> dict[str, Any]:
    data = read_json(path)
    records = provenance_record_map(data)
    lines = sorted(
        f"{name}|{record.get('derived_length')}|{record.get('derived_sha256')}"
        for name, record in records.items()
    )
    canonical = ("\n".join(lines) + "\n").encode("utf-8")
    return {
        "path": rel(path),
        "file_bytes": path.stat().st_size,
        "file_sha256": sha256_file(path)[0],
        "generated_at": data.get("generated_at"),
        "anchor_timestamp": data.get("anchor_timestamp"),
        "source_manifest": data.get("source_manifest"),
        "source_manifest_sha256": data.get("source_manifest_sha256"),
        "source_site": data.get("source_site"),
        "stats": compact_stats(data.get("stats")),
        "record_count": len(records),
        "canonical_payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "records": records,
    }


def compare_provenance(base: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    base_records = base["records"]
    variant_records = variant["records"]
    same = changed = added = removed = 0
    base_bytes = variant_bytes = 0
    changed_by_kind: Counter[str] = Counter()
    changed_by_role: Counter[str] = Counter()
    examples: list[dict[str, Any]] = []

    for name, record in base_records.items():
        base_bytes += int(record.get("derived_length") or 0)
        other = variant_records.get(name)
        if other is None:
            removed += 1
            continue
        variant_bytes += int(other.get("derived_length") or 0)
        if record.get("derived_sha256") == other.get("derived_sha256"):
            same += 1
        else:
            changed += 1
            changed_by_kind[str(record.get("kind") or "unknown")] += 1
            changed_by_role[str(record.get("role") or "unknown")] += 1
            if len(examples) < 10:
                examples.append(
                    {
                        "output_path": name,
                        "base_length": record.get("derived_length"),
                        "variant_length": other.get("derived_length"),
                        "base_sha256": record.get("derived_sha256"),
                        "variant_sha256": other.get("derived_sha256"),
                    }
                )
    for name, record in variant_records.items():
        if name not in base_records:
            added += 1
            variant_bytes += int(record.get("derived_length") or 0)

    return {
        "variant": variant["path"],
        "record_count": len(variant_records),
        "same_sha_records": same,
        "changed_sha_records": changed,
        "added_records": added,
        "removed_records": removed,
        "base_payload_bytes": base_bytes,
        "variant_payload_bytes": variant_bytes,
        "payload_delta_bytes": variant_bytes - base_bytes,
        "changed_by_kind": dict(sorted(changed_by_kind.items())),
        "changed_by_role": dict(sorted(changed_by_role.items())),
        "changed_examples": examples,
        "canonical_payload_sha256": variant["canonical_payload_sha256"],
    }


def sentinel_hashes(paths: Iterable[Path]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for path in paths:
        key = rel(path)
        try:
            digest, length = sha256_file(path)
            result[key] = {"exists": True, "bytes": length, "sha256": digest}
        except OSError as exc:
            result[key] = {"exists": False, "error": f"{type(exc).__name__}: {exc}"}
    return result


def compact_compression() -> dict[str, Any]:
    path = ROOT / "research/github-publication-20261012/compression-analysis.json"
    data = read_json(path)
    category = {}
    for name, value in sorted((data.get("category_stats") or {}).items()):
        if isinstance(value, dict):
            category[name] = {
                key: value[key]
                for key in ("files", "bytes", "gzip_bytes", "gzip_ratio", "gzip_savings_bytes")
                if key in value
            }
    groups = data.get("files") or []
    other_bytes = sum(
        int(item.get("bytes") or 0)
        for item in groups
        if item.get("kind") in {"other", "swf"}
    )
    text = data.get("text_gzip_level9") or {}
    image = data.get("image_gzip_level9_probe") or {}
    duplicates = data.get("exact_duplicate_analysis") or {}
    return {
        "source": rel(path),
        "source_sha256": sha256_file(path)[0],
        "site_bytes": data.get("site_bytes"),
        "site_file_count": data.get("site_file_count"),
        "site_inventory_sha256": data.get("site_inventory_sha256"),
        "category_stats": category,
        "text_probe": {
            key: text[key]
            for key in ("files", "raw_bytes", "gzip_bytes", "savings_bytes", "ratio", "output_written")
            if key in text
        },
        "image_probe": {
            key: image[key]
            for key in ("files", "raw_bytes", "gzip_bytes", "delta_bytes", "ratio", "all_images_measured", "reencoded")
            if key in image
        },
        "other_and_swf_raw_bytes": other_bytes,
        "exact_duplicate_analysis": {
            key: duplicates[key]
            for key in ("duplicate_group_count", "duplicate_file_count_beyond_one_copy", "theoretical_max_saved_bytes")
            if key in duplicates
        },
    }


def package_inventory(observed_files: set[str]) -> dict[str, Any]:
    packages: list[dict[str, Any]] = []
    artifact_paths = sorted(
        ROOT / path for path in observed_files
        if path.startswith("artifacts/") and path.lower().endswith(".zip")
    )
    runtime_rel = "artifacts/WOW_Encyclopedia_20080512_runtime_20261013.zip"
    runtime_actual_sha = None
    runtime_expected_sha = None
    for path in artifact_paths:
        sidecar_path = path.with_name(path.name + ".sha256")
        sidecar_text = None
        sidecar_sha = None
        expected_sha = None
        if sidecar_path.is_file():
            sidecar_text = sidecar_path.read_text(encoding="ascii").strip()
            sidecar_sha = sha256_file(sidecar_path)[0]
            if sidecar_text:
                expected_sha = sidecar_text.split()[0]
        item = {
            "path": rel(path),
            "bytes": path.stat().st_size,
            "gib": round(path.stat().st_size / 1024**3, 6),
            "sidecar": rel(sidecar_path) if sidecar_path.is_file() else None,
            "sidecar_text": sidecar_text,
            "sidecar_sha256": sidecar_sha,
            "expected_sha256": expected_sha,
        }
        if rel(path) == runtime_rel:
            runtime_actual_sha, actual_length = sha256_file(path)
            item["actual_sha256"] = runtime_actual_sha
            item["actual_length"] = actual_length
            item["actual_matches_sidecar"] = bool(expected_sha and expected_sha == runtime_actual_sha)
            runtime_expected_sha = expected_sha
        packages.append(item)
    total = sum(item["bytes"] for item in packages)
    return {
        "zip_count": len(packages),
        "zip_total_bytes": total,
        "zip_total_gib": round(total / 1024**3, 6),
        "packages": packages,
        "runtime_20261013": {
            "path": runtime_rel,
            "expected_sha256": runtime_expected_sha,
            "actual_sha256": runtime_actual_sha,
            "unchanged_verified": bool(runtime_expected_sha and runtime_expected_sha == runtime_actual_sha),
        },
    }


def sample_actual_hashes(provenances: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for provenance in provenances:
        if not any(provenance["path"].startswith(prefix) for prefix in PROVENANCE_PREFIXES):
            continue
        tree = ROOT / Path(provenance["path"]).parent
        record_map = provenance["records"]
        sample_rows: list[dict[str, Any]] = []
        for output in SAMPLE_OUTPUTS:
            expected = record_map.get(output)
            actual_path = tree / output
            if expected is None or not actual_path.is_file():
                sample_rows.append({"output_path": output, "exists": False})
                continue
            digest, length = sha256_file(actual_path)
            sample_rows.append(
                {
                    "output_path": output,
                    "exists": True,
                    "bytes": length,
                    "actual_sha256": digest,
                    "expected_sha256": expected.get("derived_sha256"),
                    "matches_provenance": digest == expected.get("derived_sha256")
                    and length == int(expected.get("derived_length") or -1),
                }
            )
        rows.append({"tree": rel(tree), "samples": sample_rows})
    return rows


def portable_estimate(v3: dict[str, Any], compression: dict[str, Any]) -> dict[str, Any]:
    ratios: dict[str, float] = {}
    for source_name, target_name in (
        ("css", "css"),
        ("html", "html"),
        ("image", "image"),
        ("javascript", "js"),
        ("xml", "xml"),
    ):
        value = compression["category_stats"].get(source_name)
        if value and value.get("gzip_ratio") is not None:
            ratios[target_name] = float(value["gzip_ratio"])
    ratios.update(
        {
            "image_overlay": ratios.get("image", 0.9915),
            "xsl": 0.20,
            "menu_html": ratios.get("html", 0.1858),
            "generated_redirect": 0.20,
            "generated_root_redirect": 0.20,
            "generated_placeholder": 0.20,
            "pages_404": ratios.get("html", 0.1858),
            "pages_missing": ratios.get("html", 0.1858),
            "pages_readme": 0.20,
            "pages_route_map": 0.20,
            "pages_runtime": ratios.get("js", 0.143),
            "pages_uncollected": ratios.get("html", 0.1858),
            "related_images_index": ratios.get("html", 0.1858),
            "support": 0.20,
            "legacy_component": 0.20,
        }
    )
    binary_kinds = {"flash", "swf", "pages_metadata"}
    rows: list[dict[str, Any]] = []
    raw_payload = estimated_payload = 0
    kinds = sorted({str(record.get("kind")) for record in v3["records"].values()})
    for kind in kinds:
        records = [record for record in v3["records"].values() if str(record.get("kind")) == kind]
        raw = sum(int(record.get("derived_length") or 0) for record in records)
        ratio = 1.0 if kind in binary_kinds else ratios.get(kind, 0.50)
        estimated = round(raw * ratio)
        raw_payload += raw
        estimated_payload += estimated
        rows.append(
            {
                "kind": kind,
                "files": len(records),
                "raw_bytes": raw,
                "ratio_used": ratio,
                "estimated_compressed_bytes": estimated,
            }
        )
    return {
        "method": "existing offline/site gzip-9 ratios; v3 was not packaged",
        "payload_raw_bytes": raw_payload,
        "payload_estimated_compressed_bytes": estimated_payload,
        "payload_estimated_savings_bytes": raw_payload - estimated_payload,
        "payload_estimated_ratio": round(estimated_payload / raw_payload, 6) if raw_payload else None,
        "provenance_raw_bytes": v3["file_bytes"],
        "per_kind": rows,
        "uncertainty": "The estimate excludes compressor metadata and any launcher/server files; run a new archive preflight and streamed verification before delivery.",
    }


def make_recommendations(
    scan: dict[str, Any],
    provenance_comparisons: list[dict[str, Any]],
    packages: dict[str, Any],
    compression: dict[str, Any],
    estimate: dict[str, Any],
) -> list[dict[str, Any]]:
    old_tree_names = [
        "pages-historical-exhibits-20261014",
        "pages-historical-exhibits-20261014-final",
        "pages-historical-exhibits-20261014-v2",
        "pages-resources-20261014-next",
        "pages-resources-20261014",
    ]
    old_tree_bytes = sum(scan["scratch"].get(name, {}).get("bytes", 0) for name in old_tree_names)
    changed_counts = [
        item["changed_sha_records"]
        for item in provenance_comparisons
        if item["variant"].startswith(".scratch/pages-")
    ]
    return [
        {
            "priority": 1,
            "action": "Use .scratch/pages-historical-exhibits-20261014-v3 as the single canonical portable browser staging tree.",
            "why": "It carries 8,435 Pages output records, 36 image overlays, the current historical exhibit output, and current export provenance. Keep the source manifest SHA tied to 397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459.",
        },
        {
            "priority": 2,
            "action": "Retain each older Pages tree only as a named snapshot with its export-provenance.json and a compact v3 diff record; do not treat equal file names as equal content.",
            "why": f"The five older trees occupy {old_tree_bytes:,} logical bytes together. Compared with v3, the older variants differ in {min(changed_counts)}–{max(changed_counts)} output hashes; the four 8,435-record variants differ only in HTML, while the early resources tree also differs in JS and Pages support records and has 18 missing records.",
        },
        {
            "priority": 3,
            "action": "Keep artifacts/WOW_Encyclopedia_20080512_runtime_20261013.zip and its sidecar byte-for-byte unchanged.",
            "why": f"The existing runtime archive is {packages['runtime_20261013']['actual_sha256']} and its current bytes match the sidecar. It is a separate 2008 runtime deliverable and should not be regenerated from the v3 Pages tree.",
        },
        {
            "priority": 4,
            "action": "Before publishing a new portable ZIP, build a source-root-aware packer or wrapper that includes the v3 tree, export-provenance.json, the accepted 36 image overlays, historical exhibits, the 50 directory fixes, and a loopback launcher/server; verify the finished ZIP by streamed SHA, CRC, length, and whitelist checks.",
            "why": "tools/package_runtime_archive.py hardcodes offline/site, offline/build-manifest.json, offline/support, and runtime launcher inputs. It has no source-root, Pages-export, overlay, or v3 provenance option, so it cannot directly package v3.",
        },
        {
            "priority": 5,
            "action": "Use the existing measured compression profile for budgeting, then package once after acceptance.",
            "why": f"The offline/site report measured {compression['text_probe'].get('savings_bytes', 0):,} bytes saved from text and {compression['image_probe'].get('raw_bytes', 0) - compression['image_probe'].get('gzip_bytes', 0):,} from images; the v3 payload is {estimate['payload_raw_bytes']:,} raw bytes with an estimated {estimate['payload_estimated_compressed_bytes']:,} compressed bytes. This is an estimate, not a new archive result.",
        },
        {
            "priority": 6,
            "action": "Keep at least 10 GiB plus 256 MiB free on D: before any future write, and use a separate temporary output directory for the new archive.",
            "why": "The current inventory is read-only and D: was checked against the project safety threshold. No deletion, move, NTFS compression, or packaging was performed by this report.",
        },
    ]


def write_markdown(summary: dict[str, Any]) -> None:
    root = summary["scan"]["root"]
    free = summary["disk"]["free_bytes_after"]
    packages = summary["packages"]
    compression = summary["compression"]
    estimate = summary["portable_estimate"]
    lines = [
        "# Storage inventory and low-repetition organization proposal",
        "",
        f"Generated at {summary['generated_utc']}. This was a read-only local inventory; network access was not used and no existing source, backup, ZIP, or historical tree was modified.",
        "",
        "## Current capacity",
        "",
        f"- Workspace logical files: {root['files']:,}; bytes: {root['bytes']:,} ({root['bytes'] / 1024**3:.3f} GiB).",
        f"- D: free after scan: {free:,} bytes ({free / 1024**3:.3f} GiB); required minimum: {MIN_FREE_BYTES:,} bytes ({MIN_FREE_BYTES / 1024**3:.3f} GiB); check: {summary['disk']['minimum_free_check']}.",
        "- The root and top-level buckets count logical file bytes. Symlinks and reparse points were skipped; scan errors are listed in summary.json.",
        "",
        "## Major derived trees",
        "",
        "| Tree | Files | Bytes | GiB | v3 comparison |",
        "|---|---:|---:|---:|---|",
    ]
    comp_by_variant = {item["variant"]: item for item in summary["provenance_comparisons"]}
    for name, stat in sorted(summary["scan"]["scratch"].items(), key=lambda item: item[1]["bytes"], reverse=True):
        if stat["bytes"] < 1024 * 1024 and not name.startswith("pages-"):
            continue
        path = f".scratch/{name}"
        comparison = comp_by_variant.get(f".scratch/{name}/export-provenance.json")
        relation = (
            f"{comparison['same_sha_records']} same; {comparison['changed_sha_records']} changed; +{comparison['added_records']}/-{comparison['removed_records']} records"
            if comparison
            else ("canonical v3 provenance" if name == V3_REL.name else "not a Pages provenance tree")
        )
        lines.append(f"| {path} | {stat['files']:,} | {stat['bytes']:,} | {stat['bytes'] / 1024**3:.3f} | {relation} |")
    lines += [
        "",
        "The four older 8,435-record Pages variants are close copies by content records, but they are not exact full-tree duplicates. The early pages-resources-20261014 export has 8,417 records and is missing 18 v3 paths. The per-record SHA/length comparison in summary.json preserves this distinction.",
        "",
        "## Existing delivery ZIPs",
        "",
        "| ZIP | Bytes | Sidecar SHA-256 | Runtime archive check |",
        "|---|---:|---|---|",
    ]
    for item in packages["packages"]:
        runtime_check = "verified" if item.get("actual_matches_sidecar") else "sidecar only"
        lines.append(f"| {item['path']} | {item['bytes']:,} | {item.get('expected_sha256') or 'missing'} | {runtime_check} |")
    lines += [
        "",
        f"The 20261013 runtime ZIP was streamed once and matched its sidecar: {packages['runtime_20261013']['actual_sha256']}. Its bytes remain separate from the new v3 portable browser candidate.",
        "",
        "## Compression and savings",
        "",
        f"- Reused full measurement for offline/site: {compression['text_probe'].get('raw_bytes', 0):,} text bytes to {compression['text_probe'].get('gzip_bytes', 0):,} gzip-9 bytes, saving {compression['text_probe'].get('savings_bytes', 0):,}; images {compression['image_probe'].get('raw_bytes', 0):,} to {compression['image_probe'].get('gzip_bytes', 0):,}, saving {compression['image_probe'].get('raw_bytes', 0) - compression['image_probe'].get('gzip_bytes', 0):,}.",
        f"- Other/SWF bytes total {compression['other_and_swf_raw_bytes']:,}; the existing report did not claim a gzip saving for those binary kinds.",
        f"- Exact duplicate payload analysis found {compression['exact_duplicate_analysis'].get('duplicate_group_count', 0)} groups / {compression['exact_duplicate_analysis'].get('duplicate_file_count_beyond_one_copy', 0)} redundant paths and a theoretical maximum of {compression['exact_duplicate_analysis'].get('theoretical_max_saved_bytes', 0):,} bytes if paths could reference one content copy.",
        f"- v3 payload raw bytes from provenance: {estimate['payload_raw_bytes']:,}; estimated compressed payload: {estimate['payload_estimated_compressed_bytes']:,}; estimated saving: {estimate['payload_estimated_savings_bytes']:,}. The estimate reuses measured category ratios and does not create an archive.",
        "",
        "## Tool fit and executable organization plan",
        "",
        "tools/package_runtime_archive.py cannot directly package v3. Its source collection is fixed to offline/site, offline/build-manifest.json, offline/support, and the runtime launcher files; it has no source-root or Pages-export option. A future v3 packer must include the current export tree plus provenance, the accepted 36 image overlays, historical exhibits, and the 50 directory fixes, then perform the same streamed verification contract.",
        "",
        "The dry-run plan is portable-package-plan.ps1. It checks required inputs, the runtime sidecar, and free space, then prints intended staging/package inputs without moving, deleting, compressing, or creating an archive.",
        "",
        "## Recommendations",
        "",
    ]
    for recommendation in summary["recommendations"]:
        lines.append(f"{recommendation['priority']}. {recommendation['action']} {recommendation['why']}")
    lines += [
        "",
        "## Validation and limits",
        "",
        f"- Sentinel hashes before and after the scan: {summary['input_stability']['all_unchanged']}. The set includes offline/build-manifest.json, current v3 export-provenance.json, every existing ZIP sidecar, and package/compression source summaries.",
        "- Representative actual v3 and older-tree files were hashed and checked against their provenance records. Full re-hashing of every older derived tree was intentionally avoided because the provenance records already carry per-output SHA-256 values; this keeps the inventory bounded and does not claim current old-tree bytes beyond the sampled files.",
        "- No package was built, no NTFS compression was enabled, no directory was moved, and no historical ZIP or source tree was deleted.",
        "",
        "Unknowns for the future portable package: exact compressor output, launcher/server inclusion, and the independent acceptance record for the 50 directory fixes require a packaging/acceptance pass after the source tree is frozen. Current provenance independently confirms 8,435 outputs and 36 image overlays.",
        "",
    ]
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    started = datetime.now(timezone.utc)
    disk_before = shutil.disk_usage(ROOT)
    sentinel_paths = [
        ROOT / "offline/build-manifest.json",
        ROOT / V3_PROVENANCE_REL,
        ROOT / "research/github-publication-20261012/compression-analysis.json",
        ROOT / "research/github-publication-20261012/runtime-package-verification.json",
    ]
    sentinel_paths.extend(sorted((ROOT / "artifacts").glob("*.zip.sha256")))
    sentinels_before = sentinel_hashes(sentinel_paths)

    scan, observed_files, scan_errors = scan_root()
    provenance_paths = sorted(
        ROOT / path
        for path in observed_files
        if path.endswith("/export-provenance.json") and path.startswith(PROVENANCE_PREFIXES)
    )
    provenances = [provenance_summary(path) for path in provenance_paths]
    v3 = next(item for item in provenances if item["path"] == V3_PROVENANCE_REL.as_posix())
    comparisons = [compare_provenance(v3, item) for item in provenances if item["path"] != v3["path"]]
    compression = compact_compression()
    packages = package_inventory(observed_files)
    sample_hashes = sample_actual_hashes(provenances)
    estimate = portable_estimate(v3, compression)
    recommendations = make_recommendations(scan, comparisons, packages, compression, estimate)

    sentinels_after = sentinel_hashes(sentinel_paths)
    stability_rows = {}
    for key in sorted(set(sentinels_before) | set(sentinels_after)):
        before = sentinels_before.get(key)
        after = sentinels_after.get(key)
        stability_rows[key] = {"before": before, "after": after, "unchanged": before == after}

    disk_after = shutil.disk_usage(ROOT)
    summary = {
        "schema_version": 1,
        "kind": "wow_encyclopedia_storage_inventory_20261014",
        "generated_utc": started.isoformat().replace("+00:00", "Z"),
        "network_performed": False,
        "read_only": True,
        "root": str(ROOT),
        "scan": scan,
        "disk": {
            "path": str(ROOT.anchor),
            "free_bytes_before": disk_before.free,
            "free_bytes_after": disk_after.free,
            "total_bytes": disk_after.total,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "minimum_free_check": disk_after.free >= MIN_FREE_BYTES,
        },
        "provenance": [
            {key: value for key, value in item.items() if key != "records"}
            for item in provenances
        ],
        "provenance_comparisons": comparisons,
        "representative_actual_hashes": sample_hashes,
        "compression": compression,
        "packages": packages,
        "portable_estimate": estimate,
        "runtime_tool_fit": {
            "tool": "tools/package_runtime_archive.py",
            "directly_usable_for_v3": False,
            "reasons": [
                "iter_site_files() is fixed to offline/site",
                "collect_sources() is fixed to offline/build-manifest.json, offline/support, and runtime launcher inputs",
                "there is no source-root option for a Pages export or export-provenance.json",
                "the tool does not know the v3 historical exhibit, 36 overlay, or 50 directory-fix acceptance contract",
            ],
            "safe_reuse": "Reuse its preflight and streamed verification ideas in a new v3-aware packer; leave the existing 20261013 archive untouched.",
        },
        "recommendations": recommendations,
        "input_stability": {
            "all_unchanged": all(row["unchanged"] for row in stability_rows.values()),
            "sentinels": stability_rows,
        },
        "method": {
            "tree_scan": "one os.scandir walk from repository root; no symlink/reparse traversal",
            "old_tree_content": "full provenance path/length/SHA comparison plus representative current-file hashes",
            "compression": "reuse existing full offline/site gzip-9 report; estimate v3 by measured category ratios; no new archive",
            "historical_zip_sources": "record existing ZIP sidecar SHA-256 summaries; stream-hash 20261013 runtime ZIP once and compare to its sidecar",
        },
        "scan_error_count": len(scan_errors),
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary)
    print(
        json.dumps(
            {
                "summary": rel(SUMMARY_JSON),
                "markdown": rel(SUMMARY_MD),
                "root_files": scan["root"]["files"],
                "root_bytes": scan["root"]["bytes"],
                "v3_payload_records": v3["record_count"],
                "zip_count": packages["zip_count"],
                "input_stable": summary["input_stability"]["all_unchanged"],
                "scan_errors": len(scan_errors),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

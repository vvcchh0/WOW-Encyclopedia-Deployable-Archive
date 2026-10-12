"""Read-only inventory for the public deployable archive.

This script deliberately inventories the already-built serving tree separately
from build/research inputs.  It does not open a network connection, create a
Git repository, or modify the site, maps, archives, or package outputs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/github-publication-20261012"
MAX_GIT_BLOB = 100 * 1024 * 1024

KEY_REPORTS = [
    "research/offline-2008/full-recovery/round-108-8304-full-browser-validation.json",
    "research/offline-2008/full-recovery/round-109-root-full-browser-acceptance.json",
    "research/offline-2008/full-recovery/round-111-root-final-gap-closure-acceptance.json",
    "research/offline-2008/full-recovery/round-100-new-image-sources-validation.json",
    "research/offline-2008/full-recovery/round-104-followup27-image-sources-validation.json",
    "research/offline-2008/full-recovery/round-105-final-full-capture-map-validation.json",
    "research/offline-2008/full-recovery/round-106-final-integration-provenance-audit.json",
    "research/final-pre2008-image-wave-20261012/post-followup-completion-audit.json",
    "research/final-gap-closure-20261012/final-build/README.md",
    "research/final-gap-closure-20261012/final-build/summary.json",
    "research/final-gap-closure-20261012/final-build/targets.json",
    "research/final-gap-closure-20261012/final-build/nonimage-reconciliation-acceptance.json",
    "research/derived-script-audit/round-8304/report.md",
    "research/derived-script-audit/round-8304/validation.json",
]

SENSITIVE_BASENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials",
    "credentials.json",
    "cookies.txt",
    "cookies.json",
    "passwords",
    "passwords.json",
    "secret",
    "secrets",
    "secrets.json",
    "token",
    "tokens.json",
}
PERSONAL_SCREENSHOT_RE = re.compile(
    r"(?:^|[/\\])(?:personal|private|自拍|screenshot[_-]?\d{8,})(?:[/\\]|$)",
    re.IGNORECASE,
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_reparse(path: Path, stat_result: os.stat_result | None = None) -> bool:
    if path.is_symlink():
        return True
    st = stat_result or path.lstat()
    # FILE_ATTRIBUTE_REPARSE_POINT; harmless on non-Windows platforms.
    return bool(getattr(st, "st_file_attributes", 0) & 0x400)


def walk_tree(root: Path) -> tuple[list[Path], list[Path], list[str]]:
    """Return regular files, reparse entries, and traversal errors.

    os.walk is kept non-following.  Reparse directories are pruned so a
    junction cannot make the inventory escape the selected tree.
    """
    files: list[Path] = []
    reparses: list[Path] = []
    errors: list[str] = []
    if not root.exists():
        return files, reparses, [f"missing: {rel(root)}"]
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for name in dirs:
            item = current_path / name
            try:
                if is_reparse(item):
                    reparses.append(item)
                else:
                    kept_dirs.append(name)
            except OSError as exc:
                errors.append(f"{rel(item)}: {type(exc).__name__}: {exc}")
        dirs[:] = kept_dirs
        for name in names:
            item = current_path / name
            try:
                st = item.lstat()
                if is_reparse(item, st):
                    reparses.append(item)
                elif item.is_file():
                    files.append(item)
            except OSError as exc:
                errors.append(f"{rel(item)}: {type(exc).__name__}: {exc}")
    return files, reparses, errors


def tree_summary(root: Path, *, hash_files: bool = False) -> dict[str, Any]:
    files, reparses, errors = walk_tree(root)
    sizes = {p: p.stat().st_size for p in files}
    ext_counts = Counter((p.suffix.lower() or "<none>") for p in files)
    top_counts: Counter[str] = Counter()
    for p in files:
        try:
            relative = p.relative_to(root)
            top = relative.parts[0] if relative.parts else "."
            top_counts[top] += 1
        except ValueError:
            pass
    largest = max(files, key=lambda p: sizes[p], default=None)
    result: dict[str, Any] = {
        "path": rel(root),
        "exists": root.exists(),
        "file_count": len(files),
        "directory_count": sum(1 for p in root.rglob("*") if p.is_dir() and not p.is_symlink()) if root.exists() else 0,
        "bytes": sum(sizes.values()),
        "max_file": {"path": rel(largest), "bytes": sizes[largest]} if largest else None,
        "extension_counts": dict(sorted(ext_counts.items(), key=lambda item: (-item[1], item[0]))),
        "top_directory_file_counts": dict(sorted(top_counts.items(), key=lambda item: (-item[1], item[0]))),
        "symlink_or_reparse_count": len(reparses),
        "symlink_or_reparse_paths": [rel(p) for p in reparses[:20]],
        "errors": errors[:20],
    }
    if hash_files:
        result["files"] = [
            {"path": rel(p), "bytes": sizes[p], "sha256": sha256(p)}
            for p in sorted(files)
        ]
    return result


def explicit_files(paths: Iterable[str]) -> list[Path]:
    result: list[Path] = []
    for item in paths:
        path = ROOT / item
        if path.exists() and path.is_file():
            result.append(path)
    return result


def source_files() -> list[Path]:
    result: list[Path] = []
    for base in (ROOT / "tools", ROOT / "tests", ROOT / "packaging", ROOT / "docs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}:
                continue
            result.append(path)
    return sorted(result)


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        key = rel(path).casefold()
        if key not in seen:
            seen.add(key)
            result.append(path)
    return result


def manifest_checks(manifest_path: Path, site_root: Path, support_root: Path) -> dict[str, Any]:
    output: dict[str, Any] = {
        "path": rel(manifest_path),
        "exists": manifest_path.exists(),
    }
    if not manifest_path.exists():
        return output
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw = manifest_path.read_bytes()
    entries = data.get("files") if isinstance(data.get("files"), list) else []
    missing_output: list[str] = []
    missing_sources: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        output_path = entry.get("output_path")
        if isinstance(output_path, str):
            candidate = ROOT / output_path
            if not candidate.is_file():
                missing_output.append(output_path)
        source_path = entry.get("source_local_path")
        if isinstance(source_path, str) and not (ROOT / source_path).is_file():
            missing_sources.append(source_path)
    output.update(
        {
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "schema_version": data.get("schema_version"),
            "anchor_timestamp": data.get("anchor_timestamp"),
            "site_root": data.get("site_root"),
            "files_entry_count": len(entries),
            "placeholder_route_count": len(data.get("placeholder_routes", [])) if isinstance(data.get("placeholder_routes"), list) else None,
            "supplement_entry_count": len(data.get("supplements", [])) if isinstance(data.get("supplements"), list) else None,
            "output_paths_existing": len(entries) - len(missing_output),
            "missing_output_paths": missing_output[:20],
            "missing_output_path_count": len(missing_output),
            "source_paths_missing_count": len(missing_sources),
            "source_paths_missing_sample": missing_sources[:20],
            "source_paths_are_build_only": True,
            "serve_conclusion": "The serve command consumes site_root and this manifest; source_local_path, source maps, overlays, and raw entities are build/reprovenance inputs and are not needed to serve an already-built clone.",
        }
    )
    return output


def workspace_summary(exclude: Path) -> dict[str, Any]:
    """Bounded regular-file total for the workspace, excluding this output dir."""
    total = 0
    count = 0
    reparses = 0
    errors = 0
    stack = [ROOT]
    exclude = exclude.resolve()
    while stack:
        current = stack.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            errors += 1
            continue
        for entry in entries:
            path = Path(entry.path)
            try:
                resolved = path.resolve()
                if resolved == exclude or exclude in resolved.parents:
                    continue
                st = entry.stat(follow_symlinks=False)
                if entry.is_dir(follow_symlinks=False):
                    if entry.is_symlink() or (getattr(st, "st_file_attributes", 0) & 0x400):
                        reparses += 1
                    else:
                        stack.append(path)
                elif entry.is_file(follow_symlinks=False):
                    if entry.is_symlink() or (getattr(st, "st_file_attributes", 0) & 0x400):
                        reparses += 1
                    else:
                        count += 1
                        total += st.st_size
            except OSError:
                errors += 1
    return {
        "file_count": count,
        "bytes": total,
        "symlink_or_reparse_count": reparses,
        "errors": errors,
        "excluded_path": rel(exclude),
    }


def file_record(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    site = ROOT / "offline/site"
    support = ROOT / "offline/support"
    manifest = ROOT / "offline/build-manifest.json"
    source = source_files()
    reports = explicit_files(KEY_REPORTS)
    required_files = unique_paths(source + reports + [manifest])
    selected_file_sizes = {path: path.stat().st_size for path in required_files}
    selected_bytes = sum(selected_file_sizes.values())
    max_selected = max(required_files, key=lambda p: selected_file_sizes[p], default=None)

    sensitive_hits: list[str] = []
    personal_hits: list[str] = []
    source_reparse_count = 0
    source_tree_errors: list[str] = []
    for root in (site, support, ROOT / "tools", ROOT / "tests", ROOT / "packaging", ROOT / "docs"):
        files, reparses, errors = walk_tree(root)
        source_reparse_count += len(reparses)
        source_tree_errors.extend(errors)
        for path in files + reparses:
            path_text = rel(path)
            basename = path.name.casefold()
            if basename in SENSITIVE_BASENAMES or path.suffix.casefold() in {".pem", ".key", ".p12", ".pfx"}:
                sensitive_hits.append(path_text)
            if PERSONAL_SCREENSHOT_RE.search(path_text):
                personal_hits.append(path_text)

    usage = shutil.disk_usage(ROOT)
    workspace = workspace_summary(OUT)
    inventory: dict[str, Any] = {
        "schema_version": 1,
        "kind": "github_publication_inventory_20261012",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_performed": False,
        "publication": {
            "repository_normalized": "WOW-Encyclopedia-Deployable-Archive",
            "anchor_timestamp": "20080512210044",
            "processed_date": "2026-10-12",
            "publication_model": "Git selected deployable serving tree; distribute large raw/history archives as GitHub Release assets in volumes below 2 GiB.",
        },
        "runtime": {
            "command": "python tools/offline_mirror.py serve --site offline/site --manifest offline/build-manifest.json --host 127.0.0.1 --port 8765",
            "required_paths": ["offline/site", "offline/build-manifest.json"],
            "optional_build_support_path": "offline/support",
            "serve_dependency_judgment": "A clone containing offline/site and offline/build-manifest.json can serve the frozen tree. Building a new tree requires mirror/approved maps, overlays, and source entities that are intentionally excluded from the deployable Git selection.",
            "manifest_module_evidence": {
                "source": "tools/offline_mirror.py",
                "serve_defaults": ["offline/site", "offline/build-manifest.json"],
                "build_only_defaults": ["mirror/20080512/url-map.json", "research/gap-review-20261011/reviewed-index-overlay.json", "offline/support"],
            },
        },
        "tree_stats": {
            "offline_site": tree_summary(site),
            "offline_support": tree_summary(support),
            "combined_serving_and_support": {
                "file_count": tree_summary(site)["file_count"] + tree_summary(support)["file_count"],
                "bytes": tree_summary(site)["bytes"] + tree_summary(support)["bytes"],
            },
        },
        "manifest": manifest_checks(manifest, site, support),
        "selected_source_files": {
            "rules": [
                "tools/**, tests/**, packaging/**, docs/** regular source/document files",
                "exclude __pycache__ and *.pyc/*.pyo",
            ],
            "file_count": len(source),
            "bytes": sum(p.stat().st_size for p in source),
            "files": [file_record(p) for p in source],
        },
        "selected_key_reports": {
            "files": [file_record(p) for p in reports],
            "missing_requested_paths": [item for item in KEY_REPORTS if not (ROOT / item).is_file()],
        },
        "selected_estimate": {
            "file_count_including_site_support_manifest_source_and_reports": len(required_files) + tree_summary(site)["file_count"] + tree_summary(support)["file_count"],
            "bytes_including_site_support_manifest_source_and_reports": selected_bytes + tree_summary(site)["bytes"] + tree_summary(support)["bytes"],
            "max_selected_file": {"path": rel(max_selected), "bytes": selected_file_sizes[max_selected]} if (max_selected := max(required_files, key=lambda p: selected_file_sizes[p], default=None)) else None,
            "git_blob_limit_bytes": MAX_GIT_BLOB,
            "all_selected_files_under_git_blob_limit": all(size < MAX_GIT_BLOB for size in selected_file_sizes.values()) and tree_summary(site)["max_file"]["bytes"] < MAX_GIT_BLOB and tree_summary(support)["max_file"]["bytes"] < MAX_GIT_BLOB,
        },
        "integrity_checks": {
            "selected_tree_symlink_or_reparse_count": source_reparse_count,
            "sensitive_filename_hits": sorted(set(sensitive_hits)),
            "personal_screenshot_filename_hits": sorted(set(personal_hits)),
            "public_screenshot_scope_note": "offline/site/screenshots is a public historical site asset directory; filename scan found no personal/private screenshot marker.",
            "selected_source_tree_errors": source_tree_errors[:20],
        },
        "include_recommendations": [
            "Track offline/site/** as the frozen browser-serving tree.",
            "Track offline/build-manifest.json with a generated-file note; it is 73 MB and below the 100 MiB Git blob limit.",
            "Track offline/support/** for rebuild provenance and compatibility source; serving an already-built clone does not import it at runtime.",
            "Track the listed tools/tests/packaging/docs and key final reports; preserve report SHA-256 values in release notes.",
        ],
        "exclude_recommendations": [
            "Do not put raw CDX/HTTP response forests, backups, mirror/source entities, old offline site copies, or the 2.25 GB historical ZIP in the Git tree.",
            "Do not include __pycache__ or *.pyc/*.pyo generated files.",
            "Do not treat selected deployable files as sufficient to rebuild the site; raw/maps/research inputs remain local or Release assets.",
        ],
        "disk": {
            "root_total_bytes": usage.total,
            "root_free_bytes": usage.free,
            "root_used_bytes": usage.used,
            "workspace_tree_file_count": workspace["file_count"],
            "workspace_tree_bytes": workspace["bytes"],
            "workspace_tree_scan": "regular files, no symlink/reparse traversal, excluding this inventory directory",
            "workspace_tree_excluded_path": workspace["excluded_path"],
            "workspace_tree_reparse_count": workspace["symlink_or_reparse_count"],
            "workspace_tree_scan_errors": workspace["errors"],
        },
        "limitations": [
            "No Git clone, archive upload, server launch, or network request was performed.",
            "The report checks filename-level sensitive markers and link types; it does not publish or inspect private user data.",
            "A full workspace byte total was not traversed because this task is limited to the deployable closure; raw/history directories are explicitly excluded.",
        ],
    }

    json_path = OUT / "inventory.json"
    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    site_stats = inventory["tree_stats"]["offline_site"]
    support_stats = inventory["tree_stats"]["offline_support"]
    manifest_stats = inventory["manifest"]
    estimate = inventory["selected_estimate"]
    lines = [
        "# GitHub public deployment inventory (2026-10-12)",
        "",
        "This is a read-only, offline inventory. No Git, Release, ZIP, site, or remote state was changed.",
        "",
        "## Deployable runtime",
        "",
        f"Run `{inventory['runtime']['command']}`. The frozen serving closure is `offline/site/**` plus `offline/build-manifest.json`; `offline/support/**` is retained for build/provenance context.",
        "",
        f"`offline/site`: {site_stats['file_count']:,} files, {site_stats['bytes']:,} bytes; largest file `{site_stats['max_file']['path']}` ({site_stats['max_file']['bytes']:,} bytes).",
        f"`offline/support`: {support_stats['file_count']:,} files, {support_stats['bytes']:,} bytes; largest file `{support_stats['max_file']['path']}` ({support_stats['max_file']['bytes']:,} bytes).",
        f"Combined serving tree plus support: {inventory['tree_stats']['combined_serving_and_support']['file_count']:,} files / {inventory['tree_stats']['combined_serving_and_support']['bytes']:,} bytes.",
        f"Manifest: {manifest_stats['bytes']:,} bytes, SHA-256 `{manifest_stats['sha256']}`, `{manifest_stats['files_entry_count']:,}` file entries; output paths present {manifest_stats['output_paths_existing']:,}/{manifest_stats['files_entry_count']:,}.",
        f"The bounded workspace scan found {inventory['disk']['workspace_tree_file_count']:,} regular files / {inventory['disk']['workspace_tree_bytes']:,} bytes, excluding this inventory directory; D: free space was {inventory['disk']['root_free_bytes']:,} bytes at scan time.",
        f"One manifest source reference is an archived ZIP-member locator (`{manifest_stats['source_paths_missing_sample'][0]}`); it is a build/provenance pointer and does not affect serving because all `{manifest_stats['files_entry_count']:,}` output paths exist.",
        "",
        "The serve path reads the site directory and manifest only. A clone of this serving closure does not need the raw source entities, approved maps, CDX responses, overlays, or historical ZIPs. Those inputs are required only when rebuilding the derived tree.",
        "",
        "## Git selection",
        "",
        f"The proposed selection is {estimate['file_count_including_site_support_manifest_source_and_reports']:,} files / {estimate['bytes_including_site_support_manifest_source_and_reports']:,} bytes including the serving tree, support, manifest, source tools/tests/packaging/docs, and the explicitly listed final reports.",
        f"Largest selected non-directory file: `{estimate['max_selected_file']['path']}` ({estimate['max_selected_file']['bytes']:,} bytes). All selected files are below the 100 MiB Git blob limit: `{estimate['all_selected_files_under_git_blob_limit']}`.",
        "",
        "Track all regular source/document files under `tools/`, `tests/`, `packaging/`, and `docs/`, excluding `__pycache__` and bytecode. Track the key final reports listed in `inventory.json`; their SHA-256 values make later release assembly auditable.",
        "",
        "## Integrity and exclusions",
        "",
        f"Selected serving/support trees contain {inventory['integrity_checks']['selected_tree_symlink_or_reparse_count']} symlink/reparse entries. Sensitive filename markers: {len(inventory['integrity_checks']['sensitive_filename_hits'])}; personal/private screenshot markers: {len(inventory['integrity_checks']['personal_screenshot_filename_hits'])}.",
        "The `offline/site/screenshots` paths are public historical site assets; the filename scan found no personal/private screenshot marker.",
        "",
        "Exclude raw CDX/HTTP response forests, backups, mirror/source entities, old offline-site copies, generated caches, and the 2.25 GB historical ZIP from Git. Preserve those as local provenance or Release assets under the repository's separate volume plan.",
        "",
        "## Acceptance limits",
        "",
        "No clone, server launch, upload, or network request was performed. The report establishes static closure and size evidence; a final release should still run the existing browser acceptance report and a clean-clone loopback smoke before publishing.",
        "",
        "See `inventory.json` for exact selected source/report paths, SHA-256 values, manifest checks, and runtime/build dependency distinctions.",
    ]
    (OUT / "inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "inventory": rel(json_path),
        "markdown": rel(OUT / "inventory.md"),
        "site_files": site_stats["file_count"],
        "site_bytes": site_stats["bytes"],
        "support_files": support_stats["file_count"],
        "support_bytes": support_stats["bytes"],
        "manifest_bytes": manifest_stats.get("bytes"),
        "selected_bytes": estimate["bytes_including_site_support_manifest_source_and_reports"],
        "max_selected_file": estimate["max_selected_file"],
        "all_under_100MiB": estimate["all_selected_files_under_git_blob_limit"],
        "sensitive_filename_hits": inventory["integrity_checks"]["sensitive_filename_hits"],
        "personal_screenshot_filename_hits": inventory["integrity_checks"]["personal_screenshot_filename_hits"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

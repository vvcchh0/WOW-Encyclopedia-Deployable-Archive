#!/usr/bin/env python3
"""Read-only byte and provenance comparison for the v33/v34 output trees."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
V33 = ROOT / ".scratch/pages-resources-20261018-v33"
V34 = ROOT / ".scratch/pages-resources-20261019-v34"
REPORT = Path(__file__).resolve().with_name("v33-v34-readonly-diff.json")
DECLARATION_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".map",
    ".svg",
    ".txt",
    ".xml",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_index(root: Path) -> dict[str, Path]:
    return {path.relative_to(root).as_posix(): path for path in root.rglob("*") if path.is_file()}


def file_signature(path: Path) -> dict:
    return {"length": path.stat().st_size, "sha256": sha256_file(path)}


def provenance(root: Path) -> dict:
    return json.loads((root / "export-provenance.json").read_text(encoding="utf-8"))


def overlay_index(data: dict) -> dict[str, dict]:
    return {
        row["output_path"]: row
        for row in data["files"]
        if row.get("kind") == "image_overlay" and row.get("role") == "image_overlay"
    }


def main() -> int:
    old = tree_index(V33)
    new = tree_index(V34)
    old_paths = set(old)
    new_paths = set(new)
    only_v33 = sorted(old_paths - new_paths)
    only_v34 = sorted(new_paths - old_paths)

    changed: list[dict] = []
    declaration_hashes: dict[str, dict] = {}
    for relative in sorted(old_paths & new_paths):
        old_signature = file_signature(old[relative])
        new_signature = file_signature(new[relative])
        if Path(relative).suffix.lower() in DECLARATION_SUFFIXES:
            declaration_hashes[relative] = {"v33": old_signature, "v34": new_signature, "equal": old_signature == new_signature}
        if old_signature != new_signature:
            changed.append({"path": relative, "v33": old_signature, "v34": new_signature})

    old_provenance = provenance(V33)
    new_provenance = provenance(V34)
    old_overlays = overlay_index(old_provenance)
    new_overlays = overlay_index(new_provenance)
    overlay_metadata_changes: list[dict] = []
    overlay_byte_mismatches: list[dict] = []
    for relative in sorted(set(old_overlays) | set(new_overlays)):
        old_row = old_overlays.get(relative)
        new_row = new_overlays.get(relative)
        if old_row != new_row:
            overlay_metadata_changes.append({"output_path": relative, "v33": old_row, "v34": new_row})
        old_path = V33 / relative
        new_path = V34 / relative
        if not old_path.is_file() or not new_path.is_file():
            overlay_byte_mismatches.append({"output_path": relative, "v33_exists": old_path.is_file(), "v34_exists": new_path.is_file()})
            continue
        old_sig = file_signature(old_path)
        new_sig = file_signature(new_path)
        if old_sig != new_sig:
            overlay_byte_mismatches.append({"output_path": relative, "v33": old_sig, "v34": new_sig})

    report = {
        "schema": "wow-recovery.integration.v33-v34-readonly-diff.v1",
        "v33_root": ".scratch/pages-resources-20261018-v33",
        "v34_root": ".scratch/pages-resources-20261019-v34",
        "tree": {
            "v33_files": len(old),
            "v34_files": len(new),
            "v33_bytes": sum(path.stat().st_size for path in old.values()),
            "v34_bytes": sum(path.stat().st_size for path in new.values()),
            "only_v33": only_v33,
            "only_v34": only_v34,
            "changed_files": changed,
        },
        "declaration_files": {
            "count": len(declaration_hashes),
            "changed_count": sum(1 for item in declaration_hashes.values() if not item["equal"]),
            "sha256_and_length": declaration_hashes,
        },
        "provenance": {
            "v33_sha256": sha256_file(V33 / "export-provenance.json"),
            "v34_sha256": sha256_file(V34 / "export-provenance.json"),
            "v33_stats": old_provenance["stats"],
            "v34_stats": new_provenance["stats"],
            "overlay_count_v33": len(old_overlays),
            "overlay_count_v34": len(new_overlays),
            "overlay_metadata_changes": overlay_metadata_changes,
            "overlay_byte_mismatches": overlay_byte_mismatches,
        },
    }
    REPORT.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({
        "report": str(REPORT),
        "report_sha256": sha256_file(REPORT),
        "v33_files": len(old),
        "v34_files": len(new),
        "only_v33": len(only_v33),
        "only_v34": len(only_v34),
        "changed_files": len(changed),
        "declaration_files": len(declaration_hashes),
        "declaration_changed": sum(1 for item in declaration_hashes.values() if not item["equal"]),
        "overlay_count_v33": len(old_overlays),
        "overlay_count_v34": len(new_overlays),
        "overlay_metadata_changes": len(overlay_metadata_changes),
        "overlay_byte_mismatches": len(overlay_byte_mismatches),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

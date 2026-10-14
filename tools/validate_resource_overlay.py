#!/usr/bin/env python3
"""Check gallery directories and restored image references in a local export."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import offline_mirror as mirror
import export_github_pages as pages

ROOT = Path(__file__).resolve().parents[1]
CALL = re.compile(r'''addshots\(\s*["']([^"']+)["']\s*,\s*["']ss["']\s*,\s*numShots\s*\)''')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / ".scratch/pages-resources-20261014")
    parser.add_argument("--output", type=Path, default=ROOT / "research/resource-integration-20261014/root-acceptance.json")
    parser.add_argument("--max-bytes", type=int, default=pages.DEFAULT_MAX_BYTES)
    parser.add_argument("--min-free-bytes", type=int, default=pages.DEFAULT_MIN_FREE_BYTES)
    args = parser.parse_args()
    site = args.site.resolve()
    prov = json.loads((site / "export-provenance.json").read_text(encoding="utf-8"))
    inv = json.loads((ROOT / "research/github-pages-20261013/gallery-inventory-20261013.json").read_text(encoding="utf-8"))
    routes = {row["route"] for row in inv["rows"] if row["route"].endswith(".html")}
    routes.add("/info/dungeons/zulaman-gallery.html")
    checks = []
    for route in sorted(routes):
        source = (ROOT / "offline/site" / route.lstrip("/")).read_text(encoding="utf-8")
        target = (site / route.lstrip("/")).read_text(encoding="utf-8")
        a, b = CALL.search(source), CALL.search(target)
        ok = bool(a and b and b.group(1) == prov["base_path"] + a.group(1).lstrip("/"))
        checks.append({"route": route, "passed": ok,
                       "source_directory": a.group(1) if a else None,
                       "local_directory": b.group(1) if b else None})

    overlays = [item for item in prov["files"] if item.get("role") == "image_overlay"]
    images = []
    for item in overlays:
        data = (site / item["output_path"]).read_bytes()
        raw = (ROOT / item["source_path"]).read_bytes()
        ok = data == raw and hashlib.sha256(data).hexdigest() == item["derived_sha256"]
        images.append({"route": item["route"], "bytes": len(data), "passed": ok})

    keys = {mirror.origin_key(item["original_url"]) for item in overlays}
    remaining = []
    scanned = 0
    for candidate in (site / "visa").rglob("*"):
        if not candidate.is_file() or candidate.suffix.lower() not in {".html", ".css", ".js"}:
            continue
        scanned += 1
        text = candidate.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r'''requested=([^&"'\s<>]+)''', text):
            original = unquote(match.group(1))
            if mirror.origin_key(original) in keys:
                remaining.append({"page": candidate.relative_to(site).as_posix(), "url": original})

    manifest_unchanged = hashlib.sha256((ROOT / "offline/build-manifest.json").read_bytes()).hexdigest() == prov["source_manifest_sha256"]
    image_routes = {item["route"] for item in prov["files"]
                    if str(item.get("mime", "")).split(";", 1)[0] == "image/jpeg"}
    direct_pairs = sum(1 for directory in (item["source_directory"] for item in checks)
                       for route in image_routes
                       if directory and re.fullmatch(re.escape(directory) + r"ss\d+\.jpg", route)
                       and route[:-4] + "-thumb.jpg" in image_routes)
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(), "local_only": True,
        "export_site": site.relative_to(ROOT).as_posix(),
        "export_manifest_sha256": prov["source_manifest_sha256"],
        "frozen_manifest_unchanged": manifest_unchanged,
        "source_records": prov["stats"]["source_records"],
        "overlay_entities": len(overlays), "overlay_bytes": sum(item["bytes"] for item in images),
        "image_bytes_unchanged": all(item["passed"] for item in images),
        "gallery_directory_checks": checks,
        "all_gallery_directories_correct": len(checks) == 50 and all(item["passed"] for item in checks),
        "visa_text_files_scanned": scanned,
        "remaining_placeholders_for_accepted_images": remaining,
        "previous_placeholder_occurrences": 67,
        "direct_gallery_pairs_available": direct_pairs,
        "workspace_bytes_including_git": pages.workspace_size(ROOT),
        "workspace_limit_bytes": args.max_bytes,
        "drive_free_bytes": shutil.disk_usage(site).free,
        "min_free_bytes": args.min_free_bytes,
    }
    result["passed"] = bool(manifest_unchanged and result["all_gallery_directories_correct"]
                            and images and result["image_bytes_unchanged"] and not remaining
                            and (args.max_bytes is None or result["workspace_bytes_including_git"] < args.max_bytes)
                            and result["drive_free_bytes"] >= args.min_free_bytes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "gallery_directory_checks"}, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

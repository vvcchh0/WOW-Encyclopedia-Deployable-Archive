"""Decode exported historical images without changing their bytes.

Run with a Python environment providing Pillow. The Codex bundled runtime
provides it; acquisition and source-index tools still use only the stdlib.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageSequence, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP = ROOT / "mirror/20080512/url-map.json"
DEFAULT_OUT = ROOT / "research/acquisition-2008/acceptance/image-decode-validation.json"
RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp"}


def verify(mapping: Path, output: Path) -> dict:
    source = json.loads(mapping.read_text(encoding="utf-8"))
    mirror_root = mapping.parent.resolve()
    results = []
    skipped = []
    for item in source["files"]:
        relative = item["local_path"]
        path = (ROOT / relative).resolve()
        if path.suffix.lower() not in RASTER_EXTENSIONS:
            skipped.append(relative)
            continue
        row = {"logical_url": item["logical_url"], "local_path": relative}
        try:
            path.relative_to(mirror_root)
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if digest != item["sha256"] or len(data) != item["content_length"]:
                raise ValueError("Export differs from source map SHA256 or length")
            with Image.open(path) as image:
                row.update(format=image.format, size=list(image.size), mode=image.mode)
                image.verify()
            # verify() checks structure; loading pixels also detects truncated
            # compressed payloads. Every GIF frame is decoded when present.
            frames = 0
            with Image.open(path) as image:
                for frame in ImageSequence.Iterator(image):
                    frame.load()
                    frames += 1
                    if frames > 10000:
                        raise ValueError("Frame verification bound exceeded")
            row.update(valid=True, frames_decoded=frames, bytes=len(data), sha256=digest)
        except Exception as error:
            row.update(valid=False, error=f"{type(error).__name__}: {error}")
        results.append(row)
    failures = [row for row in results if not row["valid"]]
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_map": mapping.relative_to(ROOT).as_posix(),
        "pillow_version": pillow_version,
        "unmodified_entities": True,
        "images_checked": len(results),
        "images_valid": len(results) - len(failures),
        "failures": failures,
        "formats": dict(Counter(row.get("format", "unknown") for row in results)),
        "results": results,
        "non_raster_files_skipped": len(skipped),
        "boundary": "Source-byte validation only; no website rendering or Flash compatibility test.",
    }
    output.resolve().relative_to(ROOT)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    report = verify(args.map.resolve(), args.out.resolve())
    print(json.dumps({key: report[key] for key in ("images_checked", "images_valid", "formats", "failures")}))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

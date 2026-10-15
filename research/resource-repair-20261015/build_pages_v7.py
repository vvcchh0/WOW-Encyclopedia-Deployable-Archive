"""Export the accepted navigation staging tree with the verified image maps."""
from __future__ import annotations

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import export_github_pages as pages


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".scratch/pages-resources-20261015-v7")
    parser.add_argument("--receipt", type=Path, default=ROOT / "research/resource-repair-20261015/build-v7.json")
    args = parser.parse_args()
    for path in (args.output, args.receipt):
        path.resolve().relative_to(ROOT)
    stage = ROOT / ".scratch/offline-navigation-20261015-v7c"
    primary = [
        ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
        ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
    ]
    supplement = [
        ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
        ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
        ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ]
    result = pages.export_pages(
        source_site=stage / "site",
        manifest_path=stage / "build-manifest.json",
        output=args.output,
        image_source_maps=primary,
        supplement_image_source_maps=supplement,
        allow_later_image_supplements=True,
    )
    receipt = {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "build": result,
        "source_stage": str(stage.relative_to(ROOT)),
        "primary_source_maps": [p.relative_to(ROOT).as_posix() for p in primary],
        "supplement_source_maps": [p.relative_to(ROOT).as_posix() for p in supplement],
        "allow_later_image_supplements": True,
        "published": False,
    }
    target = args.receipt
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()

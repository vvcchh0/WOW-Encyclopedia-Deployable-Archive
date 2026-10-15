"""Rebuild the bounded v7c navigation source tree in its fixed scratch path."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = (ROOT / ".scratch" / "offline-navigation-20261015-v7c").resolve()
EXPECTED_TARGET = (ROOT / ".scratch" / "offline-navigation-20261015-v7c").resolve()


def main() -> int:
    if TARGET != EXPECTED_TARGET or ROOT not in TARGET.parents:
        raise SystemExit(f"unsafe scratch target: {TARGET}")
    support = TARGET / "support"
    support.mkdir(parents=True, exist_ok=True)
    for name in ("compat.css", "compat.js"):
        shutil.copy2(ROOT / "offline" / "support" / name, support / name)
    command = [
        sys.executable,
        "-X",
        "utf8",
        "tools/offline_mirror.py",
        "build",
        "--url-map",
        "mirror/20080512/url-map.json",
        "--overlay",
        "research/gap-review-20261011/reviewed-index-overlay.json",
        "--site",
        ".scratch/offline-navigation-20261015-v7c/site",
        "--manifest",
        ".scratch/offline-navigation-20261015-v7c/build-manifest.json",
        "--support-dir",
        ".scratch/offline-navigation-20261015-v7c/support",
    ]
    for path in (
        "offline/approved-pages-recovery-map.json",
        "offline/approved-pages-temporal-supplement-map.json",
        "offline/approved-static-recovery-map.json",
        "offline/approved-static-temporal-supplement-map.json",
        "offline/approved-static-pre2008-supplement-map.json",
        "offline/approved-expansion-map.json",
        "offline/approved-route-alias-overlay.json",
        "offline/upstream-compatibility-map.json",
        "research/navigation-gaps-20261015/wayback-missing/effective-source-map-v7c.json",
    ):
        command.extend(("--extra-map", path))
    return subprocess.run(command, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())

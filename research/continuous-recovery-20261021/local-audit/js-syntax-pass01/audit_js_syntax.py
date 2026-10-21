"""Bounded, read-only Node syntax audit for the v45 exported JavaScript set."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[4]
SITE = ROOT / ".scratch/pages-resources-20261021-v45"
NODE = Path(r"C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
OUT = Path(__file__).resolve().parent
TEMP = ROOT / ".scratch/test-temp-20261021"
DISK_FLOOR = 11_005_853_696

# These markers identify JavaScript that is explicitly tied to screenshots,
# artwork galleries, thumbnail viewers, or SSOTD.  Other shared and legacy
# scripts remain in the check set, including offline runtime support.
GALLERY_MARKERS = (
    "gallery",
    "screenie",
    "screenshot",
    "screenshots",
    "ssotd",
    "artwork",
    "thumbnailslayout.js",
)


def disk_check() -> int:
    free = shutil.disk_usage(ROOT.anchor).free
    if free < DISK_FLOOR:
        raise RuntimeError(f"D: free space below floor: {free} < {DISK_FLOOR}")
    return free


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(SITE).as_posix()


def exclusion_reason(rel: str) -> str | None:
    lowered = rel.casefold()
    for marker in GALLERY_MARKERS:
        if marker in lowered:
            return f"explicit gallery/SSOTD marker: {marker}"
    return None


def inventory() -> dict:
    if not SITE.is_dir():
        raise RuntimeError(f"v45 site missing: {SITE}")
    entries = []
    for path in sorted(SITE.rglob("*.js"), key=lambda item: relative(item).casefold()):
        rel = relative(path)
        reason = exclusion_reason(rel)
        entries.append(
            {
                "relative_path": rel,
                "length": path.stat().st_size,
                "sha256": sha256_file(path),
                "included": reason is None,
                "exclusion_reason": reason,
            }
        )
    return {
        "schema": "wow-v45-js-syntax-inventory/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "site": ".scratch/pages-resources-20261021-v45",
        "node": str(NODE),
        "total_js": len(entries),
        "included_js": sum(1 for item in entries if item["included"]),
        "excluded_js": sum(1 for item in entries if not item["included"]),
        "entries": entries,
    }


def check(inventory_data: dict) -> dict:
    TEMP.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["TEMP"] = str(TEMP)
    env["TMP"] = str(TEMP)
    env["TMPDIR"] = str(TEMP)
    rows = []
    included = [item for item in inventory_data["entries"] if item["included"]]
    for item in included:
        path = SITE / Path(item["relative_path"])
        started = time.monotonic()
        status = "pass"
        returncode = None
        stdout = ""
        stderr = ""
        try:
            completed = subprocess.run(
                [str(NODE), "--check", str(path)],
                cwd=str(ROOT),
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                check=False,
            )
            returncode = completed.returncode
            stdout = completed.stdout[-4000:]
            stderr = completed.stderr[-4000:]
            if returncode != 0:
                status = "fail"
        except subprocess.TimeoutExpired as exc:
            status = "timeout"
            stdout = str(exc.stdout or "")[-4000:]
            stderr = str(exc.stderr or "")[-4000:]
        duration_ms = round((time.monotonic() - started) * 1000, 1)
        rows.append(
            {
                "relative_path": item["relative_path"],
                "sha256": item["sha256"],
                "length": item["length"],
                "status": status,
                "returncode": returncode,
                "duration_ms": duration_ms,
                "stdout": stdout,
                "stderr": stderr,
            }
        )
    return {
        "schema": "wow-v45-js-syntax-results/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "site": ".scratch/pages-resources-20261021-v45",
        "node": str(NODE),
        "node_command": "node.exe --check <absolute-v45-js-file>",
        "per_file_timeout_seconds": 10,
        "temp": str(TEMP.relative_to(ROOT)).replace("\\", "/"),
        "checked_js": len(rows),
        "pass": sum(1 for item in rows if item["status"] == "pass"),
        "fail": sum(1 for item in rows if item["status"] == "fail"),
        "timeout": sum(1 for item in rows if item["status"] == "timeout"),
        "results": rows,
    }


def write_json(path: Path, value: dict) -> None:
    disk_check()
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("inventory", "check"))
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    inv = inventory()
    write_json(OUT / "inventory.json", inv)
    if args.phase == "check":
        results = check(inv)
        write_json(OUT / "syntax-results.json", results)
        print(json.dumps({key: results[key] for key in ("checked_js", "pass", "fail", "timeout")}, sort_keys=True))
    else:
        print(json.dumps({key: inv[key] for key in ("total_js", "included_js", "excluded_js")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

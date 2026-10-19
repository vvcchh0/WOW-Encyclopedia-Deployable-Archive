"""Independently check the preserved v33 bundle using the reviewed checker.

The 2026-10-18 implementation and its accepted inputs remain immutable.
Only the output receipt, local server log and isolated extraction destination
are assigned to this run. The checker makes loopback requests only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRIOR = ROOT / "research/continuous-recovery-20261018/integration/portable-release-tools-v2"
OUT = ROOT / "research/continuous-recovery-20261019/publication"
sys.path.insert(0, str(PRIOR))
import check_portable as checker

original_paths = checker.release_paths


def paths_for_this_check(version: str) -> dict:
    assert version == "v33"
    paths = original_paths(version)
    paths.update({
        "portable": OUT / "root-v33-portable-acceptance.json",
        "extract": ROOT / ".scratch/local bundle smoke 20261019 v33",
        "server_log": OUT / "v33-portable-server-local.log",
    })
    return paths


if __name__ == "__main__":
    checker.release_paths = paths_for_this_check
    checker.main()
    receipt_path = paths_for_this_check("v33")["portable"]
    receipt = json.loads(receipt_path.read_bytes())
    receipt.update({
        "validation_run_date": "2026-10-19",
        "browser_coverage_complete": False,
        "browser_scope": "Original bytes and selected interactions accepted; remaining v33 UI targets are under separate audit.",
        "checker_source": str((PRIOR / "check_portable.py").relative_to(ROOT)).replace("\\", "/"),
        "checker_source_sha256": hashlib.sha256((PRIOR / "check_portable.py").read_bytes()).hexdigest(),
        "adapter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "intended_publication_tag": "archive-20080512-browser-20261019",
    })
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

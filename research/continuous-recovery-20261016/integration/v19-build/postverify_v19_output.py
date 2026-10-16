#!/usr/bin/env python3
"""Re-verify a completed v19 output without invoking the exporter.

The first v19 worker receipt records a postbuild-helper exception after the
export itself completed.  This script is deliberately read-only with respect
to the output tree and refuses to overwrite its own receipt.
"""

from __future__ import annotations

import hashlib
import json
import runpy
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HELPER = ROOT / "research/continuous-recovery-20261016/integration/v19-build/build_pages_v19.py"
FAILURE_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v19-build/worker-build-v19.json"
POST_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v19-build/postbuild-verification-v19.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v19"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> int:
    if POST_RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite existing postverification receipt: {POST_RECEIPT}")
    if not FAILURE_RECEIPT.is_file() or not OUTPUT.is_dir() or (OUTPUT.with_name(OUTPUT.name + ".partial")).exists():
        raise RuntimeError("completed v19 output and original worker failure receipt are required")
    worker = json.loads(FAILURE_RECEIPT.read_text(encoding="utf-8"))
    if worker.get("export_started") is not True or worker.get("export_completed") is not False:
        raise RuntimeError("the original worker receipt is not the expected one-time postbuild failure")
    module = runpy.run_path(str(HELPER))
    provenance = module["read_object"](OUTPUT / "export-provenance.json", "v19 provenance")
    checks = module["verify_postbuild"]({"output_files": (provenance.get("stats") or {}).get("output_files")})
    locks_after = module["locked_input_hashes"]()
    before = worker.get("input_hashes_before") or {}
    if before and before != locks_after:
        raise RuntimeError("locked inputs differ from the original one-time export")
    actual_files = module["output_file_count"](OUTPUT)
    tree_bytes = sum(item.stat().st_size for item in OUTPUT.rglob("*") if item.is_file())
    payload = {
        "schema": "wow-recovery.integration.v19.postbuild-verification.v1",
        "executed_by": "/root/local_recovery_20261016",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "network_requests": 0,
        "export_reinvoked": False,
        "original_worker_receipt": rel(FAILURE_RECEIPT),
        "original_worker_receipt_sha256": sha256(FAILURE_RECEIPT),
        "original_worker_error": worker.get("error"),
        "builder_sha256_after_helper_fix": sha256(HELPER),
        "output": rel(OUTPUT),
        "output_provenance_sha256": sha256(OUTPUT / "export-provenance.json"),
        "actual_output_files": actual_files,
        "output_tree_bytes": tree_bytes,
        "postbuild_checks": checks,
        "locked_inputs_after": locks_after,
        "locked_inputs_equal_to_original_before": bool(before == locks_after),
        "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
        "partial_exists": False,
    }
    POST_RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

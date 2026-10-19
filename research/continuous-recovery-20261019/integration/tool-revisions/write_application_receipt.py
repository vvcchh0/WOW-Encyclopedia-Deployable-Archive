"""Persist hashes and the exact bounded diff for the approved tool revision."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PRODUCTION = [
    Path("tools/export_github_pages.py"),
    Path("tools/historical_exhibits.py"),
    Path("tests/test_github_pages_export.py"),
    Path("tests/test_historical_exhibits.py"),
]
BASELINE = {
    "tools/export_github_pages.py": "e5b3a53381ddcf0b5037a726d328c7dd99fa5d2f8e24e047e474a3853305643a",
    "tools/historical_exhibits.py": "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_info(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_bytes(data), "bytes": len(data)}


def main() -> None:
    diff = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--", *(str(path) for path in PRODUCTION)],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    diff_path = HERE / "formal-application.diff"
    diff_path.write_bytes(diff)
    test_receipt_path = HERE / "focused-tests-receipt.json"
    test_receipt = json.loads(test_receipt_path.read_text(encoding="utf-8"))
    candidates = {}
    for path in (
        Path("research/continuous-recovery-20261019/integration/visa-exhibit/visa-exhibit.patch"),
        Path("research/continuous-recovery-20261019/integration/visa-exhibit/export_historical_exhibits_candidate.py"),
        Path("research/continuous-recovery-20261019/integration/visa-exhibit/test_visa_exhibit_candidate.py"),
        Path("research/continuous-recovery-20261019/integration/visa-exhibit/verification-receipt.json"),
    ):
        if (ROOT / path).is_file():
            candidates[path.as_posix()] = file_info(ROOT / path)
    initial_failure = HERE / "focused-tests-initial-path-failure.json"
    payload = {
        "schema": 1,
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "scope": {
            "applied": [str(path).replace("\\", "/") for path in PRODUCTION],
            "export_executed": False,
            "network_used": False,
            "git_commit_or_push": False,
        },
        "baseline_production_sha256": BASELINE,
        "production_files": [file_info(ROOT / path) for path in PRODUCTION],
        "formal_diff": file_info(diff_path),
        "focused_test_receipt": file_info(test_receipt_path),
        "focused_test_log": file_info(HERE / "focused-tests.log"),
        "focused_test_results": [
            {
                "command": record["command"],
                "returncode": record["returncode"],
                "timed_out": record["timed_out"],
                "elapsed_seconds": record["elapsed_seconds"],
            }
            for record in test_receipt["commands"]
        ],
        "initial_runner_path_failure": file_info(initial_failure) if initial_failure.is_file() else None,
        "frozen_candidate_artifacts": candidates,
        "behavior": {
            "uncapped_workspace_bytes": None,
            "finite_workspace_checks": "before and after retained",
            "visa_canonical_route": "/visa/index.html",
            "visa_aliases": ["/visa", "/visa/"],
            "visa_images": 6,
            "visa_navigation_targets": ["/", "/visa/reward/index.html"],
            "visa_business_controls": "removed from derived exhibit",
        },
    }
    receipt_path = HERE / "formal-application-receipt.json"
    receipt_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()

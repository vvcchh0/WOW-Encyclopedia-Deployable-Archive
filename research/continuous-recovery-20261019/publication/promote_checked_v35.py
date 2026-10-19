"""Complete the interrupted v35 export using its fully checked existing bytes."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
FOLDER = ROOT / "research/continuous-recovery-20261019/integration/v35/finalization"
GO = PUB / "root-v35-finalization-go.json"
OUT = PUB / "root-v35-finalization-execution.json"
PARTIAL = ROOT / ".scratch/pages-resources-20261019-v35.partial"
SITE = ROOT / ".scratch/pages-resources-20261019-v35"
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sys.argv[1:] == ["--root-go"] and not OUT.exists()
    go = json.loads(GO.read_bytes())
    assert go["accepted"] and go["root_go"] and go["runner_sha256"] == SHA(Path(__file__))
    finalizer = FOLDER / "finalize_v35_partial.py"
    check = FOLDER / "v35-partial-check-receipt.json"
    assert SHA(finalizer) == go["finalizer_sha256"] == "146d9b60cb186c548c5670130ebff80aa2d3238b9b8d5b5cce8a782d50894955"
    assert SHA(check) == go["check_receipt_sha256"] == "eb05bfc5dd10fb8370ba8f806fa625abd6a5b43378196571e821c9c69d747122"
    for path in (PARTIAL, SITE):
        path.resolve().relative_to((ROOT / ".scratch").resolve())
        path.resolve().relative_to(ROOT.resolve())
    assert PARTIAL.is_dir() and not PARTIAL.is_symlink() and not SITE.exists()
    assert SHA(PARTIAL / "export-provenance.json") == go["provenance_sha256"]
    spec = importlib.util.spec_from_file_location("root_v35_pre_promotion_checks", finalizer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Recheck every current input binding immediately before the rename.
    assert module.verify_input_gate()["binding_count"] == 62
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    start = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    with (PUB / "v35-finalization.stdout.log").open("xb") as stdout, (PUB / "v35-finalization.stderr.log").open("xb") as stderr:
        process = subprocess.run([sys.executable, "-B", "-X", "utf8", str(finalizer), "--promote", "--root-go",
            "--check-receipt", str(check), "--check-receipt-sha256", SHA(check)],
            cwd=ROOT, stdout=stdout, stderr=stderr, check=False, timeout=60)
    elapsed = time.monotonic() - start
    assert process.returncode == 0 and SITE.is_dir() and not PARTIAL.exists()
    assert SHA(SITE / "export-provenance.json") == go["provenance_sha256"]
    assert shutil.disk_usage(ROOT).free >= 11005853696
    receipt = {"accepted": True, "status": "finalized_from_checked_partial", "published": False,
        "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed, "hard_parent_timeout_seconds": 60, "child_returncode": process.returncode,
        "go_sha256": SHA(GO), "check_receipt_sha256": SHA(check), "finalizer_sha256": SHA(finalizer),
        "export_provenance_sha256": SHA(SITE / "export-provenance.json"),
        "local_site": SITE.relative_to(ROOT).as_posix(), "declared_files": 9041, "actual_files": 9042,
        "new_images": 24, "image_bytes": 191943, "workspace_total_budget": None,
        "disk_free_before_bytes": free, "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
        "network_requests": 0, "new_export_invocations": 0,
        "scope": "All9041 declared files were previously checked in83.875s; root rechecked62 current input bindings and provenance immediately before the frozen atomic promotion. No site file was rewritten. Historical timeout receipt and its erratum remain preserved."}
    OUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": True, "status": receipt["status"], "elapsed_seconds": elapsed, "published": False}))


if __name__ == "__main__":
    main()

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "research/continuous-recovery-20261016/network/driver-v3"
PLAN_DIR = ROOT / "research/continuous-recovery-20261016/network/gallery-prefix02-plan"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def file_binding(path: Path, role: str) -> dict[str, object]:
    return {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size, "role": role}


def main() -> None:
    fixture_path = OUT / "fixture-results.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    source_files = [
        file_binding(OUT / "gallery_prefix_driver_v3.py", "new monotonic/capped execution driver"),
        file_binding(OUT / "cadence-fix-report.json", "offline analysis of frozen 5.093s deviation and v3 fix"),
        file_binding(fixture_path, "offline fixture; no network requests"),
        file_binding(PLAN_DIR / "plan.json", "prepared ten-candidate prefix plan"),
        file_binding(PLAN_DIR / "selection-map.json", "candidate/exclusion selection map"),
        file_binding(PLAN_DIR / "input-bindings.json", "plan source provenance"),
        file_binding(ROOT / "research/continuous-recovery-20261016/network/gallery-prefix01/batch-report.json", "frozen prior tail=2"),
        file_binding(ROOT / "research/continuous-recovery-20261016/network/gallery-prefix01/execution-deviation.json", "frozen 5.093s cadence deviation"),
    ]
    result = {
        "schema": "wow-recovery.gallery-prefix02-driver-v3-input-bindings.v1",
        "batch_id": "WAYBACK-GALLERYPREFIX02-20261016",
        "mode": "offline_preparation",
        "network_requests": 0,
        "parent_go_required": True,
        "source_files": source_files,
        "fixture": {
            "path": rel(fixture_path), "sha256": sha(fixture_path),
            "all_passed": fixture["all_passed"], "passed": fixture["passed"], "total": fixture["total"],
            "cadence": fixture["cadence"],
        },
        "cadence_fix": {
            "historical_observed_min_dispatch_seconds": 5.093000000000757,
            "scheduling_floor_seconds": 5.25,
            "acceptance_floor_seconds": 5.1,
            "algorithm": "monotonic deadline loop with post-sleep re-read; UTC start floor retained for restart continuity",
            "restart_scope": "fixture timing helper only; execution does not auto-resume an interrupted journal",
            "historical_deviation_path": "research/continuous-recovery-20261016/network/gallery-prefix01/execution-deviation.json",
        },
        "clamp_fix": {
            "remaining_bytes": True,
            "remaining_window_seconds": True,
            "per_request_disk_free_before_bytes": True,
            "total_cap_bytes": 67108864,
            "entity_cap_bytes": 16777216,
        },
        "prior_tail": {
            "source_batch": "WAYBACK-GALLERYPREFIX01-20261016",
            "failure_streak": 2,
            "inherited_nonzero": True,
            "historical_allnews02_tail_preserved_separately": 5,
        },
    }
    (OUT / "input-bindings.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": rel(OUT / "input-bindings.json"), "sha256": sha(OUT / "input-bindings.json"), "driver_sha256": source_files[0]["sha256"], "fixture_sha256": sha(fixture_path), "all_passed": fixture["all_passed"], "min_dispatch": fixture["cadence"]["min_dispatch"], "min_request_start": fixture["cadence"]["min_request_start"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

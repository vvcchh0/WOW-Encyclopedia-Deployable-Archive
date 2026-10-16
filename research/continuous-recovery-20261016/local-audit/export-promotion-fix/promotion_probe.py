"""Probe the host's small-directory Path.replace behavior for LOCAL24."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RECEIPT = Path(__file__).resolve().with_name("promotion-probe.json")


def _error_fields(error: BaseException) -> dict[str, object]:
    return {
        "type": type(error).__name__,
        "errno": getattr(error, "errno", None),
        "winerror": getattr(error, "winerror", None),
        "message": str(error),
    }


def main() -> int:
    scratch_parent = ROOT / ".scratch"
    scratch_parent.mkdir(parents=True, exist_ok=True)
    observations: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="local24-promotion-probe-", dir=scratch_parent) as temp:
        base = Path(temp)
        partial = base / "absent-target.partial"
        output = base / "absent-target"
        partial.mkdir()
        (partial / "marker.txt").write_text("partial", encoding="utf-8")
        try:
            partial.replace(output)
            observations.append({
                "case": "target_absent",
                "operation": "Path.replace",
                "result": "success",
                "partial_exists_after": partial.exists(),
                "output_exists_after": output.exists(),
                "output_marker": (output / "marker.txt").read_text(encoding="utf-8"),
            })
        except OSError as error:
            observations.append({"case": "target_absent", "operation": "Path.replace", "result": "error", "error": _error_fields(error)})

        existing_partial = base / "existing-target.partial"
        existing_output = base / "existing-target"
        existing_partial.mkdir()
        existing_output.mkdir()
        (existing_partial / "marker.txt").write_text("partial", encoding="utf-8")
        (existing_output / "marker.txt").write_text("existing", encoding="utf-8")
        try:
            existing_partial.replace(existing_output)
            observations.append({
                "case": "target_exists",
                "operation": "Path.replace",
                "result": "success",
                "partial_exists_after": existing_partial.exists(),
                "output_exists_after": existing_output.exists(),
                "output_marker": (existing_output / "marker.txt").read_text(encoding="utf-8"),
                "target_was_overwritten": (existing_output / "marker.txt").read_text(encoding="utf-8") == "partial",
            })
        except OSError as error:
            observations.append({
                "case": "target_exists",
                "operation": "Path.replace",
                "result": "error",
                "partial_exists_after": existing_partial.exists(),
                "output_exists_after": existing_output.exists(),
                "output_marker": (existing_output / "marker.txt").read_text(encoding="utf-8") if (existing_output / "marker.txt").is_file() else None,
                "error": _error_fields(error),
            })

    payload = {
        "schema": "wow-recovery.local-audit.export-promotion-probe.v1",
        "executed_by": "/root/local_recovery_20261016",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "host": {"os_name": os.name, "platform": os.sys.platform},
        "scratch_cleanup": True,
        "observations": observations,
        "source_exception_receipt": "research/continuous-recovery-20261016/integration/v21-build/worker-build-v21.json",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

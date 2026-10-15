"""Offline fake-transport test for NET-CONTROL-007 persistence.

The test never calls curl.  It uses GateState with a stub transport label and
an isolated journal, then raises a simulated summary exception and invokes the
same postflight-finally helper used by the wrapper.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "research/continuous-recovery-20261015/network-control7"
CASE = OUT / "isolated-self-test/persistence-case"
CONTROL7_PATH = OUT / "control7.py"


def load_control7() -> Any:
    spec = importlib.util.spec_from_file_location("control7_self_test_module", CONTROL7_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load control7.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    c7 = load_control7()
    CASE.mkdir(parents=True, exist_ok=True)
    real_report = OUT / "control-report.json"
    real_dispatch = OUT / "dispatch-log.json"
    real_before = {"report": sha(real_report), "dispatch_log": sha(real_dispatch)}
    journal_path = CASE / "dispatch-log.json"
    fake_preflight = 20_000_000_000
    fake_postflight = 19_999_998_000
    journal = {
        "schema": "wayback-net-control7-dispatch-log/v1",
        "simulation": True,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "disk_preflight": {
            "checked_utc": datetime.now(timezone.utc).isoformat(),
            "disk_free_bytes": fake_preflight,
            "minimum_free_bytes": c7.MIN_FREE_BYTES,
            "passed": fake_preflight >= c7.MIN_FREE_BYTES,
        },
        "dispatches": [],
    }
    state = c7.GateState(
        datetime.now(timezone.utc) - timedelta(seconds=1),
        journal_path=journal_path,
        journal=journal,
    )
    state.persist()

    original_run = c7.subprocess.run

    def forbidden_run(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("stub test attempted to invoke subprocess/network")

    c7.subprocess.run = forbidden_run
    dispatch_records: list[dict[str, Any]] = []
    try:
        for number in range(1, 4):
            record = state.before_dispatch(number, "stub", "simulation://known-jpeg")
            saved = json.loads(journal_path.read_text(encoding="utf-8"))
            assert saved["simulation"] is True
            assert saved["disk_preflight"]["disk_free_bytes"] == fake_preflight
            assert len(saved["dispatches"]) == number
            assert record["persisted_before_transport"] is True
            assert isinstance(record["dispatch_utc"], str)
            assert isinstance(record["dispatch_monotonic"], float)
            # This is the fake transport: no subprocess or network call.
            dispatch_records.append({"attempt": number, "source_status": 200, "transport": "stub"})
        intervals = [
            state.dispatches[i]["dispatch_monotonic"] - state.dispatches[i - 1]["dispatch_monotonic"]
            for i in range(1, len(state.dispatches))
        ]
        assert len(intervals) == 2
        assert min(intervals) >= c7.INTERVAL_SECONDS
        summary_exception: str | None = None
        try:
            raise RuntimeError("simulated summary assembly exception")
        except RuntimeError as exc:
            summary_exception = type(exc).__name__ + ": " + str(exc)
        finally:
            postflight = c7.persist_postflight(state, len(dispatch_records), free_fn=lambda: fake_postflight)
        final = json.loads(journal_path.read_text(encoding="utf-8"))
        assert summary_exception is not None
        assert final["simulation"] is True
        assert final["disk_preflight"]["disk_free_bytes"] == fake_preflight
        assert final["disk_postflight"]["disk_free_bytes"] == fake_postflight
        assert final["disk_postflight"]["persisted_in_finally"] is True
        assert final["postflight_persisted_in_finally"] is True
        assert final["final_attempt_count"] == 3
        assert postflight["attempts_count"] == 3
        gate_test = c7.fakeclock_gate_test()
        assert gate_test["passed"] is True
        assertions = {
            "simulation": True,
            "network_requests": 0,
            "subprocess_network_guard": True,
            "early_wake_recomputed": gate_test["passed"],
            "dispatch_count": len(final["dispatches"]),
            "dispatch_utc_monotonic_persisted_immediately": all(
                isinstance(item.get("dispatch_utc"), str)
                and isinstance(item.get("dispatch_monotonic"), float)
                and item.get("persisted_before_transport") is True
                for item in final["dispatches"]
            ),
            "minimum_dispatch_interval_seconds": min(intervals),
            "minimum_interval_required_seconds": c7.INTERVAL_SECONDS,
            "interval_assertion": min(intervals) >= c7.INTERVAL_SECONDS,
            "disk_preflight_persisted": final["disk_preflight"]["disk_free_bytes"] == fake_preflight,
            "summary_exception_simulated": summary_exception,
            "postflight_persisted_in_finally": final["postflight_persisted_in_finally"] is True,
            "postflight_disk_bytes": final["disk_postflight"]["disk_free_bytes"],
            "real_report_unchanged": sha(real_report) == real_before["report"],
            "real_dispatch_log_unchanged": sha(real_dispatch) == real_before["dispatch_log"],
        }
        assert all(value is True for key, value in assertions.items() if key.endswith("persisted") or key.endswith("assertion") or key.endswith("unchanged") or key in {"simulation", "subprocess_network_guard", "early_wake_recomputed", "dispatch_utc_monotonic_persisted_immediately", "disk_preflight_persisted", "postflight_persisted_in_finally"})
        result = {
            "schema": "wayback-net-control7-gate-persistence-self-test/v1",
            "simulation": True,
            "network_requests": 0,
            "isolated_output": "isolated-self-test/persistence-case/dispatch-log.json",
            "assertions": assertions,
            "real_artifacts_before": real_before,
            "real_artifacts_after": {"report": sha(real_report), "dispatch_log": sha(real_dispatch)},
            "journal_sha256": sha(journal_path),
        }
        write_json(OUT / "gate-persistence-self-test.json", result)
        write_json(CASE / "test-result.json", result)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    finally:
        c7.subprocess.run = original_run


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"test_gate_persistence: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

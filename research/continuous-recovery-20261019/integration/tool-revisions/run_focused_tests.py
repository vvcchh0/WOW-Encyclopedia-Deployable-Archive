"""Run the two authorized focused regression suites with hard subprocess bounds."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
LOG = Path(__file__).with_name("focused-tests.log")
RECEIPT = Path(__file__).with_name("focused-tests-receipt.json")
PYTHON = r"C:\Program Files\Python311\python.exe"
COMMANDS = [
    [PYTHON, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests", "-p", "test_github_pages_export.py", "-v"],
    [PYTHON, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests", "-p", "test_historical_exhibits.py", "-v"],
]


def main() -> int:
    records: list[dict[str, object]] = []
    log_parts: list[str] = []
    overall = 0
    for command in COMMANDS:
        started = time.time()
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                check=False,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            returncode = completed.returncode
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
            stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
            returncode = None
            timed_out = True
        elapsed = round(time.time() - started, 3)
        overall = overall or int(timed_out or returncode not in (0,))
        record = {
            "command": command,
            "returncode": returncode,
            "timed_out": timed_out,
            "elapsed_seconds": elapsed,
            "stdout": stdout,
            "stderr": stderr,
        }
        records.append(record)
        log_parts.append("$ " + " ".join(command) + "\n" + stdout + stderr)
    LOG.write_text("\n\n".join(log_parts), encoding="utf-8", newline="\n")
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": 1,
                "root": str(ROOT),
                "timeout_seconds_per_subprocess": 120,
                "commands": records,
                "overall_returncode": overall,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return overall


if __name__ == "__main__":
    raise SystemExit(main())

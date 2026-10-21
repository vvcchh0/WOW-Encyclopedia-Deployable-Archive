"""Bound the once-only v45 export process and retain its actual outcome."""
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'v45-export-execution.json'
LOG = PUB / 'v45-export-execution.log'
assert not OUT.exists() and not LOG.exists()
assert shutil.disk_usage(ROOT).free >= 11005853696
started = datetime.now(timezone.utc).isoformat()
tick = time.monotonic()
command = [sys.executable, '-B', '-X', 'utf8',
           'research/continuous-recovery-20261021/integration/v45/export_v45_once.py', '--execute']
timed_out = False
try:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=540)
    code, output = result.returncode, result.stdout + result.stderr
except subprocess.TimeoutExpired as exc:
    timed_out = True
    code, output = None, (exc.stdout or b'') + (exc.stderr or b'')
LOG.write_bytes(output)
receipt = {
    'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
    'elapsed_seconds': time.monotonic() - tick, 'timeout_seconds': 540,
    'returncode': code, 'timed_out': timed_out, 'command': command,
    'log_sha256': hashlib.sha256(output).hexdigest(),
    'disk_free_after_bytes': shutil.disk_usage(ROOT).free,
    'network_requests': 0, 'published': False,
}
OUT.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(json.dumps(receipt))
assert code == 0 and not timed_out

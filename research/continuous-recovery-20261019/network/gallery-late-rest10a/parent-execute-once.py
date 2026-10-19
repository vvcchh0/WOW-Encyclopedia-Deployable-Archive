from __future__ import annotations
import hashlib, json, shutil, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
DRIVER = OUT / 'gallery_late_rest10a_driver_v1.py'
PLAN = OUT / 'plan.json'
FIXTURE = OUT / 'fixture-results.json'
GO = ROOT / 'research/continuous-recovery-20261019/publication/root-gallery-late-rest10a-execute-go.json'
STDOUT = OUT / 'parent-stdout.txt'
STDERR = OUT / 'parent-stderr.txt'
RECEIPT = OUT / 'parent-execution-receipt.json'

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def files_under(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    out=[]
    for item in sorted(path.rglob('*')):
        if item.is_file():
            out.append({'path': rel(item), 'bytes': item.stat().st_size, 'sha256': sha(item)})
    return out

go_data = json.loads(GO.read_text(encoding='utf-8'))
if go_data.get('accepted') is not True or go_data.get('root_go') is not True:
    raise SystemExit('root GO is not accepted')
expected = {
    'driver_sha256': sha(DRIVER),
    'plan_sha256': sha(PLAN),
    'fixture_before_execution_sha256': sha(FIXTURE),
}
for key, actual in expected.items():
    if go_data.get(key) != actual:
        raise SystemExit(f'GO {key} mismatch: {go_data.get(key)} != {actual}')
free_before = shutil.disk_usage(ROOT).free
floor = 11005853696
if free_before < floor:
    raise SystemExit(f'disk floor before parent run: {free_before}')
for name in ('batch-report.json','source-map.json','sanitized-summary.json','progress.json','execution-plan.json','execution-input-bindings.json','parent-execution-receipt.json'):
    if (OUT / name).exists():
        raise SystemExit(f'pre-existing runtime output: {name}')
raw = OUT / 'raw'
if files_under(raw):
    raise SystemExit('pre-existing raw evidence')

command = ['python', '-X', 'utf8', str(DRIVER), '--execute']
started = iso_now()
started_mono = time.monotonic()
returncode = None
timed_out = False
exception_text = None
with STDOUT.open('wb') as stdout_handle, STDERR.open('wb') as stderr_handle:
    try:
        completed = subprocess.run(command, cwd=str(ROOT), stdout=stdout_handle, stderr=stderr_handle, timeout=960, check=False)
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exception_text = f'{type(exc).__name__}: {exc}'
    except Exception as exc:
        exception_text = f'{type(exc).__name__}: {exc}'
finished = iso_now()
elapsed = time.monotonic() - started_mono
free_after = shutil.disk_usage(ROOT).free
stdout_text = STDOUT.read_text(encoding='utf-8', errors='replace') if STDOUT.exists() else ''
try:
    stdout_json = json.loads(stdout_text.strip().splitlines()[-1]) if stdout_text.strip() else None
except Exception:
    stdout_json = None
runtime_names = ['batch-report.json','source-map.json','sanitized-summary.json','progress.json','execution-plan.json','execution-input-bindings.json']
receipt = {
    'schema': 'wow-recovery.gallery-late-rest10a-parent-execution-receipt.v1',
    'batch_id': 'WAYBACK-GALLERY-LATE-REST10A-20261019',
    'go_path': rel(GO),
    'go_sha256': sha(GO),
    'go_fields': {'accepted': go_data.get('accepted'), 'root_go': go_data.get('root_go'), 'target_count': go_data.get('target_count'), 'max_requests': go_data.get('max_requests'), 'max_seconds': go_data.get('max_seconds'), 'max_body_bytes': go_data.get('max_body_bytes'), 'index_only': go_data.get('index_only'), 'network_deadline_utc': go_data.get('network_deadline_utc')},
    'input_bindings_at_start': expected,
    'command': command,
    'cwd': str(ROOT),
    'outer_timeout_seconds': 960,
    'started_utc': started,
    'finished_utc': finished,
    'elapsed_seconds': elapsed,
    'returncode': returncode,
    'timed_out': timed_out,
    'exception': exception_text,
    'stdout': {'path': rel(STDOUT), 'bytes': STDOUT.stat().st_size if STDOUT.exists() else 0, 'sha256': sha(STDOUT) if STDOUT.exists() else None, 'last_json': stdout_json},
    'stderr': {'path': rel(STDERR), 'bytes': STDERR.stat().st_size if STDERR.exists() else 0, 'sha256': sha(STDERR) if STDERR.exists() else None},
    'disk': {'floor_bytes': floor, 'free_before_bytes': free_before, 'free_after_bytes': free_after, 'floor_passed_before': free_before >= floor, 'floor_passed_after': free_after >= floor},
    'runtime_outputs': {name: {'path': rel(OUT/name), 'exists': (OUT/name).exists(), 'bytes': (OUT/name).stat().st_size if (OUT/name).exists() else 0, 'sha256': sha(OUT/name) if (OUT/name).exists() else None} for name in runtime_names},
    'raw_evidence_files': files_under(raw),
    'retry_count': 0,
    'network_status_mutated_by_parent_wrapper': False,
}
RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'returncode': returncode, 'timed_out': timed_out, 'elapsed_seconds': elapsed, 'receipt': rel(RECEIPT), 'receipt_sha256': sha(RECEIPT)}, ensure_ascii=False))
if timed_out or exception_text or returncode not in (0,):
    raise SystemExit(1)

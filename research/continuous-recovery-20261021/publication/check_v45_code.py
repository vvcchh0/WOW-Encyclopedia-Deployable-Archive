"""Run the checks affected by the combined v45 export and bind reviewed code."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-v45-code-acceptance.json'
assert not OUT.exists()
modules = [
    'tests.test_github_pages_export', 'tests.test_related_talent_pages',
    'tests.test_source16_layout_pages', 'tests.test_source16_layout_compat',
    'tests.test_battlegrounds_historical_entry', 'tests.test_historical_exhibits',
]
command = [sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', '-q', *modules]
started = datetime.now(timezone.utc).isoformat()
process = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=180)
log = PUB / 'v45-code-tests.log'
assert not log.exists()
log.write_bytes(process.stdout + process.stderr)
assert process.returncode == 0, log
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = json.loads((PUB / 'root-v44-code-acceptance.json').read_bytes())
paths = {item['path'] for item in old['code_bindings']} | {
    'tools/source16_layout_compat.py', 'tests/test_source16_layout_compat.py',
    'tests/test_source16_layout_pages.py', 'tests/test_historical_exhibits.py',
}
receipt = {
    'schema': 'wow-root-code-acceptance/v1', 'accepted': True,
    'reviewed_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'related_icons_historical_contest_and_layout_reuse_reviewed_pending_export_browser',
    'code_bindings': [{'path': p, 'sha256': sha(ROOT / p)} for p in sorted(paths)],
    'prior_code_acceptance': 'research/continuous-recovery-20261021/publication/root-v44-code-acceptance.json',
    'prior_code_acceptance_sha256': sha(PUB / 'root-v44-code-acceptance.json'),
    'tests': {
        'command': command, 'started_utc': started,
        'finished_utc': datetime.now(timezone.utc).isoformat(),
        'returncode': process.returncode, 'log': log.relative_to(ROOT).as_posix(),
        'log_sha256': sha(log), 'modules': modules,
    },
    'changes': [
        'Ten accepted target routes resolve to existing canonical image objects without copying payloads or emitting HTML aliases',
        'Two page records and top-level provenance describe layout compatibility separately from target capture evidence',
        'Historical contest replacement consumes the complete closing anchor and preserves neighbouring anchors',
        '986 separately attributed later related icons and all 2008 talent scripts/data retained',
    ],
    'prior_test_invocation': 'Module-style execution initially exposed a fixture import path error in three related-icon tests; only test import setup changed, and the four affected tests passed on rerun.',
    'new_original_2008_images': 0, 'browser_export_acceptance_pending': True,
}
OUT.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(process.stdout.decode('utf-8', errors='replace') + process.stderr.decode('utf-8', errors='replace'))
print(json.dumps({'accepted': True, 'code_binding_count': len(paths), 'acceptance_sha256': sha(OUT)}))

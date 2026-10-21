"""Run the affected export/loader checks using workspace-local temp space."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB/'root-v46-code-acceptance.json'
assert not OUT.exists()
assert shutil.disk_usage(ROOT).free >= 11005853696
temporary = ROOT/'.scratch/test-temp-20261021'
temporary.mkdir(exist_ok=True)
env = os.environ.copy()
env.update({key:str(temporary) for key in ('TMP','TEMP','TMPDIR')})
modules = [
    'tests.test_talent_box_layout_pages', 'tests.test_related_talent_ui_pages',
    'tests.test_talent_box_layout', 'tests.test_related_talent_ui',
    'tests.test_source16_layout_pages', 'tests.test_github_pages_export',
]
command = [sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', '-v', *modules]
started = datetime.now(timezone.utc).isoformat()
process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=180)
log = PUB/'v46-code-tests.log'
assert not log.exists()
log.write_bytes(process.stdout+process.stderr)
print((process.stdout+process.stderr).decode('utf-8', errors='replace')[-8000:])
assert process.returncode == 0, log
assert b'skipped=' not in process.stderr
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = json.loads((PUB/'root-v45-code-acceptance.json').read_bytes())
paths = {r['path'] for r in old['code_bindings']} | {
    'tools/related_talent_ui.py', 'tests/test_related_talent_ui.py',
    'tests/test_related_talent_ui_pages.py', 'tools/talent_box_layout.py',
    'tests/test_talent_box_layout.py', 'tests/test_talent_box_layout_pages.py',
}
OUT.write_text(json.dumps({
    'schema':'wow-root-code-acceptance/v1', 'accepted':True,
    'reviewed_utc':datetime.now(timezone.utc).isoformat(),
    'scope':'six_raw_related_ui_pngs_and_eight_same_site_points_box_route_reuses',
    'code_bindings':[{'path':p,'sha256':sha(ROOT/p)} for p in sorted(paths)],
    'prior_code_acceptance':'research/continuous-recovery-20261021/publication/root-v45-code-acceptance.json',
    'prior_code_acceptance_sha256':sha(PUB/'root-v45-code-acceptance.json'),
    'tests':{'command':command,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'returncode':process.returncode,'log':log.relative_to(ROOT).as_posix(),'log_sha256':sha(log),'modules':modules,'count':55,'skipped':0,'temp_directory':temporary.relative_to(ROOT).as_posix()},
    'prior_attempt':'The first 55-check invocation used the default C-drive temporary directory, which had only about55MB free. Export preflight rejected fixtures before output. This rerun changes process-local temp paths to D without modifying production disk guards or global settings.',
    'new_original_2008_images':0, 'browser_export_acceptance_pending':True,
}, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'accepted':True,'test_count':55,'code_binding_count':len(paths),'receipt_sha256':sha(OUT)}))

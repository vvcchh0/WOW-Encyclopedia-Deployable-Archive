"""Root's offline review of the single exact captured redirect probe."""
import hashlib
import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
DIR = RUN / 'network/karazhan-observed-redirect-probe-v1'
OUT = RUN / 'publication/root-karazhan-observed-redirect-probe-batch1-plan-acceptance.json'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert not OUT.exists()
pins = {
    'karazhan_redirect_probe.py': 'ee02d8526e60aee8257f7c79f1d3710db2da62fbb756996659b9e0116168bd06',
    'plan.json': '142756f3982dda0ac24915ffb855c70d21367a9dffcfb1c8ac759b49a4404b08',
    'input-bindings.json': '5d85af70e00f3540aae5adef947660c836d86791193709ae410e7a0cb17f2b49',
    'fixture-results.json': '008f829c696a7b29eb141566eaa951be22932ed0c7df8048b171425da33f826c',
}
for name, digest in pins.items():
    assert sha(DIR / name) == digest, name
spec = importlib.util.spec_from_file_location('root_redirect_probe_review', DIR / 'karazhan_redirect_probe.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
plan = m.read_json(DIR / 'plan.json')
m.validate_plan(plan, DIR / 'plan.json')
bindings = m.read_json(DIR / 'input-bindings.json')
for value in bindings.values():
    if isinstance(value, dict) and 'path' in value and 'sha256' in value:
        p = ROOT / value['path']
        assert p.is_file() and sha(p) == value['sha256']
        assert p.stat().st_size == value['bytes']
assert not (DIR / 'output').exists()
m.FIXTURE_RESULTS_PATH = RUN / 'publication/root-karazhan-redirect-probe-fixtures.json'
assert not m.FIXTURE_RESULTS_PATH.exists()
fixtures = m.run_fixtures(DIR / 'plan.json')
assert fixtures['network_requests'] == 0 and fixtures['all_passed']
assert len(fixtures['cases']) == 10
free = shutil.disk_usage(ROOT).free
assert free >= 11005853696
receipt = {
    'schema': 'wow-recovery.root-karazhan-redirect-probe-plan-acceptance.v1',
    'accepted': True,
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'plan_sha256': pins['plan.json'],
    'bindings_sha256': pins['input-bindings.json'],
    'probe_sha256': pins['karazhan_redirect_probe.py'],
    'root_fixture_sha256': sha(m.FIXTURE_RESULTS_PATH),
    'independent_offline_fixtures_passed': 10,
    'network_requests': 0,
    'candidate_count': 1,
    'exact_request_url': plan['candidates'][0]['request_url'],
    'policy': plan['policy'],
    'disk_free_bytes': free,
    'review': 'Pinned exact observed replay only; shared accepted curl and budget helpers; no redirect following; raw Location remains private and public destination omits query/userinfo; any image remains pending exact source-index acceptance.',
}
OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'accepted': True, 'path': str(OUT.relative_to(ROOT)), 'sha256': sha(OUT), 'fixtures': 10}))

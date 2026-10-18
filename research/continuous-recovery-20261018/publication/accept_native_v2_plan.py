"""Root review of the fixed twelve-target native replay probe; no HTTP."""
import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
NET = RUN / 'network/native-replay47-v2'
PLAN = NET / 'batch-01/plan.json'
OUT = PUB / 'root-native-replay47-v2-batch1-plan-acceptance.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text(encoding='utf-8'))
assert not OUT.exists(), 'Preserve completed acceptance'
pins = {
    NET/'native_replay47_driver.py': '18fae133137093651665036acbd7157eead446b4ef330a9f59889700f76ad920',
    NET/'prepare_native_replay47.py': '1904f740d2315c413c6c66394254b563e56422e4b160710b63562a2d3bee3bb2',
    PLAN: '31f3e2e451b3c9b7025ae44164092bfd22668caf395475652ace2a6552b1bc1d',
    NET/'batch-01/input-bindings.json': '1946bdb5b72d2b3e3ec75cc625a789d529f7c2bf04e60e4bb9480fb45963a20c',
    NET/'fixtures/native-replay47-fixtures.json': 'ee05474abd8650b32b729cdf214f31556f6e3fa8669c12525fa4e0debf206a82',
    PUB/'native-karazhan-unknown47-queue.json': '29b21d74f3253259a09be5d489291db12cf52782ce89b5a19c417817a8ea63cc',
}
for p, expected in pins.items():
    assert sha(p) == expected, str(p)
spec = importlib.util.spec_from_file_location('root_native_v2', NET/'native_replay47_driver.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
plan, bindings, v3_path, live = module.load_plan(PLAN)
policy = plan['policy']
for k,v in {'proxy':'http://127.0.0.1:7890','direct_connect_timeout_seconds':4.0,
            'direct_max_seconds':4.0,'proxy_connect_timeout_seconds':8.0,
            'proxy_max_seconds':20.0,'retry_after_honored':True,
            'transport_policy':'batch_after_direct_failure','inherited_failure_tail':0}.items():
    assert policy[k] == v, k
source_checks = 0
for item in plan['candidates']:
    for ref in [item['source_page_context']['source_page'], *item['source_page_context']['js_rule_evidence']]:
        p=ROOT/ref['path']
        assert sha(p)==ref['sha256'], ref['path']
        assert ref.get('literal', ref.get('quote')) in p.read_text(encoding='utf-8',errors='replace').splitlines()[ref['line']-1]
        source_checks += 1
assert not (PLAN.parent/'output').exists()
assert shutil.disk_usage(ROOT).free >= 11005853696
fixture_dir = PUB/'native-v2-independent-fixtures'
assert not fixture_dir.exists()
fixture_dir.mkdir()
module.FIXTURE_PATH=fixture_dir/'native-replay47-fixtures.json'
shutil.copyfile(NET/'fixtures/native-replay47-fixtures.json',module.FIXTURE_PATH)
with contextlib.redirect_stdout(io.StringIO()):
    fixtures = module.run_fixtures(PLAN)
assert fixtures['all_passed'] and fixtures['network_requests']==0 and len(fixtures['cases'])==11
fixture_receipt=fixture_dir/'native-replay47-fixture-results.json'
report = {
    'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
    'plan_sha256':sha(PLAN),'bindings_sha256':sha(NET/'batch-01/input-bindings.json'),
    'driver_sha256':sha(NET/'native_replay47_driver.py'),
    'source_reference_checks':source_checks,'independent_fixtures':11,
    'fixture_receipt':str(fixture_receipt.relative_to(ROOT)).replace('\\','/'),
    'fixture_receipt_sha256':sha(fixture_receipt),'live_bindings':live,
    'scope':'One batch: first twelve frozen transport-unknown replay URLs; 14 attempts, 240 seconds, 16 MiB. No redirects or CDX. Image response remains pending source-index acceptance.',
    'reviewed_repairs':['Remaining-time and remaining-byte caps passed to transport',
        'Deadline gate repeated after cadence wait','Partial HTTP transfer keeps failure tail',
        'TimeoutExpired persisted as an attempted transfer','Live source/control/tail checked before dispatch',
        'Exact queue membership enforced','Raw Location and transport paths remain local'],
    'network_requests':0,'accepted_images':[],'disk_free_bytes':shutil.disk_usage(ROOT).free,
}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'path':str(OUT.relative_to(ROOT)),'sha256':sha(OUT),'fixtures':11,'source_checks':source_checks}))

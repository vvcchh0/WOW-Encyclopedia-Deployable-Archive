"""Root gate for non-overlapping slices of the frozen native replay queue."""
import argparse
import ast
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode=True
parser=argparse.ArgumentParser()
parser.add_argument('--batch',type=int,required=True)
parser.add_argument('--plan-sha',required=True)
parser.add_argument('--bindings-sha',required=True)
parser.add_argument('--source-sha',required=True)
args=parser.parse_args()
assert args.batch in {2,3,4}
ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'research/continuous-recovery-20261018';PUB=RUN/'publication'
NET=RUN/'network/native-replay47-v3'
PLAN=NET/f'batch-{args.batch:02d}/plan.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
driver=NET/'native_replay47_driver.py'
assert sha(driver)=='84656d15036405ad6813702a4f7a0086f9d1838c2a3323d5022c84a67feb7c83'
assert sha(NET/'prepare_native_replay47.py')=='8f9adb545946487e9d4140c4b9d3d848547c77fce599191efa6600916cdea0df'
assert sha(PLAN)==args.plan_sha
assert sha(PLAN.parent/'input-bindings.json')==args.bindings_sha
old=RUN/'network/native-replay47-v2/native_replay47_driver.py'
assert sha(old)=='18fae133137093651665036acbd7157eead446b4ef330a9f59889700f76ad920'
normalized=old.read_text().replace('native-replay47-v2','native-replay47-v3').replace('_v3_v2','_v3_v3').replace('.v2','.v3').replace(' v2',' v3')
before={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(normalized).body if isinstance(n,ast.FunctionDef)}
after={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(driver.read_text()).body if isinstance(n,ast.FunctionDef)}
changes=[n for n in before if before[n]!=after[n]]
assert set(changes)=={'validate_exact_queue_membership','run_fixtures'},changes
spec=importlib.util.spec_from_file_location('root_native_v3',driver)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
plan,bindings,v3,live=module.load_plan(PLAN)
assert live['source_sha256']==args.source_sha
status=read(RUN/'status.json')
assert status.get('network_resume_gate_passed') is True
source=read(ROOT/live['source_path'])
assert source.get('resume_gate_passed') is not False
start=1+(args.batch-1)*12;end=min(start+12,48)
assert plan['selection']['selected_ranks']==list(range(start,end))
assert len(plan['candidates'])==end-start
out=ROOT/plan['root_plan_acceptance']['path'];assert not out.exists()
seen=set()
for p in PUB.glob('root-native-*-source-acceptance.json'):
    receipt=read(p)
    if receipt.get('accepted'):
        seen.update(r['target_id'] for r in receipt.get('rows',[]))
assert not seen.intersection(c['target_id'] for c in plan['candidates'])
for candidate in plan['candidates']:
    for ref in [candidate['source_page_context']['source_page'],*candidate['source_page_context']['js_rule_evidence']]:
        p=ROOT/ref['path'];assert sha(p)==ref['sha256']
        assert ref.get('literal',ref.get('quote')) in p.read_text(encoding='utf-8',errors='replace').splitlines()[ref['line']-1]
assert not (PLAN.parent/'output').exists()
fixture_bind=None
if args.batch==2:
    folder=PUB/'native-v3-independent-fixtures';assert not folder.exists();folder.mkdir()
    module.FIXTURE_PATH=folder/'native-replay47-fixtures.json'
    shutil.copyfile(NET/'fixtures/native-replay47-fixtures.json',module.FIXTURE_PATH)
    with contextlib.redirect_stdout(io.StringIO()):result=module.run_fixtures(PLAN)
    assert result['all_passed'] and result['network_requests']==0 and len(result['cases'])==14
    p=folder/'native-replay47-fixture-results.json'
    fixture_bind={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'cases':14}
assert shutil.disk_usage(ROOT).free>=11005853696
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
    'plan_sha256':sha(PLAN),'bindings_sha256':sha(PLAN.parent/'input-bindings.json'),
    'driver_sha256':sha(driver),'latest_source_sha256':args.source_sha,
    'selected_ranks':list(range(start,end)),'prior_observed_targets_excluded':len(seen),
    'unchanged_execution_policy_ast':True,'changed_functions_after_schema_normalization':changes,
    'independent_fixture_receipt':fixture_bind,'live_bindings':live,
    'network_requests':0,'accepted_images':[],
    'scope':'One disjoint frozen queue slice; identical bounded v2 dispatch/classification policy. No image accepted by this replay-only probe.'}
out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'path':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'ranks':[start,end-1]}))

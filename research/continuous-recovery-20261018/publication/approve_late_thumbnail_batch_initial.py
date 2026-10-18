"""Root gate: date-only driver clone, observed redirects, independent late-day fixtures."""
import argparse
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode=True
parser=argparse.ArgumentParser();parser.add_argument('--batch',type=int,required=True)
parser.add_argument('--plan-sha',required=True);parser.add_argument('--bindings-sha',required=True)
args=parser.parse_args();assert args.batch in {1,2}
ROOT=Path(__file__).resolve().parents[3];RUN=ROOT/'research/continuous-recovery-20261018';PUB=RUN/'publication'
NET=RUN/'network/late-thumbnails12-v1';PLAN=NET/f'batch-{args.batch:02d}/plan.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_bytes())
old=RUN/'network/reusable-image-driver-v3/reusable_image_driver.py';driver=NET/'reusable_image_driver.py'
assert sha(old)=='4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955'
assert sha(driver)=='374bcc0f8008215d09eea6203cf71a7b2f49361120540d8e01c1628c443c0328'
expected=old.read_text().replace('POLICY_FROM_TS = "20000101000000"','POLICY_FROM_TS = "20130612000000"').replace('POLICY_TO_TS = "20080512210044"','POLICY_TO_TS = "20130612235959"')
assert driver.read_text()==expected,'Only the two date constants may differ'
assert sha(NET/'prepare_late_thumbnails12.py')=='64a19a7eb4abf8797eeadfa65a94e05e5b27806a66129f04e7d2eb1e61df88a2'
assert sha(PLAN)==args.plan_sha and sha(PLAN.parent/'input-bindings.json')==args.bindings_sha
queue_path=PUB/'native-observed-late-thumbnails12-queue.json'
assert sha(queue_path)=='7fbe5026cce61fcf6e4b3e9028d3009b6a3c3d3e9be28c73ecbb0510283ad36e'
queue=read(queue_path);rows=queue['rows'][(args.batch-1)*6:args.batch*6]
plan=read(PLAN);assert len(rows)==plan['candidate_count']==len(plan['candidates'])==6
assert [c['original'] for c in plan['candidates']]==[r['original'] for r in rows]
for r,c in zip(rows,plan['candidates']):
    assert c['source_evidence']==r['source_evidence']
    receipt=ROOT/r['observed_source_receipt'];assert sha(receipt)==r['observed_source_receipt_sha256']
    assert any(x.get('original')==r['original'] and x.get('observed_redirect_url')==r['observed_replay_url'] for x in read(receipt)['rows'])
    assert c['cdx_mode']=='fresh' and not c.get('known_positive_cache_rows')
status=read(RUN/'status.json');assert status['network_resume_gate_passed'] is True
assert not (PLAN.parent/'output').exists()
spec=importlib.util.spec_from_file_location('root_late_thumbnail_driver',driver)
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
module.configure_from_plan(PLAN);module.load_and_validate_inputs()
adaptation=PUB/'root-late-thumbnail-driver-fixture-adaptation-acceptance.json'
if args.batch==1:
    assert not adaptation.exists()
    tree=ast.parse(driver.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run_fixtures')
    original_fixture=ast.get_source_segment(driver.read_text(),fn)
    adapted=original_fixture
    replacements={'20070101000000':'20130612010000','20070101000001':'20130612010001',
        '200701010000{i:02d}':'201306120100{i:02d}','20070201000000':'20130612020000',
        '20070301000000':'20130612030000','20070401000000':'20130612040000','20080101000000':'20130612050000'}
    for before,after in replacements.items():
        assert before in adapted,before;adapted=adapted.replace(before,after)
    # Only synthetic fixture timestamps change. The executed download module file is untouched.
    fixture_source=PUB/'late-thumbnail-independent-fixtures.py'
    fixture_source.write_text(adapted+'\n',encoding='utf-8')
    namespace=dict(module.__dict__);exec(compile(adapted,str(fixture_source),'exec'),namespace)
    fixture_dir=NET/'root-fixtures';assert not fixture_dir.exists();fixture_dir.mkdir()
    fixture_output=fixture_dir/'adapted-fixture-results.json'
    result=namespace['run_fixtures'](fixture_output)
    assert result['all_passed'] and len(result['cases'])==32
    checker=RUN/'integration/late-thumbnail-source-checker/accept_late_thumbnail_batch.py'
    assert sha(checker)=='36b6c352a29cae5e3b1b028eee152511448438f976dbbacf36d693c792a438e5'
    checker_spec=importlib.util.spec_from_file_location('root_late_source_checker',checker)
    checker_module=importlib.util.module_from_spec(checker_spec);checker_spec.loader.exec_module(checker_module)
    q=checker_module.load_native_queue(queue_path)
    allow=checker_module.load_native_allowlist([r['path'] for r in q['source_receipt_bindings']])
    checker_module.validate_queue_receipts(q,allow);checker_module.validate_plan_scope(plan,allow)
    assert len(allow['allowed_identities'])==12
    receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
        'new_driver_sha256':sha(driver),'frozen_driver_sha256':sha(old),'date_constants_only_difference':True,
        'unadapted_fixtures':'29/32; three old2007 synthetic timestamps fall outside the new2013day',
        'adapted_fixture_cases':32,'fixture_source_sha256':sha(fixture_source),
        'fixture_receipt':fixture_output.relative_to(ROOT).as_posix(),'fixture_receipt_sha256':sha(fixture_output),
        'fixture_timestamp_replacements':replacements,'checker_sha256':sha(checker),
        'queue_sha256':sha(queue_path),'observed_originals':12,'network_requests':0,
        'historical_window':'late2013_native_thumbnail_supplement'}
    adaptation.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
else:
    assert read(adaptation)['accepted'] and read(adaptation)['new_driver_sha256']==sha(driver)
# Preserve all generic exact-plan checks; only the explicit date window and accepted driver receipt differ.
generic=PUB/'accept_exact_plan.py';late_generic=PUB/'accept_late_thumbnail_exact_plan.py'
text=generic.read_text().replace('policy["from"] == "20000101000000" and policy["to"] == "20080512210044"',
    'policy["from"] == "20130612000000" and policy["to"] == "20130612235959"').replace('root-v3-driver-fixture-adaptation-acceptance.json','root-late-thumbnail-driver-fixture-adaptation-acceptance.json')
if late_generic.exists():assert late_generic.read_text()==text
else:late_generic.write_text(text,encoding='utf-8')
selected=PUB/f'late-thumbnails12-batch{args.batch}-selected-originals.json';assert not selected.exists()
selected.write_text(json.dumps([r['original'] for r in rows],indent=2)+'\n',encoding='utf-8')
out=PUB/f'root-late-thumbnails12-batch{args.batch}-plan-acceptance.json';assert not out.exists()
subprocess.run([sys.executable,'-B','-X','utf8',str(late_generic),'--plan',PLAN.relative_to(ROOT).as_posix(),
    '--originals',selected.relative_to(ROOT).as_posix(),'--output',out.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
print(json.dumps({'accepted':True,'path':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'selected':6}))

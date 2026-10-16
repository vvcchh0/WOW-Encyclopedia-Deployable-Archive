"""Review the one-target late adapter and bind the latest accepted tail."""
import ast,copy,hashlib,importlib.util,json,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';D=B/'network/aug27-same-day-late11';Q=B/'network/root-late11-review';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def write(p,d):assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
driver=D/'late11_image_driver.py';base=B/'network/reusable-image-driver-v2/reusable_image_driver.py'
assert sha(driver)=='f8f25ce4eca097ed1739300b9cd34b183e6de94e8e93c7d7476abd1289bbff93'
def functions(p):return {x.name:ast.dump(x) for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef)}
a,c=functions(base),functions(driver);changed=[n for n in a if a[n]!=c[n]]
assert set(changed)=={'configure_from_plan','execute','load_and_validate_inputs','persist_accepted_payload','run_fixtures','validate_replay'}
core=['_curl_request','parse_headers','parse_cdx','decoded_payload','image_validation','_dispatch_gate_for_state','_policy_hard_bounds','initial_state']
assert all(a[n]==c[n] for n in core)
def nested_request(p):return ast.dump(next(x for x in ast.walk(ast.parse(p.read_text())) if isinstance(x,ast.FunctionDef) and x.name=='request'))
assert nested_request(base)==nested_request(driver)
m=load('root_late11',driver);m.configure_from_plan(D/'plan.json');pending,_=m.load_and_validate_inputs()
f=m.run_fixtures(Q/'pending-core-fixtures.json');assert f['all_passed'] and len(f['tests'])==32
g=load('root_late11_guard_fixture',D/'fixture_late11.py');g.OUT_PATH=Q/'pending-guard-fixtures.json';assert g.main()==0
rejected=[]
for name,mutate in [('wrong_origin',lambda p:p['candidates'][0].update(original='http://example.invalid/a.jpg')),('two_targets',lambda p:p['candidates'].append(copy.deepcopy(p['candidates'][0]))),('wider_time',lambda p:p['late_supplement_guard']['late_window'].update(to='20080513000000')),('automatic_redirect',lambda p:p['late_supplement_guard'].update(automatic_redirects=1))]:
    p=copy.deepcopy(pending);mutate(p)
    try:m._validate_late_supplement_plan(p)
    except RuntimeError:rejected.append(name)
assert len(rejected)==4
try:m.execute()
except RuntimeError as e:assert 'gated' in str(e)
else:raise AssertionError('pending plan executed')
prior_path=B/'publication/root-aug-cached19-source-acceptance.json';prior=json.loads(prior_path.read_bytes());assert prior['accepted'] and prior['failure_streak_end']==0 and prior['source_responses']==1
control_path=B/'publication/root-control03-acceptance.json';control=json.loads(control_path.read_bytes());assert control['accepted'] and control['resume_gate_passed'] and control['control_final_streak']==0
ready=copy.deepcopy(pending);ready['execution_status']='prepared_root_tail_bound';ready['policy']['prior_failure_tail']=0
ready['previous_batch']={'status':'A_root_accepted_tail0','prior_failure_tail':0,'control_gate_receipt_path':control_path.relative_to(R).as_posix(),'control_gate_receipt_sha256':sha(control_path),'latest_tail_receipt_path':prior_path.relative_to(R).as_posix(),'latest_tail_receipt_sha256':sha(prior_path),'note':'A successful source response ends at zero. CONTROL03 followed the last stopped batch; no later five-failure/429/503 batch has occurred.'}
for name,p in [('latest_A_root_source',prior_path),('last_control_after_stopped_batch',control_path)]:
    b={'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size};ready['input_bindings'][name]=b;ready['source_bindings'][name]=b
ready['control_gate']={'status':'latest_A_root_accepted_tail0','execution_go_required':True};ready['tail_bound_utc']=datetime.now(timezone.utc).isoformat()
plan=D/'execution/plan.json';write(plan,ready)
write(plan.with_name('input-bindings.json'),{'plan_sha256':sha(plan),'driver_sha256':sha(driver),'source_bindings':ready['source_bindings']})
m.configure_from_plan(plan);checked,_=m.load_and_validate_inputs();f=m.run_fixtures(Q/'ready-core-fixtures.json');assert f['all_passed'] and len(f['tests'])==32
assert m.PRIOR_FAILURE_TAIL==0 and m.MAX_ATTEMPTS==6 and m.WINDOW_SECONDS==180 and len(checked['candidates'])==1
receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'driver_sha256':sha(driver),'execution_plan_path':plan.relative_to(R).as_posix(),'execution_plan_sha256':sha(plan),'starting_failure_tail':0,'latest_tail_receipt_sha256':sha(prior_path),'unchanged_core_functions':core,'core_fixtures_pending':32,'core_fixtures_ready':32,'late_guard_fixtures':9,'root_tamper_rejections':rejected,'pending_execute_rejected':True,'actual_capture_must_be_late_supplement':True,'adoption_requires_pre_anchor_digest_match':'MLUKMD2MO3CNVZGT2PCCNNXF7RDKJAA4'}
write(B/'publication/root-late11-code-plan-acceptance.json',receipt);print(json.dumps(receipt))

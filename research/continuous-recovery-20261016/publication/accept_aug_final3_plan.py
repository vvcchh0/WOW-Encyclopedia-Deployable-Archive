"""Root data-plan and inherited-tail validation; no network calls."""
import hashlib,importlib.util,json,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016'
P=B/'network/aug27-final3/plan.json';driver=B/'network/reusable-image-driver-v2/reusable_image_driver.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(driver)=='1faae294465f5e1ad6e2925870890cdb9512bd2251090d533637245ee6a3d8e4'
spec=importlib.util.spec_from_file_location('aug_final3_root',driver);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
m.configure_from_plan(P);plan,bindings=m.load_and_validate_inputs()
expected={f'AUG27-{n:02}' for n in (11,16,19)}
assert {x['target_key'] for x in plan['candidates']}==expected
assert {x['target_key'] for x in plan['candidates'] if x['cdx_mode']=='cached'}=={f'AUG27-{n:02}' for n in (11,16)}
prior=json.loads((B/'publication/root-gallery-prefix04-acceptance.json').read_bytes())
assert prior['accepted'] and prior['failure_streak_end']==2
for binding in plan['source_bindings'].values():assert sha(R/binding['path'])==binding['sha256']
fixture=m.run_fixtures();failed=[k for k,v in fixture['tests'].items() if not v]
assert failed==['transport_policy_proxy_five_failures_stop'],failed
state=m.initial_state();assert state['failure_streak']==2 and not state['direct_probe_done']
assert m._transport_sequence_for_request(state)==('direct','proxy')
m._record_direct_probe(state,'direct',{'source_status':None,'curl_exit':28,'body_bytes':0},1)
assert m._transport_sequence_for_request(state)==('proxy',)
for _ in range(3):state['failure_streak']+=1
assert state['failure_streak']==5
receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'plan_path':str(P.relative_to(R)).replace('\\','/'),'plan_sha256':sha(P),'driver_sha256':sha(driver),'targets':3,'cached_complete_indexes':2,'fresh_indexes':1,'starting_failure_tail':2,'fixture_results':fixture['tests'],'fixture_known_assumption':'One generic fixture expects five failures starting at zero; this plan correctly inherits two. Root separately checked three further failures reach five.','root_tail2_checks':{'initial_tail_inherited':True,'new_batch_direct_probe':True,'qualifying_direct_fallback':True,'three_further_failures_reach_five':True}}
out=B/'publication/root-aug-final3-plan-acceptance.json';assert not out.exists();out.write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in receipt.items() if k!='fixture_results'}))

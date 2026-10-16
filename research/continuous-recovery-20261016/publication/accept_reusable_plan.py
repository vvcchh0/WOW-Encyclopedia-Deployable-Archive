"""Root offline review of one frozen-runner batch and its current source frontier."""
import argparse,hashlib,importlib.util,json,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--data',required=True);p.add_argument('--data-key',default='candidates');p.add_argument('--queue-prefix');p.add_argument('--starting-failures',required=True,type=int);p.add_argument('--tail-receipt',required=True);p.add_argument('--output',required=True);p.add_argument('--fixture-plan');a=p.parse_args()
    plan_path=R/a.plan;data_path=R/a.data;out=R/a.output;assert not out.exists();data=json.loads(data_path.read_bytes());items=data[a.data_key]
    if a.queue_prefix:items=[x for x in items if x['queue'].startswith(a.queue_prefix)]
    assert 1<=len(items)<=20
    driver=B/'network/reusable-image-driver-v2/reusable_image_driver.py';assert sha(driver)=='1faae294465f5e1ad6e2925870890cdb9512bd2251090d533637245ee6a3d8e4'
    spec=importlib.util.spec_from_file_location('root_reusable_batch',driver);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);m.configure_from_plan(plan_path);plan,_=m.load_and_validate_inputs()
    assert [x['original'] for x in plan['candidates']]==[x['original'] for x in items]
    tail_path=R/a.tail_receipt;tail=json.loads(tail_path.read_bytes());assert tail['accepted'] and tail['failure_streak_end']==a.starting_failures==m.PRIOR_FAILURE_TAIL
    bindings=list(plan['input_bindings'].values())
    for bound in [data_path,tail_path]:assert any(x['path']==bound.relative_to(R).as_posix() and x['sha256']==sha(bound) for x in bindings)
    production_sha=sha(plan_path)
    fixture_plan=R/a.fixture_plan if a.fixture_plan else None
    if fixture_plan:
        # The legacy default-port fixture requires a bare HTTP first candidate.
        # A synthetic fixture plan exercises that assumption without rewriting
        # any production HTTPS/:80 original. It is never executed.
        fixture_plan.resolve().relative_to(B/'network')
        m.configure_from_plan(fixture_plan);fp,_=m.load_and_validate_inputs()
        assert all(plan['policy'].get(k)==v for k,v in fp['policy'].items())
        assert len(fp['candidates']) in (1,len(plan['candidates'])) and fp['candidates'][0]['original'].startswith('http://www.worldofwarcraft.com/')
        if len(fp['candidates'])>1:
            assert [x['original'] for x in fp['candidates'][1:]]==[x['original'] for x in plan['candidates'][1:]]
    q=B/'network/root-plan-reviews'/f"{plan['batch_id']}-fixtures.json";assert not q.exists();fixture=m.run_fixtures(q);failed=[n for n,v in fixture['tests'].items() if not v]
    assert failed==(['transport_policy_proxy_five_failures_stop'] if a.starting_failures else []),failed
    if fixture_plan:
        m.configure_from_plan(plan_path);restored,_=m.load_and_validate_inputs()
        assert restored==plan and sha(plan_path)==production_sha
    state=m.initial_state();assert state['failure_streak']==a.starting_failures and not state['direct_probe_done'] and m._transport_sequence_for_request(state)==('direct','proxy')
    m._record_direct_probe(state,'direct',{'source_status':None,'curl_exit':28,'body_bytes':0},1);assert m._transport_sequence_for_request(state)==('proxy',)
    for _ in range(5-a.starting_failures):state['failure_streak']+=1
    assert state['failure_streak']==5
    receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'plan_path':plan_path.relative_to(R).as_posix(),'plan_sha256':sha(plan_path),'driver_sha256':sha(driver),'source_data_sha256':sha(data_path),'latest_tail_receipt_sha256':sha(tail_path),'starting_failure_tail':a.starting_failures,'candidate_count':len(items),'offline_fixture_count':len(fixture['tests']),'offline_fixture_passed':sum(fixture['tests'].values()),'known_zero_tail_fixture_assumption':bool(failed),'root_actual_tail_and_direct_fallback_checks':True,'root_fixture_path':q.relative_to(R).as_posix(),'root_fixture_sha256':sha(q)}
    if fixture_plan:receipt.update(synthetic_fixture_plan_sha256=sha(fixture_plan),synthetic_fixture_candidate_count=len(fp['candidates']),production_plan_revalidated_unchanged=True,fixture_boundary='Shared runner fixtures use a synthetic bare HTTP first candidate; all production originals, bindings, order and current failure tail were independently validated before and after.')
    out.resolve().relative_to(B/'publication');out.write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
if __name__=='__main__':main()

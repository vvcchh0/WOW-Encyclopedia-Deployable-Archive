"""Reconcile gallery plans with actual prefix03 attempts and source literals."""
import hashlib,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';L=B/'local-audit'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
oldreg=L/'gallery-prefix-registry-v3/gallery-prefix-registry-v3.json';oldplan=L/'gallery-wave4-plan/gallery-wave4-plan-v1.json'
reg=json.loads(oldreg.read_bytes());plan=json.loads(oldplan.read_bytes());report=json.loads((B/'network/gallery-prefix03/batch-report.json').read_bytes())
assert len(reg['coverage_rows'])==50 and len(plan['candidates'])==20
actual={x['prefix']:x for x in report['candidate_results']};corrections=[]
for c in plan['candidates']:
    evidence=c['source_evidence'];p=R/evidence['path'];assert sha(p)==evidence['sha256']
    lines=p.read_text().splitlines();assert evidence['addshots_literal'] in lines[evidence['addshots_line']-1]
    assert evidence['numShots_literal'] in lines[evidence['numShots_line']-1]
    assert c['prefix']=='http://www.worldofwarcraft.com'+evidence['directory_literal']
    q=parse_qs(urlsplit(c['query_url']).query);assert q['url']==[c['prefix']] and q['from']==['20000101000000'] and q['to']==['20080512210044'] and q['matchType']==['prefix'] and 'collapse' not in q
    prior=actual.get(c['prefix'])
    if prior:
        assert prior['rank'] in (6,7,8) and prior['attempts'] and all(a['source_status'] is None for a in prior['attempts'])
        c['existing_window_evidence']['status']='attempted_transport_unknown'
        c['existing_window_evidence']['actual_attempt_count']=len(prior['attempts'])
        c['existing_window_evidence']['actual_attempt_numbers']=[a['attempt'] for a in prior['attempts']]
        corrections.append({'gallery':c['gallery'],'attempts':len(prior['attempts']),'prior_status':'prepared_but_not_executed_for_this_prefix_after_rank5_stop','corrected_status':'attempted_transport_unknown'})
for row in reg['coverage_rows']:
    e=row['source_evidence'];p=R/e['path'];assert sha(p)==e['sha256']
    assert e['addshots_literal'] in p.read_text().splitlines()[e['addshots_line']-1]
    assert row['expected_direct_entities']==2*row['declared_slots']
    prefix='http://www.worldofwarcraft.com'+e['source_directory'];prior=actual.get(prefix)
    if prior and prior['rank'] in (6,7,8):
        row['coverage_status']='prefix03_attempted_transport_unknown'
        row['actual_prefix_windows'].append({'kind':'prefix03_attempted','window':{'from':'20000101000000','to':'20080512210044'},'status':'transport_unknown','complete_prefix_evidence':False,'actual_attempt_numbers':[a['attempt'] for a in prior['attempts']]})
assert len(corrections)==3 and sum(x['attempts'] for x in corrections)==5
assert sum(x['declared_slots'] for x in reg['coverage_rows'])==1684
assert sum(x['expected_direct_entities'] for x in reg['coverage_rows'])==3368
counts=Counter(x['coverage_class'] for x in reg['coverage_rows']);assert counts=={'reviewed_window_complete':29,'not_complete_or_unknown':21}
assert sum(bool(x['prewindow_gap']) for x in reg['coverage_rows'] if x['coverage_class']=='reviewed_window_complete')==24
now=datetime.now(timezone.utc).isoformat();amendment={'reviewed_utc':now,'by':'/root','reason':'Preserve the difference between attempted but unknown and never started. Three prefix03 targets had five actual failed requests.','superseded_registry_sha256':sha(oldreg),'superseded_plan_sha256':sha(oldplan),'corrections':corrections}
plan['schema']='wow-recovery.gallery-wave4-root-plan.v2';plan['root_amendment']=amendment
newplan=L/'gallery-wave4-plan-v2/gallery-wave4-plan-v2.json';write(newplan,plan)
reg['schema']='wow-recovery.gallery-prefix-root-registry.v4';reg['root_amendment']=amendment;reg['wave4_plan_binding']={'path':newplan.relative_to(R).as_posix(),'sha256':sha(newplan)}
newreg=L/'gallery-prefix-registry-v4/gallery-prefix-registry-v4.json';write(newreg,reg)
receipt={'checked_utc':now,'accepted':True,'network_requests':0,'groups':50,'slots':1684,'direct_image_targets':3368,'complete_limited_windows':29,'incomplete_or_unknown_groups':21,'earlier_window_gaps':24,'wave4_targets':20,'source_literals_checked':50,'root_corrections':corrections,'registry':{'path':newreg.relative_to(R).as_posix(),'sha256':sha(newreg)},'plan':{'path':newplan.relative_to(R).as_posix(),'sha256':sha(newplan)},'scope':'Index coverage and source-plan evidence only; no new payload recovery.'}
write(B/'publication/root-gallery-registry-v4-acceptance.json',receipt);print(json.dumps(receipt))

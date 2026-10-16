"""Reconcile the v5 directory ledger and the non-overlapping follow-up windows."""
import hashlib,json
from datetime import datetime,timezone,timedelta
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';L=B/'local-audit';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((L/'gallery-prefix-registry-v4/gallery-prefix-registry-v4.json').read_bytes());p=L/'gallery-prefix-registry-v5/gallery-prefix-registry-v5.json';new=json.loads(p.read_bytes())
actual=json.loads((B/'publication/root-gallery-prefix04-acceptance.json').read_bytes())
before={x['gallery'] for x in old['coverage_rows'] if x['coverage_class']=='reviewed_window_complete'};added={x['label'] for x in actual['results'] if x['valid_index']};current={x['gallery'] for x in new['coverage_rows'] if x['coverage_class']=='reviewed_window_complete'}
assert len(before)==29 and len(added)==14 and not before&added and current==before|added and len(current)==43
assert len(new['coverage_rows'])==50 and sum(x['declared_slots'] for x in new['coverage_rows'])==1684 and sum(x['expected_direct_entities'] for x in new['coverage_rows'])==3368
assert new['stats']['entity_audit_status_counts']=={'archive_404':79,'transport_unknown':47,'never_requested':3242}
full_path=L/'gallery-followup-plans/incomplete-prefixes-full-window-v1.json';early_path=L/'gallery-followup-plans/early-gaps-24-v1.json';full=json.loads(full_path.read_bytes());early=json.loads(early_path.read_bytes())
allgroups={x['gallery'] for x in new['coverage_rows']};assert {x['gallery'] for x in full['items']}==allgroups-current and len(full['items'])==7
oldrows={x['gallery']:x for x in old['coverage_rows']};expected_early={x['gallery'] for x in old['coverage_rows'] if x['gallery'] in before and x['prewindow_gap']};assert {x['gallery'] for x in early['items']}==expected_early and len(early['items'])==24
for item in full['items']+early['items']:
    e=item['source_evidence'];q=item['query_window'];source=R/e['path'];assert sha(source)==e['sha256'] and e['addshots_literal'] in source.read_text().splitlines()[e['addshots_line']-1]
    assert item['prefix']=='http://www.worldofwarcraft.com'+e['source_directory'] and q['from']=='20000101000000' and q['limit']==500 and q['matchType']=='prefix' and not q['collapse']
    if item in full['items']:assert q['to']=='20080512210044'
    else:
        assert q['to']==oldrows[item['gallery']]['prewindow_gap']['to']
        assert datetime.strptime(q['to'],'%Y%m%d%H%M%S')+timedelta(seconds=1)==datetime.strptime(item['earliest_complete_prior_window_start'],'%Y%m%d%H%M%S')
receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'groups':50,'slots':1684,'direct_image_targets':3368,'limited_window_complete':43,'full_window_followup_targets':7,'earlier_gap_followup_targets':24,'early_batches':[20,4],'registry_sha256':sha(p),'incomplete_plan_sha256':sha(full_path),'early_gap_plan_sha256':sha(early_path),'scope':'Source directory and actual queried-window coverage; no new image payload recovery.'}
out=B/'publication/root-gallery-followups-acceptance.json';assert not out.exists();out.write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))

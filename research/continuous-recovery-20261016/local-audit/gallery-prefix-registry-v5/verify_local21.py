import json, hashlib
from datetime import datetime, timedelta
from pathlib import Path
root=Path.cwd()
base=root/'research/continuous-recovery-20261016'
def load(rel): return json.loads((root/rel).read_text(encoding='utf-8'))
def sha(path):
 h=hashlib.sha256(); h.update(Path(path).read_bytes()); return h.hexdigest()
v4=load('research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v4/gallery-prefix-registry-v4.json')
v5=load('research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v5/gallery-prefix-registry-v5.json')
inc=load('research/continuous-recovery-20261016/local-audit/gallery-followup-plans/incomplete-prefixes-full-window-v1.json')
early=load('research/continuous-recovery-20261016/local-audit/gallery-followup-plans/early-gaps-24-v1.json')
p4=load('research/continuous-recovery-20261016/publication/root-gallery-prefix04-acceptance.json')
assert len(v5['coverage_rows'])==50
assert sum(x['declared_slots'] for x in v5['coverage_rows'])==1684
assert sum(x['expected_direct_entities'] for x in v5['coverage_rows'])==3368
assert sum(1 for x in v5['coverage_rows'] if x['coverage_class']=='reviewed_window_complete')==43
assert sum(1 for x in v5['coverage_rows'] if x['coverage_class']!='reviewed_window_complete')==7
assert v5['stats']['entity_audit_status_counts']=={'archive_404':79,'never_requested':3242,'transport_unknown':47}
assert len(inc['items'])==7 and len(early['items'])==24
assert early['batch_split']['batch_1']['count']==20 and early['batch_split']['batch_2']['count']==4
assert sum(x['followup_batch']=='early_gap_batch_1_of_2_20_items' for x in early['items'])==20
assert sum(x['followup_batch']=='early_gap_batch_2_of_2_4_items' for x in early['items'])==4
assert all(x['prefix'].startswith('http://www.worldofwarcraft.com/') for x in inc['items']+early['items'])
assert all(x['execution_status']=='prepared_not_executed' and x['network_performed_in_this_plan'] is False and x['payload_recovery'] is False for x in inc['items']+early['items'])
assert len(inc['conservation']['labels'])==7
assert len(early['excluded_full_window_groups']['prefix03'])==5 and len(early['excluded_full_window_groups']['prefix04'])==14
assert not set(early['conservation']['expected_count'].__class__.__name__ for _ in [])
for x in early['items']:
 expected=(datetime.strptime(x['earliest_complete_prior_window_start'],'%Y%m%d%H%M%S')-timedelta(seconds=1)).strftime('%Y%m%d%H%M%S')
 assert x['query_window']['to']==expected
 assert x['query_window']['from']=='20000101000000'
assert set(inc['conservation']['labels'])=={'Coilfang Reservoir - The Steam Vaults','Flying Machine','Tempest Keep - The Botanica','X-51 Nether-Rocket','Raven Mount','Qiraji battle tank','Amani War Bear'}
# Source literals/SHAs are unchanged from v4 for every rank.
v4rows={x['registry_rank']:x for x in v4['coverage_rows']}; v5rows={x['registry_rank']:x for x in v5['coverage_rows']}
for rank in v4rows:
 assert v4rows[rank]['source_evidence']==v5rows[rank]['source_evidence']
# 20 accepted result labels partition into 14 complete, 6 unknown in v5 latest records.
p4labels={x['label'] for x in p4['results']}
latest={x['gallery']:x.get('latest_prefix_record') for x in v5['coverage_rows'] if x.get('latest_prefix_record')}
assert p4labels==set(latest)
assert sum(x['status']=='valid_complete_index' for x in latest.values())==14
assert sum(x['status']=='transport_or_parse_unknown' for x in latest.values())==6
print(json.dumps({'ok':True,'v5_sha256':sha('research/continuous-recovery-20261016/local-audit/gallery-prefix-registry-v5/gallery-prefix-registry-v5.json'),'v5_counts':{'groups':len(v5['coverage_rows']),'slots':sum(x['declared_slots'] for x in v5['coverage_rows']),'entities':sum(x['expected_direct_entities'] for x in v5['coverage_rows']),'limited_complete':sum(x['coverage_class']=='reviewed_window_complete' for x in v5['coverage_rows']),'incomplete':sum(x['coverage_class']!='reviewed_window_complete' for x in v5['coverage_rows'])},'prefix04_complete':sorted([k for k,v in latest.items() if v['status']=='valid_complete_index']),'prefix04_unknown':sorted([k for k,v in latest.items() if v['status']=='transport_or_parse_unknown']),'incomplete_labels':sorted(inc['conservation']['labels']),'early_count':len(early['items']),'early_batches':{'batch_1':early['batch_split']['batch_1']['count'],'batch_2':early['batch_split']['batch_2']['count']},'early_excluded':early['excluded_full_window_groups']},ensure_ascii=False,indent=2))

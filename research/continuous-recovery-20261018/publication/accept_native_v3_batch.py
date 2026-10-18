"""Root verification of a bounded native replay batch, with no redirect following."""
import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode=True
parser=argparse.ArgumentParser();parser.add_argument('--batch',type=int,required=True)
parser.add_argument('--report-sha',required=True);args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[3];RUN=ROOT/'research/continuous-recovery-20261018';PUB=RUN/'publication'
NET=RUN/'network/native-replay47-v3';PLAN=NET/f'batch-{args.batch:02d}/plan.json'
OUT=PUB/f'root-native-replay47-v3-batch{args.batch}-source-acceptance.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_bytes())
assert not OUT.exists()
driver=NET/'native_replay47_driver.py'
assert sha(driver)=='84656d15036405ad6813702a4f7a0086f9d1838c2a3323d5022c84a67feb7c83'
report_path=PLAN.parent/'output/batch-report.json';assert sha(report_path)==args.report_sha
report=read(report_path);plan=read(PLAN);assert report['plan_sha256']==sha(PLAN)
assert report['root_plan_acceptance_sha256']==sha(ROOT/plan['root_plan_acceptance']['path'])
spec=importlib.util.spec_from_file_location('root_native_v3_source',driver)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
v3=module.import_frozen_v3(RUN/'network/reusable-image-driver-v3/reusable_image_driver.py')
attempts=[a for a in report['attempts'] if a.get('sent')]
assert len(attempts)==report['requests']<=14
assert report['total_body_bytes']==sum(a['body_bytes'] for a in attempts)<=16777216
times=[datetime.fromisoformat(a['started_utc']) for a in attempts]
gaps=[(b-a).total_seconds() for a,b in zip(times,times[1:])];assert not gaps or min(gaps)>=5
assert (datetime.fromisoformat(report['finished_utc'])-datetime.fromisoformat(report['started_utc'])).total_seconds()<=245
assert attempts[0]['transport']=='direct'
tail=report['failure_streak_start'];target_by_id={c['target_id']:c for c in plan['candidates']}
for a in attempts:
    c=target_by_id[a['target_id']];assert a['url']==c['request_url']
    assert a['disk_free_before_request']>=11005853696 and a['disk_free_after_request']>=11005853696
    assert a['body_bytes']<=8388608
    classified=module.classify_response(v3,a,c['expected_mime'])
    assert classified['classification']==a['classification'] and classified['transfer_failure']==a['transfer_failure']
    tail=module.next_failure_streak(tail,classified)
    if a.get('body_path'):
        body=ROOT/a['body_path'];assert sha(body)==a['raw_body_sha256'] and body.stat().st_size==a['body_bytes']
assert tail==report['failure_streak_end']
rows=[]
for c in plan['candidates']:
    hits=[a for a in attempts if a['target_id']==c['target_id']]
    if not hits:continue
    a=hits[-1];classification=a['classification']
    row={'target_id':c['target_id'],'queue_rank':c['queue_rank'],'original':c['original'],
        'request_url':c['request_url'],'checked_utc':a['finished_utc'],'status':a['source_status'],
        'classification':'archive_replay_404' if classification=='actual404' else classification,
        'body_sha256':a['raw_body_sha256'],'body_bytes':a['body_bytes']}
    if classification=='observed_302_location':
        location=a['location']
        match=re.fullmatch(r'https://web\.archive\.org/web/([0-9]{14})id_/(http://www\.worldofwarcraft\.com/info/dungeons/images/karazhan/[^/?#]+)',location or '')
        assert match and match[2]==c['original']
        row.update(observed_redirect_capture_timestamp=match[1],observed_redirect_url=location,redirect_followed=False)
    rows.append(row)
gate=tail==0 and report['stop_reason']=='completed_candidate_queue' and not any(a['source_status'] in {429,503} for a in attempts)
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
    'plan_sha256':sha(PLAN),'private_report_sha256':sha(report_path),'requests':len(attempts),
    'targets_checked':len(rows),'actual_archive_replay_404':sum(r['classification']=='archive_replay_404' for r in rows),
    'observed_redirects':sum(r['classification']=='observed_302_location' for r in rows),
    'failure_streak_start':report['failure_streak_start'],'failure_streak_end':tail,
    'stop_reason':report['stop_reason'],'cooldown_not_before_utc':report['cooldown_not_before_utc'],
    'resume_gate_passed':gate,'accepted_images':[],
    'pending_source_index':sum(r['classification']=='pending_source_index' for r in rows),
    'body_bytes':report['total_body_bytes'],'minimum_request_gap_seconds':min(gaps) if gaps else None,
    'rows':rows,'boundary':'Observed Wayback replay responses only. Redirect targets are recorded without following; no image payload is accepted without source-index review.',
    'network_requests_during_acceptance':0,'disk_free_bytes':shutil.disk_usage(ROOT).free}
OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
all_rows={}
for p in PUB.glob('root-native-*-source-acceptance.json'):
    r=read(p)
    if r.get('accepted'):all_rows.update({x['target_id']:x for x in r.get('rows',[])})
resolved=[r for r in all_rows.values() if r['classification'] in {'archive_replay_404','observed_302_location','pending_source_index','http_200_nonimage'}]
status_path=RUN/'status.json';status=read(status_path)
netid=f'NET{34+args.batch:02d}'
status.update(latest_source_acceptance=OUT.relative_to(RUN).as_posix(),latest_network_batch=netid,
    latest_failure_tail=tail,network_resume_gate_passed=gate,
    native_karazhan_checked_this_run=len(all_rows),
    native_karazhan_actual404_total=79+sum(r['classification']=='archive_replay_404' for r in all_rows.values()),
    native_karazhan_observed_redirects=sum(r['classification']=='observed_302_location' for r in all_rows.values()),
    native_karazhan_transport_unknown_remaining=47-len(resolved),updated_utc=datetime.now(timezone.utc).isoformat())
if report['cooldown_not_before_utc']:status['network_cooldown_not_before_utc']=report['cooldown_not_before_utc']
if not any(x['id']==netid for x in status['network_batches']):
    status['network_batches'].append({'id':netid,'status':'source_accepted','accepted_images':0,
        'scope':f'Frozen native Karazhan queue slice batch{args.batch}',
        'requests':len(attempts),'plan':PLAN.relative_to(RUN).as_posix(),
        'root_source_acceptance':OUT.relative_to(RUN).as_posix()})
status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'source_receipt_sha256':sha(OUT),'rows':len(rows),
    'archive404_total':status['native_karazhan_actual404_total'],'observed_redirects':status['native_karazhan_observed_redirects'],
    'unknown_remaining':status['native_karazhan_transport_unknown_remaining'],'resume_gate':gate}))

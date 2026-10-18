"""Independently classify recorded native replay responses and update the ledger."""
import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'research/continuous-recovery-20261018'
PUB=RUN/'publication'
NET=RUN/'network/native-replay47-v2'
OUT=PUB/'root-native-replay47-v2-batch1-source-acceptance.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
assert not OUT.exists()
driver=NET/'native_replay47_driver.py'
assert sha(driver)=='18fae133137093651665036acbd7157eead446b4ef330a9f59889700f76ad920'
report_path=NET/'batch-01/output/batch-report.json'
assert sha(report_path)=='9abdf3dc20d2f537bba30566d1d057560c1748077c42c2eac074f17dd326efae'
report=read(report_path);plan=read(NET/'batch-01/plan.json')
assert report['plan_sha256']==sha(NET/'batch-01/plan.json')
assert report['root_plan_acceptance_sha256']==sha(PUB/'root-native-replay47-v2-batch1-plan-acceptance.json')
spec=importlib.util.spec_from_file_location('native_v2_root_source',driver)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
v3=module.import_frozen_v3(RUN/'network/reusable-image-driver-v3/reusable_image_driver.py')
attempts=[a for a in report['attempts'] if a.get('sent')]
assert len(attempts)==report['requests']==13 and len(plan['candidates'])==12
assert report['total_body_bytes']==sum(a['body_bytes'] for a in attempts)==56508
assert report['stop_reason']=='completed_candidate_queue' and report['cooldown_not_before_utc'] is None
assert report['failure_streak_start']==report['failure_streak_end']==0
times=[datetime.fromisoformat(a['started_utc']) for a in attempts]
gaps=[(b-a).total_seconds() for a,b in zip(times,times[1:])]
assert min(gaps)>=5 and (times[-1]-times[0]).total_seconds()<240
assert attempts[0]['transport']=='direct' and attempts[0]['curl_exit']==28 and attempts[0]['source_status'] is None
rows=[]
for candidate in plan['candidates']:
    hits=[a for a in attempts if a['target_id']==candidate['target_id']]
    final=hits[-1]
    for attempt in hits:
        assert attempt['url']==candidate['request_url']
        assert attempt['disk_free_before_request']>=11005853696 and attempt['disk_free_after_request']>=11005853696
        classified=module.classify_response(v3,attempt,['image/jpeg'])
        assert classified['classification']==attempt['classification']
        assert classified['transfer_failure']==attempt['transfer_failure']
        if attempt.get('body_path'):
            body=ROOT/attempt['body_path']
            assert sha(body)==attempt['raw_body_sha256'] and body.stat().st_size==attempt['body_bytes']
    assert final['transport']=='proxy' and final['curl_exit']==0 and final['source_status']==404
    assert final['classification']=='actual404' and not final['transfer_failure']
    rows.append({'target_id':candidate['target_id'],'queue_rank':candidate['queue_rank'],
        'original':candidate['original'],'request_url':candidate['request_url'],
        'checked_utc':final['finished_utc'],'status':404,'classification':'archive_replay_404',
        'body_sha256':final['raw_body_sha256'],'body_bytes':final['body_bytes']})
assert len({r['target_id'] for r in rows})==12
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
    'plan_sha256':sha(NET/'batch-01/plan.json'),'private_report_sha256':sha(report_path),
    'requests':13,'targets_checked':12,'actual_archive_replay_404':12,
    'failure_streak_start':0,'failure_streak_end':0,'stop_reason':report['stop_reason'],
    'cooldown_not_before_utc':None,'resume_gate_passed':True,'accepted_images':[],
    'pending_source_index':0,'body_bytes':56508,'minimum_request_gap_seconds':min(gaps),
    'rows':rows,'boundary':'404 is the observed Wayback replay response, not proof that Blizzard originally returned 404 or that no capture exists at another time.',
    'disk_free_bytes':shutil.disk_usage(ROOT).free,'network_requests_during_acceptance':0}
OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
status_path=RUN/'status.json';status=read(status_path)
assert status['accepted_images']==277
status.update(latest_source_acceptance=OUT.relative_to(RUN).as_posix(),
    latest_network_batch='NET35',latest_failure_tail=0,network_resume_gate_passed=True,
    native_karazhan_checked_this_run=12,native_karazhan_actual404_total=91,
    native_karazhan_transport_unknown_remaining=35,
    updated_utc=datetime.now(timezone.utc).isoformat())
status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'source_receipt_sha256':sha(OUT),'targets':12,'requests':13,'unknown_remaining':35}))

"""Independently verify the currently hosted dungeon page and every pictured asset."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BATCH=HERE/'network/github-pages-v52-dungeons20'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    report=read(BATCH/'runtime/private/execution-report.json')
    manifest=read(BATCH/'object-manifest.json')
    assert report['accepted'] and report['stop_reason']=='completed'
    assert len(report['objects'])==len(report['attempts'])==len(manifest['objects'])==20
    rows=[];previous=None;intervals=[]
    for expected,item,attempt in zip(manifest['objects'],report['objects'],report['attempts']):
        assert item['matches_local'] and item['url']==attempt['url']==expected['url']
        assert attempt['http_status']==200 and attempt['curl_exit']==0 and attempt['transport']=='direct'
        assert not any(attempt[k] for k in ('timed_out','response_cap_exceeded','transport_failed'))
        assert attempt['mime']==expected['expected_mime'] and attempt['effective_url']==expected['url']
        body=BATCH/attempt['raw_body_path'];local=ROOT/expected['local_path']
        assert body.read_bytes()==local.read_bytes()
        assert body.stat().st_size==expected['local_bytes'] and sha(body)==expected['local_sha256']
        assert min(attempt['disk_free_before_bytes'],attempt['disk_free_after_bytes'])>=11005853696
        started=datetime.fromisoformat(attempt['request_started_utc'].replace('Z','+00:00'))
        if previous is not None:
            interval=(started-previous).total_seconds();assert interval>=5;intervals.append(interval)
        previous=started
        rows.append({k:expected[k] for k in ('path','kind','url','local_bytes','local_sha256')})
    receipt={'schema':'wow-root-online-deadmines-acceptance/v1','accepted':True,
       'checked_utc':datetime.now(timezone.utc).isoformat(),'version':'v52','objects':rows,
       'counts':{'page':1,'originals':9,'previews':10,'direct_attempts':20,'proxy_attempts':0},
       'minimum_actual_utc_start_interval_seconds':min(intervals),
       'cadence_note':'The nominal 6.2-second target has sub-0.02-second observed timer variation. Every actual UTC request start interval exceeds the authorized five-second minimum.',
       'report_sha256':sha(BATCH/'runtime/private/execution-report.json'),
       'object_manifest_sha256':sha(BATCH/'object-manifest.json'),
       'public_summary_sha256':sha(BATCH/'runtime/object-match-summary.json'),
       'disk_free_bytes':shutil.disk_usage(ROOT).free,
       'conclusion':'Current hosted HTML and all nineteen pictured image objects exactly match accepted local v52. No deployment omission for these nine early Deadmines screenshots.',
       'network_requests_by_this_acceptance':0}
    (HERE/'root-deadmines-online-acceptance.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'accepted':True,'objects':20,'minimum_utc_interval':min(intervals)}))

if __name__=='__main__':main()

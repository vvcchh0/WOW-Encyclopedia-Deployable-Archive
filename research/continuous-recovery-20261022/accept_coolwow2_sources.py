"""Verify the three fetched blobs independently; no page mapping is decided here."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BATCH=HERE/'network/coolwow2-item-icons01'
ASSETS=HERE/'integration/faction-icons-candidates/assets'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(BATCH/'plan.json');report=read(BATCH/'runtime/private/report.json')
public=read(BATCH/'runtime/public-inventory.json');watch=read(BATCH/'parent-watchdog-attempt01/watchdog-receipt.json')
assert report['stop_reason']=='completed' and public['complete']
attempts=report['attempts'];assert len(attempts)==6
assert [a['transport'] for a in attempts]==['direct','proxy']*3
assert [a['http_status'] for a in attempts]==[None,200]*3
assert all(a['transport_failed'] for a in attempts[::2])
assert all(not a['transport_failed'] for a in attempts[1::2])
dt=lambda t:datetime.fromisoformat(t.replace('Z','+00:00'))
gaps=[(dt(b['request_started_utc'])-dt(a['request_started_utc'])).total_seconds() for a,b in zip(attempts,attempts[1:])]
monotonic_gaps=[a['actual_start_interval_seconds'] for a in attempts[1:]]
assert min(gaps)>=5 and min(monotonic_gaps)>=6.2
assert report['total_body_bytes']==3587 and report['cooldown_not_before_utc'] is None
journal=[json.loads(line) for line in (BATCH/'runtime/private/attempt-journal.jsonl').read_text(encoding='utf-8').splitlines()]
preflight=[r for r in journal if r.get('phase')=='attempt_preflight']
assert len(preflight)==6
assert min([r['disk_free_before_bytes'] for r in preflight]+[a['disk_free_after_bytes'] for a in attempts])>=11005853696
assert shutil.disk_usage(ROOT).free>=11005853696
ASSETS.mkdir(parents=True,exist_ok=True)
records=[]
for target,attempt,pub in zip(plan['targets'],attempts[1::2],public['records'],strict=True):
 p=Path(attempt['_body_file']);data=p.read_bytes();stem=Path(target['repository_path']).name
 assert len(data)==target['expected_bytes']==pub['body_bytes']
 blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 assert blob==target['expected_git_blob_sha1']==pub['git_blob_sha1']
 assert hashlib.sha256(data).hexdigest()==pub['body_sha256']
 with Image.open(io.BytesIO(data)) as im:
  assert im.format=='JPEG' and im.size==(36,36) and getattr(im,'n_frames',1)==1
  im.load();im.convert('RGBA').tobytes()
 dest=ASSETS/stem
 if dest.exists():assert dest.read_bytes()==data
 else:dest.write_bytes(data)
 records.append({'repository_path':target['repository_path'],'source_url':target['url'],'current_observed_utc':attempt['request_finished_utc'],
  'sha256':sha(dest),'git_blob_sha1':blob,'length':len(data),'format':'JPEG','width':36,'height':36,'frames':1,
  'original_capture_timestamp':None,'classification':'later_related_source','curated_payload':dest.relative_to(ROOT).as_posix()})
receipt={'schema':'wow-root-coolwow2-item-source-acceptance/v1','accepted_sources':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
 'accepted_for_browser_supplement':False,'pending':'Exact page role and related-source display decision',
 'repository_url':'https://github.com/boom8866/coolwow2','commit_sha':'09c52b7673871b8048da92e5a13ed753fc08162f',
 'tree_sha':'5b3f74d7522aee7d57f8f9b554570a272836e869','repository_commit_date_utc':'2015-12-16T16:29:03Z',
 'original_capture_timestamp':None,'historical_original_images_recovered':0,'images_reencoded':False,
 'network_requests':6,'direct_successes':0,'proxy_successes':3,'request_start_intervals_seconds':gaps,
 'monotonic_request_start_intervals_seconds':monotonic_gaps,
 'cadence_note':'Monotonic intervals meet the planned 6.2-second margin. UTC timestamp differences have a 6.196930-second minimum; both measurements exceed the required five seconds.',
 'tls_verification':True,'raw_http_and_cookies_public':False,'wayback_gate_unchanged':True,'records':records,
 'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [BATCH/'plan.json',BATCH/'coolwow2_item_icons01.py',BATCH/'runtime/public-inventory.json',BATCH/'runtime/private/report.json',BATCH/'parent-watchdog-attempt01/watchdog-receipt.json',HERE/'coolwow2-selected-source-tree.json']],
 'disk_free_after_bytes':shutil.disk_usage(ROOT).free}
(HERE/'root-coolwow2-item-source-acceptance.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
status=read(HERE/'status.json');status.update(new_related_source_images_accepted=4,new_related_payload_bytes=22433,pending_related_image_role_decisions=3,in_flight_network_batch=None,updated_utc=receipt['checked_utc'])
(HERE/'status.json').write_bytes((json.dumps(status,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'accepted_source_images':3,'bytes':3587,'page_mapping_pending':True}))

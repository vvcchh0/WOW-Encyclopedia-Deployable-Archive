"""Accept the nine actual responses while retaining the stopped batch result."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
batch=HERE/'network/github-pages-v55-changes69';private=read(batch/'runtime/private/report.json')
public=read(batch/'runtime/object-match-summary.json')
assert private['stop_reason']=='request_start_spacing_below_minimum'
assert len(private['attempts'])==9 and not public['accepted']
manifest=read(batch/'object-manifest.json');by_id={r['object_id']:r for r in manifest['objects']}
objects=[];times=[];gaps=[]
for record in private['attempts']:
 item=by_id[record['object_id']]
 assert record['http_status']==200 and record['returncode']==0
 assert record['transport']=='direct' and not record['timed_out'] and not record['transport_failed'] and not record['response_cap_exceeded']
 assert record['url']==record['effective_url']==item['url']
 assert record['header_parse']['content_type'].split(';')[0].strip().lower() in item['accepted_mime_types']
 body=ROOT/record['body_path'];local=ROOT/'.scratch/pages-resources-20261022-v55'/item['path']
 assert body.resolve().is_relative_to((batch/'runtime/private/raw').resolve())
 assert sha(body)==sha(local)==item['local_sha256']==record['body_sha256']
 assert body.stat().st_size==local.stat().st_size==item['local_bytes']==record['body_bytes']
 times.append(datetime.fromisoformat(record['request_started_utc'].replace('Z','+00:00')))
 if record['actual_start_interval_seconds'] is not None:gaps.append(record['actual_start_interval_seconds'])
 objects.append({'path':item['path'],'url':item['url'],'sha256':sha(body),'bytes':body.stat().st_size,'status':200,'transport':'direct','mime':record['header_parse']['content_type'].split(';')[0].strip().lower()})
utc_gaps=[(b-a).total_seconds() for a,b in zip(times,times[1:])]
assert min(utc_gaps)>=5 and min(gaps)>=5 and len(objects)==9
accepted={r['path'] for r in objects}
remaining=[{'path':r['path'],'sha256':r['local_sha256'],'bytes':r['local_bytes']} for r in manifest['objects'] if r['path'] not in accepted]
assert len(remaining)==60
result={'schema':'wow-root-v55-online-partial-acceptance/v1','accepted_for_online_objects':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
 'pages_commit':manifest['source']['pages_commit'],'actions_run':manifest['source']['actions_run'],'local_site':'.scratch/pages-resources-20261022-v55',
 'prior_batch_accepted':False,'prior_batch_report_sha256':sha(batch/'runtime/object-match-summary.json'),
 'prior_batch_stop_reason':private['stop_reason'],'objects_verified':9,'objects':objects,'remaining_count':60,'remaining':remaining,
 'planned_cadence_seconds':6.2,'minimum_actual_user_seconds':5,'observed_min_utc_seconds':min(utc_gaps),'observed_min_monotonic_seconds':min(gaps),
 'decision':'Retain the failed batch result. All nine actual bodies match the accepted export; the 6.188-second observed minimum satisfies the five-second user limit. A separate batch may inspect only the sixty remaining objects, with scheduling target and hard limit represented separately.',
 'wayback_resume_gate_passed':False,'raw_http_and_cookies_public':False}
p=HERE/'root-v55-online-partial-acceptance9.json';assert not p.exists();p.write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps({'objects_independently_accepted':9,'remaining':60,'utc_min':min(utc_gaps),'monotonic_min':min(gaps),'receipt_sha256':sha(p)}))
if __name__=='__main__':pass

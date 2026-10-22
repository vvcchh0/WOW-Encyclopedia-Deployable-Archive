from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
ROOT=Path.cwd();HERE=ROOT/'research/continuous-recovery-20261022'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
oldp=HERE/'root-v55-online-partial-acceptance9.json'
assert sha(oldp)=='b31b5918ce9e2dce4d34358924c9997eff55645943e6357c5ebc69b1f1ea40a0'
old=read(oldp);assert old['accepted_for_online_objects'] and old['objects_verified']==9
base=HERE/'network/github-pages-v55-remaining60'
pubp=base/'runtime/object-match-summary.json';privatep=base/'runtime/private/report.json'
assert sha(pubp)=='b9bf253344a8745d0c5d6523c7e12ac45f2f0ce1f54c662e3f602bf5eaf06006'
assert sha(privatep)=='6a49929f043fb6bb285e547aceb17d60f8cf9fabacf0ccd093e4559d4c183e0e'
pub=read(pubp);private=read(privatep)
assert pub['complete'] and pub['accepted'] and pub['stop_reason']=='completed'
assert pub['http_attempt_count']==60 and pub['direct_attempt_count']==60 and pub['proxy_attempt_count']==0
assert not pub['cooldown_not_before_utc'] and not pub['consecutive_transfer_failure_tail']
exp=read(HERE/'root-v55-export-acceptance.json');expected={r['path']:r for r in exp['online_changes_from_v53']};assert len(expected)==69
site=ROOT/exp['local_site'];rows=list(old['objects']);seen={r['path'] for r in rows};assert len(seen)==9
for r in pub['objects']:
 assert r['path'] not in seen
 e=expected[r['path']];assert r['matches_local'] and len(r['attempts'])==1
 a=r['attempts'][0]
 assert a['status']==200 and a['transport']=='direct' and a['effective_url']==r['url'] and a['mime'] in r['expected_mime']
 assert (a['sha256'],a['bytes'])==(e['sha256'],e['bytes'])
 saved=next(x for x in private['objects'] if x['path']==r['path'])['attempts'][0]
 assert saved['http_status']==200 and saved['returncode']==0 and not saved['transport_failed']
 body=ROOT/saved['body_path'];local=site/r['path']
 assert body.read_bytes()==local.read_bytes()
 assert (sha(body),body.stat().st_size)==(e['sha256'],e['bytes'])
 assert saved['header_parse']['content_type'].split(';')[0]==a['mime']
 rows.append({'path':r['path'],'url':r['url'],'sha256':sha(body),'bytes':body.stat().st_size,'status':200,'mime':a['mime'],'transport':'direct'})
 seen.add(r['path'])
assert seen==set(expected) and len(rows)==69
for r in rows:
 e=expected[r['path']];assert (r['sha256'],r['bytes'])==(e['sha256'],e['bytes'])
 assert (sha(site/r['path']),(site/r['path']).stat().st_size)==(e['sha256'],e['bytes'])
minimum_mono=min(a['actual_start_interval_seconds'] for a in private['attempts'] if a['actual_start_interval_seconds'] is not None)
times=[datetime.fromisoformat(a['request_started_utc'].replace('Z','+00:00')) for a in private['attempts']]
minimum_utc=min((b-a).total_seconds() for a,b in zip(times,times[1:]))
assert minimum_mono>=5 and minimum_utc>=5
floor=11005853696;free=shutil.disk_usage(ROOT).free;assert free>=floor
assert min(a['disk_free_after_bytes'] for a in private['attempts'])>=floor
out={'schema':'wow-root-v55-online-acceptance/v1','accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'version':'v55','pages_commit':pub['pages_commit'],'actions_run':pub['actions_run'],'objects_verified':69,'response_bytes':sum(r['bytes'] for r in rows),'objects':sorted(rows,key=lambda r:r['path']),'partial9_receipt_sha256':sha(oldp),'remaining60_public_summary_sha256':sha(pubp),'remaining60_private_report_sha256':sha(privatep),'remaining60_minimum_actual_monotonic_seconds':minimum_mono,'remaining60_minimum_actual_utc_seconds':minimum_utc,'original_failed_batch_preserved':True,'original_batch_failure_was_schedule_margin_only':True,'user_minimum_seconds':5,'prior_unchanged_online_checks_reused':True,'wayback_resume_gate_passed':False,'raw_http_and_cookies_public':False,'disk_free_after_bytes':free}
p=HERE/'root-v55-online-acceptance.json';assert not p.exists();p.write_bytes((json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'accepted':True,'objects':len(rows),'response_bytes':out['response_bytes'],'sha256':sha(p)}))

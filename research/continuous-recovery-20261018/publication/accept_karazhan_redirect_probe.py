"""Independently read private wire evidence, publish only the cleaned observation."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
DIR = RUN / 'network/karazhan-observed-redirect-probe-v1'
PUB = RUN / 'publication'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report_path = DIR / 'output/probe-report.json'
assert sha(report_path) == '553ce6d03df622d9e619c1fbbf10c5de72dfb59474afd19052e71dfd05bafc1f'
report = read(report_path)
gate = read(PUB / 'root-karazhan-observed-redirect-probe-batch1-plan-acceptance.json')
assert report['root_plan_acceptance_sha256'] == sha(PUB / 'root-karazhan-observed-redirect-probe-batch1-plan-acceptance.json')
assert report['plan_sha256'] == gate['plan_sha256']
assert report['requests'] == 2 and report['automatic_redirects'] == 0
assert report['accepted_images'] == report['pending_source_index'] == 0
assert report['failure_streak_end'] == 0 and report['cooldown_not_before_utc'] is None
a, b = report['attempts']
assert a['transport'] == 'direct' and a['curl_exit'] == 28 and a['source_status'] is None and a['body_bytes'] == 0
assert b['transport'] == 'proxy' and b['curl_exit'] == 0 and b['source_status'] == 301 and not b['transfer_failure']
assert a['url'] == b['url'] == gate['exact_request_url']
headers = (ROOT / b['headers_path']).read_text(encoding='iso-8859-1')
locations = [x.split(':', 1)[1].strip() for x in headers.splitlines() if x.lower().startswith('location:')]
assert locations == [b['location']]
assert locations[0] == 'https://web.archive.org/web/20130612155549id_/http://us.battle.net/wow/game/guide/'
body = ROOT / b['body_path']
assert sha(body) == b['raw_body_sha256'] and body.stat().st_size == b['body_bytes'] == report['total_body_bytes'] == 244
dt = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
gap = (dt(b['started_utc']) - dt(a['started_utc'])).total_seconds()
assert gap >= 5
assert (dt(report['finished_utc']) - dt(report['started_utc'])).total_seconds() < 50
assert min(x['disk_free_after_request'] for x in (a,b)) >= 11005853696
free = shutil.disk_usage(ROOT).free
assert free >= 11005853696
status_path = RUN / 'status.json'
status = read(status_path)
assert status['latest_source_acceptance'] == 'publication/root-late-thumbnails12-batch2-source-acceptance.json'
out = PUB / 'root-karazhan-observed-redirect-probe-source-acceptance.json'
assert not out.exists()
receipt = {
    'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'plan_sha256': report['plan_sha256'], 'report_sha256': sha(report_path),
    'requests': 2, 'source_responses': 1, 'accepted_images': [],
    'failure_streak_end': 0, 'resume_gate_passed': True,
    'stop_reason': report['stop_reason'], 'cooldown_not_before_utc': None,
    'total_body_bytes': 244, 'request_start_gap_seconds': gap,
    'classification_counts': report['classification_counts'],
    'captured_timestamp': '20130612155549', 'original': 'http://www.worldofwarcraft.com/info/dungeons/images/karazhan/ss1-thumb.jpg',
    'sanitized_destination': b['sanitized_destination'],
    'disk_free_after_request_min': min(x['disk_free_after_request'] for x in (a,b)), 'disk_free_at_review': free,
    'scope': 'One observed 2013 thumbnail capture redirects to the later Battle.net game guide, not an image. No redirect followed. The other eleven captured301 records were not replayed in this probe.',
}
out.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
rel = out.relative_to(RUN).as_posix()
status.update(latest_source_acceptance=rel, latest_network_acceptance=rel, latest_network_batch='NET41', latest_failure_tail=0,
              network_resume_gate_passed=True, network_cooldown_not_before_utc=None, updated_utc=receipt['checked_utc'])
assert not any(x['id'] == 'NET41' for x in status['network_batches'])
status['network_batches'].append({'id': 'NET41', 'plan': 'network/karazhan-observed-redirect-probe-v1/plan.json',
    'status': 'source_accepted', 'requests': 2, 'accepted_images': 0, 'root_source_acceptance': rel})
status_path.write_text(json.dumps(status, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'accepted': True, 'source_sha256': sha(out), 'next_gate_open': True, 'images': 0}))

"""Independently compare the 22 actual published responses with the accepted export."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path.cwd()
HERE = ROOT / 'research/continuous-recovery-20261022'
BASE = HERE / 'network/github-pages-v56-changes22'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
public_path = BASE / 'runtime/object-match-summary.json'
private_path = BASE / 'runtime/private/report.json'
public, private = read(public_path), read(private_path)
export = read(HERE / 'root-v56-export-acceptance.json')
go = read(HERE / 'root-v56-changes22-go.json')
assert export['accepted'] and go['accepted'] and go['root_go']
assert public['accepted'] and public['complete'] and public['stop_reason'] == 'completed'
assert public['http_attempt_count'] == public['direct_attempt_count'] == 22
assert public['proxy_attempt_count'] == 0
assert not public['cooldown_not_before_utc'] and not public['consecutive_transfer_failure_tail']
assert public['pages_commit'] == 'ada74291b7f46afe3289fb2773e31449f4a5eb83'
assert str(public['actions_run']) == '39789068533'
assert public['export_acceptance_sha256'] == sha(HERE / 'root-v56-export-acceptance.json')
assert private['go_sha256'] == sha(HERE / 'root-v56-changes22-go.json')
site = ROOT / export['local_site']
assert sha(site / 'export-provenance.json') == export['export_provenance_sha256']
expected = {row['path']: row for row in export['online_changes_from_v55']}
assert len(expected) == len(public['objects']) == len(private['objects']) == 22
private_by_path = {row['path']: row for row in private['objects']}
rows, seen = [], set()
for row in public['objects']:
    path = row['path']
    assert path not in seen and path in expected
    seen.add(path)
    target = expected[path]
    assert row['matches_local'] and len(row['attempts']) == 1
    attempt = row['attempts'][0]
    assert attempt['status'] == 200 and attempt['transport'] == 'direct'
    assert attempt['effective_url'] == row['url'] and attempt['mime'] in row['expected_mime']
    assert (attempt['sha256'], attempt['bytes']) == (target['sha256'], target['bytes'])
    saved = private_by_path[path]
    assert saved['matches_local'] and len(saved['attempts']) == 1
    actual = saved['attempts'][0]
    assert actual['http_status'] == 200 and actual['returncode'] == 0
    assert not actual['transport_failed'] and not actual['timed_out']
    assert not actual['response_cap_exceeded'] and actual['effective_url'] == row['url']
    assert actual['header_parse']['content_type'].split(';')[0].lower() == attempt['mime']
    body = (ROOT / actual['body_path']).resolve(strict=True)
    assert body.is_relative_to((BASE / 'runtime/private/raw').resolve())
    local = site / path
    assert body.read_bytes() == local.read_bytes()
    assert (sha(body), body.stat().st_size) == (target['sha256'], target['bytes'])
    rows.append({'path': path, 'url': row['url'], 'bytes': target['bytes'],
                 'sha256': target['sha256'], 'status': 200, 'mime': attempt['mime'], 'transport': 'direct'})
assert seen == set(expected)
attempts = private['attempts']
assert len(attempts) == 22
minimum_mono = min(x['actual_start_interval_seconds'] for x in attempts
                   if x['actual_start_interval_seconds'] is not None)
times = [datetime.fromisoformat(x['request_started_utc'].replace('Z', '+00:00')) for x in attempts]
minimum_utc = min((b-a).total_seconds() for a, b in zip(times, times[1:]))
assert minimum_mono >= 5 and minimum_utc >= 5
floor = 11005853696
free = shutil.disk_usage(ROOT).free
assert free >= floor and public['disk_free_before_bytes'] >= floor
assert public['disk_free_after_bytes'] >= floor
assert min(x['disk_free_after_bytes'] for x in attempts) >= floor
out = {
    'schema': 'wow-root-v56-online-acceptance/v1', 'accepted': True,
    'checked_utc': datetime.now(timezone.utc).isoformat(), 'version': 'v56',
    'pages_commit': public['pages_commit'], 'actions_run': public['actions_run'],
    'objects_verified': 22, 'response_bytes': sum(x['bytes'] for x in rows),
    'objects': sorted(rows, key=lambda x: x['path']),
    'export_acceptance_sha256': sha(HERE / 'root-v56-export-acceptance.json'),
    'public_summary_sha256': sha(public_path), 'private_report_sha256': sha(private_path),
    'root_go_sha256': sha(HERE / 'root-v56-changes22-go.json'),
    'minimum_actual_monotonic_seconds': minimum_mono,
    'minimum_actual_utc_seconds': minimum_utc, 'user_minimum_seconds': 5,
    'prior_unchanged_online_checks_reused': True, 'wayback_resume_gate_passed': False,
    'raw_http_and_cookies_public': False, 'disk_free_after_bytes': free,
}
output = HERE / 'root-v56-online-acceptance.json'
assert not output.exists()
output.write_bytes((json.dumps(out, ensure_ascii=False, indent=2)+'\n').encode())
print(json.dumps({'accepted': True, 'objects': len(rows), 'response_bytes': out['response_bytes'],
                  'sha256': sha(output)}))

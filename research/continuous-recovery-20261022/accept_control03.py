"""Independently bind the observed failed control and retain its history."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONTROL = HERE / 'network/wayback-positive-control03'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dt = lambda x: datetime.fromisoformat(x.replace('Z', '+00:00'))
report = read(CONTROL / 'runtime/control-report.json')
watch = read(CONTROL / 'parent-watchdog-attempt02/watchdog-receipt.json')
go = HERE / 'root-wayback-control03-go.json'
assert report['go_sha256'] == watch['go_sha256'] == sha(go)
assert report['network_requests'] == 2 and report['logical_requests'] == 1
attempts = report['attempts']
assert len(attempts) == 2
assert [a['transport'] for a in attempts] == ['direct', 'proxy']
assert attempts[0]['transfer_error'] and attempts[0]['http_status'] is None
assert attempts[1]['http_status'] == 429 and not attempts[1]['transfer_error']
assert report['control_positive'] is False and report['image_payload_replays'] == 0
assert report['tls_verification'] and report['redirects_followed'] == 0
assert not report['pagination_used'] and not report['historical_failure_tail_reset']
gap = (dt(attempts[1]['request_started_utc']) - dt(attempts[0]['request_started_utc'])).total_seconds()
assert gap >= 5 and abs(gap - report['request_start_deltas_seconds'][0]) < 0.001
assert (dt(report['cooldown_not_before_utc']) - dt(attempts[-1]['request_finished_utc'])).total_seconds() >= 120
assert watch['watchdog']['watchdog_enforced'] and watch['watchdog']['elapsed_seconds'] < 180
assert watch['watchdog']['return_code'] == 2 and not watch['watchdog']['timed_out']
for a in attempts:
    assert min(a['disk_free_before_bytes'], a['disk_free_after_bytes']) >= 11005853696
    for role, relative in a['private_raw_paths'].items():
        assert sha(ROOT / relative) == a['private_raw_sha256'][role]
    assert a['body_bytes'] == 0
for role in ['acceptance', 'report']:
    p = ROOT / report[f'historical_failure_tail_prior_{role}']
    assert sha(p) == report[f'historical_failure_tail_prior_{role}_sha256']
assert not read(CONTROL / 'execution-summary.json')['network_requests']
assert len(list((CONTROL / 'preflight-failure-01').rglob('*.*'))) == 3
receipt = {
    'schema': 'wow-root-control03-source-acceptance/v1',
    'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'control_positive': False, 'wayback_resume_gate_passed': False,
    'network_requests': 2, 'logical_requests': 1,
    'attempts': [{k: a[k] for k in ('transport','request_started_utc','request_finished_utc','http_status','transport_error_class','body_bytes')} for a in attempts],
    'request_start_interval_seconds': gap,
    'latest_failure_utc': attempts[-1]['request_finished_utc'],
    'latest_status': 429, 'cooldown_not_before_utc': report['cooldown_not_before_utc'],
    'historical_failure_tail_retained': True, 'image_payload_replays': 0,
    'raw_http_and_cookies_public': False,
    'report_sha256': sha(CONTROL / 'runtime/control-report.json'),
    'watchdog_receipt_sha256': sha(CONTROL / 'parent-watchdog-attempt02/watchdog-receipt.json'),
    'go_sha256': sha(go),
    'prior_failure_acceptance_sha256': report['historical_failure_tail_prior_acceptance_sha256'],
    'preflight_failure': {
        'network_requests': 0,
        'summary_sha256': sha(CONTROL / 'execution-summary.json'),
        'preserved_runtime': 'network/wayback-positive-control03/preflight-failure-01',
        'old_go': 'root-wayback-control03-go-preflight-failure-01.json',
        'reason': 'Watchdog log directories were created before a runner that requires runtime to be absent. Corrected wrapper keeps logs outside runtime.',
    },
    'interpretation': 'Wayback returned no usable CDX control. Continue local/independent related-source work; no Wayback resource batch is authorized by this result.',
}
(HERE / 'root-control03-source-acceptance.json').write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
status_path = HERE / 'status.json'
status = read(status_path)
status.update(in_flight_network_batch=None, latest_wayback_failure_utc=receipt['latest_failure_utc'], latest_wayback_status=429, wayback_resume_gate_passed=False, updated_utc=receipt['checked_utc'])
status_path.write_bytes((json.dumps(status, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'accepted_observation': True, 'control_positive': False, 'requests': 2, 'new_failure_utc': receipt['latest_failure_utc']}))

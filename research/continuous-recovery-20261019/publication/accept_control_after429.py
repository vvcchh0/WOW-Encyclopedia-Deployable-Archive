"""Accept observed control failure evidence, never authorize another batch."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
PACKET = ROOT / 'research/continuous-recovery-20261019/network/control-after429-1145'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def main():
    out = PUB / 'root-control-after429-1145-source-acceptance.json'
    assert not out.exists()
    report = READ(PACKET / 'control-report.json')
    parent = READ(PACKET / 'parent-execution-receipt.json')
    go = READ(PUB / 'root-control-after429-1145-execute-go.json')
    assert SHA(PACKET / 'control-report.json') == '3638dc60ad3c2d68512260206c8519683b8622d7b619d5d9a8c5e9e26b50786c'
    assert SHA(PACKET / 'parent-execution-receipt.json') == 'ed82bdb2183f54c83e001706ba8c33964620457c0ddc636d619ac6a36dd43e63'
    assert parent['returncode'] == 0 and parent['timed_out'] is False and parent['elapsed_seconds'] < 180
    for key, name in [('plan_sha256', 'plan.json'), ('driver_sha256', 'control_after429_1145.py'), ('fixture_sha256', 'fixture-results.json'), ('input_bindings_sha256', 'input-bindings.json')]:
        assert SHA(PACKET / name) == report[key] == parent[key] == go[key]
    assert report['root_go_sha256'] == parent['go_sha256'] == SHA(PUB / 'root-control-after429-1145-execute-go.json')
    prior = PUB / 'root-control-after-rest10b-source-acceptance.json'
    assert SHA(prior) == go['latest_failure_sha256'] and READ(prior)['endpoint_stop_status'] == 429
    assert report['latest_failure_report_sha256'] == '4e5b0e519b09c4717596de99fe9e12b36093e35d4259e8b2c973c72bcd3f9375'
    assert report['network_requests'] == len(report['attempts']) == 2 and report['source_responses'] == 1
    assert not report['control_positive'] and report['payload_replays'] == 0
    assert not report['continuation_followed'] and not report['redirects_followed']
    assert report['stop_reason'] == 'endpoint_status_429' and report['total_body_bytes'] == 162
    first, last = report['attempts']
    assert first['transport'] == 'direct' and first['curl_exit'] == 28 and first['source_status'] is None
    assert last['transport'] == 'proxy' and last['source_status'] == 429 and last['curl_exit'] == 0
    parse = lambda t: datetime.fromisoformat(t.replace('Z', '+00:00'))
    assert parse(first['started_utc']) >= parse('2026-10-19T11:45:00Z')
    assert (parse(last['started_utc']) - parse(first['started_utc'])).total_seconds() >= 5
    assert last['request_start_interval_seconds'] >= 5 and last['dispatch_interval_seconds'] >= 5
    bindings = []
    for attempt in report['attempts']:
        assert attempt['disk_free_before_bytes'] >= 11005853696
        for kind, relative in attempt['raw'].items():
            p = ROOT / relative
            exists = p.exists()
            bindings.append({'path': relative, 'exists': exists, 'bytes': p.stat().st_size if exists else None, 'sha256': SHA(p) if exists else None})
            if kind == 'body':
                raw = p.read_bytes() if exists else b''
                assert hashlib.sha256(raw).hexdigest() == attempt['body_sha256'] and len(raw) == attempt['body_bytes']
        header = (ROOT / attempt['raw']['headers']).read_bytes()
        if attempt['transport'] == 'direct':
            assert header == b''
        else:
            statuses = [int(line.split()[1]) for line in header.splitlines() if line.startswith(b'HTTP/')]
            assert statuses[-1] == 429
    assert report['disk_free_after_bytes'] >= 11005853696 and parent['disk_free_after_bytes'] >= 11005853696
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'resume_gate_passed': False,
        'is_network_batch': True, 'network_requests': 2, 'accepted_images': 0, 'endpoint_stop_status': 429,
        'stop_reason': 'endpoint_status_429', 'failure_streak_end': 0, 'cooldown_not_before_utc': report['cooldown_not_before_utc'],
        'last_failure_finished_utc': report['finished_utc'], 'acquisition_stopped_for_run': True,
        'source_failure_receipt_sha256': SHA(prior), 'private_report_sha256': SHA(PACKET / 'control-report.json'),
        'parent_receipt_sha256': SHA(PACKET / 'parent-execution-receipt.json'), 'private_evidence_bindings': bindings,
        'scope': 'Root independently verified frozen inputs, latest429 binding, actual direct/proxy ordering, request start cadence, raw finalHTTP429/body identity, hard watchdog, disk and immediate stop. This failure is not resource404 evidence. No further Wayback acquisition this run.',
        'tls_verification': True, 'settings_changed': False}
    out.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'private_evidence_bindings'}))


if __name__ == '__main__':
    main()

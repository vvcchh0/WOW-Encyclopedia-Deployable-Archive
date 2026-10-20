"""Independently accept control01 wire evidence and retain the latest failure."""
import hashlib
import importlib.util
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261020'
PACKET = RUN / 'network/control01'
OUT = RUN / 'publication/root-control01-source-acceptance.json'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())
PARSE = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))


def main():
    assert not OUT.exists()
    report = READ(PACKET / 'control-report.json')
    parent = READ(PACKET / 'parent-execution-receipt.json')
    gate_path = RUN / 'publication/root-control01-execute-go.json'
    gate = READ(gate_path)
    assert parent['returncode'] == 0 and not parent['timed_out'] and parent['elapsed_seconds'] < 180
    for key, name in [('plan_sha256', 'plan.json'), ('driver_sha256', 'control01_driver.py'),
                      ('fixture_sha256', 'fixture-results.json'), ('input_bindings_sha256', 'input-bindings.json')]:
        assert SHA(PACKET / name) == report[key] == parent[key] == gate[key], key
    assert SHA(PACKET / 'parent-execute-once.py') == gate['parent_sha256']
    assert SHA(gate_path) == report['root_go_sha256'] == parent['go_sha256']
    prior_path = ROOT / 'research/continuous-recovery-20261019/publication/root-control-after429-1145-source-acceptance.json'
    prior = READ(prior_path)
    assert SHA(prior_path) == gate['latest_failure_source_acceptance_sha256']
    assert report['latest_failure_source_acceptance_sha256'] == SHA(prior_path)
    assert report['latest_failure_report_sha256'] == gate['latest_failure_report_sha256'] == prior['private_report_sha256']
    parser_path = ROOT / 'research/continuous-recovery-20261016/network/control02-plan/control02_driver.py'
    assert SHA(parser_path) == '85457ea1baa96c474e33ffc01210b4f6d96b3d6d276dc7a2b56aff3cd8376530'
    spec = importlib.util.spec_from_file_location('root_control_wire_parser', parser_path)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    attempts = report['attempts']
    assert 1 <= len(attempts) <= 2 and report['network_requests'] == len(attempts)
    assert attempts[0]['transport'] == 'direct'
    if len(attempts) == 2:
        assert attempts[1]['transport'] == 'proxy'
        assert (PARSE(attempts[1]['started_utc']) - PARSE(attempts[0]['started_utc'])).total_seconds() >= 5
        assert attempts[1]['request_start_interval_seconds'] >= 5
        assert attempts[1]['dispatch_interval_seconds'] >= 5.25
    assert PARSE(report['started_utc']) > PARSE(prior['cooldown_not_before_utc'])
    assert PARSE(report['started_utc']) >= PARSE('2026-10-20T08:33:22Z')
    assert PARSE(report['finished_utc']) < PARSE('2026-10-20T13:15:00Z')
    assert report['elapsed_seconds'] <= 120 and not report['redirects_followed']
    assert not report['continuation_followed'] and report['payload_replays'] == 0
    bindings = []
    positive = False
    total = 0
    diagnostics = []
    for attempt in attempts:
        assert attempt['disk_free_before_bytes'] >= 11005853696
        for kind, relative in attempt['raw'].items():
            path = ROOT / relative
            path.resolve().relative_to(PACKET.resolve() / 'raw')
            bindings.append({'path': relative, 'exists': path.exists(), 'bytes': path.stat().st_size if path.exists() else None, 'sha256': SHA(path) if path.exists() else None})
        body_path = ROOT / attempt['raw']['body']
        body = body_path.read_bytes() if body_path.exists() else b''
        assert hashlib.sha256(body).hexdigest() == attempt['body_sha256'] and len(body) == attempt['body_bytes']
        assert len(body) <= 1048576
        total += len(body)
        headers = (ROOT / attempt['raw']['headers']).read_bytes()
        statuses = [int(m.group(1)) for m in re.finditer(rb'^HTTP/\S+\s+(\d{3})', headers, re.M)]
        final_status = statuses[-1] if statuses else None
        assert final_status == attempt['source_status']
        if final_status == 200 and attempt['curl_exit'] == 0:
            cdx = parser.parse_cdx(body)
            matches = [row for row in cdx.get('rows', []) if row.get('timestamp') == '20080402035201'
                       and row.get('original', '').replace(':80/', '/') == 'http://www.worldofwarcraft.com/news/images/08-02/02-14-08-2.jpg'
                       and row.get('digest') == 'TJ2TFHNGVSA64RRRP3UD2CQZCP4TTRND'
                       and row.get('mimetype') == 'image/jpeg' and row.get('statuscode') == '200']
            found = bool(cdx.get('valid') and cdx.get('complete') and not cdx.get('resume_keys') and matches)
            assert found == attempt['positive_known_row']
            positive |= found
        else:
            assert not attempt['positive_known_row']
        metrics = attempt['metrics'].splitlines()
        detail = {'transport': attempt['transport'], 'curl_exit': attempt['curl_exit'], 'http_status': final_status,
                  'tcp_connected': len(metrics) >= 5 and float(metrics[1]) > 0,
                  'tls_completed': len(metrics) >= 5 and float(metrics[2]) > 0}
        if final_status in (429, 503):
            assert attempt is attempts[-1]
            detail['meaning'] = 'Endpoint HTTP limit/unavailable response; no resource absence conclusion.'
        elif final_status is None and attempt['curl_exit'] == 28 and not detail['tcp_connected']:
            detail['meaning'] = 'TCP connection did not complete within the connect timeout; TLS/certificate validation was not reached.'
        diagnostics.append(detail)
    assert positive == report['control_positive'] and total == report['total_body_bytes'] <= 1048576
    assert parent['disk_free_before_bytes'] >= 11005853696 and parent['disk_free_after_bytes'] >= 11005853696
    assert report['disk_free_after_bytes'] >= 11005853696 and shutil.disk_usage(ROOT).free >= 11005853696
    stopped_status = attempts[-1]['source_status'] if attempts[-1]['source_status'] in (429, 503) else None
    if stopped_status:
        assert not positive and report['stop_reason'] == f'endpoint_status_{stopped_status}'
        raw_headers = (ROOT / attempts[-1]['raw']['headers']).read_bytes()
        retry_after = parser.parse_headers(raw_headers).get('retry_after') or 0
        assert PARSE(report['cooldown_not_before_utc']) >= PARSE(attempts[-1]['finished_utc']) + timedelta(seconds=max(120, int(retry_after)))
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'resume_gate_passed': positive and report['failure_streak_end'] == 0,
               'is_network_batch': True, 'network_requests': len(attempts), 'accepted_images': 0,
               'endpoint_stop_status': stopped_status, 'stop_reason': report['stop_reason'],
               'failure_streak_end': report['failure_streak_end'], 'cooldown_not_before_utc': report['cooldown_not_before_utc'],
               'last_failure_finished_utc': report['finished_utc'] if not positive else prior['last_failure_finished_utc'],
               'control_success_finished_utc': report.get('control_success_finished_utc'),
               'previous_failure_receipt_sha256': SHA(prior_path), 'private_report_sha256': SHA(PACKET / 'control-report.json'),
               'parent_receipt_sha256': SHA(PACKET / 'parent-execution-receipt.json'), 'wire_evidence_bindings': bindings,
               'diagnostics': diagnostics, 'tls_verification': True, 'settings_changed': False,
               'scope': 'Root checked bound executable inputs, actual parent watchdog, wire statuses/body, exact known CDX row when present, cadence, disk and immediate stop. Not an image payload or site completeness acceptance.'}
    OUT.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in receipt.items() if key != 'wire_evidence_bindings'}))


if __name__ == '__main__':
    main()

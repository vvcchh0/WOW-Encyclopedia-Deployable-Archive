"""Accept a known-positive control after the recorded gallery-query 503."""
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
DIRECTORY = RUN / 'network/control-after-gallery15'
OUT = RUN / 'publication/root-control03-source-acceptance.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
dt = lambda text: datetime.fromisoformat(text.replace('Z', '+00:00'))


def main():
    assert not OUT.exists()
    report = read(DIRECTORY / 'control-report.json')
    gate = read(RUN / 'publication/root-control03-plan-acceptance.json')
    prior_path = RUN / 'publication/root-gallery-retry2-source-acceptance.json'
    prior = read(prior_path)
    assert gate['accepted'] and report['script_sha256'] == gate['script_sha256'] == sha(ROOT / gate['script'])
    assert report['source_sha256'] == gate['source_receipt_sha256'] == sha(prior_path)
    assert dt(report['started_utc']) >= dt(prior['cooldown_not_before_utc'])
    assert report['failure_streak_start'] == prior['failure_streak_end'] == 0
    assert report['control_positive'] and report['payload_replays'] == 0
    assert report['tls_verification'] and not report['settings_changed']
    attempts = report['attempts']
    assert [x['transport'] for x in attempts] == ['direct', 'proxy']
    assert attempts[1]['dispatch_monotonic'] - attempts[0]['dispatch_monotonic'] >= 5.25
    assert (dt(attempts[1]['started_utc']) - dt(attempts[0]['started_utc'])).total_seconds() >= 5
    bindings, total, streak = [], 0, 0
    for attempt in attempts:
        body = ROOT / attempt['raw_body']
        data = body.read_bytes() if body.exists() else b''
        assert len(data) == attempt['body_bytes'] <= 131072
        assert hashlib.sha256(data).hexdigest() == attempt['body_sha256']
        headers = ROOT / attempt['raw_headers']
        statuses = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})', headers.read_bytes())
        if attempt['source_status'] is None:
            assert not data and attempt['curl_exit'] != 0 and not statuses
            streak += 1
        else:
            assert attempt['curl_exit'] == 0 and attempt['source_status'] == 200 and statuses[-1] == b'200'
            streak = 0
        assert attempt['disk_free_before_bytes'] >= 11005853696
        total += len(data)
        for field in ['raw_body', 'raw_headers', 'raw_trace']:
            path = ROOT / attempt[field]
            if path.exists():
                bindings.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})
    known = next(x for x in read(RUN / 'publication/root-news-unplanned-batch1-source-acceptance.json')['accepted_images'] if x['original'] == report['original'])
    rows = json.loads((ROOT / attempts[-1]['raw_body']).read_bytes())
    assert rows[0] == ['timestamp', 'original', 'mimetype', 'statuscode', 'digest', 'length']
    assert any(row[0] == known['actual_capture_timestamp'] and row[1].replace(':80/', '/') == known['original'] and row[2] == known['mime'] and row[3] == '200' and row[4] == known['cdx_digest'] for row in rows[1:])
    assert total == report['total_body_bytes'] <= 262144 and report['elapsed_seconds'] < 60
    assert streak == report['failure_streak_end'] == 0 and shutil.disk_usage(ROOT).free >= 11005853696
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'resume_gate_passed': True, 'control_final_streak': 0, 'failure_streak_start': 0,
              'failure_streak_after_direct': 1, 'failure_streak_end': 0, 'requests': 2,
              'accepted_images': [], 'control_success_finished_utc': report['control_success_finished_utc'],
              'source_failure_receipt_sha256': sha(prior_path), 'private_evidence_bindings': bindings,
              'private_report_sha256': sha(DIRECTORY / 'control-report.json'),
              'observed': 'Direct TCP timeout; TLS-verified proxy exact CDX succeeds in 1.924 seconds after the 503 cooldown. Prefix targets remain unknown.',
              'tls_verification': True, 'settings_changed': False, 'actual_body_bytes': total}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': True, 'sha256': sha(OUT), 'resume_gate_passed': True}))


if __name__ == '__main__':
    main()

"""One root-specified two-request CDX control; save private evidence only."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import time
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261018'
OUT = BASE / 'network/control-after-gallery15'
SOURCE = BASE / 'publication/root-gallery-retry2-source-acceptance.json'
KNOWN = BASE / 'publication/root-news-unplanned-batch1-source-acceptance.json'
ORIGINAL = 'http://www.worldofwarcraft.com/news/images/08-02/02-14-08-2.jpg'
URL = ('https://web.archive.org/cdx/search/cdx?url=' + quote(ORIGINAL, safe='')
       + '&from=20000101000000&to=20080512210044&output=json&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest%2Clength&limit=10&showResumeKey=true&matchType=exact')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stamp = lambda: datetime.now(timezone.utc).isoformat()


def main():
    assert not OUT.exists(), 'Preserve completed or interrupted control directory'
    prior = json.loads(SOURCE.read_bytes())
    assert prior['accepted'] and prior['failure_streak_end'] == 0
    assert prior['batch_report_sha256'] == '4c5a6ea3ea474fd3d66733b00a5798844380dace8bea8cb370348b58c954a0fe'
    assert prior['stop_reason'] == 'endpoint_status_503' and prior['resume_gate_passed'] is False
    assert datetime.now(timezone.utc) >= datetime.fromisoformat(prior['cooldown_not_before_utc'].replace('Z', '+00:00'))
    known = next(x for x in json.loads(KNOWN.read_bytes())['accepted_images'] if x['original'] == ORIGINAL)
    parser_path = ROOT / 'research/continuous-recovery-20261016/network/control02-plan/control02_driver.py'
    spec = importlib.util.spec_from_file_location('root_control_header_parser', parser_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    assert shutil.disk_usage(ROOT).free >= 11005853696
    OUT.mkdir()
    started, first_dispatch = time.monotonic(), None
    report = {'started_utc': stamp(), 'source_sha256': sha(SOURCE), 'known_source_sha256': sha(KNOWN),
              'script_sha256': sha(Path(__file__)), 'original': ORIGINAL, 'query_url': URL,
              'failure_streak_start': 0, 'failure_streak_end': 0, 'attempts': [],
              'control_positive': False, 'payload_replays': 0, 'settings_changed': False,
              'tls_verification': True, 'maximum_requests': 2, 'maximum_body_bytes': 262144,
              'maximum_seconds': 60, 'header_parser_sha256': sha(parser_path)}
    total, streak = 0, 0
    for transport in ['direct', 'proxy']:
        if first_dispatch is not None:
            while time.monotonic() - first_dispatch < 5.25:
                time.sleep(min(.1, 5.25 - (time.monotonic() - first_dispatch)))
        assert time.monotonic() - started < 35
        disk = shutil.disk_usage(ROOT).free
        assert disk >= 11005853696
        prefix = OUT / transport
        body, headers, trace = [prefix.with_suffix('.' + suffix) for suffix in ['body', 'headers.txt', 'trace.txt']]
        command = ['curl.exe', '--silent', '--show-error', '--verbose', '--header', 'Accept-Encoding: identity',
                   '--connect-timeout', '4' if transport == 'direct' else '8', '--max-time', '12' if transport == 'direct' else '20',
                   '--max-filesize', '131072', '--dump-header', str(headers), '--output', str(body),
                   '--write-out', '%{http_code}\n%{time_connect}\n%{time_appconnect}\n%{time_starttransfer}\n%{time_total}', URL]
        command[1:1] = ['--noproxy', '*'] if transport == 'direct' else ['--noproxy', '', '--proxy', 'http://127.0.0.1:7890']
        dispatch = time.monotonic()
        if first_dispatch is None:
            first_dispatch = dispatch
        attempt_start = stamp()
        with trace.open('wb') as stream:
            try:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=stream, timeout=25, check=False)
            except subprocess.TimeoutExpired as exc:
                result = SimpleNamespace(returncode=None, stdout=exc.stdout or b'')
        payload = body.read_bytes() if body.exists() else b''
        raw_headers = headers.read_bytes() if headers.exists() else b''
        parsed = helper.parse_headers(raw_headers)
        status = parsed['status']
        total += len(payload)
        assert total <= 262144 and len(payload) <= 131072
        streak = streak + 1 if status is None else 0
        positive = False
        parse_error = None
        if result.returncode == 0 and status == 200:
            try:
                rows = json.loads(payload)
                assert rows and rows[0] == ['timestamp', 'original', 'mimetype', 'statuscode', 'digest', 'length']
                positive = any(len(row) == 6 and row[0] == known['actual_capture_timestamp'] and row[1].replace(':80/', '/') == ORIGINAL
                               and row[2] == known['mime'] and row[3] == '200' and row[4] == known['cdx_digest'] for row in rows[1:])
            except (ValueError, AssertionError, TypeError) as exc:
                parse_error = str(exc)
        report['attempts'].append({'transport': transport, 'started_utc': attempt_start, 'finished_utc': stamp(),
                                   'dispatch_monotonic': dispatch, 'curl_exit': result.returncode, 'source_status': status,
                                   'metrics': result.stdout.decode(errors='replace'), 'parse_error': parse_error, 'body_bytes': len(payload),
                                   'body_sha256': hashlib.sha256(payload).hexdigest(), 'positive_known_row': positive,
                                   'disk_free_before_bytes': disk, 'raw_body': body.relative_to(ROOT).as_posix(),
                                   'raw_headers': headers.relative_to(ROOT).as_posix(), 'raw_trace': trace.relative_to(ROOT).as_posix()})
        report['failure_streak_end'] = streak
        if status in {429, 503}:
            cooldown = max(120, parsed.get('retry_after') or 0)
            report['cooldown_not_before_utc'] = (datetime.now(timezone.utc) + timedelta(seconds=cooldown)).isoformat()
            report['stop_reason'] = 'http_rate_or_service_stop'
            break
        if positive:
            report['control_positive'] = True
            report['control_success_finished_utc'] = stamp()
            break
    report.update(finished_utc=stamp(), elapsed_seconds=time.monotonic() - started,
                  total_body_bytes=total, disk_free_after_bytes=shutil.disk_usage(ROOT).free)
    assert report['elapsed_seconds'] < 60
    (OUT / 'control-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key not in {'attempts', 'query_url'}}))


if __name__ == '__main__':
    main()

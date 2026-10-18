"""Independently accept saved late-window CDX indexes, without network access."""
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261018'
DIRECTORY = BASE / 'network/gallery-late-window-20261018'
OUTPUT = BASE / 'publication/root-gallery-late-window-source-acceptance.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
FIELDS = ['urlkey', 'timestamp', 'original', 'mimetype', 'statuscode', 'digest', 'length']


def main():
    assert not OUTPUT.exists()
    approved = read(BASE / 'publication/root-gallery-late-window-plan-acceptance.json')
    assert approved['accepted']
    for binding in approved['bindings']:
        assert sha(ROOT / binding['path']) == binding['sha256']
    prepared = read(DIRECTORY / 'plan.json')
    candidates = {item['rank']: item for item in prepared['candidates']}
    report = read(DIRECTORY / 'batch-report.json')
    policy = report['policy']
    assert report['payload_replay_count'] == 0 and not report['continuation_followed']
    assert report['script_sha256'] == sha(DIRECTORY / 'gallery_late_window_driver_v1.py')
    assert report['plan_sha256'] == sha(DIRECTORY / 'execution-plan.json')
    assert report['input_binding_sha256'] == sha(DIRECTORY / 'execution-input-bindings.json')
    assert policy['max_attempts'] == 8 and policy['window_seconds'] == 180
    assert policy['max_total_body_bytes'] == 16 * 1024**2 and policy['max_entity_body_bytes'] == 8 * 1024**2
    for binding in policy['input_bindings'].values():
        assert sha(ROOT / binding['path']) == binding['sha256']
    attempts, results = [], []
    total = source_count = 0
    for candidate in report['candidate_results']:
        expected = candidates[candidate['rank']]
        query = parse_qs(urlsplit(candidate['query_url']).query)
        window = expected['query_window']
        assert query['url'] == [expected['prefix']] and query['matchType'] == ['prefix']
        assert query['from'] == [window['from']] and query['to'] == [window['to']]
        assert query['limit'] == ['500'] and query['showResumeKey'] == ['true'] and 'collapse' not in query
        assert candidate['prefix'] == expected['prefix']
        aa = candidate['attempts']
        assert [a['transport'] for a in aa] in (['direct'], ['direct', 'proxy'])
        rows, resume, valid = [], [], False
        for attempt in aa:
            attempts.append(attempt)
            body = (ROOT / attempt['raw']['body']).read_bytes()
            headers = (ROOT / attempt['raw']['headers.txt']).read_bytes()
            assert len(body) == attempt['body_bytes']
            if body:
                assert hashlib.sha256(body).hexdigest() == attempt['body_sha256']
            assert attempt['disk_free_before_bytes'] >= 11005853696 and attempt['clamp']['dispatch_allowed']
            assert len(body) <= attempt['clamp']['entity_body_limit_before_bytes'] <= 8 * 1024**2
            total += len(body)
            statuses = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})', headers)
            if attempt['source_status'] is None:
                assert attempt['curl_exit'] != 0 and not body and (not statuses or statuses == [b'200'])
                continue
            source_count += 1
            assert statuses[-1].decode() == str(attempt['source_status'])
            if attempt['source_status'] == 200:
                assert attempt['curl_exit'] == 0
                payload = json.loads(body)
                rows, resume = [], []
                if payload:
                    assert payload[0] == FIELDS
                    for record in payload[1:]:
                        assert isinstance(record, list)
                        if len(record) == 7:
                            rows.append(dict(zip(FIELDS, record)))
                        elif len(record) == 1 and record[0]:
                            resume.append(record[0])
                        else:
                            assert not record
                assert len(rows) == attempt['cdx_record_count'] and resume == attempt['resume_keys']
                valid = True
        assert len(rows) == candidate['capture_index_count'] and resume == candidate['resume_keys']
        assert bool(resume or len(rows) >= 500) == bool(candidate['potential_truncation'] or candidate['resume_keys'])
        prefix = urlsplit(candidate['prefix'])
        exact, variants, images = [], [], []
        for row in rows:
            assert window['from'] <= row['timestamp'] <= window['to']
            parsed = urlsplit(row['original'])
            literal = re.fullmatch(r'ss[1-9][0-9]*(?:-thumb)?\.jpg', parsed.path[len(prefix.path):]) if parsed.path.startswith(prefix.path) else None
            if row['statuscode'] == '200' and row['mimetype'].startswith('image/'):
                images.append(row)
                if literal and not parsed.query and not parsed.fragment:
                    (exact if (parsed.scheme, parsed.hostname, parsed.port or 80) == (prefix.scheme, prefix.hostname, prefix.port or 80) else variants).append(row)
        assert len(exact) == len(candidate['strict_literal_full_candidates']) + len(candidate['strict_literal_thumb_candidates'])
        assert len(variants) == len(candidate['direct_identity_variant_candidates'])
        results.append({'gallery': expected['gallery'], 'prefix': candidate['prefix'], 'query_window': window,
                        'valid_index': valid, 'index_rows': len(rows), 'resume_keys': resume,
                        'complete': valid and not resume and len(rows) < 500,
                        'direct_exact_candidates': len(exact), 'direct_variant_candidates': len(variants),
                        'image_index_rows': len(images), 'rows': rows})
    assert len(attempts) == report['network_requests'] <= 8 and total == report['total_body_bytes'] <= 16 * 1024**2
    assert source_count == report['source_responses']
    streak = 0
    for number, attempt in enumerate(attempts):
        streak = streak + 1 if attempt['source_status'] is None else 0
        if streak >= 5 or attempt['source_status'] in (429, 503):
            assert number == len(attempts) - 1
    assert streak == report['failure_streak']
    dispatch = [b['dispatch_monotonic'] - a['dispatch_monotonic'] for a, b in zip(attempts, attempts[1:])]
    starts = [(datetime.fromisoformat(b['started_utc']) - datetime.fromisoformat(a['started_utc'])).total_seconds() for a, b in zip(attempts, attempts[1:])]
    assert not dispatch or min(dispatch) >= 5.25
    assert not starts or min(starts) >= 5
    elapsed = (datetime.fromisoformat(report['finished_utc']) - datetime.fromisoformat(report['window_started_utc'])).total_seconds()
    assert elapsed < 180
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'requests': len(attempts), 'source_responses': source_count, 'body_bytes': total,
              'index_rows': sum(x['index_rows'] for x in results),
              'direct_exact_candidates': sum(x['direct_exact_candidates'] for x in results),
              'direct_variant_candidates': sum(x['direct_variant_candidates'] for x in results),
              'accepted_images': [], 'payload_replays': 0, 'failure_streak_start': 0, 'failure_streak_end': streak,
              'stop_reason': report['stop_reason'], 'minimum_dispatch_seconds': min(dispatch, default=None),
              'minimum_start_seconds': min(starts, default=None), 'elapsed_seconds': elapsed,
              'disk_free_after_bytes': free, 'batch_report_sha256': sha(DIRECTORY / 'batch-report.json'),
              'source_plan_sha256': sha(DIRECTORY / 'plan.json'), 'results': results,
              'scope': 'Late-window captured index records only; no image replay. An absent direct row is not an individual replay 404. Earlier complete windows and native gallery counters remain separate.'}
    OUTPUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key not in {'results', 'accepted_images'}}))


if __name__ == '__main__':
    main()

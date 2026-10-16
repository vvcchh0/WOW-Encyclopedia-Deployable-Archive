"""Independently recount saved prefix indexes; retain cadence deviation."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BATCH = ROOT / 'research/continuous-recovery-20261016/network/gallery-prefix01'


def main():
    data = (BATCH / 'batch-report.json').read_bytes()
    report = json.loads(data)
    assert len(report['candidate_results']) == 10
    assert report['payload_replay_count'] == 0 and not report['continuation_followed']
    attempts, results, image_rows = [], [], []
    for candidate in report['candidate_results']:
        query = parse_qs(urlsplit(candidate['query_url']).query)
        assert query['url'] == [candidate['prefix']]
        assert query['matchType'] == ['prefix'] and query['limit'] == ['500']
        assert query['from'] == ['20060101000000'] and query['to'] == ['20080512210044']
        assert query['showResumeKey'] == ['true'] and 'collapse' not in query
        assert [a['transport'] for a in candidate['attempts']] == ['direct', 'proxy']
        rows, source_count = [], 0
        for attempt in candidate['attempts']:
            attempts.append(attempt)
            body = (ROOT / attempt['raw']['body']).read_bytes()
            headers = (ROOT / attempt['raw']['headers.txt']).read_bytes()
            assert len(body) == attempt['body_bytes']
            if body:
                assert hashlib.sha256(body).hexdigest() == attempt['body_sha256']
            assert attempt['disk_free_before_bytes'] >= 11005853696
            assert attempt['clamp']['dispatch_allowed']
            statuses = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})', headers)
            if attempt['source_status'] == 200:
                assert statuses[-1] == b'200' and attempt['curl_exit'] == 0
                payload = json.loads(body)
                if payload:
                    assert payload[0] == ['urlkey', 'timestamp', 'original', 'mimetype', 'statuscode', 'digest', 'length']
                    assert all(isinstance(row, list) and len(row) == 7 for row in payload[1:])
                    rows = [dict(zip(payload[0], row)) for row in payload[1:]]
                assert len(rows) < 500
                source_count += 1
            else:
                assert not body and attempt['curl_exit'] != 0
                assert not statuses or statuses == [b'200']  # proxy CONNECT only
        assert source_count == candidate['source_response_count']
        assert len(rows) == candidate['capture_index_count']
        assert not candidate['resume_keys'] and not candidate['potential_truncation']
        strict, valid_images = [], []
        prefix = urlsplit(candidate['prefix'])
        for row in rows:
            assert '20060101000000' <= row['timestamp'] <= '20080512210044'
            original = urlsplit(row['original'])
            valid = (row['statuscode'] == '200' and row['mimetype'].startswith('image/'))
            same = (original.scheme, original.netloc) == (prefix.scheme, prefix.netloc)
            if valid and same and original.path.startswith(prefix.path):
                valid_images.append(row)
                remainder = original.path[len(prefix.path):]
                if re.fullmatch(r'ss[1-9][0-9]*(?:-thumb)?\.jpg', remainder) and not original.query:
                    strict.append(row)
        assert not strict
        image_rows.extend(valid_images)
        results.append({'label': candidate['label'], 'prefix': candidate['prefix'],
                        'source_responses': source_count, 'index_rows': len(rows),
                        'exact_origin_image_rows': len(valid_images), 'direct_gallery_image_rows': 0,
                        'status': 'valid_complete_index' if source_count else 'transport_unknown'})
    assert len(attempts) == report['network_requests'] == 20
    total = sum(a['body_bytes'] for a in attempts)
    assert total == report['total_body_bytes'] == 25954
    dispatch = [b['dispatch_monotonic'] - a['dispatch_monotonic'] for a, b in zip(attempts, attempts[1:])]
    starts = [(datetime.fromisoformat(b['started_utc']) - datetime.fromisoformat(a['started_utc'])).total_seconds()
              for a, b in zip(attempts, attempts[1:])]
    assert min(starts) >= 5 and min(dispatch) >= 5  # stricter target separately fails
    assert max(a['body_bytes'] for a in attempts) < 16 * 1024**2 and total < 64 * 1024**2
    elapsed = (datetime.fromisoformat(report['finished_utc']) - datetime.fromisoformat(report['window_started_utc'])).total_seconds()
    assert elapsed < 900
    streak = 0
    for a in attempts:
        streak = streak + 1 if a['transport_error'] else 0
        assert streak < 5 and a['source_status'] not in (429, 503)
    assert streak == report['failure_streak'] == 2
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'evidence_accepted': True,
              'execution_policy_compliant': False, 'accepted_with_recorded_deviation': True,
              'batch_report_sha256': hashlib.sha256(data).hexdigest(),
              'requests': len(attempts), 'source_responses': sum(r['source_responses'] for r in results),
              'index_rows': sum(r['index_rows'] for r in results), 'body_bytes': total,
              'recovered_payloads': 0, 'direct_gallery_candidates': 0, 'failure_streak_end': streak,
              'minimum_dispatch_seconds': min(dispatch), 'required_dispatch_seconds': 5.1,
              'minimum_request_start_seconds': min(starts), 'elapsed_seconds': elapsed,
              'deviation': 'Five dispatch intervals were 5.093/5.094s rather than >=5.1s; no requests were repeated. Next driver requires monotonic recheck and safety margin.',
              'scope': 'Nine complete prefix indexes and one transport-unknown prefix, exact HTTP origin and pre-anchor window only.',
              'results': results,
              'nested_or_other_exact_origin_image_rows': image_rows}
    (OUT / 'root-gallery-prefix01-acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('results', 'nested_or_other_exact_origin_image_rows')}))


if __name__ == '__main__':
    main()

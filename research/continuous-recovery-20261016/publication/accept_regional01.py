"""Root review of the three regional prefix-index responses."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NETWORK = ROOT / 'research/continuous-recovery-20261016/network/regional01'

def main():
    data = (NETWORK / 'batch-report.json').read_bytes()
    report = json.loads(data)
    attempts = report['attempts']
    assert len(attempts) == report['source_request_count'] == 6
    assert report['candidate_count'] == 0 and report['replay'] is False
    total = 0
    rows = []
    for attempt in attempts:
        assert attempt['kind'] == 'cdx'
        query = parse_qs(urlsplit(attempt['url']).query)
        assert query['matchType'] == ['prefix'] and query['limit'] == ['100']
        assert query['from'] == ['20060101000000'] and query['to'] == ['20080512210044']
        path = NETWORK / attempt['raw']['body']
        body = path.read_bytes() if path.exists() else b''
        total += len(body)
        assert len(body) == attempt['body_bytes']
        assert not body or hashlib.sha256(body).hexdigest() == attempt['body_sha256']
        if attempt['source_status'] == 200:
            headers = (NETWORK / attempt['raw']['headers']).read_bytes()
            assert re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})',headers)[-1] == b'200'
            assert json.loads(body) == []
            rows.append({'prefix':query['url'][0], 'source_status':200,'returned_rows':0,
                'body_sha256':hashlib.sha256(body).hexdigest()})
    assert len(rows) == report['source_response_count'] == 3 and total == report['total_body_bytes'] == 9
    dispatch = [x['dispatch']['dispatch_monotonic'] for x in attempts]
    starts = [datetime.fromisoformat(x['started_utc']) for x in attempts]
    min_dispatch = min(b-a for a,b in zip(dispatch,dispatch[1:]))
    min_start = min((b-a).total_seconds() for a,b in zip(starts,starts[1:]))
    assert min_dispatch >= 5.1 and min_start >= 5
    assert (datetime.fromisoformat(report['finished_utc'])-starts[0]).total_seconds() <= 480
    assert report['disk_preflight']['disk_free_bytes'] >= 11005853696
    assert report['disk_postflight']['disk_free_bytes'] >= 11005853696
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,
        'scope':'Three hypothesis-labelled literal prefixes only; zero index rows in this bounded query window.',
        'requests':6,'source_responses':3,'response_body_bytes':9,'new_images':0,'queries':rows,
        'minimum_dispatch_seconds':min_dispatch,'minimum_start_seconds':min_start,
        'batch_report_sha256':hashlib.sha256(data).hexdigest(),
        'conclusion':'Do not repeat these prefixes. Discover actual regional navigation paths before further queries.'}
    (OUT/'root-regional01-acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'accepted':True,'requests':6,'source_responses':3,'new_images':0}))

if __name__ == '__main__':
    main()

"""Root acceptance of queued news images and the actual bounded request log."""
import base64
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from PIL import Image, ImageSequence
from accept_news02_assets import identity
from accept_news01_assets import header_value, sha

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NETWORK = ROOT / 'research/continuous-recovery-20261016/network/allnews01'

def main():
    report_bytes = (NETWORK / 'batch-report.json').read_bytes()
    report = json.loads(report_bytes)
    mapping = json.loads((NETWORK / 'source-map.json').read_bytes())
    queue = json.loads((NETWORK / 'queue.json').read_bytes())['entries']
    attempts = report['attempts']
    by_key = {item['target_key']:item['original'] for item in queue}
    assert len(by_key) == len(queue) == 20
    assert len(attempts) == report['source_request_count'] <= 80
    assert all(item['target_key'] in by_key for item in report['results'])
    total = streak = 0
    for index, attempt in enumerate(attempts):
        assert attempt['executed'] is True and attempt['target_key'] in by_key
        assert attempt['dispatch']['disk_free_before_bytes'] >= 11005853696
        original = by_key[attempt['target_key']]
        if attempt['kind'] == 'cdx':
            query = parse_qs(urlsplit(attempt['url']).query)
            assert query['url'] == [original] and query['limit'] == ['250'] and query['matchType'] == ['exact']
        else:
            assert attempt['kind'] == 'replay' and attempt['url'].startswith('https://web.archive.org/web/')
        path = NETWORK / attempt['raw']['body']
        body = path.read_bytes() if path.exists() else b''
        assert len(body) == attempt['body_bytes'] <= 16777216
        assert not body or sha(body) == attempt['body_sha256']
        total += len(body)
        if attempt['source_status'] is not None:
            headers = (NETWORK / attempt['raw']['headers']).read_bytes()
            statuses = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})[^\r\n]*', headers)
            assert int(statuses[-1]) == attempt['source_status']
        streak = streak + 1 if attempt['transport_error'] else 0
        if attempt['source_status'] in {429,503} or streak >= 5:
            assert index == len(attempts)-1
    assert total == report['total_body_bytes'] <= 134217728
    dispatches = [x['dispatch']['dispatch_monotonic'] for x in attempts]
    starts = [datetime.fromisoformat(x['started_utc']) for x in attempts]
    min_dispatch = min(b-a for a,b in zip(dispatches,dispatches[1:]))
    min_start = min((b-a).total_seconds() for a,b in zip(starts,starts[1:]))
    elapsed = (datetime.fromisoformat(attempts[-1]['finished_utc'])-starts[0]).total_seconds()
    assert min_dispatch >= 5.1 and min_start >= 5 and elapsed <= 1800
    assert report['disk_postflight']['disk_free_bytes'] >= 11005853696
    accepted = []
    for entry in mapping['entries']:
        original = entry['logical_url']
        result = next(x for x in report['results'] if x['original'] == original)
        cdx_attempt = next(x for x in result['cdx_attempts'] if x['source_status'] == 200 and x['curl_exit'] == 0)
        index_bytes = (NETWORK / cdx_attempt['raw']['body']).read_bytes()
        rows = json.loads(index_bytes)
        records = [dict(zip(rows[0],row)) for row in rows[1:]] if rows else []
        assert len(records) < 250
        eligible = [x for x in records if identity(x['original']) == identity(original) and x['statuscode'] == '200'
            and x['mimetype'] in {'image/jpeg','image/gif'} and '20060101000000' <= x['timestamp'] <= '20080512210044']
        capture = max(eligible,key=lambda x:x['timestamp'])
        body = (NETWORK / entry['raw_body_path']).read_bytes()
        headers = (NETWORK / entry['raw_headers_path']).read_bytes()
        assert re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})',headers)[-1] == b'200'
        actual = parsedate_to_datetime(header_value(headers,'Memento-Datetime')).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')
        originals = [x.decode('latin1') for x in re.findall(rb'<([^>]+)>;\s*rel="original"',headers)]
        assert any(identity(url) == identity(capture['original']) for url in originals)
        mime = header_value(headers,'Content-Type').split(';')[0].strip().lower()
        digest = base64.b32encode(hashlib.sha1(body).digest()).decode().rstrip('=')
        assert actual == capture['timestamp'] == entry['capture_timestamp']
        assert mime == entry['mime'] == capture['mimetype']
        assert digest == capture['digest'] == entry['cdx_digest']
        assert len(body) == entry['body_bytes'] and sha(body) == entry['body_sha256']
        with Image.open(io.BytesIO(body)) as image:
            image.verify()
        with Image.open(io.BytesIO(body)) as image:
            size, image_format = list(image.size), image.format
            frames = 0
            for frame in ImageSequence.Iterator(image):
                frame.load()
                frames += 1
        assert image_format == {'image/jpeg':'JPEG','image/gif':'GIF'}[mime]
        accepted.append({'original':original,'captured_original':capture['original'],'actual_timestamp':actual,
            'mime':mime,'dimensions':size,'decoded_frames':frames,'length':len(body),'sha256':sha(body),
            'cdx_digest':digest,'cdx_raw_body_sha256':sha(index_bytes),
            'raw_body_path':(NETWORK / entry['raw_body_path']).relative_to(ROOT).as_posix(),'accepted':True})
    assert len(accepted) == report['valid_image_count']
    result = {'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,
        'scope':'Actual batch limits and listed payloads verified; unresolved originals remain separate.',
        'accepted_images':accepted,'total_image_bytes':sum(x['length'] for x in accepted),
        'queued_originals':len(queue),'visited_originals':len(report['results']),'requests':len(attempts),
        'source_responses':sum(x['source_status'] is not None for x in attempts),'actual_all_body_bytes':total,
        'elapsed_seconds':elapsed,'minimum_dispatch_seconds':min_dispatch,'minimum_start_seconds':min_start,
        'trailing_transfer_failures':streak,'stop_reason':report['stop_reason'],
        'remaining_results':[{'original':x['original'],'category_as_reported':x['category'],
            'cdx_source_200':any(a['source_status']==200 and a['curl_exit']==0 for a in x['cdx_attempts']),
            'replay_source_statuses':[a['source_status'] for a in x['replay_attempts']],
            'potential_truncation':x.get('cdx_counts',{}).get('potential_truncation') if x.get('cdx_counts') else None}
            for x in report['results'] if not x['accepted']],
        'batch_report_sha256':sha(report_bytes),'source_map_sha256':sha((NETWORK/'source-map.json').read_bytes()),'errors':[]}
    (OUT/'root-allnews01-acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['accepted','queued_originals','visited_originals','requests','total_image_bytes']}))

if __name__ == '__main__':
    main()

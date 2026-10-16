"""Root validation of NEWS02 selected CDX records, raw payloads and limits."""
import base64
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit
from PIL import Image, ImageSequence
from accept_news01_assets import header_value, sha

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'research/continuous-recovery-20261016/network/news02'

def identity(url):
    p = urlsplit(url)
    return p.scheme.lower(), p.hostname.lower(), p.port or (80 if p.scheme == 'http' else 443), p.path, p.query

def main():
    mapping = json.loads((OUT / 'source-map.json').read_bytes())
    report = json.loads((OUT / 'batch-report.json').read_bytes())
    errors, accepted = [], []
    attempts = report['attempts']
    actual_bytes = 0
    for attempt in attempts:
        path = OUT / attempt['raw']['body']
        body = path.read_bytes() if path.exists() else b''
        actual_bytes += len(body)
        if len(body) != attempt['body_bytes'] or (body and sha(body) != attempt['body_sha256']):
            errors.append('attempt_raw_binding:' + str(attempt['attempt']))
    for item in mapping['entries']:
        original, timestamp = item['logical_url'], item['capture_timestamp']
        source = next(x for x in report['results'] if x['target'] == original)
        cdx_attempt = next(x for x in source['cdx']['attempts'] if x['source_status'] == 200)
        index_bytes = (OUT / cdx_attempt['raw']['body']).read_bytes()
        rows = json.loads(index_bytes)
        records = [dict(zip(rows[0], row)) for row in rows[1:]] if rows else []
        eligible = [x for x in records if identity(x['original']) == identity(original) and x['statuscode'] == '200'
            and x['mimetype'] in {'image/jpeg', 'image/gif'} and '20060101000000' <= x['timestamp'] <= '20080512210044']
        row = max(eligible, key=lambda x: x['timestamp'])
        body = (OUT / item['raw_body_path']).read_bytes()
        headers = (OUT / item['raw_headers_path']).read_bytes()
        statuses = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})[^\r\n]*', headers)
        memento = header_value(headers, 'Memento-Datetime')
        actual = parsedate_to_datetime(memento).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S') if memento else None
        links = [x.decode('latin1') for x in re.findall(rb'<([^>]+)>;\s*rel="original"', headers)]
        mime = (header_value(headers, 'Content-Type') or '').split(';')[0].strip().lower()
        digest = base64.b32encode(hashlib.sha1(body).digest()).decode().rstrip('=')
        with Image.open(io.BytesIO(body)) as image:
            image.verify()
        with Image.open(io.BytesIO(body)) as image:
            dimensions, image_format = list(image.size), image.format
            frames = 0
            for frame in ImageSequence.Iterator(image):
                frame.load()
                frames += 1
        okay = (statuses[-1] == b'200' and any(identity(url) == identity(row['original']) for url in links)
            and actual == timestamp == row['timestamp'] and mime == row['mimetype'] == item['mime']
            and digest == row['digest'] == item['cdx_digest'] and sha(body) == item['body_sha256'] and len(body) == item['body_bytes']
            and image_format == ('JPEG' if mime == 'image/jpeg' else 'GIF'))
        if not okay:
            errors.append('payload_acceptance:' + original)
        accepted.append({'original': original, 'captured_original': row['original'], 'actual_timestamp': actual,
            'cdx_digest': digest, 'sha256': sha(body), 'length': len(body), 'mime': mime, 'dimensions': dimensions,
            'decoded_frames': frames, 'raw_body_path': (OUT / item['raw_body_path']).relative_to(ROOT).as_posix(),
            'cdx_raw_body_sha256': sha(index_bytes), 'accepted': okay})
    dispatches = [x['dispatch']['dispatch_monotonic'] for x in attempts]
    starts = [datetime.fromisoformat(x['started_utc']) for x in attempts]
    intervals = [b - a for a, b in zip(dispatches, dispatches[1:])]
    utc_intervals = [(b - a).total_seconds() for a, b in zip(starts, starts[1:])]
    elapsed = (datetime.fromisoformat(report['request_window_finished_utc']) - starts[0]).total_seconds()
    source_responses = sum(x['source_status'] is not None for x in attempts)
    if len(attempts) != report['source_request_count'] or len(attempts) > 40 or elapsed > 1200 or actual_bytes != report['total_body_bytes'] or actual_bytes > 67108864:
        errors.append('batch_limit_or_byte_binding')
    if min(intervals) < 5.1 or min(utc_intervals) < 5.0 or source_responses != report['source_response_count']:
        errors.append('cadence_or_source_count')
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'accepted': not errors and len(accepted) == 6,
        'accepted_images': accepted, 'total_image_bytes': sum(x['length'] for x in accepted), 'requests': len(attempts),
        'source_responses': source_responses, 'actual_all_body_bytes': actual_bytes, 'elapsed_seconds': elapsed,
        'minimum_dispatch_seconds': min(intervals), 'minimum_start_seconds': min(utc_intervals),
        'remaining_targets': [{'original': x['target'], 'category': x['category']} for x in report['results'] if x['category'] != 'valid_image'],
        'source_map_sha256': sha((OUT / 'source-map.json').read_bytes()), 'batch_report_sha256': sha((OUT / 'batch-report.json').read_bytes()),
        'errors': errors}
    Path(__file__).with_name('root-news02-acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    if not result['accepted']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

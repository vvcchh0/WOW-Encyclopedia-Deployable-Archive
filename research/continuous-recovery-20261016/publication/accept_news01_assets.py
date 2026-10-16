"""Root acceptance of raw news JPEGs against original CDX and replay headers."""
import base64
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'research/continuous-recovery-20261016/network/news01'
OLD = ROOT / 'research/continuous-recovery-20261015/network-news-assets13'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def header_value(data, field):
    values = re.findall(rb'(?im)^' + re.escape(field.encode()) + rb':\s*([^\r\n]+)', data)
    return values[-1].decode('latin1').strip() if values else None

def main():
    mapping = json.loads((OUT / 'source-map.json').read_bytes())
    report = json.loads((OUT / 'batch-report.json').read_bytes())
    old = json.loads((OLD / 'batch-report.json').read_bytes())
    errors, accepted = [], []
    for item in mapping['entries']:
        original, timestamp = item['logical_url'], item['capture_timestamp']
        prior = next(x for x in old['results'] if x['target'] == original)
        cdx_attempt = next(x for x in prior['cdx']['attempts'] if x['source_status'] == 200)
        index_bytes = (OLD / cdx_attempt['raw']['body']).read_bytes()
        if sha(index_bytes) != cdx_attempt['body_sha256']:
            errors.append('CDX raw binding:' + original)
        rows = json.loads(index_bytes)
        records = [dict(zip(rows[0], row)) for row in rows[1:]]
        row = next(x for x in records if x['original'] == original and x['timestamp'] == timestamp)
        body = (OUT / item['raw_body_path']).read_bytes()
        headers = (OUT / item['raw_headers_path']).read_bytes()
        status_lines = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})[^\r\n]*', headers)
        digest = base64.b32encode(hashlib.sha1(body).digest()).decode().rstrip('=')
        memento = header_value(headers, 'Memento-Datetime')
        actual = parsedate_to_datetime(memento).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S') if memento else None
        links = re.findall(rb'<([^>]+)>;\s*rel="original"', headers)
        exact_original = original.encode() in links
        mime = header_value(headers, 'Content-Type') or ''
        with Image.open(io.BytesIO(body)) as image:
            image.verify()
        with Image.open(io.BytesIO(body)) as image:
            image.load()
            dimensions, image_format = list(image.size), image.format
        okay = (status_lines[-1] == b'200' and exact_original and actual == timestamp and timestamp <= '20080512210044'
            and row['statuscode'] == '200' and row['mimetype'] == 'image/jpeg' and digest == row['digest'] == item['cdx_digest']
            and sha(body) == item['body_sha256'] and len(body) == item['body_bytes']
            and mime.split(';')[0].strip().lower() == 'image/jpeg' and body.startswith(b'\xff\xd8\xff') and image_format == 'JPEG')
        if not okay:
            errors.append('payload acceptance:' + original)
        accepted.append({'original': original, 'actual_timestamp': actual, 'cdx_digest': digest,
            'sha256': sha(body), 'length': len(body), 'mime': 'image/jpeg', 'dimensions': dimensions,
            'raw_body_path': (OUT / item['raw_body_path']).relative_to(ROOT).as_posix(),
            'cdx_raw_body_sha256': sha(index_bytes), 'accepted': okay})
    initial = json.loads((OUT / 'dispatch-log-parser-failure.json').read_bytes())['dispatches']
    dispatches = [x['dispatch_monotonic'] for x in initial] + [x['dispatch']['dispatch_monotonic'] for x in report['attempts']]
    starts = [datetime.fromisoformat(x['dispatch_utc']) for x in initial] + [datetime.fromisoformat(x['started_utc']) for x in report['attempts']]
    intervals = [b - a for a, b in zip(dispatches, dispatches[1:])]
    utc_intervals = [(b - a).total_seconds() for a, b in zip(starts, starts[1:])]
    count = len(dispatches)
    elapsed = (datetime.fromisoformat(report['request_window_finished_utc']) - starts[0]).total_seconds()
    if count != report['cumulative_source_request_count'] or count > 12 or elapsed > 720 or min(intervals) < 5.1 or min(utc_intervals) < 5.0:
        errors.append('cumulative batch policy')
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'accepted': not errors and len(accepted) == 3,
        'accepted_images': accepted, 'total_image_bytes': sum(x['length'] for x in accepted),
        'requests_including_initial_parser_failure': count, 'valid_run_requests': len(report['attempts']),
        'minimum_dispatch_seconds': min(intervals), 'minimum_start_seconds': min(utc_intervals), 'elapsed_seconds': elapsed,
        'batch_report_sha256': sha((OUT / 'batch-report.json').read_bytes()),
        'source_map_sha256': sha((OUT / 'source-map.json').read_bytes()),
        'prior_parser_failure': 'One direct attempt saved no source response; parser fix used a separately recorded run. Both are counted here.', 'errors': errors}
    path = Path(__file__).with_name('root-news01-acceptance.json')
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    if not result['accepted']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

"""Root verification of NEWS03/04 using actual index, response and image bytes."""
import base64
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from PIL import Image, ImageSequence
from accept_news02_assets import identity
from accept_news01_assets import header_value, sha

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def accept(batch):
    directory = ROOT / f'research/continuous-recovery-20261016/network/{batch}'
    report = json.loads((directory / 'batch-report.json').read_bytes())
    mapping = json.loads((directory / 'source-map.json').read_bytes())
    policy = report['policy']
    errors, images = [], []
    total = streak = 0
    attempts = report['attempts']
    for attempt in attempts:
        path = directory / attempt['raw']['body']
        body = path.read_bytes() if path.exists() else b''
        total += len(body)
        if len(body) != attempt['body_bytes'] or (body and sha(body) != attempt['body_sha256']):
            errors.append('raw_attempt_binding:' + str(attempt['attempt']))
        recorded_free = attempt['dispatch'].get('disk_free_before_bytes')
        if recorded_free is not None and recorded_free < 11005853696:
            errors.append('disk_floor')
        streak = streak + 1 if attempt['transport_error'] else 0
        if (attempt['source_status'] in {429, 503} or streak >= 5) and attempt != attempts[-1]:
            errors.append('continued_after_stop_condition')
    for entry in mapping['entries']:
        original = entry['logical_url']
        source = next(x for x in report['results'] if x['target'] == original)
        if batch == 'news03':
            cdx = ROOT / source['cdx_revalidated']['raw_body']
            assert sha(cdx.read_bytes()) == source['cdx_revalidated']['raw_body_sha256']
        else:
            attempt = next(x for x in source['cdx']['attempts'] if x['source_status'] == 200)
            cdx = directory / attempt['raw']['body']
        raw_index = cdx.read_bytes()
        rows = json.loads(raw_index)
        records = [dict(zip(rows[0], row)) for row in rows[1:]] if rows else []
        eligible = [x for x in records if identity(x['original']) == identity(original)
            and x['statuscode'] == '200' and x['mimetype'] in {'image/jpeg', 'image/gif'}
            and '20060101000000' <= x['timestamp'] <= '20080512210044']
        row = max(eligible, key=lambda x: x['timestamp'])
        body = (directory / entry['raw_body_path']).read_bytes()
        headers = (directory / entry['raw_headers_path']).read_bytes()
        statuses = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})[^\r\n]*', headers)
        actual = parsedate_to_datetime(header_value(headers, 'Memento-Datetime')).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')
        links = [x.decode('latin1') for x in re.findall(rb'<([^>]+)>;\s*rel="original"', headers)]
        mime = header_value(headers, 'Content-Type').split(';')[0].strip().lower()
        digest = base64.b32encode(hashlib.sha1(body).digest()).decode().rstrip('=')
        with Image.open(io.BytesIO(body)) as image:
            image.verify()
        with Image.open(io.BytesIO(body)) as image:
            size, image_format = list(image.size), image.format
            frames = 0
            for frame in ImageSequence.Iterator(image):
                frame.load()
                frames += 1
        valid = statuses[-1] == b'200' and any(identity(link) == identity(row['original']) for link in links)
        valid = valid and actual == entry['capture_timestamp'] == row['timestamp']
        valid = valid and digest == entry['cdx_digest'] == row['digest'] and sha(body) == entry['body_sha256']
        valid = valid and len(body) == entry['body_bytes'] and mime == entry['mime'] == row['mimetype']
        valid = valid and image_format == {'image/jpeg': 'JPEG', 'image/gif': 'GIF'}[mime]
        if not valid:
            errors.append('image_gate:' + original)
        images.append({'original': original, 'captured_original': row['original'], 'actual_timestamp': actual,
            'mime': mime, 'dimensions': size, 'decoded_frames': frames, 'length': len(body), 'sha256': sha(body),
            'cdx_digest': digest, 'cdx_raw_body_sha256': sha(raw_index),
            'raw_body_path': (directory / entry['raw_body_path']).relative_to(ROOT).as_posix(), 'accepted': valid})
    intervals = [b['dispatch']['dispatch_monotonic'] - a['dispatch']['dispatch_monotonic'] for a, b in zip(attempts, attempts[1:])]
    starts = [datetime.fromisoformat(x['started_utc']) for x in attempts]
    start_intervals = [(b-a).total_seconds() for a,b in zip(starts,starts[1:])]
    elapsed = (datetime.fromisoformat(report['request_window_finished_utc']) - starts[0]).total_seconds()
    if len(attempts) != report['source_request_count'] or len(attempts) > policy['max_attempts'] or elapsed > policy['window_seconds']:
        errors.append('request_or_duration_limit')
    if total != report['total_body_bytes'] or total > policy['max_total_body_bytes'] or min(intervals) < 5.1 or min(start_intervals) < 5:
        errors.append('byte_or_cadence_limit')
    preflight = json.loads((directory / 'preflight.json').read_bytes())
    cooldown = preflight.get('cooldown_satisfied', preflight.get('previous_batch', {}).get('cooldown_satisfied'))
    if not cooldown or report['disk_postflight']['disk_free_bytes'] < 11005853696:
        errors.append('cooldown_or_post_disk')
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'batch': batch,
        'accepted': not errors and len(images) == 2, 'accepted_images': images,
        'total_image_bytes': sum(x['length'] for x in images), 'requests': len(attempts),
        'source_responses': sum(x['source_status'] is not None for x in attempts),
        'actual_all_body_bytes': total, 'elapsed_seconds': elapsed,
        'minimum_dispatch_seconds': min(intervals), 'minimum_start_seconds': min(start_intervals),
        'prior_cooldown_satisfied': cooldown, 'batch_report_sha256': sha((directory / 'batch-report.json').read_bytes()),
        'per_attempt_disk_values_recorded': all('disk_free_before_bytes' in x['dispatch'] for x in attempts),
        'disk_evidence_note': 'NEWS03 records per-attempt values. NEWS04 has batch pre/post values and a per-request guard in its driver; individual values were not retained.',
        'source_map_sha256': sha((directory / 'source-map.json').read_bytes()), 'errors': errors}
    (OUT / f'root-{batch}-acceptance.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['batch','accepted','total_image_bytes','requests','errors']}))
    assert result['accepted']

if __name__ == '__main__':
    for batch in ['news03', 'news04']:
        accept(batch)

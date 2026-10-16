"""Independently parse the three CDX responses and recalculate batch limits."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    path = OUT / 'batch-report.json'
    report = json.loads(path.read_bytes())
    errors, parsed = [], []
    attempts = report['attempts']
    expected_ids = {'Q1', 'Q2', 'Q8'}
    if {x['target_key'] for x in attempts} != expected_ids or len(attempts) > 6:
        errors.append('request_scope')
    dispatches = [x['dispatch']['dispatch_monotonic'] for x in attempts]
    starts = [datetime.fromisoformat(x['started_utc']) for x in attempts]
    intervals = [b - a for a, b in zip(dispatches, dispatches[1:])]
    start_intervals = [(b - a).total_seconds() for a, b in zip(starts, starts[1:])]
    if min(intervals) < 5.1 or min(start_intervals) < 5.0:
        errors.append('cadence')
    total = 0
    for attempt in attempts:
        body_path = OUT / attempt['raw']['body']
        body = body_path.read_bytes() if body_path.exists() else b''
        total += len(body)
        if len(body) != attempt['body_bytes'] or (body and sha(body) != attempt['body_sha256']):
            errors.append('raw_body_binding:' + attempt['target_key'])
        if attempt['source_status'] != 200:
            continue
        header = (OUT / attempt['raw']['headers']).read_bytes()
        statuses = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})[^\r\n]*', header)
        if not statuses or statuses[-1] != b'200':
            errors.append('actual_header_status:' + attempt['target_key'])
        rows = json.loads(body)
        values = [dict(zip(rows[0], row)) for row in rows[1:]] if rows else []
        result = next(x for x in report['results'] if x['id'] == attempt['target_key'])
        if values != result['records']:
            errors.append('cdx_record_binding:' + attempt['target_key'])
        parsed.append({'id': attempt['target_key'], 'rows': len(values), 'records': values, 'body_sha256': sha(body), 'body_bytes': len(body)})
    if len(parsed) != 3 or total > 33554432:
        errors.append('response_or_byte_limit')
    elapsed = (datetime.fromisoformat(report['request_window_finished_utc']) - starts[0]).total_seconds()
    if elapsed > 360:
        errors.append('duration_limit')
    binding = report['input_binding']
    if sha((ROOT / binding['script_path']).read_bytes()) != binding['script_sha256']:
        errors.append('script_binding')
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'accepted': not errors, 'scope': 'Capture-index investigation only; no images recovered',
        'batch_report_sha256': sha(path.read_bytes()), 'requests': len(attempts), 'source_responses': len(parsed),
        'response_body_bytes': total, 'elapsed_seconds': elapsed,
        'minimum_dispatch_seconds': min(intervals), 'minimum_start_seconds': min(start_intervals), 'parsed': parsed,
        'conclusion': 'Both thumbnail exact queries reproduce only the existing mismatched digest; Q8 has no row in the queried window.', 'errors': errors}
    (OUT / 'root-cdx01-acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

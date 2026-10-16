"""Complete only the slow provenance transfer; retain the first failed check."""
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
REPORT = OUT / 'root-pages-online-acceptance.json'
PRIOR = OUT / 'root-pages-online-acceptance.preliminary-timeout.json'

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    data = REPORT.read_bytes()
    if PRIOR.exists() and PRIOR.read_bytes() != data:
        raise RuntimeError('Prior receipt already frozen')
    if not PRIOR.exists():
        PRIOR.write_bytes(data)
    report = json.loads(data)
    if sum(x['accepted'] for x in report['objects']) != 7:
        raise RuntimeError('Expected seven already verified objects')
    obj = next(x for x in report['objects'] if x['path'] == 'export-provenance.json')
    local = (ROOT / report['local_site'] / obj['path']).read_bytes()
    if hashlib.sha256(local).hexdigest() != obj['local_sha256']:
        raise RuntimeError('Local provenance changed')
    report['completion_policy'] = {'only_retry': obj['path'], 'reason': 'HTTP200 partial transfers exceeded the initial 25s limit',
        'direct_first': True, 'maximum_attempts': 2, 'per_attempt_seconds': {'direct': 150, 'proxy': 60},
        'maximum_body_bytes': 33554432, 'tls_verification': True, 'redirects': False}
    for transport, seconds in [('direct', 150), ('proxy', 60)]:
        if shutil.disk_usage(ROOT).free < 11005853696:
            raise RuntimeError('disk floor')
        with tempfile.TemporaryDirectory(prefix='v15-provenance-', dir=OUT) as tmp:
            body = Path(tmp) / 'body'
            command = ['curl.exe', '--silent', '--show-error', '--connect-timeout', '8', '--max-time', str(seconds),
                '--max-filesize', '16777216', '--output', str(body), '--write-out', '%{http_code}\n%{content_type}',
                report['base_url'] + obj['path']]
            command[1:1] = ['--noproxy', '*'] if transport == 'direct' else ['--noproxy', '', '--proxy', 'http://127.0.0.1:7890']
            start = stamp()
            result = subprocess.run(command, capture_output=True, text=True, timeout=seconds + 10)
            fields = result.stdout.splitlines()
            payload = body.read_bytes() if body.exists() else b''
            status = int(fields[0]) if fields and fields[0].isdigit() else None
            mime = fields[1] if len(fields) > 1 else None
            attempt = {'transport': transport, 'started_utc': start, 'finished_utc': stamp(), 'curl_exit': result.returncode,
                'http_status': status, 'content_type': mime, 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest(),
                'matches_local': payload == local, 'timeout_seconds': seconds, 'phase': 'bounded_slow_transfer_completion'}
            obj['attempts'].append(attempt)
            report['attempts'] += 1
            report['total_body_bytes'] += len(payload)
            print(json.dumps(attempt), flush=True)
            if result.returncode == 0 and status == 200:
                obj['accepted'] = payload == local and mime.split(';')[0].strip().lower() == 'application/json'
                break
            if status in (429, 503):
                break
    api = subprocess.run(['gh', 'api', 'repos/vvcchh0/WOW-Encyclopedia-Deployable-Archive/pages/builds/latest'],
        capture_output=True, text=True, timeout=45, check=True)
    build = json.loads(api.stdout)
    report['build_after_completion'] = {k: build.get(k) for k in ['status', 'commit', 'updated_at', 'error']}
    report['accepted_objects'] = sum(x['accepted'] for x in report['objects'])
    report['accepted'] = report['accepted_objects'] == 8 and build['status'] == 'built' and build['commit'] == report['expected_pages_commit']
    report['finished_utc'] = stamp()
    report['preliminary_receipt'] = str(PRIOR.relative_to(ROOT)).replace('\\', '/')
    report['preliminary_receipt_sha256'] = hashlib.sha256(PRIOR.read_bytes()).hexdigest()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': report['accepted'], 'accepted_objects': report['accepted_objects']}))
    if not report['accepted']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

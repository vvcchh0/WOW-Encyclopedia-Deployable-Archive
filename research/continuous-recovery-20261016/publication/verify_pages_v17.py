"""Bind the published v17 deployment to accepted local objects."""
import hashlib
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261016-v17'
BASE = 'https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/'

def stamp():
    return datetime.now(timezone.utc).isoformat()

def build_state():
    data = json.loads(subprocess.run(['gh', 'api', 'repos/vvcchh0/WOW-Encyclopedia-Deployable-Archive/pages/builds/latest'],
        capture_output=True, text=True, check=True, timeout=45).stdout)
    return {k: data.get(k) for k in ['status', 'commit', 'updated_at', 'error']}

def main():
    expected = json.loads((OUT / 'v17-pages-publication.json').read_bytes())['new_commit_sha']
    gate = json.loads((OUT / 'root-v17-export-acceptance.json').read_bytes())
    assert gate['accepted']
    guide_map = json.loads((ROOT / 'research/continuous-recovery-20261016/integration/guide-previews-source-map.json').read_bytes())
    paths = gate['changed_paths'] + [item['route'].lstrip('/') for group in guide_map['groups'] for item in group['previews']]
    paths += ['info/encyclopedia/index.xml.html', 'news/rss-08-2007.xml.html']
    assert len(paths) == 63
    assert len(paths) == len(set(paths))
    before = build_state()
    assert before['status'] == 'built' and before['commit'] == expected, before
    report = {'schema': 'wow-pages-publication-acceptance/v1', 'started_utc': stamp(),
        'expected_pages_commit': expected, 'local_site': str(SITE.relative_to(ROOT)), 'base_url': BASE,
        'build_before': before, 'objects': [], 'policy': {'direct_first': True, 'tls_verification': True,
        'redirects': False, 'maximum_attempts': 130, 'maximum_seconds': 900,
        'maximum_body_bytes': 67108864, 'large_object_timeout_seconds': 150, 'other_timeout_seconds': 25}}
    deadline = time.monotonic() + 900
    count = total = 0
    mimes = {'.js': {'application/javascript', 'text/javascript', 'application/x-javascript'},
        '.html': {'text/html'}, '.json': {'application/json'}, '.jpg': {'image/jpeg'}, '.gif': {'image/gif'}}
    for relative in paths:
        local = (SITE / relative).read_bytes()
        obj = {'path': relative, 'local_bytes': len(local), 'local_sha256': hashlib.sha256(local).hexdigest(),
            'attempts': [], 'accepted': False}
        for transport in ['direct', 'proxy']:
            if time.monotonic() >= deadline or count >= 130 or total >= 67108864:
                break
            count += 1
            timeout = 150 if len(local) > 4000000 else 25
            with tempfile.TemporaryDirectory(prefix='v17-online-', dir=OUT) as tmp:
                body = Path(tmp) / 'body'
                cmd = ['curl.exe', '--silent', '--show-error', '--max-time', str(timeout),
                    '--connect-timeout', '8', '--max-filesize', '16777216', '--output', str(body),
                    '--write-out', '%{http_code}\n%{content_type}', BASE + relative]
                cmd[1:1] = ['--noproxy', '*'] if transport == 'direct' else ['--noproxy', '', '--proxy', 'http://127.0.0.1:7890']
                started = stamp()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
                fields = result.stdout.splitlines()
                payload = body.read_bytes() if body.exists() else b''
                total += len(payload)
                status = int(fields[0]) if fields and fields[0].isdigit() else None
                mime = fields[1] if len(fields) > 1 else ''
                attempt = {'transport': transport, 'started_utc': started, 'finished_utc': stamp(),
                    'curl_exit': result.returncode, 'http_status': status, 'content_type': mime,
                    'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest(), 'matches_local': payload == local}
                obj['attempts'].append(attempt)
                if result.returncode == 0 and status == 200:
                    obj['accepted'] = payload == local and mime.split(';')[0].strip().lower() in mimes[Path(relative).suffix]
                    break
                if status in {429, 503}:
                    break
        report['objects'].append(obj)
        print(json.dumps({'path': relative, 'accepted': obj['accepted']}), flush=True)
        (OUT / 'v17-online-progress.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    report.update(build_after=build_state(), finished_utc=stamp(), attempts=count, total_body_bytes=total)
    report['accepted_objects'] = sum(obj['accepted'] for obj in report['objects'])
    report['accepted'] = report['accepted_objects'] == len(paths) and report['build_after']['status'] == 'built' and report['build_after']['commit'] == expected
    (OUT / 'root-v17-pages-online-acceptance.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': report['accepted'], 'objects': report['accepted_objects']}))
    return 0 if report['accepted'] else 1

if __name__ == '__main__':
    raise SystemExit(main())

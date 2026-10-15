"""Bounded direct-first byte verification of the published v10 archive."""
import hashlib
import json
import pathlib
import subprocess
import tempfile
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261015-v10'
BASE = 'https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/'
EXPECTED_COMMIT = json.loads((OUT/'root-pages-publication.json').read_text(encoding='utf-8'))['new_commit_sha']
PATHS = [
    'index.html', 'news/rss-04-2008.xml.html', 'news/rss-03-2008.xml.html',
    'news/rss-02-2008.xml.html', 'news/rss-01-2008.xml.html',
    'news/rss-05-2007.xml.html', 'news/rss-01-2007.xml.html', 'news/rss-07-2006.xml.html',
    'wrath/artwork.xml.html', 'wrath/art.xml.html', 'wrath/js/screeniesimplified.js',
    'wrath/images/layout/pixel.gif', '__offline/route-map.json',
    'downloads/ssotd/images/screens/ss1336.jpg',
]

def expected_mime(relative, content_type):
    mime = (content_type or '').split(';', 1)[0].strip().lower()
    if relative.endswith('.html'): return mime == 'text/html'
    if relative.endswith('.js'): return mime in {'application/javascript','text/javascript','application/x-javascript'}
    if relative.endswith('.json'): return mime == 'application/json'
    if relative.endswith('.gif'): return mime == 'image/gif'
    if relative.endswith('.jpg'): return mime == 'image/jpeg'
    return False


def stamp():
    return datetime.now(timezone.utc).isoformat()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def build_state():
    result = subprocess.run([
        'gh', 'api',
        'repos/vvcchh0/WOW-Encyclopedia-Deployable-Archive/pages/builds/latest'
    ], capture_output=True, text=True, timeout=45, check=True)
    data = json.loads(result.stdout)
    return {k: data.get(k) for k in ['status', 'commit', 'updated_at', 'error']}

def main():
    deadline = time.monotonic() + 480
    total_bytes = attempts = 0
    report = {'schema': 'wow-pages-publication-acceptance/v1',
              'started_utc': stamp(), 'base_url': BASE,
              'expected_pages_commit': EXPECTED_COMMIT,
              'local_site': str(SITE.relative_to(ROOT)),
              'policy': {'direct_first': True, 'tls_verification': True,
                         'redirects': False, 'per_attempt_timeout_seconds': 25,
                         'maximum_attempts': 28, 'maximum_seconds':480, 'maximum_body_bytes':67108864},
              'build_before': build_state(), 'objects': []}
    if (report['build_before']['status'] != 'built' or
            report['build_before']['commit'] != EXPECTED_COMMIT):
        raise RuntimeError('Expected Pages build has not completed')
    for relative in PATHS:
        local = (SITE / relative).read_bytes()
        obj = {'path': relative, 'local_bytes': len(local),
               'local_sha256': sha(local), 'attempts': [], 'accepted': False}
        for transport in ['direct', 'proxy']:
            if time.monotonic() >= deadline or attempts >= 28 or total_bytes >= 67108864:
                break
            attempts += 1
            with tempfile.TemporaryDirectory(prefix='pages-check-', dir=OUT) as tmp:
                body = pathlib.Path(tmp) / 'body'
                cmd = ['curl.exe', '--silent', '--show-error', '--max-time', '25',
                       '--connect-timeout', '8', '--max-filesize', '16777216',
                       '--output', str(body), '--write-out',
                       '%{http_code}\n%{content_type}', BASE + relative]
                cmd[1:1] = (['--noproxy', '*'] if transport == 'direct' else
                            ['--noproxy', '', '--proxy', 'http://127.0.0.1:7890'])
                started = stamp()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                fields = result.stdout.splitlines()
                status = int(fields[0]) if fields and fields[0].isdigit() else None
                payload = body.read_bytes() if body.exists() else b''
                total_bytes += len(payload)
                attempt = {'transport': transport, 'started_utc': started,
                           'finished_utc': stamp(), 'curl_exit': result.returncode,
                           'http_status': status,
                           'content_type': fields[1] if len(fields) > 1 else None,
                           'bytes': len(payload), 'sha256': sha(payload),
                           'matches_local': payload == local}
                obj['attempts'].append(attempt)
                if result.returncode == 0 and status == 200:
                    obj['accepted'] = payload == local and expected_mime(relative, attempt['content_type'])
                    break
                if status in (429, 503):
                    break
        report['objects'].append(obj)
        print(json.dumps({'path': relative, 'accepted': obj['accepted']}, ensure_ascii=False), flush=True)
    report['build_after'] = build_state()
    report['finished_utc'] = stamp()
    report['attempts'] = attempts
    report['total_body_bytes'] = total_bytes
    report['accepted_objects'] = sum(x['accepted'] for x in report['objects'])
    report['accepted'] = (report['accepted_objects'] == len(PATHS) and
                          report['build_after']['status'] == 'built' and
                          report['build_after']['commit'] == EXPECTED_COMMIT)
    (OUT / 'root-pages-online-acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': report['accepted'], 'objects': report['accepted_objects']}))
    return 0 if report['accepted'] else 1

if __name__ == '__main__':
    raise SystemExit(main())

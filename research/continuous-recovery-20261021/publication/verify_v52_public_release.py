"""Check anonymous small assets and the ZIP HEAD after publication, without redownloading the ZIP."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-v52-release-public-download-acceptance.json'
PRIVATE = ROOT / '.scratch/v52-public-download-check'
assert not OUT.exists() and not PRIVATE.exists()
release = json.loads((PUB / 'root-v52-release-publication.json').read_bytes())
assert release['accepted'] is True and release['published'] is True
assert release['tag'] == 'archive-20080512-browser-20261021-v52'
PRIVATE.mkdir()
environment = os.environ.copy()
for key in list(environment):
    if key.lower() in {'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy'}:
        environment.pop(key, None)
started = time.monotonic()
attempts = []
checks = []
for asset in sorted(release['assets'], key=lambda row: row['name']):
    is_zip = asset['name'].endswith('.zip')
    method = 'HEAD' if is_zip else 'GET'
    expected_url = ('https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/download/'
                    + release['tag'] + '/' + asset['name'])
    assert asset['browser_download_url'] == expected_url
    accepted = False
    for transport, proxy in (('direct', ''), ('proxy', 'http://127.0.0.1:7890')):
        assert time.monotonic() - started < 180
        assert shutil.disk_usage(ROOT).free >= 11005853696
        destination = PRIVATE / (asset['name'] + '.' + transport + ('.headers' if is_zip else '.body'))
        assert not destination.exists()
        command = ['curl.exe', '--silent', '--show-error', '--fail', '--location',
                   '--max-redirs', '5', '--connect-timeout', '10', '--max-time', '30',
                   '--proxy', proxy, '--noproxy', '*' if not proxy else '',
                   '--output', str(destination),
                   '--write-out', '%{http_code}\t%{content_type}\t%{size_download}\t%{num_redirects}']
        command += ['--head'] if is_zip else ['--max-filesize', '8192']
        command.append(expected_url)
        before = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True,
                                text=True, timeout=40)
        fields = result.stdout.strip().split('\t')
        status = int(fields[0]) if fields and fields[0].isdigit() else 0
        row = {'name': asset['name'], 'method': method, 'transport': transport,
               'started_utc': before, 'finished_utc': datetime.now(timezone.utc).isoformat(),
               'curl_exit': result.returncode, 'http_status': status,
               'redirect_count': int(fields[3]) if len(fields) == 4 else None,
               'tls_verification': True}
        if result.returncode == 0 and status == 200:
            body = destination.read_bytes()
            if is_zip:
                blocks = re.split(rb'\r?\n\r?\n', body)
                headers = [block for block in blocks if re.match(rb'HTTP/\S+ 200\b', block)]
                assert headers
                lengths = re.findall(rb'(?im)^content-length:\s*(\d+)\s*$', headers[-1])
                row['content_length'] = int(lengths[-1]) if lengths else None
                row['downloaded_zip_body_bytes'] = int(fields[2])
                accepted = row['content_length'] == asset['bytes'] and row['downloaded_zip_body_bytes'] == 0
            else:
                row['bytes'] = len(body)
                row['sha256'] = hashlib.sha256(body).hexdigest()
                accepted = len(body) == asset['bytes'] and row['sha256'] == asset['expected_sha256']
        row['accepted'] = accepted
        attempts.append(row)
        if accepted:
            break
        if status in {429, 503}:
            raise RuntimeError('Release endpoint limited; no retry')
        if result.returncode not in {5, 6, 7, 28, 35, 52, 56, 60}:
            break
    checks.append({'name': asset['name'], 'url': expected_url, 'method': method, 'accepted': accepted})
report = {'accepted': all(row['accepted'] for row in checks),
          'checked_utc': datetime.now(timezone.utc).isoformat(), 'version': 'v52',
          'anonymous': True, 'authorization_headers': False,
          'zip_body_downloaded': False, 'checks': checks, 'attempts': attempts,
          'elapsed_seconds': round(time.monotonic() - started, 3),
          'scope': 'Exact small-asset bytes and ZIP final HEAD length; the full ZIP digest is independently checked locally and by GitHub asset metadata in the separate publication acceptance.'}
OUT.write_bytes((json.dumps(report, indent=2) + '\n').encode())
print(json.dumps({'accepted': report['accepted'], 'checks': len(checks),
                  'attempts': len(attempts), 'zip_body_downloaded': False}))
assert report['accepted']

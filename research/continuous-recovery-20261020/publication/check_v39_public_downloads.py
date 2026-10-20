"""Check anonymous release downloads without re-downloading the large ZIP."""
import hashlib
import json
import shutil
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import HTTPSHandler, HTTPRedirectHandler, ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
HOSTS = {'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'}


class Redirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        assert parsed.scheme == 'https' and parsed.hostname in HOSTS
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def main():
    out = PUB / 'root-v39-public-download-acceptance.json'
    assert not out.exists()
    release = json.loads((PUB / 'root-v39-release-publication.json').read_bytes())
    assert release['accepted'] and release['published']
    assets = {a['name']: a for a in release['assets']}
    checks = []
    for suffix, method in (('.zip', 'HEAD'), ('.zip.sha256', 'GET')):
        asset = next(a for name, a in assets.items() if name.endswith(suffix))
        attempts = []
        for mode in ('direct', 'proxy'):
            assert shutil.disk_usage(ROOT).free >= 11005853696
            proxy = {} if mode == 'direct' else {'https': 'http://127.0.0.1:7890'}
            opener = build_opener(ProxyHandler(proxy), HTTPSHandler(context=ssl.create_default_context()), Redirect())
            try:
                with opener.open(Request(asset['browser_download_url'], method=method), timeout=30) as response:
                    body = response.read(2048) if method == 'GET' else b''
                    assert response.status == 200
                    assert urlsplit(response.url).hostname in HOSTS
                    assert int(response.headers['Content-Length']) == asset['bytes']
                    if method == 'GET':
                        assert len(body) == asset['bytes'] and hashlib.sha256(body).hexdigest() == asset['expected_sha256']
                    attempts.append({'transport': mode, 'status': response.status, 'content_length': int(response.headers['Content-Length']), 'body_bytes_read': len(body), 'final_host': urlsplit(response.url).hostname, 'accepted': True})
                    break
            except Exception as exc:
                attempts.append({'transport': mode, 'accepted': False, 'error_type': type(exc).__name__})
        checks.append({'asset': asset['name'], 'method': method, 'url': asset['browser_download_url'], 'attempts': attempts, 'accepted': attempts[-1]['accepted']})
    result = {'accepted': all(c['accepted'] for c in checks), 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'anonymous_requests': True, 'tls_verification': True, 'checks': checks,
        'scope': 'Anonymous public ZIP HEAD confirms exact full length; public SHA sidecar GET matches its local digest. TLS and redirect-host checks enabled. Signed redirect queries/response cookies are not retained; full ZIP byte verification is the separate local/GitHub asset-digest evidence.'}
    out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))
    assert result['accepted']


if __name__ == '__main__':
    main()

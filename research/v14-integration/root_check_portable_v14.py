"""Independently read the accepted ZIP, then serve its extracted copy in isolation."""
import hashlib
import json
import re
import shutil
import stat
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.request import ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/v14-integration'
SITE = ROOT / '.scratch/pages-resources-20261015-v14'
ARCHIVE = ROOT / 'artifacts/WOW_Encyclopedia_20080512_browser_20261015_v14.zip'
EXTRACT = ROOT / '.scratch/local bundle smoke 20261015 v14'
FLOOR = 11005853696


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    final = json.loads((OUT / 'root-final-acceptance.json').read_bytes())
    assert final['accepted'], 'Final browse acceptance is required'
    before = shutil.disk_usage(ROOT).free
    assert before >= FLOOR and not EXTRACT.exists()
    producer = json.loads((OUT / 'portable-package-report.json').read_bytes())
    provenance_bytes = (SITE / 'export-provenance.json').read_bytes()
    provenance = json.loads(provenance_bytes)
    export_receipt_bytes = (OUT / 'root-export-acceptance.json').read_bytes()
    export_receipt = json.loads(export_receipt_bytes)
    assert sha(export_receipt_bytes) == final['gates']['export']['sha256']
    assert sha(provenance_bytes) == export_receipt['export_provenance_sha256']
    expected = {'site/' + x['output_path']: (x['derived_sha256'], x['derived_length'])
                for x in provenance['files']}
    expected['site/export-provenance.json'] = (sha(provenance_bytes), len(provenance_bytes))
    for relative in ['NOTICE.md', 'tools/serve_pages_preview.py']:
        data = (ROOT / relative).read_bytes()
        expected[relative] = (sha(data), len(data))
    with ARCHIVE.open('rb') as stream:
        archive_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    assert archive_sha == producer['verification']['archive_sha256']
    checked_bytes = 0
    compression = {}
    with zipfile.ZipFile(ARCHIVE) as zf:
        infos = zf.infolist()
        names = [x.filename for x in infos]
        allowed = set(expected) | {'README.md', 'START_BROWSE.cmd', 'archive-metadata.json', 'FILE_SHA256SUMS.txt'}
        assert len(names) == len(set(names)) and set(names) == allowed
        sums = {}
        for line in zf.read('FILE_SHA256SUMS.txt').decode('utf-8').splitlines():
            if line.startswith('#') or not line:
                continue
            digest, length, relative = line.split('  ', 2)
            assert relative not in sums
            sums[relative] = (digest, int(length))
        assert set(sums) == allowed - {'FILE_SHA256SUMS.txt'}
        for item in infos:
            path = PurePosixPath(item.filename)
            suffix = path.suffix.lower()
            group = ('markup' if suffix in {'.html', '.xml', '.xsl'} else
                     'scripts_and_styles' if suffix in {'.js', '.css'} else
                     'images' if suffix in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico'} else
                     'other')
            totals = compression.setdefault(group, {'members': 0, 'uncompressed_bytes': 0, 'compressed_member_bytes': 0})
            totals['members'] += 1
            totals['uncompressed_bytes'] += item.file_size
            totals['compressed_member_bytes'] += item.compress_size
            mode = item.external_attr >> 16
            assert not path.is_absolute() and '..' not in path.parts and '\\' not in item.filename
            assert ':' not in path.parts[0] and not stat.S_ISLNK(mode)
            data = zf.read(item)  # zipfile checks the member CRC while reading.
            actual = (sha(data), len(data))
            checked_bytes += len(data)
            if item.filename in expected:
                assert actual == expected[item.filename], item.filename
            if item.filename in sums:
                assert actual == sums[item.filename], item.filename
        assert before - checked_bytes >= FLOOR
        EXTRACT.mkdir()
        zf.extractall(EXTRACT)
    requests = []
    server_log = OUT / 'portable-server-local.log'
    child = None
    try:
        with server_log.open('w', encoding='utf-8') as log:
            child = subprocess.Popen([sys.executable, '-I', str(EXTRACT / 'tools/serve_pages_preview.py'),
                                      '--site', str(EXTRACT / 'site'), '--port', '0'],
                                     cwd=EXTRACT, stdout=log, stderr=log,
                                     creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            deadline = time.monotonic() + 20
            base = None
            while time.monotonic() < deadline:
                match = re.search(r'Archive preview: (http://127\.0\.0\.1:\d+/\S*)', server_log.read_text(encoding='utf-8'))
                if match:
                    base = match.group(1)
                    break
                if child.poll() is not None:
                    raise RuntimeError('Packaged server exited before startup')
                time.sleep(0.1)
            assert base
            opener = build_opener(ProxyHandler({}))
            for relative in ['index.html', 'info/encyclopedia/index.xml.html', 'news/rss-01-2008.xml.html', 'news/rss-07-2007.xml.html',
                             'news/rss-06-2007.xml.html', 'news/rss-04-2007.xml.html',
                             'news/rss-09-2006.xml.html','news/rss-05-2008.xml.html','news/rss-12-2007.xml.html',
                             'news/rss-11-2007.xml.html','news/rss-10-2007.xml.html','news/rss-09-2007.xml.html',
                             'news/rss-03-2007.xml.html','news/rss-02-2007.xml.html','news/rss-12-2006.xml.html',
                             'news/rss-11-2006.xml.html','news/rss-08-2006.xml.html','news/rss-10-2006.xml.html',
                             'news/newsarchive.css', 'news/images/08-01/01-10-08-01.jpg',
                             'news/images/08-02/arenatourney2.gif', 'wrath/art.xml.html']:
                local = (EXTRACT / 'site' / relative).read_bytes()
                for method in ['GET', 'HEAD']:
                    with opener.open(Request(base + relative, method=method), timeout=10) as response:
                        body = response.read()
                        assert response.status == 200
                        assert int(response.headers['Content-Length']) == len(local)
                        assert (body == local if method == 'GET' else body == b'')
                        requests.append({'path': relative, 'method': method, 'status': response.status,
                                         'bytes': len(body), 'content_type': response.headers.get('Content-Type')})
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            child.wait(timeout=10)
    after = shutil.disk_usage(ROOT).free
    assert after >= FLOOR
    report = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'accepted': True,
              'archive': ARCHIVE.relative_to(ROOT).as_posix(), 'archive_sha256': archive_sha,
              'archive_bytes': ARCHIVE.stat().st_size, 'members_read': len(names),
              'uncompressed_bytes_read': checked_bytes, 'export_provenance_sha256': sha(provenance_bytes),
              'compression_by_suffix': compression,
              'isolated_server': True, 'python_isolated_flag': True, 'requests': requests,
              'external_network_requests': 0, 'space_before': before, 'space_after': after,
              'scope': 'All ZIP members read and checked; extracted packaged server GET/HEAD smoke. Browser rendering reuses the accepted identical export. Windows launcher double-click was not executed.'}
    (OUT / 'root-portable-acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['accepted', 'archive_bytes', 'members_read', 'uncompressed_bytes_read', 'space_after']}))


if __name__ == '__main__':
    main()

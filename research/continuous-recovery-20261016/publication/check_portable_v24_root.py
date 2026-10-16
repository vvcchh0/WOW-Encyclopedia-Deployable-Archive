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

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'research/continuous-recovery-20261016/publication'
QA_OUT = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261016-v24'
ARCHIVE = ROOT / 'artifacts/WOW_Encyclopedia_20080512_browser_20261016_v24.zip'
EXTRACT = ROOT / '.scratch/local bundle smoke 20261016 v24'
FLOOR = 11005853696
LOCAL_ACCEPTANCE = OUT / 'root-v24-local-acceptance.json'
EXPORT_ACCEPTANCE = OUT / 'root-v24-export-acceptance.json'
PACKAGE_REPORT = OUT / 'v24-portable-package-report.json'
RECEIPT = OUT / 'root-v24-portable-acceptance.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert not RECEIPT.exists()
    final = json.loads(LOCAL_ACCEPTANCE.read_bytes())
    assert final['accepted'], 'Final browse acceptance is required'
    before = shutil.disk_usage(ROOT).free
    assert before >= FLOOR and not EXTRACT.exists()
    producer = json.loads(PACKAGE_REPORT.read_bytes())
    provenance_bytes = (SITE / 'export-provenance.json').read_bytes()
    provenance = json.loads(provenance_bytes)
    export_receipt_bytes = EXPORT_ACCEPTANCE.read_bytes()
    export_receipt = json.loads(export_receipt_bytes)
    assert any(x['path'].endswith('/root-v24-export-acceptance.json') and x['sha256']==sha(export_receipt_bytes) for x in final['bindings'])
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
        assert shutil.disk_usage(ROOT).free >= FLOOR + checked_bytes
        for item in infos:
            assert shutil.disk_usage(ROOT).free >= FLOOR + item.file_size
            zf.extract(item, EXTRACT)
    requests = []
    server_log = QA_OUT / 'v24-portable-server-local.log'
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
            collection=json.loads(provenance_bytes)['guide_image_collections']
            records={x['route']:x for x in provenance['files']}
            assert collection.get('group_count') == 3 and collection.get('image_count') == 32
            collection_pages = []
            for group in collection['groups']:
                collection_pages.extend(records[group[k]]['output_path'] for k in ['guide_route','gallery_route'])
            assert len(set(collection_pages)) == 6
            prior_provenance = json.loads((ROOT / '.scratch/pages-resources-20261016-v23/export-provenance.json').read_bytes())
            prior_overlay_routes = {str(item['route']) for item in prior_provenance.get('files', []) if item.get('role') == 'image_overlay'}
            new_news_paths = [str(item['output_path']) for item in provenance.get('files', []) if item.get('role') == 'image_overlay' and str(item.get('route')) not in prior_overlay_routes]
            paths=['index.html','info/encyclopedia/index.xml.html','news/rss-08-2007.xml.html','pvp/worldpvp/cityattacks-gallery.html','__offline/route-map.json','__offline/pages_runtime.js']
            paths.extend(collection_pages)
            paths.extend(x['route'].lstrip('/') for group in collection['groups'] for x in group['images'])
            paths.extend(new_news_paths)
            browser_receipt=json.loads((OUT/'root-v24-browser-acceptance.json').read_bytes())
            paths.extend('news/'+x['page'] for x in browser_receipt['checks'] if 'page' in x)
            for relative in sorted(set(paths)):
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
    (RECEIPT).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['accepted', 'archive_bytes', 'members_read', 'uncompressed_bytes_read', 'space_after']}))


if __name__ == '__main__':
    main()

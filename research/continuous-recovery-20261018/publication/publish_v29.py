"""Bind the independently accepted v29 export, then publish its exact tree."""
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = OUT.parent
SITE = ROOT / '.scratch/pages-resources-20261018-v29'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}


def prepare():
    target = OUT / 'root-v29-local-acceptance.json'
    assert not target.exists()
    bindings = []
    for name in ['root-v29-input-retry1-acceptance.json', 'root-v29-export-acceptance.json',
                 'root-v29-browser-retry2-acceptance.json', 'root-v29-static-metrics-acceptance.json']:
        path = OUT / name
        receipt = json.loads(path.read_bytes())
        assert receipt['accepted']
        if 'export_provenance_sha256' in receipt:
            assert receipt['export_provenance_sha256'] == sha(SITE / 'export-provenance.json')
        bindings.append(bind(path))
    exported = json.loads((OUT / 'root-v29-export-acceptance.json').read_bytes())
    provenance = json.loads((SITE / 'export-provenance.json').read_bytes())
    records = {item['route']: item for item in provenance['files']}
    paths = set(exported['new_output_paths'] + exported['changed_output_paths'])
    prior_online = OUT / 'root-v28-pages-online-acceptance.json'
    assert json.loads(prior_online.read_bytes())['accepted']
    bindings.append(bind(prior_online))
    paths.add('export-provenance.json')
    mime = {'.html': ['text/html'], '.json': ['application/json'], '.js': ['text/javascript', 'application/javascript', 'application/x-javascript'], '.jpg': ['image/jpeg'], '.gif': ['image/gif'], '.png': ['image/png']}
    objects = []
    for relative in sorted(paths):
        item = bind(SITE / relative)
        item.update(path=relative, source_list=relative == 'export-provenance.json', mime=mime[Path(relative).suffix])
        objects.append(item)
    assert 1 <= len(objects) <= 128
    bindings.extend([bind(RUN / 'integration/v29/v29-primary-source-map.json'), bind(ROOT / 'tools/historical_exhibits.py'), bind(OUT / 'root-historical-news-tool-retry1-acceptance.json')])
    bindings.extend([bind(SITE / 'export-provenance.json'), bind(ROOT / 'tools/export_github_pages.py'), bind(ROOT / 'tools/publish_github_pages.py')])
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
               'local_site': SITE.relative_to(ROOT).as_posix(), 'objects': objects, 'bindings': bindings,
               'new_images_since_live_v28': 40, 'new_image_bytes_since_live_v28': 318622, 'guide_collection_images': 39,
               'declared_files': 8761, 'actual_files': 8762, 'published': False,
               'visual_review': ['v29-news-rss-06-2007.xml.html.png', 'v29-news-rss-10-2007.xml.html.png']}
    target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': True, 'objects': len(objects)}))


def publish():
    report = OUT / 'v29-pages-publication.json'
    assert not report.exists()
    gate = json.loads((OUT / 'root-v29-local-acceptance.json').read_bytes())
    assert gate['accepted']
    for item in gate['bindings']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    for item in gate['objects']:
        assert sha(SITE / item['path']) == item['sha256'], item['path']
    assert shutil.disk_usage(ROOT).free >= 11005853696
    os.environ['GIT_CONFIG_COUNT'] = '3'
    for n, (key, value) in enumerate([('http.proxy', 'http://127.0.0.1:7890'), ('http.lowSpeedLimit', '1024'), ('http.lowSpeedTime', '30')]):
        os.environ[f'GIT_CONFIG_KEY_{n}'] = key
        os.environ[f'GIT_CONFIG_VALUE_{n}'] = value
    spec = importlib.util.spec_from_file_location('publish_accepted_v29', ROOT / 'tools/publish_github_pages.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    result = module.build_commit(root=ROOT, site=SITE, branch='gh-pages',
                               message='Publish v29: restore forty further news illustration resources',
                               report_path=report, push=True)
    print(json.dumps({'status': result['status'], 'commit': result['new_commit_sha']}))


if __name__ == '__main__':
    publish() if '--publish' in sys.argv else prepare()

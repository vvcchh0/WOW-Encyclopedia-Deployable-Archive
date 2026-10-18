"""Bind root-accepted v32, including every change since the actual live v29."""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
RUN = PUB.parent
SITE = ROOT / '.scratch/pages-resources-20261018-v32'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
bind = lambda p: {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size}

def prepare():
    target = PUB / 'root-v32-local-acceptance.json'
    assert not target.exists()
    provenance = read(SITE / 'export-provenance.json')
    provenance_sha = sha(SITE / 'export-provenance.json')
    input_gate = read(PUB / 'root-v32-input-acceptance.json')
    assert input_gate['accepted']
    for item in input_gate['map_bindings']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    assert sha(ROOT / 'tools/publish_github_pages.py') == 'e7f4992dfdeae9f83f6771c538c8d55b084316fb2f2e73c92e874df319de9934'
    bindings = []
    for name in ['root-v32-input-acceptance.json', 'root-v32-export-acceptance.json',
                 'root-v32-browser-acceptance.json', 'root-v32-static-metrics-acceptance.json']:
        path = PUB / name
        data = read(path)
        assert data['accepted']
        if 'export_provenance_sha256' in data:
            assert data['export_provenance_sha256'] == provenance_sha
        bindings.append(bind(path))
    prior_path = ROOT / '.scratch/pages-resources-20261018-v29/export-provenance.json'
    assert sha(prior_path) == '793e99ef3c55ef5d328f8f6773c15b86ca69a79e7504d1333a9c04364dca28f8'
    before = {x['output_path']: x for x in read(prior_path)['files']}
    after = {x['output_path']: x for x in provenance['files']}
    assert set(before) <= set(after)
    new_paths = set(after)-set(before)
    assert len(new_paths) == 136 and all(after[p]['role'] == 'image_overlay' for p in new_paths)
    assert sum(after[p]['derived_length'] for p in new_paths) == 1891055
    changed = {p for p in before if (before[p]['derived_sha256'], before[p]['derived_length']) !=
               (after[p]['derived_sha256'], after[p]['derived_length'])}
    for p, item in before.items():
        if item.get('role') == 'image_overlay':
            assert item == after[p]
    prior_online = PUB / 'root-v29-pages-online-acceptance.json'
    assert read(prior_online)['accepted']
    bindings.extend([bind(prior_path), bind(prior_online)])
    paths = new_paths | changed | {'export-provenance.json'}
    mime = {'.html': ['text/html'], '.json': ['application/json'], '.js': ['text/javascript', 'application/javascript', 'application/x-javascript'],
            '.jpg': ['image/jpeg'], '.gif': ['image/gif'], '.png': ['image/png'], '.css': ['text/css']}
    objects = []
    for relative in sorted(paths):
        item = bind(SITE / relative)
        item.update(path=relative, source_list=relative == 'export-provenance.json', mime=mime[Path(relative).suffix])
        objects.append(item)
    assert 136 < len(objects) <= 256
    bindings.extend(bind(ROOT / value) for value in [
        'tools/export_github_pages.py', 'tools/historical_exhibits.py', 'tools/publish_github_pages.py',
        'research/continuous-recovery-20261018/integration/v32/v32-primary-source-map.json',
        'research/continuous-recovery-20261018/integration/v32/v32-supplement-source-map.json'])
    bindings.append(bind(SITE / 'export-provenance.json'))
    stats = provenance['stats']
    assert stats['output_files'] == 8897 and len(after) == 8897
    assert stats['image_overlay_records'] == 439 and stats['primary_image_overlay_records'] == 350 and stats['supplement_image_overlay_records'] == 89
    assert provenance['guide_image_collections']['image_count'] == 39
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'published': False,
        'local_site': SITE.relative_to(ROOT).as_posix(), 'objects': objects, 'bindings': bindings,
        'actual_previous_online_version': 'v29', 'previous_online_provenance_sha256': sha(prior_path),
        'new_images_since_live_v29': 136, 'new_image_bytes_since_live_v29': 1891055,
        'declared_files': 8897, 'actual_files': 8898, 'guide_collection_images': 39,
        'changed_since_live_v29': sorted(changed),
        'verification_scope': 'All new and changed objects versus live v29, including held v30 additions; max256 objects/512 HTTP attempts/900 seconds/256MiB.'}
    target.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'accepted': True, 'objects': len(objects), 'new_images_since_live_v29': 136}))

def publish():
    report = PUB / 'v32-pages-publication.json'
    assert not report.exists()
    gate = read(PUB / 'root-v32-local-acceptance.json')
    assert gate['accepted']
    for item in gate['bindings']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    for item in gate['objects']:
        assert sha(SITE / item['path']) == item['sha256'], item['path']
    assert shutil.disk_usage(ROOT).free >= 11005853696
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip() == head
    for name in ['tools/export_github_pages.py', 'tools/historical_exhibits.py']:
        data = subprocess.check_output(['git', 'show', f'HEAD:{name}'], cwd=ROOT)
        assert hashlib.sha256(data).hexdigest() == sha(ROOT / name)
    os.environ['GIT_CONFIG_COUNT'] = '3'
    for n, (key, value) in enumerate([('http.proxy','http://127.0.0.1:7890'), ('http.lowSpeedLimit','1024'), ('http.lowSpeedTime','30')]):
        os.environ[f'GIT_CONFIG_KEY_{n}'] = key
        os.environ[f'GIT_CONFIG_VALUE_{n}'] = value
    spec = importlib.util.spec_from_file_location('publish_accepted_v32', ROOT / 'tools/publish_github_pages.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    result = module.build_commit(root=ROOT, site=SITE, branch='gh-pages',
        message='Publish v32: recover news and guide images, attunement chart and image viewer', report_path=report, push=True)
    print(json.dumps({'status': result['status'], 'commit': result['new_commit_sha']}))

if __name__ == '__main__':
    publish() if '--publish' in sys.argv else prepare()

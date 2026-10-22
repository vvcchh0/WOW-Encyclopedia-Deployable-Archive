"""Root acceptance and a fresh derived export; frozen predecessors stay intact."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / '.scratch/pages-resources-20261022-v53'
PREP = HERE / 'integration/v53-input-preparation.json'
FLOOR = 11005853696
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
write = lambda p, x: p.write_bytes((json.dumps(x, ensure_ascii=False, indent=2) + '\n').encode())
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT))

def accept_code():
    import related_guide_images as new
    old_source = subprocess.run(['git', 'show', 'd99d393:tools/related_guide_images.py'], cwd=ROOT, capture_output=True, check=True).stdout
    old = types.ModuleType('accepted_v52_guide_images')
    sys.modules[old.__name__] = old
    exec(compile(old_source, '<accepted-v52-guide-loader>', 'exec'), old.__dict__)
    old_map = ROOT / 'research/continuous-recovery-20261021/integration/related-guide-images-v49/input-map.json'
    old_bundle = old.load_related_guide_image_bundle(old_map, ROOT, '/WOW-Encyclopedia-Deployable-Archive/')
    retained_bundle = new.load_related_guide_image_bundle(old_map, ROOT, '/WOW-Encyclopedia-Deployable-Archive/')
    assert asdict(old_bundle) == asdict(retained_bundle), 'v2 output drift'
    v3 = new.load_related_guide_image_bundle(HERE / 'integration/related-guide-images-v53/input-map.json', ROOT, '/WOW-Encyclopedia-Deployable-Archive/')
    assert len(v3.assets) == 2 and len(v3.route_reuses) == 3
    assert v3.assets[0].data == retained_bundle.assets[0].data
    assert v3.notice_by_page['/burningcrusade/townhall/bestiary.html'] == retained_bundle.notice_by_page['/burningcrusade/townhall/bestiary.html']
    assert v3.assets[1].mime == 'image/png' and len(v3.assets[1].data) == 18846
    import tempfile
    temp = ROOT / '.scratch/test-temp-20261022'
    temp.mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(temp)
    log = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_github_pages_export')
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    log_path = HERE / 'integration/v53-exporter-regression-tests.log'
    log_path.write_bytes(log.getvalue().encode())
    receipt = {
        'schema': 'wow-root-v53-code-acceptance/v1', 'accepted': result.wasSuccessful(),
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'v2_bundle_exactly_unchanged_from_commit': 'd99d393',
        'v3_existing_jpeg_and_notice_unchanged': True,
        'v3_assets': 2, 'v3_route_reuses': 3, 'new_payload_bytes': 18846,
        'tests': {'suite': 'tests.test_github_pages_export', 'run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped), 'log_sha256': sha(log_path)},
        'worker_focused_tests': {'run': 12, 'passed': True, 'evidence': 'integration/related-guide-images-v53/implementation/README.md'},
        'code_bindings': [{'path': p, 'sha256': sha(ROOT / p)} for p in ['tools/related_guide_images.py', 'tests/test_related_guide_images.py', 'tools/export_github_pages.py', 'tests/test_github_pages_export.py']],
    }
    write(HERE / 'root-v53-code-acceptance.json', receipt)
    assert receipt['accepted'] and not receipt['tests']['skipped']
    return receipt

def prepare():
    assert not PREP.exists() and not OUT.exists()
    assert read(HERE / 'root-v53-code-acceptance.json')['accepted']
    prior_path = ROOT / 'research/continuous-recovery-20261021/integration/v52/v52-input-preparation.json'
    prior = read(prior_path)
    allowed_changed = {'tools/related_guide_images.py', 'tests/test_related_guide_images.py'}
    bindings = {}
    for row in prior['bindings']:
        actual = sha(ROOT / row['path'])
        assert actual == row['sha256'] or row['path'] in allowed_changed, row['path']
        bindings[row['path']] = actual
    paths = [HERE / 'root-v53-code-acceptance.json', Path(__file__), prior_path]
    paths.extend(p for p in (HERE / 'integration/related-guide-images-v53').rglob('*') if p.is_file() and 'implementation' not in p.parts)
    for p in paths:
        bindings[p.relative_to(ROOT).as_posix()] = sha(p)
    keys = ('source_site','source_manifest','primary_maps','supplement_maps','guide_preview_map','guide_image_collection_map','flash_runtime_archive','blizzcast_source_map','related_talent_icon_map','source16_layout_map','related_talent_ui_map','talent_box_layout_map','related_encyclopedia_image_map','related_guide_image_map')
    config = {k: prior[k] for k in keys}
    config.update(schema='wow-v53-input-preparation/v1', prepared_utc=datetime.now(timezone.utc).isoformat(),
        related_guide_image_map='research/continuous-recovery-20261022/integration/related-guide-images-v53/input-map.json',
        output=OUT.relative_to(ROOT).as_posix(), bindings=[{'path': p, 'sha256': h} for p,h in sorted(bindings.items())],
        restore_aldor_scryers_lore=True, prior_accepted_version='v52',
        scope='One current related-source Profession Updates PNG; retained The Broken image and all other image bytes unchanged.',
        new_original_2008_images=0, new_current_related_images=1, network_requests=0,
        deadline_utc='2026-10-22T13:41:33Z')
    PREP.parent.mkdir(parents=True, exist_ok=True)
    write(PREP, config)
    return {'prepared': True, 'bindings': len(bindings), 'sha256': sha(PREP)}

def export():
    config = read(PREP)
    assert datetime.now(timezone.utc) < datetime.fromisoformat(config['deadline_utc'].replace('Z','+00:00'))
    assert shutil.disk_usage(ROOT).free >= FLOOR and not OUT.exists()
    for r in config['bindings']:
        assert sha(ROOT / r['path']) == r['sha256'], r['path']
    import export_github_pages
    kwargs = {k: ROOT / config[k] for k in ('guide_preview_map','guide_image_collection_map','flash_runtime_archive','blizzcast_source_map','related_talent_icon_map','related_talent_ui_map','source16_layout_map','talent_box_layout_map','related_encyclopedia_image_map','related_guide_image_map')}
    start = datetime.now(timezone.utc).isoformat()
    result = export_github_pages.export_pages(source_site=ROOT / config['source_site'], manifest_path=ROOT / config['source_manifest'], output=OUT,
        base_path='/WOW-Encyclopedia-Deployable-Archive/', workspace_root=ROOT, max_bytes=None, min_free_bytes=FLOOR,
        image_source_maps=tuple(ROOT/p for p in config['primary_maps']), supplement_image_source_maps=tuple(ROOT/p for p in config['supplement_maps']),
        allow_later_image_supplements=True, restore_aldor_scryers_lore=True, **kwargs)
    receipt = {'schema':'wow-v53-build-receipt/v1','status':'built_pending_independent_browser_acceptance','started_utc':start,
        'finished_utc':datetime.now(timezone.utc).isoformat(),'preparation_sha256':sha(PREP), 'provenance_sha256':sha(OUT/'export-provenance.json'),
        'result':result,'disk_free_after_bytes':shutil.disk_usage(ROOT).free,'network_requests':0,'published':False}
    write(HERE / 'integration/v53-build-receipt.json', receipt)
    return receipt

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['accept-code','prepare','export'])
    a = parser.parse_args()
    print(json.dumps({'accept-code':accept_code,'prepare':prepare,'export':export}[a.mode]()))

"""Verify every v40 object and constrain its delta to the reviewed compat layer."""
import hashlib
import json
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261021-v40'
OLD = ROOT / '.scratch/pages-resources-20261020-v39'
sys.path.insert(0, str(ROOT / 'tools'))
import non_gallery_compat
import offline_flash

sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())

def main():
    start = time.monotonic()
    out = PUB / 'root-v40-export-acceptance.json'
    assert not out.exists()
    free_before = shutil.disk_usage(ROOT).free
    assert free_before >= 11005853696
    code_path = PUB / 'root-compat-code-acceptance.json'
    for row in read(code_path)['code_bindings']:
        assert sha((ROOT / row['path']).read_bytes()) == row['sha256']
    build_path = ROOT / 'research/continuous-recovery-20261021/integration/v40/v40-build-receipt.json'
    build = read(build_path)
    assert build['status'] == 'export_executed_not_yet_accepted' and build['network_requests'] == 0
    prov_path = SITE / 'export-provenance.json'
    prov_sha = sha(prov_path.read_bytes())
    assert build['provenance_sha256'] == prov_sha
    prov = read(prov_path)
    files = {r['output_path']: r for r in prov['files']}
    assert len(files) == len(prov['files'])
    actual = set()
    for directory, dirs, names in os.walk(SITE, followlinks=False):
        for item in dirs + names:
            assert not (Path(directory) / item).is_symlink()
        actual.update((Path(directory) / name).relative_to(SITE).as_posix() for name in names)
    assert actual == set(files) | {'export-provenance.json'}
    def check(pair):
        relative, row = pair
        assert relative and '..' not in relative.split('/') and '\\' not in relative and not relative.startswith('/')
        data = (SITE / relative).read_bytes()
        assert len(data) == row['derived_length'] and sha(data) == row['derived_sha256'], relative
        return len(data)
    with ThreadPoolExecutor(max_workers=8) as pool:
        tree_bytes = sum(pool.map(check, files.items())) + prov_path.stat().st_size
    assert sha((OLD / 'export-provenance.json').read_bytes()) == '02b1cd43766288f96c879ef464d7198bb09d1085008ae3e500773d594f6c7760'
    old = {r['output_path']: r for r in read(OLD / 'export-provenance.json')['files']}
    assert not set(old) - set(files)
    added = set(files) - set(old)
    bundle = prov['flash_exhibits']
    runtime_paths = {r['output_path'] for r in bundle['files']}
    assert added == runtime_paths and len(added) == 10
    assert bundle['runtime_version'] == '0.7.1'
    assert bundle['runtime_license'] == 'MIT OR Apache-2.0'
    assert bundle['archive_sha256'] == offline_flash.RUFFLE_ZIP_SHA256
    assert bundle['original_swfs'] == offline_flash.SWF_EXHIBITS
    assert not any('D:\\' in json.dumps(row) for row in bundle['files'])
    changed = sorted(p for p in old if (old[p]['derived_sha256'], old[p]['derived_length']) != (files[p]['derived_sha256'], files[p]['derived_length']))
    known_generated = {'__offline/pages_runtime.js', '__offline/route-map.json', 'README.md'}
    html_changed = []
    flash_pages = []
    menu_pages = 0
    for relative in changed:
        if relative in known_generated:
            continue
        assert relative.endswith('.html'), 'unexpected non-HTML delta: ' + relative
        before = (OLD / relative).read_text(encoding='utf-8')
        expected, compat_stats = non_gallery_compat.transform_html(before, route='/' + relative)
        expected, flash_stats = offline_flash.rewrite_page(expected, route='/' + relative, base_path='/WOW-Encyclopedia-Deployable-Archive/')
        after = (SITE / relative).read_text(encoding='utf-8')
        assert expected == after, 'delta exceeds reviewed transform: ' + relative
        if expected != before:
            html_changed.append(relative)
        if flash_stats.get('helper_injected'):
            flash_pages.append(relative)
        if compat_stats.get('changed'):
            menu_pages += 1
    # Use actual helper occurrences; stats keys are implementation-specific.
    helper_pages = [p for p in files if p.endswith('.html') and b'data-offline-flash=' in (SITE / p).read_bytes()]
    expected_pages = {'info/items/socketeditems.html', 'info/races/dancing.html', 'wrath/features/factions/tuskarr.xml.html'}
    assert set(helper_pages) == expected_pages
    for relative in offline_flash.SWF_EXHIBITS.values():
        path = relative['path']
        assert old[path]['derived_sha256'] == files[path]['derived_sha256'] == relative['sha256']
    for relative in old:
        if old[relative]['mime'].startswith('image/'):
            assert old[relative]['derived_sha256'] == files[relative]['derived_sha256']
    stats = prov['stats']
    assert stats['image_overlay_records'] == 657 and stats['primary_image_overlay_records'] == 557 and stats['supplement_image_overlay_records'] == 100
    assert stats['guide_image_collection_images'] == 39 and stats['guide_preview_count'] == 22
    assert stats['flash_runtime_files'] == 10 and stats['flash_exhibit_pages'] == 3
    assert len(files) == 9125 and len(actual) == 9126
    free_after = shutil.disk_usage(ROOT).free
    assert free_after >= 11005853696
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'site': SITE.relative_to(ROOT).as_posix(),
        'scope': 'Every output hash/length verified; old images and SWFs unchanged; HTML delta constrained to reviewed transforms',
        'elapsed_seconds': time.monotonic()-start, 'declared_files': len(files), 'actual_files': len(actual), 'tree_bytes': tree_bytes,
        'export_provenance_sha256': prov_sha, 'image_overlays': 657, 'new_original_images': 0, 'new_original_pages': 0,
        'added_paths_compared_v39': sorted(added), 'changed_paths_compared_v39': changed,
        'reviewed_html_delta_pages': len(html_changed), 'exact_flash_pages': sorted(helper_pages),
        'unchanged_previous_objects': len(old)-len(changed), 'runtime_added_bytes': sum(files[p]['derived_length'] for p in added),
        'network_requests': 0, 'published': False, 'browser_accepted': False,
        'disk_free_before_bytes': free_before, 'disk_free_after_bytes': free_after,
        'bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes())} for p in [code_path, build_path]]}
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'changed_paths_compared_v39'}))

if __name__ == '__main__':
    main()

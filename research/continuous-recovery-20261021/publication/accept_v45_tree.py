"""Root verification of all v45 output bytes and its narrow delta from v43."""
import hashlib
import json
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OLD = ROOT / '.scratch/pages-resources-20261021-v43'
CANDIDATE = ROOT / '.scratch/pages-resources-20261021-v44'
SITE = ROOT / '.scratch/pages-resources-20261021-v45'
OUT = PUB / 'root-v45-export-acceptance.json'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not OUT.exists()
before = shutil.disk_usage(ROOT).free
assert before >= 11005853696
assert sha(OLD / 'export-provenance.json') == '3d1e9592769f2111de190c4bcd48ec84c20563df877bed23d4892a6c9ef1ed68'
assert sha(SITE / 'export-provenance.json') == '9556243ffc65dfe27f332ea4d45df71869617e8353f600061279a983528e544e'
old_prov, prov = map(read, (OLD / 'export-provenance.json', SITE / 'export-provenance.json'))
assert prov['source_manifest_sha256'] == old_prov['source_manifest_sha256'] == 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
assert sha(ROOT / prov['source_manifest']) == prov['source_manifest_sha256']
files = {r['output_path']: r for r in prov['files']}
old = {r['output_path']: r for r in old_prov['files']}
assert len(files) == len(prov['files']) == prov['stats']['output_files'] == 10129
icon_map = read(ROOT / 'research/continuous-recovery-20261021/integration/related-talent-icons/input-map.json')
icon_paths = {r['route'].lstrip('/') for r in icon_map['entries']}
assert len(icon_paths) == 986
new_paths = icon_paths | {'__offline/related-talent-icons.json'}
assert set(files) - set(old) == new_paths and set(old) <= set(files)
classes = ('druid', 'hunter', 'mage', 'paladin', 'priest', 'rogue', 'shaman', 'warlock', 'warrior')
talent_paths = {f'info/classes/{c}/talents.html' for c in classes}
changed = {p for p in old if old[p]['derived_sha256'] != files[p]['derived_sha256']}
assert changed == talent_paths | {
    '__offline/pages_runtime.js', '__offline/route-map.json',
    'contests/05-06-09/index.html', 'news/wow-news-06-2005.html',
    'info/items/tinfoilhat.xml.html', 'moltencore/index.html',
}
actual = set()
for directory, dirs, names in os.walk(SITE, followlinks=False):
    for name in dirs + names:
        assert not (Path(directory) / name).is_symlink()
    actual.update((Path(directory) / n).relative_to(SITE).as_posix() for n in names)
assert actual == set(files) | {'export-provenance.json'}

def check(pair):
    path, row = pair
    entity = SITE / path
    assert entity.stat().st_size == row['derived_length'] and sha(entity) == row['derived_sha256'], path
    if path in old:
        prior = OLD / path
        assert prior.stat().st_size == old[path]['derived_length'] and sha(prior) == old[path]['derived_sha256'], path
        if path not in changed:
            assert entity.read_bytes() == prior.read_bytes(), path
    return row['derived_length']

with ThreadPoolExecutor(max_workers=8) as pool:
    total = sum(pool.map(check, files.items())) + (SITE / 'export-provenance.json').stat().st_size
for entry in icon_map['entries']:
    path = entry['route'].lstrip('/')
    row = files[path]
    assert (SITE / path).read_bytes() == (ROOT / entry['payload_path']).read_bytes()
    assert row['kind'] == 'related_talent_icon' and row['transformed'] is False
    ref = row['source_refs'][0]
    assert ref['classification'] == 'later_related_source' and ref['original_capture_timestamp'] is None
    assert row['source_sha256'] == row['derived_sha256'] == entry['sha256']
    assert 'payload_path' not in json.dumps(row)
assert sha(SITE / '__offline/related-talent-icons.json') == '066d79488017adb3a10d6e9a80f2c3c093a26faae957bc2e27fd1c9babf52036'
for path in talent_paths:
    assert (SITE / path).read_bytes() == (CANDIDATE / path).read_bytes(), path
    assert (SITE / path).read_text(encoding='utf-8').count('id="__offline-related-talent-icons"') == 1
layout_map = read(ROOT / 'research/continuous-recovery-20261021/integration/source16/layout-compatibility/input-map.json')
layout = prov['layout_compatibility_reuse']
assert layout['classification'] == 'layout_compatibility_reuse'
assert layout['new_image_payloads'] == layout['target_original_images_recovered'] == 0
assert layout['reused_target_paths'] == len(layout['records']) == 10
assert layout['records'] == layout_map['entries']
old_routes, routes = map(read, (OLD / '__offline/route-map.json', SITE / '__offline/route-map.json'))
assert routes['aliases'] == old_routes['aliases']
assert all(routes['routes'][k] == v for k, v in old_routes['routes'].items())
assert set(routes['routes']) - set(old_routes['routes']) == {'/' + p for p in new_paths} | {r['target_route'] for r in layout['records']}
for entry in layout['records']:
    target, source = entry['target_route'], entry['source_route']
    assert routes['routes'][target] == routes['routes'][source]
    assert target not in routes['aliases'] and not (SITE / target.lstrip('/')).exists()
    assert sha(SITE / source.lstrip('/')) == entry['sha256']
    assert entry['target_capture_timestamp'] is None and entry['source_capture_timestamp'] <= '20080512210044'
    page = next(row for row in files.values() if row['route'] == entry['page_route'])
    assert entry in page['layout_reuse_refs']
runtime_bodies = []
for site, route_data in ((OLD, old_routes), (SITE, routes)):
    text = (site / '__offline/pages_runtime.js').read_text(encoding='utf-8')
    embedded = re.search(r'    var routes = (\{[^\n]*\});', text)
    assert embedded and json.loads(embedded[1]) == route_data['routes']
    runtime_bodies.append(text[:embedded.start(1)] + '<VERIFIED_ROUTE_MAP>' + text[embedded.end(1):])
assert runtime_bodies[0] == runtime_bodies[1]
contest = (SITE / 'contests/05-06-09/index.html').read_text(encoding='utf-8')
assert re.search(r'<p class="historical-rules-note">[^<]+</p>\s*</center>', contest)
assert 'Giving away' not in contest and 'Blizzard announced a giveaway' in contest
for k, n in {'related_talent_icons':986, 'related_talent_icon_notice_pages':9,
             'layout_compatibility_reused_target_paths':10, 'layout_compatibility_pages':2,
             'image_overlay_records':657, 'primary_image_overlay_records':557,
             'supplement_image_overlay_records':100, 'guide_preview_count':22,
             'guide_image_collection_images':39, 'source16_main_pages':8,
             'blizzcast_reading_pages':5, 'flash_exhibit_pages':3, 'talent_compat_scripts':2}.items():
    assert prov['stats'][k] == n, k
assert prov['flash_exhibits'] == old_prov['flash_exhibits']
after = shutil.disk_usage(ROOT).free
assert after >= 11005853696
receipt = {
    'accepted': True, 'version': 'v45', 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'local_site': SITE.relative_to(ROOT).as_posix(), 'export_provenance_sha256': sha(SITE / 'export-provenance.json'),
    'declared_files': len(files), 'actual_files': len(actual), 'tree_bytes': total,
    'added_files_count': len(new_paths), 'changed_existing_files': sorted(changed), 'removed_files': [],
    'unchanged_prior_objects': len(old) - len(changed), 'new_related_talent_icon_objects':986,
    'new_original_2008_images': 0, 'layout_reused_target_paths':10, 'new_layout_image_objects':0,
    'all_prior_images_swfs_wasm_and_talent_data_byte_preserved':True,
    'v44_nine_talent_pages_identical_and_browser_evidence_reusable':True,
    'runtime_changes_are_only_route_map': True, 'browser_accepted': False, 'published': False,
    'disk_free_before_bytes':before, 'disk_free_after_bytes':after,
    'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (
        PUB / 'root-v45-code-acceptance.json', PUB / 'v45-export-execution.json',
        ROOT / 'research/continuous-recovery-20261021/integration/v45/v45-build-receipt.json',
        PUB / 'root-source16-local-acceptance.json', PUB / 'root-related-talent-icon-integration-decision.json',
        PUB / 'root-source16-layout-reuse-decision.json',
    )],
}
OUT.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(json.dumps(receipt))

"""Verify all v50 bytes and the exact delta from accepted v49."""
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
OLD = ROOT / '.scratch/pages-resources-20261021-v49'
SITE = ROOT / '.scratch/pages-resources-20261021-v50'
OUT = PUB / 'root-v50-export-acceptance.json'
assert not OUT.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
assert sha(OLD / 'export-provenance.json') == '4f50a5cf661176b7409de8a8cb7a5824fa958b7c2ef1515e531943014a6574da'
build_path = ROOT / 'research/continuous-recovery-20261021/integration/v50/v50-build-receipt.json'
build = read(build_path)
assert sha(SITE / 'export-provenance.json') == build['provenance_sha256']
old, prov = read(OLD / 'export-provenance.json'), read(SITE / 'export-provenance.json')
assert old['source_manifest_sha256'] == prov['source_manifest_sha256'] == 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
files = {r['output_path']: r for r in prov['files']}
prior = {r['output_path']: r for r in old['files']}
helper = '__offline/aldor-scryers-lore.js'
page = 'info/basics/factions/aldorscryers/aldor-scryers.xml.html'
changed = {p for p in prior if prior[p]['derived_sha256'] != files[p]['derived_sha256']}
assert len(files) == len(prov['files']) == prov['stats']['output_files'] == 10143
assert set(files) - set(prior) == {helper} and set(prior) <= set(files)
assert changed == {page, '__offline/pages_runtime.js', '__offline/route-map.json'}, changed
actual = set()
for directory, dirs, names in os.walk(SITE, followlinks=False):
    assert all(not (Path(directory) / n).is_symlink() for n in dirs + names)
    actual.update((Path(directory) / n).relative_to(SITE).as_posix() for n in names)
assert actual == set(files) | {'export-provenance.json'}

def check(pair):
    name, row = pair
    entity = SITE / name
    assert entity.stat().st_size == row['derived_length'] and sha(entity) == row['derived_sha256'], name
    if name in prior:
        assert sha(OLD / name) == prior[name]['derived_sha256'], name
        if name not in changed:
            assert entity.read_bytes() == (OLD / name).read_bytes(), name
    return row['derived_length']

with ThreadPoolExecutor(max_workers=8) as pool:
    total = sum(pool.map(check, files.items())) + (SITE / 'export-provenance.json').stat().st_size
assert len(actual) == 10144
source = read(PUB / 'root-aldor-scryers-lore-source-acceptance.json')
assert source['accepted']
assert sha(SITE / helper) == source['helper']['sha256'] == '253475779f9f0246639453efb691896c930cc2285e4ecb15c265e7ba81ca2785'
assert (SITE / helper).stat().st_size == 3273
marker = '\n<script defer src="' + prov['base_path'].rstrip('/') + '/' + helper + '"></script>\n'
before, after = (OLD / page).read_bytes(), (SITE / page).read_bytes()
assert after.count(marker.encode()) == 1 and after.replace(marker.encode(), b'', 1) == before
assert after.index(marker.encode()) < after.index(b'</head>')
assert files[helper]['kind'] == 'aldor_scryers_lore_helper'
assert files[helper]['source_refs'] == [source['source']]
lore = prov['source16_lore_reuse']
assert lore['source'] == source['source'] and lore['pages'] == 1
assert lore['generated_sha256'] == source['helper']['sha256']
assert lore['generated_length'] == 3273
assert prov['stats']['aldor_scryers_lore_pages'] == prov['stats']['aldor_scryers_lore_assets'] == 1
routes, old_routes = read(SITE / '__offline/route-map.json'), read(OLD / '__offline/route-map.json')
assert {k: v for k, v in routes.items() if k != 'routes'} == {k: v for k, v in old_routes.items() if k != 'routes'}
assert set(routes['routes']) - set(old_routes['routes']) == {'/' + helper}
assert all(routes['routes'][k] == v for k, v in old_routes['routes'].items())
assert routes['routes']['/' + helper] == prov['base_path'].rstrip('/') + '/' + helper
runtime = []
for tree, data in ((OLD, old_routes), (SITE, routes)):
    text = (tree / '__offline/pages_runtime.js').read_bytes().decode()
    match = re.search(r'    var routes = (\{[^\n]*\});', text)
    assert match and json.loads(match[1]) == data['routes']
    runtime.append(text[:match.start(1)] + '<VERIFIED_ROUTES>' + text[match.end(1):])
assert runtime[0] == runtime[1]
for key in ('related_talent_ui', 'talent_box_layout_compatibility', 'layout_compatibility_reuse',
            'related_talent_icons', 'flash_exhibits', 'blizzcast_reading',
            'related_encyclopedia_images', 'related_guide_images', 'guide_image_collections'):
    assert prov[key] == old[key], key
assert shutil.disk_usage(ROOT).free >= 11005853696
receipt = {
    'schema': 'wow-root-export-acceptance/v2', 'accepted': True, 'version': 'v50',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'local_site': SITE.relative_to(ROOT).as_posix(),
    'export_provenance_sha256': sha(SITE / 'export-provenance.json'),
    'actual_files': len(actual), 'declared_files': len(files), 'tree_bytes': total,
    'added_files_count': 1, 'changed_existing_files': sorted(changed), 'removed_files': [],
    'unchanged_prior_objects': len(prior) - len(changed),
    'new_original_2008_images': 0, 'source16_lore_literals_reused': 2,
    'main_page_diff_is_only_one_deferred_helper': True,
    'all_prior_images_original_scripts_reward_data_swfs_wasm_preserved': True,
    'runtime_changes_are_only_route_map': True,
    'browser_accepted': False, 'published': False,
    'bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}
                 for p in (PUB / 'root-v50-code-acceptance.json', PUB / 'v50-export-execution.json',
                           build_path, PUB / 'root-aldor-scryers-lore-source-acceptance.json', Path(__file__))],
}
OUT.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(json.dumps(receipt))

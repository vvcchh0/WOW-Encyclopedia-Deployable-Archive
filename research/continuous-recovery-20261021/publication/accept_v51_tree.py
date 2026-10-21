"""Check v51 actual bytes and its one narrowly added image route."""
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
OLD = ROOT / '.scratch/pages-resources-20261021-v50'
SITE = ROOT / '.scratch/pages-resources-20261021-v51'
OUT = PUB / 'root-v51-export-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD / 'export-provenance.json') == '0735d19c7fb11dc0fceae2357e08798a4b1f334dd21722916df8b6e1546c55ec'
build_path = ROOT / 'research/continuous-recovery-20261021/integration/v51/v51-build-receipt.json'
assert sha(SITE / 'export-provenance.json') == read(build_path)['provenance_sha256']
old, prov = read(OLD / 'export-provenance.json'), read(SITE / 'export-provenance.json')
assert old['source_manifest_sha256'] == prov['source_manifest_sha256'] == 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
files = {r['output_path']: r for r in prov['files']}
prior = {r['output_path']: r for r in old['files']}
assert set(files) == set(prior) and len(files) == len(prov['files']) == prov['stats']['output_files'] == 10143
changed = {p for p in prior if prior[p]['derived_sha256'] != files[p]['derived_sha256']}
assert changed == {'__offline/pages_runtime.js', '__offline/route-map.json'}, changed
actual = set()
for directory, dirs, names in os.walk(SITE, followlinks=False):
    assert all(not (Path(directory) / n).is_symlink() for n in dirs + names)
    actual.update((Path(directory) / n).relative_to(SITE).as_posix() for n in names)
assert actual == set(files) | {'export-provenance.json'}

def check(pair):
    name, row = pair
    p = SITE / name
    assert p.stat().st_size == row['derived_length'] and sha(p) == row['derived_sha256'], name
    assert sha(OLD / name) == prior[name]['derived_sha256'], name
    if name not in changed:
        assert p.read_bytes() == (OLD / name).read_bytes(), name
    return row['derived_length']

with ThreadPoolExecutor(max_workers=8) as pool:
    total = sum(pool.map(check, files.items())) + (SITE / 'export-provenance.json').stat().st_size
routes, before = read(SITE / '__offline/route-map.json'), read(OLD / '__offline/route-map.json')
alias, canonical = '/wrath/images/letters/T.gif', '/wrath//images/letters/T.gif'
target = prov['base_path'].rstrip('/') + '/wrath/images/letters/T.gif'
assert routes['routes'][alias] == routes['routes'][canonical] == target
assert routes['aliases'][alias] == target
for key in ('routes', 'aliases'):
    assert set(routes[key]) - set(before[key]) == {alias}, key
    assert all(routes[key][k] == v for k, v in before[key].items()), key
assert {k: v for k, v in routes.items() if k not in {'routes', 'aliases'}} == {k: v for k, v in before.items() if k not in {'routes', 'aliases'}}
runtime = []
for tree, data in ((OLD, before), (SITE, routes)):
    text = (tree / '__offline/pages_runtime.js').read_bytes().decode()
    match = re.search(r'    var routes = (\{[^\n]*\});', text)
    assert match and json.loads(match[1]) == data['routes']
    runtime.append(text[:match.start(1)] + '<VERIFIED_ROUTES>' + text[match.end(1):])
assert runtime[0] == runtime[1]
gif = SITE / 'wrath/images/letters/T.gif'
assert gif.stat().st_size == 1419 and sha(gif) == '0a82046107b2f5a45b258143cd8f862030980507bad23190c54445b43b3a62ad'
assert not (SITE / 'wrath/images/letters/T.gif.html').exists()
assert prov['source16_lore_reuse'] == old['source16_lore_reuse']
for key in ('related_talent_ui', 'talent_box_layout_compatibility', 'layout_compatibility_reuse',
            'related_talent_icons', 'flash_exhibits', 'blizzcast_reading',
            'related_encyclopedia_images', 'related_guide_images', 'guide_image_collections'):
    assert prov[key] == old[key], key
assert shutil.disk_usage(ROOT).free >= 11005853696
receipt = {
    'schema': 'wow-root-export-acceptance/v2', 'accepted': True, 'version': 'v51',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'local_site': SITE.relative_to(ROOT).as_posix(),
    'export_provenance_sha256': sha(SITE / 'export-provenance.json'),
    'actual_files': len(actual), 'declared_files': len(files), 'tree_bytes': total,
    'added_files_count': 0, 'changed_existing_files': sorted(changed), 'removed_files': [],
    'unchanged_prior_objects': len(prior) - len(changed), 'new_original_2008_images': 0,
    'all_page_html_images_original_scripts_reward_data_swfs_wasm_preserved': True,
    'exact_added_route': alias, 'canonical_source_route': canonical,
    'runtime_changes_are_only_route_map': True, 'browser_accepted': False, 'published': False,
    'bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}
                 for p in (PUB / 'root-v51-code-acceptance.json', PUB / 'v51-export-execution.json',
                           build_path, PUB / 'root-v50-local-acceptance.json', Path(__file__))],
}
OUT.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(json.dumps(receipt))

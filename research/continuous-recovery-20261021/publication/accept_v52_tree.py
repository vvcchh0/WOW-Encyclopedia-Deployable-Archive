"""Independently check all v52 bytes and the exact one-page directory repair."""
import hashlib
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OLD = ROOT / '.scratch/pages-resources-20261021-v51'
SITE = ROOT / '.scratch/pages-resources-20261021-v52'
OUT = PUB / 'root-v52-export-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD / 'export-provenance.json') == 'd7fbb990abaf23d6931c28341d0e459c880093990f73effe3be1dfa28a6f599f'
build = ROOT / 'research/continuous-recovery-20261021/integration/v52/v52-build-receipt.json'
assert sha(SITE / 'export-provenance.json') == read(build)['provenance_sha256']
old, prov = read(OLD / 'export-provenance.json'), read(SITE / 'export-provenance.json')
assert old['source_manifest_sha256'] == prov['source_manifest_sha256'] == 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
prior, files = [{r['output_path']: r for r in p['files']} for p in (old, prov)]
assert set(prior) == set(files) and len(files) == len(prov['files']) == prov['stats']['output_files'] == 10143
changed = {p for p in files if files[p]['derived_sha256'] != prior[p]['derived_sha256']}
page = 'pvp/battlegrounds/info-arathi.html'
assert changed == {page}, changed
before = (OLD / page).read_bytes()
original = b'path = "/WOW-Encyclopedia-Deployable-Archive/info/underdev/index.html";'
replacement = b'path = "/WOW-Encyclopedia-Deployable-Archive/info/underdev/";'
assert before.count(original) == 1
assert (SITE / page).read_bytes() == before.replace(original, replacement)
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
for key in ('source16_lore_reuse', 'related_talent_ui', 'talent_box_layout_compatibility',
            'layout_compatibility_reuse', 'related_talent_icons', 'flash_exhibits',
            'blizzcast_reading', 'related_encyclopedia_images', 'related_guide_images',
            'guide_image_collections'):
    assert prov[key] == old[key], key
assert (SITE / '__offline/route-map.json').read_bytes() == (OLD / '__offline/route-map.json').read_bytes()
assert shutil.disk_usage(ROOT).free >= 11005853696
report = {
    'schema': 'wow-root-export-acceptance/v2', 'accepted': True, 'version': 'v52',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'local_site': SITE.relative_to(ROOT).as_posix(),
    'export_provenance_sha256': sha(SITE / 'export-provenance.json'),
    'actual_files': len(actual), 'declared_files': len(files), 'tree_bytes': total,
    'changed_existing_files': sorted(changed), 'added_files_count': 0, 'removed_files': [],
    'unchanged_prior_objects': len(files) - 1, 'new_original_2008_images': 0,
    'exact_page_bytes_change': 'Only the verified path assignment changes from index document to directory.',
    'image_script_reward_swf_wasm_and_all_other_page_bytes_preserved': True,
    'published': False, 'browser_accepted': False,
    'bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in (
        build, PUB / 'root-v52-code-acceptance.json', PUB / 'v52-export-execution.json',
        PUB / 'root-v51-local-acceptance.json', Path(__file__),
    )],
}
OUT.write_bytes((json.dumps(report, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'actual_files': len(actual), 'changed': sorted(changed),
                  'provenance_sha256': report['export_provenance_sha256']}))

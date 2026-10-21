"""Independent byte, route and source-reference acceptance for Source16/v43."""
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
OLD = ROOT / '.scratch/pages-resources-20261021-v42'
SITE = ROOT / '.scratch/pages-resources-20261021-v43'
OUT = PUB / 'root-v43-export-acceptance.json'
sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda path: json.loads(path.read_bytes())

assert not OUT.exists()
before = shutil.disk_usage(ROOT).free
assert before >= 11005853696
old_prov = read(OLD / 'export-provenance.json')
assert sha((OLD / 'export-provenance.json').read_bytes()) == 'e18be5d87344cf4bf0a94b860f033b3aa08811b571cc669dd43868477540a478'
prov = read(SITE / 'export-provenance.json')
assert sha((SITE / 'export-provenance.json').read_bytes()) == '3d1e9592769f2111de190c4bcd48ec84c20563df877bed23d4892a6c9ef1ed68'
assert prov['source_manifest_sha256'] == 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
assert sha((ROOT / prov['source_manifest']).read_bytes()) == prov['source_manifest_sha256']
assert read(PUB / 'root-source16-local-acceptance.json')['accepted']
files = {row['output_path']: row for row in prov['files']}
old = {row['output_path']: row for row in old_prov['files']}
assert len(files) == len(prov['files']) == 9142
new_paths = {
    'contests/05-06-09/index.html', 'info/items/tinfoilhat.xml.html',
    'info/races/two-headed-ogre.shtml.html', 'misc/fan-site-program.html',
    'moltencore/index.html', 'patchnotes/patch-9-29-04.shtml.html',
    'wrath/features/bard/bardclass.xml.html', 'contests/05-06-09.html',
    'info/basics/content-index.shtml.html', 'moltencore.html', 'wrath/index.xml.html',
}
assert set(files) - set(old) == new_paths and set(old) <= set(files)
changed = {p for p in old if old[p]['derived_sha256'] != files[p]['derived_sha256']}
assert changed == {
    '__offline/pages_runtime.js', '__offline/route-map.json', 'new-hp/js/menu5_var.js',
    'news/rss-04-2007.xml.html', 'news/rss-04-2008.xml.html',
    'news/rss-05-2008.xml.html', 'news/wow-news-06-2005.html',
    'info/basics/content-index.html',
}
actual = set()
for directory, dirs, names in os.walk(SITE, followlinks=False):
    for name in dirs + names:
        assert not (Path(directory) / name).is_symlink()
    actual.update((Path(directory) / name).relative_to(SITE).as_posix() for name in names)
assert actual == set(files) | {'export-provenance.json'}

def check(pair):
    path, row = pair
    data = (SITE / path).read_bytes()
    assert len(data) == row['derived_length'] and sha(data) == row['derived_sha256'], path
    if path in old:
        prior = (OLD / path).read_bytes()
        assert len(prior) == old[path]['derived_length'] and sha(prior) == old[path]['derived_sha256'], path
        if old[path]['kind'] == 'image_overlay' or path.endswith(('.swf', '.wasm')):
            assert data == prior, path
    return len(data)

with ThreadPoolExecutor(max_workers=8) as pool:
    total = sum(pool.map(check, files.items())) + (SITE / 'export-provenance.json').stat().st_size
source_map = read(ROOT / 'research/continuous-recovery-20261021/integration/main-pages-review/source16-input-map.json')
source_entities = source_map.get('entries') or source_map.get('sources') or source_map.get('records')
assert isinstance(source_entities, list), list(source_map)
body_refs = [row for row in files.values() if row.get('role') == 'source16_main_page']
assert len(body_refs) == prov['stats']['source16_main_pages'] == 8
for row in body_refs:
    refs = row['source_refs']
    assert len(refs) == 1 and refs[0]['source_kind'] == 'commoncrawl_arc'
    ref = refs[0]
    assert ref['actual_capture_timestamp'] <= '20080512210044'
    source = next(item for item in source_entities if item['proposed_route'] == row['route'])
    for key in ('original_url', 'actual_capture_timestamp', 'sha256', 'length', 'source_arc'):
        assert ref[key] == source[key], (row['route'], key)
    text = (SITE / row['output_path']).read_text(encoding='utf-8')
    assert text.count('id="__offline-source16-note"') == 1
    assert 'Historical page' in text and ref['actual_capture_timestamp'][:4] in text
    assert not any(key in json.dumps(ref).lower() for key in ('set-cookie', 'cookie_path', 'payload_path', 'authorization'))
old_routes = read(OLD / '__offline/route-map.json')
routes = read(SITE / '__offline/route-map.json')
assert {k:v for k,v in routes.items() if k not in ('routes','aliases')} == {k:v for k,v in old_routes.items() if k not in ('routes','aliases')}
assert all(routes['aliases'][key] == value for key, value in old_routes['aliases'].items())
assert set(routes['aliases']) - set(old_routes['aliases']) == {
    '/contests/05-06-09', '/contests/05-06-09/', '/info/basics/content-index.shtml',
    '/moltencore', '/moltencore/', '/wrath/index.xml',
}
assert all(routes['routes'][key] == value for key, value in old_routes['routes'].items())
runtime_bodies = []
for site, route_data in ((OLD, old_routes), (SITE, routes)):
    text = (site / '__offline/pages_runtime.js').read_text(encoding='utf-8')
    embedded = re.search(r'    var routes = (\{[^\n]*\});', text)
    assert embedded and json.loads(embedded[1]) == route_data['routes']
    runtime_bodies.append(text[:embedded.start(1)] + '<VERIFIED_ROUTE_MAP>' + text[embedded.end(1):])
assert runtime_bodies[0] == runtime_bodies[1]
for key, n in {'image_overlay_records':657, 'guide_preview_count':22, 'guide_image_collection_images':39,
               'flash_exhibit_pages':3, 'flash_runtime_files':10, 'talent_compat_scripts':2,
               'blizzcast_reading_pages':5, 'blizzcast_reading_styles':1}.items():
    assert prov['stats'][key] == n, key
assert prov['flash_exhibits'] == old_prov['flash_exhibits']
after = shutil.disk_usage(ROOT).free
assert after >= 11005853696
receipt = {
    'accepted':True, 'version':'v43', 'checked_utc':datetime.now(timezone.utc).isoformat(),
    'local_site':SITE.relative_to(ROOT).as_posix(),
    'export_provenance_sha256':sha((SITE / 'export-provenance.json').read_bytes()),
    'declared_files':len(files), 'actual_files':len(actual), 'tree_bytes':total,
    'added_files':sorted(new_paths), 'changed_existing_files':sorted(changed), 'removed_files':[],
    'unchanged_prior_objects':len(old)-len(changed), 'source16_reading_pages':8,
    'original_images_swfs_and_wasm_byte_preserved':True, 'new_original_images':0,
    'runtime_changes_are_only_route_map':True, 'browser_accepted':False, 'published':False,
    'disk_free_before_bytes':before, 'disk_free_after_bytes':after, 'network_requests':0,
    'bindings':[{'path':p.relative_to(ROOT).as_posix(), 'sha256':sha(p.read_bytes())} for p in (
        PUB / 'root-v43-code-acceptance.json', PUB / 'root-source16-local-acceptance.json',
        ROOT / 'research/continuous-recovery-20261021/integration/v43/v43-build-receipt-r2.json',
    )],
}
OUT.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt))

"""Independently verify every v46 object and its narrow delta from v45."""
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
OLD = ROOT/'.scratch/pages-resources-20261021-v45'
SITE = ROOT/'.scratch/pages-resources-20261021-v46'
OUT = PUB/'root-v46-export-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'export-provenance.json') == '9556243ffc65dfe27f332ea4d45df71869617e8353f600061279a983528e544e'
build_path = ROOT/'research/continuous-recovery-20261021/integration/v46/v46-build-receipt.json'
assert sha(SITE/'export-provenance.json') == read(build_path)['provenance_sha256']
old, prov = read(OLD/'export-provenance.json'), read(SITE/'export-provenance.json')
assert old['source_manifest_sha256'] == prov['source_manifest_sha256'] == 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
files = {r['output_path']:r for r in prov['files']}
prior = {r['output_path']:r for r in old['files']}
assert len(files) == len(prov['files']) == prov['stats']['output_files'] == 10136
mapping = read(ROOT/'research/continuous-recovery-20261021/integration/related-talent-ui/input-map.json')
new_paths = {r['route'].lstrip('/') for r in mapping['entries']} | {'__offline/related-talent-ui.json'}
assert len(new_paths) == 7 and set(files)-set(prior) == new_paths and set(prior) <= set(files)
classes = ('druid','hunter','mage','paladin','priest','rogue','shaman','warlock','warrior')
talent_paths = {f'info/classes/{c}/talents.html' for c in classes}
changed = {p for p in prior if prior[p]['derived_sha256'] != files[p]['derived_sha256']}
assert changed == talent_paths | {'__offline/pages_runtime.js','__offline/route-map.json'}
actual = set()
for directory, dirs, names in os.walk(SITE, followlinks=False):
    assert all(not (Path(directory)/n).is_symlink() for n in dirs+names)
    actual.update((Path(directory)/n).relative_to(SITE).as_posix() for n in names)
assert actual == set(files)|{'export-provenance.json'}
def check(pair):
    path, row = pair
    entity = SITE/path
    assert entity.stat().st_size == row['derived_length'] and sha(entity) == row['derived_sha256'], path
    if path in prior:
        assert sha(OLD/path) == prior[path]['derived_sha256'], path
        if path not in changed:
            assert entity.read_bytes() == (OLD/path).read_bytes(), path
    return row['derived_length']
with ThreadPoolExecutor(max_workers=8) as pool:
    total = sum(pool.map(check, files.items())) + (SITE/'export-provenance.json').stat().st_size
for entry in mapping['entries']:
    row = files[entry['route'].lstrip('/')]
    assert (SITE/row['output_path']).read_bytes() == (ROOT/entry['payload_path']).read_bytes()
    assert row['kind'] == 'related_talent_ui' and row['transformed'] is False
    assert row['mime'].split(';')[0] == 'image/png'
    assert row['source_refs'][0]['classification'] == 'later_related_source'
    assert row['source_refs'][0]['original_capture_timestamp'] is None
    assert 'payload_path' not in json.dumps(row)
for path in talent_paths:
    text = (SITE/path).read_text(encoding='utf-8')
    assert text.count('id="__offline-related-talent-icons"') == 1
    assert 'related-talent-ui.json' in text and 'related-talent-icons.json' in text
    assert len(files[path]['layout_reuse_refs']) == 8
point_map = read(ROOT/'research/continuous-recovery-20261021/integration/talent-box-layout/input-map.json')
layout = prov['talent_box_layout_compatibility']
assert layout['records'] == point_map['entries'] and layout['reused_target_paths'] == 8
assert layout['new_image_payloads'] == layout['target_original_images_recovered'] == 0
assert prov['layout_compatibility_reuse'] == old['layout_compatibility_reuse']
assert prov['related_talent_icons'] == old['related_talent_icons']
old_routes, routes = read(OLD/'__offline/route-map.json'), read(SITE/'__offline/route-map.json')
assert routes['aliases'] == old_routes['aliases']
assert all(routes['routes'][k] == v for k,v in old_routes['routes'].items())
ui_targets = {r['target_route']:r['route'] for r in mapping['entries']}
box_targets = {r['target_route']:r['source_route'] for r in point_map['entries']}
assert set(routes['routes'])-set(old_routes['routes']) == set(ui_targets)|set(box_targets)|{'/'+p for p in new_paths}
for target, source in (ui_targets|box_targets).items():
    assert routes['routes'][target] == routes['routes'][source]
    assert target not in routes['aliases'] and not (SITE/target.lstrip('/')).exists()
runtime = []
for site, route_data in ((OLD,old_routes),(SITE,routes)):
    text = (site/'__offline/pages_runtime.js').read_text(encoding='utf-8')
    match = re.search(r'    var routes = (\{[^\n]*\});', text)
    assert match and json.loads(match[1]) == route_data['routes']
    runtime.append(text[:match.start(1)]+'<VERIFIED_ROUTES>'+text[match.end(1):])
assert runtime[0] == runtime[1]
expected_stats = {'related_talent_ui_assets':6,'related_talent_ui_notice_pages':9,'talent_box_layout_reused_target_paths':8,'talent_box_layout_pages':9,'related_talent_icons':986,'layout_compatibility_reused_target_paths':10,'layout_compatibility_pages':2,'image_overlay_records':657,'guide_preview_count':22,'guide_image_collection_images':39,'source16_main_pages':8,'blizzcast_reading_pages':5,'flash_exhibit_pages':3,'talent_compat_scripts':2}
for key,value in expected_stats.items(): assert prov['stats'][key] == value, key
assert prov['flash_exhibits'] == old['flash_exhibits']
assert shutil.disk_usage(ROOT).free >= 11005853696
receipt = {'schema':'wow-root-export-acceptance/v2','accepted':True,'version':'v46','checked_utc':datetime.now(timezone.utc).isoformat(),'local_site':SITE.relative_to(ROOT).as_posix(),'export_provenance_sha256':sha(SITE/'export-provenance.json'),'declared_files':len(files),'actual_files':len(actual),'tree_bytes':total,'added_files_count':7,'changed_existing_files':sorted(changed),'removed_files':[],'unchanged_prior_objects':len(prior)-len(changed),'new_related_ui_images':6,'new_related_ui_bytes':5619,'new_original_2008_images':0,'points_box_reused_target_paths':8,'new_layout_image_objects':0,'all_prior_images_scripts_swfs_wasm_and_talent_data_byte_preserved':True,'runtime_changes_are_only_route_map':True,'browser_accepted':False,'published':False,'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (PUB/'root-v46-code-acceptance.json',PUB/'v46-export-execution.json',build_path,PUB/'root-related-talent-ui-integration-decision.json',PUB/'root-talent-box-layout-decision.json')]}
OUT.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))

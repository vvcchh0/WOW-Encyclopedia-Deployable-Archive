"""Build v49 from accepted v46 inputs and four attributed illustrations plus the Broken dynamic thumbnail mapping."""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PUB = ROOT/'research/continuous-recovery-20261021/publication'
PREP = HERE/'v49-input-preparation.json'
GO = PUB/'root-v49-export-go.json'
OUTPUT = ROOT/'.scratch/pages-resources-20261021-v49'
FLOOR = 11005853696
CUTOFF = datetime(2026,10,21,13,5,7,tzinfo=timezone.utc)
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def verify(rows):
    for row in rows:
        path = ROOT/row['path']
        assert path.resolve().is_relative_to(ROOT.resolve()) and path.is_file()
        assert sha(path) == row['sha256'], row['path']
def prepare():
    assert not PREP.exists() and not OUTPUT.exists() and not OUTPUT.with_name(OUTPUT.name+'.partial').exists()
    assert read(PUB/'root-v46-pages-online-acceptance.json')['accepted']
    prior_path = ROOT/'research/continuous-recovery-20261021/integration/v46/v46-input-preparation.json'
    prior = read(prior_path)
    code_path = PUB/'root-v49-code-acceptance.json'
    code = read(code_path)
    assert code['accepted'] and code['tests']['count'] == 65 and code['tests']['skipped'] == 0
    bindings = {r['path']:r['sha256'] for r in prior['bindings']}
    bindings.update({r['path']:r['sha256'] for r in code['code_bindings']})
    maps = {
        'related_talent_ui_map':'research/continuous-recovery-20261021/integration/related-talent-ui/input-map.json',
        'talent_box_layout_map':'research/continuous-recovery-20261021/integration/talent-box-layout/input-map.json',
        'related_encyclopedia_image_map':'research/continuous-recovery-20261021/integration/related-encyclopedia-images/input-map.json',
        'related_guide_image_map':'research/continuous-recovery-20261021/integration/related-guide-images-v49/input-map.json',
    }
    extra = [code_path, prior_path, PUB/'root-v46-local-acceptance.json', PUB/'root-v46-pages-online-acceptance.json', Path(__file__)]
    for map_path in maps.values():
        path = ROOT/map_path
        data = read(path)
        extra.extend([path, ROOT/data['decision']])
        if data.get('source_acceptance'):
            extra.append(ROOT/data['source_acceptance'])
        extra.extend(ROOT/r['payload_path'] for r in data['entries'] if r.get('payload_path'))
    for path in extra:
        bindings[path.relative_to(ROOT).as_posix()] = sha(path)
    rows = [{'path':p,'sha256':s} for p,s in sorted(bindings.items())]
    verify(rows)
    config = {k:prior[k] for k in ('source_site','source_manifest','primary_maps','supplement_maps','guide_preview_map','guide_image_collection_map','flash_runtime_archive','blizzcast_source_map','related_talent_icon_map','source16_layout_map')}
    config.update(maps)
    config.update({'schema':'wow-v49-input-preparation/v1','prepared_utc':datetime.now(timezone.utc).isoformat(),'output':OUTPUT.relative_to(ROOT).as_posix(),'bindings':rows,'expected_ui_images':6,'expected_ui_bytes':5619,'expected_points_box_reused_targets':8,'expected_related_encyclopedia_images':3,'expected_related_encyclopedia_image_bytes':159173,'expected_related_guide_images':1,'expected_related_guide_image_bytes':17152,'expected_reward_script_repairs':1,'expected_guide_dynamic_display_reuses':1,'new_original_2008_images':0,'prior_accepted_version':'v46','scope':'Add four current ArchiveCraft illustrations with readable source links, and correct two reward-table button paths. Preserve historical article text and prior image/script data except the exact reward script literals.','network_requests':0,'deadline_utc':CUTOFF.isoformat()})
    PREP.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    return {'prepared':True,'bindings':len(rows),'preparation_sha256':sha(PREP)}
def execute():
    config, gate = read(PREP), read(GO)
    assert gate['accepted'] and gate['export_go'] and gate['preparation_sha256'] == sha(PREP)
    assert datetime.now(timezone.utc) < CUTOFF and shutil.disk_usage(ROOT).free >= FLOOR
    assert not OUTPUT.exists() and not OUTPUT.with_name(OUTPUT.name+'.partial').exists()
    verify(config['bindings'])
    sys.path.insert(0,str(ROOT/'tools'))
    import export_github_pages
    started = datetime.now(timezone.utc).isoformat()
    kwargs = {k:ROOT/config[k] for k in ('guide_preview_map','guide_image_collection_map','flash_runtime_archive','blizzcast_source_map','related_talent_icon_map','related_talent_ui_map','source16_layout_map','talent_box_layout_map','related_encyclopedia_image_map','related_guide_image_map')}
    result = export_github_pages.export_pages(source_site=ROOT/config['source_site'],manifest_path=ROOT/config['source_manifest'],output=OUTPUT,base_path='/WOW-Encyclopedia-Deployable-Archive/',workspace_root=ROOT,min_free_bytes=FLOOR,image_source_maps=tuple(ROOT/p for p in config['primary_maps']),supplement_image_source_maps=tuple(ROOT/p for p in config['supplement_maps']),allow_later_image_supplements=True,**kwargs)
    receipt = {'status':'export_executed_not_yet_accepted','started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'preparation_sha256':sha(PREP),'gate_sha256':sha(GO),'result':result,'provenance_sha256':sha(OUTPUT/'export-provenance.json'),'network_requests':0,'published':False}
    (HERE/'v49-build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare',action='store_true')
    group.add_argument('--execute',action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare() if args.prepare else execute()))

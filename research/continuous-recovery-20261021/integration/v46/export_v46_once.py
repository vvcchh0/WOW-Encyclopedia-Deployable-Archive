"""Build a new v46 tree from the accepted v45 inputs and two narrow maps."""
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
PREP = HERE/'v46-input-preparation.json'
GO = PUB/'root-v46-export-go.json'
OUTPUT = ROOT/'.scratch/pages-resources-20261021-v46'
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
    assert read(PUB/'root-v45-pages-online-reconciliation.json')['accepted']
    prior_path = ROOT/'research/continuous-recovery-20261021/integration/v45/v45-input-preparation.json'
    prior = read(prior_path)
    code_path = PUB/'root-v46-code-acceptance.json'
    code = read(code_path)
    assert code['accepted'] and code['tests']['count'] == 55 and code['tests']['skipped'] == 0
    bindings = {r['path']:r['sha256'] for r in prior['bindings']}
    bindings.update({r['path']:r['sha256'] for r in code['code_bindings']})
    maps = {
        'related_talent_ui_map':'research/continuous-recovery-20261021/integration/related-talent-ui/input-map.json',
        'talent_box_layout_map':'research/continuous-recovery-20261021/integration/talent-box-layout/input-map.json',
    }
    extra = [code_path, prior_path, PUB/'root-v45-local-acceptance.json', PUB/'root-v45-pages-online-reconciliation.json', Path(__file__)]
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
    config.update({'schema':'wow-v46-input-preparation/v1','prepared_utc':datetime.now(timezone.utc).isoformat(),'output':OUTPUT.relative_to(ROOT).as_posix(),'bindings':rows,'expected_ui_images':6,'expected_ui_bytes':5619,'expected_points_box_reused_targets':8,'new_original_2008_images':0,'prior_accepted_version':'v45','scope':'Add six attributed raw PNG UI images and reuse eight existing dated same-site point-box borders. All original talent scripts and data are retained.','network_requests':0,'deadline_utc':CUTOFF.isoformat()})
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
    kwargs = {k:ROOT/config[k] for k in ('guide_preview_map','guide_image_collection_map','flash_runtime_archive','blizzcast_source_map','related_talent_icon_map','related_talent_ui_map','source16_layout_map','talent_box_layout_map')}
    result = export_github_pages.export_pages(source_site=ROOT/config['source_site'],manifest_path=ROOT/config['source_manifest'],output=OUTPUT,base_path='/WOW-Encyclopedia-Deployable-Archive/',workspace_root=ROOT,min_free_bytes=FLOOR,image_source_maps=tuple(ROOT/p for p in config['primary_maps']),supplement_image_source_maps=tuple(ROOT/p for p in config['supplement_maps']),allow_later_image_supplements=True,**kwargs)
    receipt = {'status':'export_executed_not_yet_accepted','started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'preparation_sha256':sha(PREP),'gate_sha256':sha(GO),'result':result,'provenance_sha256':sha(OUTPUT/'export-provenance.json'),'network_requests':0,'published':False}
    (HERE/'v46-build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare',action='store_true')
    group.add_argument('--execute',action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare() if args.prepare else execute()))

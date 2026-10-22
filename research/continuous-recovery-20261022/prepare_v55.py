"""Accept the bounded icon extension and build a fresh derived version."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import types

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'.scratch/pages-resources-20261022-v55'
OLD=ROOT/'.scratch/pages-resources-20261022-v54'
PREP=HERE/'integration/v55-input-preparation.json'
FLOOR=11005853696
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def write(p,x):
    assert not p.exists(),p
    p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode())
sys.path.insert(0,str(ROOT/'tools'))

def accept_code():
    import related_talent_icons as new
    raw=subprocess.run(['git','show','6e9acf13:tools/related_talent_icons.py'],cwd=ROOT,capture_output=True,check=True).stdout
    old=types.ModuleType('root_accepted_v53_talent_icons');sys.modules[old.__name__]=old
    exec(compile(raw,'<accepted-v53-talent-icons>','exec'),old.__dict__)
    m1=ROOT/'research/continuous-recovery-20261021/integration/related-talent-icons/input-map.json'
    m2=HERE/'integration/related-talent-icons-v55/input-map.json'
    prefix='/WOW-Encyclopedia-Deployable-Archive/'
    before=old.load_related_talent_bundle(m1,ROOT,prefix)
    retained=new.load_related_talent_bundle(m1,ROOT,prefix)
    assert asdict(before)==asdict(retained),'v1 bundle changed'
    after=new.load_related_talent_bundle(m2,ROOT,prefix)
    assert len(after.assets)==1006 and len(before.assets)==986
    assert [asdict(x) for x in after.assets[:986]]==[asdict(x) for x in before.assets]
    assert json.loads(after.catalog_bytes)['assets'][:986]==json.loads(before.catalog_bytes)['assets']
    assert len(json.loads(after.catalog_bytes)['mappings'])==20
    assert after.notice_html==before.notice_html
    entries=read(m2)['entries'];expected={e['route']:e for e in entries}
    for asset in after.assets[986:]:
        entry=expected[asset.route]
        assert hashlib.sha256(asset.data).hexdigest()==entry['sha256']
        assert len(asset.data)==entry['length']
        assert asset.metadata['source_repository_path']==entry['repository_path']
        assert asset.metadata['classification']=='later_related_source'
        assert asset.metadata['original_2008_pixel_identity']=='unknown'
        assert asset.route.split('/')[4]==entry['class']
    assert sum(len(x.data) for x in after.assets[986:])==21820
    result={'schema':'wow-root-v55-code-acceptance/v1','accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
      'v1_compared_commit':'6e9acf132760d35f00b9ca5b12e158978957e2de','v1_bundle_exactly_unchanged':True,
      'all_986_prior_assets_and_catalog_rows_exactly_retained':True,'notice_unchanged':True,
      'new_mapped_icons':20,'new_original_2008_images':0,'new_network_requests':0,'mapped_bytes':21820,
      'worker_tests':{'passed':16,'evidence':'integration/related-talent-icons-v55/implementation/validation.json'},
      'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (ROOT/'tools/related_talent_icons.py',ROOT/'tests/test_related_talent_icons_v2.py',m2,m2.parent/'decision.json',m2.parent/'root-input-pins.json')]}
    write(HERE/'root-v55-code-acceptance.json',result);return result

def prepare():
    assert not OUT.exists() and shutil.disk_usage(ROOT).free>=FLOOR
    code=read(HERE/'root-v55-code-acceptance.json');assert code['accepted']
    assert read(HERE/'root-v54-export-acceptance.json')['accepted']
    prior=read(HERE/'integration/v54-input-preparation.json')
    allowed={r['path'] for r in code['bindings']};bindings={}
    for r in prior['bindings']:
        actual=sha(ROOT/r['path'])
        assert actual==r['sha256'] or r['path'] in allowed,r['path']
        bindings[r['path']]=actual
    for r in code['bindings']:
        assert sha(ROOT/r['path'])==r['sha256'];bindings[r['path']]=r['sha256']
    required=[Path(__file__),HERE/'root-v55-code-acceptance.json',HERE/'talent-icon-reuse-audit/audit.json']
    required += [p for p in (HERE/'integration/related-talent-icons-v55/assets').iterdir() if p.is_file()]
    for p in required:bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    config={k:v for k,v in prior.items() if k not in ('bindings','prepared_utc','output','schema','scope','new_related_images','prior_accepted_version')}
    config.update(schema='wow-v55-input-preparation/v1',prepared_utc=datetime.now(timezone.utc).isoformat(),
      output=OUT.relative_to(ROOT).as_posix(),related_talent_icon_map='research/continuous-recovery-20261022/integration/related-talent-icons-v55/input-map.json',
      prior_accepted_version='v54',new_related_images=20,scope='Twenty explicit same-class artwork mappings; keep all 2008 talent data unchanged.',
      bindings=[{'path':p,'sha256':h} for p,h in sorted(bindings.items())])
    write(PREP,config);return {'prepared':True,'bindings':len(bindings),'sha256':sha(PREP)}

def export():
    config=read(PREP)
    assert datetime.now(timezone.utc)<datetime.fromisoformat(config['deadline_utc'].replace('Z','+00:00'))
    assert not OUT.exists() and shutil.disk_usage(ROOT).free>=FLOOR
    for row in config['bindings']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
    spec=importlib.util.spec_from_file_location('root_v54_export_config',HERE/'prepare_v54.py')
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    import export_github_pages
    kwargs={k:ROOT/config[k] for k in prior.CONFIG_KEYS if k not in ('source_site','source_manifest','primary_maps','supplement_maps')}
    kwargs['related_faction_icon_map']=ROOT/config['related_faction_icon_map']
    started=datetime.now(timezone.utc).isoformat()
    result=export_github_pages.export_pages(source_site=ROOT/config['source_site'],manifest_path=ROOT/config['source_manifest'],output=OUT,
       base_path='/WOW-Encyclopedia-Deployable-Archive/',workspace_root=ROOT,max_bytes=None,min_free_bytes=FLOOR,
       image_source_maps=tuple(ROOT/p for p in config['primary_maps']),supplement_image_source_maps=tuple(ROOT/p for p in config['supplement_maps']),
       allow_later_image_supplements=True,restore_aldor_scryers_lore=True,**kwargs)
    receipt={'schema':'wow-v55-build-receipt/v1','status':'built_pending_independent_acceptance','started_utc':started,
      'finished_utc':datetime.now(timezone.utc).isoformat(),'preparation_sha256':sha(PREP),'provenance_sha256':sha(OUT/'export-provenance.json'),
      'result':result,'disk_free_after_bytes':shutil.disk_usage(ROOT).free,'network_requests':0,'published':False}
    write(HERE/'integration/v55-build-receipt.json',receipt);return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['accept-code','prepare','export']);args=parser.parse_args()
    result={'accept-code':accept_code,'prepare':prepare,'export':export}[args.mode]()
    print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','result')},ensure_ascii=False))

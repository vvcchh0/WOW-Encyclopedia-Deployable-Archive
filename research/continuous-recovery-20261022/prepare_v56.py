"""Accept the nine canonical mappings and build one fresh derived version."""
from __future__ import annotations
from dataclasses import asdict
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,shutil,subprocess,sys,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
OUT=ROOT/'.scratch/pages-resources-20261022-v56';FLOOR=11005853696
PREP=HERE/'integration/v56-input-preparation.json'
MAP=HERE/'integration/related-talent-icons-v56/input-map.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def write(p,x):
 assert not p.exists(),p
 p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode())
sys.path.insert(0,str(ROOT/'tools'))
def accept_code():
 import related_talent_icons as new
 raw=subprocess.run(['git','show','9dd153096cfc649e8c46f6cfecc823b9a9e6f0e8:tools/related_talent_icons.py'],cwd=ROOT,capture_output=True,check=True).stdout
 old=types.ModuleType('root_accepted_v55_talent_icons');sys.modules[old.__name__]=old
 exec(compile(raw,'<accepted-v55-talent-icons>','exec'),old.__dict__)
 m1=ROOT/'research/continuous-recovery-20261021/integration/related-talent-icons/input-map.json'
 m2=HERE/'integration/related-talent-icons-v55/input-map.json'
 prefix='/WOW-Encyclopedia-Deployable-Archive/'
 for m in (m1,m2):
  before=old.load_related_talent_bundle(m,ROOT,prefix)
  retained=new.load_related_talent_bundle(m,ROOT,prefix)
  assert asdict(before)==asdict(retained),m
 prior=new.load_related_talent_bundle(m2,ROOT,prefix)
 after=new.load_related_talent_bundle(MAP,ROOT,prefix)
 assert len(prior.assets)==1006 and len(after.assets)==1024
 assert [asdict(a) for a in after.assets[:1006]]==[asdict(a) for a in prior.assets]
 oc,nc=json.loads(prior.catalog_bytes),json.loads(after.catalog_bytes)
 assert nc['assets'][:1006]==oc['assets'] and nc['mappings'][:20]==oc['mappings']
 assert len(nc['mappings'])==38 and after.notice_html==prior.notice_html
 entries=read(MAP)['entries'];byroute={r['route']:r for r in entries}
 for a in after.assets[1006:]:
  e=byroute[a.route]
  assert (hashlib.sha256(a.data).hexdigest(),len(a.data))==(e['sha256'],e['length'])
  assert a.metadata['old_data_sha256']==e['old_data_sha256'] and a.metadata['old_source_data_sha256']==e['old_source_data_sha256']
  assert a.metadata['classification']=='later_related_source' and a.metadata['original_capture_timestamp'] is None
 assert sum(len(a.data) for a in after.assets[1006:])==19439
 bindings=[ROOT/'tools/related_talent_icons.py',ROOT/'tests/test_related_talent_icons_v3.py',MAP,MAP.parent/'decision.json',MAP.parent/'root-input-pins.json',MAP.parent/'root-source-acceptance.json',MAP.parent/'source-preparation.json',HERE/'talent-icon-remaining-audit/audit.json']
 result={'schema':'wow-root-v56-code-acceptance/v1','accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'compared_commit':'9dd153096cfc649e8c46f6cfecc823b9a9e6f0e8','v1_and_v2_entire_bundles_exactly_unchanged':True,'all_1006_prior_assets_and_catalog_rows_exactly_retained':True,'all_20_prior_mapping_rows_retained':True,'notice_unchanged':True,'new_mapped_icons':18,'new_original_2008_images':0,'new_network_requests':0,'mapped_bytes':19439,'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in bindings]}
 write(HERE/'root-v56-code-acceptance.json',result);return result

def prepare():
 assert not OUT.exists() and shutil.disk_usage(ROOT).free>=FLOOR
 code=read(HERE/'root-v56-code-acceptance.json');assert code['accepted']
 assert read(HERE/'root-v55-export-acceptance.json')['accepted'] and read(HERE/'root-v55-browser-acceptance.json')['accepted']
 prior=read(HERE/'integration/v55-input-preparation.json')
 allowed={r['path'] for r in code['bindings']};bindings={}
 for r in prior['bindings']:
  actual=sha(ROOT/r['path']);assert actual==r['sha256'] or r['path'] in allowed,r['path'];bindings[r['path']]=actual
 for r in code['bindings']:
  assert sha(ROOT/r['path'])==r['sha256'];bindings[r['path']]=r['sha256']
 required=[Path(__file__),HERE/'root-v56-code-acceptance.json']+[p for p in (MAP.parent/'assets').iterdir() if p.is_file()]
 for p in required:bindings[p.relative_to(ROOT).as_posix()]=sha(p)
 config={k:v for k,v in prior.items() if k not in ('bindings','prepared_utc','output','schema','scope','new_related_images','prior_accepted_version')}
 config.update(schema='wow-v56-input-preparation/v1',prepared_utc=datetime.now(timezone.utc).isoformat(),output=OUT.relative_to(ROOT).as_posix(),related_talent_icon_map=MAP.relative_to(ROOT).as_posix(),prior_accepted_version='v55',new_related_images=18,deadline_utc='2026-10-22T13:41:33Z',scope='Eighteen exact canonical-title same-class mappings; preserve all original talent data.',bindings=[{'path':p,'sha256':h} for p,h in sorted(bindings.items())])
 write(PREP,config);return {'prepared':True,'bindings':len(bindings),'sha256':sha(PREP)}

def export():
 config=read(PREP)
 assert datetime.now(timezone.utc)<datetime.fromisoformat(config['deadline_utc'].replace('Z','+00:00'))
 assert not OUT.exists() and shutil.disk_usage(ROOT).free>=FLOOR
 for row in config['bindings']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 spec=importlib.util.spec_from_file_location('root_v54_export_config',HERE/'prepare_v54.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
 import export_github_pages
 kwargs={k:ROOT/config[k] for k in prior.CONFIG_KEYS if k not in ('source_site','source_manifest','primary_maps','supplement_maps')}
 kwargs['related_faction_icon_map']=ROOT/config['related_faction_icon_map']
 started=datetime.now(timezone.utc).isoformat()
 result=export_github_pages.export_pages(source_site=ROOT/config['source_site'],manifest_path=ROOT/config['source_manifest'],output=OUT,base_path='/WOW-Encyclopedia-Deployable-Archive/',workspace_root=ROOT,max_bytes=None,min_free_bytes=FLOOR,image_source_maps=tuple(ROOT/p for p in config['primary_maps']),supplement_image_source_maps=tuple(ROOT/p for p in config['supplement_maps']),allow_later_image_supplements=True,restore_aldor_scryers_lore=True,**kwargs)
 receipt={'schema':'wow-v56-build-receipt/v1','status':'built_pending_independent_acceptance','started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'preparation_sha256':sha(PREP),'provenance_sha256':sha(OUT/'export-provenance.json'),'result':result,'disk_free_after_bytes':shutil.disk_usage(ROOT).free,'network_requests':0,'published':False}
 write(HERE/'integration/v56-build-receipt.json',receipt);return receipt

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['accept-code','prepare','export']);args=parser.parse_args()
 result={'accept-code':accept_code,'prepare':prepare,'export':export}[args.mode]()
 print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','result')},ensure_ascii=False))

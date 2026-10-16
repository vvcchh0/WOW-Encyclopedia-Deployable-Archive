import hashlib,importlib.util,json,os,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;B=O.parent;S=R/'.scratch/pages-resources-20261016-v25';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def prepare():
 out=O/'root-v25-local-acceptance.json';assert not out.exists();bindings=[]
 for name in ['root-v25-input-acceptance.json','root-v25-export-acceptance.json','root-v25-browser-acceptance.json','root-v25-static-metrics-acceptance.json']:
  p=O/name;d=json.loads(p.read_bytes());assert d['accepted'];bindings.append(bind(p))
 p=json.loads((S/'export-provenance.json').read_bytes());records={x['route']:x for x in p['files']}
 images=json.loads((R/'research/continuous-recovery-20261016/publication/root-neighbors9-source-acceptance.json').read_bytes())['accepted_images']
 paths={__import__('urllib.parse',fromlist=['urlsplit']).urlsplit(x['original']).path.lstrip('/') for x in images}
 for g in p['guide_image_collections']['groups']:paths.update(records[g[k]]['output_path'] for k in ['guide_route','gallery_route'])
 paths.update(['export-provenance.json','__offline/route-map.json','__offline/pages_runtime.js','__offline/related-images/index.html'])
 objects=[]
 for rel in sorted(paths):
  item=bind(S/rel);item['path']=rel;item['source_list']=rel=='export-provenance.json';item['mime']={'.html':['text/html'],'.json':['application/json'],'.js':['text/javascript','application/javascript','application/x-javascript'],'.jpg':['image/jpeg']}[Path(rel).suffix];objects.append(item)
 d={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'local_site':S.relative_to(R).as_posix(),'objects':objects,'bindings':bindings+[bind(S/'export-provenance.json'),bind(B/'local/v25-neighbor-supplement-source-map.json'),bind(B/'local/v25-guide-image-collection-map.json')],'new_images':4,'new_image_bytes':732640,'guide_collection_images':35,'declared_files':8641,'actual_files':8642,'published':False}
 out.write_bytes((json.dumps(d,indent=2)+'\n').encode());print(json.dumps({'accepted':True,'objects':len(objects)}))
def publish():
 report=O/'v25-pages-publication.json';assert not report.exists();gate=json.loads((O/'root-v25-local-acceptance.json').read_bytes());assert gate['accepted']
 for b in gate['bindings']:assert sha(R/b['path'])==b['sha256']
 for x in gate['objects']:assert sha(S/x['path'])==x['sha256']
 assert shutil.disk_usage(R).free>=11005853696
 os.environ['GIT_CONFIG_COUNT']='3'
 for n,(k,v) in enumerate([('http.proxy','http://127.0.0.1:7890'),('http.lowSpeedLimit','1024'),('http.lowSpeedTime','30')]):os.environ[f'GIT_CONFIG_KEY_{n}']=k;os.environ[f'GIT_CONFIG_VALUE_{n}']=v
 spec=importlib.util.spec_from_file_location('publish_focused_v25',R/'tools/publish_github_pages.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 result=m.build_commit(root=R,site=S,branch='gh-pages',message='Publish v25: three more guide originals and one Lunar Festival model image',report_path=report,push=True);print(json.dumps({'status':result['status'],'commit':result['new_commit_sha']}))
if __name__=='__main__':publish() if '--publish' in sys.argv else prepare()

"""Bind accepted v23 inputs; publication uses the frozen receipt and normal push."""
import argparse,hashlib,importlib.util,json,os,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';O=B/'publication';S=R/'.scratch/pages-resources-20261016-v23'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def prepare():
    target=O/'root-v23-local-acceptance.json';assert not target.exists()
    source_names=['root-gallery-neighbors01-source-acceptance.json','root-gallery-neighbors02-source-acceptance.json','root-gallery-neighbors03-source-acceptance.json','root-gallery-neighbors-full15-source-acceptance.json','root-gallery-neighbors-other4-source-acceptance.json']
    gates=['root-v23-export-acceptance.json','root-v23-browser-acceptance.json','root-v23-final40-input-acceptance.json','root-guide-collections-code-acceptance.json']+source_names
    bindings=[]
    for name in gates:
        p=O/name;d=json.loads(p.read_bytes());assert d['accepted'];bindings.append(bind(p))
    for p in [S/'export-provenance.json',R/'.scratch/offline-navigation-20261015-v15/build-manifest.json',R/'offline/build-manifest.json',B/'integration/v23-build/worker-build-v23-final40.json',B/'integration/v23-neighbor-supplement-source-map-final40.json',B/'integration/v23-neighbor-supplement-catalog-map-final40.json',B/'integration/v23-guide-image-collection-map-final40.json',R/'tools/export_github_pages.py',R/'tools/guide_previews.py',R/'tools/guide_image_collections.py',B/'integration/v18-guide-previews/guide-previews-source-map-v2.json']:bindings.append(bind(p))
    images=[x for name in source_names for x in json.loads((O/name).read_bytes())['accepted_images']]
    assert len(images)==40
    from urllib.parse import urlsplit
    paths={urlsplit(x['original']).path.lstrip('/') for x in images}
    provenance=json.loads((S/'export-provenance.json').read_bytes());records={x['route']:x for x in provenance['files']}
    for group in provenance['guide_image_collections']['groups']:
        paths.update(records[group[k]]['output_path'] for k in ['guide_route','gallery_route'])
    paths.update(['export-provenance.json','__offline/route-map.json','__offline/pages_runtime.js','news/rss-08-2007.xml.html','info/encyclopedia/index.xml.html','pvp/worldpvp/cityattacks-gallery.html'])
    objects=[]
    for p in sorted(paths):
        objects.append({'path':p,'mime':{'.json':['application/json'],'.js':['application/javascript','text/javascript','application/x-javascript'],'.html':['text/html'],'.gif':['image/gif'],'.jpg':['image/jpeg']}[Path(p).suffix],'source_list':p=='export-provenance.json',**{k:v for k,v in bind(S/p).items() if k!='path'}})
    gate=json.loads((O/gates[0]).read_bytes());browser=json.loads((O/gates[1]).read_bytes())
    assert gate['checked_declared_files']==8620 and gate['actual_files']==8621 and len(objects)<=64
    result={'schema':'wow-recovery.root.v23-local-acceptance.v1','checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'published':False,'network_requests':0,'local_site':S.relative_to(R).as_posix(),'declared_files':8620,'actual_files':8621,'tree_bytes':gate['checked_tree_bytes'],'bindings':bindings,'objects':objects,'new_images':40,'new_image_bytes':6901604,'guide_collection_groups':3,'guide_collection_images':32,'remaining_news_missing_references':574,'browser_checks':len(browser['checks']),'independent_post_export_checks_passed':True,'new_export_invocations':0}
    target.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','objects')}))

def publish():
    report=O/'v23-pages-publication.json';assert not report.exists()
    d=json.loads((O/'root-v23-local-acceptance.json').read_bytes());assert d['accepted'] and not d['published']
    assert shutil.disk_usage(R).free>=11005853696
    for b in d['bindings']:assert sha(R/b['path'])==b['sha256'],b['path']
    for b in d['objects']:assert sha(S/b['path'])==b['sha256'],b['path']
    os.environ['GIT_CONFIG_COUNT']='3'
    for n,(k,v) in enumerate([('http.proxy','http://127.0.0.1:7890'),('http.lowSpeedLimit','1024'),('http.lowSpeedTime','60')]):os.environ[f'GIT_CONFIG_KEY_{n}']=k;os.environ[f'GIT_CONFIG_VALUE_{n}']=v
    p=R/'tools/publish_github_pages.py';s=importlib.util.spec_from_file_location('publish_v23_module',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
    result=m.build_commit(root=R,site=S,branch='gh-pages',message='Publish v23: display recovered guide originals and preserve neighboring image sources',report_path=report,push=True)
    print(json.dumps({k:result.get(k) for k in ('status','new_commit_sha')}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');a=p.parse_args();publish() if a.publish else prepare()

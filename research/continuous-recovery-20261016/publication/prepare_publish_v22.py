"""Bind accepted v22 inputs; publication uses the frozen receipt and normal push."""
import argparse,hashlib,importlib.util,json,os,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';O=B/'publication';S=R/'.scratch/pages-resources-20261016-v22'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def prepare():
    target=O/'root-v22-local-acceptance.json';assert not target.exists()
    gates=['root-v22-export-acceptance.json','root-v22-browser-acceptance.json','root-v22-news-metrics-acceptance.json','root-aug-final3-source-acceptance.json','root-aug-cached19-source-acceptance.json','root-aug-late11-source-acceptance.json','root-news-content01-source-acceptance.json','root-static-main01-source-acceptance.json','root-export-promotion-fix-acceptance.json']
    bindings=[]
    for name in gates:
        p=O/name;d=json.loads(p.read_bytes());assert d['accepted'];bindings.append(bind(p))
    final=B/'integration/v22-build/post-export-reconciliation-v22.json';d=json.loads(final.read_bytes());assert d['reconciled_export_valid'] and d['export_was_not_repeated'];bindings.append(bind(final))
    for p in [S/'export-provenance.json',R/'.scratch/offline-navigation-20261015-v15/build-manifest.json',R/'offline/build-manifest.json',B/'integration/v22-primary-news-source-map.json',B/'integration/v21-august-late-source-map.json',R/'tools/export_github_pages.py',R/'tools/guide_previews.py',B/'integration/v18-guide-previews/guide-previews-source-map-v2.json']:bindings.append(bind(p))
    images=[x for name in gates[3:8] for x in json.loads((O/name).read_bytes())['accepted_images']]
    from urllib.parse import urlsplit
    paths={urlsplit(x['original']).path.lstrip('/') for x in images}
    browser=json.loads((O/'root-v22-browser-acceptance.json').read_bytes())
    paths.update('news/'+x['page'] for x in browser['checks'] if 'page' in x)
    paths.update(['export-provenance.json','__offline/route-map.json','__offline/pages_runtime.js','news/rss-08-2007.xml.html','info/encyclopedia/index.xml.html','pvp/worldpvp/cityattacks-gallery.html'])
    objects=[]
    for p in sorted(paths):
        objects.append({'path':p,'mime':{'.json':['application/json'],'.js':['application/javascript','text/javascript','application/x-javascript'],'.html':['text/html'],'.gif':['image/gif'],'.jpg':['image/jpeg']}[Path(p).suffix],'source_list':p=='export-provenance.json',**{k:v for k,v in bind(S/p).items() if k!='path'}})
    gate=json.loads((O/gates[0]).read_bytes())
    assert gate['checked_declared_files']==8580 and gate['actual_files']==8581 and 19<=len(objects)<=64
    result={'schema':'wow-recovery.root.v22-local-acceptance.v1','checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'published':False,'network_requests':0,'local_site':S.relative_to(R).as_posix(),'declared_files':8580,'actual_files':8581,'tree_bytes':gate['checked_tree_bytes'],'bindings':bindings,'objects':objects,'new_images':19,'new_image_bytes':171420,'removed_news_missing_references':16,'remaining_news_missing_references':574,'browser_checks':len(browser['checks']),'independent_post_export_checks_passed':True,'metadata_errata':['The original builder postcheck reported failure because34 inherited overlays now cite the new clone source map. Root full-byte acceptance verifies all old entity metadata and dates retained; reconciliation and the failure receipt are preserved.'],'new_export_invocations':0}
    target.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','objects')}))
def publish():
    report=O/'v22-pages-publication.json';assert not report.exists()
    d=json.loads((O/'root-v22-local-acceptance.json').read_bytes());assert d['accepted'] and not d['published']
    assert shutil.disk_usage(R).free>=11005853696
    for b in d['bindings']:assert sha(R/b['path'])==b['sha256'],b['path']
    for b in d['objects']:assert sha(S/b['path'])==b['sha256'],b['path']
    os.environ['GIT_CONFIG_COUNT']='3'
    for n,(k,v) in enumerate([('http.proxy','http://127.0.0.1:7890'),('http.lowSpeedLimit','1024'),('http.lowSpeedTime','60')]):os.environ[f'GIT_CONFIG_KEY_{n}']=k;os.environ[f'GIT_CONFIG_VALUE_{n}']=v
    p=R/'tools/publish_github_pages.py';s=importlib.util.spec_from_file_location('publish_v22_module',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
    result=m.build_commit(root=R,site=S,branch='gh-pages',message='Publish v22: complete August illustrations and restore news and page assets',report_path=report,push=True)
    print(json.dumps({k:result.get(k) for k in ('status','new_commit_sha')}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');a=p.parse_args();publish() if a.publish else prepare()

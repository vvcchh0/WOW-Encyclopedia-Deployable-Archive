"""Bind accepted v19 inputs; publication uses the frozen receipt and normal push."""
import argparse,hashlib,importlib.util,json,os,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';O=B/'publication';S=R/'.scratch/pages-resources-20261016-v19'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def prepare():
    target=O/'root-v19-local-acceptance.json';assert not target.exists()
    gates=['root-v19-export-acceptance.json','root-v19-browser-acceptance.json','root-v19-news-metrics-acceptance.json','root-news-shared10-source-acceptance.json','root-news-shared13-source-acceptance.json','root-shared-news-visual-acceptance.json']
    bindings=[]
    for name in gates:
        p=O/name;d=json.loads(p.read_bytes());assert d['accepted'];bindings.append(bind(p))
    final=B/'integration/v19-build/post-export-reconciliation-v19-final.json';d=json.loads(final.read_bytes());assert d['accepted'] and d['reconciled_export_valid'] and d['export_invocations_after_worker_failure']==0;bindings.append(bind(final))
    for p in [S/'export-provenance.json',R/'.scratch/offline-navigation-20261015-v15/build-manifest.json',R/'offline/build-manifest.json',B/'integration/v19-primary-news-source-map.json',R/'tools/export_github_pages.py',R/'tools/guide_previews.py',B/'integration/v18-guide-previews/guide-previews-source-map-v2.json']:bindings.append(bind(p))
    images=json.loads((B/'integration/v19-primary-news-source-map.json').read_bytes())['items'][-10:]
    from urllib.parse import urlsplit
    paths={urlsplit(x['logical_url']).path.lstrip('/') for x in images}
    browser=json.loads((O/'root-v19-browser-acceptance.json').read_bytes())
    paths.update('news/'+x['page'] for x in browser['checks'] if 'page' in x)
    paths.update(['export-provenance.json','__offline/route-map.json','__offline/pages_runtime.js','news/rss-08-2007.xml.html','info/encyclopedia/index.xml.html','pvp/worldpvp/cityattacks-gallery.html'])
    objects=[]
    for p in sorted(paths):
        objects.append({'path':p,'mime':{'.json':['application/json'],'.js':['application/javascript','text/javascript','application/x-javascript'],'.html':['text/html'],'.gif':['image/gif'],'.jpg':['image/jpeg']}[Path(p).suffix],'source_list':p=='export-provenance.json',**{k:v for k,v in bind(S/p).items() if k!='path'}})
    gate=json.loads((O/gates[0]).read_bytes())
    assert gate['checked_declared_files']==8537 and gate['actual_files']==8538 and len(objects)==24
    result={'schema':'wow-recovery.root.v19-local-acceptance.v1','checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'published':False,'network_requests':0,'local_site':S.relative_to(R).as_posix(),'declared_files':8537,'actual_files':8538,'tree_bytes':gate['checked_tree_bytes'],'bindings':bindings,'objects':objects,'new_images':10,'new_image_bytes':33224,'removed_news_missing_references':184,'remaining_news_missing_references':614,'browser_checks':len(browser['checks']),'post_export_helper_failure_reconciled':True,'new_export_invocations':0}
    target.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','objects')}))
def publish():
    report=O/'v19-pages-publication.json';assert not report.exists()
    d=json.loads((O/'root-v19-local-acceptance.json').read_bytes());assert d['accepted'] and not d['published']
    assert shutil.disk_usage(R).free>=11005853696
    for b in d['bindings']:assert sha(R/b['path'])==b['sha256'],b['path']
    for b in d['objects']:assert sha(S/b['path'])==b['sha256'],b['path']
    os.environ['GIT_CONFIG_COUNT']='3'
    for n,(k,v) in enumerate([('http.proxy','http://127.0.0.1:7890'),('http.lowSpeedLimit','1024'),('http.lowSpeedTime','60')]):os.environ[f'GIT_CONFIG_KEY_{n}']=k;os.environ[f'GIT_CONFIG_VALUE_{n}']=v
    p=R/'tools/publish_github_pages.py';s=importlib.util.spec_from_file_location('publish_v19_module',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
    result=m.build_commit(root=R,site=S,branch='gh-pages',message='Publish v19: restore ten shared news images',report_path=report,push=True)
    print(json.dumps({k:result.get(k) for k in ('status','new_commit_sha')}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');a=p.parse_args();publish() if a.publish else prepare()

"""Publish the fully accepted v33 tree using the unchanged Pages publisher."""
import hashlib, importlib.util, json, os, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
SITE=ROOT/'.scratch/pages-resources-20261018-v33'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def main():
    assert sys.argv[1:]==['--publish-root-go']
    report=PUB/'v33-pages-publication.json'; assert not report.exists()
    gate=read(PUB/'root-v33-local-acceptance.json'); assert gate['accepted'] and not gate['published']
    for item in gate['bindings']:
        assert sha(ROOT/item['path'])==item['sha256'],item['path']
    for item in gate['objects']:
        assert sha(SITE/item['path'])==item['sha256'] and (SITE/item['path']).stat().st_size==item['bytes']
    assert shutil.disk_usage(ROOT).free>=11005853696
    tool=ROOT/'tools/publish_github_pages.py'
    assert sha(tool)=='e7f4992dfdeae9f83f6771c538c8d55b084316fb2f2e73c92e874df319de9934'
    git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT)
    head=git('rev-parse','HEAD').decode().strip()
    assert git('rev-parse','origin/main').decode().strip()==head
    for name in ['tools/export_github_pages.py','tools/historical_exhibits.py']:
        assert hashlib.sha256(git('show',f'HEAD:{name}')).hexdigest()==sha(ROOT/name)
    os.environ['GIT_CONFIG_COUNT']='3'
    for n,(key,value) in enumerate([('http.proxy','http://127.0.0.1:7890'),('http.lowSpeedLimit','1024'),('http.lowSpeedTime','30')]):
        os.environ[f'GIT_CONFIG_KEY_{n}']=key;os.environ[f'GIT_CONFIG_VALUE_{n}']=value
    spec=importlib.util.spec_from_file_location('root_accepted_v33_publisher',tool)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    result=module.build_commit(root=ROOT,site=SITE,branch='gh-pages',
        message='Publish v33: restore original image links, guide illustrations and archive resources',report_path=report,push=True)
    print(json.dumps({'status':result['status'],'commit':result['new_commit_sha']}))
if __name__=='__main__':main()

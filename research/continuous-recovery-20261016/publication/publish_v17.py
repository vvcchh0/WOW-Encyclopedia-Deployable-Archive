"""Publish the independently accepted v17 through the isolated Git index."""
import hashlib,importlib.util,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
SITE=ROOT/'.scratch/pages-resources-20261016-v17'
def main():
    local=json.loads((OUT/'root-v17-local-acceptance.json').read_bytes())
    export=json.loads((OUT/'root-v17-export-acceptance.json').read_bytes())
    assert local['accepted'] and export['accepted']
    assert hashlib.sha256((SITE/'export-provenance.json').read_bytes()).hexdigest()==export['export_provenance_sha256']
    for gate in local['gates'].values():
        assert hashlib.sha256((ROOT/gate['path']).read_bytes()).hexdigest()==gate['sha256']
    count=int(os.environ.get('GIT_CONFIG_COUNT','0'))
    settings=[('http.proxy','http://127.0.0.1:7890'),('http.lowSpeedLimit','1024'),('http.lowSpeedTime','60')]
    for offset,(key,value) in enumerate(settings):
        os.environ[f'GIT_CONFIG_KEY_{count+offset}']=key
        os.environ[f'GIT_CONFIG_VALUE_{count+offset}']=value
    os.environ['GIT_CONFIG_COUNT']=str(count+len(settings))
    spec=importlib.util.spec_from_file_location('publish_pages',ROOT/'tools/publish_github_pages.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result=module.build_commit(root=ROOT,site=SITE,branch='gh-pages',
        message='Publish v17: news image recovery and preserved guide previews',
        report_path=OUT/'v17-pages-publication.json',push=True)
    print(json.dumps({k:result.get(k) for k in ['new_commit_sha','network_push_performed','push_returncode','status']}))
if __name__=='__main__':main()

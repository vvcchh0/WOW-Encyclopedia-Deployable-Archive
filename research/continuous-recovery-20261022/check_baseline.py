"""Fresh read-only GitHub/local baseline for the bounded dungeon-source run."""
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=HERE/'baseline-acceptance.json'
assert not OUT.exists()
env=os.environ.copy()
for key in list(env):
    if key.lower() in {'http_proxy','https_proxy','all_proxy','no_proxy'}:
        env.pop(key,None)
attempts=[]
def api(endpoint):
    for route in ('direct','proxy'):
        child=env.copy()
        if route=='proxy':child.update(HTTPS_PROXY='http://127.0.0.1:7890',HTTP_PROXY='http://127.0.0.1:7890',NO_PROXY='',no_proxy='')
        started=datetime.now(timezone.utc).isoformat()
        try:
            p=subprocess.run(['gh','api',endpoint],cwd=ROOT,env=child,capture_output=True,text=True,timeout=30)
            attempts.append({'endpoint':endpoint,'route':route,'exit_code':p.returncode,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat()})
            if p.returncode==0:return json.loads(p.stdout)
            if not any(x in p.stderr.lower() for x in ('timeout','timed out','tls','connection','network','connect','resolve','eof')):
                raise RuntimeError('Non-transport API failure; no blind proxy retry')
        except subprocess.TimeoutExpired:
            attempts.append({'endpoint':endpoint,'route':route,'timed_out':True,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat()})
    raise RuntimeError('GitHub baseline unavailable')
repo='repos/vvcchh0/WOW-Encyclopedia-Deployable-Archive/'
main=api(repo+'git/ref/heads/main')['object']['sha']
pages=api(repo+'pages/builds/latest')
release=api(repo+'releases/latest')
assert main=='6e13e04ccbc331a2bb89273cc62eb63b8b6a7b2d'
assert pages['status']=='built' and pages['commit']=='d46c14a0d655cf55a2608581441726845537a1f4'
assert release['draft'] is False and release['tag_name']=='archive-20080512-browser-20261021-v52'
local=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert local==main
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT).strip()
pins={
 'offline/build-manifest.json':'397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459',
 '.scratch/offline-navigation-20261015-v15/build-manifest.json':'d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002',
 '.scratch/offline-non-gallery-20261021-v16/build-manifest.json':'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a',
 '.scratch/pages-resources-20261021-v52/export-provenance.json':'440390ed4b1bc429e290c21c15809387dc304918bbab47510bca5712c70d0113',
}
bindings=[]
for relative,digest in pins.items():
    p=ROOT/relative;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,relative
    bindings.append({'path':relative,'bytes':p.stat().st_size,'sha256':digest})
free=shutil.disk_usage(ROOT).free;assert free>=11005853696
report={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'main':main,
 'pages':{'commit':pages['commit'],'status':pages['status']},
 'release':{'id':release['id'],'tag':release['tag_name'],'assets':[{'name':a['name'],'bytes':a['size'],'digest':a.get('digest')} for a in release['assets']]},
 'local_tracked_tree_clean':True,'frozen_bindings':bindings,'disk_free_bytes':free,'attempts':attempts,
 'scope':'GitHub metadata and local immutable inputs only; no source website or Wayback request.'}
OUT.write_bytes((json.dumps(report,indent=2)+'\n').encode())
print(json.dumps({'accepted':True,'main':main,'pages':pages['commit'],'release':release['tag_name'],'disk_free_bytes':free}))

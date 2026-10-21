"""Run the accepted object verifier with current exact objects and larger WASM timeouts."""
import argparse
import hashlib
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];PUB=Path(__file__).resolve().parent
FROZEN=ROOT/'research/continuous-recovery-20261018/publication/verify_pages_v32.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--version',required=True);args=parser.parse_args()
assert args.version in {'v41','v42','v43','v44','v45','v46','v47','v48','v49'}
version=args.version;gate_path=PUB/f'root-{version}-local-acceptance.json';gate=json.loads(gate_path.read_bytes())
assert gate['accepted']
assert sha(FROZEN)=='82f9c2bce15c618e33d31bb583192a217a2f419d0e7cf85714f47709d5d09289'
final=PUB/f'root-{version}-pages-online-acceptance.json';assert not final.exists()
raw_result=PUB/f'{version}-online-verifier-result.json';assert not raw_result.exists()
# GitHub API follows the already-tested per-process proxy. The curl verifier
# still explicitly attempts direct first for every exact hosted object.
os.environ['HTTPS_PROXY']='http://127.0.0.1:7890'
os.environ['HTTP_PROXY']='http://127.0.0.1:7890'
os.environ['NO_PROXY']=''
os.environ['no_proxy']=''
spec=importlib.util.spec_from_file_location('root_pages_object_verifier',FROZEN)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=PUB;module.SITE=ROOT/gate['local_site'];module.PUBLISH_REPORT=PUB/f'{version}-pages-publication.json'
module.PROGRESS_REPORT=PUB/f'{version}-online-progress.json';module.FINAL_REPORT=raw_result
def mimes(path):
    if path.endswith('.html'):return {'text/html'}
    if path.endswith('.js'):return {'application/javascript','text/javascript'}
    if path.endswith('.json'):return {'application/json'}
    if path.endswith('.css'):return {'text/css'}
    if path.endswith('.wasm'):return {'application/wasm'}
    if path.endswith(('.jpg','.jpeg')):return {'image/jpeg'}
    if path.endswith('.png'):return {'image/png'}
    if path.endswith('.gif'):return {'image/gif'}
    raise RuntimeError('No reviewed MIME for '+path)
module.OBJECTS=[dict(r,mime=mimes(r['path']),source_list=r['path']=='export-provenance.json') for r in gate['objects']]
assert len(module.OBJECTS)==len({r['path'] for r in module.OBJECTS})<=128
module.MAX_ATTEMPTS=2*len(module.OBJECTS);module.MAX_SECONDS=600;module.MAX_BODY_BYTES=64*1024*1024
module.SOURCE_LIST_TIMEOUT=180;module.OTHER_TIMEOUT=60
original_attempt=module.run_attempt
def attempt(*args,**kwargs):
    result=original_attempt(*args,**kwargs)
    if result.get('http_status') in {429,503}:
        stop=PUB/f'{version}-online-endpoint-stop.json'
        assert not stop.exists()
        stop.write_text(json.dumps({'checked_utc':datetime.now(timezone.utc).isoformat(),'attempt':result,
            'stop':'No proxy retry of endpoint limit; cool down at least120seconds before any new window'},indent=2)+'\n',encoding='utf-8')
        raise RuntimeError('Hosted endpoint limit; stopped without proxy retry')
    return result
module.run_attempt=attempt
result_code=module.main();result=json.loads(raw_result.read_bytes())
result.update({'schema':'wow-pages-online-acceptance/v2','version':version,'verifier_source_sha256':sha(FROZEN),
    'raw_verifier_result_sha256':sha(raw_result),'local_gate_sha256':sha(gate_path)})
final.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
raise SystemExit(result_code)

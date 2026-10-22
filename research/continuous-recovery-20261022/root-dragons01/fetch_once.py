"""One exact related page, using the already reviewed bounded source runner."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RUNNER=ROOT/'research/continuous-recovery-20261022/network/archivecraft-dungeons01/archivecraft_dungeons01.py'
SOURCE=ROOT/'research/continuous-recovery-20261021/network/archivecraft-guides01/runtime/private/raw/attempt-03-archivecraft-bestiary-direct.body'
URL='https://archivecraft.com/townhall/bestiary/dragons-of-nightmare/'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def main():
    plan=read(HERE/'plan.json');go=read(HERE/'root-go.json')
    assert go['accepted'] and go['root_go'] and go['plan_sha256']==sha(HERE/'plan.json')
    assert go['wrapper_sha256']==sha(Path(__file__))
    assert sha(RUNNER)==plan['reviewed_runner_sha256']=='7b95fa17bff6aa5245dc9fe45331652f02db5419c0e7ac14ff454af9d0fcad00'
    assert sha(SOURCE)==plan['source_body_sha256']=='3f6dcf5aa99e1b7870bcb3d9953cc3610c4bc25c4f51103da1bb102db9e0e36e'
    assert URL in SOURCE.read_text(encoding='utf-8') and plan['target_url']==URL
    assert datetime.now(timezone.utc)<datetime.fromisoformat(go['valid_until'].replace('Z','+00:00'))
    assert shutil.disk_usage(ROOT).free>=11005853696 and not (HERE/'runtime').exists()
    spec=importlib.util.spec_from_file_location('bounded_dragons_source_runner',RUNNER)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    module.BATCH_ID='root-dragons01'
    result=module.run_core([{'target_id':'archivecraft-dragons-of-nightmare','url':URL}],module.make_paths(HERE/'runtime'),
        max_logical=1,max_attempts=2,max_seconds=120,cadence_seconds=6.2,total_cap=8*1024*1024)
    print(json.dumps({'stop_reason':result['stop_reason'],'attempts':result['attempt_count'],
       'bytes':result['total_body_bytes'],'records':[{'status':r['http_status'],'valid':r.get('valid'),'title':r.get('title')} for r in result['public_records']]}))

if __name__=='__main__':main()

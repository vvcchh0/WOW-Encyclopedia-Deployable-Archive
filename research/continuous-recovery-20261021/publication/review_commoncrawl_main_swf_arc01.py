"""Review five non-business SWF ARC investigations, without executing Flash."""
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
PACKET=ROOT/'research/continuous-recovery-20261021/network/commoncrawl-main-swf-arc01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (PACKET/'runtime').exists()
spec=importlib.util.spec_from_file_location('root_main_swf_arc01',PACKET/'commoncrawl_main_swf_arc01.py')
driver=importlib.util.module_from_spec(spec);sys.modules[spec.name]=driver;spec.loader.exec_module(driver)
with contextlib.redirect_stdout(io.StringIO()):fixture=driver._fixture()
assert fixture['all_passed'] and fixture['case_count']==27
bindings=json.loads((PACKET/'input-bindings.json').read_bytes())
for key in ['plan','runner','fixture','source_metadata','arc_parser']:
    assert bindings[key]['sha256']==sha(ROOT/bindings[key]['path'])
plan=driver.validate_plan()
source=json.loads((PUB/'commoncrawl-main-swf-candidates.json').read_bytes())
indexed={r['metadata']['url']:r for r in source['items']}
entities=plan['target']['entities'];assert len(entities)==5
for e in entities:
    r=indexed[e['url']];assert e['timestamp']==r['timestamp']
    for key in ['filename','digest','mime']:assert e[key]==r['metadata'][key]
    assert e['offset']==int(r['metadata']['offset']) and e['length']==int(r['metadata']['length'])
    assert e['timestamp'].startswith('20080509') and e['mime']=='application/x-shockwave-flash'
assert sum(e['length'] for e in entities)==448337
now=datetime.now(timezone.utc);assert now<datetime(2026,10,21,12,45,7,tzinfo=timezone.utc)
gate={'accepted':True,'root_go':True,'batch_id':plan['batch_id'],'checked_utc':now.isoformat(),
    'valid_until':(now+timedelta(minutes=10)).isoformat(),
    'plan_sha256':sha(PACKET/'plan.json'),'runner_sha256':sha(PACKET/'commoncrawl_main_swf_arc01.py'),
    'fixture_sha256':sha(PACKET/'fixture-results.json'),'input_bindings_sha256':sha(PACKET/'input-bindings.json'),
    'source_metadata_sha256':sha(PUB/'commoncrawl-main-swf-candidates.json'),'arc_parser_sha256':sha(ROOT/'tools/commoncrawl_arc.py'),
    'offline_fixture_cases':27,'scope':'Five fixed May9 non-business SWF ARC members; ARC validity and usable SWF counts separate; no Flash execution',
    'maximum_http_attempts':10,'maximum_batch_seconds':600,'parent_timeout_seconds':660,
    'maximum_response_bytes':1048576,'maximum_total_body_bytes':8388608,'maximum_inflate_bytes_per_entity':8388608,
    'minimum_start_interval_seconds':5.6,'disk_floor_bytes':11005853696,'root_review_network_requests':0,
    'wayback_resume':False,'publication_authorized_by_this_gate':False,'swf_execution':False}
out=PUB/'root-commoncrawl-main-swf-arc01-execute-go.json';assert not out.exists()
out.write_text(json.dumps(gate,indent=2)+'\n',encoding='utf-8');print(json.dumps(gate))

"""Merge immutable native observations and independently read twelve late CDX rows."""
import collections
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[3];RUN=ROOT/'research/continuous-recovery-20261018';PUB=RUN/'publication'
OUT=PUB/'root-karazhan-availability-v3.json';assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_bytes())
old=ROOT/'research/continuous-recovery-20261016/local-audit/v2/karazhan-126-item-audit-v2.json'
assert sha(old)=='fbb08f6623ade5443978279a64d3a1052aca9cedabb901b2c65130dc1ac1a5bf'
rows={}
for r in read(old)['items']:
    rows[r['target_id']]={'target_id':r['target_id'],'kind':r['kind'],'number':r['number'],
        'original':r['original_url'],'replay_url':r['request_url'],
        'outcome':'archive_replay_404' if r['global_category']=='archive_404' else 'transport_unknown',
        'evidence':old.relative_to(ROOT).as_posix()}
bindings=[{'path':old.relative_to(ROOT).as_posix(),'sha256':sha(old)}]
for name in ['root-native-replay47-v2-batch1-source-acceptance.json']+[f'root-native-replay47-v3-batch{n}-source-acceptance.json' for n in [2,3,4]]:
    p=PUB/name;a=read(p);assert a['accepted'];bindings.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
    for r in a['rows']:
        item=rows[r['target_id']];assert item['original']==r['original']
        item.update(outcome=r['classification'],checked_utc=r['checked_utc'],evidence=p.relative_to(ROOT).as_posix())
        if r['classification']=='observed_302_location':
            item['observed_late_capture_timestamp']=r['observed_redirect_capture_timestamp']
late=RUN/'integration/late-thumbnail-source-checker/accept_late_thumbnail_batch.py'
assert sha(late)=='36b6c352a29cae5e3b1b028eee152511448438f976dbbacf36d693c792a438e5'
spec=importlib.util.spec_from_file_location('late_index_summary_reader',late)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
cdx_rows=[]
for n in [1,2]:
    p=PUB/f'root-late-thumbnails12-batch{n}-source-acceptance.json';assert read(p)['accepted']
    bindings.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
    directory=RUN/f'network/late-thumbnails12-v1/batch-{n:02d}';plan=read(directory/'plan.json')
    state=read(directory/'output/state.json');by_key={c['target_key']:c for c in plan['candidates']}
    for a in state['attempts']:
        if not a.get('sent') or not a['label'].endswith(':cdx') or a['source_status']!=200:continue
        assert a['curl_exit']==0
        key=a['label'][:-4];c=by_key[key];body=ROOT/a['body_path']
        assert sha(body)==a['raw_body_sha256'] and body.stat().st_size==a['body_bytes']
        query=parse_qs(urlsplit(a['url']).query)
        assert query['url']==[c['original']] and query['matchType']==['exact']
        assert query['from']==['20130612000000'] and query['to']==['20130612235959']
        exact=module.records(body.read_bytes(),500);assert len(exact)==1
        record=exact[0]
        assert module.identity(record['original'])==module.identity(c['original'])
        assert record['statuscode']=='301' and record['mimetype']=='text/html'
        item=next(r for r in rows.values() if r['original']==c['original'])
        assert item['kind']=='thumb' and item['outcome']=='observed_302_location'
        item.update(outcome='observed_late_redirect_with_cdx_301_html',late_index_evidence=p.relative_to(ROOT).as_posix())
        cdx_rows.append({'original':c['original'],'capture_timestamp':record['timestamp'],
            'statuscode':'301','mimetype':'text/html','cdx_digest':record['digest'],
            'index_complete':True,'image_payload_accepted':False})
assert len(cdx_rows)==12 and len(rows)==126
counts={kind:dict(collections.Counter(r['outcome'] for r in rows.values() if r['kind']==kind)) for kind in ['full','thumb']}
assert counts=={'full':{'archive_replay_404':63},'thumb':{'archive_replay_404':51,'observed_late_redirect_with_cdx_301_html':12}}
report={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'target_count':126,
    'counts_by_kind':counts,'image_payloads_obtained':0,'transport_unknown_remaining':0,
    'bindings':bindings,'late_cdx_rows':cdx_rows,'rows':sorted(rows.values(),key=lambda r:(r['kind'],r['number'])),
    'scope':'Original63 full-size and63 thumbnail URLs derived from captured gallery JavaScript. This records observed replay and exact2013day index outcomes, not a claim about every historical capture point.',
    'network_requests_during_summary':0}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
status_path=RUN/'status.json';status=read(status_path)
status.update(latest_network_batch='NET40',phase='navigation_image_acquisition_preparation',
    native_karazhan_availability_summary=OUT.relative_to(RUN).as_posix(),
    native_late2013_exact_indices_checked=12,native_late2013_captured_301_html=12,
    updated_utc=datetime.now(timezone.utc).isoformat())
status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'counts':counts,'sha256':sha(OUT)}))

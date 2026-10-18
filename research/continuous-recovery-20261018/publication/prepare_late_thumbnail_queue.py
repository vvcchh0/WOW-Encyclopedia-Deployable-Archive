"""Freeze only the twelve same-resource 2013 redirects actually observed."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];RUN=ROOT/'research/continuous-recovery-20261018';PUB=RUN/'publication'
OUT=PUB/'native-observed-late-thumbnails12-queue.json';URLS=PUB/'native-observed-late-thumbnails12-originals.txt'
assert not OUT.exists() and not URLS.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];bindings=[]
for batch in [2,3,4]:
    p=PUB/f'root-native-replay47-v3-batch{batch}-source-acceptance.json';a=json.loads(p.read_bytes());assert a['accepted']
    bindings.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
    for r in a['rows']:
        if r['classification']!='observed_302_location':continue
        assert r['target_id'].startswith('thumb-') and r['observed_redirect_capture_timestamp'].startswith('20130612')
        assert r['observed_redirect_url']=='https://web.archive.org/web/'+r['observed_redirect_capture_timestamp']+'id_/'+r['original']
        assert re.fullmatch(r'http://www\.worldofwarcraft\.com/info/dungeons/images/karazhan/ss(?:[1-9]|1[0-2])-thumb\.jpg',r['original'])
        rows.append({'original':r['original'],'target_id':r['target_id'],
            'observed_capture_timestamp':r['observed_redirect_capture_timestamp'],
            'observed_replay_url':r['observed_redirect_url'],
            'observed_source_receipt':p.relative_to(ROOT).as_posix(),'observed_source_receipt_sha256':sha(p),
            'source_capture_class':'late2013_native_thumbnail_supplement'})
assert len(rows)==12 and len({r['original'] for r in rows})==12
rows.sort(key=lambda r:int(re.search(r'/ss(\d+)-thumb',r['original'])[1]))
URLS.write_text(''.join(r['original']+'\n' for r in rows),encoding='utf-8',newline='\n')
for n,r in enumerate(rows,1):
    r['rank']=n;r['source_evidence']={'path':URLS.relative_to(ROOT).as_posix(),'sha256':sha(URLS),'line':n,'literal':r['original']}
out={'accepted':True,'prepared_utc':datetime.now(timezone.utc).isoformat(),'network_requests':0,
    'scope':'Twelve literal same-original thumbnail redirects observed in native replay; investigate exact CDX only within2013-06-12, then validate actual image payload if eligible. Later-source supplements remain separate from the2008baseline.',
    'candidate_count':12,'from':'20130612000000','to':'20130612235959','source_receipt_bindings':bindings,
    'url_list':{'path':URLS.relative_to(ROOT).as_posix(),'sha256':sha(URLS)},'rows':rows}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'sha256':sha(OUT),'url_list_sha256':sha(URLS),'rows':12}))

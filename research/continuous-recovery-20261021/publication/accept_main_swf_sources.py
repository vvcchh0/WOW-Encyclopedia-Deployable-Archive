"""Independently separate acquired ARC bodies from structurally complete SWFs."""
import hashlib
import json
import re
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[3];PUB=Path(__file__).resolve().parent
PACKET=ROOT/'research/continuous-recovery-20261021/network/commoncrawl-main-swf-arc01'
sys.path.insert(0,str(ROOT/'tools'))
from commoncrawl_arc import parse_arc_gzip_member
read=lambda p:json.loads(p.read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest()
report_path=PACKET/'runtime/swf-report.json';report=read(report_path);plan=read(PACKET/'plan.json')
assert report['acquired_arc_count']==5 and report['usable_swf_count']==3 and report['error'] is None
assert report['network_attempts']==5 and report['transport_failures']==0
rows=[]
for selected,item in zip(plan['target']['entities'],report['entities'],strict=True):
    compressed=(ROOT/item['private_entity_path']).read_bytes()
    assert len(compressed)==selected['length']
    record=parse_arc_gzip_member(compressed,expected_url=selected['url'],expected_timestamp=selected['timestamp'],
        expected_status=200,expected_digest=selected['digest'],max_decompressed_bytes=8388608)
    payload=record.http.payload;assert payload[:3]==b'CWS' and len(payload)>=8
    declared=int.from_bytes(payload[4:8],'little')
    decoder=zlib.decompressobj();decoded=decoder.decompress(payload[8:],8388609)
    assert len(decoded)<=8388608 and not decoder.unconsumed_tail
    actual_length=8+len(decoded)
    values=[int(v) for v in record.http.values('content-length')]
    assert len(values)==1
    complete=decoder.eof and not decoder.unused_data and actual_length==declared and values[0]==len(payload)
    route=re.sub('/+','/',urlsplit(selected['url']).path)
    old=ROOT/'.scratch/pages-resources-20261021-v41'/route.lstrip('/')
    row={'entity_id':selected['entity_id'],'original_url':selected['url'],'route':route,
        'actual_capture_timestamp':record.timestamp,'payload_sha256':sha(payload),'payload_sha1_base32':record.payload_sha1_base32,
        'payload_bytes':len(payload),'stored_content_length':values[0],
        'cws_eof':decoder.eof,'cws_unused_bytes':len(decoder.unused_data),'declared_uncompressed_length':declared,
        'observed_uncompressed_length':actual_length,'structurally_complete':complete,'playable_accepted':False,
        'present_in_v41':old.is_file(),'identical_to_v41':old.is_file() and old.read_bytes()==payload,
        'source_arc':{'filename':selected['filename'],'offset':selected['offset'],'length':selected['length'],'compressed_sha256':sha(compressed)}}
    assert complete==bool(report['per_target_swf_status'][selected['entity_id']]['usable_swf'])
    rows.append(row)
assert [r['structurally_complete'] for r in rows]==[False,False,True,True,True]
out=PUB/'root-main-swf-source-acceptance.json';assert not out.exists()
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'scope':'Five exact acquired ARC bodies and offline SWF structure only; no ActionScript or player execution',
    'rows':rows,'acquired_arc_count':5,'structurally_complete_count':3,'truncated_count':2,
    'complete_payloads_already_identical_in_v41':sum(r['structurally_complete'] and r['identical_to_v41'] for r in rows),
    'new_playable_exhibits':0,'swf_execution':False,'root_review_network_requests':0,'source_report_sha256':sha(report_path.read_bytes()),
    'next_step':'Retain two truncated captures as evidence; compare complete duplicates before considering any new compatibility work.'}
out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))

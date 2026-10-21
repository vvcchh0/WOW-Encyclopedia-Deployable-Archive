"""Accept the five acquired XML/XHTML payloads as source content, offline."""
import hashlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
PACKET=ROOT/'research/continuous-recovery-20261021/network/commoncrawl-blizzcast-arc01'
sys.path.insert(0,str(ROOT/'tools'))
from commoncrawl_arc import parse_arc_gzip_member
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_bytes())
report_path=PACKET/'runtime/arc-report.json';report=read(report_path);plan=read(PACKET/'plan.json')
assert report['accepted_all_entities'] and report['stop_reason']=='all_entities_accepted' and report['error'] is None
assert report['network_attempts']==5 and report['transport_failures']==0
assert shutil.disk_usage(ROOT).free>=11005853696
rows=[]
for entity,item in zip(plan['target']['entities'],report['entities'],strict=True):
    assert item['accepted'] and item['entity_id']==entity['entity_id']
    path=ROOT/item['private_entity_path'];compressed=path.read_bytes()
    assert len(compressed)==entity['length']
    record=parse_arc_gzip_member(compressed,expected_url=entity['url'],expected_timestamp=entity['timestamp'],
        expected_status=200,expected_digest=entity['digest'],max_decompressed_bytes=8388608)
    payload=record.http.payload
    assert len(payload)<=131072 and b'<!ENTITY' not in payload
    doc=ET.fromstring(payload)
    http_lengths=[int(v) for v in record.http.values('content-length')]
    assert not http_lengths or all(v==len(payload) for v in http_lengths)
    payload_path=ROOT/'research/continuous-recovery-20261021/integration/blizzcast-review/private'/f"{entity['entity_id']}.xml"
    assert payload_path.read_bytes()==payload
    title=next((''.join(e.itertext()).strip() for e in doc.iter() if e.tag.split('}')[-1]=='title'),'')
    blocks=[e for e in doc.iter() if e.get('class','').split()[:1]==['trans']]
    rows.append({'entity_id':entity['entity_id'],'original_url':record.url,'actual_capture_timestamp':record.timestamp,
        'temporal_relation':entity['temporal_relation'],'mime':record.mime,'payload_path':payload_path.relative_to(ROOT).as_posix(),
        'sha256':sha(payload),'length':len(payload),'sha1_base32':record.payload_sha1_base32,
        'title':title,'xml_root':doc.tag,'xml_nodes':sum(1 for _ in doc.iter()),'transcript_blocks':len(blocks),
        'rss_items':sum(1 for e in doc.iter() if e.tag=='item'),
        'source_arc':{'filename':entity['filename'],'offset':entity['offset'],'length':entity['length'],'compressed_sha256':sha(compressed)},
        'stored_content_length_present':bool(http_lengths),'xml_well_formed':True})
assert [r['transcript_blocks'] for r in rows]==[0,19,31,0,0]
assert rows[0]['rss_items']==2
out=PUB/'root-blizzcast-source-acceptance.json';assert not out.exists()
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
    'scope':'Five actual BlizzCast source payloads; reader rendering and dependencies remain pending',
    'entities':rows,'accepted_original_html_entities':4,'accepted_rss_entities':1,
    'actual_transcript_blocks':50,'new_images':0,'published':False,'reader_browser_accepted':False,
    'root_review_network_requests':0,'source_report_sha256':sha(report_path.read_bytes()),
    'privacy':'Stored HTTP headers, cookies and ARC framing remain private; reader may use sanitized content only.'}
out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
folder=ROOT/'research/continuous-recovery-20261021/integration/blizzcast-reader';folder.mkdir(parents=True,exist_ok=True)
input_path=folder/'input-source-map.json';assert not input_path.exists()
input_path.write_text(json.dumps({'schema':'wow-blizzcast-reader-input/v1','accepted':True,
    'source_acceptance':out.relative_to(ROOT).as_posix(),'source_acceptance_sha256':sha(out.read_bytes()),'records':rows},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'html_entities':4,'rss_entities':1,'transcript_blocks':50,'reader_ready':False,'input_map':input_path.relative_to(ROOT).as_posix()}))

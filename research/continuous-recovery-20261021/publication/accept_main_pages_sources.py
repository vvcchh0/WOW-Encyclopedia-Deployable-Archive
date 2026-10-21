"""Independently accept nine source entities; distinguish additions and aliases."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[3];PUB=Path(__file__).resolve().parent
REVIEW=ROOT/'research/continuous-recovery-20261021/integration/main-pages-review'
OUT=PUB/'root-main-pages-source-acceptance.json'
assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
sys.path.insert(0,str(ROOT/'tools'))
from commoncrawl_arc import parse_arc_gzip_member
assert sha(ROOT/'tools/commoncrawl_arc.py')=='50be2eb8c749da7aecfc58d06622eb30211e98399e17fbfdc94bedf6aefc7e6c'
batch=ROOT/'research/continuous-recovery-20261021/network/commoncrawl-main-pages01'
plan=read(batch/'plan.json');report=read(batch/'runtime/arc-report.json')
proposed={
 'contest-050609':('/contests/05-06-09/index.html','add','life-size mannequin'),
 'content-index-shtml':('/info/basics/content-index.html','update','Content Index'),
 'tinfoilhat':('/info/items/tinfoilhat.xml','add','mind spies'),
 'two-headed-ogre':('/info/races/two-headed-ogre.shtml','add','Inter-Ogre Communication'),
 'fan-site-program':('/misc/fan-site-program.html','add','official fan site program'),
 'moltencore':('/moltencore/index.html','add','Atari 2600'),
 'patch-092904':('/patchnotes/patch-9-29-04.shtml','add','Warlock Talents Added'),
 'bardclass':('/wrath/features/bard/bardclass.xml','add','Fret Bar'),
 'wrath-index-xml':('/wrath/index.html','alias_only','Lich King'),
}
class Text(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.skip=0;self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag in {'script','style'}:self.skip+=1
 def handle_endtag(self,tag):
  if tag in {'script','style'}:self.skip=max(0,self.skip-1)
 def handle_data(self,data):
  if not self.skip:self.parts.append(data)
entities={r['entity_id']:r for r in report['entities']};reviewed=read(REVIEW/'page-content-review.json')
by_id={r['entity_id']:r for r in reviewed['entities']};rows=[]
for target in plan['target']['entities']:
 item=entities[target['entity_id']];attempt=item['attempts'][-1]
 body=(ROOT/attempt['body_path']).read_bytes()
 assert len(body)==target['length'] and hashlib.sha256(body).hexdigest()==attempt['body_sha256']
 record=parse_arc_gzip_member(body,expected_url=target['url'],expected_timestamp=target['timestamp'],
     expected_status=200,expected_digest=target['digest'],max_decompressed_bytes=8*1024*1024)
 review=by_id[target['entity_id']];payload=record.http.payload
 assert (ROOT/review['payload_path']).read_bytes()==payload and len(payload)==review['length']
 assert hashlib.sha256(payload).hexdigest()==review['sha256']
 route,mode,phrase=proposed[target['entity_id']]
 parsed=Text();parsed.feed(payload.decode(review['encoding']))
 text=' '.join(' '.join(parsed.parts).split())
 assert phrase.casefold() in text.casefold(),target['entity_id']
 assert not re.search(r'(?i)page not found|the page you requested could not be found|access denied',text)
 assert record.timestamp<='20080512210044'
 if mode=='alias_only':assert review['possible_local_aliases'][0]['new_payload_equals_old_original'] is True
 public={k:review[k] for k in ('entity_id','original_url','actual_capture_timestamp','mime','length','sha256','sha1_base32','encoding','source_arc')}
 public.update({'title':next(x[1] for x in review['headings'] if x[0]=='title'),'proposed_route':route,'proposed_use':mode,
     'body_content_reviewed':True,'stored_http_status':record.http.status,
     'transient_session_suffix_occurrences':len(re.findall(br';jsessionid=[A-Za-z0-9_.-]+',payload,re.I)),
     'business_context_required':target['entity_id'] in {'contest-050609','fan-site-program'},
     'private_payload_path':review['payload_path']})
 rows.append(public)
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'source_entities':9,
    'proposed_new_pages':7,'proposed_updated_existing_pages':1,'proposed_alias_only':1,
    'scope':'Exact original bodies and meaningful article text reviewed. Pages integration/browser still pending.',
    'entities':rows,'parser_sha256':sha(ROOT/'tools/commoncrawl_arc.py'),
    'frozen_source15_manifest_sha256':sha(ROOT/'.scratch/offline-navigation-20261015-v15/build-manifest.json'),
    'raw_http_private':True,'payloads_private':True,'body_transient_identifiers_must_be_removed_before_public_derivation':True,
    'browser_accepted':False,'published':False,'network_requests':0}
OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source_map={'schema':'wow-main-page-source16-input/v1','accepted':True,'source_acceptance':OUT.relative_to(ROOT).as_posix(),
    'source_acceptance_sha256':sha(OUT),'records':rows,
    'aliases':{'/contests/05-06-09':'/contests/05-06-09/index.html','/contests/05-06-09/':'/contests/05-06-09/index.html',
               '/info/basics/content-index.shtml':'/info/basics/content-index.html','/moltencore':'/moltencore/index.html',
               '/moltencore/':'/moltencore/index.html','/wrath/index.xml':'/wrath/index.html'}}
target=REVIEW/'source16-input-map.json';assert not target.exists();target.write_text(json.dumps(source_map,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'original_sources':9,'new_pages':7,'updated':1,'alias_only':1,'private_session_identifiers':sum(x['transient_session_suffix_occurrences'] for x in rows)}))

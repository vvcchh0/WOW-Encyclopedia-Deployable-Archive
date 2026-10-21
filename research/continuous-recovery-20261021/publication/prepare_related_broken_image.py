"""Root source acceptance and one related-guide illustration decision."""
import hashlib
import io
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
BASE=ROOT/'research/continuous-recovery-20261021/network/archivecraft-broken-image01'
DEST=ROOT/'research/continuous-recovery-20261021/integration/related-guide-images'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
accept=PUB/'root-archivecraft-broken-image-source-acceptance.json'
decision=PUB/'root-related-guide-image-decision.json'
mapping=DEST/'input-map.json'
assert not any(p.exists() for p in (accept,decision,mapping))
inv=read(BASE/'runtime/public-inventory.json'); private=read(BASE/'runtime/private/report.json')
assert private['stop_reason']=='completed' and private['attempt_count']==1
row=inv['records'][0]; attempt=private['attempts'][0]
assert row['url']=='https://archivecraft.com/wp-content/uploads/images/index/townhall/burning-crusade/bestiary/thumb-thebroken.jpg'
assert row['valid'] and attempt['http_status']==200 and attempt['returncode']==0
assert attempt['transport']=='direct' and not attempt['timed_out']
raw=Path(attempt['_body_file']); payload=BASE/'review/thebroken.jpg'
assert raw.read_bytes()==payload.read_bytes() and len(payload.read_bytes())==17152
assert sha(payload)==row['body_sha256']=='07f86855600ec20dbd9712ad654df2aaafd5c4b48a3355582f8d5d216dadd1b9'
with Image.open(io.BytesIO(payload.read_bytes())) as img:
    assert img.format=='JPEG' and img.size==(237,184) and getattr(img,'n_frames',1)==1
    img.load()
manifest_path=ROOT/'.scratch/offline-non-gallery-20261021-v16/build-manifest.json'
assert sha(manifest_path)=='e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
manifest=read(manifest_path)
target='/burningcrusade/townhall/images/bestiary/thumb-thebroken.jpg'
class Missing(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.targets=[]
    def handle_starttag(self,tag,attrs):
        if tag=='img':
            src=dict(attrs).get('src','')
            if '/__offline/missing-image.svg' in src:
                self.targets.extend(parse_qs(urlsplit(src).query).get('requested',[]))
matches=[]
for source in manifest['files']:
    if source['kind'] not in ('html','xml','markup') and not source['route'].endswith(('.xml','.html')):continue
    path=ROOT/source['output_path']
    if b'thumb-thebroken.jpg' not in path.read_bytes():continue
    p=Missing();p.feed(path.read_text(encoding='utf-8'))
    if any(urlsplit(u).path==target for u in p.targets):matches.append(source['route'])
assert matches==['/burningcrusade/townhall/bestiary.html'],matches
assert not (ROOT/'.scratch/offline-non-gallery-20261021-v16/site'/target.lstrip('/')).exists()
entry={'title':'The Broken','page_route':matches[0],'target_route':target,'route':'/__offline/related-guide-images/thumb-thebroken.jpg','source_image_url':row['url'],'source_page_url':'https://archivecraft.com/burningcrusade/townhall/bestiary/','current_observed_utc':row['current_observed_utc'],'sha256':sha(payload),'length':17152,'format':'JPEG','width':237,'height':184,'frames':1,'classification':'current_related_archive_source','original_capture_timestamp':None,'source_processing_note':'Processing before retrieval is unknown.','payload_path':payload.relative_to(ROOT).as_posix()}
public={k:v for k,v in entry.items() if k!='payload_path'}
accept.write_text(json.dumps({'schema':'wow-root-archivecraft-guide-image-source-acceptance/v1','accepted_sources':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'records':[public],'source_images':1,'historical_original_images_recovered':0,'raw_http_private':True,'images_reencoded':False,'root_visual_review':'Broken draenei character with purple crystal staff, framed thumbnail; no error or placeholder image.','bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (BASE/'runtime/public-inventory.json',BASE/'local-image-review.json',BASE/'parent-execution-receipt.json',BASE/'source-selection.json')]},indent=2)+'\n',encoding='utf-8')
decision.write_text(json.dumps({'schema':'wow-related-guide-image-decision/v1','accepted_for_browser_supplement':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'classification':'current_related_archive_source','original_2008_images_recovered':0,'source_acceptance':accept.relative_to(ROOT).as_posix(),'source_acceptance_sha256':sha(accept),'targets':[public],'decision':'Display the exact The Broken thumbnail referenced by ArchiveCraft Burning Crusade Bestiary at the existing same-topic missing target. Keep original article text; add a visible source-page link.','excluded':'No other current guide images, HTML, comments, scripts, audio or forms.','bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (accept,manifest_path)]},indent=2)+'\n',encoding='utf-8')
DEST.mkdir(exist_ok=True)
mapping.write_text(json.dumps({'schema':'wow-related-guide-image-map/v1','decision':decision.relative_to(ROOT).as_posix(),'decision_sha256':sha(decision),'source_acceptance':accept.relative_to(ROOT).as_posix(),'source_acceptance_sha256':sha(accept),'source_label':'ArchiveCraft community archive','source_manifest_sha256':sha(manifest_path),'entries':[entry]},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'map_sha256':sha(mapping),'decision_sha256':sha(decision),'source_acceptance_sha256':sha(accept),'active_page':matches[0]}))

"""Independently accept current archive images and bind three article supplements."""
import hashlib
import io
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
BASE = ROOT/'research/continuous-recovery-20261021/network/archivecraft-images01'
DEST = ROOT/'research/continuous-recovery-20261021/integration/related-encyclopedia-images'
ACCEPT = PUB/'root-archivecraft-images-source-acceptance.json'
DECISION = PUB/'root-related-encyclopedia-image-decision.json'
MAP = DEST/'input-map.json'
assert not ACCEPT.exists() and not DECISION.exists() and not MAP.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
review_path = BASE/'local-image-review.json'
review = read(review_path)
inventory_path = BASE/'runtime/public-inventory.json'
inventory = read(inventory_path)
private = read(BASE/'runtime/private/report.json')
correlation_path = BASE/'target-correlation.json'
correlation = read(correlation_path)
manifest_path = ROOT/'.scratch/offline-non-gallery-20261021-v16/build-manifest.json'
manifest = read(manifest_path)
assert sha(manifest_path) == 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
assert private['stop_reason'] == 'completed' and private['attempt_count'] == 4
assert private['total_body_bytes'] == 164504
images = {}
for public, attempt, local in zip(inventory['records'], private['attempts'], review['records']):
    assert public['url'] == attempt['url'] == local['url']
    assert public['valid'] and attempt['http_status'] == 200 and attempt['returncode'] == 0
    assert attempt['transport'] == 'direct' and not attempt['timed_out']
    body = Path(attempt['_body_file']).read_bytes()
    copy = ROOT/local['review_path']
    assert body == copy.read_bytes() and len(body) == public['body_bytes']
    assert hashlib.sha256(body).hexdigest() == public['body_sha256'] == local['review_sha256']
    with Image.open(io.BytesIO(body)) as image:
        assert image.format == 'JPEG' and getattr(image,'n_frames',1) == 1
        image.load()
        assert list(image.size) == [public['width'],public['height']]
    images[public['url']] = dict(public, payload_path=local['review_path'])
control = next(r for r in images.values() if r['role'] == 'stored_image_control')
control_path = ROOT/'offline/site/info/encyclopedia/images/featured/highelvesandbloodelves.jpg'
assert sha(control_path) == control['body_sha256'] == '1621e44272c23e925a7adbdd1ec1c23a97ff1dd832877062f7082c64be5a7ae8'
assert (ROOT/control['payload_path']).read_bytes() == control_path.read_bytes()
accepted_sources = [{k:v for k,v in r.items() if k != 'payload_path'} for r in images.values()]
ACCEPT.write_text(json.dumps({'schema':'wow-root-archivecraft-image-source-acceptance/v1','accepted_sources':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'records':accepted_sources,'source_images':4,'new_related_image_candidates':3,'control_bytes_identical':True,'raw_http_private':True,'images_reencoded':False,'historical_original_images_recovered':0,'root_visual_review':['alleria-image.jpg','cenarion-image.jpg','malfurion-image.jpg'],'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (inventory_path,review_path,BASE/'parent-execution-receipt.json',PUB/'root-archivecraft-pages-source-acceptance.json')]},indent=2)+'\n',encoding='utf-8')
class Images(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.sources=[]
    def handle_starttag(self,tag,attrs):
        if tag=='img': self.sources.append(dict(attrs).get('src',''))
rows = {r['route']:r for r in manifest['files']}
entries=[]
for target in correlation['targets']:
    old, current = target['source16'], target['current_related_source']
    source = images[current['image_url']]
    page_route = urlsplit(old['logical_xml_url']).path
    row = rows[page_route]
    page = ROOT/row['output_path']
    parser=Images();parser.feed(page.read_text(encoding='utf-8'))
    requested = [parse_qs(urlsplit(s).query).get('requested',[None])[0] for s in parser.sources if '/__offline/missing-image.svg' in s]
    assert requested.count(old['requested_image_url']) == 1
    target_route=urlsplit(old['requested_image_url']).path
    assert not (ROOT/'.scratch/offline-non-gallery-20261021-v16/site'/target_route.lstrip('/')).exists()
    entries.append({'title':old['article_title'],'page_route':page_route,'target_route':target_route,'route':'/__offline/related-encyclopedia-images/'+Path(target_route).name,'source_image_url':source['url'],'source_page_url':current['source_page_url'],'current_observed_utc':source['current_observed_utc'],'sha256':source['body_sha256'],'length':source['body_bytes'],'format':'JPEG','width':source['width'],'height':source['height'],'frames':1,'classification':'current_related_archive_source','original_capture_timestamp':None,'source_processing_note':'ArchiveCraft WordPress resized filename (-300x353).' if target['target_id']=='alleria-windrunner' else 'Processing before retrieval is unknown.','payload_path':source['payload_path']})
assert len(entries)==3 and sum(r['length'] for r in entries)==159173
public=[{k:v for k,v in r.items() if k!='payload_path'} for r in entries]
decision={'schema':'wow-related-encyclopedia-image-decision/v1','accepted_for_browser_supplement':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'classification':'current_related_archive_source','original_2008_images_recovered':0,'source_acceptance':ACCEPT.relative_to(ROOT).as_posix(),'source_acceptance_sha256':sha(ACCEPT),'targets':public,'decision':'Three exact image references on matching ArchiveCraft articles supplement the three existing encyclopedia article gaps. Preserve current JPEG bytes and identify the community archive in a local source note. Keep 2008 article text unchanged.','root_visual_basis':'Alleria archer line drawing, Tauren druid for Cenarion Circle, Malfurion portrait; no missing icon or unrelated picture.','control_basis':'ArchiveCraft featured high-elf control matches the already preserved entity bytes; it does not supply missing capture dates for the other three.','excluded':'Control image is not duplicated; no ArchiveCraft text, comments, scripts or business forms imported.','bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (ACCEPT,correlation_path,manifest_path)]}
DECISION.write_text(json.dumps(decision,indent=2)+'\n',encoding='utf-8')
DEST.mkdir(exist_ok=True)
MAP.write_text(json.dumps({'schema':'wow-related-encyclopedia-image-map/v1','decision':DECISION.relative_to(ROOT).as_posix(),'decision_sha256':sha(DECISION),'source_acceptance':ACCEPT.relative_to(ROOT).as_posix(),'source_acceptance_sha256':sha(ACCEPT),'source_label':'ArchiveCraft community archive','source_manifest_sha256':sha(manifest_path),'entries':entries},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted_sources':4,'accepted_supplements':3,'bytes':159173,'source_acceptance_sha256':sha(ACCEPT),'decision_sha256':sha(DECISION),'map_sha256':sha(MAP)}))

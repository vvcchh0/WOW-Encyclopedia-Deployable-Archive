"""Prepare the root-selected native-size connector subset without reencoding."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=HERE/'integration/related-talent-ui-v54'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,x:p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode())
assert not OUT.exists() and shutil.disk_usage(ROOT).free>=11005853696
audit_path=HERE/'talent-arrow-review/audit.json'
prototype_path=HERE/'talent-arrow-prototype/prototype-receipt.json'
audit=read(audit_path);prototype=read(prototype_path)
assert prototype['accepted_as_prototype'] and prototype['temporary_prototype'] and not prototype['production_export']
assert not prototype['external_requests'] and not prototype['page_errors']
oldmap_path=ROOT/'research/continuous-recovery-20261021/integration/related-talent-ui/input-map.json'
olddecision_path=ROOT/'research/continuous-recovery-20261021/publication/root-related-talent-ui-integration-decision.json'
old=read(oldmap_path);olddecision=read(olddecision_path)
assert len(old['entries'])==6
OUT.mkdir(parents=True)
entries=[]
for oldentry in old['entries']:
 entry=dict(oldentry);source=ROOT/entry['payload_path'];dest=OUT/'assets'/Path(entry['repository_path']).name
 dest.parent.mkdir(parents=True,exist_ok=True);assert sha(source)==entry['sha256']
 assert shutil.disk_usage(ROOT).free>=11005853696;dest.write_bytes(source.read_bytes())
 entry['payload_path']=dest.relative_to(ROOT).as_posix();entries.append(entry)
selected=[];held=[]
for asset in audit['assets']:
 if asset['filename'].startswith('down-3-'):
  held.append({'target_route':asset['route'],'reason':'The later 137-pixel arrow stops visibly 13 pixels before the 2008 target icon. Retain the source but hold this geometry from display.'});continue
 source=ROOT/asset['source_file'];data=source.read_bytes()
 assert len(data)==asset['source_file_bytes'] and sha(source)==asset['sha256']
 blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==asset['git_blob_sha1']
 with Image.open(io.BytesIO(data)) as im:
  assert im.format=='GIF' and list(im.size)==asset['dimensions'] and getattr(im,'n_frames',1)==1
  im.load();im.convert('RGBA').tobytes()
 dest=OUT/'assets/arrows'/asset['filename'];dest.parent.mkdir(parents=True,exist_ok=True)
 assert shutil.disk_usage(ROOT).free>=11005853696;dest.write_bytes(data)
 entry={'target_route':asset['route'],'route':'/__offline/related-talent-ui/arrows/'+asset['filename'],
  'repository_path':asset['route'].lstrip('/'),'sha256':asset['sha256'],'length':len(data),'git_blob_sha1':blob,
  'format':'GIF','width':asset['dimensions'][0],'height':asset['dimensions'][1],'frames':1,
  'classification':'later_related_source','original_capture_timestamp':None,'payload_path':dest.relative_to(ROOT).as_posix()}
 entries.append(entry);selected.append(entry)
assert len(selected)==18 and len(held)==3 and len(entries)==24
decision={'schema':'wow-related-talent-ui-integration-decision/v2','accepted_for_browser_supplement':True,
 'checked_utc':datetime.now(timezone.utc).isoformat(),'source_acceptance':old['source_acceptance'],
 'source_acceptance_sha256':old['source_acceptance_sha256'],'source':old['source'],
 'accepted_ui_count':24,'accepted_source_bytes':sum(e['length'] for e in entries),
 'classification':'later_related_source','original_capture_timestamp':None,'original_2008_images_recovered':0,
 'targets':[{k:v for k,v in e.items() if k!='payload_path'} for e in entries],
 'retained_ui_count':6,'new_cached_arrow_assets':18,'new_downloaded_images':0,
 'supersedes_arrow_exclusion_only':{'path':olddecision_path.relative_to(ROOT).as_posix(),'sha256':sha(olddecision_path)},
 'compatibility_audit':{'path':audit_path.relative_to(ROOT).as_posix(),'sha256':sha(audit_path)},
 'prototype':{'path':prototype_path.relative_to(ROOT).as_posix(),'sha256':sha(prototype_path),'production_acceptance':False},
 'root_visual_selection':{'reviewed_screenshots':['down-2-yellow.png','down-3-yellow.png','down-4-yellow.png','across-left-yellow.png','down-right-yellow.png'],
  'accepted_geometries':['across-left','across-right','down-1','down-2','down-4','down-right'],
  'reason':'The selected native-size connectors indicate the correct prerequisite and target. Small edge gaps/overlap are readable and consistent with the preserved icon frames; no layout or image resizing is applied.',
  'held':held,'original_prerequisite_logic_changed':False},
 'excluded':'Three down-3 states, all tree backgrounds, clipped class headings, repository scripts and talent data.',
 'production_export_and_browser_acceptance_required':True,
}
decision_path=OUT/'decision.json';write(decision_path,decision)
mapping={'schema':'wow-related-talent-ui-map/v2','decision':decision_path.relative_to(ROOT).as_posix(),
 'decision_sha256':sha(decision_path),'source_acceptance':old['source_acceptance'],
 'source_acceptance_sha256':old['source_acceptance_sha256'],'source':old['source'],'ui_count':24,'entries':entries}
map_path=OUT/'input-map.json';write(map_path,mapping)
pins={'map_sha256':sha(map_path),'decision_sha256':sha(decision_path),'source_acceptance_sha256':old['source_acceptance_sha256'],
 'map_schema':mapping['schema'],'ui_count':24,'source_bytes':sum(e['length'] for e in entries),'new_arrow_count':18,'held_arrow_count':3}
write(OUT/'root-input-pins.json',pins)
print(json.dumps(pins))

"""Root source and same-canonical-title review of eighteen cached icon bytes."""
from datetime import datetime,timezone
import hashlib,html,io,json,zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
OUT=HERE/'integration/related-talent-icons-v56'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
write=lambda p,d:p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
draft=OUT/'input-map.json';assert sha(draft)=='c2de1eae90b0d189a7f54091770bdc3bceda48c42f516a8fce0da8ed8433572d'
prep_path=OUT/'source-preparation.json';assert sha(prep_path)=='b5ebf6066d084f6dcda06cc78e4bc4e39114e1e0cfd3e29fb4c8ab38ad38826d'
audit_path=HERE/'talent-icon-remaining-audit/audit.json';assert sha(audit_path)=='16629cb29bfc945a2843b9ee5dbbaf5765c28bfc2ce4afb0715992d922a571f3'
data=read(draft);prep=read(prep_path);audit=read(audit_path)
selected={'mage-molten-shields','paladin-guardian-s-favor','rogue-puncturing-wounds','rogue-dirty-tricks','shaman-earth-s-grasp','warrior-death-wish','warrior-improved-disciplines','warrior-improved-thunder-clap','warrior-improved-slam'}
assert set(prep['candidate_ids'])==selected and {e['mapping_id'] for e in data['entries']}==selected
assert len(data['entries'])==18
by_id={r['candidate_id']:r for r in audit['new_same_class_candidates']}
zip_path=ROOT/data['source']['zip_path'];assert sha(zip_path)=='52cd20ed7509943d5a386c95888686f8ea043c051cb367d8efe779b2a191095f'
site=ROOT/'.scratch/pages-resources-20261022-v55';routes=read(site/'__offline/route-map.json')
payloads=[];total=0
with zipfile.ZipFile(zip_path) as archive:
 for e in data['entries']:
  candidate=by_id[e['mapping_id']];old=candidate['old_2008_target'];later=candidate['later_same_class_candidate']
  assert candidate['finding_type'] in ('exact_same_class_title','exact_same_class_title_moved_tree')
  assert old['canonical_talent_title']==later['canonical_talent_title']==e['talent']
  assert candidate['class']==e['class'] and e['route'] in old['routes']
  assert e['repository_path'].startswith('shared/global/talents/'+e['class']+'/images/')
  image=next(x for x in later['images'] if x['state']==e['state'])
  assert e['repository_path']==image['repository_path'] and not image['repository_path_present_in_base_986_map']
  assert not (site/e['route'].lstrip('/')).exists() and e['route'] not in routes['routes'] and e['route'] not in routes['aliases']
  raw=archive.read(image['zip_member']);cached=(ROOT/e['payload_path']).read_bytes()
  assert raw==cached and len(raw)==e['length']==image['length']
  assert hashlib.sha256(raw).hexdigest()==e['sha256']==image['sha256']
  assert hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()==e['git_blob_sha1']==image['git_blob_sha1']
  with Image.open(io.BytesIO(raw)) as decoded:
   assert decoded.format=='JPEG' and decoded.size==(36,36) and getattr(decoded,'n_frames',1)==1
   decoded.seek(0);decoded.load()
  old_bytes=(site/e['old_data_route'].lstrip('/')).read_bytes()
  assert e['old_data_sha256']==old['source16_data_sha256']
  e['old_source_data_sha256']=e['old_data_sha256']
  e['old_data_sha256']=hashlib.sha256(old_bytes).hexdigest()
  old_line=old_bytes.decode('utf-8',errors='strict').splitlines()[old['talent_assignment_line']-1]
  assert e['talent'] in html.unescape(old_line).replace("\\'","'")
  raw_old=ROOT/old['source16_raw_data_entity_path'];assert sha(raw_old)==e['old_source_data_sha256']
  original_lines=raw_old.read_bytes().splitlines();derived_lines=old_bytes.splitlines()
  assert len(original_lines)==len(derived_lines)
  changes=[i for i,(a,b) in enumerate(zip(original_lines,derived_lines)) if a!=b]
  assert changes==[4] and original_lines[4]==b'var talentPath = "/info/basics/talents/";'
  assert derived_lines[4].startswith(b'var talentPath = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?')
  labels=(ROOT/old['donotlocalize_source_entity_path']).read_bytes();assert hashlib.sha256(labels).hexdigest()==old['donotlocalize_source_sha256']
  assert old['image_label'] in html.unescape(labels.decode().splitlines()[old['image_label_assignment_line']-1]).replace("\\'","'")
  later_bytes=archive.read(later['data_zip_member']);assert hashlib.sha256(later_bytes).hexdigest()==e['later_data_sha256']==later['data_sha256']
  assert e['talent'] in html.unescape(later_bytes.decode('utf-8').splitlines()[later['talent_assignment_line']-1]).replace("\\'","'")
  total+=len(raw);payloads.append({'route':e['route'],'repository_path':e['repository_path'],'sha256':e['sha256'],'bytes':len(raw),'class':e['class'],'talent':e['talent'],'state':e['state']})
assert total==19439 and len({r['route'] for r in payloads})==18 and len({r['repository_path'] for r in payloads})==18
proof={'schema':'wow-root-talent-v56-source-acceptance/v1','accepted_sources':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
 'draft_map_sha256':sha(draft),'source_preparation_sha256':sha(prep_path),'semantic_audit_sha256':sha(audit_path),
 'selected_canonical_ids':sorted(selected),'images':18,'bytes':total,'source_zip_sha256':sha(zip_path),
 'all_zip_bytes_rehashed_and_frames_decoded':True,'old_and_new_data_rows_independently_checked':True,
 'old_image_label_rows_independently_checked':True,'old_2008_talent_rows_unchanged':True,'old_derived_data_unchanged':True,
 'raw_vs_derived_data_difference':'Only the pre-existing talentPath URL rewrite on line 5; source and derived hashes are recorded separately.',
 'original_2008_image_recoveries':0,
 'classification':'later_related_source','original_capture_timestamp':None,'pixel_identity_with_2008':'unknown',
 'excluded':'The other eighteen effect/merged/partial-name candidates are not accepted for mapping.', 'objects':payloads}
proof_path=OUT/'root-source-acceptance.json';assert not proof_path.exists();write(proof_path,proof)
original=OUT/'input-map.initial-draft.json';assert not original.exists();original.write_bytes(draft.read_bytes())
for key in ('base_map','semantic_audit','source_acceptance'):data[key]=data[key].replace('\\','/')
data['source'].pop('zip_path')
decision={'schema':'wow-root-related-talent-icons-v56-decision/v1','accepted_for_derived_trial':True,'decided_utc':datetime.now(timezone.utc).isoformat(),
 'base_map':data['base_map'],'base_map_sha256':data['base_map_sha256'],'semantic_audit':data['semantic_audit'],'semantic_audit_sha256':data['semantic_audit_sha256'],
 'source_acceptance':data['source_acceptance'],'source_acceptance_sha256':data['source_acceptance_sha256'],
 'root_source_acceptance':proof_path.relative_to(ROOT).as_posix(),'root_source_acceptance_sha256':sha(proof_path),
 'selected_canonical_ids':sorted(selected),'source':data['source'],'base_icon_count':1006,'mapped_icon_count':18,'icon_count':1024,'mapped_source_bytes':19439,
 'original_2008_images_recovered':0,'images_reencoded':False,'scope':'Only same-class identical canonical talent names. Supply artwork and retain all 2008 data and existing source notices.','entries':data['entries']}
decision_path=OUT/'decision.json';assert not decision_path.exists();write(decision_path,decision)
data.update(decision=decision_path.relative_to(ROOT).as_posix(),decision_sha256=sha(decision_path),
 root_source_acceptance=proof_path.relative_to(ROOT).as_posix(),root_source_acceptance_sha256=sha(proof_path),
 source_preparation=prep_path.relative_to(ROOT).as_posix(),source_preparation_sha256=sha(prep_path))
write(draft,data)
pins={'schema':'wow-related-talent-icons-v56-root-pins/v1','map_sha256':sha(draft),'decision_sha256':sha(decision_path),
 'root_source_acceptance_sha256':sha(proof_path),'source_preparation_sha256':sha(prep_path),'semantic_audit_sha256':sha(audit_path),
 'source_acceptance_sha256':data['source_acceptance_sha256'],'base_map_sha256':data['base_map_sha256'],
 'base_icon_count':1006,'mapped_icon_count':18,'icon_count':1024,'mapped_source_bytes':19439,'new_network_requests':0,'images_reencoded':False}
write(OUT/'root-input-pins.json',pins)
print(json.dumps(pins))

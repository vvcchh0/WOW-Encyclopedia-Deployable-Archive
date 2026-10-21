"""Bind the observed Broken dynamic thumbnail spelling to its related illustration."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
DEST=ROOT/'research/continuous-recovery-20261021/integration/related-guide-images-v49'
DECISION=PUB/'root-related-guide-image-v49-decision.json'
MAP=DEST/'input-map.json'
assert not DECISION.exists() and not MAP.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
old_map=ROOT/'research/continuous-recovery-20261021/integration/related-guide-images/input-map.json'
assert sha(old_map)=='79865df9bbc1c03cd7b80a5154b6fff1e649ba704fdc7db073c04aba7151f008'
mapping=read(old_map);previous=ROOT/mapping['decision'];old=read(previous)
source=ROOT/'.scratch/offline-non-gallery-20261021-v16/site'
page=source/'burningcrusade/townhall/bestiary.html'
script=source/'burningcrusade/townhall/images/bestiary/bestiary-script.js'
assert sha(page)=='d661ab5331d5cda695b74b7eba791d1745c19d755c693d296f89b6501e79db0c'
assert sha(script)=='8c622c25920d0a2045f2537e4c56c6f5274e00c521c8783da2edacaef9fdb69a'
assert 'cBroken = new bestiaryCreature("broken",100,600);' in page.read_text(encoding='utf-8')
assert "images/bestiary/thumb-\"+theNewCreature.creatureName+\".jpg" in script.read_text(encoding='utf-8-sig')
diag=PUB/'v48-bestiary-diagnostic.json';observation=read(diag)
assert not observation['errors'] and not observation['external'] and observation['asset_fulfillments']==0
assert any('requested=images%2Fbestiary%2Fthumb-broken.jpg' in row['src'] for row in observation['states'][1]['images'])
reuse={'target_route':'/burningcrusade/townhall/images/bestiary/thumb-broken.jpg','route':'/__offline/related-guide-images/thumb-thebroken.jpg','page_route':'/burningcrusade/townhall/bestiary.html','creature_name':'broken','classification':'current_related_display_mapping','original_capture_timestamp':None,'page_source_sha256':sha(page),'script_source_sha256':sha(script)}
assert not (source/reuse['target_route'].lstrip('/')).exists()
decision={**old,'schema':'wow-related-guide-image-decision/v2','checked_utc':datetime.now(timezone.utc).isoformat(),'supersedes':previous.relative_to(ROOT).as_posix(),'supersedes_sha256':sha(previous),'compatibility_reuses':[reuse],'decision':'Keep the accepted current ArchiveCraft The Broken illustration. The historical page defines cBroken with creatureName broken and the script builds thumb-broken.jpg after a real menu click, replacing the static thumb-thebroken.jpg DOM. Route both same-topic thumbnail spellings to this one explicitly attributed current illustration. Do not alias title PNGs, large screenshots, or other creatures.','bindings':old['bindings']+[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (page,script,diag,old_map)]}
DECISION.write_text(json.dumps(decision,indent=2)+'\n',encoding='utf-8')
mapping.update({'schema':'wow-related-guide-image-map/v2','decision':DECISION.relative_to(ROOT).as_posix(),'decision_sha256':sha(DECISION),'compatibility_reuses':[reuse]})
DEST.mkdir(exist_ok=True);MAP.write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
review=PUB/'root-v48-candidate-review.json'
assert not review.exists()
review.write_text(json.dumps({'version':'v48','checked_utc':datetime.now(timezone.utc).isoformat(),'bytes_accepted':True,'browser_publication_accepted':False,'published':False,'reason':'Actual The Broken menu click replaces the static DOM with thumb-broken.jpg, which remains a placeholder. Add only this source-backed display mapping in v49 and repeat actual clicks.','other_images':'The first three encyclopedia pages passed image-load and source-note contrast checks before the guide assertion stopped the browser probe.','tree_probe_correction':'The first checker used read_text and normalized CRLF before its byte comparison. A second BOM hypothesis was stopped. Final checker uses raw decoded bytes; reward script differs from v46 by exactly two URL literals, with CRLF retained and no BOM. Original Source16 bytes are separately pinned.','bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (PUB/'root-v48-export-acceptance.json',PUB/'v48-browser-command.log',diag,DECISION)]},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'map_sha256':sha(MAP),'decision_sha256':sha(DECISION),'source_acceptance_sha256':mapping['source_acceptance_sha256'],'compatibility_reuses':1}))

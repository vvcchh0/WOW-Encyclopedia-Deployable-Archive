"""Verify all v41 bytes and the sole helper delta from the frozen v40 candidate."""
import hashlib
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];PUB=Path(__file__).resolve().parent
SITE=ROOT/'.scratch/pages-resources-20261021-v41';OLD=ROOT/'.scratch/pages-resources-20261021-v40'
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_bytes())
out=PUB/'root-v41-export-acceptance.json';assert not out.exists()
before=shutil.disk_usage(ROOT).free;assert before>=11005853696
code_path=PUB/'root-v41-code-acceptance.json';code=read(code_path)
for r in code['code_bindings']:assert sha((ROOT/r['path']).read_bytes())==r['sha256']
prior_path=OLD/'export-provenance.json';assert sha(prior_path.read_bytes())=='91362223dc8b5dee7bda876834ca58ea145379e78442a2321a931866ea7b8b0d'
build_path=ROOT/'research/continuous-recovery-20261021/integration/v41/v41-build-receipt.json';build=read(build_path)
prov_path=SITE/'export-provenance.json';prov_sha=sha(prov_path.read_bytes());assert build['provenance_sha256']==prov_sha
prov=read(prov_path);files={r['output_path']:r for r in prov['files']};old={r['output_path']:r for r in read(prior_path)['files']}
assert len(files)==len(prov['files'])==9125 and set(files)==set(old)
actual=set()
for directory,dirs,names in os.walk(SITE,followlinks=False):
    for name in dirs+names:assert not (Path(directory)/name).is_symlink()
    actual.update((Path(directory)/name).relative_to(SITE).as_posix() for name in names)
assert actual==set(files)|{'export-provenance.json'}
def check(pair):
    relative,row=pair;data=(SITE/relative).read_bytes()
    assert len(data)==row['derived_length'] and sha(data)==row['derived_sha256'],relative
    return len(data)
with ThreadPoolExecutor(max_workers=8) as pool:total=sum(pool.map(check,files.items()))+prov_path.stat().st_size
changed=[p for p in old if old[p]['derived_sha256']!=files[p]['derived_sha256']]
assert changed==['__offline/flash-exhibits.js'],changed
helper=(SITE/changed[0]).read_bytes();assert sha(helper)==sha((ROOT/'tools/browser_assets/offline-flash.js').read_bytes())
assert b'unmuteOverlay: "hidden"' in helper
stats=prov['stats'];assert stats['image_overlay_records']==657 and stats['flash_exhibit_pages']==3 and stats['flash_runtime_files']==10
assert stats['guide_preview_count']==22 and stats['guide_image_collection_images']==39
after=shutil.disk_usage(ROOT).free;assert after>=11005853696
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'site':SITE.relative_to(ROOT).as_posix(),
    'export_provenance_sha256':prov_sha,'declared_files':len(files),'actual_files':len(actual),'tree_bytes':total,
    'changed_paths_compared_v40':changed,'unchanged_objects_compared_v40':len(old)-1,
    'scope':'Every file hash and length verified. Sole site delta from root-checked v40 is the reviewed unmute-overlay config in the manual helper.',
    'image_overlays':657,'new_original_images':0,'new_original_pages':0,'network_requests':0,'browser_accepted':False,'published':False,
    'disk_free_before_bytes':before,'disk_free_after_bytes':after,
    'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())} for p in [code_path,build_path,PUB/'root-v40-export-acceptance.json']]}
out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))

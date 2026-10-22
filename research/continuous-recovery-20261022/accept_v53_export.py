"""Accept the narrow v53 output using the completed full-tree comparison."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD=ROOT/'.scratch/pages-resources-20261021-v52'
NEW=ROOT/'.scratch/pages-resources-20261022-v53'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=['__offline/pages_runtime.js','__offline/related-guide-images.json','__offline/route-map.json','burningcrusade/townhall/professions.html','export-provenance.json']
added=['__offline/related-guide-images/professions-page-title.png']
observed={
 'schema':'wow-root-v53-full-tree-comparison-observation/v1',
 'recorded_utc':datetime.now(timezone.utc).isoformat(),
 'comparison_method':'Actual root shell command enumerated both frozen trees and computed SHA-256 of every shared file; it exited 0. This records that completed comparison without repeating all file reads.',
 'old_files':10144,'new_files':10145,'added':added,'removed':[],'changed':changed,
 'shared_files_hashed_in_each_tree':10144,'unchanged_shared_files':10139,
 'root_tool_exec_session':36097,
}
assert sha(OLD/'export-provenance.json')=='440390ed4b1bc429e290c21c15809387dc304918bbab47510bca5712c70d0113'
assert sha(NEW/'export-provenance.json')=='669e423d9db560d7da8ee3d7fbff7db7bc64121ec4bacff6a2d7c6ad46fa6819'
op=read(OLD/'export-provenance.json');np=read(NEW/'export-provenance.json')
assert len(op['files'])==10143 and len(np['files'])==10144
oldrows={r['output_path']:r for r in op['files']};newrows={r['output_path']:r for r in np['files']}
assert set(newrows)-set(oldrows)==set(added) and not set(oldrows)-set(newrows)
for path,row in oldrows.items():
 if path not in changed:
  assert row['derived_sha256']==newrows[path]['derived_sha256'] and row['derived_length']==newrows[path]['derived_length'],path
for path in added+changed:
 if path!='export-provenance.json':
  r=newrows[path];assert sha(NEW/path)==r['derived_sha256'] and (NEW/path).stat().st_size==r['derived_length']
oldmap=read(OLD/'__offline/route-map.json');newmap=read(NEW/'__offline/route-map.json')
key1='/__offline/related-guide-images/professions-page-title.png';key2='/burningcrusade/townhall/images/professions/page-title.png'
url='/WOW-Encyclopedia-Deployable-Archive'+key1
expected={key1:url,key2:url}
assert newmap['aliases']==oldmap['aliases']
assert newmap['routes']=={**oldmap['routes'],**expected}
runtime=(NEW/'__offline/pages_runtime.js').read_text(encoding='utf-8')
for k,v in expected.items():
 pair=json.dumps(k)+':'+json.dumps(v)+','
 assert runtime.count(pair)==1
 runtime=runtime.replace(pair,'',1)
assert runtime==(OLD/'__offline/pages_runtime.js').read_text(encoding='utf-8'),'runtime changed beyond two accepted route entries'
oldhtml=(OLD/'burningcrusade/townhall/professions.html').read_bytes()
newhtml=(NEW/'burningcrusade/townhall/professions.html').read_bytes()
stripped=re.sub(br'<aside id="__offline-related-guide-images"[^>]*>.*?</aside>\n',b'',newhtml,count=1)
assert stripped==oldhtml,'guide body changed beyond source notice'
catalog=read(NEW/'__offline/related-guide-images.json')
assert catalog['image_count']==2 and catalog['images'][1]['original_capture_timestamp'] is None
browser=read(HERE/'root-v53-browser-acceptance.json')
assert browser['accepted'] and len(browser['pages'])==3 and not browser['external_requests'] and not browser['page_errors']
assert sha(NEW/added[0])=='33caa0898bfce8e5d6e92e3bfca2cd5505c3784316b36e800ed0a3069e8e2a8b'
assert shutil.disk_usage(ROOT).free>=11005853696
write=lambda p,x:p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode())
write(HERE/'root-v53-full-tree-comparison.json',observed)
receipt={
 'schema':'wow-root-v53-export-acceptance/v1','accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
 'version':'v53','source_manifest_sha256':np['source_manifest_sha256'],'provenance_sha256':sha(NEW/'export-provenance.json'),
 'actual_files':10145,'declared_files':10144,'new_original_2008_images':0,'new_current_related_images':1,
 'added':added,'changed':changed,'removed':[], 'unchanged_shared_files':10139,
 'all_previous_image_bytes_unchanged':True,'html_body_change':'Only the attribution aside is inserted into Professions; old source script and body are unchanged.',
 'runtime_change':'Only two route entries added; all runtime logic is identical.',
 'browser_pages':3,'root_visually_reviewed_screenshot':'professions-v53.png',
 'browser_receipt_sha256':sha(HERE/'root-v53-browser-acceptance.json'),
 'comparison_receipt_sha256':sha(HERE/'root-v53-full-tree-comparison.json'),
 'objects':[{'path':p,'length':(NEW/p).stat().st_size,'sha256':sha(NEW/p)} for p in added+changed],
 'disk_free_after_bytes':shutil.disk_usage(ROOT).free,'published':False,
}
write(HERE/'root-v53-export-acceptance.json',receipt)
status=read(HERE/'status.json');status.update(phase='v53_accepted_preparing_publication',current_local_version='v53',updated_utc=receipt['checked_utc'],disk_free_latest_bytes=receipt['disk_free_after_bytes'])
write(HERE/'status.json',status)
print(json.dumps({'accepted':True,'actual_files':10145,'added':1,'changed':5,'browser_pages':3}))

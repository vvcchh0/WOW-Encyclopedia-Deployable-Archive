"""Independent byte and narrow link-delta acceptance of the v42 export."""
import hashlib
import html
import json
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[3]; PUB=Path(__file__).resolve().parent
OLD=ROOT/'.scratch/pages-resources-20261021-v41'; SITE=ROOT/'.scratch/pages-resources-20261021-v42'
OUT=PUB/'root-v42-export-acceptance.json'
assert not OUT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_bytes())
before=shutil.disk_usage(ROOT).free;assert before>=11005853696
code=read(PUB/'root-v42-code-acceptance.json')
for row in code['code_bindings']: assert sha((ROOT/row['path']).read_bytes())==row['sha256'],row['path']
old_prov=OLD/'export-provenance.json'
assert sha(old_prov.read_bytes())=='159ceef08c5254d7cd0b492176e3fd3e5152453f7376163533fc3fea677153da'
source_manifest=ROOT/'.scratch/offline-navigation-20261015-v15/build-manifest.json'
assert sha(source_manifest.read_bytes())=='d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002'
prov=read(SITE/'export-provenance.json'); prior=read(old_prov)
files={r['output_path']:r for r in prov['files']}; old={r['output_path']:r for r in prior['files']}
assert len(files)==len(prov['files'])==9131
reader_root='__offline/related-sites/blizzcast/'
expected_added={reader_root+x for x in ('index.html','archive.html','episode1.html','episode2.html','feed.html','reader.css')}
assert set(files)-set(old)==expected_added and set(old)<=set(files)
actual=set()
for directory,dirs,names in os.walk(SITE,followlinks=False):
    for name in dirs+names:assert not (Path(directory)/name).is_symlink()
    actual.update((Path(directory)/name).relative_to(SITE).as_posix() for name in names)
assert actual==set(files)|{'export-provenance.json'}
def check(pair):
    relative,row=pair; data=(SITE/relative).read_bytes()
    assert len(data)==row['derived_length'] and sha(data)==row['derived_sha256'],relative
    if relative in old:
        data_old=(OLD/relative).read_bytes()
        assert len(data_old)==old[relative]['derived_length'] and sha(data_old)==old[relative]['derived_sha256'],relative
    return len(data)
with ThreadPoolExecutor(max_workers=8) as pool:total=sum(pool.map(check,files.items()))+(SITE/'export-provenance.json').stat().st_size
prefix=prov['base_path']; assert prefix==prior['base_path']=='/WOW-Encyclopedia-Deployable-Archive/'
origins={
    ('us.blizzard.com','/blizzcast'):'index.html',('us.blizzard.com','/blizzcast/'):'index.html',
    ('us.blizzard.com','/blizzcast/index.xml'):'index.html',('us.blizzard.com','/blizzcast/archive.xml'):'archive.html',
    ('us.blizzard.com','/blizzcast/archive/episode1.xml'):'episode1.html',
    ('us.blizzard.com','/blizzcast/archive/episode2.xml'):'episode2.html',
    ('us.blizzard.com','/blizzcast/_content/en-US/rss.xml'):'feed.html',
}
anchor=re.compile(r'''(?P<start><a\b[^>]*?\bhref\s*=\s*)(?P<quote>["'])(?P<url>[^"']*)(?P=quote)''',re.I)
healed=0
def heal(match):
    global healed
    u=urlsplit(html.unescape(match['url']))
    if u.path!=prefix+'__offline/missing.html':return match[0]
    requested=parse_qs(u.query).get('requested',[])
    if len(requested)!=1:return match[0]
    r=urlsplit(requested[0]);target=origins.get((r.hostname,r.path))
    if target is None or r.scheme not in ('http','https') or r.query or r.fragment or r.username or r.password:return match[0]
    if r.port is not None and r.port!=(80 if r.scheme=='http' else 443):return match[0]
    healed+=1
    return match['start']+match['quote']+prefix+reader_root+target+match['quote']
changed=[p for p in old if old[p]['derived_sha256']!=files[p]['derived_sha256']]
changed_html=[p for p in changed if p.endswith('.html')]
assert len(changed_html)==669
for relative in changed_html:
    previous=(OLD/relative).read_text(encoding='utf-8')
    assert anchor.sub(heal,previous)==(SITE/relative).read_text(encoding='utf-8'),relative
expected_other={'shared/global/talents/includes/localize.js','shared/global/talents/includes/printOutTop.js','__offline/route-map.json','__offline/pages_runtime.js'}
assert set(changed)-set(changed_html)==expected_other
assert (SITE/'shared/global/talents/includes/printOutTop.js').read_bytes()==(ROOT/'tests/fixtures/talent_source15/printOutTop.js').read_bytes()
routes=read(SITE/'__offline/route-map.json');old_routes=read(OLD/'__offline/route-map.json')
assert {k:v for k,v in routes.items() if k!='routes'}=={k:v for k,v in old_routes.items() if k!='routes'}
assert all(routes['routes'][k]==v for k,v in old_routes['routes'].items())
assert set(routes['routes'])-set(old_routes['routes'])=={'/'+p for p in expected_added}
sys.path.insert(0,str(ROOT/'tools'));import blizzcast_reader
runtime_bodies=[]
for site,routes_data in ((OLD,old_routes),(SITE,routes)):
    text=(site/'__offline/pages_runtime.js').read_text(encoding='utf-8')
    embedded=re.search(r'    var routes = (\{[^\n]*\});',text)
    assert embedded and json.loads(embedded[1])==routes_data['routes']
    runtime_bodies.append(text[:embedded.start(1)]+'<VERIFIED_ROUTE_MAP>'+text[embedded.end(1):])
assert runtime_bodies[0]==runtime_bodies[1]
bundle=blizzcast_reader.load_blizzcast_bundle(ROOT/'research/continuous-recovery-20261021/integration/blizzcast-reader/input-source-map.json',ROOT,prefix)
for f in bundle.generated_files:
    assert f['data'].encode('utf-8')==(SITE/f['path'].lstrip('/')).read_bytes()
    public=files[f['path'].lstrip('/')]
    assert 'payload_path' not in json.dumps(public) and 'Set-Cookie' not in json.dumps(public)
stats=prov['stats']
for key,n in {'image_overlay_records':657,'guide_preview_count':22,'guide_image_collection_images':39,
              'flash_exhibit_pages':3,'flash_runtime_files':10,'talent_compat_scripts':2,'blizzcast_reading_pages':5,'blizzcast_reading_styles':1}.items():
    assert stats[key]==n,key
assert prov['flash_exhibits']==prior['flash_exhibits']
for p in old:
    if old[p]['kind']=='image_overlay' or p.endswith(('.swf','.wasm')):
        assert files[p]['derived_sha256']==old[p]['derived_sha256'],p
after=shutil.disk_usage(ROOT).free;assert after>=11005853696
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'site':SITE.relative_to(ROOT).as_posix(),
    'export_provenance_sha256':sha((SITE/'export-provenance.json').read_bytes()),'declared_files':len(files),'actual_files':len(actual),
    'tree_bytes':total,'added_files':sorted(expected_added),'removed_files':[], 'changed_html_pages':len(changed_html),
    'html_changes_are_only_exact_accepted_blizzcast_anchor_replacements':True,'restored_anchor_occurrences':healed,
    'changed_other_files':sorted(expected_other),'unchanged_prior_objects':len(old)-len(changed),
    'original_images_and_swfs_byte_preserved':True,'image_overlay_records':657,'guide_previews':22,'guide_images':39,
    'new_reading_pages':5,'new_original_images':0,'browser_accepted':False,'published':False,'network_requests':0,
    'disk_free_before_bytes':before,'disk_free_after_bytes':after,
    'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())} for p in (PUB/'root-v42-code-acceptance.json',ROOT/'research/continuous-recovery-20261021/integration/v42/v42-build-receipt.json')]}
OUT.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))

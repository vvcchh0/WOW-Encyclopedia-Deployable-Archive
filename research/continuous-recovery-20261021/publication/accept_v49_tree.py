"""Root acceptance: four exact illustrations, readable notes, two reward URLs."""
import hashlib,json,os,re,shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
OLD=ROOT/'.scratch/pages-resources-20261021-v46'
SITE=ROOT/'.scratch/pages-resources-20261021-v49'
OUT=PUB/'root-v49-export-acceptance.json'
assert not OUT.exists()
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'export-provenance.json')=='fdb6228a05174d38d263457f15d387bb53dfb74c19c544509e009cce611b0279'
build=ROOT/'research/continuous-recovery-20261021/integration/v49/v49-build-receipt.json'
assert sha(SITE/'export-provenance.json')==read(build)['provenance_sha256']
old,prov=read(OLD/'export-provenance.json'),read(SITE/'export-provenance.json')
assert old['source_manifest_sha256']==prov['source_manifest_sha256']=='e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
files={r['output_path']:r for r in prov['files']};prior={r['output_path']:r for r in old['files']}
assert len(files)==len(prov['files'])==prov['stats']['output_files']==10142
maps=[read(ROOT/('research/continuous-recovery-20261021/integration/'+name+'/input-map.json')) for name in ('related-encyclopedia-images','related-guide-images-v49')]
entries=[r for m in maps for r in m['entries']]
new_paths={r['route'].lstrip('/') for r in entries}|{'__offline/related-encyclopedia-images.json','__offline/related-guide-images.json'}
assert len(new_paths)==6 and set(files)-set(prior)==new_paths and set(prior)<=set(files)
page_path=lambda route:route.lstrip('/')+('.html' if route.endswith('.xml') else '')
page_paths={page_path(r['page_route']) for r in entries}
reward='info/basics/factions/rewardstable/scripts/rewardstable-new.js'
changed={p for p in prior if prior[p]['derived_sha256']!=files[p]['derived_sha256']}
assert changed==page_paths|{reward,'__offline/pages_runtime.js','__offline/route-map.json'}
actual=set()
for directory,dirs,names in os.walk(SITE,followlinks=False):
    assert all(not (Path(directory)/n).is_symlink() for n in dirs+names)
    actual.update((Path(directory)/n).relative_to(SITE).as_posix() for n in names)
assert actual==set(files)|{'export-provenance.json'}
def check(pair):
    path,row=pair;entity=SITE/path
    assert entity.stat().st_size==row['derived_length'] and sha(entity)==row['derived_sha256'],path
    if path in prior:
        assert sha(OLD/path)==prior[path]['derived_sha256'],path
        if path not in changed:assert entity.read_bytes()==(OLD/path).read_bytes(),path
    return row['derived_length']
with ThreadPoolExecutor(max_workers=8) as pool:total=sum(pool.map(check,files.items()))+(SITE/'export-provenance.json').stat().st_size
prefix=prov['base_path'].rstrip('/')
for entry in entries:
    row=files[entry['route'].lstrip('/')];payload=SITE/row['output_path']
    assert payload.read_bytes()==(ROOT/entry['payload_path']).read_bytes()
    assert row['kind'] in {'related_encyclopedia_image','related_guide_image'} and row['transformed'] is False
    assert row['mime'].split(';')[0]=='image/jpeg'
    assert row['source_refs'][0]['classification']=='current_related_archive_source'
    assert row['source_refs'][0]['original_capture_timestamp'] is None and 'payload_path' not in json.dumps(row)
    with Image.open(payload) as img:
        assert img.format=='JPEG' and img.size==(entry['width'],entry['height']) and getattr(img,'n_frames',1)==1
        img.load()
    path=page_path(entry['page_route']);before=(OLD/path).read_text(encoding='utf-8');after=(SITE/path).read_text(encoding='utf-8')
    image_pattern=r'<img[^>]*'+re.escape(Path(entry['target_route']).name)+r'[^>]*>'
    matches=re.findall(image_pattern,before)
    assert len(matches)==1 and 'missing-image.svg?' in matches[0]
    replacement='<img src="'+prefix+entry['route']+'"'
    # Preserve any historical img attributes while replacing only its src.
    old_src=re.search(r'\bsrc="([^"]+)"',matches[0])[1]
    assert after.count(prefix+entry['route'])==1
    reverted=after.replace(prefix+entry['route'],old_src)
    reverted,count=re.subn(r'<aside id="__offline-related-(?:encyclopedia|guide)-images" role="note"[^>]*>.*?</aside>\n?','',reverted,flags=re.S)
    assert count==1 and reverted==before,path+' changed beyond image src and source note'
    assert 'background:#eadbb7;color:#302619' in after and entry['source_page_url'] in after
    assert files[path]['related_image_refs'][0]['source_page_url']==entry['source_page_url']
source_reward=ROOT/'.scratch/offline-non-gallery-20261021-v16/site'/reward
assert sha(source_reward)=='7c73724e2c6cc60d4ee7f0efd57fc0f3a31a0818f84c23a75a1960f60ee35855'
assert source_reward.read_bytes()==b'\xef\xbb\xbf'+(OLD/reward).read_bytes()
before=(OLD/reward).read_bytes().decode('utf-8');expected=before
for side in ('alliance','horde'):
    literal=f'url(images/button-{side}.jpg)'
    assert expected.count(literal)==1
    expected=expected.replace(literal,f'url({prefix}/info/basics/factions/rewardstable/images/button-{side}.jpg)')
assert (SITE/reward).read_bytes()==expected.encode('utf-8')
old_routes,routes=read(OLD/'__offline/route-map.json'),read(SITE/'__offline/route-map.json')
assert routes['aliases']==old_routes['aliases'] and all(routes['routes'][k]==v for k,v in old_routes['routes'].items())
targets={r['target_route']:r['route'] for r in entries}
reuses=maps[1]['compatibility_reuses'];assert len(reuses)==1
for row in reuses:
    assert row['classification']=='current_related_display_mapping' and row['original_capture_timestamp'] is None
    targets[row['target_route']]=row['route']
assert prov['related_guide_images']['source']['compatibility_reuses']==reuses
assert read(SITE/'__offline/related-guide-images.json')['compatibility_reuses']==reuses
assert set(routes['routes'])-set(old_routes['routes'])==set(targets)|{'/'+p for p in new_paths}
for target,source in targets.items():
    assert routes['routes'][target]==routes['routes'][source] and target not in routes['aliases']
    assert not (SITE/target.lstrip('/')).exists()
runtime=[]
for site,route_data in ((OLD,old_routes),(SITE,routes)):
    text=(site/'__offline/pages_runtime.js').read_text(encoding='utf-8');match=re.search(r'    var routes = (\{[^\n]*\});',text)
    assert match and json.loads(match[1])==route_data['routes']
    runtime.append(text[:match.start(1)]+'<VERIFIED_ROUTES>'+text[match.end(1):])
assert runtime[0]==runtime[1]
for key in ('related_talent_ui','talent_box_layout_compatibility','layout_compatibility_reuse','related_talent_icons','flash_exhibits','blizzcast_reading'):assert prov[key]==old[key],key
for key,count in {'related_encyclopedia_image_assets':3,'related_encyclopedia_notice_pages':3,'related_guide_image_assets':1,'related_guide_notice_pages':1,'rewardstable_compat_scripts':1,'related_talent_icons':986,'flash_exhibit_pages':3,'guide_image_collection_images':39,'image_overlay_records':657}.items():assert prov['stats'][key]==count,key
for key,count in (('related_encyclopedia_images',3),('related_guide_images',1)):
    assert prov[key]['image_count']==count and prov[key]['original_2008_images_recovered']==0
assert shutil.disk_usage(ROOT).free>=11005853696
receipt={'schema':'wow-root-export-acceptance/v2','accepted':True,'version':'v49','checked_utc':datetime.now(timezone.utc).isoformat(),'local_site':SITE.relative_to(ROOT).as_posix(),'export_provenance_sha256':sha(SITE/'export-provenance.json'),'declared_files':len(files),'actual_files':len(actual),'tree_bytes':total,'added_files_count':6,'changed_existing_files':sorted(changed),'removed_files':[],'unchanged_prior_objects':len(prior)-len(changed),'new_related_encyclopedia_images':3,'new_related_guide_images':1,'new_related_image_bytes':176325,'new_original_2008_images':0,'article_html_reverts_exactly_after_removing_only_new_src_and_note':True,'all_prior_images_swfs_wasm_and_talent_data_byte_preserved':True,'all_scripts_except_exact_reward_two_literal_repair_preserved':True,'runtime_changes_are_only_route_map':True,'browser_accepted':False,'published':False,'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (PUB/'root-v49-code-acceptance.json',PUB/'v49-export-execution.json',build,PUB/'root-related-encyclopedia-image-decision.json',PUB/'root-related-guide-image-v49-decision.json',Path(__file__))]}
OUT.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))

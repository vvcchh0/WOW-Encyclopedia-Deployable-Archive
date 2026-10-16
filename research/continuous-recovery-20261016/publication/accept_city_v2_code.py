"""Verify real v1 compatibility and the new six-group preview bundle."""
import hashlib,json,subprocess,sys,types
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016'
sys.path.insert(0,str(R/'tools'))
import guide_previews as current
import export_github_pages as pages

def main():
    old_code=subprocess.check_output(['git','show','HEAD:tools/guide_previews.py'],cwd=R)
    assert hashlib.sha256(old_code).hexdigest()=='7281dd7f56b1f54da8c13088f2b5bd89f90aa73c11a5f8a326a03ac1187bd2a3'
    old=types.ModuleType('root_prior_guide_previews');sys.modules[old.__name__]=old
    exec(compile(old_code,'git-HEAD:tools/guide_previews.py','exec'),old.__dict__)
    source=R/'.scratch/offline-navigation-20261015-v15/site';mp=source.parent/'build-manifest.json'
    assert hashlib.sha256(mp.read_bytes()).hexdigest()=='d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002'
    manifest=json.loads(mp.read_bytes())
    routes={x['route']:pages.static_url(pages.DEFAULT_BASE_PATH,pages.static_rel_for_route(x['route'],x)) for x in manifest['files'] if isinstance(x,dict) and isinstance(x.get('route'),str)}
    kw={'workspace_root':R,'source_site':source,'manifest_path':mp,'manifest':manifest,'route_to_static':routes}
    v1=B/'integration/guide-previews-source-map.json';v2=B/'integration/v18-guide-previews/guide-previews-source-map-v2.json'
    assert hashlib.sha256(v1.read_bytes()).hexdigest()=='cf0da5fec45993684676d94d1cc09fad3f5a421dabbb18b56861000daa6248b2'
    assert hashlib.sha256(v2.read_bytes()).hexdigest()=='9d95ce6e8a04282da1c282e80e4fde9c29c18d853d363da418ec1bb87e1c6581'
    before=old.load_guide_preview_map(v1,**kw);after=current.load_guide_preview_map(v1,**kw);extended=current.load_guide_preview_map(v2,**kw)
    assert before.provenance()==after.provenance()
    assert len(extended.groups)==6 and extended.preview_count==22
    checks=[]
    for a,b,c in zip(before.groups,after.groups,extended.groups[:5]):
        assert old.render_gallery_section(a)==current.render_gallery_section(b)==current.render_gallery_section(c)
        checks.append({'group':a.group_id,'v1_and_v2_section_bytes_equal':True})
    city=extended.group_for_gallery('/pvp/worldpvp/cityattacks-gallery.html');assert city and len(city.previews)==3
    section=current.render_gallery_section(city)
    assert section.count('data-guide-preview-route=')==3 and section.count('Preserved guide previews')==1
    assert '/pvp/worldpvp/images/city/ss1.jpg' not in section and 'dynamic_full_candidate' not in section
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,
            'source_manifest_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),
            'production_code_sha256':hashlib.sha256((R/'tools/guide_previews.py').read_bytes()).hexdigest(),
            'v2_map_sha256':hashlib.sha256(v2.read_bytes()).hexdigest(),'v1_provenance_unchanged':True,
            'v1_render_and_existing_v2_groups_byte_equal':checks,'v2_groups':6,'v2_previews':22,
            'city_cards':3,'dynamic_full_aliases_added':0,'worker_reported_tests':{'guide_preview':9,'related_export_image':42},
            'independent_checks':'Root loaded both maps against real source15 and compared the old HEAD v1 implementation with the new v1/v2 render output.'}
    (B/'publication/root-city-v2-code-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k!='v1_render_and_existing_v2_groups_byte_equal'}))

if __name__=='__main__':main()

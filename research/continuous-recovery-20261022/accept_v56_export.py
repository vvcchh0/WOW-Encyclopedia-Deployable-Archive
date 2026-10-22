"""Independent actual-byte acceptance of the v56 derived export."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
import re,shutil
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
OLD=ROOT/'.scratch/pages-resources-20261022-v55';NEW=ROOT/'.scratch/pages-resources-20261022-v56'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(site,doc):
 out={r['output_path']:(r['derived_sha256'],r['derived_length']) for r in doc['files']}
 assert len(out)==len(doc['files'])
 out['export-provenance.json']=(sha(site/'export-provenance.json'),(site/'export-provenance.json').stat().st_size)
 return out
def main():
 assert shutil.disk_usage(ROOT).free>=11005853696
 prior=read(HERE/'root-v55-export-acceptance.json');assert prior['accepted']
 assert sha(OLD/'export-provenance.json')==prior['export_provenance_sha256']
 olddoc,newdoc=read(OLD/'export-provenance.json'),read(NEW/'export-provenance.json')
 old,new=inventory(OLD,olddoc),inventory(NEW,newdoc)
 actual={p.relative_to(NEW).as_posix():p for p in NEW.rglob('*') if p.is_file()}
 assert set(actual)==set(new)
 started=datetime.now(timezone.utc).isoformat();total=0
 for i,(name,p) in enumerate(sorted(actual.items()),1):
  assert not p.is_symlink() and not(getattr(p.stat(),'st_file_attributes',0)&0x400),name
  assert (sha(p),p.stat().st_size)==new[name],name
  total+=p.stat().st_size
  if i%2000==0:print(json.dumps({'files_hashed':i}),flush=True)
 m=read(HERE/'integration/related-talent-icons-v56/input-map.json')
 added=sorted(set(new)-set(old));removed=sorted(set(old)-set(new));changed=sorted(k for k in set(new)&set(old) if new[k]!=old[k])
 assert len(actual)==10205
 assert set(added)=={e['route'].lstrip('/') for e in m['entries']} and len(added)==18 and not removed
 assert set(changed)=={'__offline/related-talent-icons.json','__offline/route-map.json','__offline/pages_runtime.js','export-provenance.json'},changed
 for e in m['entries']:assert new[e['route'].lstrip('/')]==(e['sha256'],e['length'])
 om,nm=read(OLD/'__offline/route-map.json'),read(NEW/'__offline/route-map.json')
 assert nm['aliases']==om['aliases']
 extra={e['route']:'/WOW-Encyclopedia-Deployable-Archive'+e['route'] for e in m['entries']}
 assert nm['routes']=={**om['routes'],**extra}
 def without_routes(p):return re.sub(r'    var routes = \{[^\n]+\};','    var routes = __ROUTES__;',p.read_text(encoding='utf-8'),count=1)
 assert without_routes(OLD/'__offline/pages_runtime.js')==without_routes(NEW/'__offline/pages_runtime.js')
 oc,nc=read(OLD/'__offline/related-talent-icons.json'),read(NEW/'__offline/related-talent-icons.json')
 assert nc['mappings'][:20]==oc['mappings']
 assert nc['assets'][:1006]==oc['assets'] and len(nc['mappings'])==38 and nc['icon_count']==1024
 assert newdoc['source_manifest_sha256']==olddoc['source_manifest_sha256']
 assert newdoc['related_talent_icons']['icon_count']==1024
 # Final online verification starts from independently verified v55.
 base=old
 online_changes=sorted(k for k in new if k not in base or new[k]!=base[k]);assert not(set(base)-set(new))
 objects=[{'path':p,'sha256':new[p][0],'bytes':new[p][1]} for p in sorted(added+changed)]
 result={'schema':'wow-root-v56-export-acceptance/v1','accepted':True,'started_utc':started,'checked_utc':datetime.now(timezone.utc).isoformat(),
  'local_site':NEW.relative_to(ROOT).as_posix(),'actual_files':len(actual),'declared_files':len(newdoc['files']),'total_bytes':total,
  'all_actual_file_hashes_match_provenance':True,'prior_actual_tree_hash_check_reused':'root-v55-export-acceptance.json',
  'all_prior_image_bytes_retained':True,'all_2008_talent_data_bytes_retained':True,'existing_runtime_logic_unchanged_except_route_data':True,
  'added':added,'changed':changed,'removed':removed,'objects':objects,'new_mapped_icons':18,'new_original_2008_images':0,
  'export_provenance_sha256':new['export-provenance.json'][0],'disk_free_after_bytes':shutil.disk_usage(ROOT).free,
  'online_changes_from_v55':[{'path':p,'sha256':new[p][0],'bytes':new[p][1]} for p in online_changes],'browser_acceptance_pending':True}
 out=HERE/'root-v56-export-acceptance.json';assert not out.exists()
 out.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
 print(json.dumps({'accepted':True,'actual_files':len(actual),'added':len(added),'changed':len(changed),'online_changes_from_v55':len(online_changes)}))
if __name__=='__main__':main()

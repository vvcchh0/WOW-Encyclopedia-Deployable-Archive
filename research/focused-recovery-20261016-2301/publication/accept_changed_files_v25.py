import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;S=R/'.scratch/pages-resources-20261016-v25';P=R/'.scratch/pages-resources-20261016-v24';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 new=read(S/'export-provenance.json');old=read(P/'export-provenance.json');worker=read(O.parent/'local/worker-build-v25.json');assert worker['export_completed'] and worker['postbuild']['actual_files']==8642
 a={x['output_path']:x for x in old['files']};b={x['output_path']:x for x in new['files']};assert len(b)==8641 and set(a)<=set(b) and len(set(b)-set(a))==4
 allowed={'__offline/route-map.json','__offline/pages_runtime.js','__offline/related-images/index.html'};routes={x['route']:x for x in old['files']}
 for g in old['guide_image_collections']['groups']:allowed.update(routes[g[k]]['output_path'] for k in ['guide_route','gallery_route'])
 checked=[]
 for p,x in b.items():
  if p in a and a[p]['derived_sha256']==x['derived_sha256'] and a[p]['derived_length']==x['derived_length']:continue
  assert p not in a or p in allowed,p
  file=S/p;assert sha(file)==x['derived_sha256'] and file.stat().st_size==x['derived_length'];checked.append(p)
 for p,x in a.items():
  if x.get('role')=='image_overlay':assert b[p]==x,p
 assert new['stats']['image_overlay_records']==183 and new['guide_image_collections']['image_count']==35
 assert sha(P/'export-provenance.json')=='0d1a392e5be8f5eae71b8ca6bf73f5473331357c6f99f9ac60e79b6d07dec3d0'
 assert shutil.disk_usage(R).free>=11005853696
 d={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'declared_files':8641,'actual_files':8642,'provenance_records_compared':len(b),'prior179_overlay_metadata_preserved':True,'changed_files_rehashed':checked,'all_unchanged_files_rehashed':False,'export_provenance_sha256':sha(S/'export-provenance.json'),'scope':'All provenance records compared; actual bytes of every changed/new declared file rehashed. Unchanged files reuse frozen source and unchanged exporter write/hash evidence plus worker count. Earlier exhaustive reread stopped to honor40min budget.','network_requests':0}
 out=O/'root-v25-export-acceptance.json';assert not out.exists();out.write_bytes((json.dumps(d,indent=2)+'\n').encode());print(json.dumps(d))

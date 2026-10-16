"""Check whether the nine known index digests already occur in local images."""
import base64,hashlib,json,time
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];S=R/'.scratch/pages-resources-20261016-v24';O=Path(__file__).resolve().parent/'existing-neighbor-digest-matches.json'
if __name__=='__main__':
 assert not O.exists();started=time.monotonic()
 q=json.loads((R/'research/continuous-recovery-20261016/local-audit/final-v24-pending/public-summary.json').read_bytes())['pending_priorities']['gallery_neighbors']['items']
 wanted={d for x in q for d in x['positive_digests']};p=json.loads((S/'export-provenance.json').read_bytes());matches=[];checked=0;total=0;complete=True
 for x in p['files']:
  if not x.get('mime','').startswith('image/'):continue
  if time.monotonic()-started>75:complete=False;break
  data=(S/x['output_path']).read_bytes();assert len(data)==x['derived_length'] and hashlib.sha256(data).hexdigest()==x['derived_sha256']
  digest=base64.b32encode(hashlib.sha1(data).digest()).decode().rstrip('=');checked+=1;total+=len(data)
  if digest in wanted:matches.append({'existing_route':x['route'],'existing_source':x.get('source_path'),'sha256':x['derived_sha256'],'length':len(data),'cdx_digest':digest,'pending_originals':[z['original'] for z in q if digest in z['positive_digests']]})
 result={'checked_utc':datetime.now(timezone.utc).isoformat(),'network_requests':0,'complete':complete,'images_checked':checked,'bytes_read':total,'elapsed_seconds':time.monotonic()-started,'matches':matches,'scope':'Byte/digest reuse candidates only. No new original URL acquisition or deployment inferred.'}
 O.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))

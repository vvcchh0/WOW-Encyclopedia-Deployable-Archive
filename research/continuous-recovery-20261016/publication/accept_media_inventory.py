"""Independent saved-CDX classification and existing-payload exclusion."""
import base64,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[3]
B=R/'research/continuous-recovery-20261016'

def main():
    audit_path=B/'local-audit/media-candidates/media-candidates-audit.json'
    audit=json.loads(audit_path.read_bytes())
    rows=[];sources=[]
    for s in audit['raw_sources']['sources']:
        data=(R/s['path']).read_bytes()
        assert len(data)==s['bytes'] and hashlib.sha256(data).hexdigest()==s['sha256']
        p=json.loads(data)
        assert set(['original','timestamp','statuscode','mimetype','digest','length']).issubset(p[0])
        rr=[dict(zip(p[0],v)) for v in p[1:] if isinstance(v,list) and len(v)==len(p[0])]
        assert len(rr)==s['data_rows']
        sources.append({'path':s['path'],'sha256':s['sha256'],'rows':len(rr)})
        rows+=rr
    categories=Counter();times=Counter()
    for r in rows:
        status,mime=r['statuscode'],r['mimetype']
        category=('redirect' if status in ('301','302','303','307','308') else
                  'archive_404' if status=='404' else 'revisit' if mime=='warc/revisit' else
                  'valid_status200_image_index_row' if status=='200' and mime.startswith('image/') else
                  'status200_non_image' if status=='200' else 'other')
        categories[category]+=1
        t=r['timestamp'];times['pre_2008' if t<'20080101000000' else 'baseline_le_anchor' if t<='20080512210044' else 'late_2008' if t<='20081231235959' else 'post_2008']+=1
    assert len(rows)==2082 and dict(categories)==audit['row_accounting']['raw_category_counts']
    assert dict(times)==audit['row_accounting']['raw_temporal_bucket_counts']
    valid=[r for r in rows if r['statuscode']=='200' and r['mimetype'].startswith('image/')]
    assert len(valid)==2
    provenance=json.loads((R/'.scratch/pages-resources-20261016-v17/export-provenance.json').read_bytes())
    accepted=[]
    for item in audit['known_accepted_late_payloads']['items']:
        row=next(r for r in valid if r['original']==item['original'] and r['timestamp']==item['actual_timestamp'])
        data=(R/item['local_path']).read_bytes()
        assert len(data)==item['length'] and hashlib.sha256(data).hexdigest()==item['sha256']
        digest=base64.b32encode(hashlib.sha1(data).digest()).decode().rstrip('=')
        assert digest==row['digest']
        f=next(f for f in provenance['files'] if f.get('original_url')==row['original'])
        assert f['derived_sha256']==item['sha256'] and f['actual_capture_timestamp']==row['timestamp']
        with Image.open(R/item['local_path']) as im: im.load();assert list(im.size)==item['dimensions']
        accepted.append({'original':row['original'],'actual_capture_timestamp':row['timestamp'],'sha256':item['sha256'],'bytes':len(data),'already_present':True})
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'audit_sha256':hashlib.sha256(audit_path.read_bytes()).hexdigest(),
            'raw_rows':len(rows),'category_counts':dict(categories),'temporal_counts':dict(times),'valid_image_rows':2,
            'new_candidates':0,'known_payloads':accepted,'source_bindings':sources,
            'scope':'Saved MEDIA/SSOTD prefix pages only. Redirect and revisit rows are not new recovered images.'}
    (B/'publication/root-media-inventory-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_bindings','known_payloads')}))

if __name__=='__main__':main()

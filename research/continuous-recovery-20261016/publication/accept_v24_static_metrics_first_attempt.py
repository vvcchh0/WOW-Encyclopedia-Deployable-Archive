"""Recount the same static placeholder scope after the v24 guide additions."""
import hashlib,html,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
from accept_static_resource_inventory import normalize
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def scan(site):
    counter=Counter();news=Counter();files={};allmarkers=0
    for p in site.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(site).as_posix()
        if rel.startswith('_origins/') or p.suffix.lower() not in ('.html','.htm','.xml','.css'):continue
        files[rel]=sha(p)
        for m in re.finditer(r'missing-image\.svg\?([^\"\'<>\s\)]*)',p.read_text(encoding='utf-8',errors='replace'),re.I):
            allmarkers+=1;u=parse_qs(html.unescape(m.group(1)),keep_blank_values=True).get('requested',[''])[0];s=urlsplit(u)
            if s.scheme not in ('http','https') or Path(s.path.lower()).suffix not in ('.gif','.jpg','.jpeg','.png','.webp','.svg','.bmp'):continue
            key=normalize(u);counter[key]+=1
            if rel.startswith('news/'):news[key]+=1
    return files,counter,news,allmarkers
def main():
    out=O/'root-v24-static-metrics-acceptance.json';assert not out.exists()
    old=R/'.scratch/pages-resources-20261016-v23';site=R/'.scratch/pages-resources-20261016-v24';a,b,n,z=scan(old);c,d,m,y=scan(site)
    assert set(a)==set(c) and len(a)==1104 and sum(n.values())==574 and sum(m.values())<=557
    assert not(set(d)-set(b));assert all(d[k]<=b[k] for k in d)
    news_paths=[p for p in a if p.startswith('news/')];assert all(a[p]==c[p] for p in news_paths)
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'static_text_files':len(c),'prior_version':'v23','current_version':'v24','prior_unique_missing_images':len(b),'current_unique_missing_images':len(d),'prior_missing_occurrences':sum(b.values()),'current_missing_occurrences':sum(d.values()),'removed_occurrences':sum(b.values())-sum(d.values()),'current_news_missing_occurrences':sum(m.values()),'current_news_unique_missing_images':len(m),'news_files_checked':len(news_paths),'changed_news_files':sum(a[p]!=c[p] for p in news_paths),'all_placeholder_markers':y,'export_provenance_sha256':sha(site/'export-provenance.json'),'scope':'Fixed1104 HTML/HTM/XML/CSS files excluding _origins, static image placeholders only;3368 JavaScript gallery entities separately audited.'}
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()

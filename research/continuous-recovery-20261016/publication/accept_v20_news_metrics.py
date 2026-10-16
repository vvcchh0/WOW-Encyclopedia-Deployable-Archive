"""Count the same forty news surfaces before and after twenty-four accepted image additions."""
import html,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from accept_static_resource_inventory import normalize
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016'
def scan(site):
    audit=json.loads((B/'local-audit/v17-news/v17-news-audit.json').read_bytes())
    prior=R/'.scratch/pages-resources-20261016-v17'
    paths=[site/(R/page['v17_output']).relative_to(prior) for page in audit['page_results']]
    counts=Counter()
    for p in paths:
        for m in re.finditer(r'missing-image\.svg\?([^\"\'<>\s\)]*)',p.read_text(encoding='utf-8')):
            u=parse_qs(html.unescape(m.group(1))).get('requested',[''])[0]
            if urlsplit(u).scheme in ('http','https') and Path(urlsplit(u).path.lower()).suffix in ('.gif','.jpg','.jpeg','.png','.webp','.svg','.bmp'):
                counts[normalize(u)]+=1
    return paths,counts
def main():
    p,a=scan(R/'.scratch/pages-resources-20261016-v19');q,c=scan(R/'.scratch/pages-resources-20261016-v20')
    observed={'pages_prior':len(p),'pages_current':len(q),'occurrences_prior':sum(a.values()),'occurrences_current':sum(c.values()),'entities_prior':len(a),'entities_current':len(c)}
    assert len(p)==len(q)==40 and sum(a.values())==614 and len(a)==606,observed
    images=[]
    for n in ['root-aug20-source-acceptance.json','root-aug-remaining15-source-acceptance.json']:
        images.extend(json.loads((B/'publication'/n).read_bytes())['accepted_images'])
    removed=[{'original':x['original'],'before':a[normalize(x['original'])],'after':c[normalize(x['original'])]} for x in images]
    assert len(images)==24 and all(x['before']>0 and x['after']==0 for x in removed)
    assert sum(a.values())-sum(c.values())==sum(x['before'] for x in removed)
    assert len(c)==len(a)-24
    assert not(set(c)-set(a))
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'news_surfaces':40,'prior_missing_occurrences':sum(a.values()),'current_missing_occurrences':sum(c.values()),'removed_occurrences':sum(a.values())-sum(c.values()),'prior_unique_missing_images':len(a),'current_unique_missing_images':len(c),'new_source_images':24,'targets':removed,'scope':'The same forty news pages, static placeholders only; origin identity normalizes default ports. Dynamic gallery targets remain separate.'}
    assert not (B/'publication/root-v20-news-metrics-acceptance.json').exists()
    (B/'publication/root-v20-news-metrics-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items() if k!='targets'}))
if __name__=='__main__':main()

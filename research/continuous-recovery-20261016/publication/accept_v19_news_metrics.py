"""Count the same forty news surfaces before and after ten accepted image additions."""
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
    p,a=scan(R/'.scratch/pages-resources-20261016-v18');q,c=scan(R/'.scratch/pages-resources-20261016-v19')
    observed={'pages_prior':len(p),'pages_current':len(q),'occurrences_prior':sum(a.values()),'occurrences_current':sum(c.values()),'entities_prior':len(a),'entities_current':len(c)}
    assert observed=={'pages_prior':40,'pages_current':40,'occurrences_prior':798,'occurrences_current':614,'entities_prior':616,'entities_current':606},observed
    images=[]
    for n in ['root-news-shared10-source-acceptance.json','root-news-shared13-source-acceptance.json']:
        images.extend(json.loads((B/'publication'/n).read_bytes())['accepted_images'])
    removed=[{'original':x['original'],'before':a[normalize(x['original'])],'after':c[normalize(x['original'])]} for x in images]
    assert sum(x['before'] for x in removed)==184 and all(x['after']==0 for x in removed)
    assert not(set(c)-set(a))
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'news_surfaces':40,'prior_missing_occurrences':798,'current_missing_occurrences':614,'removed_occurrences':184,'prior_unique_missing_images':616,'current_unique_missing_images':606,'new_source_images':10,'targets':removed,'scope':'The same forty news pages, static placeholders only; origin identity normalizes default ports. Dynamic gallery targets remain separate.'}
    (B/'publication/root-v19-news-metrics-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items() if k!='targets'}))
if __name__=='__main__':main()

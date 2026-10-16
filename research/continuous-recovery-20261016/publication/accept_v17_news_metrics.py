"""Root recount of the same forty output pages and twenty repaired URLs."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs,unquote,urlsplit
import hashlib,html,json,re
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
def main():
    path=ROOT/'research/continuous-recovery-20261016/local-audit/v17-news/v17-news-audit.json'
    audit=json.loads(path.read_bytes())
    assert len(audit['page_results'])==40
    counts={'v16':Counter(),'v17':Counter()}
    for page in audit['page_results']:
        for version in counts:
            data=(ROOT/page[version+'_output']).read_bytes()
            assert hashlib.sha256(data).hexdigest()==page[version+'_output_sha256']
            for query in re.findall(r'missing-image\.svg\?([^\"\'<>\s)]+)',data.decode('utf-8'),re.I):
                requested=unquote(parse_qs(html.unescape(query),keep_blank_values=True).get('requested',[''])[0])
                if re.match(r'^https?://',requested,re.I) and urlsplit(requested).path.lower().endswith(('.jpg','.jpeg','.gif','.png')):
                    counts[version][requested]+=1
    assert sum(counts['v16'].values())==954 and sum(counts['v17'].values())==798
    mapping=json.loads((ROOT/'research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json').read_bytes())
    expected={item['logical_url'] for item in mapping['items']}
    removed=counts['v16']-counts['v17']
    assert set(removed)==expected and len(expected)==20
    assert sum(removed.values())==156 and not counts['v17']-counts['v16']
    assert all(counts['v17'][url]==0 for url in expected)
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'pages':40,
        'v16_missing_occurrences':954,'v17_missing_occurrences':798,'removed_occurrences':156,
        'repaired_original_urls':20,'new_missing_urls':0,'guide_previews_excluded':True,
        'worker_audit_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (OUT/'root-v17-news-metrics-acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()

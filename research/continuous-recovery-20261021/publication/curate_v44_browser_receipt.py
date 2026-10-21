"""Publish concise observations while retaining the 29 MB repeated DOM log locally."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261021/local-audit/v44'
SOURCE = BASE / 'v44-browser-receipt.json'
OUT = BASE / 'v44-browser-summary.json'
assert not OUT.exists()
raw = json.loads(SOURCE.read_bytes())
pages = []
for row in raw['pages']:
    item = {k:row.get(k) for k in ('id','kind','path','class_name','status','navigation_error',
                                 'page_errors','failed_requests','blocked_non_loopback_requests')}
    if row['kind']=='talent':
        item['states'] = {}
        for state in ('initial','after_add','after_reset','after_reopen','after_refresh'):
            evidence = row[state]['talent']
            item['states'][state] = {k:evidence.get(k) for k in ('rank_points','available','spent','talent_nodes')}
        assert item['states']['initial']['rank_points']==61
        assert int(item['states']['after_add']['spent'])>0
        assert int(item['states']['after_reset']['spent'])==0
        assert int(item['states']['after_reopen']['spent'])>0
        assert int(item['states']['after_refresh']['spent'])>0
        item['saved_template_nonzero'] = row['saved_template']['nonzero_code']
    pages.append(item)
receipt = {
    'schema':'wow-browser-observation-summary/v1','version':'v44',
    'started_utc':raw['started_at_utc'],'finished_utc':raw['finished_at_utc'],
    'actual_browser_pages':len(pages),'observations':pages,
    'raw_dom_log':{'path':SOURCE.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                   'bytes':SOURCE.stat().st_size,'publication':'retained locally; repeated per-image DOM omitted'},
    'missing_target_union':'Use v44-gap-union-reconciliation.json: 273 distinct targets, including 27 dynamic backgrounds.',
    'publication_status':'The v44 candidate was not published due to contest-anchor markup; identical talent pages are carried into accepted v45.',
}
OUT.write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print(json.dumps({'public_summary_bytes':OUT.stat().st_size,'local_raw_bytes':SOURCE.stat().st_size}))

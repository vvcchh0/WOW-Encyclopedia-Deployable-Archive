"""Independently reconcile the four observed source responses with the parent GO."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BATCH = HERE / 'network/archivecraft-dungeons01'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    gate = read(HERE / 'root-archivecraft-dungeons01-go.json')
    plan = read(BATCH / 'plan.json')
    report = read(BATCH / 'runtime/private/report.json')
    public = read(BATCH / 'runtime/public-inventory.json')
    for key, name in [('plan_sha256','plan.json'),('runner_sha256','archivecraft_dungeons01.py'),('fixture_sha256','fixture-results.json')]:
        assert gate[key] == sha(BATCH/name), name
    assert gate['accepted'] and report['stop_reason'] == 'completed' and public['complete']
    assert len(report['attempts']) == len(public['records']) == len(plan['targets']) == 4
    rows = []
    for expected, record, item in zip(plan['targets'],report['attempts'],public['records']):
        assert record['url'] == item['url'] == expected['url']
        assert record['http_status'] == item['http_status'] == 200
        assert record['returncode'] == 0 and record['transport'] == 'direct'
        assert not any(record[k] for k in ('timed_out','transport_failed','response_cap_exceeded'))
        assert record['header_parse']['location'] is None and item['valid']
        assert item['classification'] == 'accepted_html'
        assert record['disk_free_after_bytes'] >= 11005853696
        p = (ROOT/record['body_path']).resolve()
        assert p.is_relative_to(ROOT) and p.stat().st_size == item['body_bytes'] == record['body_bytes']
        assert sha(p) == item['body_sha256'] == record['body_sha256']
        text = p.read_text(encoding='utf-8')
        assert '</html>' in text.lower() and item['title'] in html.unescape(text)
        interval = record['actual_start_interval_seconds']
        assert interval is None or interval >= 5
        rows.append({k:item[k] for k in ('url','title','request_started_utc','request_finished_utc','body_bytes','body_sha256','http_status','transport')})
    receipt = {'schema':'wow-root-dungeon-pages-source-acceptance/v1','accepted':True,
       'checked_utc':datetime.now(timezone.utc).isoformat(),'scope':'Four current ArchiveCraft HTML sources; no image payload or original capture accepted here.',
       'pages':rows,'request_attempts':4,'total_response_bytes':sum(r['body_bytes'] for r in rows),
       'minimum_start_interval_seconds':min(r['actual_start_interval_seconds'] for r in report['attempts'][1:]),
       'disk_free_bytes':shutil.disk_usage(ROOT).free,'raw_http_private':True,
       'public_inventory_sha256':sha(BATCH/'runtime/public-inventory.json'),
       'caption_extraction_boundary':'WordPress dl/dd captions require a separate local audit; no caption-completeness claim.',
       'wayback_resume_gate_passed':False,'images_downloaded':0,'images_recovered':0}
    assert receipt['disk_free_bytes'] >= 11005853696
    (HERE/'root-archivecraft-dungeons01-source-acceptance.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'accepted':True,'pages':4,'bytes':receipt['total_response_bytes'],'minimum_interval_seconds':receipt['minimum_start_interval_seconds']}))

if __name__ == '__main__': main()

"""Carry forward the resource ledger and update only accepted page evidence."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'research/continuous-recovery-20261016'
AUDIT_PATH = ROOT / 'research/focused-recovery-20261015-2303/integration/root-sidebar-check.json'
ONLINE_PATH = OUT / 'publication/root-pages-online-acceptance.json'
PRIOR_PATH = ROOT / 'research/continuous-recovery-20261015/ledger.current.json'

def read(path):
    return json.loads(path.read_bytes())

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def relative(path):
    return path.relative_to(ROOT).as_posix()

def main():
    online, audit = read(ONLINE_PATH), read(AUDIT_PATH)
    if not online['accepted'] or not audit['accepted']:
        raise RuntimeError('unaccepted page evidence')
    prior_bytes = PRIOR_PATH.read_bytes()
    ledger = json.loads(prior_bytes)
    records = {x['record_id']: x for x in audit['records']}
    before_resources = Counter(x['resource_status'] for x in ledger['items'])
    before_interactions = Counter(x['interaction_status'] for x in ledger['items'])
    now = datetime.now(timezone.utc).isoformat()
    site = '.scratch/pages-resources-20261015-v15'
    for item in ledger['items']:
        record = records[item['audit_record_id']]
        if item['normalized_route'] != record['normalized_route']:
            raise RuntimeError('menu identity mismatch')
        item['page_status'] = record['status']
        item['page_validation_preview'] = site
        item['page_validation_evidence'] = {'path': relative(AUDIT_PATH), 'record_id': record['record_id'],
            'route_map_sha256': audit['route_map_sha256'], 'actual_file_bytes_evidence': 'research/continuous-recovery-20261016/publication/v15-publication-binding.json',
            'scope': 'Page route and exact file only. Historical resource/interaction fields retained.'}
        if item['normalized_route'] == '/news/rss-08-2007.xml':
            item['local_recovery_candidate']['published'] = True
            item['local_recovery_candidate']['online_acceptance'] = relative(ONLINE_PATH)
            item['next_action'] = '八月50条新闻已上线；后续继续新闻配图审计和资源补齐。'
            item['task_ids'].append('PUBLISH15')
    if before_resources != Counter(x['resource_status'] for x in ledger['items']) or before_interactions != Counter(x['interaction_status'] for x in ledger['items']):
        raise RuntimeError('Unintended resource/interaction rewrite')
    counts = dict(Counter(x['page_status'] for x in ledger['items']))
    if counts != audit['status_counts'] or len(ledger['items']) != 1241:
        raise RuntimeError('Page count conservation')
    ledger.update({'generated_utc': now, 'deadline_utc': '2026-10-16T14:01:49Z', 'current_preview': site,
        'published_accepted_preview': site, 'published_accepted_pages_commit': online['expected_pages_commit'],
        'previous_accepted_ledger': {'path': relative(PRIOR_PATH), 'sha256': hashlib.sha256(prior_bytes).hexdigest(), 'version': 'v14 published plus local v15 candidate'},
        'current_audit_acceptance': relative(AUDIT_PATH),
        'page_validation_version': 'v15 full local menu route/file audit; frozen bytes rebound and 8 key public objects verified',
        'published_accepted_evidence': {'binding': 'research/continuous-recovery-20261016/publication/v15-publication-binding.json', 'pages': relative(ONLINE_PATH), 'browser': 'research/focused-recovery-20261015-2303/integration/root-browser-acceptance.json'},
        'status_note': 'Published v15: August2007 50articles restored.1107 content observations/483 files, zero missing sidebar page routes. Image and interaction fields remain mixed prior audits and are not resource completeness claims.'})
    summary = ledger['summary']
    summary.update({'page_status_counts': counts, 'distinct_missing_routes': 0, 'resolved_distinct_files': 483,
        'page_observations_resolved': 1107, 'page_missing_observations': 0})
    ledger['published_preview_history'].append({'version': 'v15', 'preview': site, 'pages_commit': online['expected_pages_commit'], 'accepted_utc': now, 'evidence': relative(ONLINE_PATH)})
    write(OUT / 'ledger.current.json', ledger)
    status = read(OUT / 'status.json')
    status.update({'updated_utc': now, 'phase': 'resource_recovery', 'published_pages': {'version': 'v15', 'commit': online['expected_pages_commit'], 'acceptance': relative(ONLINE_PATH)},
        'current_ledger': 'research/continuous-recovery-20261016/ledger.current.json', 'notes': ['v15 published and 8 online objects verified.', 'Portable Release remains v14 pending a later stable checkpoint.', 'Resource and interaction ledger fields retain their original audit versions.']})
    write(OUT / 'status.json', status)
    tasks = read(OUT / 'tasks.json')
    tasks['updated_utc'] = now
    for task in tasks['tasks']:
        if task['id'] == 'PUBLISH15':
            task.update({'status': 'accepted', 'result': {'commit': online['expected_pages_commit'], 'objects_verified': 8, 'evidence': relative(ONLINE_PATH)}})
        if task['id'] == 'NETWORK01-PLAN':
            task.update({'status': 'bounded_execution_authorized', 'goal': 'Q1/Q2/Q8 exact CDX queries only, maximum6attempts/6minutes; no replays', 'network': True})
    write(OUT / 'tasks.json', tasks)
    proof = {'checked_utc': now, 'accepted': True, 'observations': len(ledger['items']), 'page_status_counts': counts,
        'resource_fields_unchanged': True, 'interaction_fields_unchanged': True, 'previous_ledger_sha256': hashlib.sha256(prior_bytes).hexdigest(),
        'ledger_sha256': hashlib.sha256((OUT / 'ledger.current.json').read_bytes()).hexdigest()}
    write(OUT / 'publication/v15-ledger-acceptance.json', proof)
    print(json.dumps(proof))

if __name__ == '__main__':
    main()

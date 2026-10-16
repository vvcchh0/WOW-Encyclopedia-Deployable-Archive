"""Independently merge the three Karazhan reports and verify the entity join."""
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261016'

def load(relative):
    return json.loads((ROOT / relative).read_bytes())

def actual_404(hops, base):
    for hop in hops:
        relative = hop.get('headers_path') or hop.get('raw', {}).get('headers')
        if not relative:
            continue
        data = (base / relative).read_bytes()
        statuses = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})[^\r\n]*', data)
        if statuses and statuses[-1] == b'404':
            return True
    return False

def main():
    errors = []
    old_path = 'research/karazhan-recheck-20261015/batch-report.final.json'
    mid_path = 'research/continuous-recovery-20261015/wayback-karazhan-batch1/batch-report.json'
    late_path = 'research/focused-recovery-20261015-2303/network/gallery23/batch-report.json'
    old, mid, late = load(old_path), load(mid_path), load(late_path)
    merged = {x['original_url']: ('archive_404' if x['category'] == '404_wayback_not_archived' else 'transport_unknown') for x in old['results']}
    old_counts = dict(Counter(merged.values()))
    mid_updates = late_updates = 0
    for item in mid['results']:
        if item['category'] != 'not_archived':
            continue
        original = item['original_url']
        if not actual_404(item['hops'], (ROOT / mid_path).parent):
            errors.append('mid_actual_404:' + original)
        if merged[original] != 'archive_404':
            mid_updates += 1
        merged[original] = 'archive_404'
    for item in late['results']:
        if item['kind'] != 'karazhan':
            continue
        headers = (ROOT / late_path).parent / item['validation']['raw_headers_path']
        statuses = re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})[^\r\n]*', headers.read_bytes())
        if not statuses or statuses[-1] != b'404':
            errors.append('late_actual_404:' + item['url'])
        if merged[item['url']] != 'archive_404':
            late_updates += 1
        merged[item['url']] = 'archive_404'
    audited = load('research/continuous-recovery-20261016/local-audit/v2/karazhan-126-item-audit-v2.json')
    candidate = {x['original_url']: x['global_category'] for x in audited['items']}
    if merged != candidate:
        errors.append('126_item_join')
    full = load('research/continuous-recovery-20261016/local-audit/v2/gallery-direct-entity-audit-v2.json')
    seen = set()
    for item in full['entities']:
        original = item['original_url']
        if original in merged:
            seen.add(original)
            if item['status'] != merged[original]:
                errors.append('3368_karazhan_join:' + original)
        elif item['status'] != 'never_requested':
            errors.append('other_gallery_classification:' + original)
    counts = dict(Counter(merged.values()))
    direct_counts = dict(Counter(x['status'] for x in full['entities']))
    if len(merged) != 126 or len(seen) != 126 or len(full['entities']) != 3368 or mid_updates != 14 or late_updates != 6:
        errors.append('count_conservation')
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'accepted': not errors,
        'scope': '126 exact URLs merged across the supplied three reports; other3368 inventory states mean no entity request in these reviewed reports, not a global assertion about all historical requests.',
        'base_counts': old_counts, 'new_mid_404': mid_updates, 'new_late_404': late_updates,
        'karazhan_counts': counts, 'direct_entity_count': len(full['entities']), 'direct_counts': direct_counts,
        'karazhan_join_count': len(seen), 'new_404_headers_independently_read': mid_updates + late_updates,
        'input_bindings': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [old_path, mid_path, late_path,
            'research/continuous-recovery-20261016/local-audit/v2/karazhan-126-item-audit-v2.json',
            'research/continuous-recovery-20261016/local-audit/v2/gallery-direct-entity-audit-v2.json',
            'research/continuous-recovery-20261016/local-audit/v3/supplement-classification-v3.json']},
        'errors': errors}
    (RUN / 'publication/root-gallery-audit-acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

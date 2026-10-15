"""Independent source retention and selected-entity acceptance for v13."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/v13-integration'
SELECTION_SHA = 'e3af3c2c9cb8c40b96bd5a6964d32faac92d4a2e6da158bcb34ad9b59313c591'
FROZEN_SHA = '397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def main():
    old = read_json('.scratch/offline-navigation-20261015-v12/build-manifest.json')
    manifest_path = ROOT / '.scratch/offline-navigation-20261015-v13/build-manifest.json'
    manifest_bytes = manifest_path.read_bytes()
    new = json.loads(manifest_bytes)
    selection_path = ROOT / 'research/continuous-recovery-20261015/selected-rss18-source-map.json'
    selection_bytes = selection_path.read_bytes()
    selected = json.loads(selection_bytes)['entries']
    before = {x['route']: x for x in old['files']}
    after = {x['route']: x for x in new['files']}
    errors, relocations, entities = [], [], []
    if digest(selection_bytes) != SELECTION_SHA:
        errors.append({'reason': 'selection_changed'})
    if len(before) != len(old['files']) or len(after) != len(new['files']):
        errors.append({'reason': 'duplicate_source_route'})
    for route, prior in before.items():
        current = after.get(route)
        if current is None:
            errors.append({'route': route, 'reason': 'prior_source_missing'})
            continue
        keys = {key for key in prior if key.startswith(('source_', 'actual_', 'origin', 'temporal_'))}
        keys.update({'route', 'kind', 'mime', 'role'})
        changed = sorted(key for key in keys if prior.get(key) != current.get(key))
        if changed == ['source_local_path'] and route in {'/__offline/compat.css', '/__offline/compat.js'}:
            a = (ROOT / prior['source_local_path']).read_bytes()
            b = (ROOT / current['source_local_path']).read_bytes()
            if a == b and digest(b) == current['source_sha256']:
                relocations.append({'route': route, 'bytes': len(b), 'sha256': digest(b), 'content_identical': True})
                changed = []
        if changed:
            errors.append({'route': route, 'reason': 'prior_source_changed', 'fields': changed})
    aliases_changed = [key for key, value in old['route_aliases'].items() if new['route_aliases'].get(key) != value]
    if aliases_changed:
        errors.append({'reason': 'prior_alias_changed', 'routes': aliases_changed})
    for item in selected:
        source = (ROOT / item['local_path']).read_bytes()
        matched = [entry for entry in new['files'] if entry.get('source_local_path') == item['local_path']]
        if len(matched) != 1:
            errors.append({'reason': 'selected_mapping_count', 'path': item['local_path'], 'count': len(matched)})
            continue
        entry = matched[0]
        derived_data = (ROOT / entry['output_path']).read_bytes()
        capture = datetime.strptime(entry['actual_timestamp'], '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
        expected = datetime.fromisoformat(item['actual_memento'].replace('Z', '+00:00'))
        check = {
            'route': entry['route'], 'original_url': item['query_original_url'],
            'actual_timestamp': entry['actual_timestamp'], 'bytes': len(source), 'sha256': digest(source),
            'selected_derived_matches': len(derived_data) == entry['derived_length'] and digest(derived_data) == entry['derived_sha256'],
            'selected_body_matches': len(source) == item['body_bytes'] and digest(source) == item['body_sha256'],
            'manifest_source_matches': len(source) == entry['source_length'] and digest(source) == entry['source_sha256'],
            'capture_matches': capture == expected and entry['actual_timestamp'] == item['actual_timestamp'],
            'pre_anchor': capture < datetime(2008, 5, 12, 21, 0, 44, tzinfo=timezone.utc),
        }
        entities.append(check)
        if not all(check[key] for key in ['selected_body_matches', 'selected_derived_matches', 'manifest_source_matches', 'capture_matches', 'pre_anchor']):
            errors.append({'route': entry['route'], 'reason': 'selected_entity_mismatch'})
    if len(before) != 8344 or len(after) != 8347 or len(selected) != 3 or len(entities) != 3:
        errors.append({'reason': 'source_counts'})
    if set(after) - set(before) != {entry['route'] for entry in entities}:
        errors.append({'reason': 'new_routes_do_not_equal_frozen_selection'})
    frozen = digest((ROOT / 'offline/build-manifest.json').read_bytes())
    if frozen != FROZEN_SHA:
        errors.append({'reason': 'frozen_manifest_changed'})
    report = {
        'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
        'accepted': not errors, 'old_source_count': len(before), 'new_source_count': len(after),
        'old_aliases_checked': len(old['route_aliases']), 'old_aliases_changed': aliases_changed,
        'manifest_sha256': digest(manifest_bytes), 'selection_sha256': digest(selection_bytes),
        'new_routes': sorted(set(after) - set(before)), 'identical_generated_support_relocations': relocations,
        'selected_derived_files_read': len(entities),
        'source_full_byte_verification': 'Required in following root exporter: each declared input is hash/length checked before transformation.',
        'selected_entity_checks': entities, 'frozen_manifest_sha256': frozen, 'errors': errors,
        'scope': 'Source metadata retention, all old aliases, identical support relocation, and three actual raw/derived additions only. Full input bytes are subsequently verified by exporter; final export is independently checked.'
    }
    (OUT / 'root-source-acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['accepted', 'old_source_count', 'new_source_count', 'selected_derived_files_read', 'errors']}))
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

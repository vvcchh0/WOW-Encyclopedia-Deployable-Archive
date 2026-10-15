"""Recheck conserved v9 menu identities against the accepted v10 route map."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/v10-integration'
SITE = ROOT / '.scratch/pages-resources-20261015-v10'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    prior_path = ROOT / 'research/continuous-recovery-20261015/v9-audit/audit.json'
    prior_bytes = prior_path.read_bytes()
    prior = json.loads(prior_bytes)
    routes_bytes = (SITE / '__offline/route-map.json').read_bytes()
    routes = json.loads(routes_bytes)
    prefix = routes['base_path']
    provenance = json.loads((SITE / 'export-provenance.json').read_text(encoding='utf-8'))
    files = {x['output_path']: x for x in provenance['files']}
    records, errors, recovered, remaining = [], [], [], []
    checked_files = {}
    for old in prior['records']:
        route = old.get('normalized_route')
        status = old['current_page_status']
        target = routes['routes'].get(route) or routes['aliases'].get(route)
        row = {key: old.get(key) for key in ['record_id', 'source_menu', 'menu_id', 'label', 'href', 'normalized_route', 'effective_in_scope']}
        row['prior_status'] = status
        if old['effective_in_scope'] and status.startswith(('resolved', 'missing_export')):
            if not target:
                row['status'] = 'missing_export_route'
                remaining.append(row)
                if status.startswith('resolved'):
                    errors.append({'record_id': old['record_id'], 'reason': 'prior_resolved_regression'})
            else:
                if not target.startswith(prefix):
                    raise RuntimeError('Non-local target in route map')
                relative = target[len(prefix):]
                data = (SITE / relative).read_bytes()
                declared = files[relative]
                match = len(data) == declared['derived_length'] and sha(data) == declared['derived_sha256']
                row.update(status='resolved', output_path=relative, bytes=len(data), sha256=sha(data))
                checked_files[relative] = match
                if not match:
                    errors.append({'record_id': old['record_id'], 'reason': 'declared_file_mismatch'})
                if status == 'missing_export_route':
                    recovered.append(row)
        else:
            row['status'] = status
        records.append(row)
    counts = dict(Counter(x['status'] for x in records))
    remaining_routes = sorted({x['normalized_route'] for x in remaining})
    report = {
        'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
        'prior_audit_sha256': sha(prior_bytes), 'route_map_sha256': sha(routes_bytes),
        'scope': 'Conserved menu identity and actual route/file verification. Resource and interaction statuses are not recomputed here.',
        'observation_count': len(records), 'effective_in_scope': sum(bool(x['effective_in_scope']) for x in records),
        'status_counts': counts, 'distinct_resolved_files_read': len(checked_files),
        'recovered_observations': recovered, 'recovered_distinct_routes': sorted({x['normalized_route'] for x in recovered}),
        'remaining_missing_observations': len(remaining), 'remaining_missing_distinct_routes': remaining_routes,
        'records': records, 'errors': errors,
    }
    report['accepted'] = not errors and len(records) == 1241 and len({x['record_id'] for x in records}) == 1241 and report['effective_in_scope'] == 1167
    (OUT / 'root-sidebar-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['accepted', 'observation_count', 'status_counts', 'distinct_resolved_files_read', 'recovered_distinct_routes', 'remaining_missing_observations', 'remaining_missing_distinct_routes', 'errors']}))
    if not report['accepted']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

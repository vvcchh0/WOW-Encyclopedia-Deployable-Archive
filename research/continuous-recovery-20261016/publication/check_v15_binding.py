"""Rebind accepted v15 bytes without modifying its frozen receipts."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SITE = ROOT / '.scratch/pages-resources-20261015-v15'
OLD = ROOT / 'research/focused-recovery-20261015-2303/integration'
OUT = Path(__file__).with_name('v15-publication-binding.json')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    free = shutil.disk_usage(ROOT).free
    if free < 11005853696:
        raise RuntimeError('disk floor')
    receipt = json.loads((OLD / 'root-final-local-acceptance.json').read_bytes())
    errors = []
    for name, binding in receipt['gates'].items():
        if sha((ROOT / binding['path']).read_bytes()) != binding['sha256']:
            errors.append({'path': binding['path'], 'reason': 'receipt_binding'})
        if not json.loads((ROOT / binding['path']).read_bytes()).get('accepted'):
            errors.append({'path': binding['path'], 'reason': 'gate_not_accepted'})
    accepted = json.loads((OLD / 'root-export-acceptance.json').read_bytes())
    provenance_bytes = (SITE / 'export-provenance.json').read_bytes()
    if sha(provenance_bytes) != accepted['export_provenance_sha256']:
        errors.append({'reason': 'provenance_binding'})
    provenance = json.loads(provenance_bytes)
    expected = {x['output_path']: x for x in provenance['files']}
    actual = set()
    total = 0
    for path in SITE.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(SITE).as_posix()
        actual.add(rel)
        data = path.read_bytes()
        total += len(data)
        if rel == 'export-provenance.json':
            continue
        record = expected.get(rel)
        if not record or len(data) != record['derived_length'] or sha(data) != record['derived_sha256']:
            errors.append({'path': rel, 'reason': 'object_binding'})
    if actual != set(expected) | {'export-provenance.json'}:
        errors.append({'reason': 'member_set'})
    build = json.loads((OLD / 'root-build-v15.json').read_bytes())
    for rel, expected_sha in build['implementation_sha256'].items():
        if sha((ROOT / rel).read_bytes()) != expected_sha:
            errors.append({'path': rel, 'reason': 'implementation_binding'})
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'accepted': receipt['accepted'] and not errors,
              'prior_acceptance': str((OLD / 'root-final-local-acceptance.json').relative_to(ROOT)).replace('\\', '/'),
              'prior_acceptance_sha256': sha((OLD / 'root-final-local-acceptance.json').read_bytes()),
              'provenance_sha256': sha(provenance_bytes), 'declared_objects': len(expected),
              'actual_files': len(actual), 'tree_bytes': total, 'disk_free_before': free,
              'disk_free_after': shutil.disk_usage(ROOT).free, 'errors': errors, 'network_requests': 0}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    if not result['accepted']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

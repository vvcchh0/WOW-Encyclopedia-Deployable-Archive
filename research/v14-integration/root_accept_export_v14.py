"""Hash every v14 export object; scan changed bytes against accepted v13 hygiene."""
import hashlib
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/v14-integration'
SITE = ROOT / '.scratch/pages-resources-20261015-v14'
PRIOR_SITE = ROOT / '.scratch/pages-resources-20261015-v13'
PRIOR_PROVENANCE_SHA = 'f1929a7f478e6579c8b1a809e512d46ca150872b4f2780787ad6d3884e42624b'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    provenance_bytes = (SITE / 'export-provenance.json').read_bytes()
    provenance = json.loads(provenance_bytes)
    prior_bytes = (PRIOR_SITE / 'export-provenance.json').read_bytes()
    prior = json.loads(prior_bytes)
    prior_receipt_path = ROOT / 'research/v13-integration/root-export-acceptance.json'
    prior_receipt_bytes = prior_receipt_path.read_bytes()
    prior_receipt = json.loads(prior_receipt_bytes)
    if not (prior_receipt['accepted'] and sha(prior_bytes) == PRIOR_PROVENANCE_SHA == prior_receipt['export_provenance_sha256']):
        raise RuntimeError('Prior hygiene acceptance binding failed')
    spec = importlib.util.spec_from_file_location('wow_public_hygiene', ROOT / 'research/github-publication-20261012/full-tree-hygiene.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    expected = {x['output_path']: x for x in provenance['files']}
    previous = {x['output_path']: x for x in prior['files']}
    reviewed = {(x['path'], x['category']) for x in prior_receipt['publication_findings'] if x['resolved']}
    errors, findings, changed_paths, reused_paths = [], [], [], []
    checked_bytes = scanned_bytes = 0
    actual_paths = set()
    if len(expected) != len(provenance['files']):
        errors.append({'reason': 'duplicate_output_path'})
    for path in SITE.rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(SITE).as_posix()
        actual_paths.add(relative)
        data = path.read_bytes()
        digest = sha(data)
        checked_bytes += len(data)
        record = expected.get(relative)
        if record:
            if len(data) != record['derived_length'] or digest != record['derived_sha256']:
                errors.append({'path': relative, 'reason': 'derived_hash_or_length'})
        elif relative != 'export-provenance.json':
            errors.append({'path': relative, 'reason': 'undeclared_file'})
        old = previous.get(relative, {})
        if record and digest == old.get('derived_sha256') and len(data) == old.get('derived_length'):
            reused_paths.append(relative)
            continue
        changed_paths.append(relative)
        scanned_bytes += len(data)
        for pattern in module.PATTERNS:
            if pattern.category in {'cookie_handling_field', 'authorization_field_without_value'}:
                continue
            matches = list(pattern.regex.finditer(data))
            if not matches:
                continue
            resolved = False
            if (relative, pattern.category) in reviewed:
                old_data = (PRIOR_SITE / relative).read_bytes()
                resolved = all(match.group(0) in old_data for match in matches)
            findings.append({'path': relative, 'category': pattern.category, 'count': len(matches),
                'resolved': resolved, 'review': 'exact prior reviewed public default bytes' if resolved else 'needs review'})
        if re.search(rb'(?im)^(?:set-cookie|x-archive-orig-set-cookie|authorization|proxy-authorization):\s*\S+', data):
            errors.append({'path': relative, 'reason': 'raw_sensitive_http_header'})
    missing = sorted(set(expected) - actual_paths)
    current = {x['route']: x for x in provenance['files']}
    overlays = []
    for old in prior['files']:
        if old['kind'] != 'image_overlay':
            continue
        new = current.get(old['route'], {})
        unchanged = all(new.get(key) == old.get(key) for key in ['original_url', 'derived_length', 'derived_sha256', 'source_sha256', 'actual_capture_timestamp', 'temporal_class'])
        overlays.append({'route': old['route'], 'unchanged': unchanged})
    source = json.loads((OUT / 'root-source-acceptance.json').read_text(encoding='utf-8'))
    build = json.loads((OUT / 'root-build-v14.json').read_text(encoding='utf-8'))
    manifest_matches = source['accepted'] and provenance['source_manifest_sha256'] == source['manifest_sha256']
    stats = provenance['stats']
    implementation_stable = build['implementation_unchanged_during_export'] and all(
        sha((ROOT / path).read_bytes()) == expected_sha for path, expected_sha in build['implementation_sha256'].items())
    report = {
        'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
        'export_provenance_sha256': sha(provenance_bytes), 'checked_declared_files': len(expected),
        'checked_tree_bytes': checked_bytes, 'missing_declared_files': missing, 'errors': errors,
        'hygiene_strategy': 'Every object hash and length read now. Same-path identical bytes reuse the pinned accepted v13 scan; changed/new bytes and current provenance scanned now.',
        'prior_acceptance_sha256': sha(prior_receipt_bytes), 'prior_provenance_sha256': sha(prior_bytes),
        'reused_hygiene_file_count': len(reused_paths), 'changed_scanned_file_count': len(changed_paths),
        'changed_scanned_bytes': scanned_bytes, 'changed_scanned_paths': sorted(changed_paths),
        'publication_findings': findings, 'retained_overlay_checks': overlays, 'stats': stats,
        'implementation_stable': implementation_stable, 'manifest_matches_accepted': manifest_matches,
        'published': False,
    }
    report['accepted'] = not (errors or missing) and all(x['resolved'] for x in findings) and len(overlays) == 38 and all(x['unchanged'] for x in overlays) and stats['source_records'] == 8356 and stats['image_overlay_records'] == 38 and implementation_stable and manifest_matches
    (OUT / 'root-export-acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['accepted', 'checked_declared_files', 'checked_tree_bytes', 'reused_hygiene_file_count', 'changed_scanned_file_count', 'changed_scanned_bytes', 'errors', 'publication_findings']}))
    if not report['accepted']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

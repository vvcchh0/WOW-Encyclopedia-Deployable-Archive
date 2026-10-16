"""Root full-byte acceptance of v18, reusing identical accepted v17 hygiene."""
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261016-v18'
PRIOR = ROOT / '.scratch/pages-resources-20261016-v17'
RUN = ROOT / 'research/continuous-recovery-20261016'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    if not SITE.is_dir():
        raise RuntimeError('v18 is not atomically completed')
    build = json.loads((RUN / 'integration/v18-build/worker-build-v18.json').read_bytes())
    old_bytes = (PRIOR / 'export-provenance.json').read_bytes()
    old_receipt = json.loads((OUT / 'root-v17-export-acceptance.json').read_bytes())
    if sha(old_bytes) != 'c6769d5636846bd27314824684e919b102bace200f1ef0458d3f976477e3f47f' or not old_receipt['accepted']:
        raise RuntimeError('Unbound prior accepted hygiene')
    current_bytes = (SITE / 'export-provenance.json').read_bytes()
    provenance, old = json.loads(current_bytes), json.loads(old_bytes)
    expected = {x['output_path']: x for x in provenance['files']}
    previous = {x['output_path']: x for x in old['files']}
    errors, findings, reused, changed = [], [], [], []
    actual, total, scanned = set(), 0, 0
    spec = importlib.util.spec_from_file_location('wow_hygiene_v18', ROOT / 'research/github-publication-20261012/full-tree-hygiene.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    for path in SITE.rglob('*'):
        if path.is_symlink():
            errors.append({'path': str(path), 'reason': 'symlink'})
        if not path.is_file():
            continue
        relative = path.relative_to(SITE).as_posix()
        data = path.read_bytes()
        digest = sha(data)
        actual.add(relative)
        total += len(data)
        record = expected.get(relative)
        if record:
            if record['derived_sha256'] != digest or record['derived_length'] != len(data):
                errors.append({'path': relative, 'reason': 'object_hash_or_length'})
        elif relative != 'export-provenance.json':
            errors.append({'path': relative, 'reason': 'undeclared_object'})
        prior = previous.get(relative)
        if prior and digest == prior['derived_sha256'] and len(data) == prior['derived_length']:
            reused.append(relative)
            continue
        changed.append(relative)
        scanned += len(data)
        for pattern in module.PATTERNS:
            if pattern.category in {'cookie_handling_field', 'authorization_field_without_value'}:
                continue
            count = len(list(pattern.regex.finditer(data)))
            if count:
                findings.append({'path': relative, 'category': pattern.category, 'count': count})
        if re.search(rb'(?im)^(?:set-cookie|x-archive-orig-set-cookie|authorization|proxy-authorization):\s*\S+', data):
            errors.append({'path': relative, 'reason': 'raw_sensitive_http_header'})
    if actual != set(expected) | {'export-provenance.json'} or len(expected) != len(provenance['files']):
        errors.append({'reason': 'member_set'})
    if provenance['source_manifest_sha256'] != 'd89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002':
        errors.append({'reason': 'source_manifest'})
    preserved = []
    current_routes = {x['route']: x for x in provenance['files']}
    for item in old['files']:
        if item['kind'] != 'image_overlay':
            continue
        new = current_routes.get(item['route'], {})
        okay = all(new.get(k) == item.get(k) for k in ['original_url', 'derived_length', 'derived_sha256', 'source_sha256', 'actual_capture_timestamp', 'temporal_class'])
        preserved.append({'route': item['route'], 'unchanged': okay})
        if not okay:
            errors.append({'route': item['route'], 'reason': 'prior_overlay_regression'})
    old_map = json.loads((PRIOR / '__offline/route-map.json').read_bytes())
    new_map = json.loads((SITE / '__offline/route-map.json').read_bytes())
    mappings = {}
    for name, values in old_map.items():
        if isinstance(values, dict):
            differences = [key for key, value in values.items() if new_map.get(name, {}).get(key) != value]
            mappings[name] = {'prior_keys': len(values), 'new_keys': len(new_map.get(name, {})), 'changed_or_removed': differences}
            if differences:
                errors.append({'reason': 'prior_routing_changed', 'map': name})
    for path, digest in build['production_sha256_after'].items():
        if sha((ROOT / path).read_bytes()) != digest:
            errors.append({'path': path, 'reason': 'implementation_changed'})
    for path, digest in build['map_sha256_after'].items():
        if sha((ROOT / path).read_bytes()) != digest:
            errors.append({'path': path, 'reason': 'map_changed'})
    if not build['maps_unchanged_during_export'] or not build['production_unchanged_during_export'] or len(preserved) != 69:
        errors.append({'reason': 'build_or_overlay_binding'})
    if build['map_sha256_before'] != build['map_sha256_after'] or build['production_sha256_before'] != build['production_sha256_after']:
        errors.append({'reason': 'input_before_after_binding'})
    if sha((ROOT / build['root_v2_code_acceptance']).read_bytes()) != build['root_v2_code_acceptance_sha256']:
        errors.append({'reason': 'root_input_gate_binding'})
    if sha((ROOT / 'offline/build-manifest.json').read_bytes()) != '397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459':
        errors.append({'reason': 'original_manifest_changed'})
    stats = provenance['stats']
    if stats['source_records'] != 8357 or stats['image_overlay_records'] != 69 or stats['primary_image_overlay_records'] != 48 or stats['supplement_image_overlay_records'] != 21:
        errors.append({'reason': 'overlay_counts'})
    if stats.get('guide_preview_gallery_pages') != 6 or stats.get('guide_preview_count') != 22:
        errors.append({'reason': 'guide_preview_counts'})
    guide = provenance.get('guide_previews', {})
    if guide.get('preview_count') != 22 or guide.get('group_count') != 6:
        errors.append({'reason': 'guide_preview_provenance'})
    for group in guide.get('groups', []):
        gallery = current_routes[group['gallery_route']]
        text = (SITE / gallery['output_path']).read_text(encoding='utf-8')
        if text.count('class="offline-guide-preview-section"') != 1 or text.count('alt="Preserved guide preview"') != group['preview_count']:
            errors.append({'route': group['gallery_route'], 'reason': 'guide_section_conservation'})
    if len(expected) != 8527 or len(actual) != 8528:
        errors.append({'reason': 'v18_object_count'})
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'accepted': not errors and not findings,
        'export_provenance_sha256': sha(current_bytes), 'prior_provenance_sha256': sha(old_bytes),
        'checked_declared_files': len(expected), 'actual_files': len(actual), 'checked_tree_bytes': total,
        'hygiene_reused_identical_files': len(reused), 'changed_scanned_files': len(changed), 'changed_scanned_bytes': scanned,
        'changed_paths': sorted(changed), 'prior_overlays': preserved, 'routing_conservation': mappings,
        'stats': stats, 'errors': errors, 'publication_findings': findings, 'disk_free_bytes': shutil.disk_usage(ROOT).free, 'published': False}
    (OUT / 'root-v18-export-acceptance.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({k: result[k] for k in ['accepted', 'checked_declared_files', 'actual_files', 'checked_tree_bytes', 'changed_scanned_files', 'changed_paths', 'errors', 'publication_findings']}))
    if not result['accepted']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

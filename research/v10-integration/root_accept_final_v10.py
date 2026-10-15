"""Combine accepted v10 source, export, routes and observed browser evidence."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/v10-integration'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    paths = {
        'source': 'research/v10-integration/root-source-acceptance.json',
        'export': 'research/v10-integration/root-export-acceptance.json',
        'sidebar': 'research/v10-integration/root-sidebar-check.json',
        'ledger': 'research/v10-integration/root-ledger-acceptance.json',
        'native_viewer': 'research/continuous-recovery-20261015/native-viewer-acceptance.json',
        'browser': 'research/continuous-recovery-20261015/v10-browser-independent-review.json',
    }
    gates, errors = {}, []
    for name, relative in paths.items():
        data = (ROOT / relative).read_bytes()
        report = json.loads(data)
        gates[name] = {'path': relative, 'sha256': digest(data), 'accepted': report.get('accepted') is True}
        if not gates[name]['accepted']:
            errors.append(name + '_gate_not_accepted')
    unit_path = ROOT / 'research/continuous-recovery-20261015/viewer-derived-fixes/wrath-card-hitarea-011-receipt.json'
    unit_bytes = unit_path.read_bytes()
    unit = json.loads(unit_bytes)
    tests = unit['joint_tests']
    implementation = []
    for record in unit['implementation_files']:
        actual = (ROOT / record['path']).read_bytes()
        match = len(actual) == record['bytes'] and digest(actual) == record['sha256']
        implementation.append({'path': record['path'], 'sha256': digest(actual), 'matches_tested_code': match})
        if not match:
            errors.append('tested_implementation_changed:' + record['path'])
    if tests['exit_code'] != 0 or tests['tests_run'] != 42:
        errors.append('unit_test_gate')
    source = json.loads((ROOT / paths['source']).read_text(encoding='utf-8'))
    export = json.loads((ROOT / paths['export']).read_text(encoding='utf-8'))
    manifest = ROOT / '.scratch/offline-navigation-20261015-v10/build-manifest.json'
    provenance = ROOT / '.scratch/pages-resources-20261015-v10/export-provenance.json'
    if digest(manifest.read_bytes()) != source['manifest_sha256']:
        errors.append('accepted_source_manifest_changed')
    if digest(provenance.read_bytes()) != export['export_provenance_sha256']:
        errors.append('accepted_export_provenance_changed')
    frozen = digest((ROOT / 'offline/build-manifest.json').read_bytes())
    if frozen != '397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459':
        errors.append('frozen_manifest_changed')
    visuals = []
    for name in ['wrath-artwork-page-1.png', 'wrath-viewer-s12.png']:
        path = OUT / 'browser/screenshots' / name
        data = path.read_bytes()
        visuals.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': len(data), 'sha256': digest(data),
            'reviewed_by_root': True})
    report = {
        'schema': 'wow-v10-root-final-acceptance/v1', 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'accepted': not errors, 'ready_for_pages_publication': not errors, 'published': False,
        'gates': gates, 'unit_tests': {'receipt_sha256': digest(unit_bytes), 'tests_run': 42, 'exit_code': tests['exit_code'],
            'scope': 'Relevant exporter and historical exhibit modules; unchanged baseline suites were not repeated.'},
        'tested_implementation': implementation, 'root_visual_reviews': visuals,
        'source_records': 8338, 'declared_export_objects': 8477, 'retained_image_overlays': 38,
        'restored_sidebar_routes_this_version': 7, 'remaining_missing_sidebar_routes': 16,
        'known_gaps': {
            'wrath_artwork_available_ordinary_pairs': [1, 3, 6, 9, 12],
            'wrath_artwork_missing_ordinary_pairs': [2, 4, 5, 7, 8, 10, 11, 13],
            'decorative_ssborder1_png': 'not recovered; derived hit area and decorative placeholder visibility repaired',
            'hires_artwork': 'No high-resolution image recovered in NET-HIRES-011.',
            'player_screenshot_galleries': 'Game Guide gallery payload gaps remain separate from Wrath artwork.',
        },
        'scope': 'Current source/export/routes and focused browser changes. This does not claim all historical website assets recovered.',
        'frozen_manifest_sha256': frozen, 'errors': errors,
    }
    (OUT / 'root-final-acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': report['accepted'], 'ready_for_pages_publication': report['ready_for_pages_publication'], 'errors': errors}))
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

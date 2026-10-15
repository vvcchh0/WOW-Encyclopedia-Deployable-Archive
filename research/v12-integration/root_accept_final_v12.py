"""Bind the three restored news pages, current object checks and focused browser evidence."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/v12-integration'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    paths = {
        'source': 'research/v12-integration/root-source-acceptance.json',
        'export': 'research/v12-integration/root-export-acceptance.json',
        'routes': 'research/v12-integration/root-sidebar-check.json',
        'browser': 'research/continuous-recovery-20261015/v12-browser-independent-review.json',
        'prior_browser': 'research/continuous-recovery-20261015/v11-browser-independent-review.json',
    }
    gates, errors = {}, []
    reports = {}
    for key, relative in paths.items():
        data = (ROOT / relative).read_bytes()
        reports[key] = json.loads(data)
        gates[key] = {'path': relative, 'sha256': sha(data), 'accepted': reports[key].get('accepted') is True}
        if not gates[key]['accepted']:
            errors.append(key + '_gate')
    source_manifest = ROOT / '.scratch/offline-navigation-20261015-v12/build-manifest.json'
    provenance_path = ROOT / '.scratch/pages-resources-20261015-v12/export-provenance.json'
    if sha(source_manifest.read_bytes()) != reports['source']['manifest_sha256']:
        errors.append('source_manifest_changed')
    if sha(provenance_path.read_bytes()) != reports['export']['export_provenance_sha256']:
        errors.append('export_provenance_changed')
    unit_path = ROOT / 'research/continuous-recovery-20261015/viewer-derived-fixes/wrath-card-hitarea-011-receipt.json'
    unit_bytes = unit_path.read_bytes()
    unit = json.loads(unit_bytes)
    implementation = []
    for item in unit['implementation_files']:
        data = (ROOT / item['path']).read_bytes()
        match = len(data) == item['bytes'] and sha(data) == item['sha256']
        implementation.append({'path': item['path'], 'sha256': sha(data), 'matches_tested_code': match})
        if not match:
            errors.append('tested_code_changed:' + item['path'])
    if unit['joint_tests']['exit_code'] != 0 or unit['joint_tests']['tests_run'] != 42:
        errors.append('prior_test_gate')
    frozen = sha((ROOT / 'offline/build-manifest.json').read_bytes())
    if frozen != '397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459':
        errors.append('frozen_manifest_changed')
    visuals = json.loads((OUT / 'root-visual-review.json').read_bytes())
    for item in visuals['images']:
        if sha((ROOT / item['path']).read_bytes()) != item['sha256'] or not item['reviewed_by_root']:
            errors.append('visual_review_binding:' + item['path'])
    report = {
        'schema': 'wow-v12-root-final-acceptance/v1', 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'accepted': not errors, 'ready_for_pages_publication': not errors, 'published': False,
        'gates': gates, 'unit_test_reuse': {'receipt_sha256': sha(unit_bytes), 'tests_run': 42,
            'exit_code': 0, 'reason': 'Relevant production implementation is byte-identical; no repeated unchanged suite.'},
        'tested_implementation': implementation, 'root_visual_reviews': visuals,
        'source_records': 8344, 'declared_export_objects': 8483, 'retained_image_overlays': 38,
        'new_source_entities': 3, 'new_original_images': 0, 'new_stylesheets': 0,
        'remaining_missing_sidebar_routes': 13, 'new_sidebar_pages': 3,
        'known_gaps': 'Game Guide player screenshot originals/thumbnails remain unavailable locally; other historical asset gaps persist.',
        'scope': 'Three new news pages, all current export bytes, conserved menu identities and focused page/accordion checks; unchanged v11 image/viewer browser evidence reused.',
        'frozen_manifest_sha256': frozen, 'errors': errors,
    }
    (OUT / 'root-final-acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': report['accepted'], 'errors': errors}))
    assert report['accepted']


if __name__ == '__main__':
    main()

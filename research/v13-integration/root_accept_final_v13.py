"""Bind the three restored news pages, current object checks and focused browser evidence."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/v13-integration'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    paths = {
        'source': 'research/v13-integration/root-source-acceptance.json',
        'export': 'research/v13-integration/root-export-acceptance.json',
        'routes': 'research/v13-integration/root-sidebar-check.json',
        'browser': 'research/continuous-recovery-20261015/v13-browser-independent-review.json',
        'code': 'research/v13-integration/root-code-acceptance.json',
        'patch_independent': 'research/continuous-recovery-20261015/news-toggle-derived-fix-027-independent-acceptance.json',
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
    source_manifest = ROOT / '.scratch/offline-navigation-20261015-v13/build-manifest.json'
    provenance_path = ROOT / '.scratch/pages-resources-20261015-v13/export-provenance.json'
    if sha(source_manifest.read_bytes()) != reports['source']['manifest_sha256']:
        errors.append('source_manifest_changed')
    if sha(provenance_path.read_bytes()) != reports['export']['export_provenance_sha256']:
        errors.append('export_provenance_changed')
    unit_path = ROOT / 'research/continuous-recovery-20261015/news-toggle-derived-fixes/news-toggle-derived-fix-027-final-receipt.json'
    unit_bytes = unit_path.read_bytes()
    unit = json.loads(unit_bytes)
    implementation = []
    for item in unit['implementation_files']:
        data = (ROOT / item['path']).read_bytes()
        match = len(data) == item['bytes'] and sha(data) == item['sha256']
        implementation.append({'path': item['path'], 'sha256': sha(data), 'matches_tested_code': match})
        if not match:
            errors.append('tested_code_changed:' + item['path'])
    if unit['joint_tests']['final_exit_code'] != 0 or unit['joint_tests']['tests_run'] != 44:
        errors.append('prior_test_gate')
    if reports['export']['stats']['source_records'] != 8347 or reports['export']['checked_declared_files'] != 8486:
        errors.append('export_version_counts')
    if len(reports['routes']['remaining_missing_distinct_routes']) != 10 or len(reports['routes']['recovered_distinct_routes']) != 3:
        errors.append('sidebar_version_counts')
    frozen = sha((ROOT / 'offline/build-manifest.json').read_bytes())
    if frozen != '397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459':
        errors.append('frozen_manifest_changed')
    visuals = json.loads((OUT / 'root-visual-review.json').read_bytes())
    for item in visuals['images']:
        if sha((ROOT / item['path']).read_bytes()) != item['sha256'] or not item['reviewed_by_root']:
            errors.append('visual_review_binding:' + item['path'])
    report = {
        'schema': 'wow-v13-root-final-acceptance/v1', 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'accepted': not errors, 'ready_for_pages_publication': not errors, 'published': False,
        'gates': gates, 'unit_test_reuse': {'receipt_sha256': sha(unit_bytes), 'tests_run': 44,
            'exit_code': 0, 'reason': 'New toggle implementation passed the 44-test relevant suite; current code hashes are bound without repeating it.'},
        'tested_implementation': implementation, 'root_visual_reviews': visuals,
        'source_records': 8347, 'declared_export_objects': 8486, 'retained_image_overlays': 38,
        'new_source_entities': 3, 'new_original_images': 0, 'new_stylesheets': 0,
        'remaining_missing_sidebar_routes': 10, 'new_sidebar_pages': 3,
        'known_gaps': 'Game Guide player screenshot originals/thumbnails remain unavailable locally; other historical asset gaps persist.',
        'scope': 'Three new news pages, all current export bytes, conserved menu identities and focused real-click and Enter regression checks for the new derived news anchors; unchanged v11 image/viewer evidence reused.',
        'frozen_manifest_sha256': frozen, 'errors': errors,
    }
    (OUT / 'root-final-acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': report['accepted'], 'errors': errors}))
    assert report['accepted']


if __name__ == '__main__':
    main()

"""Accept the one-page Arathi repair and reconcile observed paths to actual resource targets."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261021-v52'
OUT = PUB / 'root-v52-local-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
tree, browser, code = [read(PUB / f'root-v52-{kind}-acceptance.json') for kind in ('export', 'browser', 'code')]
assert all(x['accepted'] for x in (tree, browser, code))
assert len(browser['pages']) == 1 and browser['pages'][0]['restored_previews'] == 20
assert browser['pages'][0]['remaining_previews'] == 2 and browser['asset_fulfillments'] == 0
assert all(not browser[k] for k in ('page_errors', 'request_failures', 'external_requests', 'http_errors'))
assert sha(SITE / 'export-provenance.json') == tree['export_provenance_sha256'] == browser['export_provenance_sha256']
for row in code['code_bindings']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
review_path = ROOT / 'research/continuous-recovery-20261021/local-audit/underdev-final-routing-review/underdev-final-routing-review.json'
review = read(review_path)
old_csv = ROOT / 'research/continuous-recovery-20261021/local-audit/non-gallery-closeout-v49-r3/remaining-targets.csv'
rows = list(csv.DictReader(old_csv.open(encoding='utf-8-sig')))
old = {row['target_route']: row for row in rows}
malformed = {'/' + row['observed_requested_path'] for row in review['targets']}
missing = {row['proposed_intended_route'] for row in review['targets'] if not row['route_map_exact_exists']}
assert len(old) == 411 and len(malformed & set(old)) == 22 and len(missing) == 2
corrected = (set(old) - malformed) | missing
assert len(corrected) == 391
provenance = read(SITE / 'export-provenance.json')
route_map = read(SITE / '__offline/route-map.json')
for route in corrected:
    assert route not in route_map['routes'] and route not in route_map['aliases'], route
    assert not (SITE / route.lstrip('/')).exists(), route
gap_csv = PUB / 'v52-remaining-resource-targets.csv'
gap_report = PUB / 'root-v52-gap-reconciliation.json'
assert not gap_csv.exists() and not gap_report.exists()
with gap_csv.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=('target_route', 'classification', 'evidence'))
    writer.writeheader()
    for route in sorted(corrected):
        writer.writerow({'target_route': route, 'classification': 'exact_local_resource_absent',
                         'evidence': 'underdev-final-routing-review + v52 browser/tree' if route in missing else 'rolling v49-r3 audit + byte-identical v52 tree'})
gap = {'accepted': True, 'version': 'v52', 'checked_utc': datetime.now(timezone.utc).isoformat(),
       'prior_observed_missing_targets': 411, 'malformed_compositions_removed': 22,
       'existing_exact_previews_restored': 20, 'intended_missing_targets_added': sorted(missing),
       'remaining_exact_local_resource_targets': 391,
       'scope': 'Corrected rolling audited target set, not a full-site dynamic-state scan or proof of remote archive absence.',
       'bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in (old_csv, review_path, gap_csv)]}
gap_report.write_bytes((json.dumps(gap, indent=2) + '\n').encode())
paths = {'export-provenance.json', '__offline/route-map.json', '__offline/pages_runtime.js',
         '__offline/aldor-scryers-lore.js', 'pvp/battlegrounds/info-arathi.html'}
paths.update(row['proposed_intended_route'].lstrip('/') for row in review['targets'] if row['route_map_exact_exists'])
bindings = {row['path'] for row in code['code_bindings']}
bindings.update(p.relative_to(ROOT).as_posix() for p in (
    PUB / 'root-v52-code-acceptance.json', PUB / 'root-v52-export-acceptance.json',
    PUB / 'root-v52-browser-acceptance.json', PUB / 'root-v51-local-acceptance.json',
    PUB / 'root-v51-browser-acceptance.json', gap_report, review_path,
))
gate = {
    'accepted': True, 'published': False, 'version': 'v52',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'local_site': SITE.relative_to(ROOT).as_posix(), 'actual_files': tree['actual_files'],
    'tree_bytes': tree['tree_bytes'], 'export_provenance_sha256': tree['export_provenance_sha256'],
    'previous_pages_commit': '7494e7cc898b34f8f4c6a64922bde34b8dd2ee44',
    'bindings': [{'path': p, 'sha256': sha(ROOT / p)} for p in sorted(bindings)],
    'objects': [{'path': p, 'bytes': (SITE / p).stat().st_size, 'sha256': sha(SITE / p)} for p in sorted(paths)],
    'prior_online_acceptance': 'research/continuous-recovery-20261021/publication/root-v51-pages-online-acceptance.json',
    'prior_online_reuse_reason': 'All existing outputs except the exact Arathi guide HTML and provenance are byte-identical; current verification covers the changed page, all20 restored previews and four controls.',
    'scope': 'One exact resource-directory repair, restoring20 already-collected Arathi guide previews; ss17/18 remain absent.',
    'guide_collection_images': 39, 'new_original_2008_images': 0,
    'related_encyclopedia_images': 3, 'related_guide_images': 1,
    'known_gaps': ['391 exact local resource targets remain in the corrected rolling audit.',
                   'The separate anniversary screenshot-directory defect is deferred gallery scope.',
                   'Wayback remains stopped after the last proxy429.'],
}
assert len(paths) == 25 and sum(row['bytes'] for row in gate['objects']) < 64 * 1024 * 1024
OUT.write_bytes((json.dumps(gate, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'objects': len(paths), 'restored_previews': 20,
                  'remaining_resource_targets': 391, 'sha256': sha(OUT)}))

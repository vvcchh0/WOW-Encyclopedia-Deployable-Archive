"""Bind v50 source/text, all exported bytes and actual popup operation."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261021-v50'
OUT = PUB / 'root-v50-local-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
tree = read(PUB / 'root-v50-export-acceptance.json')
browser = read(PUB / 'root-v50-browser-acceptance.json')
code = read(PUB / 'root-v50-code-acceptance.json')
prior = read(PUB / 'root-v49-local-acceptance.json')
assert tree['accepted'] and browser['accepted'] and code['accepted']
assert browser['asset_fulfillments'] == 0 and len(browser['pages']) == 1
assert all(not browser[k] for k in ('page_errors', 'request_failures', 'external_requests', 'http_errors'))
assert browser['pages'][0]['actual_popup_opens'] == 2
assert sha(SITE / 'export-provenance.json') == tree['export_provenance_sha256']
for row in code['code_bindings']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
paths = {r['path'] for r in prior['objects']} | set(tree['changed_existing_files']) | {
    '__offline/aldor-scryers-lore.js',
    'info/basics/factions/aldorscryers/aldor-scryers-tokens.xml.html',
}
bindings = {r['path'] for r in code['code_bindings']}
bindings.update('research/continuous-recovery-20261021/publication/' + n for n in (
    'root-v50-code-acceptance.json', 'root-v50-export-acceptance.json',
    'root-v50-browser-acceptance.json', 'root-aldor-scryers-lore-source-acceptance.json',
    'root-related-encyclopedia-image-decision.json', 'root-related-guide-image-v49-decision.json',
))
gate = {
    'accepted': True, 'published': False, 'version': 'v50',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'local_site': SITE.relative_to(ROOT).as_posix(), 'actual_files': tree['actual_files'],
    'tree_bytes': tree['tree_bytes'],
    'previous_pages_commit': '349166108bcbf9e69a02c35be46e66f454427207',
    'source_manifest_sha256': 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a',
    'export_provenance_sha256': tree['export_provenance_sha256'],
    'bindings': [{'path': p, 'sha256': sha(ROOT / p)} for p in sorted(bindings)],
    'objects': [{'path': p, 'sha256': sha(SITE / p), 'bytes': (SITE / p).stat().st_size}
                for p in sorted(paths)],
    'scope': 'Restore two original Source16 faction-lore paragraphs on the exact main Aldor/Scryers page through a single deferred helper.',
    'browser_evidence': {'initial_lore': True, 'real_faction_switches': 2,
                         'actual_lore_popups': 2, 'parent_screenshots_reviewed': 2,
                         'asset_fulfillments': 0,
                         'probe_corrections': 'First probe compared source <br /> spelling with normalized browser <br>. Second sampled a broad text click before the faction state was observed. Both failed probes retained. Final probe uses exact original button anchors and waits for visible panel state; export unchanged.'},
    'related_encyclopedia_images': 3, 'related_guide_images': 1,
    'related_talent_icon_objects': 986, 'related_talent_ui_objects': 6,
    'guide_collection_images': 39, 'new_original_2008_images': 0,
    'known_gaps': ['Category avatars, news/guide assets and 259 talent image targets remain missing.',
                   'An existing Wrath letter image has an unmatched single-slash route; a separate narrow correction is being reviewed.',
                   'Player screenshot galleries excluded from this run.'],
}
assert len(paths) <= 128 and sum(r['bytes'] for r in gate['objects']) < 64 * 1024 * 1024
OUT.write_bytes((json.dumps(gate, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'objects': len(paths), 'sha256': sha(OUT)}))

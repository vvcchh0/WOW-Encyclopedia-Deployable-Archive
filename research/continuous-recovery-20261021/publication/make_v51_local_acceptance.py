"""Final local gate: original faction lore and four existing-letter displays."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261021-v51'
OUT = PUB / 'root-v51-local-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
tree, browser, code = [read(PUB / f'root-v51-{kind}-acceptance.json')
                       for kind in ('export', 'browser', 'code')]
prior = read(PUB / 'root-v50-local-acceptance.json')
assert all(x['accepted'] for x in (tree, browser, code))
assert browser['asset_fulfillments'] == 0 and len(browser['pages']) == 5
assert all(not browser[k] for k in ('page_errors', 'request_failures', 'external_requests', 'http_errors'))
assert browser['pages'][0]['actual_popup_opens'] == 2
assert all(p['letter_image']['width'] == p['letter_image']['height'] == 48
           and p['placeholder'] is False for p in browser['pages'][1:])
assert sha(SITE / 'export-provenance.json') == tree['export_provenance_sha256']
for row in code['code_bindings']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
paths = {r['path'] for r in prior['objects']} | set(tree['changed_existing_files'])
paths.update(p['route'].lstrip('/') for p in browser['pages'])
paths.add('wrath/images/letters/T.gif')
binding_paths = {r['path'] for r in code['code_bindings']}
binding_paths.update('research/continuous-recovery-20261021/publication/' + n for n in (
    'root-v51-code-acceptance.json', 'root-v51-export-acceptance.json',
    'root-v51-browser-acceptance.json', 'root-v50-local-acceptance.json',
    'root-aldor-scryers-lore-source-acceptance.json',
    'root-related-encyclopedia-image-decision.json', 'root-related-guide-image-v49-decision.json',
))
gate = {
    'accepted': True, 'published': False, 'version': 'v51',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'local_site': SITE.relative_to(ROOT).as_posix(), 'actual_files': tree['actual_files'],
    'tree_bytes': tree['tree_bytes'],
    'previous_pages_commit': '349166108bcbf9e69a02c35be46e66f454427207',
    'source_manifest_sha256': 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a',
    'export_provenance_sha256': tree['export_provenance_sha256'],
    'bindings': [{'path': p, 'sha256': sha(ROOT / p)} for p in sorted(binding_paths)],
    'objects': [{'path': p, 'sha256': sha(SITE / p), 'bytes': (SITE / p).stat().st_size}
                for p in sorted(paths)],
    'scope': 'Final non-gallery version: original faction lore and one exact existing T.gif route alias, retaining the accepted earlier restorations.',
    'browser_evidence': {'actual_pages': 5, 'real_faction_switches': 2, 'actual_lore_popups': 2,
                         'letter_pages': 4, 'asset_fulfillments': 0,
                         'prior_lore_visual_review': 'Two v50 popup screenshots; all page HTML, styles, helper and original scripts are byte-identical.',
                         'current_extra_visual_review': 'T.gif Bard crop inspected; source GIF inspected at its natural 48x48 dimensions.'},
    'related_encyclopedia_images': 3, 'related_guide_images': 1,
    'related_talent_icon_objects': 986, 'related_talent_ui_objects': 6,
    'guide_collection_images': 39, 'new_original_2008_images': 0,
    'known_gaps': ['411 distinct local resource targets remain missing in the rolling audited states, including 259 talent targets.',
                   'A separate anniversary screenshot-directory composition bug is recorded for later gallery work.',
                   'Wayback fresh control still returned429 via proxy; no successful resume.',
                   'Player screenshot galleries excluded from this run.'],
}
assert len(paths) <= 128 and sum(r['bytes'] for r in gate['objects']) < 64 * 1024 * 1024
OUT.write_bytes((json.dumps(gate, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'objects': len(paths), 'sha256': sha(OUT)}))

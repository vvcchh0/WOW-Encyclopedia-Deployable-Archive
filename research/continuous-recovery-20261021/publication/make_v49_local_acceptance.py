"""Bind independently checked v49 bytes and actual-browser behavior."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261021-v49'
OUT = PUB / 'root-v49-local-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
tree = read(PUB / 'root-v49-export-acceptance.json')
browser = read(PUB / 'root-v49-browser-acceptance.json')
code = read(PUB / 'root-v49-code-acceptance.json')
prior = read(PUB / 'root-v46-local-acceptance.json')
prov = read(SITE / 'export-provenance.json')
assert tree['accepted'] and browser['accepted'] and code['accepted']
assert len(browser['pages']) == 5 and browser['asset_fulfillments'] == 0
assert all(not browser[k] for k in ('page_errors', 'request_failures', 'external_requests', 'http_errors'))
assert sha(SITE / 'export-provenance.json') == tree['export_provenance_sha256']
assert tree['actual_files'] == 10143 and tree['new_related_image_bytes'] == 176325
for row in code['code_bindings']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
paths = {r['path'] for r in prior['objects']} | set(tree['changed_existing_files'])
paths.update(r['output_path'] for r in prov['files']
             if r['kind'] in {'related_encyclopedia_image', 'related_encyclopedia_image_catalog',
                              'related_guide_image', 'related_guide_image_catalog'})
paths.update({
    '__offline/related-encyclopedia-images.json',
    '__offline/related-guide-images.json',
    '__offline/related-encyclopedia-images/alleriawindrunner.jpg',
    '__offline/related-encyclopedia-images/cenarioncircle.jpg',
    '__offline/related-encyclopedia-images/malfurionstormrage.jpg',
    '__offline/related-guide-images/thumb-thebroken.jpg',
    'info/basics/factions/aldorscryers/aldor-scryers.xml.html',
    'info/basics/factions/rewardstable/images/button-alliance.jpg',
    'info/basics/factions/rewardstable/images/button-horde.jpg',
})
binding_paths = {r['path'] for r in code['code_bindings']}
binding_paths.update('research/continuous-recovery-20261021/' + p for p in (
    'publication/root-v49-code-acceptance.json',
    'publication/root-v49-export-acceptance.json',
    'publication/root-v49-browser-acceptance.json',
    'publication/root-related-encyclopedia-image-decision.json',
    'publication/root-related-guide-image-v49-decision.json',
    'publication/root-archivecraft-images-source-acceptance.json',
    'publication/root-archivecraft-broken-image-source-acceptance.json',
    'integration/related-encyclopedia-images/input-map.json',
    'integration/related-guide-images-v49/input-map.json',
    'publication/verify_accepted_pages.py',
))
gate = {
    'accepted': True, 'published': False, 'version': 'v49',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'local_site': SITE.relative_to(ROOT).as_posix(),
    'actual_files': tree['actual_files'], 'tree_bytes': tree['tree_bytes'],
    'previous_pages_commit': 'e55d8a0153c04cc1ca14726d93877cc5d2de2ff2',
    'source_manifest_sha256': prov['source_manifest_sha256'],
    'export_provenance_sha256': tree['export_provenance_sha256'],
    'bindings': [{'path': p, 'sha256': sha(ROOT / p)} for p in sorted(binding_paths)],
    'objects': [{'path': p, 'sha256': sha(SITE / p), 'bytes': (SITE / p).stat().st_size}
                for p in sorted(paths)],
    'scope': 'Three encyclopedia illustrations and The Broken thumbnail from separately attributed current ArchiveCraft sources; one verified dynamic spelling maps to that same thumbnail; exact two reward-button image URL repairs.',
    'browser_evidence': {
        'actual_pages': 5, 'parent_screenshots_reviewed': 3, 'asset_fulfillments': 0,
        'bestiary_actual_menu_click': True, 'both_reward_buttons_clicked': True,
        'source_note_minimum_text_contrast': min(p['source_text_contrast'] for p in browser['pages'][:4]),
        'probe_corrections': 'The first probe also asserted an unrelated pre-existing lore-panel behavior. Both failed attempt logs remain; the final probe records that known gap and verifies the image/button changes on the unchanged export.',
    },
    'new_original_2008_images': 0, 'related_encyclopedia_images': 3,
    'related_guide_images': 1, 'related_talent_icon_objects': 986,
    'related_talent_ui_objects': 6, 'guide_collection_images': 39,
    'known_gaps': ['Aldor/Scryers lore panel still displays undefined; a separate source-bound repair is in preparation.',
                   'Encyclopedia category avatar images and other news/guide resources remain missing.',
                   'Player screenshot galleries are excluded from this run.'],
}
assert len(paths) <= 128 and sum(r['bytes'] for r in gate['objects']) < 64 * 1024 * 1024
OUT.write_text(json.dumps(gate, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'accepted': True, 'objects': len(paths), 'bytes': sum(r['bytes'] for r in gate['objects']), 'sha256': sha(OUT)}))

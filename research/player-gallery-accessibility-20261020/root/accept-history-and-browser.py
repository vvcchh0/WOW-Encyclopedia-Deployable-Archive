"""Independent bounded checks of the saved gallery audit outputs; no network."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/player-gallery-accessibility-20261020'


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


source = read('research/player-gallery-accessibility-20261020/root/source-derived-targets.json')
history = read('research/player-gallery-accessibility-20261020/history/gallery-availability-table.json')
receipt = read('research/player-gallery-accessibility-20261020/history/history-audit-receipt.json')
browser = read('research/player-gallery-accessibility-20261020/local/browser/browser-audit-all50.json')
expected = {'/' + t['path'] for r in source['rows'] for t in r['targets']}
checks = {}
checks['all_29_selected_input_bindings_match'] = all(
    (ROOT / x['path']).stat().st_size == x['bytes'] and sha(ROOT / x['path']) == x['sha256']
    for x in receipt['source_inputs'])
checks['50_history_rows_match_source_order'] = all(
    x['rank'] == y['registry_rank'] and x['gallery'] == y['gallery'] and
    x['declared_native_slots'] == y['declared_slots']
    for x, y in zip(source['rows'], history['rows'])) and len(history['rows']) == 50

# Parse saved CDX bodies directly. A resume marker/string is not a capture row.
raw_rows = 0
native_rows = 0
raw_bodies = []
non_cdx_bodies = []
for x in receipt['source_inputs']:
    if not x['path'].endswith('.body'):
        continue
    try:
        data = json.loads((ROOT / x['path']).read_bytes())
    except (json.JSONDecodeError, UnicodeDecodeError):
        # The saved 503 diagnostic is not an empty index.
        non_cdx_bodies.append({'path': x['path'], 'sha256': x['sha256'],
                               'classification': 'non_cdx_endpoint_error_unknown_coverage'})
        continue
    assert isinstance(data, list) and data and isinstance(data[0], list)
    header = data[0]
    assert 'original' in header
    captures = [dict(zip(header, row)) for row in data[1:]
                if isinstance(row, list) and len(row) == len(header)]
    marker = any(not isinstance(row, list) or len(row) != len(header) for row in data[1:])
    count = sum(urlsplit(row['original']).path in expected for row in captures)
    # Includes the stopped Mechanar 503 body only if it were a CDX array;
    # the curated input bindings contain successful complete CDX bodies.
    raw_rows += len(captures)
    native_rows += count
    raw_bodies.append({'path': x['path'], 'rows': len(captures),
                       'native_exact_rows': count, 'resume_marker': marker,
                       'sha256': x['sha256']})
checks['saved_cdx_has_no_exact_native_targets'] = native_rows == 0
checks['saved_success_cdx_arrays_are_complete'] = all(not x['resume_marker'] for x in raw_bodies)
checks['mechanar_endpoint_error_kept_unknown'] = len(non_cdx_bodies) == 1 and history['rows'][21]['late_window']['status'] == 'source_503'
late = [r for r in history['rows'] if r['late_window']['status'] == 'covered_complete_index']
checks['late_coverage_21_and_open_29'] = len(late) == 21 and len(history['rows']) - len(late) == 29
checks['all_50_retain_post2010_unknown_window'] = all(
    any(x['from'] == '20101208000000' for x in r['next_query_plan']) for r in history['rows'])

pages = browser['results'][:50]
checks['all_50_browser_routes_match_and_open'] = all(
    r['route'] == s['route'] and r['documentStatus'] == 200 and not r['gotoError']
    and not r['pageErrors'] for r, s in zip(pages, source['rows'])) and len(pages) == 50
checks['runtime_all_1684_native_full_identities_match'] = all(
    set(urlsplit(url).path.removeprefix('/WOW-Encyclopedia-Deployable-Archive')
        for url in r['dom']['shotList']) ==
    {'/' + t['path'] for t in s['targets'] if t['kind'] == 'full'}
    for r, s in zip(pages, source['rows']))
visible = []
previews = 0
collections = 0
for r in pages:
    imgs = r['dom']['galleryImages']
    missing = sum(x['route'] == '/__offline/missing-image.svg' and
                  parse_qs(urlsplit(x['src']).query).get('reason') == ['dynamic-image-uncollected']
                  for x in imgs)
    visible.append({'gallery': r['label'], 'visible_native_slots': len(imgs),
                    'missing_placeholders': missing})
    previews += sum(x.get('complete') and x.get('naturalWidth', 0) > 16
                    for x in r['dom']['guidePreviewImages'])
    collections += sum(x.get('complete') and x.get('naturalWidth', 0) > 16
                       and 'guide image' in x.get('alt', '').lower()
                       for x in r['dom']['allImages'])
checks['all_50_visible_native_grids_are_missing_placeholders'] = all(
    x['visible_native_slots'] > 0 and x['visible_native_slots'] == x['missing_placeholders']
    for x in visible)
checks['22_preview_and_39_guide_images_decoded'] = previews == 22 and collections == 39
checks['51_documents_no_external_requests_or_page_errors'] = (
    len(browser['results']) == 51 and all(not r['blockedExternalRequests'] and not r['pageErrors']
                                        for r in browser['results']))
result = {
    'schema': 'root-player-gallery-history-browser-acceptance/v1',
    'checked_utc': datetime.now(timezone.utc).isoformat(), 'accepted': all(checks.values()),
    'checks': checks, 'saved_cdx_body_count': len(raw_bodies), 'saved_cdx_rows': raw_rows,
    'native_exact_index_rows': native_rows, 'raw_body_summaries': raw_bodies,
    'non_cdx_endpoint_error_bodies': non_cdx_bodies,
    'browser_50_visible_native_slots': sum(x['visible_native_slots'] for x in visible),
    'browser_visible_native_slots_are_missing': visible,
    'decoded_guide_previews': previews, 'decoded_guide_images': collections,
    'visual_review': {'reviewer': 'root', 'screenshots': [
        'karazhan.png', 'black-temple.png', 'fishing.png', 'lunar-festival.png'],
        'finding': 'Native grids show red-X placeholders; Fishing/Lunar adjacent guide panels remain separate.'},
    'browser_scope': 'Initial gallery page for all 50 plus ZulAman wrapper; all 3368 files checked separately. No claim of clicking every pagination or full-image link.',
    'new_network_requests': 0,
}
(BASE / 'root/history-browser-acceptance.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'accepted': result['accepted'], 'checks': checks,
                  'raw_bodies': len(raw_bodies), 'raw_rows': raw_rows,
                  'native_exact_rows': native_rows,
                  'visible_native_placeholders': result['browser_50_visible_native_slots']}, indent=2))
if not result['accepted']:
    raise SystemExit(1)

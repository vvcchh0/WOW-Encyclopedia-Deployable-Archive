"""Root independent byte/source and browser review for eight reused borders."""
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
REVIEW = ROOT / 'research/continuous-recovery-20261021/local-audit/talent-box-layout-review'
DEST = ROOT / 'research/continuous-recovery-20261021/integration/talent-box-layout'
DECISION = PUB / 'root-talent-box-layout-decision.json'
MAP = DEST / 'input-map.json'
assert not MAP.exists() and not DECISION.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
manifest_path = ROOT / '.scratch/offline-non-gallery-20261021-v16/build-manifest.json'
assert sha(manifest_path) == 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
manifest = read(manifest_path)
rows = {r['route']: r for r in manifest['files']}
dates = read(REVIEW / 'source-date-supplement.json')
prototype = read(REVIEW / 'review-decision.json')
assert prototype['decision'] == 'accept_layout_compatibility_reuse_only'
checks = prototype['browser_assertions']
for key in ('all_expected_names', 'no_page_errors', 'no_external_requests', 'no_failed_requests', 'no_bot_box_http_errors', 'all_boxes_closed', 'points_actions_changed', 'urls_have_no_query'):
    assert checks[key] is True, key
assert checks['route_fulfillments'] == 16
classes = ['druid','hunter','mage','paladin','priest','rogue','shaman','warlock','warrior']
pages = ['/info/classes/' + c + '/talents.html' for c in classes]
names = {'bot-left.gif','bot-right.gif','bot.gif','left.gif','right.gif','top-left.gif','top-right.gif','top.gif'}
assert {r['name'] for r in dates['records']} == names
entries = []
for record in dates['records']:
    row = rows[record['source_route']]
    payload = ROOT / row['output_path']
    source = ROOT / row['source_local_path']
    data = payload.read_bytes()
    assert data == source.read_bytes()
    assert len(data) == record['bytes'] == row['source_length'] == row['derived_length']
    assert sha(payload) == record['source_sha256'] == row['source_sha256'] == row['derived_sha256']
    assert row['actual_timestamp'] == record['actual_timestamp']
    assert row['source_base_url'] == record['source_base_url']
    assert row['transformed'] is False
    assert record['target_capture'] is None and record['classification'] == 'layout_compatibility_reuse'
    assert record['memento_url'] == 'https://web.archive.org/web/' + record['actual_timestamp'] + 'id_/' + row['source_base_url']
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        assert image.format == 'GIF' and image.n_frames == 1
        assert list(image.size) == record['dimensions']
    entries.append({
        'target_route': record['target_route'], 'source_route': record['source_route'],
        'page_routes': pages, 'source_original_url': row['source_base_url'],
        'source_capture_timestamp': row['actual_timestamp'],
        'source_memento_datetime': record['memento_datetime'],
        'sha256': row['source_sha256'], 'length': len(data), 'format': 'GIF',
        'dimensions': record['dimensions'], 'frames': 1,
        'layout_role': 'talent_points_box_' + record['name'].removesuffix('.gif'),
        'classification': 'layout_compatibility_reuse', 'target_capture_timestamp': None,
    })
entries.sort(key=lambda r: r['target_route'])
bindings = [manifest_path, REVIEW/'source-date-supplement.json', REVIEW/'browser-receipt-r1.json', REVIEW/'geometry-evidence.json', REVIEW/'review-decision.json']
decision = {
    'schema': 'wow-root-talent-box-layout-decision/v1',
    'accepted_for_compatibility_reuse': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'classification': 'layout_compatibility_reuse', 'new_image_payloads': 0,
    'target_original_images_recovered': 0, 'targets': entries,
    'decision': 'Eight missing talent point-box border routes reuse dated, untransformed same-site images already preserved under the old class includes directory. No image copies or HTML aliases.',
    'browser_basis': 'Druid and Warrior initial/add/reset states: closed 350 by 116.015625 pixel border, points 61/0 to 60/1 to 61/0, sixteen exact source-byte fulfillments, no external requests or page errors.',
    'root_visual_review': ['druid-points-after-add.png'],
    'scope': 'Nine talent pages only; these eight target captures remain unknown. No backgrounds, title strips, skill arrows or talent data are replaced.',
    'bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in bindings],
}
DECISION.write_text(json.dumps(decision, indent=2)+'\n', encoding='utf-8')
mapping = {
    'schema':'wow-talent-box-layout-map/v1', 'classification':'layout_compatibility_reuse',
    'source_manifest_sha256': sha(manifest_path), 'decision': DECISION.relative_to(ROOT).as_posix(),
    'decision_sha256': sha(DECISION), 'entries': entries,
}
DEST.mkdir(parents=True, exist_ok=True)
MAP.write_text(json.dumps(mapping, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'accepted':True, 'targets':len(entries), 'pages':len(pages), 'source_bytes':sum(e['length'] for e in entries), 'decision_sha256':sha(DECISION), 'map_sha256':sha(MAP)}))

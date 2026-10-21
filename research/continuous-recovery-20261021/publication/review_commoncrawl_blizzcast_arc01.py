"""Offline root checks for five source-indexed BlizzCast ARC entities."""
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
PACKET = ROOT / 'research/continuous-recovery-20261021/network/commoncrawl-blizzcast-arc01'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (PACKET / 'runtime').exists()
spec = importlib.util.spec_from_file_location('root_blizzcast_arc01', PACKET / 'commoncrawl_blizzcast_arc01.py')
driver = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = driver
spec.loader.exec_module(driver)
with contextlib.redirect_stdout(io.StringIO()):
    fixture = driver._fixture()
assert fixture['all_passed'] and fixture['case_count'] == 21
bindings = json.loads((PACKET / 'input-bindings.json').read_bytes())
for key in ['plan', 'runner', 'fixture', 'source_metadata', 'arc_parser']:
    assert bindings[key]['sha256'] == sha(ROOT / bindings[key]['path'])
plan = driver.validate_plan()
assert len(plan['target']['entities']) == 5
source = json.loads((PUB / 'commoncrawl-B01-curated-metadata.json').read_bytes())
source_rows = {r['source_cdxj_line']: r for r in source['items']}
for entity in plan['target']['entities']:
    original = source_rows[entity['source_cdxj_line']]
    assert entity['url'] == original['metadata']['url'] and entity['timestamp'] == original['timestamp']
    for field in ['filename', 'digest', 'mime']:
        assert entity[field] == original['metadata'][field]
    assert entity['offset'] == int(original['metadata']['offset']) and entity['length'] == int(original['metadata']['length'])
    assert entity['timestamp'] < '20080516000000' and '/episode3' not in entity['url']
assert [e['source_cdxj_line'] for e in plan['target']['entities']] == [464, 466, 467, 465, 469]
now = datetime.now(timezone.utc)
assert now < datetime(2026, 10, 21, 12, 45, 7, tzinfo=timezone.utc)
gate = {
    'accepted': True, 'root_go': True, 'batch_id': plan['batch_id'],
    'checked_utc': now.isoformat(), 'valid_until': (now + timedelta(minutes=10)).isoformat(),
    'plan_sha256': sha(PACKET / 'plan.json'), 'runner_sha256': sha(PACKET / 'commoncrawl_blizzcast_arc01.py'),
    'fixture_sha256': sha(PACKET / 'fixture-results.json'), 'input_bindings_sha256': sha(PACKET / 'input-bindings.json'),
    'source_metadata_sha256': sha(PUB / 'commoncrawl-B01-curated-metadata.json'),
    'arc_parser_sha256': sha(ROOT / 'tools/commoncrawl_arc.py'),
    'offline_fixture_cases': 21, 'scope': 'Five exact BlizzCast ARC members; May15 directory and homepage explicitly post-baseline; no August episode',
    'maximum_http_attempts': 10, 'maximum_batch_seconds': 600, 'parent_timeout_seconds': 660,
    'maximum_response_bytes': 1048576, 'maximum_total_body_bytes': 8388608,
    'maximum_inflate_bytes_per_entity': 8388608, 'minimum_start_interval_seconds': 5.5,
    'disk_floor_bytes': 11005853696, 'root_review_network_requests': 0, 'wayback_resume': False,
    'publication_authorized_by_this_gate': False,
}
output = PUB / 'root-commoncrawl-blizzcast-arc01-execute-go.json'
assert not output.exists()
output.write_text(json.dumps(gate, indent=2) + '\n', encoding='utf-8')
print(json.dumps(gate))

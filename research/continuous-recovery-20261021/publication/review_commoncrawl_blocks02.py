"""Root review of four never-requested CDXJ blocks, without live network."""
import contextlib
import hashlib
import importlib.util
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
PACKET = ROOT / 'research/continuous-recovery-20261021/network/commoncrawl-blocks02'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert not (PACKET / 'runtime').exists()
spec = importlib.util.spec_from_file_location('root_blocks02', PACKET / 'commoncrawl_blocks02.py')
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
with contextlib.redirect_stdout(io.StringIO()):
    fixture = driver._fixture()
assert fixture['all_passed'] and fixture['case_count'] == 34
bindings = json.loads((PACKET / 'input-bindings.json').read_text(encoding='utf-8'))
for key, filename in [('plan', 'plan.json'), ('runner', 'commoncrawl_blocks02.py'), ('fixture', 'fixture-results.json')]:
    assert bindings[key]['sha256'] == sha(PACKET / filename), key
plan = driver.validate_plan()
source = json.loads((PUB / 'commoncrawl-selected-blocks02.json').read_text(encoding='utf-8'))
assert bindings['source_plan']['sha256'] == sha(PUB / 'commoncrawl-selected-blocks02.json')
approved = {(r['part'], r['offset'], r['length']) for r in source['blocks']}
actual = {(r['part'], r['offset'], r['length']) for r in plan['target']['blocks']}
assert approved == actual and len(actual) == 4 and sum(r[2] for r in actual) == 784310
assert {r['block_id'] for r in plan['target']['blocks']} == {'B02', 'B03', 'B04', 'B05'}
assert driver.classify_cdxj('com,worldofwarcraft)/media/music/index.html')['curated']
assert not driver.classify_cdxj('com,worldofwarcraft)/screenshots/images/raids/1.jpg')['curated']
assert not driver.classify_cdxj('com,wowarmory)/character-sheet.xml')['curated']
assert driver.classify_cdxj('com,wowarmory)/images/icons/a.png')['curated']
now = datetime.now(timezone.utc)
assert now < datetime(2026, 10, 21, 12, 45, 7, tzinfo=timezone.utc)
gate = {
    'accepted': True, 'root_go': True, 'batch_id': plan['batch_id'],
    'checked_utc': now.isoformat(), 'valid_until': (now + timedelta(minutes=10)).isoformat(),
    'plan_sha256': sha(PACKET / 'plan.json'),
    'runner_sha256': sha(PACKET / 'commoncrawl_blocks02.py'),
    'fixture_sha256': sha(PACKET / 'fixture-results.json'),
    'input_bindings_sha256': sha(PACKET / 'input-bindings.json'),
    'source_plan_sha256': sha(PUB / 'commoncrawl-selected-blocks02.json'),
    'offline_fixture_cases': 34, 'root_additional_checks': 7,
    'scope': 'Four fixed Common Crawl CDXJ ranges; B01 excluded; metadata only',
    'maximum_http_attempts': 8, 'maximum_batch_seconds': 480, 'parent_timeout_seconds': 540,
    'maximum_response_bytes': 524288, 'maximum_total_body_bytes': 8388608,
    'maximum_decompressed_bytes_per_block': 16777216,
    'minimum_start_interval_seconds': 5.25, 'disk_floor_bytes': 11005853696,
    'root_review_network_requests': 0, 'wayback_resume': False, 'image_payloads_authorized': 0,
}
output = PUB / 'root-commoncrawl-blocks02-execute-go.json'
assert not output.exists()
output.write_text(json.dumps(gate, indent=2) + '\n', encoding='utf-8')
print(json.dumps(gate))

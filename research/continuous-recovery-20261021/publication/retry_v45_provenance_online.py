"""Retry only the previously incomplete large object and retain both receipts."""
import hashlib
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OLD = PUB / 'root-v45-pages-online-acceptance.json'
FOCUSED = PUB / 'v45-provenance-online-retry01.json'
FINAL = PUB / 'root-v45-pages-online-reconciliation.json'
assert not FOCUSED.exists() and not FINAL.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = read(OLD)
assert old['accepted'] is False
failed = [r for r in old['objects'] if not r['accepted']]
assert len(old['objects']) == 45 and len(failed) == 1
assert failed[0]['path'] == 'export-provenance.json'
frozen = ROOT / 'research/continuous-recovery-20261018/publication/verify_pages_v32.py'
assert sha(frozen) == '82f9c2bce15c618e33d31bb583192a217a2f419d0e7cf85714f47709d5d09289'
for key in ('HTTPS_PROXY', 'HTTP_PROXY'):
    os.environ[key] = 'http://127.0.0.1:7890'
for key in ('NO_PROXY', 'no_proxy'):
    os.environ[key] = ''
spec = importlib.util.spec_from_file_location('focused_object_check', frozen)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.OUT = PUB
module.SITE = ROOT / old['local_site']
module.PUBLISH_REPORT = PUB / 'v45-pages-publication.json'
module.PROGRESS_REPORT = PUB / 'v45-provenance-retry01-progress.json'
module.FINAL_REPORT = FOCUSED
module.OBJECTS = [{'path': 'export-provenance.json', 'mime': {'application/json'}, 'source_list': True}]
module.MAX_ATTEMPTS = 2
module.MAX_SECONDS = 400
module.MAX_BODY_BYTES = 24 * 1024 * 1024
module.SOURCE_LIST_TIMEOUT = 180
original = module.run_attempt
def attempt(*args, **kwargs):
    result = original(*args, **kwargs)
    if result.get('http_status') in (429, 503):
        (PUB / 'v45-provenance-retry01-endpoint-stop.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        raise RuntimeError('Hosted endpoint limit: stop without proxy retry')
    return result
module.run_attempt = attempt
code = module.main()
fresh = read(FOCUSED)
assert code == 0 and fresh['accepted']
new = fresh['objects'][0]
assert new['path'] == failed[0]['path'] and new['accepted']
assert new['local_bytes'] == failed[0]['local_bytes']
assert new['local_sha256'] == failed[0]['local_sha256']
assert fresh['expected_pages_commit'] == old['expected_pages_commit']
accepted = [r for r in old['objects'] if r['accepted']] + [new]
assert len(accepted) == 45 and len({r['path'] for r in accepted}) == 45
FINAL.write_text(json.dumps({
    'schema': 'wow-pages-online-reconciliation/v1', 'accepted': True, 'version': 'v45',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'expected_pages_commit': fresh['expected_pages_commit'], 'local_site': old['local_site'],
    'accepted_objects': 45, 'reused_previously_accepted_objects': 44,
    'newly_completed_objects': [new], 'build_before': fresh['build_before'], 'build_after': fresh['build_after'],
    'prior_receipt': OLD.relative_to(ROOT).as_posix(), 'prior_receipt_sha256': sha(OLD),
    'focused_receipt': FOCUSED.relative_to(ROOT).as_posix(), 'focused_receipt_sha256': sha(FOCUSED),
    'reason': 'Previous HTTP200 transfers ended at the 60-second timeout. Only the incomplete object was retried with a 180-second bound; all prior attempts remain preserved.',
}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'accepted': True, 'completed_objects': 45, 'reconciliation_sha256': sha(FINAL)}))

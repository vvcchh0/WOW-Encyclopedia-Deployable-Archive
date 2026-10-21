"""Fresh read-only GitHub, frozen-manifest and disk control for run closeout."""
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-v52-closeout-control.json'
assert not OUT.exists()
environment = os.environ.copy()
environment.update(HTTPS_PROXY='http://127.0.0.1:7890', HTTP_PROXY='http://127.0.0.1:7890',
                   NO_PROXY='', no_proxy='', GH_PROMPT_DISABLED='1')
def command(args):
    return subprocess.check_output(args, cwd=ROOT, env=environment, timeout=40, text=True).strip()
head = command(['git', 'rev-parse', 'HEAD'])
assert command(['git', 'rev-parse', 'origin/main']) == head
release_proof = json.loads((PUB / 'root-v52-release-publication.json').read_bytes())
assert release_proof['accepted'] and head == release_proof['target_commit']
pages = json.loads(command(['gh', 'api', 'repos/vvcchh0/WOW-Encyclopedia-Deployable-Archive/pages/builds/latest']))
assert pages['status'] == 'built' and pages['commit'] == 'd46c14a0d655cf55a2608581441726845537a1f4'
latest = json.loads(command(['gh', 'api', 'repos/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/latest']))
assert latest['draft'] is False and latest['tag_name'] == release_proof['tag']
assert latest['id'] == release_proof['release_id']
assets = {row['name']: row for row in latest['assets']}
assert len(assets) == 3
for row in release_proof['assets']:
    actual = assets[row['name']]
    assert actual['state'] == 'uploaded' and actual['size'] == row['bytes'] and actual['digest'] == row['digest']
baseline = json.loads((PUB / 'root-baseline-acceptance.json').read_bytes())
frozen = list(baseline['frozen_bindings']) + [{
    'path': '.scratch/offline-non-gallery-20261021-v16/build-manifest.json',
    'sha256': 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a',
}]
bindings = []
for row in frozen:
    path = ROOT / row['path']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == row['sha256'], row['path']
    bindings.append({'path': row['path'], 'bytes': path.stat().st_size, 'sha256': digest})
free = shutil.disk_usage(ROOT).free
assert free >= 11005853696
report = {
    'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'main_commit_before_final_documentation': head,
    'pages': {'status': pages['status'], 'commit': pages['commit'], 'updated_at': pages['updated_at']},
    'latest_release': {'id': latest['id'], 'tag': latest['tag_name'], 'draft': latest['draft'],
                       'assets_matching_prior_publication': 3},
    'frozen_manifest_bindings': bindings, 'disk_free_bytes': free,
    'network_scope': 'Two read-only GitHub API calls; no source acquisition',
}
OUT.write_bytes((json.dumps(report, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'latest_release': latest['tag_name'],
                  'pages_commit': pages['commit'], 'disk_free_bytes': free}))

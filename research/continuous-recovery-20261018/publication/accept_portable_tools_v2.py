"""Record root's local review and focused recovery validation, without packaging."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
BASE = RUN / 'integration/portable-release-tools'
NEW = RUN / 'integration/portable-release-tools-v2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = RUN / 'publication/root-portable-release-tools-v2-acceptance.json'
assert not out.exists()
for n in ['portable_release_common.py', 'check_portable.py', 'create_upload_release.py', 'README.md']:
    assert (BASE/n).read_bytes() == (NEW/n).read_bytes(), n
old = (BASE/'publish_release.py').read_text(encoding='utf-8')
new = (NEW/'publish_release.py').read_text(encoding='utf-8')
expected = old.replace('    assert config.get("draft") is False\n',
    '    # The saved config can still say draft=True when GitHub published the\n'
    '    # release but the edit response or subsequent verification was lost.\n'
    '    # Ownership is proven by the exact saved id/tag/target and asset bindings.\n'
    '    assert config.get("draft") in (True, False)\n').replace(
    '    if config.get("draft") is False:\n', '    if data.get("draft") is False:\n')
assert new == expected
receipt = {
    'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'files': {p.name: {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in NEW.iterdir() if p.is_file()},
    'root_validation': [
        'Reviewed v1 checker, creator and publisher; all 8 offline tests passed independently including actual accepted v32 receipts and smoke path existence.',
        'v2 only changes publisher recovery dispatch to the actual remote draft flag and permits stale saved draft=true with the exact owned id/tag/target/portable SHA/three asset digests.',
        'Both focused v2 recovery tests passed. Full main exercised with mocked GitHub reads, stale draft=true, and remote draft=false; only local git rev-parse commands occurred and no publish/upload command was called.',
        'All unchanged helper files compared byte-for-byte against reviewed v1. v1 preserved.'
    ],
    'network_requests': 0, 'archives_created': 0, 'github_mutations': 0,
    'remaining_execution': 'Run package producer and full member/extracted server checker on the final accepted export, then exact-main-target draft upload and publication verification before the deadline.',
}
out.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'accepted': True, 'sha256': sha(out)}))

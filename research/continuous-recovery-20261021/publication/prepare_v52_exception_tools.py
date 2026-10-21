"""Prepare one bounded local-only export exception for the verified Arathi directory defect."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
HERE = ROOT / 'research/continuous-recovery-20261021/integration/v52'
OUT = PUB / 'root-v52-bounded-exception-decision.json'
assert not OUT.exists() and not HERE.exists()
report_path = ROOT / 'research/continuous-recovery-20261021/local-audit/underdev-final-routing-review/underdev-final-routing-review.json'
report = json.loads(report_path.read_bytes())
assert len(report['targets']) == 22
assert sum(row['route_map_exact_exists'] for row in report['targets']) == 20
assert datetime.now(timezone.utc) < datetime(2026, 10, 21, 13, 28, tzinfo=timezone.utc)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
decision = {
    'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'reason': 'New closeout evidence identifies 20 exact already-collected Arathi guide thumbnails hidden by one page-scoped directory-base conversion. This is a bounded local repair, not renewed screenshot acquisition.',
    'plan_revision': 'One local v52 export may start before13:35 UTC despite the earlier13:05 planning cutoff. Source acquisition remains closed. Preserve v51 and all accepted historical outputs.',
    'hard_user_deadline_utc': '2026-10-21T14:25:07+00:00',
    'v52_export_start_cutoff_utc': '2026-10-21T13:35:00+00:00',
    'v52_export_timeout_seconds': 540,
    'release_cutoff_utc': '2026-10-21T14:10:00+00:00',
    'fallback': 'If time or acceptance fails, retain the published v51 and report the pending narrow repair without overwriting accepted versions.',
    'network_source_requests': 0,
    'source_report': report_path.relative_to(ROOT).as_posix(),
    'source_report_sha256': sha(report_path),
}
HERE.mkdir()
source = ROOT / 'research/continuous-recovery-20261021/integration/v51/export_v51_once.py'
text = source.read_text(encoding='utf-8').replace('v51', 'v52').replace('v50', 'v51')
text = text.replace('root-v49-pages-online-acceptance.json', 'root-v51-pages-online-acceptance.json')
text = text.replace('root-v49-local-acceptance.json', 'root-v51-local-acceptance.json')
text = text.replace('13, 5, 7, tzinfo=timezone.utc', '13, 35, 0, tzinfo=timezone.utc')
text = text.replace('Build v52 from accepted v51 with one exact existing-image route alias.',
                    'Build v52 from accepted v51 with one exact Arathi directory-base repair.')
text = text.replace('One exact T.gif compatibility route reuses the accepted April 23 2008 GIF. Existing lore, page HTML, images and scripts are preserved.',
                    'Preserve the verified Arathi resource directory on its exact guide page. All image bytes and every unrelated page remain unchanged; no new source acquisition.')
target = HERE / 'export_v52_once.py'
target.write_bytes(text.encode())
wrapper_source = PUB / 'execute_v51_once.py'
wrapper = PUB / 'execute_v52_once.py'
assert not wrapper.exists()
wrapper.write_bytes(wrapper_source.read_text(encoding='utf-8').replace('v51', 'v52').encode())
verifier_source = PUB / 'verify_accepted_pages.py'
verifier = PUB / 'verify_v52_pages.py'
assert not verifier.exists()
text = verifier_source.read_text(encoding='utf-8')
old = "'v49','v50','v51'}"
assert old in text
text = text.replace(old, "'v49','v50','v51','v52'}")
verifier.write_bytes(text.encode())
decision['prepared_tools'] = [
    {'source': p.relative_to(ROOT).as_posix(), 'source_sha256': sha(p),
     'target': q.relative_to(ROOT).as_posix(), 'target_sha256': sha(q)}
    for p, q in ((source, target), (wrapper_source, wrapper), (verifier_source, verifier))
]
OUT.write_bytes((json.dumps(decision, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'exception': 'one local Arathi guide directory repair',
                  'tools_prepared': 3, 'source_downloads': 0}))

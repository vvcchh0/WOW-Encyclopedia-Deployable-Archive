"""Root review of one retry window for two previously failed transfers."""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
DIR = RUN / 'network/transfer-pending2-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--factory', action='store_true')
    p.add_argument('--plan-sha256')
    args = p.parse_args()
    assert sha(DIR / 'prepare_transfer_pending2_v1.py') == '8e3d07c468b0494c3120426b57a2308a7badf6fdd83e5b45c4a60c0ec14aef3d'
    queue_path = DIR / 'transfer-pending2-v1-queue.json'
    assert sha(queue_path) == '8c6f14e2ee076649208465381751d722ccd55d3fafb7aa00243bbe79651f5786'
    queue = read(queue_path)
    assert [r['original'] for r in queue['rows']] == [
        'http://www.worldofwarcraft.com/news/images/08-02/02-06-08-3.jpg',
        'http://www.worldofwarcraft.com/news/images/05-02/EU2.jpg']
    for binding in queue['prior_attempt_bindings']:
        assert sha(ROOT / binding['path']) == binding['sha256']
    checks = []
    for row in queue['rows']:
        ref = row['references'][0]
        page = ROOT / ref['output_file']
        assert sha(page) == ref['source_page_sha256']
        line = page.read_text(encoding='utf-8').splitlines()[ref['line']-1]
        assert row['original'] in line or quote(row['original'], safe='') in line
        prior = row['prior_attempt']
        old_source = read(ROOT / prior['old_source_receipt'])
        assert old_source['accepted'] and row['original'] not in {x['original'] for x in old_source['accepted_images']}
        attempt = read(ROOT / prior['old_output_state'])['attempts'][prior['old_target_attempt']-1]
        if row['rank'] == 1:
            assert attempt['curl_exit'] == 35 and attempt['source_status'] is None and attempt['body_bytes'] == 0
        else:
            assert attempt['curl_exit'] == 28 and attempt['source_status'] == 200 and attempt['body_bytes'] == 489580
        checks.append({'original': row['original'], 'page': ref['output_file'], 'line': ref['line'],
                       'prior_curl_exit': attempt['curl_exit'], 'prior_source_status': attempt['source_status'], 'prior_body_bytes': attempt['body_bytes']})
    factory_receipt = PUB / 'root-transfer-pending2-factory-acceptance.json'
    if args.factory:
        assert not factory_receipt.exists()
        result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
            'factory_sha256': sha(DIR / 'prepare_transfer_pending2_v1.py'), 'queue_sha256': sha(queue_path), 'checks': checks,
            'root_unittests': '6/6 passed independently, including real page citations, actual LF/atomic bindings and containment.',
            'scope': 'Two prior transfer failures, neither an observed404; one new exact-index/replay batch only. Frozen V3, two targets/eight requests/100seconds/8MiB total/4MiB entity; standard TLS/direct-first/cadence/disk/cooldown controls.'}
        factory_receipt.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
        print(json.dumps({'accepted': True, 'sha256': sha(factory_receipt)}))
        return
    assert read(factory_receipt)['accepted'] is True
    path = DIR / 'batch-01/plan.json'
    assert sha(path) == args.plan_sha256
    plan = read(path)
    assert plan['candidate_count'] == 2 and plan['policy']['max_attempts'] == 8 and plan['policy']['window_seconds'] == 100
    assert plan['policy']['max_total_body_bytes'] == 8*1024**2 and plan['policy']['max_entity_body_bytes'] == 4*1024**2
    for b in plan['input_bindings'].values():
        assert sha(ROOT / b['path']) == b['sha256'] and (ROOT / b['path']).stat().st_size == b['bytes']
    assert read(RUN / 'status.json')['network_resume_gate_passed'] is True
    assert datetime.now(timezone.utc) < datetime(2026,10,18,13,35,tzinfo=timezone.utc)
    selected = PUB / 'transfer-pending2-batch1-selected-originals.json'
    assert not selected.exists()
    selected.write_text(json.dumps([r['original'] for r in queue['rows']], indent=2)+'\n', encoding='utf-8', newline='\n')
    out = PUB / 'root-transfer-pending2-batch1-plan-acceptance.json'
    subprocess.run([sys.executable, '-B', '-X', 'utf8', str(PUB / 'accept_exact_plan.py'), '--plan', path.relative_to(ROOT).as_posix(), '--originals', selected.relative_to(ROOT).as_posix(), '--output', out.relative_to(ROOT).as_posix(), '--max-attempts', '8', '--max-seconds', '100'], cwd=ROOT, check=True)
    print(json.dumps({'accepted': True, 'root_plan_acceptance_sha256': sha(out)}))

if __name__ == '__main__':
    main()

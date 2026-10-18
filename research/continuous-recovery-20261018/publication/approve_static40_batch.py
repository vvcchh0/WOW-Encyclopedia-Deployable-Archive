"""Root source review of the 40 literal static image targets and bounded plans."""
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
DIR = RUN / 'network/static40-v32'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--factory', action='store_true')
    p.add_argument('--batch-index', type=int)
    p.add_argument('--plan-sha256')
    args = p.parse_args()
    assert sha(DIR / 'prepare_static40.py') == '494abcf87d60439bffebaa74d9ab85eaf54da461f04d7d0708667597a65d15b5'
    assert sha(DIR / 'static40-source-queue.json') == '8cd75a65935eb416ab12ed70fa1b2f86335939a409173df899bdb7f8d48d95f9'
    queue = read(DIR / 'static40-source-queue.json')
    audit_path = ROOT / queue['source_audit']['path']
    assert sha(audit_path) == queue['source_audit']['sha256'] == '72c00aa28e7c19c86de7f877983d049662f543be48960d2879a0f566bf15657f'
    candidates = read(audit_path)['candidates']
    assert [r['candidate'] for r in queue['rows']] == candidates[:10] + candidates[11:]
    assert queue['excluded_targets'][0]['candidate'] == candidates[10]
    assert queue['excluded_targets'][0]['requested_url'] == 'http://www.worldofwarcraft.com/info/basics/images/small pets/icon.gif'
    prov = read(ROOT / '.scratch/pages-resources-20261018-v32/export-provenance.json')
    provenance = {x['output_path']: x for x in prov['files']}
    checks = []
    for row in queue['rows']:
        original = row['requested_url']
        assert not any(c.isspace() for c in original)
        for ref in row['candidate']['references']:
            page = ROOT / ref['output_file']
            relative = page.relative_to(ROOT / '.scratch/pages-resources-20261018-v32').as_posix()
            assert sha(page) == ref['source_page_sha256'] == provenance[relative]['derived_sha256']
            line = page.read_text(encoding='utf-8').splitlines()[ref['line'] - 1]
            assert original in line or quote(original, safe='') in line
            checks.append({'rank': row['queue_rank'], 'candidate_rank': row['candidate_priority_rank'], 'page': relative, 'line': ref['line'], 'original': original})
    factory_receipt = PUB / 'root-static40-factory-acceptance.json'
    if args.factory:
        assert not factory_receipt.exists()
        receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
            'factory_sha256': sha(DIR / 'prepare_static40.py'), 'queue_sha256': sha(DIR / 'static40-source-queue.json'),
            'root_independent_unittests': '7/7 passed, actual atomic LF SHA/length and escape cleanup included', 'checks': checks,
            'scope': 'Forty actual v32 static-marker image URLs; exact unchanged audit rows except one literal-space URL deferred; frozen V3 execution, 10 targets per batch, 24 requests/240 seconds/16MiB, direct-first, TLS, no redirects, cadence, disk and cooldown gates reviewed.'}
        factory_receipt.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
        print(json.dumps({'accepted': True, 'sha256': sha(factory_receipt), 'references': len(checks)}))
        return
    assert read(factory_receipt)['accepted'] is True
    n = args.batch_index
    assert n is not None and 1 <= n <= 4
    path = DIR / f'batch-{n:02d}/plan.json'
    assert sha(path) == args.plan_sha256
    plan = read(path)
    rows = queue['rows'][(n-1)*10:n*10]
    assert [x['original'] for x in plan['candidates']] == [r['requested_url'] for r in rows]
    for candidate, row in zip(plan['candidates'], rows):
        assert candidate['queue_rank'] == row['queue_rank']
        assert candidate['source_page_context']['references'] == row['candidate']['references']
    for b in plan['input_bindings'].values():
        assert sha(ROOT / b['path']) == b['sha256'] and (ROOT / b['path']).stat().st_size == b['bytes']
    assert read(RUN / 'status.json')['network_resume_gate_passed'] is True
    assert datetime.now(timezone.utc) < datetime(2026,10,18,13,35,tzinfo=timezone.utc)
    selected = PUB / f'static40-batch{n}-selected-originals.json'
    assert not selected.exists()
    selected.write_text(json.dumps([r['requested_url'] for r in rows], indent=2)+'\n', encoding='utf-8', newline='\n')
    output = PUB / f'root-static40-batch{n}-plan-acceptance.json'
    subprocess.run([sys.executable, '-B', '-X', 'utf8', str(PUB / 'accept_exact_plan.py'), '--plan', path.relative_to(ROOT).as_posix(), '--originals', selected.relative_to(ROOT).as_posix(), '--output', output.relative_to(ROOT).as_posix()], cwd=ROOT, check=True)
    print(json.dumps({'accepted': True, 'root_plan_acceptance_sha256': sha(output)}))

if __name__ == '__main__':
    main()

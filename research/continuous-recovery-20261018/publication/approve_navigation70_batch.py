"""Root acceptance of the corrected offline factory and exact referenced batches."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
FACTORY = RUN / 'network/navigation70-v32/prepare_navigation70.py'
FACTORY_SHA = 'abb37bc6bcc56e371e194236e825036545c535d05a05362813320ac2d46ebc9a'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--factory', action='store_true')
    p.add_argument('--batch-index', type=int)
    p.add_argument('--plan-sha256')
    args = p.parse_args()
    assert sha(FACTORY) == FACTORY_SHA
    queue_path = PUB / 'navigation-link-selected70.json'
    assert sha(queue_path) == '6d981e640ee377cac493e69d8a6152725fffe9ff1aa1e0585035a170bebb31fc'
    queue = read(queue_path)
    provenance = {x['output_path']: x for x in read(ROOT / queue['source_provenance']['path'])['files']}
    checks = []
    for row in queue['rows']:
        for original, refs, role in [(row['original'], row['references'], 'primary')] + [
            (a['original'], a['references'], 'alternate_context_only') for a in row['alternate_navigation_links']]:
            for ref in refs:
                file = ROOT / ref['output_file']
                relative = file.relative_to(ROOT / '.scratch/pages-resources-20261018-v30').as_posix()
                assert sha(file) == ref['source_page_sha256'] == provenance[relative]['derived_sha256']
                line = file.read_text(encoding='utf-8').splitlines()[ref['line'] - 1]
                assert original in line or quote(original, safe='') in line
                checks.append({'rank': row['rank'], 'page': relative, 'line': ref['line'], 'original': original, 'role': role})
    factory_receipt = PUB / 'root-navigation70-factory-acceptance.json'
    if args.factory:
        assert not factory_receipt.exists()
        assert len(checks) == 84
        receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
            'factory_sha256': FACTORY_SHA, 'queue_sha256': sha(queue_path), 'network_requests': 0,
            'root_independent_unittest_result': '11/11 pass, including actual atomic serialized file SHA/length and escape refusal',
            'checks': checks, 'scope': 'Root read corrected writer, boundary checks, policy, live bindings and source citations. Initial Windows newline finding and preparation receipt retained.'}
        factory_receipt.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
        print(json.dumps({'accepted': True, 'factory_sha256': FACTORY_SHA, 'receipt_sha256': sha(factory_receipt)}))
        return
    assert read(factory_receipt)['accepted'] and read(factory_receipt)['factory_sha256'] == FACTORY_SHA
    n = args.batch_index
    assert n is not None and 1 <= n <= 7
    plan_path = RUN / f'network/navigation70-v32/batch-{n:02d}/plan.json'
    assert sha(plan_path) == args.plan_sha256
    plan = read(plan_path)
    selected = queue['rows'][(n-1)*10:n*10]
    assert [x['original'] for x in plan['candidates']] == [x['original'] for x in selected]
    for row, candidate in zip(selected, plan['candidates']):
        assert candidate['queue_rank'] == row['rank']
        assert candidate['source_page_context']['queue_row'] == row
        assert len(candidate['all_references']) == len(row['references'])
        for ref, actual in zip(row['references'], candidate['all_references']):
            assert actual['path'] == ref['output_file'] and actual['sha256'] == ref['source_page_sha256']
            assert actual['line'] == ref['line'] and actual['literal'] == row['original']
    for binding in plan['input_bindings'].values():
        assert sha(ROOT / binding['path']) == binding['sha256']
        assert (ROOT / binding['path']).stat().st_size == binding['bytes']
    now = datetime.now(timezone.utc)
    assert now < datetime(2026, 10, 18, 13, 35, tzinfo=timezone.utc)
    assert read(RUN / 'status.json')['network_resume_gate_passed'] is True
    originals = PUB / f'navigation70-batch{n}-selected-originals.json'
    assert not originals.exists()
    originals.write_text(json.dumps([x['original'] for x in selected], indent=2)+'\n', encoding='utf-8', newline='\n')
    output = PUB / f'root-navigation70-batch{n}-plan-acceptance.json'
    subprocess.run([sys.executable, '-B', '-X', 'utf8', str(PUB / 'accept_exact_plan.py'), '--plan', plan_path.relative_to(ROOT).as_posix(),
                    '--originals', originals.relative_to(ROOT).as_posix(), '--output', output.relative_to(ROOT).as_posix()], cwd=ROOT, check=True)
    print(json.dumps({'root_plan_acceptance_sha256': sha(output), 'selected': len(selected)}))

if __name__ == '__main__':
    main()

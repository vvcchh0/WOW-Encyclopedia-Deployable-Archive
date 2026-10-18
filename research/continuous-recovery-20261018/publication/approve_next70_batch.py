"""Root gate for one explicitly selected, immutable next70 plan; no network."""
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
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-index', required=True, type=int)
    parser.add_argument('--plan-sha256', required=True)
    args = parser.parse_args()
    assert 1 <= args.batch_index <= 7
    queue = PUB / 'next-frontier-selected70.json'
    factory = RUN / 'network/next-frontier70-v29/prepare_next_frontier70.py'
    assert sha(queue) == '654135870971139ac04427119bcf01d4d9981af60d182f068b7da6a99187551a'
    assert sha(factory) == '55be7c2cb2f0291093a397a7d54b413c1a41811d155e33f5ad841ef46a4f65a6'
    status = read(RUN / 'status.json')
    assert status['network_resume_gate_passed'] is True
    cooldown = status.get('network_cooldown_not_before_utc')
    if cooldown:
        assert datetime.now(timezone.utc) >= datetime.fromisoformat(cooldown.replace('Z', '+00:00'))
    number = args.batch_index
    plan = RUN / f'network/next-frontier70-v29/batch-{number:02d}/plan.json'
    assert sha(plan) == args.plan_sha256
    rows = read(queue)['rows'][(number - 1) * 10:number * 10]
    candidates = {x['original']: x for x in read(plan)['candidates']}
    for row in rows:
        citations = candidates[row['original']]['all_references']
        assert len(citations) == len(row['references'])
        for ref, citation in zip(row['references'], citations):
            source = ROOT / ref['output_file']
            source.resolve().relative_to(ROOT.resolve())
            assert sha(source) == ref['source_page_sha256'] == citation['sha256']
            assert citation['path'] == ref['output_file'] and citation['line'] == ref['line']
            line = source.read_text(encoding='utf-8').splitlines()[ref['line'] - 1]
            assert row['original'] in line or quote(row['original'], safe='') in line
    selected = PUB / f'next70-batch{number}-selected-originals.json'
    originals = [x['original'] for x in rows]
    if selected.exists():
        assert read(selected) == originals
    else:
        selected.write_text(json.dumps(originals, indent=2) + '\n', encoding='utf-8')
    output = PUB / f'root-next70-batch{number}-plan-acceptance.json'
    subprocess.run([sys.executable, '-X', 'utf8', str(PUB / 'accept_exact_plan.py'),
                    '--plan', plan.relative_to(ROOT).as_posix(),
                    '--originals', selected.relative_to(ROOT).as_posix(),
                    '--output', output.relative_to(ROOT).as_posix()], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()

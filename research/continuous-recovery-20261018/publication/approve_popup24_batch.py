"""Root verification of real relative popup links before exact-image retrieval."""
import argparse
import datetime as dt
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin

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
    assert 1 <= args.batch_index <= 3
    queue, urls = PUB / 'popup24-selected-queue.json', PUB / 'popup24-original-urls.txt'
    assert sha(queue) == 'e3e708048aff5fce88cbb65f96fdc0ed6f08817f21598c71c0db7fff550153ad'
    assert sha(urls) == 'd64d8f6eddba957261d3b59fa8dac6544c05bd3c452d84abf6196967ab64d561'
    factory = RUN / 'network/popup24-v30/prepare_popup24.py'
    assert sha(factory) == 'ae831e704583fd64884b3d4252fe0176c252b11dce841fafe2185e534eac08d5'
    status = read(RUN / 'status.json')
    assert status['network_resume_gate_passed'] is True
    now = dt.datetime.now(dt.timezone.utc)
    assert now < dt.datetime(2026, 10, 18, 13, 35, tzinfo=dt.timezone.utc)
    if status.get('network_cooldown_not_before_utc'):
        assert now >= dt.datetime.fromisoformat(status['network_cooldown_not_before_utc'].replace('Z', '+00:00'))
    provenance_path = ROOT / '.scratch/pages-resources-20261018-v30/export-provenance.json'
    manifest_path = ROOT / '.scratch/offline-navigation-20261015-v15/build-manifest.json'
    assert sha(provenance_path) == 'b04eb866bd7d21aa23ce8ad064eeb55b8b263e84147bb3755f4af7df84825d85'
    assert sha(manifest_path) == 'd89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002'
    provenance = {x['output_path']: x for x in read(provenance_path)['files']}
    manifest = read(manifest_path)
    source_records = manifest.get('records') or manifest.get('files')
    if isinstance(source_records, dict):
        source_by_route = source_records
    else:
        source_by_route = {x['route']: x for x in source_records}
    number = args.batch_index
    plan = RUN / f'network/popup24-v30/batch-{number:02d}/plan.json'
    assert sha(plan) == args.plan_sha256
    rows = read(queue)['rows'][(number - 1)*10:number*10]
    candidates = {x['original']: x for x in read(plan)['candidates']}
    assert set(candidates) == {x['original'] for x in rows}
    checks = []
    for row in rows:
        original, literal, base = row['original'], row['literal_popup_argument'], row['source_base_url']
        assert urljoin(base, literal) == original
        candidate = candidates[original]
        primary = candidate['source_evidence']
        assert primary['kind'] == 'derived_resolved_url_list' and primary['path'] == urls.relative_to(ROOT).as_posix()
        assert primary['sha256'] == sha(urls) and primary['literal'] == original
        assert urls.read_text().splitlines()[primary['line']-1] == original
        assert len(candidate['all_references']) == len(row['references'])
        assert candidate['source_page_context']['literal_popup_argument'] == literal
        for ref, citation in zip(row['references'], candidate['all_references']):
            page = (ROOT / ref['output_file']).resolve()
            relative = page.relative_to(ROOT / '.scratch/pages-resources-20261018-v30').as_posix()
            record = provenance[relative]
            assert sha(page) == ref['source_page_sha256'] == record['derived_sha256'] == citation['sha256']
            assert citation['path'] == ref['output_file'] and citation['line'] == ref['line']
            line = html.unescape(page.read_text(encoding='utf-8').splitlines()[ref['line']-1])
            assert re.search(r'popUpOmega\(\s*([\'\"])' + re.escape(literal) + r'\1', line), (relative, literal)
            assert source_by_route[record['route']]['source_base_url'] == base
            checks.append({'page': relative, 'page_sha256': sha(page), 'line': ref['line'],
                           'relative_argument': literal, 'source_base_url': base, 'resolved_original': original})
    selected = PUB / f'popup24-batch{number}-selected-originals.json'
    assert not selected.exists()
    selected.write_text(json.dumps([x['original'] for x in rows], indent=2)+'\n', encoding='utf-8')
    output = PUB / f'root-popup24-batch{number}-plan-acceptance.json'
    subprocess.run([sys.executable, '-X', 'utf8', str(PUB / 'accept_exact_plan.py'), '--plan', plan.relative_to(ROOT).as_posix(),
                    '--originals', selected.relative_to(ROOT).as_posix(), '--output', output.relative_to(ROOT).as_posix()], cwd=ROOT, check=True)
    derived = PUB / f'root-popup24-batch{number}-relative-source-acceptance.json'
    assert not derived.exists()
    derived.write_text(json.dumps({'accepted': True, 'network_requests': 0, 'plan_sha256': sha(plan),
        'plan_acceptance_sha256': sha(output), 'queue_sha256': sha(queue), 'checks': checks,
        'scope': 'Actual relative popUpOmega arguments resolved against frozen source_base_url. The full URL list is derived evidence, not a literal original-page URL or availability evidence.'}, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'relative_sources_accepted': len(checks), 'receipt_sha256': sha(derived)}))

if __name__ == '__main__':
    main()

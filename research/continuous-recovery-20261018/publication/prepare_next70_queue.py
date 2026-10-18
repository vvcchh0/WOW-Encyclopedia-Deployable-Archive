"""Review the next content-image frontier against older evidence and literal pages."""
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
AUDIT = RUN / 'local-audit/next-frontier-v29/next-frontier-v29-candidates.json'
OUT = RUN / 'publication/next-frontier-selected70.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
MARKER = re.compile(r'missing-image\.svg\?([^\"\'<>\s\)]*)', re.I)


def main():
    assert not OUT.exists()
    assert sha(AUDIT) == '8ff61652fef26af64da9cf321f8ca6ebb4ae3f85813df4ce7a76a8cd399e0622'
    audit = read(AUDIT)
    site = ROOT / '.scratch/pages-resources-20261018-v29'
    provenance = site / 'export-provenance.json'
    assert sha(provenance) == '793e99ef3c55ef5d328f8f6773c15b86ca69a79e7504d1333a9c04364dca28f8'
    records = {item['output_path']: item for item in read(provenance)['files']}
    excluded, rows, completed_secondary_hashes = [], [], []
    for item in audit['candidates']:
        rank, url = item['priority_rank'], item['requested_url']
        reason = None
        if rank in {1, 2, 3}:
            reason = 'Older encyclopedia image checks already cover the requested interval: docs/gap-review-20261011.md, article-image rows. Recent JSON-only evidence inventory did not cover this older material.'
        elif rank == 15:
            reason = 'Lordaeron map exact CDX was complete and empty for 2004 through the anchor in network-assets5. Do not re-request that complete interval; any earlier gap would require a separate plan.'
        elif rank in {16, 17, 78}:
            reason = 'Sponsor/forum logo deferred until content images are checked.'
        elif rank in {38, 39, 41}:
            reason = 'Literal path contains spaces; retain for a separately reviewed URI-serialization probe.'
        if reason:
            excluded.append({'original_priority_rank': rank, 'original': url, 'reason': reason})
            continue
        assert not item['has_query_or_fragment'] and item['visual_role'] == 'content_visual_candidate'
        for ref in item['references']:
            path = (ROOT / ref['output_file']).resolve()
            relative = path.relative_to(site.resolve()).as_posix()
            actual_sha = sha(path)
            assert actual_sha == records[relative]['derived_sha256']
            if ref.get('source_page_sha256'):
                assert actual_sha == ref['source_page_sha256']
            else:
                completed_secondary_hashes.append({'path': ref['output_file'], 'sha256': actual_sha, 'basis': 'Frozen v29 provenance and actual file agree; secondary-reference hash omitted by the candidate audit.'})
                ref['source_page_sha256'] = actual_sha
            line = path.read_text(encoding='utf-8').splitlines()[ref['line'] - 1]
            literals = [parse_qs(html.unescape(m.group(1))).get('requested', [''])[0] for m in MARKER.finditer(line)]
            assert url in literals
        rows.append(dict(item, rank=len(rows) + 1, original=url))
    assert len(rows) == 70 and len(excluded) == 10
    assert len({x['requested_url'] for x in rows}) == 70
    assert not {x['requested_url'] for x in rows} & {x['requested_url'] for x in read(RUN / 'publication/static-frontier-selected38.json')['rows']}
    assert not {x['requested_url'] for x in rows} & {x['original'] for x in read(RUN / 'publication/news-remaining-v28-queue.json')['rows']}
    evidence = [AUDIT, provenance, ROOT / 'docs/gap-review-20261011.md', ROOT / 'research/continuous-recovery-20261015/network-assets5/plan.json', ROOT / 'research/continuous-recovery-20261015/network-assets5/batch-report.json']
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
              'scope': 'Seventy actual v29 content-image references; older completed encyclopedia/map checks excluded, logo and space-containing URI probes deferred. The parent eighty-row audit remains unchanged.',
              'bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in evidence],
              'rows': rows, 'excluded_or_deferred': excluded, 'completed_secondary_reference_hashes': completed_secondary_hashes}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': True, 'targets': 70, 'references': sum(len(x['references']) for x in rows), 'sha256': sha(OUT)}))


if __name__ == '__main__':
    main()

"""Select literal remaining news images outside prior reviewed plan inputs."""
import hashlib
import html
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261018-v28'
AUDIT = ROOT / 'research/continuous-recovery-20261016/local-audit/all-news/all-news-audit.json'
MARKER = re.compile(r'missing-image\.svg\?([^\"\'<>\s\)]*)', re.I)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(url):
    parsed = urlsplit(url)
    return ((parsed.hostname or '').lower(), parsed.path, parsed.query)


def original_values(value):
    if isinstance(value, dict):
        for name, child in value.items():
            if name in {'original', 'logical_url', 'exact_original'} and isinstance(child, str) and child.startswith(('http://', 'https://')):
                yield child
            elif isinstance(child, (dict, list)):
                yield from original_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from original_values(child)


def main():
    target = OUT / 'news-remaining-v28-queue.json'
    assert not target.exists()
    excluded = set()
    bindings = []
    old_queue_path = OUT / 'news-unplanned-v26-queue.json'
    assert sha(old_queue_path) == 'b10c3bfdf9dc9bc1aac8321c266fae6fb388ddd72851e996359e4a9db79c70d6'
    old_queue = json.loads(old_queue_path.read_bytes())
    for binding in old_queue['bindings']:
        path = ROOT / binding['path']
        assert sha(path) == binding['sha256']
        if path.name == 'plan.json':
            excluded.update(key(url) for url in original_values(json.loads(path.read_bytes())))
            bindings.append(binding)
    excluded.update(key(row['original']) for row in old_queue['rows'])
    bindings.append({'path': old_queue_path.relative_to(ROOT).as_posix(), 'sha256': sha(old_queue_path)})
    audit = json.loads(AUDIT.read_bytes())
    prior = {key(row['canonical_key']): row for row in audit['queue'] if row['status'] == 'uncovered_local_evidence'}
    refs = defaultdict(list)
    for path in sorted((SITE / 'news').rglob('*')):
        if not path.is_file() or path.suffix not in {'.html', '.xml', '.htm'}:
            continue
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            for match in MARKER.finditer(line):
                query = parse_qs(html.unescape(match.group(1)))
                url = query.get('requested', [''])[0]
                parsed = urlsplit(url)
                if parsed.hostname != 'www.worldofwarcraft.com' or not re.match(r'^/news/images/(?:08|07)-\d\d/', parsed.path) or Path(parsed.path).suffix.lower() not in {'.jpg', '.jpeg', '.gif', '.png'}:
                    continue
                identity = key(url)
                if identity in excluded or identity not in prior:
                    continue
                refs[identity].append({'source': path.relative_to(ROOT).as_posix() + ':' + str(number),
                                       'page': path.relative_to(SITE).as_posix(), 'line': number,
                                       'requested': url, 'reason': query.get('reason', [''])[0]})
    # Finish the anchor-year body art, then the explicitly requested August 2007 news.
    def rank(identity):
        path = identity[1]
        band = 0 if '/08-' in path else 1 if '/07-08/' in path else 2
        return band, -len(refs[identity]), path
    rows = []
    for n, identity in enumerate(sorted(refs, key=rank), 1):
        evidence = refs[identity]
        url = evidence[0]['requested']
        assert identity == key(prior[identity]['canonical_key'])
        rows.append({'rank': n, 'original': url, 'normalized_original': url,
                     'type': 'static_news_body', 'dynamic_gallery': False,
                     'priority_band': ['2008-news-body', '2007-08-news-body', 'other-2007-news-body'][rank(identity)[0]],
                     'occurrences_v28_news': len(evidence), 'v28_marker_refs': evidence,
                     'prior_attempts': {'state': 'not_in_reviewed_plan_inputs', 'all_news_audit_status': 'uncovered_local_evidence'},
                     'cdx_state': 'no_new_cdx_query_yet'})
    assert len(rows) == 49, len(rows)
    for row in rows:
        for ref in row['v28_marker_refs']:
            page = SITE / ref['page']
            ref['source_page_sha256'] = sha(page)
    result = {'accepted': True, 'generated_utc': datetime.now(timezone.utc).isoformat(),
              'network_requests': 0, 'scope': 'Forty-nine literal v28 news markers remaining after the accepted original eighty-target queue. Reuse the original reviewed exclusions; source-page SHA and line retained. No new request yet.',
              'selection': {'target_count': len(rows), 'remaining_eligible_count': len(refs), 'excluded_identity_count': len(excluded)},
              'bindings': bindings + [{'path': AUDIT.relative_to(ROOT).as_posix(), 'sha256': sha(AUDIT)},
                                       {'path': (SITE / 'export-provenance.json').relative_to(ROOT).as_posix(), 'sha256': sha(SITE / 'export-provenance.json')}],
              'rows': rows}
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': True, 'rows': len(rows), 'remaining_eligible': len(refs), 'plan_inputs': len(bindings), 'sha256': sha(target), 'priority_counts': {band: sum(x['priority_band'] == band for x in rows) for band in ['2008-news-body', '2007-08-news-body', 'other-2007-news-body']}}))


if __name__ == '__main__':
    main()

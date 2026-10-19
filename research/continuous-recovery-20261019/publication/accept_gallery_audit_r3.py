"""Check local coverage evidence and resolve the six relative HTML aliases."""
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
BASE = ROOT / 'research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/full-source15-crossrefs-r3'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend((tag, key, value) for key, value in attrs if key in ('src', 'href') and value)


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': SHA(path), 'bytes': path.stat().st_size}


def main():
    out = PUB / 'root-gallery-audit-r3-acceptance.json'
    queue_out = PUB / 'next-media-aliases-source-corrected.json'
    assert not out.exists() and not queue_out.exists()
    receipt = READ(BASE / 'r3-audit-receipt.json')
    aliases = READ(BASE / 'alias-priority-queue-v37-r3.json')
    ledger = READ(BASE / 'coverage-ledger-r3-addendum.json')
    assert aliases['network_performed'] is False and len(aliases['all_exact_concrete_aliases']) == 417
    checked = 0
    statuses = Counter()
    for row in aliases['all_exact_concrete_aliases']:
        data = row['v37_cross_reference_r3']
        statuses[data['status']] += 1
        if data['status'] == 'v37_no_provenance_route':
            continue
        identity = data['identity']
        assert identity['candidate_host'] == 'www.worldofwarcraft.com' and identity['host_match'] and identity['content_match']
        path = (ROOT / identity['actual_path']).resolve()
        path.relative_to(ROOT / '.scratch/pages-resources-20261019-v37')
        assert SHA(path) == identity['expected_sha256'] == identity['actual_sha256']
        assert path.stat().st_size == identity['expected_bytes'] == identity['actual_bytes']
        checked += 1
    assert checked == 411
    assert len(ledger['rows']) == 50
    for row in ledger['rows']:
        assert row['source_links']
        if row['decision'] == 'park':
            assert row['prior_late_status'] == 'complete' and row['uncovered_late_segments'] == []
        else:
            assert row['decision'] == 'open' and row['uncovered_late_segments']
    corrected = []
    for row in aliases['priority_queue']:
        assert row['v37_cross_reference_r3']['status'] == 'v37_no_provenance_route'
        source = row['source']
        source_path = ROOT / source['output_path']
        assert SHA(source_path) == source['sha256']
        raw_line = source_path.read_text('utf-8').splitlines()[source['line']-1]
        assert raw_line == row['references'][0]['raw_line']
        parser = Links()
        parser.feed(raw_line)
        urls = [value for tag, key, value in parser.urls if tag == 'img' and key == 'src' and re.search(r'ss0*'+str(row['shot_number'])+r'\.jpg$', value)]
        assert len(urls) == 1
        actual = urljoin(source['source_base_url'], urls[0])
        assert actual.startswith('http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/')
        corrected.append({'original': actual, 'literal': urls[0], 'source': source,
            'corrects_partial_token_url': row['resolved_url'],
            'status': 'unrecovered_source_reference; no request authorized or performed',
            'dedupe_status': 'Complete-prefix ledger checked; full historical exact-request dedupe remains required before any future download.'})
    assert len(corrected) == 6
    queue = {'network_requests': 0, 'generated_utc': datetime.now(timezone.utc).isoformat(),
        'candidates': corrected,
        'scope': 'The regex scanner began tokens at an internal slash in six relative img src values and dropped images/. HTML attribute parsing resolves the actual relative literals against the source news-page URL. These corrected references are candidate evidence only; no capture availability claim or network plan.'}
    queue_out.write_text(json.dumps(queue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
        'local_url_variants_checked': checked, 'status_counts': dict(statuses),
        'corrected_candidate_urls': len(corrected), 'gallery_late_windows_complete': 21, 'gallery_late_windows_open': 29,
        'qualification': 'Park21 means do not repeat the same completed prefix/time-window queries; it does not establish final image absence for21 galleries. Only Karazhan and Black Temple retain the separately accepted broader park-pending-new-evidence decisions. Six regex-derived aliases are superseded by exact HTML attribute resolution. No new images accepted by this audit.',
        'bindings': [bind(BASE / n) for n in ('r3-audit-receipt.json', 'crossref-r3-report.json', 'coverage-ledger-r3-addendum.json', 'alias-priority-queue-v37-r3.json', '_build_r3.py')] + [bind(queue_out)]}
    out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

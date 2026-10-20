"""Root check of active image references and source-defined gallery prefixes."""
import hashlib
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261020'
OUT = RUN / 'publication/root-prepared-queue-acceptance.json'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


class Images(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base, self.urls = base, set()

    def handle_starttag(self, tag, attrs):
        if tag != 'img':
            return
        for attr, raw in attrs:
            if attr == 'src' and raw:
                query = parse_qs(urlsplit(raw).query)
                self.urls.add(query.get('requested', [urljoin(self.base, raw)])[0])


def main():
    assert not OUT.exists()
    queue_path = RUN / 'local-audit/recovery-queue.json'
    tail_path = RUN / 'local-audit/news-extension-141-160.json'
    assert SHA(queue_path) == 'a4f7a8fed2de23fa65864a5d949f9af112694074f87318706c6b8e3ce484f03e'
    assert SHA(tail_path) == '6b8d5776e13a990d395949fbfa057032bca5e6a64d1920c12079fcad7d93ce84'
    queue, tail = READ(queue_path), READ(tail_path)
    assert not queue['network_performed'] and not tail['network_performed']
    seen = {}
    for row in queue['source_inputs'] + tail['source_inputs']:
        path = ROOT / row['path']
        if row['path'] not in seen:
            assert SHA(path) == row['sha256'] and path.stat().st_size == row['bytes'], row['path']
            seen[row['path']] = row['sha256']
    news = queue['b_news_extension_priority']['items'] + tail['items']
    assert [row['candidate_rank'] for row in news] == list(range(121, 161))
    parsed = {}
    for row in news:
        original = row['requested_url']
        evidence = row['source_reference']
        for relative, base in [(row['v38_local']['path'], evidence['v33_marker']['source_url'])] + [
                (context['source_file'], context['source_url']) for context in evidence['source15_context']]:
            if relative not in parsed:
                parser = Images(base)
                parser.feed((ROOT / relative).read_text(encoding='utf-8'))
                parsed[relative] = parser.urls
            assert original in parsed[relative], (original, relative)
        assert not (ROOT / row['v38_local']['direct_asset_path']).exists()
        assert not row['actual_exact_cdx_or_replay_evidence']
    galleries = queue['c_gallery_late_priority']['items']
    assert len(galleries) == 10
    for row in galleries:
        source = row['source_reference']
        path = ROOT / source['path']
        assert SHA(path) == source['sha256']
        text = path.read_text(encoding='utf-8')
        assert source['addshots_literal'] in text and source['numshots_literal'] in text
        directory = re.search(r'addshots\s*\(\s*"([^"]+)"', source['addshots_literal']).group(1)
        assert row['prefix_url'] == 'http://www.worldofwarcraft.com' + directory
        query = parse_qs(urlsplit(row['query_url']).query)
        assert query['url'] == [row['prefix_url']] and query['matchType'] == ['prefix']
        assert query['from'] == ['20080512210045'] and query['to'] == ['20101207235959']
        assert row['prior_late_status'] in ('source_503', 'not_queried')
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
               'queue_sha256': SHA(queue_path), 'tail_sha256': SHA(tail_path), 'input_files_checked': len(seen),
               'active_img_targets_checked': len(news), 'news_ranks': [121, 160],
               'gallery_source_prefixes_checked': len(galleries), 'gallery_registry_ranks': [row['registry_rank'] for row in galleries],
               'scope': 'Verified bound inputs, real active img/src references in Source15 and v38, direct asset absence, and exact gallery addshots prefixes/window. Historical no-execution assertions retain the bounded search scope in the worker report. Not archive availability or request authorization.'}
    OUT.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()

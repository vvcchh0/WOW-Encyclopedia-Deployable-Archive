"""Resolve only literal popup destinations on the arena and Silvermoon articles."""
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
SITE = ROOT / '.scratch/pages-resources-20261018-v30'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
CALL = re.compile(r'\bpopUpOmega\s*\(\s*([\'\"])([^\'\"<>]+?\.(?:jpe?g|gif|png))\1', re.I)


def main():
    output, urls = PUB / 'popup24-selected-queue.json', PUB / 'popup24-original-urls.txt'
    assert not output.exists() and not urls.exists()
    provenance_path = SITE / 'export-provenance.json'
    assert sha(provenance_path) == 'b04eb866bd7d21aa23ce8ad064eeb55b8b263e84147bb3755f4af7df84825d85'
    manifest_path = ROOT / '.scratch/offline-navigation-20261015-v15/build-manifest.json'
    assert sha(manifest_path) == 'd89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002'
    records = {x['route']: x for x in read(provenance_path)['files']}
    sources = {x['route']: x for x in read(manifest_path)['files']}
    paths = {x['output_path'] for x in records.values()}
    rows = []
    for route in ['/insider/11/arena.xml', '/insider/10/silvermoon.xml']:
        record = records[route]
        page = SITE / record['output_path']
        assert sha(page) == record['derived_sha256']
        source_url = sources[route]['source_base_url']
        for number, line in enumerate(page.read_text(encoding='utf-8').splitlines(), 1):
            for match in CALL.finditer(html.unescape(line)):
                literal = match.group(2)
                assert not re.search(r'[\s\\]', literal) and not literal.startswith('/WOW-Encyclopedia-Deployable-Archive/')
                original = urljoin(source_url, literal)
                parsed = urlsplit(original)
                assert parsed.hostname == 'www.worldofwarcraft.com' and not parsed.query and not parsed.fragment
                assert parsed.path.lstrip('/') not in paths, 'Already exported image must not be requested again'
                rows.append({'rank': len(rows) + 1, 'original': original,
                    'source_base_url': source_url, 'literal_popup_argument': literal,
                    'references': [{'output_file': page.relative_to(ROOT).as_posix(), 'line': number,
                        'source_page_sha256': sha(page), 'source_page': source_url,
                        'literal': literal, 'popup_helper': 'popUpOmega'}]})
    assert len(rows) == len({x['original'] for x in rows}) == 24
    urls.write_text(''.join(x['original'] + '\n' for x in rows), encoding='utf-8')
    for row in rows:
        row['resolved_url_list_line'] = row['rank']
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'network_requests': 0, 'target_count': 24, 'rows': rows,
        'source_bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in [provenance_path, manifest_path, urls]],
        'scope': '24 actual popUpOmega image arguments: 11 arena and 13 Silvermoon article destinations. Resolve literal relative paths against their frozen source_base_url; do not infer full-image names from thumbnails. URL-list lines are derived citations, not downloaded payloads or archive availability evidence.'}
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'targets': len(rows), 'queue_sha256': sha(output), 'url_list_sha256': sha(urls)}))


if __name__ == '__main__':
    main()

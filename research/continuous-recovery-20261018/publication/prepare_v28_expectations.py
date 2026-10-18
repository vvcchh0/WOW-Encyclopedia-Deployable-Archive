"""Derive v28 expected changes from actual frozen v27 markers and root receipts."""
import hashlib
import html
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261018'
SITE = ROOT / '.scratch/pages-resources-20261018-v27'
OUT = BASE / 'publication/v28-export-expectations.json'
sys.path.insert(0, str(ROOT / 'research/continuous-recovery-20261016/publication'))
from accept_static_resource_inventory import normalize

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
MARKER = re.compile(r'missing-image\.svg\?([^\"\'<>\s\)]*)', re.I)


def main():
    assert not OUT.exists()
    assert sha(SITE / 'export-provenance.json') == '271e474b80ce936c3a68b567a7c3e42c86851eb371772fa8108498613aa1f012'
    entries, bindings = [], []
    for number in range(1, 5):
        path = BASE / f'publication/root-news-unplanned-batch{number}-public-copy-acceptance.json'
        receipt = read(path)
        assert receipt['accepted'] and receipt['copy_mode'] == 'original_bytes'
        entries.extend(receipt['accepted_images'])
        bindings.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})
    assert len(entries) == 40
    by_route = {}
    for item in entries:
        parsed = urlsplit(item['original'])
        assert parsed.hostname == 'www.worldofwarcraft.com'
        route = parsed.path.lstrip('/')
        assert route not in by_route
        by_route[route] = item
    old_paths = {item['output_path'] for item in read(SITE / 'export-provenance.json')['files']}
    assert not set(by_route) & old_paths
    counters = [Counter(), Counter()]
    removed = [Counter(), Counter()]
    refs = []
    files = 0
    allowed = {'__offline/route-map.json', '__offline/pages_runtime.js', '__offline/related-images/index.html',
               'news/rss-02-2007.xml.html'}
    for path in SITE.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in {'.html', '.htm', '.xml', '.css'}:
            continue
        relative = path.relative_to(SITE).as_posix()
        if relative.startswith('_origins/'):
            continue
        files += 1
        text = path.read_text(encoding='utf-8', errors='replace')
        if any(item['original'] in text or quote(item['original'], safe='') in text for item in entries):
            allowed.add(relative)
        for number, line in enumerate(text.splitlines(), 1):
            for match in MARKER.finditer(line):
                query = parse_qs(html.unescape(match.group(1)), keep_blank_values=True)
                requested = query.get('requested', [''])[0]
                parsed = urlsplit(requested)
                if parsed.scheme not in {'http', 'https'} or Path(parsed.path.lower()).suffix not in {'.gif', '.jpg', '.jpeg', '.png', '.webp', '.svg', '.bmp'}:
                    continue
                key = normalize(requested)
                counters[0][key] += 1
                if relative.startswith('news/'):
                    counters[1][key] += 1
                target = parsed.path.lstrip('/') if parsed.hostname in {'www.worldofwarcraft.com', 'worldofwarcraft.com'} else None
                if target not in by_route:
                    continue
                removed[0][key] += 1
                if relative.startswith('news/'):
                    removed[1][key] += 1
                allowed.add(relative)
                refs.append({'original': by_route[target]['original'], 'requested': requested,
                             'output_path': target, 'page': relative, 'line': number})
    assert files == 1104 and (len(counters[0]), sum(counters[0].values())) == (1146, 1901)
    assert (len(counters[1]), sum(counters[1].values())) == (516, 516)
    remaining = [counter - delete for counter, delete in zip(counters, removed)]
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Actual frozen v27 static marker references. Also permit the independently accepted historical-news exhibit transformation on its exact target page. Native dynamic galleries remain separate.',
              'source_bindings': bindings,
              'new_output_paths': sorted(by_route), 'allowed_changed_output_paths': sorted(allowed),
              'stats': {'source_records': 8357, 'image_overlay_records': 263, 'primary_image_overlay_records': 188, 'supplement_image_overlay_records': 75, 'output_files': 8721},
              'guide_collection_images': 39, 'new_static_marker_references': refs,
              'new_news_marker_references': dict(Counter(item['original'] for item in refs if item['page'].startswith('news/'))),
              'expected_static_counts': {'static_text_files': files, 'unique_missing_images': len(remaining[0]), 'missing_occurrences': sum(remaining[0].values()), 'news_unique_missing_images': len(remaining[1]), 'news_missing_occurrences': sum(remaining[1].values())},
              'removed_static_unique_addresses': len(removed[0]), 'removed_static_occurrences': sum(removed[0].values()),
              'assets_without_current_static_marker': sorted(set(item['original'] for item in entries) - set(item['original'] for item in refs)),
              'network_requests': 0, 'export_executed': False}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ['expected_static_counts', 'removed_static_unique_addresses', 'removed_static_occurrences', 'assets_without_current_static_marker', 'allowed_changed_output_paths']}))


if __name__ == '__main__':
    main()

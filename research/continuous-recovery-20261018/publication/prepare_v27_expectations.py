"""Derive v27 expectations from actual v26 page markers, not manifest projection."""
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
SITE = ROOT / '.scratch/pages-resources-20261018-v26'
OUT = BASE / 'publication/v27-export-expectations.json'
sys.path.insert(0, str(ROOT / 'research/continuous-recovery-20261016/publication'))
from accept_static_resource_inventory import normalize

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
MARKER = re.compile(r'missing-image\.svg\?([^\"\'<>\s\)]*)', re.I)


def route(url):
    parsed = urlsplit(url)
    host = (parsed.hostname or '').lower()
    if host in {'www.worldofwarcraft.com', 'worldofwarcraft.com'}:
        return parsed.path.lstrip('/')
    if host == 'www.blizzard.com':
        return '_origins/' + host + parsed.path
    return None


def main():
    assert not OUT.exists()
    assert sha(SITE / 'export-provenance.json') == 'f5580948c5df72a744577e15bf9165ee7ec477c5adf4b458e5db0241acd9c332'
    entries = []
    for name in ['v27-primary-source-map.json', 'v27-blizzard-supplement-source-map.json']:
        entries.extend(read(BASE / 'integration/v27' / name)['items'])
    assert len(entries) == 27
    by_route = {route(item['original']): item for item in entries}
    assert len(by_route) == 27
    provenance = read(SITE / 'export-provenance.json')
    old_paths = {item['output_path'] for item in provenance['files']}
    assert not set(by_route) & old_paths
    counters = [Counter(), Counter()]
    removed = [Counter(), Counter()]
    refs = []
    files = 0
    allowed = {'__offline/route-map.json', '__offline/pages_runtime.js', '__offline/related-images/index.html'}
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
                target = route(requested)
                if target not in by_route:
                    continue
                removed[0][key] += 1
                if relative.startswith('news/'):
                    removed[1][key] += 1
                allowed.add(relative)
                refs.append({'original': by_route[target]['original'], 'requested': requested,
                             'output_path': target, 'page': relative, 'line': number})
        if files % 250 == 0:
            print(json.dumps({'checked_text_files': files}), flush=True)
    assert files == 1104 and (len(counters[0]), sum(counters[0].values())) == (1173, 1932)
    assert (len(counters[1]), sum(counters[1].values())) == (543, 547)
    remaining = [counter - delete for counter, delete in zip(counters, removed)]
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Actual frozen v26 static marker references; source-manifest metadata alone is incomplete. This is an expected-change set before export acceptance.',
              'new_output_paths': sorted(by_route), 'allowed_changed_output_paths': sorted(allowed),
              'stats': {'source_records': 8357, 'image_overlay_records': 223, 'primary_image_overlay_records': 148, 'supplement_image_overlay_records': 75, 'output_files': 8681},
              'guide_collection_images': 39, 'new_static_marker_references': refs,
              'new_news_marker_references': dict(Counter(item['original'] for item in refs if item['page'].startswith('news/'))),
              'expected_static_counts': {'static_text_files': files, 'unique_missing_images': len(remaining[0]), 'missing_occurrences': sum(remaining[0].values()), 'news_unique_missing_images': len(remaining[1]), 'news_missing_occurrences': sum(remaining[1].values())},
              'removed_static_unique_addresses': len(removed[0]), 'removed_static_occurrences': sum(removed[0].values()),
              'assets_without_current_static_marker': sorted(set(item['original'] for item in entries) - set(item['original'] for item in refs)),
              'network_requests': 0, 'export_executed': False}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ['expected_static_counts', 'removed_static_unique_addresses', 'removed_static_occurrences', 'assets_without_current_static_marker']}), flush=True)


if __name__ == '__main__':
    main()

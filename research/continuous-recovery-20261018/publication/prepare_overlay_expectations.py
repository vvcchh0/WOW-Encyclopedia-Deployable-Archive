"""Derive a proposed overlay's expected changes from a frozen, accepted local site."""
import argparse
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
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
sys.path.insert(0, str(ROOT / 'research/continuous-recovery-20261016/publication'))
from accept_static_resource_inventory import normalize

read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
MARKER = re.compile(r'missing-image\.svg\?([^\"\'<>\s\)]*)', re.I)
PRIMARY = {'www.worldofwarcraft.com', 'worldofwarcraft.com'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--previous', required=True)
    parser.add_argument('--previous-sha256', required=True)
    parser.add_argument('--maps', required=True, nargs='+')
    parser.add_argument('--new-images', required=True, type=int)
    args = parser.parse_args()
    assert re.fullmatch(r'v\d+', args.version) and re.fullmatch(r'v\d+', args.previous)
    site = ROOT / f'.scratch/pages-resources-20261018-{args.previous}'
    output = PUB / f'{args.version}-export-expectations.json'
    provenance_path = site / 'export-provenance.json'
    assert not output.exists() and sha(provenance_path) == args.previous_sha256
    provenance = read(provenance_path)
    metrics_path = PUB / f'root-{args.previous}-static-metrics-acceptance.json'
    metrics = read(metrics_path)
    assert metrics['accepted'] and metrics['export_provenance_sha256'] == args.previous_sha256
    bindings = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in [provenance_path, metrics_path]]
    entries = []
    for text in args.maps:
        path = (ROOT / text).resolve()
        path.relative_to((RUN / 'integration').resolve())
        entries.extend(read(path)['items'])
        bindings.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})
    assert len(entries) == args.new_images
    targets = {}
    for entry in entries:
        original = entry['original']
        parsed = urlsplit(original)
        assert not parsed.query and not parsed.fragment
        path = parsed.path.lstrip('/') if parsed.hostname in PRIMARY else '_origins/' + parsed.hostname + parsed.path
        key = normalize(original)
        assert key not in targets
        targets[key] = {'original': original, 'output_path': path}
    new_paths = {entry['output_path'] for entry in targets.values()}
    assert len(new_paths) == len(entries)
    assert not new_paths & {entry['output_path'] for entry in provenance['files']}
    counts, removed = [Counter(), Counter()], [Counter(), Counter()]
    references, files = [], 0
    allowed = {'__offline/route-map.json', '__offline/pages_runtime.js', '__offline/related-images/index.html'}
    for path in site.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in {'.html', '.htm', '.xml', '.css'}:
            continue
        relative = path.relative_to(site).as_posix()
        if relative.startswith('_origins/'):
            continue
        files += 1
        text = path.read_text(encoding='utf-8', errors='replace')
        if any(entry['original'] in text or quote(entry['original'], safe='') in text for entry in entries):
            allowed.add(relative)
        for line_no, line in enumerate(text.splitlines(), 1):
            for marker in MARKER.finditer(line):
                query = parse_qs(html.unescape(marker.group(1)), keep_blank_values=True)
                original = query.get('requested', [''])[0]
                parsed = urlsplit(original)
                if parsed.scheme not in {'http', 'https'} or Path(parsed.path.lower()).suffix not in {'.gif', '.jpg', '.jpeg', '.png', '.webp', '.svg', '.bmp'}:
                    continue
                key = normalize(original)
                counts[0][key] += 1
                if relative.startswith('news/'):
                    counts[1][key] += 1
                if key in targets:
                    removed[0][key] += 1
                    if relative.startswith('news/'):
                        removed[1][key] += 1
                    allowed.add(relative)
                    references.append(dict(targets[key], requested=original, page=relative, line=line_no))
    assert (files, len(counts[0]), sum(counts[0].values()), len(counts[1]), sum(counts[1].values())) == (metrics['static_text_files'], metrics['unique_missing_images'], metrics['missing_occurrences'], metrics['news_unique_missing_images'], metrics['news_missing_occurrences'])
    after = [before - delete for before, delete in zip(counts, removed)]
    stats = dict(provenance['stats'])
    additions = sum(urlsplit(entry['original']).hostname in PRIMARY for entry in entries)
    expected_stats = {'source_records': stats['source_records'], 'output_files': stats['output_files'] + len(entries),
                      'image_overlay_records': stats['image_overlay_records'] + len(entries),
                      'primary_image_overlay_records': stats['primary_image_overlay_records'] + additions,
                      'supplement_image_overlay_records': stats['supplement_image_overlay_records'] + len(entries) - additions}
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Actual frozen static references; native JavaScript gallery targets remain separate.',
              'source_bindings': bindings, 'new_output_paths': sorted(new_paths), 'allowed_changed_output_paths': sorted(allowed),
              'stats': expected_stats, 'guide_collection_images': provenance['guide_image_collections']['image_count'],
              'new_static_marker_references': references,
              'new_news_marker_references': dict(Counter(x['original'] for x in references if x['page'].startswith('news/'))),
              'expected_static_counts': {'static_text_files': files, 'unique_missing_images': len(after[0]), 'missing_occurrences': sum(after[0].values()), 'news_unique_missing_images': len(after[1]), 'news_missing_occurrences': sum(after[1].values())},
              'removed_static_unique_addresses': len(removed[0]), 'removed_static_occurrences': sum(removed[0].values()),
              'assets_without_current_static_marker': sorted({x['original'] for x in entries} - {x['original'] for x in references}),
              'network_requests': 0, 'export_executed': False}
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['stats', 'expected_static_counts', 'removed_static_unique_addresses', 'removed_static_occurrences', 'assets_without_current_static_marker', 'allowed_changed_output_paths']}))


if __name__ == '__main__':
    main()

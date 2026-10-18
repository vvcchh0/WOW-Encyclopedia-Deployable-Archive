"""Inventory literal image destinations in existing unresolved navigation links."""
import hashlib
import html
import importlib.util
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
SITE = ROOT / '.scratch/pages-resources-20261018-v30'
OUT = RUN / 'publication/image-navigation-audit-v30.json'
MARKER = re.compile(r'missing\.html\?([^\"\'<>\s\)]*)', re.I)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def main():
    assert not OUT.exists()
    provenance_path = SITE / 'export-provenance.json'
    assert sha(provenance_path) == 'b04eb866bd7d21aa23ce8ad064eeb55b8b263e84147bb3755f4af7df84825d85'
    helper_path = RUN / 'local-audit/next-frontier-v29/audit_next_frontier_v29.py'
    spec = importlib.util.spec_from_file_location('recent_image_evidence_index', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    normalize = helper.normalize
    evidence, indexed_files = helper.collect_json_evidence()
    provenance = read(provenance_path)
    already = set()
    for item in provenance['files']:
        if not item.get('mime', '').startswith('image/'):
            continue
        if item.get('original_url'):
            already.add(normalize(item['original_url']))
        route = item['route']
        if route.startswith('/_origins/'):
            already.add(normalize('http://' + route[len('/_origins/'):]))
        else:
            already.add(normalize('http://www.worldofwarcraft.com' + route))
    pending = {normalize(x['original']) for x in read(RUN / 'publication/next-frontier-selected70.json')['rows']}
    for path in (RUN / 'publication').glob('root-*-public-copy-acceptance.json'):
        for item in read(path).get('accepted_images', []):
            already.add(normalize(item['original']))
    rows = {}
    files = 0
    for record in provenance['files']:
        relative = record['output_path']
        if relative.startswith('_origins/') or not relative.endswith(('.html', '.htm', '.xml', '.css')):
            continue
        path = SITE / relative
        text = path.read_text(encoding='utf-8')
        files += 1
        for number, line in enumerate(text.splitlines(), 1):
            for match in MARKER.finditer(line):
                query = parse_qs(html.unescape(match.group(1)), keep_blank_values=True)
                original = query.get('requested', [''])[0]
                parsed = urlsplit(original)
                if parsed.scheme not in {'http', 'https'} or Path(parsed.path).suffix.lower() not in {'.jpg', '.jpeg', '.gif', '.png', '.webp'}:
                    continue
                key = normalize(original)
                row = rows.setdefault(key, {'original': original, 'normalized_identity': key, 'references': [],
                    'already_exported_or_accepted': key in already, 'in_next70_queue': key in pending})
                row['references'].append({'output_file': path.relative_to(ROOT).as_posix(), 'line': number,
                    'source_page_sha256': record['derived_sha256'], 'source_page': query.get('source', [''])[0],
                    'reason': query.get('reason', [''])[0], 'page': relative})
    candidates, unresolved_existing, deferred = [], [], []
    for key, row in rows.items():
        relevant = evidence.get(key, [])
        execution = [x for x in relevant if x['kind'] == 'execution_or_receipt']
        row['recent_evidence'] = relevant
        row['recent_execution_record_count'] = len(execution)
        original = row['original']
        parsed = urlsplit(original)
        if row['already_exported_or_accepted']:
            unresolved_existing.append(row)
            continue
        if row['in_next70_queue'] or execution or parsed.hostname not in {'www.worldofwarcraft.com', 'worldofwarcraft.com', 'www.blizzard.com'} or parsed.query or parsed.fragment or re.search(r'\s', original) or '/info/encyclopedia/' in parsed.path:
            deferred.append(row)
            continue
        pages = ' '.join(x['page'] for x in row['references'])
        row['priority'] = sum(weight for token, weight in [('insider/', 40), ('info/dungeons/', 30), ('burningcrusade/', 25), ('media/', 20), ('screenshots/', 18)] if token in pages)
        candidates.append(row)
    candidates.sort(key=lambda x: (-x['priority'], x['references'][0]['page'], x['original']))
    for rank, row in enumerate(candidates, 1):
        row['rank'] = rank
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
              'source_provenance': {'path': provenance_path.relative_to(ROOT).as_posix(), 'sha256': sha(provenance_path)},
              'evidence_index_helper': {'path': helper_path.relative_to(ROOT).as_posix(), 'sha256': sha(helper_path)},
              'scope': 'Literal requested image URLs from unresolved missing.html navigation links. No full-size filenames inferred. Recent execution index covers the three continuous recovery directories only; older records are not fully indexed. A found record is context, not proof that its URL was requested.',
              'static_text_files': files, 'recent_json_files_indexed': indexed_files,
              'unique_image_navigation_targets': len(rows), 'candidate_count': len(candidates),
              'already_exported_or_accepted_unresolved_links': unresolved_existing, 'deferred': deferred,
              'candidates': candidates, 'first80_by_source': dict(Counter(x['references'][0]['page'] for x in candidates[:80]))}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['static_text_files', 'recent_json_files_indexed', 'unique_image_navigation_targets', 'candidate_count', 'first80_by_source']}))
    print(json.dumps({'already_exported_or_accepted_unresolved_links': len(unresolved_existing), 'deferred': len(deferred), 'sha256': sha(OUT)}))


if __name__ == '__main__':
    main()

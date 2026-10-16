"""Independently bind the first news resource queue to missing local references."""
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
QUEUE = ROOT / 'research/continuous-recovery-20261016/local-audit/all-news/compact-first20.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    queue = json.loads(QUEUE.read_bytes())
    source = json.loads((ROOT / '.scratch/offline-navigation-20261015-v15/build-manifest.json').read_bytes())
    export = json.loads((ROOT / '.scratch/pages-resources-20261016-v16/export-provenance.json').read_bytes())
    for binding in queue['input_hashes']:
        assert sha(ROOT / binding['path']) == binding['sha256'], binding['path']
    source_routes = {x['route'] for x in source['files']}
    export_routes = {x['route'] for x in export['files']}
    checked = []
    for item in queue['items']:
        original = item['raw_url']
        parts = urlsplit(original)
        assert parts.scheme == 'http' and parts.netloc == 'www.worldofwarcraft.com' and not parts.query and not parts.fragment
        assert parts.path not in source_routes and parts.path not in export_routes
        assert not (ROOT / '.scratch/pages-resources-20261016-v16' / parts.path.lstrip('/')).exists()
        assert not item['v15_exact_source_base_matches'] and not item['v16_exact_original_or_logical_matches']
        assert not item['v15_actual_files'] and not item['v16_actual_files']
        evidence = item['evidence_locations'][0]
        assert evidence['layer'] == 'v16_output'
        lines = (ROOT / evidence['source_path']).read_text(encoding='utf-8').splitlines()
        line = html.unescape(lines[evidence['line']-1])
        assert 'missing-image.svg?' in line
        marker_queries = re.findall(r'missing-image\.svg\?([^\s\"\'<>]+)', line)
        assert any(original in parse_qs(query).get('requested', []) for query in marker_queries), original
        checked.append({'original':original,'v16_marker_count':item['v16_marker_count'],
            'evidence':evidence['source_path'] + ':' + str(evidence['line']), 'existing_payload':False})
    assert len(checked) == 20 and len({x['original'] for x in checked}) == 20
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,
        'scope':'20 exact missing image references, not a full-site resource completeness claim',
        'queue_sha256':sha(QUEUE),'items':checked,'source_manifest_sha256':sha(ROOT / '.scratch/offline-navigation-20261015-v15/build-manifest.json'),
        'export_provenance_sha256':sha(ROOT / '.scratch/pages-resources-20261016-v16/export-provenance.json')}
    (OUT / 'root-allnews-first20-acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'accepted':True,'originals':len(checked),'v16_missing_occurrences':sum(x['v16_marker_count'] for x in checked)}))

if __name__ == '__main__':
    main()

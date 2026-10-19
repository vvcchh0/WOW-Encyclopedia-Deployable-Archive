"""Independently bind the offline scan and qualify literal/gallery findings."""
import hashlib
import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b'
SCAN = BASE / 'full-source15-crossrefs'
OUT = Path(__file__).with_name('root-source15-crossref-acceptance.json')
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': SHA(path), 'bytes': path.stat().st_size}


def main():
    started = time.monotonic()
    assert not OUT.exists()
    receipt = READ(SCAN / 'crossref-scan-receipt.json')
    scan = READ(SCAN / 'crossref-scan.json')
    assert SHA(SCAN / 'crossref-scan.json') == '258bb942251c2f3c055b3a6e2841241682648d0702a24c51d416978d02af9811'
    assert all(receipt['validation'].values()) and receipt['network_requests'] == scan['network_requests'] == 0
    for group in ('inputs', 'outputs'):
        for row in receipt[group].values():
            assert SHA(ROOT / row['path']) == row['sha256']
            assert (ROOT / row['path']).stat().st_size == row['bytes']
    manifest = READ(ROOT / receipt['inputs']['manifest']['path'])
    exts = {'.html', '.htm', '.xml', '.xsl', '.css', '.js', '.htc'}
    mimes = {'text/html', 'application/xhtml+xml', 'application/xml', 'text/xml', 'text/css', 'application/x-javascript', 'application/javascript', 'text/plain'}
    kinds = {'html', 'menu_html', 'js', 'css', 'xsl', 'xml', 'legacy_component', 'support'}
    selected = [r for r in manifest['files'] if Path(r.get('route', '')).suffix.lower() in exts or r.get('mime', '').split(';')[0].lower() in mimes or r.get('kind') in kinds]
    inventory = {r['output_path']: r for r in scan['text_inventory']}
    assert len(selected) == len(inventory) == 1205
    assert set(inventory) == {r['output_path'] for r in selected}
    bytes_checked = 0
    text_by_path = {}
    for row in selected:
        path = (ROOT / row['output_path']).resolve()
        path.relative_to(ROOT / '.scratch/offline-navigation-20261015-v15/site')
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == inventory[row['output_path']]['sha256'] == row['derived_sha256']
        assert len(data) == inventory[row['output_path']]['bytes'] == row['derived_length']
        text_by_path[row['output_path']] = data.decode('utf-8', errors='replace').splitlines()
        bytes_checked += len(data)
    hits = scan['known_gallery_reference_hits']
    for hit in hits:
        lines = text_by_path[hit['source_file']['output_path']]
        assert lines[hit['line']-1] == hit['raw_line']
    nested = scan['nested_preview_hits']
    assert len(nested) == 28 and all('/' in r['token'].split(r['target_source_directory'], 1)[1] for r in nested)
    literal_rows = scan['generated_rule_hits']
    assert len(literal_rows) == 65
    concrete = []
    for row in literal_rows:
        match = re.search(r'shotList\[i\+\+\]\s*=\s*"(/info/events/hallowsend/images/newscreenshots/ss(\d+)\.jpg)\$Author:', row['raw_line'])
        assert match and row['target_gallery'] == "Hallow's End"
        concrete.append({'path': match[1], 'number': int(match[2]), 'source_path': row['source_file']['output_path'], 'line': row['line']})
    ledger = READ(BASE / 'coverage-ledger.json')
    hallow = next(r for r in ledger['rows'] if r['gallery'] == "Hallow's End")
    assert hallow['declared_slots'] == 65 and {r['number'] for r in concrete} == set(range(1, 66))
    assert all(r['path'].startswith(hallow['source_evidence']['source_directory']) for r in concrete)
    assert not any(r['target_gallery'] in ('Karazhan', 'Black Temple') for r in hits)
    output = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-started,
        'network_requests': 0, 'text_files_checked': len(inventory), 'text_bytes_checked': bytes_checked,
        'known_gallery_hits': len(hits), 'nested_directory_previews': 28, 'known_hallows_end_concrete_literals': 65,
        'new_target_gallery_urls': 0, 'new_karazhan_or_black_temple_leads': 0,
        'qualified_interpretation': 'The 65 shotList entries are concrete original-image literals already covered by the Hallow\'s End65-slot registry, not calculated URL guesses. All28 preview hits are actually under nested /thumb/ or /thumbs/. A flat ssN-thumb.jpg would count as a native thumbnail; none is present in these28 rows. The scan finds no new target-gallery URL, and does not prove absence from Wayback. Unmapped literal aliases remain separate candidates requiring page-context and capture review. First root-check attempt stopped before writing acceptance because it expected only /thumbs/; six actual /thumb/ rows were inspected and the check now verifies directory depth.',
        'bindings': [binding(SCAN / n) for n in ('crossref-scan.json', 'crossref-scan.md', 'crossref-scan-receipt.json', '_scan_source15_crossrefs.py')] + [binding(BASE / 'coverage-ledger.json')],
        'known_concrete_literals': concrete}
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in output.items() if k not in ('bindings', 'known_concrete_literals')}, ensure_ascii=False))


if __name__ == '__main__':
    main()

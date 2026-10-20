"""Independently derive native image targets from frozen gallery source HTML."""
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'source-derived-targets.json'
SOURCE = ROOT / '.scratch/offline-navigation-20261015-v15/site'
CURRENT = ROOT / '.scratch/pages-resources-20261020-v39'


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.inside = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'script':
            self.inside = True

    def handle_endtag(self, tag):
        if tag.lower() == 'script':
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.parts.append(data)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert not OUT.exists(), 'preserve previous derivation'
    registry_path = ROOT / 'research/continuous-recovery-20261016/local-audit/gallery-final-v7/gallery-prefix-registry-v7.json'
    registry = json.loads(registry_path.read_bytes())
    raw_provenance = (CURRENT / 'export-provenance.json').read_bytes()
    assert sha(raw_provenance) == '02b1cd43766288f96c879ef464d7198bb09d1085008ae3e500773d594f6c7760'
    provenance = json.loads(raw_provenance)
    declared = {r['output_path'] for r in provenance['files']}
    rows = []
    for row in registry['coverage_rows']:
        route = row['source_page_route']
        source = SOURCE / route.lstrip('/')
        data = source.read_bytes()
        parser = Scripts()
        parser.feed(data.decode('utf-8', errors='replace'))
        script = '\n'.join(parser.parts)
        n_values = {int(v) for v in re.findall(r'\bnumShots\s*=\s*(\d+)\s*;', script)}
        assert n_values == {row['declared_slots']}, (route, n_values)
        n = next(iter(n_values))
        builders = re.findall(r'''\baddshots\(\s*["']([^"']+)["']\s*,\s*["']([^"']+)["']\s*,\s*numShots\s*\)''', script)
        literals = re.findall(r'''\bshotList\[\s*(\d+)\s*\]\s*=\s*["']([^"']+)["']''', script)
        origin = 'http://www.worldofwarcraft.com' + route
        if builders:
            assert len(builders) == 1 and not literals, route
            directory, filename = builders[0]
            full = [urljoin(origin, directory + filename + str(i) + '.jpg') for i in range(1, n + 1)]
            method = 'literal_addshots_arguments_and_source_JS_numbering'
        else:
            numbered = {int(i): urljoin(origin, value) for i, value in literals}
            assert len(numbered) == len(literals) == n and set(numbered) == set(range(n)), route
            full = [numbered[i] for i in range(n)]
            method = 'literal_shotList_assignments'
        assert len(set(full)) == n and all(v.endswith('.jpg') for v in full), route
        targets = []
        for slot, url in enumerate(full, 1):
            for kind, target in [('full', url), ('thumbnail', url.replace('.jpg', '-thumb.jpg'))]:
                path = urlsplit(target).path.lstrip('/')
                presence = {name: (base / path).is_file() for name, base in [('original', ROOT / 'offline/site'), ('source15', SOURCE), ('current_v39', CURRENT)]}
                targets.append({'slot': slot, 'kind': kind, 'original_url': target, 'path': path, 'file_presence': presence, 'current_provenance_path_present': path in declared})
        current_page = CURRENT / route.lstrip('/')
        assert current_page.is_file(), route
        current_text = current_page.read_text(encoding='utf-8', errors='replace')
        current_parser = Scripts()
        current_parser.feed(current_text)
        current_builders = re.findall(r'''\baddshots\(\s*["']([^"']+)["']\s*,\s*["']([^"']+)["']\s*,\s*numShots\s*\)''', '\n'.join(current_parser.parts))
        assert not any('__offline/missing' in directory for directory, _ in current_builders), route
        rows.append({'rank': row['registry_rank'], 'gallery': row['gallery'], 'category': row['category'], 'route': route, 'declared_native_slots': n, 'method': method, 'source_sha256': sha(data), 'current_page_sha256': sha(current_page.read_bytes()), 'current_addshots_arguments': current_builders, 'targets': targets})
    assert len(rows) == 50 and sum(r['declared_native_slots'] for r in rows) == 1684
    targets = [target for row in rows for target in row['targets']]
    assert len(targets) == 3368 and len({r['original_url'] for r in targets}) == 3368
    result = {'accepted_source_derivation': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'site_provenance_sha256': sha(raw_provenance), 'registry_sha256': sha(registry_path.read_bytes()), 'groups': len(rows), 'native_slots': 1684, 'native_targets': len(targets), 'present_by_layer': {layer: sum(t['file_presence'][layer] for t in targets) for layer in ['original', 'source15', 'current_v39']}, 'current_provenance_targets': sum(t['current_provenance_path_present'] for t in targets), 'target_kind_counts': dict(Counter(t['kind'] for t in targets)), 'rows': rows, 'scope': 'Native targets derived from actual source scripts; separate guide preview and collection layers are not counted here. No provider requests or ZIP scans.'}
    OUT.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}))


if __name__ == '__main__':
    main()

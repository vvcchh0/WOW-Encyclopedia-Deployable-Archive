"""Locate archive-banner injection inside raw script text in frozen v30 pages."""
import hashlib
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SITE = ROOT / '.scratch/pages-resources-20261018-v30'
OUT = Path(__file__).with_name('root-v31-runtime-impact.json')


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.script = False
        self.banner_in_script = False
        self.actual_body_tags = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.script = True
        if tag == 'body':
            self.actual_body_tags += 1

    def handle_endtag(self, tag):
        if tag == 'script':
            self.script = False

    def handle_data(self, data):
        if self.script and '__offline-pages-banner' in data:
            self.banner_in_script = True


def main():
    assert not OUT.exists()
    provenance = SITE / 'export-provenance.json'
    assert hashlib.sha256(provenance.read_bytes()).hexdigest() == 'b04eb866bd7d21aa23ce8ad064eeb55b8b263e84147bb3755f4af7df84825d85'
    rows, scanned = [], 0
    for item in json.loads(provenance.read_bytes())['files']:
        if not item['output_path'].endswith(('.html', '.htm')):
            continue
        path = SITE / item['output_path']
        text = path.read_text(encoding='utf-8')
        parser = Scan()
        parser.feed(text)
        scanned += 1
        if parser.banner_in_script:
            rows.append({'output_path': item['output_path'], 'route': item['route'],
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'actual_body_tags': parser.actual_body_tags})
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'frozen_v30_provenance_sha256': hashlib.sha256(provenance.read_bytes()).hexdigest(),
              'html_files_scanned': scanned, 'affected_pages': rows, 'network_requests': 0,
              'scope': 'HTMLParser raw-text detection of an injected archive banner inside script data. These pages are allowed to change when the real-tag injection fix is exported; browser checks still required.'}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

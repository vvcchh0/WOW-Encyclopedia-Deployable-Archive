"""Independently bind original faction lore and the narrowly derived helper."""
import hashlib
from html.parser import HTMLParser
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-aldor-scryers-lore-source-acceptance.json'
assert not OUT.exists()
sys.path.insert(0, str(ROOT / 'tools'))
import aldor_scryers_lore as module

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest_path = ROOT / '.scratch/offline-non-gallery-20261021-v16/build-manifest.json'
source_site = ROOT / '.scratch/offline-non-gallery-20261021-v16/site'
manifest = json.loads(manifest_path.read_bytes())
bundle = module.load_lore_bundle(ROOT, source_site, manifest_path, manifest)
assert sha(manifest_path) == 'e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
assert bundle.generated_file.sha256 == '253475779f9f0246639453efb691896c930cc2285e4ecb15c265e7ba81ca2785'
text = (source_site / module.TOKENS_ROUTE.lstrip('/')).read_bytes().decode('utf-8')
values = module._extract_lore_assignments(text)

class LoreHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text = []
    def handle_starttag(self, tag, attrs):
        assert tag in {'h3', 'br'} and not attrs, (tag, attrs)
        self.tags.append(tag)
    def handle_endtag(self, tag):
        assert tag == 'h3', tag
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
    def handle_data(self, data):
        self.text.append(data)

expected = {
    'alliance': (850, 'a66e97b203a110fab7b1277bdce845511694abcadc8b8c62debcfc524a3ab38a', 'The Aldor'),
    'horde': (1104, '6240957e7afb12dce1026e8dffdb0c206b47f63e69c34c4a57f67a1154543a07', 'The Scryers'),
}
for key, (length, digest, heading) in expected.items():
    value = values[key]
    assert len(value) == length and hashlib.sha256(value.encode()).hexdigest() == digest
    assert value.startswith('<h3>' + heading + '</h3>')
    parser = LoreHTML()
    parser.feed(value)
    assert parser.tags.count('h3') == 1 and parser.tags.count('br') == 2
    assert len(''.join(parser.text)) > 700
main_bytes = (source_site / module.MAIN_ROUTE.lstrip('/')).read_bytes()
assert b'loreTexts["alliance"] =' not in main_bytes and b'loreTexts["horde"] =' not in main_bytes
assert b'RewardItems' not in bundle.generated_file.data
receipt = {
    'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Reuse exactly the two original April 2 2008 faction lore literals from the saved token variant on the saved main faction page.',
    'source': dict(bundle.source_metadata),
    'helper': {'path': bundle.generated_file.relative, 'bytes': bundle.generated_file.length,
               'sha256': bundle.generated_file.sha256},
    'parent_review': ['Original faction names and paragraphs inspected.',
                      'Only one h3 and two br elements per body, without attributes or active content.',
                      'Main script lacks both assignments; reward data and existing switchClick implementation remain unchanged.'],
    'design': {'enabled_only_by_explicit_export_flag': True,
               'page_route': module.PAGE_ROUTE, 'injection': 'defer',
               'fill_only_missing_lore_values': True, 'do_not_overwrite_populated_panel': True,
               'token_page_and_historical_business_pages_excluded': True},
    'bindings': [{'path': 'tools/aldor_scryers_lore.py', 'sha256': sha(ROOT / 'tools/aldor_scryers_lore.py')},
                 {'path': Path(__file__).relative_to(ROOT).as_posix(), 'sha256': sha(Path(__file__))}],
    'network_requests': 0, 'production_integrated': False, 'published': False,
}
OUT.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'lore_lengths': {k: len(v) for k, v in values.items()}, 'receipt_sha256': sha(OUT)}))

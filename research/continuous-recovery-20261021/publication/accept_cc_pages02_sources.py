"""Independently reparse three acquired ARC members and decide actual use."""
import hashlib
import html
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
from commoncrawl_arc import parse_arc_gzip_member

PUB = Path(__file__).resolve().parent
BASE = ROOT/'research/continuous-recovery-20261021/network/commoncrawl-main-pages02'
OUT = PUB/'root-commoncrawl-pages02-content-acceptance.json'
assert not OUT.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
curated_path = BASE/'runtime-r2/curated-main-pages-sources-r2.json'
curated = read(curated_path)
review_path = BASE/'content-review-r2/curated-content-review-r2.json'
review = {r['entity_id']:r for r in read(review_path)['records']}
manifest_path = ROOT/'.scratch/offline-non-gallery-20261021-v16/build-manifest.json'
manifest = {r['route']:r for r in read(manifest_path)['files']}
norm = lambda s: ' '.join(html.unescape(s).replace('\u2019', "'").split())
class ArticleParser(HTMLParser):
    def __init__(self, region=False):
        super().__init__(convert_charrefs=True)
        self.region = region
        self.depth = 0
        self.found = not region
        self.parts = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.region and tag == 'div':
            if self.depth:
                self.depth += 1
            elif 'postbody' in str(attrs.get('class','')).lower().split():
                self.depth = 1
                self.found = True
        if (not self.region or self.depth) and tag == 'img' and attrs.get('src'):
            self.images.append(attrs['src'])
    def handle_endtag(self, tag):
        if self.region and tag == 'div' and self.depth:
            self.depth -= 1
    def handle_data(self, data):
        if not self.region or self.depth:
            self.parts.append(data)
def parsed(data, region=False):
    parser = ArticleParser(region)
    parser.feed(data.decode('utf-8', errors='replace'))
    parser.close()
    assert parser.found
    return norm(' '.join(parser.parts)), sorted(set(parser.images))
month, _ = parsed((ROOT/'.scratch/offline-non-gallery-20261021-v16/site/news/rss-05-2008.xml').read_bytes())
accepted = []
for row in curated['records']:
    indexed = row['indexed']
    member = ROOT/row['private_entity_path']
    compressed = member.read_bytes()
    assert len(compressed) == indexed['length'] and sha(member) == row['request']['body_sha256']
    arc = parse_arc_gzip_member(compressed, expected_url=indexed['url'], expected_timestamp=indexed['timestamp'], expected_status=200, expected_digest=indexed['digest'], max_decompressed_bytes=8*1024*1024)
    payload = arc.http.payload
    old = review[row['entity_id']]
    payload_hash = hashlib.sha256(payload).hexdigest()
    assert len(payload) == old['payload_bytes'] and payload_hash == old['payload_sha256']
    item = {'entity_id':row['entity_id'], 'source_url':arc.url, 'capture_timestamp':arc.timestamp, 'arc_filename':indexed['filename'], 'offset':indexed['offset'], 'compressed_length':len(compressed), 'payload_length':len(payload), 'payload_sha256':payload_hash, 'stored_http_status':arc.http.status, 'arc_record_length':arc.declared_length, 'stored_http_content_length':[x.decode('ascii') for x in arc.http.values('content-length')]}
    if row['entity_id'] == 'pages02-01':
        xml = ET.fromstring(payload)
        items = xml.findall('./channel/item')
        titles = [norm(''.join(r.find('title').itertext())) for r in items]
        assert len(items) == 9 and all(t in month for t in titles)
        # Descriptions contain mixed XML/HTML; do not use Element.text as a full body.
        item.update({'decision':'retain_source_only_existing_news_titles', 'rss_items':9, 'new_reading_pages':0, 'all_titles_in_existing_month_page':True, 'descriptions_not_imported':True})
    elif row['entity_id'] == 'pages02-05':
        assert len(payload) == 131072 and b'</html>' not in payload.lower() and b'</body>' not in payload.lower()
        assert payload.rstrip().endswith(b'<td') or b'<td' in payload[-100:]
        assert arc.http.values('content-length') == ()
        item.update({'decision':'reject_truncated_html_replacement', 'new_reading_pages':0, 'reason':'Stored payload ends mid table markup at 128KiB with no body/html closure. ARC record length includes the HTTP header and is not an HTTP Content-Length.'})
    elif row['entity_id'] == 'pages02-07':
        current_row = manifest['/info/underdev/implemented/index.html']
        current = (ROOT/current_row['source_local_path']).read_bytes()
        texts = []
        images = []
        for data in (payload, current):
            text, image_set = parsed(data, region=True)
            texts.append(text)
            images.append(image_set)
        assert texts[0] == texts[1] and images[0] == images[1]
        item.update({'decision':'retain_source_only_duplicate_article', 'new_reading_pages':0, 'normalized_article_text_sha256':hashlib.sha256(texts[0].encode()).hexdigest(), 'article_images_identical':True, 'current_source_sha256':hashlib.sha256(current).hexdigest()})
    else:
        raise AssertionError(row['entity_id'])
    accepted.append(item)
assert len(accepted) == 3
OUT.write_text(json.dumps({'schema':'wow-root-cc-pages02-content-acceptance/v1', 'accepted_acquisition':True, 'checked_utc':datetime.now(timezone.utc).isoformat(), 'accepted_source_entities':3, 'new_pages':0, 'source16_modified':False, 'records':accepted, 'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (curated_path, review_path, manifest_path, ROOT/'tools/commoncrawl_arc.py')], 'raw_http_and_payloads_private':True}, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'accepted_sources':3, 'new_pages':0, 'receipt_sha256':sha(OUT)}))

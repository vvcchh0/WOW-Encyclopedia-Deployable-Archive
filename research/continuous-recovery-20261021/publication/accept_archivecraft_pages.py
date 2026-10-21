"""Root verification of four current HTML sources and their exact image refs."""
import hashlib
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
BASE = ROOT/'research/continuous-recovery-20261021/network/archivecraft-pages01'
OUT = PUB/'root-archivecraft-pages-source-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inventory = read(BASE/'runtime/public-inventory.json')
private = read(BASE/'runtime/private/report.json')
plan = read(BASE/'plan.json')
assert inventory['complete'] and private['stop_reason'] == 'completed'
assert private['attempt_count'] == 4 and private['total_body_bytes'] == 437557
attempts = private['attempts']
class SourceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.heading = False
        self.headings = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        if tag == 'h1': self.heading = True
        if tag == 'img':
            attrs = dict(attrs)
            if attrs.get('src'): self.images.append(attrs['src'])
    def handle_endtag(self, tag):
        if tag == 'h1': self.heading = False
    def handle_data(self, value):
        if self.heading: self.headings.append(value.strip())
sources = []
for target, record, attempt in zip(plan['targets'], inventory['records'], attempts):
    assert target['url'] == record['url'] == attempt['url']
    assert record['valid'] and attempt['returncode'] == 0 and attempt['http_status'] == 200
    assert attempt['transport'] == 'direct' and not attempt['timed_out']
    body_path = Path(attempt['_body_file'])
    assert body_path.resolve().is_relative_to((BASE/'runtime/private').resolve())
    body = body_path.read_bytes()
    assert len(body) == record['body_bytes'] and sha(body_path) == record['body_sha256']
    assert len(body) < 1024*1024 and b'</html>' in body.lower()
    parser = SourceParser()
    parser.feed(body.decode('utf-8'))
    assert parser.headings
    images = sorted({urljoin(target['url'], src) for src in parser.images if 'encyclopedia-' in src and '/global/' not in src})
    assert len(images) == 1, images
    sources.append({'url':target['url'],'current_observed_utc':attempt['request_finished_utc'],'body_bytes':len(body),'body_sha256':sha(body_path),'heading':' '.join(parser.headings),'article_image_url':images[0],'classification':'current_related_archive_source','historical_capture_timestamp':None})
starts = [datetime.fromisoformat(r['request_started_utc'].replace('Z','+00:00')) for r in attempts]
intervals = [(b-a).total_seconds() for a,b in zip(starts, starts[1:])]
assert min(intervals) >= 6.1
OUT.write_text(json.dumps({'schema':'wow-root-archivecraft-page-source-acceptance/v1','accepted_sources':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'source_pages':sources,'network_attempts':4,'total_body_bytes':437557,'actual_start_intervals_seconds':intervals,'historical_capture_claim':False,'scripts_or_forms_imported':False,'raw_http_private':True,'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (BASE/'plan.json',BASE/'runtime/public-inventory.json',BASE/'parent-execution-receipt.json')]},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted_sources':4,'exact_image_references':4,'receipt_sha256':sha(OUT)}))

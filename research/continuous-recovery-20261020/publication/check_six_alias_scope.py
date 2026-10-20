"""Qualify six historical references without changing the prior evidence."""
import hashlib
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name('root-six-alias-scope-correction.json')
QUEUE = ROOT / 'research/continuous-recovery-20261019/publication/next-media-aliases-source-corrected.json'
BASE = 'http://www.worldofwarcraft.com/news/wow-news2004.html'


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attrs = []
        self.comments = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ('src', 'href') and value:
                self.attrs.append({'tag': tag, 'attribute': name, 'literal': value, 'original': urljoin(BASE, value), 'line': self.getpos()[0]})

    def handle_comment(self, data):
        self.comments.append(data)


def main():
    assert not OUT.exists()
    queue = json.loads(QUEUE.read_bytes())
    targets = {row['original'] for row in queue['candidates']}
    assert len(targets) == 6
    files = []
    for relative, expected in [
        ('.scratch/offline-navigation-20261015-v15/site/news/wow-news2004.html', '825a7c5b4c77d75ed10a04908c392735462b8c56135d2deb6c0450d11002c14d'),
        ('.scratch/pages-resources-20261019-v38/news/wow-news2004.html', None),
    ]:
        body = (ROOT / relative).read_bytes()
        sha = hashlib.sha256(body).hexdigest()
        if expected:
            assert sha == expected
        outer = References()
        outer.feed(body.decode('utf-8'))
        active = [row for row in outer.attrs if row['original'] in targets]
        comments = []
        for text in outer.comments:
            inner = References()
            inner.feed(text)
            comments.extend(row for row in inner.attrs if row['original'] in targets)
        assert not active and len(comments) == 6
        assert {row['original'] for row in comments} == targets
        assert all(row['tag'] == 'img' and row['attribute'] == 'src' for row in comments)
        files.append({'path': relative, 'sha256': sha, 'bytes': len(body), 'active_references': active, 'comment_references': comments})
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
               'qualifies_prior_queue': QUEUE.relative_to(ROOT).as_posix(), 'prior_queue_sha256': hashlib.sha256(QUEUE.read_bytes()).hexdigest(),
               'corrected_attribute': 'img/src', 'reference_scope': 'comment_only', 'active_image_targets': 0,
               'candidate_count': 6, 'files': files,
               'decision': 'Retain as historical commented-source leads. Prioritize active missing-image references for downloads. Do not count these six as visible image repairs or alter the historical comment merely to expose them.'}
    OUT.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))


if __name__ == '__main__':
    main()

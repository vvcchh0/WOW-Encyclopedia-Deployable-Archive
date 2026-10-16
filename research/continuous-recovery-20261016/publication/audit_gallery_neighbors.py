"""Classify positive prefix rows without aliasing neighboring galleries."""
import base64
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image, ImageSequence

R = Path(__file__).resolve().parents[3]
B = R / 'research/continuous-recovery-20261016'
OUT = B / 'local-audit/gallery-neighbors'
sha = lambda b: hashlib.sha256(b).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    index_path = B / 'publication/root-gallery-prefix04-acceptance.json'
    manifest_path = R / '.scratch/offline-navigation-20261015-v15/build-manifest.json'
    prov_path = R / '.scratch/pages-resources-20261016-v20/export-provenance.json'
    index = json.loads(index_path.read_bytes())
    manifest = json.loads(manifest_path.read_bytes())
    provenance = json.loads(prov_path.read_bytes())
    assert index['accepted']
    sources = {x['route']: x for x in manifest['files']}
    published = {x['route']: x for x in provenance['files']}
    rows = defaultdict(list)
    for group in index['results']:
        for n, row in enumerate(group.get('rows', [])):
            u = urlsplit(row['original'])
            if row['statuscode'] != '200' or not row['mimetype'].startswith('image/'):
                continue
            assert u.hostname == 'www.worldofwarcraft.com' and not u.query
            assert '20000101000000' <= row['timestamp'] <= '20080512210044'
            rows[u.hostname + u.path].append((group['label'], n, row))
    entries = []
    for key, values in sorted(rows.items()):
        route = manifest['origin_index'].get(key)
        selected = max(values, key=lambda x: (x[2]['timestamp'], x[2]['original'].startswith('http:')))
        label, n, row = selected
        item = {'original': row['original'], 'gallery_context': label,
                'source_evidence': {'path': index_path.relative_to(R).as_posix(),
                    'sha256': sha(index_path.read_bytes()), 'result_label': label,
                    'row_index': n, 'row': row},
                'positive_rows': [v[2] for v in values],
                'filename_class': 'full' if re.search(r'/ss\d+\.jpg$', key) else 'thumbnail_or_other',
                'relationship': 'Indexed neighboring source path; no mapping to dynamic ss/ssN slots is inferred.'}
        if route is not None:
            source = sources[route]
            p = published[route]
            raw = (R / source['output_path']).read_bytes()
            assert len(raw) == source['derived_length'] == p['derived_length']
            assert sha(raw) == source['derived_sha256'] == p['derived_sha256']
            digest = base64.b32encode(hashlib.sha1(raw).digest()).decode().rstrip('=')
            assert digest in {v[2]['digest'] for v in values}
            assert (R / '.scratch/pages-resources-20261016-v20' / p['output_path']).read_bytes() == raw
            with Image.open(io.BytesIO(raw)) as im:
                im.verify()
            with Image.open(io.BytesIO(raw)) as im:
                dimensions = list(im.size)
                frames = 0
                for frame in ImageSequence.Iterator(im):
                    frame.load(); frames += 1
            item.update(state='already_local_and_published', route=route,
                        sha256=sha(raw), length=len(raw), cdx_digest=digest,
                        actual_capture_timestamp=source['actual_timestamp'],
                        dimensions=dimensions, decoded_frames=frames)
        else:
            item['state'] = 'positive_index_not_local'
        entries.append(item)
    # Balance full-size originals across the three historical directories.
    pools = defaultdict(list)
    for item in entries:
        if item['state'] == 'positive_index_not_local' and item['filename_class'] == 'full':
            pools[item['gallery_context']].append(item)
    chosen = []
    while len(chosen) < 20 and any(pools.values()):
        for label in sorted(pools):
            if pools[label] and len(chosen) < 20:
                chosen.append(pools[label].pop(0))
    assert len(chosen) == 20
    audit = {'schema': 'gallery-neighbor-audit/v1', 'checked_utc': datetime.now(timezone.utc).isoformat(),
             'network_requests': 0, 'index_sha256': sha(index_path.read_bytes()),
             'source_manifest_sha256': sha(manifest_path.read_bytes()),
             'published_provenance_sha256': sha(prov_path.read_bytes()),
             'counts': dict(Counter(x['state'] for x in entries)),
             'filename_counts': dict(Counter((x['state'] + ':' + x['filename_class']) for x in entries)),
             'entries': entries}
    (OUT / 'audit.json').write_bytes((json.dumps(audit, indent=2) + '\n').encode())
    data = {'schema': 'gallery-neighbor-exact-candidates/v1', 'generated_utc': audit['checked_utc'],
            'scope': 'Fresh exact CDX and image replay for positively indexed neighboring full images. Separate historical materials, not aliases for dynamic gallery slots.',
            'inputs': [{'path': (OUT/'audit.json').relative_to(R).as_posix(), 'sha256': sha((OUT/'audit.json').read_bytes())}],
            'candidate_count': len(chosen), 'candidates': chosen}
    (OUT / 'full-images20-candidates.json').write_bytes((json.dumps(data, indent=2) + '\n').encode())
    print(json.dumps({'counts': audit['counts'], 'filename_counts': audit['filename_counts'],
                      'selected_by_group': dict(Counter(x['gallery_context'] for x in chosen)),
                      'candidate_sha256': sha((OUT/'full-images20-candidates.json').read_bytes())}))


if __name__ == '__main__':
    main()

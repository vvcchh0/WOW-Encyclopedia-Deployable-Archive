"""Freeze an explicit list of root-reviewed source batches for v33, offline."""
import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bind = lambda p: {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}
PRIMARY = {'www.worldofwarcraft.com', 'worldofwarcraft.com'}
SUPPLEMENT = {'www.wowarmory.com', 'armory.wow-europe.com', 'www.blizzard.com'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--names', nargs='+', required=True)
    args = parser.parse_args()
    assert len(args.names) == len(set(args.names))
    assert all(re.fullmatch(r'[a-z0-9-]+', n) for n in args.names)
    out = PUB / 'root-v33-source-receipts-manifest.json'
    assert not out.exists()
    assert datetime.now(timezone.utc) < datetime(2026,10,18,13,50,tzinfo=timezone.utc)
    assert shutil.disk_usage(ROOT).free >= 11005853696
    rows, batches, originals = [], [], set()
    for name in args.names:
        source = PUB / f'root-{name}-source-acceptance.json'
        public = PUB / f'root-{name}-public-copy-acceptance.json'
        visual = PUB / f'root-{name}-visual-acceptance.json'
        s, p, v = read(source), read(public), read(visual)
        assert s['accepted'] and p['accepted'] and v['accepted']
        assert p['copy_mode'] == 'original_bytes'
        pb = p.get('source_acceptance') or p.get('source_receipt')
        assert pb['sha256'] == sha(source) and pb['path'] == source.relative_to(ROOT).as_posix()
        assert v['source_acceptance_sha256'] == sha(source)
        source_rows = {x['original']: x for x in s['accepted_images']}
        assert len(p['accepted_images']) == v['images'] == len(source_rows)
        counts = {'primary': 0, 'supplement': 0}
        total = 0
        for row in p['accepted_images']:
            assert row['accepted'] and row['original'] not in originals
            originals.add(row['original'])
            assert all(row[k] == source_rows[row['original']][k] for k in ['sha256', 'length', 'mime', 'dimensions', 'actual_capture_timestamp', 'cdx_digest', 'decoded_frames'])
            file = (ROOT / row['local_path']).resolve()
            file.relative_to((PUB / 'accepted-images').resolve())
            assert file.stat().st_size == row['length'] and sha(file) == row['sha256']
            host = urlsplit(row['original']).hostname
            assert host in PRIMARY | SUPPLEMENT
            role = 'primary' if host in PRIMARY else 'supplement'
            counts[role] += 1
            total += row['length']
            rows.append((role, row))
        role = 'mixed' if all(counts.values()) else ('primary' if counts['primary'] else 'supplement')
        batches.append({'id': name, 'role': role, 'expected_count': len(p['accepted_images']), 'expected_bytes': total,
            'expected_primary_count': counts['primary'], 'expected_supplement_count': counts['supplement'],
            'source_acceptance': bind(source), 'public_copy_acceptance': bind(public), 'visual_acceptance': bind(visual)})
    status = read(RUN / 'status.json')
    assert len(rows) == status['accepted_images'] - status['published_images_this_run'], 'explicit source list omits accepted unpublished images'
    result = {'schema': 'wow-recovery.integration.v33-source-receipts-manifest.v1', 'accepted': True,
        'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0, 'export_executed': False,
        'source15_manifest': bind(ROOT / '.scratch/offline-navigation-20261015-v15/build-manifest.json'),
        'original_manifest': bind(ROOT / 'offline/build-manifest.json'), 'batches': batches,
        'new_images': len(rows), 'image_bytes': sum(x['length'] for _,x in rows),
        'new_primary_images': sum(r == 'primary' for r,_ in rows), 'new_supplement_images': sum(r == 'supplement' for r,_ in rows),
        'scope': 'Only the explicit root-reviewed original-byte public copies named here. Failed transfers and index-only results remain outside image maps.'}
    out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: result[k] for k in ['new_images','image_bytes','new_primary_images','new_supplement_images']} | {'sha256': sha(out)}))

if __name__ == '__main__':
    main()

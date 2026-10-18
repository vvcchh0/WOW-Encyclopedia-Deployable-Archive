"""Copy only images from a root-accepted source receipt, without re-encoding."""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = (ROOT / args.receipt).resolve()
    target = (ROOT / args.destination).resolve()
    output = (ROOT / args.output).resolve()
    for path in [source, target, output]:
        path.relative_to(ROOT)
    assert not target.exists() and not output.exists()
    receipt = json.loads(source.read_bytes())
    assert receipt['accepted'] and 1 <= len(receipt['accepted_images']) <= 20
    target.mkdir(parents=True)
    copied = []
    for n, item in enumerate(receipt['accepted_images'], start=1):
        assert item['accepted']
        assert shutil.disk_usage(ROOT).free >= 11005853696 + item['length']
        data = (ROOT / item['private_payload_path']).read_bytes()
        assert len(data) == item['length'] and digest(data) == item['sha256']
        extension = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif'}[item['mime']]
        path = target / f'{n:02d}-image{extension}'
        with path.open('xb') as handle:
            handle.write(data)
        assert path.read_bytes() == data
        copied.append(dict(item, local_path=path.relative_to(ROOT).as_posix()))
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'source_acceptance': {'path': source.relative_to(ROOT).as_posix(), 'sha256': digest(source.read_bytes())},
              'copy_mode': 'original_bytes', 'accepted_images': copied,
              'image_bytes': sum(x['length'] for x in copied), 'disk_free_bytes': shutil.disk_usage(ROOT).free}
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': True, 'images': len(copied), 'bytes': result['image_bytes']}))


if __name__ == '__main__':
    main()

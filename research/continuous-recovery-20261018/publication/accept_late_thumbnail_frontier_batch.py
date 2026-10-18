"""Root checks and unchanged public copies for an explicitly approved image batch."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--plan-acceptance', required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'[a-z0-9-]+', args.name)
    directory = (ROOT / args.directory).resolve()
    directory.relative_to((RUN / 'network').resolve())
    plan = directory / 'plan.json'
    gate = json.loads((ROOT / args.plan_acceptance).read_bytes())
    assert gate['accepted'] and gate['plan_sha256'] == sha(plan)
    source = PUB / f'root-{args.name}-source-acceptance.json'
    copies = PUB / f'root-{args.name}-public-copy-acceptance.json'
    contact = PUB / f'{args.name}-contact.png'
    assert not any(p.exists() for p in [source, copies, contact])
    python = [sys.executable, '-X', 'utf8']
    subprocess.run(python + [str(RUN / 'integration/late-thumbnail-source-checker/accept_late_thumbnail_batch.py'), '--native-queue', str(PUB / 'native-observed-late-thumbnails12-queue.json'), '--batch-directory', str(directory / 'output'),
                            '--plan', str(plan), '--starting-failures', str(gate['starting_failures']), '--output', str(source)], cwd=ROOT, check=True)
    accepted = json.loads(source.read_bytes())['accepted_images']
    if not accepted:
        print(json.dumps({'source_accepted': True, 'source_sha256': sha(source), 'images': 0, 'visual_review_pending': False}))
        return
    subprocess.run(python + [str(PUB / 'copy_accepted_images.py'), '--receipt', str(source),
                            '--destination', str(PUB / 'accepted-images' / args.name), '--output', str(copies)], cwd=ROOT, check=True)
    items = json.loads(copies.read_bytes())['accepted_images']
    images = []
    for item in items:
        image = Image.open(ROOT / item['local_path'])
        image.seek(0)
        image.load()
        # This contact sheet is a QA derivative; publication copies remain the original bytes.
        preview = image.convert('RGB')
        preview.thumbnail((600, 500))
        images.append(preview)
    width = max(240, max(im.width for im in images) + 20)
    height = max(110, max(im.height for im in images) + 65)
    columns = min(3, len(items))
    sheet = Image.new('RGB', (width * columns, height * ((len(items) + columns - 1) // columns)), '#f0ece2')
    draw = ImageDraw.Draw(sheet)
    for index, (item, image) in enumerate(zip(items, images)):
        x, y = index % columns * width, index // columns * height
        draw.text((x + 5, y + 8), item['original'].rsplit('/', 1)[-1][:40], fill='#222222')
        sheet.paste(image, (x + (width - image.width) // 2, y + 30))
        draw.text((x + 5, y + height - 22), item['actual_capture_timestamp'], fill='#222222')
    sheet.save(contact)
    print(json.dumps({'source_sha256': sha(source), 'public_copy_sha256': sha(copies), 'images': len(items),
                      'contact': contact.relative_to(ROOT).as_posix(), 'contact_sha256': sha(contact),
                      'network_requests': 0, 'visual_review_pending': True}))


if __name__ == '__main__':
    main()

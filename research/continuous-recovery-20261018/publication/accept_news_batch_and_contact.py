"""Local-only root source checks, unchanged public copies and a review contact sheet."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261018'
PUB = BASE / 'publication'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-index', required=True, type=int, choices=range(1, 9))
    args = parser.parse_args()
    number = args.batch_index
    directory = BASE / f'network/news-unplanned-v26/batch-{number:02}'
    plan = directory / 'plan.json'
    gate = json.loads((PUB / f'root-news-unplanned-batch{number}-plan-acceptance.json').read_bytes())
    assert gate['accepted'] and gate['plan_sha256'] == sha(plan)
    source = PUB / f'root-news-unplanned-batch{number}-source-acceptance.json'
    copies = PUB / f'root-news-unplanned-batch{number}-public-copy-acceptance.json'
    contact = PUB / f'news-unplanned-batch{number}-contact.png'
    assert not source.exists() and not copies.exists() and not contact.exists()
    command = [sys.executable, '-X', 'utf8']
    subprocess.run(command + [str(PUB / 'accept_image_batch.py'), '--batch-directory', str(directory / 'output'),
                             '--plan', str(plan), '--starting-failures', str(gate['starting_failures']), '--output', str(source)], cwd=ROOT, check=True)
    subprocess.run(command + [str(PUB / 'copy_accepted_images.py'), '--receipt', str(source),
                             '--destination', str(PUB / f'accepted-images/news-unplanned-batch{number}'), '--output', str(copies)], cwd=ROOT, check=True)
    items = json.loads(copies.read_bytes())['accepted_images']
    images = []
    for item in items:
        image = Image.open(ROOT / item['local_path'])
        image.seek(0)
        image.load()
        assert image.width <= 600 and image.height <= 600, 'Large image needs individual visual review'
        images.append(image.convert('RGB'))
    width = max(image.width for image in images) + 20
    height = max(image.height for image in images) + 65
    sheet = Image.new('RGB', (width * 3, height * ((len(items) + 2) // 3)), '#f0ece2')
    draw = ImageDraw.Draw(sheet)
    for index, (item, image) in enumerate(zip(items, images)):
        x, y = index % 3 * width, index // 3 * height
        draw.text((x + 5, y + 8), item['original'].rsplit('/', 1)[-1], fill='#222222')
        sheet.paste(image, (x + (width - image.width) // 2, y + 28))
        draw.text((x + 5, y + height - 24), item['actual_capture_timestamp'], fill='#222222')
    sheet.save(contact)
    print(json.dumps({'source_sha256': sha(source), 'images': len(items), 'contact_sheet': str(contact),
                      'contact_sheet_sha256': sha(contact), 'network_requests': 0, 'visual_review_pending': True}))


if __name__ == '__main__':
    main()

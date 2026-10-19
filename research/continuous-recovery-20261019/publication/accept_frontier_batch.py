"""Check a saved batch, copy accepted original bytes and prepare visual QA."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
PUB = RUN / "publication"
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    args = parser.parse_args()
    assert re.fullmatch(r"frontier-[a-z0-9-]+", args.packet)
    packet = RUN / "network" / args.packet
    go = json.loads((PUB / f"root-{args.packet}-execute-go.json").read_bytes())
    assert go["accepted"] and go["root_go"] and go["plan_sha256"] == SHA(packet / "plan.json")
    source = PUB / f"root-{args.packet}-source-acceptance.json"
    copies = PUB / f"root-{args.packet}-public-copy-acceptance.json"
    contact = PUB / f"{args.packet}-contact.png"
    assert not any(p.exists() for p in (source, copies, contact))
    python = [sys.executable, "-B", "-X", "utf8"]
    subprocess.run(python + [str(PUB / "accept_image_batch.py"), "--batch-directory", str(packet / "output"),
        "--plan", str(packet / "plan.json"), "--starting-failures", str(go["prior_failure_tail"]),
        "--output", str(source)], cwd=ROOT, check=True, timeout=90)
    accepted = json.loads(source.read_bytes())["accepted_images"]
    if not accepted:
        print(json.dumps({"source_accepted": True, "images": 0, "visual_review_pending": False}))
        return
    copy_tool = ROOT / "research/continuous-recovery-20261018/publication/copy_accepted_images.py"
    assert SHA(copy_tool) == "80265091756e01f8d53886c294e6273aab98f9e9bc5fcc17bc80ae0c8350377b"
    subprocess.run(python + [str(copy_tool), "--receipt", str(source), "--destination", str(PUB / "accepted-images" / args.packet),
        "--output", str(copies)], cwd=ROOT, check=True, timeout=90)
    items = json.loads(copies.read_bytes())["accepted_images"]
    assert 1 <= len(items) <= 20 and shutil.disk_usage(ROOT).free >= 11005853696
    images = []
    for item in items:
        with Image.open(ROOT / item["local_path"]) as image:
            image.load()
            preview = image.convert("RGB")
            preview.thumbnail((600, 500))
            images.append(preview)
    width = max(240, max(im.width for im in images) + 20)
    height = max(150, max(im.height for im in images) + 65)
    columns = min(5, len(items))
    sheet = Image.new("RGB", (width * columns, height * ((len(items) + columns - 1) // columns)), "#f0ece2")
    draw = ImageDraw.Draw(sheet)
    for index, (item, image) in enumerate(zip(items, images)):
        x, y = index % columns * width, index // columns * height
        draw.text((x + 5, y + 8), str(index + 1) + " " + item["original"].rsplit("/", 1)[-1][:36], fill="#222222")
        sheet.paste(image, (x + (width - image.width) // 2, y + 30))
        draw.text((x + 5, y + height - 22), item["actual_capture_timestamp"], fill="#222222")
    sheet.save(contact)
    print(json.dumps({"source_sha256": SHA(source), "public_copy_sha256": SHA(copies),
        "images": len(items), "contact": contact.relative_to(ROOT).as_posix(),
        "contact_sha256": SHA(contact), "network_requests": 0, "visual_review_pending": True}))


if __name__ == "__main__":
    main()

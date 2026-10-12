"""Export unmodified 2008 sample entities and package the reassessment evidence."""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import urllib.parse
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples/20080512"
BACKUP = ROOT / "backups/20080512-sample"
MAX_BYTES = 14_000_000_000
MIN_FREE = 10 * 1024**3
RESERVE = 256 * 1024**2


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def guard(extra: int = 0) -> dict:
    used = sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())
    free = shutil.disk_usage(ROOT).free
    if used + extra + RESERVE > MAX_BYTES or free - extra < MIN_FREE + RESERVE:
        raise RuntimeError(f"Space guard: workspace={used}, free={free}, extra={extra}")
    return {"workspace_bytes": used, "disk_free_bytes": free}


def json_write(path: Path, value: object) -> None:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    guard(len(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def export_sample() -> dict:
    plan = json.loads((ROOT / "research/reassessment-2008/downloads/plan.json").read_text(encoding="utf-8"))
    records = [json.loads(line) for line in (BACKUP / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    records = {(r["original"], r["requested_timestamp"]): r for r in records if r["status"] == "success"}
    baseline = ROOT / "research/baseline/index.xml"
    baseline_headers = json.loads((ROOT / "research/baseline/headers.json").read_text(encoding="utf-8"))
    mapping = []
    images = 0
    cdx_checks = 0
    for item in plan["items"]:
        record = records[(item["original"], item["timestamp"])]
        with zipfile.ZipFile(BACKUP / record["zip_part"]) as archive:
            data = archive.read(record["zip_entry"])
        if sha(data) != record["sha256"] or len(data) != record["content_length"]:
            raise RuntimeError("Saved entity integrity failed: " + item["original"])
        if item.get("cdx_digest"):
            digest = base64.b32encode(hashlib.sha1(data).digest()).decode("ascii")
            if digest != item["cdx_digest"]:
                raise RuntimeError("CDX entity digest mismatch: " + item["original"])
            cdx_checks += 1
        headers = record["response_headers"]
        mime = next((v for k, v in headers.items() if k.lower() == "content-type"), "")
        actual = record["actual_timestamp"]
        source = {"manifest": "backups/20080512-sample/manifest.jsonl", "zip_part": record["zip_part"], "zip_entry": record["zip_entry"], "requested_timestamp": record["requested_timestamp"]}
        url = urllib.parse.urlsplit(item["original"])
        if url.hostname != "www.worldofwarcraft.com" or url.query:
            raise RuntimeError("Unexpected URL in finite sample")
        extension = Path(url.path).suffix.lower()
        if extension in {".jpg", ".jpeg", ".gif", ".png"}:
            valid = (extension in {".jpg", ".jpeg"} and data.startswith(b"\xff\xd8\xff")) or (extension == ".gif" and data.startswith((b"GIF87a", b"GIF89a"))) or (extension == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n"))
            if not valid:
                raise RuntimeError("Invalid image entity: " + item["original"])
            images += 1
        elif item["role"] == "sample_page":
            if not mime.lower().startswith("text/html") or b"<html" not in data[:200].lower():
                raise RuntimeError("Unexpected sample page representation")
        elif b"<!doctype html" in data[:200].lower() or b"<html" in data[:200].lower():
            raise RuntimeError("HTML error masquerading as source dependency")
        if url.path.endswith("/index.xml"):
            precise = baseline.read_bytes()
            if precise != data:
                raise RuntimeError("Exact requested baseline differs; explicit new selection required")
            data = precise
            headers = baseline_headers["headers"]
            mime = next(v for k, v in headers.items() if k.lower() == "content-type")
            actual = "20080512210044"
            source = {"body": "research/baseline/index.xml", "metadata": "research/baseline/headers.json", "requested_timestamp": "20080512210044", "identical_sample_zip_capture": record["actual_timestamp"]}
        destination = SAMPLE / "www.worldofwarcraft.com" / url.path.lstrip("/")
        destination.resolve().relative_to(SAMPLE.resolve())
        guard(len(data))
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.read_bytes() != data:
            raise RuntimeError("Refusing to replace a different exported entity")
        destination.write_bytes(data)
        mapping.append({"logical_original": item["original"], "local_path": destination.relative_to(ROOT).as_posix(), "actual_timestamp": actual, "content_type": mime, "bytes": len(data), "sha256": sha(data), "source": source, "content_class": "html_page" if item["role"] == "sample_page" else "source_resource"})
    result = {"anchor": "20080512210044", "unmodified_entities": True, "offline_rendering_verified": False, "files": len(mapping), "entity_bytes": sum(r["bytes"] for r in mapping), "image_magic_checks_passed": images, "cdx_entity_checks_passed": cdx_checks, "note": "URL paths are exported for inspection. XML filenames retain the recorded HTML MIME in this map. Absolute links and missing dependencies require a later reconstruction step. Homepage uses the exact user-supplied capture; all other items retain their own actual capture dates.", "items": mapping}
    json_write(SAMPLE / "url-map.json", result)
    return result


def package(full_2008: bool = False) -> dict:
    prior_package = ROOT / "artifacts/WOW_Encyclopedia_20101203_source.zip"
    prior_expected_sha = "9b074874780d93c55a9edd98e2dd2d498c524e4dddd2d09fd4c981e03550437d"
    if sha(prior_package.read_bytes()) != prior_expected_sha:
        raise RuntimeError("Prior 2010 package differs from its recorded acquisition hash")
    prior_reassessment = ROOT / "artifacts/WOW_Encyclopedia_20080512_sample_and_reassessment.zip"
    prior_reassessment_sha = "5d23d49010d98049162ea7ce64a0c6f4b84ad8f519cc435c0d5e3a3ed8c2bd25"
    if full_2008 and sha(prior_reassessment.read_bytes()) != prior_reassessment_sha:
        raise RuntimeError("Prior reassessment package differs from its recorded hash")
    name = "WOW_Encyclopedia_20080512_full_source.zip" if full_2008 else "WOW_Encyclopedia_20080512_sample_and_reassessment.zip"
    out = ROOT / "artifacts" / name
    if out.exists():
        raise RuntimeError("Review existing package before creating another; no silent overwrite")
    source_dirs = ("docs", "tools", "tests", "research", "backups", "packaging", "samples", "mirror") if full_2008 else ("docs", "tools", "tests", "research", "backups", "packaging", "samples")
    directories = [ROOT / directory for directory in source_dirs if (ROOT / directory).is_dir()]
    files = [ROOT / "README.md"]
    files += [p for d in directories for p in d.rglob("*") if p.is_file() and not p.is_symlink() and "__pycache__" not in p.parts and p.suffix != ".pyc"]
    files = sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix())
    source_hashes = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in files}
    checksums = "".join(f"{digest}  {path}\n" for path, digest in source_hashes.items()).encode("utf-8")
    guard(sum(p.stat().st_size for p in files) + len(checksums))
    temporary = out.with_name(name + ".partial-" + uuid.uuid4().hex)
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for p in files:
            data = p.read_bytes()
            rel = p.relative_to(ROOT).as_posix()
            if sha(data) != source_hashes[rel]:
                raise RuntimeError("Source changed during packaging: " + rel)
            guard(len(data))
            archive.writestr("WOW_Encyclopedia/" + rel, data, compress_type=zipfile.ZIP_STORED if p.suffix.lower() in {".zip", ".png", ".jpg", ".gif"} else zipfile.ZIP_DEFLATED)
        archive.writestr("WOW_Encyclopedia/FILE_SHA256SUMS.txt", checksums)
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Package CRC verification failed")
        for rel, digest in source_hashes.items():
            if sha(archive.read("WOW_Encyclopedia/" + rel)) != digest or sha((ROOT / rel).read_bytes()) != digest:
                raise RuntimeError("Package or source SHA verification failed: " + rel)
    temporary.replace(out)
    if sha(prior_package.read_bytes()) != prior_expected_sha:
        raise RuntimeError("Prior 2010 package changed while packaging")
    if full_2008 and sha(prior_reassessment.read_bytes()) != prior_reassessment_sha:
        raise RuntimeError("Prior reassessment package changed while packaging")
    digest = sha(out.read_bytes())
    (out.with_suffix(out.suffix + ".sha256")).write_text(f"{digest}  {name}\n", encoding="ascii")
    result = {"finished_at": datetime.now(timezone.utc).isoformat(), "package": out.relative_to(ROOT).as_posix(), "bytes": out.stat().st_size, "sha256": digest, "source_files": len(files), "zip_entries": len(files) + 1, "crc_ok": True, "all_source_sha256_ok": True, "space": guard(), "prior_2010_package_unchanged": True, "prior_2010_package_sha256": prior_expected_sha, "prior_reassessment_package_unchanged": True if full_2008 else None}
    verification_name = "full-2008-package-verification.json" if full_2008 else "reassessment-package-verification.json"
    json_write(ROOT / "artifacts" / verification_name, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize-only", action="store_true")
    parser.add_argument("--full-2008", action="store_true", help="Package the completed full 2008 acquisition and mirror without replacing the sample package")
    args = parser.parse_args()
    if args.full_2008:
        if args.materialize_only:
            parser.error("--full-2008 cannot be combined with --materialize-only")
        if not (ROOT / "mirror/20080512/url-map.json").is_file():
            parser.error("The full 2008 mirror URL map must be exported and reviewed first")
        print(json.dumps(package(full_2008=True), ensure_ascii=False, indent=2))
    else:
        sample = export_sample()
        print(json.dumps({"sample_files": sample["files"], "bytes": sample["entity_bytes"], "image_magic_checks_passed": sample["image_magic_checks_passed"], "cdx_entity_checks_passed": sample["cdx_entity_checks_passed"]}))
        if not args.materialize_only:
            print(json.dumps(package(), ensure_ascii=False, indent=2))

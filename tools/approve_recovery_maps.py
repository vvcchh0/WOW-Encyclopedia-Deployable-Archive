"""Normalize independently checked recovery maps for the offline builder.

This adapter changes metadata only. It never changes preserved entity bytes.
Run validate_recovery_sources.py on its output before rebuilding the site.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def original_from_replay(value: str) -> str:
    match = re.search(r"/web/\d{14}[a-z_]*?/(https?://.+)", value)
    return match.group(1) if match else value


def approve(source: Path, destination: Path, *, merge: bool = False,
            allow_pre2008_static_supplement: bool = False) -> dict:
    source_data = source.read_bytes()
    data = json.loads(source_data)
    corrections_path = ROOT / "research/offline-2008/full-recovery/mime-corrections.json"
    corrections = json.loads(corrections_path.read_text(encoding="utf-8")) if corrections_path.is_file() else {}
    files = {}
    if merge and destination.is_file():
        prior = json.loads(destination.read_text(encoding="utf-8"))
        files = {item["logical_url"]: item for item in prior.get("files", [])}
    source_sha = hashlib.sha256(source_data).hexdigest()
    snapshots = ROOT / "research/offline-2008/full-recovery/map-snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    snapshot = snapshots / f"{source.stem}-{source_sha}.json"
    if snapshot.exists():
        if snapshot.read_bytes() != source_data:
            raise ValueError("Immutable source map snapshot has different bytes")
    else:
        with snapshot.open("xb") as stream:
            stream.write(source_data)
    for record in data.get("files", []):
        item = dict(record)
        item["approval_source_map"] = source.relative_to(ROOT).as_posix()
        item["approval_source_map_sha256"] = source_sha
        item["approval_source_map_snapshot"] = snapshot.relative_to(ROOT).as_posix()
        if not item.get("local_path"):
            raise ValueError("Source map has no exported local_path")
        stamp = str(item.get("actual_timestamp", ""))
        if not stamp.startswith("2008"):
            earlier_static = (allow_pre2008_static_supplement and re.fullmatch(r"\d{14}", stamp)
                              and stamp < "20080101000000" and item.get("kind") == "image"
                              and str(item.get("response_content_type") or item.get("mime", "")).startswith("image/")
                              and item.get("temporal_class") == "pre2008_static_supplement"
                              and item.get("supplement_note") and item.get("year_fallback_evidence"))
            if not earlier_static:
                raise ValueError("Non-2008 entity cannot enter recovery approval map without explicit static supplement evidence")
        if str(item["actual_timestamp"]) > "20080512210044":
            item["original_temporal_class"] = item.get("temporal_class")
            item["temporal_class"] = "after_anchor_2008_supplement"
            item["supplement_note"] = "Actual capture is later than the fixed 2008-05-12 baseline; used explicitly as a reconstruction supplement."
        if not item.get("zip_file"):
            backup = data.get("backup_dir")
            if not backup or not item.get("zip_part"):
                raise ValueError("Missing source ZIP provenance")
            item["zip_file"] = (Path(backup) / item["zip_part"]).as_posix()
        correction = corrections.get(item["logical_url"], {})
        if correction and correction.get("sha256") == item.get("sha256"):
            item["served_mime"] = correction["served_mime"]
            item["mime_override_reason"] = correction["reason"]
            item["mime_correction_evidence"] = correction["validation_evidence"]
            item["mime_correction_policy"] = corrections_path.relative_to(ROOT).as_posix()
            policy_bytes = corrections_path.read_bytes()
            policy_sha = hashlib.sha256(policy_bytes).hexdigest()
            policy_snapshot = snapshots / f"mime-corrections-{policy_sha}.json"
            if not policy_snapshot.exists():
                with policy_snapshot.open("xb") as stream:
                    stream.write(policy_bytes)
            elif policy_snapshot.read_bytes() != policy_bytes:
                raise ValueError("Immutable MIME correction policy snapshot has different bytes")
            item["mime_correction_policy_sha256"] = policy_sha
            item["mime_correction_policy_snapshot"] = policy_snapshot.relative_to(ROOT).as_posix()
        item["mime"] = item.get("served_mime") or item.get("response_content_type") or item.get("content_type") or item.get("mime")
        actual = original_from_replay(item.get("actual_url") or "")
        # A replay can serve a directory capture at a slashless logical alias
        # without redirecting the outer replay URL. Preserve the exporter's
        # capture base (or the CDX original), rather than losing its slash.
        item["source_base_url"] = (item.get("source_base_url") or item.get("base_url")
                                   or item.get("capture_original") or item.get("source_url")
                                   or actual or item["logical_url"])
        item["base_url"] = item["source_base_url"]
        path = urlsplit(item["logical_url"]).path or "/"
        if path != "/" and not posixpath.splitext(path.rstrip("/"))[1]:
            item["derived_route"] = path.rstrip("/") + "/index.html"
            item["route_aliases"] = sorted(set(item.get("route_aliases", [])) | {path.rstrip("/"), path.rstrip("/") + "/"})
        if path == "/index.xml" and item.get("kind") == "html":
            item["route_aliases"] = sorted(set(item.get("route_aliases", [])) | {"/"})
        prior = files.get(item["logical_url"])
        if prior:
            def rank(value: dict) -> tuple:
                stamp = str(value["actual_timestamp"])
                # A later batch must not replace a nearer pre-anchor capture
                # with an older or post-anchor representation accidentally.
                return (0, -int(stamp)) if stamp <= "20080512210044" else (1, int(stamp))
            if rank(prior) < rank(item):
                continue
        files[item["logical_url"]] = item
    if not files:
        raise ValueError("No real exported source files")
    result = {
        "schema_version": 1, "anchor_timestamp": "20080512210044",
        "source_map": source.relative_to(ROOT).as_posix(),
        "source_map_sha256": source_sha,
        "status": "metadata_normalized_pending_independent_validation",
        "network_performed": False, "unmodified_entity_bytes": True,
        "files": [files[key] for key in sorted(files)],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".partial")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return {"map": destination.relative_to(ROOT).as_posix(), "files": len(files)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--merge", action="store_true", help="retain earlier independently preserved batches")
    parser.add_argument("--allow-pre2008-static-supplement", action="store_true",
                        help="explicit separate map for evidenced earlier static images; never baseline")
    args = parser.parse_args()
    print(json.dumps(approve(args.source.resolve(), args.output.resolve(), merge=args.merge,
                             allow_pre2008_static_supplement=args.allow_pre2008_static_supplement)))


if __name__ == "__main__":
    main()

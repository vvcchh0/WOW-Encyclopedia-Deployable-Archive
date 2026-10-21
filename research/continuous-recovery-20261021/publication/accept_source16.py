"""Independently compare the new Source16 input with frozen Source15 bytes."""
from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
DAY = ROOT / "research/continuous-recovery-20261021"
OLD = ROOT / ".scratch/offline-navigation-20261015-v15"
NEW = ROOT / ".scratch/offline-non-gallery-20261021-v16"
FROZEN = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class AnchorChanges(HTMLParser):
    def __init__(self, text, accepted):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.accepted = accepted
        self.edits = []
        self.line_starts = [0]
        self.line_starts += [m.end() for m in re.finditer("\n", text)]

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if not href:
            return
        parsed = urlsplit(href)
        values = parse_qs(parsed.query).get("requested", [])
        if parsed.path != "/__offline/missing.html" or len(values) != 1 or values[0] not in self.accepted:
            return
        token = self.get_starttag_text()
        match = re.search(r"\bhref\s*=\s*([\"'])(.*?)\1", token, re.I | re.S)
        assert match
        line, col = self.getpos()
        start = self.line_starts[line - 1] + col + match.start(2)
        end = self.line_starts[line - 1] + col + match.end(2)
        self.edits.append((start, end, self.accepted[values[0]]))

    def rewritten(self):
        value = self.text
        for start, end, target in reversed(self.edits):
            value = value[:start] + html.escape(target, quote=True) + value[end:]
        return value


def main():
    assert sha(OLD / "build-manifest.json") == FROZEN
    old = load(OLD / "build-manifest.json")
    new = load(NEW / "build-manifest.json")
    source_map = load(DAY / "integration/main-pages-review/source16-input-map.json")
    prep = load(DAY / "integration/source16/prepare.json")
    rows = source_map["records"]
    bodies = {r["proposed_route"].lstrip("/"): r for r in rows if r["proposed_use"] != "alias_only"}
    added = {r["proposed_route"].lstrip("/") for r in rows if r["proposed_use"] == "add"}
    old_files = {p.relative_to(OLD / "site").as_posix(): p for p in (OLD / "site").rglob("*") if p.is_file()}
    new_files = {p.relative_to(NEW / "site").as_posix(): p for p in (NEW / "site").rglob("*") if p.is_file()}
    assert len(old_files) == 8357 and len(new_files) == 8364
    assert new_files.keys() - old_files.keys() == added and old_files.keys() <= new_files.keys()
    allowed_nav = {x["source_path"] for x in prep["navigation_restore"]["matches"]}
    allowed = set(bodies) | allowed_nav
    changed = []
    unchanged = 0
    for rel, path in old_files.items():
        equal = sha(path) == sha(new_files[rel])
        if equal:
            unchanged += 1
        else:
            assert rel in allowed, rel
            changed.append(rel)
    assert set(changed) == allowed_nav | {"info/basics/content-index.html"}
    accepted = {r["original_url"]: r["proposed_route"] for r in rows}
    nav_count = 0
    for rel in allowed_nav:
        parser = AnchorChanges(old_files[rel].read_bytes().decode("utf-8"), accepted)
        parser.feed(parser.text)
        parser.close()
        assert parser.rewritten().encode("utf-8") == new_files[rel].read_bytes(), rel
        nav_count += len(parser.edits)
    assert nav_count == 4
    body_rows = []
    suffix_count = 0
    for rel, row in bodies.items():
        raw = (ROOT / row["private_payload_path"]).read_bytes()
        data = new_files[rel].read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row["sha256"]
        assert not re.search(rb";jsessionid=", data, re.I)
        stripped, count = re.subn(rb";jsessionid=[A-Za-z0-9._-]+", b"", raw)
        suffix_count += count
        if row["entity_id"] not in {"contest-050609", "fan-site-program"}:
            assert stripped == data, row["entity_id"]
        elif row["entity_id"] == "contest-050609":
            assert b"The historical contest invited players" in data
            assert b"planned publication of the winners" in data
            assert b"The winners were announced" not in data
        else:
            assert b"mailto:" not in data.lower()
            assert b"This historical exhibit does not accept applications." in data
            assert b"ask for an application" not in data
        body_rows.append({"route": row["proposed_route"], "actual_capture_timestamp": row["actual_capture_timestamp"],
                          "original_sha256": row["sha256"], "derived_sha256": hashlib.sha256(data).hexdigest(),
                          "original_length": len(raw), "derived_length": len(data)})
    assert suffix_count == 3
    assert len(new["files"]) == 8364
    manifest_routes = set()
    for record in new["files"]:
        path = (ROOT / record["output_path"]).resolve()
        assert path.is_relative_to((NEW / "site").resolve())
        assert path.is_file() and path.stat().st_size == record["derived_length"]
        assert sha(path) == record["derived_sha256"]
        manifest_routes.add(record["route"])
    assert len(manifest_routes) == 8364
    old_records = {r["route"]: r for r in old["files"]}
    new_records = {r["route"]: r for r in new["files"]}
    for route, previous in old_records.items():
        if route == "/info/basics/content-index.html":
            continue
        current = new_records[route]
        for key in ("source_sha256", "source_length", "actual_timestamp", "source_base_url", "kind", "role"):
            assert current.get(key) == previous.get(key), (route, key)
    for alias, target in source_map["aliases"].items():
        assert new["route_aliases"][alias] == target
    for row in rows:
        assert new["origin_index"]["www.worldofwarcraft.com" + urlsplit(row["original_url"]).path] == row["proposed_route"]
    assert sha(OLD / "build-manifest.json") == FROZEN
    result = {
        "schema": "wow-root-source16-local-acceptance/v1", "accepted": True,
        "checked_utc": datetime.now(timezone.utc).isoformat(), "source_site": str((NEW / "site").relative_to(ROOT)).replace("\\", "/"),
        "source_manifest": str((NEW / "build-manifest.json").relative_to(ROOT)).replace("\\", "/"),
        "source_manifest_sha256": sha(NEW / "build-manifest.json"), "frozen_source15_manifest_sha256": FROZEN,
        "old_file_count": 8357, "new_file_count": 8364, "new_page_routes": sorted(added),
        "updated_existing_route": "/info/basics/content-index.html", "alias_only_route": "/wrath/index.xml",
        "unchanged_old_files": unchanged, "changed_old_files": sorted(changed), "navigation_anchor_changes": nav_count,
        "transient_suffixes_removed": suffix_count, "body_sources": body_rows,
        "all_manifest_object_hashes_lengths_passed": True, "old_binary_files_unchanged": True,
        "network_requests": 0, "published": False,
        "legacy_statistics_note": "Inherited Source15 aggregate counters describe the earlier derivation; current file/route counts are checked independently against the 8364-object files array.",
        "checker_sha256": sha(Path(__file__)),
    }
    out = DAY / "publication/root-source16-local-acceptance.json"
    assert not out.exists()
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"body_sources", "new_page_routes"}}, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Root byte-level acceptance of the fresh v54 export against accepted v53."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / ".scratch/pages-resources-20261022-v53"
NEW = ROOT / ".scratch/pages-resources-20261022-v54"
PREFIX = "/WOW-Encyclopedia-Deployable-Archive"
FLOOR = 11005853696
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def inventory(site: Path, doc: dict) -> dict:
    result = {}
    for row in doc["files"]:
        key = row["output_path"]
        assert key not in result and not key.startswith("/") and ".." not in Path(key).parts
        result[key] = (row["derived_sha256"], row["derived_length"])
    result["export-provenance.json"] = (sha(site / "export-provenance.json"), (site / "export-provenance.json").stat().st_size)
    return result


def normalize_rewards(text: str, target_to_route: dict[str, str]) -> str:
    reverse = {PREFIX + route: target for target, route in target_to_route.items()}
    for route, target in reverse.items():
        text = text.replace(route, "__MAPPED_ICON__" + target)
    def replace(match):
        url = match.group(0)
        wanted = parse_qs(urlsplit(url).query).get("requested", [None])[0]
        if wanted is not None:
            path = urlsplit(wanted).path
            if path.startswith(PREFIX + "/"):
                path = path[len(PREFIX):]
            if path in target_to_route:
                return "__MAPPED_ICON__" + path
        return url
    return re.sub(r'(?:/WOW-Encyclopedia-Deployable-Archive)?/__offline/missing-image\.svg\?[^\s\"\'<>]+', replace, text)


def main():
    assert shutil.disk_usage(ROOT).free >= FLOOR
    assert read(HERE / "root-v53-export-acceptance.json")["accepted"]
    assert sha(OLD / "export-provenance.json") == "669e423d9db560d7da8ee3d7fbff7db7bc64121ec4bacff6a2d7c6ad46fa6819"
    newdoc, olddoc = read(NEW / "export-provenance.json"), read(OLD / "export-provenance.json")
    old, new = inventory(OLD, olddoc), inventory(NEW, newdoc)
    files = {p.relative_to(NEW).as_posix(): p for p in NEW.rglob("*") if p.is_file()}
    assert set(files) == set(new), "actual output files differ from the declared set plus provenance"
    total = 0
    started = datetime.now(timezone.utc).isoformat()
    for i, (name, p) in enumerate(sorted(files.items()), 1):
        assert not p.is_symlink() and not (getattr(p.stat(), "st_file_attributes", 0) & 0x400), name
        digest, length = new[name]
        assert p.stat().st_size == length and sha(p) == digest, name
        total += length
        if i % 2000 == 0:
            print(json.dumps({"files_hashed": i}), flush=True)
    assert shutil.disk_usage(ROOT).free >= FLOOR
    ui = read(HERE / "integration/related-talent-ui-v54/input-map.json")
    faction = read(HERE / "integration/related-faction-icons-v54/input-map.json")
    audit = read(HERE / "faction-related-candidates/semantic-usage-audit.json")
    arrows = [e for e in ui["entries"] if e["format"] == "GIF"]
    expected_added = {e["route"].lstrip("/") for e in arrows + faction["entries"]}
    expected_added.add("__offline/related-faction-icons.json")
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
    assert not removed and set(added) == expected_added, (added, removed)
    pages = sorted({r for e in faction["entries"] for r in e["page_routes"]})
    page_paths = {r.lstrip("/") + ".html" for r in pages}
    scripts = {r["path"] for r in audit["v53_data_script_hashes"]}
    allowed = page_paths | scripts | {"__offline/pages_runtime.js", "__offline/route-map.json", "__offline/related-talent-ui.json", "export-provenance.json"}
    assert set(changed) <= allowed, sorted(set(changed) - allowed)
    for rel in page_paths:
        newtext = (NEW / rel).read_text(encoding="utf-8")
        stripped, count = re.subn(r'\n<aside id="__offline-related-faction-icons"[^>]*>.*?</aside>', "", newtext, flags=re.S)
        assert count == 1 and stripped == (OLD / rel).read_text(encoding="utf-8"), rel
    target_to_route = {e["target_route"]: e["route"] for e in faction["entries"]}
    for rel in scripts:
        assert normalize_rewards((NEW / rel).read_text(encoding="utf-8"), target_to_route) == normalize_rewards((OLD / rel).read_text(encoding="utf-8"), target_to_route), rel
    om, nm = read(OLD / "__offline/route-map.json"), read(NEW / "__offline/route-map.json")
    assert om["aliases"] == nm["aliases"]
    extra_routes = {e["route"]: PREFIX + e["route"] for e in arrows + faction["entries"]}
    extra_routes.update({e["target_route"]: PREFIX + e["route"] for e in arrows + faction["entries"]})
    extra_routes["/__offline/related-faction-icons.json"] = PREFIX + "/__offline/related-faction-icons.json"
    assert nm["routes"] == {**om["routes"], **extra_routes}
    def runtime_without_routes(p):
        text = p.read_text(encoding="utf-8")
        return re.sub(r"    var routes = \{[^\n]+\};", "    var routes = __ROUTES__;", text, count=1)
    assert runtime_without_routes(OLD / "__offline/pages_runtime.js") == runtime_without_routes(NEW / "__offline/pages_runtime.js")
    assert newdoc["related_talent_ui"]["ui_count"] == 24
    assert newdoc["related_faction_icons"]["image_count"] == 3
    assert newdoc["stats"]["related_faction_icon_notice_pages"] == 11
    assert newdoc["source_manifest_sha256"] == olddoc["source_manifest_sha256"]
    objects = [{"path": p, "sha256": new[p][0], "bytes": new[p][1]} for p in sorted(added + changed)]
    result = {
        "schema": "wow-root-v54-export-acceptance/v1", "accepted": True,
        "started_utc": started, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "local_site": NEW.relative_to(ROOT).as_posix(), "published": False,
        "actual_files": len(files), "declared_files": len(newdoc["files"]), "total_bytes": total,
        "all_actual_file_hashes_match_provenance": True,
        "prior_actual_tree_hash_check_reused": "root-v53-full-tree-comparison.json",
        "all_prior_image_bytes_retained": True, "removed": removed, "added": added, "changed": changed,
        "existing_reward_data_unchanged_except_three_image_urls": True,
        "existing_runtime_logic_unchanged_except_route_data": True,
        "export_provenance_sha256": new["export-provenance.json"][0],
        "objects": objects, "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
        "browser_acceptance_pending": True,
    }
    out = HERE / "root-v54-export-acceptance.json"
    assert not out.exists()
    out.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode())
    print(json.dumps({"accepted": True, "actual_files": len(files), "added": len(added), "changed": len(changed), "removed": 0, "objects": len(objects)}))


if __name__ == "__main__":
    main()

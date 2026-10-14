"""Recheck current gallery paths/entities; all HTTP requests stay on loopback."""
import http.client
import json
from pathlib import Path
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / ".scratch/pages-local-maintenance-20261014-v5"
PREFIX = "/WOW-Encyclopedia-Deployable-Archive/"


def jpeg(path):
    if not path.is_file():
        return False
    with path.open("rb") as handle:
        return handle.read(3) == b"\xff\xd8\xff"


def directory(text):
    return re.search(r'''addshots\(\s*["']([^"']+)["']\s*,\s*["']ss["']''', text).group(1)


def main():
    inventory = json.loads((ROOT / "research/github-pages-20261013/gallery-inventory-20261013.json").read_text(encoding="utf-8"))
    routes = json.loads((SITE / "__offline/route-map.json").read_text(encoding="utf-8"))["routes"]
    provenance = json.loads((SITE / "export-provenance.json").read_text(encoding="utf-8"))
    paths = {item["output_path"] for item in provenance["files"]}
    rows, groups, http_rows = [], {}, []
    for entry in inventory["rows"]:
        route = "/info/dungeons/zulaman-gallery.html" if entry["label"] == "Zul'Aman" else entry["route"]
        text = (SITE / route.lstrip("/")).read_text(encoding="utf-8")
        source = (ROOT / "offline/site" / route.lstrip("/")).read_text(encoding="utf-8", errors="replace")
        count = int(re.search(r"\bnumShots\s*=\s*(\d+)", text).group(1))
        current, original = directory(text), directory(source)
        assert current == PREFIX + original.lstrip("/"), route
        relative = current[len(PREFIX):]
        full = thumb = route_entries = provenance_entries = 0
        for number in range(1, count + 1):
            for suffix in (".jpg", "-thumb.jpg"):
                path = relative + "ss" + str(number) + suffix
                valid = jpeg(SITE / path)
                full += valid and suffix == ".jpg"
                thumb += valid and suffix == "-thumb.jpg"
                route_entries += ("/" + path) in routes
                provenance_entries += path in paths
        nested = SITE / relative / "thumbs"
        previews = sum(jpeg(path) for path in nested.glob("ss*-thumb.jpg")) if nested.is_dir() else 0
        row = {"label": entry["label"], "category": entry["category"], "page": route, "shots": count,
               "source_directory": original, "current_directory": current, "directory_correct": True,
               "full_jpeg": full, "same_directory_thumb_jpeg": thumb, "direct_route_entries": route_entries,
               "direct_provenance_entries": provenance_entries, "nested_preview_thumbnails": previews}
        rows.append(row)
        group = groups.setdefault(entry["category"], {"galleries": 0, "shots": 0, "full_jpeg": 0, "same_directory_thumb_jpeg": 0})
        for key, value in (("galleries", 1), ("shots", count), ("full_jpeg", full), ("same_directory_thumb_jpeg", thumb)):
            group[key] += value
    selected = [row for row in rows if row["label"] in ("Karazhan", "Black Temple", "Zul'Aman")]
    selected.append(next(row for row in rows if row["category"] == "Dungeon"))
    for row in selected:
        for relative in (row["page"].lstrip("/"), row["source_directory"].lstrip("/") + "ss1.jpg", row["source_directory"].lstrip("/") + "ss1-thumb.jpg"):
            connection = http.client.HTTPConnection("127.0.0.1", 63862, timeout=5)
            connection.request("GET", PREFIX + relative)
            response = connection.getresponse()
            body = response.read()
            http_rows.append({"gallery": row["label"], "path": relative, "status": response.status,
                              "content_type": response.getheader("Content-Type"), "jpeg_magic": body[:3] == b"\xff\xd8\xff"})
            connection.close()
    result = {"checked_utc": datetime.now(timezone.utc).isoformat(), "source_site": str(SITE.relative_to(ROOT)).replace("\\", "/"),
              "network": "loopback only; no Wayback requests", "gallery_count": len(rows),
              "declared_shots": sum(row["shots"] for row in rows), "expected_full_plus_thumb_files": sum(row["shots"] for row in rows) * 2,
              "directories_correct": len(rows), "full_jpeg": sum(row["full_jpeg"] for row in rows),
              "same_directory_thumb_jpeg": sum(row["same_directory_thumb_jpeg"] for row in rows),
              "direct_route_entries": sum(row["direct_route_entries"] for row in rows),
              "direct_provenance_entries": sum(row["direct_provenance_entries"] for row in rows),
              "nested_preview_thumbnails": sum(row["nested_preview_thumbnails"] for row in rows),
              "groups": groups, "rows": rows, "representative_http": http_rows,
              "raw_download_scope": "Existing accepted image maps and Karazhan/Fishing batch receipts reviewed; no exhaustive nested historical ZIP scan."}
    assert result["gallery_count"] == 50 and result["declared_shots"] == 1684
    assert result["full_jpeg"] == result["same_directory_thumb_jpeg"] == 0
    output = Path(__file__).with_name("gallery-route-entity-recheck.json")
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, ensure_ascii=False))


if __name__ == "__main__":
    main()

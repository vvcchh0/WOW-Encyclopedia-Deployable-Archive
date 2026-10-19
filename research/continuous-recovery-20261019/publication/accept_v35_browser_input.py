"""Check the24 real source elements after decoding the old missing markers."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
FOLDER = RUN / "integration/v35"
OUT = RUN / "publication/root-v35-browser-input-acceptance.json"
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


class OneImage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img":
            self.sources.append(dict(attrs).get("src"))


def main():
    assert not OUT.exists()
    input_path = FOLDER / "v35-native-ui-inputs-r2.json"
    assert SHA(input_path) == "bce40e2d16d86bfd0a1c90c4d57c98b94ebff3255d85bc0b60a4a0b211f15d3d"
    data = json.loads(input_path.read_bytes())
    items = json.loads((FOLDER / "v35-primary-source-map.json").read_bytes())["items"]
    assert {r["original"] for r in items} == {r["original"] for r in data["targets"]}
    assert len(items) == len(data["targets"]) == data["reference_count"] == 24
    assert data["native_toggle_ids"] == ["news10-15-07-904"]
    pages = {}
    for row in data["source_pages"]:
        path = ROOT / row["path"]
        assert SHA(path) == row["sha256"] and path.stat().st_size == row["bytes"]
        pages[path.relative_to(ROOT / ".scratch/offline-navigation-20261015-v15/site").as_posix()] = path.read_text(encoding="utf-8").splitlines()
    kinds = Counter()
    for target in data["targets"]:
        assert len(target["references"]) == target["reference_count"] == 1
        assert target["served_output_path"] == urlsplit(target["original"]).path.lstrip("/")
        ref = target["references"][0]
        actual_line = pages[ref["source_page"]][ref["line"] - 1]
        assert ref["source_line"] == actual_line.strip()
        assert ref["raw_tag"] in actual_line
        parser = OneImage()
        parser.feed(ref["raw_tag"])
        assert len(parser.sources) == 1
        source = parser.sources[0]
        if urlsplit(source).path.endswith("/missing-image.svg"):
            assert parse_qs(urlsplit(source).query)["requested"] == [target["original"]]
            assert target["display_class"] == "postContainer_static_no_toggle"
            assert not target["native_toggle_ids"] and not ref["container"]["toggle"]
            kinds["decoded_marker_static"] += 1
        else:
            assert urljoin("http://www.worldofwarcraft.com/" + ref["source_page"], source) == target["original"]
            assert target["native_toggle_ids"] == ["news10-15-07-904"]
            assert ref["source_page"] == "news/rss-10-2007.xml" and ref["line"] == 2244
            assert '<div class="news-expand" id="news10-15-07-904">' in "\n".join(pages[ref["source_page"]][2190:2244])
            kinds["direct_native_toggle"] += 1
    assert kinds == {"decoded_marker_static": 23, "direct_native_toggle": 1}
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "input_path": input_path.relative_to(ROOT).as_posix(), "input_sha256": SHA(input_path),
        "target_count": 24, "reference_count": 24, "kinds": dict(kinds),
        "network_requests": 0, "browser_executed": False,
        "acceptance_plan": "In the v35 tree, decode and show all24 exact image elements at their real news locations; expand only news10-15-07-904 using its native control. Assert dimensions, src and zero external requests. This input acceptance alone does not accept the exported site."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": True, "targets": 24, "kinds": dict(kinds)}))


if __name__ == "__main__":
    main()

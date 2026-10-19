"""Record the narrow August-news marker result; reuse accepted image UI checks."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
SITE = ROOT / ".scratch/pages-resources-20261018-v33"
OUT = RUN / "publication/root-august-2007-news-coverage.json"


def binding(path):
    data = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def main():
    assert not OUT.exists()
    page = SITE / "news/rss-08-2007.xml.html"
    provenance_path = SITE / "export-provenance.json"
    provenance = json.loads(provenance_path.read_bytes())
    assert binding(provenance_path)["sha256"] == "99ac5b0a2bc7d257b2fe3c4b18a0bb74023c3c57051be3a4f4efe20258f4c8f5"
    row = next(r for r in provenance["files"] if r["output_path"] == "news/rss-08-2007.xml.html")
    assert row["derived_sha256"] == binding(page)["sha256"] == "74797bcfab955a54f3ffd9687270124e408479a906be736b7fc33f3a2a18a4e0"
    assert row["derived_length"] == page.stat().st_size
    # Count literal references too, rather than limiting this to <img> tags.
    occurrences = len(re.findall(r"missing-image\.svg", page.read_text(encoding="utf-8")))
    assert occurrences == 0
    previous = ROOT / "research/continuous-recovery-20261018/publication/root-v33-browser-acceptance.json"
    continuation = RUN / "publication/root-v33-browser-continuation-acceptance.json"
    assert json.loads(previous.read_bytes())["accepted"]
    assert json.loads(continuation.read_bytes())["accepted"]
    result = {
        "accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "August 2007 rendered news page has no remaining missing-image.svg references; accepted v33 image-delta UI evidence is reused.",
        "missing_image_marker_occurrences": occurrences,
        "network_requests": 0,
        "new_browser_runs": 0,
        "exclusions": ["This marker count is not a fresh whole-page browser test.",
                       "Native Player Screenshot Galleries remain a separate resource set."],
        "bindings": [binding(p) for p in (page, provenance_path, previous, continuation)]
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": True, "missing_image_marker_occurrences": occurrences}))


if __name__ == "__main__":
    main()

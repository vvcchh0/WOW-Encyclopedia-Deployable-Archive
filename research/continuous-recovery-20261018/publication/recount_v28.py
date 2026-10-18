"""Count the same frozen static-text scope, separately from native galleries."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SITE = ROOT / ".scratch/pages-resources-20261018-v28"
sys.path.insert(0, str(ROOT / "research/continuous-recovery-20261016/publication"))
from accept_v23_static_metrics import scan

if __name__ == "__main__":
    path = OUT / "root-v28-static-metrics-acceptance.json"
    assert not path.exists()
    files, counter, news, markers = scan(SITE)
    actual = {"static_text_files": len(files), "unique_missing_images": len(counter),
              "missing_occurrences": sum(counter.values()), "news_unique_missing_images": len(news),
              "news_missing_occurrences": sum(news.values())}
    expected = json.loads((OUT / "v28-export-expectations.json").read_bytes())["expected_static_counts"]
    assert actual == expected, (actual, expected)
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(), "version": "v28",
              **actual, "all_placeholder_markers": markers,
              "export_provenance_sha256": hashlib.sha256((SITE / "export-provenance.json").read_bytes()).hexdigest(),
              "scope": "Same1104statictextfiles excluding_origins; native3368dynamicgallerytargets remain separate."}
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))

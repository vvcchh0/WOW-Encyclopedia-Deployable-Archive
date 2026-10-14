"""Measure static-parser differences without rewriting either site or audit."""
import importlib.util
import json
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "saved_route_auditor", Path(__file__).parent / "route-audit/audit_local_routes.py"
)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
result = {"python": sys.version, "executable": sys.executable, "sites": []}
for name in ("pages-historical-exhibits-20261014-v3", "pages-local-maintenance-20261014-v4"):
    site = ROOT / ".scratch" / name
    total = 0
    missing = 0
    requested = set()
    example = None
    for path in site.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in audit.HTML_SUFFIXES | audit.CSS_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix.casefold() in audit.CSS_SUFFIXES:
            refs, _ = audit.parse_css(text)
        else:
            parser = audit.RefParser(text, path.relative_to(site).as_posix())
            parser.feed(text)
            parser.close()
            parser.finish()
            refs = parser.refs
        total += len(refs)
        if path.relative_to(site).as_posix() == "community/stories/index.html":
            example = {"refs": len(refs), "ad_link_refs": sum("clk.atdmt" in r["raw"] for r in refs)}
        for ref in refs:
            raw = ref["raw"]
            if "/__offline/missing" in raw:
                missing += 1
                for url in parse_qs(urlsplit(raw).query).get("requested", []):
                    requested.add(url.split("#", 1)[0])
    result["sites"].append({
        "site": name,
        "static_references": total,
        "placeholder_references": missing,
        "unique_requested_urls": len(requested),
        "iframe_fallback_example": example,
    })
print(json.dumps(result, ensure_ascii=False, indent=2))

from __future__ import annotations

"""Build a sanitized, compact EU dependency summary from the local audit.

The public artifacts deliberately keep only safe source positions and hashes.
Session path parameters and sensitive query pairs are removed before writing;
CSS rows derived from local US/v17 CSS are separated as hypotheses and never
enter the observed literal candidate queue.
"""

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "eu-dependencies-audit-v1.json"
PROPOSAL = HERE / "prior10-proposal.json"
PUBLIC_SUMMARY = HERE / "eu-dependencies-public-summary-v1.json"
PUBLIC_CANDIDATES = HERE / "eu-dependencies-public-candidates-v1.json"
SCAN = HERE / "public-sensitive-scan-v1.json"

SENSITIVE_KEYS = {"jsessionid", "sessionid", "auth", "authentication", "token", "access_token", "refresh_token", "cookie", "password", "passwd", "jwt", "secret"}
PATH_SESSION_RE = re.compile(r";(?:(?:jsessionid)|(?:sessionid))=[^/?#;\s\"'<>]+", re.I)
TEXT_SESSION_RE = re.compile(r";(?:(?:jsessionid)|(?:sessionid))=[^\s\"'<>]+", re.I)
TEXT_QUERY_RE = re.compile(r"([?&])(?:jsessionid|sessionid|auth(?:entication)?|token|access_token|refresh_token|cookie|password|passwd|jwt|secret)=[^&\s\"'<>]*", re.I)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sanitize_url(value: str) -> str:
    parts = urlsplit(value)
    path = PATH_SESSION_RE.sub("", parts.path)
    safe_query = []
    for key, val in parse_qsl(parts.query, keep_blank_values=True):
        if key.lower() in SENSITIVE_KEYS:
            continue
        safe_query.append((key, val))
    return urlunsplit((parts.scheme, parts.netloc, path, urlencode(safe_query), parts.fragment))


def sanitize_text(value: str) -> str:
    value = TEXT_SESSION_RE.sub("", value)
    value = TEXT_QUERY_RE.sub(r"\1[redacted]", value)
    return value


def safe_occurrence(occ: dict) -> dict:
    out = {
        "source_page": occ.get("source_page"),
        "line": occ.get("line"),
        "column": occ.get("column"),
        "tag": occ.get("tag"),
        "attribute": occ.get("attribute"),
        "raw_literal": sanitize_url(occ.get("raw_literal", "")),
        "context": sanitize_text(occ.get("context", "")),
        "extraction": occ.get("extraction"),
        "layer": occ.get("layer"),
    }
    if occ.get("html_parent_page"):
        out["html_parent_page"] = occ["html_parent_page"]
    if occ.get("parent_css"):
        parent = occ["parent_css"]
        out["parent_css"] = {
            "local_path": parent.get("local_path"),
            "route": parent.get("route"),
            "source_sha256": parent.get("source_sha256"),
        }
    return out


def safe_resource(row: dict) -> dict:
    return {
        "resolved_url": sanitize_url(row.get("resolved_url", "")),
        "kind": row.get("kind"),
        "status": row.get("local_match", {}).get("status"),
        "scope_status": row.get("scope_status"),
        "occurrence_count": row.get("occurrence_count"),
        "occurrences": [safe_occurrence(x) for x in row.get("occurrences", [])[:2]],
    }


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    resources = {row["resolved_normalized"]: row for row in audit["resources"]}
    observed = []
    for item in proposal["items"]:
        row = resources.get(item["resolved_url"].lower()) or next((r for r in audit["resources"] if r["resolved_url"] == item["resolved_url"]), None)
        # The proposal is produced from the same audit; retaining its compact
        # source evidence avoids exposing full local provenance in public JSON.
        if row is None:
            continue
        occurrences = [o for o in row.get("occurrences", []) if o.get("layer") == "html"]
        if not occurrences:
            continue
        observed.append(
            {
                "priority": item["priority"],
                "resolved_url": sanitize_url(item["resolved_url"]),
                "kind": item["kind"],
                "status": item["status"],
                "occurrence_count": item["occurrence_count"],
                "source_evidence": [safe_occurrence(o) for o in occurrences[:2]],
                "why": item["why"],
            }
        )
    observed.sort(key=lambda x: x["priority"])
    assert len(observed) <= 10
    assert all(all(o.get("layer") != "saved_css_first_layer" for o in item["source_evidence"]) for item in observed)
    hypotheses = []
    for row in audit["resources"]:
        css_occ = [o for o in row.get("occurrences", []) if o.get("layer") == "saved_css_first_layer"]
        if css_occ:
            hypotheses.append(
                {
                    "resolved_url": sanitize_url(row["resolved_url"]),
                    "kind": row["kind"],
                    "status": row["local_match"]["status"],
                    "hypothesis_only": True,
                    "observed_in_eu_html": False,
                    "source_evidence": [safe_occurrence(o) for o in css_occ[:2]],
                }
            )
    source_hashes = {k: v for k, v in audit["input_hashes"].items() if k.endswith((".html", ".headers.txt"))}
    summary = {
        "schema": "wow-recovery.eu-dependencies-public-summary.v1",
        "source_audit": rel(AUDIT),
        "source_audit_sha256": sha256_file(AUDIT),
        "network_performed": False,
        "build_performed": False,
        "git_performed": False,
        "source_pages": [
            {
                "id": page["id"],
                "source_page": page["source_page"],
                "original_url": sanitize_url(page["original_url"]),
                "sha256": source_hashes[page["source_page"]]["sha256"],
                "bytes": source_hashes[page["source_page"]]["bytes"],
            }
            for page in audit["scope"]["pages"]
        ],
        "counts": {
            "direct_literal_occurrences": audit["direct_occurrence_count"],
            "saved_css_occurrences": audit["saved_css_occurrence_count"],
            "resource_entities": audit["resource_entity_count"],
            "status_counts": audit["status_counts"],
            "scope_status_counts": audit["scope_status_counts"],
            "kind_counts": audit["kind_counts"],
        },
        "nav_menu_finding": {
            "buildtopnav_literal_present": True,
            "menu132_literal_present": True,
            "navtree_literal_present": False,
            "literal_menu_iframe_count": 7,
            "statement": "Saved EU HTML contains buildtopnav.js, menu132_com.js, and seven literal menu iframe sources; no navtree literal was observed.",
        },
        "observed_literal_candidates": observed,
        "derived_css_hypotheses": hypotheses,
        "excluded_link_count": len(audit["excluded_business_social_download_links"]),
        "input_page_hashes": source_hashes,
        "sanitization": "session path parameters and sensitive query pairs are removed; source pages and local audit remain the complete evidence",
    }
    PUBLIC_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    public_candidates = {
        "schema": "wow-recovery.eu-dependencies-public-candidates.v1",
        "source_audit": rel(AUDIT),
        "source_audit_sha256": sha256_file(AUDIT),
        "network_performed": False,
        "candidate_count": len(observed),
        "candidates_are_observed_html_literals": True,
        "saved_css_rows_excluded_from_queue": True,
        "candidates": observed,
    }
    PUBLIC_CANDIDATES.write_text(json.dumps(public_candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    public_files = [PUBLIC_SUMMARY, PUBLIC_CANDIDATES]
    patterns = ["session_path_value", "sensitive_query_value"]
    hit_files = []
    for path in public_files:
        text = path.read_text(encoding="utf-8")
        if PATH_SESSION_RE.search(text) or TEXT_SESSION_RE.search(text) or TEXT_QUERY_RE.search(text):
            hit_files.append(rel(path))
    scan = {
        "schema": "wow-recovery.eu-dependencies-public-sensitive-scan.v1",
        "checked_files": [rel(path) for path in public_files],
        "patterns_checked": patterns,
        "hit_count": len(hit_files),
        "hit_files": hit_files,
        "passed": not hit_files,
        "source_audit_unchanged_sha256": sha256_file(AUDIT),
    }
    SCAN.write_text(json.dumps(scan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": rel(PUBLIC_SUMMARY), "candidates": rel(PUBLIC_CANDIDATES), "scan": rel(SCAN), "candidate_count": len(observed), "css_hypothesis_count": len(hypotheses), "sensitive_hit_count": len(hit_files)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

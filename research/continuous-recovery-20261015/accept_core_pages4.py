"""Validate all follow-up raw evidence and select eleven immutable sources."""
import base64
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from accept_core_pages3 import uri_identity
from accept_network_batch1 import source_status

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BATCH = OUT / "network-core-pages4"
ANCHOR = "20080512210044"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def header_value(headers, name):
    values = re.findall(r"^" + re.escape(name) + r":\s*([^\r\n]+)", headers, re.M | re.I)
    return values[-1] if values else None


def main():
    report_path = BATCH / "batch-report.json"
    report = load(report_path)
    source_map = load(BATCH / "payload-source-map.json")
    errors = []
    attempts = [a for r in report["results"] for a in r["cdx"]["attempts"] + r["replay_hops"] if a.get("executed")]
    attempts.sort(key=lambda a: a["attempt"])
    byte_count = 0
    starts = []
    for a in attempts:
        body = (BATCH / a["raw"]["body"]).read_bytes()
        headers = (BATCH / a["raw"]["headers"]).read_text(encoding="utf-8", errors="replace")
        if source_status(headers) != a["source_status"] or len(body) != a["body_bytes"] or (body and hashlib.sha256(body).hexdigest() != a["body_sha256"]):
            errors.append("raw attempt mismatch: " + str(a["attempt"]))
        if a.get("automatic_redirects") != 0:
            errors.append("automatic redirect observed")
        byte_count += len(body)
        starts.append(datetime.fromisoformat(a["started_utc"]))
    intervals = [(b-a).total_seconds() for a, b in zip(starts, starts[1:])]
    source_count = sum(a["source_status"] is not None for a in attempts)
    if len(attempts) != 15 or source_count != 14 or byte_count != report["total_body_bytes"] or min(intervals) < 1.2:
        errors.append("attempt/response/body/interval aggregate mismatch")
    if (datetime.fromisoformat(report["finished_utc"])-datetime.fromisoformat(report["started_utc"])).total_seconds() > 480 or byte_count > 67108864:
        errors.append("network time/body limit exceeded")
    if sha(OUT / "network-core-pages3/batch-report.json") != report["inputs"]["accepted_003_report_sha256"]:
        errors.append("older accepted report changed")
    payloads = []
    for entry in source_map["entries"]:
        body_path = BATCH / entry["raw_body_path"]
        headers_path = BATCH / entry["raw_headers_path"]
        body = body_path.read_bytes()
        headers = headers_path.read_text(encoding="utf-8", errors="replace")
        memento = header_value(headers, "Memento-Datetime")
        actual = parsedate_to_datetime(memento).astimezone(timezone.utc) if memento else None
        stamp = actual.strftime("%Y%m%d%H%M%S") if actual else None
        digest = base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")
        title_match = re.search(r"<title[^>]*>(.*?)</title>", body.decode("utf-8", errors="replace"), re.I | re.S)
        title = html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else None
        if source_status(headers) != 200 or actual is None or stamp > ANCHOR or actual != datetime.fromisoformat(entry["actual_memento"]):
            errors.append("source status/date mismatch: " + entry["target"])
        if stamp != entry["indexed_capture_timestamp"] or digest != entry["indexed_cdx_digest"] or sha(body_path) != entry["body_sha256"] or len(body) != entry["body_bytes"]:
            errors.append("payload/CDX digest binding mismatch: " + entry["target"])
        if uri_identity(entry["captured_original_url"]) != uri_identity(entry["query_original_url"]):
            errors.append("payload origin mismatch: " + entry["target"])
        if not title or re.search(r"\b404\b|not found|wayback machine", title, re.I):
            errors.append("possible error body: " + entry["target"])
        if entry["target"].startswith("/news/wow-news-"):
            month = int(re.search(r"wow-news-(\d{2})-2005", entry["target"]).group(1))
            expected = {6:"June",7:"July",8:"August",9:"September",10:"October",11:"November"}[month]
            if expected not in title or "2005" not in title:
                errors.append("News month/year identity mismatch: " + entry["target"])
        if entry["target"] == "/news/wow-news2005.html" and "2005" not in title:
            errors.append("annual News identity mismatch")
        if entry["target"].startswith("/burningcrusade/") and not ("Burning Crusade" in title and "Profession" in title):
            errors.append("BC professions identity mismatch")
        if entry["target"] == "/wrath/artwork.xml" and not ("Wrath" in title and b"artwork" in body.lower()):
            errors.append("Wrath artwork identity mismatch")
        value = dict(entry)
        value.update({"actual_memento": actual.isoformat() if actual else None, "actual_timestamp": stamp, "local_path": str(body_path.relative_to(ROOT)).replace("\\", "/"), "headers_local_path": str(headers_path.relative_to(ROOT)).replace("\\", "/"), "batch": "network-core-pages4", "title_independently_read": title})
        payloads.append(value)
    # Verify that the annual capture is backed by the newly fetched exact CDX.
    annual = next(r for r in report["results"] if r["target"] == "/news/wow-news2005.html")
    cdx_attempt = next(a for a in annual["cdx"]["attempts"] if a["source_status"] == 200)
    table = load(BATCH / cdx_attempt["raw"]["body"])
    rows = [dict(zip(table[0], row)) for row in table[1:] if isinstance(row, list) and len(row) == len(table[0])]
    selected = annual["selected_capture"]
    if not any(all(selected.get(k) == row.get(k) for k in ("timestamp","original","mimetype","statuscode","digest","length")) for row in rows):
        errors.append("annual selected capture absent from raw CDX")
    redirects = []
    for entry in load(BATCH / "redirect-evidence.json")["entries"]:
        evidence = []
        for name in ("raw_headers_path", "follow_raw_headers_path"):
            headers = (BATCH / entry[name]).read_text(encoding="utf-8", errors="replace")
            evidence.append({"source_status": source_status(headers), "memento_datetime": header_value(headers,"Memento-Datetime"), "location": header_value(headers,"Location"), "x_archive_orig_location": header_value(headers,"X-Archive-Orig-Location"), "assessment": "archived redirect with capture Memento" if header_value(headers,"Memento-Datetime") else "Wayback dispatcher redirect; no actual capture date"})
        redirects.append({"target": entry["target"], "hops": evidence, "html_entity_accepted": False, "alias_added": False})
    old_map = load(OUT / "network-core-pages3/payload-source-map.json")
    selected_sources = {}
    for entry in old_map["entries"]:
        value = dict(entry)
        actual = datetime.fromisoformat(value["actual_memento"]).astimezone(timezone.utc)
        value.update({"actual_memento": actual.isoformat(), "actual_timestamp": actual.strftime("%Y%m%d%H%M%S"), "local_path": str((OUT / "network-core-pages3" / value["raw_body_path"]).relative_to(ROOT)).replace("\\", "/"), "headers_local_path": str((OUT / "network-core-pages3" / value["raw_headers_path"]).relative_to(ROOT)).replace("\\", "/"), "batch": "network-core-pages3"})
        selected_sources[value["target"]] = value
    for entry in payloads:
        previous = selected_sources.get(entry["target"])
        if previous is None or datetime.fromisoformat(entry["actual_memento"]) > datetime.fromisoformat(previous["actual_memento"]):
            selected_sources[entry["target"]] = entry
    if len(payloads) != 9 or len(selected_sources) != 11:
        errors.append("nine new payloads / eleven selected source conservation failed")
    result = {"schema":"continuous-wow-core-pages4-acceptance/v1", "checked_utc":datetime.now(timezone.utc).isoformat(), "accepted":not errors, "network_requests_by_acceptance":0, "report_sha256":sha(report_path), "attempts":len(attempts), "source_responses":source_count, "total_batch_body_bytes":byte_count, "valid_payload_body_bytes":sum(x["body_bytes"] for x in payloads), "valid_entities":len(payloads), "selected_unique_sources":len(selected_sources), "payloads":payloads, "redirects":redirects, "errors":errors}
    (OUT / "core-pages4-acceptance.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if errors:
        raise SystemExit(json.dumps({"accepted":False,"errors":errors}))
    merged = {"schema":"continuous-wow-selected-core-pages/v1", "generated_utc":result["checked_utc"], "acceptance":"research/continuous-recovery-20261015/core-pages4-acceptance.json", "selection_rule":"latest validated pre-anchor actual Memento for the exact query origin; default ports normalize, bare/www and schemes remain separate", "older_raw_entities_preserved":True, "entry_count":11, "entries":list(selected_sources.values()), "excluded_redirect_only_targets":["/pvp/battlegrounds/battlegroups.html"], "ptr_source":"retained 2006 valid HTML; later 2008 redirect/login chain is not substituted"}
    (OUT / "selected-core-pages-source-map.json").write_text(json.dumps(merged,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("accepted","attempts","source_responses","total_batch_body_bytes","valid_payload_body_bytes","valid_entities","selected_unique_sources","errors")},ensure_ascii=False))


if __name__ == "__main__":
    main()

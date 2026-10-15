"""Offline raw/content acceptance of the eleven untouched monthly RSS-path targets."""
import base64
import hashlib
import html
import json
import re
from collections import Counter
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from accept_network_batch1 import source_status
from accept_core_pages3 import uri_identity
from accept_core_pages4 import header_value

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
BATCH=OUT/"network-rss10"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    report=load(BATCH/"batch-report.json")
    journal=load(BATCH/"dispatch-log.json")
    entries=load(BATCH/"rss-source-map.json")["entries"]
    prior_targets={x["target"] for x in load(OUT/"network-rss6/candidates.json")["targets"]}
    all_targets={x["target"] for x in load(OUT/"local-target-reconcile/reconciliation.json")["rows"] if x["target"].startswith("/news/rss-")}
    expected=all_targets-prior_targets
    errors=[]
    if {x["target"] for x in report["results"]}!=expected or len(expected)!=11:
        errors.append("eleven untouched exact-target selection differs")
    attempts=sorted([a for r in report["results"] for a in r["cdx"]["attempts"]+r["replay_hops"] if a.get("executed")],key=lambda a:a["attempt"])
    total,streak,max_streak=0,0,0
    for a in attempts:
        body=(BATCH/a["raw"]["body"]).read_bytes()
        headers=(BATCH/a["raw"]["headers"]).read_text(encoding="utf-8",errors="replace")
        status=source_status(headers)
        if status!=a["source_status"] or len(body)!=a["body_bytes"] or (body and hashlib.sha256(body).hexdigest()!=a["body_sha256"]):
            errors.append("raw attempt differs: "+str(a["attempt"]))
        dispatch=next(x for x in journal["dispatches"] if x["attempt"]==a["attempt"])
        if a["dispatch_monotonic"]!=dispatch["dispatch_monotonic"] or a["dispatch_utc"]!=dispatch["dispatch_utc"] or not dispatch["persisted_before_transport"]:
            errors.append("dispatch binding differs")
        if a["automatic_redirects"]!=0 or status in (429,503) or len(body)>16777216:
            errors.append("request cap/redirect/ratelimit mismatch")
        streak=streak+1 if a["transport_error"] else 0
        max_streak=max(streak,max_streak)
        total+=len(body)
    mono=[x["dispatch_monotonic"] for x in journal["dispatches"]]
    intervals=[y-x for x,y in zip(mono,mono[1:])]
    if len(attempts)!=17 or sum(a["source_status"] is not None for a in attempts)!=8 or total!=438550 or min(intervals)<1.25 or max_streak>=5:
        errors.append("attempt/HTTP/bytes/interval/failure-stop mismatch")
    if total>67108864 or (datetime.fromisoformat(report["request_window_finished_utc"])-datetime.fromisoformat(report["started_utc"])).total_seconds()>480:
        errors.append("body/window cap exceeded")
    if min(journal["disk_preflight"]["disk_free_bytes"],journal["disk_postflight"]["disk_free_bytes"])<11005853696 or not journal["postflight_persisted_in_finally"]:
        errors.append("disk/finally evidence differs")
    for item in report["inputs"]["input_digests"].values():
        if sha(ROOT/item["path"])!=item["sha256"]:
            errors.append("input changed: "+item["path"])
    if sha(ROOT/report["inputs"]["candidates"])!=report["inputs"]["candidates_sha256"]:
        errors.append("candidate changed")
    rows_by_target={}
    for r in report["results"]:
        rows=[]
        for a in r["cdx"]["attempts"]:
            if a["source_status"]==200:
                table=load(BATCH/a["raw"]["body"])
                if table:
                    rows.extend(dict(zip(table[0],row)) for row in table[1:] if isinstance(row,list) and len(row)==len(table[0]))
        if len(rows)!=r["cdx"]["capture_index_count"]:
            errors.append("raw CDX count differs")
        for row in r["cdx"]["capture_records"]:
            if not any(all(row.get(k)==x.get(k) for k in ("timestamp","original","mimetype","statuscode","digest","length")) for x in rows):
                errors.append("CDX row absent from raw")
        rows_by_target[r["target"]]=rows
    payloads=[]
    for e in entries:
        body_path,headers_path=BATCH/e["raw_body_path"],BATCH/e["raw_headers_path"]
        body=body_path.read_bytes()
        headers=headers_path.read_text(encoding="utf-8",errors="replace")
        actual=parsedate_to_datetime(header_value(headers,"Memento-Datetime")).astimezone(timezone.utc)
        stamp=actual.strftime("%Y%m%d%H%M%S")
        digest=base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")
        selected=next(r for r in report["results"] if r["target"]==e["target"])["cdx"]["selected_capture"]
        if source_status(headers)!=200 or actual!=datetime.fromisoformat(e["actual_memento"]) or stamp!=e["capture_timestamp"] or stamp>"20080512210044":
            errors.append("payload source/Memento differs")
        if sha(body_path)!=e["body_sha256"] or len(body)!=e["body_bytes"] or digest!=e["cdx_digest"] or digest!=selected["digest"] or uri_identity(e["query_original"])!=uri_identity(selected["original"]):
            errors.append("payload digest/source identity differs")
        if not any(all(selected.get(k)==row.get(k) for k in ("timestamp","original","mimetype","statuscode","digest","length")) for row in rows_by_target[e["target"]]):
            errors.append("selected row absent from raw")
        text=body.decode("utf-8")
        title_match=re.search(r"<title[^>]*>(.*?)</title>",text,re.I|re.S)
        title=html.unescape(title_match.group(1)).strip() if title_match else None
        if not title or "Archived News" not in title or re.search(r"<rss\b|<feed\b",text,re.I):
            errors.append("expanded HTML identity differs")
        month,year=map(int,re.fullmatch(r"/news/rss-(\d{2})-(\d{4})\.xml",e["target"]).groups())
        dates=re.findall(r"<span\s+class=[\"']posted-date[\"'][^>]*>\s*([^<]+)",text,re.I)
        for date in dates:
            match=re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{2})",date.strip())
            if not match or int(match.group(1))!=month or 2000+int(match.group(3))!=year:
                errors.append("actual article month differs: "+e["target"])
        if not dates:
            errors.append("actual article dates absent")
        anomaly="Original title says September2006; all34 posted-date markers are July2006" if month==7 else None
        payloads.append({"target":e["target"],"query_original_url":e["query_original"],"captured_original_url":e["captured_original_url"],"local_path":body_path.relative_to(ROOT).as_posix(),"headers_local_path":headers_path.relative_to(ROOT).as_posix(),"actual_timestamp":stamp,"actual_memento":actual.isoformat(),"body_bytes":len(body),"body_sha256":sha(body_path),"cdx_digest":digest,"mime":header_value(headers,"Content-Type"),"body_format":"expanded_html","title":title,"article_posted_date_count":len(dates),"article_posted_dates":dict(Counter(dates)),"article_month_matches_url":True,"source_title_anomaly":anomaly,"logical_url":e["query_original"],"proposed_route":e["target"],"role":"archived_news_html","source_group":"rss_path_expanded_html"})
    if len(payloads)!=3 or sum(x["body_bytes"] for x in payloads)!=428871 or sum(map(len,rows_by_target.values()))!=68:
        errors.append("three payload/bytes/68 CDX rows conservation differs")
    receipt={"schema":"continuous-wow-rss10-acceptance/v1","checked_utc":datetime.now(timezone.utc).isoformat(),"accepted":not errors,"network_requests_by_acceptance":0,"report_sha256":sha(BATCH/"batch-report.json"),"attempts":len(attempts),"source_responses":8,"failed_transport_attempts":9,"maximum_consecutive_transport_failures":max_streak,"total_batch_body_bytes":total,"valid_payload_body_bytes":sum(x["body_bytes"] for x in payloads),"valid_expanded_html":len(payloads),"raw_rss_xml":0,"raw_cdx_rows":68,"minimum_monotonic_dispatch_interval_seconds":min(intervals),"payloads":payloads,"unrecovered_targets":[{"target":r["target"],"category":r["category"],"cdx_rows":r["cdx"]["capture_index_count"]} for r in report["results"] if not r["entity_valid"]],"errors":errors}
    (OUT/"rss10-acceptance.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if errors:
        raise SystemExit(json.dumps({"accepted":False,"errors":errors}))
    (OUT/"selected-rss10-source-map.json").write_text(json.dumps({"schema":"continuous-wow-selected-rss10-expanded-html/v1","entry_count":3,"entries":payloads,"acceptance":"research/continuous-recovery-20261015/rss10-acceptance.json"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if k not in ("payloads","unrecovered_targets")},indent=2))


if __name__=="__main__":
    main()

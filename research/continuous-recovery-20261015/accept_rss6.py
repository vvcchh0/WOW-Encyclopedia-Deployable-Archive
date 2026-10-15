"""Accept immutable RSS-path payloads while retaining timing evidence limits."""
import base64
import hashlib
import html
import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from accept_network_batch1 import source_status
from accept_core_pages3 import uri_identity
from accept_core_pages4 import header_value

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BATCH = OUT / "network-rss6"
ANCHOR = "20080512210044"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = load(BATCH / "batch-report.json")
    entries = load(BATCH / "rss-source-map.json")["entries"]
    reconciliation = load(OUT / "local-target-reconcile/reconciliation.json")
    expected = sorted([r for r in reconciliation["rows"] if re.fullmatch(r"/news/rss-\d{2}-\d{4}\.xml",r["target"])],key=lambda r:(int(r["target"][13:17]),int(r["target"][10:12])),reverse=True)[:12]
    errors, timing_observations, selected = [], [], []
    if [r["target"] for r in expected] != [r["target"] for r in report["results"]]:
        errors.append("twelve newest RSS targets differ from accepted reconciliation")
    for path_key, hash_key in (("reconciliation_path","reconciliation_sha256"),("acceptance_path","acceptance_sha256")):
        if sha(ROOT/report["inputs"][path_key])!=report["inputs"][hash_key]:
            errors.append("input changed: "+path_key)
    attempts = sorted([a for r in report["results"] for a in r["cdx"]["attempts"]+r["replay_hops"] if a.get("executed")],key=lambda a:a["attempt"])
    body_sum = 0
    for a in attempts:
        body = (BATCH/a["raw"]["body"]).read_bytes()
        headers = (BATCH/a["raw"]["headers"]).read_text(encoding="utf-8",errors="replace")
        if source_status(headers)!=a["source_status"] or len(body)!=a["body_bytes"] or (body and hashlib.sha256(body).hexdigest()!=a["body_sha256"]):
            errors.append("raw attempt differs: "+str(a["attempt"]))
        if a.get("automatic_redirects")!=0 or len(body)>16777216 or a["source_status"] in (429,503):
            errors.append("raw request policy mismatch: "+str(a["attempt"]))
        body_sum+=len(body)
    for prev,current in zip(attempts,attempts[1:]):
        gap=(datetime.fromisoformat(current["started_utc"])-datetime.fromisoformat(prev["started_utc"])).total_seconds()
        if gap<1.2:
            clocks=[]
            for attempt in (prev,current):
                trace=(BATCH/attempt["raw"]["trace"]).read_text(encoding="utf-8",errors="replace")
                clocks.append(re.search(r"^(\d{2}:\d{2}:\d{2}\.\d+) ",trace,re.M).group(1))
            trace_gap=(datetime.strptime(clocks[1],"%H:%M:%S.%f")-datetime.strptime(clocks[0],"%H:%M:%S.%f")).total_seconds()%86400
            timing_observations.append({"previous_attempt":prev["attempt"],"next_attempt":current["attempt"],"observed_utc_start_interval_seconds":gap,"first_trace_local_wallclock":clocks,"observed_trace_start_interval_seconds":trace_gap,"required_seconds":1.2,"assessment":"Both saved UTC starts and curl trace wall-clock observations are below threshold; monotonic slot timestamps were not persisted. Batch timing compliance is withheld and original timestamps remain unchanged."})
    responses=sum(a["source_status"] is not None for a in attempts)
    if len(attempts)!=15 or responses!=8 or body_sum!=453544 or report["total_body_bytes"]!=body_sum:
        errors.append("aggregate attempts/HTTP/bytes mismatch")
    duration=(datetime.fromisoformat(report["request_window_finished_utc"])-datetime.fromisoformat(report["started_utc"])).total_seconds()
    if duration>480 or body_sum>67108864 or min(report["preflight"]["disk_free_bytes_before"],report["preflight"]["disk_free_bytes_after"])<11005853696:
        errors.append("window/body/disk cap mismatch")
    if report["stop_reason"]!="five_consecutive_tls_or_transport_failures" or any(a["source_status"] is not None for a in attempts[-5:]):
        errors.append("five-failure stop not evidenced")
    if sum(r["category"]=="not_requested" for r in report["results"])!=2:
        errors.append("not-requested conservation failed")
    for e in entries:
        r=next(r for r in report["results"] if r["target"]==e["target"])
        c=r["selected_capture"]
        body_path,headers_path=BATCH/e["raw_body_path"],BATCH/e["raw_headers_path"]
        body=body_path.read_bytes()
        headers=headers_path.read_text(encoding="utf-8",errors="replace")
        memento=header_value(headers,"Memento-Datetime")
        actual=parsedate_to_datetime(memento).astimezone(timezone.utc) if memento else None
        stamp=actual.strftime("%Y%m%d%H%M%S") if actual else None
        digest=base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")
        if source_status(headers)!=200 or actual is None or stamp>ANCHOR or stamp!=c["timestamp"] or actual!=datetime.fromisoformat(e["actual_memento"]):
            errors.append("source/date mismatch: "+e["target"])
        if len(body)!=e["body_bytes"] or sha(body_path)!=e["body_sha256"] or digest!=e["cdx_digest"] or digest!=c["digest"]:
            errors.append("payload/CDX digest mismatch: "+e["target"])
        if uri_identity(e["query_original"])!=uri_identity(e["captured_original"]) or uri_identity(c["original"])!=uri_identity(e["query_original"]):
            errors.append("exact source identity mismatch: "+e["target"])
        raw_rows=[]
        for a in r["cdx"]["attempts"]:
            if a["source_status"]==200:
                table=load(BATCH/a["raw"]["body"])
                raw_rows.extend(dict(zip(table[0],row)) for row in table[1:] if isinstance(row,list) and len(row)==len(table[0]))
        if not any(all(c.get(k)==row.get(k) for k in ("timestamp","original","mimetype","statuscode","digest","length")) for row in raw_rows):
            errors.append("selected row absent from raw CDX: "+e["target"])
        text=body.decode("utf-8")
        title_match=re.search(r"<title[^>]*>(.*?)</title>",text,re.I|re.S)
        title=html.unescape(re.sub(r"\s+"," ",title_match.group(1)).strip()) if title_match else None
        if not re.search(r"<(?:!doctype\s+html|html)\b",text,re.I) or not title or re.search(r"<rss\b|<feed\b",text,re.I) or "Archived News" not in title:
            errors.append("HTML body classification/identity mismatch: "+e["target"])
        dates=re.findall(r"<span\s+class=[\"']posted-date[\"'][^>]*>\s*([^<]+)",text,re.I)
        expected_month,expected_year=map(int,re.fullmatch(r"/news/rss-(\d{2})-(\d{4})\.xml",e["target"]).groups())
        for date in dates:
            match=re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{2})",date.strip())
            if not match or int(match.group(1))!=expected_month or 2000+int(match.group(3))!=expected_year:
                errors.append("article posted-date month differs: "+e["target"])
        if not dates:
            errors.append("article posted-date evidence absent: "+e["target"])
        declared_title_month={1:"January",2:"February",3:"March",4:"April"}[expected_month]
        title_matches=declared_title_month in title and str(expected_year) in title
        item={"target":e["target"],"query_original_url":e["query_original"],"captured_original_url":e["captured_original"],"local_path":body_path.relative_to(ROOT).as_posix(),"headers_local_path":headers_path.relative_to(ROOT).as_posix(),"actual_timestamp":stamp,"actual_memento":actual.isoformat() if actual else None,"body_bytes":len(body),"body_sha256":sha(body_path),"cdx_digest":digest,"mime":header_value(headers,"Content-Type"),"body_format":"expanded_html","title":title,"url_declared_month":expected_month,"url_declared_year":expected_year,"title_month_matches_url":title_matches,"article_posted_date_count":len(dates),"article_posted_dates":dict(Counter(dates)),"article_month_matches_url":True,"original_raw_rss_recovered":False,"source_anomaly":"original April path retains March title; all posted-date markers are April 2008" if not title_matches else None,"integration_status":"held separate from active v9; root decision required"}
        selected.append(item)
    if len(selected)!=4 or sum(e["body_bytes"] for e in selected)!=452039:
        errors.append("four payload count/bytes mismatch")
    next_control=(datetime.fromisoformat(report["request_window_finished_utc"])+timedelta(minutes=15)).isoformat()
    result={"schema":"continuous-wow-rss6-acceptance/v1","checked_utc":datetime.now(timezone.utc).isoformat(),"accepted":not errors,"acceptance_scope":"payload authenticity and saved evidence; batch timing conformity is separately withheld","payloads_accepted":not errors,"batch_policy_accepted":False,"network_requests_by_acceptance":0,"report_sha256":sha(BATCH/"batch-report.json"),"source_map_sha256":sha(BATCH/"rss-source-map.json"),"attempts":len(attempts),"source_responses":responses,"total_batch_body_bytes":body_sum,"valid_payload_body_bytes":sum(x["body_bytes"] for x in selected),"valid_expanded_html":len(selected),"original_raw_rss":0,"timing_observations":timing_observations,"control_not_before_utc":next_control,"stop_reason":report["stop_reason"],"payloads":selected,"errors":errors}
    (OUT/"rss6-acceptance.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if errors:
        raise SystemExit(json.dumps({"accepted":False,"errors":errors}))
    source_map={"schema":"continuous-wow-selected-rss-path-html/v1","generated_utc":result["checked_utc"],"acceptance":"research/continuous-recovery-20261015/rss6-acceptance.json","entry_count":4,"raw_rss_count":0,"expanded_html_count":4,"entries":selected,"integration":"separate next layer; do not mutate currently building v9"}
    (OUT/"selected-rss6-source-map.json").write_text(json.dumps(source_map,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("accepted","payloads_accepted","batch_policy_accepted","attempts","source_responses","total_batch_body_bytes","valid_payload_body_bytes","valid_expanded_html","original_raw_rss","timing_observations","errors")}))


if __name__=="__main__":
    main()

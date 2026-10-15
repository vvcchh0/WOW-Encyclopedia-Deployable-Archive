"""Offline acceptance of the query-specific historical Wrath viewer acquisition."""
import base64
import hashlib
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from accept_network_batch1 import source_status
from accept_core_pages3 import uri_identity
from accept_core_pages4 import header_value

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
BATCH=OUT/"network-wrath8"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    report=load(BATCH/"batch-report.json")
    journal=load(BATCH/"dispatch-log.json")
    source_map=load(BATCH/"payload-source-map.json")
    errors=[]
    attempts=sorted([a for r in report["results"] for a in r["cdx"]["attempts"]+r["replay_hops"] if a.get("executed")],key=lambda a:a["attempt"])
    total=0
    for a in attempts:
        body=(BATCH/a["raw"]["body"]).read_bytes()
        headers=(BATCH/a["raw"]["headers"]).read_text(encoding="utf-8",errors="replace")
        if source_status(headers)!=a["source_status"] or len(body)!=a["body_bytes"] or (body and hashlib.sha256(body).hexdigest()!=a["body_sha256"]):
            errors.append("raw attempt mismatch: "+str(a["attempt"]))
        if a["automatic_redirects"]!=0 or a["source_status"] in (429,503) or len(body)>16777216:
            errors.append("request policy mismatch: "+str(a["attempt"]))
        dispatch=next(x for x in journal["dispatches"] if x["attempt"]==a["attempt"])
        if a["dispatch_monotonic"]!=dispatch["dispatch_monotonic"] or a["dispatch_utc"]!=dispatch["dispatch_utc"] or not dispatch["persisted_before_transport"]:
            errors.append("journal binding mismatch")
        total+=len(body)
    mono=[x["dispatch_monotonic"] for x in journal["dispatches"]]
    intervals=[y-x for x,y in zip(mono,mono[1:])]
    if len(attempts)!=15 or sum(x["source_status"] is not None for x in attempts)!=12 or total!=11269 or min(intervals)<1.25:
        errors.append("attempt/status/bytes/spacing aggregate mismatch")
    if len(report["results"])!=13 or total>67108864 or (datetime.fromisoformat(report["request_window_finished_utc"])-datetime.fromisoformat(report["started_utc"])).total_seconds()>480:
        errors.append("target/body/window cap mismatch")
    if min(journal["disk_preflight"]["disk_free_bytes"],journal["disk_postflight"]["disk_free_bytes"])<11005853696:
        errors.append("disk floor mismatch")
    for item in report["inputs"]["input_digests"].values():
        if sha(ROOT/item["path"])!=item["sha256"]:
            errors.append("input hash changed: "+item["path"])
    if sha(ROOT/report["inputs"]["candidates"])!=report["inputs"]["candidates_sha256"]:
        errors.append("candidate hash changed")
    row_count=0
    for r in report["results"]:
        rows=[]
        for a in r["cdx"]["attempts"]:
            if a["source_status"]==200:
                table=load(BATCH/a["raw"]["body"])
                if table:
                    rows.extend(dict(zip(table[0],row)) for row in table[1:] if isinstance(row,list) and len(row)==len(table[0]))
        row_count+=len(rows)
        if len(rows)!=r["cdx"]["capture_index_count"]:
            errors.append("CDX row count mismatch: "+r["target_key"])
        for row in r["cdx"]["capture_records"]:
            if not any(all(row.get(k)==x.get(k) for k in ("timestamp","original","mimetype","statuscode","digest","length")) for x in rows):
                errors.append("CDX row absent from raw")
        if r["category"]=="cdx_empty_in_range" and rows:
            errors.append("false empty CDX category")
    e=source_map["entries"][0]
    body_path,headers_path=BATCH/e["raw_body_path"],BATCH/e["raw_headers_path"]
    body=body_path.read_bytes()
    headers=headers_path.read_text(encoding="utf-8",errors="replace")
    actual=parsedate_to_datetime(header_value(headers,"Memento-Datetime")).astimezone(timezone.utc)
    stamp=actual.strftime("%Y%m%d%H%M%S")
    digest=base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")
    if source_status(headers)!=200 or stamp!="20080219075509" or stamp!=e["indexed_capture_timestamp"] or actual!=datetime.fromisoformat(e["actual_memento"]) or stamp>"20080512210044":
        errors.append("viewer actual capture mismatch")
    if len(body)!=10622 or len(body)!=e["body_bytes"] or sha(body_path)!=e["body_sha256"] or digest!=e["indexed_cdx_digest"] or uri_identity(e["query_original_url"])!=uri_identity(e["captured_original_url"]):
        errors.append("viewer hash/CDX/source identity mismatch")
    raw_cdx=next(r for r in report["results"] if r["target_key"]==e["target"])["cdx"]
    selected=raw_cdx["selected_capture"]
    if selected["timestamp"]!=stamp or selected["digest"]!=digest or selected["original"]!=e["captured_original_url"]:
        errors.append("viewer selected row differs")
    text=body.decode("utf-8")
    required=("World of Warcraft: Wrath of the Lich King",'id="Screenie"','id="Screenie2"',"nextScreen()","prevScreen()",'id="dCurrent"','id="dTotal"','id="screenLink"',"./js/screeniesimplified.js")
    if not all(token in text for token in required) or re.search(r"<title[^>]*>[^<]*(?:404|not found|wayback machine)",text,re.I):
        errors.append("viewer source identity/API markup differs")
    dependencies=[{"url":"http://www.worldofwarcraft.com/wrath/js/screeniesimplified.js","purpose":"viewer query/image/control implementation","source_reference":"./js/screeniesimplified.js"},{"url":"http://www.worldofwarcraft.com/wrath/images/layout/pixel.gif","purpose":"1x1 layout and 40x58 previous/next transparent clickable images","source_reference":"./images/layout/pixel.gif"}]
    receipt={"schema":"continuous-wow-wrath8-acceptance/v1","checked_utc":datetime.now(timezone.utc).isoformat(),"accepted":not errors,"network_requests_by_acceptance":0,"report_sha256":sha(BATCH/"batch-report.json"),"dispatch_log_sha256":sha(BATCH/"dispatch-log.json"),"attempts":len(attempts),"source_responses":sum(x["source_status"] is not None for x in attempts),"total_batch_body_bytes":total,"valid_payload_body_bytes":len(body),"valid_html":1,"valid_images":0,"raw_cdx_rows":row_count,"minimum_monotonic_dispatch_interval_seconds":min(intervals),"categories":report["category_counts"],"source_accepted":{"query_original_url":e["query_original_url"],"captured_original_url":e["captured_original_url"],"local_path":body_path.relative_to(ROOT).as_posix(),"headers_local_path":headers_path.relative_to(ROOT).as_posix(),"actual_memento":actual.isoformat(),"actual_timestamp":stamp,"body_bytes":len(body),"body_sha256":sha(body_path),"cdx_digest":digest,"mime":header_value(headers,"Content-Type")},"new_literal_dependencies":dependencies,"canonical_base_alias_approved":False,"canonical_base_alias_reason":"Only query-specific capture recovered; generic query-handling script must be validated before generalizing this source to other s values.","scripts_executed":False,"errors":errors}
    (OUT/"wrath8-acceptance.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if k not in ("source_accepted","new_literal_dependencies")},indent=2))
    if errors:
        raise SystemExit(1)


if __name__=="__main__":
    main()

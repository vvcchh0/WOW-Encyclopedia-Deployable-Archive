"""Independently verify NET009 raw evidence and static viewer API; no script execution."""
import base64
import hashlib
import io
import json
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from PIL import Image
from accept_network_batch1 import source_status
from accept_core_pages3 import uri_identity
from accept_core_pages4 import header_value

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
BATCH=OUT/"network-mixed9"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report=load(BATCH/"batch-report.json")
    journal=load(BATCH/"dispatch-log.json")
    entries=load(BATCH/"payload-source-map.json")["entries"]
    errors=[]
    attempts=sorted([a for r in report["results"] for a in r["cdx"]["attempts"]+r["replay_hops"] if a.get("executed")],key=lambda a:a["attempt"])
    total=0
    for a in attempts:
        body=(BATCH/a["raw"]["body"]).read_bytes()
        headers=(BATCH/a["raw"]["headers"]).read_text(encoding="utf-8",errors="replace")
        if source_status(headers)!=a["source_status"] or len(body)!=a["body_bytes"] or (body and hashlib.sha256(body).hexdigest()!=a["body_sha256"]):
            errors.append("raw attempt mismatch: "+str(a["attempt"]))
        dispatch=next(x for x in journal["dispatches"] if x["attempt"]==a["attempt"])
        if a["dispatch_monotonic"]!=dispatch["dispatch_monotonic"] or a["dispatch_utc"]!=dispatch["dispatch_utc"] or not dispatch["persisted_before_transport"]:
            errors.append("dispatch journal differs")
        if a["automatic_redirects"]!=0 or a["source_status"] in (429,503) or len(body)>16777216:
            errors.append("request policy mismatch")
        total+=len(body)
    intervals=[y["dispatch_monotonic"]-x["dispatch_monotonic"] for x,y in zip(journal["dispatches"],journal["dispatches"][1:])]
    if len(attempts)!=14 or sum(a["source_status"] is not None for a in attempts)!=12 or total!=8938 or min(intervals)<1.25:
        errors.append("aggregate attempt/HTTP/bytes/interval mismatch")
    if min(journal["disk_preflight"]["disk_free_bytes"],journal["disk_postflight"]["disk_free_bytes"])<11005853696 or not journal["postflight_persisted_in_finally"]:
        errors.append("disk/finally evidence mismatch")
    if (datetime.fromisoformat(report["request_window_finished_utc"])-datetime.fromisoformat(report["started_utc"])).total_seconds()>480 or total>67108864 or len(report["results"])>12:
        errors.append("batch cap exceeded")
    for item in report["inputs"]["input_digests"].values():
        if sha(ROOT/item["path"])!=item["sha256"]:
            errors.append("input changed: "+item["path"])
    if sha(ROOT/report["inputs"]["candidates"])!=report["inputs"]["candidates_sha256"]:
        errors.append("candidate changed")
    row_count=0
    for result in report["results"]:
        rows=[]
        for a in result["cdx"]["attempts"]:
            if a["source_status"]==200:
                table=load(BATCH/a["raw"]["body"])
                if table:
                    rows.extend(dict(zip(table[0],row)) for row in table[1:] if isinstance(row,list) and len(row)==len(table[0]))
        row_count+=len(rows)
        if len(rows)!=result["cdx"]["capture_index_count"]:
            errors.append("raw CDX count differs")
        for row in result["cdx"]["capture_records"]:
            if not any(all(row.get(k)==x.get(k) for k in ("timestamp","original","mimetype","statuscode","digest","length")) for x in rows):
                errors.append("reported CDX row missing from raw")
        if result["category"]=="cdx_empty_in_window" and rows:
            errors.append("false empty CDX classification")
    payloads=[]
    for e in entries:
        path=BATCH/e["raw_body_path"]
        body=path.read_bytes()
        hp=BATCH/e["raw_headers_path"]
        headers=hp.read_text(encoding="utf-8",errors="replace")
        actual=parsedate_to_datetime(header_value(headers,"Memento-Datetime")).astimezone(timezone.utc)
        stamp=actual.strftime("%Y%m%d%H%M%S")
        digest=base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")
        row=next(x for x in report["results"] if x["target_key"]==e["target"])["cdx"]["selected_capture"]
        if source_status(headers)!=200 or stamp!=e["indexed_capture_timestamp"] or stamp!=row["timestamp"] or actual!=datetime.fromisoformat(e["actual_memento"]) or stamp>"20080512210044":
            errors.append("payload source/Memento/window differs")
        if len(body)!=e["body_bytes"] or sha(path)!=e["body_sha256"] or digest!=e["indexed_cdx_digest"] or digest!=row["digest"] or uri_identity(e["query_original_url"])!=uri_identity(row["original"]):
            errors.append("payload digest/origin binding differs")
        decoded={}
        if e["target"]=="screeniesimplified-js":
            text=body.decode("utf-8")
            tokens=('function loadCheckForShot()', 'window.location.href.split("s=")','eval(checkForSpecifiedShot[1])','omegaLightBox(nowViewing-1)','shotList[i] = theDirectory+"ss"+(theShot)+".jpg"','if (i == screenshotsCommonTotal)','theDirectory = theLocDirectory','function prevScreen()', 'function nextScreen()')
            if not all(x in text for x in tokens) or text.count('eval(checkForSpecifiedShot[1])')!=1 or "javascript" not in header_value(headers,"Content-Type").lower():
                errors.append("static generic viewer API/fragment differs")
            decoded={"generic_query_driven_viewer_proven":True,"query_fragment_count":1,"original_eval_present":True,"scripts_executed":False,"common_then_locale_list_builder":True,"one_based_omega_entry":True,"additional_high_resolution_template":'dirList[nowViewing] + "ss" + hiResList[nowViewing] + "-hires.jpg"',"derived_parser_required_before_export":True}
        else:
            with Image.open(io.BytesIO(body)) as img:
                img.verify()
            with Image.open(io.BytesIO(body)) as img:
                img.load()
                decoded={"format":img.format,"width":img.width,"height":img.height,"verify_and_load":True,"resource_purpose":"layout_decoration"}
            if len(body)!=43 or decoded["format"]!="GIF" or (decoded["width"],decoded["height"])!=(1,1):
                errors.append("pixel decode differs")
        payloads.append({"target":e["target"],"query_original_url":e["query_original_url"],"captured_original_url":e["captured_original_url"],"local_path":path.relative_to(ROOT).as_posix(),"headers_local_path":hp.relative_to(ROOT).as_posix(),"actual_timestamp":stamp,"actual_memento":actual.isoformat(),"body_bytes":len(body),"body_sha256":sha(path),"cdx_digest":digest,"mime":header_value(headers,"Content-Type"),"temporal_status":"preanchor","entity_class":e["entity_class"],"independent_content_check":decoded})
    if len(payloads)!=2 or row_count!=2 or sum(x["body_bytes"] for x in payloads)!=8475:
        errors.append("two payload/row/bytes conservation failed")
    receipt={"schema":"continuous-wow-mixed9-acceptance/v1","checked_utc":datetime.now(timezone.utc).isoformat(),"accepted":not errors,"network_requests_by_acceptance":0,"report_sha256":sha(BATCH/"batch-report.json"),"attempts":len(attempts),"source_responses":sum(a["source_status"] is not None for a in attempts),"total_batch_body_bytes":total,"valid_payload_body_bytes":sum(x["body_bytes"] for x in payloads),"valid_viewer_scripts":1,"valid_layout_decoration_images":1,"valid_content_images":0,"valid_late_temporal_supplements":0,"raw_cdx_rows":row_count,"minimum_monotonic_dispatch_interval_seconds":min(intervals),"categories":report["category_counts"],"payloads":payloads,"viewer_canonical_source_mapping_supported":True,"viewer_export_condition":"Exact source route script must receive approved single-positive-safe-integer s parser; invalid/out-of-range defaults1; original raw remains unchanged.","errors":errors}
    (OUT/"mixed9-acceptance.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if k!="payloads"},indent=2))
    if errors:
        raise SystemExit(1)


if __name__=="__main__":
    main()

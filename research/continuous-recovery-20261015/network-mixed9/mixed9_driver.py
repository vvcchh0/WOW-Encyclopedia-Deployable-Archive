"""Small NET-MIXED-009 adapter over the accepted wrath8/core3 transport."""
from __future__ import annotations
import argparse, hashlib, importlib.util, io, json, re, shutil, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
try:
    from PIL import Image
except Exception:
    Image = None

ROOT = Path(__file__).resolve().parents[3]
OUT, RAW = Path(__file__).resolve().parent, Path(__file__).resolve().parent / "raw"
W8 = ROOT / "research/continuous-recovery-20261015/network-wrath8/wrath8.py"
ACCEPT = ROOT / "research/continuous-recovery-20261015/wrath8-acceptance.json"
W8C = ROOT / "research/continuous-recovery-20261015/network-wrath8/candidates.json"
W8R = ROOT / "research/continuous-recovery-20261015/network-wrath8/batch-report.json"
VIEWER = ROOT / "research/continuous-recovery-20261015/network-wrath8/raw/05-viewer-fallback-s1-replay-proxy.body"
LAYOUT = ROOT / ".scratch/offline-navigation-20261015-v9/site/wrath/js/thumbnailslayout.js"
CORE = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
PRE = {"name":"preanchor","from":"20040101000000","to":"20080512210044","temporal_status":"preanchor"}
LATE = {"name":"late","from":"20080513000000","to":"20101231235959","temporal_status":"temporal_supplement"}
UA, PROXY = "wow-recovery-mixed9/20261015", "http://127.0.0.1:7890"
INTERVAL, MAX_TARGETS, MAX_ATTEMPTS, WINDOW = 1.25, 12, 32, 480
MIN_FREE, MAX_TOTAL, MAX_ENTITY = 11_005_853_696, 64*1024*1024, 16*1024*1024
STOP, REDIRECT = {429,503}, {301,302,303,307,308}

def load(p: Path, n: str):
    s=importlib.util.spec_from_file_location(n,p)
    if not s or not s.loader: raise RuntimeError(f"cannot load {p}")
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
w8=load(W8,"mixed9_w8"); core=w8.core; gate_mod=w8.gate_mod
w8.OUT=OUT; w8.RAW=RAW; core.OUT=OUT; core.RAW=RAW; core.USER_AGENT=UA; core.MIN_INTERVAL_SECONDS=0.0; gate_mod.INTERVAL_SECONDS=INTERVAL

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return w8.sha(p)
def read(p): return w8.read(p)
def write(p,v): return w8.write(p,v)
def free(): return int(shutil.disk_usage(OUT).free)
def body(a): return w8.body(a)
def dig(p): return {"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p),"bytes":p.stat().st_size}
def b32(raw): return w8.b32_sha1(raw)

def rows():
    base="http://www.worldofwarcraft.com/wrath/"; out=[
      {"rank":1,"target_key":"screeniesimplified-js","kind":"javascript","url":base+"js/screeniesimplified.js","window":PRE,"select":"latest_valid_200_or_wayback_redirect","entity_class":"viewer_control_script"},
      {"rank":2,"target_key":"pixel-layout","kind":"layout_image","url":base+"images/layout/pixel.gif","window":PRE,"select":"latest_valid_200_or_wayback_redirect","entity_class":"layout_decoration"},
      {"rank":3,"target_key":"border-layout","kind":"layout_image","url":base+"images/layout/ssborder1.png","window":LATE,"select":"earliest_same_origin_status_200","entity_class":"layout_decoration"}]
    rank=4
    for n,win in [(4,PRE),(11,LATE),(10,LATE),(8,LATE)]:
        for suffix in ("-thumb",""):
            out.append({"rank":rank,"target_key":f"gallery-ss{n}{suffix}","kind":"content_image","url":f"{base}images/artwork/ss{n}{suffix}.jpg","window":win,"select":"earliest_same_origin_status_200" if win is LATE else "latest_valid_200_or_wayback_redirect","entity_class":"content_image","gallery_number":n,"gallery_suffix":suffix or "original"})
            rank+=1
    return out

def cdx(url,win):
    q=[("url",url),("from",win["from"]),("to",win["to"]),("output","json"),("fl",",".join(core.CDX_COLUMNS)),("limit",str(core.CDX_LIMIT)),("collapse","digest"),("matchType","exact")]
    return "https://web.archive.org/cdx/search/cdx?"+urlencode(q)

def evidence():
    a=read(ACCEPT); r=read(W8R); viewer=VIEWER.read_text(encoding="utf-8",errors="replace").splitlines(); layout=LAYOUT.read_text(encoding="utf-8",errors="replace").splitlines()
    proof={x["target_key"]:{"category":x.get("category"),"cdx_source_status":(x.get("cdx") or {}).get("source_status"),"capture_index_count":(x.get("cdx") or {}).get("capture_index_count"),"valid_capture_count":(x.get("cdx") or {}).get("valid_capture_count"),"final_source_status":x.get("final_source_status")} for x in r.get("results",[]) if x.get("target_key") in {"border-layout","gallery-ss11-thumb","gallery-ss11","gallery-ss10-thumb","gallery-ss10","gallery-ss8-thumb","gallery-ss8"}}
    return {"wrath8_acceptance":{"path":str(ACCEPT.relative_to(ROOT)).replace("\\","/"),"sha256":sha(ACCEPT),"accepted":a.get("accepted"),"report_sha256":a.get("report_sha256")},"viewer_source":{"path":str(VIEWER.relative_to(ROOT)).replace("\\","/"),"sha256":sha(VIEWER),"bytes":VIEWER.stat().st_size,"actual_memento":a.get("source_accepted",{}).get("actual_memento"),"literal_dependencies":{"screeniesimplified":{"line":151,"text":viewer[150]},"pixel":{"line":160,"text":viewer[159]},"prev_next_screenie":{"lines":[167,168,178,185]}},"scripts_executed":False},"layout_source":{"path":str(LAYOUT.relative_to(ROOT)).replace("\\","/"),"sha256":sha(LAYOUT),"line":4,"text":layout[3]},"prior_net_wrath8_proof":{"report_path":str(W8R.relative_to(ROOT)).replace("\\","/"),"report_sha256":sha(W8R),"preanchor_empty_or_prior_proof":proof}}

def candidates():
    ev=evidence(); paths=[ACCEPT,W8C,W8R,VIEWER,LAYOUT,CORE,GATE]; es=[]
    for x in rows():
        y=dict(x); y["query_original_url"]=x["url"]; y["cdx_query_url"]=cdx(x["url"],x["window"]); y["evidence_ref"]="batch_evidence"; y["no_script_execution"]=True; y["same_origin_policy"]="same scheme/lowercase host; only default ports normalize; bare/www and http/https remain separate; path/query literal"; es.append(y)
    return {"schema":"continuous-wow-network-mixed9-candidates/v1","batch_id":"NET-MIXED-009","generated_utc":now(),"network_requests":0,"target_count":len(es),"entries":es,"evidence":ev,"windows":{"preanchor":PRE,"late":LATE},"selection":{"preanchor":"latest valid same-origin status-200-or-Wayback-redirect","late":"earliest valid same-origin status-200; no late query for JS/pixel","late_temporal_supplement":True},"input_digests":{str(p.relative_to(ROOT)).replace("\\","/"):dig(p) for p in paths},"policy":{"direct_first":True,"proxy":PROXY,"direct_connect_timeout_seconds":4,"direct_total_timeout_seconds":12,"proxy_connect_timeout_seconds":8,"proxy_total_timeout_seconds":20,"max_distinct_targets":MAX_TARGETS,"max_attempts":MAX_ATTEMPTS,"window_seconds":WINDOW,"minimum_dispatch_interval_seconds":INTERVAL,"minimum_free_bytes":MIN_FREE,"max_total_body_bytes":MAX_TOTAL,"max_entity_body_bytes":MAX_ENTITY,"automatic_redirects":0,"manual_redirect_follow_hops":0,"stop_http_codes":sorted(STOP),"tls_verification":"enabled_by_curl_default","concurrent_source_requests":1,"cdx_index_and_payload_separate":True},"late_policy":"Late captures are independent temporal supplements and cannot replace pre-anchor sources."}

def prepare():
    OUT.mkdir(parents=True,exist_ok=True); RAW.mkdir(parents=True,exist_ok=True); c=candidates(); write(OUT/"candidates.json",c); cs=sha(OUT/"candidates.json"); write(OUT/"config.json",{"schema":"continuous-wow-network-mixed9-config/v1","batch_id":"NET-MIXED-009","candidate_sha256":cs,"candidate_path":"research/continuous-recovery-20261015/network-mixed9/candidates.json","transport_helper":str(CORE.relative_to(ROOT)).replace("\\","/"),"dispatch_gate_helper":str(GATE.relative_to(ROOT)).replace("\\","/"),"network_requests":0,"policy":c["policy"],"windows":{"preanchor":PRE,"late":LATE}}); d=free(); write(OUT/"plan.json",{"schema":"continuous-wow-network-mixed9-plan/v1","batch_id":"NET-MIXED-009","mode":"plan_only","prepared_utc":now(),"candidate_sha256":cs,"disk_free_bytes":d,"minimum_free_bytes":MIN_FREE,"network_requests":0,"ready":d>=MIN_FREE,"target_order":[x["target_key"] for x in c["entries"]],"windows":{"preanchor":PRE,"late":LATE}}); print(json.dumps({"mode":"plan_only","network_requests":0,"target_count":len(c["entries"]),"candidate_sha256":cs,"disk_free_bytes":d},ensure_ascii=False)); return 0

def eligible(records,target,win):
    allowed={200}|REDIRECT if win["name"]=="preanchor" else {200}; out=[]
    for i,r in enumerate(records):
        v=dict(r); ts=r.get("timestamp",""); st=int(r["statuscode"]) if r.get("statuscode","").isdigit() else None; match=core.original_match_kind(r.get("original",""),target); inside=bool(re.fullmatch(r"\d{14}",ts) and win["from"]<=ts<=win["to"]); v.update(record_index=i,statuscode_int=st,within_query_range=inside,original_match_kind=match,exact_original_match=match=="exact"); v["valid_replay_candidate"]=bool(inside and match is not None and st in allowed and core.parse_timestamp(ts)); out += [v] if v["valid_replay_candidate"] else []
    return out

def select(rs,win):
    if not rs:return None
    return sorted(rs,key=lambda x:(x["timestamp"],1 if x.get("statuscode_int")==200 else 0),reverse=win["name"]=="preanchor")[0]

def request(url,transport,kind,key,state,gate,started):
    ok,why=w8.dispatch_ok(state,started)
    if not ok:return {"executed":False,"attempt":state.attempts+1,"kind":kind,"target_key":key,"transport":transport,"url":url,"unrequested_reason":why or "limit_before_request"}
    return w8.request(url,transport,kind,key,state,gate,started)

def metric(a,c):
    raw=body(a); exp=str(c.get("digest") or "").upper() or None; calc=b32(raw)
    return {"body_bytes":len(raw),"body_sha256":hashlib.sha256(raw).hexdigest() if raw else None,"cdx_digest_expected":exp,"cdx_digest_calculated":calc,"cdx_digest_match":bool(exp and calc and exp==calc),"cdx_length":int(c["length"]) if str(c.get("length","")).isdigit() else None,"actual_memento":a.get("memento_datetime"),"content_type":a.get("content_type"),"source_status":a.get("source_status"),"raw_body_path":(a.get("raw") or {}).get("body"),"raw_headers_path":(a.get("raw") or {}).get("headers"),"raw_trace_path":(a.get("raw") or {}).get("trace")}

def js_observe(raw,ctype):
    text=raw.decode("utf-8",errors="replace"); low=text.lower(); mime=(ctype or "").lower().split(";",1)[0].strip(); html=mime in {"text/html","application/xhtml+xml"} or low.lstrip().startswith(("<!doctype html","<html","<head")); m={"query_s_parsing":bool(re.search(r"location\.(?:search|href)|[?&]s[=\\'\"]|(?:get|parse).*s",text,re.I)),"image_directory_file_concat":bool(re.search(r"(?:directory|images|screenie|jpg|jpeg|gif|png).{0,100}(?:\+|concat|src)",text,re.I|re.S)),"prevScreen":bool(re.search(r"prevScreen",text,re.I)),"nextScreen":bool(re.search(r"nextScreen",text,re.I)),"Screenie_api":bool(re.search(r"Screenie",text))}; deps=sorted(set(re.findall(r"(?:\./|/)[A-Za-z0-9_./-]+\.(?:js|gif|jpg|jpeg|png|xml)",text,re.I))); symbols=sorted(set(re.findall(r"\b(?:theDirectory|theLocDirectory|screenshotsTotal|screenshotsCommonTotal|shotList|dirList|hiResList|screenImage|nextShot|prevShot|Image|Screenie|screenLink)\b",text))); return {"content_type":ctype,"mime":mime,"html_like":html,"text_bytes":len(raw),"scripts_executed":False,"markers":m,"marker_count":sum(m.values()),"direct_dependencies":deps[:100],"dynamic_dependency_symbols":symbols,"meaningful_non_html_script":bool(text.strip()) and not html}

def classify(item,replay,capture):
    if not replay or not replay.get("executed"):return "not_requested",{"reason":(replay or {}).get("unrequested_reason","replay_not_requested"),"selected_capture":capture},None
    st=replay.get("source_status"); raw=body(replay)
    if replay.get("transport_error"):return "network_unknown",{"reason":replay.get("transport_reason") or "curl_or_tls_failure","source_status":st,"selected_capture":capture},None
    if st in STOP:return "rate_limited",{"source_status":st,"retry_after":replay.get("retry_after"),"selected_capture":capture},None
    if st==404:return "not_archived",{"reason":"replay_http_404","source_status":st,"selected_capture":capture},None
    if st in REDIRECT:return "redirect_unfollowed",{"reason":"manual_redirect_follow_hops_zero","source_status":st,"location":replay.get("location"),"selected_capture":capture},None
    if st!=200:return "http_response",{"source_status":st,"selected_capture":capture},None
    if not replay.get("memento_datetime"):return "invalid_payload",{"reason":"missing_actual_memento_header","selected_capture":capture},None
    v=metric(replay,capture or {}); v["temporal_status"]="temporal_supplement" if item["window"]["name"]=="late" else "preanchor"
    if not raw:return "soft404",{"reason":"empty_body","validation":v,"selected_capture":capture},None
    if not v["cdx_digest_match"]:return "invalid_payload",{"reason":"cdx_digest_mismatch","validation":v,"selected_capture":capture},None
    if item["kind"]=="javascript":
        obs=js_observe(raw,replay.get("content_type")); v["static_observation"]=obs
        if obs["html_like"]:return "soft404",{"reason":"html_or_wayback_body_not_javascript","validation":v,"selected_capture":capture},None
        if not obs["meaningful_non_html_script"] or not obs["marker_count"]:return "invalid_script",{"reason":"no_meaningful_static_markers","validation":v,"selected_capture":capture},None
        return ("valid_js_temporal_supplement" if item["window"]["name"]=="late" else "valid_js"),v,v
    ok,dec,reason=w8.image_validation(raw); v["decode"]=dec; expected="GIF" if item["url"].endswith("pixel.gif") else "PNG" if item["url"].endswith("ssborder1.png") else "JPEG"; v["expected_format"]=expected; v["entity_class"]=item["entity_class"]
    if not ok:return "invalid_image",{"reason":reason,"validation":v,"selected_capture":capture},None
    if dec.get("format")!=expected:return "invalid_image",{"reason":f"expected_{expected}","validation":v,"selected_capture":capture},None
    cat="valid_image_temporal_supplement" if item["window"]["name"]=="late" else "valid_image"; return cat,v,v

def public(a): return w8.public_attempt(a)

def result(item,qs,sel,rps):
    q=qs[-1] if qs else None; rp=rps[-1] if rps else None; records=(q or {}).get("cdx_records") or []; valid=(q or {}).get("cdx_valid_records") or []
    if not q or not q.get("executed"): cat,detail,val="not_requested",{"reason":(q or {}).get("unrequested_reason","query_not_requested")},None
    elif q.get("transport_error"): cat,detail,val="network_unknown",{"reason":q.get("transport_reason") or "query_transport_error","source_status":q.get("source_status")},None
    elif q.get("source_status") in STOP: cat,detail,val="rate_limited",{"source_status":q.get("source_status"),"retry_after":q.get("retry_after")},None
    elif not q.get("cdx_parse_valid"): cat,detail,val="cdx_invalid",{"reason":q.get("cdx_parse_error") or "cdx_parse_failed"},None
    elif sel is None: cat,detail,val=("cdx_empty_in_window" if not records else "cdx_no_valid_capture"),{"reason":"no same-origin eligible capture in requested time window","capture_index_count":len(records),"permanent_unarchived_claim":False},None
    elif not rp or not rp.get("executed"): cat,detail,val="not_requested",{"reason":(rp or {}).get("unrequested_reason","replay_not_requested"),"selected_capture":sel},None
    else: cat,detail,val=classify(item,rp,sel)
    raw=body(rp); return {"candidate_rank":item["rank"],"target_key":item["target_key"],"kind":item["kind"],"entity_class":item["entity_class"],"window":item["window"]["name"],"temporal_status":item["window"]["temporal_status"],"query_original_url":item["url"],"category":cat,"detail":detail,"validation":val,"cdx":{"query_url":item["cdx_query_url"],"attempts":[public(x) for x in qs],"source_status":q.get("source_status") if q else None,"source_response_count":sum(x.get("source_status") is not None for x in qs),"capture_index_count":len(records),"valid_capture_count":len(valid),"capture_records":records,"selected_capture":sel},"replay_source_response_count":sum(x.get("source_status") is not None for x in rps),"replay_hops":[public(x) for x in rps],"actual_memento_or_null":rp.get("memento_datetime") if rp and rp.get("executed") else None,"final_source_status":rp.get("source_status") if rp else None,"final_content_type":rp.get("content_type") if rp else None,"final_body_bytes":len(raw) if rp else 0,"final_body_sha256":hashlib.sha256(raw).hexdigest() if raw else None,"unrequested_reason":None if cat.startswith("valid_") else detail.get("reason")}

def one(item,transport,state,gate,started):
    q=request(item["cdx_query_url"],transport,"cdx",item["target_key"],state,gate,started); qs=[q]; sel=None; rps=[]
    if q.get("executed"):
        val=eligible(q.get("cdx_records") or [],item["url"],item["window"]); q["cdx_valid_records"]=val; q["cdx_capture_index_count"]=len(q.get("cdx_records") or []); q["cdx_valid_capture_count"]=len(val); sel=select(val,item["window"])
        if sel is not None and not state.stop_reason:rps.append(request(core.replay_url(sel),transport,"replay",item["target_key"],state,gate,started))
    return result(item,qs,sel,rps),transport

def smap(x):
    rp=(x.get("replay_hops") or [])[-1]; cap=(x["cdx"].get("selected_capture") or {}); v=x.get("validation") or {}
    return {"target":x["target_key"],"query_original_url":x["query_original_url"],"window":x["window"],"temporal_status":x["temporal_status"],"entity_class":x["entity_class"],"actual_memento":x["actual_memento_or_null"],"source_status":x["final_source_status"],"content_type":x["final_content_type"],"body_bytes":x["final_body_bytes"],"body_sha256":x["final_body_sha256"],"raw_body_path":(rp.get("raw") or {}).get("body"),"raw_headers_path":(rp.get("raw") or {}).get("headers"),"captured_original_url":cap.get("original"),"indexed_capture_timestamp":cap.get("timestamp"),"indexed_statuscode":cap.get("statuscode"),"indexed_cdx_digest":cap.get("digest"),"indexed_cdx_length":cap.get("length"),"cdx_digest_calculated":v.get("cdx_digest_calculated"),"cdx_digest_match":v.get("cdx_digest_match"),"validation":v,"action":"review temporal/source mapping before integration; entity remains only in this batch raw directory"}

def outputs(cands,results,state,start,finish,update,d0,d1,transport,gate):
    counts={}
    for x in results:counts[x["category"]]=counts.get(x["category"],0)+1
    good={"valid_js","valid_js_temporal_supplement","valid_image","valid_image_temporal_supplement"}; ents=[smap(x) for x in results if x["category"] in good]; ints=[x["interval_since_previous_dispatch_seconds"] for x in gate.dispatches if x.get("interval_since_previous_dispatch_seconds") is not None]
    report={"schema":"continuous-wow-network-mixed9-batch-report/v1","batch_id":"NET-MIXED-009","mode":"executed","started_utc":start,"finished_utc":finish,"request_window_finished_utc":finish,"report_updated_utc":update,"inputs":{"candidates":"research/continuous-recovery-20261015/network-mixed9/candidates.json","candidates_sha256":sha(OUT/"candidates.json"),"input_digests":cands["input_digests"]},"policy":cands["policy"],"preflight":{"drive":"D:","disk_free_bytes_before":d0,"disk_free_bytes_after":d1,"minimum_free_bytes":MIN_FREE},"transport":{"confirmed_transport_after_first_request":transport,"curl":str(core.CURL),"helper":str(CORE.relative_to(ROOT)).replace("\\","/"),"dispatch_gate":str(GATE.relative_to(ROOT)).replace("\\","/")},"distinct_target_count":len(results),"target_count":len(results),"max_distinct_targets":MAX_TARGETS,"preanchor_target_count":sum(x["window"]=="preanchor" for x in results),"late_target_count":sum(x["window"]=="late" for x in results),"category_counts":counts,"capture_index_count":sum(x["cdx"]["capture_index_count"] for x in results),"valid_capture_count":sum(x["cdx"]["valid_capture_count"] for x in results),"valid_entity_count":len(ents),"late_temporal_supplement_count":sum(x["category"] in {"valid_js_temporal_supplement","valid_image_temporal_supplement"} for x in results),"cdx_source_response_count":sum(x["cdx"]["source_response_count"] for x in results),"replay_source_response_count":sum(x["replay_source_response_count"] for x in results),"source_request_count":state.attempts,"transport_attempt_count":state.attempts,"failed_attempt_count":state.failed_attempts,"source_response_count":state.source_responses,"total_body_bytes":state.total_body_bytes,"dispatch_count":len(gate.dispatches),"dispatch_min_interval_observed_seconds":min(ints) if ints else None,"stop_reason":state.stop_reason,"stop_detail":state.stop_detail,"rate_limit":state.rate_limit,"results":results,"raw_evidence_note":"Raw headers, traces, stderr and bodies remain below this batch raw directory. Zero-byte transport bodies are local placeholders, CONNECT 200 is excluded, CDX length is index metadata, and late valid entities are temporal supplements."}
    write(OUT/"batch-report.json",report); targets=[{"candidate_rank":x["candidate_rank"],"target_key":x["target_key"],"kind":x["kind"],"window":x["window"],"temporal_status":x["temporal_status"],"query_original_url":x["query_original_url"],"category":x["category"],"cdx_source_status":x["cdx"]["source_status"],"replay_source_status":x["final_source_status"],"actual_memento_or_null":x["actual_memento_or_null"],"body_bytes":x["final_body_bytes"],"body_sha256":x["final_body_sha256"],"capture_index_count":x["cdx"]["capture_index_count"],"valid_capture_count":x["cdx"]["valid_capture_count"],"selected_capture_timestamp":(x["cdx"]["selected_capture"] or {}).get("timestamp"),"unrequested_reason":x["unrequested_reason"],"validation":x["validation"]} for x in results]
    summary={"schema":"continuous-wow-network-mixed9-sanitized-summary/v1","batch_id":"NET-MIXED-009","mode":"executed","report_sha256":sha(OUT/"batch-report.json"),"started_utc":start,"finished_utc":finish,"request_window_finished_utc":finish,"report_updated_utc":update,"network_requests":state.attempts,"source_response_count":state.source_responses,"failed_attempt_count":state.failed_attempts,"target_count":len(results),"max_distinct_targets":MAX_TARGETS,"capture_index_count":report["capture_index_count"],"valid_capture_count":report["valid_capture_count"],"valid_entity_count":len(ents),"late_temporal_supplement_count":report["late_temporal_supplement_count"],"category_counts":counts,"total_body_bytes":state.total_body_bytes,"disk_free_bytes_before":d0,"disk_free_bytes_after":d1,"dispatch_count":len(gate.dispatches),"dispatch_min_interval_observed_seconds":report["dispatch_min_interval_observed_seconds"],"stop_reason":state.stop_reason,"targets":targets,"raw_evidence_note":report["raw_evidence_note"]}; write(OUT/"sanitized-summary.json",summary)
    md=["# NET-MIXED-009 sanitized summary","",f"- Requests: `{state.attempts}`; source responses: `{state.source_responses}`; valid entities: `{len(ents)}`.",f"- CDX rows: `{report['capture_index_count']}`; late supplements: `{report['late_temporal_supplement_count']}`.",f"- Dispatch minimum interval: `{report['dispatch_min_interval_observed_seconds']}` seconds; stop: `{state.stop_reason or 'completed'}`.","","| Target | Window | Category | Memento | Bytes | SHA-256 |","|---|---|---|---|---:|---|"]+[f"| `{x['target_key']}` | `{x['window']}` | `{x['category']}` | `{x['actual_memento_or_null'] or ''}` | `{x['body_bytes']}` | `{x['body_sha256'] or ''}` |" for x in targets]+["",report["raw_evidence_note"]]; (OUT/"sanitized-summary.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    write(OUT/"payload-source-map.json",{"schema":"continuous-wow-network-mixed9-payload-source-map/v1","generated_utc":update,"only_real_valid_entities":True,"entries":ents}); red=[]
    for x in results:
        for h in x.get("replay_hops") or []:
            if h.get("source_status") in REDIRECT:red.append({"target_key":x["target_key"],"window":x["window"],"selected_capture":x["cdx"]["selected_capture"],"source_status":h.get("source_status"),"location":h.get("location"),"manual_followed":False})
    write(OUT/"redirect-evidence.json",{"schema":"continuous-wow-network-mixed9-redirect-evidence/v1","generated_utc":update,"manual_redirect_follow_hops":0,"entries":red})

def execute():
    OUT.mkdir(parents=True,exist_ok=True); RAW.mkdir(parents=True,exist_ok=True)
    if not (OUT/"candidates.json").exists():prepare()
    c=read(OUT/"candidates.json")
    if c.get("network_requests")!=0 or len(c.get("entries") or [])!=11:raise RuntimeError("unexpected 11-target plan")
    d0=free()
    if d0<MIN_FREE:raise RuntimeError("disk free below threshold")
    start=now(); mono=time.monotonic(); state=core.RunState(mono); journal={"schema":"continuous-wow-network-mixed9-dispatch-log/v1","batch_id":"NET-MIXED-009","simulation":False,"policy":{"minimum_dispatch_interval_seconds":INTERVAL,"manual_redirect_follow_hops":0,"max_attempts":MAX_ATTEMPTS,"network_window_seconds":WINDOW},"disk_preflight":{"checked_utc":now(),"disk_free_bytes":d0,"minimum_free_bytes":MIN_FREE},"dispatches":[]}; gate=gate_mod.GateState(datetime.now(timezone.utc)-timedelta(seconds=1),journal_path=OUT/"dispatch-log.json",journal=journal); gate.persist(); results=[]; transport="direct"
    try:
        first=c["entries"][0]; q=request(first["cdx_query_url"],"direct","cdx",first["target_key"],state,gate,mono); qs=[q];
        if q.get("executed") and q.get("transport_error") and not state.stop_reason:q2=request(first["cdx_query_url"],"proxy","cdx",first["target_key"],state,gate,mono); qs.append(q2); q=q2; transport="proxy"
        elif q.get("executed") and not q.get("transport_error"):transport="direct"
        val=eligible(q.get("cdx_records") or [],first["url"],first["window"]) if q.get("executed") else []; q["cdx_valid_records"]=val; q["cdx_capture_index_count"]=len(q.get("cdx_records") or []); q["cdx_valid_capture_count"]=len(val); sel=select(val,first["window"]); rps=[request(core.replay_url(sel),transport,"replay",first["target_key"],state,gate,mono)] if sel is not None and not state.stop_reason else []; results.append(result(first,qs,sel,rps))
        for item in c["entries"][1:]:
            x,transport=one(item,transport if transport in {"direct","proxy"} else "proxy",state,gate,mono); results.append(x)
        finish=now(); update=now(); outputs(c,results,state,start,finish,update,d0,free(),transport,gate); print(json.dumps({"batch_id":"NET-MIXED-009","targets_reported":len(results),"attempts":state.attempts,"source_responses":state.source_responses,"failed_attempts":state.failed_attempts,"capture_index_count":sum(x["cdx"]["capture_index_count"] for x in results),"valid_entities":sum(x["category"].startswith("valid_") for x in results),"category_counts":{k:sum(x["category"]==k for x in results) for k in sorted({x["category"] for x in results})},"stop_reason":state.stop_reason,"confirmed_transport":transport,"network_requests":state.attempts},ensure_ascii=False)); return 0
    finally: gate_mod.persist_postflight(gate,state.attempts,free_fn=free)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--prepare",action="store_true"); p.add_argument("--execute",action="store_true"); a=p.parse_args()
    if a.prepare==a.execute:p.error("choose exactly one")
    return prepare() if a.prepare else execute()
if __name__=="__main__":raise SystemExit(main())

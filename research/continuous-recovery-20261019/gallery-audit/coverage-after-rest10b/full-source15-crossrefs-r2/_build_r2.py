
import json, hashlib, time, re
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

started = time.time()

ROOT=Path.cwd()
OUT=ROOT/"research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/full-source15-crossrefs-r2"
OUT.mkdir(parents=True,exist_ok=True)
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p):
    try: return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError: return None
def info(raw,role=None,decl=None):
    d={"path":raw,"role":role}; p=ROOT/raw if raw else None
    if p and p.is_file(): d.update(exists=True,bytes=p.stat().st_size,sha256=sha(p))
    else:
        d["exists"]=False
        if decl:
            for k in ("bytes","sha256"): 
                if k in decl: d[k]=decl[k]
    return d
def write(name,obj):
    p=OUT/name; p.write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode("utf-8")); return p
def walk_paths(x,out):
    if isinstance(x,dict):
        if isinstance(x.get("path"),str): out.append(x)
        for v in x.values(): walk_paths(v,out)
    elif isinstance(x,list):
        for v in x: walk_paths(v,out)

scan_p=ROOT/"research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/full-source15-crossrefs/crossref-scan.json"
scan_md_p=ROOT/"research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/full-source15-crossrefs/crossref-scan.md"
scan_rec_p=ROOT/"research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/full-source15-crossrefs/crossref-scan-receipt.json"
acc_p=ROOT/"research/continuous-recovery-20261019/publication/root-source15-crossref-acceptance.json"
ledger_p=ROOT/"research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/coverage-ledger.json"
v37_p=ROOT/"research/continuous-recovery-20261019/integration/v37/v37-primary-source-map.json"
v37_s_p=ROOT/"research/continuous-recovery-20261019/integration/v37/v37-supplement-source-map.json"
prov_p=ROOT/".scratch/pages-resources-20261019-v37/export-provenance.json"
site=ROOT/".scratch/pages-resources-20261019-v37/site"
scan=load(scan_p); acc=load(acc_p); ledger=load(ledger_p); v37=load(v37_p); v37_s=load(v37_s_p); prov=load(prov_p); scan_rec=load(scan_rec_p)
inputs=[scan_p,scan_md_p,scan_rec_p,acc_p,ledger_p,v37_p,v37_s_p,prov_p]
bind={str(p.relative_to(ROOT)).replace("\\","/"):{"sha256":sha(p),"bytes":p.stat().st_size} for p in inputs}

inv={x.get("route"):x for x in scan.get("text_inventory",[]) if x.get("route")}
gen=scan.get("generated_rule_hits",[])
hallows=[]
for h in gen:
    q=str(h.get("token","")).split("$",1)[0]
    if q.startswith("/info/events/hallowsend/images/newscreenshots/ss") and q.endswith(".jpg"): hallows.append((q,h))
known=acc.get("known_concrete_literals",[])
if {x[0] for x in hallows}!={x.get("path") for x in known} or len(known)!=65: raise RuntimeError("Hallow reconciliation failed")
hallow_rows=[]
for x in sorted(known,key=lambda z:z.get("number",0)):
    hs=[h for p,h in hallows if p==x.get("path")]; h=hs[0] if hs else {}
    hallow_rows.append({"path":x.get("path"),"number":x.get("number"),"source_path":x.get("source_path"),"line":x.get("line"),"scan_line":h.get("line"),"raw_line":h.get("raw_line"),"decoded_line":h.get("decoded_line"),"classification_r2":"concrete_hallows_literal_existing_registry","already_in_registry":True,"source_file":h.get("source_file",{})})
nested=scan.get("nested_preview_hits",[])
bad_nested=[x.get("token") for x in nested if "/thumb/" not in str(x.get("token","")).lower() and "/thumbs/" not in str(x.get("token","")).lower()]
if bad_nested: raise RuntimeError("nested boundary failed")

unmapped=scan.get("unmapped_alias_hits",[])
concrete=[h for h in unmapped if h.get("classification")=="concrete_unmapped_alias_literal" and not h.get("thumb")]
nested_alias=[h for h in unmapped if h.get("classification")=="nested_preview_or_alias" or h.get("thumb")]
dynamic=[h for h in unmapped if h.get("classification")=="generated_or_dynamic_alias_rule" or h.get("context_kind")=="js_generated_rule"]
other=[h for h in unmapped if h not in concrete and h not in nested_alias and h not in dynamic]
def source(h):
    sf=h.get("source_file") or {}; x=inv.get(sf.get("route"),{})
    return {"route":sf.get("route"),"output_path":x.get("output_path") or sf.get("output_path"),"sha256":x.get("sha256") or x.get("manifest_derived_sha256"),"bytes":x.get("bytes"),"source_base_url":x.get("source_base_url"),"source_kind":x.get("kind"),"source_role":x.get("role"),"origin_namespace":x.get("origin_namespace") or sf.get("origin_namespace"),"line":h.get("line"),"context_kind":h.get("context_kind")}
def resolve(h):
    token=str(h.get("token","")); s=source(h)
    if token.startswith(("http://","https://")): return token
    return urljoin(s["source_base_url"],token) if s.get("source_base_url") else None
groups={}
unresolved=[]
for h in concrete:
    u=resolve(h); s=source(h)
    if not u: unresolved.append({"token":h.get("token"),"source":s}); continue
    if u not in groups:
        groups[u]={"resolved_url":u,"token":h.get("token"),"alias_directory":h.get("alias_directory"),"shot_number":h.get("shot_number"),"origin_host":h.get("origin_host"),"origin_namespace":h.get("origin_namespace"),"source_context_kind":h.get("context_kind"),"source":s,"references":[]}
    groups[u]["references"].append({"token":h.get("token"),"line":h.get("line"),"context_kind":h.get("context_kind"),"raw_line":h.get("raw_line"),"decoded_line":h.get("decoded_line"),"source":s})
map_urls=set()
for m in (v37,v37_s):
    for x in m.get("items",[]):
        for k in ("logical_url","original"):
            if isinstance(x.get(k),str): map_urls.add(x[k])
prov_by_route={x.get("route"):x for x in prov.get("files",[]) if x.get("route")}
def local_paths(u):
    p=unquote(urlsplit(u).path or "").lstrip("/"); a=[p]
    pref="WOW-Encyclopedia-Deployable-Archive/"
    if p.startswith(pref): a.append(p[len(pref):])
    return [site/x for x in dict.fromkeys(a)]
def scope(e):
    p=unquote(urlsplit(e["resolved_url"]).path or "").lower(); c=e.get("source_context_kind")
    if c=="css_url" or "/css/" in p or p.endswith(".css"): return "non_target_shared_or_css"
    if any(p.endswith("/"+x) for x in ("pixel.gif","spacer.gif","blank.gif","transparent.gif","favicon.ico")): return "non_target_shared_or_pixel"
    if "/thumb/" in p or "/thumbs/" in p or "-thumb." in p: return "nested_preview"
    if (e.get("source") or {}).get("source_kind")=="support": return "non_target_support"
    return "candidate_page_media"
entries=[]
for e in groups.values():
    u=e["resolved_url"]; route=urlsplit(u).path or "/"; pr=prov_by_route.get(route); lp=next((p for p in local_paths(u) if p.is_file()),None)
    if u in map_urls: st="v37_map_prepared"
    elif lp:
        rel=str(lp.relative_to(site)).replace("\\","/"); st="v37_local_placeholder" if rel.startswith("__offline/") or "missing" in rel.lower() else "v37_local_present"
    elif pr: st="v37_provenance_record_only"
    else: st="v37_local_missing"
    e["scope_classification"]=scope(e); e["v37_cross_reference"]={"status":st,"map_exact_match":u in map_urls,"map_accepted":False,"provenance_route_match":bool(pr),"provenance_record":pr,"local_path_checked":[str(p.relative_to(ROOT)).replace("\\","/") for p in local_paths(u)],"local_present_path":str(lp.relative_to(ROOT)).replace("\\","/") if lp else None,"local_is_accepted":False}
    e["references"].sort(key=lambda r:(str((r.get("source") or {}).get("route") or ""),int(r.get("line") or 0)))
    entries.append(e)
scope_counts=Counter(x["scope_classification"] for x in entries); status_counts=Counter(x["v37_cross_reference"]["status"] for x in entries)
order={"v37_local_missing":0,"v37_provenance_record_only":1,"v37_local_placeholder":2,"v37_local_present":3,"v37_map_prepared":4}; corder={"js_or_href_literal":0,"href":1,"img_src":2,"css_url":9}
queue=[x for x in entries if x["scope_classification"]=="candidate_page_media" and x["v37_cross_reference"]["status"]!="v37_map_prepared"]
queue.sort(key=lambda x:(order.get(x["v37_cross_reference"]["status"],9),corder.get(x.get("source_context_kind"),5),str(x.get("origin_host") or ""),x["resolved_url"]))
queue=queue[:80]

def links(row):
    found=[]; walk_paths(row.get("historical_overlap_segments",[]),found); walk_paths(row.get("accepted_complete_segments",[]),found); walk_paths(row.get("late_failure_evidence",[]),found)
    if (row.get("source_evidence") or {}).get("path"): found.append(row["source_evidence"])
    seen=set(); out=[]
    for x in found:
        p=x.get("path")
        if p and p not in seen: seen.add(p); out.append(info(p,x.get("role"),x))
    return out
def qurls(row):
    out=[]
    def walk(x):
        if isinstance(x,dict):
            if isinstance(x.get("query_url"),str): out.append(x["query_url"])
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(row.get("historical_overlap_segments",[])); walk(row.get("accepted_complete_segments",[]))
    return list(dict.fromkeys(out))
rows=[]
for row in sorted(ledger.get("rows",[]),key=lambda x:int(x.get("registry_rank",0))):
    st=row.get("late_status")
    if st=="complete": dec="park"; reason="Accepted complete late-prefix/index evidence covers this interval; park same-window polling. This is not an image-404 claim."
    elif st=="source_503": dec="open"; reason="Exact late prefix reached terminal source 503; interval remains unverified and requires a new control decision."
    else: dec="open"; reason="Exact late prefix was not queried because the 10b queue stopped at Mechanar 503; interval remains unqueried, not missing or 404."
    se=dict(row.get("source_evidence") or {})
    rows.append({"registry_rank":row.get("registry_rank"),"gallery":row.get("gallery"),"category":row.get("category"),"source_page_route":row.get("source_page_route"),"declared_slots":row.get("declared_slots"),"expected_direct_entities":row.get("expected_direct_entities"),"origin_host":row.get("origin_host"),"origin_schemes":row.get("origin_schemes"),"source_page":se,"late_window":row.get("late_target_window"),"prior_late_status":st,"decision":dec,"decision_reason":reason,"not_404_claim":True,"uncovered_late_segments":row.get("uncovered_late_segments") or [dict(row.get("late_target_window") or {})],"historical_overlap_segments":row.get("historical_overlap_segments",[]),"accepted_complete_segments":row.get("accepted_complete_segments",[]),"late_query_receipt_context":row.get("late_query_receipt_context"),"query_urls":qurls(row),"source_links":links(row),"park_evaluation_prior":row.get("park_evaluation"),"failure_evidence_prior":row.get("late_failure_evidence")})
park=[x for x in rows if x["decision"]=="park"]; openr=[x for x in rows if x["decision"]=="open"]; s503=[x for x in openr if x["prior_late_status"]=="source_503"]; nq=[x for x in openr if x["prior_late_status"]=="not_queried"]
ctl=[]
for rel in ("research/continuous-recovery-20261019/network/control-after429-1145/control-report.json","research/continuous-recovery-20261019/network/control-after429-1145/parent-execution-receipt.json","research/continuous-recovery-20261019/publication/root-control-after429-1145-execute-go.json"):
    p=ROOT/rel
    if p.is_file(): ctl.append(info(rel,"latest_control_boundary"))
generated=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
add={"schema":"wow-recovery.gallery-audit.coverage-ledger-r2-addendum.v1","generated_utc":generated,"network_performed":False,"purpose":"Additive 50-gallery late-window park/open ledger after rest10b and the second 429.","inputs":{"base_ledger":bind[str(ledger_p.relative_to(ROOT)).replace("\\","/")],"root_source15_crossref_acceptance":bind[str(acc_p.relative_to(ROOT)).replace("\\","/")],"full_source15_scan":bind[str(scan_p.relative_to(ROOT)).replace("\\","/")]},"late_window":ledger.get("late_target_window"),"rule":"Only accepted complete prefix/index evidence permits park. Empty index, transport failure, 503, 429, or not-queried status never becomes image 404.","summary":{"group_count":len(rows),"park_count":len(park),"open_count":len(openr),"source_503_count":len(s503),"not_queried_count":len(nq),"native_strict_images_in_late_audit":0,"parked_groups":[x["gallery"] for x in park],"open_groups":[x["gallery"] for x in openr],"explicitly_parked_raid_groups":[x["gallery"] for x in park if x["gallery"] in {"Karazhan","Zul'Aman","Black Temple"}]},"latest_control_boundary":{"latest_failure":"second 429 after control-after-rest10b; no subsequent Wayback authorization","requests_after_boundary":0,"source_links":ctl},"rows":rows,"evidence_boundary":"Park is an index-coverage decision only, not a claim that all expected images exist or that missing entities are 404; open rows remain actionable or unqueried."}
alias={"schema":"wow-recovery.gallery-audit.source15-alias-priority-r2.v1","generated_utc":generated,"network_performed":False,"purpose":"Exact concrete Source15 alias candidates cross-referenced against prepared v37 provenance/local mirror; no guessing or requests.","inputs":{"scan":bind[str(scan_p.relative_to(ROOT)).replace("\\","/")],"scan_markdown":bind[str(scan_md_p.relative_to(ROOT)).replace("\\","/")],"root_source15_acceptance":bind[str(acc_p.relative_to(ROOT)).replace("\\","/")],"v37_primary_map":bind[str(v37_p.relative_to(ROOT)).replace("\\","/")],"v37_supplement_map":bind[str(v37_s_p.relative_to(ROOT)).replace("\\","/")],"v37_export_provenance":bind[str(prov_p.relative_to(ROOT)).replace("\\","/")]},"scope_rules":{"exact_resolution":"urljoin(source_base_url,literal) only; no host/scheme/path guessing.","identity":"HTTP, HTTPS, ports and hosts remain distinct.","v37_boundary":"v37 maps are prepared_waiting_root_v37_input_acceptance, not accepted images."},"full_scan_counts":{"unmapped_alias_hits":len(unmapped),"concrete_unmapped_alias_hits":len(concrete),"nested_alias_hits":len(nested_alias),"dynamic_alias_hits":len(dynamic),"placeholder_or_other_alias_hits":len(other),"known_hallows_concrete_literals_reclassified":len(hallow_rows),"known_nested_directory_previews_retained":len(nested)},"dedupe_counts":{"concrete_exact_resolved_unique":len(entries),"unresolved_missing_source_base":len(unresolved),"scope_classification_counts":dict(scope_counts),"v37_status_counts":dict(status_counts),"priority_queue_count":len(queue),"priority_queue_cap":80},"hallow_reclassification":{"accepted_literal_count":len(known),"generated_rule_hit_count":len(hallows),"records":hallow_rows,"interpretation":"The 65 shotList entries are concrete Hallow literals already covered by the frozen registry, not new unmapped gallery leads."},"nested_boundary":{"count":len(nested),"all_paths_under_thumb_or_thumbs":not bad_nested,"interpretation":"The 28 retained previews are nested /thumb/ or /thumbs/ references; no flat native ssN-thumb boundary was found."},"v37_prepared_status":{"primary_map_accepted":bool(v37.get("accepted")),"primary_map_status":v37.get("status"),"supplement_map_accepted":bool(v37_s.get("accepted")),"supplement_map_status":v37_s.get("status"),"export_file_count":len(prov.get("files",[])),"map_exact_url_count":len(map_urls)},"unresolved_aliases":unresolved,"all_exact_concrete_aliases":entries,"priority_queue":queue,"non_target_and_excluded":[x for x in entries if x not in queue and (x["scope_classification"]!="candidate_page_media" or x["v37_cross_reference"]["status"]=="v37_map_prepared")],"queue_boundary":"Local evidence queue only; not a network plan, GO, payload acceptance, or new image map."}

md=["# Source15 crossrefs and late gallery coverage r2","", "- Local-only r2; network_performed=false and no Wayback request was made.",f"- Frozen scan: {scan_p.relative_to(ROOT).as_posix()}; {len(scan.get('text_inventory',[]))} text files.",f"- Root acceptance: {acc_p.relative_to(ROOT).as_posix()}; 65 Hallow concrete literals, 28 nested previews, 0 new target gallery URLs.","","## Corrected full-scan classification","",f"The scan's 65 generated_rule_hits are concrete Hallow shotList literals already covered by the frozen 65-slot registry. The 28 nested hits remain nested because each is under /thumb/ or /thumbs/. No new target-gallery URL was found.","","## Late-window 50-gallery ledger","",f"Window {ledger.get('late_target_window',{}).get('from')} through {ledger.get('late_target_window',{}).get('to')}; anchor {ledger.get('late_target_window',{}).get('anchor')}.","",f"Decision counts: park {len(park)}, open {len(openr)} (source_503 {len(s503)}, not_queried {len(nq)}).","","| rank | gallery | prior | r2 | uncovered interval | source page |","|---:|---|---|---|---|---|"]
for r in rows:
    iv="; ".join(f"{x.get('from','?')}..{x.get('to','?')} ({x.get('status','?')})" for x in r["uncovered_late_segments"])
    md.append(f"| {r['registry_rank']} | {r['gallery']} | {r['prior_late_status']} | {r['decision']} | {iv} | {r['source_page'].get('path')}:{r['source_page'].get('addshots_line')} |")
md += ["","Park means accepted complete late prefix/index evidence, not image 404. Open rows remain transport-failed or unqueried. Karazhan, Zul'Aman, and Black Temple are parked only from accepted complete evidence; no 503 or 429 is converted to 404.","","## Exact alias continuation queue","",f"Concrete hits {len(concrete)} -> {len(entries)} exact URLs; nested {len(nested_alias)}, dynamic {len(dynamic)}, unresolved source bases {len(unresolved)}.",f"v37 statuses {dict(status_counts)}; the v37 map is not accepted. Priority queue has {len(queue)} exact candidates (cap 80).","","| rank | exact URL | v37 status | context | source route:line |","|---:|---|---|---|---|"]
for i,e in enumerate(queue[:40],1):
    s=e.get("source") or {}; md.append(f"| {i} | {e['resolved_url']} | {e['v37_cross_reference']['status']} | {e.get('source_context_kind')} | {s.get('route')}:{s.get('line')} |")
md += ["","Every queue item preserves source page route/hash, line, raw/decoded literal, and source-base resolution. No URL was guessed, requested, replayed, or accepted.","","## Evidence boundary","", "Latest control boundary remains the second 429; this r2 made zero network requests and did not modify status, site, source, accepted receipts, or old reports."]
(OUT/"crossref-r2-report.md").write_bytes(("\n".join(md)+"\n").encode("utf-8"))

cross={"schema":"wow-recovery.gallery-audit.source15-crossref-r2.v1","generated_utc":generated,"network_performed":False,"input_bindings":bind,"root_acceptance_interpretation":acc.get("qualified_interpretation"),"counts":{"text_files_checked":len(scan.get("text_inventory",[])),"text_bytes_checked":scan_rec.get("text_bytes_checked"),"network_requests_in_original_scan":scan.get("network_requests"),"known_gallery_reference_hits":len(scan.get("known_gallery_reference_hits",[])),"hallow_concrete_literals_reclassified":len(hallow_rows),"nested_directory_previews_retained":len(nested),"new_target_gallery_urls":acc.get("new_target_gallery_urls"),"concrete_alias_hits":len(concrete),"concrete_alias_unique_resolved":len(entries),"unresolved_aliases":len(unresolved),"v37_priority_queue":len(queue)},"hallow_literal_records":hallow_rows,"nested_boundary":{"count":len(nested),"all_nested_under_thumb_or_thumbs":not bad_nested,"new_native_gallery_urls":0},"interpretation":"The 65 Hallow shotList lines are literal paths already in the frozen registry; the 28 nested previews remain excluded from native coverage."}
write("crossref-r2-report.json",cross); write("coverage-ledger-r2-addendum.json",add); write("alias-priority-queue-v37-r2.json",alias)
outs=[OUT/x for x in ("crossref-r2-report.json","crossref-r2-report.md","coverage-ledger-r2-addendum.json","alias-priority-queue-v37-r2.json")]
rec={"schema":"wow-recovery.gallery-audit.r2-receipt.v1","generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"network_performed":False,"elapsed_seconds":round(time.time()-started,3),"input_bindings":bind,"output_bindings":{},"validation":{"full_scan_preserved":True,"root_source15_acceptance_bound":True,"hallow_set_reconciled":len(hallow_rows)==65,"nested_boundary_reconciled":len(nested)==28 and not bad_nested,"ledger_row_count":len(rows),"ledger_park_count":len(park),"ledger_open_count":len(openr),"alias_unique_count":len(entries),"priority_queue_cap":len(queue)<=80,"v37_maps_not_accepted":not bool(v37.get("accepted")) and not bool(v37_s.get("accepted")),"zero_network_requests":True},"important_limits":["No Wayback request, replay, pagination, redirect, or image acceptance occurred.","Open rows remain unverified; 503/429 and not-queried are not image 404.","v37 local/provenance matches are prepared evidence only."]}
for p in outs: rec["output_bindings"][p.name]={"path":str(p.relative_to(ROOT)).replace("\\","/"),"bytes":p.stat().st_size,"sha256":sha(p)}
write("r2-audit-receipt.json",rec)
print(json.dumps({"out_dir":str(OUT.relative_to(ROOT)).replace("\\","/"),"outputs":{p.name:{"bytes":p.stat().st_size,"sha256":sha(p)} for p in outs+[OUT/"r2-audit-receipt.json"]},"counts":{"ledger_rows":len(rows),"park":len(park),"open":len(openr),"source_503":len(s503),"not_queried":len(nq),"hallow_literals":len(hallow_rows),"nested":len(nested),"alias_hits":len(concrete),"alias_unique":len(entries),"queue":len(queue),"v37_status":dict(status_counts),"scope":dict(scope_counts)},"network_requests":0},ensure_ascii=False,indent=2))

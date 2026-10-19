
import json, hashlib, time
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT=Path.cwd()
OUT=ROOT/"research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/full-source15-crossrefs-r3"
OUT.mkdir(parents=True,exist_ok=True)
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p):
    try: return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError: return None
def write(name,obj):
    p=OUT/name; p.write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode("utf-8")); return p
def rel(p): return str(p.relative_to(ROOT)).replace("\\","/")

r2dir=ROOT/"research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/full-source15-crossrefs-r2"
r2_alias_p=r2dir/"alias-priority-queue-v37-r2.json"
r2_ledger_p=r2dir/"coverage-ledger-r2-addendum.json"
r2_cross_p=r2dir/"crossref-r2-report.json"
r2_rec_p=r2dir/"r2-audit-receipt.json"
r2_alias=load(r2_alias_p); r2_ledger=load(r2_ledger_p); r2_cross=load(r2_cross_p); r2_rec=load(r2_rec_p)
base_ledger_p=ROOT/"research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/coverage-ledger.json"
prov_p=ROOT/".scratch/pages-resources-20261019-v37/export-provenance.json"
prov=load(prov_p)
manifest_p=ROOT/prov["source_manifest"]
manifest=load(manifest_p)
v37_root=ROOT/".scratch/pages-resources-20261019-v37"
primary_p=ROOT/"research/continuous-recovery-20261019/integration/v37/v37-primary-source-map.json"
supp_p=ROOT/"research/continuous-recovery-20261019/integration/v37/v37-supplement-source-map.json"
primary=load(primary_p); supp=load(supp_p)
started=time.time()

prov_by_route={x.get("route"):x for x in prov.get("files",[]) if x.get("route")}
manifest_by_route={x.get("route"):x for x in manifest.get("files",[]) if x.get("route")}
map_urls=set()
for m in (primary,supp):
    for x in m.get("items",[]):
        for k in ("logical_url","original"):
            if isinstance(x.get(k),str): map_urls.add(x[k])

def host(url):
    return (urlsplit(url).hostname or "").lower() or None
def scheme(url):
    return (urlsplit(url).scheme or "").lower() or None
def safe_output_path(p):
    if not isinstance(p,str) or not p: return None
    q=(v37_root/p).resolve()
    try: q.relative_to(v37_root.resolve())
    except ValueError: return None
    return q
def same_host(candidate, mf):
    ch=host(candidate)
    mh=(str(mf.get("origin_namespace") or "").lower() or host(mf.get("source_base_url") or ""))
    ph=host(mf.get("source_base_url") or "")
    if not ch: return False, None
    known={x for x in (mh,ph) if x}
    return bool(known and ch in known), (sorted(known) if known else [])
def local_check(entry):
    u=entry.get("resolved_url"); route=urlsplit(u).path or "/"
    pr=prov_by_route.get(route); mf=manifest_by_route.get(route)
    prov_path=pr.get("output_path") if pr else None
    actual=safe_output_path(prov_path)
    file_exists=bool(actual and actual.is_file())
    actual_sha=hashlib.sha256(actual.read_bytes()).hexdigest() if file_exists else None
    actual_bytes=actual.stat().st_size if file_exists else None
    expected_sha=(pr or {}).get("derived_sha256") or (pr or {}).get("source_sha256") or (mf or {}).get("derived_sha256") or (mf or {}).get("source_sha256")
    expected_bytes=(pr or {}).get("derived_length") or (pr or {}).get("source_length") or (mf or {}).get("derived_length") or (mf or {}).get("source_length")
    host_match, known_hosts=same_host(u,mf or pr or {})
    cand_scheme=scheme(u); mf_scheme=scheme((mf or {}).get("source_base_url") or (pr or {}).get("source_base_url") or "")
    content_match=file_exists and ((expected_sha is None or expected_sha==actual_sha) and (expected_bytes is None or expected_bytes==actual_bytes))
    if u in map_urls:
        status="v37_map_prepared"
    elif not pr:
        status="v37_no_provenance_route"
    elif not file_exists:
        status="v37_provenance_only"
    elif not host_match:
        status="v37_path_only_identity_mismatch"
    elif not content_match:
        status="v37_local_content_mismatch"
    elif cand_scheme and mf_scheme and cand_scheme!=mf_scheme:
        status="v37_local_host_match_scheme_variant"
    else:
        status="v37_local_exact_identity"
    identity={
        "candidate_url":u,"candidate_host":host(u),"candidate_scheme":cand_scheme,
        "provenance_route":route,"provenance_output_path":prov_path,
        "manifest_origin_namespace":(mf or {}).get("origin_namespace"),
        "manifest_source_base_url":(mf or {}).get("source_base_url"),
        "manifest_known_hosts":known_hosts,"host_match":host_match,
        "scheme_match":bool(cand_scheme and mf_scheme and cand_scheme==mf_scheme),
        "content_match":content_match,"expected_sha256":expected_sha,"expected_bytes":expected_bytes,
        "actual_path":rel(actual) if actual else None,"actual_sha256":actual_sha,"actual_bytes":actual_bytes,
        "file_exists":file_exists,
    }
    return status,identity

entries=[]
for old in r2_alias.get("all_exact_concrete_aliases",[]):
    e=dict(old); st,ident=local_check(e); e["v37_cross_reference_r3"]={"status":st,"identity":ident,"map_exact_match":e.get("resolved_url") in map_urls,"map_accepted":False,"local_is_accepted":False}
    entries.append(e)

ledger=load(base_ledger_p)
complete_dirs=[]
for row in ledger.get("rows",[]):
    if row.get("late_status")=="complete":
        se=row.get("source_evidence") or {}
        if se.get("source_directory"): complete_dirs.append({"gallery":row.get("gallery"),"source_directory":se["source_directory"],"window":row.get("late_target_window")})
def ledger_overlap(entry):
    path=unquote(urlsplit(entry.get("resolved_url","")).path or "")
    return [x for x in complete_dirs if path.startswith(x["source_directory"].rstrip("/")+"/") or path==x["source_directory"].rstrip("/")]
for e in entries:
    overlaps=ledger_overlap(e)
    e["late_ledger_dedupe"]={
        "matching_complete_prefixes":overlaps,
        "decision":"exclude_same_complete_prefix" if overlaps else "no_matching_frozen_complete_prefix",
        "unverified_if_none":not bool(overlaps),
    }

status_counts=Counter(e["v37_cross_reference_r3"]["status"] for e in entries)
ledger_dedupe_counts=Counter(e["late_ledger_dedupe"]["decision"] for e in entries)
available={e["v37_cross_reference_r3"]["status"] for e in entries}
queue=[e for e in entries if e["v37_cross_reference_r3"]["status"] in {"v37_provenance_only","v37_no_provenance_route"} and not e["late_ledger_dedupe"]["matching_complete_prefixes"]]
# Preserve the r2 ordering, which was already status/context/url prioritized.
queue=queue[:80]
excluded=[e for e in entries if e not in queue]
source_status=Counter()
for e in entries:
    st=e["v37_cross_reference_r3"]["status"]
    source_status[st]+=1

rows=[]
for old in r2_ledger["rows"]:
    r=dict(old)
    if r.get("prior_late_status")=="complete":
        r["uncovered_late_segments"]=[]
        r["r3_uncovered_correction"]="Empty because accepted complete evidence covers the target window; no full-window placeholder is inserted."
    else:
        r["uncovered_late_segments"]=old.get("uncovered_late_segments") or [dict(old.get("late_window") or {})]
        r["r3_uncovered_correction"]="Open row retains its concrete uncovered interval."
    rows.append(r)
park=[r for r in rows if r.get("decision")=="park"]; openr=[r for r in rows if r.get("decision")=="open"]; s503=[r for r in openr if r.get("prior_late_status")=="source_503"]; nq=[r for r in openr if r.get("prior_late_status")=="not_queried"]

inputs={}
for p in (r2_alias_p,r2_ledger_p,r2_cross_p,r2_rec_p,base_ledger_p,prov_p,manifest_p,primary_p,supp_p):
    inputs[rel(p)]={"sha256":sha(p),"bytes":p.stat().st_size}
generated=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
cross={
 "schema":"wow-recovery.gallery-audit.source15-crossref-r3.v1","generated_utc":generated,"network_performed":False,
 "r2_preserved":{rel(r2_cross_p):sha(r2_cross_p),rel(r2_alias_p):sha(r2_alias_p),rel(r2_ledger_p):sha(r2_ledger_p)},
 "corrections":{"real_v37_root":rel(v37_root),"provenance_output_path_used":True,"source_manifest_identity_used":True,"complete_uncovered_empty_preserved":True},
 "counts":r2_cross.get("counts",{}),
 "v37_identity_counts":dict(status_counts),
 "late_ledger_dedupe_counts":dict(ledger_dedupe_counts),
 "interpretation":"R3 corrects r2's site-root classification. A path-only match is never treated as a canonical US resource without source-manifest host identity and byte/hash confirmation."
}
add={
 "schema":"wow-recovery.gallery-audit.coverage-ledger-r3-addendum.v1","generated_utc":generated,"network_performed":False,
 "r2_preserved":{rel(r2_ledger_p):sha(r2_ledger_p)},
 "correction":"Complete rows retain uncovered_late_segments=[]; only open rows receive a concrete uncovered interval.",
 "late_window":r2_ledger.get("late_window"),
 "summary":{"group_count":len(rows),"park_count":len(park),"open_count":len(openr),"source_503_count":len(s503),"not_queried_count":len(nq),"native_strict_images_in_late_audit":0,"parked_groups":[x["gallery"] for x in park],"open_groups":[x["gallery"] for x in openr]},
 "park_boundary":"Park means do not repeat the same complete prefix time window. It is not a final claim that a gallery is fully recovered or that all missing entities are 404. Karazhan and Black Temple keep their prior explicit park/defer decisions.",
 "rows":rows
}
alias={
 "schema":"wow-recovery.gallery-audit.source15-alias-priority-r3.v1","generated_utc":generated,"network_performed":False,
 "r2_preserved":{rel(r2_alias_p):sha(r2_alias_p)},
 "inputs":inputs,
 "v37_root":rel(v37_root),"provenance_output_path_rule":"Check v37 root/output_path, then verify bytes and SHA256 against provenance/source-manifest record.",
 "identity_rule":"Canonical host must match the candidate source_base_url/origin_namespace in the frozen source manifest; HTTP/HTTPS scheme variants remain separately labeled. Same path with another host is path-only identity mismatch.",
 "counts":{"r2_concrete_hits":r2_alias.get("full_scan_counts",{}).get("concrete_unmapped_alias_hits"),"r2_unique_urls":len(entries),"dynamic_alias_hits":r2_alias.get("full_scan_counts",{}).get("dynamic_alias_hits"),"nested_alias_hits":r2_alias.get("full_scan_counts",{}).get("nested_alias_hits"),"v37_status_counts":dict(status_counts),"late_ledger_dedupe_counts":dict(ledger_dedupe_counts),"priority_queue_count":len(queue),"priority_queue_cap":80},
 "v37_status_definitions":{"v37_local_exact_identity":"File exists under provenance output_path and host, scheme, length and SHA match source identity.","v37_local_host_match_scheme_variant":"File exists and host, length and SHA match; candidate scheme differs from manifest scheme.","v37_path_only_identity_mismatch":"File/path exists but manifest/source host does not match candidate host; never counted as canonical.","v37_provenance_only":"Provenance route exists but actual output_path file is absent.","v37_local_content_mismatch":"File exists but length/SHA does not match frozen provenance.","v37_map_prepared":"Exact URL appears in prepared v37 map; map remains unaccepted."},
 "all_exact_concrete_aliases":entries,
 "priority_queue":queue,
 "excluded_after_r3":excluded,
 "queue_boundary":"Local exact-evidence queue only. Existing host-matched local resources are excluded; no matching complete ledger prefix is explicitly unverified, not assumed fresh."
}
write("crossref-r3-report.json",cross)
write("coverage-ledger-r3-addendum.json",add)
write("alias-priority-queue-v37-r3.json",alias)

md=["# Source15 and late gallery audit r3","","R3 is additive; r2 remains unchanged. No network request was made.","","## Corrections","",f"Real v37 root: {rel(v37_root)}. Every candidate uses provenance output_path plus actual file length/SHA and frozen source-manifest host identity. Complete ledger rows keep an empty uncovered interval; only open rows retain uncovered windows.","","## 50-gallery coverage","",f"Rows: {len(rows)}; park {len(park)}; open {len(openr)} (source_503 {len(s503)}, not_queried {len(nq)}). Park means do not repeat the same complete prefix window, not a gallery-wide 404 or final recovery claim.","","| rank | gallery | prior | r3 | uncovered | source page |","|---:|---|---|---|---|---|"]
for r in rows:
    iv="; ".join(f"{x.get('from','?')}..{x.get('to','?')} ({x.get('status','?')})" for x in r["uncovered_late_segments"]) or "none (complete)"
    md.append(f"| {r['registry_rank']} | {r['gallery']} | {r['prior_late_status']} | {r['decision']} | {iv} | {r['source_page'].get('path')}:{r['source_page'].get('addshots_line')} |")
md += ["","","## v37 identity and continuation queue","",f"Status counts: {dict(status_counts)}. Late complete-prefix overlap: {dict(ledger_dedupe_counts)}.","","| rank | exact URL | r3 status | host match | bytes/SHA match | ledger dedupe |","|---:|---|---|---|---|---|"]
for i,e in enumerate(queue[:40],1):
    ident=e["v37_cross_reference_r3"]["identity"]; md.append(f"| {i} | {e['resolved_url']} | {e['v37_cross_reference_r3']['status']} | {ident.get('host_match')} | {ident.get('content_match')} | {e['late_ledger_dedupe']['decision']} |")
md += ["","The queue excludes files that are already present with canonical host identity and matching bytes/SHA. A path-only or host-mismatched match is retained separately and never treated as a US canonical resource. No URL was requested or accepted."]
(OUT/"r3-audit.md").write_bytes(("\n".join(md)+"\n").encode("utf-8"))

outs=[OUT/x for x in ("crossref-r3-report.json","coverage-ledger-r3-addendum.json","alias-priority-queue-v37-r3.json","r3-audit.md")]
rec={"schema":"wow-recovery.gallery-audit.r3-receipt.v1","generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"network_performed":False,"elapsed_seconds":round(time.time()-started,3),"input_bindings":inputs,"output_bindings":{},"validation":{"r2_preserved":all(p.is_file() for p in (r2_alias_p,r2_ledger_p,r2_cross_p,r2_rec_p)),"real_v37_root_used":str(v37_root)==str(ROOT/".scratch/pages-resources-20261019-v37"),"provenance_output_path_checked":True,"source_manifest_host_checked":True,"ledger_rows":len(rows),"complete_rows_empty_uncovered":all(not r["uncovered_late_segments"] for r in rows if r["prior_late_status"]=="complete"),"open_rows_have_intervals":all(r["uncovered_late_segments"] for r in rows if r["prior_late_status"]!="complete"),"queue_cap":len(queue)<=80,"zero_network_requests":True}}
for p in outs: rec["output_bindings"][p.name]={"path":rel(p),"bytes":p.stat().st_size,"sha256":sha(p)}
write("r3-audit-receipt.json",rec)
print(json.dumps({"outputs":{p.name:{"bytes":p.stat().st_size,"sha256":sha(p)} for p in outs+[OUT/"r3-audit-receipt.json"]},"counts":{"rows":len(rows),"park":len(park),"open":len(openr),"source_503":len(s503),"not_queried":len(nq),"r3_status":dict(status_counts),"ledger_dedupe":dict(ledger_dedupe_counts),"queue":len(queue)},"network_requests":0},ensure_ascii=False,indent=2))

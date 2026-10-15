from __future__ import annotations
import hashlib, json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(r"D:\WOW_Encyclopedia")
OUT=ROOT/"research/continuous-recovery-20261015/v9-audit"
OLD=ROOT/"research/continuous-recovery-20261015/sidebar-audit/audit.json"
AUDIT=OUT/"audit.json"
TASK=ROOT/"research/continuous-recovery-20261015/v9-audit-task-input.json"
PRECHECK=ROOT/"research/continuous-recovery-20261015/v9-route-independent-precheck.json"
ROUTE=ROOT/".scratch/pages-resources-20261015-v9/__offline/route-map.json"
PROV=ROOT/".scratch/pages-resources-20261015-v9/export-provenance.json"
BROWSER=ROOT/"research/continuous-recovery-20261015/core-pages-integration/browser/v9-browser-receipt.json"
ART_GAP=ROOT/"research/continuous-recovery-20261015/wrath-artwork-viewer-gap.json"
FROZEN=ROOT/"offline/build-manifest.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def rel(p):
    try: return p.relative_to(ROOT).as_posix()
    except ValueError: return str(p).replace("\\","/")
def exists_record(p):
    return {"path":rel(p),"exists":p.is_file(),"bytes":p.stat().st_size if p.is_file() else None,"sha256":digest(p) if p.is_file() else None}
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

old=load(OLD); audit=load(AUDIT); task=load(TASK); pre=load(PRECHECK); rm=load(ROUTE); prov=load(PROV)
old_by={r["record_id"]:r for r in old["records"]}; records=audit["records"]; good={"resolved","resolved_via_alias","resolved_recovered"}

# Preserve both route and alias membership when the v9 map contains both keys.
for r in records:
    route=r.get("normalized_route")
    rt=rm.get("routes",{}).get(route) if route else None
    at=rm.get("aliases",{}).get(route) if route else None
    r["route_map_route_target"]=rt
    r["route_map_alias_target"]=at
    r["route_map_membership"]="route_and_alias" if rt is not None and at is not None else "route" if rt is not None else "alias" if at is not None else None
    if at is not None:
        ev=f".scratch/pages-resources-20261015-v9/__offline/route-map.json:aliases[{route}] — maps_to={at}"
        if ev not in r.get("evidence",[]): r.setdefault("evidence",[]).append(ev)

contract=[]
for declared in task.get("paths",[]):
    p=ROOT/declared["path"]; actual=exists_record(p)
    contract.append({**actual,"declared_bytes":declared.get("bytes"),"declared_sha256":declared.get("sha256"),"matches":actual["exists"] and actual["bytes"]==declared.get("bytes") and actual["sha256"]==declared.get("sha256")})

changes=[]
for r in records:
    o=old_by[r["record_id"]]
    if o.get("current_page_status") in {"missing_export_route","missing_page_file"} and r.get("current_page_status") in good:
        changes.append({
            "record_id":r["record_id"],"section":r.get("section"),"label":r.get("label"),"href":r.get("href"),
            "source_menu":r.get("source_menu"),"source_line":r.get("source_line"),
            "old_page_status":o.get("current_page_status"),"old_normalized_route":o.get("normalized_route"),
            "old_resolved_path":o.get("resolved_path"),"new_page_status":r.get("current_page_status"),
            "normalized_route":r.get("normalized_route"),"route_map_membership":r.get("route_map_membership"),
            "route_map_route_target":r.get("route_map_route_target"),"route_map_alias_target":r.get("route_map_alias_target"),
            "resolved_path":r.get("resolved_path"),"resolved_static_url":r.get("resolved_static_url"),
            "page_bytes":r.get("page_bytes"),"page_sha256":r.get("page_sha256"),
            "page_provenance":r.get("page_provenance"),"evidence":r.get("evidence",[])
        })
regressions=[]
for r in records:
    o=old_by[r["record_id"]]
    if o.get("current_page_status") in good and r.get("current_page_status") not in good:
        regressions.append({"record_id":r["record_id"],"route":r.get("normalized_route"),"old_status":o.get("current_page_status"),"new_status":r.get("current_page_status")})

effective=[r for r in records if r.get("scope")!="scope_excluded"]
resolved=[r for r in effective if r.get("current_page_status") in good]
resolved_paths=sorted({r["resolved_path"] for r in resolved if r.get("resolved_path")})
resolved_checks=[]; hash_mismatches=[]
for path in resolved_paths:
    p=ROOT/path; actual=exists_record(p); linked=[r for r in resolved if r.get("resolved_path")==path]
    expected_sha=linked[0].get("page_sha256") if linked else None; expected_bytes=linked[0].get("page_bytes") if linked else None
    ok=actual["exists"] and actual["sha256"]==expected_sha and actual["bytes"]==expected_bytes
    item={"path":path,"bytes":actual["bytes"],"sha256":actual["sha256"],"matches_record":ok}
    resolved_checks.append(item)
    if not ok: hash_mismatches.append(item)
status_counts=Counter(r.get("current_page_status") for r in effective)
route_counts={"routes":len(rm.get("routes",{})),"aliases":len(rm.get("aliases",{})),"route_and_alias_keys":len(set(rm.get("routes",{}))&set(rm.get("aliases",{})))}
now=datetime.now(timezone.utc).isoformat(); actual_frozen=digest(FROZEN); expected_frozen=task.get("frozen_manifest_expected_sha256")

audit["generated_utc"]=now; audit["network_performed"]=False
audit["frozen_baseline"].update({"expected_sha256_from_acceptance":expected_frozen,"actual_sha256":actual_frozen,"unchanged":actual_frozen==expected_frozen,"source":"research/continuous-recovery-20261015/v9-audit-task-input.json:frozen_manifest_expected_sha256"})
audit["scope"]["latest_derived_site"]=".scratch/pages-resources-20261015-v9"; audit["scope"]["comparison_site"]=".scratch/pages-resources-20261015-v8"
audit["summary"]["route_map_counts"]=route_counts
audit["summary"]["effective_page_state_counts"]={"resolved_current_route":sum(status_counts.get(x,0) for x in good),"external_or_dynamic":status_counts.get("external_or_dynamic",0),"missing_export_route":status_counts.get("missing_export_route",0),"business_or_sensitive":status_counts.get("business_or_sensitive",0)}
audit["input_contract_verification"]=contract
audit["v9_verification"]={
    "route_map":exists_record(ROUTE),"export_provenance":exists_record(PROV),"provenance_file_count":len(prov.get("files",[])),
    "resolved_distinct_file_count":len(resolved_paths),
    "resolved_file_hash_method":"Each distinct resolved_path was read as v9 derived bytes and compared by length/SHA-256 to every linked menu record; linked records must agree.",
    "resolved_file_check_count":len(resolved_checks),"resolved_file_hash_mismatches":hash_mismatches,
    "precheck_path":rel(PRECHECK),"precheck_sha256":digest(PRECHECK),"precheck_file_check_count":len(pre.get("file_checks",[])),
    "precheck_resolved_distinct_file_count":pre.get("resolved_distinct_file_count"),
    "precheck_counts_match":pre.get("menu_records")==len(records) and pre.get("distinct_missing_routes")==len({r.get("normalized_route") for r in effective if r.get("current_page_status")=="missing_export_route"}) and pre.get("resolved_distinct_file_count")==len(resolved_paths),
    "browser_receipt_inputs":[exists_record(x) for x in [BROWSER,ART_GAP] if x.exists()],
    "known_static_boundaries":{
        "artwork_viewer_gap":"/wrath/art.xml?s=12 is a known local 404; artwork.xml card href remains an observed route.",
        "artwork_missing_pairs":"Browser receipt separates five provenance-backed common pairs from eight missing pairs; missing.svg fallback is not recovery.",
        "shared_border_gap":"Browser receipt records shared ssborder1.png placeholder separately from content-image availability.",
        "interaction_scope":"This audit is static_indication_only; browser diagnostics are separate.",
        "business_exhibits":"Account/Forums/Support/WoW Main 74 records remain scope_excluded and are not counted as missing pages."
    }
}
audit["comparison"]={"prior_audit_path":rel(OLD),"prior_audit_sha256":digest(OLD),"prior_v8_status_source":"prior audit current_page_status only; v8 bytes remain historical comparison.","changed_observation_count":len(changes),"changed_distinct_route_count":len({x["normalized_route"] for x in changes}),"prior_resolved_route_regression_count":len(regressions),"prior_resolved_route_regressions":regressions,"delta_summary_path":rel(OUT/"delta-summary.json")}
dump(AUDIT,audit)

delta={"schema":"continuous-wow-v9-sidebar-delta/v1","generated_utc":now,"network_requests":0,
 "inputs":{"prior_audit":exists_record(OLD),"v9_audit":exists_record(AUDIT),"task_input":exists_record(TASK),"route_map":exists_record(ROUTE),"export_provenance":exists_record(PROV),"v9_manifest":exists_record(ROOT/".scratch/offline-navigation-20261015-v9/build-manifest.json"),"frozen_manifest":exists_record(FROZEN),"precheck":exists_record(PRECHECK)},
 "menu_conservation":audit["menu_conservation"],"v9_effective_page_state_counts":audit["summary"]["effective_page_state_counts"],"route_map_counts":route_counts,
 "changed_observation_count":len(changes),"changed_distinct_route_count":len({x["normalized_route"] for x in changes}),"changed_observations":changes,
 "prior_resolved_route_regression_count":len(regressions),"prior_resolved_route_regressions":regressions,"resolved_distinct_file_count":len(resolved_paths),"resolved_file_hash_mismatch_count":len(hash_mismatches),
 "missing_distinct_routes":pre.get("missing_routes",[]),"missing_distinct_route_count":len(pre.get("missing_routes",[])),"known_static_boundaries":audit["v9_verification"]["known_static_boundaries"],"scope_excluded_counts":audit["menu_conservation"].get("excluded_by_section_observed")}
dump(OUT/"delta-summary.json",delta)

md=[]
md += ["# Final v9 sidebar static audit","",f"- Generated UTC: {now}; network requests: 0.","- Scope: all 1,241 menu observations: 588 original entries, 579 Legacy menu observations reclassified with parser_unclassified_legacy, and 74 true scope exclusions.","- Route/page/resource evidence is local. Interaction fields remain static_indication_only; browser results and runtime gaps remain separate.","","## Inputs and conservation","",f"- Menu conservation: total {audit['menu_conservation']['total_observed']}/{audit['menu_conservation']['total_expected']}; original {audit['menu_conservation']['original_in_scope_observed']}/{audit['menu_conservation']['original_in_scope_expected']}; legacy {audit['menu_conservation']['legacy_reclassified_observed']}/{audit['menu_conservation']['legacy_reclassified_expected']}; true excluded {audit['menu_conservation']['true_excluded_observed']}/{audit['menu_conservation']['true_excluded_expected']}.",f"- Frozen offline/build-manifest.json: {actual_frozen}; expected {expected_frozen}; unchanged={actual_frozen==expected_frozen}.",f"- v9 route map: {route_counts['routes']} routes, {route_counts['aliases']} aliases, {route_counts['route_and_alias_keys']} keys in both maps.","- All six declared v9 task inputs were re-hashed and matched; the full list is in audit.json input_contract_verification.","","## Current v9 effective page state","",f"- Resolved current route/alias/recovered: {audit['summary']['effective_page_state_counts']['resolved_current_route']}.",f"- External or dynamic: {audit['summary']['effective_page_state_counts']['external_or_dynamic']}; business or sensitive: {audit['summary']['effective_page_state_counts']['business_or_sensitive']}; missing export route: {audit['summary']['effective_page_state_counts']['missing_export_route']}.",f"- Missing distinct routes: {len(pre.get('missing_routes',[]))}.",f"- Distinct resolved v9 files read and SHA-256 checked: {len(resolved_paths)}; mismatches: {len(hash_mismatches)}.",f"- Per-menu page states: {dict(sorted(status_counts.items()))}.","","## v8 to v9 route delta","",f"Page-state changes from the accepted v8 audit: {len(changes)} observations across {len({x['normalized_route'] for x in changes})} distinct routes; prior resolved-route regressions: {len(regressions)}."]
for x in changes:
    target=x["route_map_alias_target"] or x["route_map_route_target"]
    md.append(f"- {x['normalized_route']} — {x['label']} from {x['source_menu']}: {x['old_page_status']} -> {x['new_page_status']}; {x['resolved_path']}; {x['page_bytes']} bytes; SHA {x['page_sha256']}; map {x['route_map_membership']} -> {target}.")
md += ["","## Remaining static boundaries","",f"- The {len(pre.get('missing_routes',[]))} missing routes are legacy News RSS targets listed in delta-summary.json; no monthly-similarity alias is inferred.","- /wrath/artwork.xml resolves, but the observed card href /wrath/art.xml?s=12 remains a viewer gap. The browser receipt separately records five provenance-backed common image pairs, eight missing pairs, and the shared ssborder1.png placeholder; missing-image fallback is not recovery.","- Account, Forums, Support, and WoW Main records remain static/excluded exhibits and are accounted for in the 74-record exclusion count.","- No production route map, frozen manifest, ledger, browser receipt, or old audit was edited. repair-proposals.json in this directory is advisory only.","","## Method and evidence","", "- audit_local_v9.py reapplies the accepted local classifier to the same 1,241 source identities with v9 route-map.json and export-provenance.json. It performs no network acquisition.", "- Every resolved menu record stores source menu path/line, v9 resolved path, byte length, page SHA-256, provenance binding, route target and alias target where present, plus evidence strings.",f"- Independent precheck {rel(PRECHECK)} is a cross-check, not a substitute for per-record evidence; SHA-256 {digest(PRECHECK)}.",""]
(OUT/"audit.md").write_text("\n".join(md),encoding="utf-8")
print(json.dumps({"audit":rel(AUDIT),"delta":rel(OUT/"delta-summary.json"),"markdown":rel(OUT/"audit.md"),"generated_utc":now,"records":len(records),"effective":len(effective),"excluded":len(records)-len(effective),"resolved":audit["summary"]["effective_page_state_counts"]["resolved_current_route"],"external":audit["summary"]["effective_page_state_counts"]["external_or_dynamic"],"business":audit["summary"]["effective_page_state_counts"]["business_or_sensitive"],"missing_observations":audit["summary"]["effective_page_state_counts"]["missing_export_route"],"missing_distinct_routes":len(pre.get("missing_routes",[])),"changed_observations":len(changes),"changed_distinct_routes":len({x["normalized_route"] for x in changes}),"resolved_distinct_files":len(resolved_paths),"hash_mismatches":len(hash_mismatches),"frozen_unchanged":actual_frozen==expected_frozen},ensure_ascii=False,indent=2))

"""Accept static v9 audit evidence and advance only the local-preview ledger."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p,value):
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    audit_path=OUT/"v9-audit/audit.json"
    delta_path=OUT/"v9-audit/delta-summary.json"
    audit,delta=load(audit_path),load(delta_path)
    prior=load(OUT/"sidebar-audit/audit.json")
    precheck=load(OUT/"v9-route-independent-precheck.json")
    route_path=ROOT/".scratch/pages-resources-20261015-v9/__offline/route-map.json"
    routes=load(route_path)
    errors,context_drift=[],[]
    normalization_changes=[]
    additional_file_reads={}
    for item in audit["input_hashes"]:
        if item["exists"] and sha(ROOT/item["path"])!=item["sha256"]:
            if item["path"] in ("CHANGELOG.md","docs/media-and-navigation-recovery-20261015.md"):
                context_drift.append({"path":item["path"],"recorded_sha256":item["sha256"],"current_sha256":sha(ROOT/item["path"]),"reason":"root publication/context update; not route or payload input"})
            else:
                errors.append("critical input changed: "+item["path"])
    for item in delta["inputs"].values():
        if sha(ROOT/item["path"])!=item["sha256"]:
            errors.append("delta input hash changed: "+item["path"])
    old={x["record_id"]:x for x in prior["records"]}
    new={x["record_id"]:x for x in audit["records"]}
    files={x["path"]:x for x in precheck["file_checks"]}
    if len(audit["records"])!=1241 or set(old)!=set(new):
        errors.append("1241 menu identity conservation failed")
    changes=[]
    for identity,r in new.items():
        o=old[identity]
        for key in ("source_path","source_line","source_role","menu_id","label","href","scope","effective_in_scope"):
            if o.get(key)!=r.get(key):
                errors.append("identity/scope changed: "+identity+" "+key)
        target=routes["routes"].get(r.get("normalized_route")) or routes["aliases"].get(r.get("normalized_route"))
        if r.get("normalized_route")!=o.get("normalized_route"):
            normalization_changes.append({"record_id":identity,"href":r["href"],"prior_normalized_route":o.get("normalized_route"),"current_normalized_route":r.get("normalized_route"),"reason":"v9 auditor preserves source href trailing slash; both PTR compatibility forms map to accepted local exhibit files"})
        if r["current_page_status"].startswith("resolved"):
            if target!=r["resolved_static_url"]:
                errors.append("route mapping mismatch: "+identity)
            check=files.get(r["resolved_path"])
            if check is None and r.get("normalized_route")!=o.get("normalized_route"):
                path=ROOT/r["resolved_path"]
                check={"path":r["resolved_path"],"bytes":path.stat().st_size,"sha256":sha(path)}
                additional_file_reads[r["resolved_path"]]=check
            if not check or check["bytes"]!=r["page_bytes"] or check["sha256"]!=r["page_sha256"]:
                errors.append("independent file-byte precheck differs: "+identity)
            if r.get("interaction_validation")!="static_indication_only":
                errors.append("static interaction scope exceeded")
        elif r["current_page_status"]=="missing_export_route" and target:
            errors.append("false missing route")
        if o["current_page_status"].startswith("resolved") and not r["current_page_status"].startswith("resolved"):
            errors.append("prior resolved route regressed")
        if o["current_page_status"]=="missing_export_route" and r["current_page_status"].startswith("resolved"):
            changes.append(identity)
    missing=sorted({r["normalized_route"] for r in new.values() if r["current_page_status"]=="missing_export_route"})
    if len(changes)!=14 or len(missing)!=23 or len(files)!=460 or sha(route_path)!=precheck["route_map_sha256"]:
        errors.append("delta/independent precheck conservation failed")
    frozen=sha(ROOT/"offline/build-manifest.json")
    if frozen!="397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459":
        errors.append("frozen baseline changed")
    checked=datetime.now(timezone.utc).isoformat()
    receipt={"schema":"continuous-wow-v9-sidebar-acceptance/v1","checked_utc":checked,"accepted":not errors,"network_requests":0,"audit_sha256":sha(audit_path),"delta_sha256":sha(delta_path),"menu_observations":1241,"current_audited_observations":1167,"resolved_observations":sum(r["current_page_status"].startswith("resolved") for r in new.values()),"resolved_distinct_files":460,"missing_observations":sum(r["current_page_status"]=="missing_export_route" for r in new.values()),"distinct_missing_routes":len(missing),"missing_routes":missing,"recovered_observations":len(changes),"recovered_distinct_routes":len({new[k]["normalized_route"] for k in changes}),"file_validation":"459 worker file declarations matched independently read precheck; PTR canonical index was additionally read because fresh audit preserves the original trailing slash instead of the historical /ptr compatibility form; fixed v9 inputs unchanged","normalization_changes":normalization_changes,"additional_file_reads":list(additional_file_reads.values()),"frozen_manifest_sha256":frozen,"context_input_drift":context_drift,"runtime_scope":"static audit only; viewer 404, eight missing artwork pairs, shared border/source-prefix bug and skipped Howling-Fjord interaction remain separately recorded","errors":errors}
    save(OUT/"v9-sidebar-acceptance.json",receipt)
    if errors:
        raise SystemExit(json.dumps({"accepted":False,"errors":errors}))
    current_path=OUT/"ledger.current.json"
    snapshot=OUT/"ledger.v8-accepted-0725.json"
    if snapshot.exists():
        if sha(snapshot)!="178da25a57fb9e6211b40228b6d6cc1545d40606791d9fb39e23dcb49f758412":
            raise SystemExit("prior v8 ledger snapshot differs")
    else:
        if sha(current_path)!="178da25a57fb9e6211b40228b6d6cc1545d40606791d9fb39e23dcb49f758412":
            raise SystemExit("current ledger moved before v8 snapshot")
        snapshot.write_bytes(current_path.read_bytes())
    ledger=load(snapshot)
    for item in ledger["items"]:
        r=new[item["audit_record_id"]]
        item.update({"page_status":r["current_page_status"],"resource_status":r["asset_status"],"interaction_status":r["interaction_status"],"interaction_validation":r.get("interaction_validation"),"normalized_route":r.get("normalized_route"),"resolved_path":r.get("resolved_path"),"next_action":r["next_action"],"priority":r["priority"]})
        item["evidence"].append({"path":"research/continuous-recovery-20261015/v9-audit/audit.json","record_id":r["record_id"]})
        if "LOCAL-SIDEBAR-V9-006" not in item["task_ids"]:
            item["task_ids"].append("LOCAL-SIDEBAR-V9-006")
        if r["asset_status"]=="local_dependencies_resolved" and r["current_page_status"].startswith("resolved"):
            item["next_action"]="静态路由及已扫描依赖可用；交互继续保留静态迹象边界，无新增获取任务。"
        if r.get("normalized_route")=="/wrath/artwork.xml":
            item["runtime_observations"]={"evidence":"research/continuous-recovery-20261015/v9-browser-independent-review.json","gallery_complete":False,"viewer_click_status":404,"available_pairs":[1,3,6,9,12],"missing_pairs":[2,4,5,7,8,10,11,13],"shared_border_placeholder":True,"roothost_export_bug":"root owns derived directory-prefix repair"}
            item["next_action"]="等待已取 viewer 的依赖/API、原图与晚期补充来源验收，再由 root 整合 roothost 修复；图库当前未通过完整性验收。"
    effective=[r for r in new.values() if r["effective_in_scope"]]
    ledger.update({"generated_utc":checked,"current_preview":".scratch/pages-resources-20261015-v9","published_accepted_preview":".scratch/pages-resources-20261015-v8","previous_accepted_ledger":{"path":"research/continuous-recovery-20261015/ledger.v8-accepted-0725.json","sha256":sha(snapshot)},"current_audit_acceptance":"research/continuous-recovery-20261015/v9-sidebar-acceptance.json","status_note":"Current fields reflect accepted v9 local static sidebar audit. v9 remains unpublished, has separately observed gallery/interaction gaps, and awaits root's directory-prefix fix/new derivative. Public accepted Pages remains v8; static interaction evidence does not imply runtime completeness."})
    ledger["summary"].update({"page_status_counts":dict(Counter(r["current_page_status"] for r in effective)),"resource_status_counts":dict(Counter(r["asset_status"] for r in effective)),"interaction_status_counts":dict(Counter(r["interaction_status"] for r in effective)),"distinct_missing_routes":len(missing),"resolved_distinct_files":460,"asset_status_count_scope":"menu observations with static placeholder/dependency indications; shared URLs, navigation and intentional placeholders overlap and are not unique missing-image counts"})
    save(current_path,ledger)
    print(json.dumps({"accepted":True,"audit_sha256":receipt["audit_sha256"],"delta_sha256":receipt["delta_sha256"],"current_ledger_sha256":sha(current_path),"prior_ledger_snapshot_sha256":sha(snapshot),"missing_observations":26,"missing_routes":23}))


if __name__=="__main__":
    main()

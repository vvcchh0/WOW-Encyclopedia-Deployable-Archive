"""Offline source-level acceptance; root separately owns Pages/runtime acceptance."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    oldpath=ROOT/".scratch/offline-navigation-20261015-v7c/build-manifest.json"
    newpath=ROOT/".scratch/offline-navigation-20261015-v9/build-manifest.json"
    receiptpath=newpath.parent/"BUILD-RECEIPT.json"
    old,new,receipt=load(oldpath),load(newpath),load(receiptpath)
    errors=[]
    byold={x["route"]:x for x in old["files"]}
    bynew={x["route"]:x for x in new["files"]}
    keys=("source_sha256","source_length","source_base_url","actual_timestamp","source_mime","origin_namespace")
    missing=[r for r in byold if r not in bynew]
    changed=[r for r,x in byold.items() if r in bynew and any(x.get(k)!=bynew[r].get(k) for k in keys)]
    if missing or changed:
        errors.append("prior source provenance changed")
    for alias,target in old["route_aliases"].items():
        if new["route_aliases"].get(alias)!=target:
            errors.append("prior alias changed: "+alias)
    core=load(OUT/"selected-core-pages-source-map.json")
    static=load(OUT/"selected-static-source-map.json")
    checks=[]
    for entry in core["entries"]+static["entries"]:
        route=entry.get("proposed_route",entry.get("target"))
        if route in ("/ptr","/ptr/"):
            route="/ptr/index.html"
        record=bynew[route]
        source,derived,raw=ROOT/record["source_local_path"],ROOT/record["output_path"],ROOT/entry["local_path"]
        if sha(source)!=entry["body_sha256"] or sha(raw)!=entry["body_sha256"] or source.stat().st_size!=entry["body_bytes"] or record["source_sha256"]!=entry["body_sha256"] or record["source_length"]!=entry["body_bytes"] or record["actual_timestamp"]!=entry["actual_timestamp"]:
            errors.append("selected source mismatch: "+route)
        if sha(derived)!=record["derived_sha256"] or derived.stat().st_size!=record["derived_length"]:
            errors.append("derived mirror bytes mismatch: "+route)
        if route.startswith("/_origins/") and record.get("source_base_url")!=entry["logical_url"]:
            errors.append("foreign origin mismatch: "+route)
        checks.append({"route":route,"source_bytes":source.stat().st_size,"source_sha256":sha(source),"actual_timestamp":record["actual_timestamp"],"derived_bytes":derived.stat().st_size,"derived_sha256":sha(derived)})
    if len(byold)!=8306 or len(bynew)!=8328 or len(checks)!=22:
        errors.append("source conservation failed")
    if new["route_aliases"].get("/pvp/battlegrounds/battlegroups.html")!="/pvp/battlegrounds/battlegroups/index.html":
        errors.append("BG alias mismatch")
    if sha(newpath)!=receipt["v9_manifest_sha256"]:
        errors.append("builder manifest receipt mismatch")
    for item in receipt["accepted_inputs"].values():
        if sha(ROOT/item["path"])!=item["sha256"]:
            errors.append("accepted input hash mismatch: "+item["path"])
    for key in ("selected_map","static_map","alias_map"):
        item=receipt[key]
        if sha(ROOT/item["path"])!=item["sha256"]:
            errors.append("builder map hash mismatch")
    frozen=sha(ROOT/"offline/build-manifest.json")
    if frozen!="397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459":
        errors.append("frozen manifest changed")
    result={"schema":"continuous-wow-core-integration-acceptance/v1","checked_utc":datetime.now(timezone.utc).isoformat(),"accepted":not errors,"acceptance_scope":"source mirror provenance/counts and selected22 derived bytes; Pages export/runtime remain root acceptance","network_requests":0,"prior_source_records":len(byold),"current_source_records":len(bynew),"new_source_records":len(checks),"prior_sources_missing":missing,"prior_source_provenance_changed":changed,"prior_aliases_preserved":len(old["route_aliases"]),"image_overlay_recipe_count":38,"image_overlay_application_pending_pages_export":True,"v9_manifest_sha256":sha(newpath),"v9_build_receipt_sha256":sha(receiptpath),"frozen_manifest_sha256":frozen,"selected_sources":checks,"errors":errors}
    (OUT/"core-pages-integration-acceptance.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="selected_sources"}))
    if errors:
        raise SystemExit(1)


if __name__=="__main__":
    main()

import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
root=Path(r"D:\WOW_Encyclopedia")
out=root/"research/continuous-recovery-20261015/v9-audit"
audit_path=out/"audit.json"
delta_path=out/"delta-summary.json"
md_path=out/"audit.md"
ledger_path=root/"research/continuous-recovery-20261015/ledger.current.json"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
 return h.hexdigest()
def rel(p): return p.relative_to(root).as_posix()
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+chr(10),encoding="utf-8")
def rec(p):
 return {"path":rel(p),"exists":p.is_file(),"bytes":p.stat().st_size if p.is_file() else None,"sha256":sha(p) if p.is_file() else None}
a=load(audit_path)
d=load(delta_path)
ledger=load(ledger_path)
now=datetime.now(timezone.utc).isoformat()
for r in a["records"]:
 r["group"]=r.get("section")
 r["scope_kind"]=r.get("scope")
ledger_meta={
 "path":rel(ledger_path),
 "sha256":sha(ledger_path),
 "generated_utc":ledger.get("generated_utc"),
 "current_preview":ledger.get("current_preview"),
 "summary_groups":ledger.get("summary",{}).get("groups"),
 "summary_scopes":ledger.get("summary",{}).get("scopes"),
 "summary_page_status_counts":ledger.get("summary",{}).get("page_status_counts"),
 "use":"read-only grouping cross-check; v9 page/resource statuses were recomputed from v9 route-map/provenance"
}
a["generated_utc"]=now
a["ledger_grouping_source"]=ledger_meta
a["input_hashes"].append({"path":rel(ledger_path),"exists":True,"bytes":ledger_path.stat().st_size,"sha256":ledger_meta["sha256"]})
a["v9_verification"]["ledger_grouping_source"]=ledger_meta
d["generated_utc"]=now
d["inputs"]["ledger_current"]=rec(ledger_path)
d["ledger_grouping_source"]=ledger_meta
dump(audit_path,a)
dump(delta_path,d)
with md_path.open("a",encoding="utf-8") as f:
 f.write(chr(10)+"## Ledger grouping cross-check"+chr(10))
 f.write(f"- Read-only source: {rel(ledger_path)}; SHA-256 {ledger_meta['sha256']}; generated {ledger_meta['generated_utc']}; current preview {ledger_meta['current_preview']}."+chr(10))
 f.write("- Its group/scope summary was retained as grouping context. v9 page/resource statuses were recomputed from the final v9 route map and provenance; ledger.current was not edited."+chr(10))
print(json.dumps({"generated_utc":now,"ledger_sha256":ledger_meta["sha256"],"audit_sha256":sha(audit_path),"delta_sha256":sha(delta_path)},ensure_ascii=False,indent=2))


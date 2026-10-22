from __future__ import annotations
import datetime as dt, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
CONTROL=HERE.parent
ROOT=HERE.parents[4]
GO_REL="research/continuous-recovery-20261022/root-wayback-control03-go.json"
GO=ROOT/GO_REL
RUNNER=CONTROL/"wayback_positive_control03.py"
RUNTIME=CONTROL/"runtime"
FLOOR=11005853696
WATCHDOG=180

def now(): return dt.datetime.now(dt.timezone.utc)
def stamp(t=None): return (t or now()).isoformat(timespec="milliseconds").replace("+00:00","Z")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(path,obj):
    path=Path(path); tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); os.replace(tmp,path)
def tree_state(path):
    path=Path(path)
    if not path.exists(): return None
    rows=[]
    for p in sorted(path.rglob("*")):
        if p.is_file():
            st=p.stat(); rows.append((p.relative_to(path).as_posix(),st.st_size,st.st_mtime_ns))
    return hashlib.sha256(json.dumps(rows,separators=(",",":")).encode()).hexdigest(),len(rows)
def guarded(cmd,timeout,out,err):
    start=now(); mono=time.monotonic(); timed=False; killed=False; kill_error=None
    with open(out,"wb") as so, open(err,"wb") as se:
        p=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=so,stderr=se,close_fds=True,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name=="nt" else 0)
        try: rc=p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed=True
            try: p.kill(); p.wait(timeout=10); killed=p.returncode is not None; rc=p.returncode
            except Exception as e: kill_error=type(e).__name__; rc=p.poll()
    return {"started_utc":stamp(start),"finished_utc":stamp(),"elapsed_seconds":round(time.monotonic()-mono,3),"timeout_seconds":timeout,"watchdog_enforced":True,"timed_out":timed,"kill_attempted":timed,"killed":killed,"kill_error_class":kill_error,"pid":p.pid,"return_code":rc}
def selftest():
    before=tree_state(RUNTIME); logs_inside=RUNTIME in HERE.parents or HERE==RUNTIME
    with tempfile.TemporaryDirectory(prefix=".kill-test-",dir=HERE) as d:
        d=Path(d); r=guarded([sys.executable,"-c","import time;time.sleep(5)"],0.25,d/"out.private",d/"err.private")
    after=tree_state(RUNTIME)
    obj={"schema":"wow-wayback-control03-attempt02-offline-check.v1","checked_utc":stamp(),"log_directory_relative_to_control03":HERE.name,"logs_inside_runtime":logs_inside,"runtime_snapshot_before":before,"runtime_snapshot_after":after,"runtime_unchanged":before==after,"synthetic_child":r,"network_requests":0,"passed":not logs_inside and before==after and r["timed_out"] and r["kill_attempted"] and r["killed"] and r["return_code"] is not None}
    atomic(HERE/"offline-layout-timeout-check.json",obj); print(json.dumps(obj,ensure_ascii=False)); return 0 if obj["passed"] else 2
def execute():
    if RUNTIME.exists(): raise SystemExit("refusing: runtime must be absent before runner; parent owns preservation of current preflight evidence")
    if not GO.is_file() or shutil.disk_usage(ROOT.anchor).free<FLOOR: raise SystemExit("refusing: GO missing or D: below floor")
    go=json.loads(GO.read_text(encoding="utf-8"))
    if go.get("schema")!="wow-root-wayback-positive-control03-go/v1" or go.get("accepted") is not True or go.get("root_go") is not True or go.get("network_authorized") is not True or go.get("parent_watchdog_seconds")!=WATCHDOG: raise SystemExit("refusing: fresh GO validation failed")
    exp=dt.datetime.fromisoformat(go["expires_utc"].replace("Z","+00:00"))
    if not (dt.datetime.fromisoformat(go["not_before_utc"].replace("Z","+00:00"))<=now()<exp): raise SystemExit("refusing: GO outside authorization window")
    private=HERE/"private"; out=private/"runner.stdout.log"; err=private/"runner.stderr.log"; receipt=HERE/"watchdog-receipt.json"
    if private.exists() or receipt.exists(): raise SystemExit("refusing: attempt02 is single-use")
    private.mkdir()
    free=shutil.disk_usage(ROOT.anchor).free
    result=guarded([sys.executable,"-X","utf8",str(RUNNER),"--execute","--go",GO_REL],WATCHDOG,out,err)
    atomic(receipt,{"schema":"wow-wayback-control03-attempt02-watchdog.v1","go_sha256":sha(GO),"started_utc":result["started_utc"],"finished_utc":result["finished_utc"],"disk_free_bytes_before":free,"disk_free_bytes_after":shutil.disk_usage(ROOT.anchor).free,"disk_floor_bytes":FLOOR,"private_stdout":"private/runner.stdout.log","private_stderr":"private/runner.stderr.log","watchdog":result,"no_response_values_in_receipt":True})
    print(json.dumps({"receipt":str(receipt.relative_to(CONTROL)),"watchdog":result},ensure_ascii=False)); return 124 if result["timed_out"] else int(result["return_code"] or 0)
if __name__=="__main__": raise SystemExit(selftest() if "--self-test" in sys.argv else execute())

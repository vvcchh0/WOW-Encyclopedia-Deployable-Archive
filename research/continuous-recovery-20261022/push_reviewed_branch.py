"""Normal push of an already reviewed branch, direct before process-local proxy."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('branch',choices=['main','gh-pages']);a=parser.parse_args()
sha=subprocess.check_output(['git','rev-parse',a.branch],cwd=ROOT,text=True).strip()
env=os.environ.copy()
for k in list(env):
 if k.lower() in {'http_proxy','https_proxy','all_proxy','no_proxy'}:env.pop(k)
env['GIT_TERMINAL_PROMPT']='0'
attempts=[]
for route in ['direct','proxy']:
 e=env.copy();e['NO_PROXY']='*' if route=='direct' else ''
 proxy='' if route=='direct' else 'http://127.0.0.1:7890'
 started=datetime.now(timezone.utc).isoformat()
 try:
  r=subprocess.run(['git','-c','http.proxy='+proxy,'-c','http.sslVerify=true','push','--porcelain','origin',a.branch],cwd=ROOT,env=e,text=True,capture_output=True,timeout=90)
  record={'route':route,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
 except subprocess.TimeoutExpired:
  record={'route':route,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'returncode':None,'timed_out':True,'stdout':'','stderr':''}
 attempts.append(record)
 if record['returncode']==0:break
 text=(record['stdout']+' '+record['stderr']).lower()
 if not record.get('timed_out') and not any(s in text for s in ['could not resolve','failed to connect','connection timed out','connection was reset','ssl connect','recv failure','unable to access','failed to receive']):break
report={'schema':'wow-reviewed-branch-push/v1','branch':a.branch,'commit_sha':sha,'attempts':attempts,'normal_push':True,'accepted':attempts[-1]['returncode']==0}
name='push-'+a.branch+'-'+sha[:8]+'.json'
(HERE/name).write_bytes((json.dumps(report,indent=2)+'\n').encode())
print(json.dumps({'accepted':report['accepted'],'branch':a.branch,'commit_sha':sha,'attempts':len(attempts),'last_route':attempts[-1]['route'],'receipt':name}))
raise SystemExit(0 if report['accepted'] else 2)

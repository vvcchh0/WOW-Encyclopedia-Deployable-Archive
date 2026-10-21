"""Push the exact accepted main commit; direct first, process-only fallback."""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'v51-main-push.json'
assert not OUT.exists()
expected = json.loads((PUB/'v51-main-commit.json').read_bytes())['commit']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==expected
environment = os.environ.copy()
for k in list(environment):
    if k.lower() in {'http_proxy','https_proxy','all_proxy','no_proxy'} or k.startswith('GIT_TRACE'):
        environment.pop(k,None)
attempts = []
def run(operation, proxy, seconds):
    command = ['git','-c','http.proxy='+proxy,'-c','http.lowSpeedLimit=1024','-c','http.lowSpeedTime=30',*operation]
    started = datetime.now(timezone.utc).isoformat()
    try:
        p = subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,timeout=seconds)
        row = {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'timed_out':False}
    except subprocess.TimeoutExpired as exc:
        decode = lambda b:b.decode('utf-8',errors='replace') if isinstance(b,bytes) else (b or '')
        row = {'returncode':None,'stdout':decode(exc.stdout),'stderr':decode(exc.stderr),'timed_out':True}
    row.update({'operation':operation,'transport':'proxy' if proxy else 'direct',
                'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'timeout_seconds':seconds})
    attempts.append(row)
    return row

first = run(['push','origin','main'],'',90)
accepted = first['returncode']==0
remote_confirmed = False
if not accepted:
    text = first['stderr'].lower()
    transport_failure = first['timed_out'] or any(s in text for s in (
        'could not resolve','failed to connect','connection','tls','ssl','timed out','network is unreachable','operation too slow'))
    if transport_failure:
        # A timed-out push may have completed remotely.  Read before sending again.
        check = run(['ls-remote','--exit-code','origin','refs/heads/main'],'http://127.0.0.1:7890',45)
        if check['returncode']==0 and check['stdout'].split()[0]==expected:
            fetch = run(['fetch','origin','refs/heads/main:refs/remotes/origin/main'],'http://127.0.0.1:7890',60)
            accepted = fetch['returncode']==0
            remote_confirmed = accepted
        elif check['returncode']==0:
            second = run(['push','origin','main'],'http://127.0.0.1:7890',90)
            accepted = second['returncode']==0
receipt = {'accepted':accepted,'commit':expected,'attempts':attempts,'force':False,
           'already_applied_remote_confirmed':remote_confirmed,'finished_utc':datetime.now(timezone.utc).isoformat()}
OUT.write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print(json.dumps({'accepted':accepted,'commit':expected,'attempts':len(attempts),
                  'last_transport':attempts[-1]['transport']}))
assert accepted

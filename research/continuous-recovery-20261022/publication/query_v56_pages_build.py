from pathlib import Path
from datetime import datetime,timezone
import json,sys
sys.path.insert(0,str(Path(__file__).parent/'release-tools'))
import create_upload_release as base
HERE=Path(__file__).parent
inputs=base.load_inputs(HERE/'v56-release-config.json');client=base.ReleaseCreator(inputs)
endpoint=f'repos/{inputs.repo}/actions/runs?branch=gh-pages&per_page=10'
data=client._gh_read(['api',endpoint,'--jq','{workflow_runs:[.workflow_runs[]|{id,name,head_sha,head_branch,status,conclusion,html_url,created_at,updated_at}]}'])
expected='ada74291b7f46afe3289fb2773e31449f4a5eb83'
runs=[r for r in data['workflow_runs'] if r['head_sha']==expected and r['head_branch']=='gh-pages']
result={'schema':'wow-pages-build-readback/v1','checked_utc':datetime.now(timezone.utc).isoformat(),'repo':inputs.repo,'version':'v56','expected_pages_commit':expected,'matching_runs':runs,'gh_events':client.process_events}
name='pages-build-v56-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json'
base._write_json_new(HERE/name,result)
print(json.dumps({'receipt':name,'matching_runs':runs},ensure_ascii=False))

"""Publish one already uploaded, owned release after checking its three exact assets."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,sys
sys.path.insert(0,str(Path(__file__).parent/'release-tools'))
import create_upload_release as base
parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,required=True);parser.add_argument('--notes',type=Path,required=True);args=parser.parse_args()
inputs=base.load_inputs(args.config);creator=base.ReleaseCreator(inputs)
intent=base._read_json(inputs.output_dir/'create-upload-intent.json','intent')
upload=base._read_json(inputs.output_dir/'create-upload-receipt.json','upload')
assert upload['accepted'] and upload['target_commit']==inputs.source_head and upload['tag']==inputs.tag
release_id=upload['release_id'];assert isinstance(release_id,int)
endpoint=f'repos/{inputs.repo}/releases/{release_id}'
release=creator._gh_read(['api',endpoint]);check=dict(release);check['draft']=True
observed=creator._verify_release(check,intent);assert set(observed)==set(inputs.expected_assets)
notes=args.notes.read_text('utf-8').rstrip()+"\n\n"+intent['release_body_marker']+"\n"
managed=args.notes.with_name(args.notes.stem+'.managed.md');assert not managed.exists();managed.write_text(notes,encoding='utf-8',newline='\n')
if release['draft']:
 cmd=['release','edit',inputs.tag,'--repo',inputs.repo,'--draft=false','--latest','--notes-file',str(managed)]
 result=creator._gh_once(cmd,proxy=False,timeout=90);after=creator._gh_read(['api',endpoint])
 if after['draft'] and result.returncode and base._is_transport_failure(result):
  result=creator._gh_once(cmd,proxy=True,timeout=90);after=creator._gh_read(['api',endpoint])
else:after=release
assert after['id']==release_id and after['tag_name']==inputs.tag and after['target_commitish']==inputs.source_head
assert after['draft'] is False and after['body'].rstrip()==notes.rstrip()
check=dict(after);check['draft']=True;observed=creator._verify_release(check,intent);assert set(observed)==set(inputs.expected_assets)
receipt={'schema':'wow-public-release-publish/v1','accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'version':inputs.version,'release_id':release_id,'tag':inputs.tag,'target_commit':inputs.source_head,'draft':False,'published_at':after['published_at'],'html_url':after['html_url'],'body_sha256':hashlib.sha256(after['body'].encode()).hexdigest(),'upload_receipt_sha256':hashlib.sha256((inputs.output_dir/'create-upload-receipt.json').read_bytes()).hexdigest(),'assets':[{'name':a['name'],'bytes':a['size'],'digest':a['digest'],'state':a['state'],'browser_download_url':a['browser_download_url']} for a in after['assets']],'events':creator.process_events,'anonymous_asset_checks':'pending'}
output=Path(__file__).parent/(inputs.version+'-public-release-publish.json');base._write_json_new(output,receipt)
print(json.dumps({'accepted':True,'release_id':release_id,'tag':inputs.tag,'published':True}))

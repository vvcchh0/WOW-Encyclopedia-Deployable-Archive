from pathlib import Path
import json, sys, hashlib
from datetime import datetime, timezone
sys.path.insert(0,str(Path(__file__).parent/'release-tools'))
import create_upload_release as base
ROOT=Path.cwd()
PUB=Path(__file__).parent
config=PUB/'v55-release-config-r3.json'
inputs=base.load_inputs(config)
creator=base.ReleaseCreator(inputs)
intent=json.loads((inputs.output_dir/'create-upload-intent.json').read_text('utf-8'))
upload=json.loads((inputs.output_dir/'create-upload-receipt.json').read_text('utf-8'))
assert upload['accepted'] and upload['release_id']==420673117
endpoint=f'repos/{inputs.repo}/releases/420673117'
release=creator._gh_read(['api',endpoint])
check_draft=dict(release);check_draft['draft']=True
observed=creator._verify_release(check_draft,intent)
assert set(observed)==set(inputs.expected_assets)
notes="""以2008年5月12日官网为基准的可浏览历史归档。

本版补入职业专题标题图、18张天赋连线箭头、3张声望奖励图标，并接通20张因改名或移动位置而漏配的天赋图标。这些补充均标注关联来源，原有天赋数据和说明保留。

另核对了Deadmines早期图片：九张原图和十张预览已在项目内，线上可用。50个玩家截图图库的原图与缩略图仍待恢复。

下载ZIP并解压；安装Python 3后，Windows双击 START_BROWSE.cmd。macOS/Linux在解压目录运行：

```sh
python3 tools/serve_pages_preview.py --site site --port 0 --open-browser
```

[在线浏览](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/) · [来源与工作记录](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/continuous-recovery-20261022.md)
"""+"\n"+intent['release_body_marker']+"\n"
notes=notes.replace('\\n','\n')
notes_path=PUB/'v55-release-notes.md'
notes_path.write_text(notes,encoding='utf-8',newline='\n')
args=['release','edit',inputs.tag,'--repo',inputs.repo,'--draft=false','--latest','--notes-file',str(notes_path)]
assert release['draft'] is False, 'read-only recovery expects the already published release'
result=base.CommandResult(0)
after=release
if after.get('draft') is True and result.returncode and base._is_transport_failure(result):
 result=creator._gh_once(args,proxy=True,timeout=90)
 after=creator._gh_read(['api',endpoint])
assert after['id']==420673117 and after['tag_name']==inputs.tag and after['target_commitish']==inputs.source_head
assert after['draft'] is False and after['body'].rstrip('\n')==notes.rstrip('\n')
for a in after['assets']:
 e=inputs.expected_assets[a['name']]
 assert a['state']=='uploaded' and a['size']==e['bytes'] and a['digest']=='sha256:'+e['sha256']
assert {a['name'] for a in after['assets']}==set(inputs.expected_assets)
receipt={'schema':'wow-public-release-publish/v1','accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'version':'v55','release_id':after['id'],'tag':inputs.tag,'target_commit':after['target_commitish'],'draft':after['draft'],'published_at':after['published_at'],'html_url':after['html_url'],'body_sha256':hashlib.sha256(after['body'].encode()).hexdigest(),'upload_receipt_sha256':hashlib.sha256((inputs.output_dir/'create-upload-receipt.json').read_bytes()).hexdigest(),'assets':[{'name':a['name'],'bytes':a['size'],'digest':a['digest'],'state':a['state'],'browser_download_url':a['browser_download_url']} for a in after['assets']],'events':creator.process_events,'anonymous_asset_checks':'pending','recovery_note':'Publishing succeeded; initial postcheck compared a retained trailing newline with a trimmed local value. This read-only recovery normalizes only trailing newlines.'}
base._write_json_new(PUB/'v55-public-release-publish.json',receipt)
print(json.dumps({'accepted':True,'release_id':after['id'],'url':after['html_url'],'draft':after['draft']}))

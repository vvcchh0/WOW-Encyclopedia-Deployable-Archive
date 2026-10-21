"""Prepare the verified v52 Pages/package checkpoint and concise current progress."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];BASE='research/continuous-recovery-20261021/'
PUB=ROOT/BASE/'publication';OUT=PUB/'v52-release-stage-config.json'
assert not OUT.exists()
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ('root-v52-final-acceptance.json','root-v52-portable-acceptance.json'):
    assert read(PUB/name)['accepted']
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert head==read(PUB/'v52-main-commit.json')['commit']
assert subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip()==head
producer=read(PUB/'v52-portable-package-report.json')
summary={key:producer[key] for key in ('archive','baseline_timestamp','processed_date','compression',
    'network_performed','package_member_count','site_member_count','sidecar','sidecar_bytes','sidecar_sha256')}
summary.update(producer_report_sha256=sha(PUB/'v52-portable-package-report.json'),
    archive_bytes=producer['verification']['archive_bytes'],archive_sha256=producer['verification']['archive_sha256'],
    independent_acceptance=BASE+'publication/root-v52-portable-acceptance.json',
    member_list_location='FILE_SHA256SUMS.txt inside the processed ZIP; full producer listing retained locally.')
(PUB/'root-v52-package-summary.json').write_bytes((json.dumps(summary,indent=2)+'\n').encode())
now=datetime.now(timezone.utc)
state_path=ROOT/BASE/'status.json';state=read(state_path)
state.update(phase='v52_pages_and_portable_accepted_release_pending',current_local_version='v52',
    current_pages_version='v52',offline_release_version='v51',current_code_commit=head,
    current_pages_commit='d46c14a0d655cf55a2608581441726845537a1f4',
    latest_pages_acceptance=BASE+'publication/root-v52-pages-online-acceptance.json',
    latest_portable_acceptance=BASE+'publication/root-v52-portable-acceptance.json',
    network_worker_current_task='complete_processed_v52_package_no_network',
    local_worker_current_task='complete_arathi_directory_fix',
    disk_free_latest_bytes=shutil.disk_usage(ROOT).free,updated_utc=now.isoformat())
state_path.write_bytes((json.dumps(state,indent=2)+'\n').encode())
tasks_path=ROOT/BASE/'tasks.json';tasks=read(tasks_path)
for row in tasks['tasks']:
    if row['id']=='FINAL':row['state']='v52_pages25_objects_and_portable_root_accepted_release_pending'
tasks_path.write_bytes((json.dumps(tasks,indent=2)+'\n').encode())
p=ROOT/'README.md';text=p.read_text(encoding='utf-8')
text=text.replace('下载 [2026-10-20 离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/download/archive-20080512-browser-20261020-v39/WOW_Encyclopedia_20080512_browser_20261020_v39.zip)（约 534 MB，解压后约 600 MB）',
    '下载 [2026-10-21 离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/download/archive-20080512-browser-20261021-v51/WOW_Encyclopedia_20080512_browser_20261021_v51.zip)（约 546 MB，解压后约 634 MB）')
text=text.replace('在线版为 v51，离线包暂为 v39；新版离线包已完成本地验证，准备发布。','在线版为 v52，离线包为 v51；同步新版离线包已完成本地验证，准备发布。')
needle='- 恢复奥尔多／占星者说明弹窗与派系切换，修复四页 Wrath 字母图的显示。'
assert needle in text
text=text.replace(needle,needle+'\n- 修复 Arathi 指南的图片目录，恢复二十张已有预览的显示。')
p.write_bytes(text.encode())
p=ROOT/'CHANGELOG.md';text=p.read_text(encoding='utf-8')
old='- 本地完成 v52：修复 Arathi 指南的动态目录，恢复 20 张已有预览的显示；两张原始缩略图仍缺。修正分轮清单为 391 个本地资源目标，准备部署。'
assert old in text
text=text.replace(old,'- 发布 v52：修复 Arathi 指南的动态目录，恢复 20 张已有预览的显示，25 个线上对象核对通过；两张缩略图仍缺。修正分轮清单为 391 个本地资源目标。')
p.write_bytes(text.encode())
with (ROOT/'docs/continuous-recovery-20261021.md').open('ab') as f:
    f.write((f'\n### {now:%H:%M} UTC — v52线上与便携包\n\n'
        '代码提交617243ac已正常push，Pages提交d46c14a0构建完成，25个线上对象均由direct取得并匹配。包制作一次完成，原图与其他页面保持。独立读取全部ZIP成员，并用解压后的包内服务实际检查导出来源表选出的资源路径；浏览行为复用当前v52实际Chrome记录及字节未变的v51记录。\n\n'
        '[线上核对](../research/continuous-recovery-20261021/publication/root-v52-pages-online-acceptance.json) · [便携包核对](../research/continuous-recovery-20261021/publication/root-v52-portable-acceptance.json)。当前线上为v52，公开离线包仍为v51，继续发布已验收v52包。\n').encode())
names=('v52-main-commit.json','v52-main-push.json','push_v52_main.py','root-v52-package-go.json',
    'v52-package-execution.json','root-v52-package-summary.json','v52-pages-publication.json',
    'v52-pages-build-control.json','v52-pages-build-control-r2.json','root-v52-pages-online-acceptance.json',
    'accept_v52_final_site.py','root-v52-final-acceptance.json','root-v52-portable-acceptance.json',
    'v52-release-notes.md','prepare_v52_release_checkpoint.py')
paths={BASE+'publication/'+name for name in names}
paths.update({'README.md','CHANGELOG.md','docs/continuous-recovery-20261021.md',BASE+'status.json',BASE+'tasks.json',
    BASE+'integration/portable-release-tools-v52/root-review.json'})
paths.update(BASE+'publication/v52-screenshots/'+name for name in ('arathi-ss5.png','arathi-ss30.png'))
tracked={}
for item in subprocess.check_output(['git','ls-tree','-rz','HEAD'],cwd=ROOT).split(b'\0'):
    if item:
        meta,name=item.split(b'\t',1);tracked[name.decode()]=meta.split()[2].decode()
changed=[]
for name in sorted(paths):
    p=ROOT/name;assert p.is_file();data=p.read_bytes();assert len(data)<2*1024*1024
    if tracked.get(name)!=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest():changed.append(name)
OUT.write_bytes((json.dumps({'paths':changed,'receipt':BASE+'publication/root-v52-release-staged-hygiene.json',
    'scope':'Accepted final v52 deployment, source-backed restored previews, independently checked processed package and concise public status. No raw source HTTP/cookies/site payload/ZIP staged.'},indent=2)+'\n').encode())
print(json.dumps({'paths':len(changed)}))

"""Prepare the reviewed one-page exception checkpoint before Pages publication."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 'research/continuous-recovery-20261021/'
PUB = ROOT / BASE / 'publication'
OUT = PUB / 'v52-code-stage-config.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
gate = read(PUB / 'root-v52-local-acceptance.json')
assert gate['accepted'] and read(PUB / 'root-v51-release-publication.json')['published']
now = datetime.now(timezone.utc)
state_path = ROOT / BASE / 'status.json'
state = read(state_path)
state.update(phase='v52_local_accepted_single_bounded_exception', current_local_version='v52',
    current_pages_version='v51', offline_release_version='v51', candidate_version='v52',
    current_code_commit='ff7c22532e6f1ed1e43b7febae2aebe847dbd017',
    latest_local_acceptance=BASE+'publication/root-v52-local-acceptance.json',
    latest_pages_acceptance=BASE+'publication/root-v51-pages-online-acceptance.json',
    latest_release_acceptance=BASE+'publication/root-v51-release-publication.json',
    rolling_missing_local_resource_targets=391,
    latest_gap_reconciliation=BASE+'publication/root-v52-gap-reconciliation.json',
    accepted_arathi_preview_displays_restored=20,
    bounded_export_exception=BASE+'publication/root-v52-bounded-exception-decision.json',
    source_downloads_closed=True, new_exports_closed=True,
    disk_free_latest_bytes=shutil.disk_usage(ROOT).free, updated_utc=now.isoformat())
state_path.write_bytes((json.dumps(state, indent=2)+'\n').encode())
tasks_path = ROOT / BASE / 'tasks.json'
tasks=read(tasks_path)
for row in tasks['tasks']:
    if row['id']=='FINAL':row['state']='v51_published_v52_single_local_directory_exception_accepted'
    if row['id']=='BUILD01':row['state']='v52_exact_arathi_directory_preserved20_existing_previews'
tasks_path.write_bytes((json.dumps(tasks, indent=2)+'\n').encode())
with (ROOT/'docs/continuous-recovery-20261021.md').open('ab') as f:
    f.write((f'\n### {now:%H:%M} UTC — Arathi目录转换的单次收尾例外\n\n'
      'v51离线包已发布并设为最新版本，三份附件的大小与摘要匹配；匿名检查取得NOTICE与摘要文件，ZIP最终HEAD长度正确。源码发布目标为ff7c2253。\n\n'
      '最后复核发现Arathi指南页22个index.htmlimages路径并非22个独立遗失素材。原脚本用path目录与images/arathi/拼接；导出把目录变成首页文件。20张精确JPEG早已取得，实际捕获来自2006年，另外ss17/ss18仍缺。因此对原13:05导出计划截止作一次有界例外：13:35前启动唯一v52导出，不重启资源获取，保持14:25用户截止及14:10发布截止。v51与历史版本保留。\n\n'
      'v52只修改这一页的一处目录赋值；其余10,142个声明对象、所有图片与脚本逐字节一致。实际Chrome已显示20张指南预览，另外两张仍为缺口，无外联或页面/请求错误。旧清单411个观察路径去掉22个异常拼接，加入2个真实缺失地址，修正为391个本地资源目标，仍是分轮覆盖范围而非全站总数。\n\n'
      '[目录调查](../research/continuous-recovery-20261021/local-audit/underdev-final-routing-review/README.md) · [例外决定](../research/continuous-recovery-20261021/publication/root-v52-bounded-exception-decision.json) · [v52本地验收](../research/continuous-recovery-20261021/publication/root-v52-local-acceptance.json)\n').encode())
p=ROOT/'CHANGELOG.md'
text=p.read_text(encoding='utf-8')
text=text.replace('## 2026-10-21\n', '## 2026-10-21\n\n- 本地完成 v52：修复 Arathi 指南的动态目录，恢复 20 张已有预览的显示；两张原始缩略图仍缺。修正分轮清单为 391 个本地资源目标，准备部署。[复原记录](docs/non-gallery-restoration-20261021.md)\n',1)
p.write_bytes(text.encode())
p=ROOT/'docs/non-gallery-restoration-20261021.md'
with p.open('ab') as f:
    f.write(('\n## Arathi指南预览\n\n收尾调查确认页面的22个异常地址来自目录基址转换错误，其中20张精确JPEG已在本地。v52仅对该指南页的path赋值保留目录，同页导航继续指向首页文件。全文件核对和实际Chrome检查完成，20张预览恢复显示；ss17与ss18的缩略图仍未取得。这属于已有指南素材的显示修复，没有重启玩家图库下载。\n\n修正后分轮清单为391个真实本地资源目标，旧411条观察路径及原报告保留供追溯。[修正清单](../research/continuous-recovery-20261021/publication/v52-remaining-resource-targets.csv) · [调查](../research/continuous-recovery-20261021/local-audit/underdev-final-routing-review/README.md)\n').encode())
names=('prepare_v52_exception_tools.py','root-v52-bounded-exception-decision.json',
    'accept_v52_code.py','root-v52-code-acceptance.json','v52-focused-test-execution.log',
    'root-v52-export-go.json','execute_v52_once.py','v52-export-execution.json','v52-export-execution.log',
    'accept_v52_tree.py','root-v52-export-acceptance.json','root_v52_browser.cjs',
    'root-v52-browser-acceptance.json','make_v52_local_acceptance.py','root-v52-local-acceptance.json',
    'root-v52-gap-reconciliation.json','v52-remaining-resource-targets.csv','verify_v52_pages.py',
    'prepare_v52_code_checkpoint.py','v51-release-main-commit.json','v51-release-main-push.json',
    'push_v51_release_main.py','v51-release-draft.json','root-v51-release-publication.json',
    'verify_v51_public_release.py','root-v51-release-public-download-acceptance.json',
    'check_v51_closeout_controls.py','root-v51-closeout-control.json','root-preview-cleanup.json')
paths={BASE+'publication/'+name for name in names}
paths.update({'tools/export_github_pages.py','tests/test_github_pages_export.py','CHANGELOG.md',
    'docs/continuous-recovery-20261021.md','docs/non-gallery-restoration-20261021.md',
    BASE+'status.json',BASE+'tasks.json'})
for directory in ('integration/v52','integration/portable-release-tools-v52','local-audit/underdev-final-routing-review'):
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/BASE/directory).iterdir()
                 if p.is_file() and p.suffix in {'.py','.md','.json','.csv'})
tracked={}
for item in subprocess.check_output(['git','ls-tree','-rz','HEAD'],cwd=ROOT).split(b'\0'):
    if item:
        meta,name=item.split(b'\t',1);tracked[name.decode()]=meta.split()[2].decode()
changed=[]
for name in sorted(paths):
    p=ROOT/name;assert p.is_file();data=p.read_bytes();assert len(data)<2*1024*1024
    if tracked.get(name)!=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest():changed.append(name)
OUT.write_bytes((json.dumps({'paths':changed,'receipt':BASE+'publication/root-v52-code-staged-hygiene.json',
    'scope':'Exact Arathi guide directory-base repair, corrected source-backed local gap set, actual bytes/browser proof, v51 published release proof and prepared v52 release tooling. No raw HTTP, source pages or ZIP payload.'},indent=2)+'\n').encode())
print(json.dumps({'paths':len(changed)}))

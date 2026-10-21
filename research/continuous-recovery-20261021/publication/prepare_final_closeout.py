"""Close this bounded recovery run after v52 public release and fresh controls."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];BASE='research/continuous-recovery-20261021/'
PUB=ROOT/BASE/'publication';OUT=PUB/'final-stage-config.json'
assert not OUT.exists()
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
release=read(PUB/'root-v52-release-publication.json')
assert release['accepted'] and release['published']
for name in ('root-v52-release-public-download-acceptance.json','root-v52-closeout-control.json'):
    assert read(PUB/name)['accepted']
automation=read(PUB/'root-automation-closeout.json')
assert automation['deleted'] is True and automation['id']=='wow-14'
now=datetime.now(timezone.utc)
assert now < datetime(2026,10,21,14,25,7,tzinfo=timezone.utc)
free=shutil.disk_usage(ROOT).free;assert free>=11005853696
state_path=ROOT/BASE/'status.json';state=read(state_path)
state.update(phase='bounded_run_complete_v52_published',run_completed_utc=now.isoformat(),
    current_local_version='v52',current_pages_version='v52',offline_release_version='v52',
    candidate_review=BASE+'publication/root-v52-local-acceptance.json',
    current_code_commit='617243ac2dd90cf47c925686d2619bcfd4e0a1fa',
    current_pages_commit='d46c14a0d655cf55a2608581441726845537a1f4',
    main_commit_at_release=release['target_commit'],release_tag=release['tag'],
    latest_release_acceptance=BASE+'publication/root-v52-release-publication.json',
    latest_public_download_acceptance=BASE+'publication/root-v52-release-public-download-acceptance.json',
    latest_closeout_control=BASE+'publication/root-v52-closeout-control.json',
    continuation_enabled=False,automation_status='DELETED',active_automation_id=None,
    in_flight_network_batch=None,prepared_network_batch=None,
    local_worker_current_task='complete',network_worker_current_task='complete',
    source_downloads_closed=True,new_exports_closed=True,
    disk_free_latest_bytes=free,updated_utc=now.isoformat())
state.pop('current_main_commit',None)
state['closeout_scope']='This14-hour bounded run is complete; remaining resource restoration is not complete. Final documentation commits may follow the immutable release target.'
state_path.write_bytes((json.dumps(state,indent=2)+'\n').encode())
tasks_path=ROOT/BASE/'tasks.json';tasks=read(tasks_path)
for row in tasks['tasks']:
    if row['id']=='LOCAL01':row['state']='rolling177_routes_corrected391_targets_root_accepted20_existing_arathi_previews_restored'
    if row['id']=='FINAL':row['state']='complete_v52_main_pages_processed_release_and_public_download_checked'
    if row['id']=='NET01':row['state']='closed_after_fresh429_no_wayback_resume_future_resource_work_remains'
tasks_path.write_bytes((json.dumps(tasks,indent=2)+'\n').encode())
p=ROOT/'README.md';text=p.read_text(encoding='utf-8')
text=text.replace('archive-20080512-browser-20261021-v51/WOW_Encyclopedia_20080512_browser_20261021_v51.zip',
    'archive-20080512-browser-20261021-v52/WOW_Encyclopedia_20080512_browser_20261021_v52.zip')
text=text.replace('在线版为 v52，离线包为 v51；同步新版离线包已完成本地验证，准备发布。','在线版与离线包均为 v52。')
p.write_bytes(text.encode())
p=ROOT/'CHANGELOG.md';text=p.read_text(encoding='utf-8')
needle='## 2026-10-21\n'
text=text.replace(needle,needle+'\n- 同步发布[v52 离线浏览包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261021-v52)（约 546 MB，解压约 634 MB），完成本轮非图库复原。内容、来源方法和剩余缺口见[本轮回顾](docs/recovery-summary-20261021.md)。\n',1)
p.write_bytes(text.encode())
p=ROOT/'docs/non-gallery-restoration-20261021.md';text=p.read_text(encoding='utf-8')
text=text.replace('391个真实本地资源目标','391个本地缺资源目标')
start='本轮从v39继续，优先恢复已有正文和交互。'
first=text.index(start);end=text.index('\n\n',first)
text=text[:first]+('本轮从v39推进至v52，在线版与处理后的离线浏览包已同步发布。恢复九职业天赋计算器、三处Flash展示、BlizzCast文字页与早期专题正文，并修复派系说明、Wrath字母图和Arathi指南预览。结果与剩余素材见[本轮回顾](recovery-summary-20261021.md)，分阶段来源和实现细节保留在下文。')+text[end:]
text+='\n## 本轮发布结果\n\nv52在线版与[离线浏览包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261021-v52)已同步。包内资源与本地导出一致，匿名下载入口检查完成。后续以修正后的391个本地资源目标为线索继续调查；它不涵盖所有动态状态，也不判断整个网络上的存档缺失。\n'
p.write_bytes(text.encode())
with (ROOT/'docs/continuous-recovery-20261021.md').open('ab') as f:
    f.write((f'\n### {now:%H:%M} UTC — 本轮收尾\n\n'
      f'v52处理后离线包已公开并设为最新Release，标签指向{release["target_commit"][:8]}。三份附件发布前后均与本地对象匹配，匿名取得两份小附件，ZIP最终HEAD长度为546,302,959字节；未重复下载整个ZIP。Pages仍为d46c14a0。Wayback停批状态保留，未开启新来源。\n\n'
      f'自动接续wow-14已删除，两名执行者均已完成。旧候选的10个预览进程已按标识停止，v52预览保留；来源、历史版本与ZIP未清理。D盘余量约{free/1e9:.2f}GB，高于10GiB阈值。当前时间仍在14小时授权范围内，完成文档提交与正常push后结束本轮。\n\n'
      '[累计回顾](recovery-summary-20261021.md) · [公开发布核对](../research/continuous-recovery-20261021/publication/root-v52-release-publication.json) · [匿名入口核对](../research/continuous-recovery-20261021/publication/root-v52-release-public-download-acceptance.json) · [最终控制](../research/continuous-recovery-20261021/publication/root-v52-closeout-control.json)\n').encode())
summary='''# 非图库复原回顾：2026-10-21

本轮从v39推进到v52，[在线浏览](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/)与[离线浏览包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261021-v52)已同步。以2008-05-12为重建基准，处理日期2026-10-21；各补充来源保留实际捕获日期。50个玩家图库与Media截图集合未在本轮重新获取。

## 恢复内容

- 九职业天赋计算器恢复加点、重置、非零模板保存与重载；加入986张注明后期来源的图标、6张界面图，并复用既有点数框素材。
- 通过Ruffle兼容层展示三份已有原始SWF：宝石插槽火花、男性矮人舞蹈、海象人模型；下载页悬停和共享菜单标签一并修复。
- 新增七份早期专题正文，更新内容目录并接通旧地址；BlizzCast前两期访谈及目录、RSS等形成五个本地阅读页，两期共50个对话块。
- 四幅百科／指南配图作为ArchiveCraft关联来源补充，页面给出来源链接；奥尔多／占星者说明弹窗使用已保存的原文恢复，奖励按钮地址修正。
- 已有Wrath字母图在四页恢复显示；Arathi指南的动态目录修正后，20张已保存的预览恢复显示，另外两张缩略图仍缺。

新增图片来源与已有图片的显示修复分别记录。本轮未通过Wayback取得新原图；后期天赋素材、当前关联站图片和原有历史捕获在来源表中区分。历史账号、报名、支付与促销功能继续以静态展品呈现。

## 获取与修复方法

Wayback的direct控制仍超时，代理控制返回429，按批次规则停止，没有改动全局DNS、代理或证书。Common Crawl静态次级目录可由direct取得，随后按精确域名、CDXJ记录与ARC偏移取得历史正文。原始HTTP与未处理来源留在本地，公开整理后的来源定位和派生结果。

修复进入新的派生版本：保留原始站点、Source15/16、旧版本和历史ZIP；在导出器中对精确来源脚本、页面与资源目录做兼容处理。Arathi问题尤其说明，应先核对动态拼接和本地精确文件，再决定是否需要下载：原22个异常路径中，20张图片已有实体，只有两张正确目标仍缺。

来源、方案与逐项验收见[复原记录](non-gallery-restoration-20261021.md)；执行过程与计划变更见[当日总账](continuous-recovery-20261021.md)。

## 验收与文件占用

最终站点有10,144个实际文件。主代理核对全部导出对象；v52相对v51仅修改Arathi页的一处目录赋值，所有图片、原脚本及其他页面保持字节一致。实际Chrome验证20张预览；其余功能复用对应版本的实际浏览记录和未变对象证明。v51核对80个线上对象，v52另核对25个相关对象，均成功。

处理后的ZIP约546MB、解压约634MB；全部10,150个成员独立检查，随后从含空格路径运行包内隔离服务，对来源表选出的页面与资源实际进行GET/HEAD检查。GitHub附件与本地包匹配，公开入口另作匿名检查。

图片占未压缩成员约525MB，已压缩的图片再次ZIP压缩收益很小；HTML等标记文件约55MB可压至约9MB。因此继续压缩主要能减少文本冗余，无法大幅缩小原字节图片。包内提供文件清单，公开仓库保留代码、整理后的来源与验收；原始取证包未上传。

- [v52完整导出核对](../research/continuous-recovery-20261021/publication/root-v52-export-acceptance.json)
- [实际浏览](../research/continuous-recovery-20261021/publication/root-v52-browser-acceptance.json)
- [线上对象](../research/continuous-recovery-20261021/publication/root-v52-pages-online-acceptance.json)
- [离线包与包内服务](../research/continuous-recovery-20261021/publication/root-v52-portable-acceptance.json)
- [公开Release](../research/continuous-recovery-20261021/publication/root-v52-release-publication.json)

## 剩余范围

分轮审计覆盖177条独立页面路径，修正后清单仍有391个本地资源目标，包括259个天赋素材目标、12个百科分类头像和两张Arathi缩略图。这是已检查状态的清单，尚未遍历所有动态状态；没有把本地缺图直接判为全网无存档。

BlizzCast图片与音频、部分旧新闻配图、专题插图、天赋背景和其他Flash依赖仍待取得。另有周年时间线截图目录的转换问题已单独记录，留待后续图库任务。玩家图库的范围结论继续见[此前调查](player-gallery-accessibility-20261020.md)。

后续先从[修正缺口清单](../research/continuous-recovery-20261021/publication/v52-remaining-resource-targets.csv)选择精确目标；Wayback需新的成功控制才恢复批次。有新捕获或关联来源时继续调查，已查窗口不盲目重复。
'''
(ROOT/'docs/recovery-summary-20261021.md').write_bytes(summary.encode())
names=('v52-release-main-commit.json','v52-release-main-push.json','push_v52_release_main.py',
    'v52-release-draft.json','root-v52-release-publication.json','verify_v52_public_release.py',
    'root-v52-release-public-download-acceptance.json','check_v52_closeout_controls.py',
    'root-v52-closeout-control.json','v52-final-control-tool-preparation.json',
    'root-automation-closeout.json','prepare_final_closeout.py')
paths={BASE+'publication/'+name for name in names}
paths.update({'README.md','CHANGELOG.md','docs/non-gallery-restoration-20261021.md',
    'docs/continuous-recovery-20261021.md','docs/recovery-summary-20261021.md',BASE+'status.json',BASE+'tasks.json'})
tracked={}
for item in subprocess.check_output(['git','ls-tree','-rz','HEAD'],cwd=ROOT).split(b'\0'):
    if item:
        meta,name=item.split(b'\t',1);tracked[name.decode()]=meta.split()[2].decode()
changed=[]
for name in sorted(paths):
    p=ROOT/name;assert p.is_file();data=p.read_bytes();assert len(data)<2*1024*1024
    if tracked.get(name)!=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest():changed.append(name)
OUT.write_bytes((json.dumps({'paths':changed,'receipt':BASE+'publication/root-final-staged-hygiene.json',
    'scope':'Final published v52 release/public-access proof, cumulative restoration report and closed scheduling state. No raw HTTP/cookies/site payload or ZIP staged.'},indent=2)+'\n').encode())
print(json.dumps({'paths':len(changed),'elapsed_hours':(now-datetime(2026,10,21,0,25,7,tzinfo=timezone.utc)).total_seconds()/3600,
                  'disk_free_bytes':free}))

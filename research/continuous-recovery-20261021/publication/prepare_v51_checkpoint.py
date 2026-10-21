"""Prepare the final reviewed non-gallery code/publication checkpoint."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 'research/continuous-recovery-20261021/'
PUB = ROOT / BASE / 'publication'
OUT = PUB / 'v51-stage-config.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
gate = read(PUB / 'root-v51-local-acceptance.json')
assert gate['accepted']
now = datetime.now(timezone.utc)
state_path = ROOT / BASE / 'status.json'
state = read(state_path)
state.update(phase='v51_root_accepted_main_sync_pages_and_package', current_local_version='v51',
             candidate_version='v51', candidate_publication_accepted=True,
             current_main_commit='b32a90a722d44ebb43dd5e287f799b9f22f15e21',
             latest_local_acceptance=BASE + 'publication/root-v51-local-acceptance.json',
             candidate_review=BASE + 'publication/root-v51-local-acceptance.json',
             accepted_source16_lore_literals=2, accepted_existing_image_route_repairs=1,
             rolling_audited_distinct_routes=177, rolling_missing_local_resource_targets=411,
             latest_audit_acceptance=BASE + 'publication/root-non-gallery-closeout-acceptance.json',
             network_worker_current_task='processed_v51_package_production_no_network',
             local_worker_current_task='complete_exact_t_image_alias',
             disk_free_latest_bytes=shutil.disk_usage(ROOT).free, updated_utc=now.isoformat())
state_path.write_bytes((json.dumps(state, indent=2) + '\n').encode())
tasks_path = ROOT / BASE / 'tasks.json'
tasks = read(tasks_path)
states = {'LOCAL01': 'rolling_177_route_browser_records_and_411_missing_local_targets_root_accepted',
          'NET01': 'fresh_control02_direct_timeout_proxy429_stopped_no_wayback_resume',
          'BUILD01': 'v51_final_source_lore_and_one_existing_image_alias_root_accepted',
          'FINAL': 'main_sync_pages_and_processed_v51_package_in_progress'}
for row in tasks['tasks']:
    if row['id'] in states:
        row['state'] = states[row['id']]
tasks_path.write_bytes((json.dumps(tasks, indent=2) + '\n').encode())
with (ROOT / 'docs/continuous-recovery-20261021.md').open('ab') as f:
    f.write((f'\n### {now:%H:%M} UTC — 最终本地版本v51与缺口清单\n\n'
             'v51只新增T.gif的一个精确兼容地址。原GIF捕获于2008-04-23 09:51:02，48×48、1,419字节，已在本地；源逻辑地址含双斜线，输出地址为单斜线，浏览适配器此前未识别该输出地址。修复后Howling Fjord、Grizzly Hills、Borean Tundra和Bard四页实际显示原图，未新增图片实体或HTML跳转。\n\n'
             '五页Chrome检查完成，包括两派说明弹窗与四页字母图；无外联、页面错误、失败请求或HTTP错误。全部10,144个实际文件核对；相对v50只改变路由表和嵌入路由表的浏览脚本，页面HTML及所有原图、脚本、奖励数据、SWF/WASM保持。v50作为本地检查点提交并正常push，最终以v51部署。\n\n'
             '[v51本地验收](../research/continuous-recovery-20261021/publication/root-v51-local-acceptance.json)\n\n'
             '合并分轮浏览记录得到177条独立页面路径，不表示在同一版本重新执行全站扫描。已观察状态中仍有411个本地缺资源目标，包含259个天赋图片目标；另单列已有但路由未接的T.gif（现由v51修复）及周年截图脚本拼接错误。后者保留为后续图库任务。两张名称含screenshot的新闻配图仍纳入新闻缺口，没有按文件名错误排除。原型排除只依据实际证据；未记录HTTP状态的已接受交互不补造200。\n\n'
             '[整理后的缺口清单](../research/continuous-recovery-20261021/local-audit/non-gallery-closeout-v49-r3/README.md) · [主代理复核](../research/continuous-recovery-20261021/publication/root-non-gallery-closeout-acceptance.json)\n\n'
             '12:11 UTC再次取一份已知正样本CDX控制：direct连接超时，代理返回429，2次请求后停止，无正CDX行，未开启后续Wayback批次。原始HTTP头和文本留本地，公开整理后的观察；没有重置历史失败记录。\n\n'
             '[最新控制](../research/continuous-recovery-20261021/publication/root-control02-source-acceptance.json)\n').encode())
with (ROOT / 'docs/non-gallery-restoration-20261021.md').open('ab') as f:
    f.write(('\n## 最终本地版本与剩余素材\n\nv51接通一张已有Wrath字母图的单斜线地址，四页恢复显示。源GIF保留原字节，未扩展为通用斜线折叠，也未推断其他字母图片。v50的派系说明随本轮最终版本发布。\n\n分轮浏览清单覆盖177条独立路径；已观察状态仍有411个缺资源目标，包含259个天赋目标和12个百科分类头像。完整动态状态尚未遍历。周年时间线的截图目录被旧脚本拼成异常路径，已确认是导出转换问题，列入后续图库工作。\n\n[页面覆盖与缺口](../research/continuous-recovery-20261021/local-audit/non-gallery-closeout-v49-r3/README.md)保留版本、来源和观察类型。Wayback最新控制仍为429；本轮没有通过该路径取得新原图。\n').encode())
p = ROOT / 'CHANGELOG.md'
t = p.read_bytes().decode().replace('## 2026-10-21\n',
    '## 2026-10-21\n\n- 本地完成 v51：接通已有 Wrath 字母图片的精确地址，四页恢复显示；整理 177 个页面路径的分轮浏览记录与剩余素材清单，准备最终部署与离线包。[复原记录](docs/non-gallery-restoration-20261021.md)\n', 1)
p.write_bytes(t.encode())
paths = {'CHANGELOG.md', 'docs/continuous-recovery-20261021.md', 'docs/non-gallery-restoration-20261021.md',
         BASE + 'status.json', BASE + 'tasks.json'}
paths.update(r['path'] for r in gate['bindings'])
paths.update(BASE + 'publication/' + p for p in (
    'v50-main-commit.json', 'v50-main-push.json', 'push_v50_main.py',
    'root-control02-source-acceptance.json', 'root-wayback-control02-go.json',
    'accept_v51_code.py', 'root-v51-code-acceptance.json', 'root-v51-export-go.json',
    'execute_v51_once.py', 'v51-export-execution.json', 'v51-export-execution.log',
    'accept_v51_tree.py', 'root-v51-export-acceptance.json', 'root_v51_browser.cjs',
    'root-v51-browser-acceptance.json', 'make_v51_local_acceptance.py',
    'root-v51-local-acceptance.json', 'root-v51-package-go.json',
    'root-non-gallery-closeout-acceptance.json', 'prepare_v51_checkpoint.py',
    'v51-screenshots/t-letter-bard.png',
))
paths.update(BASE + p for p in (
    'integration/v51/export_v51_once.py', 'integration/v51/v51-input-preparation.json',
    'integration/v51/v51-build-receipt.json',
    'integration/available-resource-route-review/route-review.json',
    'integration/available-resource-route-review/t-gif-references.csv',
    'integration/available-resource-route-review/README.md',
    'integration/available-resource-route-review/implementation-receipt-v51.json',
    'network/control02/control02_driver.py', 'network/control02/plan.json',
    'network/control02/source-selection.json', 'network/control02/input-bindings.json',
    'network/control02/root-offline-fixture.json', 'network/control02/offline-validation.json',
))
folder = ROOT / BASE / 'local-audit/non-gallery-closeout-v49-r3'
paths.update(p.relative_to(ROOT).as_posix() for p in folder.iterdir()
             if p.is_file() and p.suffix in {'.json', '.csv', '.md', '.py'})
tracked = {}
for item in subprocess.check_output(['git', 'ls-tree', '-rz', 'HEAD'], cwd=ROOT).split(b'\0'):
    if item:
        meta, name = item.split(b'\t', 1)
        tracked[name.decode()] = meta.split()[2].decode()
changed = []
for name in sorted(paths):
    p = ROOT / name
    assert p.is_file() and not set(p.parts) & {'private', 'raw', '__pycache__'}, name
    data = p.read_bytes()
    assert len(data) < 2 * 1024 * 1024, (name, len(data))
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if tracked.get(name) != blob:
        changed.append(name)
OUT.write_bytes((json.dumps({'paths': changed, 'receipt': BASE + 'publication/root-v51-staged-hygiene.json',
    'scope': 'Exact existing-image compatibility alias, final browser/tree proof, curated rolling audit and fresh stopped Wayback control. No raw HTTP/cookies, full scraped pages or ZIP payload.'}, indent=2) + '\n').encode())
print(json.dumps({'paths': len(changed), 'bytes': sum((ROOT / p).stat().st_size for p in changed)}))

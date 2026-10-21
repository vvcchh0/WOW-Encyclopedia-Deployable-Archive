"""Stage the accepted faction-lore checkpoint and v49 publication proof."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 'research/continuous-recovery-20261021/'
PUB = ROOT / BASE / 'publication'
OUT = PUB / 'v50-stage-config.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
gate = read(PUB / 'root-v50-local-acceptance.json')
assert gate['accepted']
now = datetime.now(timezone.utc)
state_path = ROOT / BASE / 'status.json'
state = read(state_path)
state.update(phase='v50_local_accepted_available_resource_route_review',
             current_local_version='v50', candidate_version='v50',
             latest_local_acceptance=BASE + 'publication/root-v50-local-acceptance.json',
             candidate_review=BASE + 'publication/root-v50-local-acceptance.json',
             candidate_publication_accepted=True,
             local_worker_current_task='read_only_available_resource_route_review',
             network_worker_current_task='non_gallery_closeout_scope_reconciliation',
             disk_free_latest_bytes=shutil.disk_usage(ROOT).free, updated_utc=now.isoformat())
state_path.write_bytes((json.dumps(state, indent=2) + '\n').encode())
tasks_path = ROOT / BASE / 'tasks.json'
tasks = read(tasks_path)
for row in tasks['tasks']:
    if row['id'] == 'BUILD01':
        row['state'] = 'v50_source16_lore_root_accepted_additional_existing_image_route_under_review'
    if row['id'] == 'FINAL':
        row['state'] = 'v49_online_v50_local_accepted_final_browser_package_in_preparation'
tasks_path.write_bytes((json.dumps(tasks, indent=2) + '\n').encode())
history = ROOT / 'docs/continuous-recovery-20261021.md'
with history.open('ab') as f:
    f.write((f'\n### {now:%H:%M} UTC — 派系说明文字恢复\n\n'
             'v50本地验收恢复奥尔多／占星者说明。来源是Source16已保存的2008-04-02令牌脚本，提取两段原始文字，分别850和1,104字符；不导入其奖励数据。一个3,273字节defer helper只用于主介绍页，原脚本、令牌页和全部既有图片保持。\n\n'
             '73项相关检查由10项本次检查及63项相同代码绑定的既有结果组成；不是本次重复执行73项。全部10,144个输出核对完成。实际Chrome打开两派说明弹窗并切换，主代理逐张查看两张截图。两轮失败探针分别涉及浏览器br标签序列化和未等待的宽泛文字定位，保留记录；最终探针使用原按钮锚点与可见状态检查，导出站点未改。\n\n'
             '[v50本地验收](../research/continuous-recovery-20261021/publication/root-v50-local-acceptance.json) · [原文来源](../research/continuous-recovery-20261021/publication/root-aldor-scryers-lore-source-acceptance.json)\n\n'
             '另发现Wrath字母T图片已存在，源路由为双斜线，而正文单斜线路由尚未接通；进行单独最小修复评审，不把已有素材计作新取得图片。\n').encode())
detail = ROOT / 'docs/non-gallery-restoration-20261021.md'
with detail.open('ab') as f:
    f.write(('\n## 派系说明文字\n\nv50本地恢复奥尔多／占星者说明弹窗。两段文字来自已保存的2008-04-02同专题令牌脚本；仅补入缺失说明，按钮切换、原奖励数据和令牌页保持。实际Chrome完成两个弹窗及两次派系切换，正文与来源对应。准备与本轮最终版本一并发布。\n').encode())
p = ROOT / 'README.md'
t = p.read_bytes().decode()
needle = '- 补齐天赋计算器的状态边框、重置和打印按钮，并恢复点数框布局。'
if '- 补充百科与指南的四幅配图' not in t:
    t = t.replace(needle, needle + '\n- 补充百科与指南的四幅配图，页面注明 ArchiveCraft 来源。')
p.write_bytes(t.encode())
p = ROOT / 'CHANGELOG.md'
t = p.read_bytes().decode().replace('## 2026-10-21\n',
    '## 2026-10-21\n\n- 本地完成 v50：用已保存的原文恢复奥尔多／占星者介绍弹窗与派系切换，准备随最终版本发布。[复原记录](docs/non-gallery-restoration-20261021.md)\n', 1)
p.write_bytes(t.encode())
paths = {'README.md', 'CHANGELOG.md', 'docs/continuous-recovery-20261021.md',
         'docs/non-gallery-restoration-20261021.md', BASE + 'status.json', BASE + 'tasks.json'}
paths.update(r['path'] for r in gate['bindings'])
paths.update(BASE + 'publication/' + n for n in (
    'root-v49-pages-online-acceptance.json', 'v49-main-commit.json', 'v49-main-push.json',
    'check_v49_encyclopedia_remaining.cjs', 'root-v49-encyclopedia-completion.json',
    'accept_aldor_scryers_lore.py', 'root-aldor-scryers-lore-source-acceptance.json',
    'accept_v50_code.py', 'root-v50-code-acceptance.json', 'root-v50-export-go.json',
    'execute_v50_once.py', 'v50-export-execution.json', 'v50-export-execution.log',
    'accept_v50_tree.py', 'root-v50-export-acceptance.json',
    'root_v50_browser.cjs', 'root_v50_browser_attempt1.cjs', 'root_v50_browser_attempt2.cjs',
    'v50-browser-attempt1.json', 'v50-browser-attempt2.json',
    'root-v50-browser-acceptance.json', 'make_v50_local_acceptance.py',
    'root-v50-local-acceptance.json', 'prepare_v50_checkpoint.py',
    'v50-screenshots/aldor-lore.png', 'v50-screenshots/scryers-lore.png',
))
paths.update(BASE + n for n in (
    'integration/v50/export_v50_once.py', 'integration/v50/v50-input-preparation.json',
    'integration/v50/v50-build-receipt.json',
    'integration/aldor-scryers-lore/prepare-receipt.json',
    'integration/aldor-scryers-lore/exporter-integration-receipt.json',
    'integration/aldor-scryers-lore/prototype-browser/browser-receipt-r4.json',
))
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
OUT.write_bytes((json.dumps({'paths': changed, 'receipt': BASE + 'publication/root-v50-staged-hygiene.json',
    'scope': 'Accepted original faction lore reuse, narrow opt-in exporter and portable tests, actual popup/browser evidence, v49 online reconciliation and source-bound text decision; no raw HTTP, cookies or scraped source pages.'}, indent=2) + '\n').encode())
print(json.dumps({'paths': len(changed), 'bytes': sum((ROOT / p).stat().st_size for p in changed)}))

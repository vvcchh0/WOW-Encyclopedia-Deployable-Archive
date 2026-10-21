"""Prepare the reviewed v49 checkpoint without raw source payloads."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 'research/continuous-recovery-20261021/'
PUB = ROOT / BASE / 'publication'
OUT = PUB / 'v49-stage-config.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
gate = read(PUB / 'root-v49-local-acceptance.json')
assert gate['accepted'] and not gate['published']
now = datetime.now(timezone.utc)
state_path = ROOT / BASE / 'status.json'
state = read(state_path)
state.update({
    'phase': 'v49_root_accepted_main_sync_and_pages_publication',
    'current_local_version': 'v49', 'candidate_version': 'v49',
    'candidate_publication_accepted': True,
    'latest_local_acceptance': BASE + 'publication/root-v49-local-acceptance.json',
    'candidate_review': BASE + 'publication/root-v49-local-acceptance.json',
    'accepted_related_encyclopedia_images': 3, 'accepted_related_guide_images': 1,
    'published_related_encyclopedia_images': 0, 'published_related_guide_images': 0,
    'local_worker_current_task': 'source_bound_aldor_scryers_lore_adapter',
    'network_worker_current_task': 'offline_saved_archivecraft_additional_resource_correlation',
    'disk_free_latest_bytes': shutil.disk_usage(ROOT).free,
    'updated_utc': now.isoformat(),
})
state_path.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
task_path = ROOT / BASE / 'tasks.json'
tasks = read(task_path)
states = {
    'NET01': 'four_current_archivecraft_images_accepted_wayback_still_stopped',
    'BUILD01': 'v49_four_images_and_exact_reward_button_paths_root_accepted',
    'FINAL': 'v49_main_and_pages_publication_pending_v46_online_v39_release',
    'TALENT02': '986_related_icons_six_ui_and_eight_layout_targets_published_v46',
}
for row in tasks['tasks']:
    if row['id'] in states:
        row['state'] = states[row['id']]
task_path.write_text(json.dumps(tasks, indent=2) + '\n', encoding='utf-8')
history_path = ROOT / 'docs/continuous-recovery-20261021.md'
with history_path.open('a', encoding='utf-8') as f:
    f.write(f'\n### {now:%H:%M} UTC — 四幅关联配图与奖励按钮\n\n')
    f.write('v46已发布，60个线上对象由direct核对通过；保留首次main推送低速失败和随后代理正常推送的两份回执。\n\n')
    f.write('ArchiveCraft当前页面提供Alleria、塞纳里奥议会、玛法里奥三幅百科图，以及The Broken指南缩略图。四张JPEG共176,325字节，保留原字节，页面注明并链接来源。它们属于当前关联来源补充，原始2008年目标捕获日期留空。The Broken菜单使用的动态thumb-broken.jpg与静态thumb-thebroken.jpg经原页面及脚本核对，共用同一张缩略图。\n\n')
    f.write('v47候选的来源注记对比度不足，v48候选点击菜单后仍使用未映射的动态名称，两版均未发布。v49修正这两处，并只替换奖励表脚本中的两个图片路径。65项相关代码检查、10,143个实际输出对象及五页实际Chrome操作验收通过。第一版浏览探针还检查了既有派系说明文字缺口；失败记录保留，最终探针将其作为后续修复项记录。\n\n')
    f.write('[v49本地验收](../research/continuous-recovery-20261021/publication/root-v49-local-acceptance.json) · [实际浏览](../research/continuous-recovery-20261021/publication/root-v49-browser-acceptance.json)\n\n')
    f.write('百科扩展浏览审计完成49/52页，另三页因本地连接/加载超时未完成，不计作通过。已浏览页还观察到12个独立分类头像CSS目标缺失。离线服务器backlog对照没有证明增大队列有改善，未修改生产服务器。BC介绍Flash只显示封面；播放所需FLV和皮肤SWF在已缓存Common Crawl覆盖块中均无精确匹配，视频尚未恢复。\n')
detail = ROOT / 'docs/non-gallery-restoration-20261021.md'
with detail.open('a', encoding='utf-8') as f:
    f.write('\n## 百科与指南关联配图\n\nv49补入Alleria、塞纳里奥议会、玛法里奥和The Broken四幅关联来源图片。页面给出ArchiveCraft来源链接；Alleria保留该站缩放JPEG。The Broken保留一张实际237×184缩略图，菜单点击使用同一素材，尚未补回标题图和大图。\n\n奖励表的两个阵营按钮已改为已有图片的正确本地地址。奥尔多／占星者页面说明框仍显示undefined，正在从已保存的同专题令牌页面脚本提取原始说明，单独修复。[本地验收](../research/continuous-recovery-20261021/publication/root-v49-local-acceptance.json)\n')
changelog = ROOT / 'CHANGELOG.md'
body = changelog.read_text(encoding='utf-8')
body = body.replace('## 2026-10-21\n', '## 2026-10-21\n\n- 本地完成 v49：补入三幅百科人物／组织配图及 The Broken 指南缩略图，页面注明 ArchiveCraft 来源；修复奥尔多／占星者奖励按钮的图片路径，准备部署。[复原记录](docs/non-gallery-restoration-20261021.md)\n', 1)
changelog.write_text(body, encoding='utf-8')
paths = {
    'README.md', 'CHANGELOG.md', 'NOTICE.md', 'docs/continuous-recovery-20261021.md',
    'docs/non-gallery-restoration-20261021.md', BASE + 'status.json', BASE + 'tasks.json',
}
paths.update(r['path'] for r in gate['bindings'])
pub_names = (
    'root-v46-pages-online-acceptance.json', 'v46-main-push.json',
    'v46-main-push-reconciliation.json', 'root-v47-candidate-review.json',
    'root-v48-candidate-review.json', 'root-v48-code-acceptance.json',
    'root-v48-export-acceptance.json', 'root-v49-code-acceptance.json',
    'root-v49-export-acceptance.json', 'root-v49-browser-acceptance.json',
    'root-v49-local-acceptance.json', 'accept_v49_code.py', 'accept_v49_tree.py',
    'prepare_guide_dynamic_reuse.py', 'prepare_related_broken_image.py',
    'root-related-guide-image-decision.json', 'root-related-guide-image-v49-decision.json',
    'root-archivecraft-broken-image-source-acceptance.json', 'v49-export-execution.json',
    'v49-export-execution.log', 'v49-tree-acceptance.log', 'root_v49_browser.cjs',
    'root_v49_browser_attempt1.cjs', 'v49-browser-command.log',
    'v49-browser-command-r2.log', 'v49-browser-command-r3.log',
    'make_v49_local_acceptance.py', 'prepare_v49_checkpoint.py', 'push_v49_main.py',
)
paths.update(BASE + 'publication/' + p for p in pub_names)
paths.update(BASE + p for p in (
    'integration/v49/export_v49_once.py', 'integration/v49/v49-input-preparation.json',
    'integration/v49/v49-build-receipt.json',
    'integration/related-guide-images/input-map.json',
    'integration/related-guide-images-v49/input-map.json',
    'local-audit/preview-reliability/v47-evidence-correction.json',
))
paths.update(BASE + 'publication/v49-screenshots/' + p for p in (
    'alleriawindrunner.jpg-source.png', 'thumb-thebroken.jpg.png', 'aldor-button.png',
))
paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'tests/fixtures/rewardstable_source16').glob('*') if p.is_file())
tracked = {}
for item in subprocess.check_output(['git', 'ls-tree', '-rz', 'HEAD'], cwd=ROOT).split(b'\0'):
    if item:
        meta, name = item.split(b'\t', 1)
        tracked[name.decode()] = meta.split()[2].decode()
changed = []
for name in sorted(paths):
    p = ROOT / name
    assert p.is_file(), name
    assert not set(p.parts) & {'private', 'raw', '__pycache__'}
    data = p.read_bytes()
    assert len(data) < 2 * 1024 * 1024, (name, len(data))
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if tracked.get(name) != blob:
        changed.append(name)
OUT.write_text(json.dumps({'paths': changed, 'receipt': BASE + 'publication/root-v49-staged-hygiene.json',
    'scope': 'Four attributed current community illustrations, exact reward-button image repair, independently reviewed actual browser/tree evidence, prior candidate rejection and v46 publication reconciliation. No raw HTTP, cookies or full scraped source pages.'}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'paths': len(changed), 'bytes': sum((ROOT / p).stat().st_size for p in changed), 'config': OUT.relative_to(ROOT).as_posix()}))

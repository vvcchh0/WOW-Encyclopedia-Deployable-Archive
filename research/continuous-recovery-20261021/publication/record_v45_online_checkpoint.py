"""Record the accepted published checkpoint without rewriting old receipts."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261021'
proof = json.loads((BASE/'publication/root-v45-pages-online-reconciliation.json').read_bytes())
assert proof['accepted'] and proof['accepted_objects'] == 45
path = BASE/'status.json'
state = json.loads(path.read_bytes())
state.update({
    'phase': 'v45_published_v46_ui_and_layout_preparation',
    'current_pages_version': 'v45',
    'current_main_commit': '335cb44f0d92d13503359c4c47134e7a54d20993',
    'current_pages_commit': proof['expected_pages_commit'],
    'latest_pages_acceptance': 'research/continuous-recovery-20261021/publication/root-v45-pages-online-reconciliation.json',
    'pending_related_icons': 0, 'published_related_icon_supplements_this_run': 986,
    'published_related_ui_supplements_this_run': 0,
    'local_worker_current_task': 'eight_talent_points_box_layout_loader',
    'network_worker_current_task': 'archivecraft_exact_four_html_plan_preparation',
    'accepted_talent_box_layout_target_paths': 8,
    'disk_free_latest_bytes': shutil.disk_usage(ROOT).free,
    'updated_utc': datetime.now(timezone.utc).isoformat(),
})
path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
path = BASE/'tasks.json'
tasks = json.loads(path.read_bytes())
for task in tasks['tasks']:
    if task['id'] == 'FINAL':
        task['state'] = 'v45_main_pages_and45_online_objects_accepted_v39_release'
    elif task['id'] == 'BUILD01':
        task['state'] = 'v45_published_v46_six_ui_and_eight_points_box_routes_preparing'
    elif task['id'] == 'NET01':
        task['state'] = 'archivecraft_four_html_plan_preparing_wayback_stop_unchanged'
    elif task['id'] == 'TALENT02':
        task['state'] = '986_related_icons_published_six_ui_and_eight_layout_targets_accepted_pending_export'
path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
path = ROOT/'docs/continuous-recovery-20261021.md'
with path.open('a', encoding='utf-8') as handle:
    handle.write('\n### 07:37–08:07 UTC — v45部署与线上补验\n\n')
    handle.write('main提交`335cb44f`、Pages提交`6b16f914`，GitHub构建完成。首轮45个对象有44个通过；约10.8MB的来源表两次HTTP200传输均在60秒超时。保留失败回执，只对这一对象放宽至180秒，direct一次完整取得并核对通过，共45个对象完成验收。[补验与合并回执](../research/continuous-recovery-20261021/publication/root-v45-pages-online-reconciliation.json)。离线Release仍为v39。\n\n')
    handle.write('下一版准备六张带独立来源说明的后期天赋界面PNG，以及八个到已有2008年同站点数框GIF的兼容映射。九职业六图原型通过；点数框在德鲁伊、战士的初始、加点和重置状态均闭合，八个目标的原捕获日期仍留空。ArchiveCraft成为非图库缺图的新来源线索，先取四份精确百科HTML，再判断是否有可用图片。\n')
print(json.dumps({'recorded': 'v45_online', 'version': 'v45', 'objects': 45}))

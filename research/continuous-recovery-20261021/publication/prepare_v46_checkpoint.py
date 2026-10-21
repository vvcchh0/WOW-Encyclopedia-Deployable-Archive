"""Prepare only changed, reviewed public checkpoint files for v46."""
import hashlib
import io
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE='research/continuous-recovery-20261021/'
PUB=ROOT/BASE/'publication'
OUT=PUB/'v46-stage-config.json'
assert not OUT.exists()
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(PUB/'root-v46-local-acceptance.json')['accepted']
state_path=ROOT/BASE/'status.json';state=read(state_path)
state.update({'phase':'v46_root_accepted_main_sync_and_pages_publication','current_local_version':'v46','candidate_version':'v46','candidate_publication_accepted':True,'latest_local_acceptance':BASE+'publication/root-v46-local-acceptance.json','candidate_review':BASE+'publication/root-v46-local-acceptance.json','talent_missing_after_ui_and_layout':259,'accepted_related_ui_candidates':6,'accepted_talent_box_layout_target_paths':8,'accepted_related_encyclopedia_images':3,'published_related_encyclopedia_images':0,'latest_commoncrawl_content_review':BASE+'publication/root-commoncrawl-pages02-content-acceptance.json','latest_related_encyclopedia_source_acceptance':BASE+'publication/root-archivecraft-images-source-acceptance.json','local_worker_current_task':'three_related_encyclopedia_image_loader','network_worker_current_task':'four_archivecraft_guides_html_acquisition','disk_free_latest_bytes':shutil.disk_usage(ROOT).free,'updated_utc':datetime.now(timezone.utc).isoformat()})
state_path.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
tasks_path=ROOT/BASE/'tasks.json';tasks=read(tasks_path)
for row in tasks['tasks']:
    if row['id']=='BUILD01':row['state']='v46_ui_and_point_box_root_accepted_three_encyclopedia_images_in_preparation'
    if row['id']=='FINAL':row['state']='v46_main_and_pages_publication_pending_v45_online_v39_release'
    if row['id']=='NET01':row['state']='archivecraft_three_images_root_accepted_four_guide_pages_acquiring_wayback_stopped'
tasks_path.write_text(json.dumps(tasks,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc)
history=io.StringIO()
with history as handle:
    handle.write(f'\n### {now:%H:%M} UTC — v46本地验收与百科新图源\n\n')
    handle.write('v46增加六张后期关联来源的天赋PNG界面图，并把八个点数框边框地址映射到已有2008年4月同站GIF。55项受影响检查通过；10,137个文件、629,321,494字节逐项核对通过，既有图片、脚本、天赋数据、SWF和WASM字节保持。九职业实际执行初始、加点、加满首项、单树重置和全部重置，另点击三个打印视图；剩余259个独立缺图目标。两次探针分别因预期措辞过短、把图片角片当作CSS背景而失败；修正探针后通过，站点未改。[本地验收](../research/continuous-recovery-20261021/publication/root-v46-local-acceptance.json)\n\n')
    handle.write('只读脚本盘点：151个非图库外链JS有150个语法通过；奖励页旧Prototype脚本被通用转换损坏，但现有静态展品和全部HTML均不引用它，暂不接回。879份非图库HTML的12,051段内联脚本去重为2,322段，全部语法通过；语法检查未执行页面逻辑。\n\n')
    handle.write('ArchiveCraft的四份百科HTML和四张引用图均由direct取得。高等精灵控制图与已有实体字节相同；Alleria、塞纳里奥议会、玛法里奥三张图经实际查看，准备以注明社区来源的当前关联素材接入。原目标捕获日期留空，Alleria保留WordPress缩放名说明；原百科正文保持。[图源决定](../research/continuous-recovery-20261021/publication/root-related-encyclopedia-image-decision.json)\n\n')
    handle.write('Common Crawl补充三份来源复核完成：RSS九条标题已在五月新闻中，Cenarion指南截断于128KiB且末尾标记未结束，Implemented正文及文章图片与已有来源相同；保留来源，不覆盖现有页面。[复核](../research/continuous-recovery-20261021/publication/root-commoncrawl-pages02-content-acceptance.json)\n')
    history_text=handle.getvalue()
history_path=ROOT/'docs/continuous-recovery-20261021.md'
if 'v46本地验收与百科新图源' not in history_path.read_text(encoding='utf-8'):
    with history_path.open('a',encoding='utf-8') as handle:handle.write(history_text)
detail_path=ROOT/'docs/non-gallery-restoration-20261021.md'
if '## 界面与关联图源补充' not in detail_path.read_text(encoding='utf-8'):
    with detail_path.open('a',encoding='utf-8') as handle:
        handle.write('\n## 界面与关联图源补充\n\nv46本地验收补入三色天赋状态框、Reset、Reset All及Printable Version六张界面图，另复用八片已有同站点数框GIF。九职业加点和重置检查通过，天赋缺图剩259个目标；准备部署。\n\nArchiveCraft提供Alleria、塞纳里奥议会和玛法里奥三幅配图的新线索，当前JPEG已取得并查看，作为单独标注来源的关联补充准备接入。原始目标捕获仍未找到；未导入该站正文、评论、脚本或表单。\n')
paths=['README.md','CHANGELOG.md','docs/continuous-recovery-20261021.md','docs/non-gallery-restoration-20261021.md','tools/export_github_pages.py','tools/related_talent_ui.py','tools/talent_box_layout.py','tests/test_related_talent_ui.py','tests/test_related_talent_ui_pages.py','tests/test_talent_box_layout.py','tests/test_talent_box_layout_pages.py',BASE+'status.json',BASE+'tasks.json']
pub_names=[
    'retry_v45_provenance_online.py','root-v45-pages-online-acceptance.json','v45-provenance-online-retry01.json','root-v45-pages-online-reconciliation.json','record_v45_online_checkpoint.py',
    'prepare_related_talent_ui.py','root-related-talent-ui-integration-decision.json','prepare_talent_box_layout.py','root-talent-box-layout-decision.json',
    'check_v46_code.py','v46-code-tests.log','root-v46-code-acceptance.json','execute_v46_once.py','v46-export-execution.json','v46-export-execution.log','root-v46-export-go.json','accept_v46_tree.py','root-v46-export-acceptance.json','root_v46_browser.cjs','root_v46_browser_attempt1.cjs','root_v46_browser_attempt2.cjs','v46-browser-attempt1.json','v46-browser-attempt2.json','root-v46-browser-acceptance.json','make_v46_local_acceptance.py','root-v46-local-acceptance.json','v46-talent-remaining-targets.json','verify_accepted_pages.py','prepare_v46_checkpoint.py',
    'accept_cc_pages02_sources.py','root-commoncrawl-pages02-content-acceptance.json','accept_archivecraft_pages.py','root-archivecraft-pages-source-acceptance.json','prepare_related_encyclopedia_images.py','root-archivecraft-images-source-acceptance.json','root-related-encyclopedia-image-decision.json',
]
paths += [BASE+'publication/'+p for p in pub_names]
paths += [BASE+p for p in (
    'integration/related-talent-ui/input-map.json','integration/related-talent-ui/prepare-receipt-r2.json',
    'integration/talent-box-layout/input-map.json','integration/talent-box-layout/prepare-receipt.json',
    'integration/v46/export_v46_once.py','integration/v46/v46-input-preparation.json','integration/v46/v46-build-receipt.json',
    'local-audit/talent-box-layout-review/source-date-supplement.json','local-audit/talent-box-layout-review/geometry-evidence.json','local-audit/talent-box-layout-review/review-decision.json',
    'local-audit/js-syntax-pass01/audit_js_syntax.py','local-audit/js-syntax-pass01/inventory.json','local-audit/js-syntax-pass01/syntax-results.json','local-audit/js-syntax-pass01/failure-analysis.json','local-audit/js-syntax-pass01/README.md',
    'local-audit/inline-js-pass01/audit_inline_js.py','local-audit/inline-js-pass01/failure-analysis.json','local-audit/inline-js-pass01/README.md',
    'network/archivecraft-images01/target-correlation.json',
)]
paths += [BASE+'publication/v46-screenshots/'+c+'-max.png' for c in ('druid','hunter','warrior')]
tracked={}
for item in subprocess.check_output(['git','ls-tree','-rz','HEAD'],cwd=ROOT).split(b'\0'):
    if item:
        meta,name=item.split(b'\t',1);tracked[name.decode('utf-8')]=meta.split()[2].decode()
changed=[]
for name in paths:
    path=ROOT/name;assert path.is_file(),name
    assert not set(path.parts)&{'private','raw','__pycache__'}
    data=path.read_bytes()
    cap=3*1024*1024 if name.endswith('/root-v46-browser-acceptance.json') else 2*1024*1024
    assert len(data)<=cap,(name,len(data))
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if tracked.get(name)!=blob:changed.append(name)
assert len(changed)==len(set(changed))
OUT.write_text(json.dumps({'paths':changed,'receipt':BASE+'publication/root-v46-staged-hygiene.json','scope':'Accepted six talent UI PNGs, eight same-site point-box route reuses, v45 online reconciliation, independent source decisions and bounded non-gallery script audits. No raw HTTP, cookies, full scraped HTML or private payloads.'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'paths':len(changed),'bytes':sum((ROOT/p).stat().st_size for p in changed),'configuration':OUT.relative_to(ROOT).as_posix()}))

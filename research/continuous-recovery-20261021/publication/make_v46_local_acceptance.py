"""Bind v46 actual-byte/browser evidence to the exact publication objects."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT/'.scratch/pages-resources-20261021-v46'
OUT = PUB/'root-v46-local-acceptance.json'
assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
tree=read(PUB/'root-v46-export-acceptance.json')
browser=read(PUB/'root-v46-browser-acceptance.json')
assert tree['accepted'] and browser['accepted'] and len(browser['pages'])==9
assert not browser['page_errors'] and not browser['request_failures'] and not browser['external_requests']
assert browser['asset_fulfillments']==0
assert sha(SITE/'export-provenance.json')==tree['export_provenance_sha256']
prior=read(PUB/'root-v45-local-acceptance.json')
prov=read(SITE/'export-provenance.json')
paths={r['path'] for r in prior['objects']}|set(tree['changed_existing_files'])
paths.update(r['output_path'] for r in prov['files'] if r['kind'] in {'related_talent_ui','related_talent_ui_catalog'})
paths.update(r['source_route'].lstrip('/') for r in prov['talent_box_layout_compatibility']['records'])
code=read(PUB/'root-v46-code-acceptance.json')
binding_paths={r['path'] for r in code['code_bindings']}|{
    'research/continuous-recovery-20261021/publication/root-v46-code-acceptance.json',
    'research/continuous-recovery-20261021/publication/root-v46-export-acceptance.json',
    'research/continuous-recovery-20261021/publication/root-v46-browser-acceptance.json',
    'research/continuous-recovery-20261021/publication/root-related-talent-ui-integration-decision.json',
    'research/continuous-recovery-20261021/publication/root-talent-box-layout-decision.json',
    'research/continuous-recovery-20261021/integration/related-talent-ui/input-map.json',
    'research/continuous-recovery-20261021/integration/talent-box-layout/input-map.json',
    'research/continuous-recovery-20261021/publication/verify_accepted_pages.py',
}
missing=set()
for page in browser['pages']:
    missing.update(page['states']['initial']['missing_paths'])
prefix='/WOW-Encyclopedia-Deployable-Archive'
from urllib.parse import urlsplit,unquote
for response in browser['http_errors']:
    path=urlsplit(response['url']).path
    assert path.startswith(prefix+'/')
    missing.add(unquote(path[len(prefix):]))
assert len(missing)==259, len(missing)
gap=PUB/'v46-talent-remaining-targets.json'
assert not gap.exists()
gap.write_text(json.dumps({'version':'v46','distinct_missing_targets':259,'paths':sorted(missing),'scope':'Nine initial talent DOMs plus actual HTTP404 paths; static placeholders and dynamic requests remain separately observable.','previous_v45_count':273,'supplemented_target_paths':14,'original_2008_images_recovered':0},indent=2)+'\n',encoding='utf-8')
binding_paths.add(gap.relative_to(ROOT).as_posix())
gate={'accepted':True,'published':False,'version':'v46','checked_utc':datetime.now(timezone.utc).isoformat(),'local_site':SITE.relative_to(ROOT).as_posix(),'previous_pages_commit':'6b16f9144253974dfb235da37237a6e768e618c7','source_manifest_sha256':prov['source_manifest_sha256'],'export_provenance_sha256':tree['export_provenance_sha256'],'bindings':[{'path':p,'sha256':sha(ROOT/p)} for p in sorted(binding_paths)],'objects':[{'path':p,'sha256':sha(SITE/p),'bytes':(SITE/p).stat().st_size} for p in sorted(paths)],'scope':'Six separately attributed later UI PNGs and eight point-box border routes reusing existing same-site images; nine talent pages retain original data and script bytes.','browser_evidence':{'nine_classes_initial_first_max_reset_reset_all':True,'printable_clicks':3,'parent_screenshots_reviewed':1,'asset_fulfillments':0,'remaining_distinct_missing_targets':259,'probe_corrections':'First probe expected an abbreviated notice phrase; second treated corner img tags as CSS backgrounds. Both failed receipts and runners are retained. The export was unchanged; corrected probe accounts for image corners and background strips.'},'new_original_2008_images':0,'related_talent_icon_objects':986,'new_related_ui_objects':6,'points_box_reused_target_paths':8,'known_gaps':'259 talent image targets still missing, including backgrounds and headings; gallery scope excluded.'}
OUT.write_text(json.dumps(gate,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'version':'v46','online_objects':len(paths),'missing_targets':len(missing),'gate_sha256':sha(OUT)}))

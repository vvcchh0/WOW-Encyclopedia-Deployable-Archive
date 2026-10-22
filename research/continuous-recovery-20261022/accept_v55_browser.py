"""Bind independently reviewed v55 browser and export results for publication."""
from datetime import datetime,timezone
import hashlib,json,mimetypes
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def write(p,d):
 assert not p.exists(),p
 p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
export_path=HERE/'root-v55-export-acceptance.json';export=read(export_path);assert export['accepted']
site=ROOT/export['local_site'];prov=read(site/'export-provenance.json')
assert sha(site/'export-provenance.json')==export['export_provenance_sha256']
v54_path=HERE/'root-v54-browser-acceptance.json';v54=read(v54_path);assert v54['accepted']
run=HERE/'integration/related-talent-icons-v55/implementation/runs/v55-2026-10-22T11-25-38-127Z'
report_path=run/'browser-check.json';report=read(report_path)
assert report['status']=='browser_checks_passed_pending_parent_review'
s=report['summary'];assert s['talent_checks_passed']==s['expected_talent_checks']==10
assert s['mapped_image_routes_exact']==20 and s['original_class_data_routes_exact']==4
for k in ('unexpected_new_errors','mapped_image_errors','external_requests_aborted','page_errors'):assert s[k]==0,k
for r in report['talent_checks']:
 assert r['status']=='passed' and r['allocation']['final_rank']==1 and r['save_reload']['ranks_preserved']
 assert r['save_reload']['exact_saved_digits'] and r['save_reload']['tree_points_preserved']
 assert r['original_data']['page_data_sha256']==r['old_data_sha256']
visual=[run/p for p in ('paladin-improved-concentration-aura-on.png','hunter-readiness-on.png','rogue-relentless-strikes-on.png','warrior-sweeping-strikes-on.png')]
evidence=[export_path,v54_path,report_path,run.parents[1]/'browser-check.cjs']+visual
pages=list(v54['pages'])
result={'schema':'wow-root-final-browser-acceptance/v1','accepted':True,'version':'v55','checked_utc':datetime.now(timezone.utc).isoformat(),
 'local_site':export['local_site'],'export_provenance_sha256':export['export_provenance_sha256'],'pages':pages,
 'external_requests':[],'page_errors':[],'asset_fulfillments':0,
 'evidence':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in evidence],
 'manual_visual_files':[p.relative_to(ROOT).as_posix() for p in visual],
 'new_talent_mappings_verified':20,'talents_legally_allocated_and_reloaded':10,
 'retained_v54_checks':{'arrows':18,'faction_icons':3,'reward_states':51,'reason':'All faction pages/data/images and selected arrow bytes are unchanged; runtime logic is unchanged apart from twenty additional talent-image routes.'},
 'browser_harness_corrections':['Count all nine classes in the retained 986-image base bundle.','Check original current and Next Rank tooltip text; compare all non-whitespace characters across table/linebreak formatting.','Use the requested missing-image target, rather than its referring source page, for the pinned baseline classification.'],
 'known_baseline_missing_observations':s['known_baseline_missing_observations'],'original_2008_images_recovered_this_version':0}
write(HERE/'root-v55-browser-acceptance.json',result)
baseline=read(HERE/'v53-known-missing-targets.json');routes=read(site/'__offline/route-map.json')['routes']
resolved=[p for p in baseline['targets'] if p in routes];unresolved=[p for p in baseline['targets'] if p not in routes]
assert len(resolved)==41 and len(unresolved)==349
write(HERE/'v55-remaining-resource-targets.json',{'schema':'wow-bounded-remaining-resource-targets/v1','version':'v55','scope':'The previously selected v53 set of 390 non-gallery local resource targets; excludes the separately investigated player-gallery originals/previews.','prior_inventory_sha256':sha(HERE/'v53-known-missing-targets.json'),'resolved_count':len(resolved),'resolved':resolved,'remaining_count':len(unresolved),'remaining':unresolved})
smoke={r['path'] for r in export['online_changes_from_v53']}
smoke.update(('index.html','info/encyclopedia/index.xml.html','info/basics/dungeons.html','__offline/flash-exhibits.js','__offline/vendor/ruffle/ruffle.js'))
smoke.update('shared/global/talents/'+c+'/data.js' for c in ('hunter','paladin','rogue','warrior'))
smoke.update(r['path'] for r in prov['flash_exhibits']['original_swfs'].values())
smoke.update(r['output_path'] for r in prov['flash_exhibits']['files'] if r['output_path'].endswith('.wasm'))
smoke.update(p.relative_to(site).as_posix() for p in (site/'screenshots/images/basics/dungeons').glob('*.jpg'))
def mime(p):
 value=mimetypes.guess_type(p)[0] or 'application/octet-stream'
 if value.startswith('text/') or Path(p).suffix in ('.js','.json'):value+='; charset=utf-8'
 return value
config={'schema':'wow-portable-check-config/v1','version':'v55','accepted_site':export['local_site'],
 'archive':'artifacts/WOW_Encyclopedia_20080512_browser_20261022_v55.zip',
 'package_report':'research/continuous-recovery-20261022/publication/v55-portable-package-report.json',
 'export':{'path':export_path.relative_to(ROOT).as_posix()},'root_browser_acceptance':{'path':'research/continuous-recovery-20261022/root-v55-browser-acceptance.json'},
 'output_receipt':'research/continuous-recovery-20261022/publication/v55-portable-acceptance.json',
 'smoke_paths':[{'url_path':prov['base_path']+quote(p,safe='/'),'site_relative':p,'expected_mime':mime(p),'methods':['GET','HEAD']} for p in sorted(smoke)]}
assert all((site/r['site_relative']).is_file() for r in config['smoke_paths'])
write(HERE/'publication/v55-portable-config.json',config)
print(json.dumps({'accepted':True,'talents':10,'new_icons':20,'remaining_bounded_targets':349,'portable_smoke_paths':len(smoke)}))

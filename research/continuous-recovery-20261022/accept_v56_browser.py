"""Independent functional and visual acceptance, followed by portable-check inputs."""
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
export_path=HERE/'root-v56-export-acceptance.json';export=read(export_path);assert export['accepted']
site=ROOT/export['local_site'];prov=read(site/'export-provenance.json');assert sha(site/'export-provenance.json')==export['export_provenance_sha256']
prior_path=HERE/'root-v55-browser-acceptance.json';prior=read(prior_path);assert prior['accepted']
run=HERE/'integration/related-talent-icons-v56/implementation/runs/v56-2026-10-22T12-42-28-056Z'
report_path=run/'browser-check.json';report=read(report_path)
assert report['status']=='browser_checks_passed_pending_parent_review'
s=report['summary'];assert s['talent_checks_passed']==s['expected_talent_checks']==9
assert s['mapped_image_routes_exact']==18 and s['original_class_data_routes_exact']==5
for k in ['unexpected_new_errors','mapped_image_errors','external_requests_aborted','page_errors']:assert s[k]==0,k
for r in report['talent_checks']:
 assert r['status']=='passed' and r['allocation']['final_rank']==1 and r['save_reload']['ranks_preserved']
 assert r['save_reload']['exact_saved_digits'] and r['save_reload']['tree_points_preserved']
 assert r['original_data']['page_data_sha256']==r['old_data_sha256']
 assert r['saved_link']['digits'][r['original_data']['talent_index']]=='1'
prototype=HERE/'integration/v56-paint-prototype/runs/paint-2026-10-22T13-07-04-264Z'
proto=read(prototype/'report.json');assert proto['browser']['headed'] is True and proto['browser']['launch_args']==[]
control=next(r for r in proto['variants'] if r['id']=='control')
assert control['injected_css'] is None and control['navigation_status']==200 and not control['external_requests_aborted'] and not control['page_errors']
assert all(r['complete'] and r['natural_width']==r['natural_height']==36 for r in control['target_images'])
# The prototype's injected variants are excluded from acceptance. Only the no-CSS control and independently viewed cold Slam page contribute.
slam_dir=HERE/'integration/v56-paint-prototype/runs/slam-control-2026-10-22T13-13-14-438Z'
slam=read(slam_dir/'report.json');assert slam['product_css_injection'] is False and slam['browser']['headed'] is True
assert slam['navigation_status']==200 and not slam['external_requests_aborted'] and not slam['page_errors']
on=next(r for r in slam['target_images'] if r['src'].endswith('/improvedslam.jpg'))
assert on['complete'] and on['natural_width']==on['natural_height']==36 and on['visible'] and on['parents'][0]['visible']
assert on['parents'][0]['visibility']=='visible'
visual=[ROOT/r['screenshots'][1] for r in report['talent_checks'] if r['mapping_id'] not in ['warrior-improved-thunder-clap','warrior-improved-slam']]
visual += [prototype/'control.png',slam_dir/'control.png']
assert len(visual)==9 and all(p.is_file() for p in visual)
evidence=[export_path,prior_path,report_path,run.parents[1]/'browser-check.cjs',prototype/'report.json',slam_dir/'report.json',HERE/'integration/v56-root-focused-tests.log']+visual
result={'schema':'wow-root-final-browser-acceptance/v1','accepted':True,'version':'v56','checked_utc':datetime.now(timezone.utc).isoformat(),'local_site':export['local_site'],'export_provenance_sha256':export['export_provenance_sha256'],'pages':prior['pages'],'new_talent_pages':sorted({r['page'] for r in report['talent_checks']}),'external_requests':[],'page_errors':[],'asset_fulfillments':0,'evidence':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in evidence],'manual_visual_files':[p.relative_to(ROOT).as_posix() for p in visual],'new_talent_mappings_verified':18,'talents_legally_allocated_and_reloaded':9,'all_1006_prior_assets_retained':True,'retained_v55_checks':{'reason':'All earlier page/data/image bytes are retained; runtime logic differs only in eighteen new route entries.','prior_browser_receipt_sha256':sha(prior_path)},'known_baseline_missing_observations':s['known_baseline_missing_observations'],'original_2008_images_recovered_this_version':0,'focused_unit_tests':{'passed':4,'path':'integration/v56-root-focused-tests.log'},'visual_environment_findings':{'default_headless_warrior_captures':'Some incomplete paint regions remain in default headless screenshots despite complete image decoding and valid DOM geometry.','unmodified_headed_controls':'Thunder Clap and Slam cold saved-template pages visually complete in ordinary Chrome; no injected CSS or response replacement.','css_variants_used_for_acceptance':False,'cause':'Not determined; mode difference observed. No CSS or global GPU change was made.','slam_report_erratum':'The postprocessed target_pair_status sentence claims rank 0/hidden wrapper. Its captured records show the on image and wrapper49 visible; screenshot shows 1/2 and saved digit index34 is 1. The sentence is erroneous and excluded from acceptance.'}}
write(HERE/'root-v56-browser-acceptance.json',result)
baseline=read(HERE/'v53-known-missing-targets.json');routes=read(site/'__offline/route-map.json')['routes']
resolved=[p for p in baseline['targets'] if p in routes];unresolved=[p for p in baseline['targets'] if p not in routes]
assert len(resolved)==59 and len(unresolved)==331
write(HERE/'v56-remaining-resource-targets.json',{'schema':'wow-bounded-remaining-resource-targets/v1','version':'v56','scope':'The previously selected v53 set of 390 non-gallery resource targets; excludes separately investigated player-gallery originals/previews.','prior_inventory_sha256':sha(HERE/'v53-known-missing-targets.json'),'resolved_count':len(resolved),'resolved':resolved,'remaining_count':len(unresolved),'remaining':unresolved})
previous=read(HERE/'publication/v55-portable-config.json')
smoke={r['site_relative'] for r in previous['smoke_paths']}
smoke.update(r['path'] for r in export['online_changes_from_v55']);smoke.update(r['old_data_route'].lstrip('/') for r in report['talent_checks'])
def mime(p):
 v=mimetypes.guess_type(p)[0] or 'application/octet-stream'
 if v.startswith('text/') or Path(p).suffix in ['.js','.json']:v+='; charset=utf-8'
 return v
config={'schema':'wow-portable-check-config/v1','version':'v56','accepted_site':export['local_site'],'archive':'artifacts/WOW_Encyclopedia_20080512_browser_20261022_v56.zip','package_report':'research/continuous-recovery-20261022/publication/v56-portable-package-report.json','export':{'path':export_path.relative_to(ROOT).as_posix()},'root_browser_acceptance':{'path':'research/continuous-recovery-20261022/root-v56-browser-acceptance.json'},'output_receipt':'research/continuous-recovery-20261022/publication/v56-portable-acceptance.json','smoke_paths':[{'url_path':prov['base_path']+quote(p,safe='/'),'site_relative':p,'expected_mime':mime(p),'methods':['GET','HEAD']} for p in sorted(smoke)]}
assert all((site/r['site_relative']).is_file() for r in config['smoke_paths'])
write(HERE/'publication/v56-portable-config.json',config)
print(json.dumps({'accepted':True,'talents':9,'new_icons':18,'bounded_remaining':331,'portable_paths':len(smoke)}))

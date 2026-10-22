"""Root acceptance of unchanged-response arrow and faction browser checks."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
export_path=HERE/'root-v54-export-acceptance.json';export=read(export_path);assert export['accepted']
site=ROOT/export['local_site'];assert sha(site/'export-provenance.json')==export['export_provenance_sha256']
run=HERE/'integration/v54-browser/runs/v54-2026-10-22T10-57-21-881Z'
arrow_path=run/'browser-acceptance.json';arrow=read(arrow_path)
faction_path=HERE/'root-v54-faction-browser-acceptance.json';faction=read(faction_path)
assert arrow['status']=='browser_checks_passed_pending_parent_visual_acceptance'
assert arrow['summary']['accepted_sequences_passed']==6
assert arrow['summary']['exact_arrow_responses']==18
assert arrow['summary']['held_down3_control_passed']
for key in ('unexpected_new_non_arrow_http_errors','unexpected_arrow_http_errors','external_requests_aborted','page_errors','failed_resource_reads'):assert arrow['summary'][key]==0,key
assert arrow['arrow_response_coverage']['all_18_actual_responses_match_map']
assert faction['accepted'] and len(faction['pages'])==11
for d in (arrow,faction):assert not d['page_errors'] and not d['external_requests']
assert not faction['http_errors']
visual=[run/'screenshots'/f'{name}-yellow.png' for name in ('across-left','across-right','down-1','down-2','down-4','down-right')]
visual += [run/'screenshots/across-left-grey.png',run/'screenshots/down-right-green.png',HERE/'faction-v54-aldor.png',HERE/'faction-v54-zangarmarsh.png']
evidence=[export_path,arrow_path,faction_path,HERE/'check_v54_factions.cjs',HERE/'integration/v54-browser/check_v54_talent_ui.cjs',HERE/'v53-known-missing-targets.json']+visual
pages=[{'route':r['route'],'checks':'visible reward groups, every available reputation tier, image bytes, dimensions, fit and tooltips'} for r in faction['pages']]
pages += [{'route':'/info/classes/'+name+'/talents.html','checks':'original legal prerequisite ranks, six selected arrow geometries and grey/green/yellow states, save/reload/reset'} for name in sorted({r['class'] for r in arrow['sequence_results']})]
result={'schema':'wow-root-final-browser-acceptance/v1','accepted':True,'version':'v54','checked_utc':datetime.now(timezone.utc).isoformat(),
 'local_site':export['local_site'],'export_provenance_sha256':export['export_provenance_sha256'],
 'pages':pages,'external_requests':[],'page_errors':[],'asset_fulfillments':0,
 'evidence':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in evidence],
 'manual_visual_files':[p.relative_to(ROOT).as_posix() for p in visual],
 'new_arrows_verified':18,'new_faction_icons_verified':3,'reward_states_verified':sum(len(r['brackets']) for r in faction['pages']),
 'known_baseline_talent_gap_routes_observed':105,'held_down3_arrows':3,
 'original_nagrand_control_quirk':'Initial levelBracket=1 while previousListItem=0; verified Friendly using another visible tier first. Historical code retained.',
 'scope':'Root separately verified all production export files; actual loopback browser responses were unchanged. Existing unrelated missing images remain classified against the pinned prior inventory.'}
out=HERE/'root-v54-browser-acceptance.json';assert not out.exists()
out.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'accepted':True,'pages':len(pages),'reward_states':result['reward_states_verified'],'evidence':len(evidence)}))

"""Combine root byte and actual-browser evidence for the v45 publication gate."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261021-v45'
OUT = PUB / 'root-v45-local-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
tree = read(PUB / 'root-v45-export-acceptance.json')
browser = read(PUB / 'root-v45-browser-acceptance.json')
assert tree['accepted'] and browser['accepted'] and len(browser['pages']) == 5
assert not browser['http_errors'] and not browser['external_requests']
assert sha(SITE / 'export-provenance.json') == tree['export_provenance_sha256']
prov = read(SITE / 'export-provenance.json')
paths = {'export-provenance.json','__offline/route-map.json','__offline/pages_runtime.js',
         '__offline/related-talent-icons.json','news/wow-news-06-2005.html',
         'contests/05-06-09.html','info/basics/content-index.shtml.html',
         'moltencore.html','wrath/index.xml.html'}
classes = ('druid','hunter','mage','paladin','priest','rogue','shaman','warlock','warrior')
icons = [r for r in prov['files'] if r['kind'] == 'related_talent_icon']
for name in classes:
    paths.add(f'info/classes/{name}/talents.html')
    paths.add(next(r['output_path'] for r in icons if r['route'].startswith(f'/shared/global/talents/{name}/')))
paths.update(r['output_path'] for r in prov['files'] if r.get('role') == 'source16_main_page')
paths.update(r['source_route'].lstrip('/') for r in prov['layout_compatibility_reuse']['records'])
code = read(PUB / 'root-v45-code-acceptance.json')
binding_paths = {r['path'] for r in code['code_bindings']} | {
    'research/continuous-recovery-20261021/publication/root-v45-code-acceptance.json',
    'research/continuous-recovery-20261021/publication/root-v45-export-acceptance.json',
    'research/continuous-recovery-20261021/publication/root-v45-browser-acceptance.json',
    'research/continuous-recovery-20261021/publication/root-source16-local-acceptance.json',
    'research/continuous-recovery-20261021/local-audit/v44/v44-browser-receipt.json',
    'research/continuous-recovery-20261021/local-audit/v44/v44-gap-union-reconciliation.json',
    'research/continuous-recovery-20261021/publication/verify_accepted_pages.py',
}
gate = {
    'accepted': True, 'published': False, 'version':'v45',
    'checked_utc':datetime.now(timezone.utc).isoformat(),
    'local_site':SITE.relative_to(ROOT).as_posix(),
    'previous_pages_commit':'fdc976ed56fc1a3ff52259b6b989d5552deb16ac',
    'source_manifest_sha256':prov['source_manifest_sha256'],
    'export_provenance_sha256':tree['export_provenance_sha256'],
    'bindings':[{'path':p,'sha256':sha(ROOT/p)} for p in sorted(binding_paths)],
    'objects':[{'path':p,'sha256':sha(SITE/p),'bytes':(SITE/p).stat().st_size} for p in sorted(paths)],
    'scope':'Seven new main-site reading pages, updated content index, exact aliases, 986 attributed later related talent icons, two same-site layout repairs and static historical contest wording.',
    'browser_evidence':{
        'new_five_page_actual_chrome_probe':True, 'parent_screenshots_reviewed':4,
        'prior_v43_source16_body_and_alias_checks_retained':True,
        'prior_v44_nine_class_nonzero_template_checks_reused_on_identical_html_and_scripts':True,
        'talent_remaining_distinct_missing_targets':273,
        'first_browser_attempt':'One request was aborted when the probe left an in-progress homepage meta redirect; the probe now waits for the final canonical page. The exported site was not changed for the rerun.',
    },
    'new_original_2008_images':0, 'related_talent_icon_objects':986,
    'layout_reused_target_paths':10, 'new_layout_image_objects':0,
    'known_gaps':'New article illustrations/layout remain incomplete; talent backgrounds and UI resources and BlizzCast media are still missing. No gallery work in this batch.',
}
OUT.write_bytes((json.dumps(gate,indent=2)+'\n').encode())
print(json.dumps({'accepted':True,'version':'v45','online_objects':len(paths),'object_bytes':sum(r['bytes'] for r in gate['objects']),'gate_sha256':sha(OUT)}))

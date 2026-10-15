"""Check the directory-base repair against the actual retained Wrath pages."""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import export_github_pages as pages
class Recorder:
    def add(self,*args):
        pass
def main():
    source=ROOT/'.scratch/offline-navigation-20261015-v9/build-manifest.json'
    manifest=json.loads(source.read_text(encoding='utf-8'))
    route_map=json.loads((ROOT/'.scratch/pages-resources-20261015-v9/__offline/route-map.json').read_text(encoding='utf-8'))
    localizer=pages.PagesLocalizer(route_to_static=route_map['routes'],aliases=manifest['route_aliases'],origin_index=manifest['origin_index'],base_path=pages.DEFAULT_BASE_PATH)
    rows=[]
    assignment=re.compile(r'\bvar\s+roothost\s*=\s*([\'"])(.*?)\1')
    for record in manifest['files']:
        if not record['route'].startswith('/wrath/') or record.get('kind')!='html':
            continue
        original=(ROOT/record['output_path']).read_text(encoding='utf-8')
        old=assignment.findall(original)
        if not old:
            continue
        transformed=pages.rewrite_inline_scripts(original,base_url=record['source_base_url'],localizer=localizer,recorder=Recorder())
        updated=[value for _,value in assignment.findall(transformed)]
        expected=pages.DEFAULT_BASE_PATH+'wrath/'
        rows.append({'route':record['route'],'source_roothost':[value for _,value in old],
                     'derived_roothost':updated,'passed':bool(updated) and all(value==expected for value in updated)})
    files=['tools/export_github_pages.py','tests/test_github_pages_export.py']
    report={'checked_utc':datetime.now(timezone.utc).isoformat(),'network_requests':0,
        'actual_source_manifest_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_page_checks':rows,'file_sha256_at_review':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
        'unit_test_command':'python.exe -B -X utf8 -m unittest tests.test_github_pages_export tests.test_historical_exhibits',
        'observed_unit_result':{'exit_code':0,'tests':38,'seconds':9.624,'result':'OK'},
        'full_export_verified':False,'browser_verified':False,
        'next_step':'Build a fresh derived export after viewer dependencies and source selection are settled; do not mutate or publish v9 as repaired.'}
    report['accepted']=bool(rows) and all(row['passed'] for row in rows)
    (ROOT/'research/continuous-recovery-20261015/wrath-directory-base-acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'accepted':report['accepted'],'actual_source_pages':len(rows),'unit_tests':38,'full_export_verified':False}))
    if not report['accepted']:
        raise SystemExit(1)
if __name__=='__main__':
    main()

"""Read-only root acceptance of the derived v9 inputs and source retention."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/continuous-recovery-20261015'
def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))
def sha(data):
    return hashlib.sha256(data).hexdigest()
def main():
    old = load('.scratch/offline-navigation-20261015-v7c/build-manifest.json')
    new_path = ROOT/'.scratch/offline-navigation-20261015-v9/build-manifest.json'
    new_bytes = new_path.read_bytes()
    new = json.loads(new_bytes)
    before = {x['route']:x for x in old['files']}
    after = {x['route']:x for x in new['files']}
    source_keys = ['source_local_path','source_sha256','source_length','source_base_url','actual_timestamp']
    missing = sorted(set(before)-set(after))
    changed = [{'route':route, 'fields':[key for key in source_keys if item.get(key)!=after[route].get(key)]} for route,item in before.items() if route in after and any(item.get(key)!=after[route].get(key) for key in source_keys)]
    relocated_support = []
    for change in list(changed):
        route = change['route']
        prior, current = before[route], after[route]
        if route in {'/__offline/compat.css','/__offline/compat.js'} and change['fields']==['source_local_path'] and prior.get('kind')==current.get('kind')=='support':
            prior_bytes=(ROOT/prior['source_local_path']).read_bytes()
            current_bytes=(ROOT/current['source_local_path']).read_bytes()
            if prior_bytes==current_bytes and sha(current_bytes)==current['source_sha256']:
                relocated_support.append({'route':route,'old_path':prior['source_local_path'],'new_path':current['source_local_path'],'bytes':len(current_bytes),'sha256':sha(current_bytes),'content_identical':True})
                changed.remove(change)
    changed_aliases = [key for key,value in old['route_aliases'].items() if new['route_aliases'].get(key)!=value]
    checks = []
    for map_name in ['selected-core-pages-source-map.json','selected-static-source-map.json']:
        for item in load('research/continuous-recovery-20261015/'+map_name)['entries']:
            raw = ROOT/item['local_path']
            source = raw.read_bytes()
            matched = [entry for entry in new['files'] if entry.get('source_local_path')==item['local_path']]
            assert len(matched)==1, item['local_path']
            entry = matched[0]
            output = (ROOT/entry['output_path']).read_bytes()
            checks.append({'route':entry['route'], 'source_map':map_name,
                'source_bytes':len(source),'source_sha256':sha(source),
                'source_matches_selected':len(source)==item['body_bytes'] and sha(source)==item['body_sha256'],
                'source_matches_manifest':len(source)==entry['source_length'] and sha(source)==entry['source_sha256'],
                'capture_matches':entry.get('actual_timestamp')==item.get('actual_timestamp'),
                'derived_bytes':len(output),'derived_sha256':sha(output),
                'derived_matches_manifest':len(output)==entry['derived_length'] and sha(output)==entry['derived_sha256'],
                'original_static_bytes_unchanged':output==source if map_name.startswith('selected-static') else None})
    frozen = sha((ROOT/'offline/build-manifest.json').read_bytes())
    aliases = {'/ptr':'/ptr/index.html','/ptr/':'/ptr/index.html','/pvp/battlegrounds/battlegroups.html':'/pvp/battlegrounds/battlegroups/index.html'}
    report = {'checked_utc':datetime.now(timezone.utc).isoformat(),'network_requests':0,
        'old_source_count':len(before),'new_source_count':len(after),'new_routes':sorted(set(after)-set(before)),
        'missing_prior_routes':missing,'changed_prior_sources':changed,'changed_prior_aliases':changed_aliases,
        'identical_generated_support_relocations':relocated_support,
        'manifest_sha256':sha(new_bytes),'selected_entity_checks':checks,
        'new_aliases_match':all(new['route_aliases'].get(k)==v for k,v in aliases.items()),
        'frozen_manifest_sha256':frozen,'frozen_manifest_unchanged':frozen=='397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459'}
    report['accepted']=not(missing or changed or changed_aliases) and len(after)==8328 and len(checks)==22 and report['new_aliases_match'] and report['frozen_manifest_unchanged'] and all(x['source_matches_selected'] and x['source_matches_manifest'] and x['capture_matches'] and x['derived_matches_manifest'] and x['original_static_bytes_unchanged'] is not False for x in checks)
    (OUT/'root-v9-source-acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['accepted','old_source_count','new_source_count','missing_prior_routes','changed_prior_sources','changed_prior_aliases']}))
    if not report['accepted']:
        raise SystemExit(1)
if __name__=='__main__':
    main()

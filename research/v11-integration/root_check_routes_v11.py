import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path.cwd(); OUT=ROOT/'research/v11-integration'
oldsite=ROOT/'.scratch/pages-resources-20261015-v10'; site=ROOT/'.scratch/pages-resources-20261015-v11'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    prior=json.loads((ROOT/'research/v10-integration/root-sidebar-check.json').read_bytes())
    a_bytes=(oldsite/'__offline/route-map.json').read_bytes(); a=json.loads(a_bytes)
    b_bytes=(site/'__offline/route-map.json').read_bytes(); b=json.loads(b_bytes)
    provenance_bytes=(site/'export-provenance.json').read_bytes(); p=json.loads(provenance_bytes)
    accepted=json.loads((OUT/'root-export-acceptance.json').read_bytes())
    files={x['output_path']:x for x in p['files']}; prefix=b['base_path']
    checks={'prior_sidebar_accepted':prior['accepted'],'prior_route_map_bound':sha(a_bytes)==prior['route_map_sha256'],'current_full_export_accepted':accepted['accepted'] and sha(provenance_bytes)==accepted['export_provenance_sha256'],'prefix_unchanged':prefix==a['base_path'],'all_prior_routes_identical':all(b['routes'].get(k)==v for k,v in a['routes'].items()),'all_prior_aliases_identical':b['aliases']==a['aliases']}
    expected={'/news/newsarchive.css','/news/images/08-01/01-10-08-01.jpg','/news/images/08-02/arenatourney2.gif'}
    checks['only_three_added_routes']=set(b['routes'])-set(a['routes'])==expected
    checks['all_resolved_sidebar_files_declared']=all(x.get('output_path') in files for x in prior['records'] if x['status']=='resolved')
    r={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':all(checks.values()),'checks':checks,'prior_sidebar_sha256':sha((ROOT/'research/v10-integration/root-sidebar-check.json').read_bytes()),'route_map_sha256':sha(b_bytes),'scope':'All route/alias entries compared; published v10 menu identities and counts reused because every prior route target is identical. Current actual object bytes are checked by root-export-acceptance.','observation_count':prior['observation_count'],'effective_in_scope':prior['effective_in_scope'],'status_counts':prior['status_counts'],'remaining_missing_distinct_routes':prior['remaining_missing_distinct_routes'],'added_routes':sorted(expected),'new_sidebar_pages':0,'network_requests':0}
    (OUT/'root-sidebar-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r));assert r['accepted']
if __name__=='__main__':main()

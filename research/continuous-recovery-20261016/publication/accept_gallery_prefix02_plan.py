"""Root offline gate for ten observed gallery directory queries."""
import hashlib,importlib.util,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
R=Path(__file__).resolve().parents[3]
B=R/'research/continuous-recovery-20261016'
P=B/'network/gallery-prefix02-plan/plan.json'
D=B/'network/driver-v3/gallery_prefix_driver_v3.py'
EXPECTED_PLAN='2fba52ac3993db36b0bc3a2a64446c2ee82189566d7399d65782d3f6a05ad208'
EXPECTED_DRIVER='d7d86cbd86f783da76a738cd301106d91797bd022122d00a2f95670fd197929c'

def main():
    assert hashlib.sha256(P.read_bytes()).hexdigest()==EXPECTED_PLAN
    assert hashlib.sha256(D.read_bytes()).hexdigest()==EXPECTED_DRIVER
    p=json.loads(P.read_bytes())
    prior=json.loads((B/'network/gallery-prefix01/batch-report.json').read_bytes())
    assert prior['failure_streak']==p['inherited_state']['new_batch_streak_start']==2
    assert len(p['candidates'])==10 and p['expected_direct_entities']==622
    excluded={c['prefix'] for c in prior['candidate_results']}
    for c in p['candidates']:
        assert c['prefix'] not in excluded
        s=c['source_page'];data=(R/s['path']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==s['sha256']
        lines=data.decode('utf-8').splitlines()
        assert s['addshots_literal'] in lines[s['addshots_line']-1]
        assert s['numShots_literal'] in lines[s['numShots_line']-1]
        assert s['source_directory']==c['source_directory'] and c['prefix']=='http://www.worldofwarcraft.com'+c['source_directory']
        q=parse_qs(urlsplit(c['cdx_query_url']).query)
        assert q=={k:[str(v)] for k,v in c['query_parameters'].items()}
        assert q['url']==[c['prefix']] and q['limit']==['500'] and 'collapse' not in q
        assert q['from']==['20060101000000'] and q['to']==['20080512210044']
    spec=importlib.util.spec_from_file_location('root_gallery_v3_plan_gate',D)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.validate_inputs()
    fixture=module.fixture()
    assert fixture['all_passed'] and fixture['passed']==fixture['total']==14
    assert fixture['network_requests']==0
    free=shutil.disk_usage(R).free;assert free>=11005853696
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_authorized':True,
            'plan_sha256':EXPECTED_PLAN,'driver_sha256':EXPECTED_DRIVER,'candidate_count':10,
            'expected_direct_entities':622,'independent_fixture_checks':14,'fixture_network_requests':0,
            'inherited_failure_streak':2,'disk_free_bytes':free,'limits':p['policy'],
            'scope':'Exactly ten query URLs; index only, no continuation, no payload replay. Distinct-origin rows may be reported but do not add queries.',
            'completion':'Return after this batch; root acceptance is required before further requests.'}
    (B/'publication/root-gallery-prefix02-plan-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k!='limits'}))

if __name__=='__main__':main()

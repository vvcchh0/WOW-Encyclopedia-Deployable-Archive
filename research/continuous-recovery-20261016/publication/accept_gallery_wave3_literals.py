"""Check fifty source declarations and derive absolute-origin prefix candidates."""
import hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode,urlsplit,parse_qs
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016'
D=B/'local-audit/gallery-prefix-registry-wave3';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    registry=json.loads((B/'local-audit/gallery-prefix-registry/gallery-prefix-registry.json').read_bytes())
    coverage=json.loads((D/'gallery-prefix-registry-wave3-coverage-v1.json').read_bytes())
    draft=json.loads((D/'gallery-prefix-registry-wave3-plan-v1.json').read_bytes())
    rows=coverage['coverage_rows'];originals={r['gallery']:r for r in registry['rows']}
    assert len(rows)==len(originals)==50 and sum(r['declared_slots'] for r in rows)==1684
    assert sum(r['expected_direct_entities'] for r in rows)==3368
    for r in rows:
        e=r['source_evidence'];raw=(R/e['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256']
        lines=raw.decode('utf-8',errors='replace').splitlines()
        assert e['addshots_literal'] in lines[e['addshots_line']-1]
        assert e['numShots_literal'] in lines[e['numShots_line']-1]
        assert e['numShots']==r['declared_slots']==originals[r['gallery']]['declared_slots']
        assert e['directory_literal'] in e['addshots_literal'] and e['origin_host']=='www.worldofwarcraft.com'
    counts=Counter(r['coverage_class'] for r in rows)
    assert counts['reviewed_window_complete']==24
    assert len(coverage['uncovered_groups'])==26
    candidates=[]
    for c in draft['candidates']:
        e=c['source_page'];prefix='http://www.worldofwarcraft.com'+e['directory_literal']
        assert prefix.startswith('http://www.worldofwarcraft.com/') and e['directory_literal'].startswith('/')
        q={'url':prefix,'matchType':'prefix','output':'json','fl':'urlkey,timestamp,original,mimetype,statuscode,digest,length','from':'20000101000000','to':'20080512210044','limit':'500','showResumeKey':'true'}
        candidates.append({'target_key':c['target_key'],'label':c['label'],'prefix':prefix,'source_evidence':e,'declared_slots':c['declared_slots'],'query_url':'https://web.archive.org/cdx/search/cdx?'+urlencode(q)})
    assert len(candidates)==len({x['prefix'] for x in candidates})==20
    result={'schema':'wow-recovery.root.gallery-wave3-literal-plan.v1','checked_utc':datetime.now(timezone.utc).isoformat(),'accepted_as_literal_plan':True,'network_authorized_by_this_file':False,'source_draft_sha256':sha(D/'gallery-prefix-registry-wave3-plan-v1.json'),'coverage_sha256':sha(D/'gallery-prefix-registry-wave3-coverage-v1.json'),'conservation':{'groups':50,'slots':1684,'entities':3368},'reviewed_limited_windows':24,'remaining_including_transport_unknown':26,'correction':'Draft CDX url parameters were relative paths. This derived plan binds the explicit HTTP origin. No requests used the draft.','policy':{'max_attempts':40,'window_seconds':900,'max_total_body_bytes':67108864,'max_entity_body_bytes':8388608,'prefix_only':True,'payload_replay':False,'from':'20000101000000','to':'20080512210044','limit':500,'showResumeKey':True,'collapse':False,'min_dispatch_seconds':5.25,'min_request_start_seconds':5.0,'disk_floor_bytes':11005853696},'candidates':candidates,'scope':'Source literals and inventory conservation accepted. Detailed coverage windows remain bound to prior actual receipts; full historical coverage is not inferred.'}
    (B/'publication/root-gallery-wave3-literal-plan.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({'accepted':True,'groups':50,'candidates':20,'relative_prefixes_corrected':20}))
if __name__=='__main__':main()

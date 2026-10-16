"""Root source/interval acceptance of the final fifty-gallery registry."""
import hashlib,json
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';O=B/'publication';P=B/'local-audit/gallery-final-v7/gallery-prefix-registry-v7.json';V6=B/'local-audit/gallery-prefix-registry-v6/gallery-prefix-registry-v6.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dt=lambda s:datetime.strptime(s,'%Y%m%d%H%M%S')
def main():
    out=O/'root-gallery-registry-v7-acceptance.json';assert not out.exists();d=json.loads(P.read_bytes());old=json.loads(V6.read_bytes());a=d['coverage_rows'];prior={x['registry_rank']:x for x in old['coverage_rows']};assert len(a)==50 and len(prior)==50
    for v in d['input_hashes'].values():assert sha(R/v['path'])==v['sha256']
    slots=0;entities=0;counts=Counter();verified=[];resolved=[]
    for x in a:
        y=prior[x['registry_rank']]
        for k in ['registry_rank','gallery','category','source_page_route','declared_slots','expected_direct_entities','source_evidence','entity_audit_status_counts']:assert x[k]==y[k],(x['gallery'],k)
        source=x['source_evidence'];p=R/source['path'];assert sha(p)==source['sha256'];lines=p.read_text(encoding='iso-8859-1').splitlines();assert source['addshots_literal'] in lines[source['addshots_line']-1] and source['numShots_literal'] in lines[source['numShots_line']-1]
        intervals=[z['window'] for z in x['actual_prefix_windows'] if z.get('complete_prefix_evidence')]
        early=x.get('early_gap_resolution') or {}
        if early:
            assert early['valid_index'] and not early['resume_keys'];receipt=early['acceptance'];assert sha(R/receipt['path'])==receipt['sha256'];report=json.loads((R/receipt['path']).read_bytes());record=next(z for z in report['results'] if z['label']==early['label'] and z['prefix']==early['prefix']);assert all(record[k]==early[k] for k in ['query_window','valid_index','index_rows','rows']);intervals.append(early['query_window']);resolved.append(x['gallery'])
        cursor=dt('20000101000000');target=dt('20080512210044')
        for z in sorted(intervals,key=lambda z:z['from']):
            start,end=dt(z['from']),dt(z['to'])
            if start>cursor:break
            if end>=cursor:cursor=end+timedelta(seconds=1)
        assert cursor>target,('uncovered_interval',x['gallery'],str(cursor));verified.append({'gallery':x['gallery'],'complete_windows':len(intervals),'covers_from':'20000101000000','covers_through':'20080512210044'})
        slots+=x['declared_slots'];entities+=x['expected_direct_entities'];counts.update(x['entity_audit_status_counts'])
    assert (slots,entities,len(resolved))==(1684,3368,24)
    assert dict(counts)=={'archive_404':79,'transport_unknown':47,'never_requested':3242},counts
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'registry_sha256':sha(P),'prior_registry_sha256':sha(V6),'groups':50,'declared_slots':slots,'direct_entities':entities,'native_payload_status_counts':dict(counts),'early_gap_groups_resolved':len(resolved),'interval_coverage_independently_merged':verified,'global_complete_windows':50,'new_native_gallery_payloads':0,'metadata_errata':['Two input role descriptions retain working-mode wording; final acceptance bindings, SHA values and final frozen registry data were independently checked.'],'scope':'Finite complete CDX query windows joined from2000 throughanchor. This is index coverage; individual replay statuses remain79/47/3242.'}
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='interval_coverage_independently_merged'}))
if __name__=='__main__':main()

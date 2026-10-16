"""Verify saved CONTROL03 responses and open only a separately authorized window."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
from accept_eu_deps_sources import headers
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';D=B/'network/control03'
def main():
    raw=(D/'batch-report.json').read_bytes();r=json.loads(raw);a=r['attempts']
    assert hashlib.sha256(raw).hexdigest()=='60b86818a0c064f9851b1f8dcfe2605abe483b0a5be051cd85aac4bef0de1fae'
    assert r['historical_failure_tail']==5 and r['previous_tail_preserved'] and r['no_replay'] and not r['accepted_payloads']
    assert len(a)==r['network_requests']==2 and [x['transport'] for x in a]==['direct','proxy']
    total=responses=0;rows=[]
    for x in a:
        assert x['sent'] and x['disk_free_before_bytes']>=11005853696
        body_path=R/x['body_path'];body=body_path.read_bytes() if body_path.is_file() else b''
        assert len(body)==x['body_bytes'] and hashlib.sha256(body).hexdigest()==x['body_sha256']
        assert len(body)<=1048576 and 0<x['effective_connect_timeout_seconds']<=x['effective_timeout_seconds']<=20
        status,h=headers((R/x['headers_path']).read_bytes());assert status==x['source_status']
        q=parse_qs(urlsplit(x['url']).query);assert q['url']==['http://www.worldofwarcraft.com/new-hp/images/smallcaps/h.gif'] and q['matchType']==['exact'] and q['from']==['20000101000000'] and q['to']==['20080512210044'] and q['limit']==['250'] and 'collapse' not in q
        total+=len(body);responses+=int(status is not None)
        if status==200:
            assert x['curl_exit']==0
            p=json.loads(body);assert p[0]==['timestamp','original','mimetype','statuscode','digest','length']
            assert all(isinstance(z,list) and len(z)==6 for z in p[1:]);rows=[dict(zip(p[0],z)) for z in p[1:]]
    assert len(rows)==42<250 and total==r['total_body_bytes']==6082 and responses==1
    assert any(x['original']=='http://www.worldofwarcraft.com/new-hp/images/smallcaps/h.gif' and x['statuscode']=='200' and x['mimetype']=='image/gif' for x in rows)
    assert all('20000101000000'<=x['timestamp']<='20080512210044' for x in rows)
    assert a[-1]['dispatch_monotonic']-a[0]['dispatch_monotonic']>=5.25
    assert (datetime.fromisoformat(a[-1]['started_utc'])-datetime.fromisoformat(a[0]['started_utc'])).total_seconds()>=5
    assert (datetime.fromisoformat(r['finished_utc'])-datetime.fromisoformat(r['started_utc'])).total_seconds()<60
    receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'resume_gate_passed':True,'control_final_streak':0,'historical_gallery_prefix03_tail_preserved':5,'requests':2,'source_responses':1,'index_records':42,'body_bytes':total,'new_images':0,'batch_report_sha256':hashlib.sha256(raw).hexdigest(),'index_body_sha256':a[-1]['body_sha256'],'source_response_finished_utc':a[-1]['finished_utc'],'disk_free_after_bytes':shutil.disk_usage(R).free,'normal_retrieval_policy':'Root may separately authorize one new bounded window. A successful control does not erase the prior failed batch.'}
    assert receipt['disk_free_after_bytes']>=11005853696
    (B/'publication/root-control03-acceptance.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
if __name__=='__main__':main()

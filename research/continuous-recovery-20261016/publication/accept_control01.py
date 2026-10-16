"""Root verification of the bounded connectivity recovery control."""
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
NETWORK=ROOT/'research/continuous-recovery-20261016/network/control01'
def main():
    data=(NETWORK/'batch-report.json').read_bytes()
    report=json.loads(data)
    attempts=json.loads((NETWORK/'attempt-records.json').read_bytes())
    assert len(attempts)==report['network_requests']==2
    assert report['previous_allnews02_tail']==5 and report['previous_tail_preserved'] is True
    assert datetime.fromisoformat(attempts[0]['started_utc'])>=datetime(2026,10,16,4,30,tzinfo=timezone.utc)
    assert [x['transport'] for x in attempts]==['direct','proxy']
    direct=(NETWORK/'raw/01-CONTROL01-R02-cdx-direct.body').read_bytes()
    body=(NETWORK/'raw/02-CONTROL01-R02-cdx-proxy.body').read_bytes()
    headers=(NETWORK/'raw/02-CONTROL01-R02-cdx-proxy.headers.txt').read_bytes()
    assert not direct and len(body)==6082<1048576
    assert re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})',headers)[-1]==b'200'
    rows=json.loads(body)
    records=[dict(zip(rows[0],row)) for row in rows[1:]]
    assert len(records)==42<250
    assert all('20060101000000'<=x['timestamp']<='20080512210044' for x in records)
    assert any(x['original']=='http://www.worldofwarcraft.com/new-hp/images/smallcaps/h.gif' and x['statuscode']=='200' and x['mimetype']=='image/gif' for x in records)
    assert attempts[1]['curl_exit']==0 and attempts[1]['source_status']==200
    assert all(x['disk_free_before_bytes']>=11005853696 for x in report['attempts'])
    assert report['attempts'][1]['dispatch_monotonic']-report['attempts'][0]['dispatch_monotonic']>=5.1
    assert (datetime.fromisoformat(attempts[1]['started_utc'])-datetime.fromisoformat(attempts[0]['started_utc'])).total_seconds()>=5
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'resume_gate_passed':True,
        'requests':2,'source_responses':1,'index_records':42,'body_bytes':len(body),'new_images':0,
        'previous_allnews02_tail_preserved':5,'control_final_streak':0,
        'batch_report_sha256':hashlib.sha256(data).hexdigest(),'index_body_sha256':hashlib.sha256(body).hexdigest(),
        'normal_retrieval_policy':'Parent may authorize a fresh bounded window with streak0 after this successful source response; retain the old five-failure batch and control evidence.'}
    (OUT/'root-control01-acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'accepted':True,'resume_gate_passed':True,'new_images':0}))
if __name__=='__main__':main()

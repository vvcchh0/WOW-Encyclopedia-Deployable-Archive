"""Root classification of the stopped five-attempt transfer window."""
import importlib.util
import json
import hashlib
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
NETWORK=ROOT/'research/continuous-recovery-20261016/network/driver-v2'

def main():
    spec=importlib.util.spec_from_file_location('root_transport_parser',ROOT/'research/continuous-recovery-20261015/network-core-pages3/core_pages3.py')
    core=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    data=(NETWORK/'batch-report.json').read_bytes()
    report=json.loads(data)
    attempts=report['attempts']
    assert len(attempts)==report['source_request_count']==5
    assert report['source_response_count']==report['valid_image_count']==report['total_body_bytes']==0
    assert [x['curl_exit'] for x in attempts]==[28,35,28,35,28]
    checked=[]
    for attempt in attempts:
        assert attempt['source_status'] is None and attempt['transport_error'] is True
        body_path=NETWORK/attempt['raw']['body']
        assert not body_path.exists() or not body_path.read_bytes()
        headers=(NETWORK/attempt['raw']['headers']).read_text(encoding='latin1')
        assert core.source_blocks(headers)==[]
        assert attempt['dispatch']['disk_free_before_bytes']>=11005853696
        checked.append({'target':attempt['target_key'],'kind':attempt['kind'],'transport':attempt['transport'],
            'curl_exit':attempt['curl_exit'],'actual_non_connect_http_responses':0,
            'header_sha256':hashlib.sha256(headers.encode('latin1')).hexdigest()})
    starts=[datetime.fromisoformat(x['started_utc']) for x in attempts]
    dispatch=[x['dispatch']['dispatch_monotonic'] for x in attempts]
    assert min((b-a).total_seconds() for a,b in zip(starts,starts[1:]))>=5
    assert min(b-a for a,b in zip(dispatch,dispatch[1:]))>=5.1
    cooldown=report['cooldown']
    assert cooldown['applied'] and (datetime.fromisoformat(cooldown['finished_utc'])-datetime.fromisoformat(cooldown['started_utc'])).total_seconds()>=120
    assert report['stop_reason']=='five_consecutive_tls_or_transport_failures'
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,
        'scope':'Failure classification, actual zero bodies/responses, stop and cooldown verified; no asset accepted.',
        'requests':5,'source_responses':0,'new_images':0,'trailing_transfer_failures':5,
        'cooldown':cooldown,'attempts':checked,'batch_report_sha256':hashlib.sha256(data).hexdigest(),
        'not_attempted':['Blizzcon replay','I proxy replay'],'network_hold_until_utc':'2026-10-16T04:30:00Z',
        'next_gate':'Separate two-attempt connectivity control after cooldown; successful source response required before a new normal batch.'}
    (OUT/'root-allnews02-failure-acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'accepted':True,'requests':5,'new_images':0,'tail':5}))

if __name__=='__main__': main()

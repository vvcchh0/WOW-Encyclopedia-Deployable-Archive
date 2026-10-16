"""Root verification of EU index evidence and seven private text entities."""
import base64,gzip,hashlib,json,re,shutil,zlib
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';D=B/'network/eu-deps01'

def identity(v):
    u=urlsplit(v);return u.scheme,u.hostname,u.port or (80 if u.scheme=='http' else 443),u.path,u.query

def headers(raw):
    blocks=[x for x in re.split(rb'\r?\n\r?\n',raw) if re.match(rb'^HTTP/\S+\s+\d{3}',x) and b'connection established' not in x.splitlines()[0].lower()]
    if not blocks:return None,{}
    lines=blocks[-1].decode('iso-8859-1').splitlines();status=int(lines[0].split()[1]);values={}
    for x in lines[1:]:
        if ':' in x:
            k,v=x.split(':',1);values.setdefault(k.lower(),[]).append(v.strip())
    return status,values

def main():
    data=(D/'batch-report.json').read_bytes();report=json.loads(data);state=json.loads((D/'state.json').read_bytes());plan=json.loads((D/'plan.json').read_bytes())
    assert hashlib.sha256(data).hexdigest()=='59e873c933e3d987f7f2b05b2667d60647692d89558a779f07eb7de604764782'
    attempts=state['attempts'];assert len(attempts)==report['network_requests']==38
    total=0;responses=0;streak=0;indexes={};by_label={}
    for a in attempts:
        assert a['sent'] and a['disk_free_before_bytes']>=11005853696 and a['disk_free_at_dispatch']>=11005853696
        body=(R/a['body_path']).read_bytes() if a.get('body_path') else b''
        assert len(body)==a['body_bytes'] and hashlib.sha256(body).hexdigest()==a['raw_body_sha256']
        assert len(body)<=a['clamp_after_gate']['entity_body_cap']<=8*1024**2
        assert 0<a['effective_connect_timeout_seconds']<=a['effective_timeout_seconds']<=a['clamp_after_gate']['remaining_time_seconds']
        status,h=headers((R/a['headers_path']).read_bytes() if a.get('headers_path') else b'')
        assert status==a['source_status']
        total+=len(body);responses+=int(status is not None)
        streak=streak+1 if status is None or a['curl_exit']!=0 else 0
        assert streak<5 and status not in (429,503)
        by_label[a['label']]=a
        if a['label'].endswith(':cdx') and status==200 and a['curl_exit']==0:
            payload=json.loads(body);rr=[]
            if payload:
                assert payload[0]==['urlkey','timestamp','original','mimetype','statuscode','digest','length']
                assert all(isinstance(z,list) and len(z)==7 for z in payload[1:])
                rr=[dict(zip(payload[0],z)) for z in payload[1:]]
            assert len(rr)<500 and all('20060101000000'<=r['timestamp']<='20080512210044' for r in rr)
            indexes[a['label'][:-4]]=rr
    assert total==report['total_body_bytes']==69289 and responses==report['source_responses']==16
    assert len(indexes)==9 and streak==report['failure_streak']==0
    checked=[];candidate_by_key={x['target_key']:x for x in plan['candidates']}
    for p in report['accepted_payloads']:
        key=p['target_key'];c=candidate_by_key[key];ts=p['selected_capture_timestamp'];rows=indexes[key]
        row=next(r for r in rows if r['timestamp']==ts and identity(r['original'])==identity(p['original']) and r['digest']==p['cdx_digest'])
        eligible=[r for r in rows if identity(r['original'])==identity(c['original']) and r['statuscode']=='200' and r['mimetype'] in c['expected']['mime_types']]
        assert ts==max(r['timestamp'] for r in eligible)
        a=by_label[key+':replay:'+ts];assert a['curl_exit']==0
        wire=(R/a['body_path']).read_bytes();status,h=headers((R/a['headers_path']).read_bytes());assert status==200
        actual=parsedate_to_datetime(h['memento-datetime'][0]).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')
        assert actual==ts==p['actual_memento_timestamp'] and '20060101000000'<=actual<='20080512210044'
        link=next(re.search(r'<([^>]+)>\s*;\s*rel="?original',v,re.I).group(1) for v in h['link'] if re.search(r'<([^>]+)>\s*;\s*rel="?original',v,re.I))
        assert identity(link)==identity(c['original']) and link==p['actual_link_original']
        encoding=h.get('content-encoding',['identity'])[0].lower()
        body=gzip.decompress(wire) if encoding=='gzip' else zlib.decompress(wire) if encoding=='deflate' else wire
        assert len(body)<=8*1024**2 and len(body)==p['decoded_body_bytes']
        assert hashlib.sha256(body).hexdigest()==p['decoded_body_sha256']
        assert base64.b32encode(hashlib.sha1(body).digest()).decode().rstrip('=')==row['digest']
        assert (R/p['private_decoded_payload_path']).read_bytes()==body
        mime=h['content-type'][0].split(';',1)[0].lower();assert mime in c['expected']['mime_types']
        text=body.decode(p['verification']['text_encoding'])
        assert '\x00' not in text and not re.search(r'wayback machine|404 not found|this url has not been archived',text,re.I)
        assert re.search(r'function|var |document|window|;',text) if c['kind']=='javascript' else re.search(r'<(?:html|head|body|script)\b',text,re.I)
        checked.append({'original':c['original'],'kind':c['kind'],'actual_capture_timestamp':actual,'sha256':p['decoded_body_sha256'],
                        'length':len(body),'cdx_digest':row['digest'],'private_payload_path':p['private_decoded_payload_path'],
                        'accepted_as_source_data':True,'deployed':False})
    assert len(checked)==7 and sum(x['length'] for x in checked)==30206
    dispatch=[b['dispatch']['dispatch_monotonic']-a['dispatch']['dispatch_monotonic'] for a,b in zip(attempts,attempts[1:])]
    starts=[(datetime.fromisoformat(b['started_utc'])-datetime.fromisoformat(a['started_utc'])).total_seconds() for a,b in zip(attempts,attempts[1:])]
    assert min(dispatch)>=5.25 and min(starts)>=5
    elapsed=(datetime.fromisoformat(report['finished_utc'])-datetime.fromisoformat(report['started_utc'])).total_seconds();assert elapsed<1800
    free=shutil.disk_usage(R).free;assert free>=11005853696
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'batch_report_sha256':hashlib.sha256(data).hexdigest(),
            'requests':38,'source_responses':16,'complete_indexes':9,'source_payloads':7,'source_payload_bytes':30206,
            'unresolved_targets':3,'body_bytes':total,'failure_streak_end':0,'minimum_dispatch_seconds':min(dispatch),
            'minimum_request_start_seconds':min(starts),'elapsed_seconds':elapsed,'disk_free_after_bytes':free,
            'checked':checked,'scope':'Verified original EU text data for dependency and navigation research. Scripts were not executed or deployed; private content remains local.'}
    (B/'publication/root-eu-deps-source-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k!='checked'}))

if __name__=='__main__':main()

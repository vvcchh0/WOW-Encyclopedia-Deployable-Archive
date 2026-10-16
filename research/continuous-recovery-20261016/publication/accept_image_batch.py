"""Root verification of saved, bounded image batches; never sends requests."""
import argparse,base64,gzip,hashlib,io,json,re,shutil,zlib
from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from PIL import Image,ImageSequence
from accept_eu_deps_sources import headers,identity
R=Path(__file__).resolve().parents[3]; B=R/'research/continuous-recovery-20261016'
sha=lambda b:hashlib.sha256(b).hexdigest()

def records(raw,limit):
    payload=json.loads(raw)
    if not payload:return []
    assert isinstance(payload[0],list) and set(payload[0]) in ({'urlkey','timestamp','original','mimetype','statuscode','digest','length'},{'timestamp','original','mimetype','statuscode','digest','length'})
    rows=[]
    for row in payload[1:]:
        assert isinstance(row,list)
        if not row:continue
        assert len(row)==len(payload[0]),'resumption or unknown metadata: not a complete index'
        rows.append(dict(zip(payload[0],row)))
    assert len(rows)<limit,'sub-limit complete evidence required'
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--batch-directory',required=True);p.add_argument('--plan',required=True);p.add_argument('--starting-failures',required=True,type=int);p.add_argument('--output',required=True);a=p.parse_args()
    D=(R/a.batch_directory).resolve();D.relative_to(B/'network')
    plan_path=(R/a.plan).resolve();plan_path.relative_to(B/'network')
    raw=(D/'batch-report.json').read_bytes();report=json.loads(raw);state=json.loads((D/'state.json').read_bytes());plan=json.loads(plan_path.read_bytes())
    assert state['plan_sha256']==sha(plan_path.read_bytes())
    attempts=state['attempts'];candidates={x['target_key']:x for x in plan['candidates']}
    assert len(candidates)==len(plan['candidates'])==plan['candidate_count']<=20
    assert state['failure_streak_start']==a.starting_failures and 0<=a.starting_failures<5
    assert len(attempts)==report['network_requests']<=plan['policy']['max_attempts']<=100
    total=responses=0;streak=a.starting_failures;by_label={};fresh_indexes={};disk_values=[]
    for n,x in enumerate(attempts):
        if not x['sent']:
            assert n==len(attempts)-1 and x['status'].startswith('not_dispatched');continue
        disk_values.extend([x['disk_free_before_bytes'],x['disk_free_at_dispatch']]);assert min(disk_values)>=11005853696
        body=(R/x['body_path']).read_bytes() if x.get('body_path') else b''
        assert len(body)==x['body_bytes'] and sha(body)==x['raw_body_sha256']
        assert len(body)<=x['clamp_after_gate']['entity_body_cap']<=8*1024**2
        assert 0<x['effective_connect_timeout_seconds']<=x['effective_timeout_seconds']<=x['clamp_after_gate']['remaining_time_seconds']
        status,h=headers((R/x['headers_path']).read_bytes())
        assert status==x['source_status'];responses+=int(status is not None);total+=len(body)
        streak=streak+1 if status is None or x['curl_exit']!=0 else 0
        if streak>=5 or status in (429,503):assert n==len(attempts)-1
        by_label[x['label']]=x
        if x['label'].endswith(':cdx'):
            key=x['label'][:-4];q=parse_qs(urlsplit(x['url']).query);assert q['url']==[candidates[key]['original']] and q['matchType']==['exact'] and 'collapse' not in q
            assert '20000101000000'<=q['from'][0]<=q['to'][0]<='20080512210044'
            if status==200 and x['curl_exit']==0:
                try:fresh_indexes[key]=records(body,int(q['limit'][0]))
                except AssertionError:pass
    assert total==report['total_body_bytes']<=plan['policy']['max_total_body_bytes']<=64*1024**2
    assert responses==report['source_responses'] and streak==report['failure_streak']
    if streak>=5 or any(x.get('source_status') in (429,503) for x in attempts):
        last=attempts[-1];cool=datetime.fromisoformat(report['cooldown_not_before_utc'].replace('Z','+00:00'))
        assert cool>=datetime.fromisoformat(last['finished_utc'].replace('Z','+00:00'))+timedelta(seconds=120)
    result_by={x['target_key']:x for x in report['results']};checked=[]
    for x in report['accepted_payloads']:
        key=x['target_key'];c=candidates[key];r=result_by[key];ts=x['selected_capture_timestamp'];classification=r['cdx_source']
        if classification=='best_known_cached_fallback':
            rows=c['known_positive_cache_rows'];assert r['latest_unknown'] and r['status']=='best_known_cached_not_latest';selection_label='best_known_cached_not_latest'
        elif c['cdx_mode']=='cached':
            cached=c['cached_cdx'];body=(R/cached['raw_body_path']).read_bytes();assert sha(body)==cached['body_sha256']
            status,_=headers((R/cached['raw_headers_path']).read_bytes());assert status==200
            rows=records(body,int(c['query']['limit']));assert len(rows)==cached['record_count'];selection_label='latest_candidate_in_bound_complete_index'
        else:rows=fresh_indexes[key];selection_label='latest_candidate_in_complete_index'
        eligible=[z for z in rows if identity(z['original'])==identity(c['original']) and z['statuscode']=='200' and z['mimetype'] in c['expected']['mime_types'] and c['query']['from']<=z['timestamp']<=c['query']['to']]
        distinct=[];digests=set()
        for z in sorted(eligible,key=lambda z:z['timestamp'],reverse=True):
            if z['digest'] not in digests:distinct.append(z);digests.add(z['digest'])
        chosen=next(z for z in distinct[:2] if z['timestamp']==ts and z['digest']==x['cdx_digest'])
        replay=by_label[key+':replay:'+ts];assert replay['curl_exit']==0
        wire=(R/replay['body_path']).read_bytes();status,h=headers((R/replay['headers_path']).read_bytes());assert status==200
        actual=parsedate_to_datetime(h['memento-datetime'][0]).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S');assert actual==ts==x['actual_memento_timestamp']
        original=next(re.search(r'<([^>]+)>\s*;\s*rel="?original',v,re.I).group(1) for v in h['link'] if re.search(r'<([^>]+)>\s*;\s*rel="?original',v,re.I));assert identity(original)==identity(c['original'])
        encoding=h.get('content-encoding',['identity'])[0].lower();assert encoding in ('identity','gzip','deflate')
        payload=gzip.decompress(wire) if encoding=='gzip' else zlib.decompress(wire) if encoding=='deflate' else wire
        assert len(payload)==x['decoded_body_bytes']<=8*1024**2 and sha(payload)==x['decoded_body_sha256'] and payload==(R/x['private_decoded_payload_path']).read_bytes()
        digest=base64.b32encode(hashlib.sha1(payload).digest()).decode().rstrip('=');assert digest==chosen['digest']
        mime=h['content-type'][0].split(';',1)[0].lower();assert mime in c['expected']['mime_types']
        with Image.open(io.BytesIO(payload)) as img:img.verify()
        with Image.open(io.BytesIO(payload)) as img:
            fmt=img.format;size=list(img.size);frames=0
            for frame in ImageSequence.Iterator(img):frame.load();frames+=1
        assert fmt in c['expected']['pillow_formats'] and frames==x['verification']['image_frame_count']
        checked.append({'original':c['original'],'actual_capture_timestamp':actual,'mime':mime,'dimensions':size,'decoded_frames':frames,'length':len(payload),'sha256':sha(payload),'cdx_digest':digest,'private_payload_path':x['private_decoded_payload_path'],'selection_evidence':selection_label,'accepted':True,'deployed':False})
    sent=[x for x in attempts if x['sent']]
    if plan['policy'].get('transport_policy')=='batch_after_direct_failure':
        assert sent and sent[0]['transport']=='direct'
        trigger=next((x for x in sent if x['transport']=='direct' and x['source_status'] is None and x['curl_exit'] in (7,28) and x['body_bytes']==0),None)
        if trigger:
            assert state['batch_proxy_only'] and state['failed_attempt_number']==trigger['attempt']
            assert all(x['transport']=='proxy' for x in sent if x['attempt']>trigger['attempt'])
        else:assert not state['batch_proxy_only']
    dispatch=[y['dispatch']['dispatch_monotonic']-x['dispatch']['dispatch_monotonic'] for x,y in zip(sent,sent[1:])]
    starts=[(datetime.fromisoformat(y['started_utc'])-datetime.fromisoformat(x['started_utc'])).total_seconds() for x,y in zip(sent,sent[1:])]
    assert not dispatch or min(dispatch)>=5.25
    assert not starts or min(starts)>=5
    elapsed=(datetime.fromisoformat(report['finished_utc'])-datetime.fromisoformat(report['started_utc'])).total_seconds();assert elapsed<=plan['policy']['window_seconds']<=1800
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'batch_report_sha256':sha(raw),'plan_sha256':sha(plan_path.read_bytes()),'requests':len(attempts),'source_responses':responses,'body_bytes':total,'accepted_images':checked,'image_bytes':sum(x['length'] for x in checked),'failure_streak_start':a.starting_failures,'failure_streak_end':streak,'stop_reason':report['stop_reason'],'cooldown_not_before_utc':report.get('cooldown_not_before_utc'),'minimum_dispatch_seconds':min(dispatch,default=None),'minimum_request_start_seconds':min(starts,default=None),'elapsed_seconds':elapsed,'minimum_request_disk_bytes':min(disk_values,default=None),'disk_free_after_bytes':shutil.disk_usage(R).free,'scope':'Original image sources and actual batch limits verified. No deployment is inferred.'}
    assert result['disk_free_after_bytes']>=11005853696
    result['actual_transports']={name:sum(x['transport']==name for x in sent) for name in ('direct','proxy')}
    result['batch_proxy_only']=state.get('batch_proxy_only',False)
    output=(R/a.output).resolve();output.relative_to(B/'publication');assert not output.exists(),'preserve existing root receipt'
    output.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items() if k!='accepted_images'}))
if __name__=='__main__':main()

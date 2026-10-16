"""Root recheck of the stopped shared-news batch and its two image entities."""
import base64, gzip, hashlib, io, json, re, shutil, zlib
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from PIL import Image, ImageSequence
from accept_eu_deps_sources import headers, identity

R = Path(__file__).resolve().parents[3]
B = R / 'research/continuous-recovery-20261016'
D = B / 'network/news-shared10'
sha = lambda b: hashlib.sha256(b).hexdigest()

def main():
    raw = (D/'batch-report.json').read_bytes()
    assert sha(raw) == 'd140ef7917ac649a61953af6f38ff77543684d4a032d93a3beb8a96408ab1496'
    report = json.loads(raw)
    state = json.loads((D/'state.json').read_bytes())
    plan = json.loads((D/'plan.json').read_bytes())
    candidates = {c['target_key']:c for c in plan['candidates']}
    attempts = state['attempts']
    assert len(attempts) == report['network_requests'] == 11
    assert state['failure_streak_start'] == report['inherited_eu_deps01_tail'] == 0
    indexes, by_label = {}, {}
    streak = total = responses = 0
    for n, a in enumerate(attempts):
        assert a['sent'] and min(a['disk_free_before_bytes'], a['disk_free_at_dispatch']) >= 11005853696
        body = (R/a['body_path']).read_bytes() if a.get('body_path') else b''
        assert len(body) == a['body_bytes'] and sha(body) == a['raw_body_sha256']
        assert len(body) <= a['clamp_after_gate']['entity_body_cap'] <= 8*1024**2
        assert 0 < a['effective_connect_timeout_seconds'] <= a['effective_timeout_seconds'] <= a['clamp_after_gate']['remaining_time_seconds']
        status, h = headers((R/a['headers_path']).read_bytes())
        assert status == a['source_status']
        streak = streak+1 if status is None or a['curl_exit'] != 0 else 0
        if streak >= 5 or status in (429,503):
            assert n == len(attempts)-1
        total += len(body)
        responses += int(status is not None)
        by_label[a['label']] = a
        if a['label'].endswith(':cdx') and status == 200 and a['curl_exit'] == 0:
            q = parse_qs(urlsplit(a['url']).query)
            assert q['matchType'] == ['exact'] and q['limit'] == ['500'] and 'collapse' not in q
            p = json.loads(body)
            assert p[0] == ['urlkey','timestamp','original','mimetype','statuscode','digest','length']
            assert all(isinstance(x,list) and len(x)==7 for x in p[1:]) and len(p)-1 < 500
            indexes[a['label'][:-4]] = [dict(zip(p[0],x)) for x in p[1:]]
    assert total == report['total_body_bytes'] == 3631 and responses == report['source_responses'] == 3
    assert streak == report['failure_streak'] == 5
    assert report['stop_reason'] == 'five_consecutive_transport_failures'
    assert datetime.fromisoformat(report['cooldown_not_before_utc'].replace('Z','+00:00')) >= datetime.fromisoformat(attempts[-1]['finished_utc'].replace('Z','+00:00')) + timedelta(seconds=120)
    checked = []
    for p in report['accepted_payloads']:
        key = p['target_key']; c = candidates[key]; ts = p['selected_capture_timestamp']
        if key not in indexes:
            cached = next(x for x in report['results'] if x['target_key']==key)['cached_cdx_provenance']
            index_bytes = (R/cached['raw_body_path']).read_bytes()
            assert sha(index_bytes) == cached['body_sha256']
            status, _ = headers((R/cached['raw_headers_path']).read_bytes()); assert status == 200
            idx = json.loads(index_bytes)
            assert len(idx)-1 == cached['record_count'] < 250 and all(len(x)==len(idx[0]) for x in idx[1:])
            indexes[key] = [dict(zip(idx[0],x)) for x in idx[1:]]
        eligible = [x for x in indexes[key] if identity(x['original'])==identity(c['original']) and x['statuscode']=='200' and x['mimetype'] in c['expected']['mime_types'] and '20060101000000'<=x['timestamp']<='20080512210044']
        row = max(eligible,key=lambda x:x['timestamp'])
        assert ts == row['timestamp'] and p['cdx_digest'] == row['digest']
        a = by_label[key+':replay:'+ts]; assert a['curl_exit']==0
        wire = (R/a['body_path']).read_bytes(); status,h = headers((R/a['headers_path']).read_bytes()); assert status==200
        actual = parsedate_to_datetime(h['memento-datetime'][0]).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')
        assert actual == ts == p['actual_memento_timestamp']
        original = next(re.search(r'<([^>]+)>\s*;\s*rel="?original',v,re.I).group(1) for v in h['link'] if re.search(r'<([^>]+)>\s*;\s*rel="?original',v,re.I))
        assert identity(original) == identity(c['original']) and original == p['actual_link_original']
        encoding = h.get('content-encoding',['identity'])[0].lower()
        body = gzip.decompress(wire) if encoding=='gzip' else zlib.decompress(wire) if encoding=='deflate' else wire
        assert len(body)==p['decoded_body_bytes'] and sha(body)==p['decoded_body_sha256']
        assert (R/p['private_decoded_payload_path']).read_bytes()==body
        digest = base64.b32encode(hashlib.sha1(body).digest()).decode().rstrip('='); assert digest==row['digest']
        mime = h['content-type'][0].split(';',1)[0].lower(); assert mime in c['expected']['mime_types']
        with Image.open(io.BytesIO(body)) as image: image.verify()
        with Image.open(io.BytesIO(body)) as image:
            fmt = image.format; size=list(image.size); frames=0
            for frame in ImageSequence.Iterator(image): frame.load(); frames+=1
        assert fmt in c['expected']['pillow_formats'] and frames==p['verification']['image_frame_count']
        checked.append({'original':c['original'],'actual_capture_timestamp':actual,'mime':mime,'dimensions':size,'decoded_frames':frames,'length':len(body),'sha256':sha(body),'cdx_digest':digest,'private_payload_path':p['private_decoded_payload_path'],'accepted':True,'deployed':False})
    assert len(checked)==2 and sum(x['length'] for x in checked)==2370
    dispatch=[b['dispatch']['dispatch_monotonic']-a['dispatch']['dispatch_monotonic'] for a,b in zip(attempts,attempts[1:])]
    starts=[(datetime.fromisoformat(b['started_utc'])-datetime.fromisoformat(a['started_utc'])).total_seconds() for a,b in zip(attempts,attempts[1:])]
    assert min(dispatch)>=5.25 and min(starts)>=5
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'batch_report_sha256':sha(raw),'requests':11,'source_responses':3,'body_bytes':total,'accepted_images':checked,'image_bytes':2370,'failure_streak_start':0,'failure_streak_end':5,'stop_reason':report['stop_reason'],'cooldown_not_before_utc':report['cooldown_not_before_utc'],'minimum_dispatch_seconds':min(dispatch),'minimum_request_start_seconds':min(starts),'disk_free_after_bytes':shutil.disk_usage(R).free,'scope':'Two source images accepted; eight targets remain unresolved or unvisited. Historical failure tail retained. Not deployed.'}
    assert result['disk_free_after_bytes']>=11005853696
    (B/'publication/root-news-shared10-source-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k!='accepted_images'}))

if __name__=='__main__': main()

"""Verify a bounded saved prefix batch without sending requests."""
import argparse,hashlib,json,re,shutil
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
R=Path(__file__).resolve().parents[3]
B=R/'research/continuous-recovery-20261016'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--batch-directory',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--starting-failures',required=True,type=int);args=parser.parse_args()
    directory=(R/args.batch_directory).resolve();directory.relative_to(B/'network')
    data=(directory/'batch-report.json').read_bytes();report=json.loads(data)
    policy=report['policy'];attempts=[];results=[];source_count=0;total=0;all_images=[]
    assert report['failure_streak_start']==args.starting_failures
    assert report['payload_replay_count']==0 and not report['continuation_followed']
    assert policy['max_attempts']<=20 and policy['window_seconds']<=900
    assert policy['max_total_body_bytes']<=64*1024**2 and policy['max_entity_body_bytes']<=16*1024**2
    assert report['script_sha256']==hashlib.sha256((directory/'gallery_prefix_driver_v3.py').read_bytes()).hexdigest()
    assert report['plan_sha256']==hashlib.sha256((directory/'execution-plan.json').read_bytes()).hexdigest()
    for binding in policy['input_bindings'].values():
        assert hashlib.sha256((R/binding['path']).read_bytes()).hexdigest()==binding['sha256']
    for candidate in report['candidate_results']:
        q=parse_qs(urlsplit(candidate['query_url']).query)
        assert q['url']==[candidate['prefix']] and q['matchType']==['prefix']
        assert q['from']==['20060101000000'] and q['to']==['20080512210044']
        assert q['limit']==['500'] and q['showResumeKey']==['true'] and 'collapse' not in q
        aa=candidate['attempts'];assert [a['transport'] for a in aa] in (['direct'],['direct','proxy'])
        rows=[];resume=[];valid=False
        for a in aa:
            attempts.append(a);body=(R/a['raw']['body']).read_bytes();headers=(R/a['raw']['headers.txt']).read_bytes()
            assert len(body)==a['body_bytes']
            if body:assert hashlib.sha256(body).hexdigest()==a['body_sha256']
            assert a['disk_free_before_bytes']>=11005853696 and a['clamp']['dispatch_allowed']
            assert len(body)<=a['clamp']['entity_body_limit_before_bytes']
            total+=len(body)
            statuses=re.findall(rb'(?m)^HTTP/\S+\s+(\d{3})',headers)
            if a['source_status'] is None:
                assert a['curl_exit']!=0 and not body and (not statuses or statuses==[b'200'])
                continue
            source_count+=1
            assert statuses[-1].decode()==str(a['source_status'])
            if a['source_status']==200:
                assert a['curl_exit']==0
                payload=json.loads(body);rows=[];resume=[]
                if payload:
                    assert payload[0]==['urlkey','timestamp','original','mimetype','statuscode','digest','length']
                    for z in payload[1:]:
                        assert isinstance(z,list)
                        if len(z)==7:rows.append(dict(zip(payload[0],z)))
                        elif len(z)==1 and z[0]:resume.append(z[0])
                        else:assert not z
                assert len(rows)==a['cdx_record_count'] and resume==a['resume_keys']
                valid=True
        assert len(rows)==candidate['capture_index_count']
        assert resume==candidate['resume_keys']
        assert bool(resume or len(rows)>=500)==bool(candidate['potential_truncation'] or candidate['resume_keys'])
        prefix=urlsplit(candidate['prefix']);exact=[];variants=[];images=[]
        for row in rows:
            assert '20060101000000'<=row['timestamp']<='20080512210044'
            u=urlsplit(row['original']);kind=re.fullmatch(r'ss[1-9][0-9]*(?:-thumb)?\.jpg',u.path[len(prefix.path):]) if u.path.startswith(prefix.path) else None
            if row['statuscode']=='200' and row['mimetype'].startswith('image/'):
                images.append(row)
                if kind and not u.query and not u.fragment:
                    (exact if (u.scheme,u.netloc)==(prefix.scheme,prefix.netloc) else variants).append(row)
        assert len(exact)==len(candidate['strict_literal_full_candidates'])+len(candidate['strict_literal_thumb_candidates'])
        all_images+=images
        results.append({'label':candidate['label'],'prefix':candidate['prefix'],'index_rows':len(rows),'valid_index':valid,
                        'resume_keys':resume,'direct_exact_candidates':len(exact),'direct_variant_candidates':len(variants),
                        'image_index_rows':len(images),'rows':rows})
    assert len(attempts)==report['network_requests']<=20 and total==report['total_body_bytes']
    assert source_count==report['source_responses']
    streak=args.starting_failures
    for n,a in enumerate(attempts):
        streak=streak+1 if a['source_status'] is None else 0
        if streak>=5 or a['source_status'] in (429,503):assert n==len(attempts)-1
    assert streak==report['failure_streak']
    dispatch=[b['dispatch_monotonic']-a['dispatch_monotonic'] for a,b in zip(attempts,attempts[1:])]
    starts=[(datetime.fromisoformat(b['started_utc'])-datetime.fromisoformat(a['started_utc'])).total_seconds() for a,b in zip(attempts,attempts[1:])]
    assert not dispatch or min(dispatch)>=5.25
    assert not starts or min(starts)>=5
    elapsed=(datetime.fromisoformat(report['finished_utc'])-datetime.fromisoformat(report['window_started_utc'])).total_seconds();assert elapsed<900
    free=shutil.disk_usage(R).free;assert free>=11005853696
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':len(attempts),
            'source_responses':source_count,'index_rows':sum(x['index_rows'] for x in results),'body_bytes':total,
            'image_index_rows':len(all_images),'direct_exact_candidates':sum(x['direct_exact_candidates'] for x in results),
            'direct_variant_candidates':sum(x['direct_variant_candidates'] for x in results),'payload_replays':0,
            'failure_streak_start':args.starting_failures,'failure_streak_end':streak,
            'minimum_dispatch_seconds':min(dispatch,default=None),'minimum_start_seconds':min(starts,default=None),
            'elapsed_seconds':elapsed,'disk_free_after_bytes':free,'batch_report_sha256':hashlib.sha256(data).hexdigest(),
            'results':results,'scope':'Captured index records only; absent direct rows are not individual image replay 404 findings.'}
    output=R/args.output;output.resolve().relative_to(B/'publication')
    output.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k!='results'}))

if __name__=='__main__':main()

"""Root acceptance of observed EU literals for a future bounded query."""
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urljoin,urlsplit
R=Path(__file__).resolve().parents[3]
B=R/'research/continuous-recovery-20261016'
D=B/'local-audit/eu-dependencies'

def main():
    p=D/'prior10-proposal.json';proposal=json.loads(p.read_bytes())
    audit_path=R/proposal['source_audit'];audit=json.loads(audit_path.read_bytes())
    assert hashlib.sha256(audit_path.read_bytes()).hexdigest()==proposal['source_audit_sha256']
    assert len(proposal['items'])==10 and audit['base_events']=={'eu_home':[],'screen_page':[]}
    page_by_id={x['id']:x for x in audit['scope']['pages']}
    accepted=[]
    for item in proposal['items']:
        assert item['eu_exact_map'] is None and len(item['source_evidence'])==1
        e=item['source_evidence'][0];page=page_by_id[e['page_id']]
        raw=(R/e['source_page']).read_bytes();text=raw.decode('utf-8',errors='replace')
        lines=text.splitlines();assert e['raw_literal'] in lines[e['line']-1]
        assert e['context'] in lines[e['line']-1] and e['layer']=='html'
        url=urljoin(page['original_url'],e['raw_literal'])
        assert url==item['resolved_url'] and urlsplit(url).hostname=='www.wow-europe.com'
        assert not re.search(r'jsessionid|(?:session|token|auth|password|cookie)[=;:]',url,re.I)
        assert urlsplit(url).query==''
        accepted.append({'original':url,'kind':item['kind'],'literal':e['raw_literal'],'source_page':e['source_page'],
                         'source_sha256':hashlib.sha256(raw).hexdigest(),'line':e['line'],'exact_eu_payload_known':False})
    assert sum(i['kind']=='iframe' for i in accepted)==7
    for name in ['eu-dependencies-public-summary-v1.json','eu-dependencies-public-candidates-v1.json']:
        data=(D/name).read_bytes()
        assert not re.search(rb'(?i);jsessionid=|(?:access_token|refresh_token|sessionid|session_id|authorization|set-cookie)\s*[=:]',data)
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'scope':'Ten literal candidates only; full 99-entity classification remains the worker audit.',
            'proposal_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'audit_sha256':proposal['source_audit_sha256'],
            'observed_candidates':10,'iframe_menus':7,'network_requests':0,'downloaded_payloads':0,
            'candidates':accepted,'future_acquisition':'Exact CDX before replay; no US same-path substitution or dynamic expression expansion.'}
    (B/'publication/root-eu-dependency-candidates-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k!='candidates'}))

if __name__=='__main__':main()

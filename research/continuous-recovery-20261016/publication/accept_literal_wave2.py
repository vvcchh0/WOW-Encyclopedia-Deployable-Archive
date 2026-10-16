"""Independently bind the next EU dependencies and five shared image literals."""
import hashlib,json,re
from datetime import datetime,timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlsplit
R=Path(__file__).resolve().parents[3]; B=R/'research/continuous-recovery-20261016'
sha=lambda b:hashlib.sha256(b).hexdigest()
class Tags(HTMLParser):
    def __init__(self):super().__init__();self.scripts=[];self.bases=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('src'):self.scripts.append((a['src'],self.getpos()[0]))
        if tag=='base' and a.get('href'):self.bases.append(a['href'])
def main():
    accepted=json.loads((B/'publication/root-eu-deps-source-acceptance.json').read_bytes())
    sources={}
    for x in accepted['checked']:
        raw=(R/x['private_payload_path']).read_bytes();assert sha(raw)==x['sha256']
        sources[x['sha256']]=(x['original'],raw.decode())
    eu_path=B/'local-audit/eu-navigation-wave2/eu-navigation-wave2-public-summary-v1.json'
    eu=json.loads(eu_path.read_bytes());out=[]
    for c in eu['candidates']:
        for e in c['candidate_evidence']:
            if e.get('payload_sha256'):
                base,text=sources[e['payload_sha256']]
                assert e['context'] in text.splitlines()[e['line']-1]
                if e.get('tag')=='script':
                    p=Tags();p.feed(text);assert not p.bases
                    assert (e['literal'],e['line']) in p.scripts
                    assert urljoin(base,e['literal'])==c['original']
                else:assert re.search(r'([\'"])'+re.escape(c['original'])+r'\1',e['context'])
            else:
                raw=(R/e['source_page']).read_bytes();assert sha(raw)==e['source_page_sha256']
                text=raw.decode('utf-8',errors='replace')
                assert e['context'] in text.splitlines()[e['line']-1] and e['literal'] in e['context']
                assert urljoin(e['resolution_base'],e['literal'])==c['original']
        assert urlsplit(c['original']).hostname=='www.wow-europe.com'
        out.append({'original':c['original'],'kind':c['kind'],'evidence_literals':len(c['candidate_evidence'])})
    assert len(out)==10
    shared_path=B/'local-audit/shared-five-trace/shared-five-trace-audit-v1.json'
    shared=json.loads(shared_path.read_bytes());images=[]
    for x in shared['traces']:
        e=x['raw_source'];raw=(R/e['source_local_path']).read_bytes()
        assert sha(raw)==e['source_file_sha256'] and len(raw)==e['source_file_length']
        line=raw.decode('utf-8',errors='replace').splitlines()[e['source_line']-1]
        assert e['source_context'] in line
        literal=e['manifest_reference']['literal'];assert literal in line
        assert urljoin(e['source_base_url'],literal)==x['original']
        assert not x['payload_present'] and not x['is_dynamic_or_default_derived']
        images.append({'original':x['original'],'source_sha256':e['source_file_sha256'],'line':e['source_line'],'literal':literal})
    assert len(images)==5
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'eu_public_summary_sha256':sha(eu_path.read_bytes()),'eu_literal_candidates':out,'shared_audit_sha256':sha(shared_path.read_bytes()),'shared_image_literal_candidates':images,'scope':'Literal URL evidence only. No payload availability or successful recovery is inferred.'}
    (B/'publication/root-literal-wave2-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({'accepted':True,'eu_literals':len(out),'shared_image_literals':len(images)}))
if __name__=='__main__':main()

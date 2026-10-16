"""Root recount of static image placeholders and origin-aware priority inventory."""
import hashlib,html,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qs
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';D=B/'local-audit/v18-resource-priorities';S=R/'.scratch/pages-resources-20261016-v18'
sha=lambda b:hashlib.sha256(b).hexdigest()
def normalize(raw):
    u=urlsplit(raw);port=u.port
    if port==(80 if u.scheme=='http' else 443):port=None
    return urlunsplit((u.scheme.lower(),u.hostname.lower()+((':'+str(port)) if port else ''),u.path or '/',u.query,u.fragment))
def main():
    audit_path=D/'v18-resource-priorities-audit-v2.json';a=json.loads(audit_path.read_bytes());entities=a['all_entities'];wanted={x['canonical']:x['occurrence_count'] for x in entities}
    assert sha(audit_path.read_bytes())=='96f0d3586b1a23a4a190f04337016c04d86ea9884ea7ec883baa8715ecab12ea'
    counter=Counter();files=marked=allmarkers=textfiles=0;markerfiles=set();news=Counter()
    for p in S.rglob('*'):
        if not p.is_file():continue
        files+=1;rel=p.relative_to(S).as_posix()
        if rel.startswith('_origins/') or p.suffix.lower() not in ('.html','.htm','.xml','.css'):continue
        textfiles+=1;raw=p.read_bytes();text=raw.decode('utf-8',errors='replace')
        matches=list(re.finditer(r'missing-image\.svg\?([^\"\'<>\s\)]*)',text,re.I))
        if matches:markerfiles.add(rel)
        for m in matches:
            allmarkers+=1;values=parse_qs(html.unescape(m.group(1)),keep_blank_values=True);url=values.get('requested',[''])[0];u=urlsplit(url)
            if u.scheme not in ('http','https') or Path(u.path.lower()).suffix not in ('.gif','.jpg','.jpeg','.png','.webp','.svg','.bmp'):continue
            key=normalize(url);counter[key]+=1;marked+=1
            if rel.startswith('news/'):news[key]+=1
    assert files==8528 and textfiles==1104 and allmarkers==2278 and marked==2226 and len(counter)==1254
    assert dict(counter)==wanted and len(markerfiles)==236
    assert len(news)==616 and sum(news.values())==798
    armory=[x for x in entities if x['endpoint_class']=='related_origin_static_image'];assert len(armory)==367
    for x in armory:
        u=urlsplit(x['original']);assert u.hostname in ('www.wowarmory.com','armory.wow-europe.com') and '/images/' in u.path and not u.query and not u.fragment
    pending=[x for x in entities if x['candidate_state']=='acquired_pending_integration'];assert len(pending)==2
    queue=json.loads((D/'v18-resource-priorities-bounded-data-v2.json').read_bytes())['candidates'];assert len(queue)==20
    for x in queue:
        assert x['canonical'] in counter
        for e in x['evidence']:
            raw=(S/e['path']).read_bytes();assert sha(raw)==e['sha256']
            line=raw.decode('utf-8',errors='replace').splitlines()[e['line']-1]
            requested=[parse_qs(html.unescape(m.group(1))).get('requested',[''])[0] for m in re.finditer(r'missing-image\.svg\?([^\"\'<>\s\)]*)',line,re.I)]
            assert any(normalize(v)==x['canonical'] for v in requested) and normalize(e['requested'])==x['canonical']
        assert 'prior_evidence' in x and 'known_bad_capture' in x and 'uncovered_window' in x
    verification=D/'v18-resource-priorities-verification-v2.json';raw=verification.read_bytes();repair=None
    try:json.loads(raw)
    except json.JSONDecodeError:
        assert raw.endswith(b'\\n\r\n') or raw.endswith(b'\\n')
        clean=raw[:-4] if raw.endswith(b'\\n\r\n') else raw[:-2];json.loads(clean)
        old=verification.with_suffix('.invalid-json-superseded.bin');assert not old.exists();old.write_bytes(raw)
        verification.write_bytes(clean+b'\n');repair={'old_sha256':sha(raw),'new_sha256':sha(verification.read_bytes()),'change':'Removed a trailing literal backslash-n token after the JSON document; preserved the invalid preliminary bytes locally.'}
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'audit_sha256':sha(audit_path.read_bytes()),'files':files,'static_text_files':textfiles,'static_markers':allmarkers,'exact_image_marker_occurrences':marked,'exact_image_entities':len(counter),'news_entities':len(news),'news_occurrences':sum(news.values()),'related_static_armory_entities':len(armory),'pending_accepted_images':2,'priority_candidates_checked':20,'preliminary_verification_json_repair':repair,'scope':'Static HTML/XML/CSS placeholders only. JavaScript gallery targets (3368) and region-origin pages are separately audited; these are not whole-site missing image totals.'}
    (B/'publication/root-static-resource-inventory-acceptance.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
if __name__=='__main__':main()

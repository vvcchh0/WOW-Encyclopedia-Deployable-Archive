"""Accept two exact HTTP/HTTPS primary-origin aliases missed by the root estimate."""
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
out=PUB/'v33-export-expectations-r2.json';assert not out.exists()
old=PUB/'v33-export-expectations.json';data=read(old)
v32=ROOT/'.scratch/pages-resources-20261018-v32';v33=ROOT/'.scratch/pages-resources-20261018-v33'
provenance=read(v33/'export-provenance.json')
images={x['output_path']:x for x in provenance['files'] if x.get('role')=='image_overlay'}
reviews=[]
for page,image in [('community/comics/2006-08.html','community/images/comics/comics34-large.jpg'),('pvp/battlegrounds/info-warsong.html','pvp/images/warsong-gulch/warsong-gulch.jpg')]:
    before=(v32/page).read_bytes();after=(v33/page).read_bytes()
    target=('/WOW-Encyclopedia-Deployable-Archive/'+image).encode()
    candidates=re.findall(rb'href="([^"]*__offline/missing\.html\?[^"]*)"',before)
    matches=[]
    for value in candidates:
        query=parse_qs(value.decode().replace('&amp;','&').split('?',1)[1]);requested=query.get('requested',[''])[0]
        u=urlsplit(requested);original=urlsplit(images[image]['original_url'])
        if u.hostname==original.hostname and u.path==original.path and not u.query and not u.fragment:matches.append((value,requested))
    assert len(matches)==1
    value,requested=matches[0]
    assert before.replace(b'href="'+value+b'"',b'href="'+target+b'"')==after
    data['allowed_changed_output_paths'].append(page)
    row={'page':page,'original':requested,'accepted_original':images[image]['original_url'],'new_overlay':image.startswith('community/'),
         'before_sha256':sha(v32/page),'after_sha256':sha(v33/page),'change':'One image href only; HTTP/HTTPS canonical-origin equivalence already accepted by the exporter.'}
    reviews.append(row);data['navigation_href_recovery'].append(row)
data['allowed_changed_output_paths']=sorted(set(data['allowed_changed_output_paths']))
data.update(supersedes={'path':old.relative_to(ROOT).as_posix(),'sha256':sha(old)},root_reviewed_https_alias_changes=reviews)
out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'network_requests':0,'export_repeated':False,
    'input_gate_sha256':sha(PUB/'root-v33-input-acceptance.json'),'expectations_sha256':sha(out),'reviews':reviews,
    'reason':'The independent root estimator keyed schemes separately; the accepted primary-origin resolver already treats these HTTP/HTTPS URLs as the same image route. The complete before/after bytes differ only at the two reviewed href attributes.'}
p=PUB/'root-v33-href-expectations-revision-acceptance.json';assert not p.exists();p.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'accepted':True,'reviewed':2,'href_references':len(data['navigation_href_recovery']),'sha256':sha(out)}))

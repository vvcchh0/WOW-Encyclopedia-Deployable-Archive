"""Verify the owned draft assets before publishing the accepted browser archive."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPO='vvcchh0/WOW-Encyclopedia-Deployable-Archive'
RID=413917488
TAG='archive-20080512-browser-20261015'
TARGET='108c9287e910dbd1a0872f16a7078b89cd1f5911'
def api(endpoint):
    return json.loads(subprocess.check_output(['gh','api',endpoint],cwd=ROOT,text=True,timeout=45))
def main():
    q=json.loads((ROOT/'research/v14-integration/root-portable-acceptance.json').read_bytes())
    assert q['accepted']
    archive=ROOT/q['archive']
    expected={archive.name:(q['archive_bytes'],q['archive_sha256'])}
    for p in [archive.with_name(archive.name+'.sha256'),ROOT/'NOTICE.md']:
        b=p.read_bytes();expected[p.name]=(len(b),hashlib.sha256(b).hexdigest())
    def verify(d):
        assert d['id']==RID and d['tag_name']==TAG and d['target_commitish']==TARGET
        assert len(d['assets'])==3 and {a['name'] for a in d['assets']}==set(expected)
        checks=[]
        for a in d['assets']:
            n,h=expected[a['name']]
            assert a['state']=='uploaded' and a['size']==n and a.get('digest')=='sha256:'+h,a['name']
            checks.append({'id':a['id'],'name':a['name'],'state':a['state'],'bytes':a['size'],'digest':a['digest'],'expected_sha256':h,'browser_download_url':a['browser_download_url'],'accepted':True})
        return checks
    d=api(f'repos/{REPO}/releases/{RID}');before=verify(d)
    if d['draft']:
        subprocess.run(['gh','release','edit',TAG,'--repo',REPO,'--draft=false','--latest'],cwd=ROOT,check=True,timeout=60)
    d=api(f'repos/{REPO}/releases/{RID}');checks=verify(d);assert not d['draft']
    tag_commit=api(f'repos/{REPO}/commits/{TAG}')['sha'];assert tag_commit==TARGET
    report={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'published':True,'release_id':RID,'tag':TAG,'url':d['html_url'],'target_commit':TARGET,'resolved_tag_commit':tag_commit,'assets':checks,'verification':'GitHub uploaded-asset size and SHA-256 digest match the independently read local package and sidecars; metadata rechecked after publication. No duplicate full ZIP download.','portable_acceptance':'research/v14-integration/root-portable-acceptance.json'}
    (ROOT/'research/v14-integration/root-release-publication.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'published':True,'url':d['html_url'],'assets':len(checks),'target_commit':tag_commit}))
if __name__=='__main__':main()

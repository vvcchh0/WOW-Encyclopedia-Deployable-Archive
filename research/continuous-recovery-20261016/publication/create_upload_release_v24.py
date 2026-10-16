"""Create one owned draft and upload the accepted processed browser package."""
import hashlib,json,subprocess,os,shutil
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;REPO='vvcchh0/WOW-Encyclopedia-Deployable-Archive';TAG='archive-20080512-browser-20261016'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,timeout=60):return subprocess.check_output(args,cwd=R,text=True,timeout=timeout)
def main():
    assert datetime.now(timezone.utc)<datetime(2026,10,16,13,45,tzinfo=timezone.utc)
    assert shutil.disk_usage(R).free>=11005853696
    qpath=O/'root-v24-portable-acceptance.json';q=json.loads(qpath.read_bytes());assert q['accepted'];archive=R/q['archive'];assert sha(archive)==q['archive_sha256'] and archive.stat().st_size==q['archive_bytes']
    expected={p.name:(p.stat().st_size,sha(p)) for p in [archive,archive.with_name(archive.name+'.sha256'),R/'NOTICE.md']}
    target=run(['git','rev-parse','HEAD']).strip();assert run(['git','rev-parse','origin/main']).strip()==target
    config=O/'v24-release-draft.json';notes=O/'v24-release-notes.md';assert notes.is_file()
    releases=json.loads(run(['gh','api',f'repos/{REPO}/releases']));existing=[d for d in releases if d['tag_name']==TAG];assert len(existing)<=1
    if not existing:
        assert not config.exists();run(['gh','release','create',TAG,'--repo',REPO,'--target',target,'--draft','--title','2008-05-12 archive · 2026-10-16 browser v24','--notes-file',str(notes)])
        releases=json.loads(run(['gh','api',f'repos/{REPO}/releases']));existing=[d for d in releases if d['tag_name']==TAG];assert len(existing)==1
    d=existing[0];assert d['draft'] and d['target_commitish']==target
    if config.exists():
        saved=json.loads(config.read_bytes());assert saved['id']==d['id'] and saved['target_commit']==target
    else:config.write_text(json.dumps({'created_or_recovered_utc':datetime.now(timezone.utc).isoformat(),'id':d['id'],'tag':TAG,'target_commit':target,'portable_acceptance_sha256':sha(qpath),'expected_assets':expected,'draft':True},indent=2)+'\n',encoding='utf-8')
    uploaded={a['name']:a for a in d['assets']};assert set(uploaded)<=set(expected)
    pending=[]
    for p in [archive,archive.with_name(archive.name+'.sha256'),R/'NOTICE.md']:
        if p.name in uploaded:
            a=uploaded[p.name];size,digest=expected[p.name];assert a['state']=='uploaded' and a['size']==size and a.get('digest')=='sha256:'+digest
        else:pending.append(str(p))
    if pending:run(['gh','release','upload',TAG,'--repo',REPO,*pending],timeout=900)
    print(json.dumps({'draft_release_id':d['id'],'target':target,'uploaded_assets_requested':len(pending),'published':False}))
if __name__=='__main__':main()

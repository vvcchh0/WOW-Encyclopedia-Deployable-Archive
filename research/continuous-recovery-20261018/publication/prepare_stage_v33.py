"""Prepare an explicit public-only checkpoint path list; never stage files itself."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'research/continuous-recovery-20261018'
PUB=RUN/'publication'
read=lambda p:json.loads(p.read_bytes())
source_only=sys.argv[1:]==['--source-only']
assert source_only or sys.argv[1:]==[]
assert read(PUB/('root-v33-export-acceptance.json' if source_only else 'root-v33-local-acceptance.json'))['accepted']
paths={x['path'] for x in read(PUB/'v33-checkpoint-candidate-files.json')['files']}
paths={p for p in paths if p.startswith('research/') and '/preparation-initial/' not in p}
paths.update(['tools/export_github_pages.py','docs/continuous-recovery-20261018.md','research/continuous-recovery-20261018/status.json','research/continuous-recovery-20261018/tasks.json'])
for directory in [PUB,RUN/'integration/v33',RUN/'integration/portable-release-tools-v2']:
    for p in directory.rglob('*'):
        rel=p.relative_to(ROOT).as_posix()
        if not p.is_file() or p.suffix.lower() not in {'.py','.cjs','.json','.md','.png'}:continue
        if any(x in p.parts for x in ['__pycache__','accepted-images','working-before-r2']):continue
        if any(x in p.name.lower() for x in ['progress','server-local.log','contact.png','raw','private']):continue
        if source_only and p.name=='v33-release-notes.md':continue
        if directory==PUB and p.parent!=PUB:continue
        paths.add(rel)
status=read(RUN/'status.json')
for batch in status['network_batches']:
    name=batch.get('plan')
    if not name:continue
    d=RUN/Path(name).parent
    for suffix in ['plan.json','input-bindings.json','cache-status.json','status-snapshot.json','selection-manifest.json']:
        p=d/suffix
        if p.is_file():paths.add(p.relative_to(ROOT).as_posix())
for p in paths:
    assert p.startswith(('research/','docs/','tools/')) and (ROOT/p).is_file(),p
    assert '/output/' not in p and '/raw/' not in p and 'private-payloads' not in p and '__pycache__' not in p,p
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
changed=set(subprocess.check_output(['git','diff','--name-only'],cwd=ROOT).decode().splitlines())
paths={p for p in paths if p not in tracked or p in changed}
config={'paths':sorted(paths),'receipt':'research/continuous-recovery-20261018/publication/'+('root-v33-source-checkpoint-staged-acceptance.json' if source_only else 'root-v33-validation-checkpoint-staged-acceptance.json'),
    'scope':'Root-reviewed v33 source closure, exact original-byte public copies, image-link repair, accepted export evidence and sanitized acquisition plans. Final browser acceptance and deployment remain pending for the source-only checkpoint.'}
out=PUB/('v33-source-stage-configuration.json' if source_only else 'v33-stage-configuration.json')
assert not out.exists();out.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'files':len(paths),'bytes':sum((ROOT/p).stat().st_size for p in paths),'configuration':out.relative_to(ROOT).as_posix(),
    'image_copies':sum('/accepted-images/' in p for p in paths),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))

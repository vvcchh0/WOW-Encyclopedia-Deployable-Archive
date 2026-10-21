"""Root source/geometry decision for the six reviewed talent UI images."""
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
REVIEW = ROOT / 'research/continuous-recovery-20261021/local-audit/talent-ui-six-review'
DEST = ROOT / 'research/continuous-recovery-20261021/integration/related-talent-ui'
DECISION = PUB / 'root-related-talent-ui-integration-decision.json'
MAP = DEST / 'input-map.json'
assert not MAP.exists() and not DECISION.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
summary = read(REVIEW / 'review-summary.json')
inventory = read(PUB / 'talent-related-image-inventory.json')
source_map = read(ROOT / 'research/continuous-recovery-20261021/integration/related-talent-icons/input-map.json')
source_accept = PUB / 'root-talent-related-source-acceptance.json'
assert read(source_accept)['accepted_source']
assert summary['execution']['all_initial_rank_points_61'] and summary['execution']['all_reset_zero']
assert len(summary['execution']['prototype_classes']) == 9
images = {r['path']:r for r in inventory['images']}
entries = []
for target, record in summary['source']['records'].items():
    repo_path = record['source_repo_path']
    payload = ROOT / 'research/continuous-recovery-20261021/network/talent-repo-zip01/runtime/private/image-extract' / repo_path
    data = payload.read_bytes()
    inv = images[repo_path]
    assert len(data) == inv['bytes'] == record['source_bytes']
    assert sha(payload) == inv['sha256'] == record['source_sha256']
    assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == inv['git_blob_sha1']
    with Image.open(io.BytesIO(data)) as image:
        assert image.format == 'PNG' and list(image.size) == inv['dimensions'] == record['dimensions']
        assert image.n_frames == 1
        image.load()
    name = Path(repo_path).name
    entries.append({
        'target_route':target, 'route':'/__offline/related-talent-ui/'+name,
        'repository_path':repo_path, 'sha256':inv['sha256'], 'length':len(data),
        'git_blob_sha1':inv['git_blob_sha1'], 'format':'PNG',
        'width':inv['dimensions'][0], 'height':inv['dimensions'][1], 'frames':1,
        'classification':'later_related_source', 'original_capture_timestamp':None,
        'payload_path':payload.relative_to(ROOT).as_posix(),
    })
assert len(entries) == 6 and sum(r['length'] for r in entries) == 5619
public = [{k:v for k,v in r.items() if k != 'payload_path'} for r in entries]
decision = {
    'schema':'wow-related-talent-ui-integration-decision/v1',
    'accepted_for_browser_supplement':True, 'checked_utc':datetime.now(timezone.utc).isoformat(),
    'source_acceptance':source_accept.relative_to(ROOT).as_posix(),
    'source_acceptance_sha256':sha(source_accept), 'source':source_map['source'],
    'accepted_ui_count':6, 'accepted_source_bytes':5619,
    'classification':'later_related_source', 'original_capture_timestamp':None,
    'original_2008_images_recovered':0, 'targets':public,
    'decision':'Only three state overlays and three controls; raw PNGs use explicit canonical PNG URLs. Original GIF target routes resolve to them without HTML redirect files.',
    'excluded':'Nine clipped class headings, all arrows, tree backgrounds, repository scripts and talent data.',
    'browser_basis':'Nine classes: initial, first point, max first talent, reset and reset-all. Printable controls clicked on Druid, Hunter and Warrior. No external page requests.',
    'root_visual_review':['druid-first-prototype.png','druid-full-prototype.png','hunter-reset-prototype.png'],
    'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (
        REVIEW / 'browser-receipt.json', REVIEW / 'review-summary.json',
        REVIEW / 'six-target-source-table.csv', PUB / 'talent-related-image-inventory.json',
    )],
}
DECISION.write_bytes((json.dumps(decision,indent=2)+'\n').encode())
mapping = {
    'schema':'wow-related-talent-ui-map/v1', 'decision':DECISION.relative_to(ROOT).as_posix(),
    'decision_sha256':sha(DECISION), 'source_acceptance':source_accept.relative_to(ROOT).as_posix(),
    'source_acceptance_sha256':sha(source_accept), 'source':source_map['source'],
    'ui_count':6, 'entries':entries,
}
DEST.mkdir(parents=True,exist_ok=True)
MAP.write_bytes((json.dumps(mapping,indent=2)+'\n').encode())
print(json.dumps({'accepted_ui_count':6,'source_bytes':5619,'decision_sha256':sha(DECISION),'map_sha256':sha(MAP)}))

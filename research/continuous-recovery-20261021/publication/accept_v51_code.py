"""Review the exact existing-image alias and preserve the accepted lore code."""
import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-v51-code-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = read(PUB / 'root-v50-code-acceptance.json')
evidence = ROOT / 'research/continuous-recovery-20261021/integration/available-resource-route-review/implementation-receipt-v51.json'
report = read(evidence)
assert report['tests']['result'] == '5 passed, 0 failed, 0 skipped'
assert report['implementation']['expected_payload_delta'] == report['implementation']['expected_redirect_html_delta'] == 0
bindings = {r['path']: r['sha256'] for r in old['code_bindings']}
changed = {'tools/export_github_pages.py', 'research/continuous-recovery-20261021/publication/verify_accepted_pages.py'}
for p, digest in bindings.items():
    if p not in changed:
        assert sha(ROOT / p) == digest, p
for row in report['changed_files']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
    bindings[row['path']] = row['sha256']
bindings['research/continuous-recovery-20261021/publication/verify_accepted_pages.py'] = sha(PUB / 'verify_accepted_pages.py')
name = 'tests/test_github_pages_export.py'
before = ast.parse(subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT))
after = ast.parse((ROOT / name).read_bytes())
methods = lambda tree: {n.name: ast.dump(n) for c in tree.body if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, ast.FunctionDef)}
a, b = methods(before), methods(after)
assert all(b[k] == v for k, v in a.items())
new_methods = sorted(k for k in b if k.startswith('test_') and k not in a)
assert len(new_methods) == 3
ids = ['tests.test_github_pages_export.GithubPagesExportTests.' + n for n in new_methods]
test_ids = sorted(set(old['tests']['unique_test_ids']) | set(ids))
assert len(test_ids) == 76
asset = ROOT / '.scratch/pages-resources-20261021-v50/wrath/images/letters/T.gif'
assert asset.stat().st_size == 1419 and sha(asset) == '0a82046107b2f5a45b258143cd8f862030980507bad23190c54445b43b3a62ad'
with Image.open(asset) as img:
    assert img.format == 'GIF'
    frames = getattr(img, 'n_frames', 1)
    dimensions = list(img.size)
    for i in range(frames):
        img.seek(i)
        img.load()
receipt = {
    'accepted': True, 'version': 'v51', 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'tests': {'count': 76, 'skipped': 0, 'unique_test_ids': test_ids,
              'executed_affected_alias_checks': 5, 'unchanged_tests_reused': 71,
              'old_test_method_bodies_preserved': True},
    'code_bindings': [{'path': p, 'sha256': digest} for p, digest in sorted(bindings.items())],
    'review': ['One exact compatibility alias; enabled only when the accepted double-slash target exists.',
               'No general repeated-slash normalization, no D/F aliases, no new image or redirect payload.',
               'Only three test methods and one fixture helper added; existing test method ASTs unchanged.',
               'Hosted verifier change only adds the v51 label. Accepted lore module and helper unchanged.'],
    'existing_image': {'bytes': 1419, 'sha256': sha(asset), 'format': 'GIF',
                       'dimensions': dimensions, 'decoded_frames': frames,
                       'actual_capture': '20080423095102', 'newly_downloaded': False},
    'evidence': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}
                 for p in (evidence, evidence.with_name('route-review.json'),
                           PUB / 'root-v50-code-acceptance.json', Path(__file__))],
    'actual_v51_export_or_browser_claimed': False,
}
OUT.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'tests': len(test_ids), 'existing_gif_dimensions': dimensions, 'sha256': sha(OUT)}))

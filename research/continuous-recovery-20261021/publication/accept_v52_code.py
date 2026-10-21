"""Independent focused code/source acceptance for the exact Arathi base repair."""
import ast
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-v52-code-acceptance.json'
assert not OUT.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
prior = read(PUB / 'root-v51-code-acceptance.json')
review = ROOT / 'research/continuous-recovery-20261021/local-audit/underdev-final-routing-review'
implementation = read(review / 'implementation-receipt.json')
bindings = {row['path']: row['sha256'] for row in prior['code_bindings']}
changed = {'tools/export_github_pages.py', 'tests/test_github_pages_export.py'}
for path, digest in bindings.items():
    if path not in changed:
        assert sha(ROOT / path) == digest, path
for row in implementation['implementation']['files']:
    assert row['path'] in changed and sha(ROOT / row['path']) == row['sha256']
    bindings[row['path']] = row['sha256']
bindings['research/continuous-recovery-20261021/publication/verify_v52_pages.py'] = sha(PUB / 'verify_v52_pages.py')
name = 'tests/test_github_pages_export.py'
before = ast.parse(subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT))
after = ast.parse((ROOT / name).read_bytes())
methods = lambda tree: {n.name: ast.dump(n) for c in tree.body if isinstance(c, ast.ClassDef)
                       for n in c.body if isinstance(n, ast.FunctionDef)}
old_methods, new_methods = methods(before), methods(after)
assert all(new_methods[k] == value for k, value in old_methods.items())
added = sorted(k for k in new_methods if k.startswith('test_') and k not in old_methods)
assert len(added) == 2 and all(k.startswith('test_arathi_') for k in added)
prefix = 'tests.test_github_pages_export.GithubPagesExportTests.'
ids = [prefix + k for k in added] + [prefix + 'test_wrath_resource_base_remains_directory_while_navigation_uses_index']
temp = ROOT / '.scratch/test-temp-20261021'
temp.mkdir(exist_ok=True)
tempfile.tempdir = str(temp)
for key in ('TEMP', 'TMP', 'TMPDIR'):
    os.environ[key] = str(temp)
sys.path.insert(0, str(ROOT))
stream = io.StringIO()
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
(PUB / 'v52-focused-test-execution.log').write_bytes(stream.getvalue().encode())
assert result.wasSuccessful() and result.testsRun == 3 and not result.skipped
targets = read(review / 'underdev-final-routing-review.json')['targets']
decoded = []
absent = []
for target in targets:
    if target['route_map_exact_exists']:
        path = ROOT / target['v51_exact_file']['path']
        assert sha(path) == target['source_exact_file']['sha256']
        with Image.open(path) as image:
            assert image.format == 'JPEG'
            image.load()
            decoded.append({'route': target['proposed_intended_route'], 'dimensions': list(image.size),
                            'sha256': sha(path), 'actual_capture': target['source_manifest_record']['actual_timestamp']})
    else:
        assert not target['source16_exact_file']['exists'] and not target['v51_exact_file']['exists']
        absent.append(target['proposed_intended_route'])
assert len(decoded) == 20 and len(absent) == 2
all_ids = sorted(set(prior['tests']['unique_test_ids']) | {prefix + name for name in added})
assert len(all_ids) == 78
report = {
    'accepted': True, 'version': 'v52', 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'tests': {'count': len(all_ids), 'skipped': 0, 'unique_test_ids': all_ids,
              'executed_affected_checks': 3, 'unchanged_checks_reused': 75,
              'old_test_method_bodies_preserved': True},
    'code_bindings': [{'path': path, 'sha256': digest} for path, digest in sorted(bindings.items())],
    'review': ['Exact source page and primary origin only; raw path directory assignment is preserved.',
               'Optional route argument is propagated while existing callers remain compatible.',
               'Other navigation and pages retain the normal index-document mapping.',
               'No new route aliases or images; all20 exact JPEGs independently decoded.'],
    'existing_decoded_images': decoded, 'missing_exact_images': absent,
    'evidence': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in (
        review / 'underdev-final-routing-review.json', review / 'implementation-receipt.json',
        PUB / 'root-v52-bounded-exception-decision.json', PUB / 'v52-focused-test-execution.log', Path(__file__),
    )],
}
OUT.write_bytes((json.dumps(report, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'executed_tests': 3, 'cumulative_unique_checks': 78,
                  'decoded_existing_images': 20, 'missing_exact_images': 2}))

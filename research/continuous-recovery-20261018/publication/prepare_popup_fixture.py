"""Create a separate fixture for the reviewed popup runtime; no export mutation."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import export_github_pages as pages

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
tool = ROOT / 'tools/export_github_pages.py'
assert sha(tool) == 'b353b0f88da385321a70b35e2bb7f9bccc7cbb371f69c7d36c3cd8d2c3af543c'
target = PUB / 'runtime-fixture-popup'
assert not target.exists()
shutil.copytree(PUB / 'runtime-fixture-v31', target)
(target / 'fixture-receipt.json').unlink()
routes = json.loads((ROOT / '.scratch/pages-resources-20261018-v30/__offline/route-map.json').read_bytes())
runtime = target / '__offline/pages_runtime.js'
runtime.parent.mkdir(parents=True)
runtime.write_text(pages.runtime_js(pages.DEFAULT_BASE_PATH, routes['routes']), encoding='utf-8', newline='\n')
files = [{ 'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'length': p.stat().st_size }
         for p in sorted(target.rglob('*')) if p.is_file()]
(target / 'fixture-receipt.json').write_text(json.dumps({'fixture_only': True, 'export_executed': False,
    'tool_sha256': sha(tool), 'previous_fixture_sha256': sha(PUB / 'runtime-fixture-v31/fixture-receipt.json'),
    'files': files}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'files': len(files), 'receipt_sha256': sha(target / 'fixture-receipt.json')}))

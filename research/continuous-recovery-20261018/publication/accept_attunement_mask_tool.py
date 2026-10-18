"""Root source/byte acceptance of the three attunement compatibility masks."""
import ast
import datetime as dt
import hashlib
import json
import runpy
import subprocess
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
RUN = PUB.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = PUB / 'root-attunement-mask-tool-acceptance.json'
assert not dest.exists()
tool = ROOT / 'tools/export_github_pages.py'
assert sha(tool) == '8c50b1574f24a0bd2b03492ae8fe0cb7d3c48a50a247ba70d9e1859d58672afb'
worker = RUN / 'integration/attunement-mask-tool'
assert sha(worker / 'verification-receipt.json') == '50e5db1229bdc6fde36ec27449948e97c26e0d60905d4fb6f960eaff697cb587'
module = runpy.run_path(str(worker / 'make_receipt.py'), run_name='root_read_only_import')
baseline = module['reconstruct_b353'](tool.read_text(encoding='utf-8'))
assert hashlib.sha256(baseline.encode()).hexdigest() == 'b353b0f88da385321a70b35e2bb7f9bccc7cbb371f69c7d36c3cd8d2c3af543c'
def defs(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
before, after = defs(baseline), defs(tool.read_text(encoding='utf-8'))
assert set(after)-set(before) == {'rewrite_attunement_mask_pixel', '_attunement_mask_pixel_placeholder'}
assert not set(before)-set(after)
changed = [name for name in before if before[name] != after[name]]
assert changed == ['export_pages'], changed
assert before['runtime_js'] == after['runtime_js']
pixel = ROOT / '.scratch/offline-navigation-20261015-v15/site/shared/wow-com/includes/images/pixel.gif'
assert sha(pixel) == 'b1442e85b03bdcaf66dc58c7abb98745dd2687d86350be9a298a1d9382ac849b'
image = Image.open(pixel)
assert image.size == (1, 1) and getattr(image, 'n_frames', 1) == 1
assert image.convert('RGBA').getextrema()[3] == (0, 0)
sys.path.insert(0, str(ROOT/'tools'))
import export_github_pages as pages
source = ROOT / '.scratch/pages-resources-20261018-v30/bcattunement/index.html'
assert sha(source) == 'ea23f53156738370d24354f7690bf6c21363eb0e442a01bcb99f0e55532c9c20'
text = source.read_text(encoding='utf-8')
derived, repaired = pages.rewrite_attunement_mask_pixel(text, route='/bcattunement/index.html', base_path=pages.DEFAULT_BASE_PATH)
marker = 'requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Fbcattunement%2Fimages%2Fpixel.gif'
target = pages.DEFAULT_BASE_PATH+'shared/wow-com/includes/images/pixel.gif'
assert repaired and text.count(marker) == 5 and derived.count(marker) == 2
assert derived.count(target)-text.count(target) == 3
assert pages.rewrite_attunement_mask_pixel(derived, route='/bcattunement/index.html', base_path=pages.DEFAULT_BASE_PATH) == (derived, False)
command = [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_attunement_mask_pixel.py', '-v']
result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
log = PUB / 'root-attunement-mask-tool-tests.log'
log.write_text(result.stdout, encoding='utf-8')
assert result.returncode == 0 and 'Ran 2 tests' in result.stdout
receipt = {'accepted': True, 'checked_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'previous_tool_sha256': hashlib.sha256(baseline.encode()).hexdigest(), 'tool_sha256': sha(tool),
    'worker_verification_sha256': sha(worker/'verification-receipt.json'), 'test_log_sha256': sha(log),
    'changed_existing_top_level_definitions': changed, 'unchanged_existing_definitions': len(before)-1,
    'popup_runtime_unchanged': True, 'transparent_compatibility_asset_sha256': sha(pixel),
    'actual_frozen_page_sha256': sha(source), 'matching_placeholder_occurrences_before': 5,
    'matching_placeholder_occurrences_after': 2, 'compatibility_references_replaced': 3,
    'newly_recovered_original_images': 0, 'output_impact': ['bcattunement/index.html'],
    'network_requests': 0, 'export_executed': False,
    'scope': 'Source, byte scope and focused regression acceptance. Actual chart hover/lock and rendered mask require production browser acceptance.'}
dest.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
status_path = RUN/'status.json'
status = json.loads(status_path.read_bytes())
status['tool_supersessions'].append({'path': 'tools/export_github_pages.py', 'prior_sha256': receipt['previous_tool_sha256'],
    'accepted_sha256': sha(tool), 'acceptance': dest.relative_to(RUN).as_posix()})
status_path.write_text(json.dumps(status, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'accepted': True, 'receipt_sha256': sha(dest), 'tool_sha256': sha(tool), 'compatibility_refs': 3}))

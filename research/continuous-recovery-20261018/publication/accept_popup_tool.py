"""Root review and real-browser fixture acceptance for the image popup adapter."""
import ast
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = PUB / 'root-popup-tool-acceptance.json'
assert not dest.exists()
tool = ROOT / 'tools/export_github_pages.py'
previous = subprocess.check_output(['git', 'show', 'HEAD:tools/export_github_pages.py'], cwd=ROOT)
assert hashlib.sha256(previous).hexdigest() == '7c3684fb777e9c21b07fe8c8a1be0418810f448e99dd582ed4c9d9c342764dea'
assert sha(tool) == 'b353b0f88da385321a70b35e2bb7f9bccc7cbb371f69c7d36c3cd8d2c3af543c'
def definitions(data):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(data).body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
old, new = definitions(previous), definitions(tool.read_bytes())
assert old.keys() == new.keys()
changed = [name for name in old if old[name] != new[name]]
assert changed == ['runtime_js'], changed
browser_path = PUB / 'root-popup-fixture-browser-retry1-acceptance.json'
browser = json.loads(browser_path.read_bytes())
assert browser['accepted'] and browser['fixture_only'] and browser['tool_sha256'] == sha(tool)
assert not browser['errors'] and not browser['external_requests']
command = [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_popup_image_viewer.py', '-v']
result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
log = PUB / 'root-popup-tool-tests.log'
log.write_text(result.stdout, encoding='utf-8')
assert result.returncode == 0 and 'Ran 2 tests' in result.stdout
receipt = {'accepted': True, 'checked_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'previous_tool_sha256': hashlib.sha256(previous).hexdigest(), 'tool_sha256': sha(tool),
    'changed_top_level_definitions': changed, 'unchanged_top_level_definitions': len(old)-1,
    'test_log_sha256': sha(log), 'browser_fixture_receipt_sha256': sha(browser_path),
    'fixture_previous_attempt': 'root-popup-fixture-browser-acceptance.json',
    'fixture_correction': 'Use the source-cited insider/11/arena.xml route; prior checker requested a nonexistent insider/06 route.',
    'visual_review': 'Root inspected the actual fixture screenshot: original 750x600 story artwork opens and remains visible.',
    'output_impact': ['__offline/pages_runtime.js'], 'network_requests': 0,
    'scope': 'Tool and isolated browser fixture only; production export and deployment remain separate.'}
dest.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
status_path = PUB.parent / 'status.json'
status = json.loads(status_path.read_bytes())
status['tool_supersessions'].append({'path': 'tools/export_github_pages.py',
    'prior_sha256': receipt['previous_tool_sha256'], 'accepted_sha256': sha(tool),
    'acceptance': dest.relative_to(PUB.parent).as_posix()})
status_path.write_text(json.dumps(status, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'accepted': True, 'sha256': sha(dest), 'changed': changed, 'checks': len(browser['checks'])}))

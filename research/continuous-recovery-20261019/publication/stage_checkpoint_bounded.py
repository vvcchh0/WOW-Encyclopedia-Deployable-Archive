"""Stage an explicit checkpoint list and scan the exact Git blobs."""
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
configuration = json.loads(Path(sys.argv[1]).read_bytes())
paths = configuration['paths']
receipt_path = configuration['receipt']
allow = ROOT / '.gitignore'
existing = set(allow.read_text(encoding='utf-8').splitlines())
lines = ['!/' + p for p in paths + [receipt_path] if '!/' + p not in existing and not p.startswith('docs/')]
if lines:
    with allow.open('a', encoding='utf-8', newline='') as handle:
        handle.write('\n' + '\n'.join(lines) + '\n')
paths = sorted(set(paths + ['.gitignore']))
bindings = {}
for p in paths:
    path = (ROOT / p).resolve()
    path.relative_to(ROOT)
    if not path.is_file() or p.startswith(('offline/', '.scratch/')) or '/raw/' in p or '/raw-' in p or '__pycache__' in p:
        raise RuntimeError('Invalid checkpoint path: ' + p)
    bindings[p] = hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

for start in range(0, len(paths), 32):
    subprocess.run(['git', 'add', '--', *paths[start:start+32]], cwd=ROOT, check=True)
staged = git('diff', '--cached', '--name-only').decode().splitlines()
if set(staged) != set(paths):
    raise RuntimeError('Unexpected staged path set')
spec = importlib.util.spec_from_file_location('wow_checkpoint_hygiene', ROOT / 'research/github-publication-20261012/full-tree-hygiene.py')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
findings, files = [], []

def fields(value, path, location=''):
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in {'cookie', 'set-cookie', 'x-archive-orig-set-cookie', 'authorization', 'proxy-authorization'} and isinstance(item, str) and item.strip():
                findings.append({'path': path, 'category': 'raw_sensitive_json_field', 'location': location + '.' + key})
            fields(item, path, location + '.' + key)
    elif isinstance(value, list):
        for n, item in enumerate(value):
            fields(item, path, location + '[' + str(n) + ']')

for path in staged:
    data = git('show', ':' + path)
    digest = hashlib.sha256(data).hexdigest()
    if digest != bindings[path]:
        raise RuntimeError('Staged bytes differ: ' + path)
    counts = {}
    for pattern in module.PATTERNS:
        count = sum(1 for _ in pattern.regex.finditer(data))
        if count:
            counts[pattern.category] = count
            allowed = configuration.get('synthetic_test_allowlist', {}).get(path)
            synthetic = pattern.category == 'url_userinfo_value' and count == 1 and allowed == digest and (b'https://' + b'user:pass' + b'@example.invalid/') in data
            # One reviewed negative parser fixture deliberately supplies fake
            # userinfo on the otherwise valid source host. Pin its full file
            # SHA, test path and occurrence count; this is not a general waiver.
            synthetic_parser = (pattern.category == 'url_userinfo_value' and count == 1
                and path == 'tests/test_navigation_image_link_recovery.py' and allowed == digest
                and (b'http://' + b'user:password' + b'@www.worldofwarcraft.com/news/images/07-08/ss01.jpg') in data)
            if not (synthetic or synthetic_parser) and pattern.category not in {'cookie_handling_field', 'authorization_field_without_value'}:
                findings.append({'path': path, 'category': pattern.category, 'count': count})
    if re.search(rb'(?im)^(?:set-cookie|x-archive-orig-set-cookie|authorization|proxy-authorization):\s*\S+', data):
        findings.append({'path': path, 'category': 'raw_sensitive_http_header'})
    if path.endswith('.json'):
        fields(json.loads(data), path)
    files.append({'path': path, 'bytes': len(data), 'sha256': digest, 'pattern_counts': counts})
receipt = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'base_commit': git('rev-parse', 'HEAD').decode().strip(),
    'scope': configuration['scope'], 'files': files, 'findings': findings, 'accepted': not findings}
(ROOT / receipt_path).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'accepted': not findings, 'files': len(files), 'bytes': sum(x['bytes'] for x in files), 'findings': findings}))
if findings:
    raise SystemExit(1)
subprocess.run(['git', 'add', '--', receipt_path], cwd=ROOT, check=True)
subprocess.run(['git', '-c', 'core.whitespace=cr-at-eol,-blank-at-eof', 'diff', '--cached', '--check'], cwd=ROOT, check=True)

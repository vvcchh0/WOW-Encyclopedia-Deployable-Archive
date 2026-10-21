"""Reuse the accepted browser scenario against the extracted ZIP's own server."""
import hashlib
import json
from pathlib import Path

PUB = Path(__file__).resolve().parent
source = PUB / 'root_v51_browser.cjs'
target = PUB / 'root_v51_portable_browser.cjs'
report = PUB / 'v51-portable-browser-preparation.json'
assert not target.exists() and not report.exists()
data = source.read_text(encoding='utf-8')
replacements = {
    '// Actual Chrome validation of the unmodified v51 export. No asset injection.':
    '// Actual Chrome validation of the extracted v51 ZIP and its packaged server. No asset injection.',
    '.scratch/pages-resources-20261021-v51': '.scratch/local bundle smoke 20261021 v51/site',
    "const port='24772'": "const port='24773'",
    "'root-v51-browser-acceptance.json'": "'root-v51-portable-browser-acceptance.json'",
    "'v51-screenshots'": "'v51-portable-screenshots'",
    "'v51-browser-execution.json'": "'v51-portable-browser-execution.json'",
}
for old, new in replacements.items():
    assert old in data, old
    data = data.replace(old, new)
target.write_bytes(data.encode())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report.write_bytes((json.dumps({
    'source': source.name, 'source_sha256': sha(source),
    'target': target.name, 'target_sha256': sha(target),
    'changes': replacements,
    'scope': 'Only server/site/output labels change. The accepted assertions and browser interaction sequence are reused against extracted package bytes.',
}, indent=2) + '\n').encode())
print(json.dumps({'prepared': target.name, 'sha256': sha(target)}))

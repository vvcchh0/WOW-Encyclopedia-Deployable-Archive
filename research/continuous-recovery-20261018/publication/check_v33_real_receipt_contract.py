"""Exercise v33 preparation against real accepted primary and mixed receipts."""
import ast
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
DIR = RUN / 'integration/v33'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bind = lambda p: {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}
out = PUB / 'root-v33-real-receipt-preparation-contract.json'
assert not out.exists()
spec = importlib.util.spec_from_file_location('root_v33_preparation_contract', DIR / 'build_pages_v33.py')
b = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = b
spec.loader.exec_module(b)
e = b.import_exporter()
assert e.mirror.route_path('http://www.worldofwarcraft.com/news/test.jpg') == '/news/test.jpg'
_, old_primary, old_supplement, pins = b.frozen_maps()
all_rows = []
checks = []
for n in ['popup24-batch1', 'popup24-batch2', 'popup24-batch3', 'navigation70-batch6']:
    s, p = PUB / f'root-{n}-source-acceptance.json', PUB / f'root-{n}-public-copy-acceptance.json'
    items = read(p)['accepted_images']
    primary = sum(urlsplit(x['original']).hostname in b.PRIMARY_HOSTS for x in items)
    supplement = len(items) - primary
    batch = {'id': n, 'role': 'mixed' if primary and supplement else ('primary' if primary else 'supplement'),
             'expected_count': len(items), 'expected_bytes': sum(x['length'] for x in items),
             'expected_primary_count': primary, 'expected_supplement_count': supplement,
             'source_acceptance': bind(s), 'public_copy_acceptance': bind(p)}
    rows, _, _ = b.validate_batch(batch, len(checks)+1)
    assert len(rows) == len(items)
    all_rows.extend(rows)
    checks.append({'batch': n, 'rows': len(rows), 'primary': primary, 'supplement': supplement, 'source_sha256': sha(s), 'public_sha256': sha(p)})
audit = b.build_source_audit(all_rows)
assert audit['all_byte_match'] and audit['source_count'] == 31 and audit['primary_count'] == 30 and audit['supplement_count'] == 1
tree = ast.parse((DIR / 'execute_v33.py').read_text(encoding='utf-8'))
dependency = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'required_bindings')
for node in ast.walk(dependency):
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'builder':
        assert hasattr(b, node.attr), node.attr
assert not (ROOT / '.scratch/pages-resources-20261018-v33').exists()
assert not (DIR / 'v33-primary-source-map.json').exists()
result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0, 'maps_created': 0,
    'builder': bind(DIR / 'build_pages_v33.py'), 'runner': bind(DIR / 'execute_v33.py'), 'checks': checks,
    'source_byte_audit': audit, 'frozen_pin_count': len(pins),
    'scope': 'Real 21 accepted popup originals plus real mixed nine-primary/one-Blizzard receipt; clean accepted exporter import, source byte audit and every runner builder dependency name. Full input/export gate follows the final explicit source manifest.'}
out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'accepted': True, 'rows': len(all_rows), 'sha256': sha(out), 'builder_sha256': sha(DIR / 'build_pages_v33.py'), 'runner_sha256': sha(DIR / 'execute_v33.py')}))

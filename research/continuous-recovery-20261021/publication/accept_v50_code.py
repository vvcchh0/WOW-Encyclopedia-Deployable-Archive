"""Root review of the opt-in lore integration and its bounded checks."""
import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-v50-code-acceptance.json'
assert not OUT.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
old = read(PUB / 'root-v49-code-acceptance.json')
integration_path = ROOT / 'research/continuous-recovery-20261021/integration/aldor-scryers-lore/exporter-integration-receipt.json'
prepare_path = integration_path.with_name('prepare-receipt.json')
integration, prepare = read(integration_path), read(prepare_path)
assert integration['status'] == 'portable_tests_passed'
assert integration['test']['exit_code'] == integration['test']['exit_code_2'] == 0
assert integration['test']['passed'] == 4 and integration['test']['passed_2'] == 2
assert integration['test']['skipped'] == integration['test']['skipped_2'] == 0
assert prepare['tests']['result'] == '4 passed' and prepare['tests']['skipped'] == 0
assert sha(ROOT / 'tools/export_github_pages.py') == integration['exporter']['sha256']
assert sha(ROOT / 'tools/aldor_scryers_lore.py') == integration['loader']['sha256'] == prepare['loader']['sha256']
assert sha(ROOT / 'tests/test_aldor_scryers_pages.py') == integration['files']['sha256']
bindings = {r['path']: r['sha256'] for r in old['code_bindings']}
for path, digest in bindings.items():
    if path != 'tools/export_github_pages.py':
        assert sha(ROOT / path) == digest, path
new_tests = []
for module in ('test_aldor_scryers_lore', 'test_aldor_scryers_pages'):
    source = ROOT / 'tests' / (module + '.py')
    parsed = ast.parse(source.read_bytes())
    for cls in (n for n in parsed.body if isinstance(n, ast.ClassDef)):
        new_tests.extend('tests.' + module + '.' + cls.name + '.' + n.name
                         for n in cls.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_'))
assert len(new_tests) == 8 and len(set(new_tests)) == 8
all_tests = sorted(set(old['tests']['unique_test_ids']) | set(new_tests))
assert len(all_tests) == 73
for p in ('tools/export_github_pages.py', 'tools/aldor_scryers_lore.py',
          'tests/test_aldor_scryers_lore.py', 'tests/test_aldor_scryers_pages.py',
          'research/continuous-recovery-20261021/publication/verify_accepted_pages.py'):
    bindings[p] = sha(ROOT / p)
receipt = {
    'accepted': True, 'version': 'v50', 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'tests': {'count': 73, 'skipped': 0, 'unique_test_ids': all_tests,
              'executed_for_new_lore_code': 10, 'unchanged_tests_reused': 63,
              'scope': 'Four loader/parser checks, four opt-in exporter checks and two project-prefix/output-guard regression checks passed. Other unchanged checks reuse their exact accepted v49 bindings.'},
    'code_bindings': [{'path': p, 'sha256': digest} for p, digest in sorted(bindings.items())],
    'review': ['Explicit default-off API and CLI; exact Source16 manifest and source-byte validation before output creation.',
               'One generated helper and one tokenized head injection only on the main faction page.',
               'Helper bytes included in disk budget and checked before writing; source data/scripts unchanged.',
               'Portable fixtures exercise collision, source drift, default-off and embedded fake head-end guards.',
               'Hosted verifier change is solely acceptance of the new v50 version label.'],
    'evidence': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}
                 for p in (prepare_path, integration_path,
                           PUB / 'root-v49-code-acceptance.json',
                           PUB / 'root-aldor-scryers-lore-source-acceptance.json', Path(__file__))],
    'actual_v50_export_or_browser_claimed': False,
}
OUT.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'tests': len(all_tests), 'bindings': len(bindings), 'sha256': sha(OUT)}))

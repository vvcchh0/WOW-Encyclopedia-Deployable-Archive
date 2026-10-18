"""Offline independent gate for the two previously timed-out gallery indexes."""
import ast
import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
BASE = RUN / 'network/gallery-late-window-retry2'
OUT = RUN / 'publication/root-gallery-retry2-plan-acceptance.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    pins = {
        'plan.json': '3051ac1bea647313206108f2a9950d9f4f4ffd39e6ab699e2777ee14bcd20dc3',
        'input-bindings.json': 'cd2a30c442c7a58bbcf04f221f50324a950958bd88049139d43ea69230f000b5',
        'gallery_late_window_retry2_driver_v1.py': '9de27892413d02a253c88274fd857efc47f13ba76aa2909b6aad34161828b1d6',
        'fixture-results.json': '870740ea2493f862708f3ab670486b8ad64b7699fae7a74c96289901310a7f38',
    }
    for name, digest in pins.items():
        assert sha(BASE / name) == digest, name
    old = RUN / 'network/gallery-late-window-20261018/gallery_late_window_driver_v1.py'
    new = BASE / 'gallery_late_window_retry2_driver_v1.py'
    definitions = lambda p: {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(p.read_text()).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    before, after = definitions(old), definitions(new)
    assert before.keys() == after.keys()
    changed = sorted(n for n in before if before[n] != after[n])
    assert changed == ['fixture', 'plan_for_run', 'validate_inputs'], changed
    spec = importlib.util.spec_from_file_location('root_retry2_review', new)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    plan, candidates, bindings = module.validate_inputs()
    fixtures = module.fixture()
    assert fixtures['all_passed'] and fixtures['passed'] == fixtures['total'] == 15
    assert len(candidates) == 2
    wanted = {'Karazhan': '20090101000000', 'Black Temple': '20080512210045'}
    for item in candidates:
        q = parse_qs(urlsplit(item['cdx_query_url']).query)
        assert q['url'] == [item['prefix']] and q['matchType'] == ['prefix']
        assert q['from'] == [wanted[item['gallery']]] and q['to'] == ['20101207235959']
        assert q['limit'] == ['500'] and q['showResumeKey'] == ['true'] and 'collapse' not in q
    status = json.loads((RUN / 'status.json').read_bytes())
    assert status['latest_failure_tail'] == 0
    assert status['latest_source_acceptance'] == 'publication/root-news-unplanned-batch8-source-acceptance.json'
    assert status['latest_control_gate'] == 'publication/root-post-gallery-connectivity-control-acceptance.json'
    assert not (BASE / 'execution-input-bindings.json').exists()
    assert shutil.disk_usage(ROOT).free >= 11005853696
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'bindings': [{'path': (BASE / n).relative_to(ROOT).as_posix(), 'sha256': h} for n, h in pins.items()],
              'unchanged_callable_bodies': len(before) - len(changed), 'changed_callable_bodies': changed,
              'offline_fixture_passed': 15, 'candidate_count': 2, 'requests_max': 4,
              'seconds_max': 180, 'proxy_timeout_seconds': 60, 'bytes_max': 16777216,
              'network_requests_during_acceptance': 0, 'index_only': True,
              'reason': 'Two prior unknown prefix windows; successful exact control after those failures; longer first-byte wait within the same transport and stop rules.',
              'disk_free_bytes': shutil.disk_usage(ROOT).free}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

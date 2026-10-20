"""Read-only remote baseline refresh; no Wayback requests or Git mutation."""
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name('root-baseline-acceptance.json')
EXPECTED_MAIN = 'f84786d4820438213f0610df147fb78c3f0b2af9'
EXPECTED_PAGES = '78dac6c55286d43dc6a4e197a2b41d13cd6a9b4f'


def main():
    assert not OUT.exists()
    def run(args, seconds=60, env=None):
        value = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, timeout=seconds)
        return value.returncode, value.stdout.decode('utf-8', 'replace'), value.stderr.decode('utf-8', 'replace')
    code, head, _ = run(['git', 'rev-parse', 'HEAD'])
    assert code == 0 and head.strip() == EXPECTED_MAIN
    code, status, _ = run(['git', 'status', '--porcelain', '--untracked-files=no'])
    assert code == 0 and not status.strip()
    attempts = []
    for transport, proxy in [('direct', ''), ('proxy', 'http://127.0.0.1:7890')]:
        args = ['git', '-c', 'http.proxy=' + proxy, '-c', 'http.sslVerify=true', '-c', 'http.lowSpeedLimit=1', '-c', 'http.lowSpeedTime=30', 'ls-remote', 'origin', 'refs/heads/main', 'refs/heads/gh-pages']
        try:
            code, stdout, stderr = run(args, 60)
        except subprocess.TimeoutExpired:
            attempts.append({'transport': transport, 'timed_out': True})
            continue
        attempts.append({'transport': transport, 'returncode': code, 'timed_out': False})
        if code == 0:
            refs = {line.split()[1]: line.split()[0] for line in stdout.splitlines() if line.strip()}
            break
    else:
        raise RuntimeError('Remote refs unavailable; inspect bounded attempts locally')
    assert refs == {'refs/heads/main': EXPECTED_MAIN, 'refs/heads/gh-pages': EXPECTED_PAGES}, refs
    bindings = []
    for relative, expected in [
        ('offline/build-manifest.json', '397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459'),
        ('.scratch/offline-navigation-20261015-v15/build-manifest.json', 'd89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002'),
        ('.scratch/pages-resources-20261019-v38/export-provenance.json', 'de6ee4348a688cf648a86bf2537fb7f8f60490721419e7f45aea6e881b590828'),
    ]:
        path = ROOT / relative
        body = path.read_bytes()
        sha = hashlib.sha256(body).hexdigest()
        assert sha == expected, relative
        bindings.append({'path': relative, 'bytes': len(body), 'sha256': sha})
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'local_head': head.strip(), 'remote_refs': refs, 'remote_attempts': attempts, 'frozen_bindings': bindings, 'disk_free_bytes': free, 'wayback_requests': 0, 'scope': 'Independent remote refs and current frozen manifest/provenance identities. No repeated whole-site or ZIP audit.'}
    OUT.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
